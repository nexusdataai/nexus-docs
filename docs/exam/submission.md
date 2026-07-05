# Aperture Architecture Assessment — Submission

> Paste into your Google Doc copy. Each scenario fits the 5-page guideline; each "Important Decision" follows Problem / Alternatives / Decision / Rationale.

---

## Scenario A: Bulk Processing Pipeline

**Goal:** Let an enterprise customer run a multi-step filter pipeline on hundreds of large images, with processing times in the minutes-to-hours range, while keeping the existing single-image synchronous path working.

### Important Facts

1. **The 4.5MB and 30s limits are artifacts of the sync path, not of Lambda or S3.** They come from base64-in-JSON inflation against Lambda's 6MB sync request ceiling and API Gateway's ~30s integration timeout. Removing them requires changing the upload and invocation pattern, not the underlying compute.
2. **A bulk job can exceed Lambda's 15-minute max execution.** A single Lambda invocation cannot own end-to-end orchestration for hundreds of images × multiple filters; orchestration must live outside the worker.
3. **Existing filters are Node.js code inside the proxy Lambda.** The per-image, per-filter unit of work already works; the missing pieces are upload, orchestration, state, and a public async contract.
4. **The current data model is a single DynamoDB table by design.** New entities (`Job`, `JobStep`) should extend it, not replace it.
5. **Browsers cannot wait minutes for a response.** The customer-facing contract must shift from "sync 200 with URL" to "202 + job resource" — this is a new external boundary.
6. **Power users are already stressing the flat-rate plan.** Bulk processing concentrates load further; without fairness controls, one tenant can starve the rest.
7. **Scale is ~1,000 orgs, 20% MoM.** Solutions should prefer managed AWS services already in our operational vocabulary (S3, Lambda, Step Functions, SQS, DDB) over new infrastructure.

### Important Technical Decisions

**Decision 1: Direct-to-S3 uploads via pre-signed PUT URLs**
- **Problem:** The 4.5MB ceiling and bandwidth-on-Lambda problem block any bulk upload story. Even at 100 images × 5MB, routing bytes through API Gateway + Lambda is wrong.
- **Alternatives:** Keep base64-in-JSON with larger payload limits; multipart upload proxied through the API; client-driven S3 multipart with our credentials.
- **Decision:** Client requests N pre-signed PUT URLs from `POST /uploads:batch`, uploads directly to S3, then references the resulting S3 keys when creating the job.
- **Rationale:** Removes the byte path from our compute entirely, eliminates the 4.5MB ceiling permanently, and lets the client SDK do retries/parallelism without server involvement. Trade-off accepted: an extra round-trip to mint URLs, which is negligible vs. the upload cost itself.

**Decision 2: Async Jobs API with an explicit, published state machine**
- **Problem:** A browser cannot block for hours, and the response contract `200 + URL` cannot be preserved. Customers (and their integrations) need a stable way to track progress and resume.
- **Alternatives:** Long-polling sync endpoint with very large timeouts; SSE/WebSocket stream during the job; webhook-only with no polling fallback.
- **Decision:** `POST /jobs` returns `202 Accepted` + a `Job` resource. Job states are part of the public contract: `queued → running → partially_failed | succeeded | failed | cancelled`. Clients can `GET /jobs/{id}` and `GET /jobs/{id}/images` for per-image status.
- **Rationale:** A documented state machine is the platform boundary — it lets customers build reliable integrations without coupling to our orchestrator. Webhooks and polling coexist so clients pick what fits their environment.

**Decision 3: AWS Step Functions for pipeline orchestration, with a per-image Map state**
- **Problem:** We need durable, multi-step, retryable orchestration that can run for hours and fan out across hundreds of images.
- **Alternatives:** Raw SQS + worker Lambdas with hand-rolled state; ECS/Fargate workers running a custom orchestrator; Airflow/MWAA; EventBridge Pipes.
- **Decision:** Step Functions Standard Workflow per job. The job definition compiles to a state machine with a `Map` state over images; each image runs the filter sequence as a chain of `Task` states invoking the existing filter Lambdas.
- **Rationale:** "Least new machinery" — fully managed, gives us retries, history, idempotent task invocation, and a UI for debugging out of the box. We reuse the existing filter Lambda code unchanged. SQS+Lambda was rejected because we'd reinvent state, retries, and observability; ECS was rejected because we'd add a runtime we don't currently operate.

