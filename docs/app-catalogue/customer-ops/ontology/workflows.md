# Workflows

8 TMF/ITIL-aligned AI workflows that power the 3 customer operations applications. Each workflow is defined in `enterprise-knowledge/workflows/` as a YAML file with trigger conditions, ordered steps, and entity/policy dependencies.

---

## Workflow Summary

| # | Workflow | TMF/ITIL | Trigger | Primary App |
|---|---------|----------|---------|-------------|
| 1 | [Case Triage & Routing](#1-case-triage-routing) | TMF621 / Incident Mgmt | New case created or inbound interaction | Autonomous Issue Resolution |
| 2 | [Automated Remediation](#2-automated-remediation) | TMF621 / Service Request | Known issue pattern matched with >0.8 confidence | Autonomous Issue Resolution |
| 3 | [Billing Dispute Resolution](#3-billing-dispute-resolution) | TMF678 / Financial Mgmt | Billing dispute opened or case type = Billing | Autonomous Issue Resolution, Operations Hub |
| 4 | [Cross-System State Sync](#4-cross-system-state-sync) | TMF683 / Interaction | Any state change in Salesforce, Oracle, SAP, or WXCC | Unified Operations Hub |
| 5 | [Service Fulfillment Orchestration](#5-service-fulfillment-orchestration) | TMF641 / Request Fulfillment | Service order created in SAP | Unified Operations Hub |
| 6 | [Real-Time Agent Assist](#6-real-time-agent-assist) | TMF683 / Knowledge Mgmt | Live interaction detected in WXCC | Proactive Agent Assist |
| 7 | [Customer Churn Intervention](#7-customer-churn-intervention) | TMF629 / Service Relationship | Monthly schedule or churn risk score >0.7 | Proactive Agent Assist |
| 8 | [Proactive Outreach](#8-proactive-outreach) | TMF629 / Problem Mgmt | Trend alert or negative sentiment detected | Proactive Agent Assist, Operations Hub |

---

## 1. Case Triage & Routing

**ID:** `WORKFLOW_CASE_TRIAGE_V1_0` | **TMF:** TMF621 | **File:** `case-triage-routing.yaml`

**Trigger:** New Case created in Salesforce OR inbound Call_Record/Chat_Transcript transferred from IVR to agent queue

| Step | System | Action |
|------|--------|--------|
| 1. Intent Classification | Internal | NLP classifies case by issue taxonomy (Billing/Technical/Account/Service/Complaint); assigns urgency and complexity score (1-5) |
| 2. Customer Context Lookup | Salesforce/Oracle | Pull Account tier, CLV, churn risk, open cases, AR balance, recent interactions |
| 3. SLA Assignment | Internal | Match Account.Tier to Entitlement; calculate SLA deadline (response + resolution) |
| 4. Routing Decision | Internal | Score routing candidates: auto-resolution path (if pattern match >0.8), L1 agent (by skill match), L2 specialist (if complexity >3) |
| 5. Queue Assignment | WXCC | Assign to optimal queue/agent based on skill, availability, and customer tier priority |
| 6. Context Brief Push | Internal | Push assembled context card to assigned agent or automated workflow |

**Dependencies:** Case, Account, Contact, Customer_Profile, Entitlement, Escalation_Rule, Call_Record, IVR_Journey, Knowledge_Article, case-handling-policy, sla-policy

---

## 2. Automated Remediation

**ID:** `WORKFLOW_AUTO_REMEDIATION_V1_0` | **TMF:** TMF621 | **File:** `automated-remediation.yaml`

**Trigger:** Case matched to Resolution_Template with confidence >0.8 AND issue type is automation-eligible

| Step | System | Action |
|------|--------|--------|
| 1. Pattern Matching | Internal | Match case description + customer context against Resolution_Template library; rank by success rate |
| 2. Policy Compliance Check | Internal | Validate proposed resolution against applicable policies (billing-dispute-policy, customer-tier-policy) |
| 3. Action Planning | Internal | Generate ordered action plan: which systems to update, in what sequence, with rollback plan |
| 4. Execute in Oracle | Oracle | If billing action: issue credit note, adjust invoice, or waive fee per policy authority |
| 5. Execute in SAP | SAP | If service action: create/update service order, schedule dispatch, or reset service |
| 6. Update Salesforce | Salesforce | Update Case status, add resolution notes, set Resolution_Code |
| 7. Post-Resolution Scan | Internal | Check for related open cases, pending service orders, or latent billing issues on same account |
| 8. Notify Customer | Internal | Send resolution notification via customer's preferred channel |

**Dependencies:** Case, Account, Resolution_Template, Knowledge_Article, AR_Invoice, AR_Credit_Note, Billing_Dispute, Service_Order, case-handling-policy, billing-dispute-policy, customer-tier-policy

---

## 3. Billing Dispute Resolution

**ID:** `WORKFLOW_BILLING_DISPUTE_V1_0` | **TMF:** TMF678 | **File:** `billing-dispute-resolution.yaml`

**Trigger:** Billing_Dispute record created in Oracle OR Case with Type = Billing_Inquiry in Salesforce

| Step | System | Action |
|------|--------|--------|
| 1. Dispute Classification | Internal | NLP classifies dispute type: overcharge, double billing, service not received, rate disagreement, late fee |
| 2. Invoice Analysis | Oracle | Pull invoice details, line items, payment history; compare against contracted rates and service delivery records |
| 3. Service Correlation | SAP/Salesforce | Cross-reference with Service_Order history and Case history to identify if billing aligns with delivered service |
| 4. Auto-Adjudication | Internal | For clear-cut cases (duplicate invoice, documented service failure): auto-approve credit per policy thresholds |
| 5. Credit Note Generation | Oracle | Generate AR_Credit_Note with appropriate reason code; route for approval if above auto-threshold |
| 6. Case Update | Salesforce | Update linked Case with resolution; add billing dispute outcome details |
| 7. Customer Communication | Internal | Notify customer of resolution; provide credit note reference |

**Dependencies:** Billing_Dispute, AR_Invoice, AR_Payment, AR_Credit_Note, AR_Customer, Case, Account, Service_Order, billing-dispute-policy, customer-tier-policy

---

## 4. Cross-System State Sync

**ID:** `WORKFLOW_STATE_SYNC_V1_0` | **TMF:** TMF683 | **File:** `cross-system-state-sync.yaml`

**Trigger:** Any state change event in Salesforce (CDC), Oracle (Advanced Queue), SAP (IDoc), or WXCC (webhook)

| Step | System | Action |
|------|--------|--------|
| 1. Event Capture | Source System | Receive change event with entity type, ID, changed fields, timestamp |
| 2. Entity Resolution | Internal | Resolve affected customer across all systems: SF Account ↔ Oracle AR_Customer ↔ SAP Business Partner ↔ WXCC Caller Profile |
| 3. State Assembly | Internal | Build/update composite customer state: open cases, billing status, active interactions, service orders |
| 4. Discrepancy Detection | Internal | Compare states across systems; flag inconsistencies (e.g., case resolved but credit note pending) |
| 5. Propagation | Target Systems | Push relevant state updates to other systems needing awareness (e.g., Oracle credit approved → update SF case) |
| 6. Dashboard Update | Internal | Refresh unified customer view on agent desktop and operations dashboard |

**Dependencies:** Account, AR_Customer, Case, AR_Invoice, AR_Payment, Billing_Dispute, Service_Order, Call_Record, Chat_Transcript, Field_Dispatch, data-freshness-policy

---

## 5. Service Fulfillment Orchestration

**ID:** `WORKFLOW_SERVICE_FULFILLMENT_V1_0` | **TMF:** TMF641 | **File:** `service-fulfillment-orchestration.yaml`

**Trigger:** Service_Order created in SAP OR Case escalated to field service

| Step | System | Action |
|------|--------|--------|
| 1. Order Validation | SAP | Validate service order completeness: account, type, priority, required parts/skills |
| 2. Customer Context Assembly | Salesforce/Oracle/WXCC | Pull case history, interaction history, billing status, previous service visits |
| 3. Resource Matching | SAP | Match required skills and parts to available technicians; consider proximity and schedule |
| 4. Dispatch Planning | SAP | Create Field_Dispatch; set ETA; generate customer notification |
| 5. Context Card Delivery | Internal | Push pre-visit context card to technician: case summary, interaction sentiment, billing status, previous visit outcomes |
| 6. SLA Monitoring | Internal | Track SLA_Record; trigger alerts at 80% threshold; auto-escalate at breach |
| 7. Post-Visit Processing | SAP/Salesforce | Record outcome, update Service_Order status, update Case, trigger CSAT survey |

**Dependencies:** Service_Order, Field_Dispatch, SLA_Record, Case, Account, Contact, Call_Record, AR_Customer, Knowledge_Article, sla-policy, case-handling-policy

---

## 6. Real-Time Agent Assist

**ID:** `WORKFLOW_AGENT_ASSIST_V1_0` | **TMF:** TMF683 | **File:** `real-time-agent-assist.yaml`

**Trigger:** New Call_Record or Chat_Transcript interaction begins in WXCC

| Step | System | Action |
|------|--------|--------|
| 1. Customer Identification | WXCC/Salesforce | ANI/caller lookup → resolve to Account; pull Customer_Profile |
| 2. Context Hydration | All Systems | Assemble: open cases, billing status (Oracle), service orders (SAP), last 5 interactions (WXCC), NPS/CSAT, churn risk |
| 3. Real-Time Intent Detection | Internal | NLP on live speech/text stream; classify intent every 15 seconds |
| 4. Knowledge Matching | Internal | Match detected intent to top-3 Knowledge_Articles and Resolution_Templates; rank by relevance × success rate |
| 5. Action Scoring | Internal | Score candidate next-best-actions: resolve, escalate, offer, waive, upsell; factor customer tier, CLV, churn risk |
| 6. Recommendation Push | Internal | Deliver ranked recommendations to agent desktop with confidence scores and one-click action buttons |
| 7. Sentiment Monitoring | Internal | Continuous sentiment scoring; trigger coaching prompts on negative shift (below -0.4) |
| 8. Outcome Capture | Internal | Record recommendation acceptance/rejection for model learning |

**Dependencies:** Call_Record, Chat_Transcript, Account, Customer_Profile, Case, AR_Customer, AR_Invoice, Service_Order, Knowledge_Article, Resolution_Template, NPS_Response, CSAT_Survey, Agent_State, customer-tier-policy, agent-quality-policy

---

## 7. Customer Churn Intervention

**ID:** `WORKFLOW_CHURN_INTERVENTION_V1_0` | **TMF:** TMF629 | **File:** `customer-churn-intervention.yaml`

**Trigger:** Monthly (1st business day) OR Account churn_risk_score exceeds 0.7

| Step | System | Action |
|------|--------|--------|
| 1. Profile Assembly | Internal | Aggregate: interaction frequency trend, CSAT/NPS trend, billing behavior, case volume, sentiment shift |
| 2. Feature Engineering | Internal | Calculate: interaction velocity, complaint ratio, payment behavior change, usage decline, competitor mention |
| 3. Churn Scoring | Internal | Gradient-boosted model; predict 30/60/90-day churn probability |
| 4. Driver Segmentation | Internal | Classify churn driver: Price_Sensitivity, Service_Quality, Unresolved_Issues, Competitor_Pull, Life_Event |
| 5. Retention Offer Matching | Internal | Map driver to optimal retention action (discount, service upgrade, dedicated support, account review) per customer-tier-policy |
| 6. Push to CRM | Salesforce | Create retention task on Account; assign to account manager with context brief; 24-hour SLA for Platinum, 48-hour for Gold |
| 7. Outcome Tracking | Internal | Track intervention outcome (retained/churned/deferred); feed back into model |

**Dependencies:** Account, Customer_Profile, Case, Call_Record, Chat_Transcript, AR_Customer, AR_Invoice, AR_Payment, NPS_Response, Customer_Feedback, CSAT_Survey, Brand_Sentiment, customer-tier-policy, customer-experience-policy

---

## 8. Proactive Outreach

**ID:** `WORKFLOW_PROACTIVE_OUTREACH_V1_0` | **TMF:** TMF629 | **File:** `proactive-outreach.yaml`

**Trigger:** Trend_Alert with severity High/Critical OR Customer_Feedback sentiment < -50 OR Problem_Record with impact = System_Wide

| Step | System | Action |
|------|--------|--------|
| 1. Impact Assessment | Internal | Identify affected accounts from Trend_Alert or Problem_Record; calculate scope and severity |
| 2. Customer Prioritization | Internal | Rank affected accounts by tier, CLV, churn risk, and SLA entitlements |
| 3. Message Generation | Internal | Generate personalized outreach message per customer segment with issue acknowledgment and ETA |
| 4. Channel Selection | Internal | Select outreach channel per Contact.Preferred_Channel (Email, SMS, Portal notification) |
| 5. Execute Outreach | Salesforce/WXCC | Send notifications; create Activity_Log entries; update Case if one exists |
| 6. Response Monitoring | Internal | Track customer responses; escalate unresolved within 24 hours |
| 7. Root Cause Link | Internal | If Problem_Record exists, link outreach to root cause for trending and resolution tracking |

**Dependencies:** Trend_Alert, Problem_Record, Account, Contact, Customer_Profile, Case, Customer_Feedback, Brand_Sentiment, Email_Record, SMS_Record, Activity_Log, customer-experience-policy, case-handling-policy

---

[← Back to Ontology Overview](index.md)
