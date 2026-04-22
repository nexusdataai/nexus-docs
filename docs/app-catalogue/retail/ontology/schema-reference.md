# Schema Reference

Complete reference for the retail semantic schema — 12 domains, ~50 tables across 6 source systems, aligned to GS1 and NRF standards.

**Source File:** `enterprise-knowledge/retail-schema.yaml`

---

## Domain 1: Product & Catalog

**System:** ERP + POS | **GS1:** GTIN/GPC

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Product_Master` | Central product/SKU master — most connected entity in the ontology | high | SKU_ID, GTIN, Name, Category, Sub_Category, Brand, GPC_Code, Pack_Size, Unit_of_Measure, Cost_Price, Retail_Price, Shelf_Life_Days, Weight, Status (Active/Discontinued/Seasonal/New_Launch), Recyclability_Score |
| `Product_Attribute` | Extended product attributes for merchandising and filtering | low | Color, Size, Style, Material, Season |
| `Product_Hierarchy` | Merchandise hierarchy for reporting and planning | low | Department, Category, Sub_Category, Class, Sub_Class |

**Key Relationships:**

- `Product_Master` is referenced by ALL domains (most foundational entity)
- `Product_Master` --triggers--> Assortment Optimization workflow
- `Product_Master` --constrained_by--> sustainability-policy (Recyclability_Score targets)
- `Product_Hierarchy` --depends_on--> `Product_Master`
- `Product_Attribute` --depends_on--> `Product_Master`

---

## Domain 2: Customer & Loyalty

**System:** CRM/CDP + POS

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Customer_Profile` | Central customer master with loyalty and behavioral attributes | high | Customer_ID, Loyalty_ID, Email, Phone, Name, Segment (Enterprise/Premium/Standard/Casual), CLV, Churn_Risk_Score, First_Purchase_Date, Preferred_Channel, Preferred_Store, Status |
| `Loyalty_Account` | Loyalty program account with tier and points tracking | medium | Points_Balance, Tier (Gold/Silver/Bronze), Tier_Expiry, Lifetime_Points_Earned, Lifetime_Points_Redeemed |
| `Customer_Segment` | Marketing segmentation definitions | low | Segment_ID, Name, Criteria, Size, Avg_CLV |

**Key Relationships:**

- `Customer_Profile` --triggers--> Customer Churn Prediction workflow
- `Customer_Profile` --constrained_by--> data-privacy-policy (PII handling)
- `Loyalty_Account` --depends_on--> `Customer_Profile`
- `Customer_Segment` --depends_on--> `Customer_Profile` (multiple)
- `Customer_Profile` --syncs_to--> `Browsing_Session` (via CDP identity resolution)

---

## Domain 3: Transaction & Sales

**System:** POS + E-commerce

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Transaction` | Core point-of-sale and e-commerce transaction record | high | Txn_ID, Store_ID, Customer_ID, Date, Time, Channel (In_Store/Online/Mobile/Marketplace), Items_Count, Basket_Value, Discount_Amount, Payment_Method, Cashier_ID, Return_Flag |
| `Transaction_Line_Item` | Individual SKU line within a transaction | medium | Line_ID, Txn_ID, SKU_ID, Qty, Unit_Price, Discount, Promo_ID, Return_Flag |
| `Return_Transaction` | Customer return with reason and condition tracking | medium | Return_ID, Original_Txn_ID, SKU_ID, Qty, Reason (Defective/Wrong_Size/Changed_Mind/Not_As_Described), Condition (Resaleable/Damaged/Opened), Refund_Amount |

**Key Relationships:**

- `Transaction` --depends_on--> `Customer_Profile`, `Store_Master`
- `Transaction` --triggers--> Demand Forecast Generation workflow (real-time)
- `Transaction_Line_Item` --depends_on--> `Product_Master`, `Promotion`
- `Return_Transaction` --depends_on--> `Transaction`
- `Return_Transaction` --constrained_by--> return-policy

---

## Domain 4: Inventory & Warehouse

**System:** ERP/WMS | **GS1:** GLN/SSCC

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Inventory_Position` | Real-time stock per SKU x location | high | SKU_ID, Location_ID, Location_Type (Store/DC/Transit), Qty_On_Hand, Qty_Reserved, Qty_In_Transit, Days_of_Supply, Last_Updated |
| `Warehouse` | Distribution center and warehouse master | medium | Warehouse_ID, GLN, Name, Type (DC/Regional/Cross_Dock), Location, Capacity, Status |
| `Stock_Movement` | Inter-location stock transfer and adjustment records | medium | Movement_ID, SKU_ID, From_Location, To_Location, Qty, Type (Transfer/Receipt/Shipment/Adjustment), Date |
| `Shipment` | Outbound shipment with carrier and tracking | medium | Shipment_ID, SSCC, Origin, Destination, Carrier, Status, Ship_Date, ETA |

