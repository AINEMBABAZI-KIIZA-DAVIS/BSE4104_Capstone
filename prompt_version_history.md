# Prompt Version History

## v1.0
- **Status:** Initial version
- **Details:** Established the baseline role of ProcurePrep, the core task, the strict constraints (do not score, rank, or assume), and defined the standard output format.

## v1.1
- **Date:** 2026-09-09
- **Changes:** Added a strict document validity rule regarding expiry dates, internal consistency, and duplicate/conflicting documents.
- **Reason:** Triggered by failures in test cases **TC-06 (Expired documents)** and **TC-10 (Duplicate and conflicting documents)**, where the v1.0 prompt marked expired and conflicting documents as present.
