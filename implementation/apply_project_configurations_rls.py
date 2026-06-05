"""
Apply RLS to project_configurations table
"""

import psycopg2
import os

def apply_rls():
    """Apply RLS policies to project_configurations"""

    print("=" * 70)
    print("APPLYING RLS TO project_configurations TABLE")
    print("=" * 70)

    # Connect to database
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
        port=int(os.getenv('POSTGRES_PORT', 5434)),
        database=os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'password')
    )

    cur = conn.cursor()

    try:
        print("\n[*] Enabling RLS on project_configurations...")

        # Enable RLS
        cur.execute("ALTER TABLE project_configurations ENABLE ROW LEVEL SECURITY")
        print("  [OK] RLS enabled")

        # Create SELECT policy
        print("\n[*] Creating RLS policies...")

        cur.execute("""
            CREATE POLICY project_isolation_select ON project_configurations
                FOR SELECT
                USING (
                    project_id = get_current_project_id()
                    OR get_current_project_id() IS NULL
                )
        """)
        print("  [OK] SELECT policy created")

        # Create INSERT policy
        cur.execute("""
            CREATE POLICY project_isolation_insert ON project_configurations
                FOR INSERT
                WITH CHECK (
                    project_id = get_current_project_id()
                    OR get_current_project_id() IS NULL
                )
        """)
        print("  [OK] INSERT policy created")

        # Create UPDATE policy
        cur.execute("""
            CREATE POLICY project_isolation_update ON project_configurations
                FOR UPDATE
                USING (
                    project_id = get_current_project_id()
                    OR get_current_project_id() IS NULL
                )
        """)
        print("  [OK] UPDATE policy created")

        # Create DELETE policy
        cur.execute("""
            CREATE POLICY project_isolation_delete ON project_configurations
                FOR DELETE
                USING (
                    project_id = get_current_project_id()
                    OR get_current_project_id() IS NULL
                )
        """)
        print("  [OK] DELETE policy created")

        # Commit changes
        conn.commit()

        # Verify
        print("\n[*] Verifying RLS is enabled...")
        cur.execute("""
            SELECT
                schemaname,
                tablename,
                rowsecurity as rls_enabled
            FROM pg_tables
            WHERE tablename = 'project_configurations'
        """)

        result = cur.fetchone()
        if result and result[2]:
            print("  [OK] RLS verification passed")
        else:
            print("  [FAIL] RLS verification failed")
            return False

        # Check policies
        cur.execute("""
            SELECT COUNT(*) as policy_count
            FROM pg_policies
            WHERE tablename = 'project_configurations'
        """)

        policy_count = cur.fetchone()[0]
        print(f"  [OK] {policy_count} policies created")

        print("\n" + "=" * 70)
        print("[SUCCESS] RLS applied to project_configurations")
        print("=" * 70)

        cur.close()
        conn.close()

        return True

    except psycopg2.errors.DuplicateObject as e:
        print(f"\n  [INFO] RLS already exists: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        return True

    except Exception as e:
        print(f"\n  [ERROR] Failed to apply RLS: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        return False

if __name__ == "__main__":
    success = apply_rls()
    exit(0 if success else 1)
