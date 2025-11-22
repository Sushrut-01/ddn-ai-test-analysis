# Rancher Desktop Setup Scripts

This directory contains all scripts needed to set up Rancher Desktop with D: drive storage for the DDN AI Test Failure Analysis System.

## Overview

These scripts automate the complete migration from Docker Desktop to Rancher Desktop, with all storage configured on D: drive to save C: drive space.

## Setup Scripts (Run in Order)

### 00-document-current-setup.ps1
**Purpose:** Document current Docker/Docker Desktop configuration before migration

**What it does:**
- Lists all running containers
- Documents Docker images
- Records Docker volumes
- Backs up docker-compose files
- Creates migration summary report

**Prerequisites:** Docker Desktop installed (if migrating)

**Usage:**
```powershell
.\00-document-current-setup.ps1
```

**Output:** Backup directory in `D:\rancher-storage\backups\pre-migration-[timestamp]`

---

### 01-create-d-drive-structure.ps1
**Purpose:** Create necessary directory structure on D: drive

**What it does:**
- Creates `D:\rancher-storage` and subdirectories
- Sets up volume directories for databases
- Creates backup directory
- Sets proper permissions
- Creates README in storage directory

**Prerequisites:** D: drive must exist and be accessible

**Usage:**
```powershell
.\01-create-d-drive-structure.ps1
```

**Output:**
- Directory structure on D: drive
- README.md in D:\rancher-storage

---

### 02-install-rancher-desktop.ps1
**Purpose:** Install Rancher Desktop using available package managers

**What it does:**
- Detects available installation methods (WinGet, Chocolatey, Manual)
- Guides through installation process
- Verifies installation
- Helps with initial configuration

**Prerequisites:**
- Windows 10/11
- WSL2 enabled
- Internet connection

**Usage:**
```powershell
.\02-install-rancher-desktop.ps1
```

**Installation Options:**
1. WinGet (Recommended)
2. Chocolatey
3. Manual download
4. Exit for manual installation

**Post-Installation:**
- Launch Rancher Desktop
- Choose "dockerd (moby)" as container engine
- Enable Kubernetes
- Wait for initialization (5-10 minutes)

---

### 03-move-wsl-to-d-drive.ps1
**Purpose:** Move WSL2 distribution from C: to D: drive

**What it does:**
- Stops Rancher Desktop
- Exports WSL distribution
- Unregisters original distribution
- Imports to D: drive
- Verifies new location

**Prerequisites:**
- Rancher Desktop installed and launched at least once
- **Must run as Administrator**
- At least 10GB free on D: drive

**Usage:**
```powershell
# Right-click PowerShell -> Run as Administrator
.\03-move-wsl-to-d-drive.ps1
```

**Duration:** 20-30 minutes

**Output:**
- WSL distribution at `D:\WSL-Distributions\rancher-desktop`
- Backup TAR file (optional to delete)

---

### 04-configure-storage-locations.ps1
**Purpose:** Configure Rancher Desktop to use D: drive for all storage

**What it does:**
- Stops Rancher Desktop
- Updates `rdctl-settings.json` (Kubernetes data root)
- Creates/updates `daemon.json` (Docker image storage)
- Backs up original configuration files
- Sets all storage paths to D: drive

**Prerequisites:**
- Rancher Desktop installed
- Phase 1 and 3 completed

**Usage:**
```powershell
.\04-configure-storage-locations.ps1
```

**Configuration Files Modified:**
- `rdctl-settings.json` - Kubernetes data → `D:\rancher-storage\k3s-data`
- `daemon.json` - Docker images → `D:\rancher-storage\docker-images`

**Verification:**
After running script and starting Rancher Desktop:
```powershell
docker info | Select-String "Docker Root Dir"
```
Should show: `D:\rancher-storage\docker-images`

---

### 05-update-docker-compose.ps1
**Purpose:** Update docker-compose files to use D: drive for volumes

**What it does:**
- Backs up all docker-compose files
- Updates volume paths to D: drive
- Creates volume directories
- Creates .env from .env.example (if needed)

**Prerequisites:**
- Must be run from project root directory
- docker-compose files must exist

**Usage:**
```powershell
# From project root
.\scripts\rancher-setup\05-update-docker-compose.ps1
```

