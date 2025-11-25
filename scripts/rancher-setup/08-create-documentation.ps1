# Phase 8: Create Documentation and Update .gitignore
# This script generates comprehensive documentation and updates .gitignore

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Create Documentation" -ForegroundColor Cyan
Write-Host "Phase 8: Documentation & Finalization" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Create main documentation
Write-Host "`nCreating RANCHER-SETUP.md..." -ForegroundColor Yellow

$documentationContent = @'
# Rancher Desktop Setup Guide - D: Drive Configuration

This document describes the Rancher Desktop setup for the DDN AI Test Failure Analysis System, with all storage configured on D: drive.

## Overview

This project has been configured to use **Rancher Desktop** instead of Docker Desktop, with all data and storage located on the **D: drive** to preserve C: drive space.

## System Architecture

### Storage Locations

All Rancher Desktop data is stored on D: drive:

```
D:\
├── rancher-storage\
│   ├── k3s-data\              # Kubernetes data
│   ├── docker-images\         # Container images
│   ├── volumes\               # Persistent volumes
│   │   ├── mongodb-data\      # MongoDB database
│   │   ├── postgres-data\     # PostgreSQL database
│   │   ├── langfuse-db-data\  # Langfuse database
│   │   ├── redis-data\        # Redis cache
│   │   └── n8n-data\          # n8n workflows
│   └── backups\               # Automated backups
└── WSL-Distributions\
    └── rancher-desktop\       # WSL2 distribution
```

### Services

The system runs 11-15 containerized services:

**Databases:**
- MongoDB 7.0 (port 27017)
- PostgreSQL 16 (port 5434)
- PostgreSQL 15 for Langfuse (port 5433)
- Redis (port 6379)

**Workflow & Orchestration:**
- n8n (port 5678)

**AI Services:**
- LangGraph Classification Service (port 5003/5000)
- Celery Worker (background tasks)
- Manual Trigger API (port 5004)

**MCP Servers:**
- MongoDB MCP Server (port 5001)
- GitHub MCP Server (port 5002)

**Integration Services:**
- Dashboard API (port 5006/5005)
- Dashboard UI (port 3000)
- Jira Integration (port 5007)
- Slack Integration (port 5008)
- Self-Healing Service (port 5009)

**Observability:**
- Langfuse (port 3001)
- Flower (port 5555)

## Prerequisites

- Windows 10/11 with WSL2 enabled
- At least 50GB free space on D: drive
- Administrative privileges
- Internet connection for downloads

## Installation

### Quick Start

Run the setup scripts in order:

```powershell
# 1. Document current Docker setup (if migrating)
.\scripts\rancher-setup\00-document-current-setup.ps1

# 2. Create D: drive directory structure
.\scripts\rancher-setup\01-create-d-drive-structure.ps1

# 3. Install Rancher Desktop
.\scripts\rancher-setup\02-install-rancher-desktop.ps1

# 4. Move WSL2 to D: drive (requires Administrator)
.\scripts\rancher-setup\03-move-wsl-to-d-drive.ps1

# 5. Configure storage locations
.\scripts\rancher-setup\04-configure-storage-locations.ps1

# 6. Update docker-compose files
.\scripts\rancher-setup\05-update-docker-compose.ps1

# 7. Test deployment
.\scripts\rancher-setup\06-test-deployment.ps1

# 8. Create management scripts
.\scripts\rancher-setup\07-create-management-scripts.ps1

# 9. Create documentation (this script)
.\scripts\rancher-setup\08-create-documentation.ps1
```

### Manual Installation

See [RANCHER-INSTALL.md](RANCHER-INSTALL.md) for detailed step-by-step instructions.

## Configuration

### Rancher Desktop Settings

**Container Runtime:** dockerd (moby) - Docker compatible
**Kubernetes:** Enabled (K3s)
**Kubernetes Version:** v1.29.x or newer

### Storage Configuration Files

**rdctl-settings.json** (Kubernetes data):
```
C:\Users\<user>\AppData\Local\Rancher Desktop\rdctl-settings.json
```

