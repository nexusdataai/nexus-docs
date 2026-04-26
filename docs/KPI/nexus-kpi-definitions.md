# NexusAI KPI Definitions

**Project:** NexusAI Enterprise Analytics  
**Document Version:** 1.0  
**Date:** March 11, 2026

---

## 1. Executive Summary Dashboard

### 1.1 Quick Stats

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Overall QA Score | Weighted quality assurance score across all analyzed calls | `avg(grading.total_score_percent)` across all calls in the filtered set | Backend: `qa_aggregation_service.py` — averages `total_score_percent` from all call grading results. Frontend: `qaAnalyticsService.ts` `getSummaryStats()` — reads `analysis_summary.overall_team_score`, rounds to integer | — |
| Compliance Rate | Percentage of calls that pass PDPA compliance | `(calls where pdpa_pass = true / total_calls) × 100` | Frontend: `qaAnalyticsService.ts` `calculateComplianceRate()` — filters `individual_call_analysis` for `compliance.pdpa_pass === true`, divides by total, rounds to 1 decimal | Pass = `pdpa_pass === true` |
| Total Revenue Impact | Aggregate estimated deal value across the pipeline | `sum(deal_potential.estimated_value)` over all filtered calls | Frontend: `MainQADashboard.tsx` — reduces `filteredCalls` summing `deal_potential.estimated_value`. Backend: `qa_aggregation_service.py` `total_pipeline_value` | — |
| Qualifying Questions Rate | Success rate of qualifying questions asked by reps | Per call: `asked.length / (asked.length + missed.length) × 100`. Then: `avg` across all calls | Frontend: `qaAnalyticsService.ts` `calculateQualifyingQuestionsRate()` — per-call ratio averaged, rounded to 1 decimal. Legacy fallback: `compliance_rate` field | — |

### 1.2 Revenue KPI Cards

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| High Probability Deals | Total value of deals with high win probability | `sum(estimated_value)` for calls where `probability > 0.7` | Frontend: `MainQADashboard.tsx` — reduces `filteredCalls`, accumulates `estimated_value` only when `deal_potential.probability > 0.7`. Backend: `qa_aggregation_service.py` uses same threshold | Threshold: `probability > 0.7` (70%) |
| Monthly Revenue Projection | Projected monthly revenue from the pipeline | `totalPipelineValue × 0.33` | Frontend: `MainQADashboard.tsx` — multiplies total pipeline by 0.33 (assumes 1/3 of pipeline converts monthly). Backend: `sum(estimated_value × probability)` per call (probability-weighted) | Factor: `0.33` (frontend), probability-weighted (backend) |
| Coaching ROI Potential (aka Revenue Increase Potential) | Potential revenue uplift from coaching interventions on underperforming calls with low-probability deals | `sum(deal_value × (1 − probability))` for calls where `total_score_percent < 70` AND `probability < 0.7` | Frontend: `MainQADashboard.tsx` — filters calls by QA score < 70% and probability < 70%, sums `deal_value × (1 − probability)`. Backend: `qa_aggregation_service.py` uses same logic | Thresholds: QA score `< 70%`, probability `< 0.7` (70%) |
| Deals at Risk | Count of deals with a composite risk score above the at-risk threshold | Count of deals where `riskScore > 0.75`. The risk score combines close probability (40%), call quality (25%), risk factor count (up to 20%), and customer sentiment (15%) into a single 0–1 value | Frontend: `MainQADashboard.tsx` — computes `riskScore` per deal via `calculateRiskScore()`, counts deals exceeding 0.75. Backend: `qa_aggregation_service.py` uses same logic | Threshold: `riskScore > 0.75` |

