#!/bin/bash
# Test if MongoDB Listener works in Jenkins environment

echo "========================================="
echo "Testing MongoDB Listener in Jenkins"
echo "========================================="

# Set MongoDB URI like Jenkins does
export MONGODB_URI="mongodb+srv://sushrutnistane097_db_user:Sharu%40051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true&w=majority"
export BUILD_NUMBER="TEST"
export JOB_NAME="test-job"

echo "1. Testing Python MongoDB connection..."
python3 -c "
import os
from pymongo import MongoClient

uri = os.getenv('MONGODB_URI')
print(f'ENV MONGODB_URI exists: {uri is not None}')
print(f'URI length: {len(uri) if uri else 0}')

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    client.server_info()
    print('✓ MongoDB Atlas connection SUCCESS!')
except Exception as e:
    print(f'✗ MongoDB Atlas connection FAILED: {e}')
"

echo ""
echo "2. Testing with load_dotenv()..."
python3 -c "
import os
from dotenv import load_dotenv
from pymongo import MongoClient

print(f'BEFORE load_dotenv(): URI exists = {os.getenv(\"MONGODB_URI\") is not None}')
load_dotenv()  # This might CLEAR the environment variable!
uri = os.getenv('MONGODB_URI')
print(f'AFTER load_dotenv(): URI exists = {uri is not None}')

if uri:
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=10000)
        client.server_info()
        print('✓ Connection works after load_dotenv()')
    except Exception as e:
        print(f'✗ Connection failed after load_dotenv(): {e}')
else:
    print('✗ MONGODB_URI was CLEARED by load_dotenv()!')
"

echo "========================================="
