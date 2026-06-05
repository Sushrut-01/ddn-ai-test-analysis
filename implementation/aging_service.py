"""
DDN Test Failure Aging Service
Automatically triggers analysis for old unanalyzed failures

Task 0F.6: Aging Service with APScheduler
- Checks MongoDB every 6 hours for failures > 3 days old
- Auto-triggers n8n workflow for qualifying failures
- Logs all triggers to PostgreSQL
- Port: 5007
"""

from flask import Flask, jsonify, request
import os
import sys
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import psycopg2
from psycopg2.extras import RealDictCursor
import pymongo
import requests
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
MONGODB_URI = os.getenv('MONGODB_URI')  # Must be set via environment variable
MONGODB_DB = os.getenv('MONGODB_DB', 'ddn_tests')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5434))
POSTGRES_DB = os.getenv('POSTGRES_DB', 'ddn_qa_system')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_AUTO_TRIGGER', 'http://localhost:5678/webhook/ddn-test-failure')
PORT = int(os.getenv('AGING_SERVICE_PORT', 5007))

# Aging criteria (UPDATED - OR logic)
# Auto-trigger AI analysis when EITHER:
# - Aging days > AGING_DAYS_THRESHOLD (failure older than N days), OR
# - Fail count > MIN_FAILURE_COUNT (more than N failures for same build)
AGING_DAYS_THRESHOLD = 3  # Days old (trigger if > 3 days)
MIN_FAILURE_COUNT = 3  # Minimum failures (trigger if > 3 failures)
CHECK_INTERVAL_HOURS = 6

# Initialize connections
mongo_client = None
postgres_conn = None
scheduler = None

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def initialize_mongodb():
    """Initialize MongoDB connection"""
    global mongo_client
    try:
        mongo_client = pymongo.MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        # Test connection
        mongo_client.admin.command('ping')
        logger.info(f"✅ MongoDB connected: {MONGODB_URI}")
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        mongo_client = None
        return False


