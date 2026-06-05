"""
Database Setup Script for Authentication Service
Creates users and user_sessions tables
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

def setup_auth_database():
    """Create authentication tables"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        print("Creating authentication tables...")

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                role VARCHAR(50) DEFAULT 'user',
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        print("[OK] Created users table")

        # User sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token VARCHAR(500) NOT NULL,
                refresh_token VARCHAR(500),
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(50),
                user_agent TEXT
            )
        """)
        print("[OK] Created user_sessions table")

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(token)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON user_sessions(expires_at)")
        print("[OK] Created indexes")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n[SUCCESS] Authentication database setup complete!")
        print("\nTables created:")
        print("  - users")
        print("  - user_sessions")
        print("\nIndexes created:")
        print("  - idx_users_email")
        print("  - idx_users_role")
        print("  - idx_sessions_token")
        print("  - idx_sessions_user_id")
        print("  - idx_sessions_expires_at")

    except Exception as e:
        print(f"[ERROR] Error setting up authentication database: {str(e)}")
        raise


if __name__ == '__main__':
    setup_auth_database()