### 1.3 Charts and Sections

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Performance by QA Category | Average scores across 6 QA categories, derived from 16 grading elements | Each category = average of mapped element scores across all calls. **Categories and element mappings:** (1) Call Opening & Closing = avg(Greetings & Intro, Call Closing); (2) Verification = avg(Verification & Validation); (3) Product Knowledge & Selling = avg(Needs Assessment, Product/Service Presentation, Objection Handling, Sales Tenacity, Closing Technique, Upsell & Cross-sell); (4) Communication Skills = avg(Clarity of Verbal Expression, Active Listening, Telephony Skill & Etiquette); (5) Include NPS = avg(NPS Prompt); (6) Operational System Proficiency = avg(Activity Log, Opportunity Handling, Respond to Customer Queries) | Frontend: `qaAnalyticsService.ts` `calculateQACategories()` — maps each grading element name (case-insensitive `includes`) to a category, sums scores, divides by (element count × total calls) | Element name matching is case-insensitive substring |
| Rep Score Distribution | Agent performance spread with individual rankings | Per call: for each grading element with `weight > 0` and not in N/A list, apply `score >= 75 ? 100 : 0`, then `sum(passFailScore × weight) / totalWeight`. Per agent: `avg(call scores)`. Agents sorted by score descending and ranked | Frontend: `qaAnalyticsService.ts` `getAllAgentsForDistribution()` | Pass threshold: `>= 75`. N/A elements: NPS Prompt, Activity Log, Opportunity Handling, Respond to Customer Queries |
| Top Performers | Leading agents by overall QA score | Agents ranked by average weighted pass/fail score (same formula as Rep Score Distribution), top 3 displayed with call count and score | Frontend: `qaAnalyticsService.ts` `getTopPerformers(data, 3)` — uses backend `top_performers` order if available, recalculates scores, filters agents with `calls > 0` | Limit: 3 |
| Top Deals | Highest value opportunities | Calls filtered to `estimated_value > 0`, sorted by `deal_potential.estimated_value` descending, top 3 shown | Frontend: `MainQADashboard.tsx` — filter, sort, slice(0, 3) | Limit: 3 |
| Recent Alerts | Quality issues requiring attention with priority indicators | Alerts generated from call analysis: **High** priority for PDPA compliance breach (`pdpa_pass = false`) or low call score (`total_score_percent < 50`). Alerts filtered by current rep/date selection. Display capped at 10 | Backend: `qa_aggregation_service.py` `_aggregate()` — generates alerts. Frontend: `qaAnalyticsService.ts` `getRecentAlerts()` — filters by active call IDs/agents, maps priority to display | High: PDPA breach or score < 50. Display limit: 10 |

---

## 2. Call Analysis Dashboard

### 2.1 Call Overview Cards

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Total Calls | Count of analyzed calls in the current filter | `count(individual_call_analysis)` after rep, date, and search filters | Frontend: `CallAnalysisDashboard.tsx` — `searchedCalls.length` | — |
| Team Score | Average QA score across filtered calls | `avg(grading.total_score_percent)` over filtered calls, rounded to integer | Frontend: `CallAnalysisDashboard.tsx` — reduces `searchedCalls` using `getOverallScore(call)` which returns `call.grading.total_score_percent` | — |
| Average Duration | Mean call duration | Parse each call's `call_duration` ("M:SS"), convert to seconds, average, reformat to "M:SS" | Backend: `qa_aggregation_service.py` `_compute_average_duration()` | — |
| Compliance Rate | Percentage of PDPA-compliant calls | Same formula as Executive Summary: `(pdpa_pass true count / total) × 100` | Frontend: `qaAnalyticsService.ts` `calculateComplianceRate()` | Pass = `pdpa_pass === true` |
| Revenue at Risk | Total deal value of all deals classified as at-risk | `sum(deal_value)` for all deals where `riskScore > 0.75` (i.e., the monetary value of the "Deals at Risk" set) | Backend: `qa_aggregation_service.py` — sums deal values for deals exceeding the risk score threshold. Frontend: `CallAnalysisDashboard.tsx` computes `riskScore` per deal and sums values | Threshold: `riskScore > 0.75` |

