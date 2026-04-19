# Semantic RAG Pipeline — Implementation Reference

## Overview

The Semantic RAG pipeline builds an enterprise knowledge graph from Salesforce FDW metadata, business policies, workflow definitions, and integration mappings. It produces two stores:

- **pgvector** (`control_plane_embeddings`) — vector embeddings for semantic search
- **Apache AGE** (`enterprise_onto` graph) — nodes and edges for dependency traversal

The AI Copilot uses both stores via hybrid retrieval (vector + graph expansion) to answer questions with full business context: schemas, policies, workflows, integration dependencies, and approval rules.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Enterprise Knowledge Seed Data                 │
│                                                                  │
│  schema.yaml    policies/*.md    workflows/*.yaml    integrations │
│  (FDW overlay)  (business rules) (process flows)    (field sync)  │
└───────┬──────────────┬──────────────┬──────────────┬─────────────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Extraction Layer (Step 1-4)                    │
│                                                                  │
│  FDWExtractor      PolicyExtractor   WorkflowExtractor           │
│  (schema.yaml      (Markdown/PDF)    (YAML/JSON)                 │
│   overlay)                            IntegrationExtractor        │
│                                       (YAML/JSON)                │
└───────┬──────────────┬──────────────┬──────────────┬─────────────┘
        │              │              │              │
        └──────────────┴──────────┬───┴──────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│  Normalizer (Step 5)                                             │
│  Deduplicate by doc.id, merge relationships, build OntoBundle    │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│  Enricher (Step 6)                                               │
│  Schema: auto-enrich from metadata (no LLM cost)                 │
│  Policy/Workflow/Integration: LLM enrichment (gpt-4o-mini)       │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│  Chunker + Embedder (Step 7)                                     │
│  1 OntoDocument = 1 semantic chunk                               │
│  Embed with text-embedding-3-small (1536 dimensions)             │
└────────────┬────────────────────────────────┬────────────────────┘
             ▼                                ▼
┌─────────────────────────┐    ┌─────────────────────────────────┐
│  Vector Loader (Step 8) │    │  Graph Loader (Step 9)          │
│  pgvector upsert        │    │  Apache AGE Cypher MERGE        │
│  control_plane_         │    │  enterprise_onto graph          │
│  embeddings table       │    │  Entity nodes + typed edges     │
└─────────────────────────┘    └─────────────────────────────────┘
             │                                │
             ▼                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  Validator (Step 10)                                             │
│  10 black-box test scenarios, 6 scoring dimensions               │
│  Target: avg score ≥ 5.0 for production readiness                │
└──────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Steps

### Step 1: Extract FDW Metadata

**File:** `extractors/fdw_extractor.py` — `FDWExtractor`

Connects to PostgreSQL via `FDWConfig` and `FDWDiscoveryService`. Lists all foreign servers, tables, and columns. For each table, creates an `OntoDocument` with:
- `category = "schema"`, `entity_type = "Schema"`
- `content` = table name, server, column list
- `structured_metadata` = schema, server, column_count, columns array

**Schema Overlay** (`enterprise-knowledge/schema.yaml`):
- Loaded on extraction start
- Enriches matched tables with semantic descriptions, key field annotations, risk levels
- Creates `OntoRelationship` objects for cross-entity edges (triggers, syncs_to, constrained_by, depends_on)
- Generates virtual entities for Oracle ERP tables not in FDW

**Output:** ~1664 `OntoDocument`s (1661 FDW tables + 3 virtual Oracle entities), with relationships on key tables.

### Step 2: Extract Policy Documents

**File:** `extractors/policy_extractor.py` — `PolicyExtractor`

Parses Markdown, PDF, and text files from `enterprise-knowledge/policies/`. Markdown files are split by `##` headings — each section becomes a separate `OntoDocument`.

**Current seed data:**
- `credit-policy.md` → ~8 sections (source of truth, thresholds, close window, audit)
- `close-window-policy.md` → ~6 sections (schedule, restricted ops, SOX, override)
- `rbac-policy.md` → ~5 sections (roles, override auth, field access, separation of duties)

**Output:** ~21 `OntoDocument`s (category = "policy").

### Step 3: Extract Workflow Definitions

**File:** `extractors/workflow_extractor.py` — `WorkflowExtractor`

Parses YAML workflow definitions from `enterprise-knowledge/workflows/`. Each file can contain a single workflow or a `workflows` array.

**Current seed data:**
- `credit-approval.yaml` — 6-step approval flow with SLA and Oracle sync
- `customer-onboarding.yaml` — 7-step B2B onboarding with sequence constraints
- `risk-assessment.yaml` — 5-step risk scoring with tier mapping

**Output:** 3 `OntoDocument`s (category = "workflow").

### Step 4: Extract Integration Mappings

**File:** `extractors/integration_extractor.py` — `IntegrationExtractor`

Parses YAML integration definitions from `enterprise-knowledge/integrations/`.

**Current seed data:**
- `sf-oracle-sync.yaml` — Bidirectional Salesforce ↔ Oracle field-level sync

**Output:** 1 `OntoDocument` (category = "integration").

### Step 5: Normalize

**File:** `normalizer.py` — `Normalizer`

Merges all extracted documents into a single `OntoBundle`. Deduplicates by `doc.id` — on collision, merges relationships and keeps the longer content.

**Output:** `OntoBundle` with ~1689 unique documents.

### Step 6: LLM Enrichment

**File:** `enricher.py` — `Enricher`

Two enrichment paths:
- **Schema entities** (FDW tables): Auto-enriched from metadata — no LLM cost. Builds descriptions from table name, server, schema, columns, relationships.
- **Non-schema** (policies, workflows, integrations): Enriched via `gpt-4o-mini` with a prompt requesting business meaning, rules/constraints, dependent workflows, cross-system impact, and ownership.

**Output:** All documents have enriched `content` fields. Returns `(enriched_count, tokens_used)`.

### Step 7: Chunk & Embed

**File:** `chunker.py` — `Chunker`

One `OntoDocument` = one semantic chunk (no splitting). Each chunk is embedded using `text-embedding-3-small` (1536 dimensions) via batch API.

**Output:** `List[Dict]` with `onto_id`, `content_type` (`onto_schema`, `onto_policy`, `onto_workflow`, `onto_integration`), `source_id`, `content`, `metadata`, `embedding`.

### Step 8: Load Vector DB

**File:** `vector_loader.py` — `VectorLoader`

Upserts each chunk into `control_plane_embeddings` via `VectorStore.upsert()`. Uses `ON CONFLICT (content_type, source_id) DO UPDATE` for idempotency.

**Target:** PostgreSQL table `control_plane_embeddings` with pgvector extension.

### Step 9: Load Graph DB

**File:** `graph_loader.py` — `GraphLoader`

Loads all `OntoDocument`s as `Entity` nodes in the `enterprise_onto` Apache AGE graph. For each document's `relationships`, creates typed edges (TRIGGERS, SYNCS_TO, CONSTRAINED_BY, DEPENDS_ON).

Uses `LOAD 'age'` + Cypher `MERGE` with proper single-quoted property syntax. Commits every 200 nodes. Rolls back and recovers on individual node errors.

**Fallback:** If Apache AGE is unavailable, stores a JSON relationship index in pgvector as `onto_graph_index`.

### Step 10: Validate Quality

**File:** `validator.py` — `SemanticRagValidator`

Runs 10 black-box test scenarios (from `semantic-rag.md`) against the vector store. Each scenario is scored on 6 dimensions:
1. Correct Object Identified
2. Correct Fields Retrieved
3. Policy Retrieved
4. Workflow Dependency Retrieved
5. Cross-System Impact Retrieved
6. Version Correct

**Target:** Average score ≥ 5.0 for production readiness.

---

## Data Model

### OntoDocument

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Deterministic ID (e.g. `STARHUB_ITXP2DEV_ACCOUNT_V1_0`) |
| `system` | str | Salesforce / Oracle / Internal |
| `entity_type` | str | Schema / Policy / Workflow / Integration |
| `object_name` | str | Account / CreditApprovalFlow / CreditPolicy |
| `category` | str | schema / policy / workflow / integration |
| `content` | str | LLM-enriched semantic description (gets embedded) |
| `field_name` | str? | For field-level docs |
| `risk_level` | str | high / medium / low |
| `structured_metadata` | Dict | Schema, columns, domain, key fields |
| `relationships` | List[OntoRelationship] | Directed edges to other documents |
| `source` | str | fdw / policy_doc / workflow_def / integration_map |

### OntoRelationship

| Field | Type | Description |
|-------|------|-------------|
| `relation_type` | str | triggers / syncs_to / constrained_by / depends_on / owned_by / validates |
| `target_id` | str | Target OntoDocument ID |
| `description` | str | Human-readable edge description |

---

## Query Layer (AI Copilot)

### Hybrid Search

When the AI Copilot receives a question:

1. **Vector search** — Embed query, find top-15 similar documents (min similarity 0.20)
2. **Graph expansion** — Extract `onto_id`s from results, traverse Apache AGE graph for 2 hops, find neighbor policies/workflows/integrations
3. **Neighbor retrieval** — Fetch graph-expanded documents by exact `source_id` lookup
4. **Merge & deduplicate** — Combine vector + graph results, sort by relevance
5. **Build retrieval bundle** — Group into `schemas`, `policies`, `workflows`, `integrations`, `graph_dependencies`

### Agent Executor (ReAct Loop)

The agent receives the structured retrieval bundle and uses it to answer with:
- Source of Truth identification
- Relevant fields and constraints
- Applicable policies and approval thresholds
- Workflow steps and SLAs
- Cross-system integration dependencies
- Close window and RBAC restrictions

---

## Enterprise Knowledge Seed Data

Located in `starhub-backend/enterprise-knowledge/`:

| File | Category | Documents | Description |
|------|----------|-----------|-------------|
| `schema.yaml` | schema | — (overlay) | Enriches FDW tables with domains, key fields, relationships |
| `policies/credit-policy.md` | policy | ~8 | Credit limits, approval thresholds, source of truth |
| `policies/close-window-policy.md` | policy | ~6 | Financial close restrictions, SOX compliance |
| `policies/rbac-policy.md` | policy | ~5 | Role-based access, credit override authorization |
| `workflows/credit-approval.yaml` | workflow | 1 | 6-step credit approval flow |
| `workflows/customer-onboarding.yaml` | workflow | 1 | 7-step B2B customer onboarding |
| `workflows/risk-assessment.yaml` | workflow | 1 | 5-step risk tier evaluation |
| `integrations/sf-oracle-sync.yaml` | integration | 1 | Salesforce ↔ Oracle field-level sync |

---

## Storage Layer

### pgvector — `control_plane_embeddings`

```sql
CREATE TABLE control_plane_embeddings (
    id SERIAL PRIMARY KEY,
    content_type VARCHAR(50) NOT NULL,     -- onto_schema, onto_policy, onto_workflow, onto_integration
    source_id VARCHAR(255) NOT NULL,       -- OntoDocument.id
    content TEXT NOT NULL,                 -- Enriched semantic description
    metadata JSONB DEFAULT '{}',           -- Structured metadata (category, system, domain, etc.)
    embedding vector(1536),               -- text-embedding-3-small
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(content_type, source_id)
);
```

### Apache AGE — `enterprise_onto`

```cypher
-- Nodes
(:Entity {onto_id: 'STARHUB_ITXP2DEV_ACCOUNT_V1_0', system: 'Salesforce', entity_type: 'Schema', ...})

-- Edges
(:Entity)-[:TRIGGERS]->(:Entity)
(:Entity)-[:SYNCS_TO]->(:Entity)
(:Entity)-[:CONSTRAINED_BY]->(:Entity)
(:Entity)-[:DEPENDS_ON]->(:Entity)
```

---

## REST API Endpoints

### Control Plane API (`/api/v1/control-plane`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/search` | Semantic vector search |
| POST | `/ask` | RAG question answering (vector + LLM) |
| POST | `/agent` | ReAct agent with tools, policy, audit |
| POST | `/index` | Trigger schema re-indexing |
| GET | `/stats` | Live counts: embeddings, graph nodes/edges, by content type |
| GET | `/tools` | List registered agent tools with risk levels |

### Onto API (`/api/v1/control-plane/onto`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/onto/search` | Hybrid search (vector + graph) |
| GET | `/onto/stats` | Detailed index stats by content type |
| GET | `/onto/graph/{onto_id}` | Graph neighborhood visualization |
| GET | `/onto/bundles` | List .onto bundles in S3 |

---

## Current Index Stats (as of latest pipeline run)

| Metric | Count |
|--------|-------|
| Graph Nodes | 1,689 |
| Graph Edges | 6 |
| Vector Embeddings | 1,690 |
| Schema Documents | 1,664 |
| Policy Documents | 21 |
| Workflow Documents | 3 |
| Integration Documents | 1 |
| Embedding Model | text-embedding-3-small |
| Graph Backend | Apache AGE 1.7.0 |
