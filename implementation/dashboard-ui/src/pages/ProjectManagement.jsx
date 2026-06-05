import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Button,
  IconButton,
  Chip,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Skeleton,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Menu,
  MenuItem,
  Alert,
  Snackbar
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import {
  Business,
  Add,
  Settings,
  Group,
  TrendingUp,
  Error as ErrorIcon,
  CheckCircle,
  MoreVert,
  Edit,
  Delete,
  Visibility,
  Code,
  Security,
  Star,
  Refresh
} from '@mui/icons-material';
import { projectAPI } from '../services/api';
import { useColorTheme } from '../theme/ThemeContext';

const ProjectManagement = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: ''
  });
  const navigate = useNavigate();
  const { theme } = useColorTheme();

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const response = await projectAPI.getAll();
      setProjects(response.projects || []);
    } catch (error) {
      console.error('Error loading projects:', error);
      showSnackbar('Failed to load projects', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async () => {
    try {
      await projectAPI.create(formData);
      showSnackbar('Project created successfully!', 'success');
      setCreateDialogOpen(false);
      setFormData({ name: '', slug: '', description: '' });
      loadProjects();
    } catch (error) {
      showSnackbar('Failed to create project', 'error');
    }
  };

  const handleUpdateProject = async () => {
    try {
      await projectAPI.update(selectedProject.id, formData);
      showSnackbar('Project updated successfully!', 'success');
      setEditDialogOpen(false);
      setSelectedProject(null);
      loadProjects();
    } catch (error) {
      showSnackbar('Failed to update project', 'error');
    }
  };

  const handleSelectProject = (project) => {
    localStorage.setItem('current_project_id', project.id);
    localStorage.setItem('current_project_slug', project.slug);
    showSnackbar(`Switched to ${project.name}`, 'success');
    setTimeout(() => window.location.reload(), 1000);
  };

  const openEditDialog = (project) => {
    setSelectedProject(project);
    setFormData({
      name: project.name,
      slug: project.slug,
      description: project.description || ''
    });
    setEditDialogOpen(true);
    setMenuAnchor(null);
  };

  const showSnackbar = (message, severity) => {
    setSnackbar({ open: true, message, severity });
  };

  const getRoleBadgeColor = (role) => {
    const colors = {
      project_owner: '#9333ea',
      project_admin: '#3b82f6',
      developer: '#10b981',
      viewer: '#f59e0b',
      guest: '#6b7280'
    };
    return colors[role] || '#6b7280';
  };

  const getRoleDisplayName = (role) => {
    const names = {
      project_owner: 'Owner',
      project_admin: 'Admin',
      developer: 'Developer',
      viewer: 'Viewer',
      guest: 'Guest'
    };
    return names[role] || role;
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight="bold" sx={{ color: '#1a1a2e', letterSpacing: '-0.5px' }}>
            Project Management
          </Typography>
          <Typography variant="body2" color="textSecondary" mt={0.5}>
            Manage your projects, teams, and configurations
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadProjects}
            sx={{
              borderRadius: 3,
              textTransform: 'none',
              px: 3
            }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{
              borderRadius: 3,
              textTransform: 'none',
              px: 3,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)'
              }
            }}
          >
            Create Project
          </Button>
        </Box>
      </Box>

      {/* Stats Overview */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card
            elevation={0}
            sx={{
              borderRadius: 4,
              background: 'rgba(255, 255, 255, 0.85)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.4)',
              boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.1)'
            }}
          >
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Total Projects
                  </Typography>
                  <Typography variant="h3" fontWeight="bold">
                    {loading ? <Skeleton width={60} /> : projects.length}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 3,
                    bgcolor: alpha('#667eea', 0.1),
                    color: '#667eea'
                  }}
                >
                  <Business fontSize="large" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            elevation={0}
            sx={{
              borderRadius: 4,
              background: 'rgba(255, 255, 255, 0.85)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.4)',
              boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.1)'
            }}
          >
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Active Projects
                  </Typography>
                  <Typography variant="h3" fontWeight="bold">
                    {loading ? (
                      <Skeleton width={60} />
                    ) : (
                      projects.filter(p => p.status === 'active').length
                    )}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 3,
                    bgcolor: alpha('#10b981', 0.1),
                    color: '#10b981'
                  }}
                >
                  <CheckCircle fontSize="large" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            elevation={0}
            sx={{
              borderRadius: 4,
              background: 'rgba(255, 255, 255, 0.85)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.4)',
              boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.1)'
            }}
          >
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Team Members
                  </Typography>
                  <Typography variant="h3" fontWeight="bold">
                    {loading ? (
                      <Skeleton width={60} />
                    ) : (
                      projects.reduce((sum, p) => sum + (p.team_size || 0), 0)
                    )}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 3,
                    bgcolor: alpha('#3b82f6', 0.1),
                    color: '#3b82f6'
                  }}
                >
                  <Group fontSize="large" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            elevation={0}
            sx={{
              borderRadius: 4,
              background: 'rgba(255, 255, 255, 0.85)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.4)',
              boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.1)'
            }}
          >
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Total Failures
                  </Typography>
                  <Typography variant="h3" fontWeight="bold">
                    {loading ? (
                      <Skeleton width={60} />
                    ) : (
                      projects.reduce((sum, p) => sum + (p.failure_count || 0), 0)
                    )}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 3,
                    bgcolor: alpha('#ef4444', 0.1),
                    color: '#ef4444'
                  }}
                >
                  <ErrorIcon fontSize="large" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Projects Grid */}
      <Grid container spacing={3}>
        {loading ? (
          [...Array(3)].map((_, index) => (
            <Grid item xs={12} md={6} lg={4} key={index}>
              <Card
                elevation={0}
                sx={{
                  borderRadius: 4,
                  background: 'rgba(255, 255, 255, 0.85)',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255, 255, 255, 0.4)'
                }}
              >
                <CardContent>
                  <Skeleton variant="text" width="60%" height={40} />
                  <Skeleton variant="text" width="80%" />
                  <Skeleton variant="text" width="40%" />
                  <Box mt={2}>
                    <Skeleton variant="rectangular" height={80} sx={{ borderRadius: 2 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))
        ) : projects.length === 0 ? (
          <Grid item xs={12}>
            <Card
              elevation={0}
              sx={{
                borderRadius: 4,
                background: 'rgba(255, 255, 255, 0.85)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.4)',
                textAlign: 'center',
                py: 8
              }}
            >
              <Business sx={{ fontSize: 80, color: '#9ca3af', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No Projects Yet
              </Typography>
              <Typography variant="body2" color="textSecondary" mb={3}>
                Create your first project to get started
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setCreateDialogOpen(true)}
                sx={{
                  borderRadius: 3,
                  textTransform: 'none',
                  px: 4,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                }}
              >
                Create Project
              </Button>
            </Card>
          </Grid>
        ) : (
          projects.map((project) => (
            <Grid item xs={12} md={6} lg={4} key={project.id}>
              <Card
                elevation={0}
                sx={{
                  height: '100%',
                  borderRadius: 4,
                  background: 'rgba(255, 255, 255, 0.85)',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255, 255, 255, 0.4)',
                  boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.1)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 12px 40px 0 rgba(31, 38, 135, 0.15)'
                  }
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  {/* Header */}
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Box display="flex" alignItems="center" gap={1.5}>
                      <Avatar
                        sx={{
                          bgcolor: alpha(getRoleBadgeColor(project.user_role), 0.1),
                          color: getRoleBadgeColor(project.user_role),
                          width: 48,
                          height: 48
                        }}
                      >
                        <Business />
                      </Avatar>
                      <Box>
                        <Typography variant="h6" fontWeight="bold">
                          {project.name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          /{project.slug}
                        </Typography>
                      </Box>
                    </Box>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        setSelectedProject(project);
                        setMenuAnchor(e.currentTarget);
                      }}
                    >
                      <MoreVert />
                    </IconButton>
                  </Box>

                  {/* Description */}
                  <Typography
                    variant="body2"
                    color="textSecondary"
                    sx={{
                      mb: 2,
                      minHeight: 40,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical'
                    }}
                  >
                    {project.description || 'No description provided'}
                  </Typography>

                  <Divider sx={{ my: 2 }} />

                  {/* Stats */}
                  <Grid container spacing={2} mb={2}>
                    <Grid item xs={4}>
                      <Box textAlign="center">
                        <Typography variant="h6" fontWeight="bold" color="primary">
                          {project.team_size || 0}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Team
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={4}>
                      <Box textAlign="center">
                        <Typography variant="h6" fontWeight="bold" color="error">
                          {project.failure_count || 0}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Failures
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={4}>
                      <Box textAlign="center">
                        <Chip
                          label={project.status}
                          size="small"
                          color={project.status === 'active' ? 'success' : 'default'}
                          sx={{ fontWeight: 600 }}
                        />
                      </Box>
                    </Grid>
                  </Grid>

                  {/* Role & Jira */}
                  <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                    <Chip
                      label={getRoleDisplayName(project.user_role)}
                      size="small"
                      sx={{
                        bgcolor: alpha(getRoleBadgeColor(project.user_role), 0.1),
                        color: getRoleBadgeColor(project.user_role),
                        fontWeight: 600,
                        fontSize: '0.75rem'
                      }}
                    />
                    {project.jira_project_key && (
                      <Chip
                        label={`Jira: ${project.jira_project_key}`}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.75rem' }}
                      />
                    )}
                  </Box>

                  {/* Actions */}
                  <Box display="flex" gap={1}>
                    <Button
                      fullWidth
                      variant="contained"
                      startIcon={<Visibility />}
                      onClick={() => handleSelectProject(project)}
                      sx={{
                        borderRadius: 2,
                        textTransform: 'none',
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)'
                        }
                      }}
                    >
                      Switch To
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={() => openEditDialog(project)}
                      sx={{
                        borderRadius: 2,
                        textTransform: 'none',
                        minWidth: 'auto',
                        px: 2
                      }}
                    >
                      <Settings fontSize="small" />
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))
        )}
      </Grid>

      {/* Create Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 4,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)'
          }
        }}
      >
        <DialogTitle>
          <Typography variant="h6" fontWeight="bold">
            Create New Project
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={1}>
            <TextField
              label="Project Name"
              fullWidth
              value={formData.name}
              onChange={(e) => {
                const name = e.target.value;
                const slug = name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
                setFormData({ ...formData, name, slug });
              }}
              sx={{ borderRadius: 2 }}
            />
            <TextField
              label="Project Slug"
              fullWidth
              value={formData.slug}
              onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
              helperText="URL-friendly identifier (e.g., ddn-project)"
              sx={{ borderRadius: 2 }}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              sx={{ borderRadius: 2 }}
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setCreateDialogOpen(false)} sx={{ textTransform: 'none' }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleCreateProject}
            disabled={!formData.name || !formData.slug}
            sx={{
              textTransform: 'none',
              borderRadius: 2,
              px: 3,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            }}
          >
            Create Project
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 4,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)'
          }
        }}
      >
        <DialogTitle>
          <Typography variant="h6" fontWeight="bold">
            Edit Project
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={1}>
            <TextField
              label="Project Name"
              fullWidth
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              sx={{ borderRadius: 2 }}
            />
            <TextField
              label="Project Slug"
              fullWidth
              value={formData.slug}
              disabled
              helperText="Slug cannot be changed"
              sx={{ borderRadius: 2 }}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              sx={{ borderRadius: 2 }}
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setEditDialogOpen(false)} sx={{ textTransform: 'none' }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleUpdateProject}
            sx={{
              textTransform: 'none',
              borderRadius: 2,
              px: 3,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            }}
          >
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={() => setMenuAnchor(null)}
        PaperProps={{
          sx: {
            borderRadius: 2,
            mt: 1,
            minWidth: 180
          }
        }}
      >
        <MenuItem onClick={() => openEditDialog(selectedProject)}>
          <Edit fontSize="small" sx={{ mr: 1 }} />
          Edit Project
        </MenuItem>
        <MenuItem onClick={() => handleSelectProject(selectedProject)}>
          <Visibility fontSize="small" sx={{ mr: 1 }} />
          Switch To
        </MenuItem>
        <MenuItem onClick={() => navigate(`/projects/${selectedProject?.id}/config`)}>
          <Settings fontSize="small" sx={{ mr: 1 }} />
          Configuration
        </MenuItem>
      </Menu>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ borderRadius: 2 }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default ProjectManagement;
