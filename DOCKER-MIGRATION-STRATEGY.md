# Docker Migration Strategy
**Created:** 2025-11-05
**Status:** 🔴 CRITICAL - Current architecture is fragmented

---

## 🚨 Current Problem

You discovered that Docker was introduced **last minute** for Redis and Langfuse, but the project **already has a complete Docker architecture** defined in `docker-compose.yml` with **15 services**!

### Current State (FRAGMENTED):
- ✅ Redis running standalone: `docker run -d redis`
- ✅ Langfuse running separately: `docker-compose-langfuse.yml`
- ❌ All other 13 services running manually with Python scripts
- ⚠️ **PORT CONFLICTS** between services

### Intended State (UNIFIED):
- ✅ **ALL 17 services** in one `docker-compose-unified.yml`
- ✅ Proper service dependencies
- ✅ Unified networking
- ✅ Single command startup

---

## 📊 Complete Service Inventory

### **Database Layer** (3 services)
| Service | Port | Image | Purpose | Status |
|---------|------|-------|---------|--------|
| mongodb | 27017 | mongo:7.0 | Unstructured data | ❌ Manual |
| postgres | 5432 | postgres:16 | DDN AI data | ❌ Manual |
| langfuse-db | 5433 | postgres:15 | Langfuse data | ✅ Docker (separate) |

### **Caching & Messaging** (1 service)
| Service | Port | Image | Purpose | Status |
|---------|------|-------|---------|--------|
| redis | 6379 | redis:latest | Cache/broker | ✅ Docker (standalone) |

### **Monitoring & Observability** (2 services)
| Service | Port | Image | Purpose | Status |
|---------|------|-------|---------|--------|
| langfuse-server | 3001* | langfuse:2 | LLM traces | ✅ Docker (separate) |
| flower | 5555 | (built) | Celery monitor | ❌ Manual |

### **Workflow & Task Processing** (2 services)
| Service | Port | Image | Purpose | Status |
|---------|------|-------|---------|--------|
| n8n | 5678 | n8nio/n8n | Workflows | ❌ Manual |
| celery-worker | - | (built) | Async tasks | ❌ Manual |

### **Core AI Services** (1 service)
| Service | Port | Image | Purpose | Status |
|---------|------|-------|---------|--------|
| langgraph-service | 5003* | (built) | Classification | ❌ Manual |

### **MCP Servers** (2 services)
| Service | Port | Image | Purpose | Status |
|---------|------|-------|---------|--------|
| mcp-mongodb | 5001 | (built) | MongoDB MCP | ❌ Manual |
| mcp-github | 5002 | (built) | GitHub MCP | ❌ Manual |

### **API Services** (2 services)
| Service | Port | Image | Purpose | Status |
|---------|------|-------|---------|--------|
| manual-trigger-api | 5004 | (built) | Manual triggers | ❌ Manual |
| dashboard-api | 5006* | (built) | Backend API | ❌ Manual |

### **Integration Services** (3 services)
| Service | Port | Image | Purpose | Status |
|---------|------|-------|---------|--------|
| jira-service | 5007 | (built) | Jira integration | ❌ Manual |
| slack-service | 5008* | (built) | Slack integration | ❌ Manual |
| self-healing-service | 5009* | (built) | Auto-healing | ❌ Manual |

### **Frontend** (1 service)
| Service | Port | Image | Purpose | Status |
|---------|------|-------|---------|--------|
| dashboard-ui | 3000 | (built) | React UI | ❌ Manual |

**Total:** 17 services (3 in Docker, 14 manual)

\* = Port changed in unified config to avoid conflicts

---

## 🔴 Port Conflicts Found

