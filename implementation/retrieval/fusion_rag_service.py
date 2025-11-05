"""
Fusion RAG Service (Task 0-ARCH.24)

Combines 4 retrieval sources using Reciprocal Rank Fusion (RRF):
1. Pinecone Dense Retrieval (semantic similarity)
2. BM25 Sparse Retrieval (keyword matching)
3. MongoDB Full-Text Search (document search)
4. PostgreSQL Structured Query (metadata filtering)

Author: AI Analysis System
Date: 2025-11-02
Version: 1.0.0
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Database imports
try:
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logging.warning("Pinecone not available")

try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    logging.warning("MongoDB not available")

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    logging.warning("PostgreSQL not available")

# OpenAI for embeddings
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available")

# BM25 for sparse retrieval
try:
    from rank_bm25 import BM25Okapi
    import pickle
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    logging.warning("BM25 not available - install with: pip install rank-bm25")

# CrossEncoder for re-ranking (Task 0-ARCH.27)
try:
    from sentence_transformers import CrossEncoder
    import numpy as np
    CROSSENCODER_AVAILABLE = True
except ImportError:
    CROSSENCODER_AVAILABLE = False
    logging.warning("CrossEncoder not available - install with: pip install sentence-transformers")

# Query Expansion (Task 0-ARCH.28)
try:
    from .query_expansion import QueryExpander
    QUERY_EXPANSION_AVAILABLE = True
except ImportError:
    QUERY_EXPANSION_AVAILABLE = False
    logging.warning("Query expansion not available")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FusionRAG:
    """
    Fusion RAG service combining 4 retrieval sources with RRF

    Architecture:
        Query → Query Expansion → 4 Parallel Sources → RRF Fusion → Top Results

    Sources:
        1. Pinecone (dense vector search)
        2. BM25 (sparse keyword search)
        3. MongoDB (full-text search)
        4. PostgreSQL (structured query with filters)

    Performance Targets:
        - Latency: <3 seconds
        - Accuracy: 85-90% (up from 70% with single-source)
        - Recall@10: >95%
    """

    def __init__(
        self,
        pinecone_index_name: str = "knowledge-docs",
        mongodb_uri: Optional[str] = None,
        postgres_uri: Optional[str] = None,
        bm25_index_path: Optional[str] = None,
        parallel_workers: int = 4,
        rrf_k: int = 60,
        enable_rerank: bool = True,
        rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        """
        Initialize FusionRAG with all 4 retrieval sources

        Args:
            pinecone_index_name: Name of Pinecone index
            mongodb_uri: MongoDB connection string
            postgres_uri: PostgreSQL connection string
            bm25_index_path: Path to BM25 index pickle file
            parallel_workers: Number of parallel workers for retrieval
            rrf_k: RRF constant (default: 60)
            enable_rerank: Enable CrossEncoder re-ranking (default: True) [Task 0-ARCH.27]
            rerank_model: CrossEncoder model name (default: ms-marco-MiniLM-L-6-v2) [Task 0-ARCH.27]
        """
        logger.info("[FUSION-RAG] Initializing Fusion RAG service...")

        # Configuration
        self.parallel_workers = parallel_workers
        self.rrf_k = rrf_k
        self.enable_rerank = enable_rerank

        # Track which sources are available
        self.sources_available = {
            'pinecone': False,
            'bm25': False,
            'mongodb': False,
            'postgres': False
        }

        # Initialize Pinecone
        self._init_pinecone(pinecone_index_name)

        # Initialize BM25
        self._init_bm25(bm25_index_path)

        # Initialize MongoDB
        self._init_mongodb(mongodb_uri)

        # Initialize PostgreSQL
        self._init_postgres(postgres_uri)

        # Initialize CrossEncoder for re-ranking (Task 0-ARCH.27)
        self._init_crossencoder(rerank_model)

        # Initialize Query Expander (Task 0-ARCH.28)
        self._init_query_expander()

        # Log available sources
        available = [k for k, v in self.sources_available.items() if v]
        logger.info(f"[FUSION-RAG] Available sources: {available} ({len(available)}/4)")

        if len(available) == 0:
            logger.error("[FUSION-RAG] No retrieval sources available!")

    def _init_pinecone(self, index_name: str):
        """Initialize Pinecone dense retrieval"""
        if not PINECONE_AVAILABLE:
            logger.warning("[FUSION-RAG] Pinecone not available")
            return

        try:
            api_key = os.getenv('PINECONE_API_KEY')
            if not api_key:
                logger.warning("[FUSION-RAG] PINECONE_API_KEY not set")
                return

            self.pinecone_client = Pinecone(api_key=api_key)
            self.pinecone_index = self.pinecone_client.Index(index_name)
            self.sources_available['pinecone'] = True
            logger.info(f"[FUSION-RAG] ✓ Pinecone initialized (index: {index_name})")
        except Exception as e:
            logger.error(f"[FUSION-RAG] Failed to initialize Pinecone: {e}")

    def _init_bm25(self, index_path: Optional[str]):
        """Initialize BM25 sparse retrieval"""
        if not BM25_AVAILABLE:
            logger.warning("[FUSION-RAG] BM25 not available")
            return

        try:
            # Default path if not provided
            if index_path is None:
                index_path = os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    'data',
                    'bm25_index.pkl'
                )

            if not os.path.exists(index_path):
                logger.warning(f"[FUSION-RAG] BM25 index not found at {index_path}")
                logger.info("[FUSION-RAG] Run Task 0-ARCH.25 to build BM25 index")
                return

            with open(index_path, 'rb') as f:
                index_data = pickle.load(f)
                self.bm25_index = index_data['bm25']
                self.bm25_documents = index_data['documents']
                self.bm25_metadata = index_data['metadata']

            self.sources_available['bm25'] = True
            logger.info(f"[FUSION-RAG] ✓ BM25 initialized ({len(self.bm25_documents)} docs)")
        except Exception as e:
            logger.error(f"[FUSION-RAG] Failed to initialize BM25: {e}")

    def _init_mongodb(self, uri: Optional[str]):
        """Initialize MongoDB full-text search"""
        if not MONGODB_AVAILABLE:
            logger.warning("[FUSION-RAG] MongoDB not available")
            return

        try:
            if uri is None:
                uri = os.getenv('MONGODB_ATLAS_URI')

            if not uri:
                logger.warning("[FUSION-RAG] MongoDB URI not provided")
                return

            self.mongo_client = MongoClient(uri)
            self.mongo_db = self.mongo_client['test_failures']
            self.mongo_collection = self.mongo_db['failures']

            # Verify connection
            self.mongo_client.server_info()

            self.sources_available['mongodb'] = True
            logger.info("[FUSION-RAG] ✓ MongoDB initialized")
        except Exception as e:
            logger.error(f"[FUSION-RAG] Failed to initialize MongoDB: {e}")

    def _init_postgres(self, uri: Optional[str]):
        """Initialize PostgreSQL structured query"""
        if not POSTGRES_AVAILABLE:
            logger.warning("[FUSION-RAG] PostgreSQL not available")
            return

        try:
            if uri is None:
                # Build from env vars
                from urllib.parse import quote_plus
                pg_host = os.getenv('POSTGRES_HOST', 'localhost')
                pg_port = os.getenv('POSTGRES_PORT', '5432')
                pg_db = os.getenv('POSTGRES_DB', 'ddn_failures')
                pg_user = os.getenv('POSTGRES_USER', 'postgres')
                pg_pass = os.getenv('POSTGRES_PASSWORD', '')

                # URL-encode password to handle special characters
                pg_pass_encoded = quote_plus(pg_pass)
                uri = f"postgresql://{pg_user}:{pg_pass_encoded}@{pg_host}:{pg_port}/{pg_db}"

            self.postgres_engine = create_engine(uri)
            Session = sessionmaker(bind=self.postgres_engine)
            self.postgres_session = Session()

            # Verify connection
            self.postgres_session.execute("SELECT 1")

            self.sources_available['postgres'] = True
            logger.info("[FUSION-RAG] ✓ PostgreSQL initialized")
        except Exception as e:
            logger.error(f"[FUSION-RAG] Failed to initialize PostgreSQL: {e}")

    def _init_crossencoder(self, model_name: str):
        """
        Initialize CrossEncoder for re-ranking (Task 0-ARCH.27)

        Args:
            model_name: CrossEncoder model name (e.g., 'cross-encoder/ms-marco-MiniLM-L-6-v2')
        """
        if not CROSSENCODER_AVAILABLE:
            logger.warning("[FUSION-RAG] CrossEncoder not available")
            logger.warning("[FUSION-RAG] Install with: pip install sentence-transformers")
            self.cross_encoder = None
            return

        if not self.enable_rerank:
            logger.info("[FUSION-RAG] CrossEncoder re-ranking disabled")
            self.cross_encoder = None
            return

        try:
            logger.info(f"[FUSION-RAG] Loading CrossEncoder model: {model_name}")
            self.cross_encoder = CrossEncoder(model_name)
            logger.info("[FUSION-RAG] ✓ CrossEncoder initialized")
        except Exception as e:
            logger.error(f"[FUSION-RAG] Failed to initialize CrossEncoder: {e}")
            self.cross_encoder = None

    def _init_query_expander(self):
        """
        Initialize Query Expander (Task 0-ARCH.28)
        """
        if not QUERY_EXPANSION_AVAILABLE:
            logger.warning("[FUSION-RAG] Query expansion not available")
            self.query_expander = None
            return

        try:
            self.query_expander = QueryExpander(max_variations=3)
            logger.info("[FUSION-RAG] ✓ Query expander initialized")
        except Exception as e:
            logger.error(f"[FUSION-RAG] Failed to initialize query expander: {e}")
            self.query_expander = None

    def retrieve(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        expand_query: bool = False,
        top_k: int = 5,
        retrieve_k: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Main retrieval method combining all sources

        Args:
            query: User query string
            filters: Optional filters (category, date range, etc.)
            expand_query: Whether to expand query (default: False for now)
            top_k: Number of final results (default: 5)
            retrieve_k: Number of results per source (default: 50)

        Returns:
            List of top-k documents with scores and source attribution

        Example:
            >>> fusion_rag = FusionRAG()
            >>> results = fusion_rag.retrieve(
            ...     query="authentication error in middleware",
            ...     filters={'category': 'CODE_ERROR'},
            ...     top_k=5
            ... )
            >>> for doc in results:
            ...     print(f"{doc['source']}: {doc['text'][:100]}")
        """
        start_time = time.time()
        logger.info(f"[FUSION-RAG] Retrieving for query: {query[:100]}...")

        # Step 1: Query expansion (Task 0-ARCH.28)
        queries = [query]
        if expand_query and self.query_expander is not None:
            # Expand query with error category context
            error_category = filters.get('category') if filters else None
            queries = self.query_expander.expand(
                query,
                error_category=error_category,
                include_original=True
            )
            logger.info(f"[FUSION-RAG] Expanded to {len(queries)} query variations")
        elif expand_query:
            logger.warning("[FUSION-RAG] Query expansion requested but expander not available")

        # Step 2: Parallel retrieval from all available sources
        all_results = []
        for q in queries:
            results_by_source = self._parallel_retrieve(q, filters, retrieve_k)
            all_results.append(results_by_source)

        # Step 3: Merge results from all query variations (if expanded)
        merged_results = self._merge_query_variations(all_results)

        # Step 4: Reciprocal Rank Fusion
        fused_results = self._reciprocal_rank_fusion(merged_results, self.rrf_k)

        # Step 5: CrossEncoder Re-ranking (Task 0-ARCH.27)
        if self.cross_encoder is not None and len(fused_results) > 0:
            # Take top 50 for re-ranking (or all if less than 50)
            rerank_k = min(50, len(fused_results))
            top_for_rerank = fused_results[:rerank_k]

            # Get full documents for re-ranking
            docs_for_rerank = self._add_source_attribution(top_for_rerank, merged_results)

            # Re-rank with CrossEncoder
            reranked_docs = self._rerank(query, docs_for_rerank, top_k)
            final_results = reranked_docs
        else:
            # No re-ranking: just take top-k from RRF
            top_results = fused_results[:top_k]
            final_results = self._add_source_attribution(top_results, merged_results)

        elapsed = time.time() - start_time
        logger.info(f"[FUSION-RAG] Retrieved {len(final_results)} results in {elapsed:.2f}s")

        return final_results

    def _parallel_retrieve(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        top_k: int
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        Retrieve from all 4 sources in parallel

        Args:
            query: Query string
            filters: Optional filters
            top_k: Number of results per source

        Returns:
            {
                'pinecone': [(doc_id, score), ...],
                'bm25': [(doc_id, score), ...],
                'mongodb': [(doc_id, score), ...],
                'postgres': [(doc_id, score), ...]
            }
        """
        results = {
            'pinecone': [],
            'bm25': [],
            'mongodb': [],
            'postgres': []
        }

        # Create list of tasks for available sources
        tasks = []
        if self.sources_available['pinecone']:
            tasks.append(('pinecone', self._retrieve_pinecone, (query, top_k)))
        if self.sources_available['bm25']:
            tasks.append(('bm25', self._retrieve_bm25, (query, top_k)))
        if self.sources_available['mongodb']:
            tasks.append(('mongodb', self._retrieve_mongodb, (query, filters, top_k)))
        if self.sources_available['postgres']:
            tasks.append(('postgres', self._retrieve_postgres, (query, filters, top_k)))

        # Execute in parallel
        with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            future_to_source = {
                executor.submit(func, *args): source
                for source, func, args in tasks
            }

            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    results[source] = future.result()
                    logger.debug(f"[FUSION-RAG] {source}: {len(results[source])} results")
                except Exception as e:
                    logger.error(f"[FUSION-RAG] {source} failed: {e}")
                    results[source] = []

        return results

    def _retrieve_pinecone(self, query: str, top_k: int) -> List[Tuple[str, float]]:
        """
        Retrieve from Pinecone using dense vector search

        Args:
            query: Query string
            top_k: Number of results

        Returns:
            [(doc_id, similarity_score), ...]
        """
        if not self.sources_available['pinecone']:
            return []

        try:
            # Get embedding
            embedding = self._get_embedding(query)
            if embedding is None:
                return []

            # Query Pinecone
            response = self.pinecone_index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True
            )

            # Extract results
            results = [
                (match['id'], match['score'])
                for match in response.get('matches', [])
            ]

            return results

        except Exception as e:
            logger.error(f"[FUSION-RAG] Pinecone retrieval failed: {e}")
            return []

    def _retrieve_bm25(self, query: str, top_k: int) -> List[Tuple[str, float]]:
        """
        Retrieve from BM25 using sparse keyword search

        Args:
            query: Query string
            top_k: Number of results

        Returns:
            [(doc_id, bm25_score), ...]
        """
        if not self.sources_available['bm25']:
            return []

        try:
            # Tokenize query
            tokenized_query = query.lower().split()

            # Get BM25 scores
            scores = self.bm25_index.get_scores(tokenized_query)

            # Get top-k indices
            top_indices = scores.argsort()[-top_k:][::-1]

            # Build results with doc_id and score
            results = [
                (self.bm25_metadata[idx]['doc_id'], float(scores[idx]))
                for idx in top_indices
                if scores[idx] > 0  # Only include non-zero scores
            ]

            return results

        except Exception as e:
            logger.error(f"[FUSION-RAG] BM25 retrieval failed: {e}")
            return []

    def _retrieve_mongodb(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        top_k: int
    ) -> List[Tuple[str, float]]:
        """
        Retrieve from MongoDB using full-text search

        Args:
            query: Query string
            filters: Optional filters (category, date, etc.)
            top_k: Number of results

        Returns:
            [(doc_id, text_score), ...]
        """
        if not self.sources_available['mongodb']:
            return []

        try:
            # Build query
            mongo_query = {"$text": {"$search": query}}

            # Add filters
            if filters:
                if 'category' in filters:
                    mongo_query['error_category'] = filters['category']
                if 'date_from' in filters:
                    mongo_query['created_at'] = {'$gte': filters['date_from']}

            # Execute search
            cursor = self.mongo_collection.find(
                mongo_query,
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(top_k)

            # Build results
            results = [
                (str(doc['_id']), doc['score'])
                for doc in cursor
            ]

            return results

        except Exception as e:
            logger.error(f"[FUSION-RAG] MongoDB retrieval failed: {e}")
            return []

    def _retrieve_postgres(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        top_k: int
    ) -> List[Tuple[str, float]]:
        """
        Retrieve from PostgreSQL using structured query

        Args:
            query: Query string
            filters: Optional filters (category, date, confidence, etc.)
            top_k: Number of results

        Returns:
            [(doc_id, rank_score), ...]
        """
        if not self.sources_available['postgres']:
            return []

        try:
            # Build SQL query with ts_vector full-text search
            sql = """
                SELECT
                    id::text as doc_id,
                    ts_rank(search_vector, plainto_tsquery('english', :query)) as rank
                FROM failure_analysis
                WHERE search_vector @@ plainto_tsquery('english', :query)
            """

            params = {'query': query}

            # Add filters
            conditions = []
            if filters:
                if 'category' in filters:
                    conditions.append("error_category = :category")
                    params['category'] = filters['category']
                if 'date_from' in filters:
                    conditions.append("created_at >= :date_from")
                    params['date_from'] = filters['date_from']
                if 'confidence_min' in filters:
                    conditions.append("confidence_score >= :confidence_min")
                    params['confidence_min'] = filters['confidence_min']

            if conditions:
                sql += " AND " + " AND ".join(conditions)

            sql += " ORDER BY rank DESC LIMIT :top_k"
            params['top_k'] = top_k

            # Execute query
            result = self.postgres_session.execute(sql, params)

            # Build results
            results = [
                (row[0], float(row[1]))
                for row in result
            ]

            return results

        except Exception as e:
            logger.error(f"[FUSION-RAG] PostgreSQL retrieval failed: {e}")
            return []

    def _reciprocal_rank_fusion(
        self,
        results_by_source: Dict[str, List[Tuple[str, float]]],
        k: int = 60
    ) -> List[Tuple[str, float]]:
        """
        Fuse rankings from multiple sources using RRF

        Algorithm:
            For each document, calculate RRF score:
                RRF_score = Σ(1 / (k + rank_i))  across all sources

        Args:
            results_by_source: Results from each source
            k: RRF constant (default: 60)

        Returns:
            [(doc_id, rrf_score), ...] sorted by rrf_score descending

        Example:
            >>> results = {
            ...     'pinecone': [('doc_A', 0.95), ('doc_B', 0.88)],
            ...     'bm25': [('doc_B', 12.5), ('doc_A', 10.2)]
            ... }
            >>> fused = self._reciprocal_rank_fusion(results, k=60)
            >>> # doc_B gets higher RRF score (rank 2 + rank 1)
            >>> # doc_A gets lower RRF score (rank 1 + rank 2)
        """
        rrf_scores = {}

        # Calculate RRF scores
        for source, results in results_by_source.items():
            for rank, (doc_id, _) in enumerate(results, start=1):
                if doc_id not in rrf_scores:
                    rrf_scores[doc_id] = {
                        'score': 0.0,
                        'sources': []
                    }

                # RRF formula: 1 / (k + rank)
                rrf_contribution = 1 / (k + rank)
                rrf_scores[doc_id]['score'] += rrf_contribution
                rrf_scores[doc_id]['sources'].append({
                    'source': source,
                    'rank': rank,
                    'contribution': rrf_contribution
                })

        # Sort by RRF score descending
        sorted_docs = sorted(
            rrf_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )

        # Return as list of (doc_id, rrf_score)
        return [(doc_id, data['score']) for doc_id, data in sorted_docs]

    def _rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Re-rank documents using CrossEncoder (Task 0-ARCH.27)

        Uses a CrossEncoder model to precisely score query-document relevance.
        CrossEncoder encodes query+document together for better accuracy than
        separate bi-encoders (like those used in Pinecone).

        Args:
            query: User query string
            documents: List of document dicts with 'text' field
            top_k: Number of top documents to return

        Returns:
            Top-k documents sorted by relevance score

        Example:
            >>> docs = [
            ...     {'text': 'Authentication error in middleware', 'rrf_score': 0.05},
            ...     {'text': 'Database timeout', 'rrf_score': 0.04}
            ... ]
            >>> reranked = self._rerank("auth error", docs, top_k=1)
            >>> # First doc gets higher score due to better relevance
        """
        if self.cross_encoder is None:
            logger.warning("[FUSION-RAG] CrossEncoder not available - returning RRF results")
            return documents[:top_k]

        if not documents:
            return []

        try:
            start_time = time.time()

            # Prepare query-document pairs
            pairs = []
            for doc in documents:
                text = doc.get('text', '')
                if not text:
                    # Try metadata fields if text is empty
                    metadata = doc.get('metadata', {})
                    text = metadata.get('error_message', '') or metadata.get('root_cause', '')
                pairs.append((query, text[:512]))  # Limit to 512 chars for efficiency

            # Score all pairs with CrossEncoder
            scores = self.cross_encoder.predict(pairs)

            # Combine documents with scores
            docs_with_scores = []
            for i, doc in enumerate(documents):
                doc_copy = doc.copy()
                doc_copy['rerank_score'] = float(scores[i])
                docs_with_scores.append(doc_copy)

            # Sort by rerank score descending
            ranked_docs = sorted(
                docs_with_scores,
                key=lambda x: x['rerank_score'],
                reverse=True
            )

            # Take top-k
            top_docs = ranked_docs[:top_k]

            elapsed = time.time() - start_time
            logger.info(f"[FUSION-RAG] Re-ranked {len(documents)} docs → top {len(top_docs)} in {elapsed:.3f}s")

            return top_docs

        except Exception as e:
            logger.error(f"[FUSION-RAG] Re-ranking failed: {e}")
            # Fall back to RRF results
            return documents[:top_k]

    def _merge_query_variations(
        self,
        all_results: List[Dict[str, List[Tuple[str, float]]]]
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        Merge results from multiple query variations

        For now (Task 0-ARCH.24), we only have one query variation.
        This will be enhanced in Task 0-ARCH.28 (Query Expansion).

        Args:
            all_results: List of results_by_source for each query variation

        Returns:
            Merged results_by_source
        """
        if len(all_results) == 1:
            return all_results[0]

        # Merge by taking union and keeping best score per doc_id
        merged = {
            'pinecone': [],
            'bm25': [],
            'mongodb': [],
            'postgres': []
        }

        for source in merged.keys():
            doc_scores = {}

            # Collect all scores for each doc_id
            for results_by_source in all_results:
                for doc_id, score in results_by_source.get(source, []):
                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = score
                    else:
                        # Keep max score
                        doc_scores[doc_id] = max(doc_scores[doc_id], score)

            # Convert back to list and sort
            merged[source] = sorted(
                doc_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )

        return merged

    def _add_source_attribution(
        self,
        top_results: List[Tuple[str, float]],
        results_by_source: Dict[str, List[Tuple[str, float]]]
    ) -> List[Dict[str, Any]]:
        """
        Add source attribution and full document data to results

        Args:
            top_results: Top-k results from RRF [(doc_id, rrf_score), ...]
            results_by_source: Original results from each source

        Returns:
            List of document dicts with source attribution
        """
        final_results = []

        for doc_id, rrf_score in top_results:
            # Find which sources returned this doc
            sources_info = []
            for source, results in results_by_source.items():
                for rank, (result_doc_id, score) in enumerate(results, start=1):
                    if result_doc_id == doc_id:
                        sources_info.append({
                            'source': source,
                            'rank': rank,
                            'score': score
                        })
                        break

            # Get full document data
            doc_data = self._get_document_by_id(doc_id, sources_info)

            if doc_data:
                doc_data['rrf_score'] = rrf_score
                doc_data['sources'] = sources_info
                doc_data['doc_id'] = doc_id
                final_results.append(doc_data)

        return final_results

    def _get_document_by_id(
        self,
        doc_id: str,
        sources_info: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Get full document data by ID

        Try each source that returned this document until we find it.

        Args:
            doc_id: Document ID
            sources_info: List of sources that returned this doc

        Returns:
            Document dict or None
        """
        # Try each source in order of preference
        for source_info in sources_info:
            source = source_info['source']

            try:
                if source == 'pinecone' and self.sources_available['pinecone']:
                    # Fetch from Pinecone
                    response = self.pinecone_index.fetch([doc_id])
                    if doc_id in response.get('vectors', {}):
                        vector_data = response['vectors'][doc_id]
                        return {
                            'text': vector_data.get('metadata', {}).get('text', ''),
                            'metadata': vector_data.get('metadata', {}),
                            'primary_source': 'pinecone'
                        }

                elif source == 'bm25' and self.sources_available['bm25']:
                    # Find in BM25 documents
                    for idx, meta in enumerate(self.bm25_metadata):
                        if meta['doc_id'] == doc_id:
                            return {
                                'text': self.bm25_documents[idx],
                                'metadata': meta,
                                'primary_source': 'bm25'
                            }

                elif source == 'mongodb' and self.sources_available['mongodb']:
                    # Fetch from MongoDB
                    from bson import ObjectId
                    doc = self.mongo_collection.find_one({'_id': ObjectId(doc_id)})
                    if doc:
                        return {
                            'text': doc.get('error_message', ''),
                            'metadata': {
                                'build_id': doc.get('build_id'),
                                'error_category': doc.get('error_category'),
                                'root_cause': doc.get('root_cause'),
                                'fix_recommendation': doc.get('fix_recommendation')
                            },
                            'primary_source': 'mongodb'
                        }

                elif source == 'postgres' and self.sources_available['postgres']:
                    # Fetch from PostgreSQL
                    result = self.postgres_session.execute(
                        "SELECT * FROM failure_analysis WHERE id = :id",
                        {'id': int(doc_id)}
                    )
                    row = result.fetchone()
                    if row:
                        return {
                            'text': row.error_message,
                            'metadata': {
                                'build_id': row.build_id,
                                'error_category': row.error_category,
                                'root_cause': row.root_cause,
                                'fix_recommendation': row.fix_recommendation,
                                'confidence_score': row.confidence_score
                            },
                            'primary_source': 'postgres'
                        }

            except Exception as e:
                logger.warning(f"[FUSION-RAG] Failed to fetch {doc_id} from {source}: {e}")
                continue

        # Fallback: return minimal data
        logger.warning(f"[FUSION-RAG] Could not fetch full data for {doc_id}")
        return {
            'text': f"Document {doc_id}",
            'metadata': {},
            'primary_source': 'unknown'
        }

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get OpenAI embedding for text

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None
        """
        if not OPENAI_AVAILABLE:
            logger.error("[FUSION-RAG] OpenAI not available for embeddings")
            return None

        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.error("[FUSION-RAG] OPENAI_API_KEY not set")
                return None

            openai.api_key = api_key

            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )

            return response.data[0].embedding

        except Exception as e:
            logger.error(f"[FUSION-RAG] Failed to get embedding: {e}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about available sources and performance

        Returns:
            dict with source availability and stats
        """
        stats = {
            'sources_available': self.sources_available,
            'num_sources': sum(self.sources_available.values()),
            'config': {
                'rrf_k': self.rrf_k,
                'parallel_workers': self.parallel_workers
            }
        }

        # Add BM25 stats
        if self.sources_available['bm25']:
            stats['bm25'] = {
                'num_documents': len(self.bm25_documents)
            }

        return stats


# Singleton instance (optional)
_fusion_rag_instance = None

def get_fusion_rag(**kwargs) -> FusionRAG:
    """
    Get singleton FusionRAG instance

    Args:
        **kwargs: Arguments to pass to FusionRAG constructor

    Returns:
        FusionRAG instance
    """
    global _fusion_rag_instance

    if _fusion_rag_instance is None:
        _fusion_rag_instance = FusionRAG(**kwargs)

    return _fusion_rag_instance


if __name__ == '__main__':
    # Test initialization
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Fusion RAG Service - Initialization Test")
    print("=" * 60)

    fusion_rag = FusionRAG()

    print("\nStatistics:")
    import json
    print(json.dumps(fusion_rag.get_statistics(), indent=2))

    # Test query (if at least one source is available)
    if sum(fusion_rag.sources_available.values()) > 0:
        print("\n" + "=" * 60)
        print("Test Query")
        print("=" * 60)

        results = fusion_rag.retrieve(
            query="authentication error middleware",
            top_k=3
        )

        print(f"\nRetrieved {len(results)} results:")
        for i, doc in enumerate(results, 1):
            print(f"\n{i}. RRF Score: {doc['rrf_score']:.4f}")
            print(f"   Primary Source: {doc['primary_source']}")
            print(f"   Sources: {[s['source'] for s in doc['sources']]}")
            print(f"   Text: {doc['text'][:100]}...")
    else:
        print("\nNo sources available for testing. Please configure at least one source.")
