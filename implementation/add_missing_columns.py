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
print("Adding missing columns to user_feedback table...")
print("=" * 60)

# Check if validation_status column exists in user_feedback
cursor.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'user_feedback'
    AND column_name = 'validation_status'
""")
result = cursor.fetchone()

if not result:
    print("[MISSING] validation_status column not found in user_feedback")
    print("Adding validation_status column...")

    cursor.execute("""
        ALTER TABLE user_feedback
        ADD COLUMN validation_status VARCHAR(20) DEFAULT 'pending'
    """)

    cursor.execute("""
        ALTER TABLE user_feedback
        ADD CONSTRAINT check_validation_status
        CHECK (validation_status IN ('pending', 'accepted', 'rejected', 'refining', 'refined'))
    """)

    print("[OK] validation_status column added")
else:
    print("[OK] validation_status column already exists")

# Check if feedback_timestamp column exists in user_feedback
cursor.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'user_feedback'
    AND column_name = 'feedback_timestamp'
""")
result = cursor.fetchone()

if not result:
    print("[MISSING] feedback_timestamp column not found in user_feedback")
    print("Adding feedback_timestamp column...")

    cursor.execute("""
        ALTER TABLE user_feedback
        ADD COLUMN feedback_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """)

    print("[OK] feedback_timestamp column added")
else:
    print("[OK] feedback_timestamp column already exists")

# Commit changes
conn.commit()

print("\n[SUCCESS] All missing columns added!")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("Column addition complete!")
print("=" * 60)
