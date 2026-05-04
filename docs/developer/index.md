---
hide:
  - toc
---

# Developer Guide

Setup, code organisation, MCP tooling, and local development for engineers contributing to the NexusAI Data-AI Platform.

## In this section

| Topic | Page |
|---|---|
| Backend service overview (`nexus-backend`) | [Backend > Overview](backend/README.md) |
| `.env.local` template + LocalStack notes | [Backend > LocalStack Setup](backend/env-local-example.md) |
| Inside-sales / O2C-style requirement context | [Requirements](requirements/bussiness-req.md) |
| `journeys_tool` -- journey / stage / job MCP reference | [MCP Tools > Journeys Tool](mcp-tools/journeys-tool.md) |
| `run_jobs_tool` -- job lifecycle MCP reference | [MCP Tools > Run Jobs Tool](mcp-tools/run-job-tools.md) |
| `logs_and_reports_tool` -- TMF / journey log queries | [MCP Tools > Logs and Reports Tool](mcp-tools/logs-and-reports-tool.md) |
| MCP HTTP gateway internals (worker pool, streaming) | [MCP Tools > MCP Streaming Architecture](mcp-tools/MCP_STREAMING_ARCHITECTURE.md) |
| LocalStack quickstart | [LocalStack > Quick Start](localstack/QUICKSTART_LOCALSTACK.md) |
| Full LocalStack setup (DynamoDB, S3, CloudWatch, Athena emulation) | [LocalStack > Local Setup](localstack/LOCAL_SETUP_LOCALSTACK.md) |
| LocalStack command reference | [LocalStack > Reference](localstack/LOCALSTACK_REFERENCE.md) |
| Claude DevOps Assistant plugin | [Claude > User Guide](claude/user-guide.md) and [Quick Reference](claude/quick-ref.md) |

## Repository layout

| Repo | Purpose |
|---|---|
| `nexus-backend` | FastAPI services, MCP gateway, FDW + RAG + ReAct + tool registry |
| `nexus-ui` | React + TypeScript SPA -- the Console, Solution apps, AI Copilot, Workspace pages |
| `nexus-deployer` | Helm charts + EKS Operator (`NexusCapability` CRD) for production deployment |
| `nexus-docs` | This site (mkdocs-material) |

## Quick start

```bash
# Backend
cd /opt/mycode/nexus/nexus-backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
docker-compose -f docker-compose-localstack.yml up -d
export USE_LOCALSTACK=true LOCALSTACK_HOST=localhost LOCALSTACK_PORT=4566
python -m tests.localstack_automation.run_automation --setup
./gateway.sh start
./gateway.sh test

# Frontend
cd /opt/mycode/nexus/nexus-ui
npm install
npm run dev

# Docs
cd /opt/mycode/nexus/nexus-docs
mkdocs serve   # http://localhost:8000
```

## Development workflow

- **Branch** -- one branch per feature; PR into `dev` first, promote to `main` on green.
- **Tests** -- backend `pytest tests/unit/`, integration via LocalStack, BDD via `behave`; frontend `npm run test`. See [Tests](../tests/index.md) for the full layered strategy.
- **Lint / type-check** -- backend ruff + mypy; frontend ESLint + tsc.
- **Pre-commit** -- enforced via the standard `.git/hooks` configured by `pre-commit install`.

## Adding new code

| Adding a... | Where it goes | Tests live in |
|---|---|---|
| REST endpoint | `nexus-backend/src/apis/` | `tests/integration/python/api/` |
| MCP tool | `nexus-backend/src/services/control_plane/tools/` (registered in `tool_registry.py`) | `tests/unit/` + `tests/bdd/features/` |
| Journey stage | `nexus-backend/src/stages/` (subclass `BaseStage`) | `tests/unit/` |
| Per-Solution app section | `nexus-ui/src/components/apps/sections/` | `nexus-ui/src/components/apps/sections/__tests__/` |
| Solution-app tool | one entry in `APP_TOOLS` map in `nexus-ui/src/components/apps/sections/AppToolsCatalogue.tsx` | n/a (ships with Solution) |
| Vertical Solution catalogue | `nexus-docs/docs/app-catalogue/{vertical}/` (markdown + ontology subfolder) | n/a |

## Code standards

- **Python**: PEP 8, type hints on every public function, max line 100, docstrings on services and APIs.
- **TypeScript**: strict mode, functional components, prop typing required, no `any` without justification.

## Related references

- [Platform Architecture](../platform-architecture.md) -- conceptual + screen-by-screen tour.
- [Implementation Guide](../ai-os/implementation-guide.md) -- code paths mapped to architecture.
- [Tests](../tests/index.md) -- test infrastructure across all tiers.
- [Operations](../operational/index.md) -- how the code you write gets deployed.
