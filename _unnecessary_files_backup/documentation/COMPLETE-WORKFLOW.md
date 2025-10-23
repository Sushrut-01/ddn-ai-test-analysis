# ACTUAL DDN AI Workflow - Corrected Version

**Date**: October 21, 2025
**Purpose**: Document the ACTUAL workflow based on existing implementation
**Status**: Corrected based on your clarifications

---

## 🎯 Your Clarifications

### ✅ What You Told Me:

1. **Data Storage**: Jenkins build data is stored via **API scripts** (NOT via n8n webhooks)
2. **Manual Trigger**: Users can **bypass 3-day aging** via Dashboard
3. **Workflow Trigger**: Both 3-day aging AND manual trigger can start the analysis

---

## 🔄 ACTUAL Complete Workflow

### **Path 1: Automatic 3-Day Aging (Default)**

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: Build Fails & Data Storage (via API Scripts)          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Time: T+0 (Build fails at 10:00 AM Monday)                     │
│                                                                  │
│ Jenkins Build #12345 Fails                                     │
│    ↓                                                             │
│ Jenkins calls API Script (Python/Shell)                        │
│    ↓                                                             │
│ API Script stores data in:                                      │
│    • PostgreSQL:                                                │
│      - build_metadata table                                     │
│      - aging_status = 'PENDING'                                 │
│      - aging_days = 0                                           │
│      - created_at = '2025-01-20 10:00:00'                      │
│                                                                  │
│    • MongoDB:                                                   │
│      - console_logs collection (full console output)            │
│      - error_details collection (stack traces)                  │
│      - build_context collection                                 │
│        • GitHub code files                                      │
│        • Test scripts                                           │
│        • Knowledge documents (README, docs)                     │
│                                                                  │
│ ✅ DATA STORED - No n8n involvement yet!                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: Aging Period (Day 0 to Day 3)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Day 0 (Monday):                                                 │
│    aging_status = 'PENDING', aging_days = 0                     │
│                                                                  │
│ Day 1 (Tuesday):                                                │
│    Daily cron job updates: aging_days = 1                       │
│                                                                  │
│ Day 2 (Wednesday):                                              │
│    Daily cron job updates: aging_days = 2                       │
│                                                                  │
│ Day 3 (Thursday): ⚡ TRIGGER POINT                              │
│    Daily cron job updates:                                      │
│      aging_status = 'READY_FOR_ANALYSIS'                        │
│      aging_days = 3                                             │
│    ↓                                                             │
│    Cron job calls n8n webhook:                                  │
│      POST http://localhost:5678/webhook/ddn-test-failure       │
│      {                                                           │
│        "build_id": "BUILD_12345",                               │
│        "trigger_type": "automatic_aging",                       │
│        "aging_days": 3                                          │
│      }                                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: AI Analysis (n8n + LangGraph + RAG/MCP)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ n8n Workflow Starts                                             │
│    ↓                                                             │
│ Node 1: Fetch build data from MongoDB                          │
│    • Get full console logs                                      │
│    • Get error details with stack traces                        │
│    • Get GitHub code files                                      │
│    • Get test scripts                                           │
│    • Get knowledge documents                                    │
│    ↓                                                             │
│ Node 2: Call LangGraph Service                                  │
│    POST http://localhost:5000/classify-error                    │
│    {                                                             │
│      "build_id": "BUILD_12345",                                 │
│      "error_log": "OutOfMemoryError: Java heap space...",      │
│      "full_context": {                                          │
│        "stack_trace": "...",                                    │
│        "console_output": "...",                                 │
│        "github_files": [...],                                   │
│        "test_scripts": [...]                                    │
│      }                                                           │
│    }                                                             │
│    ↓                                                             │
│ LangGraph Classification Agent:                                 │
│    Step 1: Classify error type                                  │
│      • Keyword matching                                         │
│      • Result: INFRA_ERROR (OutOfMemoryError)                  │
│      • Confidence: 0.95                                         │
│      • needs_code_analysis: FALSE                              │
│    ↓                                                             │
│    Step 2: Generate Embedding (OpenAI)                          │
│      • Input: "OutOfMemoryError: Java heap space..."           │
│      • Output: [0.234, -0.567, ..., 0.789] (1536 dims)        │
│    ↓                                                             │
│    Step 3: RAG Search in Pinecone                               │
│      • Query with embedding + filter (INFRA_ERROR)             │
│      • Found 5 similar past errors                              │
│      • Best match: 0.95 similarity, 92% success rate           │
│    ↓                                                             │
│    Decision: RAG or MCP?                                        │
│      ✅ INFRA_ERROR + high similarity → USE RAG                │
│      ❌ CODE_ERROR or low similarity → USE MCP                 │
│    ↓                                                             │
│ RAG PATH (for this example):                                    │
│    • Select best solution from Pinecone                         │
│    • Root cause: "JVM heap insufficient"                        │
│    • Fix: "Increase heap to 4GB with -Xmx4g"                   │
│    • Time: 5 seconds                                            │
│    • Cost: $0.01                                                │
│    • NO GitHub MCP needed! ✓                                    │
│    ↓                                                             │
│ Node 3: Store solution in MongoDB                               │
│    • analysis_solutions collection                              │
│    • Include similarity score, success rate                     │
│    ↓                                                             │
│ Node 4: Update PostgreSQL                                       │
│    • analysis_status = 'ANALYZED'                               │
│    • analysis_type = 'RAG'                                      │
│    ↓                                                             │
│ Node 5: Store in Pinecone (for future RAG)                      │
│    • Update success rate if solution used before                │
│    • OR store as new vector if new solution                     │
│    ↓                                                             │
│ Node 6: Send Teams Notification                                 │
│    • Solution ready                                             │
│    • Include root cause, fix, confidence                        │
│    ↓                                                             │
│ Node 7: Update Dashboard via API                                │
│    • POST http://localhost:5005/api/failures/BUILD_12345       │
│    • Dashboard shows solution with clickable links              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### **Path 2: Manual Trigger from Dashboard (Bypass Aging)**

