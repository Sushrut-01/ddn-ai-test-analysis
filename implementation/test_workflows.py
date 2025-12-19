"""
Unit Tests for Python Workflows
Tests workflow JSON structure, API endpoints, and node connections
"""

import json
import os
import sys
import unittest
import requests
from datetime import datetime

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Workflow directory
WORKFLOWS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workflows')
API_BASE_URL = 'http://localhost:5006'


class TestWorkflowStructure(unittest.TestCase):
    """Test workflow JSON file structure and validity"""

    @classmethod
    def setUpClass(cls):
        """Load all workflow files"""
        cls.workflows = {}
        cls.workflow_files = [
            'ddn_ai_complete_workflow_v2.json',
            'workflow_2_manual_trigger.json',
            'workflow_3_refinement.json',
            'workflow_4_auto_fix.json'
        ]

        for filename in cls.workflow_files:
            filepath = os.path.join(WORKFLOWS_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    cls.workflows[filename] = json.load(f)

    def test_all_workflow_files_exist(self):
        """Test that all expected workflow files exist"""
        for filename in self.workflow_files:
            filepath = os.path.join(WORKFLOWS_DIR, filename)
            self.assertTrue(os.path.exists(filepath), f"Workflow file missing: {filename}")
        print("[PASS] All 4 workflow files exist")

    def test_workflow_json_valid(self):
        """Test that all workflow files contain valid JSON"""
        for filename, workflow in self.workflows.items():
            self.assertIsInstance(workflow, dict, f"Invalid JSON in {filename}")
        print("[PASS] All workflow files contain valid JSON")

    def test_workflow_has_required_fields(self):
        """Test that workflows have required top-level fields"""
        required_fields = ['name', 'version', 'description', 'nodes', 'connections']

        for filename, workflow in self.workflows.items():
            for field in required_fields:
                self.assertIn(field, workflow, f"Missing field '{field}' in {filename}")
        print("[PASS] All workflows have required fields (name, version, description, nodes, connections)")

    def test_workflow_has_nodes(self):
        """Test that workflows have at least one node"""
        for filename, workflow in self.workflows.items():
            nodes = workflow.get('nodes', [])
            self.assertGreater(len(nodes), 0, f"No nodes in {filename}")
        print("[PASS] All workflows have nodes defined")

    def test_workflow_nodes_have_required_fields(self):
        """Test that each node has required fields"""
        node_required_fields = ['id', 'name', 'type']

        for filename, workflow in self.workflows.items():
            for node in workflow.get('nodes', []):
                for field in node_required_fields:
                    self.assertIn(field, node, f"Node missing '{field}' in {filename}: {node.get('name', 'unknown')}")
        print("[PASS] All workflow nodes have required fields (id, name, type)")

    def test_workflow_version_format(self):
        """Test that workflow versions follow semver format"""
        import re
        semver_pattern = r'^\d+\.\d+\.\d+$'

        for filename, workflow in self.workflows.items():
            version = workflow.get('version', '')
            self.assertTrue(
                re.match(semver_pattern, version),
                f"Invalid version format in {filename}: {version}"
            )
        print("[PASS] All workflow versions follow semver format (X.Y.Z)")

    def test_workflow_connections_valid(self):
        """Test that connections reference valid node names"""
        for filename, workflow in self.workflows.items():
            nodes = workflow.get('nodes', [])
            node_names = {node['name'] for node in nodes}
            connections = workflow.get('connections', {})

            for source_node in connections.keys():
                # Source node should exist (by name)
                self.assertIn(source_node, node_names,
                    f"Connection source '{source_node}' not found in nodes of {filename}")
        print("[PASS] All workflow connections reference valid nodes")


class TestWorkflowAPI(unittest.TestCase):
    """Test workflow API endpoints"""

    def test_api_workflows_endpoint(self):
        """Test GET /api/workflows returns workflow list"""
        try:
            response = requests.get(f'{API_BASE_URL}/api/workflows', timeout=10)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data.get('success', False))
            self.assertIn('workflows', data)
            self.assertIn('count', data)
            print(f"[PASS] GET /api/workflows returns {data['count']} workflows")
        except requests.exceptions.ConnectionError:
            self.skipTest("API server not running on localhost:5006")

    def test_api_workflows_count(self):
        """Test that API returns correct number of workflows"""
        try:
            response = requests.get(f'{API_BASE_URL}/api/workflows', timeout=10)
            data = response.json()
            self.assertEqual(data['count'], 4, "Expected 4 workflows")
            print("[PASS] API returns correct workflow count (4)")
        except requests.exceptions.ConnectionError:
            self.skipTest("API server not running on localhost:5006")

    def test_api_workflow_details(self):
        """Test GET /api/workflows/<id> returns workflow details"""
        workflow_ids = [
            'ddn_ai_complete_workflow_v2',
            'workflow_2_manual_trigger',
            'workflow_3_refinement',
            'workflow_4_auto_fix'
        ]

        try:
            for wf_id in workflow_ids:
                response = requests.get(f'{API_BASE_URL}/api/workflows/{wf_id}', timeout=10)
                self.assertEqual(response.status_code, 200, f"Failed for {wf_id}")
                data = response.json()
                self.assertTrue(data.get('success', False))
                self.assertIn('workflow', data)
            print("[PASS] All workflow detail endpoints return valid data")
        except requests.exceptions.ConnectionError:
            self.skipTest("API server not running on localhost:5006")

    def test_api_workflow_executions(self):
        """Test GET /api/workflows/executions returns execution history"""
        try:
            response = requests.get(f'{API_BASE_URL}/api/workflows/executions', timeout=10)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data.get('success', False))
            self.assertIn('executions', data)
            print(f"[PASS] GET /api/workflows/executions returns {data.get('count', 0)} executions")
        except requests.exceptions.ConnectionError:
            self.skipTest("API server not running on localhost:5006")

    def test_api_execution_stats(self):
        """Test that execution stats are included in workflows response"""
        try:
            response = requests.get(f'{API_BASE_URL}/api/workflows', timeout=10)
            data = response.json()
            self.assertIn('execution_stats', data)
            stats = data['execution_stats']
            self.assertIn('total', stats)
            self.assertIn('successful', stats)
            self.assertIn('failed', stats)
            print(f"[PASS] Execution stats: {stats['total']} total, {stats['successful']} successful, {stats['failed']} failed")
        except requests.exceptions.ConnectionError:
            self.skipTest("API server not running on localhost:5006")


