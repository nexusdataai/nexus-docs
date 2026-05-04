# Business Requirements -- NexusAI Data-AI Platform

**Status:** Approved
**Classification:** Internal

---

## 1. Problem statement

Enterprises invest heavily in AI but **70-80% of projects never reach production**, blocked by siloed data, missing governance, and the absence of a unified operating layer between models and systems of record.

- Knowledge workers spend **40-60%** of their time on workflows that could be automated.
- Cross-system decision-making takes days because data is fragmented across ERP / CRM / data lakes / SaaS.
- Point AI tools proliferate without shared context, governance, or coordination.
- 85% of CIOs rank AI operationalisation as a top-3 strategic priority; 3-5x project success uplift comes from a unified data layer.

**NexusAI** addresses this with a single Data-AI Platform that connects existing systems, builds semantic context, and runs autonomous agents under policy.

---

## 2. Functional requirements

### 2.1 Data Plane -- Enterprise data integration

- **FR-DP-001** Connect to any enterprise system via **FDW** (live federated reads), **ETL** (batch ingest), or **CDC** (streaming change capture).
- **FR-DP-002** Ship a **Virtual Data Layer (VDL)** that exposes every connected entity through a unified API regardless of hydration mode.
- **FR-DP-003** Provide an **Entity Explorer** for inspecting schemas, fields, relationships, and live row data per entity.
- **FR-DP-004** Provide a **Mapping Rules** editor that maps raw source fields onto ontology objects with previewable execution.
- **FR-DP-005** Ship a **Connectors Catalogue** with first-party connectors (Salesforce, Office 365, Oracle ERP, SAP S/4HANA, Google Drive, Webex, Knowledge Base, Langflow, generic External Systems writeback).

### 2.2 Control Plane -- Semantic understanding

- **FR-CP-001** Build and maintain an **Ontology** (entity schemas, policies, workflows, integrations) authored as YAML.
- **FR-CP-002** Materialise the ontology into a **Knowledge Graph** on Apache AGE (PostgreSQL extension) with typed nodes and edges.
- **FR-CP-003** Index every ontology document into a **vector embedding store** on pgvector for semantic retrieval.
- **FR-CP-004** Run a **Knowledge Pipeline** that extracts schema, mappings, policies, workflows, and integrations from the live platform on demand or schedule.
- **FR-CP-005** Provide a **Policy Builder** with risk levels, source-of-truth bindings, constraints, approval matrices, and restrictions.
- **FR-CP-006** Provide a **Workflows** editor for multi-system process flows defined in YAML.
- **FR-CP-007** Provide an **Integration Rules** editor for field-level sync mappings (bidirectional, configurable frequency, failure handling).

### 2.3 Reasoning Plane -- ReAct agent runtime

- **FR-RP-001** Run a ReAct (Reason + Act) agent loop powered by configurable LLMs (OpenAI, Anthropic).
- **FR-RP-002** Expose every action as a **registered tool** with typed inputs / outputs and read-only / write-capable classification.
- **FR-RP-003** Enforce **policy guardrails** before any tool execution (approval thresholds, close windows, field-level access, dry-run mode, max step limits).
- **FR-RP-004** Provide an **AI Copilot** chat interface that returns inspectable agent steps with token counts, traces, and source citations.
- **FR-RP-005** Provide a **Planning Playground** for hybrid-RAG validation with a Retrieval Quality Score across Object/Schema, Policy, Cross-System Graph, Version Awareness, Workflow, and Integration dimensions.

### 2.4 Console -- AI Analytics

- **FR-AN-001** Author multi-panel **Dashboards** powered by the VDL, classified by intent (Outcomes / Predict / Diagnose / Monitor).
- **FR-AN-002** Author reusable **Views** -- single-purpose analytical surfaces -- composable into Solution UIs via the four-views framework.
- **FR-AN-003** Bind Views to Solutions via **Solution Mapping** so each linked View becomes a left-menu item inside its Solution.
- **FR-AN-004** Provide a **Dashboard Builder** with 20 panel types across 7 categories (Stats, Charts, Tables, Timelines, Graphs, Other) and an **AI Query Builder** that turns natural-language prompts into structured queries against the VDL.

### 2.5 Console -- AI Automation

