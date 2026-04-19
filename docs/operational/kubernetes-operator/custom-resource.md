# Custom Resource Reference

Complete reference for the `TotogiCapability` Custom Resource Definition (CRD).

## Overview

The `TotogiCapability` CRD defines a complete Totogi capability deployment including AWS infrastructure and Kubernetes workloads.

```yaml
apiVersion: totogi.com/v1
kind: TotogiCapability
```

## Short Names

The CRD supports short names for convenience:

- `tc` - TotogiCapability
- `tcap` - TotogiCapability

```bash
kubectl get tc -A       # List all capabilities
kubectl get tcap -A     # Same as above
```

## Spec Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `capabilityName` | string | Name of the capability (e.g., `call-processing`) |
| `version` | string | Semantic version (e.g., `1.0.0`) |
| `environment` | string | Target environment: `dev`, `staging`, `prod`, `test` |
| `region` | string | AWS region (e.g., `ap-southeast-1`) |

### Frontend Configuration

```yaml
spec:
  frontend:
    enabled: true              # Enable frontend deployment (default: true)
    replicas: 2                # Number of replicas (1-20, default: 2)
    image: "repo/frontend:v1"  # Container image
    resources:
      requests:
        cpu: "100m"            # CPU request (default: 100m)
        memory: "128Mi"        # Memory request (default: 128Mi)
      limits:
        cpu: "500m"            # CPU limit (default: 500m)
        memory: "512Mi"        # Memory limit (default: 512Mi)
```

### Backend Configuration

```yaml
spec:
  backend:
    enabled: true              # Enable backend deployment (default: true)
    replicas: 2                # Number of replicas (1-20, default: 2)
    image: "repo/backend:v1"   # Container image
    resources:
      requests:
        cpu: "250m"            # CPU request (default: 250m)
        memory: "512Mi"        # Memory request (default: 512Mi)
      limits:
        cpu: "1000m"           # CPU limit (default: 1000m)
        memory: "1Gi"          # Memory limit (default: 1Gi)
```

### Data Services Configuration

```yaml
spec:
  dataServices:
    dynamodb: true   # Provision DynamoDB tables (default: true)
    s3: true         # Provision S3 buckets (default: true)
    glue: true       # Provision Glue database (default: true)
```

### Deletion Policy

```yaml
spec:
  deletionPolicy: Delete  # Options: Delete, Retain
```

| Policy | Behavior |
|--------|----------|
| `Delete` | Removes all AWS resources when CR is deleted |
| `Retain` | Keeps AWS resources, only removes K8s resources |

### Ingress Configuration

```yaml
spec:
  ingress:
    enabled: true
    className: "alb"           # Ingress class (default: alb)
    annotations:
      kubernetes.io/ingress.class: alb
    tls:
      enabled: false
      secretName: ""
      certificateArn: ""
    customDomain: ""
```

### Horizontal Pod Autoscaler

```yaml
spec:
  hpa:
    enabled: false
    minReplicas: 2              # Minimum replicas (default: 2)
    maxReplicas: 10             # Maximum replicas (default: 10)
    targetCPUUtilization: 70    # Target CPU % (default: 70)
```

### Pod Disruption Budget

```yaml
spec:
  pdb:
    enabled: true
    minAvailable: 1        # Minimum available pods
    maxUnavailable: 1      # Maximum unavailable pods
```

## Status Fields

The operator maintains these status fields:

| Field | Type | Description |
|-------|------|-------------|
| `phase` | string | Current deployment phase |
| `message` | string | Human-readable status message |
| `frontendUrl` | string | Frontend LoadBalancer URL |
| `backendUrl` | string | Backend LoadBalancer URL |
| `resources` | array | List of provisioned resources |
| `lastReconcileTime` | datetime | Last reconciliation timestamp |
| `observedGeneration` | integer | Generation observed by operator |

### Phase Values

