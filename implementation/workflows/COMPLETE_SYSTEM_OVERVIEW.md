# 🚀 Complete DDN AI System - Dashboard-Centric Architecture

**Version**: 2.0.0
**Date**: October 21, 2025
**Purpose**: Complete guide to the dashboard-integrated n8n workflow system

---

## 📊 System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER DASHBOARD                            │
│  (React Frontend - Displays failures, triggers analysis)         │
└────────────┬─────────────────────────────────┬───────────────────┘
             │                                 │
             │ Manual Trigger                  │ Refinement Request
             │ (Analyze Now)                   │ (User Feedback)
             ▼                                 ▼
┌────────────────────────┐      ┌─────────────────────────────────┐
│   N8N WORKFLOW 2       │      │     N8N WORKFLOW 3              │
│   Manual Trigger       │      │     Refinement                  │
│   (12 nodes)           │      │     (12 nodes)                  │
└────────┬───────────────┘      └──────────┬──────────────────────┘
         │                                 │
         │ Calls                           │ Calls
         ▼                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                   LANGGRAPH SERVICE (Port 5000)                   │
│   - Error classification                                          │
│   - RAG search (Pinecone)                                         │
│   - Route decision (RAG vs MCP)                                   │
└────────┬────────────────────────────────────────────┬────────────┘
         │                                            │
    80% (RAG)                                    20% (MCP)
         │                                            │
         ▼                                            ▼
  ┌────────────┐                        ┌─────────────────────────┐
  │ Quick      │                        │  Claude API + MCP       │
  │ Solution   │                        │  - MongoDB MCP (5001)   │
  │ (5 sec)    │                        │  - GitHub MCP (5002)    │
  │ $0.01      │                        │  - Deep Analysis        │
  └────────────┘                        │  (15 sec, $0.08)        │
                                        └───────────┬─────────────┘
                                                    │
         ┌──────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   MongoDB    │  │   Pinecone   │  │  PostgreSQL  │          │
│  │  (Solutions) │  │  (RAG Index) │  │  (Metadata)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│              NOTIFICATIONS & RESPONSE                             │
│  ┌────────────────────┐         ┌──────────────────────┐        │
│  │  Microsoft Teams   │         │  Dashboard API       │        │
│  │  (Auto-trigger)    │         │  (JSON Response)     │        │
│  └────────────────────┘         └──────────────────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Three Workflow System

### **Workflow 1: Auto-Trigger** (Jenkins → n8n)
**File**: `workflow_1_auto_trigger.json` (use the existing one from your [ddn_ai_complete_workflow.json](ddn_ai_complete_workflow.json))

**Purpose**: Automatic analysis of aging test failures
**Trigger**: Jenkins webhook when test fails
**Conditions**: Failure >= 5 days old OR high priority
**Output**: Teams notification

**When to use**: Daily batch processing of persistent failures

---

### **Workflow 2: Manual Trigger** (Dashboard → n8n)
**File**: [workflow_2_manual_trigger.json](workflow_2_manual_trigger.json)

**Purpose**: On-demand analysis from dashboard
**Trigger**: User clicks "Analyze Now" button
**Conditions**: None (works for any build_id)
**Output**: JSON response to dashboard

**When to use**: User wants immediate analysis of recent failure

**Dashboard Code Example**:
```javascript
async function analyzeNow(buildId) {
  const response = await fetch('https://n8n.com/webhook/ddn-manual-trigger', {
    method: 'POST',
    body: JSON.stringify({ build_id: buildId, user_email: user.email })
  });
  const result = await response.json();
  showAnalysisModal(result.data); // Display in dashboard
}
```

---

### **Workflow 3: Refinement** (Dashboard → n8n)
**File**: [workflow_3_refinement.json](workflow_3_refinement.json)

**Purpose**: Re-analyze with user feedback
**Trigger**: User provides feedback on existing analysis
**Conditions**: Must have existing analysis
**Output**: Enhanced JSON response with refinement history

**When to use**: AI analysis was incorrect, user has domain knowledge

**Dashboard Code Example**:
```javascript
async function refineSolution(buildId, feedback) {
  const response = await fetch('https://n8n.com/webhook/ddn-refinement', {
    method: 'POST',
    body: JSON.stringify({
      build_id: buildId,
      user_feedback: feedback,
      user_email: user.email,
      additional_context: {
        check_recent_commits: true,
        include_config_files: true
      }
    })
  });
  const refined = await response.json();
  updateAnalysisView(refined.data); // Update dashboard
}
```