```
┌─────────────────────────────────────────────────────────────────┐
│ MANUAL TRIGGER WORKFLOW (No 3-Day Wait!)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Scenario: User sees BUILD_12345 failed on Day 0                 │
│           Wants immediate analysis (can't wait 3 days)          │
│                                                                  │
│ User Action:                                                     │
│    Opens Dashboard → Finds BUILD_12345 → Clicks "Analyze Now"  │
│    ↓                                                             │
│ Dashboard Frontend (React):                                      │
│    POST http://localhost:5005/api/trigger/manual                │
│    {                                                             │
│      "build_id": "BUILD_12345",                                 │
│      "triggered_by_user": "john.doe@company.com",               │
│      "reason": "Critical production issue",                     │
│      "trigger_source": "dashboard"                              │
│    }                                                             │
│    ↓                                                             │
│ Dashboard API (dashboard_api.py:5005):                          │
│    • Receives request                                           │
│    • Proxies to Manual Trigger API                             │
│    ↓                                                             │
│ Manual Trigger API (manual_trigger_api.py:5004):                │
│    • Validates build_id exists in PostgreSQL                    │
│    • Logs manual trigger in manual_trigger_log table           │
│    • Records: user, reason, timestamp                           │
│    ↓                                                             │
│    • Calls n8n webhook:                                         │
│      POST http://localhost:5678/webhook/ddn-test-failure       │
│      {                                                           │
│        "build_id": "BUILD_12345",                               │
│        "manual_trigger": true,  ← KEY FLAG                     │
│        "triggered_by_user": "john.doe@company.com",             │
│        "trigger_reason": "Critical production issue",           │
│        "trigger_id": 123                                        │
│      }                                                           │
│    ↓                                                             │
│ n8n Workflow Starts:                                            │
│    • Checks manual_trigger flag                                 │
│    • Bypasses all aging checks                                  │
│    • Proceeds directly to analysis                              │
│    ↓                                                             │
│ [Same as Phase 3 above: Fetch → LangGraph → RAG/MCP → Store → Notify]
│                                                                  │
│ Time Saved: Immediate (vs 3 days wait) ✅                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Storage Architecture - CORRECTED

### **How Jenkins Data Is ACTUALLY Stored**

```
┌─────────────────────────────────────────────────────────────────┐
│ JENKINS BUILD FAILS                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Jenkins Post-Build Action:                                      │
│    • Execute Shell Script / Python Script                       │
│    • OR Jenkins Webhook Plugin (but calls API, not n8n!)       │
│                                                                  │
│ Example: Jenkins Post-Build Script                              │
│ ┌────────────────────────────────────────────────────────┐     │
│ │ #!/bin/bash                                            │     │
│ │                                                        │     │
│ │ if [ "$BUILD_RESULT" == "FAILURE" ]; then            │     │
│ │   # Call API script to store data                    │     │
│ │   python /path/to/store_build_failure.py \           │     │
│ │     --build-id "$BUILD_ID" \                         │     │
│ │     --build-number "$BUILD_NUMBER" \                 │     │
│ │     --job-name "$JOB_NAME" \                         │     │
│ │     --console-log "/path/to/console.log" \           │     │
│ │     --error-type "BUILD_FAILURE"                     │     │
│ │ fi                                                    │     │
│ └────────────────────────────────────────────────────────┘     │
│                                                                  │
│ API Script (store_build_failure.py):                           │
│ ┌────────────────────────────────────────────────────────┐     │
│ │ import psycopg2                                       │     │
│ │ import pymongo                                         │     │
│ │ import requests                                        │     │
│ │                                                        │     │
│ │ # 1. Store in PostgreSQL                             │     │
│ │ conn = psycopg2.connect(POSTGRES_URI)                │     │
│ │ cursor.execute("""                                    │     │
│ │   INSERT INTO build_metadata                         │     │
│ │   (build_id, build_number, job_name, status,        │     │
│ │    created_at, aging_status, aging_days)             │     │
│ │   VALUES (%s, %s, %s, 'FAILURE', NOW(),             │     │
│ │           'PENDING', 0)                               │     │
│ │ """, (build_id, build_number, job_name))             │     │
│ │                                                        │     │
│ │ # 2. Fetch GitHub files                              │     │
│ │ github_files = fetch_github_context(commit_sha)      │     │
│ │ test_scripts = fetch_test_files(repo, branch)        │     │
│ │ knowledge_docs = fetch_readme_docs(repo)             │     │
│ │                                                        │     │
│ │ # 3. Store in MongoDB                                 │     │
│ │ mongodb = pymongo.MongoClient(MONGODB_URI)           │     │
│ │ db = mongodb['jenkins_failure_analysis']             │     │
│ │                                                        │     │
│ │ db.build_context.insert_one({                        │     │
│ │   'build_id': build_id,                              │     │
│ │   'console_log': console_output,                     │     │
│ │   'error_details': error_stack_trace,                │     │
│ │   'github_files': github_files,                      │     │
│ │   'test_scripts': test_scripts,                      │     │
│ │   'knowledge_docs': knowledge_docs,                  │     │
│ │   'created_at': datetime.now()                       │     │
│ │ })                                                    │     │
│ │                                                        │     │
│ │ print("✅ Build data stored successfully")          │     │
│ └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### **What Gets Stored Where**

