# BSE4104 AI-Native & Agentic Engineering Capstone

## Week 8 Progress Report

**Project:** ProcurePrep UG  
**Week ending:** 23 October 2026

### 1. Work completed

We went through the brief again: requirements, prompts, RAG, tools, limits, memory, tests, and secrets. The three code bugs from the catalogue (orchestrator id, expired quote, retrieve crash) are still fixed. Things we could not finish properly are written in known limitations instead of pretending they are done.

README has setup and the week-by-week commands. .env.example is in git; the real key is not.

The report, demo outline, evidence pack, and How to Run doc are under submission/WEEK8/.

### 2. Decisions

This is a local venv app, not something we deployed to campus servers. That matches the synthetic CSVs and the rule that we do not buy anything.

The bounded agent and the 32 tests still run without GEMINI_API_KEY so a marker can clone and try ITEM-004 / ITEM-005.

### 3. What went wrong

F-01 and F-02: we tightened the RAG prompt and re-ran two cases on 18 October (results/live_rag_retest.md). They did not show up on that single run. We are not treating that as “never again.”

The corpus is still twelve short files, and approval is still a terminal prompt. Both are honest limits for eight weeks.

### 4. Evidence

GitHub: https://github.com/AINEMBABAZI-KIIZA-DAVIS/BSE4104_Capstone  
ClickUp: https://app.clickup.com/1200430000003901/v/li/1200430000006616  
Diagram: submission/WEEK8/Final_Architecture.jpg

### 5. Who did what

| Member | This week | Files |
| :--- | :--- | :--- |
| Nasiwa Hafswa | Report opening sections and limitations | docs/final-engineering-report.md, docs/known-limitations.md |
| Armand Shematsi | README and .env.example | README.md |
| Ainembabazi Kiiza Davis | Demo outline and evidence pack | docs/presentation.md |
| Alvin Mayega Kenneth | Last test run | tests/, results/week7_evaluation.md |

### 6. After this week

Viva: ITEM-004 draft, one trace or eval table on screen, ITEM-005 recovery. Be ready to explain why the 32 tests do not score Gemini, and that nobody spent money through this program.

### 7. Status

Ready to demonstrate. Purchasing stays with the human.