---

## 📁 File Structure

```
implementation/
├── workflows/
│   ├── README.md                              ← Workflow overview
│   ├── COMPLETE_SYSTEM_OVERVIEW.md            ← This file
│   ├── ddn_ai_complete_workflow.json          ← Workflow 1 (auto-trigger)
│   ├── workflow_2_manual_trigger.json         ← Workflow 2 (dashboard)
│   └── workflow_3_refinement.json             ← Workflow 3 (refinement)
│
├── dashboard/
│   └── DASHBOARD_INTEGRATION_GUIDE.md         ← Dashboard integration
│
├── langgraph_agent.py                         ← Classification service
├── requirements.txt                           ← Python dependencies
└── .env.example                               ← Environment variables

mcp-configs/
├── mcp_mongodb_server.py                      ← TODO: MongoDB MCP
├── mcp_github_server.py                       ← TODO: GitHub MCP
└── pinecone_storage_service.py                ← TODO: Pinecone service
```

---

## 🎯 Key Features

### **1. Dashboard Integration**
✅ Manual trigger for any failure (no aging requirement)
✅ Real-time JSON response with analysis
✅ Direct GitHub links (file:line clickable)
✅ Direct Jenkins build links
✅ Refinement with user feedback
✅ Refinement history tracking

### **2. Intelligent Routing**
✅ 80% use RAG (fast, cheap: $0.01, 5 sec)
✅ 20% use MCP (deep, accurate: $0.08, 15 sec)
✅ Classification by LangGraph
✅ Similar solution search

### **3. User Feedback Loop**
✅ "Not Satisfied?" button in dashboard
✅ User provides context/correction
✅ Claude re-analyzes with feedback
✅ Tracks refinement versions
✅ Updates original solution

### **4. GitHub Integration**
✅ Exact file:line URLs
✅ Opens in new tab from dashboard
✅ Supports multiple files per analysis
✅ Git blame information (optional)

---

## 📊 Workflow Comparison

| Feature | Auto-Trigger | Manual Trigger | Refinement |
|---------|-------------|----------------|------------|
| **Import File** | `ddn_ai_complete_workflow.json` | `workflow_2_manual_trigger.json` | `workflow_3_refinement.json` |
| **Webhook Path** | `/ddn-test-failure` | `/ddn-manual-trigger` | `/ddn-refinement` |
| **Trigger Source** | Jenkins | Dashboard | Dashboard |
| **Aging Required** | Yes (5+ days) | No | No |
| **User Input** | None | Build ID only | Build ID + Feedback |
| **Can Use RAG** | Yes | Yes | No (always MCP) |
| **Returns To** | Teams | Dashboard (JSON) | Dashboard (JSON) |
| **Response Time** | 5-15 sec | 5-15 sec | 15-20 sec |
| **Cost Range** | $0.01-$0.08 | $0.01-$0.08 | $0.08-$0.15 |
| **Nodes Count** | 13 | 12 | 12 |

---

## 🚀 Quick Start Guide

### **Step 1: Import Workflows into n8n**

```bash
# 1. Open n8n dashboard (http://localhost:5678)
# 2. Click "Workflows" → "Import from File"
# 3. Import these 3 files:
#    - ddn_ai_complete_workflow.json (or workflow_1_auto_trigger.json)
#    - workflow_2_manual_trigger.json
#    - workflow_3_refinement.json
```

### **Step 2: Configure Credentials**

Each workflow needs:
- **MongoDB**: Connection string (`mongodb://localhost:27017/ddn`)
- **Anthropic API**: API key (`sk-ant-...`)
- **Teams Webhook**: URL (`https://outlook.office.com/webhook/...`)

### **Step 3: Start Python Services**

```bash
# Terminal 1: LangGraph Classification
cd implementation
python langgraph_agent.py
# Runs on http://localhost:5000

# Terminal 2: MongoDB MCP Server (TODO: create this)
cd mcp-configs
python mcp_mongodb_server.py
# Runs on http://localhost:5001

# Terminal 3: GitHub MCP Server (TODO: create this)
cd mcp-configs
python mcp_github_server.py
# Runs on http://localhost:5002

# Terminal 4: Pinecone Service (TODO: create this)
cd mcp-configs
python pinecone_storage_service.py
# Runs on http://localhost:5003
```

### **Step 4: Activate Workflows**

