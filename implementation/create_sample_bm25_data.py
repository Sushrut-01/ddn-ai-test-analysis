"""
Create Sample Data for BM25 Testing - Phase 3
"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'ddn_ai_analysis')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

sample_data = [
    {
        'build_id': 'BUILD_001',
        'error_category': 'CODE_ERROR',
        'root_cause': 'NullPointerException in UserService.java line 45',
        'fix_recommendation': 'Add null check before accessing user object',
        'confidence_score': 0.95
    },
    {
        'build_id': 'BUILD_002',
        'error_category': 'TIMEOUT_ERROR',
        'root_cause': 'Database connection timeout after 30 seconds',
        'fix_recommendation': 'Increase connection timeout to 60 seconds or optimize query',
        'confidence_score': 0.88
    },
    {
        'build_id': 'BUILD_003',
        'error_category': 'INFRA_ERROR',
        'root_cause': 'OutOfMemoryError: Java heap space',
        'fix_recommendation': 'Increase JVM heap size using -Xmx4g parameter',
        'confidence_score': 0.92
    },
    {
        'build_id': 'BUILD_004',
        'error_category': 'CODE_ERROR',
        'root_cause': 'IndexOutOfBoundsException in list access',
        'fix_recommendation': 'Add bounds checking before accessing list elements',
        'confidence_score': 0.90
    },
    {
        'build_id': 'BUILD_005',
        'error_category': 'NETWORK_ERROR',
        'root_cause': 'Connection refused to API endpoint at http://api.example.com',
        'fix_recommendation': 'Check network connectivity and API service status',
        'confidence_score': 0.85
    },
    {
        'build_id': 'BUILD_006',
        'error_category': 'AUTH_ERROR',
        'root_cause': 'Authentication failed - invalid credentials',
        'fix_recommendation': 'Verify API token and refresh if expired',
        'confidence_score': 0.93
    },
    {
        'build_id': 'BUILD_007',
        'error_category': 'CODE_ERROR',
        'root_cause': 'E500 Internal Server Error in payment processing',
        'fix_recommendation': 'Fix exception handling in PaymentController',
        'confidence_score': 0.87
    },
    {
        'build_id': 'BUILD_008',
        'error_category': 'TIMEOUT_ERROR',
        'root_cause': 'Test case timeout after 120 seconds waiting for element',
        'fix_recommendation': 'Increase wait timeout or optimize page load time',
        'confidence_score': 0.89
    },
    {
        'build_id': 'BUILD_009',
        'error_category': 'DATA_ERROR',
        'root_cause': 'Invalid JSON format in API response',
        'fix_recommendation': 'Add JSON validation before parsing response',
        'confidence_score': 0.91
    },
    {
        'build_id': 'BUILD_010',
        'error_category': 'CODE_ERROR',
        'root_cause': 'FileNotFoundException: config.properties not found',
        'fix_recommendation': 'Ensure config file exists in classpath or update file path',
        'confidence_score': 0.94
    }
]

def main():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

    cursor = conn.cursor()

    # Insert sample data
    for data in sample_data:
        cursor.execute("""
            INSERT INTO failure_analysis
            (build_id, error_category, root_cause, fix_recommendation, confidence_score, consecutive_failures)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['build_id'],
            data['error_category'],
            data['root_cause'],
            data['fix_recommendation'],
            data['confidence_score'],
            1
        ))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"SUCCESS: Inserted {len(sample_data)} sample records into failure_analysis table")

if __name__ == '__main__':
    main()
