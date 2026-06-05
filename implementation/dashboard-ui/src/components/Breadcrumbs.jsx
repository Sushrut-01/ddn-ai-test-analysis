import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Box, Breadcrumbs as MuiBreadcrumbs, Link, Typography, Chip } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';

// Route to breadcrumb label mapping
const routeLabels = {
    '': 'AI Completed',
    'dashboard': 'AI Completed',
    'pipeline': 'Pipeline Status',
    'services': 'Services',
    'failures': 'Failure Details',
    'analytics': 'Analytics',
    'manual-trigger': 'Manual Trigger',
    'bulk-trigger': 'Pending Analysis',
    'approval-flow': 'Approval Flow',
    'jira-bugs': 'Jira Bugs',
    'pr-workflow': 'PR Workflow',
    'ai-chatbot': 'AI Chatbot',
    'test-generator': 'Test Generator',
    'knowledge': 'Knowledge Base',
    'users': 'Users',
    'config': 'Configuration',
    'notifications': 'Notifications',
    'audit-log': 'Audit Log'
};

// Section grouping for context
const routeSections = {
    'dashboard': 'Dashboard',
    'pipeline': 'Dashboard',
    'services': 'Dashboard',
    'failures': 'Analysis',
    'analytics': 'Analysis',
    'manual-trigger': 'Analysis',
    'bulk-trigger': 'Analysis',
    'approval-flow': 'Analysis',
    'jira-bugs': 'Integrations',
    'pr-workflow': 'Integrations',
    'ai-chatbot': 'AI Tools',
    'test-generator': 'AI Tools',
    'knowledge': 'AI Tools',
    'users': 'Administration',
    'config': 'Administration',
    'notifications': 'Administration',
    'audit-log': 'Administration'
};

const AppBreadcrumbs = () => {
    const location = useLocation();
    const navigate = useNavigate();

    // Parse current path
    const pathParts = location.pathname.split('/').filter(part => part);

    // Don't show breadcrumbs on login/auth pages
    if (['login', 'signup', 'forgot-password'].includes(pathParts[0])) {
        return null;
    }

    // Build breadcrumb items
    const breadcrumbs = [];

    // Always start with Home/Dashboard
    breadcrumbs.push({
        label: 'Dashboard',
        path: '/',
        isHome: true
    });

    // Add section if not Dashboard
    if (pathParts.length > 0 && pathParts[0] !== 'dashboard') {
        const section = routeSections[pathParts[0]];
        if (section && section !== 'Dashboard') {
            breadcrumbs.push({
                label: section,
                path: null, // Non-clickable section header
                isSection: true
            });
        }
    }

    // Add current page and any sub-pages
    let currentPath = '';
    pathParts.forEach((part, index) => {
        currentPath += `/${part}`;
        const label = routeLabels[part] || (part.length < 20 ? `#${part}` : 'Details');

        breadcrumbs.push({
            label,
            path: currentPath,
            isCurrent: index === pathParts.length - 1
        });
    });

    return (
        <Box
            sx={{
                py: 1,
                px: 2,
                bgcolor: 'rgba(0,0,0,0.02)',
                borderBottom: '1px solid rgba(0,0,0,0.06)'
            }}
        >
            <MuiBreadcrumbs
                separator={<NavigateNextIcon fontSize="small" sx={{ color: 'text.disabled' }} />}
                aria-label="breadcrumb"
            >
                {breadcrumbs.map((crumb, index) => {
                    if (crumb.isHome) {
                        return (
                            <Link
                                key={index}
                                underline="hover"
                                color="inherit"
                                onClick={() => navigate(crumb.path)}
                                sx={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    cursor: 'pointer',
                                    '&:hover': { color: 'primary.main' }
                                }}
                            >
                                <HomeIcon sx={{ mr: 0.5, fontSize: 18 }} />
                                {crumb.label}
                            </Link>
                        );
                    }

                    if (crumb.isSection) {
                        return (
                            <Chip
                                key={index}
                                label={crumb.label}
                                size="small"
                                sx={{
                                    height: 20,
                                    fontSize: '0.7rem',
                                    bgcolor: 'rgba(0,0,0,0.06)',
                                    color: 'text.secondary'
                                }}
                            />
                        );
                    }

                    if (crumb.isCurrent) {
                        return (
                            <Typography
                                key={index}
                                color="primary"
                                fontWeight={600}
                                sx={{ fontSize: '0.875rem' }}
                            >
                                {crumb.label}
                            </Typography>
                        );
                    }

                    return (
                        <Link
                            key={index}
                            underline="hover"
                            color="inherit"
                            onClick={() => navigate(crumb.path)}
                            sx={{
                                cursor: 'pointer',
                                '&:hover': { color: 'primary.main' }
                            }}
                        >
                            {crumb.label}
                        </Link>
                    );
                })}
            </MuiBreadcrumbs>
        </Box>
    );
};

export default AppBreadcrumbs;
