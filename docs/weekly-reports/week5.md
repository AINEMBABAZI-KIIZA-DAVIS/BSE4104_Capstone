# BSE4104 AI-Native & Agentic Engineering Capstone

## Week 5 Progress Report

**Project:** ProcurePrep UG — AI-Native SME Procurement-Preparation Agent  
**Week:** Week 5  
**Week Ending:** 2 October 2026

### 1. Work Completed

During Week 5, the team implemented one goal-directed workflow: prepare a DRAFT purchase requisition for a named inventory item. The loop in `src/bounded_agent.py` follows Sense → Plan → Act → Observe → Stop / Re-plan. The planner chooses only among the four approved Week 4 tools.

Limits are maximum 8 iterations and 2 recoveries. Stop reasons include sufficient stock, missing quotes, expired-only quotes, unknown item, human decline and the iteration cap. Routing still requires explicit confirmation.

Three execution traces were captured: a successful ITEM-004 draft, a safe stop on ITEM-002 (stock sufficient), and a recovery on ITEM-005 where expired Q-109 is rejected and the planner re-plans onto Q-110.

### 2. Key Engineering Decisions

The team used direct orchestration rather than an extra framework. Next-action choice is deterministic Python so traces and tests can show why a tool was selected.

The first price-ranked draft attempt may hit an expired quote. Validation stays in the tool; the observer excludes that quotation and the planner re-plans. That is the required failure/recovery case.

Gemini function calling from Week 4 remains available. It is not required for the bounded loop, so the workflow can be evaluated without a live model.

### 3. Challenges

The main challenge was making recovery real. Filtering expired quotes before the first draft hid the failure. The planner now allows a cheapest-price first attempt so `QUOTATION_EXPIRED` is observed and repaired.

A second challenge was stopping safely when stock is sufficient. The agent must not fetch quotes or draft in that case. The ITEM-002 trace confirms that early stop.

### 4. Repository and Task Evidence

**GitHub Repository:** https://github.com/AINEMBABAZI-KIIZA-DAVIS/BSE4104_Capstone  
**ClickUp Project:** https://app.clickup.com/1200430000003901/v/li/1200430000006616  
**Architecture Evidence:** `submission/WEEK5/Agent_Architecture.jpg`

### 5. Individual Contributions

| Member | Responsibility | Evidence |
| :--- | :--- | :--- |
| Nasiwa Hafswa | Agent task contract: goal, tools, limits, stop conditions | `docs/architecture/agent-task-contract.md` |
| Armand Shematsi | Bounded loop and architecture diagram | `src/bounded_agent.py`, `docs/architecture/agent-architecture.md` |
| Ainembabazi Kiiza Davis | Session state object used by the planner | `src/agent_state.py` |
| Alvin Mayega Kenneth | Three execution traces and agent tests | `results/week5_execution_traces.md`, `tests/test_bounded_agent.py` |
| All members | Documentation / GitHub / ClickUp | Week 5 submission pack |

### 6. Plan for Week 6

During Week 6, the team will document the workflow state model, add justified persistent memory that prefills quantity and requester without auto-routing, demonstrate that memory helps a repeat preparation, and publish an MCP-style interface specification for the approved tools.

### 7. Week 5 Status

**Overall status:** On track

The agent can decide among approved actions, observe tool results, recover from an expired quote, and stop safely. Human control is retained on routing.
