# 🚀 CLIENT QUICK START GUIDE

## Welcome! Your DDN AI Test Analysis System is Ready

Everything is set up and ready to use. Follow these **3 simple steps**:

---

## ⚡ Quick 3-Step Setup

### STEP 1: Start MongoDB (1 minute)

MongoDB stores all test failures automatically.

```cmd
# Start MongoDB (if not running)
mongod

# Or if MongoDB is a service:
net start MongoDB
```

**Verify it's running:**
```cmd
mongosh
# If you see a MongoDB prompt, it's working! Type 'exit' to leave.
```

---

### STEP 2: Start Jenkins (1 minute)

Jenkins runs your tests automatically.

```cmd
cd C:\DDN-AI-Project-Documentation
start-jenkins.bat
```

**Wait 30-60 seconds**, then open: **http://localhost:8081**

You should see the Jenkins dashboard!

---

### STEP 3: Run Your First Test (2 minutes)

```cmd
cd C:\DDN-AI-Project-Documentation\tests
npm install
npm test
```

**What happens:**
1. Tests run against DDN storage endpoints
2. Any failures automatically save to MongoDB
3. You can view them in the dashboard!

---

## ✅ That's It!

You now have:
- ✅ Jenkins running (http://localhost:8081)
- ✅ MongoDB storing test failures
- ✅ 47 comprehensive DDN tests
- ✅ Automatic failure reporting (no configuration needed!)

---

## 📊 View Your Test Results

### Option 1: MongoDB (Raw Data)

```cmd
mongosh
use ddn_tests
db.test_failures.find().pretty()
```

### Option 2: Dashboard (Visual)

```cmd
cd implementation\dashboard-ui
npm install
npm run dev
```

Open: **http://localhost:5173**

---

## 🔄 Daily Usage

### Run Tests Manually:
```cmd
cd tests
npm test
```

### Run Specific Test Suite:
```cmd
# Basic tests only
npm run test:basic

# Advanced multi-tenancy tests
npm run test:advanced

# Security tests
npm run test:security
```

### View Jenkins Jobs:
http://localhost:8081

Your Jenkins jobs are:
1. **DDN-Basic-Tests** - Basic product tests
2. **DDN-Advanced-Tests** - Multi-tenancy tests
3. **DDN-Nightly-Tests** - Full suite (runs at 2 AM daily)

---

## 🎯 How Automatic Reporting Works

```
You push code → Jenkins runs tests → Test fails → AUTO-saves to MongoDB
```

**You don't configure anything!**

The test scripts automatically:
- ✅ Connect to MongoDB
- ✅ Save failure details
- ✅ Capture Jenkins build info
- ✅ Store Git commit info
- ✅ Mark for AI analysis

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `START-NOW.md` | Original 3-step setup guide |
| `MONGODB-AUTOMATIC-REPORTING-COMPLETE.md` | Complete MongoDB reporting documentation |
| `tests/AUTOMATIC-MONGODB-REPORTING.md` | How automatic reporting works |
| `tests/.env.example` | Configuration reference (uses defaults!) |
| `FINAL-COMPLETE-SUMMARY.md` | Complete project overview |

---

## 🆘 Troubleshooting

### MongoDB not running?
```cmd
mongod --dbpath C:\data\db
```

### Jenkins not accessible?
```cmd
cd C:\DDN-AI-Project-Documentation
start-jenkins.bat
```
Wait 60 seconds, then try http://localhost:8081

### Tests failing to connect?
Edit `tests/.env` with your actual DDN endpoints:
```env
DDN_EXASCALER_ENDPOINT=http://your-exascaler-ip:8080
DDN_API_KEY=your-actual-api-key
```

### Want to see what's in MongoDB?
```cmd
mongosh
use ddn_tests
show collections
db.test_failures.countDocuments()
```

---

## 🎓 Understanding Your Test Suite

### 47 Total Tests:

**Basic Tests (23 tests):**
- EXAScaler (Lustre) - 4 tests
- AI400X Series - 5 tests
- Infinia - 4 tests
- IntelliFlash - 4 tests
- Integration - 3 tests
- Performance - 3 tests

**Advanced Tests (24 tests):**
- Domain Isolation - 3 tests
- Multi-Tenancy - 4 tests
- Quota Management - 4 tests
- S3 Protocol - 4 tests
- Kerberos Auth - 2 tests
- Data Governance - 3 tests
- Security - 4 tests

---

## 🔐 Jenkins Jobs (Already Created)

### DDN-Basic-Tests
- **Runs:** Every 15 minutes (polls GitHub)
- **Tests:** 23 basic product tests
- **URL:** http://localhost:8081/job/DDN-Basic-Tests/

### DDN-Advanced-Tests
- **Runs:** On every commit + manual
- **Tests:** 24 advanced multi-tenancy tests
- **URL:** http://localhost:8081/job/DDN-Advanced-Tests/

### DDN-Nightly-Tests
- **Runs:** Daily at 2:00 AM
- **Tests:** All 47 tests + performance benchmarks
- **URL:** http://localhost:8081/job/DDN-Nightly-Tests/

---

## 🚦 Next Steps (Optional)

### 1. Configure Your DDN Endpoints

Copy the example and add your real endpoints:
```cmd
cd tests
copy .env.example .env
notepad .env
```

### 2. Set Up GitHub Webhook (for auto-builds)

1. Go to: https://github.com/Sushrut-01/ddn-ai-test-analysis
2. Settings → Webhooks → Add webhook
3. Payload URL: `http://your-jenkins-url:8081/github-webhook/`
4. Content type: `application/json`
5. Events: Just the push event

### 3. Enable AI Analysis

AI analysis runs through n8n workflows (separate from failure reporting).

See: `RAG-MASTER-GUIDE.md` for AI setup

---

## 💡 Key Points

1. **MongoDB Automatic Reporting**
   - No configuration needed
   - Failures automatically saved
   - Dashboard reads directly from MongoDB

2. **No Webhooks for Failure Reporting**
   - Tests write directly to MongoDB
   - n8n is only for AI orchestration
   - Simpler, more reliable

3. **Zero Client Configuration**
   - You don't touch Jenkins configs
   - You don't modify GitHub scripts
   - Everything works automatically

---

## 📞 Support

**Documentation Files:**
- Complete setup: `FINAL-COMPLETE-SUMMARY.md`
- MongoDB reporting: `MONGODB-AUTOMATIC-REPORTING-COMPLETE.md`
- Test scenarios: `tests/README.md`
- Architecture: `Architecture_process.jpg`

**Quick Commands:**
```cmd
# Start Jenkins
start-jenkins.bat

# Run tests
cd tests && npm test

# Check MongoDB
mongosh

# Start dashboard
cd implementation\dashboard-ui && npm run dev
```

---

## ✨ You're All Set!

Your DDN AI Test Analysis System is **ready to use**.

**No configuration needed - it just works!** 🎉

Run your first test:
```cmd
cd tests
npm test
```

Check the results in MongoDB or the dashboard!
