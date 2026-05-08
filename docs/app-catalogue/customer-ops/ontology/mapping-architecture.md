# Mapping Architecture & Semantic Indexing

How the unified customer operations schema maps to the existing systems of record, how the semantic indexing pipeline processes it, and how the ReAct agent uses the indexed ontology to serve queries and take actions.

---

## Schema-First Architecture

The customer operations ontology uses a **schema-first** approach — the unified schema is the primary knowledge source, not the FDW foreign tables. FDW becomes a mapping resolution layer that annotates which schema entities have live database connections.

```mermaid
flowchart TD
    subgraph SchemaOverlay [Unified Schema - customer-ops-schema.yaml]
        SF["Salesforce Entities<br/>Account, Case, Contact..."]
        WXCC["WXCC Entities - virtual<br/>Call_Record, Agent_State, Queue..."]
        ORA["Oracle Entities - virtual<br/>AR_Invoice, Billing_Dispute..."]
        SAP["SAP Entities - virtual<br/>Service_Order, Field_Dispatch..."]
        UNS["Unstructured - virtual<br/>SOP_Document, Knowledge_Article..."]
    end

    subgraph FDWLayer [FDW Mapping Resolution]
        DISC["FDW Discovery Service<br/>pg_foreign_server + information_schema"]
        MATCH["Match schema fdw_table<br/>to live foreign tables"]
    end

    subgraph Status [Mapping Status]
        MAPPED["MAPPED<br/>Live FDW table exists<br/>Queryable via SQL"]
        VIRTUAL["VIRTUAL<br/>Data via integration<br/>Not directly queryable"]
        UNMAPPED["UNMAPPED<br/>Expected FDW table<br/>not yet connected"]
    end

    SF --> MATCH
    DISC --> MATCH
    MATCH --> MAPPED
    WXCC --> VIRTUAL
    ORA --> VIRTUAL
    SAP --> VIRTUAL
    UNS --> VIRTUAL
```

### Entity Mapping Status

| Status | Meaning | Count | Example |
|--------|---------|-------|---------|
| **Mapped** | Live FDW foreign table exists; entity is queryable via `query_table` tool | ~8 | Account, Contact, Case, Case_Comment |
| **Virtual** | Entity data flows via integration sync; not directly queryable via FDW | ~25 | Call_Record, AR_Invoice, Service_Order, Agent_State |
| **Unmapped** | Schema defines the entity but no FDW table or integration connected yet | ~2 | Problem_Record, Trend_Alert (derived entities) |

---

## Semantic RAG Pipeline (12 Steps)

The pipeline follows the same 12-step process as the supply chain ontology, extended with Steps 1A (Unified Schema Extraction) and 1B (FDW Mapping Resolution):

```mermaid
flowchart LR
    subgraph Extraction [Extraction Phase]
        S1A["Step 1A<br/>Unified Schema Extract<br/>~35 entities from *-schema.yaml"]
        S1B["Step 1B<br/>FDW Mapping Resolution<br/>Match to live FDW tables"]
        S1C["Step 1C<br/>Legacy FDW Extract<br/>Non-schema FDW tables"]
        S2["Step 2<br/>Policy Extract<br/>6 policies from *.md"]
        S3["Step 3<br/>Workflow Extract<br/>8 workflows from *.yaml"]
        S4["Step 4<br/>Integration Extract<br/>5 integrations from *.yaml"]
    end

    subgraph Processing [Processing Phase]
        S5["Step 5<br/>Normalize + Dedupe<br/>Merge into OntoBundle"]
        S6["Step 6<br/>Enrich<br/>TMF/ITIL-aware"]
        S7["Step 7<br/>Chunk + Embed"]
    end

    subgraph Loading [Loading Phase]
        S8["Step 8<br/>Load pgvector"]
        S9["Step 9<br/>Load Apache AGE Graph"]
        S10["Step 10<br/>Validate - scenarios"]
    end

    S1A --> S1B --> S1C --> S5
    S2 --> S5
    S3 --> S5
    S4 --> S5
    S5 --> S6 --> S7 --> S8 --> S9 --> S10
```

### Step Details

| Step | File | What It Does |
|------|------|-------------|
| **1A** | `unified_schema_extractor.py` | Reads `customer-ops-schema.yaml`; creates OntoDocuments for every entity with TMF process, ITIL practice, and FDW mapping status annotations |
| **1B** | `fdw_mapping_resolver.py` | Queries `FDWDiscoveryService` to match schema entities to live FDW foreign tables; annotates as mapped/virtual/unmapped; enriches mapped entities with live column metadata |
| **1C** | `fdw_extractor.py` | Original FDW extractor for non-schema tables (backward compatibility for CRM-only FDW tables) |
| **2** | `policy_extractor.py` | Auto-discovers all `*.md` from `enterprise-knowledge/policies/` — includes 6 customer ops policies |
| **3** | `workflow_extractor.py` | Auto-discovers all `*.yaml` from `enterprise-knowledge/workflows/` — includes 8 customer ops workflows |
| **4** | `integration_extractor.py` | Auto-discovers all `*.yaml` from `enterprise-knowledge/integrations/` — includes 5 customer ops integrations |
| **5** | `normalizer.py` | Merges all extracted documents; deduplicates by ID; merges relationships and `structured_metadata` on collision |
| **6** | `enricher.py` | Schema entities: auto-enriched with TMF process, ITIL practice, and FDW status. Policies/workflows/integrations: LLM-enriched via gpt-4o-mini |
| **7** | `chunker.py` | 1 document = 1 chunk; batch embedded (20/batch) via OpenAI text-embedding-3-small |
| **8** | `vector_loader.py` | Upserted to pgvector `control_plane_embeddings` with content_type: `onto_schema`, `onto_policy`, `onto_workflow`, `onto_integration` |
| **9** | `graph_loader.py` | Nodes (Entity) and edges (triggers/syncs_to/constrained_by/depends_on/escalates_to) merged into Apache AGE `enterprise_onto` graph |
| **10** | `validator.py` | Black-box test scenarios validating retrieval quality across 6 dimensions |

