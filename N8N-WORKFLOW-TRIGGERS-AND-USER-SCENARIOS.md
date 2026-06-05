# n8n Workflow Triggers & End User Scenarios

## Executive Summary

The DDN AI Test Failure Analysis System uses **n8n workflow orchestration** to coordinate AI-powered analysis of test failures. The system supports **4 distinct trigger mechanisms**, each designed for different use cases and user personas.

**Quick Overview:**
- **Trigger 1:** Jenkins Webhooks (Automated CI/CD) - Real-time failure capture
- **Trigger 2:** Manual Dashboard (User-initiated) - On-demand analysis
- **Trigger 3:** Aging Service (Scheduled batch) - Auto-analysis for long-running failures
- **Trigger 4:** Direct API (Programmatic) - Integration with external systems

---

## Understanding n8n Workflow Architecture

### Workflow File Location
```
implementation/DDN_AI_Workflow_Production.json
```

### Key Workflow Nodes
1. **Webhook Trigger** - Entry point for all triggers (port 5678)
2. **Extract Webhook Data** - Parse incoming payload
3. **MongoDB Get Minimal** - Fetch failure data (collection: `test_failures`)
4. **LangGraph Classify** - AI classification (port 5000)
5. **Response Success** - Return acknowledgment

### Workflow Endpoint
```bash
http://localhost:5678/webhook/ddn-test-failure
```

---

## Trigger Mechanism #1: Jenkins Webhooks (Automated)

### Overview
**Real-time automated trigger** that fires immediately when Jenkins CI/CD pipeline detects a test failure.

### Technical Details

**Service:** Jenkins CI/CD Pipeline  
**Trigger Type:** POST webhook to n8n  
**Timing:** Real-time (< 5 seconds after build completion)  
**Port:** n8n on 5678  
**URL:** `http://localhost:5678/webhook/ddn-test-failure`  

**Webhook Configuration File:**
```
jenkins/webhook-config.json
```

**Payload Structure:**
```json
{
  "build_id": "12345",
  "build_url": "http://jenkins.company.com/job/DDN-Tests/12345",
  "job_name": "DDN-EXAScaler-Tests",
  "test_suite": "ddn_basic_tests",
  "status": "FAILURE",
  "timestamp": "2025-01-11T10:30:00Z",
  "error_log": "AssertionError: Expected 200, got 500..."
}
```

### User Scenario 1.1: Automated CI/CD Failure Capture

**Persona:** QA Engineer (Passive monitoring)  
**Context:** Jenkins nightly test run completes with failures  

**Flow:**
1. Jenkins executes Robot Framework test suite (`ddn_basic_tests.robot`)
2. Test fails with error (e.g., API timeout, assertion failure)
3. MongoDB Robot listener captures failure to `test_failures` collection
4. Jenkins post-build action triggers n8n webhook
5. n8n workflow receives webhook payload
6. Workflow extracts data and queries MongoDB for failure details
7. LangGraph service classifies error (port 5000)
8. Analysis stored in PostgreSQL `failure_analysis` table
9. Dashboard displays new failure in real-time

**Expected Outcome:**
- ✅ Failure appears in Dashboard Failures list within 30 seconds
- ✅ AI classification shows error category (e.g., "API Timeout")
- ✅ Confidence score calculated (e.g., 87%)
- ✅ Related failures linked via RAG similarity search

**Success Criteria:**
- End-to-end latency < 1 minute
- Classification accuracy > 85%
- Zero webhook delivery failures

**Key Files:**
- `jenkins/webhook-config.json` - Jenkins webhook setup
- `robot-tests/ddn_basic_tests.robot` - Test suite
- `implementation/mongodb_robot_listener.py` - Captures failures to MongoDB

---

## Trigger Mechanism #2: Manual Dashboard (User-Initiated)

### Overview
**User-initiated trigger** from Dashboard UI when QA engineers want to force immediate analysis of a specific build.

### Technical Details

**Service:** Manual Trigger API (Flask)  
**Port:** 5004  
**API File:** `implementation/manual_trigger_api.py`  
**Endpoint:** `POST /api/trigger-analysis`  

**Dashboard Pages:**
- **Manual Trigger Page:** `http://localhost:5173/manual-trigger` (old page)
- **Trigger Analysis Page:** `http://localhost:5173/trigger-analysis` (preferred)

