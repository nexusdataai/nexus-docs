# CloudWatch Logs Analysis
## Totogi CallSense Platform - Backend Services

**Document Type:** Technical Analysis  
**Version:** 1.0  
**Date:** January 2026  
**Purpose:** Estimate CloudWatch Logs volume for all backend services

---

## Backend Services Overview

The Totogi CallSense backend consists of multiple services running on ECS Fargate, all sending logs to CloudWatch:

```
┌────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVICES                            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. MCP HTTP Gateway (FastAPI)                                 │
│     ├─> Journey Management API                                 │
│     ├─> License Management API                                 │
│     ├─> WXCC Simulator API                                     │
│     ├─> Analytics API                                          │
│     ├─> QA Analytics API                                       │
│     ├─> Calls API                                              │
│     ├─> Health/Diagnostics API                                 │
│     ├─> Auth API                                               │
│     ├─> Config API                                             │
│     └─> Webex Connector API                                    │
│                                                                │
│  2. Call Processing Jobs (ECS Tasks)                           │
│     ├─> Fetch tasks from Webex CC                             │
│     ├─> Deduplication checks                                   │
│     ├─> Download and transcribe calls                         │
│     ├─> AI analysis                                            │
│     └─> Salesforce integration                                 │
│                                                                │
│  3. MCP Server Workers (Subprocess)                            │
│     ├─> MCP protocol handling                                  │
│     ├─> Tool execution (journeys, simulator, license)         │
│     └─> Streaming responses                                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## CloudWatch Log Groups

### Production Log Group Structure:

```
/aws/ecs/call-processing-prod/
├── gateway/                    # MCP HTTP Gateway logs
│   ├── task-{id}/stream-1
│   └── task-{id}/stream-2
├── call-processing/            # Call processing job logs
│   ├── task-{id}/stream-1
│   └── task-{id}/stream-2
└── mcp-workers/                # MCP server worker logs
    ├── worker-1/stream
    └── worker-2/stream
