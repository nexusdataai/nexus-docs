# CloudWatch Logs Analysis

Log volume, retention, and cost analysis for the **NexusAI Data-AI Platform** running on AWS EKS.

For the env / IAM / SSM conventions see [Infrastructure Requirements](INFRASTRUCTURE_REQUIREMENTS.md). For deployment ops see [Operations](../operational/index.md).

## Log groups

| Log group | Source | Estimated volume |
|---|---|---|
| `/aws/nexus-ai/{env}/backend` | All backend pods (FastAPI + MCP gateway + Control / Data / Reasoning Plane) | High |
| `/aws/nexus-ai/{env}/frontend` | nginx access + error logs from frontend pods | Medium |
| `/aws/nexus-ai/{env}/operator` | Nexus Capability Operator reconcile logs | Low |
| `/aws/nexus-ai/{env}/audit` | Mirrored stream of `control-plane-audit` events | Medium-high |
| `/aws/eks/{cluster}/cluster` | EKS control-plane (API server, scheduler, kube-controller, audit) | Configurable |
| `/aws/applicationelb/{name}` | ALB access logs (when enabled) | Medium |

## Volume drivers (backend log group)

The backend log group is the largest. Drivers, ranked by typical volume per environment:

- **Knowledge Pipeline runs** -- six stages emit per-document logs during a re-index. A 1,661-table FDW re-index produces a few thousand log lines and runs in ~40 seconds.
- **ReAct agent sessions** -- every step (intent, retrieval, tool call, observation, final answer) emits a structured log line. ~10-20 lines per session at INFO; more at DEBUG.
- **FDW query traffic** -- one log line per query at INFO; pagination and large filters add minor volume.
- **Journey job runs** -- per-stage and per-step lines plus per-tool-call lines.
- **Health probes** -- bounded by k8s probe frequency (default 10 s); lowest-impact filter target.

## Sizing reference (production, single tenant)

| Profile | Backend log lines / s | Daily volume (compressed) | Monthly cost band |
|---|---|---|---|
| Light (dev / pilot) | ~5 lines/s | ~1 GB / day | < $10 |
| Standard (mid customer) | ~20 lines/s | ~5 GB / day | $50-100 |
| Heavy (large customer with active CDC + many active Solutions) | ~100 lines/s | ~25 GB / day | $250-500 |

Costs are dominated by **ingestion** (PutLogEvents) and **storage** (per GB-month). Adjust by reducing log level (default INFO) and shortening retention.

## Retention defaults

| Log group | Default retention | Rationale |
|---|---|---|
| `/aws/nexus-ai/{env}/backend` | 30 days | Operational debugging window |
| `/aws/nexus-ai/{env}/frontend` | 30 days | Operational debugging window |
| `/aws/nexus-ai/{env}/operator` | 90 days | Reconcile-trace retention through quarterly review |
| `/aws/nexus-ai/{env}/audit` | 365 days | Compliance default; configurable per regulatory regime |
| `/aws/eks/{cluster}/cluster` | 30 days | Diagnostic only |
| `/aws/applicationelb/{name}` | 90 days | Access-pattern review |

## Cost levers

- **Log level** -- backend defaults to INFO; switching to WARN halves volume in steady state.
- **Per-component log level** -- override via SSM (`/nexus-ai/{env}/server/log-level`); Reasoning Plane DEBUG logs are the noisiest.
- **Subscription filters** -- forward only the audit stream to long-term storage (S3 + Athena); discard verbose backend logs after 30 days.
- **Metric filters** -- count error-rate / policy-violation patterns into custom CloudWatch metrics, then dashboard from those (cheaper than re-querying logs).
- **Sampling** -- sample non-error backend logs at 10% in heavy environments; preserve all WARN+ and all audit lines.
- **S3 export** -- export to S3 + lifecycle to Glacier for compliance retention beyond CloudWatch's hot tier.

## Alerting

| Pattern | Action |
|---|---|
| `[ERROR]` rate > 5 / minute on backend | Page on-call |
| `policy_violation` on backend | Notify ops channel (no page; expected during exploration but useful to track) |
| Reconcile failure on operator | Page on-call |
| ALB 5xx rate > 1% over 5 minutes | Page on-call |
| Knowledge Pipeline failure | Notify ops + product channels |

## Reading log lines

Backend logs are structured JSON with `timestamp`, `level`, `service`, `request_id`, `session_id` (when in an agent session), `tool` (when in a tool call), and the log message. Search by `request_id` to follow a single user request end-to-end; search by `session_id` to follow an agent session across all of its steps.

Audit lines additionally carry: `intent`, `risk_level`, `tool_name`, `policy_violation_kind` (if any), `result_summary`. They are mirrored to DynamoDB for queryable retention.

## Related references

- [DynamoDB Operations Analysis](dynamodb-operations-analysis.md)
- [Infrastructure Requirements](INFRASTRUCTURE_REQUIREMENTS.md)
- [Operations](../operational/index.md)
- [Implementation Guide](../ai-os/implementation-guide.md) -- the audit logger lives in `audit_logger.py`
