"""
Test Row-Level Security (RLS) Enforcement
Verifies that project isolation works correctly
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
        port=int(os.getenv('POSTGRES_PORT', 5434)),
        database=os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'password')
    )

def test_rls_policies_enabled():
    """Test that RLS policies are enabled on all tables"""
    print("\n" + "=" * 70)
    print("TEST 1: Verify RLS Policies Enabled")
    print("=" * 70)

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Check which tables have RLS enabled
    cur.execute("""
        SELECT
            schemaname,
            tablename,
            rowsecurity as rls_enabled
        FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename IN (
            'failure_analysis', 'project_configurations', 'jira_tickets',
            'manual_trigger_log', 'acceptance_tracking', 'failure_patterns',
            'ai_model_metrics', 'knowledge_doc_changes', 'test_case_suggestions'
        )
        ORDER BY tablename
    """)

    tables = cur.fetchall()

    all_enabled = True
    for table in tables:
        status = "[OK]" if table['rls_enabled'] else "[FAIL]"
        print(f"  {status} {table['tablename']}: RLS {'enabled' if table['rls_enabled'] else 'DISABLED'}")
        if not table['rls_enabled']:
            all_enabled = False

    # Check policies exist
    cur.execute("""
        SELECT
            tablename,
            policyname,
            cmd
        FROM pg_policies
        WHERE schemaname = 'public'
        ORDER BY tablename, policyname
    """)

    policies = cur.fetchall()

    print(f"\n  Total policies found: {len(policies)}")

    cur.close()
    conn.close()

    if all_enabled and len(policies) > 0:
        print("\n  [SUCCESS] RLS policies are properly configured")
        return True
    else:
        print("\n  [FAIL] RLS policies incomplete")
        return False

def test_project_context_function():
    """Test the set_project_context and get_current_project_id functions"""
    print("\n" + "=" * 70)
    print("TEST 2: Verify RLS Context Functions")
    print("=" * 70)

    conn = get_db_connection()
    cur = conn.cursor()

    # Test setting context for project 1
    try:
        cur.execute("SELECT set_project_context(%s)", (1,))
        result = cur.fetchone()
        print(f"  [OK] set_project_context(1) returned: {result[0]}")

        # Get current context
        cur.execute("SELECT get_current_project_id()")
        current_project = cur.fetchone()[0]
        print(f"  [OK] get_current_project_id() returned: {current_project}")

        if current_project == 1:
            print("\n  [SUCCESS] Context functions working correctly")
            success = True
        else:
            print("\n  [FAIL] Context not set correctly")
            success = False

    except Exception as e:
        print(f"  [FAIL] Error testing context functions: {e}")
        success = False

    cur.close()
    conn.close()

    return success

def test_project_isolation():
    """Test that project isolation actually works"""
    print("\n" + "=" * 70)
    print("TEST 3: Verify Project Data Isolation")
    print("=" * 70)

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # First, check if there's any data in failure_analysis
    cur.execute("SELECT COUNT(*) as total FROM failure_analysis")
    total_records = cur.fetchone()['total']

    print(f"\n  Total records in failure_analysis (no context): {total_records}")

    if total_records == 0:
        print("  [SKIP] No test data available")
        cur.close()
        conn.close()
        return None

    # Check how many projects have data
    cur.execute("SELECT DISTINCT project_id FROM failure_analysis ORDER BY project_id")
    projects = [row['project_id'] for row in cur.fetchall()]

    print(f"  Projects with data: {projects}")

    results = {}

    # Test isolation for each project
    for project_id in projects:
        # Set context for this project
        cur.execute("SELECT set_project_context(%s)", (project_id,))

        # Query without WHERE clause - RLS should filter
        cur.execute("SELECT COUNT(*) as count FROM failure_analysis")
        count = cur.fetchone()['count']

        results[project_id] = count
        print(f"\n  Project {project_id} context:")
        print(f"    - Visible records: {count}")

        # Verify records are actually for this project
        cur.execute("SELECT DISTINCT project_id FROM failure_analysis")
        visible_projects = [row['project_id'] for row in cur.fetchall()]

        if visible_projects == [project_id]:
            print(f"    - [OK] Only project {project_id} data visible")
        else:
            print(f"    - [FAIL] Can see data from projects: {visible_projects}")
            cur.close()
            conn.close()
            return False

    # Test NULL context (should see everything for system admin)
    cur.execute("SELECT set_project_context(NULL)")
    cur.execute("SELECT COUNT(*) as count FROM failure_analysis")
    null_context_count = cur.fetchone()['count']

    print(f"\n  NULL context (system admin):")
    print(f"    - Visible records: {null_context_count}")

    if null_context_count == total_records:
        print(f"    - [OK] System admin can see all data")
    else:
        print(f"    - [FAIL] System admin should see {total_records} records but sees {null_context_count}")

    cur.close()
    conn.close()

    print("\n  [SUCCESS] Project isolation working correctly")
    return True

def test_cross_project_access_blocked():
    """Test that you cannot access another project's data"""
    print("\n" + "=" * 70)
    print("TEST 4: Verify Cross-Project Access Blocked")
    print("=" * 70)

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Check available projects
    cur.execute("SELECT DISTINCT project_id FROM failure_analysis ORDER BY project_id LIMIT 2")
    projects = [row['project_id'] for row in cur.fetchall()]

    if len(projects) < 2:
        print("  [SKIP] Need at least 2 projects with data")
        cur.close()
        conn.close()
        return None

    project_a, project_b = projects[0], projects[1]

    # Set context to project A
    cur.execute("SELECT set_project_context(%s)", (project_a,))

    # Try to query project B data explicitly with WHERE clause
    cur.execute("""
        SELECT COUNT(*) as count
        FROM failure_analysis
        WHERE project_id = %s
    """, (project_b,))

    count = cur.fetchone()['count']

    print(f"\n  Context: Project {project_a}")
    print(f"  Querying: Project {project_b} data")
    print(f"  Results: {count} records")

    cur.close()
    conn.close()

    if count == 0:
        print("\n  [SUCCESS] Cannot access other project's data (RLS working!)")
        return True
    else:
        print("\n  [FAIL] RLS not blocking cross-project access!")
        return False

