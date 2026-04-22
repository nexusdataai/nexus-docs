# Workflows

10 TMF/eTOM-aligned AI workflows that power the telco applications. Each workflow is defined in `enterprise-knowledge/workflows/` as a YAML file with trigger conditions, ordered steps, and entity/policy dependencies.

---

## Workflow Summary

| # | Workflow | TMF/eTOM | Trigger | Primary App |
|---|---------|----------|---------|-------------|
| 1 | [Subscriber 360 & Churn Prediction](#1-subscriber-360--churn-prediction) | TMF629 / Customer Relations | Monthly or usage collapse >50% | Customer 360 |
| 2 | [Network Anomaly Detection & RCA](#2-network-anomaly-detection--rca) | TMF642 / Assurance | Real-time alarm or performance counter deviation | Network Performance |
| 3 | [Revenue Reconciliation & Fraud Detection](#3-revenue-reconciliation--fraud-detection) | TMF678 / Billing & Revenue | Daily or CDR volume drop >10% | Revenue Assurance |
| 4 | [Customer Experience & pNPS](#4-customer-experience--pnps) | TMF629 / Customer Relations | Qualifying experience failure or monthly batch | Customer Experience |
| 5 | [Network Capacity Forecasting](#5-network-capacity-forecasting) | TMF639 / Infrastructure Lifecycle | Monthly or congestion threshold approach | Network Capacity |
| 6 | [Dynamic Pricing & Offer Engine](#6-dynamic-pricing--offer-engine) | TMF622 / Product Lifecycle | Real-time subscriber event | Dynamic Pricing |
| 7 | [Field Dispatch & Predictive Maintenance](#7-field-dispatch--predictive-maintenance) | TMF621 / Operations Support | New work order or equipment health score <30 | Field Operations |
| 8 | [Spectrum & QoS Compliance](#8-spectrum--qos-compliance) | TMF639 / Regulatory | Filing deadline or spectrum parameter deviation | Regulatory Compliance |
| 9 | [Campaign & Retention Orchestration](#9-campaign--retention-orchestration) | TMF629 / Customer Relations | Campaign launch or churn risk threshold exceeded | Customer 360, Dynamic Pricing |
| 10 | [SLA Monitoring & Breach Prevention](#10-sla-monitoring--breach-prevention) | TMF638 / Assurance | Continuous or SLA metric approaching 80% of threshold | Network Performance, Customer Experience |

---

## 1. Subscriber 360 & Churn Prediction

**ID:** `WORKFLOW_SUBSCRIBER_CHURN_V1_0` | **TMF629 / Customer Relations** | **File:** `subscriber-churn.yaml`

**Trigger:** Monthly (1st business day) OR subscriber usage collapse >50% vs prior 30-day average

| Step | System | Action |
|------|--------|--------|
| 1. Entity Resolution | Internal | Match subscriber identity across BSS, CRM, and CDR systems into single golden record |
| 2. Household Discovery | Internal | Graph analysis: shared accounts, family plans, shared addresses → build Household structures |
| 3. Profile Assembly | Internal | Aggregate: all product holdings, usage patterns, billing history, interactions, trouble tickets, network experience |
| 4. Churn Feature Engineering | Internal | Extract features: usage velocity, recharge frequency, data consumption trends, complaint rate, tenure, device age, plan fit |
| 5. Churn Scoring | Internal | Gradient-boosted model on historical disconnects; produce 30/60/90-day churn probability per subscriber |
| 6. Retention Matching | Internal | Map churn driver to optimal retention action (plan upgrade, discount, loyalty reward, network fix) |
| 7. Upsell Scoring | Internal | Multi-label classification: predict highest-propensity add-on products (data packs, streaming, roaming, device upgrade) |
| 8. Push to CRM | CRM | Create retention task on subscriber account; 24-hour SLA for high-value subscribers; push NBA to agent desktop |

**Dependencies:** Subscriber_Profile, Household, Service_Instance, Usage_Record, CDR, Billing_Account, Trouble_Ticket, Device_Inventory, Campaign, customer-lifecycle-policy

---

## 2. Network Anomaly Detection & RCA

**ID:** `WORKFLOW_NETWORK_ANOMALY_RCA_V1_0` | **TMF642 / Assurance** | **File:** `network-anomaly-rca.yaml`

**Trigger:** Real-time alarm from NMS OR performance counter deviation >3σ from baseline

| Step | System | Action |
|------|--------|--------|
| 1. Counter Ingestion | NMS | Ingest real-time performance counters: throughput, latency, packet loss, availability, utilization per cell/link/node |
| 2. Baseline Learning | Internal | Maintain rolling baseline per counter per element using time-of-day and day-of-week seasonality models |
| 3. Anomaly Detection | Internal | Score deviations using isolation forest + LSTM ensemble; output anomaly score (0-100) per element |
| 4. Alarm Correlation | Internal | Correlate anomalies across topology: group co-occurring alarms by physical/logical proximity and time window |
| 5. Root Cause Identification | Internal | Traverse topology graph from symptom alarms to probable root cause element; rank hypotheses by likelihood |
| 6. Customer Impact Scoring | Internal | Estimate affected subscriber count and revenue impact based on cell coverage and usage patterns |
| 7. Predictive Alerting | Internal | Flag elements with degrading trends likely to breach threshold within 4/8/24 hours; publish prioritized alert queue |

**Dependencies:** Network_Element, Cell_Site, Performance_Counter, Alarm, Topology_Link, Service_Instance, Subscriber_Profile, network-performance-policy

---

## 3. Revenue Reconciliation & Fraud Detection

**ID:** `WORKFLOW_REVENUE_RECONCILIATION_V1_0` | **TMF678 / Billing & Revenue** | **File:** `revenue-reconciliation.yaml`

**Trigger:** Daily (04:00 UTC) OR CDR volume drop >10% vs same day prior week

| Step | System | Action |
|------|--------|--------|
| 1. CDR Flow Monitoring | Mediation | Track CDR volumes at each pipeline stage: network switch → mediation → rating → billing; flag volume drops or delays |
| 2. Cross-System Reconciliation | Internal | Three-way match: network-generated CDRs vs mediation output vs rated/billed records; identify leakage points |
| 3. Leakage Root Cause | Internal | Classify leakage type: unrated CDRs, misrouted records, configuration errors, tap file gaps, unbilled services |
| 4. Subscription Fraud Scoring | Internal | Score accounts for subscription fraud indicators: rapid SIM activation, credit policy bypass, identity anomalies |
| 5. SIM Box Detection | Internal | Detect SIM box patterns: high call volume, uniform call duration, geographic concentration, IMEI sharing |
| 6. Margin Validation | Internal | Validate revenue vs cost per service type; flag negative-margin products and interconnect anomalies |

**Dependencies:** CDR, Billing_Account, Rating_Tariff, Interconnect_Agreement, Service_Instance, Subscriber_Profile, Mediation_Record, revenue-assurance-policy, fraud-management-policy

---

## 4. Customer Experience & pNPS

**ID:** `WORKFLOW_CUSTOMER_EXPERIENCE_PNPS_V1_0` | **TMF629 / Customer Relations** | **File:** `customer-experience-pnps.yaml`

**Trigger:** Qualifying experience failure (dropped call, data session failure, billing dispute) OR monthly batch (1st business day)

| Step | System | Action |
|------|--------|--------|
| 1. Journey Reconstruction | Internal | Stitch subscriber touchpoints across channels: network events, app sessions, IVR calls, store visits, digital interactions |
| 2. Experience Feature Engineering | Internal | Extract features: call drop rate, data throughput vs plan, bill shock frequency, resolution time, channel switches |
| 3. pNPS Modeling | Internal | Predict Net Promoter Score per subscriber using gradient-boosted model on experience features and survey responses |
| 4. Journey Pattern Mining | Internal | Cluster subscribers by journey patterns; identify failure sequences that most strongly predict detractor status |
| 5. Proactive Recovery Triggers | Internal | Auto-trigger recovery actions for predicted detractors: service credit, priority support routing, proactive outreach |
| 6. Complaint Theme Extraction | Internal | NLP topic modeling on complaint text, IVR transcripts, and social mentions; surface emerging issue themes |

**Dependencies:** Subscriber_Profile, Usage_Record, Trouble_Ticket, Interaction_Record, Survey_Response, CDR, Service_Instance, Network_Element, customer-experience-policy

---

## 5. Network Capacity Forecasting

**ID:** `WORKFLOW_CAPACITY_FORECASTING_V1_0` | **TMF639 / Infrastructure Lifecycle** | **File:** `capacity-forecasting.yaml`

**Trigger:** Monthly (1st business day) OR cell site utilization sustained >80% for 72 hours

| Step | System | Action |
|------|--------|--------|
| 1. Traffic Aggregation | Internal | Aggregate traffic volumes per cell site, sector, and technology layer (2G/3G/4G/5G) with time-of-day profiling |
| 2. Growth Factor Modeling | Internal | Model subscriber growth, device mix evolution, application traffic trends, and seasonal patterns per region |
| 3. Traffic Forecasting | Internal | Forecast traffic demand 6-24 months forward using ensemble (Prophet + gradient-boosted) per cell/sector |
| 4. Congestion Prediction | Internal | Identify cells predicted to exceed capacity within forecast horizon; rank by severity and subscriber impact |
| 5. RF Optimization Simulation | Internal | Simulate parameter changes (tilt, power, neighbor lists) to defer capacity investment on borderline cells |
| 6. Spectrum Refarming Analysis | Internal | Model impact of refarming spectrum between technology layers (e.g., 3G→4G/5G) on capacity and coverage |
| 7. CAPEX ROI Ranking | Internal | Rank capacity projects by: subscribers relieved × revenue impact ÷ investment cost; publish prioritized build plan |

**Dependencies:** Cell_Site, Performance_Counter, Subscriber_Profile, Spectrum_License, Network_Element, Coverage_Area, capacity-planning-policy, spectrum-policy

---

## 6. Dynamic Pricing & Offer Engine

**ID:** `WORKFLOW_DYNAMIC_PRICING_OFFERS_V1_0` | **TMF622 / Product Lifecycle** | **File:** `dynamic-pricing-offers.yaml`

**Trigger:** Real-time subscriber event (allowance exhaustion, roaming entry, contract expiry T-30 days, usage spike)

| Step | System | Action |
|------|--------|--------|
| 1. Usage Profiling | Internal | Build real-time usage profile: current allowance consumption, overage trajectory, time-of-day patterns |
| 2. Plan Fit Analysis | Internal | Score current plan fit vs actual usage; identify over-spend (upgrade candidate) and under-use (downgrade risk) |
| 3. Contextual Trigger Detection | Internal | Detect trigger context: roaming entry, data exhaustion, streaming event, competitive port-out request, contract window |
| 4. Offer Selection | Internal | Uplift model selects optimal offer from catalogue: data top-up, plan migration, bundle, loyalty reward, device trade-in |
| 5. Elasticity Estimation | Internal | Estimate price elasticity per subscriber segment; set discount level to maximize expected margin |
| 6. Bundle Optimization | Internal | Optimize multi-product bundle composition (voice + data + content + device) for target segment |
| 7. Competitive Response | Internal | Monitor competitor pricing signals; adjust offer positioning and flag market-driven pricing actions |

**Dependencies:** Subscriber_Profile, Usage_Record, Service_Instance, Rating_Tariff, Product_Catalogue, Campaign, Billing_Account, Device_Inventory, pricing-policy, product-lifecycle-policy

---

## 7. Field Dispatch & Predictive Maintenance

**ID:** `WORKFLOW_FIELD_DISPATCH_MAINTENANCE_V1_0` | **TMF621 / Operations Support** | **File:** `field-dispatch-maintenance.yaml`

**Trigger:** New work order created OR equipment health score drops below 30

| Step | System | Action |
|------|--------|--------|
| 1. Remote Diagnostics | NMS | Run automated remote tests on reported element; collect performance counters, alarm history, and configuration state |
| 2. Dispatch Optimization | Internal | Optimize technician assignment by skill match, geographic proximity, parts availability, and SLA urgency |
| 3. Pre-Visit Briefing | Internal | Assemble briefing: equipment history, alarm timeline, topology context, prior repair notes, required parts/tools |
| 4. Equipment Health Scoring | Internal | Score all network equipment (0-100) based on age, alarm frequency, environmental stress, MTBF, and repair history |
| 5. Predictive Maintenance | Internal | Forecast equipment failure probability within 30/60/90 days; flag assets with >70% failure probability for preemptive replacement |
| 6. Site Selection | Internal | Prioritize site visits by combining equipment health scores, customer impact, and maintenance cost optimization |

**Dependencies:** Network_Element, Cell_Site, Work_Order, Field_Technician, Spare_Parts_Inventory, Alarm, Performance_Counter, field-operations-policy, maintenance-policy

---

## 8. Spectrum & QoS Compliance

**ID:** `WORKFLOW_SPECTRUM_QOS_COMPLIANCE_V1_0` | **TMF639 / Regulatory** | **File:** `spectrum-qos-compliance.yaml`

**Trigger:** Regulatory filing deadline 10 business days away OR spectrum parameter deviation detected

| Step | System | Action |
|------|--------|--------|
| 1. Spectrum Parameter Collection | NMS | Collect transmission power, frequency utilization, guard band compliance, and emission levels per license band |
| 2. License Compliance Check | Internal | Validate measured parameters against Spectrum_License conditions; flag deviations and calculate compliance score |
| 3. QoS Metric Aggregation | Internal | Aggregate QoS metrics per regulatory definition: call setup success rate, drop rate, data throughput, coverage percentage |
| 4. Report Generation | Internal | Populate regulatory return templates with validated metrics; apply formatting per regulator requirements |
| 5. Privacy Compliance Scan | Internal | Scan subscriber data handling for GDPR/local privacy regulation compliance; flag anomalies in consent and retention |
| 6. Regulatory Change Monitoring | Internal | NLP-based monitoring of regulatory publications and consultation papers; extract changes and assess operational impact |
| 7. Interconnect Reconciliation | Internal | Reconcile interconnect traffic volumes and settlement amounts with partner operators; flag discrepancies |

**Dependencies:** Spectrum_License, Network_Element, Cell_Site, Performance_Counter, Interconnect_Agreement, Subscriber_Profile, Regulatory_Filing, regulatory-compliance-policy, privacy-policy

---

## 9. Campaign & Retention Orchestration

**ID:** `WORKFLOW_CAMPAIGN_RETENTION_V1_0` | **TMF629 / Customer Relations** | **File:** `campaign-retention.yaml`

**Trigger:** New campaign launch OR subscriber churn risk score exceeds 0.7 threshold

| Step | System | Action |
|------|--------|--------|
| 1. Audience Selection | Internal | Select target subscribers from churn scores, segmentation, and product propensity models; apply exclusion rules |
| 2. Channel Selection | Internal | Determine optimal channel per subscriber based on historical response rates: SMS, push notification, email, outbound call, app |
| 3. Offer Personalization | Internal | Personalize offer parameters (discount level, plan recommendation, content bundle) per subscriber profile and elasticity |
| 4. Campaign Execution | CRM | Distribute offers via selected channels; enforce frequency caps, quiet hours, and regulatory opt-out compliance |
| 5. Response Tracking | Internal | Track subscriber responses: acceptance, redemption, ignore, opt-out; calculate real-time conversion rates |
| 6. Attribution Analysis | Internal | Multi-touch attribution: measure incremental impact on churn reduction, ARPU lift, and customer lifetime value |
| 7. Model Feedback Loop | Internal | Feed campaign outcomes back to churn, propensity, and elasticity models for continuous retraining |

**Dependencies:** Subscriber_Profile, Campaign, Service_Instance, Usage_Record, Billing_Account, Product_Catalogue, Interaction_Record, customer-lifecycle-policy, pricing-policy

---

## 10. SLA Monitoring & Breach Prevention

**ID:** `WORKFLOW_SLA_MONITORING_V1_0` | **TMF638 / Assurance** | **File:** `sla-monitoring.yaml`

**Trigger:** Continuous monitoring OR SLA metric reaches 80% of contractual threshold

| Step | System | Action |
|------|--------|--------|
| 1. SLA Metric Collection | Internal | Collect SLA metrics per service and customer: availability, latency, throughput, MTTR, incident count against contractual targets |
| 2. Breach Probability Prediction | Internal | Predict probability of SLA breach within 1/4/24 hours using trend analysis and historical breach patterns |
| 3. Impact Assessment | Internal | Calculate financial exposure (penalty clauses), customer impact (subscriber count, revenue tier), and reputational risk |
| 4. Preemptive Action Recommendation | Internal | Recommend corrective actions: traffic rerouting, capacity boost, priority repair dispatch, resource reallocation |
| 5. Escalation | Internal | If breach probability >80%: escalate to service manager; >95%: escalate to operations director with action plan |
| 6. Post-Breach RCA | Internal | For confirmed breaches: automated root cause analysis linking SLA failure to network events, capacity, or process gaps |
| 7. Customer Communication | CRM | Generate proactive customer notification for impacted enterprise accounts; include remediation timeline and credit offer |

**Dependencies:** SLA_Contract, Service_Instance, Performance_Counter, Network_Element, Alarm, Work_Order, Subscriber_Profile, Billing_Account, sla-management-policy, customer-experience-policy

---

[← Back to Ontology Overview](index.md)
