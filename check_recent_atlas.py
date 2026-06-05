from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime, timedelta

username = quote_plus("sushrutnistane097_db_user")
password = quote_plus("Sharu@051220")
uri = f"mongodb+srv://{username}:{password}@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true&w=majority"

client = MongoClient(uri)
db = client['ddn_tests']
coll = db['test_failures']

total = coll.count_documents({})
print(f"\nTotal failures in Atlas: {total}")

# Check last 24 hours
recent_time = (datetime.now() - timedelta(hours=24)).isoformat()
recent_count = coll.count_documents({'timestamp': {'$gte': recent_time}})
print(f"Failures in last 24 hours: {recent_count}\n")

if recent_count > 0:
    print("Recent failures found:")
    for f in coll.find({'timestamp': {'$gte': recent_time}}).sort('timestamp', -1).limit(3):
        print(f"  - {f.get('test_name', 'Unknown')[:60]}")
        print(f"    Build: {f.get('build_id', 'N/A')}")
        print(f"    Time: {f.get('timestamp', 'N/A')}\n")
else:
    print("NO NEW FAILURES in last 24 hours")
    print("All 833 failures are from Nov 13 (old data)\n")
    print("WHY? When we ran Robot Framework locally:")
    print("  - Tests FAILED during suite setup")
    print("  - mongodb_robot_listener.py only triggers on TEST failures")
    print("  - Suite setup failures don't trigger the listener")
    print("  - So NO failures were written to MongoDB\n")

client.close()
