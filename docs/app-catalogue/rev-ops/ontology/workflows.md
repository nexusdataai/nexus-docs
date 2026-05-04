# Workflows

8 AI workflows aligned to MEDDPICC and ASC 606 standards that power the revenue operations applications. Each workflow is defined in `enterprise-knowledge/workflows/` as a YAML file with trigger conditions, ordered steps, and entity/policy dependencies.

---

## Workflow Summary

| # | Workflow | Standard | Trigger | Primary App |
|---|---------|----------|---------|-------------|
| 1 | [Deal Intelligence & Scoring](#1-deal-intelligence-scoring) | MEDDPICC | New call recording or daily batch | Deal Intelligence |
| 2 | [Pipeline Risk Assessment](#2-pipeline-risk-assessment) | MEDDPICC/ASC 606 | Weekly snapshot or deal stage change | Pipeline Risk |
| 3 | [Renewal & Expansion Prediction](#3-renewal-expansion-prediction) | ASC 606/SaaS Metrics | 120 days before renewal or usage decline | Pipeline Risk |
| 4 | [Quote-to-Cash Orchestration](#4-quote-to-cash-orchestration) | ASC 606 | Opportunity reaches Closed_Won | Revenue Orchestration |
| 5 | [Revenue Leakage Detection](#5-revenue-leakage-detection) | ASC 606 | Monthly reconciliation or variance detected | Revenue Orchestration |
| 6 | [Conversation & Email NLP](#6-conversation-email-nlp) | MEDDPICC | New call recording or email thread updated | Deal Intelligence |
| 7 | [Commission & Compensation](#7-commission-compensation) | — | Deal closed-won or monthly payout cycle | Revenue Orchestration |
| 8 | [Competitive Win/Loss Analysis](#8-competitive-winloss-analysis) | MEDDPICC | Deal closed (won or lost) or quarterly batch | Deal Intelligence, Pipeline Risk |

---

## 1. Deal Intelligence & Scoring

**ID:** `WORKFLOW_DEAL_INTELLIGENCE_V1_0` | **Standard:** MEDDPICC | **File:** `deal-intelligence-scoring.yaml`

**Trigger:** New call recording ingested OR daily batch (06:00 UTC)

| Step | System | Action |
|------|--------|--------|
| 1. Deal Context Assembly | Salesforce | Pull Deal_Opportunity, Stakeholder_Map, Stage_History, Opportunity_Line_Item for target deal |
| 2. Conversation NLP | Internal | Extract MEDDPICC elements from Conversation_Record; score each dimension (Metrics/Economic_Buyer/Decision_Criteria/Decision_Process/Identify_Pain/Champion) |
| 3. Email Engagement Scoring | Internal | Analyze Email_Thread response times, executive involvement, ghost risk; score engagement health |
| 4. Product-Fit Analysis | Internal | Match Opportunity_Line_Item against Account_Profile ICP_Score and Product_Usage patterns |
| 5. Competitive Intelligence | Internal | Aggregate Competitive_Signal and Intent_Data; calculate threat score per competitor |
| 6. Composite Deal Scoring | Internal | Weighted composite: MEDDPICC (40%) + Engagement (20%) + Product-Fit (15%) + Competitive (15%) + Velocity (10%) |
| 7. Push to Salesforce | Salesforce | Update Deal_Opportunity MEDDPICC_Score, Forecast_Category; create alerts for at-risk deals |

**Dependencies:** Deal_Opportunity, Opportunity_Line_Item, Stage_History, Stakeholder_Map, Account_Profile, Contact, Conversation_Record, Email_Thread, Calendar_Event, Product_Usage, Competitive_Signal, Intent_Data

---

## 2. Pipeline Risk Assessment

**ID:** `WORKFLOW_PIPELINE_RISK_V1_0` | **Standard:** MEDDPICC/ASC 606 | **File:** `pipeline-risk-assessment.yaml`

**Trigger:** Weekly snapshot (Sunday 23:00 UTC) OR Deal_Opportunity Stage change event

| Step | System | Action |
|------|--------|--------|
| 1. Pipeline Snapshot Generation | Internal | Capture point-in-time Pipeline_Snapshot by Segment x Stage; calculate week-over-week delta |
| 2. Deal Velocity Analysis | Internal | Calculate Deal_Velocity per deal; flag deals exceeding 2x median stage duration |
| 3. Stage Inflation Detection | Internal | Compare MEDDPICC_Score against Stage; flag deals where score <40 but Stage ≥ Negotiation |
| 4. Concentration Risk Analysis | Internal | Flag segments where top 3 deals >60% of pipeline or single Account >30% |
| 5. Coverage Health Calculation | Internal | Calculate weighted pipeline coverage ratio vs quota by Segment; flag <3x coverage |
| 6. AI Forecast Generation | Internal | Generate Forecast_Submission AI_Forecast_Amount using deal scores, velocity, and historical conversion |
| 7. Variance Reporting | Internal | Compare AI_Forecast_Amount vs rep Commit_Amount; flag Variance_Pct >15% for review |

**Dependencies:** Deal_Opportunity, Stage_History, Pipeline_Snapshot, Deal_Velocity, Forecast_Submission, Quota, Account_Profile, Stakeholder_Map, MEDDPICC scoring methodology

---

## 3. Renewal & Expansion Prediction

**ID:** `WORKFLOW_RENEWAL_PREDICTION_V1_0` | **Standard:** ASC 606/SaaS Metrics | **File:** `renewal-expansion-prediction.yaml`

**Trigger:** Subscription renewal date within 120 days OR Product_Usage Usage_Trend = Declining detected

| Step | System | Action |
|------|--------|--------|
| 1. Customer Health Scoring | Internal | Aggregate Product_Usage (adoption + trend), support ticket history, NPS/CSAT, AR_Invoice payment timeliness into composite health score |
| 2. Renewal Probability | Internal | Predict Renewal_Record Predicted_Outcome using gradient-boosted model on health score, NDR history, tenure, segment |
| 3. Expansion Signal Detection | Internal | Identify accounts with Usage_Pct >80%, growing DAU/MAU, or Intent_Data on adjacent products |
| 4. Downsell/Churn Risk Identification | Internal | Flag accounts with declining usage, overdue invoices, champion departure, or competitor intent signals |
| 5. Proactive Intervention Matching | Internal | Map risk drivers to optimal action: executive sponsor call, QBR acceleration, usage enablement, pricing review |
| 6. Push Renewal Tasks to CSM | Salesforce | Create Renewal_Record; assign tasks to CSM with priority and recommended playbook |

**Dependencies:** Subscription, Product_Usage, Account_Profile, AR_Invoice, Payment, Renewal_Record, Intent_Data, Contact, Stakeholder_Map, Digital_Engagement

---

## 4. Quote-to-Cash Orchestration

**ID:** `WORKFLOW_QUOTE_TO_CASH_V1_0` | **Standard:** ASC 606 | **File:** `quote-to-cash.yaml`

**Trigger:** Deal_Opportunity Stage changes to Closed_Won

| Step | System | Action |
|------|--------|--------|
| 1. Quote Validation | Salesforce | Validate Quote approval status, expiry, discount thresholds; reject if non-compliant |
| 2. Contract NLP Extraction | Internal | Extract Contract_Record terms via NLP: performance obligations, payment terms, ramp schedule; assign Extraction_Confidence |
| 3. Billing Schedule Creation | Oracle | Generate Billing_Schedule from contract terms; handle monthly/annual/usage-based frequencies |
| 4. Revenue Schedule Generation | Oracle | Create Revenue_Schedule per ASC 606: allocate transaction price to performance obligations; set Recognition_Method (Over_Time/Point_in_Time) |
| 5. Commission Calculation | Oracle | Trigger Commission_Record creation; apply Comp_Plan rates and Quota accelerators |
| 6. Provisioning Trigger | Product Platform | Activate Subscription record; provision product access and entitlements |
| 7. Status Sync to CRM | Salesforce | Update Deal_Opportunity with Contract_ID, Subscription status; close workflow loop |

**Dependencies:** Deal_Opportunity, Quote, Contract_Record, Opportunity_Line_Item, Product_Catalog, Billing_Schedule, Revenue_Schedule, Commission_Record, Comp_Plan, Subscription, ASC 606 recognition rules

---

## 5. Revenue Leakage Detection

**ID:** `WORKFLOW_REVENUE_LEAKAGE_V1_0` | **Standard:** ASC 606 | **File:** `revenue-leakage-detection.yaml`

**Trigger:** Monthly reconciliation (3rd business day) OR Revenue_Schedule vs AR_Invoice variance >5% detected

| Step | System | Action |
|------|--------|--------|
| 1. CRM Bookings vs Billing Reconciliation | Internal | Match Deal_Opportunity Closed_Won amounts against Billing_Schedule totals; flag unmatched bookings |
| 2. Billing vs Collections Reconciliation | Internal | Match Billing_Schedule against AR_Invoice and Payment; flag unbilled periods and unapplied payments |
| 3. Unbilled Subscription Detection | Internal | Scan active Subscriptions without corresponding Billing_Schedule entries; quantify revenue gap |
| 4. Pricing Discrepancy Detection | Internal | Compare Opportunity_Line_Item Unit_Price against Product_Catalog List_Price and Contract_Record terms; flag unapproved discounts |
| 5. Unapplied Payment Matching | Oracle | Match orphan Payments to open AR_Invoices using amount, date, and account heuristics |
| 6. Leakage Quantification and Root Cause | Internal | Aggregate leakage by category (unbilled/mispriced/unapplied/uncollected); classify root cause; generate remediation queue |

**Dependencies:** Deal_Opportunity, Contract_Record, Billing_Schedule, Revenue_Schedule, AR_Invoice, Payment, Subscription, Opportunity_Line_Item, Product_Catalog, Account_Profile, ASC 606 recognition rules

---

## 6. Conversation & Email NLP

**ID:** `WORKFLOW_CONVERSATION_NLP_V1_0` | **Standard:** MEDDPICC | **File:** `conversation-email-nlp.yaml`

**Trigger:** New call recording uploaded to Conversation_Record OR Email_Thread updated with new messages

| Step | System | Action |
|------|--------|--------|
| 1. Speech-to-Text Transcription | Internal | Transcribe call recording; generate speaker-diarized transcript; store Transcript_URL |
| 2. MEDDPICC Element Extraction | Internal | NLP extraction of Metrics, Economic Buyer mentions, Decision Criteria, Decision Process, Identified Pain, Champion signals |
| 3. Competitor Mention Detection | Internal | Identify and classify Competitor_Mentions from transcript and email body; create Competitive_Signal records |
| 4. Objection Classification | Internal | Classify Objections_Raised into categories: Price, Product_Gap, Timing, Competitor, Internal_Politics, Status_Quo |
| 5. Sentiment Scoring | Internal | Calculate Sentiment_Score per participant and overall; track sentiment trend across deal lifecycle |
| 6. Next-Step Extraction | Internal | Extract Next_Steps_Committed and generate Meeting_Action_Item records with owners and due dates |
| 7. Topic Detection | Internal | Classify Topics_Detected from taxonomy: Pricing, Technical, Legal, Security, Integration, Timeline, ROI |
| 8. Enrich Deal Record | Salesforce | Update Deal_Opportunity with extracted MEDDPICC elements, sentiment, competitor flags; update Stakeholder_Map engagement levels |

**Dependencies:** Conversation_Record, Email_Thread, Deal_Opportunity, Stakeholder_Map, Contact, Meeting_Action_Item, Competitive_Signal, Account_Profile

---

## 7. Commission & Compensation

**ID:** `WORKFLOW_COMMISSION_COMP_V1_0` | **File:** `commission-compensation.yaml`

**Trigger:** Deal_Opportunity reaches Closed_Won OR monthly payout cycle (last business day)

| Step | System | Action |
|------|--------|--------|
| 1. Match CRM Closed-Won to Comp Plan | Internal | Resolve Rep_ID from Deal_Opportunity Owner_ID; match to active Comp_Plan and Quota |
| 2. Apply Commission Rate and Accelerators | Internal | Calculate Commission_Amount from Booking_Amount x Commission_Rate; apply Accelerator if Attainment_Pct > Accelerator_Threshold |
| 3. Handle Splits and Overlays | Internal | Process multi-rep deals: split commission by contribution; apply overlay rates for SEs, managers |
| 4. Generate Payout Schedule | Oracle | Create Commission_Record with Pending status; schedule payout per Comp_Plan payment cadence |
| 5. Reconcile with Finance | Oracle | Match Commission_Records against Oracle Finance GL entries; flag discrepancies |
| 6. Dispute Management | Internal | Route Disputed Commission_Records to compensation team; track resolution SLA and audit trail |

**Dependencies:** Deal_Opportunity, Commission_Record, Comp_Plan, Quota, Account_Profile, Opportunity_Line_Item, Revenue_Schedule

---

## 8. Competitive Win/Loss Analysis

**ID:** `WORKFLOW_COMPETITIVE_ANALYSIS_V1_0` | **Standard:** MEDDPICC | **File:** `competitive-win-loss.yaml`

**Trigger:** Deal_Opportunity Stage changes to Closed_Won or Closed_Lost OR quarterly batch (1st business day)

| Step | System | Action |
|------|--------|--------|
| 1. Collect All Deal Signals | Internal | Aggregate Conversation_Record competitor mentions, Email_Thread references, Intent_Data, Competitive_Signal records for closed deal |
| 2. Classify Primary Win/Loss Reason | Internal | NLP classify Win_Loss_Record Primary_Reason from call transcripts, rep input, and buyer feedback |
| 3. Competitor Analysis per Outcome | Internal | Group outcomes by Competitor_Won; calculate win rate, average deal size, and stage-of-loss per competitor |
| 4. Pattern Detection Across Cohorts | Internal | Identify systemic patterns: industry segments, deal sizes, buyer personas, product gaps where specific competitors win |
| 5. Battle Card Effectiveness Scoring | Internal | Correlate battle card usage (detected in calls) with win rates; score effectiveness per competitor per objection type |
| 6. Publish Insights to Enablement | Internal | Generate competitive intelligence report; update battle cards; push insights to enablement platform and CRM |

**Dependencies:** Deal_Opportunity, Win_Loss_Record, Competitive_Signal, Conversation_Record, Email_Thread, Intent_Data, Stakeholder_Map, Account_Profile, Product_Catalog, Opportunity_Line_Item

---

[← Back to Ontology Overview](index.md)
