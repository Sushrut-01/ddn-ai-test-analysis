# Preview Pages - Features Checklist

---

## 7. Failure Details Preview (`/failure-details-preview`) ✅ COMPLETE

### This is the MOST IMPORTANT page - Shows AI Analysis Results!

**User needs to see:**
1. **Error in Code** - What went wrong (error message, stack trace)
2. **AI Analysis** - Root cause analysis by AI
3. **AI Suggestion** - Recommended fix
4. **Before/After View** - Original code vs Suggested fix
5. **Validation Buttons** - Accept / Reject / Refine

### Currently Has (Mock Data):
- [x] Blue gradient header with build info
- [x] **Quick Access Links Section** - Verify before approving:
  - [x] GitHub Test Case button
  - [x] GitHub Source Code button
  - [x] Jenkins Build Page button
  - [x] Jenkins Console Output button
  - [x] Jenkins Test Report button
  - [x] Jenkins XML Report button
  - [x] Allure Report button
  - [x] Build Artifacts button
- [x] Error Message display (red box)
- [x] AI Root Cause Analysis (green box)
- [x] AI Fix Recommendation (blue box)
- [x] **Before/After Code Comparison** (side-by-side dark theme)
- [x] Stack Trace viewer (dark theme tab)
- [x] Full Failure Data tab (JSON)
- [x] Similar Errors tab
- [x] **Feedback History tab** (when refinements exist)
- [x] Confidence Score with progress bar
- [x] Severity Badge (HIGH/MEDIUM/LOW)
- [x] Classification Chip (CODE_ERROR, TEST_FAILURE, etc.)
- [x] **Accept/Reject/Refine buttons**
- [x] **Feedback Dialog** with text input
- [x] **Re-analysis progress indicator**
- [x] Snackbar notifications
- [x] Test Information sidebar

### Needs to Add (API Integration):
- [ ] Connect to `failuresAPI.getDetails(buildId)` for real failure data
- [ ] Connect to `feedbackAPI.submit()` for Accept/Reject/Refine
- [ ] Connect to `feedbackAPI.getRefinementHistory()` for refinement history
- [ ] Replace simple dialog with existing `FeedbackModal` component
- [ ] Use existing `BeforeAfterComparison` component for refinement comparison
- [ ] Add react-query hooks with polling during refinement
- [ ] Connect to `fixAPI.approve()` for code fix approval
- [ ] Connect to `fixAPI.reject()` for code fix rejection
- [ ] Use existing `SimilarErrorsDisplay` component
- [ ] Use existing `CodeSnippet` component for syntax highlighting
- [ ] Use existing `CodeFixApproval` component for fix approval tab
- [ ] Dynamic URL generation from failure data (GitHub, Jenkins)
- [ ] Add loading states
- [ ] Add error handling

### Existing Components to Integrate:
- `BeforeAfterComparison.jsx` - Shows original vs refined analysis with timeline
- `FeedbackModal.jsx` - Structured feedback with dropdown reasons + multi-select options
- `CodeSnippet.jsx` - Display code with syntax highlighting
- `SimilarErrorsDisplay.jsx` - Show similar past errors
- `CodeFixApproval.jsx` - Approve/reject/feedback for code fixes
- `FeedbackStatusBadge.jsx` - Show validation status

### Existing API Flow (in FailureDetails.jsx):
```javascript
// Accept
feedbackAPI.submit({ build_id, feedback_type: 'accept', validation_status: 'accepted' })

// Reject/Refine (opens FeedbackModal)
feedbackAPI.submit({
  build_id,
  feedback_type: 'reject' | 'refine',
  validation_status: 'rejected' | 'refining',
  reason: selectedReason,
  comment: userComment,
  suggestion: refinementSuggestion,
  refinement_options: selectedOptions
})

// Get refinement history
feedbackAPI.getRefinementHistory(buildId)

// Auto-refresh polling when refining
useQuery(['failure-details', buildId], ..., { refetchInterval: isRefining ? 5000 : false })
```

---

This document tracks what needs to be added to each preview page to make them production-ready.

---

## 1. Dashboard Preview (`/dashboard-preview`)

### Currently Has (Mock Data):
- [x] Modern header with gradient
- [x] Service Control Panel (Modern version)
- [x] Stats cards (Total Failures, AI Analyses, Pass Rate, Confidence)
- [x] System Health cards (MongoDB, PostgreSQL, Pinecone, AI Service)
- [x] Test Execution Trends chart
- [x] Test Status Distribution pie chart
- [x] Failure Categories progress bars
- [x] AI Validation Status chart
- [x] Acceptance Rate Trend chart
- [x] Recent Test Failures table
- [x] Footer info card

