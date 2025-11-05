"""
Create PostgreSQL Database Schema for DDN AI Test Failure Analysis
Creates all necessary tables for storing AI analysis results
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables from master config
load_dotenv('../.env.MASTER')

# PostgreSQL configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', 5432)
POSTGRES_DB = os.getenv('POSTGRES_DB', 'ddn_ai_analysis')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')

print("=" * 80)
print("PostgreSQL Database Setup for DDN AI Analysis")
print("=" * 80)
print(f"Host: {POSTGRES_HOST}")
print(f"Port: {POSTGRES_PORT}")
print(f"Database: {POSTGRES_DB}")
print(f"User: {POSTGRES_USER}")
print("=" * 80)
print()

try:
    # Step 1: Connect to PostgreSQL server (not specific database)
    print("Step 1: Connecting to PostgreSQL server...")
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database='postgres'  # Connect to default database first
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    print("[OK] Connected to PostgreSQL server")
    print()

    # Step 2: Create database if it doesn't exist
    print(f"Step 2: Creating database '{POSTGRES_DB}'...")
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{POSTGRES_DB}'")
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(f'CREATE DATABASE {POSTGRES_DB}')
        print(f"[OK] Database '{POSTGRES_DB}' created successfully")
    else:
        print(f"[INFO]  Database '{POSTGRES_DB}' already exists")

    cursor.close()
    conn.close()
    print()

    # Step 3: Connect to the new database
    print(f"Step 3: Connecting to database '{POSTGRES_DB}'...")
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB
    )
    cursor = conn.cursor()
    print(f"[OK] Connected to '{POSTGRES_DB}' database")
    print()

    # Step 4: Create tables
    print("Step 4: Creating database tables...")
    print()

    # Table 1: failure_analysis
    print("Creating table: failure_analysis...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS failure_analysis (
            id SERIAL PRIMARY KEY,
            build_id VARCHAR(255) NOT NULL,
            error_category VARCHAR(100),
            root_cause TEXT,
            fix_recommendation TEXT,
            confidence_score FLOAT,
            consecutive_failures INTEGER DEFAULT 1,
            feedback_result VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] Table 'failure_analysis' created")

    # Table 2: build_metadata
    print("Creating table: build_metadata...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS build_metadata (
            id SERIAL PRIMARY KEY,
            build_id VARCHAR(255) UNIQUE NOT NULL,
            job_name VARCHAR(255),
            test_suite VARCHAR(255),
            build_url TEXT,
            jenkins_url TEXT,
            test_status VARCHAR(50),
            git_commit VARCHAR(255),
            git_branch VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] Table 'build_metadata' created")

    # Table 3: user_feedback
    print("Creating table: user_feedback...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            id SERIAL PRIMARY KEY,
            analysis_id INTEGER REFERENCES failure_analysis(id),
            feedback_type VARCHAR(50),
            feedback_text TEXT,
            rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] Table 'user_feedback' created")

    # Table 4: failure_patterns
    print("Creating table: failure_patterns...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS failure_patterns (
            id SERIAL PRIMARY KEY,
            pattern_type VARCHAR(100),
            pattern_description TEXT,
            occurrence_count INTEGER DEFAULT 1,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            suggested_fix TEXT,
            success_rate FLOAT
        )
    """)
    print("[OK] Table 'failure_patterns' created")

    # Table 5: ai_model_metrics
    print("Creating table: ai_model_metrics...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_model_metrics (
            id SERIAL PRIMARY KEY,
            date DATE DEFAULT CURRENT_DATE,
            total_analyses INTEGER DEFAULT 0,
            avg_confidence FLOAT,
            success_rate FLOAT,
            false_positive_rate FLOAT,
            avg_response_time_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] Table 'ai_model_metrics' created")

    # Table 6: manual_trigger_log
    print("Creating table: manual_trigger_log...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manual_trigger_log (
            id SERIAL PRIMARY KEY,
            build_id VARCHAR(255),
            triggered_by VARCHAR(255),
            trigger_source VARCHAR(100),
            status VARCHAR(50),
            triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)
    print("[OK] Table 'manual_trigger_log' created")

    print()
    print("Step 5: Creating indexes for performance...")

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_build_id ON failure_analysis(build_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON failure_analysis(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_category ON failure_analysis(error_category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_build_metadata_build_id ON build_metadata(build_id)")

    print("[OK] Indexes created")
    print()

    # Commit changes
    conn.commit()
    cursor.close()
    conn.close()

    print("=" * 80)
    print("[OK] DATABASE SETUP COMPLETE!")
    print("=" * 80)
    print()
    print("Created tables:")
    print("  1. failure_analysis      - Stores AI analysis results")
    print("  2. build_metadata        - Stores Jenkins build information")
    print("  3. user_feedback         - Stores user feedback on AI recommendations")
    print("  4. failure_patterns      - Stores identified failure patterns")
    print("  5. ai_model_metrics      - Stores AI model performance metrics")
    print("  6. manual_trigger_log    - Stores manual trigger history")
    print()
    print("Next step: Run the AI analysis service!")
    print("=" * 80)

except psycopg2.OperationalError as e:
    print()
    print("=" * 80)
    print("[ERROR] ERROR: Could not connect to PostgreSQL")
    print("=" * 80)
    print()
    print("Error details:", str(e))
    print()
    print("Please check:")
    print("  1. PostgreSQL is installed and running")
    print("  2. PostgreSQL service is started")
    print("  3. Credentials in .env file are correct:")
    print(f"     - Host: {POSTGRES_HOST}")
    print(f"     - Port: {POSTGRES_PORT}")
    print(f"     - User: {POSTGRES_USER}")
    print(f"     - Password: {'*' * len(POSTGRES_PASSWORD)}")
    print()
    print("To start PostgreSQL:")
    print("  Windows: services.msc -> PostgreSQL service -> Start")
    print("=" * 80)
    exit(1)

except Exception as e:
    print()
    print("=" * 80)
    print("[ERROR] ERROR: Database setup failed")
    print("=" * 80)
    print()
    print("Error details:", str(e))
    print()
    exit(1)
