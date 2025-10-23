# DDN AI System - Complete Deployment Guide

**Last Updated**: October 22, 2025

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [GitHub Repository Setup](#github-repository-setup)
3. [Jenkins Configuration](#jenkins-configuration)
4. [Environment Configuration](#environment-configuration)
5. [Starting the System](#starting-the-system)
6. [Workflow Configuration](#workflow-configuration)
7. [Dashboard Access](#dashboard-access)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

- ✅ Docker Desktop installed (version 20.10+)
- ✅ Docker Compose installed (version 2.0+)
- ✅ Git installed
- ✅ 8GB RAM minimum
- ✅ 20GB disk space
- ✅ Port availability: 3000, 5000, 5005, 5678, 27017, 5432

### API Keys Required

- Anthropic API Key (for Claude AI)
- OpenAI API Key (for embeddings)
- Pinecone API Key (for vector storage)
- GitHub Personal Access Token
- Jenkins API Token (optional, for self-healing)

---

## GitHub Repository Setup

### Step 1: Create GitHub Repository

```bash
# Navigate to GitHub and create a new repository
# Repository name: ddn-ai-test-analysis
# Visibility: Private (recommended)
```

### Step 2: Initialize Local Repository

```bash
cd C:\DDN-AI-Project-Documentation

# Initialize git (if not already done)
git init

# Add remote
git remote add origin https://github.com/your-org/ddn-ai-test-analysis.git

# Create .gitignore
echo ".env" >> .gitignore
echo "node_modules/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".vscode/" >> .gitignore

# Commit and push
git add .
git commit -m "Initial commit: DDN AI Test Analysis System"
git push -u origin main
```

### Step 3: GitHub Folder Structure

Your repository now contains:

```
ddn-ai-test-analysis/
├── .github/
│   ├── workflows/
│   │   └── ci-cd.yml              # GitHub Actions CI/CD
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
├── jenkins/
│   ├── webhook-config.json        # Webhook configuration
│   └── Jenkinsfile.test           # Example test pipeline
├── scripts/
│   ├── start-system.bat           # Windows startup
│   └── start-system.sh            # Linux/Mac startup
├── implementation/                # All application code
├── architecture/                  # Architecture docs
├── docker-compose.yml            # All services
├── Jenkinsfile                   # Main pipeline
├── .env.example                  # Environment template
└── README.md                     # Main documentation
```

---

## Jenkins Configuration

### Step 1: Install Jenkins Plugin

1. Navigate to **Jenkins > Manage Jenkins > Manage Plugins**
2. Search for **"Generic Webhook Trigger Plugin"**
3. Install and restart Jenkins

### Step 2: Configure Webhook in Jenkins Job

Add to your Jenkins test job:

```groovy
// In your Jenkinsfile or job configuration

post {
    always {
        script {
            if (currentBuild.result == 'FAILURE') {
                // Prepare webhook payload
                def payload = [
                    build_id: "${env.BUILD_TAG}",
                    job_name: "${env.JOB_NAME}",
                    build_number: env.BUILD_NUMBER.toInteger(),
                    status: "FAILURE",
                    timestamp: new Date().format("yyyy-MM-dd'T'HH:mm:ss'Z'"),
                    build_url: "${env.BUILD_URL}",
                    console_log_url: "${env.BUILD_URL}console"
                ]

                // Send to n8n webhook
                httpRequest(
                    url: 'http://n8n:5678/webhook/ddn-test-failure',
                    httpMode: 'POST',
                    contentType: 'APPLICATION_JSON',
                    requestBody: groovy.json.JsonOutput.toJson(payload)
                )
            }
        }
    }
}
```

### Step 3: Test Jenkins Integration

```bash
# Trigger a test build
curl -X POST http://localhost:8080/job/YOUR_JOB/build \
  --user admin:your-jenkins-token
```

---

## Environment Configuration

### Step 1: Copy Environment Template

```bash
cd C:\DDN-AI-Project-Documentation
copy .env.example .env
```

### Step 2: Configure API Keys

Edit `.env` file:

```env
# AI & ML APIs
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
PINECONE_API_KEY=xxxxx
PINECONE_INDEX_NAME=test-failures

# GitHub
GITHUB_TOKEN=ghp_xxxxx
GITHUB_REPO=your-org/your-repo

# Jenkins (optional)
JENKINS_URL=http://localhost:8080
JENKINS_USER=admin
JENKINS_TOKEN=xxxxx
```

### Step 3: Verify Configuration

```bash
# Check .env file exists
dir .env

# Verify no secrets in git
git status
# .env should appear in .gitignore
```

---

## Starting the System

### Option 1: Windows (Automated)

```cmd
cd C:\DDN-AI-Project-Documentation
scripts\start-system.bat
```

### Option 2: Linux/Mac (Automated)

```bash
cd /path/to/DDN-AI-Project-Documentation
chmod +x scripts/start-system.sh
./scripts/start-system.sh
```

### Option 3: Manual Docker Compose

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Verify Services Are Running

```bash
# Check all containers
docker ps

# Test endpoints
curl http://localhost:3000        # Dashboard UI
curl http://localhost:5005/health # Dashboard API
curl http://localhost:5678        # n8n
curl http://localhost:5000/health # LangGraph
```

---

## Workflow Configuration

### Step 1: Access n8n

Open browser: http://localhost:5678

**Default credentials:**
- Username: `admin`
- Password: `password`

### Step 2: Import Workflows

1. Click **"Workflows"** → **"Import from File"**
2. Import these files in order:
   - `implementation/workflows/ddn_ai_complete_workflow.json`
   - `implementation/workflows/workflow_2_manual_trigger.json`
   - `implementation/workflows/workflow_3_refinement.json`

### Step 3: Configure MongoDB Credentials in n8n

1. Go to **Settings** → **Credentials**
2. Add **MongoDB** credential:
   - Connection String: `mongodb://admin:password@mongodb:27017/`
   - Database: `jenkins_failure_analysis`

### Step 4: Activate Workflows

1. Open each workflow
2. Click **"Active"** toggle in top-right
3. Verify webhook URLs:
   - Auto-trigger: `http://localhost:5678/webhook/ddn-test-failure`
   - Manual trigger: `http://localhost:5678/webhook/ddn-manual-trigger`
   - Refinement: `http://localhost:5678/webhook/ddn-refinement`

---

## Dashboard Access

### Dashboard UI

Open browser: http://localhost:3000

**Features:**
- View all test failures
- Click **"Analyze Now"** to trigger analysis
- View analysis results with GitHub/Jenkins links
- Provide feedback for refinement
- View analytics and metrics

### Dashboard API

API Base URL: http://localhost:5005

**Endpoints:**
- `GET /api/failures` - List all failures
- `GET /api/failures/:id` - Get failure details
- `POST /api/trigger-analysis` - Trigger manual analysis
- `POST /api/feedback` - Submit feedback for refinement
- `GET /health` - Health check

### Test Manual Trigger

```bash
curl -X POST http://localhost:5678/webhook/ddn-manual-trigger \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "SAMPLE_12345",
    "user_email": "test@example.com"
  }'
```

---

## Workflow Trigger from Dashboard

### Frontend Button Example

```javascript
// In your React dashboard
const handleAnalyze = async (buildId) => {
  try {
    const response = await fetch('http://localhost:5005/api/trigger-analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        build_id: buildId,
        user_email: 'user@example.com'
      })
    });

    const result = await response.json();
    console.log('Analysis triggered:', result);
  } catch (error) {
    console.error('Failed to trigger analysis:', error);
  }
};

// In your component
<button onClick={() => handleAnalyze(failure.build_id)}>
  Analyze Now
</button>
```

This is already implemented in: `implementation/dashboard-ui/src/pages/Failures.jsx:145`

---

## Data Storage

### MongoDB Collections

Database: `jenkins_failure_analysis`

Collections created automatically:
- `builds` - Build information
- `console_logs` - Console output
- `test_results` - Test execution results
- `analysis_solutions` - AI analysis results
- `refinement_history` - User feedback tracking

### PostgreSQL Tables

Database: `ddn_ai_analysis`

Tables created from: `implementation/postgresql_schema.sql`

---

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker --version

# Check logs
docker-compose logs

# Restart services
docker-compose restart
```

### Can't Access Dashboard

```bash
# Check if port 3000 is in use
netstat -ano | findstr :3000

# Check dashboard logs
docker-compose logs dashboard-ui
```

### n8n Workflows Not Triggering

1. Check workflow is activated (green toggle)
2. Verify webhook URLs are correct
3. Check n8n logs: `docker-compose logs n8n`
4. Test webhook manually with curl

### MongoDB Connection Failed

```bash
# Check MongoDB is running
docker-compose ps mongodb

# Test connection
docker exec -it ddn-mongodb mongosh -u admin -p password

# Verify data
use jenkins_failure_analysis
db.builds.find()
```

### API Keys Not Working

1. Verify `.env` file exists
2. Check no extra spaces in API keys
3. Restart services after changing `.env`:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

---

## Monitoring and Logs

### View All Logs

```bash
docker-compose logs -f
```

### View Specific Service Logs

```bash
docker-compose logs -f dashboard-ui
docker-compose logs -f n8n
docker-compose logs -f langgraph-service
docker-compose logs -f mongodb
```

### Check Service Health

```bash
# Dashboard API
curl http://localhost:5005/health

# LangGraph Service
curl http://localhost:5000/health
```

---

## Stopping the System

### Stop All Services

```bash
docker-compose down
```

### Stop and Remove Data

```bash
# WARNING: This deletes all database data!
docker-compose down -v
```

### Stop Specific Service

```bash
docker-compose stop dashboard-ui
docker-compose start dashboard-ui
```

---

## Next Steps

After successful deployment:

1. ✅ Configure Jenkins webhooks in your test jobs
2. ✅ Train team on using the dashboard
3. ✅ Set up production MongoDB Atlas (see MONGODB-QUICKSTART.md)
4. ✅ Configure notifications (Slack, Teams)
5. ✅ Monitor system performance
6. ✅ Review and optimize workflows

---

## Support

**Documentation:**
- Main README: [README.md](README.md)
- MongoDB Setup: [MONGODB-QUICKSTART.md](MONGODB-QUICKSTART.md)
- Architecture: [architecture/COMPLETE-ARCHITECTURE.md](architecture/COMPLETE-ARCHITECTURE.md)

**Quick Commands:**
```bash
# Start system
docker-compose up -d

# View logs
docker-compose logs -f

# Stop system
docker-compose down

# Restart service
docker-compose restart <service-name>
```

---

**Last Updated**: October 22, 2025
**Version**: 2.0
**Status**: Production Ready ✅
