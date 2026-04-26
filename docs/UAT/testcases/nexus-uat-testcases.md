# NexusAI - User Acceptance Testing (UAT) Test Cases

**Project:** NexusAI Enterprise Analytics  
**SOW Reference:** Skyvera, LLC / NexusAI Ltd - Quote# T69449 (Signed 18-Dec-2025)  
**Test Plan Version:** 1.0  
**Document Date:** March 11, 2026  
**Prepared By:** Skyvera Delivery Team

---

## 1. Overview

This document defines the User Acceptance Testing (UAT) test cases for the NexusAI platform delivered under the NexusAI Platform SOW. Test cases are organized by SOW feature category and map directly to the deliverables defined in SOW Section 4 ("In Scope Capabilities") and the detailed dashboard functionality tables (SOW pages 9-14).

**Descoped Items:**

- **B-2 Lead Conversion** — Descoped per CR-001. NexusAI creates Leads only; Lead-to-Opportunity conversion remains a manual action by NexusAI Sales team.

**Out of Scope (Future Phases):**

- Product Recommendations Engine (SOW Section 5)
- Automatic Quote Generation (SOW Section 5)
- Office 365 Integration & Email Analysis (SOW Section 5)
- WhatsApp Integration (SOW Section 5)

---

## 2. Prerequisites

| Requirement | Details |
|-------------|---------|
| Application Access | NexusAI web application on NexusAI-branded domain |
| User Accounts | One account per role: Admin, Executive, SalesManager, Rep |
| Webex Integration | Active connection to Webex Contact Center (Production instance) with real or test call recordings |
| Salesforce Access | Salesforce sandbox with valid credentials; Lead object and ContentVersion permissions |
| CloudSense (Axway) | Active Axway API gateway connection to CloudSense CPQ catalog |
| Browser | Chrome or Edge (latest version) |
| Network | Internet access to AWS Singapore region hosting environment |
| Test Data | Minimum 5 analyzed calls with varying outcomes (leads created, leads failed, different sentiment scores, different products discussed) |

---

## 3. Test Scope

### 3.1 (A) Call Monitoring and AI Processing

SOW Reference: Page 15

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| A-1.1 | Continuous Webex Monitoring | 1. Complete a call in Webex Contact Center. 2. Wait up to 10 minutes. 3. Open NexusAI Call Analysis dashboard. | New call appears in the call list within 10 minutes of call end | |
| A-1.2 | Webhook Trigger | 1. Complete a call in Webex. 2. Check Operations page for call processing activity. | Webhook triggers call processing pipeline automatically | |
| A-2.1 | Call Metadata Retrieval | 1. Locate a newly processed call in Call Analysis. 2. Open the call detail. | Call metadata displayed: agent name, customer company, call date/time, duration, call type | |
| A-2.2 | Audio Recording Available | 1. Open a processed call detail. 2. Navigate to the Recording/Audio tab. | Audio recording is available for playback with play/pause/volume controls | |
| A-3.1 | Audio-to-Transcript Conversion | 1. Open a processed call detail. 2. Navigate to the Transcript tab. | Full conversation transcript displayed with speaker identification (Agent/Customer) | |
| A-3.2 | Transcript Searchability | 1. Open a call transcript. 2. Search for a keyword mentioned during the call. | Search returns matching segments within the transcript | |
| A-4.1 | Call Analysis Generated | 1. Open a processed call detail. 2. Navigate to the Analysis tab. | AI-generated analysis available with call summary, rep performance insights, and deal analysis | |
| A-5.1 | Sentiment Analysis | 1. Open a processed call detail. 2. Check the sentiment score. | Sentiment score displayed (0-100%) with sentiment progression indicators | |
| A-6.1 | Intent Classification | 1. Open a processed call detail. 2. Review the analysis section. | Customer intent identified and classified (e.g., purchase inquiry, support, complaint) | |
| A-7.1 | Compliance Evaluation | 1. Open a processed call detail. 2. Check the Compliance Monitoring section. | PDPA compliance status shown with pass/fail, breach identification if applicable, professional conduct assessment, and risk level categorization | |

---

### 3.2 (B) Salesforce Lead/Opportunity Management

