# Policies

8 governance policies that constrain entity operations, workflow execution, and business rules across the finance & banking ontology. Each policy is defined in `enterprise-knowledge/policies/` as a Markdown file.

---

## Policy Summary

| # | Policy | ID | Basel/Regulatory | Risk | Owner | Constrains |
|---|--------|----|-----------------|------|-------|------------|
| 1 | [Credit Risk Policy](#1-credit-risk-policy) | POL-CR-001 | Pillar 1 (IRB) / IFRS 9 | Critical | Chief Risk Officer | Loan_Account, Credit_Score, ECL_Staging, Risk_Rating |
| 2 | [AML & KYC Policy](#2-aml-kyc-policy) | POL-AML-001 | FATF / FinCEN | Critical | MLRO (Money Laundering Reporting Officer) | Customer_Master, AML_Alert, SAR_Filing, KYC_Document |
| 3 | [Capital Adequacy Policy](#3-capital-adequacy-policy) | POL-CAP-001 | Basel III/IV Pillar 1 | Critical | CFO / CRO | Capital_Component, RWA_Calculation, Regulatory_Return |
| 4 | [Lending Policy](#4-lending-policy) | POL-LEND-001 | Pillar 1 (Credit) | High | Head of Credit | Loan_Application, Loan_Account, Collateral, Guarantor |
| 5 | [Collections & Recovery Policy](#5-collections-recovery-policy) | POL-COLL-001 | Pillar 1 (Credit) | High | Head of Collections | Loan_Account, Repayment_Schedule, Collateral |
| 6 | [Treasury & Liquidity Policy](#6-treasury-liquidity-policy) | POL-TREAS-001 | Basel Liquidity (LCR/NSFR) | High | Treasurer / ALCO | Investment_Holding, Liquidity_Position, FTP_Rate |
| 7 | [Data Freshness Policy](#7-data-freshness-policy) | POL-DATA-001 | BCBS 239 | Medium | Chief Data Officer | All integration feeds |
| 8 | [Operational Risk Policy](#8-operational-risk-policy) | POL-OPRISK-001 | Basel Pillar 1 (OpRisk) | High | Head of Operational Risk | Loss_Event, Control_Test, Incident_Record |

---

## 1. Credit Risk Policy

**ID:** POL-CR-001 | **Basel:** Pillar 1 (IRB) / IFRS 9 | **Systems:** LOS, CBS

| Rule Area | Key Rules |
|-----------|-----------|
| **Risk Rating** | All borrowers rated on 1-22 internal scale; annual review mandatory; downgrade ≥2 notches triggers SICR and immediate ECL recalculation |
| **Concentration Limits** | Single borrower: max 15% of Tier 1 capital; Single sector: max 25% of total exposure; Top 10 borrowers: max 15% of total book |
| **EWS Thresholds** | Red: 3+ signals simultaneously → credit committee escalation; Amber: 1-2 signals → RM notification; Green: monitored |
| **SICR Triggers** | DPD >30 days; Rating downgrade ≥2 notches; Restructured; Watchlist placement; Qualitative assessment by credit officer |
| **ECL Model Governance** | Annual model validation by independent model risk team; back-testing required; regulator/auditor approval before production use |
| **Collateral Revaluation** | Property: annual minimum, on LTV breach; Securities: daily mark-to-market; Gold: monthly; Vehicle: annual or on total loss |
| **Write-Off** | NPAs >3 years with exhausted recovery: recommend write-off; requires CRO + Board approval for >$1M |

---

## 2. AML & KYC Policy

**ID:** POL-AML-001 | **Regulatory:** FATF / FinCEN / Local Regulator | **Systems:** AML, CBS, DMS

| Rule Area | Key Rules |
|-----------|-----------|
| **CDD Tiers** | Simplified: low-risk, small accounts; Standard: all regular customers; Enhanced: PEP, high-risk country, unusual activity, >$1M relationship |
| **KYC Renewal** | Low risk: every 5 years; Medium: every 3 years; High: annually; Expired KYC: freeze high-risk transactions, notify RM |
| **Transaction Monitoring** | All transactions scored in real-time; thresholds per customer risk rating; structuring detection on multiple sub-threshold transactions |
| **Sanctions Screening** | All customers screened on onboarding and daily against OFAC, EU, UN, local lists; match score >85%: mandatory manual review within 4 hours |
| **SAR Filing** | Decision within 30 days of alert; filing within 30 days of decision; continuing SARs every 90 days for ongoing activity |
| **PEP Management** | PEP accounts require Senior Management approval; enhanced monitoring; annual review by compliance |
| **Record Retention** | All CDD records: 5 years after relationship ends; SAR records: 5 years after filing; transaction records: 7 years |

---

## 3. Capital Adequacy Policy

**ID:** POL-CAP-001 | **Basel:** III/IV Pillar 1 | **Systems:** All

| Rule Area | Key Rules |
|-----------|-----------|
| **Minimum Ratios** | CET1: ≥8.0% (regulatory 4.5% + CCB 2.5% + internal buffer 1.0%); Tier 1: ≥10.0%; Total Capital: ≥12.5% |
| **Buffer Triggers** | CET1 within 100 bps of minimum: restrict dividends; within 50 bps: suspend share buybacks + activate capital conservation plan |
| **RWA Methodology** | Credit: Standardized Approach (default), IRB Foundation (with regulatory approval); Market: FRTB-SA; OpRisk: Standardized Approach |
| **Stress Testing** | Quarterly internal stress tests; annual regulatory prescribed scenarios; results presented to ALCO and Board |
| **Capital Planning** | 3-year forward capital plan; updated quarterly; includes dividend capacity, organic growth, and M&A scenarios |
| **Regulatory Reporting** | Capital returns filed within regulatory deadline (T+20 business days); zero tolerance for late filing |
| **Model Risk** | All capital models independently validated annually; material model changes require regulatory notification |

---

## 4. Lending Policy

**ID:** POL-LEND-001 | **Basel:** Pillar 1 (Credit) | **Systems:** LOS, CBS, DMS

| Rule Area | Key Rules |
|-----------|-----------|
| **Approval Authority** | <$100K: Credit Manager auto-approve (within score band); $100K-$1M: Credit Committee; $1M-$10M: Senior Credit Committee; >$10M: Board Credit Committee |
| **LTV Limits** | Home loan: max 80% (90% with mortgage insurance); Auto: max 85%; Commercial property: max 70%; LAP: max 60% |
| **Debt-to-Income** | Retail: max 50% DTI; SME: max DSCR 1.25x; Corporate: assessed case-by-case with minimum interest coverage 2.0x |
| **Document Requirements** | Income proof (last 2 years); Bank statements (6 months); ID proof (government-issued); Property docs (for secured); Financial statements (for business) |
| **Pricing** | Risk-based pricing: base rate + credit spread based on risk rating band; minimum margin: 150 bps over cost of funds |
| **Document AI Confidence** | >0.85: auto-populate application data; 0.7-0.85: flag for verification; <0.7: mandatory manual review |
| **Loan Restructuring** | Requires demonstrated financial difficulty; maximum 2 restructurings per loan; tenor extension ≤50% of original; triggers Stage 2 classification |

---

## 5. Collections & Recovery Policy

**ID:** POL-COLL-001 | **Basel:** Pillar 1 (Credit) | **Systems:** CBS, LOS

| Rule Area | Key Rules |
|-----------|-----------|
| **Contact Strategy** | 1-30 DPD: automated SMS/email reminders; 31-60 DPD: outbound call campaign; 61-90 DPD: field visit + restructuring offer; 90+: legal notice |
| **Recovery Prioritization** | Score-based: recovery probability × amount at risk; self-cure predictions excluded from active contact |
| **Restructuring Authority** | Rate reduction: Branch Manager; Tenor extension: Credit Manager; Principal waiver <5%: Collections Head; >5%: Credit Committee |
| **NPA Classification** | 90+ DPD: NPA classification mandatory; sub-standard: up to 12 months NPA; doubtful: 12-36 months NPA; loss: >36 months NPA |
| **Provisioning Alignment** | Collections outcomes feed back into LGD models and ECL calculations; recovery data used for backtesting |
| **Legal Action** | Initiated at 120 DPD for unsecured (>$10K); 180 DPD for secured; requires legal department approval |
| **Write-Off Criteria** | All recovery avenues exhausted; >3 years NPA; legal proceedings concluded; requires CRO approval |

---

## 6. Treasury & Liquidity Policy

**ID:** POL-TREAS-001 | **Basel:** Liquidity (LCR/NSFR) | **Systems:** CBS, Market Data

| Rule Area | Key Rules |
|-----------|-----------|
| **LCR Target** | Minimum 110% (regulatory 100% + 10% internal buffer); breach of 105%: alert Treasurer; breach of 100%: emergency ALCO |
| **NSFR Target** | Minimum 105% (regulatory 100% + 5% buffer) |
| **HQLA Composition** | Level 1 assets: ≥60% of HQLA stock; Level 2A: ≤40%; Level 2B: ≤15%; geographic and issuer diversification required |
| **Duration Gap** | Board-approved limit: ≤2.0 years; trigger for hedging review at ≥1.5 years |
| **NII Sensitivity** | ±200 bps rate shock impact must be ≤10% of trailing 12-month NII; exceed: hedge within 5 business days |
| **Interbank Limits** | Single counterparty: max 5% of total assets; aggregate interbank borrowing: max 20% of total liabilities |
| **FTP Methodology** | Matched-maturity approach; rates published daily by close of business; stale rates (>2 days): interim rates from last valid curve |

---

## 7. Data Freshness Policy

**ID:** POL-DATA-001 | **BCBS 239** | **Systems:** All

### Structured System SLAs

| Source | Data | SLA |
|--------|------|-----|
| Core Banking System | Transaction_Ledger, Account balances | Real-time (<1 min for transactions; EOD for positions) |
| Core Banking System | Deposit_Account, Customer_Master | On-change + daily full sync |
| Salesforce FSC | SF_Account, Opportunity, Advisory_Interaction | Near real-time (<5 min) |
| Loan Origination System | Loan_Application, Loan_Account, Repayment_Schedule | Near real-time (<15 min) |
| AML / Transaction Monitoring | AML_Alert, Watchlist_Match | Real-time (alerts); daily (watchlist refresh) |
| Market Data | Yield_Curve, Macro_Indicator, Sector_Index | Intraday for rates; daily for macro |

### Unstructured Source SLAs

| Source | Data | SLA |
|--------|------|-----|
| Document Management | KYC_Document, Loan_Document, Contract_Document | On-upload; processing within 30 min |
| Regulatory Feeds | Regulatory_Circular | Daily scan; critical: immediate |

### Staleness Rules

- 2x SLA gap: alert Data Engineering
- 3x SLA gap: mark data as stale; exclude from AI workflow inputs; notify risk management

---

## 8. Operational Risk Policy

**ID:** POL-OPRISK-001 | **Basel:** Pillar 1 (OpRisk) | **Systems:** All

| Rule Area | Key Rules |
|-----------|-----------|
| **Loss Event Capture** | All operational losses >$1K must be recorded within 5 business days; Basel category classification mandatory |
| **Material Loss Threshold** | Loss >$500K: immediate CRO notification + formal root cause analysis; >$5M: Board notification within 24 hours |
| **RCSA Cycle** | Continuous (AI-assisted pre-population from loss data); formal review quarterly; full assessment annually |
| **Control Testing** | Key controls: quarterly testing; all controls: annual minimum; failed control: remediation plan within 30 days |
| **KRI Thresholds** | Set dynamically based on correlation with historical loss events; breach for 2+ periods: RCSA reassessment |
| **Process Conformance** | Critical processes (account opening, payments, lending): target >85% conformance; below 75%: formal investigation |
| **Incident Management** | Critical: 2-hour response SLA; High: 4-hour; all incidents: root cause within 10 business days; systemic patterns escalated to COO |

---

[← Back to Ontology Overview](index.md)
