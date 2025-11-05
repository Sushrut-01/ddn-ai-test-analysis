# Langfuse Setup Guide - Open Source LLM Monitoring

**Status:** Ready for Installation
**Cost:** $0 (100% Free Forever)
**License:** MIT (Open Source)
**Date:** 2025-11-03

---

## Overview

Langfuse is a 100% free, open-source alternative to LangSmith for monitoring LLM applications. It provides:

- ✅ **100% FREE** - No paid plans, no limits
- ✅ **Self-hosted** - Your data stays on your machine
- ✅ **Open Source** - MIT license, full transparency
- ✅ **No external dependencies** - Works completely offline
- ✅ **Unlimited traces** - No monthly limits
- ✅ **Unlimited retention** - Keep data as long as you want

---

## What You Get with Langfuse

### Core Features

1. **Trace Tracking**
   - Every LLM call logged
   - Full input/output capture
   - Nested trace support (ReAct loops)
   - Parent-child relationships

2. **Performance Monitoring**
   - Latency tracking
   - Token usage
   - Cost calculation
   - Error rate monitoring

3. **Analytics Dashboard**
   - Real-time metrics
   - Historical trends
   - User feedback integration
   - Custom filters

4. **Prompt Management**
   - Version control for prompts
   - A/B testing
   - Rollback capabilities
   - Template management

5. **User Feedback**
   - Thumbs up/down
   - Comments
   - Issue tracking
   - Quality scoring

---

## Prerequisites

### Required Software

1. **Docker Desktop** (for Windows)
   - Download: https://www.docker.com/products/docker-desktop/
   - Free for personal use
   - ~500MB download
   - Requires Windows 10/11 with WSL2

2. **Optional: Docker Compose** (included with Docker Desktop)
   - Simplifies multi-container setup
   - Already included in Docker Desktop

### System Requirements

- **OS:** Windows 10/11, Linux, macOS
- **RAM:** 2GB minimum (4GB recommended)
- **Disk:** 2GB free space
- **Network:** Internet for initial Docker image download

---

## Installation Steps

### Step 1: Install Docker Desktop (One-Time Setup)

**For Windows:**

1. **Download Docker Desktop:**
   - Go to: https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"
   - Run the installer

2. **Install WSL2** (if not already installed):
   ```powershell
   wsl --install
   ```
   - Reboot your computer after installation

3. **Start Docker Desktop:**
   - Launch Docker Desktop from Start Menu
   - Wait for it to fully start (whale icon in system tray)

4. **Verify Installation:**
   ```bash
   docker --version
   docker compose version
   ```

**Expected output:**
```
Docker version 24.0.x, build xxxxx
Docker Compose version v2.x.x
```

---

### Step 2: Create Langfuse Docker Configuration

Create a file: `docker-compose-langfuse.yml` in your project root:

```yaml
version: '3.8'

services:
  langfuse-db:
    image: postgres:15
    container_name: langfuse-postgres
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: langfuse123
      POSTGRES_DB: langfuse
    volumes:
      - langfuse-db-data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    networks:
      - langfuse-network
    restart: unless-stopped

  langfuse-server:
    image: ghcr.io/langfuse/langfuse:latest
    container_name: langfuse-server
    depends_on:
      - langfuse-db
    environment:
      # Database connection
      DATABASE_URL: postgresql://langfuse:langfuse123@langfuse-db:5432/langfuse

      # Server configuration
      NEXTAUTH_URL: http://localhost:3000
      NEXTAUTH_SECRET: very-secret-key-change-this-in-production
      SALT: salt-change-this-in-production

      # Optional: Email for notifications (can skip for now)
      # EMAIL_FROM: noreply@yourdomain.com
      # SMTP_HOST: smtp.gmail.com
      # SMTP_PORT: 587
      # SMTP_USER: your-email@gmail.com
      # SMTP_PASSWORD: your-password

      # Telemetry (set to false for privacy)
      TELEMETRY_ENABLED: false

    ports:
      - "3000:3000"
    networks:
      - langfuse-network
    restart: unless-stopped

networks:
  langfuse-network:
    driver: bridge

volumes:
  langfuse-db-data:
```

**Save this as:** `C:\DDN-AI-Project-Documentation\docker-compose-langfuse.yml`

---

### Step 3: Start Langfuse

**Using Docker Compose:**

```bash
# Navigate to project directory
cd C:\DDN-AI-Project-Documentation

# Start Langfuse (first time will download images ~500MB)
docker compose -f docker-compose-langfuse.yml up -d

# Check if containers are running
docker ps
```

**Expected output:**
```
CONTAINER ID   IMAGE                              STATUS         PORTS
abc123...      ghcr.io/langfuse/langfuse:latest   Up 2 minutes   0.0.0.0:3000->3000/tcp
def456...      postgres:15                        Up 2 minutes   0.0.0.0:5433->5432/tcp
```

