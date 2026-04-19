# Schema Reference

Complete reference for the supply chain semantic schema — 12 domains, ~45 tables across 6 source systems, aligned to SCOR and GS1 standards.

**Source File:** `enterprise-knowledge/supply-chain-schema.yaml`

---

## Domain 1: Customer & Channel Management

**System:** Salesforce | **SCOR Process:** Deliver/Plan

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Account` | Customer/distributor/retailer master record | high | Account_ID, Name, Channel_Type (Modern Trade / General Trade / HORECA / E-commerce), Region, Tier (Platinum/Gold/Silver/Bronze), Credit_Limit, Payment_Terms, Status, Owner_ID |
| `Contact` | Customer contact persons | medium | Contact_ID, Account_ID, Name, Email, Phone, Role (Buyer/Finance/Logistics/Decision_Maker), Primary_Flag |
| `Campaign` | Promotion and trade marketing programs | medium | Campaign_ID, Name, Type (Discount/BOGO/Bundle/Display/Sampling), Start_Date, End_Date, Budget, Target_Segment, Status |

**Key Relationships:**

- `Account` --syncs_to--> `Oracle_AR_Customer` (via sf-oracle-supply-chain-sync)
- `Account` --triggers--> Customer Churn Prediction workflow
- `Account` --constrained_by--> pricing-discount-policy
- `Campaign` --triggers--> Demand Forecast Generation workflow
- `Campaign` --constrained_by--> pricing-discount-policy

---

## Domain 2: Sales & Demand Signals

**System:** Salesforce | **SCOR Process:** Plan/Deliver

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Opportunity` | Sales order / demand signal | medium | Opportunity_ID, Account_ID, Total_Value, Stage (Prospect/Negotiation/Closed_Won/Closed_Lost/Fulfilled), Close_Date, Delivery_Date, Region |
| `Opportunity_Line_Item` | Individual SKU line within an order | medium | Line_ID, Opportunity_ID, Product_ID (maps to SAP Material_Master), Quantity, Unit_Price, Discount_Pct, Delivery_Priority (Standard/Express/Critical) |
| `Forecast_Override` | Sales team manual forecast adjustments | low | Override_ID, Product_ID, Region, Period, Override_Qty, Justification, Submitted_By |

**Key Relationships:**

- `Opportunity` --triggers--> Order-to-Cash Monitoring workflow
- `Opportunity` --triggers--> Demand Forecast Generation workflow
- `Opportunity` --syncs_to--> SAP Sales Document (via sf-sap-demand-sync)
- `Opportunity_Line_Item` --depends_on--> `Material_Master` (SKU resolution across systems)
- `Opportunity` --constrained_by--> order-fulfillment-policy

---

## Domain 3: Material & Product Master

**System:** SAP | **SCOR Process:** Enable | **GS1:** GTIN for product identification

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Material_Master` (MARA) | Central product/SKU master — most connected entity in the ontology | high | Material_ID, **GTIN**, Description, Category (Carbonated/Juice/Water/Energy/Sports/Snacks/Tea), Sub_Category, Brand, Pack_Size, Pack_Config, Unit_of_Measure, Shelf_Life_Days, Weight_KG, Volume_L, Status (Active/Discontinued/Seasonal/New_Launch), Recycled_Content_Pct, Recyclability_Score |
| `Material_Plant` (MARC) | Plant-level MRP and production settings | medium | Material_ID, Plant_ID, MRP_Type, Reorder_Point, Safety_Stock, Lead_Time_Days, Lot_Size, Procurement_Type (In_House_Production/External_Procurement), ABC_Classification (A/B/C) |
| `Material_Storage` (MARD) | Storage-location-level stock information | medium | Material_ID, Plant_ID, Storage_Location, Unrestricted_Stock, Blocked_Stock, In_Quality_Stock |
| `Bill_of_Materials` | Recipe/BOM — raw materials to finished goods | medium | BOM_ID, Finished_Material_ID, Component_Material_ID, Component_Qty, Unit_of_Measure, Scrap_Pct, Valid_From, Valid_To |

**Key Relationships:**

- `Material_Master` is referenced by ALL 8 applications (most foundational entity)
- `Material_Plant` --constrained_by--> inventory-policy (safety stock rules)
- `Material_Master` --constrained_by--> sustainability-policy (packaging targets)
- `Bill_of_Materials` --depends_on--> `Material_Master` (finished goods and components)

---

## Domain 4: Inventory & Warehouse

**System:** SAP | **SCOR Process:** Plan/Deliver | **GS1:** Batch/Lot identification

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Inventory_Position` | Real-time stock per material x plant x batch | high | Material_ID, Plant_ID, Storage_Location, Batch_ID, Unrestricted_Qty, Reserved_Qty, In_Transit_Qty, Blocked_Qty, Valuation_Price, Last_Count_Date |
| `Batch_Master` | Batch/lot-level tracking for traceability | high | Batch_ID, Material_ID, Production_Date, Expiry_Date, Shelf_Life_Remaining_Days, Status (Unrestricted/Restricted/Blocked/In_Quality), Production_Order_ID, Plant_ID |
| `Plant_Master` | Manufacturing plant and DC master | medium | Plant_ID, **GLN**, Name, Type (Manufacturing/Distribution_Center/Depot/Co_Packer), Location (lat/long), Capacity_Units_Per_Day, Operating_Shifts, Status |
| `Storage_Location` | Sub-divisions within a plant | low | Storage_Location_ID, Plant_ID, Type (Raw_Material/WIP/Finished_Goods/Cold_Chain/Quarantine), Capacity, Temperature_Controlled |
| `Warehouse_Transfer` | Inter-warehouse stock movement orders | medium | Transfer_ID, From_Plant, To_Plant, Material_ID, Batch_ID, Qty, Status (Planned/Approved/In_Transit/Received/Cancelled), Ship_Date, ETA |

