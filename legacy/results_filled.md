# ProcurePrep – Test Results Log (Auto-generated)


**Model:** gemini-3.5-flash-lite  
**Prompt Version:** prompt_v1.txt  
**Checklist:** checklist.txt (8 items)  

---

## Results

### TC-01 – Fully complete submission
**File:** `submission_1.txt`  
**Expected Missing:** None – all 8 items present  

**Model Output:**
```
COMPLETENESS CHECK REPORT
==========================

PRESENT ITEMS:
- Company Registration Certificate
- Tax Clearance Certificate
- Bid Security (Tender Bond)
- Technical Proposal
- Financial Proposal (Itemised Price Schedule)
- Company Profile and Capability Statement
- Reference Letters (Minimum Two)
- Signed Cover Letter (Original Signature Required)

MISSING ITEMS:
- None – all items accounted for.

CANNOT DETERMINE:
- None.

REVIEWER NOTE:
This report flags completeness only. A human reviewer must make all
further decisions regarding this submission.

END OF REPORT
```

---

### TC-02 – Missing 1 item – Bid Security
**File:** `submission_2.txt`  
**Expected Missing:** Bid Security (Tender Bond)  

**Model Output:**
```
COMPLETENESS CHECK REPORT
==========================

PRESENT ITEMS:
- Company Registration Certificate
- Tax Clearance Certificate
- Technical Proposal
- Financial Proposal (Itemised Price Schedule)
- Company Profile and Capability Statement
- Reference Letters (Minimum Two)
- Signed Cover Letter (Original Signature Required)

MISSING ITEMS:
- Bid Security (Tender Bond)

CANNOT DETERMINE:
- None.

REVIEWER NOTE:
This report flags completeness only. A human reviewer must make all
further decisions regarding this submission.

END OF REPORT
```

---

### TC-03 – Missing 2 items
**File:** `submission_3.txt`  
**Expected Missing:** Reference Letters; Signed Cover Letter  

**Model Output:**
```
COMPLETENESS CHECK REPORT
==========================

PRESENT ITEMS:
- Company Registration Certificate
- Tax Clearance Certificate
- Bid Security (Tender Bond)
- Technical Proposal
- Financial Proposal (Itemised Price Schedule)
- Company Profile and Capability Statement

MISSING ITEMS:
- Reference Letters (Minimum Two)
- Signed Cover Letter (Original Signature Required)

CANNOT DETERMINE:
- None.

REVIEWER NOTE:
This report flags completeness only. A human reviewer must make all
further decisions regarding this submission.

END OF REPORT
```

---

### TC-04 – Mostly empty – only Financial Proposal present
**File:** `submission_4.txt`  
**Expected Missing:** 7 of 8 items missing (all except Financial Proposal)  

**Model Output:**
```
COMPLETENESS CHECK REPORT
==========================

PRESENT ITEMS:
- Financial Proposal (Itemised Price Schedule)

MISSING ITEMS:
- Company Registration Certificate
- Tax Clearance Certificate
- Bid Security (Tender Bond)
- Technical Proposal
- Company Profile and Capability Statement
- Reference Letters (Minimum Two)

CANNOT DETERMINE:
- Signed Cover Letter (Original Signature Required): The submission includes a signed closing statement from the proprietor, but it cannot be determined if this is on official company letterhead or formally addressed to the procuring entity.

REVIEWER NOTE:
This report flags completeness only. A human reviewer must make all
further decisions regarding this submission.

END OF REPORT
```

---

### TC-05 – Ambiguous / vague descriptions
**File:** `submission_5.txt`  
**Expected Missing:** CANNOT DETERMINE on most items  

**Model Output:**
```
COMPLETENESS CHECK REPORT
==========================

PRESENT ITEMS:
- Technical Proposal
- Company Profile and Capability Statement

MISSING ITEMS:
- Bid Security (Tender Bond) (Submission states the bank is prepared to provide documentation, but no bank guarantee or surety bond is included)
- Reference Letters (Minimum Two) (Submission offers past client contact details upon request instead of providing actual reference letters)
- Signed Cover Letter (Original Signature Required) (Submission lacks an official cover letter on company letterhead signed by an authorised representative)

CANNOT DETERMINE:
- Company Registration Certificate (Submission states registration papers are "available on request," making it unclear if the certificate is attached)
- Tax Clearance Certificate (Submission asserts tax compliance but does not explicitly confirm whether a valid Tax Clearance Certificate is included)
- Financial Proposal (Itemised Price Schedule) (Submission mentions "costs involved" within the proposal document, but does not clearly confirm an itemised price schedule with unit costs and quantities)

REVIEWER NOTE:
This report flags completeness only. A human reviewer must make all
further decisions regarding this submission.

END OF REPORT
```

