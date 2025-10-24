"""
Test PostgreSQL Connection
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', 5432)
POSTGRES_DB = os.getenv('POSTGRES_DB', 'ddn_ai_analysis')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')

print("Testing PostgreSQL Connection...")
print(f"Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
print(f"Database: {POSTGRES_DB}")
print(f"User: {POSTGRES_USER}")
print()

try:
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB
    )

    cursor = conn.cursor()
    cursor.execute("SELECT version()")
    version = cursor.fetchone()

    print("✅ SUCCESS: Connected to PostgreSQL!")
    print(f"Version: {version[0]}")
    print()

    # Test query
    cursor.execute("SELECT COUNT(*) FROM failure_analysis")
    count = cursor.fetchone()[0]
    print(f"✅ failure_analysis table has {count} records")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ ERROR: {e}")
    exit(1)
