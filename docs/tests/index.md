# CallSense Test Documentation

**Project:** Starhub Enterprise Sales Call Analytics (CallSense)  
**Document Version:** 1.0  
**Date:** March 11, 2026

---

## 1. Overview

CallSense has a comprehensive automated testing infrastructure covering the backend (Python) and frontend (TypeScript/React). Tests are organized into six tiers, each targeting a different layer of confidence:

| Tier | Framework | Location | Needs Server | Needs AWS |
|------|-----------|----------|:------------:|:---------:|
| Unit | pytest | `tests/unit/` | No | No (moto mocks) |
| Property | pytest + Hypothesis | `tests/property/` | No | LocalStack (some) |
| Integration (Python) | pytest | `tests/integration/python/` | Yes | No (moto) |
| Integration (Shell) | bash | `tests/integration/shell/` | Yes | No |
| BDD | behave | `tests/bdd/features/` | Yes | No |
| Endurance | behave + custom runner | `tests/endurance/` | Yes | Optional |
| E2E | pytest | `tests/e2e/` | Yes | Yes (live) |
| Frontend Unit | vitest + React Testing Library | `starhub-ui/src/**/__tests__/` | No | No |

All backend paths are relative to `/opt/mycode/trilogy/starhub-backend`.

---

## 2. Test Runner

The primary test orchestrator is `tests/run_tests.sh` (~1600 lines). It handles environment setup, test execution across all tiers, report generation, and optional upload to CloudFront.

### Quick Reference

```bash
cd /opt/mycode/trilogy/starhub-backend

# Run quick smoke test (< 1 minute)
./tests/run_tests.sh smoke

# Run all unit tests
./tests/run_tests.sh unit

# Run integration tests (requires running server)
./tests/run_tests.sh integration

# Run BDD tests
./tests/run_tests.sh bdd

# Run endurance/stability tests
./tests/run_tests.sh endurance

# Run everything
./tests/run_tests.sh all

# Run everything + upload reports to CloudFront
./tests/run_tests.sh all --upload

# Run specific combinations
./tests/run_tests.sh unit,integration,bdd

# Target a specific server
./tests/run_tests.sh integration --server https://my-server:8000

# Skip SSL verification
./tests/run_tests.sh integration --server https://... --insecure

# Generate consolidated HTML report
./tests/run_tests.sh consolidated-report

# Upload existing reports to S3/CloudFront
./tests/run_tests.sh upload-to-s3

# Clean test artifacts
./tests/run_tests.sh clean
```

### All Commands

| Command | Description | Duration |
|---------|-------------|----------|
| `smoke` / `quick` | Fast sanity check | < 1 min |
| `all` | Full suite (unit + integration + BDD + endurance) | 10-30 min |
| `all-quick` | Full suite with 1-minute endurance | 5-10 min |
| `full` | Full suite + AWS credential refresh + gateway restart | 15-35 min |
| `unit` | All unit tests | 2-5 min |
| `integration` | Shell + Python integration tests | 3-8 min |
| `integration-shell` | Shell integration only | 1-3 min |
| `integration-python` | Python integration only | 2-5 min |
| `bdd` | All BDD scenarios | 3-8 min |
| `endurance` | Endurance/stability tests (30 min default) | 30+ min |
| `journey` | Journey tests (unit + integration + BDD) | 3-8 min |
| `call-process` | Call process tests (unit + integration + BDD) | 3-8 min |
| `coverage` | Full suite with coverage report | 10-30 min |
| `performance` | Include performance benchmarks | varies |
| `server-check` | Check server health only | < 10s |
| `server-restart` | Restart the gateway | < 30s |
| `aws-refresh` | Refresh AWS credentials | < 10s |

### Flags

| Flag | Description |
|------|-------------|
| `--server URL` / `-s URL` | Target server URL (default: `http://localhost:8000`) |
| `--insecure` / `-k` | Skip SSL verification |
| `--upload` / `-u` | Upload reports to CloudFront after run |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_URL` | `http://localhost:8000` | Backend server URL |
| `VERBOSE` | `false` | Verbose output |
| `JSON_OUTPUT` | `false` | JSON-formatted output |
| `UPLOAD_TO_S3` | `false` | Auto-upload reports |
| `S3_BUCKET_NAME` | `ai-engine-test-reports` | S3 bucket for reports |
| `S3_REGION` | `ap-southeast-1` | AWS region |
| `CLOUDFRONT_DOMAIN` | `d37vwg02pj6oqg.cloudfront.net` | CloudFront domain |