### 2.2 Individual Call QA Score

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Overall QA Score | Per-call quality score | `grading.total_score_percent` (0-100) as computed by AI analysis | Frontend: `CallAnalysisDashboard.tsx` `getOverallScore()` — returns `call.grading.total_score_percent` | — |
| QA Pass/Fail (Table) | Visual badge in call list | `total_score_percent >= 90` = Pass (green), `< 90` = Fail (red) | Frontend: `CallAnalysisDashboard.tsx` — badge color logic | Pass: `>= 90` |
| QA Pass/Fail (Report) | Pass/fail in PDF report | `total_score_percent >= 75` = Pass, `< 75` = Fail | Frontend: `CallAnalysisDashboard.tsx` report section | Pass: `>= 75` |

### 2.3 Compliance and Sentiment

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| PDPA Compliance | Per-call compliance status | Binary: `compliance.pdpa_pass === true` → 100 (Pass), `false` → 0 (Fail). Includes breach list and professional conduct assessment | Frontend: `CallAnalysisDashboard.tsx` `getComplianceScore()`. Backend AI: `ai_analyzer.py` — prompt checks for PDPA breaches | Pass = `pdpa_pass === true` |
| Customer Sentiment | Overall customer sentiment for a call | `sentiment_analysis.overall_sentiment × 100` (displayed as 0-100%) | Frontend: `CallAnalysisDashboard.tsx` — `Math.round(call.sentiment_analysis.overall_sentiment * 100)`. Backend: `ai_analyzer.py` — keyword-based fallback: `(positive_count - negative_count) / (positive_count + negative_count)`, normalized from [-1,1] to [0,1] via `(sentiment + 1) / 2` | Range: 0-100% |
| Sentiment Progression | Sentiment change over the course of a call | Transcript split into 5 equal chunks; average sentiment per chunk produces a 5-point progression array | Backend: `ai_analyzer.py` — divides `segment_sentiments` into 5 chunks, averages each. Frontend: `transcriptService.ts` — linear interpolation to match transcript segment count | Max 5 data points |
| Key Sentiment Moments | Points in the call where sentiment shifted significantly | Segments where `abs(current_sentiment - previous_sentiment) > 0.2` | Frontend: `transcriptService.ts` — flags segments exceeding the threshold | Change threshold: `> 0.2` |

### 2.4 QA Scoring Breakdown

The AI scores each call against 16 grading elements. Each element receives a score (0-100) with evidence quotes.

| Element | Weight | Category |
|---------|--------|----------|
| Greetings & Intro | 5 | Call Opening & Closing |
| Call Closing | 5 | Call Opening & Closing |
| Verification & Validation | 5 | Verification |
| Needs Assessment | 10 | Product Knowledge & Selling |
| Product/Service Presentation | 10 | Product Knowledge & Selling |
| Objection Handling | 10 | Product Knowledge & Selling |
| Sales Tenacity & Determination | 10 | Product Knowledge & Selling |
| Closing Technique & Follow-Up | 10 | Product Knowledge & Selling |
| Upsell & Cross-sell | 10 | Product Knowledge & Selling |
| Clarity of Verbal Expression | 5 | Communication Skills |
| Active Listening | 5 | Communication Skills |
| Telephony Skill & Etiquette | 10 | Communication Skills |
| NPS Prompt | 10 | Include NPS |
| Activity Log | 15 | Operational System Proficiency |
| Opportunity Handling | 15 | Operational System Proficiency |
| Respond to Customer Queries | 15 | Operational System Proficiency |

**Total weight:** 150

**Per-element pass/fail logic (frontend weighted scoring):**

- If element `score >= 75` → passFailScore = 100
- If element `score < 75` → passFailScore = 0
- Weighted score = `sum(passFailScore × weight) / sum(weight)` (excluding N/A elements)

**AI prompt pass threshold:** 70% (backend `ai_analyzer.py`)

