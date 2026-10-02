# Infrastructure Requirements

Environment variables, secrets, DynamoDB tables, S3 buckets, and SSM parameters required to run the **NexusAI Data-AI Platform** (`nexus-backend` + `nexus-ui`).

For the deployment surface that creates these resources, see [Operations > Kubernetes Operator](../operational/kubernetes-operator/index.md).

## Naming convention

All AWS resources follow the `capability-env-name` pattern.

```
SSM:        /nexus-ai/{env}/{category}/{resource}
Secrets:    nexus-ai/{env}/{secret}
DynamoDB:   nexus-ai-{env}-{name}
S3:         nexus-ai-{env}-{name}
CloudWatch: /aws/nexus-ai/{env}
```

Where `{env}` is one of `dev`, `stage`, `test`, `prod`. The ECS / EKS task definition exports `ENVIRONMENT` so the service can construct resource names at runtime.

## DynamoDB tables

| Pattern | Example (prod) | Purpose | Key schema | GSIs |
|---|---|---|---|---|
| `nexus-ai-{env}-transformation-system` | `nexus-ai-prod-transformation-system` | Journey / Stage / Job state ([schema](dbdesign/journey-data.md)) | PK (HASH), SK (RANGE) | GSI1 (GSI1PK, GSI1SK) |
| `nexus-ai-{env}-capability-system` | `nexus-ai-prod-capability-system` | Capability catalogue metadata ([schema](dbdesign/capability-data.md)) | PK (HASH), SK (RANGE) | -- |
| `nexus-ai-{env}-license` | `nexus-ai-prod-license` | License records + audit logs | PK (HASH), SK (RANGE) | status-index, holder-index, license-index |
| `control-plane-audit` | `control-plane-audit` | Per-step ReAct agent audit (intent, tool calls, results, policy violations) | session_id (HASH), step_id (RANGE) | -- |

## S3 buckets

| Pattern | Example (prod) | Purpose |
|---|---|---|
| `nexus-ai-{env}-call-data` | `nexus-ai-prod-call-data` | Journey artefacts, intermediate outputs, transcripts (when used) |
| `nexus-ai-{env}-journey-logs` | `nexus-ai-prod-journey-logs` | Per-stage execution logs |
| `nexus-ai-{env}-sfdc-simulator` | `nexus-ai-prod-sfdc-simulator` | SFDC simulator dump (foreign servers, tables, columns, row data) |

All buckets ship with: SSE-KMS or SSE-S3 encryption, versioning enabled, lifecycle policies for old artefacts, and CloudWatch metrics.

## SSM Parameter Store

| Path | Purpose |
|---|---|
| `/nexus-ai/{env}/server/log-level` | Backend log level |
| `/nexus-ai/{env}/server/timeout` | Default request timeout |
| `/nexus-ai/{env}/cognito/user-pool-id` | Cognito user pool |
| `/nexus-ai/{env}/cognito/client-id` | Cognito app client |
| `/nexus-ai/{env}/cognito/domain` | Cognito hosted-UI domain |
| `/nexus-ai/{env}/sfdc/enabled` | SFDC simulator master toggle |
| `/nexus-ai/{env}/sfdc/bucket` | SFDC simulator dump bucket |
| `/nexus-ai/{env}/sfdc/prefix` | SFDC simulator dump key prefix |
| `/nexus-ai/{env}/control-plane/embedding-model` | Vector embedding model name |
| `/nexus-ai/{env}/control-plane/llm-model` | LLM model used by ReAct agent |
| `/nexus-ai/{env}/control-plane/max-steps` | Default ReAct step budget |
| `/nexus-ai/{env}/fdw/host` | Backend PostgreSQL FDW host |
| `/nexus-ai/{env}/fdw/database` | Backend PostgreSQL DB name |
| `/nexus-ai/{env}/fdw/schema` | Default FDW schema |

## Secrets Manager

| Secret | Purpose |
|---|---|
| `nexus-ai/{env}/openai-api-key` | OpenAI API key for embeddings + chat completions |
| `nexus-ai/{env}/cognito-client-secret` | Cognito app client secret |
| `nexus-ai/{env}/fdw-credentials` | PostgreSQL FDW credentials |
| `nexus-ai/{env}/bssmagic-credentials` | BSSMagic CRM credentials (Salesforce TMF API) |
| `nexus-ai/{env}/api-keys` | Outbound integration API keys |

## Environment variables (backend pod)

