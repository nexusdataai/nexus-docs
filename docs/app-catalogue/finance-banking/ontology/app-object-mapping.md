# Application-Object Mapping

Minimum required ontology objects per application, with relationship details and cross-application dependency analysis.

---

## App 1: Customer 360 & Relationship Intelligence

**Basel:** Pillar 3 (Conduct) | **Minimum Objects: 12**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Customer_Master` | CBS | Core entity — golden customer record | — |
| `Household` | Internal | Family grouping for TRV calculation | depends_on -> Customer_Master |
| `Deposit_Account` | CBS | Product holdings and balance trends | depends_on -> Customer_Master |
| `Loan_Account` | LOS/CBS | Lending relationship and performance | depends_on -> Customer_Master |
| `Transaction_Ledger` | CBS | Transaction patterns for behavioral analysis | depends_on -> Deposit_Account |
| `SF_Account` | Salesforce FSC | CRM profile, RM assignment | syncs_to -> Customer_Master |
| `SF_Financial_Account` | Salesforce FSC | Salesforce view of product holdings | depends_on -> SF_Account |
| `Advisory_Interaction` | Salesforce FSC | Advisor notes and interaction history | depends_on -> SF_Account |
| `Opportunity` | Salesforce FSC | Cross-sell pipeline | depends_on -> SF_Account |
| `Credit_Score` | Internal | Risk context for customer profile | depends_on -> Customer_Master |
| `AML_Alert` | AML System | Risk flags for customer profile | depends_on -> Customer_Master |
| `KYC_Document` | DMS | Compliance status for profile | validates -> Customer_Master |

**Policies:** customer-relationship-policy, aml-kyc-policy
**Workflows:** customer-360-nba
**Integrations:** cbs-sfsc-sync

---

## App 2: Credit Risk & Early Warning System

**Basel:** Pillar 1 (IRB) / IFRS 9 | **Minimum Objects: 12**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Customer_Master` | CBS | Borrower identity | — |
| `Loan_Account` | LOS/CBS | Credit exposure master | depends_on -> Customer_Master |
| `Repayment_Schedule` | CBS | Payment behavior tracking | depends_on -> Loan_Account |
| `Collateral` | LOS | Security for recovery estimation | depends_on -> Loan_Account |
| `Credit_Score` | Internal | Composite risk score (bureau + behavioral) | depends_on -> Customer_Master |
| `ECL_Staging` | Internal | IFRS 9 stage and ECL per exposure | depends_on -> Loan_Account, Credit_Score |
| `EWS_Signal` | Internal | Early warning indicators | depends_on -> Customer_Master |
| `Risk_Rating` | Internal | Internal rating (1-22 scale) | depends_on -> Customer_Master |
| `Deposit_Account` | CBS | Linked account balance trends for EWS | depends_on -> Customer_Master |
| `Macro_Indicator` | Market Data | Forward-looking macro overlay for ECL | — |
| `Sector_Index` | Market Data | Sector stress signals | — |
| `Relationship_Group` | Internal | Concentration risk (group exposure) | depends_on -> Customer_Master |

**Policies:** credit-risk-policy, capital-adequacy-policy
**Workflows:** credit-ews, ecl-calculation
**Integrations:** cbs-los-sync, market-data-feed

---

## App 3: Fraud Detection & AML Intelligence

