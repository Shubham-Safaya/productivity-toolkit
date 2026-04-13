"""
LinkedIn "Day X" Series — Batch Post Generator

Produces multiple LinkedIn posts in one sitting. Feed it a list of topics
and day numbers, get back ready-to-publish drafts in your voice.

Usage:
    python -m linkedin_batch.generator --start-day 31 --topics "Privacy-first identity,Clean room adoption,Retail media measurement"
    python -m linkedin_batch.generator --topics-file topics.txt --start-day 31
    python -m linkedin_batch.generator --start-day 31 --topics "Topic 1,Topic 2" --output drafts/
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

VOICE_PROMPT = """You are ghostwriting LinkedIn posts for Shubham Safaya, a Senior Product Manager at Walmart Global Tech who leads identity resolution and data platform products.

Writing style rules (CRITICAL — violating any of these means the draft is unusable):
- NO emojis whatsoever
- NO bullet points or lists
- Practitioner tone — write like someone who builds these systems, not someone who comments on them
- Short paragraphs (2-3 sentences max)
- Open with a concrete observation or contrarian take, not "Day X of..."
- The "Day X of building in public" framing should appear naturally in the first line or two, not as a header
- End with a reflective insight or forward-looking thought, not a call to action
- 150-250 words per post
- No hashtags in the body — add 3-5 relevant hashtags at the very end, separated by a blank line
- Write in first person
- Be specific — reference real patterns in identity, adtech, data platforms, privacy, retail media
- Do not be generic or motivational. Every sentence should carry signal."""


def generate_batch(topics: list[str], start_day: int, output_dir: str | None = None) -> list[dict]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set. Add it to .env or export it.")
        sys.exit(1)

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    posts = []
    for i, topic in enumerate(topics):
        day_num = start_day + i
        print(f"Generating Day {day_num}: {topic}...")

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""{VOICE_PROMPT}

Write a LinkedIn post for Day {day_num} of the "building in public" series.

Topic: {topic}

Return ONLY the post text, ready to copy-paste into LinkedIn. Nothing else."""
            }]
        )

        post_text = message.content[0].text.strip()
        posts.append({
            "day": day_num,
            "topic": topic,
            "post": post_text,
        })
        print(f"  Done ({len(post_text)} chars)")

    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        for p in posts:
            file_path = out_path / f"day_{p['day']}.txt"
            file_path.write_text(p["post"])
            print(f"Saved: {file_path}")

        manifest = out_path / "batch_manifest.json"
        manifest.write_text(json.dumps(posts, indent=2))
        print(f"Manifest: {manifest}")
    else:
        for p in posts:
            print(f"\n{'='*60}")
            print(f"DAY {p['day']} — {p['topic']}")
            print(f"{'='*60}")
            print(p["post"])

    return posts


def main():
    parser = argparse.ArgumentParser(description="Batch-generate LinkedIn 'Day X' posts")
    parser.add_argument("--start-day", type=int, required=True, help="Starting day number")
    parser.add_argument("--topics", type=str, help="Comma-separated list of topics")
    parser.add_argument("--topics-file", type=str, help="File with one topic per line")
    parser.add_argument("--output", type=str, help="Output directory (prints to stdout if omitted)")
    args = parser.parse_args()

    if args.topics_file:
        topics = [line.strip() for line in Path(args.topics_file).read_text().splitlines() if line.strip()]
    elif args.topics:
        topics = [t.strip() for t in args.topics.split(",")]
    else:
        print("Error: provide --topics or --topics-file")
        sys.exit(1)

    generate_batch(topics, args.start_day, args.output)


if __name__ == "__main__":
    main()