```

---

## Log Volume Estimation

### Service 1: MCP HTTP Gateway

**Service Type:** FastAPI application (long-running)  
**Container Count:** 2-4 containers (ECS Fargate)  
**Log Level:** INFO (default)

**Logging Events:**

| Event Type | Frequency | Log Size | Notes |
|------------|-----------|----------|-------|
| **HTTP Requests** | ~50/hour | 200 bytes | API calls (health checks, queries) |
| **MCP Tool Calls** | ~10/hour | 500 bytes | journeys_tool, logs_tool, etc. |
| **Health Checks** | ~720/day | 100 bytes | Every 2 minutes |
| **Startup/Shutdown** | 2-10/day | 1KB | Container restarts |
| **Error Logs** | ~5/day | 1KB | Occasional errors |
| **Debug Logs** | 0 | - | Only if LOG_LEVEL=DEBUG |

**Daily Log Volume:**
- HTTP Requests: 1,200 × 200 bytes = 240 KB
- MCP Calls: 240 × 500 bytes = 120 KB
- Health Checks: 720 × 100 bytes = 72 KB
- Startup/Shutdown: 5 × 1KB = 5 KB
- Error Logs: 5 × 1KB = 5 KB

**Per Container:** ~442 KB/day  
**4 Containers:** ~1.77 MB/day  
**Monthly:** ~53 MB/month

---

### Service 2: Call Processing Jobs

**Service Type:** ECS Tasks (short-lived, triggered every 5 minutes)  
**Task Count:** 1 task per job  
**Log Level:** INFO with detailed call processing logs

**Given by User:**
- **Call Processing Log:** 1 MB per call
- **Job Frequency:** Every 5 minutes (288 jobs/day)
- **Calls per Job:** 1 call

**Logging Components per Call:**

| Component | Size | Description |
|-----------|------|-------------|
| **Job Initialization** | 10 KB | Journey load, job setup |
| **Deduplication Check** | 5 KB | Check WXCC tracking table |
| **Fetch Tasks** | 20 KB | Webex CC API call logs |
| **Process Recording** | 850 KB | Download, transcribe, S3 upload logs |
| **Register Metadata** | 30 KB | Glue catalog registration |
| **AI Analysis** | 50 KB | GPT analysis logs |
| **Salesforce Actions** | 20 KB | SFDC lead/opp creation |
| **Job Completion** | 15 KB | Final stats, cleanup |
| **Total per Call** | **~1 MB** | ✅ Matches user estimate |

**Daily Log Volume:**
- Jobs per day: 288
- Calls per day: 288 (1 call/job)
- Logs per day: 288 MB

**Monthly:** 8,640 MB = **~8.6 GB/month**

---

### Service 3: MCP Server Workers

**Service Type:** Subprocess workers (2-8 workers)  
**Worker Count:** 4 workers average  
**Log Level:** INFO

**Logging Events:**

| Event Type | Frequency | Log Size | Notes |
|------------|-----------|----------|-------|
| **Worker Startup** | 4/day | 2 KB | Worker pool initialization |
| **Tool Execution** | ~10/hour | 1 KB | MCP tool calls |
| **Heartbeat** | ~1,440/day | 50 bytes | Per worker status |
| **Error Logs** | ~2/day | 1 KB | Occasional errors |

**Per Worker Daily:**
- Startup: 1 × 2 KB = 2 KB
- Tool Execution: 240 × 1 KB = 240 KB
- Heartbeat: 1,440 × 50 bytes = 72 KB
- Errors: 2 × 1 KB = 2 KB

**Per Worker:** ~316 KB/day  
**4 Workers:** ~1.26 MB/day  
**Monthly:** ~38 MB/month

---

### Service 4: API-Specific Logs

**Individual API Endpoints** (all running in Gateway container):

| API Endpoint | Requests/Day | Log Size/Request | Daily Volume |
|--------------|--------------|------------------|--------------|
| **Journey Management** | 50 | 500 bytes | 25 KB |
| **Analytics** | 100 | 300 bytes | 30 KB |
| **License** | 20 | 400 bytes | 8 KB |
| **WXCC Simulator** | 10 | 500 bytes | 5 KB |
| **Calls API** | 200 | 200 bytes | 40 KB |
| **QA Analytics** | 50 | 300 bytes | 15 KB |
| **Health/Diagnostics** | 720 | 100 bytes | 72 KB |
| **Auth** | 30 | 300 bytes | 9 KB |
| **Config** | 20 | 200 bytes | 4 KB |
| **Webex Connector** | 10 | 400 bytes | 4 KB |

**Total API Logs:** ~212 KB/day  
**Monthly:** ~6.4 MB/month

**Note:** These are already included in Gateway logs above (Service 1)

---

## Total CloudWatch Logs Volume

### Daily Summary:

| Service | Containers/Tasks | Log Volume | Total |
|---------|------------------|------------|-------|
| **MCP HTTP Gateway** | 4 containers | 442 KB each | **1.77 MB/day** |
| **Call Processing Jobs** | 288 tasks/day | 1 MB each | **288 MB/day** |
| **MCP Workers** | 4 workers | 316 KB each | **1.26 MB/day** |
| **TOTAL** | - | - | **291 MB/day** |

### Monthly Summary:

| Service | Daily Volume | Monthly Volume | Percentage |
|---------|--------------|----------------|------------|
| **Call Processing Jobs** | 288 MB | **8,640 MB** (~8.6 GB) | **96.2%** |
| **MCP HTTP Gateway** | 1.77 MB | **53 MB** | **0.6%** |
| **MCP Workers** | 1.26 MB | **38 MB** | **0.4%** |
| **System/Overhead** | 8 MB | **240 MB** | **2.7%** |
| **TOTAL** | 299 MB | **~9 GB/month** | **100%** |

### Yearly Summary:

| Period | Call Logs | Gateway Logs | Worker Logs | System Logs | Total |
|--------|-----------|--------------|-------------|-------------|-------|
| **Month 1** | 8.6 GB | 53 MB | 38 MB | 240 MB | **~9 GB** |
| **Year 1** | 103.7 GB | 636 MB | 456 MB | 2.9 GB | **~108 GB** |

**Note:** CloudWatch Logs don't accumulate indefinitely - retention policy determines actual storage.

---

## CloudWatch Logs Configuration

### Recommended Retention Policies:

| Log Group | Retention | Reason |
|-----------|-----------|---------|
| **Call Processing** | 30 days | High volume, calls detailed in S3 |
| **Gateway** | 90 days | Low volume, useful for debugging |
| **Workers** | 90 days | Low volume, system diagnostics |
| **Error Logs** | 180 days | Long-term troubleshooting |

### With Retention Applied:

| Log Group | Monthly Ingestion | Retention | Stored Volume |
|-----------|-------------------|-----------|---------------|
| **Call Processing** | 8.6 GB | 30 days | **8.6 GB** |
| **Gateway** | 53 MB | 90 days | **159 MB** |
| **Workers** | 38 MB | 90 days | **114 MB** |
| **TOTAL** | 9 GB | - | **~8.9 GB steady state** |

---

## CloudWatch Logs Costs

### Pricing (ap-southeast-1):
- **Ingestion:** $0.50 per GB
- **Storage:** $0.03 per GB-month
- **Vended Logs (cross-account):** $0.10 per GB (not applicable)
- **Data Scanning (Insights):** $0.005 per GB

### Monthly Costs:

| Cost Component | Volume | Rate | Cost |
|----------------|--------|------|------|
| **Ingestion** | 9 GB | $0.50/GB | **$4.50** |
| **Storage** | 8.9 GB | $0.03/GB | **$0.27** |
| **Data Scanning** (occasional) | 1 GB | $0.005/GB | **$0.01** |
| **TOTAL** | - | - | **$4.78/month** |

**Annual CloudWatch Logs Cost:** **$57.36/year**

### Cost Breakdown by Service:

| Service | Monthly Ingestion | Ingestion Cost | Storage Cost | Total |
|---------|-------------------|----------------|--------------|-------|
| **Call Processing** | 8.6 GB | $4.30 | $0.26 | **$4.56** (95%) |
| **Gateway** | 53 MB | $0.03 | $0.005 | **$0.035** (1%) |
| **Workers** | 38 MB | $0.02 | $0.003 | **$0.023** (0.5%) |
| **System/Overhead** | 240 MB | $0.12 | $0.007 | **$0.127** (2.7%) |
| **TOTAL** | 9 GB | $4.47 | $0.28 | **$4.78** |

---

## Comparison with Other Infrastructure Costs

### Infrastructure Cost Summary:

| Service | Monthly Cost | Yearly Cost | Primary Driver |
|---------|--------------|-------------|----------------|
| **DynamoDB** | $0.30 | $3.60 | Job tracking & deduplication |
| **S3 Storage** | $0.99 | $11.88 | Call recordings, transcripts, analysis |
| **CloudWatch Logs** | $4.78 | $57.36 | Call processing logs (96%) |
| **OpenAI API** | $518 | $6,216 | Transcription + analysis |
| **TOTAL INFRASTRUCTURE** | **$524** | **$6,289** | OpenAI is 99% of cost |

**Key Insight:** CloudWatch Logs ($57/year) is **minimal compared to OpenAI** ($6,216/year)

---

## Log Volume by Category

### 1. Call Processing Logs (96% of volume)

**Per Call:**
- Fetch task: 20 KB
- Deduplication: 5 KB
- Download recording: 100 KB
- Transcribe (OpenAI API): 500 KB
- Upload to S3: 50 KB
- Register Glue: 30 KB
- AI analysis: 250 KB
- Salesforce actions: 20 KB
- Completion: 25 KB

**Total:** ~1 MB per call ✅

**Monthly (8,640 calls):** 8.6 GB

### 2. Gateway/API Logs (3% of volume)

**Per Day:**
- HTTP access logs: 1,200 requests × 200 bytes = 240 KB
- MCP tool calls: 240 calls × 500 bytes = 120 KB
- Health checks: 720 checks × 100 bytes = 72 KB
- Error/warning logs: 10 × 1 KB = 10 KB
- System logs: 50 × 500 bytes = 25 KB

**Total:** ~470 KB/day × 4 containers = 1.88 MB/day

**Monthly:** ~56 MB

### 3. Worker Logs (1% of volume)

**Per Worker Per Day:**
- Startup logs: 2 KB
- Tool execution: 240 KB
- Heartbeat: 72 KB
- Error logs: 2 KB

**Total:** ~316 KB/day × 4 workers = 1.26 MB/day

**Monthly:** ~38 MB

---

## Log Optimization Strategies

### 1. Reduce Call Processing Log Volume

**Current:** 1 MB per call

**Optimization Options:**

| Strategy | Savings | Trade-off |
|----------|---------|-----------|
| **Log Level: WARNING** (errors only) | 80% reduction to 200 KB/call | Lose debugging info |
| **Structured Logging** (JSON only, no verbose) | 40% reduction to 600 KB/call | Less human-readable |
| **Log Sampling** (detailed logs for 10% of calls) | 70% reduction to 300 KB/call | Limited visibility |
| **S3-Only Detailed Logs** (CloudWatch summary only) | 90% reduction to 100 KB/call | Need S3 for debugging |

**Recommendation:** Use **S3-Only Detailed Logs** option:
- CloudWatch: Summary logs only (100 KB per call)
- S3: Full detailed logs (900 KB per call)
- **Savings:** $40/year in CloudWatch costs
- **Benefit:** S3 storage much cheaper ($0.025/GB vs $0.50/GB ingestion)

### 2. Optimize Gateway Logs

**Current:** 442 KB/day per container

**Options:**
- Reduce health check logging (720 logs/day → 48 logs/day)
- **Savings:** 50% reduction
- **New Cost:** $0.02/month (negligible)

### 3. Implement Log Retention Tiers

| Priority | Retention | Volume | Cost Impact |
|----------|-----------|--------|-------------|
| **Critical Errors** | 180 days | ~1% | +$0.01/month |
| **Call Processing** | 30 days | 96% | Base cost |
| **Gateway/Workers** | 90 days | 3% | +$0.05/month |
| **Debug Logs** | 7 days | N/A | Not enabled |

---

## Scaling Projections

### If Call Volume Increases:

| Calls/Day | Calls/Month | Call Logs/Month | Gateway Logs | Total/Month | Monthly Cost |
|-----------|-------------|-----------------|--------------|-------------|--------------|
| **288** (current) | 8,640 | 8.6 GB | 53 MB | **9 GB** | $4.78 |
| **576** (2x) | 17,280 | 17.3 GB | 53 MB | **18 GB** | $9.30 |
| **1,440** (5x) | 43,200 | 43.2 GB | 53 MB | **45 GB** | $22.90 |
| **2,880** (10x) | 86,400 | 86.4 GB | 53 MB | **90 GB** | $45.50 |

**Cost Scaling:** Nearly linear with call volume (call logs are 96% of cost)

---

## Optimization Recommendations

### Immediate Actions (No Code Changes):

1. **Set Retention Policies**
   - Call processing: 30 days
   - Gateway/Workers: 90 days
   - **Savings:** Minimal (storage is cheap)

2. **Enable Log Insights**
   - Query logs for patterns
   - Identify optimization opportunities
   - **Cost:** $0.01-0.05/month

### Medium-Term Optimizations:

3. **Implement S3 Log Archiving**
   - CloudWatch: Summary logs only (100 KB/call)
   - S3: Full detailed logs (900 KB/call)
   - **Savings:** ~$40/year
   - **Benefit:** Cheaper storage + better querying (Athena)

4. **Structured JSON Logging**
   - Consistent log format
   - Better Insights queries
   - More efficient parsing
   - **Savings:** ~10-20% log size reduction

5. **Log Sampling for High Volume**
   - Detailed logs for 10% of calls
   - Summary logs for rest
   - **Savings:** ~70% reduction at high scale
   - **Apply when:** Call volume > 50,000/month

---

## CloudWatch Logs vs S3 Storage

### Cost Comparison:

| Storage Type | Ingestion | Storage | Total/GB | Use Case |
|--------------|-----------|---------|----------|----------|
| **CloudWatch** | $0.50/GB | $0.03/GB-month | **$0.53/GB** | Real-time, recent logs |
| **S3 Standard** | Free | $0.025/GB-month | **$0.025/GB** | Archive, analysis |
| **S3 Glacier** | Free | $0.004/GB-month | **$0.004/GB** | Long-term archive |

**Recommendation for Call Logs:**
- **Days 0-7:** CloudWatch (real-time debugging)
- **Days 8-90:** S3 Standard (cheaper storage, Athena queries)
- **Days 91+:** S3 Glacier (long-term compliance)

**Savings:** ~85% cost reduction for logs older than 7 days

---

## Summary

### Current Configuration (1 call/job, every 5 min):

| Metric | Value |
|--------|-------|
| **Calls per Month** | 8,640 |
| **Total Logs Ingested** | 9 GB/month |
| **CloudWatch Cost** | $4.78/month ($57/year) |
| **Cost per Call** | $0.00055 (~0.055¢) |

### Log Volume Breakdown:

| Service | Monthly Volume | Percentage |
|---------|----------------|------------|
| **Call Processing Jobs** | 8.6 GB | **96%** |
| **MCP HTTP Gateway** | 53 MB | **1%** |
| **MCP Workers** | 38 MB | **0.4%** |
| **System/Overhead** | 240 MB | **2.7%** |

### Key Insights:

✅ **Call processing dominates** - 96% of CloudWatch logs  
✅ **Cost is reasonable** - $57/year for complete audit trail  
✅ **Scalable** - Cost scales linearly with call volume  
✅ **Gateway efficient** - Only 53 MB/month for all APIs  
✅ **Optimization available** - S3 archiving can save 85% for old logs  

### Optimization Potential:

| Strategy | Current Cost | Optimized Cost | Savings |
|----------|--------------|----------------|---------|
| **No optimization** | $57/year | - | - |
| **S3 archiving (7+ days)** | $57/year | $8.50/year | **$48.50** (85%) |
| **Log sampling (10%)** | $57/year | $8.70/year | **$48.30** (85%) |
| **Combined optimizations** | $57/year | $3/year | **$54** (95%) |

**Recommendation:** At current scale ($57/year), optimization is not urgent. Implement S3 archiving when costs exceed $100/month (at 20,000+ calls/month).

---

## Infrastructure Cost Comparison

### All AWS Services (Monthly):

| Service | Cost | Percentage | Purpose |
|---------|------|------------|---------|
| **OpenAI API** | $518 | **98.8%** | Transcription + AI analysis |
| **CloudWatch Logs** | $4.78 | **0.9%** | Logging and monitoring |
| **S3 Storage** | $0.99 | **0.2%** | Call data storage |
| **DynamoDB** | $0.30 | **0.06%** | Metadata and tracking |
| **ECS Fargate** | Variable | - | Compute (charged separately) |
| **TOTAL (excl. compute)** | **$524** | **100%** | Per month |

**Annual Total:** $6,289 (infrastructure only, excluding ECS compute)

**Key Insight:** OpenAI costs ($6,216/year) dwarf all other costs. CloudWatch Logs ($57/year) and DynamoDB ($3.60/year) are negligible by comparison.

---

**Prepared by:** Platform Architecture Team  
**Date:** January 2026  
**Related Documents:**  
- [DynamoDB Operations Analysis](dynamodb-operations-analysis.md)
- [Infrastructure Requirements](INFRASTRUCTURE_REQUIREMENTS.md)
- [Job Execution Flow](architecture/job-execution-flow.md)
