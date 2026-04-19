# Call Processing Algorithm

This document describes the call processing algorithm implemented in `src/stages/call-process/`. The Call Processing Stage handles Webex Contact Center (CC) calls as part of the journey management system.

---

## Overview

The call processing pipeline transforms raw Webex CC telephony tasks into enriched call records stored in S3 and catalogued in AWS Glue for analytics.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CALL PROCESSING PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Webex CC API   ──►  Fetch Tasks   ──►  Deduplicate  ──►  Process Recordings│
│                                                                             │
│                      Register Metadata  ◄──  Transcribe  ◄──┘               │
│                             │                                               │
│                             ▼                                               │
│                      AI Analysis   ──►   S3 + Glue Catalog                  │
│                             │                                               │
│                             ▼                                               │
│                      CRM Actions   ──►   Salesforce (Leads/Opportunities)   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Processing Steps

The algorithm executes 6 sequential steps:

```
┌──────────────────┐
│  1. FETCH TASKS  │  Query Webex CC for telephony tasks in time window
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. DEDUPLICATION │  Check DynamoDB for previously processed task IDs
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. PROCESS RECS  │  Download recordings, transcribe, upload to S3
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 4. REGISTER META │  Create JSON metadata, register Glue partitions
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 5. AI ANALYSIS   │  Run GPT analysis on transcripts, store results
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 6. CRM ACTIONS   │  Create/update Salesforce leads and opportunities
└──────────────────┘
```

---

## Step 1: Fetch Tasks

Retrieves telephony tasks from Webex CC API for a configurable time window.

```
┌─────────────────────────────────────────────────────────────┐
│                    FETCH TASKS FLOW                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Config                                                    │
│   ┌──────────────────┐                                      │
│   │ minutes_back:    │                                      │
│   │ 10080 (7 days)   │                                      │
│   └────────┬─────────┘                                      │
│            │                                                │
│            ▼                                                │
│   ┌──────────────────┐     ┌──────────────────┐             │
│   │ Calculate        │────►│ Webex CC API     │             │
│   │ from_time        │     │ GET /tasks       │             │
│   │ (now - minutes)  │     │ channel=telephony│             │
│   └──────────────────┘     └────────┬─────────┘             │
│                                     │                       │
│                                     ▼                       │
│                            ┌──────────────────┐             │
│                            │ Store tasks in   │             │
│                            │ self.tasks[]     │             │
│                            │ self.task_data_map{}│          │
│                            └──────────────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Output**: List of task objects with task IDs, status, and metadata.

---

## Step 2: Deduplication Check

Prevents reprocessing of already-handled tasks by checking DynamoDB.

```
┌─────────────────────────────────────────────────────────────┐
│                 DEDUPLICATION FLOW                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   self.tasks[]                                              │
│       │                                                     │
│       ▼                                                     │
│   ┌──────────────────┐     ┌──────────────────┐             │
│   │ Extract task_ids │────►│ TaskTracker      │             │
│   │ from tasks       │     │ (DynamoDB)       │             │
│   └──────────────────┘     └────────┬─────────┘             │
│                                     │                       │
│                                     ▼                       │
│                            ┌──────────────────┐             │
│                            │ batch_check_     │             │
│                            │ processed()      │             │
│                            └────────┬─────────┘             │
│                                     │                       │
│                    ┌────────────────┴────────────────┐      │
│                    ▼                                 ▼      │
│           ┌──────────────┐                 ┌──────────────┐ │
│           │ new_task_ids │                 │skipped_task_ │ │
│           │ (to process) │                 │ids (already  │ │
│           │              │                 │done)         │ │
│           └──────────────┘                 └──────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Logic**:
- If `skip_processed=True` (default): Filter out already-processed tasks
- If `skip_processed=False`: Process all tasks regardless of history

---

## Step 3: Process Recordings

