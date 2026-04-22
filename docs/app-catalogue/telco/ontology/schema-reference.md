# Schema Reference

Complete reference for the telco semantic schema — 12 domains, ~50 tables across 6 source systems, aligned to TMF Open APIs and eTOM.

**Source File:** `enterprise-knowledge/telco-schema.yaml`

---

## Domain 1: Subscriber & Account Management

**System:** BSS | **TMF:** TMF629/TMF632

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Subscriber_Master` | Central subscriber/SIM master — most connected entity in the ontology | high | MSISDN, IMSI, Account_ID, Name, DOB, Segment (Postpaid/Prepaid/Enterprise/IoT), Tier (Platinum/Gold/Silver/Bronze), Tenure_Months, Contract_End_Date, Status (Active/Suspended/Churned), Churn_Risk_Score, CLV, PCP_Rep_ID |
| `Account_Hierarchy` | Family/corporate account grouping structure | medium | Parent_Account, Child_Accounts, Relationship_Type (Individual/Family/Corporate) |
| `Contact` | Customer contact persons | medium | Contact_ID, Account_ID, Name, Email, Phone, Role (Decision_Maker/User/Billing) |

**Key Relationships:**

- `Subscriber_Master` --triggers--> Churn Prediction workflow
- `Subscriber_Master` --triggers--> CLV Calculation workflow
- `Subscriber_Master` --constrained_by--> consent-policy
- `Account_Hierarchy` --depends_on--> `Subscriber_Master` (multiple)
- `Contact` --depends_on--> `Subscriber_Master`

---

## Domain 2: Plan & Product Catalog

**System:** BSS | **TMF:** TMF622/TMF620

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Plan_Product` | Voice/data/bundle plan definition in the catalog | high | Plan_ID, Name, Type (Voice/Data/Bundle/IoT), Monthly_Fee, Data_Allowance_GB, Voice_Minutes, SMS_Allowance, Validity_Days, Contract_Term_Months, Status (Active/Retired/Promotional) |
| `Product_Instance` | Active plan assignment to a subscriber | medium | Instance_ID, Subscriber_MSISDN, Plan_ID, Activation_Date, Expiry_Date, Status, Add_Ons (array) |
| `Add_On` | Supplementary product add-on | low | Add_On_ID, Name, Type (Data_Booster/Roaming/Streaming/Insurance/Device_Protection), Price, Validity |

**Key Relationships:**

- `Plan_Product` --triggers--> Revenue Assurance workflow (on price change)
- `Product_Instance` --depends_on--> `Subscriber_Master`, `Plan_Product`
- `Product_Instance` --triggers--> Upsell/Cross-sell Recommendation workflow
- `Add_On` --depends_on--> `Plan_Product`

---

## Domain 3: Usage & CDR

**System:** CDR/Network Data Lake | **TMF:** TMF635

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `CDR_Record` | Call detail record — core usage event | high | CDR_ID, MSISDN, IMSI, Call_Type (Voice_MO/Voice_MT/Data/SMS/MMS/Roaming), A_Party, B_Party, Cell_ID, Duration_Seconds, Data_Volume_MB, Timestamp, Rating_Status |
| `Data_Session` | Packet data session record | medium | Session_ID, MSISDN, Cell_ID, Start_Time, End_Time, Volume_Up_MB, Volume_Down_MB, Bearer_Type (4G/5G), QoS_Class |
| `Aggregated_Usage` | Pre-aggregated usage summaries per subscriber | medium | MSISDN, Period (Daily/Weekly/Monthly), Total_Voice_Min, Total_Data_GB, Total_SMS, Roaming_Events, Peak_Hour_Usage_Pct |

**Key Relationships:**

- `CDR_Record` --depends_on--> `Subscriber_Master`
- `CDR_Record` --triggers--> Revenue Assurance workflow (rating validation)
- `CDR_Record` --triggers--> Fraud Detection workflow (anomaly detection)
- `Data_Session` --depends_on--> `Network_Element`, `Cell_Site`
- `Aggregated_Usage` --triggers--> Churn Prediction workflow