**Request Payload:**
```json
{
  "build_id": "12345",
  "triggered_by_user": "john.doe@company.com",
  "trigger_source": "dashboard",
  "reason": "Critical production issue needs immediate analysis"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Analysis triggered successfully",
  "trigger_id": 456,
  "build_id": "12345",
  "consecutive_failures": 3,
  "webhook_response": {...}
}
```

### User Scenario 2.1: Manual Analysis from Dashboard

**Persona:** QA Engineer (Active investigation)  
**Context:** Engineer notices a critical failure pattern that needs immediate attention  

**Flow:**
1. User navigates to Dashboard (`http://localhost:5173`)
2. Reviews Failures list, sees critical failure for build `BUILD-42`
3. Clicks "Trigger Analysis" button on failure card
4. Dashboard sends POST request to Manual Trigger API (port 5004)
5. API logs manual trigger to PostgreSQL `manual_trigger_log` table
6. API fetches consecutive failure count from `failure_analysis` table
7. API constructs payload with `manual_trigger: true` flag
8. API sends webhook to n8n (`http://localhost:5678/webhook/ddn-test-failure`)
9. n8n workflow processes request (same flow as Jenkins webhook)
10. Analysis results returned to Dashboard
11. User sees updated analysis with AI recommendations

**Expected Outcome:**
- ✅ Trigger logged with ID and user email in PostgreSQL
- ✅ n8n workflow executes within 10 seconds
- ✅ Dashboard shows "Analysis in progress..." indicator
- ✅ Results displayed when analysis completes
- ✅ User can provide feedback on AI recommendation

**Success Criteria:**
- Button click to results < 30 seconds
- Trigger success rate > 99%
- User feedback mechanism available

**Key Files:**
- `implementation/manual_trigger_api.py` - Manual trigger API (port 5004)
- `dashboard/src/pages/TriggerAnalysis.tsx` - UI page
- `dashboard/src/components/FailureCard.tsx` - Trigger button component

### User Scenario 2.2: Manual Trigger with Custom Reason

**Persona:** QA Team Lead  
**Context:** Production escalation requires immediate root cause analysis  

**Flow:**
1. User navigates to Manual Trigger page (`/manual-trigger`)
2. Enters build ID: `PROD-BUILD-789`
3. Selects trigger reason from dropdown: "Production Critical Issue"
4. Adds custom note: "Customer reported data corruption after deployment"
5. Clicks "Trigger Analysis" button
6. API validates input fields (build_id required)
7. API logs trigger with reason and user email
8. n8n workflow triggered with enhanced metadata
9. Analysis prioritized due to "Production Critical" flag
10. Slack notification sent to QA team channel
11. Results emailed to stakeholders

**Expected Outcome:**
- ✅ Trigger reason captured in database for audit trail
- ✅ High-priority analysis queue placement
- ✅ Stakeholder notifications sent
- ✅ Analysis includes historical context from previous builds

**Key Features:**
- Input validation (build_id required)
- Reason tracking for compliance/audit
- Priority queue for critical issues

---

## Trigger Mechanism #3: Aging Service (Scheduled Batch)

### Overview
**Automated scheduled batch processing** that analyzes failures meeting aging criteria (failures persisting for 3+ days without resolution).

### Technical Details

**Service:** Aging Service (Flask + APScheduler)  
**Port:** 5007  
**Service File:** `implementation/aging_service.py`  
**Schedule:** Every 6 hours (cron: `0 */6 * * *`)  

**Aging Criteria:**
- **Time Threshold:** Failure span (first to last occurrence) >= 3 days
- **Failure Count:** Minimum 2 failures for same build_id
- **Status:** Failures marked as `analyzed: false` in MongoDB

**MongoDB Query:**
```javascript
// Aggregation pipeline in aging_service.py
{
  $match: {
    status: "failed",
    analyzed: { $ne: true }
  }
},
{
  $group: {
    _id: "$build_id",
    first_failure: { $min: "$created_at" },
    last_failure: { $max: "$created_at" },
    failure_count: { $sum: 1 }
  }
},
{
  $match: {
    days_span: { $gte: 3 },
    failure_count: { $gte: 2 }
  }
}
```

**Payload Structure:**
```json
{
  "build_id": "12345",
  "build_url": "http://jenkins/job/DDN-Tests/12345",
  "job_name": "DDN-AI400X-Tests",
  "test_suite": "ddn_advanced_tests",
  "status": "FAILURE",
  "timestamp": "2025-01-11T10:30:00Z",
  "trigger_source": "aging_service",
  "aging_metadata": {
    "days_span": 5.3,
    "failure_count": 8,
    "first_failure": "2025-01-06T08:15:00Z",
    "last_failure": "2025-01-11T10:30:00Z"
  }
}
```

