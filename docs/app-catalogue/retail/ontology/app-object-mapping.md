# Application-Object Mapping

Minimum required ontology objects per application, with relationship details and cross-application dependency analysis.

---

## App 1: Customer 360 & Loyalty

**NRF:** Customer | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Customer_Profile` | CRM/CDP | Core entity — golden customer record | — |
| `Loyalty_Account` | CRM/CDP | Loyalty tier, points balance, rewards history | depends_on -> Customer_Profile |
| `Transaction` | POS | In-store purchase history and basket analysis | depends_on -> Customer_Profile |
| `Transaction_Line_Item` | POS | SKU-level purchase detail for affinity analysis | depends_on -> Transaction |
| `Browsing_Session` | E-commerce | Online browsing behavior and session context | depends_on -> Customer_Profile |
| `Product_Review` | Social/Reviews | Customer-authored product reviews and ratings | depends_on -> Customer_Profile, Product_Master |
| `Brand_Sentiment` | Social Listening | Brand perception across social channels | — |
| `Customer_Segment` | CRM/CDP | Behavioral and demographic segmentation | depends_on -> Customer_Profile |
| `Promotion` | ERP | Promotion response and offer history | constrained_by -> pricing-promotion-policy |
| `Store_Master` | ERP | Preferred store and location context | — |

**Policies:** customer-data-privacy-policy, pricing-promotion-policy
**Workflows:** customer-360-loyalty
**Integrations:** cdp-pos-sync, ecom-digital-feed

---

## App 2: Demand Forecasting

**NRF:** Merchandising / Supply Chain | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Product_Master` | ERP | SKU attributes, hierarchy, lifecycle stage | — |
| `Transaction` | POS | Historical sales data for demand signal | depends_on -> Product_Master |
| `Inventory_Position` | ERP | Current stock for demand-supply balancing | depends_on -> Product_Master, Store_Master |
| `Promotion` | ERP | Promotion calendar for lift modeling | constrained_by -> pricing-promotion-policy |
| `Store_Master` | ERP | Store attributes, format, region, climate zone | — |
| `Market_Trend` | Social/External | External trend signals (search trends, category data) | — |
| `Brand_Sentiment` | Social Listening | Consumer sentiment as demand indicator | — |
| `Product_Hierarchy` | ERP | Category/subcategory for aggregate forecasting | depends_on -> Product_Master |
| `Warehouse` | ERP/WMS | DC capacity and lead time for supply planning | — |
| `Store_Traffic` | IoT | Foot traffic patterns for conversion-based forecasting | depends_on -> Store_Master |

**Policies:** inventory-fulfillment-policy, data-freshness-policy
**Workflows:** demand-forecast-generation
**Integrations:** pos-erp-sync, social-market-intelligence-feed

---

## App 3: Personalization

**NRF:** Customer / Digital Commerce | **Minimum Objects: 9**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Customer_Profile` | CRM/CDP | Customer identity and preference profile | — |
| `Transaction` | POS | Purchase history for collaborative filtering | depends_on -> Customer_Profile |
| `Browsing_Session` | E-commerce | Session context for real-time recommendations | depends_on -> Customer_Profile |
| `Clickstream_Event` | E-commerce | Page views, searches, cart actions for intent modeling | depends_on -> Browsing_Session |
| `Product_Master` | ERP | Product attributes for content-based filtering | — |
| `Product_Review` | Social/Reviews | Review sentiment for recommendation ranking | depends_on -> Product_Master |
| `Loyalty_Account` | CRM/CDP | Tier-based personalization and reward offers | depends_on -> Customer_Profile |
| `Online_Order` | E-commerce | Online purchase history and fulfillment preferences | depends_on -> Customer_Profile |
| `Promotion` | ERP | Personalized offer targeting and eligibility | constrained_by -> pricing-promotion-policy |

**Policies:** customer-data-privacy-policy, pricing-promotion-policy
**Workflows:** personalization-recommendation
**Integrations:** cdp-pos-sync, ecom-digital-feed

---

## App 4: Price Optimization

**NRF:** Merchandising | **Minimum Objects: 9**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Product_Master` | ERP | SKU master with cost, category, lifecycle | — |
| `Transaction` | POS | Price elasticity signals from historical sales | depends_on -> Product_Master |
| `Price_Record` | ERP | Current and historical pricing data | depends_on -> Product_Master |
| `Promotion` | ERP | Promotion effectiveness and cannibalization | constrained_by -> pricing-promotion-policy |
| `Competitor_Price` | External | Competitive price intelligence for KVI matching | — |
| `Markdown_Schedule` | ERP | Seasonal markdown cadence and clearance pricing | constrained_by -> pricing-promotion-policy |
| `Inventory_Position` | ERP | Stock levels for markdown urgency and depth | depends_on -> Product_Master |
| `Product_Attribute` | ERP | Brand, pack size, private label flag for price architecture | depends_on -> Product_Master |
| `Customer_Profile` | CRM/CDP | Segment-level price sensitivity for targeted pricing | — |

