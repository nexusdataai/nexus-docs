# Design Document

## Overview

The Totogi Customer Toolkit is a cloud-native, enterprise-grade management platform that enables customers to deploy and manage modular business capabilities across their own infrastructure. The system architecture follows a modern three-tier design with a Progressive Web Application (PWA) frontend, a microservices-based backend API layer, and a multi-tenant data layer. The toolkit supports both browser-based PWA access and native desktop applications via Electron, providing flexibility for different deployment scenarios.

The core design principle is security-first with defense-in-depth: multi-factor authentication, license-based entitlement validation, role-based access control, and comprehensive audit logging. The system orchestrates infrastructure deployments using CloudFormation templates while providing real-time monitoring, health checks, and lifecycle management capabilities.

Key architectural decisions:
- **Stateless API services** for horizontal scalability
- **JWT-based authentication** with short-lived tokens and refresh token rotation
- **License validation as a separate service** to enable flexible licensing models
- **Event-driven architecture** for deployment orchestration and monitoring
- **Offline-first PWA design** with service workers for resilience
- **CloudFormation-based deployments** for infrastructure-as-code consistency

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Client Layer                                 │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │  PWA (Browser)   │         │ Electron Desktop │            │
│  │  - React UI      │         │  - Native Shell  │            │
│  │  - Drag & Drop   │         │  - Auto-Update   │            │
│  │  - Service Worker│         │  - System Tray   │            │
│  │  - Offline Cache │         │  - Topology View │            │
│  └──────────────────┘         └──────────────────┘            │
└────────────────────┬──────────────────┬─────────────────────────┘
                     │                  │
                     ▼                  ▼
        ┌────────────────────────────────────────┐
        │   CDN / API Gateway Layer              │
        │   - CloudFront (Static Assets)         │
        │   - API Gateway (REST/WebSocket)       │
        │   - Rate Limiting & DDoS Protection    │
        └────────────────────────────────────────┘
                     │
        ┌────────────┼────────────────────────┐
        │            │            │           │
        ▼            ▼            ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
    │ Auth   │  │License │  │Capability│ │Landing │  │Product │
    │Service │  │Service │  │Service  │  │  Zone  │  │Enclave │
    └────────┘  └────────┘  └────────┘  └────────┘  └────────┘
        │            │            │            │            │
        ▼            ▼            ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
    │Deploy  │  │Monitor │  │Topology│  │ Audit  │  │  API   │
    │Service │  │Service │  │Service │  │Service │  │  Keys  │
    └────────┘  └────────┘  └────────┘  └────────┘  └────────┘
        │            │            │            │            │
        └────────────┴────────────┴────────────┴────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
    │DynamoDB│  │  RDS   │  │   S3   │  │ Redis  │
    │Sessions│  │ Audit  │  │ Assets │  │ Cache  │
    └────────┘  └────────┘  └────────┘  └────────┘
                     │
                     ▼
        ┌────────────────────────────────────────────────────┐
        │   Multi-Cloud Infrastructure                       │
        │                                                    │
        │   ┌──────────────────────────────────────┐       │
        │   │  Landing Zone (AWS/Azure/GCP/K8s/Ray)│       │
        │   │  ┌────────────────────────────────┐  │       │
        │   │  │  Product Enclave 1             │  │       │
        │   │  │  - Capability A (deployed)     │  │       │
        │   │  │  - Capability B (deployed)     │  │       │
        │   │  └────────────────────────────────┘  │       │
        │   │  ┌────────────────────────────────┐  │       │
        │   │  │  Product Enclave 2             │  │       │
        │   │  │  - Capability C (deployed)     │  │       │
        │   │  └────────────────────────────────┘  │       │
        │   └──────────────────────────────────────┘       │
        └────────────────────────────────────────────────────┘
```

### Authentication Flow

```
User → Login Form → Auth Service → [MFA Check] → License Service → 
JWT Token → Entitlement Cache → Dashboard Access
```

### Deployment Flow

```
User → Landing Zone Creation → Product Enclave Creation → 
Capability Catalog View → Drag Capability → Drop on Enclave → 
License Check → Deployment Wizard (pre-filled) → Parameter Validation → 
Cloud Permission Check → Infrastructure Provisioning → 
Progress Monitoring → Health Check → Topology Update → Completion
```

### Infrastructure Hierarchy

```
Tenant
  └── Landing Zone (AWS/Azure/GCP/K8s/Ray)
       ├── Product Enclave 1
       │    ├── Capability A
       │    └── Capability B
       └── Product Enclave 2
            └── Capability C
