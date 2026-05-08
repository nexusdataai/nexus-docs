# Application-Object Mapping

Minimum required ontology objects per application, with relationship details and cross-application dependency analysis.

---

## App 1: Demand Forecasting & Planning

**SCOR:** Plan | **Minimum Objects: 9**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Opportunity` | Salesforce | Order history / demand signal | depends_on -> Account |
| `Opportunity_Line_Item` | Salesforce | SKU-level demand | depends_on -> Opportunity, Material_Master |
| `Account` | Salesforce | Customer/channel segmentation | — |
| `Campaign` | Salesforce | Promotion calendar for lift modeling | triggers -> demand-forecast-generation |
| `Forecast_Override` | Salesforce | Sales team manual adjustments | depends_on -> Material_Master |
| `Material_Master` | SAP | Product master for SKU hierarchy | — |
| `Material_Plant` | SAP | Plant-level MRP parameters | depends_on -> Material_Master, Plant_Master |
| `Inventory_Position` | SAP | Current stock for demand-supply balancing | depends_on -> Material_Master |
| `Market_Signal` | Social Listening | External trend and sentiment signals | — |

**Policies:** pricing-discount-policy, data-freshness-policy
**Workflows:** demand-forecast-generation
**Integrations:** sf-sap-demand-sync, social-listening-feed

---

## App 2: Inventory Optimization & Distribution

**SCOR:** Plan/Deliver | **Minimum Objects: 11**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Material_Master` | SAP | SKU attributes, shelf life, pack config | — |
| `Material_Plant` | SAP | Safety stock, reorder point, lead time | depends_on -> Material_Master |
| `Inventory_Position` | SAP | Stock on hand per SKU x location x batch | depends_on -> Material_Master, Batch_Master |
| `Batch_Master` | SAP | Expiry dates, batch status | depends_on -> Material_Master |
| `Plant_Master` | SAP | Warehouse locations, capacity | — |
| `Storage_Location` | SAP | Cold chain, capacity by type | depends_on -> Plant_Master |
| `Warehouse_Transfer` | SAP | Stock rebalancing orders | depends_on -> Plant_Master |
| `Delivery_Document` | SAP | Outbound delivery for route optimization | depends_on -> Shipment |
| `Shipment` | SAP | Vehicle routing, load planning | — |
| `Opportunity` | Salesforce | Channel demand signal | depends_on -> Account |
| `Cost_Accounting` | Oracle | Carrying cost, COGS for optimization | depends_on -> Material_Master |

**Policies:** inventory-policy, data-freshness-policy
**Workflows:** inventory-rebalancing, expiry-management
**Integrations:** sap-inventory-feed

---

## App 3: Intelligent Order-to-Cash

**SCOR:** Deliver/Enable | **Minimum Objects: 12**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Opportunity` | Salesforce | Order source | depends_on -> Account |
| `Opportunity_Line_Item` | Salesforce | Order line details | depends_on -> Opportunity |
| `Account` | Salesforce | Customer master, credit, payment terms | — |
| `Delivery_Document` | SAP | Fulfillment / shipment | depends_on -> Opportunity (via mapping) |
| `AR_Invoice` | Oracle | Invoice generated for delivery | depends_on -> Delivery_Document, Account |
| `AR_Payment` | Oracle | Payment received | depends_on -> AR_Invoice |
| `AR_Credit_Note` | Oracle | Returns, disputes, adjustments | depends_on -> AR_Invoice |
| `AR_Customer` | Oracle | Credit limit, AR balance, collection priority | syncs_to -> Account |
| `GL_Journal` | Oracle | Revenue recognition | depends_on -> AR_Invoice |
| `GL_Period` | Oracle | Financial close window | constrained_by -> close-window-policy |
| `Goods_Receipt` | SAP | Three-way match (PO-GRN-Invoice) | depends_on -> Purchase_Order |
| `Return_Order` | SAP | Reverse logistics | depends_on -> Delivery_Document |

**Policies:** order-fulfillment-policy, credit-policy
**Workflows:** order-to-cash-monitoring
**Integrations:** sf-oracle-supply-chain-sync, sap-oracle-finance-sync

---

## App 4: Supply Chain Risk & Disruption Radar

**SCOR:** Source/Enable | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Vendor_Master` | SAP | Supplier profile, rating, certifications | — |
| `Source_List` | SAP | Material-to-vendor mapping, single-source detection | depends_on -> Vendor_Master, Material_Master |
| `Purchase_Order` | Oracle | Procurement history, delivery performance | depends_on -> Vendor_Master |
| `Goods_Receipt` | SAP | On-time delivery, quality acceptance rates | depends_on -> Purchase_Order |
| `Material_Master` | SAP | Material criticality, alternative materials | — |
| `Contract_Document` | Google Drive | Contract terms, SLAs, penalty clauses (NLP) | depends_on -> Vendor_Master |
| `Market_Signal` | Social Listening | Disruption signals (news, weather, port) | — |
| `Commodity_Price` | Social Listening | Raw material price trends | — |
| `AP_Invoice` | Oracle | Vendor payment and dispute history | depends_on -> Vendor_Master |
| `Quality_Inspection_Lot` | SAP | Incoming material quality history | depends_on -> Vendor_Master, Material_Master |

