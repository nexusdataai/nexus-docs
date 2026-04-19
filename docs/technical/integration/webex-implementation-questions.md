# Questions for Cisco Webex Team - Enterprise Implementation

## Context
We are implementing call recording retrieval from Webex Contact Center for enterprise-scale deployment. Based on your guidelines, we have questions regarding API usage, filtering, authentication, and best practices.

---

## Current Understanding

Based on the Webex team's guidelines:
1. Create API client with OAuth2/Bearer token authentication
2. Use **Captures API (List Captures)** to query recordings with filters
3. Receive pre-signed S3 URLs in API response
4. Download recordings directly using pre-signed URLs

**Reference**: https://developer.webex.com/webex-contact-center/docs/api/v1/captures/list-captures

---

## Questions


### 1. Filtering and Querying Recordings

**Question 1.1**: Organization-level filtering

We have a understanding that customer webex cc instance is a multi-tenant instance that does call cater calls of multiple Business Units. Our implementation needs to query recordings for specific business unit / organization.

**Questions**:
What is the best way we can filter - 
a. Filter at tasks api level b. Filter at Captur Api Level 


**Question 1.2**: Time-range filtering

**Questions**:
- What are the time range parameters supported by the Captures API?
  - `from` and `to` (milliseconds epoch)?
  - `startTime` and `endTime`?
  - Date format expectations?
- What is the maximum time range we can query in a single API call?
  - Can we query 7 days? 30 days? 90 days?
- Is there a pagination mechanism for large result sets?
  - `pageSize` and `pageToken` parameters?
  - Maximum results per page?

---

**Question 1.3**: Metadata-based filtering

Your guidelines mention "metadata" as a filter option.

**Questions**:
- What metadata fields are available for filtering recordings?
  - Queue name/ID?
  - Agent name/ID?
  - Call direction (inbound/outbound)?
  - Call status (ended, abandoned, transferred)?
  - Customer phone number?
  - Call duration?
- How do we specify metadata filters in the API request?
- Example query with metadata filters?

```json
// Example - is this correct?
{
  "query": {
    "orgId": "org-id",
    "timeRange": {
      "from": 1736174400000,
      "to": 1736260800000
    },
    "metadata": {
      "queueId": "queue-id",
      "direction": "inbound",
      "status": "ended"
    }
  }
}
```

**Question 1.4**: Recording availability

**Questions**:
- Are recordings available immediately after a call ends?
- Is there a delay/processing time before recordings are queryable?
- How long are recordings retained in Webex storage?
- Are there any calls that don't have recordings (e.g., abandoned calls, short calls)?

---

### 2. API Response Structure

**Question 2.1**: Multiple recordings per call

**Questions**:
- Can a single call/task have multiple recordings?
  - Separate channels (agent vs customer)?
  - Call transfers resulting in multiple segments?
- How are multiple recordings represented in the API response?
- Do we get separate pre-signed URLs for each recording?

---

### 3. Pre-Signed S3 URLs

**Question 3.1**: URL validity and expiration

**Questions**:
- How long are pre-signed S3 URLs valid?
  - 1 hour? 2 hours? 24 hours?
- What happens if we try to use an expired URL?
- Can we request a new pre-signed URL for the same recording?
- Is there a way to extend the validity period?

---

**Question 3.2**: Download behavior

**Questions**:
- Do we need to send any authentication headers when downloading from pre-signed URLs?
  - We assume NO authentication headers - is this correct?
- Are there any rate limits on downloads?
- Can the same pre-signed URL be used multiple times?
- What HTTP status codes should we handle?
  - 200 OK (success)
  - 403 Forbidden (expired URL?)
  - 404 Not Found (recording deleted?)

---

### 4. Authentication and Token Management (Enterprise Scale)

**Question 4.1**: OAuth2 token lifecycle

**Questions**:
- What is the access token expiration time?
  - Currently we see 1209599 seconds (~14 days) - is this standard?
