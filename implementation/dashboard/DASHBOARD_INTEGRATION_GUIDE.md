# Dashboard Integration Guide

## 📊 Complete Dashboard Integration for DDN AI System

This guide shows how to integrate your React/Angular/Vue dashboard with the n8n workflows.

---

## 🎯 Dashboard Features

### **1. Failure List View**
- Display all test failures with aging days
- Filter by date range, job name, test suite
- Sort by aging days, priority
- Color coding by status

### **2. Manual Analysis Trigger**
- "Analyze Now" button for each failure
- Works regardless of aging criteria
- Real-time progress indicator
- Automatic refresh on completion

### **3. Analysis Details View**
- Root cause analysis
- Fix recommendations with code examples
- Clickable links to GitHub (exact file:line)
- Clickable link to Jenkins build
- Confidence score visualization
- Similar past cases

### **4. Refinement with Feedback**
- "Not Satisfied?" button
- Feedback modal with text input
- Optional checkboxes for context
- Re-analyze with user input
- Show refinement history

---

## 🔌 API Endpoints

### **Base URLs**

```javascript
const API_CONFIG = {
  n8n_manual_trigger: 'https://n8n.your-domain.com/webhook/ddn-manual-trigger',
  n8n_refinement: 'https://n8n.your-domain.com/webhook/ddn-refinement',
  dashboard_backend: 'http://localhost:3001/api' // Your dashboard backend
};
```

---

## 📝 API Integration Examples

### **1. Fetch Failure List**

**Endpoint**: Your Dashboard Backend

```javascript
//================================================================
// FETCH FAILURES FROM MONGODB
//================================================================

async function fetchFailures(filters = {}) {
  const response = await fetch(`${API_CONFIG.dashboard_backend}/failures`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`
    },
    body: JSON.stringify({
      aging_days_min: filters.agingDaysMin || 0,
      aging_days_max: filters.agingDaysMax || 365,
      job_name: filters.jobName || null,
      test_suite: filters.testSuite || null,
      status: filters.status || null, // 'ANALYZED', 'NOT_ANALYZED', 'ALL'
      date_from: filters.dateFrom || null,
      date_to: filters.dateTo || null,
      limit: filters.limit || 50,
      offset: filters.offset || 0
    })
  });

  const data = await response.json();

  return data.failures; // Array of failure objects
}

// Example response:
[
  {
    build_id: "12345",
    job_name: "DDN-Smoke-Tests",
    test_suite: "Health_Check",
    status: "FAILURE",
    build_url: "https://jenkins.com/job/12345",
    timestamp: "2025-10-10T10:00:00Z",
    aging_days: 7,
    has_analysis: true,
    analysis_confidence: 0.92,
    error_category: "CODE_ERROR"
  },
  {
    build_id: "12346",
    job_name: "DDN-Integration",
    test_suite: "API_Tests",
    status: "FAILURE",
    build_url: "https://jenkins.com/job/12346",
    timestamp: "2025-10-15T14:30:00Z",
    aging_days: 2,
    has_analysis: false,
    error_category: null
  }
]
```

---

### **2. Trigger Manual Analysis**

**Endpoint**: n8n Manual Trigger Workflow

```javascript
//================================================================
// TRIGGER MANUAL ANALYSIS (Analyze Now Button)
//================================================================

async function triggerManualAnalysis(buildId, userEmail) {
  // Show loading spinner
  setLoading(true);
  setAnalysisStatus('Analyzing...');

  try {
    const response = await fetch(API_CONFIG.n8n_manual_trigger, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        build_id: buildId,
        triggered_by: 'dashboard',
        user_email: userEmail
      })
    });

    const result = await response.json();

    if (result.status === 'success') {
      // Display analysis results
      showAnalysisModal(result.data);

      // Update failure list
      await refreshFailureList();

      return result.data;
    } else {
      throw new Error(result.message || 'Analysis failed');
    }
  } catch (error) {
    console.error('Analysis error:', error);
    showError(`Analysis failed: ${error.message}`);
  } finally {
    setLoading(false);
  }
}

