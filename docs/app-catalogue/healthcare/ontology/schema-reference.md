# Schema Reference

Complete reference for the healthcare semantic schema — 12 domains, ~50 tables across 6 source systems, aligned to HL7 FHIR, ICD-10, CPT/HCPCS, SNOMED CT, LOINC, NDC, RxNorm, and HIPAA standards.

**Source File:** `enterprise-knowledge/healthcare-schema.yaml`

---

## Domain 1: Patient & Demographics

**System:** EHR | **FHIR Resource:** Patient

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Patient_Master` | Central patient master record — most connected entity in the ontology | high | MRN, Name, DOB, Gender, Race, Ethnicity, Language, Address, Phone, Insurance_ID, PCP_ID, Consent_Status, Status (Active/Inactive/Deceased/Merged) |
| `Emergency_Contact` | Patient emergency contact persons | low | Contact_ID, Patient_ID, Name, Relationship, Phone, Priority |
| `Patient_Identifier` | MRN cross-references across systems for EMPI resolution | medium | Identifier_ID, Patient_ID, MRN, Source_System (EHR/Billing/Lab/Imaging/Pharmacy), Identifier_Type (MRN/SSN/Insurance/Enterprise), Status (Active/Merged/Retired) |

**Key Relationships:**

- `Patient_Master` is referenced by ALL 8 applications (most foundational entity)
- `Patient_Master` --syncs_to--> `Population_Roster` (via ehr-population-health-sync)
- `Patient_Master` --constrained_by--> hipaa-privacy-policy
- `Patient_Identifier` --triggers--> Patient Identity Resolution workflow (EMPI matching)
- `Patient_Master` --triggers--> Patient 360 Assembly workflow

---

## Domain 2: Clinical Records

**System:** EHR | **FHIR Resource:** Condition | **Coding:** ICD-10-CM / SNOMED CT

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Diagnosis` | Clinical diagnosis record with standardized coding | high | Diagnosis_ID, Patient_ID, Encounter_ID, ICD10_Code, SNOMED_Code, Description, Type (Admitting/Principal/Secondary), Status (Active/Resolved/Chronic), Onset_Date, Diagnosed_By |
| `Problem_List` | Longitudinal chronic condition tracking | medium | Problem_ID, Patient_ID, Diagnosis_ID, ICD10_Code, SNOMED_Code, Description, Status (Active/Inactive/Resolved), Onset_Date, Last_Reviewed |
| `Allergy` | Patient allergy and adverse reaction record | high | Allergy_ID, Patient_ID, Allergen, SNOMED_Code, Reaction, Severity (Mild/Moderate/Severe/Life_Threatening), Status (Active/Inactive/Entered_in_Error), Verified_By |

**Key Relationships:**

- `Diagnosis` --syncs_to--> `Claim` (via ehr-rcm-billing-sync)
- `Diagnosis` --triggers--> Clinical Decision Support workflow (new diagnosis detection)
- `Diagnosis` --constrained_by--> clinical-documentation-policy
- `Problem_List` --depends_on--> `Diagnosis`
- `Allergy` --triggers--> Medication Safety Alerting workflow (interaction check)

---

## Domain 3: Medications & Pharmacy