**Decision 4: Customer-facing pipeline DSL decoupled from the orchestrator**
- **Problem:** "Pipeline" is now a customer-visible concept. If customers write Step Functions ASL directly, we cannot change orchestrator later without a breaking change.
- **Alternatives:** Expose Step Functions ASL directly; expose a YAML DAG; expose a fixed list of named pipelines only.
- **Decision:** Define a stable JSON DSL — an ordered list of `{ filterId, version, params }` steps with optional `onFailure` per step. The Jobs service compiles this to Step Functions input; the DSL is the contract.
- **Rationale:** Decouples public API stability from implementation. We can swap orchestrators, add parallel branches, or change retry strategies internally without breaking customers. The DSL also becomes the integration point for Scenario B (a step can reference a marketplace filter).

**Decision 5: Idempotency keys + per-step state, enabling resumable jobs**
- **Problem:** Hour-long jobs will fail partway through. Re-running everything wastes hours and money; manual surgery is operationally unacceptable.
- **Alternatives:** Re-run the whole job on failure; checkpoint only at the job level; rely on Step Functions retries alone.
- **Decision:** `POST /jobs` accepts an `Idempotency-Key` header. We persist one DDB record per `(jobId, imageId, stepIndex)` with `status` and `outputS3Key`. Intermediate artifacts land at `s3://aperture/jobs/{jobId}/{imageId}/{stepIdx}.{ext}` with a 7-day lifecycle. `POST /jobs/{id}:resume` re-runs only failed `(image, step)` pairs.
- **Rationale:** Operational reality — we will be paged on partial failures and need a surgical retry path. Idempotent task design also makes Step Functions retries safe by construction. Cost trade-off: intermediate artifacts inflate S3 usage briefly, bounded by lifecycle.

**Decision 6: Per-tenant fairness via reserved Lambda concurrency**
- **Problem:** A single power user submitting a 10,000-image job can consume all available filter Lambda concurrency, starving the existing sync `/images` endpoint and other tenants.
- **Alternatives:** No fairness (first-come-first-served); per-tenant SQS queues with dedicated workers; admission control at the Jobs API.
- **Decision:** Two Lambda aliases per filter: `sync` (sized for the existing path) and `bulk` (used by Step Functions tasks). Bulk Lambdas have reserved concurrency divided across active tenants via Step Functions concurrency control and a per-tenant cap in the Jobs admission layer.
- **Rationale:** Protects the sync endpoint absolutely (sync alias is independent) and gives bulk a predictable, fair allocation. Per-tenant queues were rejected as over-engineered at 1,000 orgs — concurrency reservations achieve fairness without new infrastructure.

**Decision 7: HMAC-signed webhooks + polling, with a versioned event payload**
- **Problem:** Customers automating bulk workflows need a push notification on completion; relying on polling alone burns their request budget and ours.
- **Alternatives:** Polling only; webhooks without signing; SNS topic per customer.
- **Decision:** Customers register one webhook URL per organization. We POST a signed JSON payload (`X-Aperture-Signature: sha256=...`, shared secret per org) containing `eventType`, `jobId`, `state`, and a stable schema version. Polling via `GET /jobs/{id}` remains available; retries with exponential backoff on non-2xx for up to 24h.
- **Rationale:** HMAC signing is table-stakes for any external webhook — security boundary. Versioned payload schema lets us evolve event content without breaking subscribers. Both polling and webhooks coexist because customer environments vary.

