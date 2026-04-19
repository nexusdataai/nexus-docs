# Customer Setup Steps for Webex Contact Center Integration

## What You Need to Do

Follow these steps to set up the Webex integration for accessing your Contact Center recordings.

---

## Step 1: Create Integration App in Webex Developer Portal

1. **Go to**: https://developer.webex.com/
2. **Sign in** with your Webex account
3. **Click**: "My Webex Apps" in the top navigation
4. **Click**: "Create a New App"
5. **Select**: "Integration" as the app type
6. **Fill in**:
   - **App Name**: `Contact Center Recording Integration`
   - **App Description**: `Integration for accessing Contact Center recordings and task data`
7. **Click**: "Create App"

—
Note : Please note that the user should have a compliance officer role so that he has the access to all the recorded media files.

## Step 2: Configure OAuth Settings

1. **In your new app**, go to the "OAuth Settings" section
2. **Set Redirect URI**: `https://trilogy.com`
3. **Add these scopes** (copy and paste exactly):
   ```
   spark-admin:recordings_read
   spark-admin:recordings_write
   spark:kms
   cjp:config
   cjp:config_read
   ```
4. **Save** the OAuth settings

---

## Step 3: Get Your Credentials

1. **Copy your Client ID** from the app details page
2. **Copy your Client Secret** from the app details page
3. **Save both** - you'll need them for the next step

---

## Step 4: Get Your Organization ID

1. **Log into** your Webex Contact Center Admin portal
2. **Go to**: Administration → Organization Settings
3. **Copy your Organization ID** (looks like: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

---

## Step 5: Generate Access Tokens

1. **Create this URL** (replace YOUR_CLIENT_ID with your actual Client ID):
   ```
   https://webexapis.com/v1/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=https%3A%2F%2Ftrilogy.com&scope=spark-admin%3Arecordings_read%20spark-admin%3Arecordings_write%20spark%3Akms%20cjp%3Aconfig%20cjp%3Aconfig_read&state=set_state_here
   ```

2. **Open the URL** in your web browser
3. **Sign in** with your Webex account
4. **Grant permissions** to the integration
5. **Copy the authorization code** from the redirect URL (it will be in the URL parameters)

---

## Step 6: Exchange Code for Tokens

1. **Use a tool like Postman, curl, or any HTTP client**
2. **Make a POST request** to: `https://webexapis.com/v1/access_token`
3. **Set headers**:
   ```
   Content-Type: application/x-www-form-urlencoded
   ```
4. **Set body** (replace with your actual values):
   ```
   grant_type=authorization_code
   &client_id=YOUR_CLIENT_ID
   &client_secret=YOUR_CLIENT_SECRET
   &code=AUTHORIZATION_CODE
   &redirect_uri=https://trilogy.com
   ```
Example Curl -

curl -X POST https://webexapis.com/v1/access_token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "client_id=C5373f3b452d9a15d544c160ca7a3827e1d74eeefd7949e312383fedbd6c8005d" \
  -d "client_secret=838e9dcb904ec1df0b6343e44c64881d84e8746633a0b953f0b742dbbd85d91e" \
  -d "code=NTQ5MTFmMDgtOWEzYy00MWE0LWE1OWEtYmZjZTFkYmQxMTQwYTk1MWExMDMtNDBh_P0A1_5bd961a5-2622-453a-a5b3-6eb512ddb289" \
  -d "redirect_uri=https://trilogy.com"



5. **Copy the response** - you'll get something like:
   ```json
   {
     "access_token": "NzFhMTg4MTUtMTIxMS00MWQ1LWI4YTQtY2IyYTljZWUzMGQyYjEyMDEwOTQtYmM3_P0A1_5bd961a5-2622-453a-a5b3-6eb512ddb289",
     "refresh_token": "MmJhYzRjN2MtYTZlMS00N2ExLWFjMzUtZjBjMzZjMjc4NmJhZDdjOGU2ZGMtMTdl_P0A1_5bd961a5-2622-453a-a5b3-6eb512ddb289",
     "expires_in": 1209599,
     "refresh_token_expires_in": 7775999,
     "token_type": "Bearer",
     "scope": "spark-admin:recordings_write spark:kms cjp:config spark-admin:recordings_read cjp:config_read"
   }
   ```

---

## Step 7: Send Us Your Credentials

**Email us** the following information:

### Required Credentials:
```
Client ID: [your_client_id]
Client Secret: [your_client_secret]
Organization ID: [your_organization_id]
Access Token: [your_access_token]
Refresh Token: [your_refresh_token]
```

### Example:
```
Client ID: Cfb322fa73edfbefd1121e93d87ecbf8eab8e582ee6b279c668d13de451323443
Client Secret: 2535aa118d0d2d56b6c6b9bdc8c02a737727541c87a37367e5b6f592218287bb
Organization ID: 5bd961a5-2622-453a-a5b3-6eb512ddb289
Access Token: NzFhMTg4MTUtMTIxMS00MWQ1LWI4YTQtY2IyYTljZWUzMGQyYjEyMDEwOTQtYmM3_P0A1_5bd961a5-2622-453a-a5b3-6eb512ddb289
Refresh Token: MmJhYzRjN2MtYTZlMS00N2ExLWFjMzUtZjBjMzZjMjc4NmJhZDdjOGU2ZGMtMTdl_P0A1_5bd961a5-2622-453a-a5b3-6eb512ddb289
```

---

## What This Integration Will Do

Once set up, the integration will:
- ✅ Access your Contact Center recordings
- ✅ Download call audio files
- ✅ Get call details and metadata
- ✅ Process recordings for analysis
- ✅ Upload to secure cloud storage

## Security Notes

- 🔒 **Minimal Access**: Only 5 required permissions (not 50+)
- 🔒 **Secure Tokens**: Automatically refreshed and stored securely
- 🔒 **Limited Scope**: Only accesses recording and task data
- 🔒 **No Admin Rights**: Cannot modify your Contact Center settings

---

**We'll help you complete the setup!** 

## Some test curl commands

curl -X GET "https://api.wxcc-us1.cisco.com/v1/tasks?from=TO_TIMESTAMP&to=FROM_TIMESTAMP&orgId=YOUR_ORG_ID&channelType=telephony" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"


curl -L --request GET \
--url https://api.wxcc-us1.cisco.com/v1/tasks?from=1753315200000 \
--header 'Authorization: Bearer NDBiNjlhYzEtZjQzZS00ZGU4LTlhODUtMjY0YjNjZDNhNjFhYjg0MjliMDctMWM1_P0A1_5bd961a5-2622-453a-a5b3-6eb512ddb289' \
--header 'Accept: application/json'

curl -L --request POST \
--url https://api.wxcc-us1.cisco.com/v1/captures/query \
--header 'Authorization: Bearer NDBiNjlhYzEtZjQzZS00ZGU4LTlhODUtMjY0YjNjZDNhNjFhYjg0MjliMDctMWM1_P0A1_5bd961a5-2622-453a-a5b3-6eb512ddb289' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--data '{ "query": { "taskIds": ["99a53828-6a11-4bee-a257-8730a56963ce"] } }'

curl -L --request POST \
--url https://api.wxcc-us1.cisco.com/v1/captures/query \
--header 'Authorization: Bearer NDBiNjlhYzEtZjQzZS00ZGU4LTlhODUtMjY0YjNjZDNhNjFhYjg0MjliMDctMWM1_P0A1_5bd961a5-2622-453a-a5b3-6eb512ddb289' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--data '{ "query": { "taskIds": ["d61cb7a9-98ab-4142-b8f7-89a7e1b9379d"] } }'