### In Original docker-compose.yml:
| Conflict | Service 1 | Service 2 | Resolution |
|----------|-----------|-----------|------------|
| Port 3000 | dashboard-ui | langfuse-server | Move Langfuse → 3001 |
| Port 5000 | langgraph-service | (external?) | Move langgraph → 5003 |
| Port 5005 | dashboard-api | (external?) | Move to 5006 |
| Port 5007 | jira-service | slack-service | Keep Jira 5007, Slack → 5008 |
| Port 5008 | slack-service | self-healing | Slack → 5008, Self-healing → 5009 |

---

## 🎯 Migration Options

### Option 1: Big Bang Migration (RECOMMENDED)
**Approach:** Stop all services, migrate to unified Docker Compose, start everything together

**Pros:**
- ✅ Clean architecture
- ✅ All services properly networked
- ✅ Consistent environment
- ✅ Easy to start/stop all services

**Cons:**
- ⚠️ Requires downtime
- ⚠️ All Dockerfiles must work
- ⚠️ Need to test all services

**Steps:**
1. Stop all running services (manual Python + existing Docker)
2. Build all Docker images: `docker-compose -f docker-compose-unified.yml build`
3. Start all services: `docker-compose -f docker-compose-unified.yml up -d`
4. Verify each service health check
5. Test end-to-end workflows

**Estimated Time:** 2-3 hours

### Option 2: Gradual Migration
**Approach:** Migrate services in phases (databases → core → integrations)

**Pros:**
- ✅ Lower risk
- ✅ Can rollback individual services
- ✅ Test incrementally

**Cons:**
- ⚠️ Takes longer
- ⚠️ More complex networking (Docker ↔ manual)
- ⚠️ Temporary inconsistency

**Phases:**
1. **Phase A:** Databases (MongoDB, PostgreSQL)
2. **Phase B:** Core services (LangGraph, MCP servers)
3. **Phase C:** APIs (Manual trigger, Dashboard API)
4. **Phase D:** Integrations (Jira, Slack, Self-healing)
5. **Phase E:** Frontend (Dashboard UI)

**Estimated Time:** 5-6 hours

### Option 3: Hybrid (Keep Current + New)
**Approach:** Run critical services in Docker, keep others manual

**Pros:**
- ✅ Fastest
- ✅ Minimal changes
- ✅ Low risk

**Cons:**
- ⚠️ Inconsistent architecture
- ⚠️ Hard to maintain
- ⚠️ Network complexity
- ⚠️ Not scalable

**Not Recommended**

---

## 🚀 Recommended Migration Plan

### Pre-Migration Checklist

- [ ] Verify all Dockerfiles exist and are valid
  - [ ] `implementation/Dockerfile`
  - [ ] `implementation/dashboard-ui/Dockerfile`
  - [ ] `mcp-configs/Dockerfile`

- [ ] Create `.env` file with all required variables
  - [ ] API keys (Anthropic, OpenAI, Gemini, Pinecone)
  - [ ] GitHub token and repo
  - [ ] Langfuse keys
  - [ ] Jira credentials (if using)
  - [ ] Slack tokens (if using)

- [ ] Backup current data
  - [ ] MongoDB data export
  - [ ] PostgreSQL data export
  - [ ] Redis data (if any)

- [ ] Update documentation
  - [ ] README with new startup commands
  - [ ] Architecture diagram
  - [ ] Port mapping reference

### Migration Steps (Big Bang)

#### Step 1: Stop All Current Services (15 min)
```bash
# Stop manual Python processes (find and kill)
# Stop standalone Redis
docker stop redis-ddn

# Stop Langfuse
docker-compose -f docker-compose-langfuse.yml down

# Stop any other Docker containers
docker ps  # Check what's running
```

#### Step 2: Prepare Environment (10 min)
```bash
# Copy .env.MASTER to root as .env
copy .env.MASTER .env

# Edit .env and fill in all API keys
# Ensure all required keys are set

# Verify Dockerfiles exist
dir implementation\Dockerfile
dir implementation\dashboard-ui\Dockerfile
dir mcp-configs\Dockerfile
```

