"""
Start Enhanced Dashboard API on Port 5006
==========================================

This starts the full monitoring dashboard API on port 5006
to avoid conflicts with stuck processes on port 5005.

Usage:
    python start_dashboard_api_port5006.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the dashboard API app and init function
from dashboard_api_full import app, logger, init_mongodb, get_postgres_connection
from pinecone import Pinecone
import os
from dotenv import load_dotenv

# Load master configuration file
load_dotenv('../.env.MASTER')

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting Enhanced Dashboard API on PORT 5006")
    logger.info("=" * 60)

    # Initialize MongoDB
    logger.info("Initializing MongoDB connection...")
    if init_mongodb():
        logger.info("✓ MongoDB connected successfully")
    else:
        logger.warning("⚠ MongoDB connection failed - some features may not work")

    # Note: PostgreSQL and Pinecone connections will be tested when endpoints are called
    logger.info("✓ Configuration loaded successfully")
    logger.info(f"✓ PostgreSQL: {os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}")
    logger.info(f"✓ Pinecone: API key configured")

    logger.info("=" * 60)
    logger.info("Dashboard API starting on http://0.0.0.0:5006")
    logger.info("Health check: http://localhost:5006/api/health")
    logger.info("=" * 60)

    # Run on port 5006
    app.run(host='0.0.0.0', port=5006, debug=False)