### Needs to Add (API Integration):
- [ ] Connect to `monitoringAPI.getSystemStatus()` for real system health
- [ ] Connect to `monitoringAPI.getStats()` for real stats
- [ ] Connect to `failuresAPI.getList()` for recent failures
- [ ] Connect to `analyticsAPI.getAcceptanceRate()` for validation data
- [ ] Connect to `analyticsAPI.getRefinementStats()` for refinement metrics
- [ ] Add react-query hooks for auto-refresh
- [ ] Add loading states with spinners
- [ ] Add error handling with alerts
- [ ] Navigate to failure details on row click

---

## 2. Failures Preview (`/failures-preview`)

### Currently Has (Mock Data):
- [x] Red gradient header
- [x] Stats cards (Total, Analyzed, Pending, Resolved)
- [x] Search input
- [x] Category filter dropdown
- [x] Validation status filter
- [x] Modern table with all columns
- [x] Aging days chips with colors
- [x] AI confidence progress bars
- [x] Pagination

### Needs to Add (API Integration):
- [ ] Connect to `failuresAPI.getList()` with pagination
- [ ] Implement search functionality with API
- [ ] Implement category filter with API
- [ ] Implement validation status filter with API
- [ ] Add `FeedbackStatusBadge` component for validation status
- [ ] Navigate to `/failures/:buildId` on row click
- [ ] Add loading spinner during data fetch
- [ ] Add error alert on API failure
- [ ] Add "Export" button functionality
- [ ] Calculate real stats from API data

---

## 3. Analytics Preview (`/analytics-preview`)

### Currently Has (Mock Data):
- [x] Purple gradient header
- [x] Time range toggle (7d, 30d, 90d)
- [x] Key metric cards
- [x] Acceptance Rate Trend area chart
- [x] Validation Distribution pie chart
- [x] Error Category Trends bar chart
- [x] Confidence Distribution progress bars
- [x] Top Failure Patterns table

### Needs to Add (API Integration):
- [ ] Connect to `analyticsAPI.getAcceptanceRate(timeRange)`
- [ ] Connect to `analyticsAPI.getRefinementStats(timeRange)`
- [ ] Connect to `analyticsAPI.getTrends(timeRange)` (when implemented)
- [ ] Connect to `analyticsAPI.getPatterns()` (when implemented)
- [ ] Time range toggle should trigger API refetch
- [ ] Add loading states for each chart
- [ ] Add error handling for failed API calls
- [ ] Format dates properly with date-fns

---

## 4. Manual Trigger Preview (`/manual-trigger-preview`)

### Currently Has (Mock Data):
- [x] Cyan gradient header
- [x] Trigger form (Build ID, Email, Reason)
- [x] Trigger button with loading state
- [x] Success alert
- [x] Info card with usage instructions
- [x] Trigger history table with mock data

### Needs to Add (API Integration):
- [ ] Connect to `triggerAPI.triggerAnalysis()` for triggering
- [ ] Connect to `triggerAPI.getHistory()` for history table
- [ ] Add form validation (required fields)
- [ ] Add react-query mutation for trigger
- [ ] Invalidate history query after successful trigger
- [ ] Add error alert on trigger failure
- [ ] Add pagination to history table
- [ ] Show real trigger status (success/failed)

---

## 5. Trigger Analysis Preview (`/trigger-analysis-preview`)

### Currently Has (Mock Data):
- [x] Orange gradient header
- [x] Stats cards (Pending, Analyzing, Completed, Selected)
- [x] Select All / Deselect All buttons
- [x] Trigger button with count
- [x] Progress bar during analysis
- [x] Table with checkboxes
- [x] Status chips (pending, analyzing, completed, failed)

### Needs to Add (API Integration):
- [ ] Connect to `failuresAPI.getList()` filtered for unanalyzed
- [ ] Connect to `triggerAPI.triggerAnalysis()` for bulk trigger
- [ ] Implement real progress tracking during bulk analysis
- [ ] Add react-query for auto-refresh every 10 seconds
- [ ] Update status in real-time as analyses complete
- [ ] Add snackbar notifications for success/failure
- [ ] Disable checkboxes for non-pending items
- [ ] Add error handling

---

## 6. Knowledge Management Preview (`/knowledge-preview`)

### Currently Has (Mock Data):
- [x] Green gradient header
- [x] Stats cards (Total Docs, Categories, Usage, Critical)
- [x] Search input
- [x] Category filter
- [x] Severity filter
- [x] Documents table
- [x] View/Edit/Delete action buttons
- [x] Add Document dialog (UI only)
- [x] Pagination

