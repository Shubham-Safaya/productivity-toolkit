"""
Content Repurposing Engine

One idea → LinkedIn post, Medium paragraph, YouTube episode outline,
and Instagram caption. Extract full value from every piece of content.

Usage:
    python -m content_repurpose.repurpose --idea "Clean rooms are the new CDPs — here's why that framing is wrong"
    python -m content_repurpose.repurpose --input post.txt --formats linkedin,medium,youtube,instagram
    python -m content_repurpose.repurpose --input post.txt --output repurposed/
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

FORMAT_PROMPTS = {
    "linkedin": """Convert this into a LinkedIn post for Shubham Safaya (Senior PM, identity/data platforms at Walmart Global Tech).
Rules:
- NO emojis, NO bullet points
- Practitioner tone, first person
- 150-250 words
- Short paragraphs (2-3 sentences)
- Open with a concrete observation or contrarian take
- End with a reflective insight
- Add 3-5 hashtags at the end, separated by a blank line""",

    "medium": """Convert this into 2-3 paragraphs suitable for a Medium article section.
Rules:
- Practitioner voice, first person
- NO emojis
- Flowing prose, no bullet points
- Can use one subheading if needed
- 200-400 words
- Include a specific example or real-world pattern
- Technical depth appropriate for PM and data practitioner audience""",

    "youtube": """Convert this into a YouTube episode outline for a product management / tech channel.
Rules:
- Episode title (under 60 chars, compelling)
- Hook (first 30 seconds — what will the viewer learn?)
- 3-5 main segments with talking points (2-3 sentences each)
- Suggested examples or screen shares
- Closing takeaway
- Keep it structured but conversational
- Total target: 8-12 minute episode""",

    "instagram": """Convert this into an Instagram caption for a professional/tech audience.
Rules:
- Hook in the first line (this shows before "more")
- 3-5 short paragraphs
- Conversational but substantive
- Can use line breaks for emphasis
- End with a question to drive comments
- Add 10-15 relevant hashtags in a comment block at the end (separated by blank line)
- 150-300 words total
- NO emojis unless they genuinely add meaning (max 2-3 total)""",

    "twitter_thread": """Convert this into a Twitter/X thread (5-8 tweets).
Rules:
- First tweet is the hook — standalone interesting take
- Each tweet is self-contained but flows as a narrative
- Last tweet is a synthesis or call for discussion
- No emojis
- Under 280 chars per tweet
- Number each tweet (1/, 2/, etc.)""",
}


def repurpose(content: str, formats: list[str]) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    results = {}
    for fmt in formats:
        if fmt not in FORMAT_PROMPTS:
            print(f"  Skipping unknown format: {fmt}")
            continue

        print(f"  Generating {fmt}...")
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""{FORMAT_PROMPTS[fmt]}

SOURCE CONTENT:
{content}

Return ONLY the formatted content, ready to post. No meta-commentary."""
            }]
        )

        results[fmt] = message.content[0].text.strip()

    return results


def main():
    parser = argparse.ArgumentParser(description="Content Repurposing Engine")
    parser.add_argument("--idea", type=str, help="Raw idea or take to repurpose")
    parser.add_argument("--input", type=str, help="Text file with source content")
    parser.add_argument("--formats", type=str, default="linkedin,medium,youtube,instagram",
                        help="Comma-separated output formats: linkedin,medium,youtube,instagram,twitter_thread")
    parser.add_argument("--output", type=str, help="Output directory (prints to stdout if omitted)")
    args = parser.parse_args()

    if args.input:
        content = Path(args.input).read_text().strip()
    elif args.idea:
        content = args.idea
    else:
        print("Error: provide --idea or --input")
        sys.exit(1)

    formats = [f.strip() for f in args.formats.split(",")]
    print(f"Repurposing into {len(formats)} formats...")

    results = repurpose(content, formats)

    if args.output:
        out_path = Path(args.output)
        out_path.mkdir(parents=True, exist_ok=True)
        for fmt, text in results.items():
            file = out_path / f"{fmt}.txt"
            file.write_text(text)
            print(f"  Saved: {file}")

        manifest = out_path / "repurpose_manifest.json"
        manifest.write_text(json.dumps({
            "source": content[:200] + "..." if len(content) > 200 else content,
            "formats": list(results.keys()),
        }, indent=2))
        print(f"  Manifest: {manifest}")
    else:
        for fmt, text in results.items():
            print(f"\n{'='*60}")
            print(f"  {fmt.upper()}")
            print(f"{'='*60}")
            print(text)


if __name__ == "__main__":
    main()
