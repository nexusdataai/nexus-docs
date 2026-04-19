# Revenue Cycle Optimization

Claims denial prediction, coding accuracy improvement, prior authorization automation, and collections acceleration.

**Priority:** P1 — High Value  
**Time to Value:** 6-8 weeks  
**Category:** Revenue & Finance

---

## Business Problem

Healthcare revenue cycle management involves submitting millions of claims to hundreds of payers, each with different rules. The process is error-prone and financially material:

- **High denial rates** — 5-10% of claims are initially denied; reworking denials costs $25-50 per claim, and 60% of denied claims are never reworked
- **Coding errors** — inaccurate or suboptimal ICD-10/CPT coding leads to undercoding (lost revenue), overcoding (compliance risk), and claim rejections
- **Prior authorization delays** — manual prior auth processes delay patient care by 2-5 days and consume significant staff time
- **Slow collections** — average days in accounts receivable (A/R) exceeds 50 days for many health systems, tying up working capital
- **Charge capture leakage** — services rendered but never charged (missed charges) represent 1-3% of net revenue
- **Payer underpayment** — contract terms are complex; underpayments by payers go undetected without systematic variance analysis

---

## Capabilities

### Denial Prediction & Prevention
ML model predicting which claims are likely to be denied before submission, based on payer rules, coding patterns, clinical documentation, and historical denial reasons — enabling pre-submission correction.

### AI-Assisted Medical Coding
NLP extraction of diagnoses, procedures, and clinical context from physician notes to suggest optimal ICD-10 and CPT codes, improving coding accuracy, completeness, and compliance.

### Prior Authorization Automation
AI-powered determination of prior auth requirements per payer/procedure, automated submission of clinical documentation, and real-time status tracking to reduce delays and denials.

### Collections Prioritization
Score outstanding A/R accounts by collectability: payer-expected payment, patient financial capacity, aging bucket, and historical payment patterns — focusing effort where recovery probability is highest.

### Charge Capture Assurance
Compare clinical activity documented in the EHR (procedures performed, medications administered, supplies used) against charges posted in the billing system to identify missed charges.

---

## Data Sources & Ontology Mapping

| Ontology Entity | Source System | Key Fields |
|----------------|--------------|------------|
| Claims | Revenue Cycle / Billing | Claim ID, Patient, Payer, Diagnosis (ICD-10), Procedure (CPT), Charge, Status, Denial Reason |
| Clinical Documentation | EHR + Clinical Notes | Encounter, Provider Notes, Procedure Notes, Discharge Summary, H&P |
| Payer Contracts | Revenue Cycle | Payer, Plan, Fee Schedule, Reimbursement Terms, Prior Auth Rules, Timely Filing Limits |
| Patient Financial | RCM + EHR | Patient, Insurance, Coverage, Copay, Deductible Met, Financial Assistance Status |
| Charge Master | Revenue Cycle | CPT Code, Description, Standard Charge, Payer-Specific Rate, Revenue Code |

---

## AI Workflow

1. **Pre-Submission Scoring** — Before claim submission, evaluate each claim against: payer-specific denial rules, coding validation (DRG accuracy, modifier requirements), documentation sufficiency, and prior auth status
2. **Coding Assistance** — NLP analysis of clinical notes to extract diagnoses (ICD-10) and procedures (CPT) with confidence scores; flag discrepancies between documented clinical activity and coded claims; suggest code additions for under-documented encounters
3. **Denial Root Cause Analysis** — Cluster denied claims by payer, denial reason, service type, and provider to identify systematic denial patterns; generate targeted corrective action plans
4. **Prior Auth Engine** — For each scheduled procedure, automatically determine if prior auth is required (payer rule engine), compile supporting clinical documentation from EHR, and submit via payer portal or clearinghouse
5. **Collections Scoring** — Rank outstanding A/R by expected recovery: payer claims scored by payer payment history and denial status; patient balances scored by financial capacity, insurance, and payment history
6. **Charge Reconciliation** — Compare EHR-documented clinical activity (OR logs, medication administration records, procedure notes) against billing system charges to identify unbilled services
7. **Output** — Denial risk dashboard for billing team; coding suggestions in coder workflow; prior auth status tracker for scheduling; collections priority queue for A/R team; charge capture alerts for department managers

---

## Dashboard & Alerts

### Key Metrics

| KPI | Description | Target |
|-----|-------------|--------|
| **Clean Claim Rate** | % of claims accepted on first submission | > 95% (up from 85-90%) |
| **Denial Rate** | % of claims initially denied | < 4% (down from 8-10%) |
| **Days in A/R** | Average days from service to payment collection | < 38 days |
| **Coding Accuracy** | % of claims with correct primary diagnosis and procedures | > 97% |
| **Prior Auth Turnaround** | Average days from auth request to determination | < 2 days |
| **Net Collection Rate** | Collected revenue / Allowed revenue | > 97% |

### Alert Rules

| Alert | Trigger | Severity | Action |
|-------|---------|----------|--------|
| High denial risk | Claim scored >0.7 denial probability before submission | Critical | Route to coding specialist for review and correction before filing |
| Timely filing risk | Claim approaching payer's filing deadline (within 5 business days) | Critical | Prioritize for immediate submission; escalate if documentation incomplete |
| Coding discrepancy | NLP-extracted diagnoses differ significantly from coded diagnoses | High | Route to coding auditor; assess documentation sufficiency |
| Underpayment detected | Payer reimbursement <95% of contracted rate for claim | Medium | Queue for payer variance follow-up; compile contract evidence |
| Missed charge identified | Clinical activity documented in EHR with no matching billing charge | Medium | Alert department billing coordinator; generate charge capture ticket |

---

## ROI Model

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Denial rate | 8.5% | 3.8% | **55% reduction → $4.7M recovered revenue** (on $100M net revenue) |
| Days in A/R | 52 days | 36 days | **16-day improvement → $4.4M working capital freed** |
| Missed charges | 2.1% of net revenue | 0.6% | **71% reduction → $1.5M captured** |
| Coding staff productivity | 18 charts/coder/day | 28 charts/coder/day | **56% improvement → $1.8M labor savings** |
| Prior auth denial rate | 22% | 8% | **64% reduction → faster patient access** |

!!! success "Estimated Annual ROI"
    **$10M - $18M** annually from denial prevention, accelerated collections, charge capture, coding efficiency, and prior auth optimization — across a mid-size health system with $100M net patient revenue.

---

## Implementation Notes

- Denial prediction models need minimum 24 months of claims data with denial reason codes and final resolution outcomes
- Coding NLP requires access to full clinical documentation (progress notes, procedure notes, discharge summaries); de-identified training data recommended
- Prior auth rule engine must be maintained with current payer-specific requirements; payer portals may offer APIs for automated submission
- Payer contract terms must be digitized and loaded into the system for underpayment detection; manual contract review may be needed for legacy agreements
- All coding suggestions are advisory; final coding responsibility remains with certified coders per CMS and payer requirements

---

[← Back to Catalogue](index.md) | [Previous: Clinical Decision Support](clinical-decision-support.md) | [Next: Operational Efficiency →](operational-efficiency.md)
