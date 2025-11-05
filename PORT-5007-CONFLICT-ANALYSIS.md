# Port 5007 Conflict Analysis

## Issue Summary

**Current Situation:**
- `service_manager_api.py` is using port 5007 (CURRENTLY RUNNING)
- `aging_service.py` is planned for Phase 0F and also configured for port 5007 (NOT YET IMPLEMENTED)

**Conflict:** Both services cannot run on the same port simultaneously.

---

## Service Descriptions

### Service Manager API (port 5007 - ACTIVE)
**File:** `implementation/service_manager_api.py`
**Purpose:** Central orchestration service for starting/stopping all services
**Features:**
- Controls 8 services (PostgreSQL, AI Analysis, Dashboard API, Dashboard UI, n8n, Jenkins, Re-Ranking, Knowledge API)
- Provides REST API for service control
- Used by dashboard ServiceControl.jsx component
- Essential for "START ALL" / "STOP ALL" buttons in UI
- Already integrated and working

**Endpoints:**
- `GET /api/services/status` - Get all service statuses
- `POST /api/services/start/<service_id>` - Start specific service
- `POST /api/services/stop/<service_id>` - Stop specific service
- `POST /api/services/start-all` - Start all services
- `POST /api/services/stop-all` - Stop all services
- `POST /api/services/restart-all` - Restart all services
- `GET /health` - Health check

**Dependencies:**
- Dashboard UI depends on this for service control
- All automated service startup flows use this
- Critical for production deployment

### Aging Service (port 5007 - PLANNED)
**File:** `implementation/aging_service.py` (NOT YET CREATED)
**Purpose:** Auto-trigger analysis for old test failures
**Phase:** 0F
**Features (Planned):**
- APScheduler cron job (checks every 6 hours)
- Queries MongoDB for failures older than 3 days with consecutive_failures >= 3
- Automatically triggers n8n workflow for AI analysis
- Reduces manual intervention for persistent failures

**Status:** Planned but not implemented yet

---

## Options Analysis

### Option 1: Change Aging Service Port (RECOMMENDED)
**Move aging_service.py to port 5010**

**Pros:**
✅ Service Manager API stays on port 5007 (no breaking changes)
✅ Dashboard already integrated with port 5007
✅ All existing documentation references port 5007 for service manager
✅ No code changes needed in dashboard UI
✅ No risk to currently working system
✅ Aging service not yet implemented - easy to configure

**Cons:**
❌ Need to update .env configuration when aging service is implemented
❌ Need to document new port assignment

**Impact:** LOW - Aging service doesn't exist yet, easy change

**Changes Required:**
1. When creating `aging_service.py`, use port 5010
2. Update `.env.MASTER` with `AGING_SERVICE_PORT=5010`
3. Add to service documentation

### Option 2: Change Service Manager Port
**Move service_manager_api.py to port 5010 or 5011**

**Pros:**
✅ Aging service could use "originally planned" port 5007
✅ Keeps aging service configuration as documented

**Cons:**
❌ **BREAKING CHANGE** - Dashboard UI hardcodes `http://localhost:5007`
❌ Requires changes to `ServiceControl.jsx` component
❌ All documentation references port 5007 for service manager
❌ Risks breaking currently working dashboard service control
❌ Service manager is actively used, aging service isn't implemented
❌ Need to rebuild and redeploy dashboard UI
❌ Potential for configuration drift if not updated everywhere

**Impact:** HIGH - Requires changes to multiple components

**Changes Required:**
1. Modify `service_manager_api.py` to use new port
2. Update `ServiceControl.jsx` API_URL constant
3. Rebuild dashboard UI
4. Update all documentation
5. Update `.env.MASTER`
6. Update `START-ALL-SERVICES.bat` references
7. Test entire dashboard service control flow

### Option 3: Merge Services
**Combine aging service functionality into service_manager_api.py**

**Pros:**
✅ Single service on one port
✅ Simpler architecture
✅ Aging service can directly control services (already has the code)
✅ No port conflict

**Cons:**
❌ Service manager becomes more complex
❌ Mixing concerns (orchestration + scheduled tasks)
❌ Harder to test independently
❌ Service manager needs APScheduler dependency

**Impact:** MEDIUM - Architectural change

**Changes Required:**
1. Add APScheduler to service_manager_api.py
2. Add aging check logic to service manager
3. Add new endpoints for aging configuration
4. Test combined functionality

### Option 4: Use Dynamic Port for Aging Service
**Let aging service use any available port**

**Pros:**
✅ No hardcoded port conflict
✅ Flexible deployment

**Cons:**
❌ Need service discovery mechanism
❌ More complex configuration
❌ Aging service needs to be findable by other services

**Impact:** MEDIUM - Requires service discovery

---

## Recommendation

**✅ OPTION 1: Change Aging Service to Port 5010**

**Reasoning:**
1. **No Breaking Changes:** Service Manager API stays on port 5007 where it currently works
2. **Aging Service Not Implemented:** Easy to assign different port during implementation
3. **Dashboard Already Integrated:** ServiceControl.jsx already uses port 5007
4. **Documentation Consistency:** All docs reference port 5007 for service manager
5. **Low Risk:** No changes to working systems
6. **Future Flexibility:** Port 5010 is currently unused and available

**Implementation Plan:**
1. When implementing Phase 0F aging service:
   - Configure `aging_service.py` to use port 5010
   - Add `AGING_SERVICE_PORT=5010` to `.env.MASTER`
   - Add aging service to `service_manager_api.py` SERVICES dict
   - Update documentation

2. Port Assignment Map:
   ```
   5000 - AI Analysis Service
   5002 - MCP GitHub Server
   5004 - Manual Trigger API
   5005 - Hybrid Search Service
   5006 - Dashboard API
   5007 - Service Manager API ✅ KEEP
   5008 - Knowledge Management API
   5009 - Re-Ranking Service
   5010 - Aging Service (NEW) ✅ ASSIGN
   5173 - Dashboard UI (Vite)
   5432 - PostgreSQL
   5678 - n8n Workflows
   8081 - Jenkins
   ```

---

## Decision Required

**Question for Team:**
Which option should we proceed with?

**Recommendation:** Option 1 (Change Aging Service to Port 5010)

**Please confirm:**
- [ ] Option 1: Change aging service to port 5010 (RECOMMENDED)
- [ ] Option 2: Change service manager to different port
- [ ] Option 3: Merge aging service into service manager
- [ ] Option 4: Dynamic port allocation
- [ ] Other (specify):

---

## Next Steps After Decision

### If Option 1 (Recommended):
1. Update Phase 0F task definition to use port 5010
2. Add note in `.env.MASTER` for aging service configuration
3. Reserve port 5010 in port assignment documentation
4. No immediate code changes needed

### If Option 2:
1. Modify service_manager_api.py port
2. Update ServiceControl.jsx
3. Rebuild dashboard
4. Update all documentation
5. **Test thoroughly** - high risk of breaking changes

### If Option 3:
1. Design combined service architecture
2. Add scheduling to service_manager_api.py
3. Implement aging logic
4. Test extensively

### If Option 4:
1. Implement service discovery mechanism
2. Add configuration for dynamic ports
3. Update all service references

---

**Document Created:** 2025-11-04
**Status:** Awaiting Decision
**Priority:** MEDIUM (Blocks Phase 0F implementation)
**References:**
- Task 0F.6 in progress tracker
- service_manager_api.py (line 418)
- Planned aging_service.py (Phase 0F)
