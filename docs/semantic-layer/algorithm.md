# Reference Algorithm — Three-Plane AI Reasoning Architecture

ASCII rendering of [Algorithm.pdf](Algorithm.pdf). Top-to-bottom: User → Reasoning Plane → Control Plane → Data Plane → Source Systems. A feedback loop returns observations to the planner so the ReAct agent can replan.

For our concrete implementation of this reference see [Knowledge Indexing & Copilot Reasoning](knowledge-indexing-and-copilot-reasoning.md), [Reasoning Plane](../planes/reasoning-plane.md), [Control Plane](../planes/control-plane.md), and [Data Plane](../planes/data-plane.md).

---

## Full Architecture (single diagram)

```text
                       ┌─────────────────────────────────┐
                       │          User Interface         │
                       │     (Chat / API / Copilot)      │
                       └────────────────┬────────────────┘
                                        │
                                        ▼
                       ┌─────────────────────────────────┐
                       │       Identity & RBAC Layer     │
                       │      (SSO, OAuth, SCIM)         │
                       └────────────────┬────────────────┘
                                        │
                                        ▼
                       ┌─────────────────────────────────┐
                       │       Intent + Risk Analyzer    │
                       │   Classifies:                   │
                       │     read-only,                  │
                       │     low-risk write,             │
                       │     high-risk write,            │
                       │     cross-system                │
                       └────────────────┬────────────────┘
                                        │
                                        ▼
 ╔══════════════════════════════════════════════════════════════════════╗
 ║                  REASONING PLANE (LLM Agent Loop)                    ║
 ║                                                                      ║
 ║   ┌──────────────────────────────────────────────────────────────┐   ║
 ║   │      ReAct Planning Engine                                   │   ║
 ║   │      PLAN → EXECUTE → OBSERVE → REPLAN → EXECUTE → OBSERVE   │   ║
 ║   │                                                              │   ║
 ║   │   1. Receives user intent + risk classification              │   ║
 ║   │   2. Queries Enterprise RAG for context                      │   ║
 ║   │   3. Reasons about next action                               │   ║
 ║   │   4. Selects tool from Tool Abstraction Layer                │   ║
 ║   │   5. Policy Engine validates before execution                │   ║
 ║   │   6. Observes result, replans if needed                      │   ║
 ║   │   7. Loops until goal achieved or step limit reached         │   ║
 ║   └──────────────────────────────────────────────────────────────┘   ║
 ║                                                                      ║
 ║   ┌──────────────────────────────────────────────────────────────┐   ║
 ║   │   AI Applications (powered by this loop)                     │   ║
 ║   │     - Fraud AI Assistant                                     │   ║
 ║   │     - AML Investigator Copilot                               │   ║
 ║   │     - Risk Analytics Dashboard                               │   ║
 ║   │     - Enterprise System Orchestrator                         │   ║
 ║   └──────────────────────────────────────────────────────────────┘   ║
 ║                                                                      ║
 ║   ┌──────────────────────────────────────────────────────────────┐   ║
 ║   │   Policy & Guardrail Core (OPA / Custom Engine)              │   ║
 ║   │     - Approval thresholds       - Close windows              │   ║
 ║   │     - Field-level access        - Cross-system checks        │   ║
 ║   │     - Risk-based routing        - Dry-run mode               │   ║
 ║   │     - Max step limits           - Audit logging              │   ║
 ║   └──────────────────────────────────────────────────────────────┘   ║
 ║                                                                      ║
 ║   ┌──────────────────────────────────────────────────────────────┐   ║
 ║   │   Tool Abstraction Layer (Controlled APIs)                   │   ║
 ║   │     - get_account()        - propose_credit_change()         │   ║
 ║   │     - get_ar_balance()     - submit_gl_adjustment()          │   ║
 ║   │     - create_customer()    - trigger_workflow()              │   ║
 ║   │   LLM never calls raw APIs — only safe tools                 │   ║
 ║   └──────────────────────────────────────────────────────────────┘   ║
 ║                            │            ▲                            ║
 ║                            │            │ (feedback loop)            ║
 ║                            ▼            │                            ║
 ╚══════════════════════════════════════════════════════════════════════╝
                              │            │
                              ▼            │
 ╔══════════════════════════════════════════════════════════════════════╗
 ║              CONTROL PLANE (Semantic Intelligence)                   ║
 ║                                                                      ║
 ║   ┌──────────────────────────────────────────────────────────────┐   ║
 ║   │   Enterprise RAG Layer                                       │   ║
 ║   │   (Semantic Retrieval for LLM Context)                       │   ║
 ║   │                                                              │   ║
 ║   │   Retrieves from Vector DB + Graph DB to provide:            │   ║
 ║   │     - Schema & field definitions                             │   ║
 ║   │     - Business policies & approval rules                     │   ║
 ║   │     - Workflow dependencies & process rules                  │   ║
 ║   │     - API specs & integration mappings                       │   ║
 ║   │     - Cross-system dependency awareness                      │   ║
 ║   │                                                              │   ║
 ║   │   Answers questions like:                                    │   ║
 ║   │     "Which object stores credit risk?"                       │   ║
 ║   │     "What triggers approval workflow?"                       │   ║
 ║   │     "What fields are required for customer creation?"        │   ║
 ║   │     "What is the ERP sync dependency?"                       │   ║
 ║   │                                                              │   ║
 ║   │   This is semantic retrieval, not relational querying.       │   ║
 ║   └──────────────────────────────────────────────────────────────┘   ║
 ║                                                                      ║
 ║   ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐          ║
 ║   │ Graph Query   │  │ Vector Search │  │  ML Scoring     │          ║
 ║   │  + Reasoner   │  │  (Similarity) │  │     Engine      │          ║
 ║   └───────┬───────┘  └───────┬───────┘  └────────┬────────┘          ║
 ║           │                  │                   │                   ║
 ║   ┌───────┴──────────────────┴───────────────────┴─────────────┐    ║
 ║   │                     Intelligence Layer                      │    ║
 ║   │                                                             │    ║
 ║   │   ┌──────────────────────┐    ┌────────────────────────┐    │    ║
 ║   │   │  Graph DB            │    │   Vector DB            │    │    ║
 ║   │   │  (Ontology + RDF)    │    │   (Embeddings Store)   │    │    ║
 ║   │   │                      │    │                        │    │    ║
 ║   │   │  Structural          │    │   Semantic             │    │    ║
 ║   │   │  Knowledge:          │    │   Knowledge:           │    │    ║
 ║   │   │    - Accounts        │    │     - Schema           │    │    ║
 ║   │   │    - Transactions    │    │     - Policy           │    │    ║
 ║   │   │    - Customers       │    │     - Workflow         │    │    ║
 ║   │   │    - Risk Rules      │    │     - API spec         │    │    ║
 ║   │   │    - Relationships   │    │     - Process rule     │    │    ║
 ║   │   │    - Ontology        │    │     - Fraud case       │    │    ║
 ║   │   │                      │    │     - Customer         │    │    ║
 ║   │   └──────────────────────┘    └────────────────────────┘    │    ║
 ║   └─────────────────────────────────────────────────────────────┘    ║
 ║                              │                                       ║
 ╚══════════════════════════════╪═══════════════════════════════════════╝
                                │
                                ▼
 ╔══════════════════════════════════════════════════════════════════════╗
 ║              DATA PLANE (Ingestion & Transformation)                 ║
 ║                                                                      ║
 ║       CDC Path           ETL Path              FDW Path              ║
 ║          │                  │                     │                  ║
 ║          ▼                  ▼                     ▼                  ║
 ║   ┌─────────────┐   ┌─────────────────┐   ┌───────────────────┐      ║
 ║   │ RDF Stream  │   │  RDF Batch      │   │  FDW Wrapper      │      ║
 ║   │ Processor   │   │  Transformer    │   │  (Virtual Access) │      ║
 ║   │ (CDC →      │   │  (R2RML/Batch)  │   │                   │      ║
 ║   │  Ontology   │   │                 │   │  Postgres FDW /   │      ║
 ║   │  Mapper)    │   │                 │   │  Trino / Presto   │      ║
 ║   └──────┬──────┘   └────────┬────────┘   └─────────┬─────────┘      ║
 ║          │                   │                      │                ║
 ║          ▼                   ▼                      │                ║
 ║   ┌─────────────┐   ┌─────────────────┐             │                ║
 ║   │   Kafka     │   │   ETL Engine    │             │                ║
 ║   │             │   │   (Spark /      │             │                ║
 ║   │             │   │    Airflow /    │             │                ║
 ║   │             │   │    Custom)      │             │                ║
 ║   └──────┬──────┘   └────────┬────────┘             │                ║
 ║          │                   │                      │                ║
 ║          ▼                   │                      │                ║
 ║   ┌─────────────┐            │                      │                ║
 ║   │ CDC Engine  │            │                      │                ║
 ║   │ (Debezium)  │            │                      │                ║
 ║   └──────┬──────┘            │                      │                ║
 ║          │                   │                      │                ║
 ║          └─────────┬─────────┴──────────┬───────────┘                ║
 ║                    ▼                    ▼                            ║
 ║   ┌────────────────────────────────────────────────────────────┐     ║
 ║   │             Enterprise Source Systems                      │     ║
 ║   │                                                            │     ║
 ║   │  ┌──────────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐  │     ║
 ║   │  │ Core Banking │ │ ERP / GL │ │   CRM     │ │ Legacy   │  │     ║
 ║   │  │ (Temenos /   │ │ (SAP /   │ │(Salesforce│ │ Systems  │  │     ║
 ║   │  │  Finacle)    │ │  Oracle) │ │ / Custom) │ │ / Files) │  │     ║
 ║   │  └──────────────┘ └──────────┘ └───────────┘ └──────────┘  │     ║
 ║   └────────────────────────────────────────────────────────────┘     ║
 ║                                                                      ║
 ║   CDC: Real-time event streams from transaction-heavy systems        ║
 ║   ETL: Batch extraction for historical, analytical & master data     ║
 ║   FDW: Virtual access for low-volume / governance-restricted data    ║
 ╚══════════════════════════════════════════════════════════════════════╝
```

