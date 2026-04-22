# Workflows

10 GS1/NRF-aligned AI workflows that power the 8 retail applications. Each workflow is defined in `enterprise-knowledge/workflows/` as a YAML file with trigger conditions, ordered steps, and entity/policy dependencies.

---

## Workflow Summary

| # | Workflow | GS1/NRF | Trigger | Primary App |
|---|---------|---------|---------|-------------|
| 1 | [Customer Identity Resolution & CLV](#1-customer-identity-resolution--clv) | Customer | New transaction or monthly batch | Customer 360 |
| 2 | [Demand Forecast Generation](#2-demand-forecast-generation) | Merchandising | Weekly or >10% volume change | Demand Forecasting |
| 3 | [Personalization & Recommendations](#3-personalization--recommendations) | Digital Commerce | Customer interaction (web/email/store) | Personalization |
| 4 | [Price & Promotion Optimization](#4-price--promotion-optimization) | Merchandising | Weekly or promotion launch/end | Price Optimization |
| 5 | [Inventory Rebalancing & Fulfillment](#5-inventory-rebalancing--fulfillment) | Logistics (GS1) | Hourly or stockout risk | Inventory & Fulfillment |
| 6 | [Store Operations Intelligence](#6-store-operations-intelligence) | Store Ops | Daily or shift change | Store Operations |
| 7 | [Supplier Performance & Assortment](#7-supplier-performance--assortment) | Merchandising | Monthly or vendor delivery event | Supplier & Merchandising |
| 8 | [Sustainability & Traceability](#8-sustainability--traceability) | Traceability (GS1) | Quarterly or recall/excursion event | Sustainability & Compliance |
| 9 | [Campaign & Engagement Orchestration](#9-campaign--engagement-orchestration) | Customer | Campaign launch or lifecycle event | Customer 360, Personalization |
| 10 | [Omnichannel Fraud & Loss Prevention](#10-omnichannel-fraud--loss-prevention) | Store Ops | Real-time POS event or inventory discrepancy | Store Operations |

---

## 1. Customer Identity Resolution & CLV

**ID:** `WORKFLOW_CUSTOMER_IDENTITY_CLV_V1_0` | **GS1/NRF:** Customer | **File:** `customer-identity-clv.yaml`

**Trigger:** New Transaction record across POS/CRM/E-commerce OR monthly batch (1st business day)

| Step | System | Action |
|------|--------|--------|
| 1. Probabilistic Matching | Internal | Match customer identities across POS, CRM/CDP, and E-commerce using probabilistic matching (email, phone, payment token, device fingerprint) |
| 2. Profile Assembly | Internal | Merge matched identities into single golden Customer_Profile; resolve conflicts by source priority and recency |
| 3. CLV Modeling | Internal | Calculate customer lifetime value using BG/NBD (frequency/recency) + Gamma-Gamma (monetary) models on transaction history |
| 4. Behavioral Segmentation | Internal | Classify customers into behavioral segments: High-Value Loyalist, Promising, At-Risk, Hibernating, New, Price-Sensitive |
| 5. Loyalty Optimization | Internal | Evaluate loyalty tier placement; recommend point multipliers, exclusive offers, and tier acceleration paths |
| 6. Lapsed Detection | Internal | Flag customers with no activity >90 days and declining CLV trajectory; trigger win-back workflow |

**Dependencies:** Customer_Profile, Transaction, Loyalty_Account, Loyalty_Transaction, Basket, Basket_Line, Store_Master, Product_Master, Segment, customer-data-policy, loyalty-policy

---

## 2. Demand Forecast Generation

**ID:** `WORKFLOW_DEMAND_FORECAST_V1_0` | **NRF:** Merchandising | **File:** `demand-forecast-generation.yaml`

**Trigger:** Scheduled weekly (Sunday 02:00 UTC) OR POS volume change >10% week-over-week for any category

| Step | System | Action |
|------|--------|--------|
| 1. Sales Decomposition | Internal | Decompose historical sales into trend, seasonality, promotion lift, and residual components per SKU × Store |
| 2. Feature Engineering | Internal | Build feature set: calendar events, weather forecasts, local events, competitor signals, social sentiment |
| 3. Model Ensemble | Internal | Run LightGBM + DeepAR in parallel; weighted ensemble with dynamic weight selection based on recent accuracy |
| 4. Promotion Overlay | Internal | Apply learned promotion response curves per Promotion mechanic × category × store cluster |
| 5. New Item Handling | Internal | For items with <12 weeks history: transfer demand from analogous Product_Master items using attribute similarity |
| 6. Replenishment Conversion | Internal | Convert demand forecast to replenishment plan: apply safety stock, lead times, MOQs, and shelf-life constraints |
| 7. Push to ERP | ERP | Publish SKU × Store × Week demand plan and replenishment orders to ERP (retry 3×) |

**Dependencies:** Transaction, Basket_Line, Product_Master, Store_Master, Promotion, Inventory_Position, Vendor_Master, Calendar_Event, Weather_Forecast, demand-forecast-policy, inventory-policy

---

## 3. Personalization & Recommendations

**ID:** `WORKFLOW_PERSONALIZATION_RECO_V1_0` | **NRF:** Digital Commerce | **File:** `personalization-recommendations.yaml`

**Trigger:** Customer interaction — web session start, email send event, or store visit (loyalty scan)

| Step | System | Action |
|------|--------|--------|
| 1. Profile Enrichment | Internal | Refresh Customer_Profile with latest browsing behavior, purchase history, loyalty status, and segment membership |
| 2. Collaborative Filtering | Internal | Generate recommendations from user-item interaction matrix; identify "customers like you also bought" patterns |
| 3. Content-Based Filtering | Internal | Score product affinity based on Product_Master attributes (category, brand, price tier, ingredients) vs. customer preferences |
| 4. Hybrid Ensemble | Internal | Combine collaborative and content-based scores with recency weighting; apply diversity constraints to avoid filter bubbles |
| 5. Context Layer | Internal | Adjust rankings for real-time context: location (store vs. online), time of day, weather, device, basket contents |
| 6. Offer Targeting (Uplift) | Internal | Select highest-uplift Promotion for each customer; predict incremental conversion vs. would-buy-anyway baseline |
| 7. A/B Testing | Internal | Assign customer to experiment variant; log recommendation served, impression, click, and conversion for model feedback |

**Dependencies:** Customer_Profile, Transaction, Basket, Basket_Line, Product_Master, Promotion, Loyalty_Account, Web_Session, Email_Event, Segment, personalization-policy, customer-data-policy

---

## 4. Price & Promotion Optimization

**ID:** `WORKFLOW_PRICE_PROMO_OPT_V1_0` | **NRF:** Merchandising | **File:** `price-promotion-optimization.yaml`

**Trigger:** Weekly (Monday 06:00 UTC) OR Promotion launch/end event

| Step | System | Action |
|------|--------|--------|
| 1. Baseline Estimation | Internal | Estimate non-promoted baseline sales per SKU × Store using regression on historical Transaction data |
| 2. Promotion Decomposition | Internal | Decompose promotion lift into incremental sales, pull-forward (time shift), cannibalization (cross-SKU), and halo (complementary lift) |
| 3. Elasticity Estimation | Internal | Calculate own-price and cross-price elasticities per category × store cluster from Transaction and Promotion history |
| 4. Markdown Optimization | Internal | For end-of-season/clearance: optimize markdown cadence to maximize revenue recovery while clearing inventory by target date |
| 5. Competitive Analysis | Internal | Ingest competitor pricing signals; flag items where own price >5% above market; recommend selective price matches for KVIs |
| 6. KVI Detection | Internal | Identify Key Value Items — products with outsized traffic-driving and basket-building impact — using association rules and elasticity |

**Dependencies:** Transaction, Basket_Line, Product_Master, Promotion, Store_Master, Inventory_Position, Competitor_Price, Segment, pricing-policy, promotion-policy

---

## 5. Inventory Rebalancing & Fulfillment

**ID:** `WORKFLOW_INVENTORY_FULFILLMENT_V1_0` | **GS1:** Logistics | **File:** `inventory-fulfillment.yaml`

**Trigger:** Hourly inventory scan OR Inventory_Position.Available_Qty falls below safety stock threshold

| Step | System | Action |
|------|--------|--------|
| 1. Inventory Aggregation | Internal | Build real-time inventory view across all nodes: stores, warehouses, distribution centers, in-transit, and on-order |
| 2. Order Routing Optimization | Internal | For each inbound order: evaluate fulfillment options (DC, store, vendor-direct) by cost, speed, and inventory health |
| 3. Ship-from-Store Scoring | Internal | Score eligible stores for ship-from-store: proximity to customer, excess inventory, labor capacity, historical ship accuracy |
| 4. Allocation Modeling | Internal | When inventory is constrained: allocate scarce stock across channels by demand priority, margin contribution, and customer segment |
| 5. Return Prediction | Internal | Predict return probability per order line using product category, customer history, and order attributes; adjust ATP accordingly |
| 6. ATP Calculation | ERP | Calculate Available-to-Promise considering on-hand, in-transit, allocated, reserved, and predicted returns; publish to all channels |

**Dependencies:** Inventory_Position, Store_Master, Warehouse, Product_Master, Order, Order_Line, Shipment, Return, Customer_Profile, inventory-policy, fulfillment-policy

---

## 6. Store Operations Intelligence

**ID:** `WORKFLOW_STORE_OPS_V1_0` | **NRF:** Store Ops | **File:** `store-operations.yaml`

**Trigger:** Daily (05:00 local time) OR shift change event

| Step | System | Action |
|------|--------|--------|
| 1. Traffic Forecasting | Internal | Predict hourly foot traffic per store using historical patterns, calendar events, weather, and local events |
| 2. Labor Optimization | Internal | Generate optimal staff schedule: map traffic forecast to labor demand by role (cashier, floor, receiving); minimize cost within service targets |
| 3. Shelf Monitoring (CV) | IoT/Internal | Process shelf camera feeds via computer vision; detect out-of-stock, misplaced items, planogram compliance deviations |
| 4. Shrinkage Scoring | Internal | Score shrinkage risk per store × category using inventory variance, POS exception patterns, and historical loss data |
| 5. Performance Aggregation | Internal | Aggregate store KPIs: sales per labor hour, conversion rate, basket size, NPS, task completion rate; rank across fleet |
| 6. Energy Modeling | IoT/Internal | Analyze HVAC, lighting, and refrigeration energy consumption; recommend optimization schedules based on occupancy and weather |

**Dependencies:** Store_Master, Transaction, Inventory_Position, Shelf_Condition, Staff_Schedule, Traffic_Count, Energy_Reading, Shrinkage_Event, Product_Master, store-operations-policy, sustainability-policy

---

## 7. Supplier Performance & Assortment

**ID:** `WORKFLOW_SUPPLIER_ASSORTMENT_V1_0` | **NRF:** Merchandising | **File:** `supplier-assortment.yaml`

**Trigger:** Monthly (1st business day) OR vendor delivery event with variance >10%

| Step | System | Action |
|------|--------|--------|
| 1. Vendor KPI Aggregation | ERP/Internal | Calculate supplier scorecard: on-time delivery %, fill rate, quality defect rate, lead time consistency, cost competitiveness |
| 2. Assortment Analysis | Internal | Evaluate incremental contribution of each SKU: marginal revenue lift, cannibalization of existing items, category role alignment |
| 3. Space-to-Sales Optimization | Internal | Optimize shelf space allocation using sales velocity, margin, and strategic role (traffic driver, margin builder, seasonal) |
| 4. Trend Signal Processing (NLP) | Internal | NLP scan of social media, reviews, and search trends to detect emerging product demand and declining interest signals |
| 5. Vendor Negotiation Intelligence | Internal | Prepare negotiation briefs: vendor performance vs. peers, market pricing benchmarks, volume leverage, and alternative sources |
| 6. Co-op Tracking | Internal | Track co-op and trade fund accruals vs. actuals; flag underspend and approaching expiration; recommend claims |

**Dependencies:** Vendor_Master, Product_Master, Purchase_Order, Delivery_Receipt, Transaction, Basket_Line, Store_Master, Shelf_Condition, Review, Social_Signal, vendor-management-policy, pricing-policy

---

## 8. Sustainability & Traceability

**ID:** `WORKFLOW_SUSTAINABILITY_TRACE_V1_0` | **GS1:** Traceability | **File:** `sustainability-traceability.yaml`

**Trigger:** Quarterly (5th business day after quarter end) OR product recall event OR cold-chain temperature excursion

| Step | System | Action |
|------|--------|--------|
| 1. Traceability Graph Build | Internal | Construct product lineage graph using GS1 identifiers (GTIN, GLN, SSCC): source → manufacturer → DC → store → customer |
| 2. Cold Chain Monitoring | IoT/Internal | Aggregate temperature/humidity readings along shipment path; flag excursions against product-specific thresholds |
| 3. Waste Prediction | Internal | Predict waste probability per SKU × Store using expiry dates, sell-through velocity, and demand forecast |
| 4. Dynamic Markdown for Near-Expiry | Internal | Calculate optimal markdown for items within expiry risk window to maximize sell-through and minimize waste |
| 5. Carbon Calculation | Internal | Calculate carbon footprint per product: Scope 1 (own operations), Scope 2 (energy), Scope 3 (supply chain + last-mile delivery) |
| 6. ESG Report Assembly | Internal | Generate compliance reports: GHG Protocol, food waste (FUSIONS framework), packaging recyclability, and supplier sustainability scores |

**Dependencies:** Product_Master, Shipment, Warehouse, Store_Master, Vendor_Master, Inventory_Position, Temperature_Log, Waste_Event, Energy_Reading, Packaging_Spec, sustainability-policy, food-safety-policy

---

## 9. Campaign & Engagement Orchestration

**ID:** `WORKFLOW_CAMPAIGN_ORCHESTRATION_V1_0` | **NRF:** Customer | **File:** `campaign-orchestration.yaml`

**Trigger:** Campaign launch event OR customer lifecycle trigger (new sign-up, birthday, tier change, lapsed detection)

| Step | System | Action |
|------|--------|--------|
| 1. Audience Selection | Internal | Build target audience from Segment definitions; apply suppression rules (recent contact, opt-out, fatigue limits) |
| 2. Channel Selection | Internal | Select optimal channel per customer (email, SMS, push notification, in-store display) based on historical engagement and preference |
| 3. Content Personalization | Internal | Generate personalized content: product recommendations, offer value, creative variant matched to customer segment and channel |
| 4. Send / Deploy | CRM/CDP | Execute campaign delivery across selected channels; respect send-time optimization windows per customer timezone |
| 5. Response Tracking | Internal | Capture engagement signals: open, click, redemption, store visit (geo-fence), purchase attribution within campaign window |
| 6. Attribution Analysis | Internal | Multi-touch attribution across channels; calculate incremental lift vs. control holdout; compute campaign ROI and cost per acquisition |
| 7. Model Feedback | Internal | Feed response data back to personalization and CLV models; update segment membership and channel preferences |

**Dependencies:** Customer_Profile, Segment, Promotion, Loyalty_Account, Email_Event, Web_Session, Transaction, Product_Master, Store_Master, Campaign, campaign-policy, customer-data-policy

---

## 10. Omnichannel Fraud & Loss Prevention

**ID:** `WORKFLOW_FRAUD_LOSS_PREVENTION_V1_0` | **NRF:** Store Ops | **File:** `fraud-loss-prevention.yaml`

**Trigger:** Real-time POS Transaction event (void, refund, discount override) OR inventory count discrepancy >threshold

| Step | System | Action |
|------|--------|--------|
| 1. POS Anomaly Detection | Internal | Score transactions for anomalies: excessive voids, suspicious refunds, sweethearting patterns, unusual discount overrides |
| 2. Self-Checkout Monitoring | IoT/Internal | Analyze self-checkout events: scan-skip detection, weight mismatch, barcode switching, and non-scan rate per session |
| 3. Inventory Shrinkage Correlation | Internal | Correlate inventory variance with POS exceptions, receiving discrepancies, and transfer anomalies to identify shrinkage root cause |
| 4. Employee Pattern Analysis | Internal | Detect anomalous employee behavior: register patterns outside peer norms, high void rates, after-hours transactions, buddy punching |
| 5. Return Fraud Scoring | Internal | Score return transactions: receipt-less frequency, high-value serial returners, cross-store return patterns, wardrobing indicators |
| 6. Alert Generation | Internal | Generate prioritized alerts for Loss Prevention team; attach evidence package: transaction details, video timestamp links, pattern history |

**Dependencies:** Transaction, Basket, Basket_Line, Return, Inventory_Position, Store_Master, Staff_Schedule, Shrinkage_Event, Self_Checkout_Event, Product_Master, loss-prevention-policy, store-operations-policy

---

[← Back to Ontology Overview](index.md)
