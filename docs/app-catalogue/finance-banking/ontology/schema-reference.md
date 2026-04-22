# Schema Reference

Complete reference for the finance & banking semantic schema — 12 domains, ~50 tables across 6 source systems, aligned to Basel III/IV, IFRS 9, and FATF standards.

**Source File:** `enterprise-knowledge/finance-banking-schema.yaml`

---

## Domain 1: Customer & Relationship Management

**System:** Core Banking System + Salesforce FSC | **Basel:** Pillar 3 (Disclosure) | **FATF:** CDD

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Customer_Master` | Central customer/entity master — most connected entity in the ontology | high | CIF_Number, Name, Type (Individual/Corporate/Trust/Joint), Segment (Retail/SME/Corporate/HNW/UHNW), DOB, Nationality, Tax_ID, KYC_Status (Verified/Pending/Expired/Enhanced), Risk_Rating (Low/Medium/High/Very_High), PEP_Flag, Onboard_Date, Status (Active/Dormant/Suspended/Closed), Relationship_Manager_ID |
| `Household` | Family/relationship group aggregation | medium | Household_ID, Primary_CIF, Members (array of CIF), Total_AUM, Total_Relationship_Value, Segment, Status |
| `Relationship_Group` | Corporate group / beneficial ownership structure | high | Group_ID, Parent_Entity_CIF, Members (array of CIF + ownership_pct), Group_Type (Corporate_Group/Family_Office/Trust_Structure), Total_Exposure |

**Key Relationships:**

- `Customer_Master` --syncs_to--> `SF_Account` (via cbs-sfsc-sync)
- `Customer_Master` --triggers--> Customer Churn Prediction workflow
- `Customer_Master` --constrained_by--> aml-kyc-policy
- `Customer_Master` --validates--> `KYC_Document`
- `Household` --depends_on--> `Customer_Master` (multiple)
- `Relationship_Group` --depends_on--> `Customer_Master` (multiple)

---

## Domain 2: Deposit & Account Management

**System:** Core Banking System | **Basel:** Pillar 1 (Liquidity — LCR/NSFR)

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Deposit_Account` | Customer deposit/savings/current account | high | Account_ID, CIF_Number, Type (Savings/Current/Fixed_Deposit/Recurring_Deposit/Money_Market), Currency, Balance, Interest_Rate, Maturity_Date, Auto_Renewal, Status (Active/Dormant/Frozen/Closed), Branch_ID |
| `Fixed_Deposit` | Term deposit with specific maturity | medium | FD_ID, Account_ID, CIF_Number, Principal, Rate, Tenor_Months, Start_Date, Maturity_Date, Payout_Frequency, Premature_Withdrawal_Penalty_Pct, Auto_Renewal |
| `Account_Balance_History` | Daily balance snapshots for trend analysis | medium | Account_ID, Date, Opening_Balance, Closing_Balance, Avg_Monthly_Balance, Min_Balance, Max_Balance |

**Key Relationships:**

- `Deposit_Account` --depends_on--> `Customer_Master`
- `Deposit_Account` --triggers--> Cash Flow Forecasting workflow (on maturity approach)
- `Account_Balance_History` --depends_on--> `Deposit_Account`
- `Deposit_Account` --constrained_by--> treasury-liquidity-policy (LCR classification)

---

## Domain 3: Lending & Credit