---

## 3. Backend Tests

### 3.1 Unit Tests

**Location:** `tests/unit/`  
**Runner:** `pytest tests/unit/ -v --tb=short`  
**Dependencies:** moto, freezegun, responses (all mocked, no external services)

| Module | Test Files | Test Count | What It Tests |
|--------|-----------|------------|---------------|
| TMF API | `test_tmf_api.py`, `test_tmf_sql_generator.py`, `test_tmf_spec_registry.py`, `test_tmf_response_mapper.py` | ~126 | TMF proxy API, SQL generation, spec registry, response mapping |
| FDW | `test_fdw_api.py`, `test_fdw_config.py`, `test_fdw_discovery.py`, `test_fdw_errors.py`, `test_fdw_lifecycle.py` | ~80 | Foreign Data Wrapper API, config, discovery, lifecycle |
| Journey | `test_journey_model.py`, `test_manage_journey.py`, `test_manage_stage.py`, `test_stage_creation_flow.py`, etc. | ~100 | Journey CRUD, stage management, rules, logs |
| Call Process | `test_call_process_journey.py`, `test_call_process_stage.py`, `test_call_processor.py` | ~42 | Call ingestion, processing pipeline, Webex integration (mocked) |
| WXCC Simulator | `test_simulator_service.py`, `test_simulator_api.py`, `test_wxcc_simulator_stage.py` | ~50 | Simulator CRUD, API, stage integration |
| Capability | `test_manage_capability.py`, `test_manage_capability_jobs.py` | ~30 | Capability management |
| License | `test_license_properties.py`, `test_license_validation_properties.py` | ~21 | License activation, validation, expiry |
| Health | `test_health_fdw.py`, `test_health_localstack.py` | ~20 | Health checks |
| Journey API | `apis/test_journey_api.py` | 28 | Journey REST API handlers |

**Key fixtures** (from `tests/unit/call_process/conftest.py`):

- `mock_wxcc_api` -- Mocked Webex Contact Center API
- `mock_s3_client`, `mock_dynamodb_table`, `mock_glue_client` -- AWS service mocks
- `mock_ai_analyzer` -- Mocked GPT analysis
- `sample_tasks`, `sample_recordings`, `sample_transcript`, `sample_analysis_result` -- Test data

### 3.2 Property-Based Tests

**Location:** `tests/property/`  
**Runner:** `pytest tests/property/ -v --tb=short`  
**Framework:** Hypothesis

| Test File | What It Tests |
|-----------|---------------|
| `test_tmf_properties.py` | TMF API edge cases with random inputs |
| `test_fdw_properties.py` | FDW with generated data |
| `test_gateway_properties.py` | Gateway routing with random payloads |
| `test_config_properties.py` | Config loading edge cases |
| `test_real_dashboard_properties.py` (root) | Dashboard data aggregation (43 tests) |
| `localstack_automation/test_*_properties.py` | LocalStack automation |

### 3.3 Integration Tests

**Location:** `tests/integration/`  
**Requires:** Running server at `SERVER_URL`

#### Python Integration

**Location:** `tests/integration/python/`  
**Runner:** `pytest tests/integration/python/ -v`

| Test File | Tests | What It Tests |
|-----------|-------|---------------|
| `api/test_journey_rest_api.py` | 5 | Journey REST API CRUD |
| `api/test_health_api.py` | varies | Health endpoint responses |
| `mcp/test_journey_crud.py` | 9 | Journey MCP tool CRUD |
| `mcp/test_core_operations.py` | varies | Core MCP operations |
| `services/test_journey_service_integration.py` | varies | Journey service layer |
| `call_process/test_live_call_processing.py` | 9 | Live call pipeline (needs Webex, S3, Glue) |
| `call_process/test_journey_api_integration.py` | 13 | Journey API with call process |
| `call_process/test_call_process_integration.py` | varies | Call process with moto mocks |
| `wxcc_simulator/test_wxcc_simulator_integration.py` | 11 | Simulator with AWS (or LocalStack) |
| `license/test_license_integration.py` | 24 | License service integration |

#### Shell Integration

**Location:** `tests/integration/shell/`

| Test Script | What It Tests |
|------------|---------------|
| `tools/test_tool_availability.sh` | Tool/command availability |
| `journey/test_create_journey.sh` | Journey creation via API |
| `journey/test_journey_lifecycle.sh` | Full journey lifecycle |
| `jobs/test_run_job.sh` | Job execution via API |
| `jobs/test_job_status.sh` | Job status polling |

