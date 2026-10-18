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

## 3. Failure Re-Test Verifications (F-01 and F-02)

### RQ-10 Live Re-Test (Evaluating Failure F-02)

**Question:** What dispute resolution mechanism should be in a supplier contract?  
**Pipeline:** `python3 src/rag_reorder_checker.py --question "What dispute resolution mechanism should be in a supplier contract?"`  
**Execution Timestamp:** 2026-10-18T23:05:59  
**Retrieved Chunks:**
- `supplier_code_of_conduct_addendum.txt` (chunk 0, score=0.6061)
- `supplier_terms_conditions.txt` (chunk 0, score=0.6054)
- `contract_negotiation_guidelines.txt` (chunk 0, score=0.6035)
- `supplier_code_of_conduct.txt` (chunk 0, score=0.5963)

**Generated Response:**
```markdown
### POLICY / TEMPLATE ANSWER [RAG v1.0]

**Question:** What dispute resolution mechanism should be in a supplier contract?

**Answer:**
The available knowledge corpus states that dispute resolution mechanisms should be a focus during contract negotiations (per `contract_negotiation_guidelines.txt`). However, the corpus does not define specific methods, steps, or required dispute resolution clauses (such as arbitration, mediation, or court jurisdiction). 

Per `supplier_code_of_conduct_addendum.txt`, criminal penalties, court jurisdiction, and monetary fine schedules are not specified in the supplier addendum and are instead governed by applicable law and separate legal contracts.

**SOURCES USED:**
- contract_negotiation_guidelines.txt (mentions dispute resolution as a key negotiation clause)
- supplier_code_of_conduct_addendum.txt (mentions that jurisdiction and fines are governed by applicable law and separate contracts)
```

**Status of F-02:** **FIXED.**  
In Week 3, the model failed by treating a partially covered topic as an all-or-nothing refusal (*"Cannot determine from the available knowledge corpus"* with *SOURCES USED: None*). In this live re-test, the model correctly produced a nuanced partial answer: it confirmed dispute resolution is a recognized negotiation focus area per `contract_negotiation_guidelines.txt`, explicitly distinguished that specific procedural mechanisms are not prescribed in the corpus, and cited both relevant documents in `SOURCES USED`.

---

### ITEM-001 Live Comparison Re-Test (Evaluating Failure F-01)

**Item:** `ITEM-001` (Printing Paper A4 80gsm, deficit 28 reams, 3 quotations)  
**Pipeline:** `python3 src/rag_reorder_checker.py --items ITEM-001`  
**Execution Timestamp:** 2026-10-18T23:06:19  
**Retrieved Chunks:**
- `quotation_evaluation_criteria_sme.txt` (chunk 0, score=0.7154)
- `sme_reorder_policy.txt` (chunk 0, score=0.7048)
- `procurement_policy_ug.txt` (chunk 0, score=0.6731)
- `vendor_evaluation_criteria.txt` (chunk 0, score=0.6675)

**Generated Quotation Table & Alerts:**
```markdown
#### 1. Quotation Summary Table
| Quotation ID | Supplier Name | Unit Price (UGX) | Available Qty | Delivery Terms | Validity Status | Notes / Flags |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Q-101 | Kampala Modern Stationers Ltd | 24,000 | 100 | Delivery within 2 business days | Valid (2026-10-15) | Free delivery within Kampala central |
| Q-102 | Uganda Paper & Stationery Mills | 22,500 | 500 | 5-7 business days transit time | Valid (2026-10-30) | Bulk warehouse dispatch from Jinja |
| Q-103 | Crested Office Supplies | 26,000 | 50 | Same-day courier dispatch | Valid (2026-09-30) | Payment terms: Cash on delivery |

#### 3. Critical Alerts & Risk Observations
- No critical risk flags triggered (all quotes are valid, delivery terms are present, no extreme price outliers, adequate quantities available, and multiple quotes are on file).
```

**Status of F-01:** **FIXED.**  
In Week 3, the model raised a false `[MISSING TERMS - CLARIFICATION REQUIRED]` alert on Q-103 (Crested Office Supplies) despite `delivery_terms` being present (*Same-day courier dispatch*). In this live re-test using the tightened `prompt_rag_v1.0.txt`, Q-103 contains no false alert (notes only state *"Payment terms: Cash on delivery"*), and Critical Alerts confirms that delivery terms are recognized as present for all three quotes without triggering unneeded clarification loops.
