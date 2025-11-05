# Task 0F.10: GitHub Repository Setup Guide

## Status: Ready for User Action

All test data files have been created locally in the `ddn-test-data/` directory. Now we need to create the GitHub repository and push these files.

---

## Step 1: Verify Local Files

First, let's verify all files were created correctly:

```bash
cd c:\DDN-AI-Project-Documentation\ddn-test-data
dir /s /b
```

**Expected Structure:**
```
ddn-test-data/
├── .gitignore
├── README.md
├── robot-tests/
│   ├── ddn_basic_tests.robot
│   ├── ddn_advanced_tests.robot
│   └── DDN_Keywords.py
├── tests/
│   └── python/
│       └── test_ha_failover.py
├── src/
│   ├── storage/
│   │   └── DDNStorage.java
│   └── network/
│       └── connection.py
└── test-data/
    └── error-logs/
        └── code-errors.json
```

---

## Step 2: Create GitHub Repository

### Option A: Via GitHub Web Interface (Recommended)

1. **Go to GitHub:**
   - Open https://github.com/Sushrut-01
   - Click the "+" icon in the top right
   - Select "New repository"

2. **Repository Settings:**
   - **Owner:** Sushrut-01
   - **Repository name:** `ddn-test-data`
   - **Description:** "Test data repository for DDN AI Test Failure Analysis System - MCP GitHub integration testing"
   - **Visibility:**
     - ✅ **Public** (recommended for testing - easier setup)
     - OR ☐ Private (requires `repo` scope token, not just `public_repo`)
   - **Initialize:**
     - ☐ Do NOT add README (we already have one)
     - ☐ Do NOT add .gitignore (we already have one)
     - ☐ Do NOT add license (optional)

3. **Click "Create repository"**

### Option B: Via GitHub CLI (If installed)

```bash
cd c:\DDN-AI-Project-Documentation\ddn-test-data
gh repo create Sushrut-01/ddn-test-data --public --description "Test data repository for DDN AI Test Failure Analysis System"
```

---

## Step 3: Initialize Git and Push Files

After creating the repository on GitHub, run these commands:

```bash
cd c:\DDN-AI-Project-Documentation\ddn-test-data

# Initialize git repository
git init

# Add all files
git add .

# Commit files
git commit -m "Initial commit: Test data for MCP GitHub integration

- Added Robot Framework tests (ddn_basic_tests.robot, ddn_advanced_tests.robot)
- Added Python test file with error at line 145 (tests/python/test_ha_failover.py)
- Added Java source file with error at line 142 (src/storage/DDNStorage.java)
- Added network connection module with timeout error at line 87 (src/network/connection.py)
- Added sample error logs (test-data/error-logs/code-errors.json)
- Added comprehensive README documentation
- Repository structure for CODE_ERROR testing with actual source code
"

# Set the main branch
git branch -M main

# Add remote origin (replace with your actual GitHub URL)
git remote add origin https://github.com/Sushrut-01/ddn-test-data.git

# Push to GitHub
git push -u origin main
```

