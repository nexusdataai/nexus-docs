# Application-Object Mapping

Minimum required ontology objects per application, with relationship details and cross-application dependency analysis.

---

## App 1: Patient 360 & Care Coordination

**FHIR:** Patient/Encounter | **Minimum Objects: 12**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Patient_Master` | EHR | Core entity — golden patient record | — |
| `Patient_Identifier` | EHR | MRN, SSN, insurance ID cross-referencing | depends_on -> Patient_Master |
| `Encounter` | EHR | Visit/admission tracking and episode management | depends_on -> Patient_Master |
| `Diagnosis` | EHR | Active and historical diagnoses for longitudinal view | depends_on -> Encounter |
| `Problem_List` | EHR | Chronic condition tracking across encounters | depends_on -> Patient_Master |
| `Medication_Order` | EHR | Active medications and reconciliation | depends_on -> Patient_Master |
| `Lab_Result` | Lab/Imaging | Lab results for clinical trending | depends_on -> Patient_Master |
| `Imaging_Result` | Lab/Imaging | Radiology and imaging findings | depends_on -> Patient_Master |
| `Allergy` | EHR | Allergy and adverse reaction history | depends_on -> Patient_Master |
| `Discharge` | EHR | Discharge planning and disposition tracking | depends_on -> Encounter |
| `SDoH_Assessment` | EHR | Social determinants of health screening | depends_on -> Patient_Master |
| `Care_Gap` | Internal | HEDIS/quality measure compliance gaps | depends_on -> Patient_Master |

**Policies:** clinical-safety-policy, hipaa-privacy-policy
**Workflows:** patient-matching, care-gap-detection
**Integrations:** ehr-rcm-sync, notes-nlp, population-feed

---

## App 2: Clinical Decision Support

**FHIR:** MedicationRequest/Observation | **Minimum Objects: 11**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Patient_Master` | EHR | Patient context for clinical rules | — |
| `Diagnosis` | EHR | Active diagnoses triggering decision rules | depends_on -> Patient_Master |
| `Medication_Order` | EHR | Prescription data for interaction checking | depends_on -> Patient_Master |
| `Medication_Administration` | EHR | MAR data for dose timing validation | depends_on -> Medication_Order |
| `Lab_Result` | Lab/Imaging | Lab values for clinical alerting | depends_on -> Patient_Master |
| `Vital_Sign` | EHR | Real-time vitals for early warning scoring | depends_on -> Patient_Master |
| `Allergy` | EHR | Allergy context for drug safety checks | depends_on -> Patient_Master |
| `Clinical_Order` | EHR | Order entry for CPOE decision support | depends_on -> Patient_Master |
| `Drug_Interaction` | Internal | Drug-drug and drug-allergy interaction rules | depends_on -> Medication_Order |
| `Clinical_Guideline` | Internal | Evidence-based clinical pathways and protocols | — |
| `Early_Warning_Score` | Internal | Composite deterioration score (NEWS/MEWS) | depends_on -> Vital_Sign |

**Policies:** clinical-safety-policy
**Workflows:** clinical-decision-support, critical-result-management
**Integrations:** lab-imaging-feed, notes-nlp

---

## App 3: Revenue Cycle Optimization

