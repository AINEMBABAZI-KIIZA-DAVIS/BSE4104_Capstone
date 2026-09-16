# Prompt Version History

## Overview
This document tracks the evolution of the ProcurePrep system prompt from the initial baseline existence checker to the RAG-grounded compliance assistant.

| Version | Focus / Mode | Key Additions | Primary Motivation / Trigger |
| :--- | :--- | :--- | :--- |
| **v1.0** | Lexical Existence Checker | Baseline instructions, no scoring/assumptions, standard output format | Initial project establishment |
| **v1.1** | Rule-Based Validity Checker | Strict Document Validity Rule (expiry dates, internal consistency, duplicate/conflicting docs) | Baseline failures on TC-06 (expired docs) and TC-10 (conflicting docs) |
| **v2.0** | RAG-Augmented Compliance Assistant | Dynamic knowledge grounding block, explicit `SOURCES USED` citation requirement, external policy enforcement (e.g. UGX currency, URA clearance) | Transition to contextual procurement compliance verification using ChromaDB vector retrieval |

---

## Detailed Version Log

### v1.0
- **Status:** Initial Baseline Version
- **Model:** `gemini-3.5-flash-lite`
- **Details:** Established the baseline persona and role of ProcurePrep. Instructed the model to perform a strict checklist comparison, listing items as `PRESENT`, `MISSING`, or `CANNOT DETERMINE`. Constrained the model against quality scoring, grading, ranking, or making speculative assumptions.
- **Limitation:** Pure existence/keyword matching failed to detect expired dates, conflicting duplicate files, currency mismatches, or wrong tender references.

### v1.1
- **Date:** 2026-09-09
- **Model:** `gemini-3.5-flash-lite`
- **Changes:** Introduced the **Document Validity Rule (Rule 7)**:
  - Required documents to be non-expired (comparing validity dates against the submission date).
  - Required submissions to be free from contradictory duplicate documents.
  - Required internal consistency across documents (matching company name and tender references).
- **Reason:** Directly addressed failures in test cases **TC-06 (Expired documents)** and **TC-10 (Duplicate and conflicting documents)**, where the v1.0 prompt marked expired and conflicting documents as present.

### v2.0
- **Status:** RAG-Augmented Production Version (Week 3 Milestone)
- **Model:** `gemini-2.0-flash`
- **Changes:** 
  - Added the **Knowledge Grounding** block instructively bounding the model's reasoning exclusively to the retrieved passages from the `procureprep_corpus`.
  - Added mandatory **`SOURCES USED`** reporting format to attribute determinations directly to retrieved documents (e.g., `tender_checklist.txt`).
  - Integrated domain-specific compliance checks (e.g., verifying UGX currency and URA tax clearance requirements) retrieved dynamically from the vector store.
- **Reason:** Transitioned ProcurePrep from a static prompt checker to a knowledge-grounded compliance system, resolving subtle edge cases like foreign currency submissions (TC-04), ambiguous tender promises (TC-05), expired records (TC-06), mismatched tender references (TC-07), and conflicting submissions (TC-10).
