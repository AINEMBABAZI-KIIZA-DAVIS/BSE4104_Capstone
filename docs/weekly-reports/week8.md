# BSE4104 AI-Native & Agentic Engineering Capstone

## Week 8 Progress Report

**Project:** ProcurePrep UG — AI-Native SME Procurement-Preparation Agent  
**Week:** Week 8  
**Week Ending:** 23 October 2026

### 1. Work Completed

During Week 8, the team reviewed requirements, architecture, prompts, RAG, tools, agent limits, memory, tests and secrets handling. Critical defects already catalogued were confirmed fixed (orchestrator `id` error, expired-quote recovery, retrieve import crash). Remaining limitations were written down instead of overstated as complete.

The repository README now describes setup, Week 2–7 run commands, environment variables and safety boundaries. `.env.example` is provided; real keys stay out of git.

The final engineering report (8–12 pages plus appendices), demonstration outline and evaluation evidence pack were assembled in `submission/WEEK8/`.

### 2. Key Engineering Decisions

The release is a reproducibly runnable local application, not a cloud deployment. That matches the synthetic CSV data and the charter’s no-live-purchasing rule.

The team kept Gemini optional for the bounded agent so examiners can run the 32-scenario suite and Week 5 traces without an API key.

### 3. Challenges

The main remaining limitation is live RAG re-evaluation of F-01 and F-02 after the prompt edit. The report states this honestly.

A second limitation is the small 12-chunk corpus and the CLI-only human gate. Both are in-scope for an eight-week capstone and are listed as future work.

### 4. Repository and Task Evidence

**GitHub Repository:** https://github.com/AINEMBABAZI-KIIZA-DAVIS/BSE4104_Capstone  
**ClickUp Project:** https://app.clickup.com/1200430000003901/v/li/1200430000006616  
**Architecture Evidence:** `submission/WEEK8/Final_Architecture.jpg`

### 5. Individual Contributions

| Member | Responsibility | Evidence |
| :--- | :--- | :--- |
| Nasiwa Hafswa | Final report sections 1–3 and known limitations | `docs/final-engineering-report.md` |
| Armand Shematsi | README, `.env.example`, architecture review | `README.md` |
| Ainembabazi Kiiza Davis | Demonstration outline and evidence pack | `docs/presentation.md` |
| Alvin Mayega Kenneth | Final test run and release checklist | `tests/`, `results/week7_evaluation.md` |
| All members | Documentation / GitHub / ClickUp | Week 8 submission pack |

### 6. Plan after Week 8

Present the live demonstration: successful ITEM-004 draft, one inspectable trace, and one recovered failure (ITEM-005 expired quote). Answer questions on guardrails and human approval.

### 7. Week 8 Status

**Overall status:** Ready for demonstration

The system is bounded, tested, documented and reproducible locally. Humans retain purchasing decisions.
