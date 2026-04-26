# Platform Architecture

This page provides a comprehensive overview of the NexusAI Data Platform architecture, including high-level system design, deployment architecture, and data flow patterns.

---

## Overview

The NexusAI Data Platform is an enterprise-grade AI operating platform that delivers:

- **Modular AI capabilities** deployed into customer-owned cloud infrastructure
- **Real-time AI insights** on operational data, compliance, and performance
- **Multi-million dollar revenue impact** with measurable ROI
- **Automated quality assurance** and compliance monitoring
- **AI-powered analytics** with actionable recommendations
- **Enterprise system integration** (Salesforce, Office 365, Webex, and more)

---

## High-Level Architecture

<div style="min-height: 1200px; width: 100%; margin: 3em auto;">

```mermaid
graph TD
    A[NexusAI Data Platform] --> B[Backend Services]
    A --> C[UI Application]
    A --> D[Deployment Tools]
    
    B --> E[Call Processing]
    B --> F[AI Analysis]
    B --> G[Journey Management]
    B --> H[CRM Actions]
    
    C --> I[React Frontend]
    C --> J[User Dashboard]
    
    D --> K[AWS Deployment]
    D --> L[Infrastructure]
    
    H --> M[Salesforce Integration]
```

</div>

---

## System Architecture

<div style="min-height: 1400px; width: 100%; margin: 3em auto;">

```mermaid
graph TB
    subgraph UI["USER INTERFACES"]
        UI1[NexusAI UI<br/>Analytics Dashboard<br/>React + TypeScript<br/>Port: 5173]
        UI2[NexusAI Deployer<br/>Wizard Frontend<br/>React + TypeScript<br/>Port: 5173]
        UI3[Electron App<br/>Desktop Application<br/>Cross-platform]
    end
    
    subgraph Backend["BACKEND SERVICES"]
        BE1[NexusAI Backend<br/>Call Processing<br/>Python 3.11+ FastAPI<br/>MCP HTTP Gateway<br/>Port: 8000]
        BE2[Deployer Backend<br/>AWS Orchestration<br/>Python + FastAPI<br/>CloudFormation<br/>Port: 8001]
    end
    
    subgraph AWS["AWS INFRASTRUCTURE"]
        DB[(DynamoDB<br/>Tables)]
        S3[(S3<br/>Buckets)]
        ATH[Athena<br/>Queries]
        GLUE[Glue<br/>Catalog]
        CW[CloudWatch<br/>Logs/Metrics]
        COG[Cognito<br/>Auth]
        ECS[ECS<br/>Fargate]
        CF[CloudFront<br/>CDN]
        SM[Secrets<br/>Manager]
        SSM[SSM<br/>Parameters]
    end
    
    subgraph EXT["EXTERNAL INTEGRATIONS"]
        WX[Webex CC<br/>Contact Center]
        SF[Salesforce<br/>CRM]
        O365[Office 365<br/>Integration]
        AI[OpenAI<br/>GPT Analysis]
    end
    
    UI1 --> BE1
    UI2 --> BE2
    UI3 --> BE1
    UI3 --> BE2
    
    BE1 --> DB
    BE1 --> S3
    BE1 --> ATH
    BE1 --> GLUE
    BE1 --> CW
    BE1 --> COG
    BE1 --> ECS
    BE1 --> SM
    BE1 --> SSM
    
    BE2 --> CF
    BE2 --> S3
    
    BE1 --> WX
    BE1 --> SF
    BE1 --> O365
    BE1 --> AI
    
    style UI fill:#e3f2fd
    style Backend fill:#fff3e0
    style AWS fill:#f3e5f5
    style EXT fill:#e8f5e9
```

</div>

---

## Repository Structure

The platform consists of three primary repositories:

| Repository | Application | Purpose | Technology Stack |
|------------|-------------|---------|------------------|
| **nexus-ui** | NexusAI | Analytics Dashboard & Visualization | React 18, TypeScript, Vite, Tailwind CSS, Recharts |
| **nexus-backend** | NexusAI | Call Processing & MCP Server | Python 3.11+, FastAPI, boto3, MCP Protocol |
| **nexus-deployer** | NexusAI Toolkit | Deployment Wizard & AWS Orchestration | React + Python FastAPI + Electron |

### Repository Mapping

```
Application 1: NexusAI
├── nexus-ui (Frontend)
│   └── React-based analytics dashboard
└── nexus-backend (Backend)
    └── Python-based call processing engine

Application 2: NexusAI Toolkit
└── nexus-deployer (Complete Application)
    ├── Frontend (React wizard)
    ├── Backend (Python orchestrator)
    └── Desktop (Electron wrapper)
```

