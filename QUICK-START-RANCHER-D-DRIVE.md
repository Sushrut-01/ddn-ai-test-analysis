# Quick Start: Rancher Desktop on D: Drive

This guide will help you set up Rancher Desktop with **ALL storage strictly on D: drive**.

## ⚡ Super Quick Start (Automated)

### Option 1: Run Master Script (Recommended)

```powershell
# Open PowerShell and navigate to project root
cd C:\DDN-AI-Project-Documentation

# Run the master setup script
.\scripts\rancher-setup\SETUP-RANCHER-ON-D-DRIVE.ps1
```

**This single script does everything:**
- ✅ Creates D: drive directory structure
- ✅ Installs Rancher Desktop
- ✅ Moves WSL2 to D: drive
- ✅ Configures all storage on D: drive
- ✅ Updates docker-compose files
- ✅ Tests deployment
- ✅ Creates management tools
- ✅ Generates documentation

**Time:** 2-3 hours (mostly waiting for downloads/initialization)

---

### Option 2: Manual Step-by-Step

If you prefer to understand each step:

```powershell
# Navigate to project root
cd C:\DDN-AI-Project-Documentation

# Phase 1: Create D: drive structure
.\scripts\rancher-setup\01-create-d-drive-structure.ps1

# Phase 2: Install Rancher Desktop
.\scripts\rancher-setup\02-install-rancher-desktop.ps1

# Phase 3: Move WSL2 to D: drive (REQUIRES ADMINISTRATOR)
# Right-click PowerShell -> Run as Administrator
.\scripts\rancher-setup\03-move-wsl-to-d-drive.ps1

# Phase 4: Configure storage
.\scripts\rancher-setup\04-configure-storage-locations.ps1

# Phase 5: Update docker-compose
.\scripts\rancher-setup\05-update-docker-compose.ps1

# Phase 6: Configure .env and deploy
notepad .env  # Add your API keys
.\scripts\rancher-setup\06-test-deployment.ps1

# Phase 7-8: Create tools and docs
.\scripts\rancher-setup\07-create-management-scripts.ps1
.\scripts\rancher-setup\08-create-documentation.ps1
```

---

## 📋 Prerequisites

### Before You Start

- [ ] **D: drive exists** with at least 50GB free space
- [ ] **Windows 10/11** with WSL2 enabled
- [ ] **Administrator access** (needed for WSL2 migration)
- [ ] **Internet connection** (for downloads)

### Enable WSL2 (if not already enabled)

```powershell
# Run as Administrator
wsl --install

# Restart computer
```

---

## 🎯 What Gets Installed Where

### D: Drive Layout (STRICT MODE)

```
D:\
├── rancher-storage\                   # Main storage directory
│   ├── k3s-data\                      # Kubernetes/K3s data
│   ├── docker-images\                 # All Docker images
│   ├── volumes\                       # Container volumes
│   │   ├── mongodb-data\              # MongoDB database files
│   │   ├── postgres-data\             # PostgreSQL database files
│   │   ├── langfuse-db-data\          # Langfuse observability DB
│   │   ├── redis-data\                # Redis cache
│   │   └── n8n-data\                  # n8n workflow data
│   └── backups\                       # Automated backups
│       ├── pre-migration-*/           # Original Docker setup backups
│       ├── config-backup-*/           # Configuration backups
│       ├── docker-compose-backup-*/   # Compose file backups
│       └── volumes-*/                 # Volume data backups
│
└── WSL-Distributions\                 # WSL2 distributions
    └── rancher-desktop\               # Rancher Desktop WSL2 instance
        └── rancher-desktop-backup.tar # Backup of WSL2 (optional to delete)
```

### C: Drive (Minimal Footprint)

```
C:\
└── Users\<YourName>\AppData\Local\Rancher Desktop\
    ├── rdctl-settings.json            # Points to D: drive
    └── docker\daemon.json             # Points to D: drive
```

**Total C: drive usage:** ~5-10GB (Rancher Desktop application only)
**Total D: drive usage:** 20-100GB+ (all data and images)