**N/A elements** (excluded from weighted scoring in Rep Score Distribution): NPS Prompt, Activity Log, Opportunity Handling, Respond to Customer Queries

### 2.5 Qualifying Questions

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Success Rate | Percentage of qualifying questions successfully asked | `asked.length / (asked.length + missed.length) × 100` per call | Frontend: `CallAnalysisDashboard.tsx` and `qaAnalyticsService.ts`. Backend: `qa_aggregation_service.py` | — |

**Standard qualifying questions checked by AI:**

1. Pain points with existing service
2. Budget range
3. Decision timeline
4. Number of users/employees
5. Current contract status
6. Decision makers involved
7. Current service provider
8. Business goals and objectives
9. Compliance/security requirements

### 2.6 Call Metrics

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Talk-to-Listen Ratio | Proportion of call where the agent spoke | `agent_words / (agent_words + customer_words)` | Backend: `ai_analyzer.py` — counts words per speaker from transcript segments. Default: 0.5 if no words | Default: 0.5 |
| Interruptions | Count of times the customer was interrupted | Speaker change where gap < 0.5s and gap > -0.5s, and the new speaker is the customer | Backend: `ai_analyzer.py` — analyzes speaker turn timestamps | Gap threshold: `< 0.5s` |
| Speaking Pace (WPM) | Agent's speaking speed in words per minute | `total_words / (duration_in_seconds / 60)`, clamped to range | Backend: `ai_analyzer.py` — calculates from transcript timestamps. Default: 150 WPM if duration is 0 | Range: 80-250 WPM |
| Energy Level | Agent's vocal energy during the call | Default value (audio-level analysis not yet implemented) | Backend: `ai_analyzer.py` — returns static default | Default: 0.65 |
| Voice Clarity | Clarity of the agent's speech | Default value (audio-level analysis not yet implemented) | Backend: `ai_analyzer.py` — returns static default | Default: 0.85 |

---

## 3. Rep Performance Dashboard

### 3.1 Overview Metrics

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Team Average Score | Mean QA score across all reps | `avg(grading.total_score_percent)` across all calls, rounded to integer | Frontend: `AgentPerformanceDashboard.tsx` — reduces all `individual_call_analysis` using `getOverallScore()` | — |
| Top Performer | Best performing agent | Agent with the highest `avg(total_score_percent)` across their calls | Frontend: `AgentPerformanceDashboard.tsx` — groups calls by agent, averages scores, sorts descending, takes first | — |
| Revenue Pipeline | Total estimated deal value | Team total: `revenue_impact.total_pipeline_value` from backend. Per rep: `sum(deal_potential.estimated_value)` for that rep's calls | Frontend: `AgentPerformanceDashboard.tsx` — accumulates `deal_potential.estimated_value` per agent during `processAgentMetrics` | — |
| Team Compliance % | Team-wide PDPA compliance rate | `compliance_overview.average_compliance` from backend = `(compliant_calls / total_calls) × 100` | Backend: `qa_aggregation_service.py` — counts calls with `pdpa_pass = true` | — |

### 3.2 Rep Scorecards

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Rep Overall Score | Individual rep QA score | `avg(total_score_percent)` across that agent's calls, rounded to integer | Frontend: `AgentPerformanceDashboard.tsx` `processAgentMetrics()` | — |
| Rep Total Calls | Number of calls analyzed for a rep | Count of `individual_call_analysis` where `agent_name` matches | Frontend: `AgentPerformanceDashboard.tsx` | — |
| Rep Avg Duration | Average call duration for a rep | Mean of call durations for that agent | Frontend: `AgentPerformanceDashboard.tsx` | — |

### 3.3 Skills Radar

Six dimensions derived from the 16 QA grading elements:

