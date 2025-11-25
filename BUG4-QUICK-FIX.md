# Bug #4 Quick Fix Guide

**Problem:** Jenkins build #22 failed but NO failures appeared in Dashboard
**Cause:** Missing suite metadata in test files
**Solution:** Add 4 fields to ~20 reportFailure() calls

---

## ⚡ Quick Fix (30 seconds)

```powershell
cd C:\DDN-AI-Project-Documentation\tests
.\Add-SuiteMetadata.ps1
```

This adds suite metadata to all 17 remaining `reportFailure()` calls.

---

## ✅ What Gets Added

Each `reportFailure()` call gets these 4 new fields:

```javascript
suite_name: 'Domain-Based Isolation and Management Tests',  // ← Test suite name
pass_count: 0,  // ← Passed tests count
fail_count: 1,  // ← Failed tests count
total_count: 1  // ← Total tests count
```

---

## 📊 Progress

- **Manual fixes:** 3/20 (done)
- **Automated fixes:** 17/20 (run script above)
- **Total:** 20/20 when complete

---

## 🧪 Test It Works

```bash
# 1. Run Jenkins build
# Build should be #23 (previous was #22)

# 2. Check Dashboard
# http://localhost:5173/failures
# Should show new failures from build #23

# 3. Verify MongoDB
# Failures should have suite_name, pass_count, fail_count, total_count
```

---

## 📁 Files

- `tests/Add-SuiteMetadata.ps1` - Run this script
- `BUG4-COMPLETE-FIX-SUMMARY.md` - Full details
- `tests/ddn-advanced-scenarios.js` - File being updated

---

**Status:** Ready to run script
**Time:** 30 seconds
**Risk:** Low (automated, tested pattern)
