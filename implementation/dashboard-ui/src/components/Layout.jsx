import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  Avatar,
  Menu,
  MenuItem,
  Tooltip,
  Badge,
  Collapse
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import MenuIcon from '@mui/icons-material/Menu'
import LogoutIcon from '@mui/icons-material/Logout'
import PersonIcon from '@mui/icons-material/Person'
import AccountCircleIcon from '@mui/icons-material/AccountCircle'
import SecurityIcon from '@mui/icons-material/Security'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import DashboardIcon from '@mui/icons-material/Dashboard'
import ErrorIcon from '@mui/icons-material/Error'
import AnalyticsIcon from '@mui/icons-material/Analytics'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import RefreshIcon from '@mui/icons-material/Refresh'
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks'
import BoltIcon from '@mui/icons-material/Bolt'
import MonitorHeartIcon from '@mui/icons-material/MonitorHeart'
import AccountTreeIcon from '@mui/icons-material/AccountTree'
import BugReportIcon from '@mui/icons-material/BugReport'
import MergeIcon from '@mui/icons-material/Merge'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import ScienceIcon from '@mui/icons-material/Science'
import GroupIcon from '@mui/icons-material/Group'
import SettingsIcon from '@mui/icons-material/Settings'
import NotificationsIcon from '@mui/icons-material/Notifications'
import HistoryIcon from '@mui/icons-material/History'
import ExpandLess from '@mui/icons-material/ExpandLess'
import ExpandMore from '@mui/icons-material/ExpandMore'
import ThemeSelector from './ThemeSelector'
import { useColorTheme } from '../theme/ThemeContext'

const drawerWidth = 260

