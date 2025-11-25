# Docker Desktop to Rancher Desktop Migration Status

**Migration Date:** November 25, 2025  
**Status:** ⚠️ **PARTIALLY COMPLETE** - Rancher structure created but not fully migrated

---

## 📊 Current Status Overview

### ✅ What's Been Completed

1. **✅ D: Drive Storage Structure Created**
   - Location: `D:\rancher-storage\`
   - Directories: backups/, docker-images/, k3s-data/, volumes/
   - Location: `D:\WSL-Distributions\`
   - **Verified:** Both directories exist

2. **✅ Rancher Desktop Scripts Created**
   - 10 PowerShell automation scripts in `scripts/rancher-setup/`
   - Master setup script: `SETUP-RANCHER-ON-D-DRIVE.ps1`
   - Management scripts planned in `scripts/rancher-management/`

3. **✅ Documentation Created**
   - `QUICK-START-RANCHER-D-DRIVE.md` - Complete setup guide
   - Migration guide for D: drive only setup
   - Service access URLs and troubleshooting

4. **✅ Rancher Desktop WSL Distribution**
   - **Installed:** `rancher-desktop` WSL distribution (Running)
   - **Installed:** `rancher-desktop-data` WSL distribution (Stopped)
   - **Status:** Both distributions present in WSL

### ⚠️ What's Currently Running

**Active System:** Docker Desktop (not Rancher Desktop)
- Docker version: 28.5.1
- Docker Root Dir: `/var/lib/docker` (not D: drive)
- WSL Distribution: `docker-desktop` (Running)

**Why?**
- System is using Docker Desktop alongside Rancher Desktop installations
- Docker data still on C: drive
- Haven't switched to use Rancher Desktop as primary runtime

### ❌ What's NOT Complete

1. **❌ Rancher Desktop Not Primary Runtime**
   - Docker Desktop still active
   - Need to switch container runtime to Rancher Desktop

2. **❌ Docker Data Not Moved to D: Drive**
   - Current: `/var/lib/docker` (C: drive via WSL)
   - Target: `D:\rancher-storage\docker-images`
   - docker-compose volumes still referencing default locations

3. **❌ docker-compose Not Updated for D: Drive**
   - Current: `docker-compose-unified.yml` uses named volumes
   - Need: Volume paths pointing to `D:\rancher-storage\volumes\*`

4. **❌ Services Not Migrated**
   - Services still running on Docker Desktop
   - Need to stop Docker Desktop, start with Rancher Desktop
   - Re-deploy containers with new volume mappings

5. **❌ Management Scripts Not Created**
   - Setup scripts exist
   - Management scripts (`scripts/rancher-management/`) not yet created
   - No backup scripts, cleanup scripts, verify scripts yet

---

## 📋 Migration Plan - What Needs to Be Done

### Phase 1: Stop Current Services ⏸️
```powershell
# Stop all running containers
docker-compose -f docker-compose-unified.yml down

# Backup current data (optional but recommended)
# Copy volumes from Docker Desktop to D: drive
```

### Phase 2: Update docker-compose Volumes 📝
```yaml
# Change from named volumes to D: drive paths
volumes:
  - D:\rancher-storage\volumes\postgres-data:/var/lib/postgresql/data
  - D:\rancher-storage\volumes\langfuse-db-data:/var/lib/postgresql/data
  - D:\rancher-storage\volumes\redis-data:/data
```

### Phase 3: Configure Rancher Desktop 🔧
```powershell
# Run setup scripts (if not already done)
.\scripts\rancher-setup\04-configure-storage-locations.ps1
.\scripts\rancher-setup\05-update-docker-compose.ps1
```

### Phase 4: Switch to Rancher Desktop 🔄
```powershell
# Stop Docker Desktop
# Open Rancher Desktop from Start Menu
# Wait for Rancher to initialize (5-10 minutes)