**Key Relationships:**

- `Inventory_Position` --triggers--> Inventory Rebalancing workflow (imbalance detection)
- `Inventory_Position` --depends_on--> `Product_Master`, `Store_Master`, `Warehouse`
- `Inventory_Position` --constrained_by--> inventory-policy (Days_of_Supply thresholds)
- `Stock_Movement` --depends_on--> `Inventory_Position`
- `Shipment` --depends_on--> `Stock_Movement`, `Warehouse`

---

## Domain 5: Store & Location

**System:** POS + HIS | **GS1:** GLN

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Store_Master` | Physical store master record | medium | Store_ID, GLN, Name, Format (Hypermarket/Supermarket/Convenience/Department/Specialty), Region, City, Sq_Footage, Operating_Hours, Status |
| `Store_Zone` | Zone/area within a store for traffic and merchandising | low | Zone_ID, Store_ID, Zone_Type (Entrance/Checkout/Aisle/Endcap/Window), Sq_Footage |
| `Register` | Point-of-sale register/terminal | low | Register_ID, Store_ID, Type (Manned/Self_Checkout/Mobile_POS), Status |

**Key Relationships:**

- `Store_Master` --depends_on--> `Inventory_Position` (store-level stock)
- `Store_Master` --triggers--> Store Performance Analysis workflow
- `Store_Zone` --depends_on--> `Store_Master`
- `Store_Zone` --triggers--> Planogram Compliance workflow (via Shelf_Condition)
- `Register` --depends_on--> `Store_Master`

---

## Domain 6: Pricing & Promotions

**System:** ERP + POS + Marketing

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Price_Record` | SKU price by store cluster with markdown tracking | high | SKU_ID, Store_Cluster, Regular_Price, Current_Price, Markdown_Pct, Effective_Date, End_Date |
| `Promotion` | Promotional campaign with mechanic and scope | high | Promo_ID, Name, Mechanic (BOGO/Pct_Off/Bundle/Loyalty_Points/Gift_With_Purchase), Discount_Value, Start_Date, End_Date, SKU_Scope, Store_Scope, Vendor_Funded_Pct, Status |
| `Competitor_Price` | Competitor pricing intelligence | medium | Competitor, SKU_Match_ID, Price, Promo_Flag, Channel, Capture_Date |
| `Markdown_Schedule` | Planned markdown cadence for sell-through optimization | medium | SKU_ID, Store_Cluster, Markdown_Step, Markdown_Pct, Start_Date, Target_Sell_Through |

**Key Relationships:**

- `Price_Record` --depends_on--> `Product_Master`
- `Price_Record` --constrained_by--> pricing-policy (margin floors)
- `Promotion` --triggers--> Demand Forecast Generation workflow
- `Promotion` --depends_on--> `Product_Master`, `Store_Master`
- `Competitor_Price` --triggers--> Price Optimization workflow
- `Markdown_Schedule` --depends_on--> `Inventory_Position` (sell-through velocity)

---

## Domain 7: Digital & E-commerce

