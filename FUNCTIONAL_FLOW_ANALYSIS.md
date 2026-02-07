# DDN-AI Project: Functional Flow Analysis
## End-to-End Workflow Documentation

**Date:** 2026-02-02
**Architect:** DB & API Architect
**Purpose:** Document how data flows through the system

---

## OVERVIEW: System Architecture Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    DDN AI PLATFORM FLOWS                         │
│                                                                  │
│  1. Test Execution → Failure Detection → AI Analysis → Actions  │
│  2. User Requests → Authentication → Project Context → Response │
│  3. AI Processing → RAG Search → Code Analysis → Recommendations│
└─────────────────────────────────────────────────────────────────┘
```

---

## FLOW 1: TEST FAILURE ANALYSIS (Core Workflow)

### 1.1 Entry Point: Jenkins Build Failure

```
┌───────────────┐
│   JENKINS     │ (Port 8081)
│   CI Server   │
└───────┬───────┘
        │ Test execution completes
        │ Status: FAILURE
        │
        ▼
   Build Result
   ├─ build_id: "DDN-Test-Job-123"
   ├─ status: "FAILURE"
   ├─ error_log: "AssertionError: Expected 200, got 500"
   ├─ stack_trace: "..."
   └─ timestamp: "2026-02-02T10:30:00Z"
```

**What Happens:**
1. Jenkins runs test suite (DDN or Guruttava project)
2. Test fails → Jenkins captures:
   - Console output
   - Stack trace
   - JUnit XML results (Robot Framework)
3. Jenkins stores artifacts

---

### 1.2 Data Ingestion Path

#### **Path A: Automated Trigger (Webhook)**
```
JENKINS
   │
   │ POST webhook on build complete
   │
   ▼
┌─────────────────────┐
│  N8N Workflow       │ (Port 5678)
│  (Automation)       │
└──────────┬──────────┘
           │
           │ Extract build data
           │ Validate webhook
           │
           ▼
┌─────────────────────┐
│ Manual Trigger API  │ (Port 5004)
│ /api/trigger-auto   │
└──────────┬──────────┘
           │
           ▼
     [FLOW CONTINUES BELOW]
```

#### **Path B: Manual Trigger (Dashboard)**
```
DASHBOARD UI (React)
   │
   │ User clicks "Analyze This Build"
   │
   ▼
┌─────────────────────────┐
│ Dashboard API           │ (Port 5006)
│ /api/manual-trigger     │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Manual Trigger API      │ (Port 5004)
│ /api/trigger-manual     │
└──────────┬──────────────┘
           │
           ▼
     [FLOW CONTINUES BELOW]
```

---

### 1.3 Data Storage (Dual Database)

```
Manual Trigger API
   │
   ├─────────────────────┬──────────────────────┐
   │                     │                      │
   ▼                     ▼                      ▼
MongoDB Atlas       PostgreSQL            Build Metadata
(Test Data)         (Analysis)            Extraction
   │                    │                      │
   │ Collection:        │ Table:               │
   │ • ddn_test_        │ • build_metadata    │ Parse:
   │   failures         │ • failure_analysis  │ • Robot logs
   │ • guruttava_       │                     │ • JUnit XML
   │   test_failures    │                     │ • Stack traces
   │                    │                     │
   │ Document:          │ Row:                │
   │ {                  │ id, build_id,       │
   │   build_id,        │   job_name,         │
   │   test_name,       │   status,           │
   │   error_msg,       │   timestamp,        │
   │   stack_trace,     │   project_id (NEW!) │
   │   timestamp,       │                     │
   │   project_id: 1    │                     │
   │ }                  │                     │
   └────────────────────┴─────────────────────┘
```

**Key Issue Found:**
- ⚠️ MongoDB uses collection prefixes (`ddn_`, `guruttava_`) - not true isolation
- ✅ PostgreSQL has `project_id` column but no RLS enforcement

---

### 1.4 AI Analysis Workflow (Multi-Agent System)

```
Manual Trigger API (Port 5004)
   │
   │ Step 1: Route to AI Engine
   │
   ▼
