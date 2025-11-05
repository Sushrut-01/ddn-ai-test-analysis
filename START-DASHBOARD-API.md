# Start Dashboard API - Clean Setup

**Problem:** Multiple dashboard API processes running on port 5005, blocking the new enhanced API.

## Quick Fix (Recommended)

### Step 1: Stop ALL Python processes on port 5005

Open PowerShell or Command Prompt and run:

```powershell
# Find all processes on port 5005
netstat -ano | findstr ":5005"

# You'll see output like:
#   TCP    0.0.0.0:5005    0.0.0.0:0    LISTENING    35820
#   TCP    0.0.0.0:5005    0.0.0.0:0    LISTENING    42056

# Stop each process (replace PID with actual numbers from above)
taskkill /PID 35820 /F
taskkill /PID 42056 /F
```

### Step 2: Verify port 5005 is clear

```powershell
netstat -ano | findstr ":5005"
# Should return nothing
```

### Step 3: Start the new enhanced dashboard API

```cmd
cd C:\DDN-AI-Project-Documentation\implementation
python dashboard_api_full.py
```

**You should see:**
```
============================================================
DDN Dashboard API (Full System Monitoring)
============================================================
✓ MongoDB connected
✓ PostgreSQL connected
✓ Pinecone connected (156 vectors)
============================================================
Dashboard API running on http://0.0.0.0:5005
============================================================

Available Endpoints:
  GET /api/system/status    - System health status
  GET /api/pipeline/flow    - Pipeline flow monitoring
  GET /api/failures         - Test failures with AI analysis
  GET /api/analysis/<id>    - Detailed AI analysis
  GET /api/stats            - System statistics
  GET /api/activity         - Recent activity log
  GET /api/health           - Health check
============================================================
```

### Step 4: Test the new API

Open another terminal and test:

```cmd
curl http://localhost:5005/api/health
curl http://localhost:5005/api/system/status
curl http://localhost:5005/api/stats
```

**All should return JSON, not 404 errors!**

---

## Alternative: Use Different Port (If Port 5005 is busy)

If you can't clear port 5005, you can run the enhanced dashboard API on a different port:

### Option A: Modify dashboard_api_full.py

Edit `implementation/dashboard_api_full.py`, change the last line:

```python
# Find this line (at the end):
app.run(host='0.0.0.0', port=5005, debug=True)

# Change to:
app.run(host='0.0.0.0', port=5006, debug=True)
```

Then start:
```cmd
python dashboard_api_full.py
```

Test with:
```cmd
curl http://localhost:5006/api/health
```

### Option B: Keep Old Dashboard (MongoDB only)

If you want to keep port 5005 for the old dashboard:

1. Use old dashboard on port 5005 (already running)
2. Run new enhanced dashboard on port 5006

**Note:** Your React dashboard at http://localhost:5173 will need to be updated to point to the correct port.

---

## What Each Dashboard API Does

| File | What It Does | Port | Status |
|------|--------------|------|--------|
| `dashboard_api_mongodb_only.py` | OLD: Only reads MongoDB failures | 5005 | Temporary, can be replaced |
| `dashboard_api_full.py` | **NEW**: Full monitoring system | 5005 | **Use this one!** |

### New Enhanced API Features:
- ✅ MongoDB test failures
- ✅ PostgreSQL AI analyses
- ✅ Pinecone vector search
- ✅ System health status (all components)
- ✅ Pipeline flow visualization
- ✅ Recent activity log
- ✅ Statistics and metrics
- ✅ Test failures WITH AI analysis attached

---

## Troubleshooting

### Issue: Port 5005 still busy after killing processes

```cmd
# Use PowerShell to forcefully stop
powershell -Command "Get-NetTCPConnection -LocalPort 5005 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }"
```

### Issue: Can't find what's using port 5005

```cmd
# List all Python processes
tasklist | findstr python

# Kill ALL Python processes (WARNING: Stops ALL Python including AI service)
taskkill /IM python.exe /F

# Then restart what you need:
cd C:\DDN-AI-Project-Documentation\implementation
start "AI Service" python ai_analysis_service.py
start "Dashboard API" python dashboard_api_full.py
```

---

## Recommended Setup (Fresh Start)

1. **Stop everything on port 5005:**
   ```cmd
   netstat -ano | findstr ":5005"
   taskkill /PID <each_pid> /F
   ```

2. **Start AI Service (port 5000):**
   ```cmd
   cd implementation
   start "AI Service" python ai_analysis_service.py
   ```

3. **Start Enhanced Dashboard API (port 5005):**
   ```cmd
   start "Dashboard API" python dashboard_api_full.py
   ```

4. **Check React Dashboard (port 5173):**
   ```
   http://localhost:5173
   ```

---

## Next Steps After Starting

Once the enhanced dashboard API is running successfully:

1. ✅ Test all endpoints work (no 404 errors)
2. ✅ Run system status checker: `python check_system_status.py`
3. ✅ Update React dashboard to use new endpoints
4. ✅ Add OpenAI credits and reload error docs

---

**Created:** 2025-10-24
**Purpose:** Clean startup guide for enhanced dashboard API
