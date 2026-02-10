# MedAssist - Healthcare Research Agent

**Elastic x Contextual AI Hack Night | Challenge 2: Build Your Own Agent**

MedAssist is an AI-powered healthcare research assistant that helps clinicians, researchers, and patients navigate medical literature, clinical guidelines, and health information. Unlike general-purpose LLMs that rely on stale training data, MedAssist uses **up-to-date documents** as its knowledge source — every answer is grounded in real healthcare literature with source citations.

---

## The Problem

- Medical guidelines are **thousands of pages long** across dozens of sources — NIH, CDC, WHO
- Doctors don't have time to read them all during patient care
- General AI chatbots (ChatGPT, etc.) **hallucinate medical facts** with no sources and rely on outdated training data
- When new guidelines are published, LLMs don't know about them until they're retrained

## The Solution

MedAssist is a **RAG (Retrieval-Augmented Generation) pipeline** that:
- Ingests the **latest** healthcare documents directly — no waiting for model retraining
- Answers questions **only from the uploaded documents**, not from the model's training data
- **Cites every claim** with the exact document name and page number
- Supports **follow-up questions** with conversation memory
- Includes **medical disclaimers** automatically

### Why RAG Over a Regular LLM?

| | Regular LLM (ChatGPT) | MedAssist (RAG) |
|---|---|---|
| **Data freshness** | Frozen at training cutoff | Upload new PDFs anytime — instant updates |
| **Sources** | No citations, no way to verify | Every answer cites document + page |
| **Hallucination** | Makes up facts confidently | Only answers from retrieved documents |
| **Customization** | Same model for everyone | Your documents, your prompts, your agent |
| **Patient data** | Can't securely use private data | Enterprise datastores with access controls |

---

## Future Vision: Patient-Specific Recommendations

Today MedAssist searches clinical guidelines. But the same architecture scales to **personalized medicine**:

```
Current (built tonight):
  Guidelines (NIH, CDC, WHO)  -->  Datastore  -->  General recommendations

Future (enterprise deployment):
  Guidelines + Patient Records  -->  Datastore  -->  Personalized recommendations
                                                      for a specific patient
```

A hospital could add:
- **Lab results** — MedAssist flags abnormal values and recommends next steps per guidelines
- **Medication lists** — checks for drug interactions against pharmacovigilance data
- **Radiology reports** — cross-references findings with diagnostic criteria
- **Medical histories** — provides treatment recommendations tailored to the patient

Patient data requires HIPAA compliance and strict access controls. Contextual AI's enterprise platform supports private datastores with role-based access, enabling secure deployment without patient data leaving the hospital's environment.

---

## How It Works

