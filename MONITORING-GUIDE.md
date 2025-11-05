# System Monitoring & Tracing Guide

**How to monitor and trace everything in the DDN AI Test Analysis System**

---

## Quick Status Check

Run this anytime to see if everything is working:

```bash
cd C:\DDN-AI-Project-Documentation\implementation
python check_system_status.py
```

**Expected Output:**
```
======================================================================
DDN AI Test Analysis System - Status Check
======================================================================

==================================================================
AI Analysis Service (Port 5000)
==================================================================

✓ AI Service                          healthy
✓   Gemini AI                         available
✓   OpenAI Embeddings                 available
✓   Pinecone                          connected
    ├─ Vectors: 156
    └─ Dimension: 1536
✓   MongoDB                           connected
    └─ Total Failures: 146
✓   PostgreSQL                        connected
    └─ Total Analyses: 42
✓   RAG (Error Docs)                  enabled

==================================================================
Dashboard API (Port 5005)
==================================================================

✓ Dashboard API                       healthy
✓   MONGODB                           healthy
    └─ Failures: 146
✓   POSTGRESQL                        healthy
    └─ Analyses: 42
✓   PINECONE                          connected
    └─ Vectors: 156

Statistics:
   ├─ Total Failures: 146
   ├─ Failures (24h): 19
   ├─ AI Analyses: 42
   └─ Avg Confidence: 0.78

==================================================================
Pipeline Flow
==================================================================

✓ Stage 1: Test Execution (Jenkins)  active
   └─ Recent: 5 activities
✓ Stage 2: MongoDB Storage            active
   ├─ Total: 146
   └─ Last 24h: 19
✓ Stage 3: AI Analysis                active
   ├─ Total: 42
   ├─ Last 24h: 12
   └─ Avg Confidence: 0.78
✓ Stage 4: Dashboard Display          active
```

---

## API Endpoints for Monitoring

### 1. System Status (All Components)

```bash
curl http://localhost:5005/api/system/status | jq
```

**Returns:**
```json
{
  "timestamp": "2025-10-24T10:30:00",
  "overall_status": "healthy",
  "components": {
    "mongodb": {
      "status": "healthy",
      "connected": true,
      "total_failures": 146
    },
    "postgresql": {
      "status": "healthy",
      "connected": true,
      "total_analyses": 42
    },
    "pinecone": {
      "status": "healthy",
      "connected": true,
      "total_vectors": 156,
      "dimension": 1536
    },
    "ai_service": {
      "status": "healthy",
      "gemini_available": true,
      "openai_available": true,
      "rag_enabled": true
    }
  }
}
```

---

### 2. Pipeline Flow (What's Happening)

```bash
curl http://localhost:5005/api/pipeline/flow | jq
```

**Shows:**
- Stage 1: Test Execution (Jenkins) → Recent test failures
- Stage 2: MongoDB Storage → Total failures stored
- Stage 3: AI Analysis → Analyses performed
- Stage 4: Dashboard Display → Viewing now

---

### 3. Recent Activity Log

```bash
curl http://localhost:5005/api/activity | jq
```

**Shows last 20 activities:**
```json
{
  "activities": [
    {
      "type": "test_failure",
      "timestamp": "2025-10-24T10:25:00",
      "description": "Test failed: EXAScaler Health Check",
      "details": {
        "test": "EXAScaler Health Check",
        "build": "42",
        "error": "Connection refused..."
      }
    },
    {
      "type": "ai_analysis",
      "timestamp": "2025-10-24T10:25:15",
      "description": "AI analyzed failure as INFRASTRUCTURE",
      "details": {
        "classification": "INFRASTRUCTURE",
        "confidence": 0.85,
        "failure_id": "67..."
      }
    }
  ]
}
```

---

### 4. Statistics

```bash
curl http://localhost:5005/api/stats | jq
```

**Shows:**
- Total failures
- Failures in last 24 hours
- Failures in last 7 days
- Total AI analyses
- Average AI confidence
- Classification breakdown

---

### 5. AI Service Health

```bash
curl http://localhost:5000/api/health | jq
```

**Detailed AI service status:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T10:30:00",
  "components": {
    "gemini": {
      "api_key_configured": true,
      "model_initialized": true,
      "model_name": "models/gemini-flash-latest",
      "status": "available"
    },
    "openai": {
      "api_key_configured": true,
      "embedding_model": "text-embedding-3-small",
      "status": "available"
    },
    "pinecone": {
      "status": "connected",
      "total_vectors": 156
    }
  },
  "rag_enabled": true
}
```

---

## Tracing Complete Pipeline

### Step-by-Step: What Happens When Jenkins Test Fails

#### 1. Jenkins Executes Test

```
Jenkins (Port 8081)
├─ Runs Robot Framework test
├─ Test fails
└─ mongodb_robot_listener.py captures failure
```

**Check Jenkins:**
```
http://localhost:8081/job/DDN-Robot-Tests/lastBuild/console
```

---

#### 2. Failure Stored in MongoDB

```
MongoDB Atlas
├─ Collection: test_failures
├─ Document created with:
│   ├─ test_name
│   ├─ error_message
│   ├─ stack_trace
│   ├─ timestamp
│   └─ build_number
```

**Check MongoDB:**
```bash
curl http://localhost:5005/api/failures?limit=5 | jq
```

Or query directly:
```bash
cd implementation
python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['ddn_tests']
failures = list(db['test_failures'].find().sort('timestamp', -1).limit(5))
for f in failures:
    print(f'{f[\"test_name\"]} - {f[\"timestamp\"]}')