---

## Page 1 — Reasoning Plane (LLM Agent Loop)

The top-most plane: a user request enters through the UI, passes identity/RBAC, is classified by the Intent & Risk Analyzer, then drives the ReAct planning loop. The loop reaches into the Control Plane for context, picks a tool from the Tool Abstraction Layer, runs it through the Policy & Guardrail Core, observes the result, and replans until done.

```text
 ┌─────────────────────────────────┐
 │          User Interface         │
 │     (Chat / API / Copilot)      │
 └────────────────┬────────────────┘
                  │
                  ▼
 ┌─────────────────────────────────┐
 │       Identity & RBAC Layer     │
 │      (SSO, OAuth, SCIM)         │
 └────────────────┬────────────────┘
                  │
                  ▼
 ┌─────────────────────────────────┐
 │       Intent + Risk Analyzer    │
 │   Classifies:                   │
 │     read-only,                  │
 │     low-risk write, high-risk   │
 │     write, cross-system         │
 └────────────────┬────────────────┘
                  │
                  ▼
 ┌──────────────────────────────────────────────────────────────┐
 │            ReAct Planning Engine (LLM Agent Loop)            │
 │                                                              │
 │  PLAN → EXECUTE → OBSERVE → REPLAN → EXECUTE → OBSERVE       │
 │                                                              │
 │  1. Receives user intent + risk classification               │
 │  2. Queries Enterprise RAG for context ──────────┐           │
 │  3. Reasons about next action                    │           │
 │  4. Selects tool from Tool Abstraction Layer     │           │
 │  5. Policy Engine validates before execution     │           │
 │  6. Observes result, replans if needed           │           │
 │  7. Loops until goal achieved or step limit      │           │
 │                                                  │           │
 │  ┌─────────────────────────────────────────────┐ │           │
 │  │ AI Applications (powered by this loop)      │ │           │
 │  │   - Fraud AI Assistant                      │ │           │
 │  │   - AML Investigator Copilot                │ │           │
 │  │   - Risk Analytics Dashboard                │ │           │
 │  │   - Enterprise System Orchestrator          │ │           │
 │  └─────────────────────────────────────────────┘ │           │
 │                                                  │           │
 │  ┌─────────────────────────────────────────────┐ │           │
 │  │ Policy & Guardrail Core (OPA / Custom)      │ │           │
 │  │  - Approval thresholds  - Close windows     │ │           │
 │  │  - Field-level access   - Cross-system chk  │ │           │
 │  │  - Risk-based routing   - Dry-run mode      │ │           │
 │  │  - Max step limits      - Audit logging     │ │           │
 │  └─────────────────────────────────────────────┘ │           │
 │                                                  │           │
 │  ┌─────────────────────────────────────────────┐ │           │
 │  │ Tool Abstraction Layer (Controlled APIs)    │ │           │
 │  │  - get_account()      - propose_credit_*    │ │           │
 │  │  - get_ar_balance()   - submit_gl_adjust*   │ │           │
 │  │  - create_customer()  - trigger_workflow()  │ │           │
 │  │ LLM never calls raw APIs — only safe tools  │ │           │
 │  └─────────────────────────────────────────────┘ │           │
 └────────────────┬─────────────────────────────────┘           │
                  │                                              │
                  ▼                       (feedback loop)        │
                            ◄─────────────────────────────────────
```

