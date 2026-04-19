# Supply Chain & Pharmacy Intelligence

Medical supply optimization, drug formulary management, expiry reduction, and procurement analytics for healthcare.

**Priority:** P2 — Strategic Value  
**Time to Value:** 8-10 weeks  
**Category:** Supply Chain & Pharmacy

---

## Business Problem

Healthcare supply chain and pharmacy operations represent 30-40% of a hospital's operating budget, yet are managed with limited data-driven intelligence:

- **Supply waste** — surgical supplies opened but unused, expired medications destroyed, and overstocked items tying up capital across departments
- **Stockouts of critical items** — essential medications and surgical supplies run out, forcing expensive emergency orders or clinical workarounds
- **Formulary cost creep** — drug costs rise as new high-cost medications enter formulary without rigorous therapeutic equivalence and cost-effectiveness analysis
- **Physician preference variation** — surgeons use different implants and supplies for the same procedure, creating cost variation without outcome improvement
- **Contract compliance gaps** — GPO (Group Purchasing Organization) contract pricing is not consistently captured, leaving negotiated savings on the table
- **Controlled substance diversion** — opioid and controlled substance diversion by staff or patients is difficult to detect with manual auditing

---

## Capabilities

### Demand-Driven Supply Replenishment
AI forecasting of supply consumption at the department level based on scheduled procedures, census predictions, seasonal patterns, and historical usage — replacing par-level guesswork with data-driven replenishment.

### Formulary Optimization
Analysis of drug utilization patterns, therapeutic equivalence, and total cost (acquisition + administration + monitoring + adverse events) to recommend formulary additions, removals, and therapeutic substitutions.

### Expiry & Waste Reduction
Track lot-level expiry dates across pharmacy and supply rooms; predict waste risk; recommend redistribution between locations, FIFO enforcement, and vendor return eligibility before items expire.

### Physician Preference Standardization
Analyze supply and implant utilization per procedure per surgeon; identify variation that does not correlate with better outcomes; support standardization conversations with outcome-linked data.

### Controlled Substance Monitoring
AI analysis of controlled substance dispensing patterns, waste documentation, and patient administration records to detect anomalies indicative of diversion.

---

## Data Sources & Ontology Mapping

| Ontology Entity | Source System | Key Fields |
|----------------|--------------|------------|
| Supply Inventory | HIS / Materials Management | Item, Location, Quantity, Lot, Expiry Date, Par Level, Vendor |
| Pharmacy Inventory | Pharmacy System | Drug, NDC, Quantity, Lot, Expiry, Formulary Status, Cost |
| Consumption / Usage | EHR + OR System | Item, Case/Encounter, Quantity Used, Waste Qty, Department, Date |
| Purchase Orders | HIS Procurement | PO Number, Vendor, Items, Qty, Price, GPO Contract, Delivery Date |
| Controlled Substances | Pharmacy + EHR | Drug, Dispense Event, Patient, Nurse, Waste Witness, Quantity, Timestamp |

---

## AI Workflow

1. **Consumption Forecasting** — Predict department-level supply and drug consumption based on surgical schedule (implants, surgical supplies), census forecast (floor supplies, medications), and historical usage patterns
2. **Replenishment Optimization** — Convert forecasts into replenishment orders considering lead times, vendor minimums, storage capacity, and expiry risk; prioritize FIFO rotation
3. **Formulary Analysis** — Compare drug utilization across therapeutic classes; identify opportunities for generic substitution, biosimilar adoption, and therapeutic interchange; model total cost impact including adverse event rates
4. **Variation Analysis** — For high-cost procedure categories, compare supply/implant utilization per surgeon against peer benchmarks and outcome data; flag statistically significant cost outliers without outcome justification
5. **Expiry Tracking** — Monitor lot-level expiry across all locations; predict waste probability based on current consumption rate vs. remaining shelf life; route near-expiry items for redistribution or vendor credit
6. **Diversion Detection** — Analyze controlled substance transaction patterns for anomalies: nurse accessing narcotics during off-shift, waste quantities exceeding norms, patient-reported pain inconsistent with documented administration
7. **Output** — Supply dashboard for materials management; formulary recommendations for P&T committee; surgeon variation reports for service line leaders; expiry alerts for pharmacy; diversion flags for compliance officer

---

## Dashboard & Alerts

### Key Metrics

| KPI | Description | Target |
|-----|-------------|--------|
| **Supply Expense per Case** | Supply cost per surgical case (by procedure type) | Reduce 5% year-over-year |
| **Drug Expense PMPM** | Pharmacy cost per member per month (for employed populations) | Below benchmark |
| **Expired Waste Rate** | Value of expired items / Total inventory value | < 1% |
| **Formulary Compliance** | % of prescriptions written for formulary drugs | > 92% |
| **GPO Contract Compliance** | % of purchases at GPO-contracted pricing | > 95% |
| **Stockout Rate** | Critical supply/drug stockout events per month | < 3 |

### Alert Rules

| Alert | Trigger | Severity | Action |
|-------|---------|----------|--------|
| Critical stockout risk | Essential medication or supply projected to reach zero within 48 hours | Critical | Emergency order; notify pharmacy/materials director; identify clinical alternatives |
| Diversion anomaly | Controlled substance dispensing pattern for a nurse exceeds 3σ above unit average | Critical | Alert compliance officer and pharmacy director; initiate investigation per policy |
| Expiry imminent | Drug or supply lot within 30 days of expiry with quantity >$5K value | High | Redistribute to higher-consumption location; process vendor return if eligible |
| Surgeon cost outlier | Surgeon's supply cost per case exceeds peer average by >25% for same procedure | Medium | Generate variation report; schedule review with service line chief |
| Off-contract purchase | Purchase placed at non-GPO pricing for a contracted item | Medium | Alert procurement; redirect future orders to contracted vendor |

---

## ROI Model

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Supply cost per surgical case | $2,400 average | $2,100 average | **12% reduction → $3.6M savings** on 12K cases/year |
| Pharmacy expired waste | $1.8M / year | $600K / year | **67% reduction → $1.2M savings** |
| Formulary optimization | — | Generic/biosimilar substitution | **$2.4M annual drug cost reduction** |
| GPO compliance | 82% | 96% | **17% improvement → $1.1M additional contracted savings** |
| Controlled substance diversion | 4 incidents/year detected (reactive) | Proactive monitoring | **Risk reduction + $500K liability avoidance** |

!!! success "Estimated Annual ROI"
    **$6M - $10M** annually from supply cost reduction, waste elimination, formulary optimization, and contract compliance — across a mid-size health system with $80M annual supply and pharmacy spend.

---

## Implementation Notes

- Supply consumption tracking requires item-level usage capture in OR and floor supply systems; barcode/RFID scanning at point of use provides the most accurate data
- Formulary optimization recommendations must be reviewed and approved by the Pharmacy & Therapeutics (P&T) committee
- Surgeon variation analysis is sensitive; data must be presented in the context of clinical outcomes (not just cost) to gain physician engagement
- Controlled substance diversion detection must comply with HR policies and legal requirements; false positives carry significant consequences
- GPO contract pricing data must be loaded and maintained; contract renegotiations happen annually and pricing must be updated accordingly

---

[← Back to Catalogue](index.md) | [Previous: Population Health](population-health.md) | [Next: Clinical Quality →](clinical-quality.md)
