import React, { useState } from 'react'
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
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  TableContainer,
  TablePagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Switch,
  Divider,
  Alert,
  Tooltip,
  InputAdornment,
  Badge,
  LinearProgress,
  Skeleton,
  CircularProgress
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import PersonIcon from '@mui/icons-material/Person'
import GroupIcon from '@mui/icons-material/Group'
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings'
import SecurityIcon from '@mui/icons-material/Security'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import SearchIcon from '@mui/icons-material/Search'
import EmailIcon from '@mui/icons-material/Email'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import BlockIcon from '@mui/icons-material/Block'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import MoreVertIcon from '@mui/icons-material/MoreVert'
import KeyIcon from '@mui/icons-material/Key'
import HistoryIcon from '@mui/icons-material/History'
import SendIcon from '@mui/icons-material/Send'
import RefreshIcon from '@mui/icons-material/Refresh'
import VisibilityIcon from '@mui/icons-material/Visibility'
import DashboardIcon from '@mui/icons-material/Dashboard'
import BugReportIcon from '@mui/icons-material/BugReport'
import AnalyticsIcon from '@mui/icons-material/Analytics'
import SettingsIcon from '@mui/icons-material/Settings'
import BuildIcon from '@mui/icons-material/Build'

// Mock users data
const mockUsers = [
  {
    id: 1,
    name: 'John Doe',
    email: 'john.doe@company.com',
    role: 'Admin',
    team: 'Platform',
    status: 'Active',
    lastLogin: '2024-11-28 14:30',
    createdAt: '2024-01-15',
    avatar: 'J',
    permissions: ['dashboard', 'failures', 'analytics', 'triggers', 'jira', 'settings', 'users']
  },
  {
    id: 2,
    name: 'Jane Smith',
    email: 'jane.smith@company.com',
    role: 'Developer',
    team: 'Backend',
    status: 'Active',
    lastLogin: '2024-11-28 12:15',
    createdAt: '2024-02-20',
    avatar: 'J',
    permissions: ['dashboard', 'failures', 'analytics', 'triggers']
  },
  {
    id: 3,
    name: 'Bob Wilson',
    email: 'bob.wilson@company.com',
    role: 'QA Engineer',
    team: 'QA',
    status: 'Active',
    lastLogin: '2024-11-27 16:45',
    createdAt: '2024-03-10',
    avatar: 'B',
    permissions: ['dashboard', 'failures', 'analytics', 'triggers', 'jira']
  },
  {
    id: 4,
    name: 'Alice Johnson',
    email: 'alice.johnson@company.com',
    role: 'Developer',
    team: 'Frontend',
    status: 'Active',
    lastLogin: '2024-11-28 09:20',
    createdAt: '2024-04-05',
    avatar: 'A',
    permissions: ['dashboard', 'failures', 'analytics']
  },
  {
    id: 5,
    name: 'Charlie Brown',
    email: 'charlie.brown@company.com',
    role: 'Viewer',
    team: 'Management',
    status: 'Inactive',
    lastLogin: '2024-11-15 11:00',
    createdAt: '2024-05-12',
    avatar: 'C',
    permissions: ['dashboard', 'analytics']
  }
]

// Mock roles data
const mockRoles = [
  {
    id: 1,
    name: 'Admin',
    description: 'Full access to all features',
    usersCount: 2,
    color: '#dc2626',
    permissions: ['dashboard', 'failures', 'analytics', 'triggers', 'jira', 'pr', 'knowledge', 'services', 'settings', 'users']
  },
  {
    id: 2,
    name: 'Developer',
    description: 'Access to development-related features',
    usersCount: 5,
    color: '#2563eb',
    permissions: ['dashboard', 'failures', 'analytics', 'triggers', 'pr']
  },
  {
    id: 3,
    name: 'QA Engineer',
    description: 'Access to testing and bug tracking',
    usersCount: 3,
    color: '#16a34a',
    permissions: ['dashboard', 'failures', 'analytics', 'triggers', 'jira', 'knowledge']
  },
  {
    id: 4,
    name: 'Viewer',
    description: 'Read-only access to dashboards',
    usersCount: 8,
    color: '#64748b',
    permissions: ['dashboard', 'analytics']
  }
]