### User Scenario 3.1: Automated Aging Analysis

**Persona:** QA Engineer (Passive discovery)  
**Context:** Long-running test failures that fell through the cracks  

**Flow:**
1. Aging service scheduler triggers every 6 hours (cron job)
2. Service queries MongoDB `test_failures` collection
3. Aggregation pipeline identifies builds meeting aging criteria:
   - Build `BUILD-27`: 8 failures over 5.3 days
   - Build `BUILD-31`: 4 failures over 3.8 days
4. Service triggers n8n for each aged build (oldest first)
5. Trigger logged to PostgreSQL `aging_trigger_log` table with metadata
6. n8n workflow processes each build sequentially
7. AI analysis identifies root cause patterns across multiple failures
8. Dashboard displays aged failures with "Aging Service" badge
9. Email notification sent to QA team with summary

**Expected Outcome:**
- ✅ Aged failures automatically analyzed without manual intervention
- ✅ Historical context included (failure trend over time)
- ✅ Root cause patterns identified across multiple occurrences
- ✅ Team notified of chronic issues requiring attention

**Success Criteria:**
- Aging detection accuracy 100%
- Zero false positives (only analyze qualifying failures)
- Analysis completion within 2 hours of detection

**Key Files:**
- `implementation/aging_service.py` - Aging service with APScheduler
- PostgreSQL `aging_trigger_log` table - Audit trail

### User Scenario 3.2: Aging Service Dashboard Monitoring

**Persona:** QA Manager  
**Context:** Weekly review of chronic failure trends  

**Flow:**
1. User navigates to Dashboard Analytics page
2. Filters by trigger source: "Aging Service"
3. Views aging trigger statistics:
   - 12 aged failures detected this week
   - Average days span: 4.2 days
   - Most common failure: "API Timeout" (5 occurrences)
4. Reviews aging trigger log table
5. Identifies systemic issues requiring architectural fixes
6. Creates Jira epic for infrastructure improvements
7. Assigns tasks to engineering team

**Expected Outcome:**
- ✅ Visibility into chronic failure patterns
- ✅ Data-driven prioritization of technical debt
- ✅ Proactive issue resolution before customer impact

---

## Trigger Mechanism #4: Direct API (Programmatic)

### Overview
**Direct API access** for integrations with external systems (CI/CD tools, monitoring platforms, custom scripts).

### Technical Details

**Service:** Manual Trigger API (Flask)  
**Port:** 5004  
**Authentication:** Bearer token (optional, configure in .env)  
**Endpoint:** `POST http://localhost:5004/api/trigger-analysis`  

**Use Cases:**
- GitHub Actions workflow integration
- Custom monitoring alerting systems
- Programmatic batch analysis scripts
- Third-party CI/CD platforms (CircleCI, GitLab CI)

**cURL Example:**
```bash
curl -X POST http://localhost:5004/api/trigger-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "GH-ACTION-456",
    "triggered_by_user": "github-actions-bot",
    "trigger_source": "github_actions",
    "reason": "Automated smoke test failure"
  }'
```

**Python SDK Example:**
```python
import requests

def trigger_analysis(build_id: str, user: str, reason: str):
    """Trigger DDN AI analysis programmatically"""
    response = requests.post(
        "http://localhost:5004/api/trigger-analysis",
        json={
            "build_id": build_id,
            "triggered_by_user": user,
            "trigger_source": "python_sdk",
            "reason": reason
        },
        timeout=10
    )
    return response.json()

# Usage
result = trigger_analysis(
    build_id="CUSTOM-BUILD-123",
    user="automation@company.com",
    reason="Post-deployment smoke test failure"
)
print(f"Trigger ID: {result['trigger_id']}")
```

### User Scenario 4.1: GitHub Actions Integration

**Persona:** DevOps Engineer  
**Context:** Integrate DDN AI analysis into GitHub Actions CI/CD pipeline  

