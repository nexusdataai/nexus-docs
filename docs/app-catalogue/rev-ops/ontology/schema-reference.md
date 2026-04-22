# Schema Reference

Complete reference for the revenue operations semantic schema — 10 domains, ~40 tables across 6 source systems, aligned to MEDDPICC and ASC 606 standards.

**Source File:** `enterprise-knowledge/rev-ops-schema.yaml`

---

## Domain 1: Deal & Opportunity Management

**System:** Salesforce CRM | **Standard:** MEDDPICC

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Deal_Opportunity` | Core sales opportunity record with MEDDPICC scoring | high | Opp_ID, Account_ID, Name, Amount, ARR, Stage (Prospect/Discovery/Evaluation/Negotiation/Closed_Won/Closed_Lost), Close_Date, Owner_ID, Deal_Type (New_Business/Expansion/Renewal), Probability, MEDDPICC_Score (0-100), Forecast_Category (Commit/Best_Case/Pipeline/Omit), Created_Date, Days_in_Stage, Competitor_Present |
| `Opportunity_Line_Item` | Individual product line within a deal | medium | Line_ID, Opp_ID, Product_ID, Quantity, Unit_Price, Discount_Pct, ARR_Contribution, TCV |
| `Stage_History` | Stage transition audit trail for velocity analysis | medium | Opp_ID, From_Stage, To_Stage, Changed_Date, Changed_By, Days_in_Previous_Stage |

**Key Relationships:**

- `Deal_Opportunity` --triggers--> Deal Intelligence & Scoring workflow
- `Deal_Opportunity` --triggers--> Pipeline Risk Assessment workflow
- `Deal_Opportunity` --constrained_by--> MEDDPICC scoring methodology
- `Stage_History` --triggers--> Deal Velocity analysis (stage inflation detection)
- `Opportunity_Line_Item` --depends_on--> `Product_Catalog` (SKU resolution)

---

## Domain 2: Account & Buyer Intelligence

**System:** Salesforce CRM + Market Intel | **Standard:** MEDDPICC

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Account_Profile` | Customer/prospect master record with health metrics | high | Account_ID, Name, Industry, Employee_Count, ARR_Current, Segment (Enterprise/Mid_Market/SMB), Tier (Strategic/Growth/Standard), ICP_Score (0-100), LTV, NDR_Pct, Health_Score, Owner_ID, Status (Active/Prospect/Churned) |
| `Contact` | Individual contact persons at accounts | medium | Contact_ID, Account_ID, Name, Title, Role (Decision_Maker/Champion/Influencer/Blocker/End_User), Email, Phone, Engagement_Score, Last_Activity_Date |
| `Stakeholder_Map` | Deal-level buyer influence and sentiment map | high | Map_ID, Opp_ID, Contact_ID, Role_in_Deal (Economic_Buyer/Champion/Technical_Evaluator/Coach/Blocker), Sentiment (Positive/Neutral/Negative), Engagement_Level (High/Medium/Low/None), Last_Interaction_Date |

**Key Relationships:**

- `Account_Profile` --triggers--> Renewal & Expansion Prediction workflow
- `Account_Profile` --constrained_by--> ICP scoring model
- `Stakeholder_Map` --triggers--> Deal Intelligence & Scoring workflow (buyer coverage gaps)
- `Contact` --depends_on--> `Account_Profile`
- `Stakeholder_Map` --depends_on--> `Deal_Opportunity` and `Contact`

---

## Domain 3: Conversation Intelligence

**System:** Gong/Chorus/Call Platform | **Standard:** MEDDPICC

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Conversation_Record` | Call/meeting recording with NLP-extracted insights | high | Call_ID, Opp_ID, Account_ID, Participants (array), Duration_Minutes, Date, Transcript_URL, Sentiment_Score (-100 to +100), Talk_Ratio_Rep_Pct, Topics_Detected (array), Competitor_Mentions (array), Objections_Raised (array), Next_Steps_Committed, MEDDPICC_Elements_Extracted (JSON) |
| `Meeting_Action_Item` | Follow-up actions extracted from conversations | medium | Action_ID, Call_ID, Description, Owner, Due_Date, Status, Completed_Date |

**Key Relationships:**

- `Conversation_Record` --triggers--> Conversation & Email NLP workflow
- `Conversation_Record` --triggers--> Deal Intelligence & Scoring workflow (MEDDPICC extraction)
- `Conversation_Record` --triggers--> Competitive Win/Loss Analysis workflow (competitor mentions)
- `Meeting_Action_Item` --depends_on--> `Conversation_Record`

---

## Domain 4: Email & Digital Engagement

**System:** Email Platform + Calendar | **Standard:** MEDDPICC

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Email_Thread` | Aggregated email thread metrics per deal | high | Thread_ID, Opp_ID, Account_ID, Participants (array), Message_Count, Direction_Distribution (Inbound_Pct/Outbound_Pct), Avg_Response_Time_Hours, Executive_Involved_Flag, Last_Activity_Date, Ghost_Risk_Flag (days_since_last_reply >7) |
| `Calendar_Event` | Scheduled meetings and their outcomes | medium | Event_ID, Opp_ID, Account_ID, Type (Demo/Discovery/Negotiation/Technical/Executive), Attendees, Duration_Minutes, Date, Outcome, No_Show_Flag |
| `Digital_Engagement` | Website, content, and product trial activity | low | Account_ID, Source (Website/Content/Webinar/Product_Trial), Event_Type, Timestamp, Score |

