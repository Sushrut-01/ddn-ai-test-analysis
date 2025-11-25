import os
from pymongo import MongoClient
from datetime import datetime, timedelta

# Connect to MongoDB Atlas
uri = 'mongodb+srv://sushrutnistane097_db_user:Sharu%40051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true&w=majority'
client = MongoClient(uri)
db = client['ddn_tests']
collection = db['test_failures']

print("\n" + "="*50)
print("Checking for Build #37 failures in MongoDB")
print("="*50)

# Check for failures from Build #37 specifically
build37_failures = list(collection.find({'build_number': '37'}).limit(5))
print(f"\nFailures from Build #37: {len(build37_failures)}")

if build37_failures:
    print("\n✓ FOUND Build #37 failures!")
    for failure in build37_failures:
        print(f"  - {failure['test_name']}")
        print(f"    Time: {failure['timestamp']}")
        print(f"    Build: {failure['build_id']}")
else:
    print("\n✗ NO failures from Build #37")
    
# Check for ANY recent failures (last hour)
one_hour_ago = datetime.utcnow() - timedelta(hours=1)
recent = collection.count_documents({'timestamp': {'$gte': one_hour_ago}})
print(f"\nFailures in last hour: {recent}")

# Check total
total = collection.count_documents({})
print(f"Total failures in database: {total}")

client.close()
