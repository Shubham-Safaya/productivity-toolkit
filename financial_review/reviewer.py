"""
Financial Portfolio Review Tool

Paste your holdings, get concentration risk analysis, rebalancing suggestions,
and NRI/GIFT City tax considerations.

Usage:
    python -m financial_review.reviewer --portfolio portfolio.json
    python -m financial_review.reviewer --interactive
    python -m financial_review.reviewer --portfolio portfolio.json --focus "rebalancing"
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SAMPLE_PORTFOLIO = {
    "holdings": [
        {"name": "VOO (S&P 500 ETF)", "value_usd": 50000, "category": "US Large Cap"},
        {"name": "VGT (Tech ETF)", "value_usd": 30000, "category": "US Tech"},
        {"name": "VXUS (International ETF)", "value_usd": 15000, "category": "International"},
        {"name": "BND (Bond ETF)", "value_usd": 10000, "category": "Bonds"},
        {"name": "Company RSUs", "value_usd": 40000, "category": "Single Stock"},
        {"name": "Indian MF (via NRE)", "value_inr": 1500000, "category": "India Equity"},
    ],
    "nri_status": True,
    "tax_residency": "US",
    "age": 30,
    "risk_tolerance": "moderate-aggressive",
}

REVIEW_SYSTEM = """You are a financial analysis assistant helping an NRI (Non-Resident Indian) tech professional review their investment portfolio.

Your role:
- Analyze concentration risk (single stock, sector, geography)
- Flag rebalancing opportunities based on stated risk tolerance and age
- Note NRI-specific tax considerations (DTAA, GIFT City, NRE/NRO implications, LTCG/STCG in India)
- Be specific with numbers and percentages
- Flag if any holding exceeds 25% of total portfolio
- Note if tech/single-employer exposure is too high for someone in tech

Style:
- Direct and specific — use actual numbers from the portfolio
- Flag risks clearly but don't be alarmist
- Give actionable suggestions, not generic advice
- Note what you DON'T know (tax bracket, specific goals) and what assumptions you're making

IMPORTANT: You are not a licensed financial advisor. Always note that this is analysis, not financial advice, and recommend consulting a CPA/financial advisor for tax-specific decisions."""


def analyze_portfolio(portfolio: dict, focus: str = "") -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    focus_text = f"\nFocus area: {focus}" if focus else ""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        system=REVIEW_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"""Review this portfolio:{focus_text}

{json.dumps(portfolio, indent=2)}

Provide:
1. PORTFOLIO SUMMARY — total value, allocation breakdown by category
2. CONCENTRATION RISK — any holdings or sectors that are overweight
3. REBALANCING SUGGESTIONS — specific moves based on the data
4. NRI TAX CONSIDERATIONS — relevant tax implications for US-resident NRI
5. ACTION ITEMS — 3-5 specific next steps, prioritized"""
        }]
    )

    return message.content[0].text.strip()


def interactive_mode():
    print("Financial Portfolio Review")
    print("=" * 40)
    print("\nEnter holdings one per line: name, value_usd, category")
    print("Example: VOO, 50000, US Large Cap")
    print("For INR holdings: name, value_inr:1500000, India Equity")
    print("Empty line when done.\n")

    holdings = []
    while True:
        line = input(f"  Holding {len(holdings) + 1}: ").strip()
        if not line:
            break
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            print("    Format: name, value, category")
            continue
        holding = {"name": parts[0], "category": parts[2]}
        if "inr:" in parts[1].lower():
            holding["value_inr"] = int(parts[1].lower().replace("inr:", ""))
        else:
            holding["value_usd"] = int(parts[1].replace("$", "").replace(",", ""))
        holdings.append(holding)

    if not holdings:
        print("No holdings entered.")
        sys.exit(1)

    nri = input("NRI status? (y/n, default y): ").strip().lower() != "n"
    risk = input("Risk tolerance (conservative/moderate/moderate-aggressive/aggressive, default moderate-aggressive): ").strip()
    if not risk:
        risk = "moderate-aggressive"

    portfolio = {
        "holdings": holdings,
        "nri_status": nri,
        "tax_residency": "US",
        "risk_tolerance": risk,
    }

    print("\nAnalyzing portfolio...")
    result = analyze_portfolio(portfolio)
    print(f"\n{result}")


def main():
    parser = argparse.ArgumentParser(description="Financial Portfolio Review")
    parser.add_argument("--portfolio", type=str, help="JSON file with portfolio data")
    parser.add_argument("--focus", type=str, default="", help="Focus area: rebalancing, tax, risk, all")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--sample", action="store_true", help="Show sample portfolio format")
    args = parser.parse_args()

    if args.sample:
        print(json.dumps(SAMPLE_PORTFOLIO, indent=2))
        return

    if args.interactive:
        interactive_mode()
        return

    if not args.portfolio:
        print("Error: provide --portfolio, --interactive, or --sample")
        sys.exit(1)

    portfolio = json.loads(Path(args.portfolio).read_text())
    print("Analyzing portfolio...")
    result = analyze_portfolio(portfolio, args.focus)
    print(f"\n{result}")


if __name__ == "__main__":
    main()
