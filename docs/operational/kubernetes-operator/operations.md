# Management & Operations

Day-to-day management and operational procedures for the Nexus Kubernetes Operator.

## Operator Management

### Check Status

```bash
./operator-nexus-dev.sh status
```

Expected healthy output:
```
✓ Operator is installed
  Status: installed
  Version: latest
  Namespace: nexus-system
  Ready replicas: 1/1

✓ Operator is healthy and running
```

### View Logs

```bash
# Stream logs
kubectl -n nexus-system logs -f deployment/nexus-operator

# Last 100 lines
kubectl -n nexus-system logs deployment/nexus-operator --tail=100

# Logs with timestamps
kubectl -n nexus-system logs deployment/nexus-operator --timestamps
```

### Restart Operator

```bash
kubectl -n nexus-system rollout restart deployment/nexus-operator
```

### Scale Operator

```bash
# Not recommended - operator should run as single replica
kubectl -n nexus-system scale deployment/nexus-operator --replicas=1
```

## Capability Management

### List All Capabilities

```bash
kubectl get nexuscapabilities -A
# or
kubectl get tc -A
```

### Get Capability Details

```bash
kubectl describe nexuscapability <name> -n <namespace>
```

### Watch Capability Status

```bash
kubectl get nexuscapabilities -A -w
```

### Update Capability

Edit the CR and apply:

```bash
kubectl edit nexuscapability <name> -n <namespace>
# or
kubectl apply -f updated-capability.yaml
```

### Delete Capability

```bash
kubectl delete nexuscapability <name> -n <namespace>
```

!!! note "Deletion Policy"
    The `deletionPolicy` in the CR spec determines whether AWS resources are deleted or retained.

## Monitoring

### Health Endpoints

The operator exposes health endpoints on port 8080:

| Endpoint | Purpose |
|----------|---------|
| `/healthz` | Liveness probe |
| `/readyz` | Readiness probe |
| `/metrics` | Prometheus metrics |

### Check Health Manually

```bash
# From within cluster
kubectl -n nexus-system exec -it deploy/nexus-operator -- curl localhost:8080/healthz
kubectl -n nexus-system exec -it deploy/nexus-operator -- curl localhost:8080/readyz
```

### Prometheus Metrics

```bash
kubectl -n nexus-system exec -it deploy/nexus-operator -- curl localhost:8080/metrics
```

Available metrics:
```
# HELP nexus_operator_reconciliations_total Total number of reconciliations
# TYPE nexus_operator_reconciliations_total counter
nexus_operator_reconciliations_total 0

# HELP nexus_operator_ready Operator readiness status
# TYPE nexus_operator_ready gauge
nexus_operator_ready 1
```

## Application Updates (Quick Deploy)

For code-only changes (no operator or infrastructure changes), use `deploy-app-changes.sh`:

```bash
cd /opt/mycode/nexus/nexus-deployer/kube-operator
./deploy-app-changes.sh
```

This script:

1. Builds `ai-job-engine` (backend) and `nexus-ui` (frontend) Docker images
2. Pushes both to ECR
3. Deletes existing pods to trigger a rollout with the new images
4. Waits for all pods to be Ready

## Application Lifecycle

### Deploy

```bash
kubectl create namespace myapp-dev
kubectl apply -f myapp-dev.yaml
```

### Update

Edit the YAML (e.g., change image tag or replica count) and reapply:

```bash
kubectl apply -f myapp-dev.yaml
```

### Scale

```bash
kubectl patch tc myapp-dev -n myapp-dev --type=merge \
  -p '{"spec":{"frontend":{"replicas":5}}}'
```

### Delete

```bash
kubectl delete tc myapp-dev -n myapp-dev
```

- `deletionPolicy: Delete` - Operator removes all AWS resources (DynamoDB, S3, Glue, SSM, Secrets, IAM)
- `deletionPolicy: Retain` - Operator keeps AWS resources, only removes K8s workloads

## Real-Time Monitoring

```bash
# Watch deployment step-by-step
./operator-nexus-dev.sh monitor

# Watch a specific capability
./operator-nexus-dev.sh monitor nexus-ai-prod/nexus-ai-prod
```

The monitor shows a live-updating table with each step's status, duration, and resources created.

## Post-Deployment Verification

```bash
./operator-nexus-dev.sh verify-capability
```

This runs 4 verification sections:

1. **AWS Resources** - DynamoDB tables (ACTIVE), S3 buckets (accessible), SSM parameters, Secrets, Glue database, IAM role (IRSA check)
2. **Kubernetes Resources** - Pods (Running/Ready), Services, Ingress (ALB address), ServiceAccount (IRSA annotation)
3. **Application Health** - Frontend via ALB (HTTP 200), Backend via ALB, Internal health check from pod
4. **Connectivity** - IRSA token mounted, AWS identity from pod

