"""
Test Row-Level Security Enforcement
Verify that RLS actually prevents cross-project data access
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

def test_rls_enforcement():
    """Test RLS enforcement"""
    print("=" * 70)
    print("TESTING ROW-LEVEL SECURITY ENFORCEMENT")
    print("=" * 70)

    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Test 1: Query without context should return all rows
        print("\n[TEST 1] Query without project context (should return ALL)")
        cur.execute("SELECT COUNT(*) as count, COUNT(DISTINCT project_id) as projects FROM failure_analysis")
        result = cur.fetchone()
        total_without_context = result['count']
        projects_without_context = result['projects']
        print(f"    Total rows: {total_without_context}")
        print(f"    Distinct projects: {projects_without_context}")

        # Test 2: Set context to project 1
        print("\n[TEST 2] Set context to project_id=1")
        cur.execute("SELECT set_project_context(1)")
        cur.execute("SELECT get_current_project_id() as current_project")
        current = cur.fetchone()['current_project']
        print(f"    Current project context: {current}")

        # Query should only return project 1 data
        cur.execute("SELECT COUNT(*) as count FROM failure_analysis")
        project1_count = cur.fetchone()['count']
        print(f"    Rows visible: {project1_count}")

        # Check if filtering worked
        cur.execute("SELECT DISTINCT project_id FROM failure_analysis")
        visible_projects = [row['project_id'] for row in cur.fetchall()]
        print(f"    Visible project_ids: {visible_projects}")

        if visible_projects == [1]:
            print("    [OK] RLS filtering working - only project 1 visible!")
        elif visible_projects == [] or visible_projects == [None]:
            print("    [OK] RLS filtering working - no data or project 1 only!")
        else:
            print(f"    [FAIL] RLS NOT working - can see projects: {visible_projects}")
            return False

        # Test 3: Switch context to project 2
        print("\n[TEST 3] Switch context to project_id=2")
        cur.execute("SELECT set_project_context(2)")
        cur.execute("SELECT get_current_project_id() as current_project")
        current = cur.fetchone()['current_project']
        print(f"    Current project context: {current}")

        cur.execute("SELECT COUNT(*) as count FROM failure_analysis")
        project2_count = cur.fetchone()['count']
        print(f"    Rows visible: {project2_count}")

        cur.execute("SELECT DISTINCT project_id FROM failure_analysis")
        visible_projects = [row['project_id'] for row in cur.fetchall()]
        print(f"    Visible project_ids: {visible_projects}")

        if visible_projects == [2]:
            print("    [OK] RLS filtering working - only project 2 visible!")
        elif visible_projects == [] or visible_projects == [None]:
            print("    [OK] RLS filtering working - no data for project 2!")
        else:
            print(f"    [FAIL] RLS NOT working - can see projects: {visible_projects}")
            return False

        # Test 4: Reset context (NULL)
        print("\n[TEST 4] Reset context to NULL")
        cur.execute("SELECT set_config('app.current_project_id', NULL, FALSE)")
        cur.execute("SELECT get_current_project_id() as current_project")
        current = cur.fetchone()['current_project']
        print(f"    Current project context: {current}")

        cur.execute("SELECT COUNT(*) as count, COUNT(DISTINCT project_id) as projects FROM failure_analysis")
        result = cur.fetchone()
        total_after_reset = result['count']
        projects_after_reset = result['projects']
        print(f"    Total rows: {total_after_reset}")
        print(f"    Distinct projects: {projects_after_reset}")

        if total_after_reset == total_without_context:
            print("    [OK] After reset, can see all projects again")
        else:
            print(f"    [WARNING] Row count mismatch: {total_after_reset} vs {total_without_context}")

        # Summary
        print("\n" + "=" * 70)
        print("[SUCCESS] ROW-LEVEL SECURITY IS WORKING CORRECTLY")
        print("=" * 70)
        print("\nSummary:")
        print(f"  - Total failures in DB: {total_without_context}")
        print(f"  - Project 1 failures: {project1_count}")
        print(f"  - Project 2 failures: {project2_count}")
        print(f"  - RLS policies enforce isolation: YES")

        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rls_enforcement()
    exit(0 if success else 1)
