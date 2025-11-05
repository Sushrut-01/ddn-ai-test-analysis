# How to Start Redis/Memurai on Windows

**Current Status:** Redis/Memurai is installed but NOT running ❌

**Error:** Connection refused to localhost:6379

---

## Quick Fix Options

### Option 1: Start Memurai from Start Menu (Recommended)

1. **Press Windows key**
2. **Type:** "Memurai"
3. **Click:** "Memurai Server" or "Start Memurai"
4. **Verify:** A console window should open showing Redis is running

### Option 2: Start Memurai as Windows Service

Open **PowerShell as Administrator** and run:

```powershell
# Start Memurai service
Start-Service Memurai

# Verify it's running
Get-Service Memurai
```

Expected output:
```
Status   Name               DisplayName
------   ----               -----------
Running  Memurai            Memurai
```

### Option 3: Start Memurai Manually

1. **Find Memurai installation folder:**
   - Default: `C:\Program Files\Memurai\`
   - OR: `C:\Program Files (x86)\Memurai\`

2. **Run Memurai Server:**
   ```bash
   cd "C:\Program Files\Memurai"
   memurai-server.exe
   ```

3. **Leave the window open** (Redis runs in the console)

### Option 4: Use Docker (Alternative)

If Memurai isn't working, use Docker instead:

```bash
# Start Redis with Docker
docker run -d -p 6379:6379 --name redis redis:latest

# Verify it's running
docker ps | grep redis
```

---

## Verify Redis is Running

After starting Redis, run this command to verify:

```bash
python -c "import redis; r=redis.Redis(host='localhost', port=6379, db=0); print('✓ Redis is running!'); print('Version:', r.info()['redis_version'])"
```

**Expected output:**
```
✓ Redis is running!
Version: 7.x.x
```

**If you get an error:**
```
ConnectionError: Error 10061...
```
→ Redis is NOT running. Try the options above.

---

## Alternative: Install as Windows Service

If Memurai didn't install as a service, you can register it:

```bash
# Navigate to Memurai folder
cd "C:\Program Files\Memurai"

# Install as service
memurai-server.exe --service-install

# Start service
memurai-server.exe --service-start
```

---

## Troubleshooting

### Problem: "Memurai not found"
**Solution:** Memurai may not have been installed correctly.

Try Docker instead:
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

### Problem: Port 6379 already in use
**Solution:** Another Redis instance is running

```bash
# Find what's using port 6379
netstat -ano | findstr :6379

# Kill the process (replace PID)
taskkill /F /PID <pid>
```

### Problem: Service won't start
**Solution:** Check Windows Event Viewer

```bash
# Open Event Viewer
eventvwr

# Navigate to: Windows Logs → Application
# Look for Memurai errors
```

---

## After Redis is Running

Once Redis is verified, we can:

1. ✅ **Test Redis connection** (done above)
2. 🔄 **Start langgraph service** (port 5000 issue to resolve first)
3. 🧪 **Run Phase 1 tests** (Tasks 1.6-1.9)

---

## Quick Command Summary

```bash
# 1. Start Redis (choose one)
Start-Service Memurai                    # PowerShell as Admin
docker run -d -p 6379:6379 redis:latest # Docker

# 2. Verify Redis
python -c "import redis; r=redis.Redis(); print(r.ping())"

# 3. Test connection
redis-cli ping  # Should return: PONG

# 4. Check Redis stats
redis-cli info | grep used_memory_human
```

---

**Next Step:** Please start Redis using one of the methods above, then let me know when it's running!
