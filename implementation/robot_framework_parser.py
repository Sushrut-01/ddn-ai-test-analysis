"""
Robot Framework Test Result Parser for Guruttava Project
Date: 2026-01-14
Description: Parses Robot Framework output.xml files and stores results in MongoDB
Supports: Mobile (Android/iOS) and Web test automation
"""

import xml.etree.ElementTree as ET
import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RobotFrameworkParser:
    """Parse Robot Framework output.xml and extract test failures"""

    def __init__(self, mongodb_uri: str = None, database_name: str = 'ddn_tests'):
        """Initialize parser with MongoDB connection"""
        self.mongodb_uri = mongodb_uri or os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = database_name
        self.client = None
        self.db = None

    def connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            logger.info(f"📡 Connecting to MongoDB: {self.mongodb_uri}")
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.server_info()
            logger.info(f"✅ Connected to MongoDB database: {self.database_name}")
            return True
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False

    def parse_output_xml(self, xml_path: str, project_id: int, build_id: str,
                        platform: str = 'Unknown', test_type: str = 'Unknown') -> Dict:
        """
        Parse Robot Framework output.xml file

        Args:
            xml_path: Path to output.xml file
            project_id: Project ID (e.g., 2 for Guruttava)
            build_id: Jenkins build ID
            platform: Android, iOS, or Web
            test_type: Smoke, Regression, Sanity, etc.

        Returns:
            Dict with parsed results
        """
        try:
            logger.info(f"📖 Parsing Robot Framework output: {xml_path}")

            if not os.path.exists(xml_path):
                raise FileNotFoundError(f"Output XML not found: {xml_path}")

            # Parse XML
            tree = ET.parse(xml_path)
            root = tree.getroot()

            results = {
                'project_id': project_id,
                'build_id': build_id,
                'platform': platform,
                'test_type': test_type,
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0,
                'failures': [],
                'metadata': {}
            }

            # Extract metadata
            results['metadata'] = {
                'generator': root.get('generator', 'Robot Framework'),
                'generated_time': root.get('generated', ''),
                'source': root.get('source', ''),
                'rpa': root.get('rpa', 'false')
            }

            # Extract statistics
            stats_elem = root.find('.//statistics/total/stat')
            if stats_elem is not None:
                results['passed_tests'] = int(stats_elem.get('pass', 0))
                results['failed_tests'] = int(stats_elem.get('fail', 0))
                results['skipped_tests'] = int(stats_elem.get('skip', 0))
                results['total_tests'] = results['passed_tests'] + results['failed_tests'] + results['skipped_tests']

            logger.info(f"📊 Test Summary: {results['total_tests']} total, "
                       f"{results['passed_tests']} passed, "
                       f"{results['failed_tests']} failed, "
                       f"{results['skipped_tests']} skipped")

            # Extract individual test failures
            for suite in root.findall('.//suite'):
                suite_name = suite.get('name', 'Unknown Suite')
                suite_source = suite.get('source', '')

                for test in suite.findall('.//test'):
                    status_elem = test.find('status')
                    if status_elem is not None and status_elem.get('status') == 'FAIL':
                        failure = self._extract_test_failure(
                            test, suite_name, suite_source, project_id, build_id, platform, test_type
                        )
                        results['failures'].append(failure)

            logger.info(f"✅ Extracted {len(results['failures'])} test failures")

            return results

        except Exception as e:
            logger.error(f"❌ Error parsing Robot Framework output: {e}")
            raise

    def _extract_test_failure(self, test_elem: ET.Element, suite_name: str,
                             suite_source: str, project_id: int, build_id: str,
                             platform: str, test_type: str) -> Dict:
        """Extract detailed failure information from test element"""

        test_name = test_elem.get('name', 'Unknown Test')
        test_id = test_elem.get('id', '')

        # Get status element for timing and error message
        status_elem = test_elem.find('status')
        start_time = status_elem.get('starttime', '') if status_elem is not None else ''
        end_time = status_elem.get('endtime', '') if status_elem is not None else ''
        error_message = status_elem.text.strip() if status_elem is not None and status_elem.text else "Unknown error"

        # Extract duration in milliseconds
        duration_ms = self._calculate_duration(start_time, end_time)

        # Find the failing keyword
        stack_trace_parts = []
        screenshot_path = None

        for kw in test_elem.findall('.//kw'):
            kw_status = kw.find('status')
            if kw_status is not None and kw_status.get('status') == 'FAIL':
                kw_name = kw.get('name', '')
                kw_library = kw.get('library', '')
                kw_type = kw.get('type', 'KEYWORD')

                # Build stack trace
                stack_line = f"{kw_library}.{kw_name}" if kw_library else kw_name

                # Extract arguments
                args = [arg.text for arg in kw.findall('.//arg') if arg.text]
                if args:
                    stack_line += f"({', '.join(args)})"

                # Extract error message from keyword
                kw_error = kw_status.text.strip() if kw_status.text else ""
                if kw_error:
                    stack_line += f"\n  Error: {kw_error}"

                stack_trace_parts.append(stack_line)

                # Look for screenshot in messages
                for msg in kw.findall('.//msg'):
                    msg_text = msg.text or ""
                    if 'screenshot' in msg_text.lower() or '.png' in msg_text.lower():
                        screenshot_path = msg_text.strip()

        stack_trace = '\n'.join(stack_trace_parts) if stack_trace_parts else error_message

        # Extract tags
        tags = [tag.text for tag in test_elem.findall('.//tag') if tag.text]

        # Categorize error (basic categorization - can be enhanced)
        error_category = self._categorize_error(error_message, stack_trace)

        failure_data = {
            'project_id': project_id,
            'build_id': build_id,
            'test_name': test_name,
            'test_id': test_id,
            'test_suite': suite_name,
            'suite_source': suite_source,
            'error_message': error_message,
            'stack_trace': stack_trace,
            'error_category': error_category,
            'platform': platform,
            'test_type': test_type,
            'tags': tags,
            'screenshot_path': screenshot_path,
            'start_time': start_time,
            'end_time': end_time,
            'duration_ms': duration_ms,
            'timestamp': datetime.utcnow(),
            'analyzed': False,
            'analysis_id': None
        }

        return failure_data

    def _calculate_duration(self, start_time: str, end_time: str) -> int:
        """Calculate test duration in milliseconds"""
        try:
            if not start_time or not end_time:
                return 0

            # Robot Framework timestamp format: 20240114 12:30:45.123
            fmt = '%Y%m%d %H:%M:%S.%f'

            start = datetime.strptime(start_time, fmt)
            end = datetime.strptime(end_time, fmt)

            duration = (end - start).total_seconds() * 1000
            return int(duration)

        except Exception as e:
            logger.warning(f"⚠️  Could not calculate duration: {e}")
            return 0

    def _categorize_error(self, error_message: str, stack_trace: str) -> str:
        """Basic error categorization for Robot Framework failures"""

        error_text = (error_message + ' ' + stack_trace).lower()

        # Element/Locator errors
        if any(keyword in error_text for keyword in ['element not found', 'no element', 'could not find element',
                                                      'locator', 'xpath', 'selector']):
            return 'ELEMENT_NOT_FOUND'

        # Timeout errors
        if any(keyword in error_text for keyword in ['timeout', 'timed out', 'time limit exceeded']):
            return 'TIMEOUT_ERROR'

        # Assertion/Verification errors
        if any(keyword in error_text for keyword in ['should be equal', 'should contain', 'should not',
                                                      'assertion failed', 'expected', 'actual']):
            return 'ASSERTION_FAILED'

        # Mobile-specific errors
        if any(keyword in error_text for keyword in ['appium', 'android', 'ios', 'mobile', 'device',
                                                      'application not responding']):
            return 'MOBILE_ERROR'

        # Network/Connection errors
        if any(keyword in error_text for keyword in ['connection', 'network', 'socket', 'http', 'status code']):
            return 'NETWORK_ERROR'

        # Environment/Setup errors
        if any(keyword in error_text for keyword in ['setup failed', 'teardown failed', 'import error',
                                                      'library', 'resource']):
            return 'ENVIRONMENT_ERROR'

        return 'UNKNOWN'

    def store_failures_in_mongodb(self, failures: List[Dict], project_config: Dict) -> bool:
        """Store parsed failures in project-specific MongoDB collection"""
        try:
            if not self.db:
                if not self.connect_mongodb():
                    return False

            if not failures:
                logger.info("ℹ️  No failures to store")
                return True

            collection_prefix = project_config.get('mongodb_collection_prefix', 'guruttava_')
            collection_name = f"{collection_prefix}test_failures"

            logger.info(f"💾 Storing {len(failures)} failures in collection: {collection_name}")

            collection = self.db[collection_name]

            # Insert failures
            for failure in failures:
                # Check if failure already exists
                existing = collection.find_one({
                    'build_id': failure['build_id'],
                    'test_id': failure['test_id']
                })

                if existing:
                    logger.info(f"  ℹ️  Failure already exists for test: {failure['test_name']}")
                    continue

                collection.insert_one(failure)
                logger.info(f"  ✅ Stored: {failure['test_name']}")

            logger.info(f"✅ Successfully stored failures in MongoDB")
            return True

        except Exception as e:
            logger.error(f"❌ Error storing failures in MongoDB: {e}")
            return False

    def store_build_result(self, build_data: Dict, project_config: Dict) -> bool:
        """Store build result summary in MongoDB"""
        try:
            if not self.db:
                if not self.connect_mongodb():
                    return False

            collection_prefix = project_config.get('mongodb_collection_prefix', 'guruttava_')
            collection_name = f"{collection_prefix}build_results"

            logger.info(f"💾 Storing build result in collection: {collection_name}")

            collection = self.db[collection_name]

            # Check if build already exists
            existing = collection.find_one({'build_id': build_data['build_id']})

            if existing:
                # Update existing build
                collection.update_one(
                    {'build_id': build_data['build_id']},
                    {'$set': build_data}
                )
                logger.info(f"✅ Updated existing build: {build_data['build_id']}")
            else:
                # Insert new build
                collection.insert_one(build_data)
                logger.info(f"✅ Stored new build: {build_data['build_id']}")

            return True

        except Exception as e:
            logger.error(f"❌ Error storing build result: {e}")
            return False

    def trigger_analysis(self, build_id: str, project_id: int, project_slug: str,
                        api_url: str = 'http://localhost:5004/api/trigger-analysis') -> bool:
        """Trigger Python workflow analysis for failed tests"""
        try:
            logger.info(f"🚀 Triggering analysis for build: {build_id}")

            payload = {
                'project_id': project_id,
                'project_slug': project_slug,
                'build_id': build_id,
                'trigger_source': 'robot_framework_parser',
                'triggered_by_user': 'system'
            }

            response = requests.post(api_url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Analysis triggered: {result}")
                return True
            else:
                logger.error(f"❌ Analysis trigger failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Error triggering analysis: {e}")
            return False

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB connection closed")


def main():
    """Main entry point for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Parse Robot Framework test results')
    parser.add_argument('--output', required=True, help='Path to output.xml file')
    parser.add_argument('--build-id', required=True, help='Jenkins build ID')
    parser.add_argument('--project-id', type=int, required=True, help='Project ID (e.g., 2 for Guruttava)')
    parser.add_argument('--project-slug', required=True, help='Project slug (e.g., guruttava)')
    parser.add_argument('--platform', default='Unknown', help='Platform: Android, iOS, or Web')
    parser.add_argument('--test-type', default='Unknown', help='Test type: Smoke, Regression, etc.')
    parser.add_argument('--mongodb-uri', help='MongoDB connection URI')
    parser.add_argument('--api-url', default='http://localhost:5004/api/trigger-analysis',
                       help='Python workflow API URL')
    parser.add_argument('--collection-prefix', default='guruttava_',
                       help='MongoDB collection prefix')

    args = parser.parse_args()

    # Initialize parser
    parser_obj = RobotFrameworkParser(
        mongodb_uri=args.mongodb_uri,
        database_name='ddn_tests'
    )

    try:
        # Parse Robot Framework output
        results = parser_obj.parse_output_xml(
            xml_path=args.output,
            project_id=args.project_id,
            build_id=args.build_id,
            platform=args.platform,
            test_type=args.test_type
        )

        # Project configuration
        project_config = {
            'mongodb_collection_prefix': args.collection_prefix,
            'project_id': args.project_id,
            'project_slug': args.project_slug
        }

        # Store failures in MongoDB
        if results['failures']:
            parser_obj.store_failures_in_mongodb(results['failures'], project_config)

        # Store build result
        build_data = {
            'project_id': args.project_id,
            'build_id': args.build_id,
            'platform': args.platform,
            'test_type': args.test_type,
            'total_tests': results['total_tests'],
            'passed_tests': results['passed_tests'],
            'failed_tests': results['failed_tests'],
            'skipped_tests': results['skipped_tests'],
            'status': 'FAILURE' if results['failed_tests'] > 0 else 'SUCCESS',
            'timestamp': datetime.utcnow(),
            'analyzed': False,
            'metadata': results['metadata']
        }
        parser_obj.store_build_result(build_data, project_config)

        # Trigger analysis if there are failures
        if results['failed_tests'] > 0:
            parser_obj.trigger_analysis(
                build_id=args.build_id,
                project_id=args.project_id,
                project_slug=args.project_slug,
                api_url=args.api_url
            )

        # Close connection
        parser_obj.close()

        print("\n" + "="*70)
        print("✅ Robot Framework Parser Complete")
        print("="*70)
        print(f"Build ID: {args.build_id}")
        print(f"Project: {args.project_slug} (ID: {args.project_id})")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Skipped: {results['skipped_tests']}")
        print("="*70)

        sys.exit(0)

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        parser_obj.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
