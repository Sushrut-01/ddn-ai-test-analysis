#!/usr/bin/env python3
"""Test MongoDB Atlas Connection"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os

# Replace with your connection string
ATLAS_URI = "mongodb+srv://ddn_admin:YOUR_PASSWORD@ddn-ai-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority"
DATABASE = "ddn_ai_project"

def test_atlas():
    print("🔍 Testing MongoDB Atlas Connection...")
    print()

    if "YOUR_PASSWORD" in ATLAS_URI:
        print("❌ Please update ATLAS_URI in the script!")
        return False

    try:
        # Connect
        client = MongoClient(ATLAS_URI, serverSelectionTimeoutMS=10000)

        # Test connection
        client.admin.command('ping')
        print("✅ Atlas connection successful!")

        # Get database
        db = client[DATABASE]

        # List collections
        collections = db.list_collection_names()
        print(f"\n📦 Collections in '{DATABASE}':")
        for coll in collections:
            count = db[coll].count_documents({})
            print(f"  ✅ {coll}: {count} documents")

        # Test query
        sample = db.builds.find_one()
        if sample:
            print(f"\n📊 Sample build: {sample.get('build_id')}")

        print("\n✅ All tests passed!")

        client.close()
        return True

    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check connection string")
        print("  2. Verify password is correct")
        print("  3. Whitelist your IP address")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_atlas()
    exit(0 if success else 1)