**Key Relationships:**

- `Inventory_Position` --triggers--> Inventory Rebalancing workflow (imbalance detection)
- `Batch_Master` --triggers--> Expiry Management workflow (near-expiry detection)
- `Inventory_Position` --constrained_by--> inventory-policy
- `Batch_Master` --constrained_by--> quality-policy (hold/release)
- `Plant_Master` --triggers--> ESG Reporting workflow

---

## Domain 5: Production & Quality

**System:** SAP | **SCOR Process:** Make

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Production_Order` | Manufacturing work order | high | Order_ID, Material_ID, Plant_ID, Qty_Planned, Qty_Produced, Qty_Scrapped, Production_Line, Shift, Start_Date, End_Date, Status (Planned/Released/In_Progress/Confirmed/Closed), Yield_Pct |
| `Production_Line` | Physical production line within a plant | medium | Line_ID, Plant_ID, Name, Technology, Capacity_Units_Per_Hour, Changeover_Time_Min, OEE_Target, Status |
| `Quality_Inspection_Lot` | QC inspection record per batch | high | Inspection_ID, Batch_ID, Material_ID, Inspection_Type (In_Process/Final/Incoming_Material/Stability), Test_Count, Pass_Count, Fail_Count, Result (Accepted/Rejected/Conditionally_Accepted), Inspector_ID, Date |
| `Quality_Test_Result` | Individual test measurement within an inspection | high | Result_ID, Inspection_ID, Test_Name (pH/Brix/Turbidity/Carbonation/etc.), Measured_Value, Unit, Spec_Lower_Limit, Spec_Upper_Limit, Pass_Flag |

**Key Relationships:**

- `Production_Order` --triggers--> Production Scheduling workflow
- `Quality_Inspection_Lot` --triggers--> Quality Deviation Response workflow (on failure)
- `Production_Order` --constrained_by--> quality-policy
- `Quality_Test_Result` --depends_on--> `Quality_Inspection_Lot`
- `Batch_Master` --depends_on--> `Production_Order`

---

## Domain 6: Procurement & Supplier

**System:** SAP | **SCOR Process:** Source

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Vendor_Master` | Supplier/vendor master record | high | Vendor_ID, Name, Country, City, Category (Raw_Material/Packaging/Co_Packer/Logistics/Services/Equipment), Lead_Time_Days, Payment_Terms, Risk_Rating (0-100), Status (Active/Probation/Suspended/Deactivated), Certification (ISO_9001/FSSC_22000/ISO_14001/Organic/Fair_Trade) |
| `Source_List` | Approved vendor-material mapping | medium | Source_ID, Material_ID, Vendor_ID, Valid_From, Valid_To, Priority (Primary/Secondary/Emergency), Fixed_Vendor_Flag |
| `Purchase_Requisition` | Internal request to procure material | medium | Requisition_ID, Material_ID, Qty, Plant_ID, Requested_By, Delivery_Date, Status (Open/Approved/Converted_to_PO/Rejected) |
| `Goods_Receipt` | Inbound material receipt against PO | medium | GRN_ID, PO_ID, Material_ID, Vendor_ID, Qty_Ordered, Qty_Received, Qty_Rejected, Receipt_Date, Quality_Check_Status (Pending/Passed/Failed/Waived) |

**Key Relationships:**