**System:** Loan Origination System + CBS | **Basel:** Pillar 1 (Credit Risk) | **IFRS 9:** ECL

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Loan_Application` | Loan application through origination pipeline | high | Application_ID, Applicant_CIF, Co_Applicant_CIF, Product_Type (Home_Loan/Personal_Loan/Auto_Loan/Business_Loan/Credit_Card/Overdraft), Amount_Requested, Stage (Application/Credit_Check/Underwriting/Approval/Disbursement/Rejected/Withdrawn), Submit_Date, Decision_Date, Decision (Approved/Declined/Conditional/Referred), Underwriter_ID |
| `Loan_Account` | Active loan/credit facility | high | Loan_ID, CIF_Number, Product_Type, Sanctioned_Amount, Outstanding_Balance, Disbursed_Amount, Interest_Rate, Rate_Type (Fixed/Floating/Mixed), Tenor_Months, EMI_Amount, Next_Due_Date, DPD (Days_Past_Due), Delinquency_Bucket (Current/1-30/31-60/61-90/90+/NPA), Status (Active/Closed/Written_Off/Restructured), NPA_Date, Risk_Weight |
| `Repayment_Schedule` | Loan EMI schedule and payment history | high | Schedule_ID, Loan_ID, Installment_Number, Due_Date, Principal_Due, Interest_Due, Total_Due, Amount_Paid, Paid_Date, Bounce_Flag, Bounce_Reason, DPD |
| `Collateral` | Security/collateral pledged against loan | high | Collateral_ID, Loan_ID, CIF_Number, Type (Residential_Property/Commercial_Property/Vehicle/Gold/Securities/Fixed_Deposit/Plant_Machinery), Description, Original_Valuation, Current_Market_Value, LTV_Ratio, Last_Valuation_Date, Lien_Status (First_Charge/Second_Charge/Pari_Passu), Valuation_Source |
| `Guarantor` | Personal/corporate guarantee | medium | Guarantor_ID, Loan_ID, CIF_Number, Guarantee_Type (Personal/Corporate/Government), Guarantee_Amount, Status (Active/Invoked/Released) |

**Key Relationships:**

- `Loan_Account` --depends_on--> `Customer_Master`
- `Loan_Account` --triggers--> ECL Calculation workflow (on DPD change)
- `Loan_Account` --triggers--> Collections Prioritization workflow (on delinquency)
- `Loan_Application` --constrained_by--> lending-policy
- `Collateral` --depends_on--> `Loan_Account`
- `Collateral` --triggers--> Credit Risk EWS workflow (on valuation decline)
- `Repayment_Schedule` --depends_on--> `Loan_Account`

---

## Domain 4: Credit Risk & Scoring

**System:** Internal (derived from CBS + LOS) | **Basel:** Pillar 1 (IRB) | **IFRS 9:** PD/LGD/EAD

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Credit_Score` | Composite credit risk score per borrower | high | Score_ID, CIF_Number, Bureau_Score, Behavioral_Score, Composite_Score (0-1000), PD_12M, PD_Lifetime, Score_Date, Model_Version, Score_Band (AAA/AA/A/BBB/BB/B/CCC/CC/C/D) |
| `ECL_Staging` | IFRS 9 stage classification and ECL per exposure | high | Staging_ID, Loan_ID, Stage (1/2/3), SICR_Flag, SICR_Trigger (DPD_30/Rating_Downgrade_2/Restructured/Watchlist/Qualitative), PD, LGD, EAD, ECL_12M, ECL_Lifetime, Macro_Scenario (Base/Upside/Downside), Model_Version, Calculation_Date |
| `EWS_Signal` | Early Warning System signal per borrower | medium | Signal_ID, CIF_Number, Loan_ID, Signal_Type (DPD_Trend/Balance_Erosion/Sector_Stress/Adverse_News/Collateral_Decline/Behavioral_Change), Severity (Green/Amber/Red), Detection_Date, Description |
| `Risk_Rating` | Internal credit risk rating per borrower | high | Rating_ID, CIF_Number, Rating (1-22 scale), Rating_Date, Previous_Rating, Migration_Direction (Upgrade/Stable/Downgrade), Reviewer_ID, Override_Flag |

**Key Relationships:**

- `Credit_Score` --depends_on--> `Customer_Master`, `Loan_Account`, `Repayment_Schedule`
- `ECL_Staging` --depends_on--> `Loan_Account`, `Credit_Score`, `Collateral`
- `ECL_Staging` --constrained_by--> credit-risk-policy
- `EWS_Signal` --triggers--> Credit Risk EWS workflow
- `Risk_Rating` --triggers--> ECL Calculation workflow (on downgrade)

---

## Domain 5: Financial Crime & AML

**System:** AML / Transaction Monitoring | **FATF:** Recommendations 10-21

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `AML_Alert` | Transaction monitoring alert | high | Alert_ID, CIF_Number, Rule_Name, Score, Status (New/Under_Investigation/Escalated/Closed_True_Positive/Closed_False_Positive), Assigned_Analyst, Transactions_Flagged (array), Generated_Date, Disposition_Date |
| `SAR_Filing` | Suspicious Activity Report | high | SAR_ID, Alert_ID, CIF_Number, Filing_Type (Initial/Continuation/Joint), Suspicious_Activity_Type, Amount_Involved, Narrative, Status (Draft/Review/Filed/Acknowledged), Filing_Date, Regulatory_Reference |
| `Watchlist_Match` | Sanctions/PEP screening match | high | Match_ID, CIF_Number, List_Source (OFAC/EU/UN/Local_Regulator/PEP_Database), Matched_Entity_Name, Match_Score (0-100), Status (Pending_Review/True_Match/False_Positive/Escalated), Screening_Date |
| `Transaction_Pattern` | Behavioral transaction pattern profile | medium | Pattern_ID, CIF_Number, Typical_Monthly_Volume, Typical_Monthly_Value, Typical_Counterparties, Typical_Channels, Typical_Geographies, Baseline_Period, Last_Updated |

