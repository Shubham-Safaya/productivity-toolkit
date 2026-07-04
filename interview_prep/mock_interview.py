"""
Mock Interview System

Run structured mock interviews on demand. Supports behavioral, product sense,
strategy, and technical PM question types. Gets AI-powered feedback on your
responses with scoring on structure, specificity, and signal strength.

Usage:
    python -m interview_prep.mock_interview --type behavioral --questions 3
    python -m interview_prep.mock_interview --type product_sense --role "Staff PM, Identity"
    python -m interview_prep.mock_interview --type strategy --company "Google"
    python -m interview_prep.mock_interview --review-answer "My answer text here" --question "Tell me about a time..."
"""

import argparse
import sys

from toolkit.client import complete, handle_errors

QUESTION_BANKS = {
    "behavioral": [
        "Tell me about a time you had to make a product decision with incomplete data. What was the outcome?",
        "Describe a situation where you had to align multiple stakeholders with conflicting priorities.",
        "Give me an example of a time you killed a feature or initiative. How did you make that call?",
        "Tell me about the most technically complex product you've managed. How did you bridge the gap between engineering and business?",
        "Describe a time you had to push back on leadership. What was at stake?",
        "Tell me about a product launch that didn't go as planned. What did you learn?",
        "Give an example of how you used data to change a product direction.",
        "Describe a time you had to build consensus across teams that didn't report to you.",
        "Tell me about a time you identified an opportunity that wasn't in the roadmap.",
        "How have you handled a situation where engineering said something wasn't feasible?",
    ],
    "product_sense": [
        "How would you improve LinkedIn's identity verification system?",
        "Design a privacy-preserving identity resolution product for the open web.",
        "You're the PM for a retail media network. How do you measure ad effectiveness without third-party cookies?",
        "How would you build a clean room product for a mid-market company?",
        "Design an identity graph that balances accuracy with privacy compliance.",
        "You notice your product's DAU is flat but revenue is growing. What's happening and what do you do?",
        "How would you approach building a first-party data platform for a large retailer?",
        "Design a measurement product that works across walled gardens.",
    ],
    "strategy": [
        "How should a retail media network think about identity in a post-cookie world?",
        "What's your framework for deciding between building vs. buying vs. partnering for a data platform?",
        "How would you prioritize between improving identity match rates vs. expanding to new data sources?",
        "If you were leading product at LiveRamp, what would your 3-year identity strategy look like?",
        "How do you think about platform vs. product strategy for data infrastructure?",
        "What's the right way to think about privacy regulations as a product opportunity rather than a constraint?",
        "How would you build a moat for an identity resolution product?",
    ],
    "technical": [
        "Explain how probabilistic identity matching works and when you'd choose it over deterministic.",
        "Walk me through how you'd architect a system to process 20M+ identity records daily.",
        "How do clean rooms work technically, and what are the product implications?",
        "Explain the tradeoffs between real-time and batch processing for an identity graph.",
        "How would you design an API for identity resolution that serves both internal and external clients?",
        "What are the technical considerations for GDPR/CCPA compliance in an identity product?",
    ],
}

INTERVIEWER_SYSTEM = """You are a senior PM interviewer at a top tech company. You are conducting a {interview_type} interview for a {role} position{company_context}.

Your job:
1. Ask the question provided
2. After the candidate responds, give structured feedback

Feedback format:
SCORE: X/10

STRUCTURE: [How well-organized was the response? Did they use a clear framework?]

SPECIFICITY: [Did they give concrete examples with real metrics, or stay vague?]

SIGNAL STRENGTH: [Would a hiring committee see this as a strong signal? What stood out?]

WHAT WORKED: [1-2 specific things they did well]

WHAT TO IMPROVE: [1-2 specific, actionable suggestions]

REWRITTEN ANSWER: [Optional — if the answer was below 7/10, show a stronger version of their key points]

Be direct and specific. Don't pad with compliments. The candidate is a senior PM who wants real feedback."""


def run_interactive(interview_type: str, num_questions: int, role: str, company: str):
    import random

    questions = QUESTION_BANKS.get(interview_type, QUESTION_BANKS["behavioral"])
    selected = random.sample(questions, min(num_questions, len(questions)))
    company_context = f" at {company}" if company else ""

    print(f"\n{'='*60}")
    print(f"  MOCK INTERVIEW — {interview_type.upper()}")
    print(f"  Role: {role}")
    if company:
        print(f"  Company: {company}")
    print(f"  Questions: {num_questions}")
    print(f"{'='*60}")
    print("\nType your answer after each question. Type 'skip' to skip.")
    print("Type 'quit' to end the session.\n")

    results = []
    for i, question in enumerate(selected, 1):
        print(f"\n--- Question {i}/{len(selected)} ---")
        print(f"\n{question}\n")

        lines = []
        print("Your answer (press Enter twice to submit):")
        empty_count = 0
        while True:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append("")
            else:
                empty_count = 0
                lines.append(line)

            if line.lower() == "quit":
                print("\nEnding session.")
                return results
            if line.lower() == "skip":
                lines = []
                break

        answer = "\n".join(lines).strip()
        if not answer or answer.lower() == "skip":
            print("Skipped.")
            continue

        print("\nAnalyzing your response...")
        system = INTERVIEWER_SYSTEM.format(
            interview_type=interview_type,
            role=role,
            company_context=company_context,
        )

        feedback = complete(
            f"Question: {question}\n\nCandidate's answer:\n{answer}",
            system=system,
            max_tokens=4096,
        )
        print(f"\n{feedback}")
        results.append({
            "question": question,
            "answer": answer,
            "feedback": feedback,
        })

    print(f"\n{'='*60}")
    print(f"  SESSION COMPLETE — {len(results)} questions answered")
    print(f"{'='*60}")
    return results


def review_single(question: str, answer: str, role: str = "Staff PM"):
    system = INTERVIEWER_SYSTEM.format(
        interview_type="behavioral",
        role=role,
        company_context="",
    )

    feedback = complete(
        f"Question: {question}\n\nCandidate's answer:\n{answer}",
        system=system,
        max_tokens=4096,
    )
    print(feedback)


def list_questions(interview_type: str | None = None):
    types = [interview_type] if interview_type else QUESTION_BANKS.keys()
    for t in types:
        questions = QUESTION_BANKS.get(t, [])
        print(f"\n{t.upper()} ({len(questions)} questions)")
        print("-" * 40)
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="PM Mock Interview System")
    parser.add_argument("--type", type=str, default="behavioral",
                        choices=["behavioral", "product_sense", "strategy", "technical"],
                        help="Interview type")
    parser.add_argument("--questions", type=int, default=3, help="Number of questions")
    parser.add_argument("--role", type=str, default="Staff Product Manager", help="Target role")
    parser.add_argument("--company", type=str, default="", help="Target company")
    parser.add_argument("--review-answer", type=str, help="Review a single answer (non-interactive)")
    parser.add_argument("--question", type=str, help="The question for --review-answer")
    parser.add_argument("--list", action="store_true", help="List available questions")
    args = parser.parse_args(argv)

    if args.list:
        list_questions(args.type)
        return

    if args.review_answer:
        if not args.question:
            print("Error: --question is required with --review-answer")
            sys.exit(1)
        review_single(args.question, args.review_answer, args.role)
        return

    run_interactive(args.type, args.questions, args.role, args.company)


if __name__ == "__main__":
    main()