### 3.4 BDD Tests

**Location:** `tests/bdd/`  
**Runner:** `behave tests/bdd/features/`  
**Framework:** behave + cucumber-expressions

23 feature files organized by domain:

| Domain | Feature Files | Scenarios |
|--------|--------------|-----------|
| Journey | `journey_management.feature`, `stage_management.feature`, `job_execution.feature` | ~30 |
| Call Process | `call_process/call_process_journey.feature`, `call_process_simulator.feature` | ~15 |
| WXCC Simulator | `wxcc_simulator/wxcc_simulator_mcp.feature` | ~10 |
| License | `license/license_management.feature` | ~8 |

**Step definitions:** `tests/bdd/steps/`  
**Support:** `tests/bdd/support/` (TestDataManager, CLI adapter)

Run specific BDD domains:

```bash
./tests/run_tests.sh journey-bdd
./tests/run_tests.sh call-process-bdd
```

### 3.5 End-to-End Tests

**Location:** `tests/e2e/`  
**Runner:** `pytest tests/e2e/ -v -m live`  
**Requires:** Live Webex CC, S3, Glue, optionally OpenAI

| Test File | Tests | What It Tests |
|-----------|-------|---------------|
| `test_call_process_e2e.py` | 12 | Full call processing pipeline: Webex fetch -> transcription -> AI analysis -> S3 storage -> Glue catalog |

These tests require the `--run-live` flag and real AWS credentials.

### 3.6 Endurance Tests

**Location:** `tests/endurance/`  
**Runner:** `./tests/run_tests.sh endurance` or `python tests/endurance/bdd_endurance_runner.py`  
**Config:** `tests/endurance/endurance_config.yaml`

Endurance tests run BDD scenarios repeatedly for a configurable duration (default: 30 minutes) with health monitoring.

**Strategy:** Weighted random selection across test categories:

| Category | Weight |
|----------|--------|
| Journey Management | 35% |
| Stage Management | 25% |
| Job Execution | 15% |
| Error Scenarios | 10% |
| Simulator Management | 15% |

**Health monitoring metrics:** CPU, memory, file descriptors, threads, DB connections, network I/O, disk I/O

**Alert thresholds:**

| Metric | Threshold |
|--------|-----------|
| CPU | 80% |
| Memory | 8 GB |
| Memory growth | 100 MB/hour |
| Response time | 5000 ms |
| Error rate | 5% |
| File descriptors | 1000 |

---

## 4. Frontend Tests

**Location:** `starhub-ui/src/**/__tests__/`  
**Runner:** `vitest`  
**Framework:** vitest + React Testing Library + fast-check (property tests)

### Running Frontend Tests