**Policies:** pricing-promotion-policy, loss-prevention-policy
**Workflows:** price-optimization, markdown-management
**Integrations:** pos-erp-sync, social-market-intelligence-feed

---

## App 5: Inventory & Fulfillment

**NRF:** Supply Chain | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Inventory_Position` | ERP/WMS | Stock on hand per SKU x location x batch | depends_on -> Product_Master, Store_Master |
| `Warehouse` | ERP/WMS | DC locations, capacity, fulfillment capability | — |
| `Store_Master` | ERP | Store locations, ship-from-store eligibility | — |
| `Online_Order` | E-commerce | Online order routing and fulfillment tracking | depends_on -> Customer_Profile |
| `Shipment` | ERP/WMS | Carrier, tracking, estimated delivery | depends_on -> Online_Order |
| `Stock_Movement` | ERP/WMS | Receipts, issues, transfers, adjustments | depends_on -> Inventory_Position |
| `Return_Transaction` | POS/E-commerce | Return processing and inventory credit | depends_on -> Transaction |
| `Product_Master` | ERP | SKU attributes, shelf life, handling requirements | — |
| `Store_Traffic` | IoT | Foot traffic for store-level demand sensing | depends_on -> Store_Master |
| `Goods_Receipt` | ERP/WMS | Inbound receipt confirmation and quality check | depends_on -> Purchase_Order |

**Policies:** inventory-fulfillment-policy, data-freshness-policy
**Workflows:** inventory-rebalancing, ship-from-store-routing
**Integrations:** erp-wms-inventory-feed, ecom-digital-feed

---

## App 6: Store Operations

**NRF:** Store Operations | **Minimum Objects: 9**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Store_Master` | ERP | Store profile, format, sq footage, region | — |
| `Store_Traffic` | IoT | Foot traffic by zone and time for staffing optimization | depends_on -> Store_Master |
| `Labor_Schedule` | WFM | Employee shift schedules and labor cost | depends_on -> Store_Master |
| `Employee` | WFM/HR | Associate profile, skills, certification | depends_on -> Store_Master |
| `Shelf_Condition` | IoT (CV) | Planogram compliance and out-of-stock detection | depends_on -> Store_Master |
| `Transaction` | POS | Sales performance and conversion rate by store | depends_on -> Store_Master |
| `Inventory_Position` | ERP | Store-level stock for replenishment triggers | depends_on -> Product_Master, Store_Master |
| `Temperature_Sensor` | IoT | Cold chain compliance monitoring | depends_on -> Store_Master |
| `Register` | POS | Register performance, void rates, transaction speed | depends_on -> Store_Master |

**Policies:** store-operations-policy, loss-prevention-policy
**Workflows:** store-performance-monitoring, planogram-compliance
**Integrations:** pos-erp-sync, iot-sensor-feed

---

## App 7: Supplier & Merchandising