**System:** EHR + Pharmacy | **FHIR Resource:** MedicationRequest / MedicationAdministration | **Coding:** NDC / RxNorm

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Medication_Order` | Physician medication prescription / CPOE order | high | Order_ID, Patient_ID, Encounter_ID, Drug_Name, NDC, RxNorm_CUI, Dose, Route, Frequency, Start_Date, End_Date, Prescriber_ID, Indication, Status (Active/Completed/Discontinued/Cancelled) |
| `Medication_Administration` | Bedside MAR record of drug administration | high | Admin_ID, Order_ID, Patient_ID, Drug_Name, Dose_Given, Route, Time, Nurse_ID, Site, Status (Given/Held/Refused/Not_Given) |
| `Drug_Interaction` | Drug-drug and drug-allergy interaction knowledge base | medium | Interaction_ID, Drug_A_RxNorm, Drug_B_RxNorm, Severity (Minor/Moderate/Major/Contraindicated), Effect, Evidence_Level, Source |
| `Pharmacy_Inventory` | Pharmacy stock and formulary management | medium | Inventory_ID, NDC, Drug_Name, Lot, Qty, Expiry, Location, Formulary_Status (Formulary/Non_Formulary/Restricted), Cost, Controlled_Flag, DEA_Schedule |

**Key Relationships:**

- `Medication_Order` --triggers--> Medication Safety Alerting workflow (interaction/allergy check)
- `Medication_Order` --constrained_by--> clinical-safety-policy, controlled-substance-policy
- `Medication_Administration` --depends_on--> `Medication_Order`
- `Medication_Administration` --validates--> `Medication_Order` (five-rights verification)
- `Pharmacy_Inventory` --triggers--> Supply Replenishment workflow (below par level)

---

## Domain 4: Lab & Diagnostics

**System:** LIS + Imaging/PACS | **FHIR Resource:** Observation / DiagnosticReport | **Coding:** LOINC

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Lab_Order` | Physician order for laboratory test | medium | Order_ID, Patient_ID, Encounter_ID, LOINC_Code, Test_Name, Ordering_Provider, Priority (Routine/Urgent/STAT), Specimen_Type, Status (Ordered/Collected/In_Process/Resulted/Cancelled) |
| `Lab_Result` | Laboratory test result with standardized coding | high | Result_ID, Order_ID, Patient_ID, LOINC_Code, Test_Name, Value, Unit, Reference_Range, Critical_Flag, Status (Preliminary/Final/Corrected/Cancelled), Resulted_Date |
| `Imaging_Order` | Physician order for diagnostic imaging | medium | Order_ID, Patient_ID, Encounter_ID, Modality (XRAY/CT/MRI/US/PET/Fluoroscopy), Body_Part, Ordering_Provider, Priority (Routine/Urgent/STAT), Clinical_Indication, Status (Ordered/Scheduled/Completed/Cancelled) |
| `Imaging_Result` | Radiology report and findings | high | Result_ID, Order_ID, Patient_ID, Modality (XRAY/CT/MRI/US/PET), Findings_Text, Impression, Critical_Flag, Radiologist_ID, Report_Date, Status (Preliminary/Final/Addended) |

**Key Relationships:**

- `Lab_Result` --triggers--> Critical Result Management workflow (Critical_Flag = true)
- `Lab_Result` --validates--> `Diagnosis` (clinical confirmation)
- `Lab_Result` --depends_on--> `Lab_Order`
- `Imaging_Result` --triggers--> Critical Result Management workflow (Critical_Flag = true)
- `Imaging_Result` --depends_on--> `Imaging_Order`

---

## Domain 5: Clinical Orders & Guidelines

**System:** EHR CPOE | **FHIR Resource:** ServiceRequest

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Clinical_Order` | Unified clinical order across order types | medium | Order_ID, Patient_ID, Encounter_ID, Order_Type (Lab/Imaging/Procedure/Consult/Diet/Therapy), Priority (Routine/Urgent/STAT), Ordering_Provider, Indication, Status (Ordered/In_Progress/Completed/Cancelled) |
| `Clinical_Guideline` | Evidence-based clinical protocol knowledge base | low | Guideline_ID, Condition, Source (UpToDate/NCCN/ADA/ACC/AHA/IDSA), Recommendation, Evidence_Level (A/B/C/D), Last_Reviewed |
| `Early_Warning_Score` | Patient deterioration risk scoring (MEWS/NEWS) | medium | Score_ID, Patient_ID, Encounter_ID, Score_Type (MEWS/NEWS/NEWS2), Vital_Signs_Used, Score, Alert_Level (Low/Medium/High/Critical), Timestamp |

**Key Relationships:**

- `Clinical_Order` --triggers--> Order Fulfillment workflow (routing to Lab/Imaging/Pharmacy)
- `Clinical_Order` --constrained_by--> clinical-documentation-policy
- `Clinical_Guideline` --validates--> `Clinical_Order` (order appropriateness)
- `Early_Warning_Score` --triggers--> Rapid Response workflow (High/Critical alert)
- `Early_Warning_Score` --depends_on--> `Encounter` (inpatient context)

---

## Domain 6: Encounters & Visits

**System:** EHR + HIS | **FHIR Resource:** Encounter

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Encounter` | Patient visit or admission episode — second most connected entity | high | Encounter_ID, Patient_ID, Type (Inpatient/Outpatient/ED/Observation/Telehealth), Admission_Date, Discharge_Date, LOS_Days, Facility, Unit, Attending_ID, Disposition (Home/SNF/Rehab/AMA/Expired), DRG, Status (Pre_Admit/Active/Discharged/Cancelled) |
| `Admission` | Inpatient admission detail record | high | Admission_ID, Encounter_ID, Patient_ID, Admit_Date, Admit_Source (ED/Direct/Transfer/Newborn), Admit_Type (Emergency/Urgent/Elective), Attending_ID, Service_Line, Expected_LOS |
| `Transfer` | Unit-to-unit patient movement within a visit | medium | Transfer_ID, Encounter_ID, Patient_ID, From_Unit, To_Unit, Transfer_Time, Reason, Ordering_Provider |
| `Discharge` | Discharge planning and execution record | high | Discharge_ID, Encounter_ID, Patient_ID, Discharge_Date, Disposition (Home/Home_Health/SNF/Rehab/LTAC/AMA/Expired), Discharge_Instructions, Follow_Up_Appointments, Medication_Reconciliation_Status (Pending/Complete) |