**Files Modified:**
- `docker-compose.yml`
- `docker-compose-unified.yml`
- `docker-compose-langfuse.yml`

**Volume Mappings:**
- `mongodb_data` → `D:/rancher-storage/volumes/mongodb-data`
- `postgres_data` → `D:/rancher-storage/volumes/postgres-data`
- `langfuse_db_data` → `D:/rancher-storage/volumes/langfuse-db-data`
- `redis_data` → `D:/rancher-storage/volumes/redis-data`
- `n8n_data` → `D:/rancher-storage/volumes/n8n-data`

---

### 06-test-deployment.ps1
**Purpose:** Test docker-compose deployment and verify services

**What it does:**
- Checks Rancher Desktop is running
- Verifies .env configuration
- Pulls Docker images
- Deploys services
- Tests database connectivity
- Generates test report

**Prerequisites:**
- Rancher Desktop running
- .env file configured
- All previous phases completed

**Usage:**
```powershell
.\06-test-deployment.ps1
```

**Deployment Options:**
1. Basic services only (MongoDB + PostgreSQL)
2. Full stack (all services)
3. Unified stack with observability
4. Custom service selection

**Post-Deployment:**
- View logs: `docker-compose logs -f`
- Check status: `docker-compose ps`
- Access services on configured ports

---

### 07-create-management-scripts.ps1
**Purpose:** Generate operational management scripts

**What it does:**
- Creates `scripts/rancher-management/` directory
- Generates health check script
- Creates backup automation
- Generates stack management tools
- Creates cleanup utilities
- Generates documentation

**Prerequisites:** None (can run anytime)

**Usage:**
```powershell
.\07-create-management-scripts.ps1
```

**Scripts Created:**
1. `verify-setup.ps1` - Health check
2. `backup-volumes.ps1` - Volume backup
3. `manage-stack.ps1` - Service management
4. `cleanup.ps1` - Resource cleanup
5. `README.md` - Management documentation

---

### 08-create-documentation.ps1
**Purpose:** Generate comprehensive documentation

**What it does:**
- Creates `RANCHER-SETUP.md` (full guide)
- Creates `RANCHER-QUICK-REF.md` (quick reference)
- Creates `RANCHER-INSTALL-SUMMARY.md` (summary)
- Updates `.gitignore` with D: drive exclusions

**Prerequisites:** None (can run anytime)

**Usage:**
```powershell
.\08-create-documentation.ps1
```

**Documentation Created:**
1. **RANCHER-SETUP.md** - Complete setup and operations guide
2. **RANCHER-QUICK-REF.md** - Quick command reference
3. **RANCHER-INSTALL-SUMMARY.md** - Installation summary
4. **.gitignore** - Updated with Rancher exclusions

---

## Complete Installation Workflow

### Quick Installation (Recommended)

Run all scripts in sequence:

```powershell
# Navigate to project root
cd C:\DDN-AI-Project-Documentation

# Run all setup scripts
.\scripts\rancher-setup\00-document-current-setup.ps1
.\scripts\rancher-setup\01-create-d-drive-structure.ps1
.\scripts\rancher-setup\02-install-rancher-desktop.ps1

# Run as Administrator
.\scripts\rancher-setup\03-move-wsl-to-d-drive.ps1

# Continue with regular user
.\scripts\rancher-setup\04-configure-storage-locations.ps1
.\scripts\rancher-setup\05-update-docker-compose.ps1

# Configure .env file with your API keys
notepad .env

# Deploy and test
.\scripts\rancher-setup\06-test-deployment.ps1
.\scripts\rancher-setup\07-create-management-scripts.ps1
.\scripts\rancher-setup\08-create-documentation.ps1
```

**Total Time:** ~2-3 hours (including download and initialization times)

### Step-by-Step Installation

If you prefer to understand each step:

1. **Day 1: Preparation**
   - Run script 00 to document current setup
   - Run script 01 to create D: drive structure
   - Review what will be installed

2. **Day 2: Installation**
   - Run script 02 to install Rancher Desktop
   - Launch and configure Rancher Desktop
   - Wait for initialization

