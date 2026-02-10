# MedAssist - Healthcare Research Agent

**Elastic x Contextual AI Hack Night | Challenge 2: Build Your Own Agent**

MedAssist is an AI-powered healthcare research assistant that helps clinicians, researchers, and patients navigate medical literature, clinical guidelines, and health information. It provides evidence-based answers grounded in real healthcare documents, with source citations for every response.

---

## How It Works

MedAssist is a **RAG (Retrieval-Augmented Generation) agent** built on the [Contextual AI](https://contextual.ai) platform. Here's the pipeline:

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

- **Reranker**: After initial retrieval returns 30 candidate passages, a reranker model (`ctxl-rerank-v2`) scores them for relevance and keeps the top 10. This dramatically improves answer quality.

- **Multi-turn Conversations**: The agent tracks `conversation_id` so follow-up questions retain context from previous exchanges.

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

## Healthcare Documents

The agent's knowledge base includes authoritative medical literature from:

| Document | Source | Topic |
|----------|--------|-------|
| JNC7 Hypertension Guidelines | NIH/NHLBI | Blood pressure classification, treatment algorithms |
| NHLBI Lifestyle & Cardiovascular Risk | NIH/NHLBI | Diet, sodium, exercise effects on heart health |
| HHS Physical Activity Guidelines | US HHS | Federal exercise recommendations for all ages |
| CDC Chronic Disease Surveillance | CDC | Public health monitoring via electronic health records |

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

Type questions like:
- "What are the recommended blood pressure targets for adults?"
- "Summarize the evidence on physical activity and cardiovascular risk"
- "What lifestyle interventions help prevent chronic disease?"

Type `new` to start a fresh conversation, `quit` to exit.

**Demo mode** (for recording your submission):
```bash
python query_agent.py <AGENT_ID> --demo
```

### 4. Agent Composer (Optional - GUI)

For the advanced multi-step workflow:
1. Go to [app.contextual.ai](https://app.contextual.ai)
2. Open your agent and click **Customize**
3. Paste the contents of `agent_composer.yaml`

---

## How the Prompts Work

The agent uses a carefully designed system prompt with three layers:

### Identity
Defines who MedAssist is - a healthcare research assistant that is evidence-based, careful, accessible, and responsible. This shapes every response.

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

## Example Queries

| Category | Query |
|----------|-------|
| Clinical Guidelines | "What are the current recommended screening guidelines for common chronic diseases?" |
| Treatment Options | "What are the evidence-based treatment approaches for managing Type 2 diabetes?" |
| Drug Information | "What are the most important drug interactions that clinicians should be aware of?" |
| Research Synthesis | "Summarize the latest research findings on preventive care and lifestyle interventions." |
| Differential Diagnosis | "A patient presents with fatigue, weight gain, and cold intolerance. What conditions should be considered?" |

---

## Tech Stack

- **Platform**: [Contextual AI](https://contextual.ai) - Enterprise RAG agent platform
- **LLM**: Claude Sonnet 4.5 (via Vertex AI)
- **Reranker**: ctxl-rerank-v2-instruct-multilingual
- **SDK**: [contextual-client](https://docs.contextual.ai/sdks/python) (Python)
- **Documents**: WHO, NIH, CDC authoritative healthcare literature

---

## Built For

[Elastic x Contextual AI Hack Night](https://github.com/ContextualAI/contextual-elastic-hack-night) - Challenge 2: Build Your Own Agent (Healthcare category)

---

## License

MIT
