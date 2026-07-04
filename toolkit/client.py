"""Shared Anthropic client and request helpers used by every AI-powered tool.

Tool modules call ``complete()`` or ``complete_json()`` instead of
instantiating ``anthropic.Anthropic`` themselves. This module owns:

- model selection (via ``toolkit.config``),
- prompt caching for static system prompts,
- structured JSON outputs,
- refusal handling with a server-side fallback on Fable/Mythos-class models,
- consistent, user-facing error handling (``ToolkitError``).
"""

import functools
import json
import sys

import anthropic

from . import config


class ToolkitError(Exception):
    """User-facing failure. CLI entry points print it and exit 1 — no traceback."""


_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not config.get_api_key():
            raise ToolkitError("ANTHROPIC_API_KEY not set. Add it to .env or export it.")
        _client = anthropic.Anthropic()
    return _client


def _is_fable_class(model: str) -> bool:
    return model.startswith(("claude-fable", "claude-mythos"))


def complete(
    prompt: str,
    *,
    system: str | None = None,
    max_tokens: int = 4096,
    schema: dict | None = None,
) -> str:
    """Send a single-turn request and return the response text.

    ``system`` is sent as a cache-marked block: identical system prompts
    across calls (e.g. batch generation loops) hit the prompt cache once the
    prompt exceeds the model's minimum cacheable prefix.

    ``schema`` enables structured outputs — the returned text is guaranteed
    to be JSON that validates against the schema.
    """
    model = config.get_model()
    kwargs: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = [
            {"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}
        ]
    if schema:
        kwargs["output_config"] = {"format": {"type": "json_schema", "schema": schema}}

    client = get_client()
    try:
        if _is_fable_class(model):
            # Fable 5's safety classifiers can decline benign-adjacent
            # requests; the server-side fallback re-serves those on Opus 4.8
            # within the same call.
            response = client.beta.messages.create(
                betas=[config.SERVER_SIDE_FALLBACK_BETA],
                fallbacks=[{"model": config.FALLBACK_MODEL}],
                **kwargs,
            )
        else:
            response = client.messages.create(**kwargs)
    except anthropic.AuthenticationError:
        raise ToolkitError("Invalid ANTHROPIC_API_KEY — check your .env.") from None
    except anthropic.RateLimitError:
        raise ToolkitError("Rate limited by the API. Wait a minute and retry.") from None
    except anthropic.APIStatusError as e:
        raise ToolkitError(f"API error ({e.status_code}): {e.message}") from None
    except anthropic.APIConnectionError:
        raise ToolkitError("Could not reach the Anthropic API. Check your network.") from None

    # check stop_reason before touching content: a refusal can carry an
    # empty content array
    if response.stop_reason == "refusal":
        raise ToolkitError(
            "The model declined this request (safety classifiers). "
            "Rephrase the input and try again."
        )
    if response.stop_reason == "max_tokens":
        print(
            "Warning: response hit the max_tokens limit and may be truncated.",
            file=sys.stderr,
        )

    # thinking blocks may precede the text block on Fable 5 — never index content[0]
    text = next((b.text for b in response.content if b.type == "text"), None)
    if text is None:
        raise ToolkitError("The API returned no text content.")
    return text.strip()


def complete_json(
    prompt: str,
    *,
    schema: dict,
    system: str | None = None,
    max_tokens: int = 4096,
) -> dict:
    """Structured-output request: returns the parsed JSON object."""
    return json.loads(
        complete(prompt, system=system, max_tokens=max_tokens, schema=schema)
    )


def handle_errors(fn):
    """Wrap a CLI ``main()`` so ToolkitError prints cleanly and exits 1."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ToolkitError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    return wrapper
