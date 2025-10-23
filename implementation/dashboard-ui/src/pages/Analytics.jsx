import React, { useState } from 'react'
import { useQuery } from 'react-query'
import {
  Box,
  Paper,
  Typography,
  Grid,
  ToggleButtonGroup,
  ToggleButton,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts'
import { analyticsAPI, metricsAPI } from '../services/api'
import { format } from 'date-fns'

function Analytics() {
  const [timeRange, setTimeRange] = useState('30d')

  const { data: trendsData, isLoading: trendsLoading } = useQuery(
    ['analytics-trends', timeRange],
    () => analyticsAPI.getTrends(timeRange, 'daily')
  )

  const { data: patternsData, isLoading: patternsLoading } = useQuery(
    'failure-patterns',
    () => analyticsAPI.getPatterns()
  )

  const { data: metricsData, isLoading: metricsLoading } = useQuery(
    ['model-metrics', timeRange],
    () => metricsAPI.getModelMetrics(timeRange)
  )

  const handleTimeRangeChange = (event, newRange) => {
    if (newRange) {
      setTimeRange(newRange)
    }
  }

  if (trendsLoading || patternsLoading || metricsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  const trends = trendsData?.data?.trends || []
  const patterns = patternsData?.data?.patterns || []
  const metrics = metricsData?.data?.metrics || []

  // Prepare data for category trend chart
  const categoryTrendData = trends.map(t => ({
    date: format(new Date(t.period), 'MMM dd'),
    'Code Errors': t.code_errors,
    'Test Failures': t.test_failures,
    'Infra Errors': t.infra_errors,
    'Dep Errors': t.dep_errors,
    'Config Errors': t.config_errors
  }))

  // Prepare data for AI metrics
  const aiMetricsData = metrics.map(m => ({
    date: format(new Date(m.date), 'MMM dd'),
    accuracy: (m.accuracy_rate * 100).toFixed(1),
    avgConfidence: (m.avg_confidence_score * 100).toFixed(1),
    totalPredictions: m.total_predictions
  }))

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Advanced Analytics
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Detailed failure trends and AI model performance
          </Typography>
        </Box>
        <ToggleButtonGroup
          value={timeRange}
          exclusive
          onChange={handleTimeRangeChange}
          size="small"
        >
          <ToggleButton value="7d">7 Days</ToggleButton>
          <ToggleButton value="30d">30 Days</ToggleButton>
          <ToggleButton value="90d">90 Days</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <Grid container spacing={3}>
        {/* Error Category Trends */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Error Category Trends
            </Typography>
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart data={categoryTrendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="Code Errors" stackId="1" stroke="#f44336" fill="#f44336" />
                <Area type="monotone" dataKey="Test Failures" stackId="1" stroke="#ff9800" fill="#ff9800" />
                <Area type="monotone" dataKey="Infra Errors" stackId="1" stroke="#2196f3" fill="#2196f3" />
                <Area type="monotone" dataKey="Dep Errors" stackId="1" stroke="#9c27b0" fill="#9c27b0" />
                <Area type="monotone" dataKey="Config Errors" stackId="1" stroke="#4caf50" fill="#4caf50" />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* AI Model Performance */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              AI Model Accuracy Over Time
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={aiMetricsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="accuracy" stroke="#4caf50" strokeWidth={2} name="Accuracy %" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* AI Confidence Scores */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Average Confidence Score
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={aiMetricsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="avgConfidence" stroke="#2196f3" strokeWidth={2} name="Avg Confidence %" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Daily Build Volume */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Daily Failure Volume
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={(item) => format(new Date(item.period), 'MMM dd')} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="total_failures" fill="#1976d2" name="Total Failures" />
                <Bar dataKey="unique_builds" fill="#4caf50" name="Unique Builds" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Failure Patterns */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Identified Failure Patterns
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Most common failure patterns identified by AI
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Pattern Type</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell align="center">Occurrences</TableCell>
                    <TableCell align="center">Success Rate</TableCell>
                    <TableCell>Last Seen</TableCell>
                    <TableCell>Suggested Fix</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {patterns.map((pattern, idx) => (
                    <TableRow key={idx}>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {pattern.pattern_type}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                          {pattern.pattern_description}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Typography variant="body2" fontWeight="bold">
                          {pattern.occurrence_count}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Typography
                          variant="body2"
                          color={pattern.success_rate > 0.7 ? 'success.main' : 'warning.main'}
                        >
                          {(pattern.success_rate * 100).toFixed(1)}%
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {pattern.last_seen ? format(new Date(pattern.last_seen), 'MMM dd, yyyy') : 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap sx={{ maxWidth: 250 }}>
                          {pattern.suggested_fix}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Analytics