---

## Domain 4: Network Inventory

**System:** OSS | **TMF:** TMF639

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Network_Element` | Physical/logical network node | high | Element_ID, Type (eNodeB/gNodeB/Router/Switch/OLT/Core_Node), Vendor (Ericsson/Nokia/Huawei/Samsung), Model, Software_Version, Status (Operational/Degraded/Down/Planned), Location, Parent_Element |
| `Cell_Site` | Tower/site hosting radio equipment | high | Site_ID, Location_Lat_Long, Site_Type (Macro/Micro/Small_Cell/Indoor), Tower_Type (Monopole/Lattice/Rooftop/COW), Height_Meters, Sector_Count, Technology_Layers (array: 2G/3G/4G/5G), Status, Lease_Expiry |
| `Sector` | Individual radio sector within a cell site | medium | Sector_ID, Cell_Site_ID, Azimuth, Beam_Width, Tilt_Mechanical, Tilt_Electrical, Frequency_Band, Technology, Antenna_Model |
| `Link` | Transport link between network elements | medium | Link_ID, Type (Fiber/Microwave/Satellite), From_Element, To_Element, Capacity_Mbps, Utilization_Pct, Status |

**Key Relationships:**

- `Network_Element` --triggers--> Alarm Correlation workflow (on status change)
- `Cell_Site` --triggers--> Coverage Optimization workflow
- `Cell_Site` --constrained_by--> spectrum-license-policy (power/frequency limits)
- `Sector` --depends_on--> `Cell_Site`
- `Link` --depends_on--> `Network_Element` (from and to)

---

## Domain 5: Alarm & Fault Management

**System:** OSS | **TMF:** TMF642

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Alarm` | Network alarm event from element management | high | Alarm_ID, Element_ID, Severity (Critical/Major/Minor/Warning/Clear), Category (Equipment/Communication/Processing/Environmental/QoS), Probable_Cause, Timestamp, Acknowledged_By, Status (Active/Cleared/Acknowledged) |
| `Fault_Ticket` | Trouble ticket correlating one or more alarms | high | Ticket_ID, Alarm_IDs (array), Root_Cause, Affected_Elements, Affected_Subscribers_Count, Status (Open/In_Progress/Resolved), MTTR_Hours, Resolution |
| `Correlation_Group` | AI-correlated alarm cluster | medium | Group_ID, Root_Alarm_ID, Correlated_Alarm_IDs, Correlation_Confidence, Timestamp |

**Key Relationships:**

- `Alarm` --depends_on--> `Network_Element`
- `Alarm` --triggers--> Alarm Correlation workflow (real-time)
- `Fault_Ticket` --depends_on--> `Alarm` (multiple)
- `Fault_Ticket` --triggers--> Field Dispatch workflow (on priority threshold)
- `Correlation_Group` --depends_on--> `Alarm` (multiple)

---

## Domain 6: Performance Counters

**System:** OSS | **TMF:** TMF628

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Performance_Counter` | Network KPI measurement per element | high | Counter_ID, Element_ID, Counter_Name (Throughput_DL/Throughput_UL/Latency/Packet_Loss/PRB_Utilization/RSRP/RSRQ/Call_Drop_Rate/Handover_Success_Rate), Value, Unit, Granularity (15min/Hourly/Daily), Timestamp |
| `SLA_Metric` | Service-level agreement metric tracking | high | SLA_ID, Service_ID, Metric_Name (Availability/Latency/Throughput/Jitter), Target_Value, Actual_Value, Breach_Flag, Period |
| `KQI` | Key Quality Indicator per service type | medium | KQI_ID, Service_Type (Voice/Data/Video/IoT), Quality_Score (0-100), Components (array), Timestamp |

**Key Relationships:**

- `Performance_Counter` --depends_on--> `Network_Element`
- `Performance_Counter` --triggers--> Capacity Planning workflow (on utilization threshold)
- `SLA_Metric` --triggers--> SLA Breach Notification workflow (on Breach_Flag)
- `SLA_Metric` --constrained_by--> sla-policy
- `KQI` --depends_on--> `Performance_Counter` (derived)

---

## Domain 7: Billing & Revenue

**System:** BSS | **TMF:** TMF678/TMF654

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Billing_Record` | Customer invoice per billing cycle | high | Invoice_ID, Account_ID, Billing_Period, Total_Charge, Recurring_Charges, Usage_Charges, One_Time_Charges, Taxes, Credits, Status (Open/Paid/Overdue) |
| `Payment` | Payment received against invoice | medium | Payment_ID, Account_ID, Amount, Date, Method (Card/Bank/Mobile_Money/Voucher), Status |
| `Prepay_Balance` | Prepaid subscriber balance tracking | medium | MSISDN, Balance_Type (Airtime/Data/Bonus), Current_Balance, Last_Topup_Date, Last_Topup_Amount, Expiry_Date |
| `Revenue_Leakage` | Detected revenue leakage event | high | Leakage_ID, Type (CDR_Drop/Rating_Error/Unbilled_Service/Config_Error), Amount, Detection_Date, Resolution_Status |

