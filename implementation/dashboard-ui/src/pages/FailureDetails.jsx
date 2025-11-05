import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from 'react-query'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Divider,
  Tabs,
  Tab,
  Snackbar
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  Code as CodeIcon,
  BugReport as BugReportIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Edit as EditIcon,
  GitHub as GitHubIcon,
  Build as BuildIcon,
  PlayArrow as PlayArrowIcon,
  Construction as ConstructionIcon,
  LibraryBooks as LibraryBooksIcon
} from '@mui/icons-material'
import { failuresAPI, feedbackAPI, triggerAPI, fixAPI } from '../services/api'
import { format } from 'date-fns'
import FeedbackModal from '../components/FeedbackModal'
import BeforeAfterComparison from '../components/BeforeAfterComparison'
import { CodeSnippetList } from '../components/CodeSnippet' // Task 0E.8: GitHub code display
import SimilarErrorsDisplay from '../components/SimilarErrorsDisplay' // Task 0B.8: Similar documented errors
import CodeFixApproval from '../components/CodeFixApproval' // Phase B: Automated code fixing

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

function FailureDetails() {
  const { buildId } = useParams()
  const navigate = useNavigate()
  const [tabValue, setTabValue] = useState(0)
  const [feedbackStatus, setFeedbackStatus] = useState(null) // 'accepted', 'rejected', 'refining'
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' })
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false)
  const [feedbackModalType, setFeedbackModalType] = useState(null) // 'reject' | 'refine'
  const [isRefining, setIsRefining] = useState(false)
  // Phase B: Code fix approval state
  const [prStatus, setPrStatus] = useState(null)
  const [fixApplicationId, setFixApplicationId] = useState(null)

  const { data, isLoading, error, refetch } = useQuery(
    ['failure-details', buildId],
    () => failuresAPI.getDetails(buildId),
    {
      retry: 1,
      refetchInterval: isRefining ? 5000 : false // Poll every 5 seconds when refining
    }
  )

  // Query for fetching refinement history
  const { data: refinementData } = useQuery(
    ['refinement-history', buildId],
    () => feedbackAPI.getRefinementHistory(buildId),
    {
      retry: 1,
      enabled: !!buildId // Only run if buildId exists
    }
  )

  // Mutation for submitting feedback
  const feedbackMutation = useMutation(
    (feedbackData) => feedbackAPI.submit(feedbackData),
    {
      onSuccess: () => {
        setSnackbar({ open: true, message: 'Feedback submitted successfully!', severity: 'success' })
        refetch()
      },
      onError: (err) => {
        setSnackbar({ open: true, message: `Failed to submit feedback: ${err.message}`, severity: 'error' })
      }
    }
  )

  // Mutation for triggering AI analysis
  const analysisMutation = useMutation(
    (analysisData) => triggerAPI.triggerAnalysis(analysisData),
    {
      onSuccess: () => {
        setSnackbar({ open: true, message: 'AI analysis started! Refreshing...', severity: 'success' })
        setIsAnalyzing(true)
        // Refetch after a delay to allow analysis to complete
        setTimeout(() => {
          refetch()
          setIsAnalyzing(false)
        }, 3000)
      },
      onError: (err) => {
        setSnackbar({ open: true, message: `Failed to start analysis: ${err.message}`, severity: 'error' })
        setIsAnalyzing(false)
      }
    }
  )

  // Handler for Accept button
  const handleAccept = () => {
    feedbackMutation.mutate({
      build_id: buildId,
      feedback_type: 'accept',
      validation_status: 'accepted',
      comment: 'AI analysis accepted by validator'
    })
    setFeedbackStatus('accepted')
  }

  // Handler for Reject button - opens modal
  const handleReject = () => {
    setFeedbackModalType('reject')
    setFeedbackModalOpen(true)
  }

  // Handler for Refine button - opens modal
  const handleRefine = () => {
    setFeedbackModalType('refine')
    setFeedbackModalOpen(true)
  }

  // Handler for modal close
  const handleModalClose = () => {
    setFeedbackModalOpen(false)
    setFeedbackModalType(null)
  }

  // Handler for feedback submission from modal
  const handleFeedbackSubmit = (feedbackData) => {
    feedbackMutation.mutate(feedbackData, {
      onSuccess: () => {
        if (feedbackData.feedback_type === 'reject') {
          setFeedbackStatus('rejected')
        } else if (feedbackData.feedback_type === 'refine') {
          setFeedbackStatus('refining')
          setIsRefining(true)
          setSnackbar({ open: true, message: 'Refinement requested! Processing...', severity: 'info' })
        }
        handleModalClose()
      }
    })
  }

  // Effect to detect refinement completion
  useEffect(() => {
    if (isRefining && refinementData?.data?.refinements) {
      const latestRefinement = refinementData.data.refinements[refinementData.data.refinements.length - 1]

      // Check if refinement is complete (has refined_analysis)
      if (latestRefinement && latestRefinement.refined_analysis) {
        setIsRefining(false)
        setFeedbackStatus('refined')
        setSnackbar({
          open: true,
          message: 'Refinement complete! Analysis has been updated.',
          severity: 'success'
        })
      }
    }
  }, [refinementData, isRefining])

  // Handler for Analyze with AI button
  const handleAnalyze = () => {
    analysisMutation.mutate({
      build_id: buildId,
      trigger_source: 'manual_ui'
    })
  }

  // Handler for GitHub redirect (with authentication from env)
  const handleGitHubRedirect = () => {
    // Extract file path from AI analysis or stack trace
    const failure = data?.data?.failure || {}
    const filePath = failure.ai_analysis?.file_path || extractFilePathFromStackTrace(failure.stack_trace)

    if (filePath) {
      // GitHub URL with authentication handled by browser (token in env)
      const githubUrl = `https://github.com/${import.meta.env.VITE_GITHUB_REPO}/blob/main/${filePath}`
      window.open(githubUrl, '_blank', 'noopener,noreferrer')
    } else {
      setSnackbar({ open: true, message: 'No file path found in analysis', severity: 'warning' })
    }
  }

  // Handler for Jenkins redirect (with authentication from env)
  const handleJenkinsRedirect = () => {
    const failure = data?.data?.failure || {}
    if (failure.build_url) {
      // Jenkins authentication handled by browser (credentials in env)
      window.open(failure.build_url, '_blank', 'noopener,noreferrer')
    } else {
      setSnackbar({ open: true, message: 'No Jenkins URL available', severity: 'warning' })
    }
  }

  // Helper function to extract file path from stack trace
  const extractFilePathFromStackTrace = (stackTrace) => {
    if (!stackTrace) return null
    const match = stackTrace.match(/File "([^"]+)"/)
    return match ? match[1] : null
  }

  // Task 0E.8: Helper function to extract error line number from stack trace
  const extractErrorLineNumber = (stackTrace) => {
    if (!stackTrace) return null
    // Match patterns like ":142" or "line 142" or ".java:142"
    const match = stackTrace.match(/:(\d+)[:\)]|line\s+(\d+)/)
    return match ? parseInt(match[1] || match[2]) : null
  }

  // Handler for closing snackbar
  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false })
  }

  // Phase B: Code fix approval handlers
  const handleFixApprove = async (analysisId) => {
    try {
      const result = await fixAPI.approve({
        analysis_id: analysisId,
        approved_by_name: 'UI User', // TODO: Get from auth context
        approved_by_email: 'user@example.com' // TODO: Get from auth context
      })

      if (result.success) {
        setPrStatus({
          pr_number: result.pr_number,
          pr_url: result.pr_url,
          status: 'pr_created',
          created_at: new Date().toISOString()
        })
        setFixApplicationId(result.fix_application_id)
        setSnackbar({
          open: true,
          message: `Pull Request #${result.pr_number} created successfully!`,
          severity: 'success'
        })
        refetch() // Refresh failure details
      } else {
        throw new Error(result.error || 'Failed to create PR')
      }
    } catch (err) {
      console.error('Fix approval error:', err)
      setSnackbar({
        open: true,
        message: `Failed to approve fix: ${err.message}`,
        severity: 'error'
      })
    }
  }

  const handleFixReject = async (analysisId) => {
    try {
      const result = await fixAPI.reject({
        analysis_id: analysisId,
        rejected_by_name: 'UI User', // TODO: Get from auth context
        rejected_by_email: 'user@example.com', // TODO: Get from auth context
        rejection_reason: 'Fix not suitable'
      })

      if (result.success) {
        setSnackbar({
          open: true,
          message: 'Fix rejected successfully',
          severity: 'info'
        })
        refetch()
      }
    } catch (err) {
      console.error('Fix rejection error:', err)
      setSnackbar({
        open: true,
        message: `Failed to reject fix: ${err.message}`,
        severity: 'error'
      })
    }
  }

  const handleFixFeedback = async (analysisId) => {
    // Open feedback modal for fix refinement
    setFeedbackModalType('refine')
    setFeedbackModalOpen(true)
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load failure details: {error.message}
      </Alert>
    )
  }

  const failure = data?.data?.failure || {}
  const hasAiAnalysis = failure?.ai_analysis !== null && failure?.ai_analysis !== undefined
  // Task 0E.8: Check if GitHub code is available
  const hasGitHubCode = hasAiAnalysis && failure?.ai_analysis?.github_code_included === true
  // Task 0B.8: Check if similar documented errors are available
  const hasSimilarCases = hasAiAnalysis && failure?.ai_analysis?.similar_cases && failure.ai_analysis.similar_cases.length > 0

  // Extract refinement history data
  const refinementHistory = refinementData?.data?.refinements || []
  const hasRefinements = refinementHistory.length > 0
  const refinementCount = refinementHistory.length

  // Get original and refined analysis for comparison
  const originalAnalysis = hasRefinements && refinementHistory[0]?.original_analysis
    ? refinementHistory[0].original_analysis
    : failure?.ai_analysis
  const refinedAnalysis = hasRefinements && refinementHistory[refinementHistory.length - 1]?.refined_analysis
    ? refinementHistory[refinementHistory.length - 1].refined_analysis
    : null

  // Calculate aging days
  const calculateAgingDays = (timestamp) => {
    if (!timestamp) return 0
    const failureDate = new Date(timestamp)
    const now = new Date()
    const diffTime = Math.abs(now - failureDate)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/failures')}>
          Back to Failures
        </Button>
        <Typography variant="h4">
          Failure Details: {buildId}
        </Typography>
        {hasRefinements && (
          <Chip
            label={`${refinementCount} Refinement${refinementCount > 1 ? 's' : ''}`}
            color="info"
            icon={<EditIcon />}
            size="medium"
            sx={{ fontWeight: 600 }}
          />
        )}
      </Box>

      <Grid container spacing={3}>
        {/* Main Info Card */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="textSecondary">Job Name</Typography>
                <Typography variant="body1" gutterBottom>{failure.job_name || 'N/A'}</Typography>

                <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 2 }}>Test Name</Typography>
                <Typography variant="body1" gutterBottom>{failure.test_name || 'N/A'}</Typography>

                <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 2 }}>Build Number</Typography>
                <Typography variant="body1" fontFamily="monospace" gutterBottom>
                  {failure.build_number || failure._id?.substring(0, 8) || 'N/A'}
                </Typography>

                {hasAiAnalysis && (
                  <>
                    <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 2 }}>AI Classification</Typography>
                    <Chip
                      label={failure.ai_analysis.classification}
                      color="error"
                      sx={{ mt: 1 }}
                    />
                  </>
                )}
              </Grid>

              <Grid item xs={12} md={6}>
                {hasAiAnalysis && (
                  <>
                    <Typography variant="subtitle2" color="textSecondary">AI Confidence Score</Typography>
                    <Typography variant="h5" gutterBottom>
                      {Math.round((failure.ai_analysis.confidence_score || 0) * 100)}%
                    </Typography>
                  </>
                )}

                <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 2 }}>Aging Days</Typography>
                <Typography variant="h5" gutterBottom>
                  {calculateAgingDays(failure.timestamp)} days
                </Typography>

                <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 2 }}>Failure Date</Typography>
                <Typography variant="body1">
                  {failure.timestamp ? format(new Date(failure.timestamp), 'MMM dd, yyyy HH:mm:ss') : 'N/A'}
                </Typography>

                {hasAiAnalysis && failure.ai_analysis.analyzed_at && (
                  <>
                    <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 2 }}>Analysis Date</Typography>
                    <Typography variant="body1">
                      {format(new Date(failure.ai_analysis.analyzed_at), 'MMM dd, yyyy HH:mm:ss')}
                    </Typography>
                  </>
                )}
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            {/* Error Message */}
            <Typography variant="h6" gutterBottom>
              <BugReportIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Error Message
            </Typography>
            <Paper sx={{ p: 2, bgcolor: '#f5f5f5', mb: 3 }}>
              <Typography variant="body1" style={{ whiteSpace: 'pre-wrap' }}>
                {failure.error_message || 'No error message available'}
              </Typography>
            </Paper>

            {/* AI Analysis Section - only if analyzed */}
            {hasAiAnalysis && (
              <>
                {/* Root Cause */}
                <Typography variant="h6" gutterBottom>
                  <BugReportIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  AI Root Cause Analysis
                </Typography>
                <Paper sx={{ p: 2, bgcolor: '#e8f5e9', mb: 3 }}>
                  <Typography variant="body1" style={{ whiteSpace: 'pre-wrap' }}>
                    {failure.ai_analysis.root_cause || 'No root cause analysis available'}
                  </Typography>
                </Paper>

                {/* Fix Recommendation */}
                <Typography variant="h6" gutterBottom>
                  <CodeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  AI Fix Recommendation
                </Typography>
                <Paper sx={{ p: 2, bgcolor: '#e3f2fd', mb: 3 }}>
                  <Typography variant="body1" style={{ whiteSpace: 'pre-wrap' }}>
                    {failure.ai_analysis.recommendation || 'No recommendation available'}
                  </Typography>
                </Paper>

                {/* Severity */}
                {failure.ai_analysis.severity && (
                  <Box mb={3}>
                    <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                      Severity
                    </Typography>
                    <Chip
                      label={failure.ai_analysis.severity}
                      color={
                        failure.ai_analysis.severity === 'HIGH' ? 'error' :
                        failure.ai_analysis.severity === 'MEDIUM' ? 'warning' : 'info'
                      }
                    />
                  </Box>
                )}

                {/* Refinement Processing Message */}
                {isRefining && (
                  <Alert severity="info" sx={{ mb: 3 }} icon={<CircularProgress size={20} />}>
                    <Typography variant="subtitle2" fontWeight={600}>
                      Refinement in Progress
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                      The AI is re-analyzing this failure with your feedback. This page will auto-refresh when complete.
                    </Typography>
                  </Alert>
                )}

                {/* Validation Status Badge */}
                {feedbackStatus && (
                  <Box mb={3}>
                    <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                      Validation Status
                    </Typography>
                    <Chip
                      label={
                        feedbackStatus === 'accepted' ? 'Accepted' :
                        feedbackStatus === 'rejected' ? 'Rejected' :
                        feedbackStatus === 'refining' ? 'Refining...' :
                        'Refined'
                      }
                      color={
                        feedbackStatus === 'accepted' ? 'success' :
                        feedbackStatus === 'rejected' ? 'error' :
                        feedbackStatus === 'refined' ? 'info' : 'warning'
                      }
                      icon={
                        feedbackStatus === 'accepted' ? <CheckCircleIcon /> :
                        feedbackStatus === 'rejected' ? <CancelIcon /> : <EditIcon />
                      }
                    />
                  </Box>
                )}

                {/* Accept/Reject/Refine Buttons */}
                {!feedbackStatus && (
                  <Box display="flex" gap={2} mb={3}>
                    <Button
                      variant="contained"
                      color="success"
                      startIcon={<CheckCircleIcon />}
                      onClick={handleAccept}
                      disabled={feedbackMutation.isLoading}
                    >
                      Accept
                    </Button>
                    <Button
                      variant="contained"
                      color="error"
                      startIcon={<CancelIcon />}
                      onClick={handleReject}
                      disabled={feedbackMutation.isLoading}
                    >
                      Reject
                    </Button>
                    <Button
                      variant="contained"
                      color="warning"
                      startIcon={<EditIcon />}
                      onClick={handleRefine}
                      disabled={feedbackMutation.isLoading}
                    >
                      Refine
                    </Button>
                  </Box>
                )}

                {/* GitHub and Jenkins Links */}
                <Box display="flex" gap={2} mb={3}>
                  <Button
                    variant="outlined"
                    startIcon={<GitHubIcon />}
                    onClick={handleGitHubRedirect}
                  >
                    View Code on GitHub
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<BuildIcon />}
                    onClick={handleJenkinsRedirect}
                  >
                    View Build in Jenkins
                  </Button>
                </Box>
              </>
            )}

            {/* If not analyzed, show analyze button */}
            {!hasAiAnalysis && (
              <>
                <Alert severity="info" sx={{ mb: 3 }}>
                  This failure has not been analyzed by AI yet. The AI service can provide root cause analysis and fix recommendations.
                </Alert>
                <Box display="flex" gap={2} mb={3}>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={isAnalyzing ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
                    onClick={handleAnalyze}
                    disabled={isAnalyzing || analysisMutation.isLoading}
                  >
                    {isAnalyzing ? 'Analyzing...' : 'Analyze with AI'}
                  </Button>
                </Box>
              </>
            )}
          </Paper>
        </Grid>

        {/* Before/After Comparison - Only show if refinements exist */}
        {hasRefinements && (
          <Grid item xs={12}>
            <BeforeAfterComparison
              originalAnalysis={originalAnalysis}
              refinedAnalysis={refinedAnalysis}
              refinementHistory={refinementHistory}
            />
          </Grid>
        )}

        {/* Technical Details Tabs */}
        <Grid item xs={12}>
          <Paper>
            <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
              <Tab label="Stack Trace" />
              <Tab label="Full Failure Data" />
              {hasAiAnalysis && <Tab label="AI Analysis Details" />}
              {hasGitHubCode && <Tab label="GitHub Source Code" icon={<GitHubIcon />} iconPosition="start" />}
              {hasSimilarCases && <Tab label="Similar Documented Errors" icon={<LibraryBooksIcon />} iconPosition="start" />}
              {hasAiAnalysis && <Tab label="Code Fix" icon={<ConstructionIcon />} iconPosition="start" />}
            </Tabs>

            <TabPanel value={tabValue} index={0}>
              <Paper sx={{ p: 2, bgcolor: '#1e1e1e', color: '#fff', fontFamily: 'monospace', maxHeight: 500, overflow: 'auto' }}>
                <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                  {failure.stack_trace || 'No stack trace available'}
                </pre>
              </Paper>
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <Paper sx={{ p: 2, bgcolor: '#f5f5f5', maxHeight: 500, overflow: 'auto' }}>
                <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.875rem' }}>
                  {JSON.stringify(failure, null, 2)}
                </pre>
              </Paper>
            </TabPanel>

            {hasAiAnalysis && (
              <TabPanel value={tabValue} index={2}>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" color="textSecondary">Classification</Typography>
                    <Typography variant="body1" gutterBottom>{failure.ai_analysis.classification}</Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" color="textSecondary">AI Model Used</Typography>
                    <Typography variant="body1" gutterBottom>{failure.ai_analysis.ai_model || 'N/A'}</Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" color="textSecondary">Confidence Score</Typography>
                    <Typography variant="body1" gutterBottom>
                      {Math.round((failure.ai_analysis.confidence_score || 0) * 100)}%
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" color="textSecondary">Severity</Typography>
                    <Typography variant="body1" gutterBottom>{failure.ai_analysis.severity || 'N/A'}</Typography>
                  </Grid>
                  {/* Task 0B.8: Similar cases now displayed in dedicated tab - removed raw JSON display */}
                </Grid>
              </TabPanel>
            )}

            {/* Task 0E.8: GitHub Source Code Tab */}
            {hasGitHubCode && (
              <TabPanel value={tabValue} index={2 + (hasAiAnalysis ? 1 : 0)}>
                <CodeSnippetList
                  githubFiles={failure.ai_analysis.github_files || []}
                  errorLine={extractErrorLineNumber(failure.stack_trace)}
                  title="GitHub Source Code"
                  emptyMessage="No GitHub code available for this error"
                />
              </TabPanel>
            )}

            {/* Task 0B.8: Similar Documented Errors Tab */}
            {hasSimilarCases && (
              <TabPanel value={tabValue} index={2 + (hasAiAnalysis ? 1 : 0) + (hasGitHubCode ? 1 : 0)}>
                <SimilarErrorsDisplay
                  similarCases={failure.ai_analysis.similar_cases}
                  maxDisplay={5}
                  showCodeExamples={true}
                />
              </TabPanel>
            )}

            {/* Phase B: Code Fix Approval Tab */}
            {hasAiAnalysis && (
              <TabPanel value={tabValue} index={2 + (hasAiAnalysis ? 1 : 0) + (hasGitHubCode ? 1 : 0) + (hasSimilarCases ? 1 : 0)}>
                <CodeFixApproval
                  analysisId={failure.ai_analysis?.id || failure._id}
                  fixData={{
                    error_message: failure.error_message,
                    root_cause: failure.ai_analysis?.root_cause,
                    recommended_fix: failure.ai_analysis?.recommendation,
                    file_path: failure.ai_analysis?.file_path,
                    error_line: extractErrorLineNumber(failure.stack_trace),
                    confidence_score: failure.ai_analysis?.confidence_score,
                    classification: failure.ai_analysis?.classification,
                    severity: failure.ai_analysis?.severity,
                    build_id: buildId,
                    code_patch: failure.ai_analysis?.code_patch,
                    before_code: failure.ai_analysis?.before_code,
                    after_code: failure.ai_analysis?.after_code
                  }}
                  onApprove={handleFixApprove}
                  onReject={handleFixReject}
                  onFeedback={handleFixFeedback}
                  prStatus={prStatus}
                  disabled={!!prStatus}
                />
              </TabPanel>
            )}
          </Paper>
        </Grid>

      </Grid>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Feedback Modal for Reject/Refine */}
      <FeedbackModal
        open={feedbackModalOpen}
        onClose={handleModalClose}
        onSubmit={handleFeedbackSubmit}
        feedbackType={feedbackModalType}
        buildId={buildId}
        isLoading={feedbackMutation.isLoading}
      />
    </Box>
  )
}

export default FailureDetails
