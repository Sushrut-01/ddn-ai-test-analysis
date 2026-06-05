"""
Verify all tables have project_id column
"""

import psycopg2
from psycopg2.extras import RealDictCursor
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

TABLES_NEED_PROJECT_ID = [
    'failure_analysis',
    'build_metadata',
    'test_case_history',
    'user_feedback',
    'acceptance_tracking',
    'failure_patterns',
    'manual_trigger_log',
    'ai_model_metrics',
    'knowledge_doc_changes'
]

def verify_project_id_columns():
    """Verify project_id exists on all tables"""
    print("=" * 70)
    print("VERIFYING project_id COLUMNS")
    print("=" * 70)

    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        missing_tables = []

        for table in TABLES_NEED_PROJECT_ID:
            cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
                AND column_name = 'project_id'
            """, (table,))

            result = cur.fetchone()

            if result:
                print(f"[OK] {table:30s} has project_id")
            else:
                # Check if table exists
                cur.execute("""
                    SELECT tablename FROM pg_tables
                    WHERE schemaname = 'public'
                    AND tablename = %s
                """, (table,))

                if cur.fetchone():
                    print(f"[MISSING] {table:30s} EXISTS but NO project_id column!")
                    missing_tables.append(table)
                else:
                    print(f"[SKIP] {table:30s} table does not exist")

        cur.close()
        conn.close()

        print("\n" + "=" * 70)
        if missing_tables:
            print(f"[ACTION REQUIRED] {len(missing_tables)} tables need project_id column:")
            for table in missing_tables:
                print(f"  - {table}")
            print("\nRun: 001_add_multi_project_support.sql")
            return False
        else:
            print("[OK] All tables have project_id column")
            return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_project_id_columns()
    exit(0 if success else 1)
