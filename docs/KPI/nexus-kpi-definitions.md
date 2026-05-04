# NexusAI KPI Definitions

Standard KPIs the **NexusAI Data-AI Platform** measures and exposes. Two layers: **platform KPIs** (apply to every deployment regardless of vertical) and **Solution KPIs** (vertical-specific, shipped with each Solution in the catalogue).

For the platform's broader business framing, see [Business Requirements](../business/source/business-requirements.md).

---

## 1. Platform KPIs

### 1.1 Data Plane

| KPI | Definition | Where it surfaces |
|---|---|---|
| Data Sources connected | Number of enterprise systems wired to the platform via FDW / ETL / CDC | Data Plane > Data Sources tab |
| Total Entities | Virtual entities discovered across all sources (mapped + unmapped) | Data Plane > Virtual Data tab |
| Mapped Entities | Entities mapped to ontology objects | Data Plane > Virtual Data tab |
| Mapping Rules | Active rules mapping raw fields onto ontology objects | Data Plane > Mapping Rules tab |
| Active Pipelines | ETL pipelines currently running | Data Plane > Data Pipelines tab |
| Pipeline Success Rate | `successful runs / total runs` over the configured window | Data Plane > Data Pipelines tab |

### 1.2 Control Plane

| KPI | Definition | Where it surfaces |
|---|---|---|
| Graph Nodes | Entities materialised in the Apache AGE Knowledge Graph | Control Plane > Knowledge Pipeline tab |
| Graph Edges | Typed relationships in the Knowledge Graph (`triggers`, `syncs_to`, `depends_on`, `constrained_by`, `owned_by`) | Control Plane > Knowledge Pipeline tab |
| Embeddings | Vector embeddings indexed in pgvector | Control Plane > Knowledge Pipeline tab |
| Schemas | Ontology entity schemas loaded | Control Plane > Knowledge Pipeline tab |
| Policies | Active business-rule policies | Control Plane > Policy Builder tab |
| Workflows | Defined multi-system workflow templates | Control Plane > Workflows tab |
| Integrations | Configured integration / sync rules between systems | Control Plane > Integration Rules tab |
| Index Freshness | Time since the last successful Knowledge Pipeline run | Control Plane > Knowledge Pipeline tab |

### 1.3 Reasoning Plane

| KPI | Definition | Where it surfaces |
|---|---|---|
| Registered Tools | Total tools available to the ReAct agent (read-only + write-capable) | Reasoning Plane > ReAct Tools tab |
| Agent Sessions | Distinct AI Copilot sessions over the configured window | Reasoning Plane > AI Copilot tab |
| Avg Steps per Session | Mean ReAct iterations per session | Reasoning Plane internal metrics |
| Avg Tokens per Session | Mean LLM token consumption per session | Reasoning Plane internal metrics |
| Policy Violations Blocked | Count of tool calls blocked by the policy engine | Reasoning Plane internal metrics |
| Retrieval Quality Score | 0-6 score per retrieval bundle (Object/Schema, Policy, Workflow, Integration, Cross-System Graph, Version Awareness); production threshold 5+ | Reasoning Plane > Planning Playground |

### 1.4 AI Analytics

| KPI | Definition | Where it surfaces |
|---|---|---|
| Dashboards | Total dashboards in the workspace | AI Analytics > Dashboards tab |
| Views | Total reusable Views | AI Analytics > Views tab |
| Auto-seeded Views | Views auto-created via the four-views framework (`outcomes` / `predict` / `diagnose` / `monitor`) per Solution | AI Analytics > Views tab |
| Solutions Mapped | Solutions with at least one View bound | AI Analytics > Solution Mapping tab |
| AI Query Builder Generations | Count of AI-generated queries authored via the Dashboard Builder | AI Analytics internal metrics |

### 1.5 AI Automation

| KPI | Definition | Where it surfaces |
|---|---|---|
| Journeys | Total registered journeys | AI Automation > Journeys tab |
| Templates | Available `+ New … Journey` templates (one per pipeline type / Solution) | AI Automation > Journeys tab |
| Jobs (per journey) | Total job executions for the journey | Journey card |
| Done / Running / Failed | Per-journey job outcome counters | Journey card |
| Success Rate | `done / (done + failed)` per journey | Journey card |
| Avg Duration | Mean execution time per job | Journey card |
| Stage Steps | Per-journey ordered execution graph | Journey Studio |

### 1.6 Solutions Catalogue

