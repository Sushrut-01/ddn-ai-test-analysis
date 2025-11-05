import React from 'react'
import { useQuery } from 'react-query'
import {
  Paper,
  Typography,
  Box,
  Grid,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material'
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon
} from '@mui/icons-material'
import { monitoringAPI } from '../services/api'

function ComponentStatus({ name, data }) {
  const isHealthy = data?.status === 'healthy' || data?.connected === true
  const hasError = data?.status === 'error' || data?.connected === false

  return (
    <Box
      sx={{
        p: 2,
        border: '1px solid',
        borderColor: isHealthy ? 'success.light' : hasError ? 'error.light' : 'warning.light',
        borderRadius: 1,
        bgcolor: isHealthy ? 'success.lighter' : hasError ? 'error.lighter' : 'warning.lighter'
      }}
    >
      <Box display="flex" alignItems="center" gap={1} mb={1}>
        {isHealthy ? (
          <CheckCircleIcon color="success" />
        ) : hasError ? (
          <ErrorIcon color="error" />
        ) : (
          <WarningIcon color="warning" />
        )}
        <Typography variant="h6">{name}</Typography>
        <Chip
          label={isHealthy ? 'Healthy' : hasError ? 'Error' : 'Warning'}
          color={isHealthy ? 'success' : hasError ? 'error' : 'warning'}
          size="small"
        />
      </Box>

      <Box sx={{ pl: 4 }}>
        {data?.total_failures !== undefined && (
          <Typography variant="body2">Failures: {data.total_failures}</Typography>
        )}
        {data?.total_analyses !== undefined && (
          <Typography variant="body2">Analyses: {data.total_analyses}</Typography>
        )}
        {data?.total_vectors !== undefined && (
          <Typography variant="body2">Vectors: {data.total_vectors}</Typography>
        )}
        {data?.error && (
          <Typography variant="body2" color="error" sx={{ mt: 1, fontSize: '0.75rem' }}>
            Error: {data.error.substring(0, 100)}...
          </Typography>
        )}
      </Box>
    </Box>
  )
}

function SystemStatus() {
  const { data, isLoading, error } = useQuery(
    'system-status',
    () => monitoringAPI.getSystemStatus(),
    {
      refetchInterval: 10000, // Refresh every 10 seconds
      retry: 2
    }
  )

  if (isLoading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      </Paper>
    )
  }

  if (error) {
    return (
      <Paper sx={{ p: 3 }}>
        <Alert severity="error">
          Failed to load system status: {error.message}
        </Alert>
      </Paper>
    )
  }

  const components = data?.components || {}
  const overallStatus = data?.overall_status || 'unknown'

  return (
    <Paper sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">System Health Status</Typography>
        <Chip
          label={overallStatus.toUpperCase()}
          color={overallStatus === 'healthy' ? 'success' : 'warning'}
          icon={overallStatus === 'healthy' ? <CheckCircleIcon /> : <WarningIcon />}
        />
      </Box>

      <Grid container spacing={2}>
        {components.mongodb && (
          <Grid item xs={12} sm={6} md={3}>
            <ComponentStatus name="MongoDB" data={components.mongodb} />
          </Grid>
        )}
        {components.postgresql && (
          <Grid item xs={12} sm={6} md={3}>
            <ComponentStatus name="PostgreSQL" data={components.postgresql} />
          </Grid>
        )}
        {components.pinecone && (
          <Grid item xs={12} sm={6} md={3}>
            <ComponentStatus name="Pinecone" data={components.pinecone} />
          </Grid>
        )}
        {components.ai_service && (
          <Grid item xs={12} sm={6} md={3}>
            <ComponentStatus name="AI Service" data={components.ai_service} />
          </Grid>
        )}
      </Grid>

      <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
        Last updated: {data?.timestamp ? new Date(data.timestamp).toLocaleTimeString() : 'N/A'}
      </Typography>
    </Paper>
  )
}

export default SystemStatus
