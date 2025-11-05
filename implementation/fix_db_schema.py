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
print("Checking for acceptance_tracking table...")
print("=" * 60)

# Check if acceptance_tracking table exists
cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name = 'acceptance_tracking'
""")
result = cursor.fetchone()

if not result:
    print("[MISSING] acceptance_tracking table NOT FOUND")
    print("\nCreating acceptance_tracking table...")

    # Create the acceptance_tracking table from schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS acceptance_tracking (
            id SERIAL PRIMARY KEY,
            analysis_id INTEGER NOT NULL REFERENCES failure_analysis(id) ON DELETE CASCADE,
            build_id VARCHAR(255) NOT NULL,

            -- Validation status tracking
            validation_status VARCHAR(20) NOT NULL DEFAULT 'pending',
            refinement_count INTEGER DEFAULT 0,
            final_acceptance BOOLEAN DEFAULT NULL,

            -- Validator information
            validator_name VARCHAR(100),
            validator_email VARCHAR(255),

            -- Feedback details
            feedback_comment TEXT,

            -- Refinement tracking
            previous_analysis_id INTEGER REFERENCES failure_analysis(id),
            confidence_improvement DECIMAL(3,2),

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            validated_at TIMESTAMP,

            -- Constraints
            CHECK (validation_status IN ('pending', 'accepted', 'rejected', 'refining', 'refined')),
            CHECK (refinement_count >= 0)
        )
    """)

    print("[OK] acceptance_tracking table created")

    # Create indexes
    print("Creating indexes...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_acceptance_tracking_analysis_id ON acceptance_tracking(analysis_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_acceptance_tracking_build_id ON acceptance_tracking(build_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_acceptance_tracking_validation_status ON acceptance_tracking(validation_status)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_acceptance_tracking_final_acceptance ON acceptance_tracking(final_acceptance)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_acceptance_tracking_created_at ON acceptance_tracking(created_at DESC)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_acceptance_tracking_validator ON acceptance_tracking(validator_email)
    """)

    print("[OK] Indexes created")

    # Create trigger
    print("Creating trigger...")
    cursor.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)

    cursor.execute("""
        DROP TRIGGER IF EXISTS update_acceptance_tracking_updated_at ON acceptance_tracking
    """)

    cursor.execute("""
        CREATE TRIGGER update_acceptance_tracking_updated_at
            BEFORE UPDATE ON acceptance_tracking
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column()
    """)

    print("[OK] Trigger created")

    # Commit changes
    conn.commit()
    print("\n[SUCCESS] Database schema fixed!")

else:
    print("[OK] acceptance_tracking table exists")

    # Check for validation_status column
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'acceptance_tracking'
        AND column_name = 'validation_status'
    """)
    col_result = cursor.fetchone()

    if col_result:
        print("[OK] validation_status column exists")
    else:
        print("[MISSING] validation_status column NOT FOUND - THIS SHOULD NOT HAPPEN")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("Schema check complete!")
print("=" * 60)