**FATF / FinCEN | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Customer_Master` | CBS | Entity under investigation | — |
| `Transaction_Ledger` | CBS | Transaction data for anomaly detection | depends_on -> Customer_Master |
| `Card_Transaction` | CBS | Card fraud detection | depends_on -> Customer_Master |
| `Transaction_Pattern` | Internal | Behavioral baseline for anomaly scoring | depends_on -> Customer_Master |
| `AML_Alert` | AML System | Alert from transaction monitoring | depends_on -> Customer_Master |
| `SAR_Filing` | AML System | Suspicious activity report | depends_on -> AML_Alert |
| `Watchlist_Match` | AML System | Sanctions/PEP screening result | depends_on -> Customer_Master |
| `KYC_Document` | DMS | Customer due diligence status | validates -> Customer_Master |
| `Relationship_Group` | Internal | Network analysis for laundering detection | depends_on -> Customer_Master |
| `Interbank_Transaction` | CBS | Interbank flow for network analysis | — |

**Policies:** aml-kyc-policy
**Workflows:** transaction-anomaly-detection, sar-generation
**Integrations:** cbs-aml-sync, unstructured-extraction

---

## App 4: Regulatory Compliance & Reporting

**Basel:** All Pillars / BCBS 239 | **Minimum Objects: 12**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Capital_Component` | Internal | CET1, AT1, Tier 2 components | — |
| `RWA_Calculation` | Internal | Risk-weighted assets by risk type | depends_on -> Loan_Account, Investment_Holding |
| `Provision_Record` | Internal | ECL provisions for IFRS 9 reporting | depends_on -> ECL_Staging |
| `Regulatory_Return` | Internal | Filing status and submission tracking | — |
| `Regulatory_Circular` | Regulatory Feeds | Change intelligence and impact assessment | — |
| `Loan_Account` | LOS/CBS | Credit exposure for RWA | depends_on -> Customer_Master |
| `Investment_Holding` | CBS/Treasury | Market risk positions | — |
| `Liquidity_Position` | CBS/Treasury | LCR/NSFR for liquidity reporting | — |
| `Loss_Event` | Internal | Operational risk data for OpRisk RWA | — |
| `AML_Alert` | AML System | AML metrics for regulatory reporting | depends_on -> Customer_Master |
| `SAR_Filing` | AML System | SAR filing metrics | depends_on -> AML_Alert |
| `Collateral` | LOS | Collateral for LGD in RWA calculation | depends_on -> Loan_Account |

**Policies:** capital-adequacy-policy, data-freshness-policy
**Workflows:** capital-adequacy-calculation, regulatory-return-generation
**Integrations:** market-data-feed, regulatory-feed

---

## App 5: Treasury & Liquidity Optimization

**Basel:** Liquidity (LCR/NSFR) | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Balance_Sheet_Position` | CBS/Treasury | Aggregated balance sheet line items | — |
| `Deposit_Account` | CBS | Deposit base for cash flow and LCR | depends_on -> Customer_Master |
| `Fixed_Deposit` | CBS | Term deposits with maturity schedule | depends_on -> Customer_Master |
| `Loan_Account` | LOS/CBS | Lending side of balance sheet | depends_on -> Customer_Master |
| `Investment_Holding` | CBS/Treasury | HQLA portfolio and investment book | — |
| `Liquidity_Position` | Internal | Daily LCR/NSFR tracking | — |
| `FTP_Rate` | Internal | Fund transfer pricing rates | depends_on -> Yield_Curve |
| `Yield_Curve` | Market Data | Interest rate curves for ALM and FTP | — |
| `Interbank_Transaction` | CBS | Interbank positions | — |
| `Opportunity` | Salesforce FSC | Business pipeline for cash flow forecasting | depends_on -> SF_Account |

**Policies:** treasury-liquidity-policy, capital-adequacy-policy
**Workflows:** cash-flow-alm
**Integrations:** cbs-sfsc-sync, market-data-feed

---

## App 6: Loan Lifecycle Intelligence

**Basel:** Pillar 1 (Credit) | **Minimum Objects: 11**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Loan_Application` | LOS | Origination pipeline tracking | depends_on -> Customer_Master |
| `Loan_Account` | LOS/CBS | Active loan master | depends_on -> Customer_Master |
| `Repayment_Schedule` | CBS | Payment schedule and history | depends_on -> Loan_Account |
| `Collateral` | LOS | Collateral value and LTV monitoring | depends_on -> Loan_Account |
| `Guarantor` | LOS | Guarantee coverage | depends_on -> Loan_Account |
| `Loan_Document` | DMS | Supporting documents (OCR+LLM extracted) | depends_on -> Loan_Application |
| `Customer_Master` | CBS | Borrower profile and identity | — |
| `Credit_Score` | Internal | Credit decision input | depends_on -> Customer_Master |
| `KYC_Document` | DMS | KYC verification for origination | validates -> Customer_Master |
| `Commodity_Price` | Market Data | Collateral market value (gold, property indices) | — |
| `SF_Financial_Account` | Salesforce FSC | Advisor view of loan | depends_on -> SF_Account |

**Policies:** lending-policy, collections-recovery-policy, aml-kyc-policy
**Workflows:** loan-origination, collections-prioritization
**Integrations:** cbs-los-sync, unstructured-extraction

---

## App 7: Revenue & Product Recommendation

