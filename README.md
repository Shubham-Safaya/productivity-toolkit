# Productivity Toolkit

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Anthropic SDK](https://img.shields.io/badge/Anthropic-Claude_API-cc785c.svg)](https://docs.anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Seven CLI tools powered by the Claude API to accelerate career development, content creation, and financial planning.

## Tools

| # | Tool | What it does | Time saved |
|---|------|-------------|------------|
| 1 | **LinkedIn Batch** | Batch-produce "Day X" series posts in your voice | ~25 min/post → ~5 min editing |
| 2 | **Outreach Templates** | Generate cold emails, LinkedIn DMs, and referral messages with variables | ~20 min/message → seconds |
| 3 | **Interview Prep** | Mock PM interviews (behavioral, product sense, strategy) with scored feedback | On-demand, no scheduling |
| 4 | **EB1A Tracker** | Map EB1A criteria to evidence, track coverage, export for attorney review | Always audit-ready |
| 5 | **Medium Drafts** | Thesis + key points → full first draft in your voice | ~3 hours → ~45 min editing |
| 6 | **Financial Review** | Portfolio analysis with concentration risk, rebalancing, NRI tax considerations | Structured monthly review |
| 7 | **Content Repurpose** | One idea → LinkedIn, Medium, YouTube outline, Instagram caption | 1 input → 4 outputs |

## Quick Start

```bash
git clone https://github.com/Shubham-Safaya/productivity-toolkit.git
cd productivity-toolkit
python3 -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

Installing with `pip install -e .` puts a `toolkit` command on your PATH:

```bash
toolkit linkedin --start-day 31 --topics "Topic 1,Topic 2"
toolkit eb1a stats
```

`python cli.py <command>` works identically without installing.

## Configuration

| Env var | Purpose | Default |
|---------|---------|---------|
| `ANTHROPIC_API_KEY` | API key for all AI-powered tools | (required) |
| `CLAUDE_MODEL` | Model used by every tool — one knob for future model swaps | `claude-fable-5` |

Set both in `.env` (see `.env.example`). When running on Claude Fable 5, requests
declined by its safety classifiers automatically fall back to Claude Opus 4.8
within the same API call.

## Usage

All tools are accessible through the unified CLI or as standalone modules
(`python -m linkedin_batch.generator ...`). The examples below use
`python cli.py`; substitute `toolkit` if installed.

### 1. LinkedIn Batch Generator

```bash
# Generate 7 posts at once
python cli.py linkedin --start-day 31 --topics "Privacy-first identity,Clean room adoption,Retail media measurement,First-party data strategy,Identity graphs at scale,Cookie deprecation reality,Platform vs product thinking"

# From a topics file
python cli.py linkedin --start-day 31 --topics-file topics.txt --output drafts/
```

### 2. Outreach Templates

```bash
# Single message
python cli.py outreach --role "Staff PM, Identity" --company "Google" --contact "Jane Doe" --angle "identity platform" --type external

# Internal referral
python cli.py outreach --role "Senior PM" --company "LiveRamp" --contact "John Smith" --type internal

# Batch from file
python cli.py outreach --batch outreach_templates/templates/sample_contacts.json --output drafts/
```

### 3. Mock Interview

```bash
# Interactive session
python cli.py interview --type behavioral --questions 3
python cli.py interview --type product_sense --company "Google" --role "Staff PM"
python cli.py interview --type strategy --questions 2

# Review a single answer
python cli.py interview --review-answer "My answer..." --question "Tell me about a time..."

# List all available questions
python cli.py interview --list
```

### 4. EB1A Evidence Tracker

```bash
# View all evidence
python cli.py eb1a view

# Add new evidence
python cli.py eb1a add --criterion published_work --title "LinkedIn Series" --description "30+ posts on identity and data platforms"

# Check coverage
python cli.py eb1a stats

# Export for attorney
python cli.py eb1a export --format markdown
python cli.py eb1a export --format json
```

Valid criteria: `awards`, `membership`, `press`, `judging`, `original_contributions`, `published_work`, `exhibitions`, `leading_role`, `high_salary`, `commercial_success`

### 5. Medium Article Drafts

```bash
# From command line
python cli.py medium --thesis "Identity maturity is a spectrum, not a binary" --points "Most companies are at level 1,Clean rooms are level 3,Few reach level 5"

# From a brief file
python cli.py medium --brief brief.txt --output draft.md

# Interactive mode
python cli.py medium --interactive
```

### 6. Financial Portfolio Review

```bash
# From portfolio file
python cli.py finance --portfolio portfolio.json
python cli.py finance --portfolio portfolio.json --focus "rebalancing"

# Interactive mode
python cli.py finance --interactive

# See sample portfolio format
python cli.py finance --sample
```

### 7. Content Repurposing

```bash
# From an idea
python cli.py repurpose --idea "Clean rooms are the new CDPs — here's why that framing is wrong"

# From a file, specific formats
python cli.py repurpose --input post.txt --formats linkedin,medium,youtube,instagram

# Save all outputs
python cli.py repurpose --input post.txt --output repurposed/
```

Available formats: `linkedin`, `medium`, `youtube`, `instagram`, `twitter_thread`

## Project Structure

```
productivity-toolkit/
├── cli.py                          # Unified CLI entry point (`toolkit <command>`)
├── toolkit/                        # Shared config + Anthropic client
│   ├── config.py                   #   CLAUDE_MODEL env var, API key lookup
│   └── client.py                   #   Prompt caching, structured outputs, error handling
├── linkedin_batch/generator.py     # LinkedIn "Day X" batch generator
├── outreach_templates/generator.py # Job outreach message generator
├── interview_prep/mock_interview.py # Mock PM interview system
├── eb1a_tracker/tracker.py         # EB1A evidence tracker
├── eb1a_tracker/evidence.json      # Evidence data store
├── medium_drafts/drafter.py        # Medium article draft generator
├── financial_review/reviewer.py    # Portfolio review tool
├── content_repurpose/repurpose.py  # Content repurposing engine
├── tests/test_smoke.py             # Smoke test per subcommand (API mocked)
├── pyproject.toml
└── .env.example
```

## Tests

```bash
pip install -e ".[dev]"
pytest
```

The suite runs one smoke test per subcommand with the API fully mocked — no
network access and no API key needed.

## Requirements

- Python 3.10+
- Anthropic API key (for AI-powered features)
- The EB1A tracker works fully offline (no API needed)

## Notes

- All AI-generated content is a first draft — review and personalize before publishing
- The financial review tool provides analysis, not financial advice
- Outreach templates include both AI-powered and template-based fallbacks
