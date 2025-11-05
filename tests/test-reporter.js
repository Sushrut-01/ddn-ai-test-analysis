/**
 * Test MongoDB Reporter with dotenv fix
 */

const mongoReporter = require('./mongodb-reporter');

async function testReporter() {
    console.log('Testing MongoDB Reporter...');
    console.log('');

    try {
        // Test reporting a failure
        const testFailure = {
            test_name: 'Test Reporter Verification',
            test_category: 'System Test',
            product: 'MongoDB Reporter',
            error_message: 'This is a test failure to verify MongoDB Atlas connection',
            stack_trace: 'at testReporter (test-reporter.js:15:10)'
        };

        console.log('Reporting test failure...');
        const failureId = await mongoReporter.reportFailure(testFailure);

        if (failureId) {
            console.log('');
            console.log('════════════════════════════════════════════════════════════');
            console.log('✅ MongoDB Reporter is working correctly!');
            console.log('════════════════════════════════════════════════════════════');
            console.log('');
            console.log('Failure ID:', failureId);
            console.log('Check MongoDB Atlas to see the document.');
        } else {
            console.log('');
            console.log('════════════════════════════════════════════════════════════');
            console.log('❌ MongoDB Reporter failed to save failure');
            console.log('════════════════════════════════════════════════════════════');
        }

        // Close connection
        await mongoReporter.close();

    } catch (error) {
        console.error('❌ Error:', error.message);
        process.exit(1);
    }
}

testReporter();
