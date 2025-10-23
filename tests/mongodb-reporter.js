/**
 * MongoDB Failure Reporter
 *
 * Automatically reports test failures to MongoDB database
 * No Jenkins or GitHub configuration needed - works out of the box
 */

const { MongoClient } = require('mongodb');

class MongoDBReporter {
    constructor() {
        this.mongodbUri = process.env.MONGODB_URI || 'mongodb://localhost:27017/ddn_tests';
        this.database = process.env.MONGODB_DATABASE || 'ddn_tests';
        this.collection = process.env.MONGODB_COLLECTION_FAILURES || 'test_failures';
        this.client = null;
    }

    /**
     * Connect to MongoDB
     */
    async connect() {
        if (!this.client) {
            this.client = new MongoClient(this.mongodbUri);
            await this.client.connect();
            console.log('✓ MongoDB Reporter: Connected to database');
        }
        return this.client.db(this.database);
    }

    /**
     * Report test failure to MongoDB
     * @param {Object} failureData - Test failure information
     */
    async reportFailure(failureData) {
        try {
            const db = await this.connect();
            const collection = db.collection(this.collection);

            // Build complete failure document
            const document = {
                // Test Information
                test_name: failureData.test_name,
                test_category: failureData.test_category,
                product: failureData.product || 'DDN Storage',
                error_message: failureData.error_message,
                stack_trace: failureData.stack_trace,

                // Build Information (from Jenkins environment variables)
                build_id: process.env.BUILD_ID || process.env.BUILD_NUMBER || 'local',
                job_name: process.env.JOB_NAME || 'manual-run',
                build_url: process.env.BUILD_URL || 'local',

                // Git Information
                git_commit: process.env.GIT_COMMIT || 'unknown',
                git_branch: process.env.GIT_BRANCH || 'main',
                repository: 'https://github.com/Sushrut-01/ddn-ai-test-analysis',

                // Status and Analysis
                status: 'FAILURE',
                analyzed: false,  // AI will set this to true after analysis
                analysis_required: true,

                // Timestamps
                timestamp: new Date(),
                created_at: new Date(),

                // Additional context
                environment: process.env.NODE_ENV || 'test',
                system: 'DDN Storage Tests',
                ...failureData  // Include any additional fields
            };

            const result = await collection.insertOne(document);
            console.log(`✓ Failure saved to MongoDB (ID: ${result.insertedId})`);
            return result.insertedId;
        } catch (error) {
            console.error('✗ MongoDB Reporter Error:', error.message);
            // Don't throw - we don't want MongoDB errors to break tests
            return null;
        }
    }

    /**
     * Report successful test to MongoDB (for tracking)
     */
    async reportSuccess(testData) {
        try {
            const db = await this.connect();
            const collection = db.collection('test_results');

            const document = {
                test_name: testData.test_name,
                test_category: testData.test_category,
                product: testData.product,
                status: 'SUCCESS',
                duration_ms: testData.duration_ms,
                build_id: process.env.BUILD_ID || 'local',
                job_name: process.env.JOB_NAME || 'manual-run',
                timestamp: new Date(),
                created_at: new Date()
            };

            await collection.insertOne(document);
            console.log(`✓ Success recorded in MongoDB`);
        } catch (error) {
            console.error('✗ MongoDB Reporter Error:', error.message);
        }
    }

    /**
     * Close MongoDB connection
     */
    async close() {
        if (this.client) {
            await this.client.close();
            this.client = null;
            console.log('✓ MongoDB Reporter: Connection closed');
        }
    }
}

// Export singleton instance
module.exports = new MongoDBReporter();
