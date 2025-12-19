"""
Workflow Execution Tracker - n8n-style debugging for LangGraph workflows
Creates detailed execution logs with node-level input/output tracking

Similar to n8n's execution visualization:
- Stores every workflow execution
- Captures input/output for each node
- Tracks execution time per node
- Stores error details
- Enables execution replay and debugging
"""

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from datetime import datetime
import json
import os
from typing import Dict, List, Optional, Any
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class WorkflowExecutionTracker:
    """
    Tracks LangGraph workflow executions with node-level detail

    Similar to n8n's execution storage:
    - Execution metadata (ID, start time, end time, status)
    - Node execution data (input, output, duration, error)
    - Execution flow (sequence of nodes executed)
    """

    def __init__(self):
        """Initialize tracker with PostgreSQL connection"""
        self.postgres_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', 5432),
            'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'password')
        }

        # Initialize database schema
        self._initialize_schema()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = psycopg2.connect(**self.postgres_config)
        try:
            yield conn
        finally:
            conn.close()

    def _initialize_schema(self):
        """Create execution tracking tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Workflow executions table (main execution record)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    id SERIAL PRIMARY KEY,
                    execution_id VARCHAR(100) UNIQUE NOT NULL,
                    workflow_name VARCHAR(100) NOT NULL,
                    build_id VARCHAR(100),
                    status VARCHAR(50) NOT NULL,  -- running, completed, failed, stopped
                    started_at TIMESTAMP NOT NULL,
                    finished_at TIMESTAMP,
                    duration_ms INTEGER,

                    -- Input data
                    input_data JSONB NOT NULL,

                    -- Output data
                    output_data JSONB,

                    -- Error information
                    error_message TEXT,
                    error_node VARCHAR(100),

                    -- Metadata
                    trigger_type VARCHAR(50),  -- manual, cron, api, aging
                    triggered_by VARCHAR(100),

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_executions_execution_id ON workflow_executions(execution_id);
                CREATE INDEX IF NOT EXISTS idx_executions_build_id ON workflow_executions(build_id);
                CREATE INDEX IF NOT EXISTS idx_executions_status ON workflow_executions(status);
                CREATE INDEX IF NOT EXISTS idx_executions_started_at ON workflow_executions(started_at DESC);
            """)

            # Node executions table (detailed node-level tracking)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS node_executions (
                    id SERIAL PRIMARY KEY,
                    execution_id VARCHAR(100) NOT NULL,
                    node_name VARCHAR(100) NOT NULL,
                    node_type VARCHAR(50),  -- classify, reasoning, select_tool, execute_tool, observe, answer, verify
                    sequence_number INTEGER NOT NULL,

                    -- Execution timing
                    started_at TIMESTAMP NOT NULL,
                    finished_at TIMESTAMP,
                    duration_ms INTEGER,

                    -- Node data
                    input_data JSONB NOT NULL,
                    output_data JSONB,

                    -- State before/after
                    state_before JSONB,
                    state_after JSONB,

                    -- Status
                    status VARCHAR(50) NOT NULL,  -- running, completed, failed, skipped
                    error_message TEXT,

                    -- Metadata
                    iteration INTEGER,
                    retry_count INTEGER DEFAULT 0,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (execution_id) REFERENCES workflow_executions(execution_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_node_executions_execution_id ON node_executions(execution_id);
                CREATE INDEX IF NOT EXISTS idx_node_executions_sequence ON node_executions(execution_id, sequence_number);
            """)

            conn.commit()
            cursor.close()
            logger.info("✅ Workflow execution tracking schema initialized")

    def start_execution(
        self,
        execution_id: str,
        workflow_name: str,
        input_data: Dict,
        build_id: Optional[str] = None,
        trigger_type: str = "manual",
        triggered_by: Optional[str] = None
    ) -> str:
        """
        Start tracking a new workflow execution

        Args:
            execution_id: Unique execution identifier
            workflow_name: Name of the workflow (e.g., "react_agent")
            input_data: Input data for the workflow
            build_id: Optional build ID for correlation
            trigger_type: How the workflow was triggered
            triggered_by: User/service that triggered it

        Returns:
            execution_id
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO workflow_executions (
                    execution_id, workflow_name, build_id, status,
                    started_at, input_data, trigger_type, triggered_by
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                execution_id,
                workflow_name,
                build_id,
                'running',
                datetime.utcnow(),
                Json(input_data),
                trigger_type,
                triggered_by
            ))

            conn.commit()
            cursor.close()

            logger.info(f"🚀 Started execution tracking: {execution_id}")
            return execution_id

    def log_node_start(
        self,
        execution_id: str,
        node_name: str,
        node_type: str,
        input_data: Dict,
        state_before: Dict,
        sequence_number: int,
        iteration: int = 0
    ) -> int:
        """
        Log the start of a node execution

        Args:
            execution_id: Execution ID
            node_name: Node name
            node_type: Type of node
            input_data: Input data for this node
            state_before: Full state before node execution
            sequence_number: Order of execution
            iteration: Iteration number (for loops)

        Returns:
            node_execution_id
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO node_executions (
                    execution_id, node_name, node_type, sequence_number,
                    started_at, input_data, state_before, status, iteration
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                execution_id,
                node_name,
                node_type,
                sequence_number,
                datetime.utcnow(),
                Json(input_data),
                Json(state_before),
                'running',
                iteration
            ))

            node_execution_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()

            logger.debug(f"  📍 Node started: {node_name} (seq: {sequence_number})")
            return node_execution_id

    def log_node_complete(
        self,
        execution_id: str,
        node_name: str,
        sequence_number: int,
        output_data: Dict,
        state_after: Dict,
        duration_ms: int
    ):
        """
        Log successful node completion

        Args:
            execution_id: Execution ID
            node_name: Node name
            sequence_number: Sequence number
            output_data: Output from the node
            state_after: Full state after node execution
            duration_ms: Execution time in milliseconds
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE node_executions
                SET status = 'completed',
                    finished_at = %s,
                    duration_ms = %s,
                    output_data = %s,
                    state_after = %s
                WHERE execution_id = %s
                  AND sequence_number = %s
            """, (
                datetime.utcnow(),
                duration_ms,
                Json(output_data),
                Json(state_after),
                execution_id,
                sequence_number
            ))

            conn.commit()
            cursor.close()

            logger.debug(f"  ✅ Node completed: {node_name} ({duration_ms}ms)")

    def log_node_error(
        self,
        execution_id: str,
        node_name: str,
        sequence_number: int,
        error_message: str,
        duration_ms: int,
        state_after: Optional[Dict] = None
    ):
        """
        Log node execution error

        Args:
            execution_id: Execution ID
            node_name: Node name
            sequence_number: Sequence number
            error_message: Error message
            duration_ms: Time before error
            state_after: State after error (if available)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE node_executions
                SET status = 'failed',
                    finished_at = %s,
                    duration_ms = %s,
                    error_message = %s,
                    state_after = %s
                WHERE execution_id = %s
                  AND sequence_number = %s
            """, (
                datetime.utcnow(),
                duration_ms,
                error_message,
                Json(state_after) if state_after else None,
                execution_id,
                sequence_number
            ))

            conn.commit()
            cursor.close()

            logger.error(f"  ❌ Node failed: {node_name} - {error_message}")

    def complete_execution(
        self,
        execution_id: str,
        status: str,  # 'completed' or 'failed'
        output_data: Optional[Dict] = None,
        error_message: Optional[str] = None,
        error_node: Optional[str] = None
    ):
        """
        Mark workflow execution as complete

        Args:
            execution_id: Execution ID
            status: Final status
            output_data: Final output data
            error_message: Error message if failed
            error_node: Node where error occurred
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get start time to calculate duration
            cursor.execute("""
                SELECT started_at FROM workflow_executions
                WHERE execution_id = %s
            """, (execution_id,))

            row = cursor.fetchone()
            if row:
                started_at = row[0]
                duration_ms = int((datetime.utcnow() - started_at).total_seconds() * 1000)
            else:
                duration_ms = None

            cursor.execute("""
                UPDATE workflow_executions
                SET status = %s,
                    finished_at = %s,
                    duration_ms = %s,
                    output_data = %s,
                    error_message = %s,
                    error_node = %s
                WHERE execution_id = %s
            """, (
                status,
                datetime.utcnow(),
                duration_ms,
                Json(output_data) if output_data else None,
                error_message,
                error_node,
                execution_id
            ))

            conn.commit()
            cursor.close()

            status_emoji = "✅" if status == "completed" else "❌"
            logger.info(f"{status_emoji} Execution {status}: {execution_id} ({duration_ms}ms)")

    def get_execution_details(self, execution_id: str) -> Optional[Dict]:
        """
        Get complete execution details with all node data

        Returns execution in n8n-style format with:
        - Execution metadata
        - List of all nodes with input/output
        - Execution flow

        Args:
            execution_id: Execution ID

        Returns:
            Dictionary with execution details or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get execution metadata
            cursor.execute("""
                SELECT * FROM workflow_executions
                WHERE execution_id = %s
            """, (execution_id,))

            execution = cursor.fetchone()
            if not execution:
                return None

            # Get all node executions
            cursor.execute("""
                SELECT * FROM node_executions
                WHERE execution_id = %s
                ORDER BY sequence_number ASC
            """, (execution_id,))

            nodes = cursor.fetchall()
            cursor.close()

            # Format like n8n execution data
            return {
                'id': execution['id'],
                'execution_id': execution['execution_id'],
                'workflow_name': execution['workflow_name'],
                'build_id': execution['build_id'],
                'status': execution['status'],
                'started_at': execution['started_at'].isoformat() if execution['started_at'] else None,
                'finished_at': execution['finished_at'].isoformat() if execution['finished_at'] else None,
                'duration_ms': execution['duration_ms'],
                'input_data': execution['input_data'],
                'output_data': execution['output_data'],
                'error_message': execution['error_message'],
                'error_node': execution['error_node'],
                'trigger_type': execution['trigger_type'],
                'triggered_by': execution['triggered_by'],
                'nodes': [
                    {
                        'id': node['id'],
                        'node_name': node['node_name'],
                        'node_type': node['node_type'],
                        'sequence_number': node['sequence_number'],
                        'started_at': node['started_at'].isoformat() if node['started_at'] else None,
                        'finished_at': node['finished_at'].isoformat() if node['finished_at'] else None,
                        'duration_ms': node['duration_ms'],
                        'status': node['status'],
                        'input_data': node['input_data'],
                        'output_data': node['output_data'],
                        'state_before': node['state_before'],
                        'state_after': node['state_after'],
                        'error_message': node['error_message'],
                        'iteration': node['iteration'],
                        'retry_count': node['retry_count']
                    }
                    for node in nodes
                ]
            }

    def get_recent_executions(self, limit: int = 50, workflow_name: Optional[str] = None) -> List[Dict]:
        """
        Get recent workflow executions (like n8n's executions list)

        Args:
            limit: Maximum number of executions to return
            workflow_name: Filter by workflow name

        Returns:
            List of execution summaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT
                    id, execution_id, workflow_name, build_id, status,
                    started_at, finished_at, duration_ms,
                    trigger_type, triggered_by,
                    error_message, error_node
                FROM workflow_executions
            """

            params = []
            if workflow_name:
                query += " WHERE workflow_name = %s"
                params.append(workflow_name)

            query += " ORDER BY started_at DESC LIMIT %s"
            params.append(limit)

            cursor.execute(query, params)
            executions = cursor.fetchall()
            cursor.close()

            return [
                {
                    'id': ex['id'],
                    'execution_id': ex['execution_id'],
                    'workflow_name': ex['workflow_name'],
                    'build_id': ex['build_id'],
                    'status': ex['status'],
                    'started_at': ex['started_at'].isoformat() if ex['started_at'] else None,
                    'finished_at': ex['finished_at'].isoformat() if ex['finished_at'] else None,
                    'duration_ms': ex['duration_ms'],
                    'trigger_type': ex['trigger_type'],
                    'triggered_by': ex['triggered_by'],
                    'error_message': ex['error_message'],
                    'error_node': ex['error_node']
                }
                for ex in executions
            ]


# Global instance
_tracker = None

def get_workflow_tracker() -> WorkflowExecutionTracker:
    """Get or create global tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = WorkflowExecutionTracker()
    return _tracker
