---
hide:
  - toc
---

# Migrating from the CallSense Toolkit

The legacy **CallSense Toolkit** product (Webex CC capture, call processing pipeline, NexusAI Toolkit Deployer wizard) has been retired. Its capabilities have been folded into the broader **NexusAI Data-AI Platform** -- a generalised AI Operating Layer for any enterprise system, not just contact centres.

## What changed

- **Generalised data ingestion.** The Webex Contact Center integration and call-processing pipeline are replaced by the Data Plane's three-mechanism hydration model (FDW Connectors, ETL Pipelines, CDC), which works for any enterprise system.
- **Generalised reasoning.** Sales Manager and Sales Rep dashboards are replaced by per-Solution **Views** following the four-views framework (Outcomes / Predict / Diagnose / Monitor).
- **Generalised automation.** The call-processing journey is replaced by the **Journeys** primitive, authored in the Journey Builder or via natural language with the AI Copilot.
- **Generalised deployment.** The NexusAI Toolkit Deployer is replaced by the [Nexus Capability Kubernetes Operator](../operational/kubernetes-operator/index.md).

## Where things moved

| Toolkit page (retired) | Data-AI Platform equivalent |
|---|---|
| NexusAI Toolkit Deployer User Guide | [Operations Overview](../operational/index.md) and [Kubernetes Operator](../operational/kubernetes-operator/index.md) |
| Webex CC integration / Call recording | [Data Plane](../planes/data-plane.md) (FDW / ETL / CDC connectors) |
| Call-processing pipeline / SFDC action | [AI Automation](../console/ai-automation.md) (Journeys, Journey Studio) |
| Sales Manager / Rep dashboards | [AI Analytics](../console/ai-analytics.md) (Views, four-views framework) |
| WXCC simulator | Retired. See the surviving [SFDC / CRM Simulator](../simulators/sfdc/index.md). |
| Toolkit Executive Summary | [Business Executive Summary](../business/source/executive-summary.md) (Data-AI Platform) |
| Toolkit AWS WAFR Compliance | [Technical Solution Architecture](../technical/solution-architecture.md) and [EKS Hardening](../technical/eks-hardening/README.md) |
| Capability Architecture | [Platform Architecture](../platform-architecture.md) and [AI Operating System](../ai-os/architecture.md) |

For escalation or transition support, contact the platform team.
