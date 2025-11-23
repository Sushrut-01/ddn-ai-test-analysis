# Automatic MongoDB Failure Reporting

## How It Works (Zero Configuration Required)

When Jenkins runs your tests, **failures are automatically saved to MongoDB Atlas** (cloud). Tests will write to the database referenced by the `MONGODB_URI` environment variable and the Dashboard reads from the same Atlas instance.

```
Jenkins → npm test → Test fails → Writes to MongoDB Atlas → Dashboard shows it
```

## For the Client: Minimal configuration

The test scripts **automatically**:
1. Detect when a test fails
2. Connect to the MongoDB instance specified by `MONGODB_URI`
3. Save the failure with all details
4. Dashboard reads from MongoDB Atlas and displays it

**You only need to provide a MongoDB Atlas connection string once** (see below). We recommend storing the Atlas URI securely in Jenkins credentials or in a `.env` file for local development.

---

## How to Use

### 1. Configure MongoDB Atlas (one-time)

1. Create a free or paid cluster at https://cloud.mongodb.com/ and create a database user with read/write permissions for the test database (example: `ddn_tests`).
2. Copy the connection string (MongoDB SRV URI) and set it in your `.env` file or as a Jenkins credential named `MONGODB_URI`.

Example `.env` entry:
```env
MONGODB_URI=mongodb+srv://ddn_user:MySecret%40123@cluster0.abcd.mongodb.net/ddn_tests?retryWrites=true&w=majority
MONGODB_DATABASE=ddn_tests
MONGODB_COLLECTION_FAILURES=test_failures
```

### 2. Run tests (they report to Atlas)

From your CI job or developer machine (with `MONGODB_URI` available):
```powershell
cd tests
npm ci
npm test
```

### 3. View failures in Atlas (Atlas UI or mongosh)

Use the Atlas web UI to inspect the `test_failures` collection, or connect via `mongosh` using the same SRV URI:
```powershell
mongosh "${MONGODB_URI}"
use ddn_tests
db.test_failures.find().sort({timestamp: -1}).limit(5).pretty()
```

### 4. Dashboard automatically shows failures
- Dashboard reads from `MONGODB_URI` and displays failures from the configured Atlas database.

If `MONGODB_URI` is not set, the Dashboard will log a clear error and startup will fail; set the environment variable or inject it from Jenkins credentials.

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

If you want to customize MongoDB settings, create a `.env` file and set the `MONGODB_URI` to your Atlas connection string. Do NOT check secrets into source control; add `.env` to your `.gitignore` or use Jenkins credentials for CI.

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
