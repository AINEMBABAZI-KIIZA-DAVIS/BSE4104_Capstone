# Legacy Tender Completeness Checker Build (Archived)

## Overview & Scope Correction
This directory archives the entire codebase and all artifacts from the initial Week 2 and Week 3 implementation of the ProcurePrep project.

### Why Were These Files Moved?
The project Charter defines **ProcurePrep UG** as an **AI-Native SME Procurement-Preparation Agent** designed to automate internal purchasing preparation for small-and-medium enterprises (SMEs). The core operational workflow is:
$$\text{Inventory Monitoring} \longrightarrow \text{Reorder Check} \longrightarrow \text{Quotation Comparison} \longrightarrow \text{Requisition Drafting} \longrightarrow \text{Human Approval}$$

During initial development, a scope drift occurred: the system was erroneously built as an external tender-bid completeness checker (evaluating vendor bid submissions against formal public procurement checklists). 

To realign the codebase with the actual project Charter without discarding auditability or history, all legacy files from that direction have been consolidated here in `legacy/` rather than deleted.

### Archived Files & Components
- **Batch Runners & Logic:**
  - `main.py`: Original tender bid evaluation script (baseline).
  - `run_all.py`: Batch runner supporting both baseline and tender RAG mode.
  - `cache_builder.py`, `cache.json`: Caching utilities.
- **RAG & Vector Search (Tender-Specific):**
  - `src/`: Contains `ingest.py`, `embed_store.py`, `retrieve.py`, and `rag_checker.py` built for the tender checklist corpus.
  - `knowledge/`: 10 tender and public procurement policy text files.
- **Tender Test Submissions & Checklists:**
  - `checklist.txt`: 8-point tender compliance checklist.
  - `submission_1.txt` through `submission_10.txt`: Synthetic vendor bid response documents (TC-01 to TC-10).
- **Prompts & Prompt History (Tender Checker):**
  - `prompt_v1.txt`: Baseline tender existence prompt.
  - `prompt_v1.1.txt`: Rule-based validity prompt for tenders.
  - `prompt_v2.txt`: RAG-augmented prompt for tender compliance checking.
  - `prompt_version_history.md`: Old prompt evolution notes for the tender checker.
- **Results & Evaluations (Tender Checker):**
  - `results_filled.md`, `results_v1.1.md`, `results_template.md`: Baseline tender test logs.
  - `results_rag.md`: RAG-augmented tender evaluation results.
  - `retrieval_log.txt`: ChromaDB retrieval log for tender cases.
  - `evaluation_rag.md`: Detailed comparative report of the old tender RAG vs baseline.
  - `docs_requirements/`: Requirements register for the old tender corpus.

---

### Active Project
All active development for the **ProcurePrep SME Procurement Agent** resides in the root workspace:
- `data/`: SME inventory (`inventory.csv`) and supplier quotation records (`quotations.csv`).
- `main.py`: SME procurement preparation engine (deterministic reorder logic + Gemini quotation analysis).
- `prompts/`: Active prompt specifications and version history (`prompt_spec_v1.0.md`, `prompt_spec_v1.1.md`, `prompt_version_history.md`).
- `results/`: Test logs and evaluation reports (`week2_evaluation.md`, `reorder_reports_v1.1.md`).
- `docs/`: Model selection notes and weekly milestone reports (`docs/model-selection-note.md`, `docs/weekly-reports/week2.md`).
