# Call Processing Capability - Infrastructure Requirements

This document lists all environment variables, secrets, DynamoDB tables, and S3 buckets required for the **nexus-ai** capability (nexus-backend service + UI).

---

## Naming Convention

All resources follow the `capability-env-name` naming convention.

### SSM Parameters & Secrets

```
/nexus-ai/{env}/{category}/{resource}
```

### AWS Resources (DynamoDB, S3, etc.)

```
nexus-ai-{env}-{resource-name}
```

### Components

| Component | Description | Values |
|-----------|-------------|--------|
| `nexus-ai` | Capability name (fixed) | `nexus-ai` |
| `{env}` | Environment | `dev`, `stage`, `test`, `prod` |
| `{category}` | Resource category (SSM/Secrets) | `aws`, `server`, `cognito`, `wxcc`, `s3`, `glue`, `cloudwatch`, `license`, `ui-dev` |
| `{resource-name}` | AWS resource name | e.g., `transformation-system`, `call-data`, `license` |

### Examples by Environment

| Resource Type | Pattern | Example (prod) |
|---------------|---------|----------------|
| SSM Parameter | `/nexus-ai/{env}/server/log-level` | `/nexus-ai/prod/server/log-level` |
| Secret | `nexus-ai/{env}/api-keys` | `nexus-ai/prod/api-keys` |
| DynamoDB Table | `nexus-ai-{env}-{name}` | `nexus-ai-prod-transformation-system` |
| S3 Bucket | `nexus-ai-{env}-{name}` | `nexus-ai-prod-call-data` |
| CloudWatch Log Group | `/aws/nexus-ai/{env}` | `/aws/nexus-ai/prod` |

### Environment Variable

The ECS task definition includes an `ENVIRONMENT` variable (e.g., `dev`, `stage`, `test`, `prod`) that the service uses to construct the correct resource names at runtime.

---

## DynamoDB Tables

Table names follow the `nexus-ai-{env}-{name}` convention:

| Table Name Pattern | Example (prod) | Purpose | Key Schema | GSIs |
|--------------------|----------------|---------|------------|------|
| `nexus-ai-{env}-transformation-system` | `nexus-ai-prod-transformation-system` | Journey/Stage/Job state management | PK (HASH), SK (RANGE) | GSI1 (GSI1PK, GSI1SK) |
| `nexus-ai-{env}-license` | `nexus-ai-prod-license` | License records + audit logs | PK (HASH), SK (RANGE) | status-index, holder-index, license-index |
| `nexus-ai-{env}-wxcc-task-tracking` | `nexus-ai-prod-wxcc-task-tracking` | WXCC task tracking | task_id (HASH) | - |

### Table Schemas

#### nexus-ai-{env}-transformation-system
```
PK: "JOURNEY#<id>" | "JOB#<id>" | "STAGE#<id>"
SK: "METADATA" | "STATUS" | "STAGE#<n>"
GSI1PK: For alternate access patterns
GSI1SK: For sorting
```

#### nexus-ai-{env}-license
```
License Records:
  PK: "INSTANCE#<instance_id>"
  SK: "LICENSE#<license_id>"

Audit Logs:
  PK: "AUDIT#<YYYY-MM>"
  SK: "<timestamp>#<event_id>"
```

---

## S3 Buckets

Bucket names follow the `nexus-ai-{env}-{name}` convention:

| Bucket Name Pattern | Example (prod) | Purpose | Required | Env Variable |
|---------------------|----------------|---------|----------|--------------|
| `nexus-ai-{env}-call-data` | `nexus-ai-prod-call-data` | Processed call data for Glue tables | Yes | `S3_RECORDINGS_BUCKET` |
| `nexus-ai-{env}-wxcc-simulator` | `nexus-ai-prod-wxcc-simulator` | WXCC simulator data | Yes | `WXCC_SIMULATOR_BUCKET` |
| `nexus-ai-{env}-journey-logs` | `nexus-ai-prod-journey-logs` | Journey execution logs | Yes | `S3_JOURNEY_LOGS_BUCKET` |
| `nexus-ai-{env}-journey-reports` | `nexus-ai-prod-journey-reports` | Journey reports and artifacts | Yes | `S3_JOURNEY_REPORTS_BUCKET` |
| `nexus-ai-{env}-journey-specs` | `nexus-ai-prod-journey-specs` | Journey specifications (UI development) | Optional | `S3_JOURNEY_SPECS_BUCKET` |