```bash
# In n8n UI, activate all 3 workflows:
- Workflow 1 (Auto-Trigger): Toggle "Active" ON
- Workflow 2 (Manual Trigger): Toggle "Active" ON
- Workflow 3 (Refinement): Toggle "Active" ON
```

### **Step 5: Get Webhook URLs**

```bash
# Click each workflow, copy Production URL:
Workflow 1: https://n8n.your-domain.com/webhook/ddn-test-failure
Workflow 2: https://n8n.your-domain.com/webhook/ddn-manual-trigger
Workflow 3: https://n8n.your-domain.com/webhook/ddn-refinement
```

### **Step 6: Configure Dashboard**

```javascript
// In your React dashboard config:
const N8N_CONFIG = {
  manualTrigger: 'https://n8n.your-domain.com/webhook/ddn-manual-trigger',
  refinement: 'https://n8n.your-domain.com/webhook/ddn-refinement'
};
```

### **Step 7: Test the Flow**

```bash
# Test Manual Trigger:
curl -X POST https://n8n.your-domain.com/webhook/ddn-manual-trigger \
  -H "Content-Type: application/json" \
  -d '{"build_id": "12345", "user_email": "test@example.com"}'

# Expected: JSON response with analysis in 5-15 seconds

# Test Refinement:
curl -X POST https://n8n.your-domain.com/webhook/ddn-refinement \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "12345",
    "user_feedback": "This is actually a config issue, not code",
    "user_email": "test@example.com",
    "additional_context": {"include_config_files": true}
  }'

# Expected: JSON response with refined analysis in 15-20 seconds
```

---

## 🎨 Dashboard Integration Points

### **1. Failure List Page**

```
┌─────────────────────────────────────────────────────────────┐
│  Test Failures Dashboard                                    │
├─────────────────────────────────────────────────────────────┤
│  Filters: [Aging >= 3 days ▼] [Job: All ▼] [Status: All ▼] │
├──────┬──────────────┬─────────┬──────────────┬──────────────┤
│ Build│ Job Name     │ Aging   │ Status       │ Actions      │
├──────┼──────────────┼─────────┼──────────────┼──────────────┤
│ 12345│ DDN-Smoke    │ 8 days  │ 🟢 Analyzed  │ [View][Re-run]│
│ 12346│ DDN-Smoke    │ 2 days  │ ⚪ Not Yet   │ [Analyze Now]│← Click
│ 12347│ DDN-Integr.  │ 10 days │ 🟢 Analyzed  │ [View][Re-run]│
└──────┴──────────────┴─────────┴──────────────┴──────────────┘
```

**When user clicks "Analyze Now"**:
→ Calls Workflow 2 (Manual Trigger)
→ Shows loading spinner
→ Opens modal with results

### **2. Analysis Details Modal**

```
┌───────────────────────────────────────────────────────────────┐
│  Analysis Details - Build 12346                          [X]  │
├───────────────────────────────────────────────────────────────┤
│  [🔧 View in Jenkins] [📂 GitHub Repo]                        │
│                                                               │
│  Category: CODE_ERROR     Confidence: 92%    Type: MCP        │
├───────────────────────────────────────────────────────────────┤
│  📝 Root Cause:                                               │
│  NullPointerException at DDNStorage.java:127                  │
│  Missing null check for storageConfig object                  │
│                                                               │
│  💡 Recommended Fix:                                          │
│  Add null validation before accessing storageConfig...        │
│                                                               │
│  📁 Related Files:                                            │
│  ├─ src/main/java/DDNStorage.java:127  [View in GitHub →]    │← Opens exact line
│  └─ src/test/java/DDNStorageTest.java:45  [View in GitHub →] │
│                                                               │
│  ❌ Not Satisfied?                                            │
│  [💬 Provide Feedback & Re-analyze]                           │← Opens feedback form
└───────────────────────────────────────────────────────────────┘
```

**When user clicks "Provide Feedback"**:
→ Shows textarea for feedback
→ Calls Workflow 3 (Refinement)
→ Updates modal with refined analysis

### **3. Feedback Modal**

```
┌───────────────────────────────────────────────────────────────┐
│  Why are you not satisfied?                                   │
├───────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ This is not a code issue. It's actually a               │ │
│  │ configuration problem with the storage path setup.      │ │
│  │ Please check the app.properties file.                   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  Additional Context:                                          │
│  ☐ Check recent commits (last 7 days)                        │
│  ☐ Check related test files                                  │
│  ☑ Include configuration files                               │
│                                                               │
│          [Cancel]  [Re-analyze with Feedback]                 │
└───────────────────────────────────────────────────────────────┘
```

