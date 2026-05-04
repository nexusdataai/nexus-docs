# UAT Test Cases -- NexusAI Data-AI Platform

User Acceptance Testing (UAT) scenarios for the NexusAI Data-AI Platform. Test cases are organised by Plane, Console surface, and Solution app, mapping directly to the [Platform Architecture](../../platform-architecture.md) screens and the [Business Requirements](../../business/source/business-requirements.md) functional requirements.

For the developer-side test infrastructure (unit / integration / BDD / endurance / E2E), see [Tests](../../tests/index.md).

---

## 1. Prerequisites

| Requirement | Detail |
|---|---|
| Application access | NexusAI Console on the deployment host |
| User accounts | One per role: Admin, Operations, Analyst, Read-only |
| Data sources | At least one connected enterprise system (real FDW or SFDC simulator) |
| Solution(s) under test | Order-to-Cash Monitor activated as the canonical example |
| Browser | Chrome or Edge (latest) |
| Test data | Minimum 10 representative entities per tested Solution; at least one Journey with completed runs |

---

## 2. Data Plane

| ID | Test case | Steps | Expected | Status |
|---|---|---|---|---|
| DP-1 | Data Sources health | Open Data Plane > Data Sources | All connected sources show as healthy with table / row counts | |
| DP-2 | Mode toggle | Toggle FDW <-> Simulator on a source | Subsequent queries route through the chosen mode | |
| DP-3 | Entity Explorer | Select an entity (e.g. `Opportunity`) | Schema fields, relationships, and live row preview render | |
| DP-4 | Mapping Rule create | Create a new mapping rule with field mappings | Resolved mapping summary + live preview match expected rows | |
| DP-5 | Pipeline run | Trigger a pipeline manually | Stage flow renders Extract -> Validate -> Transform -> Load -> Verify; recent runs list updates with row counts | |
| DP-6 | Connector configure | Open a connector card and click Configure | Connector configuration form renders with the documented Inputs / Outputs | |

## 3. Control Plane

| ID | Test case | Steps | Expected | Status |
|---|---|---|---|---|
| CP-1 | Knowledge Pipeline run | Trigger the Knowledge Pipeline | All six stages complete (Extract Unified Schema -> Resolve FDW Mapping -> Extract Mapping Rules -> Extract Policies -> Extract Workflows -> Extract Integrations) and counters update | |
| CP-2 | Knowledge Index search | Filter by Schemas / Policies / Workflows / Integrations and select a document | Right pane shows full metadata + canonical YAML body | |
| CP-3 | Knowledge Graph render | Open Knowledge Graph tab | Nodes are colour-coded by source system; typed edges are visible | |
| CP-4 | Policy author | Open Policy Builder, select a policy, edit Constraints / Approval Matrix / Restrictions | Edits save; Knowledge Pipeline picks up the change on next run | |
| CP-5 | Workflow author | Open Workflows, select a YAML workflow | Header, Trigger, Description, Steps, and Dependencies render correctly | |
| CP-6 | Integration author | Open Integration Rules, select a sync rule | Source <-> Target wiring, frequency, and Field Mappings render correctly | |

## 4. Reasoning Plane

| ID | Test case | Steps | Expected | Status |
|---|---|---|---|---|
| RP-1 | AI Copilot read | Ask a read-only question (e.g. *"Which system is the source of truth for customer credit limits?"*) | Answer renders; agent steps are inspectable; intent badge = `read only`; token count surfaced | |
| RP-2 | AI Copilot tool trace | Expand any agent step | Tool name, latency, input args, and output preview are visible | |
| RP-3 | Planning Playground | Run a query in the Semantic RAG Query input | Retrieval Bundle, Graph View, and Test Suite tabs populate; Retrieval Quality Score is displayed | |
| RP-4 | ReAct Tools list | Open ReAct Tools tab | All registered tools render with read-only / write-capable tags | |
| RP-5 | Policy block | Ask a question that would require a write the user is not permitted to perform | Agent halts with a `policy_violation` event; no write is executed | |
| RP-6 | Approval gate | Trigger a high-risk write (e.g. `create_salesforce_lead`) | Action waits on explicit approval; on approve, the write completes and is audited | |

## 5. AI Analytics

| ID | Test case | Steps | Expected | Status |
|---|---|---|---|---|
| AN-1 | Dashboards browse | Open Dashboards tab | Card grid shows every dashboard with name, description, panel count, last-updated, classification + Solution tags | |
| AN-2 | Views browse | Open Views tab | Auto-seeded four-views (`outcomes` / `predict` / `diagnose` / `monitor`) appear for every Solution | |
| AN-3 | Solution Mapping | Open Solution Mapping; Add a View to a Solution | Solution row updates view count; the mapped View shows up in the Solution app's left navigation | |
| AN-4 | Dashboard Builder -- panel | Click + New Dashboard, pick Bar Chart | Panel editor opens with empty preview, Title input, Discard / Apply, Query / Visualization tabs | |
| AN-5 | Dashboard Builder -- AI Query | Type *"show top 10 vendors by risk score"* and click Generate | Structured Query A populates; one-line description appears; chart renders against the Virtual Entity | |
| AN-6 | Dashboard Builder -- persist | Click Apply | Panel adds to the dashboard; Save persists the dashboard | |

