---
hide:
  - toc
---

# Features & Capabilities

The platform's capabilities are documented end-to-end in [Platform Architecture](../platform-architecture.md). This page is the index to deeper conceptual and FAQ-style reading.

## In this section

| Page | What it covers |
|---|---|
| [Enterprise AI Capability FAQ](source/enterprise-ai-capability-faq.md) | What an Enterprise AI Solution is, what it ships with, how Solutions compose with the Planes and the Console |

## Headline capabilities

| Plane / Layer | What it brings |
|---|---|
| **Data Plane** | Virtual Data Layer hydrated via FDW / ETL / CDC; one query API across every connected enterprise system |
| **Control Plane** | Ontology + Knowledge Graph (Apache AGE) + vector embeddings (pgvector); Knowledge Pipeline that re-indexes on schema or policy change |
| **Reasoning Plane** | ReAct agent loop with policy-gated tool registry; AI Copilot; Planning Playground with Retrieval Quality Score |
| **AI Analytics** | Dashboards + Views (four-views framework); Solution Mapping; Dashboard Builder with the AI Query Builder |
| **AI Automation** | Journeys engine with templates per Solution; AI Copilot Journey planner; visual Journey Builder; per-journey Journey Studio |
| **Solutions** | 7 vertical-aligned app catalogues (Supply Chain, Finance & Banking, Telco, Retail, Healthcare, Customer Ops, Rev Ops) |
| **Operations** | Kubernetes-native via the Nexus Capability Operator (`NexusCapability` CRD); cloud or on-premise |

## Cross-cutting

- **AI-Ops at every layer** -- audit trail of every agent step and journey step; policy engine pre-execution validation; loop detection; field-level access; dry-run mode.
- **Hybrid retrieval** -- Knowledge Graph (structural truth) + vector store (semantic similarity); the agent never sees one without the other.
- **Open-source GPL core** -- enterprise support subscription; deploys in customer infrastructure; no data leaves the perimeter.

## Related references

- [Platform Architecture](../platform-architecture.md) -- screen-by-screen tour of every capability.
- [Business Requirements](../business/source/business-requirements.md) -- functional + non-functional requirements catalogue.
- [AI Operating System](../ai-os/architecture.md) -- conceptual reference for the layer stack.
- [Implementation Guide](../ai-os/implementation-guide.md) -- production code paths.
