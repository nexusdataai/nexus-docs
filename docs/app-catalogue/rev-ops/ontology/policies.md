# Policies

6 governance policies that constrain entity operations, workflow execution, and business rules across the Rev-Ops ontology. Each policy is defined in `enterprise-knowledge/policies/` as a Markdown file.

---

## Policy Summary

| # | Policy | ID | Framework | Risk | Owner | Constrains |
|---|--------|----|-----------|------|-------|------------|
| 1 | [Deal Qualification Policy](#1-deal-qualification-policy) | POL-DEAL-001 | MEDDPICC | High | VP Sales / CRO | Deal_Opportunity, Stage_History, Stakeholder_Map, Forecast_Submission |
| 2 | [Revenue Recognition Policy](#2-revenue-recognition-policy) | POL-REV-001 | ASC 606 / IFRS 15 | Critical | CFO / Controller | Revenue_Schedule, Contract_Record, Billing_Schedule, Subscription |
| 3 | [Forecast Governance Policy](#3-forecast-governance-policy) | POL-FCST-001 | SaaS Metrics | High | CRO / VP RevOps | Forecast_Submission, Deal_Opportunity, Pipeline_Snapshot |
| 4 | [Pricing & Discount Policy](#4-pricing--discount-policy) | POL-PRICE-001 | SaaS Metrics | High | CFO / VP RevOps | Quote, Deal_Opportunity, Opportunity_Line_Item, Product_Catalog |
| 5 | [Data Freshness Policy](#5-data-freshness-policy) | POL-DATA-001 | SaaS Metrics | Medium | VP RevOps / CDO | All integration feeds |
| 6 | [Commission & Compensation Policy](#6-commission--compensation-policy) | POL-COMP-001 | SaaS Metrics | High | VP RevOps / CFO | Commission_Record, Quota, Deal_Opportunity, Subscription |

---

## 1. Deal Qualification Policy

**ID:** POL-DEAL-001 | **Framework:** MEDDPICC | **Systems:** Salesforce CRM, Gong

| Rule Area | Key Rules |
|-----------|-----------|
| **MEDDPICC Score Gate** | MEDDPICC score >40 required for Stage 3+ progression; deals below threshold blocked from advancing |
| **Economic Buyer** | Economic Buyer identified by Stage 4 (mandatory); deal cannot progress to Stage 5 without documented Economic Buyer contact |
| **Champion Validation** | Champion validated (not just named) by Stage 3; validation = at least 1 recorded interaction confirming internal advocacy |
| **Multi-threading** | Minimum 3 contacts engaged for deals >$100K; measured via email/meeting/call activity across unique contacts |
| **Deal Amount Changes** | Deal amount change >20% requires manager approval; automated hold placed on stage progression until approved |
| **Stage Integrity** | Stage regression allowed (no stage skipping forward); forward progression must be sequential |
| **Forecast Commit Gate** | Forecast category Commit requires MEDDPICC >70 + signed proposal on file |

---

## 2. Revenue Recognition Policy

**ID:** POL-REV-001 | **Framework:** ASC 606 / IFRS 15 | **Systems:** Oracle Finance, Salesforce CRM

| Rule Area | Key Rules |
|-----------|-----------|
| **ASC 606 Five-Step Gate** | Revenue recognized only when all ASC 606 five-step criteria met; no exceptions |
| **Contract Execution** | Contract must be executed (not verbal); verbal commitments do not constitute a contract for recognition purposes |
| **Performance Obligations** | Performance obligations identified and allocated per contract; each obligation tracked independently |
| **Multi-Element Arrangements** | Multi-element arrangements: standalone selling price allocation required; residual method prohibited |
| **Usage-Based Revenue** | Usage-based revenue: recognized as consumed; metered at billing cycle or monthly, whichever is shorter |
| **Professional Services** | Professional services: recognized over time (percentage of completion method); milestones must be objectively measurable |
| **License Revenue** | License revenue: point-in-time recognition at delivery; delivery = customer access enabled |
| **Contingent Deals** | No revenue recognized on contingent deals until contingency resolved; contingent amounts held in deferred revenue |

---

## 3. Forecast Governance Policy

**ID:** POL-FCST-001 | **Framework:** SaaS Metrics | **Systems:** Salesforce CRM, Internal

| Rule Area | Key Rules |
|-----------|-----------|
| **Submission Cadence** | Weekly forecast submission mandatory for all quota-carrying reps; submissions due by Friday 5 PM local |
| **Commit Category** | Commit: >80% close probability + active engagement in last 7 days; active engagement = email/call/meeting logged |
| **Best Case** | Best Case: 50-80% probability; requires at least one recent (14-day) interaction |
| **Pipeline** | Pipeline: <50% probability; included for coverage analysis but excluded from commit/best case rollups |
| **Manager Override** | Forecast override by manager requires documented justification; justification visible to CRO in rollup |
| **AI Variance Review** | AI forecast vs. rep forecast variance >20% triggers mandatory review; review must be completed before forecast lock |
| **Quarter-End Lock** | Quarter-end forecast lock: 5 business days before quarter close; no changes after lock without CRO approval |
| **Sandbagging Detection** | Sandbagging detection: deals repeatedly pushed then pulled into commit flagged; pattern = 2+ push-pull cycles in same quarter |

---

## 4. Pricing & Discount Policy

**ID:** POL-PRICE-001 | **Framework:** SaaS Metrics | **Systems:** CPQ, Salesforce CRM, Oracle Finance

| Rule Area | Key Rules |
|-----------|-----------|
| **Standard Pricing** | Standard pricing from CPQ price book; all quotes must originate from current published price book |
| **Discount Authority** | 0-10%: AE; 10-20%: Sales Manager; 20-30%: VP Sales; >30%: CRO + CFO joint approval |
| **Multi-Year Discounts** | Multi-year discount max 15% for 2-year, 25% for 3-year; no discounts beyond 3-year without CFO approval |
| **Floor Pricing** | No below-floor pricing; floor = 60% of list price; any exception requires Board-level approval |
| **Payment Terms** | Standard Net 30; Net 60 requires VP Finance approval; no terms beyond Net 90 |
| **Annual Prepay** | Annual prepay discount: 10% of total contract value |
| **Monthly Billing** | Monthly billing premium: 10% markup over annual equivalent |
| **Non-Standard Terms** | All non-standard terms (custom SLAs, liability caps, indemnification) require legal review before execution |

---

## 5. Data Freshness Policy

**ID:** POL-DATA-001 | **Framework:** SaaS Metrics | **Systems:** All

### Structured System SLAs

| Source | Data | SLA |
|--------|------|-----|
| Salesforce CRM | Deal_Opportunity, Account_Profile, Stage_History, Contact | Real-time (<5 min) |
| Gong / Conversation Intelligence | Conversation_Record, Meeting_Action_Item | <4 hours from call end |
| Email & Calendar | Email_Thread, Calendar_Event | Real-time sync |
| Product & Usage Platform | Subscription, Product_Usage | Daily aggregation |
| Oracle Finance | AR_Invoice, Payment, Revenue_Schedule | 15-min sync for AR; daily for GL |
| Market Intelligence (Bombora/6sense/ZoomInfo) | Intent_Data, Competitive_Signal | Daily |

### Unstructured Source SLAs

| Source | Data | SLA |
|--------|------|-----|
| Document Management / CLM | Contract_Record, Quote (PDFs) | On-upload + NLP extraction within 60 min |

### Staleness Rules

- 2x SLA gap: alert Data Engineering
- 3x SLA gap: mark data as stale; exclude from AI workflow inputs; notify RevOps leadership

---

## 6. Commission & Compensation Policy

**ID:** POL-COMP-001 | **Framework:** SaaS Metrics | **Systems:** Commission System, Oracle Finance, Salesforce CRM

| Rule Area | Key Rules |
|-----------|-----------|
| **Commission Basis** | Commission calculated on booked ARR (not TCV unless specified in comp plan) |
| **Collection-Based Payment** | Payment on invoice collection (not booking) for accounts with terms >Net 60 |
| **Accelerators** | Accelerators activate at 100% quota attainment; rates defined per comp plan tier |
| **Clawback** | If customer churns within 12 months, pro-rated clawback applied; clawback = (months remaining / 12) × commission paid |
| **Split Deals** | Split deals: documented agreement between reps required before close; no retroactive splits |
| **Dispute Window** | Dispute window: 30 days from payout statement date; disputes after window closed require VP RevOps escalation |
| **SPIF Programs** | SPIF programs: pre-approved by CRO with defined budget, criteria, and expiration; no open-ended SPIFs |

---

[← Back to Ontology Overview](index.md)