```

## Components and Interfaces

### Frontend Components

#### 1. PWA Application (React-based)

**Responsibilities:**
- Render user interface components
- Manage client-side state (Redux/Context API)
- Handle offline functionality via service workers
- Communicate with backend APIs
- Display real-time deployment progress

**Key Modules:**
- `AuthModule`: Login, MFA, SSO integration
- `DashboardModule`: Capability catalog, deployment status
- `LandingZoneModule`: Landing zone creation and management
- `ProductEnclaveModule`: Product enclave creation and management
- `TopologyVisualization`: Hierarchical view of infrastructure and deployments
- `DragDropDeployment`: Drag-and-drop interface for capability deployment
- `DeploymentWizard`: Step-by-step deployment guidance
- `MonitoringModule`: Health checks, logs, metrics
- `AdminModule`: User management, role assignment, audit logs

**Service Worker Strategy:**
- Cache-first for static assets (HTML, CSS, JS, images)
- Network-first for API calls with fallback to cache
- Background sync for offline actions
- Push notification handling

#### 2. Electron Desktop Application

**Responsibilities:**
- Wrap PWA in native desktop shell
- Provide system tray integration
- Handle auto-update mechanism
- Enable enhanced file system access
- Display native OS notifications

**Key Features:**
- IPC (Inter-Process Communication) between main and renderer processes
- Native menu integration
- Deep linking support
- Code signing for trusted distribution

### Backend Services

#### 1. Authentication Service

**API Endpoints:**
```
POST   /api/v1/auth/login
POST   /api/v1/auth/mfa/verify
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/auth/sso/redirect
POST   /api/v1/auth/sso/callback
```

**Responsibilities:**
- Validate username/password credentials
- Generate and validate JWT tokens
- Handle MFA enrollment and verification
- Integrate with SSO providers (SAML, OAuth, OIDC)
- Manage session lifecycle
- Enforce account lockout policies

**Dependencies:**
- Redis: Session storage and rate limiting
- RDS: User credentials and MFA secrets
- External: SSO identity providers

**Security Measures:**
- Argon2 password hashing with salt
- JWT with RS256 signing algorithm
- Refresh token rotation
- CSRF protection
- Rate limiting (5 attempts per 15 minutes)

#### 2. License Validation Service

**API Endpoints:**
```
POST   /api/v1/license/validate
GET    /api/v1/license/entitlements
GET    /api/v1/license/status
POST   /api/v1/license/refresh
```

**Responsibilities:**
- Validate license keys against cryptographic signatures
- Retrieve entitlement lists for valid licenses
- Enforce user count limits per tenant
- Check license expiration dates
- Cache entitlements for session duration
- Track license usage metrics

**License Key Format:**
```
{
  "licenseKey": "TOTOGI-XXXX-XXXX-XXXX-XXXX",
  "tenantId": "uuid",
  "entitlements": ["capability-1", "capability-2"],
  "userLimit": 50,
  "expiresAt": "2025-12-31T23:59:59Z",
  "signature": "base64-encoded-signature"
}
```

**Validation Algorithm:**
1. Parse license key structure
2. Verify cryptographic signature using public key
3. Check expiration date
4. Query current user count for tenant
5. Return entitlement list if valid

**Dependencies:**
- RDS: License metadata and usage tracking
- Redis: Entitlement cache (30-minute TTL)
- KMS: Cryptographic key management

#### 3. Capability Management Service

**API Endpoints:**
```
GET    /api/v1/capabilities
GET    /api/v1/capabilities/:id
GET    /api/v1/capabilities/:id/versions
GET    /api/v1/capabilities/:id/documentation
POST   /api/v1/capabilities/sync
```

**Responsibilities:**
- Maintain capability catalog
- Track capability versions and release notes
- Provide capability documentation and demos
- Sync with artifact repositories (GitHub, S3)
- Filter capabilities by license entitlements
- Manage capability dependencies

**Capability Metadata Schema:**
```json
{
  "id": "capability-id",
  "name": "Capability Name",
  "description": "Business value description",
  "version": "1.2.3",
  "dependencies": ["capability-x", "capability-y"],
  "cloudFormationTemplate": "s3://bucket/template.yaml",
  "documentation": "https://docs.example.com",
  "requiredPermissions": ["iam:CreateRole", "ec2:CreateVpc"],
  "estimatedCost": "$50/month"
}
```

**Dependencies:**
- RDS: Capability catalog
- S3: CloudFormation templates and documentation
- GitHub API: Capability updates

#### 4. Deployment Orchestration Service

**API Endpoints:**
```
POST   /api/v1/deployments
GET    /api/v1/deployments/:id
GET    /api/v1/deployments/:id/progress
POST   /api/v1/deployments/:id/rollback
DELETE /api/v1/deployments/:id
GET    /api/v1/environments
POST   /api/v1/environments
```

**Responsibilities:**
- Validate deployment requests
- Check license entitlements before deployment
- Validate AWS credentials and IAM permissions
- Generate CloudFormation templates with parameters
- Execute CloudFormation stack operations
- Track deployment progress and status
- Handle rollback scenarios
- Manage environment configurations

**Deployment State Machine:**
```
PENDING → VALIDATING → GENERATING_TEMPLATE → DEPLOYING → 
DEPLOYED | FAILED | ROLLED_BACK
```

**Dependencies:**
- AWS CloudFormation API
- AWS IAM API (permission validation)
- AWS STS (assume role for cross-account)
- RDS: Deployment history and environment configs
- Redis: Real-time deployment status
- WebSocket: Progress updates to clients

#### 5. Monitoring & Operations Service

**API Endpoints:**
```
GET    /api/v1/monitoring/health/:deploymentId
GET    /api/v1/monitoring/metrics/:deploymentId
GET    /api/v1/monitoring/logs/:deploymentId
POST   /api/v1/monitoring/logs/:deploymentId/download
GET    /api/v1/monitoring/alerts
POST   /api/v1/monitoring/alerts/configure
```

**Responsibilities:**
- Perform periodic health checks (every 5 minutes)
- Retrieve CloudWatch metrics for deployed resources
- Aggregate and retrieve logs from CloudWatch
- Generate downloadable log archives
- Send alert notifications (email, SMS, push)
- Track capability uptime and performance

**Health Check Logic:**
1. Query CloudFormation stack status
2. Check endpoint availability (HTTP 200 response)
3. Validate CloudWatch alarms
4. Update health status in cache
5. Trigger alerts if status changes to unhealthy

**Dependencies:**
- AWS CloudWatch API (metrics and logs)
- AWS CloudFormation API (stack status)
- SNS/SES: Notification delivery
- Redis: Health status cache
- RDS: Alert configurations

#### 6. Audit & Compliance Service

**API Endpoints:**
```
POST   /api/v1/audit/log
GET    /api/v1/audit/logs
GET    /api/v1/audit/export
GET    /api/v1/audit/reports
```

**Responsibilities:**
- Log all user actions with context
- Store immutable audit records
- Provide audit log search and filtering
- Generate compliance reports
- Export audit logs with cryptographic signatures

**Audit Log Schema:**
```json
{
  "timestamp": "2025-11-29T10:30:00Z",
  "userId": "user-uuid",
  "action": "DEPLOYMENT_INITIATED",
  "resource": "capability-id",
  "environment": "production",
  "ipAddress": "192.168.1.1",
  "userAgent": "Mozilla/5.0...",
  "result": "SUCCESS",
  "metadata": {}
}
```

**Dependencies:**
- AWS CloudTrail (AWS API calls)
- RDS: Audit log storage
- S3: Long-term audit log archival

#### 7. Landing Zone Management Service

**API Endpoints:**
```
POST   /api/v1/landing-zones
GET    /api/v1/landing-zones
GET    /api/v1/landing-zones/:id
PUT    /api/v1/landing-zones/:id
DELETE /api/v1/landing-zones/:id
POST   /api/v1/landing-zones/:id/validate
```

**Responsibilities:**
- Create and configure landing zones for multiple cloud providers
- Validate cloud provider credentials and configurations
- Provision foundational infrastructure (VPCs, networks, security groups)
- Track landing zone status and health
- Prevent deletion of landing zones with active product enclaves
- Support AWS, Azure, GCP, Kubernetes, and Ray clusters

**Landing Zone Provisioning Logic:**
1. Validate cloud provider credentials
2. Check for existing infrastructure conflicts
3. Provision networking layer (VPC/VNet/Network)
4. Configure security groups/firewall rules
5. Set up IAM roles and policies (cloud providers)
6. Create namespaces and quotas (Kubernetes/Ray)
7. Update landing zone status to ACTIVE
8. Log provisioning actions to audit trail

**Dependencies:**
- AWS SDK: VPC, Security Groups, IAM
- Azure SDK: Resource Groups, Virtual Networks, NSGs
- GCP SDK: VPC Networks, Firewall Rules
- Kubernetes API: Namespaces, Resource Quotas
- Ray API: Cluster management
- RDS: Landing zone metadata storage

#### 8. Product Enclave Management Service

**API Endpoints:**
```
POST   /api/v1/product-enclaves
GET    /api/v1/product-enclaves
GET    /api/v1/product-enclaves/:id
PUT    /api/v1/product-enclaves/:id
DELETE /api/v1/product-enclaves/:id
GET    /api/v1/product-enclaves/:id/capabilities
POST   /api/v1/product-enclaves/:id/validate
```

**Responsibilities:**
- Create product enclaves within landing zones
- Provision isolated infrastructure within parent landing zone
- Track deployed capabilities within each enclave
- Validate enclave configuration changes
- Prevent deletion of enclaves with deployed capabilities
- Support multi-cloud and on-premise environments

**Product Enclave Provisioning Logic:**
1. Validate parent landing zone exists and is ACTIVE
2. Validate enclave configuration against landing zone constraints
3. Provision isolated subnets/namespaces within landing zone
4. Configure security boundaries and network policies
5. Allocate resource quotas (Kubernetes/Ray)
6. Update enclave status to ACTIVE
7. Log provisioning actions to audit trail

**Dependencies:**
- Landing Zone Management Service
- AWS/Azure/GCP/Kubernetes/Ray SDKs
- RDS: Product enclave metadata storage
- Deployment Orchestration Service (for capability tracking)

#### 9. Topology Visualization Service

**API Endpoints:**
```
GET    /api/v1/topology
GET    /api/v1/topology/landing-zones/:id
GET    /api/v1/topology/product-enclaves/:id
GET    /api/v1/topology/capabilities/:id
```

**Responsibilities:**
- Generate hierarchical topology data structure
- Aggregate health status across landing zones, enclaves, and capabilities
- Provide detailed information for topology nodes
- Support filtering and search within topology
- Real-time updates via WebSocket

**Topology Data Structure:**
```json
{
  "landingZones": [
    {
      "id": "lz-uuid",
      "name": "Production AWS",
      "cloudProvider": "AWS",
      "status": "ACTIVE",
      "healthStatus": "HEALTHY",
      "productEnclaves": [
        {
          "id": "pe-uuid",
          "name": "Payment Services",
          "status": "ACTIVE",
          "healthStatus": "HEALTHY",
          "capabilities": [
            {
              "id": "cap-uuid",
              "name": "Payment Gateway",
              "version": "1.2.3",
              "healthStatus": "HEALTHY"
            }
          ]
        }
      ]
    }
  ]
}
```

**Dependencies:**
- Landing Zone Management Service
- Product Enclave Management Service
- Deployment Orchestration Service
- Monitoring & Operations Service (health status)
- WebSocket: Real-time updates

### API Gateway Configuration

**Rate Limiting:**
- Authentication endpoints: 5 requests per 15 minutes per IP
- API endpoints: 100 requests per minute per user
- Deployment endpoints: 10 concurrent deployments per tenant

**CORS Policy:**
- Allow origins: Configured PWA domains
- Allow methods: GET, POST, PUT, DELETE
- Allow headers: Authorization, Content-Type
- Credentials: true

**Authentication Middleware:**
1. Extract JWT from Authorization header
2. Verify JWT signature and expiration
3. Load user context and role from token
4. Attach user context to request
5. Proceed to route handler

## Data Models

### User Model

```typescript
interface User {
  id: string;                    // UUID
  tenantId: string;              // Organization identifier
  username: string;              // Unique username
  email: string;                 // Email address
  passwordHash: string;          // Argon2 hash
  passwordHistory: string[];     // Last 5 password hashes
  passwordChangedAt: Date;       // Last password change timestamp
  role: 'ADMINISTRATOR' | 'OPERATOR' | 'VIEWER';
  mfaEnabled: boolean;
  mfaSecret?: string;            // TOTP secret (encrypted)
  mfaRecoveryCodes?: string[];   // Encrypted recovery codes
  accountLocked: boolean;
  failedLoginAttempts: number;
  lockedUntil?: Date;
  lastLoginAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}