**Key Relationships:**

- `AML_Alert` --depends_on--> `Customer_Master`, `Transaction_Ledger`
- `AML_Alert` --triggers--> Transaction Anomaly Detection workflow
- `SAR_Filing` --depends_on--> `AML_Alert`
- `SAR_Filing` --constrained_by--> aml-kyc-policy
- `Watchlist_Match` --triggers--> immediate escalation (per aml-kyc-policy)
- `Transaction_Pattern` --depends_on--> `Customer_Master`, `Transaction_Ledger`

---

## Domain 6: Transaction & Payments

**System:** Core Banking System | **Basel:** Pillar 1 (Operational Risk)

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Transaction_Ledger` | Core banking transaction record | high | Txn_ID, Account_ID, CIF_Number, Date, Amount, Currency, Type (Credit/Debit), Category (Salary/Transfer/ATM/POS/Wire/ACH/Check/Interest/Fee/Loan_Repayment), Channel (Branch/ATM/Mobile/Internet/Wire/ACH), Counterparty_Account, Counterparty_Name, Reference, Status |
| `Interbank_Transaction` | Interbank settlement and money market | high | Txn_ID, Counterparty_Bank, Direction (Lend/Borrow), Amount, Currency, Rate, Tenor, Settlement_Date, Maturity_Date, Status |
| `Card_Transaction` | Debit/credit card transaction | medium | Txn_ID, Card_Number, CIF_Number, Merchant_Name, MCC_Code, Amount, Currency, Country, Channel (POS/Online/Contactless/ATM), Authorization_Status, Fraud_Score |

**Key Relationships:**

- `Transaction_Ledger` --depends_on--> `Deposit_Account` or `Loan_Account`
- `Transaction_Ledger` --triggers--> Transaction Anomaly Detection workflow (real-time)
- `Card_Transaction` --triggers--> Transaction Anomaly Detection workflow (real-time)
- `Interbank_Transaction` --constrained_by--> treasury-liquidity-policy

---

## Domain 7: Treasury & Investments

**System:** Core Banking System / Treasury | **Basel:** Pillar 1 (Market Risk) + Liquidity

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Balance_Sheet_Position` | Aggregated balance sheet line item | high | Position_ID, Category (Assets/Liabilities/Equity), Sub_Category, Currency, Balance, Maturity_Bucket, Repricing_Date, Duration, Rate_Sensitivity, Date |
| `Investment_Holding` | Bank's proprietary investment portfolio | high | Holding_ID, Security_Type (Government_Bond/Corporate_Bond/Equity/Mutual_Fund/T_Bill/Commercial_Paper), ISIN, Face_Value, Market_Value, Yield, Maturity_Date, HQLA_Level (Level_1/Level_2A/Level_2B/Non_HQLA), Credit_Rating, Accounting_Treatment (HTM/AFS/FVTPL) |
| `FTP_Rate` | Fund transfer pricing rate | medium | Rate_ID, Tenor_Bucket, Currency, Rate, Liquidity_Premium, Credit_Spread, Effective_Date, Published_By |
| `Liquidity_Position` | Daily liquidity ratio tracking | high | Position_ID, Date, HQLA_Stock, Net_Cash_Outflow_30D, LCR_Ratio, Available_Stable_Funding, Required_Stable_Funding, NSFR_Ratio |

**Key Relationships:**

- `Balance_Sheet_Position` --triggers--> Capital Adequacy Calculation workflow
- `Investment_Holding` --depends_on--> `Balance_Sheet_Position`
- `Investment_Holding` --constrained_by--> treasury-liquidity-policy (HQLA composition)
- `Liquidity_Position` --triggers--> Cash Flow Forecasting workflow (on LCR threshold approach)
- `FTP_Rate` --depends_on--> `Yield_Curve`