# Verify Rancher is active
docker context use rancher-desktop
docker info | Select-String "Docker Root Dir"
# Should show: D:\rancher-storage\docker-images
```

### Phase 5: Deploy Services on Rancher 🚀
```powershell
# Deploy with updated volumes
docker-compose -f docker-compose-unified.yml up -d

# Verify services
docker-compose ps
```

### Phase 6: Create Management Scripts 🛠️
```powershell
# Run script creation
.\scripts\rancher-setup\07-create-management-scripts.ps1

# This creates:
# - backup-volumes.ps1
# - verify-setup.ps1
# - cleanup.ps1
# - manage-stack.ps1
```

### Phase 7: Verify Migration ✅
```powershell
# Check all services running
docker-compose ps

# Verify D: drive usage
Get-ChildItem D:\rancher-storage -Recurse -Depth 1

# Run verification
.\scripts\rancher-management\verify-setup.ps1
```

---

## 🎯 Why Migrate to Rancher Desktop?

### Current (Docker Desktop)
- ❌ Paid license for businesses >250 employees
- ❌ All data on C: drive (50-100GB+)
- ❌ Single container runtime only
- ✅ Familiar, well-documented

### Target (Rancher Desktop)
- ✅ 100% Free & Open Source (Apache 2.0)
- ✅ All data on D: drive (C: only 5-10GB)
- ✅ Built-in Kubernetes (K3s)
- ✅ Multiple runtime support (dockerd, containerd)
- ✅ Same Docker CLI/commands

---

## 📂 Current vs Target Architecture

### Current Setup (Docker Desktop)
```
C:\
├── Users\<User>\AppData\Local\Docker\
│   └── wsl\
│       └── data\               # 50-100GB
├── WSL Distributions\
│   └── docker-desktop\         # Running
└── Program Files\Docker\

D:\
└── (empty)
```

### Target Setup (Rancher Desktop)
```
C:\
├── Users\<User>\AppData\Local\Rancher Desktop\
│   ├── rdctl-settings.json     # Points to D:
│   └── docker\daemon.json      # Points to D:
└── Program Files\Rancher Desktop\  # 5-10GB

D:\
├── rancher-storage\            # 50-100GB
│   ├── docker-images\          # All images
│   ├── volumes\                # All data
│   ├── k3s-data\               # Kubernetes
│   └── backups\                # Backups
└── WSL-Distributions\
    └── rancher-desktop\        # WSL2 instance
```

---

## 🔍 Current System Analysis

### Active Containers
```powershell
# Check what's running
docker ps

# Current volumes
docker volume ls

# Current images
docker images
```

### Docker Desktop Status
- **Running:** Yes
- **Root Dir:** C: drive (via WSL2)
- **Volumes:** Named volumes on C: drive

### Rancher Desktop Status
- **Installed:** Yes (WSL distributions present)
- **Running:** Partially (distributions exist but not active runtime)
- **Storage:** D: drive structure created but not in use

---

## ⚠️ Important Considerations

### Before Migration

1. **Backup Data**
   ```powershell
   # Backup existing volumes
   docker run --rm -v postgres_data:/data -v D:\backups:/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
   ```

2. **Document Current State**
   ```powershell
   # Export current container configs
   docker inspect $(docker ps -aq) > container-configs.json
   ```

3. **Stop All Services**
   ```powershell
   docker-compose -f docker-compose-unified.yml down
   ```

### After Migration

1. **Verify All Services**
   - Check each service starts correctly
   - Verify data persisted correctly
   - Test connectivity between services

2. **Update CI/CD**
   - GitHub Actions workflows
   - Jenkins pipelines
   - Any automation scripts

3. **Monitor Performance**
   - D: drive space usage
   - Container performance
   - Network connectivity

---

## 📊 Disk Space Comparison

### Current (Docker Desktop on C:)
- Docker Desktop: ~50-100GB
- WSL2 distributions: ~10-20GB
- **Total C: Drive Usage:** 60-120GB

### After Migration (Rancher Desktop on D:)
- C: Drive: ~5-10GB (app only)
- D: Drive: ~50-100GB (all data)
- **C: Drive Savings:** 50-110GB freed

---

## 🚀 Quick Migration Commands

### One-Line Migration (After Manual Review)
```powershell
# CAUTION: Review each script before running!

