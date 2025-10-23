# Manual Dashboard Setup - Step by Step

**Let's get your dashboard running manually, one step at a time**

---

## 🔍 First: Check Your System

Run this to see what you have:

```cmd
CHECK-SYSTEM.bat
```

This will tell you:
- ✅ What's installed
- ❌ What's missing
- 💡 What you can do

---

## 📋 Method 1: Node.js (Recommended)

**Time:** 5-10 minutes
**Requirements:** Node.js installed

### Step 1: Install Node.js (if needed)

**Check if you have it:**
```cmd
node --version
```

**If you see "command not found":**

1. Go to: https://nodejs.org/
2. Download **LTS** version (left side, recommended)
3. Run installer
4. Click Next → Next → Install
5. **Restart your terminal** (close and open new one)
6. Test again: `node --version`

---

### Step 2: Open Terminal

**Windows:**
- Press `Win + R`
- Type: `cmd`
- Press Enter

---

### Step 3: Navigate to Dashboard Folder

```cmd
cd C:\DDN-AI-Project-Documentation\implementation\dashboard-ui
```

**Verify you're in the right place:**
```cmd
dir
```

**You should see:**
- `package.json`
- `src` folder
- `index.html`
- `vite.config.js`

---

### Step 4: Install Dependencies

**First time only (takes 2-3 minutes):**

```cmd
npm install
```

**Wait for it to finish. You should see:**
```
added XXX packages
```

**If you see errors about Python or build tools:**
- These are warnings, usually okay to ignore
- Dashboard will still work

---

### Step 5: Start Development Server

```cmd
npm run dev
```

**Wait for this message:**
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

### Step 6: Open Browser

**Either:**
- Hold `Ctrl` and click the `http://localhost:5173/` link in terminal
- Or manually open browser and go to: `http://localhost:5173`

---

### Step 7: Verify Dashboard Loaded

**You should see:**
- Page title: "DDN AI Test Failure Analysis Dashboard"
- Navigation menu: Dashboard, Failures, Analytics, Manual Trigger
- Clean interface (no errors)

✅ **SUCCESS!**

**To stop:** Press `Ctrl + C` in the terminal

---

## 📋 Method 2: Docker

**Time:** 10 minutes
**Requirements:** Docker Desktop installed and running

### Step 1: Install Docker (if needed)

**Check if you have it:**
```cmd
docker --version
```

**If you see "command not found":**

1. Go to: https://www.docker.com/products/docker-desktop
2. Download Docker Desktop for Windows
3. Run installer
4. **Restart your computer**
5. Start Docker Desktop from Start menu
6. Wait for whale icon in system tray (stops animating when ready)

---

### Step 2: Verify Docker is Running

```cmd
docker ps
```

**Should show:** Table with columns (CONTAINER ID, IMAGE, etc.)

**If error "daemon not running":**
- Start Docker Desktop
- Wait for it to fully start
- Try again

---

### Step 3: Navigate to Project

```cmd
cd C:\DDN-AI-Project-Documentation
```

---

### Step 4: Start Dashboard Container

```cmd
docker-compose up -d dashboard-ui
```

**This will:**
- Build the dashboard image (first time: 5-10 minutes)
- Start the container
- Return to prompt

---

### Step 5: Wait for Container to Start

```cmd
timeout /t 60
```

**Or check manually:**
```cmd
docker ps | findstr dashboard
```

**Should show:** `ddn-dashboard-ui` container

---

### Step 6: Check Logs

```cmd
docker-compose logs dashboard-ui
```

**Look for:** No errors, successful startup messages

---

### Step 7: Open Browser

```cmd
start http://localhost:3000
```

**Or manually open:** `http://localhost:3000`

---

### Step 8: Verify Dashboard Loaded

**You should see:**
- DDN AI Test Failure Analysis Dashboard
- Navigation working
- No error messages

✅ **SUCCESS!**

