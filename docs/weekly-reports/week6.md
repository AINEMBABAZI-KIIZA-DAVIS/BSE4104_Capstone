# BSE4104 AI-Native & Agentic Engineering Capstone

## Week 6 Progress Report

**Project:** ProcurePrep UG  
**Week ending:** 9 October 2026

### 1. Work completed

This week was mostly making the session obvious and adding a small memory file. WorkflowState in src/agent_state.py holds the current item, quotes, draft id, and why we stopped. src/agent_memory.py stores the usual requester name and the last quantity for an item so we do not retype them every time.

On a second run of ITEM-004 it prefills 20 cartons and Jane Okello, but it still checks stock and quotes. The new record stays DRAFT. Memory does not send anything for approval on its own.

We also wrapped the four tools in src/mcp_interface.py (list/call, roles, confirm on route). It is in-process only. We did not stand up a real MCP server.

### 2. Decisions

Memory is hints, not authority. last_quotation_id is stored but the draft tool still validates the live CSV.

Only procurement_officer and store_manager can read it. Anyone else gets MEMORY_FORBIDDEN. Rows older than 90 days get dropped.

The brief allowed either an external integration or an MCP-style catalogue. Given our data is local CSVs, the catalogue was the honest option.

### 3. What went wrong

We were worried memory would quietly turn into “just buy what we bought last time.” There is a test that a remembered ITEM-004 run does not become PENDING_APPROVAL unless someone asks to route and confirms.

We also refused to store a “winning supplier”. Quantity and name are enough to save typing.

### 4. Evidence

GitHub: https://github.com/AINEMBABAZI-KIIZA-DAVIS/BSE4104_Capstone  
ClickUp: https://app.clickup.com/1200430000003901/v/li/1200430000006616  
Diagram: submission/WEEK6/State_Memory_Architecture.jpg

### 5. Who did what

| Member | This week | Files |
| :--- | :--- | :--- |
| Nasiwa Hafswa | What we store, who can see it, how long we keep it | docs/architecture/memory-design.md |
| Armand Shematsi | State model write-up | docs/architecture/state-model.md, src/agent_state.py |
| Ainembabazi Kiiza Davis | JSON memory file and the MCP wrapper | src/agent_memory.py, src/mcp_interface.py |
| Alvin Mayega Kenneth | Second-run demo and the memory tests | results/week6_memory_demo.md, tests/test_bounded_agent.py |

### 6. Next week

At least 30 scenarios, traces, guardrails, and a failure catalogue with five real issues (not invented ones).

### 7. Status

On track. State is visible, memory is small on purpose, tools are listed as capabilities. Spend still sits with the store manager.
