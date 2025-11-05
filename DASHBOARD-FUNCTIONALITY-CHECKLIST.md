# DDN AI Dashboard - Functionality Checklist

**Dashboard URL:** http://localhost:5173

**Last Updated:** 2025-11-05

**✅ Latest Updates:**
- Service Manager API (port 5007) is NOW RUNNING
- Service Control Panel now fully functional
- TriggerAnalysis page error fixed
- ServiceControl component error handling improved

---

## ✅ CHECKLIST - Verify Each Item

### **1. MAIN DASHBOARD PAGE** (http://localhost:5173/)

**Header Section:**
- [ ] Purple gradient hero banner displays "DDN AI Test Failure Analysis"
- [ ] System overview statistics show total failures count
- [ ] "Enhanced Monitoring", "AI-Powered Analysis", "Real-time Status" chips visible

**System Status Cards (Top Row):**
- [ ] **MongoDB** card shows:
  - Status: Healthy (green) or Error (red)
  - Total failures: 581
  - Connection status
- [ ] **PostgreSQL** card shows:
  - Status: Healthy or Error
  - Total analyses: 20
  - Connection status
- [ ] **Pinecone Knowledge** card shows:
  - Status: Healthy or Error
  - Total vectors: 39
  - Purpose: "Error Documentation (Source A)"
- [ ] **Pinecone Failures** card shows:
  - Status: Healthy or Error
  - Total vectors: 10
  - Purpose: "Past Error Cases (Source B)"
- [ ] **AI Service** card shows:
  - Status: Error (expected - service not running on port 5000)
  - Error message displayed

**Statistics Cards (Middle Row):**
- [ ] **Total Test Failures** card shows: 581
- [ ] **Failures (Last 7 Days)** card shows: 271
- [ ] **AI Analyses** card shows: 20
- [ ] **Average Confidence** card shows: 90% (or calculated value)

**Recent Failures Table (Bottom Section):**
- [ ] Table displays last 10 test failures
- [ ] Columns visible:
  - Job Name
  - Error Message (truncated)
  - Aging (days since failure) with color coding:
    - Green: < 3 days
    - Orange: 3-7 days
    - Red: > 7 days
  - Analysis Status (Analyzed/Not Analyzed)
  - AI Recommendation (if analyzed)
  - Failed Time (relative, e.g., "2 days ago")
  - Actions (View/Analyze buttons)
- [ ] Clicking "View Details" navigates to failure details page
- [ ] Clicking "Analyze" button triggers AI analysis

---

### **2. FAILURES PAGE** (http://localhost:5173/failures)

**Filters Section:**
- [ ] Status filter dropdown (All, Pending, Analyzed, Not Analyzed)
- [ ] Job name filter dropdown
- [ ] Date range filter (Last 24h, 7d, 30d, All Time)
- [ ] Search box for error messages
- [ ] "Apply Filters" button
- [ ] "Clear Filters" button

**Failures List:**
- [ ] Displays all 581 test failures from MongoDB
- [ ] Pagination controls (showing 20 per page)
- [ ] Each failure card shows:
  - Build ID
  - Job name
  - Test name
  - Error message
  - Status badge
  - Timestamp
  - "View Details" button

**Functionality:**
- [ ] Filters work correctly
- [ ] Pagination navigates between pages
- [ ] Clicking failure opens detail view

---

### **3. FAILURE DETAILS PAGE** (http://localhost:5173/failures/BUILD_xxxxx)

**Failure Information:**
- [ ] Build ID displayed
- [ ] Job name displayed
- [ ] Test name displayed
- [ ] Full error message displayed
- [ ] Stack trace displayed (expandable)
- [ ] Build URL link (to Jenkins)
- [ ] Git branch and commit info
- [ ] Environment info

**AI Analysis Section:**
- [ ] Root cause analysis displayed (if analyzed)
- [ ] Fix recommendation displayed
- [ ] Confidence score shown (percentage)
- [ ] Analysis type (RAG_BASED, CLAUDE_DEEP_ANALYSIS)
- [ ] Processing time shown

**GitHub Code Integration (Task 0E):**
- [ ] Code snippets from GitHub displayed
- [ ] File paths shown with line numbers
- [ ] Syntax highlighting for code
- [ ] Links to GitHub repository

**Validation/Feedback Section (Phase 0-HITL):**
- [ ] Accept button (green)
- [ ] Reject button (red)
- [ ] Request Refinement button (orange)
- [ ] Feedback text area
- [ ] Validation status badge (pending/accepted/rejected/refining)
- [ ] Refinement history displayed (if any)

---

### **4. ANALYTICS PAGE** (http://localhost:5173/analytics)

