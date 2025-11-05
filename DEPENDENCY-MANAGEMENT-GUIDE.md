# Python Dependency Management Guide

**Created:** 2025-11-03
**Purpose:** Best practices for managing Python package dependencies and avoiding version conflicts

---

## Why Dependency Conflicts Happen

### The Problem We Just Fixed

**What Happened:**
```
pip install --upgrade spacy
# Installed: spacy 3.8.7, numpy 2.3.4, scipy 1.16.3, thinc 8.3.6

ERROR: numpy.dtype size changed (expected 96, got 88)
```

**Root Cause:**
- `pip install --upgrade` installs **latest versions** without checking compatibility
- numpy 2.3.4 broke binary compatibility with packages compiled for numpy 1.x
- langchain-pinecone requires numpy<2.0
- numba requires numpy<1.25

---

## Best Practices for Dependency Management

### 1. **Pin Exact Versions in requirements.txt**

**❌ BAD (What caused our issue):**
```python
spacy>=3.7.2          # Could install 3.8.x, 3.9.x, etc.
sentence-transformers>=2.2.2
```

**✅ GOOD:**
```python
# Core packages with exact versions
numpy==1.24.4
scipy==1.11.4
spacy==3.7.5
thinc==8.2.5

# Use >= only for packages you control or test regularly
anthropic>=0.41.0     # OK if you test each version
openai>=1.58.1
```

**Why:** Exact versions ensure reproducible builds and prevent surprise upgrades.

---

### 2. **Use requirements-lock.txt for Production**

Create two files:

**requirements.txt** (Development - Flexible):
```python
# Phase 0/1 Dependencies
redis==5.0.1
spacy==3.7.5
numpy==1.24.4
scipy==1.11.4
```

**requirements-lock.txt** (Production - Frozen):
```bash
# Generate with:
pip freeze > requirements-lock.txt

# Result: ALL transitive dependencies pinned
redis==7.0.1
spacy==3.7.5
numpy==1.24.4
scipy==1.11.4
thinc==8.2.5
cymem==2.0.11
murmurhash==1.0.13
# ... (50+ more dependencies)
```

**Usage:**
- Development: `pip install -r requirements.txt`
- Production: `pip install -r requirements-lock.txt`

---

### 3. **Use pip-tools for Dependency Resolution**

**Install:**
```bash
pip install pip-tools
```

**Create requirements.in:**
```python
# requirements.in (high-level dependencies only)
redis==5.0.1
spacy==3.7.5
presidio-analyzer==2.2.354
sentence-transformers==2.2.2
```

**Compile to requirements.txt:**
```bash
pip-compile requirements.in
# Creates requirements.txt with ALL resolved dependencies
```

**Benefits:**
- Resolves version conflicts automatically
- Shows dependency tree
- Easy to update: `pip-compile --upgrade`

---

### 4. **Use Poetry (Alternative to pip-tools)**

**Install:**
```bash
pip install poetry
```

**Initialize:**
```bash
poetry init
```

**Add dependencies:**
```bash
poetry add spacy@3.7.5
poetry add numpy@1.24.4
```

**Lock dependencies:**
```bash
poetry lock
# Creates poetry.lock with all resolved versions
```

**Benefits:**
- Better dependency resolution than pip
- Automatic virtual environment management
- Separate dev/prod dependencies

---

### 5. **Check Compatibility Before Installing**

**Before upgrading:**
```bash
# Check what will be upgraded
pip list --outdated

# Check specific package versions
pip index versions spacy

# Test in isolated environment first
python -m venv test_env
test_env\Scripts\activate
pip install spacy==3.8.7
python -c "import spacy; print(spacy.__version__)"
deactivate
```

---

### 6. **Use Version Constraints Strategically**

**Constraint Types:**
```python
# Exact version (safest)
numpy==1.24.4

# Compatible release (allows patch updates)
numpy~=1.24.0        # Allows 1.24.1, 1.24.2, but NOT 1.25.0

# Minimum version (risky)
numpy>=1.24.0        # Could install 2.x, 3.x...

# Version range (moderate)
numpy>=1.24.0,<2.0.0  # Safe for numpy 1.x only
```