**Basel:** Pillar 3 (Conduct) | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Customer_Master` | CBS | Customer profile and segmentation | — |
| `Deposit_Account` | CBS | Product holding (deposit side) | depends_on -> Customer_Master |
| `Loan_Account` | LOS/CBS | Product holding (lending side) | depends_on -> Customer_Master |
| `Transaction_Ledger` | CBS | Transaction patterns for life-stage detection | depends_on -> Customer_Master |
| `Credit_Score` | Internal | Risk context for pricing | depends_on -> Customer_Master |
| `SF_Account` | Salesforce FSC | CRM profile for campaign targeting | syncs_to -> Customer_Master |
| `Advisory_Interaction` | Salesforce FSC | Interaction history for offer timing | depends_on -> SF_Account |
| `Opportunity` | Salesforce FSC | Cross-sell pipeline tracking | depends_on -> SF_Account |
| `Campaign` | Salesforce FSC | Campaign execution and attribution | — |
| `Yield_Curve` | Market Data | Competitive rate benchmarking | — |

**Policies:** customer-relationship-policy, lending-policy
**Workflows:** customer-360-nba
**Integrations:** cbs-sfsc-sync, market-data-feed

---

## App 8: Operational Risk & Process Mining

**Basel:** Pillar 1 (OpRisk) | **Minimum Objects: 9**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Loss_Event` | Internal | Operational loss tracking per Basel taxonomy | — |
| `Control_Test` | Internal | Control effectiveness testing | — |
| `Process_Event_Log` | CBS/LOS/SFSC | System event logs for process mining | — |
| `Incident_Record` | Internal | Operational incident tracking | — |
| `Audit_Finding` | DMS | Internal/external audit findings | depends_on -> Compliance_Report |
| `Compliance_Report` | DMS | Audit and compliance reports (NLP-extracted) | — |
| `Customer_Master` | CBS | Context for customer-impacting incidents | — |
| `Transaction_Ledger` | CBS | Transaction logs for process conformance | depends_on -> Customer_Master |
| `Deposit_Account` | CBS | Account operations for process mining | depends_on -> Customer_Master |

**Policies:** operational-risk-policy, data-freshness-policy
**Workflows:** process-mining-rca, rcsa-kri-analysis (shared from capital adequacy)
**Integrations:** All system integrations (event log collection)

---

## Cross-Application Dependency Matrix

Shows which entities are shared across applications (checkmark = required by that app):

| Entity | Cust 360 | Credit Risk | Fraud/AML | Regulatory | Treasury | Loan Lifecycle | Revenue | OpRisk |
|--------|----------|-------------|-----------|------------|----------|---------------|---------|--------|
| **Customer_Master** | x | x | x | — | — | x | x | x |
| **Deposit_Account** | x | x | — | — | x | — | x | x |
| **Loan_Account** | x | x | — | x | x | x | x | — |
| **Transaction_Ledger** | x | — | x | — | — | — | x | x |
| **Credit_Score** | x | x | — | — | — | x | x | — |
| **SF_Account** | x | — | — | — | — | — | x | — |
| **AML_Alert** | x | — | x | x | — | — | — | — |
| **Collateral** | — | x | — | x | — | x | — | — |
| **Investment_Holding** | — | — | — | x | x | — | — | — |
| **Yield_Curve** | — | — | — | — | x | — | x | — |
| **ECL_Staging** | — | x | — | x | — | — | — | — |
| **Capital_Component** | — | — | — | x | x | — | — | — |
| **Loss_Event** | — | — | — | x | — | — | — | x |
| **KYC_Document** | x | — | x | — | — | x | — | — |

---

## Entity Count per App

| Application | Min Objects | Workflows | Policies | Integrations |
|------------|-----------|-----------|----------|--------------|
| Customer 360 | 12 | 1 | 2 | 1 |
| Credit Risk & EWS | 12 | 2 | 2 | 2 |
| Fraud & AML | 10 | 2 | 1 | 2 |
| Regulatory Compliance | 12 | 2 | 2 | 2 |
| Treasury & Liquidity | 10 | 1 | 2 | 2 |
| Loan Lifecycle | 11 | 2 | 3 | 2 |
| Revenue & Product | 10 | 1 | 2 | 2 |
| Operational Risk | 9 | 1 | 2 | 6 (all) |

---

[← Back to Ontology Overview](index.md)
