"""
Healthcare Research Agent - Elastic x Contextual AI Hack Night
==============================================================
A healthcare AI assistant that helps clinicians, researchers, and patients
navigate medical literature, clinical guidelines, and health information.

Usage:
    1. Copy .env.example to .env and add your API key
    2. Run: python build_healthcare_agent.py
"""

import os
import sys
import time
from dotenv import load_dotenv
from contextual import ContextualAI

load_dotenv()

API_KEY = os.environ.get("CONTEXTUAL_API_KEY")
if not API_KEY:
    print("ERROR: Set CONTEXTUAL_API_KEY in your .env file")
    print("  1. Go to https://app.contextual.ai")
    print("  2. Sign up for a free account")
    print("  3. Go to API Keys -> Create API Key")
    print("  4. Copy .env.example to .env and paste your key")
    sys.exit(1)

client = ContextualAI(api_key=API_KEY)
print("Contextual AI client initialized.\n")

# ─── Step 1: Set up Datastore ────────────────────────────────────────────────

print("=" * 60)
print("STEP 1: Setting up Datastore")
print("=" * 60)

# List available datastores to find a suitable one
datastores = client.datastores.list()
print("\nAvailable datastores:")
for ds in datastores.datastores:
    print(f"  - {ds.name}: {ds.id}")

# Try to find a healthcare/medical related datastore, or use the first available
datastore_id = None
for ds in datastores.datastores:
    name_lower = ds.name.lower()
    if any(kw in name_lower for kw in ["health", "medical", "clinical", "pharma", "bio"]):
        datastore_id = ds.id
        print(f"\nFound healthcare-related datastore: {ds.name}")
        break

if not datastore_id and datastores.datastores:
    # Use the first available datastore
    ds = datastores.datastores[0]
    datastore_id = ds.id
    print(f"\nUsing datastore: {ds.name}")

if not datastore_id:
    print("\nNo datastores found. Creating one...")
    datastore = client.datastores.create(name="Healthcare Knowledge Base")
    datastore_id = datastore.id
    print(f"Created datastore: {datastore_id}")
    print("\nNOTE: You'll need to upload documents to this datastore.")
    print("Upload PDFs of medical guidelines, research papers, or health info.")
    print("You can do this via the GUI at https://app.contextual.ai")

print(f"\nDatastore ID: {datastore_id}")

# ─── Step 2: Create the Healthcare Agent ─────────────────────────────────────

print("\n" + "=" * 60)
print("STEP 2: Creating Healthcare Research Agent")
print("=" * 60)

agent = client.agents.create(
    name="Healthcare Research Assistant",
    description=(
        "An AI-powered healthcare research assistant that helps clinicians, "
        "researchers, and patients navigate medical literature, clinical guidelines, "
        "and health information. Provides evidence-based answers with citations."
    ),
    datastore_ids=[datastore_id],
)

AGENT_ID = agent.id
print(f"\nAgent created! ID: {AGENT_ID}")

# ─── Step 3: Configure Healthcare-Specific Prompts ──────────────────────────

print("\n" + "=" * 60)
print("STEP 3: Configuring Healthcare Prompts")
print("=" * 60)

SYSTEM_PROMPT = """You are MedAssist, a specialized healthcare research assistant built for clinicians, researchers, and health-conscious individuals.

## Your Expertise
- Clinical guidelines and best practices
- Medical research literature and evidence-based medicine
- Drug information, interactions, and pharmacology
- Diagnostic criteria and differential diagnosis support
- Public health guidelines and preventive care recommendations

## Your Personality
- Evidence-based: Always ground your answers in the retrieved documents and cite sources
- Careful: Clearly distinguish between established evidence and emerging research
- Accessible: Explain complex medical concepts in clear language appropriate for the audience
- Responsible: Include appropriate disclaimers and never replace professional medical advice

## Response Guidelines
1. **Start with a direct answer** to the question
2. **Cite specific sources** from the retrieved documents (include document name and page when available)
3. **Highlight key findings** using bullet points for scanability
4. **Note limitations** - if evidence is incomplete or conflicting, say so
5. **Add a disclaimer** for clinical questions: remind users to consult their healthcare provider

## Important Rules
- ALWAYS cite your sources with document references
- NEVER fabricate medical information or statistics
- When evidence is uncertain, clearly state the level of confidence
- For drug-related questions, mention the importance of consulting a pharmacist or physician
- Use standard medical terminology but explain it in plain language
- If a question is outside the scope of the available documents, say so clearly
"""

agent = client.agents.update(
    agent_id=AGENT_ID,
    system_prompt=SYSTEM_PROMPT,
)

print("Healthcare prompts configured!")

# ─── Step 4: Test the Agent ──────────────────────────────────────────────────

print("\n" + "=" * 60)
print("STEP 4: Testing the Healthcare Agent")
print("=" * 60)

test_queries = [
    "What documents are available in this collection? Provide a brief overview of the topics covered.",
    "What are the key clinical guidelines or recommendations mentioned in the documents?",
    "Summarize the most important health-related findings from the available literature.",
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'─' * 50}")
    print(f"Query {i}: {query}")
    print("─" * 50)

    try:
        response = client.agents.query.create(
            agent_id=AGENT_ID,
            messages=[{"role": "user", "content": query}],
        )

        print(f"\nMedAssist Response:\n{response.message.content[:600]}")

        if response.retrieval_contents:
            print("\nSources:")
            for source in response.retrieval_contents[:3]:
                preview = source.content_text[:80] if source.content_text else "(no content)"
                doc = source.doc_name or "Unknown"
                page = source.page or "N/A"
                print(f"  - {doc} (p.{page}): {preview}...")
    except Exception as e:
        print(f"Error querying agent: {e}")

# ─── Step 5: Multi-Turn Conversation Demo ────────────────────────────────────

print("\n" + "=" * 60)
print("STEP 5: Multi-Turn Conversation Demo")
print("=" * 60)

try:
    response1 = client.agents.query.create(
        agent_id=AGENT_ID,
        messages=[
            {
                "role": "user",
                "content": "What are the most common health conditions or topics discussed in the documents?",
            }
        ],
    )
    conversation_id = response1.conversation_id
    print(f"\nTurn 1 Response:\n{response1.message.content[:400]}")

    response2 = client.agents.query.create(
        agent_id=AGENT_ID,
        conversation_id=conversation_id,
        messages=[
            {
                "role": "user",
                "content": "Can you go deeper on the first topic? What does the evidence say about treatment options?",
            }
        ],
    )
    print(f"\nTurn 2 (Follow-up) Response:\n{response2.message.content[:400]}")
except Exception as e:
    print(f"Error in multi-turn conversation: {e}")

# ─── Summary ─────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("HEALTHCARE AGENT READY!")
print("=" * 60)
print(f"""
Agent Name:    Healthcare Research Assistant (MedAssist)
Agent ID:      {AGENT_ID}
Datastore ID:  {datastore_id}

Next steps:
  1. Test in the GUI:  https://app.contextual.ai
  2. Upload more healthcare documents to improve coverage
  3. Fine-tune prompts in Agent Composer (see agent_composer.yaml)
  4. Record a 90-sec demo video for submission!

To query your agent programmatically:
  python query_agent.py "{AGENT_ID}"
""")