**daemon.json** (Docker images):
```
C:\Users\<user>\AppData\Local\Rancher Desktop\docker\daemon.json
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Core APIs
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# Databases
# Use `MONGODB_URI` to provide your MongoDB connection string (Atlas recommended).
# Example (Atlas):
# mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net/ddn_ai_project?retryWrites=true&w=majority
MONGODB_URI=mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net/ddn_ai_project?retryWrites=true&w=majority
POSTGRES_HOST=ddn-postgres
POSTGRES_PORT=5432

# Integrations
GITHUB_TOKEN=your_token_here
JIRA_URL=https://your-jira.atlassian.net
JIRA_API_TOKEN=your_token_here
SLACK_BOT_TOKEN=your_token_here

# Observability
LANGFUSE_PUBLIC_KEY=your_key_here
LANGFUSE_SECRET_KEY=your_key_here
```

## Daily Operations

### Starting the Stack

```powershell
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d ddn-mongodb ddn-postgres

# Use management script
.\scripts\rancher-management\manage-stack.ps1 -Action start
```

### Stopping the Stack

```powershell
# Stop all services
docker-compose stop

# Stop specific service
docker-compose stop ddn-mongodb

# Use management script
.\scripts\rancher-management\manage-stack.ps1 -Action stop
```

### Viewing Logs

```powershell
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f ddn-langgraph

# Use management script
.\scripts\rancher-management\manage-stack.ps1 -Action logs -Service ddn-langgraph
```

### Checking Status

```powershell
# Check service status
docker-compose ps

# Health check
.\scripts\rancher-management\verify-setup.ps1

# Use management script
.\scripts\rancher-management\manage-stack.ps1 -Action status
```

## Backup & Recovery

### Creating Backups

```powershell
# Live backup (containers running)
.\scripts\rancher-management\backup-volumes.ps1

# Full backup (stops containers for consistency)
.\scripts\rancher-management\backup-volumes.ps1 -Full
```

Backups are saved to: `D:\rancher-storage\backups\volumes-[timestamp]`

### Restoring from Backup

1. Stop all services: `docker-compose down`
2. Copy backup data to volume directories
3. Restart services: `docker-compose up -d`

## Maintenance

### Weekly Tasks

```powershell
# 1. Create backup
.\scripts\rancher-management\backup-volumes.ps1 -Full

# 2. Check health
.\scripts\rancher-management\verify-setup.ps1

# 3. Review logs for errors
.\scripts\rancher-management\manage-stack.ps1 -Action logs
```

### Monthly Tasks

```powershell
# 1. Clean up unused resources
.\scripts\rancher-management\cleanup.ps1

# 2. Update Rancher Desktop (via UI)

# 3. Update container images
docker-compose pull
docker-compose up -d
```

### Monitoring Disk Space

```powershell
# Check D: drive space
Get-Volume -DriveLetter D

# View Docker disk usage
docker system df

# Cleanup if needed
.\scripts\rancher-management\cleanup.ps1
```

## Troubleshooting

### Rancher Desktop Won't Start

1. Check if WSL2 is running: `wsl --list -v`
2. Restart WSL: `wsl --shutdown` then start Rancher Desktop
3. Check Windows Event Viewer for errors

### Services Won't Start

1. Check logs: `docker-compose logs [service-name]`
2. Verify .env configuration
3. Check port conflicts: `netstat -ano | findstr :[port]`
4. Restart services: `docker-compose restart [service-name]`

### D: Drive Not Accessible

1. Verify drive is mounted: `Test-Path D:\`
2. Check WSL mount: `wsl -d rancher-desktop -- ls /mnt/d/`
3. Restart WSL: `wsl --shutdown`

### Out of Disk Space

1. Check usage: `docker system df`
2. Clean up: `.\scripts\rancher-management\cleanup.ps1`
3. Remove old backups: `D:\rancher-storage\backups\`
4. Prune volumes (DANGEROUS): `docker volume prune`

### Performance Issues

1. Increase WSL2 memory in `.wslconfig`:
   ```
   [wsl2]
   memory=8GB
   processors=4
   ```
2. Check D: drive I/O performance
3. Reduce running services
4. Close unnecessary applications

## Useful Commands

### Docker

```powershell
# List containers
docker ps -a

# List images
docker images

# List volumes
docker volume ls

# System info
docker info

# Remove stopped containers
docker container prune

# Remove unused images
docker image prune
```

### Kubernetes

```powershell
# Get cluster info
kubectl cluster-info

# List nodes
kubectl get nodes

# List pods
kubectl get pods -A

# Get services
kubectl get svc -A
```

### WSL2

```powershell
# List distributions
wsl --list -v

# Shutdown WSL
wsl --shutdown

# Enter distribution
wsl -d rancher-desktop

