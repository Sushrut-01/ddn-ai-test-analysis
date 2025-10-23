# 🚀 START HERE - Complete Setup Guide

**Everything you need to get the DDN AI System running**

---

## What This System Does

This is an **AI-powered test failure analysis system** that:

✅ **Automatically detects** Jenkins test failures
✅ **Analyzes root causes** using Claude AI
✅ **Provides fix recommendations** with direct GitHub links
✅ **Allows manual triggers** from a web dashboard
✅ **Stores all data** in MongoDB and PostgreSQL
✅ **95% cost reduction** ($1.50 → $0.05 per analysis)
✅ **99.5% faster** (60 min → 15 sec per analysis)

---

## Quick Overview

```
GitHub/Jenkins → Test Failure → n8n Workflow → AI Analysis → Dashboard
                                      ↓
                                  MongoDB Storage
                                      ↓
                            User clicks "Analyze Now"
                                      ↓
                              Results in 15 seconds
```

---

## ⚡ 3 Setup Options

Choose based on your goal:

### Option 1: Just Want to See It Working? (5 minutes)

**Perfect for:** Quick demo, understanding the system

```bash
cd C:\DDN-AI-Project-Documentation

# Windows
scripts\start-system.bat

# Linux/Mac
./scripts/start-system.sh
```

**Then open:** http://localhost:3000

**What you get:**
- ✅ Dashboard running
- ✅ All services started
- ✅ Can test manual triggers
- ⚠️ No real Jenkins data (use test data)

