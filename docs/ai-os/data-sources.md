# Data Sources — FDW vs ETL vs CDC

The Data Plane hydrates the **Virtual Data Layer (VDL)** through three complementary mechanisms. Each source system is mapped to one (or more) of them based on latency, payload shape, and governance constraints.

## Mechanisms at a Glance

- **FDW (Foreign Data Wrapper)** — live federated query (Postgres FDW / Trino / Presto). Millisecond latency. No replication. Best for real-time dashboards, low-volume sources, governance-restricted data.
- **ETL (Extract / Transform / Load)** — batch ingest into an ontology-aligned warehouse. Minute-to-hour latency. Full replication. Best for analytical workloads, historical snapshots, cross-domain joins, master data.
- **CDC (Change Data Capture)** — log-based streaming (Debezium / Kafka). Second latency. Incremental replication. Best for transaction-heavy systems, real-time fraud / AML, operational graphs.

## FDW

- **Pattern** — source DB → FDW → VDL → consumer. Query is pushed down to the source; nothing is copied.
- **Used in NexusAI for** — live federated reads against Salesforce, Oracle ERP, SAP S/4HANA, BSSMagic CRM via PostgreSQL FDW with Multicorn for protocol-specific wrappers.
- **Strengths** — no duplication; real-time; fast to set up; low infrastructure cost; source remains source-of-truth.
- **Limitations** — query performance depends on the source; complex cross-system joins can be slow; source availability impacts the platform.
- **Use when** — the source must stay authoritative; latency matters; volumes are small-to-medium; governance forbids copying.

## ETL

- **Pattern** — source → extractor → ontology-aligned transformer (R2RML / batch / custom) → warehouse / graph store → VDL.
- **Used in NexusAI for** — bulk historical data, master data, document and file feeds (Google Drive, file uploads, sustainability reports, market signals).
- **Strengths** — high query performance; data consistency; historical snapshots; full control over schema; ideal for ML feature engineering and regulatory reporting.
- **Limitations** — duplication; batch latency; more infrastructure; higher storage cost.
- **Use when** — workloads are analytical; historical depth matters; complex joins span domains.

## CDC

- **Pattern** — source DB log → CDC engine (Debezium) → Kafka → streaming transformer → ontology store → VDL.
- **Used in NexusAI for** — transaction-heavy operational systems (Core Banking, ERP transactions, AR / AP, journey events), real-time fraud detection, AML monitoring.
- **Strengths** — near-real-time; incrementally efficient; event-driven; supports operational graphs and compliance monitoring.
- **Limitations** — more complex infrastructure; requires event streaming; harder debugging; schema evolution must be handled explicitly.
- **Use when** — the source generates a high volume of events; downstream needs to react in real time; full audit trail of every change matters.

## Decision Framework

- **Need real-time updates?** → CDC (or FDW for ad-hoc reads).
- **Heavy cross-domain joins?** → ETL.
- **Performance critical for large analytical queries?** → ETL or CDC.
- **Want minimal infrastructure footprint?** → FDW.
- **Powering operational AI / agents?** → ETL or CDC (for the materialised graph).

## Hybrid Is the Norm

Most production deployments use all three together:

- **CDC** for core operational entities (transactions, payments, orders).
- **ETL** for the historical / analytical warehouse and large reference data.
- **FDW** for rare, low-value, or governance-restricted datasets that should never be copied.

Concretely:

```text
Salesforce, Oracle ERP, SAP -> FDW (live reads + writes via Tool layer)
Google Drive, file uploads, market signals, sustainability reports -> ETL
Kafka / Debezium event streams from transactional cores -> CDC
```

Whichever path the data took, the VDL exposes it through one query API; the Reasoning Plane never has to know the difference.

For the console-side view of these mechanisms, see [Platform Architecture > Data Plane](../platform-architecture.md#data-plane). For the deeper drill-down see the [Data Plane page](../planes/data-plane.md).