**Key Relationships:**

- `Encounter` --syncs_to--> `Claim` (via ehr-rcm-billing-sync)
- `Encounter` --triggers--> Length of Stay Prediction workflow (on admission)
- `Encounter` --constrained_by--> patient-flow-policy
- `Admission` --depends_on--> `Encounter`
- `Discharge` --triggers--> Readmission Risk Prediction workflow

---

## Domain 7: Revenue & Billing

**System:** Revenue Cycle | **FHIR Resource:** Claim / ExplanationOfBenefit | **Coding:** CPT / HCPCS / DRG

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Claim` | Insurance claim for services rendered | high | Claim_ID, Patient_ID, Encounter_ID, Payer_ID, Type (Professional/Institutional), Diagnosis_Codes, Procedure_Codes_CPT, Total_Charge, Allowed_Amount, Status (Submitted/Accepted/Denied/Paid/Appealed) |
| `Charge` | Individual charge line item within an encounter | medium | Charge_ID, Encounter_ID, CPT_Code, HCPCS_Code, Description, Qty, Unit_Price, Total_Amount, Department, Service_Date |
| `Denial` | Claim denial tracking and rework | high | Denial_ID, Claim_ID, Denial_Code, Reason, Amount, Rework_Status (Open/In_Review/Appealed/Overturned/Written_Off), Appeal_Deadline |
| `Payer_Contract` | Insurance payer fee schedules and terms | high | Contract_ID, Payer_ID, Payer_Name, Fee_Schedule_Type, Reimbursement_Terms, Prior_Auth_Rules, Timely_Filing_Limit_Days, Effective_Date, Expiry_Date |
| `Prior_Authorization` | Pre-service authorization from payer | medium | Auth_ID, Patient_ID, Payer_ID, Service_Requested, CPT_Code, Status (Requested/Approved/Denied/Expired), Approved_Units, Valid_From, Valid_To |
| `Patient_Financial` | Patient financial responsibility tracking | medium | Record_ID, Patient_ID, Encounter_ID, Copay, Deductible, Coinsurance, Out_of_Pocket_Max, Financial_Assistance_Status (None/Applied/Approved/Charity_Care), Collection_Status |

**Key Relationships:**

- `Claim` --triggers--> Denial Prevention workflow (pre-submission validation)
- `Claim` --depends_on--> `Encounter`, `Diagnosis`, `Charge`
- `Claim` --constrained_by--> revenue-cycle-policy (timely filing, clean claim rules)
- `Denial` --triggers--> Denial Management workflow (rework prioritization)
- `Payer_Contract` --constrained_by--> revenue-cycle-policy

---

## Domain 8: Hospital Operations

**System:** HIS | **FHIR Resource:** Location / Schedule

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Bed_Census` | Real-time bed status and patient assignment | high | Census_ID, Unit, Bed_ID, Patient_ID, Status (Occupied/Clean/Dirty/Blocked/Reserved), Expected_Discharge, Isolation_Flag, Acuity_Level |
| `OR_Schedule` | Operating room scheduling and utilization | high | Case_ID, Encounter_ID, Surgeon_ID, Procedure, Room, Scheduled_Start, Estimated_Duration, Actual_Duration, Status (Scheduled/In_Progress/Completed/Cancelled/Delayed), Anesthesia_Type |
| `ED_Arrival` | Emergency department arrival and triage record | high | Arrival_ID, Patient_ID, Arrival_Time, Acuity_ESI (1/2/3/4/5), Chief_Complaint, Triage_Nurse_ID, Disposition (Admit/Discharge/Transfer/LWBS/AMA), Boarding_Time, Door_to_Provider_Min |
| `Staffing` | Unit staffing levels and labor tracking | medium | Staffing_ID, Unit, Shift (Day/Evening/Night), Staff_Type (RN/LPN/CNA/RT/PharmD), Hours, FTE_Count, Patient_Ratio, Agency_Flag, Overtime_Hours |
| `Patient_Acuity` | Nursing acuity scoring for staffing decisions | medium | Acuity_ID, Patient_ID, Encounter_ID, Unit, Acuity_Score, Classification (Low/Medium/High/ICU), Assessment_Date |

