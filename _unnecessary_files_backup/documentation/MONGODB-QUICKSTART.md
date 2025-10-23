# MongoDB Quick Start Guide - DDN AI Project

## ✅ Your MongoDB Options

You have **TWO options** for MongoDB:

### **🖥️ Option 1: Local MongoDB** (Recommended for Development)
**Status**: ✅ Running
- **Host**: `127.0.0.1` (localhost)
- **Port**: `27017`
- **Connection**: `mongodb://localhost:27017`
- **Best for**: Development, testing
- **Setup**: Follow steps below ↓

### **☁️ Option 2: MongoDB Atlas** (Recommended for Production)
**Status**: Account available
- **Atlas URL**: https://cloud.mongodb.com
- **Connection**: `mongodb+srv://...` (cloud)
- **Best for**: Production, team access
- **Setup**: See [MONGODB-ATLAS-SETUP.md](implementation/database/MONGODB-ATLAS-SETUP.md) →

**This guide covers Local MongoDB. For Atlas (cloud), see the Atlas setup guide.**

---

## 🚀 Local MongoDB Setup - 3 Steps (5 Minutes)

### **Step 1: Create Database & Collections**

```bash
# Navigate to database folder
cd C:\DDN-AI-Project-Documentation\implementation\database

# Run setup script
python setup_mongodb.py
```

**This creates:**
- ✅ Database: `ddn_ai_project`
- ✅ Collections: `builds`, `console_logs`, `test_results`, `analysis_solutions`, `refinement_history`
- ✅ Indexes for fast queries
- ✅ Sample test data

**Expected output:**
```
==================================================================
  DDN AI Project - MongoDB Setup
==================================================================

🔌 Connecting to MongoDB...
✅ Connected successfully!

📦 Setting up 'builds' collection...
  ✅ Created indexes: build_id, timestamp, status...
  ✅ Inserted sample build (SAMPLE_12345)

📝 Setting up 'console_logs' collection...
  ✅ Created indexes: build_id, timestamp
  ✅ Inserted sample console log

...

✅ MongoDB Setup Complete!
```

---

### **Step 2: Test Connection**

```bash
# Run connection test
python test_mongodb_connection.py
```

**This verifies:**
- ✅ MongoDB is accessible
- ✅ Database and collections exist
- ✅ Can read/write data
- ✅ Indexes are created
- ✅ Aggregation queries work

**Expected output:**
```
==================================================================
  DDN AI Project - MongoDB Connection Test
==================================================================

1️⃣  Testing connection...
   ✅ MongoDB server is responding
   ✅ MongoDB version: 7.0.4

2️⃣  Testing database access...
   ✅ Connected to database: ddn_ai_project

3️⃣  Checking collections...
   ✅ builds                    (  1 documents)
   ✅ console_logs              (  1 documents)
   ✅ test_results              (  1 documents)
   ✅ analysis_solutions        (  0 documents)
   ✅ refinement_history        (  0 documents)

...

✅ ALL TESTS PASSED!
```

---

### **Step 3: Configure n8n**

#### **A. Add MongoDB Credentials in n8n**

```bash
1. Open n8n: http://localhost:5678
2. Go to: Settings → Credentials
3. Click: "Add Credential"
4. Select: "MongoDB"
5. Fill in:
   Name: MongoDB Production
   Connection String: mongodb://localhost:27017/ddn_ai_project
   Database: ddn_ai_project
6. Click: "Save"
```

#### **B. Update .env File**

Create/edit `.env` in the implementation folder:

```bash
# Copy example
cd C:\DDN-AI-Project-Documentation\implementation
copy .env.example .env

# Edit .env and add:
MONGODB_URI=mongodb://localhost:27017/ddn_ai_project
MONGODB_DATABASE=ddn_ai_project
```

---

## 📊 View Your Data

### **Option 1: MongoDB Compass (GUI - Recommended)**