**Next:** See [Testing Without Jenkins](#testing-without-jenkins)

---

### Option 2: Full Setup with GitHub & Jenkins (15 minutes)

**Perfect for:** Complete integration, production-ready setup

**Follow:** [QUICK-START-GITHUB-JENKINS.md](QUICK-START-GITHUB-JENKINS.md)

**What you get:**
- ✅ GitHub repository configured
- ✅ Jenkins webhooks sending data
- ✅ n8n workflows processing failures
- ✅ Dashboard showing real data
- ✅ Complete automation

---

### Option 3: Understanding Before Implementation (20 minutes)

**Perfect for:** Technical review, architecture understanding

**Read in order:**
1. [PROJECT-COMPLETION-SUMMARY.md](PROJECT-COMPLETION-SUMMARY.md) - What we built
2. [architecture/COMPLETE-ARCHITECTURE.md](architecture/COMPLETE-ARCHITECTURE.md) - How it works
3. [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) - How to deploy

**Then choose Option 1 or 2**

---

## Prerequisites

Before you start, make sure you have:

```bash
# Check Docker
docker --version
# Need: 20.10 or higher

# Check Docker Compose
docker compose version
# Need: 2.0 or higher

# Check Git
git --version
# Any version OK
```

**Don't have these?**
- Docker Desktop: https://www.docker.com/products/docker-desktop
- Git: https://git-scm.com/downloads

---

## File Structure Overview

```
C:\DDN-AI-Project-Documentation\
│
├── 🎯 START-HERE.md                    (👈 You are here!)
├── 📖 README.md                         (Main documentation)
│
├── ⚡ QUICK STARTS
│   ├── QUICK-START-GITHUB-JENKINS.md   (15-min complete setup)
│   └── MONGODB-QUICKSTART.md           (Database setup)
│
├── 📚 GUIDES
│   ├── DEPLOYMENT-GUIDE.md             (Production deployment)
│   ├── GITHUB-JENKINS-INTEGRATION-GUIDE.md
│   └── COMPLETE-SETUP-CHECKLIST.md
│
├── 🏗️ ARCHITECTURE
│   └── architecture/COMPLETE-ARCHITECTURE.md
│
├── ⚙️ IMPLEMENTATION
│   ├── docker-compose.yml              (All services defined)
│   ├── implementation/                 (All code)
│   │   ├── langgraph_agent.py         (AI classification)
│   │   ├── dashboard_api.py           (Backend API)
│   │   ├── workflows/                 (n8n workflows)
│   │   └── dashboard-ui/              (React frontend)
│   │
│   └── scripts/
│       ├── start-system.bat           (Windows startup)
│       └── start-system.sh            (Linux/Mac startup)
│
├── 🔧 CONFIGURATION
│   ├── .env.example                    (Environment template)
│   ├── Jenkinsfile                     (Jenkins pipeline)
│   └── jenkins/webhook-config.json
│
└── 📊 DOCUMENTATION
    └── [Various guides and docs]
```

---

## Testing Without Jenkins

If you don't have Jenkins yet, you can still test everything:

### Step 1: Start Services

```bash
cd C:\DDN-AI-Project-Documentation

# Windows
scripts\start-system.bat

# Linux/Mac
chmod +x scripts/start-system.sh
./scripts/start-system.sh
```

### Step 2: Access Dashboard

Open: http://localhost:3000

### Step 3: Trigger Test Analysis

**Option A: Use Dashboard UI**
1. Click "Manual Trigger" tab
2. Enter:
   - Build ID: `TEST_12345`
   - Job Name: `DDN-Smoke-Test`
3. Click "Trigger Analysis"
4. Wait 15 seconds
5. See results!

**Option B: Use API**
```bash
curl -X POST http://localhost:5678/webhook/ddn-manual-trigger \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "TEST_12345",
    "job_name": "DDN-Smoke-Test",
    "user_email": "test@example.com"
  }'
```

### Step 4: View Results

Results appear in:
- Dashboard UI (http://localhost:3000)
- MongoDB (`jenkins_failure_analysis` database)
- n8n executions (http://localhost:5678)

---

## Common Access Points

| What | URL | Login |
|------|-----|-------|
| **Dashboard** | http://localhost:3000 | None needed |
| **n8n Workflows** | http://localhost:5678 | admin / password |
| **Dashboard API** | http://localhost:5005 | None needed |
| **MongoDB** | localhost:27017 | admin / password |
| **PostgreSQL** | localhost:5432 | postgres / password |

---

## Environment Configuration

### Required API Keys

Edit `.env` file with your keys:

```env
# AI Services (Required)
ANTHROPIC_API_KEY=sk-ant-xxxxx     # Get from: https://console.anthropic.com/
OPENAI_API_KEY=sk-xxxxx            # Get from: https://platform.openai.com/
PINECONE_API_KEY=xxxxx             # Get from: https://www.pinecone.io/

# GitHub (Required for self-healing)
GITHUB_TOKEN=ghp_xxxxx             # Get from: https://github.com/settings/tokens
GITHUB_REPO=your-org/your-repo     # Your repository

# Jenkins (Optional - only if integrating)
JENKINS_URL=http://localhost:8080
JENKINS_USER=admin
JENKINS_TOKEN=xxxxx

# Optional Integrations
JIRA_URL=https://yourcompany.atlassian.net
SLACK_BOT_TOKEN=xoxb-xxxxx
```

**Can I test without API keys?**
- Yes, but AI analysis won't work
- Dashboard and data storage will work
- Use for UI testing only

---

## What Happens When You Start?

When you run `start-system.bat` or `start-system.sh`:

```
[1/5] Stopping any running containers...
      ✅ Clean slate

[2/5] Building Docker images...
      ✅ Creates images for all services (2-3 min)

[3/5] Starting all services...
      ✅ MongoDB, PostgreSQL, n8n, Dashboard, APIs
      ✅ 13 services total

[4/5] Waiting for services to initialize...
      ✅ 30 seconds for all to be ready

[5/5] Health checks...
      ✅ Dashboard API: OK
      ✅ Dashboard UI: OK
      ✅ n8n: OK
      ✅ LangGraph: OK
```

**Total time:** 3-5 minutes

---

## The 3 Workflows

The system uses 3 n8n workflows:

### Workflow 1: Auto-Trigger (Jenkins → n8n)

```
Jenkins test fails
    → Webhook sent to n8n
    → Data stored in MongoDB
    → Appears in Dashboard
    → Waits for aging >= 5 days OR manual trigger
```

**When:** Automatically on Jenkins failures
**File:** `ddn_ai_complete_workflow_v2.json`

### Workflow 2: Manual Trigger (Dashboard → AI Analysis)

```
User clicks "Analyze Now"
    → Dashboard API → n8n webhook
    → LangGraph classification
    → Claude AI analysis
    → Results back to Dashboard
```

**When:** User clicks button in Dashboard
**File:** `workflow_2_manual_trigger.json`

### Workflow 3: Refinement (User Feedback)

```
User provides feedback
    → Dashboard → n8n
    → Re-analyze with user context
    → Updated results
    → Stored in refinement_history
```

**When:** User not satisfied with analysis
**File:** `workflow_3_refinement.json`

---

## How to Use the Dashboard

### View Failures

1. Open: http://localhost:3000
2. See all test failures listed
3. Filter by:
   - Job name
   - Status
   - Aging days

### Trigger Analysis

1. Click "Analyze Now" button
2. Wait 10-15 seconds
3. See results:
   - Root cause analysis
   - Recommended fix
   - Related files with line numbers
   - Direct GitHub links
   - Jenkins build link

### Provide Feedback

1. Not satisfied with analysis?
2. Click "Provide Feedback"
3. Add your insights
4. System re-analyzes with your context
5. Get refined results

---

## Verify Everything Works

### Check 1: Services Running

```bash
docker ps
```

Should show 13 containers running:
- ddn-mongodb
- ddn-postgres
- ddn-n8n
- ddn-langgraph
- ddn-dashboard-ui
- ddn-dashboard-api
- ddn-manual-trigger
- ddn-jira
- ddn-slack
- ddn-self-healing
- ddn-mcp-mongodb
- ddn-mcp-github
- ddn-pinecone

### Check 2: Health Endpoints

```bash
curl http://localhost:3000        # Should return HTML
curl http://localhost:5005/health # Should return {"status": "healthy"}
curl http://localhost:5678        # Should return n8n login page
```

### Check 3: MongoDB Data

```bash
docker exec -it ddn-mongodb mongosh -u admin -p password

use jenkins_failure_analysis
db.builds.find()
```

Should show sample data if you ran a test trigger.

---

## Troubleshooting

### "Port already in use"

```bash
# Check what's using the port
netstat -ano | findstr :3000
netstat -ano | findstr :5678

# Stop the process or change port in docker-compose.yml
```

### "Cannot connect to MongoDB"

```bash
# Restart MongoDB
docker-compose restart mongodb

# Check logs
docker-compose logs mongodb

# Verify it's running
docker ps | grep mongodb
```

### "n8n workflows not triggering"

1. Open n8n: http://localhost:5678
2. Check workflows are Active (green toggle)
3. Click "Executions" to see runs
4. Test webhook:
   ```bash
   curl -X POST http://localhost:5678/webhook/ddn-manual-trigger \
     -d '{"build_id": "TEST"}'
   ```

### "Dashboard shows blank page"

```bash
# Check logs
docker-compose logs dashboard-ui

# Rebuild and restart
docker-compose build dashboard-ui
docker-compose restart dashboard-ui

# Clear browser cache and reload
```

---

## Next Steps After Setup

### 1. Test the System (Today)

- ✅ Trigger manual analysis
- ✅ View results in Dashboard
- ✅ Check MongoDB data
- ✅ Review n8n executions

### 2. Configure Jenkins (This Week)

- Add webhook to Jenkins jobs
- Test auto-trigger flow
- Configure all test suites

### 3. Production Deployment (Next Week)

- Set up MongoDB Atlas (cloud database)
- Deploy n8n to production
- Deploy Dashboard to hosting
- Train your team

### 4. Advanced Features (Later)

- Enable self-healing mode
- Configure Jira integration
- Set up Slack notifications
- Implement auto-retry logic

---

## Get Help

### Documentation

**Quick Starts:**
- [QUICK-START-GITHUB-JENKINS.md](QUICK-START-GITHUB-JENKINS.md) - Complete setup
- [MONGODB-QUICKSTART.md](MONGODB-QUICKSTART.md) - Database setup

**Detailed Guides:**
- [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) - Production deployment
- [GITHUB-JENKINS-INTEGRATION-GUIDE.md](GITHUB-JENKINS-INTEGRATION-GUIDE.md) - Integration details

**Architecture:**
- [architecture/COMPLETE-ARCHITECTURE.md](architecture/COMPLETE-ARCHITECTURE.md)
- [PROJECT-COMPLETION-SUMMARY.md](PROJECT-COMPLETION-SUMMARY.md)

### Common Commands

```bash
# Start system
docker-compose up -d

# Stop system
docker-compose down

# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f dashboard-ui
docker-compose logs -f n8n

# Restart service
docker-compose restart dashboard-ui

# Check status
docker ps

# Stop and remove all data (⚠️ WARNING: Deletes database)
docker-compose down -v
```

---

## Success Checklist

After setup, you should have:

✅ All Docker services running (`docker ps` shows 13 containers)
✅ Dashboard accessible at http://localhost:3000
✅ n8n accessible at http://localhost:5678
✅ Can trigger manual analysis
✅ Results appear in Dashboard
✅ MongoDB storing data
✅ GitHub links working (if configured)
✅ Jenkins integration (optional) working

**Time to complete:** 5-15 minutes depending on option chosen

---

## What Makes This System Special?

🎯 **Manual Trigger** - No waiting for aging days
⚡ **Fast** - 15 seconds vs 60 minutes
💰 **Cheap** - $0.05 vs $1.50 per analysis
🔗 **Direct Links** - Click to exact file:line on GitHub
💬 **User Feedback** - Refine results with your knowledge
🧠 **Smart Routing** - RAG for common, MCP for complex
📊 **Complete Visibility** - Dashboard shows everything

---

## Ready to Start?

**Choose your path:**

1. **Quick Demo** → Run `scripts/start-system.bat` → Open http://localhost:3000
2. **Full Setup** → Follow [QUICK-START-GITHUB-JENKINS.md](QUICK-START-GITHUB-JENKINS.md)
3. **Learn First** → Read [PROJECT-COMPLETION-SUMMARY.md](PROJECT-COMPLETION-SUMMARY.md)

**Questions?** Check the guides above or the [README.md](README.md)

---

**Last Updated**: October 22, 2025
**Version**: 1.0
**Status**: Ready to Use ✅

**Let's get started! 🚀**