SOW Reference: Page 15 | Change Request: CR-001

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| B-1.1 | Lead Creation - Valid Data | 1. Process a call where Company Name, BRN, and Contact Number are mentioned. 2. Open the call detail Salesforce tab. 3. Verify in Salesforce sandbox. | New Lead created in Salesforce with Company Name, BRN, and Contact Number populated | |
| B-1.2 | Lead Creation - Data Enrichment | 1. Process a call with additional context (products discussed, customer needs). 2. Check the Lead record in Salesforce. | Lead record enriched with additional fields from call analysis (description, lead source, etc.) | |
| B-1.3 | Lead Creation - Missing Mandatory Data | 1. Process a call where BRN or Company Name is NOT mentioned. 2. Check Lead Failures dashboard. | No Lead created; exception logged with Call ID, available captured data, and reason for failure | |
| B-1.4 | Lead Failure Exception Report | 1. Navigate to Lead Creation Failure Report dashboard. 2. Review the failure list. | Failures displayed with: Call ID/Task ID, available captured data, reason for failure, date, agent | |
| B-1.5 | Lead Failure - Resolve Action | 1. Open Lead Failures dashboard. 2. Click Resolve on a failure entry. | Failure marked as resolved; status updated in the list | |
| B-1.6 | Lead Failure - Export | 1. Open Lead Failures dashboard. 2. Export the failure report. | CSV report downloaded with all failure records | |
| B-3.1 | Call Transcript Attachment | 1. Process a call that creates a Lead. 2. Check the Lead record in Salesforce. | Call summary/transcript attached to the Lead record as a ContentVersion document | |
| B-4.1 | Automated Action Recommendations | 1. Open a processed call detail in Call Analysis. 2. Review the next steps section. | Next steps and follow-up recommendations displayed based on call analysis | |

---

### 3.3 (C) Intelligent Product Identification

SOW Reference: Page 15

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| C-1.1 | AI Product Identification | 1. Process a call where specific products are discussed. 2. Open the call detail or Deal Analysis for this call. | Products discussed during the call are automatically identified and listed | |
| C-2.1 | Product Details Capture | 1. Open the Deal Analysis for a call with product discussions. 2. Review the product details section. | Product names, types, bandwidth requirements, contract lengths, and estimated costs captured | |
| C-3.1 | Product Feature Extraction | 1. Process a call where specific product features are mentioned (e.g., bandwidth, SLA). 2. Review the product details. | Product features automatically extracted and categorized from the call transcript | |
| C-4.1 | CloudSense Product Code Matching | 1. Process a call mentioning a product available in CloudSense catalog. 2. Review the product details in Deal Analysis. | Product matched to CloudSense catalog with accurate product codes and pricing | |
| C-4.2 | CloudSense Price Retrieval | 1. Open a deal with matched products. 2. Verify pricing against CloudSense catalog. | Product pricing (recurring and one-off) retrieved from CloudSense matches catalog values | |
| C-5.1 | Customer Interest Scoring | 1. Open a processed call in Deal Analysis. 2. Check the interest scoring for identified products. | Customer interest level scored and displayed (High/Medium/Low) based on sentiment and engagement | |
| C-6.1 | Cross-sell/Upsell Identification | 1. Process a call where the customer expresses interest in multiple products or additional services. 2. Review the deal details. | Cross-sell and/or upsell opportunities identified and flagged in the deal analysis | |

---

### 3.4 (D) Deal Value Identification & Revenue Analysis

SOW Reference: Pages 15-16

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| D-1.1 | Automatic Deal Value Calculation | 1. Process a call with identifiable products. 2. Open the Deal Analysis for this call. | Deal value automatically calculated: (number of products) x (CloudSense price) x (contract duration) | |
| D-1.2 | Deal Value Accuracy | 1. Compare the calculated deal value against manually computed value using CloudSense prices. | Calculated deal value matches expected value based on product prices and contract terms | |
| D-2.1 | Salesforce Value Synchronization | 1. Update a deal value in Salesforce. 2. Refresh the NexusAI dashboard. | Updated value from Salesforce reflected in the NexusAI UI | |
| D-3.1 | Total Pipeline Value | 1. Open Executive Summary or Deal Analysis dashboard. 2. Check the pipeline value KPI. | Total pipeline value aggregated across all active deals and displayed correctly | |
| D-4.1 | Coaching ROI Potential | 1. Open Executive Summary dashboard. 2. Check the Coaching ROI Potential card. | Coaching ROI potential calculation displayed based on rep performance data | |
| D-5.1 | Monthly Revenue Projection | 1. Open Executive Summary dashboard. 2. Check the Monthly Revenue Projection card. | Monthly revenue projected based on current pipeline and deal probabilities | |
| D-6.1 | Revenue Increase Potential | 1. Open Rep Performance dashboard. 2. Review coaching section. | Revenue increase potential via coaching identified and displayed | |
| D-7.1 | Revenue at Risk | 1. Open Executive Summary or Deal Analysis dashboard. 2. Check the Revenue at Risk metric. | Deals at risk identified and revenue at risk amount calculated and displayed | |
| D-8.1 | High Probability Revenue | 1. Open Executive Summary dashboard. 2. Check High Probability Deals card. | Deals with >70% probability counted and their total value displayed | |

