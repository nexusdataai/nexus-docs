# Call Processing Capability - Infrastructure Requirements

This document lists all environment variables, secrets, DynamoDB tables, and S3 buckets required for the **call-processing** capability (starhub-backend service + UI).

---

## Naming Convention

All resources follow the `capability-env-name` naming convention.

### SSM Parameters & Secrets

```
/call-processing/{env}/{category}/{resource}
```

### AWS Resources (DynamoDB, S3, etc.)

```
call-processing-{env}-{resource-name}
```

### Components

| Component | Description | Values |
|-----------|-------------|--------|
| `call-processing` | Capability name (fixed) | `call-processing` |
| `{env}` | Environment | `dev`, `stage`, `test`, `prod` |
| `{category}` | Resource category (SSM/Secrets) | `aws`, `server`, `cognito`, `wxcc`, `s3`, `glue`, `cloudwatch`, `license`, `ui-dev` |
| `{resource-name}` | AWS resource name | e.g., `transformation-system`, `call-data`, `license` |

### Examples by Environment

| Resource Type | Pattern | Example (prod) |
|---------------|---------|----------------|
| SSM Parameter | `/call-processing/{env}/server/log-level` | `/call-processing/prod/server/log-level` |
| Secret | `call-processing/{env}/api-keys` | `call-processing/prod/api-keys` |
| DynamoDB Table | `call-processing-{env}-{name}` | `call-processing-prod-transformation-system` |
| S3 Bucket | `call-processing-{env}-{name}` | `call-processing-prod-call-data` |
| CloudWatch Log Group | `/aws/call-processing/{env}` | `/aws/call-processing/prod` |

### Environment Variable

The ECS task definition includes an `ENVIRONMENT` variable (e.g., `dev`, `stage`, `test`, `prod`) that the service uses to construct the correct resource names at runtime.

---

## DynamoDB Tables

Table names follow the `call-processing-{env}-{name}` convention:

| Table Name Pattern | Example (prod) | Purpose | Key Schema | GSIs |
|--------------------|----------------|---------|------------|------|
| `call-processing-{env}-transformation-system` | `call-processing-prod-transformation-system` | Journey/Stage/Job state management | PK (HASH), SK (RANGE) | GSI1 (GSI1PK, GSI1SK) |
| `call-processing-{env}-license` | `call-processing-prod-license` | License records + audit logs | PK (HASH), SK (RANGE) | status-index, holder-index, license-index |
| `call-processing-{env}-wxcc-task-tracking` | `call-processing-prod-wxcc-task-tracking` | WXCC task tracking | task_id (HASH) | - |

### Table Schemas

#### call-processing-{env}-transformation-system
```
PK: "JOURNEY#<id>" | "JOB#<id>" | "STAGE#<id>"
SK: "METADATA" | "STATUS" | "STAGE#<n>"
GSI1PK: For alternate access patterns
GSI1SK: For sorting
```

#### call-processing-{env}-license
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

Bucket names follow the `call-processing-{env}-{name}` convention:

| Bucket Name Pattern | Example (prod) | Purpose | Required | Env Variable |
|---------------------|----------------|---------|----------|--------------|
| `call-processing-{env}-call-data` | `call-processing-prod-call-data` | Processed call data for Glue tables | Yes | `S3_RECORDINGS_BUCKET` |
| `call-processing-{env}-wxcc-simulator` | `call-processing-prod-wxcc-simulator` | WXCC simulator data | Yes | `WXCC_SIMULATOR_BUCKET` |
| `call-processing-{env}-journey-logs` | `call-processing-prod-journey-logs` | Journey execution logs | Yes | `S3_JOURNEY_LOGS_BUCKET` |
| `call-processing-{env}-journey-reports` | `call-processing-prod-journey-reports` | Journey reports and artifacts | Yes | `S3_JOURNEY_REPORTS_BUCKET` |
| `call-processing-{env}-journey-specs` | `call-processing-prod-journey-specs` | Journey specifications (UI development) | Optional | `S3_JOURNEY_SPECS_BUCKET` |

### S3 Bucket Structure

#### call-processing-{env}-call-data
```
call-processing-{env}-call-data/
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

#### call-processing-{env}-wxcc-simulator
```
call-processing-{env}-wxcc-simulator/
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
| `WXCC_SIMULATOR_BUCKET` | S3 bucket for simulator data | `call-processing-{env}-wxcc-simulator` | SSM Parameter |
| `WXCC_SIMULATOR_PREFIX` | S3 prefix for simulator | `wxcc-simulator` | SSM Parameter |
| `WXCC_SIMULATOR_BASE_URL` | Base URL for recordings | `http://localhost:8000` | SSM Parameter |
| `WXCC_SIM_ORG_ID` | Simulated organization ID | `sim-org-001` | SSM Parameter |
| `WXCC_SIM_TOKEN` | Simulator auth token | `test-token-12345` | Secrets Manager |

### 4. Call Processing Configuration