## 6. AI Automation

| ID | Test case | Steps | Expected | Status |
|---|---|---|---|---|
| AU-1 | Journeys list | Open Journeys tab | Card grid shows every journey with JRN-id, type chip, status, run counters, success rate, avg duration | |
| AU-2 | AI Copilot Journey | Type a goal in `What do you want to automate?` and submit | Draft journey of typed steps returned; steps reference real registered tools | |
| AU-3 | Journey Builder authoring | Drag a tool from the Tool Palette into the canvas | Step is added; Step Editor opens for per-step config | |
| AU-4 | Journey validate | Click Validate on a wired journey | Validation passes; Save and Run become enabled | |
| AU-5 | Journey trigger | Set trigger to Manual and click Run | Job starts; Journey card counters update in near real time | |
| AU-6 | Journey Studio | From a Journey card, click Journey Studio | Per-journey console renders KPI tiles, Processing Stages, Stage detail, and ordered Stage Steps with Logs (N) drill-in | |

## 7. Solutions Catalogue

| ID | Test case | Steps | Expected | Status |
|---|---|---|---|---|
| SC-1 | Browse catalogue | Open Solutions | All Solutions render with icon, priority badge, status, KPI targets, source-entity chips | |
| SC-2 | Filter by vertical | Click a vertical chip (e.g. Operations) | Catalogue filters to matching Solutions only | |
| SC-3 | Open App | Click Open App on Order-to-Cash Monitor | Solution workspace opens with Analytics / Views / Workspace left nav and Manage Views / Run Journey actions | |
| SC-4 | Business Insights | Open Business Insights | Hero KPI strip (DSO, Match Rate, Leakage, On-Time Payment), stat tiles, capability cards, entity strip render | |
| SC-5 | Process Analytics | Open Process Analytics | KPI tiles show actual vs target; Order Match Status donut and Top Anomaly Scores bar render; Top Risk Orders table populates | |
| SC-6 | Workflow Actions | Open Workflow Actions | Action-type counters and Action Log feed populate from real journey runs | |
| SC-7 | Reports | Open Reports | Severity counters and alert feed populate; alert rows show type, target, deviation, remediation | |
| SC-8 | View navigation | Click each of O2C Monitor / Diagnose / Predict / Act & Outcomes | Each View renders intent-specific panels; multi-tab Views show Tab 1 / Tab 2 sub-tabs where authored | |
| SC-9 | Agent Builder | Open Agent Builder | Custom Tools, Journey Templates, Agent Profiles, Test Harness cards render | |
| SC-10 | Tools Catalogue | Open Tools Catalogue | App-curated tools render with typed Inputs / Outputs, availability, Try Tool action | |

## 8. Operations

| ID | Test case | Steps | Expected | Status |
|---|---|---|---|---|
| OP-1 | Pod readiness | `kubectl get pods -n nexus-ai-prod` | Backend, frontend, and BSSMagic pods are Ready; counts match the K8s Operator's spec | |
| OP-2 | FDW health | `curl /api/v1/health/fdw` | Healthy; foreign-server count > 0 | |
| OP-3 | Re-index | `curl -X POST /api/v1/control-plane/index` | Returns `{status: ok, indexed: {servers: N, tables: N, errors: 0}}` | |
| OP-4 | Audit trail | After an agent session, query DynamoDB `control-plane-audit` | Per-step records present (intent, tool calls, results, policy violations) | |

## 9. Cross-cutting non-functional

| ID | Test case | Expected |
|---|---|---|
| NFR-1 | Knowledge Graph query latency | < 2 seconds |
| NFR-2 | Agent latency for standard workflows | < 5 seconds |
| NFR-3 | Dashboard render | < 2 seconds |
| NFR-4 | RBAC enforcement | Access denied returns 403 with no data leak |
| NFR-5 | Audit completeness | Every write surface produces an audit record |
| NFR-6 | Data residency | All data stays in customer-controlled infrastructure (no egress to vendor) |

---

## Related references

- [Platform Architecture](../../platform-architecture.md) -- screen-by-screen tour these tests exercise.
- [Business Requirements](../../business/source/business-requirements.md) -- functional + non-functional requirements catalogue.
- [Tests](../../tests/index.md) -- developer-side automated test infrastructure.
- [Implementation Guide](../../ai-os/implementation-guide.md) -- code paths under test.
