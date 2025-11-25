# DDN AI Project - Complete Services Reference
**Last Updated:** 2025-11-05
**Total Services:** 17
**Architecture:** Unified Docker Compose

---

## 📊 Service Overview

| # | Service Name | Type | Port(s) | Status | Priority |
|---|--------------|------|---------|--------|----------|
| 1 | MongoDB | Database | 27017 | To Deploy | CRITICAL |
| 2 | PostgreSQL (DDN) | Database | 5432 | To Deploy | CRITICAL |
| 3 | PostgreSQL (Langfuse) | Database | 5433 | To Deploy | CRITICAL |
| 4 | Redis | Cache/Broker | 6379 | To Deploy | CRITICAL |
| 5 | Langfuse Server | Monitoring | 3001 | To Deploy | HIGH |
| 6 | Flower | Monitoring | 5555 | To Deploy | HIGH |
| 7 | n8n | Workflow | 5678 | To Deploy | HIGH |
| 8 | Celery Worker | Task Queue | - | To Deploy | CRITICAL |
| 9 | LangGraph Service | AI Core | 5003 | To Deploy | CRITICAL |
| 10 | MCP MongoDB | MCP Server | 5001 | To Deploy | HIGH |
| 11 | MCP GitHub | MCP Server | 5002 | To Deploy | HIGH |
| 12 | Manual Trigger API | API | 5004 | To Deploy | CRITICAL |
| 13 | Dashboard API | API | 5006 | To Deploy | CRITICAL |
| 14 | Jira Service | Integration | 5007 | To Deploy | MEDIUM |
| 15 | Slack Service | Integration | 5008 | To Deploy | MEDIUM |
| 16 | Self-Healing Service | Integration | 5009 | To Deploy | MEDIUM |
| 17 | Dashboard UI | Frontend | 3000 | To Deploy | HIGH |

---

## 1️⃣ **MongoDB** (Unstructured Data Storage)

### Configuration
- **Connection:** The project requires a MongoDB connection string provided via the `MONGODB_URI` environment variable.
    - Example Atlas connection (replace placeholders):
        `mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net/ddn_ai_project?retryWrites=true&w=majority`
    - For local development you can run a local MongoDB and set `MONGODB_URI` to `mongodb://localhost:27017/<db>` but production and CI should use Atlas.

### Environment Variables
```bash
# Required: set your MongoDB connection string (Atlas recommended)
MONGODB_URI=mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net/ddn_ai_project?retryWrites=true&w=majority
MONGODB_DB=jenkins_failure_analysis
```

### Purpose
Stores unstructured test failure data, analysis results, and historical records (accessed via `MONGODB_URI`)

---

## 2️⃣ **PostgreSQL - DDN AI Analysis** (Structured Data Storage)

### Configuration
- **Container Name:** `ddn-postgres`
- **Image:** `postgres:16`
- **Port:** `5434` (external) / `5432` (internal) - *Changed to avoid conflict with native PostgreSQL*
- **Network:** `ddn-network`

### Environment Variables
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ddn_ai_analysis
```

### Volumes
- `postgres_data:/var/lib/postgresql/data`
- `./implementation/postgresql_schema.sql:/docker-entrypoint-initdb.d/init.sql`

### Health Check
```bash
pg_isready -U postgres
```

### Purpose
Stores structured data: test results, analysis history, user feedback, knowledge base

### Dependencies
None (Base infrastructure)

### Tables
- `test_failures` - Test failure records
- `analysis_results` - AI analysis outputs
- `user_feedback` - HITL feedback
- `knowledge_documents` - Document metadata
- `templates` - Solution templates
- And more (see `postgresql_schema.sql`)

### Access
```bash
# Connection string (external - from host machine)
postgresql://postgres:password@localhost:5434/ddn_ai_analysis

# CLI (external - from host machine)
psql -h localhost -p 5434 -U postgres -d ddn_ai_analysis

