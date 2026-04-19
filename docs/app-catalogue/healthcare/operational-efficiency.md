# Operational Efficiency & Capacity

Bed management optimization, OR scheduling intelligence, patient flow prediction, and staffing optimization.

**Priority:** P1 — High Value  
**Time to Value:** 6-8 weeks  
**Category:** Hospital Operations

---

## Business Problem

Hospital operations are constrained by fixed physical capacity (beds, ORs, infusion chairs) and variable demand (ED arrivals, scheduled admissions, surgical cases). Inefficient capacity utilization is costly:

- **Bed boarding** — ED patients wait 4-8 hours for inpatient beds because discharge timing is unpredictable and bed turnover is slow
- **OR idle time** — 20-30% of scheduled OR time is wasted through late starts, case cancellations, inaccurate case duration estimates, and turnover inefficiency
- **Staffing mismatches** — nurse staffing based on midnight census misses daytime peaks; travel nurse costs escalate during surges
- **Length of stay (LOS) outliers** — patients stay longer than clinically necessary due to discharge process delays (pending tests, transport, post-acute placement)
- **Patient flow bottlenecks** — congestion at handoff points (ED-to-inpatient, PACU-to-floor, floor-to-discharge) creates cascading delays throughout the hospital

---

## Capabilities

### Predictive Bed Management
Forecast bed demand by unit 24-72 hours ahead using scheduled admissions, predicted ED admissions, expected discharges (LOS prediction), and post-surgical transfers — enabling proactive bed assignment.

### OR Schedule Optimization
AI-driven block schedule optimization and real-time surgical schedule management: accurate case duration prediction, optimal case sequencing, turnover time minimization, and add-on case placement.

### Patient Flow Prediction
Model patient flow through the hospital: ED arrival forecasting, ED-to-admission conversion prediction, inpatient LOS prediction, and discharge timing prediction — identifying bottlenecks before they form.

### Discharge Planning Intelligence
Predict optimal discharge date per patient at admission; identify barriers to timely discharge (pending tests, consults, post-acute bed availability, patient/family readiness); surface actionable worklists for case managers.

### Staffing Optimization
Match nursing and support staff levels to predicted patient acuity and census by unit and shift, minimizing overtime and agency nurse usage while maintaining safe staffing ratios.

---

## Data Sources & Ontology Mapping

| Ontology Entity | Source System | Key Fields |
|----------------|--------------|------------|
| Bed Census | HIS / EHR | Unit, Bed, Patient, Admission Date, Expected Discharge, Status (occupied/clean/dirty) |
| OR Schedule | HIS Surgical Scheduling | Case ID, Surgeon, Procedure, Scheduled Start, Estimated Duration, Room, Status |
| ED Arrivals | EHR ED Module | Arrival Time, Acuity (ESI), Chief Complaint, Disposition (admit/discharge), Boarding Time |
| Patient Acuity | EHR Nursing | Patient, Unit, Acuity Score, Nursing Hours Required, Isolation Status |
| Staffing | HIS / HR | Unit, Shift, Staff Type, Scheduled Hours, Actual Hours, Agency Flag, Overtime |

---

## AI Workflow

1. **Census Forecasting** — Predict 24/48/72-hour census by unit: scheduled admissions + predicted ED admissions (time-series model on historical ED volumes, day-of-week, season, weather) − predicted discharges (LOS model per patient)
2. **LOS Prediction** — At admission, predict expected LOS based on diagnosis, acuity, age, comorbidities, and surgical status; update daily as clinical trajectory unfolds
3. **Discharge Barrier Detection** — For each inpatient, identify pending items blocking discharge: outstanding lab results, consult completion, post-acute bed search, transportation, medication reconciliation, patient education
4. **OR Duration Prediction** — Predict actual case duration per procedure × surgeon using historical case logs; account for patient complexity factors (BMI, comorbidities, revision vs. primary)
5. **OR Schedule Optimization** — Sequence cases within blocks to minimize turnover waste; identify gaps for add-on cases; flag blocks with consistent underutilization for reallocation
6. **Staffing Model** — Combine predicted census and acuity to calculate required nursing hours by unit and shift; compare against scheduled staff; recommend adjustments (float, overtime, agency)
7. **Output** — Bed management dashboard for house supervisors; OR utilization dashboard for surgical services; discharge worklists for case managers; staffing recommendations for nurse managers

---

## Dashboard & Alerts

### Key Metrics

| KPI | Description | Target |
|-----|-------------|--------|
| **Bed Occupancy Rate** | % of staffed beds occupied | 82-88% (optimized range) |
| **ED Boarding Time** | Average hours ED admission patients wait for inpatient bed | < 2 hours |
| **OR Utilization** | % of scheduled OR block time used for surgery (wheels-in to wheels-out) | > 80% |
| **Average LOS** | Mean length of stay in days | Meet or beat CMS geometric mean by DRG |
| **Discharge Before Noon** | % of discharges completed before 12:00 PM | > 40% |
| **Agency Nurse %** | % of nursing hours filled by agency/travel nurses | < 5% |

### Alert Rules

| Alert | Trigger | Severity | Action |
|-------|---------|----------|--------|
| Capacity crisis | Predicted occupancy >95% within 24 hours with <5 predicted discharges | Critical | Activate surge protocol; expedite discharges; consider ED diversion |
| ED boarding breach | Any ED patient boarding >4 hours for an inpatient bed | High | Escalate to house supervisor; identify next available bed; consider hallway bed |
| OR schedule delay | Current case running >45 min over predicted duration, impacting next case | High | Notify next surgical team; assess delay cascade and rescheduling options |
| LOS outlier | Patient exceeds predicted LOS by >2 days with no documented clinical reason | Medium | Alert case manager; review discharge barriers |
| Staffing gap | Predicted acuity-based staffing need exceeds scheduled staff by >15% for upcoming shift | Medium | Notify nurse manager; initiate float/overtime/agency request |

---

## ROI Model

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| ED boarding time | 5.2 hours average | 1.8 hours average | **65% reduction → better patient experience + ED throughput** |
| OR utilization | 68% | 82% | **14 pt improvement → $5.2M additional surgical revenue** (from add-on cases) |
| Average LOS | 4.8 days | 4.2 days | **0.6-day reduction → 1,800 bed-days freed annually** |
| Agency nurse spend | $4.8M / year | $2.8M / year | **$2M savings from better staffing prediction** |
| Discharge before noon | 22% | 42% | **91% improvement → better bed turnover** |

!!! success "Estimated Annual ROI"
    **$8M - $14M** annually from surgical revenue capture, LOS reduction, agency cost avoidance, and throughput improvement — across a mid-size health system with 300+ beds and 15 ORs.

---

## Implementation Notes

- Real-time ADT feeds from HIS/EHR are essential; bed status updates must be reflected within minutes, not hours
- OR duration prediction requires 24+ months of surgical case log data with actual start/stop times per case
- LOS prediction models perform best when trained per DRG/service line with clinical features (not just administrative data)
- Discharge prediction depends on case management documentation of discharge barriers; workflow compliance is critical
- Staffing optimization must respect collective bargaining agreements, minimum staffing ratios (state-mandated where applicable), and employee scheduling preferences

---

[← Back to Catalogue](index.md) | [Previous: Revenue Cycle](revenue-cycle.md) | [Next: Population Health →](population-health.md)