**Maps to our codebase:**

| Reference block | Implementation |
|-----------------|----------------|
| Intent + Risk Analyzer | [`intent_analyzer.py`](../../../nexus-backend/src/services/control_plane/intent_analyzer.py) |
| ReAct Planning Engine | [`agent_executor.py`](../../../nexus-backend/src/services/control_plane/agent_executor.py) (`AgentExecutor.run`, max-10-step loop) |
| Policy & Guardrail Core | [`policy_engine.py`](../../../nexus-backend/src/services/control_plane/policy_engine.py) (every tool call goes through `PolicyEngine.validate`) |
| Audit logging | [`audit_logger.py`](../../../nexus-backend/src/services/control_plane/audit_logger.py) (DynamoDB session per request) |
| Tool Abstraction Layer | [`tool_registry.py`](../../../nexus-backend/src/services/control_plane/tool_registry.py); per-domain tool modules under [`tools/`](../../../nexus-backend/src/services/control_plane/tools/) |
| AI Applications | Solutions in [appRegistry.ts](../../../nexus-ui/src/config/appRegistry.ts) — O2C Monitor, Trade CPQ, Sourcing CPQ, Customer 360, Supply Chain Risk, etc. |
| UI / Chat | [`CopilotPage.tsx`](../../../nexus-ui/src/pages/CopilotPage.tsx), [`ReasoningPage.tsx`](../../../nexus-ui/src/pages/ai-stack/ReasoningPage.tsx) |
| Identity & RBAC | [`cognito_auth_middleware.py`](../../../nexus-backend/src/apis/cognito_auth_middleware.py), [`rbac_service.py`](../../../nexus-backend/src/services/rbac_service.py) |

