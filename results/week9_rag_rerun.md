# ProcurePrep UG — Live RAG Verification Report (Week 9)

**Operating Date:** 2026-10-18  
**Pipeline:** `src/rag_reorder_checker.py --question`  
**Model:** `gemini-3.5-flash-lite` via `google-genai`  
**Vector Store:** ChromaDB `procureprep_corpus`, top_k=4  

## 1. Executive Summary

In the original Week 3 RAG evaluation (`results/week3_rag_evaluation.md`), 5 of the 15 policy questions were not run live against the Gemini API: RQ-02 was retrieval-only ('would list'), and RQ-12 to RQ-15 were marked as 'assumed'.

This run executes all 5 missing questions live through the end-to-end RAG pipeline (`src/rag_reorder_checker.py`), capturing the actual retrieved chunks, scores, generated text, grounding citations, and refusal behaviors.

---

## 2. Live Execution Results

### RQ-02: What terms should a supplier quotation specify?
- **Category:** Answerable
- **Verdict:** **PASS** (Grounded answer listing required quotation fields and citing sources.)
- **Retrieval Top Chunks:**
  Retrieved 4 chunk(s):
    - quotation_evaluation_criteria_sme.txt (chunk 0, score=0.6524)
    - supplier_terms_conditions.txt (chunk 0, score=0.6349)
    - sme_reorder_policy.txt (chunk 0, score=0.614)
    - vendor_evaluation_criteria.txt (chunk 0, score=0.6118)

**Generated Model Response:**

```markdown
### POLICY / TEMPLATE ANSWER [RAG v1.0]

**Question:** What terms should a supplier quotation specify?

**Answer:**
According to the SME procurement guidelines and evaluation criteria, a supplier quotation must specify the following minimum information:
- Supplier name
- Unit price in Uganda Shillings (UGX)
- Quantity available relative to the replenishment need
- Delivery terms, which must include the delivery location, lead time, and transport responsibility
- Quotation validity date (`valid_until`)
- Optional notes such as Minimum Order Quantity (MOQ), split-order constraints, and non-standard payment terms.

*(Sources: `quotation_evaluation_criteria_sme.txt`, `sme_reorder_policy.txt`)*

**SOURCES USED:**
- `quotation_evaluation_criteria_sme.txt`
- `sme_reorder_policy.txt`
```

---

### RQ-12: Which supplier won the last cleaning supplies contract?
- **Category:** Deliberately unanswerable
- **Verdict:** **PASS** (Refused correctly without hallucination; respected knowledge boundary.)
- **Retrieval Top Chunks:**
  Retrieved 4 chunk(s):
    - vendor_evaluation_criteria.txt (chunk 0, score=0.5837)
    - supplier_terms_conditions.txt (chunk 0, score=0.5696)
    - supplier_code_of_conduct.txt (chunk 0, score=0.5646)
    - procurement_policy_ug.txt (chunk 0, score=0.5642)

**Generated Model Response:**

```markdown
### POLICY / TEMPLATE ANSWER [RAG v1.0]

**Question:** Which supplier won the last cleaning supplies contract?

**Answer:**
Cannot determine from the available knowledge corpus. The retrieved documents contain vendor evaluation criteria, supplier terms and conditions, a supplier code of conduct, and SME procurement policies, but do not contain historical contract award records or specific transaction data regarding cleaning supplies.

**SOURCES USED:**
- None – question outside corpus scope
```

---

### RQ-13: What is the exact legal liability cap in our standard contract?
- **Category:** Deliberately unanswerable
- **Verdict:** **PASS** (Refused correctly without hallucination; respected knowledge boundary.)
- **Retrieval Top Chunks:**
  Retrieved 4 chunk(s):
    - supplier_terms_conditions.txt (chunk 0, score=0.5717)
    - contract_negotiation_guidelines.txt (chunk 0, score=0.5592)
    - supplier_code_of_conduct_addendum.txt (chunk 0, score=0.5582)
    - quotation_evaluation_criteria_sme.txt (chunk 0, score=0.5558)

**Generated Model Response:**

```markdown
### POLICY / TEMPLATE ANSWER [RAG v1.0]

**Question:** What is the exact legal liability cap in our standard contract?

**Answer:**
The available knowledge corpus cannot determine the exact legal liability cap. The supplier code of conduct addendum notes that monetary fine schedules and criminal penalties are not specified and are governed by applicable law and separate legal contracts (`supplier_code_of_conduct_addendum.txt`), but none of the retrieved corpus documents specify a numerical or contractual legal liability cap.

**SOURCES USED:**
- supplier_code_of_conduct_addendum.txt
```

---

### RQ-14: What is the name of our preferred toner cartridge supplier?
- **Category:** Deliberately unanswerable
- **Verdict:** **PASS** (Refused correctly without hallucination; respected knowledge boundary.)
- **Retrieval Top Chunks:**
  Retrieved 4 chunk(s):
    - vendor_evaluation_criteria.txt (chunk 0, score=0.5812)
    - supplier_terms_conditions.txt (chunk 0, score=0.5777)
    - supplier_code_of_conduct.txt (chunk 0, score=0.5756)
    - supplier_code_of_conduct_addendum.txt (chunk 0, score=0.57)

**Generated Model Response:**

```markdown
### POLICY / TEMPLATE ANSWER [RAG v1.0]

**Question:** What is the name of our preferred toner cartridge supplier?

**Answer:**
Cannot determine from the available knowledge corpus. The provided procurement knowledge documents do not list specific approved vendors, preferred suppliers, or item-specific supplier assignments for toner cartridges.

**SOURCES USED:**
- None – question outside corpus scope
```

---

### RQ-15: What is the current VAT registration number of Kampala Office Supplies?
- **Category:** Deliberately unanswerable
- **Verdict:** **PASS** (Refused correctly without hallucination; question outside corpus scope.)
- **Retrieval Top Chunks:**
  Retrieved 4 chunk(s):
    - purchase_order_template.txt (chunk 0, score=0.591)
    - supplier_terms_conditions.txt (chunk 0, score=0.5781)
    - procurement_policy_ug.txt (chunk 0, score=0.5738)
    - supplier_code_of_conduct.txt (chunk 0, score=0.5713)

**Generated Model Response:**

```markdown
### POLICY / TEMPLATE ANSWER [RAG v1.0]

**Question:** What is the current VAT registration number of Kampala Office Supplies?

**Answer:**
The answer cannot be determined from the available knowledge corpus. None of the retrieved documents mention Kampala Office Supplies or its VAT registration number.

**SOURCES USED:**
- None – question outside corpus scope
```

---