**Flow:**
1. GitHub Actions workflow runs test suite
2. Test job fails with exit code 1
3. GitHub Actions step extracts build ID and error log
4. Workflow step calls DDN API programmatically:
   ```yaml
   - name: Trigger DDN AI Analysis
     if: failure()
     run: |
       curl -X POST http://ddn-api:5004/api/trigger-analysis \
         -H "Content-Type: application/json" \
         -d "{
           \"build_id\": \"${{ github.run_id }}\",
           \"triggered_by_user\": \"github-actions\",
           \"trigger_source\": \"github_actions\",
           \"reason\": \"Workflow failure in ${{ github.workflow }}\"
         }"
   ```
5. DDN API receives request and triggers n8n workflow
6. Analysis results posted back to GitHub PR as comment
7. Jira ticket auto-created with AI recommendations

**Expected Outcome:**
- ✅ Seamless integration with GitHub Actions
- ✅ Analysis results visible in PR comments
- ✅ Automated ticket creation in Jira
- ✅ Zero manual intervention required

**Key Features:**
- RESTful API design
- Standard HTTP status codes
- JSON request/response
- Timeout handling (10s default)

### User Scenario 4.2: Monitoring Alert Integration

**Persona:** Site Reliability Engineer (SRE)  
**Context:** Production monitoring alert triggers automated analysis  

**Flow:**
1. Datadog monitoring detects anomaly (API response time > 5s)
2. Datadog webhook fires to DDN API endpoint
3. Webhook payload mapped to DDN trigger format
4. Analysis triggered with monitoring context metadata
5. AI identifies root cause (database connection pool exhaustion)
6. PagerDuty incident created with AI recommendations
7. On-call engineer receives actionable insights

**Expected Outcome:**
- ✅ Monitoring alerts enriched with AI analysis
- ✅ Faster incident resolution (MTTR reduced by 60%)
- ✅ Contextual recommendations based on historical data

---

## Trigger Comparison Matrix

| Trigger Type | Timing | User Interaction | Use Case | Latency | Priority |
|-------------|--------|------------------|----------|---------|----------|
| **Jenkins Webhook** | Real-time | None (automated) | CI/CD pipeline failures | < 1 min | High |
| **Manual Dashboard** | On-demand | User clicks button | Specific build investigation | < 30 sec | Critical |
| **Aging Service** | Every 6 hours | None (scheduled) | Chronic failure detection | N/A | Medium |
| **Direct API** | On-demand | Programmatic | External system integration | < 1 min | Variable |

---

## End-to-End Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          TRIGGER MECHANISMS                             │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                │                  │                  │
                ▼                  ▼                  ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │ Jenkins Webhook │  │ Manual Trigger  │  │  Aging Service  │
    │   (Real-time)   │  │   (On-demand)   │  │   (Scheduled)   │
    │   Port: N/A     │  │   Port: 5004    │  │   Port: 5007    │
    └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
             │                    │                     │
             └────────────────────┼─────────────────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │   n8n Webhook Node    │
                      │   Port: 5678          │
                      │   /webhook/ddn-test   │
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │ Extract Webhook Data  │
                      │ (Parse payload)       │
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │  MongoDB Query        │
                      │  Collection:          │
                      │  test_failures        │
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │  LangGraph Classify   │
                      │  Port: 5000           │
                      │  (AI Analysis)        │
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │  PostgreSQL Store     │
                      │  Table:               │
                      │  failure_analysis     │
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │  Dashboard Update     │
                      │  Port: 5173           │
                      │  (Real-time UI)       │
                      └───────────────────────┘
```

---

## Configuration Files Reference

### 1. n8n Workflow Configuration
**File:** `implementation/DDN_AI_Workflow_Production.json`  
**Purpose:** n8n workflow definition with webhook trigger  
**Key Nodes:**
- Webhook Trigger (ID: `webhook-trigger`)
- Extract Data (ID: `extract-webhook-data`)
- MongoDB Query (ID: `mongodb-get-minimal`)
- LangGraph Call (ID: `langgraph-classify`)

### 2. Manual Trigger API
**File:** `implementation/manual_trigger_api.py`  
**Port:** 5004  
**Endpoints:**
- `POST /api/trigger-analysis` - Trigger analysis
- `POST /api/feedback` - Submit feedback
- `GET /api/feedback/:build_id` - Get feedback
- `GET /health` - Health check

### 3. Aging Service
**File:** `implementation/aging_service.py`  
**Port:** 5007  
**Schedule:** Every 6 hours (APScheduler)  
**Endpoints:**
- `GET /health` - Health check
- `GET /api/aging-stats` - Get aging statistics
- `POST /api/force-check` - Force aging check (admin)

### 4. Jenkins Webhook
**File:** `jenkins/webhook-config.json`  
**Webhook URL:** `http://localhost:5678/webhook/ddn-test-failure`  
**Trigger:** Post-build action (when build status = FAILURE)

