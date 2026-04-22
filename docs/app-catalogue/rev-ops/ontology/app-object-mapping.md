# Application-Object Mapping

Minimum required ontology objects per application, with relationship details and cross-application dependency analysis.

---

## App 1: Deal Intelligence & Contextual Analytics

**MEDDPICC | Minimum Objects: 12**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Deal_Opportunity` | Salesforce CRM | Core entity — deal being analyzed | depends_on -> Account_Profile |
| `Opportunity_Line_Item` | Salesforce CRM | Product mix and deal structure | depends_on -> Deal_Opportunity, Product_Catalog |
| `Stage_History` | Salesforce CRM | Deal progression velocity | depends_on -> Deal_Opportunity |
| `Account_Profile` | Salesforce CRM | Buyer context, ICP score, health | — |
| `Contact` | Salesforce CRM | Buyer contacts and roles | depends_on -> Account_Profile |
| `Stakeholder_Map` | Salesforce CRM | MEDDPICC role mapping per deal | depends_on -> Deal_Opportunity, Contact |
| `Conversation_Record` | Gong / Call Platform | Call intelligence, MEDDPICC extraction | depends_on -> Deal_Opportunity |
| `Meeting_Action_Item` | Gong / Call Platform | Next steps and commitments | depends_on -> Conversation_Record |
| `Email_Thread` | Email Platform | Engagement velocity and multi-threading | depends_on -> Deal_Opportunity |
| `Calendar_Event` | Calendar Platform | Meeting frequency and attendance | depends_on -> Deal_Opportunity |
| `Product_Usage` | Product Platform | Product-fit and expansion signals | depends_on -> Account_Profile |
| `Competitive_Signal` | Market Intelligence | Competitor presence and threat score | depends_on -> Deal_Opportunity |

**Policies:** deal-qualification-policy, pricing-discount-policy
**Workflows:** deal-intelligence-scoring, conversation-email-nlp, competitive-win-loss
**Integrations:** gong-conversation-feed, email-calendar-sync, market-intelligence-feed

---

## App 2: Pipeline Risk & Revenue Forecasting

**MEDDPICC / ASC 606 | Minimum Objects: 12**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Deal_Opportunity` | Salesforce CRM | Pipeline deal inventory | depends_on -> Account_Profile |
| `Stage_History` | Salesforce CRM | Velocity and stage inflation detection | depends_on -> Deal_Opportunity |
| `Account_Profile` | Salesforce CRM | Customer health for renewal prediction | — |
| `Pipeline_Snapshot` | Internal (derived) | Weekly pipeline state for trending | depends_on -> Deal_Opportunity |
| `Deal_Velocity` | Internal (derived) | Per-deal slip risk scoring | depends_on -> Deal_Opportunity |
| `Forecast_Submission` | Salesforce CRM | Rep vs. AI forecast comparison | depends_on -> Deal_Opportunity |
| `Renewal_Record` | Salesforce CRM / Product | Upcoming renewal risk assessment | depends_on -> Account_Profile, Subscription |
| `Subscription` | Product Platform | Current ARR and usage for renewal context | depends_on -> Account_Profile |
| `Product_Usage` | Product Platform | Usage trends for expansion/churn signals | depends_on -> Account_Profile |
| `Revenue_Schedule` | Oracle Finance | ASC 606 revenue projection alignment | depends_on -> Contract_Record |
| `Conversation_Record` | Gong / Call Platform | Deal engagement context for risk scoring | depends_on -> Deal_Opportunity |
| `Email_Thread` | Email Platform | Engagement signals for risk scoring | depends_on -> Deal_Opportunity |

**Policies:** forecast-governance-policy, revenue-recognition-policy
**Workflows:** pipeline-risk-assessment, renewal-expansion-prediction
**Integrations:** crm-finance-sync, product-usage-feed

---

## App 3: Revenue Operations Orchestration Hub

**ASC 606 | Minimum Objects: 12**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Deal_Opportunity` | Salesforce CRM | Closed-won trigger for quote-to-cash | depends_on -> Account_Profile |
| `Account_Profile` | Salesforce CRM | Customer master for billing/collections | — |
| `Quote` | Salesforce CPQ | Pricing and terms for billing creation | depends_on -> Deal_Opportunity |
| `Contract_Record` | Document Management / CLM | NLP-extracted terms, obligations, ramp | depends_on -> Deal_Opportunity, Account_Profile |
| `Revenue_Schedule` | Oracle Finance | ASC 606 recognition schedule | depends_on -> Contract_Record |
| `Billing_Schedule` | Oracle Finance | Invoice timing and amounts | depends_on -> Contract_Record |
| `AR_Invoice` | Oracle Finance | Invoice status and aging | depends_on -> Account_Profile |
| `Payment` | Oracle Finance | Payment application and reconciliation | depends_on -> AR_Invoice |
| `Commission_Record` | Oracle Finance / CRM | Commission calculation and payout | depends_on -> Deal_Opportunity |
| `Quota` | Salesforce CRM / Finance | Quota attainment for commission | depends_on -> Commission_Record |
| `Subscription` | Product Platform | Active subscription for billing alignment | depends_on -> Account_Profile |
| `Product_Catalog` | Product Platform | Price book for CPQ and billing validation | — |

**Policies:** revenue-recognition-policy, pricing-discount-policy, commission-compensation-policy
**Workflows:** quote-to-cash-orchestration, revenue-leakage-detection, commission-compensation
**Integrations:** crm-finance-sync, document-clm-feed, product-usage-feed

---

## Cross-Application Dependency Matrix

Shows which entities are shared across applications (checkmark = required by that app):

| Entity | Deal Intelligence | Pipeline Risk | Revenue Orchestration |
|--------|------------------|---------------|----------------------|
| **Deal_Opportunity** | x | x | x |
| **Account_Profile** | x | x | x |
| **Stage_History** | x | x | — |
| **Conversation_Record** | x | x | — |
| **Email_Thread** | x | x | — |
| **Product_Usage** | x | x | — |
| **Subscription** | — | x | x |
| **Revenue_Schedule** | — | x | x |
| **Contact** | x | — | — |
| **Stakeholder_Map** | x | — | — |
| **Competitive_Signal** | x | — | — |
| **Calendar_Event** | x | — | — |
| **Pipeline_Snapshot** | — | x | — |
| **Deal_Velocity** | — | x | — |
| **Forecast_Submission** | — | x | — |
| **Renewal_Record** | — | x | — |
| **Quote** | — | — | x |
| **Contract_Record** | — | — | x |
| **Billing_Schedule** | — | — | x |
| **AR_Invoice** | — | — | x |
| **Payment** | — | — | x |
| **Commission_Record** | — | — | x |

---

## Entity Count per App

| Application | Min Objects | Workflows | Policies | Integrations |
|------------|-----------|-----------|----------|--------------|
| Deal Intelligence | 12 | 3 | 2 | 3 |
| Pipeline Risk & Forecasting | 12 | 2 | 2 | 2 |
| Revenue Orchestration | 12 | 3 | 3 | 3 |

---

[← Back to Ontology Overview](index.md)
