# DDN AI Workflows - Complete System

## 📋 Overview

This folder contains **3 n8n workflows** that work together to provide:
- ✅ Automatic analysis of aging test failures
- ✅ Manual on-demand analysis from dashboard
- ✅ User feedback and solution refinement

---

## 🔄 Workflow Files

### **1. `workflow_1_auto_trigger.json`**
**Purpose**: Automatic analysis via Jenkins webhook

**Trigger**: Jenkins sends webhook when test fails
**Conditions**:
- Failure must be >= 5 days old (aging threshold)
- OR marked as "high priority" in Jenkins

**Flow**:
```
Jenkins Webhook → Check Aging → Classify → Route (RAG/MCP) → Store → Teams Notification
```

**Use Case**: Daily automated analysis of persistent failures

---

### **2. `workflow_2_manual_trigger.json`**
**Purpose**: On-demand analysis from dashboard

**Trigger**: User clicks "Analyze Now" button on dashboard
**Conditions**:
- No aging requirement
- Works for ANY build_id

**Flow**:
```
Dashboard API → Get Build Data → Classify → Route (RAG/MCP) → Store → Return to Dashboard
```

**Use Case**: QA engineer wants immediate analysis of recent failure

---

### **3. `workflow_3_refinement.json`**
**Purpose**: Re-analyze with user feedback

**Trigger**: User provides feedback on existing analysis
**Conditions**:
- Must have existing analysis
- User feedback text required

**Flow**:
```
Dashboard API → Get Original Analysis → Append User Feedback →
Force MCP Analysis → Update Solution → Return to Dashboard
```

**Use Case**: AI analysis was incorrect, user provides context for better result

---

## 🚀 Import Instructions

### **Step 1: Import All 3 Workflows**

```bash
# In n8n UI:
1. Go to Workflows
2. Click "Import from File"
3. Select workflow_1_auto_trigger.json
4. Repeat for workflow_2 and workflow_3
```

### **Step 2: Configure Credentials**

Each workflow needs:
- **MongoDB**: Connection to builds database
- **Anthropic API**: Claude API key
- **Teams Webhook**: Microsoft Teams notification URL

### **Step 3: Activate Workflows**

```bash
# Activate all 3:
- workflow_1_auto_trigger: Toggle "Active"
- workflow_2_manual_trigger: Toggle "Active"
- workflow_3_refinement: Toggle "Active"
```

### **Step 4: Get Webhook URLs**

```bash
# Copy webhook URLs from each workflow:
Workflow 1: https://n8n.your-domain.com/webhook/ddn-auto-trigger
Workflow 2: https://n8n.your-domain.com/webhook/ddn-manual-trigger
Workflow 3: https://n8n.your-domain.com/webhook/ddn-refinement
```

---

## 🔗 Integration with Dashboard

### **Dashboard → Manual Trigger**

```javascript
// When user clicks "Analyze Now" button
async function triggerManualAnalysis(buildId) {
  const response = await fetch('https://n8n.your-domain.com/webhook/ddn-manual-trigger', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      build_id: buildId,
      triggered_by: 'dashboard',
      user_email: currentUser.email
    })
  });

  const result = await response.json();
  // Display result in dashboard
  showAnalysisModal(result.data);
}
```

### **Dashboard → Refinement Trigger**

```javascript
// When user provides feedback
async function refineSolution(buildId, userFeedback) {
  const response = await fetch('https://n8n.your-domain.com/webhook/ddn-refinement', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      build_id: buildId,
      user_feedback: userFeedback,
      user_email: currentUser.email,
      additional_context: {
        check_recent_commits: true,
        include_config_files: true
      }
    })
  });

  const updatedResult = await response.json();
  // Update analysis display
  updateAnalysisView(updatedResult.data);
}
```

---

## 📊 Workflow Comparison

| Feature | Auto-Trigger | Manual Trigger | Refinement |
|---------|-------------|----------------|------------|
| **Trigger Source** | Jenkins webhook | Dashboard button | Dashboard feedback |
| **Aging Required** | Yes (5+ days) | No | No |
| **Can Use RAG** | Yes (80%) | Yes (80%) | No (always MCP) |
| **Returns to** | Teams | Dashboard | Dashboard |
| **User Input** | None | Build ID only | Build ID + Feedback |
| **Response Time** | 5-15 sec | 5-15 sec | 15-20 sec |
| **Cost** | $0.01-$0.08 | $0.01-$0.08 | $0.08-$0.15 |

---

## 🔍 Workflow Details

### **Auto-Trigger Workflow**

