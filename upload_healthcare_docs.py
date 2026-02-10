"""
Upload Healthcare Documents to Contextual AI Datastore
=======================================================
Creates a dedicated healthcare datastore and uploads all PDFs.
Then updates the agent to use the new datastore.
"""

import os
import sys
import time
import glob
from dotenv import load_dotenv
from contextual import ContextualAI

load_dotenv()

API_KEY = os.environ.get("CONTEXTUAL_API_KEY")
if not API_KEY:
    print("ERROR: Set CONTEXTUAL_API_KEY in your .env file")
    sys.exit(1)

# Agent ID from build_healthcare_agent.py
AGENT_ID = os.environ.get("AGENT_ID", "fd173c56-7f3b-4a1c-ade1-39b9211dd675")
DOCS_DIR = os.path.join(os.path.dirname(__file__), "healthcare_docs")

client = ContextualAI(api_key=API_KEY)

# ─── Step 1: Create Healthcare Datastore ─────────────────────────────────────

print("=" * 60)
print("Creating Healthcare Knowledge Base datastore...")
print("=" * 60)

datastore = client.datastores.create(name="Healthcare Knowledge Base")
DATASTORE_ID = datastore.id
print(f"Datastore created: {DATASTORE_ID}\n")

# ─── Step 2: Upload All PDFs ─────────────────────────────────────────────────

pdf_files = sorted(glob.glob(os.path.join(DOCS_DIR, "*.pdf")))
print(f"Found {len(pdf_files)} PDF files to upload:\n")

uploaded_docs = []
for pdf_path in pdf_files:
    filename = os.path.basename(pdf_path)
    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"  Uploading: {filename} ({size_mb:.1f} MB)...", end=" ", flush=True)

    try:
        with open(pdf_path, "rb") as f:
            result = client.datastores.documents.ingest(
                datastore_id=DATASTORE_ID,
                file=f,
            )
        uploaded_docs.append({"id": result.id, "name": filename})
        print(f"OK (doc_id: {result.id})")
    except Exception as e:
        print(f"FAILED: {e}")

print(f"\nUploaded {len(uploaded_docs)}/{len(pdf_files)} documents.")

# ─── Step 3: Wait for Ingestion ──────────────────────────────────────────────

print("\n" + "=" * 60)
print("Waiting for document ingestion to complete...")
print("=" * 60)

max_wait = 300  # 5 minutes max
start_time = time.time()

while time.time() - start_time < max_wait:
    all_done = True
    for doc in uploaded_docs:
        try:
            metadata = client.datastores.documents.metadata(
                datastore_id=DATASTORE_ID,
                document_id=doc["id"],
            )
            status = metadata.status
            if status != "completed":
                all_done = False
                print(f"  {doc['name']}: {status}")
        except Exception:
            all_done = False

    if all_done:
        print("\nAll documents ingested successfully!")
        break

    elapsed = int(time.time() - start_time)
    print(f"  ... waiting ({elapsed}s elapsed)")
    time.sleep(10)
else:
    print("\nTimeout waiting for ingestion. Some docs may still be processing.")
    print("You can check status in the GUI at https://app.contextual.ai")

# ─── Step 4: Update Agent to Use New Datastore ──────────────────────────────

print("\n" + "=" * 60)
print("Updating agent to use Healthcare Knowledge Base...")
print("=" * 60)

try:
    agent = client.agents.update(
        agent_id=AGENT_ID,
        datastore_ids=[DATASTORE_ID],
    )
    print(f"Agent updated! Now using datastore: {DATASTORE_ID}")
except Exception as e:
    print(f"Could not auto-update agent: {e}")
    print(f"Manually update the agent in the GUI to use datastore: {DATASTORE_ID}")

# ─── Summary ─────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("HEALTHCARE DATASTORE READY!")
print("=" * 60)
print(f"""
Datastore ID:  {DATASTORE_ID}
Agent ID:      {AGENT_ID}
Documents:     {len(uploaded_docs)} uploaded

Documents included:
""")
for doc in uploaded_docs:
    print(f"  - {doc['name']}")

print(f"""
Next: Run the demo again to see improved healthcare responses:
  source venv/bin/activate
  python query_agent.py "{AGENT_ID}" --demo
""")