| KPI | Definition | Where it surfaces |
|---|---|---|
| Solutions Available | Pre-built Solutions in the catalogue (across 7 verticals) | Solutions catalogue page |
| Solutions Activated | Solutions with mapped Views and active Journeys | Solutions catalogue page |
| Solution Setup Time | Estimated weeks to onboard the Solution per the catalogue card | Solutions catalogue card |
| Solution Entities | Ontology entities the Solution consumes | Solutions catalogue card |

### 1.7 Operations

| KPI | Definition | Where it surfaces |
|---|---|---|
| Pod Health | Backend / frontend / BSSMagic pod readiness | AI Ops > Health |
| FDW Connection Health | Live FDW probe status per source | AI Ops > Diagnostics |
| API Diagnostics | Per-endpoint health and latency | AI Ops > Diagnostics |
| Audit Volume | Audit events emitted per hour to DynamoDB | CloudWatch metrics |

---

## 2. Solution-specific KPIs (catalogue defaults)

Every Solution ships with target KPI badges visible on its catalogue card. These are platform-recommended targets; customers can override per deployment.

### 2.1 Supply Chain

| Solution | Headline KPI targets |
|---|---|
| Order-to-Cash Monitor | DSO < 35 days, Match Rate > 95%, Leakage < 0.5%, On-Time Payment > 88% |
| Demand Forecasting Engine | MAPE < 15%, Stockout Rate < 2%, Bias ± 3%, Promo Lift Accuracy ± 10% |
| Inventory Optimisation | Turns > 12x, Fill Rate > 97%, Expiry < 1% |
| Procurement & Spend Analytics | Maverick < 5%, STP Rate > 80%, Price Variance < 3% |
| Production & Quality Copilot | OEE > 85%, Yield > 98%, First Pass > 95% |
| Supply Chain Risk Radar | Risk Score < 30, OTD > 95%, Early Warning > 7 days |
| Customer 360 & Revenue Growth | Churn < 5%, Wallet Share > 60%, CLV +15% |
| ESG & Sustainability Tracker | Per-customer carbon / water / compliance targets (configured at onboarding) |

### 2.2 Finance & Banking

| Solution | Headline KPI targets |
|---|---|
| Customer 360 (banking) | Cross-sell rate, NPS, share of wallet |
| Credit Risk & Early Warning | PD calibration, expected vs realised loss |
| Fraud Detection & AML | Detection precision, suspicious-activity SLA, false-positive rate |
| Regulatory Compliance | Reporting on-time rate, breach count, audit pass rate |
| Treasury & Liquidity | LCR, NSFR, intraday liquidity coverage |
| Loan Lifecycle | Time to disburse, NPA rate, recovery rate |
| Revenue Optimisation | Pricing optimisation lift, fee leakage |
| Operational Risk | Loss-event count, near-miss reporting, control effectiveness |

### 2.3 Telecommunications

| Solution | Headline KPI targets |
|---|---|
| Customer 360 & Churn | Churn rate, NPS, ARPU |
| Network Performance | Availability %, drop-call rate, throughput |
| Revenue Assurance & Fraud | Leakage %, fraud loss, TT detect |
| Customer Experience | First-contact resolution, NPS by journey |
| Network Capacity Planning | Forecast accuracy, congestion index |
| Dynamic Pricing | Take-up rate, ARPU lift |
| Field Operations | First-time fix rate, MTTR |
| Regulatory Compliance | SLA / QoS compliance, spectrum compliance |

### 2.4 Retail / Healthcare / Customer Ops / Rev Ops

For the per-vertical catalogue and KPI definitions, see the vertical's index page:

- [Retail](../app-catalogue/retail/index.md)
- [Healthcare](../app-catalogue/healthcare/index.md)
- [Customer Operations](../app-catalogue/customer-ops/index.md)
- [Revenue Operations](../app-catalogue/rev-ops/index.md)

---

## 3. KPI authoring conventions

When adding a new Solution or extending an existing one, follow these conventions so KPIs render consistently in the Solution catalogue card and in the Solution app's Process Analytics tab.

| Convention | Detail |
|---|---|
| Direction | Targets are written as `Metric Op Target` (`DSO < 35 days`, `OEE > 85%`) so the Solution card can colour-code achieved vs missed. |
| Time window | Default rolling 30-day window unless the metric is naturally per-event (e.g. per order, per call, per loan). |
| Source-of-truth | KPIs are computed against the Virtual Data Layer; never against snapshot exports. |
| Audit | Every Workflow Action triggered by a KPI breach is logged to DynamoDB `control-plane-audit`. |
| Override | Customers can override targets per deployment via the Policy Builder. |

For the full functional + non-functional requirements catalogue, see [Business Requirements](../business/source/business-requirements.md).