┌──────────────────────────────────────────────┐
│  LangGraph Agent (ReAct Pattern)            │ (Port 5000)
│  File: langgraph_agent.py                   │
│                                              │
│  POST /api/analyze-error                    │
│  Body: {                                     │
│    "error_log": "...",                       │
│    "stack_trace": "...",                     │
│    "project_id": 1                           │
│  }                                           │
└──────────────┬───────────────────────────────┘
               │
               │ Step 2: Classification
               │
┌──────────────▼───────────────────────────────┐
│  REACT AGENT WORKFLOW                        │
│  (7 Nodes - Iterative Reasoning)            │
│                                              │
│  Node 1: CLASSIFY                            │
│  ├─ Determine error category:               │
│  │  • CODE_ERROR                             │
│  │  • INFRA_ERROR                            │
│  │  • TEST_FAILURE                           │
│  │  • DEPENDENCY_ERROR                       │
│  │  • CONFIG_ERROR                           │
│  │                                           │
│  Node 2: REASONING                           │
│  ├─ Generate analysis plan                   │
│  │  "Need to search similar failures"       │
│  │  "Need to check GitHub code"             │
│  │                                           │
│  Node 3: SELECT_TOOL                         │
│  ├─ Choose tool based on category:          │
│  │  • rag_search (80% of cases)             │
│  │  • github_mcp (20% - CODE_ERROR only)    │
│  │                                           │
│  Node 4: EXECUTE_TOOL                        │
│  ├─ Run selected tool                        │
│  │                                           │
│  Node 5: OBSERVE                             │
│  ├─ Check tool results                       │
│  ├─ Self-correction if needed                │
│  │                                           │
│  Node 6: ANSWER                              │
│  ├─ Generate root cause analysis             │
│  │                                           │
│  Node 7: VERIFY                              │
│  └─ Validate confidence score                │
│                                              │
└──────────────┬───────────────────────────────┘
               │
               │ Step 3: Routing Decision
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
   CODE_ERROR    OTHER CATEGORIES
        │             │
        ▼             ▼
┌─────────────┐ ┌──────────────┐
│   CLAUDE    │ │   RAG ONLY   │
│  Deep Code  │ │   Fast Path  │
│  Analysis   │ │   (Pinecone) │
└──────┬──────┘ └──────┬───────┘
       │               │
       └───────┬───────┘
               │
               ▼
         Final Analysis
```

**Analysis Output:**
```json
{
  "classification": "CODE_ERROR",
  "root_cause": "NullPointerException in LoginService.authenticate()",
  "fix_recommendation": "Add null check for user object before calling methods",
  "confidence_score": 0.87,
  "similar_failures": [...],
  "github_files": ["src/services/LoginService.java"],
  "analysis_type": "CLAUDE_DEEP_ANALYSIS",
  "estimated_cost_usd": 0.0234
}
```

---

### 1.5 RAG Search Flow (Knowledge Base)

```
ReAct Agent → SELECT_TOOL: "rag_search"
   │
   ▼
┌────────────────────────────────────────┐
│  RAG SEARCH PIPELINE                   │
│                                        │
│  Step 1: Generate Embedding            │
│  ├─ OpenAI Embeddings API              │
│  │   Model: text-embedding-3-small     │
│  │   Input: error_log + stack_trace    │
│  │   Output: 1536-dim vector           │
│  │                                     │
│  Step 2: Vector Search (Pinecone)      │
│  ├─ Query: embedding vector            │
│  ├─ Filter: project_id namespace       │
│  │   • DDN → namespace: "ddn_knowledge"│
│  │   • Guruttava → "guruttava_knowledge"│
│  ├─ Top-K: 10 results                  │
│  │                                     │
│  Step 3: Reranking (Optional)          │
│  ├─ Reranking Service (Port 5011)      │
│  │   Model: cross-encoder/ms-marco     │
│  │   Rerank top 10 → top 3             │
│  │                                     │
│  Step 4: Context Assembly               │
│  └─ Combine:                           │
│      • Similar failure docs            │
│      • Historical fixes                │
│      • Knowledge base articles         │
└────────────┬───────────────────────────┘
             │
             ▼
      Contextualized Results
      (Sent to Claude/Gemini)