---

## Core Components

### NexusAI UI (Analytics Dashboard)

**Technology Stack:**
- **Frontend**: React 18, TypeScript, Vite
- **UI Components**: Radix UI, shadcn/ui, Tailwind CSS
- **Charts**: Recharts, Mapbox GL
- **State Management**: React Query, Context API
- **Authentication**: AWS Amplify, Cognito

**Key Features:**
- Call Analytics Dashboard with real-time metrics
- Journey Management and visualization
- WXCC Simulator interface
- AI Workspace for insights
- Tools Catalogue (Webex, Salesforce, O365 connectors)
- Processed Calls View with transcripts and analysis

**Component Structure:**
```
nexus-ui/src/
├── components/
│   ├── dashboards/          # Analytics dashboards
│   ├── journeys/            # Journey management UI
│   ├── processed-calls/     # Call analysis views
│   ├── wxcc-simulator/      # Simulator interface
│   ├── settings/            # Configuration panels
│   └── ui/                  # Reusable UI components
├── services/
│   ├── callProcessingJourneyService.ts
│   ├── transformationJourneyService.ts
│   ├── wxccSimulatorService.ts
│   ├── licenseService.ts
│   └── webexConnectorService.ts
├── context/
│   ├── AuthContext.tsx
│   ├── DashboardContext.tsx
│   └── EnterpriseAuthContext.tsx
└── types/
    ├── transformationJourney.ts
    ├── processedCalls.ts
    └── license.ts
```

---

### NexusAI Backend (Call Processing Engine)

**Technology Stack:**
- **Framework**: Python 3.11+, FastAPI
- **Protocol**: Model Context Protocol (MCP) with HTTP Gateway
- **AWS SDK**: boto3 for AWS service integration
- **AI**: OpenAI GPT for transcription and analysis

**MCP Tools:**
| Tool | Description |
|------|-------------|
| `journeys_tool` | Journey, stage, and job management |
| `logs_and_reports_tool` | Logs and report generation |
| `wxcc_simulator_tool` | WXCC simulator operations |
| `license_tool` | License activation and validation |

**REST APIs:**
| Endpoint | Description |
|----------|-------------|
| `/api/v1/journeys/*` | Journey management |
| `/api/v1/license/*` | License management |
| `/api/v1/simulator/*` | WXCC Simulator APIs |
| `/api/v1/analytics/*` | Analytics and metrics |
| `/api/v1/calls/*` | Processed calls data |
| `/health` | Health check |

**Call Processing Stages:**
1. **Fetch Tasks** - Retrieve tasks from Webex CC
2. **Deduplication** - Check for already-processed tasks
3. **Process Recordings** - Download, transcribe, upload
4. **Register Metadata** - Create metadata and Glue partitions
5. **AI Analysis** - GPT-powered call analysis

---

## ECS Fargate Deployment Architecture

<div style="min-height: 1300px; width: 100%; margin: 3em auto;">

```mermaid
graph TB
    APP[Application<br/>ALB Load Balancer]
    EB[EventBridge<br/>Event Triggers]
    
    subgraph FARGATE["ECS FARGATE"]
        subgraph CONN["CONNECTORS"]
            WC[Webex<br/>Connector]
            CSC[CloudSense<br/>Connector]
        end
        
        subgraph BATCH["BATCHES"]
            TG[Transcript<br/>Generator]
            CA[Call<br/>Analysis]
            CD[Call<br/>Diarization]
            SY[Synthesizer]
        end
        
        subgraph MCP["MCP TOOLS"]
            REP[Reporter]
            MON[Monitoring]
            DIAG[Diagnostics]
        end
        
        BS[Backend<br/>Services]
    end
    
    DB[(DynamoDB<br/>Tables)]
    ATH[Athena/S3<br/>Analytics]
    CW[CloudWatch<br/>Logs/Metrics]
    GLUE[Glue<br/>Catalog]
    
    APP --> EB
    EB --> BS
    
    BS --> WC
    BS --> CSC
    BS --> TG
    BS --> CA
    BS --> CD
    BS --> SY
    BS --> REP
    BS --> MON
    BS --> DIAG
    
    BS --> DB
    BS --> ATH
    BS --> CW
    BS --> GLUE
    
    style FARGATE fill:#ff9800,color:#fff
    style CONN fill:#e3f2fd
    style BATCH fill:#fff3e0
    style MCP fill:#fce4ec
    style APP fill:#4caf50,color:#fff
    style EB fill:#9c27b0,color:#fff
```

