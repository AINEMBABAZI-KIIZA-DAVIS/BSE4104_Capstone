# BSE4104 AI-Native & Agentic Engineering Capstone

## Week 6 Progress Report

**Project:** ProcurePrep UG — AI-Native SME Procurement-Preparation Agent  
**Week:** Week 6  
**Week Ending:** 9 October 2026

### 1. Work Completed

During Week 6, the team made workflow state explicit in `WorkflowState` (`src/agent_state.py`) and added justified persistent memory in `src/agent_memory.py`. Memory stores a default requester and last quantity per item so a repeat preparation can prefill those fields.

A demonstration on ITEM-004 shows the second run reusing last quantity 20 and requester Jane Okello while still re-checking stock and quotations. The new draft stays `DRAFT`. Memory does not route or award.

The four tools were also published as an MCP-style capability catalogue in `src/mcp_interface.py`, with roles, confirmation flags and reject-unknown-tool behaviour. No networked MCP server was added.

### 2. Key Engineering Decisions

Memory is limited to prefill. `last_quotation_id` is recorded as a hint only. The agent must still call `get_reorder_status` and `get_supplier_quotations`.

Access is restricted to `procurement_officer` and `store_manager`. Other roles receive `MEMORY_FORBIDDEN`. Item history older than 90 days is pruned. Officers can delete one item or clear the store.

Interoperability is specified as an MCP-style interface rather than a new external API, which fits the synthetic local dataset and the assignment option.

### 3. Challenges

The main risk was memory silently becoming a purchasing decision. Tests assert that a remembered ITEM-004 run does not become `PENDING_APPROVAL` unless the officer asks to route and confirms.

A second challenge was keeping memory useful without storing commercial “preferred supplier” awards. Quantity and requester are enough to reduce re-entry error.

### 4. Repository and Task Evidence

**GitHub Repository:** https://github.com/AINEMBABAZI-KIIZA-DAVIS/BSE4104_Capstone  
**ClickUp Project:** https://app.clickup.com/1200430000003901/v/li/1200430000006616  
**Architecture Evidence:** `submission/WEEK6/State_Memory_Architecture.jpg`

### 5. Individual Contributions

| Member | Responsibility | Evidence |
| :--- | :--- | :--- |
| Nasiwa Hafswa | Memory design, retention and access rules | `docs/architecture/memory-design.md` |
| Armand Shematsi | State model and session fields | `docs/architecture/state-model.md`, `src/agent_state.py` |
| Ainembabazi Kiiza Davis | Persistent memory store and MCP adapter | `src/agent_memory.py`, `src/mcp_interface.py` |
| Alvin Mayega Kenneth | Memory demonstration and MCP/authorization tests | `results/week6_memory_demo.md`, `tests/test_bounded_agent.py` |
| All members | Documentation / GitHub / ClickUp | Week 6 submission pack |

### 6. Plan for Week 7

During Week 7, the team will build a 30-scenario evaluation set, add traces/logs, implement remaining guardrails, and produce a failure catalogue with at least five genuine failures and re-tests.

### 7. Week 6 Status

**Overall status:** On track

Workflow state is inspectable, memory is justified and bounded, and tools are described as an MCP-style interface. Critical decisions remain with the human store manager.