```

### License Model

```typescript
interface License {
  id: string;                    // UUID
  licenseKey: string;            // Formatted key
  tenantId: string;              // Organization identifier
  entitlements: string[];        // Capability IDs
  userLimit: number;             // Maximum concurrent users
  expiresAt: Date;               // License expiration
  signature: string;             // Cryptographic signature
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

### Capability Model

```typescript
interface Capability {
  id: string;                    // Unique identifier
  name: string;                  // Display name
  description: string;           // Business value description
  version: string;               // Semantic version
  dependencies: string[];        // Dependent capability IDs
  cloudFormationTemplateUrl: string;
  documentationUrl: string;
  requiredPermissions: string[]; // IAM permissions
  estimatedMonthlyCost: number;
  releaseNotes: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

### Environment Model

```typescript
interface Environment {
  id: string;                    // UUID
  tenantId: string;              // Organization identifier
  name: string;                  // e.g., "production", "staging"
  awsRegion: string;             // AWS region
  awsAccountId: string;          // Target AWS account
  iamRoleArn: string;            // Cross-account role ARN
  tags: Record<string, string>;  // Environment tags
  createdBy: string;             // User ID
  createdAt: Date;
  updatedAt: Date;
}
```

### Deployment Model

```typescript
interface Deployment {
  id: string;                    // UUID
  tenantId: string;
  capabilityId: string;
  environmentId: string;
  version: string;               // Deployed capability version
  status: 'PENDING' | 'VALIDATING' | 'DEPLOYING' | 
          'DEPLOYED' | 'FAILED' | 'ROLLED_BACK';
  cloudFormationStackId: string;
  cloudFormationStackName: string;
  parameters: Record<string, string>;
  outputs: Record<string, string>;
  errorMessage?: string;
  deployedBy: string;            // User ID
  deployedAt: Date;
  completedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}
```

### Session Model (Redis)

```typescript
interface Session {
  sessionId: string;             // UUID
  userId: string;
  tenantId: string;
  role: string;
  entitlements: string[];        // Cached from license
  ipAddress: string;
  userAgent: string;
  createdAt: number;             // Unix timestamp
  expiresAt: number;             // Unix timestamp
  refreshToken: string;          // Encrypted refresh token
}
```

### Audit Log Model

```typescript
interface AuditLog {
  id: string;                    // UUID
  timestamp: Date;
  userId: string;
  tenantId: string;
  action: string;                // Action type enum
  resource: string;              // Resource identifier
  resourceType: string;          // Resource type enum
  environment?: string;
  ipAddress: string;
  userAgent: string;
  result: 'SUCCESS' | 'FAILURE';
  errorMessage?: string;
  metadata: Record<string, any>;
}
```

### Landing Zone Model

```typescript
interface LandingZone {
  id: string;                    // UUID
  tenantId: string;              // Organization identifier
  name: string;                  // Display name
  cloudProvider: 'AWS' | 'AZURE' | 'GCP' | 'KUBERNETES' | 'RAY';
  region?: string;               // Cloud region (AWS/Azure/GCP)
  status: 'PROVISIONING' | 'ACTIVE' | 'FAILED' | 'DELETING';
  configuration: LandingZoneConfiguration;
  createdBy: string;             // User ID
  createdAt: Date;
  updatedAt: Date;
}

interface LandingZoneConfiguration {
  // AWS-specific
  awsAccountId?: string;
  vpcId?: string;
  vpcCidr?: string;
  securityGroupIds?: string[];
  iamRoleArn?: string;
  