**Key Relationships:**

- `Bed_Census` --triggers--> Capacity Management workflow (occupancy threshold breach)
- `Bed_Census` --constrained_by--> patient-flow-policy
- `OR_Schedule` --triggers--> Surgical Block Optimization workflow
- `ED_Arrival` --triggers--> ED Throughput Management workflow
- `Staffing` --depends_on--> `Patient_Acuity` (ratio-based staffing model)

---

## Domain 9: Supply & Materials

**System:** HIS + Pharmacy

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Supply_Inventory` | Medical/surgical supply stock levels | medium | Item_ID, Description, Location, Qty, Par_Level, Lot, Expiry, Vendor, GPO_Contract_Flag, Unit_Cost, Category (Med_Surg/Implant/PPE/Sterile/General) |
| `Supply_Usage` | Supply consumption per case or encounter | medium | Usage_ID, Item_ID, Case_ID, Encounter_ID, Qty_Used, Waste_Qty, Department, Charge_Flag |
| `Purchase_Order` | Supply procurement order | medium | PO_ID, Vendor, Items, Qty, Price, GPO_Price, Delivery_Date, Status (Draft/Approved/Shipped/Received/Closed) |
| `Controlled_Substance_Log` | DEA-regulated substance chain-of-custody | high | Log_ID, Drug_Name, NDC, Dispense_Event, Patient_ID, Nurse_ID, Qty_Dispensed, Qty_Wasted, Waste_Witness, Timestamp, Discrepancy_Flag |

**Key Relationships:**

- `Supply_Inventory` --triggers--> Supply Replenishment workflow (below par level)
- `Supply_Inventory` --constrained_by--> supply-management-policy
- `Controlled_Substance_Log` --constrained_by--> controlled-substance-policy
- `Controlled_Substance_Log` --triggers--> Diversion Detection workflow (discrepancy detection)
- `Supply_Usage` --depends_on--> `Encounter` (consumption attribution)

---

## Domain 10: Quality & Safety

**System:** EHR + Internal | **Standards:** CMS / TJC

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Quality_Measure` | CMS/TJC quality metric definition and performance | high | Measure_ID, CMS_ID, Name, Numerator_Criteria, Denominator_Criteria, Exclusion_Criteria, Performance_Rate, Benchmark, Period, Status (Active/Retired) |
| `Adverse_Event` | Patient safety event and incident report | high | Event_ID, Event_Type (Medication_Error/Fall/Procedural_Complication/HAI/Missed_Diagnosis/Near_Miss), Patient_ID, Encounter_ID, Severity (Near_Miss/Minor/Moderate/Major/Sentinel), Date, Contributing_Factors, Outcome, RCA_Status |
| `Infection_Indicator` | Healthcare-associated infection surveillance | high | Indicator_ID, Patient_ID, Encounter_ID, Infection_Type (CLABSI/CAUTI/SSI/CDiff/VAP/MRSA), Culture_Result, Device_Days, Detection_Date, Confirmed_Flag, NHSN_Reported |
| `Safety_Assessment` | Standardized patient risk screening scores | medium | Assessment_ID, Patient_ID, Encounter_ID, Assessment_Type (Fall_Risk_Morse/Pressure_Injury_Braden/VTE_Risk/Delirium_CAM/Suicide_Risk_Columbia), Score, Risk_Level, Timestamp, Assessed_By |
| `Antibiotic_Order` | Antibiotic stewardship tracking | medium | Order_ID, Patient_ID, Encounter_ID, Drug_Name, NDC, Indication, Culture_Pending_Flag, Duration_Days, De_Escalation_Flag, Stewardship_Review_Status (Pending/Reviewed/Approved/Modified) |

