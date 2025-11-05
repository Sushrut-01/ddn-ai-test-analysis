import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  Chip,
  LinearProgress,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Snackbar
} from '@mui/material'
import {
  PlayArrow as PlayArrowIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  SelectAll as SelectAllIcon,
  Deselect as DeselectIcon
} from '@mui/icons-material'
import { failuresAPI, triggerAPI } from '../services/api'
import { format } from 'date-fns'

/**
 * TriggerAnalysis Page - Task 0F.7
 *
 * Provides interface for bulk triggering AI analysis on unanalyzed test failures.
 *
 * Features:
 * - Lists all failures without AI analysis
 * - Bulk selection and triggering
 * - Progress tracking
 * - Real-time status updates
 */
function TriggerAnalysis() {
  const queryClient = useQueryClient()
  const [selectedBuilds, setSelectedBuilds] = useState(new Set())
  const [analyzingBuilds, setAnalyzingBuilds] = useState(new Set())
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' })

  // Query for unanalyzed failures
  const { data, isLoading, error, refetch } = useQuery(
    'unanalyzed-failures',
    async () => {
      // Get all failures and filter for those without AI analysis
      const response = await failuresAPI.getList({ limit: 100 })
      const failures = response?.data?.failures || []

      // Filter out failures that already have AI analysis
      return failures.filter(failure => !failure.ai_analysis || !failure.ai_analysis?.classification)
    },
    {
      refetchInterval: 10000, // Auto-refresh every 10 seconds
      staleTime: 5000,
      onError: (error) => console.warn('Failed to fetch unanalyzed failures:', error)
    }
  )

  // Mutation for bulk triggering
  const triggerMutation = useMutation(
    async (buildIds) => {
      const results = []

      for (const buildId of buildIds) {
        setAnalyzingBuilds(prev => new Set([...prev, buildId]))

        try {
          const result = await triggerAPI.triggerAnalysis({
            build_id: buildId,
            trigger_source: 'bulk_ui'
          })
          results.push({ buildId, success: true, result })
        } catch (error) {
          results.push({ buildId, success: false, error: error.message })
        }

        // Small delay between requests to avoid overwhelming the server
        await new Promise(resolve => setTimeout(resolve, 500))
      }

      return results
    },
    {
      onSuccess: (results) => {
        const successCount = results.filter(r => r.success).length
        const failCount = results.filter(r => !r.success).length

        setSnackbar({
          open: true,
          message: `Triggered ${successCount} analyses. ${failCount} failed.`,
          severity: failCount > 0 ? 'warning' : 'success'
        })

        setSelectedBuilds(new Set())
        setAnalyzingBuilds(new Set())

        // Refetch to update the list
        setTimeout(() => {
          refetch()
          queryClient.invalidateQueries('failures')
        }, 3000)
      },
      onError: (error) => {
        setSnackbar({
          open: true,
          message: `Failed to trigger analyses: ${error.message}`,
          severity: 'error'
        })
        setAnalyzingBuilds(new Set())
      }
    }
  )

  // Handlers
  const handleSelectAll = () => {
    if (!data) return
    setSelectedBuilds(new Set(data.map(f => f._id)))
  }

  const handleDeselectAll = () => {
    setSelectedBuilds(new Set())
  }

  const handleToggle = (buildId) => {
    const newSelected = new Set(selectedBuilds)
    if (newSelected.has(buildId)) {
      newSelected.delete(buildId)
    } else {
      newSelected.add(buildId)
    }
    setSelectedBuilds(newSelected)
  }

  const handleTriggerSelected = () => {
    if (selectedBuilds.size === 0) {
      setSnackbar({
        open: true,
        message: 'Please select at least one failure to analyze',
        severity: 'warning'
      })
      return
    }

    triggerMutation.mutate([...selectedBuilds])
  }

  const unanalyzedFailures = data || []
  const selectedCount = selectedBuilds.size
  const analyzingCount = analyzingBuilds.size
  const isAnalyzing = triggerMutation.isLoading

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Trigger AI Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manually trigger AI analysis for test failures that haven't been analyzed yet
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Unanalyzed Failures
              </Typography>
              <Typography variant="h3">
                {unanalyzedFailures.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Selected
              </Typography>
              <Typography variant="h3" color="primary">
                {selectedCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Analyzing
              </Typography>
              <Typography variant="h3" color="warning.main">
                {analyzingCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Success Rate
              </Typography>
              <Typography variant="h3" color="success.main">
                {triggerMutation.data ?
                  `${Math.round((triggerMutation.data.filter(r => r.success).length / triggerMutation.data.length) * 100)}%` :
                  'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Actions Bar */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            startIcon={isAnalyzing ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
            onClick={handleTriggerSelected}
            disabled={selectedCount === 0 || isAnalyzing}
          >
            {isAnalyzing ? `Analyzing ${analyzingCount}...` : `Analyze Selected (${selectedCount})`}
          </Button>

          <Button
            variant="outlined"
            startIcon={<SelectAllIcon />}
            onClick={handleSelectAll}
            disabled={isAnalyzing}
          >
            Select All
          </Button>

          <Button
            variant="outlined"
            startIcon={<DeselectIcon />}
            onClick={handleDeselectAll}
            disabled={selectedCount === 0 || isAnalyzing}
          >
            Deselect All
          </Button>

          <Box sx={{ flex: 1 }} />

          <IconButton onClick={refetch} disabled={isLoading}>
            <RefreshIcon />
          </IconButton>
        </Box>

        {/* Progress Bar */}
        {isAnalyzing && (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Processing {analyzingCount} / {selectedCount}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {Math.round((analyzingCount / selectedCount) * 100)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={(analyzingCount / selectedCount) * 100}
            />
          </Box>
        )}
      </Paper>

      {/* Failures Table */}
      <Paper>
        {isLoading ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress />
            <Typography sx={{ mt: 2 }}>Loading unanalyzed failures...</Typography>
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ m: 2 }}>
            Error loading failures: {error.message}
          </Alert>
        ) : unanalyzedFailures.length === 0 ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <CheckCircleIcon sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              All Failures Analyzed!
            </Typography>
            <Typography color="text.secondary">
              There are no unanalyzed test failures at this time.
            </Typography>
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selectedCount === unanalyzedFailures.length && unanalyzedFailures.length > 0}
                      indeterminate={selectedCount > 0 && selectedCount < unanalyzedFailures.length}
                      onChange={() => selectedCount === unanalyzedFailures.length ? handleDeselectAll() : handleSelectAll()}
                      disabled={isAnalyzing}
                    />
                  </TableCell>
                  <TableCell>Build ID</TableCell>
                  <TableCell>Test Name</TableCell>
                  <TableCell>Suite</TableCell>
                  <TableCell>Error Message</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {unanalyzedFailures.map((failure) => {
                  const isSelected = selectedBuilds.has(failure._id)
                  const isCurrentlyAnalyzing = analyzingBuilds.has(failure._id)

                  return (
                    <TableRow
                      key={failure._id}
                      hover
                      selected={isSelected}
                      sx={{ opacity: isCurrentlyAnalyzing ? 0.6 : 1 }}
                    >
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={isSelected}
                          onChange={() => handleToggle(failure._id)}
                          disabled={isAnalyzing}
                        />
                      </TableCell>
                      <TableCell>
                        <Tooltip title={failure.build_id || failure._id}>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 150 }}>
                            {failure.build_id || failure._id}
                          </Typography>
                        </Tooltip>
                      </TableCell>
                      <TableCell>
                        <Tooltip title={failure.test_name || 'Unknown'}>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                            {failure.test_name || 'Unknown Test'}
                          </Typography>
                        </Tooltip>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={failure.suite || 'Unknown'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Tooltip title={failure.error || failure.error_message || 'No error message'}>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                            {failure.error || failure.error_message || 'No error message'}
                          </Typography>
                        </Tooltip>
                      </TableCell>
                      <TableCell>
                        {failure.timestamp ? format(new Date(failure.timestamp), 'MMM dd, yyyy HH:mm') : 'N/A'}
                      </TableCell>
                      <TableCell>
                        {isCurrentlyAnalyzing ? (
                          <Chip
                            icon={<CircularProgress size={16} />}
                            label="Analyzing..."
                            size="small"
                            color="warning"
                          />
                        ) : (
                          <Chip
                            icon={<ErrorIcon />}
                            label="Not Analyzed"
                            size="small"
                            color="error"
                            variant="outlined"
                          />
                        )}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default TriggerAnalysis
