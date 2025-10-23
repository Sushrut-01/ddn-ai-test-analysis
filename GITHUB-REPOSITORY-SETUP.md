# GitHub Repository Setup Guide

**Create and push your DDN AI System to GitHub**

**Your GitHub Profile:** https://github.com/Sushrut-01

---

## Quick Start (5 minutes)

### Step 1: Create Repository on GitHub

1. **Go to:** https://github.com/new
2. **Or click:** "+" in top-right → "New repository"
3. **Repository name:** `ddn-ai-test-analysis`
4. **Description:** `AI-powered test failure analysis system for DDN using Claude AI, n8n, and MongoDB`
5. **Visibility:**
   - Choose **Private** (recommended for company projects)
   - Or **Public** (if open source)
6. **Initialize:**
   - ❌ Don't check "Add a README file" (we already have one)
   - ❌ Don't add .gitignore (we already have one)
   - ❌ Don't choose a license yet
7. **Click:** "Create repository"

**Your new repo URL will be:**
```
https://github.com/Sushrut-01/ddn-ai-test-analysis
```

---

## Step 2: Initialize Git in Your Project

Open terminal/command prompt:

```bash
cd C:\DDN-AI-Project-Documentation

# Initialize git (if not already initialized)
git init

# Check status
git status
```

---

## Step 3: Configure Git (First Time Only)

If you haven't configured Git before:

```bash
# Set your name
git config --global user.name "Sushrut-01"

# Set your email (use your GitHub email)
git config --global user.email "your-email@example.com"

# Verify
git config --global user.name
git config --global user.email
```

---

## Step 4: Create .gitignore File

Make sure `.gitignore` excludes sensitive files:

```bash
# Check if .gitignore exists
cat .gitignore

# If it doesn't exist, create it
```

**Contents of `.gitignore`:**
```
# Environment and secrets
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# Build outputs
build/
dist/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Docker
*.log

# Database
*.sqlite
*.db

# Temporary files
*.tmp
*.temp
.cache/
```

---

## Step 5: Add Remote Repository

```bash
# Add GitHub as remote
git remote add origin https://github.com/Sushrut-01/ddn-ai-test-analysis.git

# Verify remote was added
git remote -v
```

**Expected output:**
```
origin  https://github.com/Sushrut-01/ddn-ai-test-analysis.git (fetch)
origin  https://github.com/Sushrut-01/ddn-ai-test-analysis.git (push)
```

---

## Step 6: Stage and Commit Files

```bash
# Check what files will be added
git status

# Add all files
git add .

# Or add selectively
git add README.md
git add docker-compose.yml
git add implementation/
# etc.

# Create first commit
git commit -m "Initial commit: DDN AI Test Analysis System

- Complete GitHub + Jenkins + n8n integration
- MongoDB Atlas support
- Dashboard with workflow triggers
- 3 n8n workflows (auto, manual, refinement)
- Complete documentation and guides
- Docker Compose configuration for all services
- Startup scripts for Windows and Linux
- CI/CD pipeline with GitHub Actions"

# Verify commit
git log --oneline
```

---

## Step 7: Push to GitHub

### Option A: Push via HTTPS (Easier)

```bash
# Push to GitHub
git push -u origin main

# You'll be prompted for GitHub credentials
# Username: Sushrut-01
# Password: Use Personal Access Token (not your GitHub password!)
```

