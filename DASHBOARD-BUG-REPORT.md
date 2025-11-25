# Dashboard Bug Report - E2E Testing Blockers

**Date:** November 23, 2025  
**Reporter:** QA Agent  
**Priority:** HIGH - Blocking E2E Testing

---

## Executive Summary

Dashboard is displaying Jenkins build failures correctly, but **critical test suite data is missing** from the MongoDB records. The build data flow is incomplete, preventing proper validation of test suite completeness.

**Status:** 
- ✅ Data Flow: Jenkins → MongoDB → Dashboard API → UI (**Working**)
- ❌ Test Suite Metadata: Pass/Fail/Total counts (**Missing**)
- ❌ AI Analysis: All failures show "Analyzed - 0%" (**Not functioning properly**)

---

## Bug #1: Missing Test Suite Pass/Fail Counts (CRITICAL)

### Issue
Jenkins test failures in MongoDB are **missing complete test suite information**:
- ❌ `suite_name` - Not captured
- ❌ `pass_count` - Not captured  
- ❌ `fail_count` - Not captured
- ❌ `total_count` - Not captured

### Impact
- Cannot verify if build represents complete test suite
- Cannot calculate pass/fail ratio for builds
- Cannot determine test suite coverage
- Cannot validate if all tests from suite were reported

### Evidence
```javascript
// Current data in MongoDB:
{
  "build_id": "BUILD_1762999514935",
  "test_name": "should measure Lustre parallel I/O scalability",
  "job_name": "Performance-Scalability",
  "error_message": "...",
  "stack_trace": "...",
  // MISSING:
  "suite_name": undefined,
  "pass_count": undefined,
  "fail_count": undefined,
  "total_count": undefined
}
```

### Expected Data
```javascript
{
  "build_id": "BUILD_1762999514935",
  "test_name": "should measure Lustre parallel I/O scalability",
  "job_name": "Performance-Scalability",
  "suite_name": "Performance Test Suite",
  "pass_count": 25,
  "fail_count": 1,
  "total_count": 26,
  "build_url": "http://localhost:8080/job/Performance-Scalability/123/",
  "jenkins_job_url": "http://localhost:8080/job/Performance-Scalability/"
}
```

### Root Cause
Jenkins webhook payload is not including test suite summary data when reporting failures to `jenkins_integration_service.py`

### Fix Location
**File:** `implementation/jenkins_integration_service.py`

**Required Changes:**
1. Update Jenkins webhook configuration to send suite summary
2. Update `POST /webhook/test-failure` endpoint to parse and store:
   - `suite_name`
   - `pass_count`
   - `fail_count`  
   - `total_count`
3. Update MongoDB schema to include these fields

**Jenkins Pipeline Changes:**
```groovy
// In Jenkinsfile, send complete suite data:
def testResults = junit testResults: '**/test-results/*.xml'
def payload = [
    test_name: testName,
    job_name: env.JOB_NAME,
    build_id: env.BUILD_ID,
    suite_name: testResults.suiteName,
    pass_count: testResults.passCount,
    fail_count: testResults.failCount,
    total_count: testResults.totalCount,
    // ... other fields
]
```

---

## Bug #2: AI Analysis Showing "Analyzed - 0%" (HIGH)

### Issue
All test failures show:
- AI Status: `"Analyzed - 0%"`
- AI Recommendation: `"Category: N/A No recommendation"`

This indicates AI analysis either:
1. Ran but failed to generate valid results
2. Never ran at all
3. Stored results with 0% confidence score

### Impact
- AI recommendations not available for any failures
- Cannot validate AI analysis workflow
- Aging service may not be triggering analysis
- Manual trigger may not be working

### Evidence
From Dashboard table (10 failures sampled):
- All 10 show `"Analyzed - 0%"`
- All 10 show `"Category: N/A"`
- All 10 failures are **11 days old** (should have been auto-analyzed)

### Expected Behavior
Failures > 3 days old should be automatically analyzed by `aging_service.py` and show:
- AI Status: `"Analyzed - 87%"` (with actual confidence score)
- AI Recommendation: Actual category and recommendation text

### Root Cause (Hypothesis)
1. **Aging Service not running** - Check port 5010
2. **Analysis stored with NULL confidence** - Check PostgreSQL `failure_analysis` table
3. **AI Service failing** - Check port 5000 health
4. **n8n workflow not triggering** - Check n8n webhooks

### Fix Investigation Required
**Check these services:**
```powershell
# 1. Check aging service
curl http://localhost:5010/health

# 2. Check AI analysis service  
curl http://localhost:5000/api/health

# 3. Check PostgreSQL data
# Query: SELECT * FROM failure_analysis WHERE confidence_score IS NULL OR confidence_score = 0;

# 4. Check n8n workflows
# Visit: http://localhost:5678
```

