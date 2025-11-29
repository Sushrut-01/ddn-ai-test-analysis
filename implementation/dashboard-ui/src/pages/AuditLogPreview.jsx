import React, { useState, useEffect, useCallback } from 'react'
import { useLocation } from 'react-router-dom'
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  Avatar,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  TableContainer,
  TablePagination,
  TextField,
  MenuItem,
  InputAdornment,
  Tooltip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  List,
  ListItem,
  ListItemText,
  Skeleton,
  CircularProgress
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import HistoryIcon from '@mui/icons-material/History'
import SearchIcon from '@mui/icons-material/Search'
import FilterListIcon from '@mui/icons-material/FilterList'
import DownloadIcon from '@mui/icons-material/Download'
import VisibilityIcon from '@mui/icons-material/Visibility'
import PersonIcon from '@mui/icons-material/Person'
import SettingsIcon from '@mui/icons-material/Settings'
import SecurityIcon from '@mui/icons-material/Security'
import BugReportIcon from '@mui/icons-material/BugReport'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import AddIcon from '@mui/icons-material/Add'
import LoginIcon from '@mui/icons-material/Login'
import LogoutIcon from '@mui/icons-material/Logout'
import KeyIcon from '@mui/icons-material/Key'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import BuildIcon from '@mui/icons-material/Build'
import CalendarTodayIcon from '@mui/icons-material/CalendarToday'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import ComputerIcon from '@mui/icons-material/Computer'
import RefreshIcon from '@mui/icons-material/Refresh'
import { auditLogAPI } from '../services/api'

const getActionIcon = (action) => {
  switch (action) {
    case 'LOGIN':
    case 'LOGIN_FAILED': return <LoginIcon fontSize="small" />
    case 'LOGOUT': return <LogoutIcon fontSize="small" />
    case 'ACCEPT_ANALYSIS':
    case 'REJECT_ANALYSIS':
    case 'TRIGGER_ANALYSIS': return <SmartToyIcon fontSize="small" />
    case 'CREATE_BUG': return <BugReportIcon fontSize="small" />
    case 'UPDATE_ROLE':
    case 'INVITE_USER': return <PersonIcon fontSize="small" />
    case 'UPDATE_CONFIG': return <SettingsIcon fontSize="small" />
    case 'API_KEY_REGENERATE': return <KeyIcon fontSize="small" />
    case 'CREATE_PR': return <BuildIcon fontSize="small" />
    case 'CRON_JOB': return <AccessTimeIcon fontSize="small" />
    default: return <HistoryIcon fontSize="small" />
  }
}

const getCategoryColor = (category) => {
  const colors = {
    authentication: '#6366f1',
    analysis: '#10b981',
    jira: '#3b82f6',
    users: '#8b5cf6',
    settings: '#64748b',
    security: '#ef4444',
    system: '#f59e0b',
    github: '#1f2937'
  }
  return colors[category] || '#64748b'
}

