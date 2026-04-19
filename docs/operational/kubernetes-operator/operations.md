# Management & Operations

Day-to-day management and operational procedures for the Totogi Kubernetes Operator.

## Operator Management

### Check Status

```bash
./operator-starhub-test.sh status
```

Expected healthy output:
```
✓ Operator is installed
  Status: installed
  Version: latest
  Namespace: totogi-system
  Ready replicas: 1/1

✓ Operator is healthy and running
```

### View Logs

```bash
# Stream logs
kubectl -n totogi-system logs -f deployment/totogi-operator

# Last 100 lines
kubectl -n totogi-system logs deployment/totogi-operator --tail=100

# Logs with timestamps
kubectl -n totogi-system logs deployment/totogi-operator --timestamps
```

### Restart Operator

```bash
kubectl -n totogi-system rollout restart deployment/totogi-operator
```

### Scale Operator

```bash
# Not recommended - operator should run as single replica
kubectl -n totogi-system scale deployment/totogi-operator --replicas=1
```

## Capability Management

### List All Capabilities

```bash
kubectl get totogicapabilities -A
# or
kubectl get tc -A
```

### Get Capability Details

```bash
kubectl describe totogicapability <name> -n <namespace>
```

### Watch Capability Status

```bash
kubectl get totogicapabilities -A -w
```

### Update Capability

Edit the CR and apply:

```bash
kubectl edit totogicapability <name> -n <namespace>
# or
kubectl apply -f updated-capability.yaml
```

### Delete Capability

```bash
kubectl delete totogicapability <name> -n <namespace>
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
kubectl -n totogi-system exec -it deploy/totogi-operator -- curl localhost:8080/healthz
kubectl -n totogi-system exec -it deploy/totogi-operator -- curl localhost:8080/readyz
```

### Prometheus Metrics

```bash
kubectl -n totogi-system exec -it deploy/totogi-operator -- curl localhost:8080/metrics
```

Available metrics:
```
# HELP totogi_operator_reconciliations_total Total number of reconciliations
# TYPE totogi_operator_reconciliations_total counter
totogi_operator_reconciliations_total 0

# HELP totogi_operator_ready Operator readiness status
# TYPE totogi_operator_ready gauge
totogi_operator_ready 1
```

## Application Updates (Quick Deploy)

For code-only changes (no operator or infrastructure changes), use `deploy-app-changes.sh`:

```bash
cd /opt/mycode/trilogy/starhub-deployer/kube-operator
./deploy-app-changes.sh
```

This script:

1. Builds `ai-job-engine` (backend) and `starhub-ui` (frontend) Docker images
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
./operator-starhub-test.sh monitor

# Watch a specific capability
./operator-starhub-test.sh monitor call-processing-prod/call-processing-prod
```

The monitor shows a live-updating table with each step's status, duration, and resources created.

## Post-Deployment Verification

```bash
./operator-starhub-test.sh verify-capability
```

This runs 4 verification sections:

1. **AWS Resources** - DynamoDB tables (ACTIVE), S3 buckets (accessible), SSM parameters, Secrets, Glue database, IAM role (IRSA check)
2. **Kubernetes Resources** - Pods (Running/Ready), Services, Ingress (ALB address), ServiceAccount (IRSA annotation)
3. **Application Health** - Frontend via ALB (HTTP 200), Backend via ALB, Internal health check from pod
4. **Connectivity** - IRSA token mounted, AWS identity from pod

## Common Operations

### Verify CRD

```bash
kubectl get crd totogicapabilities.totogi.com
kubectl api-resources | grep totogi
```

### Check RBAC

```bash
kubectl get clusterrole totogi-operator -o yaml
kubectl get clusterrolebinding totogi-operator -o yaml
kubectl get serviceaccount totogi-operator -n totogi-system -o yaml
```

### View Events

```bash
# Operator events
kubectl -n totogi-system get events --sort-by='.lastTimestamp' | tail -20

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
kubectl get totogicapability <name> -n <namespace> -o yaml > capability-backup.yaml
```

### Export All CRs

```bash
kubectl get totogicapabilities -A -o yaml > all-capabilities-backup.yaml
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
kubectl -n totogi-system set image deployment/totogi-operator \
  totogi-operator=764119721991.dkr.ecr.ap-southeast-1.amazonaws.com/totogi-operator:latest

# Or use management script
./operator-starhub-test.sh update
```

### Clean Up Failed Deployments

```bash
# List failed capabilities
kubectl get tc -A | grep Failed

# Force delete stuck capability
kubectl delete totogicapability <name> -n <namespace> --force --grace-period=0

# Remove finalizer if stuck
kubectl patch totogicapability <name> -n <namespace> \
  -p '{"metadata":{"finalizers":null}}' --type=merge
```

### Rotate IAM Credentials

IRSA handles credential rotation automatically. No manual rotation needed.

### Check IRSA Configuration

```bash
# Verify ServiceAccount annotation
kubectl get serviceaccount totogi-operator -n totogi-system -o yaml | grep eks.amazonaws.com

# Verify IAM role trust policy
aws iam get-role --role-name TotogiOperatorRole --query 'Role.AssumeRolePolicyDocument'
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
kubectl auth can-i --list --as=system:serviceaccount:totogi-system:totogi-operator
```

### Review IAM Role Policy

```bash
aws iam list-attached-role-policies --role-name TotogiOperatorRole
aws iam get-role-policy --role-name TotogiOperatorRole --policy-name TotogiOperatorPolicy
```

### Check Pod Security

```bash
kubectl get pod -n totogi-system -o jsonpath='{.items[*].spec.securityContext}'
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
| Check operator status | `./operator-starhub-test.sh status` |
| View operator logs | `kubectl -n totogi-system logs -f deployment/totogi-operator` |
| List capabilities | `kubectl get tc -A` |
| Describe capability | `kubectl describe tc <name>` |
| Watch capabilities | `kubectl get tc -A -w` |
| Delete capability | `kubectl delete tc <name>` |
| View events | `kubectl -n totogi-system get events` |
| Restart operator | `kubectl -n totogi-system rollout restart deployment/totogi-operator` |
| Check CRD | `kubectl get crd totogicapabilities.totogi.com` |

---

[← Back to Kubernetes Operator](index.md) | [Next: Troubleshooting →](troubleshooting.md)
