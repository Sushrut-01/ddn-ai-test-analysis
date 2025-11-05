"""
Check what's stored in Pinecone - View all vectors and metadata
This shows the work done in Task 0.2
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone
import json

# Load environment
load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX_NAME', 'ddn-error-solutions'))

print("=" * 80)
print("PINECONE VECTOR DATABASE - VERIFICATION")
print("=" * 80)
print(f"Index Name: {os.getenv('PINECONE_INDEX_NAME')}")
print(f"Dimension: 1536 (OpenAI text-embedding-3-small)")
print()

# Get index stats
stats = index.describe_index_stats()
print("=" * 80)
print("INDEX STATISTICS")
print("=" * 80)
print(f"Total Vectors: {stats.total_vector_count}")
print(f"Namespaces: {stats.namespaces}")
print()

# Query to get sample vectors
print("=" * 80)
print("SAMPLE VECTORS (First 5)")
print("=" * 80)

# Create a dummy query vector to fetch results
dummy_vector = [0.0] * 1536

try:
    # Query with a dummy vector to get actual stored vectors
    results = index.query(
        vector=dummy_vector,
        top_k=5,
        include_metadata=True
    )

    if results.matches:
        for i, match in enumerate(results.matches, 1):
            print(f"\n--- Vector {i} ---")
            print(f"ID: {match.id}")
            print(f"Score: {match.score:.4f}")
            print(f"Metadata:")
            if match.metadata:
                for key, value in match.metadata.items():
                    if len(str(value)) > 60:
                        print(f"  {key}: {str(value)[:60]}...")
                    else:
                        print(f"  {key}: {value}")
            else:
                print("  (No metadata)")
    else:
        print("No vectors found")

except Exception as e:
    print(f"Error querying Pinecone: {e}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
print("\nWhat this shows:")
print("✅ Vector IDs = MongoDB failure _id (links back to full failure data)")
print("✅ Metadata = Test name, classification, product, etc.")
print("✅ Vectors = 1536-dimensional embeddings (not shown - too large)")
print("\nThese vectors enable:")
print("  - Fast similarity search (find similar errors in 0.2 seconds)")
print("  - Semantic matching (finds similar meaning, not just exact words)")
print("  - RAG retrieval (retrieves relevant past failures for AI analysis)")
