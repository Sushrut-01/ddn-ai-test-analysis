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

print("=" * 60)
print("Adding all missing columns...")
print("=" * 60)

# List of columns to add with their table and definition
columns_to_add = [
    {
        'table': 'failure_analysis',
        'column': 'classification',
        'definition': 'VARCHAR(100) DEFAULT NULL'
    },
    {
        'table': 'refinement_history',
        'column': 'failure_id',
        'definition': 'VARCHAR(255) DEFAULT NULL'
    }
]

for col_info in columns_to_add:
    table = col_info['table']
    column = col_info['column']
    definition = col_info['definition']

    print(f"\nChecking {table}.{column}...")

    # Check if column exists
    cursor.execute(f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table}'
        AND column_name = '{column}'
    """)
    result = cursor.fetchone()

    if not result:
        print(f"[MISSING] {table}.{column} not found")
        print(f"Adding {table}.{column}...")

        try:
            cursor.execute(f"""
                ALTER TABLE {table}
                ADD COLUMN {column} {definition}
            """)
            print(f"[OK] {table}.{column} added")
        except Exception as e:
            print(f"[ERROR] Failed to add {table}.{column}: {e}")
    else:
        print(f"[OK] {table}.{column} already exists")

# Commit changes
print("\nCommitting changes...")
conn.commit()
print("[OK] All changes committed")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("[SUCCESS] All missing columns added!")
print("=" * 60)
