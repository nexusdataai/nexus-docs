# AWS Prerequisites & IAM Setup

This document details the AWS prerequisites and IAM permissions required before deploying the Totogi Kubernetes Operator.

## Overview

Before deploying the operator, you need to set up:

1. **EKS Cluster** with OIDC provider
2. **IAM Permissions** for the deploying user
3. **ECR Repository** for operator images
4. **Network Configuration** for AWS service access

## Prerequisites Checklist

| Requirement | Status | Notes |
|------------|--------|-------|
| EKS Cluster | Required | Kubernetes 1.27+ |
| OIDC Provider | Required | For IRSA authentication |
| IAM Permissions | Required | For deploying user |
| ECR Repository | Auto-created | Created by deployment script |
| VPC/Subnets | Required | Private subnets recommended |

---

## Exact Steps: Permission Setup (AWS Account + EKS Cluster)

If you already have an **AWS account** and an **EKS cluster**, follow these steps so the operator deploys correctly and capabilities can perform all their activities (DynamoDB, S3, Glue, SSM, Secrets Manager, Cognito, etc.).

### Who Needs What (Summary)

| Identity | Purpose | Permissions / Role | When Created |
|----------|---------|--------------------|--------------|
| **Deployer** (user or role running the deploy) | Create operator IAM role, push image to ECR, deploy operator to EKS | IAM (create role, ECR, EKS access) — you must set up | Before deployment |
| **Operator** (pod in cluster) | Provision AWS resources and create app roles when you apply a TotogiCapability | `totogi-operator-role` with `totogi-operator-policy` | Created automatically by deploy |
| **Capability** (app pods per capability) | Access DynamoDB, S3, Glue, SSM, Secrets, Athena, Cognito | `{capability}-{env}-app-role` with inline policy | Created automatically by operator when you deploy a capability |

No manual permission setup is needed for the operator role or for capability roles—only for the **deployer** and for **OIDC** on the cluster.

### Step 1: Enable OIDC on the EKS Cluster

IRSA (IAM Roles for Service Accounts) requires the cluster’s OIDC provider to be registered in IAM. Without this, the operator and capability pods cannot assume their IAM roles.

**Option A — eksctl (recommended if you use eksctl):**

```bash
eksctl utils associate-iam-oidc-provider \
  --cluster <your-cluster-name> \
  --region <your-region> \
  --approve
```

**Option B — Operator script (if the cluster already has an OIDC issuer but the provider is not in IAM):**

```bash
cd /path/to/starhub-deployer/kube-operator
./operator-starhub-test.sh fix-irsa
```

