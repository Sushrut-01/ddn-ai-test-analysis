# Complete System Architecture - DDN AI Test Failure Analysis

**Version**: 1.0
**Date**: October 2025
**Status**: Final Design

---

## 🎯 Architecture Principles

1. **Intelligent Routing**: AI decides what data to fetch (not fixed paths)
2. **Token Efficiency**: RAG-first approach reduces AI API costs by 90%
3. **Selective Code Analysis**: Only fetch GitHub code for code-related errors
4. **Database-Centric**: All data pre-stored in MongoDB/PostgreSQL
5. **Human-in-Loop**: Manual intervention for complex cases

---

## 🏗️ Complete System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                   COMPLETE SYSTEM FLOW                          │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [EXTERNAL - Already Happening]                                │
│  GitHub/Jenkins → MongoDB/PostgreSQL (Data pre-stored)         │
│                                                                 │
│  ────────────────────────────────────────────────────────────  │
│                                                                 │
│  [DDN AI WORKFLOW STARTS HERE]                                 │
│                                                                 │
│  1. TRIGGER                                                    │
│     └─ Jenkins webhook / Scheduled check                       │
│                                                                 │
│  2. INITIAL DATA FETCH (Minimal)                               │
│     └─ MongoDB Query: Get build_id, error_log, status         │
│        (Only 3 fields, NOT 40+ collections)                    │
│                                                                 │
│  3. LANGGRAPH ERROR CLASSIFICATION                             │
│     ├─ RAG Search (Pinecone)                                   │
│     │  └─ Find similar past errors                             │
│     ├─ Error Category Detection                                │
│     │  ├─ CODE_ERROR (needs GitHub)                            │
│     │  ├─ TEST_FAILURE (needs GitHub)                          │
│     │  ├─ INFRA_ERROR (no GitHub needed)                       │
│     │  ├─ DEPENDENCY_ERROR (no GitHub needed)                  │
│     │  └─ CONFIG_ERROR (no GitHub needed)                      │
│     └─ Decision: needs_code_analysis?                          │
│                                                                 │
│  4. ROUTING DECISION                                           │
│     │                                                           │
│     ├─ IF needs_code_analysis == FALSE (80% of cases)          │
│     │   • Infra/Dependency/Config errors                       │
│     │   • NO additional DB queries                             │
│     │   • Use RAG solution directly                            │
│     │   • Generate fix (5 seconds) ──────────────┐             │
│     │                                             │             │
│     └─ IF needs_code_analysis == TRUE (20% of cases)           │
│         • Code/Test errors                                     │
│         • Use MCP to query MongoDB:                            │
│         •   - Full error details                               │
│         •   - Stack trace                                      │
│         • Use MCP to fetch GitHub:                             │
│         •   - Specific failing files only                      │
│         • Claude analyzes code                                 │
│         • Generate code fix (15 seconds) ───────┐              │
│                                                  │              │
│  5. SOLUTION GENERATION ◄────────────────────────┴──────────────┘
│     └─ AI generates:                                           │
│        ├─ Root cause analysis                                  │
│        ├─ Fix recommendations                                  │
│        └─ Prevention strategies                                │
│                                                                 │
│  6. STORAGE                                                    │
│     ├─ MongoDB: Solution + metadata                            │
│     └─ Pinecone: Vector embedding (for future RAG)             │
│                                                                 │
│  7. NOTIFICATION                                               │
│     ├─ Microsoft Teams: Automated alert                        │
│     └─ Dashboard: Manual trigger button                        │
│                                                                 │
│  8. HUMAN-IN-LOOP                                              │
│     └─ Expert review via dashboard                             │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 📊 Component Details

### **1. Data Sources (Pre-Existing)**

```
GitHub Repository
└─ Test automation code (Python + Robot Framework)

Jenkins CI/CD
└─ Build logs, test results, console output

↓ (External process - not part of our scope)

MongoDB Collections:
├─ builds (build metadata)
├─ console_logs (full console output)
├─ test_results (test execution data)
├─ error_details (stack traces)
└─ debug_logs (detailed debug info)

PostgreSQL Tables:
├─ build_metadata (structured data)
├─ test_suites (test suite info)
└─ user_mappings (QA engineer assignments)
```

---

### **2. LangGraph Error Classification Agent**

```python
# Error Classification State Machine

State: ErrorAnalysisState
├─ build_id: str
├─ error_log: str
├─ error_category: str
├─ similar_errors: list
├─ needs_github: bool
├─ github_files: list
└─ solution: str

Workflow Steps:
1. classify_error(state)
   └─ Analyze error keywords → Determine category

2. search_similar_errors_rag(state)
   └─ Query Pinecone → Find past solutions

3. route_based_on_category(state)
   └─ IF needs_github: fetch_github_code_mcp()
   └─ ELSE: generate_solution_from_rag()

4. Final output:
   └─ Root cause + Fix recommendations
```

**Error Categories:**