**System:** Digital Analytics + E-commerce Platform

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Browsing_Session` | Customer digital session with engagement metrics | medium | Session_ID, Customer_ID, Device, Channel (Web/App/Mobile_Web), Start_Time, Pages_Viewed, Products_Viewed, Search_Queries, Cart_Events, Conversion_Flag |
| `Clickstream_Event` | Individual user interaction event | low | Event_ID, Session_ID, Event_Type (Page_View/Product_View/Add_to_Cart/Remove/Search/Checkout), SKU_ID, Timestamp |
| `Online_Order` | E-commerce order with fulfillment details | high | Order_ID, Customer_ID, Items, Delivery_Method (Ship_to_Home/BOPIS/Curbside/Same_Day), Delivery_Address, Promised_Date, Status, Fulfillment_Node |

**Key Relationships:**

- `Browsing_Session` --depends_on--> `Customer_Profile`
- `Browsing_Session` --triggers--> Personalization Engine workflow
- `Clickstream_Event` --depends_on--> `Browsing_Session`, `Product_Master`
- `Online_Order` --depends_on--> `Customer_Profile`, `Inventory_Position`
- `Online_Order` --triggers--> Order Fulfillment workflow (Fulfillment_Node allocation)

---

## Domain 8: Supplier & Procurement

**System:** ERP

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Vendor_Master` | Supplier/vendor master record | high | Vendor_ID, Name, Category, Country, Lead_Time_Days, Payment_Terms, Performance_Score (0-100), GPO_Flag, Status, Certification (Organic/Fair_Trade/B_Corp) |
| `Purchase_Order` | Formal procurement order to vendor | medium | PO_ID, Vendor_ID, SKU_ID, Qty, Unit_Cost, Total, Delivery_Date, Status, GPO_Contract_Flag |
| `Goods_Receipt` | Inbound goods receipt against purchase order | medium | GRN_ID, PO_ID, Qty_Ordered, Qty_Received, Qty_Rejected, Receipt_Date, Quality_Status |
| `Vendor_Co_Op` | Vendor co-operative funding and spend tracking | medium | Co_Op_ID, Vendor_ID, Fund_Amount, Spent_Amount, Period, Type (Advertising/Markdown/Display), Status |

**Key Relationships:**

- `Vendor_Master` --triggers--> Supplier Risk Scoring workflow
- `Vendor_Master` --constrained_by--> procurement-policy
- `Purchase_Order` --depends_on--> `Vendor_Master`, `Product_Master`
- `Purchase_Order` --triggers--> Procurement Spend Analysis workflow
- `Goods_Receipt` --validates--> `Purchase_Order` (three-way match: PO-GRN-Invoice)
- `Vendor_Co_Op` --depends_on--> `Vendor_Master`, `Promotion`

---

## Domain 9: Workforce & Labor

**System:** WFM/HR + IoT

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Employee` | Store employee master record | low | Employee_ID, Store_ID, Role (Cashier/Floor_Associate/Manager/Stocker), Employment_Type (Full_Time/Part_Time/Seasonal), Hourly_Rate |
| `Labor_Schedule` | Workforce shift schedule with actuals | medium | Schedule_ID, Employee_ID, Store_ID, Shift_Date, Start_Time, End_Time, Planned_Hours, Actual_Hours, Overtime_Flag, Agency_Flag |
| `Store_Traffic` | In-store foot traffic and dwell time by zone | medium | Store_ID, Zone_ID, Timestamp, Visitor_Count, Dwell_Time_Seconds |

**Key Relationships:**

- `Employee` --depends_on--> `Store_Master`
- `Labor_Schedule` --depends_on--> `Employee`, `Store_Master`
- `Labor_Schedule` --triggers--> Labor Optimization workflow (schedule vs traffic alignment)
- `Store_Traffic` --depends_on--> `Store_Master`, `Store_Zone`
- `Store_Traffic` --triggers--> Staffing Adjustment workflow (peak detection)

---

## Domain 10: In-Store IoT & Visual

**System:** IoT Sensors + Cameras

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Shelf_Condition` | Shelf compliance status from visual inspection | medium | Store_ID, Aisle, Shelf, SKU_ID, Compliance_Status (Compliant/Gap/Misplaced/Price_Missing), Capture_Time, Image_URL |
| `Temperature_Sensor` | Cold chain and ambient temperature monitoring | medium | Sensor_ID, Location, Temperature, Humidity, Timestamp, Excursion_Flag |
| `RFID_Tag` | RFID-based item-level tracking | low | Tag_ID, SKU_ID, Location, Last_Scan, Status |

