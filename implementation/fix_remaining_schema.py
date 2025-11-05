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
print("Fixing remaining database schema issues...")
print("=" * 60)

# 1. Add analyzed_at column to failure_analysis table
print("\n[1/3] Checking for analyzed_at column in failure_analysis...")
cursor.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'failure_analysis'
    AND column_name = 'analyzed_at'
""")
result = cursor.fetchone()

if not result:
    print("[MISSING] analyzed_at column not found")
    print("Adding analyzed_at column...")

    cursor.execute("""
        ALTER TABLE failure_analysis
        ADD COLUMN analyzed_at TIMESTAMP DEFAULT NULL
    """)

    # Update existing rows with created_at value (if exists)
    cursor.execute("""
        UPDATE failure_analysis
        SET analyzed_at = created_at
        WHERE analyzed_at IS NULL AND created_at IS NOT NULL
    """)

    print("[OK] analyzed_at column added and populated")
else:
    print("[OK] analyzed_at column already exists")

# 2. Create refinement_history table
print("\n[2/3] Checking for refinement_history table...")
cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name = 'refinement_history'
""")
result = cursor.fetchone()

if not result:
    print("[MISSING] refinement_history table not found")
    print("Creating refinement_history table...")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS refinement_history (
            id SERIAL PRIMARY KEY,
            analysis_id INTEGER NOT NULL REFERENCES failure_analysis(id) ON DELETE CASCADE,
            build_id VARCHAR(255) NOT NULL,

            -- Refinement details
            iteration_number INTEGER NOT NULL DEFAULT 1,
            refinement_reason TEXT,

            -- Changes made
            previous_root_cause TEXT,
            new_root_cause TEXT,
            previous_fix TEXT,
            new_fix TEXT,
            previous_confidence DECIMAL(3,2),
            new_confidence DECIMAL(3,2),
            confidence_improvement DECIMAL(3,2),

            -- Validator feedback
            validator_name VARCHAR(100),
            validator_email VARCHAR(255),
            feedback_text TEXT,

            -- Metadata
            refined_by VARCHAR(50),  -- 'ai' or 'human'
            refinement_cost_usd DECIMAL(10,4),
            processing_time_ms INTEGER,

            -- Status after refinement
            accepted BOOLEAN DEFAULT NULL,

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accepted_at TIMESTAMP,

            -- Constraints
            CHECK (iteration_number > 0),
            CHECK (refined_by IN ('ai', 'human'))
        )
    """)

    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_refinement_history_analysis_id
        ON refinement_history(analysis_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_refinement_history_build_id
        ON refinement_history(build_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_refinement_history_created_at
        ON refinement_history(created_at DESC)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_refinement_history_accepted
        ON refinement_history(accepted)
    """)

    print("[OK] refinement_history table created with indexes")
else:
    print("[OK] refinement_history table already exists")

# 3. Commit changes
print("\n[3/3] Committing changes...")
conn.commit()
print("[OK] All changes committed")

# 4. Verify the fixes
print("\n" + "=" * 60)
print("Verifying fixes...")
print("=" * 60)

# Verify analyzed_at column
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'failure_analysis'
    AND column_name = 'analyzed_at'
""")
result = cursor.fetchone()
if result:
    print(f"[OK] failure_analysis.analyzed_at: {result[1]}")
else:
    print("[ERROR] analyzed_at column still missing!")

# Verify refinement_history table
cursor.execute("""
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name = 'refinement_history'
""")
result = cursor.fetchone()
if result[0] > 0:
    print("[OK] refinement_history table exists")
else:
    print("[ERROR] refinement_history table still missing!")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("[SUCCESS] All database schema fixes complete!")
print("=" * 60)