---

## Domain 8: Market Data & Rates

**System:** Market Data (Bloomberg/Refinitiv) | **Basel:** Market Risk (FRTB)

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Yield_Curve` | Interest rate term structure | medium | Curve_ID, Curve_Type (Government/Swap/Corporate/OIS), Currency, Date, Tenor_Points (array: tenor + rate pairs), Source |
| `Macro_Indicator` | Macroeconomic indicator for stress testing | medium | Indicator_ID, Name (GDP_Growth/Unemployment_Rate/CPI/Policy_Rate/Housing_Index), Country, Value, Date, Source, Forecast_Value, Forecast_Period |
| `Sector_Index` | Industry sector performance index | low | Index_ID, Sector, Country, Value, Change_Pct_30D, Change_Pct_90D, Date, Source |
| `Commodity_Price` | Commodity price for collateral and market risk | low | Price_ID, Commodity (Gold/Silver/Crude_Oil/Steel), Price_Per_Unit, Currency, Date, Source, Change_Pct_30D |

**Key Relationships:**

- `Yield_Curve` --triggers--> ALM Analysis in Treasury workflow
- `Macro_Indicator` --triggers--> ECL Calculation workflow (forward-looking overlay)
- `Sector_Index` --triggers--> Credit Risk EWS workflow (sector stress)
- All ingested via `market-data-feed` integration

---

## Domain 9: Regulatory & Compliance

**System:** Internal (derived) + Document Management | **Basel:** All Pillars | **BCBS 239**

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Capital_Component` | Regulatory capital components | high | Component_ID, Type (CET1/AT1/Tier_2), Sub_Type (Share_Capital/Retained_Earnings/Reserves/Subordinated_Debt/Deductions), Amount, Currency, Date |
| `RWA_Calculation` | Risk-weighted asset computation | high | RWA_ID, Risk_Type (Credit/Market/Operational), Approach (Standardized/IRB_Foundation/IRB_Advanced/FRTB_SA/FRTB_IMA/BIA/TSA), Exposure_Amount, Risk_Weight, RWA_Amount, Date |
| `Provision_Record` | ECL provision booking per accounting period | high | Provision_ID, Period, Stage_1_ECL, Stage_2_ECL, Stage_3_ECL, Total_ECL, PnL_Impact, Model_Version, Macro_Scenario_Weights |
| `Regulatory_Return` | Regulatory filing/return record | high | Return_ID, Return_Type (Basel_III_Capital/LCR/NSFR/IFRS9_Disclosure/AML_Report/Local_Central_Bank), Period, Status (Draft/Review/Approved/Filed), Submission_Deadline, Actual_Submission_Date |
| `Regulatory_Circular` | Regulatory publication/amendment (NLP-extracted) | medium | Circular_ID, Issuer (Basel_Committee/Central_Bank/IASB/FATF), Title, Publication_Date, Effective_Date, Impact_Areas, Compliance_Status (Assessed/Action_Required/Compliant), Extraction_Confidence |

**Key Relationships:**

- `Capital_Component` --triggers--> Capital Adequacy Calculation workflow
- `RWA_Calculation` --depends_on--> `Loan_Account`, `Investment_Holding`, `Loss_Event`
- `Provision_Record` --depends_on--> `ECL_Staging`
- `Regulatory_Circular` --triggers--> Regulatory Change Intelligence workflow
- `Regulatory_Return` --constrained_by--> capital-adequacy-policy

---

## Domain 10: Document Intelligence

**System:** Document Management (SharePoint/Box) | **FATF:** CDD Documentation

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `KYC_Document` | Know Your Customer documentation | high | Document_ID, CIF_Number, Type (ID_Proof/Address_Proof/Income_Proof/Financial_Statement/Board_Resolution/Beneficial_Ownership), Verification_Status (Verified/Pending/Rejected/Expired), Expiry_Date, Extraction_Confidence, Source |
| `Loan_Document` | Loan origination supporting document | medium | Document_ID, Application_ID, Type (Income_Proof/Bank_Statement/Title_Deed/Valuation_Report/Insurance_Policy/Financial_Statement), Extracted_Data (JSON), Verification_Status, Extraction_Confidence |
| `Contract_Document` | Legal agreements and contracts (NLP-extracted) | high | Contract_ID, CIF_Number, Type (Loan_Agreement/Guarantee_Deed/Mortgage_Deed/Service_Agreement), Effective_Date, Expiry_Date, Key_Terms_Extracted, Extraction_Confidence |
| `Compliance_Report` | Audit and compliance reports (NLP-extracted) | medium | Report_ID, Type (Internal_Audit/External_Audit/Regulatory_Exam/Compliance_Review), Period, Findings_Count, Critical_Findings, Status, Document_Path |

