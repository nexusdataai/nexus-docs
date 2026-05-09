---
hide:
  - toc
---

# Operations

How the NexusAI Data-AI Platform is deployed, run, and operated. The platform is Kubernetes-native -- the **Nexus Capability Operator** reconciles `NexusCapability` custom resources on any EKS or compatible cluster (cloud or on-premise).

## In this section

| Topic | Page |
|---|---|
| Operator overview | [Kubernetes Operator > Overview](kubernetes-operator/index.md) |
| 5-minute install | [Quick Start](kubernetes-operator/quick-start.md) |
| AWS prerequisites (IAM, EKS, ALB, ACM, secrets) | [AWS Prerequisites](kubernetes-operator/aws-prerequisites.md) |
| Operator architecture | [Architecture](kubernetes-operator/architecture.md) |
| `NexusCapability` CRD reference | [Custom Resource Reference](kubernetes-operator/custom-resource.md) |
| End-to-end deployment guide | [Deployment Guide](kubernetes-operator/deployment.md) |
| Day-2 operations (upgrade / scale / backup) | [Operations](kubernetes-operator/operations.md) |
| Incident triage | [Troubleshooting](kubernetes-operator/troubleshooting.md) |

## Day-2 operations at a glance

- **Health & monitoring** -- CloudWatch dashboards (or your Prometheus equivalent), service health, pod status, FDW connection health, agent / journey success rates.
- **Capability lifecycle** -- the operator handles install, upgrade, scale, and rollback for every Capability via the CRD.
- **Backup & recovery** -- DynamoDB point-in-time recovery for journey / job state; S3 versioning for audit logs and journey artefacts; multi-AZ EKS for HA.
- **Re-indexing the Knowledge Pipeline** -- `POST /api/v1/control-plane/index` after any ontology change (~40 s for a 1,661-table FDW). See [Implementation Guide](../ai-os/implementation-guide.md#re-indexing-after-schema-changes).
- **Cost management** -- right-size pods through the CRD, manage S3 lifecycle policies for old journey artefacts, set CloudWatch budget alarms.
- **Security operations** -- rotate Cognito and OpenAI secrets via Secrets Manager, periodic IAM review, CloudTrail audit, FDW credential rotation.

## Common commands

```bash
# Operator status
kubectl get nexuscapability -A
kubectl describe nexuscapability <name> -n <ns>

# Backend / frontend health
kubectl get pods -n nexus-ai-prod
kubectl logs -f -n nexus-ai-prod -l app=nexus-ai-prod-backend

# Re-index Control Plane after ontology changes
curl -X POST https://<host>/api/v1/control-plane/index

# Rebuild & redeploy the app stack
cd /opt/mycode/nexus/nexus-deployer/kube-operator
./deploy-app-changes.sh
```

## Related references

- [Platform Architecture](../platform-architecture.md) -- system shape and deployment topology.
- [Technical > Solution Architecture](../technical/solution-architecture.md) -- detailed AWS / EKS topology.
- [Implementation Guide](../ai-os/implementation-guide.md) -- production code mapping (`nexus-backend`, `nexus-ui`, BSSMagic, FDW, pgvector).