  // Azure-specific
  subscriptionId?: string;
  resourceGroupName?: string;
  virtualNetworkId?: string;
  virtualNetworkCidr?: string;
  networkSecurityGroupIds?: string[];
  
  // GCP-specific
  projectId?: string;
  vpcNetworkName?: string;
  vpcNetworkCidr?: string;
  firewallRuleNames?: string[];
  
  // Kubernetes-specific
  clusterEndpoint?: string;
  clusterCaCertificate?: string;
  authenticationToken?: string;   // Encrypted
  defaultNamespace?: string;
  
  // Ray-specific
  rayClusterEndpoint?: string;
  rayAuthToken?: string;          // Encrypted
  totalCpus?: number;
  totalMemoryGb?: number;
  totalGpus?: number;
}
```

### Product Enclave Model

```typescript
interface ProductEnclave {
  id: string;                    // UUID
  tenantId: string;              // Organization identifier
  landingZoneId: string;         // Parent landing zone
  name: string;                  // Display name
  description?: string;
  status: 'PROVISIONING' | 'ACTIVE' | 'FAILED' | 'DELETING';
  configuration: ProductEnclaveConfiguration;
  deployedCapabilities: string[]; // Capability IDs
  createdBy: string;             // User ID
  createdAt: Date;
  updatedAt: Date;
}

interface ProductEnclaveConfiguration {
  // AWS-specific
  subnetIds?: string[];
  subnetCidrs?: string[];
  securityGroupIds?: string[];
  iamRoleArn?: string;
  
  // Azure-specific
  subnetIds?: string[];
  subnetCidrs?: string[];
  networkSecurityGroupIds?: string[];
  
  // GCP-specific
  subnetNames?: string[];
  subnetCidrs?: string[];
  firewallRuleNames?: string[];
  
  // Kubernetes-specific
  namespace?: string;
  resourceQuotas?: {
    cpuLimit?: string;
    memoryLimit?: string;
    storageLimit?: string;
  };
  networkPolicies?: string[];
  