---

## ✅ Verification

### After Setup is Complete

Run these commands to verify everything is on D: drive:

```powershell
# 1. Check WSL2 location
wsl --list -v
# Should show "rancher-desktop" distribution

# 2. Verify Docker storage location
docker info | Select-String "Docker Root Dir"
# Should show: D:\rancher-storage\docker-images

# 3. Check Rancher Desktop version
rancher-desktop --version
docker --version
kubectl version --client

# 4. Verify D: drive directory structure
Get-ChildItem D:\rancher-storage -Recurse -Depth 1
Get-ChildItem D:\WSL-Distributions

# 5. Run health check
.\scripts\rancher-management\verify-setup.ps1

# 6. Check service status
docker-compose ps
```

---

## 🚀 Deploy Your Services

### Configure Environment

```powershell
# 1. Edit .env file with your credentials
notepad .env

# Required settings:
# - ANTHROPIC_API_KEY=your_key_here
# - OPENAI_API_KEY=your_key_here
# - GITHUB_TOKEN=your_token_here
# - JIRA_API_TOKEN=your_token_here
# - SLACK_BOT_TOKEN=your_token_here
```

### Start Services

```powershell
# Option 1: Start all services
docker-compose up -d

# Option 2: Start specific services
docker-compose up -d ddn-mongodb ddn-postgres ddn-langgraph

# Option 3: Use management script
.\scripts\rancher-management\manage-stack.ps1 -Action start
```

### Check Status

```powershell
# View service status
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f ddn-langgraph
```

---

## 📊 Service Access

After deployment, access services at:

| Service | URL | Purpose |
|---------|-----|---------|
| **Dashboard UI** | http://localhost:3000 | Main web interface |
| **n8n Workflows** | http://localhost:5678 | Workflow automation |
| **Langfuse** | http://localhost:3001 | LLM observability |
| **Flower** | http://localhost:5555 | Celery task monitor |
| **MongoDB** | mongodb://localhost:27017 | Database |
| **PostgreSQL** | localhost:5434 | Database |
| **Redis** | localhost:6379 | Cache |

---

## 🛠️ Daily Operations

### Common Commands

```powershell
# Start all services
docker-compose up -d

# Stop all services
docker-compose stop

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Check disk space on D: drive
Get-Volume -DriveLetter D

# Create backup
.\scripts\rancher-management\backup-volumes.ps1
```

### Management Scripts

```powershell
# Health check
.\scripts\rancher-management\verify-setup.ps1

# Backup volumes
.\scripts\rancher-management\backup-volumes.ps1 -Full

# Manage services
.\scripts\rancher-management\manage-stack.ps1 -Action status
.\scripts\rancher-management\manage-stack.ps1 -Action logs

# Cleanup unused resources
.\scripts\rancher-management\cleanup.ps1
```

---

## 🔧 Troubleshooting

### Rancher Desktop Won't Start

```powershell
# Check WSL2
wsl --list -v

# Restart WSL2
wsl --shutdown

# Start Rancher Desktop from Start Menu
```

### Services Won't Start

```powershell
# Check logs
docker-compose logs [service-name]

# Verify .env file
notepad .env

# Check port conflicts
netstat -ano | findstr :27017  # Example for MongoDB
```

### Out of Disk Space on D:

```powershell
# Check usage
docker system df

# Cleanup
.\scripts\rancher-management\cleanup.ps1

# Remove old backups
Remove-Item -Path "D:\rancher-storage\backups\*" -Recurse -Force
```

### Docker Can't Find D: Drive

```powershell
# Verify D: drive is accessible
Test-Path D:\

# Check from WSL
wsl -d rancher-desktop -- ls /mnt/d/

# Restart Rancher Desktop
```

---

## 📚 Documentation

After setup, refer to these files:

- **[RANCHER-SETUP.md](RANCHER-SETUP.md)** - Complete setup and operations guide
- **[RANCHER-QUICK-REF.md](RANCHER-QUICK-REF.md)** - Quick command reference
- **[scripts/rancher-management/README.md](scripts/rancher-management/README.md)** - Management scripts documentation

