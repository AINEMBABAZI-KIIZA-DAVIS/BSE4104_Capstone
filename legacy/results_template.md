# ProcurePrep – Test Results Log

**Project:** ProcurePrep – Week 2 Baseline  
**Model:** gemini-1.5-flash  
**Prompt Version:** prompt_v1.txt  
**Checklist:** checklist.txt (8 items)

---

## How to Run Each Test

```bash
export GEMINI_API_KEY="your-key-here"
python main.py --checklist checklist.txt --submission submission_1.txt
```

Copy the model's printed output into the **Actual Result** column below.

---

## Results Table

| Test Case | Submission File | Expected Missing Items | Actual Result (paste model output) | Notes |
|-----------|----------------|------------------------|-------------------------------------|-------|
| TC-01 | submission_1.txt | None (all 8 present) | | Fully complete submission – model should report no missing items |
| TC-02 | submission_2.txt | Bid Security | | Missing 1 item – straightforward omission |
| TC-03 | submission_3.txt | Reference Letters; Signed Cover Letter | | Missing 2 items – both explicitly noted in the file |
| TC-04 | submission_4.txt | Company Registration Certificate; Tax Clearance Certificate; Bid Security; Technical Proposal; Company Profile; Reference Letters; Signed Cover Letter | | Only Financial Proposal present; 7 items missing |
| TC-05 | submission_5.txt | CANNOT DETERMINE for most items | | Ambiguous submission – vague descriptions, documents not physically attached |
| TC-06 | submission_6.txt *(add your own)* | *(define expected result)* | | |
| TC-07 | submission_7.txt *(add your own)* | *(define expected result)* | | |
| TC-08 | submission_8.txt *(add your own)* | *(define expected result)* | | |
| TC-09 | submission_9.txt *(add your own)* | *(define expected result)* | | |
| TC-10 | submission_10.txt *(add your own)* | *(define expected result)* | | |

---

## Observations & Issues

_Record any patterns, unexpected model behaviour, or prompt weaknesses here as you run the tests._

| Run | Observation |
|-----|-------------|
| | |

---

## Prompt Iteration Notes

_If you adjust prompt_v1.txt during testing, note what changed and why._

| Version | Change Made | Reason |
|---------|-------------|---------|
| v1 | Initial prompt | Baseline for Week 2 |
| | | |

---

> **Reminder:** This tool flags completeness only. All award decisions are made by a human reviewer.
