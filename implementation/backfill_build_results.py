#!/usr/bin/env python3
"""
Backfill Build Results from Jenkins to MongoDB

This script syncs all historical Jenkins build data to the `build_results` MongoDB collection.
It captures BUILD-level data (not test-level) including:
- Build result (SUCCESS/FAILURE/UNSTABLE)
- Build duration
- Build trigger type
- Test pass/fail counts

Run this once to backfill historical data, then use the Robot Framework listener
to capture new builds going forward.

Usage:
    python backfill_build_results.py
"""

import os
import sys
import requests
from datetime import datetime
from urllib.parse import quote_plus
import pymongo
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Jenkins Configuration
JENKINS_URL = os.getenv('JENKINS_URL', 'http://localhost:8081')
JENKINS_USER = os.getenv('JENKINS_USER', 'admin')
JENKINS_PASSWORD = os.getenv('JENKINS_PASSWORD', 'admin123')

# MongoDB Configuration
MONGODB_USERNAME = quote_plus(os.getenv('MONGODB_USERNAME', 'sushrutnistane097_db_user'))
MONGODB_PASSWORD = quote_plus(os.getenv('MONGODB_PASSWORD', 'Sharu@051220'))
MONGODB_URI = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true&w=majority"

# Jobs to backfill
JOBS_TO_BACKFILL = [
    "DDN-Basic-Tests",
    "DDN-Advanced-Tests",
    "DDN-Nightly-Tests",
    "DDN-Tests"
]


def get_jenkins_auth():
    """Return authentication tuple for Jenkins API requests"""
    return (JENKINS_USER, JENKINS_PASSWORD)


