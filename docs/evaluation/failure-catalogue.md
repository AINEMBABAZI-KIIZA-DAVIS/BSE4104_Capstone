# ProcurePrep Failure Catalogue (Week 7)

At least five genuine failures observed during Weeks 2–7, with remediation and re-test evidence.

---

## F-01 — False `[MISSING TERMS]` on a quote that already has delivery terms

**When:** Week 3 RAG comparison, ITEM-001 / Q-103  
**Observed:** Model flagged *Same-day courier dispatch* as `[MISSING TERMS]` because transport cost responsibility was not in the CSV.  
**Impact:** Unnecessary clarification loop for the store manager.  
**Remediation:** `prompts/prompt_rag_v1.0.txt` now flags `[MISSING TERMS]` only when Delivery Terms is blank or `[Not Specified]`. Transport-cost ambiguity is a separate note.  
**Re-test:** Prompt contract updated. Live Gemini comparison was not re-billed in this run; the deterministic Week 7 suite does not score LLM flags. Residual risk: a future model may still over-flag if the prompt is ignored.  
**Status:** Mitigated in prompt; residual model risk documented.

---

## F-02 — Partial corpus topic answered as fully unanswerable

**When:** Week 3 RQ-10, dispute-resolution mechanism  
**Observed:** Corpus names dispute resolution as a negotiation focus; model answered “Cannot determine” and cited no sources.  
**Remediation:** Policy Question Mode now requires a PARTIAL answer when a retrieved source mentions the topic but does not prescribe the mechanism.  
**Re-test:** Prompt updated. Full live RAG re-run not executed in Week 7 (API-bound). Guarded by documented residual limitation.  
**Status:** Mitigated in prompt; residual.

---

## F-03 — Noisy top-k retrieval for operational-data questions

**When:** Week 3 RQ-11 (QuickFix price for ITEM-015)  
**Observed:** Four policy chunks retrieved; generation still refused correctly.  
**Remediation:** Operational prices stay in CSV tools, not the vector store. Week 5 agent answers stock/price questions via `get_supplier_quotations`, not RAG.  
**Re-test:** EV-19 prepares ITEM-015 through the agent using CSV quotes (`GOAL_COMPLETE`). RAG noise remains if `--question` is used for prices.  
**Status:** Fixed for the agent workflow; residual for standalone RAG Q&A.

---

## F-04 — Function-response `id` rejected by the Gemini SDK

**When:** Week 4 human-decline test  
**Observed:** `Part.from_function_response() got an unexpected keyword argument 'id'` after a declined route.  
**Remediation:** `src/agent_orchestrator.py` no longer passes unsupported `id` kwargs.  
**Re-test:** `tests/test_tools.py::test_human_declines_routing` — **PASS**.  
**Status:** Fixed.

---

## F-05 — Expired cheapest quote blocked the draft with no recovery

**When:** Week 5 design review of ITEM-005  
**Observed:** Q-109 (UGX 38,000, expired 2026-08-15) is cheapest. Without observe/re-plan the workflow stopped or drafted an invalid quote.  
**Remediation:** Observer excludes `QUOTATION_EXPIRED` IDs; planner re-plans onto Q-110. Tool validation remains in Python.  
**Re-test:** `test_recovery_expired_then_valid_quote` and EV-12 — **PASS** (`selected_quotation_id=Q-110`).  
**Status:** Fixed.

---

## F-06 — `src/retrieve.py` exited on import without an API key or Chroma collection

**When:** Week 4/8 review  
**Observed:** `import src.retrieve` called `sys.exit(1)` if `GEMINI_API_KEY` was missing, taking down `rag_reorder_checker`.  
**Remediation:** Clients are created on first retrieve call and raise `RuntimeError` instead of exiting the process.  
**Re-test:** `tests/test_guardrails.py::test_retrieve_import_does_not_exit` — **PASS**.  
**Status:** Fixed.
