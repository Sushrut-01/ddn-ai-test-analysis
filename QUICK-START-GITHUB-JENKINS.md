# Quick Start: GitHub + Jenkins + Dashboard Workflow

**Get the complete system running in 15 minutes**

---

## What You'll Get

✅ **GitHub repository** with all code
✅ **Jenkins pipeline** auto-triggering on test failures
✅ **n8n workflows** processing failures
✅ **Dashboard** to manually trigger analysis
✅ **Complete automation** from GitHub push to AI analysis

---

## Prerequisites (2 minutes)

```bash
# Check you have these installed
docker --version        # Should be 20.10+
docker-compose --version # Should be 2.0+
git --version           # Any version
```

---

## Step 1: GitHub Setup (3 minutes)

### Create Repository

```bash
# 1. Go to https://github.com/new
# Repository name: ddn-ai-test-analysis
# Visibility: Private
# Click "Create repository"

# 2. Clone locally
cd C:\
git clone https://github.com/your-org/ddn-ai-test-analysis.git
cd ddn-ai-test-analysis

# 3. Copy project files
# Copy everything from C:\DDN-AI-Project-Documentation to here

# 4. Push to GitHub
git add .
git commit -m "Initial setup"
git push origin main
```

**Done! ✅** Repository created with all files

---

## Step 2: Configure Environment (2 minutes)

```bash
# 1. Copy environment template
copy .env.example .env

# 2. Edit .env file (use notepad or VS Code)
notepad .env
```

**Add your API keys:**
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
PINECONE_API_KEY=your-key-here
GITHUB_TOKEN=ghp_your-token-here
```

**Get API keys:**
- Anthropic: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/api-keys
- Pinecone: https://www.pinecone.io/
- GitHub: https://github.com/settings/tokens

**Done! ✅** Environment configured

---

## Step 3: Start All Services (5 minutes)

### Windows

```cmd
cd C:\DDN-AI-Project-Documentation
scripts\start-system.bat
```

### Linux/Mac

```bash
cd /path/to/DDN-AI-Project-Documentation
chmod +x scripts/start-system.sh
./scripts/start-system.sh
```

**What it does:**
- Builds Docker images (2-3 min)
- Starts MongoDB, PostgreSQL, n8n, Dashboard, APIs
- Runs health checks
- Shows access URLs

**Wait for:** "System Started Successfully!" message

**Done! ✅** All services running

---

## Step 4: Verify Services (1 minute)

Open these URLs in browser:

```
✅ Dashboard:    http://localhost:3000
✅ n8n:          http://localhost:5678
✅ Dashboard API: http://localhost:5005
```

**n8n login:**
- Username: `admin`
- Password: `password`

**Done! ✅** Services accessible

---

## Step 5: Import n8n Workflows (2 minutes)

1. **Open n8n:** http://localhost:5678

2. **Import workflows:**
   - Click "Workflows" → "Import from File"
   - Select: `implementation/workflows/ddn_ai_complete_workflow_v2.json`
   - Click "Import"
   - Repeat for:
     - `workflow_2_manual_trigger.json`
     - `workflow_3_refinement.json`

3. **Activate workflows:**
   - Open each workflow
   - Click "Active" toggle (top-right)

**Done! ✅** Workflows ready

---

## Step 6: Configure Jenkins (Optional - 5 minutes)

### Option A: Use Existing Jenkins

If you have Jenkins running:

```groovy
// Add to your Jenkinsfile
post {
    always {
        script {
            if (currentBuild.result == 'FAILURE') {
                def payload = [
                    build_id: "${env.BUILD_TAG}",
                    job_name: "${env.JOB_NAME}",
                    build_number: env.BUILD_NUMBER.toInteger(),
                    status: "FAILURE",
                    build_url: "${env.BUILD_URL}"
                ]

                httpRequest(
                    url: 'http://host.docker.internal:5678/webhook/ddn-test-failure',
                    httpMode: 'POST',
                    contentType: 'APPLICATION_JSON',
                    requestBody: groovy.json.JsonOutput.toJson(payload)
                )
            }
        }
    }
}
```

### Option B: Start Jenkins with Docker

```bash
docker run -d \
  -p 8080:8080 \
  --name jenkins \
  jenkins/jenkins:lts