### S3 Bucket Structure

#### nexus-ai-{env}-call-data
```
nexus-ai-{env}-call-data/
├── call-data/                    # Glue table data (Parquet)
│   └── year=YYYY/month=MM/day=DD/
│       └── *.parquet
├── call-detail/                  # Raw call details JSON
│   └── {task_id}/
│       └── call_details.json
├── recordings/                   # Call recordings (WAV/MP3)
│   └── {task_id}/
│       └── recording.wav
├── transcripts/                  # Transcription results
│   └── {task_id}/
│       └── transcript.json
└── athena-results/               # Athena query results
    └── *.csv
```

#### nexus-ai-{env}-wxcc-simulator
```
nexus-ai-{env}-wxcc-simulator/
├── wxcc-simulator/
│   ├── tasks/                    # Simulated WXCC tasks
│   ├── recordings/               # Task recordings
│   └── sample-recordings/        # Sample recordings for seeding
```

---

## Comprehensive Environment Variables & Secrets

### 1. AWS Core Configuration

The service uses boto3's default credential chain:
- **ECS**: IAM task role (automatic via instance metadata) - no credentials needed
- **Local**: `~/.aws/credentials` (via `aws-login.sh` or AWS CLI) - no env vars needed
- **LocalStack**: Dummy credentials auto-provided when `USE_LOCALSTACK=true`

| Variable | Description | Default | Required | Store In |
|----------|-------------|---------|----------|----------|
| `AWS_REGION` | AWS region for services | `ap-southeast-1` | Yes | SSM Parameter |

#### Optional (rarely needed)

| Variable | Description | When Needed |
|----------|-------------|-------------|
| `AWS_ROLE_ARN` | IAM role ARN | Only if using cross-account role assumption |
| `AWS_PROFILE` | AWS CLI profile | Local dev with multiple profiles |
| `AWS_ACCESS_KEY_ID` | Access key | **Never in ECS** - only CI/CD pipelines |
| `AWS_SECRET_ACCESS_KEY` | Secret key | **Never in ECS** - only CI/CD pipelines |

> **Note**: On ECS, credentials are provided by the task IAM role. Do NOT set `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` in ECS task definitions.

### 2. Gateway & Server Configuration

| Variable | Description | Default | Store In |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Deployment environment | `development` | SSM Parameter |
| `LOG_LEVEL` | Logging verbosity | `INFO` | SSM Parameter |
| `API_KEY` | Gateway API key for auth | `super-secret` | Secrets Manager |
| `GATEWAY_PORT` | HTTP gateway port | `8000` | SSM Parameter |
| `MIN_WORKERS` | Minimum worker pool size | `2` | SSM Parameter |
| `MAX_WORKERS` | Maximum worker pool size | `8` | SSM Parameter |
| `MCP_REQUEST_TIMEOUT` | Request timeout in seconds | `60.0` | SSM Parameter |

### 3. WXCC Simulator Configuration

| Variable | Description | Default Pattern | Store In |
|----------|-------------|-----------------|----------|
| `WXCC_SIMULATOR_ENABLED` | Enable/disable simulator | `true` | SSM Parameter |
| `WXCC_SIMULATOR_BUCKET` | S3 bucket for simulator data | `nexus-ai-{env}-wxcc-simulator` | SSM Parameter |
| `WXCC_SIMULATOR_PREFIX` | S3 prefix for simulator | `wxcc-simulator` | SSM Parameter |
| `WXCC_SIMULATOR_BASE_URL` | Base URL for recordings | `http://localhost:8000` | SSM Parameter |
| `WXCC_SIM_ORG_ID` | Simulated organization ID | `sim-org-001` | SSM Parameter |
| `WXCC_SIM_TOKEN` | Simulator auth token | `test-token-12345` | Secrets Manager |

### 4. Call Processing Configuration

