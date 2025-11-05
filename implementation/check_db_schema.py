import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=os.getenv('POSTGRES_PORT', '5432'),
    database=os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    user=os.getenv('POSTGRES_USER', 'postgres'),
    password=os.getenv('POSTGRES_PASSWORD', 'Sharu@051220')
)

cursor = conn.cursor()

# Check for ai_analyses table
print("=" * 60)
print("Checking for ai_analyses table...")
print("=" * 60)

cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name = 'ai_analyses'
""")
result = cursor.fetchone()

if result:
    print(f"[OK] Table 'ai_analyses' exists")

    # Get column names
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'ai_analyses'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()

    print(f"\nColumns in ai_analyses table:")
    for col in columns:
        print(f"  - {col[0]} ({col[1]})")

    # Check for validation_status column
    if any(col[0] == 'validation_status' for col in columns):
        print("\n[OK] validation_status column exists")
    else:
        print("\n[MISSING] validation_status column NOT FOUND")
else:
    print("[NOT FOUND] Table 'ai_analyses' does NOT exist")
    print("\nLooking for similar tables...")
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    print("\nExisting tables:")
    for table in tables:
        print(f"  - {table[0]}")

cursor.close()
conn.close()
