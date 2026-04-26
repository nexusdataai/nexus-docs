# DynamoDB Operations Analysis
## NexusAI Data Platform - Job Execution

**Document Type:** Technical Analysis  
**Version:** 1.0  
**Date:** January 2026  
**Purpose:** Calculate DynamoDB read/write operations for transformation jobs

---

## Scenario Parameters

**Given:**
- **Job Frequency:** Every 5 minutes
- **Calls per Job:** 1 call
- **Job Data Size:** ~5KB per job record in DynamoDB
- **Call Data Size:** ~1KB per call record in DynamoDB (deduplication)
- **Storage:** Logs, analysis, transcripts in S3 (not DynamoDB)
- **Metadata:** All job metadata and status in DynamoDB

**Stage:** Call Processing (typical call processing job)
- **Number of Steps:** 5 steps per job
- **Calls Processed:** 1 call per job
- **Total Job Duration:** ~5-10 minutes per call

---

## DynamoDB Tables Used

The system uses **two separate DynamoDB tables**:

### Table 1: Transformation System Table
- **Purpose:** Track journeys, stages, and job executions
- **PK:** `JOURNEY#{journey_id}`
- **SK:** `JOB#{stage_order}#{stage_id}#{execution_number}#{timestamp}`
- **Usage:** Job orchestration and progress tracking

### Table 2: WXCC Task Tracking Table
- **Purpose:** Deduplication - prevent reprocessing of already-processed calls
- **PK:** `task_id` (Webex CC task identifier)
- **SK:** None (single-attribute key)
- **Usage:** Check if task already processed, mark tasks as SUCCESS/FAILED
- **TTL:** 30 days (automatic cleanup)

---

## DynamoDB Operations Per Job Execution

### Phase 0: Deduplication Check (Before Processing)

**For 1 Call:**

| Operation | Type | Description | Table | Item Size |
|-----------|------|-------------|-------|-----------|
| **0. Check if Processed** | READ | Check if task_id already processed | WXCC Tracking | ~1KB |

**Subtotal:** 1 Read + 0 Writes (to WXCC Tracking table)

**Note:** This is done ONCE per job before processing the call.

---

### Phase 1: Job Initialization (4 operations)

| Operation | Type | Description | Item Size |
|-----------|------|-------------|-----------|
| **1. Load Journey** | READ | Get journey metadata | ~2KB |
| **2. Create Job Record** | WRITE | Insert new job execution record | ~5KB |
| **3. Update Journey Current Job** | WRITE | Update journey with active job ID | ~2KB |
| **4. Get Job Data** | READ | Retrieve job for execution | ~5KB |

**Subtotal:** 2 Reads + 2 Writes

---

### Phase 2: Call Processing (1 call)

**For the Single Call Being Processed:**

| Operation | Type | Description | Table | Item Size |
|-----------|------|-------------|-------|-----------|
| **2a. Mark Processing** | WRITE | Mark task as "PROCESSING" | WXCC Tracking | ~1KB |
| **2b. Process Call** | - | Download, transcribe, analyze (S3 operations) | - | - |
| **2c. Mark Success** | WRITE | Mark task as "SUCCESS" with S3 path | WXCC Tracking | ~1KB |

**Subtotal:** 0 Reads + 2 Writes (to WXCC Tracking table)

---

### Phase 3: Step Execution (15 operations per job)

**For Each of 5 Steps:**

| Operation | Type | Description | Table | Item Size |
|-----------|------|-------------|-------|-----------|
| **5. Update Step Status START** | WRITE | Mark step as "in_progress" | Transformation | ~5KB |
| **6. Update Step Results** | WRITE | Save step completion data | Transformation | ~5KB |
| **7. Update Job Progress** | WRITE | Update overall job progress % | Transformation | ~5KB |

**Per Step:** 0 Reads + 3 Writes  
**Total for 5 Steps:** 0 Reads + 15 Writes (to Transformation table)

**Note:** Logs and reports are uploaded to S3, NOT DynamoDB

---

### Phase 4: Job Completion (2 operations)

| Operation | Type | Description | Table | Item Size |
|-----------|------|-------------|-------|-----------|
| **8. Complete Job** | WRITE | Mark job status as "completed" | Transformation | ~5KB |
| **9. Update Journey Statistics** | WRITE | Update journey stats (total jobs, success rate) | Transformation | ~2KB |

**Subtotal:** 0 Reads + 2 Writes (to Transformation table)

---

## Total Operations Per Job

### Call Processing Job (1 call per job)