### What Gets Indexed

| Source | Content Type | Approx Count |
|--------|-------------|-------------|
| Unified schema (Salesforce + WXCC + Oracle + SAP + unstructured) | `onto_schema` | ~35 |
| Policies (6 customer ops) | `onto_policy` | ~40+ (split by section) |
| Workflows (8 customer ops) | `onto_workflow` | ~8 |
| Integrations (5 customer ops) | `onto_integration` | ~5 |
| **Total** | — | **~88+** |

---

## ReAct Agent and Tools

The ReAct agent uses the indexed ontology to answer questions and take actions. The flow is: **Search ontology -> Reason with policies -> Execute actions -> Validate compliance.**

### Tool Inventory

#### Read Tools

| Tool | Domain | What It Does |
|------|--------|-------------|
| `search_enterprise_knowledge` | Core | Hybrid vector + graph search across all ontology types |
| `search_schema_knowledge` | Core | Vector search over FDW table definitions |
| `discover_tables` / `discover_columns` / `query_table` | Core | FDW table discovery and parameterized SQL queries |
| `check_policy_compliance` | Governance | Validates proposed actions against indexed policies |
| `get_customer_360` | Customer Ops | Assemble unified customer profile across all systems |
| `get_case_lifecycle` | Customer Ops | Trace case from creation through resolution across systems |
| `get_billing_status` | Customer Ops | Query billing status, disputes, and payment history |
| `get_interaction_history` | Customer Ops | Retrieve interaction timeline from WXCC + Salesforce |

#### Write Tools

| Tool | Risk Level | What It Does |
|------|-----------|-------------|
| `create_case` | LOW_RISK_WRITE | Create new case in Salesforce with full context |
| `update_case_status` | LOW_RISK_WRITE | Update case status, add comments, set resolution code |
| `issue_credit_note` | HIGH_RISK_WRITE | Issue credit note in Oracle (triggers approval per policy) |
| `create_service_order` | LOW_RISK_WRITE | Create service order in SAP for field dispatch |
| `escalate_case` | LOW_RISK_WRITE | Escalate case to next level with context brief |

### End-to-End ReAct Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent as ReAct Agent
    participant RAG as Ontology Search
    participant Policy as Policy Check
    participant SoR as System of Record

    User->>Agent: "Customer ACCT-1205 is disputing invoice INV-4521 for $342"
    Agent->>RAG: search_enterprise_knowledge("billing dispute ACCT-1205 INV-4521")
    RAG-->>Agent: Account profile + billing-dispute-policy + AR_Invoice schema + Case schema
    Agent->>Agent: REASON: Invoice $342, customer is Gold tier, dispute type likely overcharge
    Agent->>Policy: check_policy_compliance("issue_credit", "AR_Invoice", "$342 credit for Gold tier")
    Policy-->>Agent: COMPLIANT — auto-approve <$500 for billing error per POL-BILL-001
    Agent->>SoR: issue_credit_note(customer="ACCT-1205", invoice="INV-4521", amount=342, reason="Billing_Error")
    SoR-->>Agent: Credit_Note_ID: CN-2026-0891
    Agent->>SoR: update_case_status(case="SF-2026-8831", status="Resolved", resolution="Credit issued")
    Agent->>User: Credit note CN-2026-0891 issued for $342. Case resolved. Auto-approved per billing dispute policy.
```

---

## UI Integration

### Data Plane Page

- **Vertical selector** filters data sources by domain (All / Customer Ops / Supply Chain / CRM)
- Each source node shows **ontology entity count** and **TMF process coverage**
- Source cards display **FDW mapping status** (mapped / virtual) and **entity count badges**

### Control Plane Page

- **Semantic Layer tab** shows vertical-level stats (Customer Ops: 35 entities, 8 workflows, 6 policies, 5 integrations)
- **TMF process distribution** badges (Customer Mgmt, Trouble Ticket, Service Order, Billing, Interaction, SLA)
- **Knowledge Formation** and **Semantic Explorer** tabs support system and TMF filtering

### Reasoning Page

- **ReAct Tools tab** organizes tools into **Read Tools** and **Write Tools** with domain badges (Core / Customer Ops / CRM / Governance)
- **AI Copilot** system prompt includes customer operations context and tool selection strategy

---

## Configuration

The pipeline is configured via `SemanticRagConfig`:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `schema_dir` | `enterprise-knowledge/` | Directory containing `*-schema.yaml` files |
| `policy_path` | `enterprise-knowledge/policies/` | Directory with policy Markdown files |
| `workflow_path` | `enterprise-knowledge/workflows/` | Directory with workflow YAML files |
| `integration_path` | `enterprise-knowledge/integrations/` | Directory with integration YAML files |
| `skip_unified_schema` | `false` | Skip Step 1A (unified schema extraction) |
| `skip_fdw_mapping` | `false` | Skip Step 1B (FDW mapping resolution) |
| `enrich_with_llm` | `true` | Enable LLM enrichment for non-schema docs |
| `skip_graph` | `false` | Skip Apache AGE graph loading |

Trigger reindex via: `POST /api/v1/control-plane/reindex`

---

[← Back to Ontology Overview](index.md)
