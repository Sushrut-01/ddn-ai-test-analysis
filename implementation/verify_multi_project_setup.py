"""
Verify Multi-Project Setup
Checks database tables and data to confirm migration succeeded
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database config
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', '')
}

def verify_setup():
    """Verify multi-project setup"""
    print("=" * 70)
    print("  MULTI-PROJECT SETUP VERIFICATION")
    print("=" * 70)
    print(f"\nConnecting to: {DB_CONFIG['database']} @ {DB_CONFIG['host']}:{DB_CONFIG['port']}")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 1. Check if tables exist
        print("\n1. Checking Tables...")
        print("-" * 70)
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('projects', 'user_projects', 'project_configurations', 'project_activity_log')
            ORDER BY table_name
        """)
        tables = [row['table_name'] for row in cur.fetchall()]

        expected_tables = ['project_activity_log', 'project_configurations', 'projects', 'user_projects']
        print(f"   Expected tables: {len(expected_tables)}")
        print(f"   Found tables: {len(tables)}")
        for table in tables:
            print(f"   [+] {table}")

        if len(tables) == len(expected_tables):
            print("   [+] All tables created successfully!")
        else:
            print(f"   [X] Missing tables: {set(expected_tables) - set(tables)}")
            return False

        # 2. Check projects
        print("\n2. Checking Projects...")
        print("-" * 70)
        cur.execute("SELECT id, slug, name, status, created_at FROM projects ORDER BY id")
        projects = cur.fetchall()

        print(f"   Total projects: {len(projects)}")
        for p in projects:
            print(f"   - ID: {p['id']} | Slug: {p['slug']:15} | Name: {p['name']:25} | Status: {p['status']}")

        # 3. Check user-project assignments
        print("\n3. Checking User-Project Assignments...")
        print("-" * 70)
        cur.execute("""
            SELECT up.id, up.user_id, p.name as project_name, up.role, up.joined_at
            FROM user_projects up
            JOIN projects p ON up.project_id = p.id
            ORDER BY up.user_id, p.name
        """)
        assignments = cur.fetchall()

        print(f"   Total assignments: {len(assignments)}")
        for a in assignments:
            print(f"   - User {a['user_id']:2} | Project: {a['project_name']:25} | Role: {a['role']:20} | Joined: {a['joined_at']}")

        # 4. Check project configurations
        print("\n4. Checking Project Configurations...")
        print("-" * 70)
        cur.execute("""
            SELECT pc.id, p.name as project_name, pc.jira_project_key,
                   pc.github_repo_owner, pc.github_repo_name, pc.confidence_threshold
            FROM project_configurations pc
            JOIN projects p ON pc.project_id = p.id
            ORDER BY p.name
        """)
        configs = cur.fetchall()

        print(f"   Total configurations: {len(configs)}")
        for c in configs:
            print(f"   - Project: {c['project_name']:25}")
            print(f"     Jira Key: {c['jira_project_key'] or 'Not set'}")
            print(f"     GitHub: {c['github_repo_owner'] or 'Not set'}/{c['github_repo_name'] or 'Not set'}")
            print(f"     Confidence Threshold: {c['confidence_threshold']}")

        # 5. Check existing data has project_id
        print("\n5. Checking Existing Data Migration...")
        print("-" * 70)

        # Check failure_analysis
        try:
            cur.execute("SELECT COUNT(*) as total, COUNT(project_id) as with_project FROM failure_analysis")
            fa = cur.fetchone()
            print(f"   failure_analysis: {fa['with_project']}/{fa['total']} records have project_id")
        except:
            print("   failure_analysis: Table might not have project_id column yet")

        # Check build_metadata
        try:
            cur.execute("SELECT COUNT(*) as total, COUNT(project_id) as with_project FROM build_metadata")
            bm = cur.fetchone()
            print(f"   build_metadata: {bm['with_project']}/{bm['total']} records have project_id")
        except:
            print("   build_metadata: Table might not have project_id column yet")

        # 6. Verify helper functions
        print("\n6. Checking Helper Functions...")
        print("-" * 70)
        cur.execute("""
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND routine_name IN ('user_has_project_access', 'get_user_project_role')
        """)
        functions = [row['routine_name'] for row in cur.fetchall()]

        for func in ['user_has_project_access', 'get_user_project_role']:
            if func in functions:
                print(f"   [+] {func}() exists")
            else:
                print(f"   [ ] {func}() not found (optional)")

        cur.close()
        conn.close()

        print("\n" + "=" * 70)
        print("  VERIFICATION COMPLETE!")
        print("=" * 70)
        print("\n[+] Multi-project system is ready to use!")
        print("\nNext steps:")
        print("  1. Start API server: python run_project_api.py")
        print("  2. Start frontend: cd dashboard-ui && npm run dev")
        print("  3. Open http://localhost:5173/projects/manage")

        return True

    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    verify_setup()