// Example success response:
{
  status: "success",
  message: "Analysis completed successfully",
  data: {
    build_id: "12346",
    analysis_type: "CLAUDE_MCP_ANALYSIS",
    error_category: "CODE_ERROR",
    confidence: 0.92,
    root_cause: "NullPointerException at DDNStorage.java:127. Missing null check for storageConfig object.",
    fix_recommendation: "Add null validation before accessing storageConfig...",
    code_fix: "```java\n+ if (storageConfig == null) {\n+   throw new IllegalStateException(...);\n+ }\n```",
    test_case: "testSaveDataWithoutInit() should verify exception is thrown",
    prevention_strategy: "Add defensive null checks for all config objects",
    estimated_fix_time: "30 minutes",
    links: {
      jenkins: "https://jenkins.com/job/12346",
      github_repo: "https://github.com/org/ddn-repo",
      github_files: [
        {
          file_path: "src/main/java/DDNStorage.java",
          line_number: 127,
          github_url: "https://github.com/org/ddn-repo/blob/main/src/main/java/DDNStorage.java#L127"
        }
      ]
    },
    similar_cases_found: 3,
    similar_solutions: [...],
    processing_time_ms: 15000,
    cost_usd: 0.08,
    timestamp: "2025-10-17T10:30:00Z",
    can_refine: true,
    refinement_count: 0
  }
}
```

---

### **3. Submit Refinement Feedback**

**Endpoint**: n8n Refinement Workflow

```javascript
//================================================================
// SUBMIT USER FEEDBACK FOR REFINEMENT
//================================================================

async function submitRefinementFeedback(buildId, feedback, additionalContext) {
  setLoading(true);
  setStatus('Re-analyzing with your feedback...');

  try {
    const response = await fetch(API_CONFIG.n8n_refinement, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        build_id: buildId,
        user_feedback: feedback.text,
        user_email: feedback.userEmail,
        additional_context: {
          check_recent_commits: additionalContext.checkCommits || false,
          check_related_tests: additionalContext.checkTests || false,
          include_config_files: additionalContext.includeConfig || false,
          focus_areas: additionalContext.focusAreas || []
        }
      })
    });

    const result = await response.json();

    if (result.status === 'success') {
      // Show updated analysis
      showRefinedAnalysis(result.data);

      return result.data;
    } else {
      throw new Error(result.message || 'Refinement failed');
    }
  } catch (error) {
    console.error('Refinement error:', error);
    showError(`Refinement failed: ${error.message}`);
  } finally {
    setLoading(false);
  }
}

// Example success response:
{
  status: "success",
  message: "Analysis refined successfully based on user feedback",
  data: {
    build_id: "12346",
    refinement_version: 2,
    refinement_summary: "Re-classified from CODE_ERROR to CONFIG_ERROR based on user feedback",
    user_feedback_addressed: "Investigated configuration files as suggested",
    category_changed: true,
    error_category: "CONFIG_ERROR",
    original_category: "CODE_ERROR",
    confidence_score: 0.95,
    confidence_improvement: "+3%",
    root_cause: "Configuration path for storage not set in app.properties",
    fix_recommendation: "Set storage.path property in config file...",
    code_fix: "# app.properties\n+ storage.path=/var/lib/ddn/storage",
    evidence: [
      "Config file missing storage.path property",
      "Code expects storageConfig.getPath() to be non-null",
      "Recent deployment didn't include updated config"
    ],
    why_original_was_wrong: "Initial analysis focused on code null check, but root cause is missing configuration",
    links: {
      jenkins: "https://jenkins.com/job/12346",
      github_repo: "https://github.com/org/ddn-repo",
      github_files: [
        {
          file_path: "src/main/resources/app.properties",
          line_number: 45,
          reason: "Missing storage.path configuration",
          github_url: "https://github.com/org/ddn-repo/blob/main/src/main/resources/app.properties#L45"
        },
        {
          file_path: "src/main/java/DDNStorage.java",
          line_number: 127,
          reason: "Code that fails when config missing",
          github_url: "https://github.com/org/ddn-repo/blob/main/src/main/java/DDNStorage.java#L127"
        }
      ]
    },
    processing_time_ms: 18000,
    cost_usd: 0.12,
    timestamp: "2025-10-17T10:45:00Z",
    can_refine: true
  }
}
```

---

## 🎨 React Component Examples

### **1. Failure List Component**

```jsx
import React, { useState, useEffect } from 'react';
import { fetchFailures, triggerManualAnalysis } from '../api/ddnApi';