---

### 3.5 (E) Call Storage & Data Management

SOW Reference: Pages 5-6, 16

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| E-1.1 | Secure Call Storage | 1. Process a call. 2. Verify S3 bucket contents for the call. | Per-call outputs stored in S3: transcript, analysis metadata, Salesforce action records | |
| E-2.1 | Data Organization | 1. Check S3 bucket structure for multiple calls across different dates. | Call data organized by call ID and date in S3 path: `call-detail/{task_id}/` | |
| E-3.1 | Data Retention - Online Access | 1. Access a call processed within the last 6 months. 2. Open call details. | Call data fully accessible and available online within the 6-month window | |
| E-4.1 | Data Residency Compliance | 1. Verify the AWS region of the S3 bucket and application infrastructure. | All data stored in AWS Singapore region (ap-southeast-1) within NexusAI's jurisdiction | |

---

### 3.6 (F) Executive Summary Dashboard

SOW Reference: Pages 8-9

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| F-1.1 | Filter by Representative | 1. Open Executive Summary dashboard. 2. Select a specific representative from the filter dropdown. | Dashboard metrics update to show data only for the selected representative | |
| F-1.2 | Filter by Representative - All | 1. Open Executive Summary dashboard. 2. Clear the representative filter (select All). | Dashboard metrics show aggregated data for all representatives | |
| F-2.1 | Filter by Date Range - Presets | 1. Open Executive Summary dashboard. 2. Select "Last 7 days", "Last 30 days", "Last 90 days" presets. | Dashboard metrics update to reflect the selected date range for each preset | |
| F-2.2 | Filter by Date Range - Custom | 1. Open Executive Summary dashboard. 2. Select custom date range with specific start and end dates. | Dashboard metrics update to reflect only calls within the custom date range | |
| F-3.1 | Deal Count Display | 1. Open Executive Summary dashboard. 2. Observe deal count metrics. | Deal count displayed and updates correctly when filters are applied | |
| F-4.1 | Overall QA Score | 1. Open Executive Summary dashboard. 2. Check the Overall QA Score metric. | Weighted QA score displayed with correct calculation across all analyzed calls | |
| F-5.1 | Compliance Rate | 1. Open Executive Summary dashboard. 2. Check the Compliance Rate metric. | Percentage of compliant calls displayed accurately | |
| F-6.1 | Total Revenue Impact | 1. Open Executive Summary dashboard. 2. Check the Total Revenue Impact metric. | Total revenue impact calculation displayed | |
| F-7.1 | Qualifying Questions Rate | 1. Open Executive Summary dashboard. 2. Check the Qualifying Questions success rate. | Success rate of qualifying questions asked across calls displayed as a percentage | |
| F-8.1 | Real-time Metric Updates | 1. Open Executive Summary dashboard. 2. Change the representative filter. 3. Change the date range. | All metrics, charts, and sections update immediately based on applied filters | |
| F-9.1 | High Probability Deals KPI | 1. Open Executive Summary dashboard. 2. Check the High Probability Deals card. | Total value of deals with >70% probability displayed | |
| F-10.1 | Monthly Revenue Projection KPI | 1. Open Executive Summary dashboard. 2. Check the Monthly Revenue Projection card. | Projected monthly revenue displayed | |
| F-11.1 | Coaching ROI Potential KPI | 1. Open Executive Summary dashboard. 2. Check the Coaching ROI Potential card. | Coaching ROI potential value displayed | |
| F-12.1 | Deals at Risk KPI | 1. Open Executive Summary dashboard. 2. Check the Deals at Risk card. | Number and value of at-risk deals displayed | |
| F-13.1 | Performance by QA Category | 1. Open Executive Summary dashboard. 2. Locate the Performance by QA Category section. | Bar chart displayed showing average scores across QA categories with interactive tooltips | |
| F-14.1 | Rep Score Distribution | 1. Open Executive Summary dashboard. 2. Locate the Rep Score Distribution section. | Visualization showing agent performance spread with individual agent scores and rankings | |
| F-15.1 | Top Performers Section | 1. Open Executive Summary dashboard. 2. Locate the Top Performers section. | Top 3 performers displayed with individual performance metrics and call count | |
| F-16.1 | Top Deals Section | 1. Open Executive Summary dashboard. 2. Locate the Top Deals section. | Highest value opportunities displayed with deal ranking, status indicators, and probabilities | |
| F-17.1 | Recent Alerts Section | 1. Open Executive Summary dashboard. 2. Locate the Recent Alerts section. | Quality issues displayed with alert categorization by type, priority level indicators (High/Medium/Low), related agent identification, and recommendations | |
| F-17.2 | Alert Priority Indicators | 1. Open Executive Summary dashboard. 2. Check alert priority colors. | Alerts color-coded by priority: High, Medium, Low with distinct visual indicators | |