</div>

---

## Data Flow - Call Processing

<div style="min-height: 1400px; width: 100%; margin: 3em auto;">

```mermaid
graph TD
    WH[WEBHOOK: New Call<br/>Trigger]
    WP[Webex Platform]
    WC[Webex Connector]
    AR[(Audio Recordings<br/>S3 Storage)]
    TG[Transcript Generator<br/>OpenAI Whisper]
    TR[(Transcripts<br/>S3 Storage)]
    CA[Call Analysis<br/>GPT-4 AI]
    SFC[Salesforce<br/>Connector]
    AD[(Analysis Data<br/>S3 Storage)]
    REP[(Report<br/>S3 Storage)]
    CRM[SFDC/CloudSense<br/>CRM]
    DASH[Analytics<br/>Dashboard]
    
    WP -->|Call Completed| WH
    WH -->|Trigger| WC
    WC -->|Pull| WP
    WC -->|Process Audio| AR
    AR -->|Speech to Text| TG
    TG --> TR
    TR --> CA
    CA -->|Structured Data| SFC
    CA -->|Structured Data| AD
    CA -->|Structured Data| REP
    SFC --> CRM
    AD --> DASH
    REP --> DASH
    CRM -->|Display| DASH
    
    style WH fill:#c8e6c9
    style WP fill:#81d4fa
    style WC fill:#fff59d
    style AR fill:#f8bbd0
    style TG fill:#fff59d
    style TR fill:#f8bbd0
    style CA fill:#ce93d8
    style SFC fill:#fff59d
    style AD fill:#f8bbd0
    style REP fill:#f8bbd0
    style CRM fill:#e1bee7
    style DASH fill:#e1bee7
```

</div>

---

## Data Organization

### S3 Data Structure

```
s3://nexus-ai-{env}-call-data/
├── audio/
│   └── year=YYYY/month=MM/day=DD/
│       └── {call-id}-audio.wav
├── transcripts/
│   └── year=YYYY/month=MM/day=DD/
│       └── {call-id}-transcript.json
├── analysis/
│   └── year=YYYY/month=MM/day=DD/
│       └── {call-id}-analysis.json
├── diarized/
│   └── year=YYYY/month=MM/day=DD/
│       └── {call-id}-diarized.json
└── sfdcaction/
    └── year=YYYY/month=MM/day=DD/
        └── {call-id}-sfdcaction.json
```

### DynamoDB Tables

| Table | Purpose | Key Schema |
|-------|---------|------------|
| `nexus-ai-{env}-transformation-system` | Journey/Stage/Job tracking | PK: journey_id, SK: entity_type |
| `nexus-ai-{env}-license` | License management | PK: license_key |
| `nexus-ai-{env}-wxcc-tracking` | WXCC task tracking | PK: task_id |

---

## Integration Architecture

### API Integration Points

| Source | Target | Protocol | Purpose |
|--------|--------|----------|---------|
| NexusAI UI | NexusAI Backend | HTTP/REST | Call analytics, journey management |
| NexusAI UI | NexusAI Deployer | HTTP/REST | Deployment status, capability info |
| NexusAI Backend | AWS Services | boto3 SDK | DynamoDB, S3, Glue, CloudWatch |
| NexusAI Backend | Webex CC | REST API | Call recordings, task data |
| NexusAI Backend | OpenAI | REST API | Transcription, AI analysis |
| NexusAI Deployer | AWS CloudFormation | boto3 SDK | Stack provisioning |

---

## AWS Deployment Architecture

The complete infrastructure deployed by NexusAI Deployer:

### VPC Architecture
- **VPC CIDR**: 10.0.0.0/16
- **Public Subnet**: ALB, NAT Gateway
- **Private Subnet**: ECS Fargate, RDS (optional)

### Compute Layer
- **ALB**: Application Load Balancer for traffic distribution
- **ECS Fargate**: Serverless container execution
- **EventBridge**: Event-driven automation

### Storage Layer
- **S3 Buckets**: call-data, wxcc-simulator, deployment artifacts
- **DynamoDB**: Transformation system, license, tracking tables

### Security & Identity
- **Cognito**: User authentication and authorization
- **Secrets Manager**: API keys and credentials
- **SSM Parameter Store**: Configuration management

### Monitoring & Analytics
- **CloudWatch**: Logs, metrics, alarms, dashboards
- **Athena**: SQL analytics on S3 data
- **Glue**: Data catalog and ETL