**NRF:** Merchandising / Supply Chain | **Minimum Objects: 9**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Vendor_Master` | ERP | Supplier profile, performance score, certifications | — |
| `Purchase_Order` | ERP | Procurement history and delivery performance | depends_on -> Vendor_Master |
| `Goods_Receipt` | ERP/WMS | On-time delivery and quality acceptance rates | depends_on -> Purchase_Order |
| `Product_Master` | ERP | Product sourcing, cost, and category management | — |
| `Transaction` | POS | Sell-through rate for vendor performance context | depends_on -> Product_Master |
| `Product_Hierarchy` | ERP | Category structure for assortment planning | depends_on -> Product_Master |
| `Vendor_Co_Op` | ERP | Vendor co-op and trade fund agreements | depends_on -> Vendor_Master |
| `Market_Trend` | Social/External | Category trends for assortment decisions | — |
| `Competitor_Price` | External | Competitive landscape for vendor negotiations | — |

**Policies:** supplier-procurement-policy, pricing-promotion-policy
**Workflows:** supplier-scorecard, assortment-planning
**Integrations:** erp-wms-inventory-feed, social-market-intelligence-feed

---

## App 8: Sustainability

**NRF:** Sustainability | **Minimum Objects: 8**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Product_Origin` | ERP/Vendor | Product sourcing traceability and origin data | depends_on -> Product_Master, Vendor_Master |
| `Carbon_Footprint` | Internal | Per-product and per-store carbon emission tracking | depends_on -> Product_Master |
| `Waste_Record` | ERP | Food waste, donation, and disposal tracking | depends_on -> Store_Master, Inventory_Position |
| `Packaging` | ERP | Recycled content, recyclability score per SKU | depends_on -> Product_Master |
| `Temperature_Sensor` | IoT | Cold chain excursion monitoring | depends_on -> Store_Master |
| `Inventory_Position` | ERP | Perishable inventory for waste minimization | depends_on -> Product_Master |
| `Product_Master` | ERP | Product attributes, shelf life, packaging specs | — |
| `Vendor_Master` | ERP | Supplier sustainability certifications | — |

**Policies:** sustainability-policy, data-freshness-policy
**Workflows:** esg-reporting, food-waste-management
**Integrations:** erp-wms-inventory-feed, iot-sensor-feed

---

## Cross-Application Dependency Matrix

Shows which entities are shared across applications (checkmark = required by that app):

| Entity | Cust 360 | Demand | Personal. | Price Opt | Inv & Fulfill | Store Ops | Supplier | Sustain. |
|--------|----------|--------|-----------|-----------|---------------|-----------|----------|----------|
| **Product_Master** | — | x | x | x | x | — | x | x |
| **Transaction** | x | x | x | x | — | x | x | — |
| **Customer_Profile** | x | — | x | x | — | — | — | — |
| **Store_Master** | x | x | — | — | x | x | — | — |
| **Inventory_Position** | — | x | — | x | x | x | — | x |
| **Promotion** | x | x | x | x | — | — | — | — |
| **Loyalty_Account** | x | — | x | — | — | — | — | — |
| **Browsing_Session** | x | — | x | — | — | — | — | — |
| **Online_Order** | — | — | x | — | x | — | — | — |
| **Store_Traffic** | — | x | — | — | — | x | — | — |
| **Vendor_Master** | — | — | — | — | — | — | x | x |
| **Temperature_Sensor** | — | — | — | — | — | x | — | x |
| **Competitor_Price** | — | — | — | x | — | — | x | — |
| **Product_Review** | x | — | x | — | — | — | — | — |
| **Brand_Sentiment** | x | x | — | — | — | — | — | — |
| **Goods_Receipt** | — | — | — | — | x | — | x | — |

---

## Entity Count per App

| Application | Min Objects | Workflows | Policies | Integrations |
|------------|-----------|-----------|----------|--------------|
| Customer 360 & Loyalty | 10 | 1 | 2 | 2 |
| Demand Forecasting | 10 | 1 | 2 | 2 |
| Personalization | 9 | 1 | 2 | 2 |
| Price Optimization | 9 | 2 | 2 | 2 |
| Inventory & Fulfillment | 10 | 2 | 2 | 2 |
| Store Operations | 9 | 2 | 2 | 2 |
| Supplier & Merchandising | 9 | 2 | 2 | 2 |
| Sustainability | 8 | 2 | 2 | 2 |

---

[← Back to Ontology Overview](index.md)