```

**Key Issue Found:**
- ⚠️ Namespace filtering exists BUT not enforced at query level
- Could accidentally query wrong namespace

---

### 1.6 GitHub Code Analysis (20% of Cases)

```
ReAct Agent → Routing: "CODE_ERROR detected"
   │
   ▼
┌────────────────────────────────────────┐
│  GITHUB MCP SERVER                     │ (Port 5002)
│                                        │
│  Capabilities:                         │
│  ├─ List files in repo                 │
│  ├─ Read file contents                 │
│  ├─ Search code                        │
│  ├─ Get commit history                 │
│  └─ Check PR status                    │
│                                        │
│  Configuration (from env):             │
│  ├─ DDN Project:                       │
│  │   Repo: Sushrut-01/ddn-test-data    │
│  ├─ Guruttava Project:                 │
│  │   Repo: Guruttava-Org/automation    │
│                                        │
└────────────┬───────────────────────────┘
             │
             ▼
  Retrieve actual source code
  ├─ File: src/services/LoginService.java
  ├─ Last modified: 2026-01-15
  └─ Commit: abc123 "Fix user validation"
             │
             ▼
     Send code to Claude API
     ├─ Model: claude-sonnet-4-20250514
     ├─ Prompt: "Analyze this code for bug"
     └─ Response: Detailed code review
```

**Key Issue Found:**
- ⚠️ GitHub repo configured per project BUT mixed in environment variables
- No dynamic routing based on `project_id`

---

### 1.7 Results Storage & Integration Triggers

```
LangGraph Agent completes analysis
   │
   ▼
┌────────────────────────────────────────┐
│  RESULT STORAGE                        │
│                                        │
│  PostgreSQL: failure_analysis table    │
│  INSERT INTO failure_analysis (        │
│    build_id,                           │
│    project_id,          ← CRITICAL     │
│    classification,                     │
│    root_cause,                         │
│    fix_recommendation,                 │
│    confidence_score,                   │
│    ai_model_used,                      │
│    token_usage,                        │
│    analysis_cost_usd,                  │
│    created_at                          │
│  ) VALUES (...)                        │
└────────────┬───────────────────────────┘
             │
             │ Trigger integrations
             │
    ┌────────┼────────┬────────┐
    │        │        │        │
    ▼        ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ JIRA │ │GITHUB│ │SLACK │ │TEAMS │
│Service│ │ PR   │ │Notify│ │Alert │
│(5009)│ │      │ │(5012)│ │      │
└──────┘ └──────┘ └──────┘ └──────┘
    │        │        │        │
    │        │        │        │
    ▼        ▼        ▼        ▼
Create     Create    Send      Send
Ticket     PR with   Message   Card
DDN-123    Fix       #qa       Alert
```

---

## FLOW 2: USER AUTHENTICATION & PROJECT ACCESS

### 2.1 Login Flow

```
USER (Dashboard)
   │
   │ POST /api/auth/login
   │ Body: { "email": "user@company.com", "password": "..." }
   │
   ▼
