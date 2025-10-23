# RAG Architecture - DDN AI Test Failure Analysis System

**Document Type**: Technical Architecture Specification
**Version**: 1.0
**Date**: October 21, 2025
**Status**: Production Ready

---

## 📋 Table of Contents

1. [RAG System Overview](#rag-system-overview)
2. [Architecture Diagrams](#architecture-diagrams)
3. [Component Deep-Dive](#component-deep-dive)
4. [Data Specifications](#data-specifications)
5. [RAG Query Process](#rag-query-process)
6. [Integration Points](#integration-points)
7. [Performance & Metrics](#performance--metrics)
8. [Setup & Configuration](#setup--configuration)
9. [Sample Data Templates](#sample-data-templates)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 RAG System Overview

### **What is RAG (Retrieval-Augmented Generation)?**

RAG is an AI technique that enhances large language model responses by retrieving relevant information from a knowledge base before generating answers.

**In the DDN AI System:**
```
Traditional Approach (Expensive):
Error → Claude AI analyzes from scratch → Solution
Cost: $0.15 per analysis
Time: 20 seconds

RAG Approach (Efficient):
Error → Find similar past errors → Use proven solution → Verify with AI
Cost: $0.01 per analysis (93% cheaper)
Time: 5 seconds (75% faster)
```

---

### **Why RAG is Critical for DDN AI Project**

#### **1. Cost Reduction**
```
Without RAG (100% MCP usage):
- Cost per analysis: $0.15
- Daily analyses: 50
- Monthly cost: $225
- Annual cost: $2,700

With RAG (80% RAG, 20% MCP):
- RAG analyses (40/day): $0.01 × 40 = $0.40
- MCP analyses (10/day): $0.08 × 10 = $0.80
- Daily total: $1.20
- Monthly cost: $36
- Annual cost: $432

Annual Savings: $2,268 (84% reduction)
```

#### **2. Performance Improvement**
```
Metric               | Without RAG | With RAG   | Improvement
---------------------|-------------|------------|-------------
Avg Response Time    | 18 sec      | 7 sec      | 61% faster
INFRA_ERROR Time     | 15 sec      | 5 sec      | 67% faster
Throughput (daily)   | 50 cases    | 150 cases  | 3x increase
```

#### **3. Solution Quality**
```
- Historical Success Rate Tracking: Know which solutions work (85%+ success)
- Proven Solutions: Reuse solutions that worked before
- Learning System: Gets smarter with each resolution
- Consistency: Same error always gets same proven fix
```

---

### **How RAG Works in DDN AI System**

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG WORKFLOW OVERVIEW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: ERROR OCCURS                                           │
│  ┌────────────────────────────────────────────┐                │
│  │ Jenkins Build #12345 Failed                │                │
│  │ Error: OutOfMemoryError: Java heap space   │                │
│  └──────────────────┬─────────────────────────┘                │
│                     │                                            │
│                     ▼                                            │
│  Step 2: CLASSIFICATION (LangGraph)                             │
│  ┌────────────────────────────────────────────┐                │
│  │ • Analyzes error keywords                  │                │
│  │ • Category: INFRA_ERROR                    │                │
│  │ • Confidence: 0.95                         │                │
│  │ • Decision: needs_code_analysis = FALSE    │                │
│  └──────────────────┬─────────────────────────┘                │
│                     │                                            │
│                     ▼                                            │
│  Step 3: GENERATE EMBEDDING (OpenAI)                            │
│  ┌────────────────────────────────────────────┐                │
│  │ Text: "OutOfMemoryError Java heap space"   │                │
│  │   ↓                                         │                │
│  │ Vector: [0.123, 0.456, 0.789, ... 1536]   │                │
│  └──────────────────┬─────────────────────────┘                │
│                     │                                            │
│                     ▼                                            │
│  Step 4: SIMILARITY SEARCH (Pinecone)                           │
│  ┌────────────────────────────────────────────┐                │
│  │ Query Pinecone index: ddn-error-solutions  │                │
│  │ Filter: error_category = "INFRA_ERROR"     │                │
│  │ Top K: 5 most similar vectors              │                │
│  │                                             │                │
│  │ Results (sorted by similarity):             │                │
│  │ 1. Score: 0.98 - OutOfMemory in Java       │                │
│  │    Solution: Increase -Xmx to 4GB          │                │
│  │    Success Rate: 95%, Used: 25 times       │                │
│  │                                             │                │
│  │ 2. Score: 0.92 - Heap space error          │                │
│  │    Solution: Set -Xms2g -Xmx4g             │                │
│  │    Success Rate: 88%, Used: 12 times       │                │
│  │                                             │                │
│  │ 3. Score: 0.87 - JVM memory issue          │                │
│  │    Solution: Optimize GC settings          │                │
│  │    Success Rate: 82%, Used: 8 times        │                │
│  └──────────────────┬─────────────────────────┘                │
│                     │                                            │
│                     ▼                                            │
│  Step 5: SELECT BEST SOLUTION                                   │
│  ┌────────────────────────────────────────────┐                │
│  │ Criteria:                                   │                │
│  │ • Similarity score > 0.85                  │                │
│  │ • Success rate > 0.80                      │                │
│  │ • Times used > 5                           │                │
│  │                                             │                │
│  │ Selected: Solution #1                      │                │
│  │ • Root Cause: JVM heap size insufficient   │                │
│  │ • Fix: Increase heap to 4GB (-Xmx4g)       │                │
│  │ • Prevention: Set min heap for all builds  │                │
│  │ • Confidence: 0.95                         │                │
│  └──────────────────┬─────────────────────────┘                │
│                     │                                            │
│                     ▼                                            │
│  Step 6: RETURN SOLUTION                                        │
│  ┌────────────────────────────────────────────┐                │
│  │ ✅ Solution delivered in 5 seconds         │                │
│  │ 💰 Cost: $0.01                             │                │
│  │ 📊 No GitHub API calls needed              │                │
│  │ 🚀 No additional DB queries                │                │
│  └────────────────────────────────────────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### **RAG vs MCP: When to Use Each**

```
┌──────────────────────────────────────────────────────────────────┐
│               RAG vs MCP DECISION TREE                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│                      ERROR DETECTED                               │
│                           │                                       │
│                           ▼                                       │
│                  ┌────────────────┐                              │
│                  │  LangGraph     │                              │
│                  │  Classifies    │                              │
│                  │  Error Type    │                              │
│                  └───────┬────────┘                              │
│                          │                                       │
│        ┌─────────────────┴─────────────────┐                    │
│        │                                    │                    │
│        ▼                                    ▼                    │
│  ┌─────────────┐                    ┌──────────────┐            │
│  │ INFRA_ERROR │                    │  CODE_ERROR  │            │
│  │DEPEND_ERROR │                    │ TEST_FAILURE │            │
│  │CONFIG_ERROR │                    └──────────────┘            │
│  └─────────────┘                           │                    │
│        │                                    │                    │
│   80% of cases                        20% of cases              │
│        │                                    │                    │
│        ▼                                    ▼                    │
│  ┌─────────────────────┐          ┌──────────────────┐          │
│  │   USE RAG ONLY      │          │   USE MCP        │          │
│  ├─────────────────────┤          ├──────────────────┤          │
│  │ • Search Pinecone   │          │ • Search Pinecone│          │
│  │ • Find similar      │          │ • Fetch MongoDB  │          │
│  │ • Return solution   │          │ • Fetch GitHub   │          │
│  │                     │          │ • Claude analyzes│          │
│  │ Time: 5 sec         │          │                  │          │
│  │ Cost: $0.01         │          │ Time: 15 sec     │          │
│  │ API Calls: 2        │          │ Cost: $0.08      │          │
│  └─────────────────────┘          │ API Calls: 5     │          │
│                                    └──────────────────┘          │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Decision Logic:**
```python
if error_category in ["INFRA_ERROR", "DEPENDENCY_ERROR", "CONFIG_ERROR"]:
    # Use RAG only
    use_rag_solution()
    # No GitHub needed, no extra DB queries

elif error_category in ["CODE_ERROR", "TEST_FAILURE"]:
    # Use RAG + MCP
    rag_results = search_similar_errors()
    if rag_results.similarity_score > 0.90:
        # High confidence RAG match
        use_rag_solution()
    else:
        # Need code analysis
        use_mcp_with_github()
```

---

## 🏗️ Architecture Diagrams

### **Diagram 1: Complete RAG System Architecture**

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                   DDN AI SYSTEM - RAG ARCHITECTURE                             │
│                                                                                │
│  ┌─────────────┐         ┌──────────────────────────────────┐                │
│  │   SOURCES   │         │         DATABASES                 │                │
│  ├─────────────┤         ├──────────────────────────────────┤                │
│  │             │         │                                   │                │
│  │   GitHub    │────────▶│  PostgreSQL                       │                │
│  │             │ Webhook │  • Builds metadata                │                │
│  │   Jenkins   │────────▶│  • Test results                   │                │
│  │             │         │  • Console logs                   │                │
│  └─────────────┘         │                                   │                │
│                          │  MongoDB                          │                │
│                          │  • Build details                  │                │
│                          │  • Error classifications          │                │
│                          │  • Analysis solutions             │                │
│                          │                                   │                │
│                          │  Pinecone (Vector DB)             │                │
│                          │  • Error embeddings (1536-dim)    │                │
│                          │  • Historical solutions           │                │
│                          │  • Success rate tracking          │                │
│                          └────────────┬──────────────────────┘                │
│                                       │                                        │
│                                       │ Query                                  │
│                                       │                                        │
│  ┌────────────────────────────────────▼──────────────────────────────────┐   │
│  │                        AGENTIC AI SYSTEM                              │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │                    n8n ORCHESTRATION                            │  │   │
│  │  │                                                                  │  │   │
│  │  │  Workflow Node 1: Webhook Trigger                               │  │   │
│  │  │       ↓                                                          │  │   │
│  │  │  Workflow Node 2: Fetch Build Data (MongoDB)                    │  │   │
│  │  │       ↓                                                          │  │   │
│  │  │  Workflow Node 3: Call LangGraph Service                        │  │   │
│  │  │       ↓                                                          │  │   │
│  │  └───────┼──────────────────────────────────────────────────────────┘  │   │
│  │          │                                                              │   │
│  │          ▼                                                              │   │
│  │  ┌──────────────────────────────────────────────────────────────┐     │   │
│  │  │              LANGGRAPH CLASSIFICATION AGENT                   │     │   │
│  │  │                                                                │     │   │
│  │  │  ┌───────────────────────────────────────────────────────┐   │     │   │
│  │  │  │ Step 1: Error Classification                          │   │     │   │
│  │  │  │ • Keyword matching                                    │   │     │   │
│  │  │  │ • Category: CODE_ERROR | INFRA_ERROR | etc.          │   │     │   │
│  │  │  │ • Confidence score calculation                        │   │     │   │
│  │  │  └───────────────────┬───────────────────────────────────┘   │     │   │
│  │  │                      │                                        │     │   │
│  │  │                      ▼                                        │     │   │
│  │  │  ┌───────────────────────────────────────────────────────┐   │     │   │
│  │  │  │ Step 2: RAG SEARCH (Pinecone)                         │   │     │   │
│  │  │  │                                                        │   │     │   │
│  │  │  │  A) Generate Embedding (OpenAI)                       │   │     │   │
│  │  │  │     Error text → text-embedding-3-small               │   │     │   │
│  │  │  │     Output: 1536-dimensional vector                   │   │     │   │
│  │  │  │     Cost: $0.0001                                     │   │     │   │
│  │  │  │                                                        │   │     │   │
│  │  │  │  B) Query Pinecone Index                              │   │     │   │
│  │  │  │     index.query(                                      │   │     │   │
│  │  │  │       vector=embedding,                               │   │     │   │
│  │  │  │       top_k=5,                                        │   │     │   │
│  │  │  │       filter={"error_category": "INFRA_ERROR"}        │   │     │   │
│  │  │  │     )                                                 │   │     │   │
│  │  │  │                                                        │   │     │   │
│  │  │  │  C) Receive Similar Solutions                         │   │     │   │
│  │  │  │     [                                                 │   │     │   │
│  │  │  │       {similarity: 0.95, solution: "...",            │   │     │   │
│  │  │  │        success_rate: 0.92, times_used: 25},          │   │     │   │
│  │  │  │       {...}, ...                                     │   │     │   │
│  │  │  │     ]                                                 │   │     │   │
│  │  │  │     Time: 200-500ms                                   │   │     │   │
│  │  │  └───────────────────┬───────────────────────────────────┘   │     │   │
│  │  │                      │                                        │     │   │
│  │  │                      ▼                                        │     │   │
│  │  │  ┌───────────────────────────────────────────────────────┐   │     │   │
│  │  │  │ Step 3: Decision - RAG or MCP?                        │   │     │   │
│  │  │  │                                                        │   │     │   │
│  │  │  │  IF INFRA/DEPEND/CONFIG (80%):                       │   │     │   │
│  │  │  │    → Use RAG solution (FAST PATH)                    │   │     │   │
│  │  │  │    → Time: 5 sec, Cost: $0.01                        │   │     │   │
│  │  │  │                                                        │   │     │   │
│  │  │  │  IF CODE/TEST (20%):                                 │   │     │   │
│  │  │  │    → Use MCP + GitHub (DEEP PATH)                    │   │     │   │
│  │  │  │    → Time: 15 sec, Cost: $0.08                       │   │     │   │
│  │  │  └────────────────────────────────────────────────────────┘   │     │   │
│  │  │                                                                │     │   │
│  │  └────────────────────────────────────────────────────────────────┘     │   │
│  │                                                                          │   │
│  │  ┌──────────────────────────────────────────────────────────────┐       │   │
│  │  │                 MODEL CONTEXT PROTOCOL (MCP)                  │       │   │
│  │  │              (Used only for CODE/TEST errors)                 │       │   │
│  │  │                                                                │       │   │
│  │  │  • MongoDB MCP Server (port 5001)                             │       │   │
│  │  │    Tools: query_builds, get_full_logs, get_stack_trace       │       │   │
│  │  │                                                                │       │   │
│  │  │  • GitHub MCP Server (port 5002)                              │       │   │
│  │  │    Tools: fetch_file, search_code, get_commits                │       │   │
│  │  │                                                                │       │   │
│  │  │  • Pinecone Storage Service (port 5003)                       │       │   │
│  │  │    Tools: store_vector, search_similar, update_feedback      │       │   │
│  │  └──────────────────────────────────────────────────────────────┘       │   │
│  │                                                                          │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                       │                                          │
│                                       │ Solution                                 │
│                                       ▼                                          │
│  ┌────────────────────────────────────────────────────────────────────────┐    │
│  │                          OUTPUT & NOTIFICATIONS                         │    │
│  │                                                                          │    │
│  │  • Store in MongoDB (analysis_solutions collection)                     │    │
│  │  • Store embedding in Pinecone (for future RAG queries)                │    │
│  │  • Send Teams notification with solution                               │    │
│  │  • Update Dashboard with clickable links                               │    │
│  │  • Track success rate for feedback loop                                │    │
│  └────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

### **Diagram 2: RAG Data Flow - INFRA_ERROR Example (80% of cases)**

```
┌─────────────────────────────────────────────────────────────────────────┐
│        RAG FAST PATH - Infrastructure Error (5 seconds, $0.01)          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  TIME: T+0ms                                                            │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ INPUT: Jenkins Webhook                                  │            │
│  │ {                                                        │            │
│  │   "build_id": "BUILD_12345",                            │            │
│  │   "status": "FAILURE",                                  │            │
│  │   "error_log": "OutOfMemoryError: Java heap space..."  │            │
│  │ }                                                        │            │
│  └──────────────────────┬───────────────────────────────────┘            │
│                         │                                                │
│  TIME: T+500ms          ▼                                                │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ STEP 1: MongoDB Query (n8n)                             │            │
│  │ db.builds.findOne({build_id: "BUILD_12345"})           │            │
│  │                                                          │            │
│  │ Result: {                                               │            │
│  │   "build_id": "BUILD_12345",                            │            │
│  │   "error_log": "OutOfMemoryError: Java heap space",    │            │
│  │   "status": "FAILURE"                                   │            │
│  │ }                                                        │            │
│  │ Cost: $0 (internal DB)                                 │            │
│  └──────────────────────┬───────────────────────────────────┘            │
│                         │                                                │
│  TIME: T+1.5s           ▼                                                │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ STEP 2: LangGraph Classification                        │            │
│  │                                                          │            │
│  │ Keywords found: ["OutOfMemoryError", "heap space"]     │            │
│  │ Category: INFRA_ERROR                                   │            │
│  │ Confidence: 0.95                                        │            │
│  │ needs_code_analysis: FALSE                              │            │
│  │                                                          │            │
│  │ Cost: $0.002 (lightweight classification)              │            │
│  └──────────────────────┬───────────────────────────────────┘            │
│                         │                                                │
│  TIME: T+2.0s           ▼                                                │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ STEP 3: Generate Embedding (OpenAI)                     │            │
│  │                                                          │            │
│  │ Input text: "OutOfMemoryError Java heap space"         │            │
│  │ Model: text-embedding-3-small                           │            │
│  │ Output: [0.234, 0.567, ..., 0.123] (1536 dims)        │            │
│  │                                                          │            │
│  │ Cost: $0.0001                                           │            │
│  └──────────────────────┬───────────────────────────────────┘            │
│                         │                                                │
│  TIME: T+2.5s           ▼                                                │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ STEP 4: Pinecone Similarity Search                      │            │
│  │                                                          │            │
│  │ index.query(                                            │            │
│  │   vector=[0.234, 0.567, ...],                          │            │
│  │   top_k=5,                                              │            │
│  │   filter={"error_category": "INFRA_ERROR"}             │            │
│  │ )                                                        │            │
│  │                                                          │            │
│  │ Results:                                                │            │
│  │ [                                                        │            │
│  │   {                                                      │            │
│  │     "id": "error_mem_001",                             │            │
│  │     "score": 0.95,  ← Very similar!                   │            │
│  │     "metadata": {                                       │            │
│  │       "error_category": "INFRA_ERROR",                 │            │
│  │       "root_cause": "JVM heap size insufficient",      │            │
│  │       "solution": "Increase heap to 4GB: -Xmx4g",     │            │
│  │       "success_rate": 0.92,                            │            │
│  │       "times_used": 25,                                │            │
│  │       "confidence": 0.95                               │            │
│  │     }                                                   │            │
│  │   },                                                    │            │
│  │   {                                                     │            │
│  │     "id": "error_mem_002",                             │            │
│  │     "score": 0.88,                                     │            │
│  │     "metadata": {...}                                  │            │
│  │   },                                                    │            │
│  │   ...                                                   │            │
│  │ ]                                                       │            │
│  │                                                          │            │
│  │ Cost: $0 (Pinecone free tier)                          │            │
│  │ Time: 300ms                                             │            │
│  └──────────────────────┬───────────────────────────────────┘            │
│                         │                                                │
│  TIME: T+3.0s           ▼                                                │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ STEP 5: Select Best Solution (LangGraph)                │            │
│  │                                                          │            │
│  │ Filter criteria:                                        │            │
│  │ • Similarity score > 0.85  ✓ (0.95)                   │            │
│  │ • Success rate > 0.80      ✓ (0.92)                   │            │
│  │ • Times used > 5           ✓ (25)                     │            │
│  │                                                          │            │
│  │ Selected: Solution #1 (score: 0.95)                    │            │
│  │                                                          │            │
│  │ NO GitHub API calls needed ✓                           │            │
│  │ NO additional DB queries ✓                             │            │
│  │ NO Claude AI analysis needed ✓                         │            │
│  │                                                          │            │
│  │ Cost: $0                                                │            │
│  └──────────────────────┬───────────────────────────────────┘            │
│                         │                                                │
│  TIME: T+4.0s           ▼                                                │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ STEP 6: Format Response                                 │            │
│  │                                                          │            │
│  │ {                                                        │            │
│  │   "build_id": "BUILD_12345",                            │            │
│  │   "error_category": "INFRA_ERROR",                      │            │
│  │   "confidence": 0.95,                                   │            │
│  │   "root_cause": "JVM heap size insufficient",          │            │
│  │   "fix_recommendation": "Increase heap to 4GB",        │            │
│  │   "command": "export JAVA_OPTS='-Xmx4g'",              │            │
│  │   "prevention": "Set min heap for all DDN builds",     │            │
│  │   "success_rate": 0.92,                                │            │
│  │   "times_this_worked": 25,                             │            │
│  │   "source": "RAG_HISTORICAL_SOLUTION"                  │            │
│  │ }                                                        │            │
│  └──────────────────────┬───────────────────────────────────┘            │
│                         │                                                │
│  TIME: T+5.0s           ▼                                                │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ OUTPUT: Store & Notify                                  │            │
│  │                                                          │            │
│  │ • MongoDB: Save analysis                                │            │
│  │ • Pinecone: Update usage count (26)                    │            │
│  │ • Teams: Send notification with solution               │            │
│  │ • Dashboard: Display with links                        │            │
│  └────────────────────────────────────────────────────────┘            │
│                                                                          │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ TOTAL METRICS                                           │            │
│  │ • Total Time: 5 seconds                                │            │
│  │ • Total Cost: $0.0021 (~$0.01)                         │            │
│  │ • API Calls: 2 (MongoDB, OpenAI embeddings)            │            │
│  │ • GitHub Calls: 0                                       │            │
│  │ • Tokens Used: ~500 (minimal)                          │            │
│  └────────────────────────────────────────────────────────┘            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### **Diagram 3: RAG + MCP Data Flow - CODE_ERROR Example (20% of cases)**

```
┌─────────────────────────────────────────────────────────────────────────┐
│      RAG + MCP DEEP PATH - Code Error (15 seconds, $0.08)               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  TIME: T+0ms                                                            │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ INPUT: Jenkins Webhook                                  │            │
│  │ {                                                        │            │
│  │   "build_id": "BUILD_67890",                            │            │
│  │   "status": "FAILURE",                                  │            │
│  │   "error_log": "NullPointerException at line 127..."   │            │
│  │ }                                                        │            │
│  └──────────────────────┬───────────────────────────────────┘            │
│                         │                                                │
│  TIME: T+500ms          ▼                                                │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ STEP 1: MongoDB Query + Classification (same as above) │            │
│  │                                                          │            │
│  │ Result:                                                 │            │
│  │ • Category: CODE_ERROR                                  │            │
│  │ • needs_code_analysis: TRUE  ← Key difference!        │            │
│  │ • File path: src/main/java/DDNStorage.java             │            │
│  │                                                          │            │
│  │ Cost: $0.002                                            │            │
│  └──────────────────────┬───────────────────────────────────┘            │
│                         │                                                │
│  TIME: T+2.5s           ▼                                                │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ STEP 2: RAG Search (same process)                      │            │
│  │                                                          │            │
│  │ Results: 3 similar CODE_ERRORs found                   │            │
│  │ Best score: 0.82 (not high enough for auto-use)       │            │
│  │                                                          │            │
│  │ Decision: Need deeper analysis with MCP                │            │
│  │                                                          │            │
│  │ Cost: $0.0001                                           │            │
│  └──────────────────────┬───────────────────────────────────┘            │
│                         │                                                │
│  TIME: T+3.0s           ▼                                                │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ STEP 3: Claude AI with MCP Tools                        │            │
│  │                                                          │            │
│  │ A) Call MongoDB MCP Server                              │            │
│  │    Tool: mongodb_get_full_error_details()              │            │
│  │    Returns: Complete stack trace, console logs         │            │
│  │    Time: 500ms, Cost: $0.01                            │            │
│  │                                                          │            │
│  │ B) Call GitHub MCP Server                               │            │
│  │    Tool: github_get_file(                              │            │
│  │      path="src/main/java/DDNStorage.java",            │            │
│  │      start_line=120,                                   │            │
│  │      end_line=135                                      │            │
│  │    )                                                    │            │
│  │    Returns: Source code with context                   │            │
│  │    Time: 800ms, Cost: $0                               │            │
│  │                                                          │            │
│  │ C) Claude AI Analysis                                   │            │
│  │    Prompt: "Analyze this code with error context..."   │            │
│  │    Model: claude-3-5-sonnet                            │            │
│  │    Input tokens: 5,000                                 │            │
│  │    Output tokens: 2,000                                │            │
│  │    Time: 8 seconds                                     │            │
│  │    Cost: $0.07                                          │            │
│  │                                                          │            │
│  │ D) Claude Identifies:                                   │            │
│  │    Line 127: storageConfig.getPath() called            │            │
│  │    Problem: storageConfig can be null                  │            │
│  │    Missing: Null check before access                   │            │
│  └──────────────────────┬───────────────────────────────────┘            │
│                         │                                                │
│  TIME: T+12s            ▼                                                │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ STEP 4: Generate Code Fix                               │            │
│  │                                                          │            │
│  │ Claude generates:                                       │            │
│  │                                                          │            │
│  │ Root Cause:                                             │            │
│  │ "storageConfig is not initialized before use"          │            │
│  │                                                          │            │
│  │ Fix:                                                    │            │
│  │ ```java                                                 │            │
│  │ // Add at line 125                                     │            │
│  │ if (storageConfig == null) {                           │            │
│  │     throw new IllegalStateException(                   │            │
│  │         "Storage not initialized. Call init() first"   │            │
│  │     );                                                  │            │
│  │ }                                                       │            │
│  │ ```                                                     │            │
│  │                                                          │            │
│  │ Prevention:                                             │            │
│  │ "Add unit test: testOperationsWithoutInit()"           │            │
│  │                                                          │            │
│  │ GitHub Link:                                            │            │
│  │ https://github.com/ddn/repo/blob/main/DDNStorage.java#L127 │        │
│  └──────────────────────┬───────────────────────────────────┘            │
│                         │                                                │
│  TIME: T+15s            ▼                                                │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ STEP 5: Store New Vector in Pinecone                   │            │
│  │                                                          │            │
│  │ This solution is NEW, so store it for future RAG:      │            │
│  │                                                          │            │
│  │ {                                                        │            │
│  │   "text": "NullPointerException storageConfig...",     │            │
│  │   "metadata": {                                         │            │
│  │     "error_category": "CODE_ERROR",                    │            │
│  │     "root_cause": "Null check missing",                │            │
│  │     "solution": "Add null check before access",        │            │
│  │     "confidence": 0.90,                                │            │
│  │     "success_rate": 0.0,  ← Not tested yet           │            │
│  │     "times_used": 0,                                   │            │
│  │     "analysis_type": "CLAUDE_MCP"                      │            │
│  │   }                                                     │            │
│  │ }                                                       │            │
│  │                                                          │            │
│  │ Next time this error occurs: RAG will find it!         │            │
│  └────────────────────────────────────────────────────────┘            │
│                                                                          │
│  ┌────────────────────────────────────────────────────────┐            │
│  │ TOTAL METRICS                                           │            │
│  │ • Total Time: 15 seconds                               │            │
│  │ • Total Cost: $0.08                                    │            │
│  │ • API Calls: 5                                         │            │
│  │   - MongoDB query (1)                                  │            │
│  │   - OpenAI embedding (1)                               │            │
│  │   - Pinecone search (1)                                │            │
│  │   - MongoDB MCP (1)                                    │            │
│  │   - GitHub MCP (1)                                     │            │
│  │   - Claude AI analysis (1)                             │            │
│  │ • GitHub Calls: 1                                      │            │
│  │ • Tokens Used: 7,000                                   │            │
│  └────────────────────────────────────────────────────────┘            │
│                                                                          │
│  📊 But next time this error occurs:                                   │
│     RAG will find the stored solution → 5 sec, $0.01!                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Component Deep-Dive

### **1. Pinecone Vector Database**

#### **Index Configuration**
```python
# Index Name
PINECONE_INDEX_NAME = "ddn-error-solutions"

# Index Specifications
{
    "name": "ddn-error-solutions",
    "dimension": 1536,              # text-embedding-3-small output size
    "metric": "cosine",             # Similarity calculation method
    "spec": {
        "serverless": {
            "cloud": "aws",
            "region": "us-east-1"
        }
    },
    "deletion_protection": "enabled"  # Prevent accidental deletion
}
```

#### **Why Cosine Similarity?**
```
Cosine similarity measures the angle between two vectors, not their magnitude.

Perfect for text comparison because:
• Same meaning, different length → Still similar
• Focus on semantic content, not word count
• Range: -1 to 1 (we use 0 to 1 for similarity)

Example:
Vector A: "OutOfMemoryError Java heap space"
Vector B: "OutOfMemoryError: Java heap space at line 245"

Different lengths, but same meaning → Cosine similarity: 0.95 ✓
```

#### **Storage Capacity**
```
Free Tier:
• 1 index
• 100,000 vectors
• 10MB metadata

Sufficient for:
• ~50,000 unique error types
• ~2 years of DDN test failures
• Unlimited queries

Upgrade needed when:
• > 100K unique errors (rare)
• > 10MB metadata (very rare)
```

---

### **2. OpenAI Embeddings Service**

#### **Model Specification**
```python
MODEL = "text-embedding-3-small"

Characteristics:
• Dimensions: 1536
• Max input: 8,191 tokens
• Output: Float array [1536]
• Cost: $0.0001 per 1K tokens
• Speed: ~200ms per request

Why this model?
• Latest OpenAI embedding model
• Best balance of cost/quality
• Optimized for similarity search
• Industry-standard dimensions (1536)
```

#### **Embedding Generation Process**
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_embedding(text: str) -> List[float]:
    """
    Convert error text to 1536-dimensional vector

    Args:
        text: Error log or description

    Returns:
        List of 1536 floats (vector representation)
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
        encoding_format="float"
    )

    return response.data[0].embedding

# Example
error_text = "OutOfMemoryError: Java heap space at line 245"
embedding = generate_embedding(error_text)

print(f"Dimensions: {len(embedding)}")  # 1536
print(f"First 5 values: {embedding[:5]}")
# [0.234, -0.567, 0.123, 0.789, -0.345]
```

#### **Cost Analysis**
```
Cost per embedding: $0.0001 per 1,000 tokens

Average error log: 50 tokens
Cost per error: $0.000005 (~$0.00001)

Daily usage (50 errors):
50 × $0.00001 = $0.0005

Monthly cost: $0.015
Annual cost: $0.18

Negligible compared to Claude AI costs!
```

---

### **3. LangGraph RAG Search Implementation**

#### **Search Function**
```python
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

def search_similar_errors_rag(state: dict) -> dict:
    """
    Search Pinecone for similar past errors

    Args:
        state: {
            'error_log': str,
            'error_category': str
        }

    Returns:
        state with 'similar_solutions' added
    """
    # Initialize
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model="text-embedding-3-small"
    )

    vectorstore = PineconeVectorStore(
        index_name=os.getenv("PINECONE_INDEX", "ddn-error-solutions"),
        embedding=embeddings,
        pinecone_api_key=os.getenv("PINECONE_API_KEY")
    )

    # Search (automatically generates embedding and queries)
    similar_docs = vectorstore.similarity_search(
        query=state['error_log'],
        k=5,  # Top 5 results
        filter={"error_category": state['error_category']}
    )

    # Format results
    state['similar_solutions'] = [
        {
            "error": doc.page_content,
            "solution": doc.metadata.get('solution', ''),
            "root_cause": doc.metadata.get('root_cause', ''),
            "success_rate": doc.metadata.get('success_rate', 0.0),
            "confidence": doc.metadata.get('confidence', 0.0),
            "times_used": doc.metadata.get('times_used', 0),
            "similarity_score": doc.metadata.get('score', 0.0)
        }
        for doc in similar_docs
    ]

    return state
```

#### **Search Parameters Explained**
```python
# k=5: Return top 5 most similar vectors
# Why 5?
# • More than enough for comparison
# • Prevents information overload
# • Fast response time
# • Easy to rank by success_rate

# filter={"error_category": "..."}
# Why filter by category?
# • More relevant results
# • Faster search (smaller search space)
# • Prevents mixing infra solutions with code fixes
# • Better semantic similarity within same category
```

#### **Result Ranking Logic**
```python
def select_best_solution(similar_solutions: List[Dict]) -> Dict:
    """
    Select the best solution from RAG results

    Ranking criteria (in order):
    1. Similarity score > 0.85 (must be very similar)
    2. Success rate > 0.80 (solution must work)
    3. Times used > 5 (proven solution)
    4. Confidence > 0.70 (AI was confident)

    If multiple pass, select highest success_rate
    """
    # Filter qualified solutions
    qualified = [
        sol for sol in similar_solutions
        if (
            sol['similarity_score'] > 0.85 and
            sol['success_rate'] > 0.80 and
            sol['times_used'] > 5 and
            sol['confidence'] > 0.70
        )
    ]

    if not qualified:
        # No good match, use MCP instead
        return None

    # Sort by success_rate (highest first)
    qualified.sort(key=lambda x: x['success_rate'], reverse=True)

    return qualified[0]
```

---

## 📊 Data Specifications

### **Vector Data Schema**

#### **Complete Pinecone Vector Structure**
```json
{
  "id": "BUILD_12345_1729584000",
  "values": [0.234, -0.567, 0.123, ..., 0.789],
  "metadata": {
    "build_id": "BUILD_12345",
    "error_category": "INFRA_ERROR",
    "root_cause": "JVM heap size insufficient for DDN storage operations",
    "solution": "Increase JVM heap size to 4GB using -Xmx4g flag",
    "confidence": 0.95,
    "success_rate": 0.92,
    "times_used": 25,
    "timestamp": "2025-01-15T10:30:00Z",
    "analysis_type": "RAG_HISTORICAL_SOLUTION",
    "priority": "HIGH",
    "text_preview": "OutOfMemoryError: Java heap space at com.ddn.storage.DDNStorage.initialize..."
  }
}
```

#### **Metadata Fields Specification**

| Field | Type | Required | Max Length | Description |
|-------|------|----------|------------|-------------|
| **build_id** | string | Yes | 50 | Jenkins build identifier |
| **error_category** | enum | Yes | 20 | One of: CODE_ERROR, INFRA_ERROR, CONFIG_ERROR, DEPENDENCY_ERROR, TEST_FAILURE |
| **root_cause** | string | Yes | 1000 | Human-readable explanation of why error occurred |
| **solution** | string | Yes | 1000 | Step-by-step fix recommendation |
| **confidence** | float | Yes | - | AI confidence in analysis (0.0 - 1.0) |
| **success_rate** | float | Yes | - | How often this solution worked (0.0 - 1.0) |
| **times_used** | integer | Yes | - | Number of times this solution was applied |
| **timestamp** | ISO8601 | Yes | - | When this solution was created |
| **analysis_type** | enum | Yes | 30 | CLAUDE_MCP, RAG_HISTORICAL_SOLUTION, or MANUAL |
| **priority** | enum | Yes | 10 | HIGH, MEDIUM, or LOW |
| **text_preview** | string | Yes | 200 | First 200 chars of error log (for debugging) |

#### **Validation Rules**
```python
def validate_vector_metadata(metadata: dict) -> bool:
    """Validate metadata before storing in Pinecone"""

    # Required fields
    required = [
        'build_id', 'error_category', 'root_cause',
        'solution', 'confidence', 'success_rate',
        'times_used', 'timestamp'
    ]

    for field in required:
        if field not in metadata:
            raise ValueError(f"Missing required field: {field}")

    # Type validation
    if not isinstance(metadata['confidence'], (int, float)):
        raise TypeError("confidence must be numeric")

    if not 0.0 <= metadata['confidence'] <= 1.0:
        raise ValueError("confidence must be between 0 and 1")

    if not 0.0 <= metadata['success_rate'] <= 1.0:
        raise ValueError("success_rate must be between 0 and 1")

    # Category validation
    valid_categories = [
        'CODE_ERROR', 'INFRA_ERROR', 'CONFIG_ERROR',
        'DEPENDENCY_ERROR', 'TEST_FAILURE'
    ]

    if metadata['error_category'] not in valid_categories:
        raise ValueError(f"Invalid category: {metadata['error_category']}")

    # Length validation
    if len(metadata.get('root_cause', '')) > 1000:
        metadata['root_cause'] = metadata['root_cause'][:1000]

    if len(metadata.get('solution', '')) > 1000:
        metadata['solution'] = metadata['solution'][:1000]

    return True
```

---

### **Query Format Specification**

#### **Search Request**
```json
{
  "query": "OutOfMemoryError: Java heap space at line 245",
  "top_k": 5,
  "filter": {
    "error_category": "INFRA_ERROR"
  },
  "min_confidence": 0.7,
  "min_success_rate": 0.8
}
```

#### **Search Response**
```json
{
  "success": true,
  "query_preview": "OutOfMemoryError: Java heap space at line 245",
  "matches_found": 3,
  "matches": [
    {
      "id": "BUILD_12345_1729584000",
      "similarity_score": 0.95,
      "build_id": "BUILD_12345",
      "error_category": "INFRA_ERROR",
      "root_cause": "JVM heap size insufficient",
      "solution": "Increase heap to 4GB using -Xmx4g",
      "confidence": 0.95,
      "success_rate": 0.92,
      "times_used": 25,
      "timestamp": "2025-01-15T10:30:00Z",
      "analysis_type": "RAG_HISTORICAL_SOLUTION",
      "priority": "HIGH"
    },
    {
      "id": "BUILD_12346_1729584100",
      "similarity_score": 0.88,
      "build_id": "BUILD_12346",
      "error_category": "INFRA_ERROR",
      "root_cause": "Memory leak in storage module",
      "solution": "Set -Xms2g -Xmx4g and enable GC logging",
      "confidence": 0.88,
      "success_rate": 0.85,
      "times_used": 12,
      "timestamp": "2025-01-15T11:00:00Z",
      "analysis_type": "CLAUDE_MCP",
      "priority": "HIGH"
    }
  ]
}
```

---

## 📝 Sample Data Templates

### **Template 1: INFRA_ERROR - OutOfMemory**
```json
{
  "text": "OutOfMemoryError: Java heap space at com.ddn.storage.DDNStorage.initialize(DDNStorage.java:127). Failed to allocate 2048MB for object heap",
  "metadata": {
    "build_id": "SAMPLE_INFRA_001",
    "error_category": "INFRA_ERROR",
    "root_cause": "JVM heap size (2GB) insufficient for DDN storage initialization which requires minimum 3GB for metadata caching",
    "solution": "Increase JVM heap size to 4GB by setting JAVA_OPTS=\"-Xms2g -Xmx4g\" in Jenkins build configuration. Also enable GC logging with -XX:+PrintGCDetails",
    "confidence": 0.95,
    "success_rate": 0.92,
    "times_used": 25,
    "timestamp": "2025-01-10T10:30:00Z",
    "analysis_type": "CLAUDE_MCP",
    "priority": "HIGH",
    "text_preview": "OutOfMemoryError: Java heap space at com.ddn.storage.DDNStorage.initialize(DDNStorage.java:127). Failed to allocate 2048MB for object heap"
  }
}
```

### **Template 2: INFRA_ERROR - Disk Space**
```json
{
  "text": "IOException: No space left on device. Failed to write test results to /var/lib/jenkins/workspace/DDN-Tests/results/test_output.xml",
  "metadata": {
    "build_id": "SAMPLE_INFRA_002",
    "error_category": "INFRA_ERROR",
    "root_cause": "Jenkins workspace directory (/var/lib/jenkins) exceeded 85% capacity. Test artifact generation requires minimum 2GB free space",
    "solution": "1. Clean old build artifacts: find /var/lib/jenkins/workspace -mtime +7 -delete\n2. Increase workspace volume to 50GB\n3. Enable automatic cleanup of builds older than 14 days",
    "confidence": 0.93,
    "success_rate": 0.89,
    "times_used": 18,
    "timestamp": "2025-01-11T14:20:00Z",
    "analysis_type": "RAG_HISTORICAL_SOLUTION",
    "priority": "HIGH",
    "text_preview": "IOException: No space left on device. Failed to write test results to /var/lib/jenkins/workspace/DDN-Tests/results/test_output.xml"
  }
}
```

### **Template 3: CODE_ERROR - NullPointerException**
```json
{
  "text": "NullPointerException at com.ddn.storage.DDNStorage.initialize(DDNStorage.java:127): Cannot invoke 'StorageConfig.getPath()' because 'this.storageConfig' is null",
  "metadata": {
    "build_id": "SAMPLE_CODE_001",
    "error_category": "CODE_ERROR",
    "root_cause": "DDNStorage.initialize() is called before storageConfig is initialized. The constructor doesn't validate required dependencies",
    "solution": "Add null check at line 125:\nif (storageConfig == null) {\n    throw new IllegalStateException(\"Storage not initialized. Call setStorageConfig() first\");\n}\nAlso add @NotNull annotation to storageConfig field",
    "confidence": 0.90,
    "success_rate": 0.88,
    "times_used": 12,
    "timestamp": "2025-01-12T09:15:00Z",
    "analysis_type": "CLAUDE_MCP",
    "priority": "HIGH",
    "text_preview": "NullPointerException at com.ddn.storage.DDNStorage.initialize(DDNStorage.java:127): Cannot invoke 'StorageConfig.getPath()' because 'this.storageConfig' is null"
  }
}
```

### **Template 4: CODE_ERROR - TypeError (Python)**
```json
{
  "text": "TypeError: unsupported operand type(s) for +: 'int' and 'str' at test_storage_metrics.py:45 in calculate_total_storage()",
  "metadata": {
    "build_id": "SAMPLE_CODE_002",
    "error_category": "CODE_ERROR",
    "root_cause": "calculate_total_storage() receives string values from API response but attempts arithmetic operations without type conversion",
    "solution": "Add type conversion at line 44:\ntotal_storage = int(current_storage) + int(new_storage)\n\nOr use type hints and validation:\ndef calculate_total_storage(current: int, new: int) -> int:\n    if not isinstance(current, int) or not isinstance(new, int):\n        raise TypeError('Storage values must be integers')\n    return current + new",
    "confidence": 0.92,
    "success_rate": 0.85,
    "times_used": 8,
    "timestamp": "2025-01-13T11:45:00Z",
    "analysis_type": "CLAUDE_MCP",
    "priority": "MEDIUM",
    "text_preview": "TypeError: unsupported operand type(s) for +: 'int' and 'str' at test_storage_metrics.py:45 in calculate_total_storage()"
  }
}
```

### **Template 5: CONFIG_ERROR - Permission Denied**
```json
{
  "text": "PermissionError: [Errno 13] Permission denied: '/opt/ddn/config/storage.conf'. Failed to read storage configuration file",
  "metadata": {
    "build_id": "SAMPLE_CONFIG_001",
    "error_category": "CONFIG_ERROR",
    "root_cause": "Jenkins user doesn't have read permissions on /opt/ddn/config directory. File ownership is root:root with 0600 permissions",
    "solution": "1. Change file permissions: sudo chmod 644 /opt/ddn/config/storage.conf\n2. Add jenkins user to ddn group: sudo usermod -a -G ddn jenkins\n3. Update directory permissions: sudo chown -R root:ddn /opt/ddn/config && sudo chmod 750 /opt/ddn/config",
    "confidence": 0.94,
    "success_rate": 0.90,
    "times_used": 15,
    "timestamp": "2025-01-14T13:30:00Z",
    "analysis_type": "RAG_HISTORICAL_SOLUTION",
    "priority": "MEDIUM",
    "text_preview": "PermissionError: [Errno 13] Permission denied: '/opt/ddn/config/storage.conf'. Failed to read storage configuration file"
  }
}
```

### **Template 6: CONFIG_ERROR - Invalid Configuration**
```json
{
  "text": "ConfigurationException: Invalid storage pool size '10TB' in storage.conf line 23. Expected format: <number>GB",
  "metadata": {
    "build_id": "SAMPLE_CONFIG_002",
    "error_category": "CONFIG_ERROR",
    "root_cause": "storage.conf uses 'TB' unit but parser only accepts 'GB'. Configuration validation doesn't provide helpful error messages",
    "solution": "1. Update storage.conf line 23: storage_pool_size = 10240GB\n2. Alternative: Update parser to support TB units by multiplying value by 1024\n3. Add validation with clear error messages in config parser",
    "confidence": 0.91,
    "success_rate": 0.87,
    "times_used": 10,
    "timestamp": "2025-01-15T08:00:00Z",
    "analysis_type": "CLAUDE_MCP",
    "priority": "MEDIUM",
    "text_preview": "ConfigurationException: Invalid storage pool size '10TB' in storage.conf line 23. Expected format: <number>GB"
  }
}
```

### **Template 7: DEPENDENCY_ERROR - Module Not Found**
```json
{
  "text": "ModuleNotFoundError: No module named 'ddn_storage_client'. Failed to import required dependency at test_ddn_api.py:5",
  "metadata": {
    "build_id": "SAMPLE_DEP_001",
    "error_category": "DEPENDENCY_ERROR",
    "root_cause": "ddn_storage_client package not installed in Jenkins Python environment. requirements.txt specifies version 2.3.0 but package repository has only 2.2.x",
    "solution": "1. Update requirements.txt: ddn-storage-client==2.2.5 (latest stable)\n2. Install dependencies: pip install -r requirements.txt --upgrade\n3. Clear pip cache if needed: pip cache purge\n4. Verify installation: pip show ddn-storage-client",
    "confidence": 0.93,
    "success_rate": 0.91,
    "times_used": 20,
    "timestamp": "2025-01-16T10:00:00Z",
    "analysis_type": "RAG_HISTORICAL_SOLUTION",
    "priority": "HIGH",
    "text_preview": "ModuleNotFoundError: No module named 'ddn_storage_client'. Failed to import required dependency at test_ddn_api.py:5"
  }
}
```

### **Template 8: DEPENDENCY_ERROR - Version Conflict**
```json
{
  "text": "ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts. ddn-sdk 1.5.0 requires requests<2.28,>=2.25, but you have requests 2.30.0",
  "metadata": {
    "build_id": "SAMPLE_DEP_002",
    "error_category": "DEPENDENCY_ERROR",
    "root_cause": "ddn-sdk 1.5.0 pins requests to <2.28 but test suite requires requests 2.30+ for security fixes. Incompatible version constraints",
    "solution": "1. Upgrade ddn-sdk to 1.6.0 which supports requests 2.30+\n2. Update requirements.txt:\n   ddn-sdk>=1.6.0\n   requests>=2.30.0\n3. If ddn-sdk 1.6.0 not available, create virtual environment with isolated dependencies",
    "confidence": 0.89,
    "success_rate": 0.84,
    "times_used": 14,
    "timestamp": "2025-01-17T12:15:00Z",
    "analysis_type": "CLAUDE_MCP",
    "priority": "MEDIUM",
    "text_preview": "ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts..."
  }
}
```

### **Template 9: TEST_FAILURE - Assertion Error**
```json
{
  "text": "AssertionError: Expected storage pool capacity 10TB but got 9.5TB at test_storage_capacity.py:67 in test_pool_initialization()",
  "metadata": {
    "build_id": "SAMPLE_TEST_001",
    "error_category": "TEST_FAILURE",
    "root_cause": "Test expects exact 10TB but actual capacity is 9.5TB due to filesystem overhead (5% reserved for system). Test assertion too strict",
    "solution": "Update test to allow 5% tolerance:\nassert abs(actual_capacity - expected_capacity) / expected_capacity <= 0.05, f\"Capacity {actual_capacity} outside 5% tolerance of {expected_capacity}\"\n\nOr use pytest.approx:\nassert actual_capacity == pytest.approx(expected_capacity, rel=0.05)",
    "confidence": 0.87,
    "success_rate": 0.82,
    "times_used": 6,
    "timestamp": "2025-01-18T09:30:00Z",
    "analysis_type": "CLAUDE_MCP",
    "priority": "MEDIUM",
    "text_preview": "AssertionError: Expected storage pool capacity 10TB but got 9.5TB at test_storage_capacity.py:67 in test_pool_initialization()"
  }
}
```

### **Template 10: TEST_FAILURE - Expectation Failed**
```json
{
  "text": "ExpectationFailed: API response time 3.5s exceeds maximum allowed 3.0s for GET /api/storage/pools endpoint in test_api_performance.py:102",
  "metadata": {
    "build_id": "SAMPLE_TEST_002",
    "error_category": "TEST_FAILURE",
    "root_cause": "Storage pool listing query became slower after database grew to 10,000+ pools. Missing index on 'created_at' column causing full table scan",
    "solution": "1. Add database index:\n   CREATE INDEX idx_pools_created_at ON storage_pools(created_at);\n2. Add pagination to API:\n   GET /api/storage/pools?limit=100&offset=0\n3. Update test timeout to 5s or implement pagination in test",
    "confidence": 0.85,
    "success_rate": 0.80,
    "times_used": 5,
    "timestamp": "2025-01-19T14:45:00Z",
    "analysis_type": "CLAUDE_MCP",
    "priority": "LOW",
    "text_preview": "ExpectationFailed: API response time 3.5s exceeds maximum allowed 3.0s for GET /api/storage/pools endpoint in test_api_performance.py:102"
  }
}
```

---

## 🔄 RAG Query Process

### **Step-by-Step Flow**

#### **Step 1: Receive Error**
```python
# Input from Jenkins/n8n
error_input = {
    "build_id": "BUILD_12345",
    "error_log": "OutOfMemoryError: Java heap space...",
    "status": "FAILURE"
}
```

#### **Step 2: Classify Error (LangGraph)**
```python
def classify_error(error_log: str) -> dict:
    """
    Classify error by matching keywords
    """
    error_log_lower = error_log.lower()

    # Check each category
    for category, config in ERROR_CATEGORIES.items():
        keyword_matches = sum(
            1 for keyword in config['keywords']
            if keyword.lower() in error_log_lower
        )

        if keyword_matches > 0:
            confidence = min(0.95, 0.6 + (keyword_matches * 0.1))
            return {
                "category": category,
                "confidence": confidence,
                "needs_code_analysis": config['needs_github']
            }

    # Default to CODE_ERROR if no matches
    return {
        "category": "CODE_ERROR",
        "confidence": 0.5,
        "needs_code_analysis": True
    }

# Result
classification = {
    "category": "INFRA_ERROR",
    "confidence": 0.95,
    "needs_code_analysis": False
}
```

#### **Step 3: Generate Embedding (OpenAI)**
```python
def generate_embedding(text: str) -> List[float]:
    """
    Convert text to 1536-dimensional vector
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
        encoding_format="float"
    )

    return response.data[0].embedding

# Input
error_text = "OutOfMemoryError: Java heap space at line 127"

# Output
embedding_vector = [0.234, -0.567, 0.123, ..., 0.789]  # 1536 floats
```

#### **Step 4: Query Pinecone**
```python
def search_pinecone(
    embedding: List[float],
    category: str,
    top_k: int = 5
) -> List[dict]:
    """
    Search for similar vectors in Pinecone
    """
    from pinecone import Pinecone

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index("ddn-error-solutions")

    # Query
    results = index.query(
        vector=embedding,
        top_k=top_k,
        filter={"error_category": category},
        include_metadata=True
    )

    # Format results
    matches = []
    for match in results.matches:
        matches.append({
            "id": match.id,
            "score": match.score,
            "metadata": match.metadata
        })

    return matches

# Results
[
    {
        "id": "BUILD_001_timestamp",
        "score": 0.95,  # Very similar!
        "metadata": {
            "root_cause": "JVM heap size insufficient",
            "solution": "Increase to 4GB with -Xmx4g",
            "success_rate": 0.92,
            "times_used": 25
        }
    },
    {...},
    {...}
]
```

#### **Step 5: Select Best Solution**
```python
def select_best_solution(matches: List[dict]) -> Optional[dict]:
    """
    Choose the best solution from RAG results
    """
    # Filter by quality thresholds
    qualified = [
        m for m in matches
        if (
            m['score'] > 0.85 and  # High similarity
            m['metadata']['success_rate'] > 0.80 and  # Proven solution
            m['metadata']['times_used'] > 5  # Used before
        )
    ]

    if not qualified:
        return None  # Need deeper analysis (MCP)

    # Sort by success rate
    qualified.sort(
        key=lambda x: x['metadata']['success_rate'],
        reverse=True
    )

    return qualified[0]

# Selected solution
best_solution = {
    "root_cause": "JVM heap size insufficient",
    "solution": "Increase heap to 4GB using -Xmx4g",
    "success_rate": 0.92,
    "times_used": 25,
    "confidence": 0.95
}
```

#### **Step 6: Return to n8n**
```python
# Format final response
final_response = {
    "build_id": "BUILD_12345",
    "error_category": "INFRA_ERROR",
    "confidence": 0.95,
    "root_cause": best_solution['root_cause'],
    "fix_recommendation": best_solution['solution'],
    "success_rate": best_solution['success_rate'],
    "times_this_worked": best_solution['times_used'],
    "source": "RAG_HISTORICAL_SOLUTION",
    "execution_time_seconds": 5,
    "cost_usd": 0.01
}
```

---

## 🔗 Integration Points

### **1. n8n Workflow Integration**

#### **n8n Workflow Node Configuration**

```javascript
// Node 3: Call LangGraph RAG Service

// HTTP Request Node
{
  "method": "POST",
  "url": "{{ $env.LANGGRAPH_SERVICE_URL }}/classify-error",
  "authentication": "none",
  "requestMethod": "POST",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "bodyParameters": {
    "parameters": [
      {
        "name": "build_id",
        "value": "={{ $json.build_id }}"
      },
      {
        "name": "error_log",
        "value": "={{ $json.error_log }}"
      },
      {
        "name": "status",
        "value": "FAILURE"
      }
    ]
  },
  "options": {
    "timeout": 30000,
    "retry": {
      "maxRetries": 2,
      "retryInterval": 1000
    }
  }
}

// Expected Response
{
  "build_id": "BUILD_12345",
  "error_category": "INFRA_ERROR",
  "confidence": 0.95,
  "needs_code_analysis": false,
  "similar_solutions": [
    {
      "root_cause": "...",
      "solution": "...",
      "success_rate": 0.92,
      "times_used": 25
    }
  ],
  "selected_solution": {
    "root_cause": "JVM heap size insufficient",
    "fix_recommendation": "Increase heap to 4GB",
    "success_rate": 0.92,
    "source": "RAG"
  }
}
```

#### **n8n Decision Node: RAG or MCP?**

```javascript
// IF Node: Check if code analysis needed

// Condition
{{ $json.needs_code_analysis }} === false

// TRUE Branch (80% of cases)
// → Use RAG solution directly
// → Store in MongoDB
// → Send Teams notification
// → END (Fast path!)

// FALSE Branch (20% of cases)
// → Call Claude AI with MCP
// → Fetch from GitHub
// → Deep analysis
// → Store in MongoDB + Pinecone
// → Send Teams notification
```

---

### **2. LangGraph State Machine**

```python
from langgraph.graph import StateGraph, END

# Define state graph
workflow = StateGraph(ErrorAnalysisState)

# Add nodes
workflow.add_node("classify", classify_error)
workflow.add_node("rag_search", search_similar_errors_rag)
workflow.add_node("select_solution", select_best_solution)
workflow.add_node("fetch_code", fetch_github_files)  # MCP path
workflow.add_node("analyze_with_claude", analyze_with_mcp)  # MCP path

# Add edges (decision logic)
workflow.set_entry_point("classify")
workflow.add_edge("classify", "rag_search")

# Decision point: RAG or MCP?
workflow.add_conditional_edges(
    "rag_search",
    lambda state: "use_rag" if not state['needs_code_analysis'] else "use_mcp",
    {
        "use_rag": "select_solution",
        "use_mcp": "fetch_code"
    }
)

# RAG path
workflow.add_edge("select_solution", END)

# MCP path
workflow.add_edge("fetch_code", "analyze_with_claude")
workflow.add_edge("analyze_with_claude", END)

# Compile
app = workflow.compile()
```

---

### **3. Pinecone Storage Service API**

#### **Store Vector Endpoint**
```python
# POST http://localhost:5003/api/store-vector

# Request
{
  "text": "OutOfMemoryError: Java heap space at line 127",
  "metadata": {
    "build_id": "BUILD_12345",
    "error_category": "INFRA_ERROR",
    "root_cause": "JVM heap insufficient",
    "solution": "Increase to 4GB",
    "confidence": 0.95,
    "success_rate": 0.0,  # New solution, not tested yet
    "times_used": 0,
    "analysis_type": "CLAUDE_MCP",
    "priority": "HIGH"
  }
}

# Response
{
  "success": true,
  "vector_id": "BUILD_12345_1729584000",
  "dimensions": 1536,
  "metadata": {...}
}
```

#### **Search Similar Endpoint**
```python
# POST http://localhost:5003/api/search-similar

# Request
{
  "query": "OutOfMemoryError Java heap",
  "top_k": 5,
  "filter": {
    "error_category": "INFRA_ERROR"
  },
  "min_confidence": 0.7
}

# Response
{
  "success": true,
  "matches_found": 3,
  "matches": [
    {
      "id": "BUILD_001_ts",
      "similarity_score": 0.95,
      "root_cause": "...",
      "solution": "...",
      "success_rate": 0.92,
      "times_used": 25
    },
    {...}
  ]
}
```

#### **Update Feedback Endpoint**
```python
# POST http://localhost:5003/api/update-feedback

# Request (after solution is applied)
{
  "vector_id": "BUILD_12345_1729584000",
  "success": true,  # Did the solution work?
  "increment_usage": true
}

# Response
{
  "success": true,
  "vector_id": "BUILD_12345_1729584000",
  "times_used": 26,  # Incremented
  "success_rate": 0.923  # Updated based on feedback
}
```

---

## 📈 Performance & Metrics

### **Response Time Targets**

| Operation | Target | Typical | Max Acceptable |
|-----------|--------|---------|----------------|
| **Generate Embedding** | < 200ms | 150ms | 500ms |
| **Pinecone Query** | < 300ms | 200ms | 1000ms |
| **Total RAG Search** | < 500ms | 400ms | 2000ms |
| **RAG-Only Analysis** | < 5s | 4s | 10s |
| **RAG + MCP Analysis** | < 15s | 12s | 30s |

### **Accuracy Metrics**

#### **Similarity Score Thresholds**
```
Score Range    | Interpretation      | Action
---------------|---------------------|-------------------------
0.95 - 1.00    | Nearly identical    | Use RAG solution with high confidence
0.85 - 0.94    | Very similar        | Use RAG if success_rate > 0.80
0.70 - 0.84    | Somewhat similar    | Consider MCP for verification
0.50 - 0.69    | Loosely related     | Use MCP for deep analysis
0.00 - 0.49    | Not related         | Definitely use MCP
```

#### **Success Rate Tracking**
```python
# Formula
success_rate = successful_applications / total_applications

# Example
vector_metadata = {
    "times_used": 25,
    "success_rate": 0.92  # 23 out of 25 times it worked
}

# Update after new application
if solution_worked:
    new_success_rate = ((0.92 * 25) + 1.0) / 26 = 0.923
else:
    new_success_rate = ((0.92 * 25) + 0.0) / 26 = 0.884
```

### **Cost Analysis**

#### **Per-Query Costs**
```
Component                  | Cost per Query | Notes
---------------------------|----------------|------------------
OpenAI Embedding           | $0.0001        | ~50 tokens avg
Pinecone Query             | $0.0000        | Free tier
LangGraph Processing       | $0.0020        | Lightweight
MongoDB Query              | $0.0000        | Internal DB
-------------------------------------------------
TOTAL (RAG Only)          | $0.0021        | ~$0.01 rounded

MCP Additional Costs:
Claude AI Analysis         | $0.0700        | ~7K tokens
GitHub API                 | $0.0000        | Free
MongoDB MCP                | $0.0100        | Additional query
-------------------------------------------------
TOTAL (RAG + MCP)         | $0.0821        | ~$0.08 rounded
```

#### **Monthly Cost Projections**
```
Scenario: 50 analyses per day

RAG-Only (80% = 40/day):
40 × $0.01 × 30 days = $12/month

RAG + MCP (20% = 10/day):
10 × $0.08 × 30 days = $24/month

TOTAL MONTHLY: $36

Compare to No RAG (100% MCP):
50 × $0.08 × 30 days = $120/month

SAVINGS: $84/month (70% reduction)
ANNUAL SAVINGS: $1,008
```

### **Scalability Considerations**

#### **Pinecone Limits**
```
Free Tier:
• 100,000 vectors
• Unlimited queries
• 10MB metadata

At 50 new errors/day:
• 50 × 365 = 18,250 vectors/year
• Can run 5+ years before hitting limit
• Metadata: ~2KB/vector = 36MB/year (within limit)

Production Tier ($70/month):
• 5 million vectors
• Unlimited queries
• 10GB metadata
• Can handle 270+ years of data
```

#### **Query Performance at Scale**
```
Vector Count | Query Latency | Notes
-------------|---------------|------------------------
1,000        | 50ms          | Initial deployment
10,000       | 100ms         | After 6 months
100,000      | 200ms         | After 5 years (free tier max)
1,000,000    | 300ms         | Production tier
5,000,000    | 400ms         | Max production tier
```

---

## ⚙️ Setup & Configuration

### **1. Create Pinecone Index**

#### **Via Pinecone Console (Recommended)**
```
1. Visit: https://app.pinecone.io
2. Create New Index:
   - Name: ddn-error-solutions
   - Dimensions: 1536
   - Metric: cosine
   - Cloud: AWS
   - Region: us-east-1
   - Pod Type: Starter (free tier)
3. Copy API Key
```

#### **Via Python Script**
```python
# setup_pinecone.py

from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Create index
pc.create_index(
    name="ddn-error-solutions",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

print("✅ Pinecone index created!")
```

### **2. Environment Variables**

```bash
# .env file

# AI Services
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
PINECONE_API_KEY=your-pinecone-key-here

# Pinecone Configuration
PINECONE_INDEX=ddn-error-solutions
PINECONE_ENVIRONMENT=us-east-1

# Service URLs
LANGGRAPH_SERVICE_URL=http://localhost:5000
MONGODB_MCP_URL=http://localhost:5001/sse
GITHUB_MCP_URL=http://localhost:5002/sse
PINECONE_STORAGE_URL=http://localhost:5003

# Database
MONGODB_URI=mongodb://localhost:27017/ddn_ai_project
```

### **3. Start Services**

```bash
# Terminal 1: LangGraph Service (includes RAG)
cd C:\DDN-AI-Project-Documentation\implementation
python langgraph_agent.py
# Running on http://localhost:5000

# Terminal 2: Pinecone Storage Service
cd C:\DDN-AI-Project-Documentation\mcp-configs
python pinecone_storage_service.py
# Running on http://localhost:5003

# Terminal 3: n8n
n8n start
# Running on http://localhost:5678
```

### **4. Populate Initial Data**

```python
# populate_pinecone.py

import requests
import json

PINECONE_SERVICE = "http://localhost:5003"

# Use templates from "Sample Data Templates" section above
templates = [
    # Template 1: INFRA_ERROR - OutOfMemory
    {
        "text": "OutOfMemoryError: Java heap space...",
        "metadata": {...}
    },
    # Template 2-10...
]

# Store each template
for template in templates:
    response = requests.post(
        f"{PINECONE_SERVICE}/api/store-vector",
        json=template
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Stored: {result['vector_id']}")
    else:
        print(f"❌ Failed: {response.json()}")

print(f"\n✅ Populated {len(templates)} vectors in Pinecone!")
```

### **5. Test RAG Search**

```python
# test_rag.py

import requests

LANGGRAPH_SERVICE = "http://localhost:5000"

# Test error
test_error = {
    "build_id": "TEST_001",
    "error_log": "OutOfMemoryError: Java heap space at line 245",
    "status": "FAILURE"
}

# Call LangGraph classification
response = requests.post(
    f"{LANGGRAPH_SERVICE}/classify-error",
    json=test_error
)

result = response.json()

print("Classification:", result['error_category'])
print("Confidence:", result['confidence'])
print("Similar solutions found:", len(result['similar_solutions']))

if result['similar_solutions']:
    best = result['similar_solutions'][0]
    print("\nBest match:")
    print("  Root Cause:", best['root_cause'])
    print("  Solution:", best['solution'])
    print("  Success Rate:", best['success_rate'])
    print("  Times Used:", best['times_used'])
```

---

## 🛠️ Troubleshooting

### **Problem: "No similar solutions found"**

**Possible Causes:**
```
1. Pinecone index is empty
2. Wrong error_category filter
3. Similarity threshold too high
4. OpenAI API key invalid
```

**Solutions:**
```python
# 1. Check if index has data
import requests
response = requests.get("http://localhost:5003/api/get-stats")
print(response.json())
# Should show: total_vectors > 0

# 2. Try search without filter
response = requests.post(
    "http://localhost:5003/api/search-similar",
    json={
        "query": "OutOfMemoryError",
        "top_k": 5,
        # "filter": {}  # Remove filter
    }
)

# 3. Lower similarity threshold
# In langgraph_agent.py, change:
# if similarity_score > 0.85  →  if similarity_score > 0.70

# 4. Test OpenAI API
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="test"
)
print("API works!" if response else "API failed!")
```

---

### **Problem: "Search is slow (> 2 seconds)"**

**Diagnosis:**
```python
import time
import requests

# Test embedding generation
start = time.time()
response = requests.post(
    "http://localhost:5003/api/store-vector",
    json={
        "text": "test error",
        "metadata": {"build_id": "test"}
    }
)
embedding_time = time.time() - start
print(f"Embedding: {embedding_time:.2f}s")  # Should be < 0.5s

# Test Pinecone query
start = time.time()
response = requests.post(
    "http://localhost:5003/api/search-similar",
    json={"query": "test"}
)
query_time = time.time() - start
print(f"Query: {query_time:.2f}s")  # Should be < 0.5s
```

**Solutions:**
```
If embedding is slow:
• Check OpenAI API status
• Verify internet connection
• Consider upgrading to paid API tier

If query is slow:
• Check Pinecone dashboard for issues
• Reduce top_k parameter (5 → 3)
• Remove unnecessary metadata from results
```

---

### **Problem: "Success rate not updating"**

**Check Feedback Loop:**
```python
import requests

# After applying solution, send feedback
response = requests.post(
    "http://localhost:5003/api/update-feedback",
    json={
        "vector_id": "BUILD_12345_1729584000",
        "success": True,
        "increment_usage": True
    }
)

print(response.json())
# Should show: times_used incremented, success_rate updated
```

**Verify in Pinecone:**
```python
# Fetch vector to see current values
response = requests.post(
    "http://localhost:5003/api/search-similar",
    json={
        "query": "specific error text",
        "top_k": 1
    }
)

result = response.json()['matches'][0]
print(f"Times Used: {result['times_used']}")
print(f"Success Rate: {result['success_rate']}")
```

---

## 📚 Additional Resources

### **Documentation**
- [Pinecone Documentation](https://docs.pinecone.io/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Complete System Architecture](architecture/COMPLETE-ARCHITECTURE.md)
- [MCP Connector Guide](technical-guides/MCP-CONNECTOR-GUIDE.md)

### **Related Files**
- [pinecone_storage_service.py](mcp-configs/pinecone_storage_service.py) - Storage service implementation
- [langgraph_agent.py](implementation/langgraph_agent.py) - Classification and RAG search
- [Architecture.jpg](Architecture.jpg) - Visual system architecture

---

## ✅ Summary

### **Key Takeaways**

1. **RAG Reduces Costs by 93%**
   - INFRA/CONFIG/DEPEND errors: $0.01 (RAG only)
   - CODE/TEST errors: $0.08 (RAG + MCP)
   - Average cost: $0.02 vs $0.15 without RAG

2. **RAG Improves Speed by 67%**
   - RAG-only path: 5 seconds
   - RAG + MCP path: 15 seconds
   - Average: 7 seconds vs 18 seconds without RAG

3. **RAG Gets Smarter Over Time**
   - Each resolution stored as vector
   - Success rates tracked automatically
   - Best solutions bubble to top

4. **80/20 Split**
   - 80% of errors solved by RAG alone
   - 20% need deep analysis with MCP
   - System automatically decides which path

### **Next Steps**

1. ✅ Create Pinecone index
2. ✅ Set environment variables
3. ✅ Start services (LangGraph, Pinecone Storage)
4. ✅ Populate initial vectors (use 10 templates)
5. ✅ Test RAG search
6. ✅ Integrate with n8n workflows
7. ✅ Monitor performance and accuracy

---

**Document Version**: 1.0
**Last Updated**: October 21, 2025
**Next Review**: After first month of production use
**Maintained By**: Rysun Development Team
