# Store Operations & Workforce

Labor scheduling optimization, planogram compliance monitoring, and shrinkage detection for physical retail.

**Priority:** P2 — Strategic Value  
**Time to Value:** 8-10 weeks  
**Category:** Store Operations

---

## Business Problem

Physical stores remain the primary revenue channel for most retailers, yet store operations are managed with limited data-driven intelligence:

- **Over/under-staffing** — labor schedules based on historical averages, not predicted traffic; stores are overstaffed during slow periods and understaffed during peaks
- **Planogram non-compliance** — product placement deviates from planned merchandising layouts; premium shelf positions are empty or misplaced, reducing category performance
- **Shrinkage** — inventory loss from theft (internal and external), administrative errors, and vendor fraud amounts to 1.4-1.6% of retail sales industry-wide
- **Store performance opacity** — managers lack real-time visibility into traffic-to-conversion ratios, average basket size, and staff productivity metrics
- **Energy waste** — HVAC, lighting, and refrigeration run at fixed schedules regardless of store occupancy and weather conditions

---

## Capabilities

### AI-Driven Labor Scheduling
Predict store traffic by hour and day using historical patterns, weather, local events, and promotional calendar. Generate optimized staff schedules that match labor to demand while respecting labor laws and employee preferences.

### Planogram Compliance Monitoring
Computer vision analysis of shelf images (from cameras or associate mobile captures) to detect: out-of-stocks, misplaced products, planogram deviations, and price tag accuracy.

### Shrinkage Detection & Prevention
Anomaly detection on POS transactions (voids, refunds, discounts, no-sale drawer openings), inventory movements, and self-checkout patterns to identify potential theft and administrative loss.

### Store Performance Analytics
Real-time dashboard combining foot traffic (IoT), conversion rate (traffic vs. transactions), average basket size, units per transaction, and staff productivity (revenue per labor hour).

### Energy Optimization
AI control of HVAC, lighting, and refrigeration based on store occupancy, weather forecasts, and time-of-day patterns to reduce energy consumption without impacting customer comfort.

---

## Data Sources & Ontology Mapping

| Ontology Entity | Source System | Key Fields |
|----------------|--------------|------------|
| Store Traffic | In-Store IoT (foot traffic sensors) | Store, Zone, Timestamp, Visitor Count, Dwell Time |
| POS Transactions | POS / Commerce | Transaction ID, Store, Register, Items, Total, Voids, Refunds, Employee |
| Labor Schedules | Workforce Management / HR | Employee, Store, Shift, Hours, Role, Cost Rate |
| Shelf Conditions | IoT (cameras, shelf sensors, RFID) | Store, Aisle, Shelf, SKU, Compliance Status, Gap Detected, Image |
| Inventory Shrinkage | ERP + POS | SKU, Store, Expected Stock, Actual Stock, Variance, Last Count Date |

---

## AI Workflow

1. **Traffic Forecasting** — Predict hourly foot traffic per store using historical patterns, weather forecasts, local events, promotional calendar, and day-of-week/holiday effects
2. **Labor Optimization** — Generate staff schedules that minimize labor cost while meeting service-level targets (max wait time, customer-to-staff ratio); respect labor law constraints (breaks, maximum hours, minimum notice)
3. **Shelf Monitoring** — Process shelf images through computer vision models to detect: empty facings (OOS), wrong product placement, missing price tags, and planogram deviations
4. **Shrinkage Scoring** — Analyze POS patterns for anomalies: excessive voids/refunds per cashier, sweethearting patterns (items scanned but not charged), unusual self-checkout behavior, inventory count discrepancies
5. **Performance Aggregation** — Combine traffic, conversion, basket, and labor data into real-time store performance scorecards; benchmark across the fleet
6. **Energy Modeling** — Correlate energy consumption with occupancy patterns and weather; optimize HVAC/lighting schedules based on predicted traffic and external temperature
7. **Output** — Labor schedules for store managers; planogram compliance reports for merchandising; shrinkage alerts for loss prevention; store performance dashboard for regional directors; energy optimization commands for BMS

---

## Dashboard & Alerts

### Key Metrics

| KPI | Description | Target |
|-----|-------------|--------|
| **Labor Cost as % of Revenue** | Store labor cost / Store revenue | < 12% |
| **Traffic-to-Conversion Rate** | Transactions / Foot traffic visitors | > 25% |
| **Planogram Compliance** | % of shelf positions matching planned layout | > 92% |
| **Shrinkage Rate** | Inventory loss / Revenue | < 1.0% (industry avg 1.4%) |
| **Revenue per Labor Hour** | Store revenue / Total labor hours worked | Year-over-year improvement of 5% |
| **Energy Cost per Sq Ft** | Annual energy cost / Store square footage | Reduce 10% year-over-year |

### Alert Rules

| Alert | Trigger | Severity | Action |
|-------|---------|----------|--------|
| Staffing gap | Predicted traffic exceeds staffed capacity by >20% for upcoming shift | High | Call in additional staff; adjust schedule |
| Shrinkage anomaly | Cashier void/refund rate exceeds 3σ above store average | High | Alert loss prevention; review transaction footage |
| Planogram violation | >15% of checked shelf positions non-compliant in a department | Medium | Notify store associate for reset; flag to merchandising |
| Conversion drop | Store conversion rate drops >5 pts below 30-day average | Medium | Investigate causes (staffing, OOS, layout change); notify store manager |
| Energy spike | Store energy consumption exceeds predicted by >20% for 3+ days | Info | Check HVAC settings; investigate equipment malfunction |

---

## ROI Model

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Labor cost as % of revenue | 13.5% | 11.8% | **1.7 pt reduction → $4.3M savings** across 100 stores |
| Shrinkage rate | 1.5% of revenue | 0.9% of revenue | **40% reduction → $1.5M savings** |
| Planogram compliance | 78% | 94% | **21% improvement → $1.2M sales lift** from better placement |
| Conversion rate | 22% | 27% | **5 pt improvement → $3.1M incremental revenue** |
| Energy costs | $2.8M / year | $2.2M / year | **$600K savings** |

!!! success "Estimated Annual ROI"
    **$7M - $12M** annually from labor optimization, shrinkage reduction, planogram compliance, conversion improvement, and energy savings — across a 100-store retailer with $250M annual revenue.

---

## Implementation Notes

- Foot traffic sensors (overhead counters or thermal sensors) must be installed at store entrances; accuracy should be validated against manual counts
- Computer vision for planogram compliance requires camera infrastructure or a mobile capture workflow for associates
- Shrinkage detection models need 12+ months of POS transaction data with labeled shrinkage events (confirmed theft, administrative errors)
- Labor scheduling must integrate with the retailer's workforce management system and respect local labor regulations
- Energy optimization requires integration with the Building Management System (BMS) for HVAC and lighting control

---

[← Back to Catalogue](index.md) | [Previous: Inventory & Fulfillment](inventory-fulfillment.md) | [Next: Supplier & Merchandising →](supplier-merchandising.md)