For each new task, download recording, transcribe, and upload to S3.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PROCESS RECORDINGS FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   FOR EACH task_id IN new_task_ids:                                         │
│                                                                             │
│   ┌──────────────────┐                                                      │
│   │ TaskTracker      │                                                      │
│   │ mark_processing()│◄─────────────────────────────────────┐               │
│   └────────┬─────────┘                                      │               │
│            │                                                │               │
│            ▼                                                │               │
│   ┌──────────────────┐     ┌──────────────────┐             │               │
│   │ WXCCAPI          │────►│ Download         │             │               │
│   │ process_task_    │     │ Recording        │             │               │
│   │ unified()        │     │ (WAV/MP3)        │             │               │
│   └──────────────────┘     └────────┬─────────┘             │               │
│                                     │                       │               │
│                                     ▼                       │               │
│                            ┌──────────────────┐             │               │
│                            │ Transcribe       │             │               │
│                            │ (if enabled)     │             │               │
│                            └────────┬─────────┘             │               │
│                                     │                       │               │
│                                     ▼                       │               │
│                            ┌──────────────────┐             │               │
│                            │ Upload to S3     │             │               │
│                            │ s3://bucket/     │             │               │
│                            │ call-detail/     │             │               │
│                            │ {task_id}/       │             │               │
│                            └────────┬─────────┘             │               │
│                                     │                       │               │
│            ┌────────────────────────┴────────────────────┐  │               │
│            ▼                                             ▼  │               │
│   ┌────────────────┐                           ┌────────────────┐           │
│   │ SUCCESS:       │                           │ FAILURE:       │           │
│   │ mark_success() │                           │ mark_failed()  │           │
│   │ + collect      │                           │ + store error  │           │
│   │   transcript   │                           │                │           │
│   └────────────────┘                           └────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**S3 Structure**:
```
s3://{bucket}/
├── call-detail/
│   └── {task_id}/
│       ├── recording.wav     # Original audio
│       └── transcript.json   # Transcribed text with speaker labels
```

---

## Step 4: Register Metadata

Creates JSON metadata files and registers Glue partitions for analytics.