**Key Relationships:**

- `Email_Thread` --triggers--> Conversation & Email NLP workflow
- `Email_Thread` --triggers--> Deal Intelligence & Scoring workflow (ghost risk detection)
- `Calendar_Event` --triggers--> Deal Intelligence & Scoring workflow (meeting cadence analysis)
- `Digital_Engagement` --triggers--> Renewal & Expansion Prediction workflow (trial activity)

---

## Domain 5: Product & Subscription

**System:** Product Platform + BSS | **Standard:** ASC 606

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Product_Catalog` | Master product and pricing catalog | medium | Product_ID, Name, Category, Type (Subscription/Usage/Professional_Services/Hardware), List_Price, Billing_Frequency (Monthly/Annual/Usage_Based) |
| `Subscription` | Active subscription record with usage and adoption metrics | high | Sub_ID, Account_ID, Product_ID, ARR, Start_Date, End_Date, Billing_Schedule, Status (Active/Cancelled/Paused), Auto_Renew, Usage_Pct, Feature_Adoption_Score |
| `Product_Usage` | Product and feature-level usage telemetry | medium | Account_ID, Product_ID, Feature, MAU, DAU, Usage_Trend (Growing/Stable/Declining), Last_Login, API_Calls, Storage_Used |

**Key Relationships:**

- `Subscription` --triggers--> Renewal & Expansion Prediction workflow
- `Product_Usage` --triggers--> Renewal & Expansion Prediction workflow (usage decline detection)
- `Product_Catalog` --constrained_by--> ASC 606 performance obligation rules
- `Opportunity_Line_Item` --depends_on--> `Product_Catalog`
- `Subscription` --depends_on--> `Account_Profile` and `Product_Catalog`

---

## Domain 6: Contract & Legal

**System:** Document Management + CLM | **Standard:** ASC 606

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Contract_Record` | Contract master with NLP-extracted terms | high | Contract_ID, Account_ID, Opp_ID, Type (MSA/Order_Form/SOW/Amendment/Renewal), Total_Value, Start_Date, End_Date, Auto_Renew, Performance_Obligations (array), Payment_Terms, Ramp_Schedule, Termination_Clause, Status (Draft/In_Review/Executed/Expired), Extraction_Confidence |
| `Quote` | CPQ-generated quote with approval workflow | medium | Quote_ID, Opp_ID, Version, Total_Amount, Discount_Pct, Approval_Status, Expiry_Date, CPQ_Generated |

**Key Relationships:**

- `Contract_Record` --triggers--> Quote-to-Cash Orchestration workflow (on execution)
- `Contract_Record` --triggers--> Revenue Leakage Detection workflow (billing reconciliation)
- `Contract_Record` --constrained_by--> ASC 606 performance obligation identification
- `Quote` --depends_on--> `Deal_Opportunity` and `Product_Catalog`

---

## Domain 7: Revenue & Finance

