"""
Retrieval Module (Tasks 0-ARCH.24, 0-ARCH.25, 0-ARCH.27, 0-ARCH.28)

Multi-source retrieval system for Fusion RAG combining:
1. Pinecone dense retrieval (semantic similarity)
2. BM25 sparse retrieval (keyword matching)
3. MongoDB full-text search (document search)
4. PostgreSQL structured query (metadata filtering)

Main Components:
- FusionRAG: Main retrieval orchestrator (Task 0-ARCH.24)
- BM25IndexBuilder: BM25 index builder (Task 0-ARCH.25)
- QueryExpander: Query expansion for better recall (Task 0-ARCH.28)

Tasks:
- 0-ARCH.24: Fusion RAG service implementation
- 0-ARCH.25: BM25 index builder
- 0-ARCH.26: RRF scoring (implemented in FusionRAG)
- 0-ARCH.27: CrossEncoder re-ranking ✅ COMPLETE
- 0-ARCH.28: Query expansion ✅ COMPLETE
"""

from .fusion_rag_service import FusionRAG, get_fusion_rag
from .build_bm25_index import BM25IndexBuilder
from .query_expansion import QueryExpander, get_query_expander

__all__ = [
    'FusionRAG',
    'get_fusion_rag',
    'BM25IndexBuilder',
    'QueryExpander',
    'get_query_expander'
]

__version__ = '1.2.0'  # Tasks 0-ARCH.24, 0-ARCH.25, 0-ARCH.27, 0-ARCH.28