def initialize_postgres():
    """Initialize PostgreSQL connection and create aging log table"""
    global postgres_conn
    try:
        postgres_conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        logger.info(f"✅ PostgreSQL connected: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

        # Create aging_trigger_log table if not exists
        with postgres_conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aging_trigger_log (
                    id SERIAL PRIMARY KEY,
                    build_id VARCHAR(255) NOT NULL,
                    job_name VARCHAR(500),
                    test_suite VARCHAR(500),
                    consecutive_failures INTEGER,
                    days_old NUMERIC(10,2),
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    trigger_status VARCHAR(50) DEFAULT 'pending',
                    webhook_response TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_aging_build_id ON aging_trigger_log(build_id);
                CREATE INDEX IF NOT EXISTS idx_aging_triggered_at ON aging_trigger_log(triggered_at);
            """)
            postgres_conn.commit()
            logger.info("✅ PostgreSQL aging_trigger_log table ready")

        return True
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        postgres_conn = None
        return False


# ============================================================================
# AGING LOGIC
# ============================================================================

def get_build_level_summary() -> Dict:
    """
    Phase 6: Query build_results collection for build-level metrics.
    Returns failed build count per job (Jenkins pipeline failures vs test failures).

    Returns:
        Dict with job_name -> {total_builds, failed_builds, success_builds, etc.}
    """
    if not mongo_client:
        logger.warning("MongoDB not connected for build_level_summary")
        return {}

    try:
        db = mongo_client[MONGODB_DB]
        build_results = db['build_results']

        # Aggregation to summarize builds by job
        pipeline = [
            # Group by job_name and count build results
            {
                "$group": {
                    "_id": "$job_name",
                    "total_builds": {"$sum": 1},
                    "failed_builds": {
                        "$sum": {
                            "$cond": [{"$eq": ["$build_result", "FAILURE"]}, 1, 0]
                        }
                    },
                    "success_builds": {
                        "$sum": {
                            "$cond": [{"$eq": ["$build_result", "SUCCESS"]}, 1, 0]
                        }
                    },
                    "unstable_builds": {
                        "$sum": {
                            "$cond": [{"$eq": ["$build_result", "UNSTABLE"]}, 1, 0]
                        }
                    },
                    "latest_build": {"$max": "$build_number"},
                    "latest_timestamp": {"$max": "$timestamp"},
                    "total_test_failures": {"$sum": {"$ifNull": ["$test_fail_count", 0]}},
                    "total_test_passes": {"$sum": {"$ifNull": ["$test_pass_count", 0]}}
                }
            },
            # Project clean output
            {
                "$project": {
                    "job_name": "$_id",
                    "total_builds": 1,
                    "failed_builds": 1,
                    "success_builds": 1,
                    "unstable_builds": 1,
                    "latest_build": 1,
                    "latest_timestamp": 1,
                    "total_test_failures": 1,
                    "total_test_passes": 1,
                    "build_success_rate": {
                        "$cond": [
                            {"$eq": ["$total_builds", 0]},
                            0,
                            {"$multiply": [
                                {"$divide": ["$success_builds", "$total_builds"]},
                                100
                            ]}
                        ]
                    }
                }
            }
        ]

        results = list(build_results.aggregate(pipeline))

        # Convert to dict keyed by job_name
        summary = {}
        for r in results:
            job_name = r.get('job_name') or r.get('_id')
            summary[job_name] = {
                'total_builds': r.get('total_builds', 0),
                'failed_builds': r.get('failed_builds', 0),
                'success_builds': r.get('success_builds', 0),
                'unstable_builds': r.get('unstable_builds', 0),
                'latest_build': r.get('latest_build', 0),
                'latest_timestamp': r.get('latest_timestamp'),
                'total_test_failures': r.get('total_test_failures', 0),
                'total_test_passes': r.get('total_test_passes', 0),
                'build_success_rate': round(r.get('build_success_rate', 0), 1)
            }

        logger.info(f"📊 Build-level summary: {len(summary)} jobs")
        for job, data in summary.items():
            logger.info(f"   - {job}: {data['failed_builds']}/{data['total_builds']} failed builds, "
                       f"{data['total_test_failures']} test failures")

        return summary

    except Exception as e:
        logger.error(f"❌ Error getting build-level summary: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {}


def get_aged_failures() -> List[Dict]:
    """
    Query MongoDB for failures meeting aging criteria (OR logic):
    - Aging days > AGING_DAYS_THRESHOLD (failure older than N days), OR
    - Fail count > MIN_FAILURE_COUNT (more than N failures for same build)
    - Not yet analyzed

    Returns:
        List of build summaries that need analysis
        Each summary contains: build_id, job_name, first_failure, last_failure,
                              failure_count, days_span, latest_build_data
    """
    if not mongo_client:
        logger.error("MongoDB not connected")
        return []

    try:
        db = mongo_client[MONGODB_DB]
        # BUG FIX #2: Changed from 'builds' to 'test_failures' (actual collection name)
        builds_collection = db['test_failures']

        # Aggregation pipeline to group builds by build_id and calculate span
        pipeline = [
            # Stage 1: Match only failures that haven't been analyzed
            # BUG FIX #3: Support both "FAILURE" (simulator) and "failed" (Robot Framework) statuses
            # Also filter out documents with null build_id (can't be grouped)
            {
                "$match": {
                    "status": {"$in": ["FAILURE", "failed"]},
                    "analyzed": {"$ne": True},
                    "build_id": {"$ne": None, "$exists": True}
                }
            },

            # Stage 2: Group by build_id and calculate metrics
            # BUG FIX #3: Use $timestamp (always populated) instead of $created_at (often None)
            # BUG FIX #3: Use $sum:1 to count failures (fail_count field is never populated)
            {
                "$group": {
                    "_id": "$build_id",
                    "job_name": {"$first": "$job_name"},
                    "test_suite": {"$first": "$test_suite"},
                    "build_url": {"$first": "$build_url"},
                    "first_failure": {"$min": "$timestamp"},
                    "last_failure": {"$max": "$timestamp"},
                    "failure_count": {"$sum": 1},  # Count failures (fail_count field is never populated)
                    "latest_build": {"$last": "$$ROOT"}  # Keep latest build document
                }
            },

            # Stage 3: Calculate days span and prepare output
            {
                "$project": {
                    "build_id": "$_id",
                    "job_name": 1,
                    "test_suite": 1,
                    "build_url": 1,
                    "first_failure": 1,
                    "last_failure": 1,
                    "failure_count": 1,
                    "latest_build": 1,
                    "days_span": {
                        "$divide": [
                            {"$subtract": ["$last_failure", "$first_failure"]},
                            86400000  # milliseconds per day
                        ]
                    }
                }
            },

            # Stage 4: Filter by aging criteria (OR logic)
            # Trigger if: days_span > 3 OR failure_count > 3
            {
                "$match": {
                    "$or": [
                        {"days_span": {"$gt": AGING_DAYS_THRESHOLD}},
                        {"failure_count": {"$gt": MIN_FAILURE_COUNT}}
                    ]
                }
            },

            # Stage 5: Sort by days_span (oldest first)
            {
                "$sort": {"days_span": -1}
            },

            # Stage 6: Limit results
            {
                "$limit": 100
            }
        ]

        # Execute aggregation
        aged_builds = list(builds_collection.aggregate(pipeline))

        logger.info(f"📊 Found {len(aged_builds)} aged failure patterns:")
        for build in aged_builds:
            failure_count = build.get('failure_count') or 0
            days_span = build.get('days_span') or 0
            logger.info(f"   - {build['build_id']}: {failure_count} failures over {days_span:.1f} days")

        return aged_builds

    except Exception as e:
        logger.error(f"❌ Error querying aged failures: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []


def trigger_n8n_analysis(build_summary: Dict) -> Dict:
    """
    Trigger n8n auto-trigger workflow for a build

    Args:
        build_summary: Aggregated build summary from get_aged_failures()
                      Contains: build_id, job_name, first_failure, last_failure,
                               failure_count, days_span, latest_build

    Returns:
        Dict with status and response
    """
    try:
        # Extract data from summary
        build_id = build_summary.get('build_id')
        latest = build_summary.get('latest_build') or {}

        # BUG FIX #3: Handle None values properly (use 'or' not default in .get())
        # .get(key, default) returns None if key exists with None value, not default
        last_failure = build_summary.get('last_failure') or datetime.now()
        first_failure = build_summary.get('first_failure') or datetime.now()
        days_span = build_summary.get('days_span') or 0
        failure_count = build_summary.get('failure_count') or 0

        # Prepare payload for n8n webhook
        payload = {
            'build_id': build_id,
            'build_url': build_summary.get('build_url') or latest.get('build_url') or '',
            'job_name': build_summary.get('job_name') or '',
            'test_suite': build_summary.get('test_suite') or '',
            'status': 'FAILURE',
            'timestamp': last_failure.isoformat(),
            'trigger_source': 'aging_service',
            'aging_metadata': {
                'days_span': round(days_span, 2),
                'failure_count': failure_count,
                'first_failure': first_failure.isoformat(),
                'last_failure': last_failure.isoformat()
            }
        }

        logger.info(
            f"🚀 Triggering n8n for build {build_id}: "
            f"{payload['aging_metadata']['failure_count']} failures over "
            f"{payload['aging_metadata']['days_span']} days"
        )

        # Call n8n webhook
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            logger.info(f"✅ Successfully triggered analysis for {build_id}")
            return {
                'status': 'success',
                'response': response.json() if response.text else {},
                'status_code': response.status_code
            }
        else:
            logger.warning(f"⚠️  n8n returned non-200 status: {response.status_code}")
            return {
                'status': 'failed',
                'error': f"HTTP {response.status_code}",
                'response': response.text[:500]
            }

    except requests.exceptions.Timeout:
        logger.error(f"❌ Timeout triggering n8n for {build_summary.get('build_id')}")
        return {
            'status': 'timeout',
            'error': 'Request timeout after 30s'
        }
    except Exception as e:
        logger.error(f"❌ Error triggering n8n: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


def log_trigger_to_postgres(build_summary: Dict, trigger_result: Dict):
    """
    Log trigger attempt to PostgreSQL aging_trigger_log table

    Args:
        build_summary: Aggregated build summary from get_aged_failures()
        trigger_result: Result from trigger_n8n_analysis
    """
    if not postgres_conn:
        logger.warning("PostgreSQL not connected, skipping log")
        return

    try:
        with postgres_conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO aging_trigger_log
                (build_id, job_name, test_suite, consecutive_failures, days_old,
                 trigger_status, webhook_response, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                build_summary.get('build_id'),
                build_summary.get('job_name'),
                build_summary.get('test_suite'),
                # BUG FIX #3: Handle None values properly (use 'or' not default in .get())
                build_summary.get('failure_count') or 0,
                round(build_summary.get('days_span') or 0, 2),
                trigger_result.get('status') or 'unknown',
                str(trigger_result.get('response') or '')[:1000],
                (trigger_result.get('error') or '')[:500] if 'error' in trigger_result else None
            ))
            postgres_conn.commit()
            logger.debug(f"📝 Logged trigger for {build_summary.get('build_id')} to PostgreSQL")

    except Exception as e:
        logger.error(f"❌ Error logging to PostgreSQL: {e}")
        try:
            postgres_conn.rollback()
        except:
            pass


def process_aged_failures():
    """
    Main aging process:
    1. Query MongoDB for aged failures
    2. Trigger n8n workflow for each
    3. Log results to PostgreSQL

    This function is called by APScheduler every CHECK_INTERVAL_HOURS hours
    """
    logger.info("=" * 80)
    logger.info("🕐 AGING SERVICE CHECK STARTED")
    logger.info(f"   Criteria: days > {AGING_DAYS_THRESHOLD} OR failures > {MIN_FAILURE_COUNT}, not analyzed")
    logger.info("=" * 80)

    # Get aged failures
    aged_builds = get_aged_failures()

    if not aged_builds:
        logger.info("✅ No aged failures found - all clear!")
        return

    # Process each aged build pattern
    success_count = 0
    failure_count = 0

    for build_summary in aged_builds:
        build_id = build_summary.get('build_id')

        # Trigger n8n analysis
        result = trigger_n8n_analysis(build_summary)

        # Log to PostgreSQL
        log_trigger_to_postgres(build_summary, result)

        # Track stats
        if result['status'] == 'success':
            success_count += 1
        else:
            failure_count += 1

        # Mark ALL occurrences of this build_id as analyzed in MongoDB
        # This prevents re-triggering the same build pattern
        # BUG FIX #2: Changed from 'builds' to 'test_failures' and status from 'FAILURE' to 'failed'
        try:
            if mongo_client:
                db = mongo_client[MONGODB_DB]
                update_result = db['test_failures'].update_many(
                    {'build_id': build_id, 'status': 'failed'},
                    {'$set': {
                        'analyzed': True,
                        'analyzed_at': datetime.now(),
                        'analyzed_by': 'aging_service'
                    }}
                )
                logger.debug(f"📝 Marked {update_result.modified_count} builds as analyzed for {build_id}")
        except Exception as e:
            logger.error(f"❌ Error marking builds as analyzed: {e}")

    # Summary
    logger.info("=" * 80)
    logger.info("🏁 AGING SERVICE CHECK COMPLETE")
    logger.info(f"   Processed: {len(aged_builds)} builds")
    logger.info(f"   ✅ Success: {success_count}")
    logger.info(f"   ❌ Failed: {failure_count}")
    logger.info("=" * 80)


# ============================================================================
# SCHEDULER MANAGEMENT
# ============================================================================

def initialize_scheduler():
    """Initialize APScheduler with cron job"""
    global scheduler

    try:
        scheduler = BackgroundScheduler(
            daemon=True,
            timezone='UTC'
        )

        # Add job to run every CHECK_INTERVAL_HOURS hours
        # Runs at minute 0 (top of the hour) every N hours
        scheduler.add_job(
            func=process_aged_failures,
            trigger=CronTrigger(hour=f'*/{CHECK_INTERVAL_HOURS}', minute=0),
            id='aging_check',
            name='Check for Aged Failures',
            replace_existing=True,
            misfire_grace_time=300  # 5 minutes grace period
        )

        scheduler.start()

        # Get next run time
        job = scheduler.get_job('aging_check')
        next_run = job.next_run_time if job else None

        logger.info(f"✅ Scheduler initialized: Every {CHECK_INTERVAL_HOURS} hours")
        logger.info(f"   Next run: {next_run.isoformat() if next_run else 'Unknown'}")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to initialize scheduler: {e}")
        return False


# ============================================================================
# FLASK API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    mongodb_status = 'connected' if mongo_client else 'disconnected'
    postgres_status = 'connected' if postgres_conn else 'disconnected'
    scheduler_status = 'running' if scheduler and scheduler.running else 'stopped'

    # Get next scheduled run
    next_run = None
    if scheduler:
        job = scheduler.get_job('aging_check')
        if job:
            next_run = job.next_run_time.isoformat()

    return jsonify({
        'status': 'healthy',
        'service': 'aging_service',
        'port': PORT,
        'mongodb': mongodb_status,
        'postgresql': postgres_status,
        'scheduler': scheduler_status,
        'next_run': next_run,
        'config': {
            'aging_threshold_days': AGING_DAYS_THRESHOLD,
            'min_failure_count': MIN_FAILURE_COUNT,
            'check_interval_hours': CHECK_INTERVAL_HOURS,
            'n8n_webhook': N8N_WEBHOOK_URL
        }
    }), 200


@app.route('/trigger-now', methods=['POST'])
def trigger_now():
    """
    Manual trigger endpoint for testing
    Runs the aging check immediately (bypasses scheduler)
    """
    logger.info("📥 Manual aging check triggered via API")

    try:
        process_aged_failures()
        return jsonify({
            'status': 'success',
            'message': 'Aging check completed',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"❌ Manual trigger failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get aging service statistics with dual metrics (test failures + build failures)"""
    try:
        # Get aged builds count (test-level)
        aged_count = len(get_aged_failures())

        # Phase 6: Get build-level summary
        build_summary = get_build_level_summary()

        # Calculate totals from build summary
        total_failed_builds = sum(j.get('failed_builds', 0) for j in build_summary.values())
        total_test_failures = sum(j.get('total_test_failures', 0) for j in build_summary.values())
        total_builds = sum(j.get('total_builds', 0) for j in build_summary.values())

        # Get PostgreSQL trigger log stats
        pg_stats = {}
        if postgres_conn:
            with postgres_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Total triggers
                cursor.execute("SELECT COUNT(*) as total FROM aging_trigger_log")
                pg_stats['total_triggers'] = cursor.fetchone()['total']

                # Success/failure breakdown
                cursor.execute("""
                    SELECT trigger_status, COUNT(*) as count
                    FROM aging_trigger_log
                    GROUP BY trigger_status
                """)
                pg_stats['by_status'] = {row['trigger_status']: row['count'] for row in cursor.fetchall()}

                # Recent triggers (last 24 hours)
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM aging_trigger_log
                    WHERE triggered_at > NOW() - INTERVAL '24 hours'
                """)
                pg_stats['last_24h'] = cursor.fetchone()['count']

        return jsonify({
            'aged_failures_pending': aged_count,
            # Phase 6: Dual metrics
            'dual_metrics': {
                'failed_test_count': total_test_failures,
                'failed_build_count': total_failed_builds,
                'total_builds': total_builds,
                'jobs_tracked': len(build_summary)
            },
            'build_summary_by_job': build_summary,
            'trigger_log': pg_stats,
            'criteria': {
                'aging_threshold_days': AGING_DAYS_THRESHOLD,
                'min_failure_count': MIN_FAILURE_COUNT
            }
        }), 200

    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/builds/summary', methods=['GET'])
def get_builds_summary():
    """
    Phase 6: New endpoint for build-level metrics.
    Returns dual metrics: failed_test_count AND failed_build_count per job.
    """
    try:
        build_summary = get_build_level_summary()

        # Calculate totals
        total_failed_builds = sum(j.get('failed_builds', 0) for j in build_summary.values())
        total_success_builds = sum(j.get('success_builds', 0) for j in build_summary.values())
        total_test_failures = sum(j.get('total_test_failures', 0) for j in build_summary.values())
        total_test_passes = sum(j.get('total_test_passes', 0) for j in build_summary.values())
        total_builds = sum(j.get('total_builds', 0) for j in build_summary.values())

        return jsonify({
            'totals': {
                'failed_build_count': total_failed_builds,
                'success_build_count': total_success_builds,
                'total_builds': total_builds,
                'failed_test_count': total_test_failures,
                'passed_test_count': total_test_passes,
                'build_success_rate': round((total_success_builds / total_builds * 100) if total_builds > 0 else 0, 1)
            },
            'by_job': build_summary,
            'generated_at': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"❌ Error getting builds summary: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/recent-triggers', methods=['GET'])
def get_recent_triggers():
    """Get recent trigger log entries"""
    limit = request.args.get('limit', 50, type=int)

    if not postgres_conn:
        return jsonify({'error': 'PostgreSQL not connected'}), 503

    try:
        with postgres_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT build_id, job_name, consecutive_failures, days_old,
                       trigger_status, triggered_at, error_message
                FROM aging_trigger_log
                ORDER BY triggered_at DESC
                LIMIT %s
            """, (limit,))

            results = cursor.fetchall()

            # Convert datetime to ISO format
            for row in results:
                if 'triggered_at' in row and row['triggered_at']:
                    row['triggered_at'] = row['triggered_at'].isoformat()

            return jsonify({
                'triggers': results,
                'count': len(results)
            }), 200

    except Exception as e:
        logger.error(f"❌ Error getting recent triggers: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Initialize and start the aging service"""
    logger.info("=" * 80)
    logger.info("🚀 DDN AGING SERVICE STARTING")
    logger.info(f"   Port: {PORT}")
    logger.info(f"   Check Interval: Every {CHECK_INTERVAL_HOURS} hours")
    logger.info(f"   Criteria: days > {AGING_DAYS_THRESHOLD} OR failures > {MIN_FAILURE_COUNT}")
    logger.info("=" * 80)

    # Initialize connections
    mongodb_ok = initialize_mongodb()
    postgres_ok = initialize_postgres()

    if not mongodb_ok:
        logger.error("❌ MongoDB connection required - exiting")
        sys.exit(1)

    if not postgres_ok:
        logger.warning("⚠️  PostgreSQL not available - trigger logging disabled")

    # Initialize scheduler
    scheduler_ok = initialize_scheduler()

    if not scheduler_ok:
        logger.error("❌ Scheduler initialization failed - exiting")
        sys.exit(1)

    logger.info("✅ All systems initialized")
    logger.info(f"🌐 Starting Flask server on port {PORT}...")

    # Start Flask app
    try:
        app.run(
            host='0.0.0.0',
            port=PORT,
            debug=False,
            use_reloader=False  # Important: Prevents duplicate scheduler
        )
    except KeyboardInterrupt:
        logger.info("\n👋 Aging service shutting down...")
        if scheduler:
            scheduler.shutdown()
    except Exception as e:
        logger.error(f"❌ Flask server error: {e}")
        if scheduler:
            scheduler.shutdown()
        sys.exit(1)


if __name__ == '__main__':
    main()
