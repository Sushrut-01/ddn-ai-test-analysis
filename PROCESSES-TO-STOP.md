# Processes to Stop - Only Port 5005 Dashboard APIs

## STOP ONLY THESE (Port 5005 Dashboard APIs):

Based on investigation, **ONLY stop processes on port 5005**:

```cmd
# Step 1: Check what's on port 5005
netstat -ano | findstr ":5005" | findstr "LISTENING"
```

**Expected output:**
```
TCP    0.0.0.0:5005    0.0.0.0:0    LISTENING    35820
TCP    0.0.0.0:5005    0.0.0.0:0    LISTENING    42056
```

**Stop ONLY these two processes:**
```cmd
taskkill /PID 35820 /F
taskkill /PID 42056 /F
```

---

## ✅ KEEP RUNNING - DO NOT STOP:

### Port 5000 - AI Analysis Service
- **Process**: `python ai_analysis_service.py`
- **Why keep**: Provides Gemini AI analysis and RAG functionality
- **Check**: `curl http://localhost:5000/api/health`

### Port 5173 - React Dashboard
- **Process**: Node.js / Vite dev server
- **PID**: 152
- **Why keep**: Your dashboard UI
- **Check**: Open http://localhost:5173 in browser

### Port 8081 - Jenkins
- **Process**: Jenkins server
- **Why keep**: Runs test builds
- **Check**: Open http://localhost:8081 in browser

### MongoDB Atlas (Cloud)
- **Why keep**: Stores all test failures
- **No local process to stop**

### PostgreSQL (Port 5432)
- **Process**: PostgreSQL database
- **Why keep**: Stores AI analysis results
- **No need to stop**

### Pinecone (Cloud)
- **Why keep**: Vector database for RAG
- **No local process to stop**

---

## After Stopping Port 5005 Processes:

**Step 1: Verify port 5005 is clear**
```cmd
netstat -ano | findstr ":5005"
```
Should return **nothing**.

**Step 2: Start NEW dashboard API**
```cmd
cd C:\DDN-AI-Project-Documentation\implementation
python dashboard_api_full.py
```

**Step 3: Verify it works**
```cmd
# In another terminal
curl http://localhost:5005/api/health
curl http://localhost:5005/api/system/status
```

Should return **JSON**, not 404!

---

## Summary

**STOP (2 processes):**
- ❌ PID 35820 (old dashboard API on port 5005)
- ❌ PID 42056 (conflicting dashboard API on port 5005)

**KEEP RUNNING (Everything else):**
- ✅ AI Service (port 5000)
- ✅ React Dashboard (port 5173, PID 152)
- ✅ Jenkins (port 8081)
- ✅ MongoDB (cloud)
- ✅ PostgreSQL (port 5432)
- ✅ Pinecone (cloud)
- ✅ All background AI service instances
- ✅ All other processes

**Reason:** Port 5005 has old/conflicting dashboard APIs that return 404 for new monitoring endpoints. Only those need to be replaced with the new `dashboard_api_full.py`.

---

**Created:** 2025-10-24
**Purpose:** Clear guide on exactly which processes to stop (only port 5005 dashboard APIs)