**Expected Output:**
```
Enumerating objects: 15, done.
Counting objects: 100% (15/15), done.
Delta compression using up to 8 threads
Compressing objects: 100% (12/12), done.
Writing objects: 100% (15/15), 15.24 KiB | 5.08 MiB/s, done.
Total 15 (delta 2), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (2/2), done.
To https://github.com/Sushrut-01/ddn-test-data.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

## Step 4: Verify Repository on GitHub

1. **Open Repository:**
   - Visit https://github.com/Sushrut-01/ddn-test-data

2. **Verify Files:**
   - ✅ README.md displays correctly
   - ✅ All directories visible (robot-tests, tests, src, test-data, docs)
   - ✅ Files can be browsed

3. **Check Specific Files:**
   - **tests/python/test_ha_failover.py** - Verify line 145 visible
   - **src/storage/DDNStorage.java** - Verify line 142 visible
   - **test-data/error-logs/code-errors.json** - Verify JSON formatting

---

## Step 5: Generate GitHub Personal Access Token

**CRITICAL:** You need a GitHub token to access the repository via API.

### 5.1 Go to Token Settings

1. Visit https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"

### 5.2 Configure Token

**Token Name:**
```
DDN AI MCP GitHub Integration
```

**Expiration:**
- Select: **90 days**
- Set calendar reminder to regenerate before expiration

**Scopes:** (Select these checkboxes)

For **Public Repository:**
- ✅ `public_repo` - Access public repositories

For **Private Repository:**
- ✅ `repo` - Full control of private repositories
  - ✅ `repo:status`
  - ✅ `repo_deployment`
  - ✅ `public_repo`
  - ✅ `repo:invite`
  - ✅ `security_events`

### 5.3 Generate and Save Token

1. Click "Generate token"
2. **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)
3. Token format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
4. Save it temporarily in a secure note

**Token Example:**
```
ghp_1234567890abcdefghijklmnopqrstuvwxyzABCD
```

---

## Step 6: Verify Token Works

Test your token with curl:

```bash
# Test authentication (replace YOUR_TOKEN with actual token)
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Test repository access
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/repos/Sushrut-01/ddn-test-data

# Test file fetching
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/repos/Sushrut-01/ddn-test-data/contents/README.md
```

**Expected:** All three commands return JSON data (not 401 Unauthorized)

---

## Troubleshooting

### Problem: "Repository not found" error

**Solution:**
- Verify repository name is exactly `ddn-test-data`
- Verify repository owner is `Sushrut-01`
- If private repo, ensure token has `repo` scope

### Problem: "Authentication failed" error

**Solution:**
- Verify token is copied correctly (no spaces)
- Verify token hasn't expired
- Regenerate token if needed

### Problem: Git push requires username/password

**Solution:**
Use token as password:
```bash
# When prompted:
Username: Sushrut-01
Password: ghp_YOUR_TOKEN_HERE
```

Or configure git credential manager:
```bash
git config --global credential.helper manager
```

### Problem: Files not showing on GitHub

**Solution:**
```bash
# Check git status
git status

# Verify remote
git remote -v

# Re-push if needed
git push origin main --force
```

---

## What's Next?

After completing these steps, you'll be ready for **Task 0F.11: Configure GitHub Integration**.

**Checklist:**
- ✅ Repository created at https://github.com/Sushrut-01/ddn-test-data
- ✅ All files pushed to GitHub
- ✅ Files visible and browsable on GitHub
- ✅ GitHub Personal Access Token generated
- ✅ Token verified with curl test

**Ready to proceed to Task 0F.11!**

---

## Files Created

**Local Directory:** `C:\DDN-AI-Project-Documentation\ddn-test-data\`

| File | Size | Purpose |
|------|------|---------|
| README.md | ~6KB | Repository documentation |
| .gitignore | ~300B | Git ignore rules |
| robot-tests/ddn_basic_tests.robot | ~14KB | Robot Framework tests |
| robot-tests/ddn_advanced_tests.robot | ~8KB | Advanced Robot tests |
| robot-tests/DDN_Keywords.py | ~18KB | Python keywords |
| tests/python/test_ha_failover.py | ~6KB | Python HA tests (line 145 error) |
| src/storage/DDNStorage.java | ~7KB | Java storage client (line 142 error) |
| src/network/connection.py | ~8KB | Network connection (line 87 error) |
| test-data/error-logs/code-errors.json | ~3KB | Sample error logs |

**Total:** ~70KB of test data

---

## Contact

If you encounter issues:
1. Check this guide's troubleshooting section
2. Verify GitHub account access
3. Verify internet connectivity
4. Regenerate token if expired

**Task:** 0F.10 - Create GitHub Test Data Repository
**Status:** Local files ready, awaiting GitHub creation
**Next:** Task 0F.11 - Configure GitHub Integration
**Created:** 2025-11-03
