# Enterprise AI Solution FAQ

Frequently-asked questions about how the NexusAI Data-AI Platform packages, ships, and operates **Enterprise AI Solutions**.

## What is an Enterprise AI Solution?

An **Enterprise AI Solution** is a complete, vertical-aligned business application that runs on the NexusAI Data-AI Platform. Each Solution bundles the ontology, KPIs, dashboards, journeys, and tools needed to operate one slice of the business end-to-end.

**Examples** (from the catalogue): Order-to-Cash Monitor, Demand Forecasting Engine, Inventory Optimisation, Procurement & Spend Analytics, Production & Quality Copilot, Supply Chain Risk Radar, Customer 360 & Revenue Growth, ESG & Sustainability Tracker, Credit Risk & Early Warning, Fraud Detection & AML, Patient 360, Network Performance, etc.

For the full catalogue, see [Solutions Catalogue](../../console/solutions-catalogue.md).

## What does every Solution ship with?

Every Solution opens into the same three-group workspace shell, parameterised by its ontology entities, KPI targets, and journeys.

### Analytics

- **Business Insights** -- Solution home with KPI targets, capability cards, and an entity strip.
- **Process Analytics** -- live KPIs against the VDL with composition charts and drill-down tables.
- **Workflow Actions** -- counters and an action-log feed for every automated remediation the Solution has fired.
- **Reports** -- alert digest and severity counters.

### Views (four-views framework)

Auto-seeded Views that become the Solution's left navigation:

- **Outcomes** -- live KPIs and active alerts.
- **Predict** -- forward-looking forecasts.
- **Diagnose** -- cohort breakdown and dimension x metric heatmaps.
- **Act & Outcomes** -- action ledger and impact tracking.

### Workspace

- **Agent Builder** -- author Custom Tools (YAML), Journey Templates, Agent Profiles, Test Harness.
- **Tools Catalogue** -- app-curated tool registry grounded in the Solution's ontology entities (e.g. for O2C: *Order Match Verifier*, *Order Anomaly Scorer*, *AR Cash Flow Projector*, *O2C Alert Generator*, *Dunning Notice Composer*, *DSO Optimizer*).

For the canonical example, see [Solutions Catalogue > Order-to-Cash Monitor](../../console/solutions-catalogue.md#solution-app-example----order-to-cash-monitor).

## What's "the platform" underneath?

The platform is the AI Operating System: three planes plus a Console, all powered by ontology-driven semantic understanding of enterprise data.

- **Data Plane** -- hydrates a Virtual Data Layer from any enterprise system via FDW (live), ETL (batch), or CDC (streaming).
- **Control Plane** -- builds the Knowledge Graph (Apache AGE) and vector index (pgvector) over the platform's ontology bundle.
- **Reasoning Plane** -- ReAct agent loop with a registered tool registry, policy gating, and human-in-the-loop.
- **Console** -- AI Analytics (Dashboards, Views, Dashboard Builder) + AI Automation (Journeys, Journey Builder, Journey Studio).

A Solution is the curated face of all four for one specific business problem.

## How do Solutions compose with the Console?

- The Solution defines its **ontology entities** -- those become rows in the Data Plane VDL and nodes in the Control Plane Knowledge Graph.
- The Solution's **Views** are mapped via [AI Analytics > Solution Mapping](../../console/ai-analytics.md#solution-mapping) to become the Solution's left navigation.
- The Solution's **Journeys** run on the [AI Automation](../../console/ai-automation.md) runtime and surface in the Solution's Workflow Actions tab.
- The Solution's **Agent Builder** authors agents that use the Reasoning Plane's [registered tools](../../planes/reasoning-plane.md), augmented by app-curated tools.

Authoring a new Solution is mostly ontology + Views + Journeys + tool registration; the platform does the rest.

## How is the platform deployed?

The platform is Kubernetes-native: the **Nexus Capability Operator** reconciles `NexusCapability` custom resources on any EKS or compatible cluster. Deployment is the same for cloud or on-premise.

For details, see [Operations > Kubernetes Operator](../../operational/kubernetes-operator/index.md).

## What does the platform deploy?

- **Frontend pods** -- nginx + the React SPA (Console, Solution apps, AI Copilot, Workspace) + the docs site.
- **Backend pods** -- FastAPI + MCP HTTP Gateway + Control Plane services + Data Plane FDW services.
- **Database** -- PostgreSQL with Apache AGE (Knowledge Graph) + pgvector (embeddings) + Multicorn FDW.
- **AWS dependencies** (in the AWS reference deployment) -- EKS, ECR, S3, CloudWatch, Cognito, Secrets Manager, DynamoDB.
- **Identity** -- SSO via Cognito with role-based access at every Plane.

For the production code map, see [Implementation Guide](../../ai-os/implementation-guide.md).

## How is governance built in?

- **Policy engine** -- OPA-compatible; gates every write action with approval thresholds, close-window restrictions, field-level access, cross-system checks, dry-run mode, and max-step limits.
- **Audit trail** -- every agent step (intent, retrieved context, tool call, result, policy violation) is recorded in the audit store.
- **Human-in-the-loop** -- high-risk actions block on explicit approval before execution.
- **Hybrid retrieval guard** -- the Reasoning Plane never sees a retrieval bundle without both Knowledge Graph and vector results, so it can't ignore deterministic constraints.

## Why this architecture?

- **Standardisation** -- the same shell, the same governance, the same retrieval contract across every Solution, regardless of vertical.
- **Portability** -- Kubernetes-native; the same artefacts deploy to any cloud or on-premise cluster.
- **Composability** -- Solutions plug into the Planes / Console rather than being separate apps. Adding a new Solution is mostly authoring an ontology and a few Journeys.
- **Customer control** -- deploys in customer infrastructure; data never leaves the perimeter; open-source GPL core.

## Key takeaways

- An **Enterprise AI Solution** is a complete vertical app on the platform, not a separate product.
- Every Solution ships with the same three-group shell (Analytics + Views + Workspace), parameterised by its ontology and journeys.
- The Solution composes with the platform's Planes and Console; nothing is bolted on.
- Deployment is Kubernetes-native via the [Nexus Capability Operator](../../operational/kubernetes-operator/index.md).
- Governance (policy, audit, human-in-the-loop) is built into the platform, not added per Solution.

## Related references

- [Platform Architecture](../../platform-architecture.md)
- [Solutions Catalogue](../../console/solutions-catalogue.md)
- [AI Analytics](../../console/ai-analytics.md)
- [AI Automation](../../console/ai-automation.md)
- [AI Operating System](../../ai-os/architecture.md)
- [Implementation Guide](../../ai-os/implementation-guide.md)
