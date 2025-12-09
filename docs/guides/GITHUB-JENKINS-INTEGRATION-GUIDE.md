# GitHub + Jenkins + Dashboard Integration Guide

**Complete workflow automation setup**

---

## Overview

This guide explains how to integrate:
1. **GitHub** - Source code repository
2. **Jenkins** - CI/CD pipeline and test execution
3. **n8n Workflows** - Automation and AI analysis
4. **Dashboard** - User interface to trigger workflows

---

## Architecture Flow

```
GitHub Push
    ↓
Jenkins Build & Test
    ↓
Test Failure Detected
    ↓
Jenkins Webhook → n8n (Auto-trigger)
    ↓
Store in MongoDB + PostgreSQL
    ↓
Dashboard Shows Failure
    ↓
User Clicks "Analyze Now"
    ↓
Dashboard → n8n (Manual trigger)
    ↓
LangGraph Classification
    ↓
Claude AI Analysis
    ↓
Results Back to Dashboard
```

---

## Part 1: GitHub Repository Setup

### Create GitHub Repository

1. **Create new repository:**
   ```bash
   # On GitHub.com
   Repository name: ddn-ai-test-analysis
   Visibility: Private
   Initialize with: README
   ```

2. **Clone locally:**
   ```bash
   git clone https://github.com/your-org/ddn-ai-test-analysis.git
   cd ddn-ai-test-analysis
   ```

3. **Copy project files:**
   ```bash
   # Copy all files from C:\DDN-AI-Project-Documentation
   # to your cloned repository
   ```

4. **Create folder structure:**
   ```
   ddn-ai-test-analysis/
   ├── .github/
   │   ├── workflows/
   │   │   └── ci-cd.yml
   │   └── ISSUE_TEMPLATE/
   ├── implementation/
   ├── jenkins/
   ├── scripts/
   └── docker-compose.yml
   ```

5. **Configure .gitignore:**
   ```bash
   echo ".env" >> .gitignore
   echo "node_modules/" >> .gitignore
   echo "__pycache__/" >> .gitignore
   echo "*.log" >> .gitignore
   ```

6. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Initial setup: DDN AI Test Analysis System"
   git push origin main
   ```

### GitHub Actions Configuration

The `.github/workflows/ci-cd.yml` file automatically runs on:
- Push to `main` or `develop` branches
- Pull requests
- Manual workflow dispatch

**What it does:**
- Builds Docker images
- Runs tests
- Starts services
- Performs health checks
- Deploys (on main branch)

---

## Part 2: Jenkins Setup

### Install Jenkins

#### Option 1: Docker (Recommended)

```bash
docker run -d \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  --name jenkins \
  jenkins/jenkins:lts
```

#### Option 2: Windows Installer

Download from: https://www.jenkins.io/download/

### Initial Jenkins Configuration

1. **Access Jenkins:**
   - Open: http://localhost:8080
   - Get initial password: `docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword`

2. **Install plugins:**
   - Install suggested plugins
   - Additional required plugins:
     - Generic Webhook Trigger Plugin
     - HTTP Request Plugin
     - Git Plugin

3. **Create admin user:**
   - Username: `admin`
   - Password: (your choice)
   - Generate API token: User → Configure → API Token

### Configure Jenkins Job

1. **Create new Pipeline Job:**
   ```
   New Item → Pipeline → Name: "DDN-Test-Job"
   ```

2. **Configure SCM:**
   ```
   Pipeline → Definition: Pipeline script from SCM
   SCM: Git
   Repository URL: https://github.com/your-org/ddn-ai-test-analysis.git
   Script Path: jenkins/Jenkinsfile.test
   ```

3. **Add webhook trigger:**
   ```groovy
   // In your Jenkinsfile
   post {
       always {
           script {
               if (currentBuild.result == 'FAILURE') {
                   def payload = [
                       build_id: "${env.BUILD_TAG}",
                       job_name: "${env.JOB_NAME}",
                       build_number: env.BUILD_NUMBER.toInteger(),
                       status: "FAILURE",
                       timestamp: new Date().format("yyyy-MM-dd'T'HH:mm:ss'Z'"),
                       build_url: "${env.BUILD_URL}",
                       console_log_url: "${env.BUILD_URL}console"
                   ]

                   httpRequest(
                       url: 'http://host.docker.internal:5678/webhook/ddn-test-failure',
                       httpMode: 'POST',
                       contentType: 'APPLICATION_JSON',
                       requestBody: groovy.json.JsonOutput.toJson(payload),
                       validResponseCodes: '200:299'
                   )
               }
           }
       }
   }
   ```

4. **Test the job:**
   ```bash
   # Trigger build
   curl -X POST http://localhost:8080/job/DDN-Test-Job/build \
     --user admin:your-jenkins-token
   ```

---

## Part 3: n8n Workflow Configuration

### Start n8n Service

```bash
docker-compose up -d n8n
```

Access: http://localhost:5678

### Import Workflows

1. **Workflow 1: Auto-trigger (Jenkins webhook)**
   - File: `implementation/workflows/ddn_ai_complete_workflow.json`
   - Webhook: `/webhook/ddn-test-failure`
   - Trigger: Jenkins sends failure data

2. **Workflow 2: Manual trigger (Dashboard button)**
   - File: `implementation/workflows/workflow_2_manual_trigger.json`
   - Webhook: `/webhook/ddn-manual-trigger`
   - Trigger: User clicks "Analyze Now"

3. **Workflow 3: Refinement (User feedback)**
   - File: `implementation/workflows/workflow_3_refinement.json`
   - Webhook: `/webhook/ddn-refinement`
   - Trigger: User provides feedback

### Configure Workflow Webhooks

Each workflow has a webhook node:

```
Workflow 1 (Auto):
- URL: http://localhost:5678/webhook/ddn-test-failure
- Method: POST
- Responds: 200 OK

