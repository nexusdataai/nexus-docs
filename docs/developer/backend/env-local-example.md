# Environment Configuration for Local Development

Copy the configuration below to `.env.local` in the project root.

```bash
# =============================================================================
# NexusAI Backend - Local Development Configuration
# =============================================================================
# This is the ONLY environment file needed for local development and LocalStack.
# On ECS, configuration is loaded from SSM Parameter Store and Secrets Manager.
#
# Naming Convention: nexus-ai-{env}-{resource-name}
# Example: nexus-ai-dev-transformation-system

# =============================================================================
# LOCALSTACK CONFIGURATION (Local AWS Emulation)
# =============================================================================
# Set USE_LOCALSTACK=true to use LocalStack instead of real AWS services.
# This is useful for local development without AWS costs or credentials.

# Enable/disable LocalStack mode (true = LocalStack, false = Real AWS)
USE_LOCALSTACK=false

# LocalStack connection settings (only used when USE_LOCALSTACK=true)
LOCALSTACK_HOST=localhost
LOCALSTACK_PORT=4566

# =============================================================================
# ADFS / AWS Login Configuration
# =============================================================================
ADFS_HOST=adfs.devfactory.com/adfs/ls/idpinitiatedsignon
ADFS_PROVIDER_ID=urn:amazon:webservices
AWS_PROFILE=external-access
AD_USERNAME=devfactory\\your-username
AD_PASSWORD=your-password
SESSION_DURATION=3600
PRINT_CONSOLE_URL=true

# For automatic role selection, uncomment one:
# AWS_ROLE_ARN=arn:aws:iam::764119721991:role/RAM-AWS-Prod-TelcoDR-NexusAIPS-Admin

# =============================================================================
# Environment Configuration
# =============================================================================
ENVIRONMENT=dev
CAPABILITY_NAME=nexus-ai

# AWS Region
AWS_REGION=ap-southeast-1
AWS_DEFAULT_REGION=ap-southeast-1

# =============================================================================
# Webex OAuth Configuration
# =============================================================================
WEBEX_CLIENT_ID=your-webex-client-id
WEBEX_CLIENT_SECRET=your-webex-client-secret
WEBEX_REDIRECT_URI=https://trilogy.com

# =============================================================================
# Webex Contact Center Configuration
# =============================================================================
WXCC_ORG_ID=your-wxcc-org-id
WXCC_BASE_URL=https://api.wxcc-us1.cisco.com/v1

# =============================================================================
# DynamoDB Tables (nexus-ai-{env}-{table})
# =============================================================================
DYNAMODB_TABLE=nexus-ai-dev-transformation-system
LICENSE_TABLE=nexus-ai-dev-license
DYNAMODB_TRACKING_TABLE=nexus-ai-dev-wxcc-task-tracking
TASK_TRACKING_TTL_DAYS=30

# =============================================================================
# S3 Buckets (nexus-ai-{env}-{bucket})
# =============================================================================
S3_RECORDINGS_BUCKET=nexus-ai-dev-call-data
S3_JOURNEY_LOGS_BUCKET=nexus-ai-dev-journey-logs
S3_JOURNEY_REPORTS_BUCKET=nexus-ai-dev-journey-reports
WXCC_SIMULATOR_BUCKET=nexus-ai-dev-wxcc-simulator

# S3 prefixes
S3_RECORDINGS_PREFIX=call-detail/
S3_WXCC_DATA_PREFIX=call-data/

# =============================================================================
# AWS Glue Configuration (nexus-ai-{env}-{database})
# =============================================================================
GLUE_DATABASE_NAME=nexus-ai-dev-wxcc-analytics
GLUE_TABLE_NAME=calls

# =============================================================================
# OpenAI Configuration (for transcription and AI analysis)
# =============================================================================
OPENAI_API_KEY=sk-proj-your-openai-api-key
OPENAI_TRANSCRIPTION_MODEL=gpt-4o-transcribe
OPENAI_DIARIZATION_MODEL=gpt-4o-transcribe

# =============================================================================
# WXCC Simulator Configuration
# =============================================================================
WXCC_SIMULATOR_ENABLED=true
WXCC_SIMULATOR_PREFIX=wxcc-simulator
WXCC_SIMULATOR_BASE_URL=http://localhost:8000/api/v1/simulator
WXCC_SIM_TOKEN=test-token-12345
WXCC_SIM_ORG_ID=sim-org-001

# =============================================================================
# Gateway & Logging Configuration
# =============================================================================
LOG_LEVEL=INFO
API_KEY=super-secret
GATEWAY_PORT=8000

# Worker pool configuration
MIN_WORKERS=2
MAX_WORKERS=8

# Request timeout in seconds
MCP_REQUEST_TIMEOUT=300.0

# =============================================================================
# Cognito Configuration (Optional)
# =============================================================================
# COGNITO_REGION=ap-southeast-1
# COGNITO_USER_POOL_ID=
# COGNITO_APP_CLIENT_ID=

# =============================================================================
# CloudWatch Configuration (Optional)
# =============================================================================
# CLOUDWATCH_LOG_GROUP=/aws/nexus-ai/dev
# CLOUDWATCH_LOG_STREAM_PREFIX=script
```

## Quick Start

### For LocalStack (local AWS emulation):
```bash
USE_LOCALSTACK=true
LOCALSTACK_HOST=localhost
LOCALSTACK_PORT=4566
ENVIRONMENT=local
```

### For Real AWS:
```bash
USE_LOCALSTACK=false
AWS_PROFILE=external-access
AWS_REGION=ap-southeast-1
ENVIRONMENT=dev
```

## Sensitive Values to Update

After copying to `.env.local`, update these placeholders with your actual values:

| Variable | Description |
|----------|-------------|
| `AD_USERNAME` | Your DevFactory AD username |
| `AD_PASSWORD` | Your DevFactory AD password |
| `WEBEX_CLIENT_ID` | Webex OAuth client ID |
| `WEBEX_CLIENT_SECRET` | Webex OAuth client secret |
| `WXCC_ORG_ID` | Your Webex Contact Center org ID |
| `OPENAI_API_KEY` | Your OpenAI API key |