| Variable | Description | Default Pattern | Store In |
|----------|-------------|-----------------|----------|
| `S3_RECORDINGS_BUCKET` | S3 bucket for call data & Glue tables | `call-processing-{env}-call-data` | SSM Parameter |
| `S3_JOURNEY_LOGS_BUCKET` | S3 bucket for journey logs | `call-processing-{env}-journey-logs` | SSM Parameter |
| `S3_JOURNEY_REPORTS_BUCKET` | S3 bucket for journey reports | `call-processing-{env}-journey-reports` | SSM Parameter |
| `GLUE_DATABASE_NAME` | AWS Glue database name | `call-processing-{env}-analytics` | SSM Parameter |
| `GLUE_TABLE_NAME` | AWS Glue table name | `wxcc_calls` | SSM Parameter |
| `DYNAMODB_TABLE` | DynamoDB transformation system table | `call-processing-{env}-transformation-system` | SSM Parameter |
| `LICENSE_TABLE` | DynamoDB license table | `call-processing-{env}-license` | SSM Parameter |
| `WXCC_TASK_TABLE` | DynamoDB WXCC task tracking table | `call-processing-{env}-wxcc-task-tracking` | SSM Parameter |
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
| `CLOUDWATCH_LOG_GROUP` | CloudWatch log group | `/aws/call-processing/default` | SSM Parameter |
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
| `call-processing/{env}/api-keys` | `API_KEY` | `call-processing/prod/api-keys` |
| `call-processing/{env}/wxcc` | `WXCC_SIM_TOKEN` | `call-processing/prod/wxcc` |
| `call-processing/{env}/openai` | `OPENAI_API_KEY` | `call-processing/prod/openai` |
| `call-processing/{env}/license` | `LICENSE_PUBLIC_KEY`, `LICENSE_PRIVATE_KEY` | `call-processing/prod/license` |
| `call-processing/{env}/anthropic` | `CLAUDE_API_KEY`, `ANTHROPIC_API_KEY` | `call-processing/prod/anthropic` |
| `call-processing/{env}/github` | `GITHUB_TOKEN` | `call-processing/prod/github` |

Where `{env}` is one of: `dev`, `stage`, `test`, `prod`

> **Note**: AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) are NOT stored in Secrets Manager. On ECS, use IAM task roles instead.

### SSM Parameter Store (Configuration) - 35+ parameters

Parameter paths follow the `capability/env/resource` convention:

| Parameter Path Pattern | Variables | Example (prod) |
|------------------------|-----------|----------------|
| `/call-processing/{env}/aws/region` | `AWS_REGION` | `/call-processing/prod/aws/region` |
| `/call-processing/{env}/aws/role-arn` | `AWS_ROLE_ARN` | `/call-processing/prod/aws/role-arn` |
| `/call-processing/{env}/server/environment` | `ENVIRONMENT` | `/call-processing/prod/server/environment` |
| `/call-processing/{env}/server/log-level` | `LOG_LEVEL` | `/call-processing/prod/server/log-level` |
| `/call-processing/{env}/server/min-workers` | `MIN_WORKERS` | `/call-processing/prod/server/min-workers` |
| `/call-processing/{env}/server/max-workers` | `MAX_WORKERS` | `/call-processing/prod/server/max-workers` |
| `/call-processing/{env}/server/timeout` | `MCP_REQUEST_TIMEOUT` | `/call-processing/prod/server/timeout` |
| `/call-processing/{env}/cognito/region` | `COGNITO_REGION` | `/call-processing/prod/cognito/region` |
| `/call-processing/{env}/cognito/user-pool-id` | `COGNITO_USER_POOL_ID` | `/call-processing/prod/cognito/user-pool-id` |
| `/call-processing/{env}/cognito/app-client-id` | `COGNITO_APP_CLIENT_ID` | `/call-processing/prod/cognito/app-client-id` |
| `/call-processing/{env}/wxcc/enabled` | `WXCC_SIMULATOR_ENABLED` | `/call-processing/prod/wxcc/enabled` |
| `/call-processing/{env}/wxcc/bucket` | `WXCC_SIMULATOR_BUCKET` | `/call-processing/prod/wxcc/bucket` |
| `/call-processing/{env}/wxcc/prefix` | `WXCC_SIMULATOR_PREFIX` | `/call-processing/prod/wxcc/prefix` |
| `/call-processing/{env}/wxcc/org-id` | `WXCC_SIM_ORG_ID` | `/call-processing/prod/wxcc/org-id` |
| `/call-processing/{env}/s3/recordings-bucket` | `S3_RECORDINGS_BUCKET` | `/call-processing/prod/s3/recordings-bucket` |
| `/call-processing/{env}/s3/journey-logs-bucket` | `S3_JOURNEY_LOGS_BUCKET` | `/call-processing/prod/s3/journey-logs-bucket` |
| `/call-processing/{env}/s3/journey-reports-bucket` | `S3_JOURNEY_REPORTS_BUCKET` | `/call-processing/prod/s3/journey-reports-bucket` |
| `/call-processing/{env}/dynamodb/transformation-table` | `DYNAMODB_TABLE` | `/call-processing/prod/dynamodb/transformation-table` |
| `/call-processing/{env}/dynamodb/license-table` | `LICENSE_TABLE` | `/call-processing/prod/dynamodb/license-table` |
| `/call-processing/{env}/dynamodb/wxcc-task-table` | `WXCC_TASK_TABLE` | `/call-processing/prod/dynamodb/wxcc-task-table` |
| `/call-processing/{env}/glue/database` | `GLUE_DATABASE_NAME` | `/call-processing/prod/glue/database` |
| `/call-processing/{env}/glue/table` | `GLUE_TABLE_NAME` | `/call-processing/prod/glue/table` |
| `/call-processing/{env}/cloudwatch/log-group` | `CLOUDWATCH_LOG_GROUP` | `/call-processing/prod/cloudwatch/log-group` |
| `/call-processing/{env}/cloudwatch/stream-prefix` | `CLOUDWATCH_LOG_STREAM_PREFIX` | `/call-processing/prod/cloudwatch/stream-prefix` |