class TestWorkflowContent(unittest.TestCase):
    """Test workflow content and logic"""

    @classmethod
    def setUpClass(cls):
        """Load all workflow files"""
        cls.workflows = {}
        workflow_files = [
            'ddn_ai_complete_workflow_v2.json',
            'workflow_2_manual_trigger.json',
            'workflow_3_refinement.json',
            'workflow_4_auto_fix.json'
        ]

        for filename in workflow_files:
            filepath = os.path.join(WORKFLOWS_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    cls.workflows[filename] = json.load(f)

    def test_complete_workflow_has_webhook_trigger(self):
        """Test that complete workflow starts with webhook trigger"""
        workflow = self.workflows.get('ddn_ai_complete_workflow_v2.json', {})
        nodes = workflow.get('nodes', [])
        trigger_nodes = [n for n in nodes if 'webhook' in n.get('type', '').lower() or 'trigger' in n.get('name', '').lower()]
        self.assertGreater(len(trigger_nodes), 0, "No webhook trigger found")
        print("[PASS] Complete workflow has webhook trigger node")

    def test_workflows_have_mongodb_integration(self):
        """Test that workflows integrate with MongoDB"""
        for filename, workflow in self.workflows.items():
            nodes = workflow.get('nodes', [])
            mongo_nodes = [n for n in nodes if 'mongo' in n.get('type', '').lower() or 'mongodb' in n.get('name', '').lower()]
            # At least main workflow should have MongoDB
            if 'complete' in filename.lower():
                self.assertGreater(len(mongo_nodes), 0, f"No MongoDB node in {filename}")
        print("[PASS] Workflows have MongoDB integration")

    def test_complete_workflow_has_langgraph_classification(self):
        """Test that complete workflow has LangGraph classification"""
        workflow = self.workflows.get('ddn_ai_complete_workflow_v2.json', {})
        nodes = workflow.get('nodes', [])
        langgraph_nodes = [n for n in nodes if 'langgraph' in n.get('name', '').lower() or 'classify' in n.get('name', '').lower()]
        self.assertGreater(len(langgraph_nodes), 0, "No LangGraph classification found")
        print("[PASS] Complete workflow has LangGraph classification node")

    def test_workflows_have_solution_storage(self):
        """Test that workflows store solutions (store, update, save patterns)"""
        for filename, workflow in self.workflows.items():
            nodes = workflow.get('nodes', [])
            # Look for any node that stores/updates/saves solutions
            store_patterns = ['store', 'update', 'save', 'write', 'persist']
            store_nodes = [n for n in nodes if any(p in n.get('name', '').lower() for p in store_patterns)]
            self.assertGreater(len(store_nodes), 0, f"No solution storage in {filename}")
        print("[PASS] All workflows have solution storage nodes")

    def test_workflow_node_count(self):
        """Test workflow node counts match expectations"""
        expected_counts = {
            'ddn_ai_complete_workflow_v2.json': (15, 20),  # min, max
            'workflow_2_manual_trigger.json': (10, 18),
            'workflow_3_refinement.json': (10, 18),
            'workflow_4_auto_fix.json': (8, 15)
        }

        for filename, workflow in self.workflows.items():
            node_count = len(workflow.get('nodes', []))
            min_count, max_count = expected_counts.get(filename, (1, 100))
            self.assertGreaterEqual(node_count, min_count, f"Too few nodes in {filename}: {node_count}")
            self.assertLessEqual(node_count, max_count, f"Too many nodes in {filename}: {node_count}")
            print(f"[PASS] {filename}: {node_count} nodes (expected {min_count}-{max_count})")


class TestWorkflowIntegration(unittest.TestCase):
    """Integration tests for workflow system"""

    def test_workflow_api_responds(self):
        """Test that workflow API is responding"""
        try:
            response = requests.get(f'{API_BASE_URL}/api/workflows', timeout=5)
            self.assertEqual(response.status_code, 200)
            print("[PASS] Workflow API is responding")
        except requests.exceptions.ConnectionError:
            self.skipTest("API server not running")

    def test_workflow_metadata_complete(self):
        """Test that workflow metadata is complete"""
        try:
            response = requests.get(f'{API_BASE_URL}/api/workflows', timeout=10)
            data = response.json()

            for workflow in data.get('workflows', []):
                self.assertIn('id', workflow)
                self.assertIn('name', workflow)
                self.assertIn('version', workflow)
                self.assertIn('node_count', workflow)
                self.assertIn('status', workflow)
                self.assertIn('type', workflow)
            print("[PASS] All workflow metadata fields are present")
        except requests.exceptions.ConnectionError:
            self.skipTest("API server not running")


def run_tests():
    """Run all tests and generate summary"""
    print("\n" + "="*70)
    print("  PYTHON WORKFLOWS UNIT TEST SUITE")
    print("  Testing: Structure, API, Content, Integration")
    print("="*70 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowContent))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Generate summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)

    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total - failures - errors - skipped

    print(f"\n  Total Tests:   {total}")
    print(f"  [PASS]  Passed:    {passed}")
    print(f"  [FAIL]  Failed:    {failures}")
    print(f"  [ERROR] Errors:    {errors}")
    print(f"  [SKIP]  Skipped:   {skipped}")
    print(f"\n  Success Rate:  {(passed/total*100):.1f}%" if total > 0 else "  No tests run")

    print("\n" + "="*70)

    if failures > 0:
        print("\n  FAILURES:")
        for test, traceback in result.failures:
            print(f"    - {test}: {traceback.split(chr(10))[0]}")

    if errors > 0:
        print("\n  ERRORS:")
        for test, traceback in result.errors:
            print(f"    - {test}: {traceback.split(chr(10))[0]}")

    return result


if __name__ == '__main__':
    run_tests()
