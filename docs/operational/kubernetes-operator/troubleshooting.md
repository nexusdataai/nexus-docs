# Troubleshooting

Common issues and solutions for the Totogi Kubernetes Operator.

## Quick Diagnostics

Run these commands to gather diagnostic information:

```bash
# Operator status
./operator-starhub-test.sh status

# Operator pods
kubectl -n totogi-system get pods

# Operator logs
kubectl -n totogi-system logs deployment/totogi-operator --tail=100

# Events
kubectl -n totogi-system get events --sort-by='.lastTimestamp' | tail -20

# CRD status
kubectl get crd totogicapabilities.totogi.com
```

## Common Issues

### Issue: kubectl Access Denied (401 Unauthorized)

**Symptoms:**
```
error: You must be logged in to the server (Unauthorized)
```

**Cause:** Not in aws-auth ConfigMap or Access Entry not configured.

**Solution:** The deploy script automatically fixes this. Run:

```bash
./operator-starhub-test.sh deploy
```

Or manually add to aws-auth:
```bash
kubectl patch configmap aws-auth -n kube-system --type merge -p '{
  "data": {
    "mapRoles": "- rolearn: YOUR_ROLE_ARN\n  username: admin:{{SessionName}}\n  groups:\n    - system:masters\n"
  }
}'
```

### Issue: ImagePullBackOff

**Symptoms:**
```
NAME                              READY   STATUS             RESTARTS   AGE
totogi-operator-xxx-xxx           0/1     ImagePullBackOff   0          5m
```

**Cause:** Operator image doesn't exist in ECR.

**Solution:** Build and push the image:

```bash
./build-and-push.sh
./operator-starhub-test.sh deploy --force
```

### Issue: Operator Pod Not Starting

**Symptoms:**
- Pod stuck in `Pending` or `CrashLoopBackOff`
- Status shows `0/1 Ready`

**Diagnosis:**

```bash
kubectl -n totogi-system describe pod -l app.kubernetes.io/name=totogi-operator
kubectl -n totogi-system logs deployment/totogi-operator
```

**Common causes and solutions:**

| Cause | Solution |
|-------|----------|
| Image pull errors | Check ECR permissions, run `./build-and-push.sh` |
| IRSA misconfiguration | Verify ServiceAccount annotation |
| Resource constraints | Check node capacity, adjust resource limits |
| Missing CRD | Run `kubectl apply -f manifests/crd.yaml` |

### Issue: Token Expiry Errors

**Symptoms:**
```
Unauthorized: token expired
```

**Status:** ✅ FIXED in current version

The operator uses kubeconfig which calls `aws eks get-token` for auto-refreshing tokens.

**If still occurring:**
```bash
# Refresh credentials
aws sso login --profile external-access
# or
aws sts get-caller-identity --profile external-access
```

### Issue: Capabilities Not Deploying

**Symptoms:**
- Capability stuck in `Pending` or `Provisioning`
- No AWS resources created

**Diagnosis:**

```bash
# Check operator logs
kubectl -n totogi-system logs -f deployment/totogi-operator

# Check capability status
kubectl describe totogicapability <name>

# Check events
kubectl get events -n <capability-namespace>
```

**Common causes:**

| Cause | Solution |
|-------|----------|
| AWS permissions | Check IAM role has required policies |
| Invalid spec | Validate capability YAML against CRD |
| Resource conflicts | Check for existing resources with same names |
| Region mismatch | Ensure region in spec matches cluster region |

### Issue: AWS Resource Creation Failed

**Symptoms:**
```
ERROR | Failed to create DynamoDB table: AccessDeniedException
```

**Solution:**

1. Check IAM role policy:
```bash
aws iam get-role-policy --role-name TotogiOperatorRole --policy-name TotogiOperatorPolicy
```

2. Verify required permissions:
    - `dynamodb:*` for DynamoDB operations
    - `s3:*` for S3 operations
    - `glue:*` for Glue operations
    - `iam:*` for IAM role creation
    - `ssm:*` for SSM parameters
    - `secretsmanager:*` for secrets

### Issue: IRSA Not Working

