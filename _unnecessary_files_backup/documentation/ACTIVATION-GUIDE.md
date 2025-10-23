# 🚀 DDN AI Agentic Workflow - Complete Activation Guide

**Document Purpose**: Step-by-step guide to activate the DDN AI Test Failure Analysis System
**Created**: October 17, 2025
**Time to Complete**: 45-60 minutes
**Difficulty**: Intermediate

---

## 📋 Table of Contents

1. [Prerequisites Checklist](#prerequisites-checklist)
2. [Required Credentials (14 Items)](#required-credentials-14-items)
3. [Optional Integrations (10 Items)](#optional-integrations-10-items)
4. [Step-by-Step Activation](#step-by-step-activation)
5. [Verification & Testing](#verification--testing)
6. [Troubleshooting](#troubleshooting)
7. [Quick Reference](#quick-reference)

---

## ✅ Prerequisites Checklist

Before starting, ensure you have:

- [ ] Windows 10/11 or Linux/macOS
- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed (for n8n)
- [ ] MongoDB running (local or Atlas)
- [ ] Git installed
- [ ] Code editor (VS Code recommended)
- [ ] Internet connection (for API access)
- [ ] Admin/sudo access (for installations)

---

## 🔑 Required Credentials (14 Items)

### **Category 1: AI & ML Services (3 items)**

#### 1.1 Anthropic API Key (Claude AI)
- **Purpose**: Main AI reasoning, error analysis, code fix generation
- **Cost**: Pay-as-you-go (~$0.05-$0.15 per analysis)
- **How to get**:
  ```
  1. Visit: https://console.anthropic.com
  2. Sign up or log in
  3. Navigate to: API Keys
  4. Click: "Create Key"
  5. Copy the key (starts with: sk-ant-...)
  ```
- **Free tier**: $5 credit for new accounts
- **Env variable**: `ANTHROPIC_API_KEY=sk-ant-...`

#### 1.2 OpenAI API Key
- **Purpose**: Text embeddings for RAG (vector search)
- **Cost**: ~$0.12/year for 1000 searches (extremely cheap)
- **How to get**:
  ```
  1. Visit: https://platform.openai.com
  2. Sign up or log in
  3. Navigate to: API Keys
  4. Click: "Create new secret key"
  5. Copy the key (starts with: sk-...)
  ```
- **Free tier**: $5 credit for new accounts
- **Env variable**: `OPENAI_API_KEY=sk-...`

#### 1.3 Pinecone API Key + Index Name
- **Purpose**: Vector database for storing historical solutions
- **Cost**: Free tier (1 index, 100K vectors)
- **How to get**:
  ```
  1. Visit: https://www.pinecone.io
  2. Sign up for free account
  3. Create a project
  4. Navigate to: API Keys
  5. Copy the API key
  6. Create an index:
     - Name: ddn-error-solutions
     - Dimensions: 1536 (for OpenAI embeddings)
     - Metric: cosine
  ```
- **Env variables**:
  ```
  PINECONE_API_KEY=your-key-here
  PINECONE_INDEX_NAME=ddn-error-solutions
  ```

---

### **Category 2: Version Control (2 items)**

#### 2.1 GitHub Personal Access Token
- **Purpose**: Fetch source code, file history, create PRs
- **Permissions needed**: `repo`, `read:org`, `workflow`
- **How to get**:
  ```
  1. GitHub → Settings → Developer settings
  2. Personal access tokens → Tokens (classic)
  3. Click: "Generate new token (classic)"
  4. Select scopes:
     ☑ repo (full control)
     ☑ read:org
     ☑ workflow
  5. Click: "Generate token"
  6. Copy immediately (won't be shown again)
  ```
- **Env variable**: `GITHUB_TOKEN=ghp_...`

#### 2.2 GitHub Repository
- **Format**: `organization/repository-name`
- **Example**: `ddn/test-automation` or `your-org/your-repo`
- **Env variable**: `GITHUB_REPO=your-org/your-repo`

---

### **Category 3: CI/CD System (3 items)**

#### 3.1 Jenkins URL
- **Format**: `http://your-jenkins-server:8080`
- **Example**: `http://localhost:8080` or `https://jenkins.company.com`
- **Env variable**: `JENKINS_URL=http://localhost:8080`

#### 3.2 Jenkins Username
- **Your Jenkins login username**
- **Env variable**: `JENKINS_USER=admin`

#### 3.3 Jenkins API Token
- **How to get**:
  ```
  1. Log in to Jenkins
  2. Click your name (top right)
  3. Click: "Configure"
  4. Section: "API Token"
  5. Click: "Add new Token"
  6. Give it a name (e.g., "DDN-AI-Integration")
  7. Click: "Generate"
  8. Copy the token immediately
  ```
- **Env variable**: `JENKINS_TOKEN=your-token-here`

---

### **Category 4: Database (1 item - Choose ONE option)**

#### ✅ Recommended: MongoDB Atlas (Cloud - Production Ready)
- **You have access**: Atlas account at https://cloud.mongodb.com/v2#/org/68dc1c4495ae3e552cffa964/projects
- **Connection string format**: `mongodb+srv://username:password@cluster.mongodb.net/ddn_ai_project`
- **Setup time**: 10 minutes
- **Complete guide**: [MONGODB-ATLAS-SETUP.md](implementation/database/MONGODB-ATLAS-SETUP.md)
- **How to get connection string**:
  ```
  1. Visit: https://cloud.mongodb.com
  2. Login with your account
  3. Select/Create cluster (M0 Free tier available)
  4. Database Access → Add user:
     - Username: ddn_admin
     - Password: [generate secure password]
     - Role: Atlas admin
  5. Network Access → Add IP Address:
     - For testing: 0.0.0.0/0 (Allow from anywhere)
     - For production: Add specific IPs
  6. Clusters → Connect → "Connect your application"
  7. Driver: Python 3.12+
  8. Copy connection string
  9. Replace <password> with actual password
  ```
- **Example**: `mongodb+srv://ddn_admin:SecurePass123@ddn-cluster.xxxxx.mongodb.net/ddn_ai_project?retryWrites=true&w=majority`
- **Env variable**: `MONGODB_ATLAS_URI=mongodb+srv://...`

#### Alternative: Local MongoDB (Development Only)
- **If available**: MongoDB v7.0.4 on `localhost:27017`
- **Connection string**: `mongodb://localhost:27017/ddn_ai_project`
- **Setup time**: 5 minutes
- **Guide**: [MONGODB-QUICKSTART.md](MONGODB-QUICKSTART.md)
- **Note**: Local setup is good for learning, but Atlas is recommended for team collaboration and production

---

### **Category 5: Service URLs (3 items)**

#### 5.1 LangGraph Service URL
- **Default**: `http://localhost:5000`
- **Purpose**: Error classification service
- **Env variable**: `LANGGRAPH_SERVICE_URL=http://localhost:5000`
- **Setup**: Automatically starts when you run `python langgraph_agent.py`

#### 5.2 MongoDB MCP Server URL
- **Default**: `http://localhost:5001/sse`
- **Purpose**: Database query tool for Claude AI
- **Env variable**: `MONGODB_MCP_URL=http://localhost:5001/sse`
- **Setup**: Run `python mcp-configs/mcp_mongodb_server.py`

#### 5.3 GitHub MCP Server URL
- **Default**: `http://localhost:5002/sse`
- **Purpose**: Code fetch tool for Claude AI
- **Env variable**: `GITHUB_MCP_URL=http://localhost:5002/sse`
- **Setup**: Run `python mcp-configs/mcp_github_server.py`

---

### **Category 6: n8n Workflow (2 items)**

#### 6.1 n8n Installation
- **URL**: `http://localhost:5678`
- **Install**:
  ```bash
  npm install -g n8n
  n8n start
  ```

#### 6.2 MongoDB Credentials in n8n
- **Configure in n8n UI**:
  ```
  1. Open: http://localhost:5678
  2. Settings → Credentials
  3. Add Credential → MongoDB
  4. Name: MongoDB Production
  5. Connection String: mongodb://localhost:27017/ddn_ai_project
  6. Database: ddn_ai_project
  7. Test Connection → Save
  ```

---

## ⚠️ Optional Integrations (10 Items)

### **Category 7: Jira (Optional - 3 items)**

#### 7.1 Jira URL
- **Example**: `https://your-company.atlassian.net`
- **Env variable**: `JIRA_URL=https://your-company.atlassian.net`

#### 7.2 Jira Email
- **Your Jira account email**
- **Env variable**: `JIRA_EMAIL=your-email@company.com`

#### 7.3 Jira API Token
- **How to get**:
  ```
  1. Jira → Profile → Security → API Tokens
  2. Click: "Create API token"
  3. Copy the token
  ```
- **Env variable**: `JIRA_API_TOKEN=your-token`

---

### **Category 8: Slack (Optional - 3 items)**

#### 8.1 Slack Bot Token
- **How to get**:
  ```
  1. Visit: https://api.slack.com/apps
  2. Create New App → From scratch
  3. OAuth & Permissions → Add scopes: chat:write, channels:read
  4. Install to Workspace
  5. Copy "Bot User OAuth Token" (starts with xoxb-)
  ```
- **Env variable**: `SLACK_BOT_TOKEN=xoxb-...`

#### 8.2 Slack Signing Secret
- **Found in**: App Settings → Basic Information → Signing Secret
- **Env variable**: `SLACK_SIGNING_SECRET=...`

#### 8.3 Slack Default Channel
- **Example**: `#test-failures`
- **Env variable**: `SLACK_DEFAULT_CHANNEL=#test-failures`

---

### **Category 9: Microsoft Teams (Optional - 1 item)**

#### 9.1 Teams Webhook URL
- **How to get**:
  ```
  1. Open Teams channel
  2. Click: ⋯ → Connectors
  3. Search: "Incoming Webhook"
  4. Configure → Add
  5. Name: "DDN AI Notifications"
  6. Copy webhook URL
  ```
- **Env variable**: `TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...`

---

## 🚀 Step-by-Step Activation

### **Phase 1: Environment Setup (10 minutes)**

#### Step 1: Clone/Navigate to Project
```bash
cd C:\DDN-AI-Project-Documentation
```

#### Step 2: Create Environment File
```bash
# Copy example file
copy .env.example .env

# Edit with your favorite editor
notepad .env
```

#### Step 3: Fill in Required Values
```bash
# ===================== AI & ML APIs =====================
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=ddn-error-solutions

# ===================== GitHub =====================
GITHUB_TOKEN=ghp_your-token-here
GITHUB_REPO=your-org/your-repo

# ===================== Jenkins =====================
JENKINS_URL=http://localhost:8080
JENKINS_USER=admin
JENKINS_TOKEN=your-jenkins-token

# ===================== Database =====================
# MongoDB Atlas (Cloud - Recommended)
MONGODB_ATLAS_URI=mongodb+srv://ddn_admin:YOUR_PASSWORD@ddn-cluster.xxxxx.mongodb.net/ddn_ai_project?retryWrites=true&w=majority

# OR Local MongoDB (Development only)
# MONGODB_URI=mongodb://localhost:27017/ddn_ai_project

# Use Atlas by default
MONGODB_URI=${MONGODB_ATLAS_URI}

# ===================== Service URLs =====================
LANGGRAPH_SERVICE_URL=http://localhost:5000
MONGODB_MCP_URL=http://localhost:5001/sse
GITHUB_MCP_URL=http://localhost:5002/sse

# ===================== Configuration =====================
AGING_THRESHOLD_DAYS=5
MAX_TOKENS=8000
DEBUG=False
SELF_HEALING_SAFE_MODE=true
MIN_SUCCESS_RATE=0.8
MIN_PATTERN_OCCURRENCES=3
```

#### Step 4: Install Python Dependencies
```bash
cd C:\DDN-AI-Project-Documentation\implementation

# Install all required packages
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed:
- flask
- langgraph
- langchain
- langchain-anthropic
- langchain-openai
- langchain-pinecone
- pymongo
- pinecone-client
- python-dotenv
... (and dependencies)
```

---

### **Phase 2: MongoDB Atlas Setup (10 minutes)**

#### Step 5: Setup MongoDB Atlas Database

**5.1 - Update Connection String in Setup Script:**
```bash
cd C:\DDN-AI-Project-Documentation\implementation\database

# Open setup_mongodb_atlas.py in editor
notepad setup_mongodb_atlas.py

# Update line 143 with your actual Atlas connection string:
# ATLAS_URI = "mongodb+srv://ddn_admin:YOUR_PASSWORD@ddn-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority"
```

**5.2 - Run Atlas Setup:**
```bash
python setup_mongodb_atlas.py
```

**Expected output:**
```
======================================================================
  DDN AI Project - MongoDB Atlas Setup
======================================================================

🔌 Connecting to MongoDB Atlas...
   Database: ddn_ai_project

✅ Connected to Atlas successfully!

   MongoDB Version: 7.0.x

📦 Setting up 'builds' collection...
  ✅ Created indexes
  ✅ Inserted sample build

📝 Setting up other collections...
  ✅ All collections configured

======================================================================
✅ MongoDB Atlas Setup Complete!
======================================================================

📊 Database: ddn_ai_project
📍 Atlas Cluster: Connected

📦 Collections Created:
  ✅ analysis_solutions         (0 documents)
  ✅ builds                      (1 documents)
  ✅ console_logs                (0 documents)
  ✅ refinement_history          (0 documents)
  ✅ test_results                (0 documents)

🎯 Next Steps:
  1. Update .env file with Atlas connection string
  2. Configure n8n with Atlas credentials
  3. Test connection with: python test_mongodb_atlas.py
```

#### Step 6: Verify Atlas Connection
```bash
python test_mongodb_atlas.py
```

**Expected output:**
```
🔍 Testing MongoDB Atlas Connection...

✅ Atlas connection successful!

📦 Collections in 'ddn_ai_project':
  ✅ analysis_solutions: 0 documents
  ✅ builds: 1 documents
  ✅ console_logs: 0 documents
  ✅ refinement_history: 0 documents
  ✅ test_results: 0 documents

📊 Sample build: ATLAS_SAMPLE_12345

✅ All tests passed!
```

**Troubleshooting:**
- **"Connection failed"** → Check password in connection string
- **"IP not whitelisted"** → Go to Atlas → Network Access → Add your IP
- **"Authentication failed"** → Verify database user credentials in Atlas

---

### **Phase 3: Pinecone Vector Database (5 minutes)**

#### Step 7: Initialize Pinecone Index
```bash
# Run Pinecone setup
python setup_pinecone.py
```

**Expected output:**
```
🚀 Initializing Pinecone Vector Database
✅ Connected to Pinecone
✅ Index 'ddn-error-solutions' created
✅ Sample embeddings uploaded (10 historical solutions)
✅ Pinecone ready for RAG queries
```

---

### **Phase 4: Start Services (5 minutes)**

#### Step 8: Start LangGraph Classification Service
```bash
# Open Terminal 1
cd C:\DDN-AI-Project-Documentation\implementation
python langgraph_agent.py
```

**Expected output:**
```
🚀 Starting DDN LangGraph Classification Service...
✅ Loaded environment variables
✅ Connected to Pinecone (index: ddn-error-solutions)
✅ Claude AI initialized (model: claude-3-5-sonnet)
📍 Service running on: http://localhost:5000
 * Running on http://0.0.0.0:5000
```

**Keep this terminal open!**

#### Step 9: Start MongoDB MCP Server
```bash
# Open Terminal 2
cd C:\DDN-AI-Project-Documentation\mcp-configs
python mcp_mongodb_server.py
```

**Expected output:**
```
🚀 MongoDB MCP Server Starting...
✅ Connected to MongoDB (ddn_ai_project)
✅ MCP Server running on: http://localhost:5001/sse
✅ Available tools: [query_builds, query_failures, store_analysis]
```

**Keep this terminal open!**

#### Step 10: Start GitHub MCP Server
```bash
# Open Terminal 3
cd C:\DDN-AI-Project-Documentation\mcp-configs
python mcp_github_server.py
```

**Expected output:**
```
🚀 GitHub MCP Server Starting...
✅ Connected to GitHub (repo: your-org/your-repo)
✅ MCP Server running on: http://localhost:5002/sse
✅ Available tools: [fetch_file, search_code, get_commits, create_pr]
```

**Keep this terminal open!**

---

### **Phase 5: n8n Workflow Setup (10 minutes)**

#### Step 11: Start n8n
```bash
# Open Terminal 4
n8n start
```

**Access at**: `http://localhost:5678`

#### Step 12: Configure MongoDB Atlas Credentials in n8n
```
1. Open browser: http://localhost:5678
2. Click: Settings (gear icon)
3. Click: Credentials
4. Click: "Add Credential"
5. Search: "MongoDB"
6. Fill in:
   - Credential Name: MongoDB Atlas Production
   - Connection String: mongodb+srv://ddn_admin:YOUR_PASSWORD@ddn-cluster.xxxxx.mongodb.net/ddn_ai_project?retryWrites=true&w=majority
   - Database Name: ddn_ai_project
7. Click: "Test Connection" (should show ✅ Success)
8. Click: "Save"
```

**Important:**
- Replace `YOUR_PASSWORD` with actual database user password
- Replace `ddn-cluster.xxxxx.mongodb.net` with your actual cluster hostname
- You can find this in Atlas → Clusters → Connect → Connection String

**If using local MongoDB instead:**
```
Connection String: mongodb://localhost:27017/ddn_ai_project
```

#### Step 13: Import Workflows
```
Navigate to: C:\DDN-AI-Project-Documentation\implementation\workflows\

Import these 3 files:
1. workflow_2_manual_trigger.json
2. workflow_3_refinement.json
3. ddn_ai_complete_workflow_phase3_final.json
```

**In n8n UI:**
```
1. Click: Workflows (left sidebar)
2. Click: "Import from File" (top right)
3. Select: workflow_2_manual_trigger.json
4. Workflow opens → Click "Save"
5. Repeat for other 2 workflows
```

#### Step 14: Configure Workflow Credentials
**For EACH workflow:**
```
1. Open workflow in n8n
2. Look for nodes with ⚠️ yellow warning
3. Click each MongoDB node
4. Select credential: "MongoDB Production"
5. Click "Save" on the node
6. Click "Save" on the workflow
```

**Workflows to configure:**
- Workflow 2: MongoDB nodes (#3, #10) → Select "MongoDB Atlas Production"
- Workflow 3: MongoDB nodes (#3, #5, #9, #10) → Select "MongoDB Atlas Production"
- Complete Workflow: MongoDB nodes (multiple) → Select "MongoDB Atlas Production"

**Note:** All MongoDB nodes must use the same credential ("MongoDB Atlas Production")

#### Step 15: Activate Workflows
```
1. Open each workflow
2. Toggle "Active" switch to ON (top right)
3. Verify status shows "Active"
```

**All 3 workflows should now show: ✅ Active**

---

## ✅ Verification & Testing

### **Phase 6: System Health Checks (5 minutes)**

#### Test 1: Verify All Services Running
```bash
# Check LangGraph service
curl http://localhost:5000/health

# Expected: {"status": "healthy", "service": "DDN LangGraph Agent"}

# Check MongoDB MCP
curl http://localhost:5001/health

# Expected: {"status": "healthy", "tools_available": 5}

# Check GitHub MCP
curl http://localhost:5002/health

# Expected: {"status": "healthy", "repo": "your-org/your-repo"}

# Check n8n
curl http://localhost:5678

# Expected: HTML page (n8n UI)
```

#### Test 2: Manual Trigger Workflow
```bash
# Windows (PowerShell)
$body = @{
    build_id = "SAMPLE_12345"
    user_email = "test@example.com"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5678/webhook/ddn-manual-trigger" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

**Expected response (15-20 seconds):**
```json
{
  "status": "success",
  "message": "Analysis completed successfully",
  "data": {
    "build_id": "SAMPLE_12345",
    "error_category": "CODE_ERROR",
    "confidence": 0.85,
    "root_cause": "Null pointer exception in UserService.java",
    "fix_recommendation": "Add null check before accessing user object...",
    "links": {
      "jenkins": "http://localhost:8080/job/ddn-tests/SAMPLE_12345",
      "github_files": [
        {
          "file_path": "src/main/java/UserService.java",
          "line_number": 42,
          "github_url": "https://github.com/..."
        }
      ]
    },
    "execution_time": "14.3s",
    "cost_estimate": "$0.08"
  }
}
```

#### Test 3: Verify Data in MongoDB Atlas
```bash
# Option A: Using MongoDB Compass (GUI)
# 1. Open MongoDB Compass
# 2. Connect with Atlas connection string
# 3. Navigate to: ddn_ai_project → analysis_solutions
# 4. Should see the analysis document for ATLAS_SAMPLE_12345

# Option B: Using mongosh (CLI)
mongosh "mongodb+srv://ddn_admin:YOUR_PASSWORD@ddn-cluster.xxxxx.mongodb.net/ddn_ai_project"

# View the analysis
db.analysis_solutions.findOne()

# Should see the complete analysis with root cause, fix, links, etc.
```

**Verify in Atlas Dashboard:**
```
1. Go to: https://cloud.mongodb.com
2. Clusters → Browse Collections
3. Database: ddn_ai_project
4. Collection: analysis_solutions
5. Should see 1 document with build_id: ATLAS_SAMPLE_12345
```

#### Test 4: Refinement Workflow
```bash
# Windows (PowerShell)
$body = @{
    build_id = "SAMPLE_12345"
    user_feedback = "This is actually a config issue, not code"
    user_email = "test@example.com"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5678/webhook/ddn-refinement" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

**Expected response (15-20 seconds):**
```json
{
  "status": "success",
  "message": "Analysis refined successfully",
  "data": {
    "build_id": "SAMPLE_12345",
    "refinement_version": 2,
    "category_changed": true,
    "previous_category": "CODE_ERROR",
    "new_category": "CONFIG_ERROR",
    "refinement_summary": "Re-classified based on user feedback",
    "updated_root_cause": "...",
    "updated_fix": "..."
  }
}
```

---

## ✅ Final Verification Checklist

Mark each item as complete:

### **Services:**
- [ ] MongoDB Atlas cluster active and accessible
- [ ] LangGraph service running (localhost:5000)
- [ ] MongoDB MCP server running (localhost:5001)
- [ ] GitHub MCP server running (localhost:5002)
- [ ] n8n running (localhost:5678)

### **Configuration:**
- [ ] .env file created with all API keys
- [ ] MongoDB Atlas connection string configured
- [ ] Atlas database 'ddn_ai_project' created
- [ ] 5 collections exist with indexes
- [ ] Sample data loaded (ATLAS_SAMPLE_12345)
- [ ] Pinecone index created with embeddings
- [ ] n8n MongoDB Atlas credentials configured
- [ ] Network access configured in Atlas (IP whitelisted)

### **Workflows:**
- [ ] 3 workflows imported
- [ ] All MongoDB nodes configured with credentials
- [ ] All 3 workflows activated

### **Testing:**
- [ ] Health endpoints respond
- [ ] Manual trigger workflow succeeds
- [ ] Analysis stored in MongoDB
- [ ] Refinement workflow succeeds
- [ ] GitHub files fetched correctly

---

## 🛠️ Troubleshooting

### **Problem: "MongoDB Atlas connection failed"**

**Solution:**
```bash
# 1. Verify connection string is correct
echo $MONGODB_ATLAS_URI

# 2. Check if password is correct (no special chars issues)
# Replace: mongodb+srv://user:p@ssw0rd@... (URL encode special chars)

# 3. Test connection with mongosh
mongosh "mongodb+srv://ddn_admin:YOUR_PASSWORD@cluster.mongodb.net/ddn_ai_project"

# 4. Verify IP is whitelisted
# Atlas → Security → Network Access → Add IP Address → 0.0.0.0/0 (testing)

# 5. Check database user exists
# Atlas → Security → Database Access → Should see 'ddn_admin'

# 6. Verify cluster is active
# Atlas → Clusters → Status should be green "Active"
```

**Common Atlas Issues:**
- **Wrong password** → Reset in Atlas → Database Access → Edit User
- **IP not whitelisted** → Add 0.0.0.0/0 for testing, specific IPs for production
- **Cluster paused** → Atlas free tier pauses after inactivity → Click "Resume"

---

### **Problem: "LangGraph service not responding"**

**Check:**
```bash
# Verify .env file exists
ls .env

# Check API keys are set
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('ANTHROPIC_API_KEY:', os.getenv('ANTHROPIC_API_KEY')[:20])"

# Restart service
cd implementation
python langgraph_agent.py
```

---

### **Problem: "Pinecone index not found"**

**Solution:**
```bash
# Recreate index
python setup_pinecone.py

# Or manually at: https://app.pinecone.io
# Create index:
#   - Name: ddn-error-solutions
#   - Dimensions: 1536
#   - Metric: cosine
```

---

### **Problem: "n8n workflow returns 404"**

**Check:**
```
1. Is workflow activated? (Toggle should be ON)
2. Is webhook URL correct?
   - Should be: http://localhost:5678/webhook/ddn-manual-trigger
3. Check n8n execution log for errors
4. Verify MongoDB credentials in workflow nodes
```

---

### **Problem: "GitHub MCP can't fetch files"**

**Check:**
```bash
# Verify GitHub token has permissions
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/user

# Should return your GitHub user info

# Check token scopes include: repo, read:org
```

---

### **Problem: "Analysis returns empty results"**

**Check:**
```
1. LangGraph service running? (localhost:5000)
2. MongoDB has sample data? (db.builds.find())
3. Pinecone index populated? (check dashboard)
4. API keys valid? (check .env file)
5. Check n8n execution logs for detailed errors
```

---

## 📊 Quick Reference

### **Service Ports:**
| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| MongoDB Atlas | Cloud | mongodb+srv://cluster.mongodb.net | Database (Cloud) |
| LangGraph | 5000 | http://localhost:5000 | Classification |
| MongoDB MCP | 5001 | http://localhost:5001/sse | DB queries |
| GitHub MCP | 5002 | http://localhost:5002/sse | Code fetch |
| n8n | 5678 | http://localhost:5678 | Workflows |

### **Webhook Endpoints:**
| Workflow | URL | Purpose |
|----------|-----|---------|
| Manual Trigger | http://localhost:5678/webhook/ddn-manual-trigger | On-demand analysis |
| Refinement | http://localhost:5678/webhook/ddn-refinement | User feedback |
| Auto Analysis | http://localhost:5678/webhook/jenkins-build-failed | Jenkins integration |

### **Environment Variables Summary:**
```bash
# Core (Required)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=ddn-error-solutions
GITHUB_TOKEN=ghp_...
GITHUB_REPO=org/repo
JENKINS_URL=http://localhost:8080
JENKINS_USER=admin
JENKINS_TOKEN=...

# MongoDB Atlas (Recommended)
MONGODB_ATLAS_URI=mongodb+srv://ddn_admin:PASSWORD@cluster.xxxxx.mongodb.net/ddn_ai_project?retryWrites=true&w=majority
MONGODB_URI=${MONGODB_ATLAS_URI}

# OR Local MongoDB (Development only)
# MONGODB_URI=mongodb://localhost:27017/ddn_ai_project

# Services
LANGGRAPH_SERVICE_URL=http://localhost:5000
MONGODB_MCP_URL=http://localhost:5001/sse
GITHUB_MCP_URL=http://localhost:5002/sse

# Optional
JIRA_URL=https://company.atlassian.net
JIRA_EMAIL=user@company.com
JIRA_API_TOKEN=...
SLACK_BOT_TOKEN=xoxb-...
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
```

### **Startup Commands:**
```bash
# Terminal 1: LangGraph
cd C:\DDN-AI-Project-Documentation\implementation
python langgraph_agent.py

# Terminal 2: MongoDB MCP
cd C:\DDN-AI-Project-Documentation\mcp-configs
python mcp_mongodb_server.py

# Terminal 3: GitHub MCP
cd C:\DDN-AI-Project-Documentation\mcp-configs
python mcp_github_server.py

# Terminal 4: n8n
n8n start
```

---

## 🎯 Success Criteria

Your system is **fully activated** when:

✅ All 5 services running without errors
✅ Health endpoints respond correctly
✅ Manual trigger workflow completes in <20 seconds
✅ Analysis stored in MongoDB with all fields
✅ GitHub files fetched successfully
✅ Refinement workflow works with user feedback
✅ Cost per analysis: $0.05-$0.15
✅ No error logs in any service

---

## 📈 What's Next?

After activation, you can:

### **1. Build Dashboard Integration**
- Use React components from [DASHBOARD_INTEGRATION_GUIDE.md](implementation/dashboard/DASHBOARD_INTEGRATION_GUIDE.md)
- Connect to webhook endpoints
- Display analysis results with clickable links

### **2. Connect Jenkins**
- Add webhook in Jenkins build configuration
- Point to: `http://localhost:5678/webhook/jenkins-build-failed`
- Automatic analysis on every test failure

### **3. Monitor Performance**
- Track execution times
- Monitor API costs
- Analyze error patterns
- Optimize based on metrics

### **4. Production Deployment**
- Move to cloud infrastructure
- Setup MongoDB Atlas cluster
- Deploy n8n to production server
- Configure SSL/TLS
- Setup monitoring & alerts

---

## 📞 Support

**Documentation:**
- [Complete Architecture](architecture/COMPLETE-ARCHITECTURE.md)
- [MCP Guide](technical-guides/MCP-CONNECTOR-GUIDE.md)
- [MongoDB Setup](MONGODB-QUICKSTART.md)
- [Workflow Documentation](implementation/workflows/README.md)

**Common Issues:**
- Check service logs in terminals
- Verify .env file has all keys
- Test each service independently
- Review n8n execution logs

---

## 🎉 Congratulations!

If you've completed all steps, you now have:

✅ **Fully operational AI-powered test failure analysis system**
✅ **3 active workflows (auto, manual, refinement)**
✅ **RAG-based intelligent routing (80% use RAG, 20% use MCP)**
✅ **Complete analysis in 15-20 seconds**
✅ **Cost reduced from $1.50 to $0.05-$0.15 per analysis**
✅ **Ready for dashboard integration**

**Time to analyze some real test failures!** 🚀

---

**Document Version**: 1.0
**Last Updated**: October 17, 2025
**Maintained By**: Rysun Development Team
