# DDN AI PROJECT - QUICK REFERENCE GUIDE
## 1-Page Cheat Sheet for Daily Development

**Version:** 1.0 | **Date:** 2025-10-28

---

## 🎯 PROJECT GOAL
Transform 70% complete system → 95% production-ready with 8 enhancements
- ✅ Keep existing: 3 n8n workflows, LangGraph, Dashboard, MCP servers
- ➕ Add: Caching, Re-ranking, Hybrid Search, PII, Query Expansion, RAGAS, Celery, LangSmith

---

## 📁 FILES TO CREATE (13 New Files)

| # | File | Port | Purpose | Phase |
|---|------|------|---------|-------|
| 1 | `reranking_service.py` | 5004 | Re-rank Pinecone results | 2 |
| 2 | `hybrid_search_service.py` | 5005 | Dense + Sparse search | 3 |
| 3 | `build_bm25_index.py` | - | Build BM25 index | 3 |
| 4 | `security/pii_redaction.py` | - | Redact PII | 4 |
| 5 | `retrieval/query_expansion.py` | - | Expand queries | 5 |
| 6 | `evaluation/ragas_evaluation.py` | - | RAGAS metrics | 6 |
| 7 | `evaluation/test_set.json` | - | Test cases | 6 |
| 8 | `evaluation/run_evaluation.py` | - | Run eval | 6 |
| 9 | `tasks/celery_tasks.py` | - | Async tasks | 7 |
| 10 | `start_celery_workers.bat` | - | Workers | 7 |
| 11 | `agents/react_agent_service.py` | 5009 | ReAct agent | 9 |
| 12 | `docker-compose.yml` | - | Deploy | 10 |
| 13 | `.env.production` | - | Prod config | 10 |

---

## 🔧 FILES TO MODIFY (3 Files)

| File | Phases | Changes |
|------|--------|---------|
| `langgraph_agent.py` | 1,2,3,5,8 | Add caching, re-ranking, hybrid search, tracing |
| `mongodb_robot_listener.py` | 4 | Add PII redaction before storing |
| `ai_analysis_service.py` | 4,7 | Add PII redaction, Celery tasks |

---

## 🚀 ALL SERVICES & PORTS

| Port | Service | File | Status |
|------|---------|------|--------|
| 3000 | Dashboard UI | dashboard-ui/ | ✅ Existing |
| 5000 | LangGraph Agent | langgraph_agent.py | ✅ Existing |
| 5001 | MongoDB MCP | mcp_mongodb_server.py | ✅ Existing |
| 5002 | GitHub MCP | mcp_github_server.py | ✅ Existing |
| 5003 | Pinecone Service | pinecone_storage_service.py | ✅ Existing |
| 5004 | **Re-Ranking** | reranking_service.py | 🆕 Phase 2 |
| 5005 | **Hybrid Search** | hybrid_search_service.py | 🆕 Phase 3 |
| 5006 | Dashboard API | dashboard_api_full.py | ✅ Existing |
| 5007 | Jira Integration | jira_integration_service.py | ✅ Existing |
| 5008 | Self-Healing | self_healing_service.py | ✅ Existing |
| 5009 | **ReAct Agent** | react_agent_service.py | 🆕 Phase 9 |
| 6379 | Redis | Docker/Windows | 🆕 Phase 0 |

---

## 💻 ESSENTIAL COMMANDS

### **Start All Services (Copy-Paste)**
```bash
# Terminal 1: LangGraph
cd implementation && python langgraph_agent.py

# Terminal 2: Dashboard API
cd implementation && python dashboard_api_full.py

# Terminal 3: MCP MongoDB
cd mcp-configs && python mcp_mongodb_server.py

# Terminal 4: MCP GitHub
cd mcp-configs && python mcp_github_server.py

# Terminal 5: Re-Ranking (Phase 2+)
cd implementation && python reranking_service.py

# Terminal 6: Hybrid Search (Phase 3+)
cd implementation && python hybrid_search_service.py

# Terminal 7: Celery Workers (Phase 7+)
cd implementation && celery -A tasks.celery_tasks worker --loglevel=info
```

### **Quick Health Check**
```bash
curl http://localhost:5000/health  # LangGraph
curl http://localhost:5004/health  # Re-Ranking (Phase 2+)
curl http://localhost:5005/health  # Hybrid Search (Phase 3+)
redis-cli ping                     # Redis (should return PONG)
```

### **Test Classification**
```bash
curl -X POST http://localhost:5000/classify-error \
  -H "Content-Type: application/json" \
  -d '{"build_id":"TEST001","error_log":"TimeoutError after 30 seconds"}'
```

### **Check Cache Stats**
```bash
curl http://localhost:5000/cache-stats
redis-cli KEYS "analysis:*"
```

---

## 📊 VALIDATION CHECKLIST (After Each Phase)

**Phase 1 (Caching):**
```
[_] First call takes 3-5 seconds
[_] Second identical call returns instantly (<100ms)
[_] Response has "from_cache": true
[_] redis-cli KEYS shows cached entries
```