# Docker services connect internally via: postgres:5432
```

---

## 3️⃣ **PostgreSQL - Langfuse** (Observability Data)

### Configuration
- **Container Name:** `langfuse-postgres`
- **Image:** `postgres:15`
- **Port:** `5433` (mapped from internal 5432)
- **Network:** `ddn-network`

### Environment Variables
```bash
POSTGRES_USER=langfuse
POSTGRES_PASSWORD=langfuse123
POSTGRES_DB=langfuse
```

### Volumes
- `langfuse_db_data:/var/lib/postgresql/data`

### Health Check
```bash
pg_isready -U langfuse
```

### Purpose
Stores Langfuse observability data: LLM traces, generations, scores, prompts

### Dependencies
None (Base infrastructure for Langfuse)

### Access
```bash
# Connection string
postgresql://langfuse:langfuse123@localhost:5433/langfuse
```

---

## 4️⃣ **Redis** (Cache & Message Broker)

### Configuration
- **Container Name:** `ddn-redis`
- **Image:** `redis:latest`
- **Port:** `6379`
- **Network:** `ddn-network`

### Volumes
- `redis_data:/data`

### Health Check
```bash
redis-cli ping
```

### Purpose
- Caching layer for AI responses (60-75% hit rate, 50-100x speedup)
- Message broker for Celery task queue
- Session storage

### Dependencies
None (Base infrastructure)

### Configuration
- **TTL:** 3600 seconds (1 hour)
- **Max Connections:** 10
- **Database:** 0 (default)

### Access
```bash
# Connection string
redis://localhost:6379/0

