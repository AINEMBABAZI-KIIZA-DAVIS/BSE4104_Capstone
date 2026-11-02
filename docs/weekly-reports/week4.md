# BSE4104 AI-Native & Agentic Engineering Capstone

## Week 4 Progress Report

**Project:** ProcurePrep UG  
**Week ending:** 25 September 2026

### 1. Work completed

We spent this week getting Gemini to call tools instead of only writing comparison reports. The loop lives in src/agent_orchestrator.py. Automatic function calling is switched off, which is annoying for the happy path but it means we can stop routing before it runs.

There are four tools. get_reorder_status still does the stock check in Python. get_supplier_quotations reads the CSV. create_requisition_draft writes a local DRAFT json file (not a purchase order). route_requisition_for_approval only flips the status after someone types y or n in the terminal.

We ran tests for missing arguments, unknown tool names, expired quotes, and the case where the human says no. The ITEM-004 demo is the one we will show: the model picks tools and drafts on the cheapest quote that is still valid.

### 2. Decisions

Contracts stay in Python. Gemini can decide *when* to call something, but it cannot skip expiry or quantity checks.

Only routing is gated. Drafting felt like the “low-risk side effect” the brief asked for.

The comparison prompts from weeks 2 and 3 still say not to pick a winner. If a draft is tied to a quote, a person still has to approve routing.

### 3. What went wrong

Gemini kept trying to route without asking. Staging the route tool and turning off auto function calling fixed it for the CLI. If we ever put this on a server we would need a real approval screen. We do not have that yet.

Also, Week 3 still had those false [MISSING TERMS] flags. They do not matter for drafts because expiry and “does this quote belong to this item” are checked in tools.py.

### 4. Evidence

GitHub: https://github.com/AINEMBABAZI-KIIZA-DAVIS/BSE4104_Capstone  
ClickUp: https://app.clickup.com/1200430000003901/v/li/1200430000006616  
Diagram: submission/WEEK4/Agent_Architecture.jpg

### 5. Who did what

| Member | This week | Files |
| :--- | :--- | :--- |
| Nasiwa Hafswa | Tool catalogue and schemas | docs/tool-catalogue.md |
| Armand Shematsi | Orchestrator and the y/n gate | src/agent_orchestrator.py, docs/architecture/agent-architecture.md |
| Ainembabazi Kiiza Davis | tools.py and the requisition json store | src/tools.py, src/requisition_store.py |
| Alvin Mayega Kenneth | Tests (missing params, expired quotes, no API) | tests/test_tools.py, results/week4_tool_tests.md |

### 6. Next week

Week 5 is the bounded loop: limits, stop reasons, and at least three traces, one of them a failure we recover from.

### 7. Status

On track. Tools exist and routing cannot run quietly. Next week we wrap a loop around them, not a free-roaming agent.