---

### 3.7 (G) Call Analysis Dashboard

SOW Reference: Pages 10-11

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| G-1.1 | Search by Company Name | 1. Open Call Analysis dashboard. 2. Enter a company name in the search field. | Call list filters to show only calls matching the company name | |
| G-1.2 | Search by Agent Name | 1. Open Call Analysis dashboard. 2. Enter an agent name in the search field. | Call list filters to show only calls matching the agent name | |
| G-1.3 | Search by Call ID | 1. Open Call Analysis dashboard. 2. Enter a call ID in the search field. | Call list filters to the specific call matching the ID | |
| G-2.1 | Filter by Representative | 1. Open Call Analysis dashboard. 2. Select a representative from the filter. | Call list shows only calls for the selected representative | |
| G-2.2 | Filter by Date Range | 1. Open Call Analysis dashboard. 2. Select a date range (preset or custom). | Call list shows only calls within the selected date range | |
| G-3.1 | Sort by Call Date | 1. Open Call Analysis dashboard. 2. Sort by call date (ascending/descending). | Call list reorders by call date in the selected direction | |
| G-3.2 | Sort by Duration | 1. Open Call Analysis dashboard. 2. Sort by duration. | Call list reorders by call duration | |
| G-3.3 | Sort by QA Score | 1. Open Call Analysis dashboard. 2. Sort by QA score. | Call list reorders by QA score | |
| G-4.1 | Real-time Search | 1. Open Call Analysis dashboard. 2. Begin typing in the search field. | Call list filters instantly as characters are typed | |
| G-5.1 | Call Overview Cards | 1. Open Call Analysis dashboard. 2. Review the overview cards at the top. | Cards display: total calls analyzed, overall team score (weighted), average call duration, compliance rate percentage, revenue at risk | |
| G-6.1 | Call Metadata Display | 1. Open a call detail from the call list. | Call metadata displayed: agent name, customer company, call duration, call type classification | |
| G-7.1 | QA Score with Pass/Fail | 1. Open a call detail. 2. Check the QA score. | Overall QA score displayed with clear pass/fail status indicator | |
| G-8.1 | Customer Sentiment Score | 1. Open a call detail. 2. Check the sentiment section. | Sentiment analysis score displayed (0-100%) with customer satisfaction rating | |
| G-8.2 | Sentiment Progression | 1. Open a call detail. 2. Review the sentiment progression view. | Sentiment progression throughout the call displayed with key sentiment moments identified | |
| G-9.1 | PDPA Compliance Assessment | 1. Open a call detail. 2. Check the compliance section. | PDPA compliance assessment displayed with pass/fail status | |
| G-10.1 | QA Scoring Breakdown | 1. Open a call detail. 2. Navigate to the QA scoring section. | Detailed element-by-element scoring shown: weight-based calculation, pass/fail logic per element, evidence documentation, color indicators for performance levels | |
| G-11.1 | Compliance Monitoring Detail | 1. Open a call detail. 2. Navigate to the compliance section. | PDPA status, breach identification and listing, professional conduct assessment, risk level categorization all displayed | |
| G-12.1 | Qualifying Questions | 1. Open a call detail. 2. Navigate to the qualifying questions section. | Questions asked successfully shown with answers, missed questions identified, success rate calculated, questions categorized by type | |
| G-13.1 | Call Metrics | 1. Open a call detail. 2. Navigate to the call metrics section. | Metrics displayed: talk-to-listen ratio, customer interruption count, speaking pace (WPM), energy level measurement, voice clarity assessment | |
| G-14.1 | Call Transcript Display | 1. Open a call detail. 2. Navigate to the Transcript tab. | Full conversation transcript displayed with speaker identification (Agent/Customer) and searchable content | |
| G-15.1 | Call Diarization | 1. Open a call detail. 2. Navigate to the diarization view. | Visual timeline of conversation displayed with speaker identification, segment highlighting, and audio navigation controls | |
| G-16.1 | Salesforce Integration Display | 1. Open a call detail. 2. Navigate to the Salesforce tab. | Lead creation validation shown, contact information verification, BRN validation status, automated action recommendations displayed | |
| G-17.1 | Audio Playback | 1. Open a call detail. 2. Navigate to the recording section. 3. Click Play. | Call recording plays with controls: Play, Pause, Volume. Time-based navigation available. Recording availability status shown. | |
| G-17.2 | Audio Navigation | 1. During audio playback, use the time-based navigation controls. | Audio jumps to the selected time position accurately | |
| G-18.1 | Call Report Generation | 1. Open a call detail. 2. Click the Report/PDF generation button. | Comprehensive PDF report generated containing: performance metrics, coaching recommendations, actionable insights summary | |