## Common Operations

### Verify CRD

```bash
kubectl get crd nexuscapabilities.nexus.ai
kubectl api-resources | grep nexus
```

### Check RBAC

```bash
kubectl get clusterrole nexus-operator -o yaml
kubectl get clusterrolebinding nexus-operator -o yaml
kubectl get serviceaccount nexus-operator -n nexus-system -o yaml
```

### View Events

```bash
# Operator events
kubectl -n nexus-system get events --sort-by='.lastTimestamp' | tail -20

# Capability events
kubectl get events -n <capability-namespace> --sort-by='.lastTimestamp'
```

### Check Resource Status

#### Kubernetes Resources

```bash
kubectl get all -n <capability>-<env>
```

#### AWS Resources

```bash
# DynamoDB tables
aws dynamodb list-tables | grep <capability>

# S3 buckets
aws s3 ls | grep <capability>

# IAM roles
aws iam list-roles | grep <capability>

# SSM parameters
aws ssm get-parameters-by-path --path /<capability>/<env>/ --recursive
```

## Backup & Recovery

### Export Capability CR

```bash
kubectl get nexuscapability <name> -n <namespace> -o yaml > capability-backup.yaml
```

### Export All CRs

```bash
kubectl get nexuscapabilities -A -o yaml > all-capabilities-backup.yaml
```

### Restore Capability

```bash
kubectl apply -f capability-backup.yaml
```

## Maintenance Tasks

### Update Operator Image

```bash
# Build new image
./build-and-push.sh

# Update deployment
kubectl -n nexus-system set image deployment/nexus-operator \
  nexus-operator=764119721991.dkr.ecr.ap-southeast-1.amazonaws.com/nexus-operator:latest

# Or use management script
./operator-nexus-dev.sh update
```

### Clean Up Failed Deployments

```bash
# List failed capabilities
kubectl get tc -A | grep Failed

# Force delete stuck capability
kubectl delete nexuscapability <name> -n <namespace> --force --grace-period=0

# Remove finalizer if stuck
kubectl patch nexuscapability <name> -n <namespace> \
  -p '{"metadata":{"finalizers":null}}' --type=merge
```

### Rotate IAM Credentials

IRSA handles credential rotation automatically. No manual rotation needed.

### Check IRSA Configuration

```bash
# Verify ServiceAccount annotation
kubectl get serviceaccount nexus-operator -n nexus-system -o yaml | grep eks.amazonaws.com

# Verify IAM role trust policy
aws iam get-role --role-name NexusAIOperatorRole --query 'Role.AssumeRolePolicyDocument'
```

## Scaling Capabilities

### Scale Workloads

Update the capability CR:

```yaml
spec:
  backend:
    replicas: 5    # Increase from 2
  frontend:
    replicas: 3    # Increase from 2
```

Apply:
```bash
kubectl apply -f capability.yaml
```

### Enable HPA

```yaml
spec:
  hpa:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilization: 70
```

## Security Operations

### Audit Operator Permissions

```bash
# Check what the operator can do
kubectl auth can-i --list --as=system:serviceaccount:nexus-system:nexus-operator
```

### Review IAM Role Policy

```bash
aws iam list-attached-role-policies --role-name NexusAIOperatorRole
aws iam get-role-policy --role-name NexusAIOperatorRole --policy-name NexusAIOperatorPolicy
```

### Check Pod Security

```bash
kubectl get pod -n nexus-system -o jsonpath='{.items[*].spec.securityContext}'
```

## Performance Tuning

### Operator Resources

Adjust operator resource limits in `manifests/deployment.yaml`:

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

### Capability Resources

Adjust in the capability CR:

```yaml
spec:
  backend:
    resources:
      requests:
        cpu: "500m"
        memory: "1Gi"
      limits:
        cpu: "2000m"
        memory: "4Gi"
```

## Useful Commands Reference

| Task | Command |
|------|---------|
| Check operator status | `./operator-nexus-dev.sh status` |
| View operator logs | `kubectl -n nexus-system logs -f deployment/nexus-operator` |
| List capabilities | `kubectl get tc -A` |
| Describe capability | `kubectl describe tc <name>` |
| Watch capabilities | `kubectl get tc -A -w` |
| Delete capability | `kubectl delete tc <name>` |
| View events | `kubectl -n nexus-system get events` |
| Restart operator | `kubectl -n nexus-system rollout restart deployment/nexus-operator` |
| Check CRD | `kubectl get crd nexuscapabilities.nexus.ai` |

---

[← Back to Kubernetes Operator](index.md) | [Next: Troubleshooting →](troubleshooting.md)