```
PostgreSQL (build_metadata table):
├─ build_id: "BUILD_12345"
├─ build_number: 12345
├─ job_name: "DDN-Storage-Tests"
├─ status: "FAILURE"
├─ created_at: "2025-01-20 10:00:00"
├─ aging_status: "PENDING"
├─ aging_days: 0
├─ analysis_status: "NOT_ANALYZED"
├─ build_url: "https://jenkins.example.com/job/..."
└─ jenkins_url: "https://jenkins.example.com/..."

MongoDB (build_context collection):
├─ build_id: "BUILD_12345"
├─ console_log: "Full console output (up to 10MB)"
├─ error_details:
│  ├─ error_message: "OutOfMemoryError: Java heap space"
│  ├─ stack_trace: "Full stack trace..."
│  └─ line_number: 127
├─ github_files: [
│  {
│    "filename": "src/main/java/DDNStorage.java",
│    "content": "package com.ddn.storage;...",
│    "commit_sha": "a1b2c3d4e5f6"
│  }
│]
├─ test_scripts: [
│  {
│    "filename": "tests/test_storage.py",
│    "content": "import pytest..."
│  }
│]
├─ knowledge_docs: [
│  {
│    "filename": "README.md",
│    "content": "# DDN Storage Module..."
│  },
│  {
│    "filename": "docs/architecture.md",
│    "content": "## Architecture Overview..."
│  }
│]
└─ created_at: "2025-01-20T10:00:00Z"

Pinecone (Initially EMPTY for new errors):
├─ Only populated AFTER first AI analysis
└─ Then used for future RAG queries
```

