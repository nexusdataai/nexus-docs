# Quick Start Guide

Get the Nexus Kubernetes Operator running in minutes.

## Prerequisites

Before starting, ensure you have:

- EKS cluster (e.g., `nexus-dev`)
- AWS CLI configured with credentials
- Python 3.9+ installed

### Install Python Dependencies

```bash
pip install kubernetes boto3 pyyaml
```

## Deploy in 4 Steps

```bash
# Step 1: Navigate to operator directory
cd /opt/mycode/nexus/nexus-deployer/kube-operator

# Step 2: Scan cluster (optional but recommended)
./operator-nexus-dev.sh scan

# Step 3: Build and deploy (one command)
./build-and-deploy.sh

# Step 4: Verify
./operator-nexus-dev.sh status
```

Done! The operator is running. ✅

## Pre-Deployment Scan (Recommended)

Before deploying, run a comprehensive scan:

```bash
./operator-nexus-dev.sh scan
```

This checks:

- ✅ Cluster exists and is active
- ✅ EKS version compatibility
- ✅ OIDC provider configured
- ✅ Authentication mode
- ✅ Your access level
- ✅ Node groups health
- ✅ ECR pull permissions
- ✅ Python K8s client works
- ✅ kubectl works
- ✅ Ready for operator deployment

**Example output:**
```
[✓] CLUSTER IS READY FOR OPERATOR DEPLOYMENT
```

## Verify Deployment

### Check Operator Status

```bash
./operator-nexus-dev.sh status
```

**Expected output when healthy:**
```
✓ Operator is installed
  Status: installed
  Version: latest
  Namespace: nexus-system
  Ready replicas: 1/1

✓ Operator is healthy and running
```

### Check Pods

```bash
kubectl -n nexus-system get pods
```

Expected:
```
NAME                              READY   STATUS    RESTARTS   AGE
nexus-operator-xxx-xxx           1/1     Running   0          2m
```

### View Logs

```bash
kubectl -n nexus-system logs -f deployment/nexus-operator
```

## Deploy a Test Capability

Once the operator is running, deploy a test capability:

```bash
# Apply test capability
kubectl apply -f examples/test-capability.yaml

# Watch deployment progress
kubectl get nexuscapabilities -A -w

# Check status
kubectl describe nexuscapability nexus-ai-dev
```

## Success Criteria

You'll know deployment succeeded when:

1. ✅ Build script shows: "✓ Image pushed successfully"
2. ✅ Deploy script shows: "✓ DEPLOYMENT COMPLETE"
3. ✅ Status shows: "✓ Operator is healthy and running"
4. ✅ Pods show: `1/1 Running`

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `./build-and-deploy.sh` | Build image and deploy operator |
| `./operator-nexus-dev.sh deploy` | Deploy operator only |
| `./operator-nexus-dev.sh status` | Check operator health |
| `./operator-nexus-dev.sh update` | Update operator |
| `./operator-nexus-dev.sh delete` | Safe delete (keeps IAM/ECR) |
| `./operator-nexus-dev.sh delete --full` | Complete cleanup |

## What Each Script Does

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `build-and-push.sh` | Build Docker image, push to ECR | After code changes |
| `build-and-deploy.sh` | Build + deploy in one command | First time setup, or after code changes |
| `operator-nexus-dev.sh` | Manage operator lifecycle | Daily operations |

## Tips

1. **First time?** Use `./build-and-deploy.sh` - it does everything
2. **Code changes?** Use `./build-and-deploy.sh` - rebuilds and redeploys
3. **Just checking?** Use `./operator-nexus-dev.sh status` - quick health check
4. **Redeploying?** Use `./operator-nexus-dev.sh update` - faster than full rebuild
5. **Cleaning up?** Use `./operator-nexus-dev.sh delete` - safe delete preserves IAM/ECR

## No kubectl Required

All scripts use the **Python Kubernetes API** - no kubectl binary needed!

**What you need:**
- Python 3.9+
- AWS credentials
- Python packages: `kubernetes`, `boto3`, `pyyaml`

---

[← Back to Kubernetes Operator](index.md) | [Next: Architecture →](architecture.md)