| Radar Dimension | Source Elements | Formula |
|-----------------|----------------|---------|
| Call Opening & Closing | Greetings & Intro, Call Closing | `avg(element_scores)` per call, then mean across calls |
| Verification | Verification & Validation | `avg(element_score)` across calls |
| Product Knowledge & Selling | Needs Assessment, Product/Service Presentation, Objection Handling | `avg(element_scores)` per call, then mean across calls |
| Communication Skills | Clarity of Verbal Expression, Active Listening, Telephony Skill & Etiquette | `avg(element_scores)` per call, then mean across calls |
| Include NPS | NPS Prompt | `avg(element_score)` across calls |
| Operational System Proficiency | Activity Log, Opportunity Handling, Respond to Customer Queries | `avg(element_scores)` per call, then mean across calls |

**Implementation:** Frontend: `AgentPerformanceDashboard.tsx` — `getScoreFromGrading()` finds grading element by case-insensitive substring match, computes per-call category average, then averages across calls. Individual rep radar overlays agent values against team averages.

### 3.4 Revenue Distribution

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Revenue per Agent | Each rep's contribution to total pipeline | Per agent: `sum(deal_potential.estimated_value)` for their calls | Frontend: `AgentPerformanceDashboard.tsx` — pie chart with `agent.revenue_generated` | — |
| Revenue Percentage | Share of total pipeline | `(agent_revenue / total_revenue) × 100` | Frontend: `AgentPerformanceDashboard.tsx` — computed in pie chart tooltip | — |

### 3.5 Training and Coaching

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Training Priorities | QA elements needing most improvement across the team | Bottom 5 grading elements by average score across all calls. **Priority:** High if `avg_score < 60`, Medium otherwise. **Affected agents:** agents with at least one call where the element `score < 75` | Backend: `qa_aggregation_service.py` — sorts `element_scores` ascending, takes bottom 5 | High: `avg < 60`. Affected: `score < 75`. Limit: 5 |
| Agent Strengths | Top scoring areas for an individual rep | Top 3 grading elements by average score for that agent's calls | Backend: `qa_aggregation_service.py` `_find_strengths()` — groups element scores per agent, sorts descending, takes top 3 | Limit: 3 |
| Agent Improvement Areas | Lowest scoring areas for an individual rep | Bottom 3 grading elements by average score for that agent's calls | Backend: `qa_aggregation_service.py` `_find_weak_areas()` — groups element scores per agent, sorts ascending, takes bottom 3 | Limit: 3 |
| Coaching Eligibility | Reps who would benefit from coaching | Agents whose `avg(total_score_percent) < 75` | Backend: `qa_aggregation_service.py` — filters agents with average score below threshold, returns focus areas and coaching score. Limit: 5 agents | Threshold: `avg < 75`. Limit: 5 |
| Immediate Actions | Most urgent skill gaps to address | Grading elements with `score < 50` or questions in `qualifying_questions.missed`, aggregated by frequency, top 3 returned | Backend: `qa_aggregation_service.py` — counts occurrences of low-scoring elements and missed questions, sorts by frequency descending, formats as "Improve {element}" | Weak threshold: `score < 50`. Limit: 3 (backend), 5 (frontend) |

### 3.6 Performance Trends

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Weekly Team Average | Team QA score trend over time | `avg(total_score_percent)` for calls in each ISO week, plotted over last 6 weeks | Frontend: `AgentPerformanceDashboard.tsx` — groups calls by ISO week, computes team average per week | Window: 6 weeks |
| Weekly Top Performer | Best agent score per week | `max(agent_avg_score)` per week | Frontend: `AgentPerformanceDashboard.tsx` | Window: 6 weeks |
| Weekly Revenue | Pipeline value trend over time | `sum(deal_potential.estimated_value)` per week | Frontend: `AgentPerformanceDashboard.tsx` | Window: 6 weeks |
| Trend Direction | Whether a metric is improving or declining | `change > 2` = "up", `change < -2` = "down", else "stable" | Frontend: `dashboardComputations.ts` | Up: `> 2`, Down: `< -2` |

---

## 4. Deal Analysis Dashboard

