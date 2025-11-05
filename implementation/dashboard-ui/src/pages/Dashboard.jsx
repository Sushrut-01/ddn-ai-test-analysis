import React from 'react'
import { useQuery } from 'react-query'
import { useNavigate } from 'react-router-dom'
import ServiceControl from '../components/ServiceControl'
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Divider,
  alpha
} from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Cloud as CloudIcon,
  Storage as StorageIcon,
  SmartToy as SmartToyIcon,
  Timeline as TimelineIcon,
  BubbleChart as BubbleChartIcon,
  Visibility as VisibilityIcon,
  Warning as WarningIcon
} from '@mui/icons-material'
import { monitoringAPI, failuresAPI, analyticsAPI } from '../services/api'
import SystemStatus from '../components/SystemStatus'
import { format, formatDistanceToNow } from 'date-fns'
import {
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'

// Beautiful gradient card with animation
function MetricCard({ title, value, subtitle, icon: Icon, gradient, trend }) {
  return (
    <Card
      sx={{
        background: `linear-gradient(135deg, ${gradient[0]} 0%, ${gradient[1]} 100%)`,
        color: 'white',
        position: 'relative',
        overflow: 'hidden',
        transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
        '&:hover': {
          transform: 'translateY(-8px)',
          boxShadow: 8
        }
      }}
    >
      <CardContent sx={{ position: 'relative', zIndex: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box
            sx={{
              backgroundColor: alpha('#fff', 0.2),
              borderRadius: 2,
              p: 1.5,
              display: 'flex'
            }}
          >
            <Icon sx={{ fontSize: 32 }} />
          </Box>
          {trend && (
            <Chip
              label={trend}
              size="small"
              sx={{
                backgroundColor: alpha('#fff', 0.2),
                color: 'white',
                fontWeight: 600
              }}
            />
          )}
        </Box>

        <Typography variant="h3" fontWeight="bold" sx={{ mb: 1 }}>
          {value}
        </Typography>

        <Typography variant="body2" sx={{ opacity: 0.9, fontWeight: 500 }}>
          {title}
        </Typography>

        {subtitle && (
          <Typography variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
            {subtitle}
          </Typography>
        )}
      </CardContent>

      {/* Decorative background pattern */}
      <Box
        sx={{
          position: 'absolute',
          top: -50,
          right: -50,
          width: 200,
          height: 200,
          borderRadius: '50%',
          backgroundColor: alpha('#fff', 0.1),
          zIndex: 0
        }}
      />
    </Card>
  )
}

// Component health indicator
function ComponentHealth({ name, status, icon: Icon, metrics }) {
  const isHealthy = status === 'healthy' || status === 'connected'
  const statusColor = isHealthy ? '#4caf50' : '#f44336'

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2.5,
        border: 2,
        borderColor: alpha(statusColor, 0.2),
        borderRadius: 2,
        backgroundColor: alpha(statusColor, 0.05),
        transition: 'all 0.3s ease',
        '&:hover': {
          borderColor: statusColor,
          transform: 'scale(1.02)'
        }
      }}
    >
      <Box display="flex" alignItems="center" gap={1.5} mb={2}>
        <Box
          sx={{
            p: 1,
            borderRadius: 1.5,
            backgroundColor: alpha(statusColor, 0.1),
            display: 'flex'
          }}
        >
          <Icon sx={{ color: statusColor, fontSize: 28 }} />
        </Box>
        <Box flex={1}>
          <Typography variant="h6" fontWeight="600">
            {name}
          </Typography>
          <Chip
            label={isHealthy ? 'Healthy' : 'Offline'}
            size="small"
            sx={{
              backgroundColor: statusColor,
              color: 'white',
              fontWeight: 600,
              fontSize: '0.7rem',
              height: 20
            }}
          />
        </Box>
      </Box>

      {metrics && (
        <Box sx={{ mt: 2 }}>
          {Object.entries(metrics).map(([key, value]) => (
            <Box key={key} display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
              <Typography variant="caption" color="text.secondary">
                {key}
              </Typography>
              <Typography variant="caption" fontWeight="600">
                {value}
              </Typography>
            </Box>
          ))}
        </Box>
      )}
    </Paper>
  )
}

