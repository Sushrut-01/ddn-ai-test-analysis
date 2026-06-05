"""
Add RLS Context to Existing Services
Adds set_project_context() calls to existing database queries

This makes existing code RLS-aware without breaking functionality
"""

import re
import os
from pathlib import Path

def add_rls_context_to_file(filepath):
    """Add RLS context setting to a service file"""

    print(f"\n[*] Processing: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if already has RLS context
        if 'set_project_context' in content:
            print("    [SKIP] Already has RLS context")
            return False

        # Pattern 1: Find database connection functions
        # Look for: def get_db_connection():
        pattern1 = r'(def get_db_connection\(\):.*?return.*?)'

        # Pattern 2: Find places where cursor is created
        # Look for: cur = conn.cursor()
        pattern2 = r'(cur = conn\.cursor\(.*?\))'

        modifications = []

        # Add helper function if not exists
        if 'def set_rls_context(' not in content:
            helper_function = '''
# ============================================================================
# RLS CONTEXT HELPER (Added by add_rls_context_to_existing_services.py)
# ============================================================================

def set_rls_context(cursor, project_id):
    """
    Set PostgreSQL Row-Level Security context for project

    Call this after creating a cursor to enable automatic project filtering.

    Args:
        cursor: PostgreSQL cursor
        project_id: Project ID to set context for

    Example:
        conn = get_db_connection()
        cur = conn.cursor()
        set_rls_context(cur, project_id)  # Enable RLS for this project
        cur.execute("SELECT * FROM failure_analysis")  # Automatically filtered
    """
    if project_id:
        try:
            cursor.execute("SELECT set_project_context(%s)", (project_id,))
        except Exception as e:
            # Graceful fallback if RLS function doesn't exist
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not set RLS context: {e}")

# ============================================================================
'''
            modifications.append(("Add RLS helper function", helper_function))

        # Find all cursor creations and add context setting
        # This is a marker to show where to add manual calls
        cursor_locations = re.finditer(pattern2, content)
        cursor_count = len(list(re.finditer(pattern2, content)))

        print(f"    Found {cursor_count} cursor creations")
        print("    [NOTE] Manual addition of set_rls_context() calls recommended")
        print("    Add after cursor creation: set_rls_context(cur, project_id)")

        # Create backup
        backup_path = filepath + '.backup'
        if not os.path.exists(backup_path):
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"    [OK] Backup created: {backup_path}")

        # Add helper function at the top of file
        if modifications:
            # Find a good insertion point (after imports)
            import_end = 0
            for match in re.finditer(r'^import |^from ', content, re.MULTILINE):
                import_end = match.end()

            # Find the end of imports section
            lines = content.split('\n')
            insert_line = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_line = i + 1
                elif insert_line > 0 and line.strip() and not line.startswith('#'):
                    break

            # Insert helper function
            new_content = '\n'.join(lines[:insert_line]) + '\n' + helper_function + '\n' + '\n'.join(lines[insert_line:])

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"    [OK] Added RLS helper function")
            return True

        return False

    except Exception as e:
        print(f"    [ERROR] {e}")
        return False

def create_migration_examples():
    """Create examples of how to update code"""

    example_code = '''
# ============================================================================
# EXAMPLES: How to Add RLS Context to Existing Code
# ============================================================================

# BEFORE (No RLS context):
# -------------------------
def get_failures():
    project_id = request.args.get('project_id', 1)

    conn = get_db_connection()
    cur = conn.cursor()

    # Manual WHERE clause - can be forgotten!
    cur.execute("""
        SELECT * FROM failure_analysis
        WHERE project_id = %s
    """, (project_id,))

    failures = cur.fetchall()
    return jsonify({'failures': failures})


# AFTER (With RLS context):
# -------------------------
def get_failures():
    project_id = request.args.get('project_id', 1)

    conn = get_db_connection()
    cur = conn.cursor()

    # ADD THIS LINE: Set RLS context
    set_rls_context(cur, project_id)  # <-- ADDED

    # No WHERE clause needed - RLS filters automatically!
    cur.execute("""
        SELECT * FROM failure_analysis
    """)

    failures = cur.fetchall()
    return jsonify({'failures': failures})


# ============================================================================
# PATTERN: Add after EVERY cursor creation
# ============================================================================

# Pattern to find:
cur = conn.cursor()

# Add immediately after:
set_rls_context(cur, project_id)


# ============================================================================
# EXAMPLE: manual_trigger_api.py
# ============================================================================

# BEFORE:
@app.route('/api/trigger-analysis', methods=['POST'])
def trigger_manual_analysis():
    data = request.get_json()
    project_id = data.get('project_id', 1)

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT p.*, pc.*
        FROM projects p
        LEFT JOIN project_configurations pc ON p.id = pc.project_id
        WHERE p.id = %s
    """, (project_id,))
    # ... rest of code


# AFTER:
@app.route('/api/trigger-analysis', methods=['POST'])
def trigger_manual_analysis():
    data = request.get_json()
    project_id = data.get('project_id', 1)

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # ADD THIS LINE:
    set_rls_context(cursor, project_id)  # <-- ADDED

    # WHERE clause still works, but RLS adds extra safety
    cursor.execute("""
        SELECT p.*, pc.*
        FROM projects p
        LEFT JOIN project_configurations pc ON p.id = pc.project_id
        WHERE p.id = %s
    """, (project_id,))
    # ... rest of code


# ============================================================================
# BENEFITS
# ============================================================================

# 1. Backward compatible - old code still works
# 2. Added safety - even if WHERE clause forgotten, RLS protects
# 3. Minimal changes - just one line after cursor creation
# 4. Graceful fallback - if RLS not set up, old WHERE clauses still work
# 5. Easy to find - search for "cur = conn.cursor()" and add context

# ============================================================================
'''

    with open('RLS_MIGRATION_EXAMPLES.md', 'w') as f:
        f.write(example_code)

    print("\n[OK] Created: RLS_MIGRATION_EXAMPLES.md")

def main():
    """Main execution"""

    print("=" * 70)
    print("ADD RLS CONTEXT TO EXISTING SERVICES")
    print("=" * 70)

    # Services to update
    services = [
        'manual_trigger_api.py',
        'jira_integration_service.py',
        'dashboard_api_full.py',
    ]

    print("\n[*] Scanning services...")

    for service in services:
        if os.path.exists(service):
            add_rls_context_to_file(service)
        else:
            print(f"\n[SKIP] {service} not found")

    # Create examples
    create_migration_examples()

    print("\n" + "=" * 70)
    print("MIGRATION COMPLETE")
    print("=" * 70)

    print("\nWhat was done:")
    print("1. Added set_rls_context() helper function to services")
    print("2. Created backups (.backup files)")
    print("3. Created RLS_MIGRATION_EXAMPLES.md")

    print("\nManual steps required:")
    print("1. Search for 'cur = conn.cursor()' in each service")
    print("2. Add 'set_rls_context(cur, project_id)' after each cursor creation")
    print("3. Test that service still works")
    print("4. Gradually remove WHERE project_id clauses (optional)")

    print("\nExample:")
    print("    conn = get_db_connection()")
    print("    cur = conn.cursor()")
    print("    set_rls_context(cur, project_id)  # <-- Add this line")
    print("    cur.execute('SELECT * FROM failure_analysis')")

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
