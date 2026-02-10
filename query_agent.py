"""
Interactive Healthcare Agent Query Tool
========================================
Query your healthcare agent interactively or run demo queries.

Usage:
    python query_agent.py <AGENT_ID>
    python query_agent.py <AGENT_ID> --demo
"""

import os
import sys
from dotenv import load_dotenv
from contextual import ContextualAI

load_dotenv()

API_KEY = os.environ.get("CONTEXTUAL_API_KEY")
if not API_KEY:
    print("ERROR: Set CONTEXTUAL_API_KEY in your .env file")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python query_agent.py <AGENT_ID> [--demo]")
    sys.exit(1)

AGENT_ID = sys.argv[1]
DEMO_MODE = "--demo" in sys.argv

client = ContextualAI(api_key=API_KEY)

# ─── Demo Queries (for recording your submission video) ──────────────────────

DEMO_QUERIES = [
    {
        "category": "Clinical Guidelines",
        "query": "What are the current recommended screening guidelines for common chronic diseases?",
    },
    {
        "category": "Treatment Options",
        "query": "What are the evidence-based treatment approaches for managing Type 2 diabetes?",
    },
    {
        "category": "Drug Information",
        "query": "What are the most important drug interactions that clinicians should be aware of?",
    },
    {
        "category": "Research Synthesis",
        "query": "Summarize the latest research findings on preventive care and lifestyle interventions.",
    },
    {
        "category": "Differential Diagnosis",
        "query": "A patient presents with fatigue, weight gain, and cold intolerance. What conditions should be considered and what initial workup is recommended?",
    },
]


def print_response(response):
    """Pretty-print an agent response with sources."""
    print(f"\n{'─' * 60}")
    print("MedAssist Response:")
    print("─" * 60)
    print(response.message.content)

    if response.retrieval_contents:
        print(f"\n{'─' * 40}")
        print(f"Sources ({len(response.retrieval_contents)} retrieved):")
        print("─" * 40)
        for i, source in enumerate(response.retrieval_contents[:5], 1):
            doc = source.doc_name or "Unknown"
            page = source.page or "N/A"
            preview = (source.content_text[:100] if source.content_text else "(no content)")
            print(f"  {i}. {doc} (p.{page})")
            print(f"     {preview}...")
    print()


def run_demo():
    """Run demo queries for the submission video."""
    print("=" * 60)
    print("  MEDASSIST - Healthcare Research Agent Demo")
    print("=" * 60)
    print()

    conversation_id = None

    for i, demo in enumerate(DEMO_QUERIES, 1):
        print(f"\n{'=' * 60}")
        print(f"  Demo {i}/{len(DEMO_QUERIES)}: {demo['category']}")
        print(f"  Query: {demo['query']}")
        print("=" * 60)

        kwargs = {
            "agent_id": AGENT_ID,
            "messages": [{"role": "user", "content": demo["query"]}],
        }
        if conversation_id:
            kwargs["conversation_id"] = conversation_id

        try:
            response = client.agents.query.create(**kwargs)
            if not conversation_id:
                conversation_id = response.conversation_id
            print_response(response)
        except Exception as e:
            print(f"Error: {e}")

        if i < len(DEMO_QUERIES):
            input("Press Enter for next query...")

    print("\n" + "=" * 60)
    print("  Demo complete! Don't forget to submit your video.")
    print("=" * 60)


def run_interactive():
    """Run interactive chat with the healthcare agent."""
    print("=" * 60)
    print("  MEDASSIST - Interactive Healthcare Chat")
    print("  Type 'quit' to exit, 'new' for new conversation")
    print("=" * 60)

    conversation_id = None

    while True:
        try:
            query = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() == "quit":
            print("Goodbye!")
            break
        if query.lower() == "new":
            conversation_id = None
            print("Started new conversation.")
            continue

        kwargs = {
            "agent_id": AGENT_ID,
            "messages": [{"role": "user", "content": query}],
        }
        if conversation_id:
            kwargs["conversation_id"] = conversation_id

        try:
            response = client.agents.query.create(**kwargs)
            conversation_id = response.conversation_id
            print_response(response)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    if DEMO_MODE:
        run_demo()
    else:
        run_interactive()
