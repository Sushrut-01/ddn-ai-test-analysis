# CRAG Verification Layer Design

**Task**: 0-ARCH.13
**Status**: Design Phase
**Date**: 2025-11-02
**Priority**: CRITICAL

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [CRAG Overview](#crag-overview)
3. [Confidence Scoring Methodology](#confidence-scoring-methodology)
4. [Threshold Definitions](#threshold-definitions)
5. [Verification Workflow](#verification-workflow)
6. [Integration with ReAct Agent](#integration-with-react-agent)
7. [Implementation Architecture](#implementation-architecture)
8. [Evaluation Metrics](#evaluation-metrics)
9. [Implementation Plan](#implementation-plan)

---

## Executive Summary

This document defines the architecture for implementing **Corrective Retrieval Augmented Generation (CRAG)** as a verification layer for the ReAct agent. CRAG enhances the reliability of AI-generated answers by:

1. **Assessing Confidence**: Scoring each answer's confidence (0.0-1.0)
2. **Triggering Actions**: Based on confidence thresholds
   - **High (≥ 0.85)**: Pass through ✓
   - **Medium (0.65-0.85)**: Human-in-the-Loop (HITL) ⚠️
   - **Low (< 0.65)**: Self-Correction ↻
3. **Improving Quality**: Through corrective actions before delivery to users

**Goal**: Achieve >95% accuracy with CRAG compared to ~85-90% without it.

---

## CRAG Overview

### What is CRAG?

**Corrective Retrieval Augmented Generation (CRAG)** is an advanced RAG technique that adds a verification and correction layer to traditional RAG systems.

**Traditional RAG Flow**:
```
Query → Retrieval → LLM Generation → Answer
```

**CRAG Flow**:
```
Query → Retrieval → LLM Generation → Verification → Corrective Action → Answer
                                           ↓
                                   [High Conf: Pass Through]
                                   [Medium Conf: HITL]
                                   [Low Conf: Self-Correct]
```

### Why CRAG for ReAct Agent?

The ReAct agent already provides:
- ✓ Multi-step reasoning
- ✓ Context-aware routing
- ✓ Self-correction for tool failures
- ✓ RAG integration

**CRAG adds**:
- ✓ **Answer quality verification** (not just tool execution)
- ✓ **Confidence-based routing** to HITL or self-correction
- ✓ **Quality guarantees** before delivering to users
- ✓ **Continuous improvement** through feedback loops

---

## Confidence Scoring Methodology

### Multi-Dimensional Confidence Score

Confidence is calculated as a **weighted average** of multiple factors:

```python
confidence = (
    w1 * relevance_score +
    w2 * consistency_score +
    w3 * grounding_score +
    w4 * completeness_score +
    w5 * classification_confidence
)
```

**Where:**
- `w1-w5` are weights (sum = 1.0)
- Each score ∈ [0.0, 1.0]

---

### 1. Relevance Score (Weight: 0.25)

**Measures**: How relevant the retrieved documents are to the error

**Calculation**:
```python
relevance_score = average([
    doc['similarity_score'] for doc in top_k_documents
])
```

**Interpretation**:
- **> 0.90**: Highly relevant documents found
- **0.70-0.90**: Moderately relevant
- **< 0.70**: Low relevance - may need query expansion

**Example**:
- Error: "401 Unauthorized"
- Top 3 docs: [0.92, 0.87, 0.85]
- Relevance: (0.92 + 0.87 + 0.85) / 3 = **0.88** ✓

---

### 2. Consistency Score (Weight: 0.20)

**Measures**: Whether retrieved documents agree with each other

**Calculation**:
```python
# Generate multiple answer variations
answers = [generate_answer(doc) for doc in top_k_documents]

# Calculate semantic similarity between answers
consistency_score = average_pairwise_similarity(answers)
```

**Interpretation**:
- **> 0.85**: All documents suggest same solution
- **0.60-0.85**: Some variation but generally aligned
- **< 0.60**: Conflicting information - needs human review

**Example**:
- Doc 1: "Update token expiration to 1 hour"
- Doc 2: "Fix token validation - set expiration to 3600s"
- Doc 3: "Increase auth token TTL to 1h"
- Consistency: **0.92** (all say same thing in different ways)

---

### 3. Grounding Score (Weight: 0.25)

**Measures**: Whether the answer is grounded in retrieved documents (no hallucination)

**Calculation**:
```python
# Extract key facts from answer
answer_facts = extract_facts(generated_answer)

# Check if each fact is supported by retrieved documents
grounding_score = sum([
    is_supported(fact, retrieved_docs) for fact in answer_facts
]) / len(answer_facts)
```

**Interpretation**:
- **1.0**: Every fact is cited from retrieved documents
- **0.80-1.0**: Most facts grounded, some inference
- **< 0.80**: Contains unsupported claims - hallucination risk

**Example**:
- Answer claims: ["Token expiration is 30 minutes", "Update to 1 hour", "Located in auth/middleware.py"]
- Retrieved docs support: [✓, ✓, ✗] (file location not in docs)
- Grounding: 2/3 = **0.67** (needs correction)

---

### 4. Completeness Score (Weight: 0.15)

**Measures**: Whether the answer fully addresses the error

**Calculation**:
```python
required_components = [
    'has_root_cause',      # Did we identify why it failed?
    'has_fix_steps',       # Did we provide actionable fix?
    'has_code_location',   # Do we know where to fix? (for CODE errors)
    'has_verification'     # How to verify the fix works?
]

completeness_score = sum([
    check_component(answer, component)
    for component in required_components
]) / len(required_components)
```

**Interpretation**:
- **1.0**: All required components present
- **0.75-1.0**: Most components covered
- **< 0.75**: Incomplete answer - missing critical info

**Example**:
- Answer has: Root cause ✓, Fix steps ✓, Code location ✗, Verification ✗
- Completeness: 2/4 = **0.50** (incomplete)

---

### 5. Classification Confidence (Weight: 0.15)

**Measures**: How confident the ReAct agent was in error classification

**Source**: Already provided by ReAct agent from Task 0-ARCH.10

**Interpretation**:
- **> 0.90**: Very confident classification
- **0.70-0.90**: Confident classification
- **< 0.70**: Uncertain classification - may affect solution quality

**Example**:
- ReAct classified as CODE_ERROR with confidence **0.85**

---

### Combined Confidence Calculation

**Default Weights** (tunable based on error category):

| Component | Weight | Rationale |
|-----------|--------|-----------|
| **Relevance** | 0.25 | Most important - bad retrieval → bad answer |
| **Grounding** | 0.25 | Critical for accuracy - must cite sources |
| **Consistency** | 0.20 | Important - conflicting docs reduce confidence |
| **Completeness** | 0.15 | Important - incomplete answer less useful |
| **Classification** | 0.15 | Baseline - affects all downstream quality |

**Example Calculation**:
```python
confidence = (
    0.25 * 0.88 +  # Relevance
    0.20 * 0.92 +  # Consistency
    0.25 * 0.67 +  # Grounding
    0.15 * 0.50 +  # Completeness
    0.15 * 0.85    # Classification
) = 0.76
```

**Result**: 0.76 → **Medium Confidence** → Trigger HITL

---

## Threshold Definitions

### Confidence Thresholds and Actions

| Threshold | Confidence Range | Action | Rationale |
|-----------|------------------|--------|-----------|
| **HIGH** | ≥ 0.85 | **Pass Through** ✓ | High quality - deliver immediately |
| **MEDIUM** | 0.65 - 0.85 | **HITL** ⚠️ | Uncertain - get human validation |
| **LOW** | 0.40 - 0.65 | **Self-Correction** ↻ | Fixable - retry with more context |
| **VERY LOW** | < 0.40 | **Web Search Fallback** 🌐 | Internal RAG failed - search external sources |

---

### Action Definitions

#### 1. HIGH Confidence (≥ 0.85): Pass Through ✓

**Criteria:**
- Relevance > 0.80
- Grounding > 0.85
- Consistency > 0.80
- Completeness > 0.75

**Action:**
```python
# Deliver answer immediately
return {
    'answer': generated_answer,
    'confidence': 0.87,
    'verification_status': 'PASS',
    'action_taken': 'none'
}
```

**Expected**: 60-70% of cases

---

#### 2. MEDIUM Confidence (0.65-0.85): HITL ⚠️

**Criteria:**
- Decent retrieval but some uncertainty
- Or conflicting information in retrieved docs
- Or incomplete answer

**Action:**
```python
# Queue for human review
hitl_queue.add({
    'failure_id': failure_id,
    'generated_answer': answer,
    'confidence': 0.76,
    'concerns': [
        'Grounding score low (0.67)',
        'Completeness missing: code_location, verification'
    ],
    'priority': calculate_priority(confidence, error_severity)
})

# Return provisional answer with warning
return {
    'answer': generated_answer,
    'confidence': 0.76,
    'verification_status': 'PENDING_REVIEW',
    'action_taken': 'queued_for_hitl',
    'review_url': f'/review/{failure_id}'
}
```

**Expected**: 20-30% of cases

**HITL Workflow**:
1. Queue failure in `hitl_queue` PostgreSQL table
2. Send notification (Teams/Slack/Email)
3. Human reviewer validates/corrects answer
4. Store corrections for learning
5. Update answer confidence based on feedback

---

#### 3. LOW Confidence (0.40-0.65): Self-Correction ↻

**Criteria:**
- Low relevance (< 0.70)
- Or low grounding (< 0.70)
- But retrievable information likely exists

**Action:**
```python
# Attempt self-correction
correction_result = self_correct_answer(
    original_query=error_message,
    retrieved_docs=docs,
    generated_answer=answer,
    low_scores={'grounding': 0.67, 'completeness': 0.50}
)

if correction_result['improved']:
    return {
        'answer': correction_result['corrected_answer'],
        'confidence': correction_result['new_confidence'],  # e.g., 0.82
        'verification_status': 'CORRECTED',
        'action_taken': 'self_correction',
        'correction_method': 'query_expansion'
    }
else:
    # Correction failed - escalate to HITL
    trigger_hitl(failure_id, reason='self_correction_failed')
```

**Self-Correction Strategies**:
1. **Query Expansion**: Generate alternative queries
2. **Re-ranking**: Re-score retrieved documents
3. **Additional Retrieval**: Fetch more documents (top-10 instead of top-3)
4. **Fact Checking**: Verify each fact against retrieved docs

**Expected**: 10-15% of cases

---

#### 4. VERY LOW Confidence (< 0.40): Web Search Fallback 🌐

**Criteria:**
- Very low relevance (< 0.50)
- Or empty/irrelevant retrieved documents
- Internal knowledge base doesn't have solution

**Action:**
```python
# Fall back to web search
web_results = search_web(
    query=f"{error_message} {error_category} solution",
    num_results=5
)

# Generate answer from web results
web_answer = generate_answer_from_web(
    error=error_message,
    web_results=web_results
)

# Re-verify web-based answer
web_confidence = calculate_confidence(web_answer, web_results)

if web_confidence >= 0.65:
    # Web search succeeded
    return {
        'answer': web_answer,
        'confidence': web_confidence,
        'verification_status': 'WEB_SEARCH_SUCCESS',
        'action_taken': 'web_search_fallback',
        'sources': [r['url'] for r in web_results]
    }
else:
    # Even web search failed - escalate to HITL
    trigger_hitl(failure_id, reason='web_search_failed', priority='high')
```

**Expected**: 5-10% of cases (mostly UNKNOWN errors or rare edge cases)

---

## Verification Workflow

### End-to-End CRAG Flow

```
┌────────────────────────────────────────────────────────────────┐
│                  ReAct Agent Analysis                          │
│  (Classification + RAG + Multi-Step Reasoning)                 │
└────────────────────────────────────────────────────────────────┘
                              ↓
                   ReAct Result Generated
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                  CRAG Verification Layer                       │
│                                                                │
│  Step 1: Calculate Multi-Dimensional Confidence               │
│    - Relevance Score (0.25 weight)                           │
│    - Consistency Score (0.20 weight)                          │
│    - Grounding Score (0.25 weight)                            │
│    - Completeness Score (0.15 weight)                         │
│    - Classification Confidence (0.15 weight)                  │
│                                                                │
│  Step 2: Determine Action Based on Confidence                 │
│                                                                │
│    ┌─────────────────────────────────────────────┐           │
│    │ Confidence ≥ 0.85? (HIGH)                   │           │
│    └─────────────────────────────────────────────┘           │
│            │ YES                      │ NO                    │
│            ↓                          ↓                       │
│    ┌─────────────┐          ┌─────────────────────┐          │
│    │ PASS THROUGH│          │ Confidence ≥ 0.65?  │          │
│    │      ✓      │          │     (MEDIUM)        │          │
│    └─────────────┘          └─────────────────────┘          │
│                                    │ YES        │ NO          │
│                                    ↓            ↓             │
│                            ┌──────────┐  ┌──────────────┐    │
│                            │   HITL   │  │ Confidence   │    │
│                            │    ⚠️     │  │   ≥ 0.40?    │    │
│                            └──────────┘  └──────────────┘    │
│                                                │ YES  │ NO    │
│                                                ↓      ↓       │
│                                        ┌──────────────────┐   │
│                                        │ SELF-CORRECTION  │   │
│                                        │        ↻         │   │
│                                        └──────────────────┘   │
│                                                    │           │
│                                                    ↓           │
│                                        ┌──────────────────┐   │
│                                        │  WEB SEARCH      │   │
│                                        │      🌐          │   │
│                                        └──────────────────┘   │
└────────────────────────────────────────────────────────────────┘
                              ↓
               Final Answer (with verification metadata)
```

---

### Detailed Verification Steps

#### Step 1: Calculate Scores

```python
def verify_answer(react_result, retrieved_docs):
    """
    Comprehensive answer verification
    """

    # Extract components
    answer = react_result['root_cause'] + "\n" + react_result['fix_recommendation']
    classification_conf = react_result['classification_confidence']

    # Calculate individual scores
    relevance = calculate_relevance_score(retrieved_docs)
    consistency = calculate_consistency_score(retrieved_docs, answer)
    grounding = calculate_grounding_score(answer, retrieved_docs)
    completeness = calculate_completeness_score(answer, react_result['error_category'])

    # Weighted average
    confidence = (
        0.25 * relevance +
        0.20 * consistency +
        0.25 * grounding +
        0.15 * completeness +
        0.15 * classification_conf
    )

    return {
        'confidence': confidence,
        'components': {
            'relevance': relevance,
            'consistency': consistency,
            'grounding': grounding,
            'completeness': completeness,
            'classification': classification_conf
        }
    }
```

#### Step 2: Route Based on Confidence

```python
def route_based_on_confidence(confidence, answer, failure_data):
    """
    Route answer to appropriate action
    """

    if confidence >= 0.85:
        # HIGH: Pass through
        return pass_through(answer, confidence)

    elif confidence >= 0.65:
        # MEDIUM: Queue for HITL
        return queue_for_hitl(answer, confidence, failure_data)

    elif confidence >= 0.40:
        # LOW: Attempt self-correction
        corrected = self_correct(answer, failure_data)
        if corrected['success'] and corrected['confidence'] >= 0.65:
            return corrected
        else:
            # Self-correction failed - escalate to HITL
            return queue_for_hitl(corrected['answer'], corrected['confidence'],
                                 failure_data, reason='correction_failed')

    else:
        # VERY LOW: Web search fallback
        web_result = web_search_fallback(failure_data)
        if web_result['confidence'] >= 0.65:
            return web_result
        else:
            # Web search also failed - high-priority HITL
            return queue_for_hitl(web_result['answer'], web_result['confidence'],
                                 failure_data, priority='high',
                                 reason='all_methods_failed')
```

---

## Integration with ReAct Agent

### Current ReAct Flow (Task 0-ARCH.10)

```python
# In ai_analysis_service.py
def analyze_failure_with_gemini(failure_data):
    # Try ReAct agent
    react_result = analyze_with_react_agent(failure_data)

    # Format with Gemini
    formatted_result = format_react_result_with_gemini(react_result)

    return formatted_result
```

### Enhanced Flow with CRAG (Task 0-ARCH.18)

```python
# In ai_analysis_service.py
def analyze_failure_with_gemini(failure_data):
    # Try ReAct agent
    react_result = analyze_with_react_agent(failure_data)

    # NEW: CRAG Verification Layer
    verified_result = verify_with_crag(react_result, failure_data)

    # Format with Gemini (if not already formatted by CRAG)
    if verified_result['status'] == 'PASS':
        formatted_result = format_react_result_with_gemini(verified_result['answer'])
    elif verified_result['status'] == 'HITL':
        # Return provisional answer + HITL metadata
        formatted_result = format_hitl_response(verified_result)
    elif verified_result['status'] == 'CORRECTED':
        # Return corrected answer
        formatted_result = format_react_result_with_gemini(verified_result['answer'])

    return formatted_result
```

---

## Implementation Architecture

### Component Structure

```
implementation/
├── verification/
│   ├── __init__.py
│   ├── crag_verifier.py          # Main CRAG verifier (Task 0-ARCH.14)
│   ├── confidence_scorer.py      # Multi-dimensional scoring
│   ├── self_correction.py        # Self-correction strategies (Task 0-ARCH.15)
│   ├── hitl_manager.py           # HITL queue management (Task 0-ARCH.16)
│   └── web_search_fallback.py   # Web search integration (Task 0-ARCH.17)
│
└── tests/
    └── test_crag_verifier.py     # Comprehensive tests (Task 0-ARCH.20)
```

### Class Structure

#### CRAGVerifier (Main Class)

```python
class CRAGVerifier:
    """
    Main CRAG verification class
    """

    def __init__(self):
        self.confidence_scorer = ConfidenceScorer()
        self.self_corrector = SelfCorrector()
        self.hitl_manager = HITLManager()
        self.web_searcher = WebSearchFallback()

    def verify(self, react_result, retrieved_docs, failure_data):
        """
        Main verification method

        Returns:
            {
                'status': 'PASS' | 'HITL' | 'CORRECTED' | 'WEB_SEARCH',
                'answer': verified_answer,
                'confidence': float,
                'verification_metadata': {...}
            }
        """
        # Calculate confidence
        scores = self.confidence_scorer.calculate_all_scores(
            react_result, retrieved_docs
        )

        confidence = scores['overall_confidence']

        # Route based on confidence
        if confidence >= 0.85:
            return self._pass_through(react_result, confidence, scores)

        elif confidence >= 0.65:
            return self._queue_hitl(react_result, confidence, scores, failure_data)

        elif confidence >= 0.40:
            return self._self_correct(react_result, confidence, scores, failure_data)

        else:
            return self._web_search(react_result, confidence, scores, failure_data)
```

---

## Evaluation Metrics

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Overall Accuracy** | > 95% | % of answers validated as correct (via HITL feedback) |
| **High Conf Pass Rate** | 60-70% | % of answers passing with conf ≥ 0.85 |
| **HITL Queue Size** | < 30% | % of answers requiring human review |
| **Self-Correction Success** | > 70% | % of low-conf answers improved to ≥ 0.65 |
| **Web Search Usage** | < 10% | % of answers requiring web fallback |
| **False Positive Rate** | < 5% | % of high-conf answers that were actually wrong |
| **False Negative Rate** | < 10% | % of low-conf answers that were actually correct |

### Tracking Metrics (Task 0-ARCH.19)

```python
class CRAGMetrics:
    """
    Track CRAG performance metrics
    """

    def track(self, verification_result, ground_truth=None):
        """
        Track metrics for each verification
        """
        # Confidence distribution
        confidence_distribution[bucket(confidence)] += 1

        # Action distribution
        action_counts[verification_result['status']] += 1

        # Self-correction effectiveness
        if verification_result['status'] == 'CORRECTED':
            correction_improvements.append(
                verification_result['new_confidence'] -
                verification_result['original_confidence']
            )

        # Accuracy (if ground truth available)
        if ground_truth:
            is_correct = evaluate_answer(
                verification_result['answer'],
                ground_truth
            )
            accuracy_by_confidence[bucket(confidence)].append(is_correct)
```

---

## Implementation Plan

### Task Breakdown

| Task | Component | Estimated Time | Dependencies |
|------|-----------|----------------|--------------|
| **0-ARCH.13** | Design (this doc) | 3 hours | None |
| **0-ARCH.14** | crag_verifier.py | 4 hours | 0-ARCH.13 |
| **0-ARCH.15** | Self-correction | 3 hours | 0-ARCH.14 |
| **0-ARCH.16** | HITL integration | 3 hours | 0-ARCH.14 |
| **0-ARCH.17** | Web search fallback | 2 hours | 0-ARCH.14 |
| **0-ARCH.18** | Integration with ai_analysis_service | 2 hours | 0-ARCH.15, 0-ARCH.16, 0-ARCH.17 |
| **0-ARCH.19** | Evaluation metrics | 2 hours | 0-ARCH.18 |
| **0-ARCH.20** | Testing | 2 hours | 0-ARCH.14 |

**Total Estimated Time**: 21 hours

---

### Phase 1: Core Verification (Tasks 0-ARCH.14)

**Deliverable**: Basic CRAG verifier with confidence scoring

**Features**:
- Multi-dimensional confidence calculation
- Pass-through for high confidence
- Basic threshold routing

---

### Phase 2: Corrective Actions (Tasks 0-ARCH.15, 0-ARCH.16, 0-ARCH.17)

**Deliverable**: Full corrective action suite

**Features**:
- Self-correction with query expansion
- HITL queue management and notifications
- Web search fallback

---

### Phase 3: Integration (Task 0-ARCH.18)

**Deliverable**: CRAG integrated into production AI service

**Features**:
- Transparent verification layer
- Backward compatible API
- Confidence metadata in responses

---

### Phase 4: Evaluation (Tasks 0-ARCH.19, 0-ARCH.20)

**Deliverable**: Metrics and validation

**Features**:
- Performance tracking
- Accuracy measurement
- Comprehensive test suite

---

## Conclusion

The CRAG verification layer will significantly improve the ReAct agent's reliability by:

1. **Quantifying Uncertainty**: Multi-dimensional confidence scores
2. **Preventing Errors**: Catching low-quality answers before delivery
3. **Enabling Correction**: Self-correction and HITL workflows
4. **Providing Transparency**: Confidence metadata for all answers

**Expected Impact**:
- Accuracy: 85-90% → **>95%**
- User Trust: Increased through confidence transparency
- Error Recovery: 70-80% of low-confidence answers improved
- Human Workload: Only 20-30% of cases need review (vs 100% manual analysis)

---

**Document Version**: 1.0
**Created**: 2025-11-02
**Task**: 0-ARCH.13
**Next**: 0-ARCH.14 (Implement crag_verifier.py)