**Key Relationships:**

- `KYC_Document` --validates--> `Customer_Master` (onboarding and renewal)
- `KYC_Document` --constrained_by--> aml-kyc-policy
- `Loan_Document` --depends_on--> `Loan_Application`
- `Loan_Document` --triggers--> Loan Origination Processing workflow (on verification)
- All extracted via `unstructured-extraction` integration pipeline

---

## Domain 11: Interaction & Advisory

**System:** Salesforce FSC | **Basel:** Pillar 3 (Conduct)

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `SF_Account` | Salesforce account record (synced from CBS) | medium | Account_ID, CIF_Number, Name, Segment, Tier, Relationship_Manager, Status |
| `SF_Financial_Account` | Salesforce financial account view | medium | Financial_Account_ID, Account_ID, Product_Type, Balance, Status |
| `Advisory_Interaction` | Advisor-customer interaction record | low | Interaction_ID, Account_ID, Advisor_ID, Date, Channel (Branch/Phone/Video/Email), Type (Review/Recommendation/Complaint/KYC_Update), Notes, Outcome, Pipeline_Value |
| `Opportunity` | Sales pipeline / cross-sell opportunity | medium | Opportunity_ID, Account_ID, Product, Amount, Stage (Prospect/Qualified/Proposed/Won/Lost), Close_Date, Advisor_ID |
| `Campaign` | Marketing campaign for customer outreach | low | Campaign_ID, Name, Type (Cross_Sell/Retention/Acquisition/Re_Engagement), Target_Segment, Start_Date, End_Date, Budget, Conversion_Rate |

**Key Relationships:**

- `SF_Account` --syncs_to--> `Customer_Master` (bidirectional via cbs-sfsc-sync)
- `Advisory_Interaction` --depends_on--> `SF_Account`
- `Opportunity` --depends_on--> `SF_Account`
- `Campaign` --triggers--> Revenue Product Recommendation workflow
- `Opportunity` --constrained_by--> conduct-risk (suitability)

---

## Domain 12: Operational Risk & Audit

**System:** All Systems + Document Management | **Basel:** Pillar 1 (OpRisk)

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Loss_Event` | Operational loss event per Basel taxonomy | high | Event_ID, Basel_Category (Internal_Fraud/External_Fraud/Employment/Clients_Products/Physical_Assets/Business_Disruption/Execution_Delivery), Amount, Date, Business_Unit, Root_Cause, Status (Open/Investigated/Closed), Recovery_Amount |
| `Control_Test` | Internal control testing record | medium | Test_ID, Control_ID, Risk_ID, Test_Result (Effective/Partially_Effective/Ineffective), Tester_ID, Test_Date, Next_Test_Date, Findings |
| `Process_Event_Log` | System event log for process mining | low | Event_ID, Case_ID, Activity, Timestamp, User_ID, System (CBS/LOS/SFSC), Status, Duration_Seconds |
| `Incident_Record` | Operational incident (system failure, error, breach) | high | Incident_ID, Category (System_Outage/Processing_Error/Cyber_Event/Vendor_Failure/Data_Breach), Severity (Low/Medium/High/Critical), Start_Time, Resolution_Time, Affected_Systems, Root_Cause, Impact_Description |
| `Audit_Finding` | Internal/external audit finding | high | Finding_ID, Audit_Type (Internal/External/Regulatory), Severity (Low/Medium/High/Critical), Area, Description, Recommendation, Owner, Due_Date, Status (Open/In_Progress/Closed/Overdue) |

**Key Relationships:**

- `Loss_Event` --triggers--> RCSA and KRI Analysis workflow
- `Loss_Event` --constrained_by--> operational-risk-policy
- `Control_Test` --constrained_by--> operational-risk-policy
- `Process_Event_Log` --triggers--> Process Mining workflow
- `Incident_Record` --triggers--> Root Cause Analysis workflow
- `Audit_Finding` --depends_on--> `Compliance_Report`

---

[← Back to Ontology Overview](index.md)
