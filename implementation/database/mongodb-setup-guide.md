# MongoDB Setup Guide for DDN AI Project

## 📊 Your MongoDB Status

✅ **MongoDB is Running!**
- **Host**: `127.0.0.1` (localhost)
- **Port**: `27017`
- **Connection String**: `mongodb://localhost:27017`
- **Data Directory**: `C:\DDN-Project\mongodb-data`
- **Log File**: `C:\DDN-Project\logs\mongodb.log`

---

## 🎯 What We'll Set Up

1. **Database**: `ddn_ai_project`
2. **Collections**:
   - `builds` - Test failure build information
   - `console_logs` - Full console output and stack traces
   - `test_results` - Test execution details
   - `analysis_solutions` - AI-generated solutions
   - `refinement_history` - User feedback and refinements

---

## 🚀 Step 1: Create Database & Collections

### **Option A: Using MongoDB Compass (GUI)**

```bash
# 1. Download MongoDB Compass (if not installed):
https://www.mongodb.com/try/download/compass

# 2. Connect to your MongoDB:
Connection String: mongodb://localhost:27017

# 3. Create new database:
- Click "Create Database"
- Database Name: ddn_ai_project
- Collection Name: builds

# 4. Create remaining collections:
- analysis_solutions
- console_logs
- test_results
- refinement_history
```

---

### **Option B: Using MongoDB Shell (Command Line)**

```bash
# Open Command Prompt or PowerShell
# Connect to MongoDB:
mongosh mongodb://localhost:27017

# Create database and collections:
use ddn_ai_project

db.createCollection("builds")
db.createCollection("console_logs")
db.createCollection("test_results")
db.createCollection("analysis_solutions")
db.createCollection("refinement_history")

# Verify collections created:
show collections
```

---

### **Option C: Using Python Script (Automated)**

Save this as `setup_mongodb.py`:

```python
#!/usr/bin/env python3
"""
MongoDB Setup Script for DDN AI Project
Creates database, collections, and indexes
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime

# Connection
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "ddn_ai_project"

def setup_mongodb():
    print("🔌 Connecting to MongoDB...")
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]

    print(f"✅ Connected to database: {DATABASE_NAME}")

    # ================================================================
    # 1. BUILDS COLLECTION
    # ================================================================
    print("\n📦 Setting up 'builds' collection...")

    builds = db.builds

    # Create indexes
    builds.create_index([("build_id", ASCENDING)], unique=True)
    builds.create_index([("timestamp", DESCENDING)])
    builds.create_index([("status", ASCENDING)])
    builds.create_index([("job_name", ASCENDING)])
    builds.create_index([("test_suite", ASCENDING)])

    # Insert sample data
    sample_build = {
        "build_id": "SAMPLE_12345",
        "job_name": "DDN-Smoke-Tests",
        "test_suite": "Health_Check_Suite",
        "status": "FAILURE",
        "build_url": "https://jenkins.your-domain.com/job/DDN-Smoke-Tests/12345",
        "timestamp": datetime.utcnow(),
        "repository": "your-org/ddn-repo",
        "branch": "main",
        "commit_sha": "abc123def456",
        "error_log": """
[ERROR] Test failed: test_storage_initialization
java.lang.NullPointerException: Cannot invoke "StorageConfig.getPath()" because "this.storageConfig" is null
    at com.ddn.storage.DDNStorage.initialize(DDNStorage.java:127)
    at com.ddn.tests.HealthCheckTest.testStorageInit(HealthCheckTest.java:45)
""".strip(),
        "aging_days": 5,
        "has_analysis": False
    }

    # Only insert if sample doesn't exist
    if not builds.find_one({"build_id": "SAMPLE_12345"}):
        builds.insert_one(sample_build)
        print("  ✅ Sample build inserted")
    else:
        print("  ℹ️  Sample build already exists")

    print(f"  ✅ Created indexes for 'builds'")

    # ================================================================
    # 2. CONSOLE_LOGS COLLECTION
    # ================================================================
    print("\n📝 Setting up 'console_logs' collection...")

    console_logs = db.console_logs

    # Create indexes
    console_logs.create_index([("build_id", ASCENDING)])

    # Insert sample data
    sample_log = {
        "build_id": "SAMPLE_12345",
        "full_log": "[Full console output would be here... 1000s of lines]",
        "stack_trace": """
java.lang.NullPointerException: Cannot invoke "StorageConfig.getPath()" because "this.storageConfig" is null
    at com.ddn.storage.DDNStorage.initialize(DDNStorage.java:127)
    at com.ddn.storage.DDNStorage.<init>(DDNStorage.java:45)
    at com.ddn.tests.HealthCheckTest.setUp(HealthCheckTest.java:30)
    at com.ddn.tests.HealthCheckTest.testStorageInit(HealthCheckTest.java:45)
""".strip(),
        "error_count": 1,
        "warning_count": 5,
        "timestamp": datetime.utcnow()
    }

    if not console_logs.find_one({"build_id": "SAMPLE_12345"}):
        console_logs.insert_one(sample_log)
        print("  ✅ Sample console log inserted")

    print(f"  ✅ Created indexes for 'console_logs'")

    # ================================================================
    # 3. TEST_RESULTS COLLECTION
    # ================================================================
    print("\n🧪 Setting up 'test_results' collection...")

    test_results = db.test_results

    # Create indexes
    test_results.create_index([("build_id", ASCENDING)])

    # Insert sample data
    sample_test = {
        "build_id": "SAMPLE_12345",
        "total_tests": 50,
        "passed": 49,
        "failed": 1,
        "skipped": 0,
        "failed_tests": [
            {
                "test_name": "testStorageInit",
                "test_class": "com.ddn.tests.HealthCheckTest",
                "test_file": "src/test/java/com/ddn/tests/HealthCheckTest.java",
                "error_message": "NullPointerException",
                "duration_ms": 150
            }
        ],
        "timestamp": datetime.utcnow()
    }

    if not test_results.find_one({"build_id": "SAMPLE_12345"}):
        test_results.insert_one(sample_test)
        print("  ✅ Sample test results inserted")

    print(f"  ✅ Created indexes for 'test_results'")

    # ================================================================
    # 4. ANALYSIS_SOLUTIONS COLLECTION
    # ================================================================
    print("\n🤖 Setting up 'analysis_solutions' collection...")

    analysis_solutions = db.analysis_solutions

    # Create indexes
    analysis_solutions.create_index([("build_id", ASCENDING)], unique=True)
    analysis_solutions.create_index([("analysis_timestamp", DESCENDING)])
    analysis_solutions.create_index([("error_category", ASCENDING)])
    analysis_solutions.create_index([("confidence_score", DESCENDING)])

    print(f"  ✅ Created indexes for 'analysis_solutions'")

    # ================================================================
    # 5. REFINEMENT_HISTORY COLLECTION
    # ================================================================
    print("\n🔄 Setting up 'refinement_history' collection...")

    refinement_history = db.refinement_history

    # Create indexes
    refinement_history.create_index([("build_id", ASCENDING)])
    refinement_history.create_index([("timestamp", DESCENDING)])
    refinement_history.create_index([("user_email", ASCENDING)])

    print(f"  ✅ Created indexes for 'refinement_history'")

    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "="*60)
    print("✅ MongoDB Setup Complete!")
    print("="*60)
    print(f"\n📊 Database: {DATABASE_NAME}")
    print(f"📍 Connection: {MONGO_URI}")
    print(f"\n📦 Collections Created:")

    for collection_name in db.list_collection_names():
        count = db[collection_name].count_documents({})
        print(f"  - {collection_name}: {count} documents")

    print("\n🎯 Next Steps:")
    print("  1. Update .env file with MongoDB connection string")
    print("  2. Configure n8n workflows with MongoDB credentials")
    print("  3. Start Python services (LangGraph, MCP servers)")
    print("  4. Test workflows with sample data")

    print("\n📝 Connection String for .env:")
    print(f"  MONGODB_URI={MONGO_URI}/{DATABASE_NAME}")

    client.close()
    print("\n✅ Setup complete!\n")

if __name__ == "__main__":
    setup_mongodb()
```

**Run the script:**
```bash
cd C:\DDN-AI-Project-Documentation\implementation\database
python setup_mongodb.py
```

---

## 🔗 Step 2: Configure n8n MongoDB Credentials

### **In n8n UI:**

```bash
1. Open n8n (http://localhost:5678)
2. Go to Settings → Credentials
3. Click "Add Credential"
4. Select "MongoDB"
5. Fill in:
   - Name: "MongoDB Production" (or "mongodb-prod")
   - Connection String: mongodb://localhost:27017/ddn_ai_project
   - Database: ddn_ai_project
6. Click "Save"
```

### **Connection String Formats:**

```bash
# Basic (no authentication):
mongodb://localhost:27017/ddn_ai_project

# With authentication:
mongodb://username:password@localhost:27017/ddn_ai_project

# With authentication + auth database:
mongodb://username:password@localhost:27017/ddn_ai_project?authSource=admin
```