# Stop current services
docker-compose down

# Run master migration script
.\scripts\rancher-setup\SETUP-RANCHER-ON-D-DRIVE.ps1

# This will:
# 1. Configure Rancher Desktop
# 2. Update docker-compose
# 3. Migrate volumes
# 4. Start services on Rancher
```

### Manual Step-by-Step (Recommended for First Time)
```powershell
# 1. Backup current setup
docker-compose down
docker volume ls > current-volumes.txt

# 2. Run Rancher setup scripts
.\scripts\rancher-setup\01-create-d-drive-structure.ps1
# ... (continue with each script)

# 3. Update docker-compose
.\scripts\rancher-setup\05-update-docker-compose.ps1

# 4. Start Rancher Desktop (from Start Menu)

# 5. Deploy services
docker-compose -f docker-compose-unified.yml up -d
```

---

## 📝 Action Items

### Immediate Next Steps

1. **Review Migration Scripts**
   - [ ] Check `scripts/rancher-setup/` scripts
   - [ ] Understand what each does
   - [ ] Verify D: drive has 50GB+ free

2. **Backup Current Setup**
   - [ ] Export container configs
   - [ ] Note current volume locations
   - [ ] Document running services

3. **Execute Migration**
   - [ ] Stop Docker Desktop services
   - [ ] Run Rancher setup scripts
   - [ ] Update docker-compose volumes
   - [ ] Start Rancher Desktop
   - [ ] Deploy services

4. **Verify Migration**
   - [ ] Check all services running
   - [ ] Verify D: drive contains data
   - [ ] Test service connectivity
   - [ ] Run health checks

5. **Cleanup**
   - [ ] Uninstall Docker Desktop (optional)
   - [ ] Remove old WSL distributions
   - [ ] Delete C: drive Docker data
   - [ ] Free up C: drive space

---

## 📚 Resources

### Documentation
- `QUICK-START-RANCHER-D-DRIVE.md` - Complete setup guide
- `scripts/rancher-setup/` - Migration scripts
- `docker-compose-unified.yml` - Current service config

### Scripts
- **Setup:** `scripts/rancher-setup/SETUP-RANCHER-ON-D-DRIVE.ps1`
- **Management:** (To be created)
- **Verification:** (To be created)

### Support
- Rancher Desktop Docs: https://docs.rancherdesktop.io
- Docker Docs: https://docs.docker.com
- WSL2 Docs: https://learn.microsoft.com/en-us/windows/wsl/

---

## ✅ Success Criteria

Migration is complete when:

- ✅ Rancher Desktop is primary container runtime
- ✅ Docker Root Dir points to D: drive
- ✅ All volumes are on D:\rancher-storage\volumes\
- ✅ All services running and healthy
- ✅ C: drive freed up (50-110GB)
- ✅ docker-compose ps shows all services up
- ✅ Management scripts created and working
- ✅ Backup strategy in place

---

## 🎯 Timeline Estimate

**Total Time:** 2-3 hours

| Phase | Time | Complexity |
|-------|------|------------|
| Backup current setup | 30 min | Low |
| Run setup scripts | 45 min | Medium |
| Update docker-compose | 15 min | Low |
| Start Rancher Desktop | 10 min | Low |
| Deploy services | 30 min | Medium |
| Verification | 20 min | Low |
| Cleanup | 20 min | Low |

**Note:** Most time is waiting for downloads and container initialization.

---

**Status Date:** November 25, 2025  
**Next Review:** After migration completion  
**Owner:** QA Team