**Nodes**: 14
- Webhook (Jenkins)
- Aging Check (filter)
- Extract Data
- MongoDB Query
- LangGraph Classification
- Routing Decision
- RAG Solution (fast path)
- Claude MCP (deep path)
- Parse Response
- Merge Paths
- Store MongoDB
- Store Pinecone
- Teams Notification
- Response

### **Manual Trigger Workflow**

**Nodes**: 13 (same as auto, minus aging check)
- Webhook (Dashboard)
- Validate Request
- Extract Data
- MongoDB Query
- LangGraph Classification
- Routing Decision
- RAG Solution
- Claude MCP
- Parse Response
- Merge Paths
- Store MongoDB
- Store Pinecone
- Return to Dashboard (JSON response)

### **Refinement Workflow**

**Nodes**: 11
- Webhook (Dashboard)
- Validate Request
- Get Original Analysis (MongoDB)
- Merge User Feedback
- Force Claude MCP Analysis (no RAG)
- Parse Enhanced Response
- Update MongoDB (add to history)
- Store Pinecone (new version)
- Log Refinement Event
- Notify Original Analyzer (optional)
- Return Enhanced Solution

---

## 🎯 Expected Outcomes

### **Successful Auto-Trigger**
```json
{
  "status": "success",
  "workflow": "auto-trigger",
  "data": {
    "build_id": "12345",
    "error_category": "INFRA_ERROR",
    "analysis_type": "RAG_RETRIEVAL",
    "confidence": 0.95,
    "processing_time_ms": 5000,
    "cost_usd": 0.01,
    "notification_sent": true
  }
}
```

### **Successful Manual Trigger**
```json
{
  "status": "success",
  "workflow": "manual-trigger",
  "data": {
    "build_id": "12346",
    "error_category": "CODE_ERROR",
    "analysis_type": "CLAUDE_MCP_ANALYSIS",
    "root_cause": "NullPointerException at...",
    "fix_recommendation": "Add null check...",
    "github_link": "https://github.com/org/repo/blob/main/src/DDNStorage.java#L127",
    "jenkins_link": "https://jenkins.com/job/12346",
    "confidence": 0.92,
    "processing_time_ms": 15000,
    "cost_usd": 0.08
  }
}
```

### **Successful Refinement**
```json
{
  "status": "success",
  "workflow": "refinement",
  "data": {
    "build_id": "12345",
    "refinement_version": 2,
    "original_analysis": {
      "error_category": "CODE_ERROR",
      "root_cause": "NullPointerException..."
    },
    "refined_analysis": {
      "error_category": "CONFIG_ERROR",
      "root_cause": "Configuration path not set...",
      "user_feedback_incorporated": true
    },
    "confidence_improvement": "+15%",
    "processing_time_ms": 18000,
    "cost_usd": 0.12
  }
}
```

---

## 🛡️ Error Handling

All workflows include:
- ✅ Timeout protection (max 2 minutes)
- ✅ Retry logic for API failures
- ✅ `continueOnFail` for non-critical nodes
- ✅ Error logging to MongoDB
- ✅ Fallback to basic analysis if MCP fails

---

## 📈 Monitoring

### **Check Workflow Health**

```bash
# Query n8n API
curl https://n8n.your-domain.com/api/v1/executions \
  -H "X-N8N-API-KEY: your-api-key"

# Check success rate by workflow
SELECT
  workflow_name,
  COUNT(*) as total_runs,
  SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as successes,
  AVG(execution_time_ms) as avg_time_ms
FROM executions
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY workflow_name;
```

---

## 🔧 Customization

### **Change Aging Threshold**

Edit `workflow_1_auto_trigger.json` → Node "Aging Check":

```javascript
// Change from 5 days to 7 days
const agingThreshold = 7; // days
const failureDate = new Date($json.timestamp);
const daysSinceFailure = (Date.now() - failureDate) / (1000 * 60 * 60 * 24);

return daysSinceFailure >= agingThreshold;
```

### **Add Custom Routing Logic**

Edit any workflow → Node "Routing Decision":

```javascript
// Add custom condition: Always use MCP for specific jobs
const alwaysUseMCP = [
  'Critical-Security-Tests',
  'Production-Smoke-Tests'
];

if (alwaysUseMCP.includes($json.job_name)) {
  return { needs_code_analysis: true };
}

// Otherwise use classification result
return { needs_code_analysis: $json.needs_code_analysis };
```

---

## 📞 Support

**Issues with workflows?**
1. Check n8n execution logs (Click workflow → Executions)
2. Verify all Python services are running
3. Check credential configuration
4. Review error logs in MongoDB

**Need help?**
Contact: dev-team@your-company.com

---

**Last Updated**: October 21, 2025
**Version**: 2.0.0