┌─────────────────────────────────────────┐
│  AUTH SERVICE                           │ (Port 5013)
│  File: auth_service.py                  │
│                                         │
│  Step 1: Validate Credentials           │
│  ├─ Query: SELECT * FROM users          │
│  │         WHERE email = ?              │
│  ├─ Verify: bcrypt.check(password)      │
│  │                                      │
│  Step 2: Get User's Projects            │
│  ├─ Query: SELECT p.*, up.role          │
│  │         FROM projects p              │
│  │         JOIN user_projects up        │
│  │         WHERE up.user_id = ?         │
│  │         AND p.status = 'active'      │
│  │                                      │
│  Result:                                │
│  User "john@company.com" has access to: │
│  • Project 1 (DDN) - Role: developer    │
│  • Project 2 (Guruttava) - Role: viewer │
│                                         │
│  Step 3: Generate JWT Token             │
│  ├─ Payload: {                          │
│  │   "user_id": 42,                     │
│  │   "email": "john@company.com",       │
│  │   "role": "user",                    │
│  │   "default_project_id": 1,           │
│  │   "projects": [1, 2],                │
│  │   "exp": 1738512000                  │
│  │  }                                   │
│  ├─ Sign with: JWT_SECRET_KEY           │
│  └─ Algorithm: HS256                    │
└─────────────┬───────────────────────────┘
              │
              ▼
        Return JWT Token
        {
          "token": "eyJhbGc...",
          "user": {...},
          "projects": [...]
        }
```

**Key Issue Found:**
- ⚠️ Single JWT secret for all projects (should be per-project)
- ⚠️ Token includes `default_project_id` but not validated on every request

---

### 2.2 API Request Flow (With Project Context)

```
USER REQUEST
   │
   │ GET /api/projects/2/failures?limit=50
   │ Headers: Authorization: Bearer eyJhbGc...
   │
   ▼
┌─────────────────────────────────────────┐
│  DASHBOARD API                          │ (Port 5006)
│  File: dashboard_api_full.py (251KB!)   │
│                                         │
│  Current Flow (INCONSISTENT):           │
│                                         │
│  ❌ Step 1: Parse JWT                   │
│     ├─ Extract user_id from token       │
│     └─ No project validation!           │
│                                         │
│  ❌ Step 2: Extract project_id          │
│     ├─ From URL path: project_id=2      │
│     └─ No access check!                 │
│                                         │
│  ❌ Step 3: Query Database              │
│     └─ SELECT * FROM failure_analysis   │
│        WHERE project_id = 2             │
│        └─ BUT: No RLS enforcement!      │
│                                         │
│  RISK: If code forgets WHERE clause     │
│        → Data leakage!                  │
└─────────────────────────────────────────┘
```

**What SHOULD Happen (With My Middleware):**
```
USER REQUEST
   │
   ▼
┌─────────────────────────────────────────┐
│  MIDDLEWARE: project_context.py         │
│  @require_auth                          │
│  @require_project_access(role='viewer') │
│                                         │
│  ✅ Step 1: Validate JWT                │
│     ├─ Decode token                     │
│     ├─ Check expiry                     │
│     └─ Set g.user_id                    │
│                                         │
│  ✅ Step 2: Extract project_id          │
│     ├─ Priority 1: URL path             │
│     ├─ Priority 2: Query param          │
│     ├─ Priority 3: Request body         │
│     └─ Priority 4: JWT default          │
│                                         │
│  ✅ Step 3: Verify Access               │
│     └─ Query: user_projects table       │
│        WHERE user_id=42 AND project_id=2│
│        └─ Result: role='viewer' ✓       │
│                                         │
│  ✅ Step 4: Set DB Context              │
│     └─ Execute: SELECT set_project_     │
│        context(2)                       │
│        └─ PostgreSQL RLS now enforces   │
│           project_id=2 on ALL queries   │
│                                         │
│  ✅ Step 5: Set Flask g context         │
│     ├─ g.project_id = 2                 │
│     ├─ g.project_role = 'viewer'        │
│     └─ g.project_info = {...}           │
└─────────────┬───────────────────────────┘
              │
              ▼
        Route Handler
        (Automatic filtering)
```

---

## FLOW 3: INTEGRATION FLOWS

### 3.1 Jira Ticket Creation

```
Analysis Complete (confidence > 0.70)
   │
   ▼
