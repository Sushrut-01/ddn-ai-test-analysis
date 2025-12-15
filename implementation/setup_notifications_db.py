"""
Database Setup Script for Notifications Service
Creates notifications and email_queue tables
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', 5432),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password')
}

def setup_notifications_database():
    """Create notifications tables"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        print("Creating notifications tables...")

        # Notifications table (in-app)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                type VARCHAR(50),
                category VARCHAR(50),
                related_resource_type VARCHAR(50),
                related_resource_id VARCHAR(255),
                is_read BOOLEAN DEFAULT false,
                is_archived BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                action_url VARCHAR(500)
            )
        """)
        print("[OK] Created notifications table")

        # Email queue table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_queue (
                id SERIAL PRIMARY KEY,
                to_email VARCHAR(255) NOT NULL,
                subject VARCHAR(500) NOT NULL,
                body_text TEXT,
                body_html TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                attempts INTEGER DEFAULT 0,
                last_error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP
            )
        """)
        print("[OK] Created email_queue table")

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user_email ON notifications(user_email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_category ON notifications(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_queue_status ON email_queue(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_queue_created_at ON email_queue(created_at DESC)")
        print("[OK] Created indexes")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n[SUCCESS] Notifications database setup complete!")
        print("\nTables created:")
        print("  - notifications")
        print("  - email_queue")
        print("\nIndexes created:")
        print("  - idx_notifications_user_email")
        print("  - idx_notifications_is_read")
        print("  - idx_notifications_category")
        print("  - idx_notifications_created_at")
        print("  - idx_email_queue_status")
        print("  - idx_email_queue_created_at")

    except Exception as e:
        print(f"[ERROR] Error setting up notifications database: {str(e)}")
        raise


if __name__ == '__main__':
    setup_notifications_database()