### Needs to Add (API Integration):
- [ ] Connect to `knowledgeAPI.getDocs()` for documents list
- [ ] Connect to `knowledgeAPI.getCategories()` for categories
- [ ] Connect to `knowledgeAPI.getStats()` for statistics
- [ ] Implement `knowledgeAPI.createDoc()` in Add dialog
- [ ] Implement `knowledgeAPI.updateDoc()` for Edit
- [ ] Implement `knowledgeAPI.deleteDoc()` with confirmation
- [ ] Connect to `knowledgeAPI.refreshCategories()` for Sync button
- [ ] Add `AddKnowledgeDocModal` component
- [ ] Add search functionality with API
- [ ] Add filter functionality with API
- [ ] Add loading states
- [ ] Add success/error notifications

---

## Common Components Needed

These components from the original pages should be integrated:

1. **FeedbackStatusBadge** - Shows validation status with tooltip
2. **FeedbackModal** - For accepting/rejecting/refining analyses
3. **CodeSnippet** - For displaying code in failure details
4. **DiffView** - For showing before/after comparisons
5. **SimilarErrorsDisplay** - For showing similar past errors
6. **BeforeAfterComparison** - For code fix visualization

---

## API Services Reference

Located in `/src/services/api.js`:

```javascript
// Monitoring
monitoringAPI.getSystemStatus()
monitoringAPI.getStats()

// Failures
failuresAPI.getList({ skip, limit, category, feedback_status, search })
failuresAPI.getById(id)
failuresAPI.triggerAnalysis(id)

// Analytics
analyticsAPI.getAcceptanceRate(timeRange)
analyticsAPI.getRefinementStats(timeRange)
analyticsAPI.getTrends(timeRange, granularity)
analyticsAPI.getPatterns()

// Triggers
triggerAPI.triggerAnalysis({ build_id, triggered_by_user, reason })
triggerAPI.getHistory(page, limit)

// Knowledge
knowledgeAPI.getDocs({ category, severity, search, limit })
knowledgeAPI.getCategories()
knowledgeAPI.getStats()
knowledgeAPI.createDoc(data)
knowledgeAPI.updateDoc(id, data)
knowledgeAPI.deleteDoc(id)
knowledgeAPI.refreshCategories()
```

---

## 8. Services Monitoring Preview (`/services-preview`) ✅ COMPLETE

### Comprehensive monitoring for all backend services including Langfuse, Celery, Redis, n8n

### Currently Has (Mock Data):
- [x] Purple gradient header with service count
- [x] Quick stats (Total Services, LLM Traces, Tasks Processed, Cache Hit Rate)
- [x] **All Services Tab** - Complete service list with status, ports, memory usage
- [x] **Langfuse Tab** - LLM Observability:
  - [x] Total traces, generations, avg latency
  - [x] Token usage and cost breakdown
  - [x] Model usage table (Gemini, GPT-4, Claude)
  - [x] Latency trend chart
  - [x] Recent traces table with status
- [x] **Celery Tasks Tab** - Task Queue Monitoring:
  - [x] Active workers count
  - [x] Tasks processed/queued/succeeded/failed
  - [x] Worker status table
  - [x] Task trend chart (success/failed)
  - [x] Recent tasks table
- [x] **Redis Cache Tab** - Cache Monitoring:
  - [x] Memory usage, total keys, hit rate
  - [x] Cache performance (hits/misses/expired)
  - [x] Key distribution pie chart
- [x] **n8n Workflows Tab** - Workflow Automation:
  - [x] Total/active workflows
  - [x] Execution count and success rate
  - [x] Workflow list with status
- [x] Quick links to open external dashboards (Langfuse, Flower, n8n)

### Needs to Add (API Integration):
- [ ] Create `/api/services/status` endpoint to aggregate all service health
- [ ] Langfuse API integration:
  - [ ] Fetch traces from Langfuse API (`/api/public/traces`)
  - [ ] Fetch generations from Langfuse API (`/api/public/generations`)
  - [ ] Calculate token usage and costs
- [ ] Celery/Flower API integration:
  - [ ] Connect to Flower API (`/api/workers`, `/api/tasks`)
  - [ ] Get real-time worker status
  - [ ] Get task history and stats
- [ ] Redis stats integration:
  - [ ] Add Redis INFO command endpoint to dashboard API
  - [ ] Fetch memory, keys, ops/sec stats
- [ ] n8n API integration:
  - [ ] Connect to n8n API for workflow status
  - [ ] Get execution history
- [ ] Add react-query hooks for auto-refresh
- [ ] Add WebSocket support for real-time updates

### External Dashboards (Already Available):
- **Langfuse UI:** http://localhost:3000
- **Flower UI:** http://localhost:5555
- **n8n UI:** http://localhost:5678