**Policies:** supply-chain-risk-policy, procurement-policy
**Workflows:** supplier-risk-scoring, disruption-response
**Integrations:** social-listening-feed, unstructured-extraction

---

## App 5: Customer 360 & Revenue Growth

**SCOR:** Deliver/Plan | **Minimum Objects: 11**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Account` | Salesforce | Customer master, tier, channel | — |
| `Contact` | Salesforce | Key contacts per account | depends_on -> Account |
| `Opportunity` | Salesforce | Order history, win rate, pipeline | depends_on -> Account |
| `Opportunity_Line_Item` | Salesforce | Product mix per customer | depends_on -> Opportunity |
| `Campaign` | Salesforce | Campaign response history | — |
| `Delivery_Document` | SAP | Fill rate, on-time delivery per customer | depends_on -> Account |
| `Return_Order` | SAP | Returns and complaints per customer | depends_on -> Account |
| `AR_Customer` | Oracle | AR balance, credit status, payment behavior | syncs_to -> Account |
| `AR_Invoice` | Oracle | Revenue, discounts, deductions per customer | depends_on -> Account |
| `Cost_Accounting` | Oracle | Cost-to-serve per customer | depends_on -> Account |
| `Brand_Sentiment` | Social Listening | Customer/market sentiment | — |

**Policies:** pricing-discount-policy
**Workflows:** customer-churn-prediction
**Integrations:** sf-oracle-supply-chain-sync, social-listening-feed

---

## App 6: Procurement & Spend Analytics

**SCOR:** Source | **Minimum Objects: 11**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Vendor_Master` | SAP | Vendor master for spend analysis | — |
| `Source_List` | SAP | Contracted vs. maverick vendor detection | depends_on -> Vendor_Master |
| `Purchase_Requisition` | SAP | Internal procurement requests | depends_on -> Material_Master |
| `Purchase_Order` | Oracle | PO data for spend cube | depends_on -> Vendor_Master, Material_Master |
| `Goods_Receipt` | SAP | Receiving confirmation for three-way match | depends_on -> Purchase_Order |
| `AP_Invoice` | Oracle | Vendor invoices for matching and analysis | depends_on -> Purchase_Order |
| `AP_Payment` | Oracle | Payment execution and status | depends_on -> AP_Invoice |
| `Material_Master` | SAP | Material categorization for spend cube | — |
| `Contract_Document` | Google Drive | Contracted prices, volume commitments (NLP) | depends_on -> Vendor_Master |
| `Invoice_Upload` | File Uploads | Scanned invoices for OCR+LLM extraction | triggers -> invoice-processing |
| `Commodity_Price` | Social Listening | Market price benchmarking | — |

**Policies:** procurement-policy
**Workflows:** procurement-spend-analysis, invoice-processing
**Integrations:** sap-oracle-finance-sync, unstructured-extraction

---

## App 7: Production & Quality Control