function AuditLogPreview() {
  const location = useLocation()
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [actionFilter, setActionFilter] = useState('')
  const [dateRange, setDateRange] = useState('today')
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false)
  const [selectedLog, setSelectedLog] = useState(null)

  // Real data state
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [auditLogs, setAuditLogs] = useState([])
  const [error, setError] = useState(null)

  const fetchAuditLogs = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true)
      else setLoading(true)

      const response = await auditLogAPI.getEntries({ limit: 100 })
      const data = response?.data || response
      const entries = data?.entries || []

      // Transform API response to expected format
      const transformedLogs = entries.map((item, idx) => ({
        id: item.id || idx + 1,
        timestamp: item.timestamp ? new Date(item.timestamp).toLocaleString() : '-',
        user: item.user_email || item.user_name || 'system',
        action: item.action || 'ACTIVITY',
        category: item.resource_type || 'system',
        resource: item.resource_id || '-',
        details: item.details || '-',
        status: item.status || 'success',
        ipAddress: item.ip_address || '-',
        userAgent: item.user_agent || '-'
      }))

      setAuditLogs(transformedLogs)
      setError(null)
    } catch (err) {
      console.error('Error fetching audit logs:', err)
      setError(err.message || 'Failed to fetch audit logs')
      setAuditLogs([])
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  // Auto-fetch on mount and navigation
  useEffect(() => {
    fetchAuditLogs()
  }, [location.key, fetchAuditLogs])

  const handleRefresh = () => fetchAuditLogs(true)

  const categories = [...new Set(auditLogs.map(l => l.category))]
  const actions = [...new Set(auditLogs.map(l => l.action))]

  const handleViewDetails = (log) => {
    setSelectedLog(log)
    setDetailsDialogOpen(true)
  }

  const stats = {
    total: auditLogs.length,
    success: auditLogs.filter(l => l.status === 'success').length,
    failed: auditLogs.filter(l => l.status === 'failed').length,
    users: [...new Set(auditLogs.map(l => l.user))].length
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc', pb: 4 }}>
      {/* Header */}
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 3,
          borderRadius: 3,
          background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
          color: 'white'
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h5" fontWeight={600} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <HistoryIcon /> Audit Log
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
              Track all user actions and system events
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            sx={{ bgcolor: 'white', color: '#334155', '&:hover': { bgcolor: '#f1f5f9' } }}
          >
            Export Logs
          </Button>
        </Box>
      </Paper>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {[
          { label: 'Total Events', value: stats.total, icon: <HistoryIcon />, color: '#64748b' },
          { label: 'Successful', value: stats.success, icon: <CheckCircleIcon />, color: '#10b981' },
          { label: 'Failed', value: stats.failed, icon: <ErrorIcon />, color: '#ef4444' },
          { label: 'Active Users', value: stats.users, icon: <PersonIcon />, color: '#6366f1' }
        ].map((stat, idx) => (
          <Grid item xs={6} md={3} key={idx}>
            <Card elevation={0} sx={{ borderRadius: 3, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: alpha(stat.color, 0.1), color: stat.color, width: 48, height: 48 }}>
                  {stat.icon}
                </Avatar>
                <Box>
                  <Typography variant="h4" fontWeight="bold">{stat.value}</Typography>
                  <Typography variant="body2" color="textSecondary">{stat.label}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Filters */}
      <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 3, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              size="small"
              InputProps={{
                startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment>
              }}
            />
          </Grid>
          <Grid item xs={6} md={2}>
            <TextField
              fullWidth
              select
              label="Category"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              size="small"
            >
              <MenuItem value="">All Categories</MenuItem>
              {categories.map(c => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={6} md={2}>
            <TextField
              fullWidth
              select
              label="Action"
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              size="small"
            >
              <MenuItem value="">All Actions</MenuItem>
              {actions.map(a => <MenuItem key={a} value={a}>{a}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid item xs={6} md={2}>
            <TextField
              fullWidth
              select
              label="Date Range"
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              size="small"
            >
              <MenuItem value="today">Today</MenuItem>
              <MenuItem value="yesterday">Yesterday</MenuItem>
              <MenuItem value="week">Last 7 Days</MenuItem>
              <MenuItem value="month">Last 30 Days</MenuItem>
              <MenuItem value="custom">Custom Range</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={6} md={3}>
            <Button fullWidth variant="outlined" onClick={() => {
              setSearchTerm('')
              setCategoryFilter('')
              setActionFilter('')
              setDateRange('today')
            }}>
              Clear Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Audit Logs Table */}
      <Paper elevation={0} sx={{ borderRadius: 3, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', overflow: 'hidden' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: 'grey.50' }}>
                <TableCell sx={{ fontWeight: 600 }}>Timestamp</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>User</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Action</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Category</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Resource</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>IP Address</TableCell>
                <TableCell align="center" sx={{ fontWeight: 600 }}>Details</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                // Loading skeleton
                [...Array(5)].map((_, idx) => (
                  <TableRow key={idx}>
                    <TableCell><Skeleton width={150} /></TableCell>
                    <TableCell><Skeleton width={100} /></TableCell>
                    <TableCell><Skeleton width={100} /></TableCell>
                    <TableCell><Skeleton width={80} /></TableCell>
                    <TableCell><Skeleton width={100} /></TableCell>
                    <TableCell><Skeleton width={60} /></TableCell>
                    <TableCell><Skeleton width={100} /></TableCell>
                    <TableCell><Skeleton width={30} /></TableCell>
                  </TableRow>
                ))
              ) : error ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                    <ErrorIcon sx={{ fontSize: 48, color: 'error.main', mb: 1 }} />
                    <Typography color="error">{error}</Typography>
                  </TableCell>
                </TableRow>
              ) : auditLogs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                    <HistoryIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                    <Typography color="textSecondary">No audit logs found</Typography>
                  </TableCell>
                </TableRow>
              ) : auditLogs.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((log) => (
                <TableRow
                  key={log.id}
                  hover
                  sx={{ bgcolor: log.status === 'failed' ? alpha('#ef4444', 0.05) : 'inherit' }}
                >
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CalendarTodayIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                        {log.timestamp}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Avatar sx={{ width: 24, height: 24, fontSize: '0.7rem', bgcolor: log.user === 'system' ? '#f59e0b' : '#6366f1' }}>
                        {log.user === 'system' ? 'S' : log.user[0].toUpperCase()}
                      </Avatar>
                      <Typography variant="body2">
                        {log.user === 'system' ? 'System' : log.user.split('@')[0]}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getActionIcon(log.action)}
                      <Typography variant="body2" fontWeight={500}>
                        {log.action.replace(/_/g, ' ')}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={log.category}
                      size="small"
                      sx={{
                        bgcolor: alpha(getCategoryColor(log.category), 0.1),
                        color: getCategoryColor(log.category),
                        fontSize: '0.7rem'
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {log.resource}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      icon={log.status === 'success' ? <CheckCircleIcon /> : <ErrorIcon />}
                      label={log.status}
                      size="small"
                      sx={{
                        bgcolor: log.status === 'success' ? '#dcfce7' : '#fee2e2',
                        color: log.status === 'success' ? '#166534' : '#991b1b',
                        '& .MuiChip-icon': { color: 'inherit' },
                        fontSize: '0.7rem'
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                      {log.ipAddress}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title="View Details">
                      <IconButton size="small" onClick={() => handleViewDetails(log)}>
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={auditLogs.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(e, p) => setPage(p)}
          onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value)); setPage(0); }}
        />
      </Paper>

      {/* Details Dialog */}
      <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth="sm" fullWidth>
        {selectedLog && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <HistoryIcon />
                Audit Log Details
              </Box>
            </DialogTitle>
            <DialogContent>
              <List>
                <ListItem>
                  <ListItemText
                    primary="Timestamp"
                    secondary={selectedLog.timestamp}
                    primaryTypographyProps={{ variant: 'caption', color: 'textSecondary' }}
                    secondaryTypographyProps={{ variant: 'body1', fontFamily: 'monospace' }}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary="User"
                    secondary={selectedLog.user}
                    primaryTypographyProps={{ variant: 'caption', color: 'textSecondary' }}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary="Action"
                    secondary={
                      <Chip
                        label={selectedLog.action.replace(/_/g, ' ')}
                        size="small"
                        sx={{ mt: 0.5 }}
                      />
                    }
                    primaryTypographyProps={{ variant: 'caption', color: 'textSecondary' }}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary="Category"
                    secondary={
                      <Chip
                        label={selectedLog.category}
                        size="small"
                        sx={{
                          mt: 0.5,
                          bgcolor: alpha(getCategoryColor(selectedLog.category), 0.1),
                          color: getCategoryColor(selectedLog.category)
                        }}
                      />
                    }
                    primaryTypographyProps={{ variant: 'caption', color: 'textSecondary' }}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary="Resource"
                    secondary={selectedLog.resource}
                    primaryTypographyProps={{ variant: 'caption', color: 'textSecondary' }}
                    secondaryTypographyProps={{ fontFamily: 'monospace' }}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary="Details"
                    secondary={selectedLog.details}
                    primaryTypographyProps={{ variant: 'caption', color: 'textSecondary' }}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary="Status"
                    secondary={
                      <Chip
                        icon={selectedLog.status === 'success' ? <CheckCircleIcon /> : <ErrorIcon />}
                        label={selectedLog.status}
                        size="small"
                        sx={{
                          mt: 0.5,
                          bgcolor: selectedLog.status === 'success' ? '#dcfce7' : '#fee2e2',
                          color: selectedLog.status === 'success' ? '#166534' : '#991b1b',
                          '& .MuiChip-icon': { color: 'inherit' }
                        }}
                      />
                    }
                    primaryTypographyProps={{ variant: 'caption', color: 'textSecondary' }}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary="IP Address"
                    secondary={selectedLog.ipAddress}
                    primaryTypographyProps={{ variant: 'caption', color: 'textSecondary' }}
                    secondaryTypographyProps={{ fontFamily: 'monospace' }}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary="User Agent"
                    secondary={selectedLog.userAgent}
                    primaryTypographyProps={{ variant: 'caption', color: 'textSecondary' }}
                  />
                </ListItem>
              </List>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  )
}

export default AuditLogPreview