| Variable | Required | Default | Description |
|---|---|---|---|
| `ENVIRONMENT` | yes | -- | `dev` / `stage` / `test` / `prod` |
| `AWS_REGION` | yes | -- | AWS region |
| `USE_LOCALSTACK` | no | `false` | LocalStack mode for development |
| `LOCALSTACK_HOST` | local-only | `localhost` | LocalStack host |
| `LOCALSTACK_PORT` | local-only | `4566` | LocalStack port |
| `FDW_PG_HOST` | yes (to enable) | -- | PostgreSQL host for FDW |
| `FDW_PG_PORT` | no | `5432` | PostgreSQL port |
| `FDW_PG_DATABASE` | yes | -- | Database name |
| `FDW_PG_USER` | yes | -- | DB user |
| `FDW_PG_PASSWORD` | yes | -- | DB password (or use secret) |
| `FDW_PG_SCHEMA` | no | `public` | Default schema |
| `FDW_PG_SSL_MODE` | no | `prefer` | SSL mode |
| `FDW_PG_POOL_MIN` | no | `2` | Connection-pool min |
| `FDW_PG_POOL_MAX` | no | `10` | Connection-pool max |
| `FDW_PG_QUERY_TIMEOUT` | no | `30` | Query timeout (s) |
| `OPENAI_API_KEY` | yes (or secret) | -- | OpenAI API key |
| `LLM_MODEL` | no | `gpt-4o-mini` | Reasoning Plane model |
| `EMBEDDING_MODEL` | no | `text-embedding-3-small` | Control Plane embedding model |
| `MAX_AGENT_STEPS` | no | `10` | ReAct step budget per session |
| `SIMULATOR_ENABLED` | no | `true` | Require remote nexus-simulator (fail-fast if URL missing) |
| `SIMULATOR_BASE_URL` | yes (when enabled) | -- | In-cluster simulator API, e.g. `http://simulator-{env}-backend-svc-internal.simulator-{env}.svc.cluster.local:8000` |
| `SIMULATOR_UI_URL` | no | `http://localhost:8082` | Browser link to the standalone simulator UI |

## CloudWatch log groups

| Log group | Purpose |
|---|---|
| `/aws/nexus-ai/{env}/backend` | Backend application logs |
| `/aws/nexus-ai/{env}/frontend` | Frontend nginx logs |
| `/aws/nexus-ai/{env}/operator` | Nexus Capability Operator logs |
| `/aws/nexus-ai/{env}/audit` | Mirrored audit log stream (also in DynamoDB) |

For log volume / cost analysis, see [CloudWatch Logs Analysis](cloudwatch-logs-analysis.md).
For DynamoDB throughput / cost analysis, see [DynamoDB Operations Analysis](dynamodb-operations-analysis.md).

## IAM (IRSA -- IAM Roles for Service Accounts)

The Operator creates one IAM role per pod with least-privilege policies. Backend pods need:

- `dynamodb:*` on the four `nexus-ai-{env}-*` tables and `control-plane-audit`.
- `s3:GetObject` / `PutObject` / `ListBucket` on the three `nexus-ai-{env}-*` buckets.
- `ssm:GetParameter` / `GetParametersByPath` on `/nexus-ai/{env}/*`.
- `secretsmanager:GetSecretValue` on `nexus-ai/{env}/*`.
- `cognito-idp:DescribeUserPool` (if Cognito integration enabled).

## Networking

- VPC with at least 2 public + 2 private subnets across 2 AZs.
- Internal ALB with path-based routing: `/` -> frontend pod, `/api/` -> backend pod.
- ACM TLS certificate for the ALB hostname (issued in `us-east-1` for CloudFront, in the deployment region for ALB).
- NAT Gateway (or VPC endpoints) for outbound calls (OpenAI, source-system FDW, Cognito).

## Sizing reference (production)

| Resource | Reference values |
|---|---|
| Backend pods | 3 replicas, 2 vCPU + 4 GB each |
| Frontend pods | 3 replicas, 0.5 vCPU + 0.5 GB each |
| BSSMagic StatefulSet | 1 replica, 4 vCPU + 16 GB, 100 GB EBS |
| EKS node group | 3+ m5.xlarge in 2 AZs |
| DynamoDB | On-demand or provisioned 200 RCU + 200 WCU base, GSI 100 + 100 |
| S3 lifecycle | 30 days hot -> 90 days IA -> Glacier (configurable per bucket) |

For per-Solution resource sizing guidance, see the per-vertical pages in the [Application Catalogue](../app-catalogue/supply-chain/index.md).

## Related references

- [Solution Architecture](solution-architecture.md) -- system design and deployment topology.
- [Operations > Kubernetes Operator](../operational/kubernetes-operator/index.md) -- the Operator that creates these resources.
- [Implementation Guide](../ai-os/implementation-guide.md) -- production code mapping.
- [DynamoDB Operations Analysis](dynamodb-operations-analysis.md) -- throughput and cost.
- [CloudWatch Logs Analysis](cloudwatch-logs-analysis.md) -- log volumes and retention.