### 4.1 Deal Overview Cards

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Total Pipeline Value | Aggregate value of all deals | `sum(recurring_charge + one_off_charge)` from SFDC action data per call. Falls back to `sum(deal_potential.estimated_value)` when SFDC data unavailable | Frontend: `DealAnalysisDashboard.tsx` — fetches SFDC action per call via `/api/v1/calls/{id}/sfdc-action`, sums `recurring + one_off`. Backend fallback: `qa_aggregation_service.py` sums `deal_potential.estimated_value` | — |
| High Probability Deals | Count of deals likely to close | Primary: count where `probability > 0.7`. Alternative: count where `deal_value > 10000 AND probability > 0.6` | Frontend: `DealAnalysisDashboard.tsx` — KPI card uses `probability > 0.7` only | Primary: `> 0.7`. Alt: `> 10000` and `> 0.6` |
| At-Risk Deals | Count of deals with a composite risk score above the at-risk threshold | Count of deals where `riskScore > 0.75`. The risk score is a composite of close probability (40%), call quality (25%), risk factor count (up to 20%), and customer sentiment (15%) | Frontend: `DealAnalysisDashboard.tsx` — computes `riskScore` per deal via `calculateRiskScore()`, counts those exceeding 0.75 | Threshold: `riskScore > 0.75` |
| Monthly Revenue Projection | Expected monthly revenue | `totalPipelineValue × 0.33` | Frontend: `DealAnalysisDashboard.tsx` | Factor: `0.33` |
| Coaching ROI Potential (aka Revenue Increase Potential) | Revenue uplift from coaching interventions on underperforming, low-probability deals | `sum(deal_value × (1 − probability))` for calls where `total_score_percent < 70` AND `probability < 0.7` | Frontend: `DealAnalysisDashboard.tsx` — filters by QA score < 70% and probability < 70%, sums `deal_value × (1 − probability)` | Thresholds: QA score `< 70%`, probability `< 0.7` |

### 4.2 Risk Assessment

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Risk Score | Composite risk indicator for a deal, combining four weighted signals into a single 0–1 value. A deal is "at risk" when this score exceeds 0.75 | `(1 - probability) × 0.4 + (1 - overallScore/100) × 0.25 + min(riskFactorCount × 0.05, 0.2) + (1 - sentimentScore) × 0.15`, capped at 1.0 | Frontend: `DealAnalysisDashboard.tsx` `calculateRiskScore()` | Weights: Probability 40%, Performance 25%, Risk Factors 5%/factor (max 20%), Sentiment 15%. Cap: 1.0. At-risk threshold: `> 0.75` |
| Risk Level | Categorical risk classification based on the composite risk score | Low: `riskScore <= 0.4`. Medium: `riskScore > 0.4 AND <= 0.75`. High: `riskScore > 0.75` | Frontend: `DealAnalysisDashboard.tsx` — risk distribution calculation | Low: `<= 0.4`, Medium: `0.4–0.75`, High: `> 0.75` |

**How the Risk Score works (plain language):**

The risk score is a single number between 0 and 1. It adds four pieces together, each making the score higher when things look worse:

1. **Close chance (40% of the score):** The lower the probability the deal will close, the more risk. "Unlikely to close" pushes the score up.
2. **Call quality (25% of the score):** The lower the QA score for the call, the more risk. "Poor call" pushes the score up.
3. **Number of risk factors (up to 20% of the score):** Each risk factor (e.g., contract issues, competitor mentions) adds a bit. The more factors the higher this part, but it stops increasing after a point (capped at 20%).
4. **Customer sentiment (15% of the score):** The more negative the customer sounded on the call, the more risk. "Unhappy customer" pushes the score up.

The four parts are added together and the result is capped at 1.0. A deal is classified as **"at risk"** when this number exceeds **0.75**.