# CLI
redis-cli -h localhost -p 6379
```

---

## 5️⃣ **Langfuse Server** (LLM Observability)

### Configuration
- **Container Name:** `langfuse-server`
- **Image:** `ghcr.io/langfuse/langfuse:2`
- **Port:** `3001` (changed from 3000 to avoid conflict)
- **Network:** `ddn-network`

### Environment Variables
```bash
DATABASE_URL=postgresql://langfuse:langfuse123@langfuse-db:5432/langfuse
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=very-secret-key-change-this-in-production-12345678
SALT=salt-change-this-in-production-abcdefgh
TELEMETRY_ENABLED=false
```

### Dependencies
- `langfuse-db` (PostgreSQL)

### Health Check
```bash
curl -f http://localhost:3001/api/public/health
```

### Purpose
Monitor and trace all LLM API calls (Gemini, OpenAI, Anthropic)

### Features
- Trace complete workflows
- Track token usage and costs
- Debug LLM performance issues
- Prompt versioning

### Web UI
http://localhost:3001

### API Keys
- **Public Key:** `pk-lf-99176382-54aa-40dc-8900-768db9fd0278`
- **Secret Key:** `sk-lf-158d4ee5-d9b7-47d9-87ab-217c4edb74e6`

---

## 6️⃣ **Flower** (Celery Monitoring)

### Configuration
- **Container Name:** `ddn-flower`
- **Build:** `implementation/Dockerfile`
- **Port:** `5555`
- **Network:** `ddn-network`

### Environment Variables
```bash
REDIS_URL=redis://redis:6379/0
```

### Dependencies
- `redis` (Message broker)

### Command
```bash
celery -A tasks.celery_tasks flower --port=5555 --broker=redis://redis:6379/0
```

### Purpose
Real-time monitoring of Celery task queue

### Features
- View active workers
- Monitor task success/failure rates
- Track queue lengths
- Task execution history

### Web UI
http://localhost:5555

---

## 7️⃣ **n8n** (Workflow Automation)

### Configuration
- **Container Name:** `ddn-n8n`
- **Image:** `n8nio/n8n:latest`
- **Port:** `5678`
- **Network:** `ddn-network`

### Environment Variables
```bash
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=password
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=postgres
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=postgres
DB_POSTGRESDB_PASSWORD=password
WEBHOOK_URL=http://localhost:5678/
```

### Volumes
- `n8n_data:/home/node/.n8n`
- `./implementation/workflows:/workflows`

### Dependencies
- `postgres` (DDN PostgreSQL)

### Purpose
Orchestrate automated workflows for test failure analysis

### Workflows
1. **Auto-Trigger Workflow:** Automatic failure analysis
2. **Manual Trigger Workflow:** On-demand analysis
3. **Refinement Workflow:** HITL feedback processing
4. **Code Fix Workflow:** Automated fix generation

### Web UI
http://localhost:5678

### Credentials
- **Username:** admin
- **Password:** password

---

## 8️⃣ **Celery Worker** (Async Task Processing)

### Configuration
- **Container Name:** `ddn-celery-worker`
- **Build:** `implementation/Dockerfile`
- **Network:** `ddn-network`

### Environment Variables
```bash
REDIS_URL=redis://redis:6379/0
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
GEMINI_API_KEY=${GEMINI_API_KEY}
MONGODB_URI=${MONGODB_URI}
PINECONE_API_KEY=${PINECONE_API_KEY}
LANGFUSE_ENABLED=true
LANGFUSE_HOST=http://langfuse-server:3000
LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
```

### Dependencies
- `redis` (Broker)
- `mongodb` (Data storage)

### Command
```bash
celery -A tasks.celery_tasks worker --loglevel=info --concurrency=4 --pool=solo
```

### Purpose
Execute async tasks: AI analysis, batch processing, cleanup

### Tasks
- `tasks.analyze_test_failure` - Single failure analysis
- `tasks.batch_analyze_failures` - Batch processing
- `tasks.cleanup_old_results` - Maintenance

### Configuration
- **Concurrency:** 4
- **Pool:** solo (Windows compatible)
- **Log Level:** info

---

## 9️⃣ **LangGraph Service** (AI Classification)

### Configuration
- **Container Name:** `ddn-langgraph`
- **Build:** `implementation/Dockerfile`
- **Port:** `5003` (changed from 5000)
- **Network:** `ddn-network`

### Environment Variables
```bash
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
GEMINI_API_KEY=${GEMINI_API_KEY}
MONGODB_URI=${MONGODB_URI}
MONGODB_DB=jenkins_failure_analysis
PINECONE_API_KEY=${PINECONE_API_KEY}
PINECONE_INDEX_NAME=test-failures
REDIS_URL=redis://redis:6379/0
LANGFUSE_ENABLED=true
LANGFUSE_HOST=http://langfuse-server:3000
```

### Dependencies
- `mongodb` (Data storage)
- `redis` (Caching)

### Command
```bash
python langgraph_agent.py
```

### Purpose
Core AI service for error classification and routing

### Features
- Multi-step reasoning with LangGraph
- Error classification (CODE_ERROR, ENVIRONMENT_ERROR, etc.)
- RAG query routing
- Redis caching integration

### Endpoints
- `POST /analyze-error` - Analyze single error
- `GET /health` - Health check
- `GET /cache-stats` - Cache statistics

### API URL
http://localhost:5003

---

## 🔟 **MCP MongoDB Server** (Database MCP)

### Configuration
- **Container Name:** `ddn-mcp-mongodb`
- **Build:** `mcp-configs/Dockerfile`
- **Port:** `5001`
- **Network:** `ddn-network`

### Environment Variables
```bash
MONGODB_URI=${MONGODB_URI}
MONGODB_DB=jenkins_failure_analysis
```

### Dependencies
- `mongodb`

### Command
```bash
python mcp_mongodb_server.py
```

### Purpose
Model Context Protocol server for MongoDB access

### API URL
http://localhost:5001

---

## 1️⃣1️⃣ **MCP GitHub Server** (Source Code MCP)

### Configuration
- **Container Name:** `ddn-mcp-github`
- **Build:** `mcp-configs/Dockerfile`
- **Port:** `5002`
- **Network:** `ddn-network`

### Environment Variables
```bash
GITHUB_TOKEN=${GITHUB_TOKEN}
GITHUB_REPO=${GITHUB_REPO}
```

### Dependencies
None

### Command
```bash
python mcp_github_server.py
```

### Purpose
Model Context Protocol server for GitHub source code access

### Features
- Fetch source code files
- Get specific line ranges
- Navigate repository structure
- Support for CODE_ERROR analysis

### API URL
http://localhost:5002

---

## 1️⃣2️⃣ **Manual Trigger API** (On-Demand Analysis)

### Configuration
- **Container Name:** `ddn-manual-trigger`
- **Build:** `implementation/Dockerfile`
- **Port:** `5004`
- **Network:** `ddn-network`

### Environment Variables
```bash
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ddn_ai_analysis
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
N8N_WEBHOOK_URL=http://n8n:5678/webhook/ddn-test-failure
```

### Dependencies
- `postgres` (DDN)

### Command
```bash
python manual_trigger_api.py
```

### Purpose
API for manually triggering test failure analysis

### Endpoints
- `POST /trigger-analysis` - Trigger analysis
- `GET /health` - Health check

### API URL
http://localhost:5004

---

## 1️⃣3️⃣ **Dashboard API** (Backend API)

### Configuration
- **Container Name:** `ddn-dashboard-api`
- **Build:** `implementation/Dockerfile`
- **Port:** `5006` (changed from 5005)
- **Network:** `ddn-network`

### Environment Variables
```bash
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ddn_ai_analysis
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
MONGODB_URI=${MONGODB_URI}
MONGODB_DB=jenkins_failure_analysis
MANUAL_TRIGGER_API=http://manual-trigger-api:5004
GITHUB_TOKEN=${GITHUB_TOKEN}
GITHUB_REPO=${GITHUB_REPO}
```

### Dependencies
- `postgres` (DDN)
- `mongodb`

### Command
```bash
python dashboard_api_full.py
```

### Purpose
Backend API for React dashboard

### Features
- Failure data retrieval
- Analytics and metrics
- Knowledge management
- User feedback handling
- GitHub integration

### Endpoints
- `GET /api/failures` - List failures
- `GET /api/analytics` - Analytics data
- `GET /api/knowledge` - Knowledge base
- `POST /api/feedback` - Submit feedback
- And 20+ more endpoints

### API URL
http://localhost:5006

---

## 1️⃣4️⃣ **Jira Service** (Jira Integration)

### Configuration
- **Container Name:** `ddn-jira`
- **Build:** `implementation/Dockerfile`
- **Port:** `5007`
- **Network:** `ddn-network`

### Environment Variables
```bash
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ddn_ai_analysis
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
JIRA_URL=${JIRA_URL}
JIRA_EMAIL=${JIRA_EMAIL}
JIRA_API_TOKEN=${JIRA_API_TOKEN}
JIRA_PROJECT_KEY=${JIRA_PROJECT_KEY}
```

### Dependencies
- `postgres` (DDN)

### Command
```bash
python jira_integration_service.py
```

### Purpose
Create Jira tickets for test failures

### API URL
http://localhost:5007

### Status
Optional (configure if using Jira)

---

## 1️⃣5️⃣ **Slack Service** (Slack Integration)

### Configuration
- **Container Name:** `ddn-slack`
- **Build:** `implementation/Dockerfile`
- **Port:** `5008` (changed from 5007)
- **Network:** `ddn-network`

### Environment Variables
```bash
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ddn_ai_analysis
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
SLACK_SIGNING_SECRET=${SLACK_SIGNING_SECRET}
SLACK_DEFAULT_CHANNEL=${SLACK_DEFAULT_CHANNEL}
DASHBOARD_URL=http://localhost:3000
```

### Dependencies
- `postgres` (DDN)

### Command
```bash
python slack_integration_service.py
```

### Purpose
Send Slack notifications for test failures

### API URL
http://localhost:5008

### Status
Optional (configure if using Slack)

---

## 1️⃣6️⃣ **Self-Healing Service** (Auto-Remediation)

### Configuration
- **Container Name:** `ddn-self-healing`
- **Build:** `implementation/Dockerfile`
- **Port:** `5009` (changed from 5008)
- **Network:** `ddn-network`

### Environment Variables
```bash
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ddn_ai_analysis
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
JENKINS_URL=${JENKINS_URL}
JENKINS_USER=${JENKINS_USER}
JENKINS_TOKEN=${JENKINS_TOKEN}
GITHUB_TOKEN=${GITHUB_TOKEN}
GITHUB_REPO=${GITHUB_REPO}
SELF_HEALING_SAFE_MODE=true
MIN_SUCCESS_RATE=0.8
MIN_PATTERN_OCCURRENCES=3
```

### Dependencies
- `postgres` (DDN)

### Command
```bash
python self_healing_service.py
```

### Purpose
Automatically apply fixes to recurring test failures

### Features
- Pattern recognition
- Safe mode validation
- Success rate tracking
- GitHub PR creation

### API URL
http://localhost:5009

---

## 1️⃣7️⃣ **Dashboard UI** (React Frontend)

### Configuration
- **Container Name:** `ddn-dashboard-ui`
- **Build:** `implementation/dashboard-ui/Dockerfile`
- **Port:** `3000`
- **Network:** `ddn-network`

### Environment Variables
```bash
VITE_API_URL=http://localhost:5006
```

### Dependencies
- `dashboard-api`

### Purpose
React-based web dashboard for monitoring and interaction

### Features
- Test failure visualization
- Real-time analytics
- Knowledge management interface
- Human-in-the-loop feedback
- Code fix approval workflow

### Tech Stack
- React 18
- Vite
- Material-UI
- React Router
- Recharts (analytics)

### Web UI
http://localhost:3000

---

## 🌐 Network Architecture

### Docker Network: `ddn-network`
- **Driver:** bridge
- **Purpose:** All services communicate via this network
- **Service Discovery:** Services reference each other by container name

### Internal Communication
```
dashboard-ui → dashboard-api → postgres/mongodb
                             → manual-trigger-api → n8n