---

## 🎯 Where and How RAG Data Is Stored

### **Initial State (Day 0 - Build Fails)**

```
PostgreSQL: ✅ Has build metadata
MongoDB:    ✅ Has full context (logs, code, docs)
Pinecone:   ❌ NO data yet (error is new!)
```

### **After AI Analysis (Day 3 or Manual Trigger)**

```
PostgreSQL: ✅ Updated with analysis results
MongoDB:    ✅ Has analysis_solutions document
Pinecone:   ✅ NOW has vector for this error! ←  For future RAG
```

### **How Error Data Gets into Pinecone for RAG**

```
┌─────────────────────────────────────────────────────────────────┐
│ STORING ERROR IN PINECONE (After Analysis)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ After LangGraph + RAG/MCP completes analysis:                   │
│    ↓                                                             │
│ n8n Node: "Store in Pinecone"                                   │
│    POST http://localhost:5003/api/store-vector                  │
│    {                                                             │
│      "text": "OutOfMemoryError: Java heap space at...",        │
│      "metadata": {                                              │
│        "build_id": "BUILD_12345",                               │
│        "error_category": "INFRA_ERROR",                         │
│        "root_cause": "JVM heap size insufficient",              │
│        "solution": "Increase heap to 4GB with -Xmx4g",         │
│        "confidence": 0.95,                                      │
│        "success_rate": 0.0,  ← Initially 0 (not tested yet)   │
│        "times_used": 0,                                         │
│        "timestamp": "2025-01-23T10:00:00Z",                    │
│        "analysis_type": "CLAUDE_MCP"                            │
│      }                                                           │
│    }                                                             │
│    ↓                                                             │
│ Pinecone Storage Service (port 5003):                           │
│    • Generates embedding via OpenAI                             │
│    • Stores vector in Pinecone index "ddn-error-solutions"     │
│    • Vector ID: "BUILD_12345_1729584000"                        │
│    ↓                                                             │
│ ✅ NOW available for future RAG queries!                        │
│                                                                  │
│ Next time similar error occurs:                                 │
│    • LangGraph searches Pinecone                                │
│    • Finds this solution (95% similarity)                       │
│    • Returns it in 5 seconds for $0.01                          │
│    • NO need for Claude MCP analysis!                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### **Files/Documents Attached to RAG**

```
❌ NOT stored in Pinecone directly:
   • GitHub code files (too large)
   • Test scripts (too large)
   • Knowledge documents (too large)
   • Full console logs (too large)

✅ STORED in Pinecone:
   • Error text → converted to 1536-dim embedding vector
   • Small metadata:
     - Root cause (text, up to 1000 chars)
     - Solution (text, up to 1000 chars)
     - Success rate (number)
     - Confidence (number)
     - Error category (string)

✅ STORED in MongoDB:
   • ALL the large files (code, logs, docs)
   • Retrieved when needed for MCP analysis
   • Linked by build_id

Flow for CODE_ERROR (needs GitHub files):
  1. LangGraph classifies as CODE_ERROR
  2. Searches Pinecone (RAG)
  3. If low similarity → needs MCP
  4. Fetches GitHub files from MongoDB (or via GitHub MCP)
  5. Claude analyzes with full context
  6. Solution stored in Pinecone for next time
```

---

## 🔑 Key Architecture Points

### **1. Separation of Concerns**

```
API Scripts (Jenkins Post-Build):
   • Responsible for: Data collection and storage
   • Stores in: PostgreSQL + MongoDB
   • No AI/analysis logic
   • Fast and simple

