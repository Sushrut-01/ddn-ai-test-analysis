"""
Multi-Project Setup Script
Runs database migration and starts the API server

Usage:
    python setup_multi_project.py

This will:
1. Connect to PostgreSQL database
2. Run the migration to add multi-project tables
3. Create default "DDN" project
4. Assign existing users to the default project
5. Start the API server
"""

import psycopg2
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', '')
}

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def run_migration():
    """Run the database migration"""
    print_header("STEP 1: Running Database Migration")

    try:
        # Connect to database
        print(f"\nConnecting to database: {DB_CONFIG['database']} @ {DB_CONFIG['host']}...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()
        print("[+] Connected successfully")

        # Read migration SQL file
        migration_file = 'db_migrations/add_multi_project_tables.sql'
        print(f"\nReading migration file: {migration_file}...")

        if not os.path.exists(migration_file):
            print(f"[X] Migration file not found: {migration_file}")
            print("  Make sure you're running this script from the implementation directory")
            return False

        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()

        print("[+] Migration file loaded")

        # Execute migration
        print("\nExecuting migration SQL...")
        print("This may take a few moments...")

        cur.execute(migration_sql)

        print("[+] Migration executed successfully")

        # Verify tables were created
        print("\nVerifying migration...")
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('projects', 'user_projects', 'project_configurations', 'project_activity_log')
        """)

        tables = [row[0] for row in cur.fetchall()]
        print(f"[+] Found {len(tables)} new tables: {', '.join(tables)}")

        # Get project count
        cur.execute("SELECT COUNT(*) FROM projects")
        project_count = cur.fetchone()[0]
        print(f"[+] Projects in database: {project_count}")

        # Get user-project assignments
        cur.execute("SELECT COUNT(*) FROM user_projects")
        user_project_count = cur.fetchone()[0]
        print(f"[+] User-project assignments: {user_project_count}")

        cur.close()
        conn.close()

        print("\n[+] Migration completed successfully!")
        return True

    except psycopg2.Error as e:
        print(f"\n[X] Database error: {e}")
        return False
    except Exception as e:
        print(f"\n[X] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_projects():
    """Create test projects (optional)"""
    print_header("STEP 2: Creating Test Projects (Optional)")

    response = input("\nDo you want to create a 'Guruttava' test project? (y/n): ")

    if response.lower() != 'y':
        print("Skipping test project creation")
        return True

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Check if Guruttava already exists
        cur.execute("SELECT id FROM projects WHERE slug = 'guruttava'")
        if cur.fetchone():
            print("[+] Guruttava project already exists")
            cur.close()
            conn.close()
            return True

        # Create Guruttava project
        cur.execute("""
            INSERT INTO projects (slug, name, description, status, created_at)
            VALUES ('guruttava', 'Guruttava', 'Test project for multi-project demo', 'active', CURRENT_TIMESTAMP)
            RETURNING id
        """)
        project_id = cur.fetchone()[0]

        # Create configuration
        cur.execute("""
            INSERT INTO project_configurations (
                project_id, jira_project_key, mongodb_collection_prefix,
                pinecone_namespace, confidence_threshold
            ) VALUES (%s, 'GURU', 'guruttava_', 'guruttava_knowledge', 0.70)
        """, (project_id,))

        # Assign first user as owner
        cur.execute("SELECT id FROM users ORDER BY id LIMIT 1")
        user_row = cur.fetchone()

        if user_row:
            user_id = user_row[0]
            cur.execute("""
                INSERT INTO user_projects (user_id, project_id, role, joined_at)
                VALUES (%s, %s, 'project_owner', CURRENT_TIMESTAMP)
            """, (user_id, project_id))
            print(f"[+] Assigned user {user_id} as project owner")

        conn.commit()
        cur.close()
        conn.close()

        print(f"[+] Created 'Guruttava' project (ID: {project_id})")
        return True

    except Exception as e:
        print(f"[X] Error creating test project: {e}")
        return False

def display_project_summary():
    """Display summary of projects"""
    print_header("STEP 3: Project Summary")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Get all projects
        cur.execute("""
            SELECT p.id, p.slug, p.name, p.status,
                   COUNT(up.user_id) as user_count
            FROM projects p
            LEFT JOIN user_projects up ON p.id = up.project_id
            GROUP BY p.id, p.slug, p.name, p.status
            ORDER BY p.created_at
        """)

        projects = cur.fetchall()

        print("\nProjects in database:")
        print("-" * 60)
        for project in projects:
            proj_id, slug, name, status, user_count = project
            print(f"  ID: {proj_id} | Slug: {slug:15} | Name: {name:20} | Users: {user_count} | Status: {status}")

        print("-" * 60)
        print(f"Total: {len(projects)} project(s)")

        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"[X] Error getting project summary: {e}")
        return False

def start_api_server():
    """Start the API server"""
    print_header("STEP 4: Starting API Server")

    print("\nStarting multi-project API server...")
    print("Press Ctrl+C to stop the server\n")

    import subprocess
    try:
        subprocess.run([sys.executable, 'run_project_api.py'])
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")

def main():
    """Main execution"""
    print("=" * 60)
    print("  DDN AI Platform - Multi-Project Setup")
    print("=" * 60)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Database: {DB_CONFIG['database']} @ {DB_CONFIG['host']}:{DB_CONFIG['port']}")

    # Step 1: Run migration
    if not run_migration():
        print("\n[X] Migration failed. Please fix errors and try again.")
        sys.exit(1)

    # Step 2: Create test projects (optional)
    create_test_projects()

    # Step 3: Display summary
    display_project_summary()

    # Step 4: Ask to start server
    print("\n" + "=" * 60)
    response = input("\nDo you want to start the API server now? (y/n): ")

    if response.lower() == 'y':
        start_api_server()
    else:
        print("\n[+] Setup complete!")
        print("\nTo start the API server later, run:")
        print("  python run_project_api.py")
        print("\nFrontend will be available at:")
        print("  http://localhost:5173")
        print("\nAPI will be available at:")
        print("  http://localhost:5006/api/projects")

if __name__ == '__main__':
    main()
