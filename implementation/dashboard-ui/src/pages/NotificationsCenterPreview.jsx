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
  IconButton,
  Avatar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Tabs,
  Tab,
  Divider,
  Badge,
  Tooltip,
  Menu,
  MenuItem,
  Checkbox,
  FormControlLabel
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import { useColorTheme } from '../theme/ThemeContext'
import NotificationsIcon from '@mui/icons-material/Notifications'
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive'
import NotificationsOffIcon from '@mui/icons-material/NotificationsOff'
import ErrorIcon from '@mui/icons-material/Error'
import WarningIcon from '@mui/icons-material/Warning'
import InfoIcon from '@mui/icons-material/Info'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import BugReportIcon from '@mui/icons-material/BugReport'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import BuildIcon from '@mui/icons-material/Build'
import EmailIcon from '@mui/icons-material/Email'
import DeleteIcon from '@mui/icons-material/Delete'
import DoneAllIcon from '@mui/icons-material/DoneAll'
import FilterListIcon from '@mui/icons-material/FilterList'
import MoreVertIcon from '@mui/icons-material/MoreVert'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import PersonIcon from '@mui/icons-material/Person'
import SettingsIcon from '@mui/icons-material/Settings'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import RefreshIcon from '@mui/icons-material/Refresh'
import CircularProgress from '@mui/material/CircularProgress'
import Skeleton from '@mui/material/Skeleton'
import { notificationsAPI } from '../services/api'

const getNotificationIcon = (type) => {
  switch (type) {
    case 'error': return <ErrorIcon />
    case 'warning': return <WarningIcon />
    case 'success': return <CheckCircleIcon />
    case 'info': return <InfoIcon />
    default: return <NotificationsIcon />
  }
}

const getNotificationColor = (type) => {
  switch (type) {
    case 'error': return '#ef4444'
    case 'warning': return '#f59e0b'
    case 'success': return '#10b981'
    case 'info': return '#3b82f6'
    default: return '#64748b'
  }
}

const getCategoryIcon = (category) => {
  switch (category) {
    case 'failure': return <BugReportIcon fontSize="small" />
    case 'analysis': return <SmartToyIcon fontSize="small" />
    case 'jira': return <BugReportIcon fontSize="small" />
    case 'pr': return <BuildIcon fontSize="small" />
    case 'pipeline': return <TrendingUpIcon fontSize="small" />
    case 'system': return <SettingsIcon fontSize="small" />
    default: return <NotificationsIcon fontSize="small" />
  }
}