```

**Done! ✅** Jenkins configured

---

## Step 7: Test the Complete Workflow

### Test 1: Manual Trigger from Dashboard

```bash
# 1. Open Dashboard
http://localhost:3000

# 2. Click "Manual Trigger" tab

# 3. Enter test data:
Build ID: TEST_123
Job Name: DDN-Smoke-Test

# 4. Click "Trigger Analysis"

# 5. See results appear (10-15 seconds)
```

**Expected:**
- ✅ Analysis triggered
- ✅ Loading indicator shown
- ✅ Results displayed with GitHub/Jenkins links
- ✅ Confidence score shown

### Test 2: API Trigger

```bash
curl -X POST http://localhost:5678/webhook/ddn-manual-trigger \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "TEST_456",
    "user_email": "test@example.com"
  }'
```

**Expected:**
- ✅ Returns: `{"status": "success"}`
- ✅ Check n8n executions
- ✅ Check MongoDB for data

### Test 3: Jenkins Auto-Trigger (if Jenkins configured)

```bash
# Trigger a failing Jenkins job
curl -X POST http://localhost:8080/job/YOUR_JOB/build \
  --user admin:your-jenkins-token
```

**Expected:**
- ✅ Jenkins job fails
- ✅ Webhook sent to n8n
- ✅ Failure appears in Dashboard
- ✅ Can click "Analyze Now"

**Done! ✅** Complete workflow tested

---

## Access Points Summary

| Service | URL | Credentials |
|---------|-----|-------------|
| **Dashboard UI** | http://localhost:3000 | None |
| **n8n Workflows** | http://localhost:5678 | admin / password |
| **Dashboard API** | http://localhost:5005 | None |
| **MongoDB** | localhost:27017 | admin / password |
| **PostgreSQL** | localhost:5432 | postgres / password |
| **Jenkins** | http://localhost:8080 | admin / (your password) |

---

## Workflow Trigger Methods

### Method 1: Dashboard Button (Manual)

```
User opens Dashboard
    → Clicks "Analyze Now"
    → n8n Workflow 2 triggered
    → Results in 10-15 seconds
```

**Use case:** On-demand analysis without waiting for aging days

### Method 2: Jenkins Webhook (Auto)

```
Jenkins job fails
    → Sends webhook to n8n
    → n8n Workflow 1 triggered
    → Stored in MongoDB
    → Appears in Dashboard
```

**Use case:** Automatic capture of all test failures

### Method 3: API Call (Programmatic)

```bash
curl -X POST http://localhost:5005/api/trigger-analysis \
  -H "Content-Type: application/json" \
  -d '{"build_id": "BUILD_789"}'
```

**Use case:** Integration with other tools/scripts

---

## Common Commands

### Start System
```bash
cd C:\DDN-AI-Project-Documentation
docker-compose up -d
```

### Stop System
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f dashboard-ui
docker-compose logs -f n8n
```

### Restart Service
```bash
docker-compose restart dashboard-ui
```

### Check Service Health
```bash
curl http://localhost:3000        # Dashboard UI
curl http://localhost:5005/health # Dashboard API
curl http://localhost:5678        # n8n
```

---

## Verify Data Storage

### MongoDB

```bash
# Connect to MongoDB
docker exec -it ddn-mongodb mongosh -u admin -p password

# Use database
use jenkins_failure_analysis

# View builds
db.builds.find().pretty()

# View analysis results
db.analysis_solutions.find().pretty()

# Exit
exit
```

### PostgreSQL

