"""
CRAG Verifier - Core Implementation (Task 0-ARCH.14)

Implements Corrective Retrieval Augmented Generation verification layer
for ReAct agent outputs.

Classes:
- ConfidenceScorer: Multi-dimensional confidence scoring
- CRAGVerifier: Main verification and routing orchestrator

Author: AI Analysis System
Date: 2025-11-02
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Import self-correction module (Task 0-ARCH.15)
try:
    from .self_correction import SelfCorrector
    SELF_CORRECTION_AVAILABLE = True
except ImportError:
    SELF_CORRECTION_AVAILABLE = False
    logger.warning("SelfCorrector not available - low confidence will escalate to HITL")

# Import HITL manager module (Task 0-ARCH.16)
try:
    from .hitl_manager import HITLManager
    HITL_MANAGER_AVAILABLE = True
except ImportError:
    HITL_MANAGER_AVAILABLE = False
    logger.warning("HITLManager not available - medium confidence will return provisional answers")

# Import web search fallback module (Task 0-ARCH.17)
try:
    from .web_search_fallback import WebSearchFallback
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    logger.warning("WebSearchFallback not available - very low confidence will escalate to HITL")

# Import metrics tracker (Task 0-ARCH.19)
try:
    from .crag_metrics import get_metrics
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    logger.warning("CRAG Metrics not available - metrics will not be tracked")


class ConfidenceScorer:
    """
    Multi-dimensional confidence scorer for CRAG verification

    Calculates 5 confidence components:
    1. Relevance Score (weight: 0.25) - Document relevance
    2. Consistency Score (weight: 0.20) - Document agreement
    3. Grounding Score (weight: 0.25) - No hallucination
    4. Completeness Score (weight: 0.15) - All required components
    5. Classification Confidence (weight: 0.15) - ReAct's confidence
    """

    def __init__(self):
        # Default weights (tunable per error category)
        self.weights = {
            'relevance': 0.25,
            'consistency': 0.20,
            'grounding': 0.25,
            'completeness': 0.15,
            'classification': 0.15
        }

        # Required answer components per category
        self.required_components = {
            'CODE_ERROR': ['root_cause', 'fix_steps', 'code_location', 'verification'],
            'INFRA_ERROR': ['root_cause', 'fix_steps', 'verification'],
            'CONFIG_ERROR': ['root_cause', 'fix_steps', 'config_location', 'verification'],
            'DEPENDENCY_ERROR': ['root_cause', 'fix_steps', 'verification'],
            'TEST_ERROR': ['root_cause', 'fix_steps', 'verification'],
            'UNKNOWN': ['root_cause', 'fix_steps']
        }

    def calculate_relevance_score(self, retrieved_docs: List[Dict]) -> float:
        """
        Calculate relevance score based on document similarity scores

        Args:
            retrieved_docs: List of documents with 'similarity_score' key

        Returns:
            float: Average similarity score (0.0-1.0)
        """
        if not retrieved_docs:
            logger.warning("No documents retrieved - relevance score 0.0")
            return 0.0

        # Extract similarity scores
        similarity_scores = []
        for doc in retrieved_docs:
            score = doc.get('similarity_score', doc.get('score', 0.0))
            similarity_scores.append(score)

        if not similarity_scores:
            return 0.0

        # Average of top-k documents
        relevance = sum(similarity_scores) / len(similarity_scores)

        logger.debug(f"Relevance score: {relevance:.3f} from {len(similarity_scores)} docs")
        return min(1.0, max(0.0, relevance))  # Clamp to [0, 1]

    def calculate_consistency_score(self, retrieved_docs: List[Dict],
                                   generated_answer: str) -> float:
        """
        Calculate consistency score - do retrieved documents agree?

        Args:
            retrieved_docs: List of retrieved documents
            generated_answer: The generated answer text

        Returns:
            float: Consistency score (0.0-1.0)
        """
        if not retrieved_docs or len(retrieved_docs) < 2:
            # Only one doc - assume consistent (1.0)
            return 1.0

        # Extract key terms from documents
        doc_texts = [doc.get('text', '') for doc in retrieved_docs]

        # Simple heuristic: Check for common keywords across documents
        # More sophisticated: Use embedding similarity between docs
        all_terms = []
        for text in doc_texts:
            # Extract important terms (simple word extraction)
            terms = set(re.findall(r'\b\w{4,}\b', text.lower()))
            all_terms.append(terms)

        if not all_terms:
            return 0.5  # Neutral - can't determine

        # Calculate pairwise overlap
        overlaps = []
        for i in range(len(all_terms)):
            for j in range(i + 1, len(all_terms)):
                if all_terms[i] and all_terms[j]:
                    overlap = len(all_terms[i] & all_terms[j]) / len(all_terms[i] | all_terms[j])
                    overlaps.append(overlap)

        if not overlaps:
            return 0.5

        consistency = sum(overlaps) / len(overlaps)

        logger.debug(f"Consistency score: {consistency:.3f} from {len(overlaps)} pairs")
        return min(1.0, max(0.0, consistency))

    def calculate_grounding_score(self, generated_answer: str,
                                  retrieved_docs: List[Dict]) -> float:
        """
        Calculate grounding score - is answer supported by retrieved docs?

        Args:
            generated_answer: The generated answer text
            retrieved_docs: List of retrieved documents

        Returns:
            float: Grounding score (0.0-1.0)
        """
        if not retrieved_docs:
            logger.warning("No documents for grounding check - score 0.0")
            return 0.0

        if not generated_answer or len(generated_answer.strip()) == 0:
            return 0.0

        # Extract key facts from answer (sentences with actionable content)
        answer_sentences = [s.strip() for s in generated_answer.split('.') if len(s.strip()) > 20]

        if not answer_sentences:
            return 0.5  # Short answer, hard to verify

        # Combine all retrieved doc text
        all_doc_text = ' '.join([doc.get('text', '') for doc in retrieved_docs]).lower()

        # Check how many answer sentences have support in docs
        grounded_count = 0
        for sentence in answer_sentences:
            # Extract key terms from sentence
            key_terms = set(re.findall(r'\b\w{4,}\b', sentence.lower()))

            # Check if significant terms appear in documents
            if key_terms:
                matched_terms = sum(1 for term in key_terms if term in all_doc_text)
                # If >50% of terms found in docs, consider grounded
                if matched_terms / len(key_terms) > 0.5:
                    grounded_count += 1

        grounding = grounded_count / len(answer_sentences) if answer_sentences else 0.0

        logger.debug(f"Grounding score: {grounding:.3f} ({grounded_count}/{len(answer_sentences)} sentences)")
        return min(1.0, max(0.0, grounding))

    def calculate_completeness_score(self, react_result: Dict,
                                     error_category: str) -> float:
        """
        Calculate completeness score - does answer have all required components?

        Args:
            react_result: ReAct agent result dictionary
            error_category: Error category (CODE_ERROR, INFRA_ERROR, etc.)

        Returns:
            float: Completeness score (0.0-1.0)
        """
        required = self.required_components.get(error_category,
                                               self.required_components['UNKNOWN'])

        present_count = 0
        total_count = len(required)

        # Check each required component
        for component in required:
            if component == 'root_cause':
                if react_result.get('root_cause') and len(react_result['root_cause']) > 20:
                    present_count += 1

            elif component == 'fix_steps':
                fix_rec = react_result.get('fix_recommendation', '')
                if fix_rec and len(fix_rec) > 30:
                    present_count += 1

            elif component == 'code_location':
                # Check if file paths mentioned
                root_cause = react_result.get('root_cause', '')
                if re.search(r'[\w/\\]+\.py|[\w/\\]+\.java|[\w/\\]+\.js', root_cause):
                    present_count += 1

            elif component == 'config_location':
                # Check if config files mentioned
                root_cause = react_result.get('root_cause', '')
                if re.search(r'\.env|\.yaml|\.json|\.config|\.properties', root_cause):
                    present_count += 1

            elif component == 'verification':
                # Check if verification steps mentioned
                fix_rec = react_result.get('fix_recommendation', '')
                verify_keywords = ['test', 'verify', 'check', 'confirm', 'validate']
                if any(keyword in fix_rec.lower() for keyword in verify_keywords):
                    present_count += 1

        completeness = present_count / total_count if total_count > 0 else 0.0

        logger.debug(f"Completeness score: {completeness:.3f} ({present_count}/{total_count} components)")
        return min(1.0, max(0.0, completeness))

    def calculate_all_scores(self, react_result: Dict,
                            retrieved_docs: List[Dict]) -> Dict[str, Any]:
        """
        Calculate all confidence scores and combined confidence

        Args:
            react_result: ReAct agent result dictionary
            retrieved_docs: List of retrieved documents

        Returns:
            dict: {
                'overall_confidence': float,
                'components': {
                    'relevance': float,
                    'consistency': float,
                    'grounding': float,
                    'completeness': float,
                    'classification': float
                }
            }
        """
        # Build answer text
        answer = f"{react_result.get('root_cause', '')} {react_result.get('fix_recommendation', '')}"
        error_category = react_result.get('error_category', 'UNKNOWN')
        classification_conf = react_result.get('classification_confidence', 0.5)

        # Calculate individual scores
        relevance = self.calculate_relevance_score(retrieved_docs)
        consistency = self.calculate_consistency_score(retrieved_docs, answer)
        grounding = self.calculate_grounding_score(answer, retrieved_docs)
        completeness = self.calculate_completeness_score(react_result, error_category)

        # Weighted average
        overall_confidence = (
            self.weights['relevance'] * relevance +
            self.weights['consistency'] * consistency +
            self.weights['grounding'] * grounding +
            self.weights['completeness'] * completeness +
            self.weights['classification'] * classification_conf
        )

        result = {
            'overall_confidence': round(overall_confidence, 3),
            'components': {
                'relevance': round(relevance, 3),
                'consistency': round(consistency, 3),
                'grounding': round(grounding, 3),
                'completeness': round(completeness, 3),
                'classification': round(classification_conf, 3)
            },
            'weights': self.weights
        }

        logger.info(f"CRAG Confidence: {overall_confidence:.3f} | "
                   f"R={relevance:.2f} C={consistency:.2f} G={grounding:.2f} "
                   f"Cp={completeness:.2f} Cl={classification_conf:.2f}")

        return result


class CRAGVerifier:
    """
    Main CRAG verification orchestrator

    Routes ReAct agent results based on confidence thresholds:
    - HIGH (≥0.85): Pass through
    - MEDIUM (0.65-0.85): Queue for HITL
    - LOW (0.40-0.65): Attempt self-correction
    - VERY_LOW (<0.40): Web search fallback
    """

    # Threshold constants
    THRESHOLD_HIGH = 0.85
    THRESHOLD_MEDIUM = 0.65
    THRESHOLD_LOW = 0.40

    def __init__(self):
        self.confidence_scorer = ConfidenceScorer()

        # Task 0-ARCH.15: Self-correction module
        if SELF_CORRECTION_AVAILABLE:
            try:
                self.self_corrector = SelfCorrector()
                logger.info("✓ SelfCorrector initialized (query expansion + re-retrieval)")
            except Exception as e:
                logger.error(f"✗ SelfCorrector initialization failed: {e}")
                self.self_corrector = None
        else:
            self.self_corrector = None

        # Task 0-ARCH.16: HITL manager
        if HITL_MANAGER_AVAILABLE:
            try:
                self.hitl_manager = HITLManager()
                logger.info("✓ HITLManager initialized (PostgreSQL queue + notifications)")
            except Exception as e:
                logger.error(f"✗ HITLManager initialization failed: {e}")
                self.hitl_manager = None
        else:
            self.hitl_manager = None

        # Task 0-ARCH.17: Web search fallback
        if WEB_SEARCH_AVAILABLE:
            try:
                self.web_searcher = WebSearchFallback()
                logger.info("✓ WebSearchFallback initialized (Google/Bing/DuckDuckGo)")
            except Exception as e:
                logger.error(f"✗ WebSearchFallback initialization failed: {e}")
                self.web_searcher = None
        else:
            self.web_searcher = None

        logger.info("CRAGVerifier initialized")

    def verify(self, react_result: Dict, retrieved_docs: List[Dict],
              failure_data: Dict) -> Dict[str, Any]:
        """
        Main verification method - verifies ReAct agent output

        Args:
            react_result: ReAct agent result dictionary
            retrieved_docs: List of retrieved documents from Pinecone
            failure_data: Original failure data context

        Returns:
            dict: {
                'status': 'PASS' | 'HITL' | 'CORRECTED' | 'WEB_SEARCH',
                'answer': verified_answer,
                'confidence': float,
                'confidence_level': 'HIGH' | 'MEDIUM' | 'LOW' | 'VERY_LOW',
                'verification_metadata': {...}
            }
        """
        logger.info(f"[CRAG] Verifying ReAct result for failure: {failure_data.get('build_id', 'unknown')}")

        # Calculate multi-dimensional confidence
        scores = self.confidence_scorer.calculate_all_scores(react_result, retrieved_docs)
        confidence = scores['overall_confidence']

        # Route based on confidence threshold
        if confidence >= self.THRESHOLD_HIGH:
            result = self._pass_through(react_result, confidence, scores, failure_data)

        elif confidence >= self.THRESHOLD_MEDIUM:
            result = self._queue_hitl(react_result, confidence, scores, failure_data)

        elif confidence >= self.THRESHOLD_LOW:
            result = self._self_correct(react_result, confidence, scores, failure_data)

        else:
            result = self._web_search(react_result, confidence, scores, failure_data)

        # Task 0-ARCH.19: Record metrics
        if METRICS_AVAILABLE:
            try:
                metrics = get_metrics()
                metrics.record_verification(result)
            except Exception as e:
                logger.warning(f"Failed to record metrics: {e}")

        return result

    def _pass_through(self, react_result: Dict, confidence: float,
                     scores: Dict, failure_data: Dict) -> Dict[str, Any]:
        """
        HIGH confidence (≥0.85) - Pass through immediately

        Expected: 60-70% of cases
        """
        logger.info(f"[CRAG] ✓ HIGH confidence ({confidence:.3f}) - PASS THROUGH")

        return {
            'status': 'PASS',
            'confidence_level': 'HIGH',
            'answer': react_result,
            'confidence': confidence,
            'action_taken': 'pass_through',
            'verification_metadata': {
                'timestamp': datetime.now().isoformat(),
                'confidence_scores': scores,
                'threshold': self.THRESHOLD_HIGH,
                'reasoning': f'High confidence ({confidence:.3f} ≥ {self.THRESHOLD_HIGH})'
            }
        }

    def _queue_hitl(self, react_result: Dict, confidence: float,
                   scores: Dict, failure_data: Dict) -> Dict[str, Any]:
        """
        MEDIUM confidence (0.65-0.85) - Queue for human review

        Expected: 20-30% of cases
        """
        logger.info(f"[CRAG] ⚠ MEDIUM confidence ({confidence:.3f}) - QUEUE FOR HITL")

        # Calculate priority
        priority = self._calculate_priority(confidence, failure_data)

        # Task 0-ARCH.16: Queue in HITL manager
        if self.hitl_manager:
            try:
                queue_item = self.hitl_manager.queue(
                    react_result=react_result,
                    confidence=confidence,
                    confidence_scores=scores,
                    failure_data=failure_data,
                    priority=priority
                )
                logger.info(f"[CRAG] ✓ Queued in HITL (id={queue_item.get('id')}, priority={priority})")

                # Task 0-ARCH.19: Record HITL queue metrics
                if METRICS_AVAILABLE:
                    try:
                        metrics = get_metrics()
                        metrics.record_hitl_queue(priority=priority)
                    except Exception as e:
                        logger.warning(f"Failed to record HITL metrics: {e}")

                hitl_metadata = {
                    'queue_id': queue_item.get('id'),
                    'timestamp': queue_item.get('created_at'),
                    'confidence': confidence,
                    'concerns': queue_item.get('concerns', []),
                    'priority': priority,
                    'confidence_scores': scores,
                    'sla_deadline': queue_item.get('sla_deadline')
                }
            except Exception as e:
                logger.error(f"[CRAG] Failed to queue in HITL: {e}")
                hitl_metadata = {
                    'timestamp': datetime.now().isoformat(),
                    'confidence': confidence,
                    'priority': priority,
                    'confidence_scores': scores,
                    'error': str(e)
                }
        else:
            logger.warning("[CRAG] HITL manager not available - returning provisional answer")
            hitl_metadata = {
                'timestamp': datetime.now().isoformat(),
                'confidence': confidence,
                'priority': priority,
                'confidence_scores': scores
            }

        return {
            'status': 'HITL',
            'confidence_level': 'MEDIUM',
            'answer': react_result,  # Provisional answer
            'confidence': confidence,
            'action_taken': 'queued_for_hitl',
            'verification_metadata': hitl_metadata,
            'review_url': f"/review/{failure_data.get('build_id', 'unknown')}"
        }

    def _self_correct(self, react_result: Dict, confidence: float,
                     scores: Dict, failure_data: Dict) -> Dict[str, Any]:
        """
        LOW confidence (0.40-0.65) - Attempt self-correction

        Expected: 10-15% of cases
        """
        logger.info(f"[CRAG] ↻ LOW confidence ({confidence:.3f}) - ATTEMPTING SELF-CORRECTION")

        # Task 0-ARCH.15: Self-correction via query expansion + re-retrieval
        if self.self_corrector:
            correction_result = self.self_corrector.correct(
                react_result, scores, failure_data
            )

            # Task 0-ARCH.19: Record self-correction metrics
            if METRICS_AVAILABLE:
                try:
                    metrics = get_metrics()
                    metrics.record_self_correction(
                        success=correction_result['improved'],
                        original_confidence=confidence,
                        new_confidence=correction_result.get('new_confidence')
                    )
                except Exception as e:
                    logger.warning(f"Failed to record self-correction metrics: {e}")

            if correction_result['improved']:
                logger.info(f"[CRAG] ✓ Self-correction successful: "
                          f"{confidence:.3f} → {correction_result['new_confidence']:.3f}")
                return {
                    'status': 'CORRECTED',
                    'confidence_level': 'CORRECTED',
                    'answer': correction_result['corrected_answer'],
                    'confidence': correction_result['new_confidence'],
                    'action_taken': 'self_correction',
                    'verification_metadata': {
                        'timestamp': datetime.now().isoformat(),
                        'original_confidence': confidence,
                        'new_confidence': correction_result['new_confidence'],
                        'correction_method': correction_result.get('method', 'query_expansion'),
                        'confidence_scores': scores
                    }
                }
            else:
                # Correction failed - escalate to HITL
                logger.warning("[CRAG] Self-correction failed - escalating to HITL")
                return self._queue_hitl(react_result, confidence, scores, failure_data)

        else:
            # Self-corrector not available - escalate to HITL
            logger.warning("[CRAG] Self-corrector not available - escalating to HITL")
            return self._queue_hitl(react_result, confidence, scores, failure_data)

    def _web_search(self, react_result: Dict, confidence: float,
                   scores: Dict, failure_data: Dict) -> Dict[str, Any]:
        """
        VERY LOW confidence (<0.40) - Web search fallback

        Expected: 5-10% of cases
        """
        logger.info(f"[CRAG] 🌐 VERY LOW confidence ({confidence:.3f}) - WEB SEARCH FALLBACK")

        # Task 0-ARCH.17: Web search fallback
        if self.web_searcher:
            try:
                search_result = self.web_searcher.fallback_search(
                    react_result, scores, failure_data
                )

                # Task 0-ARCH.19: Record web search metrics
                if METRICS_AVAILABLE:
                    try:
                        metrics = get_metrics()
                        metrics.record_web_search(
                            success=search_result['improved'],
                            original_confidence=confidence,
                            new_confidence=search_result.get('new_confidence')
                        )
                    except Exception as e:
                        logger.warning(f"Failed to record web search metrics: {e}")

                if search_result['improved']:
                    # Web search succeeded
                    new_confidence = search_result['new_confidence']
                    logger.info(f"[CRAG] ✓ Web search successful: {confidence:.3f} → {new_confidence:.3f}")

                    return {
                        'status': 'WEB_SEARCH',
                        'confidence_level': 'WEB_ENHANCED',
                        'answer': search_result['enhanced_answer'],
                        'confidence': new_confidence,
                        'action_taken': 'web_search_fallback',
                        'verification_metadata': {
                            'timestamp': datetime.now().isoformat(),
                            'original_confidence': confidence,
                            'new_confidence': new_confidence,
                            'web_sources': search_result.get('web_sources', []),
                            'search_engine': search_result.get('search_engine', 'unknown'),
                            'search_query': search_result.get('search_query', ''),
                            'improvement_delta': search_result.get('improvement_delta', 0.0),
                            'confidence_scores': scores
                        }
                    }
                else:
                    # Web search failed to improve - high-priority HITL
                    logger.warning("[CRAG] Web search failed to improve confidence - high-priority HITL")
                    hitl_result = self._queue_hitl(react_result, confidence, scores, failure_data)
                    hitl_result['verification_metadata']['priority'] = 'high'
                    hitl_result['verification_metadata']['reason'] = 'web_search_failed'
                    hitl_result['verification_metadata']['web_sources'] = search_result.get('web_sources', [])
                    return hitl_result

            except Exception as e:
                logger.error(f"[CRAG] Web search error: {e}")
                hitl_result = self._queue_hitl(react_result, confidence, scores, failure_data)
                hitl_result['verification_metadata']['priority'] = 'high'
                hitl_result['verification_metadata']['reason'] = 'web_search_error'
                hitl_result['verification_metadata']['error'] = str(e)
                return hitl_result

        else:
            # Web searcher not available - high-priority HITL
            logger.warning("[CRAG] Web searcher not available - high-priority HITL")
            hitl_result = self._queue_hitl(react_result, confidence, scores, failure_data)
            hitl_result['verification_metadata']['priority'] = 'high'
            hitl_result['verification_metadata']['reason'] = 'web_search_unavailable'
            return hitl_result

    def _calculate_priority(self, confidence: float, failure_data: Dict) -> str:
        """
        Calculate HITL review priority based on confidence and error context

        Returns:
            'high' | 'medium' | 'low'
        """
        # High priority if:
        # - Very low confidence (close to self-correction threshold)
        # - Critical error category
        # - Production environment

        if confidence < 0.70:
            return 'high'

        error_category = failure_data.get('error_category', '')
        if error_category in ['INFRA_ERROR', 'CONFIG_ERROR']:
            return 'high'

        return 'medium'

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get CRAG verification statistics (for monitoring)

        Returns:
            dict: Statistics about verification outcomes
        """
        # Task 0-ARCH.19: Delegate to metrics tracker
        if METRICS_AVAILABLE:
            try:
                metrics = get_metrics()
                return metrics.get_statistics()
            except Exception as e:
                logger.error(f"Failed to get metrics: {e}")
                return {'error': str(e)}
        else:
            return {
                'error': 'Metrics not available',
                'total_verifications': 0,
                'pass_through_count': 0,
                'hitl_count': 0,
                'self_correction_count': 0,
                'web_search_count': 0,
                'average_confidence': 0.0
            }
