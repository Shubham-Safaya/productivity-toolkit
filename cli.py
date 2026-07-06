"""
Productivity Toolkit — Unified CLI

Entry point for all 7 tools. Run any tool as a subcommand.

Usage:
    toolkit linkedin --start-day 31 --topics "Topic 1,Topic 2,Topic 3"
    toolkit outreach --role "Staff PM" --company "Google" --contact "Jane Doe"
    toolkit interview --type behavioral --questions 3
    toolkit eb1a view
    toolkit medium --thesis "Your thesis" --points "Point 1,Point 2"
    toolkit finance --interactive
    toolkit repurpose --idea "Your idea or take"

`python cli.py <command>` works identically for a non-installed checkout.
"""

import argparse
import importlib
import sys

# command -> (module exposing main(argv), help text)
COMMANDS = {
    "linkedin": ("linkedin_batch.generator", "Batch-generate LinkedIn 'Day X' series posts"),
    "outreach": ("outreach_templates.generator", "Generate job outreach messages (cold email, LinkedIn DM, referral)"),
    "interview": ("interview_prep.mock_interview", "Run mock PM interviews with AI feedback"),
    "eb1a": ("eb1a_tracker.tracker", "Track EB1A evidence across all 10 criteria"),
    "medium": ("medium_drafts.drafter", "Generate Medium article first drafts"),
    "finance": ("financial_review.reviewer", "Portfolio review with concentration risk and NRI tax analysis"),
    "repurpose": ("content_repurpose.repurpose", "Repurpose one idea into LinkedIn, Medium, YouTube, Instagram"),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="toolkit",
        description="Productivity Toolkit — 7 CLI tools powered by the Claude API",
        epilog="Run any command with --help for full usage, e.g. `toolkit linkedin --help`.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")
    for name, (_, help_text) in COMMANDS.items():
        # add_help=False so `toolkit <command> --help` is forwarded to the
        # tool's own parser instead of being swallowed here
        subparsers.add_parser(name, help=help_text, add_help=False)
    return parser


def main(argv: list[str] | None = None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "help":  # backward-compat: `python cli.py help`
        argv = ["--help"]

    parser = build_parser()
    # parse_known_args: the subcommand's own flags stay unparsed here and are
    # forwarded verbatim to the tool's parser
    ns, tool_args = parser.parse_known_args(argv)

    if not ns.command:
        parser.print_help()
        return

    module_name, _ = COMMANDS[ns.command]
    module = importlib.import_module(module_name)
    module.main(tool_args)


if __name__ == "__main__":
    main()