# Check version
wsl --version
```

## Differences from Docker Desktop

| Feature | Docker Desktop | Rancher Desktop |
|---------|---------------|-----------------|
| **License** | Subscription required (business) | 100% Free |
| **Container Runtime** | dockerd only | dockerd OR containerd |
| **Kubernetes** | Optional | Built-in (K3s) |
| **docker-compose** | ✅ Yes | ✅ Yes |
| **CLI Tools** | docker, docker-compose | docker, docker-compose, kubectl, nerdctl |
| **GUI** | ✅ Yes | ✅ Yes |
| **Extensions** | ✅ Yes | ❌ No |

## Support & Resources

### Documentation
- [Rancher Desktop Docs](https://docs.rancherdesktop.io/)
- [K3s Documentation](https://docs.k3s.io/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

### Management Scripts
- Location: `scripts/rancher-management/`
- See: `scripts/rancher-management/README.md`

### Project Issues
- GitHub: [Your Repository Issues]
- Contact: Your team contact information

## Migration Notes

This setup was migrated from Docker Desktop on [date].

Original configuration backed up to:
- `D:\rancher-storage\backups\pre-migration-[timestamp]`

All docker-compose files have been updated to use D: drive storage paths.

## License

This setup uses:
- **Rancher Desktop:** Apache 2.0 License (Free)
- **K3s:** Apache 2.0 License (Free)
- **Docker Compose:** Apache 2.0 License (Free)

No licensing fees required for any component.
'@

Set-Content -Path "RANCHER-SETUP.md" -Value $documentationContent
Write-Host "  [+] Created: RANCHER-SETUP.md" -ForegroundColor Green

# Update .gitignore
Write-Host "`nUpdating .gitignore..." -ForegroundColor Yellow

$gitignoreAdditions = @'

# Rancher Desktop D: drive storage (do not commit)
# Note: All actual data is on D: drive, these patterns prevent
# accidental commits of local paths or temporary files

# D: drive path references (if accidentally created in project)
/D:/
D:\

# Rancher Desktop specific
.rancher/
rancher-desktop.log

# Deployment test reports
deployment-test-report.txt
'@

if (Test-Path ".gitignore") {
    $currentGitignore = Get-Content ".gitignore" -Raw

    if ($currentGitignore -notmatch "Rancher Desktop") {
        Add-Content -Path ".gitignore" -Value $gitignoreAdditions
        Write-Host "  [+] Updated .gitignore with Rancher Desktop exclusions" -ForegroundColor Green
    } else {
        Write-Host "  [~] .gitignore already contains Rancher Desktop exclusions" -ForegroundColor Gray
    }
} else {
    Write-Host "  [!] .gitignore not found" -ForegroundColor Yellow
}

# Create quick reference card
Write-Host "`nCreating quick reference card..." -ForegroundColor Yellow

$quickRefContent = @'
# Rancher Desktop Quick Reference

## Essential Commands

### Start/Stop Services
```powershell
docker-compose up -d              # Start all
docker-compose stop               # Stop all
docker-compose restart            # Restart all
```

### View Logs
```powershell
docker-compose logs -f            # All services
docker-compose logs -f [service]  # Specific service
```

### Check Status
```powershell
docker-compose ps                 # Service status
docker ps                         # Running containers
```

### Management Scripts
```powershell
.\scripts\rancher-management\verify-setup.ps1      # Health check
.\scripts\rancher-management\backup-volumes.ps1    # Backup
.\scripts\rancher-management\manage-stack.ps1      # Manage services
.\scripts\rancher-management\cleanup.ps1           # Free space
```

## Storage Locations