**To stop:**
```cmd
docker-compose down
```

---

## ❌ Troubleshooting

### Problem: "npm: command not found"

**Fix:** Install Node.js from https://nodejs.org/

---

### Problem: "Cannot find module"

**Fix:**
```cmd
cd C:\DDN-AI-Project-Documentation\implementation\dashboard-ui
rm -rf node_modules
npm install
```

---

### Problem: "Port 5173 already in use"

**Fix:**
```cmd
# Find what's using it
netstat -ano | findstr :5173

# Kill the process (replace XXXX with PID from above)
taskkill /F /PID XXXX

# Try again
npm run dev
```

---

### Problem: "ECONNREFUSED" errors in browser console

**Cause:** Backend API not running (that's okay for UI testing!)

**Fix (if you want full functionality):**
```cmd
# In new terminal
cd C:\DDN-AI-Project-Documentation
docker-compose up -d dashboard-api postgres
```

---

### Problem: Blank white page

**Fix 1:** Hard refresh
- Press `Ctrl + Shift + R`

**Fix 2:** Check browser console
- Press `F12`
- Click "Console" tab
- Look for red error messages
- Share error message for help

**Fix 3:** Clear cache
- Browser settings → Clear cache
- Reload page

---

### Problem: Docker build fails

**Fix 1:** Clean and rebuild
```cmd
docker-compose down
docker-compose build --no-cache dashboard-ui
docker-compose up -d dashboard-ui
```

**Fix 2:** Check Docker has enough resources
- Docker Desktop → Settings → Resources
- RAM: At least 4GB
- Disk: At least 10GB free

---

## 📊 What Each Command Does

### `npm install`
- Downloads all dependencies
- Creates `node_modules` folder
- Only needed first time

### `npm run dev`
- Starts Vite development server
- Hot reload (changes appear instantly)
- Opens on port 5173

### `docker-compose up -d dashboard-ui`
- Builds Docker image
- Starts container in background
- Dashboard on port 3000

---

## ✅ Success Checklist

Dashboard is working when you can:

- [ ] Open browser to localhost:5173 (Node.js) or localhost:3000 (Docker)
- [ ] See "DDN AI Test Failure Analysis Dashboard" title
- [ ] Click navigation menu items (they load different pages)
- [ ] No red errors in browser console (F12)
- [ ] Pages load without crashing

**All checked?** Dashboard is running perfectly! 🎉

---

## 🎯 What to Do After Dashboard Works

### 1. Test the UI
- Click all menu items
- See the layout
- Check responsiveness

### 2. Start Backend (Optional)
```cmd
cd C:\DDN-AI-Project-Documentation
docker-compose up -d dashboard-api postgres
```

### 3. Import n8n Workflows
```cmd
docker-compose up -d n8n
# Open: http://localhost:5678
```

### 4. Test Full System
Follow: [START-HERE.md](START-HERE.md:1)

---

## 🆘 Still Not Working?

**Tell me:**

1. **What command did you run?**
   ```
   (paste the command here)
   ```

2. **What error did you see?**
   ```
   (paste error message here)
   ```

3. **What does CHECK-SYSTEM.bat show?**
   ```
   (run CHECK-SYSTEM.bat and share results)
   ```

---

## 📞 Quick Commands Reference

### Check System
```cmd
CHECK-SYSTEM.bat
```

### Node.js Method
```cmd
cd C:\DDN-AI-Project-Documentation\implementation\dashboard-ui
npm install
npm run dev
# Open: http://localhost:5173
```

### Docker Method
```cmd
cd C:\DDN-AI-Project-Documentation
docker-compose up -d dashboard-ui
# Open: http://localhost:3000
```

### Stop
```cmd
# Node.js: Press Ctrl+C

# Docker:
docker-compose down
```

---

**Most common issue:** Node.js not installed. Install from https://nodejs.org/ and try again!

**Last Updated:** October 22, 2025
