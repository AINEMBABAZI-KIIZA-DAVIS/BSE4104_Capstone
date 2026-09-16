# Legacy Tender Completeness Checker Build (Archived)

## Overview & Scope Correction
This directory archives the files from the initial Week 2 and early Week 3 implementation of the ProcurePrep project.

### Why Were These Files Moved?
The project Charter defines **ProcurePrep UG** as an **AI-Native SME Procurement-Preparation Agent** designed to automate internal purchasing preparation for small-and-medium enterprises (SMEs). The core operational workflow is:
$$\text{Inventory Monitoring} \longrightarrow \text{Reorder Check} \longrightarrow \text{Quotation Comparison} \longrightarrow \text{Requisition Drafting} \longrightarrow \text{Human Approval}$$

During initial development, a scope drift occurred: the system was erroneously built as an external tender-bid completeness checker (evaluating vendor bid submissions against formal public procurement checklists). 

To realign the codebase with the actual project Charter without discarding auditability, these legacy files have been preserved in `legacy/` rather than deleted.

### Archived Files
- `main.py`: Original tender bid evaluation script.
- `checklist.txt`: 8-point tender compliance checklist.
- `submission_1.txt` to `submission_10.txt`: Synthetic tender bid response documents (TC-01 to TC-10).
- `cache.json`, `cache_builder.py`: Response caching utilities for the tender checker.
- `prompt_v1.txt`, `prompt_v1.1.txt`: Prompts designed for tender document completeness checking.
- `results_filled.md`, `results_v1.1.md`, `results_template.md`: Baseline test results for the tender bid checker.

All active development for the SME Procurement-Preparation Agent now resides in the project root (`data/`, `prompts/`, `docs/`, `results/`, `main.py`).