| Variable | Description | Default Pattern | Store In |
|----------|-------------|-----------------|----------|
| `S3_RECORDINGS_BUCKET` | S3 bucket for call data & Glue tables | `nexus-ai-{env}-call-data` | SSM Parameter |
| `S3_JOURNEY_LOGS_BUCKET` | S3 bucket for journey logs | `nexus-ai-{env}-journey-logs` | SSM Parameter |
| `S3_JOURNEY_REPORTS_BUCKET` | S3 bucket for journey reports | `nexus-ai-{env}-journey-reports` | SSM Parameter |
| `GLUE_DATABASE_NAME` | AWS Glue database name | `nexus-ai-{env}-analytics` | SSM Parameter |
| `GLUE_TABLE_NAME` | AWS Glue table name | `wxcc_calls` | SSM Parameter |
| `DYNAMODB_TABLE` | DynamoDB transformation system table | `nexus-ai-{env}-transformation-system` | SSM Parameter |
| `LICENSE_TABLE` | DynamoDB license table | `nexus-ai-{env}-license` | SSM Parameter |
| `WXCC_TASK_TABLE` | DynamoDB WXCC task tracking table | `nexus-ai-{env}-wxcc-task-tracking` | SSM Parameter |
| `OPENAI_API_KEY` | OpenAI API key for transcription | - | Secrets Manager |

### 5. Cognito Authentication

| Variable | Description | Default | Store In |
|----------|-------------|---------|----------|
| `COGNITO_REGION` | Cognito region | `ap-southeast-1` | SSM Parameter |
| `COGNITO_USER_POOL_ID` | Cognito User Pool ID | `ap-southeast-1_hUa7fsNkd` | SSM Parameter |
| `COGNITO_APP_CLIENT_ID` | Cognito App Client ID | - | SSM Parameter |

### 6. License Management

| Variable | Description | Default | Store In |
|----------|-------------|---------|----------|
| `LICENSE_PUBLIC_KEY` | License verification public key (PEM) | embedded | Secrets Manager |
| `LICENSE_PUBLIC_KEY_FILE` | Path to public key file | - | SSM Parameter |
| `LICENSE_PRIVATE_KEY` | License signing private key (PEM) | embedded | Secrets Manager |
| `INSTANCE_ID` | Unique instance identifier | auto-generated | SSM Parameter |

### 7. CloudWatch Logging

| Variable | Description | Default | Store In |
|----------|-------------|---------|----------|
| `CLOUDWATCH_LOG_GROUP` | CloudWatch log group | `/aws/nexus-ai/default` | SSM Parameter |
| `CLOUDWATCH_LOG_STREAM_PREFIX` | Log stream prefix | `script` | SSM Parameter |
| `ENABLE_CLOUDWATCH_LOGS` | Force enable CloudWatch | `false` | SSM Parameter |
| `ECS_CONTAINER_METADATA_URI` | ECS metadata (auto-set by ECS) | - | - |

### 8. UI Development Stage (Optional)

| Variable | Description | Default | Store In |
|----------|-------------|---------|----------|
| `CLAUDE_API_KEY` | Anthropic Claude API key | - | Secrets Manager |
| `ANTHROPIC_API_KEY` | Anthropic API key (alternate) | - | Secrets Manager |
| `CLAUDE_MODEL` | Claude model to use | - | SSM Parameter |
| `GITHUB_TOKEN` | GitHub personal access token | - | Secrets Manager |
| `AWS_ACCOUNT_ID` | AWS account ID | - | SSM Parameter |
| `AWS_DEPLOYMENT_ROLE` | Deployment IAM role | - | SSM Parameter |

### 9. LocalStack (Local Development Only)

When running locally with LocalStack, set these in `.env` file (not SSM):

| Variable | Description | Default |
|----------|-------------|---------|
| `USE_LOCALSTACK` | Enable LocalStack mode | `false` |
| `LOCALSTACK_HOST` | LocalStack hostname | `localhost` |
| `LOCALSTACK_PORT` | LocalStack port | `4566` |
| `AWS_ENDPOINT_URL` | Override endpoint for all services | - |
| `AWS_ENDPOINT_URL_DYNAMODB` | Override DynamoDB endpoint | - |
| `DYNAMODB_ENDPOINT_URL` | DynamoDB endpoint (alternate) | - |

> **Note**: When `USE_LOCALSTACK=true`, credentials auto-default to `test/test`. No need to set `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`.

### 10. Data & File Paths

