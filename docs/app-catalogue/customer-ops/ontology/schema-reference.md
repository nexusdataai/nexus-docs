# Schema Reference

Complete reference for the customer operations semantic schema — 10 domains, ~35 tables across 6 source systems, aligned to TMF Open APIs and ITIL v4.

**Source File:** `enterprise-knowledge/customer-ops-schema.yaml`

---

## Domain 1: Customer & Account Management

**System:** Salesforce | **TMF:** Customer Management (TMF629) | **ITIL:** Service Relationship Management

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Account` | Customer/subscriber/enterprise account master | high | Account_ID, Name, Segment (Enterprise/SMB/Consumer), Tier (Platinum/Gold/Silver/Bronze), Industry, Region, CLV, Churn_Risk_Score, Status (Active/Suspended/Churned), Owner_ID |
| `Contact` | Customer contact persons | medium | Contact_ID, Account_ID, Name, Email, Phone, Role (Decision_Maker/Technical/Billing/End_User), Preferred_Channel (Phone/Email/Chat/Portal), Primary_Flag |
| `Customer_Profile` | Aggregated behavioral profile | medium | Profile_ID, Account_ID, Tenure_Months, Total_Interactions, Avg_CSAT, NPS_Score, Product_Holdings, Usage_Trend (Growing/Stable/Declining), Last_Interaction_Date |

**Key Relationships:**

- `Account` --syncs_to--> `AR_Customer` (via sf-oracle-custops-sync)
- `Account` --triggers--> Customer Churn Intervention workflow
- `Account` --constrained_by--> customer-tier-policy
- `Contact` --depends_on--> `Account`
- `Customer_Profile` --depends_on--> `Account`

---

## Domain 2: Case & Service Management

**System:** Salesforce | **TMF:** Trouble Ticket (TMF621) | **ITIL:** Incident / Service Request Management

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Case` | Customer case/ticket/trouble ticket | high | Case_ID, Account_ID, Contact_ID, Subject, Description, Type (Incident/Service_Request/Billing_Inquiry/Complaint/Feedback), Priority (Critical/High/Medium/Low), Status (New/In_Progress/Pending_Customer/Escalated/Resolved/Closed), Origin (Phone/Email/Chat/Portal/Social), Owner_ID, SLA_Deadline, Escalation_Level (L1/L2/L3), Resolution_Code |
| `Case_Comment` | Case activity log and agent notes | low | Comment_ID, Case_ID, Author_ID, Body, Is_Public, Created_Date |
| `Entitlement` | Customer SLA entitlement based on tier | medium | Entitlement_ID, Account_ID, Service_Level (Premium_24x7/Business_8x5/Standard), Response_Time_Hours, Resolution_Time_Hours, Status (Active/Expired) |
| `Escalation_Rule` | Escalation path definition per case attributes | medium | Rule_ID, Trigger_Condition, Escalation_Level, Target_Team, SLA_Hours, Auto_Escalate_Flag |

**Key Relationships:**

- `Case` --triggers--> Case Triage & Routing workflow
- `Case` --triggers--> Automated Remediation workflow (when type matches known pattern)
- `Case` --constrained_by--> case-handling-policy, sla-policy
- `Case` --escalates_to--> `Escalation_Rule` (on SLA breach)
- `Case_Comment` --depends_on--> `Case`
- `Entitlement` --depends_on--> `Account`

---

## Domain 3: Contact Center Operations

