# Policies

8 governance policies that constrain entity operations, workflow execution, and business rules across the supply chain ontology. Each policy is defined in `enterprise-knowledge/policies/` as a Markdown file.

---

## Policy Summary

| # | Policy | ID | SCOR | Risk | Owner | Constrains |
|---|--------|----|------|------|-------|------------|
| 1 | [Inventory Policy](#1-inventory-policy) | POL-INV-001 | Plan | High | Supply Chain Operations | Inventory_Position, Batch_Master, Warehouse_Transfer |
| 2 | [Procurement Policy](#2-procurement-policy) | POL-PROC-001 | Source | High | Procurement Department | Vendor_Master, Oracle_Purchase_Order, Purchase_Requisition |
| 3 | [Quality Policy](#3-quality-policy) | POL-QA-001 | Make | Critical | Quality Assurance | Quality_Inspection_Lot, Quality_Test_Result, Batch_Master |
| 4 | [Supply Chain Risk Policy](#4-supply-chain-risk-policy) | POL-SCR-001 | Source/Enable | High | SC Risk Management | Vendor_Master, Source_List, Market_Signal |
| 5 | [Pricing & Discount Policy](#5-pricing--discount-policy) | POL-PRICE-001 | Deliver | High | Commercial / Revenue Mgmt | Account, Opportunity, Campaign |
| 6 | [Sustainability Policy](#6-sustainability-policy) | POL-ESG-001 | Enable | Medium | Sustainability & Corp Affairs | Plant_Master, Material_Master, Shipment |
| 7 | [Data Freshness Policy](#7-data-freshness-policy) | POL-DATA-001 | Enable | Medium | Data Engineering / IT Ops | All integration feeds |
| 8 | [Order Fulfillment Policy](#8-order-fulfillment-policy) | POL-OFC-001 | Deliver | High | Order Mgmt / SC Operations | Delivery_Document, Oracle_AR_Invoice, Return_Order |

---

## 1. Inventory Policy

**ID:** POL-INV-001 | **SCOR:** Plan | **Systems:** SAP, Oracle ERP

| Rule Area | Key Rules |
|-----------|-----------|
| **Safety Stock** | Min days-of-supply: A=7 days, B=14 days, C=21 days; recalculated weekly from demand forecast variance |
| **Reorder Point** | Average Daily Demand x Lead Time + Safety Stock; auto-trigger when Unrestricted_Qty falls below |
| **Expiry Windows** | 90d: accelerate sales; 60d: markdown/redistribution mandatory; 30d: final action; 7d: donate/destroy |
| **FIFO Enforcement** | Oldest batch shipped first; exception requires Supply Chain Manager approval |
| **Rebalancing** | Trigger: Plant A >45 days AND Plant B <5 days same SKU; approval: <$50K auto, >$50K SC Manager |
| **Markdown Authority** | 0-15%: Store/Depot Manager; 15-30%: Regional Manager; >30%: SC Director |
| **Cycle Counts** | A: monthly, B: quarterly, C: semi-annual; >5% variance triggers investigation |

---

## 2. Procurement Policy

**ID:** POL-PROC-001 | **SCOR:** Source | **Systems:** SAP, Oracle ERP, Google Drive

| Rule Area | Key Rules |
|-----------|-----------|
| **Approved Vendors** | All procurement must use SAP Source_List vendors; non-listed vendor = maverick spend requiring VP Procurement approval |
| **PO Approval** | <$10K auto; $10-50K Procurement Manager; $50-250K Procurement Director; >$250K VP + CFO; >$1M Board |
| **Competitive Bidding** | 3+ quotes required >$50K; sole-source only for patented materials or emergency |
| **Three-Way Match** | PO qty vs GRN qty vs Invoice qty; tolerance: qty +-2%, price +-5%; escalation after 5 business days |
| **Maverick Spend** | Definition: non-contracted vendor for contracted material OR price >5% above contracted rate; target: <5% of spend |
| **Payment Terms** | Standard: Net 30; payment blocked until three-way match clears |

---

## 3. Quality Policy

**ID:** POL-QA-001 | **SCOR:** Make | **Systems:** SAP, File Uploads

| Rule Area | Key Rules |
|-----------|-----------|
| **Inspection** | New vendors: 100% incoming inspection; Established: sampling per AQL; Every batch: final inspection before release |
| **Spec Limits** | Each Material_Master has defined spec limits per test; out-of-spec = automatic batch hold |
| **Batch Hold/Release** | Failed test: Batch_Master.Status = Blocked; Minor: QC Manager release; Major: Quality Director; Critical food safety: no release |
| **Repeat Failure Escalation** | 1 fail: QC Supervisor; 2 consecutive: QC Manager + root cause; 3+: STOP line + Plant Manager + Quality Director |
| **Recall** | Trigger: consumer safety risk, regulatory notification, systematic contamination; full trace in <30 minutes |
| **Lab Report NLP** | Extraction confidence >0.85: auto-populate; <0.85: mandatory manual verification |
| **Retention** | All QC records retained 5 years minimum; regulatory audit access within 24 hours |

---

## 4. Supply Chain Risk Policy

**ID:** POL-SCR-001 | **SCOR:** Source/Enable | **Systems:** SAP, Oracle, Social Listening, Google Drive

| Rule Area | Key Rules |
|-----------|-----------|
| **Risk Score** | Composite 0-100: Delivery Reliability 30%, Financial Health 20%, Geographic Risk 15%, Quality 15%, Contract 10%, External 10% |
| **Risk Tiers** | 80-100: Low (standard monitoring); 60-79: Medium (quarterly review); 40-59: High (monthly review + improvement plan); 0-39: Critical (freeze POs, activate alternatives, executive escalation) |
| **Single-Source** | No ABC Class A material may have only one approved vendor; exception: patented ingredients with VP approval; qualification deadline: 90 days |
| **Disruption SLA** | Critical: 2h assessment + 4h mitigation; High: 8h assessment + 24h plan; Medium: 48h assessment |
| **Commodity Monitoring** | Alert when Change_Pct_30D exceeds +-15%; trigger hedging review with Finance |
| **Re-evaluation** | All active vendors re-scored monthly; new vendors within 5 business days |

---

## 5. Pricing & Discount Policy

**ID:** POL-PRICE-001 | **SCOR:** Deliver | **Systems:** Salesforce, Oracle ERP

| Channel/Tier | Modern Trade | General Trade | HORECA | E-commerce |
|-------------|-------------|--------------|--------|------------|
| Platinum | 18% | 15% | 20% flat | 10% flat |
| Gold | 15% | 12% | 20% flat | 10% flat |
| Silver | 12% | 10% | 20% flat | 10% flat |

| Rule Area | Key Rules |
|-----------|-----------|
| **Margin Floor** | No transaction below 15% gross margin; exception requires Commercial Director + documented justification |
| **Promotion Stacking** | Tier + campaign discount combined max 25%; BOGO limited 1 per customer per campaign; overlap on substitutable SKUs prohibited |
| **Price Change Approval** | Within tier max: auto; exceeds by <=5%: Regional Sales Manager; >5%: Commercial Director; below margin floor: CFO |
| **Trade Spend Cap** | 8% of trailing 12-month revenue per account; excess requires VP Sales approval |

---

## 6. Sustainability Policy

**ID:** POL-ESG-001 | **SCOR:** Enable | **Systems:** SAP, Oracle, Social Listening, Google Drive

| Rule Area | Key Rules |
|-----------|-----------|
| **Carbon Targets** | 5% year-over-year reduction in kg CO2e per liter of beverage produced |
| **Water Targets** | <2.0 liters water per liter beverage by 2027; plants exceeding 2.5 L/L for any week require investigation |
| **Packaging** | Recycled content: 2025=30%, 2026=40%, 2027=50%; all new launches minimum 25%; Recyclability_Score target >3.5 |
| **Energy** | 3% year-over-year improvement in kWh per 1,000 liters; plants >10% over budget flagged for energy audit |
| **Waste** | Perishable waste target <3%; food donation rate >40% of near-expiry safe product |
| **Sentiment Response** | Brand_Sentiment on ESG topics <30 for 7+ days: notify Corporate Affairs within 24 hours |
| **Non-Compliance** | Plant miss: review within 10 days; Corporate miss: Board ESG Committee within 30 days |

---

## 7. Data Freshness Policy

**ID:** POL-DATA-001 | **SCOR:** Enable | **Systems:** All

### Structured System SLAs

| Source | Data | SLA |
|--------|------|-----|
| Salesforce CRM | Accounts, Opportunities, Campaigns | Near real-time (<5 min) |
| SAP Inventory | Inventory_Position, Batch_Master | Daily (by 06:00 UTC) |
| SAP Master Data | Material_Master, Vendor_Master, Plant_Master | On-change + daily full sync |
| SAP Transactions | Production_Order, Goods_Receipt, Delivery_Document | Near real-time (<15 min) |
| Oracle Finance | AR_Invoice, AR_Payment, GL_Journal | 15-minute sync interval |
| Oracle Operations | AP_Invoice, Purchase_Order, Cost_Accounting | 15-minute sync interval |

### Unstructured Source SLAs

| Source | Data | SLA |
|--------|------|-----|
| Google Drive | Contract_Document, Sustainability_Report | On-upload + daily scan |
| File Uploads | Invoice_Upload, Lab_Report_Upload | On-upload, processing within 30 min |
| Social Listening | Market_Signal, Brand_Sentiment, Commodity_Price | 4-hour refresh (critical signals immediate) |

### Staleness Rules

- 2x SLA gap: alert Data Engineering
- 3x SLA gap: mark data as stale, exclude from AI workflow inputs

---

## 8. Order Fulfillment Policy

**ID:** POL-OFC-001 | **SCOR:** Deliver | **Systems:** Salesforce, SAP, Oracle ERP

| Rule Area | Key Rules |
|-----------|-----------|
| **Order Acknowledgment** | Closed_Won in SAP within 4 hours; Express/Critical within 1 hour |
| **Fulfillment SLA** | Standard: 5 business days; Express: 2 business days; Critical: same/next day |
| **Three-Way Match** | Opportunity qty vs Delivery qty vs Invoice qty; tolerance: qty +-2%, price +-5% |
| **Credit Hold** | AR_Balance >80% of Credit_Limit: new orders held; On Credit_Hold: all shipments blocked |
| **SLA Breach** | 80%: alert fulfillment team; 100%: Regional SC Manager + customer comms; 120%: VP Supply Chain |
| **Partial Shipment** | Allowed if >70% available; remainder within SLA + 3 days; <70%: customer approval required |
| **Return Processing** | Accepted within 30 days; credit note in Oracle within 5 business days of receipt |

---

[← Back to Ontology Overview](index.md)