#### Step 3: Build All Images (30-45 min)
```bash
# Build all services
docker-compose -f docker-compose-unified.yml build

# Expected output: 10+ images built
# This will take time on first run
```

#### Step 4: Start Infrastructure Services (10 min)
```bash
# Start databases first
docker-compose -f docker-compose-unified.yml up -d mongodb postgres langfuse-db redis

# Wait for health checks
docker-compose -f docker-compose-unified.yml ps

# Verify all healthy
```

#### Step 5: Start Monitoring Services (5 min)
```bash
# Start Langfuse and Flower
docker-compose -f docker-compose-unified.yml up -d langfuse-server flower

# Verify accessible
# Langfuse: http://localhost:3001
# Flower: http://localhost:5555
```

#### Step 6: Start Core Services (10 min)
```bash
# Start n8n, Celery, LangGraph, MCP servers
docker-compose -f docker-compose-unified.yml up -d n8n celery-worker langgraph-service mcp-mongodb mcp-github

# Check logs for errors
docker-compose -f docker-compose-unified.yml logs --tail=50 langgraph-service
```

#### Step 7: Start API Services (10 min)
```bash
# Start API services
docker-compose -f docker-compose-unified.yml up -d manual-trigger-api dashboard-api

# Verify endpoints
curl http://localhost:5004/health
curl http://localhost:5006/health
```

#### Step 8: Start Integration Services (10 min)
```bash
# Start integrations (optional if configured)
docker-compose -f docker-compose-unified.yml up -d jira-service slack-service self-healing-service

# Skip if not using Jira/Slack
```

#### Step 9: Start Frontend (5 min)
```bash
# Start dashboard UI
docker-compose -f docker-compose-unified.yml up -d dashboard-ui

# Verify accessible
# Dashboard: http://localhost:3000
```

#### Step 10: End-to-End Testing (30 min)
- [ ] Dashboard UI loads
- [ ] Can trigger manual analysis
- [ ] LangGraph classification works
- [ ] MongoDB data visible
- [ ] PostgreSQL queries work
- [ ] Flower shows Celery worker
- [ ] Langfuse shows traces
- [ ] n8n workflows accessible

---

## 📝 Updated Port Mapping

| Service | Old Port | New Port | URL |
|---------|----------|----------|-----|
| Dashboard UI | 3000 | 3000 | http://localhost:3000 |
| Langfuse | 3000 | **3001** | http://localhost:3001 |
| LangGraph | 5000 | **5003** | http://localhost:5003 |
| MCP MongoDB | 5001 | 5001 | http://localhost:5001 |
| MCP GitHub | 5002 | 5002 | http://localhost:5002 |
| Manual Trigger | 5004 | 5004 | http://localhost:5004 |
| Dashboard API | 5005 | **5006** | http://localhost:5006 |
| Flower | 5555 | 5555 | http://localhost:5555 |
| n8n | 5678 | 5678 | http://localhost:5678 |
| Jira Service | 5006 | **5007** | http://localhost:5007 |
| Slack Service | 5007 | **5008** | http://localhost:5008 |
| Self-Healing | 5008 | **5009** | http://localhost:5009 |
| MongoDB | 27017 | 27017 | localhost:27017 |
| PostgreSQL | 5432 | 5432 | localhost:5432 |
| Langfuse DB | 5432 | **5433** | localhost:5433 |
| Redis | 6379 | 6379 | localhost:6379 |

**Changes highlighted in bold**

---

## 🔧 Required Configuration Updates

### Update .env Files
After migration, update the following in `.env.MASTER` and sync to `.env`:

```bash
# Update Langfuse host (port changed to 3001)
LANGFUSE_HOST=http://localhost:3001

# Update Dashboard API URL (port changed to 5006)
VITE_API_URL=http://localhost:5006

# Add Docker network references
MONGODB_URI=mongodb://admin:password@mongodb:27017/
POSTGRES_HOST=postgres  # Docker service name, not localhost
REDIS_URL=redis://redis:6379/0  # Docker service name
```

