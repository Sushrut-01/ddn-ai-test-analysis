import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  Alert,
  Stack
} from '@mui/material'
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent
} from '@mui/lab'
import {
  ExpandMore as ExpandMoreIcon,
  Compare as CompareIcon,
  CheckCircle as CheckCircleIcon,
  Edit as EditIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  BugReport as BugReportIcon
} from '@mui/icons-material'
import { format } from 'date-fns'

/**
 * BeforeAfterComparison Component
 *
 * Displays side-by-side comparison of original and refined AI analysis
 * with difference highlighting, refinement timeline, and collapsible sections.
 *
 * Props:
 * - originalAnalysis: object - Original AI analysis data
 * - refinedAnalysis: object - Refined AI analysis data
 * - refinementHistory: array - Array of refinement records with timestamps
 */
function BeforeAfterComparison({ originalAnalysis, refinedAnalysis, refinementHistory = [] }) {
  const [expandedSections, setExpandedSections] = useState({
    rootCause: true,
    recommendation: true,
    classification: false,
    severity: false,
    confidence: false
  })

  const handleAccordionChange = (section) => (event, isExpanded) => {
    setExpandedSections({
      ...expandedSections,
      [section]: isExpanded
    })
  }

  // Helper function to detect if text has changed
  const hasChanged = (originalValue, refinedValue) => {
    if (!originalValue && !refinedValue) return false
    return originalValue !== refinedValue
  }

  // Helper function to calculate confidence improvement
  const getConfidenceImprovement = () => {
    const originalConfidence = originalAnalysis?.confidence_score || 0
    const refinedConfidence = refinedAnalysis?.confidence_score || 0
    const improvement = ((refinedConfidence - originalConfidence) * 100).toFixed(1)
    return { improvement, isPositive: improvement > 0 }
  }

  // Comparison section component
  const ComparisonSection = ({ title, originalContent, refinedContent, section }) => {
    const changed = hasChanged(originalContent, refinedContent)

    return (
      <Accordion
        expanded={expandedSections[section]}
        onChange={handleAccordionChange(section)}
        sx={{
          '&:before': { display: 'none' },
          boxShadow: 1,
          mb: 1,
          border: changed ? '2px solid #ff9800' : '1px solid #e0e0e0'
        }}
      >
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          sx={{
            bgcolor: changed ? '#fff3e0' : 'transparent',
            '&:hover': { bgcolor: changed ? '#ffe0b2' : '#f5f5f5' }
          }}
        >
          <Box display="flex" alignItems="center" gap={1}>
            <CompareIcon color={changed ? 'warning' : 'action'} />
            <Typography variant="subtitle1" fontWeight={600}>
              {title}
            </Typography>
            {changed && (
              <Chip
                label="Modified"
                size="small"
                color="warning"
                icon={<EditIcon />}
                sx={{ ml: 1 }}
              />
            )}
          </Box>
        </AccordionSummary>

        <AccordionDetails>
          <Grid container spacing={2}>
            {/* Original Version */}
            <Grid item xs={12} md={6}>
              <Box>
                <Typography variant="caption" color="textSecondary" fontWeight={600} gutterBottom>
                  ORIGINAL
                </Typography>
                <Paper
                  sx={{
                    p: 2,
                    bgcolor: changed ? '#ffebee' : '#f5f5f5',
                    border: changed ? '1px solid #ef5350' : '1px solid #e0e0e0',
                    minHeight: 100
                  }}
                >
                  <Typography
                    variant="body2"
                    style={{ whiteSpace: 'pre-wrap' }}
                    color={changed ? 'error.dark' : 'textPrimary'}
                  >
                    {originalContent || 'No data'}
                  </Typography>
                </Paper>
              </Box>
            </Grid>

            {/* Refined Version */}
            <Grid item xs={12} md={6}>
              <Box>
                <Typography variant="caption" color="textSecondary" fontWeight={600} gutterBottom>
                  REFINED
                </Typography>
                <Paper
                  sx={{
                    p: 2,
                    bgcolor: changed ? '#e8f5e9' : '#f5f5f5',
                    border: changed ? '1px solid #66bb6a' : '1px solid #e0e0e0',
                    minHeight: 100
                  }}
                >
                  <Typography
                    variant="body2"
                    style={{ whiteSpace: 'pre-wrap' }}
                    color={changed ? 'success.dark' : 'textPrimary'}
                  >
                    {refinedContent || 'No data'}
                  </Typography>
                </Paper>
              </Box>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>
    )
  }

  // Stats comparison section
  const StatsComparison = () => {
    const { improvement, isPositive } = getConfidenceImprovement()
    const confidenceChanged = hasChanged(
      originalAnalysis?.confidence_score,
      refinedAnalysis?.confidence_score
    )
    const classificationChanged = hasChanged(
      originalAnalysis?.classification,
      refinedAnalysis?.classification
    )
    const severityChanged = hasChanged(
      originalAnalysis?.severity,
      refinedAnalysis?.severity
    )

    return (
      <Paper sx={{ p: 3, mb: 2, bgcolor: '#f9fafb' }}>
        <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
          <SpeedIcon color="primary" />
          Analysis Improvements Summary
        </Typography>

        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Confidence Score */}
          <Grid item xs={12} sm={4}>
            <Box textAlign="center" p={2} bgcolor="white" borderRadius={1} boxShadow={1}>
              <Typography variant="caption" color="textSecondary">
                Confidence Score
              </Typography>
              <Box display="flex" alignItems="center" justifyContent="center" gap={1} mt={1}>
                <Typography variant="h6" color="error.main">
                  {Math.round((originalAnalysis?.confidence_score || 0) * 100)}%
                </Typography>
                <Typography variant="body2">→</Typography>
                <Typography variant="h6" color="success.main">
                  {Math.round((refinedAnalysis?.confidence_score || 0) * 100)}%
                </Typography>
              </Box>
              {confidenceChanged && (
                <Chip
                  label={`${isPositive ? '+' : ''}${improvement}%`}
                  size="small"
                  color={isPositive ? 'success' : 'error'}
                  icon={<TrendingUpIcon />}
                  sx={{ mt: 1 }}
                />
              )}
            </Box>
          </Grid>

          {/* Classification */}
          <Grid item xs={12} sm={4}>
            <Box textAlign="center" p={2} bgcolor="white" borderRadius={1} boxShadow={1}>
              <Typography variant="caption" color="textSecondary">
                Classification
              </Typography>
              <Box display="flex" alignItems="center" justifyContent="center" gap={1} mt={1} flexWrap="wrap">
                <Chip
                  label={originalAnalysis?.classification || 'N/A'}
                  size="small"
                  color={classificationChanged ? 'error' : 'default'}
                />
                <Typography variant="body2">→</Typography>
                <Chip
                  label={refinedAnalysis?.classification || 'N/A'}
                  size="small"
                  color={classificationChanged ? 'success' : 'default'}
                />
              </Box>
            </Box>
          </Grid>

          {/* Severity */}
          <Grid item xs={12} sm={4}>
            <Box textAlign="center" p={2} bgcolor="white" borderRadius={1} boxShadow={1}>
              <Typography variant="caption" color="textSecondary">
                Severity
              </Typography>
              <Box display="flex" alignItems="center" justifyContent="center" gap={1} mt={1} flexWrap="wrap">
                <Chip
                  label={originalAnalysis?.severity || 'N/A'}
                  size="small"
                  color={
                    originalAnalysis?.severity === 'HIGH' ? 'error' :
                    originalAnalysis?.severity === 'MEDIUM' ? 'warning' : 'info'
                  }
                />
                <Typography variant="body2">→</Typography>
                <Chip
                  label={refinedAnalysis?.severity || 'N/A'}
                  size="small"
                  color={
                    refinedAnalysis?.severity === 'HIGH' ? 'error' :
                    refinedAnalysis?.severity === 'MEDIUM' ? 'warning' : 'info'
                  }
                />
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    )
  }

  // Refinement timeline component
  const RefinementTimeline = () => {
    if (!refinementHistory || refinementHistory.length === 0) {
      return null
    }

    return (
      <Paper sx={{ p: 3, mb: 2 }}>
        <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
          <EditIcon color="primary" />
          Refinement Timeline
        </Typography>

        <Timeline position="alternate" sx={{ mt: 2 }}>
          {refinementHistory.map((refinement, index) => (
            <TimelineItem key={index}>
              <TimelineOppositeContent color="textSecondary">
                <Typography variant="caption">
                  {refinement.timestamp ? format(new Date(refinement.timestamp), 'MMM dd, yyyy HH:mm') : 'N/A'}
                </Typography>
              </TimelineOppositeContent>

              <TimelineSeparator>
                <TimelineDot color={index === refinementHistory.length - 1 ? 'success' : 'primary'}>
                  {index === refinementHistory.length - 1 ? <CheckCircleIcon fontSize="small" /> : <EditIcon fontSize="small" />}
                </TimelineDot>
                {index < refinementHistory.length - 1 && <TimelineConnector />}
              </TimelineSeparator>

              <TimelineContent>
                <Paper elevation={2} sx={{ p: 2, bgcolor: index === refinementHistory.length - 1 ? '#e8f5e9' : 'white' }}>
                  <Typography variant="subtitle2" fontWeight={600}>
                    {refinement.feedback_type === 'refine' ? 'Refinement Requested' : 'Analysis Updated'}
                  </Typography>
                  {refinement.suggestion && (
                    <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                      {refinement.suggestion}
                    </Typography>
                  )}
                  {refinement.refinement_options && refinement.refinement_options.length > 0 && (
                    <Stack direction="row" spacing={1} sx={{ mt: 1 }} flexWrap="wrap">
                      {refinement.refinement_options.map((option, idx) => (
                        <Chip
                          key={idx}
                          label={option}
                          size="small"
                          variant="outlined"
                          sx={{ mb: 0.5 }}
                        />
                      ))}
                    </Stack>
                  )}
                </Paper>
              </TimelineContent>
            </TimelineItem>
          ))}
        </Timeline>
      </Paper>
    )
  }

  if (!originalAnalysis && !refinedAnalysis) {
    return (
      <Alert severity="info" icon={<BugReportIcon />}>
        No analysis data available for comparison.
      </Alert>
    )
  }

  if (!refinedAnalysis) {
    return (
      <Alert severity="info" icon={<EditIcon />}>
        No refinements have been made yet. Click "Refine" to request improvements to this analysis.
      </Alert>
    )
  }

  return (
    <Box>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 2, bgcolor: 'primary.main', color: 'white' }}>
        <Box display="flex" alignItems="center" gap={1}>
          <CompareIcon />
          <Typography variant="h5">
            Before & After Comparison
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
          Compare the original AI analysis with the refined version to see improvements
        </Typography>
      </Paper>

      {/* Stats Summary */}
      <StatsComparison />

      {/* Refinement Timeline */}
      <RefinementTimeline />

      {/* Detailed Comparisons */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Detailed Analysis Comparison
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <ComparisonSection
          title="Root Cause Analysis"
          originalContent={originalAnalysis?.root_cause}
          refinedContent={refinedAnalysis?.root_cause}
          section="rootCause"
        />

        <ComparisonSection
          title="Fix Recommendation"
          originalContent={originalAnalysis?.recommendation}
          refinedContent={refinedAnalysis?.recommendation}
          section="recommendation"
        />

        <ComparisonSection
          title="Classification"
          originalContent={originalAnalysis?.classification}
          refinedContent={refinedAnalysis?.classification}
          section="classification"
        />

        <ComparisonSection
          title="Severity Assessment"
          originalContent={originalAnalysis?.severity}
          refinedContent={refinedAnalysis?.severity}
          section="severity"
        />

        <ComparisonSection
          title="Confidence Score Details"
          originalContent={`${Math.round((originalAnalysis?.confidence_score || 0) * 100)}% confidence`}
          refinedContent={`${Math.round((refinedAnalysis?.confidence_score || 0) * 100)}% confidence`}
          section="confidence"
        />
      </Paper>

      {/* Summary Footer */}
      <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mt: 2 }}>
        Analysis has been refined based on feedback. Review the changes above to see improvements.
      </Alert>
    </Box>
  )
}

export default BeforeAfterComparison
