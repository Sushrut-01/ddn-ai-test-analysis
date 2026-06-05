#!/usr/bin/env python3
import os
import sys

# Exact same environment as Build #37
os.environ['MONGODB_URI'] = 'mongodb+srv://sushrutnistane097_db_user:Sharu%40051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true&w=majority'
os.environ['BUILD_NUMBER'] = '37'
os.environ['JOB_NAME'] = 'DDN-Nightly-Tests'

print("=" * 50)
print("Testing MongoDB Listener in Build #37 environment")
print("=" * 50)

print(f"\n1. Environment check:")
print(f"   MONGODB_URI set: {os.getenv('MONGODB_URI') is not None}")
print(f"   URI length: {len(os.getenv('MONGODB_URI', ''))}")
print(f"   Has %40: {'%40' in os.getenv('MONGODB_URI', '')}")

sys.path.insert(0, 'implementation')

print(f"\n2. Importing listener...")
try:
    from mongodb_robot_listener import MongoDBListener
    print("   ✓ Import successful")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

print(f"\n3. Creating listener instance...")
try:
    listener = MongoDBListener()
    print("   ✓ Listener created")
except Exception as e:
    print(f"   ✗ Listener creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n4. Checking connection:")
print(f"   Client exists: {listener.client is not None}")

if listener.client:
    print(f"   ✓ MongoDB connected!")
    print(f"   Database: {listener.mongodb_db}")
    count = listener.collection.count_documents({})
    print(f"   Current failures: {count}")
    print(f"\n🎉 SUCCESS! Listener working in Build #37 environment!")
else:
    print(f"   ✗ Client is None - connection failed")
    print(f"\n❌ FAILED: MongoDB connection not established")
