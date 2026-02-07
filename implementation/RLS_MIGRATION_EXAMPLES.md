
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
