# BSE4104 AI-Native & Agentic Engineering Capstone

## Week 2 Progress Report

**Project:** ProcurePrep UG — AI-Native SME Procurement-Preparation Agent  
**Week:** Week 2  
**Week Ending:** 11 September 2026

### 1. Work Completed

During Week 2, the team rebuilt the foundation-model layer around the approved SME procurement-preparation workflow after an earlier scope drift toward tender-submission checking. Legacy tender artifacts were archived under `legacy/` rather than deleted.

The team integrated Google Gemini 3.5 Flash-Lite through `main.py`, created Prompt Specification v1.0 and a risk-aware v1.1 iteration, and evaluated the baseline on ten test cases covering sufficient stock, missing quotes, expired validity, price outliers and MOQ constraints.

Deterministic Python now decides whether stock is below the reorder threshold. The model is called only when a reorder is needed and quotations exist. It compares tradeoffs and does not select a supplier.

### 2. Key Engineering Decisions

The team selected Gemini 3.5 Flash-Lite for cost, latency and instruction adherence on a small SME workload.

Reorder math (`current_stock < reorder_threshold`) and zero-quote alerts remain in code so the model cannot invent a reorder decision.

Prompt v1.1 added mandatory risk flags after v1.0 buried expired quotes, missing delivery terms and MOQ cash-flow impact in narrative text.

### 3. Challenges

The main challenge was correcting the tender-checker drift without losing auditability. The team archived the first build and rebuilt Week 2 against the charter.

A further challenge was making operational risks visible to a busy storekeeper. Prompt v1.1 addresses this with explicit flags rather than prose-only warnings.

### 4. Repository and Task Evidence

**GitHub Repository:** https://github.com/AINEMBABAZI-KIIZA-DAVIS/BSE4104_Capstone  
**ClickUp Project:** https://app.clickup.com/1200430000003901/v/li/1200430000006616  
**Architecture Evidence:** `submission/WEEK2/SME_Reorder_Architecture.jpg`

### 5. Individual Contributions

| Member | Responsibility | Evidence |
| :--- | :--- | :--- |
| Nasiwa Hafswa | Prompt specification v1.0 / v1.1 and version history | `prompts/prompt_spec_v1.0.md`, `prompts/prompt_spec_v1.1.md` |
| Armand Shematsi | Reorder engine and application integration | `main.py`, `data/inventory.csv`, `data/quotations.csv` |
| Ainembabazi Kiiza Davis | Model selection note and Gemini integration | `docs/model-selection-note.md` |
| Alvin Mayega Kenneth | 10-case evaluation table and prompt comparison | `results/week2_evaluation.md` |
| All members | Documentation / GitHub / ClickUp | Week 2 submission pack |

### 6. Plan for Week 3

During Week 3, the team will assemble a controlled SME procurement corpus, implement ingestion, embedding and retrieval, ground quotation comparison in retrieved sources, and evaluate at least fifteen RAG questions including unanswerable cases.

### 7. Week 2 Status

**Overall status:** On track

The project has a working model-backed baseline, versioned prompts, a documented model rationale and a ten-case evaluation aligned to the SME reorder workflow.
