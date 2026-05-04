---
hide:
  - toc
---

# AI Operating System -- Architecture

The NexusAI Data-AI Platform is built as a layered AI Operating System: the **Data Plane** hydrates a Virtual Data Layer from any enterprise system, the **Control Plane** turns that data into semantic context, and the **Reasoning Plane** runs ReAct agents under policy. The Console (AI Analytics + AI Automation) and the Solutions catalogue sit on top.

For the full screen-by-screen tour, see [Platform Architecture](../platform-architecture.md). This page summarises the architectural shape and links into the deeper plane-specific docs.

## Reference layer stack

| Layer | Responsibility |
|---|---|
| **User Interface** | Chat, REST API, AI Copilot, Solution Apps. |
| **Identity & RBAC** | SSO (Cognito / OIDC), session management, role-based access across every surface. |
| **Intent + Risk Analyzer** | Classifies each query into `read_only` / `low_risk_write` / `high_risk_write` / `cross_system`; routes risk to the appropriate tool subset. |
| **Reasoning Plane (ReAct loop)** | LLM agent loop -- PLAN -> EXECUTE -> OBSERVE -> REPLAN -- with bounded steps and tool-only execution. |
| **Policy & Guardrail Core** | Pre-execution validation (approval thresholds, close windows, field-level access, cross-system checks, dry-run mode, max step limits, audit logging). |
| **Tool Abstraction Layer** | The LLM never calls raw APIs -- only registered, typed tools (`get_account`, `query_table`, `submit_credit_change`, ...). |
| **Control Plane** | Enterprise RAG (Knowledge Graph + Vector store), ontology bundle, semantic retrieval. |
| **Data Plane** | Virtual Data Layer hydrated via FDW (live), ETL (batch), CDC (streaming). |
| **Enterprise Source Systems** | ERP (SAP / Oracle), CRM (Salesforce), data lakes, legacy systems, files. |

## Plane drill-downs

| Plane | What it does | Drill-down |
|---|---|---|
| **Data Plane** | Hydrates the VDL via FDW / ETL / CDC; exposes a single query API regardless of source. | [Data Plane](../planes/data-plane.md) |
| **Control Plane** | Builds and maintains the Knowledge Graph + vector index; runs the Knowledge Pipeline that ingests schemas, policies, workflows, integrations. | [Control Plane](../planes/control-plane.md) |
| **Reasoning Plane** | Runs the ReAct loop with the registered tool registry, the policy engine, and the AI Copilot. | [Reasoning Plane](../planes/reasoning-plane.md) |

## Cross-plane principles

- **LLM plans, backend enforces.** The LLM never executes write actions directly; every action is a registered tool whose execution the policy engine gates.
- **Hybrid retrieval.** Every reasoning step queries both the Knowledge Graph (structural truth) and the vector store (semantic similarity).
- **Versioned context.** The Control Plane re-indexes on schema or policy change; agent context is always pinned to the current version.
- **Audit by default.** Every agent step, tool call, policy violation, and write operation is recorded in the audit store.

## Related references

- [Total System Architecture](Total-system-architecture.md) -- the unified data-flow diagram (Data Plane -> Control Plane -> Reasoning Plane -> Console).
- [Data Sources](data-sources.md) -- when to choose FDW vs ETL vs CDC for each source system.
- [Implementation Guide](implementation-guide.md) -- the production code paths (`nexus-backend`, `nexus-ui`, BSSMagic) that realise this architecture.
- [ReAct Layer](re-act-layer.md) -- how the agent loop reasons, plans, and acts.
- [Semantic RAG](semantic-rag.md) -- what the retrieval bundle must contain to enable safe orchestration.