**System:** Webex Contact Center (WXCC) | **TMF:** Interaction (TMF683)

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Call_Record` | Voice interaction record | high | Call_ID, ANI (caller number), DNIS (dialed number), Account_ID (resolved), Agent_ID, Queue_ID, Start_Time, End_Time, Duration_Seconds, Hold_Time_Seconds, Wrap_Time_Seconds, Disposition (Resolved/Transferred/Escalated/Callback/Abandoned), Sentiment_Score (-100 to +100), Recording_URL, Transcript_ID |
| `Chat_Transcript` | Digital chat interaction | medium | Chat_ID, Account_ID, Agent_ID, Channel (Web_Chat/WhatsApp/SMS/Social), Start_Time, End_Time, Message_Count, Sentiment_Score, Disposition, Transcript_Text |
| `Agent_State` | Real-time agent availability and status | medium | State_ID, Agent_ID, State (Available/On_Call/Wrap_Up/Break/Offline/Training), Queue_ID, Since_Timestamp, Skills (Billing/Technical/Retention/General) |
| `Queue` | Contact center queue definition | low | Queue_ID, Name, Type (Voice/Chat/Email/Blended), Skill_Required, SLA_Threshold_Seconds, Current_Wait_Time, Agents_Available, Calls_Waiting |
| `IVR_Journey` | Customer IVR navigation path | low | Journey_ID, Call_ID, Steps_Taken, Selections, Self_Service_Attempted, Self_Service_Result (Resolved/Abandoned/Agent_Transfer), Duration_Seconds |

**Key Relationships:**

- `Call_Record` --triggers--> Real-Time Agent Assist workflow (on interaction start)
- `Call_Record` --depends_on--> `Account` (via ANI lookup)
- `Call_Record` --depends_on--> `Agent_State`
- `Chat_Transcript` --triggers--> Real-Time Agent Assist workflow
- `IVR_Journey` --triggers--> Case Triage & Routing workflow (on agent transfer)

---

## Domain 4: Billing & Revenue

**System:** Oracle | **TMF:** Billing (TMF678) | **ITIL:** Financial Management

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `AR_Customer` | Accounts Receivable customer record | high | Customer_ID (maps to SF Account), Customer_Name, Credit_Limit, AR_Balance, Collection_Priority (Priority/Standard/Monitored/Basic), Payment_Terms, Currency, Status |
| `AR_Invoice` | Customer invoice for services | high | Invoice_ID, Customer_ID, Invoice_Date, Due_Date, Total_Amount, Tax_Amount, Status (Open/Partially_Paid/Paid/Overdue/Disputed/Written_Off), Linked_Service_Order_ID |
| `AR_Payment` | Payment received against invoice | high | Payment_ID, Invoice_ID, Customer_ID, Amount, Payment_Date, Payment_Method (Bank_Transfer/Credit_Card/ACH/Check), Applied_Flag |
| `AR_Credit_Note` | Credit memo for disputes/adjustments | high | Credit_Note_ID, Customer_ID, Invoice_ID, Amount, Reason (Billing_Error/Service_Failure/Goodwill/Dispute_Resolution/Promotional_Credit), Status, Approval_Status |
| `Billing_Dispute` | Customer billing dispute record | high | Dispute_ID, Customer_ID, Invoice_ID, Case_ID (maps to SF Case), Dispute_Type (Overcharge/Double_Billing/Service_Not_Received/Rate_Disagreement/Late_Fee), Dispute_Amount, Status (Open/Under_Review/Approved/Rejected/Partially_Approved), Resolution_Amount, Resolved_Date |

**Key Relationships:**

- `AR_Customer` --syncs_to--> `Account` (bidirectional via sf-oracle-custops-sync)
- `AR_Invoice` --triggers--> Billing Dispute Resolution workflow (when disputed)
- `Billing_Dispute` --constrained_by--> billing-dispute-policy
- `AR_Credit_Note` --depends_on--> `Billing_Dispute`
- `Billing_Dispute` --depends_on--> `AR_Invoice`, `Case`

---

## Domain 5: Service Fulfillment

**System:** SAP | **TMF:** Service Order (TMF641) | **ITIL:** Service Request Fulfillment

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Service_Order` | Service work order for fulfillment | high | Service_Order_ID, Account_ID, Case_ID, Type (Installation/Modification/Repair/Deactivation/Migration), Status (Open/Scheduled/In_Progress/Completed/Cancelled), Priority, Scheduled_Date, Completion_Date, Assigned_Team |
| `Field_Dispatch` | Field technician dispatch record | medium | Dispatch_ID, Service_Order_ID, Technician_ID, Status (Assigned/En_Route/On_Site/Completed/Failed/Rescheduled), ETA, Actual_Arrival, Outcome (Resolved/Partial/Failed/Customer_Absent), Parts_Used |
| `SLA_Record` | Service level agreement tracking | high | SLA_ID, Account_ID, Service_Order_ID, Response_SLA_Hours, Resolution_SLA_Hours, Response_Actual_Hours, Resolution_Actual_Hours, Breach_Flag, Breach_Type (Response/Resolution/Both) |

**Key Relationships:**

- `Service_Order` --triggers--> Service Fulfillment Orchestration workflow
- `Service_Order` --depends_on--> `Case`, `Account`
- `Service_Order` --constrained_by--> sla-policy
- `Field_Dispatch` --depends_on--> `Service_Order`
- `SLA_Record` --depends_on--> `Service_Order`
- `SLA_Record` --escalates_to--> `Escalation_Rule` (on breach)

---

## Domain 6: Agent Performance & Quality

