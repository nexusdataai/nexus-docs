# Webex Call Recording Access and S3 Storage - Pseudo Code

## Overview
This document provides focused pseudo code for accessing call recordings from Webex Contact Center API and storing them in Amazon S3.

**Scope**: This document covers ONLY:
- ✅ Webex authentication and token management
- ✅ Webex API calls to fetch tasks and recordings
- ✅ Downloading recordings from Webex
- ✅ Uploading recordings to S3


## Table of Contents
1. [Webex Authentication](#1-webex-authentication)
2. [Webex API: Fetch Tasks](#2-webex-api-fetch-tasks)
3. [Webex API: Get Recording URL](#3-webex-api-get-recording-url)
4. [Download Recording from Webex](#4-download-recording-from-webex)
5. [Upload Recording to S3](#5-upload-recording-to-s3)
6. [Complete Workflow](#6-complete-workflow)

---

## 1. Webex Authentication

### Webex API Endpoints
- **Token Refresh URL**: `https://webexapis.com/v1/access_token`
- **Authorization URL**: `https://webexapis.com/v1/authorize`

### Required OAuth Scopes
```
spark-admin:recordings_read    # Read call recordings
spark-admin:recordings_write   # Access recording metadata
spark:kms                      # Key management for encryption
cjp:config                     # Contact center configuration
cjp:config_read                # Read contact center data
```

### Pseudo Code: Token Management

```python
FUNCTION initialize_authentication():
    """
    Initialize Webex authentication and manage tokens
    """
    # Load credentials from secrets (AWS Secrets Manager or local)
    credentials = load_secrets()
    
    config = {
        'client_id': credentials['client_id'],
        'client_secret': credentials['client_secret'],
        'org_id': credentials['org_id'],
        'base_url': 'https://api.wxcc-us1.cisco.com/v1',
        'redirect_uri': 'https://trilogy.com'
    }
    
    # Load existing tokens
    tokens = load_tokens()
    
    RETURN config, tokens
END FUNCTION


FUNCTION refresh_token_if_needed(tokens, config):
    """
    Check token expiration and refresh if needed
    API: POST https://webexapis.com/v1/access_token
    """
    current_time = get_current_timestamp()
    expires_at = tokens['expires_at']
    buffer_seconds = 300  # 5 minutes buffer
    
    IF current_time >= (expires_at - buffer_seconds):
        log("Token expired or expiring soon, refreshing...")
        
        # Prepare refresh request
        payload = {
            'grant_type': 'refresh_token',
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'refresh_token': tokens['refresh_token']
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Call token refresh API
        response = POST('https://webexapis.com/v1/access_token', 
                       data=payload, 
                       headers=headers)
        
        IF response.status == 200:
            token_data = response.json()
            
            # Update tokens
            new_tokens = {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', tokens['refresh_token']),
                'expires_in': token_data['expires_in'],
                'expires_at': current_time + token_data['expires_in'],
                'token_type': token_data.get('token_type', 'Bearer'),
                'scope': token_data.get('scope', '')
            }
            
            # Save updated tokens
            save_tokens(new_tokens)
            
            log("Token refreshed successfully")
            RETURN new_tokens
        ELSE:
            throw_error("Token refresh failed: " + response.text)
        END IF
    ELSE:
        log("Token still valid")
        RETURN tokens
    END IF
END FUNCTION


FUNCTION get_auth_headers(tokens):
    """
    Generate HTTP headers with access token
    """
    RETURN {
        'Authorization': 'Bearer ' + tokens['access_token'],
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
END FUNCTION
```

---

## 2. Webex API: Fetch Tasks

### API Details
- **Endpoint**: `GET https://api.wxcc-us1.cisco.com/v1/tasks`
- **Authentication**: Bearer token in Authorization header
- **Purpose**: Get list of calls/tasks from Webex Contact Center

### Query Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `from` | integer | Yes | Start time in milliseconds (Unix epoch) | `1736780400000` |
| `to` | integer | No | End time in milliseconds | `1736866800000` |
| `orgId` | string | Yes | Your Webex organization ID | `5bd961a5-2622-...` |
| `channelType` | string | No | Filter by channel type | `telephony` |
| `pageSize` | integer | No | Results per page (max 1000) | `100` |

### Pseudo Code: Fetch Tasks

```python
FUNCTION get_tasks(config, tokens, time_range):
    """
    Fetch tasks/calls from Webex Contact Center
    API: GET {base_url}/tasks
    """
    # Ensure token is valid
    tokens = refresh_token_if_needed(tokens, config)
    
    # Calculate time range
    IF time_range.from_time is NULL:
        # Default: last N days
        from_time = (current_time() - (time_range.days_back * 24 * 3600)) * 1000
    ELSE:
        from_time = time_range.from_time
    END IF
    
    # Build API URL
    url = config['base_url'] + '/tasks'
    
    # Build query parameters
    params = {
        'from': from_time,
        'orgId': config['org_id'],
        'channelType': 'telephony',
        'pageSize': 100
    }
    
    IF time_range.to_time is NOT NULL:
        params['to'] = time_range.to_time
    END IF
    
    # Get authorization headers
    headers = get_auth_headers(tokens)
    
    # Make API request
    response = GET(url, params=params, headers=headers)
    
    IF response.status == 200:
        data = response.json()
        tasks = data['data']
        
        log("Retrieved " + len(tasks) + " tasks")
        
        # Extract task information
        task_list = []
        FOR EACH task IN tasks:
            task_info = {
                'task_id': task['id'],
                'status': task['attributes']['status'],
                'direction': task['attributes']['direction'],
                'origin': task['attributes']['origin'],
                'destination': task['attributes']['destination'],
                'created_time': task['attributes']['createdTime'],
                'ended_time': task['attributes']['endedTime'],
                'queue_name': task['attributes']['queue']['name'],
                'agent_name': task['attributes']['owner']['name'],
                'duration': task['attributes']['totalDuration']
            }
            task_list.append(task_info)
        END FOR
        
        RETURN {
            'success': TRUE,
            'tasks': task_list,
            'total_count': len(tasks),
            'metadata': data.get('meta')
        }
    ELSE:
        throw_error("Failed to get tasks: " + response.status + " - " + response.text)
    END IF
END FUNCTION
```

---

## 3. Webex API: Get Recording URL

### API Details
- **Endpoint**: `POST https://api.wxcc-us1.cisco.com/v1/captures/query`
- **Authentication**: Bearer token in Authorization header
- **Purpose**: Get recording metadata and download URL for specific call(s)

### Request Body Format
```json
{
  "query": {
    "taskIds": ["99a53828-6a11-4bee-a257-8730a56963ce"]
  }
}
```

### Response Format
```json
{
  "data": [
    {
      "taskId": "99a53828-6a11-4bee-a257-8730a56963ce",
      "recording": [
        {
          "id": "recording-id",
          "attributes": {
            "fileName": "recording.wav",
            "filePath": "https://storage.webex.com/...",  // Pre-signed download URL
            "startTime": 1736780400000,
            "stopTime": 1736780700000,
            "participants": ["agent@example.com", "+1234567890"],
            "channel1": "agent",
            "channel2": "customer",
            "callType": "inbound"
          }
        }
      ]
    }
  ]
}
```

### Pseudo Code: Get Recording URL

```python
FUNCTION get_recording_url(config, tokens, task_id):
    """
    Get recording URL and metadata for a specific task
    API: POST {base_url}/captures/query
    """
    # Ensure token is valid
    tokens = refresh_token_if_needed(tokens, config)
    
    # Build API URL
    url = config['base_url'] + '/captures/query'
    
    # Build request payload
    payload = {
        'query': {
            'taskIds': [task_id]
        }
    }
    
    # Get authorization headers
    headers = get_auth_headers(tokens)
    
    # Make API request
    response = POST(url, json=payload, headers=headers)
    
    IF response.status == 200:
        data = response.json()
        
        # Extract recording information
        recordings = []
        FOR EACH item IN data['data']:
            item_task_id = item['taskId']
            
            FOR EACH recording IN item['recording']:
                recording_info = {
                    'task_id': item_task_id,
                    'recording_id': recording['id'],
                    'file_name': recording['attributes']['fileName'],
                    'file_path': recording['attributes']['filePath'],  # Pre-signed download URL
                    'start_time': recording['attributes']['startTime'],
                    'stop_time': recording['attributes']['stopTime'],
                    'participants': recording['attributes']['participants'],
                    'channel1': recording['attributes']['channel1'],
                    'channel2': recording['attributes']['channel2'],
                    'call_type': recording['attributes']['callType']
                }
                recordings.append(recording_info)
            END FOR
        END FOR
        
        IF len(recordings) > 0:
            log("Found " + len(recordings) + " recording(s) for task " + task_id)
            RETURN {
                'success': TRUE,
                'recordings': recordings,
                'metadata': data.get('meta')
            }
        ELSE:
            log("No recordings found for task " + task_id)
            RETURN {
                'success': FALSE,
                'recordings': [],
                'error': 'No recording available'
            }
        END IF
    ELSE:
        throw_error("Failed to get recording URL: " + response.status + " - " + response.text)
    END IF
END FUNCTION
```

---

## 4. Download Recording from Webex

### Important Notes
⚠️ **Critical**: Recording URLs from Webex are **pre-signed URLs**
- **DO NOT send Authorization headers** when downloading
- The URL itself contains authentication parameters
- URLs are time-limited (typically 1-2 hours validity)
- Download using simple HTTP GET request

### Pseudo Code: Download Recording

```python
FUNCTION download_recording(file_url, local_path):
    """
    Download recording file from pre-signed URL
    NOTE: No authentication headers needed - URL is pre-signed
    """
    log("Downloading recording from: " + file_url)
    log("Saving to: " + local_path)
    
    # Create directory if it doesn't exist
    create_directory(parent_directory(local_path))
    
    # Make download request WITHOUT authentication headers
    # Pre-signed URLs contain authentication in the URL itself
    response = GET(file_url, stream=TRUE, timeout=300)
    
    IF response.status == 200:
        bytes_downloaded = 0
        start_time = current_time()
        
        # Write file in chunks
        OPEN local_path FOR BINARY WRITE AS file:
            FOR EACH chunk IN response.iter_content(chunk_size=8192):
                file.write(chunk)
                bytes_downloaded += len(chunk)
            END FOR
        END OPEN
        
        download_time = current_time() - start_time
        file_size = get_file_size(local_path)
        speed = file_size / download_time / 1024  # KB/s
        
        log("Download complete:")
        log("  File size: " + file_size + " bytes")
        log("  Download time: " + download_time + " seconds")
        log("  Speed: " + speed + " KB/s")
        
        RETURN {
            'success': TRUE,
            'local_path': local_path,
            'file_size': file_size,
            'download_time': download_time
        }
    ELSE:
        throw_error("Failed to download recording: " + response.status + " - " + response.text)
    END IF
END FUNCTION
```

---

## 5. Upload Recording to S3

### S3 Storage Structure

Simple storage approach - store recordings by task ID:

```
s3://your-bucket-name/
└── call-detail/
    ├── task-id-1/
    │   └── recording.wav
    ├── task-id-2/
    │   └── recording.mp3
    └── task-id-3/
        └── recording.wav
```

### Content Type Mapping

| File Extension | Content-Type |
|----------------|--------------|
| `.wav` | `audio/wav` |
| `.mp3` | `audio/mpeg` |
| `.m4a` | `audio/mp4` |
| `.ogg` | `audio/ogg` |
| `.flac` | `audio/flac` |

### Pseudo Code: Upload to S3

```python
FUNCTION upload_to_s3(local_path, bucket, s3_key, content_type):
    """
    Upload a file to S3
    """
    log("Uploading to S3:")
    log("  Local: " + local_path)
    log("  S3: s3://" + bucket + "/" + s3_key)
    
    # Get file size
    file_size = get_file_size(local_path)
    
    # Create S3 client
    s3_client = create_s3_client(region='ap-southeast-1')
    
    # Upload file
    start_time = current_time()
    
    s3_client.upload_file(
        Filename=local_path,
        Bucket=bucket,
        Key=s3_key,
        ExtraArgs={
            'ContentType': content_type
        }
    )
    
    upload_time = current_time() - start_time
    speed = file_size / upload_time / 1024  # KB/s
    s3_uri = "s3://" + bucket + "/" + s3_key
    
    log("Upload complete:")
    log("  S3 URI: " + s3_uri)
    log("  Upload time: " + upload_time + " seconds")
    log("  Speed: " + speed + " KB/s")
    
    RETURN {
        'success': TRUE,
        'bucket': bucket,
        's3_key': s3_key,
        's3_uri': s3_uri,
        'file_size': file_size,
        'upload_time': upload_time
    }
END FUNCTION
```

---

## 6. Complete Workflow

### Pseudo Code: Fetch, Download, and Store Recording

```python
FUNCTION process_single_recording(task_id, config):
    """
    Simple workflow: Fetch recording from Webex and store in S3
    
    Steps:
    1. Initialize authentication
    2. Get recording URL from Webex API
    3. Download recording from Webex
    4. Upload recording to S3
    """
    log("===== PROCESSING RECORDING: " + task_id + " =====")
    
    # Initialize authentication
    config, tokens = initialize_authentication()
    
    result = {
        'task_id': task_id,
        'recording_file': NULL,
        's3_uri': NULL,
        'error': NULL
    }
    
    
    # ============================================================
    # STEP 1: Get Recording URL from Webex
    # ============================================================
    log("Step 1: Calling Webex API to get recording URL...")
    
    TRY:
        recording_data = get_recording_url(config, tokens, task_id)
        
        IF NOT recording_data['success'] OR len(recording_data['recordings']) == 0:
            result['error'] = "No recording available for task"
            log("ERROR: No recording found")
            RETURN result
        END IF
        
        recording = recording_data['recordings'][0]
        file_url = recording['file_path']        # Pre-signed download URL
        file_name = recording['file_name']       # e.g., "recording.wav"
        
        log("✓ Recording URL obtained: " + file_name)
        
    CATCH error:
        result['error'] = "Webex API failed: " + error
        log("ERROR: " + error)
        RETURN result
    END TRY
    
    
    # ============================================================
    # STEP 2: Download Recording from Webex
    # ============================================================
    log("Step 2: Downloading recording from Webex...")
    
    # Determine file extension
    file_ext = get_file_extension(file_name)  # e.g., ".wav", ".mp3"
    
    # Create temporary file path
    temp_recording = get_temp_path() + "/" + task_id + file_ext
    
    TRY:
        download_result = download_recording(file_url, temp_recording)
        
        file_size = download_result['file_size']
        log("✓ Downloaded " + file_size + " bytes")
        
    CATCH error:
        result['error'] = "Download failed: " + error
        log("ERROR: " + error)
        RETURN result
    END TRY
    
    
    # ============================================================
    # STEP 3: Upload Recording to S3
    # ============================================================
    log("Step 3: Uploading recording to S3...")
    
    # Build S3 key: call-detail/{task_id}/recording.{ext}
    s3_key = "call-detail/" + task_id + "/recording" + file_ext
    
    # Map file extension to content type
    content_types = {
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.m4a': 'audio/mp4',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac'
    }
    content_type = content_types.get(file_ext, 'audio/wav')
    
    TRY:
        upload_result = upload_to_s3(
            local_path=temp_recording,
            bucket=config['s3_bucket'],
            s3_key=s3_key,
            content_type=content_type
        )
        
        result['s3_uri'] = upload_result['s3_uri']
        result['recording_file'] = file_name
        
        log("✓ Uploaded to: " + result['s3_uri'])
        
    CATCH error:
        result['error'] = "S3 upload failed: " + error
        log("ERROR: " + error)
    FINALLY:
        # Clean up temporary file
        IF file_exists(temp_recording):
            delete_file(temp_recording)
        END IF
    END TRY
    
    
    # ============================================================
    # Summary
    # ============================================================
    log("===== PROCESSING COMPLETE =====")
    log("Task ID: " + task_id)
    log("File: " + result['recording_file'])
    log("S3 Location: " + result['s3_uri'])
    
    IF result['error'] IS NULL:
        log("Status: ✓ SUCCESS")
    ELSE:
        log("Status: ✗ FAILED - " + result['error'])
    END IF
    
    RETURN result
END FUNCTION
```

### Pseudo Code: Batch Processing Multiple Recordings

```python
FUNCTION process_multiple_recordings(days_back, config):
    """
    Process multiple recordings from a time period
    
    Steps:
    1. Fetch all tasks from Webex
    2. Loop through each task and process its recording
    """
    log("===== BATCH PROCESSING: LAST " + days_back + " DAYS =====")
    
    # Initialize
    config, tokens = initialize_authentication()
    
    results = {
        'total_found': 0,
        'processed': [],
        'failed': []
    }
    
    
    # ============================================================
    # STEP 1: Fetch Tasks from Webex
    # ============================================================
    log("Step 1: Calling Webex API to fetch tasks...")
    
    TRY:
        time_range = {
            'from_time': NULL,  # Will use days_back
            'to_time': NULL,
            'days_back': days_back
        }
        
        tasks_data = get_tasks(config, tokens, time_range)
        tasks = tasks_data['tasks']
        results['total_found'] = len(tasks)
        
        log("✓ Found " + len(tasks) + " tasks")
        
        IF len(tasks) == 0:
            log("No tasks to process")
            RETURN results
        END IF
        
    CATCH error:
        log("ERROR: Failed to fetch tasks - " + error)
        RETURN results
    END TRY
    
    
    # ============================================================
    # STEP 2: Process Each Task
    # ============================================================
    log("Step 2: Processing recordings...")
    
    FOR i = 1 TO len(tasks):
        task = tasks[i]
        task_id = task['task_id']
        
        log("--- [" + i + "/" + len(tasks) + "] Task: " + task_id + " ---")
        
        TRY:
            # Process this recording
            result = process_single_recording(task_id, config)
            
            IF result['error'] IS NULL:
                results['processed'].append({
                    'task_id': task_id,
                    's3_uri': result['s3_uri']
                })
                log("✓ Success")
            ELSE:
                results['failed'].append({
                    'task_id': task_id,
                    'error': result['error']
                })
                log("✗ Failed: " + result['error'])
            END IF
            
        CATCH error:
            results['failed'].append({
                'task_id': task_id,
                'error': str(error)
            })
            log("✗ Failed: " + error)
        END TRY
    END FOR
    
    
    # ============================================================
    # Summary
    # ============================================================
    log("===== BATCH PROCESSING COMPLETE =====")
    log("Total Tasks: " + results['total_found'])
    log("Processed: ✓ " + len(results['processed']))
    log("Failed: ✗ " + len(results['failed']))
    
    RETURN results
END FUNCTION
```

---

## Quick Reference

### Webex API Endpoints

| API | Method | Endpoint | Authentication | Purpose |
|-----|--------|----------|----------------|---------|
| **Token Refresh** | POST | `https://webexapis.com/v1/access_token` | Client credentials | Get new access token |
| **Get Tasks** | GET | `https://api.wxcc-us1.cisco.com/v1/tasks` | Bearer token | List calls/tasks |
| **Get Recording** | POST | `https://api.wxcc-us1.cisco.com/v1/captures/query` | Bearer token | Get recording URL |
| **Download File** | GET | Pre-signed URL | NONE | Download recording |

### Example cURL Commands

```bash
# 1. Refresh Access Token
curl -X POST "https://webexapis.com/v1/access_token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "refresh_token=YOUR_REFRESH_TOKEN"

# 2. Get Tasks (last 7 days)
curl -X GET "https://api.wxcc-us1.cisco.com/v1/tasks?from=1736174400000&orgId=YOUR_ORG_ID&channelType=telephony" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Accept: application/json"

# 3. Get Recording URL
curl -X POST "https://api.wxcc-us1.cisco.com/v1/captures/query" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": {"taskIds": ["task-id-here"]}}'

# 4. Download Recording (NO Authorization header!)
curl -X GET "https://storage.webex.com/...pre-signed-url..." \
  -o recording.wav
```

### S3 Storage Pattern

```
s3://your-bucket/
└── call-detail/
    ├── task-abc123/
    │   └── recording.wav
    ├── task-def456/
    │   └── recording.mp3
    └── task-ghi789/
        └── recording.wav
```

### AWS Services Required

| Service | Purpose |
|---------|---------|
| **AWS Secrets Manager** | Store Webex credentials and tokens |
| **Amazon S3** | Store downloaded call recordings |

---

## End of Document
