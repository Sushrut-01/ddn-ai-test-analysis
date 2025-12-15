"""
Database Setup Script for Configuration Management
Creates system_config table for application settings
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

def setup_config_database():
    """Create system configuration tables"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        print("Creating configuration tables...")

        # System configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id SERIAL PRIMARY KEY,
                config_key VARCHAR(255) UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                value_type VARCHAR(50) NOT NULL,
                category VARCHAR(50) NOT NULL,
                description TEXT,
                is_sensitive BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by VARCHAR(255)
            )
        """)
        print("[OK] Created system_config table")

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_config_key ON system_config(config_key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_config_category ON system_config(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_config_updated_at ON system_config(updated_at DESC)")
        print("[OK] Created indexes")

        # Insert default configuration values
        default_configs = [
            # AI Settings
            ('ai.model.primary', 'gemini-1.5-flash', 'string', 'ai', 'Primary AI model for analysis', False),
            ('ai.model.fallback', 'gpt-4o-mini', 'string', 'ai', 'Fallback AI model if primary fails', False),
            ('ai.confidence_threshold', '0.7', 'float', 'ai', 'Minimum confidence score for auto-approval', False),
            ('ai.analysis_timeout', '120', 'integer', 'ai', 'Maximum seconds for AI analysis', False),
            ('ai.max_retries', '3', 'integer', 'ai', 'Maximum retry attempts for failed analysis', False),

            # Notification Settings
            ('notifications.email.enabled', 'true', 'boolean', 'notifications', 'Enable email notifications', False),
            ('notifications.slack.enabled', 'false', 'boolean', 'notifications', 'Enable Slack notifications', False),
            ('notifications.in_app.enabled', 'true', 'boolean', 'notifications', 'Enable in-app notifications', False),
            ('notifications.frequency', 'immediate', 'string', 'notifications', 'Notification frequency (immediate/hourly/daily)', False),
            ('notifications.team_emails', 'sushrut.nistane@rysun.com,amit.manjesh@rysun.com', 'string', 'notifications', 'Team email addresses (comma-separated)', False),

            # Integration Settings
            ('integrations.jira.auto_create', 'true', 'boolean', 'integrations', 'Auto-create Jira tickets for failures', False),
            ('integrations.jira.priority_threshold', 'high', 'string', 'integrations', 'Minimum priority for Jira ticket creation', False),
            ('integrations.github.auto_pr', 'false', 'boolean', 'integrations', 'Auto-create GitHub PRs for fixes', False),
            ('integrations.jenkins.auto_trigger', 'true', 'boolean', 'integrations', 'Auto-trigger Jenkins builds after fixes', False),

            # System Settings
            ('system.auto_approval.enabled', 'true', 'boolean', 'system', 'Enable auto-approval for high-confidence analyses', False),
            ('system.auto_approval.threshold', '0.85', 'float', 'system', 'Confidence threshold for auto-approval', False),
            ('system.aging.check_interval', '24', 'integer', 'system', 'Hours between aging service checks', False),
            ('system.aging.stale_days', '7', 'integer', 'system', 'Days before marking failure as stale', False),
            ('system.cache.ttl', '3600', 'integer', 'system', 'Cache time-to-live in seconds', False),
            ('system.max_parallel_analyses', '5', 'integer', 'system', 'Maximum parallel AI analyses', False),

            # Dashboard Settings
            ('dashboard.refresh_interval', '30', 'integer', 'dashboard', 'Dashboard auto-refresh interval in seconds', False),
            ('dashboard.items_per_page', '20', 'integer', 'dashboard', 'Default items per page in lists', False),
            ('dashboard.theme', 'light', 'string', 'dashboard', 'Default dashboard theme (light/dark)', False)
        ]

        for key, value, value_type, category, description, is_sensitive in default_configs:
            cursor.execute("""
                INSERT INTO system_config (config_key, config_value, value_type, category, description, is_sensitive)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (config_key) DO NOTHING
            """, (key, value, value_type, category, description, is_sensitive))

        conn.commit()
        cursor.close()
        conn.close()

        print("\n[SUCCESS] Configuration database setup complete!")
        print("\nTable created:")
        print("  - system_config")
        print("\nIndexes created:")
        print("  - idx_config_key")
        print("  - idx_config_category")
        print("  - idx_config_updated_at")
        print("\nDefault configurations inserted:")
        print(f"  - {len(default_configs)} configuration entries")

    except Exception as e:
        print(f"[ERROR] Error setting up configuration database: {str(e)}")
        raise


if __name__ == '__main__':
    setup_config_database()