### 4.3 Deal Value Calculation

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Deal Value (CRM) | Actual deal value from Salesforce CPQ pricing | Per product: `product_recurring_charge × quantity` + `product_one_off_charge × quantity`. Deal total: sum across all matched products | Backend: `crm_actions_step6.py` — queries Salesforce CPQ (`cspmb__Price_Item__c`) via BSSMagic TMF, retrieves pricing from `cspmb__Pricing_Element__c` → `cspmb__Price_Item_Pricing_Rule_Association__c`. Writes `sfdc_action.json` with `total_recurring_charge` and `total_one_off_charge` | Currency: SGD. Default quantity: 1. Default contract term: 24 months |
| Deal Value (AI Estimate) | AI-estimated deal value when CRM pricing unavailable | GPT estimates deal value in SGD based on products discussed; set to 0 if no pricing discussed | Backend: `ai_analyzer.py` — prompt instructs: "Deal value (in SGD) — set to 0 if no pricing was discussed" | — |
| Deal Probability | Likelihood of deal closing | AI-generated win probability on a 0-1 scale | Backend: `ai_analyzer.py` — GPT estimates based on call context. Output: `deal_potential.probability` (0-1) | Range: 0-1 |
| Product Interest Level | Customer's interest in a specific product | AI-classified from transcript: **High** = customer explicitly agreed or showed enthusiasm; **Medium** = customer asked questions without committing; **Low** = customer hesitated or declined | Backend: `ai_analyzer.py` — prompt: "Base this strictly on what the customer said — do NOT infer or assume" | Values: high, medium, low |

### 4.4 Engagement and Filtering

| KPI | Business Definition | Formula / Logic | Implementation | Constants / Thresholds |
|-----|---------------------|-----------------|----------------|------------------------|
| Engagement Score | Per-call performance in the engagement timeline | `grading.total_score_percent` (0-100). Visual: >= 80 large indicator, 60-79 medium, < 60 small/red | Frontend: `DealAnalysisDashboard.tsx` — timeline circles sized and colored by score | Large: `>= 80`, Medium: `60-79`, Small/Red: `< 60` |

---

## 5. Constants and Thresholds Reference

| Constant | Value | Used In |
|----------|-------|---------|
| High probability threshold | `> 0.7` (70%) | Executive Summary, Deal Analysis |
| High probability alt (value) | `> 10,000` SGD | Deal Analysis (alternative filter) |
| High probability alt (prob) | `> 0.6` (60%) | Deal Analysis (alternative filter) |
| Monthly projection factor | `0.33` | Executive Summary, Deal Analysis (frontend) |
| Coaching ROI — QA score threshold | `< 70%` | Executive Summary, Deal Analysis (filters calls eligible for coaching ROI) |
| Coaching ROI — probability threshold | `< 0.7` (70%) | Executive Summary, Deal Analysis (filters calls eligible for coaching ROI) |
| At-risk risk score threshold | `> 0.75` | Executive Summary, Call Analysis, Deal Analysis (Deals at Risk, Revenue at Risk) |
| QA element pass/fail (weighted) | `>= 75` → 100, `< 75` → 0 | Rep Score Distribution, Top Performers |
| QA pass badge (call list table) | `>= 90` | Call Analysis list view |
| QA pass badge (PDF report) | `>= 75` | Call Analysis report |
| AI prompt pass threshold | 70% | AI Analyzer grading |
| Coaching eligibility | `avg < 75` | Rep Performance coaching |
| Training priority High | `avg < 60` | Rep Performance training |
| Weak element threshold | `score < 50` | Immediate actions |
| N/A weight elements | NPS Prompt, Activity Log, Opportunity Handling, Respond to Customer Queries | Weighted score calc (excluded) |
| Risk score — probability weight | 0.4 (40%) | Deal Analysis risk score |
| Risk score — performance weight | 0.25 (25%) | Deal Analysis risk score |
| Risk score — risk factor weight | 0.05 per factor, max 0.2 | Deal Analysis risk score |
| Risk score — sentiment weight | 0.15 (15%) | Deal Analysis risk score |
| Interruption detection gap | `< 0.5s` | Call Metrics |
| WPM clamp range | 80-250 | Call Metrics |
| Sentiment key moment threshold | `change > 0.2` | Sentiment Progression |
| Default energy level | 0.65 | Call Metrics (static) |
| Default voice clarity | 0.85 | Call Metrics (static) |
| Default contract term | 24 months | Product pricing / deal value |
| Default product quantity | 1 | Product pricing / deal value |
| Currency | SGD | Product pricing |
| Trend direction — up | `change > 2` | Performance Trends |
| Trend direction — down | `change < -2` | Performance Trends |
| Top performers limit | 3 | Executive Summary |
| Top deals limit | 3 | Executive Summary |
| Recent alerts limit | 10 | Executive Summary |
| Training priorities limit | 5 | Rep Performance |
| Strengths / improvements limit | 3 each | Rep Performance |
| Coaching opportunities limit | 5 | Rep Performance |
| Performance trends window | 6 weeks | Rep Performance |