```bash
cd /opt/mycode/trilogy/starhub-ui

# Run all tests
npm run test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

### Test Files (32 total)

| Location | Count | What They Test |
|----------|-------|---------------|
| `src/services/__tests__/` | 14 | TMF service, license service, config service, dashboard computations, email analytics (includes property tests) |
| `src/components/__tests__/` | 4 | DataSourceIndicator, AgentInstructionsEditor, AIWorkspace |
| `src/components/wxcc-simulator/__tests__/` | 6 | WXCCSimulatorPanel, TasksTable, SimulatorStatusCard |
| `src/components/settings/license/__tests__/` | 2 | LicenseStatusCard, LicenseActivationForm |
| `src/components/journeys/__tests__/` | 4 | JourneyStudioView, JourneysPanel (property), AIWorkspaceIntegration |
| `src/types/__tests__/` | 2 | Type validation (email-analysis, callProcessingJourney) |
| `src/utils/__tests__/` | 1 | Journey utilities (property) |
| `src/pages/__tests__/` | 1 | ChatbotEditor |
| `src/context/__tests__/` | 1 | EnterpriseAuthContext |
| `src/config/__tests__/` | 1 | Amplify config |

### Configuration

**File:** `vitest.config.ts`

- Environment: `jsdom`
- Setup: `./src/test/setup.ts` (mocks `import.meta.env`, `window.location`, `global.fetch`)
- Pattern: `src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}`
- Coverage: text, JSON, HTML output

---

## 5. Test Dependencies

### Backend (`tests/requirements-test.txt`)

| Package | Purpose |
|---------|---------|
| pytest >= 8.0.0 | Test framework |
| pytest-asyncio | Async test support |
| pytest-mock | Mock fixtures |
| pytest-cov | Coverage |
| pytest-html | HTML reports |
| hypothesis | Property-based testing |
| moto >= 5.1.17 | AWS service mocking (S3, DynamoDB, Glue) |
| freezegun | Time mocking |
| responses | HTTP mocking |
| behave >= 1.3.3 | BDD framework |
| behave-html-formatter | BDD HTML reports |

### Integration extras (`tests/integration/requirements-test.txt`)

| Package | Purpose |
|---------|---------|
| httpx, aiohttp | HTTP clients |
| pytest-xdist | Parallel execution |
| locust | Load testing |
| pytest-benchmark | Benchmarks |
| allure-pytest | Allure reports |
| testcontainers | Container-based tests |

### Frontend (`package.json` devDependencies)

| Package | Purpose |
|---------|---------|
| vitest ^1.3.1 | Test runner |
| @testing-library/react ^14.2.1 | React component testing |
| fast-check ^3.15.0 | Property-based testing |
| jsdom ^24.0.0 | DOM environment |

---

## 6. Test Reports

### Report Types

| Type | Format | Output Location |
|------|--------|----------------|
| Unit (pytest) | HTML + JSON | `test_reports/unit/` |
| Unit (enhanced) | HTML | `test_reports/unit/unit_test_report_enhanced_*.html` |
| Integration (pytest) | HTML + JSON | `test_reports/integration/` |
| Integration (enhanced) | HTML | `test_reports/integration/integration_test_report_enhanced_*.html` |
| BDD | JSON + HTML | `test_reports/bdd/` |
| BDD (enhanced) | HTML | `test_reports/bdd/bdd_test_report_enhanced_*.html` |
| Endurance | JSON + HTML | `test_reports/endurance/` |
| Endurance (enhanced) | HTML | `test_reports/endurance/endurance_test_report_enhanced_*.html` |
| Consolidated | HTML | `test_reports/consolidated_report_*.html` |
| Coverage | HTML | `htmlcov/` |

Enhanced reports are generated by scripts in `tests/report_generators/`:

| Generator | Produces |
|-----------|----------|
| `generate_unit_report.py` | Rich unit test HTML report with charts |
| `generate_integration_report.py` | Rich integration HTML report |
| `generate_bdd_report.py` | Rich BDD HTML report |
| `generate_endurance_report.py` | Rich endurance HTML report with health graphs |

### Generating Reports

```bash
# Run tests and generate reports
./tests/run_tests.sh all

# Generate consolidated report from existing results
./tests/run_tests.sh consolidated-report
```

---

## 7. Publishing Reports to CloudFront

Test reports can be published to a CloudFront-backed S3 bucket for team-wide access.

### Infrastructure

| Component | Value |
|-----------|-------|
| S3 Bucket | `ai-engine-test-reports` |
| Region | `ap-southeast-1` |
| CloudFront Distribution | `E269STPYK4FJVQ` |
| CloudFront Domain | `d37vwg02pj6oqg.cloudfront.net` |

### Report Dashboard URL

```
https://d37vwg02pj6oqg.cloudfront.net/index.html
```

The dashboard shows a 2x2 grid of test categories (Unit, Integration, BDD, Endurance) with pass rates, test counts, and links to detailed reports.

### Publishing Steps

**Option 1: Auto-upload after test run**

```bash
./tests/run_tests.sh all --upload
```

**Option 2: Upload existing reports**

```bash
cd /opt/mycode/trilogy/starhub-backend
./tests/report_setup/upload_reports_to_cloudfront.sh
```

**What the upload script does:**

1. Finds latest enhanced HTML reports in `test_reports/`
2. Uploads each report to S3 at `test-reports/{type}/{timestamp}/report.html`
3. Generates an index HTML dashboard with stats extracted from reports
4. Uploads the index to `test-reports/index.html`
5. Invalidates CloudFront cache so changes are immediately visible

**Published report URLs:**

| Report | URL |
|--------|-----|
| Dashboard | `https://d37vwg02pj6oqg.cloudfront.net/index.html` |
| Unit | `https://d37vwg02pj6oqg.cloudfront.net/unit/{timestamp}/report.html` |
| Integration | `https://d37vwg02pj6oqg.cloudfront.net/integration/{timestamp}/report.html` |
| BDD | `https://d37vwg02pj6oqg.cloudfront.net/bdd/{timestamp}/report.html` |
| Endurance | `https://d37vwg02pj6oqg.cloudfront.net/endurance/{timestamp}/report.html` |

---

## 8. CI/CD Integration

### GitHub Actions

**Workflow:** `.github/workflows/test-localstack.yml` (manual trigger via `workflow_dispatch`)

