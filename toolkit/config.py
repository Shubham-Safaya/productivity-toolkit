"""Central configuration for the productivity toolkit.

All model selection goes through the CLAUDE_MODEL env var so future model
swaps are a one-line change in .env — never hardcode a model string in a
tool module.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Default model for every tool. Override with CLAUDE_MODEL in .env or the shell.
DEFAULT_MODEL = "claude-fable-5"

# Model that transparently re-serves requests declined by Fable 5's safety
# classifiers (server-side fallback, same API call).
FALLBACK_MODEL = "claude-opus-4-8"

SERVER_SIDE_FALLBACK_BETA = "server-side-fallback-2026-06-01"


def get_model() -> str:
    return os.getenv("CLAUDE_MODEL", DEFAULT_MODEL)


def get_api_key() -> str | None:
    return os.getenv("ANTHROPIC_API_KEY")
