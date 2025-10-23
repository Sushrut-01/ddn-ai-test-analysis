# Automatic MongoDB Failure Reporting

## How It Works (Zero Configuration Required)

When Jenkins runs your tests, **failures are automatically saved to MongoDB** - no manual configuration needed!

```
Jenkins → npm test → Test fails → Automatically writes to MongoDB → Dashboard shows it
```

## For the Client: Nothing to Configure!

The test scripts **automatically**:
1. Detect when a test fails
2. Connect to MongoDB (localhost:27017)
3. Save the failure with all details
4. Dashboard reads from MongoDB and displays it

**You don't need to:**
- ❌ Configure Jenkins
- ❌ Modify GitHub scripts
- ❌ Set up webhooks
- ❌ Install anything extra

**It just works!**

---

## How to Use

### 1. Make sure MongoDB is running:
```cmd
# MongoDB should be running on localhost:27017
# Check if it's running:
mongosh
```

### 2. Run tests (they automatically report to MongoDB):
```cmd
cd tests
npm install
npm test
```

### 3. View failures in MongoDB:
```javascript
// Connect to MongoDB
use ddn_tests

// See all test failures
db.test_failures.find().pretty()

// See latest failure
db.test_failures.find().sort({timestamp: -1}).limit(1).pretty()
```

### 4. Dashboard automatically shows failures:
- Dashboard reads from MongoDB
- No configuration needed
- Real-time updates

---

## Example: What Gets Saved to MongoDB

When a test fails, this is automatically saved:

```json
{
  "_id": ObjectId("..."),
  "test_name": "should connect to EXAScaler Lustre file system",
  "test_category": "STORAGE_CONNECTIVITY",
  "product": "EXAScaler",
  "error_message": "connect ECONNREFUSED 127.0.0.1:8080",
  "stack_trace": "Error: connect ECONNREFUSED...",

  "build_id": "123",
  "job_name": "DDN-Basic-Tests",
  "build_url": "http://localhost:8081/job/DDN-Basic-Tests/123/",

  "git_commit": "38d11f08ebd4ed68bf701a8887509172bd6fe2a8",
  "git_branch": "main",
  "repository": "https://github.com/Sushrut-01/ddn-ai-test-analysis",

  "status": "FAILURE",
  "analyzed": false,
  "analysis_required": true,

  "timestamp": ISODate("2025-10-23T16:31:19.000Z"),
  "created_at": ISODate("2025-10-23T16:31:19.000Z"),

  "environment": "test",
  "system": "DDN Storage Tests"
}
```

---

## MongoDB Collections

The system automatically creates these collections:

| Collection | Purpose |
|-----------|---------|
| `test_failures` | All failed tests (waiting for AI analysis) |
| `test_results` | All test results (pass/fail) |
| `analysis_results` | AI analysis of failures |

---

## Environment Variables (Optional)

If you want to customize MongoDB settings, create a `.env` file:

```env
# MongoDB Configuration (Optional - defaults work out of the box)
MONGODB_URI=mongodb://localhost:27017/ddn_tests
MONGODB_DATABASE=ddn_tests
MONGODB_COLLECTION_FAILURES=test_failures
```

**But you don't need to!** The defaults work automatically.

---

## How Jenkins Uses This

Jenkins job configuration is simple:

```xml
<builders>
  <hudson.tasks.Shell>
    <command>
cd tests
npm ci
npm test
    </command>
  </hudson.tasks.Shell>
</builders>
```

That's it! When `npm test` runs:
1. Tests execute
2. Failures automatically go to MongoDB
3. Jenkins doesn't need to do anything else
4. Dashboard shows the failures

---

## Viewing in Dashboard

The dashboard automatically:
1. Connects to MongoDB
2. Queries `test_failures` collection
3. Displays all unanalyzed failures
4. Shows "Analyze with AI" button
5. Updates when AI analysis completes

**No configuration needed!**

---

## Technical Details (For Developers)

The `mongodb-reporter.js` module:
- Automatically connects to MongoDB
- Uses environment variables from Jenkins (BUILD_ID, JOB_NAME, etc.)
- Gracefully handles MongoDB connection failures
- Doesn't break tests if MongoDB is unavailable

Test scripts import and use it:
```javascript
const mongoReporter = require('./mongodb-reporter');

// In test failure handler:
await mongoReporter.reportFailure({
    test_name: 'My Test',
    test_category: 'CONNECTIVITY',
    error_message: error.message,
    stack_trace: error.stack
});
```

Jenkins provides these automatically:
- `BUILD_ID` or `BUILD_NUMBER`
- `JOB_NAME`
- `BUILD_URL`
- `GIT_COMMIT`
- `GIT_BRANCH`

---

## Summary

✅ **Automatic** - No configuration needed
✅ **Zero-touch** - Client doesn't modify scripts
✅ **Reliable** - Works even if MongoDB is temporarily down
✅ **Complete** - Captures all failure details
✅ **Integrated** - Dashboard reads directly from MongoDB

**The client just runs Jenkins → Everything works automatically!**
