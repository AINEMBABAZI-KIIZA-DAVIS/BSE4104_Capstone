# BSE4104 AI-Native & Agentic Engineering Capstone

## Week 5 Progress Report

**Project:** ProcurePrep UG  
**Week ending:** 2 October 2026

### 1. Work completed

The assignment wanted one real multi-step job. Ours is: prepare a DRAFT requisition for one stock item. src/bounded_agent.py runs sense, plan, act, observe, then either stop or try again. It only uses the four tools from last week.

We capped the loop at 8 steps and 2 recoveries. It stops if stock is fine, if there are no quotes, if every quote is expired, if the item id is wrong, if the person says no to routing, or if it hits the cap. Routing still asks first.

Three traces are in results/week5_execution_traces.md. ITEM-004 goes through to a draft. ITEM-002 stops after the stock check (45 is above 20). ITEM-005 is the messy one: Q-109 is cheaper but expired, the tool returns QUOTATION_EXPIRED, then it drafts on Q-110.

### 2. Decisions

We did not pull in LangChain. The next tool is chosen in Python from the session state, which made the traces easier to explain in class.

At first we filtered expired quotes before drafting, which hid the failure. We let it try the cheapest quote first so the recovery is actually visible. That is F-05 in the catalogue.

Week 4 function calling is still there if someone has a key. The bounded loop does not need Gemini, which helped later when we wrote the 32 tests.

### 3. What went wrong

Making recovery honest took a couple of tries. If you pre-filter, the trace looks too clean and you cannot show observe/re-plan.

The other bug was almost fetching quotes when stock was already enough. ITEM-002 is the check that we do not do that.

### 4. Evidence

GitHub: https://github.com/AINEMBABAZI-KIIZA-DAVIS/BSE4104_Capstone  
ClickUp: https://app.clickup.com/1200430000003901/v/li/1200430000006616  
Diagram: submission/WEEK5/Agent_Architecture.jpg

### 5. Who did what

| Member | This week | Files |
| :--- | :--- | :--- |
| Nasiwa Hafswa | Task contract (goal, limits, stops) | docs/architecture/agent-task-contract.md |
| Armand Shematsi | The loop and the diagram | src/bounded_agent.py, docs/architecture/agent-architecture.md |
| Ainembabazi Kiiza Davis | WorkflowState | src/agent_state.py |
| Alvin Mayega Kenneth | The three traces and unit tests | results/week5_execution_traces.md, tests/test_bounded_agent.py |

### 6. Next week

State model, a bit of memory that only prefills name/quantity, and an MCP-style description of the same four tools. No network server.

### 7. Status

On track. It can recover from an expired cheapest quote and it stops when it should. Routing is still human.