---

## 📝 Step 3: Update Environment Variables

Create/Update `.env` file:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/ddn_ai_project
MONGODB_DATABASE=ddn_ai_project

# Alternative: Full connection string
# MONGODB_URI=mongodb://username:password@localhost:27017/ddn_ai_project?authSource=admin
```

---

## 🧪 Step 4: Test MongoDB Connection

### **Test Script** (`test_mongodb_connection.py`):

```python
#!/usr/bin/env python3
"""Test MongoDB connection for DDN AI Project"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017"
DATABASE = "ddn_ai_project"

def test_connection():
    print("🔍 Testing MongoDB Connection...")
    print(f"URI: {MONGO_URI}")
    print(f"Database: {DATABASE}\n")

    try:
        # Connect
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!\n")

        # Access database
        db = client[DATABASE]

        # List collections
        collections = db.list_collection_names()
        print(f"📦 Collections in '{DATABASE}':")
        for coll in collections:
            count = db[coll].count_documents({})
            print(f"  - {coll}: {count} documents")

        # Test query
        print(f"\n🔍 Testing query on 'builds' collection...")
        builds = db.builds.find().limit(5)

        print(f"\n📊 Sample builds:")
        for build in builds:
            print(f"  - Build ID: {build.get('build_id')}")
            print(f"    Job: {build.get('job_name')}")
            print(f"    Status: {build.get('status')}")
            print(f"    Aging: {build.get('aging_days', 0)} days\n")

        # Test insert (and cleanup)
        print("✍️  Testing insert operation...")
        test_doc = {
            "build_id": "TEST_CONNECTION_" + str(int(datetime.utcnow().timestamp())),
            "job_name": "Connection Test",
            "status": "TEST",
            "timestamp": datetime.utcnow()
        }

        result = db.builds.insert_one(test_doc)
        print(f"✅ Insert successful! ID: {result.inserted_id}")

        # Cleanup
        db.builds.delete_one({"_id": result.inserted_id})
        print(f"🧹 Test document cleaned up\n")

        print("="*60)
        print("✅ All tests passed! MongoDB is ready to use.")
        print("="*60)

        client.close()
        return True

    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
```

**Run test:**
```bash
python test_mongodb_connection.py
```

---

## 📊 Step 5: Populate with Sample Data (Optional)

### **Add More Test Data** (`populate_sample_data.py`):

```python
#!/usr/bin/env python3
"""Populate MongoDB with sample test failure data"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import random

MONGO_URI = "mongodb://localhost:27017"
DATABASE = "ddn_ai_project"

def populate_sample_data(num_builds=10):
    client = MongoClient(MONGO_URI)
    db = client[DATABASE]

    print(f"📊 Populating {num_builds} sample builds...\n")

    job_names = ["DDN-Smoke-Tests", "DDN-Integration-Tests", "DDN-Performance-Tests"]
    test_suites = ["Health_Check", "API_Tests", "Storage_Tests", "Network_Tests"]
    error_types = [
        ("NullPointerException", "CODE_ERROR"),
        ("OutOfMemoryError", "INFRA_ERROR"),
        ("ModuleNotFoundError", "DEPENDENCY_ERROR"),
        ("ConfigurationException", "CONFIG_ERROR"),
        ("AssertionError", "TEST_FAILURE")
    ]

    for i in range(num_builds):
        build_id = f"BUILD_{10000 + i}"
        job_name = random.choice(job_names)
        test_suite = random.choice(test_suites)
        error_type, error_category = random.choice(error_types)
        aging_days = random.randint(1, 15)

        # Build document
        build = {
            "build_id": build_id,
            "job_name": job_name,
            "test_suite": test_suite,
            "status": "FAILURE",
            "build_url": f"https://jenkins.example.com/job/{job_name}/{10000 + i}",
            "timestamp": datetime.utcnow() - timedelta(days=aging_days),
            "repository": "your-org/ddn-repo",
            "branch": "main",
            "commit_sha": f"abc{random.randint(100, 999)}def{random.randint(100, 999)}",
            "error_log": f"[ERROR] {error_type}: Test execution failed",
            "aging_days": aging_days,
            "has_analysis": random.choice([True, False])
        }

        # Insert if not exists
        if not db.builds.find_one({"build_id": build_id}):
            db.builds.insert_one(build)
            print(f"✅ Inserted: {build_id} ({job_name}, {aging_days} days old)")

    print(f"\n✅ Sample data population complete!")
    print(f"📊 Total builds in database: {db.builds.count_documents({})}")

    client.close()

