# ProcurePrep – Week 3 Progress Report

**Milestone:** Context Engineering & Retrieval-Augmented Generation (RAG)  
**Author:** AI Agentic Development Team  
**Date:** September 17, 2026  
**Course / Project:** BSE4104 AI Agentic Capstone

---

## 1. Executive Summary

Week 3 rebuilds the RAG layer around the **corrected SME procurement-preparation workflow** established in Week 2. Rather than grounding a tender-submission completeness checker, ProcurePrep now retrieves from a 12-document internal knowledge corpus to support **inventory reorder quotation comparison** and **policy/template Q&A**.

Legacy tender-oriented artifacts remain untouched under `legacy/`. New RAG infrastructure lives at the project root: `knowledge/`, `src/ingest.py`, `src/embed_store.py`, `src/retrieve.py`, and `src/rag_reorder_checker.py`.

### Key Deliverables

1. **Corrected knowledge corpus** (12 documents) with register in `docs/corpus_register.md`
2. **RAG-augmented reorder checker** extending Week 2's deterministic gate with retrieval + grounded Gemini explanations
3. **15-question RAG evaluation suite** with documented failures in `results/week3_rag_evaluation.md`
4. **Architecture diagram** in `docs/architecture/rag-architecture.md`

---

## 2. Corpus Correction

### Kept (9 from legacy + 1 policy doc)

The majority of the original `knowledge/` content was already SME-relevant and was promoted to the active corpus:

- Requisition checklist and templates (goods + services)
- Purchase order template
- Supplier terms, code of conduct, vendor evaluation criteria
- Contract negotiation guidelines
- **`procurement_policy_ug.txt`** — retained because its purchase-value bands (micro / small / large) and three-quote rule apply directly to SME quotation comparison, not only to external tenders

### Removed

- **`tender_checklist.txt`** — removed from the active corpus. Content covers trading licenses, URA tax clearance, incorporation certificates, and technical/financial bid proposals for **external tender packages**. This is scope drift from the charter; the file remains in `legacy/knowledge/` for audit only.

### Added (3 new documents)

| Document | Purpose |
| :--- | :--- |
| `sme_reorder_policy.txt` | Reorder trigger rules, quote solicitation, validity requirements, human approval gate |
| `quotation_evaluation_criteria_sme.txt` | Required quotation fields and standard risk flags for small-purchase comparison |
| `supplier_code_of_conduct_addendum.txt` | SME local-purchasing addendum (registration, quotation integrity, violation reporting) |

**Total:** 12 documents → 12 embedding chunks (400-word chunk size; each file fits in one chunk).

---

## 3. Technical Architecture

Week 2's deterministic reorder gate is unchanged. RAG sits **downstream** of the gate, only when quotes exist:

```
inventory.csv → reorder check → quotations.csv → retrieval query
                                                      ↓
knowledge/*.txt → ingest → embed → ChromaDB ← top-k chunks
                                                      ↓
                              RELEVANT KNOWLEDGE + quote data
                                                      ↓
                              Gemini (prompt_rag_v1.0.txt)
                                                      ↓
                         comparison report + SOURCES USED
                                                      ↓
                              human manager review
```

See `docs/architecture/rag-architecture.md` for the full Mermaid diagram and component table.

### Implementation Notes

- **`src/rag_reorder_checker.py`:** Batch mode mirrors `main.py` item loop; adds retrieval before each comparison LLM call. `--question` mode supports standalone policy Q&A for evaluation.
- **`prompts/prompt_rag_v1.0.txt`:** Extends Week 2 prompt v1.1 with KNOWLEDGE GROUNDING rules, Policy Question Mode, and mandatory **SOURCES USED** section.
- **Vector store:** ChromaDB collection `procureprep_corpus`, Gemini `models/gemini-embedding-001`, rebuilt clean (12 chunks, no orphan `tender_checklist` embedding).

---

## 4. Evaluation Highlights

Fifteen test questions across three categories (`results/week3_rag_evaluation.md`):

| Category | Examples | Result |
| :--- | :--- | :--- |
| **Answerable** | Goods requisition template fields; three-quote rule for UGX 500k–5M band | 5/5 grounded correctly with source citations |
| **Partially answerable** | Environmental certifications; >5M approval workflow; dispute resolution | 4/5 handled well; 1 under-answered (dispute resolution) |
| **Unanswerable** | QuickFix unit price; inventory-specific thresholds; supplier PII | 5/5 refused without hallucination |

**Integration test (ITEM-001):** RAG comparison cited `procurement_policy_ug.txt` for the three-quote threshold and `quotation_evaluation_criteria_sme.txt` for risk-flag vocabulary. Output: `results/reorder_reports_rag_sample.md`.

### Documented Failures (3)

1. **False `[MISSING TERMS]` on Q-103** — delivery method present in CSV but flagged because transport cost responsibility was ambiguous; prompt over-triggered the flag.
2. **Dispute resolution partial miss** — `contract_negotiation_guidelines.txt` retrieved but model answered fully unanswerable instead of noting the topic is a negotiation focus without prescribing a mechanism.
3. **Noisy retrieval for operational questions** — small single-chunk corpus forces top-4 hits on generic policy docs even when the answer requires CSV data; generation still refused correctly.

---

## 5. What Changed from Legacy Week 3

| Dimension | Legacy (Tender RAG) | Rebuilt Week 3 (SME RAG) |
| :--- | :--- | :--- |
| **Use case** | Tender submission completeness vs checklist | Reorder quotation comparison + policy Q&A |
| **Primary retrieval target** | `tender_checklist.txt` | `sme_reorder_policy.txt`, `quotation_evaluation_criteria_sme.txt` |
| **Orchestrator** | `legacy/src/rag_checker.py` | `src/rag_reorder_checker.py` |
| **Operational data** | Free-text submissions | Structured CSV inventory + quotations |
| **Output contract** | PRESENT / MISSING / CANNOT DETERMINE | Comparison tables + SOURCES USED |

---

## 6. Next Steps: Week 4 Preview

Week 3 intentionally stops at retrieve → generate. Week 4 will add:

1. **Tool use / function calling** — e.g. fetch live inventory rows, draft requisitions from templates
2. **Agent orchestration** — multi-step flows from reorder alert through requisition draft
3. **Retrieval refinements** — score thresholds, separate operational vs policy collections, partial-answer prompt tuning

No changes were made to `legacy/` in this rebuild step.