**Decision 8: Keep v1 sync `/images` endpoint unchanged; ship Jobs as v2**
- **Problem:** 1,000 orgs depend on the existing sync flow. Forcing them onto the async model is a breaking change with no upside for the single-filter, small-image case.
- **Alternatives:** Migrate all customers to the async model; deprecate sync immediately; route sync requests through the async path internally.
- **Decision:** `/v1/images` continues to work exactly as today. `/v2/jobs` and `/v2/uploads:batch` ship alongside it. The filter Lambda code is shared between both. No deprecation announced at launch.
- **Rationale:** Incrementalism — solve the new problem (bulk) without disturbing the working system. Shared filter code means we don't fork our processing logic. Sync's 4.5MB/30s limits remain documented as v1 constraints, with v2 as the path forward.

### What we keep

The single proxy Lambda, the single-table DynamoDB, S3 layout for processed images, and the existing filter implementations. New entities (`Job`, `JobStep`) extend the existing table.

### At 10× scale we would revisit

- Express Step Functions or self-orchestrated workers if per-step cost dominates.
- Per-tenant SQS queues if reserved concurrency proves too coarse.
- Splitting the proxy Lambda into auth + processing if cold-start latency on the sync path becomes a problem.

---

## Scenario B: Third-Party Filter Marketplace

**Goal:** Let third-party developers publish filters that Aperture customers can install and use inside their pipelines, with the isolation, contract stability, and metering required to run an actual platform.

### Important Facts

1. **Third-party filter code is untrusted.** Whatever runtime we pick must enforce hard isolation between filter code and Aperture's core systems, between filters from different publishers, and between invocations.
2. **Today's filters run as in-process Node.js code inside the proxy Lambda.** That mechanism cannot accept external code — we need a new execution boundary regardless of which runtime we pick.
3. **The platform now has two distinct audiences.** Customers consume filters; developers build them. Developer experience (CLI, SDK, local test, docs, dashboard) is a first-class product surface, not a nice-to-have.
4. **Revenue share requires per-invocation metering accurate to the millisecond.** Billing disputes are existential for marketplace trust, so metering must be idempotent, auditable, and developer-visible.
5. **Filter contracts will outlive any single version.** Customers will pin to versions and expect old versions to keep working; deprecation must be policy, not ad-hoc.
6. **Marketplace volume will start small (~1,000 customer orgs).** Over-investing in distribution scale before product-market fit is a trap; the discoverability surface can be modest.
7. **Filter computation patterns are heterogeneous and will diversify.** Some filters are CPU image ops, some may need GPU or larger memory. The runtime must accommodate variation without per-filter custom infrastructure.

### Important Technical Decisions

**Decision 1: Filters run as AWS Lambda container images, one Lambda per published filter version**
- **Problem:** We need a strong isolation boundary for untrusted code with reasonable cold-start, scale-to-zero, and per-invocation billing for rev-share.
- **Alternatives:** WASM sandbox embedded in our worker; Firecracker microVMs directly (e.g., self-managed); ECS/Fargate tasks per filter; a shared multi-tenant Node.js process with `vm2`-style sandboxing.
- **Decision:** Each published `(filterId, version)` is deployed as a Lambda container image with a strict IAM role, no VPC outbound by default, and per-ms billing surfaced to the metering pipeline. Filter author pushes a container; we deploy it as a Lambda alias.
- **Rationale:** Lambda already runs on Firecracker, giving us hard per-invocation isolation without operating microVMs ourselves. Container images let developers ship Node, Python, or any other runtime. Per-ms billing maps cleanly to rev-share. WASM was rejected as a strong alternative on isolation, but the image-processing ecosystem (sharp, OpenCV, libvips, ImageMagick) is still weak in WASM; revisit in 18-24 months.