**Verify:** The cluster has an OIDC issuer and the provider exists in IAM (see [Pre-Deployment Verification](#pre-deployment-verification) for a full check script).

### Step 2: Grant IAM Permissions to the Deployer

The **identity** that will run the operator deploy (e.g. your IAM user, CI role, or an assumed role) must be able to:

- Create and configure the IAM role **totogi-operator-role** (trust policy + inline policy).
- Create the ECR repository **totogi-operator** (if it does not exist) and push the operator image.
- Access the EKS cluster (describe cluster, and either `eks update-kubeconfig` or aws-auth so the deployer can apply manifests).

Attach the required permissions to that role (or user) using **managed policies** (EKS, ECR, IAM full access). Replace `<role-name>` (or `<username>`) as needed.

### Step 3: Deploy the Operator

From a environment where the deployer identity has the permissions above and can reach the EKS cluster:

```bash
cd /path/to/starhub-deployer/kube-operator
./build-and-deploy.sh
```

Or build the image first, then deploy:

```bash
./build-and-push.sh
./operator-starhub-test.sh deploy
```

This will:

- Create the IAM role **totogi-operator-role** with IRSA trust for the operator ServiceAccount and attach **totogi-operator-policy** (DynamoDB, S3, SSM, Secrets Manager, Glue, IAM, EKS, Cognito).
- Create the ECR repository **totogi-operator** (if missing), build and push the operator image.
- Deploy the operator into the cluster and annotate the operator ServiceAccount with the role ARN so the pod uses IRSA.
- Optionally install the AWS Load Balancer Controller for ALB Ingress.

After this step, the operator is running and has all permissions it needs to provision resources and create capability roles.

### Step 4: Deploy Capabilities (No Extra Permission Setup)

When you create a **TotogiCapability** (e.g. `kubectl apply -f examples/call-processing-complete.yaml`), the operator will:

- Create the IAM role **{capability}-{env}-app-role** with IRSA trust for the capability namespace’s ServiceAccount.
- Attach an inline policy so the capability workload can use DynamoDB, S3, SSM, Secrets Manager, Glue, Athena, and Cognito as required.
- Provision the AWS resources (tables, buckets, parameters, secrets, etc.) and deploy the Kubernetes workloads.

You do **not** need to create any IAM roles or policies for capabilities. The operator creates them and the capability pods assume the app role via IRSA automatically.

### Minimal Checklist (What You Must Do)

1. **OIDC:** Ensure the EKS cluster has its OIDC provider registered in IAM (Step 1).
2. **Deployer permissions:** Attach the deployer policy (or managed policies) to the user/role that runs the deploy (Step 2).
3. **Deploy:** Run `./build-and-deploy.sh` (or equivalent) from the kube-operator directory (Step 3).
4. **Capabilities:** Apply TotogiCapability manifests as needed; no further permission setup required (Step 4).

### After Install: Can You Remove the Deployer Role?

**Yes.** Once the operator and capabilities are installed, the operator uses **totogi-operator-role** (IRSA) and each capability uses **{capability}-{env}-app-role** (IRSA). They do not use the deployer’s credentials. You can remove or greatly reduce the deployer’s IAM permissions for day-to-day operation.

**Minimal role to keep operator and capability functionality intact**

For ongoing use you only need **Kubernetes API access** to the EKS cluster so you can:

- Create, update, and delete **TotogiCapability** resources (`kubectl apply` / `kubectl delete`).
- Inspect operator and capability pods, logs, and status.

The operator and capability pods assume their own IAM roles via IRSA; they do not need the deployer’s IAM permissions.

**Minimal IAM for ongoing access (no deployer permissions):**

| Purpose | Required IAM / access |
|--------|------------------------|
| Run `kubectl` against the cluster | EKS cluster access so your identity can call the Kubernetes API. Typically: `eks:DescribeCluster`, `eks:ListClusters`, and `eks:AccessKubernetesApi` (or equivalent via EKS Access Entries). Your IAM user or role must be granted access in the cluster (e.g. EKS Access Entry or `aws-auth` ConfigMap). |
| Operator and capability workloads | No IAM needed from you. They use **totogi-operator-role** and **{capability}-{env}-app-role** via IRSA. |

**Example: minimal policy for a user who only manages TotogiCapability resources (no deployer powers):**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EKSClusterAccess",
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster",
        "eks:ListClusters",
        "eks:AccessKubernetesApi"
      ],
      "Resource": "*"
    }
  ]
}
```

You must also ensure this user/role is allowed to authenticate to the cluster (e.g. EKS Access Entry associating the principal with the cluster and a policy that allows API access, or an entry in the cluster’s `aws-auth` ConfigMap if the cluster uses that).

With only this, you can `kubectl apply` and `kubectl delete` TotogiCapability resources; the operator will continue to provision AWS resources and create capability IAM roles using **totogi-operator-role**.

**When you need deployer-level permissions again**

- **Upgrading the operator** (new image/code): You need to push a new image to ECR and update the operator deployment. That requires ECR push and cluster access (and possibly IAM if the operator role was recreated).
- **Re-creating the operator IAM role** (e.g. after accidental deletion): You need IAM permissions to create **totogi-operator-role** and attach **totogi-operator-policy** again.
- **Installing or updating the AWS Load Balancer Controller**: May require the same kind of IAM/ECR/cluster access as the initial deploy.

So you can use a **separate, minimal- privilege identity** for day-to-day capability management and keep the full deployer role only for upgrades and recovery.

The sections below give the detailed IAM policies, OIDC verification, ECR, and network options for reference.

---

## 2. IAM Permissions for Deploying User

The role (or user) that deploys the operator needs **EKS**, **ECR**, and **IAM** full access. Use AWS managed policies attached to the deploying role.

### Attach managed policies to the deploying role

```bash
# Replace <role-name> with your deploying role name
aws iam attach-role-policy --role-name <role-name> --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy
aws iam attach-role-policy --role-name <role-name> --policy-arn arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy
aws iam attach-role-policy --role-name <role-name> --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess
aws iam attach-role-policy --role-name <role-name> --policy-arn arn:aws:iam::aws:policy/IAMFullAccess
```

If you deploy as an **IAM user** instead of a role, use `attach-user-policy` and `--user-name <username>` in place of `attach-role-policy` and `--role-name <role-name>`.

---

## 3. Operator IAM Role (totogi-operator-role)

The operator itself needs an IAM role to provision AWS resources. This role is **automatically created** by the deployment flow (`operator-starhub-test.sh deploy` or `build-and-deploy.sh`, which use the deployer backend). The role name is **totogi-operator-role** and the inline policy name is **totogi-operator-policy**.

### Trust Policy (IRSA)

The trust policy allows the operator ServiceAccount to assume the role. When deployed via the kube-operator manifests, the ServiceAccount name is **totogi-operator** (namespace **totogi-system**). The deployer may create a ServiceAccount named **totogi-operator-sa**; ensure the trust policy subject matches the ServiceAccount name actually used by the operator pod.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<account-id>:oidc-provider/<oidc-provider-id>"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "<oidc-provider-id>:sub": "system:serviceaccount:totogi-system:totogi-operator",
          "<oidc-provider-id>:aud": "sts.amazonaws.com"
        }
      }
    }
  ]
}
```

