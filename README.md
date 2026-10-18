# ProcurePrep UG

BSE4104 AI-Native & Agentic Engineering Capstone. An SME procurement-preparation agent for Uganda:

**inventory check → reorder decision → quotation comparison → requisition draft → human approval**

AI compares and drafts. Deterministic Python decides reorder math, validates quotes and blocks unauthorized actions. The system does not purchase, pay or award a supplier.

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
copy .env.example .env         # then set GEMINI_API_KEY
```

`GEMINI_API_KEY` is required for Week 2 reports, Week 3 RAG and Week 4 live tool calling. Weeks 5–7 (bounded agent, memory, 32-scenario eval) run without it.

Build the RAG index after clone (needs the API key):

```bash
python src/embed_store.py
```

## Run

| Week | Command |
| :--- | :--- |
| 2 – reorder + comparison | `python main.py --prompt prompts/prompt_v1.1.txt --output results/reorder_reports_v1.1.md` |
| 3 – RAG comparison | `python src/rag_reorder_checker.py --items ITEM-001` |
| 3 – policy question | `python src/rag_reorder_checker.py --question "How many quotations are required between UGX 500,000 and 5,000,000?"` |
| 4 – Gemini tools | `python src/agent_orchestrator.py --demo` |
| 5 – bounded agent | `python src/bounded_agent.py --item ITEM-004` |
| 5 – traces | `python src/bounded_agent.py --traces results/week5_execution_traces.md` |
| 7 – evaluation | `python scripts/run_week7_evaluation.py` |
| Tests | `python -m unittest discover -s tests -q` |

## Safety boundary

- Reorder trigger: `current_stock < reorder_threshold` in Python only.
- Drafts are local JSON. Routing needs an explicit human yes.
- Tool allow-list: reorder status, quotations, draft, route.
- Prompt-injection and unauthorized roles fail closed (`src/guardrails.py`).

## Repository layout

```
data/            inventory and quotation CSVs
knowledge/       12-document SME corpus
prompts/         versioned system prompts
src/             tools, RAG, bounded agent, memory, guardrails
tests/           unit tests
evaluation/      32 Week 7 scenarios
docs/            architecture, weekly reports, final report
submission/      WEEK1 … WEEK8 academic packs
legacy/          archived tender-checker drift
```

## Secrets

Never commit `.env`. Use `.env.example`. `chroma_db/`, `data/requisitions.json` and `data/agent_memory.json` are gitignored runtime files.
