import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
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
  Card,
  CardContent,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  Code as CodeIcon,
  BugReport as BugReportIcon
} from '@mui/icons-material'
import { failuresAPI, feedbackAPI } from '../services/api'
import { format } from 'date-fns'

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
  const queryClient = useQueryClient()
  const [feedbackOpen, setFeedbackOpen] = useState(false)
  const [feedbackType, setFeedbackType] = useState('')
  const [feedbackText, setFeedbackText] = useState('')
  const [tabValue, setTabValue] = useState(0)

  const { data, isLoading, error } = useQuery(
    ['failure-details', buildId],
    () => failuresAPI.getDetails(buildId)
  )

  const feedbackMutation = useMutation(
    (feedbackData) => feedbackAPI.submit(feedbackData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['failure-details', buildId])
        setFeedbackOpen(false)
        setFeedbackText('')
      }
    }
  )

  const handleFeedbackOpen = (type) => {
    setFeedbackType(type)
    setFeedbackOpen(true)
  }

  const handleFeedbackSubmit = () => {
    feedbackMutation.mutate({
      build_id: buildId,
      feedback_type: feedbackType,
      feedback_text: feedbackText,
      user_id: 'dashboard-user'
    })
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

  const { failure, feedback, full_context } = data?.data || {}

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
      </Box>

      <Grid container spacing={3}>
        {/* Main Info Card */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="textSecondary">Job Name</Typography>
                <Typography variant="body1" gutterBottom>{failure.job_name || 'N/A'}</Typography>

                <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 2 }}>Test Suite</Typography>
                <Typography variant="body1" gutterBottom>{failure.test_suite || 'N/A'}</Typography>

                <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 2 }}>Error Category</Typography>
                <Chip
                  label={failure.error_category}
                  color="error"
                  sx={{ mt: 1 }}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="textSecondary">Confidence Score</Typography>
                <Typography variant="h5" gutterBottom>
                  {Math.round(failure.confidence_score * 100)}%
                </Typography>

                <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 2 }}>Consecutive Failures</Typography>
                <Typography variant="h5" gutterBottom>{failure.consecutive_failures}</Typography>

                <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 2 }}>Analysis Date</Typography>
                <Typography variant="body1">
                  {format(new Date(failure.created_at), 'MMM dd, yyyy HH:mm:ss')}
                </Typography>
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            {/* Root Cause */}
            <Typography variant="h6" gutterBottom>
              <BugReportIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Root Cause Analysis
            </Typography>
            <Paper sx={{ p: 2, bgcolor: '#f5f5f5', mb: 3 }}>
              <Typography variant="body1" style={{ whiteSpace: 'pre-wrap' }}>
                {failure.root_cause}
              </Typography>
            </Paper>

            {/* Fix Recommendation */}
            <Typography variant="h6" gutterBottom>
              <CodeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Fix Recommendation
            </Typography>
            <Paper sx={{ p: 2, bgcolor: '#f5f5f5', mb: 3 }}>
              <Typography variant="body1" style={{ whiteSpace: 'pre-wrap' }}>
                {failure.fix_recommendation}
              </Typography>
            </Paper>

            {/* Feedback Buttons */}
            {!failure.feedback_result && (
              <Box display="flex" gap={2}>
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<ThumbUpIcon />}
                  onClick={() => handleFeedbackOpen('success')}
                >
                  Fix Worked
                </Button>
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<ThumbDownIcon />}
                  onClick={() => handleFeedbackOpen('failed')}
                >
                  Fix Did Not Work
                </Button>
              </Box>
            )}

            {failure.feedback_result && (
              <Alert severity={failure.feedback_result === 'success' ? 'success' : 'warning'}>
                Feedback received: {failure.feedback_result}
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Full Context Tabs */}
        <Grid item xs={12}>
          <Paper>
            <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
              <Tab label="Console Log" />
              <Tab label="Error Details" />
              <Tab label="Test Results" />
              <Tab label="System Info" />
              <Tab label="Feedback History" />
            </Tabs>

            <TabPanel value={tabValue} index={0}>
              <Paper sx={{ p: 2, bgcolor: '#1e1e1e', color: '#fff', fontFamily: 'monospace', maxHeight: 500, overflow: 'auto' }}>
                <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                  {full_context?.console_log || 'No console log available'}
                </pre>
              </Paper>
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                {JSON.stringify(full_context?.error_details, null, 2) || 'No error details available'}
              </pre>
            </TabPanel>

            <TabPanel value={tabValue} index={2}>
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                {JSON.stringify(full_context?.test_results, null, 2) || 'No test results available'}
              </pre>
            </TabPanel>

            <TabPanel value={tabValue} index={3}>
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                {JSON.stringify(full_context?.system_info, null, 2) || 'No system info available'}
              </pre>
            </TabPanel>

            <TabPanel value={tabValue} index={4}>
              {feedback && feedback.length > 0 ? (
                feedback.map((fb, idx) => (
                  <Card key={idx} sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="subtitle2" color="textSecondary">
                        {format(new Date(fb.created_at), 'MMM dd, yyyy HH:mm')}
                      </Typography>
                      <Chip
                        label={fb.feedback_type}
                        size="small"
                        color={fb.feedback_type === 'success' ? 'success' : 'error'}
                        sx={{ mb: 1 }}
                      />
                      {fb.feedback_text && (
                        <Typography variant="body2">{fb.feedback_text}</Typography>
                      )}
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Typography color="textSecondary">No feedback yet</Typography>
              )}
            </TabPanel>
          </Paper>
        </Grid>

        {/* Jenkins Link */}
        {failure.build_url && (
          <Grid item xs={12}>
            <Button
              variant="outlined"
              href={failure.build_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              View in Jenkins
            </Button>
          </Grid>
        )}
      </Grid>

      {/* Feedback Dialog */}
      <Dialog open={feedbackOpen} onClose={() => setFeedbackOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Submit Feedback: {feedbackType === 'success' ? 'Fix Worked' : 'Fix Did Not Work'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Additional Comments (Optional)"
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackOpen(false)}>Cancel</Button>
          <Button
            onClick={handleFeedbackSubmit}
            variant="contained"
            disabled={feedbackMutation.isLoading}
          >
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default FailureDetails