---

## 9. Pipeline Status Preview (`/pipeline-preview`) ✅ COMPLETE

### Real-time tracking of AI analysis pipeline stages

### Currently Has (Mock Data):
- [x] Cyan gradient header with active/queued counts
- [x] **Pipeline Stages Overview** - Visual stepper showing all stages:
  - Trigger Received → Queued in Celery → ReAct Agent Analysis → CRAG Verification → Gemini Formatting → Complete
- [x] **Active Analyses Panel**:
  - [x] Job cards with build ID, test name, trigger type
  - [x] Real-time progress stepper for each job
  - [x] Current stage progress bar with percentage
  - [x] Estimated time remaining
  - [x] Expandable details showing all stage durations
  - [x] Auto-updating progress every 2 seconds (simulated)
- [x] **Recent Completed Analyses Table**:
  - [x] Build ID, test name, trigger type
  - [x] Success/Failed status
  - [x] Total duration
  - [x] Completion time

### Needs to Add (API Integration):
- [ ] Connect to Celery task status API for real job tracking
- [ ] WebSocket connection for real-time updates
- [ ] Fetch active tasks from Redis queue
- [ ] Connect to analysis service for stage progress
- [ ] Historical job data from database

---

## 10. Jira Bugs Preview (`/jira-bugs-preview`) ✅ COMPLETE

### Bug creation from validated AI analyses and bug tracking

### Currently Has (Mock Data):
- [x] Blue gradient header with "Create Bug" button
- [x] Stats cards (Total, Open, In Progress, Resolved)
- [x] Search and filter controls (status, priority)
- [x] **Bugs Table**:
  - [x] Bug ID with Jira link chip
  - [x] Title with AI icon indicator
  - [x] Status chip (Open, In Progress, Resolved, Closed)
  - [x] Priority chip (Critical, High, Medium, Low)
  - [x] Linked failure reference
  - [x] AI confidence progress bar
  - [x] Assignee avatar
  - [x] Open in Jira action button
- [x] **Create Bug Dialog**:
  - [x] Pre-filled from AI analysis
  - [x] Title, Priority, Assignee fields
  - [x] Auto-generated description with AI analysis
  - [x] Submit to Jira button
- [x] **View Bug Dialog** with full details

### Needs to Add (API Integration):
- [ ] Connect to `jiraAPI.createBug()` for bug creation
- [ ] Connect to `jiraAPI.getBugs()` for bugs list
- [ ] Connect to `jiraAPI.updateBug()` for status updates
- [ ] Link to failure details page
- [ ] Fetch AI analysis data for pre-fill
- [ ] Real Jira API integration

---

## 11. PR Workflow Preview (`/pr-workflow-preview`) ✅ COMPLETE

### Track AI-generated code fix PRs from approval to merge

### Currently Has (Mock Data):
- [x] Purple gradient header with merged/in-progress counts
- [x] Stats cards (Total PRs, Merged, In Progress, Failed CI)
- [x] **PR Workflow Stages Overview** - Visual stepper:
  - Fix Approved → Branch Created → Changes Committed → PR Created → CI Running → Code Review → Merged
- [x] **PR Cards** with:
  - [x] PR number and title
  - [x] Status chip (Merged, In Review, CI Running, CI Failed)
  - [x] AI Auto-Fix indicator
  - [x] Branch name
  - [x] CI status icon
  - [x] Progress stepper showing current stage
  - [x] Expandable details:
    - Linked failure
    - Classification
    - AI confidence
    - Code changes (files, additions, deletions)
    - Timeline (created, merged, reviewers)
  - [x] Open in GitHub action
- [x] CI failure error alerts

### Needs to Add (API Integration):
- [ ] Connect to `fixAPI.getHistory()` for PR list
- [ ] Connect to `fixAPI.getStatus()` for PR status
- [ ] GitHub API for PR details
- [ ] CI/CD webhook for status updates
- [ ] Real-time status updates via WebSocket

---

## Priority Order for Integration

1. **High Priority** - Core functionality
   - Dashboard: System status, stats, recent failures
   - Failures: List with pagination and filters
   - Manual Trigger: Trigger form working

2. **Medium Priority** - Analytics & Bulk
   - Analytics: Acceptance rate, refinement stats
   - Trigger Analysis: Bulk trigger functionality

3. **Lower Priority** - Knowledge base
   - Knowledge: CRUD operations

---

## Notes

- All preview pages currently use **mock data** for demonstration
- Original pages have full API integration with react-query
- Preview pages have the **modern UI design** ready
- Integration requires copying API hooks from original pages
- Consider creating a shared hook file for reusable queries