// Mock teams data
const mockTeams = [
  { id: 1, name: 'Platform', members: 4, lead: 'John Doe' },
  { id: 2, name: 'Backend', members: 6, lead: 'Jane Smith' },
  { id: 3, name: 'Frontend', members: 5, lead: 'Alice Johnson' },
  { id: 4, name: 'QA', members: 3, lead: 'Bob Wilson' },
  { id: 5, name: 'DevOps', members: 2, lead: 'Mike Chen' },
  { id: 6, name: 'Management', members: 3, lead: 'Sarah Davis' }
]

const allPermissions = [
  { key: 'dashboard', label: 'Dashboard', icon: <DashboardIcon fontSize="small" /> },
  { key: 'failures', label: 'Failures', icon: <BugReportIcon fontSize="small" /> },
  { key: 'analytics', label: 'Analytics', icon: <AnalyticsIcon fontSize="small" /> },
  { key: 'triggers', label: 'Triggers', icon: <BuildIcon fontSize="small" /> },
  { key: 'jira', label: 'Jira Integration', icon: <BugReportIcon fontSize="small" /> },
  { key: 'pr', label: 'PR Workflow', icon: <BuildIcon fontSize="small" /> },
  { key: 'knowledge', label: 'Knowledge Base', icon: <VisibilityIcon fontSize="small" /> },
  { key: 'services', label: 'Services', icon: <SettingsIcon fontSize="small" /> },
  { key: 'settings', label: 'Settings', icon: <SettingsIcon fontSize="small" /> },
  { key: 'users', label: 'User Management', icon: <GroupIcon fontSize="small" /> }
]

const getRoleColor = (role) => {
  const colors = {
    Admin: '#dc2626',
    Developer: '#2563eb',
    'QA Engineer': '#16a34a',
    Viewer: '#64748b'
  }
  return colors[role] || '#64748b'
}