---

## Testing Each Trigger Mechanism

### Test Scenario 1: Jenkins Webhook
```bash
# Simulate Jenkins webhook
curl -X POST http://localhost:5678/webhook/ddn-test-failure \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "TEST-JENKINS-001",
    "build_url": "http://jenkins/job/DDN/001",
    "job_name": "DDN-Tests",
    "status": "FAILURE",
    "error_log": "Test assertion failed"
  }'
```

### Test Scenario 2: Manual Dashboard
```bash
# Test manual trigger API
curl -X POST http://localhost:5004/api/trigger-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "TEST-MANUAL-002",
    "triggered_by_user": "qa-engineer@company.com",
    "reason": "Testing manual trigger flow"
  }'
```

### Test Scenario 3: Aging Service
```bash
# Check aging service health
curl http://localhost:5007/health

# Force aging check (admin endpoint)
curl -X POST http://localhost:5007/api/force-check
```

### Test Scenario 4: Direct API (Python)
```python
import requests

response = requests.post(
    "http://localhost:5004/api/trigger-analysis",
    json={
        "build_id": "TEST-API-003",
        "triggered_by_user": "automation-script",
        "trigger_source": "pytest",
        "reason": "Integration test suite failure"
    },
    timeout=10
)

print(f"Status: {response.status_code}")
print(f"Result: {response.json()}")
```

---

## Monitoring & Observability

### Key Metrics to Track

#### Trigger Success Rate
```sql
-- Manual triggers in last 24 hours
SELECT
    COUNT(*) as total_triggers,
    SUM(CASE WHEN trigger_successful = true THEN 1 ELSE 0 END) as successful,
    ROUND(100.0 * SUM(CASE WHEN trigger_successful = true THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM manual_trigger_log
WHERE triggered_at > NOW() - INTERVAL '24 hours';
```

#### Aging Service Statistics
```sql
-- Aged failures detected per day
SELECT
    DATE(triggered_at) as trigger_date,
    COUNT(*) as aged_failures,
    AVG(days_old) as avg_days_old,
    AVG(consecutive_failures) as avg_failures
FROM aging_trigger_log
GROUP BY DATE(triggered_at)
ORDER BY trigger_date DESC
LIMIT 30;
```

#### Trigger Source Distribution
```sql
-- Analysis breakdown by trigger source
SELECT
    trigger_source,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM manual_trigger_log
WHERE triggered_at > NOW() - INTERVAL '7 days'
GROUP BY trigger_source
ORDER BY count DESC;
```

### Dashboard Widgets

**Widget 1: Trigger Source Pie Chart**
- Jenkins Webhooks: 45%
- Manual Dashboard: 30%
- Aging Service: 20%
- Direct API: 5%

**Widget 2: Trigger Success Rate (Last 7 Days)**
- Line chart showing daily success rate
- Target: > 99% success rate

**Widget 3: Average Analysis Latency**
- Bar chart per trigger type
- Jenkins: 45s avg
- Manual: 28s avg
- Aging: 62s avg (batch processing)
- API: 35s avg

---

## Troubleshooting Guide

### Issue: Manual Trigger Fails with 500 Error

**Symptoms:**
- Dashboard button click returns error
- API logs show database connection error

**Diagnosis:**
```bash
# Check Manual Trigger API health
curl http://localhost:5004/health

# Check PostgreSQL connection
psql -h localhost -p 5434 -U postgres -d ddn_qa_system -c "SELECT 1;"
```

**Resolution:**
1. Verify PostgreSQL service is running
2. Check `POSTGRES_URI` environment variable
3. Restart Manual Trigger API: `python implementation/manual_trigger_api.py`

---

### Issue: Aging Service Not Finding Failures

**Symptoms:**
- Aging service reports 0 aged failures
- Known chronic failures not triggered

**Diagnosis:**
```bash
# Check aging service health
curl http://localhost:5007/health

# Query MongoDB directly
mongosh "mongodb+srv://..." --eval '
  db.test_failures.aggregate([
    { $match: { status: "failed", analyzed: { $ne: true } } },
    { $count: "total" }
  ])
'
```

**Resolution:**
1. Verify MongoDB connection string in `.env`
2. Check `status` field in documents (should be "failed", not "FAILURE")
3. Ensure `analyzed` field is boolean false, not string
4. Review aging criteria (3 days span, 2+ failures)

