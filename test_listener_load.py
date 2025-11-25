#!/usr/bin/env python3
import sys
import os

os.environ["MONGODB_URI"] = "mongodb+srv://sushrutnistane097_db_user:Sharu%40051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true&w=majority"

try:
    from implementation.mongodb_robot_listener import MongoDBListener
    listener = MongoDBListener()
    print("✓✓✓ SUCCESS: Listener initialized!")
    print(f"  Client exists: {listener.client is not None}")
    print(f"  Database: {listener.db.name if listener.client else 'None'}")
    print(f"  Collection: {listener.collection.name if listener.client else 'None'}")
except Exception as e:
    print(f"✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
