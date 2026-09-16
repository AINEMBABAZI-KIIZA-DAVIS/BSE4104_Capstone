# ProcurePrep Evaluation Report: RAG vs. Baseline Completeness Checking

## 1. Executive Summary

This report evaluates the performance of the ProcurePrep completeness checking pipeline across two distinct phases:
- **Baseline (Week 2):** Direct prompt-based evaluation using `gemini-3.5-flash-lite`, `prompt_v1.txt`, and standard checklist matching without external grounding (`results_filled.md`).
- **RAG-Augmented (Week 3):** Retrieval-Augmented Generation using `gemini-2.0-flash`, `prompt_v2.txt`, and context dynamically retrieved from a 10-document ChromaDB vector store (`procureprep_corpus`) (`results_rag.md`).

Across the 10 standardized test cases (TC-01 through TC-10), RAG delivered measurable, significant improvements in accuracy, compliance verification, and hallucination reduction:
- **Improved:** 5 test cases (TC-04, TC-05, TC-06, TC-07, TC-10)
- **Stayed the Same:** 5 test cases (TC-01, TC-02, TC-03, TC-08, TC-09)
- **Got Worse / Regressions:** 0 test cases

---

## 2. Test Case by Test Case Detailed Comparison

| Test Case | Description | Baseline Result (`results_filled.md`) | RAG Result (`results_rag.md`) | Evaluation Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Fully complete submission (8/8 present) | All 8 marked `PRESENT` | All 8 marked `PRESENT` (Cites `tender_checklist.txt`) | **Same** (Correct pass) |
| **TC-02** | Missing Bid Security | Correctly flagged Bid Security as `MISSING` | Correctly flagged Bid Security as `MISSING` | **Same** (Correct pass) |
| **TC-03** | Missing References & Cover Letter | Correctly flagged both items as `MISSING` | Correctly flagged both items as `MISSING` | **Same** (Correct pass) |
| **TC-04** | Minimal submission (Financial proposal in ZAR) | Marked Financial Proposal as `PRESENT` | Flagged Financial Proposal as `MISSING` due to currency mismatch (ZAR vs. required UGX) | **Improved** |
| **TC-05** | Ambiguous / vague submission | Marked 2 items `PRESENT`, 3 `MISSING`, 3 `CANNOT DETERMINE` | Marked 0 items `PRESENT`, 5 `MISSING`, 3 `CANNOT DETERMINE` | **Improved** |
| **TC-06** | Expired documents (Tax Clearance & Bid Security) | Marked all 8 items `PRESENT` (Missed expiry dates completely) | Flagged Tax Clearance & Bid Security as `MISSING` with expiration dates | **Improved** |
| **TC-07** | Wrong tender reference (RFT-2025-017) | Marked all 8 items `PRESENT` (Ignored wrong tender reference) | Flagged Cover Letter as `MISSING` due to wrong tender reference & internal inconsistency | **Improved** |
| **TC-08** | Only 1 of 2 reference letters provided | Correctly flagged Reference Letters as `MISSING` | Correctly flagged Reference Letters as `MISSING` | **Same** (Correct pass) |
| **TC-09** | Unsigned cover letter | Correctly flagged Signed Cover Letter as `MISSING` | Correctly flagged Signed Cover Letter as `MISSING` | **Same** (Correct pass) |
| **TC-10** | Duplicate and conflicting documents | Marked all 8 items `PRESENT` (Missed conflicting versions & math) | Flagged Tax Clearance, Technical Proposal, and Financial Proposal as `MISSING` with conflict details | **Improved** |

---

## 3. Deep-Dive Analysis on Critical Test Cases