---

## Page 2 — Control Plane (Semantic Intelligence & Reasoning)

The middle plane. The ReAct loop calls into the Enterprise RAG Layer here. Underneath the RAG layer are three retrieval styles (graph reasoning, vector similarity, ML scoring) and two stores (a Graph DB for structural knowledge and a Vector DB for semantic embeddings).

```text
 ┌─────────────────────────────────────────────────────────────────────┐
 │                          AI-CONTROL-PLANE                           │
 │              (Semantic Intelligence & Reasoning Layer)              │
 │                                                                     │
 │   ┌─────────────────────────────────────────────────────────────┐   │
 │   │              Enterprise RAG Layer                           │   │
 │   │           (Semantic Retrieval for LLM Context)              │   │
 │   │                                                             │   │
 │   │   Retrieves from Vector DB + Graph DB to provide:           │   │
 │   │     - Schema & field definitions                            │   │
 │   │     - Business policies & approval rules                    │   │
 │   │     - Workflow dependencies & process rules                 │   │
 │   │     - API specs & integration mappings                      │   │
 │   │     - Cross-system dependency awareness                     │   │
 │   │                                                             │   │
 │   │   Answers questions like:                                   │   │
 │   │     "Which object stores credit risk?"                      │   │
 │   │     "What triggers approval workflow?"                      │   │
 │   │     "What fields are required for customer creation?"       │   │
 │   │     "What is the ERP sync dependency?"                      │   │
 │   │                                                             │   │
 │   │   This is semantic retrieval, not relational querying.      │   │
 │   └─────────────────────────────────────────────────────────────┘   │
 │                                                                     │
 │   ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐          │
 │   │ Graph Query  │  │ Vector       │  │   ML Scoring     │          │
 │   │ + Reasoner   │  │ Search       │  │   Engine         │          │
 │   │              │  │ (Similarity) │  │                  │          │
 │   └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘          │
 │          │                 │                   │                    │
 │          └────────┬────────┴────────┬──────────┘                    │
 │                   ▼                 ▼                               │
 │   ┌─────────────────────────────────────────────────────────────┐   │
 │   │                    Intelligence Layer                       │   │
 │   │                                                             │   │
 │   │   ┌───────────────────────┐  ┌──────────────────────────┐   │   │
 │   │   │ Graph DB              │  │ Vector DB                │   │   │
 │   │   │ (Ontology + RDF)      │  │ (Embeddings Store)       │   │   │
 │   │   │                       │  │                          │   │   │
 │   │   │ Structural Knowledge: │  │ Semantic Knowledge:      │   │   │
 │   │   │   - Accounts          │  │   - Schema embeddings    │   │   │
 │   │   │   - Transactions      │  │   - Policy embeddings    │   │   │
 │   │   │   - Customers         │  │   - Workflow embeddings  │   │   │
 │   │   │   - Risk Rules        │  │   - API spec embeddings  │   │   │
 │   │   │   - Relationships     │  │   - Process rule embed.  │   │   │
 │   │   │   - Ontology          │  │   - Fraud case embed.    │   │   │
 │   │   │                       │  │   - Customer embeddings  │   │   │
 │   │   └───────────────────────┘  └──────────────────────────┘   │   │
 │   └─────────────────────────────────────────────────────────────┘   │
 └─────────────────────────────────────────────────────────────────────┘
```