**Summary Metrics:**
- [ ] Total analyses count
- [ ] Acceptance rate (%)
- [ ] Rejection rate (%)
- [ ] Refinement rate (%)
- [ ] Average confidence score

**Charts/Visualizations:**
- [ ] **Acceptance Rate Trend** (line chart)
  - Shows daily acceptance over time
- [ ] **Validation Status Distribution** (pie chart)
  - Breakdown: Accepted, Rejected, Pending, Refining
- [ ] **Confidence Score Distribution** (bar chart)
  - Shows distribution of AI confidence scores
- [ ] **Refinement Effectiveness** (chart)
  - Shows improvement after refinement

**Time Range Filter:**
- [ ] Last 7 days
- [ ] Last 30 days
- [ ] Last 90 days
- [ ] All time

---

### **5. MANUAL TRIGGER PAGE** (http://localhost:5173/manual-trigger)

**Trigger Form:**
- [ ] Build ID input field
- [ ] Error message textarea
- [ ] Stack trace textarea
- [ ] Job name input
- [ ] Test name input
- [ ] "Trigger AI Analysis" button

**Trigger History:**
- [ ] List of manually triggered analyses
- [ ] Shows:
  - Build ID
  - Triggered by user
  - Trigger time
  - Analysis status
  - Result link

**Functionality:**
- [ ] Form validation works
- [ ] Clicking "Trigger" sends request to API
- [ ] Success message displayed
- [ ] History updates after trigger

---

### **6. TRIGGER ANALYSIS (BULK)** (http://localhost:5173/trigger-analysis)

**Purpose:** Bulk analysis for multiple failures (Task 0F.7)

**Bulk Selection:**
- [ ] Checkbox to select multiple failures
- [ ] "Select All" checkbox
- [ ] Selected count display

**Bulk Actions:**
- [ ] "Analyze Selected" button
- [ ] Progress indicator during analysis
- [ ] Results summary after completion

**Filters:**
- [ ] Filter by status (Not Analyzed, Failed Analysis)
- [ ] Filter by job name
- [ ] Filter by date range

---

### **7. SERVICE CONTROL PANEL** (In Dashboard Main Page - Bottom Section)

**Purpose:** Control all DDN AI system services from the UI

**Quick Access Links:**
- [ ] MongoDB Atlas button (green gradient)
- [ ] Jira/Atlassian button (blue gradient)
- [ ] Pinecone button (teal gradient)
- [ ] Jenkins button (red gradient)
- [ ] n8n button (pink gradient)
- [ ] All buttons open in new tab when clicked

**Main Control Buttons:**
- [ ] "▶️ START ALL" button
- [ ] "⏹️ STOP ALL" button
- [ ] "🔄 RESTART ALL" button
- [ ] Buttons disabled during loading
- [ ] Confirmation dialog appears before starting/stopping

**Service Status Table:**
- [ ] Displays all 8 services:
  1. PostgreSQL Database (port 5432)
  2. AI Analysis Service (port 5000)
  3. Dashboard API (port 5006)
  4. Dashboard UI (port 5173)
  5. n8n Workflows (port 5678)
  6. Jenkins CI/CD (port 8081)
  7. Re-Ranking Service (port 5009)
  8. Knowledge Management API (port 5008)

- [ ] Each service row shows:
  - Service name
  - Port number
  - Status: ✅ Running or ❌ Stopped
  - Actions: ▶️ Start or ⏹️ Stop button
  - 🗑️ Remove button (to hide service)

**Hidden Services Section:**
- [ ] Shows count of hidden services in button: "👁️ Show Hidden Services (X)"
- [ ] Hidden services table appears when services are hidden
- [ ] "👁️ Show" button to restore hidden services
- [ ] "Show All Hidden" button at top

**Auto-Refresh:**
- [ ] Status updates every 5 seconds automatically
- [ ] No manual refresh needed

**Error Handling:**
- [ ] Shows friendly message if Service Manager API (port 5007) is not running
- [ ] Message: "Service Manager API not running (optional feature - use batch files instead)"
- [ ] Dashboard doesn't crash if service manager is offline

**Functionality Test:**
- [ ] Click "START ALL" - confirmation dialog appears
- [ ] Try starting individual service - button changes to "Stop"
- [ ] Hide a service - it moves to "Hidden Services" section
- [ ] Show hidden service - it returns to main table
- [ ] Status updates reflect actual service state

---

### **8. KNOWLEDGE MANAGEMENT PAGE** (http://localhost:5173/knowledge)

**Purpose:** Manage error documentation in Pinecone (Task 0-HITL-KM)