┌─────────────────────────────────────────┐
│  JIRA INTEGRATION SERVICE               │ (Port 5009)
│  File: jira_integration_service.py      │
│                                         │
│  POST /api/jira/create-issue            │
│  Body: {                                │
│    "build_id": "DDN-123",               │
│    "project_id": 1,      ← REQUIRED     │
│    "error_category": "CODE_ERROR",      │
│    "root_cause": "...",                 │
│    "fix_recommendation": "..."          │
│  }                                      │
│                                         │
│  Step 1: Get Project Config             │
│  ├─ Query: project_configurations       │
│  │   WHERE project_id = 1               │
│  │                                      │
│  │   Returns:                           │
│  │   • jira_project_key: "DDN"          │
│  │   • jira_url: "ddn.atlassian.net"    │
│  │   • jira_email: "..."                │
│  │   • jira_api_token: "..."            │
│  │                                      │
│  Step 2: Create Jira Issue              │
│  ├─ API: POST /rest/api/3/issue         │
│  ├─ Project: DDN                        │
│  ├─ Issue Type: Bug                     │
│  ├─ Priority: High (based on failures)  │
│  ├─ Labels: [ai-detected, code-error]   │
│  └─ Description: [Formatted analysis]   │
│                                         │
│  Step 3: Store Ticket Reference         │
│  └─ UPDATE failure_analysis             │
│     SET jira_issue_key = 'DDN-456'      │
│     WHERE build_id = 'DDN-123'          │
└─────────────────────────────────────────┘
```

**Key Issue Found:**
- ✅ Code reads project config from DB (GOOD!)
- ⚠️ But falls back to env vars if not found (RISKY)
- ⚠️ Encryption fields exist but not used

---

### 3.2 GitHub PR Workflow (Self-Healing)

```
High Confidence Fix (> 0.85)
   │
   ▼
