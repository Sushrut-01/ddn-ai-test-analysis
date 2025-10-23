# 🚀 One-Command Setup

**Get your entire DDN AI System running with a single command**

---

## Windows (Easiest Way)

```cmd
COMPLETE-SETUP-WIZARD.bat
```

That's it! The wizard will:
1. ✅ Check all prerequisites (Docker, Python, Git)
2. ✅ Help you configure API keys
3. ✅ Test MongoDB Atlas connection
4. ✅ Build Docker images
5. ✅ Start all 13 services
6. ✅ Perform health checks
7. ✅ Open Dashboard in browser

**Time:** 10 minutes (mostly waiting for Docker)

---

## Linux/Mac

```bash
chmod +x COMPLETE-SETUP-WIZARD.sh
./COMPLETE-SETUP-WIZARD.sh
```

Same features as Windows version!

---

## What You'll Be Asked

### 1. MongoDB Atlas Connection String

**Get from:** https://cloud.mongodb.com/v2/68dc1c4495ae3e552cffaa08

**Format:**
```
mongodb+srv://username:password@cluster.mongodb.net/
```

**Or press Enter** to use local MongoDB (Docker will handle it)

---

### 2. Anthropic API Key (Required)

**Get from:** https://console.anthropic.com/

**Format:**
```
sk-ant-xxxxxxxxxxxxxxxxxxxxx
```

**Used for:** Claude AI analysis

---

### 3. OpenAI API Key (Required)

**Get from:** https://platform.openai.com/api-keys

**Format:**
```
sk-xxxxxxxxxxxxxxxxxxxxx
```

**Used for:** Embeddings and vectorization

---

### 4. Pinecone API Key (Required)

**Get from:** https://www.pinecone.io/

**Format:**
```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Used for:** Vector similarity search (RAG)

---

### 5. GitHub Token (Optional)

**Get from:** https://github.com/settings/tokens

**Format:**
```
ghp_xxxxxxxxxxxxxxxxxxxxx
```

**Used for:** Self-healing features

---

## After Setup Completes

The wizard will automatically:

✅ Create `.env` file with your configuration
✅ Test MongoDB connection (if Atlas is used)
✅ Build all Docker images
✅ Start 13 services
✅ Run health checks
✅ Show you access URLs

**You'll see:**
```
========================================
System Ready!
========================================

Access Points:
 - Dashboard UI:  http://localhost:3000
 - n8n Workflows: http://localhost:5678 (admin/password)
 - Dashboard API: http://localhost:5005