**When to use each:**
- **Exact (`==`)**: Critical packages (numpy, scipy, torch)
- **Compatible (`~=`)**: Stable packages where you want security updates
- **Range (`>=,<`)**: Packages with breaking changes between major versions
- **Minimum (`>=`)**: Your own packages or well-tested dependencies

---

## Preventing numpy 2.x Issues Specifically

### The numpy 2.0 Breaking Change

**Problem:** numpy 2.0+ changed ABI (Application Binary Interface)
- Packages compiled against numpy 1.x don't work with numpy 2.x
- Many scientific packages (scipy, scikit-learn, h5py) need recompilation

**Solution in requirements.txt:**
```python
# Force numpy 1.24.x (most compatible)
numpy>=1.24.0,<1.25.0

# Or pin exactly
numpy==1.24.4

# Ensure scipy matches
scipy>=1.11.0,<1.12.0  # Compatible with numpy 1.24
```

---

## Tools to Help Manage Dependencies

### 1. **pipdeptree** - Visualize Dependencies
```bash
pip install pipdeptree
pipdeptree

# Shows tree:
spacy==3.7.5
├── thinc [required: <8.3.0,>=8.2.0]
│   ├── numpy [required: >=1.19.0]  <-- Dependency chain
│   └── cymem [required: <2.1.0,>=2.0.2]
```

### 2. **pip-audit** - Security Checks
```bash
pip install pip-audit
pip-audit

# Checks for known vulnerabilities
```

### 3. **safety** - Vulnerability Scanner
```bash
pip install safety
safety check
```

---

## Project-Specific Recommendations

### For This Project (DDN AI System)

**1. Update requirements.txt with exact versions:**
```python
# implementation/requirements.txt

# Critical: Pin these exactly
numpy==1.24.4
scipy==1.11.4
spacy==3.7.5
thinc==8.2.5

# ML/DL: Pin major versions
torch==2.9.0
transformers==4.57.1
sentence-transformers==5.1.2

# Flexible: Allow minor updates
redis>=5.0.1,<6.0.0
celery>=5.3.0,<6.0.0
```

**2. Create requirements-lock.txt:**
```bash
cd implementation
pip freeze > requirements-lock.txt
```

**3. Document in README:**
```markdown
## Installation

Development:
pip install -r requirements.txt

Production:
pip install -r requirements-lock.txt
```

**4. Add pre-commit hook to check versions:**
```bash
# .git/hooks/pre-commit
python -c "import numpy; assert numpy.__version__ == '1.24.4', 'Wrong numpy version'"
python -c "import spacy; assert spacy.__version__ == '3.7.5', 'Wrong spacy version'"
```

---

## Handling Future Upgrades

### Safe Upgrade Process

**1. Check compatibility first:**
```bash
# Read release notes
# Check: https://github.com/explosion/spaCy/releases

# Check breaking changes
pip show spacy
# Version: 3.7.5
# Requires: numpy>=1.19.0  <-- Check this
```

**2. Test in isolated environment:**
```bash
# Create test virtualenv
python -m venv upgrade_test
upgrade_test\Scripts\activate

# Install new version
pip install spacy==3.8.0

# Run your tests
python -m pytest tests/

# If tests pass, update requirements.txt
deactivate
rm -rf upgrade_test
```

**3. Update incrementally:**
```bash
# Don't upgrade everything at once
# Upgrade one package at a time

# Step 1: Update spacy only
pip install spacy==3.8.0

# Step 2: Test
python -m pytest

# Step 3: If success, commit
git commit -m "Upgrade spacy 3.7.5 -> 3.8.0"
```

---

## Emergency Recovery (If Things Break)

### Quick Fix
```bash
# Reinstall from requirements-lock.txt
pip install -r requirements-lock.txt --force-reinstall

# Or downgrade specific packages
pip install numpy==1.24.4 scipy==1.11.4 spacy==3.7.5 thinc==8.2.5 --force-reinstall
```