3. **Day 3: Migration**
   - Run script 03 (as Administrator) to move WSL2
   - Run script 04 to configure storage
   - Run script 05 to update docker-compose files

4. **Day 4: Deployment**
   - Configure .env file
   - Run script 06 to test deployment
   - Run scripts 07 and 08 for tools and docs

## Prerequisites

### System Requirements
- **OS:** Windows 10 version 2004+ or Windows 11
- **WSL2:** Enabled and updated
- **Disk Space:**
  - C: drive: 5-10 GB for Rancher Desktop
  - D: drive: 50+ GB for data storage
- **RAM:** 8GB minimum, 16GB recommended
- **CPU:** 4 cores recommended

### Required Software
- PowerShell 5.1 or newer
- WSL2 enabled
- Internet connection

### Optional (for installation)
- WinGet (Windows Package Manager)
- Chocolatey package manager

## Verification

After completing all scripts, verify the setup:

```powershell
# Run health check
.\scripts\rancher-management\verify-setup.ps1

# Check Rancher Desktop
rancher-desktop --version
docker --version
kubectl version --client

# Check WSL2 location
wsl --list -v

# Check Docker storage
docker info | Select-String "Docker Root Dir"

# Should show: D:\rancher-storage\docker-images

# Check services
docker-compose ps
```

## Troubleshooting

### Script Execution Policy Error

```powershell
# If you get "cannot be loaded because running scripts is disabled"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### D: Drive Not Found

- Ensure D: drive is mounted and accessible
- Check drive letter in Disk Management
- Update scripts if using different drive letter

### WSL2 Not Installed

```powershell
# Install WSL2
wsl --install

# Restart computer
# Then continue with Rancher Desktop installation
```

### Administrator Rights Required

- Right-click PowerShell
- Select "Run as Administrator"
- Navigate back to script location
- Run script 03 again

### Rancher Desktop Won't Start

1. Check WSL2: `wsl --list -v`
2. Restart WSL: `wsl --shutdown`
3. Check Windows Event Viewer
4. Reinstall if necessary

## Backup and Recovery

### Before Starting

All scripts create backups automatically:
- **Script 00:** Documents current Docker setup
- **Script 03:** Exports WSL2 distribution before moving
- **Script 04:** Backs up configuration files
- **Script 05:** Backs up docker-compose files

### Backup Locations

All backups are stored in:
```
D:\rancher-storage\backups\
├── pre-migration-[timestamp]\     # Original Docker setup
├── config-backup-[timestamp]\     # Configuration files
├── docker-compose-backup-[timestamp]\  # Compose files
└── volumes-[timestamp]\           # Volume data (manual backups)
```

### Recovery

If something goes wrong:

1. **WSL2 Migration Failed:**
   - Import backup: `wsl --import rancher-desktop D:\recovery D:\WSL-Distributions\rancher-desktop-backup.tar`

2. **Configuration Issues:**
   - Restore from: `D:\rancher-storage\backups\config-backup-[timestamp]\`

3. **docker-compose Issues:**
   - Restore from: `D:\rancher-storage\backups\docker-compose-backup-[timestamp]\`

## Support

### Documentation
- **Full Setup Guide:** `RANCHER-SETUP.md`
- **Quick Reference:** `RANCHER-QUICK-REF.md`
- **Install Summary:** `RANCHER-INSTALL-SUMMARY.md`
- **Management Scripts:** `scripts/rancher-management/README.md`

### Common Issues
- Check the Troubleshooting section in `RANCHER-SETUP.md`
- Run health check: `.\scripts\rancher-management\verify-setup.ps1`
- Review logs: `docker-compose logs`

### Resources
- [Rancher Desktop Docs](https://docs.rancherdesktop.io/)
- [WSL2 Documentation](https://docs.microsoft.com/windows/wsl/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

## License

These setup scripts are provided as-is for the DDN AI Test Failure Analysis System.

**Software Licenses:**
- **Rancher Desktop:** Apache 2.0 (Free & Open Source)
- **K3s:** Apache 2.0 (Free & Open Source)
- **Docker Compose:** Apache 2.0 (Free & Open Source)

No licensing fees required for any component.

---

**Last Updated:** Auto-generated during Phase 8
**Maintained By:** Project Team