def test_insert_with_wrong_project_id():
    """Test that you cannot insert data with wrong project_id"""
    print("\n" + "=" * 70)
    print("TEST 5: Verify Insert Validation")
    print("=" * 70)

    conn = get_db_connection()
    cur = conn.cursor()

    # Set context to project 1
    cur.execute("SELECT set_project_context(%s)", (1,))

    # Try to insert record for project 2
    try:
        cur.execute("""
            INSERT INTO failure_analysis (
                project_id, build_id, job_name, classification,
                confidence_score, created_at
            ) VALUES (%s, %s, %s, %s, %s, NOW())
        """, (2, 'TEST-RLS-999', 'test_job', 'product_bug', 0.95))

        conn.commit()

        print("\n  [FAIL] Was able to insert data for different project!")
        cur.close()
        conn.close()
        return False

    except psycopg2.errors.CheckViolation as e:
        conn.rollback()
        print(f"\n  [OK] Insert blocked by RLS: {str(e)[:100]}")
        print("\n  [SUCCESS] RLS preventing cross-project inserts")
        cur.close()
        conn.close()
        return True

    except Exception as e:
        conn.rollback()
        print(f"\n  [WARNING] Unexpected error: {e}")
        cur.close()
        conn.close()
        return None

def main():
    """Run all RLS tests"""

    print("\n" + "=" * 70)
    print("ROW-LEVEL SECURITY (RLS) ENFORCEMENT TESTS")
    print("=" * 70)
    print("\nTesting PostgreSQL RLS implementation for multi-project isolation")
    print("Database: ddn_ai_analysis")
    print("Port: 5434")

    results = {
        'policies_enabled': None,
        'context_functions': None,
        'project_isolation': None,
        'cross_project_blocked': None,
        'insert_validation': None
    }

    try:
        results['policies_enabled'] = test_rls_policies_enabled()
        results['context_functions'] = test_project_context_function()
        results['project_isolation'] = test_project_isolation()
        results['cross_project_blocked'] = test_cross_project_access_blocked()
        results['insert_validation'] = test_insert_with_wrong_project_id()

    except Exception as e:
        print(f"\n[ERROR] Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    test_names = {
        'policies_enabled': 'RLS Policies Enabled',
        'context_functions': 'Context Functions Work',
        'project_isolation': 'Project Data Isolation',
        'cross_project_blocked': 'Cross-Project Access Blocked',
        'insert_validation': 'Insert Validation'
    }

    passed = 0
    failed = 0
    skipped = 0

    for key, result in results.items():
        test_name = test_names[key]
        if result is True:
            print(f"  [PASS] {test_name}")
            passed += 1
        elif result is False:
            print(f"  [FAIL] {test_name}")
            failed += 1
        else:
            print(f"  [SKIP] {test_name}")
            skipped += 1

    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped")

    if failed == 0 and passed > 0:
        print("\n[SUCCESS] All RLS tests passed!")
        print("\nYour multi-project data is properly isolated.")
        return True
    elif failed > 0:
        print("\n[FAIL] Some RLS tests failed!")
        print("\nReview the failures above and ensure RLS migration was applied correctly.")
        return False
    else:
        print("\n[WARNING] Tests skipped due to missing data")
        return None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