**System:** WXCC / Salesforce | **TMF:** Interaction (TMF683) / Workforce Management

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Agent_Metrics` | Aggregated agent performance metrics | medium | Agent_ID, Period (Daily/Weekly/Monthly), Calls_Handled, Avg_Handle_Time, First_Call_Resolution_Rate, CSAT_Avg, Adherence_Pct, Utilization_Pct, Upsell_Count, Quality_Score |
| `Quality_Score` | QA evaluation per interaction | medium | Score_ID, Call_ID, Agent_ID, Evaluator_ID, Overall_Score (0-100), Greeting_Score, Resolution_Score, Compliance_Score, Empathy_Score, Feedback |
| `CSAT_Survey` | Post-interaction customer satisfaction survey | low | Survey_ID, Interaction_ID, Account_ID, Score (1-5), Comments, Response_Date, Channel |

**Key Relationships:**

- `Agent_Metrics` --depends_on--> `Call_Record`, `Chat_Transcript`, `Case`
- `Quality_Score` --depends_on--> `Call_Record`
- `Quality_Score` --constrained_by--> agent-quality-policy
- `CSAT_Survey` --depends_on--> `Call_Record` or `Chat_Transcript`

---

## Domain 7: Knowledge & Resolution

**System:** Salesforce / Google Drive | **ITIL:** Knowledge Management

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Knowledge_Article` | Published resolution article | medium | Article_ID, Title, Category (Billing/Technical/Account/Service/Policy), Body, Resolution_Steps, Version, Status (Draft/Published/Archived), Usage_Count, Success_Rate, Last_Updated |
| `Resolution_Template` | Structured resolution template for automation | medium | Template_ID, Issue_Type, Steps (ordered JSON), Systems_Involved (Salesforce/Oracle/SAP/WXCC), Automation_Eligible, Success_Rate, Avg_Resolution_Minutes |
| `SOP_Document` | Standard operating procedure (NLP-extracted) | medium | SOP_ID, Document_Path, Title, Category, Effective_Date, Version, Key_Steps_Extracted, Extraction_Confidence |

**Key Relationships:**

- `Knowledge_Article` --triggers--> Knowledge Delivery workflow (on case match)
- `Resolution_Template` --triggers--> Automated Remediation workflow
- `SOP_Document` --depends_on--> unstructured extraction pipeline
- `Knowledge_Article` --constrained_by--> knowledge-management-policy

---

## Domain 8: Customer Sentiment & Feedback

**System:** Social Listening / Salesforce | **TMF:** Customer Management (TMF629)

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `NPS_Response` | Net Promoter Score survey response | low | Response_ID, Account_ID, Score (0-10), Category (Promoter/Passive/Detractor), Verbatim, Survey_Date, Follow_Up_Required |
| `Customer_Feedback` | Multi-channel customer feedback aggregation | low | Feedback_ID, Account_ID, Source (Survey/Social/Review/Portal/Email), Sentiment_Score (-100 to +100), Topic (Service/Billing/Product/Experience), Date |
| `Brand_Sentiment` | Aggregated brand/service sentiment | low | Sentiment_ID, Brand, Service_Category, Platform (Twitter_X/Reddit/Review_Site/Industry_Forum), Sentiment_Score (-100 to +100), Topic, Mention_Count, Period |

**Key Relationships:**

- `NPS_Response` --triggers--> Customer Churn Intervention workflow (Detractor score)
- `Customer_Feedback` --triggers--> Proactive Outreach workflow (negative sentiment)
- `Brand_Sentiment` --constrained_by--> customer-experience-policy
- All ingested via `social-listening-feed` integration

---

## Domain 9: Communication History

**System:** Salesforce / WXCC | **TMF:** Interaction (TMF683)

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Email_Record` | Inbound/outbound email interaction | medium | Email_ID, Case_ID, Account_ID, Direction (Inbound/Outbound), Subject, Body_Preview, Sentiment_Score, Agent_ID, Timestamp |
| `SMS_Record` | SMS notification or interaction | low | SMS_ID, Account_ID, Direction, Message_Text, Status (Sent/Delivered/Failed/Read), Timestamp |
| `Activity_Log` | Generic Salesforce activity (task, event, call log) | low | Activity_ID, Account_ID, Case_ID, Type (Task/Event/Call/Email), Subject, Status, Due_Date, Owner_ID |

**Key Relationships:**

- `Email_Record` --triggers--> Case Triage & Routing workflow (inbound email)
- `Email_Record` --depends_on--> `Case`
- `SMS_Record` --depends_on--> `Account`
- `Activity_Log` --depends_on--> `Case`, `Account`

---

## Domain 10: Problem & Trend Analysis

**System:** Internal (derived) | **ITIL:** Problem Management

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Problem_Record` | Root cause record for recurring incidents | high | Problem_ID, Title, Description, Related_Case_IDs (array), Root_Cause, Status (Open/Under_Investigation/Known_Error/Resolved), Impact_Scope (Individual/Segment/System_Wide), Affected_Accounts_Count, Owner_ID |
| `Trend_Alert` | Detected pattern/anomaly in case or interaction data | medium | Alert_ID, Pattern_Type (Volume_Spike/New_Issue_Type/Sentiment_Shift/SLA_Degradation), Severity (Low/Medium/High/Critical), Affected_Category, Detection_Date, Case_Count, Description |

**Key Relationships:**

- `Problem_Record` --triggers--> Root Cause Analysis workflow
- `Problem_Record` --depends_on--> `Case` (multiple)
- `Trend_Alert` --triggers--> Proactive Outreach workflow
- `Trend_Alert` --constrained_by--> case-handling-policy

---

[← Back to Ontology Overview](index.md)
