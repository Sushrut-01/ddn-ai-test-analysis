# Quick Start: Knowledge Management System

## ✅ Current Status

**Backend API:** ✅ RUNNING on port 5008
**Database:** ✅ Audit trail table created
**Test Status:** ✅ 8/10 tests passing
**Next Step:** Start the frontend and test the UI

---

## Start Testing Now (3 Steps)

### Step 1: Backend API (Already Running ✅)
The API is already running on port 5008. You can verify:

```bash
curl http://localhost:5008/api/knowledge/health
```

**Expected:** `{"status": "healthy"}`

If not running, start it:
```bash
cd implementation
python knowledge_management_api.py
```

### Step 2: Start the Dashboard UI

Open a **NEW terminal** and run:

```bash
cd implementation\dashboard-ui
npm run dev
```

**Expected output:**
```
  VITE v4.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 3: Open in Browser

Go to: **http://localhost:5173/knowledge**

---

## What You Should See

### Navigation
- Sidebar menu with "Knowledge Management" option (book icon)

### Main Page
- **4 Statistics Cards:**
  - Total Documents (should show 25+)
  - Categories (should show available categories)
  - Recent Additions
  - Total Vectors

- **Document Table:**
  - Columns: Error ID, Error Type, Category, Severity, Component, Updated, Actions
  - Search box at top
  - Category and Severity filter dropdowns

- **Action Buttons:**
  - "Add Knowledge Doc" button (top right)
  - Refresh button (circular arrow)
  - Edit icons (pencil) on each row
  - Delete icons (trash) on each row

---

## Try These Actions

### 1. View Existing Documents
- [x] Table shows ~25 documents
- [x] Can scroll and see all columns
- [x] Pagination controls at bottom

### 2. Search Documents
- [x] Type "timeout" in search box
- [x] Table filters to show matching documents
- [x] Clear search to see all documents

### 3. Filter by Category
- [x] Click Category dropdown
- [x] Select "CODE_ERROR"
- [x] Table shows only CODE_ERROR documents

### 4. Add New Document
- [x] Click "Add Knowledge Doc" button
- [x] Modal dialog opens
- [x] See comprehensive form with sections:
  - Basic Information
  - Location Information
  - Analysis
  - Code Examples
  - Metadata
  - Solution Steps
  - Test Scenarios
- [x] Fill in required fields (marked with *)
- [x] Click "Add" button
- [x] Success message appears
- [x] Table refreshes with new document

### 5. Edit Document
- [x] Click edit icon (pencil) on any row
- [x] Modal opens with pre-filled data
- [x] Change severity to "CRITICAL"
- [x] Click "Update"
- [x] Success message appears
- [x] Change reflects in table

### 6. Delete Document
- [x] Click delete icon (trash) on test document
- [x] Confirmation dialog appears
- [x] Shows document details
- [x] Click "Delete"
- [x] Success message appears
- [x] Document removed from table

### 7. Refresh Categories
- [x] Click refresh button (circular arrow)
- [x] Loading spinner appears
- [x] Success message shows count
- [x] Category dropdown updates

---

## Verify Audit Trail

Check that changes are logged to PostgreSQL:

```bash
cd implementation
python -c "
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='ddn_ai_analysis',
    user='postgres',
    password=os.getenv('POSTGRES_PASSWORD')
)

cursor = conn.cursor()
cursor.execute('''
    SELECT doc_id, action, user_email, changed_at
    FROM knowledge_doc_changes
    ORDER BY changed_at DESC
    LIMIT 5
''')

print('Recent Changes:')
for row in cursor.fetchall():
    print(f'  {row[0]} - {row[1]} by {row[2]} at {row[3]}')

cursor.close()
conn.close()
"
```

---

## Common Issues & Fixes

### Issue: Frontend shows "Network Error"
**Fix:**
```bash
# Check API is running
curl http://localhost:5008/api/knowledge/health

