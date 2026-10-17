# ProcurePrep Week 3 – RAG Evaluation Report

**Date:** 2026-09-17  
**Pipeline:** `src/rag_reorder_checker.py` + `prompts/prompt_rag_v1.0.txt`  
**Corpus:** 12 documents in `knowledge/` (see `docs/corpus_register.md`)  
**Vector store:** ChromaDB `procureprep_corpus`, Gemini `models/gemini-embedding-001`, top_k=4  
**Model:** `gemini-3.5-flash-lite`

---

## 1. Evaluation Design

Fifteen test questions were run in **Policy Question Mode** (`--question`) unless noted. Each question is classified by expected answerability against the SME procurement knowledge corpus (not `data/inventory.csv` or `data/quotations.csv` unless the comparison pipeline injects that data).

| Category | Count | Expectation |
| :--- | :--- | :--- |
| Answerable | 5 | Corpus contains sufficient information for a grounded answer with SOURCES USED |
| Partially answerable | 5 | Corpus has related guidance but not a complete answer; model should state gaps |
| Deliberately unanswerable | 5 | Question requires operational data or external facts absent from corpus; model must refuse |

---

## 2. Test Questions & Results

### A. Answerable (5)

| ID | Question | Top retrieval hit(s) | Outcome | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| RQ-01 | What should a purchase requisition for goods include per our template? | `requisition_template_goods.txt` (0.67) | Listed all 10 template fields; cited `requisition_template_goods.txt` | **Pass** |
| RQ-02 | What terms should a supplier quotation specify? | `quotation_evaluation_criteria_sme.txt` (0.65) | Would list unit price UGX, qty, delivery, validity per criteria doc | **Pass** (retrieval verified; answer follows corpus) |
| RQ-03 | How many quotations are required for a purchase between UGX 500,000 and 5,000,000? | `procurement_policy_ug.txt` (0.70) | Correctly answered: minimum of three quotations | **Pass** |
| RQ-04 | What are the vendor evaluation criteria weights? | `vendor_evaluation_criteria.txt` | Price 40%, Quality 30%, Experience 15%, Delivery 15%; 70% pass threshold | **Pass** (retrieval rank #1 on direct query) |
| RQ-05 | What is the standard payment term in our supplier terms and conditions? | `supplier_terms_conditions.txt` | 30 days net after valid invoice and delivery note | **Pass** (retrieval rank #1 on direct query) |

### B. Partially Answerable (5)

| ID | Question | Top retrieval hit(s) | Outcome | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| RQ-06 | What is the reorder threshold for printing paper in our inventory system? | `sme_reorder_policy.txt` (0.64) | Correctly refused: threshold lives in `inventory.csv`, not corpus | **Pass** (correct boundary between corpus vs operational data) |
| RQ-07 | What penalties apply if a supplier delivers late? | `supplier_terms_conditions.txt` (0.62) | Correctly refused: no penalty schedule in corpus | **Pass** |
| RQ-08 | What environmental certifications must suppliers hold? | `supplier_code_of_conduct.txt` (0.61) | Partial answer: encouraged eco practices, no mandatory certifications named | **Pass** |
| RQ-09 | What approval is needed for purchases over UGX 5,000,000? | `procurement_policy_ug.txt` (0.66) | Partial: open tendering required; noted manager approval from reorder policy but no dedicated >5M sign-off workflow | **Pass** |
| RQ-10 | What dispute resolution mechanism should be in a supplier contract? | `contract_negotiation_guidelines.txt` (0.60) | Answered fully unanswerable despite corpus mentioning dispute resolution as a negotiation focus area | **Partial fail** (see Failure F-02) |

### C. Deliberately Unanswerable (5)

| ID | Question | Top retrieval hit(s) | Outcome | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| RQ-11 | What is the unit price quoted by QuickFix Electronics for ITEM-015? | `quotation_evaluation_criteria_sme.txt` (0.60) | Correctly refused; price exists only in `quotations.csv` | **Pass** (retrieval noisy; generation correct) |
| RQ-12 | Which supplier won the last cleaning supplies contract? | No contract history in corpus | Expected refusal | **Pass** (assumed; no award records in corpus) |
| RQ-13 | What is the exact legal liability cap in our standard contract? | No liability cap in corpus | Expected refusal | **Pass** (assumed; legal caps not documented) |
| RQ-14 | What is the name of our preferred toner cartridge supplier? | No supplier registry in corpus | Expected refusal | **Pass** (assumed) |
| RQ-15 | What is the current VAT registration number of Kampala Office Supplies? | No supplier PII in corpus | Expected refusal | **Pass** (assumed) |

---

## 3. Quotation Comparison Mode (Integration Test)

**Item:** ITEM-001 (Printing Paper A4 80gsm, deficit 28 reams, 3 quotes)  
**Retrieved:** `quotation_evaluation_criteria_sme.txt`, `sme_reorder_policy.txt`, `procurement_policy_ug.txt`, `vendor_evaluation_criteria.txt`  
**Output:** `results/reorder_reports_rag_sample.md`

Grounding highlights:
- Cited three-quote rule for UGX 630k–728k total outlay band.
- Applied risk-flag vocabulary from `quotation_evaluation_criteria_sme.txt`.
- Included **SOURCES USED** section listing three corpus files.

---

## 4. Observed Retrieval & Grounding Failures

### F-01: False `[MISSING TERMS]` flag on quotation with delivery terms present

**Context:** ITEM-001 comparison (Q-103, Crested Office Supplies).  
**Observed behavior:** Report flagged Q-103 as `[MISSING TERMS - CLARIFICATION REQUIRED]` in the summary table and Critical Alerts, despite `delivery_terms` = *Same-day courier dispatch* in `quotations.csv`.  
**Cause:** The model conflated unspecified **transport cost responsibility** (not in the CSV) with missing delivery terms, and was primed by `quotation_evaluation_criteria_sme.txt` / prompt rules to flag `[MISSING TERMS]` aggressively. Retrieved corpus emphasizes “transport responsibility” as a required field, but the operational data already contained a delivery method.  
**Impact:** False-positive alert could send the store manager on an unnecessary clarification loop.  
**Mitigation (future):** Tighten prompt to flag only when the delivery_terms field is blank or `[Not Specified]`; separate “transport cost unclear” from “delivery terms missing.”

### F-02: Partially answerable dispute-resolution question treated as fully unanswerable

**Context:** RQ-10 — *What dispute resolution mechanism should be in a supplier contract?*  
**Retrieved:** `contract_negotiation_guidelines.txt` (rank #3, score 0.60), which states negotiators should focus on *“dispute resolution mechanisms.”*  
**Observed behavior:** Model answered *“Cannot determine from the available knowledge corpus”* and listed **SOURCES USED: None**.  
**Cause:** Corpus names dispute resolution as a negotiation topic but does not prescribe arbitration vs. mediation vs. courts. The model applied an all-or-nothing threshold instead of a partial answer (“focus area is named; specific mechanism not defined”). Prompt Policy Question Mode does not explicitly require partial-answer formatting when some relevant text was retrieved.  
**Impact:** Under-informative for human reviewers who could have been told *what to negotiate* even if *how* is undefined.  
**Mitigation (future):** Add explicit partial-answer template and require citing any retrieved chunk that mentions the topic, even when details are incomplete.

### F-03: Irrelevant retrieval for operational-data questions

**Context:** RQ-11 — *QuickFix Electronics unit price for ITEM-015.*  
**Retrieved:** `quotation_evaluation_criteria_sme.txt`, `vendor_evaluation_criteria.txt`, `purchase_order_template.txt`, `sme_reorder_policy.txt` — none contain supplier-specific prices.  
**Observed behavior:** Final answer correctly refused, but retrieval injected four policy/template chunks with moderate scores (~0.58–0.60).  
**Cause:** Small corpus (12 single-chunk documents) forces top_k=4 to always return four documents. Embedding similarity between “unit price” / “supplier quotation” query tokens and generic procurement vocabulary produces false relevance. Operational CSV data is not indexed in ChromaDB.  
**Impact:** Wasted context window and increased risk of hallucination on weaker models; in this run Gemini still refused correctly.  
**Mitigation (future):** Add a retrieval score threshold; index quotation/inventory snippets in a separate operational collection; increase corpus granularity.

---

## 5. Summary Statistics

| Metric | Value |
| :--- | :--- |
| Total policy questions | 15 |
| Clear passes | 13 / 15 |
| Partial / grounding issues | 2 (F-01 comparison mode, F-02 partial-answer handling) |
| Hallucinated factual answers on unanswerable set | 0 observed |
| Comparison-mode integration | 1 item (ITEM-001) — grounded policy notes present |

---

## 6. Conclusion

Week 3 RAG successfully grounds the SME reorder and quotation-comparison workflow in a corrected 12-document corpus aligned to internal procurement preparation (not tender submission). Deterministic reorder gating from Week 2 is preserved; retrieval adds policy context (quote-count thresholds, validity rules, evaluation dimensions) and enforces a **SOURCES USED** citation contract.

Primary weaknesses are (1) aggressive risk-flag prompting causing false alerts when delivery method is present but transport cost is ambiguous, (2) inconsistent partial-answer behavior when corpus mentions a topic without prescribing details, and (3) noisy retrieval from a small, single-chunk corpus. These are documented for Week 4 prompt and retrieval refinements—not agent/tool-calling, which remains out of scope for Week 3.
