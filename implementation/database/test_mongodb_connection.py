#!/usr/bin/env python3
"""
Test MongoDB Connection for DDN AI Project
Verifies database setup and performs basic CRUD operations
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
import sys

MONGO_URI = "mongodb://localhost:27017"
DATABASE = "ddn_ai_project"

def test_connection():
    print("="*70)
    print("  DDN AI Project - MongoDB Connection Test")
    print("="*70)
    print()

    print("🔍 Testing MongoDB Connection...")
    print(f"   URI: {MONGO_URI}")
    print(f"   Database: {DATABASE}")
    print()

    try:
        # ================================================================
        # 1. CONNECTION TEST
        # ================================================================
        print("1️⃣  Testing connection...")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

        # Ping server
        client.admin.command('ping')
        print("   ✅ MongoDB server is responding")

        # Get server info
        server_info = client.server_info()
        print(f"   ✅ MongoDB version: {server_info['version']}")
        print()

        # ================================================================
        # 2. DATABASE ACCESS
        # ================================================================
        print("2️⃣  Testing database access...")
        db = client[DATABASE]
        print(f"   ✅ Connected to database: {DATABASE}")
        print()

        # ================================================================
        # 3. COLLECTIONS CHECK
        # ================================================================
        print("3️⃣  Checking collections...")
        collections = db.list_collection_names()

        if not collections:
            print("   ⚠️  No collections found!")
            print("   💡 Run setup_mongodb.py to create collections")
            return False

        expected_collections = [
            "builds",
            "console_logs",
            "test_results",
            "analysis_solutions",
            "refinement_history"
        ]

        print(f"   Found {len(collections)} collections:")
        for coll in sorted(collections):
            count = db[coll].count_documents({})
            status = "✅" if coll in expected_collections else "ℹ️"
            print(f"   {status} {coll:25} ({count:3} documents)")

        missing = set(expected_collections) - set(collections)
        if missing:
            print(f"\n   ⚠️  Missing collections: {', '.join(missing)}")
            print("   💡 Run setup_mongodb.py to create them")
        print()

        # ================================================================
        # 4. QUERY TEST
        # ================================================================
        print("4️⃣  Testing query operations...")

        # Test find
        builds = list(db.builds.find().limit(3))
        if builds:
            print(f"   ✅ Found {len(builds)} sample builds:")
            for build in builds:
                print(f"      - {build.get('build_id')}: {build.get('job_name')} ({build.get('status')})")
        else:
            print("   ⚠️  No builds found in database")
            print("   💡 Run setup_mongodb.py or populate_sample_data.py")
        print()

        # ================================================================
        # 5. INSERT TEST
        # ================================================================
        print("5️⃣  Testing insert operation...")

        test_doc = {
            "build_id": f"TEST_CONN_{int(datetime.utcnow().timestamp())}",
            "job_name": "Connection Test",
            "status": "TEST",
            "timestamp": datetime.utcnow(),
            "test_flag": True
        }

        result = db.builds.insert_one(test_doc)
        print(f"   ✅ Insert successful!")
        print(f"      Document ID: {result.inserted_id}")
        print()

        # ================================================================
        # 6. UPDATE TEST
        # ================================================================
        print("6️⃣  Testing update operation...")

        update_result = db.builds.update_one(
            {"_id": result.inserted_id},
            {"$set": {"status": "TEST_UPDATED"}}
        )

        if update_result.modified_count == 1:
            print(f"   ✅ Update successful!")
            print(f"      Modified: {update_result.modified_count} document")
        print()

        # ================================================================
        # 7. DELETE TEST
        # ================================================================
        print("7️⃣  Testing delete operation...")

        delete_result = db.builds.delete_one({"_id": result.inserted_id})

        if delete_result.deleted_count == 1:
            print(f"   ✅ Delete successful!")
            print(f"      Deleted: {delete_result.deleted_count} document")
        print()

        # ================================================================
        # 8. AGGREGATION TEST
        # ================================================================
        print("8️⃣  Testing aggregation pipeline...")

        pipeline = [
            {"$match": {"status": "FAILURE"}},
            {"$group": {
                "_id": "$job_name",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]

        agg_result = list(db.builds.aggregate(pipeline))

        if agg_result:
            print(f"   ✅ Aggregation successful!")
            print(f"      Failures by job:")
            for item in agg_result[:5]:  # Show top 5
                print(f"      - {item['_id']}: {item['count']} failures")
        else:
            print("   ℹ️  No failure data for aggregation")
        print()

        # ================================================================
        # 9. INDEX CHECK
        # ================================================================
        print("9️⃣  Checking indexes...")

        for coll_name in ['builds', 'analysis_solutions']:
            if coll_name in collections:
                indexes = list(db[coll_name].list_indexes())
                print(f"   ✅ {coll_name}: {len(indexes)} indexes")
                for idx in indexes:
                    if idx['name'] != '_id_':
                        keys = ', '.join([f"{k[0]}" for k in idx['key'].items()])
                        print(f"      - {idx['name']}: {keys}")
        print()

        # ================================================================
        # SUMMARY
        # ================================================================
        print("="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print()
        print("📊 Database Statistics:")
        print(f"   Database: {DATABASE}")
        print(f"   Collections: {len(collections)}")

        total_docs = sum(db[coll].count_documents({}) for coll in collections)
        print(f"   Total Documents: {total_docs}")
        print()

        print("🎯 MongoDB is ready for use!")
        print()
        print("Next Steps:")
        print("  1. Configure n8n with MongoDB credentials")
        print("  2. Update .env file: MONGODB_URI=mongodb://localhost:27017/ddn_ai_project")
        print("  3. Start Python services (LangGraph, MCP servers)")
        print("  4. Import and activate n8n workflows")
        print()

        client.close()
        return True

    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed!")
        print(f"   Error: {e}")
        print()
        print("💡 Troubleshooting:")
        print("  1. Ensure MongoDB is running:")
        print("     - Check MongoDB service status")
        print("     - Try: mongosh mongodb://localhost:27017")
        print("  2. Verify connection string:")
        print(f"     - Current: {MONGO_URI}")
        print("  3. Check firewall/network settings")
        print()
        return False

    except Exception as e:
        print(f"❌ Test failed with error!")
        print(f"   Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        return False

if __name__ == "__main__":
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        sys.exit(1)
