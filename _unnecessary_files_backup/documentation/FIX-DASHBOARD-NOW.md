# 🚀 FIX DASHBOARD NOW - 2 Minutes

**Dashboard not running? Here's the fastest way to get it working!**

---

## ⚡ FASTEST WAY (2 minutes)

### Do you have Node.js?

**Check:**
```cmd
node --version
```

**If yes (shows version number):**

```cmd
START-DASHBOARD-ONLY.bat
```

**Then open:** http://localhost:5173

✅ **DONE! Dashboard is running!**

---

**If no (error message):**

**Install Node.js:**
1. Go to: https://nodejs.org/
2. Download LTS version
3. Install (click Next, Next, Finish)
4. Open new terminal
5. Run: `START-DASHBOARD-ONLY.bat`

**Time:** 5 minutes

---

## 🐳 Using Docker? (5 minutes)

### Is Docker Desktop running?

**Check system tray** for Docker whale icon

**If yes:**

```cmd
cd C:\DDN-AI-Project-Documentation

# Start just dashboard + API
docker-compose up -d dashboard-ui dashboard-api postgres

# Wait 2 minutes
timeout /t 120

# Open dashboard
start http://localhost:3000
```

✅ **DONE! Dashboard is running!**

---

**If Docker not running:**

1. **Start Docker Desktop** (search in Start menu)
2. **Wait** for whale icon to stop animating
3. Run commands above

---

**If Docker not installed:**

**Use Node.js method above instead!** (Faster)

---

## 🎯 Which Method Should I Use?

### Use Node.js Method If:
- ✅ You want to test UI quickly
- ✅ You don't need backend/database yet
- ✅ Docker is not installed
- ✅ You want to develop/modify dashboard

**Run:** `START-DASHBOARD-ONLY.bat`
**Opens:** http://localhost:5173

---

### Use Docker Method If:
- ✅ You need complete system
- ✅ You want backend + database + workflows
- ✅ Docker is already installed
- ✅ You want production-like environment

**Run:** `docker-compose up -d`
**Opens:** http://localhost:3000

---

## 📋 Step-by-Step (Node.js Method)

### Step 1: Check Node.js

```cmd
node --version
```

**See version?** ✅ Go to Step 2
**Error?** Install from https://nodejs.org/ then restart terminal

---

### Step 2: Run Script

```cmd
cd C:\DDN-AI-Project-Documentation
START-DASHBOARD-ONLY.bat
```

---

### Step 3: Wait for This Message

```
Local: http://localhost:5173
```

---

### Step 4: Open Browser

Click the link or open: http://localhost:5173

---

### Step 5: You Should See

**"DDN AI Test Failure Analysis Dashboard"**

✅ **SUCCESS!**

---

## 📋 Step-by-Step (Docker Method)

### Step 1: Start Docker Desktop

**Find Docker in Start Menu → Click**

Wait for whale icon to appear in system tray

---

### Step 2: Open Terminal

**Press:** Win + R
**Type:** cmd
**Press:** Enter

---

### Step 3: Navigate to Project

```cmd
cd C:\DDN-AI-Project-Documentation
```

---

### Step 4: Start Services

```cmd
docker-compose up -d dashboard-ui dashboard-api postgres
```

**Wait for:** "Creating ddn-dashboard-ui... done"

---

### Step 5: Wait 2 Minutes

Services need time to start

```cmd
timeout /t 120
```

---

### Step 6: Open Browser

```cmd
start http://localhost:3000
```

Or manually open: http://localhost:3000

---

### Step 7: You Should See

**"DDN AI Test Failure Analysis Dashboard"**

✅ **SUCCESS!**

---

## ❌ Still Not Working?

### Error: "node: command not found"

**Fix:** Install Node.js from https://nodejs.org/

---

### Error: "docker: command not found"

**Fix:**
1. Check if Docker Desktop is running
2. If not installed, use Node.js method instead

---

### Error: "Port 3000 already in use"

**Fix:**
```cmd
# Kill what's using the port
netstat -ano | findstr :3000
# Note the PID number, then:
taskkill /F /PID <number>

# Try again
docker-compose up -d dashboard-ui
```

---

### Error: "Cannot GET /"

**Fix:** Wait longer (services still starting)

```cmd
# Check if running
docker ps

# Check logs
docker-compose logs dashboard-ui
```

---

### Dashboard shows blank page

**Fix 1:** Hard refresh browser (Ctrl + Shift + R)

**Fix 2:** Clear cache and reload

**Fix 3:** Check browser console (F12) for errors

---

## 🔍 Verify It's Working

### Test 1: Can you access it?

**Open:** http://localhost:3000 (Docker) or http://localhost:5173 (Node.js)

**See:** Dashboard page

---

### Test 2: Navigation works?

**Click:** Dashboard, Failures, Analytics tabs

**All work?** ✅ Good!

---

### Test 3: No console errors?

**Press:** F12 in browser
**Click:** Console tab
**See:** No red errors

✅ **Working perfectly!**

---

## 📞 What's Next?

### Once Dashboard is Running:

1. **Test the UI**
   - Click around all pages
   - See the layout

2. **Start Backend** (if using Node.js method)
   ```cmd
   # In new terminal
   docker-compose up -d dashboard-api postgres
   ```

3. **Import n8n Workflows**
   ```cmd
   docker-compose up -d n8n
   # Open: http://localhost:5678
   ```

4. **Test Complete System**
   - Follow: [START-HERE.md](START-HERE.md:1)

---

## 🎯 Quick Reference

### Start Dashboard (Node.js)
```cmd
START-DASHBOARD-ONLY.bat
```
**URL:** http://localhost:5173

### Start Dashboard (Docker)
```cmd
docker-compose up -d dashboard-ui
```
**URL:** http://localhost:3000

### Start Everything (Docker)
```cmd
docker-compose up -d
```
**URL:** http://localhost:3000

### Stop Everything
```cmd
# Docker
docker-compose down

# Node.js
# Press Ctrl+C in terminal
```

### Check Status
```cmd
# Docker
docker ps

# Node.js
# Look for "Local: http://localhost:5173" message
```

---

## ✅ Success!

**Dashboard running?** ✅

**Next steps:**
- Read: [README-FIRST.md](README-FIRST.md:1)
- Follow: [START-HERE.md](START-HERE.md:1)
- Get full system: [ONE-COMMAND-SETUP.md](ONE-COMMAND-SETUP.md:1)

---

**Most people fix it by running:** `START-DASHBOARD-ONLY.bat`

**Last Updated:** October 22, 2025

**Just run the script and you're done!** 🚀
