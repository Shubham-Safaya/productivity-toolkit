"""Smoke tests: one per CLI subcommand, with the Anthropic API fully mocked.

The fake client is installed by patching ``toolkit.client.get_client``, so no
test can ever hit the network. Each test drives the real argparse path via
``cli.main([...])``.
"""

import json
from types import SimpleNamespace

import pytest

import cli
from toolkit import client as toolkit_client
from toolkit import config as toolkit_config


class FakeAPI:
    """Stands in for anthropic.Anthropic. Records every request it receives."""

    DEFAULT_TEXT = "Generated draft text for smoke testing."
    JSON_TEXT = json.dumps({
        "angle_paragraph": "Fake angle paragraph connecting background to role.",
        "angle_sentence": "Fake angle sentence.",
    })

    def __init__(self):
        self.calls: list[dict] = []
        self.stop_reason = "end_turn"
        self.messages = SimpleNamespace(create=self._create)
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        text = self.JSON_TEXT if "output_config" in kwargs else self.DEFAULT_TEXT
        return SimpleNamespace(
            stop_reason=self.stop_reason,
            content=[
                # Fable 5 responses carry thinking blocks before the text block
                SimpleNamespace(type="thinking", thinking=""),
                SimpleNamespace(type="text", text=text),
            ],
        )


@pytest.fixture
def fake_api(monkeypatch):
    api = FakeAPI()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.delenv("CLAUDE_MODEL", raising=False)
    monkeypatch.setattr(toolkit_client, "get_client", lambda: api)
    return api


# ── one smoke test per subcommand ──────────────────────────────────


def test_linkedin(fake_api, tmp_path):
    cli.main(["linkedin", "--start-day", "5", "--topics", "Topic A,Topic B",
              "--output", str(tmp_path)])

    assert (tmp_path / "day_5.txt").read_text() == FakeAPI.DEFAULT_TEXT
    assert (tmp_path / "day_6.txt").exists()
    manifest = json.loads((tmp_path / "batch_manifest.json").read_text())
    assert [p["topic"] for p in manifest] == ["Topic A", "Topic B"]

    call = fake_api.calls[0]
    assert call["model"] == "claude-fable-5"
    # static voice prompt is a cache-marked system block
    assert call["system"][0]["cache_control"] == {"type": "ephemeral"}
    # Fable-class requests opt into the server-side refusal fallback
    assert call["betas"] == [toolkit_config.SERVER_SIDE_FALLBACK_BETA]
    assert call["fallbacks"] == [{"model": toolkit_config.FALLBACK_MODEL}]


def test_outreach(fake_api, capsys):
    cli.main(["outreach", "--role", "Staff PM", "--company", "Acme",
              "--contact", "Jane", "--angle", "identity"])

    out = capsys.readouterr().out
    assert "Fake angle paragraph" in out  # email uses the structured angle
    assert "Fake angle sentence." in out  # DM uses the one-liner
    # angle generation used structured outputs with a strict schema
    fmt = fake_api.calls[0]["output_config"]["format"]
    assert fmt["type"] == "json_schema"
    assert fmt["schema"]["additionalProperties"] is False


def test_outreach_falls_back_to_templates_without_api_key(monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    cli.main(["outreach", "--role", "Staff PM", "--company", "Acme"])
    out = capsys.readouterr().out
    assert "identity resolution and data platform products" in out


def test_interview_review(fake_api, capsys):
    cli.main(["interview", "--review-answer", "I shipped an identity graph.",
              "--question", "Tell me about a complex product."])

    assert FakeAPI.DEFAULT_TEXT in capsys.readouterr().out
    # interviewer rubric goes through the system prompt, not the user turn
    assert "senior PM interviewer" in fake_api.calls[0]["system"][0]["text"]


def test_eb1a_offline(fake_api, tmp_path, capsys, monkeypatch):
    from eb1a_tracker import tracker
    monkeypatch.setattr(tracker, "DATA_FILE", tmp_path / "evidence.json")

    cli.main(["eb1a", "add", "--criterion", "judging",
              "--title", "Mentorship", "--description", "Evaluated PM cases"])
    cli.main(["eb1a", "stats"])
    cli.main(["eb1a", "export", "--format", "markdown",
              "--output", str(tmp_path / "export.md")])

    out = capsys.readouterr().out
    assert "Judging the Work of Others: 1 items" in out
    assert "Mentorship" in (tmp_path / "export.md").read_text()
    assert fake_api.calls == []  # the tracker must never touch the API


def test_medium(fake_api, tmp_path):
    draft_file = tmp_path / "draft.md"
    cli.main(["medium", "--thesis", "Identity maturity is a spectrum",
              "--points", "Point one,Point two", "--output", str(draft_file)])

    assert draft_file.read_text() == FakeAPI.DEFAULT_TEXT
    assert "Identity maturity is a spectrum" in fake_api.calls[0]["messages"][0]["content"]


def test_finance(fake_api, tmp_path, capsys):
    from financial_review.reviewer import SAMPLE_PORTFOLIO
    portfolio = tmp_path / "portfolio.json"
    portfolio.write_text(json.dumps(SAMPLE_PORTFOLIO))

    cli.main(["finance", "--portfolio", str(portfolio), "--focus", "rebalancing"])

    assert FakeAPI.DEFAULT_TEXT in capsys.readouterr().out
    call = fake_api.calls[0]
    assert "Focus area: rebalancing" in call["messages"][0]["content"]
    assert "not a licensed financial advisor" in call["system"][0]["text"]


def test_repurpose(fake_api, tmp_path):
    cli.main(["repurpose", "--idea", "Clean rooms are the new CDPs",
              "--formats", "linkedin,twitter_thread", "--output", str(tmp_path)])

    assert (tmp_path / "linkedin.txt").exists()
    assert (tmp_path / "twitter_thread.txt").exists()
    assert len(fake_api.calls) == 2  # one request per format


# ── shared client behavior ─────────────────────────────────────────


def test_model_override_via_env(fake_api, monkeypatch):
    monkeypatch.setenv("CLAUDE_MODEL", "claude-opus-4-8")
    toolkit_client.complete("hello")

    call = fake_api.calls[0]
    assert call["model"] == "claude-opus-4-8"
    # non-Fable models take the plain (non-beta, no-fallback) path
    assert "betas" not in call and "fallbacks" not in call


def test_refusal_raises_toolkit_error(fake_api):
    fake_api.stop_reason = "refusal"
    with pytest.raises(toolkit_client.ToolkitError, match="declined"):
        toolkit_client.complete("hello")


def test_missing_api_key_raises_toolkit_error(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(toolkit_client, "_client", None)
    with pytest.raises(toolkit_client.ToolkitError, match="ANTHROPIC_API_KEY"):
        toolkit_client.get_client()


def test_cli_help_lists_all_commands(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    for command in cli.COMMANDS:
        assert command in out
