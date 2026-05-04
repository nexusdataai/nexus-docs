---
hide:
  - toc
---

# Project Scope

Scope, releases, and roadmap for the **NexusAI Data-AI Platform**.

## In this section

- [Release notes v0.1.0](releases/v0.1.0.md) -- first release of the Data-AI Platform after the rebrand from the legacy CallSense Toolkit.

## Current version

**v0.1.0** -- Data-AI Platform GA. Three-plane architecture (Data / Control / Reasoning), Console (AI Analytics + AI Automation), 7 vertical Solution catalogues, Kubernetes-native deployment via the Nexus Capability Operator.

## Repositories

| Repo | Purpose |
|---|---|
| `nexus-backend` | FastAPI services, MCP gateway, FDW + Control Plane + Reasoning Plane code |
| `nexus-ui` | React SPA -- Console, Solution apps, AI Copilot, Workspace |
| `nexus-deployer` | Helm + Nexus Capability Operator (`NexusCapability` CRD) |
| `nexus-docs` | This documentation site (mkdocs-material) |

## In scope (v0.1.0)

- Data Plane -- Virtual Data Layer with FDW + ETL + CDC hydration; Mapping Rules; Connectors catalogue.
- Control Plane -- Ontology + Knowledge Graph (Apache AGE) + vector index (pgvector); Knowledge Pipeline; Policy / Workflow / Integration editors.
- Reasoning Plane -- ReAct agent loop with policy gating; AI Copilot; Planning Playground; registered Tool Registry.
- AI Analytics -- Dashboards, Views, Solution Mapping, Dashboard Builder with the AI Query Builder.
- AI Automation -- Journeys, AI Copilot Journey, Journey Builder, Journey Studio.
- 7 vertical Solution catalogues -- Supply Chain, Finance & Banking, Telco, Retail, Healthcare, Customer Operations, Revenue Operations.
- Kubernetes-native deployment via the [Nexus Capability Operator](../operational/kubernetes-operator/index.md).
- Cognito SSO with role-based access; SOC 2 Type II posture; GDPR + CCPA support.
- SFDC simulator for offline development and testing.

## Roadmap (post-v0.1.0)

- **CDC Path** -- Debezium / Kafka pipeline (currently planned in [Implementation Guide](../ai-os/implementation-guide.md)).
- **ETL Path engine** -- Spark / Airflow native batch runtime.
- **Apache AGE rollout** -- replace the planned Graph DB stub with the production AGE deployment.
- **Tool Builder** -- the Reasoning Plane's Tool Builder console (currently `coming soon`).
- **Per-Solution app drill-downs** -- documentation and screenshots for additional Solutions beyond the canonical Order-to-Cash Monitor example.
- **Solution-tool wiring** -- the `Try Tool` button on app-curated Tools Catalogue cards is currently a no-op; wire to journey draft / direct invocation.

## Migration

Customers coming from the legacy **CallSense Toolkit** product (Webex CC capture, call processing pipeline, Toolkit Deployer wizard) -- see [Migration from CallSense Toolkit](../migration/from-callsense-toolkit.md) for where the retired surfaces now live.

## Related references

- [Platform Architecture](../platform-architecture.md) -- end-to-end product surface.
- [Business Executive Summary](../business/source/executive-summary.md) -- positioning, market opportunity, commercial model.
- [Business Requirements](../business/source/business-requirements.md) -- full functional + non-functional requirements catalogue.
