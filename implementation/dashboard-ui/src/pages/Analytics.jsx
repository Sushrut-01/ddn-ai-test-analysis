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
  PieChart,
  Pie,
  Cell,
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

  const { data: trendsData, isLoading: trendsLoading, error: trendsError } = useQuery(
    ['analytics-trends', timeRange],
    () => analyticsAPI.getTrends(timeRange, 'daily'),
    { retry: 1, enabled: false, refetchInterval: 60000 } // Keep disabled - endpoint not implemented yet
  )

  const { data: patternsData, isLoading: patternsLoading, error: patternsError } = useQuery(
    'failure-patterns',
    () => analyticsAPI.getPatterns(),
    { retry: 1, enabled: false, refetchInterval: 60000 } // Keep disabled - endpoint not implemented yet
  )

  const { data: metricsData, isLoading: metricsLoading, error: metricsError } = useQuery(
    ['model-metrics', timeRange],
    () => metricsAPI.getModelMetrics(timeRange),
    { retry: 1, enabled: false, refetchInterval: 60000 } // Keep disabled - endpoint not implemented yet
  )

  // NEW: Feedback Analytics queries (enabled)
  const { data: acceptanceRateData, isLoading: acceptanceLoading } = useQuery(
    ['acceptance-rate-analytics', timeRange],
    () => analyticsAPI.getAcceptanceRate(timeRange),
    { retry: 1, refetchInterval: 60000 }
  )

  const { data: refinementStatsData, isLoading: refinementLoading } = useQuery(
    ['refinement-stats-analytics', timeRange],
    () => analyticsAPI.getRefinementStats(timeRange),
    { retry: 1, refetchInterval: 60000 }
  )

  const handleTimeRangeChange = (event, newRange) => {
    if (newRange) {
      setTimeRange(newRange)
    }
  }

  // Check if feedback analytics are ready (we have these endpoints now!)
  const feedbackAnalyticsReady = !acceptanceLoading && acceptanceRateData && refinementStatsData

  // Legacy analytics endpoints are not yet implemented
  const legacyAnalyticsReady = false

  if (acceptanceLoading || refinementLoading) {
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

      {/* Legacy Analytics Coming Soon Alert */}
      {!legacyAnalyticsReady && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Additional Analytics Features Coming Soon
          </Typography>
          <Typography variant="body2">
            Some advanced analytics features including error category trends, failure patterns, and historical AI model metrics are still being developed.
            Currently available:
          </Typography>
          <ul style={{ marginTop: '8px', marginBottom: 0 }}>
            <li><strong>Feedback Analytics</strong> - AI validation acceptance rates and trends</li>
            <li><strong>Refinement Metrics</strong> - Effectiveness of the refinement process</li>
          </ul>
          <Typography variant="body2" sx={{ mt: 1 }}>
            Coming soon: Error category trends, failure patterns, and historical performance analysis.
          </Typography>
        </Alert>
      )}

      {/* NEW: Feedback Analytics Section (Always shown when data available) */}
      {feedbackAnalyticsReady && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
              Feedback Analytics
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 3 }}>
              Human-in-the-loop validation and refinement metrics
            </Typography>
          </Grid>

          {/* Validation Status Overview - Pie Chart */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Validation Status Distribution
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 2 }}>
                How AI analyses are being validated
              </Typography>
              <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Accepted', value: acceptanceRateData?.summary?.accepted || 0, color: '#4caf50' },
                      { name: 'Rejected', value: acceptanceRateData?.summary?.rejected || 0, color: '#f44336' },
                      { name: 'Refining', value: acceptanceRateData?.summary?.refining || 0, color: '#ff9800' }
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {[
                      { name: 'Accepted', value: acceptanceRateData?.summary?.accepted || 0, color: '#4caf50' },
                      { name: 'Rejected', value: acceptanceRateData?.summary?.rejected || 0, color: '#f44336' },
                      { name: 'Refining', value: acceptanceRateData?.summary?.refining || 0, color: '#ff9800' }
                    ].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>

              {/* Summary Stats */}
              <Grid container spacing={2} sx={{ mt: 2 }}>
                <Grid item xs={4}>
                  <Typography variant="body2" color="textSecondary">
                    Total Feedback
                  </Typography>
                  <Typography variant="h6" fontWeight="600">
                    {acceptanceRateData?.summary?.total_feedback || 0}
                  </Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" color="textSecondary">
                    Acceptance Rate
                  </Typography>
                  <Typography variant="h6" fontWeight="600" color="success.main">
                    {acceptanceRateData?.summary?.acceptance_rate?.toFixed(1) || 0}%
                  </Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" color="textSecondary">
                    Rejection Rate
                  </Typography>
                  <Typography variant="h6" fontWeight="600" color="error.main">
                    {acceptanceRateData?.summary?.rejection_rate?.toFixed(1) || 0}%
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Acceptance Rate Trend Over Time */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Acceptance Rate Trend
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 2 }}>
                Daily acceptance rate over selected time period
              </Typography>
              <ResponsiveContainer width="100%" height={350}>
                <LineChart
                  data={acceptanceRateData?.trend || []}
                  margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(value) => {
                      const date = new Date(value)
                      return `${date.getMonth() + 1}/${date.getDate()}`
                    }}
                  />
                  <YAxis domain={[0, 100]} />
                  <Tooltip
                    labelFormatter={(value) => format(new Date(value), 'MMM dd, yyyy')}
                    formatter={(value) => [`${value}%`, 'Acceptance Rate']}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="acceptance_rate"
                    stroke="#4caf50"
                    strokeWidth={3}
                    dot={{ fill: '#4caf50', r: 4 }}
                    activeDot={{ r: 6 }}
                    name="Acceptance Rate (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          {/* Refinement Effectiveness */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Refinement Effectiveness
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 2 }}>
                How well refinements improve AI analysis quality
              </Typography>
              <Grid container spacing={3} sx={{ mt: 1 }}>
                <Grid item xs={6}>
                  <Box textAlign="center" sx={{ p: 2, bgcolor: '#e3f2fd', borderRadius: 2 }}>
                    <Typography variant="h3" fontWeight="bold" color="primary.main">
                      {refinementStatsData?.summary?.total_refined || 0}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                      Total Refined
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center" sx={{ p: 2, bgcolor: '#f3e5f5', borderRadius: 2 }}>
                    <Typography variant="h3" fontWeight="bold" color="secondary.main">
                      {refinementStatsData?.summary?.avg_refinement_count?.toFixed(1) || 0}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                      Avg Iterations
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box textAlign="center" sx={{ p: 3, bgcolor: '#e8f5e9', borderRadius: 2 }}>
                    <Typography variant="h2" fontWeight="bold" color="success.main">
                      {refinementStatsData?.summary?.effectiveness_rate?.toFixed(1) || 0}%
                    </Typography>
                    <Typography variant="body1" color="textSecondary" sx={{ mt: 1 }}>
                      Effectiveness Rate
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Percentage of refined analyses that were eventually accepted
                    </Typography>
                  </Box>
                </Grid>
                {refinementStatsData?.summary?.avg_confidence_improvement && (
                  <Grid item xs={12}>
                    <Box textAlign="center" sx={{ p: 2, bgcolor: '#fff3e0', borderRadius: 2 }}>
                      <Typography variant="h4" fontWeight="bold" color="warning.main">
                        +{refinementStatsData.summary.avg_confidence_improvement.toFixed(1)}%
                      </Typography>
                      <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                        Avg Confidence Improvement
                      </Typography>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </Paper>
          </Grid>

          {/* Model Performance Summary */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Model Performance Summary
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 2 }}>
                Overall AI analysis quality metrics
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Metric</strong></TableCell>
                      <TableCell align="right"><strong>Value</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>Total Analyses</TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="600">
                          {acceptanceRateData?.summary?.total_feedback || 0}
                        </Typography>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Accepted</TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="600" color="success.main">
                          {acceptanceRateData?.summary?.accepted || 0} ({acceptanceRateData?.summary?.acceptance_rate?.toFixed(1) || 0}%)
                        </Typography>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Rejected</TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="600" color="error.main">
                          {acceptanceRateData?.summary?.rejected || 0} ({acceptanceRateData?.summary?.rejection_rate?.toFixed(1) || 0}%)
                        </Typography>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Required Refinement</TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="600" color="warning.main">
                          {refinementStatsData?.summary?.total_refined || 0}
                        </Typography>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Refinement Success Rate</TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="600" color="success.main">
                          {refinementStatsData?.summary?.effectiveness_rate?.toFixed(1) || 0}%
                        </Typography>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Legacy Analytics Section (Coming Soon) */}
      {legacyAnalyticsReady && (
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
      )}
    </Box>
  )
}

export default Analytics
