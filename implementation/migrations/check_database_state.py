"""
Check Database State
Verify what migrations have been applied
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

def check_database_state():
    """Check current database state"""
    print("=" * 70)
    print("DATABASE STATE CHECK")
    print("=" * 70)

    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        print(f"\n[*] Checking tables...")

        # Check if multi-project tables exist
        cur.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename IN ('projects', 'user_projects', 'project_configurations')
        """)

        multi_project_tables = [row['tablename'] for row in cur.fetchall()]

        if not multi_project_tables:
            print("[WARNING] Multi-project tables DO NOT exist!")
            print("    Need to run: 001_add_multi_project_support.sql")
            return False

        print(f"[OK] Multi-project tables exist: {', '.join(multi_project_tables)}")

        # Check if failure_analysis has project_id
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'failure_analysis'
            AND column_name = 'project_id'
        """)

        if not cur.fetchone():
            print("\n[WARNING] failure_analysis table DOES NOT have project_id column!")
            print("    Need to run: 001_add_multi_project_support.sql")
            return False

        print("[OK] failure_analysis has project_id column")

        # Check data in projects table
        cur.execute("SELECT id, slug, name, status FROM projects")
        projects = cur.fetchall()

        print(f"\n[*] Projects in database: {len(projects)}")
        for proj in projects:
            print(f"    [{proj['id']}] {proj['slug']} - {proj['name']} ({proj['status']})")

        # Check RLS status
        cur.execute("""
            SELECT tablename, rowsecurity
            FROM pg_tables t
            JOIN pg_class c ON c.relname = t.tablename
            WHERE schemaname = 'public'
            AND tablename IN (
                'failure_analysis', 'build_metadata', 'test_case_history'
            )
        """)

        rls_status = cur.fetchall()
        print(f"\n[*] RLS Status:")
        for row in rls_status:
            status = "[ENABLED]" if row['rowsecurity'] else "[DISABLED]"
            print(f"    {row['tablename']:30s} {status}")

        cur.close()
        conn.close()

        print("\n" + "=" * 70)
        print("[OK] Database state check complete")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n[ERROR] Error checking database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_database_state()
    exit(0 if success else 1)
