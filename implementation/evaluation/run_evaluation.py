"""
Run Evaluation Script for DDN AI System
Executes test cases against live AI system and evaluates with RAGAS
"""

import json
import os
import sys
import time
import logging
import argparse
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import evaluation framework
from ragas_evaluation import RAGASEvaluator, RAGAS_AVAILABLE

# Import AI analysis service components
try:
    from ai_analysis_service import analyze_with_react_agent, format_react_result_with_gemini
    AI_SERVICE_AVAILABLE = True
except ImportError as e:
    AI_SERVICE_AVAILABLE = False
    logging.warning(f"AI service not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EvaluationRunner:
    """
    Runs evaluation against live AI system

    Process:
    1. Load test cases from test_set.json
    2. For each test case, call AI system
    3. Collect responses and contexts
    4. Evaluate with RAGAS
    5. Generate comprehensive report
    """

    def __init__(self, test_set_path: str = None):
        """
        Initialize evaluation runner

        Args:
            test_set_path: Path to test_set.json
        """
        self.test_set_path = test_set_path or os.path.join(
            os.path.dirname(__file__),
            'test_set.json'
        )

        # Initialize evaluator
        self.evaluator = RAGASEvaluator(self.test_set_path)
        self.test_responses = []

        logger.info(f"✓ EvaluationRunner initialized")
        logger.info(f"  - AI Service available: {AI_SERVICE_AVAILABLE}")
        logger.info(f"  - RAGAS available: {RAGAS_AVAILABLE}")

    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run single test case against AI system

        Args:
            test_case: Test case from test_set.json

        Returns:
            Dict with test_id, generated_answer, retrieved_contexts, execution_time_ms
        """
        test_id = test_case['id']
        query = test_case['query']
        error_message = test_case.get('error_message', query)
        stack_trace = test_case.get('stack_trace', '')

        logger.info(f"Running test {test_id}: {query[:80]}...")

        if not AI_SERVICE_AVAILABLE:
            # Mock response if AI service not available
            return {
                'test_id': test_id,
                'generated_answer': f"MOCK: AI service not available. Root cause: {test_case['ground_truth'].get('root_cause', 'Unknown')}",
                'retrieved_contexts': [
                    f"Mock context 1 for {test_id}",
                    f"Mock context 2 for {test_id}"
                ],
                'execution_time_ms': 100
            }

        start_time = time.time()

        try:
            # Prepare failure data (mimicking Robot Framework format)
            failure_data = {
                'suite_name': 'Evaluation Test Suite',
                'test_name': f'Test_{test_id}',
                'error_message': error_message,
                'error_type': test_case.get('category', 'UNKNOWN_ERROR'),
                'stack_trace': stack_trace,
                'build_number': 'EVAL_001',
                'timestamp': datetime.now().isoformat()
            }

            # Call ReAct agent for analysis
            react_result = analyze_with_react_agent(failure_data)

            # Format with Gemini
            final_result = format_react_result_with_gemini(react_result, failure_data)

            # Extract answer and contexts
            generated_answer = self._extract_answer(final_result)
            retrieved_contexts = self._extract_contexts(react_result)

            execution_time_ms = (time.time() - start_time) * 1000

            return {
                'test_id': test_id,
                'generated_answer': generated_answer,
                'retrieved_contexts': retrieved_contexts,
                'execution_time_ms': execution_time_ms
            }

        except Exception as e:
            logger.error(f"✗ Test {test_id} failed: {e}")
            execution_time_ms = (time.time() - start_time) * 1000

            return {
                'test_id': test_id,
                'generated_answer': f"ERROR: {str(e)}",
                'retrieved_contexts': [],
                'execution_time_ms': execution_time_ms
            }

    def _extract_answer(self, final_result: Dict[str, Any]) -> str:
        """Extract answer text from AI result"""
        # Try different possible keys
        if 'analysis' in final_result:
            analysis = final_result['analysis']
            parts = []

            if isinstance(analysis, dict):
                if 'root_cause' in analysis:
                    parts.append(f"Root Cause: {analysis['root_cause']}")
                if 'recommendation' in analysis:
                    parts.append(f"Recommendation: {analysis['recommendation']}")
                if 'classification' in analysis:
                    parts.append(f"Classification: {analysis['classification']}")
                if 'severity' in analysis:
                    parts.append(f"Severity: {analysis['severity']}")
            else:
                parts.append(str(analysis))

            return '\n'.join(parts) if parts else str(analysis)

        elif 'answer' in final_result:
            return str(final_result['answer'])

        else:
            return json.dumps(final_result, indent=2)

    def _extract_contexts(self, react_result: Dict[str, Any]) -> List[str]:
        """Extract retrieved contexts from ReAct result"""
        contexts = []

        # Extract from RAG tool results
        if 'observations' in react_result:
            for obs in react_result['observations']:
                if isinstance(obs, dict) and 'content' in obs:
                    contexts.append(obs['content'])
                elif isinstance(obs, str):
                    contexts.append(obs)

        # Extract from retrieved documents
        if 'retrieved_docs' in react_result:
            for doc in react_result['retrieved_docs']:
                if isinstance(doc, dict):
                    if 'content' in doc:
                        contexts.append(doc['content'])
                    elif 'text' in doc:
                        contexts.append(doc['text'])
                else:
                    contexts.append(str(doc))

        # Fallback: extract from state
        if not contexts and 'state' in react_result:
            state = react_result['state']
            if 'rag_results' in state:
                for result in state['rag_results']:
                    if isinstance(result, dict) and 'content' in result:
                        contexts.append(result['content'])

        return contexts[:10]  # Limit to top 10 contexts

    def run_evaluation(
        self,
        limit: int = None,
        categories: List[str] = None,
        parallel: bool = False
    ) -> Dict[str, Any]:
        """
        Run full evaluation on test set

        Args:
            limit: Maximum number of tests to run (None = all)
            categories: List of categories to test (None = all)
            parallel: Run tests in parallel (not implemented yet)

        Returns:
            Dict with summary and results
        """
        logger.info("=" * 80)
        logger.info("STARTING EVALUATION RUN")
        logger.info("=" * 80)

        # Filter test cases
        test_cases = self.evaluator.test_cases

        if categories:
            test_cases = [tc for tc in test_cases if tc['category'] in categories]
            logger.info(f"Filtering to categories: {categories}")

        if limit:
            test_cases = test_cases[:limit]

        logger.info(f"Running {len(test_cases)} test cases")

        # Run tests
        self.test_responses = []
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n[{i}/{len(test_cases)}] Testing {test_case['id']}...")

            response = self.run_single_test(test_case)
            self.test_responses.append(response)

            # Progress update
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{len(test_cases)} tests completed")

        # Run RAGAS evaluation
        logger.info("\n" + "=" * 80)
        logger.info("RUNNING RAGAS EVALUATION")
        logger.info("=" * 80)

        summary = self.evaluator.evaluate_batch(self.test_responses)

        # Save results
        logger.info("\n" + "=" * 80)
        logger.info("SAVING RESULTS")
        logger.info("=" * 80)

        results_file, summary_file = self.evaluator.save_results()

        # Prepare return data
        return {
            'summary': summary.to_dict(),
            'results_file': results_file,
            'summary_file': summary_file,
            'test_responses': self.test_responses
        }

    def print_summary_report(self, evaluation_result: Dict[str, Any]):
        """Print human-readable summary report"""
        summary = evaluation_result['summary']

        print("\n" + "=" * 80)
        print("EVALUATION SUMMARY REPORT")
        print("=" * 80)

        print(f"\n📊 Overall Results:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Passed: {summary['passed_tests']} ✅")
        print(f"  Failed: {summary['failed_tests']} ❌")
        print(f"  Pass Rate: {summary['pass_rate']:.1%}")

        print(f"\n📈 RAGAS Metrics:")
        print(f"  Context Precision: {summary['avg_context_precision']:.3f}")
        print(f"  Context Recall: {summary['avg_context_recall']:.3f}")
        print(f"  Faithfulness: {summary['avg_faithfulness']:.3f}")
        print(f"  Answer Relevancy: {summary['avg_answer_relevancy']:.3f}")
        print(f"  Answer Similarity: {summary['avg_answer_similarity']:.3f}")
        print(f"  Answer Correctness: {summary['avg_answer_correctness']:.3f}")
        print(f"  Overall Score: {summary['avg_overall_score']:.3f}")

        # Success criteria check
        print(f"\n✅ Success Criteria:")
        target_score = 0.90
        if summary['avg_overall_score'] >= target_score:
            print(f"  ✅ PASSED: Overall score {summary['avg_overall_score']:.3f} >= {target_score}")
        else:
            print(f"  ❌ FAILED: Overall score {summary['avg_overall_score']:.3f} < {target_score}")

        print(f"\n📁 Category Breakdown:")
        for category, scores in summary['category_scores'].items():
            print(f"  {category}:")
            print(f"    Tests: {scores['count']}")
            print(f"    Pass Rate: {scores['pass_rate']:.1%}")
            print(f"    Avg Score: {scores['avg_overall_score']:.3f}")

        print(f"\n💾 Results saved to:")
        print(f"  {evaluation_result['results_file']}")
        print(f"  {evaluation_result['summary_file']}")

        print("\n" + "=" * 80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run RAGAS evaluation on DDN AI system')
    parser.add_argument('--limit', type=int, help='Maximum number of tests to run')
    parser.add_argument('--categories', nargs='+', help='Categories to test (e.g., CODE_ERROR INFRA_ERROR)')
    parser.add_argument('--test-set', help='Path to test_set.json')
    parser.add_argument('--mock', action='store_true', help='Run with mock responses (no AI service)')

    args = parser.parse_args()

    # Initialize runner
    runner = EvaluationRunner(test_set_path=args.test_set)

    # Check prerequisites
    if not RAGAS_AVAILABLE:
        print("\n⚠️  WARNING: RAGAS not installed!")
        print("Install with: pip install ragas datasets langchain-openai")
        print("Continuing with mock evaluation...")

    if not AI_SERVICE_AVAILABLE and not args.mock:
        print("\n⚠️  WARNING: AI service not available!")
        print("Running with mock responses...")

    # Run evaluation
    try:
        evaluation_result = runner.run_evaluation(
            limit=args.limit,
            categories=args.categories
        )

        # Print summary
        runner.print_summary_report(evaluation_result)

        # Exit code based on success
        summary = evaluation_result['summary']
        if summary['avg_overall_score'] >= 0.90:
            print("\n✅ EVALUATION PASSED!")
            sys.exit(0)
        else:
            print("\n❌ EVALUATION FAILED - Score below 0.90 threshold")
            sys.exit(1)

    except Exception as e:
        logger.error(f"✗ Evaluation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
