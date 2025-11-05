import React, { useState } from 'react'
import { useQuery } from 'react-query'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  TextField,
  MenuItem,
  Grid,
  CircularProgress,
  Alert
} from '@mui/material'
import { Visibility as VisibilityIcon } from '@mui/icons-material'
import { failuresAPI } from '../services/api'
import { format } from 'date-fns'
import FeedbackStatusBadge from '../components/FeedbackStatusBadge'

const ERROR_CATEGORIES = [
  { value: '', label: 'All Categories' },
  { value: 'CODE_ERROR', label: 'Code Error' },
  { value: 'TEST_FAILURE', label: 'Test Failure' },
  { value: 'INFRA_ERROR', label: 'Infrastructure Error' },
  { value: 'DEPENDENCY_ERROR', label: 'Dependency Error' },
  { value: 'CONFIG_ERROR', label: 'Config Error' }
]

const FEEDBACK_STATUSES = [
  { value: '', label: 'All Statuses' },
  { value: 'accepted', label: 'Accepted' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'refining', label: 'Refining' },
  { value: 'refined', label: 'Refined' },
  { value: 'pending', label: 'Pending Review' }
]

function Failures() {
  const navigate = useNavigate()
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(20)
  const [category, setCategory] = useState('')
  const [feedbackStatus, setFeedbackStatus] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  const { data, isLoading, error } = useQuery(
    ['failures', page, rowsPerPage, category, feedbackStatus, searchTerm],
    () => failuresAPI.getList({
      skip: page * rowsPerPage,
      limit: rowsPerPage,
      category: category || undefined,
      feedback_status: feedbackStatus || undefined,
      search: searchTerm || undefined
    }),
    { keepPreviousData: true }
  )

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleCategoryChange = (event) => {
    setCategory(event.target.value)
    setPage(0)
  }

  const handleFeedbackStatusChange = (event) => {
    setFeedbackStatus(event.target.value)
    setPage(0)
  }

  const handleRowClick = (buildId) => {
    navigate(`/failures/${buildId}`)
  }

  const getStatusColor = (feedbackResult) => {
    if (feedbackResult === 'success') return 'success'
    if (feedbackResult === 'failed') return 'error'
    return 'default'
  }

  const getCategoryColor = (category) => {
    const colors = {
      'CODE_ERROR': 'error',
      'TEST_FAILURE': 'warning',
      'INFRA_ERROR': 'info',
      'DEPENDENCY_ERROR': 'secondary',
      'CONFIG_ERROR': 'primary'
    }
    return colors[category] || 'default'
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
        Failed to load failures: {error.message}
      </Alert>
    )
  }

  const failures = data?.data?.failures || []
  const total = data?.data?.total || 0

  // Calculate aging days
  const calculateAgingDays = (timestamp) => {
    if (!timestamp) return 0
    const failureDate = new Date(timestamp)
    const now = new Date()
    const diffTime = Math.abs(now - failureDate)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  // Get aging color
  const getAgingColor = (days) => {
    if (days >= 7) return 'error'
    if (days >= 3) return 'warning'
    return 'success'
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Test Failures
      </Typography>
      <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 3 }}>
        Browse and analyze test failure history
      </Typography>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Search"
              variant="outlined"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by build ID, job name..."
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              select
              label="Error Category"
              value={category}
              onChange={handleCategoryChange}
              variant="outlined"
            >
              {ERROR_CATEGORIES.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              select
              label="Validation Status"
              value={feedbackStatus}
              onChange={handleFeedbackStatusChange}
              variant="outlined"
            >
              {FEEDBACK_STATUSES.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        </Grid>
      </Paper>

      {/* Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Build ID</TableCell>
              <TableCell>Test Name</TableCell>
              <TableCell>Job Name</TableCell>
              <TableCell align="center">Aging</TableCell>
              <TableCell>AI Analysis Status</TableCell>
              <TableCell>Validation Status</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Root Cause / Error</TableCell>
              <TableCell>Date</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {failures.length === 0 ? (
              <TableRow>
                <TableCell colSpan={10} align="center">
                  <Typography color="textSecondary" sx={{ py: 3 }}>
                    No test failures found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              failures.map((failure) => {
                const agingDays = calculateAgingDays(failure.timestamp)
                const hasAiAnalysis = failure.ai_analysis !== null && failure.ai_analysis !== undefined

                return (
                  <TableRow
                    key={failure._id}
                    hover
                    sx={{ cursor: 'pointer' }}
                    onClick={() => handleRowClick(failure._id)}
                  >
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace" fontWeight="600">
                        {failure.build_number || failure._id?.substring(0, 8) || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                        {failure.test_name || 'Unknown Test'}
                      </Typography>
                    </TableCell>
                    <TableCell>{failure.job_name || 'N/A'}</TableCell>
                    <TableCell align="center">
                      <Chip
                        label={`${agingDays}d`}
                        size="small"
                        color={getAgingColor(agingDays)}
                      />
                    </TableCell>
                    <TableCell>
                      {hasAiAnalysis ? (
                        <Chip
                          label={`Analyzed - ${Math.round((failure.ai_analysis.confidence_score || 0) * 100)}%`}
                          size="small"
                          color="success"
                        />
                      ) : (
                        <Chip label="Not Analyzed" size="small" variant="outlined" />
                      )}
                    </TableCell>
                    <TableCell>
                      {failure.feedback_status ? (
                        <FeedbackStatusBadge
                          status={failure.feedback_status}
                          timestamp={failure.feedback_timestamp}
                          validatorName={failure.validator_name}
                          comment={failure.feedback_comment}
                          refinementCount={failure.refinement_count}
                          size="small"
                        />
                      ) : (
                        <FeedbackStatusBadge status="pending" size="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      {hasAiAnalysis && failure.ai_analysis.classification ? (
                        <Chip
                          label={failure.ai_analysis.classification}
                          size="small"
                          color={getCategoryColor(failure.ai_analysis.classification)}
                        />
                      ) : (
                        <Typography variant="caption" color="textSecondary">-</Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                        {hasAiAnalysis
                          ? (failure.ai_analysis.root_cause || failure.ai_analysis.recommendation || 'No analysis')
                          : (failure.error_message || 'No error message')}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {failure.timestamp ? format(new Date(failure.timestamp), 'MMM dd, HH:mm') : 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleRowClick(failure._id)
                        }}
                      >
                        <VisibilityIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                )
              })
            )}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[10, 20, 50]}
          component="div"
          count={total}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
    </Box>
  )
}

export default Failures
