"""
Productivity Toolkit — Unified CLI

Entry point for all 7 tools. Run any tool as a subcommand.

Usage:
    python cli.py linkedin --start-day 31 --topics "Topic 1,Topic 2,Topic 3"
    python cli.py outreach --role "Staff PM" --company "Google" --contact "Jane Doe"
    python cli.py interview --type behavioral --questions 3
    python cli.py eb1a view
    python cli.py medium --thesis "Your thesis" --points "Point 1,Point 2"
    python cli.py finance --interactive
    python cli.py repurpose --idea "Your idea or take"
"""

import sys


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    command = sys.argv[1]
    sys.argv = [sys.argv[0]] + sys.argv[2:]  # Strip the subcommand for argparse

    if command == "linkedin":
        from linkedin_batch.generator import main as run
        run()
    elif command == "outreach":
        from outreach_templates.generator import main as run
        run()
    elif command == "interview":
        from interview_prep.mock_interview import main as run
        run()
    elif command == "eb1a":
        from eb1a_tracker.tracker import main as run
        run()
    elif command == "medium":
        from medium_drafts.drafter import main as run
        run()
    elif command == "finance":
        from financial_review.reviewer import main as run
        run()
    elif command == "repurpose":
        from content_repurpose.repurpose import main as run
        run()
    elif command in ("help", "--help", "-h"):
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()
        sys.exit(1)


def print_help():
    print("""
Productivity Toolkit
====================

Commands:
  linkedin    Batch-generate LinkedIn "Day X" series posts
  outreach    Generate job outreach messages (cold email, LinkedIn DM, referral)
  interview   Run mock PM interviews with AI feedback
  eb1a        Track EB1A evidence across all 10 criteria
  medium      Generate Medium article first drafts
  finance     Portfolio review with concentration risk and NRI tax analysis
  repurpose   Repurpose one idea into LinkedIn, Medium, YouTube, Instagram

Run any command with --help for full usage:
  python cli.py linkedin --help
  python cli.py eb1a --help
""")


if __name__ == "__main__":
    main()
