---
hide:
  - toc
---

# Functional Specifications

The functional surface of the NexusAI Data-AI Platform is documented as a screen-by-screen tour in [Platform Architecture](../platform-architecture.md) and as a structured business / functional / non-functional requirements catalogue in [Business Requirements](../business/source/business-requirements.md).

## Where to find each kind of spec

| What you're looking for | Page |
|---|---|
| End-to-end product surface (every screen in every Plane and Solution app) | [Platform Architecture](../platform-architecture.md) |
| Functional + non-functional requirements organised by Plane / Console / Solutions / Operations | [Business Requirements](../business/source/business-requirements.md) |
| Per-Plane functional drill-downs | [Data Plane](../planes/data-plane.md), [Control Plane](../planes/control-plane.md), [Reasoning Plane](../planes/reasoning-plane.md) |
| Per-Console drill-downs (Catalogue, AI Analytics, AI Automation) | [Console](../console/solutions-catalogue.md) |
| Per-Solution app shell (Business Insights, Process Analytics, Workflow Actions, Reports, Views, Workspace) | [Solutions Catalogue](../console/solutions-catalogue.md) (Order-to-Cash example) |
| Reference architecture and data flow | [AI Operating System](../ai-os/architecture.md) and [Total System Architecture](../ai-os/Total-system-architecture.md) |
| Production code that realises each requirement | [Implementation Guide](../ai-os/implementation-guide.md) |

## Functional areas at a glance

- **Data Plane** -- VDL, hydration via FDW / ETL / CDC, Entity Explorer, Mapping Rules, Data Pipelines, Connectors. See [Data Plane](../planes/data-plane.md).
- **Control Plane** -- ontology bundle, Knowledge Pipeline, Knowledge Index, Knowledge Graph, Policy Builder, Workflows, Integration Rules. See [Control Plane](../planes/control-plane.md).
- **Reasoning Plane** -- AI Copilot, Planning Playground, ReAct Tools, Tool Builder, the agent loop with policy gating. See [Reasoning Plane](../planes/reasoning-plane.md).
- **AI Analytics** -- Dashboards, Views, Solution Mapping, Dashboard Builder with the AI Query Builder. See [AI Analytics](../console/ai-analytics.md).
- **AI Automation** -- Journeys, AI Copilot Journey, Journey Builder, Journey Studio. See [AI Automation](../console/ai-automation.md).
- **Solutions** -- Catalogue, per-Solution app shell (Analytics + Views + Workspace + Tools Catalogue). See [Solutions Catalogue](../console/solutions-catalogue.md).

## Non-functional shape

| Area | Target |
|---|---|
| Performance | Knowledge Graph query < 2s; agent latency < 5s; dashboard render < 2s; up to 10 TB customer data |
| Scalability | 50-5,000 users per customer; horizontal auto-scaling; 99.9% uptime SLA |
| Security | SOC 2 Type II; AES-256 at rest, TLS 1.2+ in transit; deploys in customer infrastructure |
| Compliance | GDPR, CCPA; per-vertical regulatory ontologies (HIPAA, SOX, Basel) |
| Auditability | Every agent step + journey step logged with full reasoning trace |
| Governance | Policy engine (OPA-compatible) gates every write; human-in-the-loop on high-risk actions |

For the full functional + non-functional requirements catalogue, see [Business Requirements](../business/source/business-requirements.md).
