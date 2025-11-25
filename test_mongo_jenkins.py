import os
import sys
from pymongo import MongoClient

uri = os.getenv('MONGODB_URI', 'NOT_SET')
print(f'MONGODB_URI length: {len(uri)}')
print(f'MONGODB_URI starts with: {uri[:50]}...')

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.server_info()
    print('SUCCESS: Connected to MongoDB Atlas!')
    db = client['ddn_tests']
    count = db['test_failures'].count_documents({})
    print(f'Found {count} failures in database')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