**Verify Langfuse is running:**
- Open browser: http://localhost:3000
- You should see Langfuse login page

---

### Step 4: Create Langfuse Account (First Time)

1. **Open Langfuse:** http://localhost:3000

2. **Sign Up:**
   - Click "Sign Up"
   - Email: your-email@example.com (any email works, it's local)
   - Password: (choose a strong password)
   - Click "Sign Up"

3. **Create Organization:**
   - Organization name: "DDN AI Analysis"
   - Click "Create"

4. **Create Project:**
   - Project name: "ddn-ai-analysis"
   - Click "Create"

---

### Step 5: Get API Keys

1. **Go to Settings:**
   - Click on your profile (top right)
   - Click "Settings"

2. **Navigate to API Keys:**
   - Click "API Keys" in left sidebar

3. **Create New API Key:**
   - Click "Create API Key"
   - Name: "DDN AI System"
   - Click "Create"

4. **Copy Keys:**
   - **Public Key:** `pk-lf-...` (copy this)
   - **Secret Key:** `sk-lf-...` (copy this)
   - ⚠️ **Save these keys securely** - you won't see the secret key again!

---

### Step 6: Configure Your Application

**Update `.env` file:**

```bash
# ============================================================================
# LANGFUSE MONITORING (Phase 8 - Open Source Alternative)
# ============================================================================
#
# Langfuse is a 100% free, open-source LLM monitoring platform
#
# BENEFITS:
# - 100% FREE forever (no paid plans)
# - Self-hosted (your data stays local)
# - Unlimited traces and retention
# - Full privacy and control
#
# SETUP:
# 1. Start Langfuse: docker compose -f docker-compose-langfuse.yml up -d
# 2. Open http://localhost:3000
# 3. Create account and project
# 4. Copy API keys below
#

# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key-here
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key-here
LANGFUSE_HOST=http://localhost:3000

# Enable tracing
LANGFUSE_ENABLED=true

# Optional: Set project name (if you created multiple projects)
LANGFUSE_PROJECT=ddn-ai-analysis
```

---

### Step 7: Install Python SDK

**Add to requirements.txt:**

```bash
# Monitoring & Tracing (Phase 8)
langfuse>=2.0.0
```

**Install:**

```bash
cd implementation
python -m pip install langfuse>=2.0.0
```

---

### Step 8: Update Python Code

**Add Langfuse to your services:**

**File: `implementation/langfuse_tracing.py`** (create new file)

```python
"""
Langfuse Tracing Module
Centralized configuration for Langfuse monitoring
"""

import os
from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context

# Load environment
load_dotenv()

# Initialize Langfuse client
langfuse_client = None
LANGFUSE_ENABLED = os.getenv('LANGFUSE_ENABLED', 'false').lower() == 'true'

if LANGFUSE_ENABLED:
    try:
        langfuse_client = Langfuse(
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            host=os.getenv('LANGFUSE_HOST', 'http://localhost:3000')
        )
        print("✅ Langfuse tracing enabled")
    except Exception as e:
        print(f"⚠️ Langfuse initialization failed: {e}")
        LANGFUSE_ENABLED = False
else:
    print("ℹ️ Langfuse tracing disabled")

# Export decorator for easy use
trace = observe if LANGFUSE_ENABLED else lambda f: f

def get_langfuse_client():
    """Get Langfuse client instance"""
    return langfuse_client

def is_enabled():
    """Check if Langfuse is enabled"""
    return LANGFUSE_ENABLED
```

**Update your services to use Langfuse:**

**Example: `langgraph_agent.py`**

```python
from langfuse_tracing import trace

@trace(name="analyze_error")
def analyze_error_endpoint():
    """Trace the entire error analysis"""
    # Your existing code
    result = react_agent.analyze(...)
    return result
```

**Example: `ai_analysis_service.py`**

```python
from langfuse_tracing import trace

@trace(name="gemini_analysis")
def analyze_with_gemini(error_data):
    """Trace Gemini API calls"""
    # Your existing code
    response = model.generate_content(...)
    return response
```

---

## Using Langfuse Dashboard

### View Traces

1. **Open Dashboard:** http://localhost:3000

2. **Navigate to Traces:**
   - Click "Traces" in sidebar
   - See all your LLM calls

3. **Inspect a Trace:**
   - Click on any trace
   - See full details:
     - Input/output
     - Token usage
     - Latency
     - Nested operations

### Monitor Performance

1. **Dashboard Overview:**
   - Total requests
   - Average latency
   - Token usage
   - Cost breakdown

2. **Filter Traces:**
   - By date range
   - By status (success/error)
   - By user
   - By operation type

3. **Search:**
   - Search by input/output content
   - Find specific errors
   - Track specific users

---

## Managing Langfuse

### Start/Stop Langfuse

```bash
# Start
docker compose -f docker-compose-langfuse.yml up -d

# Stop
docker compose -f docker-compose-langfuse.yml down

# Stop and remove data (careful!)
docker compose -f docker-compose-langfuse.yml down -v

# View logs
docker compose -f docker-compose-langfuse.yml logs -f

# Restart
docker compose -f docker-compose-langfuse.yml restart
```

### Update Langfuse

```bash
# Pull latest version
docker compose -f docker-compose-langfuse.yml pull

# Restart with new version
docker compose -f docker-compose-langfuse.yml up -d
```

### Backup Data

**Database backup:**

```bash
# Backup database
docker exec langfuse-postgres pg_dump -U langfuse langfuse > langfuse_backup.sql

# Restore database
docker exec -i langfuse-postgres psql -U langfuse langfuse < langfuse_backup.sql
```

### Check Status

```bash
# Check if containers are running
docker ps | grep langfuse

# Check container health
docker compose -f docker-compose-langfuse.yml ps

# View resource usage
docker stats langfuse-server langfuse-postgres
```

---

## Troubleshooting

### Issue: Can't access http://localhost:3000

**Solutions:**

1. **Check if containers are running:**
   ```bash
   docker ps
   ```

2. **Check logs:**
   ```bash
   docker compose -f docker-compose-langfuse.yml logs langfuse-server
   ```

3. **Restart:**
   ```bash
   docker compose -f docker-compose-langfuse.yml restart
   ```

4. **Port conflict:**
   - Another service using port 3000?
   - Change port in docker-compose file: `"3001:3000"`

### Issue: Database connection error

**Solution:**

```bash
# Restart database
docker compose -f docker-compose-langfuse.yml restart langfuse-db

# Check database logs
docker compose -f docker-compose-langfuse.yml logs langfuse-db
```

### Issue: Python SDK not connecting

**Check:**

1. **Keys correct in .env?**
   - Public key starts with `pk-lf-`
   - Secret key starts with `sk-lf-`

2. **Langfuse running?**
   ```bash
   curl http://localhost:3000/api/public/health
   ```

3. **Test connection:**
   ```python
   from langfuse import Langfuse

   client = Langfuse(
       public_key="pk-lf-...",
       secret_key="sk-lf-...",
       host="http://localhost:3000"
   )

   # Create a test trace
   trace = client.trace(name="test")
   print("✅ Connected!")
   ```

---

## Cost Comparison

| Feature | Langfuse (Free) | LangSmith (Paid) |
|---------|-----------------|------------------|
| **Monthly Cost** | $0 | $50-200 |
| **Traces/month** | Unlimited | 5K-500K |
| **Data Retention** | Unlimited | 14-90 days |
| **Self-hosted** | ✅ Yes | ❌ No |
| **Open Source** | ✅ Yes | ❌ No |
| **Privacy** | ✅ Full control | ⚠️ Cloud |
| **Setup Time** | 30 min | 5 min |
| **Maintenance** | You manage | They manage |

**For your usage (150 traces/month):**
- **Langfuse:** $0/month, unlimited retention
- **LangSmith:** $0/month (free tier), 14-day retention

**For heavy usage (100K traces/month):**
- **Langfuse:** $0/month
- **LangSmith:** $200/month

---

## Next Steps

### After Installation

1. **Test Integration:**
   - Run an error analysis
   - Check Langfuse dashboard
   - Verify traces appear

2. **Configure Dashboards:**
   - Set up custom views
   - Create filters
   - Bookmark important queries

3. **Enable User Feedback:**
   - Add feedback buttons to UI
   - Track quality scores
   - Iterate on prompts

4. **Set Up Backups:**
   - Schedule daily database backups
   - Store backups securely
   - Test restore process

### Optional Enhancements

1. **Add More Tracing:**
   - Trace individual tool calls
   - Track reasoning steps
   - Monitor database queries

2. **Custom Metrics:**
   - Add business metrics
   - Track user satisfaction
   - Monitor SLA compliance

3. **Integration:**
   - Connect to your dashboard
   - Add to monitoring stack
   - Set up alerts

---

## Resources

- **Official Docs:** https://langfuse.com/docs
- **GitHub:** https://github.com/langfuse/langfuse
- **Discord Community:** https://discord.gg/7NXusRtqYU
- **Docker Hub:** https://hub.docker.com/r/langfuse/langfuse

---

## Summary

**Langfuse provides:**
- ✅ 100% free, unlimited tracing
- ✅ Self-hosted privacy and control
- ✅ Open source transparency
- ✅ Production-ready monitoring
- ✅ Easy Docker deployment

**Total cost:** $0
**Setup time:** ~30 minutes
**Maintenance:** Minimal (Docker handles it)

**You're getting enterprise-grade LLM monitoring for free!**

---

**Status:** Ready for installation after Docker is set up
**Next:** Install Docker Desktop, then follow this guide