### Full Reset
```bash
# Remove virtual environment
rm -rf venv/

# Recreate
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Continuous Integration Recommendations

### Add to CI/CD Pipeline

**GitHub Actions Example:**
```yaml
name: Test Dependencies

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements-lock.txt

      - name: Verify versions
        run: |
          python -c "import numpy; assert numpy.__version__ == '1.24.4'"
          python -c "import spacy; assert spacy.__version__ == '3.7.5'"

      - name: Run tests
        run: pytest tests/
```

---

## Monthly Dependency Audit Process

### Why Monthly Audits?

**Benefits:**
- Catch security vulnerabilities early
- Stay compatible with ecosystem changes
- Avoid "dependency debt" (outdated packages)
- Plan upgrades proactively vs. reactive firefighting

**Recommended Schedule:** First Monday of each month (20-30 minutes)

---

### Monthly Audit Checklist

#### 1. **Security Vulnerability Scan (5 min)**

```bash
# Run pip-audit (install if not present)
pip install pip-audit
pip-audit

# Alternative: Use safety
pip install safety
safety check
```

**Actions if vulnerabilities found:**
- **Critical/High:** Upgrade immediately (test first)
- **Medium:** Schedule upgrade within 2 weeks
- **Low:** Note for next quarterly review

---

#### 2. **Check for Outdated Packages (5 min)**

```bash
# List all outdated packages
pip list --outdated

# Save to file for review
pip list --outdated > monthly_audit_$(date +%Y-%m).txt
```

**Review output:**
- Note packages with major version increases (e.g., 1.x → 2.x)
- Note packages with minor version increases (e.g., 1.24.x → 1.25.x)
- Check release notes for breaking changes

---

#### 3. **Run Dependency Tests (5 min)**

```bash
# Run the automated dependency verification
python tests/test_dependencies.py

# Expected output: All critical packages passing
# If failures: Investigate immediately
```

**What to check:**
- numpy still on 1.24.x (not 2.x)
- scipy compatible with numpy
- spacy and thinc versions aligned
- No unexpected package upgrades

---

#### 4. **Check Dependency Tree for Conflicts (5 min)**

```bash
# Install pipdeptree if not present
pip install pipdeptree

# Check for conflicts
pipdeptree --warn

# Look for version conflicts in output
pipdeptree | grep -i "conflict\|incompatible"
```

**Common conflicts to watch for:**
- numpy version mismatches between packages
- Incompatible LangChain/LangGraph versions
- urllib3/requests version conflicts

---

#### 5. **Review Release Notes for Critical Packages (10 min)**

**Packages to monitor monthly:**

1. **numpy**
   - Check: https://github.com/numpy/numpy/releases
   - Look for: Security fixes, ABI changes

2. **spacy**
   - Check: https://github.com/explosion/spaCy/releases
   - Look for: Model updates, breaking changes

3. **langchain/langgraph**
   - Check: https://github.com/langchain-ai/langchain/releases
   - Look for: API changes, new features

4. **torch/transformers** (if using)
   - Check: https://github.com/pytorch/pytorch/releases
   - Look for: CUDA compatibility, model updates

**Create audit report:**
```markdown
# Dependency Audit - [Month Year]

## Security Scan
- [ ] pip-audit: [No issues / X vulnerabilities]
- [ ] safety check: [No issues / X vulnerabilities]

## Outdated Packages
- Critical packages: [List]
- Optional packages: [List]
- Action needed: [Yes/No]

## Test Results
- [ ] test_dependencies.py: [PASS/FAIL]
- Issues found: [None / List]

## Release Notes Review
- numpy: [Version, notes]
- spacy: [Version, notes]
- langchain: [Version, notes]

## Recommended Actions
1. [Action 1]
2. [Action 2]
...

## Next Audit Date
[First Monday of next month]
```

---

### Quarterly Deep Audit (Every 3 Months)

**In addition to monthly checks, do quarterly:**

#### 1. **Test Upgrade Paths**

```bash
# Create isolated test environment
python -m venv quarterly_test
quarterly_test\Scripts\activate

