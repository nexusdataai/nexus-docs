# Workflows

12 SCOR-aligned AI workflows that power the 8 supply chain applications. Each workflow is defined in `enterprise-knowledge/workflows/` as a YAML file with trigger conditions, ordered steps, and entity/policy dependencies.

---

## Workflow Summary

| # | Workflow | SCOR | Trigger | Primary App |
|---|---------|------|---------|-------------|
| 1 | [Demand Forecast Generation](#1-demand-forecast-generation) | Plan | Weekly schedule or >10% volume change | Demand Forecasting |
| 2 | [Inventory Rebalancing](#2-inventory-rebalancing) | Plan | Stock imbalance detected | Inventory Optimization |
| 3 | [Expiry Management](#3-expiry-management) | Plan/Return | Batch enters 90/60/30-day expiry window | Inventory Optimization |
| 4 | [Order-to-Cash Monitoring](#4-order-to-cash-monitoring) | Deliver | Opportunity reaches Closed_Won | Order-to-Cash |
| 5 | [Supplier Risk Scoring](#5-supplier-risk-scoring) | Source | New vendor or monthly re-evaluation | Supply Chain Risk |
| 6 | [Disruption Response](#6-disruption-response) | Source | High/Critical Market_Signal detected | Supply Chain Risk |
| 7 | [Customer Churn Prediction](#7-customer-churn-prediction) | Deliver | Monthly schedule or >20% volume decline | Customer 360 |
| 8 | [Procurement Spend Analysis](#8-procurement-spend-analysis) | Source | Weekly schedule or PO >$100K | Procurement Analytics |
| 9 | [Invoice Processing](#9-invoice-processing) | Source | New PDF/scan uploaded | Procurement Analytics |
| 10 | [Production Scheduling](#10-production-scheduling) | Make | Forecast updated or schedule conflict | Production & Quality |
| 11 | [Quality Deviation Response](#11-quality-deviation-response) | Make | Test result outside spec limits | Production & Quality |
| 12 | [ESG Reporting](#12-esg-reporting) | Enable | Quarterly schedule or emission spike | ESG Tracker |

---

## 1. Demand Forecast Generation

**ID:** `WORKFLOW_DEMAND_FORECAST_V1_0` | **SCOR:** Plan | **File:** `demand-forecast-generation.yaml`

**Trigger:** Scheduled weekly (Sunday 02:00 UTC) OR Salesforce Opportunity volume change >10% week-over-week

| Step | System | Action |
|------|--------|--------|
| 1. Feature Engineering | Internal | Aggregate sales history (Opportunities), inventory (SAP), promotions (Campaigns), weather, social signals (Market_Signal) |
| 2. Model Ensemble | Internal | Run Prophet/ARIMA + XGBoost/LightGBM in parallel; weighted average ensemble |
| 3. Promotion Overlay | Internal | Apply learned promotion response curves per Campaign mechanic x category x region |
| 4. Cannibalization Adjustment | Internal | Apply cross-product substitution factors from historical data |
| 5. Consensus Integration | Salesforce | Merge AI forecast with Forecast_Override entries from sales team |
| 6. Publish Forecast | SAP | Push SKU x Region x Week demand plan to SAP MRP (retry 3x) |

**Dependencies:** Opportunity, Material_Master, Campaign, Market_Signal, Forecast_Override, Inventory_Position, pricing-discount-policy, data-freshness-policy

---

## 2. Inventory Rebalancing

**ID:** `WORKFLOW_INVENTORY_REBALANCING_V1_0` | **SCOR:** Plan | **File:** `inventory-rebalancing.yaml`

**Trigger:** Inventory_Position imbalance — Plant A >45 days supply while Plant B <5 days for same SKU

| Step | System | Action |
|------|--------|--------|
| 1. Identify Imbalance | SAP | Scan inventory positions; flag surplus/deficit beyond policy thresholds |
| 2. Calculate Transfer Qty | Internal | Optimal transfer considering safety stock, in-transit, and demand forecast |
| 3. Validate Receiving Capacity | SAP | Check destination Plant_Master capacity and Storage_Location availability |
| 4. Generate Transfer Order | SAP | Create Warehouse_Transfer record (FIFO batch selection) |
| 5. Route Optimization | Internal | VRP solver for distance, vehicle capacity, delivery windows |
| 6. Execute Transfer | SAP | Release transfer order; update Inventory_Position at both plants |

**Dependencies:** Inventory_Position, Material_Plant, Plant_Master, Warehouse_Transfer, Batch_Master, inventory-policy, data-freshness-policy

---

## 3. Expiry Management

**ID:** `WORKFLOW_EXPIRY_MANAGEMENT_V1_0` | **SCOR:** Plan/Return | **File:** `expiry-management.yaml`

**Trigger:** Batch_Master Shelf_Life_Remaining_Days enters 90/60/30-day window

| Step | System | Action |
|------|--------|--------|
| 1. Scan Batches | SAP | Daily scan; calculate days to expiry |
| 2. Score Waste Risk | Internal | Waste probability from stock qty, sell-through rate, demand forecast |
| 3. Classify Action Window | Internal | 90d: accelerate sales; 60d: markdown/redistribute; 30d: mandatory action; 7d: donate/destroy |
| 4. Execute Markdown | Salesforce | Update pricing via Campaign; notify sales team |
| 5. Execute Redistribution | SAP | Create Warehouse_Transfer to higher-demand location |
| 6. Process Donation/Destruction | SAP | Route to donation partner or schedule destruction; block batch |
| 7. Notify | Internal | Generate alerts per severity; update dashboard |

**Dependencies:** Batch_Master, Inventory_Position, Material_Master, Warehouse_Transfer, Campaign, inventory-policy, sustainability-policy

---

## 4. Order-to-Cash Monitoring

**ID:** `WORKFLOW_ORDER_TO_CASH_V1_0` | **SCOR:** Deliver | **File:** `order-to-cash-monitoring.yaml`

**Trigger:** Salesforce Opportunity Stage changes to Closed_Won

| Step | System | Action |
|------|--------|--------|
| 1. Entity Resolution | Internal | Match Opportunity -> SAP Delivery_Document -> Oracle AR_Invoice |
| 2. Three-Way Match | Internal | Validate qty/price across order, delivery, invoice (tolerance: qty +-2%, price +-5%) |
| 3. Anomaly Scoring | Internal | Score against learned baselines for cycle times, values, payment patterns |
| 4. Risk Prioritization | Internal | Rank by value x days overdue x account tier x SLA proximity |
| 5. Cash Flow Projection | Internal | Customer-specific payment probability curves on open invoices |
| 6. Alert and Escalate | Internal | Trigger alerts per severity; push to dashboard and CRM |

**Dependencies:** Opportunity, Opportunity_Line_Item, Account, Delivery_Document, AR_Invoice, AR_Payment, AR_Credit_Note, AR_Customer, Goods_Receipt, Return_Order, order-fulfillment-policy, credit-policy

---

## 5. Supplier Risk Scoring

**ID:** `WORKFLOW_SUPPLIER_RISK_SCORING_V1_0` | **SCOR:** Source | **File:** `supplier-risk-scoring.yaml`

**Trigger:** New Vendor_Master record created OR monthly re-evaluation (1st business day)

| Step | System | Action |
|------|--------|--------|
| 1. Gather Performance Data | SAP/Oracle | Delivery history, quality data, spend data |
| 2. Delivery Reliability (30%) | Internal | On-time %, lead time variance, partial shipments |
| 3. External Signal Scan (10%) | Social Listening | NLP scan for vendor news, country risk |
| 4. Contract Intelligence (10%) | Google Drive | Extract and validate Contract_Document terms |
| 5. Financial Health (20%) | Internal | Payment behavior from Oracle AP, credit reports |
| 6. Quality Performance (15%) | SAP | Incoming Quality_Inspection_Lot pass rates |
| 7. Geographic Risk (15%) | Internal | Country risk index, disaster exposure, trade policy |
| 8. Composite Risk Score | Internal | Weighted 0-100; tiers: 80-100=Low, 60-79=Medium, 40-59=High, 0-39=Critical |
| 9. Publish Alerts | Internal | Critical/High vendors: alert procurement; recommend alternatives from Source_List |

**Dependencies:** Vendor_Master, Source_List, Purchase_Order, Goods_Receipt, Quality_Inspection_Lot, AP_Invoice, Contract_Document, Market_Signal, supply-chain-risk-policy, procurement-policy

---

## 6. Disruption Response

**ID:** `WORKFLOW_DISRUPTION_RESPONSE_V1_0` | **SCOR:** Source | **File:** `disruption-response.yaml`

**Trigger:** Market_Signal with Severity = High or Critical

| Step | System | Action |
|------|--------|--------|
| 1. Assess Impact Scope | Internal | Match signal against Vendor_Master locations and Material_Master dependencies |
| 2. Identify Affected Orders | Oracle/SAP | Find open POs and GRNs from affected vendors; calculate exposure |
| 3. Check Safety Stock | SAP | Calculate days-of-supply remaining for affected materials |
| 4. Activate Alternatives | SAP | Query Source_List for secondary/emergency vendors |
| 5. Trigger Emergency Procurement | Oracle | If safety stock <10 days, generate emergency PO |
| 6. Notify Stakeholders | Internal | Alert procurement head, SC director, affected plant managers |
| 7. Update Risk Scores | Internal | Trigger Supplier Risk Scoring for affected vendors |

**Dependencies:** Market_Signal, Vendor_Master, Material_Master, Source_List, Purchase_Order, Inventory_Position, Material_Plant, supply-chain-risk-policy

---

## 7. Customer Churn Prediction

**ID:** `WORKFLOW_CUSTOMER_CHURN_V1_0` | **SCOR:** Deliver | **File:** `customer-churn-prediction.yaml`

**Trigger:** Monthly (1st business day) OR Account order volume declines >20% vs prior quarter

| Step | System | Action |
|------|--------|--------|
| 1. Profile Assembly | Internal | Aggregate purchase history, fulfillment KPIs, financial metrics, returns, sentiment |
| 2. Feature Engineering | Internal | Order frequency velocity, basket trends, complaints, payment changes |
| 3. Churn Scoring | Internal | Gradient-boosted model; predict 30/60/90-day churn probability |
| 4. Driver Segmentation | Internal | Classify: Price_Sensitivity, Network_Quality, Competitor_Pull, Service_Issue, Life_Event |
| 5. Match Retention Offer | Internal | Map driver to optimal action (discount, SLA commitment, match offer) |
| 6. Push to CRM | Salesforce | Create retention task on Account; 48-hour SLA for Platinum/Gold |

**Dependencies:** Account, Opportunity, Opportunity_Line_Item, Delivery_Document, Return_Order, AR_Customer, AR_Invoice, Cost_Accounting, Brand_Sentiment, Campaign, pricing-discount-policy

---

## 8. Procurement Spend Analysis

**ID:** `WORKFLOW_PROCUREMENT_SPEND_V1_0` | **SCOR:** Source | **File:** `procurement-spend-analysis.yaml`

**Trigger:** Weekly (Monday 06:00 UTC) OR new Purchase_Order value exceeds $100K

| Step | System | Action |
|------|--------|--------|
| 1. Spend Aggregation | Internal | Build spend cube: vendor x material x plant x period |
| 2. Contract Intelligence | Internal | Extract pricing/volume terms from Contract_Document via NLP |
| 3. Maverick Detection | Internal | Flag: non-contracted vendor, price >5% above contract, unapproved material |
| 4. Three-Way Match | Internal | PO qty vs GRN qty vs Invoice amount; route exceptions |
| 5. Consolidation Analysis | Internal | Cluster vendor x material; identify 4+ vendors with >10% price spread |
| 6. Generate Reports | Internal | Spend dashboard, maverick report, consolidation recommendations |

**Dependencies:** Purchase_Order, Vendor_Master, Material_Master, Source_List, Goods_Receipt, AP_Invoice, AP_Payment, Contract_Document, Commodity_Price, procurement-policy

---

## 9. Invoice Processing

**ID:** `WORKFLOW_INVOICE_PROCESSING_V1_0` | **SCOR:** Source | **File:** `invoice-processing.yaml`

**Trigger:** New file uploaded to Invoice_Upload (PDF/scan)

| Step | System | Action |
|------|--------|--------|
| 1. OCR + LLM Extraction | Internal | Extract vendor, invoice number, amounts, line items; assign confidence score |
| 2. Data Validation | Internal | Validate against Vendor_Master; check duplicates; flag confidence <0.7 |
| 3. PO Matching | Internal | Match to Purchase_Order by vendor + material + amount |
| 4. GRN Matching | Internal | Match to Goods_Receipt; validate qty within 2% tolerance |
| 5. Three-Way Match Decision | Internal | Auto-approve if matched; route mismatches to AP exception queue |
| 6. Approval or Rejection | Oracle | Create AP_Invoice; schedule payment per terms |

**Dependencies:** Invoice_Upload, Vendor_Master, Purchase_Order, Goods_Receipt, AP_Invoice, procurement-policy, order-fulfillment-policy

---

## 10. Production Scheduling

**ID:** `WORKFLOW_PRODUCTION_SCHEDULING_V1_0` | **SCOR:** Make | **File:** `production-scheduling.yaml`

**Trigger:** Demand forecast updated OR schedule conflict (raw material shortage)

| Step | System | Action |
|------|--------|--------|
| 1. Demand Integration | Internal | Pull latest forecast and Express/Critical Opportunities |
| 2. Material Availability Check | SAP | Explode BOM; check Inventory_Position for each component |
| 3. Capacity Check | SAP | Check Production_Line availability; account for changeover |
| 4. Schedule Optimization | Internal | Minimize changeover + waste; maximize throughput; respect constraints |
| 5. Batch Planning | SAP | Assign Batch_ID; calculate Expiry_Date |
| 6. Publish Schedule | SAP | Release Production_Orders in SAP PP; notify supervisors |

**Dependencies:** Production_Order, Production_Line, Bill_of_Materials, Material_Master, Material_Plant, Inventory_Position, Batch_Master, Plant_Master, quality-policy, inventory-policy

---

## 11. Quality Deviation Response

**ID:** `WORKFLOW_QUALITY_DEVIATION_V1_0` | **SCOR:** Make | **File:** `quality-deviation-response.yaml`

**Trigger:** Quality_Test_Result.Pass_Flag = false OR Lab_Report_Upload.Spec_Compliance = false OR 3+ consecutive batch failures

| Step | System | Action |
|------|--------|--------|
| 1. Detect Deviation | SAP/Internal | Classify severity: Minor (marginal), Major (outside spec), Critical (repeated/multiple) |
| 2. Hold Batch | SAP | Set Batch_Master.Status = Blocked; move stock to Blocked_Qty |
| 3. Root Cause Correlation | Internal | Correlate with material batch, production line, shift, environmental conditions |
| 4. Escalation | Internal | Minor: QC Supervisor (24h); Major: Quality Manager (8h); Critical: stop line + Plant Manager (2h) |
| 5. Corrective Action | SAP | Re-test, rework, scrap, or conditionally release |
| 6. Resolution Tracking | Internal | Log root cause and preventive measures; update trends dashboard |

**Dependencies:** Quality_Test_Result, Quality_Inspection_Lot, Batch_Master, Production_Order, Production_Line, Bill_of_Materials, Material_Master, Lab_Report_Upload, Inventory_Position, quality-policy

---

## 12. ESG Reporting

**ID:** `WORKFLOW_ESG_REPORTING_V1_0` | **SCOR:** Enable | **File:** `esg-reporting.yaml`

**Trigger:** Quarterly (5th business day after quarter end) OR Plant emission data >15% above target

| Step | System | Action |
|------|--------|--------|
| 1. Collect Energy/Water Data | SAP/Oracle | Plant-level energy from SAP utilities and Oracle Cost_Accounting; water from SAP metering |
| 2. Emission Calculation | Internal | Scope 1 (combustion), Scope 2 (electricity), Scope 3 (supply chain + logistics) |
| 3. Per-SKU Allocation | Internal | Allocate via BOM activity-based allocation |
| 4. Packaging Assessment | Internal | Aggregate Recycled_Content_Pct and Recyclability_Score across portfolio |
| 5. Benchmarking | Internal | Compare vs prior period, annual target, industry benchmarks |
| 6. Report Generation | Internal | GRI 301/303/305, SASB FB-NB, CDP Climate framework reports |
| 7. Sentiment Check | Internal | Monitor Brand_Sentiment for ESG-related topics |
| 8. Publish | Internal | ESG dashboard; board-ready summary; flag non-compliance |

**Dependencies:** Plant_Master, Production_Order, Bill_of_Materials, Material_Master, Shipment, Delivery_Document, Cost_Accounting, Fixed_Asset, Sustainability_Report, Brand_Sentiment, sustainability-policy, data-freshness-policy

---

[← Back to Ontology Overview](index.md)