---

### 3.8 (H) Rep Performance Dashboard

SOW Reference: Pages 12-13

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| H-1.1 | Overview - Team Average Score | 1. Open Rep Performance dashboard. 2. Check the Overview section. | Team average score displayed with weighted calculation | |
| H-1.2 | Overview - Top Performer | 1. Open Rep Performance dashboard. 2. Check the top performer identification. | Top performing agent identified with their score and key metrics | |
| H-1.3 | Overview - Revenue Pipeline | 1. Open Rep Performance dashboard. 2. Check the revenue pipeline value. | Total revenue pipeline value displayed | |
| H-1.4 | Overview - Compliance Percentage | 1. Open Rep Performance dashboard. 2. Check team compliance. | Team compliance percentage displayed | |
| H-1.5 | Overview - Rep Scorecards | 1. Open Rep Performance dashboard. 2. Review rep scorecards. | Individual rep scorecards displayed with performance indicators | |
| H-1.6 | Overview - Performance Comparison Charts | 1. Open Rep Performance dashboard. 2. Check comparison charts. | Performance comparison charts (bar/line) displayed across reps | |
| H-1.7 | Overview - Skills Radar | 1. Open Rep Performance dashboard. 2. Check the team skills radar chart. | Radar chart displayed showing team skills across QA categories | |
| H-1.8 | Overview - Revenue Distribution | 1. Open Rep Performance dashboard. 2. Check revenue distribution. | Revenue distribution by agent displayed | |
| H-1.9 | Overview - Training Priorities | 1. Open Rep Performance dashboard. 2. Check training priorities section. | Training priorities identified and listed by priority level | |
| H-2.1 | Individual Rep - Personal Metrics | 1. Open Rep Performance dashboard. 2. Select an individual representative. | Detailed personal performance metrics displayed for the selected rep | |
| H-2.2 | Individual Rep - Skills Radar with Team Comparison | 1. Select an individual rep. 2. Check the skills radar chart. | Individual skills radar overlaid with team average for comparison | |
| H-2.3 | Individual Rep - Strengths and Improvements | 1. Select an individual rep. 2. Review strengths and improvement areas. | Specific strengths identified and areas for improvement listed | |
| H-2.4 | Individual Rep - Active Alerts | 1. Select an individual rep. 2. Check alerts section. | Active alerts and notifications relevant to the rep displayed | |
| H-2.5 | Individual Rep - Performance Trends | 1. Select an individual rep. 2. Check trends over time. | Performance trend line/chart displayed showing historical performance | |
| H-2.6 | Individual Rep - Revenue Contribution | 1. Select an individual rep. 2. Check revenue contribution. | Revenue contribution by the selected rep displayed | |
| H-2.7 | Individual Rep - Coaching Plan | 1. Select an individual rep. 2. Check the coaching plan section. | Personalized coaching plan displayed with development priorities for the selected rep | |
| H-3.1 | Team Comparison - Multi-metric | 1. Open Rep Performance dashboard. 2. Navigate to team comparison view. | Multi-metric agent comparison table/chart displayed with performance ranking system | |
| H-3.2 | Team Comparison - Skills Comparison | 1. Review team comparison view. 2. Check skills comparison. | Skills comparison across team members displayed with performance spread visualization | |
| H-4.1 | Skills Analysis - Team Radar | 1. Open Rep Performance dashboard. 2. Navigate to skills analysis. | Team skills radar chart displayed with individual skills breakdown | |
| H-4.2 | Skills Analysis - Gap Identification | 1. Review skills analysis section. | Skills gap identification displayed with training needs assessment | |
| H-5.1 | Performance Trends - Team | 1. Open Rep Performance dashboard. 2. Navigate to performance trends. | Team performance trends over time displayed with revenue trends | |
| H-5.2 | Performance Trends - Individual | 1. Select an individual rep. 2. Review performance history. | Individual performance history and improvement tracking displayed | |
| H-6.1 | Coaching & Training - Opportunities | 1. Open Rep Performance dashboard. 2. Navigate to coaching section. | Coaching opportunities identified with personalized development plans | |
| H-6.2 | Coaching & Training - Action Items | 1. Review coaching section. | Immediate action items listed with actionable feedback and implementation roadmap | |
| H-6.3 | Coaching & Training - Process Improvements | 1. Review coaching section. | Process improvements and training priorities listed by priority level | |

