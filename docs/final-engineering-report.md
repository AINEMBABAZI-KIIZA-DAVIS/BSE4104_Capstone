# ProcurePrep UG — Final Engineering Report

**Course:** BSE4104 Emerging Trends in Software Engineering  
**Project:** AI-Native SME Procurement-Preparation Agent  
**Period:** 31 August 2026 – 23 October 2026  
**Team:** Nasiwa Hafswa, Armand Shematsi, Ainembabazi Kiiza Davis, Alvin Mayega Kenneth

---

## 1. Executive Summary

ProcurePrep UG helps a Ugandan SME procurement officer prepare an internal purchase when stock falls below a reorder threshold. The system reads synthetic inventory and supplier quotations, explains tradeoffs, drafts a requisition and routes it only after a human confirms. It does not buy, pay or award a supplier.

AI is used for quotation comparison and optional function calling. Deterministic software owns reorder arithmetic, quote validation, tool permissions and stop conditions. Week 7 evaluated 32 scenarios (normal, edge, incorrect, adversarial, tool-failure, unauthorized); all 32 passed. The principal limitation is residual RAG over-flagging and a small policy corpus. Those risks are documented; they do not allow autonomous spend.

---

## 2. Problem Context and Requirements

SME storekeepers in Uganda often compare paper quotes by eye. Errors include reordering too late, missing expired quotes and locking cash in minimum-order quantities. The charter use case is:

inventory tracking → reorder evaluation → quotation tradeoff analysis → requisition drafting → human store-manager approval.

Acceptance criteria used throughout the build:

- Reorder if and only if `current_stock < reorder_threshold`.
- No LLM call when stock is sufficient or when zero quotes exist.
- Comparison reports must not name a winning supplier.
- Drafts never become purchase orders.
- Routing requires explicit confirmation.

The AI Boundary Matrix (Week 1) keeps calculations, authorization and workflow state in software. AI may interpret, compare, explain and draft.

Success measures: 10-case Week 2 prompt table; 15-question Week 3 RAG set; four-tool Week 4 contracts; three Week 5 traces; Week 6 memory demo; 32-scenario Week 7 suite.

---

## 3. System Architecture

Operational data live in `data/inventory.csv` and `data/quotations.csv`. `main.py` (Week 2) and `get_reorder_status` apply the reorder gate. When quotes exist, Gemini plus `prompts/prompt_v1.1.txt` or `prompt_rag_v1.0.txt` produces a human-readable comparison. Week 3 retrieval uses Gemini embeddings and ChromaDB collection `procureprep_corpus`.

Week 4 exposes four tools through Gemini function calling with automatic function calling disabled. Week 5 adds a direct-orchestration loop (`src/bounded_agent.py`): Sense → Plan → Act → Observe → Stop / Re-plan. Week 6 adds `WorkflowState`, justified JSON memory and an in-process MCP-style adapter. Week 7 adds guardrails and JSONL traces.

External-service boundary: Google Gemini API for generation and embeddings only. No payment, ERP or email integration.

---

## 4. Foundation Model and Prompt Engineering

**Selected model:** `gemini-3.5-flash-lite` via `google-genai`. Rationale: low cost and latency, adequate numerical comparison, acceptable negative-constraint following for a student-scale SME workload. Privacy: commercial quotes are synthetic; a production SME should use a paid/enterprise API tier.

Prompt v1.0 established the comparison table and “do not pick a winner” rule. Prompt v1.1 added mandatory risk flags after ten test cases showed expiry, missing terms, outliers and MOQ cash impact buried in prose. All ten Week 2 cases passed; v1.1 improved visibility on TC-04, TC-05, TC-08, TC-09 and TC-10.

The model is not used to decide reorder. Temperature is 0.1 on comparison calls.

---

## 5. Context Engineering and RAG

Twelve team-created documents in `knowledge/` cover reorder policy, quotation criteria, requisition templates, supplier terms and purchase-value bands. `tender_checklist.txt` was removed as charter drift and kept only under `legacy/`.

Chunking is 400 words with 50-word overlap (`src/ingest.py`). Each current file fits in one chunk. Retrieval embeds the query with `retrieval_query` and stores documents with `retrieval_document`. Scores in code are L2 distances converted to `1/(1+d)`; the architecture note originally said cosine and was later aligned to the implementation.

Grounding contract: RELEVANT KNOWLEDGE block plus a SOURCES USED section. Unanswerable policy questions must refuse. Documented retrieval failures: false missing-terms flag (F-01), all-or-nothing partial answers (F-02), noisy top-4 hits (F-03). Prompts were tightened in Week 7; operational prices are answered by CSV tools in the agent path.