  // Ray-specific
  allocatedCpus?: number;
  allocatedMemoryGb?: number;
  allocatedGpus?: number;
  isolationPolicy?: string;
}
```

## Correctness Properties


*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Authentication Properties

Property 1: Valid credentials create sessions
*For any* valid username and password combination, submitting the credentials should result in a new session being created with a valid JWT token
**Validates: Requirements 1.1**

Property 2: Invalid credentials increment failure counter
*For any* invalid username or password combination, submitting the credentials should result in authentication rejection and the failed login counter incrementing by one
**Validates: Requirements 1.2**

Property 3: JWT tokens have correct expiration
*For any* newly created session, the generated JWT token should have an expiration time exactly thirty minutes from creation
**Validates: Requirements 1.4**

Property 4: Expired tokens require re-authentication
*For any* expired JWT token, attempting to use it for API requests should result in authentication failure and require re-authentication
**Validates: Requirements 1.5**

### Multi-Factor Authentication Properties

Property 5: MFA enrollment generates TOTP secret
*For any* user enabling MFA, the system should generate a unique TOTP secret and provide a QR code for enrollment
**Validates: Requirements 2.1**

Property 6: MFA-enabled users require verification code
*For any* user with MFA enabled who submits valid credentials, the system should prompt for an MFA verification code before completing authentication
**Validates: Requirements 2.2**

Property 7: Valid MFA codes complete authentication
*For any* valid TOTP code submitted within the thirty-second time window, the authentication process should complete successfully
**Validates: Requirements 2.3**

### SSO Integration Properties

Property 8: SSO configuration triggers redirect
*For any* SSO-configured tenant, when a user initiates login, the system should redirect to the configured identity provider
**Validates: Requirements 3.1**

Property 9: Valid SAML assertions create sessions
*For any* valid SAML assertion returned by an identity provider, the system should create a user session with role mappings extracted from the assertion
**Validates: Requirements 3.2**

Property 10: Valid OAuth tokens create sessions
*For any* valid OAuth token returned by an identity provider, the system should validate the token and create a user session
**Validates: Requirements 3.3**

Property 11: OIDC authentication extracts claims
*For any* completed OpenID Connect authentication, the system should extract user claims and create a session with appropriate attributes
**Validates: Requirements 3.4**

Property 12: SSO failures provide fallback
*For any* SSO authentication failure, the system should display an error message and provide a fallback option to local authentication
**Validates: Requirements 3.5**

### License Validation Properties

Property 13: Authentication prompts for license key
*For any* user completing authentication, the system should prompt for a License Key before granting access to the capability dashboard
**Validates: Requirements 4.1**

Property 14: License keys are validated
*For any* submitted License Key, the system should validate it against the license validation service before proceeding
**Validates: Requirements 4.2**

Property 15: Valid licenses retrieve entitlements
*For any* valid License Key, the system should retrieve the entitlement list and unlock access to entitled capabilities
**Validates: Requirements 4.3**

Property 16: Invalid licenses are rejected
*For any* invalid or expired License Key, the system should reject the key and display an error message with expiration details
**Validates: Requirements 4.4**

Property 17: User count limits are enforced
*For any* License Key with a user count limit, the system should enforce the limit and reject authentication attempts that would exceed the licensed user count
**Validates: Requirements 4.5**

Property 18: Entitlements are cached
*For any* validated License Key, the system should cache the entitlement list for the duration of the user session
**Validates: Requirements 4.6**

Property 19: Deployment requires entitlement verification
*For any* capability deployment attempt, the system should verify the capability is included in the cached entitlement list before proceeding
**Validates: Requirements 4.7**

### Role-Based Access Control Properties

Property 20: Role assignments persist across sessions
*For any* role assignment made by an Administrator, the assignment should be stored and applied to all subsequent user sessions
**Validates: Requirements 5.1**

Property 21: Administrators have full access
*For any* user with Administrator role, the system should grant full access to all capabilities, configurations, and audit logs
**Validates: Requirements 5.2**

Property 22: Operators have limited environment access
*For any* user with Operator role, the system should grant deployment permissions only for their assigned environments
**Validates: Requirements 5.3**

Property 23: Viewers have read-only access
*For any* user with Viewer role, the system should grant read-only access to dashboards, reports, and non-sensitive logs
**Validates: Requirements 5.4**

Property 24: Unauthorized actions are denied and logged
*For any* action attempt not permitted by a user's role, the system should deny the action and log the authorization failure
**Validates: Requirements 5.5**

### Capability Dashboard Properties

Property 25: Dashboard displays all capabilities
*For any* user accessing the capability dashboard, the system should display all capabilities with their deployment status, description, and business value
**Validates: Requirements 6.1**

Property 26: Entitled capabilities are marked available
*For any* capability entitled by the user's license, the system should mark the capability as available for deployment
**Validates: Requirements 6.2**

Property 27: Non-entitled capabilities show upgrade info
*For any* capability not entitled by the user's license, the system should mark it as unavailable and display upgrade information
**Validates: Requirements 6.3**

Property 28: Deployed capabilities show status
*For any* capability that is already deployed, the system should display the deployment status and environment information
**Validates: Requirements 6.4**

Property 29: Capability selection shows details
*For any* capability selected by a user, the system should display detailed documentation, sample demos, and deployment options
**Validates: Requirements 6.5**

### Deployment Wizard Properties

Property 30: Capability selection launches wizard
*For any* capability selected for deployment by an Operator, the system should launch a deployment wizard with step-by-step guidance
**Validates: Requirements 7.1**

Property 31: Deployment mode options are offered
*For any* deployment wizard, the system should offer options for customer infrastructure or SaaS-hosted deployment
**Validates: Requirements 7.2**

Property 32: Configured environments are displayed
*For any* target environment prompt in the wizard, the system should display all configured environments and allow selection
**Validates: Requirements 7.3**

Property 33: Configuration parameters are validated
*For any* configuration parameter input in the wizard, the system should validate the input against the capability requirements
**Validates: Requirements 7.4**

Property 34: Completed wizard initiates deployment
*For any* deployment wizard with all steps completed, the system should initiate the deployment and display real-time progress updates
**Validates: Requirements 7.5**

Property 35: Successful deployments show outputs
*For any* deployment that completes successfully, the system should display the CloudFormation stack outputs and capability endpoints
**Validates: Requirements 7.6**

Property 36: Failed deployments show error details
*For any* deployment that fails, the system should display error details and offer rollback or retry options
**Validates: Requirements 7.7**

### Environment Management Properties

Property 37: Environment creation stores configuration
*For any* environment created by an Administrator, the system should store the environment configuration with a unique identifier
**Validates: Requirements 8.1**

Property 38: Environment configuration requires AWS details
*For any* environment being configured, the system should require AWS region, credentials, and IAM role specifications
**Validates: Requirements 8.2**

Property 39: Deployments are isolated by environment
*For any* capability deployed to an environment, the system should isolate the deployment from other environments
**Validates: Requirements 8.3**

Property 40: Deployment history is grouped by environment
*For any* deployment history view, the system should display deployments grouped by environment
**Validates: Requirements 8.4**

Property 41: Environments with deployments cannot be deleted
*For any* environment with active deployments, the system should prevent deletion of that environment
**Validates: Requirements 8.5**

### Monitoring Properties

Property 42: Deployed capabilities have health checks
*For any* deployed capability, the system should perform health checks every five minutes and display the current status
**Validates: Requirements 9.1**

Property 43: Failed health checks trigger alerts
*For any* health check that fails, the system should send an alert notification to configured recipients
**Validates: Requirements 9.2**

Property 44: Metrics display CloudWatch data
*For any* capability metrics view by an Operator, the system should display CloudWatch metrics for the deployed resources
**Validates: Requirements 9.3**

Property 45: Log requests retrieve CloudWatch logs
*For any* log request by an Operator, the system should retrieve logs from CloudWatch and display them in the interface
**Validates: Requirements 9.4**

Property 46: Log downloads generate archives
*For any* log download request, the system should generate a downloadable log archive in JSON or text format
**Validates: Requirements 9.5**

### Patching Properties

Property 47: New versions trigger notifications
*For any* new capability version that becomes available, the system should display a notification in the dashboard
**Validates: Requirements 10.1**

Property 48: Patch selection shows version info
*For any* capability selected for patching by an Administrator, the system should display the current version, available version, and release notes
**Validates: Requirements 10.2**

Property 49: Patch initiation creates change sets
*For any* patch initiated by an Administrator, the system should create a CloudFormation change set and display the proposed changes
**Validates: Requirements 10.3**

Property 50: Change set approval executes patch
*For any* change set approved by an Administrator, the system should execute the patch deployment and track progress
**Validates: Requirements 10.4**

Property 51: Failed patches trigger rollback
*For any* patch that fails, the system should automatically roll back to the previous version and log the failure details
**Validates: Requirements 10.5**

Property 52: Successful patches update metadata
*For any* patch that completes successfully, the system should update the capability version in the deployment metadata
**Validates: Requirements 10.6**

### PWA Properties

Property 53: Browser access loads PWA
*For any* user accessing the Toolkit URL in a browser, the system should load as a PWA with service worker registration
**Validates: Requirements 11.1**

Property 54: Offline mode displays cached content
*For any* user in offline state, the system should display cached documentation and deployment status using service workers
**Validates: Requirements 11.3**

Property 55: Connectivity restoration syncs data
*For any* user regaining connectivity, the system should synchronize any pending actions and refresh data
**Validates: Requirements 11.4**

Property 56: New versions prompt refresh
*For any* new version deployed, the system should prompt the user to refresh and load the updated application
**Validates: Requirements 11.5**

### Desktop Application Properties

Property 57: Notifications display natively
*For any* notification event in the desktop application, the system should display a native OS notification
**Validates: Requirements 12.3**

Property 58: Updates trigger download and prompt
*For any* new version detected by the desktop application, the system should automatically download and prompt the user to install the update
**Validates: Requirements 12.4**

Property 59: File system access uses native dialogs
*For any* file system access in the desktop application, the system should use native file dialogs for log downloads and configuration imports
**Validates: Requirements 12.5**

### Audit Logging Properties

Property 60: All actions are logged
*For any* user action performed in the system, the system should log the action to CloudTrail with timestamp, user identity, and action details
**Validates: Requirements 13.1**

Property 61: Authentication events are logged with details
*For any* authentication event, the system should log the event with IP address, user agent, and authentication result
**Validates: Requirements 13.2**

Property 62: Deployment initiations are logged
*For any* deployment initiated, the system should log the deployment request with capability, environment, and configuration parameters
**Validates: Requirements 13.3**

Property 63: Audit logs support filtering
*For any* audit log view by an Administrator, the system should display logs with filtering capabilities by user, action type, and time range
**Validates: Requirements 13.4**

Property 64: Audit exports are tamper-evident
*For any* audit log export, the system should generate a tamper-evident export in CSV or JSON format with cryptographic signatures
**Validates: Requirements 13.5**

### Capability Updates Properties

Property 65: Toolkit startup checks for updates
*For any* Toolkit startup, the system should check the configured artifact repository for capability updates
**Validates: Requirements 14.1**

Property 66: New capabilities show indicator
*For any* new capability that becomes available, the system should display it in the dashboard with a "New" indicator
**Validates: Requirements 14.2**

Property 67: Manual approval requires explicit action
*For any* manual approval configuration, the system should require explicit approval before displaying new capabilities
**Validates: Requirements 14.4**

Property 68: GitHub releases update catalog
*For any* new GitHub release published (where GitHub integration is configured), the system should retrieve the release artifacts and update the capability catalog
**Validates: Requirements 14.5**

### Password Security Properties

Property 69: Password creation enforces complexity
*For any* password creation, the system should require a minimum of twelve characters with uppercase, lowercase, numbers, and special characters
**Validates: Requirements 15.1**

Property 70: Password changes prevent reuse
*For any* password change, the system should prevent reuse of the previous five passwords
**Validates: Requirements 15.2**

Property 71: Old passwords trigger change prompt
*For any* password that is ninety days old, the system should prompt the user to change their password at next login
**Validates: Requirements 15.3**

Property 72: Passwords are hashed with Argon2
*For any* password entered by a user, the system should hash the password using Argon2 before storage
**Validates: Requirements 15.4**

Property 73: New accounts require password change
*For any* newly created user account, the system should require password change on first login
**Validates: Requirements 15.5**

### Notification Properties

Property 74: Successful deployments send notifications
*For any* deployment that completes successfully, the system should send a notification to configured recipients via email or SMS
**Validates: Requirements 16.1**

Property 75: Failed deployments send alerts
*For any* deployment that fails, the system should send an alert notification with error details and recommended actions
**Validates: Requirements 16.2**

Property 76: Failed health checks send alerts
*For any* health check that fails, the system should send an alert notification within two minutes of detection
**Validates: Requirements 16.3**

Property 77: Notification preferences allow configuration
*For any* notification preference configuration by an Administrator, the system should allow selection of notification channels and event types
**Validates: Requirements 16.4**

Property 78: Push notifications are delivered
*For any* event occurring when push notifications are enabled, the system should deliver a push notification to the PWA or desktop application
**Validates: Requirements 16.5**

### AWS Permission Validation Properties

Property 79: Deployments validate IAM permissions
*For any* deployment initiation, the system should validate that AWS credentials have the required IAM permissions before proceeding
**Validates: Requirements 17.1**

Property 80: Insufficient permissions show details
*For any* IAM permission validation that finds insufficient permissions, the system should display the missing permissions and provide documentation links
**Validates: Requirements 17.2**

Property 81: Invalid credentials are rejected
*For any* AWS credentials that are invalid, the system should reject the deployment and prompt for credential correction
**Validates: Requirements 17.3**

Property 82: Cross-account access validates trust
*For any* deployment requiring cross-account access, the system should validate the trust relationship and assume-role permissions
**Validates: Requirements 17.4**

Property 83: Successful validation proceeds to template generation
*For any* permission validation that completes successfully, the system should proceed with CloudFormation template generation
**Validates: Requirements 17.5**

### API Key Management Properties

Property 84: API key creation generates secure keys
*For any* API key created by an Administrator, the system should generate a cryptographically secure key and display it once
**Validates: Requirements 18.1**

Property 85: API key usage validates and applies permissions
*For any* API key used for authentication, the system should validate the key and apply the associated user's role permissions
**Validates: Requirements 18.2**

Property 86: API key revocation invalidates immediately
*For any* API key revoked by an Administrator, the system should immediately invalidate the key and reject subsequent requests
**Validates: Requirements 18.3**

Property 87: API key views hide key values
*For any* API key view by an Administrator, the system should display key metadata without revealing the key value
**Validates: Requirements 18.4**

Property 88: API key creation allows expiration and scope
*For any* API key creation, the system should allow setting an expiration date and scope restrictions
**Validates: Requirements 18.5**

### Landing Zone Management Properties

Property 89: Landing zone creation stores configuration
*For any* landing zone created by an Administrator, the system should store the landing zone configuration with unique identifiers and cloud provider details
**Validates: Requirements 19.1**

Property 90: AWS landing zones require VPC configuration
*For any* landing zone configured for AWS, the system should require VPC configuration, security groups, IAM roles, and region specifications
**Validates: Requirements 19.2**

Property 91: Azure landing zones require virtual network configuration
*For any* landing zone configured for Azure, the system should require resource group, virtual network, network security groups, and region specifications
**Validates: Requirements 19.3**

Property 92: GCP landing zones require VPC network configuration
*For any* landing zone configured for Google Cloud, the system should require project ID, VPC network, firewall rules, and region specifications
**Validates: Requirements 19.4**

Property 93: Kubernetes landing zones require cluster configuration
*For any* landing zone configured for on-premise Kubernetes, the system should require cluster endpoint, authentication credentials, and namespace specifications
**Validates: Requirements 19.5**

Property 94: Ray landing zones require cluster configuration
*For any* landing zone configured for on-premise Ray cluster, the system should require cluster endpoint, authentication credentials, and resource allocation specifications
**Validates: Requirements 19.6**

Property 95: Landing zone views display all configurations
*For any* Administrator viewing landing zones, the system should display all configured landing zones with their cloud provider type and status
**Validates: Requirements 19.7**

### Product Enclave Management Properties

Property 96: Product enclave creation requires landing zone
*For any* product enclave created by an Administrator, the system should require selection of a parent landing zone and store the enclave configuration
**Validates: Requirements 20.1**

Property 97: AWS enclaves provision isolated infrastructure
*For any* product enclave created in AWS, the system should provision isolated subnets, security groups, and IAM roles within the landing zone VPC
**Validates: Requirements 20.2**

Property 98: Azure enclaves provision isolated infrastructure
*For any* product enclave created in Azure, the system should provision isolated subnets and network security groups within the landing zone virtual network
**Validates: Requirements 20.3**

Property 99: GCP enclaves provision isolated infrastructure
*For any* product enclave created in Google Cloud, the system should provision isolated subnets and firewall rules within the landing zone VPC network
**Validates: Requirements 20.4**

Property 100: Kubernetes enclaves create namespaces
*For any* product enclave created in Kubernetes, the system should create a dedicated namespace with resource quotas and network policies
**Validates: Requirements 20.5**

Property 101: Ray enclaves allocate resources
*For any* product enclave created in Ray cluster, the system should allocate dedicated compute resources and establish resource isolation
**Validates: Requirements 20.6**

Property 102: Product enclave views group by landing zone
*For any* Administrator viewing product enclaves, the system should display all enclaves grouped by their parent landing zone with deployment status
**Validates: Requirements 20.7**

### Drag-and-Drop Deployment Properties

Property 103: Deployment interface displays catalog and enclaves
*For any* Operator viewing the deployment interface, the system should display the capability catalog on one side and product enclaves on the other side
**Validates: Requirements 21.1**

Property 104: Dragging highlights compatible enclaves
*For any* capability dragged from the catalog by an Operator, the system should highlight compatible product enclaves that can host the capability
**Validates: Requirements 21.2**

Property 105: Dropping validates license entitlement
*For any* capability dropped onto a product enclave by an Operator, the system should validate the capability is entitled by the license before proceeding
**Validates: Requirements 21.3**

Property 106: Drop launches pre-filled wizard
*For any* capability dropped onto a product enclave, the system should launch a deployment wizard with pre-filled enclave configuration
**Validates: Requirements 21.4**

Property 107: Drag-and-drop provisions within enclave
*For any* capability deployment initiated via drag-and-drop, the system should provision the capability infrastructure within the selected product enclave
**Validates: Requirements 21.5**

Property 108: Deployed capabilities show in enclave
*For any* capability successfully deployed to a product enclave, the system should display the capability as deployed within the enclave visualization
**Validates: Requirements 21.6**

Property 109: Enclave view shows deployed capabilities
*For any* product enclave viewed by an Operator, the system should display all capabilities deployed within that enclave with their health status
**Validates: Requirements 21.7**

### Infrastructure Lifecycle Properties

Property 110: Landing zones with enclaves cannot be deleted
*For any* landing zone with existing product enclaves, the system should prevent deletion of that landing zone
**Validates: Requirements 22.1**

Property 111: Enclaves with capabilities cannot be deleted
*For any* product enclave with deployed capabilities, the system should prevent deletion of that enclave
**Validates: Requirements 22.2**

Property 112: Landing zone updates are validated
*For any* landing zone configuration update by an Administrator, the system should validate the changes and apply them to the underlying infrastructure
**Validates: Requirements 22.3**

Property 113: Enclave updates validate compatibility
*For any* product enclave configuration update by an Administrator, the system should validate the changes do not conflict with deployed capabilities
**Validates: Requirements 22.4**

Property 114: Infrastructure changes are audited
*For any* landing zone or product enclave modification, the system should log the change to the audit trail with user identity and timestamp
**Validates: Requirements 22.5**

### Topology Visualization Properties

Property 115: Topology displays hierarchical structure
*For any* Operator accessing the topology view, the system should display a hierarchical visualization of landing zones containing product enclaves containing capabilities
**Validates: Requirements 23.1**

Property 116: Landing zone selection highlights children
*For any* landing zone selected in the topology by an Operator, the system should highlight all product enclaves and capabilities within that landing zone
**Validates: Requirements 23.2**

Property 117: Enclave selection shows details
*For any* product enclave selected in the topology by an Operator, the system should display detailed information about the enclave and its deployed capabilities
**Validates: Requirements 23.3**

Property 118: Capability selection shows metrics
*For any* capability selected in the topology by an Operator, the system should display capability details, health status, and operational metrics
**Validates: Requirements 23.4**

Property 119: Topology uses health indicators
*For any* topology view displayed, the system should use visual indicators to show health status for each landing zone, product enclave, and capability
**Validates: Requirements 23.5**

## Error Handling

### Error Categories

**Authentication Errors:**
- Invalid credentials (401 Unauthorized)
- Account locked (403 Forbidden)
- MFA verification failed (401 Unauthorized)
- Session expired (401 Unauthorized)
- SSO integration failure (502 Bad Gateway)

**Authorization Errors:**
- Insufficient permissions (403 Forbidden)
- License validation failed (403 Forbidden)
- Capability not entitled (403 Forbidden)
- User count limit exceeded (403 Forbidden)

**Deployment Errors:**
- Invalid AWS credentials (400 Bad Request)
- Insufficient IAM permissions (403 Forbidden)
- CloudFormation stack creation failed (500 Internal Server Error)
- Parameter validation failed (400 Bad Request)
- Environment not found (404 Not Found)

**Monitoring Errors:**
- CloudWatch API failure (502 Bad Gateway)
- Health check timeout (504 Gateway Timeout)
- Log retrieval failed (500 Internal Server Error)

**System Errors:**
- Database connection failure (503 Service Unavailable)
- External service timeout (504 Gateway Timeout)
- Rate limit exceeded (429 Too Many Requests)

### Error Response Format

All API errors follow a consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context",
      "suggestion": "Recommended action"
    },
    "timestamp": "2025-11-29T10:30:00Z",
    "requestId": "uuid"
  }
}
```

### Error Handling Strategies

**Retry Logic:**
- Transient errors (network timeouts, 503 errors): Exponential backoff with 3 retries
- Rate limit errors (429): Wait for retry-after header duration
- CloudFormation operations: Poll status with exponential backoff

**Fallback Mechanisms:**
- SSO failure: Fallback to local authentication
- CloudWatch unavailable: Display cached metrics
- Offline mode: Service worker serves cached content

**User Notifications:**
- Critical errors: Display modal dialog with error details
- Warning errors: Display toast notification
- Background errors: Log to console and audit trail

**Logging:**
- All errors logged to CloudWatch with full context
- Error stack traces included for 500-level errors
- User-facing error messages sanitized to prevent information leakage

## Testing Strategy

### Unit Testing

**Framework:** Jest for JavaScript/TypeScript components

**Coverage Targets:**
- Business logic: 90% code coverage
- API endpoints: 85% code coverage
- Utility functions: 95% code coverage

**Key Unit Test Areas:**
- Authentication service: Credential validation, JWT generation, MFA verification
- License validation: Key parsing, signature verification, entitlement checking
- RBAC middleware: Permission checking, role validation
- Deployment orchestration: Parameter validation, template generation
- Password security: Complexity validation, Argon2 hashing, history checking

**Example Unit Tests:**
- Test that valid credentials create a session with correct JWT expiration
- Test that invalid license keys are rejected with appropriate error messages
- Test that Operator role cannot access Administrator-only endpoints
- Test that deployment parameter validation catches invalid AWS regions
- Test that password complexity rules reject weak passwords

### Property-Based Testing

**Framework:** fast-check for JavaScript/TypeScript

**Configuration:** Minimum 100 iterations per property test

**Property Test Tagging:** Each property-based test must include a comment with the format:
```javascript
// Feature: totogi-customer-toolkit, Property 1: Valid credentials create sessions
```

**Key Property Test Areas:**

**Authentication Properties:**
- Property 1: Valid credentials create sessions (test with random valid username/password combinations)
- Property 4: Expired tokens require re-authentication (test with random expired tokens)
- Property 7: Valid MFA codes complete authentication (test with random valid TOTP codes)

**License Validation Properties:**
- Property 15: Valid licenses retrieve entitlements (test with random valid license keys)
- Property 17: User count limits are enforced (test with random user counts and limits)
- Property 19: Deployment requires entitlement verification (test with random capability/entitlement combinations)

**RBAC Properties:**
- Property 21: Administrators have full access (test with random Administrator users and endpoints)
- Property 22: Operators have limited environment access (test with random Operator users and environments)
- Property 24: Unauthorized actions are denied and logged (test with random unauthorized action attempts)

**Deployment Properties:**
- Property 33: Configuration parameters are validated (test with random parameter inputs)
- Property 39: Deployments are isolated by environment (test with random deployment/environment combinations)
- Property 79: Deployments validate IAM permissions (test with random IAM permission sets)

**Password Security Properties:**
- Property 69: Password creation enforces complexity (test with random password strings)
- Property 70: Password changes prevent reuse (test with random password histories)
- Property 72: Passwords are hashed with Argon2 (test with random passwords and verify hash format)

**Audit Logging Properties:**
- Property 60: All actions are logged (test with random user actions)
- Property 64: Audit exports are tamper-evident (test with random audit log sets)

### Integration Testing

**Framework:** Supertest for API integration tests

**Key Integration Test Areas:**
- End-to-end authentication flow: Login → MFA → License validation → Dashboard access
- Deployment workflow: Capability selection → Wizard → AWS validation → CloudFormation execution
- Monitoring integration: Health checks → CloudWatch metrics → Alert notifications
- SSO integration: SAML/OAuth flow with mock identity provider

**Test Environment:**
- LocalStack for AWS service mocking (CloudFormation, CloudWatch, S3, DynamoDB)
- Test database with seed data
- Mock SSO identity provider

### End-to-End Testing

**Framework:** Playwright for browser automation

**Key E2E Test Scenarios:**
- User completes full authentication flow and deploys a capability
- Administrator manages users, roles, and environments
- Operator monitors deployed capabilities and downloads logs
- PWA offline functionality: Cache, sync, and service worker behavior
- Desktop application: Auto-update, system tray, native notifications

### Performance Testing

**Framework:** k6 for load testing

**Performance Targets:**
- API response time: < 500ms (P95)
- Authentication flow: < 2 seconds (P95)
- Deployment initiation: < 5 seconds
- Dashboard load: < 2 seconds (P95)

**Load Test Scenarios:**
- 100 concurrent users authenticating
- 50 concurrent deployments
- 1000 requests per second to capability dashboard

### Security Testing

**Tools:**
- OWASP ZAP for vulnerability scanning
- npm audit for dependency vulnerabilities
- Snyk for continuous security monitoring

**Security Test Areas:**
- SQL injection prevention
- XSS prevention
- CSRF protection
- JWT token security
- Password hashing strength
- License key cryptographic validation

### Test Data Generation

**Strategy:**
- Use faker.js for generating realistic test data
- Property-based testing generators for random valid/invalid inputs
- Seed data scripts for consistent integration test environments

**Test Data Categories:**
- Users: Various roles, MFA configurations, password histories
- Licenses: Valid/invalid/expired keys, different entitlement sets
- Capabilities: Various versions, dependencies, configurations
- Deployments: Different states, environments, error scenarios