# Try upgrading to latest compatible versions
pip install numpy~=1.24.0 --upgrade
pip install scipy~=1.11.0 --upgrade

# Run full test suite
python -m pytest tests/

# Document results
deactivate
rm -rf quarterly_test
```

#### 2. **Review All Dependencies**

```bash
# Generate full dependency report
pip list > quarterly_deps_$(date +%Y-%m).txt

# Compare with previous quarter
diff quarterly_deps_2025-01.txt quarterly_deps_2025-04.txt
```

#### 3. **Update requirements-lock.txt**

```bash
# After testing, update frozen requirements
pip freeze > implementation/requirements-lock.txt
git commit -m "Update requirements-lock.txt - Q[X] [YEAR]"
```

---

### Annual Major Version Planning (Once Per Year)

**Plan major upgrades (e.g., numpy 2.x, Python 3.12):**

1. **Research Phase (Month 1)**
   - Read migration guides
   - Check ecosystem compatibility
   - Estimate effort/risk

2. **Testing Phase (Month 2)**
   - Create test branch
   - Upgrade packages in isolated env
   - Run full test suite
   - Document breaking changes

3. **Migration Phase (Month 3)**
   - Update code for compatibility
   - Update documentation
   - Deploy to staging
   - Monitor for issues

---

### Automation Tips

**Create monthly audit script:**

```bash
# scripts/monthly_audit.sh
#!/bin/bash

echo "=== MONTHLY DEPENDENCY AUDIT ==="
echo "Date: $(date)"
echo ""

echo "1. Security Scan"
pip-audit || echo "[WARNING] Vulnerabilities found"
echo ""

echo "2. Outdated Packages"
pip list --outdated
echo ""

echo "3. Dependency Tests"
python tests/test_dependencies.py
echo ""

echo "4. Dependency Tree Conflicts"
pipdeptree --warn
echo ""

echo "=== AUDIT COMPLETE ==="
echo "Review output and create audit report"
```

**Schedule reminder:**
- Add to calendar: First Monday of each month
- Assign owner: [Team member responsible]
- Duration: 30 minutes

---

### Emergency Audit Triggers

**Run audit immediately if:**
- Security advisory released for any dependency
- Production failure related to package version
- Before major deployment
- After Python version upgrade
- After system/OS upgrade

---

## Summary: What You Should Do NOW

### Immediate Actions

1. **✅ DONE: Downgraded to compatible versions**
   - numpy 1.24.4
   - scipy 1.11.4
   - spacy 3.7.5
   - thinc 8.2.5

2. **TODO: Create requirements-lock.txt**
   ```bash
   cd implementation
   pip freeze > requirements-lock.txt
   git add requirements-lock.txt
   git commit -m "Add frozen requirements"
   ```

3. **TODO: Update requirements.txt with constraints**
   ```python
   # Add version ranges instead of >=
   numpy>=1.24.0,<1.25.0
   scipy>=1.11.0,<1.12.0
   spacy==3.7.5
   ```

4. **TODO: Document in README**
   ```markdown
   ## Known Issues
   - Do NOT use `pip install --upgrade` on production dependencies
   - Use `requirements-lock.txt` for reproducible builds
   - numpy 2.x is not compatible - stay on 1.24.x
   ```

### Long-term Strategy

- **Monthly:** Review security updates with `pip-audit`
- **Quarterly:** Test minor version upgrades in isolated environment
- **Annually:** Plan major version upgrades (e.g., numpy 2.x migration)

---

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/en/latest/)
- [pip-tools Documentation](https://pip-tools.readthedocs.io/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [numpy 2.0 Migration Guide](https://numpy.org/devdocs/numpy_2_0_migration_guide.html)
- [Semantic Versioning](https://semver.org/)

---

**Remember:** Prevention is better than cure. Spend 10 minutes now to pin versions correctly, save hours debugging later!
