#!/usr/bin/env python3
"""
MongoDB Atlas Connection Test for DDN AI System

This script tests the connection to MongoDB Atlas and sets up
the required database and collections.
"""

import os
import sys
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

# Try to load dotenv, but continue if not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  Warning: python-dotenv not installed. Using environment variables only.")
    print("   Install with: pip install python-dotenv\n")

def test_mongodb_atlas():
    """Test MongoDB Atlas connection and setup database"""

    print("=" * 60)
    print("MongoDB Atlas Connection Test - DDN AI System")
    print("=" * 60)
    print()

    # Get connection string from .env
    mongodb_uri = os.getenv('MONGODB_URI')
    mongodb_db = os.getenv('MONGODB_DB', 'jenkins_failure_analysis')

    if not mongodb_uri:
        print("❌ ERROR: MONGODB_URI not found in .env file")
        print()
        print("Please add to your .env file:")
        print("MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/")
        print("MONGODB_DB=jenkins_failure_analysis")
        return False

    # Mask password in output
    if '@' in mongodb_uri:
        parts = mongodb_uri.split('@')
        masked_uri = parts[0].split(':')[0] + ':****@' + parts[1]
    else:
        masked_uri = mongodb_uri[:20] + '...'

    print(f"🔗 Connecting to MongoDB Atlas...")
    print(f"📦 Database: {mongodb_db}")
    print(f"🌐 Connection: {masked_uri}")
    print()

    try:
        # Create client with server API
        print("⏳ Creating MongoDB client...")
        client = MongoClient(mongodb_uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)

        # Test connection
        print("⏳ Testing connection (ping)...")
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully!")
        print()

        # Get server info
        server_info = client.server_info()
        print(f"📊 Server Information:")
        print(f"   MongoDB Version: {server_info.get('version', 'Unknown')}")
        print(f"   Max Wire Version: {server_info.get('maxWireVersion', 'Unknown')}")
        print()

        # Get database
        db = client[mongodb_db]

        # List collections
        collections = db.list_collection_names()
        print(f"📂 Collections in database '{mongodb_db}':")
        if collections:
            for col in collections:
                count = db[col].count_documents({})
                print(f"   - {col}: {count} documents")
        else:
            print("   (No collections yet - will be created)")
        print()

        # Create required collections
        required_collections = {
            'builds': 'Build information and metadata',
            'console_logs': 'Jenkins console output logs',
            'test_results': 'Test execution results and failures',
            'analysis_solutions': 'AI analysis and recommendations',
            'refinement_history': 'User feedback and refinement tracking'
        }

        print("📋 Setting up required collections...")
        created_count = 0
        for col_name, description in required_collections.items():
            if col_name not in collections:
                db.create_collection(col_name)
                print(f"   ✅ Created: {col_name}")
                print(f"      ({description})")
                created_count += 1
            else:
                print(f"   ✓ Exists: {col_name}")
        print()

        if created_count > 0:
            print(f"✅ Created {created_count} new collections")
            print()

        # Insert test document
        print("🧪 Testing write operations...")
        test_collection = db['builds']
        test_doc = {
            'test': True,
            'message': 'MongoDB Atlas connection test successful',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'system': 'DDN AI Test Failure Analysis',
            'version': '2.0'
        }

        result = test_collection.insert_one(test_doc)
        print(f"   ✅ Test document inserted with ID: {result.inserted_id}")

        # Read it back
        retrieved = test_collection.find_one({'_id': result.inserted_id})
        print(f"   ✅ Test document retrieved successfully")

        # Clean up test document
        test_collection.delete_one({'_id': result.inserted_id})
        print(f"   🧹 Test document cleaned up")
        print()

        # Create indexes for performance
        print("🔍 Creating indexes for optimal performance...")
        try:
            # Builds collection indexes
            db.builds.create_index('build_id', unique=True)
            db.builds.create_index('timestamp')
            db.builds.create_index('status')
            print("   ✅ Indexes created on 'builds' collection")

            # Test results indexes
            db.test_results.create_index('build_id')
            db.test_results.create_index('test_name')
            print("   ✅ Indexes created on 'test_results' collection")

            # Analysis solutions indexes
            db.analysis_solutions.create_index('build_id', unique=True)
            db.analysis_solutions.create_index('timestamp')
            print("   ✅ Indexes created on 'analysis_solutions' collection")

        except Exception as e:
            print(f"   ⚠️  Index creation warning: {str(e)}")
        print()

        # Insert sample data (optional)
        print("📝 Inserting sample data for testing...")
        sample_build = {
            'build_id': 'SAMPLE_12345',
            'job_name': 'DDN-Smoke-Test',
            'build_number': 12345,
            'status': 'FAILURE',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'duration': 180000,
            'test_results': {
                'total': 100,
                'passed': 98,
                'failed': 2,
                'skipped': 0
            }
        }

        # Check if sample already exists
        existing = db.builds.find_one({'build_id': 'SAMPLE_12345'})
        if not existing:
            db.builds.insert_one(sample_build)
            print("   ✅ Sample build data inserted")
        else:
            print("   ✓ Sample data already exists")
        print()

        # Final statistics
        print("=" * 60)
        print("✅ MongoDB Atlas Setup Complete!")
        print("=" * 60)
        print()
        print("📊 Database Statistics:")
        stats = db.command('dbStats')
        print(f"   Database: {mongodb_db}")
        print(f"   Collections: {stats.get('collections', 0)}")
        print(f"   Objects: {stats.get('objects', 0)}")
        print(f"   Data Size: {stats.get('dataSize', 0) / 1024:.2f} KB")
        print(f"   Storage Size: {stats.get('storageSize', 0) / 1024:.2f} KB")
        print()

        print("🎯 Next Steps:")
        print("   1. Update your services to use MongoDB Atlas")
        print("   2. Start Docker Compose: docker-compose up -d")
        print("   3. Import n8n workflows")
        print("   4. Test the system with manual trigger")
        print()
        print("🌐 View your data at:")
        print("   https://cloud.mongodb.com/")
        print()

        client.close()
        return True

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR connecting to MongoDB Atlas")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        print("🔧 Troubleshooting Steps:")
        print()
        print("1. Check your connection string in .env:")
        print("   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/")
        print()
        print("2. Verify password is URL-encoded:")
        print("   Special characters need encoding:")
        print("   @ → %40, # → %23, ! → %21, etc.")
        print()
        print("3. Check Network Access in MongoDB Atlas:")
        print("   - Go to: Network Access")
        print("   - Add IP: 0.0.0.0/0 (allow from anywhere)")
        print("   - Wait 2-3 minutes for changes to apply")
        print()
        print("4. Verify database user exists:")
        print("   - Go to: Database Access")
        print("   - Check user exists with correct password")
        print("   - User should have 'Read and write' privileges")
        print()
        print("5. Connection string format:")
        print("   mongodb+srv://USER:PASS@cluster.mongodb.net/DATABASE?options")
        print()
        return False

if __name__ == '__main__':
    success = test_mongodb_atlas()
    sys.exit(0 if success else 1)