**Result**: Updated analysis with new category and evidence

---

## 💡 Example User Journey

### **Scenario**: QA Engineer finds a failure that doesn't meet aging criteria but needs immediate attention

```
1. Opens Dashboard
   └─> Sees "Build 12346, 2 days old, Not Analyzed"

2. Clicks "Analyze Now"
   └─> Workflow 2 triggers
   └─> LangGraph: "CODE_ERROR, needs_code_analysis: true"
   └─> Claude MCP: Fetches MongoDB + GitHub
   └─> Response in 15 seconds

3. Modal Opens:
   └─> Root Cause: "NullPointerException at DDNStorage.java:127"
   └─> Fix: "Add null check..."
   └─> GitHub Link: https://github.com/org/repo/blob/main/src/main/java/DDNStorage.java#L127

4. Clicks GitHub Link:
   └─> Opens in new tab
   └─> Sees exact code at line 127
   └─> Reviews code: "Wait, this is not a null issue, it's a config issue!"

5. Goes back to dashboard, clicks "Not Satisfied?"
   └─> Enters feedback: "This is a config issue, check app.properties"
   └─> Checks "Include configuration files"
   └─> Clicks "Re-analyze"

6. Workflow 3 (Refinement) runs:
   └─> Claude reads feedback
   └─> Fetches app.properties file
   └─> Discovers missing storage.path property
   └─> Response in 18 seconds

7. Modal Updates:
   └─> Refinement Summary: "Re-classified from CODE_ERROR to CONFIG_ERROR"
   └─> New Root Cause: "Missing storage.path in app.properties"
   └─> New Fix: "Add storage.path=/var/lib/ddn/storage"
   └─> Evidence: ["Config missing property", "Code expects non-null"]
   └─> GitHub Links: [app.properties:45, DDNStorage.java:127]

8. QA Engineer satisfied:
   └─> Applies config fix
   └─> Problem resolved
   └─> Solution stored for future RAG
```

---

## 🎯 Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Manual Trigger Response Time** | < 20 sec | n8n execution logs |
| **Refinement Accuracy** | > 90% | User satisfaction survey |
| **GitHub Link Accuracy** | 100% | Manual spot checks |
| **Cost per Analysis** | < $0.15 | MongoDB cost tracking |
| **User Adoption** | > 70% | Dashboard analytics |

---

## 📞 Support & Troubleshooting

### **Common Issues**:

**Issue**: "Analyze Now" returns 404
- **Fix**: Check workflow is activated in n8n
- **Fix**: Verify webhook URL is correct

**Issue**: GitHub links don't work
- **Fix**: Verify `repository` field in MongoDB
- **Fix**: Check branch name (default is 'main')

**Issue**: Refinement returns "No existing analysis"
- **Fix**: Run manual analysis first
- **Fix**: Check MongoDB for analysis_solutions document

**Issue**: Response too slow (> 30 sec)
- **Fix**: Check Python services are running
- **Fix**: Verify MCP server health endpoints
- **Fix**: Review Claude API rate limits

---

## 🔮 Future Enhancements

- [ ] Real-time websocket updates (show analysis progress)
- [ ] Batch analysis (analyze multiple failures at once)
- [ ] Auto-apply fixes (create PR automatically)
- [ ] Integration with Slack/Discord
- [ ] Mobile dashboard app
- [ ] AI confidence calibration over time
- [ ] Advanced filtering (by error pattern, code author, etc.)

---

**Last Updated**: October 21, 2025
**Maintained By**: Development Team
**Questions?**: Contact dev-team@your-company.com

---

## ✅ Checklist for Go-Live

- [ ] All 3 workflows imported into n8n
- [ ] Credentials configured (MongoDB, Anthropic, Teams)
- [ ] All 4 Python services running and healthy
- [ ] Webhook URLs configured in dashboard
- [ ] Test data available in MongoDB
- [ ] Manual trigger tested successfully
- [ ] Refinement flow tested successfully
- [ ] GitHub links verified working
- [ ] Jenkins links verified working
- [ ] User training completed
- [ ] Documentation reviewed by team
- [ ] Monitoring dashboards set up
- [ ] Error alerting configured
- [ ] Backup strategy in place

---

**🎉 You're ready to go live!**
