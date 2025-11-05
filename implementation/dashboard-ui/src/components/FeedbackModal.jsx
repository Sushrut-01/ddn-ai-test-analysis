import React, { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  CircularProgress
} from '@mui/material'
import {
  Cancel as CancelIcon,
  Edit as EditIcon,
  Send as SendIcon
} from '@mui/icons-material'

/**
 * FeedbackModal Component
 *
 * Modal dialog for collecting detailed feedback when rejecting or refining AI analysis.
 *
 * Props:
 * - open: boolean - Controls modal visibility
 * - onClose: function - Handler for closing modal
 * - onSubmit: function - Handler for submitting feedback
 * - feedbackType: 'reject' | 'refine' - Type of feedback being collected
 * - buildId: string - Build ID for the failure
 * - isLoading: boolean - Loading state during submission
 */
function FeedbackModal({ open, onClose, onSubmit, feedbackType, buildId, isLoading = false }) {
  const [reason, setReason] = useState('')
  const [comment, setComment] = useState('')
  const [suggestion, setSuggestion] = useState('')
  const [refinementOptions, setRefinementOptions] = useState([])

  const isReject = feedbackType === 'reject'
  const isRefine = feedbackType === 'refine'

  const rejectReasons = [
    'Incorrect root cause analysis',
    'Wrong fix recommendation',
    'Missing critical information',
    'Analysis not applicable',
    'Severity assessment incorrect',
    'Other (please specify)'
  ]

  const refinementOptionsAvailable = [
    'Need more context from code',
    'Need previous error history',
    'Need environment details',
    'Need stack trace analysis',
    'Need similar case comparison'
  ]

  const handleSubmit = () => {
    const feedbackData = {
      build_id: buildId,
      feedback_type: feedbackType,
      validation_status: isReject ? 'rejected' : 'refining',
      reason: reason,
      comment: comment,
      suggestion: isRefine ? suggestion : null,
      refinement_options: isRefine ? refinementOptions : null,
      timestamp: new Date().toISOString()
    }

    onSubmit(feedbackData)
  }

  const handleClose = () => {
    // Reset form
    setReason('')
    setComment('')
    setSuggestion('')
    setRefinementOptions([])
    onClose()
  }

  const isFormValid = () => {
    if (isReject) {
      return reason !== '' && comment.trim() !== ''
    }
    if (isRefine) {
      return suggestion.trim() !== '' && refinementOptions.length > 0
    }
    return false
  }

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      aria-labelledby="feedback-modal-title"
    >
      <DialogTitle id="feedback-modal-title">
        <Box display="flex" alignItems="center" gap={1}>
          {isReject ? <CancelIcon color="error" /> : <EditIcon color="warning" />}
          <Typography variant="h6">
            {isReject ? 'Reject AI Analysis' : 'Refine AI Analysis'}
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Box display="flex" flexDirection="column" gap={3}>
          {/* Build ID display */}
          <Box>
            <Typography variant="caption" color="textSecondary">
              Build ID
            </Typography>
            <Typography variant="body2" fontFamily="monospace">
              {buildId}
            </Typography>
          </Box>

          {/* Reject Form */}
          {isReject && (
            <>
              <FormControl fullWidth required>
                <InputLabel id="reject-reason-label">Reason for Rejection</InputLabel>
                <Select
                  labelId="reject-reason-label"
                  id="reject-reason"
                  value={reason}
                  label="Reason for Rejection"
                  onChange={(e) => setReason(e.target.value)}
                >
                  {rejectReasons.map((r) => (
                    <MenuItem key={r} value={r}>
                      {r}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                label="Additional Comments"
                placeholder="Please provide detailed feedback on why this analysis is incorrect..."
                multiline
                rows={4}
                fullWidth
                required
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                helperText="Your feedback will help improve future AI analysis"
              />
            </>
          )}

          {/* Refine Form */}
          {isRefine && (
            <>
              <TextField
                label="Suggestions for Refinement"
                placeholder="What additional information or changes would improve this analysis?"
                multiline
                rows={4}
                fullWidth
                required
                value={suggestion}
                onChange={(e) => setSuggestion(e.target.value)}
                helperText="Be specific about what needs to be refined"
              />

              <FormControl fullWidth required>
                <InputLabel id="refinement-options-label">What additional data should be included?</InputLabel>
                <Select
                  labelId="refinement-options-label"
                  id="refinement-options"
                  multiple
                  value={refinementOptions}
                  label="What additional data should be included?"
                  onChange={(e) => setRefinementOptions(e.target.value)}
                  renderValue={(selected) => selected.join(', ')}
                >
                  {refinementOptionsAvailable.map((option) => (
                    <MenuItem key={option} value={option}>
                      {option}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Box bgcolor="#fff3e0" p={2} borderRadius={1}>
                <Typography variant="body2" color="textSecondary">
                  After submitting, the refinement workflow will automatically start and re-analyze
                  this failure with your suggestions included as additional context.
                </Typography>
              </Box>
            </>
          )}
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button
          onClick={handleClose}
          disabled={isLoading}
          color="inherit"
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={!isFormValid() || isLoading}
          variant="contained"
          color={isReject ? 'error' : 'warning'}
          startIcon={isLoading ? <CircularProgress size={20} /> : <SendIcon />}
        >
          {isLoading ? 'Submitting...' : 'Submit Feedback'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default FeedbackModal