**Symptoms:**
```
Unable to locate credentials
NoCredentialProviders: no valid providers in chain
```

**Diagnosis:**

```bash
# Check ServiceAccount annotation
kubectl get sa totogi-operator -n totogi-system -o yaml | grep eks.amazonaws.com

# Verify OIDC provider
aws iam list-open-id-connect-providers

# Check IAM role trust policy
aws iam get-role --role-name TotogiOperatorRole --query 'Role.AssumeRolePolicyDocument'
```

**Solution:**

1. Ensure OIDC provider is associated:
```bash
eksctl utils associate-iam-oidc-provider --cluster <cluster-name> --approve
```

2. Verify ServiceAccount annotation matches IAM role ARN

### Issue: Capability Stuck in Deleting

**Symptoms:**
- Capability CR won't delete
- Stuck with finalizers

**Solution:**

```bash
# Remove finalizer
kubectl patch totogicapability <name> -n <namespace> \
  -p '{"metadata":{"finalizers":null}}' --type=merge

# Force delete
kubectl delete totogicapability <name> -n <namespace> --force --grace-period=0
```

### Issue: LoadBalancer Not Getting External IP

**Symptoms:**
- Service stuck in `<pending>` for external IP
- No load balancer created

**Diagnosis:**

```bash
kubectl describe service <service-name> -n <namespace>
kubectl get events -n <namespace> | grep LoadBalancer
```

**Common causes:**

| Cause | Solution |
|-------|----------|
| Missing AWS LB Controller | Install AWS Load Balancer Controller |
| Subnet tags missing | Add required Kubernetes tags to subnets |
| IAM permissions | Check LB controller role permissions |

## Advanced Troubleshooting

### Enable Debug Logging

```bash
# Set debug level
kubectl -n totogi-system set env deployment/totogi-operator LOG_LEVEL=DEBUG

# View debug logs
kubectl -n totogi-system logs -f deployment/totogi-operator
```

### Check AWS API Calls

```bash
# Enable CloudTrail logging
# View recent API calls for troubleshooting
```

### Verify Network Connectivity

```bash
# From operator pod
kubectl -n totogi-system exec -it deploy/totogi-operator -- python -c "
import boto3
sts = boto3.client('sts')
print(sts.get_caller_identity())
"
```

### Check Resource Quotas

```bash
kubectl describe resourcequota -n totogi-system
kubectl describe limitrange -n totogi-system
```

## Recovery Procedures

### Recover from Failed Deployment

```bash
# 1. Check what failed
kubectl describe totogicapability <name>

# 2. Delete the failed capability
kubectl delete totogicapability <name>

# 3. Clean up any partial AWS resources
aws dynamodb delete-table --table-name <capability>-<env>-transformation-system
aws s3 rb s3://<capability>-<env>-call-data --force

# 4. Redeploy
kubectl apply -f capability.yaml
```

### Recover from Operator Crash

```bash
# 1. Check crash reason
kubectl -n totogi-system logs deployment/totogi-operator --previous

# 2. Restart operator
kubectl -n totogi-system rollout restart deployment/totogi-operator

# 3. If persistent, redeploy
./operator-starhub-test.sh delete
./build-and-deploy.sh
```

### Reset Operator State

```bash
# 1. Delete operator
./operator-starhub-test.sh delete

# 2. Clean up CRs manually
kubectl delete totogicapabilities --all -A

# 3. Redeploy
./build-and-deploy.sh
```

## Getting Help

### Gather Information

Before reporting an issue, gather:

1. Operator status: `./operator-starhub-test.sh status`
2. Operator logs: `kubectl -n totogi-system logs deployment/totogi-operator`
3. Capability description: `kubectl describe tc <name>`
4. Events: `kubectl get events -A --sort-by='.lastTimestamp'`
5. AWS credentials: `aws sts get-caller-identity`

### Support Contacts

For internal support, contact the platform team with:
- Cluster name and region
- Error messages
- Steps to reproduce
- Diagnostic information gathered above

---

[← Back to Kubernetes Operator](index.md) | [← Previous: Operations Guide](operations.md)