### Content Delivery
- **CloudFront**: CDN for frontend distribution
- **S3 Static Hosting**: Frontend assets

### Deployment Options

| Component | Option 1 | Option 2 |
|-----------|----------|----------|
| **Frontend** | CloudFront + S3 | AWS Amplify |
| **Backend** | ECS Fargate | EKS (Kubernetes) |
| **Database** | DynamoDB | RDS PostgreSQL |

---

## Security Architecture

### Authentication & Authorization

**Authentication Layer:**
- **Cognito User Pool**: Primary identity provider
- **MFA**: TOTP/SMS multi-factor authentication
- **SSO**: SAML/OIDC integration
- **License Validation**: Cryptographic validation

**Authorization Layer:**
- **Role-Based Access Control (RBAC)**
  - Administrator: Full access
  - Operator: Deploy and manage
  - Viewer: Read-only access

**Data Protection:**
- **Encryption at Rest**: AES-256 (S3, DynamoDB)
- **Encryption in Transit**: TLS 1.2+
- **Secrets Management**: AWS Secrets Manager
- **IAM Roles**: Least privilege principle
- **Audit Logging**: CloudWatch Logs + CloudTrail

### Security Features

| Feature | Implementation |
|---------|----------------|
| **Authentication** | AWS Cognito with MFA support |
| **API Security** | API Key + JWT tokens |
| **Encryption at Rest** | AES-256 (S3, DynamoDB) |
| **Encryption in Transit** | TLS 1.2+ |
| **Secrets Management** | AWS Secrets Manager |
| **Audit Logging** | CloudWatch Logs + CloudTrail |
| **License Enforcement** | Cryptographic validation |

---

## Environment Configuration

### Configuration Sources

| Environment | Config Source | Resource Pattern |
|-------------|---------------|------------------|
| **ECS/AWS** | SSM Parameter Store + Secrets Manager | `nexus-ai-prod-*` |
| **Local AWS** | Environment variables | `nexus-ai-dev-*` |
| **LocalStack** | `.env.local` file | `nexus-ai-local-*` |

### Key Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `dev` |
| `AWS_REGION` | AWS region | `ap-southeast-1` |
| `USE_LOCALSTACK` | Enable LocalStack mode | `false` |
| `GATEWAY_PORT` | HTTP gateway port | `8000` |
| `API_KEY` | Gateway API key | (secure) |

---

## Monitoring & Operations

### Health Endpoints

| Service | Endpoint | Purpose |
|---------|----------|---------|
| NexusAI Backend | `/health` | Service health |
| NexusAI Backend | `/ready` | Readiness probe |
| NexusAI Backend | `/live` | Liveness probe |
| NexusAI Deployer | `/` | Root health check |
| NexusAI Deployer | `/api/health` | Detailed health |

### CloudWatch Integration

- **Logs**: Application logs streamed to CloudWatch Logs
- **Metrics**: Custom metrics for data processing and AI analysis
- **Alarms**: Automated alerts for failures
- **Dashboards**: Real-time monitoring dashboards

---

## Architecture Highlights

### Scalability
- **ECS Fargate** for auto-scaling containerized workloads
- **DynamoDB** for high-performance NoSQL data storage
- **S3** for scalable object storage
- **CloudFront** for global content delivery
- **Event-driven architecture** with EventBridge

### Integration
- **Webex Contact Center** for call data and recordings
- **Salesforce** for CRM automation
- **OpenAI** for AI-powered transcription and analysis
- **Office 365** for email integration

### Monitoring & Observability
- **CloudWatch** for logs, metrics, and alarms
- **Athena** for ad-hoc analytics
- **Glue** for data cataloging
- **X-Ray** for distributed tracing (optional)

### Security
- **Cognito** for authentication and authorization
- **Secrets Manager** for secure credential storage
- **IAM** for fine-grained access control
- **CloudTrail** for audit logging
- **VPC** for network isolation### High Availability
- **Multi-AZ deployment** for resilience
- **Auto-scaling** for compute resources
- **Load balancing** for traffic distribution
- **S3 replication** for data durability
- **DynamoDB global tables** (optional)---## Version Information| Application | Component | Version | Status |
|-------------|-----------|---------|--------|
| **NexusAI** | NexusAI UI | 1.0.0 | Production Ready |
| **NexusAI** | NexusAI Backend | 2.0.0 | Production Ready |
| **NexusAI Toolkit** | NexusAI Deployer | 1.0.0 | Production Ready |---*Last Updated: January 2026*  
*Document Version: 2.0*