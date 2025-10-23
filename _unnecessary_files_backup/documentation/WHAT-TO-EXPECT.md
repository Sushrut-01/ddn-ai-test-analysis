# What to Expect When Running START-DASHBOARD-ONLY.bat

**Here's exactly what should happen when you run the script:**

---

## ✅ If Everything Works (Best Case)

### You'll See:

```
========================================
Starting DDN AI Dashboard (Standalone)
========================================

This will start ONLY the dashboard UI for testing.
For full system, use COMPLETE-SETUP-WIZARD.bat

[OK] Node.js found:
v18.x.x

Installing dependencies (first time only)...
This may take 2-3 minutes...

[OK] Dependencies installed!

Creating .env file...
[OK] .env file created

========================================
Starting Dashboard Development Server
========================================

The dashboard will be available at:

   http://localhost:5173

Note: Port 5173 is Vite's default dev server port

Press Ctrl+C to stop the server
========================================

  VITE v5.x.x  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### What to Do:
1. **Hold Ctrl and click** the `http://localhost:5173/` link
2. **OR** open browser and go to: `http://localhost:5173`
3. You should see the dashboard!

---

## ❌ If Node.js Not Installed

### You'll See:

```
[X] Node.js not found!

Please install Node.js from: https://nodejs.org/
Then run this script again.
Press any key to continue . . .
```

### What to Do:
1. Go to: https://nodejs.org/
2. Click "Download LTS" (left button)
3. Run installer
4. **Important:** Restart your terminal
5. Run `START-DASHBOARD-ONLY.bat` again

---

## ⚠️ If npm install Fails

### You Might See:

```
Installing dependencies...
npm ERR! code ENOENT
npm ERR! syscall open
npm ERR! path C:\...\package.json
npm ERR! errno -4058
```

### What to Do:
1. Make sure you're in the right folder
2. Check that `package.json` exists:
   ```cmd
   cd C:\DDN-AI-Project-Documentation\implementation\dashboard-ui
   dir package.json
   ```
3. Try manual install:
   ```cmd
   npm install
   ```

---

## ⚠️ If Port 5173 is Busy

### You'll See:

```
Port 5173 is in use, trying another one...
  ➜  Local:   http://localhost:5174/
```

### What to Do:
- This is fine! Just use the port it gives you
- Open: `http://localhost:5174` (or whatever port shown)

---

## ⚠️ If Build Errors

### You Might See:

```
✘ [ERROR] Could not resolve "react"
```

### What to Do:
```cmd
cd C:\DDN-AI-Project-Documentation\implementation\dashboard-ui
rm -rf node_modules
npm install
npm run dev
```

---

## 📊 Common Scenarios

### Scenario 1: First Time Running
**Time:** 3-5 minutes (downloading dependencies)
**Normal:** Yes, npm install takes time
**What to do:** Wait patiently

### Scenario 2: Second Time Running
**Time:** 10-30 seconds
**Normal:** Yes, much faster after first time
**What to do:** Nothing, just wait

### Scenario 3: After Code Changes
**Time:** Instant (hot reload)
**Normal:** Yes, changes appear automatically
**What to do:** Nothing, just refresh browser

---

## 🎯 Success Indicators

You know it worked when you see:

✅ **In terminal:**
```
➜  Local:   http://localhost:5173/
```

✅ **In browser:**
- Page loads
- Title: "DDN AI Test Failure Analysis Dashboard"
- Navigation menu visible
- No error messages

---

## 🐛 Troubleshooting Quick Reference

### Error: "command not found: node"
**Fix:** Install Node.js from https://nodejs.org/

### Error: "EACCES: permission denied"
**Fix:** Run as administrator or use different folder

### Error: "Port already in use"
**Fix:** Close other apps using port 5173, or use different port shown

### Error: "Cannot find module"
**Fix:**
```cmd
npm install
```

### Error: "Blank page in browser"
**Fix:**
1. Check browser console (F12)
2. Hard refresh (Ctrl + Shift + R)
3. Clear cache and reload

---

## 💡 What Each Step Does

### Step 1: Check Node.js
- Verifies Node.js is installed
- Shows version number
- Stops if not found

### Step 2: Navigate to Dashboard
- Changes to: `implementation/dashboard-ui`
- This is where `package.json` lives

### Step 3: Install Dependencies
- Downloads React, Vite, etc.
- Creates `node_modules` folder
- Only happens first time

### Step 4: Create .env
- Sets API URL
- Configuration for development
- Auto-generated

### Step 5: Start Dev Server
- Runs Vite
- Hot reload enabled
- Opens port 5173

---

## 📸 Screenshots of What to Expect

### Terminal Output (Good):
```
  VITE v5.0.8  ready in 538 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.100:5173/
```

### Browser (Good):
```
╔══════════════════════════════════════════╗
║  DDN AI Test Failure Analysis Dashboard ║
╠══════════════════════════════════════════╣
║  Dashboard | Failures | Analytics | ... ║
╠══════════════════════════════════════════╣
║                                          ║
║  [Dashboard content loads here]          ║
║                                          ║
╚══════════════════════════════════════════╝
```

---

## ⏱️ Timing Guide

| Step | First Time | Next Times |
|------|-----------|------------|
| Check Node.js | 1 sec | 1 sec |
| npm install | 2-3 min | Skip |
| Start server | 10-30 sec | 10-30 sec |
| **Total** | **3-5 min** | **10-30 sec** |

---

## 🎓 Understanding the Output

### Normal Messages (Ignore These):
```
npm WARN deprecated ...
(node:xxxxx) ExperimentalWarning: ...
```

### Good Messages (Success):
```
[OK] ...
✓ ...
➜  Local: ...
ready in ...
```

### Bad Messages (Need Fixing):
```
[X] ...
npm ERR! ...
✘ [ERROR] ...
ENOENT ...
```

---

## 🔄 Starting/Stopping

### To Start:
```cmd
START-DASHBOARD-ONLY.bat
```

### To Stop:
- Press `Ctrl + C` in terminal
- Confirm with `Y` if asked

### To Restart:
1. Stop (Ctrl + C)
2. Run script again
3. Or just refresh browser (changes auto-reload)

---

## 📝 What the Script Actually Does

```batch
1. Check if Node.js exists ✓
2. Show Node.js version ✓
3. Navigate to dashboard folder ✓
4. Check if node_modules exists
   - If NO: Run npm install (first time)
   - If YES: Skip install (faster!)
5. Check if .env exists
   - If NO: Create it
   - If YES: Use existing
6. Run npm run dev ✓
7. Show URL ✓
8. Wait (keep running) ✓
```

---

## ✅ Final Checklist

After running script, verify:

- [ ] Terminal shows no red errors
- [ ] You see "Local: http://localhost:5173/"
- [ ] Browser opens that URL
- [ ] Dashboard page loads
- [ ] Navigation works
- [ ] No console errors (F12)

**All checked?** Dashboard is working! 🎉

---

## 🆘 If Nothing Above Helps

**Run diagnostics:**
```cmd
cd C:\DDN-AI-Project-Documentation
CHECK-SYSTEM.bat
```

**Share with me:**
1. Full output from CHECK-SYSTEM.bat
2. Full output from START-DASHBOARD-ONLY.bat
3. Any error messages in browser console (F12)

---

**Most common issue:** Node.js not installed. Just install it and try again!

**Last Updated:** October 22, 2025