function UserManagementPreview() {
  const [activeTab, setActiveTab] = useState(0)
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [teamFilter, setTeamFilter] = useState('')
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [addUserDialogOpen, setAddUserDialogOpen] = useState(false)
  const [editUserDialogOpen, setEditUserDialogOpen] = useState(false)
  const [addRoleDialogOpen, setAddRoleDialogOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [inviting, setInviting] = useState(false)

  // Real data state
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [users, setUsers] = useState([])
  const [roles, setRoles] = useState([])
  const [teams, setTeams] = useState([])

  // Fetch users data from API
  React.useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch from users API if available
        const response = await fetch('http://localhost:5001/api/users')
        if (response.ok) {
          const data = await response.json()
          setUsers(data?.users || data || [])
        }
        setError(null)
      } catch (err) {
        console.error('Error fetching users:', err)
        setError(err.message?.includes('Network') ? 'No connection to server' : err.message)
        setUsers([])
        setRoles([])
        setTeams([])
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    role: '',
    team: '',
    permissions: []
  })

  const stats = {
    totalUsers: users.length,
    activeUsers: users.filter(u => u.status === 'Active').length,
    roles: roles.length,
    teams: teams.length
  }

  const handleInviteUser = () => {
    setInviting(true)
    setTimeout(() => {
      setInviting(false)
      setAddUserDialogOpen(false)
      setNewUser({ name: '', email: '', role: '', team: '', permissions: [] })
    }, 2000)
  }

  const handleEditUser = (user) => {
    setSelectedUser(user)
    setEditUserDialogOpen(true)
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
          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
          color: 'white'
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h5" fontWeight={600} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <GroupIcon /> User Management
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
              Manage users, roles, permissions, and teams
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip
              label={`${stats.activeUsers} Active Users`}
              sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
              icon={<PersonIcon sx={{ color: 'white !important' }} />}
            />
          </Box>
        </Box>
      </Paper>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {[
          { label: 'Total Users', value: stats.totalUsers, icon: <PersonIcon />, color: '#6366f1' },
          { label: 'Active Users', value: stats.activeUsers, icon: <CheckCircleIcon />, color: '#10b981' },
          { label: 'Roles', value: stats.roles, icon: <AdminPanelSettingsIcon />, color: '#f59e0b' },
          { label: 'Teams', value: stats.teams, icon: <GroupIcon />, color: '#3b82f6' }
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

      {/* Tabs */}
      <Paper elevation={0} sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
        <Tabs
          value={activeTab}
          onChange={(e, v) => setActiveTab(v)}
          sx={{ borderBottom: '1px solid', borderColor: 'divider', px: 2 }}
        >
          <Tab icon={<PersonIcon />} label="Users" iconPosition="start" />
          <Tab icon={<AdminPanelSettingsIcon />} label="Roles & Permissions" iconPosition="start" />
          <Tab icon={<GroupIcon />} label="Teams" iconPosition="start" />
          <Tab icon={<HistoryIcon />} label="Activity Log" iconPosition="start" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {/* Users Tab */}
          {activeTab === 0 && (
            <>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Box sx={{ display: 'flex', gap: 2, flex: 1 }}>
                  <TextField
                    placeholder="Search users..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    size="small"
                    sx={{ width: 300 }}
                    InputProps={{
                      startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment>
                    }}
                  />
                  <TextField
                    select
                    label="Role"
                    value={roleFilter}
                    onChange={(e) => setRoleFilter(e.target.value)}
                    size="small"
                    sx={{ width: 150 }}
                  >
                    <MenuItem value="">All Roles</MenuItem>
                    {(roles.length > 0 ? roles : mockRoles).map(r => <MenuItem key={r.id} value={r.name}>{r.name}</MenuItem>)}
                  </TextField>
                  <TextField
                    select
                    label="Team"
                    value={teamFilter}
                    onChange={(e) => setTeamFilter(e.target.value)}
                    size="small"
                    sx={{ width: 150 }}
                  >
                    <MenuItem value="">All Teams</MenuItem>
                    {(teams.length > 0 ? teams : mockTeams).map(t => <MenuItem key={t.id} value={t.name}>{t.name}</MenuItem>)}
                  </TextField>
                </Box>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setAddUserDialogOpen(true)}
                  sx={{ bgcolor: '#6366f1' }}
                >
                  Invite User
                </Button>
              </Box>

              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow sx={{ bgcolor: 'grey.50' }}>
                      <TableCell sx={{ fontWeight: 600 }}>User</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Role</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Team</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Last Login</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Permissions</TableCell>
                      <TableCell align="center" sx={{ fontWeight: 600 }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {loading ? (
                      [...Array(5)].map((_, idx) => (
                        <TableRow key={idx}>
                          <TableCell><Box sx={{ display: 'flex', gap: 2 }}><Skeleton variant="circular" width={40} height={40} /><Box><Skeleton width={100} /><Skeleton width={150} /></Box></Box></TableCell>
                          <TableCell><Skeleton width={80} /></TableCell>
                          <TableCell><Skeleton width={80} /></TableCell>
                          <TableCell><Skeleton width={60} /></TableCell>
                          <TableCell><Skeleton width={120} /></TableCell>
                          <TableCell><Skeleton width={100} /></TableCell>
                          <TableCell><Skeleton width={80} /></TableCell>
                        </TableRow>
                      ))
                    ) : error ? (
                      <TableRow>
                        <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                          <Typography color="error">{error}</Typography>
                        </TableCell>
                      </TableRow>
                    ) : users.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                          <PersonIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                          <Typography color="textSecondary">No users found</Typography>
                        </TableCell>
                      </TableRow>
                    ) : users.map((user) => (
                      <TableRow key={user.id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Avatar sx={{ bgcolor: getRoleColor(user.role), width: 40, height: 40 }}>
                              {user.avatar}
                            </Avatar>
                            <Box>
                              <Typography variant="body2" fontWeight={600}>{user.name}</Typography>
                              <Typography variant="caption" color="textSecondary">{user.email}</Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={user.role}
                            size="small"
                            sx={{ bgcolor: alpha(getRoleColor(user.role), 0.1), color: getRoleColor(user.role), fontWeight: 600 }}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{user.team}</Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={user.status === 'Active' ? <CheckCircleIcon /> : <BlockIcon />}
                            label={user.status}
                            size="small"
                            sx={{
                              bgcolor: user.status === 'Active' ? '#dcfce7' : '#fee2e2',
                              color: user.status === 'Active' ? '#166534' : '#991b1b',
                              '& .MuiChip-icon': { color: 'inherit' }
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="textSecondary">{user.lastLogin}</Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {user.permissions.slice(0, 3).map(p => (
                              <Chip key={p} label={p} size="small" variant="outlined" sx={{ fontSize: '0.65rem', height: 20 }} />
                            ))}
                            {user.permissions.length > 3 && (
                              <Chip label={`+${user.permissions.length - 3}`} size="small" sx={{ fontSize: '0.65rem', height: 20 }} />
                            )}
                          </Box>
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title="Edit">
                            <IconButton size="small" onClick={() => handleEditUser(user)}>
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Reset Password">
                            <IconButton size="small">
                              <KeyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton size="small" color="error">
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <TablePagination
                rowsPerPageOptions={[10, 25, 50]}
                component="div"
                count={users.length}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={(e, p) => setPage(p)}
                onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value)); setPage(0); }}
              />
            </>
          )}

          {/* Roles & Permissions Tab */}
          {activeTab === 1 && (
            <>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">Roles & Permissions</Typography>
                <Button variant="contained" startIcon={<AddIcon />} onClick={() => setAddRoleDialogOpen(true)} sx={{ bgcolor: '#6366f1' }}>
                  Create Role
                </Button>
              </Box>

              <Grid container spacing={3}>
                {loading ? (
                  [...Array(4)].map((_, idx) => (
                    <Grid item xs={12} md={6} key={idx}>
                      <Card variant="outlined"><CardContent><Skeleton width="60%" height={24} /><Skeleton width="80%" /></CardContent></Card>
                    </Grid>
                  ))
                ) : (roles.length > 0 ? roles : mockRoles).length === 0 ? (
                  <Grid item xs={12}>
                    <Alert severity="info">No roles configured. Click "Create Role" to add one.</Alert>
                  </Grid>
                ) : (roles.length > 0 ? roles : mockRoles).map((role) => (
                  <Grid item xs={12} md={6} key={role.id}>
                    <Card variant="outlined" sx={{ height: '100%' }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <Avatar sx={{ bgcolor: alpha(role.color, 0.1), color: role.color }}>
                              <SecurityIcon />
                            </Avatar>
                            <Box>
                              <Typography variant="subtitle1" fontWeight={600}>{role.name}</Typography>
                              <Typography variant="caption" color="textSecondary">{role.description}</Typography>
                            </Box>
                          </Box>
                          <Chip label={`${role.usersCount} users`} size="small" />
                        </Box>
                        <Divider sx={{ my: 2 }} />
                        <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mb: 1 }}>
                          Permissions
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                          {role.permissions.map(p => (
                            <Chip
                              key={p}
                              label={p}
                              size="small"
                              sx={{ bgcolor: alpha(role.color, 0.1), color: role.color, fontSize: '0.7rem' }}
                            />
                          ))}
                        </Box>
                        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                          <Button size="small" startIcon={<EditIcon />}>Edit</Button>
                          {role.name !== 'Admin' && (
                            <Button size="small" color="error" startIcon={<DeleteIcon />}>Delete</Button>
                          )}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              <Box sx={{ mt: 4 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Permission Matrix</Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow sx={{ bgcolor: 'grey.50' }}>
                        <TableCell sx={{ fontWeight: 600 }}>Permission</TableCell>
                        {(roles.length > 0 ? roles : mockRoles).map(role => (
                          <TableCell key={role.id} align="center" sx={{ fontWeight: 600 }}>{role.name}</TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {allPermissions.map(perm => (
                        <TableRow key={perm.key}>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {perm.icon}
                              {perm.label}
                            </Box>
                          </TableCell>
                          {(roles.length > 0 ? roles : mockRoles).map(role => (
                            <TableCell key={role.id} align="center">
                              {role.permissions.includes(perm.key) ? (
                                <CheckCircleIcon sx={{ color: '#10b981', fontSize: 20 }} />
                              ) : (
                                <BlockIcon sx={{ color: '#e2e8f0', fontSize: 20 }} />
                              )}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            </>
          )}

          {/* Teams Tab */}
          {activeTab === 2 && (
            <>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">Teams</Typography>
                <Button variant="contained" startIcon={<AddIcon />} sx={{ bgcolor: '#6366f1' }}>
                  Create Team
                </Button>
              </Box>

              <Grid container spacing={3}>
                {loading ? (
                  [...Array(3)].map((_, idx) => (
                    <Grid item xs={12} md={4} key={idx}>
                      <Card variant="outlined"><CardContent><Skeleton width="60%" height={24} /><Skeleton width="40%" /></CardContent></Card>
                    </Grid>
                  ))
                ) : (teams.length > 0 ? teams : mockTeams).length === 0 ? (
                  <Grid item xs={12}>
                    <Alert severity="info">No teams configured. Click "Create Team" to add one.</Alert>
                  </Grid>
                ) : (teams.length > 0 ? teams : mockTeams).map((team) => (
                  <Grid item xs={12} md={4} key={team.id}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                          <Avatar sx={{ bgcolor: '#6366f1', width: 48, height: 48 }}>
                            <GroupIcon />
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle1" fontWeight={600}>{team.name}</Typography>
                            <Typography variant="caption" color="textSecondary">
                              {team.members} members
                            </Typography>
                          </Box>
                        </Box>
                        <Divider sx={{ my: 1.5 }} />
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Box>
                            <Typography variant="caption" color="textSecondary">Team Lead</Typography>
                            <Typography variant="body2" fontWeight={500}>{team.lead}</Typography>
                          </Box>
                          <Box>
                            <IconButton size="small"><EditIcon fontSize="small" /></IconButton>
                            <IconButton size="small" color="error"><DeleteIcon fontSize="small" /></IconButton>
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </>
          )}

          {/* Activity Log Tab */}
          {activeTab === 3 && (
            <>
              <Typography variant="h6" sx={{ mb: 3 }}>Recent Activity</Typography>
              <List>
                {[
                  { user: 'John Doe', action: 'Updated role for Jane Smith', time: '2 minutes ago', type: 'role' },
                  { user: 'Admin', action: 'Invited new user: bob.new@company.com', time: '1 hour ago', type: 'invite' },
                  { user: 'Jane Smith', action: 'Created new team: Mobile', time: '3 hours ago', type: 'team' },
                  { user: 'John Doe', action: 'Reset password for Charlie Brown', time: '5 hours ago', type: 'password' },
                  { user: 'Admin', action: 'Deactivated user: old.user@company.com', time: 'Yesterday', type: 'deactivate' },
                  { user: 'Bob Wilson', action: 'Updated permissions for QA Engineer role', time: 'Yesterday', type: 'permission' }
                ].map((activity, idx) => (
                  <ListItem key={idx} sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
                    <ListItemIcon>
                      <Avatar sx={{ width: 32, height: 32, bgcolor: '#6366f1', fontSize: '0.8rem' }}>
                        {activity.user[0]}
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography variant="body2">
                          <strong>{activity.user}</strong> {activity.action}
                        </Typography>
                      }
                      secondary={activity.time}
                    />
                  </ListItem>
                ))}
              </List>
            </>
          )}
        </Box>
      </Paper>

      {/* Invite User Dialog */}
      <Dialog open={addUserDialogOpen} onClose={() => setAddUserDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PersonIcon sx={{ color: '#6366f1' }} />
            Invite New User
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Full Name"
                value={newUser.name}
                onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email Address"
                type="email"
                value={newUser.email}
                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                InputProps={{
                  startAdornment: <InputAdornment position="start"><EmailIcon /></InputAdornment>
                }}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                select
                label="Role"
                value={newUser.role}
                onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
              >
                {(roles.length > 0 ? roles : mockRoles).map(r => <MenuItem key={r.id} value={r.name}>{r.name}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                select
                label="Team"
                value={newUser.team}
                onChange={(e) => setNewUser({ ...newUser, team: e.target.value })}
              >
                {(teams.length > 0 ? teams : mockTeams).map(t => <MenuItem key={t.id} value={t.name}>{t.name}</MenuItem>)}
              </TextField>
            </Grid>
          </Grid>
          <Alert severity="info" sx={{ mt: 2 }}>
            An invitation email will be sent to the user with instructions to set up their account.
          </Alert>
          {inviting && <LinearProgress sx={{ mt: 2 }} />}
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setAddUserDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            startIcon={inviting ? <RefreshIcon /> : <SendIcon />}
            onClick={handleInviteUser}
            disabled={inviting || !newUser.email || !newUser.role}
            sx={{ bgcolor: '#6366f1' }}
          >
            {inviting ? 'Sending Invite...' : 'Send Invitation'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog open={editUserDialogOpen} onClose={() => setEditUserDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          {selectedUser && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField fullWidth label="Full Name" defaultValue={selectedUser.name} />
              </Grid>
              <Grid item xs={12}>
                <TextField fullWidth label="Email" defaultValue={selectedUser.email} disabled />
              </Grid>
              <Grid item xs={6}>
                <TextField fullWidth select label="Role" defaultValue={selectedUser.role}>
                  {(roles.length > 0 ? roles : mockRoles).map(r => <MenuItem key={r.id} value={r.name}>{r.name}</MenuItem>)}
                </TextField>
              </Grid>
              <Grid item xs={6}>
                <TextField fullWidth select label="Team" defaultValue={selectedUser.team}>
                  {(teams.length > 0 ? teams : mockTeams).map(t => <MenuItem key={t.id} value={t.name}>{t.name}</MenuItem>)}
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={<Switch defaultChecked={selectedUser.status === 'Active'} />}
                  label="Account Active"
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setEditUserDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" sx={{ bgcolor: '#6366f1' }}>Save Changes</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default UserManagementPreview