---

### 3.9 (I) Deal Analysis Dashboard

SOW Reference: Pages 13-14

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| I-1.1 | Deal Overview - Pipeline Value | 1. Open Deal Analysis dashboard. 2. Check the overview cards. | Total pipeline value calculation displayed | |
| I-1.2 | Deal Overview - High Probability Count | 1. Check the overview cards. | Count of high probability deals displayed | |
| I-1.3 | Deal Overview - At-Risk Deals | 1. Check the overview cards. | At-risk deals identified and counted | |
| I-1.4 | Deal Overview - Monthly Projection | 1. Check the overview cards. | Monthly revenue projection displayed | |
| I-1.5 | Deal Overview - Coaching ROI | 1. Check the overview cards. | Coaching ROI potential calculation displayed | |
| I-2.1 | Company Deal Details | 1. Open Deal Analysis dashboard. 2. Select a company/deal. | Comprehensive company information displayed: deal value, probability, agent assignment | |
| I-2.2 | Related Products | 1. Open a deal detail. 2. Check the products section. | Related products listed with interest levels, product specifications, and pricing | |
| I-2.3 | Expected Close Date | 1. Open a deal detail. 2. Check the close date. | Expected close date displayed with warnings if applicable | |
| I-3.1 | Next Steps Tracking | 1. Open a deal detail. 2. Check the next steps section. | Action items identified with follow-up requirements, timeline management, task prioritization, and progress tracking | |
| I-4.1 | Risk Assessment | 1. Open a deal detail. 2. Check the risk section. | Risk factors identified with level categorization (Low/Medium/High), risk score, and mitigation recommendations | |
| I-5.1 | Engagement Timeline | 1. Open a deal detail. 2. Check the engagement timeline. | Call history visualization with engagement tracking, performance scoring per engagement, timeline navigation, and call type categorization | |
| I-6.1 | Filter by Representative | 1. Open Deal Analysis dashboard. 2. Select a representative filter. | Deal list filters to selected representative | |
| I-6.2 | Filter by Date Range | 1. Open Deal Analysis dashboard. 2. Select a custom date range. | Deal list filters to the selected date range | |
| I-6.3 | Sort by Deal Value | 1. Open Deal Analysis dashboard. 2. Sort by deal value. | Deal list reorders by deal value (ascending/descending) | |
| I-6.4 | Sort by Probability | 1. Open Deal Analysis dashboard. 2. Sort by probability. | Deal list reorders by deal probability | |

---

### 3.10 (J) User Management & Security

SOW Reference: Pages 5, 6, 8

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| J-1.1 | RBAC - Admin Role | 1. Log in as Admin. 2. Navigate through the application. | Admin has access to: all dashboards, Settings, User Management, RBAC, System Settings, Operations | |
| J-1.2 | RBAC - Executive Role | 1. Log in as Executive. 2. Navigate through the application. | Executive has access to: Executive Summary, Call Analysis, Rep Performance, Deal Analysis, Lead Failures | |
| J-1.3 | RBAC - SalesManager Role | 1. Log in as SalesManager. 2. Navigate through the application. | SalesManager has access to: Call Analysis (team calls), Rep Performance, Deal Analysis | |
| J-1.4 | RBAC - Rep Role | 1. Log in as Rep. 2. Navigate through the application. | Rep redirected to Individual Dashboard; access limited to own calls via My Calls view | |
| J-1.5 | RBAC - Unauthorized Access | 1. Log in as Rep. 2. Attempt to navigate to Executive Summary via URL. | Access denied; user redirected to their authorized dashboard | |
| J-2.1 | SSO Login | 1. Navigate to the NexusAI application URL. 2. Use NexusAI SSO credentials to log in. | User authenticated via SSO and redirected to appropriate dashboard based on role | |
| J-2.2 | Login - Cognito Direct | 1. Navigate to login page. 2. Enter valid email and password. | User authenticated and redirected to dashboard | |
| J-2.3 | Login - Invalid Credentials | 1. Navigate to login page. 2. Enter invalid credentials. | Clear error message displayed; login denied | |
| J-2.4 | Logout | 1. Log in to the application. 2. Click Logout from user menu. | User session terminated; redirected to login page | |
| J-2.5 | MFA Setup | 1. Log in as a user without MFA. 2. Navigate to Settings > Profile. 3. Set up MFA (TOTP). | MFA successfully configured; QR code displayed for authenticator app | |
| J-2.6 | MFA Verification | 1. Log in with a user that has MFA enabled. 2. Enter TOTP code. | MFA challenge presented; valid code grants access | |
| J-2.7 | Password Change | 1. Log in to the application. 2. Navigate to Settings > Profile. 3. Change password. | Password changed successfully; user can log in with new password | |
| J-2.8 | Forced Password Change | 1. Create a new user (Admin). 2. Log in as the new user with temporary password. | User prompted to change password on first login | |
| J-3.1 | Encrypted Connection | 1. Access the NexusAI application URL. 2. Check browser security indicator. | Application served over HTTPS with valid SSL certificate | |