**SCOR:** Make | **Minimum Objects: 11**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Production_Order` | SAP | Manufacturing work order | depends_on -> Material_Master, Plant_Master |
| `Production_Line` | SAP | Line capacity, OEE, changeover | depends_on -> Plant_Master |
| `Bill_of_Materials` | SAP | Recipe / raw material requirements | depends_on -> Material_Master |
| `Material_Master` | SAP | Finished goods and raw material specs | — |
| `Material_Plant` | SAP | MRP parameters for material availability | depends_on -> Material_Master |
| `Batch_Master` | SAP | Batch traceability, expiry | depends_on -> Production_Order |
| `Quality_Inspection_Lot` | SAP | Inspection record per batch | depends_on -> Batch_Master |
| `Quality_Test_Result` | SAP | Individual test measurements | depends_on -> Quality_Inspection_Lot |
| `Lab_Report_Upload` | File Uploads | Unstructured lab results (NLP-extracted) | triggers -> quality-deviation-response |
| `Inventory_Position` | SAP | Raw material availability for scheduling | depends_on -> Material_Master |
| `Cost_Accounting` | Oracle | Production cost tracking | depends_on -> Production_Order |

**Policies:** quality-policy, inventory-policy
**Workflows:** production-scheduling, quality-deviation-response
**Integrations:** sap-inventory-feed, sap-oracle-finance-sync, unstructured-extraction

---

## App 8: ESG & Sustainability Tracker

**SCOR:** Enable | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Plant_Master` | SAP | Plant-level energy and water consumption | — |
| `Production_Order` | SAP | Activity data for emission allocation | depends_on -> Plant_Master |
| `Bill_of_Materials` | SAP | Per-SKU allocation basis | depends_on -> Material_Master |
| `Material_Master` | SAP | Packaging attributes (recycled %, recyclability) | — |
| `Shipment` | SAP | Logistics emissions (distance x vehicle type x load) | — |
| `Delivery_Document` | SAP | Per-route delivery data | depends_on -> Shipment |
| `Cost_Accounting` | Oracle | Energy and utility costs | depends_on -> Plant_Master |
| `Fixed_Asset` | Oracle | Equipment energy profiles | depends_on -> Plant_Master |
| `Sustainability_Report` | Google Drive | Historical ESG reports (NLP-extracted) | — |
| `Brand_Sentiment` | Social Listening | Public ESG sentiment monitoring | — |

**Policies:** sustainability-policy, data-freshness-policy
**Workflows:** esg-reporting
**Integrations:** sap-inventory-feed, sap-oracle-finance-sync, social-listening-feed, unstructured-extraction

---

## Cross-Application Dependency Matrix

Shows which entities are shared across applications (checkmark = required by that app):

| Entity | Demand | Inventory | O2C | Risk | Customer 360 | Procurement | Production | ESG |
|--------|--------|-----------|-----|------|--------------|-------------|------------|-----|
| **Material_Master** | x | x | — | x | — | x | x | x |
| **Account** | x | — | x | — | x | — | — | — |
| **Opportunity** | x | x | x | — | x | — | — | — |
| **Opportunity_Line_Item** | x | — | x | — | x | — | — | — |
| **Delivery_Document** | — | x | x | — | x | — | — | x |
| **Cost_Accounting** | — | x | — | — | x | — | x | x |
| **Inventory_Position** | x | x | — | — | — | — | x | — |
| **Plant_Master** | — | x | — | — | — | — | x | x |
| **Batch_Master** | — | x | — | — | — | — | x | — |
| **Vendor_Master** | — | — | — | x | — | x | — | — |
| **Purchase_Order** | — | — | — | x | — | x | — | — |
| **Goods_Receipt** | — | — | x | x | — | x | — | — |
| **Contract_Document** | — | — | — | x | — | x | — | — |
| **Market_Signal** | x | — | — | x | — | — | — | — |
| **Brand_Sentiment** | — | — | — | — | x | — | — | x |
| **AR_Invoice** | — | — | x | — | x | — | — | — |
| **AR_Customer** | — | — | x | — | x | — | — | — |

---

## Entity Count per App

| Application | Min Objects | Workflows | Policies | Integrations |
|------------|-----------|-----------|----------|--------------|
| Demand Forecasting | 9 | 1 | 2 | 2 |
| Inventory Optimization | 11 | 2 | 2 | 1 |
| Order-to-Cash | 12 | 1 | 2 | 2 |
| Supply Chain Risk | 10 | 2 | 2 | 2 |
| Customer 360 | 11 | 1 | 1 | 2 |
| Procurement Analytics | 11 | 2 | 1 | 3 |
| Production & Quality | 11 | 2 | 2 | 3 |
| ESG Tracker | 10 | 1 | 2 | 4 |

---

[← Back to Ontology Overview](index.md)
