# DDN AI Test Failure Analysis System - Architecture

## Executive Summary

The DDN AI system is an intelligent, cloud-native platform for analyzing test failures using advanced LLMs, retrieval-augmented generation (RAG), and workflow orchestration. It combines Claude 3.5 Sonnet, Gemini Flash, and OpenAI for multi-model resilience, with a dual-index RAG system for context-aware analysis.

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard (React/TypeScript)  │  GitHub UI  │  Jenkins UI      │
│         (Port 5173)            │  Webhooks   │  CLI             │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER (FastAPI)                      │
├─────────────────────────────────────────────────────────────────┤
│  • /failures              (POST, GET)                            │
│  • /analysis              (GET stream)                           │
│  • /workflows             (POST, GET)                           │
│  • /health                (GET)                                 │
│  • /metrics               (GET)                                 │
│  Port: 5000               Replicas: 1-N                         │
└──────────┬──────────────────────────────────────────────────────┘
           │
    ┌──────┴──────────────────────┐
    │                             │
    ▼                             ▼
┌──────────────────────┐   ┌─────────────────────┐
│   AGENT LAYER        │   │  ASYNC PROCESSING   │
├──────────────────────┤   ├─────────────────────┤
│ LangGraph (7 nodes): │   │ Celery Workers      │
│                      │   │ • Batch analysis    │
│ 1. Route Failure     │   │ • Scheduled tasks   │
│ 2. Extract Features  │   │ • Report generation │
│ 3. Query RAG         │   │ • Integrations      │
│ 4. Reason & Analyze  │   │ Workers: 4          │
│ 5. Generate Insights │   │ Concurrency: 4      │
│ 6. Rank Results      │   └─────────────────────┘
│ 7. Output Format     │
│                      │
│ Port: 5000           │
│ Timeout: 300s        │
└──────────┬───────────┘
           │
    ┌──────┴─────────────────────────────────────┐
    │                                           │
    ▼                                           ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│      KNOWLEDGE LAYER     │       │     PERSISTENCE LAYER   │
├─────────────────────────┤       ├─────────────────────────┤
│ Pinecone Vector DB:     │       │ PostgreSQL:             │
│                         │       │ • Test metadata         │
│ Index 1 (Reasoning):    │       │ • Workflow history      │
│ • Test patterns         │       │ • User preferences      │
│ • Error signatures      │       │ • Analytics data        │
│ • Fix suggestions       │       │ Port: 5432              │
│                         │       │ Connections: 20         │
│ Index 2 (Synthesis):    │       │                         │
│ • Similar failures      │       │ MongoDB Atlas:          │
│ • Industry patterns     │       │ • Raw failure logs      │
│ • Best practices        │       │ • LLM conversation      │
│                         │       │ • Audit trail           │
│ Dimension: 1536         │       │ TTL: 90 days            │
│ Top-K: 5               │       │                         │
└─────────────────────────┘       └─────────────────────────┘
```

## Component Details

### 1. Frontend (Dashboard)

**Framework**: React 18 + TypeScript  
**Build Tool**: Vite  
**Styling**: TailwindCSS  
**State Management**: Redux  
**Port**: 5173

**Key Screens**:
- Failure Inbox (real-time list)
- Analysis Details (insights & recommendations)
- Workflow Triggers (run automation)
- Analytics Dashboard (trends & metrics)
- Settings (preferences & integrations)

**Features**:
- Server-Sent Events (SSE) for real-time updates
- WebSocket fallback for compatibility
- Responsive mobile design
- Dark mode support
- Keyboard shortcuts

### 2. API Layer (FastAPI)

**Framework**: FastAPI with Uvicorn  
**Port**: 5000  
**Authentication**: JWT tokens  
**Rate Limiting**: 60 req/min per IP  
**Timeout**: 30s per request

**Main Endpoints**:

```
POST   /api/failures              Create new failure
GET    /api/failures              List failures (paginated)
GET    /api/failures/{id}         Get failure details
PUT    /api/failures/{id}         Update failure
DELETE /api/failures/{id}         Delete failure

POST   /api/analysis              Start analysis
GET    /api/analysis/{id}         Get analysis results (stream)

POST   /api/workflows             Trigger workflow
GET    /api/workflows             List workflows
GET    /api/workflows/{id}/status Get workflow status