| Phase | Reads | Writes | Total | Table |
|-------|-------|--------|-------|-------|
| **Deduplication Check** | 1 | 0 | 1 | WXCC Tracking |
| **Call Processing (1 call)** | 0 | 2 | 2 | WXCC Tracking |
| **Initialization** | 2 | 2 | 4 | Transformation |
| **Step Execution (5 steps)** | 0 | 15 | 15 | Transformation |
| **Completion** | 0 | 2 | 2 | Transformation |
| **TOTAL PER JOB** | **3** | **21** | **24** | Both tables |

**Breakdown by Table:**
- **WXCC Tracking Table:** 1 read + 2 writes = 3 operations per call
- **Transformation Table:** 2 reads + 19 writes = 21 operations per job

---

## Data Volume Per Job

### DynamoDB Storage:

**Transformation Table:**

| Item Type | Size | Count | Total |
|-----------|------|-------|-------|
| **Job Record** | 5KB | 1 | 5KB |
| **Journey Update** | 2KB | 1 | 2KB |
| **Step Results** | 5KB (updated 15x) | Final | 5KB |
| **Total per Job** | - | - | **~5KB** |

**WXCC Tracking Table:**

| Item Type | Size | Count | Total |
|-----------|------|-------|-------|
| **Call Record** | 1KB | 1 | 1KB |
| **Total per Call** | - | - | **~1KB** |

**Total per Job (1 call):** ~6KB (5KB job + 1KB call)

**Note:** Updates to the same item don't increase storage linearly; final item size is stored.

### S3 Storage (NOT DynamoDB):

| Item Type | Size | Count | Total |
|-----------|------|-------|-------|
| **Logs per Step** | ~100-500KB | 5 | 500KB-2.5MB |
| **Reports per Step** | ~50-200KB | 5 | 250KB-1MB |
| **Transcripts** | ~50-500KB | Variable | Variable |
| **Analysis** | ~20-100KB | Variable | Variable |
| **Total per Job** | - | - | **~1-5MB** |

---

## Operations at Scale

### Scenario: Call Processing Job Every 5 Minutes (1 call per job)

**Frequency Calculations:**
- Jobs per hour: 12 jobs (60 min ÷ 5 min)
- Jobs per day: 288 jobs (12 × 24)
- Jobs per month: 8,640 jobs (288 × 30)
- Jobs per year: 105,120 jobs (288 × 365)

**Calls per Month:** 8,640 calls (1 call/job × 8,640 jobs)  
**Calls per Year:** 105,120 calls

### DynamoDB Operations Per Month (1 call per job):

| Table | Reads per Job | Writes per Job | Reads/Month | Writes/Month |
|-------|---------------|----------------|-------------|--------------|
| **WXCC Tracking** | 1 | 2 | **8,640** | **17,280** |
| **Transformation** | 2 | 19 | **17,280** | **164,160** |
| **TOTAL** | **3** | **21** | **25,920** | **181,440** |
| **GRAND TOTAL** | - | - | **207,360 operations/month** | |

### DynamoDB Operations Per Year (1 call per job):

| Table | Reads/Month | Writes/Month | Reads/Year | Writes/Year |
|-------|-------------|--------------|------------|-------------|
| **WXCC Tracking** | 8,640 | 17,280 | **103,680** | **207,360** |
| **Transformation** | 17,280 | 164,160 | **207,360** | **1,969,920** |
| **TOTAL** | 25,920 | 181,440 | **311,040** | **2,177,280** |
| **GRAND TOTAL** | - | - | **2,488,320 operations/year (~2.5M)** | |

---

## Storage Calculations

### DynamoDB Storage:

**Transformation Table** (90-day retention):

| Period | Jobs | Storage per Job | Total Storage |
|--------|------|-----------------|---------------|
| **90 days** | 25,920 | 5KB | **129.6 MB** |

**WXCC Tracking Table** (30-day TTL):

| Period | Calls | Storage per Call | Total Storage |
|--------|-------|------------------|---------------|
| **30 days** | 8,640 | 1KB | **8.4 MB** |

**Total DynamoDB Storage:** ~138 MB (combined tables)

**Monthly Growth:** 
- Transformation: 43.2 MB (8,640 jobs × 5KB)
- WXCC Tracking: 8.4 MB (replaces expired records via TTL, so stable)

### S3 Storage:

**Assumption:** Jobs retained indefinitely

| Period | Jobs | Storage per Job | Total Storage |
|--------|------|-----------------|---------------|
| **1 Month** | 8,640 | 2.5MB (avg) | **21.6 GB** |
| **1 Year** | 105,120 | 2.5MB (avg) | **259.2 GB** (~260 GB) |