**System:** Oracle ERP/Finance | **Standard:** ASC 606

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Revenue_Schedule` | ASC 606 revenue recognition schedule | high | Schedule_ID, Contract_ID, Account_ID, Product_ID, Recognition_Method (Over_Time/Point_in_Time), Recognition_Start, Recognition_End, Monthly_Amount, Total_Amount, Status (Scheduled/Recognized/Deferred) |
| `AR_Invoice` | Accounts receivable invoice | high | Invoice_ID, Account_ID, Contract_ID, Amount, Due_Date, Status (Open/Paid/Overdue/Disputed), Aging_Bucket (Current/30/60/90/90_Plus) |
| `Payment` | Payment received against invoice | medium | Payment_ID, Invoice_ID, Amount, Date, Method, Applied_Flag |
| `Billing_Schedule` | Contract billing cadence and amounts | medium | Schedule_ID, Contract_ID, Billing_Date, Amount, Status |

**Key Relationships:**

- `Revenue_Schedule` --constrained_by--> ASC 606 recognition rules
- `Revenue_Schedule` --triggers--> Revenue Leakage Detection workflow (schedule vs actuals)
- `AR_Invoice` --triggers--> Revenue Leakage Detection workflow (billing vs collections)
- `Payment` --depends_on--> `AR_Invoice`
- `Billing_Schedule` --depends_on--> `Contract_Record`

---

## Domain 8: Pipeline & Forecast

**System:** Salesforce CRM + Internal | **Standard:** MEDDPICC

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Pipeline_Snapshot` | Weekly point-in-time pipeline snapshot for trend analysis | high | Snapshot_ID, Date, Segment, Stage, Deal_Count, Total_Amount, Weighted_Amount, Coverage_Ratio, created weekly |
| `Deal_Velocity` | Stage-level velocity and slip risk metrics per deal | medium | Opp_ID, Stage, Days_in_Stage, Conversion_Probability, Predicted_Close_Date, Slip_Risk_Score (0-100) |
| `Forecast_Submission` | Rep-level forecast with AI comparison | medium | Submission_ID, Rep_ID, Period, Commit_Amount, Best_Case_Amount, Pipeline_Amount, Submission_Date, AI_Forecast_Amount, Variance_Pct |
| `Renewal_Record` | Upcoming renewal with predicted outcome | high | Renewal_ID, Account_ID, Sub_ID, Renewal_Date, Current_ARR, Predicted_Outcome (Renew/Expand/Flat/Downsell/Churn), Probability, Risk_Drivers (array) |

**Key Relationships:**

- `Pipeline_Snapshot` --triggers--> Pipeline Risk Assessment workflow (weekly generation)
- `Deal_Velocity` --triggers--> Pipeline Risk Assessment workflow (stage inflation detection)
- `Forecast_Submission` --triggers--> Pipeline Risk Assessment workflow (variance reporting)
- `Renewal_Record` --triggers--> Renewal & Expansion Prediction workflow
- `Renewal_Record` --depends_on--> `Subscription` and `Account_Profile`

---

## Domain 9: Compensation & Commission

**System:** Oracle Finance + CRM

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Commission_Record` | Individual commission payout per closed deal | high | Commission_ID, Rep_ID, Opp_ID, Booking_Amount, Commission_Rate, Commission_Amount, Status (Pending/Approved/Paid/Disputed), Period |
| `Quota` | Rep-level quota and attainment tracking | medium | Quota_ID, Rep_ID, Period, Target_Amount, Attainment_Pct, Accelerator_Threshold |
| `Comp_Plan` | Compensation plan structure and components | low | Plan_ID, Name, Components (array: Base/Variable/Accelerator/SPIF), Effective_Date |

**Key Relationships:**

- `Commission_Record` --triggers--> Commission & Compensation workflow (on deal close)
- `Commission_Record` --depends_on--> `Deal_Opportunity` and `Comp_Plan`
- `Quota` --constrained_by--> `Comp_Plan` (accelerator thresholds)
- `Commission_Record` --syncs_to--> Oracle Finance (payout reconciliation)

---

## Domain 10: Market & Competitive Intelligence

**System:** External + Salesforce

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Competitive_Signal` | Competitor activity detected across deal touchpoints | high | Signal_ID, Competitor, Opp_ID, Source (Call/Email/Intent/Web), Signal_Type (Mention/Evaluation/Shortlist/Win/Loss), Detection_Date, Threat_Score (0-100) |
| `Intent_Data` | Third-party buyer intent signals | medium | Account_ID, Topic, Intent_Score, Source (Bombora/6sense/G2), Date |
| `Win_Loss_Record` | Post-deal outcome analysis record | medium | Record_ID, Opp_ID, Outcome (Won/Lost), Primary_Reason, Competitor_Won, Feedback_Source (Rep/Buyer/Third_Party) |

**Key Relationships:**

- `Competitive_Signal` --triggers--> Competitive Win/Loss Analysis workflow
- `Competitive_Signal` --triggers--> Deal Intelligence & Scoring workflow (threat scoring)
- `Intent_Data` --triggers--> Deal Intelligence & Scoring workflow (account prioritization)
- `Win_Loss_Record` --triggers--> Competitive Win/Loss Analysis workflow (pattern detection)
- All ingested via call NLP, email NLP, and third-party intent integrations

---

[← Back to Ontology Overview](index.md)