`<oidc-provider-id>` is the OIDC issuer without `https://` (e.g. `oidc.eks.ap-southeast-1.amazonaws.com/id/XXXXX`).

### Operator Permissions Policy

The operator needs these permissions to provision AWS resources (aligned with `starhub-deployer` backend operator deployment service). Resources are scoped by account (and region where applicable):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoDBManagement",
      "Effect": "Allow",
      "Action": [
        "dynamodb:CreateTable",
        "dynamodb:DeleteTable",
        "dynamodb:DescribeTable",
        "dynamodb:UpdateTable",
        "dynamodb:TagResource",
        "dynamodb:ListTables"
      ],
      "Resource": "arn:aws:dynamodb:<region>:<account-id>:table/*"
    },
    {
      "Sid": "S3Management",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:DeleteBucket",
        "s3:PutBucketPolicy",
        "s3:PutBucketTagging",
        "s3:PutLifecycleConfiguration",
        "s3:PutBucketVersioning",
        "s3:GetBucketVersioning",
        "s3:PutBucketEncryption",
        "s3:GetBucketEncryption",
        "s3:PutBucketPublicAccessBlock",
        "s3:GetBucketPublicAccessBlock",
        "s3:GetBucketLocation",
        "s3:ListBucket",
        "s3:ListAllMyBuckets"
      ],
      "Resource": "arn:aws:s3:::*"
    },
    {
      "Sid": "SSMManagement",
      "Effect": "Allow",
      "Action": [
        "ssm:PutParameter",
        "ssm:DeleteParameter",
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:GetParametersByPath",
        "ssm:AddTagsToResource"
      ],
      "Resource": "arn:aws:ssm:<region>:<account-id>:parameter/*"
    },
    {
      "Sid": "SecretsManagerManagement",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:CreateSecret",
        "secretsmanager:DeleteSecret",
        "secretsmanager:GetSecretValue",
        "secretsmanager:PutSecretValue",
        "secretsmanager:UpdateSecret",
        "secretsmanager:TagResource",
        "secretsmanager:DescribeSecret",
        "secretsmanager:ListSecrets"
      ],
      "Resource": "arn:aws:secretsmanager:<region>:<account-id>:secret:*"
    },
    {
      "Sid": "GlueManagement",
      "Effect": "Allow",
      "Action": [
        "glue:CreateDatabase",
        "glue:DeleteDatabase",
        "glue:GetDatabase",
        "glue:GetDatabases",
        "glue:CreateTable",
        "glue:DeleteTable",
        "glue:UpdateTable",
        "glue:GetTable",
        "glue:GetTables",
        "glue:CreatePartition",
        "glue:BatchCreatePartition",
        "glue:UpdatePartition",
        "glue:DeletePartition",
        "glue:GetPartition",
        "glue:GetPartitions",
        "glue:BatchGetPartition",
        "glue:DeleteUserDefinedFunction",
        "glue:GetUserDefinedFunction",
        "glue:GetUserDefinedFunctions"
      ],
      "Resource": [
        "arn:aws:glue:<region>:<account-id>:catalog",
        "arn:aws:glue:<region>:<account-id>:database/*",
        "arn:aws:glue:<region>:<account-id>:table/*",
        "arn:aws:glue:<region>:<account-id>:userDefinedFunction/*"
      ]
    },
    {
      "Sid": "IAMRoleManagement",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:GetRole",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:UpdateAssumeRolePolicy",
        "iam:GetOpenIDConnectProvider",
        "iam:TagRole",
        "iam:PassRole"
      ],
      "Resource": "arn:aws:iam::<account-id>:role/*"
    },
    {
      "Sid": "EKSAccess",
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster",
        "eks:ListClusters"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CognitoManagement",
      "Effect": "Allow",
      "Action": [
        "cognito-idp:CreateUserPool",
        "cognito-idp:DeleteUserPool",
        "cognito-idp:DescribeUserPool",
        "cognito-idp:ListUserPools",
        "cognito-idp:CreateGroup",
        "cognito-idp:GetGroup",
        "cognito-idp:CreateUserPoolClient",
        "cognito-idp:DeleteUserPoolClient",
        "cognito-idp:DescribeUserPoolClient",
        "cognito-idp:ListUserPoolClients",
        "cognito-idp:CreateUserPoolDomain",
        "cognito-idp:DeleteUserPoolDomain",
        "cognito-idp:DescribeUserPoolDomain",
        "cognito-idp:ListUsersInGroup",
        "cognito-idp:AdminCreateUser",
        "cognito-idp:AdminGetUser",
        "cognito-idp:AdminAddUserToGroup",
        "cognito-idp:AdminSetUserPassword",
        "cognito-idp:TagResource",
        "cognito-idp:UntagResource"
      ],
      "Resource": "*"
    }
  ]
}
```

### Pre-create Operator Role (Optional)

If you want to pre-create the role instead of letting the deploy script create it:

```bash
# Get OIDC provider ID (no https://)
OIDC_PROVIDER=$(aws eks describe-cluster --name starhub-test --query "cluster.identity.oidc.issuer" --output text | sed 's|https://||')
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create trust policy file (use the SA name your deployment uses: totogi-operator or totogi-operator-sa)
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/${OIDC_PROVIDER}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "${OIDC_PROVIDER}:sub": "system:serviceaccount:totogi-system:totogi-operator",
          "${OIDC_PROVIDER}:aud": "sts.amazonaws.com"
        }
      }
    }
  ]
}
EOF

