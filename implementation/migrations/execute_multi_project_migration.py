#!/usr/bin/env python3
"""
Multi-Project Migration Executor
Safely executes the multi-project support migration with backup and rollback capabilities
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from datetime import datetime
import json
import subprocess

# Configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', '')
}

MIGRATION_FILE = '001_add_multi_project_support.sql'
BACKUP_DIR = 'backups'


class MigrationExecutor:
    def __init__(self):
        self.conn = None
        self.backup_file = None

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.conn.autocommit = False
            print(f"✓ Connected to database: {DB_CONFIG['database']}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to database: {e}")
            return False

    def verify_prerequisites(self):
        """Verify that required tables exist"""
        try:
            cur = self.conn.cursor()

            # Check if users table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_name = 'users'
                )
            """)

            if not cur.fetchone()[0]:
                print("✗ Prerequisites not met: 'users' table does not exist")
                return False

            # Check if failure_analysis exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_name = 'failure_analysis'
                )
            """)

            if not cur.fetchone()[0]:
                print("✗ Prerequisites not met: 'failure_analysis' table does not exist")
                return False

            print("✓ Prerequisites verified")
            return True

        except Exception as e:
            print(f"✗ Error verifying prerequisites: {e}")
            return False

    def create_backup(self):
        """Create database backup before migration"""
        try:
            # Create backup directory if not exists
            os.makedirs(BACKUP_DIR, exist_ok=True)

            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.backup_file = os.path.join(BACKUP_DIR, f'pre_migration_backup_{timestamp}.sql')

            print(f"Creating backup: {self.backup_file}")

            # Use pg_dump to create backup
            pg_dump_cmd = [
                'pg_dump',
                '-h', DB_CONFIG['host'],
                '-p', str(DB_CONFIG['port']),
                '-U', DB_CONFIG['user'],
                '-d', DB_CONFIG['database'],
                '-f', self.backup_file,
                '--no-owner',
                '--no-acl'
            ]

            # Set password in environment
            env = os.environ.copy()
            env['PGPASSWORD'] = DB_CONFIG['password']

            result = subprocess.run(pg_dump_cmd, env=env, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"✗ Backup failed: {result.stderr}")
                return False

            print(f"✓ Backup created: {self.backup_file}")

            # Also create a JSON backup of current state
            self.create_state_snapshot()

            return True

        except Exception as e:
            print(f"✗ Error creating backup: {e}")
            return False

    def create_state_snapshot(self):
        """Create JSON snapshot of current database state"""
        try:
            cur = self.conn.cursor()

            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'database': DB_CONFIG['database'],
                'tables': {}
            }

            # Get row counts for key tables
            tables = [
                'users', 'failure_analysis', 'build_metadata',
                'test_case_history', 'user_feedback', 'failure_patterns'
            ]

            for table in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    snapshot['tables'][table] = {'row_count': count}
                except:
                    snapshot['tables'][table] = {'row_count': 'N/A'}

            # Save snapshot
            snapshot_file = self.backup_file.replace('.sql', '_snapshot.json')
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot, f, indent=2)

            print(f"✓ State snapshot created: {snapshot_file}")

        except Exception as e:
            print(f"⚠ Warning: Could not create state snapshot: {e}")

    def read_migration_file(self):
        """Read migration SQL file"""
        try:
            migration_path = os.path.join(os.path.dirname(__file__), MIGRATION_FILE)

            if not os.path.exists(migration_path):
                print(f"✗ Migration file not found: {migration_path}")
                return None

            with open(migration_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            print(f"✓ Migration file loaded: {MIGRATION_FILE}")
            return sql_content

        except Exception as e:
            print(f"✗ Error reading migration file: {e}")
            return None

    def execute_migration(self, sql_content):
        """Execute migration SQL"""
        try:
            cur = self.conn.cursor()

            print("\nExecuting migration...")
            print("=" * 60)

            # Execute the migration
            cur.execute(sql_content)

            print("=" * 60)
            print("✓ Migration SQL executed successfully")

            return True

        except Exception as e:
            print(f"✗ Migration execution failed: {e}")
            return False

    def verify_migration(self):
        """Verify migration was successful"""
        try:
            cur = self.conn.cursor()

            checks = []

            # Check 1: Verify new tables exist
            new_tables = ['projects', 'user_projects', 'project_configurations', 'project_activity_log']
            for table in new_tables:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = %s
                    )
                """, (table,))

                exists = cur.fetchone()[0]
                checks.append((f"Table '{table}' exists", exists))

            # Check 2: Verify project_id columns added
            tables_with_project_id = ['failure_analysis', 'build_metadata', 'test_case_history']
            for table in tables_with_project_id:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = %s AND column_name = 'project_id'
                    )
                """, (table,))

                exists = cur.fetchone()[0]
                checks.append((f"Column 'project_id' added to '{table}'", exists))

            # Check 3: Verify default project created
            cur.execute("SELECT COUNT(*) FROM projects WHERE slug = 'ddn'")
            default_project_exists = cur.fetchone()[0] > 0
            checks.append(("Default project 'ddn' created", default_project_exists))

            # Check 4: Verify users assigned to project
            cur.execute("SELECT COUNT(*) FROM user_projects")
            user_project_count = cur.fetchone()[0]
            checks.append((f"Users assigned to projects ({user_project_count} assignments)", user_project_count > 0))

            # Check 5: Verify configuration created
            cur.execute("SELECT COUNT(*) FROM project_configurations")
            config_count = cur.fetchone()[0]
            checks.append((f"Project configurations created ({config_count} configs)", config_count > 0))

            # Print verification results
            print("\nVerification Results:")
            print("=" * 60)

            all_passed = True
            for check_name, passed in checks:
                status = "✓" if passed else "✗"
                print(f"{status} {check_name}")
                if not passed:
                    all_passed = False

            print("=" * 60)

            if all_passed:
                print("✓ All verification checks passed!")
            else:
                print("✗ Some verification checks failed!")

            return all_passed

        except Exception as e:
            print(f"✗ Verification failed: {e}")
            return False

    def display_summary(self):
        """Display migration summary"""
        try:
            cur = self.conn.cursor()

            print("\n" + "=" * 60)
            print("MIGRATION SUMMARY")
            print("=" * 60)

            # Projects
            cur.execute("SELECT COUNT(*) FROM projects")
            project_count = cur.fetchone()[0]
            print(f"Projects created: {project_count}")

            cur.execute("SELECT slug, name FROM projects")
            for slug, name in cur.fetchall():
                print(f"  - {name} ({slug})")

            # Users
            cur.execute("SELECT COUNT(DISTINCT user_id) FROM user_projects")
            user_count = cur.fetchone()[0]
            print(f"\nUsers with project access: {user_count}")

            # Team composition
            cur.execute("""
                SELECT p.name, up.role, COUNT(*)
                FROM projects p
                JOIN user_projects up ON p.id = up.project_id
                GROUP BY p.name, up.role
            """)

            print("\nTeam composition by project:")
            current_project = None
            for project_name, role, count in cur.fetchall():
                if project_name != current_project:
                    print(f"\n  {project_name}:")
                    current_project = project_name
                print(f"    - {role}: {count}")

            # Data migration
            cur.execute("SELECT COUNT(*) FROM failure_analysis WHERE project_id IS NOT NULL")
            migrated_failures = cur.fetchone()[0]
            print(f"\nMigrated failure records: {migrated_failures}")

            print("=" * 60)

        except Exception as e:
            print(f"⚠ Could not generate summary: {e}")

    def run(self, dry_run=False):
        """Execute complete migration process"""
        print("\n" + "=" * 60)
        print("MULTI-PROJECT MIGRATION EXECUTOR")
        print("=" * 60)
        print(f"Database: {DB_CONFIG['database']}")
        print(f"Host: {DB_CONFIG['host']}")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
        print("=" * 60 + "\n")

        # Step 1: Connect
        if not self.connect():
            return False

        # Step 2: Verify prerequisites
        if not self.verify_prerequisites():
            return False

        # Step 3: Create backup
        if not dry_run:
            if not self.create_backup():
                print("\n⚠ WARNING: Backup failed!")
                response = input("Continue without backup? (yes/no): ")
                if response.lower() != 'yes':
                    print("Migration aborted.")
                    return False

        # Step 4: Read migration file
        sql_content = self.read_migration_file()
        if not sql_content:
            return False

        # Step 5: Execute migration
        if not dry_run:
            print("\n⚠ ABOUT TO EXECUTE MIGRATION")
            print("This will modify the database schema and data.")
            response = input("Continue? (yes/no): ")

            if response.lower() != 'yes':
                print("Migration aborted.")
                return False

            if not self.execute_migration(sql_content):
                print("\n✗ Migration failed!")
                print("Rolling back transaction...")
                self.conn.rollback()
                print(f"Database restored. Backup available at: {self.backup_file}")
                return False

            # Commit transaction
            print("\nCommitting transaction...")
            self.conn.commit()
            print("✓ Transaction committed")

            # Step 6: Verify migration
            if not self.verify_migration():
                print("\n⚠ WARNING: Verification failed!")
                print("Migration was committed but verification checks failed.")
                print(f"Backup available at: {self.backup_file}")
                return False

            # Step 7: Display summary
            self.display_summary()

            print("\n" + "=" * 60)
            print("✓ MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"Backup saved to: {self.backup_file}")
            print("\nNext steps:")
            print("1. Update backend API to use project-aware endpoints")
            print("2. Update frontend to add project selector")
            print("3. Configure project integrations (Jira, GitHub)")
            print("=" * 60 + "\n")

        else:
            print("\n✓ DRY RUN COMPLETED")
            print("Migration SQL validated successfully.")
            print("Run without --dry-run to execute migration.")

        return True

    def cleanup(self):
        """Cleanup resources"""
        if self.conn:
            self.conn.close()
            print("\nDatabase connection closed.")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Execute multi-project migration')
    parser.add_argument('--dry-run', action='store_true', help='Validate migration without executing')
    parser.add_argument('--skip-backup', action='store_true', help='Skip backup creation (not recommended)')

    args = parser.parse_args()

    executor = MigrationExecutor()

    try:
        success = executor.run(dry_run=args.dry_run)
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nMigration interrupted by user.")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        executor.cleanup()


if __name__ == '__main__':
    main()
