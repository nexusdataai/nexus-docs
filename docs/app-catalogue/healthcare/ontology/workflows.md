# Workflows

10 standards-aligned AI workflows that power the healthcare applications. Each workflow is defined in `enterprise-knowledge/workflows/` as a YAML file with trigger conditions, ordered steps, and entity/policy dependencies.

---

## Workflow Summary

| # | Workflow | Standard | Trigger | Primary App |
|---|---------|----------|---------|-------------|
| 1 | [Patient Matching & Profile Assembly](#1-patient-matching--profile-assembly) | FHIR: Patient | New patient registration or encounter | Patient 360 |
| 2 | [Care Gap Detection & Outreach](#2-care-gap-detection--outreach) | HEDIS/USPSTF | Monthly schedule or new clinical data update | Patient 360, Population Health |
| 3 | [Clinical Decision Support](#3-clinical-decision-support) | FHIR: MedicationRequest | New medication order or clinical order in CPOE | Clinical Decision Support |
| 4 | [Critical Result Management](#4-critical-result-management) | FHIR: Observation | Lab or imaging result with Critical_Flag = true | Clinical Decision Support |
| 5 | [Claim Denial Prediction & Prevention](#5-claim-denial-prediction--prevention) | CPT/ICD-10 | Pre-submission claim review or denial received | Revenue Cycle |
| 6 | [Bed Management & Patient Flow](#6-bed-management--patient-flow) | FHIR: Encounter/Location | Hourly schedule or ED boarding >2 hours | Operational Efficiency |
| 7 | [Population Risk Stratification](#7-population-risk-stratification) | HCC/HEDIS | Monthly schedule or new claims data load | Population Health |
| 8 | [HAI Surveillance & Quality Monitoring](#8-hai-surveillance--quality-monitoring) | CMS/TJC | Positive culture result or daily surveillance scan | Clinical Quality |
| 9 | [Supply Demand Forecasting](#9-supply-demand-forecasting) | Internal | Daily schedule or stockout risk detected | Supply Chain & Pharmacy |
| 10 | [Regulatory Reporting & HIPAA Monitoring](#10-regulatory-reporting--hipaa-monitoring) | HIPAA/CMS | Reporting deadline approach or PHI access anomaly | Regulatory Compliance |

---

## 1. Patient Matching & Profile Assembly

**ID:** `WORKFLOW_PATIENT_MATCHING_V1_0` | **FHIR: Patient** | **File:** `patient-matching.yaml`

**Trigger:** New patient registration or encounter across any connected EHR instance

| Step | System | Action |
|------|--------|--------|
| 1. Probabilistic Matching | Internal | Match across EHR instances using weighted probabilistic algorithm on MRN, Name, DOB, SSN, Address, Phone |
| 2. EMPI Resolution | Internal | Resolve matched identities into a single Enterprise Master Patient Index record; merge or link duplicates |
| 3. Profile Assembly | Internal | Aggregate clinical history, encounters, coverage, social determinants of health (SDoH) into unified patient profile |
| 4. Care Team Mapping | Internal | Identify and link active care team members: PCP, specialists, care coordinators, assigned nurses |
| 5. Dashboard Publish | Internal | Publish assembled Patient 360 profile to clinical dashboard; notify care team of new or updated record |

**Dependencies:** Patient, Encounter, Coverage, Condition, Observation, Practitioner, Organization, CareTeam, patient-matching-policy, data-freshness-policy

---

## 2. Care Gap Detection & Outreach

**ID:** `WORKFLOW_CARE_GAP_DETECTION_V1_0` | **HEDIS/USPSTF** | **File:** `care-gap-detection.yaml`

**Trigger:** Monthly (1st business day) OR new clinical data update (lab result, encounter close, or claims adjudication)

| Step | System | Action |
|------|--------|--------|
| 1. Guideline Application | Internal | Apply HEDIS, USPSTF, and ADA clinical guidelines against patient clinical record and claims history |
| 2. Gap Identification | Internal | Identify overdue screenings, labs, immunizations, and preventive services per guideline schedule |
| 3. Risk Prioritization | Internal | Prioritize gaps by clinical impact, patient risk score, and time since last completed measure |
| 4. Outreach List Generation | Internal | Generate outreach lists segmented by channel: patient portal, phone, mail, SMS |
| 5. Outreach Execution | Internal | Execute outreach via configured channels; create scheduling links for identified gaps |
| 6. Closure Tracking | Internal | Track gap closure rates; update patient record on completion; report measure compliance |

**Dependencies:** Patient, Condition, Observation, Immunization, Procedure, DiagnosticReport, Coverage, CareGap, care-gap-policy, outreach-policy

---

## 3. Clinical Decision Support

**ID:** `WORKFLOW_CLINICAL_DECISION_SUPPORT_V1_0` | **FHIR: MedicationRequest** | **File:** `clinical-decision-support.yaml`

**Trigger:** New medication order or clinical order entered in CPOE

| Step | System | Action |
|------|--------|--------|
| 1. Patient Context Assembly | Internal | Assemble current diagnoses, active medications, renal/hepatic function, allergies, weight, and age |
| 2. Drug Interaction Scoring | Internal | Score drug-drug and drug-condition interactions weighted by patient-specific factors (renal function, age, comorbidities) |
| 3. Alert Prioritization | Internal | Classify alerts by severity; suppress low-clinical-significance alerts to reduce fatigue; escalate critical interactions |
| 4. Pathway Matching | Internal | Match clinical scenario against evidence-based guidelines and institutional clinical pathways |
| 5. EHR Alert Output | EHR | Deliver prioritized alerts and recommendations inline within EHR ordering workflow; log clinician response |

**Dependencies:** Patient, MedicationRequest, Medication, AllergyIntolerance, Condition, Observation, Procedure, Practitioner, clinical-decision-support-policy, formulary-policy

---

## 4. Critical Result Management

**ID:** `WORKFLOW_CRITICAL_RESULT_V1_0` | **FHIR: Observation** | **File:** `critical-result-management.yaml`

**Trigger:** Lab_Result or Imaging_Result with Critical_Flag = true

| Step | System | Action |
|------|--------|--------|
| 1. Critical Result Detection | Internal | Detect observation result exceeding critical threshold per institutional critical value list |
| 2. Ordering Provider Identification | Internal | Identify ordering provider from the originating order; resolve covering provider if off-shift |
| 3. Auto-Page Provider | Internal | Send automated page/notification to ordering provider with result details and patient context |
| 4. Escalation Tier 1 | Internal | If unacknowledged within 15 minutes, escalate to covering physician via page and phone |
| 5. Escalation Tier 2 | Internal | If unacknowledged within 30 minutes, escalate to department chief and nursing supervisor |
| 6. Acknowledgment Logging | Internal | Log provider acknowledgment timestamp, action taken, and response time for compliance reporting |
| 7. Dashboard Update | Internal | Update critical result dashboard; flag overdue acknowledgments; generate shift-end compliance report |

**Dependencies:** Patient, Observation, DiagnosticReport, Practitioner, Encounter, CareTeam, critical-result-policy, escalation-policy

---

## 5. Claim Denial Prediction & Prevention

**ID:** `WORKFLOW_DENIAL_PREDICTION_V1_0` | **CPT/ICD-10** | **File:** `denial-prediction.yaml`

**Trigger:** Pre-submission claim review batch OR denial remittance received from payer

| Step | System | Action |
|------|--------|--------|
| 1. Claim Risk Scoring | Internal | Score each claim against payer-specific rules, historical coding patterns, and documentation completeness |
| 2. Pre-Submission Flagging | Internal | Flag high-risk claims for manual review before submission; route to coding specialists |
| 3. NLP Coding Assistance | Internal | Extract billable codes from clinical notes using NLP; suggest ICD-10/CPT corrections and additions |
| 4. Denial Root Cause Analysis | Internal | Classify denial reasons; identify systemic patterns by payer, department, provider, and code category |
| 5. Prior Authorization Engine | Internal | Identify services requiring prior auth; auto-initiate auth requests with supporting clinical documentation |
| 6. Collections Prioritization | Internal | Rank denied claims by recovery probability × dollar value; generate prioritized work queues for follow-up |

**Dependencies:** Patient, Claim, ExplanationOfBenefit, Encounter, Procedure, Condition, Coverage, Practitioner, Organization, billing-policy, payer-contract-policy

---

## 6. Bed Management & Patient Flow

**ID:** `WORKFLOW_BED_MANAGEMENT_V1_0` | **FHIR: Encounter/Location** | **File:** `bed-management.yaml`

**Trigger:** Hourly schedule OR ED boarding time exceeds 2 hours for any patient

| Step | System | Action |
|------|--------|--------|
| 1. Census Forecasting | Internal | Predict facility census at 24/48/72-hour horizons using admission patterns, surgical schedule, and seasonal trends |
| 2. LOS Prediction | Internal | Estimate remaining length of stay per inpatient using diagnosis, acuity, and care plan progress |
| 3. Discharge Barrier Detection | Internal | Identify barriers to discharge: pending results, incomplete orders, insurance authorization, post-acute placement |
| 4. Bed Assignment Optimization | Internal | Optimize bed assignments by unit, isolation requirements, acuity, and proximity to care team |
| 5. ED Boarding Management | Internal | Prioritize boarded ED patients for bed placement; trigger escalation protocols for boarding >4 hours |
| 6. Staffing Model Alignment | Internal | Align nurse staffing ratios to projected census; flag units exceeding target patient-to-nurse ratios |

**Dependencies:** Patient, Encounter, Location, Condition, Procedure, Practitioner, CareTeam, ServiceRequest, bed-management-policy, staffing-policy

---

## 7. Population Risk Stratification

**ID:** `WORKFLOW_POPULATION_RISK_V1_0` | **HCC/HEDIS** | **File:** `population-risk-stratification.yaml`

**Trigger:** Monthly (1st business day) OR new claims data load from payer

| Step | System | Action |
|------|--------|--------|
| 1. Population Roster Build | Internal | Build attributed patient roster from payer attribution files and PCP panel assignments |
| 2. HCC Risk Scoring | Internal | Calculate HCC risk scores; augment with AI model incorporating SDoH, utilization history, and clinical data |
| 3. Utilization Prediction | Internal | Predict 90-day ED visit and inpatient admission probability per patient using gradient-boosted model |
| 4. Intervention Matching | Internal | Match patients to intervention programs by risk tier: care management, chronic disease program, transitional care |
| 5. Contract Performance Tracking | Internal | Track quality and cost metrics against value-based contract benchmarks; project shared savings/losses |
| 6. Risk Panel Output | Internal | Publish risk-stratified panels to PCPs; generate actionable patient lists for care coordinators |

**Dependencies:** Patient, Condition, Claim, ExplanationOfBenefit, Encounter, Observation, Coverage, CareTeam, Practitioner, risk-stratification-policy, value-based-contract-policy

---

## 8. HAI Surveillance & Quality Monitoring

**ID:** `WORKFLOW_HAI_SURVEILLANCE_V1_0` | **CMS/TJC** | **File:** `hai-surveillance.yaml`

**Trigger:** Positive culture result OR daily surveillance scan (06:00 UTC)

| Step | System | Action |
|------|--------|--------|
| 1. Device Monitoring | Internal | Monitor patients with indwelling devices: central lines, urinary catheters, ventilators; track device-days |
| 2. Infection Indicator Tracking | Internal | Track infection indicators: positive cultures, fever, WBC trends, antibiotic escalation patterns |
| 3. HAI Classification | Internal | Classify suspected healthcare-associated infection by NHSN criteria: CLABSI, CAUTI, VAP, SSI |
| 4. Infection Prevention Alert | Internal | Alert infection prevention team with patient details, device history, and suspected HAI classification |
| 5. Quality Measure Extraction | Internal | Extract quality measures from EHR: core measures, eCQMs, patient safety indicators |
| 6. Adverse Event NLP Detection | Internal | NLP scan of clinical notes for unreported adverse events, near-misses, and safety concerns |
| 7. Safety Score Update | Internal | Update unit and facility safety scores; publish to quality dashboard; flag measures below benchmark |

**Dependencies:** Patient, Encounter, Observation, DiagnosticReport, Condition, Procedure, Device, Practitioner, Location, infection-control-policy, quality-reporting-policy

---

## 9. Supply Demand Forecasting

**ID:** `WORKFLOW_SUPPLY_DEMAND_FORECAST_V1_0` | **Internal** | **File:** `supply-demand-forecasting.yaml`

**Trigger:** Daily schedule (05:00 UTC) OR stockout risk detected for any critical item

| Step | System | Action |
|------|--------|--------|
| 1. Consumption Prediction | Internal | Predict department-level consumption from surgical schedule, census forecast, and historical usage patterns |
| 2. Replenishment Optimization | Internal | Calculate optimal reorder points and quantities with FIFO batch selection; generate purchase requisitions |
| 3. Formulary Analysis | Internal | Analyze formulary utilization; identify therapeutic substitution opportunities and cost-saving alternatives |
| 4. Expiry Tracking | Internal | Track lot expiration dates; trigger redistribution to high-consumption locations before expiry |
| 5. Diversion Detection | Internal | Monitor controlled substance dispensing patterns; flag anomalies indicating potential diversion |
| 6. Supply Dashboard Output | Internal | Publish supply dashboard with stockout risks, consumption trends, cost analytics, and diversion alerts |

**Dependencies:** Patient, Encounter, Procedure, Location, Device, SupplyDelivery, MedicationRequest, Medication, supply-chain-policy, formulary-policy, controlled-substance-policy

---

## 10. Regulatory Reporting & HIPAA Monitoring

**ID:** `WORKFLOW_REGULATORY_REPORTING_V1_0` | **HIPAA/CMS** | **File:** `regulatory-reporting.yaml`

**Trigger:** Reporting deadline 10 business days away OR PHI access anomaly detected

| Step | System | Action |
|------|--------|--------|
| 1. PHI Access Analysis | Internal | Analyze PHI access patterns; detect anomalies: break-the-glass overuse, after-hours access, bulk record access |
| 2. Quality Reporting Extraction | Internal | Extract and validate quality reporting data: CMS Star ratings, HEDIS measures, eCQMs, MIPS scores |
| 3. Accreditation Monitoring | Internal | Monitor compliance against accreditation standards: TJC, NCQA, CMS Conditions of Participation |
| 4. Consent Tracking | Internal | Track patient consent status for treatment, research, and data sharing; flag expired or missing consents |
| 5. Regulatory Change Scan | Internal | NLP scan of regulatory publications (CMS, OIG, OCR) for changes impacting current compliance posture |
| 6. Compliance Dashboard Output | Internal | Publish compliance dashboards; generate submission-ready regulatory reports; flag non-compliance risks |

**Dependencies:** Patient, Encounter, Consent, AuditEvent, Observation, Condition, Procedure, Coverage, Organization, Practitioner, hipaa-policy, quality-reporting-policy, accreditation-policy

---

[← Back to Ontology Overview](index.md)