// Organized menu structure with sections
const menuSections = [
  {
    title: 'Dashboard',
    items: [
      { text: 'Overview', icon: <DashboardIcon />, path: '/' },
      { text: 'Pipeline Status', icon: <AccountTreeIcon />, path: '/pipeline' },
      { text: 'Services', icon: <MonitorHeartIcon />, path: '/services' }
    ]
  },
  {
    title: 'Analysis',
    items: [
      { text: 'Failures', icon: <ErrorIcon />, path: '/failures' },
      { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
      { text: 'Manual Trigger', icon: <PlayArrowIcon />, path: '/manual-trigger' },
      { text: 'Bulk Trigger', icon: <BoltIcon />, path: '/bulk-trigger' }
    ]
  },
  {
    title: 'Integrations',
    items: [
      { text: 'Jira Bugs', icon: <BugReportIcon />, path: '/jira-bugs' },
      { text: 'PR Workflow', icon: <MergeIcon />, path: '/pr-workflow' }
    ]
  },
  {
    title: 'AI Tools',
    items: [
      { text: 'AI Chatbot', icon: <SmartToyIcon />, path: '/ai-chatbot' },
      { text: 'Test Generator', icon: <ScienceIcon />, path: '/test-generator' },
      { text: 'Knowledge Base', icon: <LibraryBooksIcon />, path: '/knowledge' }
    ]
  },
  {
    title: 'Administration',
    items: [
      { text: 'Users', icon: <GroupIcon />, path: '/users' },
      { text: 'Configuration', icon: <SettingsIcon />, path: '/config' },
      { text: 'Notifications', icon: <NotificationsIcon />, path: '/notifications' },
      { text: 'Audit Log', icon: <HistoryIcon />, path: '/audit-log' }
    ]
  }
]

function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [userMenuAnchor, setUserMenuAnchor] = useState(null)
  const [user, setUser] = useState(null)
  const [expandedSections, setExpandedSections] = useState({
    Dashboard: true,
    Analysis: true,
    Integrations: true,
    'AI Tools': true,
    Administration: true
  })
  const navigate = useNavigate()
  const location = useLocation()
  const { theme } = useColorTheme()

  // Load user from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem('ddn-user')
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    }
  }, [])

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  const handleNavigation = (path) => {
    navigate(path)
    setMobileOpen(false)
  }

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget)
  }

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null)
  }

  const handleLogout = () => {
    localStorage.removeItem('ddn-user')
    setUser(null)
    handleUserMenuClose()
    navigate('/login')
  }

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const getInitials = (name) => {
    if (!name) return 'U'
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  const formatLoginTime = (isoString) => {
    if (!isoString) return 'N/A'
    const date = new Date(isoString)
    return date.toLocaleString()
  }

  const isPathActive = (path) => {
    if (path === '/') {
      return location.pathname === '/' || location.pathname === '/dashboard'
    }
    return location.pathname === path || location.pathname.startsWith(path + '/')
  }

  const drawer = (
    <Box sx={{ bgcolor: theme.isDark ? theme.surface : 'white', height: '100%', overflowY: 'auto' }}>
      <Toolbar sx={{ background: theme.headerGradient }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 36, height: 36 }}>
            <SmartToyIcon sx={{ color: 'white', fontSize: 20 }} />
          </Avatar>
          <Box>
            <Typography variant="h6" noWrap component="div" sx={{ color: 'white', fontWeight: 700, fontSize: '1rem', lineHeight: 1.2 }}>
              DDN AI
            </Typography>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.65rem' }}>
              Test Analysis Platform
            </Typography>
          </Box>
        </Box>
      </Toolbar>
      <Divider />

      {menuSections.map((section, sectionIndex) => (
        <Box key={section.title}>
          <ListItemButton
            onClick={() => toggleSection(section.title)}
            sx={{
              py: 1,
              px: 2,
              '&:hover': { bgcolor: alpha(theme.primary, 0.05) }
            }}
          >
            <ListItemText
              primary={section.title}
              primaryTypographyProps={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: theme.textSecondary,
                textTransform: 'uppercase',
                letterSpacing: 0.5
              }}
            />
            {expandedSections[section.title] ?
              <ExpandLess sx={{ color: theme.textSecondary, fontSize: 18 }} /> :
              <ExpandMore sx={{ color: theme.textSecondary, fontSize: 18 }} />
            }
          </ListItemButton>
          <Collapse in={expandedSections[section.title]} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {section.items.map((item) => (
                <ListItem key={item.path} disablePadding>
                  <ListItemButton
                    selected={isPathActive(item.path)}
                    onClick={() => handleNavigation(item.path)}
                    sx={{
                      py: 0.75,
                      pl: 3,
                      '&.Mui-selected': {
                        bgcolor: alpha(theme.primary, 0.1),
                        borderRight: `3px solid ${theme.primary}`,
                        '& .MuiListItemIcon-root': { color: theme.primary },
                        '& .MuiListItemText-primary': { color: theme.primary, fontWeight: 600 }
                      },
                      '&:hover': { bgcolor: alpha(theme.primary, 0.05) }
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 36, color: isPathActive(item.path) ? theme.primary : theme.textSecondary }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText
                      primary={item.text}
                      primaryTypographyProps={{
                        fontSize: '0.875rem',
                        color: isPathActive(item.path) ? theme.primary : theme.textPrimary
                      }}
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Collapse>
          {sectionIndex < menuSections.length - 1 && <Divider sx={{ my: 0.5 }} />}
        </Box>
      ))}
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: theme.background }}>
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          background: theme.headerGradient,
          borderBottom: `1px solid ${alpha(theme.primary, 0.1)}`
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Test Failure Analysis Dashboard
          </Typography>
          <ThemeSelector />
          <IconButton color="inherit" onClick={() => window.location.reload()}>
            <RefreshIcon />
          </IconButton>

          {/* User Menu */}
          {user ? (
            <>
              <Tooltip title="Account settings">
                <IconButton
                  onClick={handleUserMenuOpen}
                  sx={{ ml: 1 }}
                >
                  <Badge
                    overlap="circular"
                    anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                    badgeContent={
                      <Box
                        sx={{
                          width: 10,
                          height: 10,
                          bgcolor: '#10b981',
                          borderRadius: '50%',
                          border: '2px solid white'
                        }}
                      />
                    }
                  >
                    <Avatar
                      sx={{
                        width: 36,
                        height: 36,
                        bgcolor: 'rgba(255,255,255,0.2)',
                        color: 'white',
                        fontSize: '0.9rem',
                        fontWeight: 600,
                        border: '2px solid rgba(255,255,255,0.3)'
                      }}
                    >
                      {getInitials(user.name)}
                    </Avatar>
                  </Badge>
                </IconButton>
              </Tooltip>
              <Menu
                anchorEl={userMenuAnchor}
                open={Boolean(userMenuAnchor)}
                onClose={handleUserMenuClose}
                onClick={handleUserMenuClose}
                PaperProps={{
                  elevation: 0,
                  sx: {
                    overflow: 'visible',
                    filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.15))',
                    mt: 1.5,
                    minWidth: 280,
                    borderRadius: 2,
                    '&:before': {
                      content: '""',
                      display: 'block',
                      position: 'absolute',
                      top: 0,
                      right: 14,
                      width: 10,
                      height: 10,
                      bgcolor: 'background.paper',
                      transform: 'translateY(-50%) rotate(45deg)',
                      zIndex: 0,
                    },
                  },
                }}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
              >
                {/* User Info Header */}
                <Box sx={{ px: 2, py: 1.5, bgcolor: alpha(theme.primary, 0.05) }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <Avatar
                      sx={{
                        width: 48,
                        height: 48,
                        bgcolor: theme.primary,
                        fontSize: '1.1rem',
                        fontWeight: 600
                      }}
                    >
                      {getInitials(user.name)}
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={600}>
                        {user.name || 'User'}
                      </Typography>
                      <Typography variant="body2" color="textSecondary" sx={{ fontSize: '0.8rem' }}>
                        {user.email}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
                <Divider />

                {/* Session Info */}
                <Box sx={{ px: 2, py: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <SecurityIcon sx={{ fontSize: 16, color: '#10b981' }} />
                    <Typography variant="caption" color="textSecondary">
                      Secure Session Active
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AccessTimeIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                    <Typography variant="caption" color="textSecondary">
                      Logged in: {formatLoginTime(user.loginTime)}
                    </Typography>
                  </Box>
                </Box>
                <Divider />

                {/* Menu Items */}
                <MenuItem onClick={() => navigate('/users')}>
                  <ListItemIcon>
                    <PersonIcon fontSize="small" />
                  </ListItemIcon>
                  Profile Settings
                </MenuItem>
                <MenuItem onClick={() => navigate('/config')}>
                  <ListItemIcon>
                    <SettingsIcon fontSize="small" />
                  </ListItemIcon>
                  Configuration
                </MenuItem>
                <Divider />
                <MenuItem onClick={handleLogout} sx={{ color: '#ef4444' }}>
                  <ListItemIcon>
                    <LogoutIcon fontSize="small" sx={{ color: '#ef4444' }} />
                  </ListItemIcon>
                  Logout
                </MenuItem>
              </Menu>
            </>
          ) : (
            <Tooltip title="Login">
              <IconButton
                color="inherit"
                onClick={() => navigate('/login')}
                sx={{ ml: 1 }}
              >
                <AccountCircleIcon />
              </IconButton>
            </Tooltip>
          )}
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              bgcolor: theme.isDark ? theme.surface : 'white',
              borderRight: `1px solid ${alpha(theme.primary, 0.1)}`
            }
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              bgcolor: theme.isDark ? theme.surface : 'white',
              borderRight: `1px solid ${alpha(theme.primary, 0.1)}`
            }
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: 8,
          bgcolor: theme.background,
          minHeight: 'calc(100vh - 64px)'
        }}
      >
        {children}
      </Box>
    </Box>
  )
}

export default Layout