GET    /api/health                Service health
GET    /api/metrics               Prometheus metrics
POST   /api/auth/login            User authentication
```

**Middleware**:
- CORS
- Request logging
- Error handling
- JWT verification
- Rate limiting

### 3. Agent Layer (LangGraph)

**Framework**: LangGraph  
**Orchestration**: ReAct (Reasoning + Acting)  
**Nodes**: 7  
**Timeout**: 300 seconds  
**Max Iterations**: 10

**Node Pipeline**:

```
1. ROUTE NODE
   ├─ Classify failure type (crash, timeout, flaky, etc.)
   ├─ Extract priority level
   └─ Select analysis strategy

2. EXTRACT FEATURES NODE
   ├─ Parse logs
   ├─ Extract stack traces
   ├─ Identify error patterns
   └─ Extract timing data

3. QUERY RAG NODE
   ├─ Query reasoning index (80%)
   ├─ Query synthesis index (20%)
   ├─ Rank results by relevance
   └─ Format context

4. REASON NODE
   ├─ Apply chain-of-thought
   ├─ Analyze error root causes
   ├─ Generate hypotheses
   └─ Score each hypothesis

5. SYNTHESIZE NODE
   ├─ Combine LLM insights
   ├─ Cross-reference with patterns
   ├─ Apply confidence scoring
   └─ Generate confidence score

6. RANK NODE
   ├─ Score results
   ├─ Apply CRAG (if confidence < 0.7)
   ├─ Filter low-confidence results
   └─ Sort by relevance

7. FORMAT NODE
   ├─ Prepare output JSON
   ├─ Generate markdown report
   ├─ Create UI visualization data
   └─ Log analysis metrics
```

**Key Features**:
- Tool use for external APIs
- Memory management (within token limits)
- Graceful error handling
- Fallback strategies

### 4. Async Processing (Celery)

**Broker**: Redis (task queue)  
**Result Backend**: Redis (result storage)  
**Workers**: 4  
**Concurrency**: 4 tasks/worker  
**Prefetch**: 2 tasks

**Key Tasks**:
- `analyze_batch`: Process multiple failures
- `generate_report`: Create analysis reports
- `sync_integrations`: Push results to external systems
- `cleanup_cache`: Periodic cache maintenance
- `train_classifier`: Model updates (scheduled)

### 5. Knowledge Layer

#### Pinecone Vector Database

**Configuration**:
- **API Version**: 3.0
- **Namespace**: default
- **Dimension**: 1536 (OpenAI embedding size)

**Indexes**:

1. **Reasoning Index (80% RAG routing)**
   - **Namespace**: `reasoning`
   - **Purpose**: Chain-of-thought analysis
   - **Content**:
     - Test failure patterns
     - Error signatures
     - Fix recommendations
     - Stack trace analyses
   - **Metadata**: `type`, `severity`, `language`, `framework`

2. **Synthesis Index (20% RAG routing)**
   - **Namespace**: `synthesis`
   - **Purpose**: Context and best practices
   - **Content**:
     - Similar failure cases
     - Industry patterns
     - Testing best practices
     - Performance optimization tips
   - **Metadata**: `category`, `relevance_score`, `last_updated`

**Query Strategy**:
- Top-K retrieval (k=5)
- MMR (Maximum Marginal Relevance) for diversity
- Confidence threshold: 0.7
- Fallback: CRAG when low confidence

### 6. Data Layer

#### PostgreSQL (Primary Store)

**Version**: 13+  
**Port**: 5432  
**Connection Pool**: 20 (max 40)  
**SSL**: Required in production

**Schema**:

```sql
-- Core tables
failures          -- Test failure records
failure_logs      -- Detailed logs per failure
analyses          -- AI analysis results
workflows         -- Automation workflows
jobs              -- Background job tracking
users             -- User accounts
audit_logs        -- Security audit trail