**Get Personal Access Token:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: `DDN-AI-Project`
4. Expiration: 90 days (or custom)
5. Scopes: Check `repo` (full control of private repositories)
6. Click "Generate token"
7. **Copy the token** (you won't see it again!)
8. Use this as password when pushing

### Option B: Push via SSH (More Secure)

```bash
# If you have SSH key set up
git remote set-url origin git@github.com:Sushrut-01/ddn-ai-test-analysis.git
git push -u origin main
```

**Set up SSH key:**
1. Generate key: `ssh-keygen -t ed25519 -C "your-email@example.com"`
2. Add to GitHub: https://github.com/settings/keys
3. Copy public key: `cat ~/.ssh/id_ed25519.pub`
4. Paste into GitHub

---

## Step 8: Verify Repository on GitHub

1. **Go to:** https://github.com/Sushrut-01/ddn-ai-test-analysis
2. **You should see:**
   - All your files
   - README.md displayed
   - Commit history
   - GitHub Actions tab (if workflow exists)

---

## Step 9: Set Up GitHub Actions (Already Done!)

Your project already has `.github/workflows/ci-cd.yml`:

**What it does:**
- ✅ Runs on every push to main/develop
- ✅ Builds Docker images
- ✅ Runs tests
- ✅ Performs health checks
- ✅ Deploys on main branch

**View Actions:**
1. Go to your repository
2. Click "Actions" tab
3. See workflow runs

---

## Step 10: Configure Repository Settings

### Add Repository Description

1. **Go to:** https://github.com/Sushrut-01/ddn-ai-test-analysis
2. **Click:** ⚙️ (Settings)
3. **Description:** `AI-powered test failure analysis system using Claude AI, n8n workflows, and MongoDB Atlas`
4. **Website:** `http://localhost:3000` (or your deployed URL)
5. **Topics:** Add tags:
   - `ai`
   - `claude-ai`
   - `n8n`
   - `mongodb`
   - `test-automation`
   - `jenkins`
   - `langraph`
   - `docker`

### Set Default Branch

1. **Settings** → **Branches**
2. **Default branch:** `main`
3. **Branch protection rules:**
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date

### Add Collaborators (Optional)

1. **Settings** → **Collaborators**
2. **Add people** to invite team members

---

## Step 11: Create Additional Branches (Optional)

```bash
# Create develop branch
git checkout -b develop
git push -u origin develop

# Create feature branch
git checkout -b feature/dashboard-improvements
git push -u origin feature/dashboard-improvements

# Switch back to main
git checkout main
```

---

## Repository Structure

Your GitHub repository now contains:

```
ddn-ai-test-analysis/
├── 📄 README.md                     (Main documentation)
├── 📄 START-HERE.md                 (Quick start guide)
├── 📄 DEPLOYMENT-GUIDE.md           (Deployment instructions)
├── 📄 MONGODB-ATLAS-SETUP.md        (MongoDB Atlas guide)
├── 📄 GITHUB-REPOSITORY-SETUP.md    (This file)
│
├── 🔧 docker-compose.yml            (All services)
├── 🔧 Jenkinsfile                   (CI/CD pipeline)
├── 🔧 .gitignore                    (Ignored files)
├── 🔧 .env.example                  (Environment template)
├── 🔧 .env.atlas.example            (Atlas template)
│
├── 📁 .github/
│   ├── workflows/ci-cd.yml          (GitHub Actions)
│   └── ISSUE_TEMPLATE/              (Issue templates)
│
├── 📁 implementation/
│   ├── 🐍 langgraph_agent.py        (AI classification)
│   ├── 🐍 dashboard_api.py          (Backend API)
│   ├── 📦 requirements.txt          (Python dependencies)
│   ├── 🐳 Dockerfile                (Docker image)
│   ├── 📁 workflows/                (n8n workflows)
│   ├── 📁 dashboard-ui/             (React frontend)
│   └── 📁 database/                 (DB setup scripts)
│
├── 📁 jenkins/
│   ├── webhook-config.json          (Jenkins webhook config)
│   └── Jenkinsfile.test             (Test pipeline)
│
├── 📁 scripts/
│   ├── start-system.bat             (Windows startup)
│   └── start-system.sh              (Linux startup)
│
├── 📁 architecture/                 (Architecture docs)
├── 📁 technical-guides/             (Technical guides)
└── 📁 mcp-configs/                  (MCP server configs)
```

---

## Useful Git Commands

### Daily Workflow

```bash
# Check status
git status

# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/new-feature

# Make changes, then:
git add .
git commit -m "Add new feature"

# Push feature branch
git push -u origin feature/new-feature

# Merge to main (after PR approval)
git checkout main
git merge feature/new-feature
git push origin main
```

### Undo Changes

```bash
# Undo uncommitted changes
git checkout -- filename

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - CAREFUL!
git reset --hard HEAD~1
```

### View History

```bash
# View commits
git log --oneline --graph --all

# View specific file history
git log -- filename

# View changes in commit
git show commit-hash
```

---

## GitHub Best Practices

### Commit Messages

✅ **Good:**
```
Add manual trigger functionality to dashboard

- Implement "Analyze Now" button in Failures page
- Connect to n8n webhook for manual analysis
- Add loading state and success notification
- Update API endpoint to handle manual triggers
```

❌ **Bad:**
```
update code
```

### Branch Naming

✅ **Good:**
- `feature/dashboard-analytics`
- `fix/mongodb-connection-timeout`
- `docs/update-setup-guide`
- `refactor/langgraph-classification`

❌ **Bad:**
- `test`
- `temp`
- `asdfgh`

### Pull Requests

When creating PR:
1. **Title:** Clear and descriptive
2. **Description:** What changed and why
3. **Link issues:** Reference related issues
4. **Request review:** Tag team members
5. **Add labels:** bug, enhancement, documentation, etc.

---

## Protecting Secrets

### Never Commit These Files

❌ `.env` - Environment variables
❌ `credentials.json` - API credentials
❌ `*.key` - Private keys
❌ `*.pem` - Certificates
❌ `.aws/` - AWS credentials
❌ `config.local.js` - Local configs

### Already Protected

Your `.gitignore` already excludes:
- ✅ `.env` files
- ✅ `node_modules/`
- ✅ `__pycache__/`
- ✅ `.vscode/`
- ✅ Build outputs

### If You Accidentally Commit Secrets

```bash
# Remove from Git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (CAREFUL!)
git push origin --force --all

# Rotate all exposed credentials immediately!
```

---

## GitHub Features to Use

### Issues

Track bugs and feature requests:
- Go to "Issues" tab
- Use templates in `.github/ISSUE_TEMPLATE/`
- Assign to team members
- Add labels and milestones

### Projects

Organize work:
- Go to "Projects" tab
- Create Kanban board
- Track progress

### Wiki

Documentation:
- Enable in Settings
- Create technical docs
- API documentation

### Releases

Version your software:
1. Create tag: `git tag v1.0.0`
2. Push tag: `git push origin v1.0.0`
3. Create release on GitHub
4. Add release notes

---

## Cloning Repository (For Team Members)

Share these instructions with your team:

```bash
# Clone repository
git clone https://github.com/Sushrut-01/ddn-ai-test-analysis.git

# Navigate to project
cd ddn-ai-test-analysis

# Create .env file
cp .env.example .env

# Edit .env with your credentials
notepad .env  # or code .env

# Start system
scripts\start-system.bat  # Windows
./scripts/start-system.sh # Linux/Mac
```

---

## Keeping Repository Updated

```bash
# Pull latest changes
git pull origin main

# If you have local changes
git stash              # Save local changes
git pull origin main   # Update from remote
git stash pop          # Restore local changes

# If conflicts occur
git status             # See conflicted files
# Edit files to resolve conflicts
git add .
git commit -m "Resolve merge conflicts"
```

---

## Summary Checklist

After completing this guide, you should have:

✅ GitHub repository created at `https://github.com/Sushrut-01/ddn-ai-test-analysis`
✅ All project files pushed to GitHub
✅ `.gitignore` configured to exclude sensitive files
✅ GitHub Actions CI/CD pipeline active
✅ Repository description and topics added
✅ README.md displayed on repository page
✅ Team members can clone and contribute

---

## Next Steps

1. **Share repository with team:**
   ```
   Send: https://github.com/Sushrut-01/ddn-ai-test-analysis
   ```

2. **Configure Jenkins to use GitHub:**
   - Add GitHub webhook to trigger builds
   - See: jenkins/webhook-config.json

3. **Set up branch protection:**
   - Settings → Branches → Add rule
   - Require PR reviews before merging

4. **Enable GitHub Actions:**
   - Check "Actions" tab
   - Workflows run automatically on push

5. **Create first release:**
   - Tag: `v1.0.0`
   - Release notes with features list

---

## Support

**Git Help:**
- https://git-scm.com/doc
- https://guides.github.com/

**GitHub Actions:**
- https://docs.github.com/en/actions

**Your Project Docs:**
- [START-HERE.md](START-HERE.md)
- [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)

---

**Repository Owner:** Sushrut-01
**Repository:** https://github.com/Sushrut-01/ddn-ai-test-analysis
**Last Updated:** October 22, 2025
**Status:** Ready to Push ✅
