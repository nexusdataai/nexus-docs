# Policies

6 governance policies that constrain entity operations, workflow execution, and business rules across the customer operations ontology. Each policy is defined in `enterprise-knowledge/policies/` as a Markdown file.

---

## Policy Summary

| # | Policy | ID | TMF/ITIL | Risk | Owner | Constrains |
|---|--------|----|----------|------|-------|------------|
| 1 | [Case Handling Policy](#1-case-handling-policy) | POL-CASE-001 | TMF621 / Incident Mgmt | High | Customer Operations | Case, Escalation_Rule, Problem_Record |
| 2 | [SLA Policy](#2-sla-policy) | POL-SLA-001 | TMF623 / SLA Mgmt | Critical | Service Delivery | SLA_Record, Entitlement, Service_Order |
| 3 | [Billing Dispute Policy](#3-billing-dispute-policy) | POL-BILL-001 | TMF678 / Financial Mgmt | High | Finance / Revenue Assurance | Billing_Dispute, AR_Credit_Note, AR_Invoice |
| 4 | [Customer Tier Policy](#4-customer-tier-policy) | POL-TIER-001 | TMF629 / Customer Mgmt | High | Customer Success | Account, Case, Entitlement |
| 5 | [Agent Quality Policy](#5-agent-quality-policy) | POL-AQ-001 | TMF683 / Workforce Mgmt | Medium | Contact Center Operations | Quality_Score, Agent_Metrics, Call_Record |
| 6 | [Customer Experience Policy](#6-customer-experience-policy) | POL-CX-001 | TMF629 / CX Management | Medium | Customer Experience | NPS_Response, Customer_Feedback, Brand_Sentiment |

---

## 1. Case Handling Policy

**ID:** POL-CASE-001 | **TMF:** TMF621 | **Systems:** Salesforce, WXCC

| Rule Area | Key Rules |
|-----------|-----------|
| **Case Classification** | All cases must be classified by Type and Priority within 5 minutes of creation; unclassified cases auto-escalate after 15 minutes |
| **Priority Assignment** | Critical: system-wide outage or Platinum account service failure; High: revenue-impacting or Gold+ account; Medium: standard issue; Low: inquiry or feedback |
| **Ownership** | Every case must have an owner within SLA response time; unassigned cases alert team lead after 50% of response SLA |
| **Escalation Path** | L1→L2: 2 failed resolution attempts OR complexity >3 OR customer requests; L2→L3: requires specialized skill OR cross-system issue; L3→Management: SLA breach OR reputational risk |
| **Repeat Contact** | 3rd contact on same issue within 7 days: auto-escalate to L2 + notify team lead; create Problem_Record if >5 accounts affected by same issue |
| **Case Closure** | Cannot close without Resolution_Code; customer confirmation required for Complaint type; auto-close after 5 days no response (except Critical) |
| **Reopening** | Customer contact within 7 days of closure on same issue: reopen (not new case); after 7 days: new case linked to original |

---

## 2. SLA Policy

**ID:** POL-SLA-001 | **TMF:** TMF623 | **Systems:** Salesforce, SAP, WXCC

### Response SLA (time to first meaningful agent response)

| Priority | Platinum (24x7) | Gold (24x7) | Silver (8x5) | Bronze (8x5) |
|----------|-----------------|-------------|---------------|---------------|
| Critical | 15 minutes | 30 minutes | 1 hour | 2 hours |
| High | 30 minutes | 1 hour | 2 hours | 4 hours |
| Medium | 1 hour | 2 hours | 4 hours | 8 hours |
| Low | 4 hours | 8 hours | 24 hours | 48 hours |

### Resolution SLA (time to case resolution)

| Priority | Platinum | Gold | Silver | Bronze |
|----------|----------|------|--------|--------|
| Critical | 2 hours | 4 hours | 8 hours | 24 hours |
| High | 4 hours | 8 hours | 24 hours | 48 hours |
| Medium | 24 hours | 48 hours | 72 hours | 5 business days |
| Low | 48 hours | 72 hours | 5 business days | 10 business days |

| Rule Area | Key Rules |
|-----------|-----------|
| **Breach Escalation** | 80% of SLA: alert owning agent; 100%: escalate to team lead + case priority auto-incremented; 120%: notify VP Customer Ops |
| **SLA Pause** | Paused when Status = Pending_Customer; resumes on customer response; max pause: 5 business days |
| **Field Service SLA** | Appointment window: ±2 hours of scheduled time; missed window: auto-reschedule + customer notification + credit per tier policy |
| **SLA Reporting** | Daily: breach count and near-miss; Weekly: SLA attainment by tier, team, and category; Monthly: trend and root cause analysis |

---

## 3. Billing Dispute Policy

**ID:** POL-BILL-001 | **TMF:** TMF678 | **Systems:** Oracle ERP, Salesforce

| Rule Area | Key Rules |
|-----------|-----------|
| **Dispute Acknowledgment** | Acknowledge within 24 hours; dispute status visible to customer in portal within 4 hours |
| **Auto-Adjudication** | Auto-approve credit: billing error <$100 for any tier; service failure with documented Service_Order; duplicate invoice (any amount) |
| **Approval Thresholds** | $0-$100: auto-approve; $100-$500: Team Lead; $500-$2,000: Operations Manager; $2,000-$10,000: Finance Director; >$10,000: VP Finance + CFO |
| **Goodwill Credits** | Platinum: up to $200/quarter without escalation; Gold: up to $100/quarter; Silver/Bronze: up to $50/quarter; exceeding cap requires manager approval |
| **Resolution Timeline** | Simple disputes (overcharge, duplicate): 3 business days; Complex (rate disagreement, multi-invoice): 10 business days; escalated: 15 business days |
| **Write-Off Authority** | <$500: Finance Manager; $500-$5,000: Finance Director; >$5,000: VP Finance; all write-offs require documented justification |
| **Repeat Dispute** | 3+ disputes from same account in 90 days: trigger account review; assign dedicated billing analyst; root cause investigation mandatory |

---

## 4. Customer Tier Policy

**ID:** POL-TIER-001 | **TMF:** TMF629 | **Systems:** Salesforce, Oracle, WXCC

| Tier | CLV Threshold | SLA Level | Queue Priority | Retention Authority | Assigned Resources |
|------|--------------|-----------|---------------|--------------------|--------------------|
| **Platinum** | >$100K/year | Premium 24x7 | Highest (skip queue) | Dedicated account manager; pre-approved retention offers up to 25% discount | Named agent team; priority field dispatch |
| **Gold** | $25K-$100K/year | Premium 24x7 | High | Account manager; retention offers up to 15% discount | Skilled agent routing; priority dispatch |
| **Silver** | $5K-$25K/year | Business 8x5 | Standard | Team lead approval for retention offers up to 10% | Standard routing |
| **Bronze** | <$5K/year | Standard 8x5 | Standard | Standard retention playbook only | Standard routing |

| Rule Area | Key Rules |
|-----------|-----------|
| **Tier Calculation** | Recalculated quarterly based on trailing 12-month revenue; manual override requires VP Customer Success approval |
| **Downgrade Protection** | Tier cannot drop more than 1 level per quarter; 30-day notification before downgrade |
| **Churn Intervention** | Platinum: immediate intervention on any churn signal; Gold: intervention within 48 hours; Silver/Bronze: batch monthly review |
| **Proactive Outreach** | System-wide issues: Platinum notified first (within 1 hour), then Gold (within 4 hours), then Silver/Bronze (within 24 hours) |

---

## 5. Agent Quality Policy

**ID:** POL-AQ-001 | **TMF:** TMF683 | **Systems:** WXCC, Salesforce

| Rule Area | Key Rules |
|-----------|-----------|
| **QA Sampling** | Minimum 5 interactions per agent per month evaluated; 100% evaluation for agents in first 90 days or on performance improvement plan |
| **Quality Scorecard** | Greeting/Opening: 10%; Issue Understanding: 20%; Resolution Quality: 30%; Compliance: 20%; Empathy & Communication: 20% |
| **Score Thresholds** | 90-100: Exceeds (eligible for mentor role); 75-89: Meets; 60-74: Needs Improvement (coaching plan); <60: Critical (performance improvement plan + daily monitoring) |
| **Recommendation Compliance** | Agents must acknowledge AI-surfaced recommendations within 30 seconds; rejection requires reason code selection |
| **Handle Time** | No hard cap; handle time monitored for trend analysis only; quality over speed |
| **After-Call Work** | Max 3 minutes for standard cases; 5 minutes for complex; exceeded: alert to team lead (not punitive) |
| **Calibration** | Monthly QA calibration session across evaluators; inter-rater reliability target >85% |

---

## 6. Customer Experience Policy

**ID:** POL-CX-001 | **TMF:** TMF629 | **Systems:** All

| Rule Area | Key Rules |
|-----------|-----------|
| **NPS Targets** | Enterprise target NPS: >45; Detractor follow-up mandatory within 48 hours for Platinum/Gold, 5 business days for Silver/Bronze |
| **CSAT Targets** | Post-interaction CSAT target: >4.2/5.0; CSAT <3.0: trigger immediate supervisor review of interaction |
| **Sentiment Monitoring** | Brand_Sentiment <30 on any topic for 7+ consecutive days: alert CX Director within 24 hours |
| **Survey Cadence** | Post-interaction: every interaction for Platinum; every 3rd for Gold; every 5th for Silver/Bronze; NPS: quarterly all accounts |
| **Feedback Loop** | All Detractor verbatims reviewed weekly by CX team; top 5 themes → action items within 10 business days |
| **Customer Effort Score** | Target CES: <2.5 (low effort); CES >4.0: trigger process review for that case category |
| **Proactive NPS Recovery** | Detractor→Passive: 30-day check-in; Detractor→Promoter goal: 10% conversion rate per quarter |

---

[← Back to Ontology Overview](index.md)