"
```

---

#### 3. AI Analysis with RAG

```
AI Analysis Service (Port 5000)
├─ Reads failure from MongoDB
├─ STEP 1: Query RAG (Pinecone)
│   ├─ Create embedding of error message
│   ├─ Query for similar documented errors
│   └─ Returns top 3 matches
├─ STEP 2: Build enhanced prompt
│   ├─ Include current failure
│   └─ Add similar error documentation
├─ STEP 3: Gemini AI analysis
│   ├─ Analyzes with RAG context
│   ├─ Returns classification
│   ├─ Provides root cause
│   └─ Suggests solution
└─ STEP 4: Store results
    ├─ PostgreSQL: AI analysis
    └─ Pinecone: Current failure embedding
```

**Trace AI Analysis:**

Check if analysis happened:
```bash
curl "http://localhost:5005/api/analysis/<failure_id>" | jq
```

Check AI service logs:
```bash
# If running in terminal, you'll see:
[RAG] Querying error documentation for: Test Name
[RAG] Found 3 similar error docs
[Gemini] Analyzing with RAG context: <failure_id>
[Gemini] SUCCESS (RAG-enhanced): INFRASTRUCTURE
```

---

#### 4. Storage in Databases

**PostgreSQL:**
```
Table: failure_analysis
├─ mongodb_failure_id
├─ classification (ENVIRONMENT/CODE/etc)
├─ root_cause
├─ severity
├─ recommendation
├─ confidence_score
└─ analyzed_at
```

**Check PostgreSQL:**
```bash
cd implementation
python -c "
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(
    host='localhost',
    database='ddn_ai_analysis',
    user='postgres',
    password=os.getenv('POSTGRES_PASSWORD')
)
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM failure_analysis')
print(f'Total analyses: {cursor.fetchone()[0]}')
cursor.close()
conn.close()
"
```

**Pinecone:**
```
Vectors stored:
├─ Current failure (doc_type="test_failure")
└─ Error documentation (doc_type="error_documentation")
```

**Check Pinecone:**
```bash
python -c "
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index('ddn-test-failures')
stats = index.describe_index_stats()
print(f'Total vectors: {stats.total_vector_count}')
print(f'Dimension: {stats.dimension}')
"
```

---

#### 5. Dashboard Display

```
Dashboard (Port 5173)
├─ Fetches from Dashboard API (Port 5005)
├─ Shows test failures
├─ Shows AI analysis
├─ Shows similar failures
└─ Shows statistics
```

**Check Dashboard API:**
```bash
curl http://localhost:5005/api/failures?limit=1 | jq
```

**View in Browser:**
```
http://localhost:5173
```

---

## How to Know AI is Working

### Method 1: Check AI Service Health

```bash
curl http://localhost:5000/api/health | jq '.gemini_available'
```

**Expected:** `true`

---

### Method 2: Check AI Analysis in Dashboard API

```bash
curl http://localhost:5005/api/failures?limit=1 | jq '.[0].ai_analysis'
```

**If AI working, you'll see:**
```json
{
  "classification": "INFRASTRUCTURE",
  "root_cause": "...",
  "severity": "HIGH",
  "recommendation": "...",
  "confidence_score": 0.85,
  "analyzed_at": "2025-10-24T10:25:15"
}
```

**If AI not working:**
```json
null
```

---

### Method 3: Check PostgreSQL for Analyses

```bash
curl http://localhost:5005/api/stats | jq '.total_analyzed'
```

**Should show:** Number > 0 (if failures analyzed)

---

### Method 4: Trigger Analysis Manually

```bash
# Get a failure ID
FAILURE_ID=$(curl -s http://localhost:5005/api/failures?limit=1 | jq -r '.failures[0]._id')

# Trigger analysis
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"failure_id\": \"$FAILURE_ID\"}" | jq
```

**Expected:** AI analysis with classification, root_cause, solution

---

## How to Know RAG is Working

### Method 1: Check AI Health for RAG Status

```bash
curl http://localhost:5000/api/health | jq '.rag_enabled'
```

**Expected:** `true`

---

### Method 2: Check Analysis for similar_error_docs

When you analyze a failure, the response should include `similar_error_docs`:

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"failure_id": "..."}' | jq '.similar_error_docs'
```

**If RAG working:**
```json
[
  {
    "similarity_score": 0.8456,
    "error_id": "ERR001",
    "error_type": "NullPointerException",
    "category": "CODE",
    "root_cause": "...",
    "tags": ["null-pointer", "initialization"]
  }
]
```

**If RAG not working:** `[]` (empty array)

---

### Method 3: Check Pinecone has Error Docs

```bash
python -c "
from pinecone import Pinecone
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Check Pinecone
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index('ddn-test-failures')

# Create test embedding
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = openai_client.embeddings.create(
    model='text-embedding-3-small',
    input='error documentation'
)
embedding = response.data[0].embedding

# Query for error docs
results = index.query(
    vector=embedding,
    top_k=10,
    include_metadata=True,
    filter={'doc_type': {'$eq': 'error_documentation'}}
)

print(f'Error docs in Pinecone: {len(results.matches)}')
for match in results.matches:
    print(f'  - {match.metadata.get(\"error_id\")}: {match.metadata.get(\"error_type\")}')
"
```

**Expected:** 10 error documents

---

## Continuous Monitoring

### Option 1: Watch Status in Real-Time

```bash
# Run status check every 30 seconds
while true; do
  clear
  python check_system_status.py
  sleep 30
done
```

---

### Option 2: Monitor Logs

**AI Service Logs:**
```bash
cd implementation
python ai_analysis_service.py 2>&1 | tee ai_service.log
```

**Dashboard API Logs:**
```bash
python dashboard_api_full.py 2>&1 | tee dashboard.log
```

---

### Option 3: Monitor Activity

```bash
# Watch recent activity every 10 seconds
while true; do
  clear
  echo "=== Recent Activity ==="
  curl -s http://localhost:5005/api/activity | jq '.activities[0:5]'
  sleep 10
done
```

---

## Troubleshooting

### Issue: AI Service shows "degraded"

**Check:**
```bash
curl http://localhost:5000/api/health | jq '.components'
```

**Look for:** Which component has `"status": "error"`

**Fix:**
- Gemini error → Check `GEMINI_API_KEY` in `.env`
- OpenAI error → Check `OPENAI_API_KEY` in `.env`
- Pinecone error → Check `PINECONE_API_KEY` in `.env`
- MongoDB error → Check `MONGODB_URI` in `.env`
- PostgreSQL error → Check database is running

---

### Issue: No AI analyses appearing

**Diagnose:**

1. Check MongoDB has failures:
   ```bash
   curl http://localhost:5005/api/failures?limit=1
   ```

2. Check AI service is running:
   ```bash
   curl http://localhost:5000/api/health
   ```

3. Manually trigger analysis:
   ```bash
   FAILURE_ID=$(curl -s http://localhost:5005/api/failures?limit=1 | jq -r '.failures[0]._id')
   curl -X POST http://localhost:5000/api/analyze \
     -H "Content-Type: application/json" \
     -d "{\"failure_id\": \"$FAILURE_ID\"}"
   ```

---

### Issue: RAG not finding similar errors

**Check error docs loaded:**
```bash
cd implementation
python test_rag_query.py
```

**If no error docs found:**
```bash
python load_error_docs_to_pinecone.py
```

---

## Dashboard Enhancement (To Do)

The dashboard UI should be updated to show:

### 1. System Status Page

```
System Health
├─ ✓ MongoDB (146 failures)
├─ ✓ PostgreSQL (42 analyses)
├─ ✓ Pinecone (156 vectors)
├─ ✓ Gemini AI (available)
├─ ✓ OpenAI (available)
└─ ✓ RAG (enabled)
```

### 2. Pipeline View

```
Jenkins → MongoDB → AI Analysis (RAG) → PostgreSQL + Pinecone → Dashboard

Stage 1: 5 recent test failures
Stage 2: 146 total failures stored
Stage 3: 42 analyses (78% avg confidence)
Stage 4: Viewing now
```

### 3. Activity Stream

```
10:30:00 - Test failed: EXAScaler Health Check
10:30:15 - AI analyzed as INFRASTRUCTURE (confidence: 0.85)
10:30:16 - RAG found 3 similar documented errors
10:31:00 - Test failed: AI400X Checkpoint Test
...
```

---

## Summary: How to Monitor Everything

### Quick Commands

```bash
# Overall status
python check_system_status.py

# AI service health
curl http://localhost:5000/api/health | jq

# System status
curl http://localhost:5005/api/system/status | jq

# Pipeline flow
curl http://localhost:5005/api/pipeline/flow | jq

# Recent activity
curl http://localhost:5005/api/activity | jq

# Statistics
curl http://localhost:5005/api/stats | jq

# Test failures
curl http://localhost:5005/api/failures | jq

# Specific analysis
curl "http://localhost:5005/api/analysis/<failure_id>" | jq
```

---

## Ports Summary

| Service | Port | URL | Check |
|---------|------|-----|-------|
| AI Analysis Service | 5000 | http://localhost:5000 | `curl http://localhost:5000/api/health` |
| Dashboard API | 5005 | http://localhost:5005 | `curl http://localhost:5005/api/health` |
| Dashboard UI | 5173 | http://localhost:5173 | Open in browser |
| Jenkins | 8081 | http://localhost:8081 | Open in browser |
| PostgreSQL | 5432 | localhost:5432 | `psql -h localhost -U postgres ddn_ai_analysis` |

---

**Quick Test: Is Everything Working?**

```bash
cd C:\DDN-AI-Project-Documentation\implementation
python check_system_status.py
```

If all components show ✓ (green checkmark), everything is working!
