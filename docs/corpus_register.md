# ProcurePrep Knowledge Corpus Register

**Last updated:** 2026-09-17 (Week 3 scope correction)  
**Location:** `knowledge/`  
**Vector store:** ChromaDB collection `procureprep_corpus` (built via `src/embed_store.py`)

This corpus grounds the SME procurement-preparation workflow: inventory reorder checks, quotation comparison, requisition drafting, and supplier compliance—not external tender bid submission.

---

## Corpus Summary

| # | Filename | Purpose | Provenance | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `requisition_checklist.txt` | Internal approval checklist before a purchase requisition is authorized (budget, signatures, specifications, threshold, justification). | team-created/synthetic | **Kept** |
| 2 | `requisition_template_goods.txt` | Standard fields for requesting physical goods (quantity, UGX pricing, purpose, approver). | team-created/synthetic (public template style) | **Kept** |
| 3 | `requisition_template_services.txt` | Standard fields for requesting services (duration, location, deliverables, justification). | team-created/synthetic (public template style) | **Kept** |
| 4 | `purchase_order_template.txt` | PO layout: line items, UGX subtotal, 18% VAT, authorized signature. | team-created/synthetic (public template style) | **Kept** |
| 5 | `supplier_terms_conditions.txt` | Default supplier T&Cs: 30-day net payment, UGX currency, Kampala delivery, quality/returns, 14-day termination notice. | team-created/synthetic | **Kept** |
| 6 | `supplier_code_of_conduct.txt` | Ethical expectations: Ugandan law compliance, anti-corruption, labor rights, environment, conflict of interest. | team-created/synthetic | **Kept** |
| 7 | `supplier_code_of_conduct_addendum.txt` | SME-specific addendum: local registration, quotation integrity, delivery commitments, violation reporting. | team-created/synthetic | **Added (Week 3)** |
| 8 | `vendor_evaluation_criteria.txt` | Formal scoring weights: Price 40%, Quality 30%, Experience 15%, Delivery 15%; 70% minimum pass threshold. | team-created/synthetic | **Kept** |
| 9 | `quotation_evaluation_criteria_sme.txt` | Required quotation fields and risk flags for small-purchase / reorder comparison (validity, MOQ, shortfall, anomalies). | team-created/synthetic | **Added (Week 3)** |
| 10 | `sme_reorder_policy.txt` | When to reorder (stock < threshold), quote solicitation rules, validity requirements, human approval gate. | team-created/synthetic | **Added (Week 3)** |
| 11 | `procurement_policy_ug.txt` | SME purchase-value bands: micro direct buy (< UGX 500k), small purchases (3 quotes, UGX 500k–5M), large/open tender (> UGX 5M); local preference. | team-created/synthetic (informed by PPDA SME concepts) | **Kept** |
| 12 | `contract_negotiation_guidelines.txt` | Negotiation focus areas: market rates, payment/delivery/warranty clauses, legal/procurement approval for non-standard terms. | team-created/synthetic | **Kept** |

**Total active documents:** 12

---

## Documents Removed or Set Aside

| Filename | Decision | Rationale |
| :--- | :--- | :--- |
| `tender_checklist.txt` | **Removed from active corpus** | Content is exclusively external tender-submission oriented (trading license, URA tax clearance, certificate of incorporation, technical/financial proposals for bid packages). This belongs to the legacy tender-checker use case in `legacy/`, not the SME internal reorder → quotation → requisition workflow. Retained only under `legacy/knowledge/` for auditability. |
| `procurement_policy_ug.txt` | **Kept** | Although it mentions “open tendering” for purchases over UGX 5M, the threshold bands and three-quote rule for small purchases are directly applicable to SME quotation comparison and requisition approval. It is not tender-checklist-specific. |

---

## Chunking & Embedding

- **Ingestion:** `src/ingest.py` — 400-word chunks, 50-word overlap.
- **Embeddings:** Gemini `models/gemini-embedding-001` with `retrieval_document` / `retrieval_query` task types.
- **Storage:** ChromaDB persistent client at `chroma_db/`.

Re-run after corpus changes:

```bash
python src/embed_store.py
```

---

## Intended Retrieval Targets by Workflow Step

| Workflow step | Primary corpus documents |
| :--- | :--- |
| Reorder triggered | `sme_reorder_policy.txt`, `procurement_policy_ug.txt` |
| Quotation comparison | `quotation_evaluation_criteria_sme.txt`, `supplier_terms_conditions.txt`, `vendor_evaluation_criteria.txt` |
| Requisition drafting (Week 4+) | `requisition_template_goods.txt`, `requisition_template_services.txt`, `requisition_checklist.txt` |
| PO issuance | `purchase_order_template.txt`, `supplier_terms_conditions.txt` |
| Supplier compliance | `supplier_code_of_conduct.txt`, `supplier_code_of_conduct_addendum.txt` |
