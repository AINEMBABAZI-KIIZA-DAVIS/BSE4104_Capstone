# BSE4104 AI-Native & Agentic Engineering Capstone

## Week 7 Progress Report

**Project:** ProcurePrep UG  
**Week ending:** 16 October 2026

### 1. Work completed

We wrote 32 scenarios (the brief asked for 30). They cover normal runs, edges, bad ids, injection-style text, tool errors, and people using the wrong role. All 32 passed when we ran scripts/run_week7_evaluation.py. That runner does not call Gemini.

src/observability.py writes JSONL lines (session, tool, latency, outcome). src/guardrails.py checks item ids, quantity > 0, the four-name allow-list, roles, confirmation on route, and a few injection / “award the contract” / “approve payment” strings.

The failure catalogue has six issues we actually hit. Three are fixed in code: the Gemini function-response id (F-04), expired-quote recovery (F-05), and retrieve.py used to sys.exit on a missing key (F-06). F-01 and F-02 are prompt changes. F-03 we handled by not asking RAG for prices.

### 2. Decisions

The 32 tests are for the Python layer so we can re-run them in the lab without burning quota. Gemini is still used for weeks 2–3 reports and the optional week 4 demo.

If an injection string or unknown tool shows up, we stop. We do not ask the model to “please ignore that.”

### 3. What went wrong

We did not want to spend more Gemini calls during week 7 just to score RAG wording. F-01/F-02 were still listed as residual at the 16 Oct freeze. We later re-ran two of those cases on 18 Oct (results/live_rag_retest.md) as part of week 8 write-up, not as a ninth week. They did not come back on that one run (temperature 0.1). The model can still drift on another run.

EV-22 put DROP TABLE in the item id. The injection regex fired before the ITEM-NNN format check. We accepted INJECTION_BLOCKED as the result because that is the stricter stop.

### 4. Evidence

GitHub: https://github.com/AINEMBABAZI-KIIZA-DAVIS/BSE4104_Capstone  
ClickUp: https://app.clickup.com/1200430000003901/v/li/1200430000006616  
Diagram: submission/WEEK7/Evaluation_Guardrails.jpg

### 5. Who did what

| Member | This week | Files |
| :--- | :--- | :--- |
| Nasiwa Hafswa | Scenario list | evaluation/scenarios.py |
| Armand Shematsi | Guardrails and traces | src/guardrails.py, src/observability.py |
| Ainembabazi Kiiza Davis | Failure catalogue and prompt edits | docs/evaluation/failure-catalogue.md |
| Alvin Mayega Kenneth | The 32-run and guardrail tests | results/week7_evaluation.md, tests/test_guardrails.py |

### 6. Next week

README, the 8–12 page report, known limitations, and the demo slides.

### 7. Status

On track. Unauthorized and adversarial cases fail closed. We are not claiming the 32 tests measure how good the Gemini comparisons are.