### TC-05: Ambiguous Submission
- **Baseline Behavior:** The baseline model was too lenient. It categorized the Technical Proposal and Company Profile as `PRESENT` simply because text mentioning them existed, despite the content being high-level and vague. It gave the benefit of the doubt to phrases like "registration papers available on request" by assigning `CANNOT DETERMINE`.
- **RAG Behavior:** RAG achieved zero false positives (0 `PRESENT` items). Grounded in the explicit document definitions from `tender_checklist.txt`, RAG recognized that promising a document ("available on request") does not constitute submitting a document; hence, Company Registration, Tax Clearance, and Bid Security were correctly classified as `MISSING`. Furthermore, RAG strictly categorized Technical Proposal, Financial Proposal, and Company Profile under `CANNOT DETERMINE` because the text lacked the required itemised breakdowns and methodology.

### TC-06: Expired Documents
- **Baseline Behavior:** Complete failure. The baseline model operated as a superficial keyword/existence matcher, marking all documents `PRESENT` and completely overlooking that the Tax Clearance Certificate expired on 31 December 2024 and the Bid Security had expired prior to the September 2026 submission date.
- **RAG Behavior:** Total success. The RAG pipeline correctly flagged both the Tax Clearance Certificate and the Bid Security as `MISSING`, providing explicit explanations citing the expiration dates relative to the submission date.
- **Grounding Analysis:** ChromaDB retrieved `tender_checklist.txt` (which explicitly requires a valid URA Tax Clearance Certificate), along with `vendor_evaluation_criteria.txt`, `supplier_terms_conditions.txt`, and `contract_negotiation_guidelines.txt`. Combined with prompt v2 Rule 7 (validity: not expired), the system enforced business validation rules that pure baseline existence checking failed to apply.

### TC-07: Wrong Tender Reference
- **Baseline Behavior:** Failed to validate internal consistency. The baseline marked all 8 items as `PRESENT`, completely missing that the Cover Letter referenced Tender `RFT-2025-017` instead of the active tender `RFT-2026-004`.
- **RAG Behavior:** Grounded in the requirement for internal consistency across tender submission documents, RAG identified the mismatched tender code on the Cover Letter and marked `Signed Cover Letter` as `MISSING`.

### Additional Highlights (TC-04 & TC-10)
- **TC-04 Currency Validation:** Grounded by `tender_checklist.txt` ("Financial proposal (in UGX)"), RAG recognized that the submitted pricing of ZAR 490,000 violated the tender instructions, correctly marking it `MISSING`.
- **TC-10 Duplicate & Conflicting Docs:** Baseline marked all items `PRESENT`. RAG detected duplicate Tax Clearance versions (including an expired Version B), conflicting Technical Proposals (Draft vs. Final), and a numerical discrepancy in the Financial Proposal (Lot 3 subtotal ZAR 320,000 vs. ZAR 290,000 summary), marking all three as `MISSING`.

---

## 4. Retrieval Relevance and Noise Filtering

An inspection of `retrieval_log.txt` versus `results_rag.md` shows the following retrieval characteristics:
- **Retrieval Profile:** ChromaDB queries (using all-MiniLM-L6-v2 embeddings) retrieved the top 4 chunks for each test case query. Across all runs, `tender_checklist.txt` consistently ranked #1 with cosine similarity scores between 0.629 and 0.662.
- **Noise Analysis:** Ranks #2 through #4 frequently retrieved peripheral documents such as `purchase_order_template.txt`, `contract_negotiation_guidelines.txt`, or `supplier_terms_conditions.txt`.
- **Noise Filtering:** Despite the presence of non-governing templates in the context window, `gemini-2.0-flash` demonstrated strong noise immunity. In `results_rag.md`, the model cited `tender_checklist.txt` exclusively across all test cases, using it to verify mandatory requirements (trading license, URA clearance, UGX currency, reference counts) without hallucinating requirements from the purchase order templates.

---

## 5. Conclusion

Adding Retrieval-Augmented Generation (RAG) measurably and significantly improved completeness checking for the ProcurePrep use case. Baseline prompting was limited to lexical existence matching, which allowed expired documents, mismatched tender references, foreign currencies, and conflicting submissions to pass undetected. Grounding the generation with retrieved procurement knowledge and strict validity guidelines transformed ProcurePrep from a naive keyword detector into an intelligent procurement compliance assistant capable of enforcing actual tender rules, with zero observed regressions across all test cases.
