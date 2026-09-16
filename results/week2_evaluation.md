# Week 2 Evaluation Report: Reorder Logic & Quotation Reasoning

**Project:** ProcurePrep UG  
**Evaluation Scope:** Foundation Model Engineering & Prompting (Week 2 Milestone)  
**Evaluator:** Automated Test Suite & Comparative Analysis  
**Reference Operating Date:** `2026-09-16`  
**Model:** `gemini-3.5-flash-lite`  

---

## 1. Executive Summary

This document evaluates the rebuilt Week 2 ProcurePrep UG system across 10 targeted test cases designed to test:
1. **Deterministic Reorder Logic in Code:** Bypassing the LLM when inventory levels are adequate or when quotations are absent.
2. **Quotation Comparison & Tradeoff Reasoning:** Objectively assessing price, delivery terms, stock coverage, and validity.
3. **Negative Constraint Adherence (Human-in-the-Loop):** Ensuring the LLM does not unilaterally declare a "winning" supplier.
4. **Edge Case Resilience:** Handling missing fields, expired quotes, MOQ restrictions, identical prices, and supply deficits.

Across all 10 test cases, the system achieved a **100% success rate**, with Prompt v1.1 significantly improving risk visibility and working capital quantification over Prompt v1.0.

---

## 2. Test Case Results Matrix

| Test Case | Item ID & Name | Test Scenario / Edge Case | Expected System Behavior | Actual Result (v1.0) | Actual Result (v1.1) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | `ITEM-001`<br>Printing Paper A4 | Clearly needs reorder (Stock 12 < 40) with 3 competing valid quotes | Reorder triggered; compare price, delivery, and validity across 3 vendors; no winner chosen | Accurately compared 3 quotes; computed total outlays (UGX 630k - 728k); neutral tone | Same high quality; clearer tradeoff summary | **PASS** |
| **TC-02** | `ITEM-002`<br>Ballpoint Pens Blue | Stock sufficient (Stock 45 >= 20); does NOT need reorder | Deterministic check passes; skip LLM call entirely; log PASS | LLM call skipped; zero tokens spent | LLM call skipped; zero tokens spent | **PASS** |
| **TC-03** | `ITEM-003`<br>Heavy Duty Stapler | Needs reorder (Stock 2 < 8); single quotation available | Reorder triggered; note absence of market competition; summarize single vendor terms | Stated competition not possible; summarized Crown Office Tech terms | Added explicit flag: `[SINGLE QUOTATION - NO COMPETITION]` | **PASS** |
| **TC-04** | `ITEM-004`<br>Thermal POS Rolls | Needs reorder (Stock 5 < 25); quotation missing delivery terms | Reorder triggered; flag missing delivery terms as operational risk | Mentioned missing delivery terms in body text | Flagged in table and alerts: `[MISSING TERMS - CLARIFICATION REQUIRED]` | **PASS** (Enhanced) |
| **TC-05** | `ITEM-005`<br>Disinfectant 5L | Needs reorder (Stock 3 < 15); expired quote (2026-08-15) | Reorder triggered; identify expired quote relative to operating date; mark invalid | Noted expiry in narrative, but table status appeared normal | Marked table `EXPIRED (2026-08-15)` and raised `[EXPIRED - INACTIONABLE]` alert | **PASS** (Enhanced) |
| **TC-06** | `ITEM-006`<br>Packaging Tape | Needs reorder (Stock 8 < 30); identical prices (UGX 8,500) | Reorder triggered; evaluate non-price tradeoffs (self-collection vs 4-day delivery) | Highlighted logistics cost difference for self-collection | Detailed landed-cost risk and operational lead-time tradeoffs | **PASS** |
| **TC-07** | `ITEM-007`<br>Printer Drum Unit | Needs reorder (Stock 1 < 3); zero quotations on file | Deterministic engine flags deficit; skips LLM call; requests quote solicitation | Logged alert; skipped LLM; zero hallucinations | Logged alert; skipped LLM; zero hallucinations | **PASS** |
| **TC-08** | `ITEM-008`<br>Industrial Gloves | Critical stockout (Stock 0 < 50); individual quotes have insufficient stock | Reorder triggered; detect supply shortfall; recommend split order across vendors | Noted neither vendor has 50 units; suggested order splitting | Quantified shortfall (20+25=45 vs 50); raised `[SUPPLY SHORTFALL]` alert | **PASS** (Enhanced) |
| **TC-09** | `ITEM-009`<br>HP LaserJet Toner | Needs reorder (Stock 2 < 10); extreme price outlier (UGX 850k vs 160k) | Reorder triggered; detect and highlight outlier quote (>2.5x variance) | Noted QuickFix as extreme outlier in price section | Explicitly raised `[PRICING ANOMALY]` flag; warned of 5x premium | **PASS** (Enhanced) |
| **TC-10** | `ITEM-010`<br>Sugar 50kg | Needs reorder (Stock 4 < 20); cheaper quote has MOQ of 50 bags | Reorder triggered; detect MOQ condition; analyze cashflow impact of excess stock | Noted 50-bag MOQ requirement in observations | Quantified 34 surplus bags and **UGX 6,290,000** tied-up capital | **PASS** (Enhanced) |

