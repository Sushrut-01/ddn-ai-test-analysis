# Phase 3 Hybrid Search - Dependency Fix Plan

## Issue Analysis - November 4, 2025

### Current Problem
When trying to start `hybrid_search_service.py`, we get:
```
Exception: The official Pinecone python package has been renamed from
`pinecone-client` to `pinecone`. Please remove `pinecone-client` from
your project dependencies and add `pinecone` instead.
```

## Root Cause Analysis

### 1. **Pinecone Package Naming Conflict** 🔴 CRITICAL
**Problem**: Project uses both old and new Pinecone package names inconsistently

**Current State**:
- `requirements.txt` specifies: `pinecone-client==5.0.1` (OLD)
- 18 files import: `from pinecone import Pinecone` (NEW package syntax)
- Virtual environment has: `pinecone-client==6.0.0` (installed but incompatible)

**Affected Files** (18 files):
```
ai_analysis_service.py
dashboard_api_full.py
hybrid_search_service.py
knowledge_management_api.py
start_dashboard_api_port5006.py
retrieval/fusion_rag_service.py
retrieval/build_bm25_index.py
migrate_templates_to_pinecone.py
migrate_to_dual_index.py
create_dual_pinecone_indexes.py
load_error_docs_to_pinecone.py
recreate_pinecone_index.py
test_dual_index_rag.py
test_pinecone_connection.py
test_rag_query.py
evaluation/scripts/check_pinecone.py
... (3 more)
```

### 2. **NumPy Version Mismatch** ⚠️ HIGH
**Problem**: Installed numpy 2.3.4 conflicts with requirements

**Current State**:
- `requirements.txt` specifies: `numpy>=1.24.0,<1.25.0` (for compatibility)
- Virtual environment has: `numpy==2.3.4` (breaks compatibility)

**Impact**:
- May break `sentence-transformers`, `spacy`, `presidio`
- These packages were designed for numpy 1.x

### 3. **Missing PostgreSQL Driver** ⚠️ MEDIUM
**Problem**: BM25 index builder needs PostgreSQL connection

**Current State**:
- `build_bm25_index.py` imports `psycopg2`
- Not installed in virtual environment

### 4. **BM25 Index Files Status** ℹ️ INFO
**Problem**: Need to verify if index files exist

**Files needed**:
- `implementation/bm25_index.pkl`
- `implementation/bm25_documents.pkl`

---

## Resolution Plan

### Option A: Minimal Fix (Quick - 15 min)
**Pros**: Fast, minimal changes
**Cons**: Leaves old package references in requirements.txt

1. ✅ Uninstall `pinecone-client`
2. ✅ Install `pinecone>=5.0.0`
3. ✅ Downgrade `numpy` to `1.24.x`
4. ✅ Install `psycopg2-binary`
5. ✅ Test service startup

### Option B: Full Resolution (Thorough - 45 min)
**Pros**: Clean, consistent, future-proof
**Cons**: More changes, needs testing

1. ✅ Update `requirements.txt` to use `pinecone` instead of `pinecone-client`
2. ✅ Verify all 18 files use correct import syntax
3. ✅ Fix numpy version to `1.24.x`
4. ✅ Add `psycopg2-binary` to requirements
5. ✅ Reinstall all dependencies from requirements.txt
6. ✅ Test all services (not just hybrid search)
7. ✅ Update documentation

---

## Recommended Approach: **Option A First, Then B**

### Phase 1: Get Hybrid Search Working (Now)
```bash
# 1. Fix Pinecone package
pip uninstall -y pinecone-client
pip install "pinecone>=5.0.0"

# 2. Fix NumPy version
pip uninstall -y numpy
pip install "numpy>=1.24.0,<1.25.0"

# 3. Install PostgreSQL driver
pip install psycopg2-binary

# 4. Test
python hybrid_search_service.py
```

### Phase 2: Clean Up Project (Later)
1. Update `requirements.txt`:
   - Change `pinecone-client==5.0.1` → `pinecone>=5.0.0`
   - Ensure `numpy>=1.24.0,<1.25.0`
   - Add `psycopg2-binary==2.9.10`

2. Test other services:
   - `python ai_analysis_service.py`
   - `python dashboard_api_full.py`
   - `python knowledge_management_api.py`

3. Update project documentation

---

## Dependency Tree

```
hybrid_search_service.py
├── flask (✅ installed)
├── flask-cors (✅ installed)
├── python-dotenv (✅ installed)
├── rank-bm25 (✅ installed)
├── numpy (⚠️ wrong version - needs 1.24.x)
├── pinecone (❌ needs new package)
└── openai (✅ installed)

build_bm25_index.py
├── psycopg2 (❌ missing - needs psycopg2-binary)
├── python-dotenv (✅ installed)
├── rank-bm25 (✅ installed)
└── numpy (⚠️ wrong version)
```

---

## Risk Assessment

### Low Risk ✅
- Installing new `pinecone` package (widely used, stable)
- Downgrading numpy to 1.24.x (tested in requirements)
- Installing psycopg2-binary (standard PostgreSQL driver)

### Medium Risk ⚠️
- Uninstalling `pinecone-client` while other services running
  - **Mitigation**: Stop all services first

### High Risk 🔴
- Breaking existing services that depend on Pinecone
  - **Mitigation**: Test each service after changes

---

## Testing Checklist

After implementing Option A:
- [ ] `python hybrid_search_service.py` starts without errors
- [ ] Can access `http://localhost:5005/health`
- [ ] `python build_bm25_index.py` connects to PostgreSQL
- [ ] BM25 index builds successfully
- [ ] `python test_hybrid_search_phase3.py` all tests pass

After implementing Option B (if needed):
- [ ] `python ai_analysis_service.py` starts
- [ ] `python dashboard_api_full.py` starts
- [ ] `python knowledge_management_api.py` starts
- [ ] All Pinecone-dependent tests pass

---

## Commands to Execute (Option A)

```powershell
# Stop any running services first
# Then in virtual environment:

# Step 1: Fix Pinecone
pip uninstall -y pinecone-client
pip install "pinecone>=5.0.0"

# Step 2: Fix NumPy (CRITICAL for compatibility)
pip uninstall -y numpy
pip install "numpy>=1.24.0,<1.25.0"

# Step 3: Add PostgreSQL
pip install psycopg2-binary

# Step 4: Verify installations
pip list | findstr /i "pinecone numpy psycopg"

# Step 5: Test
cd implementation
python hybrid_search_service.py
```

---

## Success Criteria

✅ **Hybrid Search Service**:
- Starts without errors
- Loads BM25 index successfully
- Connects to Pinecone
- Health endpoint returns 200 OK

✅ **No Breaking Changes**:
- Other services still work
- No import errors
- No runtime errors

---

## Rollback Plan

If something breaks:

```powershell
# Rollback to pinecone-client
pip uninstall -y pinecone
pip install pinecone-client==5.0.1

# Restore numpy if needed
pip install numpy==2.3.4
```

---

## Next Steps After Fix

1. ✅ Complete Phase 3 Task 3.6 (Integration with langgraph_agent.py)
2. ✅ Test end-to-end hybrid search
3. ✅ Update requirements.txt permanently
4. ✅ Document dependency management best practices

---

**Decision Needed**: Which option should we proceed with?
- **Option A** (Quick Fix): Get hybrid search working now
- **Option B** (Full Fix): Clean up entire project

**Recommendation**: Start with Option A to unblock Phase 3, then schedule Option B for next maintenance window.