| Variable | Description | Default | Store In |
|----------|-------------|---------|----------|
| `LOG_FILES_PATH` | Local log files path | `./data/logs` | SSM Parameter |
| `METRICS_DB_HOST` | Metrics database host | `localhost` | SSM Parameter |
| `METRICS_DB_PORT` | Metrics database port | `5432` | SSM Parameter |

### 11. Testing Variables (Test Environment Only)

| Variable | Description | Default |
|----------|-------------|---------|
| `TEST_BASE_URL` | Test server base URL | - |
| `SERVER_URL` | Server URL for tests | `http://localhost:8000` |
| `TEST_TIMEOUT` | Test timeout seconds | `30` |
| `USE_MOCK_AWS` | Use mocked AWS | `true` |
| `USE_DOCKER_COMPOSE` | Use Docker Compose | `false` |
| `MCP_GATEWAY_URL` | MCP gateway URL for tests | `http://localhost:8765` |
| `MCP_API_KEY` | MCP API key for tests | `test-api-key` |
| `DYNAMODB_TABLE` | DynamoDB table for tests | `aurorastack-transformation-jobs` |
| `TEST_JOURNEY_ID` | Test journey ID | `JRN-TEST-001` |
| `TEST_JOB_ID` | Test job ID | `JOB-TEST-001` |

---

## Summary: Recommended AWS Configuration

### Secrets Manager (Sensitive) - 6 secrets

Secret names follow the `capability/env/resource` convention:

| Secret Name Pattern | Variables | Example (prod) |
|---------------------|-----------|----------------|
| `nexus-ai/{env}/api-keys` | `API_KEY` | `nexus-ai/prod/api-keys` |
| `nexus-ai/{env}/wxcc` | `WXCC_SIM_TOKEN` | `nexus-ai/prod/wxcc` |
| `nexus-ai/{env}/openai` | `OPENAI_API_KEY` | `nexus-ai/prod/openai` |
| `nexus-ai/{env}/license` | `LICENSE_PUBLIC_KEY`, `LICENSE_PRIVATE_KEY` | `nexus-ai/prod/license` |
| `nexus-ai/{env}/anthropic` | `CLAUDE_API_KEY`, `ANTHROPIC_API_KEY` | `nexus-ai/prod/anthropic` |
| `nexus-ai/{env}/github` | `GITHUB_TOKEN` | `nexus-ai/prod/github` |

Where `{env}` is one of: `dev`, `stage`, `test`, `prod`

> **Note**: AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) are NOT stored in Secrets Manager. On ECS, use IAM task roles instead.

### SSM Parameter Store (Configuration) - 35+ parameters

Parameter paths follow the `capability/env/resource` convention:

