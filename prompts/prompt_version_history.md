# Prompt Version History: ProcurePrep UG (Rebuilt Week 2)

## Overview
This document logs the evolution of the prompt specifications for the ProcurePrep UG SME Procurement Preparation Agent. The system was rebuilt in Week 2 to realign with the project charter: transitioning from an external tender compliance checker to an internal SME inventory reorder and quotation comparison assistant.

---

## Evolution Summary Matrix

| Version | Date | Target Model | Key Capabilities Added | Test Case Triggers & Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **v1.0** | 2026-09-16 | `gemini-3.5-flash-lite` | Baseline quotation comparison, table generation, unit price tradeoff, human-in-the-loop negative constraint (no winner selection). | Initial implementation for the corrected SME procurement charter. |
| **v1.1** | 2026-09-16 | `gemini-3.5-flash-lite` | Dedicated `Critical Alerts & Risk Observations` section; mandatory flags for `[EXPIRED - INACTIONABLE]`, `[MISSING TERMS]`, `[PRICING ANOMALY]`, `[SUPPLY SHORTFALL]`, and working capital calculations for MOQ restrictions. | Prompt v1.0 passed basic comparisons but lacked prominent operational and financial warning flags for edge cases in TC-04, TC-05, TC-08, TC-09, and TC-10. |

---

## Detailed Version Notes

### Prompt v1.0 (Baseline SME Comparison Engine)
- **Status:** Initial Corrected Baseline
- **Specification Document:** `prompts/prompt_spec_v1.0.md`
- **File:** `prompts/prompt_v1.0.txt`
- **Architecture:** 
  - Works downstream of deterministic code evaluation (`current_stock < reorder_threshold`).
  - Formats stock level, threshold, replenishment deficit, and supplier quotation table into markdown prompt context.
  - Instructs model to produce:
    1. Quotation Summary Table
    2. Key Differences & Tradeoffs (Price, Delivery, Validity)
    3. Observations & Noted Conditions
    4. Reviewer Next Steps (strict non-autonomous constraint)
- **Findings from 10 Test Cases:**
  - *Strengths:* Successfully followed the negative constraint (never picked a winner or declared an award). Accurately calculated total costs for deficits.
  - *Weaknesses identified:*
    - **TC-04 (Missing delivery terms):** Noted missing terms casually in text rather than raising a prominent operational risk flag.
    - **TC-05 (Expired quotation):** Noted the expired date in the narrative, but left the table status looking normal, creating a risk that a busy storekeeper might miss the expiry.
    - **TC-08 (Stockout & supply shortfall):** Correctly noted supplier stock limits, but did not formalize split-order recommendations.
    - **TC-09 (Price outlier):** Described the 5x price difference as an outlier, but did not formally flag potential price gouging or emergency premium pricing.
    - **TC-10 (MOQ restriction):** Mentioned the MOQ, but did not calculate the financial burden of excess capital tied up in surplus inventory.

---

### Prompt v1.1 (Risk-Aware SME Procurement Engine)
- **Status:** Current Production Release (Week 2 Milestone)
- **Specification Document:** `prompts/prompt_spec_v1.1.md`
- **File:** `prompts/prompt_v1.1.txt`
- **Key Refinements & Behavioral Changes:**
  1. **Validity Status Table Formatting:**
     - Prompt mandates populating the `Validity Status` column with `EXPIRED (YYYY-MM-DD)` and `[EXPIRED - INACTIONABLE]` tag if `valid_until < reference_date`.
     - *Result in TC-05:* Prominently warns reviewer that CleanPro's quote expired on 2026-08-15 and is legally non-binding.
  2. **Missing Information Flagging:**
     - Mandates explicit label `[MISSING TERMS - CLARIFICATION REQUIRED]` for absent lead times or logistics terms.
     - *Result in TC-04:* Highlights transport responsibility uncertainty and risks of hidden delivery costs.
  3. **Supply Shortfall & Order Splitting:**
     - Mandates explicit calculation of supplier stock shortfalls against the deficit.
     - *Result in TC-08:* Proactively calculates that Apex (20 pairs) + Guardian (25 pairs) = 45 pairs, requiring an order split across both vendors and still leaving a 5-pair deficit.
  4. **Pricing Anomaly Detection:**
     - Added rule to flag quotations exceeding 2.5x variance from other quotes as `[PRICING ANOMALY]`.
     - *Result in TC-09:* Immediately highlights QuickFix Electronics (UGX 850,000 vs UGX 160,000) as an extreme emergency-stock outlier.
  5. **Working Capital & MOQ Impact:**
     - Added rule requiring calculation of surplus units and excess capital when MOQ exceeds item deficit.
     - *Result in TC-10:* Quantified that Lugazi's 50-bag MOQ forces the purchase of 34 surplus bags, locking up **UGX 6,290,000** in excess capital.
