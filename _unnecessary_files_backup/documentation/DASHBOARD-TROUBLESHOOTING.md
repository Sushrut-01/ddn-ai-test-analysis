# Dashboard Not Running - Quick Fix Guide

**Let's get your dashboard up and running!**

---

## 🎯 Three Ways to Start the Dashboard

### Option 1: Standalone Dashboard (Fastest - 2 minutes)

**Best for:** Testing the UI without Docker

```cmd
START-DASHBOARD-ONLY.bat
```

**What it does:**
- Installs Node.js dependencies
- Starts development server
- Opens at: http://localhost:5173

**Requirements:**
- Node.js installed (https://nodejs.org/)

---

### Option 2: Full Docker System (10 minutes)

**Best for:** Complete system with all services

```cmd
COMPLETE-SETUP-WIZARD.bat
```

**What it does:**
- Starts all 13 Docker services
- Dashboard + Backend + Database + Workflows
- Opens at: http://localhost:3000

**Requirements:**
- Docker Desktop installed and running

---

### Option 3: Manual Docker Start

**If you have Docker running:**

```cmd
cd C:\DDN-AI-Project-Documentation

# Start all services
docker-compose up -d

# Wait 2-3 minutes, then check
docker ps

# Open dashboard
start http://localhost:3000
```

---

## 🔍 Troubleshooting Steps

### Check 1: Is Docker Running?

**Windows:** Check if Docker Desktop is running in system tray

**Test:**
```cmd
docker --version
```

**If not installed:**
- Download: https://www.docker.com/products/docker-desktop
- Install and restart computer

---

### Check 2: Are Services Running?

```cmd
docker ps
```

**Should show containers like:**
- `ddn-dashboard-ui`
- `ddn-dashboard-api`
- `ddn-n8n`
- etc.

**If empty:** Services not started yet

---

### Check 3: Check Docker Compose

```cmd
cd C:\DDN-AI-Project-Documentation

# Check if docker-compose.yml exists
dir docker-compose.yml

# Start services
docker-compose up -d

# Check logs
docker-compose logs dashboard-ui
```

---

### Check 4: Is Node.js Installed? (For Standalone)

**Test:**
```cmd
node --version
npm --version
```

**If not installed:**
- Download: https://nodejs.org/
- Install LTS version
- Restart terminal

---

## 🚀 Quick Fix Solutions

### Solution 1: Start Dashboard Standalone (No Docker Needed)

```cmd
# Navigate to dashboard folder
cd C:\DDN-AI-Project-Documentation\implementation\dashboard-ui

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Opens at:** http://localhost:5173

---

### Solution 2: Start with Docker

```cmd
cd C:\DDN-AI-Project-Documentation

# Stop any existing services
docker-compose down

# Build images
docker-compose build dashboard-ui

# Start just dashboard and API
docker-compose up -d dashboard-ui dashboard-api postgres

# Check status
docker-compose ps

# View logs
docker-compose logs -f dashboard-ui
```

**Opens at:** http://localhost:3000

---

### Solution 3: Use the Wizard

```cmd
cd C:\DDN-AI-Project-Documentation
COMPLETE-SETUP-WIZARD.bat
```

Follow the prompts. The wizard will:
1. Check prerequisites
2. Configure environment
3. Start all services
4. Open dashboard automatically

---

## 🐛 Common Errors & Fixes

### Error: "Port 3000 already in use"

**Fix:**
```cmd
# Find what's using port 3000
netstat -ano | findstr :3000

# Kill the process (replace PID with actual number)
taskkill /F /PID <PID>

# Or use different port
set PORT=3001
docker-compose up -d dashboard-ui
```

---

### Error: "Cannot find module"

**Fix:**
```cmd
cd implementation\dashboard-ui
npm install
npm run dev
```

---

### Error: "Docker daemon not running"

**Fix:**
1. Open Docker Desktop
2. Wait for it to fully start (whale icon stops animating)
3. Try again:
   ```cmd
   docker ps
   ```

---

### Error: "ECONNREFUSED localhost:5005"

**Means:** Dashboard is running but API is not

**Fix:**
```cmd
# Start the API
docker-compose up -d dashboard-api

# Or start all services
docker-compose up -d
```

---

### Error: Dashboard shows blank page

**Fix 1:** Clear browser cache and reload

**Fix 2:** Check browser console (F12) for errors

**Fix 3:** Restart dashboard:
```cmd
docker-compose restart dashboard-ui
```

**Fix 4:** Rebuild:
```cmd
docker-compose build dashboard-ui
docker-compose up -d dashboard-ui
```

---

## 📊 Verify Dashboard is Running

### Test 1: Check the Port

```cmd
# Windows
netstat -ano | findstr :3000

# Should show something listening on port 3000
```

---

### Test 2: Curl Test

```cmd
curl http://localhost:3000
```

**Should return:** HTML content

---

### Test 3: Browser Test

**Open:** http://localhost:3000

**Should see:** DDN AI Test Failure Analysis Dashboard

---

### Test 4: Check Docker Logs

```cmd
docker-compose logs dashboard-ui
```

**Should NOT show:** Error messages

**Should show:**
- "Server running on port 3000"
- "Compiled successfully"

---

## 🎯 Recommended Approach

**For quick testing:**

1. **Install Node.js** (if not installed)
   - https://nodejs.org/

2. **Run standalone dashboard:**
   ```cmd
   START-DASHBOARD-ONLY.bat
   ```

3. **Open browser:**
   - http://localhost:5173

**For full system:**

1. **Install Docker Desktop** (if not installed)
   - https://www.docker.com/products/docker-desktop

2. **Run complete wizard:**
   ```cmd
   COMPLETE-SETUP-WIZARD.bat
   ```

3. **Open browser:**
   - http://localhost:3000

---

## 📝 Step-by-Step: Get Dashboard Running NOW

### If you have Node.js:

```cmd
# Step 1: Open terminal
# Press Win+R, type: cmd, press Enter

# Step 2: Navigate to project
cd C:\DDN-AI-Project-Documentation

# Step 3: Run standalone dashboard
START-DASHBOARD-ONLY.bat

# Step 4: Wait for "Local: http://localhost:5173"

# Step 5: Open browser to http://localhost:5173
```

**Time:** 2 minutes

---

### If you have Docker:

```cmd
# Step 1: Start Docker Desktop
# Wait for it to fully start

# Step 2: Open terminal
cd C:\DDN-AI-Project-Documentation

# Step 3: Start services
docker-compose up -d dashboard-ui dashboard-api postgres

# Step 4: Wait 2 minutes

# Step 5: Open http://localhost:3000
```

**Time:** 5 minutes

---

## 🆘 Still Not Working?

### Collect Debug Info:

```cmd
# Check Node.js
node --version

# Check npm
npm --version

# Check Docker
docker --version
docker ps

# Check if ports are free
netstat -ano | findstr :3000
netstat -ano | findstr :5173

# Check logs
docker-compose logs dashboard-ui
```

**Send this output for help!**

---

## ✅ Success Checklist

Dashboard is running when:

- [ ] Browser opens http://localhost:3000 or http://localhost:5173
- [ ] You see "DDN AI Test Failure Analysis" heading
- [ ] No error messages in browser console (F12)
- [ ] Navigation menu works (Dashboard, Failures, Analytics)

**All checked?** Dashboard is working! 🎉

---

## 🎯 Quick Commands Reference

### Standalone (Node.js)
```cmd
START-DASHBOARD-ONLY.bat
# Opens: http://localhost:5173
```

### Docker (Full System)
```cmd
docker-compose up -d
# Opens: http://localhost:3000
```

### Wizard (Complete Setup)
```cmd
COMPLETE-SETUP-WIZARD.bat
# Opens: http://localhost:3000
```

### Stop Everything
```cmd
# Stop Docker
docker-compose down

# Stop Node.js
# Press Ctrl+C in the terminal
```

---

## 📞 Next Steps After Dashboard Starts

1. **Test the UI**
   - Click around
   - Check all pages load

2. **Connect to Backend**
   - Needs dashboard-api running
   - Start with: `docker-compose up -d dashboard-api`

3. **Import Workflows**
   - Open: http://localhost:5678
   - Import n8n workflows

4. **Test Full Flow**
   - Trigger analysis
   - See results

---

**Most Common Fix:** Just run `START-DASHBOARD-ONLY.bat`! 🚀

**Last Updated:** October 22, 2025
