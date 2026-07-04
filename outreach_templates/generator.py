"""
Job Outreach Template System

Drop in role title, hiring manager name, and team-specific angle —
get a ready-to-send message in seconds. Supports internal referral
and external cold outreach variants.

Usage:
    python -m outreach_templates.generator --role "Staff PM, Identity" --company "Google" --contact "Jane Doe" --angle "identity platform"
    python -m outreach_templates.generator --role "Senior PM" --company "LiveRamp" --contact "John Smith" --type internal
    python -m outreach_templates.generator --batch contacts.json --output drafts/
"""

import argparse
import json
import sys
from pathlib import Path

from toolkit import config
from toolkit.client import complete_json, handle_errors

PROFILE = {
    "name": "Shubham Safaya",
    "title": "Senior Product Manager",
    "company": "Walmart Global Tech",
    "domain": "identity resolution and data platform products",
    "metrics": [
        "22M+ identity records processed",
        "$15M+ incremental ad revenue",
        "$5.8M cost savings",
        "32M+ record identity graph",
    ],
}

# ── Built-in Templates (no API needed) ─────────────────────────────

TEMPLATES = {
    "external_email": {
        "subject": "{role} at {company} — identity and data platform PM",
        "body": """Hi {contact},

I came across the {role} position at {company} and wanted to reach out directly. I lead identity resolution and data platform products at Walmart Global Tech, where I've built systems processing 22M+ identity records and driven $15M+ in incremental ad revenue.

{angle_paragraph}

I'd welcome a 15-minute conversation about how my experience maps to what you're building. Happy to work around your schedule.

Best,
Shubham Safaya""",
    },
    "external_linkedin": {
        "body": "Hi {contact}, I saw the {role} opening at {company}. I lead identity resolution and data platform products at Walmart Global Tech — processing 22M+ identity records and driving $15M+ in ad revenue. {angle_sentence} Would love to connect about the role if you have a few minutes.",
    },
    "internal_referral": {
        "subject": "Referral request — {role} at {company}",
        "body": """Hi {contact},

Hope you're doing well. I saw the {role} opening on your team and wanted to reach out — I think there's a strong fit given my work on identity and data platforms at Walmart.

{angle_paragraph}

Would you be open to a quick chat about the role, and potentially putting in a referral if it seems like a match? Happy to send over my resume and any context that would make the referral easy for you.

Thanks,
Shubham""",
    },
    "internal_linkedin": {
        "body": "Hi {contact}, hope you're well. I'm interested in the {role} position on your team at {company}. I lead identity and data platform products at Walmart — {angle_sentence} Would you be open to a quick chat about the role?",
    },
}


ANGLE_SCHEMA = {
    "type": "object",
    "properties": {
        "angle_paragraph": {
            "type": "string",
            "description": "2-sentence paragraph connecting the background to this opportunity",
        },
        "angle_sentence": {
            "type": "string",
            "description": "1-sentence version of the same connection, for LinkedIn DMs",
        },
    },
    "required": ["angle_paragraph", "angle_sentence"],
    "additionalProperties": False,
}


def generate_angle(role: str, company: str, angle: str) -> dict:
    """Generate angle-specific paragraphs. Uses AI if available, falls back to templates."""
    if config.get_api_key():
        try:
            return complete_json(
                f"""Generate two things for a job outreach message:

1. A 2-sentence "angle paragraph" connecting Shubham Safaya's background (identity resolution, data platforms, 22M+ identity records, $15M+ ad revenue at Walmart Global Tech) to this specific opportunity.
2. A 1-sentence "angle sentence" version of the same connection (for LinkedIn DMs).

Role: {role}
Company: {company}
Team/domain angle: {angle}""",
                schema=ANGLE_SCHEMA,
                max_tokens=2048,
            )
        except Exception:
            pass

    # Fallback
    return {
        "angle_paragraph": f"My work on identity resolution and data platform products maps directly to what your team is building around {angle}. The systems I've architected handle identity data at scale and I've navigated the same technical and privacy challenges your team likely faces.",
        "angle_sentence": f"My identity and data platform work connects directly to your team's focus on {angle}.",
    }


def generate_messages(role: str, company: str, contact: str, angle: str, msg_type: str = "external") -> dict:
    angles = generate_angle(role, company, angle)

    results = {}
    if msg_type == "external":
        keys = ["external_email", "external_linkedin"]
    elif msg_type == "internal":
        keys = ["internal_referral", "internal_linkedin"]
    else:
        keys = list(TEMPLATES.keys())

    for key in keys:
        template = TEMPLATES[key]
        formatted = {}
        for field, text in template.items():
            formatted[field] = text.format(
                role=role,
                company=company,
                contact=contact,
                angle_paragraph=angles["angle_paragraph"],
                angle_sentence=angles["angle_sentence"],
            )
        results[key] = formatted

    return results


def generate_batch(contacts_file: str, output_dir: str | None = None) -> list[dict]:
    contacts = json.loads(Path(contacts_file).read_text())
    all_results = []

    for entry in contacts:
        print(f"Generating for {entry['company']} — {entry['role']}...")
        messages = generate_messages(
            role=entry["role"],
            company=entry["company"],
            contact=entry.get("contact", "Hiring Manager"),
            angle=entry.get("angle", ""),
            msg_type=entry.get("type", "external"),
        )
        all_results.append({"input": entry, "messages": messages})

    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        output_file = out_path / "outreach_drafts.json"
        output_file.write_text(json.dumps(all_results, indent=2))
        print(f"Saved: {output_file}")

    return all_results


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Generate job outreach messages")
    parser.add_argument("--role", type=str, help="Job title")
    parser.add_argument("--company", type=str, help="Company name")
    parser.add_argument("--contact", type=str, default="Hiring Manager", help="Contact name")
    parser.add_argument("--angle", type=str, default="", help="Team-specific angle or domain")
    parser.add_argument("--type", type=str, default="external", choices=["external", "internal", "all"],
                        help="Message type: external (cold), internal (referral), or all")
    parser.add_argument("--batch", type=str, help="JSON file with multiple contacts for batch generation")
    parser.add_argument("--output", type=str, help="Output directory")
    args = parser.parse_args(argv)

    if args.batch:
        results = generate_batch(args.batch, args.output)
        if not args.output:
            print(json.dumps(results, indent=2))
        return

    if not args.role or not args.company:
        print("Error: --role and --company are required (or use --batch)")
        sys.exit(1)

    messages = generate_messages(args.role, args.company, args.contact, args.angle, args.type)

    for key, content in messages.items():
        print(f"\n{'='*60}")
        print(f"  {key.upper().replace('_', ' ')}")
        print(f"{'='*60}")
        for field, text in content.items():
            if field == "subject":
                print(f"Subject: {text}")
            else:
                print(text)


if __name__ == "__main__":
    main()