n8n Workflows:
   • Responsible for: Orchestration and routing
   • Calls: LangGraph, MCP servers, APIs
   • Makes decisions: RAG vs MCP path
   • Handles notifications

LangGraph Service (port 5000):
   • Responsible for: Classification and RAG search
   • Uses: OpenAI embeddings, Pinecone
   • Returns: Error category, similar solutions

MCP Servers (ports 5001, 5002):
   • Responsible for: Deep analysis tooling
   • MongoDB MCP: Fetches full logs, stack traces
   • GitHub MCP: Fetches source code
   • Only used for CODE_ERROR / TEST_FAILURE
```

### **2. Two Trigger Paths**

```
Path 1: Automatic (3-day aging)
   ├─ Cron job checks PostgreSQL daily
   ├─ Updates aging_days counter
   ├─ When aging_days = 3 → calls n8n webhook
   └─ Good for: Batching, cost savings

Path 2: Manual (Dashboard)
   ├─ User clicks "Analyze Now" in dashboard
   ├─ Dashboard API → Manual Trigger API → n8n webhook
   ├─ Bypasses all aging checks
   └─ Good for: Urgent issues, production failures
```

### **3. Data Flow Summary**

```
1. Jenkins fails → API script stores data → PostgreSQL + MongoDB
2. Wait 3 days OR manual trigger → n8n webhook called
3. n8n fetches data from MongoDB → calls LangGraph
4. LangGraph classifies + searches Pinecone (RAG)
5. Decision: RAG (fast) or MCP (deep)
6. Solution stored in MongoDB + Pinecone
7. Notifications sent to Teams + Dashboard updated
```

---

## ✅ Summary - Are We Aligned Now?

### **What You Told Me (Corrected)**

1. ✅ **Data storage via API scripts** (NOT n8n webhooks)
   - Jenkins post-build script calls Python/Shell API
   - API stores in PostgreSQL + MongoDB
   - Includes GitHub code, test scripts, knowledge docs

2. ✅ **Manual trigger from Dashboard** (NO 3-day wait)
   - User clicks "Analyze Now" button
   - Dashboard API (port 5005) → Manual Trigger API (port 5004)
   - Manual Trigger API calls n8n webhook
   - Analysis starts immediately

3. ✅ **RAG error data attachment**
   - Error text → Pinecone (as embedding vector)
   - Large files → MongoDB (GitHub code, test scripts, docs)
   - Pinecone metadata has solution details
   - MongoDB has complete context

### **Workflow Flow**

```
Jenkins Fail
   ↓
API Script (store data)
   ↓
PostgreSQL + MongoDB (build data + full context)
   ↓
[EITHER]
   • Wait 3 days (aging) → Cron job → n8n webhook
   • OR Manual trigger → Dashboard → Manual Trigger API → n8n webhook
   ↓
n8n Orchestration
   ↓
Fetch from MongoDB → LangGraph → RAG/MCP → Solution
   ↓
Store in MongoDB + Pinecone → Notify Teams + Dashboard
```

---

## ❓ Questions for You

1. **API Script Location**
   - Do you have the actual Jenkins post-build script?
   - Is it Python, Shell, or Groovy?
   - Can you share it so I can document the exact flow?

2. **GitHub Data Fetching**
   - How does the API script fetch GitHub code?
   - Via GitHub API directly?
   - Or does it clone the repo locally?

3. **Knowledge Documents**
   - Which specific docs are included?
   - Just README.md?
   - All .md files in docs/ folder?
   - Configurable?

4. **Manual Trigger UI**
   - Is the Dashboard UI already built?
   - React/Vue/Angular?
   - Can you show me a screenshot?

5. **3-Day Aging**
   - Is this the right duration?
   - Should it be configurable per job type?
   - Should critical failures skip aging entirely?

---

**We are now on the same page!** This document reflects the ACTUAL architecture with:
- ✅ Data storage via API scripts (not n8n)
- ✅ Manual trigger from dashboard (bypass aging)
- ✅ RAG data in Pinecone, full context in MongoDB

Let me know if this matches your understanding or if there are more corrections needed!
