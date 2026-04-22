# Application-Object Mapping

Minimum required ontology objects per application, with relationship details and cross-application dependency analysis.

---

## App 1: Customer 360 & Churn

**TMF:** TMF629 | **Minimum Objects: 12**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Subscriber_Master` | BSS | Core entity — golden subscriber record | — |
| `Account_Hierarchy` | BSS | Account grouping for household and enterprise views | depends_on -> Subscriber_Master |
| `Contact` | CRM | Contact details and communication preferences | depends_on -> Subscriber_Master |
| `Plan_Product` | BSS | Current plan, features, and pricing tier | depends_on -> Subscriber_Master |
| `Product_Instance` | BSS | Active service instances (voice, data, VAS) | depends_on -> Subscriber_Master, Plan_Product |
| `CDR_Record` | CDR / Mediation | Usage patterns for behavioral analysis | depends_on -> Subscriber_Master |
| `Aggregated_Usage` | Internal | Daily/weekly usage summaries for trending | depends_on -> Subscriber_Master |
| `Service_Request` | CRM | Complaint and service request history | depends_on -> Subscriber_Master |
| `Interaction_Record` | Contact Center | Call, chat, email interaction history | depends_on -> Subscriber_Master |
| `NPS_Survey` | CRM | Net promoter score and satisfaction tracking | depends_on -> Subscriber_Master |
| `Campaign` | CRM | Campaign response and offer history | depends_on -> Subscriber_Master |
| `Churn_Event` | Internal | Churn classification, reason code, and timing | depends_on -> Subscriber_Master |

**Policies:** customer-retention-policy, data-privacy-consent-policy
**Workflows:** churn-prediction, customer-360-assembly
**Integrations:** bss-crm-sync, customer-interaction-feed

---

## App 2: Network Performance

**TMF:** TMF642 | **Minimum Objects: 11**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Network_Element` | OSS | Core entity — network equipment inventory | — |
| `Cell_Site` | OSS | Physical site with location and configuration | depends_on -> Network_Element |
| `Sector` | OSS | Per-cell sector with frequency and tilt config | depends_on -> Cell_Site |
| `Link` | OSS | Transport links between network elements | depends_on -> Network_Element |
| `Alarm` | OSS / Fault Mgmt | Active and historical fault alarms | depends_on -> Network_Element |
| `Fault_Ticket` | OSS | Fault investigation and resolution tracking | depends_on -> Alarm |
| `Correlation_Group` | Internal | Correlated alarm groups for root cause analysis | depends_on -> Alarm |
| `Performance_Counter` | OSS / PM | 15-min KPI counters (PRB, throughput, latency) | depends_on -> Cell_Site, Sector |
| `SLA_Metric` | Internal | Availability and MTTR SLA tracking per region | depends_on -> Network_Element |
| `KQI` | Internal | Key quality indicators derived from counters | depends_on -> Performance_Counter |
| `CDR_Record` | CDR / Mediation | Customer impact correlation for network faults | depends_on -> Cell_Site |

**Policies:** network-sla-policy, data-freshness-policy
**Workflows:** fault-resolution, alarm-correlation
**Integrations:** oss-alarm-perf-feed, cdr-mediation-feed

---

## App 3: Revenue Assurance & Fraud

**TMF:** TMF678 | **Minimum Objects: 11**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `CDR_Record` | CDR / Mediation | Raw usage records for reconciliation | — |
| `Data_Session` | CDR / Mediation | Data usage records for volume validation | depends_on -> CDR_Record |
| `Billing_Record` | BSS | Invoice and charge records | depends_on -> Subscriber_Master |
| `Payment` | BSS | Payment transactions and aging | depends_on -> Billing_Record |
| `Prepay_Balance` | BSS | Prepaid balance, topup, and charging events | depends_on -> Subscriber_Master |
| `Revenue_Leakage` | Internal | Detected leakage events with root cause | depends_on -> CDR_Record, Billing_Record |
| `Subscriber_Master` | BSS | Subscriber identity for fraud investigation | — |
| `Plan_Product` | BSS | Plan configuration for rating validation | depends_on -> Subscriber_Master |
| `Product_Instance` | BSS | Active services for entitlement verification | depends_on -> Subscriber_Master, Plan_Product |
| `Performance_Counter` | OSS / PM | Network counters for CDR-network reconciliation | depends_on -> Cell_Site |
| `Churn_Event` | Internal | Fraud-driven churn classification | depends_on -> Subscriber_Master |

