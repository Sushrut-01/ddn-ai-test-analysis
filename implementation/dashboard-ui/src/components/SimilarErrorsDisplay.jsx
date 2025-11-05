import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Grid,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Button,
  Paper
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  LibraryBooks as LibraryBooksIcon,
  Code as CodeIcon,
  LightbulbOutlined as LightbulbIcon,
  Security as SecurityIcon,
  Build as BuildIcon,
  Warning as WarningIcon
} from '@mui/icons-material'
import CodeSnippet from './CodeSnippet'

/**
 * SimilarErrorsDisplay Component - Task 0B.8
 *
 * Displays similar documented errors from the RAG system with:
 * - Similarity scoring (color-coded)
 * - Error details (ID, type, category, root cause)
 * - Expandable solution steps
 * - Code before/after comparison using CodeSnippet
 * - Prevention tips
 *
 * Props:
 * - similarCases: array - Array of similar error objects from AI analysis
 *   [{
 *     error_id: string,
 *     error_type: string,
 *     error_category: string,
 *     similarity_score: number (0-1),
 *     root_cause: string,
 *     solution_steps: string[],
 *     code_before: string,
 *     code_after: string,
 *     prevention: string,
 *     severity: string,
 *     tags: string[]
 *   }]
 * - maxDisplay: number - Maximum errors to display (default: 5)
 * - showCodeExamples: boolean - Whether to show code snippets (default: true)
 */