- `Vendor_Master` --triggers--> Supplier Risk Scoring workflow
- `Vendor_Master` --constrained_by--> procurement-policy, supply-chain-risk-policy
- `Source_List` --constrained_by--> supply-chain-risk-policy (single-source prohibition)
- `Goods_Receipt` --validates--> `Oracle_AP_Invoice` (three-way match)

---

## Domain 7: Logistics & Delivery

**System:** SAP | **SCOR Process:** Deliver/Return | **GS1:** SSCC for shipment tracking

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Delivery_Document` | Outbound delivery to customer | high | Delivery_ID, Sales_Order_ID (maps to SF Opportunity), Ship_To_Account_ID, Material_ID, Qty, Batch_ID, Ship_Date, Planned_Arrival, Actual_Arrival, Carrier, POD_Status (Pending/Signed/Disputed/Not_Delivered), **SSCC** |
| `Shipment` | Vehicle/route-level shipment | medium | Shipment_ID, Route, Vehicle_ID, Driver, Load_Weight_KG, Departure_Time, Arrival_Time, Status (Loading/In_Transit/Delivered/Delayed), Cost |
| `Return_Order` | Customer returns and reverse logistics | medium | Return_ID, Delivery_ID, Material_ID, Qty, Return_Reason (Damaged/Expired/Wrong_Item/Overstock/Quality_Issue), Condition (Resaleable/Damaged/Expired/Contaminated), Disposition (Restock/Destroy/Rework/Donate/Vendor_Return), Credit_Note_ID |

**Key Relationships:**

- `Delivery_Document` --syncs_to--> `Oracle_AR_Invoice` (triggers billing)
- `Return_Order` --syncs_to--> `Oracle_AR_Credit_Note`
- `Delivery_Document` --constrained_by--> order-fulfillment-policy
- `Shipment` --constrained_by--> sustainability-policy (route emissions)

---

## Domain 8: Oracle Finance

**System:** Oracle | **SCOR Process:** Enable

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Oracle_AR_Customer` | Accounts Receivable customer record | high | Customer_ID (maps to SF Account), Customer_Name, Credit_Limit, AR_Balance, Collection_Priority, Payment_Terms, Currency, Status |
| `Oracle_AR_Invoice` | Customer invoice for goods delivered | high | Invoice_ID, Customer_ID, Invoice_Date, Due_Date, Total_Amount, Tax_Amount, Status (Open/Partially_Paid/Paid/Overdue/Disputed/Written_Off), Linked_Delivery_ID |
| `Oracle_AR_Payment` | Payment received against invoice | high | Payment_ID, Invoice_ID, Customer_ID, Amount, Payment_Date, Payment_Method, Applied_Flag |
| `Oracle_AR_Credit_Note` | Credit memo for returns/disputes | high | Credit_Note_ID, Customer_ID, Invoice_ID, Amount, Reason (Return/Price_Adjustment/Dispute_Resolution/Damaged_Goods/Promotional_Credit), Status, Approval_Status |
| `Oracle_GL_Journal` | General ledger journal entries | high | Journal_ID, Period_Name, Journal_Status (Posted/Unposted/Reversed), Debit_Amount, Credit_Amount, Account_Code, Description, Source_Module |
| `Oracle_GL_Period` | Accounting period open/close status | high | Period_ID, Period_Name, Year, Status (Open/Closed/Permanently_Closed), Close_Date |

**Key Relationships:**

- `Oracle_AR_Customer` --syncs_to--> `Account` (bidirectional via sf-oracle-supply-chain-sync)
- `Oracle_GL_Journal` --constrained_by--> close-window-policy
- `Oracle_AR_Invoice` --depends_on--> `Delivery_Document`

---

## Domain 9: Oracle Operations

