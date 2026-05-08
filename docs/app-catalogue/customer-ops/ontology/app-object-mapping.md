# Application-Object Mapping

Minimum required ontology objects per application, with relationship details and cross-application dependency analysis.

---

## App 1: Autonomous Issue Resolution Engine

**TMF:** TMF621/TMF678 | **Minimum Objects: 14**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Case` | Salesforce | Core entity — case to be resolved | depends_on -> Account, Contact |
| `Case_Comment` | Salesforce | Resolution notes and agent activity | depends_on -> Case |
| `Account` | Salesforce | Customer context, tier, CLV | — |
| `Contact` | Salesforce | Customer contact for communication | depends_on -> Account |
| `Entitlement` | Salesforce | SLA assignment based on tier | depends_on -> Account |
| `Escalation_Rule` | Salesforce | Escalation path when SLA breached | — |
| `Call_Record` | WXCC | Interaction context and sentiment | depends_on -> Account |
| `Chat_Transcript` | WXCC | Digital interaction context | depends_on -> Account |
| `AR_Customer` | Oracle | Billing status, AR balance | syncs_to -> Account |
| `AR_Invoice` | Oracle | Invoice details for billing cases | depends_on -> AR_Customer |
| `Billing_Dispute` | Oracle | Dispute record for billing cases | depends_on -> AR_Invoice, Case |
| `Service_Order` | SAP | Service order for fulfillment cases | depends_on -> Case, Account |
| `Knowledge_Article` | Salesforce/GDrive | Resolution matching | — |
| `Resolution_Template` | Internal | Automation-eligible resolution patterns | triggers -> automated-remediation |

**Policies:** case-handling-policy, sla-policy, billing-dispute-policy, customer-tier-policy
**Workflows:** case-triage-routing, automated-remediation, billing-dispute-resolution
**Integrations:** sf-oracle-custops-sync, sf-wxcc-interaction-sync, sf-sap-service-sync

---

## App 2: Unified Operations Hub

**TMF:** TMF641/TMF683 | **Minimum Objects: 14**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Case` | Salesforce | Case state tracking across systems | depends_on -> Account |
| `Account` | Salesforce | Customer master for entity resolution | — |
| `AR_Customer` | Oracle | Billing state for cross-system sync | syncs_to -> Account |
| `AR_Invoice` | Oracle | Invoice state for billing-service correlation | depends_on -> AR_Customer |
| `AR_Payment` | Oracle | Payment state tracking | depends_on -> AR_Invoice |
| `AR_Credit_Note` | Oracle | Credit note state for reconciliation | depends_on -> Billing_Dispute |
| `Billing_Dispute` | Oracle | Dispute state for billing-case linking | depends_on -> AR_Invoice |
| `Call_Record` | WXCC | Interaction state for handoff context | depends_on -> Account |
| `Chat_Transcript` | WXCC | Chat state for handoff context | depends_on -> Account |
| `Agent_State` | WXCC | Agent availability for routing | — |
| `Service_Order` | SAP | Service execution state | depends_on -> Case, Account |
| `Field_Dispatch` | SAP | Field technician dispatch state | depends_on -> Service_Order |
| `SLA_Record` | SAP | SLA tracking for breach detection | depends_on -> Service_Order |
| `Knowledge_Article` | Salesforce/GDrive | Context cards for field technicians | — |

**Policies:** sla-policy, case-handling-policy, billing-dispute-policy, data-freshness-policy
**Workflows:** cross-system-state-sync, service-fulfillment-orchestration, proactive-outreach
**Integrations:** sf-oracle-custops-sync, sf-wxcc-interaction-sync, sf-sap-service-sync

---

## App 3: Proactive Agent Assist Copilot

**TMF:** TMF629/TMF683 | **Minimum Objects: 14**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Account` | Salesforce | Customer profile, tier, CLV, churn risk | — |
| `Customer_Profile` | Salesforce | Behavioral profile for personalization | depends_on -> Account |
| `Contact` | Salesforce | Preferred channel, role | depends_on -> Account |
| `Case` | Salesforce | Open/historical cases for context | depends_on -> Account |
| `Call_Record` | WXCC | Live interaction for real-time assist | depends_on -> Account, Agent_State |
| `Chat_Transcript` | WXCC | Live chat for real-time assist | depends_on -> Account |
| `Agent_State` | WXCC | Agent skills and availability | — |
| `AR_Customer` | Oracle | Billing context for recommendations | syncs_to -> Account |
| `AR_Invoice` | Oracle | Invoice context for billing inquiries | depends_on -> AR_Customer |
| `Knowledge_Article` | Salesforce/GDrive | Knowledge delivery to agent | — |
| `Resolution_Template` | Internal | Resolution suggestions ranked by success | — |
| `NPS_Response` | Social Listening | Churn signal and sentiment context | depends_on -> Account |
| `CSAT_Survey` | Social Listening | Post-interaction satisfaction signal | depends_on -> Call_Record |
| `Customer_Feedback` | Social Listening | Multi-channel feedback for sentiment | depends_on -> Account |

**Policies:** customer-tier-policy, agent-quality-policy, customer-experience-policy
**Workflows:** real-time-agent-assist, customer-churn-intervention
**Integrations:** sf-wxcc-interaction-sync, sf-oracle-custops-sync, social-feedback-feed

---

## Cross-Application Dependency Matrix

Shows which entities are shared across applications (checkmark = required by that app):

| Entity | Issue Resolution | Operations Hub | Agent Assist |
|--------|-----------------|----------------|--------------|
| **Account** | x | x | x |
| **Case** | x | x | x |
| **Call_Record** | x | x | x |
| **AR_Customer** | x | x | x |
| **Knowledge_Article** | x | x | x |
| **Chat_Transcript** | x | x | x |
| **AR_Invoice** | x | x | x |
| **Billing_Dispute** | x | x | — |
| **Service_Order** | x | x | — |
| **Contact** | x | — | x |
| **Entitlement** | x | — | — |
| **Escalation_Rule** | x | — | — |
| **Case_Comment** | x | — | — |
| **Resolution_Template** | x | — | x |
| **AR_Payment** | — | x | — |
| **AR_Credit_Note** | — | x | — |
| **Agent_State** | — | x | x |
| **Field_Dispatch** | — | x | — |
| **SLA_Record** | — | x | — |
| **Customer_Profile** | — | — | x |
| **NPS_Response** | — | — | x |
| **CSAT_Survey** | — | — | x |
| **Customer_Feedback** | — | — | x |

---

## Entity Count per App

| Application | Min Objects | Workflows | Policies | Integrations |
|------------|-----------|-----------|----------|--------------|
| Autonomous Issue Resolution | 14 | 3 | 4 | 3 |
| Unified Operations Hub | 14 | 3 | 4 | 3 |
| Proactive Agent Assist | 14 | 2 | 3 | 3 |

---

[← Back to Ontology Overview](index.md)
