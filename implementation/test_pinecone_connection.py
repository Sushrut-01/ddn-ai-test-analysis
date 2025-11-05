"""
Test Pinecone Connection
Verifies that Pinecone is properly configured and accessible
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_pinecone_connection():
    """Test connection to Pinecone"""
    print("=" * 60)
    print("Testing Pinecone Connection")
    print("=" * 60)

    # Get credentials
    api_key = os.getenv('PINECONE_API_KEY')
    environment = os.getenv('PINECONE_ENVIRONMENT')
    index_name = os.getenv('PINECONE_INDEX')

    print(f"\n[INFO] Configuration:")
    print(f"  - API Key: {api_key[:20]}...{api_key[-10:]}")
    print(f"  - Environment: {environment}")
    print(f"  - Index Name: {index_name}")

    try:
        # Import Pinecone
        print("\n[INFO] Importing Pinecone library...")
        from pinecone import Pinecone, ServerlessSpec

        # Initialize Pinecone
        print("[INFO] Initializing Pinecone client...")
        pc = Pinecone(api_key=api_key)

        # List all indexes
        print("\n[INFO] Listing all indexes...")
        indexes = pc.list_indexes()
        print(f"[OK] Found {len(indexes)} index(es):")
        for idx in indexes:
            print(f"  - {idx.name}")
            print(f"    Dimension: {idx.dimension}")
            print(f"    Metric: {idx.metric}")
            print(f"    Host: {idx.host}")

        # Check if our index exists
        if index_name in [idx.name for idx in indexes]:
            print(f"\n[OK] Index '{index_name}' found!")

            # Connect to the index
            print(f"\n[INFO] Connecting to index '{index_name}'...")
            index = pc.Index(index_name)

            # Get index stats
            print("[INFO] Fetching index statistics...")
            stats = index.describe_index_stats()
            print(f"\n[OK] Index Statistics:")
            print(f"  - Total vectors: {stats.total_vector_count}")
            print(f"  - Dimension: {stats.dimension}")
            print(f"  - Index fullness: {stats.index_fullness}")

            print("\n" + "=" * 60)
            print("[OK] Pinecone connection test PASSED!")
            print("=" * 60)
            return True
        else:
            print(f"\n[ERROR] Index '{index_name}' not found!")
            print("\nAvailable indexes:")
            for idx in indexes:
                print(f"  - {idx.name}")
            return False

    except ImportError:
        print("\n[ERROR] Pinecone library not installed!")
        print("\nTo install, run:")
        print("  python -m pip install pinecone-client")
        return False
    except Exception as e:
        print(f"\n[ERROR] Connection test failed: {str(e)}")
        print(f"\nError type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_pinecone_connection()

    if success:
        print("\n[INFO] Next steps:")
        print("  1. Start PostgreSQL service (run START-POSTGRESQL.bat as admin)")
        print("  2. Install remaining Python packages")
        print("  3. Start AI services")
    else:
        print("\n[INFO] Please fix the errors above before proceeding")