┌─────────────────────────────────────────┐
│  SELF-HEALING SERVICE                   │ (Port 5008)
│  File: self_healing_service.py          │
│                                         │
│  POST /api/self-healing/create-pr       │
│                                         │
│  Step 1: Generate Code Fix              │
│  ├─ Use Claude to generate patch        │
│  └─ Validate syntax                     │
│                                         │
│  Step 2: Create GitHub Branch           │
│  ├─ Branch: fix/ai-repair-DDN-123       │
│  └─ From: main                          │
│                                         │
│  Step 3: Commit Changes                 │
│  ├─ File: src/LoginService.java         │
│  └─ Message: "AI Fix: Add null check"   │
│                                         │
│  Step 4: Create Pull Request            │
│  ├─ Title: "🤖 AI Fix: NullPointer..."  │
│  ├─ Body: [Analysis + Fix + Tests]      │
│  └─ Labels: [ai-generated, needs-review]│
│                                         │
│  Step 5: Notify Team                    │
│  └─ Slack notification sent             │
└─────────────────────────────────────────┘
```

---

## FLOW 4: MULTI-PROJECT DATA ISOLATION

### 4.1 Current State (WEAK ISOLATION)

```
┌─────────────────────────────────────────────────────┐
│  PostgreSQL (Single Database)                       │
│                                                      │
│  failure_analysis table                             │
│  ┌────┬────────────┬──────────┬─────────────────┐  │
│  │ id │ project_id │ build_id │ error_message   │  │
│  ├────┼────────────┼──────────┼─────────────────┤  │
│  │ 1  │     1      │ DDN-001  │ Login failed    │  │ ← DDN
│  │ 2  │     1      │ DDN-002  │ DB timeout      │  │ ← DDN
│  │ 3  │     2      │ GURU-001 │ App crashed     │  │ ← Guruttava
│  │ 4  │     2      │ GURU-002 │ Element missing │  │ ← Guruttava
│  └────┴────────────┴──────────┴─────────────────┘  │
│                                                      │
│  ⚠️  RISK: Query without WHERE project_id = ?       │
│     → Returns ALL rows (mixed projects!)            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  MongoDB Atlas (Single Database: ddn_tests)         │
│                                                      │
│  Collections (by prefix):                           │
│  ├─ ddn_test_failures        ← DDN data             │
│  ├─ ddn_build_results                               │
│  ├─ guruttava_test_failures  ← Guruttava data       │
│  └─ guruttava_build_results                         │
│                                                      │
│  ⚠️  RISK: Code can query wrong collection          │
│     db['ddn_test_failures']  # If project_id=2 bug! │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Pinecone (Single Index: test-failures)             │
│                                                      │
│  Vectors with namespace filter:                     │
│  ├─ Namespace: "ddn_knowledge"     ← DDN            │
│  └─ Namespace: "guruttava_knowledge" ← Guruttava    │
│                                                      │
│  ⚠️  RISK: Query without namespace filter           │
│     → Returns vectors from all projects!            │
└─────────────────────────────────────────────────────┘
```

---

### 4.2 Recommended State (STRONG ISOLATION)

```
┌─────────────────────────────────────────────────────┐
│  PostgreSQL with Row-Level Security (RLS)           │
│                                                      │
│  ✅ Session variable: set_project_context(1)        │
│                                                      │
│  failure_analysis table (RLS enabled)               │
│  ├─ Policy: project_isolation_select                │
│  │   USING (project_id = get_current_project_id())  │
│  │                                                   │
│  └─ Effect: ALL queries automatically filtered      │
│     • SELECT * FROM failure_analysis                │
│       → Returns ONLY project_id=1 rows              │
│     • Even if code forgets WHERE clause!            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  MongoDB - Database Per Project (Recommended)       │
│                                                      │
│  ├─ ddn_project_db (Database 1)                     │
│  │   ├─ test_failures       ← Only DDN data         │
│  │   └─ build_results                               │
│  │                                                   │
│  └─ guruttava_project_db (Database 2)               │
│      ├─ test_failures       ← Only Guruttava data   │
│      └─ build_results                               │
│                                                      │
│  ✅ Effect: Impossible to query wrong project       │
│     Connection string includes database name        │
└─────────────────────────────────────────────────────┘
```

---

## FLOW 5: COST & PERFORMANCE TRACKING

### 5.1 AI Cost Tracking

```
Every AI Analysis
   │
   ├─ Claude API Call
   │  ├─ Input tokens: 2,500
   │  ├─ Output tokens: 1,200
   │  ├─ Cost: $0.0234
   │  │
   │  └─ Stored in: ai_model_metrics table
   │     INSERT (
   │       project_id,
   │       model_name: 'claude-sonnet-4',
   │       input_tokens: 2500,
   │       output_tokens: 1200,
   │       cost_usd: 0.0234
   │     )
   │
   ├─ RAG Search
   │  ├─ OpenAI Embeddings: $0.0001
   │  └─ Pinecone Query: $0.0002
   │
   └─ Total Analysis Cost: $0.0237
      │
      └─ Dashboard shows:
         • Cost per project
         • Cost per day/week/month
         • Most expensive analyses
```

---

## SUMMARY: Critical Flow Issues

### ✅ **What Works:**
1. **Data ingestion** - Jenkins → MongoDB/PostgreSQL
2. **AI analysis** - ReAct agent with routing
3. **Integration triggers** - Jira, GitHub, Slack
4. **User authentication** - JWT tokens
5. **Project configurations** - DB storage

### 🔴 **Critical Gaps:**
1. **No RLS enforcement** - Data leakage risk
2. **Inconsistent project context** - 4 different methods
3. **Weak MongoDB isolation** - Collection prefixes only
4. **No namespace validation** - Pinecone can leak
5. **Monolithic API** - 251KB single file
6. **No connection pooling** - Performance under load

### 📊 **Flow Metrics:**
- **Average analysis time:** 8-15 seconds
- **AI routing:** 80% RAG, 20% Claude MCP
- **Success rate:** ~85% accurate classifications
- **Cost per analysis:** $0.02-0.05

---

## NEXT STEPS

**To fix the functional flows, we need:**

1. **Add RLS** → Automatic project filtering
2. **Implement middleware** → Consistent project context
3. **Migrate MongoDB** → Database per project
4. **Add validation** → Input sanitization
5. **Break down API** → Microservices

**Which flow do you want me to fix first?**