**Maps to our codebase:**

| Reference block | Implementation |
|-----------------|----------------|
| Enterprise RAG Layer | [`rag_service.py`](../../../nexus-backend/src/services/control_plane/rag_service.py) — `hybrid_search(query)` merges vector top-K + graph expansion |
| Graph Query + Reasoner | [`graph_store.py`](../../../nexus-backend/src/services/control_plane/graph_store.py) — `GraphStore.expand_neighbors(onto_ids, hops=2)` over Apache AGE graph `enterprise_onto` |
| Vector Search (Similarity) | [`vector_store.py`](../../../nexus-backend/src/services/control_plane/vector_store.py) — pgvector cosine on `control_plane_embeddings` |
| Graph DB (Ontology + RDF) | Apache AGE on PostgreSQL — graph `enterprise_onto` populated by [`graph_loader.py`](../../../nexus-backend/src/stages/semantic-rag/graph_loader.py) |
| Vector DB (Embeddings Store) | pgvector table `control_plane_embeddings` (1536-d `text-embedding-3-small`) populated by [`vector_loader.py`](../../../nexus-backend/src/stages/semantic-rag/vector_loader.py) |
| Schema, Policy, Workflow, API spec, Process rule embeddings | `content_type` values `onto_schema`, `onto_policy`, `onto_workflow`, `onto_integration`, `onto_tool`, `onto_use_case` |
| The agent's `search_enterprise_knowledge` tool | [`rag_tools.py`](../../../nexus-backend/src/services/control_plane/tools/rag_tools.py) — wraps `hybrid_search`; only call point from the agent into this plane |
| ML Scoring Engine | Domain tools that score (e.g. `score_vendor_response`, `forecast_quote_win_probability`, `score_supplier_disruption_risk`) — composite-score classifiers callable from the agent |

