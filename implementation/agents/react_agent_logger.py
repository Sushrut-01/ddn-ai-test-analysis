"""
ReAct Agent Enhanced Logger with n8n-style execution tracking

Wraps the ReAct agent to add detailed logging at each node execution.
Captures input/output, timing, and state for workflow debugging.
"""

import time
import uuid
import logging
from typing import Dict, Any, Optional
from functools import wraps
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from workflow_execution_tracker import get_workflow_tracker

logger = logging.getLogger(__name__)

class ReActAgentLogger:
    """
    Enhanced logger for ReAct agent workflows

    Tracks execution at node level with:
    - Input/Output capture
    - Timing measurements
    - State snapshots
    - Error tracking
    """

    def __init__(self, agent):
        """
        Initialize logger wrapper

        Args:
            agent: ReActAgent instance to wrap
        """
        self.agent = agent
        self.tracker = get_workflow_tracker()
        self.current_execution_id = None
        self.sequence_counter = 0

    def execute_with_logging(
        self,
        build_id: str,
        error_log: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        job_name: Optional[str] = None,
        test_name: Optional[str] = None,
        trigger_type: str = "manual",
        triggered_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute workflow with complete logging

        Args:
            build_id: Build identifier
            error_log: Full error log
            error_message: Error message
            stack_trace: Stack trace (optional)
            job_name: Jenkins job name (optional)
            test_name: Test case name (optional)
            trigger_type: How workflow was triggered
            triggered_by: Who triggered it

        Returns:
            Analysis result with execution_id added
        """
        # Generate execution ID
        self.current_execution_id = f"exec_{build_id}_{uuid.uuid4().hex[:8]}"
        self.sequence_counter = 0

        # Prepare input data
        input_data = {
            'build_id': build_id,
            'error_log': error_log[:500] + "..." if len(error_log) > 500 else error_log,  # Truncate for storage
            'error_message': error_message,
            'stack_trace': stack_trace[:500] if stack_trace and len(stack_trace) > 500 else stack_trace,
            'job_name': job_name,
            'test_name': test_name
        }

        try:
            # Start execution tracking
            self.tracker.start_execution(
                execution_id=self.current_execution_id,
                workflow_name='react_agent',
                input_data=input_data,
                build_id=build_id,
                trigger_type=trigger_type,
                triggered_by=triggered_by
            )

            logger.info(f"🚀 Starting ReAct Agent Execution: {self.current_execution_id}")
            logger.info(f"   Build ID: {build_id}")
            logger.info(f"   Trigger: {trigger_type}")

            # Execute workflow with node-level tracking
            result = self._execute_workflow_with_tracking(
                build_id=build_id,
                error_log=error_log,
                error_message=error_message,
                stack_trace=stack_trace,
                job_name=job_name,
                test_name=test_name
            )

            # Complete execution tracking
            self.tracker.complete_execution(
                execution_id=self.current_execution_id,
                status='completed',
                output_data={
                    'root_cause': result.get('root_cause'),
                    'fix_recommendation': result.get('fix_recommendation'),
                    'error_category': result.get('error_category'),
                    'solution_confidence': result.get('solution_confidence'),
                    'iterations': result.get('iterations', 0)
                }
            )

            # Add execution ID to result
            result['execution_id'] = self.current_execution_id

            logger.info(f"✅ Execution completed: {self.current_execution_id}")
            return result

        except Exception as e:
            logger.error(f"❌ Execution failed: {str(e)}")

            # Mark execution as failed
            self.tracker.complete_execution(
                execution_id=self.current_execution_id,
                status='failed',
                error_message=str(e),
                error_node='workflow'
            )

            raise

    def _execute_workflow_with_tracking(
        self,
        build_id: str,
        error_log: str,
        error_message: str,
        stack_trace: Optional[str],
        job_name: Optional[str],
        test_name: Optional[str]
    ) -> Dict[str, Any]:
        """
        Execute workflow nodes with detailed tracking

        This wraps each node execution to capture:
        - Node input
        - Node output
        - Execution time
        - State before/after
        """
        # Initialize state
        state = {
            'build_id': build_id,
            'error_log': error_log,
            'error_message': error_message,
            'stack_trace': stack_trace,
            'job_name': job_name,
            'test_name': test_name,
            'iteration': 0,
            'reasoning_history': [],
            'actions_taken': [],
            'observations': []
        }

        # Node 1: Classify Error
        state = self._execute_node(
            node_name='classify',
            node_type='classify',
            state=state,
            execution_func=lambda s: self.agent._classify_error(s)
        )

        # Iterative reasoning loop (max 5 iterations)
        max_iterations = state.get('max_iterations', 5)

        for iteration in range(max_iterations):
            state['iteration'] = iteration

            # Node 2: Reasoning
            state = self._execute_node(
                node_name=f'reasoning_iter{iteration}',
                node_type='reasoning',
                state=state,
                execution_func=lambda s: self.agent._reasoning_node(s),
                iteration=iteration
            )

            # Check if we should continue
            if not state.get('should_continue', True):
                logger.info(f"   Reasoning complete after {iteration + 1} iterations")
                break

            # Node 3: Select Tool
            state = self._execute_node(
                node_name=f'select_tool_iter{iteration}',
                node_type='select_tool',
                state=state,
                execution_func=lambda s: self.agent._select_tool_node(s),
                iteration=iteration
            )

            # Node 4: Execute Tool
            state = self._execute_node(
                node_name=f'execute_tool_iter{iteration}',
                node_type='execute_tool',
                state=state,
                execution_func=lambda s: self.agent._execute_tool_node(s),
                iteration=iteration
            )

            # Node 5: Observe Results
            state = self._execute_node(
                node_name=f'observe_iter{iteration}',
                node_type='observe',
                state=state,
                execution_func=lambda s: self.agent._observe_node(s),
                iteration=iteration
            )

        # Node 6: Generate Answer
        state = self._execute_node(
            node_name='answer',
            node_type='answer',
            state=state,
            execution_func=lambda s: self.agent._answer_node(s)
        )

        # Node 7: Verify with CRAG
        state = self._execute_node(
            node_name='verify',
            node_type='verify',
            state=state,
            execution_func=lambda s: self.agent._verify_node(s)
        )

        # Return final result
        return {
            'root_cause': state.get('root_cause'),
            'fix_recommendation': state.get('fix_recommendation'),
            'error_category': state.get('error_category'),
            'solution_confidence': state.get('solution_confidence'),
            'similar_cases': state.get('similar_cases', []),
            'iterations': state.get('iteration', 0) + 1,
            'reasoning_history': state.get('reasoning_history', []),
            'crag_confidence': state.get('crag_confidence', 0.0),
            'crag_action': state.get('crag_action')
        }

    def _execute_node(
        self,
        node_name: str,
        node_type: str,
        state: Dict,
        execution_func: callable,
        iteration: int = 0
    ) -> Dict:
        """
        Execute a single node with tracking

        Args:
            node_name: Name of the node
            node_type: Type of node
            state: Current state
            execution_func: Function to execute the node
            iteration: Iteration number

        Returns:
            Updated state
        """
        self.sequence_counter += 1

        # Prepare input data (exclude large fields)
        input_data = self._prepare_node_input(state, node_type)

        # Prepare state snapshot (before execution)
        state_before = self._create_state_snapshot(state)

        # Log node start
        logger.info(f"   [{self.sequence_counter}] 📍 {node_name} - Starting...")

        start_time = time.time()

        try:
            # Track node start
            self.tracker.log_node_start(
                execution_id=self.current_execution_id,
                node_name=node_name,
                node_type=node_type,
                input_data=input_data,
                state_before=state_before,
                sequence_number=self.sequence_counter,
                iteration=iteration
            )

            # Execute node
            updated_state = execution_func(state)

            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Prepare output data
            output_data = self._prepare_node_output(updated_state, node_type)

            # Prepare state snapshot (after execution)
            state_after = self._create_state_snapshot(updated_state)

            # Log node completion
            self.tracker.log_node_complete(
                execution_id=self.current_execution_id,
                node_name=node_name,
                sequence_number=self.sequence_counter,
                output_data=output_data,
                state_after=state_after,
                duration_ms=duration_ms
            )

            logger.info(f"   [{self.sequence_counter}] ✅ {node_name} - Completed ({duration_ms}ms)")

            return updated_state

        except Exception as e:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Log node error
            self.tracker.log_node_error(
                execution_id=self.current_execution_id,
                node_name=node_name,
                sequence_number=self.sequence_counter,
                error_message=str(e),
                duration_ms=duration_ms,
                state_after=state  # Use original state
            )

            logger.error(f"   [{self.sequence_counter}] ❌ {node_name} - Failed: {str(e)}")
            raise

    def _prepare_node_input(self, state: Dict, node_type: str) -> Dict:
        """Prepare node input data for storage (extract relevant fields)"""
        if node_type == 'classify':
            return {
                'error_message': state.get('error_message', '')[:200],
                'error_log': state.get('error_log', '')[:200]
            }
        elif node_type == 'reasoning':
            return {
                'error_category': state.get('error_category'),
                'iteration': state.get('iteration', 0),
                'needs_more_info': state.get('needs_more_info', True)
            }
        elif node_type == 'select_tool':
            return {
                'current_thought': state.get('current_thought', ''),
                'error_category': state.get('error_category')
            }
        elif node_type == 'execute_tool':
            return {
                'next_action': state.get('next_action'),
                'error_category': state.get('error_category')
            }
        elif node_type == 'observe':
            return {
                'tool_results': list(state.get('tool_results', {}).keys())
            }
        elif node_type == 'answer':
            return {
                'iterations': state.get('iteration', 0),
                'actions_taken_count': len(state.get('actions_taken', []))
            }
        elif node_type == 'verify':
            return {
                'root_cause': state.get('root_cause', '')[:200],
                'solution_confidence': state.get('solution_confidence', 0.0)
            }
        else:
            return {}

    def _prepare_node_output(self, state: Dict, node_type: str) -> Dict:
        """Prepare node output data for storage"""
        if node_type == 'classify':
            return {
                'error_category': state.get('error_category'),
                'classification_confidence': state.get('classification_confidence', 0.0)
            }
        elif node_type == 'reasoning':
            return {
                'current_thought': state.get('current_thought', ''),
                'should_continue': state.get('should_continue', True)
            }
        elif node_type == 'select_tool':
            return {
                'next_action': state.get('next_action')
            }
        elif node_type == 'execute_tool':
            return {
                'tool_result_keys': list(state.get('tool_results', {}).keys()),
                'execution_success': True
            }
        elif node_type == 'observe':
            return {
                'observation_added': len(state.get('observations', [])) > 0
            }
        elif node_type == 'answer':
            return {
                'root_cause': state.get('root_cause', '')[:200],
                'solution_confidence': state.get('solution_confidence', 0.0)
            }
        elif node_type == 'verify':
            return {
                'crag_confidence': state.get('crag_confidence', 0.0),
                'crag_action': state.get('crag_action')
            }
        else:
            return {}

    def _create_state_snapshot(self, state: Dict) -> Dict:
        """Create a lightweight snapshot of state for storage"""
        return {
            'error_category': state.get('error_category'),
            'iteration': state.get('iteration', 0),
            'solution_confidence': state.get('solution_confidence', 0.0),
            'needs_more_info': state.get('needs_more_info', True),
            'actions_taken_count': len(state.get('actions_taken', [])),
            'observations_count': len(state.get('observations', [])),
            'reasoning_history_count': len(state.get('reasoning_history', []))
        }


def create_logged_agent(agent):
    """
    Create a ReActAgent wrapper with enhanced logging

    Args:
        agent: ReActAgent instance

    Returns:
        ReActAgentLogger instance
    """
    return ReActAgentLogger(agent)