---

## 6. Tools and Agentic Workflow

| Tool | Risk | Confirmation |
| :--- | :--- | :--- |
| `get_reorder_status` | Read | No |
| `get_supplier_quotations` | Read | No |
| `create_requisition_draft` | Low local write | No |
| `route_requisition_for_approval` | Workflow change | Yes |

The Week 5 goal is “prepare a DRAFT requisition for one item.” The planner chooses the next approved tool from session state. Limits: 8 iterations, 2 recoveries. ITEM-005 demonstrates observe/re-plan: expired Q-109 is rejected; Q-110 is drafted.

Human hand-off: decline leaves status `DRAFT`. The agent never issues a PO.

---

## 7. Memory, State and Interoperability

Session state (`WorkflowState`) holds item, quotes, excluded quote IDs, draft id, iteration and stop reason for one run.

Persistent memory stores default requester and last quantity per item for 90 days. Roles `procurement_officer` and `store_manager` may read or delete. Memory must not skip reorder checks or auto-route. The Week 6 demo prefills quantity 20 on a second ITEM-004 run and still ends as DRAFT.

Interoperability is an MCP-style catalogue (`src/mcp_interface.py`): list/call, role permissions, confirmation on route. It is not a networked MCP server.

---

## 8. Evaluation, Observability and Guardrails

**Week 7 suite:** 32 scenarios. Result: 32/32 pass. Categories: 8 normal, 6 edge, 5 incorrect-information, 5 adversarial, 4 tool-failure, 4 unauthorized.

Criteria: expected stop reason or tool error (task completion), allow-list (tool selection), injection block (instruction following), role/confirm rejects (safety), milliseconds per case (latency).

Traces: `results/traces/week7_eval.jsonl` records session, phase, tool, latency and outcome.

Guardrails: `ITEM-NNN` validation, quantity > 0, allow-list, roles, confirmation, injection regex (ignore-instructions, award/payment, DROP TABLE).

Failure catalogue: six genuine issues. Fixed and re-tested in code: F-04 (SDK `id`), F-05 (expired-quote recovery), F-06 (retrieve import exit). Prompt-mitigated: F-01, F-02. Architectural mitigation: F-03 (prices via tools).

---

## 9. Software Engineering Quality and Deployment

Tests: `tests/test_tools.py`, `test_bounded_agent.py`, `test_guardrails.py` (34 unit tests at Week 8 freeze) plus the 32-scenario runner. Secrets via `.env`; `.env.example` committed. `chroma_db/` and runtime JSON stores are gitignored.

The release is local and reproducible: clone, venv, `pip install -r requirements.txt`, copy `.env.example`, run commands in the README. There is no production deploy and no CI in this milestone.

Maintainability: legacy tender code is isolated; week packs live under `submission/WEEK1`–`WEEK8`.

---

## 10. Results, Limitations and Professional Reflection

**What works.** Deterministic reorder gating; versioned comparison prompts; RAG with citations; four tools with a human gate; a bounded prepare-requisition loop that recovers from an expired cheapest quote; memory that prefills without awarding; a 32/32 evaluation suite.

**What does not.** Live RAG still depends on a small corpus. Prompt edits for F-01/F-02 were not fully re-run against Gemini. Approval is CLI-only. Memory is a single JSON file.

**Human responsibility.** The store manager still selects the supplier and authorizes spend. The team owns the generated code, tests and the decision to keep purchasing outside the agent.

**Future work.** Retrieval score threshold; approval UI; encrypted multi-user memory; optional MCP server; 30-scenario live Gemini comparison set.

---

## References

Huyen, C. (2025). *AI Engineering: Building Applications with Foundation Models*. O’Reilly.  
Lanham, M. (2025). *AI Agents in Action*. Manning.  
Osmani, A. (2025). *Beyond Vibe Coding*. O’Reilly.  
Makerere University (2026). *BSE4104 8-Week AI-Native & Agentic Engineering Capstone Project Brief*.

## Appendices

A. Prompt excerpts: `prompts/prompt_v1.1.txt`, `prompts/prompt_rag_v1.0.txt`  
B. Tool schemas: `docs/tool-catalogue.md`  
C. Week 7 table: `results/week7_evaluation.md`  
D. Failure catalogue: `docs/evaluation/failure-catalogue.md`  
E. Week 5 traces: `results/week5_execution_traces.md`  
F. AI Boundary Matrix and charter: `submission/WEEK1/`
