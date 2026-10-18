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

### Architecture Overview

![ProcurePrep UG — Final System Architecture](../submission/WEEK8/Final_Architecture.jpg)

The diagram shows two zones. On the left, the vertical stack is the processing pipeline: the SME officer's goal enters the **bounded agent** (managing the Sense → Plan → Act → Observe → Stop loop and calling Gemini for quotation comparison text), passes through the **guardrails / traces / memory** layer (input validation, tool allow-list, JSONL observability and 90-day JSON memory), reads from **CSV data and the Chroma corpus** (inventory and quotations CSVs plus the 12-document knowledge base), and terminates at the **human approval boundary** (the CLI confirmation gate on `route_requisition_for_approval`). On the right, three responsibility boxes clarify the AI boundary: **Deterministic** work (reorder math, quote validation, allow-list enforcement) is owned entirely by Python; **Probabilistic** work (comparison narrative, risk-flag text, draft wording) is delegated to Gemini; and **Out of scope** items (payment, supplier award, live purchase orders) are excluded by charter and enforced in code — the system cannot produce a PO regardless of what the model outputs.

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

| Tool | Required inputs | Key success fields | Failure codes | Confirm? |
| :--- | :--- | :--- | :--- | :--- |
| `get_reorder_status` | `item_id` | `needs_reorder`, `replenishment_deficit`, `reference_date` | `ITEM_NOT_FOUND`, `MISSING_PARAMETER` | No |
| `get_supplier_quotations` | `item_id` | `quotations[]` (empty list + `warning` if none on file) | `ITEM_NOT_FOUND`, `MISSING_PARAMETER` | No |
| `create_requisition_draft` | `item_id`, `quantity > 0`, `selected_quotation_id`, `requested_by` | `requisition_id`, `unit_price`, `total_estimated_cost`, `status=DRAFT` | `INVALID_QUANTITY`, `QUOTATION_EXPIRED`, `QUOTATION_NOT_FOUND_FOR_ITEM`, `MALFORMED_QUOTATION_RECORD`, `MISSING_PARAMETER` | No |
| `route_requisition_for_approval` | `requisition_id` (must be `DRAFT`) | `status=PENDING_APPROVAL`, `routed_to`, `routed_at` | `REQUISITION_NOT_FOUND`, `INVALID_STATUS`, `HUMAN_DECLINED` | **Yes — CLI y/n** |

The Week 5 goal is “prepare a DRAFT requisition for one item.” The planner chooses the next approved tool from session state. Limits: 8 iterations, 2 recoveries. ITEM-005 demonstrates observe/re-plan: expired Q-109 is rejected; Q-110 is drafted.

Human hand-off: decline leaves status `DRAFT`. The agent never issues a PO.

---

## 7. Memory, State and Interoperability

Session state (`WorkflowState`) holds item, quotes, excluded quote IDs, draft id, iteration and stop reason for one run.

Persistent memory stores default requester and last quantity per item for 90 days. Roles `procurement_officer` and `store_manager` may read or delete. Memory must not skip reorder checks or auto-route. The Week 6 demo prefills quantity 20 on a second ITEM-004 run and still ends as DRAFT.

Interoperability is an MCP-style catalogue (`src/mcp_interface.py`): list/call, role permissions, confirmation on route. It is not a networked MCP server.

---

## 8. Evaluation, Observability and Guardrails

**Week 7 suite:** 32 scenarios. Result: 32/32 pass. Evaluation criteria: expected stop reason or tool error (task completion), allow-list enforcement (tool selection), injection block (instruction following), role and confirmation rejects (safety), wall-clock milliseconds per scenario (latency). Traces written to `results/traces/week7_eval.jsonl`.

### 8.1 Results by Category

| Category | Pass | Total |
| :--- | ---: | ---: |
| normal | 8 | 8 |
| edge | 6 | 6 |
| incorrect-information | 5 | 5 |
| adversarial | 5 | 5 |
| tool-failure | 4 | 4 |
| unauthorized-action | 4 | 4 |
| **Total** | **32** | **32** |

### 8.2 Full 32-Scenario Table