| Parameter Path Pattern | Variables | Example (prod) |
|------------------------|-----------|----------------|
| `/nexus-ai/{env}/aws/region` | `AWS_REGION` | `/nexus-ai/prod/aws/region` |
| `/nexus-ai/{env}/aws/role-arn` | `AWS_ROLE_ARN` | `/nexus-ai/prod/aws/role-arn` |
| `/nexus-ai/{env}/server/environment` | `ENVIRONMENT` | `/nexus-ai/prod/server/environment` |
| `/nexus-ai/{env}/server/log-level` | `LOG_LEVEL` | `/nexus-ai/prod/server/log-level` |
| `/nexus-ai/{env}/server/min-workers` | `MIN_WORKERS` | `/nexus-ai/prod/server/min-workers` |
| `/nexus-ai/{env}/server/max-workers` | `MAX_WORKERS` | `/nexus-ai/prod/server/max-workers` |
| `/nexus-ai/{env}/server/timeout` | `MCP_REQUEST_TIMEOUT` | `/nexus-ai/prod/server/timeout` |
| `/nexus-ai/{env}/cognito/region` | `COGNITO_REGION` | `/nexus-ai/prod/cognito/region` |
| `/nexus-ai/{env}/cognito/user-pool-id` | `COGNITO_USER_POOL_ID` | `/nexus-ai/prod/cognito/user-pool-id` |
| `/nexus-ai/{env}/cognito/app-client-id` | `COGNITO_APP_CLIENT_ID` | `/nexus-ai/prod/cognito/app-client-id` |
| `/nexus-ai/{env}/wxcc/enabled` | `WXCC_SIMULATOR_ENABLED` | `/nexus-ai/prod/wxcc/enabled` |
| `/nexus-ai/{env}/wxcc/bucket` | `WXCC_SIMULATOR_BUCKET` | `/nexus-ai/prod/wxcc/bucket` |
| `/nexus-ai/{env}/wxcc/prefix` | `WXCC_SIMULATOR_PREFIX` | `/nexus-ai/prod/wxcc/prefix` |
| `/nexus-ai/{env}/wxcc/org-id` | `WXCC_SIM_ORG_ID` | `/nexus-ai/prod/wxcc/org-id` |
| `/nexus-ai/{env}/s3/recordings-bucket` | `S3_RECORDINGS_BUCKET` | `/nexus-ai/prod/s3/recordings-bucket` |
| `/nexus-ai/{env}/s3/journey-logs-bucket` | `S3_JOURNEY_LOGS_BUCKET` | `/nexus-ai/prod/s3/journey-logs-bucket` |
| `/nexus-ai/{env}/s3/journey-reports-bucket` | `S3_JOURNEY_REPORTS_BUCKET` | `/nexus-ai/prod/s3/journey-reports-bucket` |
| `/nexus-ai/{env}/dynamodb/transformation-table` | `DYNAMODB_TABLE` | `/nexus-ai/prod/dynamodb/transformation-table` |
| `/nexus-ai/{env}/dynamodb/license-table` | `LICENSE_TABLE` | `/nexus-ai/prod/dynamodb/license-table` |
| `/nexus-ai/{env}/dynamodb/wxcc-task-table` | `WXCC_TASK_TABLE` | `/nexus-ai/prod/dynamodb/wxcc-task-table` |
| `/nexus-ai/{env}/glue/database` | `GLUE_DATABASE_NAME` | `/nexus-ai/prod/glue/database` |
| `/nexus-ai/{env}/glue/table` | `GLUE_TABLE_NAME` | `/nexus-ai/prod/glue/table` |
| `/nexus-ai/{env}/cloudwatch/log-group` | `CLOUDWATCH_LOG_GROUP` | `/nexus-ai/prod/cloudwatch/log-group` |
| `/nexus-ai/{env}/cloudwatch/stream-prefix` | `CLOUDWATCH_LOG_STREAM_PREFIX` | `/nexus-ai/prod/cloudwatch/stream-prefix` |

Where `{env}` is one of: `dev`, `stage`, `test`, `prod`

---

## IAM Permissions Required

### DynamoDB

Resources use pattern: `nexus-ai-{env}-*`

```json
{
  "Action": [
    "dynamodb:GetItem",
    "dynamodb:PutItem",
    "dynamodb:UpdateItem",
    "dynamodb:DeleteItem",
    "dynamodb:Query",
    "dynamodb:Scan",
    "dynamodb:BatchGetItem",
    "dynamodb:BatchWriteItem",
    "dynamodb:DescribeTable"
  ],
  "Resource": [
    "arn:aws:dynamodb:REGION:ACCOUNT:table/nexus-ai-*",
    "arn:aws:dynamodb:REGION:ACCOUNT:table/nexus-ai-*/index/*"
  ]
}
```

> **Note**: Wildcard `nexus-ai-*` covers all environments and tables (e.g., `nexus-ai-prod-transformation-system`, `nexus-ai-dev-license`)

### S3

Resources use pattern: `nexus-ai-{env}-*`

```json
{
  "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "s3:DeleteObject",
    "s3:ListBucket",
    "s3:GetBucketLocation"
  ],
  "Resource": [
    "arn:aws:s3:::nexus-ai-*",
    "arn:aws:s3:::nexus-ai-*/*"
  ]
}
```

> **Note**: Wildcard `nexus-ai-*` covers all environments and buckets (e.g., `nexus-ai-prod-call-data`, `nexus-ai-dev-wxcc-simulator`)

### CloudWatch Logs
```json
{
  "Action": [
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents",
    "logs:DescribeLogStreams"
  ],
  "Resource": "arn:aws:logs:REGION:ACCOUNT:log-group:/aws/nexus-ai/*"
}
```