function NotificationsCenterPreview() {
  const { theme } = useColorTheme()
  const location = useLocation()
  const [activeTab, setActiveTab] = useState(0)
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState(null)

  // Fetch notifications from API
  const fetchNotifications = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true)
      else setLoading(true)

      const response = await notificationsAPI.getNotifications({ limit: 50 })
      const data = response?.data || response
      const notificationList = data?.notifications || []

      // Transform API response to expected format
      const transformedNotifications = notificationList.map((item, idx) => ({
        id: item.id || idx + 1,
        type: item.severity === 'error' ? 'error' :
              item.severity === 'warning' ? 'warning' :
              item.severity === 'success' ? 'success' : 'info',
        title: item.title || 'Notification',
        message: item.message || '-',
        time: item.created_at ? new Date(item.created_at).toLocaleString() : 'Recently',
        read: item.is_read || false,
        link: item.action_url || null,
        category: item.type || 'system'
      }))

      setNotifications(transformedNotifications)
      setError(null)
    } catch (err) {
      console.error('Error fetching notifications:', err)
      setError(err.message || 'Failed to fetch notifications')
      setNotifications([])
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  // Auto-fetch on mount and navigation
  useEffect(() => {
    fetchNotifications()
  }, [location.key, fetchNotifications])

  const handleRefresh = () => fetchNotifications(true)

  const handleMarkAsReadAPI = async (id) => {
    try {
      await notificationsAPI.markAsRead(id)
    } catch (err) {
      console.error('Error marking notification as read:', err)
    }
  }

  const handleMarkAllAsReadAPI = async () => {
    try {
      await notificationsAPI.markAllAsRead()
    } catch (err) {
      console.error('Error marking all as read:', err)
    }
  }
  const [selectedNotifications, setSelectedNotifications] = useState([])
  const [filterAnchorEl, setFilterAnchorEl] = useState(null)
  const [categoryFilter, setCategoryFilter] = useState('all')

  const unreadCount = notifications.filter(n => !n.read).length
  const filteredNotifications = categoryFilter === 'all'
    ? notifications
    : notifications.filter(n => n.category === categoryFilter)

  const handleMarkAsRead = (id) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n))
  }

  const handleMarkAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }

  const handleDelete = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const handleDeleteSelected = () => {
    setNotifications(prev => prev.filter(n => !selectedNotifications.includes(n.id)))
    setSelectedNotifications([])
  }

  const handleSelectNotification = (id) => {
    setSelectedNotifications(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  const handleSelectAll = () => {
    if (selectedNotifications.length === filteredNotifications.length) {
      setSelectedNotifications([])
    } else {
      setSelectedNotifications(filteredNotifications.map(n => n.id))
    }
  }

  const stats = {
    total: notifications.length,
    unread: unreadCount,
    failures: notifications.filter(n => n.category === 'failure').length,
    analyses: notifications.filter(n => n.category === 'analysis').length
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: theme.background, pb: 4 }}>
      {/* Header */}
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 3,
          borderRadius: 3,
          background: theme.headerGradient,
          color: 'white'
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h5" fontWeight={600} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <NotificationsActiveIcon /> Notifications Center
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
              Stay updated on failures, analyses, and system events
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Badge badgeContent={unreadCount} color="error">
              <Chip
                label="Unread"
                sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                icon={<NotificationsIcon sx={{ color: 'white !important' }} />}
              />
            </Badge>
          </Box>
        </Box>
      </Paper>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {[
          { label: 'Total', value: stats.total, icon: <NotificationsIcon />, color: '#64748b' },
          { label: 'Unread', value: stats.unread, icon: <NotificationsActiveIcon />, color: '#ef4444' },
          { label: 'Failures', value: stats.failures, icon: <BugReportIcon />, color: '#f59e0b' },
          { label: 'Analyses', value: stats.analyses, icon: <SmartToyIcon />, color: '#3b82f6' }
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

      {/* Notifications List */}
      <Paper elevation={0} sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
        {/* Toolbar */}
        <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={selectedNotifications.length === filteredNotifications.length && filteredNotifications.length > 0}
                  indeterminate={selectedNotifications.length > 0 && selectedNotifications.length < filteredNotifications.length}
                  onChange={handleSelectAll}
                />
              }
              label={selectedNotifications.length > 0 ? `${selectedNotifications.length} selected` : 'Select all'}
            />
            {selectedNotifications.length > 0 && (
              <>
                <Button size="small" startIcon={<DoneAllIcon />} onClick={() => {
                  setNotifications(prev => prev.map(n => selectedNotifications.includes(n.id) ? { ...n, read: true } : n))
                  setSelectedNotifications([])
                }}>
                  Mark as Read
                </Button>
                <Button size="small" color="error" startIcon={<DeleteIcon />} onClick={handleDeleteSelected}>
                  Delete
                </Button>
              </>
            )}
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              size="small"
              startIcon={<FilterListIcon />}
              onClick={(e) => setFilterAnchorEl(e.currentTarget)}
            >
              {categoryFilter === 'all' ? 'All Categories' : categoryFilter}
            </Button>
            <Menu
              anchorEl={filterAnchorEl}
              open={Boolean(filterAnchorEl)}
              onClose={() => setFilterAnchorEl(null)}
            >
              <MenuItem onClick={() => { setCategoryFilter('all'); setFilterAnchorEl(null) }}>All</MenuItem>
              <MenuItem onClick={() => { setCategoryFilter('failure'); setFilterAnchorEl(null) }}>Failures</MenuItem>
              <MenuItem onClick={() => { setCategoryFilter('analysis'); setFilterAnchorEl(null) }}>Analyses</MenuItem>
              <MenuItem onClick={() => { setCategoryFilter('jira'); setFilterAnchorEl(null) }}>Jira</MenuItem>
              <MenuItem onClick={() => { setCategoryFilter('pr'); setFilterAnchorEl(null) }}>PRs</MenuItem>
              <MenuItem onClick={() => { setCategoryFilter('pipeline'); setFilterAnchorEl(null) }}>Pipeline</MenuItem>
              <MenuItem onClick={() => { setCategoryFilter('system'); setFilterAnchorEl(null) }}>System</MenuItem>
            </Menu>
            <Button size="small" startIcon={<DoneAllIcon />} onClick={handleMarkAllAsRead}>
              Mark All Read
            </Button>
          </Box>
        </Box>

        {/* Notifications */}
        <List sx={{ p: 0 }}>
          {filteredNotifications.map((notification, idx) => (
            <ListItem
              key={notification.id}
              sx={{
                borderBottom: idx < filteredNotifications.length - 1 ? '1px solid' : 'none',
                borderColor: 'divider',
                bgcolor: notification.read ? 'white' : alpha('#3b82f6', 0.05),
                '&:hover': { bgcolor: alpha('#3b82f6', 0.08) },
                cursor: 'pointer'
              }}
              onClick={() => handleMarkAsRead(notification.id)}
            >
              <Checkbox
                checked={selectedNotifications.includes(notification.id)}
                onChange={(e) => {
                  e.stopPropagation()
                  handleSelectNotification(notification.id)
                }}
                onClick={(e) => e.stopPropagation()}
              />
              <ListItemIcon sx={{ minWidth: 48 }}>
                <Avatar
                  sx={{
                    bgcolor: alpha(getNotificationColor(notification.type), 0.1),
                    color: getNotificationColor(notification.type),
                    width: 40,
                    height: 40
                  }}
                >
                  {getNotificationIcon(notification.type)}
                </Avatar>
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body1" fontWeight={notification.read ? 400 : 600}>
                      {notification.title}
                    </Typography>
                    {!notification.read && (
                      <Box sx={{ width: 8, height: 8, bgcolor: '#3b82f6', borderRadius: '50%' }} />
                    )}
                    <Chip
                      size="small"
                      label={notification.category}
                      icon={getCategoryIcon(notification.category)}
                      sx={{ height: 20, fontSize: '0.65rem', ml: 1 }}
                    />
                  </Box>
                }
                secondary={
                  <Box sx={{ mt: 0.5 }}>
                    <Typography variant="body2" color="textSecondary">
                      {notification.message}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                      <AccessTimeIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                      <Typography variant="caption" color="textSecondary">
                        {notification.time}
                      </Typography>
                    </Box>
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                {notification.link && (
                  <Tooltip title="View Details">
                    <IconButton size="small">
                      <OpenInNewIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
                <Tooltip title="Delete">
                  <IconButton size="small" onClick={(e) => { e.stopPropagation(); handleDelete(notification.id) }}>
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>

        {filteredNotifications.length === 0 && (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <NotificationsOffIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
            <Typography color="textSecondary">No notifications</Typography>
          </Box>
        )}
      </Paper>
    </Box>
  )
}

export default NotificationsCenterPreview