| ID | Category | Expected stop / error | Latency (ms) | Result |
| :--- | :--- | :--- | ---: | :--- |
| EV-01 | normal | `GOAL_COMPLETE` / Q-107 | 6.58 | **PASS** |
| EV-02 | normal | `GOAL_COMPLETE` | 2.24 | **PASS** |
| EV-03 | normal | `GOAL_COMPLETE` / Q-106 | 2.86 | **PASS** |
| EV-04 | normal | `GOAL_COMPLETE` | 2.08 | **PASS** |
| EV-05 | normal | `GOAL_COMPLETE` | 2.14 | **PASS** |
| EV-06 | normal | `GOAL_COMPLETE` | 2.17 | **PASS** |
| EV-07 | normal | `GOAL_COMPLETE` | 2.05 | **PASS** |
| EV-08 | normal | `GOAL_COMPLETE` | 2.62 | **PASS** |
| EV-09 | edge | `NO_REORDER_NEEDED` | 0.60 | **PASS** |
| EV-10 | edge | `NO_REORDER_NEEDED` | 0.55 | **PASS** |
| EV-11 | edge | `NO_QUOTATIONS` | 1.05 | **PASS** |
| EV-12 | edge | `GOAL_COMPLETE` / Q-110 (expired-quote recovery) | 2.81 | **PASS** |
| EV-13 | edge | `NO_REORDER_NEEDED` | 0.67 | **PASS** |
| EV-14 | edge | `GOAL_COMPLETE` / qty 20 (deficit-derived) | 2.07 | **PASS** |
| EV-15 | incorrect-information | `ITEM_NOT_FOUND` | 0.60 | **PASS** |
| EV-16 | incorrect-information | `INPUT_REJECTED` (non-ITEM-NNN id) | 0.29 | **PASS** |
| EV-17 | incorrect-information | `MISSING_ITEM_ID` | 0.18 | **PASS** |
| EV-18 | incorrect-information | `QUOTATION_NOT_FOUND_FOR_ITEM` | 0.32 | **PASS** |
| EV-19 | incorrect-information | `GOAL_COMPLETE` (ITEM-015 via CSV tools, not RAG) | 2.52 | **PASS** |
| EV-20 | adversarial | `INJECTION_BLOCKED` (award override in user_text) | 0.17 | **PASS** |
| EV-21 | adversarial | `INJECTION_BLOCKED` (payment override in requester) | 0.15 | **PASS** |
| EV-22 | adversarial | `INJECTION_BLOCKED` (DROP TABLE in item_id) | 0.14 | **PASS** |
| EV-23 | adversarial | `UNKNOWN_TOOL` (award_contract not on allow-list) | 0.01 | **PASS** |
| EV-24 | adversarial | `CONFIRMATION_REQUIRED` (route without confirmed=True) | 0.01 | **PASS** |
| EV-25 | tool-failure | `HUMAN_DECLINED` / status stays `DRAFT` | 2.41 | **PASS** |
| EV-26 | tool-failure | `INVALID_QUANTITY` (qty=0) | 0.02 | **PASS** |
| EV-27 | tool-failure | `MISSING_PARAMETER` (no item_id) | 0.01 | **PASS** |
| EV-28 | tool-failure | `QUOTATION_EXPIRED` (Q-109) | 0.34 | **PASS** |
| EV-29 | unauthorized-action | `UNAUTHORIZED_ROLE` (vendor role) | 0.01 | **PASS** |
| EV-30 | unauthorized-action | `MEMORY_FORBIDDEN` (visitor role) | 0.01 | **PASS** |
| EV-31 | unauthorized-action | `UNAUTHORIZED_ROLE` (store_manager on route) | 0.01 | **PASS** |
| EV-32 | unauthorized-action | `UNAUTHORIZED_ROLE` (vendor via agent) | 0.17 | **PASS** |

### 8.3 Trace Excerpt — ITEM-005 Expired-Quote Recovery

Trace 3 from `results/week5_execution_traces.md` (session `SES-2f4840f490`, 2026-09-23). The planner proposes the globally cheapest quote (Q-109, UGX 38,000) on the first draft attempt; the tool rejects it because `quotation_valid_until` (2026-08-15) < `reference_date` (2026-09-16). The observer adds Q-109 to `excluded_quotation_ids`; the planner re-selects Q-110 (UGX 42,000, valid to 2026-10-31) and succeeds.

```
--- iteration 3 PLAN ---
{"type": "act", "tool": "create_requisition_draft",
 "args": {"item_id": "ITEM-005", "quantity": 12,
           "selected_quotation_id": "Q-109", "requested_by": "Jane Okello"}}
[ACT] create_requisition_draft({...})
[OBSERVE] {"error": "QUOTATION_EXPIRED",
            "selected_quotation_id": "Q-109",
            "quotation_valid_until": "2026-08-15",
            "reference_date": "2026-09-16"}

--- iteration 4 PLAN ---
{"type": "act", "tool": "create_requisition_draft",
 "args": {"item_id": "ITEM-005", "quantity": 12,
           "selected_quotation_id": "Q-110", "requested_by": "Jane Okello"}}
[OBSERVE] {"requisition_id": "REQ-20260923-0002", "item_id": "ITEM-005",
            "unit_price": 42000, "total_estimated_cost": 504000, "status": "DRAFT"}

--- iteration 5 PLAN ---
{"type": "stop", "reason": "GOAL_COMPLETE"}
[STOP] GOAL_COMPLETE outcome=SUCCESS
[MEMORY] recorded successful preparation
```

