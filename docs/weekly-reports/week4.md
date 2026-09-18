# ProcurePrep – Week 4 Progress Report

**Milestone:** Tools and Function Calling
**Author:** AI Agentic Development Team
**Date:** September 17, 2026
**Course / Project:** BSE4104 AI Agentic Capstone

---

## 1. Executive Summary

Week 4 adds a **tool-calling layer** on top of the corrected SME workflow from Weeks 2–3. Four callable tools are implemented in `src/tools.py` and exposed to **`gemini-3.5-flash-lite`** through Gemini’s native function-calling API (manual dispatch loop in `src/agent_orchestrator.py` with automatic function calling disabled).

The model decides **when** to invoke each tool based on the user task—not a hardcoded Python pipeline. Low-risk tools (`get_reorder_status`, `get_supplier_quotations`, `create_requisition_draft`) run immediately; **`route_requisition_for_approval`** is staged behind an explicit CLI **y/n human confirmation** gate before any state change.

---

## 2. What Was Built

### Tools (see `docs/tool-catalogue.md`)

| Tool                               | Purpose                                    |
| :--------------------------------- | :----------------------------------------- |
| `get_supplier_quotations`        | Read quotes from`data/quotations.csv`    |
| `get_reorder_status`             | Expose deterministic reorder decision      |
| `create_requisition_draft`       | Persist DRAFT to`data/requisitions.json` |
| `route_requisition_for_approval` | DRAFT → PENDING_APPROVAL (gated)          |

### Orchestration

- **`src/agent_orchestrator.py`:** Multi-turn tool loop, transcript logging, `--demo` mode.
- **`src/requisition_store.py`:** JSON persistence with thread-safe updates.
- **`src/procure_data.py`:** Shared CSV loaders aligned with `main.py`.

### Architecture

- **`docs/architecture/agent-architecture.md`:** Full Week 2 → 3 → 4 flow diagram.
- **`docs/tool-catalogue.md`:** Input/output schemas, authorization, failure behavior.

---

## 3. Demonstration

A live demo run (`results/week4_tool_demo.md`) shows the model autonomously calling:

1. **`get_reorder_status`** for ITEM-004 (confirms reorder need, deficit 20 cartons).
2. **`get_supplier_quotations`** for ITEM-004 (returns Q-107 and Q-108).
3. **`create_requisition_draft`** for 20 cartons on Q-107 (cheapest valid quote on 2026-09-16), requested by Jane Okello.

The transcript includes raw `[TOOL CALL]` and `[TOOL RESULT]` JSON from the orchestrator, not paraphrased summaries.

---

## 4. Test Findings

Evidence in `results/week4_tool_tests.md` and `tests/test_tools.py`:

| Category                      | Finding                                                                                                                  |
| :---------------------------- | :----------------------------------------------------------------------------------------------------------------------- |
| **Missing parameters**  | All tools return`MISSING_PARAMETER` with field name; no crashes.                                                       |
| **Invalid requests**    | Expired quote (Q-109), wrong-item quotation, re-route of PENDING requisition—all rejected deterministically.            |
| **Unavailable API**     | Mocked`TimeoutError` on `generate_content`; orchestrator raises `AgentOrchestratorError` with transcript, no hang. |
| **Malformed quotation** | Incomplete CSV row rejected as`MALFORMED_QUOTATION_RECORD` before draft creation.                                      |

### Reliability / safety gaps revealed

1. **False `[MISSING TERMS]` carry-over from Week 3** does not affect tools, but reminds us that LLM flags and tool validation must stay separate—which Week 4 enforces for drafts.
2. **Human gate dependency:** Routing safety relies on CLI confirmation; a headless deployment would need an equivalent approval UI or OAuth-scoped role check.
3. **Single JSON store:** Adequate for capstone simulation; production would need transactional DB and audit logs.

---

## 5. Outlook: Week 5

Week 5 will add a **bounded multi-turn agent loop** with session state/memory:

- Carry conversation context across reorder → compare → draft → route steps.
- Persist agent session state (selected item, draft ID, pending confirmations).
- Retain Week 4 human gate on `route_requisition_for_approval`.
- Optional integration with Week 3 RAG for grounded comparison inside the agent loop.

Week 4 intentionally stops short of full autonomous looping—tools and the approval gate are the scope boundary.