========================================
```

---

## What Gets Started

When wizard completes, you'll have 13 services running:

| Service | Port | Status |
|---------|------|--------|
| Dashboard UI | 3000 | ✅ Running |
| Dashboard API | 5005 | ✅ Running |
| n8n | 5678 | ✅ Running |
| LangGraph | 5000 | ✅ Running |
| MongoDB | 27017 | ✅ Running |
| PostgreSQL | 5432 | ✅ Running |
| Manual Trigger API | 5004 | ✅ Running |
| Pinecone Service | 5003 | ✅ Running |
| MCP MongoDB | 5001 | ✅ Running |
| MCP GitHub | 5002 | ✅ Running |
| Jira Service | 5006 | ✅ Running |
| Slack Service | 5007 | ✅ Running |
| Self-Healing | 5008 | ✅ Running |

---

## Next Steps After Setup

### 1. Open Dashboard

```
http://localhost:3000
```

You should see the DDN AI Test Analysis Dashboard!

---

### 2. Import n8n Workflows

1. **Open:** http://localhost:5678
2. **Login:** admin / password
3. **Click:** "Workflows" → "Import from File"
4. **Import these files:**
   - `implementation/workflows/ddn_ai_complete_workflow_v2.json`
   - `implementation/workflows/workflow_2_manual_trigger.json`
   - `implementation/workflows/workflow_3_refinement.json`
5. **Activate:** Click toggle to make each workflow active (green)

---

### 3. Test Manual Trigger

1. **In Dashboard:** http://localhost:3000
2. **Click:** "Manual Trigger" tab
3. **Enter:**
   - Build ID: `TEST_12345`
   - Job Name: `DDN-Smoke-Test`
4. **Click:** "Trigger Analysis"
5. **Wait:** 15 seconds
6. **See:** AI analysis results!

---

## Troubleshooting

### Wizard stops at "Docker not found"

**Solution:**
1. Install Docker Desktop: https://www.docker.com/products/docker-desktop
2. Restart computer
3. Run wizard again

---

### Services fail to start

**Check Docker is running:**
```cmd
docker --version
docker ps
```

**View logs:**
```cmd
docker-compose logs
```

**Restart Docker Desktop and try again**

---

### MongoDB Atlas connection fails

**Check:**
1. Connection string is correct
2. Password is URL-encoded (@ → %40, # → %23, etc.)
3. Network Access allows your IP (0.0.0.0/0)
4. Database user exists with correct password

**Or skip** and use local MongoDB instead (press Enter)

---

### Dashboard doesn't load

**Wait 3-5 minutes** for all services to fully start

**Then check:**
```cmd
curl http://localhost:3000
```

**If still not working:**
```cmd
docker-compose restart dashboard-ui
```

---

## Manual Commands (If Wizard Fails)

If the wizard doesn't work, you can run manually:

### 1. Create .env

```cmd
copy .env.example .env
notepad .env
```

Add your API keys

---

### 2. Start Services

```cmd
docker-compose build
docker-compose up -d
```

---

### 3. Check Status

```cmd
docker ps
```

Should show 13 containers running

---

### 4. View Logs

```cmd
docker-compose logs -f
```

---

## Quick Commands Reference

### Start system
```cmd
COMPLETE-SETUP-WIZARD.bat
```

### Stop system
```cmd
docker-compose down
```

### Restart system
```cmd
docker-compose restart
```

### View logs
```cmd
docker-compose logs -f
```

### Check running services
```cmd
docker ps
```

### Rebuild specific service
```cmd
docker-compose build dashboard-ui
docker-compose up -d dashboard-ui
```

---

## What If I Don't Have API Keys?

### Without API Keys

You can still:
- ✅ Start the system
- ✅ See the Dashboard UI
- ✅ Test MongoDB storage
- ✅ Import n8n workflows

You **cannot:**
- ❌ Run AI analysis
- ❌ Use Claude for root cause detection
- ❌ Use RAG similarity search

**Recommendation:** Get free tier API keys:
- Anthropic: https://console.anthropic.com/ (Free trial)
- OpenAI: https://platform.openai.com/ (Free trial)
- Pinecone: https://www.pinecone.io/ (Free tier)

---

## Success Checklist

After wizard completes, verify:

- [ ] Dashboard opens at http://localhost:3000
- [ ] n8n opens at http://localhost:5678
- [ ] Dashboard API responds at http://localhost:5005/health
- [ ] `docker ps` shows 13 containers
- [ ] No errors in `docker-compose logs`

**All checked?** You're ready to use the system! 🎉

---

## Get Help

**Wizard issues:**
- Check: docker --version (need 20.10+)
- Check: docker-compose --version (need 2.0+)
- Restart Docker Desktop

**Service issues:**
- View logs: docker-compose logs -f
- Check ports: netstat -ano | findstr :3000
- Restart: docker-compose restart

**MongoDB issues:**
- Test: python test-mongodb-atlas.py
- Check connection string in .env
- Verify Network Access in Atlas

**Documentation:**
- [START-HERE.md](START-HERE.md)
- [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)
- [FINAL-CHECKLIST.md](FINAL-CHECKLIST.md)

---

## Summary

**To get everything running:**

1. **Run:** `COMPLETE-SETUP-WIZARD.bat` (Windows) or `./COMPLETE-SETUP-WIZARD.sh` (Linux/Mac)
2. **Answer** questions (API keys, MongoDB connection)
3. **Wait** 5-10 minutes for setup
4. **Access:** http://localhost:3000

**That's it!** The wizard handles everything else automatically.

---

**Time to setup:** 10 minutes
**Commands needed:** 1
**Difficulty:** Super Easy ⭐
**Status:** Ready to run! 🚀

---

**Last Updated:** October 22, 2025
**Maintained by:** Rysun Labs Development Team