- **FR-AU-001** Author and run **Journeys** -- multi-step pipelines with persistent run history, success / failure metrics, and full audit trail.
- **FR-AU-002** Ship **Journey Templates** for common pipeline types (Call Processing, Semantic RAG indexing) and per-Solution operational journeys.
- **FR-AU-003** Provide an **AI Copilot Journey** planner that turns natural-language goals into draft journeys.
- **FR-AU-004** Provide a **Journey Builder** -- visual three-pane authoring (Tool Palette / canvas / Step Editor) with `AI Suggest`, `Validate`, `Save`, `Run` controls.
- **FR-AU-005** Support trigger types: **Manual**, **Schedule**, **Webhook**.
- **FR-AU-006** Provide a **Journey Studio** drill-down per journey with KPI tiles, processing-stage list, stage detail with run controls, and per-step `Logs (N)` drill-in.

### 2.6 Solutions -- Vertical app catalogues

- **FR-SO-001** Ship a one-page **Solutions Catalogue** filterable by vertical (Finance, Planning, Operations, Risk, Revenue, ESG) with priority, KPI targets, setup time, and source-entity chips per app.
- **FR-SO-002** Each Solution opens into a dedicated workspace with a left nav grouped into **Analytics** (Business Insights, Process Analytics, Workflow Actions, Reports), **Views** (auto-seeded four-views), and **Workspace** (Agent Builder, Tools Catalogue).
- **FR-SO-003** Ship 7 industry-aligned ontologies and Solution catalogues: Supply Chain, Finance & Banking, Telecommunications, Retail, Healthcare, Customer Operations, Revenue Operations.

### 2.7 Deployment & Operations

- **FR-OP-001** Deploy via the **Nexus Capability Operator** -- a Kubernetes operator that reconciles `NexusCapability` custom resources.
- **FR-OP-002** Support cloud (AWS EKS) and on-premise Kubernetes.
- **FR-OP-003** Bundle observability through CloudWatch / Prometheus-compatible metrics, end-to-end run audit trail, and DynamoDB-backed job state.
- **FR-OP-004** Bundle simulators (SFDC / CRM) for testing journeys against synthetic data before connecting live systems.

---

## 3. Non-functional requirements

| Area | Requirement |
|---|---|
| **Performance** | Knowledge Graph query < 2s; agent execution latency < 5s for standard workflows; dashboard render < 2s; supports up to 10 TB of customer data. |
| **Scalability** | 50-5,000 users per customer; horizontal auto-scaling; 99.9% uptime SLA. |
| **Security** | SOC 2 Type II; AES-256 at rest, TLS 1.2+ in transit; deploys in customer infrastructure (no data leaves perimeter); RBAC across every surface. |
| **Compliance** | GDPR, CCPA; per-vertical regulatory ontologies (HIPAA for Healthcare, SOX/Basel for Finance, etc.). |
| **Auditability** | Every agent action and every Journey step logged with full reasoning trace. |
| **Governance** | Policy engine (OPA-compatible) gates every write; human-in-the-loop for high-risk actions. |

---

## 4. Customer use cases

| # | Use case | Primary user | Value |
|---|---|---|---|
| 1 | **Enterprise Workflow Automation** -- agents handle repetitive cross-system workflows under policy | Operations Leader | 40-60% reduction in manual workflow effort |
| 2 | **Intelligent Decision Support** -- semantic graph + agents synthesise context across ERP / CRM / data lakes | Analyst, Executive | 50% faster decision cycles |
| 3 | **Operational Cost Optimisation** -- AI identifies inefficiencies, automates resource allocation | CFO, Ops Director | 30-40% ops cost reduction |
| 4 | **Enterprise Data Unification** -- siloed systems become queryable through one API via the VDL | CIO, Data Architecture | Single source of truth |
| 5 | **Vertical Solution Adoption** -- pre-built apps ship with ontology, KPIs, journeys (e.g. Order-to-Cash Monitor) | Business Capability Owner | 10x faster time from concept to production |

