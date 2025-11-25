#!/usr/bin/env python3
"""Check LOCAL Docker MongoDB"""
from pymongo import MongoClient

# Connect to LOCAL Docker MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['ddn_tests']
collection = db['test_failures']

total = collection.count_documents({})
print(f"Total Failures in Docker MongoDB: {total}")

if total > 0:
    recent = list(collection.find().sort('timestamp', -1).limit(3))
    print("\nLatest 3 failures:")
    for i, f in enumerate(recent, 1):
        print(f"  {i}. {f.get('test_name', 'Unknown')[:50]}")
        print(f"     Time: {f.get('timestamp', 'Unknown')}")
        print(f"     Suite: {f.get('suite_name', 'N/A')}")

client.close()