# Create role (name must be totogi-operator-role for deployer/scan to recognize it)
aws iam create-role \
  --role-name totogi-operator-role \
  --assume-role-policy-document file://trust-policy.json \
  --description "IAM role for Totogi Operator with IRSA"

# Attach inline policy (save operator-policy.json from above, with <region> and <account-id> replaced)
aws iam put-role-policy \
  --role-name totogi-operator-role \
  --policy-name totogi-operator-policy \
  --policy-document file://operator-policy.json
```

---

## 4. Application IAM Role

Each deployed capability gets its own IAM role with least-privilege access. The operator creates this automatically when reconciling a `TotogiCapability` (see `kube-operator` `IAMProvisioner`). Role name pattern: **{capability}-{env}-app-role**. Policy name: **{role-name}-policy**.

### Application Role Permissions

The following matches the operator implementation (`src/totogi_operator/resources/iam.py`), including DynamoDB indexes, Glue create/update, Athena, and Cognito read/admin for app backends:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:BatchGetItem",
        "dynamodb:BatchWriteItem",
        "dynamodb:DescribeTable"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:<account-id>:table/<capability>-<env>-*",
        "arn:aws:dynamodb:*:<account-id>:table/<capability>-<env>-*/index/*"
      ]
    },
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:DeleteObject",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::<capability>-<env>-*",
        "arn:aws:s3:::<capability>-<env>-*/*"
      ]
    },
    {
      "Sid": "SSMAccess",
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:GetParametersByPath"
      ],
      "Resource": "arn:aws:ssm:<region>:<account-id>:parameter/<capability>/<env>/*"
    },
    {
      "Sid": "SecretsAccess",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret",
        "secretsmanager:PutSecretValue",
        "secretsmanager:UpdateSecret",
        "secretsmanager:CreateSecret",
        "secretsmanager:DeleteSecret",
        "secretsmanager:TagResource"
      ],
      "Resource": [
        "arn:aws:secretsmanager:<region>:<account-id>:secret:<capability>/<env>/*",
        "arn:aws:secretsmanager:<region>:<account-id>:secret:<capability>-<env>-*"
      ]
    },
    {
      "Sid": "GlueAccess",
      "Effect": "Allow",
      "Action": [
        "glue:GetDatabase",
        "glue:GetDatabases",
        "glue:CreateDatabase",
        "glue:DeleteDatabase",
        "glue:GetTable",
        "glue:GetTables",
        "glue:CreateTable",
        "glue:UpdateTable",
        "glue:DeleteTable",
        "glue:GetPartition",
        "glue:GetPartitions",
        "glue:BatchGetPartition",
        "glue:CreatePartition",
        "glue:BatchCreatePartition",
        "glue:UpdatePartition",
        "glue:DeletePartition"
      ],
      "Resource": [
        "arn:aws:glue:<region>:<account-id>:catalog",
        "arn:aws:glue:<region>:<account-id>:database/<capability>*",
        "arn:aws:glue:<region>:<account-id>:table/<capability>*/*"
      ]
    },
    {
      "Sid": "AthenaAccess",
      "Effect": "Allow",
      "Action": [
        "athena:StartQueryExecution",
        "athena:GetQueryExecution",
        "athena:GetQueryResults",
        "athena:StopQueryExecution",
        "athena:GetWorkGroup"
      ],
      "Resource": "arn:aws:athena:<region>:<account-id>:workgroup/*"
    },
    {
      "Sid": "CognitoAccess",
      "Effect": "Allow",
      "Action": [
        "cognito-idp:AdminInitiateAuth",
        "cognito-idp:AdminRespondToAuthChallenge",
        "cognito-idp:AdminGetUser",
        "cognito-idp:AdminSetUserPassword",
        "cognito-idp:ListUsers",
        "cognito-idp:ListUsersInGroup",
        "cognito-idp:AdminListGroupsForUser",
        "cognito-idp:DescribeUserPool",
        "cognito-idp:DescribeUserPoolClient"
      ],
      "Resource": "arn:aws:cognito-idp:<region>:<account-id>:userpool/*"
    }
  ]
}
```

