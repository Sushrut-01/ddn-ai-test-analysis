"""
MongoDB Collection Setup for Guruttava Project
Date: 2026-01-14
Description: Creates MongoDB collections with indexes for Guruttava project data isolation
"""

import os
import sys
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime

# MongoDB connection configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'ddn_tests')

def setup_mongodb_collections():
    """Create Guruttava MongoDB collections with proper indexes"""
    try:
        # Connect to MongoDB
        print(f"📡 Connecting to MongoDB: {MONGODB_URI}")
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]

        print(f"✅ Connected to database: {MONGODB_DATABASE}")

        # ========================================================================
        # Collection 1: guruttava_test_failures
        # ========================================================================
        print("\n📦 Creating collection: guruttava_test_failures")

        collection_name = "guruttava_test_failures"
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"✅ Created collection: {collection_name}")
        else:
            print(f"ℹ️  Collection {collection_name} already exists")

        # Create indexes
        collection = db[collection_name]

        indexes = [
            ("build_id", ASCENDING),
            ("test_name", ASCENDING),
            ("timestamp", DESCENDING),
            ("error_category", ASCENDING),
            ("project_id", ASCENDING),
            ("analyzed", ASCENDING),
            ("platform", ASCENDING),  # For filtering by Android/iOS/Web
            ("test_suite", ASCENDING),
        ]

        for field, direction in indexes:
            try:
                collection.create_index([(field, direction)])
                print(f"  ✅ Index created: {field}")
            except Exception as e:
                print(f"  ⚠️  Index {field} may already exist: {e}")

        # Compound indexes for common queries
        try:
            collection.create_index([("project_id", ASCENDING), ("build_id", ASCENDING)])
            print(f"  ✅ Compound index created: project_id + build_id")
        except Exception as e:
            print(f"  ⚠️  Compound index may already exist: {e}")

        try:
            collection.create_index([("analyzed", ASCENDING), ("timestamp", DESCENDING)])
            print(f"  ✅ Compound index created: analyzed + timestamp")
        except Exception as e:
            print(f"  ⚠️  Compound index may already exist: {e}")

        # ========================================================================
        # Collection 2: guruttava_build_results
        # ========================================================================
        print("\n📦 Creating collection: guruttava_build_results")

        collection_name = "guruttava_build_results"
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"✅ Created collection: {collection_name}")
        else:
            print(f"ℹ️  Collection {collection_name} already exists")

        collection = db[collection_name]

        indexes = [
            ("job_name", ASCENDING),
            ("timestamp", DESCENDING),
            ("status", ASCENDING),
            ("analyzed", ASCENDING),
            ("project_id", ASCENDING),
            ("platform", ASCENDING),
            ("test_type", ASCENDING),  # Smoke, Regression, etc.
        ]

        for field, direction in indexes:
            try:
                collection.create_index([(field, direction)])
                print(f"  ✅ Index created: {field}")
            except Exception as e:
                print(f"  ⚠️  Index {field} may already exist: {e}")

        # Unique index on build_id
        try:
            collection.create_index([("build_id", ASCENDING)], unique=True)
            print(f"  ✅ Unique index created: build_id")
        except Exception as e:
            print(f"  ⚠️  Unique index may already exist: {e}")

        # Compound indexes
        try:
            collection.create_index([("project_id", ASCENDING), ("status", ASCENDING)])
            print(f"  ✅ Compound index created: project_id + status")
        except Exception as e:
            print(f"  ⚠️  Compound index may already exist: {e}")

        # ========================================================================
        # Collection 3: guruttava_failure_analysis_detailed
        # ========================================================================
        print("\n📦 Creating collection: guruttava_failure_analysis_detailed")

        collection_name = "guruttava_failure_analysis_detailed"
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"✅ Created collection: {collection_name}")
        else:
            print(f"ℹ️  Collection {collection_name} already exists")

        collection = db[collection_name]

        indexes = [
            ("analysis_id", ASCENDING),
            ("project_id", ASCENDING),
            ("timestamp", DESCENDING),
            ("build_id", ASCENDING),
        ]

        for field, direction in indexes:
            try:
                collection.create_index([(field, direction)])
                print(f"  ✅ Index created: {field}")
            except Exception as e:
                print(f"  ⚠️  Index {field} may already exist: {e}")

        # ========================================================================
        # Verify Collections
        # ========================================================================
        print("\n🔍 Verifying Guruttava collections:")

        guruttava_collections = [name for name in db.list_collection_names() if name.startswith('guruttava_')]

        for coll_name in guruttava_collections:
            count = db[coll_name].count_documents({})
            indexes = db[coll_name].list_indexes()
            index_names = [idx['name'] for idx in indexes]
            print(f"  ✅ {coll_name}")
            print(f"     - Documents: {count}")
            print(f"     - Indexes: {len(index_names)} ({', '.join(index_names)})")

        # ========================================================================
        # Insert Sample Document (Optional - for testing)
        # ========================================================================
        print("\n📝 Inserting sample test document (optional):")

        sample_doc = {
            "project_id": 2,  # Guruttava project ID
            "build_id": "SAMPLE-GURUTTAVA-TEST-001",
            "job_name": "Guruttava-Sample-Test",
            "test_name": "Sample Test Failure",
            "test_suite": "Android Login Tests",
            "error_message": "Sample error for testing",
            "error_category": "UNKNOWN",
            "stack_trace": "Sample stack trace",
            "platform": "Android",
            "analyzed": False,
            "timestamp": datetime.utcnow(),
            "metadata": {
                "sample": True,
                "created_by": "migration_script"
            }
        }

        try:
            result = db.guruttava_test_failures.insert_one(sample_doc)
            print(f"  ✅ Sample document inserted with ID: {result.inserted_id}")
            print(f"  ℹ️  You can delete this sample with:")
            print(f"     db.guruttava_test_failures.deleteOne({{build_id: 'SAMPLE-GURUTTAVA-TEST-001'}})")
        except Exception as e:
            print(f"  ⚠️  Could not insert sample: {e}")

        # ========================================================================
        # Summary
        # ========================================================================
        print("\n" + "="*70)
        print("✅ MongoDB Setup Complete for Guruttava Project")
        print("="*70)
        print(f"Database: {MONGODB_DATABASE}")
        print(f"Collections Created: {len(guruttava_collections)}")
        print("\nNext Steps:")
        print("1. Run PostgreSQL migration: 002_add_guruttava_project.sql")
        print("2. Configure Jenkins jobs for Guruttava")
        print("3. Update service APIs with project-aware endpoints")
        print("4. Test end-to-end flow with Robot Framework tests")

        client.close()
        return True

    except Exception as e:
        print(f"\n❌ Error setting up MongoDB collections: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_mongodb_isolation():
    """Verify that DDN and Guruttava collections are properly isolated"""
    try:
        print("\n🔒 Verifying Data Isolation:")

        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]

        # Check DDN collections
        ddn_collections = [name for name in db.list_collection_names() if name.startswith('ddn_')]
        print(f"\nDDN Collections: {len(ddn_collections)}")
        for coll in ddn_collections:
            print(f"  - {coll}")

        # Check Guruttava collections
        guruttava_collections = [name for name in db.list_collection_names() if name.startswith('guruttava_')]
        print(f"\nGuruttava Collections: {len(guruttava_collections)}")
        for coll in guruttava_collections:
            print(f"  - {coll}")

        # Verify no overlap
        if set(ddn_collections).intersection(set(guruttava_collections)):
            print("\n⚠️  WARNING: Collection overlap detected!")
        else:
            print("\n✅ No collection overlap - Data isolation verified")

        client.close()

    except Exception as e:
        print(f"\n❌ Error verifying isolation: {e}")