---

## Page 3 — Data Plane (Ingestion & Transformation)

The bottom plane. Three ingestion paths from the source systems into the intelligence layer above. Each path matches the latency and governance profile of its sources.

```text
 ┌─────────────────────────────────────────────────────────────────────┐
 │                          AI-DATA-PLANE                              │
 │                  (Data Ingestion & Transformation)                  │
 │                                                                     │
 │       CDC Path             ETL Path              FDW Path           │
 │          │                    │                     │               │
 │          ▼                    ▼                     ▼               │
 │   ┌─────────────┐    ┌──────────────────┐   ┌──────────────────┐    │
 │   │ RDF Stream  │    │  RDF Batch       │   │  FDW Wrapper     │    │
 │   │ Processor   │    │  Transformer     │   │  (Virtual Access)│    │
 │   │ (CDC →      │    │  (R2RML / Batch) │   │                  │    │
 │   │  Ontology   │    │                  │   │  Postgres FDW /  │    │
 │   │  Mapper)    │    │                  │   │  Trino / Presto  │    │
 │   └──────┬──────┘    └────────┬─────────┘   └────────┬─────────┘    │
 │          │                    │                      │              │
 │          ▼                    ▼                      │              │
 │   ┌─────────────┐    ┌──────────────────┐            │              │
 │   │   Kafka     │    │   ETL Engine     │            │              │
 │   │             │    │   (Spark /       │            │              │
 │   │             │    │    Airflow /     │            │              │
 │   │             │    │    Custom)       │            │              │
 │   └──────┬──────┘    └────────┬─────────┘            │              │
 │          │                    │                      │              │
 │          ▼                    │                      │              │
 │   ┌─────────────┐             │                      │              │
 │   │ CDC Engine  │             │                      │              │
 │   │ (Debezium)  │             │                      │              │
 │   └──────┬──────┘             │                      │              │
 │          │                    │                      │              │
 │          └────────────┬───────┴──────────┬───────────┘              │
 │                       ▼                  ▼                          │
 │   ┌─────────────────────────────────────────────────────────────┐   │
 │   │                Enterprise Source Systems                    │   │
 │   │                                                             │   │
 │   │   ┌──────────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐  │   │
 │   │   │ Core Banking │ │ ERP / GL │ │    CRM    │ │ Legacy   │  │   │
 │   │   │ (Temenos /   │ │ (SAP /   │ │(Salesforce│ │ Systems  │  │   │
 │   │   │  Finacle)    │ │  Oracle) │ │ / Custom) │ │ / Files) │  │   │
 │   │   └──────────────┘ └──────────┘ └───────────┘ └──────────┘  │   │
 │   └─────────────────────────────────────────────────────────────┘   │
 │                                                                     │
 │   CDC: Real-time event streams from transaction-heavy systems       │
 │   ETL: Batch extraction for historical, analytical & master data    │
 │   FDW: Virtual access for low-volume / governance-restricted data   │
 └─────────────────────────────────────────────────────────────────────┘
```

**Maps to our codebase:**

