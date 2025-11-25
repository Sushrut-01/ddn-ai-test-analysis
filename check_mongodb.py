#!/usr/bin/env python3
"""Check MongoDB database status and recent failures"""

import pymongo
from datetime import datetime
from urllib.parse import quote_plus

# Connect to MongoDB
username = quote_plus("sushrutnistane097_db_user")
password = quote_plus("Sharu@051220")
MONGODB_URI = f"mongodb+srv://{username}:{password}@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true&w=majority"

try:
    client = pymongo.MongoClient(MONGODB_URI)
    db = client['ddn_tests']
    collection = db['test_failures']
    
    print("\n🔍 MongoDB Database Status")
    print("=" * 70)
    
    # Get total count
    total = collection.count_documents({})
    print(f"\n✅ MongoDB Connection: SUCCESS")
    print(f"📊 Total Failures in Database: {total}")
    
    # Get latest failures
    print(f"\n📋 Latest 5 Failures:")
    print("━" * 70)
    
    failures = list(collection.find({}).sort('timestamp', -1).limit(5))
    
    for i, f in enumerate(failures, 1):
        suite = f.get('suite_name', 'N/A')
        test = f.get('test_name', 'Unknown')[:60]
        timestamp = f.get('timestamp', 'Unknown')
        build_id = f.get('build_id', 'N/A')
        pass_count = f.get('pass_count', '?')
        fail_count = f.get('fail_count', '?')
        total_count = f.get('total_count', '?')
        
        print(f"\n{i}. Test: {test}")
        print(f"   Suite: {suite}")
        print(f"   Build ID: {build_id}")
        print(f"   Counts: Pass={pass_count}, Fail={fail_count}, Total={total_count}")
        print(f"   Time: {timestamp}")
    
    print("\n" + "━" * 70)
    
    # Check metadata coverage
    has_suite = collection.count_documents({'suite_name': {'$exists': True, '$ne': None}})
    no_suite = total - has_suite
    
    print(f"\n📈 Metadata Coverage:")
    print(f"   ✅ Failures WITH suite_name: {has_suite}")
    print(f"   ❌ Failures WITHOUT suite_name: {no_suite}")
    
    if total > 0:
        percentage = (has_suite / total * 100)
        print(f"   📊 Percentage with metadata: {percentage:.1f}%")
    
    # Check recent failures (last 24 hours)
    from datetime import timedelta
    recent_date = (datetime.now() - timedelta(days=1)).isoformat()
    recent_count = collection.count_documents({'timestamp': {'$gte': recent_date}})
    print(f"\n📅 Failures in Last 24 Hours: {recent_count}")
    
    print("\n" + "=" * 70)
    print("\n💡 Status: Database is ready!")
    print("   Waiting for Jenkins build to add new Robot Framework failures.\n")
    
    client.close()
    
except Exception as e:
    print(f"\n❌ MongoDB Connection Error: {e}\n")