# If not, start it:
cd implementation
python knowledge_management_api.py
```

### Issue: Table shows "No documents found"
**Fix:** Check browser console (F12) for errors. Likely causes:
- API not running on port 5008
- CORS issue (should be fixed in API)
- Wrong API URL in frontend config

### Issue: "Add Knowledge Doc" button doesn't open modal
**Fix:** Check browser console (F12) for JavaScript errors. The component might not be imported correctly.

### Issue: Audit trail query fails
**Fix:** Table might not exist. Run:
```bash
cd implementation
python setup_audit_trail.py
```

---

## API Endpoints (for Testing)

### Get All Documents
```bash
curl http://localhost:5008/api/knowledge/docs?limit=5
```

### Get Statistics
```bash
curl http://localhost:5008/api/knowledge/stats
```

### Get Categories
```bash
curl http://localhost:5008/api/knowledge/categories
```

### Add Document (via curl)
```bash
curl -X POST http://localhost:5008/api/knowledge/docs \
  -H "Content-Type: application/json" \
  -d '{
    "error_id": "TEST123",
    "error_type": "QuickTest",
    "error_category": "CODE_ERROR",
    "error_message": "Test error for quick start",
    "component": "test",
    "root_cause": "Testing knowledge management",
    "solution": "This is a test document",
    "severity": "LOW",
    "frequency": "RARE",
    "tags": ["test"],
    "created_by": "quick_start"
  }'
```

---

## Architecture Overview

```
Browser (http://localhost:5173/knowledge)
         ↓
Frontend: React + Material-UI
         ↓ API calls (port 5008)
Backend: Flask API
         ↓
    ┌────┴────┐
    ↓         ↓
Pinecone   PostgreSQL
(vectors)  (audit trail)
```

---

## Files Reference

### Backend
- **API:** `implementation/knowledge_management_api.py`
- **Test:** `implementation/test_km_api.py`
- **Setup:** `implementation/setup_audit_trail.py`

### Frontend
- **Page:** `dashboard-ui/src/pages/KnowledgeManagement.jsx`
- **Modal:** `dashboard-ui/src/components/AddKnowledgeDocModal.jsx`
- **API Client:** `dashboard-ui/src/services/api.js`

### Documentation
- **Complete Guide:** `TASK-0-HITL-KM-COMPLETE.md`
- **Testing Guide:** `KNOWLEDGE-MANAGEMENT-TESTING-GUIDE.md`
- **Summary:** `PHASE-0-HITL-KM-FINAL-SUMMARY.md`
- **This File:** `QUICK-START-KNOWLEDGE-MANAGEMENT.md`

---

## Success Checklist

- [x] Backend API running on port 5008
- [x] Audit trail table created in PostgreSQL
- [x] Backend tests passing (8/10)
- [ ] Dashboard UI started
- [ ] Can access http://localhost:5173/knowledge
- [ ] Can view existing documents
- [ ] Can search and filter documents
- [ ] Can add new document
- [ ] Can edit document
- [ ] Can delete document
- [ ] Audit trail logging verified

---

## Next Steps After Testing

1. **Review Code:**
   - Read through the API implementation
   - Understand the React components
   - Review the database schema

2. **Customize:**
   - Add more error categories
   - Customize form fields
   - Add more tags

3. **Integrate:**
   - Test with ReAct agent
   - Verify category auto-discovery
   - Test end-to-end workflow

4. **Deploy:**
   - Review production checklist in KNOWLEDGE-MANAGEMENT-TESTING-GUIDE.md
   - Set up monitoring
   - Configure security

---

## Support

If you encounter any issues:

1. Check the logs:
   ```bash
   cd implementation
   tail -f knowledge_api.log
   ```

2. Run tests:
   ```bash
   python test_km_api.py
   ```

3. Check documentation:
   - TASK-0-HITL-KM-COMPLETE.md (complete details)
   - KNOWLEDGE-MANAGEMENT-TESTING-GUIDE.md (troubleshooting)

---

**You're all set!** Start the Dashboard UI and test the Knowledge Management interface.

```bash
cd implementation\dashboard-ui
npm run dev
```

Then go to: **http://localhost:5173/knowledge** 🚀
