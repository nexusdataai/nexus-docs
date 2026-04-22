# Policies

8 governance policies that constrain entity operations, workflow execution, and business rules across the healthcare ontology. Each policy is defined in `enterprise-knowledge/policies/` as a Markdown file.

---

## Policy Summary

| # | Policy | ID | Regulatory | Risk | Owner | Constrains |
|---|--------|----|-----------|------|-------|------------|
| 1 | [Clinical Safety Policy](#1-clinical-safety-policy) | POL-CLIN-001 | FHIR / TJC | Critical | CMO (Chief Medical Officer) | Medication_Order, Clinical_Order, Lab_Result, Drug_Interaction |
| 2 | [HIPAA Privacy & Security Policy](#2-hipaa-privacy--security-policy) | POL-HIPAA-001 | HIPAA | Critical | Privacy Officer / CISO | PHI_Access_Log, Patient_Consent, Patient_Master |
| 3 | [Revenue Cycle Policy](#3-revenue-cycle-policy) | POL-REV-001 | CMS / CPT | High | CFO / Revenue Cycle Director | Claim, Denial, Charge, Prior_Authorization |
| 4 | [Bed Management & Capacity Policy](#4-bed-management--capacity-policy) | POL-BED-001 | CMS CoP | High | COO / VP Operations | Bed_Census, OR_Schedule, ED_Arrival, Staffing |
| 5 | [Quality Measure Policy](#5-quality-measure-policy) | POL-QUAL-001 | CMS / TJC / HEDIS | High | CMO / Chief Quality Officer | Quality_Measure, Adverse_Event, Infection_Indicator, Safety_Assessment |
| 6 | [Pharmacy & Formulary Policy](#6-pharmacy--formulary-policy) | POL-PHARM-001 | FDA / P&T | High | Chief Pharmacy Officer | Medication_Order, Pharmacy_Inventory, Controlled_Substance_Log, Supply_Inventory |
| 7 | [Data Freshness Policy](#7-data-freshness-policy) | POL-DATA-001 | FHIR / Interop | Medium | CMIO / Chief Data Officer | All integration feeds |
| 8 | [Regulatory Reporting Policy](#8-regulatory-reporting-policy) | POL-REG-001 | CMS / State / TJC | High | Chief Compliance Officer | Regulatory_Return, Accreditation_Standard, Regulatory_Publication |

---

## 1. Clinical Safety Policy

**ID:** POL-CLIN-001 | **Regulatory:** FHIR / TJC | **Systems:** EHR, CPOE, LIS

| Rule Area | Key Rules |
|-----------|-----------|
| **Medication Safety** | High-severity drug interactions trigger interruptive hard stop; override requires attending physician justification documented in order |
| **Critical Lab Acknowledgment** | Critical lab result acknowledgment SLA: 15 min to ordering provider; 30 min escalation to covering physician and department head |
| **Sepsis Bundle Compliance** | Sepsis bundle compliance target >85%; non-compliance triggers real-time nursing and physician alert with escalation to charge nurse |
| **Clinical Pathway Adherence** | Clinical pathway adherence target >80%; variance documentation required for deviations; quarterly pathway review by clinical governance |
| **Duplicate Order Prevention** | Duplicate orders within active timeframe blocked with override requiring clinical justification; applies to labs, imaging, and medications |
| **Weight-Based Dosing** | Weight-based dosing verification mandatory for pediatric patients and renal-adjusted patients; dose outside calculated range requires pharmacist sign-off |

---

## 2. HIPAA Privacy & Security Policy

**ID:** POL-HIPAA-001 | **Regulatory:** HIPAA | **Systems:** EHR, IAM, Audit

| Rule Area | Key Rules |
|-----------|-----------|
| **Minimum Necessary Access** | Access to PHI restricted to minimum necessary for job function; role definitions reviewed semi-annually by Privacy Officer |
| **Role-Based PHI Access** | PHI access granted by role assignment; cross-department access requires supervisor approval; VIP/restricted patient records require explicit authorization |
| **Break-the-Glass Audit** | Break-the-glass override triggers immediate audit log entry; >3 uses by same user in 30 days triggers formal investigation by Privacy Officer |
| **Access Anomaly Detection** | Automated detection of unusual access patterns (after-hours, volume spikes, accessing records outside care team); anomalies flagged for review within 24 hours |
| **Breach Notification** | Breach notification within 60 days for incidents affecting >500 individuals; immediate notification to HHS and affected individuals per HIPAA Breach Notification Rule |
| **PHI Log Retention** | PHI access log retention: 6 years minimum; logs must be tamper-evident and available for audit within 48 hours of request |
| **De-Identification** | De-identification per Safe Harbor (18 identifiers removed) or Expert Determination method; re-identification risk assessment required for limited datasets |
| **Consent Management** | Consent management for research data sharing and HIE participation; patient opt-in/opt-out tracked; consent expiration and renewal enforced |

---

## 3. Revenue Cycle Policy

**ID:** POL-REV-001 | **Regulatory:** CMS / CPT | **Systems:** PAS, Billing, Claims

| Rule Area | Key Rules |
|-----------|-----------|
| **Clean Claim Rate** | Clean claim rate target >95%; claims failing front-end edits returned to coding within 24 hours; root cause analysis for rates below 90% |
| **Denial Rework SLA** | High-value denials (>$5K): rework within 48 hours; standard denials: rework within 5 business days; aging denials >30 days escalated to Revenue Cycle Director |
| **Timely Filing** | 100% compliance with payer-specific filing deadlines; automated alerts at 75% and 90% of deadline elapsed; missed deadlines tracked as revenue leakage |
| **Coding Accuracy** | Coding accuracy target >97%; quarterly audit of random sample (minimum 5% of encounters); discrepancies >3% trigger coder re-education |
| **Charge Capture** | Charge capture reconciliation within 3 business days of service date; missing charges identified by comparing scheduled procedures to posted charges |
| **Underpayment Follow-Up** | Underpayment follow-up initiated for variance >5% from contracted rate; appeals filed within payer-specific appeal window; trends reported monthly to CFO |
| **Prior Authorization** | Prior authorization submission within 24 hours of scheduling; status tracked through determination; expired auths flagged before service date |

---

## 4. Bed Management & Capacity Policy

**ID:** POL-BED-001 | **Regulatory:** CMS CoP | **Systems:** ADT, ED, OR Scheduling, Staffing

| Rule Area | Key Rules |
|-----------|-----------|
| **ED Boarding** | ED boarding maximum 4 hours; escalation to house supervisor at 2 hours; >4 hours triggers capacity alert to COO and activates surge discharge protocol |
| **Bed Occupancy** | Optimal bed occupancy range 82-88%; below 80%: review elective scheduling capacity; above 90%: activate pre-surge planning |
| **Surge Protocol** | Surge protocol activation at >95% predicted occupancy; includes discharge acceleration, elective case review, and regional transfer coordination |
| **OR Utilization** | OR utilization target >80% of allocated block time; unused block released at T-72 hours; chronic underutilization (<70% for 3 months) triggers block reallocation |
| **Discharge Timing** | Discharge before noon target >40%; barriers-to-discharge huddle daily at 10 AM; pending discharges visible on real-time capacity dashboard |
| **Staffing Ratios** | Staffing ratios per state mandate with acuity-based adjustment; understaffing triggers float pool activation then agency escalation |
| **Agency Nurse Cap** | Agency nurse hours capped at <5% of total nursing hours; exceeding cap for >2 consecutive pay periods triggers workforce planning review |

---

## 5. Quality Measure Policy

**ID:** POL-QUAL-001 | **Regulatory:** CMS / TJC / HEDIS | **Systems:** EHR, Infection Control, Quality

| Rule Area | Key Rules |
|-----------|-----------|
| **HAI Targets** | CLABSI <0.8 per 1,000 central line-days; CAUTI <1.0 per 1,000 catheter-days; SSI below NHSN benchmark; breaches trigger unit-level root cause analysis |
| **Fall Rate** | Fall rate target <2.5 per 1,000 patient-days; falls with injury trigger immediate safety huddle and 24-hour post-fall assessment |
| **Adverse Event Reporting** | Adverse event reporting within 24 hours for serious events; near-miss reporting encouraged (non-punitive); sentinel events reported to TJC within required timeframe |
| **Quality Measure Compliance** | Quality measure compliance >90% across CMS/TJC core measures; measures below 75th percentile benchmarked for focused improvement |
| **Antibiotic Stewardship** | Antibiotic stewardship compliance target >85%; 48-hour antibiotic timeout review mandatory; culture-directed de-escalation tracked |
| **Safety Assessment Frequency** | Fall risk assessment: every shift and on transfer; pressure injury risk assessment: every shift for high-risk patients; reassessment on clinical status change |

---

## 6. Pharmacy & Formulary Policy

**ID:** POL-PHARM-001 | **Regulatory:** FDA / P&T | **Systems:** EHR, Pharmacy, Inventory

| Rule Area | Key Rules |
|-----------|-----------|
| **Formulary Compliance** | Formulary compliance target >92%; non-formulary orders require clinical exception with P&T-approved criteria; compliance reported monthly |
| **Generic Substitution** | Generic substitution mandatory unless clinical exception documented by prescriber; brand-only exceptions reviewed quarterly by P&T committee |
| **Controlled Substance Waste** | Controlled substance waste requires dual-witness documentation; discrepancies investigated within 24 hours; patterns reported to Pharmacy Director and compliance |
| **Dispense Anomaly Detection** | Nurse dispense volume >3σ above unit average triggers automated investigation flag; patterns reviewed weekly by Chief Pharmacy Officer |
| **Expiry Waste** | Expiry waste target <1% of total inventory value; FEFO (first expiry, first out) dispensing enforced; monthly expiry report reviewed by Pharmacy Director |
| **Critical Med Stockout** | Stockout of critical medications: emergency procurement within 4 hours; therapeutic substitution protocol activated; clinical notification to affected units |
| **Formulary Changes** | All formulary additions, deletions, and restrictions require P&T committee approval; clinical evidence review and cost-effectiveness analysis mandatory |

---

## 7. Data Freshness Policy

**ID:** POL-DATA-001 | **Regulatory:** FHIR / Interop | **Systems:** All

### Clinical System SLAs

| Source | Data | SLA |
|--------|------|-----|
| EHR (Epic/Cerner) | Vitals, Orders, Results | Real-time via HL7/FHIR (<1 min) |
| Laboratory Information System | Lab_Result, Microbiology | <15 min from resulted status |
| Radiology (PACS/RIS) | Imaging results, Reports | <30 min from finalized report |
| Pharmacy System | Medication_Order, Dispense | Real-time (<1 min) |

### Operational & Financial System SLAs

| Source | Data | SLA |
|--------|------|-----|
| Revenue Cycle (Claims/Denials) | Claim, Denial, Charge | Daily sync (end of business day) |
| HIS (ADT/Bed Status) | Bed_Census, ED_Arrival | Real-time via ADT feeds |
| Population Health (Payer Claims) | Payer claims, Quality gaps | Monthly |
| Clinical NLP | Clinical notes, Dictation | <60 min from dictation completion |

### Staleness Rules

- 2× SLA gap: alert Data Engineering and system owner
- 3× SLA gap: mark data as stale; exclude from AI workflow inputs; notify clinical and operational stakeholders

---

## 8. Regulatory Reporting Policy

**ID:** POL-REG-001 | **Regulatory:** CMS / State / TJC | **Systems:** All

| Rule Area | Key Rules |
|-----------|-----------|
| **CMS Quality Reports** | CMS quality reports filed before deadline (100% on-time target); draft completion required 10 business days before due date for review |
| **Accreditation Readiness** | Accreditation readiness score maintained >95% at all times; mock survey conducted semi-annually; deficiencies remediated within 30 days |
| **Policy Review Cycle** | All policies reviewed annually at minimum; policies impacted by regulatory changes reviewed within 30 days of effective date |
| **Staff Training** | Regulatory and compliance training completion >98%; new hire training within 30 days of start; annual refresher tracked per employee |
| **Regulatory Change Assessment** | Regulatory change impact assessment completed within 14 days of publication; affected policies, workflows, and systems identified and remediation planned |
| **Consent Management** | Research consent renewal tracked with expiration alerts; re-consent required for protocol amendments; IRB approval status linked to consent records |
| **Audit Trail** | All reporting data must have complete audit trail from source system to reported number; lineage documentation required for all regulatory submissions |

---

[← Back to Ontology Overview](index.md)
