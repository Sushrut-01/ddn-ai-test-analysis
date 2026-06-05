#!/usr/bin/env python3
import os
import sys

# Set environment like Jenkins
os.environ['MONGODB_URI'] = 'mongodb+srv://sushrutnistane097_db_user:Sharu@051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true&w=majority'
os.environ['BUILD_NUMBER'] = 'TEST'
os.environ['JOB_NAME'] = 'test-job'

# Add implementation to path
sys.path.insert(0, 'implementation')

print("Testing MongoDB Listener initialization...")
print(f"MONGODB_URI set: {os.getenv('MONGODB_URI') is not None}")
print(f"URI length: {len(os.getenv('MONGODB_URI', ''))}")

try:
    from mongodb_robot_listener import MongoDBListener
    print("✓ Listener module imported successfully")
    
    listener = MongoDBListener()
    print(f"✓ Listener initialized")
    print(f"✓ Client connected: {listener.client is not None}")
    
    if listener.client:
        print(f"✓ Database: {listener.mongodb_db}")
        print(f"✓ Collection: test_failures")
        count = listener.collection.count_documents({})
        print(f"✓ Current failure count: {count}")
        print("\n🎉 SUCCESS: MongoDB Listener works in Jenkins!")
    else:
        print("\n✗ FAILED: Listener client is None")
        
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