For a representative end-to-end app, see the **Order-to-Cash Monitor** drill-down in [Platform Architecture > Solutions](../../platform-architecture.md#solutions).

---

## 5. Target customer profile

**Industry fit (priority order)**

1. Financial Services & Banking
2. Manufacturing & Supply Chain
3. Telecommunications
4. Healthcare & Life Sciences
5. Retail
6. Insurance

**Company profile**

- 500-50,000 employees, $50M-$5B+ revenue.
- Existing or willing to adopt Kubernetes.
- Existing ERP (SAP, Oracle), CRM (Salesforce, HubSpot), and data warehouse / data lake.
- Multiple enterprise systems with siloed data; failed AI pilots; manual operational processes.

**Buyer & technical decision-maker**

- Buyers: CIO, CTO, COO, VP Operations, VP Data & Analytics.
- Influencers: Business Capability Owners, Solution Architects, Enterprise Architects.

---

## 6. Success metrics

**Customer success**

- Workflow automation rate > 40%.
- Decision cycle reduction > 50% vs baseline.
- Ops cost reduction > 30% in year one.
- CSAT > 4.5 / 5; NPS > 60.
- Time to first value < 4 weeks.

**Platform**

- Uptime > 99.9%.
- Knowledge Graph query < 2s.
- Agent execution latency < 5s.
- Dashboard response < 2s.

**Business**

- Sales cycle < 60 days.
- Annual retention > 90%.
- Net revenue retention > 120%.
- 50%+ accounts add new Solutions within 12 months.

---

## 7. Competitive differentiation

| Competitor | Their pitch | NexusAI advantage |
|---|---|---|
| Point AI tools | Single use case | Unified operating layer across every system |
| Palantir / Dataiku | Analytics + heavy services | Operational AI with autonomous agents; open-source GPL core; deploys in customer infra |
| LangFlow / CrewAI | Developer SDK for agents | Production AI-Ops, policy guardrails, human-in-the-loop, registered-tool registry |
| Enterprise vendors | Multi-quarter implementations | Kubernetes-native; ships with 7 vertical Solution catalogues; customer-controlled |

**Defensibility:** hybrid Graph + Vector reasoning, compounded ontology moat per customer, AI-Ops at every layer, open-source flywheel.

---

## 8. Go-to-market

### 8.1 Value proposition

> "The intelligent AI operating layer for the enterprise: connect your systems, build semantic context, and deploy autonomous agents that reason and act -- in your infrastructure, under your governance."

### 8.2 Segments (priority order)

1. Financial Services -- credit risk, fraud detection, regulatory compliance, treasury.
2. Manufacturing & Supply Chain -- demand forecasting, inventory optimisation, order-to-cash, supplier risk.
3. Telecommunications -- customer 360, network performance, revenue assurance.
4. Healthcare -- patient 360, clinical decision support, revenue cycle.
5. Retail -- personalisation, price optimisation, store operations.
6. Insurance -- claims, underwriting, fraud.

### 8.3 Sales motion

| Stage | Activity | Outcome |
|---|---|---|
| **Discovery** (W1-2) | Identify pain points; qualify (siloed data, failed AI pilots, manual ops, $200K+ software budget). | Qualified opportunity |
| **Self-evaluation** (W3-4) | Customer deploys via the K8s Operator on their cluster; uses Simulators to validate; runs the AI Copilot against their Knowledge Graph. | Hands-on validation |
| **POC** (W5-8) | Customer connects one or two production data sources; activates one Solution app; measures KPIs vs baseline. | Quantified ROI |
| **Close** (W9-12) | Present customer-specific ROI; sign Enterprise Support contract. | $300K ACV booking |
| **Expand** (M6-12) | Add Solutions from the catalogue; expand to additional departments. | 50%+ account expansion |

### 8.4 Pricing

- **AI Stack & Solution Catalogues** -- Open-source GPL. Free.
- **Enterprise Support** -- $300K / year (security updates, AI-Ops tooling, dedicated FDE + PM, 5,000 FP change-request capacity, SLA support).
- **Onboarding** -- 10% upfront, 25% spread across three quarters.

### 8.5 Per-customer economics

| Metric | Value |
|---|---|
| ACV | $300K |
| CAC | $30K |
| LTV (3-year) | $900K |
| LTV:CAC | 30:1 |
| Gross margin | 85% |

---

## 9. Risks

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Competitors copy model | Medium | High | Compounded ontology moat; feature velocity; open-source community |
| Data privacy concerns | High | Medium | SOC 2 Type II; GDPR; data stays in customer infrastructure |
| AI accuracy / hallucination | High | Low | Policy guardrails; human-in-the-loop; simulation; AI-Ops at every layer |
| Integration complexity | Medium | Medium | Pre-built connectors; FDW / ETL / CDC; per-vertical Solutions ship with mappings |
| Enterprise sales-cycle length | Medium | Medium | Self-evaluation via simulators; published ROI playbooks |

---

## 10. Year-one and year-three goals

| Goal | Year 1 | Year 3 |
|---|---|---|
| Customers | 75 | 575 |
| ARR | $22.5M | $172M |
| Annual retention | 90% | 92% |
| Avg ops cost reduction (documented) | 30%+ | 40%+ |
| CSAT | 4.5 / 5 | 4.6 / 5 |
| NPS | 50+ | 60+ |

---

## References

- [Executive Summary](executive-summary.md)
- [Business Overview](business-overview.md)
- [AI Stack](../ai-stack.md)
- [Platform Architecture](../../platform-architecture.md)
- [Technical Solution Architecture](../../technical/solution-architecture.md)
- [Kubernetes Operator](../../operational/kubernetes-operator/index.md)