| Category | Needs GitHub? | Keywords | Action |
|----------|---------------|----------|--------|
| **CODE_ERROR** | ✅ Yes | SyntaxError, NullPointerException, TypeError | Fetch code → Analyze |
| **TEST_FAILURE** | ✅ Yes | AssertionError, test failed | Fetch test code → Analyze |
| **INFRA_ERROR** | ❌ No | OutOfMemoryError, DiskSpace, NetworkError | Use RAG solution |
| **DEPENDENCY_ERROR** | ❌ No | ModuleNotFoundError, ClassNotFoundException | Use RAG solution |
| **CONFIG_ERROR** | ❌ No | ConfigurationException, permission denied | Use RAG solution |

---

### **3. MCP (Model Context Protocol) Servers**

#### **MongoDB MCP Server**

```python
# mongodb_mcp_server.py

Tools:
├─ mongodb_get_full_error_details(build_id)
│  └─ Returns: Complete stack trace, error context
│
├─ mongodb_get_console_log(build_id)
│  └─ Returns: Full console output
│
├─ mongodb_get_test_results(build_id)
│  └─ Returns: Test execution results
│
└─ mongodb_get_debug_logs(build_id)
   └─ Returns: Detailed debug information

Purpose: Selective database queries (only when needed)
```

#### **GitHub MCP Server**

```python
# github_mcp_server.py

Tools:
├─ github_get_file(repo, file_path, start_line, end_line)
│  └─ Returns: Source code snippet
│
├─ github_get_blame(repo, file_path, line)
│  └─ Returns: Who changed what, when
│
└─ github_get_commit_history(repo, file_path)
   └─ Returns: Recent changes to file

Purpose: Fetch only relevant code files (not entire repo)
```

---

### **4. RAG (Retrieval-Augmented Generation)**

```
Pinecone Vector Database

Document Structure:
{
  "id": "error_12345",
  "values": [0.123, 0.456, ...],  // Embedding vector
  "metadata": {
    "error_category": "INFRA_ERROR",
    "error_message": "OutOfMemoryError: Java heap space",
    "solution": "Increase heap size to 4GB using -Xmx4g",
    "success_rate": 0.98,
    "times_used": 15,
    "avg_resolution_time": "5 minutes",
    "last_used": "2025-01-15",
    "build_type": "DDN_STORAGE",
    "severity": "HIGH"
  }
}

Query Process:
1. User error → Generate embedding (OpenAI Embeddings)
2. Similarity search in Pinecone (k=5)
3. Return top 5 similar past solutions
4. Filter by category, success_rate
5. Use as context for AI analysis
```

---

### **5. n8n Workflow Orchestration**

```
n8n Workflow Nodes:

1. Webhook Trigger
   └─ Receives Jenkins failure event

2. MongoDB Query (Initial)
   └─ Get minimal data: build_id, error_log, status

3. HTTP Request → LangGraph Service
   └─ POST /classify-error
   └─ Body: {build_id, error_log, status}
   └─ Response: {category, needs_code_analysis, similar_solutions}

4. IF Condition
   └─ IF needs_code_analysis == false → Node 5a
   └─ ELSE → Node 5b

5a. Code Node (RAG Solution)
   └─ Extract solution from similar_solutions
   └─ Format response

5b. HTTP Request → Claude with MCP
   └─ POST https://api.anthropic.com/v1/messages
   └─ Headers: anthropic-beta: mcp-client-2025-04-04
   └─ Body: {
        mcp_servers: [mongodb-mcp, github-mcp],
        messages: [{role: "user", content: "..."}]
      }

6. MongoDB Insert (Store Solution)

7. Pinecone Insert (Vector Embedding)

8. Teams Webhook (Notification)

9. Dashboard Update (Optional)
```

---

### **6. Notification System**

**Microsoft Teams Notification Structure:**

```json
{
  "type": "MessageCard",
  "@context": "https://schema.org/extensions",
  "summary": "Test Case Failure - ETTxyz",
  "sections": [
    {
      "activityTitle": "🚨 Test Case Failed: ETTxyz",
      "activitySubtitle": "Failing since 5 days",
      "facts": [
        {"name": "Pipeline", "value": "EXAScaler-Smoke-Tests"},
        {"name": "Test Suite", "value": "Health_Check_Suite"},
        {"name": "Script", "value": "test_memory_usage.py:127"},
        {"name": "Error Category", "value": "INFRA_ERROR"},
        {"name": "Error Code", "value": "OutOfMemoryError"}
      ],
      "text": "**Root Cause**: JVM heap size insufficient\\n**Recommended Fix**: Increase heap to 4GB\\n**Prevention**: Set minimum heap for all DDN builds"
    }
  ],
  "potentialAction": [
    {
      "@type": "OpenUri",
      "name": "View Jenkins Log",
      "targets": [{"os": "default", "uri": "https://jenkins/job/123"}]
    },
    {
      "@type": "OpenUri",
      "name": "View in Dashboard",
      "targets": [{"os": "default", "uri": "https://dashboard/failure/123"}]
    }
  ]
}
```