**What it runs:**

1. Spins up LocalStack service container (DynamoDB, S3, CloudWatch, STS)
2. Initializes LocalStack with `localstack-init.sh`
3. Runs property tests: `pytest tests/property/ -v --tb=short`
4. Runs unit tests: `pytest tests/unit/ -v --tb=short`
5. Runs integration tests: `pytest tests/integration/ -v -k "localstack or local"`
6. Runs lint (flake8) and type check (mypy)
7. Produces artifacts: `pytest-results.xml`, `coverage.xml`

**Other deployment workflows** (`deploy-stage.yml`, `deploy-dev.yml`, `deploy-prod.yml`) include lint (ruff) and security (safety) checks but do not execute tests.

---

## 9. Test Data and Fixtures

### Backend Fixtures

| Fixture Source | What It Provides |
|----------------|-----------------|
| `tests/conftest.py` | `mock_context`, `temp_workspace`, `sample_journey_id`, `mock_aws_credentials` (autouse) |
| `tests/unit/call_process/conftest.py` | `mock_wxcc_api`, `mock_s3_client`, `mock_dynamodb_table`, `mock_glue_client`, `mock_athena_client`, `mock_boto3_session`, `mock_ai_analyzer`, `sample_tasks`, `sample_recordings`, `sample_transcript`, `sample_analysis_result` |
| `tests/integration/conftest.py` | `api_client` (AsyncClient), `test_journey_data`, `test_stage_data`, `test_rule_data`, `cleanup_manager`, `performance_tracker` |
| `tests/integration/python/fixtures/journey_fixtures.py` | `basic_journey_data`, `journey_with_stages_data`, `stage_data_fixture`, `rule_data_fixture` |
| `tests/endurance/endurance_config.yaml` | Duration, strategy weights, health thresholds, scenario definitions |

### Frontend Test Setup

**File:** `starhub-ui/src/test/setup.ts`

- Mocks `import.meta.env` (VITE_API_BASE_URL, VITE_BYPASS_AUTH, etc.)
- Mocks `window.location` (assign, reload)
- Mocks `global.fetch` (returns `{ ok: true, json: {} }`)

---

## 10. Running Tests -- Step by Step

### Prerequisites

```bash
# Backend: create venv and install dependencies
cd /opt/mycode/trilogy/starhub-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r tests/requirements-test.txt

# Frontend: install node dependencies
cd /opt/mycode/trilogy/starhub-ui
npm install
```

### Run Backend Unit Tests (no server needed)

```bash
cd /opt/mycode/trilogy/starhub-backend
source .venv/bin/activate
./tests/run_tests.sh unit
```

### Run Backend Integration Tests (server required)

```bash
# Terminal 1: Start the server
cd /opt/mycode/trilogy/starhub-backend
source .venv/bin/activate
python mcp_http_gateway.py

# Terminal 2: Run integration tests
cd /opt/mycode/trilogy/starhub-backend
source .venv/bin/activate
./tests/run_tests.sh integration --server http://localhost:8000
```

### Run BDD Tests

```bash
./tests/run_tests.sh bdd --server http://localhost:8000
```

### Run Endurance Tests

```bash
./tests/run_tests.sh endurance --server http://localhost:8000
```

### Run Frontend Tests

```bash
cd /opt/mycode/trilogy/starhub-ui
npm run test           # single run
npm run test:watch     # watch mode
npm run test:coverage  # with coverage
```

### Run Everything and Publish

```bash
cd /opt/mycode/trilogy/starhub-backend
source .venv/bin/activate
./tests/run_tests.sh all --server http://localhost:8000 --upload
```

---

## 11. Test Coverage Summary

| Layer | Framework | Approximate Test Count | Coverage Areas |
|-------|-----------|----------------------|----------------|
| Backend Unit | pytest | ~500+ | TMF, FDW, Journey, Call Process, Simulator, License, Health |
| Backend Property | Hypothesis | ~100+ | Edge cases, random inputs, data generation |
| Backend Integration | pytest + bash | ~80+ | REST APIs, MCP tools, services, connectors |
| Backend BDD | behave | ~63 scenarios (23 features) | Journey lifecycle, call processing, simulator, license |
| Backend E2E | pytest | 12 | Full call pipeline with live services |
| Backend Endurance | behave runner | configurable | Stability, memory leaks, resource exhaustion |
| Frontend Unit | vitest | ~32 files | Services, components, config, types, contexts |
| **Total** | | **~800+** | |

---
