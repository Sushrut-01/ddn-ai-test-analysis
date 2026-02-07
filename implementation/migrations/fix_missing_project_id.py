"""
Fix Missing project_id Columns
Add project_id to tables that are missing it
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5434)),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password')
}

TABLES_TO_FIX = [
    'acceptance_tracking',
    'failure_patterns',
    'manual_trigger_log',
    'ai_model_metrics',
    'knowledge_doc_changes'
]

def fix_missing_project_id():
    """Add project_id to tables that are missing it"""
    print("=" * 70)
    print("FIXING MISSING project_id COLUMNS")
    print("=" * 70)

    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.autocommit = False
        cur = conn.cursor()

        for table in TABLES_TO_FIX:
            print(f"\n[*] Processing {table}...")

            # Add project_id column
            print(f"    Adding project_id column...")
            cur.execute(f"""
                ALTER TABLE {table}
                ADD COLUMN IF NOT EXISTS project_id INTEGER
            """)

            # Add foreign key constraint
            print(f"    Adding foreign key constraint...")
            cur.execute(f"""
                ALTER TABLE {table}
                ADD CONSTRAINT fk_{table}_project
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            """)

            # Create index
            print(f"    Creating index...")
            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{table}_project
                ON {table}(project_id)
            """)

            # Set default value to 1 (DDN project) for existing rows
            print(f"    Setting default project_id=1 for existing rows...")
            cur.execute(f"""
                UPDATE {table}
                SET project_id = 1
                WHERE project_id IS NULL
            """)

            # Make NOT NULL
            print(f"    Making project_id NOT NULL...")
            cur.execute(f"""
                ALTER TABLE {table}
                ALTER COLUMN project_id SET NOT NULL
            """)

            print(f"[OK] {table} updated successfully")

        print(f"\n[*] Committing changes...")
        conn.commit()

        print(f"\n" + "=" * 70)
        print("[SUCCESS] All missing project_id columns added")
        print("=" * 70)

        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        if conn:
            conn.rollback()
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_missing_project_id()
    exit(0 if success else 1)
