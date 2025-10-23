# ⚡ DDN AI Agentic Workflow - Quick Start Checklist

**Print this page and check off items as you complete them!**

---

## 🔑 Step 1: Get API Keys (14 Required)

### **AI Services (3 items)**
- [ ] **Anthropic API Key** → https://console.anthropic.com
  - Copy to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

- [ ] **OpenAI API Key** → https://platform.openai.com
  - Copy to `.env`: `OPENAI_API_KEY=sk-...`

- [ ] **Pinecone API Key + Index** → https://www.pinecone.io
  - Copy to `.env`: `PINECONE_API_KEY=...`
  - Create index: `ddn-error-solutions` (1536 dimensions)
  - Copy to `.env`: `PINECONE_INDEX_NAME=ddn-error-solutions`

### **GitHub (2 items)**
- [ ] **GitHub Token** → GitHub → Settings → Developer settings → Personal access tokens
  - Scopes: `repo`, `read:org`, `workflow`
  - Copy to `.env`: `GITHUB_TOKEN=ghp_...`

- [ ] **GitHub Repo** → Your repository name
  - Copy to `.env`: `GITHUB_REPO=your-org/your-repo`

### **Jenkins (3 items)**
- [ ] **Jenkins URL** → Your Jenkins server
  - Copy to `.env`: `JENKINS_URL=http://localhost:8080`

- [ ] **Jenkins User** → Your username
  - Copy to `.env`: `JENKINS_USER=admin`

- [ ] **Jenkins Token** → Jenkins → User → Configure → API Token
  - Copy to `.env`: `JENKINS_TOKEN=...`

### **Database (1 item)**
- [ ] **MongoDB Connection** → Choose one:
  - **Local**: `MONGODB_URI=mongodb://localhost:27017/ddn_ai_project`
  - **Atlas**: `MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/ddn_ai_project`

### **Service URLs (3 items - Auto-configured)**
- [ ] `LANGGRAPH_SERVICE_URL=http://localhost:5000`
- [ ] `MONGODB_MCP_URL=http://localhost:5001/sse`
- [ ] `GITHUB_MCP_URL=http://localhost:5002/sse`

### **n8n (2 items)**
- [ ] Install n8n: `npm install -g n8n`
- [ ] Configure MongoDB credentials in n8n UI

---

## 📦 Step 2: Install Dependencies

```bash
# Navigate to project
cd C:\DDN-AI-Project-Documentation\implementation

# Install Python packages
pip install -r requirements.txt
```

**Check off when complete:**
- [ ] Python dependencies installed

---

## 🗄️ Step 3: Setup Database

```bash
cd C:\DDN-AI-Project-Documentation\implementation\database

# Setup MongoDB
python setup_mongodb.py

# Test connection
python test_mongodb_connection.py
```

**Check off when complete:**
- [ ] MongoDB setup complete
- [ ] Connection test passed
- [ ] Sample data loaded (build: SAMPLE_12345)

---

## 🚀 Step 4: Start Services (Keep 4 terminals open)

### **Terminal 1: LangGraph Service**
```bash
cd C:\DDN-AI-Project-Documentation\implementation
python langgraph_agent.py
```
- [ ] Running on http://localhost:5000

### **Terminal 2: MongoDB MCP Server**
```bash
cd C:\DDN-AI-Project-Documentation\mcp-configs
python mcp_mongodb_server.py
```
- [ ] Running on http://localhost:5001/sse

### **Terminal 3: GitHub MCP Server**
```bash
cd C:\DDN-AI-Project-Documentation\mcp-configs
python mcp_github_server.py
```
- [ ] Running on http://localhost:5002/sse

### **Terminal 4: n8n**
```bash
n8n start
```
- [ ] Running on http://localhost:5678

---

## ⚙️ Step 5: Configure n8n

### **5.1: Add MongoDB Credentials**
1. Open: http://localhost:5678
2. Settings → Credentials → Add Credential → MongoDB
3. Name: `MongoDB Production`
4. Connection: `mongodb://localhost:27017/ddn_ai_project`
5. Database: `ddn_ai_project`
6. Test Connection → Save

- [ ] MongoDB credentials added and tested

