# Phase 3: Agentic Workflow Debugging System (n8n-style)

**Date**: December 17, 2025
**Status**: ✅ **IMPLEMENTED**

## Overview

Phase 3 implements a comprehensive workflow execution tracking and debugging system, similar to n8n's workflow visualization. This allows you to:

- **View all workflow executions** in a list (like n8n's executions page)
- **Inspect each node** with input/output data (like clicking on nodes in n8n)
- **Debug failures** with detailed error logs at node level
- **Monitor performance** with execution timing for each node
- **Track state changes** across the workflow

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Triggers Workflow                   │
│              (Manual Trigger / Cron / Aging Service)         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      v
    ┌──────────────────────────────────────────────────┐
    │        LangGraph ReAct Agent (Port 5000)         │
    │   Wrapped with ReActAgentLogger                  │
    └──────────────────┬───────────────────────────────┘
                       │
                       │ Logs each node execution
                       v
    ┌──────────────────────────────────────────────────┐
    │     WorkflowExecutionTracker (PostgreSQL)        │
    │   - workflow_executions table                    │
    │   - node_executions table                        │
    └──────────────────┬───────────────────────────────┘
                       │
                       │ API queries
                       v
    ┌──────────────────────────────────────────────────┐
    │   Workflow Executions API (Port 5016)            │
    │   REST API to retrieve execution data            │
    └──────────────────┬───────────────────────────────┘
                       │
                       │ Frontend calls API
                       v
    ┌──────────────────────────────────────────────────┐
    │   Workflow Executions Page (React)               │
    │   http://localhost:5173/workflow-executions      │
    │   n8n-style UI visualization                     │
    └──────────────────────────────────────────────────┘
```

---

## Components

### 1. Workflow Execution Tracker

**File**: `implementation/workflow_execution_tracker.py`

**Purpose**: Core tracking system that stores execution data in PostgreSQL

**Database Schema**:

```sql
-- Main execution record
CREATE TABLE workflow_executions (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(100) UNIQUE,
    workflow_name VARCHAR(100),
    build_id VARCHAR(100),
    status VARCHAR(50),  -- running, completed, failed, stopped
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    duration_ms INTEGER,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    error_node VARCHAR(100),
    trigger_type VARCHAR(50),
    triggered_by VARCHAR(100)
);

-- Node-level execution data
CREATE TABLE node_executions (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(100),
    node_name VARCHAR(100),
    node_type VARCHAR(50),
    sequence_number INTEGER,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    duration_ms INTEGER,
    input_data JSONB,        -- Node input (like n8n's Input tab)
    output_data JSONB,       -- Node output (like n8n's Output tab)
    state_before JSONB,      -- State snapshot before execution
    state_after JSONB,       -- State snapshot after execution
    status VARCHAR(50),
    error_message TEXT,
    iteration INTEGER,
    retry_count INTEGER
);
```

**Key Methods**:
- `start_execution()` - Start tracking a new workflow run
- `log_node_start()` - Log when a node starts executing
- `log_node_complete()` - Log successful node completion with output
- `log_node_error()` - Log node execution errors
- `complete_execution()` - Mark workflow as complete/failed
- `get_execution_details()` - Retrieve full execution with all nodes
- `get_recent_executions()` - Get list of recent executions

### 2. ReAct Agent Logger

**File**: `implementation/agents/react_agent_logger.py`

**Purpose**: Wrapper around your ReActAgent that adds automatic logging

**How It Works**:

```python
from agents.react_agent_logger import create_logged_agent
from agents.react_agent_service import create_react_agent

# Create base agent
agent = create_react_agent()

# Wrap with logging
logged_agent = create_logged_agent(agent)

# Execute with full tracking
result = logged_agent.execute_with_logging(
    build_id="BUILD-123",
    error_log="Test failed...",
    error_message="AssertionError: Expected 5 but got 3",
    trigger_type="manual",
    triggered_by="user@example.com"
)

# Result includes execution_id
print(f"Execution ID: {result['execution_id']}")
# View at: http://localhost:5173/workflow-executions
```

**Logged Data for Each Node**:

1. **classify** node:
   - Input: error_message, error_log
   - Output: error_category, classification_confidence

2. **reasoning** node (iterative):
   - Input: error_category, iteration, needs_more_info
   - Output: current_thought, should_continue

3. **select_tool** node:
   - Input: current_thought, error_category
   - Output: next_action (tool to execute)

4. **execute_tool** node:
   - Input: next_action, error_category
   - Output: tool_result_keys, execution_success

5. **observe** node:
   - Input: tool_results
   - Output: observation_added

6. **answer** node:
   - Input: iterations, actions_taken_count
   - Output: root_cause, solution_confidence

7. **verify** node (CRAG):
   - Input: root_cause, solution_confidence
   - Output: crag_confidence, crag_action

### 3. Workflow Executions API

**File**: `implementation/workflow_executions_api.py`
**Port**: 5016

**Endpoints**:

```bash
# Health check
GET /health

# List all executions (with filters)
GET /api/executions?limit=50&status=completed&workflow=react_agent

# Get detailed execution data
GET /api/executions/{execution_id}

# Get specific node execution
GET /api/executions/{execution_id}/nodes/{sequence_number}

# Get execution statistics
GET /api/executions/stats?days=7

# Advanced search
POST /api/executions/search
{
  "workflow_name": "react_agent",
  "status": ["completed", "failed"],
  "date_range": {
    "from": "2025-12-01T00:00:00Z",
    "to": "2025-12-31T23:59:59Z"
  }
}
```

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "execution_id": "exec_BUILD-123_a1b2c3d4",
    "workflow_name": "react_agent",
    "build_id": "BUILD-123",
    "status": "completed",
    "started_at": "2025-12-17T10:30:00Z",
    "finished_at": "2025-12-17T10:30:15Z",
    "duration_ms": 15234,
    "nodes": [
      {
        "id": 1,
        "node_name": "classify",
        "node_type": "classify",
        "sequence_number": 1,
        "duration_ms": 1245,
        "status": "completed",
        "input_data": {
          "error_message": "AssertionError: Expected 5 but got 3",
          "error_log": "test_calculator.py:line 42..."
        },
        "output_data": {
          "error_category": "TEST_FAILURE",
          "classification_confidence": 0.95
        },
        "state_before": {...},
        "state_after": {...}
      },
      {
        "node_name": "reasoning_iter0",
        "node_type": "reasoning",
        ...
      }
    ]
  }
}
```

### 4. Workflow Executions UI Page

**File**: `implementation/dashboard-ui/src/pages/WorkflowExecutionsPage.jsx`
**URL**: http://localhost:5173/workflow-executions

**Features** (n8n-style):

✅ **Executions List**:
- Table view of all executions
- Filter by status (completed, failed, running)
- Search by execution ID or build ID
- Shows duration, trigger type, timestamps

✅ **Execution Details Modal**:
- Click any execution to see full details
- Timeline of all nodes executed
- Each node shows:
  - Status (success/failed/running)
  - Duration
  - Input/Output tabs (like n8n)
  - State snapshot
  - Error messages

✅ **Node Visualization**:
- Expandable cards for each node
- Icon for node type (🏷️ classify, 🤔 reasoning, etc.)
- Iteration badges for loop nodes
- JSON viewers for input/output data
- Color-coded status indicators

✅ **Performance Metrics**:
- Total execution time
- Per-node timing
- Success rate statistics

---

## How to Use

### Step 1: Start the Service

```bash
# Start workflow executions API
docker compose -f docker-compose-unified.yml up -d workflow-executions

# Check health
curl http://localhost:5016/health
```

### Step 2: Run a Workflow

When you trigger a manual analysis or any workflow runs, it will automatically be logged.

**Example: Manual Trigger**

```bash
curl -X POST http://localhost:5004/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "BUILD-456",
    "error_log": "Test failed with assertion error",
    "error_message": "Expected 10 but got 5",
    "trigger_type": "manual",
    "triggered_by": "admin@example.com"
  }'
```

### Step 3: View Execution in UI

1. Open browser: http://localhost:5173/workflow-executions
2. See your execution in the list
3. Click "View Details" icon (eye icon)
4. Explore each node:
   - Click expand arrow on any node
   - View Input/Output/State tabs
   - Check execution timing
   - See errors if any

### Step 4: Debug Failures

If a workflow fails:

1. Find the failed execution (red error chip)
2. Open details
3. Find the node that failed (red status)
4. Check the error message
5. Expand the node to see:
   - What input it received
   - What state it was in
   - Exact error message
   - How long before it failed

---

## API Examples

### Get Recent Executions

```bash
curl http://localhost:5016/api/executions?limit=10
```

### Get Execution Details

```bash
curl http://localhost:5016/api/executions/exec_BUILD-456_a1b2c3d4
```

### Filter by Status

```bash
curl "http://localhost:5016/api/executions?status=failed&limit=20"
```

### Get Statistics

```bash
curl "http://localhost:5016/api/executions/stats?days=7"
```

Response:
```json
{
  "status": "success",
  "data": {
    "summary": {
      "total_executions": 145,
      "completed": 128,
      "failed": 15,
      "running": 2,
      "success_rate": 88.28,
      "avg_duration_ms": 12456,
      "avg_duration_sec": 12.46
    },
    "by_trigger": {
      "manual": 45,
      "cron": 80,
      "aging": 20
    },
    "recent_failures": [...]
  }
}
```

### Advanced Search

```bash
curl -X POST http://localhost:5016/api/executions/search \
  -H "Content-Type: application/json" \
  -d '{
    "status": ["failed"],
    "error_contains": "timeout",
    "date_range": {
      "from": "2025-12-01T00:00:00Z",
      "to": "2025-12-17T23:59:59Z"
    },
    "limit": 50
  }'
```

---

## Integration with Existing System

### Update LangGraph Agent

**Current**: `implementation/langgraph_agent.py`

**Add logging wrapper**:

```python
# At the top
from agents.react_agent_logger import create_logged_agent

# When creating agent
react_agent = create_react_agent()

# Wrap with logger
logged_agent = create_logged_agent(react_agent)

# In your analyze endpoint, use logged_agent instead
@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()

    # Use logged agent (automatic tracking)
    result = logged_agent.execute_with_logging(
        build_id=data['build_id'],
        error_log=data['error_log'],
        error_message=data['error_message'],
        stack_trace=data.get('stack_trace'),
        job_name=data.get('job_name'),
        test_name=data.get('test_name'),
        trigger_type=data.get('trigger_type', 'manual'),
        triggered_by=request.headers.get('X-User-Email')
    )

    return jsonify(result)
```

---

## Comparison with n8n

| Feature | n8n | Our System | Status |
|---------|-----|------------|--------|
| Execution list | ✅ | ✅ | Implemented |
| Node-level input/output | ✅ | ✅ | Implemented |
| Execution timeline | ✅ | ✅ | Implemented |
| Error tracking | ✅ | ✅ | Implemented |
| Performance metrics | ✅ | ✅ | Implemented |
| State snapshots | ❌ | ✅ | **Enhanced!** |
| Iteration tracking | ❌ | ✅ | **Enhanced!** |
| Search & filter | ✅ | ✅ | Implemented |
| Execution replay | ✅ | 🔄 | Future |
| Real-time updates | ✅ | 🔄 | Future |

---

## Testing

### 1. Initialize Database

The database schema is automatically created on first run by `WorkflowExecutionTracker`.

### 2. Test API

```bash
# Health check
curl http://localhost:5016/health

# Should return:
{
  "service": "workflow_executions_api",
  "status": "healthy",
  "port": 5016
}
```

### 3. Run Test Workflow

```bash
# Trigger a test analysis
curl -X POST http://localhost:5004/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "TEST-001",
    "error_log": "test_example.py:45 AssertionError",
    "error_message": "Expected 42 but got 43"
  }'
```

### 4. View in UI

1. Open http://localhost:5173/workflow-executions
2. You should see TEST-001 in the list
3. Click to view details
4. Expand nodes to see input/output

---

## Services & Ports Summary

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| LangGraph Agent | 5000 | http://localhost:5000 | Main workflow engine |
| Workflow Executions API | 5016 | http://localhost:5016 | Execution data API |
| Dashboard UI | 5173 | http://localhost:5173 | Frontend |
| Executions Page | - | http://localhost:5173/workflow-executions | n8n-style viewer |

---

## Troubleshooting

### No executions showing up

**Check**:
1. Is workflow-executions service running?
   ```bash
   docker ps | grep workflow-executions
   ```

2. Are database tables created?
   ```bash
   docker exec ddn-postgres psql -U postgres -d ddn_ai_analysis -c "\dt"
   ```
   Should show: `workflow_executions` and `node_executions`

3. Is the logger integrated?
   - Check if `react_agent_logger.py` is imported in your workflow

### Executions showing but no node data

**Check**:
1. View API response directly:
   ```bash
   curl http://localhost:5016/api/executions/{execution_id}
   ```

2. Check node_executions table:
   ```bash
   docker exec ddn-postgres psql -U postgres -d ddn_ai_analysis \
     -c "SELECT * FROM node_executions WHERE execution_id = 'exec_...' ORDER BY sequence_number;"
   ```

### UI not loading

**Check**:
1. Environment variable set:
   ```bash
   docker exec ddn-dashboard-ui env | grep WORKFLOW
   ```
   Should show: `VITE_WORKFLOW_API_URL=http://workflow-executions:5016`

2. Restart dashboard:
   ```bash
   docker compose -f docker-compose-unified.yml restart dashboard-ui
   ```

---

## Next Steps & Enhancements

### Planned for Phase 4:

1. **Real-time Updates**
   - WebSocket connection for live execution monitoring
   - Auto-refresh when new executions start

2. **Execution Replay**
   - Re-run failed executions with same input
   - Step-by-step debugging mode

3. **Performance Analytics**
   - Identify slow nodes
   - Execution time trends
   - Bottleneck detection

4. **Export & Share**
   - Download execution logs as JSON
   - Share execution URLs
   - Generate execution reports

5. **Workflow Comparison**
   - Compare two executions side-by-side
   - Diff tool for inputs/outputs
   - Identify what changed between runs

---

## Documentation References

### n8n Workflow Debugging
- [Debug and re-run past executions | n8n Docs](https://docs.n8n.io/workflows/executions/debug/)
- [All executions | n8n Docs](https://docs.n8n.io/workflows/executions/all-executions/)
- [n8n Workflow Debugging Guide](https://n8npro.in/n8n-basics/debugging-your-n8n-workflows-effectively/)

### Project Files
- `implementation/workflow_execution_tracker.py` - Core tracking system
- `implementation/agents/react_agent_logger.py` - Logging wrapper
- `implementation/workflow_executions_api.py` - REST API
- `implementation/dashboard-ui/src/pages/WorkflowExecutionsPage.jsx` - UI

---

**Phase 3 Status**: ✅ **COMPLETE**
**Created by**: Claude Sonnet 4.5
**Date**: December 17, 2025

**Ready to debug workflows like a pro!** 🚀