-- Indexes
failures.created_at
failures.status
failures.project_id
analyses.failure_id
workflows.status
```

#### MongoDB Atlas (Log Store)

**Version**: 5.0+  
**Cluster**: Shared (production: Dedicated M10)  
**Retention**: 90 days (TTL index)
**Backup**: Daily snapshots

**Collections**:

```
failures_raw        -- Raw failure logs (TTL)
llm_conversations   -- LLM call history
audit_trail         -- User actions
integrations_log    -- External API calls
```

#### Redis (Cache & Queue)

**Port**: 6379-6380 (primary + replica)  
**Memory**: 2GB  
**TTL**: 3600s (default)  
**Eviction**: LRU

**Usage**:
- **DB 0**: Celery task queue
- **DB 1**: Analysis result cache
- **DB 2**: User session cache
- **DB 3**: Feature cache

### 7. Observability

#### Langfuse (LLM Monitoring)

**Port**: 3000  
**Features**:
- LLM call tracing
- Token usage tracking
- Cost analytics
- Model performance metrics
- User interaction tracking

**Data Collected**:
- Prompt/completion tokens
- Model name and version
- Latency per call
- Cost per call
- Cache hits

#### Prometheus Metrics

**Port**: 9090  
**Scrape Interval**: 15s  
**Retention**: 15 days

**Key Metrics**:
- `http_requests_total` - API request count
- `http_request_duration_seconds` - Request latency
- `rag_query_duration_seconds` - RAG latency
- `llm_tokens_used` - Token consumption
- `agent_iterations` - Analysis iterations
- `celery_task_duration_seconds` - Task duration

#### Structured Logging

**Format**: JSON  
**Level**: INFO (prod), DEBUG (dev)  
**Rotation**: Daily, 10 backups  
**Path**: `./logs/ddn-ai.log`

**Fields**:
- timestamp
- level
- service
- request_id
- user_id
- message
- trace_id (for distributed tracing)

### 8. Integration Layer

#### GitHub Integration

- **Webhooks**: Push, PR, Release events
- **API**: Create issues, post comments
- **Credentials**: OAuth + PAT
- **Use Cases**: Auto-create issues, link PRs

#### Jenkins Integration

- **Protocol**: REST API
- **Authentication**: Token-based
- **Features**: Trigger jobs, monitor builds
- **Use Cases**: Trigger test reruns, mark as flaky

#### n8n Automation

**Workflows**:
1. **Auto-trigger**: Analyze failure → Create issue → Notify team
2. **Manual-trigger**: Dashboard button → Run analysis → Send report
3. **Refinement**: Collect feedback → Update model → Test improvements

**Nodes**: GitHub, Slack, Email, HTTP, Database

### 9. LLM Provider Strategy

#### Provider Selection

```
┌─────────────────────────────────────────┐
│ Input Request                           │
└────────────────────┬────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Check Model Availability│
        └──────┬─────────────┬──┘
               │             │
               ▼             ▼
         Claude        Gemini
        (Primary)    (Secondary)
               │             │
               └──────┬──────┘
                      │
                      ▼
            ┌─────────────────────┐
            │ LLM Call (streaming)│
            │ Timeout: 60s        │
            │ Tokens: Context used│
            └──────┬──────────────┘
                   │
              ┌────┴────┐
              │          │
              ▼          ▼
         Success   Fallback
                      │
                      ▼
              OpenAI (Fallback)
              Timeout: 60s
```

**Model Selection**:
- **Claude 3.5 Sonnet**: Default (reasoning & analysis)
- **Gemini Flash**: Secondary (parallel processing)
- **OpenAI GPT-4**: Fallback (reliability)

#### Token Management

- **Context Window**: 200K tokens (Claude), 1M (Gemini Pro)
- **Cost Optimization**: Prompt caching for repeated patterns
- **Rate Limiting**: Per-model quotas

### 10. Deployment Topology

#### Local Development

```
Docker Compose (all services):
├─ API (5000)
├─ Dashboard (5173)
├─ PostgreSQL (5432)
├─ MongoDB (local or Atlas)
├─ Redis (6379-6380)
├─ Pinecone (cloud API)
├─ Langfuse (3000)
├─ Celery Worker
├─ n8n (5678)
└─ Jenkins (8080)
```

#### Production (Kubernetes)

```
Namespace: ddn-ai
├─ API Deployment (3 replicas)
├─ Worker Deployment (4 replicas)
├─ Dashboard StatefulSet (1 replica)
├─ Celery Flower UI (1 replica)
├─ Prometheus (1 replica)
├─ PostgreSQL StatefulSet (1 primary + 1 replica)
├─ Redis StatefulSet (1 primary + 1 replica)
└─ Ingress (API + Dashboard)
```

## Data Flow Examples

### Failure Analysis Workflow

```
1. User submits test failure via Dashboard
   POST /api/failures
   {
     "test_name": "TestUserLogin",
     "error": "AssertionError: Expected 200, got 500",
     "logs": "...",
     "project_id": "proj_123"
   }

