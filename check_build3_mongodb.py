#!/usr/bin/env python3
from pymongo import MongoClient

uri = 'mongodb+srv://sushrutnistane097_db_user:Sharu%40051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true&w=majority'
client = MongoClient(uri)
db = client.ddn_tests

build3_count = db.test_failures.count_documents({"build_id": "3"})
total_count = db.test_failures.count_documents({})
build3_samples = list(db.test_failures.find({"build_id": "3"}).limit(5))

print(f"✓ Found {build3_count} failures from Build #3")
print(f"✓ Total failures in MongoDB: {total_count}")
print(f"\n📋 Sample failures from Build #3:")
for f in build3_samples:
    print(f"  - {f['test_name']}")
