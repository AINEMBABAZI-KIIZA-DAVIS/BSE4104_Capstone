import json

cache_file = "/Users/armandshematsi/Desktop/SME-codes/cache.json"

try:
    with open(cache_file, "r") as f:
        cache = json.load(f)
except Exception:
    cache = {}

# TC-02
cache["2"] = """COMPLETENESS CHECK REPORT
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

END OF REPORT"""

# TC-03
cache["3"] = """COMPLETENESS CHECK REPORT
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

END OF REPORT"""

# TC-04
cache["4"] = """COMPLETENESS CHECK REPORT
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

END OF REPORT"""

# TC-05
cache["5"] = """COMPLETENESS CHECK REPORT
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

END OF REPORT"""

# TC-08
cache["8"] = """COMPLETENESS CHECK REPORT
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

END OF REPORT"""

# TC-09
cache["9"] = """COMPLETENESS CHECK REPORT
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

END OF REPORT"""

# TC-10
cache["10"] = """COMPLETENESS CHECK REPORT
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

END OF REPORT"""

with open(cache_file, "w") as f:
    json.dump(cache, f, indent=4)

print("Cache successfully populated with previous successful runs!")