---

## AWS Costs Estimation

### DynamoDB Costs (On-Demand Pricing)

**Pricing (ap-southeast-1):**
- Read: $0.285 per million reads
- Write: $1.425 per million writes
- Storage: $0.25 per GB-month

**Monthly Costs (1 call per job):**

| Operation Type | Count | Rate | Cost |
|----------------|-------|------|------|
| **Reads** (both tables) | 25,920 | $0.285/million | **$0.01** |
| **Writes** (both tables) | 181,440 | $1.425/million | **$0.26** |
| **Storage** (both tables) | 0.138 GB | $0.25/GB | **$0.03** |
| **Total DynamoDB** | - | - | **$0.30/month** |

**Annual DynamoDB Cost:** **$3.60/year**

**Cost Breakdown by Table:**

| Table | Reads/Month | Writes/Month | Monthly Cost |
|-------|-------------|--------------|--------------|
| **WXCC Tracking** | 8,640 | 17,280 | $0.03 |
| **Transformation** | 17,280 | 164,160 | $0.27 |
| **TOTAL** | 25,920 | 181,440 | **$0.30** |

### S3 Costs (Standard Storage)

**Pricing (ap-southeast-1):**
- Storage: $0.025 per GB-month
- PUT requests: $0.005 per 1,000 requests
- GET requests: $0.0004 per 1,000 requests

**Monthly Costs:**

| Operation Type | Count/Size | Rate | Cost |
|----------------|------------|------|------|
| **Storage** | 21.6 GB | $0.025/GB | **$0.54** |
| **PUT (logs+reports)** | 86,400 | $0.005/1K | **$0.43** |
| **GET (read logs/reports)** | ~50,000 | $0.0004/1K | **$0.02** |
| **Total S3** | - | - | **$0.99/month** |

**Annual S3 Cost (Year 1):** **$11.88**  
**Annual S3 Cost (Year 2):** **$324** (cumulative storage: 260GB + 260GB)

### Combined Infrastructure Cost (1 call per job):

| Service | Monthly | Annual (Year 1) | Annual (Year 2) |
|---------|---------|-----------------|-----------------|
| **DynamoDB** | $0.30 | $3.60 | $3.60 |
| **S3** | $0.99 | $11.88 | $324 |
| **Total** | **$1.29** | **$15.48** | **$327.60** |

**Note:** These are infrastructure costs only for job metadata, deduplication, and results. Actual call processing costs (OpenAI transcription/analysis, Webex CC API calls) are separate and depend on call volume.

**Call Processing Additional Costs (estimated for 8,640 calls/month):**
- OpenAI Whisper transcription: ~$0.006 per minute of audio
- OpenAI GPT-4 analysis: ~$0.03 per call
- For 8,640 calls/month (avg 5 min each): ~$518/month OpenAI costs (~$6,216/year)

---

## Optimization Recommendations

### 1. DynamoDB Write Reduction

**Current:** 19 writes per job

**Optimization Options:**

**Option A: Batch Updates (Reduce to 7 writes)**
- Batch step status updates (write all 5 steps at once after completion)
- **Savings:** 63% reduction (19 → 7 writes)
- **Trade-off:** Less granular real-time progress

**Option B: Reduce Progress Updates (Reduce to 14 writes)**
- Update progress every 2 steps instead of every step
- **Savings:** 26% reduction (19 → 14 writes)
- **Trade-off:** Slightly less frequent progress visibility

**Option C: Consolidate Final Updates (Reduce to 17 writes)**
- Single write for job completion + journey stats
- **Savings:** 10% reduction (19 → 17 writes)
- **Trade-off:** Minimal

### 2. Storage Optimization

**DynamoDB:**
- Archive jobs older than 90 days to S3
- Use Time-to-Live (TTL) for automatic deletion
- **Savings:** ~$1-2/year (minimal)

**S3:**
- Use S3 Intelligent-Tiering for automatic cost optimization
- Move old logs to Glacier after 180 days
- **Savings:** ~50-70% on Year 2+ storage costs

---

## Capacity Planning

### DynamoDB Capacity

**Provisioned Capacity (if used):**
- **Read Capacity:** 1 RCU (very low) - 2 reads per 5 minutes
- **Write Capacity:** 1-2 WCU - 19 writes per 5 minutes = ~0.063 WCU

**Recommendation:** **Use On-Demand** (current setup)
- Cost-effective at this volume
- No capacity planning needed
- Automatic scaling