def get_jenkins_jobs():
    """Get list of all Jenkins jobs"""
    try:
        response = requests.get(
            f"{JENKINS_URL}/api/json",
            auth=get_jenkins_auth(),
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return [job['name'] for job in data.get('jobs', [])]
    except Exception as e:
        logger.error(f"Failed to get Jenkins jobs: {e}")
        return []


def get_job_builds(job_name: str) -> list:
    """Get all builds for a job"""
    try:
        response = requests.get(
            f"{JENKINS_URL}/job/{job_name}/api/json",
            auth=get_jenkins_auth(),
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get('builds', [])
    except Exception as e:
        logger.error(f"Failed to get builds for {job_name}: {e}")
        return []


def get_build_details(job_name: str, build_number: int) -> dict:
    """Get detailed information for a specific build"""
    try:
        response = requests.get(
            f"{JENKINS_URL}/job/{job_name}/{build_number}/api/json",
            auth=get_jenkins_auth(),
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get build details for {job_name}#{build_number}: {e}")
        return {}


def extract_build_trigger(build_data: dict) -> str:
    """Extract the trigger type from build actions"""
    actions = build_data.get('actions', [])
    for action in actions:
        if action.get('_class') == 'hudson.model.CauseAction':
            causes = action.get('causes', [])
            for cause in causes:
                cause_class = cause.get('_class', '')
                if 'TimerTrigger' in cause_class:
                    return 'TimerTrigger'
                elif 'UserIdCause' in cause_class:
                    return 'UserTrigger'
                elif 'RemoteCause' in cause_class:
                    return 'RemoteTrigger'
                elif 'SCMTrigger' in cause_class:
                    return 'SCMTrigger'
                elif 'UpstreamCause' in cause_class:
                    return 'UpstreamTrigger'
                else:
                    return cause.get('shortDescription', 'Unknown')
    return 'Unknown'


def extract_test_counts_from_artifacts(job_name: str, build_number: int) -> dict:
    """
    Try to extract test counts from Robot Framework artifacts.
    This is a fallback if not available in MongoDB.
    """
    # Default counts
    return {
        'test_pass_count': None,
        'test_fail_count': None,
        'test_total_count': None
    }


def get_test_counts_from_mongodb(db, job_name: str, build_number: int) -> dict:
    """Get test pass/fail counts from existing test_failures collection"""
    build_id = f"{job_name}-{build_number}"

    # Count documents in test_failures for this build
    pipeline = [
        {'$match': {'build_id': build_id}},
        {'$group': {
            '_id': None,
            'fail_count': {'$sum': 1},
            'total_from_doc': {'$first': '$total_count'},
            'pass_from_doc': {'$first': '$pass_count'},
            'fail_from_doc': {'$first': '$fail_count'}
        }}
    ]

    result = list(db.test_failures.aggregate(pipeline))

    if result:
        r = result[0]
        # Prefer the counts stored in documents if available
        return {
            'test_pass_count': r.get('pass_from_doc') or 0,
            'test_fail_count': r.get('fail_from_doc') or r.get('fail_count', 0),
            'test_total_count': r.get('total_from_doc') or r.get('fail_count', 0)
        }

    return {
        'test_pass_count': 0,
        'test_fail_count': 0,
        'test_total_count': 0
    }


def backfill_job(db, job_name: str) -> int:
    """Backfill all builds for a single job"""
    builds = get_job_builds(job_name)

    if not builds:
        logger.warning(f"No builds found for {job_name}")
        return 0

    logger.info(f"Backfilling {len(builds)} builds for {job_name}")

    success_count = 0

    for build in builds:
        build_number = build['number']
        build_url = build['url']

        # Get detailed build info
        build_data = get_build_details(job_name, build_number)

        if not build_data:
            continue

        # Extract build result
        build_result = build_data.get('result', 'UNKNOWN')
        if build_result is None:
            build_result = 'IN_PROGRESS'  # Build still running

        # Extract trigger type
        build_trigger = extract_build_trigger(build_data)

        # Get test counts from MongoDB
        test_counts = get_test_counts_from_mongodb(db, job_name, build_number)

        # Build timestamp
        timestamp_ms = build_data.get('timestamp', 0)
        timestamp = datetime.fromtimestamp(timestamp_ms / 1000) if timestamp_ms else datetime.now()

        # Create build result document
        build_doc = {
            'job_name': job_name,
            'build_number': build_number,
            'build_id': f"{job_name}-{build_number}",
            'build_result': build_result,
            'build_duration_ms': build_data.get('duration', 0),
            'build_trigger': build_trigger,
            'build_url': build_url,
            'timestamp': timestamp,
            'test_pass_count': test_counts['test_pass_count'],
            'test_fail_count': test_counts['test_fail_count'],
            'test_total_count': test_counts['test_total_count'],
            'analyzed': False,
            'analyzed_at': None,
            'analysis_id': None,
            'backfilled': True,
            'backfill_timestamp': datetime.now()
        }

        # Upsert to avoid duplicates
        try:
            db.build_results.update_one(
                {'build_id': build_doc['build_id']},
                {'$set': build_doc},
                upsert=True
            )
            success_count += 1
            logger.debug(f"  Backfilled {job_name}#{build_number}: {build_result}")
        except Exception as e:
            logger.error(f"  Failed to insert {job_name}#{build_number}: {e}")

    logger.info(f"Successfully backfilled {success_count}/{len(builds)} builds for {job_name}")
    return success_count


def create_indexes(db):
    """Create indexes on build_results collection for efficient queries"""
    logger.info("Creating indexes on build_results collection...")

    # Index on build_id (unique)
    db.build_results.create_index('build_id', unique=True)

    # Index on job_name for filtering
    db.build_results.create_index('job_name')

    # Index on build_result for filtering
    db.build_results.create_index('build_result')

    # Index on timestamp for sorting
    db.build_results.create_index('timestamp')

    # Compound index for job + build number
    db.build_results.create_index([('job_name', 1), ('build_number', -1)])

    # Index on analyzed status for aging service queries
    db.build_results.create_index('analyzed')

    logger.info("Indexes created successfully")


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Jenkins Build Results Backfill Script")
    logger.info("=" * 60)

    # Connect to MongoDB
    logger.info(f"Connecting to MongoDB...")
    try:
        client = pymongo.MongoClient(MONGODB_URI)
        db = client['ddn_tests']

        # Test connection
        db.command('ping')
        logger.info("MongoDB connection successful")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

    # Create indexes
    create_indexes(db)

    # Get available Jenkins jobs
    logger.info(f"Jenkins URL: {JENKINS_URL}")
    available_jobs = get_jenkins_jobs()
    logger.info(f"Available Jenkins jobs: {available_jobs}")

    # Filter to only jobs we want to backfill
    jobs_to_process = [j for j in JOBS_TO_BACKFILL if j in available_jobs]

    if not jobs_to_process:
        logger.warning("No matching jobs found to backfill")
        logger.info(f"Looking for: {JOBS_TO_BACKFILL}")
        logger.info(f"Available: {available_jobs}")
        sys.exit(1)

    logger.info(f"Jobs to backfill: {jobs_to_process}")

    # Backfill each job
    total_backfilled = 0
    for job_name in jobs_to_process:
        count = backfill_job(db, job_name)
        total_backfilled += count

    # Summary
    logger.info("=" * 60)
    logger.info(f"Backfill Complete!")
    logger.info(f"Total builds backfilled: {total_backfilled}")

    # Show collection stats
    total_docs = db.build_results.count_documents({})
    success_count = db.build_results.count_documents({'build_result': 'SUCCESS'})
    failure_count = db.build_results.count_documents({'build_result': 'FAILURE'})

    logger.info(f"Collection stats:")
    logger.info(f"  Total documents: {total_docs}")
    logger.info(f"  SUCCESS builds: {success_count}")
    logger.info(f"  FAILURE builds: {failure_count}")
    logger.info("=" * 60)

    client.close()


if __name__ == '__main__':
    main()
