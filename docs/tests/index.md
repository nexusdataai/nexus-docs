# Tests

The NexusAI Data-AI Platform ships a layered automated test infrastructure across the backend (Python) and frontend (TypeScript / React). Tests are organised into seven tiers, each targeting a different layer of confidence.

| Tier | Framework | Location | Server needed | AWS needed |
|---|---|---|:---:|:---:|
| Unit | pytest | `nexus-backend/tests/unit/` | no | moto mocks |
| Property | pytest + Hypothesis | `nexus-backend/tests/property/` | no | LocalStack (some) |
| Integration (Python) | pytest | `nexus-backend/tests/integration/python/` | yes | moto |
| Integration (Shell) | bash | `nexus-backend/tests/integration/shell/` | yes | -- |
| BDD | behave | `nexus-backend/tests/bdd/features/` | yes | -- |
| Endurance | behave + custom runner | `nexus-backend/tests/endurance/` | yes | optional |
| E2E | pytest | `nexus-backend/tests/e2e/` | yes | live |
| Frontend Unit | vitest + React Testing Library | `nexus-ui/src/**/__tests__/` | no | -- |

All backend paths are relative to `/opt/mycode/nexus/nexus-backend`.

## Test runner

The primary orchestrator is `tests/run_tests.sh` (~1,600 lines). It handles environment setup, test execution across all tiers, report generation, and optional upload to CloudFront.

```bash
cd /opt/mycode/nexus/nexus-backend

./tests/run_tests.sh smoke            # < 1 min sanity
./tests/run_tests.sh unit             # all unit tests
./tests/run_tests.sh integration      # requires running gateway
./tests/run_tests.sh bdd              # all BDD scenarios
./tests/run_tests.sh endurance        # default 30 min stability
./tests/run_tests.sh all              # everything
./tests/run_tests.sh all --upload     # everything + publish reports
./tests/run_tests.sh consolidated-report
./tests/run_tests.sh clean
```

### Common flags

| Flag | Description |
|---|---|
| `--server URL` / `-s URL` | Target server URL (default `http://localhost:8000`) |
| `--insecure` / `-k` | Skip SSL verification |
| `--upload` / `-u` | Upload reports to CloudFront after the run |

### Common env vars

| Variable | Default | Description |
|---|---|---|
| `SERVER_URL` | `http://localhost:8000` | Backend server URL |
| `VERBOSE` | `false` | Verbose output |
| `JSON_OUTPUT` | `false` | JSON-formatted output |
| `UPLOAD_TO_S3` | `false` | Auto-upload reports |
| `S3_BUCKET_NAME` | `ai-engine-test-reports` | S3 bucket for reports |
| `S3_REGION` | `ap-southeast-1` | AWS region |

## Backend tests

### Unit tests

`tests/unit/` -- mocks via moto / freezegun / responses; no external services.

| Module | Test file(s) | What it tests |
|---|---|---|
| TMF API | `test_tmf_api.py`, `test_tmf_sql_generator.py`, `test_tmf_spec_registry.py`, `test_tmf_response_mapper.py` | TMF proxy API, SQL generation, spec registry, response mapping |
| FDW | `test_fdw_api.py`, `test_fdw_config.py`, `test_fdw_discovery.py`, `test_fdw_errors.py`, `test_fdw_lifecycle.py` | Foreign Data Wrapper API, config, discovery, lifecycle |
| Journey | `test_journey_model.py`, `test_manage_journey.py`, `test_manage_stage.py`, `test_stage_creation_flow.py`, ... | Journey CRUD, stage management, rules, logs |
| Capability | `test_manage_capability.py`, `test_manage_capability_jobs.py` | Capability management |
| Health | `test_health_fdw.py`, `test_health_localstack.py` | Health checks |
| Journey API | `apis/test_journey_api.py` | Journey REST API handlers |

### Property-based tests

`tests/property/` -- Hypothesis edge-case discovery on TMF, FDW, gateway routing, config loading, dashboard aggregation.

### Integration tests

`tests/integration/` -- requires a running gateway at `SERVER_URL`.

- **Python** (`tests/integration/python/`) -- REST API CRUD, MCP tool CRUD, journey lifecycle, FDW integration, license integration.
- **Shell** (`tests/integration/shell/`) -- tool availability, journey lifecycle, job execution, status polling.

### BDD tests

`tests/bdd/` -- behave + cucumber-expressions. ~63 scenarios across journey management, stage management, job execution, FDW integration, license management.

