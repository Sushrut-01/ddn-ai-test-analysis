# Task 0F.5: Import Workflows to n8n

**Status:** Ready for Implementation
**Priority:** CRITICAL
**Time:** 1 hour
**Prerequisites:** n8n service running on http://localhost:5678

---

## Overview

Import the three updated dual-index workflows into n8n and test each end-to-end.

## Updated Workflow Files

All three workflows have been updated to v2.1.0 with:
- **Dual-Index RAG**: Queries both `ddn-knowledge-docs` and `ddn-error-library`
- **OPTION C Routing**: All CODE_ERROR → Deep Analysis (Gemini+GitHub)
- **Updated Metadata**: Version 2.1.0-dual-index-option-c

### Files Ready for Import

1. **Auto-Trigger Workflow**
   - File: `implementation/workflows/ddn_ai_complete_workflow_v2.json`
   - Backup: `implementation/workflows/ddn_ai_complete_workflow_v2.json.backup-2025-11-05`
   - Version: 2.1.0
   - Description: Complete test failure analysis with dual-index RAG

2. **Manual Trigger Workflow**
   - File: `implementation/workflows/workflow_2_manual_trigger.json`
   - Backup: `implementation/workflows/workflow_2_manual_trigger.json.backup-2025-11-05`
   - Version: 2.1.0
   - Description: On-demand analysis from dashboard with dual-index RAG

3. **Refinement Workflow**
   - File: `implementation/workflows/workflow_3_refinement.json`
   - Backup: `implementation/workflows/workflow_3_refinement.json.backup-2025-11-05`
   - Version: 2.1.0
   - Description: User feedback refinement with dual-index RAG

---

## Step-by-Step Import Process

### Prerequisites Check

```bash
# 1. Verify n8n is running
curl http://localhost:5678/healthz

# Expected: HTTP 200 OK

# 2. Verify workflow files exist
ls -l implementation/workflows/*.json

# Expected: See all 3 workflow files
```

### Step 1: Start n8n Service (if not running)

```bash
# Option A: If n8n installed globally
n8n start

# Option B: If using Docker
docker-compose up n8n

# Option C: If using npm
cd path/to/n8n
npm start
```

**Verify n8n is accessible:**
- Open browser: http://localhost:5678
- You should see n8n UI

---

### Step 2: Import Auto-Trigger Workflow

1. **Navigate to n8n UI:**
   - Open: http://localhost:5678
   - Click: "Workflows" in sidebar

2. **Import Workflow:**
   - Click: "Add workflow" dropdown → "Import from file"
   - Select file: `implementation/workflows/ddn_ai_complete_workflow_v2.json`
   - Click: "Import"

3. **Configure Workflow:**
   - **Name**: Keep as "DDN AI Complete Workflow - Dual-Index RAG v2.1"
   - **Active**: Toggle ON (if ready to use)
   - **Webhook URL**: Copy the webhook URL (will be something like `http://localhost:5678/webhook/ddn-test-failure`)

4. **Set Credentials:**
   - Click on node "3. MongoDB Extract Full Context"
   - Configure MongoDB credentials if not already set
   - Click on node "8b. Claude Deep Analysis"
   - Configure Anthropic API credentials if not already set

5. **Test Workflow:**
   - Click: "Execute Workflow" button
   - Provide test payload:
   ```json
   {
     "build_id": "test-123",
     "build_url": "http://jenkins.local/job/test/123",
     "job_name": "EXAScaler-Test",
     "timestamp": "2025-11-05T10:00:00Z"
   }
   ```
   - Verify all nodes execute successfully
   - Check routing logic works (node 7 splits correctly)

6. **Save and Document:**
   - Click: "Save" button
   - Copy Workflow ID from URL (e.g., `/workflow/abc123def456`)
   - Document webhook URL for integration

---

### Step 3: Import Manual Trigger Workflow

1. **Import:**
   - Click: "Add workflow" → "Import from file"
   - Select: `implementation/workflows/workflow_2_manual_trigger.json`

2. **Configure:**
   - **Name**: "DDN AI - Manual Trigger from Dashboard (Dual-Index)"
   - **Webhook URL**: Copy (e.g., `http://localhost:5678/webhook/ddn-manual-trigger`)

3. **Set Credentials:**
   - Configure MongoDB credentials (node 3)
   - Configure Anthropic API (node 7b)

4. **Test:**
   ```json
   {
     "build_id": "12345",
     "triggered_by": "dashboard",
     "user_email": "test@example.com"
   }
   ```

5. **Save and Document:**
   - Save workflow
   - Copy Workflow ID
   - Update `dashboard_api_full.py` with webhook URL (if needed)

---

### Step 4: Import Refinement Workflow

1. **Import:**
   - Click: "Add workflow" → "Import from file"
   - Select: `implementation/workflows/workflow_3_refinement.json`

2. **Configure:**
   - **Name**: "DDN AI - Solution Refinement with User Feedback (Dual-Index)"
   - **Webhook URL**: Copy (e.g., `http://localhost:5678/webhook/ddn-refinement`)

3. **Set Credentials:**
   - Configure MongoDB credentials
   - Configure Anthropic API

4. **Test:**
   ```json
   {
     "build_id": "12345",
     "user_feedback": "The fix didn't work, still seeing timeout errors in production",
     "user_email": "developer@example.com"
   }
   ```

5. **Save and Document:**
   - Save workflow
   - Copy Workflow ID

---

### Step 5: Update Configuration Files

After importing all workflows, update configuration to use new webhook URLs:

