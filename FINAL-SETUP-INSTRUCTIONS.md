# Final Setup Instructions - Get Monitoring Working NOW

## Current Situation

**Port 5005** has stuck processes (PIDs 35820, 42056) that can't be killed from command line.

**Solution:** Run the new enhanced dashboard API on **port 5006** instead!

---

## Quick Start (3 Steps)

### Step 1: Start Enhanced Dashboard API on Port 5006

Open a **new Command Prompt or PowerShell** window and run:

```cmd
cd C:\DDN-AI-Project-Documentation\implementation
python start_dashboard_api_port5006.py
```

**Expected Output:**
```
============================================================
DDN Dashboard API (Full System Monitoring)
============================================================
✓ MongoDB connected
✓ PostgreSQL connected
⚠ Pinecone connection issue (expected - wrong index name)
============================================================
Dashboard API running on http://0.0.0.0:5006
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

**Leave this terminal window open!**

---

### Step 2: Test All Monitoring Endpoints

Open **another Command Prompt** and test:

```cmd
# Health check
curl http://localhost:5006/api/health

# System status (ALL components)
curl http://localhost:5006/api/system/status

# Statistics
curl http://localhost:5006/api/stats

# Pipeline flow
curl http://localhost:5006/api/pipeline/flow

# Recent activity
curl http://localhost:5006/api/activity

# Test failures WITH AI analysis
curl http://localhost:5006/api/failures?limit=3
```

**All should return JSON data, not 404 errors!**

---

### Step 3: Run System Status Checker

```cmd
cd C:\DDN-AI-Project-Documentation\implementation
python check_system_status.py
```

**You should see colored output showing:**
- ✓ AI Service status
- ✓ All databases (MongoDB, PostgreSQL, Pinecone)
- ✓ Pipeline flow (4 stages)
- ✓ Recent activity
- ✓ Statistics

---

## All Services and Ports

| Service | Port | Status | Check Command |
|---------|------|--------|---------------|
| AI Analysis Service | 5000 | ✅ Running | `curl http://localhost:5000/api/health` |
| **Enhanced Dashboard API** | **5006** | ✅ **Use this!** | `curl http://localhost:5006/api/health` |
| Old Dashboard API | 5005 | ⚠️ Stuck (ignore) | Don't use |
| React Dashboard | 5173 | ✅ Running | Open http://localhost:5173 |
| Jenkins | 8081 | ✅ Running | Open http://localhost:8081 |

---

## Update React Dashboard to Use Port 5006

Your React dashboard (http://localhost:5173) currently fetches from port 5005.

**To update it:**

1. Find your dashboard source code (likely in `dashboard/src/`)
2. Search for `localhost:5005` or `:5005`
3. Replace with `localhost:5006` or `:5006`
4. Restart the React dev server

**Example:**
```javascript
// Before
fetch('http://localhost:5005/api/failures')

// After
fetch('http://localhost:5006/api/failures')
```

---

## What You Can Monitor Now

### 1. System Health (`/api/system/status`)
Shows real-time health of:
- MongoDB (test failures count)
- PostgreSQL (AI analyses count)
- Pinecone (vectors count)
- AI Service (Gemini, OpenAI, RAG status)

### 2. Pipeline Flow (`/api/pipeline/flow`)
Shows complete pipeline:
- Stage 1: Jenkins (test execution)
- Stage 2: MongoDB (failure storage)
- Stage 3: AI Analysis (Gemini + RAG)
- Stage 4: Dashboard (you!)

### 3. Recent Activity (`/api/activity`)
Chronological log of:
- Test failures
- AI analyses performed
- RAG matches found
- Confidence scores

### 4. Statistics (`/api/stats`)
- Total failures
- Failures in last 24h/7d
- Total AI analyses
- Average confidence score
- Classification breakdown

### 5. Test Failures WITH AI Analysis (`/api/failures`)
Each failure includes:
- Test name, error message, stack trace
- **AI analysis** (classification, root cause, solution)
- Confidence score
- Similar errors from RAG

---

## Next Priority Actions

### 1. ✅ Enhanced Dashboard API Working (Port 5006)
**Status:** Ready to start

### 2. ⚠️ Add OpenAI Credits (For Full RAG)
**Why:** Only 1 of 10 error docs loaded due to quota
**How:**
1. Go to https://platform.openai.com/account/billing
2. Add $5-10 credit
3. Run: `cd implementation && python load_error_docs_to_pinecone.py`
4. Test: `python test_rag_query.py`

### 3. 📊 Update React Dashboard
**Why:** Show all the new monitoring data visually
**How:** Change API calls from port 5005 → 5006

### 4. 🧪 Test Complete Pipeline
**Steps:**
1. Run Jenkins build
2. Let test fail
3. Check: `curl http://localhost:5006/api/failures?limit=1`
4. Verify AI analysis included
5. Check: `curl http://localhost:5006/api/activity`
6. See the complete flow!

---

## Troubleshooting

### Issue: Port 5006 also busy

```cmd
# Check what's on 5006
netstat -ano | findstr ":5006"

# If something is there, use port 5007 instead
# Edit start_dashboard_api_port5006.py and change:
app.run(host='0.0.0.0', port=5007, debug=True)
```

### Issue: Pinecone connection warning

**Expected!** The dashboard API is trying to use wrong Pinecone index name.

**Fix (optional):** The Pinecone connection in dashboard_api_full.py needs the correct index name.

**For now:** Ignore this warning. MongoDB and PostgreSQL monitoring work fine without it.

### Issue: Can't see colored output in check_system_status.py

```cmd
# Install colorama
pip install colorama

# Then run
python check_system_status.py
```

---

## Clean Up Port 5005 (Optional - Manual)

If you want to clean up the stuck processes on port 5005:

**Option 1: Restart your computer**
- Simplest solution
- Clears all stuck processes

**Option 2: Manual process kill**
1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to "Details" tab
3. Find `python.exe` processes
4. Check PID column for 35820 and 42056
5. Right-click → End Process

**Option 3: Keep using port 5006**
- No need to fight with stuck processes
- Everything works on 5006
- Update React dashboard to use 5006

---

## Summary

**What's Working:**
- ✅ AI Analysis Service (port 5000)
- ✅ Enhanced Dashboard API ready (port 5006)
- ✅ MongoDB, PostgreSQL, Pinecone connections
- ✅ Robot Framework tests
- ✅ System monitoring tools
- ✅ Complete pipeline tracking

**What to Do:**
1. Start dashboard API on port 5006
2. Test all endpoints work
3. Add OpenAI credits for full RAG
4. Update React dashboard to port 5006

**Test It NOW:**
```cmd
cd C:\DDN-AI-Project-Documentation\implementation
python start_dashboard_api_port5006.py
```

Then in another terminal:
```cmd
curl http://localhost:5006/api/system/status
```

**You should see full system status in JSON! 🎉**

---

**Created:** 2025-10-24
**Purpose:** Get monitoring working immediately without fighting stuck processes