```bash
# 1. Download MongoDB Compass (if not installed):
https://www.mongodb.com/try/download/compass

# 2. Connect:
Connection String: mongodb://localhost:27017

# 3. Select database: ddn_ai_project

# 4. Browse collections:
- builds (test failures)
- console_logs (error details)
- test_results (test execution data)
- analysis_solutions (AI analysis results)
- refinement_history (user feedback history)
```

### **Option 2: MongoDB Shell (Command Line)**

```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017

# Switch to database
use ddn_ai_project

# View sample build
db.builds.findOne()

# View all builds
db.builds.find().pretty()

# Count documents
db.builds.countDocuments()

# View builds without analysis
db.builds.find({ has_analysis: false })

# View recent analyses
db.analysis_solutions.find().sort({ analysis_timestamp: -1 }).limit(5)
```

---

## 🧪 Optional: Add More Sample Data

```bash
# Navigate to database folder
cd C:\DDN-AI-Project-Documentation\implementation\database

# Create populate script
notepad populate_sample_data.py
```

**Paste this code:**

```python
#!/usr/bin/env python3
from pymongo import MongoClient
from datetime import datetime, timedelta
import random

MONGO_URI = "mongodb://localhost:27017"
DATABASE = "ddn_ai_project"

def populate(num_builds=10):
    client = MongoClient(MONGO_URI)
    db = client[DATABASE]

    jobs = ["DDN-Smoke-Tests", "DDN-Integration-Tests", "DDN-Performance-Tests"]
    suites = ["Health_Check", "API_Tests", "Storage_Tests"]
    errors = ["NullPointerException", "OutOfMemoryError", "AssertionError"]

    for i in range(num_builds):
        build_id = f"BUILD_{10000 + i}"
        build = {
            "build_id": build_id,
            "job_name": random.choice(jobs),
            "test_suite": random.choice(suites),
            "status": "FAILURE",
            "build_url": f"https://jenkins.example.com/job/{build_id}",
            "timestamp": datetime.utcnow() - timedelta(days=random.randint(1, 15)),
            "repository": "your-org/ddn-repo",
            "branch": "main",
            "error_log": f"[ERROR] {random.choice(errors)}: Test failed",
            "aging_days": random.randint(1, 15),
            "has_analysis": False
        }

        if not db.builds.find_one({"build_id": build_id}):
            db.builds.insert_one(build)
            print(f"✅ Inserted: {build_id}")

    print(f"\n✅ Total builds: {db.builds.count_documents({})}")
    client.close()

if __name__ == "__main__":
    populate(10)
```

**Run it:**
```bash
python populate_sample_data.py
```

---

## 🔍 Verify Setup

### **Quick Verification Checklist:**

```bash
# 1. Check MongoDB is running
mongosh mongodb://localhost:27017 --eval "db.runCommand({ ping: 1 })"

# 2. Check database exists
mongosh mongodb://localhost:27017 --eval "show dbs" | findstr ddn_ai_project

# 3. Check collections
mongosh mongodb://localhost:27017/ddn_ai_project --eval "show collections"

# 4. Check sample data
mongosh mongodb://localhost:27017/ddn_ai_project --eval "db.builds.countDocuments()"
```

**Expected results:**
```
✅ { ok: 1 }
✅ ddn_ai_project
✅ builds, console_logs, test_results, analysis_solutions, refinement_history
✅ 1 (or more if you ran populate script)
```

---

## 🎯 Integration with Workflows

### **How n8n Workflows Use MongoDB:**

```javascript
// Workflow 2 (Manual Trigger):
// Node 3: "MongoDB Get Minimal Data"
{
  "operation": "aggregate",
  "collection": "builds",
  "query": [
    { "$match": { "build_id": "{{ $json.build_id }}" } },
    { "$project": {
        "build_id": 1,
        "error_log": { "$substr": ["$error_log", 0, 2000] },
        "status": 1,
        "job_name": 1
    }}
  ]
}

// Node 10: "Store Solution"
{
  "operation": "insertOne",
  "collection": "analysis_solutions",
  "fields": "={{ JSON.stringify($json) }}"
}
```