```bash
# Connect to PostgreSQL
docker exec -it ddn-postgres psql -U postgres -d ddn_ai_analysis

# List tables
\dt

# View data
SELECT * FROM test_failures LIMIT 5;

# Exit
\q
```

---

## Dashboard Features

### Failures Page

- View all test failures
- Filter by job name, status, aging
- Click "Analyze Now" for instant analysis
- View analysis results inline
- GitHub/Jenkins direct links

### Manual Trigger Page

- Enter any build ID
- Trigger analysis on-demand
- No aging requirement
- See immediate results

### Analytics Page

- View failure trends
- Success/failure rates
- Most common error types
- Time-to-resolution metrics

---

## GitHub Integration

### View Exact Code Location

When analysis completes, you get:

```
Related Files:
├─ DDNStorage.java:127  [View in GitHub →]
└─ ConfigLoader.java:45  [View in GitHub →]
```

**Clicking the link opens:**
```
https://github.com/your-org/your-repo/blob/main/src/DDNStorage.java#L127
```

**Exactly at the line with the error!**

### Commit Hooks (Optional)

Add to `.github/workflows/ci-cd.yml`:

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
```

**Automatically runs:**
- Build and test
- Docker image creation
- Health checks
- Deployment (on main)

---

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker --version

# Check ports are free
netstat -ano | findstr :3000
netstat -ano | findstr :5678

# Restart Docker Desktop

# Try again
docker-compose up -d
```

### Can't Access Dashboard

```bash
# Check if running
docker ps | findstr dashboard

# Check logs
docker-compose logs dashboard-ui

# Restart
docker-compose restart dashboard-ui
```

### n8n Workflow Not Triggering

1. Check workflow is Active (green toggle)
2. Test webhook:
   ```bash
   curl -X POST http://localhost:5678/webhook/ddn-manual-trigger \
     -H "Content-Type: application/json" \
     -d '{"build_id": "TEST"}'
   ```
3. Check n8n executions tab
4. View logs: `docker-compose logs n8n`

### MongoDB Connection Failed

```bash
# Check MongoDB running
docker ps | findstr mongodb

# Restart MongoDB
docker-compose restart mongodb

# Wait 10 seconds
timeout /t 10

# Test again
docker exec -it ddn-mongodb mongosh -u admin -p password
```

---

## What's Next?

### Phase 1: Testing (Today)
- ✅ Test manual triggers
- ✅ Test all workflows
- ✅ Verify data storage
- ✅ Check GitHub links work

### Phase 2: Jenkins Integration (This Week)
- Configure Jenkins webhooks
- Add to all test jobs
- Test auto-trigger flow

### Phase 3: Production (Next Week)
- Set up MongoDB Atlas (cloud)
- Deploy n8n to production
- Deploy Dashboard to production
- Train team

---

## Support Resources

**Documentation:**
- Full Deployment Guide: [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)
- Integration Guide: [GITHUB-JENKINS-INTEGRATION-GUIDE.md](GITHUB-JENKINS-INTEGRATION-GUIDE.md)
- MongoDB Setup: [MONGODB-QUICKSTART.md](MONGODB-QUICKSTART.md)
- Workflow Details: [implementation/workflows/COMPLETE_SYSTEM_OVERVIEW.md](implementation/workflows/COMPLETE_SYSTEM_OVERVIEW.md)

**Quick Commands:**
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Status
docker ps
```

---

## Success Checklist

After following this guide, you should have:

✅ GitHub repository with complete code
✅ All Docker services running
✅ n8n workflows activated
✅ Dashboard accessible and functional
✅ Manual trigger working
✅ Data stored in MongoDB
✅ GitHub links working
✅ Jenkins integration (optional) configured

**Total Time:** 15 minutes
**Status:** Production Ready ✅

---

**Last Updated**: October 22, 2025
**Version**: 1.0
**Maintained By**: Rysun Labs Development Team