| Reference block | Implementation |
|-----------------|----------------|
| FDW Wrapper / Postgres FDW | [`fdw_lifecycle.py`](../../../nexus-backend/src/fdw_lifecycle.py), [`fdw_connection_manager.py`](../../../nexus-backend/src/services/fdw_connection_manager.py), [`fdw_query_service.py`](../../../nexus-backend/src/services/fdw_query_service.py), [`fdw_discovery_service.py`](../../../nexus-backend/src/services/fdw_discovery_service.py) |
| CRM (Salesforce) ingestion | [`sfdc_simulator_service.py`](../../../nexus-backend/src/services/sfdc_simulator_service.py); live mode via Postgres FDW to Salesforce |
| ERP / GL (SAP / Oracle) ingestion | [`sap_simulator_service.py`](../../../nexus-backend/src/services/sap_simulator_service.py), [`oracle_erp_simulator_service.py`](../../../nexus-backend/src/services/oracle_erp_simulator_service.py) |
| Trade CPQ / Sourcing CPQ overlays | [`tpm_simulator_service.py`](../../../nexus-backend/src/services/tpm_simulator_service.py), [`sourcing_simulator_service.py`](../../../nexus-backend/src/services/sourcing_simulator_service.py) |
| Legacy / Files (Google Drive, uploads, social listening) | [`external_source_simulator_service.py`](../../../nexus-backend/src/services/external_source_simulator_service.py), [`gdrive_connector_service.py`](../../../nexus-backend/src/services/gdrive_connector_service.py) |
| ETL Engine (Spark / Airflow / Custom) | Apache NiFi flows under [`nexus-backend/nifi/`](../../../nexus-backend/nifi/) and the unstructured-extraction pipeline |
| CDC Engine (Debezium) | Event streams handled by the integration YAMLs (`sf-oracle-supply-chain-sync.yaml`, `sap-oracle-finance-sync.yaml`, etc.) under [`enterprise-knowledge/integrations/`](../../../nexus-backend/enterprise-knowledge/integrations/) |
| RDF Batch Transformer / RDF Stream Processor | Semantic RAG pipeline extractors under [`stages/semantic-rag/extractors/`](../../../nexus-backend/src/stages/semantic-rag/extractors/) (unified schema, FDW mapping, mapping rule, policy, workflow, integration) |
| Virtual Data Layer (the FDW-level abstraction) | [Data Plane console doc](../planes/data-plane.md) — the Virtual Data Layer (VDL) exposes every source as a uniform virtual entity |

---

## End-to-End Flow (request → response)

How a single user prompt traverses all three planes.

```text
   USER PROMPT
       │
       ▼
   ┌──────────────────────────┐
   │ "Find policies about     │   1.  Identity / RBAC check
   │  credit limits"          │   2.  Intent analyzer → "read_only"
   └──────────────────────────┘   3.  Risk = read-only
       │
       ▼ (Reasoning Plane)
   ┌──────────────────────────┐
   │   ReAct loop step 1      │
   │   LLM picks tool:        │
   │   search_enterprise_     │
   │   knowledge("credit      │
   │   limit policies")       │
   └──────────────────────────┘
       │
       ▼ (Control Plane)
   ┌──────────────────────────┐
   │  Enterprise RAG Layer    │
   │  ─ embed query           │
   │  ─ Vector Search (top-K) ├──── Vector DB (pgvector)
   │  ─ Graph Query reasoner  ├──── Graph DB (Apache AGE)
   │  ─ ML Scoring (optional) │
   │  Merge + dedupe          │
   └──────────────────────────┘
       │ retrieval_bundle (schemas / policies / workflows / integrations)
       │
       ▼ (back to Reasoning Plane)
   ┌──────────────────────────┐
   │  ReAct loop step 2       │
   │  Policy Engine ✓         │
   │  LLM composes answer     │
   │  Audit log written       │
   └──────────────────────────┘
       │
       ▼
   FINAL ANSWER + steps[] + retrieval_details

   (No Data Plane call in this example. A "show me overdue invoices"
    prompt would chain a second tool call into query_virtual_entity,
    which traverses the Data Plane via FDW/simulator paths back to
    the source systems.)
```

---

## Related References

- [Knowledge Indexing & Copilot Reasoning](knowledge-indexing-and-copilot-reasoning.md) — concrete step-by-step of how this reference is implemented.
- [Semantic RAG Pipeline](semantic-rag-pipeline.md) — deeper view of the indexing path that fills the Graph DB and Vector DB.
- [Semantic RAG Overview](../ai-os/semantic-rag.md) — retrieval engineering principles.
- [ReAct Layer](../ai-os/re-act-layer.md) — loop mechanics, policy gating, failure modes.
- [Reasoning Plane](../planes/reasoning-plane.md) — console drill-down of the agent loop.
- [Control Plane](../planes/control-plane.md) — ontology + knowledge graph.
- [Data Plane](../planes/data-plane.md) — Virtual Data Layer + FDW / ETL / CDC ingestion.
- Source artwork: [Algorithm.pdf](Algorithm.pdf).