**Key Relationships:**

- `Billing_Record` --depends_on--> `Subscriber_Master`, `CDR_Record`
- `Billing_Record` --triggers--> Collections workflow (on Overdue status)
- `Payment` --depends_on--> `Billing_Record`
- `Prepay_Balance` --depends_on--> `Subscriber_Master`
- `Revenue_Leakage` --triggers--> Revenue Assurance workflow

---

## Domain 8: Customer Interactions

**System:** CRM/Contact Center | **TMF:** TMF621

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Service_Request` | Customer service ticket/case | high | SR_ID, Subscriber_MSISDN, Category (Billing/Network/Plan_Change/Complaint/Inquiry), Priority, Status, Channel (Phone/Chat/Email/Social/Store), Agent_ID, Resolution_Time_Hours, Repeat_Contact_Flag |
| `Interaction_Record` | Individual customer interaction event | medium | Interaction_ID, Subscriber_MSISDN, Channel, Start_Time, Duration, Sentiment_Score, Topics, Disposition, Agent_ID |
| `NPS_Survey` | Net Promoter Score survey response | low | Survey_ID, Subscriber_MSISDN, Score (0-10), Category (Promoter/Passive/Detractor), Verbatim, Survey_Date |
| `Campaign` | Marketing/retention campaign definition | medium | Campaign_ID, Name, Type (Retention/Upsell/Win_Back/Acquisition), Target_Segment, Offer, Channel, Start_Date, End_Date, Conversion_Rate |

**Key Relationships:**

- `Service_Request` --depends_on--> `Subscriber_Master`
- `Service_Request` --triggers--> Repeat Contact Analysis workflow (on Repeat_Contact_Flag)
- `Interaction_Record` --depends_on--> `Subscriber_Master`
- `NPS_Survey` --triggers--> Churn Prediction workflow (Detractor score)
- `Campaign` --triggers--> Upsell/Cross-sell Recommendation workflow

---

## Domain 9: Field & Site Operations

**System:** Field/CMMS | **TMF:** TMF621

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Work_Order` | Field work order for site operations | high | WO_ID, Type (Install/Repair/Maintenance/Survey), Site_ID, Priority, Status (Open/Assigned/In_Progress/Completed/Failed), Assigned_Technician, SLA_Hours, Actual_Hours |
| `Technician` | Field technician resource | medium | Tech_ID, Name, Skills (array: RF/Fiber/Power/Civil), Certifications, Home_Location, Vehicle_ID, Availability_Status |
| `Equipment_Telemetry` | Remote monitoring of site equipment | medium | Site_ID, Equipment_Type (Battery/Generator/HVAC/Antenna), Parameter (Voltage/Temperature/Fuel_Level/Tilt), Value, Timestamp, Alert_Flag |
| `Site_Survey` | Pre-build or audit site survey record | low | Survey_ID, Location, Type (New_Site/Upgrade/Audit), Coverage_Test_Results, Access_Notes, Power_Availability, Lease_Status |

**Key Relationships:**

