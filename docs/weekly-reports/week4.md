# BSE4104 AI-Native & Agentic Engineering Capstone

## Week 4 Progress Report

**Project:** ProcurePrep UG — AI-Native SME Procurement-Preparation Agent  
**Week:** Week 4  
**Week Ending:** 25 September 2026

### 1. Work Completed

During Week 4, the team moved beyond answer generation by exposing four explicit tools to Gemini through a manual function-calling loop in `src/agent_orchestrator.py`. Automatic function calling is disabled so the application can intercept high-impact actions.

`get_supplier_quotations` reads current rows from `data/quotations.csv`. `get_reorder_status` returns the deterministic reorder decision. `create_requisition_draft` writes a DRAFT record to `data/requisitions.json` without approving spend. `route_requisition_for_approval` changes status to PENDING_APPROVAL only after an explicit CLI yes/no confirmation.

The team tested missing parameters, unauthorized or unknown tools, expired and malformed quotations, unavailable Gemini responses and human decline of routing. A live demonstration on ITEM-004 shows the model selecting tools and drafting a requisition on the cheapest valid quote.

### 2. Key Engineering Decisions

Tool contracts are enforced in Python. The model may choose when to call a tool, but it cannot bypass quantity, quotation-ownership, expiry or status checks.

Only routing is gated. Draft creation is treated as a low-risk simulated side effect, matching the assignment requirement.

The Week 2/3 comparison prompts still forbid picking a winner. The agent may draft against a quote the user asked for; a human must still approve routing.

### 3. Challenges

The main challenge was keeping Gemini from executing routing without a human. Disabling automatic function calling and staging `route_requisition_for_approval` solves this in the CLI. A headless deployment would need an equivalent approval UI.

A second challenge was distinguishing LLM risk flags from tool validation. Week 3 false `[MISSING TERMS]` alerts do not affect drafts because expiry and quotation membership are checked in code.

### 4. Repository and Task Evidence

**GitHub Repository:** https://github.com/AINEMBABAZI-KIIZA-DAVIS/BSE4104_Capstone  
**ClickUp Project:** https://app.clickup.com/1200430000003901/v/li/1200430000006616  
**Architecture Evidence:** `submission/WEEK4/Agent_Architecture.jpg`

### 5. Individual Contributions

| Member | Responsibility | Evidence |
| :--- | :--- | :--- |
| Nasiwa Hafswa | Tool catalogue, schemas, authorization notes | `docs/tool-catalogue.md` |
| Armand Shematsi | Orchestrator, human approval gate, architecture | `src/agent_orchestrator.py`, `docs/architecture/agent-architecture.md` |
| Ainembabazi Kiiza Davis | Tool implementations and requisition store | `src/tools.py`, `src/requisition_store.py` |
| Alvin Mayega Kenneth | Failure, authorization and API-unavailable tests | `tests/test_tools.py`, `results/week4_tool_tests.md` |
| All members | Documentation / GitHub / ClickUp | Week 4 submission pack |

### 6. Plan for Week 5

During Week 5, the team will implement one bounded multi-step agent workflow with approved tools, iteration limits, stop conditions and human hand-off, and capture at least three execution traces including one failure or recovery case.

### 7. Week 4 Status

**Overall status:** On track

The system now uses explicit tools with contracts, permissions and a human gate on higher-impact routing. Week 5 will add bounded autonomy around these tools, not open-ended execution.
