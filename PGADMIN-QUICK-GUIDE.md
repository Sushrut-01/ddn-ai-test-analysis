# pgAdmin 4 - OFFICIAL PostgreSQL GUI (FREE & OPEN SOURCE)

## IMPORTANT: How pgAdmin Opens

pgAdmin is a **desktop application** that opens in its own window, NOT a regular web browser port.
- It may take 30-60 seconds to start
- A pgAdmin window will appear
- It runs its own embedded browser

## Opening pgAdmin

### Method 1: Double-click the Batch File
```cmd
OPEN-PGADMIN.bat
```

### Method 2: Direct Path
```cmd
"C:\Program Files\PostgreSQL\18\pgAdmin 4\runtime\pgAdmin4.exe"
```

### Method 3: Windows Start Menu
- Click Start → Search "pgAdmin 4" → Click pgAdmin 4

## Connection Details for PostgreSQL

| Setting | Value |
|---------|-------|
| **Host** | localhost |
| **Port** | 5432 |
| **Database** | ddn_ai_analysis |
| **Username** | postgres |
| **Password** | Sharu@051220 |

## First Time Setup

1. **Open pgAdmin** (it will open in your browser)
2. **Set Master Password** (one-time, protects saved passwords)
3. **Add Server:**
   - Right-click "Servers" → Register → Server
   - General Tab: Name = "DDN Local PostgreSQL"
   - Connection Tab: Enter details above
   - Check "Save password"
   - Click "Save"

## Useful SQL Queries

### Check all tables:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';
```

### View failure analysis data:
```sql
SELECT * FROM failure_analysis ORDER BY created_at DESC LIMIT 10;
```

### Check build metadata:
```sql
SELECT * FROM build_metadata ORDER BY created_at DESC LIMIT 10;
```

### Count records in each table:
```sql
SELECT
    'failure_analysis' as table_name, COUNT(*) as count FROM failure_analysis
UNION ALL
SELECT
    'build_metadata', COUNT(*) FROM build_metadata
UNION ALL
SELECT
    'user_feedback', COUNT(*) FROM user_feedback
UNION ALL
SELECT
    'failure_patterns', COUNT(*) FROM failure_patterns
UNION ALL
SELECT
    'ai_model_metrics', COUNT(*) FROM ai_model_metrics
UNION ALL
SELECT
    'manual_trigger_log', COUNT(*) FROM manual_trigger_log;
```

## Troubleshooting

### If pgAdmin doesn't open:
- Check if it's already running in browser: http://127.0.0.1:5050
- Try running as Administrator
- Check Windows Firewall settings

### If connection fails:
- Verify PostgreSQL service is running: `net start postgresql-x64-18`
- Check password is correct: Sharu@051220
- Ensure port 5432 is not blocked

## Why pgAdmin?

- **Official PostgreSQL GUI** - Developed by the PostgreSQL team
- **100% Free and Open Source** - No cost, ever
- **Full-featured** - Complete database management capabilities
- **Already installed** - Comes with PostgreSQL installation