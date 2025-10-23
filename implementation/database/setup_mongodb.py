#!/usr/bin/env python3
"""
MongoDB Setup Script for DDN AI Project
Creates database, collections, indexes, and sample data
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime

# Connection Configuration
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "ddn_ai_project"

def setup_mongodb():
    print("="*70)
    print("  DDN AI Project - MongoDB Setup")
    print("="*70)
    print()

    print("🔌 Connecting to MongoDB...")
    print(f"   URI: {MONGO_URI}")
    print(f"   Database: {DATABASE_NAME}")
    print()

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        print("✅ Connected successfully!\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nPlease ensure MongoDB is running:")
        print("  - Check if MongoDB service is active")
        print("  - Verify connection string: mongodb://localhost:27017")
        return False

    db = client[DATABASE_NAME]

    # ================================================================
    # 1. BUILDS COLLECTION
    # ================================================================
    print("📦 Setting up 'builds' collection...")

    builds = db.builds

    # Create indexes
    builds.create_index([("build_id", ASCENDING)], unique=True)
    builds.create_index([("timestamp", DESCENDING)])
    builds.create_index([("status", ASCENDING)])
    builds.create_index([("job_name", ASCENDING)])
    builds.create_index([("test_suite", ASCENDING)])
    builds.create_index([("aging_days", DESCENDING)])
    builds.create_index([("has_analysis", ASCENDING)])

    print("  ✅ Created indexes:")
    print("     - build_id (unique)")
    print("     - timestamp, status, job_name, test_suite")
    print("     - aging_days, has_analysis")

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
        "error_log": """[ERROR] Test failed: test_storage_initialization
java.lang.NullPointerException: Cannot invoke "StorageConfig.getPath()" because "this.storageConfig" is null
    at com.ddn.storage.DDNStorage.initialize(DDNStorage.java:127)
    at com.ddn.tests.HealthCheckTest.testStorageInit(HealthCheckTest.java:45)""",
        "aging_days": 5,
        "has_analysis": False
    }

    if not builds.find_one({"build_id": "SAMPLE_12345"}):
        builds.insert_one(sample_build)
        print("  ✅ Inserted sample build (SAMPLE_12345)")
    else:
        print("  ℹ️  Sample build already exists")

    # ================================================================
    # 2. CONSOLE_LOGS COLLECTION
    # ================================================================
    print("\n📝 Setting up 'console_logs' collection...")

    console_logs = db.console_logs

    # Create indexes
    console_logs.create_index([("build_id", ASCENDING)])
    console_logs.create_index([("timestamp", DESCENDING)])

    print("  ✅ Created indexes: build_id, timestamp")

    # Insert sample data
    sample_log = {
        "build_id": "SAMPLE_12345",
        "full_log": "[BUILD LOG START]\nStarting test execution...\n[Full console output would be here with 1000s of lines]\n[BUILD LOG END]",
        "stack_trace": """java.lang.NullPointerException: Cannot invoke "StorageConfig.getPath()" because "this.storageConfig" is null
    at com.ddn.storage.DDNStorage.initialize(DDNStorage.java:127)
    at com.ddn.storage.DDNStorage.<init>(DDNStorage.java:45)
    at com.ddn.tests.HealthCheckTest.setUp(HealthCheckTest.java:30)
    at com.ddn.tests.HealthCheckTest.testStorageInit(HealthCheckTest.java:45)""",
        "error_count": 1,
        "warning_count": 5,
        "timestamp": datetime.utcnow()
    }

    if not console_logs.find_one({"build_id": "SAMPLE_12345"}):
        console_logs.insert_one(sample_log)
        print("  ✅ Inserted sample console log")
    else:
        print("  ℹ️  Sample console log already exists")

    # ================================================================
    # 3. TEST_RESULTS COLLECTION
    # ================================================================
    print("\n🧪 Setting up 'test_results' collection...")

    test_results = db.test_results

    # Create indexes
    test_results.create_index([("build_id", ASCENDING)])
    test_results.create_index([("timestamp", DESCENDING)])

    print("  ✅ Created indexes: build_id, timestamp")

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
        print("  ✅ Inserted sample test results")
    else:
        print("  ℹ️  Sample test results already exists")

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
    analysis_solutions.create_index([("analysis_type", ASCENDING)])

    print("  ✅ Created indexes:")
    print("     - build_id (unique)")
    print("     - analysis_timestamp, error_category")
    print("     - confidence_score, analysis_type")

    # ================================================================
    # 5. REFINEMENT_HISTORY COLLECTION
    # ================================================================
    print("\n🔄 Setting up 'refinement_history' collection...")

    refinement_history = db.refinement_history

    # Create indexes
    refinement_history.create_index([("build_id", ASCENDING)])
    refinement_history.create_index([("timestamp", DESCENDING)])
    refinement_history.create_index([("user_email", ASCENDING)])
    refinement_history.create_index([("category_changed", ASCENDING)])

    print("  ✅ Created indexes:")
    print("     - build_id, timestamp")
    print("     - user_email, category_changed")

    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "="*70)
    print("✅ MongoDB Setup Complete!")
    print("="*70)
    print(f"\n📊 Database: {DATABASE_NAME}")
    print(f"📍 Connection: {MONGO_URI}")
    print(f"\n📦 Collections Created:")

    collections_info = []
    for collection_name in sorted(db.list_collection_names()):
        count = db[collection_name].count_documents({})
        collections_info.append((collection_name, count))
        print(f"  ✅ {collection_name:25} ({count:3} documents)")

    print("\n🎯 Next Steps:")
    print("  1. Update .env file with MongoDB connection string")
    print("  2. Configure n8n workflows with MongoDB credentials")
    print("  3. (Optional) Run populate_sample_data.py for more test data")
    print("  4. Start Python services (LangGraph, MCP servers)")
    print("  5. Test workflows with sample data")

    print("\n📝 Connection String for .env:")
    print(f"  MONGODB_URI={MONGO_URI}/{DATABASE_NAME}")

    print("\n📝 Connection String for n8n:")
    print(f"  {MONGO_URI}/{DATABASE_NAME}")

    print("\n💡 Quick Test Commands:")
    print(f"  mongosh {MONGO_URI}")
    print(f"  use {DATABASE_NAME}")
    print(f"  db.builds.find().pretty()")

    client.close()
    print("\n✅ Setup complete! MongoDB is ready to use.\n")
    return True

if __name__ == "__main__":
    try:
        success = setup_mongodb()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