```
┌─────────────────────────────────────────────────────────────┐
│                 REGISTER METADATA FLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   processed_results[]                                       │
│       │                                                     │
│       ▼                                                     │
│   ┌──────────────────┐     ┌──────────────────┐             │
│   │ Create metadata  │────►│ Upload to S3     │             │
│   │ JSON per task    │     │ call-data/       │             │
│   │                  │     │ year=.../month=. │             │
│   └──────────────────┘     └────────┬─────────┘             │
│                                     │                       │
│                                     ▼                       │
│                            ┌──────────────────┐             │
│                            │ Glue Catalog     │             │
│                            │ Add partition    │             │
│                            │ (if register_glue│             │
│                            │  = True)         │             │
│                            └──────────────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Glue Partitioning Schema**:
```
call-data/
├── year=2026/
│   └── month=01/
│       └── day=07/
│           └── hour=14/
│               └── {task_id}.json
```

**Metadata JSON Fields**:
```json
{
  "task_id": "...",
  "status": "completed|abandoned",
  "direction": "inbound|outbound",
  "origin_phone": "+1234567890",
  "destination_phone": "+0987654321",
  "queue_name": "Support",
  "agent_name": "John Doe",
  "duration_seconds": 180,
  "recording_file": "s3://...",
  "transcript_file": "s3://...",
  "analysis_file": "s3://..."
}
```

---

## Step 5: AI Analysis

Runs GPT-powered comprehensive analysis on collected transcripts.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AI ANALYSIS FLOW                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   self.transcripts[]                                                        │
│       │                                                                     │
│       ▼                                                                     │
│   ┌──────────────────┐     ┌──────────────────┐                             │
│   │ Format segments  │────►│ AIAnalyzer       │                             │
│   │ with speaker     │     │ analyze_call_    │                             │
│   │ labels           │     │ comprehensive()  │                             │
│   └──────────────────┘     └────────┬─────────┘                             │
│                                     │                                       │
│                                     ▼                                       │
│                            ┌──────────────────┐                             │
│                            │ OpenAI GPT       │                             │
│                            │ Analysis:        │                             │
│                            │ • Summary        │                             │
│                            │ • Sentiment      │                             │
│                            │ • Grading        │                             │
│                            │ • Issues         │                             │
│                            └────────┬─────────┘                             │
│                                     │                                       │
│                                     ▼                                       │
│                            ┌──────────────────┐                             │
│                            │ Upload analysis  │                             │
│                            │ to S3            │                             │
│                            │ call-detail/     │                             │
│                            │ {task_id}/       │                             │
│                            │ analysis.json    │                             │
│                            └────────┬─────────┘                             │
│                                     │                                       │
│                                     ▼                                       │
│                            ┌──────────────────┐                             │
│                            │ Update metadata  │                             │
│                            │ with analysis_   │                             │
│                            │ file reference   │                             │
│                            └──────────────────┘                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Analysis Output**:
```json
{
  "call_id": "...",
  "summary": "Customer called about billing issue...",
  "sentiment": "neutral",
  "grading": {
    "total_score_percent": 85,
    "pass": true,
    "categories": {...}
  },
  "issues_detected": [...],
  "recommendations": [...]
}
```

---

## Step 6: CRM Actions

Processes analyzed transcripts and creates/updates Salesforce CRM records via Python integration.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CRM ACTIONS - PROCESSING FLOW PER CALL                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   6.1 READ TRANSCRIPT FROM S3                                               │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ s3_client.get_object()                                              │   │
│   │ • Read JSON transcript with metadata + transcript text              │   │
│   │ • Extract: caller_name, customer_name, company, email, phone        │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                          │                                                  │
│                          ▼                                                  │
│   6.2 DEDUPLICATION CHECK                                                   │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ s3_client.head_object("SFDC/<TaskId>.txt")                          │   │
│   │                                                                     │   │
│   │ • If EXISTS → SKIP this call (already processed)                    │   │
│   │ • If NOT EXISTS → Continue processing                               │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                          │                                                  │
│                          ▼                                                  │
│   6.3 ANALYZE TRANSCRIPT CONTENT                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ GPT analyzes transcript for:                                        │   │
│   │                                                                     │   │
│   │ • Call Type: New inquiry vs Existing customer renewal               │   │
│   │ • Customer Segment: SME / Enterprise / Consumer                     │   │
│   │ • Service Type: Internet, landline, broadband, etc.                 │   │
│   │ • Business Registration Number (BRN) - required for enterprise      │   │
│   │ • Lead ID (if mentioned - indicates conversion case)                │   │
│   │ • Revenue Flag Status                                               │   │
│   │ • Qualification strength (strong vs weak)                           │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                          │                                                  │
│                          ▼                                                  │
│   6.4 APPLY VALIDATION RULES                                                │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Match to one of 7 scenarios:                                        │   │
│   │                                                                     │   │
│   │ ✅ Good Lead Creation       → Create new Salesforce Lead            │   │
│   │ ✅ Lead to Opportunity      → Convert existing Lead to Opportunity  │   │
│   │ ✅ Existing Customer Renewal → Update Account/Opportunity           │   │
│   │ ❌ Requires Transfer        → Add note, transfer to Managed Accts   │   │
│   │ ❌ Insufficient Qualification → NO Salesforce action                │   │
│   │ ❌ Poor Data Practices      → Block lead creation                   │   │
│   │ ❌ Consumer Redirect        → Redirect to consumer hotline          │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                          │                                                  │
│                          ▼                                                  │
│   6.5 ARCHIVE ANALYSIS TO S3 (Dedup Marker)                                 │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ s3_client.put_object("SFDC/<TaskId>.txt")                           │   │
│   │ • Marks this call as processed                                      │   │
│   │ • Contains the analysis/decision made                               │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                          │                                                  │
│                          ▼                                                  │
│   6.6 EXECUTE SALESFORCE ACTIONS                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ SFDCClient (Python) → Salesforce REST API                           │   │
│   │                                                                     │   │
│   │ ACTION: Lead Creation                                               │   │
│   │ ┌─────────────────────────────────────────────────────────────────┐ │   │
│   │ │ sfdc_client.create_lead(company, brn, contact, requirements)   │ │   │
│   │ │ Output: New Lead record in Salesforce                          │ │   │
│   │ └─────────────────────────────────────────────────────────────────┘ │   │
│   │                                                                     │   │
│   │ ACTION: Lead Conversion                                             │   │
│   │ ┌─────────────────────────────────────────────────────────────────┐ │   │
│   │ │ sfdc_client.convert_lead(lead_id, customer_details)            │ │   │
│   │ │ Output: Lead → Opportunity + Account + Contact in SFDC         │ │   │
│   │ └─────────────────────────────────────────────────────────────────┘ │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**CRM Decision Logic**:

| Scenario | Condition | Salesforce Action |
|----------|-----------|-------------------|
| New Lead | Valid company, BRN, qualified inquiry | Create Lead |
| Lead Conversion | Transcript contains Lead ID (00Q...) | Convert Lead → Opportunity |
| Renewal (with Lead ID) | Existing customer + Lead ID | Convert Lead → Opportunity |
| Renewal (no Lead ID) | Existing customer, no Lead ID | Update existing Account/Opportunity |
| Revenue Flagged | Customer is revenue-flagged | Transfer to Managed Accounts |
| Insufficient Data | Missing BRN, vague requirements | NO action - log only |
| Consumer Call | Non-enterprise customer | Redirect to consumer hotline |

**S3 Deduplication Marker**:
```
s3://{bucket}/
├── SFDC/
│   └── {task_id}.txt    # Contains analysis decision, prevents reprocessing
```

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COMPONENT ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        CallProcessStage                             │   │
│   │  (extends BaseStage for journey integration)                        │   │
│   │                                                                     │   │
│   │  • execute_step(step_id, step_data)                                 │   │
│   │  • Logging & metrics via BaseStage                                  │   │
│   │  • S3 log/report upload                                             │   │
│   └────────────────────────────────┬────────────────────────────────────┘   │
│                                    │                                        │
│                                    │ uses                                   │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        CallProcessor                                │   │
│   │  (core processing logic)                                            │   │
│   │                                                                     │   │
│   │  • fetch_tasks()                                                    │   │
│   │  • check_deduplication()                                            │   │
│   │  • process_recordings()                                             │   │
│   │  • register_metadata()                                              │   │
│   │  • run_ai_analysis()                                                │   │
│   │  • run_crm_actions()           ◄── NEW: CRM integration step        │   │
│   │  • generate_execution_report()                                      │   │
│   └────────────────────────────────┬────────────────────────────────────┘   │
│                                    │                                        │
│          ┌─────────────────────────┼─────────────────────────┐              │
│          │                         │                         │              │
│          ▼                         ▼                         ▼              │
│   ┌────────────────┐     ┌────────────────┐       ┌────────────────┐        │
│   │    WXCCAPI     │     │  TaskTracker   │       │   AIAnalyzer   │        │
│   │ (Webex CC API) │     │  (DynamoDB)    │       │  (OpenAI GPT)  │        │
│   └────────────────┘     └────────────────┘       └────────────────┘        │
│                                                                             │
│                                    │                                        │
│                                    ▼                                        │
│                         ┌────────────────────┐                              │
│                         │   SFDCClient       │                              │
│                         │  (Salesforce API)  │                              │
│                         │                    │                              │
│                         │  • create_lead()   │                              │
│                         │  • convert_lead()  │                              │
│                         │  • update_account()│                              │
│                         └────────────────────┘                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Configuration

The processing behavior is controlled via `CallProcessConfig`:

| Parameter        | Default | Description                                    |
|-----------------|---------|------------------------------------------------|
| `minutes_back`  | 10080   | Time window to fetch tasks (7 days)            |
| `transcribe`    | True    | Enable audio transcription                     |
| `register_glue` | True    | Enable Glue catalog registration               |
| `run_analysis`  | True    | Enable AI analysis on transcripts              |
| `run_crm_actions`| True   | Enable Salesforce CRM integration              |
| `s3_bucket`     | ""      | S3 bucket for storage (from config provider)   |
| `skip_processed`| True    | Skip already-processed tasks (deduplication)   |
| `aws_region`    | ap-southeast-1 | AWS region                              |
| `sfdc_url`      | ""      | Salesforce instance URL                        |
| `sfdc_client_id`| ""      | Salesforce OAuth client ID                     |

---

## State Management

The `CallProcessor` maintains internal state across steps:

```
┌─────────────────────────────────────────────────────────────────┐
│                       PROCESSING STATE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Step 1 (fetch)        Step 2 (dedup)       Step 3 (proc)      │
│   ──────────────        ────────────────     ──────────────     │
│   self.tasks[]    ───►  self.new_task_ids[]  ───►  processed    │
│   self.task_data_map    self.skipped_task_ids    _results[]     │
│                                                  failed_        │
│                                                  results[]      │
│                                                  transcripts    │
│                                                                 │
│   Step 5 (analysis)     Step 6 (CRM)                            │
│   ─────────────────     ────────────                            │
│   self.analysis_        SFDC/<TaskId>.txt   (S3 dedup marker)   │
│   results{}             leads_created[]                         │
│                         leads_converted[]                       │
│                         crm_skipped[]                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Execution Report