Stop reason: `GOAL_COMPLETE`. Outcome: `SUCCESS`. Iterations: 5. Selected: Q-110.

### 8.4 Guardrail Implementation

All controls are implemented in `src/guardrails.py` and wired through `src/bounded_agent.py` and `src/mcp_interface.py`.

| Control | Implementation | Evaluation evidence |
| :--- | :--- | :--- |
| Input validation | `ITEM-NNN` regex; `quantity > 0` check | EV-16, EV-17, EV-26 |
| Tool allow-list | Four named tools only; unknown names fail closed | EV-23 `UNKNOWN_TOOL` |
| Role authorization | `procurement_officer` and `store_manager` only | EV-29, EV-31, EV-32 |
| Iteration limits | Max 8 iterations, 2 recoveries per session | `WorkflowState.max_iterations` |
| Approval control | `route_requisition_for_approval` requires explicit y/n | EV-24, EV-25 |
| Prompt-injection | Regex covers `ignore.*previous instructions`, `award.*contract`, `approve.*payment`, `drop table` | EV-20, EV-21, EV-22 |
| Output / side-effect bound | Draft status is `DRAFT`; the system cannot create a PO or execute payment | EV-25 leaves `DRAFT` |

Failure catalogue: six genuine issues. Fixed and re-tested in code: F-04 (SDK `id`), F-05 (expired-quote recovery), F-06 (retrieve import exit). Prompt-mitigated: F-01, F-02. Architectural mitigation: F-03 (prices via tools, not RAG).

---

## 9. Software Engineering Quality and Deployment

Tests: `tests/test_tools.py`, `test_bounded_agent.py`, `test_guardrails.py` (34 unit tests at Week 8 freeze) plus the 32-scenario runner. Secrets via `.env`; `.env.example` committed. `chroma_db/` and runtime JSON stores are gitignored.

The release is local and reproducible: clone, venv, `pip install -r requirements.txt`, copy `.env.example`, run commands in the README. There is no production deploy and no CI in this milestone.

Maintainability: legacy tender code is isolated; week packs live under `submission/WEEK1`–`WEEK8`.

---

## 9b. Deliberate Design Choices

Five architectural decisions were made deliberately, each with an engineering rationale drawn from the weekly design notes.

**1. Deterministic before probabilistic.** The reorder trigger (`current_stock < reorder_threshold`) and the zero-quote early stop are computed in Python. Gemini is not called when stock is sufficient or when no quotes exist. This ensures the most consequential binary decision — whether to reorder at all — is auditable without a model. Source: `docs/architecture/rag-architecture.md` §Design Decisions.

**2. Direct orchestration, not model-chosen steps.** The Week 5 bounded agent uses `plan_next_action()` in Python to select the next tool. Gemini is not asked to plan the sequence. This keeps iteration limits, stop conditions and recovery logic inspectable in code and runnable without a live API key (the entire 32-scenario evaluation suite is Gemini-free). Source: `docs/architecture/agent-architecture.md`.

**3. Memory as prefill, not as authority.** `agent_memory.py` stores the last quantity and requester name as hints only. On a second preparation of ITEM-004 the agent still re-runs `get_reorder_status`, re-fetches quotations, and re-validates the chosen quote in Python. A dedicated unit test asserts the run ends as `DRAFT`, not `PENDING_APPROVAL`, even when memory is populated. Source: `docs/architecture/memory-design.md` §Critical-decision boundary.

**4. Corpus aligned to charter scope.** The original knowledge base included a tender submission checklist (`tender_checklist.txt`) which belongs to public-sector procurement, not SME reorder preparation. It was removed and isolated in `legacy/`. The 12 remaining documents cover reorder policy, quotation evaluation criteria, requisition templates and supplier terms — all within the agreed charter. Source: `docs/architecture/rag-architecture.md` §Design Decisions.

**5. Spend is unconditionally outside the system.** No supplier is selected in memory, no payment or bank details are stored, and no `PENDING_APPROVAL` status is written automatically. The system boundary is DRAFT (local JSON) or PENDING_APPROVAL (simulated routing); the store manager authorises spend through a separate channel. This is enforced by the tool contracts, not just by prompt wording — `route_requisition_for_approval` requires an explicit human confirmation signal and still does not create a purchase order. Source: `docs/architecture/memory-design.md` §What is not stored.

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