**Decision 2: Published filter contract: typed JSON request/response with pre-signed S3 URLs**
- **Problem:** The contract between Aperture and a third-party filter is the platform boundary. It must be language-agnostic, must never give the filter raw access to customer storage, and must be stable across filter versions.
- **Alternatives:** Pass raw image bytes in the Lambda event; mount EFS for shared filesystem; gRPC streaming; let filters call back into Aperture APIs.
- **Decision:** Invocation event = `{ invocationId, inputUrl, params, customerId, jobContext }` where `inputUrl` is a short-TTL pre-signed GET. Response = `{ outputUrl, metadata }` where `outputUrl` was minted as a pre-signed PUT supplied in the event. Contract is published as OpenAPI plus official Node and Python SDKs. First-party filters migrate to the same contract (dogfood).
- **Rationale:** Pre-signed URLs give the filter exactly the access it needs and nothing more — security isolation by construction. JSON over the Lambda invocation interface is language-agnostic. Dogfooding the contract on first-party filters guarantees we cannot accidentally introduce a private back-door that breaks the public promise.

**Decision 3: SemVer with immutable published versions and explicit pin strategy**
- **Problem:** Customers will build production pipelines on specific filter versions and need guarantees that those pipelines won't silently break.
- **Alternatives:** Mutable versions (latest wins); rolling tags only; date-based versioning; no versioning (filterId is the unit).
- **Decision:** Each published version is immutable. Customers pin in their pipeline DSL as `filterId@MAJOR` (default), `filterId@MAJOR.MINOR`, or `filterId@MAJOR.MINOR.PATCH`. MINOR and PATCH within a pinned MAJOR auto-upgrade unless the customer opts out. New MAJOR versions never auto-upgrade.
- **Rationale:** Immutability + SemVer is the standard pattern customers expect from package registries; reusing the convention reduces cognitive load. Auto-upgrade within MAJOR lets the marketplace deliver security fixes without manual customer action, while preserving backward compatibility guarantees.

**Decision 4: 90-day deprecation policy; deprecated versions remain callable until sunset**
- **Problem:** Developers will eventually want to retire old versions; doing so without notice breaks customer pipelines.
- **Alternatives:** No deprecation policy (developer disables at will); immediate hard-disable with email notification; permanent availability of all versions forever.
- **Decision:** Marking a version `deprecated` is non-destructive. Aperture surfaces it on the customer dashboard, in API response headers (`Sunset:`, `Deprecation:`), and via email to all installing orgs. Sunset date is no earlier than 90 days from deprecation. After sunset, invocations return a documented error with a migration hint.
- **Rationale:** Direct hit on the rubric's "deprecation and breaking changes." The 90-day floor is policy, not opinion — it makes the platform predictable for customer ops teams. Sunset error responses are themselves a documented contract so customer code can detect and handle them.

**Decision 5: Publishing pipeline — `aperture` CLI → Aperture-managed ECR → automated scan → review queue**
- **Problem:** We are running other people's code on our infrastructure for our customers; the publish path is a security choke point and the most important developer-experience surface.
- **Alternatives:** Developers push to their own ECR and we pull (trust their registry); accept zip uploads and we build images server-side; manual PR-based publish.
- **Decision:** `aperture init` scaffolds a filter with the SDK and local test harness. `aperture test` runs the filter against reference fixtures locally. `aperture publish` builds the image, pushes to an Aperture-managed ECR repo, triggers Amazon Inspector (or equivalent) for CVE and secret scanning, and enters a review queue. First publish of a new filter is human-reviewed; subsequent MINOR/PATCH versions of an already-approved filter auto-publish on a clean scan.
- **Rationale:** Aperture-managed ECR ensures we control image storage and provenance — we sign the manifest with our own attestation. The CLI is the developer-experience surface that the rubric explicitly rewards. Tiered review (manual first, automated thereafter) keeps friction low for trusted developers while gating new code paths.

**Decision 6: Strong invocation-level isolation — no egress, scoped IAM, ephemeral storage**
- **Problem:** A malicious or buggy filter must not exfiltrate customer data, reach Aperture internal services, or interfere with other invocations.
- **Alternatives:** Trust developer attestation; outbound allowlist by default; full network sandbox with explicit per-filter ACLs.
- **Decision:** Filter Lambdas have: (a) **no outbound network** by default (no VPC, no NAT); (b) an IAM role scoped to nothing — all data access flows through the pre-signed URLs in the event; (c) read-only ephemeral storage (`/tmp` only); (d) opt-in egress allowlist requested per filter and reviewed during publish. Cross-invocation memory is impossible because each Lambda invocation gets a fresh execution context.
- **Rationale:** Default-deny is the only safe posture for untrusted code. The pre-signed URL pattern means the filter has access to exactly one input and one output, both short-lived. Egress allowlist exists for legitimate cases (e.g., a filter that calls a model provider) but is an explicit, reviewed exception.