---

## 🎯 Key Differences from Docker Desktop

| Feature | Docker Desktop | Rancher Desktop (D: Drive) |
|---------|----------------|----------------------------|
| **License** | Paid (business >250 employees) | **100% Free** |
| **C: Drive Usage** | 50-100GB+ | **5-10GB only** |
| **D: Drive Usage** | None | **All data here** |
| **Container Runtime** | dockerd only | dockerd (Docker compatible) |
| **Kubernetes** | Optional | **Built-in K3s** |
| **CLI Tools** | docker, docker-compose | docker, docker-compose, kubectl |

---

## 💾 Backup Strategy

### Automated Backups

```powershell
# Create backup (services keep running)
.\scripts\rancher-management\backup-volumes.ps1

# Full backup (stops services for consistency)
.\scripts\rancher-management\backup-volumes.ps1 -Full
```

**Backup location:** `D:\rancher-storage\backups\volumes-[timestamp]`

### What Gets Backed Up

- ✅ MongoDB data
- ✅ PostgreSQL data
- ✅ Langfuse database
- ✅ Redis data
- ✅ n8n workflows

### Recommended Schedule

- **Daily:** Live backups (no service interruption)
- **Weekly:** Full backups (with service stop)
- **Before updates:** Always create a backup

---

## ⚠️ Important Notes

### Administrator Rights

**Phase 3** (WSL2 migration) **REQUIRES Administrator privileges**:
1. Right-click PowerShell
2. Select "Run as Administrator"
3. Navigate back to project directory
4. Run script 03

### Disk Space Monitoring

Monitor D: drive space regularly:

```powershell
# Check space
Get-Volume -DriveLetter D

# Docker disk usage
docker system df

# Cleanup when needed
.\scripts\rancher-management\cleanup.ps1
```

### First Launch of Rancher Desktop

After installation, Rancher Desktop takes **5-10 minutes** to initialize:
- Downloads Kubernetes images
- Sets up WSL2 distribution
- Configures networking

**Be patient!** Don't force-close during initialization.

---

## 🆘 Getting Help

### Health Check First

Always start with:
```powershell
.\scripts\rancher-management\verify-setup.ps1
```

### Common Issues Resolved

1. **"D: drive not found"** → Verify drive is mounted in Disk Management
2. **"WSL2 not installed"** → Run `wsl --install` and restart
3. **"Permission denied"** → Run PowerShell as Administrator
4. **"Out of space"** → Run cleanup script or free up D: drive

### Log Files

Check logs when troubleshooting:
```powershell
# All service logs
docker-compose logs

# Specific service
docker-compose logs ddn-mongodb

# Rancher Desktop logs
Get-Content "$env:LOCALAPPDATA\Rancher Desktop\logs\*"
```

---

## ✨ Success Criteria

Your setup is successful when:

- ✅ `wsl --list -v` shows `rancher-desktop` distribution
- ✅ `docker info` shows D: drive as Docker Root Dir
- ✅ `docker-compose ps` shows services running
- ✅ D:\rancher-storage\ contains data directories
- ✅ D:\WSL-Distributions\ contains rancher-desktop
- ✅ C: drive usage is minimal (5-10GB only)
- ✅ All services accessible via configured ports

---

## 🎉 Next Steps After Setup

1. **Verify .env configuration**
   ```powershell
   notepad .env
   ```

2. **Start your services**
   ```powershell
   docker-compose up -d
   ```

3. **Access the dashboard**
   ```
   http://localhost:3000
   ```

4. **Create your first backup**
   ```powershell
   .\scripts\rancher-management\backup-volumes.ps1
   ```

5. **Set up regular maintenance**
   - Weekly backups
   - Monthly cleanup
   - Regular health checks

---

**Installation Date:** [Auto-generated during setup]
**Storage Mode:** STRICT D: DRIVE ONLY
**License:** 100% Free & Open Source (Apache 2.0)
