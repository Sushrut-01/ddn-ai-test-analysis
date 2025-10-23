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

const ERROR_CATEGORIES = [
  { value: '', label: 'All Categories' },
  { value: 'CODE_ERROR', label: 'Code Error' },
  { value: 'TEST_FAILURE', label: 'Test Failure' },
  { value: 'INFRA_ERROR', label: 'Infrastructure Error' },
  { value: 'DEPENDENCY_ERROR', label: 'Dependency Error' },
  { value: 'CONFIG_ERROR', label: 'Config Error' }
]

function Failures() {
  const navigate = useNavigate()
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(20)
  const [category, setCategory] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  const { data, isLoading, error } = useQuery(
    ['failures', page + 1, rowsPerPage, category],
    () => failuresAPI.getList({
      page: page + 1,
      limit: rowsPerPage,
      category: category || undefined
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
  const pagination = data?.data?.pagination || { total: 0, pages: 0 }

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
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search"
              variant="outlined"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by build ID, job name..."
            />
          </Grid>
          <Grid item xs={12} md={6}>
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
        </Grid>
      </Paper>

      {/* Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Build ID</TableCell>
              <TableCell>Job Name</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Root Cause</TableCell>
              <TableCell align="center">Confidence</TableCell>
              <TableCell align="center">Failures</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Date</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {failures.map((failure) => (
              <TableRow
                key={failure.id}
                hover
                sx={{ cursor: 'pointer' }}
                onClick={() => handleRowClick(failure.build_id)}
              >
                <TableCell>
                  <Typography variant="body2" fontFamily="monospace">
                    {failure.build_id}
                  </Typography>
                </TableCell>
                <TableCell>{failure.job_name || '-'}</TableCell>
                <TableCell>
                  <Chip
                    label={failure.error_category}
                    size="small"
                    color={getCategoryColor(failure.error_category)}
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                    {failure.root_cause}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Chip
                    label={`${Math.round(failure.confidence_score * 100)}%`}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell align="center">
                  <Chip
                    label={failure.consecutive_failures}
                    size="small"
                    color={failure.consecutive_failures >= 5 ? 'error' : 'default'}
                  />
                </TableCell>
                <TableCell>
                  {failure.feedback_result ? (
                    <Chip
                      label={failure.feedback_result}
                      size="small"
                      color={getStatusColor(failure.feedback_result)}
                    />
                  ) : (
                    <Chip label="Pending" size="small" variant="outlined" />
                  )}
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {format(new Date(failure.created_at), 'MMM dd, HH:mm')}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleRowClick(failure.build_id)
                    }}
                  >
                    <VisibilityIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[10, 20, 50]}
          component="div"
          count={pagination.total}
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
