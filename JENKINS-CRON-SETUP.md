# Jenkins Cron Job Setup for Robot Framework Tests

## 🎯 Objective
Configure Jenkins to automatically run Robot Framework tests every 10 minutes using cron scheduling.

---

## 📋 Quick Setup Steps

### Step 1: Open Jenkins Configuration
1. Navigate to: http://localhost:8081/job/DDN-Nightly-Tests/configure
2. Scroll to **Build Triggers** section

### Step 2: Enable Cron Scheduling
1. Check the box: ☑️ **Build periodically**
2. In the **Schedule** field, enter:
   ```
   */10 * * * *
   ```
3. Click **Save**

---

## ⏰ Cron Schedule Options

| Schedule | Description | Frequency |
|----------|-------------|-----------|
| `*/10 * * * *` | Every 10 minutes | 144 builds/day |
| `*/5 * * * *` | Every 5 minutes | 288 builds/day |
| `*/15 * * * *` | Every 15 minutes | 96 builds/day |
| `H/10 * * * *` | Every ~10 minutes (load balanced) | ~144 builds/day |
| `0 * * * *` | Every hour at minute 0 | 24 builds/day |
| `0 */2 * * *` | Every 2 hours | 12 builds/day |
| `0 9-17 * * 1-5` | 9 AM - 5 PM, weekdays only | 9 builds/day |

**Recommended:** `*/10 * * * *` for continuous testing

---

## 🔍 Cron Syntax Explained

```
*/10 * * * *
│    │ │ │ │
│    │ │ │ └─── Day of week (0-7, 0=Sunday)
│    │ │ └───── Month (1-12)
│    │ └─────── Day of month (1-31)
│    └───────── Hour (0-23)
└────────────── Minute (0-59)
```

**Special Characters:**
- `*` = Every unit (every minute, every hour, etc.)
- `*/10` = Every 10 units (every 10 minutes)
- `H` = Hash (Jenkins spreads builds to avoid spikes)
- `H/10` = Every ~10 minutes with hash distribution

---

## ✅ Verification Steps

### 1. Confirm Cron is Active
```bash
# Check Jenkins job configuration via API
curl -s "http://localhost:8081/job/DDN-Nightly-Tests/config.xml" | grep -A 3 "<triggers>"
```

**Expected output:**
```xml
<triggers>
  <hudson.triggers.TimerTrigger>
    <spec>*/10 * * * *</spec>
  </hudson.triggers.TimerTrigger>
</triggers>
```

### 2. Monitor Auto-Builds
```bash
# Watch Jenkins console for scheduled builds
curl -s "http://localhost:8081/job/DDN-Nightly-Tests/lastBuild/api/json" | jq '.result, .timestamp'
```

### 3. Check MongoDB Atlas for New Failures
```bash
python check_recent_atlas.py
```

**Expected output:**
```
Total failures in Atlas: 833
Failures in last 10 minutes: X
✓ NEW FAILURES detected!
```

---

## 🚀 What Happens Next?

**Every 10 minutes:**
1. Jenkins triggers Build #N automatically
2. Linux bash script executes (`COPY-THIS-TO-JENKINS-LINUX.sh`)
3. Robot Framework tests run
4. `mongodb_robot_listener.py` captures failures
5. Failures written to MongoDB Atlas
6. Dashboard refreshes automatically

**Complete Flow:**
```
⏰ Cron Trigger (*/10 * * * *)
    ↓
🔨 Jenkins Build #N
    ↓
🤖 Robot Framework Tests
    ↓
📊 mongodb_robot_listener.py
    ↓
☁️ MongoDB Atlas (ddn_tests.test_failures)
    ↓
📈 Dashboard (http://localhost:5173)
```

---

## 🛠️ Troubleshooting

### Build Not Triggering Automatically?
1. Check cron syntax in Jenkins UI
2. Verify Jenkins job is not disabled
3. Look for errors in Jenkins system log: http://localhost:8081/log/all

### Tests Running But No Dashboard Updates?
1. Check Build #N console output: http://localhost:8081/job/DDN-Nightly-Tests/lastBuild/console
2. Verify `mongodb_robot_listener.py` loaded successfully
3. Check MongoDB connection in console
4. Run `python check_recent_atlas.py` to verify data

### Too Many Builds?
- Use `*/15 * * * *` (every 15 min) or `*/30 * * * *` (every 30 min)
- Or schedule only during work hours: `*/10 9-17 * * 1-5`

---

## 📊 Current Configuration

**Job:** DDN-Nightly-Tests
**Current Schedule:** `0 2 * * *` (2 AM daily)
**Recommended:** `*/10 * * * *` (every 10 minutes)

**Build Command:**
```bash
#!/bin/bash
python3 -m pip install --quiet robotframework pymongo boto3 requests
export MONGODB_URI="mongodb+srv://..."
python3 -m robot --outputdir robot-results --listener implementation/mongodb_robot_listener.py robot-tests/
```

---

## ✅ Success Criteria

- ✅ Jenkins triggers builds automatically every 10 minutes
- ✅ Robot Framework tests execute successfully
- ✅ Test failures captured to MongoDB Atlas
- ✅ Dashboard shows new failures within 10 minutes
- ✅ Bug fixes verified: suite_name, pass_count, fail_count, total_count populated

---

## 📝 Next Steps

1. **Configure cron:** Add `*/10 * * * *` to Jenkins
2. **Wait 10 minutes:** Let first auto-build trigger
3. **Verify MongoDB:** Check for new failures in Atlas
4. **Check Dashboard:** Confirm updates visible at http://localhost:5173
5. **Monitor:** Watch Jenkins build history for consistent execution

**Ready to enable!** 🚀
