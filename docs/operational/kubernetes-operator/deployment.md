# Deployment Guide

Step-by-step guide for deploying the Totogi Kubernetes Operator.

## Prerequisites

### Required

| Requirement | Version | Purpose |
|------------|---------|---------|
| EKS Cluster | 1.27+ | Kubernetes platform |
| AWS CLI | 2.x | AWS access |
| Python | 3.9+ | Scripts and operator |
| OIDC Provider | - | IRSA authentication |

### Python Dependencies

```bash
pip install kubernetes boto3 pyyaml
```

### AWS Permissions

The deploying user needs these permissions:

- **EKS**: DescribeCluster, ListClusters, AccessKubernetesApi
- **IAM**: CreateRole, AttachRolePolicy, CreateOpenIDConnectProvider
- **ECR**: CreateRepository, PutImage, GetAuthorizationToken
- **STS**: GetCallerIdentity, AssumeRole

## Deployment Scripts

All scripts are located in `/opt/mycode/trilogy/starhub-deployer/kube-operator/`.

### Script Overview

| Script | Purpose |
|--------|---------|
| `build-and-deploy.sh` | Build image and deploy (all-in-one) |
| `build-and-push.sh` | Build and push image to ECR |
| `operator-starhub-test.sh` | Manage operator lifecycle |

## Deployment Methods

### Method 1: One-Command Deployment (Recommended)

```bash
cd /opt/mycode/trilogy/starhub-deployer/kube-operator
./build-and-deploy.sh
```

This script:
1. Builds the operator Docker image
2. Creates ECR repository if needed
3. Pushes image to ECR
4. Deploys operator to cluster
5. Verifies health

### Method 2: Step-by-Step Deployment

#### Step 1: Scan Cluster (Optional)

```bash
./operator-starhub-test.sh scan
```

Verifies:
- Cluster exists and is active
- EKS version compatibility
- OIDC provider configured
- Your access level
- Node groups health

#### Step 2: Build and Push Image

```bash
./build-and-push.sh
```

This:
- Builds Docker image from `Dockerfile`
- Creates ECR repository `totogi-operator`
- Pushes image to ECR

#### Step 3: Deploy Operator

```bash
./operator-starhub-test.sh deploy
```

This:
- Creates `totogi-system` namespace
- Applies CRD
- Creates RBAC resources
- Creates IAM role with IRSA
- Deploys operator

#### Step 4: Verify Deployment

```bash
./operator-starhub-test.sh status
```

Expected output:
```
✓ Operator is installed
  Status: installed
  Version: latest
  Namespace: totogi-system
  Ready replicas: 1/1

✓ Operator is healthy and running
```

## Using Python Scripts Directly

For more control, use the Python scripts directly:

### deploy_operator_to_cluster.py

```bash
cd /opt/mycode/trilogy/starhub-deployer/backend

python3 scripts/deploy_operator_to_cluster.py \
  --cluster starhub-test \
  --region ap-southeast-1 \
  --profile external-access
```

**Options:**

| Option | Description |
|--------|-------------|
| `--cluster` | EKS cluster name (required) |
| `--region` | AWS region (default: ap-southeast-1) |
| `--profile` | AWS profile name |
| `--session-id` | AWS session ID (for UI integration) |
| `--version` | Operator version (default: latest) |
| `--force` | Force redeploy |
| `--skip-verify` | Skip cluster verification |
| `--skip-access-check` | Skip access check |
| `--debug` | Enable debug logging |

### cleanup_operator.py

```bash
# Safe cleanup (keeps IAM, ECR, access)
python3 scripts/cleanup_operator.py \
  --cluster starhub-test \
  --profile external-access

# Keep IAM and ECR
python3 scripts/cleanup_operator.py \
  --cluster starhub-test \
  --profile external-access \
  --keep-iam --keep-ecr

# Complete cleanup (removes access)
python3 scripts/cleanup_operator.py \
  --cluster starhub-test \
  --profile external-access \
  --remove-aws-auth
```

## Deploying Capabilities

Once the operator is running, deploy capabilities using CRs.

### Deploy Test Capability

```bash
kubectl apply -f examples/test-capability.yaml
```

### Watch Deployment Progress

```bash
# Watch capability status
kubectl get totogicapabilities -A -w

# View operator logs
kubectl -n totogi-system logs -f deployment/totogi-operator
```

### Check Created Resources

```bash
# Kubernetes resources
kubectl get all -n call-processing-dev

# AWS resources
aws dynamodb list-tables | grep call-processing
aws s3 ls | grep call-processing
aws iam get-role --role-name call-processing-dev-app-role
```

## Production Deployment Checklist

### Pre-Deployment

- [ ] EKS cluster is healthy and accessible
- [ ] OIDC provider is configured
- [ ] IAM permissions are in place
- [ ] Container images are built and pushed
- [ ] SSL certificates are ready (if using HTTPS)
- [ ] DNS is configured (if using custom domain)

### Deployment

- [ ] Operator deployed successfully
- [ ] Operator pod is running (1/1 Ready)
- [ ] CRD is installed
- [ ] RBAC is configured

### Post-Deployment

- [ ] Health check endpoints responding
- [ ] Operator logs show no errors
- [ ] Test capability deploys successfully
- [ ] AWS resources are created correctly

## Updating the Operator

### Update with New Image

```bash
cd /opt/mycode/trilogy/starhub-deployer/kube-operator

# Rebuild and redeploy
./build-and-deploy.sh
```

### Update Without Rebuild

```bash
./operator-starhub-test.sh update
```

### Force Redeployment

```bash
./operator-starhub-test.sh deploy --force
```

## Deleting the Operator

### Safe Delete (Recommended)

Preserves IAM roles, ECR repository, and access:

```bash
./operator-starhub-test.sh delete
```

### Complete Cleanup

Removes everything including access:

```bash
./operator-starhub-test.sh delete --full
```

!!! warning "Access Loss"
    Using `--full` may remove your cluster access. Ensure you have another way to access the cluster.

## Multi-Cluster Deployment

To deploy to multiple clusters:

```bash
# Cluster 1
python3 scripts/deploy_operator_to_cluster.py \
  --cluster cluster-1 \
  --region us-east-1

# Cluster 2
python3 scripts/deploy_operator_to_cluster.py \
  --cluster cluster-2 \
  --region ap-southeast-1
```

## Configuration

### Operator Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | INFO | Logging level |
| `OPERATOR_NAMESPACE` | totogi-system | Operator namespace |
| `AWS_REGION` | ap-southeast-1 | AWS region |

### Customizing Deployment

Edit `manifests/deployment.yaml` to customize:
- Resource limits
- Environment variables
- Node affinity
- Tolerations

---

[← Back to Kubernetes Operator](index.md) | [Next: Operations Guide →](operations.md)