**Policies:** revenue-assurance-policy, data-freshness-policy
**Workflows:** revenue-reconciliation, fraud-detection
**Integrations:** cdr-mediation-feed, bss-crm-sync

---

## App 4: Customer Experience

**TMF:** TMF629 | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Subscriber_Master` | BSS | Subscriber identity and segment | — |
| `Service_Request` | CRM | Complaint tracking and resolution | depends_on -> Subscriber_Master |
| `Interaction_Record` | Contact Center | Multi-channel interaction history with sentiment | depends_on -> Subscriber_Master |
| `NPS_Survey` | CRM | NPS scores and verbatim feedback | depends_on -> Subscriber_Master |
| `CDR_Record` | CDR / Mediation | Usage patterns for experience correlation | depends_on -> Subscriber_Master |
| `Performance_Counter` | OSS / PM | Network quality experienced by subscriber | depends_on -> Cell_Site |
| `KQI` | Internal | Customer-facing quality indicators | depends_on -> Performance_Counter |
| `Campaign` | CRM | Campaign effectiveness and response tracking | depends_on -> Subscriber_Master |
| `Aggregated_Usage` | Internal | Usage trends for experience scoring | depends_on -> Subscriber_Master |
| `Plan_Product` | BSS | Plan context for experience benchmarking | depends_on -> Subscriber_Master |

**Policies:** customer-retention-policy, network-sla-policy
**Workflows:** customer-experience-scoring, complaint-resolution
**Integrations:** customer-interaction-feed, bss-crm-sync

---

## App 5: Network Capacity

**TMF:** TMF639 | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Cell_Site` | OSS | Physical site for capacity planning | — |
| `Sector` | OSS | Sector-level capacity and frequency allocation | depends_on -> Cell_Site |
| `Performance_Counter` | OSS / PM | PRB utilization, throughput, congestion metrics | depends_on -> Cell_Site, Sector |
| `Spectrum_Utilization` | OSS | Current spectrum usage per band per cell | depends_on -> Cell_Site, Spectrum_License |
| `Spectrum_License` | Regulatory | Licensed spectrum bands and conditions | — |
| `CDR_Record` | CDR / Mediation | Traffic volume and demand patterns | depends_on -> Cell_Site |
| `Aggregated_Usage` | Internal | Aggregated traffic for forecasting | depends_on -> Subscriber_Master |
| `Subscriber_Master` | BSS | Subscriber density per cell for demand modeling | — |
| `Link` | OSS | Transport capacity between sites | depends_on -> Network_Element |
| `Site_Survey` | Field | Site feasibility and expansion options | depends_on -> Cell_Site |

**Policies:** network-capacity-policy, spectrum-regulatory-policy
**Workflows:** capacity-planning, spectrum-refarming
**Integrations:** oss-alarm-perf-feed, cdr-mediation-feed

---

## App 6: Dynamic Pricing

**TMF:** TMF622 | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Subscriber_Master` | BSS | Subscriber segment and CLV for pricing tiers | — |
| `Plan_Product` | BSS | Plan catalog, features, and current pricing | — |
| `Product_Instance` | BSS | Active service instances per subscriber | depends_on -> Subscriber_Master, Plan_Product |
| `Add_On` | BSS | Value-added service bundles and upsell options | depends_on -> Plan_Product |
| `CDR_Record` | CDR / Mediation | Usage elasticity and consumption patterns | depends_on -> Subscriber_Master |
| `Aggregated_Usage` | Internal | Usage trends for price sensitivity modeling | depends_on -> Subscriber_Master |
| `Campaign` | CRM | Promotion and campaign response data | depends_on -> Subscriber_Master |
| `Competitor_Plan` | External | Competitor pricing and feature benchmarks | — |
| `Churn_Event` | Internal | Price-driven churn for elasticity calibration | depends_on -> Subscriber_Master |
| `Billing_Record` | BSS | Revenue per plan for margin analysis | depends_on -> Subscriber_Master |

**Policies:** customer-retention-policy, revenue-assurance-policy
**Workflows:** dynamic-pricing-optimization, plan-launch-validation
**Integrations:** bss-crm-sync, external-regulatory-feed

---

## App 7: Field Operations

**TMF:** TMF621 | **Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Work_Order` | CMMS | Field work order lifecycle tracking | depends_on -> Cell_Site |
| `Technician` | Workforce Mgmt | Technician profile, skills, availability, GPS | — |
| `Equipment_Telemetry` | Field Systems | Battery, generator, HVAC, antenna telemetry | depends_on -> Cell_Site |
| `Site_Survey` | Field Systems | Site feasibility and condition assessment | depends_on -> Cell_Site |
| `Cell_Site` | OSS | Physical site context for field dispatch | — |
| `Network_Element` | OSS | Equipment inventory for maintenance planning | depends_on -> Cell_Site |
| `Alarm` | OSS / Fault Mgmt | Alarms triggering field dispatch | depends_on -> Network_Element |
| `Fault_Ticket` | OSS | Fault context for work order creation | depends_on -> Alarm |
| `Service_Request` | CRM | Customer-reported issues requiring field visit | depends_on -> Subscriber_Master |
| `Subscriber_Master` | BSS | Subscriber context for customer-facing field work | — |

