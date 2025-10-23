# Complete Setup Checklist - DDN AI Project

**Your Complete Guide to Setting Up the Dashboard-Centric DDN AI System**

---

## 📋 Overview

You now have a complete system with:
- ✅ **3 n8n workflows** (Auto-trigger, Manual trigger, Refinement)
- ✅ **MongoDB integration** (Database structure, sample data)
- ✅ **Dashboard integration guide** (React components, API calls)
- ✅ **Complete documentation** (Setup guides, architecture diagrams)

---

## 🎯 Current Status

### **✅ What You Already Have:**
- MongoDB v7.0.4 running on `localhost:27017`
- Data directory: `C:\DDN-Project\mongodb-data`
- LangGraph agent code: [langgraph_agent.py](implementation/langgraph_agent.py)
- n8n workflow files (3 JSON files)

### **📝 What You Need to Do:**
Follow the steps below (estimated time: 30 minutes)

---

## 🚀 Step-by-Step Setup

### **PHASE 1: Database Setup (10 minutes)**

#### ✅ **Step 1: Create MongoDB Database**

```bash
# 1. Navigate to database folder
cd C:\DDN-AI-Project-Documentation\implementation\database

# 2. Run setup script
python setup_mongodb.py

# Expected output: "✅ MongoDB Setup Complete!"
```

**What this does:**
- Creates database `ddn_ai_project`
- Creates 5 collections with indexes
- Inserts sample test data
- Verifies everything is working

#### ✅ **Step 2: Test MongoDB Connection**

```bash
# Run connection test
python test_mongodb_connection.py

# Expected output: "✅ ALL TESTS PASSED!"
```

**What this verifies:**
- MongoDB is accessible
- Collections exist with correct indexes
- Can read/write data
- Aggregation queries work

#### ✅ **Step 3: View Your Data (Optional)**

**Option A - MongoDB Compass (Recommended):**
```
1. Download: https://www.mongodb.com/try/download/compass
2. Connect: mongodb://localhost:27017
3. Select database: ddn_ai_project
4. Browse collections
```

**Option B - Command Line:**
```bash
mongosh mongodb://localhost:27017
use ddn_ai_project
db.builds.find().pretty()
```

**Checkpoint:** You should see 1 sample build (`SAMPLE_12345`)

---

### **PHASE 2: n8n Configuration (10 minutes)**

#### ✅ **Step 4: Start n8n**

```bash
# Start n8n (if not already running)
n8n start

# Or use existing n8n instance
# Access at: http://localhost:5678
```

#### ✅ **Step 5: Add MongoDB Credentials**

```bash
1. Open n8n: http://localhost:5678
2. Click: Settings → Credentials
3. Click: "Add Credential"
4. Select: "MongoDB"
5. Configure:
   - Name: MongoDB Production
   - Connection String: mongodb://localhost:27017/ddn_ai_project
   - Database: ddn_ai_project
6. Click: "Test Connection"
7. Click: "Save"
```

**Checkpoint:** Should see "✅ Connection successful"

#### ✅ **Step 6: Import Workflows**

```bash
# Import 3 workflows from:
C:\DDN-AI-Project-Documentation\implementation\workflows\

Files to import:
1. ddn_ai_complete_workflow.json      (Workflow 1: Auto-trigger)
2. workflow_2_manual_trigger.json     (Workflow 2: Manual)
3. workflow_3_refinement.json         (Workflow 3: Refinement)
```

**In n8n UI:**
```
1. Click: Workflows
2. Click: Import from File
3. Select: workflow_2_manual_trigger.json
4. Repeat for the other 2 files
```

#### ✅ **Step 7: Configure Workflow Credentials**

For **each** workflow (do this 3 times):

```
1. Open workflow in n8n
2. Find MongoDB nodes (have yellow warning ⚠️)
3. Click node → Select credentials → "MongoDB Production"
4. Save workflow
```

