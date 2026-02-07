"""
Apply Row-Level Security Migration
Executes 003_enable_row_level_security.sql via psycopg2
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

def apply_rls_migration():
    """Apply RLS migration from SQL file"""
    print("=" * 70)
    print("APPLYING ROW-LEVEL SECURITY MIGRATION")
    print("=" * 70)

    # Read SQL file
    sql_file = os.path.join(os.path.dirname(__file__), '003_enable_row_level_security.sql')

    with open(sql_file, 'r') as f:
        sql_script = f.read()

    print(f"\n[+] Loaded SQL script: {sql_file}")
    print(f"    Length: {len(sql_script)} characters")

    # Connect and execute
    try:
        print(f"\n[*] Connecting to PostgreSQL...")
        print(f"    Host: {POSTGRES_CONFIG['host']}")
        print(f"    Port: {POSTGRES_CONFIG['port']}")
        print(f"    Database: {POSTGRES_CONFIG['database']}")

        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.autocommit = True  # Important for CREATE POLICY
        cur = conn.cursor()

        print(f"\n[SUCCESS] Connected successfully!")

        print(f"\n[*] Executing migration...")
        cur.execute(sql_script)

        print(f"\n[SUCCESS] Migration applied successfully!")

        # Verify RLS is enabled
        print(f"\n[*] Verifying RLS status...")
        cur.execute("""
            SELECT tablename, rowsecurity
            FROM pg_tables t
            JOIN pg_class c ON c.relname = t.tablename
            WHERE schemaname = 'public'
            AND tablename IN (
                'failure_analysis', 'build_metadata', 'test_case_history',
                'user_feedback', 'acceptance_tracking', 'failure_patterns',
                'manual_trigger_log', 'ai_model_metrics', 'knowledge_doc_changes'
            )
            ORDER BY tablename
        """)

        results = cur.fetchall()

        print(f"\n[*] RLS Status:")
        print("-" * 70)
        for table, rls_enabled in results:
            status = "[OK] ENABLED" if rls_enabled else "[FAIL] DISABLED"
            print(f"    {table:30s} {status}")

        enabled_count = sum(1 for _, rls in results if rls)
        print("-" * 70)
        print(f"    Total: {enabled_count}/{len(results)} tables have RLS enabled")

        if enabled_count < len(results):
            print(f"\n[WARNING] Not all tables have RLS enabled!")
            return False

        # Verify functions exist
        print(f"\n[*] Verifying functions...")
        cur.execute("""
            SELECT proname FROM pg_proc
            WHERE proname IN ('set_project_context', 'get_current_project_id')
        """)

        functions = [row[0] for row in cur.fetchall()]
        print(f"    Functions found: {', '.join(functions)}")

        if len(functions) < 2:
            print(f"\n[WARNING] Not all functions created!")
            return False

        print(f"\n" + "=" * 70)
        print("[SUCCESS] RLS MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 70)

        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"\n[ERROR] Error applying migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = apply_rls_migration()
    exit(0 if success else 1)