---

## 5. ECR Repository Setup

The ECR repository is automatically created by the deployment script. If you want to pre-create it:

```bash
# Create ECR repository
aws ecr create-repository \
  --repository-name totogi-operator \
  --region ap-southeast-1 \
  --image-scanning-configuration scanOnPush=true

# Get repository URI
aws ecr describe-repositories \
  --repository-names totogi-operator \
  --query 'repositories[0].repositoryUri' \
  --output text
```

---

## 6. Network Requirements

### VPC Configuration

Ensure your EKS cluster VPC has:

- **Private subnets** for worker nodes
- **NAT Gateway** for outbound internet access
- **VPC Endpoints** (optional, for private clusters)

### Required VPC Endpoints (for Private Clusters)

If running a fully private cluster, create these VPC endpoints:

```bash
# Required endpoints
aws ec2 create-vpc-endpoint --vpc-id <vpc-id> --service-name com.amazonaws.ap-southeast-1.ecr.api --vpc-endpoint-type Interface
aws ec2 create-vpc-endpoint --vpc-id <vpc-id> --service-name com.amazonaws.ap-southeast-1.ecr.dkr --vpc-endpoint-type Interface
aws ec2 create-vpc-endpoint --vpc-id <vpc-id> --service-name com.amazonaws.ap-southeast-1.s3 --vpc-endpoint-type Gateway
aws ec2 create-vpc-endpoint --vpc-id <vpc-id> --service-name com.amazonaws.ap-southeast-1.dynamodb --vpc-endpoint-type Gateway
aws ec2 create-vpc-endpoint --vpc-id <vpc-id> --service-name com.amazonaws.ap-southeast-1.sts --vpc-endpoint-type Interface
aws ec2 create-vpc-endpoint --vpc-id <vpc-id> --service-name com.amazonaws.ap-southeast-1.ssm --vpc-endpoint-type Interface
aws ec2 create-vpc-endpoint --vpc-id <vpc-id> --service-name com.amazonaws.ap-southeast-1.secretsmanager --vpc-endpoint-type Interface
```

---

## 7. Pre-Deployment Verification

Run this script to verify all prerequisites:

