# Policies

8 governance policies that constrain entity operations, workflow execution, and business rules across the retail ontology. Each policy is defined in `enterprise-knowledge/policies/` as a Markdown file.

---

## Policy Summary

| # | Policy | ID | Standard | Risk | Owner | Constrains |
|---|--------|----|----------|------|-------|------------|
| 1 | [Pricing & Promotion Policy](#1-pricing-promotion-policy) | POL-PRICE-001 | NRF: Merchandising | High | Chief Merchandising Officer | Product_Master, Promotion, Price_Record, Markdown_Schedule |
| 2 | [Inventory & Fulfillment Policy](#2-inventory-fulfillment-policy) | POL-INV-001 | GS1 | High | VP Supply Chain | Inventory_Position, Warehouse, Shipment, Stock_Movement |
| 3 | [Customer Data & Privacy Policy](#3-customer-data-privacy-policy) | POL-CUST-001 | GDPR/CCPA | Critical | Chief Privacy Officer | Customer_Profile, Loyalty_Account, Browsing_Session, Customer_Segment |
| 4 | [Store Operations Policy](#4-store-operations-policy) | POL-STORE-001 | NRF | Medium | VP Store Operations | Store_Master, Store_Traffic, Labor_Schedule, Shelf_Condition |
| 5 | [Supplier & Procurement Policy](#5-supplier-procurement-policy) | POL-SUPP-001 | GS1 | High | Head of Procurement | Vendor_Master, Purchase_Order, Goods_Receipt, Product_Master |
| 6 | [Sustainability Policy](#6-sustainability-policy) | POL-SUST-001 | GRI/SASB | Medium | Chief Sustainability Officer | Product_Origin, Carbon_Footprint, Waste_Record, Packaging |
| 7 | [Data Freshness Policy](#7-data-freshness-policy) | POL-DATA-001 | NRF/GS1 | Medium | Chief Data Officer | All integration feeds |
| 8 | [Loss Prevention Policy](#8-loss-prevention-policy) | POL-LP-001 | NRF | High | Director of Loss Prevention | Transaction, Register, Inventory_Position, Store_Master |

---

## 1. Pricing & Promotion Policy

**ID:** POL-PRICE-001 | **Standard:** NRF: Merchandising | **Systems:** POS, ERP, E-commerce

| Rule Area | Key Rules |
|-----------|-----------|
| **Margin Floor** | No transaction below 20% gross margin without CMO approval; exception requires documented competitive justification |
| **Promotion Stacking** | Maximum 30% combined discount when stacking tier + campaign + coupon; BOGO limited to 1 per customer per campaign |
| **Markdown Cadence** | Seasonal markdowns at 4-week intervals: 30% → 50% → 70%; clearance override requires Merchandising Director approval |
| **Competitive Price Matching** | Key Value Items (KVIs) matched within 48 hours of verified competitor price change; non-KVI at CMO discretion |
| **Vendor-Funded Promotions** | BOGO and deep-discount promotions require minimum 50% vendor cost share; co-op agreements documented in Vendor_Co_Op |
| **Price Change Frequency** | Maximum 2 price changes per week per SKU; exceptions for perishables and competitive response on KVIs |

---

## 2. Inventory & Fulfillment Policy

**ID:** POL-INV-001 | **Standard:** GS1 | **Systems:** ERP, WMS, E-commerce

| Rule Area | Key Rules |
|-----------|-----------|
| **Safety Stock** | ABC classification: A=7 days, B=14 days, C=21 days; recalculated weekly from demand forecast variance and lead time variability |
| **FIFO Enforcement** | Oldest batch shipped/sold first; exception requires Supply Chain Manager approval; perishables: strict FIFO, no exceptions |
| **Stockout SLA** | Critical items (top 200 SKUs) replenished within 24 hours; standard items within 48 hours; seasonal within SLA + 3 days |
| **Ship-from-Store** | Store must have >10 units excess above safety stock; pick-pack SLA: 2 hours; carrier pickup within 4 hours |
| **Split Shipment Avoidance** | Route to single fulfillment node if >70% of order available; <70%: split with customer notification; max 2 shipments per order |
| **ATP Accuracy** | Available-to-Promise accuracy target >98%; breach triggers inventory reconciliation within 24 hours |

---

## 3. Customer Data & Privacy Policy

**ID:** POL-CUST-001 | **Regulatory:** GDPR / CCPA | **Systems:** CRM/CDP, POS, E-commerce

| Rule Area | Key Rules |
|-----------|-----------|
| **Consent** | Explicit consent required for cross-channel identity stitching; separate consent for marketing, analytics, and partner sharing |
| **Data Retention** | Transaction data: 7 years; browsing/clickstream: 2 years; marketing consent records: until withdrawn + 1 year audit trail |
| **Right to Delete** | Customer deletion request fulfilled within 30 days; cascades to Browsing_Session, Clickstream_Event, Customer_Segment membership |
| **Anonymization** | All personally identifiable data anonymized for analytics after 24 months; aggregated cohort data exempt |
| **Loyalty Data Sharing** | Loyalty transaction and preference data shared with partners only with explicit opt-in; revocable at any time |

---

## 4. Store Operations Policy

**ID:** POL-STORE-001 | **Standard:** NRF | **Systems:** POS, IoT, WFM

| Rule Area | Key Rules |
|-----------|-----------|
| **Staffing Ratios** | Minimum 1 associate per 2,000 sq ft during trading hours; peak hours (11am-2pm, 5pm-7pm): 1 per 1,500 sq ft |
| **Planogram Compliance** | Target >92% compliance on audited sections; below 85%: store manager remediation plan within 7 days |
| **Shrinkage Investigation** | Cashier void rate >3σ above store average triggers LP investigation; self-checkout void rate monitored separately |
| **Self-Checkout Loss Prevention** | Scan rate target >95%; stores below 90% for 2+ consecutive weeks: intervention review with LP Director |
| **Energy Target** | 10% year-over-year reduction in kWh per sq ft; stores exceeding 15% over budget flagged for energy audit |

---

## 5. Supplier & Procurement Policy

**ID:** POL-SUPP-001 | **Standard:** GS1 | **Systems:** ERP, Vendor Portal

| Rule Area | Key Rules |
|-----------|-----------|
| **Vendor Approval** | Performance_Score >60 required for continued listing; below 40: suspend new POs; below 30: delist with 90-day wind-down |
| **PO Approval** | <$50K: auto-approve; $50K-$250K: Procurement Director; >$250K: VP + CFO; >$1M: Board approval |
| **Lead Time Compliance** | Target >95% on-time delivery; below 90% for 3 consecutive months: vendor performance improvement plan |
| **Quality Defect Threshold** | <2% rejection rate on incoming inspection; >5%: automatic vendor hold; >10%: delist review |
| **Single-Source Prohibition** | Top 100 SKUs must have ≥2 approved vendors; exception: proprietary/patented items with VP Supply Chain approval; qualification deadline: 90 days |

---

## 6. Sustainability Policy

**ID:** POL-SUST-001 | **Standard:** GRI / SASB | **Systems:** ERP, Vendor Portal, IoT

| Rule Area | Key Rules |
|-----------|-----------|
| **Carbon Targets** | 5% year-over-year reduction in kg CO2e per product unit; Scope 1+2 tracked at store and DC level |
| **Packaging** | Recyclable packaging target >80% of SKUs by 2027; recycled content minimum >30% across all private label |
| **Food Waste** | Target <3% of perishable inventory; donation rate >50% of near-expiry safe product; stores exceeding 5% for 2+ weeks: investigation |
| **Cold Chain Excursion** | Any temperature excursion outside spec = immediate quarantine + root cause investigation; affected inventory blocked until QA release |
| **Supplier Certification** | New suppliers must hold recognized sustainability certification (Rainforest Alliance, Fair Trade, BSCI, or equivalent) within 12 months of onboarding |

---

## 7. Data Freshness Policy

**ID:** POL-DATA-001 | **Standard:** NRF / GS1 | **Systems:** All

### Structured System SLAs

| Source | Data | SLA |
|--------|------|-----|
| POS System | Transaction, Transaction_Line_Item, Register | Real-time (<1 min) |
| ERP | Inventory_Position, Stock_Movement, Goods_Receipt | Daily full + real-time delta |
| E-commerce Platform | Online_Order, Clickstream_Event, Browsing_Session | Real-time (<1 min) |
| CRM / CDP | Customer_Profile, Loyalty_Account, Customer_Segment | On-change + daily full sync |
| Social / Reviews | Product_Review, Brand_Sentiment, Market_Trend | 4-hour refresh cycle |
| IoT Sensors | Store_Traffic, Shelf_Condition, Temperature_Sensor | Real-time (<1 min) |

### Staleness Rules

- 2x SLA gap: alert Data Engineering
- 3x SLA gap: mark data as stale; exclude from AI workflow inputs; notify operations management

---

## 8. Loss Prevention Policy

**ID:** POL-LP-001 | **Standard:** NRF | **Systems:** POS, CCTV, IoT

| Rule Area | Key Rules |
|-----------|-----------|
| **Shrinkage Target** | <1.0% of revenue; stores exceeding 1.5% for 2+ consecutive periods: LP audit within 14 days |
| **Void/Refund Investigation** | Cashier void or refund rate >3σ above store average: automatic flag for LP review within 48 hours |
| **Self-Checkout Intervention** | Intervention rate monitored per store; stores with scan-miss rate >5%: technology and process review |
| **Age-Restricted Items** | 100% age verification on controlled substances (alcohol, tobacco); failed verification = blocked transaction; no override |
| **Internal Theft Protocol** | Suspected internal theft: LP Director notification within 24 hours; investigation completed within 30 days; dual-approval for employee termination based on LP findings |
| **Cycle Count Frequency** | A items: monthly; B items: quarterly; C items: semi-annual; >5% variance triggers full location audit |

---

[← Back to Ontology Overview](index.md)
