# Quick Start - Run Build #27 with BOTH Test Frameworks

## ⚡ 3-Minute Setup

### 1️⃣ Open Jenkins Script (5 seconds)
```powershell
notepad C:\DDN-AI-Project-Documentation\JENKINS-UNIFIED-BUILD-SCRIPT.bat
```

### 2️⃣ Copy Everything (5 seconds)
- Press **Ctrl+A** (Select All)
- Press **Ctrl+C** (Copy)

### 3️⃣ Paste into Jenkins (1 minute)
1. Go to: **http://localhost:8081/job/DDN-Nightly-Tests/configure**
2. Scroll to **"Build Steps"**
3. **Delete** old build step
4. Click **"Add build step"** → **"Execute Windows batch command"**
5. **Paste** with **Ctrl+V**
6. Click **"Save"**

### 4️⃣ Run Build (1 second)
- Click **"Build Now"**
- Watch Build #27 run!

---

## ✅ What Happens in Build #27

### Both Frameworks Run:
```
Build #27 starts
    ↓
[1] Robot Framework tests run
    ↓
    Failures → MongoDB (with suite metadata)
    ↓
[2] Mocha tests run
    ↓
    Failures → MongoDB (with suite metadata)
    ↓
Build #27 complete
    ↓
Dashboard shows ALL failures!
```

---

## 🔍 How to Verify It Worked

### Check Jenkins Console:
Should see:
```
[STEP 4/5] Running Robot Framework Tests...
✓ Failure saved to MongoDB (ID: ...)

[STEP 5/5] Running Mocha/JavaScript Tests...
✓ Failure saved to MongoDB (ID: ...)
```

### Check MongoDB:
```powershell
python check_mongodb.py
```

Should show:
```
Found X failures from Build #27
✓ All have suite_name
✓ All have pass_count, fail_count, total_count
```

### Check Dashboard:
```
http://localhost:5173/failures
```

Should show:
- Failures from both Robot Framework AND Mocha
- Each has suite metadata
- Build ID: DDN-Nightly-Tests-27

---

## 📊 Expected Results

| Framework | Test File | Suite Name | Failures |
|-----------|-----------|------------|----------|
| Robot | robot-tests/basic_tests.robot | "Basic DDN Tests" | 0-5 |
| Mocha | tests/ddn-advanced-scenarios.js | "Domain-Based Isolation..." | 0-10 |

**Total:** Up to 15 possible test failures across both frameworks

---

## 🎯 Success = Build #27 Shows:

- ✅ Both "Running Robot Framework" and "Running Mocha Tests"
- ✅ Failures reported to MongoDB from BOTH frameworks
- ✅ Dashboard displays ALL failures
- ✅ Suite metadata present on ALL failures

---

**Ready?** Open Jenkins and paste the script! 🚀