---

## 6. Backend vs Frontend Computation Notes

### Where Calculations Happen

The NexusAI architecture splits KPI computation between the backend aggregation service and the frontend dashboard components. Understanding which layer computes what is critical for debugging discrepancies.

**Backend** (`qa_aggregation_service.py`):

- `overall_team_score` — `avg(grading.total_score_percent)`
- `compliance_rate` — `(pdpa_pass true count / total) × 100`
- `average_call_duration` — parsed and averaged from call metadata
- `revenue_impact.total_pipeline_value` — `sum(deal_potential.estimated_value)`
- `revenue_impact.high_probability_deals` — `sum(estimated_value)` where `probability > 0.7`
- `revenue_impact.at_risk_deals` — count where `riskScore > 0.75`
- `revenue_impact.revenue_at_risk` — `sum(deal_value)` where `riskScore > 0.75`
- `revenue_impact.coaching_roi_potential` — `sum(deal_value × (1 − probability))` where QA score < 70% and probability < 0.7
- `revenue_impact.monthly_revenue_projection` — `sum(estimated_value × probability)` (probability-weighted)
- `areas_for_improvement` — bottom 5 elements by avg score
- `coaching_opportunities` — agents with avg score < 75
- `alerts_and_flags` — PDPA breaches and low scores

**Frontend overrides** (when rep/date filters are applied):

- `total_pipeline_value` → `sum(deal_potential.estimated_value)` over filtered calls
- `high_probability_deals` → `sum(estimated_value)` where `probability > 0.7` over filtered calls
- `coaching_roi_potential` → `sum(deal_value × (1 − probability))` for calls where QA score < 70% and probability < 0.7
- `monthly_revenue_projection` → `totalPipeline × 0.33` (simplified from backend's probability-weighted formula)
- `at_risk_deals` → count of deals where `riskScore > 0.75`, re-computed from filtered deal set
- `revenue_at_risk` → `sum(deal_value)` where `riskScore > 0.75`

### Key Differences

| Metric | Backend Formula | Frontend Formula (with filters) |
|--------|----------------|--------------------------------|
| Coaching ROI | `sum(deal_value × (1 − probability))` where QA < 70% and prob < 0.7 | Same formula applied to filtered call set |
| Monthly Projection | `sum(estimated_value × probability)` | `total_pipeline × 0.33` |
| Deal Value Source | AI estimate (`deal_potential.estimated_value`) | SFDC actual (`recurring + one_off`) with AI fallback |

### Deal Value Pipeline

```
Call in Webex → AI Analyzer (GPT) → estimated_value (AI estimate)
                                  ↓
                   CRM Actions Step 6 → CloudSense product matching
                                      → Salesforce CPQ pricing query
                                      → sfdc_action.json (recurring + one_off)
                                  ↓
         Deal Analysis Dashboard → uses SFDC values when available, AI estimate as fallback
         Executive Summary       → uses AI estimated_value (no SFDC fetch)
```

---