MedAssist is built on the [Contextual AI](https://contextual.ai) platform — an enterprise RAG platform that handles document ingestion, semantic search, reranking, and grounded generation in one stack.

```
User Question
     |
     v
+--------------------+
| 1. DATASTORE       |  Healthcare PDFs (WHO, NIH, CDC guidelines)
|    (Knowledge Base) |  are chunked, embedded, and indexed
+--------------------+
     |
     v
+--------------------+
| 2. RETRIEVAL       |  The agent searches the datastore for
|    (Search + Rank)  |  relevant passages using semantic search,
|                     |  then re-ranks the top 30 results down to 10
+--------------------+
     |
     v
+--------------------+
| 3. RESEARCH LOOP   |  An agentic loop (up to 5 turns) decides
|    (Agent Composer) |  if it needs more info and runs additional
|                     |  searches to build comprehensive context
+--------------------+
     |
     v
+--------------------+
| 4. GENERATION      |  The LLM generates a response grounded in
|    (Claude Sonnet)  |  the retrieved documents, with citations,
|                     |  structured formatting, and disclaimers
+--------------------+
     |
     v
  MedAssist Response
  (with sources cited)
```

### Key Concepts

- **Datastore**: A searchable knowledge base where healthcare PDFs are uploaded, chunked into passages, and indexed for semantic search. Think of it as the agent's "memory" of medical literature.

- **RAG (Retrieval-Augmented Generation)**: Instead of relying only on the LLM's training data, the agent *retrieves* relevant passages from the datastore first, then *generates* a response grounded in those real documents. This prevents hallucination and ensures citations.

- **Agent Composer**: A YAML-based workflow engine that defines multi-step pipelines. Our agent uses three steps: (1) capture the query, (2) research with multiple search passes, (3) generate a cited response.

- **Reranker**: After initial retrieval returns 30 candidate passages, Contextual AI's reranker model (`ctxl-rerank-v2`) scores them for relevance and keeps the top 10. This dramatically improves answer quality.

- **Multi-turn Conversations**: The agent tracks `conversation_id` so follow-up questions retain context from previous exchanges.

---

## Healthcare Documents

The agent's knowledge base includes authoritative medical literature from:

| Document | Source | Topic |
|----------|--------|-------|
| JNC7 Hypertension Guidelines | NIH/NHLBI | Blood pressure classification, treatment algorithms |
| NHLBI Lifestyle & Cardiovascular Risk | NIH/NHLBI | Diet, sodium, exercise effects on heart health |
| HHS Physical Activity Guidelines | US HHS | Federal exercise recommendations for all ages |
| CDC Chronic Disease Surveillance | CDC | Public health monitoring via electronic health records |

New documents can be uploaded at any time — the agent's knowledge updates instantly after ingestion.

---

## Demo Prompts

Try these in order at [app.contextual.ai](https://app.contextual.ai):

| # | Category | Prompt |
|---|----------|--------|
| 1 | Clinical Guidelines | "What are the current blood pressure classification levels and treatment recommendations according to the JNC7 guidelines?" |
| 2 | Lifestyle & Prevention | "What lifestyle modifications are recommended to reduce cardiovascular risk, and what does the evidence say about their effectiveness?" |
| 3 | Follow-up (same chat) | "How much physical activity is recommended per week, and does it differ by age group?" |
| 4 | Clinical Scenario | "A 55-year-old patient has a blood pressure of 152/95 and a BMI of 31. What treatment approach would the guidelines recommend?" |
| 5 | Public Health | "What role do electronic health records play in chronic disease surveillance according to the CDC?" |

---

## Project Structure

```
medassist-healthcare-agent/
|-- build_healthcare_agent.py   # Creates the agent, configures prompts, runs initial tests
|-- upload_healthcare_docs.py   # Creates a healthcare datastore and uploads PDFs
|-- query_agent.py              # Interactive chat + demo mode for testing
|-- agent_composer.yaml         # Agent Composer YAML workflow config
|-- .env.example                # Template for your API key
|-- .gitignore                  # Keeps secrets and large files out of git
```

### What Each File Does

**`build_healthcare_agent.py`** - The main setup script. It:
1. Connects to Contextual AI with your API key
2. Finds or creates a datastore for the agent to search
3. Creates a new agent named "Healthcare Research Assistant"
4. Configures the MedAssist system prompt (identity, expertise, response rules)
5. Runs 3 test queries to verify the agent works
6. Demonstrates multi-turn conversation capability

**`upload_healthcare_docs.py`** - Populates the knowledge base. It:
1. Creates a dedicated "Healthcare Knowledge Base" datastore
2. Uploads all PDFs from the `healthcare_docs/` folder
3. Waits for document ingestion (chunking + indexing) to complete
4. Updates the agent to use the new datastore

**`query_agent.py`** - Two modes for interacting with the agent:
- **Interactive mode**: Chat with MedAssist in your terminal (supports follow-ups)
- **Demo mode** (`--demo`): Runs 5 pre-built healthcare queries across clinical guidelines, treatment options, drug interactions, research synthesis, and differential diagnosis

**`agent_composer.yaml`** - The advanced workflow configuration that defines:
- How the agent searches (tool config, top_k, reranker settings)
- How the agent researches (multi-turn agentic loop with up to 5 search passes)
- How the agent responds (structured format with citations and disclaimers)

---

## How the Prompts Work

The agent uses a carefully designed system prompt with three layers:

### Identity
Defines who MedAssist is — a healthcare research assistant that is evidence-based, careful, accessible, and responsible. This shapes every response.

### Research Guidelines
Tells the agent *when* and *how* to search:
- Search when users ask about conditions, treatments, drugs, or guidelines
- Use broad-to-narrow search strategy
- Cross-reference multiple sources
- Don't search for casual conversation

### Response Guidelines
Controls the output format:
1. Start with a direct answer
2. Cite specific sources with document name and page
3. Use bullet points for key findings
4. Note evidence limitations
5. Add a medical disclaimer

---

## Setup

### Prerequisites
- Python 3.8+
- A free [Contextual AI account](https://app.contextual.ai) (comes with $25-50 in credits)

### Installation

```bash
# Clone the repo
git clone https://github.com/SenayYakut/medassist-healthcare-agent.git
cd medassist-healthcare-agent

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install contextual-client python-dotenv
```

### Configuration

```bash
# Copy the env template and add your API key
cp .env.example .env
```

Edit `.env` and paste your Contextual AI API key:
```
CONTEXTUAL_API_KEY=your-api-key-here
```

To get your API key:
1. Go to [app.contextual.ai](https://app.contextual.ai)
2. Sign up for a free account
3. Expand the sidebar, click **API Keys**
4. Click **Create API Key** and copy it

---

## Usage

### 1. Build the Agent

```bash
python build_healthcare_agent.py
```

This creates the agent, configures healthcare prompts, and runs initial test queries. Save the **Agent ID** it prints at the end.

### 2. Upload Healthcare Documents (Optional)

Place PDF files in a `healthcare_docs/` folder, then:

```bash
python upload_healthcare_docs.py
```

### 3. Chat with MedAssist

**Interactive mode:**
```bash
python query_agent.py <AGENT_ID>
```

**Demo mode** (for recording your submission):
```bash
python query_agent.py <AGENT_ID> --demo
```

### 4. Demo in Browser

Go to [app.contextual.ai](https://app.contextual.ai), click **Agents**, and open **Healthcare Research Assistant** to chat directly in the web UI.

### 5. Agent Composer (Optional - GUI)

For the advanced multi-step workflow:
1. Go to [app.contextual.ai](https://app.contextual.ai)
2. Open your agent and click **Customize**
3. Paste the contents of `agent_composer.yaml`

---

## Built With

- **Platform**: [Contextual AI](https://contextual.ai) - Enterprise RAG agent platform
- **LLM**: Claude Sonnet 4.5 (via Vertex AI)
- **Reranker**: ctxl-rerank-v2-instruct-multilingual
- **SDK**: [contextual-client](https://docs.contextual.ai/sdks/python) (Python)
- **Documents**: NIH, CDC, HHS authoritative healthcare literature
- **Build Method**: API (Python SDK) — built entirely from scratch, no templates

---

## Built For

[Elastic x Contextual AI Hack Night](https://github.com/ContextualAI/contextual-elastic-hack-night) - Challenge 2: Build Your Own Agent (Healthcare category)

---

## License

MIT