**Key Relationships:**

- `Quality_Measure` --triggers--> Quality Reporting workflow (period close)
- `Quality_Measure` --constrained_by--> quality-reporting-policy
- `Adverse_Event` --triggers--> Patient Safety Response workflow (severity >= Moderate)
- `Infection_Indicator` --triggers--> Infection Control Response workflow
- `Safety_Assessment` --depends_on--> `Encounter` (assessment context)

---

## Domain 11: Population Health

**System:** External + EHR | **Standards:** HEDIS / HCC

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Population_Roster` | Attributed patient panel for value-based care | medium | Roster_ID, MRN, Patient_ID, Payer, Attributed_PCP, HCC_Risk_Score, Chronic_Conditions, Last_Visit, Panel_Status (Active/Inactive/Disenrolled) |
| `Risk_Stratification` | Patient risk tier assignment for care management | medium | Stratification_ID, Patient_ID, Risk_Tier (Low/Rising/High/Complex), Risk_Score, Key_Drivers, Model_Version, Calculation_Date |
| `SDoH_Assessment` | Social determinants of health screening | medium | Assessment_ID, Patient_ID, Housing_Status, Food_Security, Transportation, Employment, ADI_Score, Screening_Date, Referral_Status |
| `Care_Gap` | Open quality/preventive care gap for outreach | medium | Gap_ID, Patient_ID, Measure_HEDIS, Gap_Type (Screening/Lab/Immunization/Annual_Visit/Follow_Up), Due_Date, Status (Open/Closed/Excluded), Closure_Date, Outreach_Attempts |

**Key Relationships:**

- `Population_Roster` --syncs_to--> `Patient_Master` (via ehr-population-health-sync)
- `Risk_Stratification` --triggers--> Care Management Outreach workflow (High/Complex tier)
- `Risk_Stratification` --depends_on--> `Diagnosis`, `Encounter`, `Medication_Order`
- `SDoH_Assessment` --triggers--> Community Resource Referral workflow
- `Care_Gap` --constrained_by--> quality-reporting-policy (HEDIS measure specs)

---

## Domain 12: Regulatory & Compliance

**System:** Internal + External | **Standards:** HIPAA / CMS / TJC

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `PHI_Access_Log` | Protected health information access audit trail | high | Log_ID, User_ID, Patient_ID, System, Action (View/Modify/Print/Export), Timestamp, Access_Justification, Anomaly_Score, IP_Address |
| `Regulatory_Return` | Required regulatory submission tracking | high | Return_ID, Return_Type (CMS_MIPS/IQR/Promoting_Interop/VBP/State_Report), Period, Status (Drafting/Under_Review/Submitted/Accepted/Rejected), Submission_Deadline, Submitted_Date |
| `Accreditation_Standard` | Hospital accreditation compliance tracking | medium | Standard_ID, Body (TJC/DNV/CMS_CoP/State), Category, Requirement, Compliance_Status (Compliant/Partial/Non_Compliant), Last_Review, Next_Review, Evidence_Location |
| `Patient_Consent` | Patient consent and advance directive management | medium | Consent_ID, Patient_ID, Consent_Type (Treatment/Research/Data_Sharing/Advance_Directive/HIE_Opt_In), Status (Active/Revoked/Expired), Granted_Date, Expiry, Witness |
| `Regulatory_Publication` | External regulatory update tracking (NLP-extracted) | medium | Publication_ID, Source (CMS/State/TJC/OIG/FDA), Title, Publication_Date, Effective_Date, Impact_Areas, Summary, Extraction_Confidence |

**Key Relationships:**

- `PHI_Access_Log` --triggers--> Privacy Breach Detection workflow (Anomaly_Score threshold)
- `PHI_Access_Log` --constrained_by--> hipaa-privacy-policy
- `Regulatory_Return` --depends_on--> `Quality_Measure` (measure data feeds submissions)
- `Accreditation_Standard` --constrained_by--> accreditation-readiness-policy
- `Regulatory_Publication` --triggers--> Regulatory Change Impact workflow (new effective dates)

---

[← Back to Ontology Overview](index.md)