**Phase 2 (Re-Ranking):**
```
[_] Re-ranking service starts on port 5004
[_] LangGraph logs show "Re-ranking X candidates"
[_] Results include "rerank_score" field
[_] Top results have higher scores
```

**Phase 3 (Hybrid Search):**
```
[_] Hybrid search service on port 5005
[_] BM25 index built successfully
[_] Exact error codes (E500) found in top 3
[_] Semantic queries still work
```

**Phase 4 (PII Redaction):**
```
[_] Test log with email/IP stored
[_] MongoDB shows <EMAIL>, <IP> instead of real values
[_] No PII in Pinecone embeddings
```

**Phase 6 (RAGAS):**
```
[_] Baseline evaluation run
[_] All 6 metrics calculated
[_] Overall RAGAS score ≥ 0.90
```

**Phase 7 (Celery):**
```
[_] Celery workers start (4 concurrent)
[_] Task queued, returns task_id
[_] Task status endpoint works
[_] 50+ concurrent requests handled
```

---

## 🐛 COMMON ERRORS & FIXES

### **Error: Redis connection refused**
```bash
# Fix: Start Redis
docker run -d -p 6379:6379 redis:latest
# Or: redis-server.exe (Windows)
```

### **Error: Module 'sentence_transformers' not found**
```bash
pip install sentence-transformers==3.0.1
```

### **Error: Re-ranking service not responding**
```bash
# Check if running:
netstat -an | findstr 5004
# Start if not:
cd implementation && python reranking_service.py
```

### **Error: RAGAS import fails**
```bash
pip install ragas==0.1.9 datasets==2.18.0
```

### **Error: Celery workers not starting**
```bash
# Ensure Redis is running first
redis-cli ping
# Then start Celery:
celery -A tasks.celery_tasks worker --loglevel=info
```

### **Error: LangSmith traces not showing**
```bash
# Check .env:
echo $env:LANGSMITH_API_KEY
echo $env:LANGCHAIN_TRACING_V2
# Should be: true

# Verify account at https://smith.langchain.com
```

---

## 📈 SUCCESS METRICS (Target)

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| **Accuracy** | 70-75% | 90-95% | ≥90% |
| **Cache Hit Rate** | 0% | 40-60% | ≥40% |
| **Response Time** | 10-15s | 5-8s | <10s |
| **Cost per Query** | $0.40 | $0.24 | <$0.30 |
| **RAGAS Score** | - | 0.90+ | ≥0.90 |
| **Concurrent Load** | 1-5 | 50+ | ≥50 |

---

## 🔑 KEY DEPENDENCIES (.env)

```env
# Existing
MONGODB_URI=mongodb+srv://...
POSTGRES_HOST=localhost
POSTGRES_DB=ddn_ai_analysis
PINECONE_API_KEY=...
PINECONE_INDEX=ddn-error-solutions
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Phase 0+
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/0

# Phase 8 (Optional)
LANGSMITH_API_KEY=lsv2_...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=DDN-QA-System
```

---

## 📚 DOCUMENTATION FILES

- `IMPLEMENTATION-CHECKLIST.md` - Full detailed guide (THIS is your bible!)
- `PROGRESS-TRACKER.csv` - Daily checklist (open in Excel)
- `PROGRESS-TRACKER-FORMATTED.html` - Pretty tracker (convert to Excel)
- `AGENTIC-AI-GAP-ANALYSIS-AND-RECOMMENDATIONS.md` - Architecture analysis
- `QUICK-REFERENCE-GUIDE.md` - This file (daily use)

---

## ⚡ DAILY WORKFLOW

**Morning:**
1. Check PROGRESS-TRACKER.csv - what's today's task?
2. Start all required services (see commands above)
3. Open IMPLEMENTATION-CHECKLIST.md for detailed steps

**During Work:**
1. Follow step-by-step instructions
2. Use this QUICK-REFERENCE for commands
3. Run validation checklist after each file
4. Update PROGRESS-TRACKER.csv

**End of Day:**
1. Commit work: `git commit -m "Phase X: Task Y complete"`
2. Update progress tracker
3. Test services still running
4. Plan tomorrow's tasks

---

## 🆘 NEED HELP?

1. **Check logs:** `tail -f implementation/*.log`
2. **Verify services:** `netstat -an | findstr "5000 5001 5002 5004 5005"`
3. **Redis health:** `redis-cli ping`
4. **Review traces:** https://smith.langchain.com (Phase 8+)
5. **Check documentation:** `IMPLEMENTATION-CHECKLIST.md`

---

## 🎯 TODAY'S FOCUS (Example)

**If you're on Phase 2, Day 1:**
```
✅ Morning: Create reranking_service.py
✅ Noon: Test re-ranking standalone
✅ Afternoon: Integrate into langgraph_agent.py
✅ End of day: Validation checklist + commit
```

---

**💡 TIP:** Print this page or keep it open in a second monitor for quick reference!

**Last Updated:** 2025-10-28
**Status:** Ready to Use ✅