if __name__ == "__main__":
    populate_sample_data(10)
```

**Run:**
```bash
python populate_sample_data.py
```

---

## 🔌 Step 6: Configure n8n Workflows to Use MongoDB

### **Update MongoDB Nodes in Workflows:**

When you import the workflows, configure the MongoDB nodes:

```javascript
// In n8n MongoDB node configuration:
{
  "credentials": {
    "mongoDb": {
      "id": "your-credential-id",
      "name": "MongoDB Production"  // Match the name you created
    }
  }
}
```

**The workflows will automatically use your MongoDB for:**
1. **Workflow 2 (Manual Trigger)**: Query `builds` collection → Get failure data
2. **Workflow 3 (Refinement)**: Query `analysis_solutions` → Get original analysis
3. **All Workflows**: Store results in `analysis_solutions` collection

---

## 📋 Database Schema Reference

### **1. `builds` Collection**
```javascript
{
  "_id": ObjectId("..."),
  "build_id": "12345",                    // Unique build identifier
  "job_name": "DDN-Smoke-Tests",          // Jenkins job name
  "test_suite": "Health_Check_Suite",     // Test suite name
  "status": "FAILURE",                     // Build status
  "build_url": "https://jenkins.../12345", // Jenkins URL
  "timestamp": ISODate("2025-10-10..."),  // Failure timestamp
  "repository": "your-org/ddn-repo",      // GitHub repository
  "branch": "main",                        // Git branch
  "commit_sha": "abc123...",               // Git commit hash
  "error_log": "Error message...",         // First 1000 chars of error
  "aging_days": 7,                         // Days since failure
  "has_analysis": false                    // Analysis completed?
}
```

### **2. `analysis_solutions` Collection**
```javascript
{
  "_id": ObjectId("..."),
  "build_id": "12345",
  "analysis_timestamp": ISODate("..."),
  "analysis_type": "CLAUDE_MCP_ANALYSIS",
  "error_category": "CODE_ERROR",
  "confidence_score": 0.92,
  "root_cause": "NullPointerException...",
  "fix_recommendation": "Add null check...",
  "code_fix": "```java\n+ if (config != null)...",
  "links": {
    "jenkins": "https://...",
    "github_repo": "https://...",
    "github_files": [...]
  },
  "token_usage": 8500,
  "estimated_cost_usd": 0.08,
  "refinement_count": 0,
  "can_refine": true
}
```

### **3. `refinement_history` Collection**
```javascript
{
  "_id": ObjectId("..."),
  "build_id": "12345",
  "refinement_version": 2,
  "user_email": "engineer@example.com",
  "user_feedback": "This is actually a config issue...",
  "timestamp": ISODate("..."),
  "category_before": "CODE_ERROR",
  "category_after": "CONFIG_ERROR",
  "category_changed": true,
  "confidence_before": 0.92,
  "confidence_after": 0.95,
  "cost_usd": 0.12
}
```

---

## 🎯 Quick Command Reference

```bash
# Connect to MongoDB shell
mongosh mongodb://localhost:27017

# Switch to database
use ddn_ai_project

# View all builds
db.builds.find().pretty()

# View builds without analysis
db.builds.find({ has_analysis: false })

# View recent analyses
db.analysis_solutions.find().sort({ analysis_timestamp: -1 }).limit(5)

# Count documents
db.builds.countDocuments()
db.analysis_solutions.countDocuments()

# View refinement history
db.refinement_history.find().pretty()

# Clear test data (CAREFUL!)
db.builds.deleteMany({ build_id: /^TEST_/ })
```

---

## ✅ Verification Checklist

- [ ] MongoDB running on `localhost:27017`
- [ ] Database `ddn_ai_project` created
- [ ] All 5 collections created
- [ ] Indexes created on collections
- [ ] Sample data inserted
- [ ] Connection test passed
- [ ] n8n credentials configured
- [ ] `.env` file updated with MongoDB URI
- [ ] Workflows can connect to MongoDB

---

## 🚀 You're Ready!

Your MongoDB is now configured and ready to use with the DDN AI workflows!

**Next Steps:**
1. ✅ Import workflows into n8n
2. ✅ Configure MongoDB credentials in n8n
3. ✅ Start Python services
4. ✅ Test manual trigger workflow

---

**Questions?** Your MongoDB is ready at `mongodb://localhost:27017/ddn_ai_project`!