def cleanup_guruttava_collections():
    """Cleanup function - DANGEROUS! Only use for rollback"""
    print("\n⚠️  WARNING: This will DELETE all Guruttava collections!")
    print("This operation cannot be undone.")

    confirm = input("Type 'DELETE GURUTTAVA' to confirm: ")

    if confirm != "DELETE GURUTTAVA":
        print("❌ Cleanup cancelled")
        return

    try:
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]

        guruttava_collections = [name for name in db.list_collection_names() if name.startswith('guruttava_')]

        for coll_name in guruttava_collections:
            db[coll_name].drop()
            print(f"🗑️  Dropped collection: {coll_name}")

        print("\n✅ Cleanup complete - All Guruttava collections removed")

        client.close()

    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")


if __name__ == "__main__":
    print("="*70)
    print("Guruttava Project - MongoDB Collection Setup")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"MongoDB URI: {MONGODB_URI}")
    print(f"Database: {MONGODB_DATABASE}")
    print("="*70)

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "cleanup":
            cleanup_guruttava_collections()
            sys.exit(0)
        elif sys.argv[1] == "verify":
            verify_mongodb_isolation()
            sys.exit(0)
        elif sys.argv[1] == "help":
            print("\nUsage:")
            print("  python 002_setup_guruttava_mongodb.py          - Setup collections")
            print("  python 002_setup_guruttava_mongodb.py verify   - Verify isolation")
            print("  python 002_setup_guruttava_mongodb.py cleanup  - Delete collections (DANGEROUS)")
            print("  python 002_setup_guruttava_mongodb.py help     - Show this help")
            sys.exit(0)

    # Run setup
    success = setup_mongodb_collections()

    if success:
        verify_mongodb_isolation()
        sys.exit(0)
    else:
        sys.exit(1)
