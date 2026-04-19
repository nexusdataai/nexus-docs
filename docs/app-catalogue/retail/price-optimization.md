# Price & Promotion Optimization

Markdown optimization, promotion effectiveness measurement, and competitive pricing intelligence for retail.

**Priority:** P1 — High Value  
**Time to Value:** 6-8 weeks  
**Category:** Merchandising & Finance

---

## Business Problem

Pricing and promotions are the largest levers for retail profitability, yet most pricing decisions are made manually using rules of thumb:

- **Margin erosion** — promotions are run on gut feel; 30-40% of promotional spend generates no incremental volume (subsidizing purchases that would happen anyway)
- **Markdown timing** — end-of-season markdowns are applied too late or too aggressively, either leaving unsold inventory or destroying margin unnecessarily
- **Competitive blind spots** — pricing decisions made without real-time visibility into competitor pricing and promotional activity
- **Price perception gap** — customers perceive the retailer as expensive on key value items (KVIs) while the retailer over-invests in discounting low-sensitivity items
- **Promotion cannibalization** — promotions on one SKU steal volume from full-price substitutes without growing the category

---

## Capabilities

### Promotion Effectiveness Measurement
Measure true incremental lift of every promotion by controlling for base demand, seasonality, and cannibalization — quantifying which promotions drive profit vs. destroy margin.

### Markdown Optimization
AI-driven markdown timing and depth recommendations for end-of-life, seasonal, and slow-moving inventory to maximize revenue recovery while clearing stock by target dates.

### Competitive Price Monitoring
Automated tracking of competitor prices across key SKUs and categories. Alert when competitive gaps exceed thresholds; model the volume impact of price matching vs. maintaining position.

### Price Elasticity Modeling
Measure price sensitivity per SKU × store cluster to identify optimal regular price points that maximize revenue or margin, depending on category strategy (traffic-driver vs. margin-builder).

### Key Value Item (KVI) Identification
AI analysis of which products most influence customer price perception. Ensure competitive pricing on KVIs while protecting margin on low-sensitivity items.

---

## Data Sources & Ontology Mapping

| Ontology Entity | Source System | Key Fields |
|----------------|--------------|------------|
| Sales & Price History | POS + E-commerce | SKU, Store, Date, Units, Revenue, Selling Price, Original Price, Promo Flag |
| Promotion Details | ERP / Marketing | Promo ID, Mechanic, Discount %, Start/End, Scope (SKU/Category), Cost Share (Vendor) |
| Competitor Prices | Web Scraping / Price Intel | Competitor, SKU/Match, Price, Promo, Date, Channel |
| Product Attributes | ERP Item Master | SKU, Category, Brand, Cost Price, Margin %, Shelf Life, Season |
| Inventory Positions | ERP Warehouse/Store | SKU, Store, On Hand, Weeks of Supply, Sell-Through Rate |

---

## AI Workflow

1. **Baseline Estimation** — Build per-SKU-store baseline demand models isolating the effect of price, promotion, seasonality, and trend
2. **Promotion Decomposition** — For each historical promotion, decompose total sales into: baseline (would have happened anyway), incremental (true lift), pull-forward (borrowed from future weeks), cannibalization (stolen from other SKUs), and halo (category uplift)
3. **Elasticity Estimation** — Estimate price elasticity per SKU × store cluster using natural price variation, markdown events, and A/B tests where available
4. **Markdown Optimization** — For items requiring clearance, optimize markdown schedule (timing, depth, cadence) to maximize revenue recovery subject to sell-through target by deadline
5. **Competitive Analysis** — Match competitor SKUs to own assortment; track price positioning; model volume impact of competitive gaps using cross-elasticity estimates
6. **KVI Detection** — Identify products where price perception impact (measured through traffic, basket size, and customer sentiment correlation) exceeds their direct margin contribution
7. **Output** — Promotion ROI reports for merchandising; markdown recommendations for planning; competitive alerts for pricing team; KVI scorecard for category managers

---

## Dashboard & Alerts

### Key Metrics

| KPI | Description | Target |
|-----|-------------|--------|
| **Promotion ROI** | Incremental gross margin / Promotion cost | > 3.0x |
| **Promotion Waste %** | % of promotional volume that is non-incremental | < 25% |
| **Markdown Recovery Rate** | Revenue recovered / Original full-price potential for marked-down goods | > 65% |
| **Gross Margin %** | Gross margin as % of revenue | Improve 1-2 pts annually |
| **Competitive Price Index** | Average price position vs. key competitors (100 = parity) | 98-102 on KVIs |
| **Price Perception Score** | Customer survey-based value-for-money rating | > 7.5 / 10 |

### Alert Rules

| Alert | Trigger | Severity | Action |
|-------|---------|----------|--------|
| Promotion destroying margin | Promotion ROI < 1.0x (cost exceeds incremental margin) for current running promotion | High | Evaluate early termination; review promo mechanic |
| Competitive gap | Competitor prices >10% below on a KVI for 7+ days | High | Model volume impact; recommend pricing response |
| Markdown deadline risk | Seasonal inventory >40% remaining with <4 weeks to clearance deadline | High | Trigger deeper markdown; consider channel shift (online clearance) |
| Elasticity shift | Price elasticity for a category changes >25% vs. prior quarter | Medium | Investigate driver (competitor action, market shift); recalibrate models |
| Cannibalization detected | Promotion on SKU A causes >15% volume decline in substitute SKU B | Info | Alert category manager; consider excluding substitute from next promo cycle |

---

## ROI Model

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Gross margin % | 38.2% | 40.5% | **2.3 pt improvement → $5.8M on $250M revenue** |
| Promotion waste | 38% non-incremental | 22% non-incremental | **42% reduction → $2.1M margin recovered** |
| Markdown recovery | 52% of original value | 68% of original value | **31% improvement → $1.8M margin saved** |
| Competitive price response time | 7-14 days (manual review) | Same-day automated alert | **90% faster** |
| Pricing team productivity | 80% time on manual analysis | 30% time (AI-assisted) | **62% time freed for strategic work** |

!!! success "Estimated Annual ROI"
    **$7M - $12M** annually from margin improvement, promotion optimization, markdown recovery, and competitive responsiveness — across a mid-size retailer with $250M annual revenue.

---

## Implementation Notes

- Promotion effectiveness measurement requires clean promotion master data with exact start/end dates, mechanics, and SKU scope
- Price elasticity estimation needs sufficient natural price variation; retailers with rigid pricing may need to run controlled price tests
- Competitive price monitoring requires either an automated web scraping pipeline or subscription to a price intelligence provider (Competera, Prisync)
- Markdown optimization is most impactful for fashion, seasonal, and perishable categories with clear sell-through deadlines
- KVI identification requires customer traffic and basket data linked to price changes — POS + foot traffic (IoT) data combination is ideal

---

[← Back to Catalogue](index.md) | [Previous: Personalization](personalization.md) | [Next: Inventory & Fulfillment →](inventory-fulfillment.md)