---

### Issue: Jenkins Webhook Not Reaching n8n

**Symptoms:**
- Jenkins build fails but no analysis triggered
- n8n webhook execution logs empty

**Diagnosis:**
```bash
# Check n8n service
curl http://localhost:5678/healthz

# Test webhook manually
curl -X POST http://localhost:5678/webhook/ddn-test-failure \
  -H "Content-Type: application/json" \
  -d '{"build_id": "TEST-001", "status": "FAILURE"}'
```

**Resolution:**
1. Verify n8n service is running: `docker-compose ps n8n`
2. Check Jenkins webhook configuration in job settings
3. Ensure firewall allows Jenkins → n8n communication
4. Review n8n workflow is active (not paused)

---

## Best Practices

### 1. Use Appropriate Trigger for Context
- **Real-time failures:** Jenkins webhooks (automated)
- **Specific investigations:** Manual Dashboard (user-initiated)
- **Chronic issues:** Aging Service (scheduled)
- **External integrations:** Direct API (programmatic)

### 2. Include Meaningful Context
```json
{
  "build_id": "BUILD-789",
  "triggered_by_user": "john.doe@company.com",
  "reason": "Customer-reported issue in production deployment",
  "trigger_source": "dashboard",
  "priority": "critical"
}
```

### 3. Monitor Trigger Success Rates
- Set up alerts for success rate < 95%
- Track latency metrics per trigger type
- Review aging service logs weekly

### 4. Provide Feedback on Analysis
- Use feedback API after reviewing AI recommendations
- Track success/failure of applied fixes
- Refine aging criteria based on feedback trends

---

## Summary Table: When to Use Each Trigger

| Scenario | Recommended Trigger | Why |
|----------|-------------------|-----|
| CI/CD pipeline failure detected | Jenkins Webhook | Automated, real-time, zero latency |
| Investigating specific build failure | Manual Dashboard | User control, immediate feedback, contextual |
| Weekly chronic issue detection | Aging Service | Automated batch, low-priority queue |
| GitHub Actions integration | Direct API | Programmatic, flexible, third-party |
| Production monitoring alert | Direct API | External system integration |
| Post-deployment smoke test failure | Direct API or Jenkins | Automated, high priority |
| QA engineer debugging flaky test | Manual Dashboard | On-demand, user-driven |
| Manager reviewing failure trends | Aging Service (view results) | Historical context, pattern detection |

---

## Next Steps

### For QA Engineers
1. **Test each trigger mechanism** using test scenarios in this document
2. **Monitor Dashboard** for triggered analyses
3. **Provide feedback** on AI recommendations
4. **Review aging service results** weekly for chronic issues

### For DevOps Engineers
1. **Configure Jenkins webhooks** using `jenkins/webhook-config.json`
2. **Integrate with GitHub Actions** using Direct API examples
3. **Set up monitoring alerts** for trigger success rates
4. **Review n8n workflow logs** for errors

### For QA Managers
1. **Review trigger statistics** in Dashboard Analytics
2. **Identify chronic failure patterns** from aging service
3. **Prioritize technical debt** based on aging trends
4. **Track ROI metrics** (MTTR reduction, effort savings)

---

## Related Documentation

- **Architecture Overview:** `00-PROJECT-OVERVIEW.md`
- **Test Plan:** `COMPLETE-TEST-PLAN.md`
- **API Reference:** `ALL-SERVICES-REFERENCE.md`
- **MCP Integration:** `ddn-playwright-automation/docs/MCP-INTEGRATION.md`
- **Jenkins Setup:** `QUICK-START-GITHUB-JENKINS.md`

---

## Appendix: API Response Codes

### Manual Trigger API (Port 5004)

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Analysis triggered |
| 400 | Bad Request | Check `build_id` field |
| 500 | Server Error | Check PostgreSQL/n8n connectivity |
| 504 | Gateway Timeout | n8n webhook timeout (> 10s) |

### Aging Service API (Port 5007)

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Service healthy |
| 503 | Service Unavailable | Check MongoDB/PostgreSQL |

### n8n Webhook

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Workflow executed |
| 404 | Not Found | Check webhook URL/workflow active |
| 500 | Server Error | Review n8n logs |

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-11  
**Author:** GitHub Copilot (Playwright Planner Agent)  
**Status:** ✅ Complete
