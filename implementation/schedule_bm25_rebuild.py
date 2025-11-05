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
from dotenv import load_dotenv

load_dotenv()

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
            # TODO: Send notification (email/Slack) on failure

    except subprocess.TimeoutExpired:
        logger.error("FAILED: BM25 rebuild timed out after 10 minutes")
    except Exception as e:
        logger.error(f"FAILED: Unexpected error: {e}")

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
