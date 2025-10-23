#!/usr/bin/env python3
"""
MongoDB Atlas Setup for DDN AI Project
Creates database and collections in Atlas cloud
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
import os

# ============================================================================
# CONFIGURATION - UPDATE THESE!
# ============================================================================

# Replace with your actual Atlas connection string
ATLAS_URI = "mongodb+srv://ddn_admin:YOUR_PASSWORD@ddn-ai-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority"

# Or use environment variable
# ATLAS_URI = os.getenv("MONGODB_ATLAS_URI")

DATABASE_NAME = "ddn_ai_project"

# ============================================================================

def setup_atlas():
    print("="*70)
    print("  DDN AI Project - MongoDB Atlas Setup")
    print("="*70)
    print()

    if "YOUR_PASSWORD" in ATLAS_URI or "xxxxx" in ATLAS_URI:
        print("❌ ERROR: Please update ATLAS_URI with your actual connection string!")
        print()
        print("Get it from:")
        print("1. MongoDB Atlas → Clusters → Connect")
        print("2. Choose 'Connect your application'")
        print("3. Copy connection string")
        print("4. Replace <password> with your actual password")
        print()
        return False

    print("🔌 Connecting to MongoDB Atlas...")
    print(f"   Database: {DATABASE_NAME}")
    print()

    try:
        # Connect to Atlas
        client = MongoClient(ATLAS_URI, serverSelectionTimeoutMS=10000)

        # Test connection
        client.admin.command('ping')
        print("✅ Connected to Atlas successfully!")
        print()

        # Get database
        db = client[DATABASE_NAME]

        # Get cluster info
        server_info = client.server_info()
        print(f"   MongoDB Version: {server_info.get('version', 'Unknown')}")
        print()

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
        builds.create_index([("aging_days", DESCENDING)])

        print("  ✅ Created indexes")

        # Sample data
        sample_build = {
            "build_id": "ATLAS_SAMPLE_12345",
            "job_name": "DDN-Smoke-Tests",
            "test_suite": "Health_Check_Suite",
            "status": "FAILURE",
            "build_url": "https://jenkins.example.com/job/12345",
            "timestamp": datetime.utcnow(),
            "repository": "your-org/ddn-repo",
            "branch": "main",
            "commit_sha": "abc123def456",
            "error_log": "NullPointerException at DDNStorage.java:127",
            "aging_days": 5,
            "has_analysis": False
        }

        if not builds.find_one({"build_id": "ATLAS_SAMPLE_12345"}):
            builds.insert_one(sample_build)
            print("  ✅ Inserted sample build")

        # ================================================================
        # 2. OTHER COLLECTIONS
        # ================================================================
        print("\n📝 Setting up other collections...")

        # Console logs
        db.console_logs.create_index([("build_id", ASCENDING)])

        # Test results
        db.test_results.create_index([("build_id", ASCENDING)])

        # Analysis solutions
        db.analysis_solutions.create_index([("build_id", ASCENDING)], unique=True)
        db.analysis_solutions.create_index([("analysis_timestamp", DESCENDING)])

        # Refinement history
        db.refinement_history.create_index([("build_id", ASCENDING)])

        print("  ✅ All collections configured")

        # ================================================================
        # SUMMARY
        # ================================================================
        print("\n" + "="*70)
        print("✅ MongoDB Atlas Setup Complete!")
        print("="*70)
        print()
        print(f"📊 Database: {DATABASE_NAME}")
        print(f"📍 Atlas Cluster: Connected")
        print()
        print("📦 Collections Created:")

        for coll_name in sorted(db.list_collection_names()):
            count = db[coll_name].count_documents({})
            print(f"  ✅ {coll_name:25} ({count} documents)")

        print()
        print("🎯 Next Steps:")
        print("  1. Update .env file with Atlas connection string")
        print("  2. Configure n8n with Atlas credentials")
        print("  3. Test connection with: python test_mongodb_atlas.py")
        print()
        print("📝 Connection String for .env:")
        print(f"  MONGODB_ATLAS_URI={ATLAS_URI}")
        print()

        client.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check connection string is correct")
        print("  2. Replace <password> with actual password")
        print("  3. Verify IP address is whitelisted")
        print("  4. Check database user has correct permissions")
        print()
        return False

if __name__ == "__main__":
    success = setup_atlas()
    exit(0 if success else 1)
