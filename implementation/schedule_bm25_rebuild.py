"""
Schedule Weekly BM25 Index Rebuild - Phase 3 (Task 3.9)
Automatically rebuilds BM25 index every week to keep it fresh

This script:
- Runs every Sunday at 2:00 AM
- Rebuilds BM25 index from PostgreSQL
- Logs rebuild status
- Sends notifications on failures

Usage:
  python schedule_bm25_rebuild.py  # Run as service
"""

import schedule
import time
import subprocess
import logging
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Slack notification configuration
SLACK_SERVICE_URL = os.getenv('SLACK_SERVICE_URL', 'http://localhost:5012')
SLACK_ALERTS_ENABLED = os.getenv('SLACK_ALERTS_ENABLED', 'true').lower() == 'true'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bm25_rebuild.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(__file__)
BUILD_SCRIPT = os.path.join(SCRIPT_DIR, 'build_bm25_index.py')


def send_slack_alert(error_message: str, error_type: str = "BM25 Rebuild Failed"):
    """Send alert to Slack when BM25 rebuild fails"""
    if not SLACK_ALERTS_ENABLED:
        logger.info("Slack alerts disabled, skipping notification")
        return

    try:
        payload = {
            'build_id': f'bm25-rebuild-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
            'job_name': 'BM25 Index Rebuild',
            'error_category': 'INFRA_ERROR',
            'root_cause': error_message,
            'fix_recommendation': 'Check PostgreSQL connection and disk space. Review build_bm25_index.py logs for details.',
            'confidence_score': 1.0,
            'consecutive_failures': 1,
            'build_url': ''
        }

        response = requests.post(
            f'{SLACK_SERVICE_URL}/api/slack/send-notification',
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            logger.info(f"Slack alert sent successfully: {error_type}")
        else:
            logger.warning(f"Failed to send Slack alert: {response.status_code} - {response.text}")

    except requests.exceptions.ConnectionError:
        logger.warning("Could not connect to Slack service - notification skipped")
    except Exception as e:
        logger.warning(f"Failed to send Slack notification: {e}")


def rebuild_bm25_index():
    """Rebuild BM25 index"""
    logger.info("=" * 80)
    logger.info("STARTING WEEKLY BM25 INDEX REBUILD")
    logger.info(f"Time: {datetime.now()}")
    logger.info("=" * 80)

    try:
        # Run build script
        result = subprocess.run(
            ['python', BUILD_SCRIPT],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode == 0:
            logger.info("SUCCESS: BM25 index rebuilt successfully")
            logger.info(result.stdout)
        else:
            logger.error("FAILED: BM25 index rebuild failed")
            logger.error(result.stderr)
            send_slack_alert(
                error_message=f"BM25 index rebuild failed.\n\nError output:\n{result.stderr[:500]}",
                error_type="BM25 Rebuild Failed"
            )

    except subprocess.TimeoutExpired:
        logger.error("FAILED: BM25 rebuild timed out after 10 minutes")
        send_slack_alert(
            error_message="BM25 index rebuild timed out after 10 minutes. The process may be stuck or the database may be under heavy load.",
            error_type="BM25 Rebuild Timeout"
        )
    except Exception as e:
        logger.error(f"FAILED: Unexpected error: {e}")
        send_slack_alert(
            error_message=f"Unexpected error during BM25 rebuild: {str(e)}",
            error_type="BM25 Rebuild Error"
        )

    logger.info("=" * 80)

def main():
    """Main scheduler loop"""
    logger.info("BM25 Index Rebuild Scheduler Started")
    logger.info("Schedule: Every Sunday at 2:00 AM")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 80)

    # Schedule weekly rebuild (Sunday at 2:00 AM)
    schedule.every().sunday.at("02:00").do(rebuild_bm25_index)

    # For testing: uncomment to run every minute
    # schedule.every(1).minutes.do(rebuild_bm25_index)

    # Run immediately on startup (optional)
    # rebuild_bm25_index()

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nScheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler crashed: {e}")
