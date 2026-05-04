---
hide:
  - toc
---

# Developer Requirements

The platform's authoritative business and functional requirements live elsewhere. This page is a pointer for engineers who land here from the developer nav.

## Where to find requirements

| For... | See |
|---|---|
| Business case, target market, ROI, commercial model | [Business > Executive Summary](../../business/source/executive-summary.md) |
| Functional + non-functional requirements catalogue (per Plane / Console / Solution / Operations) | [Business > Business Requirements](../../business/source/business-requirements.md) |
| Functional surface (screen-by-screen) | [Platform Architecture](../../platform-architecture.md) |
| Per-Plane drill-downs | [Data Plane](../../planes/data-plane.md), [Control Plane](../../planes/control-plane.md), [Reasoning Plane](../../planes/reasoning-plane.md) |
| Per-Console drill-downs | [Solutions Catalogue](../../console/solutions-catalogue.md), [AI Analytics](../../console/ai-analytics.md), [AI Automation](../../console/ai-automation.md) |
| Per-Solution catalogues | [Application Catalogue](../../app-catalogue/supply-chain/index.md) (and the 6 sibling verticals) |
| KPI definitions (platform + per-Solution) | [KPI Definitions](../../KPI/nexus-kpi-definitions.md) |

## When you're adding a new requirement

- If it changes the user-facing product surface, update [Platform Architecture](../../platform-architecture.md) and the relevant Plane / Console drill-down.
- If it changes the platform's KPIs or success metrics, update [KPI Definitions](../../KPI/nexus-kpi-definitions.md).
- If it changes the business case (pricing, ROI, target market), update [Business Requirements](../../business/source/business-requirements.md) and [Executive Summary](../../business/source/executive-summary.md).
- If it changes a Solution's ontology or KPIs, update the per-Solution page in the [Application Catalogue](../../app-catalogue/supply-chain/index.md).
- For UAT acceptance criteria, update [UAT Test Cases](../../UAT/testcases/nexus-uat-testcases.md).