1. **Update .env files:**
   ```bash
   # Add to .env.MASTER, .env, implementation/.env
   N8N_WEBHOOK_AUTO_TRIGGER=http://localhost:5678/webhook/ddn-test-failure
   N8N_WEBHOOK_MANUAL_TRIGGER=http://localhost:5678/webhook/ddn-manual-trigger
   N8N_WEBHOOK_REFINEMENT=http://localhost:5678/webhook/ddn-refinement
   ```

2. **Update dashboard API:**
   - File: `implementation/manual_trigger_api.py`
   - Update webhook URLs to point to n8n

---

### Step 6: End-to-End Testing

Test each workflow with real data:

#### Test 1: Auto-Trigger Workflow
```bash
# Trigger from Jenkins webhook
curl -X POST http://localhost:5678/webhook/ddn-test-failure \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "BUILD-456",
    "build_url": "http://jenkins/job/tests/456",
    "job_name": "EXAScaler-Nightly",
    "status": "FAILURE"
  }'

# Expected:
# - Workflow executes
# - MongoDB queried for full context
# - LangGraph ReAct agent classifies error (dual-index)
# - Routes to correct path (8a or 8b based on OPTION C)
# - Solution stored in MongoDB
# - Pinecone updated
# - Teams notification sent
# - HTTP 200 response
```

#### Test 2: Manual Trigger Workflow
```bash
# Trigger from dashboard
curl -X POST http://localhost:5678/webhook/ddn-manual-trigger \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "BUILD-456",
    "triggered_by": "dashboard",
    "user_email": "qa@example.com"
  }'

# Expected:
# - Workflow validates request
# - MongoDB queried for build
# - Analysis runs with dual-index RAG
# - Returns detailed solution with GitHub/Jenkins links
# - HTTP 200 with full analysis
```

#### Test 3: Refinement Workflow
```bash
# Trigger refinement with feedback
curl -X POST http://localhost:5678/webhook/ddn-refinement \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "BUILD-456",
    "user_feedback": "This solution was partially helpful but missed the configuration file issue",
    "user_email": "developer@example.com"
  }'

# Expected:
# - Original analysis retrieved from MongoDB
# - User feedback merged with context
# - Claude re-analyzes with enhanced context
# - Refinement history updated
# - New solution version stored
# - HTTP 200 with refined solution
```

---

## Verification Checklist

After completing all imports, verify:

- [ ] All 3 workflows visible in n8n UI
- [ ] All workflows have status "Active" (if ready to use)
- [ ] MongoDB credentials configured correctly
- [ ] Anthropic API credentials configured correctly
- [ ] Webhook URLs documented and accessible
- [ ] OPTION C routing works (CODE_ERROR goes to deep analysis)
- [ ] Dual-index RAG queries both Pinecone indexes
- [ ] All test payloads execute successfully
- [ ] Error handling works (try invalid build_id)
- [ ] Configuration files updated with webhook URLs
- [ ] Teams notifications working (if configured)
- [ ] Dashboard integration working (manual trigger)

---

## Workflow IDs Documentation

After import, document the workflow IDs here:

```
AUTO_TRIGGER_WORKFLOW_ID: __________________
MANUAL_TRIGGER_WORKFLOW_ID: __________________
REFINEMENT_WORKFLOW_ID: __________________

AUTO_TRIGGER_WEBHOOK: http://localhost:5678/webhook/ddn-test-failure
MANUAL_TRIGGER_WEBHOOK: http://localhost:5678/webhook/ddn-manual-trigger
REFINEMENT_WEBHOOK: http://localhost:5678/webhook/ddn-refinement
```

---

## Troubleshooting

### Issue: "Workflow import failed"
**Solution:**
- Verify JSON is valid: `python -m json.tool workflow.json`
- Check n8n version compatibility (requires v1.0.0+)
- Try importing via CLI: `n8n import:workflow --input=workflow.json`

### Issue: "MongoDB connection failed"
**Solution:**
- Verify MongoDB is running: `mongo --eval "db.adminCommand('ping')"`
- Check credentials in n8n settings
- Update connection string in n8n credentials manager

### Issue: "Anthropic API error"
**Solution:**
- Verify API key is valid
- Check API key has sufficient credits
- Verify MCP server URLs are accessible: `curl http://localhost:5002/health`

### Issue: "OPTION C routing not working"
**Solution:**
- Check node 7 condition logic: `error_category === 'CODE_ERROR'`
- Verify LangGraph service returns `error_category` field
- Test classification endpoint: `curl http://localhost:5000/analyze-error`

### Issue: "Dual-index queries not working"
**Solution:**
- Verify both Pinecone indexes exist: `ddn-knowledge-docs` and `ddn-error-library`
- Check LangGraph agent tool registry: `tool_registry.py` has both indexes configured
- Test Pinecone connection: `python implementation/test_dual_index_rag.py`

---

## Next Steps

After completing Task 0F.5:

1. **Task 0F.6**: Create `aging_service.py` with APScheduler
   - Automatically triggers analysis for old unanalyzed failures
   - Runs every 6 hours
   - Calls n8n auto-trigger webhook

2. **Task 0F.11**: Update GitHub MCP configuration
   - Point to new test data repository
   - Test GitHub file fetching

3. **Integration Testing**:
   - Run full end-to-end tests with real Jenkins data
   - Monitor Teams notifications
   - Verify dashboard shows analysis results

---

## Success Criteria

Task 0F.5 is complete when:

✅ All 3 workflows imported successfully
✅ All workflows active and tested
✅ OPTION C routing verified (CODE_ERROR → deep analysis)
✅ Dual-index RAG confirmed (queries both Pinecone indexes)
✅ Webhook URLs documented
✅ Configuration files updated
✅ End-to-end tests pass
✅ Dashboard integration works
✅ Error handling verified
✅ Credentials configured

---

**File Created:** 2025-11-05
**Status:** Ready for Implementation
**Next Task:** 0F.6 - Create aging_service.py