```bash
#!/bin/bash
# verify-prerequisites.sh

CLUSTER_NAME="starhub-test"
REGION="ap-southeast-1"

echo "=== Totogi Operator Prerequisites Check ==="

# Check AWS credentials
echo -n "1. AWS Credentials: "
if aws sts get-caller-identity > /dev/null 2>&1; then
    echo "✓ Valid"
else
    echo "✗ Invalid or expired"
    exit 1
fi

# Check EKS cluster
echo -n "2. EKS Cluster ($CLUSTER_NAME): "
if aws eks describe-cluster --name $CLUSTER_NAME --region $REGION > /dev/null 2>&1; then
    echo "✓ Exists"
else
    echo "✗ Not found"
    exit 1
fi

# Check OIDC provider
echo -n "3. OIDC Provider: "
OIDC_URL=$(aws eks describe-cluster --name $CLUSTER_NAME --region $REGION --query "cluster.identity.oidc.issuer" --output text)
OIDC_ID=$(echo $OIDC_URL | cut -d '/' -f 5)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if aws iam get-open-id-connect-provider --open-id-connect-provider-arn arn:aws:iam::${ACCOUNT_ID}:oidc-provider/oidc.eks.${REGION}.amazonaws.com/id/${OIDC_ID} > /dev/null 2>&1; then
    echo "✓ Configured"
else
    echo "✗ Not configured"
    echo "  Run: eksctl utils associate-iam-oidc-provider --cluster $CLUSTER_NAME --approve"
    exit 1
fi

# Check IAM permissions (operator role name used by deployer)
echo -n "4. IAM Permissions: "
if aws iam get-role --role-name totogi-operator-role > /dev/null 2>&1; then
    echo "✓ totogi-operator-role exists"
else
    echo "○ totogi-operator-role will be created during deployment"
fi

# Check ECR
echo -n "5. ECR Repository: "
if aws ecr describe-repositories --repository-names totogi-operator --region $REGION > /dev/null 2>&1; then
    echo "✓ Exists"
else
    echo "○ Will be created during deployment"
fi

echo ""
echo "=== All prerequisites satisfied! ==="
echo "You can now run: ./build-and-deploy.sh  (or ./operator-starhub-test.sh deploy)"
```

---

## Quick Setup Commands

### Complete Setup (Copy & Paste)

```bash
# Set variables
export CLUSTER_NAME="starhub-test"
export REGION="ap-southeast-1"

# 1. Associate OIDC provider (or use operator script to fix if missing)
eksctl utils associate-iam-oidc-provider \
  --cluster $CLUSTER_NAME \
  --region $REGION \
  --approve

# Alternatively: from kube-operator dir, fix IRSA (creates OIDC provider in IAM if missing)
# ./operator-starhub-test.sh fix-irsa

# 2. Verify setup
aws eks describe-cluster --name $CLUSTER_NAME --query "cluster.identity.oidc.issuer" --output text

# 3. Deploy operator (creates totogi-operator-role and ECR repo automatically)
cd /opt/mycode/trilogy/starhub-deployer/kube-operator
./build-and-deploy.sh
# Or: ./operator-starhub-test.sh deploy   (after building image separately)
```

The deploy step runs the deployer backend, which creates the operator IAM role **totogi-operator-role**, applies the operator manifests, and can install the AWS Load Balancer Controller for ALB Ingress support.

---

## Summary

| Component | Created By | When |
|-----------|------------|------|
| EKS Cluster | User | Before deployment |
| OIDC Provider | User (eksctl) or `fix-irsa` | Before or during deployment |
| Deployer IAM Permissions | User | Before deployment |
| totogi-operator-role | Deployer (operator-starhub-test.sh / build-and-deploy) | During deployment |
| ECR Repository | build-and-push / deploy | During deployment |
| Application IAM Roles ({capability}-{env}-app-role) | Operator | When capability deployed |

### Note on kube-operator/iam_policy.json

The file `starhub-deployer/kube-operator/iam_policy.json` is the IAM policy for the **AWS Load Balancer Controller** (ALB Ingress), not for the Totogi operator itself. It is used when installing the ALB Controller via `operator-starhub-test.sh install-alb-controller` (or automatically during `deploy`). The operator’s own permissions are created by the deployer as the inline policy **totogi-operator-policy** on **totogi-operator-role**.

---

[← Back to Kubernetes Operator](index.md) | [Next: Deployment Guide →](deployment.md)