**FHIR:** Claim/EOB | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Patient_Master` | EHR | Patient identity for billing | — |
| `Encounter` | EHR | Visit context for charge capture | depends_on -> Patient_Master |
| `Diagnosis` | EHR | DRG assignment and coding accuracy | depends_on -> Encounter |
| `Claim` | RCM | Claim submission and adjudication tracking | depends_on -> Encounter |
| `Charge` | RCM | Charge capture and CDM mapping | depends_on -> Encounter |
| `Denial` | RCM | Denial tracking and root cause analysis | depends_on -> Claim |
| `Payer_Contract` | RCM | Contract terms and reimbursement rates | — |
| `Prior_Authorization` | RCM | Authorization status and compliance | depends_on -> Encounter |
| `Patient_Financial` | RCM | Patient liability and payment plans | depends_on -> Patient_Master |
| `Procedure_Record` | EHR | Procedure coding for claim accuracy | depends_on -> Encounter |

**Policies:** revenue-cycle-policy
**Workflows:** denial-prediction
**Integrations:** ehr-rcm-sync, notes-nlp

---

## App 4: Operational Efficiency & Capacity

**FHIR:** Location/Schedule | **Minimum Objects: 9**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Patient_Master` | EHR | Patient identity for census and flow | — |
| `Encounter` | EHR | Admission/discharge/transfer tracking | depends_on -> Patient_Master |
| `Bed_Census` | HIS | Real-time bed availability and occupancy | depends_on -> Encounter |
| `OR_Schedule` | HIS | Operating room utilization and scheduling | depends_on -> Encounter |
| `ED_Arrival` | HIS | Emergency department throughput tracking | depends_on -> Patient_Master |
| `Staffing` | HIS | Nurse/physician staffing levels and ratios | depends_on -> Bed_Census |
| `Patient_Acuity` | EHR | Acuity-based patient classification | depends_on -> Patient_Master |
| `Discharge` | EHR | Discharge readiness and disposition planning | depends_on -> Encounter |
| `Vital_Sign` | EHR | Vital trends for patient acuity scoring | depends_on -> Patient_Master |

**Policies:** bed-management-policy
**Workflows:** bed-management
**Integrations:** ehr-his-sync

---

## App 5: Population Health Management

**HEDIS/HCC | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Patient_Master` | EHR | Patient demographics for population segmentation | — |
| `Encounter` | EHR | Utilization patterns and visit frequency | depends_on -> Patient_Master |
| `Diagnosis` | EHR | Chronic condition prevalence and HCC coding | depends_on -> Patient_Master |
| `Medication_Order` | EHR | Medication adherence tracking | depends_on -> Patient_Master |
| `Lab_Result` | Lab/Imaging | Lab trends for chronic disease management | depends_on -> Patient_Master |
| `Population_Roster` | Population Data | Health plan member roster and attribution | depends_on -> Patient_Master |
| `Risk_Stratification` | Internal | Risk score assignment (HCC, CDPS) | depends_on -> Patient_Master |
| `SDoH_Assessment` | EHR | Social risk factors for population analytics | depends_on -> Patient_Master |
| `Care_Gap` | Internal | Quality measure compliance gaps per patient | depends_on -> Patient_Master |
| `Quality_Measure` | Internal | HEDIS/MIPS measure definitions and targets | — |

**Policies:** quality-measure-policy
**Workflows:** population-risk-stratification, care-gap-detection
**Integrations:** population-feed, ehr-rcm-sync

---

## App 6: Supply Chain & Pharmacy Intelligence

**Minimum Objects: 8**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Supply_Inventory` | HIS | Par-level and stock-on-hand tracking | — |
| `Supply_Usage` | HIS | Consumption data for demand forecasting | depends_on -> Supply_Inventory |
| `Purchase_Order` | HIS | Procurement and vendor order tracking | depends_on -> Supply_Inventory |
| `Pharmacy_Inventory` | HIS | Drug inventory and formulary status | — |
| `Controlled_Substance_Log` | HIS | DEA-regulated substance chain of custody | depends_on -> Pharmacy_Inventory |
| `Medication_Order` | EHR | Prescription demand signal for pharmacy | depends_on -> Pharmacy_Inventory |
| `OR_Schedule` | HIS | Surgical supply demand based on case schedule | depends_on -> Supply_Inventory |
| `Encounter` | EHR | Patient volume for supply demand correlation | — |

**Policies:** pharmacy-formulary-policy
**Workflows:** supply-demand-forecasting
**Integrations:** ehr-his-sync

---

## App 7: Clinical Quality & Safety