- **Volumes:** `D:\rancher-storage\volumes\`
- **Backups:** `D:\rancher-storage\backups\`
- **K3s Data:** `D:\rancher-storage\k3s-data\`
- **Images:** `D:\rancher-storage\docker-images\`

## Common Services

| Service | Port | Purpose |
|---------|------|---------|
| MongoDB | 27017 | Database |
| PostgreSQL | 5434 | Database |
| Redis | 6379 | Cache |
| n8n | 5678 | Workflows |
| Dashboard | 3000 | UI |
| LangGraph | 5003 | AI Service |
| Langfuse | 3001 | Observability |

## Troubleshooting

**Services won't start:**
1. Check logs: `docker-compose logs [service]`
2. Verify .env file exists and is configured
3. Check port conflicts: `netstat -ano | findstr :[port]`

**Out of space:**
1. Run cleanup: `.\scripts\rancher-management\cleanup.ps1`
2. Remove old backups from `D:\rancher-storage\backups\`

**Rancher won't start:**
1. Check WSL: `wsl --list -v`
2. Restart: `wsl --shutdown` then launch Rancher Desktop

## Daily Checklist

- [ ] Check service status: `docker-compose ps`
- [ ] Review logs for errors: `docker-compose logs`
- [ ] Monitor disk space: `Get-Volume -DriveLetter D`

## Weekly Checklist

- [ ] Create backup: `.\scripts\rancher-management\backup-volumes.ps1 -Full`
- [ ] Run health check: `.\scripts\rancher-management\verify-setup.ps1`
- [ ] Clean up: `.\scripts\rancher-management\cleanup.ps1`
'@

Set-Content -Path "RANCHER-QUICK-REF.md" -Value $quickRefContent
Write-Host "  [+] Created: RANCHER-QUICK-REF.md" -ForegroundColor Green

# Create installation summary
$summaryContent = @'
# Rancher Desktop Installation Summary

## What Was Installed

✅ **Rancher Desktop** - Container runtime and Kubernetes
✅ **WSL2 Distribution** - Moved to D:\WSL-Distributions\rancher-desktop
✅ **Storage Configuration** - All data on D: drive
✅ **Docker Compose** - Service orchestration
✅ **Management Scripts** - Automation tools

## Storage Configuration

All data is stored on **D: drive**:

```
D:\rancher-storage\
├── k3s-data\           # Kubernetes data
├── docker-images\      # Container images
├── volumes\            # Application data
│   ├── mongodb-data\
│   ├── postgres-data\
│   ├── langfuse-db-data\
│   ├── redis-data\
│   └── n8n-data\
└── backups\            # Automated backups
```

## Configuration Files

- **rdctl-settings.json:** `C:\Users\[user]\AppData\Local\Rancher Desktop\rdctl-settings.json`
- **daemon.json:** `C:\Users\[user]\AppData\Local\Rancher Desktop\docker\daemon.json`
- **.env:** Project root (configure your API keys here)

## Next Steps

1. **Configure Environment:**
   - Edit `.env` file with your API keys and credentials

2. **Start Services:**
   ```powershell
   docker-compose up -d
   ```

3. **Verify Setup:**
   ```powershell
   .\scripts\rancher-management\verify-setup.ps1
   ```

4. **Create First Backup:**
   ```powershell
   .\scripts\rancher-management\backup-volumes.ps1
   ```

## Documentation

- **Full Guide:** [RANCHER-SETUP.md](RANCHER-SETUP.md)
- **Quick Reference:** [RANCHER-QUICK-REF.md](RANCHER-QUICK-REF.md)
- **Management Scripts:** [scripts/rancher-management/README.md](scripts/rancher-management/README.md)

## Support

For issues or questions:
1. Run health check: `.\scripts\rancher-management\verify-setup.ps1`
2. Check logs: `docker-compose logs`
3. Review troubleshooting section in RANCHER-SETUP.md

---

**Installation Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Rancher Desktop Version:** [Check with: rancher-desktop --version]
**Storage Location:** D:\rancher-storage\
'@

Set-Content -Path "RANCHER-INSTALL-SUMMARY.md" -Value $summaryContent
Write-Host "  [+] Created: RANCHER-INSTALL-SUMMARY.md" -ForegroundColor Green

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Phase 8 Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nDocumentation created:" -ForegroundColor Green
Write-Host "  1. RANCHER-SETUP.md              - Complete setup guide" -ForegroundColor White
Write-Host "  2. RANCHER-QUICK-REF.md          - Quick reference card" -ForegroundColor White
Write-Host "  3. RANCHER-INSTALL-SUMMARY.md    - Installation summary" -ForegroundColor White
Write-Host "  4. .gitignore updated             - D: drive exclusions added" -ForegroundColor White

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "All Setup Scripts Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nSetup Scripts Location: scripts\rancher-setup\" -ForegroundColor Cyan
Write-Host "Management Scripts Location: scripts\rancher-management\" -ForegroundColor Cyan

Write-Host "`nTo complete the setup:" -ForegroundColor Yellow
Write-Host "1. Review RANCHER-SETUP.md for detailed information" -ForegroundColor White
Write-Host "2. Configure .env file with your API keys" -ForegroundColor White
Write-Host "3. Run verification: .\scripts\rancher-management\verify-setup.ps1" -ForegroundColor White
Write-Host "4. Deploy services: docker-compose up -d" -ForegroundColor White

Write-Host "`nPress Enter to exit..." -ForegroundColor Gray
Read-Host