**Knowledge Documents List:**
- [ ] Displays all 39 knowledge documents from Pinecone
- [ ] Shows for each document:
  - Error type/category
  - Title
  - Description
  - Tags
  - Last updated date
  - Actions (View, Edit, Delete)

**Add New Document:**
- [ ] "+ Add Knowledge Doc" button
- [ ] Modal/form with fields:
  - Error type
  - Category
  - Title
  - Description
  - Solution/fix
  - Tags
  - Related errors
- [ ] "Save" button
- [ ] "Cancel" button

**Edit/Delete:**
- [ ] Edit button opens document in edit mode
- [ ] Delete button removes document (with confirmation)
- [ ] Audit trail recorded for changes

**Search/Filter:**
- [ ] Search box for documents
- [ ] Filter by category
- [ ] Filter by error type

**Statistics:**
- [ ] Total documents count: 39
- [ ] Documents by category breakdown
- [ ] Recent changes log

---

## 🔌 BACKEND API ENDPOINTS

### **Core APIs (Port 5006)**

**Health & Status:**
- [ ] GET `/api/health` - Returns service health
- [ ] GET `/api/system/status` - Returns all components status
- [ ] GET `/api/stats` - Returns system statistics

**Failures:**
- [ ] GET `/api/failures` - List all failures (with pagination)
- [ ] GET `/api/failures/:buildId` - Get single failure details

**Analytics:**
- [ ] GET `/api/analytics/summary` - Get summary metrics
- [ ] GET `/api/analytics/acceptance-rate` - Get acceptance rate data
- [ ] GET `/api/analytics/refinement-stats` - Get refinement statistics
- [ ] GET `/api/analytics/trends` - Get trend data

**Manual Trigger:**
- [ ] POST `/api/trigger/manual` - Trigger manual analysis
- [ ] GET `/api/trigger/history` - Get trigger history

**Feedback:**
- [ ] POST `/api/feedback/submit` - Submit validation feedback
- [ ] GET `/api/feedback/recent` - Get recent feedback
- [ ] GET `/api/feedback/refinement-history/:buildId` - Get refinement history

**Pipeline/Monitoring:**
- [ ] GET `/api/pipeline/flow` - Get pipeline flow data
- [ ] GET `/api/activity` - Get recent activity log

### **Knowledge Management API (Port 5008)**

- [ ] GET `/api/knowledge/docs` - List all knowledge documents
- [ ] GET `/api/knowledge/docs/:id` - Get single document
- [ ] POST `/api/knowledge/docs` - Add new document
- [ ] PUT `/api/knowledge/docs/:id` - Update document
- [ ] DELETE `/api/knowledge/docs/:id` - Delete document
- [ ] GET `/api/knowledge/categories` - Get available categories
- [ ] GET `/api/knowledge/stats` - Get knowledge base stats

---

## 🗄️ DATABASE STATUS

### **PostgreSQL (localhost:5432)**

**Tables:**
- [ ] `failure_analysis` - 20 analyses stored
- [ ] `build_metadata` - Build information
- [ ] `user_feedback` - Validation feedback
- [ ] `acceptance_tracking` - Validation lifecycle
- [ ] `refinement_history` - Refinement iterations
- [ ] `manual_trigger_log` - Manual trigger records
- [ ] `ai_model_metrics` - AI performance metrics
- [ ] `knowledge_doc_changes` - Audit trail for knowledge docs

**Required Columns Added:**
- [ ] `user_feedback.validation_status`
- [ ] `user_feedback.feedback_timestamp`
- [ ] `user_feedback.failure_id`
- [ ] `failure_analysis.analyzed_at`
- [ ] `failure_analysis.classification`
- [ ] `refinement_history.failure_id`
- [ ] `refinement_history.refinement_timestamp`

### **MongoDB Atlas (Cloud)**

- [ ] Connected successfully
- [ ] 581 test failures stored
- [ ] Auto-populated from Jenkins test runs

### **Pinecone (Cloud)**

- [ ] **ddn-knowledge-docs** index: 39 vectors
- [ ] **ddn-error-library** index: 10 vectors
- [ ] Both connected successfully

---

## 🎨 UI/UX FEATURES

**Layout:**
- [ ] Responsive sidebar menu
- [ ] Top app bar with title
- [ ] Mobile-friendly design
- [ ] Smooth navigation between pages

**Menu Items (Sidebar):**
- [ ] Dashboard
- [ ] Failures
- [ ] Analytics
- [ ] Manual Trigger
- [ ] Trigger Analysis (Bulk)
- [ ] Knowledge Management

