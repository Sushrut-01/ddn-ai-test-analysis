"""
Run database migration to add missing columns for Analytics and PR Workflow
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL configuration
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

def run_migration():
    """Execute the migration SQL file"""
    print("="*70)
    print("RUNNING DATABASE MIGRATION")
    print("="*70)
    print(f"Host: {POSTGRES_CONFIG['host']}")
    print(f"Port: {POSTGRES_CONFIG['port']}")
    print(f"Database: {POSTGRES_CONFIG['database']}")
    print(f"User: {POSTGRES_CONFIG['user']}")
    print()

    try:
        # Connect to PostgreSQL
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        print("[OK] Connected successfully\n")

        # Read migration file
        migration_file = 'migrations/add_missing_columns_for_pr_workflow.sql'
        print(f"Reading migration file: {migration_file}")

        with open(migration_file, 'r') as f:
            sql = f.read()

        print(f"[OK] Migration file loaded ({len(sql)} characters)\n")

        # Remove psql-specific commands that can't be executed via psycopg2
        print("Cleaning SQL (removing psql-specific commands)...")
        sql_lines = sql.split('\n')
        cleaned_lines = []
        for line in sql_lines:
            # Skip psql meta-commands
            if line.strip().startswith('\\c') or line.strip().startswith('\\'):
                print(f"  Skipping: {line.strip()[:50]}")
                continue
            cleaned_lines.append(line)

        sql = '\n'.join(cleaned_lines)
        print(f"[OK] SQL cleaned ({len(sql)} characters)\n")

        # Execute migration
        print("Executing migration...")
        cursor.execute(sql)
        print("[OK] Migration executed successfully\n")

        # Verify columns were added
        print("Verifying migration...")

        # Check failure_analysis columns
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'failure_analysis'
            AND column_name IN ('error_type', 'error_message', 'component',
                                'file_path', 'line_number', 'stack_trace',
                                'severity', 'classification', 'mongodb_failure_id')
            ORDER BY column_name
        """)
        fa_columns = [row[0] for row in cursor.fetchall()]

        print(f"[OK] failure_analysis table - Added {len(fa_columns)} columns:")
        for col in fa_columns:
            print(f"  - {col}")

        # Check code_fix_applications columns
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'code_fix_applications'
            AND column_name IN ('job_name', 'file_path', 'fix_type')
            ORDER BY column_name
        """)
        cfa_columns = [row[0] for row in cursor.fetchall()]

        print(f"\n[OK] code_fix_applications table - Added {len(cfa_columns)} columns:")
        for col in cfa_columns:
            print(f"  - {col}")

        # Check record counts
        cursor.execute("SELECT COUNT(*) FROM failure_analysis")
        fa_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM code_fix_applications")
        cfa_count = cursor.fetchone()[0]

        print(f"\n[OK] Current record counts:")
        print(f"  - failure_analysis: {fa_count} records")
        print(f"  - code_fix_applications: {cfa_count} records")

        cursor.close()
        conn.close()

        print("\n" + "="*70)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("  1. Analytics page is now ready to use")
        print("  2. PR Workflow page is now ready to use")
        print("  3. PR creation workflow will work end-to-end")
        print("  4. Start dashboard API: python dashboard_api_full.py")
        print("  5. Test pages at:")
        print("     - http://localhost:5173/analytics")
        print("     - http://localhost:5173/pr-workflow")
        print("="*70)

        return True

    except psycopg2.Error as e:
        print(f"\n[ERROR] PostgreSQL Error: {e}")
        print(f"   Error code: {e.pgcode}")
        print(f"   Error message: {e.pgerror}")
        return False

    except FileNotFoundError:
        print(f"\n[ERROR] Migration file not found: {migration_file}")
        print("   Make sure you're running from the implementation directory")
        return False

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
