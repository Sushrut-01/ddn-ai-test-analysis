"""
RAGAS Evaluation Framework for DDN AI System
Evaluates RAG system quality using RAGAS metrics
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Try to import RAGAS (may not be installed yet)
try:
    from ragas import evaluate
    from ragas.metrics import (
        context_precision,
        context_recall,
        faithfulness,
        answer_relevancy,
        answer_similarity,
        answer_correctness
    )
    from datasets import Dataset
    RAGAS_AVAILABLE = True
except ImportError as e:
    RAGAS_AVAILABLE = False
    logging.warning(f"RAGAS not available: {e}")
    logging.warning("Install with: pip install ragas datasets langchain-openai")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Single test case evaluation result"""
    test_id: str
    category: str
    query: str

    # RAGAS metrics
    context_precision: float
    context_recall: float
    faithfulness: float
    answer_relevancy: float
    answer_similarity: float
    answer_correctness: float

    # Overall score
    overall_score: float

    # Metadata
    passed: bool
    execution_time_ms: float
    timestamp: str

    # Response data
    generated_answer: str
    retrieved_contexts: List[str]
    ground_truth_answer: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class EvaluationSummary:
    """Overall evaluation summary"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float

    # Average RAGAS scores
    avg_context_precision: float
    avg_context_recall: float
    avg_faithfulness: float
    avg_answer_relevancy: float
    avg_answer_similarity: float
    avg_answer_correctness: float
    avg_overall_score: float

    # Per-category breakdown
    category_scores: Dict[str, Dict[str, float]]

    # Metadata
    evaluation_date: str
    total_execution_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class RAGASEvaluator:
    """
    RAGAS-based evaluator for RAG system

    Evaluates:
    1. Context Precision: How relevant are retrieved contexts?
    2. Context Recall: Are all relevant contexts retrieved?
    3. Faithfulness: Is answer grounded in retrieved context?
    4. Answer Relevancy: How relevant is answer to query?
    5. Answer Similarity: How similar is answer to ground truth?
    6. Answer Correctness: Overall correctness combining similarity and faithfulness
    """

    def __init__(self, test_set_path: str = None):
        """
        Initialize evaluator

        Args:
            test_set_path: Path to test_set.json file
        """
        self.test_set_path = test_set_path or os.path.join(
            os.path.dirname(__file__),
            'test_set.json'
        )
        self.test_cases = []
        self.results = []

        # Load test set
        self._load_test_set()

        logger.info(f"✓ RAGASEvaluator initialized")
        logger.info(f"  - Test set: {self.test_set_path}")
        logger.info(f"  - Test cases: {len(self.test_cases)}")
        logger.info(f"  - RAGAS available: {RAGAS_AVAILABLE}")

    def _load_test_set(self):
        """Load test set from JSON file"""
        try:
            with open(self.test_set_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.test_cases = data.get('test_cases', [])
                logger.info(f"✓ Loaded {len(self.test_cases)} test cases")
        except Exception as e:
            logger.error(f"✗ Failed to load test set: {e}")
            raise

    def evaluate_single(
        self,
        test_case: Dict[str, Any],
        generated_answer: str,
        retrieved_contexts: List[str],
        execution_time_ms: float = 0
    ) -> EvaluationResult:
        """
        Evaluate a single test case using RAGAS metrics

        Args:
            test_case: Test case from test_set.json
            generated_answer: AI-generated answer
            retrieved_contexts: List of retrieved context strings
            execution_time_ms: Time taken to generate answer

        Returns:
            EvaluationResult with all metrics
        """
        if not RAGAS_AVAILABLE:
            logger.error("RAGAS not available - cannot evaluate")
            return self._create_mock_result(test_case, generated_answer, retrieved_contexts, execution_time_ms)

        try:
            # Extract ground truth
            ground_truth = test_case['ground_truth']
            ground_truth_answer = self._format_ground_truth_answer(ground_truth)

            # Prepare data for RAGAS
            dataset_dict = {
                'question': [test_case['query']],
                'answer': [generated_answer],
                'contexts': [retrieved_contexts],
                'ground_truth': [ground_truth_answer]
            }

            dataset = Dataset.from_dict(dataset_dict)

            # Run RAGAS evaluation
            logger.info(f"Evaluating test case: {test_case['id']}")
            ragas_result = evaluate(
                dataset,
                metrics=[
                    context_precision,
                    context_recall,
                    faithfulness,
                    answer_relevancy,
                    answer_similarity,
                    answer_correctness
                ]
            )

            # Extract scores
            scores = ragas_result.to_pandas().iloc[0]
            context_prec = float(scores.get('context_precision', 0))
            context_rec = float(scores.get('context_recall', 0))
            faith = float(scores.get('faithfulness', 0))
            relevancy = float(scores.get('answer_relevancy', 0))
            similarity = float(scores.get('answer_similarity', 0))
            correctness = float(scores.get('answer_correctness', 0))

            # Calculate overall score (weighted average)
            overall_score = (
                context_prec * 0.15 +
                context_rec * 0.15 +
                faith * 0.25 +
                relevancy * 0.20 +
                similarity * 0.15 +
                correctness * 0.10
            )

            # Determine pass/fail (threshold: 0.80)
            passed = overall_score >= 0.80

            result = EvaluationResult(
                test_id=test_case['id'],
                category=test_case['category'],
                query=test_case['query'],
                context_precision=context_prec,
                context_recall=context_rec,
                faithfulness=faith,
                answer_relevancy=relevancy,
                answer_similarity=similarity,
                answer_correctness=correctness,
                overall_score=overall_score,
                passed=passed,
                execution_time_ms=execution_time_ms,
                timestamp=datetime.now().isoformat(),
                generated_answer=generated_answer,
                retrieved_contexts=retrieved_contexts,
                ground_truth_answer=ground_truth_answer
            )

            logger.info(f"✓ Test {test_case['id']}: Overall={overall_score:.3f} Passed={passed}")
            return result

        except Exception as e:
            logger.error(f"✗ Evaluation failed for {test_case['id']}: {e}")
            return self._create_mock_result(test_case, generated_answer, retrieved_contexts, execution_time_ms, error=str(e))

    def _format_ground_truth_answer(self, ground_truth: Dict[str, Any]) -> str:
        """Format ground truth as text answer"""
        parts = []

        if 'root_cause' in ground_truth:
            parts.append(f"Root Cause: {ground_truth['root_cause']}")

        if 'recommendation' in ground_truth:
            parts.append(f"Recommendation: {ground_truth['recommendation']}")

        if 'severity' in ground_truth:
            parts.append(f"Severity: {ground_truth['severity']}")

        if 'category' in ground_truth:
            parts.append(f"Category: {ground_truth['category']}")

        return '\n'.join(parts)

    def _create_mock_result(
        self,
        test_case: Dict[str, Any],
        generated_answer: str,
        retrieved_contexts: List[str],
        execution_time_ms: float,
        error: str = None
    ) -> EvaluationResult:
        """Create mock result when RAGAS not available"""
        ground_truth = test_case['ground_truth']
        ground_truth_answer = self._format_ground_truth_answer(ground_truth)

        # Simple heuristic scoring when RAGAS not available
        overall_score = 0.50  # Default to 50%

        return EvaluationResult(
            test_id=test_case['id'],
            category=test_case['category'],
            query=test_case['query'],
            context_precision=0.5,
            context_recall=0.5,
            faithfulness=0.5,
            answer_relevancy=0.5,
            answer_similarity=0.5,
            answer_correctness=0.5,
            overall_score=overall_score,
            passed=False,
            execution_time_ms=execution_time_ms,
            timestamp=datetime.now().isoformat(),
            generated_answer=generated_answer or "EVALUATION_ERROR: " + (error or "RAGAS not available"),
            retrieved_contexts=retrieved_contexts,
            ground_truth_answer=ground_truth_answer
        )

    def evaluate_batch(
        self,
        test_responses: List[Dict[str, Any]],
        limit: int = None
    ) -> EvaluationSummary:
        """
        Evaluate a batch of test responses

        Args:
            test_responses: List of dicts with keys:
                - test_id: Test case ID
                - generated_answer: AI-generated answer
                - retrieved_contexts: List of context strings
                - execution_time_ms: Time taken
            limit: Maximum number of tests to evaluate (None = all)

        Returns:
            EvaluationSummary with aggregated results
        """
        start_time = datetime.now()
        self.results = []

        # Limit test cases if specified
        test_cases_to_evaluate = self.test_cases[:limit] if limit else self.test_cases

        logger.info(f"Starting batch evaluation of {len(test_cases_to_evaluate)} test cases")

        for test_case in test_cases_to_evaluate:
            test_id = test_case['id']

            # Find corresponding response
            response = next(
                (r for r in test_responses if r['test_id'] == test_id),
                None
            )

            if not response:
                logger.warning(f"No response found for test {test_id} - skipping")
                continue

            # Evaluate single test case
            result = self.evaluate_single(
                test_case=test_case,
                generated_answer=response['generated_answer'],
                retrieved_contexts=response.get('retrieved_contexts', []),
                execution_time_ms=response.get('execution_time_ms', 0)
            )

            self.results.append(result)

        # Calculate summary
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000

        summary = self._calculate_summary(total_time)

        logger.info(f"✓ Batch evaluation complete")
        logger.info(f"  - Total tests: {summary.total_tests}")
        logger.info(f"  - Passed: {summary.passed_tests}")
        logger.info(f"  - Failed: {summary.failed_tests}")
        logger.info(f"  - Pass rate: {summary.pass_rate:.1%}")
        logger.info(f"  - Avg overall score: {summary.avg_overall_score:.3f}")

        return summary

    def _calculate_summary(self, total_execution_time_ms: float) -> EvaluationSummary:
        """Calculate evaluation summary from results"""
        if not self.results:
            return EvaluationSummary(
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                pass_rate=0.0,
                avg_context_precision=0.0,
                avg_context_recall=0.0,
                avg_faithfulness=0.0,
                avg_answer_relevancy=0.0,
                avg_answer_similarity=0.0,
                avg_answer_correctness=0.0,
                avg_overall_score=0.0,
                category_scores={},
                evaluation_date=datetime.now().isoformat(),
                total_execution_time_ms=total_execution_time_ms
            )

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        pass_rate = passed_tests / total_tests if total_tests > 0 else 0.0

        # Calculate averages
        avg_context_precision = sum(r.context_precision for r in self.results) / total_tests
        avg_context_recall = sum(r.context_recall for r in self.results) / total_tests
        avg_faithfulness = sum(r.faithfulness for r in self.results) / total_tests
        avg_answer_relevancy = sum(r.answer_relevancy for r in self.results) / total_tests
        avg_answer_similarity = sum(r.answer_similarity for r in self.results) / total_tests
        avg_answer_correctness = sum(r.answer_correctness for r in self.results) / total_tests
        avg_overall_score = sum(r.overall_score for r in self.results) / total_tests

        # Per-category breakdown
        category_scores = {}
        for category in set(r.category for r in self.results):
            category_results = [r for r in self.results if r.category == category]
            category_scores[category] = {
                'count': len(category_results),
                'passed': sum(1 for r in category_results if r.passed),
                'pass_rate': sum(1 for r in category_results if r.passed) / len(category_results),
                'avg_overall_score': sum(r.overall_score for r in category_results) / len(category_results),
                'avg_context_precision': sum(r.context_precision for r in category_results) / len(category_results),
                'avg_faithfulness': sum(r.faithfulness for r in category_results) / len(category_results),
                'avg_answer_relevancy': sum(r.answer_relevancy for r in category_results) / len(category_results)
            }

        return EvaluationSummary(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            pass_rate=pass_rate,
            avg_context_precision=avg_context_precision,
            avg_context_recall=avg_context_recall,
            avg_faithfulness=avg_faithfulness,
            avg_answer_relevancy=avg_answer_relevancy,
            avg_answer_similarity=avg_answer_similarity,
            avg_answer_correctness=avg_answer_correctness,
            avg_overall_score=avg_overall_score,
            category_scores=category_scores,
            evaluation_date=datetime.now().isoformat(),
            total_execution_time_ms=total_execution_time_ms
        )

    def save_results(self, output_dir: str = None):
        """Save evaluation results to JSON files"""
        if not self.results:
            logger.warning("No results to save")
            return

        output_dir = output_dir or os.path.join(
            os.path.dirname(__file__),
            'results'
        )

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save detailed results
        results_file = os.path.join(output_dir, f'ragas_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in self.results], f, indent=2)

        logger.info(f"✓ Results saved to {results_file}")

        # Save summary
        summary = self._calculate_summary(0)
        summary_file = os.path.join(output_dir, f'ragas_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary.to_dict(), f, indent=2)

        logger.info(f"✓ Summary saved to {summary_file}")

        return results_file, summary_file


def main():
    """Test harness"""
    print("=" * 80)
    print("RAGAS Evaluation Framework - Test Harness")
    print("=" * 80)

    # Check RAGAS availability
    if not RAGAS_AVAILABLE:
        print("\n⚠️  RAGAS not installed!")
        print("Install with:")
        print("  pip install ragas datasets langchain-openai")
        print("\nRunning with mock evaluation...")

    # Initialize evaluator
    evaluator = RAGASEvaluator()

    # Create mock responses for first 5 test cases
    mock_responses = []
    for i, test_case in enumerate(evaluator.test_cases[:5]):
        mock_responses.append({
            'test_id': test_case['id'],
            'generated_answer': f"Mock answer for {test_case['id']}: {test_case['ground_truth']['root_cause']}",
            'retrieved_contexts': [
                f"Context 1 for {test_case['id']}",
                f"Context 2 for {test_case['id']}"
            ],
            'execution_time_ms': 1500
        })

    # Run evaluation
    print(f"\n📊 Evaluating {len(mock_responses)} test cases...")
    summary = evaluator.evaluate_batch(mock_responses, limit=5)

    # Display summary
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {summary.total_tests}")
    print(f"Passed: {summary.passed_tests}")
    print(f"Failed: {summary.failed_tests}")
    print(f"Pass Rate: {summary.pass_rate:.1%}")
    print(f"\nAverage Scores:")
    print(f"  Context Precision: {summary.avg_context_precision:.3f}")
    print(f"  Context Recall: {summary.avg_context_recall:.3f}")
    print(f"  Faithfulness: {summary.avg_faithfulness:.3f}")
    print(f"  Answer Relevancy: {summary.avg_answer_relevancy:.3f}")
    print(f"  Answer Similarity: {summary.avg_answer_similarity:.3f}")
    print(f"  Answer Correctness: {summary.avg_answer_correctness:.3f}")
    print(f"  Overall Score: {summary.avg_overall_score:.3f}")

    print(f"\nCategory Breakdown:")
    for category, scores in summary.category_scores.items():
        print(f"  {category}: {scores['count']} tests, {scores['pass_rate']:.1%} pass rate, {scores['avg_overall_score']:.3f} avg score")

    # Save results
    print(f"\n💾 Saving results...")
    evaluator.save_results()

    print("\n✅ Test harness complete!")


if __name__ == '__main__':
    main()