**Nodes to configure:**
- Workflow 1: Nodes 3, 9 (MongoDB operations)
- Workflow 2: Nodes 3, 10 (MongoDB operations)
- Workflow 3: Nodes 3, 5, 9, 10 (MongoDB operations)

#### ✅ **Step 8: Activate Workflows**

```
1. Open each workflow
2. Toggle "Active" switch to ON
3. Verify status shows "Active"
```

**Checkpoint:** All 3 workflows should show "Active" status

---

### **PHASE 3: Python Services (5 minutes)**

#### ✅ **Step 9: Install Python Dependencies**

```bash
# Navigate to implementation folder
cd C:\DDN-AI-Project-Documentation\implementation

# Install dependencies
pip install -r requirements.txt
```

**Key packages installed:**
- Flask (for LangGraph service)
- LangChain + LangGraph
- Anthropic (Claude API)
- OpenAI (embeddings)
- Pinecone (vector database)
- PyMongo (MongoDB)

#### ✅ **Step 10: Configure Environment Variables**

```bash
# Copy example file
copy .env.example .env

# Edit .env file
notepad .env
```

**Add these values:**
```bash
# AI Services
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
PINECONE_API_KEY=your-pinecone-key-here
PINECONE_INDEX=ddn-error-solutions

# MongoDB
MONGODB_URI=mongodb://localhost:27017/ddn_ai_project
MONGODB_DATABASE=ddn_ai_project

# Services URLs
LANGGRAPH_SERVICE_URL=http://localhost:5000
MONGODB_MCP_URL=http://localhost:5001/sse
GITHUB_MCP_URL=http://localhost:5002/sse

# GitHub
GITHUB_TOKEN=ghp_your-token-here

# Notifications
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/your-webhook

# Configuration
AGING_THRESHOLD_DAYS=5
MAX_TOKENS=8000
DEBUG=False
```

#### ✅ **Step 11: Start LangGraph Service**

```bash
# Open new terminal/command prompt
cd C:\DDN-AI-Project-Documentation\implementation

# Start service
python langgraph_agent.py
```

**Expected output:**
```
🚀 Starting DDN LangGraph Classification Service...
📍 Service will run on: http://localhost:5000
 * Running on http://0.0.0.0:5000
```

**Keep this terminal open!**

**Checkpoint:** Visit http://localhost:5000/health
Should see: `{"status": "healthy", "service": "DDN LangGraph Classification Agent"}`

---

### **PHASE 4: Testing (5 minutes)**

#### ✅ **Step 12: Test Workflow 2 (Manual Trigger)**

**Option A - Using curl:**
```bash
curl -X POST http://localhost:5678/webhook/ddn-manual-trigger ^
  -H "Content-Type: application/json" ^
  -d "{\"build_id\": \"SAMPLE_12345\", \"user_email\": \"test@example.com\"}"
```

**Option B - Using PowerShell:**
```powershell
$body = @{
    build_id = "SAMPLE_12345"
    user_email = "test@example.com"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5678/webhook/ddn-manual-trigger" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

**Expected response (after 5-15 seconds):**
```json
{
  "status": "success",
  "message": "Analysis completed successfully",
  "data": {
    "build_id": "SAMPLE_12345",
    "error_category": "CODE_ERROR",
    "confidence": 0.85,
    "root_cause": "...",
    "fix_recommendation": "...",
    "links": {
      "jenkins": "https://...",
      "github_files": [...]
    }
  }
}
```

#### ✅ **Step 13: Verify in MongoDB**

```bash
# Check analysis was stored
mongosh mongodb://localhost:27017/ddn_ai_project

# View the analysis
db.analysis_solutions.findOne()

# Should see the solution with root_cause, fix_recommendation, etc.
```

#### ✅ **Step 14: Test Workflow 3 (Refinement)**

```bash
curl -X POST http://localhost:5678/webhook/ddn-refinement ^
  -H "Content-Type: application/json" ^
  -d "{\"build_id\": \"SAMPLE_12345\", \"user_feedback\": \"This is actually a config issue, not code\", \"user_email\": \"test@example.com\"}"