At completion, `generate_execution_report()` produces a summary:

```
┌─────────────────────────────────────────────────────────────┐
│                   EXECUTION REPORT                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Execution Summary                                         │
│   ├── tasks_found: 25                                       │
│   ├── new_tasks: 10                                         │
│   ├── skipped_already_processed: 15                         │
│   ├── processed_successfully: 8                             │
│   ├── failed: 2                                             │
│   ├── transcripts_collected: 8                              │
│   └── analyzed: 8                                           │
│                                                             │
│   Glue Table State                                          │
│   ├── total_records: 150                                    │
│   ├── with_recording: 145                                   │
│   ├── with_transcript: 130                                  │
│   └── with_analysis: 120                                    │
│                                                             │
│   CRM Actions                                               │
│   ├── leads_created: 5                                      │
│   ├── leads_converted: 2                                    │
│   ├── accounts_updated: 1                                   │
│   └── crm_skipped: 2 (insufficient data)                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## External Dependencies

| Component           | Purpose                                      |
|--------------------|----------------------------------------------|
| Webex CC API       | Source of call tasks and recordings          |
| AWS S3             | Storage for recordings, transcripts, metadata|
| AWS Glue           | Data catalog for analytics                   |
| AWS Athena         | Query engine for Glue tables                 |
| DynamoDB           | Task deduplication tracking                  |
| OpenAI GPT         | AI-powered call analysis & CRM validation    |
| Salesforce API     | Lead and opportunity management (REST API)   |

---

## Files

- `call_process_stage.py` - Stage wrapper for journey integration (includes CRM step)
- `call_processor.py` - Core processing logic and state management
- `sfdc_client.py` - Salesforce API client for lead/opportunity operations
- `__init__.py` - Package exports

