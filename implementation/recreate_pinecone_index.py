"""
Recreate Pinecone Index with Correct Dimensions
This script will delete the old index and create a new one with 1536 dimensions
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def recreate_pinecone_index():
    """Recreate Pinecone index with correct dimensions"""
    print("=" * 60)
    print("Recreating Pinecone Index with 1536 Dimensions")
    print("=" * 60)

    # Get credentials
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX', 'ddn-error-solutions')

    print(f"\n[INFO] Configuration:")
    print(f"  - API Key: {api_key[:20]}...{api_key[-10:]}")
    print(f"  - Index Name: {index_name}")

    try:
        # Import Pinecone
        print("\n[INFO] Importing Pinecone library...")
        from pinecone import Pinecone, ServerlessSpec

        # Initialize Pinecone
        print("[INFO] Initializing Pinecone client...")
        pc = Pinecone(api_key=api_key)

        # Check if index exists
        print(f"\n[INFO] Checking if index '{index_name}' exists...")
        existing_indexes = pc.list_indexes()
        index_names = [idx.name for idx in existing_indexes]

        if index_name in index_names:
            print(f"[INFO] Found existing index '{index_name}'")

            # Get current index details
            for idx in existing_indexes:
                if idx.name == index_name:
                    print(f"  - Current Dimension: {idx.dimension}")
                    print(f"  - Metric: {idx.metric}")

                    if idx.dimension == 1536:
                        print(f"\n[OK] Index already has correct dimensions (1536)!")
                        return True

                    print(f"\n[WARNING] Index has wrong dimensions ({idx.dimension} instead of 1536)")
                    print(f"[INFO] Deleting old index...")
                    pc.delete_index(index_name)
                    print(f"[OK] Old index deleted")

                    # Wait for deletion to complete
                    print("[INFO] Waiting for deletion to complete...")
                    time.sleep(5)
                    break

        # Create new index with correct dimensions
        print(f"\n[INFO] Creating new index '{index_name}' with 1536 dimensions...")
        pc.create_index(
            name=index_name,
            dimension=1536,  # text-embedding-3-small dimension
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        print(f"[OK] Index '{index_name}' created successfully!")

        # Wait for index to be ready
        print("[INFO] Waiting for index to be ready...")
        time.sleep(10)

        # Verify the new index
        print("\n[INFO] Verifying new index...")
        indexes = pc.list_indexes()
        for idx in indexes:
            if idx.name == index_name:
                print(f"[OK] Index verified:")
                print(f"  - Name: {idx.name}")
                print(f"  - Dimension: {idx.dimension}")
                print(f"  - Metric: {idx.metric}")
                print(f"  - Host: {idx.host}")

                # Update environment note
                environment = idx.host.split('.')[-3]  # Extract environment from host
                print(f"\n[INFO] Update your .env file with:")
                print(f"  PINECONE_ENVIRONMENT={environment}")
                print(f"  PINECONE_DIMENSION=1536")
                print(f"  PINECONE_HOST={idx.host}")

        print("\n" + "=" * 60)
        print("[OK] Pinecone index recreation COMPLETED!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERROR] Failed to recreate index: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = recreate_pinecone_index()

    if success:
        print("\n[INFO] Next steps:")
        print("  1. Update .env file with new PINECONE_ENVIRONMENT value")
        print("  2. Start PostgreSQL service")
        print("  3. Start AI services")
    else:
        print("\n[ERROR] Please fix the errors above and try again")