- `Work_Order` --depends_on--> `Cell_Site`, `Fault_Ticket`
- `Work_Order` --triggers--> SLA Breach Notification workflow (on SLA threshold)
- `Technician` --depends_on--> `Work_Order`
- `Equipment_Telemetry` --triggers--> Preventive Maintenance workflow (on Alert_Flag)
- `Site_Survey` --depends_on--> `Cell_Site`

---

## Domain 10: Spectrum & RF

**System:** OSS + Regulatory | **TMF:** TMF639

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Spectrum_License` | Regulatory spectrum license record | high | License_ID, Band, Bandwidth_MHz, Region, Expiry_Date, Power_Limit_dBm, Coverage_Obligation, License_Fee, Regulator |
| `Spectrum_Utilization` | Spectrum usage measurement per cell | medium | Cell_ID, Band, Technology, Allocated_MHz, Utilized_Pct, Refarming_Eligible, Timestamp |
| `Interference_Event` | Detected interference incident | medium | Event_ID, Cell_ID, Band, Source (Internal/External), Severity, Duration, Impact_Description, Detection_Date |

**Key Relationships:**

- `Spectrum_License` --constrained_by--> regulatory-compliance-policy
- `Spectrum_License` --triggers--> License Renewal workflow (on expiry approach)
- `Spectrum_Utilization` --depends_on--> `Cell_Site`, `Spectrum_License`
- `Spectrum_Utilization` --triggers--> Spectrum Refarming workflow (on low utilization)
- `Interference_Event` --depends_on--> `Cell_Site`

---

## Domain 11: Market & Competitive Intelligence

**System:** External + CRM

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Competitor_Plan` | Competitor product/plan benchmark | medium | Competitor, Plan_Name, Type, Price, Data_Allowance, Voice_Minutes, Channel, Effective_Date |
| `Market_Share` | Regional market share snapshot | low | Region, Operator, Subscriber_Count, Market_Share_Pct, Period, Source |
| `Churn_Event` | Subscriber churn event record | high | MSISDN, Churn_Type (Voluntary_Port/Non_Renewal/Deactivation), Churn_Date, Destination_Operator, Churn_Driver (Price/Network/Service/Life_Event), Revenue_Lost |

**Key Relationships:**

- `Competitor_Plan` --triggers--> Competitive Response workflow (on price change)
- `Market_Share` --triggers--> Market Strategy workflow
- `Churn_Event` --depends_on--> `Subscriber_Master`
- `Churn_Event` --triggers--> Win-Back Campaign workflow
- All ingested via `market-intelligence-feed` integration

---

## Domain 12: Regulatory & Compliance

**System:** Internal + External

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `QoS_Report` | Quality of service regulatory filing | high | Report_ID, Report_Type (Quarterly/Annual), Regulator, Metrics, Status (Draft/Validated/Filed), Filing_Date, Deadline |
| `Consent_Record` | Subscriber consent/preference record | high | MSISDN, Consent_Type (Marketing/Data_Processing/Location/Analytics), Status (Granted/Withdrawn), Date, Channel |
| `Regulatory_Publication` | Regulatory circular/amendment (NLP-extracted) | medium | Publication_ID, Issuer, Title, Date, Effective_Date, Impact_Areas, Compliance_Status |
| `Interconnect_Record` | Inter-operator traffic and settlement record | medium | Partner_Operator, Traffic_Type (Voice/SMS/Data), Direction (Inbound/Outbound), Volume, Settlement_Rate, Period, Dispute_Flag |

**Key Relationships:**

- `QoS_Report` --depends_on--> `Performance_Counter`, `SLA_Metric`
- `QoS_Report` --constrained_by--> regulatory-compliance-policy
- `Consent_Record` --depends_on--> `Subscriber_Master`
- `Consent_Record` --constrained_by--> data-privacy-policy
- `Regulatory_Publication` --triggers--> Regulatory Change Intelligence workflow
- `Interconnect_Record` --triggers--> Settlement Reconciliation workflow (on Dispute_Flag)

---

[← Back to Ontology Overview](index.md)
