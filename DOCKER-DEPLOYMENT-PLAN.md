# Docker Deployment Plan - DDN AI Analysis System
**Date:** 2025-11-05
**Version:** 1.0
**Purpose:** Comprehensive deployment strategy for 17 Dockerized services

---

## Table of Contents
1. [Overview](#overview)
2. [Service Architecture](#service-architecture)
3. [Deployment Order](#deployment-order)
4. [Health Checks](#health-checks)
5. [Quick Start Commands](#quick-start-commands)
6. [Verification Procedures](#verification-procedures)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Rollback Procedures](#rollback-procedures)

---

## Overview

### System Architecture
- **Total Services:** 17 containers
- **Deployment Layers:** 7 layers (sequential startup)
- **External Dependencies:** Native PostgreSQL on port 5432
- **Container Orchestration:** Docker Compose
- **Configuration File:** `docker-compose-unified.yml`

### Key Infrastructure Details
- **Docker PostgreSQL Port:** 5434 (external) / 5432 (internal)
- **Native PostgreSQL Port:** 5432 (kept for other applications)
- **MongoDB:** Docker container on port 27018
- **Redis:** Docker container on port 6380
- **Network Mode:** Bridge networking with service discovery

---

## Service Architecture

### Layer 1: Infrastructure (2 services)
**Purpose:** Core data storage
**Dependencies:** None (start first)

| Service | Container | Port(s) | Priority |
|---------|-----------|---------|----------|
| PostgreSQL | `postgres` | 5434:5432 | CRITICAL |
| MongoDB | `mongodb` | 27018:27017 | CRITICAL |

**Notes:**
- PostgreSQL uses external port 5434 to avoid conflict with native PostgreSQL
- MongoDB stores test results and failure data
- Both must be healthy before proceeding to Layer 2

---

### Layer 2: Caching & Monitoring (3 services)
**Purpose:** Performance optimization and observability
**Dependencies:** Layer 1 (PostgreSQL, MongoDB)

| Service | Container | Port(s) | Priority |
|---------|-----------|---------|----------|
| Redis | `redis` | 6380:6379 | HIGH |
| Langfuse | `langfuse` | 3001:3000 | MEDIUM |
| Flower | `flower` | 5555:5555 | LOW |

**Notes:**
- Redis used for Phase 1 caching (RAG queries, embeddings)
- Langfuse provides LLM observability (traces, metrics)
- Flower monitors Celery task queues

---

### Layer 3: Workflow Engine (1 service)
**Purpose:** Async task processing
**Dependencies:** Redis, MongoDB

| Service | Container | Port(s) | Priority |
|---------|-----------|---------|----------|
| Celery Worker | `celery-worker` | None | HIGH |

**Notes:**
- Processes async tasks (AI analysis, fix generation)
- Connects to Redis for task queue
- Connects to MongoDB for results storage
- Requires Redis to be fully healthy

---

### Layer 4: AI Core Services (3 services)
**Purpose:** RAG, classification, and error analysis
**Dependencies:** PostgreSQL, MongoDB, Redis, Pinecone

| Service | Container | Port(s) | Priority |
|---------|-----------|---------|----------|
| LangGraph Agent | `langgraph-service` | 5000:5000 | CRITICAL |
| LangGraph Classification | `langgraph-classification` | 5004:5004 | HIGH |
| AI Analysis Service | `ai-analysis-service` | 5005:5005 | HIGH |

**Notes:**
- LangGraph Agent: Main orchestrator for AI workflows
- Classification Service: Query routing (RAG vs Knowledge Base)
- AI Analysis: Root cause analysis and fix suggestions
- All require Pinecone API keys and OpenAI/Gemini keys

---

### Layer 5: Integration Services (5 services)
**Purpose:** External system integrations
**Dependencies:** MongoDB, PostgreSQL

| Service | Container | Port(s) | Priority |
|---------|-----------|---------|----------|
| JIRA Service | `jira-service` | 5009:5009 | MEDIUM |
| Slack Service | `slack-service` | 5010:5010 | MEDIUM |
| MCP MongoDB | `mcp-mongodb` | 5001:5001 | MEDIUM |
| MCP GitHub | `mcp-github` | 5002:5002 | LOW |
| Self-Healing | `self-healing-service` | 5011:5011 | LOW |

**Notes:**
- JIRA/Slack: Optional (require external API keys)
- MCP servers: Model Context Protocol integrations
- Self-Healing: Automated fix deployment (Phase 9)

---

### Layer 6: API Gateway (2 services)
**Purpose:** External API access
**Dependencies:** All backend services

| Service | Container | Port(s) | Priority |
|---------|-----------|---------|----------|
| Dashboard API | `dashboard-api` | 5006:5006 | CRITICAL |
| Manual Trigger API | `manual-trigger-api` | 5008:5008 | HIGH |

**Notes:**
- Dashboard API: Main REST API for UI
- Manual Trigger API: On-demand analysis endpoint
- Both connect to PostgreSQL on `postgres:5432` (internal)

---

### Layer 7: Frontend (1 service)
**Purpose:** User interface
**Dependencies:** Dashboard API (5006)

| Service | Container | Port(s) | Priority |
|---------|-----------|---------|----------|
| Dashboard UI | `dashboard-ui` | 3000:3000 | HIGH |

**Notes:**
- React application
- Proxies API calls to Dashboard API
- Accessible at http://localhost:3000

---

## Deployment Order

### Phase 1: Start Infrastructure Layer (2 min)
```bash
# Start PostgreSQL and MongoDB
docker-compose -f docker-compose-unified.yml up -d postgres mongodb

# Wait for containers to be healthy
timeout /t 30

# Verify layer 1
docker-compose -f docker-compose-unified.yml ps postgres mongodb
```

**Expected Result:** Both containers show "healthy" status

---

### Phase 2: Start Caching & Monitoring Layer (3 min)
```bash
# Start Redis, Langfuse, Flower
docker-compose -f docker-compose-unified.yml up -d redis langfuse flower

# Wait for Redis to be ready
timeout /t 20

# Verify layer 2
docker-compose -f docker-compose-unified.yml ps redis langfuse flower
```

**Expected Result:** Redis healthy, Langfuse UI accessible at http://localhost:3001

---

### Phase 3: Start Workflow Engine (2 min)
```bash
# Start Celery worker
docker-compose -f docker-compose-unified.yml up -d celery-worker

# Verify worker is running
docker logs celery-worker --tail 20
```

**Expected Result:** Celery worker shows "ready" status, connected to Redis

---

### Phase 4: Start AI Core Services (5 min)
```bash
# Start LangGraph services and AI Analysis
docker-compose -f docker-compose-unified.yml up -d ^
  langgraph-service ^
  langgraph-classification ^
  ai-analysis-service

# Wait for services to initialize
timeout /t 30

# Verify layer 4
docker-compose -f docker-compose-unified.yml ps langgraph-service
```

**Expected Result:** All 3 services running, logs show "Application startup complete"

---

### Phase 5: Start Integration Services (3 min)
```bash
# Start integration services
docker-compose -f docker-compose-unified.yml up -d ^
  jira-service ^
  slack-service ^
  mcp-mongodb ^
  mcp-github ^
  self-healing-service

# Verify layer 5
docker-compose -f docker-compose-unified.yml ps
```

**Expected Result:** All integration services running (JIRA/Slack may show warnings if not configured)

---

### Phase 6: Start API Gateway (2 min)
```bash
# Start API services
docker-compose -f docker-compose-unified.yml up -d ^
  dashboard-api ^
  manual-trigger-api

# Wait for APIs to be ready
timeout /t 15

# Verify API health
curl http://localhost:5006/health
curl http://localhost:5008/health
```

**Expected Result:** Both APIs return `{"status": "healthy"}`

---

### Phase 7: Start Frontend (2 min)
```bash
# Start Dashboard UI
docker-compose -f docker-compose-unified.yml up -d dashboard-ui

# Wait for UI build
timeout /t 30

# Open browser
start http://localhost:3000
```

**Expected Result:** Dashboard UI loads successfully

---

## Health Checks

### Container Status Check
```bash
# View all container statuses
docker-compose -f docker-compose-unified.yml ps

# View logs for specific service
docker logs <container-name> --tail 50

# Follow logs in real-time
docker logs <container-name> -f
```

### Individual Service Health Checks

#### PostgreSQL (Port 5434)
```bash
# Connection test
psql -h localhost -p 5434 -U postgres -d ddn_ai_analysis -c "SELECT 1;"

# Expected: Returns "1"
```

#### MongoDB (Port 27018)
```bash
# Connection test
mongosh --host localhost --port 27018 --eval "db.adminCommand('ping')"

# Expected: Returns { ok: 1 }
```

#### Redis (Port 6380)
```bash
# Connection test
redis-cli -h localhost -p 6380 PING

# Expected: Returns "PONG"
```

#### Dashboard API (Port 5006)
```bash
# Health check
curl http://localhost:5006/health

# Expected: {"status": "healthy", "database": "connected", "redis": "connected"}
```

#### Manual Trigger API (Port 5008)
```bash
# Health check
curl http://localhost:5008/health

# Expected: {"status": "ok"}
```

#### Langfuse UI (Port 3001)
```bash
# Open in browser
start http://localhost:3001

# Expected: Langfuse login page
```

#### Flower UI (Port 5555)
```bash
# Open in browser
start http://localhost:5555

# Expected: Flower dashboard showing Celery workers
```

#### Dashboard UI (Port 3000)
```bash
# Open in browser
start http://localhost:3000

# Expected: DDN AI Dashboard homepage
```

---

## Quick Start Commands

### All-in-One Deployment
```bash
# Start all services at once
cd c:\DDN-AI-Project-Documentation
docker-compose -f docker-compose-unified.yml up -d

# Monitor startup progress
docker-compose -f docker-compose-unified.yml logs -f

# Verify all containers running
docker-compose -f docker-compose-unified.yml ps
```

**Estimated Time:** 5-10 minutes for full startup

---

### Stop All Services
```bash
# Graceful shutdown
docker-compose -f docker-compose-unified.yml down

# Stop and remove volumes (WARNING: deletes data)
docker-compose -f docker-compose-unified.yml down -v
```

---

### Restart Individual Service
```bash
# Restart a specific service
docker-compose -f docker-compose-unified.yml restart <service-name>

# Example: Restart Dashboard API
docker-compose -f docker-compose-unified.yml restart dashboard-api
```

---

### View Service Logs
```bash
# All services
docker-compose -f docker-compose-unified.yml logs

# Specific service
docker-compose -f docker-compose-unified.yml logs dashboard-api

# Follow logs (Ctrl+C to exit)
docker-compose -f docker-compose-unified.yml logs -f dashboard-api

# Last 50 lines
docker-compose -f docker-compose-unified.yml logs --tail=50 dashboard-api
```

---

### Check Resource Usage
```bash
# View CPU/Memory usage
docker stats

# View disk usage
docker system df

# View container details
docker inspect <container-name>
```

---

## Verification Procedures

### End-to-End Verification Script

Create `verify-deployment.bat`:
```batch
@echo off
echo ====================================
echo DDN AI System - Deployment Verification
echo ====================================
echo.

echo [1/8] Checking container status...
docker-compose -f docker-compose-unified.yml ps
echo.

echo [2/8] Testing PostgreSQL (port 5434)...
psql -h localhost -p 5434 -U postgres -d ddn_ai_analysis -c "SELECT 1;" 2>nul
if %errorlevel%==0 (echo [PASS] PostgreSQL) else (echo [FAIL] PostgreSQL)
echo.

echo [3/8] Testing Redis (port 6380)...
redis-cli -h localhost -p 6380 PING 2>nul
if %errorlevel%==0 (echo [PASS] Redis) else (echo [FAIL] Redis)
echo.

echo [4/8] Testing Dashboard API (port 5006)...
curl -s http://localhost:5006/health >nul 2>&1
if %errorlevel%==0 (echo [PASS] Dashboard API) else (echo [FAIL] Dashboard API)
echo.

echo [5/8] Testing Manual Trigger API (port 5008)...
curl -s http://localhost:5008/health >nul 2>&1
if %errorlevel%==0 (echo [PASS] Manual Trigger API) else (echo [FAIL] Manual Trigger API)
echo.

echo [6/8] Testing Dashboard UI (port 3000)...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel%==0 (echo [PASS] Dashboard UI) else (echo [FAIL] Dashboard UI)
echo.

echo [7/8] Testing Langfuse (port 3001)...
curl -s http://localhost:3001 >nul 2>&1
if %errorlevel%==0 (echo [PASS] Langfuse) else (echo [FAIL] Langfuse)
echo.

echo [8/8] Testing Flower (port 5555)...
curl -s http://localhost:5555 >nul 2>&1
if %errorlevel%==0 (echo [PASS] Flower) else (echo [FAIL] Flower)
echo.

echo ====================================
echo Verification Complete
echo ====================================
pause
```

**Usage:**
```bash
verify-deployment.bat
```

---

### Manual Verification Checklist

- [ ] **PostgreSQL (5434):** Can connect via psql
- [ ] **MongoDB (27018):** Can connect via mongosh
- [ ] **Redis (6380):** Responds to PING
- [ ] **Langfuse (3001):** Web UI accessible
- [ ] **Flower (5555):** Celery dashboard accessible
- [ ] **LangGraph Service (5000):** Health endpoint returns 200
- [ ] **Dashboard API (5006):** Health endpoint returns healthy status
- [ ] **Manual Trigger API (5008):** Health endpoint returns OK
- [ ] **Dashboard UI (3000):** Homepage loads successfully
- [ ] **Database Connectivity:** Dashboard can query PostgreSQL
- [ ] **Redis Caching:** Dashboard shows cached queries
- [ ] **Celery Tasks:** Flower shows active workers

---

## Troubleshooting Guide

### Issue 1: Container Won't Start

**Symptoms:**
- Container shows "Exited" status
- Container restarts continuously

**Diagnosis:**
```bash
# Check logs
docker logs <container-name> --tail 50

# Check exit code
docker inspect <container-name> | findstr ExitCode
```

**Common Causes:**
1. **Missing environment variables:** Check `.env` file
2. **Port conflict:** Another service using the port
3. **Dependency not ready:** Start dependencies first
4. **Configuration error:** Review docker-compose-unified.yml

**Solutions:**
```bash
# Restart with dependency check
docker-compose -f docker-compose-unified.yml up -d --force-recreate <service-name>

# Check environment variables
docker exec <container-name> env | findstr <VAR_NAME>

# Check port availability
netstat -ano | findstr :<PORT>
```

---

### Issue 2: "Connection Refused" Errors

**Symptoms:**
- Service can't connect to PostgreSQL/MongoDB/Redis
- API returns 500 errors

**Diagnosis:**
```bash
# Check if target service is running
docker-compose -f docker-compose-unified.yml ps <target-service>

# Test connection from container
docker exec <source-container> ping <target-service>

# Check network
docker network ls
docker network inspect docker-compose-default
```

**Common Causes:**
1. **Service not started:** Start dependency first
2. **Wrong hostname:** Use service name (e.g., `postgres:5432`)
3. **Network issue:** Recreate Docker network
4. **Firewall:** Windows Firewall blocking Docker

**Solutions:**
```bash
# Restart dependencies
docker-compose -f docker-compose-unified.yml restart postgres redis

# Recreate network
docker-compose -f docker-compose-unified.yml down
docker-compose -f docker-compose-unified.yml up -d

# Check connection string in .env
type .env | findstr DATABASE_URL
```

---

### Issue 3: PostgreSQL Port Conflict (5432)

**Symptoms:**
- Error: "port is already allocated"
- PostgreSQL container won't start

**Diagnosis:**
```bash
# Check what's using port 5432
netstat -ano | findstr :5432
```

**Solution:**
**ALREADY FIXED** - Docker PostgreSQL uses port 5434 (external)

If you see this error, verify:
```bash
# Check docker-compose-unified.yml
findstr "5434:5432" docker-compose-unified.yml

# Should show:
# ports:
#   - "5434:5432"
```

---

### Issue 4: "No module named X" Errors

**Symptoms:**
- Python import errors in logs
- Service crashes on startup

**Diagnosis:**
```bash
# Check logs
docker logs <container-name> --tail 100

# Check installed packages
docker exec <container-name> pip list
```

**Common Causes:**
1. **requirements.txt out of sync:** Rebuild image
2. **Cache issue:** Build with --no-cache
3. **Dependency conflict:** Check requirements.txt

**Solutions:**
```bash
# Rebuild specific service
docker-compose -f docker-compose-unified.yml build --no-cache <service-name>

# Restart service
docker-compose -f docker-compose-unified.yml up -d --force-recreate <service-name>

# Verify requirements.txt
docker exec <container-name> cat /app/requirements.txt
```

---

### Issue 5: Dashboard UI Shows "API Error"

**Symptoms:**
- UI loads but shows connection errors
- Network tab shows 404 or 500 errors

**Diagnosis:**
```bash
# Check Dashboard API
curl http://localhost:5006/health

# Check API logs
docker logs dashboard-api --tail 50

# Check if UI can reach API
docker exec dashboard-ui curl http://dashboard-api:5006/health
```

**Common Causes:**
1. **Dashboard API not running:** Start dashboard-api
2. **Wrong API URL:** Check vite.config.js proxy
3. **CORS issue:** Check flask-cors configuration

**Solutions:**
```bash
# Restart both UI and API
docker-compose -f docker-compose-unified.yml restart dashboard-ui dashboard-api

# Check proxy configuration
docker exec dashboard-ui cat /app/vite.config.js

# Test API directly
curl -v http://localhost:5006/api/test-results
```

---

### Issue 6: High Resource Usage

**Symptoms:**
- Docker using excessive CPU/RAM
- System slowdown

**Diagnosis:**
```bash
# Check resource usage
docker stats

# Check container processes
docker top <container-name>
```

**Solutions:**
```bash
# Restart high-usage containers
docker-compose -f docker-compose-unified.yml restart <service-name>

# Limit resources in docker-compose-unified.yml
# Add under service:
#   deploy:
#     resources:
#       limits:
#         cpus: '1.0'
#         memory: 1G

# Prune unused resources
docker system prune -a
```

---

### Issue 7: Langsmith Dependency Conflict

**Symptoms:**
- Build fails with "ResolutionImpossible"
- Error about langsmith vs langchain

**Diagnosis:**
```bash
# Check build logs
type docker-build-fixed.log | findstr langsmith
```

**Solution:**
**ALREADY FIXED** - langsmith is commented out in requirements.txt

Verify fix:
```bash
# Should show commented line
findstr "# langsmith" implementation\requirements.txt

# Output should be:
# # langsmith>=0.4.39  # DISABLED: Conflicts with langchain dependencies
```

---

## Rollback Procedures

### Rollback to Native (Non-Docker) Setup

If Docker deployment fails, revert to native services:

**Step 1: Stop All Docker Containers**
```bash
cd c:\DDN-AI-Project-Documentation
docker-compose -f docker-compose-unified.yml down
```

**Step 2: Restore Configuration Files**
```bash
# Restore .env.MASTER (if needed)
copy .env.MASTER.backup-2025-11-05 .env.MASTER

# Restore docker-compose files (if needed)
copy docker-compose-unified.yml.backup-2025-11-05 docker-compose-unified.yml
```

**Step 3: Start Native PostgreSQL**
```bash
# PostgreSQL should still be on port 5432
START-POSTGRESQL.bat
```

**Step 4: Verify Native Services**
```bash
# Test native PostgreSQL
psql -h localhost -p 5432 -U postgres -d ddn_ai_analysis -c "SELECT 1;"

# Expected: Returns "1"
```

**Step 5: Start Native Python Services**
```bash
# Start Dashboard API (native)
cd implementation
python dashboard_api_full.py

# In another terminal - start Celery
cd implementation
python -m celery -A tasks.celery_tasks worker
```

**Step 6: Start Native Dashboard UI**
```bash
cd implementation\dashboard-ui
npm run dev
```

**Result:** System back to fully native setup

---

### Partial Rollback (Keep Some Docker Services)

**Option A: Keep Only Infrastructure (PostgreSQL, MongoDB, Redis)**
```bash
# Stop all except infrastructure
docker-compose -f docker-compose-unified.yml stop ^
  dashboard-ui dashboard-api manual-trigger-api ^
  langgraph-service ai-analysis-service

# Run Python services natively
cd implementation
python dashboard_api_full.py
```

**Option B: Keep Monitoring Tools (Langfuse, Flower)**
```bash
# Keep only monitoring
docker-compose -f docker-compose-unified.yml up -d langfuse flower

# Run everything else natively
START-ALL-SERVICES.bat
```

---

## Performance Baseline

### Expected Resource Usage (17 containers running)

| Resource | Normal | High | Critical |
|----------|--------|------|----------|
| **CPU Usage** | 20-30% | 50-60% | >80% |
| **RAM Usage** | 4-6 GB | 8-10 GB | >12 GB |
| **Disk Usage** | 10-15 GB | 20-25 GB | >30 GB |
| **Network** | 100-500 KB/s | 1-5 MB/s | >10 MB/s |

### Startup Times

| Layer | Services | Expected Time | Max Time |
|-------|----------|---------------|----------|
| Layer 1 | Infrastructure | 30-60s | 2 min |
| Layer 2 | Caching/Monitoring | 20-40s | 1 min |
| Layer 3 | Workflow | 10-20s | 30s |
| Layer 4 | AI Core | 60-90s | 3 min |
| Layer 5 | Integrations | 30-60s | 2 min |
| Layer 6 | APIs | 15-30s | 1 min |
| Layer 7 | Frontend | 30-60s | 2 min |
| **Total** | **All 17** | **3-5 min** | **10 min** |

---

## Next Steps After Deployment

### 1. Configure Integrations
- [ ] Add JIRA API keys to `.env`
- [ ] Add Slack webhook URL to `.env`
- [ ] Add GitHub token to `.env`
- [ ] Test integration services

### 2. Run End-to-End Tests
- [ ] Trigger manual analysis via API
- [ ] Verify AI analysis generates fixes
- [ ] Check Celery tasks in Flower
- [ ] Verify LangGraph traces in Langfuse

### 3. Load Test Data
- [ ] Import error documentation to Pinecone
- [ ] Load sample test results to MongoDB
- [ ] Create test cases in Dashboard UI
- [ ] Verify RAG queries return relevant docs

### 4. Performance Tuning
- [ ] Benchmark query response times
- [ ] Monitor Redis cache hit rates
- [ ] Optimize Celery worker count
- [ ] Review LangGraph token usage

### 5. Production Preparation
- [ ] Set up automated backups (PostgreSQL, MongoDB)
- [ ] Configure log rotation
- [ ] Set up monitoring alerts
- [ ] Document recovery procedures
- [ ] Create admin runbook

---

## References

- [docker-compose-unified.yml](docker-compose-unified.yml) - Main orchestration file
- [ALL-SERVICES-REFERENCE.md](ALL-SERVICES-REFERENCE.md) - Service details
- [POSTGRES-PORT-CHANGE-COMPLETE.md](POSTGRES-PORT-CHANGE-COMPLETE.md) - Port change documentation
- [DEPENDENCY-MANAGEMENT-GUIDE.md](DEPENDENCY-MANAGEMENT-GUIDE.md) - Python dependencies
- [QUICK-START-GUIDE.md](QUICK-REFERENCE-GUIDE.md) - Quick reference

---

**End of Deployment Plan**