```

**Expected response (after 15-20 seconds):**
```json
{
  "status": "success",
  "message": "Analysis refined successfully",
  "data": {
    "build_id": "SAMPLE_12345",
    "refinement_version": 2,
    "refinement_summary": "Re-classified based on user feedback",
    "category_changed": true,
    ...
  }
}
```

---

## ✅ Verification Checklist

Mark each item as you complete it:

### **Database:**
- [ ] MongoDB running on localhost:27017
- [ ] Database `ddn_ai_project` created
- [ ] 5 collections exist with indexes
- [ ] Sample build `SAMPLE_12345` exists
- [ ] Connection test passes

### **n8n:**
- [ ] n8n running on localhost:5678
- [ ] MongoDB credentials configured
- [ ] 3 workflows imported
- [ ] All MongoDB nodes configured with credentials
- [ ] All 3 workflows activated
- [ ] Webhook URLs accessible

### **Python Services:**
- [ ] Python dependencies installed
- [ ] .env file configured with API keys
- [ ] LangGraph service running on port 5000
- [ ] Health check endpoint responds

### **Testing:**
- [ ] Manual trigger workflow tested successfully
- [ ] Analysis stored in MongoDB
- [ ] Refinement workflow tested successfully
- [ ] Refinement history logged

---

## 📁 File Structure Reference

```
C:\DDN-AI-Project-Documentation\
│
├── README.md                              ← Project overview
├── MONGODB-QUICKSTART.md                  ← MongoDB setup (this guide)
├── COMPLETE-SETUP-CHECKLIST.md            ← Complete checklist
│
├── implementation/
│   ├── langgraph_agent.py                 ← Classification service
│   ├── requirements.txt                   ← Python dependencies
│   ├── .env.example                       ← Environment template
│   ├── .env                               ← Your config (create this)
│   │
│   ├── workflows/
│   │   ├── README.md                      ← Workflow documentation
│   │   ├── COMPLETE_SYSTEM_OVERVIEW.md    ← Architecture guide
│   │   ├── ddn_ai_complete_workflow.json  ← Workflow 1 (auto)
│   │   ├── workflow_2_manual_trigger.json ← Workflow 2 (manual)
│   │   └── workflow_3_refinement.json     ← Workflow 3 (refinement)
│   │
│   ├── dashboard/
│   │   └── DASHBOARD_INTEGRATION_GUIDE.md ← React components
│   │
│   └── database/
│       ├── mongodb-setup-guide.md         ← Detailed MongoDB guide
│       ├── setup_mongodb.py               ← Database setup script
│       ├── test_mongodb_connection.py     ← Connection test
│       └── populate_sample_data.py        ← (Optional) More data
│
└── architecture/
    └── COMPLETE-ARCHITECTURE.md           ← System architecture
```

---

## 🎯 What You Can Do Now

After completing the setup, you can:

### **1. Manual Analysis from Dashboard**

```javascript
// Frontend code (React)
async function analyzeNow(buildId) {
  const response = await fetch('http://localhost:5678/webhook/ddn-manual-trigger', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      build_id: buildId,
      user_email: currentUser.email
    })
  });

  const result = await response.json();
  // Display result in modal
  showAnalysisModal(result.data);
}
```

### **2. Refine with User Feedback**

```javascript
// Frontend code (React)
async function refineSolution(buildId, feedback) {
  const response = await fetch('http://localhost:5678/webhook/ddn-refinement', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      build_id: buildId,
      user_feedback: feedback,
      user_email: currentUser.email,
      additional_context: {
        include_config_files: true
      }
    })
  });

  const refined = await response.json();
  // Update display with refined analysis
  updateAnalysisView(refined.data);
}
```

### **3. View Results in Dashboard**

```javascript
// Display analysis with clickable links
<div>
  <h3>Root Cause:</h3>
  <p>{analysis.root_cause}</p>

  <h3>Fix Recommendation:</h3>
  <pre>{analysis.fix_recommendation}</pre>

  <h3>Related Files:</h3>
  {analysis.links.github_files.map(file => (
    <a href={file.github_url} target="_blank">
      {file.file_path}:{file.line_number}
    </a>
  ))}

  <a href={analysis.links.jenkins} target="_blank">
    View in Jenkins
  </a>
