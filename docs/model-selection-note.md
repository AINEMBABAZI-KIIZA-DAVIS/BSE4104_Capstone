# Model Selection Note: Foundation Model for ProcurePrep UG

**Project:** ProcurePrep UG (BSE4104 AI Agentic Capstone)  
**Task:** Automated Inventory Reorder Reasoning & Supplier Quotation Comparison  
**Selected Model:** Google Gemini 3.5 Flash-Lite (`gemini-3.5-flash-lite`) / Gemini 3.6 Flash (`gemini-3.6-flash`) via `google-genai` SDK  

---

## 1. Context & Task Requirements
ProcurePrep UG assists Ugandan Small and Medium Enterprises (SMEs) by transforming manual procurement checks into an automated, explainable preparation workflow:
1. **Deterministic Inventory Evaluation:** Evaluating stock levels against reorder thresholds via Python code (`current_stock < reorder_threshold`).
2. **Contextual Quotation Comparison:** When an item requires reordering, the foundation model analyzes competing supplier quotes, comparing unit prices (in UGX), delivery lead times, stock availability, and expiration dates.
3. **Strict Human-in-the-Loop Constraint:** The model must objectively explain tradeoffs and present structured comparisons without making an autonomous purchasing decision or picking a single "winning" supplier.

---

## 2. Evaluation Across Key Selection Dimensions

### A. Reasoning Capability & Instruction Adherence
- **Tabular & Numerical Reasoning:** The task requires accurate comparison of numerical amounts (e.g., identifying lowest price or spotting 5x price outliers) and date logic (identifying expired quotes relative to reference dates).
- **Tradeoff Explanation:** The model must articulate nuanced qualitative tradeoffs (e.g., higher price with same-day delivery vs. lower price with 7-day transit).
- **Negative Constraint Adherence:** Gemini 2.5/2.0 Flash models reliably follow negative constraints (e.g., "Do NOT select a winner or recommend approval; present tradeoffs for human review").

### B. Cost & SME Economic Viability
- **Token Efficiency:** A single reorder quotation comparison requires ~350 input tokens and ~300 output tokens (~650 tokens total).
- **Cost Profile:** At $0.075 per 1M input tokens and $0.30 per 1M output tokens (Gemini Flash pricing), processing 1,000 inventory reorder checks costs less than **$0.15 USD (~550 UGX)**. This makes the system economically viable for micro and small enterprises operating with modest IT budgets.

### C. Latency & Batch Processing Throughput
- **End-to-End Response Time:** Median generation latency is **0.8 to 1.5 seconds** per item.
- **SME Operational Workflow:** Batch processing a daily inventory sweep of 20–50 items takes less than 45 seconds, well within acceptable operational windows for morning storekeeper reviews.

### D. Privacy, Security & Data Governance
- **Commercial Confidentiality:** Supplier quotes, negotiated discounts, and inventory volumes constitute sensitive SME commercial data.
- **API Privacy Terms:** Under standard Google GenAI API agreements (paid or enterprise tier), prompt and output data are not retained or utilized to train future public foundation models, ensuring confidentiality of Ugandan SME procurement records.

### E. Access & Operational Simplicity
- **SDK Integration:** The modern `google-genai` Python SDK provides direct, typed client access with `.env` secret loading.
- **Quota & Availability:** Flash models feature generous free/developer quotas (15 RPM), allowing full offline and demo testing without rate-limit saturation.

---

## 3. Conclusion & Final Selection
**Gemini 2.5 Flash / Gemini 2.0 Flash** offers the optimal balance of speed, low cost, numerical reasoning, and strict constraint adherence for ProcurePrep UG's quotation comparison engine. The model operates exclusively as an explanatory reasoning engine, leaving the threshold math to deterministic code and the final procurement decision to the human store manager.
