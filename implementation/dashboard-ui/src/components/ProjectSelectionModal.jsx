import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Chip,
  alpha,
  Fade
} from '@mui/material';
import {
  Business as Building2,
  Error as AlertCircle,
  CheckCircle,
  TrendingUp,
  Group as Users,
  Close as CloseIcon
} from '@mui/icons-material';

const ProjectSelectionModal = ({ open, onProjectSelect, onClose }) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);

  useEffect(() => {
    if (open) {
      loadProjects();
    }
  }, [open]);

  const loadProjects = async () => {
    try {
      setLoading(true);
      console.log('🔄 ProjectSelectionModal: Loading projects...');

      const token = localStorage.getItem('auth_token');
      console.log('🔑 Token exists:', !!token);
      console.log('🔑 Token length:', token?.length);

      if (!token) {
        console.error('❌ No auth token found');
        setError('Authentication required. Please log in again.');
        setLoading(false);
        return;
      }

      console.log('🌐 Calling API:', 'http://localhost:5006/api/projects');

      const response = await fetch('http://localhost:5006/api/projects', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('📡 API Response status:', response.status);
      console.log('📡 API Response ok:', response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ API Error:', errorText);
        throw new Error(`Failed to load projects: ${response.status} ${errorText}`);
      }

      const data = await response.json();
      console.log('✅ Projects loaded:', data);

      setProjects(data.projects || []);
      setLoading(false);
    } catch (err) {
      console.error('❌ Error loading projects:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const handleProjectClick = (project) => {
    setSelectedProject(project);
  };

  const handleContinue = () => {
    if (selectedProject) {
      // Store project in localStorage
      localStorage.setItem('current_project_id', selectedProject.id);
      localStorage.setItem('current_project_slug', selectedProject.slug);

      // Call the onProjectSelect callback
      onProjectSelect(selectedProject);
    }
  };

  const getRoleBadgeClass = (role) => {
    const roleColors = {
      'project_owner': '#10b981',  // Emerald for owner
      'project_admin': '#3b82f6',  // Blue for admin
      'developer': '#10b981',      // Emerald for developer
      'viewer': '#fbbf24',         // Amber for viewer
      'guest': '#9ca3af'           // Gray for guest
    };
    return roleColors[role] || '#64748b';
  };

  const getRoleDisplayName = (role) => {
    const nameMap = {
      'project_owner': 'Owner',
      'project_admin': 'Admin',
      'developer': 'Developer',
      'viewer': 'Viewer',
      'guest': 'Guest'
    };
    return nameMap[role] || role;
  };

  return (
    <Dialog
      open={open}
      maxWidth="md"
      fullWidth
      onClose={onClose}
      PaperProps={{
        sx: {
          borderRadius: 4,
          background: 'linear-gradient(135deg, rgba(17, 24, 39, 0.98) 0%, rgba(31, 41, 55, 0.98) 50%, rgba(17, 24, 39, 0.98) 100%)',
          backdropFilter: 'blur(20px)',
          border: '1.5px solid',
          borderColor: alpha('#10b981', 0.3),
          boxShadow: '0 25px 80px rgba(0,0,0,0.6), 0 0 40px rgba(16, 185, 129, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.05)'
        }
      }}
    >
      <DialogTitle>
        {/* Close button */}
        <Button
          onClick={onClose}
          sx={{
            position: 'absolute',
            right: 8,
            top: 8,
            minWidth: 'auto',
            width: 40,
            height: 40,
            borderRadius: '50%',
            color: '#9ca3af',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              bgcolor: alpha('#10b981', 0.15),
              color: '#10b981',
              transform: 'rotate(90deg)'
            }
          }}
        >
          <CloseIcon />
        </Button>

        <Box sx={{ textAlign: 'center', pt: 2 }}>
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #10b981, #14b8a6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mx: 'auto',
              mb: 2,
              boxShadow: '0 0 30px rgba(16, 185, 129, 0.6), inset 0 2px 8px rgba(255, 255, 255, 0.15)',
              border: '2px solid rgba(16, 185, 129, 0.3)'
            }}
          >
            <Building2 sx={{ fontSize: 40, color: 'white', filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3))' }} />
          </Box>
          <Typography variant="h5" fontWeight={700} sx={{ color: '#f9fafb', mb: 1, textShadow: '0 2px 8px rgba(0, 0, 0, 0.4)' }}>
            Select Your Project
          </Typography>
          <Typography variant="body2" sx={{ color: '#9ca3af', fontSize: '0.95rem' }}>
            Choose which project you want to work on
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ px: 3, pb: 3 }}>
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
            <CircularProgress sx={{ color: '#10b981' }} />
            <Typography sx={{ ml: 2, color: '#9ca3af', fontWeight: 500 }}>Loading projects...</Typography>
          </Box>
        )}

        {error && (
          <Box>
            <Alert
              severity="error"
              sx={{
                borderRadius: 2,
                bgcolor: alpha('#ef4444', 0.1),
                color: '#ef4444',
                border: '1px solid',
                borderColor: alpha('#ef4444', 0.3)
              }}
            >
              {error}
            </Alert>
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center', gap: 2 }}>
              <Button
                variant="outlined"
                onClick={onClose}
                sx={{
                  px: 4,
                  py: 1.5,
                  borderRadius: 3,
                  borderColor: alpha('#10b981', 0.5),
                  color: '#10b981',
                  fontSize: '1rem',
                  fontWeight: 600,
                  textTransform: 'none',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    borderColor: '#10b981',
                    bgcolor: alpha('#10b981', 0.1),
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 12px rgba(16, 185, 129, 0.25)'
                  }
                }}
              >
                Go Back to Login
              </Button>
              <Button
                variant="contained"
                onClick={loadProjects}
                sx={{
                  px: 4,
                  py: 1.5,
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #10b981, #14b8a6)',
                  fontSize: '1rem',
                  fontWeight: 600,
                  textTransform: 'none',
                  boxShadow: '0 4px 15px rgba(16, 185, 129, 0.4)',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #14b8a6, #10b981)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 6px 20px rgba(16, 185, 129, 0.5)'
                  }
                }}
              >
                Try Again
              </Button>
            </Box>
          </Box>
        )}

        {!loading && !error && projects.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <AlertCircle sx={{ fontSize: 64, color: '#64748b', mb: 2 }} />
            <Typography variant="h6" sx={{ color: '#94a3b8', mb: 1 }}>
              No Projects Available
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748b' }}>
              Please contact your administrator to get access to a project
            </Typography>
          </Box>
        )}

        {!loading && !error && projects.length > 0 && (
          <Fade in timeout={500}>
            <Box>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                {projects.map((project) => (
                  <Grid item xs={12} key={project.id}>
                    <Card
                      elevation={0}
                      onClick={() => handleProjectClick(project)}
                      sx={{
                        cursor: 'pointer',
                        borderRadius: 3,
                        background: selectedProject?.id === project.id
                          ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(20, 184, 166, 0.12) 100%)'
                          : 'rgba(255, 255, 255, 0.03)',
                        backdropFilter: 'blur(12px)',
                        border: '2px solid',
                        borderColor: selectedProject?.id === project.id
                          ? '#10b981'
                          : alpha('#64748b', 0.25),
                        transition: 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)',
                        '&:hover': {
                          borderColor: '#10b981',
                          background: alpha('#10b981', 0.08),
                          transform: 'translateX(4px) translateY(-2px)',
                          boxShadow: '0 8px 24px rgba(16, 185, 129, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.05)'
                        }
                      }}
                    >
                      <CardContent sx={{ p: 2.5 }}>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, flex: 1 }}>
                            <Box
                              sx={{
                                width: 48,
                                height: 48,
                                borderRadius: 2,
                                background: 'linear-gradient(135deg, #10b981, #14b8a6)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                flexShrink: 0,
                                boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3), inset 0 1px 4px rgba(255, 255, 255, 0.2)',
                                border: '1px solid rgba(16, 185, 129, 0.3)'
                              }}
                            >
                              <Building2 sx={{ color: 'white', fontSize: 24, filter: 'drop-shadow(0 2px 3px rgba(0, 0, 0, 0.3))' }} />
                            </Box>
                            <Box sx={{ flex: 1 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                <Typography variant="h6" fontWeight={600} sx={{ color: '#f9fafb', textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)' }}>
                                  {project.name}
                                </Typography>
                                {selectedProject?.id === project.id && (
                                  <CheckCircle sx={{ color: '#10b981', fontSize: 20, filter: 'drop-shadow(0 0 8px rgba(16, 185, 129, 0.6))' }} />
                                )}
                              </Box>
                              <Typography variant="caption" sx={{ color: '#10b981', display: 'block', mb: 1, fontFamily: '"Courier New", monospace', opacity: 0.8 }}>
                                /{project.slug}
                              </Typography>
                              {project.description && (
                                <Typography variant="body2" sx={{ color: '#9ca3af', mb: 1, lineHeight: 1.6 }}>
                                  {project.description}
                                </Typography>
                              )}
                              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                                <Chip
                                  label={getRoleDisplayName(project.my_role)}
                                  size="small"
                                  sx={{
                                    bgcolor: alpha(getRoleBadgeClass(project.my_role), 0.2),
                                    color: getRoleBadgeClass(project.my_role),
                                    borderColor: getRoleBadgeClass(project.my_role),
                                    border: '1px solid',
                                    fontWeight: 600
                                  }}
                                />
                                {project.recent_failure_count > 0 && (
                                  <Chip
                                    icon={<AlertCircle sx={{ fontSize: 14 }} />}
                                    label={`${project.recent_failure_count} failures`}
                                    size="small"
                                    sx={{
                                      bgcolor: alpha('#ef4444', 0.1),
                                      color: '#ef4444',
                                      borderColor: alpha('#ef4444', 0.3),
                                      border: '1px solid'
                                    }}
                                  />
                                )}
                              </Box>
                            </Box>
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  size="large"
                  disabled={!selectedProject}
                  onClick={handleContinue}
                  sx={{
                    px: 6,
                    py: 1.5,
                    borderRadius: 3,
                    background: selectedProject
                      ? 'linear-gradient(135deg, #10b981, #14b8a6)'
                      : alpha('#64748b', 0.3),
                    fontSize: '1rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    letterSpacing: '0.3px',
                    boxShadow: selectedProject ? '0 4px 20px rgba(16, 185, 129, 0.5)' : 'none',
                    transition: 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      background: selectedProject
                        ? 'linear-gradient(135deg, #14b8a6, #10b981)'
                        : alpha('#64748b', 0.3),
                      boxShadow: selectedProject ? '0 6px 24px rgba(16, 185, 129, 0.6)' : 'none',
                      transform: selectedProject ? 'translateY(-2px)' : 'none'
                    },
                    '&:disabled': {
                      color: '#64748b'
                    }
                  }}
                >
                  Continue to Dashboard
                </Button>
              </Box>
            </Box>
          </Fade>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default ProjectSelectionModal;