**Key Relationships:**

- `Shelf_Condition` --depends_on--> `Store_Master`, `Product_Master`
- `Shelf_Condition` --triggers--> Planogram Compliance workflow (on Gap/Misplaced)
- `Temperature_Sensor` --triggers--> Cold Chain Excursion Alert workflow (on Excursion_Flag)
- `Temperature_Sensor` --constrained_by--> food-safety-policy
- `RFID_Tag` --depends_on--> `Product_Master`, `Inventory_Position`

---

## Domain 11: Market Intelligence

**System:** Social Media + Reviews + Web Scraping

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Product_Review` | Customer product review from multiple platforms | low | Review_ID, SKU_ID, Platform (Amazon/Google/Own_Site/Social), Rating (1-5), Review_Text, Sentiment_Score, Date |
| `Brand_Sentiment` | Aggregated brand sentiment by platform and topic | low | Brand, Category, Platform, Sentiment_Score, Topic, Mention_Count, Period |
| `Market_Trend` | Emerging category and consumer trend signals | medium | Trend_ID, Category, Trend_Description, Growth_Rate, Source (Social/Search/News), Detection_Date, Confidence |

**Key Relationships:**

- `Product_Review` --depends_on--> `Product_Master`
- `Product_Review` --triggers--> Product Quality Alert workflow (on low ratings)
- `Brand_Sentiment` --triggers--> Brand Health Monitoring workflow
- `Market_Trend` --triggers--> Assortment Planning workflow
- All ingested via `social-listening-feed` integration

---

## Domain 12: Sustainability & Compliance

**System:** ERP + IoT + External

| Table | Semantic | Risk | Key Fields |
|-------|----------|------|------------|
| `Product_Origin` | Product provenance and certification tracking | medium | SKU_ID, Supplier_ID, Origin_Country, Farm_Facility, Certification (Organic/Fair_Trade/Rainforest_Alliance), Batch_ID |
| `Carbon_Footprint` | Per-SKU carbon emissions across supply chain stages | medium | SKU_ID, Transport_Emissions, Warehouse_Emissions, Store_Emissions, Total_CO2e_Per_Unit, Calculation_Date |
| `Waste_Record` | Store-level waste and donation tracking | medium | SKU_ID, Store_ID, Qty_Wasted, Waste_Reason (Expired/Damaged/Overstock), Donation_Flag, Date |
| `Packaging` | Product packaging material and recyclability | low | SKU_ID, Pack_Type, Material (Plastic/Glass/Cardboard/Mixed), Recycled_Content_Pct, Recyclability_Score, Weight |

**Key Relationships:**

- `Product_Origin` --depends_on--> `Product_Master`, `Vendor_Master`
- `Product_Origin` --constrained_by--> sustainability-policy (certification requirements)
- `Carbon_Footprint` --depends_on--> `Product_Master`, `Shipment`
- `Carbon_Footprint` --triggers--> ESG Reporting workflow
- `Waste_Record` --depends_on--> `Product_Master`, `Store_Master`
- `Waste_Record` --triggers--> Waste Reduction workflow (threshold alerts)
- `Packaging` --depends_on--> `Product_Master`
- `Packaging` --constrained_by--> sustainability-policy (recycled content targets)

---

[← Back to Ontology Overview](index.md)