### **Data Flow:**

```
User clicks "Analyze Now" in Dashboard
  ↓
Workflow 2 triggers
  ↓
MongoDB: Query builds collection → Get failure data
  ↓
LangGraph: Classify error
  ↓
Claude/RAG: Generate solution
  ↓
MongoDB: Insert solution into analysis_solutions
  ↓
Response to Dashboard with results
```

---

## 📋 Database Schema

### **`builds` Collection (Input Data)**
```javascript
{
  "build_id": "12345",              // Unique ID
  "job_name": "DDN-Smoke-Tests",    // Jenkins job
  "test_suite": "Health_Check",     // Test suite
  "status": "FAILURE",              // Build status
  "build_url": "https://...",       // Jenkins link
  "error_log": "NullPointerException...", // Error message
  "timestamp": ISODate("..."),      // When it failed
  "aging_days": 7,                  // Days since failure
  "has_analysis": false             // Analyzed yet?
}
```

### **`analysis_solutions` Collection (AI Output)**
```javascript
{
  "build_id": "12345",
  "error_category": "CODE_ERROR",
  "root_cause": "NullPointerException at line 127...",
  "fix_recommendation": "Add null check before...",
  "confidence_score": 0.92,
  "links": {
    "github_files": [
      {
        "file_path": "src/main/java/File.java",
        "line_number": 127,
        "github_url": "https://github.com/..."
      }
    ]
  },
  "analysis_timestamp": ISODate("..."),
  "estimated_cost_usd": 0.08
}
```

---

## 🛠️ Troubleshooting

### **Problem: "Connection Failed"**

```bash
# Check MongoDB is running
net start | findstr -i mongo

# Or check process
tasklist | findstr -i mongod

# If not running, start it:
net start MongoDB

# Or manually:
mongod --dbpath C:\DDN-Project\mongodb-data
```

### **Problem: "Database Not Found"**

```bash
# Re-run setup
cd C:\DDN-AI-Project-Documentation\implementation\database
python setup_mongodb.py
```

### **Problem: "No Sample Data"**

```bash
# Check data exists
mongosh mongodb://localhost:27017/ddn_ai_project --eval "db.builds.find().pretty()"

# If empty, re-run setup
python setup_mongodb.py
```

### **Problem: "n8n Can't Connect"**

```bash
# Verify connection string in n8n:
mongodb://localhost:27017/ddn_ai_project

# NOT:
mongodb://localhost:27017

# The database name must be included!
```

---

## ✅ You're Ready!

After completing these 3 steps, you have:

- ✅ MongoDB database `ddn_ai_project` created
- ✅ All 5 collections with indexes
- ✅ Sample test data loaded
- ✅ Connection verified working
- ✅ n8n credentials configured
- ✅ Ready to import workflows!

---

## 🚀 Next Steps

1. **Import n8n workflows**:
   - [workflow_2_manual_trigger.json](implementation/workflows/workflow_2_manual_trigger.json)
   - [workflow_3_refinement.json](implementation/workflows/workflow_3_refinement.json)

2. **Start Python services**:
   ```bash
   cd implementation
   python langgraph_agent.py
   ```

3. **Test manual trigger**:
   ```bash
   curl -X POST http://localhost:5678/webhook/ddn-manual-trigger \
     -H "Content-Type: application/json" \
     -d '{"build_id": "SAMPLE_12345", "user_email": "test@example.com"}'
   ```

4. **View results in MongoDB**:
   ```bash
   mongosh mongodb://localhost:27017/ddn_ai_project
   db.analysis_solutions.findOne()
   ```

---

**Questions?** Your MongoDB is ready at: `mongodb://localhost:27017/ddn_ai_project`

**Documentation**: See [mongodb-setup-guide.md](implementation/database/mongodb-setup-guide.md) for detailed info.