Workflow 2 (Manual):
- URL: http://localhost:5678/webhook/ddn-manual-trigger
- Method: POST
- Body: { build_id, user_email }

Workflow 3 (Refinement):
- URL: http://localhost:5678/webhook/ddn-refinement
- Method: POST
- Body: { build_id, feedback, user_email }
```

### Activate Workflows

1. Open each workflow
2. Click "Active" toggle (top-right)
3. Test with curl:

```bash
# Test Manual Trigger
curl -X POST http://localhost:5678/webhook/ddn-manual-trigger \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "TEST_123",
    "user_email": "test@example.com"
  }'
```

---

## Part 4: Dashboard Integration

### Dashboard API Endpoints

The `dashboard_api.py` provides these endpoints:

```python
# Trigger workflow from dashboard
POST /api/trigger-analysis
Body: {
  "build_id": "string",
  "user_email": "string"
}

# Response:
{
  "status": "analysis_triggered",
  "build_id": "TEST_123",
  "webhook_url": "http://n8n:5678/webhook/ddn-manual-trigger"
}
```

### Frontend Button Implementation

Already implemented in `implementation/dashboard-ui/src/pages/Failures.jsx`:

```javascript
const handleAnalyze = async (buildId) => {
  try {
    setLoading(true);

    const response = await fetch('http://localhost:5005/api/trigger-analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        build_id: buildId,
        user_email: currentUser.email
      })
    });

    const result = await response.json();

    if (result.status === 'analysis_triggered') {
      showNotification('Analysis started! Results will appear shortly.');
      // Poll for results
      pollAnalysisResults(buildId);
    }
  } catch (error) {
    showError('Failed to trigger analysis');
  } finally {
    setLoading(false);
  }
};
```

### How It Works

1. **User clicks "Analyze Now" button**
   - Button in Failures.jsx line 145
   - Sends POST to Dashboard API

2. **Dashboard API receives request**
   - Validates build_id exists
   - Forwards to n8n webhook

3. **n8n Workflow 2 triggered**
   - Retrieves failure data from MongoDB
   - Sends to LangGraph for classification
   - Calls Claude AI for analysis

4. **Results stored in MongoDB**
   - Collection: `analysis_solutions`
   - Links to build_id

5. **Dashboard polls for results**
   - Every 5 seconds
   - Updates UI when analysis complete
   - Shows GitHub/Jenkins links

---

## Part 5: Complete Integration Test

### Step-by-Step Test

**1. Start all services:**
```bash
cd C:\DDN-AI-Project-Documentation
docker-compose up -d
```

**2. Verify services:**
```bash
curl http://localhost:3000        # Dashboard UI
curl http://localhost:5005/health # Dashboard API
curl http://localhost:5678        # n8n
curl http://localhost:8080        # Jenkins
```

**3. Create test failure in Jenkins:**
```bash
# Trigger Jenkins job that will fail
curl -X POST http://localhost:8080/job/DDN-Test-Job/build \
  --user admin:your-jenkins-token
```

**4. Jenkins sends webhook to n8n:**
- Jenkins detects failure
- Sends POST to `http://host.docker.internal:5678/webhook/ddn-test-failure`
- n8n Workflow 1 processes it

**5. Check data stored:**
```bash
# Connect to MongoDB
docker exec -it ddn-mongodb mongosh -u admin -p password

# Check data
use jenkins_failure_analysis
db.builds.find().pretty()
```

**6. View in Dashboard:**
- Open: http://localhost:3000
- Navigate to Failures page
- See the new failure listed

**7. Trigger analysis from Dashboard:**
- Click "Analyze Now" button
- n8n Workflow 2 triggered
- Wait 10-15 seconds
- See analysis results

