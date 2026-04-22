# Workflows

10 Basel/IFRS-aligned AI workflows that power the 8 finance & banking applications. Each workflow is defined in `enterprise-knowledge/workflows/` as a YAML file with trigger conditions, ordered steps, and entity/policy dependencies.

---

## Workflow Summary

| # | Workflow | Basel/IFRS | Trigger | Primary App |
|---|---------|------------|---------|-------------|
| 1 | [Credit Score Enhancement & EWS](#1-credit-score-enhancement--ews) | Pillar 1 (IRB) | Monthly schedule or EWS signal detected | Credit Risk |
| 2 | [ECL Calculation & Stage Migration](#2-ecl-calculation--stage-migration) | IFRS 9 | Quarterly or DPD change or rating downgrade | Credit Risk, Regulatory Compliance |
| 3 | [Transaction Anomaly Detection](#3-transaction-anomaly-detection) | FATF | Real-time on every transaction | Fraud & AML |
| 4 | [SAR Generation & Filing](#4-sar-generation--filing) | FATF | AML Alert escalated to True Positive | Fraud & AML |
| 5 | [Capital Adequacy Calculation](#5-capital-adequacy-calculation) | Pillar 1 | Monthly or material portfolio change | Regulatory Compliance |
| 6 | [Regulatory Return Generation](#6-regulatory-return-generation) | Pillar 3 / BCBS 239 | Filing deadline approach or ad-hoc request | Regulatory Compliance |
| 7 | [Cash Flow Forecasting & ALM](#7-cash-flow-forecasting--alm) | Liquidity (LCR/NSFR) | Daily schedule or large unexpected flow | Treasury & Liquidity |
| 8 | [Loan Origination Processing](#8-loan-origination-processing) | Pillar 1 (Credit) | New loan application submitted | Loan Lifecycle |
| 9 | [Collections Prioritization](#9-collections-prioritization) | Pillar 1 (Credit) | Daily schedule or new delinquency event | Loan Lifecycle |
| 10 | [Customer 360 & NBA](#10-customer-360--next-best-action) | Pillar 3 (Conduct) | Customer interaction or monthly batch | Customer 360, Revenue |

---

## 1. Credit Score Enhancement & EWS

**ID:** `WORKFLOW_CREDIT_EWS_V1_0` | **Basel:** Pillar 1 (IRB) | **File:** `credit-ews.yaml`

**Trigger:** Monthly (1st business day) OR EWS_Signal detected with severity Amber/Red

| Step | System | Action |
|------|--------|--------|
| 1. Feature Engineering | Internal | Combine bureau scores with CBS behavioral features (transaction velocity, balance trends, utilization, tenure) and LOS repayment data |
| 2. Behavioral Scoring | Internal | Gradient-boosted model on historical defaults; produce composite score (0-1000) incorporating behavioral signals |
| 3. EWS Signal Scan | Internal | Continuous scan: DPD trends, deposit balance erosion, sector index deterioration (Sector_Index), adverse news, collateral movement |
| 4. SICR Assessment | Internal | Evaluate if exposure shows Significant Increase in Credit Risk since origination; flag for stage migration |
| 5. Risk Rating Update | Internal | Recalculate internal risk rating (1-22 scale); flag downgrades for credit committee review |
| 6. Alert Generation | Internal | Red signals: escalate to credit review; Amber: notify relationship manager; publish to dashboard |

**Dependencies:** Customer_Master, Loan_Account, Repayment_Schedule, Deposit_Account, Credit_Score, EWS_Signal, Risk_Rating, Collateral, Sector_Index, Macro_Indicator, credit-risk-policy

---

## 2. ECL Calculation & Stage Migration

**ID:** `WORKFLOW_ECL_CALCULATION_V1_0` | **IFRS 9** | **File:** `ecl-calculation.yaml`

**Trigger:** Quarterly (5th business day after quarter end) OR Loan_Account DPD crosses 30-day threshold OR Risk_Rating downgrade ≥2 notches

| Step | System | Action |
|------|--------|--------|
| 1. Stage Classification | Internal | Apply SICR rules: Stage 1 (performing), Stage 2 (SICR triggered), Stage 3 (credit-impaired / 90+ DPD) |
| 2. PD Model Execution | Internal | Run PD term structures: 12-month PD for Stage 1, lifetime PD for Stage 2/3; incorporate forward-looking macro overlay |
| 3. LGD Estimation | Internal | Calculate loss given default factoring collateral recovery rates, historical recovery data, and collateral market values |
| 4. EAD Projection | Internal | Estimate exposure at default: outstanding + undrawn commitments × credit conversion factor |
| 5. ECL Computation | Internal | Stage 1: 12-month ECL = PD × LGD × EAD; Stage 2/3: lifetime ECL; probability-weighted across macro scenarios (Base/Upside/Downside) |
| 6. Provisioning Impact | Internal | Calculate P&L and balance sheet impact; compare against prior period provisions |
| 7. Publish | Internal | ECL numbers to finance for booking; stage migration reports to credit committee; dashboard update |

**Dependencies:** Loan_Account, Repayment_Schedule, Collateral, Credit_Score, ECL_Staging, Risk_Rating, Macro_Indicator, Provision_Record, credit-risk-policy, capital-adequacy-policy

---

## 3. Transaction Anomaly Detection

**ID:** `WORKFLOW_TXN_ANOMALY_V1_0` | **FATF** | **File:** `transaction-anomaly-detection.yaml`

**Trigger:** Real-time on every Transaction_Ledger or Card_Transaction record

| Step | System | Action |
|------|--------|--------|
| 1. Behavioral Baseline Lookup | Internal | Retrieve customer's Transaction_Pattern profile: typical amounts, frequency, counterparties, channels, geographies |
| 2. Real-Time Scoring | Internal | Score transaction against baseline using isolation forest + autoencoder ensemble; output anomaly score (0-100) |
| 3. Rule Overlay | AML System | Apply regulatory rules: structuring detection, round-trip detection, sanctions geography, high-risk MCC codes |
| 4. Alert Triage | Internal | Classification model trained on historical dispositions; auto-suppress low-risk (score <30); prioritize genuine suspicious activity |
| 5. Network Analysis | Internal | For high-score alerts: build transaction graph; apply community detection and cycle detection for laundering patterns |
| 6. Case Assembly | Internal | Compile case package: customer 360, 90-day transaction timeline, linked entities, KYC status, prior alerts/SARs, sanctions matches |
| 7. Publish | Internal | Prioritized alert queue for investigators; case packages attached; network visualization for complex cases |

**Dependencies:** Transaction_Ledger, Card_Transaction, Transaction_Pattern, Customer_Master, AML_Alert, Watchlist_Match, KYC_Document, aml-kyc-policy

---

## 4. SAR Generation & Filing

**ID:** `WORKFLOW_SAR_GENERATION_V1_0` | **FATF** | **File:** `sar-generation.yaml`

**Trigger:** AML_Alert disposition = True_Positive or Escalated

| Step | System | Action |
|------|--------|--------|
| 1. Evidence Compilation | Internal | Aggregate all evidence: transaction details, network graph, customer profile, KYC docs, prior alerts/SARs, watchlist matches |
| 2. Narrative Generation | Internal | LLM generates SAR narrative per FinCEN/local FIU format: subject information, suspicious activity description, supporting evidence |
| 3. Quality Validation | Internal | Validate completeness: all required fields populated, narrative coherence, regulatory format compliance |
| 4. Investigator Review | AML System | Route to senior investigator for review, edit, and approval |
| 5. Filing | AML System | Submit to FinCEN/local FIU via secure filing channel; record Regulatory_Reference |
| 6. Post-Filing | Internal | Update AML_Alert and SAR_Filing records; link to customer profile; schedule continuing activity monitoring |

**Dependencies:** AML_Alert, SAR_Filing, Customer_Master, Transaction_Ledger, KYC_Document, Watchlist_Match, Transaction_Pattern, aml-kyc-policy

---

## 5. Capital Adequacy Calculation

**ID:** `WORKFLOW_CAPITAL_ADEQUACY_V1_0` | **Basel Pillar 1** | **File:** `capital-adequacy.yaml`

**Trigger:** Monthly (3rd business day) OR material portfolio change (>5% RWA shift)

| Step | System | Action |
|------|--------|--------|
| 1. Exposure Aggregation | Internal | Pull all credit exposures (Loan_Account), market positions (Investment_Holding), and operational loss data (Loss_Event) |
| 2. Credit RWA | Internal | Calculate risk-weighted assets for credit risk per Standardized/IRB approach; apply risk weights per asset class and rating |
| 3. Market RWA | Internal | Calculate market risk capital per FRTB Standardized/IMA approach on Investment_Holding portfolio |
| 4. Operational RWA | Internal | Calculate operational risk capital per Basic Indicator/Standardized approach using Loss_Event history |
| 5. Capital Assembly | Internal | Aggregate Capital_Components: CET1, AT1, Tier 2; apply regulatory deductions |
| 6. Ratio Computation | Internal | CET1 Ratio = CET1 / Total RWA; Tier 1 Ratio; Total Capital Ratio; compare against minimums + buffers |
| 7. Stress Test | Internal | Run prescribed + internal stress scenarios; project ratios under adverse conditions |
| 8. Publish | Internal | Capital dashboard for ALCO/Board; regulatory return data for Pillar 3 disclosure; stress test results for supervisory review |

**Dependencies:** Loan_Account, Investment_Holding, Loss_Event, Capital_Component, RWA_Calculation, Macro_Indicator, Yield_Curve, capital-adequacy-policy

---

## 6. Regulatory Return Generation

**ID:** `WORKFLOW_REG_RETURN_V1_0` | **Basel Pillar 3 / BCBS 239** | **File:** `regulatory-return-generation.yaml`

**Trigger:** Filing deadline 10 business days away OR ad-hoc request from compliance

| Step | System | Action |
|------|--------|--------|
| 1. Data Aggregation | Internal | Pull required data points from ontology: capital, RWA, ECL, liquidity, AML metrics, loss events |
| 2. Reconciliation | Internal | Three-way reconciliation: CBS balances vs. LOS loan book vs. GL positions; flag and route breaks |
| 3. Template Population | Internal | Map calculated numbers to regulatory return template fields; apply validation rules |
| 4. Data Lineage Capture | Internal | Record source-to-report traceability for every number; store transformation logic and model parameters |
| 5. Review & Approval | Internal | Route to compliance officer for review; CFO sign-off for capital returns |
| 6. Submission | Internal | Generate submission-ready files; file electronically; record Regulatory_Return status |
| 7. Regulatory Change Scan | Internal | LLM-based monitoring of regulatory publications; extract changes and assess impact on current filings |

**Dependencies:** Capital_Component, RWA_Calculation, Provision_Record, Liquidity_Position, AML_Alert, SAR_Filing, Loss_Event, Regulatory_Return, Regulatory_Circular, capital-adequacy-policy, data-freshness-policy

---

## 7. Cash Flow Forecasting & ALM

**ID:** `WORKFLOW_CASH_FLOW_ALM_V1_0` | **Basel Liquidity** | **File:** `cash-flow-alm.yaml`

**Trigger:** Daily (06:00 UTC) OR single-day net outflow exceeds 2σ above forecast

| Step | System | Action |
|------|--------|--------|
| 1. Position Snapshot | CBS | Extract end-of-day balance sheet positions: deposits, loans, investments, interbank balances with maturity schedules |
| 2. Cash Flow Projection | Internal | Combine contractual flows with behavioral models (deposit stickiness, prepayment rates, drawdown patterns) and Salesforce pipeline |
| 3. Yield Curve Ingestion | Market Data | Pull end-of-day yield curves across relevant tenors and currencies |
| 4. LCR/NSFR Calculation | Internal | Compute LCR (HQLA / 30-day net outflows) and NSFR; recommend HQLA composition optimization |
| 5. ALM Analysis | Internal | Duration gap, repricing gap, NII sensitivity (±100/200/300 bps), EVE impact |
| 6. FTP Rate Computation | Internal | Tenor-matched FTP rates using swap curve + liquidity premium + credit spread |
| 7. Stress Scenarios | Internal | Multi-factor scenarios: rate movements, deposit run-off, credit line drawdowns, market stress |
| 8. Publish | Internal | Treasury dashboard; LCR/NSFR monitoring; FTP rates for business units; stress results for ALCO |

**Dependencies:** Balance_Sheet_Position, Deposit_Account, Fixed_Deposit, Loan_Account, Investment_Holding, Liquidity_Position, Yield_Curve, FTP_Rate, Interbank_Transaction, Opportunity, treasury-liquidity-policy

---

## 8. Loan Origination Processing

**ID:** `WORKFLOW_LOAN_ORIGINATION_V1_0` | **Basel Pillar 1** | **File:** `loan-origination.yaml`

**Trigger:** New Loan_Application submitted in LOS

| Step | System | Action |
|------|--------|--------|
| 1. Application Intake | LOS | Validate completeness; assign to processing queue |
| 2. Document Processing | Internal | LLM + OCR extraction from Loan_Documents: income figures, employer, property details, financial ratios |
| 3. KYC Verification | Internal | Validate Customer_Master KYC status; trigger enhanced due diligence if risk-rated High/Very_High |
| 4. Credit Assessment | Internal | Pull Credit_Score; run credit decision model combining bureau, behavioral, and document-extracted data |
| 5. Collateral Valuation | Internal | For secured loans: verify Collateral valuation; calculate LTV ratio; flag if >80% LTV |
| 6. Underwriting Decision | LOS | Auto-approve within policy limits; refer to underwriter for exceptions; reject if below threshold |
| 7. Disbursement | CBS | On approval: create Loan_Account; set Repayment_Schedule; disburse funds |

**Dependencies:** Loan_Application, Customer_Master, Loan_Document, KYC_Document, Credit_Score, Collateral, Loan_Account, Repayment_Schedule, lending-policy, aml-kyc-policy

---

## 9. Collections Prioritization

**ID:** `WORKFLOW_COLLECTIONS_V1_0` | **Basel Pillar 1** | **File:** `collections-prioritization.yaml`

**Trigger:** Daily (07:00 UTC) OR new Loan_Account enters 1+ DPD

| Step | System | Action |
|------|--------|--------|
| 1. Delinquency Scan | CBS | Identify all accounts with DPD ≥ 1; calculate delinquency bucket assignment |
| 2. Recovery Scoring | Internal | ML model predicting: self-cure probability, recovery probability with contact, optimal channel, best time to contact |
| 3. Segmentation | Internal | Segment: self-cure (monitor only), soft collection (SMS/email), hard collection (call/visit), restructuring candidate, legal action |
| 4. Work Queue Generation | Internal | Prioritize by: recovery probability × amount at risk × customer tier; assign to collectors |
| 5. NPA Early Warning | Internal | Flag accounts with >60% probability of reaching 90 DPD in next 90 days; recommend proactive restructuring |
| 6. Collateral Assessment | Internal | For secured delinquent loans: check current Collateral market value; assess recovery via collateral enforcement |
| 7. Publish | Internal | Collections work queue for recovery team; NPA watchlist for credit team; dashboard metrics |

**Dependencies:** Loan_Account, Repayment_Schedule, Customer_Master, Credit_Score, Collateral, EWS_Signal, collections-recovery-policy

---

## 10. Customer 360 & Next-Best-Action

**ID:** `WORKFLOW_CUSTOMER_NBA_V1_0` | **Basel Pillar 3 (Conduct)** | **File:** `customer-nba.yaml`

**Trigger:** Customer interaction in Salesforce FSC OR monthly batch (1st business day)

| Step | System | Action |
|------|--------|--------|
| 1. Entity Resolution | Internal | Match CIF across CBS, Salesforce FSC, LOS, AML into single golden record |
| 2. Household Discovery | Internal | Graph analysis: joint accounts, shared addresses, beneficiaries → build Household structures |
| 3. Profile Assembly | Internal | Aggregate: all product holdings, balances, transactions, interactions, loan performance, risk flags |
| 4. CLV Modeling | Internal | Predict 3-year forward revenue per customer; gradient-boosted on product trajectory and balance trends |
| 5. Churn Scoring | Internal | Survival analysis for 90-day churn probability; features: balance velocity, transaction frequency, complaints |
| 6. Product Propensity | Internal | Multi-label classification: predict highest-propensity unowned products per customer |
| 7. Next-Best-Action | Internal | Combine CLV, churn risk, product gaps, life-stage triggers, compliance needs → ranked recommendations |
| 8. Publish | Salesforce FSC | Push NBA to advisor; churn alerts to RM; dashboard for branch and digital channels |

**Dependencies:** Customer_Master, Household, Deposit_Account, Loan_Account, Transaction_Ledger, SF_Account, SF_Financial_Account, Advisory_Interaction, Opportunity, Campaign, Credit_Score, AML_Alert, KYC_Document, customer-relationship-policy

---

[← Back to Ontology Overview](index.md)