---

## Bug #3: Build ID Inconsistency (MEDIUM)

### Issue
Build IDs are inconsistent across failures:
- Some use timestamp format: `BUILD_1762999514935`
- Some use simple numbers: `19`
- Dashboard shows yet different IDs: `69153cda`

### Impact
- Difficult to correlate failures from same build
- Cannot group failures by build reliably
- May cause issues in build-level analysis

### Evidence
```
API Build IDs:     BUILD_1762999514935, BUILD_1762999514516, 19
Dashboard Build IDs: 69153cda, 69153cd9, 69153cd8
```

### Root Cause
Inconsistent build ID generation across different Jenkins jobs or multiple data insertion paths.

### Fix Location
**File:** `implementation/jenkins_integration_service.py`

Standardize build ID format:
```python
# Use consistent format: JOB_NAME-BUILD_NUMBER
build_id = f"{job_name}-{build_number}"
# Example: "Performance-Scalability-123"
```

---

## Bug #4: Trigger Analysis Page Found But Not Functional (HIGH)

### Issue
**Update:** Trigger Analysis functionality exists on separate page (`/trigger-analysis`) but has usability issues.

Found:
- ✅ Navigation menu has "Trigger Analysis" link
- ✅ Page exists at `http://localhost:5173/trigger-analysis`
- ✅ Page has "Analyze Selected (0)" button
- ⚠️ Button is **disabled** until failures are selected
- ⚠️ No failures displayed to select from

### Impact
- Cannot trigger analysis without selecting failures
- No UI to select which failures to analyze
- Page appears incomplete/broken

### Evidence
From Trigger Analysis page:
- Found 6 buttons
- "Analyze Selected (0)" button exists but is **disabled**
- "Select All" and "Deselect All" buttons present
- No failure list/checkboxes visible for selection
- Page heading shows "100" (likely total count)

### Expected Behavior
Page should display:
1. List of unanalyzed failures with checkboxes
2. Ability to select failures
3. "Analyze Selected (N)" button becomes enabled when N > 0
4. Clicking triggers API call to analyze selected failures

### Fix Location
**File:** `implementation/dashboard-ui/src/pages/TriggerAnalysis.jsx`

**Required Changes:**
1. Fetch unanalyzed failures from API
2. Display failures in selectable list/table
3. Enable "Analyze Selected" button when failures selected
4. Wire up button to call `/api/trigger/manual` endpoint

**Alternative:** "Manual Trigger" page at `/manual-trigger` may be the working version - needs investigation.

---

## Data Validation Results

### ✅ What's Working
1. **Jenkins Integration** - Failures being captured
2. **MongoDB Storage** - Data persisting correctly
3. **Dashboard API** - Serving data on port 5006
4. **Dashboard UI** - Loading and displaying on port 5173
5. **Table Display** - Showing all required columns
6. **Aging Calculation** - Correctly showing "11 days"

### ❌ What's Missing
1. **Test Suite Counts** - 5/5 samples missing pass/fail counts
2. **AI Analysis Results** - 10/10 failures show 0% confidence
3. **Manual Trigger Button** - No UI element to trigger analysis
4. **Build Grouping** - Inconsistent build ID formats

---

## Testing Recommendations

### Immediate (Before E2E Testing)
1. **Fix Bug #1:** Add suite counts to Jenkins payload → **BLOCKER**
2. **Fix Bug #4:** Add Trigger Analysis button → **BLOCKER**
3. **Investigate Bug #2:** Why AI analysis shows 0% → **BLOCKER**

### Next Phase
4. Fix Bug #3: Standardize build IDs
5. Verify aging service is running and triggering
6. Test manual trigger workflow end-to-end
7. Verify AI recommendations are meaningful

---

## Files Requiring Changes

1. `implementation/jenkins_integration_service.py` - Add suite data parsing
2. `implementation/dashboard-ui/src/pages/Dashboard.jsx` - Add trigger button
3. Jenkins Pipeline files (Jenkinsfile) - Include suite summary in webhook
4. `implementation/aging_service.py` - Verify auto-trigger logic
5. MongoDB schema documentation - Add suite fields

---

## Validation Script

Created comprehensive validation script:
```
tests/ui/complete-validation.js
tests/ui/complete-validation.png (screenshot)
```

**Run validation:**
```bash
cd tests/ui
node complete-validation.js
```

---

## Next Steps for QA

1. **Discuss with development team** - Prioritize Bug #1 and #4
2. **Check aging service status** - Is it running? Is it triggering?
3. **Verify AI service health** - Test analysis endpoint directly
4. **Once bugs fixed** - Re-run validation and begin E2E test suite

---

**End of Report**