---

### 3.11 (K) System Integrations

SOW Reference: Pages 4, 5, 6, 13, 15, 16

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| K-1.1 | Webex Contact Center Integration | 1. Complete a call in Webex Contact Center. 2. Verify call appears in NexusAI. | Call recording and metadata (agent name, company name, call date/time) retrieved via Webex API | |
| K-1.2 | Webex Metadata Accuracy | 1. Compare call metadata in NexusAI with Webex records. | Agent name, company name, call date/time, and duration match Webex source data | |
| K-2.1 | Salesforce CRM - Lead Creation | 1. Process a call with valid mandatory data. 2. Check Salesforce sandbox. | Lead created automatically with correct field values | |
| K-2.2 | Salesforce CRM - Transcript Attachment | 1. Process a call that creates a Lead. 2. Check the Lead record in Salesforce. | Call summary attached as ContentVersion to the Lead record | |
| K-3.1 | CloudSense Product Catalog | 1. Process a call mentioning a known product. 2. Check Deal Analysis product details. | Product matched to CloudSense catalog (via Axway) with correct product codes and pricing | |
| K-4.1 | Amazon S3 Storage | 1. Process a call. 2. Verify S3 contents. | Call data (transcript, analysis, SFDC action records) stored in S3 under `call-detail/{task_id}/` | |

---

### 3.12 (L) Data Flow Architecture

