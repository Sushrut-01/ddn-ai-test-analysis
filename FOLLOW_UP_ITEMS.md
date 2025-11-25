# Follow-Up Items & Recommendations

**Created**: November 23, 2025  
**Status**: Tracking post-deployment improvements

---

## 🟡 Medium Priority

### 1. Investigate LangGraph Redis Connection
**Status:** To investigate  
**Current State:** LangGraph health endpoint reports `redis_available: false`  
**Impact:** May affect caching and async task coordination  
**Action:** 
- Check Redis configuration in LangGraph service
- Verify Redis connection string in `docker-compose-unified.yml`
- Confirm Redis container is reachable from LangGraph
- Review `implementation/langgraph_agent.py` Redis client initialization

---

## 🟢 Low Priority

### 2. PostgreSQL Cursor Errors (Non-Critical)
**Status:** Non-critical  
**Impact:** Does not affect functionality  
**Location:** Dashboard API logs  
**Description:** Recurring PostgreSQL cursor-related errors appear in logs but don't impact API operations.  
**Action:** Investigate root cause when time permits. May be related to connection pooling or query execution patterns.

### 3. UI Button Text Consistency
**Status:** ✅ Mitigated - Playwright tests updated with flexible selector  
**Issue:** UI button text varies between "Analyze Now" and "Trigger Analysis"  
**Action (optional):** Standardize button text in dashboard-ui components and document conventions

---

## 📋 Documentation & Maintenance

### 4. Create PR for `feature/qa-agent` Branch
**Action:** Open pull request to merge QA automation changes into main  
**Branch:** `feature/qa-agent`  
**Changes include:**
- QA agent scaffold and documentation
- Playwright UI test suite
- Jenkins pipeline updates
- MongoDB Atlas migration (removed local Mongo references)

### 5. Add More Playwright E2E Tests
**Suggested scenarios:**
- Test failure detail page navigation
- Validate analysis results rendering
- Test filtering and search functionality
- Verify integration service status indicators

---

## ✅ Completed Items
- ✅ Docker Compose configuration updated (20 services)
- ✅ Docker Compose files consolidated (removed duplicates)
- ✅ MongoDB Atlas migration complete
- ✅ Health checks validated for all core services
- ✅ Playwright test selector updated for "Trigger Analysis" button
- ✅ All services started and verified healthy
- ✅ QA agent scaffold and documentation created
- ✅ Jenkins pipeline updated with QA stage
- ✅ MCP Playwright agents installed (`@ejazullah/mcp-playwright`)
  - Test Generator Agent (auto-generates tests from interactions)
  - Test Healer Agent (auto-repairs failing selectors)
  - Test Planner Agent (generates test plans from requirements)
  - CDP support for connecting to existing browsers
  - Configuration file created: `mcp-configs/mcp-playwright-config.json`
  - Documentation: `tests/ui/MCP-PLAYWRIGHT-AGENTS.md`

---

**Last Updated**: November 23, 2025
