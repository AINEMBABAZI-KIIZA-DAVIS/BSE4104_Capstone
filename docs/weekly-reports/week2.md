# ProcurePrep  – Week 2 Progress Report

**Milestone:** Foundation Model Engineering & Prompting
**Author:** AI Agentic Development Team
**Date:** September 16, 2026
**Course / Project:** BSE4104 AI Agentic Capstone

---

## 1. Executive Summary: Scope Drift Correction

During Weeks 2 and 3, an unintended scope drift occurred: the ProcurePrep system was mistakenly developed as an external tender-submission completeness checker (evaluating public procurement bid submissions against standard checklists).

The official project Charter defines **ProcurePrep UG** as an **AI-Native SME Procurement-Preparation Agent**. Its core operational mission is to automate the internal purchasing preparation cycle for Ugandan Small and Medium Enterprises:

$$
\text{Inventory Tracking} \longrightarrow \text{Reorder Evaluation} \longrightarrow \text{Quotation Tradeoff Analysis} \longrightarrow \text{Requisition Drafting} \longrightarrow \text{Human Store Manager Approval}
$$

### Key Rebuild Decisions

1. **Preserve Legacy for Transparency:** Rather than deleting the previous tender checker code, all related files (`main.py`, `checklist.txt`, `submission_*.txt`, baseline results, and cache files) were moved into `legacy/` accompanied by `legacy/README.md`. This maintains working-tree transparency and auditability.
2. **Rebuild Week 2 Strictly to Charter:** Week 2 has been completely rebuilt from the ground up, focusing exclusively on:
   - Synthetic SME inventory and quotation datasets in CSV format.
   - Foundation model evaluation and selection (`gemini-3.5-flash-lite` / `gemini-3.6-flash`).
   - Deterministic procedural logic in Python for stock threshold evaluation.
   - Formal Prompt Specifications (v1.0 and v1.1) for objective quotation comparison.
   - A rigorous 10-case evaluation suite and version history log.

---

## 2. Technical Architecture of Rebuilt Week 2

```
                       +-------------------------+
                       |    data/inventory.csv   |
                       +------------+------------+
                                    |
                                    v
                     +-----------------------------+
                     |   Deterministic Gatekeeper  |
                     |  current_stock < threshold? |
                     +--------------+--------------+
                                    |
                    +---------------+---------------+
                    |                               |
              [No / Stock OK]                 [Yes / Deficit]
                    |                               |
                    v                               v
             +--------------+            +---------------------+
             |  Log [PASS]  |            | data/quotations.csv |
             | Skip API Call|            +----------+----------+
             +--------------+                       |
                                        +-----------+-----------+
                                        |                       |
                                   [0 Quotes]              [>= 1 Quotes]
                                        |                       |
                                        v                       v
                              +--------------------+  +-------------------+
                              | Deterministic Alert|  | Gemini Flash-Lite |
                              | "Solicit Quotes"   |  | (Prompt v1.0/v1.1)|
                              +--------------------+  +---------+---------+
                                                                |
                                                                v
                                                      +-------------------+
                                                      | Objective Report  |
                                                      |  (Human Review)   |
                                                      +-------------------+
```

### A. Data Layer (`data/`)

- **`inventory.csv`:** 20 realistic SME inventory items across office supplies, IT hardware, safety gear, cleaning chemicals, packaging, and raw materials (all units and thresholds calibrated for Ugandan SMEs).
- **`quotations.csv`:** Multi-supplier quotations containing unit prices in UGX, lead times, stock availability, quotation validity dates, and commercial notes.

### B. Procedural Engine (`main.py`)

- **Deterministic Math:** Reorder decisions are executed via pure Python code:
  $$
  \text{Needs Reorder} \iff \text{current\_stock} < \text{reorder\_threshold}
  $$

  This avoids probabilistic hallucinations and eliminates API costs on items with adequate stock.
- **Zero-Quote Handling:** Items needing reorder that lack supplier quotes are deterministically flagged, instructing the user to solicit quotes without invoking the LLM.

### C. Foundation Model & Prompt Specifications (`prompts/`)

