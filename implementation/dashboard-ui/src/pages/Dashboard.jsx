import React from 'react'
import { useQuery } from 'react-query'
import { useNavigate } from 'react-router-dom'
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
  List,
  ListItem,
  ListItemText,
  IconButton
} from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Speed as SpeedIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { analyticsAPI, statusAPI } from '../services/api'
import { format } from 'date-fns'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8']

function StatCard({ title, value, icon, color = 'primary', subtitle }) {
  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
            {subtitle && (
              <Typography color="textSecondary" variant="body2" sx={{ mt: 1 }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              backgroundColor: `${color}.light`,
              borderRadius: '50%',
              p: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}

function Dashboard() {
  const navigate = useNavigate()

  const { data: summaryData, isLoading: summaryLoading, error: summaryError } = useQuery(
    ['analytics-summary', '7d'],
    () => analyticsAPI.getSummary('7d'),
    { refetchInterval: 30000 }
  )

  const { data: liveStatus } = useQuery(
    'live-status',
    () => statusAPI.getLiveStatus(),
    { refetchInterval: 10000 }
  )

  if (summaryLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (summaryError) {
    return (
      <Alert severity="error">
        Failed to load dashboard data: {summaryError.message}
      </Alert>
    )
  }

  const { overview, categories, trends, recent_failures } = summaryData?.data || {}

  // Prepare trend data for chart
  const trendChartData = trends?.map(t => ({
    date: format(new Date(t.date), 'MMM dd'),
    failures: t.failure_count,
    successes: t.success_count
  })) || []

  // Prepare category data for pie chart
  const categoryChartData = categories?.map(c => ({
    name: c.error_category,
    value: c.count
  })) || []

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard Overview
      </Typography>
      <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 3 }}>
        Last 7 days performance metrics
      </Typography>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Failures"
            value={overview?.total_failures || 0}
            icon={<ErrorIcon fontSize="large" />}
            color="error"
            subtitle={`${overview?.unique_builds || 0} unique builds`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Success Rate"
            value={`${overview?.success_rate || 0}%`}
            icon={<CheckCircleIcon fontSize="large" />}
            color="success"
            subtitle="Fix effectiveness"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Confidence"
            value={`${overview?.avg_confidence || 0}%`}
            icon={<SpeedIcon fontSize="large" />}
            color="primary"
            subtitle="AI confidence score"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Resolution"
            value={`${Math.round((overview?.avg_resolution_time_seconds || 0) / 60)}m`}
            icon={<TrendingUpIcon fontSize="large" />}
            color="warning"
            subtitle="Time to fix"
          />
        </Grid>
      </Grid>

      {/* Live Status Banner */}
      {liveStatus?.data && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <strong>Live Status (Last 24h):</strong> {liveStatus.data.activity_24h?.failures_24h || 0} failures,{' '}
          {liveStatus.data.activity_24h?.successes_24h || 0} fixes applied
          {liveStatus.data.latest_failure && (
            <> • Latest: {liveStatus.data.latest_failure.job_name} ({liveStatus.data.latest_failure.error_category})</>
          )}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Failure Trend Chart */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Failure Trends (Last 7 Days)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trendChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="failures" stroke="#f44336" name="Failures" strokeWidth={2} />
                <Line type="monotone" dataKey="successes" stroke="#4caf50" name="Successful Fixes" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Error Category Distribution */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Error Categories
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Category Breakdown Bar Chart */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Error Category Breakdown
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={categories}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="error_category" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#1976d2" name="Count" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Recent Failures */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Failures
            </Typography>
            <List>
              {recent_failures?.slice(0, 5).map((failure) => (
                <ListItem
                  key={failure.id}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      onClick={() => navigate(`/failures/${failure.build_id}`)}
                    >
                      <VisibilityIcon />
                    </IconButton>
                  }
                  sx={{ borderBottom: '1px solid #eee' }}
                >
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body1">{failure.job_name || failure.build_id}</Typography>
                        <Chip
                          label={failure.error_category}
                          size="small"
                          color={failure.feedback_result === 'success' ? 'success' : 'default'}
                        />
                      </Box>
                    }
                    secondary={
                      <>
                        {failure.root_cause?.substring(0, 80)}...
                        <br />
                        <Typography variant="caption" color="textSecondary">
                          {format(new Date(failure.created_at), 'MMM dd, HH:mm')} • Confidence: {Math.round(failure.confidence_score * 100)}%
                          {failure.consecutive_failures > 1 && ` • ${failure.consecutive_failures} failures`}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