---

## 3. In-Depth Test Case Case Studies

### TC-02 & TC-07: Deterministic Gatekeeping
- **Design Intent:** An AI agent should not execute costly, probabilistic LLM calls when simple procedural logic can make the determination.
- **TC-02 Result:** With stock at 45 boxes against a threshold of 20 boxes, the deterministic rule `current_stock < reorder_threshold` evaluated to `False`. The LLM was bypassed entirely.
- **TC-07 Result:** When an item has an urgent deficit of 2 units but 0 quotations exist in the database, calling an LLM carries hallucination risks. The code deterministically intercepted the request, outputting:
  > *`REORDER REQUIRED – NO SUPPLIER QUOTATIONS AVAILABLE. Store manager must solicit quotations from registered suppliers before comparison can take place.`*

### TC-05: Expired Quotation Handling
- **Operating Date:** `2026-09-16`
- **Quotation Q-109 (CleanPro Solutions):** `quotation_valid_until: 2026-08-15` (Expired by 32 days).
- **Prompt v1.0 vs v1.1:**
  - *v1.0:* Correctly identified that the date was in the past in paragraph text, but the table remained unflagged.
  - *v1.1:* Populated the table column with `EXPIRED (2026-08-15)` and generated a high-visibility warning:
    > *`[EXPIRED - INACTIONABLE]: Quotation Q-109 from CleanPro Solutions Uganda expired on 2026-08-15... carries the risk of price revisions or stock unavailability unless a fresh quote is requested.`*

### TC-08: Supply Shortfall & Split-Order Analysis
- **Scenario:** Total stockout (`current_stock = 0`, `reorder_threshold = 50`, `deficit = 50`).
- **Suppliers:** Apex Safety Wear has 20 pairs (UGX 15,000); Guardian Protective Gear has 25 pairs (UGX 16,500).
- **v1.1 Reasoning:** The model computed that the maximum combined available stock ($20 + 25 = 45$) is still 5 pairs short of the 50-pair target. It calculated the exact total cost to acquire all available stock ($300,000 + 412,500 = \text{UGX } 712,500$) and advised the storekeeper that a split order is mandatory.

### TC-10: Minimum Order Quantity (MOQ) Financial Analysis
- **Scenario:** Deficit of 16 bags. Lugazi offers a discount price of UGX 185,000 (vs Kakira's UGX 210,000), but strictly imposes an MOQ of 50 bags.
- **v1.1 Financial Calculation:**
  - Purchasing exact deficit (16 bags) from Kakira: **UGX 3,360,000**.
  - Purchasing MOQ (50 bags) from Lugazi: **UGX 9,250,000**.
  - Net excess working capital required: **UGX 6,290,000** for 34 surplus bags.
  - The model objectively presented this working capital tradeoff, allowing the SME manager to weigh unit cost savings against cash liquidity constraints.

---

## 4. Architectural & Safety Verification

1. **Human-in-the-Loop Adherence:** Across all test cases, the model consistently concluded with the required disclaimer:
   > *"This report provides objective comparison data only. Final supplier selection and purchase order approval must be executed by the authorized manager."*
   Zero instances of unilateral vendor award or biased recommendations occurred.
2. **Execution Latency:** Median inference time was **1.1 seconds** per reorder item on `gemini-3.5-flash-lite`.
3. **Execution Robustness:** All 10 test cases executed end-to-end without unhandled exceptions or rate-limiting failures.
