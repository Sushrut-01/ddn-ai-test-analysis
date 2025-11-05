"""
Setup Audit Trail Table for Knowledge Management
Task 0-HITL-KM.5: Create knowledge_doc_changes table
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection
conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=int(os.getenv('POSTGRES_PORT', 5432)),
    database=os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    user=os.getenv('POSTGRES_USER', 'postgres'),
    password=os.getenv('POSTGRES_PASSWORD')
)

cursor = conn.cursor()

print("Creating knowledge_doc_changes table...")

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_doc_changes (
        id SERIAL PRIMARY KEY,
        doc_id VARCHAR(255) NOT NULL,
        action VARCHAR(50) NOT NULL,
        user_email VARCHAR(255) NOT NULL,
        details JSONB,
        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT valid_action CHECK (action IN ('add', 'update', 'delete'))
    );
""")

# Create indexes
print("Creating indexes...")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_doc_changes_doc_id ON knowledge_doc_changes(doc_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_doc_changes_action ON knowledge_doc_changes(action);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_doc_changes_user_email ON knowledge_doc_changes(user_email);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_doc_changes_changed_at ON knowledge_doc_changes(changed_at DESC);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_doc_changes_details ON knowledge_doc_changes USING GIN (details);")

# Add comments
print("Adding table comments...")
cursor.execute("COMMENT ON TABLE knowledge_doc_changes IS 'Audit trail for all knowledge documentation changes in Pinecone knowledge base';")

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'knowledge_doc_changes';")
exists = cursor.fetchone()[0]

if exists:
    print("\n[SUCCESS] Audit trail table created successfully!")

    # Show structure
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'knowledge_doc_changes'
        ORDER BY ordinal_position;
    """)

    print("\nTable structure:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")

    # Show indexes
    cursor.execute("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'knowledge_doc_changes';
    """)

    print("\nIndexes:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
else:
    print("\n[ERROR] Table creation failed!")

cursor.close()
conn.close()

print("\nAudit trail is ready for use!")