---

### TC-06 – Expired documents
**File:** `submission_6.txt`  
**Expected Missing:** CANNOT DETERMINE – Tax Clearance & Bid Security expired  

**Model Output:**
```
COMPLETENESS CHECK REPORT
==========================

PRESENT ITEMS:
- Company Registration Certificate
- Tax Clearance Certificate
- Bid Security (Tender Bond)
- Technical Proposal
- Financial Proposal (Itemised Price Schedule)
- Company Profile and Capability Statement
- Reference Letters (Minimum Two)
- Signed Cover Letter (Original Signature Required)

MISSING ITEMS:
- None – all items accounted for.

CANNOT DETERMINE:
- None.

REVIEWER NOTE:
This report flags completeness only. A human reviewer must make all
further decisions regarding this submission.

END OF REPORT
```

---

### TC-07 – All docs present but wrong tender reference
**File:** `submission_7.txt`  
**Expected Missing:** All 8 present (wrong tender ref – completeness only)  

**Model Output:**
```
COMPLETENESS CHECK REPORT
==========================

PRESENT ITEMS:
- Company Registration Certificate
- Tax Clearance Certificate
- Bid Security (Tender Bond)
- Technical Proposal
- Financial Proposal (Itemised Price Schedule)
- Company Profile and Capability Statement
- Reference Letters (Minimum Two)
- Signed Cover Letter (Original Signature Required)

MISSING ITEMS:
- None – all items accounted for.

CANNOT DETERMINE:
- None.

REVIEWER NOTE:
This report flags completeness only. A human reviewer must make all
further decisions regarding this submission.

END OF REPORT
```

---

### TC-08 – Only one reference letter
**File:** `submission_8.txt`  
**Expected Missing:** Reference Letters (only 1 of 2 provided)  

**Model Output:**
```
COMPLETENESS CHECK REPORT
==========================

PRESENT ITEMS:
- Company Registration Certificate
- Tax Clearance Certificate
- Bid Security (Tender Bond)
- Technical Proposal
- Financial Proposal (Itemised Price Schedule)
- Company Profile and Capability Statement
- Signed Cover Letter (Original Signature Required)

MISSING ITEMS:
- Reference Letters (Minimum Two) (Only one reference letter was provided; the second required reference letter is missing)

CANNOT DETERMINE:
- None.

REVIEWER NOTE:
This report flags completeness only. A human reviewer must make all
further decisions regarding this submission.

END OF REPORT
```

---

### TC-09 – Cover letter present but unsigned
**File:** `submission_9.txt`  
**Expected Missing:** Signed Cover Letter (cover letter unsigned)  

**Model Output:**
```
COMPLETENESS CHECK REPORT
==========================

PRESENT ITEMS:
- Company Registration Certificate
- Tax Clearance Certificate
- Bid Security (Tender Bond)
- Technical Proposal
- Financial Proposal (Itemised Price Schedule)
- Company Profile and Capability Statement
- Reference Letters (Minimum Two)

MISSING ITEMS:
- Signed Cover Letter (Original Signature Required)

CANNOT DETERMINE:
- None.

REVIEWER NOTE:
This report flags completeness only. A human reviewer must make all
further decisions regarding this submission.

END OF REPORT
```

---

### TC-10 – Duplicate and conflicting documents
**File:** `submission_10.txt`  
**Expected Missing:** CANNOT DETERMINE – conflicting/duplicate documents  

**Model Output:**
```
COMPLETENESS CHECK REPORT
==========================

PRESENT ITEMS:
- Company Registration Certificate
- Tax Clearance Certificate
- Bid Security (Tender Bond)
- Technical Proposal
- Financial Proposal (Itemised Price Schedule)
- Company Profile and Capability Statement
- Reference Letters (Minimum Two)
- Signed Cover Letter (Original Signature Required)

MISSING ITEMS:
- None – all items accounted for.

CANNOT DETERMINE:
- None.

REVIEWER NOTE:
This report flags completeness only. A human reviewer must make all
further decisions regarding this submission.

END OF REPORT
```

---
