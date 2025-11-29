import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Button,
    Chip,
    Grid,
    IconButton,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    CircularProgress,
    Alert,
    Tooltip,
    Collapse
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import RefreshIcon from '@mui/icons-material/Refresh';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import StorageIcon from '@mui/icons-material/Storage';
import CloudIcon from '@mui/icons-material/Cloud';
import SettingsIcon from '@mui/icons-material/Settings';
import WorkflowIcon from '@mui/icons-material/AccountTree';
import BugReportIcon from '@mui/icons-material/BugReport';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

const ServiceControlModern = () => {
    const [services, setServices] = useState({});
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState('info');
    const [hiddenServices, setHiddenServices] = useState(() => {
        const saved = localStorage.getItem('hiddenServices');
        return saved ? JSON.parse(saved) : [];
    });
    const [showHidden, setShowHidden] = useState(false);

    const API_URL = 'http://localhost:5007/api/services';

    const fetchStatus = async () => {
        try {
            const response = await fetch(`${API_URL}/status`);
            if (!response.ok) throw new Error('Service Manager API not available');
            const data = await response.json();
            setServices(data);
            setMessage('');
        } catch (error) {
            setMessage('Service Manager API not running (start service_manager_api.py)');
            setMessageType('warning');
            setServices({});
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleAction = async (action, serviceId = null) => {
        setLoading(true);
        const actionLabel = serviceId ? `${action} ${serviceId}` : `${action} all services`;
        setMessage(`${actionLabel}...`);
        setMessageType('info');

        try {
            const url = serviceId ? `${API_URL}/${action}/${serviceId}` : `${API_URL}/${action}-all`;
            const response = await fetch(url, { method: 'POST' });
            const data = await response.json();
            setMessage(data.message || `${actionLabel} completed`);
            setMessageType('success');
            await new Promise(resolve => setTimeout(resolve, 2000));
            fetchStatus();
        } catch (error) {
            setMessage(`Error: ${error.message}`);
            setMessageType('error');
        } finally {
            setLoading(false);
        }
    };

    const handleRemoveService = (serviceId, serviceName) => {
        const updated = [...hiddenServices, serviceId];
        setHiddenServices(updated);
        localStorage.setItem('hiddenServices', JSON.stringify(updated));
    };

    const handleShowService = (serviceId) => {
        const updated = hiddenServices.filter(id => id !== serviceId);
        setHiddenServices(updated);
        localStorage.setItem('hiddenServices', JSON.stringify(updated));
    };

    const openExternalService = (url) => {
        window.open(url, '_blank');
    };

    const visibleServices = Object.entries(services).filter(([id]) => !hiddenServices.includes(id));
    const hiddenServicesData = Object.entries(services).filter(([id]) => hiddenServices.includes(id));
    const runningCount = visibleServices.filter(([_, s]) => s.running).length;
    const totalCount = visibleServices.length;

    const quickLinks = [
        { name: 'MongoDB Atlas', url: 'https://cloud.mongodb.com/', color: '#4caf50', icon: <StorageIcon /> },
        { name: 'Jira', url: 'https://id.atlassian.com/login', color: '#0052CC', icon: <BugReportIcon /> },
        { name: 'Pinecone', url: 'https://app.pinecone.io/', color: '#00C9A7', icon: <CloudIcon /> },
        { name: 'Jenkins', url: 'http://localhost:8081', color: '#D24939', icon: <SettingsIcon /> },
        { name: 'n8n', url: 'http://localhost:5678', color: '#EA4B71', icon: <WorkflowIcon /> },
    ];

    return (
        <Box>
            {/* Header */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Box>
                    <Typography variant="h6" fontWeight="bold" color="#1e293b">
                        Service Control Panel
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                        {totalCount > 0 ? `${runningCount}/${totalCount} services running` : 'Checking services...'}
                    </Typography>
                </Box>
                <Box display="flex" gap={1}>
                    <Button
                        variant="contained"
                        size="small"
                        startIcon={loading ? <CircularProgress size={16} color="inherit" /> : <PlayArrowIcon />}
                        onClick={() => handleAction('start')}
                        disabled={loading}
                        sx={{
                            bgcolor: '#10b981',
                            '&:hover': { bgcolor: '#059669' },
                            borderRadius: 2,
                            textTransform: 'none',
                            fontWeight: 600
                        }}
                    >
                        Start All
                    </Button>
                    <Button
                        variant="contained"
                        size="small"
                        startIcon={<StopIcon />}
                        onClick={() => handleAction('stop')}
                        disabled={loading}
                        sx={{
                            bgcolor: '#ef4444',
                            '&:hover': { bgcolor: '#dc2626' },
                            borderRadius: 2,
                            textTransform: 'none',
                            fontWeight: 600
                        }}
                    >
                        Stop All
                    </Button>
                    <Button
                        variant="outlined"
                        size="small"
                        startIcon={<RefreshIcon />}
                        onClick={() => handleAction('restart')}
                        disabled={loading}
                        sx={{
                            borderRadius: 2,
                            textTransform: 'none',
                            fontWeight: 600
                        }}
                    >
                        Restart
                    </Button>
                </Box>
            </Box>

            {/* Quick Links */}
            <Box mb={3}>
                <Typography variant="body2" color="textSecondary" mb={1.5} fontWeight={500}>
                    Quick Access
                </Typography>
                <Box display="flex" gap={1.5} flexWrap="wrap">
                    {quickLinks.map((link) => (
                        <Button
                            key={link.name}
                            variant="contained"
                            size="small"
                            startIcon={link.icon}
                            endIcon={<OpenInNewIcon sx={{ fontSize: 14 }} />}
                            onClick={() => openExternalService(link.url)}
                            sx={{
                                bgcolor: link.color,
                                '&:hover': { bgcolor: alpha(link.color, 0.85) },
                                borderRadius: 2,
                                textTransform: 'none',
                                fontWeight: 500,
                                fontSize: '0.8rem',
                                py: 0.75
                            }}
                        >
                            {link.name}
                        </Button>
                    ))}
                </Box>
            </Box>

            {/* Status Message */}
            {message && (
                <Alert
                    severity={messageType}
                    sx={{ mb: 2, borderRadius: 2 }}
                    onClose={() => setMessage('')}
                >
                    {message}
                </Alert>
            )}

            {/* Services Table */}
            {totalCount > 0 ? (
                <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 3, border: '1px solid #e2e8f0' }}>
                    <Table size="small">
                        <TableHead>
                            <TableRow sx={{ bgcolor: '#f8fafc' }}>
                                <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Service</TableCell>
                                <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Port</TableCell>
                                <TableCell align="center" sx={{ fontWeight: 600, color: '#64748b' }}>Status</TableCell>
                                <TableCell align="right" sx={{ fontWeight: 600, color: '#64748b' }}>Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {visibleServices.map(([id, service]) => (
                                <TableRow key={id} sx={{ '&:hover': { bgcolor: '#f8fafc' } }}>
                                    <TableCell>
                                        <Typography variant="body2" fontWeight={500}>{service.name}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Chip
                                            label={service.port}
                                            size="small"
                                            sx={{
                                                bgcolor: '#f1f5f9',
                                                fontFamily: 'monospace',
                                                fontWeight: 600,
                                                fontSize: '0.75rem'
                                            }}
                                        />
                                    </TableCell>
                                    <TableCell align="center">
                                        <Chip
                                            label={service.running ? 'Running' : 'Stopped'}
                                            size="small"
                                            sx={{
                                                bgcolor: service.running ? '#dcfce7' : '#fee2e2',
                                                color: service.running ? '#166534' : '#991b1b',
                                                fontWeight: 600,
                                                fontSize: '0.7rem'
                                            }}
                                        />
                                    </TableCell>
                                    <TableCell align="right">
                                        <Box display="flex" gap={0.5} justifyContent="flex-end">
                                            {service.running ? (
                                                <Button
                                                    size="small"
                                                    onClick={() => handleAction('stop', id)}
                                                    disabled={loading}
                                                    sx={{
                                                        minWidth: 'auto',
                                                        px: 1.5,
                                                        color: '#ef4444',
                                                        fontSize: '0.75rem',
                                                        textTransform: 'none'
                                                    }}
                                                >
                                                    Stop
                                                </Button>
                                            ) : (
                                                <Button
                                                    size="small"
                                                    onClick={() => handleAction('start', id)}
                                                    disabled={loading}
                                                    sx={{
                                                        minWidth: 'auto',
                                                        px: 1.5,
                                                        color: '#10b981',
                                                        fontSize: '0.75rem',
                                                        textTransform: 'none'
                                                    }}
                                                >
                                                    Start
                                                </Button>
                                            )}
                                            <Tooltip title="Hide service">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => handleRemoveService(id, service.name)}
                                                    sx={{ color: '#94a3b8' }}
                                                >
                                                    <VisibilityOffIcon fontSize="small" />
                                                </IconButton>
                                            </Tooltip>
                                        </Box>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            ) : (
                <Paper
                    elevation={0}
                    sx={{
                        p: 3,
                        textAlign: 'center',
                        borderRadius: 3,
                        bgcolor: '#f8fafc',
                        border: '1px dashed #cbd5e1'
                    }}
                >
                    <Typography color="textSecondary">
                        No services detected. Start the Service Manager API first.
                    </Typography>
                </Paper>
            )}

            {/* Hidden Services */}
            {hiddenServicesData.length > 0 && (
                <Box mt={2}>
                    <Button
                        size="small"
                        startIcon={showHidden ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        onClick={() => setShowHidden(!showHidden)}
                        sx={{ color: '#64748b', textTransform: 'none' }}
                    >
                        {hiddenServicesData.length} hidden service(s)
                    </Button>
                    <Collapse in={showHidden}>
                        <Box mt={1} display="flex" gap={1} flexWrap="wrap">
                            {hiddenServicesData.map(([id, service]) => (
                                <Chip
                                    key={id}
                                    label={service.name}
                                    size="small"
                                    onDelete={() => handleShowService(id)}
                                    deleteIcon={<VisibilityIcon fontSize="small" />}
                                    sx={{ bgcolor: '#f1f5f9' }}
                                />
                            ))}
                        </Box>
                    </Collapse>
                </Box>
            )}
        </Box>
    );
};

export default ServiceControlModern;
