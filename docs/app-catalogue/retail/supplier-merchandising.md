# Supplier & Merchandising Analytics

Vendor performance management, assortment optimization, and category management intelligence.

**Priority:** P3 — Operational Excellence  
**Time to Value:** 10-12 weeks  
**Category:** Merchandising & Procurement

---

## Business Problem

Retail merchandising involves managing thousands of vendor relationships and tens of thousands of SKUs. Decisions about what to carry, how much to buy, and from whom are high-stakes:

- **Vendor performance opacity** — supplier on-time delivery, fill rates, and quality are tracked in spreadsheets, not systematically measured against commitments
- **Assortment bloat** — SKU count grows over time as new products are added but slow-sellers are not delisted, tying up shelf space and working capital
- **Category strategy gaps** — category managers rely on intuition rather than data to determine the right mix of brands, price tiers, and pack sizes per store cluster
- **Vendor negotiation weakness** — without unified performance data, buyers lack leverage to negotiate better terms, co-op funding, and markdown allowances
- **Trend lag** — emerging consumer trends (plant-based, sugar-free, sustainable packaging) are detected from social media and reviews months before sales data shows the shift

---

## Capabilities

### Vendor Scorecard & Performance Management
Automated vendor performance tracking: on-time delivery rate, fill rate, quality defect rate, cost compliance, and promotional support — scored and ranked across the supplier base.

### Assortment Optimization
Data-driven SKU rationalization: identify which products to add, keep, or delist based on incremental contribution (would sales be lost or captured by substitutes?), margin, inventory turns, and customer demand.

### Category Space Optimization
Optimize shelf space allocation per category and sub-category using planogram performance data, sales velocity, margin contribution, and cross-category affinity.

### Trend Detection & New Product Intelligence
AI monitoring of social media trends, product reviews, search query shifts, and competitor assortment changes to identify emerging categories and products before they reach mainstream demand.

### Vendor Co-Op & Trade Fund Optimization
Track and optimize vendor co-op advertising spend, trade promotions, and markdown allowances to ensure the retailer captures full entitled funding and allocates it effectively.

---

## Data Sources & Ontology Mapping

| Ontology Entity | Source System | Key Fields |
|----------------|--------------|------------|
| Vendor / Supplier | ERP Vendor Master | Vendor ID, Name, Category, Lead Time, Payment Terms, Rating |
| Purchase Orders | ERP Procurement | PO Number, Vendor, SKUs, Qty, Price, Delivery Date, Status |
| Product Performance | POS + ERP | SKU, Store, Units Sold, Revenue, Margin, Inventory Turns, Days of Supply |
| Category Structure | ERP Item Master | Category, Sub-category, Brand, Price Tier, Attributes, Planogram Position |
| Market Trends | Social Media + Reviews + Digital | Trending Topics, Search Volume, Review Sentiment, Competitor New Products |

---

## AI Workflow

1. **Vendor Performance Aggregation** — Calculate per-vendor KPIs from ERP data: on-time delivery %, fill rate %, cost variance, quality return rate, and promotional compliance
2. **Assortment Analysis** — For each SKU, model incremental contribution: if delisted, what % of sales would be lost (unique demand) vs. captured by substitutes? Rank SKUs by contribution per facing
3. **Space-to-Sales Optimization** — Correlate shelf space (facings, position) with sales velocity and margin; identify over-spaced low performers and under-spaced high performers
4. **Trend Signal Processing** — NLP on social media, product review platforms, and search trends to detect emerging categories, ingredients, formats, and consumer preferences
5. **Vendor Negotiation Intelligence** — Compile performance data, market benchmarks, and competitive alternatives into negotiation briefing packages for buying team
6. **Co-Op Tracking** — Reconcile vendor co-op funding commitments against actual spending; identify unclaimed allowances and sub-optimal allocation
7. **Output** — Vendor scorecards for buying team; assortment recommendations for category managers; space optimization for planogram team; trend reports for product development; co-op reconciliation for finance

---

## Dashboard & Alerts

### Key Metrics

| KPI | Description | Target |
|-----|-------------|--------|
| **Vendor On-Time Delivery** | % of POs delivered within committed window | > 95% |
| **SKU Productivity** | Revenue per SKU per store per week | Grow top 80% of assortment |
| **Assortment ROI** | Total category margin / Total SKU count (margin per SKU) | Year-over-year improvement |
| **Shelf Space Yield** | Gross margin per linear foot of shelf space | Improve 5% annually |
| **Trend Detection Lead Time** | Weeks between trend signal detection and assortment response | < 8 weeks |
| **Co-Op Fund Capture** | % of entitled vendor co-op funding actually claimed | > 95% |

### Alert Rules

| Alert | Trigger | Severity | Action |
|-------|---------|----------|--------|
| Vendor underperformance | On-time delivery drops below 85% for 2 consecutive months | High | Issue vendor warning; initiate performance improvement plan |
| Dead stock | SKU has <2 units sold across all stores in 8 weeks | Medium | Initiate delist review; consider markdown to clear |
| Emerging trend | Social + search signals detect a new trend growing >50% month-over-month | Medium | Brief category manager; assess assortment gap; source potential suppliers |
| Co-op underspend | Vendor co-op fund utilization <60% with 3 months remaining in period | Medium | Notify marketing team; plan co-op funded campaigns |
| Space mismatch | SKU getting 4+ facings but ranks in bottom 25% of category by sales velocity | Info | Flag for planogram review; consider space reallocation |

---

## ROI Model

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Vendor on-time delivery | 88% | 95% | **8% improvement → fewer stockouts** |
| SKU rationalization | 18,000 SKUs | 14,500 SKUs (with same revenue) | **19% reduction → freed shelf space and working capital** |
| Shelf space yield | $42/linear ft/week | $51/linear ft/week | **21% improvement → $2.8M margin lift** |
| Unclaimed co-op funds | $1.2M left unclaimed annually | $200K unclaimed | **$1M recovered** |
| Trend response time | 16 weeks from signal to shelf | 6 weeks | **63% faster → first-mover advantage** |

!!! success "Estimated Annual ROI"
    **$4M - $7M** annually from assortment optimization, space yield improvement, vendor performance gains, and co-op fund recovery — across a mid-size retailer with $250M revenue and 500+ vendors.

---

## Implementation Notes

- Vendor performance measurement requires clean PO and receiving data from ERP with reliable delivery dates and quantity accuracy
- Assortment optimization is best applied at the category-store-cluster level; a single national assortment ignores local demand differences
- Trend detection NLP requires monitoring of category-specific social channels, review platforms, and food/lifestyle blogs relevant to the retailer's categories
- Co-op fund tracking requires digitization of vendor agreements, which are often managed in email/PDF format
- Space optimization works best when combined with planogram compliance monitoring from the Store Operations app

---

[← Back to Catalogue](index.md) | [Previous: Store Operations](store-operations.md) | [Next: Sustainability →](sustainability-compliance.md)
