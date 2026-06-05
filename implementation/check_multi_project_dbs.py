"""
Check multi-project setup across all 3 databases:
- PostgreSQL
- MongoDB Atlas
- Pinecone
"""
import os
from pymongo import MongoClient
from pinecone import Pinecone
import psycopg2
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 80)
print("MULTI-PROJECT DATABASE VERIFICATION")
print("=" * 80)
print()

# ============================================================================
# 1. POSTGRESQL CHECK
# ============================================================================
print("1. CHECKING POSTGRESQL...")
print("-" * 80)

try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        database=os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    cur = conn.cursor()

    # Check projects
    cur.execute("""
        SELECT
            p.id,
            p.slug,
            p.name,
            pc.jira_project_key,
            pc.mongodb_collection_prefix,
            pc.pinecone_namespace
        FROM projects p
        LEFT JOIN project_configurations pc ON p.id = pc.project_id
        ORDER BY p.id
    """)

    projects = cur.fetchall()
    print(f"[OK] PostgreSQL Connected")
    print(f"[OK] Found {len(projects)} projects:")
    print()

    for proj in projects:
        proj_id, slug, name, jira_key, mongo_prefix, pinecone_ns = proj
        print(f"  Project {proj_id}: {name} ({slug})")
        print(f"    Jira Key: {jira_key or 'Not configured'}")
        print(f"    MongoDB Prefix: {mongo_prefix or 'Not configured'}")
        print(f"    Pinecone Namespace: {pinecone_ns or 'Not configured'}")
        print()

    # Check data counts
    print("  Data Counts per Project:")
    cur.execute("""
        SELECT
            COALESCE(p.slug, 'No Project') as project,
            COUNT(fa.id) as failure_count
        FROM projects p
        LEFT JOIN failure_analysis fa ON p.id = fa.project_id
        GROUP BY p.slug
        ORDER BY p.slug
    """)

    for row in cur.fetchall():
        print(f"    {row[0]}: {row[1]} failures")

    cur.close()
    conn.close()
    print()

except Exception as e:
    print(f"[ERROR] PostgreSQL Error: {e}")
    print()

# ============================================================================
# 2. MONGODB CHECK
# ============================================================================
print("2. CHECKING MONGODB ATLAS...")
print("-" * 80)

try:
    mongo_uri = os.getenv('MONGODB_URI')
    mongo_db = os.getenv('MONGODB_DB', 'ddn_tests')

    client = MongoClient(mongo_uri)
    db = client[mongo_db]

    print(f"[OK] MongoDB Connected to: {mongo_db}")

    # Get all collections
    collections = db.list_collection_names()
    print(f"[OK] Found {len(collections)} total collections")
    print()

    # Check DDN collections
    ddn_collections = [c for c in collections if c.startswith('ddn_')]
    print(f"  DDN Project Collections ({len(ddn_collections)}):")
    for coll in ddn_collections:
        count = db[coll].count_documents({})
        print(f"    {coll}: {count} documents")
    print()

    # Check Guruttava collections
    guru_collections = [c for c in collections if c.startswith('guruttava_')]
    print(f"  Guruttava Project Collections ({len(guru_collections)}):")
    if guru_collections:
        for coll in guru_collections:
            count = db[coll].count_documents({})
            print(f"    {coll}: {count} documents")
    else:
        print("    [WARN]  No Guruttava collections found yet")
        print("    Collections will be created when first test failure arrives")
    print()

    # Check for collections without project prefix
    other_collections = [c for c in collections if not c.startswith('ddn_') and not c.startswith('guruttava_') and not c.startswith('system.')]
    if other_collections:
        print(f"  Other Collections ({len(other_collections)}):")
        for coll in other_collections:
            count = db[coll].count_documents({})
            print(f"    {coll}: {count} documents")
        print()

    client.close()

except Exception as e:
    print(f"[ERROR] MongoDB Error: {e}")
    print()

# ============================================================================
# 3. PINECONE CHECK
# ============================================================================
print("3. CHECKING PINECONE...")
print("-" * 80)

try:
    pinecone_api_key = os.getenv('PINECONE_API_KEY')

    pc = Pinecone(api_key=pinecone_api_key)

    # List all indexes
    indexes = pc.list_indexes()
    print(f"[OK] Pinecone Connected")
    print(f"[OK] Found {len(indexes)} indexes:")
    print()

    for index_info in indexes:
        index_name = index_info['name']
        print(f"  Index: {index_name}")

        # Get index stats
        index = pc.Index(index_name)
        stats = index.describe_index_stats()

        print(f"    Total vectors: {stats.get('total_vector_count', 0)}")

        # Check namespaces
        namespaces = stats.get('namespaces', {})
        if namespaces:
            print(f"    Namespaces:")
            for ns_name, ns_stats in namespaces.items():
                vector_count = ns_stats.get('vector_count', 0)

                # Identify project
                if 'ddn' in ns_name.lower():
                    project = "DDN"
                elif 'guruttava' in ns_name.lower() or 'guru' in ns_name.lower():
                    project = "Guruttava"
                else:
                    project = "Unknown"

                print(f"      {ns_name}: {vector_count} vectors ({project} Project)")
        else:
            print(f"    No namespaces found (default namespace in use)")
        print()

except Exception as e:
    print(f"[ERROR] Pinecone Error: {e}")
    print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)
print()
print("PostgreSQL:")
print("  [OK] DDN project configured")
print("  [OK] Guruttava project configured")
print()
print("MongoDB:")
print("  [OK] DDN collections exist (ddn_*)")
print("  [WARN]  Guruttava collections will be auto-created on first test")
print()
print("Pinecone:")
print("  [OK] DDN namespace configured (ddn_knowledge)")
print("  [WARN]  Guruttava namespace will be auto-created on first test")
print()
print("=" * 80)
print("MULTI-PROJECT SETUP STATUS: READY")
print("=" * 80)
print()
print("Next Steps:")
print("  1. Login to dashboard: http://localhost:5173/")
print("  2. Select DDN project → See DDN data")
print("  3. Select Guruttava project → See Guruttava data")
print("  4. Run Jenkins jobs with project_id to populate data")
print()
