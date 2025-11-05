# Langfuse Installation - Step-by-Step Tasks

**Goal:** Replace LangSmith references with Langfuse (open-source, free)
**Estimated Time:** 1-2 hours (mostly Docker installation)
**Cost:** $0

---

## Prerequisites Checklist

Before starting, verify:

- [ ] Windows 10/11 with WSL2 enabled
- [ ] Administrator access to install Docker
- [ ] 2GB+ free RAM
- [ ] 2GB+ free disk space
- [ ] Internet connection (for Docker image download)

---

## Phase 1: Install Docker Desktop (30-45 minutes)

### Task 1.1: Download Docker Desktop
**Time:** 5 minutes

- [ ] Go to: https://www.docker.com/products/docker-desktop/
- [ ] Click "Download for Windows"
- [ ] Wait for download (~500MB)

### Task 1.2: Install WSL2 (if not already installed)
**Time:** 10 minutes + reboot

- [ ] Open PowerShell as Administrator
- [ ] Run: `wsl --install`
- [ ] Reboot computer
- [ ] Verify: `wsl --list --verbose`

### Task 1.3: Install Docker Desktop
**Time:** 10 minutes

- [ ] Run Docker Desktop installer
- [ ] Accept license agreement
- [ ] Use WSL2 backend (recommended)
- [ ] Complete installation
- [ ] Start Docker Desktop

### Task 1.4: Verify Docker Installation
**Time:** 2 minutes

```bash
# Open PowerShell or CMD
docker --version
docker compose version
```

**Expected output:**
```
Docker version 24.0.x, build xxxxx
Docker Compose version v2.x.x
```

- [ ] Docker version displayed correctly
- [ ] Docker Compose version displayed correctly
- [ ] Docker Desktop running (whale icon in system tray)

---

## Phase 2: Set Up Langfuse (15 minutes)

### Task 2.1: Create Docker Compose File
**Time:** 3 minutes