SOW Reference: Page 5

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| L-1.1 | Webhook Trigger | 1. Complete a new call in Webex. 2. Monitor the call processing pipeline. | New call event triggers the processing workflow automatically | |
| L-2.1 | Webex Connector | 1. Monitor the pipeline after a new call. | Audio recording retrieved from Webex platform by the connector | |
| L-3.1 | Transcript Generation | 1. After audio retrieval, check for transcript output. | Speech-to-text conversion completes; transcript available in S3 and UI | |
| L-4.1 | Call Analysis Engine | 1. After transcript generation, check for analysis output. | AI-based analysis of transcript completes; analysis.json, product-details.json generated | |
| L-5.1 | Salesforce Connector | 1. After analysis completes, check Salesforce for CRM updates. | Salesforce Lead created/updated with call data via the Salesforce connector | |
| L-6.1 | End-to-End Pipeline Timing | 1. Record the time a call ends in Webex. 2. Monitor when results appear in the NexusAI dashboard. | Complete pipeline (call end to dashboard display) completes within 10 minutes (SOW Success Criteria #3) | |

---

### 3.13 (M) Infrastructure & Architecture

SOW Reference: Pages 5-6, 16-17

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| M-1.1 | AWS Singapore Region | 1. Verify application hosting region. | Application and data hosted in AWS Singapore region (ap-southeast-1) for data residency compliance | |
| M-2.1 | NexusAI-Branded Domain | 1. Access the application via the configured domain. | Application accessible via NexusAI-branded domain with valid SSL | |
| M-3.1 | SSO Access | 1. Access the application. 2. Authenticate via SSO. | Single sign-on works for authorized users | |
| M-5.1 | Backend Architecture | 1. Attempt to access backend API directly from public internet. | Backend not publicly accessible; reachable only over private network connectivity | |
| M-8.1 | Application Health | 1. Access the application. 2. Check health endpoints. | Application health check returns healthy status; all services operational | |

---

### 3.14 Lead Creation Failure Report (CR-001 Addendum)

SOW Reference: CR-001 Agreement

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| CR-1.1 | Failure List Display | 1. Navigate to Lead Creation Failure Report dashboard. | Failures listed with: Call ID/Task ID, available captured data, reason for failure, date, and agent | |
| CR-1.2 | Failure Metrics | 1. Open Lead Failures dashboard. 2. Check metrics section. | Summary metrics displayed: total failures, failures by error type, failures by agent | |
| CR-1.3 | Failure Filtering | 1. Open Lead Failures dashboard. 2. Apply filters (date range, status, agent, error type). | Failure list filters correctly based on applied criteria | |
| CR-1.4 | Resolve Failure | 1. Select a failure entry. 2. Click Resolve. | Failure status updated to Resolved; entry visually distinguished from unresolved | |
| CR-1.5 | Export Failure Report | 1. Open Lead Failures dashboard. 2. Click Export. | CSV file downloaded with all failure records matching current filter criteria | |
| CR-1.6 | Pagination | 1. Open Lead Failures dashboard with more than 20 failure records. 2. Navigate pages. | Pagination works correctly; 20 records per page with page navigation controls | |

---

## 4. SOW Success Criteria Verification

SOW Reference: Page 19

| Criteria ID | SOW Criteria | Test Method | Expected Result | Owner | Status |
|-------------|-------------|-------------|-----------------|-------|--------|
| SC-1 | Proven integration with NexusAI Salesforce and CloudSense platforms | Execute test cases K-2.1, K-2.2, K-3.1; verify Lead creation, transcript attachment, and product/pricing retrieval | Leads created in Salesforce with correct data; products matched with CloudSense pricing | Skyvera | |
| SC-2 | Proven integration with Webex for gathering call recordings and major call information | Execute test cases K-1.1, K-1.2; verify recording retrieval and metadata accuracy | Call recordings and metadata (agent name, company name, date/time) successfully retrieved from Webex | Joint | |
| SC-3 | New calls analyzed and results reflected to UI within 10 minutes after call ends | Execute test case L-6.1; timestamp call end and verify dashboard appearance | Call analysis results visible in NexusAI dashboard within 10 minutes of call completion | Skyvera | |
| SC-4 | Call Analysis, Representative Performance, and Deal Analysis Dashboards created with real calls | Execute test cases in sections G, H, and I using real call data | All three dashboards display data from real Webex calls with accurate analysis | Skyvera | |
| SC-5 | New leads and opportunities created correctly with available information for real calls in Salesforce | Execute test cases B-1.1, B-1.2, B-3.1; verify Salesforce records against call data | Leads created in Salesforce with all available information from real call analysis | Skyvera | |

---

## 5. Known Limitations

| Limitation | Description | SOW Reference |
|------------|-------------|---------------|
| B-2 Lead Conversion | Descoped per CR-001. Lead conversion from Lead to Opportunity remains a manual NexusAI Sales team action. | Page 15, CR-001 |
| CloudSense Catalog Coverage | NexusAI's CloudSense platform does not include all products. Product matches are limited to available catalog items. | Page 19 |
| Product Recommendations Engine | Out of scope for current phase. Available for future activation. | Page 14 (Section 5) |
| Automatic Quote Generation | Out of scope for current phase. Available for future activation. | Page 14 (Section 5) |
| Office 365 Integration | Out of scope for current phase. Available for future activation. | Pages 14-15 (Section 5) |
| WhatsApp Integration | Out of scope for current phase. Available for future activation. | Page 15 (Section 5) |

---

## 6. Test Execution Summary

| Section | Description | Total Test Cases | Passed | Failed | Blocked | Not Tested |
|---------|-------------|-----------------|--------|--------|---------|------------|
| A | Call Monitoring and AI Processing | 10 | | | | |
| B | Salesforce Lead/Opportunity Management | 8 | | | | |
| C | Intelligent Product Identification | 7 | | | | |
| D | Deal Value Identification & Revenue Analysis | 9 | | | | |
| E | Call Storage & Data Management | 4 | | | | |
| F | Executive Summary Dashboard | 20 | | | | |
| G | Call Analysis Dashboard | 25 | | | | |
| H | Rep Performance Dashboard | 25 | | | | |
| I | Deal Analysis Dashboard | 15 | | | | |
| J | User Management & Security | 14 | | | | |
| K | System Integrations | 6 | | | | |
| L | Data Flow Architecture | 6 | | | | |
| M | Infrastructure & Architecture | 5 | | | | |
| CR | Lead Creation Failure Report | 6 | | | | |
| SC | SOW Success Criteria | 5 | | | | |
| **Total** | | **165** | | | | |

---

## 7. Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Skyvera Project Lead | | | |
| NexusAI Project Lead | | | |
| NexusAI QA Lead | | | |

---
