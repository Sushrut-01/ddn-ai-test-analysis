import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  TablePagination
} from '@mui/material'
import { PlayArrow as PlayArrowIcon } from '@mui/icons-material'
import { triggerAPI } from '../services/api'
import { format } from 'date-fns'

function ManualTrigger() {
  const queryClient = useQueryClient()
  const [buildId, setBuildId] = useState('')
  const [triggeredByUser, setTriggeredByUser] = useState('')
  const [reason, setReason] = useState('')
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(20)

  const { data: historyData, isLoading: historyLoading } = useQuery(
    ['trigger-history', page + 1, rowsPerPage],
    () => triggerAPI.getHistory(page + 1, rowsPerPage),
    { keepPreviousData: true }
  )

  const triggerMutation = useMutation(
    (data) => triggerAPI.triggerAnalysis(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('trigger-history')
        setBuildId('')
        setReason('')
      }
    }
  )

  const handleTrigger = () => {
    if (!buildId.trim()) {
      return
    }

    triggerMutation.mutate({
      build_id: buildId.trim(),
      triggered_by_user: triggeredByUser.trim() || 'dashboard-user',
      reason: reason.trim() || 'Manual trigger from dashboard'
    })
  }

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const triggers = historyData?.data?.triggers || []
  const pagination = historyData?.data?.pagination || { total: 0, pages: 0 }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Manual Trigger
      </Typography>
      <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 3 }}>
        Manually trigger AI analysis for specific build failures (bypasses 3-failure rule)
      </Typography>

      <Grid container spacing={3}>
        {/* Trigger Form */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Trigger AI Analysis
            </Typography>

            <TextField
              fullWidth
              label="Build ID"
              value={buildId}
              onChange={(e) => setBuildId(e.target.value)}
              placeholder="e.g., 12345"
              required
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Triggered By (Email)"
              value={triggeredByUser}
              onChange={(e) => setTriggeredByUser(e.target.value)}
              placeholder="e.g., john.doe@company.com"
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              multiline
              rows={3}
              label="Reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Why is manual trigger needed? e.g., Critical production issue"
              sx={{ mb: 2 }}
            />

            <Button
              variant="contained"
              size="large"
              fullWidth
              startIcon={<PlayArrowIcon />}
              onClick={handleTrigger}
              disabled={!buildId.trim() || triggerMutation.isLoading}
            >
              {triggerMutation.isLoading ? 'Triggering...' : 'Trigger Analysis'}
            </Button>

            {triggerMutation.isSuccess && (
              <Alert severity="success" sx={{ mt: 2 }}>
                AI analysis triggered successfully! Check your Teams notifications for results.
              </Alert>
            )}

            {triggerMutation.isError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                Failed to trigger analysis: {triggerMutation.error?.response?.data?.message || 'Unknown error'}
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Info Card */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              About Manual Triggers
            </Typography>
            <Typography variant="body2" paragraph>
              Manual triggers allow you to bypass the 3-failure rule and immediately trigger AI analysis for a specific build.
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>When to use:</strong>
            </Typography>
            <ul>
              <li>
                <Typography variant="body2">Critical production failures requiring immediate attention</Typography>
              </li>
              <li>
                <Typography variant="body2">First-time failures in important pipelines</Typography>
              </li>
              <li>
                <Typography variant="body2">Urgent debugging sessions</Typography>
              </li>
              <li>
                <Typography variant="body2">When you need AI insights before 3 consecutive failures</Typography>
              </li>
            </ul>
            <Typography variant="body2" paragraph sx={{ mt: 2 }}>
              <strong>What happens:</strong>
            </Typography>
            <ol>
              <li>
                <Typography variant="body2">System fetches complete failure context from MongoDB</Typography>
              </li>
              <li>
                <Typography variant="body2">AI analyzes logs and generates recommendations</Typography>
              </li>
              <li>
                <Typography variant="body2">Results sent to Teams with feedback buttons</Typography>
              </li>
              <li>
                <Typography variant="body2">Analysis stored in database for future reference</Typography>
              </li>
            </ol>
          </Paper>
        </Grid>

        {/* Trigger History */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Manual Trigger History
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 2 }}>
              View all manual trigger events
            </Typography>

            {historyLoading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Build ID</TableCell>
                        <TableCell>Triggered By</TableCell>
                        <TableCell>Source</TableCell>
                        <TableCell>Reason</TableCell>
                        <TableCell align="center">Failures at Trigger</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Date</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {triggers.map((trigger) => (
                        <TableRow key={trigger.id}>
                          <TableCell>
                            <Typography variant="body2" fontFamily="monospace">
                              {trigger.build_id}
                            </Typography>
                          </TableCell>
                          <TableCell>{trigger.triggered_by_user}</TableCell>
                          <TableCell>
                            <Chip label={trigger.trigger_source} size="small" />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                              {trigger.reason}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label={trigger.consecutive_failures_at_trigger}
                              size="small"
                              color={trigger.consecutive_failures_at_trigger >= 3 ? 'error' : 'default'}
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={trigger.trigger_successful ? 'Success' : 'Failed'}
                              size="small"
                              color={trigger.trigger_successful ? 'success' : 'error'}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {format(new Date(trigger.triggered_at), 'MMM dd, HH:mm')}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                <TablePagination
                  rowsPerPageOptions={[10, 20, 50]}
                  component="div"
                  count={pagination.total}
                  rowsPerPage={rowsPerPage}
                  page={page}
                  onPageChange={handleChangePage}
                  onRowsPerPageChange={handleChangeRowsPerPage}
                />
              </>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default ManualTrigger
