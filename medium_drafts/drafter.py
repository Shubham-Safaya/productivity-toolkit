"""
Medium Article Draft Generator

Bring your thesis and 3-4 key points, get a full first draft in your voice.
Turns a 3-hour writing session into 45 minutes of reshaping.

Usage:
    python -m medium_drafts.drafter --thesis "Identity maturity is a spectrum, not a binary" --points "Most companies are at level 1,Clean rooms are level 3,Few reach level 5"
    python -m medium_drafts.drafter --brief brief.txt --output draft.md
    python -m medium_drafts.drafter --interactive
"""

import argparse
import sys
from pathlib import Path

from toolkit.client import complete, handle_errors

VOICE_PROMPT = """You are ghostwriting a Medium article for Shubham Safaya, a Senior Product Manager at Walmart Global Tech who leads identity resolution and data platform products.

Writing style rules (CRITICAL):
- Practitioner voice — write as someone who builds these systems, not an observer
- NO emojis
- Use subheadings to break up sections
- Open with a hook that challenges conventional thinking or states a non-obvious truth
- Each section should have a concrete example or real-world pattern (from identity, adtech, data platforms, retail media, privacy)
- End with a synthesis — what this means for the reader's work, not a generic call to action
- 1200-2000 words
- Short paragraphs (2-4 sentences)
- Conversational but substantive — every paragraph should carry signal
- Include a suggested title and subtitle
- Do NOT use phrases like "In today's world", "In the ever-evolving landscape", or similar filler
- Do NOT use bullet points in the body — use flowing prose
- It's fine to use technical terms without over-explaining them — the audience is practitioners
- First person throughout"""


def generate_draft(thesis: str, points: list[str], audience: str = "product managers and data practitioners") -> str:
    points_text = "\n".join(f"- {p}" for p in points)

    return complete(
        f"""Write a Medium article based on:

THESIS: {thesis}

KEY POINTS:
{points_text}

TARGET AUDIENCE: {audience}

Return the complete article in Markdown format, starting with the title as an H1.
Include a suggested subtitle after the title.
Do not include any meta-commentary — just the article itself.""",
        system=VOICE_PROMPT,
        max_tokens=8192,
    )


def interactive_mode():
    print("Medium Article Draft Generator")
    print("=" * 40)

    thesis = input("\nThesis (the core argument of your article):\n> ").strip()
    if not thesis:
        print("Error: thesis is required")
        sys.exit(1)

    print("\nKey points (enter each point, empty line when done):")
    points = []
    while True:
        point = input(f"  {len(points) + 1}. ").strip()
        if not point:
            break
        points.append(point)

    if not points:
        print("Error: at least one key point is required")
        sys.exit(1)

    audience = input("\nTarget audience (press Enter for default 'product managers and data practitioners'):\n> ").strip()
    if not audience:
        audience = "product managers and data practitioners"

    print(f"\nGenerating draft ({len(points)} key points)...")
    draft = generate_draft(thesis, points, audience)

    print(f"\n{'='*60}")
    print(draft)
    print(f"\n{'='*60}")

    save = input("\nSave to file? (enter filename or press Enter to skip): ").strip()
    if save:
        Path(save).write_text(draft)
        print(f"Saved to: {save}")


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Medium Article Draft Generator")
    parser.add_argument("--thesis", type=str, help="Core thesis/argument")
    parser.add_argument("--points", type=str, help="Comma-separated key points")
    parser.add_argument("--audience", type=str, default="product managers and data practitioners")
    parser.add_argument("--brief", type=str, help="Text file with thesis on line 1, points on subsequent lines")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    args = parser.parse_args(argv)

    if args.interactive:
        interactive_mode()
        return

    if args.brief:
        lines = [l.strip() for l in Path(args.brief).read_text().splitlines() if l.strip()]
        if not lines:
            print(f"Error: brief file {args.brief} is empty", file=sys.stderr)
            sys.exit(1)
        thesis = lines[0]
        points = lines[1:]
    elif args.thesis and args.points:
        thesis = args.thesis
        points = [p.strip() for p in args.points.split(",")]
    else:
        print("Error: provide --thesis and --points, --brief, or --interactive")
        sys.exit(1)

    print(f"Generating draft: \"{thesis}\" ({len(points)} points)...")
    draft = generate_draft(thesis, points, args.audience)

    if args.output:
        Path(args.output).write_text(draft)
        print(f"Saved to: {args.output}")
    else:
        print(f"\n{draft}")


if __name__ == "__main__":
    main()
