#!/usr/bin/env python3
"""Test PostgreSQL connection on port 5434 (Docker)"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.MASTER')

print("=" * 60)
print("PostgreSQL Port 5434 Connection Test")
print("=" * 60)

# Test 1: External connection to Docker PostgreSQL (port 5434)
print("\n[TEST 1] Testing Docker PostgreSQL (localhost:5434)...")
try:
    conn = psycopg2.connect(
        host='localhost',
        port=5434,
        database='ddn_ai_analysis',
        user='postgres',
        password='password'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print("[PASS] DOCKER PostgreSQL Connected!")
    print("   Version:", version[:50] + "...")
    cursor.close()
    conn.close()
except Exception as e:
    print("[FAIL] DOCKER PostgreSQL:", str(e))

# Test 2: Verify native PostgreSQL still on 5432
print("\n[TEST 2] Testing Native PostgreSQL (localhost:5432)...")
try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='postgres',
        user='postgres',
        password='Sharu@051220'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print("[PASS] NATIVE PostgreSQL Connected!")
    print("   Version:", version[:50] + "...")
    cursor.close()
    conn.close()
except Exception as e:
    print("[FAIL] NATIVE PostgreSQL:", str(e))

# Test 3: Environment variable connection
print("\n[TEST 3] Testing with environment variables...")
try:
    port = int(os.getenv('POSTGRES_PORT', 5434))
    host = os.getenv('POSTGRES_HOST', 'localhost')
    print("   Using:", host + ":" + str(port))

    conn = psycopg2.connect(
        host=host,
        port=port,
        database='ddn_ai_analysis',
        user='postgres',
        password='password'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 'Connection successful!' as message;")
    result = cursor.fetchone()[0]
    print("[PASS] ENV VAR Connection:", result)
    cursor.close()
    conn.close()
except Exception as e:
    print("[FAIL] ENV VAR Connection:", str(e))

print("\n" + "=" * 60)
print("Test Summary:")
print("  Docker PostgreSQL (5434): Expected PASS")
print("  Native PostgreSQL (5432): Expected PASS")
print("  ENV VAR Connection (5434): Expected PASS")
print("=" * 60)