function Dashboard() {
  const navigate = useNavigate()

  // Fetch system status
  const { data: systemStatus, isLoading } = useQuery(
    'system-status',
    () => monitoringAPI.getSystemStatus(),
    {
      refetchInterval: 10000,
      retry: 2
    }
  )

  // Fetch stats
  const { data: stats } = useQuery(
    'stats',
    () => monitoringAPI.getStats(),
    {
      refetchInterval: 15000,
      retry: 1,
      onError: (error) => console.warn('Stats API error:', error)
    }
  )

  // Fetch recent failures
  const { data: recentFailuresData, isLoading: failuresLoading } = useQuery(
    'recent-failures',
    () => failuresAPI.getList({ limit: 10 }),
    {
      refetchInterval: 20000,
      retry: 2,
      onError: (error) => console.warn('Failures API error:', error)
    }
  )

  // Fetch acceptance rate analytics
  const { data: acceptanceRateData } = useQuery(
    'acceptance-rate',
    () => analyticsAPI.getAcceptanceRate('30d'),
    {
      refetchInterval: 30000,
      retry: 1,
      onError: (error) => console.warn('Acceptance rate API error:', error)
    }
  )

  // Fetch refinement stats
  const { data: refinementStatsData } = useQuery(
    'refinement-stats',
    () => analyticsAPI.getRefinementStats('30d'),
    {
      refetchInterval: 30000,
      retry: 1,
      onError: (error) => console.warn('Refinement stats API error:', error)
    }
  )

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <Box textAlign="center">
          <CircularProgress size={60} thickness={4} />
          <Typography variant="h6" sx={{ mt: 3 }} color="text.secondary">
            Loading monitoring data...
          </Typography>
        </Box>
      </Box>
    )
  }

  const components = systemStatus?.components || {}
  const recentFailures = recentFailuresData?.data?.failures || []

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
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: 3,
          p: 4,
          mb: 4,
          color: 'white',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <Box position="relative" zIndex={1}>
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            DDN AI Test Analysis
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.9, mb: 2 }}>
            Intelligent Test Failure Analysis & Monitoring
          </Typography>
          <Box display="flex" gap={2} flexWrap="wrap">
            <Chip
              label="Enhanced Monitoring"
              sx={{
                backgroundColor: alpha('#fff', 0.2),
                color: 'white',
                fontWeight: 600
              }}
              icon={<TimelineIcon sx={{ color: 'white !important' }} />}
            />
            <Chip
              label="AI-Powered Analysis"
              sx={{
                backgroundColor: alpha('#fff', 0.2),
                color: 'white',
                fontWeight: 600
              }}
              icon={<SmartToyIcon sx={{ color: 'white !important' }} />}
            />
            <Chip
              label="Real-time Status"
              sx={{
                backgroundColor: alpha('#fff', 0.2),
                color: 'white',
                fontWeight: 600
              }}
              icon={<BubbleChartIcon sx={{ color: 'white !important' }} />}
            />
          </Box>
        </Box>

        {/* Decorative elements */}
        <Box
          sx={{
            position: 'absolute',
            top: -100,
            right: -100,
            width: 300,
            height: 300,
            borderRadius: '50%',
            backgroundColor: alpha('#fff', 0.1)
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            bottom: -50,
            left: -50,
            width: 200,
            height: 200,
            borderRadius: '50%',
            backgroundColor: alpha('#fff', 0.08)
          }}
        />
      </Box>

      {/* Service Control Panel */}
      <Paper
        elevation={3}
        sx={{
          p: 3,
          mb: 4,
          borderRadius: 2,
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
        }}
      >
        <ServiceControl />
      </Paper>

      {/* System Health Overview */}
      <Typography variant="h5" fontWeight="bold" gutterBottom sx={{ mb: 3 }}>
        System Health Overview
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <ComponentHealth
            name="MongoDB"
            status={components.mongodb?.status}
            icon={StorageIcon}
            metrics={
              components.mongodb?.connected
                ? { 'Test Failures': components.mongodb.total_failures || 0 }
                : null
            }
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <ComponentHealth
            name="PostgreSQL"
            status={components.postgresql?.status}
            icon={StorageIcon}
            metrics={
              components.postgresql?.connected
                ? { 'AI Analyses': components.postgresql.total_analyses || 0 }
                : null
            }
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <ComponentHealth
            name="Pinecone"
            status={components.pinecone?.status}
            icon={CloudIcon}
            metrics={
              components.pinecone?.connected
                ? { 'Vectors': components.pinecone.total_vectors || 0 }
                : null
            }
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <ComponentHealth
            name="AI Service"
            status={components.ai_service?.status}
            icon={SmartToyIcon}
            metrics={
              components.ai_service?.connected
                ? { 'Status': 'Active' }
                : null
            }
          />
        </Grid>
      </Grid>

      <Divider sx={{ my: 4 }} />

      {/* Metrics Section */}
      <Typography variant="h5" fontWeight="bold" gutterBottom sx={{ mb: 3 }}>
        Performance Metrics
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Test Failures"
            value={stats?.total_failures || "0"}
            subtitle="Across all builds"
            icon={ErrorIcon}
            gradient={['#f093fb', '#f5576c']}
            trend="+0%"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="AI Analyses"
            value={stats?.total_analyzed || "0"}
            subtitle="Completed analyses"
            icon={SmartToyIcon}
            gradient={['#4facfe', '#00f2fe']}
            trend="Active"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Confidence"
            value={`${Math.round((stats?.avg_confidence || 0) * 100)}%`}
            subtitle="AI confidence score"
            icon={SpeedIcon}
            gradient={['#43e97b', '#38f9d7']}
            trend="High"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="System Status"
            value={systemStatus?.overall_status === 'healthy' ? "Healthy" : "Degraded"}
            subtitle="Overall system health"
            icon={CheckCircleIcon}
            gradient={['#fa709a', '#fee140']}
            trend={systemStatus?.overall_status === 'healthy' ? "✓" : "!"}
          />
        </Grid>
      </Grid>

      <Divider sx={{ my: 4 }} />

      {/* AI Validation Analytics Section */}
      <Typography variant="h5" fontWeight="bold" gutterBottom sx={{ mb: 3 }}>
        AI Validation Analytics
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Validation Status Distribution - Pie Chart */}
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              height: '100%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white'
            }}
          >
            <Typography variant="h6" fontWeight="600" gutterBottom>
              Validation Status Distribution
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9, mb: 2 }}>
              Last 30 days
            </Typography>

            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'Accepted', value: acceptanceRateData?.summary?.accepted || 0, color: '#4caf50' },
                    { name: 'Rejected', value: acceptanceRateData?.summary?.rejected || 0, color: '#f44336' },
                    { name: 'Refining', value: acceptanceRateData?.summary?.refining || 0, color: '#ff9800' }
                  ]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
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
                <RechartsTooltip
                  contentStyle={{ backgroundColor: 'rgba(33, 33, 33, 0.95)', border: 'none', borderRadius: 8 }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>

            {/* Summary Stats */}
            <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid rgba(255,255,255,0.2)' }}>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Total Feedback
                  </Typography>
                  <Typography variant="h6" fontWeight="600">
                    {acceptanceRateData?.summary?.total_feedback || 0}
                  </Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Acceptance Rate
                  </Typography>
                  <Typography variant="h6" fontWeight="600">
                    {acceptanceRateData?.summary?.acceptance_rate?.toFixed(1) || 0}%
                  </Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Rejection Rate
                  </Typography>
                  <Typography variant="h6" fontWeight="600">
                    {acceptanceRateData?.summary?.rejection_rate?.toFixed(1) || 0}%
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        </Grid>

        {/* Acceptance Rate Trend - Line Chart */}
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              height: '100%',
              background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
              color: 'white'
            }}
          >
            <Typography variant="h6" fontWeight="600" gutterBottom>
              Acceptance Rate Trend
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9, mb: 2 }}>
              Daily acceptance rate over time
            </Typography>

            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={acceptanceRateData?.trend || []}
                margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.2)" />
                <XAxis
                  dataKey="date"
                  stroke="rgba(255,255,255,0.8)"
                  tick={{ fill: 'white' }}
                  tickFormatter={(value) => {
                    const date = new Date(value)
                    return `${date.getMonth() + 1}/${date.getDate()}`
                  }}
                />
                <YAxis
                  stroke="rgba(255,255,255,0.8)"
                  tick={{ fill: 'white' }}
                  domain={[0, 100]}
                />
                <RechartsTooltip
                  contentStyle={{ backgroundColor: 'rgba(33, 33, 33, 0.95)', border: 'none', borderRadius: 8 }}
                  labelFormatter={(value) => format(new Date(value), 'MMM dd, yyyy')}
                  formatter={(value) => [`${value}%`, 'Acceptance Rate']}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="acceptance_rate"
                  stroke="#ffffff"
                  strokeWidth={3}
                  dot={{ fill: '#ffffff', r: 5 }}
                  activeDot={{ r: 8 }}
                  name="Acceptance Rate"
                />
              </LineChart>
            </ResponsiveContainer>

            {/* Refinement Stats */}
            <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid rgba(255,255,255,0.2)' }}>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Total Refined
                  </Typography>
                  <Typography variant="h6" fontWeight="600">
                    {refinementStatsData?.summary?.total_refined || 0}
                  </Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Avg Refinements
                  </Typography>
                  <Typography variant="h6" fontWeight="600">
                    {refinementStatsData?.summary?.avg_refinement_count?.toFixed(1) || 0}
                  </Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Effectiveness
                  </Typography>
                  <Typography variant="h6" fontWeight="600">
                    {refinementStatsData?.summary?.effectiveness_rate?.toFixed(1) || 0}%
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Divider sx={{ my: 4 }} />

      {/* Recent Test Failures with AI Analysis */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight="bold">
          Recent Test Failures with AI Analysis
        </Typography>
        <Button
          variant="outlined"
          onClick={() => navigate('/failures')}
          endIcon={<TrendingUpIcon />}
        >
          View All Failures
        </Button>
      </Box>

      <Paper>
        {failuresLoading ? (
          <Box display="flex" justifyContent="center" alignItems="center" p={4}>
            <CircularProgress />
          </Box>
        ) : recentFailures.length === 0 ? (
          <Alert severity="info" sx={{ m: 2 }}>
            No test failures found. This could mean:
            <ul style={{ marginTop: 8, marginBottom: 0 }}>
              <li>All tests are passing (Great!)</li>
              <li>MongoDB connection needs to be established</li>
              <li>Jenkins hasn't pushed any test results yet</li>
            </ul>
          </Alert>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Build ID</TableCell>
                  <TableCell>Test Name</TableCell>
                  <TableCell>Job Name</TableCell>
                  <TableCell align="center">Aging Days</TableCell>
                  <TableCell>AI Analysis Status</TableCell>
                  <TableCell>AI Recommendation</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentFailures.map((failure) => {
                  const agingDays = calculateAgingDays(failure.timestamp)
                  const hasAiAnalysis = failure.ai_analysis !== null

                  return (
                    <TableRow
                      key={failure._id}
                      hover
                      sx={{ '&:hover': { backgroundColor: alpha('#667eea', 0.05) } }}
                    >
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace" fontWeight="600">
                          {failure.build_number || failure._id?.substring(0, 8) || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ maxWidth: 200 }} noWrap>
                          {failure.test_name || 'Unknown Test'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {failure.job_name || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={`${agingDays} days`}
                          size="small"
                          color={getAgingColor(agingDays)}
                          icon={agingDays >= 7 ? <WarningIcon /> : null}
                        />
                      </TableCell>
                      <TableCell>
                        {hasAiAnalysis ? (
                          <Chip
                            label={`Analyzed - ${Math.round((failure.ai_analysis?.confidence_score || 0) * 100)}%`}
                            size="small"
                            color="success"
                            icon={<SmartToyIcon />}
                          />
                        ) : (
                          <Chip
                            label="Not Analyzed"
                            size="small"
                            color="default"
                            variant="outlined"
                          />
                        )}
                      </TableCell>
                      <TableCell>
                        {hasAiAnalysis ? (
                          <Box>
                            <Typography variant="caption" display="block" color="text.secondary">
                              Category: {failure.ai_analysis?.classification || 'N/A'}
                            </Typography>
                            <Typography variant="body2" sx={{ maxWidth: 300 }} noWrap>
                              {failure.ai_analysis?.recommendation || failure.ai_analysis?.root_cause || 'No recommendation'}
                            </Typography>
                          </Box>
                        ) : (
                          <Typography variant="caption" color="text.secondary">
                            Click "Analyze" to get AI recommendations
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">
                          {failure.timestamp ? formatDistanceToNow(new Date(failure.timestamp), { addSuffix: true }) : 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Button
                          size="small"
                          variant={hasAiAnalysis ? "outlined" : "contained"}
                          color={hasAiAnalysis ? "primary" : "success"}
                          startIcon={hasAiAnalysis ? <VisibilityIcon /> : <SmartToyIcon />}
                          onClick={() => navigate(`/failures/${failure._id}`)}
                        >
                          {hasAiAnalysis ? 'View' : 'Analyze'}
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Info Card */}
      <Paper
        sx={{
          p: 3,
          mt: 4,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          borderRadius: 2
        }}
      >
        <Box display="flex" alignItems="center" gap={2}>
          <MemoryIcon sx={{ fontSize: 40 }} />
          <Box>
            <Typography variant="h6" fontWeight="600">
              Enhanced Monitoring Active
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              Real-time system health monitoring is enabled on port 5006.
              All components are being tracked and analyzed continuously.
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Box>
  )
}

export default Dashboard