| Phase | Description |
|-------|-------------|
| `Pending` | CR created, not yet processed |
| `ProvisioningDataServices` | Creating DynamoDB, S3, Glue |
| `ProvisioningSSM` | Creating SSM parameters |
| `ProvisioningSecrets` | Creating Secrets Manager secrets |
| `ProvisioningIAM` | Creating IAM roles |
| `DeployingBackend` | Deploying backend workloads |
| `DeployingFrontend` | Deploying frontend workloads |
| `CreatingServices` | Creating LoadBalancer services |
| `Ready` | Deployment complete |
| `Failed` | Deployment failed |
| `Deleting` | CR being deleted |

## Complete Example

```yaml
apiVersion: totogi.com/v1
kind: TotogiCapability
metadata:
  name: call-processing-prod
  namespace: call-processing-prod
  labels:
    app.kubernetes.io/name: call-processing
    app.kubernetes.io/version: "1.0.0"
    totogi.com/environment: prod
spec:
  # Required fields
  capabilityName: call-processing
  version: "1.0.0"
  environment: prod
  region: ap-southeast-1
  
  # Frontend deployment
  frontend:
    enabled: true
    replicas: 3
    image: "764119721991.dkr.ecr.ap-southeast-1.amazonaws.com/call-processing-ui:v1.0.0"
    resources:
      requests:
        cpu: "200m"
        memory: "256Mi"
      limits:
        cpu: "1000m"
        memory: "1Gi"
  
  # Backend deployment
  backend:
    enabled: true
    replicas: 3
    image: "764119721991.dkr.ecr.ap-southeast-1.amazonaws.com/call-processing-api:v1.0.0"
    resources:
      requests:
        cpu: "500m"
        memory: "1Gi"
      limits:
        cpu: "2000m"
        memory: "2Gi"
  
  # AWS data services
  dataServices:
    dynamodb: true
    s3: true
    glue: true
  
  # Ingress configuration
  ingress:
    enabled: true
    className: "alb"
    annotations:
      alb.ingress.kubernetes.io/scheme: internet-facing
      alb.ingress.kubernetes.io/target-type: ip
    tls:
      enabled: true
      certificateArn: "arn:aws:acm:ap-southeast-1:764119721991:certificate/xxx"
    customDomain: "call-processing.example.com"
  
  # Auto-scaling
  hpa:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilization: 70
  
  # Pod disruption budget
  pdb:
    enabled: true
    minAvailable: 2
  
  # Deletion policy
  deletionPolicy: Retain
```

## Minimal Example

```yaml
apiVersion: totogi.com/v1
kind: TotogiCapability
metadata:
  name: call-processing-dev
  namespace: call-processing-dev
spec:
  capabilityName: call-processing
  version: "1.0.0"
  environment: dev
  region: ap-southeast-1
  
  frontend:
    image: "nginx:latest"
  
  backend:
    image: "nginx:latest"
  
  dataServices:
    dynamodb: true
    s3: true
    glue: true
  
  deletionPolicy: Delete
```

## Validation Rules

### capabilityName
- Pattern: `^[a-z0-9-]+$`
- Min length: 1
- Max length: 63

### version
- Pattern: `^[0-9]+\.[0-9]+\.[0-9]+.*$`
- Example: `1.0.0`, `2.1.0-beta`

### environment
- Allowed values: `dev`, `staging`, `prod`, `test`

### region
- Pattern: `^[a-z]{2}-[a-z]+-[0-9]+$`
- Example: `ap-southeast-1`, `us-east-1`

### replicas
- Min: 1
- Max: 20
- Default: 2

## Printer Columns

When listing capabilities, these columns are displayed:

```bash
$ kubectl get totogicapabilities -A
NAMESPACE              NAME                   CAPABILITY        VERSION   ENVIRONMENT   PHASE   AGE
call-processing-dev    call-processing-dev    call-processing   1.0.0     dev           Ready   5m
call-processing-prod   call-processing-prod   call-processing   1.0.0     prod          Ready   1h
```

---

[← Back to Kubernetes Operator](index.md) | [Next: Deployment Guide →](deployment.md)