- **Selected Model:** Google Gemini 3.5 Flash-Lite via `google-genai` SDK, offering sub-1.5s latency, reliable constraint following, and negligible operating costs (~$0.0002 per check).
- **Prompt Spec v1.0:** Established baseline quotation comparison table, price breakdown, and strict human-in-the-loop negative constraint (LLM cannot choose a winner).
- **Prompt Spec v1.1:** Enhanced with dedicated **Critical Alerts & Risk Observations**:
  - `[EXPIRED - INACTIONABLE]` flags for lapsed validity dates.
  - `[MISSING TERMS - CLARIFICATION REQUIRED]` for unspecified logistics terms.
  - `[SUPPLY SHORTFALL]` and split-order calculations when vendor stock is less than the deficit.
  - `[PRICING ANOMALY]` for prices exceeding 2.5x variance.
  - Working capital impact calculations for Minimum Order Quantity (MOQ) conditions.

---

## 3. Evaluation & Prompt Iteration Highlights

The system was evaluated against 10 comprehensive test cases (`results/week2_evaluation.md`):

1. **TC-01 (Standard Reorder):** Compared 3 valid quotes for Printing Paper (defict 28 reams), computing total outlays (UGX 630k - 728k) and lead-time tradeoffs.
2. **TC-02 (Sufficient Stock):** Correctly bypassed the LLM for Ballpoint Pens (stock 45 >= threshold 20), spending zero API tokens.
3. **TC-03 (Single Supplier):** Handled Heavy Duty Stapler with only 1 quotation on file, explicitly noting the lack of market competition.
4. **TC-04 (Missing Terms):** Flagged PointOfSale Uganda's missing delivery terms, highlighting transport cost risks.
5. **TC-05 (Expired Quote):** Identified CleanPro's quote expired on 2026-08-15 (relative to reference date 2026-09-16), flagging it as non-binding.
6. **TC-06 (Identical Prices):** Evaluated Packaging Tape where two vendors quote UGX 8,500, highlighting the difference between warehouse self-collection and included doorstep delivery.
7. **TC-07 (No Quotes):** Deterministically caught missing quotes for LaserJet Drum, instructing quote solicitation.
8. **TC-08 (Stockout & Supply Shortfall):** Handled a 50-pair glove stockout where suppliers only had 20 and 25 pairs, calculating the mandatory split order and remaining 5-pair shortfall.
9. **TC-09 (Price Outlier):** Flagged QuickFix Electronics' UGX 850,000 quote (>5x standard rate of UGX 160,000) as an emergency-stock outlier.
10. **TC-10 (MOQ vs Working Capital):** Quantified that Lugazi's 50-bag MOQ for sugar forces the purchase of 34 surplus bags, locking up **UGX 6,290,000** in excess capital.

---

## 4. What Changed from the Original Week 2 Attempt

| Dimension                    | Original Week 2 (Tender Checker)                 | Rebuilt Week 2 (SME Procurement Agent)                               |
| :--------------------------- | :----------------------------------------------- | :------------------------------------------------------------------- |
| **Domain Use Case**    | External vendor tender bid compliance checking   | Internal SME inventory replenishment & quotation analysis            |
| **Input Data**         | Free-text unstructured tender response documents | Structured tabular CSV files (`inventory.csv`, `quotations.csv`) |
| **Reorder Decision**   | Absent (Not an inventory system)                 | Deterministic code (`current_stock < reorder_threshold`)           |
| **Core LLM Task**      | Binary checklist presence/absence detection      | Tradeoff reasoning (Price vs Delivery vs Validity vs MOQ)            |
| **Human Role**         | Review checklist report                          | Final vendor selection and purchase order authorization              |
| **Economic Relevance** | Large public tender bids                         | Daily SME operational purchasing in Ugandan Shillings (UGX)          |

---

## 5. Next Steps: Roadmap to Week 3

With the Week 2 Foundation Model and Prompting layer solidly established, Week 3 will introduce:

1. **Retrieval-Augmented Generation (RAG):** Integrating Ugandan procurement guidelines (e.g. PPDA SME guidelines, preferred payment terms, and vendor evaluation criteria) from a vector store to ground quotation analysis.
2. **Requisition Drafting Agent:** Automatically generating structured purchase requisition drafts in JSON/PDF format once the human reviewer confirms vendor selection.
3. **Multi-Source Integration:** Adding support for automated quote ingestion from email and messaging channels.