function FailureList() {
  const [failures, setFailures] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    agingDaysMin: 0,
    status: 'ALL'
  });

  useEffect(() => {
    loadFailures();
  }, [filters]);

  async function loadFailures() {
    setLoading(true);
    try {
      const data = await fetchFailures(filters);
      setFailures(data);
    } catch (error) {
      console.error('Failed to load failures:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalyzeNow(buildId) {
    try {
      const result = await triggerManualAnalysis(buildId, getCurrentUserEmail());
      // Open analysis modal
      openAnalysisModal(result);
      // Refresh list
      await loadFailures();
    } catch (error) {
      alert(`Analysis failed: ${error.message}`);
    }
  }

  function getAgingColor(days) {
    if (days >= 7) return 'bg-red-100 text-red-800';
    if (days >= 3) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Test Failures</h1>

      {/* Filters */}
      <div className="mb-4 flex gap-4">
        <select
          value={filters.status}
          onChange={(e) => setFilters({...filters, status: e.target.value})}
          className="border rounded px-3 py-2"
        >
          <option value="ALL">All Failures</option>
          <option value="ANALYZED">Analyzed</option>
          <option value="NOT_ANALYZED">Not Analyzed</option>
        </select>

        <input
          type="number"
          placeholder="Min aging days"
          value={filters.agingDaysMin}
          onChange={(e) => setFilters({...filters, agingDaysMin: parseInt(e.target.value)})}
          className="border rounded px-3 py-2 w-40"
        />
      </div>

      {/* Failure Table */}
      {loading ? (
        <div className="text-center py-8">Loading...</div>
      ) : (
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100">
              <th className="border p-2">Build ID</th>
              <th className="border p-2">Job Name</th>
              <th className="border p-2">Test Suite</th>
              <th className="border p-2">Aging Days</th>
              <th className="border p-2">Status</th>
              <th className="border p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {failures.map((failure) => (
              <tr key={failure.build_id} className="hover:bg-gray-50">
                <td className="border p-2">{failure.build_id}</td>
                <td className="border p-2">{failure.job_name}</td>
                <td className="border p-2">{failure.test_suite}</td>
                <td className="border p-2">
                  <span className={`px-2 py-1 rounded ${getAgingColor(failure.aging_days)}`}>
                    {failure.aging_days} days
                  </span>
                </td>
                <td className="border p-2">
                  {failure.has_analysis ? (
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded">
                      Analyzed ({(failure.analysis_confidence * 100).toFixed(0)}%)
                    </span>
                  ) : (
                    <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded">
                      Not Analyzed
                    </span>
                  )}
                </td>
                <td className="border p-2">
                  {failure.has_analysis ? (
                    <button
                      onClick={() => openAnalysisModal(failure.build_id)}
                      className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 mr-2"
                    >
                      View
                    </button>
                  ) : (
                    <button
                      onClick={() => handleAnalyzeNow(failure.build_id)}
                      className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 mr-2"
                    >
                      Analyze Now
                    </button>
                  )}
                  <a
                    href={failure.build_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600"
                  >
                    Jenkins
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default FailureList;
```

---

### **2. Analysis Details Modal**

```jsx
import React, { useState } from 'react';
import { submitRefinementFeedback } from '../api/ddnApi';

function AnalysisModal({ analysis, onClose, onRefine }) {
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [additionalContext, setAdditionalContext] = useState({
    checkCommits: false,
    checkTests: false,
    includeConfig: false
  });

  async function handleSubmitFeedback() {
    if (feedback.trim().length < 10) {
      alert('Please provide detailed feedback (at least 10 characters)');
      return;
    }

    try {
      const result = await submitRefinementFeedback(
        analysis.build_id,
        {
          text: feedback,
          userEmail: getCurrentUserEmail()
        },
        additionalContext
      );

      // Update modal with refined analysis
      onRefine(result);
      setShowFeedback(false);
      setFeedback('');
    } catch (error) {
      alert(`Refinement failed: ${error.message}`);
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-blue-500 text-white p-4 rounded-t-lg flex justify-between items-center">
          <h2 className="text-xl font-bold">
            Analysis Details - Build {analysis.build_id}
          </h2>
          <button onClick={onClose} className="text-white hover:text-gray-200">
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Quick Links */}
          <div className="mb-6 flex gap-3">
            <a
              href={analysis.links.jenkins}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              🔧 View in Jenkins
            </a>
            <a
              href={analysis.links.github_repo}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-800"
            >
              📂 GitHub Repository
            </a>
          </div>

          {/* Metadata */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div>
              <div className="text-sm text-gray-600">Category</div>
              <div className="font-semibold">{analysis.error_category}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Confidence</div>
              <div className="font-semibold">{(analysis.confidence * 100).toFixed(1)}%</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Analysis Type</div>
              <div className="font-semibold">{analysis.analysis_type}</div>
            </div>
          </div>

          {/* Root Cause */}
          <div className="mb-6">
            <h3 className="text-lg font-bold mb-2">📝 Root Cause</h3>
            <div className="bg-gray-100 p-4 rounded">
              {analysis.root_cause}
            </div>
          </div>

          {/* Fix Recommendation */}
          <div className="mb-6">
            <h3 className="text-lg font-bold mb-2">💡 Recommended Fix</h3>
            <div className="bg-gray-100 p-4 rounded whitespace-pre-wrap">
              {analysis.fix_recommendation}
            </div>
          </div>

          {/* Code Fix */}
          {analysis.code_fix && (
            <div className="mb-6">
              <h3 className="text-lg font-bold mb-2">🔧 Code Fix</h3>
              <pre className="bg-gray-900 text-gray-100 p-4 rounded overflow-x-auto">
                <code>{analysis.code_fix}</code>
              </pre>
            </div>
          )}

          {/* GitHub Files */}
          {analysis.links.github_files && analysis.links.github_files.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-bold mb-2">📁 Related Files</h3>
              <div className="space-y-2">
                {analysis.links.github_files.map((file, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">{file.file_path}</span>
                    {file.line_number && (
                      <span className="text-sm text-gray-500">Line {file.line_number}</span>
                    )}
                    <a
                      href={file.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-auto px-3 py-1 bg-gray-700 text-white text-sm rounded hover:bg-gray-800"
                    >
                      View in GitHub →
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Refinement Section */}
          {!showFeedback ? (
            <div className="border-t pt-4">
              <button
                onClick={() => setShowFeedback(true)}
                className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
              >
                ❌ Not Satisfied? Provide Feedback
              </button>
            </div>
          ) : (
            <div className="border-t pt-4">
              <h3 className="text-lg font-bold mb-2">💬 Provide Your Feedback</h3>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Explain why the analysis is incorrect or what should be investigated..."
                className="w-full border rounded p-3 h-32 mb-3"
              />

              <div className="mb-3 space-y-2">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={additionalContext.checkCommits}
                    onChange={(e) => setAdditionalContext({...additionalContext, checkCommits: e.target.checked})}
                  />
                  <span>Check recent commits (last 7 days)</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={additionalContext.checkTests}
                    onChange={(e) => setAdditionalContext({...additionalContext, checkTests: e.target.checked})}
                  />
                  <span>Check related test files</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={additionalContext.includeConfig}
                    onChange={(e) => setAdditionalContext({...additionalContext, includeConfig: e.target.checked})}
                  />
                  <span>Include configuration files in analysis</span>
                </label>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => setShowFeedback(false)}
                  className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitFeedback}
                  className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                >
                  Re-analyze with Feedback
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AnalysisModal;
```

---

## 🎯 Complete Integration Summary

### **User Journey:**

1. **User opens dashboard** → Sees failure list
2. **Filters by aging days** → e.g., show failures >= 3 days
3. **Sees "Not Analyzed" failure** → Clicks "Analyze Now"
4. **n8n workflow runs** → Returns analysis in 5-15 seconds
5. **Modal opens** → Shows root cause, fix, GitHub links
6. **Clicks GitHub link** → Opens exact file at exact line
7. **Not satisfied?** → Provides feedback text
8. **Refinement runs** → Claude re-analyzes with context
9. **Updated analysis** → Shows in same modal

---

## 📦 Next Steps

1. **Import all 3 workflows into n8n**
2. **Configure credentials** (MongoDB, Anthropic, Teams)
3. **Start Python services** (LangGraph, MCP servers, Pinecone)
4. **Build dashboard** using React components above
5. **Test complete flow** with sample failure

---

**Last Updated**: October 17, 2025
