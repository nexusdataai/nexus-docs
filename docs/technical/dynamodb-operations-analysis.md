# DynamoDB Operations Analysis

Throughput, hot-key, and cost analysis for the four DynamoDB tables that back the **NexusAI Data-AI Platform**.

For the schemas themselves see [Database Design > Journey Data](dbdesign/journey-data.md) and [Database Design > Capability Data](dbdesign/capability-data.md). For the env / IAM / SSM resource conventions see [Infrastructure Requirements](INFRASTRUCTURE_REQUIREMENTS.md).

## Tables in scope

| Table | Drives |
|---|---|
| `nexus-ai-{env}-transformation-system` | Journey / Stage / Job state for AI Automation. Single-table design with one partition per journey, items for stages and jobs under it. |
| `nexus-ai-{env}-capability-system` | Capability catalogue (NexusCapability custom resources, Solution metadata). |
| `nexus-ai-{env}-license` | License records, activation events, audit log. |
| `control-plane-audit` | Per-step ReAct agent audit (intent, tool calls, results, policy violations) -- highest write volume on the platform. |

## Per-table operation profile

### `transformation-system`

| Operation | Trigger | Per-call ops |
|---|---|---|
| Create journey | UI / API authoring | 1 PutItem (PK = `JOURNEY#<id>`, SK = `META`) |
| Add stage | Journey Builder save | 1 PutItem per stage |
| Trigger run | Manual / Schedule / Webhook | 1 PutItem per job (PK = `JOURNEY#<id>`, SK = `JOB#<run-id>`) |
| Stage step start / end | per-step execution | 2 UpdateItem per stage step (start, end) |
| Read journey | UI render | 1 Query on PK |
| Read job history | UI render | 1 Query on GSI1 (`GSI1PK = JOURNEY#<id>`) ordered by SK |
| Cleanup | Operator GC | BatchDeleteItem batches of 25 |

**Hot-key risk**: high-frequency journey runs (e.g. CDC ingestion, scheduled hourly) concentrate writes under one PK. Mitigation: split partition by introducing a date / hour suffix (`JOURNEY#<id>#<yyyymmddhh>`) when the per-journey write rate exceeds 1,000 / s.

### `capability-system`

| Operation | Trigger | Per-call ops |
|---|---|---|
| Register Solution | Operator reconcile | 1 PutItem |
| Update Solution metadata | Catalogue edit | 1 UpdateItem |
| List Solutions | Catalogue render | 1 Scan or Query (small N; uncached on first hit) |

**Hot-key risk**: low. Read volume scales with Catalogue page renders; cacheable.

### `license`

| Operation | Trigger | Per-call ops |
|---|---|---|
| Activate license | Onboarding | 1 PutItem |
| Validate license | Backend startup, periodic | 1 GetItem |
| Audit event | Activation, change, revoke | 1 PutItem to audit partition |

**Hot-key risk**: low. Audit-partition writes are append-only and bounded by license-state-change frequency.

### `control-plane-audit`

| Operation | Trigger | Per-call ops |
|---|---|---|
| Step record | Every ReAct iteration | 1 PutItem (PK = `session_id`, SK = `step#<n>`) |
| Tool call | Every tool invocation | 1 PutItem (extends current step's record OR inserts a child record) |
| Policy violation | Every gate block | 1 PutItem |
| Session query | UI step trace render | 1 Query on PK |

**Highest write volume on the platform.** A single agent session can produce 5-15 PutItems. Sustained 10 sessions / s -> ~150 writes / s.

**Hot-key risk**: per-session is bounded (~10s of writes); **across sessions it's effectively random** because `session_id` is a UUID. No mitigation needed unless agent session rate exceeds 1,000 / s.

## Capacity recommendations

### Pay-per-request (default for dev / stage)

Recommended for non-production environments. No capacity planning, billed per request.

### Provisioned (for prod)

Reference values for a typical production deployment:

| Table | Base RCU | Base WCU | Auto-scaling | Burst headroom |
|---|---|---|---|---|
| `transformation-system` | 100 | 200 | 50-1000 RCU, 50-1000 WCU | 200% |
| `transformation-system` GSI1 | 50 | 100 | 25-500 each | 200% |
| `capability-system` | 50 | 25 | 10-200 each | 100% |
| `license` | 25 | 10 | 5-100 each | 100% |
| `control-plane-audit` | 50 | 200 | 50-2000 each | 300% |

Tune from CloudWatch metrics after one week in production.

## Cost levers

- **TTL on stale audit data** -- enable TTL on `control-plane-audit` (90-day default) to bound costs.
- **TTL on completed journeys** -- enable TTL on completed `transformation-system` job items (30-day default; original journey definition is preserved).
- **PITR** -- on for `transformation-system` and `license` (regulatory); optional for `capability-system` and `control-plane-audit`.
- **Storage class** -- DynamoDB Standard-IA for the audit table beyond the hot 7-day window if write rate falls.

## Reading the metrics

| CloudWatch metric | What to watch | Action |
|---|---|---|
| `ConsumedReadCapacityUnits` / `ConsumedWriteCapacityUnits` | Approaching provisioned cap | Raise auto-scale ceiling |
| `ThrottledRequests` | Non-zero | Auto-scale settings too narrow; raise ceiling |
| `SystemErrors` | Non-zero sustained | Investigate region health, retries |
| `SuccessfulRequestLatency` (p99) | > 100 ms sustained | Investigate per-table partition distribution |
| `ConditionalCheckFailedRequests` | Spike | Optimistic-locking conflict on a journey or job; investigate |

## Related references

- [Database Design > Journey Data](dbdesign/journey-data.md)
- [Database Design > Capability Data](dbdesign/capability-data.md)
- [Infrastructure Requirements](INFRASTRUCTURE_REQUIREMENTS.md)
- [CloudWatch Logs Analysis](cloudwatch-logs-analysis.md)
- [Implementation Guide](../ai-os/implementation-guide.md)