### S3 Capacity

**Storage Growth:**
- Month 1: 22 GB
- Month 6: 130 GB
- Month 12: 260 GB
- Month 24: 520 GB

**Recommendation:**
- Enable S3 Intelligent-Tiering (automatic cost optimization)
- Implement lifecycle policy:
  - 0-90 days: Standard
  - 91-365 days: Infrequent Access
  - 365+ days: Glacier

---

## Summary

### Per Job (5-minute frequency, 1 call per job):

| Metric | Value | Table |
|--------|-------|-------|
| **DynamoDB Reads** | 3 (1 dedup + 2 job) | Both |
| **DynamoDB Writes** | 21 (2 tracking + 19 job) | Both |
| **DynamoDB Storage** | ~6KB (5KB job + 1KB call) | Both |
| **S3 Writes** | 11 (1 call + 10 job) | - |
| **S3 Storage** | ~2.5MB (2.5MB call + logs) | - |

### Per Month (8,640 jobs, 8,640 calls):

| Metric | Value | Table |
|--------|-------|-------|
| **DynamoDB Reads** | 25,920 | Both |
| **DynamoDB Writes** | 181,440 | Both |
| **DynamoDB Storage** | ~138 MB | Both |
| **S3 Storage Growth** | ~22 GB | - |
| **Infrastructure Cost** | **$1.29** | - |

**Breakdown by Table:**
- **WXCC Tracking:** 8,640 reads + 17,280 writes = 26K ops/month
- **Transformation:** 17,280 reads + 164,160 writes = 181K ops/month

### Per Year (105,120 jobs, 105,120 calls):

| Metric | Value | Table |
|--------|-------|-------|
| **DynamoDB Reads** | 311,040 (~311K) | Both |
| **DynamoDB Writes** | 2,177,280 (~2.2M) | Both |
| **S3 Storage** | ~260 GB | - |
| **Infrastructure Cost** | **$15.48** (Year 1), **$327.60** (Year 2) | - |

---

## Key Insights

✅ **Very Low DynamoDB Costs** - $0.30/month (~$3.60/year) - Extremely cost-effective!  
✅ **Job Tracking is Primary Cost** - 87% of DynamoDB operations are for job orchestration  
✅ **Deduplication is Minor Cost** - 13% of operations (1 read + 2 writes per call)  
✅ **Moderate S3 Costs** - $1/month Year 1, growing with cumulative storage  
✅ **Total Infrastructure** - $15.48/year for complete call tracking, job orchestration, and audit trail  
✅ **Highly Scalable** - Can handle 10x volume with proportional cost increase  
✅ **On-Demand Optimal** - Current volume (181K writes/month) is perfect for on-demand pricing  

**Cost Drivers:**
- **Primary:** Transformation table (job tracking) - 181K operations/month (87%)
- **Secondary:** S3 storage growth - 260GB per year
- **Minor:** WXCC Tracking table (deduplication) - 26K operations/month (13%)

**Recommendation:** Current architecture is highly cost-optimal. Infrastructure costs are negligible compared to OpenAI processing costs ($518/month vs $1.29/month infrastructure).

---

## Impact of Frequency Changes

### If Job Frequency Increases (1 call per job):

| Frequency | Jobs/Month | Calls/Month | DynamoDB Ops/Month | Monthly Cost |
|-----------|------------|-------------|-------------------|--------------|
| **5 minutes** (current) | 8,640 | 8,640 | 207K | $0.30 |
| **1 minute** | 43,200 | 43,200 | 1.04M | $1.50 |
| **30 seconds** | 86,400 | 86,400 | 2.07M | $3.00 |
| **10 seconds** | 259,200 | 259,200 | 6.22M | $9.01 |

**Cost Breakdown (5 min frequency, 1 call/job):**
- Job Tracking (Transformation): $0.27/month (90% of cost)
- Deduplication (WXCC Tracking): $0.03/month (10% of cost)

**Recommendation:** At 5-minute frequency with 1 call/job:
- ✅ **$0.30/month is negligible** for 8,640 calls/month
- ✅ **Cost per call: $0.000035** (~0.0035¢ per call)
- ✅ Remain on on-demand pricing (extremely cost-effective)
- ✅ Even at 10-second frequency ($9/month), still very affordable
- ✅ Infrastructure costs are **minimal compared to OpenAI** ($0.30 vs $518/month)

---

**Prepared by:** Platform Architecture Team  
**Date:** January 2026  
**Based on:** [Job Execution Flow Documentation](architecture/job-execution-flow.md)
