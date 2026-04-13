"""
EB1A Evidence Tracker

Maps each EB1A criterion to your evidence. Add, view, update, and export
your evidence portfolio. Keeps you audit-ready.

Usage:
    python -m eb1a_tracker.tracker view                          # View all criteria and evidence
    python -m eb1a_tracker.tracker add --criterion published_work --title "LinkedIn Day X Series" --description "30+ posts on identity, data platforms, privacy"
    python -m eb1a_tracker.tracker add --criterion judging --title "Topmate Mentorship" --description "Evaluated product cases for aspiring PMs"
    python -m eb1a_tracker.tracker export --format markdown      # Export for attorney review
    python -m eb1a_tracker.tracker export --format json
    python -m eb1a_tracker.tracker stats                         # Coverage summary
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).parent / "evidence.json"

EB1A_CRITERIA = {
    "awards": {
        "name": "Awards / Prizes",
        "description": "Documentation of nationally or internationally recognized prizes or awards for excellence",
        "uscis_code": "8 CFR 204.5(h)(3)(i)",
    },
    "membership": {
        "name": "Membership in Associations",
        "description": "Documentation of membership in associations that require outstanding achievements",
        "uscis_code": "8 CFR 204.5(h)(3)(ii)",
    },
    "press": {
        "name": "Published Material About You",
        "description": "Published material in professional or major trade publications about you and your work",
        "uscis_code": "8 CFR 204.5(h)(3)(iii)",
    },
    "judging": {
        "name": "Judging the Work of Others",
        "description": "Evidence of participation as a judge of the work of others in your field",
        "uscis_code": "8 CFR 204.5(h)(3)(iv)",
    },
    "original_contributions": {
        "name": "Original Contributions of Major Significance",
        "description": "Evidence of original scientific, scholarly, artistic, athletic, or business-related contributions of major significance",
        "uscis_code": "8 CFR 204.5(h)(3)(v)",
    },
    "published_work": {
        "name": "Authorship of Scholarly Articles",
        "description": "Evidence of authorship of scholarly articles in professional journals or major media",
        "uscis_code": "8 CFR 204.5(h)(3)(vi)",
    },
    "exhibitions": {
        "name": "Artistic Exhibitions or Showcases",
        "description": "Evidence of display of your work at artistic exhibitions or showcases",
        "uscis_code": "8 CFR 204.5(h)(3)(vii)",
    },
    "leading_role": {
        "name": "Leading or Critical Role",
        "description": "Evidence of performing a leading or critical role in distinguished organizations",
        "uscis_code": "8 CFR 204.5(h)(3)(viii)",
    },
    "high_salary": {
        "name": "High Salary or Remuneration",
        "description": "Evidence of commanding a high salary or significantly high remuneration relative to others",
        "uscis_code": "8 CFR 204.5(h)(3)(ix)",
    },
    "commercial_success": {
        "name": "Commercial Success in Performing Arts",
        "description": "Evidence of commercial successes in the performing arts",
        "uscis_code": "8 CFR 204.5(h)(3)(x)",
    },
}


def load_evidence() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"evidence": [], "last_updated": None}


def save_evidence(data: dict):
    data["last_updated"] = date.today().isoformat()
    DATA_FILE.write_text(json.dumps(data, indent=2))


def add_evidence(criterion: str, title: str, description: str, url: str = "", evidence_type: str = ""):
    if criterion not in EB1A_CRITERIA:
        print(f"Error: Unknown criterion '{criterion}'")
        print(f"Valid criteria: {', '.join(EB1A_CRITERIA.keys())}")
        sys.exit(1)

    data = load_evidence()
    entry = {
        "criterion": criterion,
        "title": title,
        "description": description,
        "url": url,
        "evidence_type": evidence_type,
        "date_added": date.today().isoformat(),
        "status": "active",
    }
    data["evidence"].append(entry)
    save_evidence(data)
    print(f"Added: [{EB1A_CRITERIA[criterion]['name']}] {title}")


def view_evidence(criterion_filter: str | None = None):
    data = load_evidence()
    evidence = data.get("evidence", [])

    if criterion_filter:
        evidence = [e for e in evidence if e["criterion"] == criterion_filter]

    # Group by criterion
    grouped = {}
    for e in evidence:
        key = e["criterion"]
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(e)

    for crit_key, info in EB1A_CRITERIA.items():
        items = grouped.get(crit_key, [])
        status = f"({len(items)} items)" if items else "(no evidence yet)"
        print(f"\n{'='*60}")
        print(f"  {info['name']} {status}")
        print(f"  {info['uscis_code']}")
        print(f"{'='*60}")

        if items:
            for i, item in enumerate(items, 1):
                print(f"  {i}. {item['title']}")
                print(f"     {item['description']}")
                if item.get("url"):
                    print(f"     URL: {item['url']}")
                print(f"     Added: {item['date_added']}")
        else:
            print(f"  (none)")


def show_stats():
    data = load_evidence()
    evidence = data.get("evidence", [])

    print(f"\nEB1A Evidence Coverage")
    print(f"Last updated: {data.get('last_updated', 'never')}")
    print(f"{'='*50}")

    total_items = 0
    criteria_with_evidence = 0
    for crit_key, info in EB1A_CRITERIA.items():
        items = [e for e in evidence if e["criterion"] == crit_key]
        count = len(items)
        total_items += count
        if count > 0:
            criteria_with_evidence += 1
        marker = "x" if count > 0 else " "
        print(f"  [{marker}] {info['name']}: {count} items")

    print(f"\n  Total evidence items: {total_items}")
    print(f"  Criteria covered: {criteria_with_evidence}/10")
    print(f"  EB1A requires: 3 of 10 criteria (you need {max(0, 3 - criteria_with_evidence)} more)")

    if criteria_with_evidence >= 3:
        print(f"\n  You meet the minimum threshold.")
    else:
        print(f"\n  Focus on building evidence for {3 - criteria_with_evidence} more criteria.")


def export_evidence(fmt: str, output_path: str | None = None):
    data = load_evidence()
    evidence = data.get("evidence", [])

    if fmt == "json":
        content = json.dumps(data, indent=2)
        ext = "json"
    elif fmt == "markdown":
        lines = [f"# EB1A Evidence Portfolio", f"*Last updated: {data.get('last_updated', 'N/A')}*\n"]
        for crit_key, info in EB1A_CRITERIA.items():
            items = [e for e in evidence if e["criterion"] == crit_key]
            lines.append(f"## {info['name']}")
            lines.append(f"*{info['uscis_code']}*\n")
            if items:
                for item in items:
                    lines.append(f"**{item['title']}**")
                    lines.append(f"{item['description']}")
                    if item.get("url"):
                        lines.append(f"Link: {item['url']}")
                    lines.append("")
            else:
                lines.append("*(No evidence yet)*\n")
        content = "\n".join(lines)
        ext = "md"
    else:
        print(f"Unknown format: {fmt}")
        sys.exit(1)

    if output_path:
        Path(output_path).write_text(content)
        print(f"Exported to: {output_path}")
    else:
        out = Path(__file__).parent / f"evidence_export.{ext}"
        out.write_text(content)
        print(f"Exported to: {out}")


def main():
    parser = argparse.ArgumentParser(description="EB1A Evidence Tracker")
    subparsers = parser.add_subparsers(dest="command")

    # view
    view_parser = subparsers.add_parser("view", help="View all evidence")
    view_parser.add_argument("--criterion", type=str, help="Filter by criterion")

    # add
    add_parser = subparsers.add_parser("add", help="Add evidence")
    add_parser.add_argument("--criterion", type=str, required=True, help=f"Criterion key: {', '.join(EB1A_CRITERIA.keys())}")
    add_parser.add_argument("--title", type=str, required=True, help="Evidence title")
    add_parser.add_argument("--description", type=str, required=True, help="Description")
    add_parser.add_argument("--url", type=str, default="", help="Supporting URL")
    add_parser.add_argument("--evidence-type", type=str, default="", help="Type (e.g., article, video, certificate)")

    # export
    export_parser = subparsers.add_parser("export", help="Export evidence")
    export_parser.add_argument("--format", type=str, default="markdown", choices=["markdown", "json"])
    export_parser.add_argument("--output", type=str, help="Output file path")

    # stats
    subparsers.add_parser("stats", help="Show coverage statistics")

    args = parser.parse_args()

    if args.command == "view":
        view_evidence(args.criterion)
    elif args.command == "add":
        add_evidence(args.criterion, args.title, args.description, args.url, args.evidence_type)
    elif args.command == "export":
        export_evidence(args.format, args.output)
    elif args.command == "stats":
        show_stats()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
