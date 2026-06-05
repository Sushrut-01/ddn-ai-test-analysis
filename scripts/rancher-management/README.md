# Rancher Desktop Management Scripts

This directory contains utility scripts for managing Rancher Desktop and your Docker Compose stack.

## Available Scripts

### 1. verify-setup.ps1
**Purpose:** Health check for Rancher Desktop installation and configuration

**Usage:**
\\\powershell
.\verify-setup.ps1
\\\

**Checks:**
- Rancher Desktop installation
- Docker engine status
- Kubernetes cluster status
- WSL2 distribution
- D: drive storage configuration
- Running containers
- Disk space

---

### 2. backup-volumes.ps1
**Purpose:** Backup volume data to prevent data loss

**Usage:**
\\\powershell
# Live backup (containers keep running)
.\backup-volumes.ps1

# Full backup (stops containers for consistency)
.\backup-volumes.ps1 -Full
\\\

**Backups:**
- MongoDB data
- PostgreSQL data
- Langfuse database
- Redis data
- n8n workflows

**Location:** D:\rancher-storage\backups\volumes-[timestamp]

---

### 3. manage-stack.ps1
**Purpose:** Easy management of Docker Compose services

**Usage:**
\\\powershell
# Start all services
.\manage-stack.ps1 -Action start

# Stop all services
.\manage-stack.ps1 -Action stop

# Restart all services
.\manage-stack.ps1 -Action restart

# Check status
.\manage-stack.ps1 -Action status

# View logs
.\manage-stack.ps1 -Action logs

# Manage specific service
.\manage-stack.ps1 -Action start -Service ddn-mongodb
.\manage-stack.ps1 -Action logs -Service ddn-langgraph
\\\

---

### 4. cleanup.ps1
**Purpose:** Remove unused Docker resources to free up disk space

**Usage:**
\\\powershell
.\cleanup.ps1
\\\

**Removes:**
- Stopped containers
- Unused networks
- Dangling images
- Build cache

---

## Common Workflows

### Daily Operations
\\\powershell
# Check health
.\verify-setup.ps1

# View service status
.\manage-stack.ps1 -Action status

# View logs
.\manage-stack.ps1 -Action logs
\\\

### Weekly Maintenance
\\\powershell
# Backup volumes
.\backup-volumes.ps1 -Full

# Cleanup unused resources
.\cleanup.ps1

# Verify setup
.\verify-setup.ps1
\\\

### Troubleshooting
\\\powershell
# Check logs for specific service
.\manage-stack.ps1 -Action logs -Service [service-name]

# Restart problematic service
.\manage-stack.ps1 -Action restart -Service [service-name]

# Verify configuration
.\verify-setup.ps1
\\\

---

## Best Practices

1. **Regular Backups:** Run \ackup-volumes.ps1\ at least weekly
2. **Monitor Disk Space:** Check D: drive space regularly
3. **Review Logs:** Periodically check service logs for errors
4. **Cleanup:** Run \cleanup.ps1\ monthly to free space

---

## Support

For issues or questions:
1. Run \erify-setup.ps1\ to identify problems
2. Check service logs with \manage-stack.ps1 -Action logs\
3. Refer to main documentation in RANCHER-SETUP.md
