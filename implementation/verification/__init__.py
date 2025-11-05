"""
CRAG (Corrective Retrieval Augmented Generation) Verification Module

This module provides verification and quality assurance for ReAct agent outputs
through multi-dimensional confidence scoring and intelligent routing.

Main Components:
- CRAGVerifier: Main verification orchestrator
- ConfidenceScorer: Multi-dimensional confidence scoring
- SelfCorrector: Query expansion and re-retrieval (Task 0-ARCH.15)
- HITLManager: Human-in-the-loop queue management (Task 0-ARCH.16)
- WebSearchFallback: External search integration (Task 0-ARCH.17)
- CRAGMetrics: Performance metrics tracking (Task 0-ARCH.19)

Tasks:
- 0-ARCH.14: Core CRAG verifier and confidence scorer
- 0-ARCH.15: Self-correction implementation
- 0-ARCH.16: HITL queue implementation
- 0-ARCH.17: Web search fallback
- 0-ARCH.18: Integration with ai_analysis_service
- 0-ARCH.19: CRAG evaluation metrics
"""

from .crag_verifier import CRAGVerifier, ConfidenceScorer
from .self_correction import SelfCorrector
from .hitl_manager import HITLManager, HITLPriority, HITLStatus
from .web_search_fallback import WebSearchFallback
from .crag_metrics import CRAGMetrics, get_metrics, reset_metrics

__all__ = [
    'CRAGVerifier', 'ConfidenceScorer', 'SelfCorrector',
    'HITLManager', 'HITLPriority', 'HITLStatus',
    'WebSearchFallback',
    'CRAGMetrics', 'get_metrics', 'reset_metrics'
]
__version__ = '1.4.0'  # Task 0-ARCH.19: Added CRAGMetrics