**CMS/TJC | **Minimum Objects: 11**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Patient_Master` | EHR | Patient identity for quality measure attribution | — |
| `Encounter` | EHR | Episode context for quality measures | depends_on -> Patient_Master |
| `Diagnosis` | EHR | Condition data for quality numerator/denominator | depends_on -> Encounter |
| `Medication_Order` | EHR | Medication data for safety and stewardship | depends_on -> Patient_Master |
| `Lab_Result` | Lab/Imaging | Lab values for infection and safety indicators | depends_on -> Patient_Master |
| `Vital_Sign` | EHR | Vitals for sepsis and deterioration screening | depends_on -> Patient_Master |
| `Quality_Measure` | Internal | CMS/TJC measure definitions and benchmarks | — |
| `Adverse_Event` | Internal | Safety event tracking and root cause analysis | depends_on -> Encounter |
| `Infection_Indicator` | Lab/Internal | HAI surveillance markers (CAUTI, CLABSI, SSI) | depends_on -> Encounter |
| `Safety_Assessment` | Internal | Fall risk, pressure injury, and restraint scoring | depends_on -> Patient_Master |
| `Antibiotic_Order` | EHR | Antibiotic stewardship and usage tracking | depends_on -> Medication_Order |

**Policies:** quality-measure-policy, clinical-safety-policy
**Workflows:** hai-surveillance
**Integrations:** lab-imaging-feed, notes-nlp

---

## App 8: Regulatory & Compliance Automation

**HIPAA/CMS | **Minimum Objects: 9**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Patient_Master` | EHR | Patient identity for compliance tracking | — |
| `Encounter` | EHR | Episode data for regulatory submissions | depends_on -> Patient_Master |
| `PHI_Access_Log` | Internal | HIPAA access audit trail | depends_on -> Patient_Master |
| `Quality_Measure` | Internal | CMS/MIPS/IQR measure reporting | — |
| `Regulatory_Return` | Internal | Filing status and submission tracking | — |
| `Accreditation_Standard` | Internal | TJC/DNV accreditation requirement mapping | — |
| `Patient_Consent` | EHR | Consent forms and authorization records | depends_on -> Patient_Master |
| `Regulatory_Publication` | External | Regulatory change intelligence and updates | — |
| `Claim` | RCM | Claim data for CMS regulatory reporting | depends_on -> Encounter |

**Policies:** hipaa-privacy-policy, regulatory-reporting-policy
**Workflows:** regulatory-reporting
**Integrations:** regulatory-feed

---

## Cross-Application Dependency Matrix

Shows which entities are shared across applications (checkmark = required by that app):

| Entity | Patient 360 | CDS | Revenue Cycle | Ops | Pop Health | Supply | Quality | Regulatory |
|--------|-------------|-----|---------------|-----|------------|--------|---------|------------|
| **Patient_Master** | x | x | x | x | x | — | x | x |
| **Encounter** | x | — | x | x | x | x | x | x |
| **Diagnosis** | x | x | x | — | x | — | x | — |
| **Medication_Order** | x | x | — | — | x | x | x | — |
| **Lab_Result** | x | x | — | — | x | — | x | — |
| **Vital_Sign** | — | x | — | x | — | — | x | — |
| **Quality_Measure** | — | — | — | — | x | — | x | x |
| **Allergy** | x | x | — | — | — | — | — | — |
| **Discharge** | x | — | — | x | — | — | — | — |
| **SDoH_Assessment** | x | — | — | — | x | — | — | — |
| **Care_Gap** | x | — | — | — | x | — | — | — |
| **Claim** | — | — | x | — | — | — | — | x |
| **OR_Schedule** | — | — | — | x | — | x | — | — |

---

## Entity Count per App

| Application | Min Objects | Workflows | Policies | Integrations |
|------------|-----------|-----------|----------|--------------|
| Patient 360 & Care Coordination | 12 | 2 | 2 | 3 |
| Clinical Decision Support | 11 | 2 | 1 | 2 |
| Revenue Cycle Optimization | 10 | 1 | 1 | 2 |
| Operational Efficiency & Capacity | 9 | 1 | 1 | 1 |
| Population Health Management | 10 | 2 | 1 | 2 |
| Supply Chain & Pharmacy | 8 | 1 | 1 | 1 |
| Clinical Quality & Safety | 11 | 1 | 2 | 2 |
| Regulatory & Compliance | 9 | 1 | 2 | 1 |

---

[← Back to Ontology Overview](index.md)