```bash
./tests/run_tests.sh bdd --server http://localhost:8000
```

### E2E tests

`tests/e2e/` -- live Salesforce, S3, CloudWatch. Requires `--run-live` and real AWS credentials.

### Endurance tests

`tests/endurance/` -- BDD scenarios run repeatedly for a configurable duration with health monitoring (CPU, memory, file descriptors, threads, DB connections, network / disk I/O).

| Alert | Threshold |
|---|---|
| CPU | 80% |
| Memory | 8 GB |
| Memory growth | 100 MB / hour |
| Response time | 5,000 ms |
| Error rate | 5% |
| File descriptors | 1,000 |

## Frontend tests

`nexus-ui/src/**/__tests__/` -- vitest + React Testing Library + fast-check.

```bash
cd /opt/mycode/nexus/nexus-ui
npm run test            # single run
npm run test:watch      # watch mode
npm run test:coverage   # with coverage
```

Coverage spans services, components (Solution-app sections, AI Copilot, journey panels), config, types, and contexts. Configuration in `vitest.config.ts`; setup mocks in `src/test/setup.ts` (`import.meta.env`, `window.location`, `global.fetch`).

## Test dependencies

| Component | Package | Purpose |
|---|---|---|
| Backend | pytest >= 8.0.0 | Test framework |
| Backend | pytest-asyncio | Async tests |
| Backend | pytest-cov / pytest-html | Coverage / HTML reports |
| Backend | hypothesis | Property-based |
| Backend | moto >= 5.1.17 | AWS mocking |
| Backend | freezegun | Time mocking |
| Backend | behave >= 1.3.3 | BDD |
| Integration | httpx, aiohttp | HTTP clients |
| Integration | pytest-xdist | Parallel exec |
| Integration | locust | Load testing |
| Frontend | vitest ^1.3.1 | Test runner |
| Frontend | @testing-library/react ^14.2.1 | Component testing |
| Frontend | fast-check ^3.15.0 | Property-based |

## Reports

Reports land in `test_reports/` per tier. Enhanced HTML reports are generated by scripts in `tests/report_generators/`.

```bash
./tests/run_tests.sh all                    # run + generate reports
./tests/run_tests.sh consolidated-report    # combine existing results
```

Reports can be auto-published to a CloudFront-backed S3 bucket via `--upload` -- the upload script generates a 2x2 dashboard with per-tier pass rates and links to the detail HTML.

## CI/CD

| Workflow | Purpose |
|---|---|
| `.github/workflows/test-localstack.yml` | LocalStack-backed unit + property + integration tests, plus lint and type-check |
| `deploy-{stage,dev,prod}.yml` | Lint (ruff) and security (safety); production tests run separately via `run_tests.sh` |

## Running tests step by step

```bash
# Backend
cd /opt/mycode/nexus/nexus-backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r tests/requirements-test.txt

# Frontend
cd /opt/mycode/nexus/nexus-ui
npm install

# Backend unit (no server)
cd /opt/mycode/nexus/nexus-backend && source .venv/bin/activate
./tests/run_tests.sh unit

# Backend integration (start the gateway in another terminal first)
python mcp_http_gateway.py
./tests/run_tests.sh integration --server http://localhost:8000

# BDD
./tests/run_tests.sh bdd --server http://localhost:8000

# Frontend
cd /opt/mycode/nexus/nexus-ui
npm run test
```

## Test coverage summary

| Tier | Approximate count | Coverage areas |
|---|---|---|
| Backend Unit | ~500+ | TMF, FDW, Journey, Capability, License, Health |
| Backend Property | ~100+ | Edge cases, random inputs, dashboard aggregation |
| Backend Integration | ~80+ | REST APIs, MCP tools, services, connectors |
| Backend BDD | ~63 scenarios across 23 features | Journey lifecycle, FDW integration, license, capability |
| Backend E2E | 12 | Full pipeline against live Salesforce / S3 / CloudWatch |
| Backend Endurance | configurable | Stability, memory leaks, resource exhaustion |
| Frontend Unit | ~32 files | Services, Solution-app components, journey panels, config, types, contexts |

## Related references

- [Developer Guide](../developer/index.md) -- contributor workflow and code organisation.
- [UAT](../UAT/testcases/nexus-uat-testcases.md) -- platform-level UAT scenarios mapped to Planes / Console / Solutions.
- [Implementation Guide](../ai-os/implementation-guide.md) -- code paths the tests exercise.