**System:** Oracle | **SCOR Process:** Source/Enable

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Oracle_AP_Invoice` | Vendor invoice for goods/services | high | Invoice_ID, Vendor_ID, PO_ID, Invoice_Date, Due_Date, Total_Amount, Tax_Amount, Status (Pending/Validated/Approved/Paid/On_Hold/Disputed), Three_Way_Match_Status (Matched/Qty_Mismatch/Price_Mismatch/GRN_Missing/Under_Review) |
| `Oracle_AP_Payment` | Payment issued to vendor | high | Payment_ID, Invoice_ID, Vendor_ID, Amount, Payment_Date, Payment_Method (Bank_Transfer/Check/Wire/ACH), Check_Number, Bank_Account |
| `Oracle_Purchase_Order` | Formal procurement order to vendor | high | PO_ID, Vendor_ID, Material_ID, Qty, Unit_Price, Total_Amount, Delivery_Date, Plant_ID, Status (Draft/Approved/Sent/Partially_Received/Fully_Received/Closed), Contract_ID |
| `Oracle_Cost_Accounting` | Product and production cost tracking | high | Cost_ID, Material_ID, Cost_Type (Standard/Actual), Material_Cost, Labor_Cost, Overhead_Cost, Freight_Cost, Total_Unit_Cost, Period, Plant_ID |
| `Oracle_Fixed_Asset` | Plant equipment and capital assets | medium | Asset_ID, Name, Category (Production_Line/Warehouse_Equipment/Vehicle/Refrigeration/IT_Systems), Plant_ID, Acquisition_Date, Acquisition_Cost, Depreciation_Method, Net_Book_Value, Status (In_Service/Under_Maintenance/Retired/Disposed) |
| `Oracle_Budget` | Operating and capital budget | medium | Budget_ID, Cost_Center, Period, Category (OPEX/CAPEX), Planned_Amount, Actual_Amount, Variance_Amount, Variance_Pct |

**Key Relationships:**

- `Oracle_AP_Invoice` --validates--> `Goods_Receipt` (three-way match: PO-GRN-Invoice)
- `Oracle_Purchase_Order` --triggers--> Procurement Spend Analysis workflow
- `Oracle_Purchase_Order` --constrained_by--> procurement-policy
- `Oracle_Cost_Accounting` --syncs_to--> sap-oracle-finance-sync

---

## Domain 10: Document Intelligence

**System:** Google Drive | **SCOR Process:** Enable

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Contract_Document` | Vendor contracts (NLP-extracted) | high | Contract_ID, Vendor_ID, Document_Path, Effective_Date, Expiry_Date, Contracted_Price, Volume_Commitment, SLA_Terms, Penalty_Clauses, Auto_Renewal, Extraction_Confidence |
| `Sustainability_Report` | ESG reports (NLP-extracted) | medium | Report_ID, Document_Path, Report_Type (Annual/Quarterly/Audit), Period, KPIs_Extracted, Targets, Actuals, Framework (GRI/SASB/CDP/TCFD) |

**Key Relationships:**

- `Contract_Document` --depends_on--> `Vendor_Master`
- `Contract_Document` --triggers--> Supplier Risk Scoring workflow
- Both extracted via `unstructured-extraction` integration pipeline

---

## Domain 11: Market Intelligence

**System:** Social Listening | **SCOR Process:** Plan/Enable

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Market_Signal` | External event impacting supply chain | medium | Signal_ID, Source (News/Social_Media/Government/Weather_Service/Port_Authority), Event_Type (Supply_Disruption/Regulatory_Change/Competitor_Action/Weather_Event/Port_Congestion/Labor_Strike), Location, Severity (Low/Medium/High/Critical), Affected_Commodity, Timestamp |
| `Brand_Sentiment` | Consumer/trade sentiment | low | Sentiment_ID, Brand, Product_Category, Platform (Twitter_X/Reddit/Instagram/News/Review_Site/Industry_Forum), Sentiment_Score (-100 to +100), Topic, Mention_Count, Period |
| `Commodity_Price` | Raw material market prices | medium | Price_ID, Commodity (Sugar/High_Fructose_Corn_Syrup/PET_Resin/Aluminum/Glass/Concentrate/CO2), Price_Per_Unit, Currency, Unit, Date, Source, Change_Pct_30D |

**Key Relationships:**

- `Market_Signal` --triggers--> Disruption Response workflow (High/Critical severity)
- `Market_Signal` --constrained_by--> supply-chain-risk-policy
- All ingested via `social-listening-feed` integration

---

## Domain 12: File Processing

**System:** File Uploads | **SCOR Process:** Source/Enable

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Invoice_Upload` | Vendor invoice from PDF/scan (OCR+LLM) | medium | Upload_ID, File_Path, Vendor_Name_Extracted, Invoice_Number_Extracted, Amount_Extracted, Line_Items, Extraction_Confidence, Matched_PO_ID, Validation_Status (Validated/Needs_Review/Rejected/Pending) |
| `Lab_Report_Upload` | QC lab test results from PDF/Excel | high | Upload_ID, File_Path, Material_ID, Batch_ID, Tests_Extracted, Results, Spec_Compliance, Extraction_Confidence, Inspector_Name |

**Key Relationships:**

- `Invoice_Upload` --triggers--> Invoice Processing workflow
- `Lab_Report_Upload` --triggers--> Quality Deviation Response workflow (if spec non-compliant)
- Both processed via `unstructured-extraction` integration pipeline

---

[← Back to Ontology Overview](index.md)