function SimilarErrorsDisplay({
  similarCases = [],
  maxDisplay = 5,
  showCodeExamples = true
}) {
  const [expandedPanels, setExpandedPanels] = useState({})

  // Handle accordion expand/collapse
  const handleAccordionChange = (errorId) => (event, isExpanded) => {
    setExpandedPanels(prev => ({
      ...prev,
      [errorId]: isExpanded
    }))
  }

  // Get similarity color based on score
  const getSimilarityColor = (score) => {
    const percentage = score * 100
    if (percentage >= 80) return 'success'
    if (percentage >= 60) return 'warning'
    return 'default'
  }

  // Get similarity label
  const getSimilarityLabel = (score) => {
    const percentage = score * 100
    if (percentage >= 80) return 'High Match'
    if (percentage >= 60) return 'Good Match'
    return 'Possible Match'
  }

  // Get severity color
  const getSeverityColor = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL': return 'error'
      case 'HIGH': return 'warning'
      case 'MEDIUM': return 'info'
      case 'LOW': return 'default'
      default: return 'default'
    }
  }

  // Get category icon
  const getCategoryIcon = (category) => {
    switch (category?.toUpperCase()) {
      case 'CODE': return <CodeIcon />
      case 'SECURITY': return <SecurityIcon />
      case 'INFRASTRUCTURE': return <BuildIcon />
      case 'CONFIGURATION': return <BuildIcon />
      default: return <ErrorIcon />
    }
  }

  // Empty state
  if (!similarCases || similarCases.length === 0) {
    return (
      <Paper
        elevation={1}
        sx={{
          p: 4,
          textAlign: 'center',
          bgcolor: 'grey.50',
          border: '1px dashed',
          borderColor: 'grey.300'
        }}
      >
        <LibraryBooksIcon sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No Similar Documented Errors Found
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          This error doesn't closely match any documented cases in our knowledge base.
          <br />
          Consider contributing this error to our documentation after resolving it.
        </Typography>
        <Button
          variant="outlined"
          startIcon={<LibraryBooksIcon />}
          sx={{ mt: 2 }}
          href="#"
          onClick={(e) => {
            e.preventDefault()
            alert('See CONTRIBUTING-ERROR-DOCS.md for contribution guidelines')
          }}
        >
          Learn How to Contribute
        </Button>
      </Paper>
    )
  }

  // Limit display to maxDisplay
  const displayCases = similarCases.slice(0, maxDisplay)

  return (
    <Box sx={{ mt: 2 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <LibraryBooksIcon color="primary" />
          <Typography variant="h6" fontWeight={600}>
            Similar Documented Errors
          </Typography>
          <Chip
            label={`${displayCases.length} match${displayCases.length > 1 ? 'es' : ''}`}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>
        <Alert severity="info" sx={{ mt: 1 }}>
          These documented errors were found by our RAG system based on semantic similarity.
          Review the solutions below for potential fixes.
        </Alert>
      </Box>

      {/* Similar Error Cards */}
      <Grid container spacing={2}>
        {displayCases.map((errorCase, index) => {
          const similarityPercentage = Math.round((errorCase.similarity_score || 0) * 100)
          const isExpanded = expandedPanels[errorCase.error_id] || false

          return (
            <Grid item xs={12} key={errorCase.error_id || index}>
              <Card
                elevation={3}
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  '&:hover': {
                    boxShadow: 6,
                    borderColor: 'primary.main'
                  },
                  transition: 'all 0.2s'
                }}
              >
                <CardContent>
                  {/* Header Row */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                    {/* Error ID Badge */}
                    <Chip
                      label={errorCase.error_id}
                      color="primary"
                      size="small"
                      sx={{ fontWeight: 600, fontFamily: 'monospace' }}
                    />

                    {/* Category Icon & Label */}
                    <Chip
                      icon={getCategoryIcon(errorCase.error_category)}
                      label={errorCase.error_category || 'UNKNOWN'}
                      size="small"
                      variant="outlined"
                    />

                    {/* Severity */}
                    {errorCase.severity && (
                      <Chip
                        label={errorCase.severity}
                        size="small"
                        color={getSeverityColor(errorCase.severity)}
                      />
                    )}

                    {/* Similarity Score */}
                    <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        {getSimilarityLabel(errorCase.similarity_score)}
                      </Typography>
                      <Chip
                        label={`${similarityPercentage}%`}
                        size="small"
                        color={getSimilarityColor(errorCase.similarity_score)}
                        sx={{ fontWeight: 600 }}
                      />
                    </Box>
                  </Box>

                  {/* Similarity Progress Bar */}
                  <LinearProgress
                    variant="determinate"
                    value={similarityPercentage}
                    color={getSimilarityColor(errorCase.similarity_score)}
                    sx={{ mb: 2, height: 6, borderRadius: 3 }}
                  />

                  {/* Error Type */}
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ErrorIcon fontSize="small" color="error" />
                    {errorCase.error_type || 'Unknown Error Type'}
                  </Typography>

                  {/* Tags */}
                  {errorCase.tags && errorCase.tags.length > 0 && (
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 2 }}>
                      {errorCase.tags.map((tag, idx) => (
                        <Chip
                          key={idx}
                          label={tag}
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: '0.7rem' }}
                        />
                      ))}
                    </Box>
                  )}

                  <Divider sx={{ my: 2 }} />

                  {/* Root Cause Snippet */}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Root Cause:
                    </Typography>
                    <Typography variant="body2" sx={{ pl: 2, borderLeft: 3, borderColor: 'warning.main' }}>
                      {errorCase.root_cause && errorCase.root_cause.length > 300
                        ? errorCase.root_cause.substring(0, 300) + '...'
                        : errorCase.root_cause || 'No root cause documented'}
                    </Typography>
                  </Box>

                  {/* Expandable Solution Section */}
                  <Accordion
                    expanded={isExpanded}
                    onChange={handleAccordionChange(errorCase.error_id)}
                    sx={{ boxShadow: 0, '&:before': { display: 'none' } }}
                  >
                    <AccordionSummary
                      expandIcon={<ExpandMoreIcon />}
                      sx={{
                        bgcolor: 'primary.50',
                        borderRadius: 1,
                        '&:hover': { bgcolor: 'primary.100' }
                      }}
                    >
                      <Typography variant="subtitle1" fontWeight={600} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CheckCircleIcon fontSize="small" color="success" />
                        View Complete Solution
                      </Typography>
                    </AccordionSummary>

                    <AccordionDetails sx={{ pt: 3 }}>
                      {/* Full Root Cause */}
                      {errorCase.root_cause && errorCase.root_cause.length > 300 && (
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            Complete Root Cause:
                          </Typography>
                          <Typography variant="body2" sx={{ pl: 2, borderLeft: 3, borderColor: 'warning.main' }}>
                            {errorCase.root_cause}
                          </Typography>
                        </Box>
                      )}

                      {/* Solution Steps */}
                      {errorCase.solution_steps && errorCase.solution_steps.length > 0 && (
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <CheckCircleIcon fontSize="small" color="success" />
                            Solution Steps:
                          </Typography>
                          <List dense>
                            {errorCase.solution_steps.map((step, idx) => (
                              <ListItem key={idx} sx={{ alignItems: 'flex-start' }}>
                                <ListItemIcon sx={{ minWidth: 36, mt: 0.5 }}>
                                  <Chip
                                    label={idx + 1}
                                    size="small"
                                    color="primary"
                                    sx={{ width: 24, height: 24, fontSize: '0.75rem' }}
                                  />
                                </ListItemIcon>
                                <ListItemText
                                  primary={step}
                                  primaryTypographyProps={{ variant: 'body2' }}
                                />
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      )}

                      {/* Code Examples */}
                      {showCodeExamples && (errorCase.code_before || errorCase.code_after) && (
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                            <CodeIcon fontSize="small" />
                            Code Example:
                          </Typography>

                          <Grid container spacing={2}>
                            {/* Before */}
                            {errorCase.code_before && (
                              <Grid item xs={12} md={6}>
                                <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                                  <Typography variant="caption" fontWeight={600} color="error" sx={{ mb: 1, display: 'block' }}>
                                    BEFORE (Problematic Code):
                                  </Typography>
                                  <CodeSnippet
                                    fileData={{
                                      file_path: errorCase.file_path || 'example.java',
                                      content: errorCase.code_before,
                                      total_lines: errorCase.code_before.split('\n').length,
                                      line_range: errorCase.line_range || 'Complete file'
                                    }}
                                    showHeader={false}
                                    maxHeight={300}
                                    defaultExpanded={true}
                                  />
                                </Paper>
                              </Grid>
                            )}

                            {/* After */}
                            {errorCase.code_after && (
                              <Grid item xs={12} md={6}>
                                <Paper elevation={1} sx={{ p: 2, bgcolor: 'success.50' }}>
                                  <Typography variant="caption" fontWeight={600} color="success.dark" sx={{ mb: 1, display: 'block' }}>
                                    AFTER (Fixed Code):
                                  </Typography>
                                  <CodeSnippet
                                    fileData={{
                                      file_path: errorCase.file_path || 'example.java',
                                      content: errorCase.code_after,
                                      total_lines: errorCase.code_after.split('\n').length,
                                      line_range: errorCase.line_range || 'Complete file'
                                    }}
                                    showHeader={false}
                                    maxHeight={300}
                                    defaultExpanded={true}
                                  />
                                </Paper>
                              </Grid>
                            )}
                          </Grid>
                        </Box>
                      )}

                      {/* Prevention Tips */}
                      {errorCase.prevention && (
                        <Box sx={{ mb: 2 }}>
                          <Alert severity="success" icon={<LightbulbIcon />}>
                            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                              Prevention:
                            </Typography>
                            <Typography variant="body2">
                              {errorCase.prevention}
                            </Typography>
                          </Alert>
                        </Box>
                      )}

                      {/* Related Errors */}
                      {errorCase.related_errors && errorCase.related_errors.length > 0 && (
                        <Box>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            Related Errors:
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {errorCase.related_errors.map((relatedId, idx) => (
                              <Chip
                                key={idx}
                                label={relatedId}
                                size="small"
                                variant="outlined"
                                color="primary"
                                sx={{ fontFamily: 'monospace' }}
                              />
                            ))}
                          </Box>
                        </Box>
                      )}
                    </AccordionDetails>
                  </Accordion>
                </CardContent>
              </Card>
            </Grid>
          )
        })}
      </Grid>

      {/* Footer Note */}
      {similarCases.length > maxDisplay && (
        <Alert severity="info" sx={{ mt: 2 }}>
          Showing top {maxDisplay} of {similarCases.length} similar errors.
          Additional matches available in the AI analysis data.
        </Alert>
      )}

      <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <WarningIcon fontSize="small" />
          These are suggestions based on similar documented errors. Always verify the solution applies to your specific context.
        </Typography>
      </Box>
    </Box>
  )
}

export default SimilarErrorsDisplay