---

### **7. Dashboard (UI)**

**Features:**
- Historical failure view
- Manual trigger button for deep analysis
- Filter by:
  - Test suite
  - Error category
  - Date range
  - Priority
- Export to CSV/PDF
- Integration with Jenkins (SSO)

**Tech Stack (Proposed):**
- Frontend: React + TypeScript
- State Management: Redux
- UI Library: Material-UI
- Charts: Recharts
- API: REST (Node.js + Express)

---

## 📈 Data Flow Examples

### **Example 1: Infrastructure Error (80% of cases)**

```
1. Jenkins webhook: Build #12345 failed
   └─ n8n receives event

2. MongoDB query: Get minimal data
   └─ {
        build_id: "12345",
        error_log: "OutOfMemoryError: Java heap space at line 245",
        status: "FAILURE"
      }

3. LangGraph classification:
   └─ Category: INFRA_ERROR
   └─ needs_code_analysis: FALSE
   └─ RAG search found 5 similar errors

4. Solution from RAG (NO GitHub, NO extra DB queries):
   └─ "Root Cause: JVM heap size insufficient
       Fix: Increase heap to 4GB using -Xmx4g
       Prevention: Set minimum heap for all DDN builds"

5. Store solution → Send Teams notification

Total Time: 5 seconds
API Calls: 1 (LangGraph only)
Cost: $0.01
```

---

### **Example 2: Code Error (20% of cases)**

```
1. Jenkins webhook: Build #12346 failed
   └─ n8n receives event

2. MongoDB query: Get minimal data
   └─ {
        build_id: "12346",
        error_log: "NullPointerException at DDNStorage.java:127",
        status: "FAILURE"
      }

3. LangGraph classification:
   └─ Category: CODE_ERROR
   └─ needs_code_analysis: TRUE
   └─ File path extracted: src/main/java/DDNStorage.java

4. Claude with MCP:
   a) MCP Tool: mongodb_get_full_error_details(12346)
      └─ Returns: Complete stack trace

   b) MCP Tool: github_get_file("ddn-repo", "DDNStorage.java", 120, 135)
      └─ Returns: Source code lines 120-135

   c) Claude analyzes:
      └─ Identifies: Missing null check at line 127

5. Solution generated:
   └─ Root Cause: storageConfig can be null
   └─ Code Fix:
       ```java
       + if (storageConfig == null) {
       +     throw new IllegalStateException("Storage not initialized");
       + }
       ```
   └─ Test case: testSaveDataWithoutInit()

6. Store solution → Send Teams notification

Total Time: 15 seconds
API Calls: 3 (LangGraph + 2 MCP tools + Claude)
Cost: $0.08
```

---

## 🔧 Configuration Files

### **n8n Environment Variables**

```env
# AI Services
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...

# Databases
MONGODB_URI=mongodb://localhost:27017/ddn
POSTGRES_URI=postgresql://user:pass@localhost:5432/ddn
PINECONE_INDEX=ddn-error-solutions

# Services
LANGGRAPH_SERVICE_URL=http://localhost:5000
JENKINS_URL=http://jenkins.ddn.com
GITHUB_TOKEN=ghp_...

# Notifications
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...

# MCP Servers
MONGODB_MCP_URL=http://localhost:5001/sse
GITHUB_MCP_URL=http://localhost:5002/sse

# Configuration
AGING_THRESHOLD_DAYS=5
MAX_TOKENS=8000
```

---

## 🚀 Deployment Architecture

```
Production Environment:

┌─────────────────────────────────────────┐
│         Load Balancer (nginx)           │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
   ┌────▼────┐         ┌───▼─────┐
   │ n8n (1) │         │ n8n (2) │
   └────┬────┘         └────┬────┘
        │                   │
   ┌────▼───────────────────▼────┐
   │   LangGraph Service (API)    │
   │   (Flask/FastAPI - Port 5000)│
   └─────────────┬─────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
   ┌────▼────┐      ┌────▼────┐
   │MongoDB  │      │Pinecone │
   │Cluster  │      │  Cloud  │
   └─────────┘      └─────────┘
```

---

## 📊 Performance Monitoring

**Key Metrics to Track:**

1. **Response Time**
   - Target: < 20 seconds for 95% of cases
   - Alert: If > 30 seconds

2. **Accuracy**
   - Target: > 85% correct root cause
   - Measure: QA engineer feedback

3. **Token Usage**
   - Target: < 10,000 tokens per analysis
   - Alert: If > 15,000 tokens

4. **API Costs**
   - Target: < $0.15 per analysis
   - Monitor: Daily spending

5. **Database Query Count**
   - Target: < 5 queries per analysis
   - Alert: If > 10 queries

---

**Next Steps**:
- Review [MCP Configuration](../mcp-configs/MCP-SETUP.md)
- Implement [LangGraph Agent](../implementation/LANGGRAPH-AGENT.md)
- Follow [Best Practices](../best-practices/BEST-PRACTICES.md)

**Last Updated**: October 17, 2025