**8. Verify GitHub links work:**
- Click "View in GitHub" link
- Should open exact file:line in browser

---

## Part 6: Production Deployment

### GitHub Repository

1. **Push to production branch:**
   ```bash
   git checkout main
   git pull origin main
   git push origin main
   ```

2. **GitHub Actions deploys automatically**
   - Builds Docker images
   - Runs tests
   - Deploys to server

### Jenkins Production

1. **Configure production Jenkins:**
   - Update webhook URLs to production n8n
   - Use production API tokens
   - Configure all test jobs

2. **Update .env for production:**
   ```env
   # Production n8n URL
   N8N_URL=https://n8n.yourcompany.com

   # Production MongoDB
   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
   ```

### n8n Production

1. **Deploy n8n to cloud:**
   - Use n8n cloud: https://n8n.io/cloud
   - Or self-host with Docker

2. **Update webhook URLs in Jenkins:**
   ```groovy
   url: 'https://n8n.yourcompany.com/webhook/ddn-test-failure'
   ```

### Dashboard Production

1. **Build for production:**
   ```bash
   cd implementation/dashboard-ui
   npm run build
   ```

2. **Deploy to server:**
   - Use Netlify, Vercel, or your server
   - Update API URL in environment

---

## Workflow Trigger Methods

### Method 1: Jenkins Auto-Trigger
```
Jenkins detects failure
    → Sends webhook to n8n
    → Workflow 1 executes automatically
```

### Method 2: Dashboard Manual Trigger
```
User clicks "Analyze Now"
    → Dashboard API calls n8n webhook
    → Workflow 2 executes on-demand
```

### Method 3: API Direct Trigger
```bash
curl -X POST http://localhost:5678/webhook/ddn-manual-trigger \
  -H "Content-Type: application/json" \
  -d '{"build_id": "BUILD_123", "user_email": "user@company.com"}'
```

### Method 4: Scheduled Trigger (n8n)
```
n8n Cron node
    → Runs daily at 2 AM
    → Analyzes all failures with aging >= 5 days
```

---

## Monitoring and Debugging

### View Workflow Execution

1. **n8n Executions:**
   - Open n8n: http://localhost:5678
   - Click "Executions" tab
   - See all workflow runs with inputs/outputs

2. **Dashboard API Logs:**
   ```bash
   docker-compose logs -f dashboard-api
   ```

3. **n8n Logs:**
   ```bash
   docker-compose logs -f n8n
   ```

### Common Issues

**Webhook not triggering:**
- Check Jenkins plugin installed
- Verify URL: `http://host.docker.internal:5678/webhook/...`
- Check n8n workflow is Active

**Dashboard button not working:**
- Check Dashboard API is running: `curl http://localhost:5005/health`
- Verify n8n webhook URL in dashboard_api.py
- Check browser console for errors

**Analysis not completing:**
- Check LangGraph service: `docker-compose logs langgraph-service`
- Verify API keys in .env
- Check MongoDB connection

---

## Summary Checklist

✅ **GitHub:**
- [ ] Repository created
- [ ] Code pushed
- [ ] GitHub Actions configured
- [ ] .gitignore includes .env

✅ **Jenkins:**
- [ ] Jenkins installed
- [ ] Plugins installed (Generic Webhook, HTTP Request)
- [ ] Test job created
- [ ] Webhook configured in Jenkinsfile
- [ ] API token generated

✅ **n8n:**
- [ ] Service running (port 5678)
- [ ] 3 workflows imported
- [ ] All workflows activated
- [ ] MongoDB credentials configured
- [ ] Webhooks tested

✅ **Dashboard:**
- [ ] Dashboard UI running (port 3000)
- [ ] Dashboard API running (port 5005)
- [ ] "Analyze Now" button works
- [ ] Results display correctly
- [ ] GitHub/Jenkins links work

✅ **Integration Test:**
- [ ] Jenkins triggers n8n on failure
- [ ] Data appears in Dashboard
- [ ] Manual trigger from Dashboard works
- [ ] Analysis results displayed
- [ ] All services healthy

---

## Next Steps

1. Configure production MongoDB Atlas
2. Set up production n8n instance
3. Deploy Dashboard to production
4. Train team on using the system
5. Monitor and optimize workflows

---

**Documentation References:**
- [Deployment Guide](DEPLOYMENT-GUIDE.md)
- [MongoDB Setup](MONGODB-QUICKSTART.md)
- [Workflow Overview](implementation/workflows/COMPLETE_SYSTEM_OVERVIEW.md)
- [Dashboard Guide](implementation/dashboard/DASHBOARD_INTEGRATION_GUIDE.md)

---

**Last Updated**: October 22, 2025
**Status**: Production Ready ✅
