# CLAUDE.md

Guidance for coding agents working in this repository.

## What this project is

A personal productivity toolkit: seven small CLI tools that accelerate career
development, content creation, and financial planning. Six of the seven call
the Claude API; the EB1A tracker is fully offline. This is a single-user tool
collection, not a library — there is no public API surface beyond the CLI.

## Architecture

```
cli.py                           # Unified entrypoint: `toolkit <command>` / `python cli.py <command>`
toolkit/                         # Shared infrastructure used by every AI-powered tool
├── config.py                    #   CLAUDE_MODEL env var, API key lookup, fallback model
└── client.py                    #   Shared Anthropic client, complete()/complete_json(),
                                 #   prompt caching, structured outputs, error handling
linkedin_batch/generator.py      # LinkedIn "Day X" batch post generator (API)
outreach_templates/generator.py  # Job outreach messages; AI angle + template fallback (API, optional)
interview_prep/mock_interview.py # Mock PM interviews with scored feedback (API)
eb1a_tracker/tracker.py          # EB1A evidence tracker (OFFLINE — no API, no network)
medium_drafts/drafter.py         # Medium article first-draft generator (API)
financial_review/reviewer.py     # Portfolio review with NRI tax analysis (API)
content_repurpose/repurpose.py   # One idea → LinkedIn/Medium/YouTube/Instagram (API)
tests/test_smoke.py              # Smoke test per subcommand, API fully mocked
```

Each tool module exposes `main(argv=None)` (argparse) and is runnable three
ways: `toolkit <command> ...`, `python cli.py <command> ...`, or standalone
`python -m <package>.<module> ...`. `cli.py` forwards the remaining argv to
the tool's own parser, so each tool owns its flags.

## Model configuration

All model selection goes through **one** place: the `CLAUDE_MODEL` env var
read in `toolkit/config.py` (default: `claude-fable-5`). Never hardcode a
model string in a tool module — future model swaps must stay a one-line
`.env` change.

When the configured model is Fable/Mythos-class, `toolkit/client.py`:
- uses the beta endpoint with the server-side fallback
  (`server-side-fallback-2026-06-01`, fallback model `claude-opus-4-8`) so
  safety-classifier false positives are transparently re-served;
- checks `stop_reason == "refusal"` before reading content;
- extracts the first `text` block rather than `content[0]` (thinking blocks
  may precede text on Fable 5).

Static prompts are sent as `system` blocks with
`cache_control: {"type": "ephemeral"}`. Note: the current prompts are below
Fable 5's ~2048-token minimum cacheable prefix, so caching is dormant until
the prompts grow — the structure is in place, don't move prompts back into
user messages.

## Running tests

```bash
pip install -e ".[dev]"   # or: pip install -r requirements.txt pytest
pytest
```

Tests never hit the network: `toolkit.client.get_client` is monkeypatched
with a fake client. Keep it that way — any new test that would make a real
API call is a bug.

## Conventions

- Python 3.10+, stdlib `argparse`, minimal dependencies (`anthropic`,
  `python-dotenv`; `pytest` for dev only).
- API access goes through `toolkit.client.complete()` /
  `complete_json()` — never instantiate `anthropic.Anthropic` in a tool
  module.
- User-facing errors raise `toolkit.client.ToolkitError`; CLI `main()`
  functions are wrapped with `@handle_errors` which prints the message and
  exits 1. No tracebacks for expected failures.
- The prompt texts (VOICE_PROMPT, INTERVIEWER_SYSTEM, REVIEW_SYSTEM,
  FORMAT_PROMPTS) are tuned product content — do not reword them as part of
  unrelated changes.
- Output style in generated content: no emojis, practitioner tone. That is
  enforced by the prompts, not code.

## Things a coding agent must never break

- **CLI compatibility**: subcommand names (`linkedin`, `outreach`,
  `interview`, `eb1a`, `medium`, `finance`, `repurpose`) and every existing
  flag. Scripts and muscle memory depend on them.
- **EB1A tracker stays offline**: `eb1a_tracker` must never import
  `anthropic` or require a network call. `evidence.json` is a data store —
  do not change its schema without a migration.
- **Outreach template fallback**: `outreach_templates` must keep producing
  usable messages with no API key configured (built-in templates).
- **Drafts-only behavior**: no tool sends, posts, or publishes anything.
  They generate text for human review.
- **Single model knob**: `CLAUDE_MODEL` is the only model configuration
  point.