**Policies:** field-operations-policy, network-sla-policy
**Workflows:** predictive-maintenance, field-dispatch-optimization
**Integrations:** field-telemetry-feed, oss-alarm-perf-feed

---

## App 8: Regulatory Compliance

**Minimum Objects: 10**

| Object | System | Role in App | Key Relationship |
|--------|--------|-------------|-----------------|
| `Spectrum_License` | Regulatory | Licensed spectrum bands, conditions, and obligations | — |
| `Spectrum_Utilization` | OSS | Actual spectrum usage for compliance monitoring | depends_on -> Spectrum_License, Cell_Site |
| `Interference_Event` | OSS | Detected interference events and resolution | depends_on -> Spectrum_License |
| `QoS_Report` | Internal | Regulatory QoS report generation and filing | depends_on -> Performance_Counter |
| `Performance_Counter` | OSS / PM | Network KPIs for QoS compliance reporting | depends_on -> Cell_Site |
| `Consent_Record` | CRM | Subscriber consent status for privacy compliance | depends_on -> Subscriber_Master |
| `Regulatory_Publication` | External | Regulatory changes and impact assessments | — |
| `Interconnect_Record` | BSS | Interconnect traffic and settlement records | — |
| `CDR_Record` | CDR / Mediation | CDR data for regulatory audit and QoS validation | depends_on -> Cell_Site |
| `Cell_Site` | OSS | Cell site coverage for license obligation tracking | — |

**Policies:** spectrum-regulatory-policy, data-privacy-consent-policy
**Workflows:** regulatory-reporting, spectrum-compliance-monitoring
**Integrations:** external-regulatory-feed, oss-alarm-perf-feed

---

## Cross-Application Dependency Matrix

Shows which entities are shared across applications (checkmark = required by that app):

| Entity | Cust 360 | Net Perf | Rev Assur | Cust Exp | Net Cap | Dyn Price | Field Ops | Reg Comp |
|--------|----------|----------|-----------|----------|---------|-----------|-----------|----------|
| **Subscriber_Master** | x | — | x | x | x | x | x | — |
| **CDR_Record** | x | x | x | x | x | x | — | x |
| **Cell_Site** | — | x | — | — | x | — | x | x |
| **Performance_Counter** | — | x | x | x | x | — | — | x |
| **Plan_Product** | x | — | x | x | — | x | — | — |
| **Alarm** | — | x | — | — | — | — | x | — |
| **Campaign** | x | — | — | x | — | x | — | — |
| **NPS_Survey** | x | — | — | x | — | — | — | — |
| **Churn_Event** | x | — | x | — | — | x | — | — |
| **Service_Request** | x | — | — | x | — | — | x | — |
| **Aggregated_Usage** | x | — | — | x | x | x | — | — |
| **Spectrum_License** | — | — | — | — | x | — | — | x |
| **Work_Order** | — | — | — | — | — | — | x | — |
| **Billing_Record** | — | — | x | — | — | x | — | — |
| **Network_Element** | — | x | — | — | — | — | x | — |
| **Fault_Ticket** | — | x | — | — | — | — | x | — |

---

## Entity Count per App

| Application | Min Objects | Workflows | Policies | Integrations |
|------------|-----------|-----------|----------|--------------|
| Customer 360 & Churn | 12 | 2 | 2 | 2 |
| Network Performance | 11 | 2 | 2 | 2 |
| Revenue Assurance & Fraud | 11 | 2 | 2 | 2 |
| Customer Experience | 10 | 2 | 2 | 2 |
| Network Capacity | 10 | 2 | 2 | 2 |
| Dynamic Pricing | 10 | 2 | 2 | 2 |
| Field Operations | 10 | 2 | 2 | 2 |
| Regulatory Compliance | 10 | 2 | 2 | 2 |

---

[← Back to Ontology Overview](index.md)