</div>
```

---

## 🛠️ Troubleshooting

### **Problem: Workflow returns 404**

**Solution:**
- Check workflow is activated (toggle "Active")
- Verify webhook URL is correct
- Check n8n is running

### **Problem: "MongoDB connection failed"**

**Solution:**
```bash
# Verify MongoDB is running
mongosh mongodb://localhost:27017 --eval "db.runCommand({ ping: 1 })"

# Check connection string in n8n includes database name:
mongodb://localhost:27017/ddn_ai_project
#                           ^^^^^^^^^^^^^^^^^ Must include this!
```

### **Problem: "LangGraph service not responding"**

**Solution:**
```bash
# Check service is running
curl http://localhost:5000/health

# If not running, start it:
cd C:\DDN-AI-Project-Documentation\implementation
python langgraph_agent.py
```

### **Problem: "No analysis returned"**

**Check:**
1. LangGraph service running on port 5000
2. MongoDB has sample data (`SAMPLE_12345`)
3. n8n workflow credentials configured
4. Check n8n execution logs for errors

---

## 📊 System Performance

**Expected metrics after setup:**

| Metric | Target | How to Verify |
|--------|--------|---------------|
| Manual trigger response | < 20 sec | Test with curl, measure time |
| MongoDB query time | < 100 ms | Check n8n execution logs |
| LangGraph classification | < 5 sec | Check service logs |
| Storage operations | < 500 ms | MongoDB logs |

---

## 🚀 Next Steps

### **Phase 5: Build Dashboard (Future)**

Use the React components from:
- [DASHBOARD_INTEGRATION_GUIDE.md](implementation/dashboard/DASHBOARD_INTEGRATION_GUIDE.md)

Key components to build:
1. **FailureList** - Shows all test failures with "Analyze Now" button
2. **AnalysisModal** - Displays results with GitHub/Jenkins links
3. **FeedbackModal** - Collects user feedback for refinement

### **Phase 6: Production Deployment (Future)**

1. Deploy n8n to production server
2. Configure production MongoDB cluster
3. Set up MCP servers (MongoDB, GitHub, Pinecone)
4. Configure authentication and security
5. Set up monitoring and alerts

---

## 📞 Support

**Documentation:**
- [MongoDB Setup Guide](implementation/database/mongodb-setup-guide.md)
- [Workflow README](implementation/workflows/README.md)
- [System Overview](implementation/workflows/COMPLETE_SYSTEM_OVERVIEW.md)
- [Dashboard Integration](implementation/dashboard/DASHBOARD_INTEGRATION_GUIDE.md)

**Quick Links:**
- MongoDB: `mongodb://localhost:27017/ddn_ai_project`
- n8n: `http://localhost:5678`
- LangGraph: `http://localhost:5000`

---

## ✅ Success!

**If you've completed all steps above, you now have:**

✅ MongoDB database with test failure data
✅ 3 n8n workflows (auto, manual, refinement)
✅ LangGraph classification service
✅ Complete API for dashboard integration
✅ Sample data for testing
✅ Documentation for everything

**You're ready to:**
- ✅ Trigger manual analysis from dashboard
- ✅ Refine solutions with user feedback
- ✅ View results with clickable GitHub links
- ✅ Track refinement history
- ✅ Build your React dashboard

---

**Congratulations! Your DDN AI system is fully set up!** 🎉

**Time to build the dashboard and start analyzing failures!**
