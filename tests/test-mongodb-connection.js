/**
 * Test MongoDB Connection
 *
 * Run this to verify MongoDB is accessible and working
 */

require('dotenv').config();
const { MongoClient } = require('mongodb');

const mongodbUri = process.env.MONGODB_URI || 'mongodb://localhost:27017/ddn_tests';

async function testConnection() {
    console.log('Testing MongoDB Connection...');
    console.log('MongoDB URI:', mongodbUri);
    console.log('');

    try {
        console.log('Attempting to connect...');
        const client = new MongoClient(mongodbUri);
        await client.connect();

        console.log('✅ SUCCESS: Connected to MongoDB!');

        const db = client.db('ddn_tests');
        console.log('✅ Database: ddn_tests accessed');

        // Try to insert a test document
        const collection = db.collection('test_failures');
        const testDoc = {
            test_name: 'connection_test',
            timestamp: new Date(),
            message: 'This is a test document to verify MongoDB is working'
        };

        const result = await collection.insertOne(testDoc);
        console.log('✅ Test document inserted:', result.insertedId);

        // Retrieve it back
        const found = await collection.findOne({ _id: result.insertedId });
        console.log('✅ Test document retrieved:', found.test_name);

        // Clean up test document
        await collection.deleteOne({ _id: result.insertedId });
        console.log('✅ Test document deleted');

        await client.close();
        console.log('✅ Connection closed');

        console.log('');
        console.log('═'.repeat(60));
        console.log('✅ MongoDB is working correctly!');
        console.log('═'.repeat(60));
        console.log('');
        console.log('Your test failures should now be stored in MongoDB.');
        console.log('Run: npm test');

    } catch (error) {
        console.log('');
        console.log('═'.repeat(60));
        console.log('❌ MongoDB Connection FAILED');
        console.log('═'.repeat(60));
        console.log('');
        console.log('Error:', error.message);
        console.log('');
        console.log('Possible issues:');
        console.log('1. MongoDB is not running');
        console.log('   → Start MongoDB: mongod');
        console.log('   → Or: net start MongoDB');
        console.log('');
        console.log('2. MongoDB is running on a different port');
        console.log('   → Check: netstat -ano | findstr ":27017"');
        console.log('');
        console.log('3. MongoDB URI is incorrect');
        console.log('   → Current URI:', mongodbUri);
        console.log('   → Set in .env file: MONGODB_URI=mongodb://localhost:27017/ddn_tests');
        console.log('');
        process.exit(1);
    }
}

testConnection();