- [ ] Create file: `C:\DDN-AI-Project-Documentation\docker-compose-langfuse.yml`
- [ ] Copy content from [LANGFUSE-SETUP-GUIDE.md](LANGFUSE-SETUP-GUIDE.md#step-2-create-langfuse-docker-configuration)
- [ ] Save file

### Task 2.2: Start Langfuse Containers
**Time:** 5-10 minutes (first time downloads images)

```bash
cd C:\DDN-AI-Project-Documentation
docker compose -f docker-compose-langfuse.yml up -d
```

- [ ] Docker images downloaded successfully
- [ ] Containers started successfully
- [ ] Check status: `docker ps`

### Task 2.3: Verify Langfuse is Running
**Time:** 2 minutes

- [ ] Open browser: http://localhost:3000
- [ ] Langfuse login page appears
- [ ] No errors in console

---

## Phase 3: Configure Langfuse (10 minutes)

### Task 3.1: Create Langfuse Account
**Time:** 3 minutes

- [ ] Click "Sign Up" on http://localhost:3000
- [ ] Enter email: (any email, it's local)
- [ ] Enter password: (choose strong password)
- [ ] Click "Sign Up"
- [ ] Verify account created

### Task 3.2: Create Organization and Project
**Time:** 2 minutes

- [ ] Organization name: "DDN AI Analysis"
- [ ] Click "Create"
- [ ] Project name: "ddn-ai-analysis"
- [ ] Click "Create"

### Task 3.3: Get API Keys
**Time:** 3 minutes

- [ ] Click profile → Settings
- [ ] Click "API Keys" in sidebar
- [ ] Click "Create API Key"
- [ ] Name: "DDN AI System"
- [ ] Click "Create"
- [ ] Copy **Public Key** (pk-lf-...)
- [ ] Copy **Secret Key** (sk-lf-...)
- [ ] Save keys securely (you won't see secret key again!)

### Task 3.4: Update .env File
**Time:** 2 minutes

Update `C:\DDN-AI-Project-Documentation\.env.MASTER`:

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-your-copied-public-key-here
LANGFUSE_SECRET_KEY=sk-lf-your-copied-secret-key-here
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_ENABLED=true
```

- [ ] Public key updated
- [ ] Secret key updated
- [ ] File saved

- [ ] Copy to `implementation/.env`:
  ```bash
  cp .env.MASTER implementation/.env
  ```

---

## Phase 4: Install Python SDK (5 minutes)

### Task 4.1: Update requirements.txt
**Time:** 1 minute

Edit `implementation/requirements.txt`:

Change:
```python
# Monitoring & Tracing (Phase 8)
langsmith>=0.4.39
```

To:
```python
# Monitoring & Tracing (Phase 8)
langfuse>=2.0.0
```

- [ ] requirements.txt updated
- [ ] File saved

### Task 4.2: Install Langfuse Package
**Time:** 3 minutes

```bash
cd implementation
python -m pip install langfuse>=2.0.0
```

- [ ] Package installed successfully
- [ ] No errors

### Task 4.3: Verify Installation
**Time:** 1 minute

```python
python -c "from langfuse import Langfuse; print('✅ Langfuse installed!')"
```

- [ ] "✅ Langfuse installed!" displayed
- [ ] No import errors

---

## Phase 5: Update Code (20 minutes)

### Task 5.1: Create Langfuse Tracing Module
**Time:** 5 minutes

- [ ] Create file: `implementation/langfuse_tracing.py`
- [ ] Copy code from [LANGFUSE-SETUP-GUIDE.md](LANGFUSE-SETUP-GUIDE.md#step-8-update-python-code)
- [ ] Save file

### Task 5.2: Update langgraph_agent.py
**Time:** 5 minutes

Add at top of `implementation/langgraph_agent.py`:

```python
# Import Langfuse tracing
try:
    from langfuse_tracing import trace
    TRACING_ENABLED = True
except ImportError:
    TRACING_ENABLED = False
    def trace(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else decorator(args[0])
```

Add decorator to analyze endpoint:

```python
@trace(name="analyze_error")
@app.route('/analyze-error', methods=['POST'])
def analyze_error_endpoint():
    # existing code
```

- [ ] Imports added
- [ ] Decorator added
- [ ] File saved

### Task 5.3: Update ai_analysis_service.py
**Time:** 5 minutes

Add at top of `implementation/ai_analysis_service.py`:

```python
# Import Langfuse tracing
try:
    from langfuse_tracing import trace
    TRACING_ENABLED = True
except ImportError:
    TRACING_ENABLED = False
    def trace(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else decorator(args[0])
```

Add decorators to key functions:

```python
@trace(name="gemini_analysis")
def analyze_with_gemini(error_data):
    # existing code

@trace(name="crag_verification")
def verify_with_crag(result):
    # existing code
```

- [ ] Imports added
- [ ] Decorators added
- [ ] File saved

### Task 5.4: Update react_agent_service.py
**Time:** 5 minutes

Add at top of `implementation/agents/react_agent_service.py`:

```python
# Import Langfuse tracing
try:
    from langfuse_tracing import trace
    TRACING_ENABLED = True
except ImportError:
    TRACING_ENABLED = False
    def trace(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else decorator(args[0])
```

Add decorators to workflow nodes (optional, but recommended):

```python
@trace(name="classification_node")
def classification_node(self, state):
    # existing code

@trace(name="reasoning_node")
def reasoning_node(self, state):
    # existing code
```

- [ ] Imports added
- [ ] Decorators added (optional)
- [ ] File saved

---

## Phase 6: Test Integration (10 minutes)

### Task 6.1: Restart Services
**Time:** 2 minutes

```bash
# Stop all running services (Ctrl+C in each terminal)

# Restart services
cd implementation
python langgraph_agent.py
# In another terminal
python ai_analysis_service.py
# In another terminal
python dashboard_api_full.py
```

- [ ] langgraph_agent.py started
- [ ] ai_analysis_service.py started
- [ ] dashboard_api_full.py started
- [ ] No errors in console

### Task 6.2: Trigger a Test Analysis
**Time:** 3 minutes

```bash
curl -X POST http://localhost:5000/analyze-error \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "test-langfuse-123",
    "error_log": "NullPointerException at line 45 in UserService.java",
    "error_message": "Null pointer exception in user service"
  }'
```

- [ ] Request sent successfully
- [ ] Response received (200 OK)
- [ ] No errors

### Task 6.3: Verify Trace in Langfuse
**Time:** 5 minutes

- [ ] Open http://localhost:3000
- [ ] Click "Traces" in sidebar
- [ ] See new trace for "analyze_error"
- [ ] Click on trace to view details
- [ ] Verify:
  - [ ] Input data visible
  - [ ] Output data visible
  - [ ] Nested traces (if any)
  - [ ] Token usage tracked
  - [ ] Latency recorded

---

## Phase 7: Update Documentation (10 minutes)

### Task 7.1: Update Project Documentation
**Time:** 5 minutes

Files to update:

- [ ] Update [PHASE-8-AND-9-COMPLETE.md](PHASE-8-AND-9-COMPLETE.md):
  - Replace LangSmith references with Langfuse
  - Update setup instructions
  - Update cost analysis

- [ ] Update [README.md](README.md) (if exists):
  - Add Langfuse setup instructions
  - Link to LANGFUSE-SETUP-GUIDE.md

### Task 7.2: Update Progress Tracker
**Time:** 3 minutes

- [ ] Open [PROGRESS-TRACKER-FINAL.csv](PROGRESS-TRACKER-FINAL.csv)
- [ ] Update Phase 8 notes to mention Langfuse
- [ ] Mark Langfuse installation as complete
- [ ] Save file

### Task 7.3: Create Quick Reference Card
**Time:** 2 minutes

Create file: `LANGFUSE-QUICK-START.md` with:

```markdown
# Langfuse Quick Start

## Start Langfuse
\`\`\`bash
docker compose -f docker-compose-langfuse.yml up -d
\`\`\`

## Stop Langfuse
\`\`\`bash
docker compose -f docker-compose-langfuse.yml down
\`\`\`

## View Dashboard
http://localhost:3000

## Logs
\`\`\`bash
docker compose -f docker-compose-langfuse.yml logs -f
\`\`\`
```

- [ ] File created
- [ ] Saved

---

## Phase 8: Cleanup (Optional, 5 minutes)

### Task 8.1: Remove LangSmith References (Optional)
**Time:** 5 minutes

Only if you want to completely remove LangSmith:

- [ ] Remove `langsmith` from requirements.txt
- [ ] Uninstall: `pip uninstall langsmith`
- [ ] Remove LangSmith env vars from `.env.MASTER` (or just disable)

**Note:** You can keep both for flexibility!

---

## Verification Checklist

Before marking complete, verify:

- [ ] ✅ Docker Desktop installed and running
- [ ] ✅ Langfuse containers running (`docker ps`)
- [ ] ✅ Langfuse dashboard accessible (http://localhost:3000)
- [ ] ✅ API keys created and saved in .env
- [ ] ✅ Python SDK installed (`pip list | grep langfuse`)
- [ ] ✅ Code updated with tracing decorators
- [ ] ✅ Services restart without errors
- [ ] ✅ Test trace appears in Langfuse dashboard
- [ ] ✅ Documentation updated

---

## Troubleshooting Guide

### Issue: Docker won't start

**Solutions:**
1. Enable WSL2: `wsl --install`
2. Enable virtualization in BIOS
3. Restart Docker Desktop
4. Check Docker Desktop settings

### Issue: Port 3000 already in use

**Solution:**
Edit `docker-compose-langfuse.yml`:
```yaml
ports:
  - "3001:3000"  # Changed from 3000:3000
```

Update `.env`:
```bash
LANGFUSE_HOST=http://localhost:3001
```

### Issue: Can't see traces

**Check:**
1. Langfuse running? `docker ps`
2. Keys correct in .env?
3. Services restarted after .env update?
4. Check logs: `docker compose -f docker-compose-langfuse.yml logs`

### Issue: Import errors

**Solution:**
```bash
cd implementation
pip install langfuse>=2.0.0
python -c "from langfuse import Langfuse; print('OK')"
```

---

## Time Estimate Summary

| Phase | Time | Critical? |
|-------|------|-----------|
| 1. Install Docker | 30-45 min | ✅ Yes |
| 2. Set Up Langfuse | 15 min | ✅ Yes |
| 3. Configure Langfuse | 10 min | ✅ Yes |
| 4. Install Python SDK | 5 min | ✅ Yes |
| 5. Update Code | 20 min | ✅ Yes |
| 6. Test Integration | 10 min | ✅ Yes |
| 7. Update Docs | 10 min | ⚠️ Recommended |
| 8. Cleanup | 5 min | ❌ Optional |
| **TOTAL** | **1-2 hours** | |

---

## Success Criteria

Installation is complete when:

1. ✅ Docker Desktop running
2. ✅ Langfuse containers running
3. ✅ Dashboard accessible at http://localhost:3000
4. ✅ Test trace visible in dashboard
5. ✅ No errors in service logs

---

## Next Steps After Installation

1. **Explore Dashboard:**
   - View all traces
   - Filter by date/status
   - Search traces
   - Create custom views

2. **Add More Tracing:**
   - Trace individual tools
   - Track specific operations
   - Monitor database queries

3. **Set Up Backups:**
   - Schedule database backups
   - Test restore process

4. **Integrate with Dashboard:**
   - Add trace links to UI
   - Show performance metrics

---

## Support

- **Documentation:** [LANGFUSE-SETUP-GUIDE.md](LANGFUSE-SETUP-GUIDE.md)
- **Official Docs:** https://langfuse.com/docs
- **GitHub Issues:** https://github.com/langfuse/langfuse/issues
- **Discord:** https://discord.gg/7NXusRtqYU

---

**Status:** Ready to start
**First Step:** Install Docker Desktop
**Estimated Total Time:** 1-2 hours
**Cost:** $0