**Visual Features:**
- [ ] Material-UI theme applied
- [ ] Purple/blue color scheme
- [ ] Status badges with colors (green/red/orange)
- [ ] Loading spinners during data fetch
- [ ] Error boundaries catch crashes
- [ ] Tooltips on hover
- [ ] Icons for visual context

**Data Refresh:**
- [ ] Dashboard auto-refreshes every 10 seconds
- [ ] Failures list auto-refreshes every 20 seconds
- [ ] Analytics refresh every 30 seconds

---

## ⚙️ SERVICES STATUS

**Required Services:**
- [x] PostgreSQL running (port 5432) ✅
- [x] MongoDB Atlas connected (cloud) ✅
- [x] Pinecone connected (cloud) ✅
- [x] Dashboard API running (port 5006) ✅
- [x] Dashboard UI running (port 5173) ✅
- [x] **Service Manager API running (port 5007) ✅ NOW WORKING**

**Optional Services:**
- [ ] AI Analysis Service (port 5000) - NOT required for dashboard viewing
- [ ] Knowledge Management API (port 5008) - for knowledge management features
- [ ] Re-ranking Service (port 5009) - for Phase 2 features
- [ ] n8n Workflow (port 5678) - for automation

**How to Start Service Manager API:**
Run the batch file: `START-SERVICE-MANAGER.bat`

---

## 🐛 KNOWN ISSUES / LIMITATIONS

**API Issues:**
- [ ] Some analytics endpoints return errors due to missing data
- [ ] Refinement stats may show errors (missing historical data)
- [ ] AI Service offline (expected - not critical for viewing)

**Database Issues:**
- [ ] Some columns may still be missing in older tables
- [ ] Empty tables: refinement_history (no refinements yet)

**Functionality Not Implemented Yet:**
- [ ] Code fix automation (Phase B)
- [ ] Automatic PR creation
- [ ] GitHub integration for code fixes
- [ ] Advanced analytics visualizations

---

## 📊 DATA SUMMARY

**Current Data in System:**
- **Test Failures:** 581 (from Jenkins)
- **AI Analyses:** 20
- **Knowledge Documents:** 39
- **Error Cases:** 10
- **User Feedback:** 0 (no feedback submitted yet)
- **Refinements:** 0 (no refinements yet)

---

## ✅ VERIFICATION STEPS

### **Quick Verification:**

1. **Open Dashboard:** http://localhost:5173
   - ✓ Should load without white screen
   - ✓ Should show system status cards
   - ✓ Should display recent failures table

2. **Test Navigation:**
   - Click "Failures" in sidebar
   - Click "Analytics" in sidebar
   - Click "Knowledge Management" in sidebar
   - ✓ Pages should load (may show "no data" but shouldn't crash)

3. **Test API Connectivity:**
   ```bash
   curl http://localhost:5006/api/health
   curl http://localhost:5006/api/failures?limit=1
   curl http://localhost:5006/api/system/status
   ```
   - ✓ All should return JSON responses

4. **Check Data:**
   - ✓ Dashboard shows 581 failures
   - ✓ System status shows MongoDB: 581, PostgreSQL: 20
   - ✓ Pinecone shows 39 + 10 vectors

---

## 🎯 WHAT SHOULD WORK NOW

**✅ WORKING (2025-11-05 Update):**
1. Dashboard loads without white screen ✅
2. System status cards display ✅
3. Recent failures table shows 10 failures ✅
4. Navigation between pages works ✅
5. API endpoints respond correctly ✅
6. Database connections work ✅
7. Error boundaries catch crashes ✅
8. **Service Control Panel fully functional ✅ NEW**
9. **Service Manager API running on port 5007 ✅ NEW**
10. **Trigger Analysis page loads without errors ✅ FIXED**
11. **ServiceControl component handles API errors gracefully ✅ FIXED**

**⚠️ MAY NOT WORK:**
1. Analytics charts (missing historical data)
2. Refinement stats (no refinements yet)
3. Some advanced features (Phase B not implemented)
4. GitHub code integration (if GitHub service not configured)

**❌ NOT WORKING (EXPECTED):**
1. AI Service (port 5000) - offline, not critical
2. Code fix automation - Phase B not implemented
3. Some analytics due to missing database columns

---

## 📝 NEXT STEPS IF ISSUES FOUND

**If a page shows white screen:**
1. Open browser console (F12)
2. Note the error message
3. Report: "Page X shows error: [error message]"

**If a feature doesn't work:**
1. Describe which button/feature
2. What you expected to happen
3. What actually happened

**If data is missing:**
1. Check if service is running
2. Check API endpoint manually
3. Check database has data

---

**Use this checklist to verify each item. Mark with ✓ what works, ✗ what doesn't work.**