Where `{env}` is one of: `dev`, `stage`, `test`, `prod`

---

## IAM Permissions Required

### DynamoDB

Resources use pattern: `call-processing-{env}-*`

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
    "arn:aws:dynamodb:REGION:ACCOUNT:table/call-processing-*",
    "arn:aws:dynamodb:REGION:ACCOUNT:table/call-processing-*/index/*"
  ]
}
```

> **Note**: Wildcard `call-processing-*` covers all environments and tables (e.g., `call-processing-prod-transformation-system`, `call-processing-dev-license`)

### S3

Resources use pattern: `call-processing-{env}-*`

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
    "arn:aws:s3:::call-processing-*",
    "arn:aws:s3:::call-processing-*/*"
  ]
}
```

> **Note**: Wildcard `call-processing-*` covers all environments and buckets (e.g., `call-processing-prod-call-data`, `call-processing-dev-wxcc-simulator`)

### CloudWatch Logs
```json
{
  "Action": [
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents",
    "logs:DescribeLogStreams"
  ],
  "Resource": "arn:aws:logs:REGION:ACCOUNT:log-group:/aws/call-processing/*"
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
  "Resource": "arn:aws:ssm:REGION:ACCOUNT:parameter/call-processing/*"
}
```

> **Note**: The wildcard `*` covers all environments (`/call-processing/dev/*`, `/call-processing/prod/*`, etc.)

### Secrets Manager
```json
{
  "Action": [
    "secretsmanager:GetSecretValue",
    "secretsmanager:DescribeSecret"
  ],
  "Resource": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:call-processing/*"
}
```

> **Note**: The wildcard `*` covers all environments (`call-processing/dev/*`, `call-processing/prod/*`, etc.)

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
/call-processing/prod/aws/region=ap-southeast-1

# Server
/call-processing/prod/server/environment=production
/call-processing/prod/server/log-level=INFO

# Cognito
/call-processing/prod/cognito/region=ap-southeast-1
/call-processing/prod/cognito/user-pool-id=<user-pool-id>
/call-processing/prod/cognito/app-client-id=<app-client-id>

# S3 Buckets (values are the actual bucket names)
/call-processing/prod/s3/recordings-bucket=call-processing-prod-call-data
/call-processing/prod/s3/journey-logs-bucket=call-processing-prod-journey-logs
/call-processing/prod/s3/journey-reports-bucket=call-processing-prod-journey-reports

# DynamoDB Tables (values are the actual table names)
/call-processing/prod/dynamodb/transformation-table=call-processing-prod-transformation-system
/call-processing/prod/dynamodb/license-table=call-processing-prod-license
/call-processing/prod/dynamodb/wxcc-task-table=call-processing-prod-wxcc-task-tracking

# Glue
/call-processing/prod/glue/database=call-processing-prod-analytics
/call-processing/prod/glue/table=wxcc_calls

# WXCC Simulator
/call-processing/prod/wxcc/bucket=call-processing-prod-wxcc-simulator
```

### Secrets to Create (for prod)

```bash
call-processing/prod/api-keys     # Contains: API_KEY
call-processing/prod/openai       # Contains: OPENAI_API_KEY
call-processing/prod/license      # Contains: LICENSE_PUBLIC_KEY, LICENSE_PRIVATE_KEY
```

### DynamoDB Tables (Required for prod)
- `call-processing-prod-transformation-system`
- `call-processing-prod-license`
- `call-processing-prod-wxcc-task-tracking`

### S3 Buckets (Required for prod)
- `call-processing-prod-call-data` (call data & Glue tables)
- `call-processing-prod-wxcc-simulator` (simulator data)
- `call-processing-prod-journey-logs`
- `call-processing-prod-journey-reports`

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