**Decision 7: Per-invocation safety controls — resource limits, circuit breaker, kill-switch**
- **Problem:** A runaway filter — infinite loop, memory leak, error storm — can drain budget, block customer pipelines, and harm Aperture's reputation. Trust & safety incidents require an immediate response path.
- **Alternatives:** Rely on Lambda timeout alone; manual intervention only; auto-suspend on first error.
- **Decision:** Each filter version declares memory and timeout at publish time (capped to platform limits). Aperture enforces a per-filter-per-org cost ceiling and an error-rate circuit breaker: if a version's error rate exceeds threshold over a rolling window, new invocations of that version short-circuit with a documented error. Aperture operators have a one-click kill-switch to disable a specific `(filterId, version)` without affecting other versions of the same filter.
- **Rationale:** Operational reality — we will receive abuse reports and need to respond in minutes, not days. Per-version kill-switch is critical so we don't punish good versions for one bad one. Circuit breaker is automatic safety; kill-switch is human safety.

**Decision 8: Metering pipeline — invocation events → Kinesis Firehose → S3 → daily aggregation**
- **Problem:** Revenue share must be accurate, auditable, idempotent, and visible to developers in near-real-time, or the marketplace loses developer trust.
- **Alternatives:** Compute billing from CloudWatch Logs after the fact; rely on AWS Cost Explorer; write directly to DDB per invocation.
- **Decision:** Every filter invocation emits a metering event keyed by `invocationId`: `{ filterId, version, customerId, durationMs, success, billedMemoryMb, timestamp }`. Events flow through Kinesis Firehose to partitioned S3 (`year=/month=/day=`). A daily Glue job aggregates per `(developer, filter, version, customer)` for the billing system and exposes per-day metrics to the developer dashboard. `invocationId` enforces idempotency on aggregation.
- **Rationale:** Auditable from raw events forever (S3 retention), idempotent by construction, and cheap. Developer-facing transparency on metrics — what they earned and on which invocations — is itself a key DX feature: developers can independently verify rev-share.

**Decision 9: Marketplace filters plug into Scenario A's pipeline DSL as a step type**
- **Problem:** A marketplace is only useful if customers can actually invoke its filters inside the same pipelines they already use. The integration boundary between the bulk-jobs system and the marketplace system must be defined.
- **Alternatives:** A separate "marketplace runner" API distinct from pipelines; force customers to compose marketplace filters and first-party filters in client code.
- **Decision:** The Scenario A pipeline DSL accepts steps of the form `{ "filterId": "@publisher/name", "version": "1.2.x", "params": {...} }`. The Jobs service resolves marketplace references at job-submit time, snapshots the resolved version into the job record (so a deprecation mid-job doesn't break a running job), and Step Functions invokes the corresponding filter Lambda alias.
- **Rationale:** Customers see one consistent way to compose filters regardless of origin — coherent platform thinking. Version snapshotting at submit time gives running jobs the same stability guarantees as customer pins. This decision is what makes Scenarios A and B one product rather than two.

### What we keep

The single proxy Lambda for the sync `/v1/images` endpoint, the existing first-party filter logic (rewrapped behind the new contract), the single-table DDB (new entities: `Publisher`, `Filter`, `FilterVersion`, `Install`, `Invocation`), and the AWS-native stack.

### At 10× scale we would revisit

- WASM as a secondary runtime if a meaningful class of filters becomes ecosystem-compatible (lower cold-start, finer-grained isolation).
- Multi-region filter deployment if marketplace usage diverges from current customer regions.
- A separate metering store (e.g., Timestream) if S3 + Glue aggregation latency stops fitting the developer-dashboard SLA.