- What is the refresh token expiration time?
  - Currently we see 7775999 seconds (~90 days) - is this standard?
- Can we refresh tokens indefinitely, or do we need to re-authenticate periodically?
- Best practice for token refresh:
  - Refresh proactively before expiration?
  - How much buffer time do you recommend (5 minutes, 10 minutes)?

---

**Question 4.2**: Token refresh rate limits

For enterprise deployment, we may be making frequent API calls.

**Questions**:
- Are there rate limits on token refresh API calls?
- If tokens are refreshed too frequently, are there penalties?
- Should we implement token caching across multiple application instances?
- Recommended token refresh strategy for high-volume scenarios?

---

**Question 4.3**: Service account vs user account

**Questions**:
- Should we use a dedicated service account for API integration?
- Are there different permission requirements for service accounts vs user accounts?
- What is the recommended OAuth flow for automated/unattended systems?
  - Client Credentials flow?
  - Authorization Code flow with refresh tokens?
- Do we need a "Compliance Officer" role for accessing recordings (as mentioned in setup docs)?

---

**Question 4.4**: Multi-tenant/Multi-organization scenarios

For serving multiple organizations:

**Questions**:
- Do we need separate API clients (client_id/secret) for each organization?
- Can a single API client access recordings across multiple organizations?
- How do we handle token management for multi-tenant scenarios?
- Are there any shared authentication mechanisms or do we maintain separate credentials per org?

---

### 5. API Rate Limits and Quotas

**Question 5.1**: API rate limits

**Questions**:
- What are the rate limits for the Captures API?
  - Requests per second/minute/hour?
  - Different limits for different endpoints?
- What HTTP status code is returned when rate limit is exceeded?
  - 429 Too Many Requests?
- Are there any headers indicating remaining quota?
  - `X-RateLimit-Remaining`?
  - `Retry-After`?

---

**Question 5.2**: Bulk retrieval best practices

For processing hundreds or thousands of recordings:

**Questions**:
- What is the recommended batch size when querying recordings?
- Should we implement exponential backoff for retries?
- Are there any best practices for bulk downloading?
  - Sequential vs parallel downloads?
  - Recommended concurrency level?

---

### 6. Error Handling and Edge Cases

**Question 6.1**: Common error scenarios

**Questions**:
- What error codes should we handle?
  - 401 Unauthorized (token expired?)
  - 403 Forbidden (insufficient permissions?)
  - 404 Not Found (recording not available?)
  - 429 Too Many Requests (rate limit?)
  - 500 Internal Server Error?
- How should we differentiate between:
  - Recording not yet available (still processing)?
  - Recording never existed (call not recorded)?
  - Recording deleted/expired?

---

**Question 6.2**: Retry logic

**Questions**:
- Which errors are retryable (transient failures)?
- Which errors are permanent and should not be retried?
- Recommended retry strategy (max attempts, backoff time)?

---

### 7. Recording Metadata and Task Details

**Question 7.1**: Relationship between Tasks and Captures

**Questions**:
- Do we still need to call `/v1/tasks` endpoint first, or can we query recordings directly?
- If we query recordings directly, do we get task/call metadata in the response?
- Is `taskId` the primary identifier for correlating recordings with call details?

---

**Question 7.2**: Additional metadata

**Questions**:
- What additional metadata is available in the Captures API response?
  - ANI (Automatic Number Identification)?
  - DNIS (Dialed Number Identification Service)?
  - IVR path/selections?
  - Call disposition codes?
  - Custom metadata/variables set during the call?
- Can we access CAD (Computer-Aided Dispatch) variables via API?

---


### 8. Testing and Sandbox Environment

**Question 8.1**: Testing environment

**Questions**:
- Is there a sandbox/test environment for development?
- Can we generate test recordings without making actual calls?
- Are there mock/simulator APIs for testing integration before going live?