### **5.2: Import Workflows**
Navigate to: `C:\DDN-AI-Project-Documentation\implementation\workflows\`

Import these files in n8n:
- [ ] `workflow_2_manual_trigger.json`
- [ ] `workflow_3_refinement.json`
- [ ] `ddn_ai_complete_workflow_phase3_final.json`

### **5.3: Configure Workflow Credentials**
For each workflow:
1. Open workflow
2. Click MongoDB nodes (yellow warning ⚠️)
3. Select credential: "MongoDB Production"
4. Save node → Save workflow

- [ ] Workflow 2 configured
- [ ] Workflow 3 configured
- [ ] Complete workflow configured

### **5.4: Activate Workflows**
- [ ] Workflow 2: Manual Trigger → Active ✅
- [ ] Workflow 3: Refinement → Active ✅
- [ ] Complete Workflow → Active ✅

---

## ✅ Step 6: Verify Everything Works

### **Test 1: Health Checks**
```bash
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health
```
- [ ] All services respond "healthy"

### **Test 2: Manual Trigger Workflow**
```powershell
$body = @{
    build_id = "SAMPLE_12345"
    user_email = "test@example.com"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5678/webhook/ddn-manual-trigger" `
    -Method Post -ContentType "application/json" -Body $body
```
- [ ] Response received in 15-20 seconds
- [ ] Status: "success"
- [ ] Contains: root_cause, fix_recommendation, links

### **Test 3: Check MongoDB**
```bash
mongosh mongodb://localhost:27017/ddn_ai_project
db.analysis_solutions.findOne()
```
- [ ] Analysis data saved in MongoDB

### **Test 4: Refinement Workflow**
```powershell
$body = @{
    build_id = "SAMPLE_12345"
    user_feedback = "This is a config issue"
    user_email = "test@example.com"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5678/webhook/ddn-refinement" `
    -Method Post -ContentType "application/json" -Body $body
```
- [ ] Refinement completed successfully

---

## 🎉 Final Checklist

### **Services Running:**
- [ ] MongoDB (port 27017)
- [ ] LangGraph (port 5000)
- [ ] MongoDB MCP (port 5001)
- [ ] GitHub MCP (port 5002)
- [ ] n8n (port 5678)

### **Configuration Complete:**
- [ ] .env file with 14 API keys/credentials
- [ ] MongoDB database created (ddn_ai_project)
- [ ] 5 collections with indexes
- [ ] Pinecone index created
- [ ] n8n credentials configured
- [ ] 3 workflows imported and active

### **Testing Passed:**
- [ ] Health endpoints respond
- [ ] Manual trigger works (<20 sec)
- [ ] Data saved in MongoDB
- [ ] Refinement workflow works

---

## 🎯 Success!

**If all items are checked, your system is FULLY ACTIVATED!** ✅

You can now:
- ✅ Analyze test failures on demand
- ✅ Get AI-powered root cause analysis
- ✅ Receive code fix recommendations
- ✅ Refine solutions with user feedback
- ✅ Build dashboard integration

---

## 📊 Quick Reference

**Webhook URLs:**
- Manual Analysis: `http://localhost:5678/webhook/ddn-manual-trigger`
- Refinement: `http://localhost:5678/webhook/ddn-refinement`
- Auto (Jenkins): `http://localhost:5678/webhook/jenkins-build-failed`

**Service Health Checks:**
- LangGraph: `http://localhost:5000/health`
- MongoDB MCP: `http://localhost:5001/health`
- GitHub MCP: `http://localhost:5002/health`

**MongoDB:**
- Connection: `mongodb://localhost:27017/ddn_ai_project`
- Database: `ddn_ai_project`
- Collections: builds, test_failures, error_classifications, analysis_solutions, refinement_history

**Documentation:**
- Full Guide: [ACTIVATION-GUIDE.md](ACTIVATION-GUIDE.md)
- Architecture: [architecture/COMPLETE-ARCHITECTURE.md](architecture/COMPLETE-ARCHITECTURE.md)
- MCP Guide: [technical-guides/MCP-CONNECTOR-GUIDE.md](technical-guides/MCP-CONNECTOR-GUIDE.md)

---

## ⏱️ Estimated Time

- Setup (Steps 1-3): **20 minutes**
- Services (Step 4): **5 minutes**
- n8n Config (Step 5): **10 minutes**
- Testing (Step 6): **10 minutes**

**Total: 45 minutes** ⚡

---

**Print this checklist and keep it handy during setup!**
