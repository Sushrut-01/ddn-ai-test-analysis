# How to Start PostgreSQL Service

## Method 1: Run Batch File as Administrator (RECOMMENDED)

### Steps:
1. **Right-click** on `START-POSTGRESQL.bat`
2. Select **"Run as administrator"**
3. Click **"Yes"** when Windows asks for permission
4. You should see: `[OK] PostgreSQL service started successfully!`

### Visual Guide:
```
START-POSTGRESQL.bat
  └─> Right-click
       └─> "Run as administrator"
            └─> Click "Yes"
```

---

## Method 2: Using Windows Services (Alternative)

If you prefer to use Windows Services Manager:

### Steps:
1. Press `Windows Key + R` to open Run dialog
2. Type: `services.msc`
3. Press Enter
4. Find service: **`postgresql-x64-18`**
5. Right-click → **Start**

### Visual Guide:
```
Win + R → services.msc → Enter
  └─> Find "postgresql-x64-18"
       └─> Right-click → Start
```

---

## Method 3: Using Command Prompt as Administrator

### Steps:
1. Press `Windows Key`
2. Type: `cmd`
3. Right-click on **"Command Prompt"**
4. Select **"Run as administrator"**
5. Run command:
   ```batch
   net start postgresql-x64-18
   ```

---

## Verify PostgreSQL is Running

After starting, verify it's running:

### Option A: Check via Services
1. Open `services.msc`
2. Find `postgresql-x64-18`
3. Status should show: **Running**

### Option B: Check via Command
```batch
# Open Command Prompt (doesn't need admin)
sc query postgresql-x64-18
```

Look for:
```
STATE              : 4  RUNNING
```

### Option C: Test Connection with Python
```bash
cd implementation
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, database='ddn_ai_analysis', user='postgres', password='Sharu@051220'); print('[OK] PostgreSQL is running!'); conn.close()"
```

---

## Common Issues

### Issue: "Service name is invalid"
- PostgreSQL might not be installed
- Service name might be different
- Check actual service name in services.msc

### Issue: "Service did not start"
- Port 5432 might be in use
- PostgreSQL installation might be corrupted
- Check PostgreSQL logs in: `C:\Program Files\PostgreSQL\18\data\log\`

### Issue: "Access Denied" (Current Issue)
- **Solution:** Run as Administrator (see Method 1 above)
- Windows requires admin privileges to start/stop services

---

## Auto-Start PostgreSQL (Optional)

To make PostgreSQL start automatically when Windows boots:

1. Open `services.msc`
2. Find `postgresql-x64-18`
3. Right-click → **Properties**
4. Change **Startup type** to: **Automatic**
5. Click **Apply** → **OK**

---

## Next Steps After Starting PostgreSQL

Once PostgreSQL is running:

1. **Verify database exists:**
   ```bash
   cd implementation
   python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, database='ddn_ai_analysis', user='postgres', password='Sharu@051220'); print('[OK] Database connection successful!'); conn.close()"
   ```

2. **Install AI packages** (next major step)

3. **Start LangGraph service:**
   ```bash
   cd implementation
   python langgraph_service.py
   ```

4. **Switch to full dashboard API:**
   ```bash
   cd implementation
   python dashboard_api.py
   ```

---

## Quick Troubleshooting

**PostgreSQL won't start?**
```batch
# Check if port 5432 is in use
netstat -ano | findstr :5432

# If port is in use, find what's using it
tasklist | findstr <PID>
```

**Forgot PostgreSQL password?**
- Your password is: `Sharu@051220`
- It's stored in: `implementation\.env`

**Need to reinstall PostgreSQL?**
- Download from: https://www.postgresql.org/download/windows/
- Use same password: `Sharu@051220`
- Select port: `5432`