### SSM Parameter Store
```json
{
  "Action": [
    "ssm:GetParameter",
    "ssm:GetParameters",
    "ssm:GetParametersByPath"
  ],
  "Resource": "arn:aws:ssm:REGION:ACCOUNT:parameter/nexus-ai/*"
}
```

> **Note**: The wildcard `*` covers all environments (`/nexus-ai/dev/*`, `/nexus-ai/prod/*`, etc.)

### Secrets Manager
```json
{
  "Action": [
    "secretsmanager:GetSecretValue",
    "secretsmanager:DescribeSecret"
  ],
  "Resource": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:nexus-ai/*"
}
```

> **Note**: The wildcard `*` covers all environments (`nexus-ai/dev/*`, `nexus-ai/prod/*`, etc.)

### Glue/Athena (for Call Processing)
```json
{
  "Action": [
    "glue:GetDatabase",
    "glue:GetTable",
    "glue:GetPartitions",
    "athena:StartQueryExecution",
    "athena:GetQueryExecution",
    "athena:GetQueryResults"
  ],
  "Resource": "*"
}
```

---

## Quick Reference - Minimum Required for Production

### ECS Task Definition Environment Variable

The ECS task definition must set the `ENVIRONMENT` variable to tell the service which parameter/secret paths to use:

```bash
ENVIRONMENT=prod  # or: dev, stage, test
```

### SSM Parameters to Create (for prod)

```bash
# AWS
/nexus-ai/prod/aws/region=ap-southeast-1

# Server
/nexus-ai/prod/server/environment=production
/nexus-ai/prod/server/log-level=INFO

# Cognito
/nexus-ai/prod/cognito/region=ap-southeast-1
/nexus-ai/prod/cognito/user-pool-id=<user-pool-id>
/nexus-ai/prod/cognito/app-client-id=<app-client-id>

# S3 Buckets (values are the actual bucket names)
/nexus-ai/prod/s3/recordings-bucket=nexus-ai-prod-call-data
/nexus-ai/prod/s3/journey-logs-bucket=nexus-ai-prod-journey-logs
/nexus-ai/prod/s3/journey-reports-bucket=nexus-ai-prod-journey-reports

# DynamoDB Tables (values are the actual table names)
/nexus-ai/prod/dynamodb/transformation-table=nexus-ai-prod-transformation-system
/nexus-ai/prod/dynamodb/license-table=nexus-ai-prod-license
/nexus-ai/prod/dynamodb/wxcc-task-table=nexus-ai-prod-wxcc-task-tracking

# Glue
/nexus-ai/prod/glue/database=nexus-ai-prod-analytics
/nexus-ai/prod/glue/table=wxcc_calls

# WXCC Simulator
/nexus-ai/prod/wxcc/bucket=nexus-ai-prod-wxcc-simulator
```

### Secrets to Create (for prod)

```bash
nexus-ai/prod/api-keys     # Contains: API_KEY
nexus-ai/prod/openai       # Contains: OPENAI_API_KEY
nexus-ai/prod/license      # Contains: LICENSE_PUBLIC_KEY, LICENSE_PRIVATE_KEY
```

### DynamoDB Tables (Required for prod)
- `nexus-ai-prod-transformation-system`
- `nexus-ai-prod-license`
- `nexus-ai-prod-wxcc-task-tracking`

### S3 Buckets (Required for prod)
- `nexus-ai-prod-call-data` (call data & Glue tables)
- `nexus-ai-prod-wxcc-simulator` (simulator data)
- `nexus-ai-prod-journey-logs`
- `nexus-ai-prod-journey-reports`

---

## Variable Count Summary

| Category | Count |
|----------|-------|
| AWS Core | 5 |
| Gateway & Server | 7 |
| WXCC Simulator | 6 |
| Call Processing (S3, DynamoDB, Glue) | 9 |
| Cognito Auth | 3 |
| License Management | 4 |
| CloudWatch | 4 |
| UI Development | 6 |
| LocalStack | 6 |
| Data & Paths | 3 |
| Testing | 10 |
| **Total** | **63** |

| Storage | Count |
|---------|-------|
| Secrets Manager | 6 secrets |
| SSM Parameter Store | ~40 parameters |
| Auto/Runtime | ~17 variables |

---

*Last Updated: December 29, 2025*