2. API stores in PostgreSQL + MongoDB

3. Celery task triggered via Redis

4. Worker calls Agent via LangGraph

5. Agent queries Pinecone (dual-index):
   - Query: "AssertionError 500 login auth"
   - Reasoning index: Get analysis strategies
   - Synthesis index: Get similar cases
   - Merge results

6. Agent calls Claude 3.5 Sonnet with context

7. Claude returns reasoning + recommendations

8. Agent scores results (CRAG if needed)

9. Results stored in PostgreSQL

10. Langfuse logs all LLM calls

11. Dashboard updated via SSE

12. n8n automation triggered:
    - Create GitHub issue
    - Notify Slack
    - Update tracking sheet
```

### Caching Strategy

```
Request arrives:
  → Check Redis DB2 (feature cache)
  → If HIT: Return cached result (< 100ms)
  → If MISS: Call RAG + LLM
  → Store in Redis (TTL: 3600s)
  → Return result

Result: ~80% cache hit rate during office hours
```

## Performance Characteristics

| Operation | Target | Actual | Notes |
|-----------|--------|--------|-------|
| API latency | <500ms | 200-400ms | Cached, simple ops |
| Analysis latency | <5s | 2-4s | Full LLM pipeline |
| RAG query | <500ms | 300-400ms | Pinecone + vector ops |
| LLM generation | <2s | 1.5-2s | Streaming, token usage |
| Dashboard load | <2s | 1-1.5s | React + SSE |
| Cache hit ratio | >40% | ~60% | Office hours peak |

## Security Architecture

```
┌─────────────────────────────────────────────┐
│ External Network                            │
└──────────────────┬──────────────────────────┘
                   │ HTTPS (TLS 1.3)
                   ▼
┌─────────────────────────────────────────────┐
│ Load Balancer (AWS ALB)                     │
├─────────────────────────────────────────────┤
│ • SSL termination                           │
│ • DDoS protection (AWS Shield)              │
│ • Rate limiting                             │
└──────────────┬──────────────────────────────┘
               │ Private VPC
               ▼
    ┌──────────────────────────────┐
    │ API Pods (Kubernetes)        │
    ├──────────────────────────────┤
    │ • Network policies           │
    │ • Pod security policies      │
    │ • RBAC enabled               │
    └──────────┬──────────────────┘
               │
        ┌──────┴──────────────────┐
        │                         │
        ▼                         ▼
    Database (PostgreSQL)  Redis (encrypted at rest)
    (encrypted at rest)    (encrypted in transit)
    (encrypted in transit) (AUTH enabled)
```

## Disaster Recovery

- **RTO** (Recovery Time Objective): <1 hour
- **RPO** (Recovery Point Objective): <5 minutes
- **Backup**: Daily snapshots, 30-day retention
- **Failover**: Automated to replica in <30 seconds
- **Monitoring**: Continuous health checks

## Scaling Strategy

### Horizontal Scaling

- **API**: Replicate (load balanced)
- **Workers**: Increase worker replicas (auto-scale on queue depth)
- **Database**: Read replicas for queries
- **Cache**: Redis cluster mode (sharding)

### Vertical Scaling

- **Memory**: Increase per-node memory for LLM calls
- **CPU**: Increase for RAG queries and analysis
- **Storage**: Expand PostgreSQL volumes

### Cost Optimization

- **Spot instances**: For worker nodes (fault-tolerant)
- **Reserved capacity**: For database/cache (steady state)
- **Regional distribution**: Multi-region for lower latency
- **Model selection**: Use cheaper models when possible

## Dependencies

- **Critical**: PostgreSQL, Redis, Pinecone, Claude API
- **Important**: MongoDB, Langfuse, n8n
- **Nice-to-have**: Jenkins, GitHub (can operate standalone)

---

**Architecture Version**: 1.0  
**Last Updated**: November 2025  
**Next Review**: March 2026
