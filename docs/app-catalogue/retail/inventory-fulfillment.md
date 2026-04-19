# Inventory & Fulfillment Intelligence

Omnichannel inventory visibility, ship-from-store optimization, and intelligent stock allocation.

**Priority:** P2 — Strategic Value  
**Time to Value:** 8-10 weeks  
**Category:** Fulfillment & Logistics

---

## Business Problem

Omnichannel retail requires inventory visibility across stores, warehouses, dark stores, and third-party fulfillment — with customers expecting same-day or next-day delivery:

- **Siloed inventory** — store stock, DC stock, and e-commerce inventory managed independently; a customer sees "out of stock" online while nearby stores hold excess
- **Fulfillment cost escalation** — fulfilling online orders from DCs via parcel shipping costs 3-5x more than ship-from-store or BOPIS (buy online, pick up in-store)
- **Stock allocation guesswork** — initial seasonal allocation to stores is based on last year's sales mix, not current demand signals
- **Split shipments** — multi-item orders fulfilled from multiple locations, multiplying shipping costs and degrading customer experience
- **Return complexity** — cross-channel returns (buy online, return in-store) create inventory reconciliation headaches and misplaced stock

---

## Capabilities

### Unified Inventory Visibility
Single real-time view of inventory across all nodes: DCs, stores, dark stores, drop-ship suppliers, and in-transit stock — with available-to-promise (ATP) calculation per channel.

### Intelligent Order Routing
AI-driven fulfillment decision for each online order: which node should fulfill based on inventory availability, shipping cost, delivery speed, store workload, and margin impact?

### Ship-From-Store Optimization
Identify stores with excess stock that can profitably fulfill online orders, turning overstock into a fulfillment asset rather than a markdown liability.

### Predictive Stock Allocation
AI-driven initial allocation and replenishment of seasonal/new products to stores based on store-level demand potential, local demographics, and similar-item sales history.

### Return Flow Optimization
Predict return probability per order and optimize return routing: return to nearest store for resale, return to DC for redistribution, or direct to liquidation based on item condition and demand.

---

## Data Sources & Ontology Mapping

| Ontology Entity | Source System | Key Fields |
|----------------|--------------|------------|
| Inventory Positions | ERP / WMS | SKU, Location (Store/DC/Transit), Quantity, Status, Last Updated |
| Online Orders | E-commerce Platform | Order ID, Items, Customer Address, Delivery Promise, Status |
| Store Capacity | POS + Operations | Store ID, Fulfillment Capacity (orders/day), Pick Accuracy, Packing Time |
| Shipping Costs | ERP / 3PL | Origin, Destination, Weight, Service Level, Cost, Transit Days |
| Return History | POS + E-commerce | Order ID, Return Reason, Condition, Channel, Refund/Exchange, Disposition |

---

## AI Workflow

1. **Inventory Aggregation** — Real-time consolidation of stock positions from ERP (DC/warehouse), POS (store), in-transit (logistics), and supplier ATP into unified available-to-promise per SKU-location
2. **Order Routing Optimization** — For each incoming online order, evaluate candidate fulfillment nodes by: has stock → shipping cost to customer → delivery speed → store picking capacity → profit margin after fulfillment cost
3. **Ship-From-Store Scoring** — Rank stores by SFS suitability: excess stock level, historical pick accuracy, fulfillment cost competitiveness vs. DC, and store operational capacity
4. **Allocation Modeling** — For new seasonal buys, predict store-level demand using demand forecasting outputs, local demographics, similar-item performance, and store traffic data; allocate proportionally
5. **Return Prediction** — Score each order at checkout for return probability based on item category, customer return history, size selection confidence, and historical return rates; route returns to optimal destination
6. **Output** — Inventory visibility dashboard for supply chain; order routing decisions for OMS; SFS store scoring for operations; allocation recommendations for buying; return flow routing for logistics

---

## Dashboard & Alerts

### Key Metrics

| KPI | Description | Target |
|-----|-------------|--------|
| **Inventory Accuracy** | % of SKU-locations where system matches physical count | > 98% |
| **Order Fulfillment Cost** | Average cost to fulfill an online order (pick + pack + ship) | Reduce 15% year-over-year |
| **Ship-From-Store %** | % of online orders fulfilled from stores | > 25% (where profitable) |
| **On-Time Delivery** | % of orders delivered within promised window | > 95% |
| **Split Shipment Rate** | % of multi-item orders shipped from 2+ locations | < 15% |
| **Allocation Accuracy** | Actual vs. planned sell-through by store at end of season | ± 10% |

### Alert Rules

| Alert | Trigger | Severity | Action |
|-------|---------|----------|--------|
| Fulfillment bottleneck | Store SFS queue exceeds daily capacity by >30% | High | Reroute new orders to alternate node; notify store manager |
| Inventory discrepancy | System vs. physical count gap >5% for a store after cycle count | High | Investigate cause (shrinkage, receiving error); adjust ATP |
| Delivery SLA risk | Order in fulfillment pipeline projected to miss delivery promise | Medium | Expedite shipping; notify customer if needed |
| Overstock + online demand match | Store has >8 weeks supply while online demand exists in same region | Medium | Activate SFS for those SKUs at that store |
| Return surge | Return rate for a product exceeds 25% in 7-day window | Info | Flag to merchandising; investigate sizing/description issue |

---

## ROI Model

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Average fulfillment cost / order | $8.50 | $6.20 | **27% reduction → $4.6M savings** on 2M online orders |
| Ship-from-store adoption | 8% of online orders | 28% of online orders | **3.5x increase → turns store overstock into revenue** |
| Split shipment rate | 28% | 13% | **54% reduction → cost and CX improvement** |
| Markdown from mis-allocation | $3.8M / year | $2.2M / year | **$1.6M margin saved** |
| On-time delivery | 89% | 96% | **7 pt improvement → NPS and repeat purchase boost** |

!!! success "Estimated Annual ROI"
    **$6M - $10M** annually from fulfillment cost reduction, SFS optimization, better allocation, and delivery improvement — across a mid-size omnichannel retailer with $250M revenue and 2M online orders.

---

## Implementation Notes

- Unified inventory visibility requires real-time integration with ERP/WMS (DC stock) and POS (store stock); stock accuracy must be >95% before ATP is reliable
- Order routing optimization requires integration with the Order Management System (OMS); some OMS platforms have native routing that can be enhanced vs. replaced
- Ship-from-store requires operational readiness at stores (pick/pack stations, shipping supplies, carrier pickup schedules)
- Return prediction models need 12+ months of return data with reason codes, item attributes, and customer history
- Store-level demand allocation for new products relies on the Demand Forecasting app's new-item forecasting capability

---

[← Back to Catalogue](index.md) | [Previous: Price Optimization](price-optimization.md) | [Next: Store Operations →](store-operations.md)