### Update Dashboard UI Configuration
File: `implementation/dashboard-ui/.env`
```bash
VITE_API_URL=http://localhost:5006  # Updated port
```

### Update Service Code (if hardcoded)
Check these files for hardcoded `localhost` or port references:
- `implementation/langgraph_agent.py` - Database connections
- `implementation/dashboard_api_full.py` - Service URLs
- `implementation/manual_trigger_api.py` - n8n webhook URL

---

## 🎯 Quick Start Commands (After Migration)

### Start Everything
```bash
docker-compose -f docker-compose-unified.yml up -d
```

### Stop Everything
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

### Restart Specific Service
```bash
docker-compose -f docker-compose-unified.yml restart dashboard-api
```

### Rebuild After Code Changes
```bash
docker-compose -f docker-compose-unified.yml build dashboard-api
docker-compose -f docker-compose-unified.yml up -d dashboard-api
```

---

## 📊 Benefits of Unified Docker Architecture

### Development
- ✅ **One-command startup:** `docker-compose up -d`
- ✅ **Consistent environments:** No "works on my machine"
- ✅ **Easy onboarding:** New developers get full stack in 10 minutes
- ✅ **Version control:** Infrastructure as code

### Operations
- ✅ **Easy deployment:** Same compose file for staging/prod
- ✅ **Service isolation:** Each service in own container
- ✅ **Automatic restarts:** Resilient to crashes
- ✅ **Health monitoring:** Built-in health checks

### Maintenance
- ✅ **Clear dependencies:** Service relationships explicit
- ✅ **Unified networking:** Services communicate via names
- ✅ **Easy scaling:** Add replicas with one command
- ✅ **Simple updates:** Rebuild and restart services independently

---

## 🚨 Risks & Mitigation

### Risk 1: Dockerfiles Don't Work
**Mitigation:** Test build before migration
```bash
docker build -t test-impl -f implementation/Dockerfile implementation
docker build -t test-ui -f implementation/dashboard-ui/Dockerfile implementation/dashboard-ui
docker build -t test-mcp -f mcp-configs/Dockerfile mcp-configs
```

### Risk 2: Port Conflicts
**Mitigation:** Check ports before starting
```bash
netstat -ano | findstr "3000 3001 5001 5002 5003 5004 5006 5007 5008 5009 5555 5678"
```

### Risk 3: Data Loss
**Mitigation:** Backup before migration
```bash
# MongoDB backup
docker exec ddn-mongodb mongodump --out=/backup

# PostgreSQL backup
docker exec ddn-postgres pg_dump -U postgres ddn_ai_analysis > backup.sql
```

### Risk 4: Missing Environment Variables
**Mitigation:** Validate .env file
```bash
# Required variables
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=
PINECONE_API_KEY=
GITHUB_TOKEN=
GITHUB_REPO=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
```

---

## 📋 Decision Required

**QUESTION FOR YOU:**

Which migration approach do you prefer?

1. **Option 1: Big Bang** (Recommended)
   - Migrate everything at once
   - Clean architecture
   - Estimated time: 2-3 hours

2. **Option 2: Gradual**
   - Migrate in phases
   - Lower risk
   - Estimated time: 5-6 hours

3. **Option 3: Keep Current**
   - Don't migrate
   - Maintain hybrid
   - Not recommended

**My Recommendation:** **Option 1 (Big Bang)** because:
- You already have Redis and Langfuse in Docker
- The architecture is designed for Docker
- Cleaner and more maintainable
- Easier to troubleshoot
- Better for future scaling

**Next Steps After Decision:**
1. I'll guide you through the migration
2. We'll test each service as we go
3. We'll update all documentation
4. We'll create startup/shutdown scripts

---

**What would you like to do?**