langgraph-service → mongodb, redis, pinecone
celery-worker → redis, mongodb
flower → redis
langfuse-server → langfuse-db
```

---

## 💾 Persistent Volumes

| Volume | Purpose | Size (Approx) |
|--------|---------|---------------|
| `mongodb_data` | MongoDB database files | Variable |
| `postgres_data` | PostgreSQL (DDN) data | Variable |
| `langfuse_db_data` | PostgreSQL (Langfuse) data | Variable |
| `redis_data` | Redis persistence | Small |
| `n8n_data` | n8n workflows and config | Small |

**Total Storage:** Depends on usage, plan for 10-50 GB

---

## 🚀 Quick Start Commands

### Start All Services
```bash
docker-compose -f docker-compose-unified.yml up -d
```

### Stop All Services
```bash
docker-compose -f docker-compose-unified.yml down
```

### View Logs
```bash
# All services
docker-compose -f docker-compose-unified.yml logs -f

# Specific service
docker-compose -f docker-compose-unified.yml logs -f langgraph-service
```

### Check Status
```bash
docker-compose -f docker-compose-unified.yml ps
```

### Restart Service
```bash
docker-compose -f docker-compose-unified.yml restart dashboard-api
```

### Rebuild After Code Changes
```bash
docker-compose -f docker-compose-unified.yml build dashboard-api
docker-compose -f docker-compose-unified.yml up -d dashboard-api
```

---

## 🔐 Required Environment Variables

Create `.env` file in project root with:

```bash
# API Keys (Required)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
PINECONE_API_KEY=...

