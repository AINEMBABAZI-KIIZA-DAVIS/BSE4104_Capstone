# BSE4104 AI-Native & Agentic Engineering Capstone

## Week 7 Progress Report

**Project:** ProcurePrep UG — AI-Native SME Procurement-Preparation Agent  
**Week:** Week 7  
**Week Ending:** 16 October 2026

### 1. Work Completed

During Week 7, the team produced a 32-scenario evaluation set covering normal, edge, incorrect-information, adversarial, tool-failure and unauthorized-action cases. All 32 scenarios passed. Criteria were task completion, tool selection, instruction following, safety violations and latency.

Structured traces are written by `src/observability.py`. Guardrails in `src/guardrails.py` validate item IDs and quantities, enforce the tool allow-list, check roles, require confirmation for routing, and block prompt-injection / award-payment overrides.

A failure catalogue records six genuine failures from earlier weeks. Three are fixed and re-tested in code (function-response `id`, expired-quote recovery, retrieve import crash). Two RAG prompt issues are mitigated in `prompt_rag_v1.0.txt`. Retrieval noise is avoided on the agent path by using CSV tools for prices.

### 2. Key Engineering Decisions

The evaluation runner executes the bounded agent and MCP adapter without a live Gemini call so the 32-case suite is reproducible and free. Gemini remains in Week 2/3 comparison and optional Week 4 function calling.

Guardrails fail closed. An injection string or unknown tool stops the session rather than asking the model to ignore it.

### 3. Challenges

The main challenge was scoring LLM grounding (F-01, F-02) without re-spending API quota. The team updated the prompt contract and recorded residual model risk instead of claiming a live re-test.

EV-22 (`ITEM-004; DROP TABLE`) matched the injection detector before the format check. The expected result was corrected to `INJECTION_BLOCKED`, which is the stricter and correct control.

### 4. Repository and Task Evidence

**GitHub Repository:** https://github.com/AINEMBABAZI-KIIZA-DAVIS/BSE4104_Capstone  
**ClickUp Project:** https://app.clickup.com/1200430000003901/v/li/1200430000006616  
**Architecture Evidence:** `submission/WEEK7/Evaluation_Guardrails.jpg`

### 5. Individual Contributions

| Member | Responsibility | Evidence |
| :--- | :--- | :--- |
| Nasiwa Hafswa | Evaluation criteria and 32-scenario set | `evaluation/scenarios.py` |
| Armand Shematsi | Guardrails and observability | `src/guardrails.py`, `src/observability.py` |
| Ainembabazi Kiiza Davis | Failure catalogue and prompt remediations | `docs/evaluation/failure-catalogue.md` |
| Alvin Mayega Kenneth | Evaluation run and re-tests | `results/week7_evaluation.md`, `tests/test_guardrails.py` |
| All members | Documentation / GitHub / ClickUp | Week 7 submission pack |

### 6. Plan for Week 8

During Week 8, the team will harden the README and run instructions, write the 8–12 page final engineering report, document remaining limitations, and prepare the demonstration deck.

### 7. Week 7 Status

**Overall status:** On track

The bounded workflow is evaluated, inspectable and fail-closed on unauthorized or adversarial input. Residual RAG flagging risk is documented rather than hidden.