# GitHub (Required for CODE_ERROR analysis)
GITHUB_TOKEN=ghp_...
GITHUB_REPO=owner/repo-name

# Langfuse (Auto-configured)
LANGFUSE_PUBLIC_KEY=pk-lf-99176382-54aa-40dc-8900-768db9fd0278
LANGFUSE_SECRET_KEY=sk-lf-158d4ee5-d9b7-47d9-87ab-217c4edb74e6

# Jira (Optional)
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@domain.com
JIRA_API_TOKEN=...
JIRA_PROJECT_KEY=PROJ

# Slack (Optional)
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
SLACK_DEFAULT_CHANNEL=#test-failures

# Jenkins (Optional - for self-healing)
JENKINS_URL=http://jenkins-server
JENKINS_USER=admin
JENKINS_TOKEN=...
```

---

## 📊 Port Reference

| Port | Service | URL |
|------|---------|-----|
| 3000 | Dashboard UI | http://localhost:3000 |
| 3001 | Langfuse | http://localhost:3001 |
| 5001 | MCP MongoDB | http://localhost:5001 |
| 5002 | MCP GitHub | http://localhost:5002 |
| 5003 | LangGraph | http://localhost:5003 |
| 5004 | Manual Trigger API | http://localhost:5004 |
| 5006 | Dashboard API | http://localhost:5006 |
| 5007 | Jira Service | http://localhost:5007 |
| 5008 | Slack Service | http://localhost:5008 |
| 5009 | Self-Healing | http://localhost:5009 |
| 5555 | Flower | http://localhost:5555 |
| 5678 | n8n | http://localhost:5678 |
| 5432 | PostgreSQL (DDN) | localhost:5432 |
| 5433 | PostgreSQL (Langfuse) | localhost:5433 |
| 6379 | Redis | localhost:6379 |
| 27017 | MongoDB | set via `MONGODB_URI` (use MongoDB Atlas for production) |

---

## ✅ Health Check Endpoints

| Service | Endpoint | Expected Response |
|---------|----------|-------------------|
| LangGraph | http://localhost:5003/health | `{"status":"ok"}` |
| Dashboard API | http://localhost:5006/health | `{"status":"ok"}` |
| Langfuse | http://localhost:3001/api/public/health | `{"status":"OK"}` |
| Manual Trigger | http://localhost:5004/health | `{"status":"ok"}` |

---

**End of Services Reference**
