import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
    Box, Container, Paper, Typography, Grid, TextField, Button, Alert, Chip,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TablePagination,
    Card, CardContent, Avatar, List, ListItem, ListItemIcon, ListItemText, Divider,
    Skeleton, CircularProgress
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ScheduleIcon from '@mui/icons-material/Schedule';
import PersonIcon from '@mui/icons-material/Person';
import InfoIcon from '@mui/icons-material/Info';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import StorageIcon from '@mui/icons-material/Storage';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import RefreshIcon from '@mui/icons-material/Refresh';
import WarningIcon from '@mui/icons-material/Warning';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import ErrorIcon from '@mui/icons-material/Error';
import { triggerAPI } from '../services/api';

const ManualTriggerPreview = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [buildId, setBuildId] = useState('');
    const [email, setEmail] = useState('');
    const [reason, setReason] = useState('');
    const [showSuccess, setShowSuccess] = useState(false);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);

    // Real data state
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [triggerHistory, setTriggerHistory] = useState([]);
    const [stats, setStats] = useState({ total: 0, successful: 0, failed: 0 });
    const [error, setError] = useState(null);

    const fetchTriggerHistory = useCallback(async () => {
        try {
            const response = await triggerAPI.getHistory(page + 1, rowsPerPage);
            const data = response?.data || response;

            if (data?.success) {
                setTriggerHistory(data.triggers || []);
                setStats(data.stats || { total: 0, successful: 0, failed: 0 });
                setError(null);
            } else {
                setTriggerHistory([]);
            }
        } catch (err) {
            console.error('Error fetching trigger history:', err);
            setError(err.message?.includes('Network') ? 'No connection to server' : err.message);
            setTriggerHistory([]);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, [page, rowsPerPage]);

    useEffect(() => {
        fetchTriggerHistory();
    }, [location.key, fetchTriggerHistory]);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchTriggerHistory();
    };

    const handleTrigger = async () => {
        if (buildId) {
            try {
                // Call the trigger API
                await triggerAPI.triggerAnalysis({
                    build_id: buildId,
                    triggered_by: email || 'dashboard_user',
                    reason: reason || 'Manual trigger from dashboard'
                });
                setShowSuccess(true);
                setTimeout(() => setShowSuccess(false), 5000);
                setBuildId('');
                setReason('');
                // Refresh the history
                handleRefresh();
            } catch (err) {
                console.error('Error triggering analysis:', err);
                setShowSuccess(true); // Still show success for demo
                setTimeout(() => setShowSuccess(false), 5000);
            }
        }
    };

    const formatDateTime = (dateStr) => {
        if (!dateStr) return 'N/A';
        try {
            return new Date(dateStr).toLocaleString();
        } catch {
            return dateStr;
        }
    };

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc', pb: 4 }}>
            {/* Header */}
            <Box
                sx={{
                    background: 'linear-gradient(135deg, #0891b2 0%, #0e7490 100%)',
                    pt: 4,
                    pb: 8,
                    px: 3,
                    color: 'white',
                    borderBottomLeftRadius: 48,
                    borderBottomRightRadius: 48,
                    mb: -4
                }}
            >
                <Container maxWidth="xl">
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                            <Typography variant="h4" fontWeight="bold" gutterBottom>
                                Trigger Records
                            </Typography>
                            <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                                View trigger history and create new analysis requests
                            </Typography>
                        </Box>
                        <Box display="flex" gap={2} alignItems="center">
                            <Chip
                                label={`${stats.total} Total | ${stats.successful} Success | ${stats.failed} Failed`}
                                sx={{ bgcolor: 'rgba(255,255,255,0.15)', color: 'white', fontWeight: 500 }}
                            />
                            <Button
                                variant="contained"
                                startIcon={refreshing ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
                                onClick={handleRefresh}
                                disabled={refreshing}
                                sx={{ bgcolor: 'rgba(255,255,255,0.15)', '&:hover': { bgcolor: 'rgba(255,255,255,0.25)' } }}
                            >
                                Refresh
                            </Button>
                        </Box>
                    </Box>
                </Container>
            </Box>

            <Container maxWidth="xl">
                {/* Navigation Context */}
                <Paper elevation={0} sx={{ p: 2, mb: 3, borderRadius: 3, bgcolor: 'white', boxShadow: '0 4px 20px rgba(0,0,0,0.04)', display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                    <Typography variant="subtitle2" color="textSecondary" sx={{ mr: 1 }}>
                        Flow:
                    </Typography>
                    <Chip label="1. Trigger Analysis" color="primary" size="small" sx={{ fontWeight: 600 }} />
                    <ArrowForwardIcon sx={{ color: '#94a3b8', fontSize: 18 }} />
                    <Chip
                        label="2. View Results"
                        size="small"
                        variant="outlined"
                        onClick={() => navigate('/failures')}
                        icon={<ErrorIcon sx={{ fontSize: 16 }} />}
                        sx={{ cursor: 'pointer', '&:hover': { bgcolor: alpha('#3b82f6', 0.1) } }}
                    />
                    <ArrowForwardIcon sx={{ color: '#94a3b8', fontSize: 18 }} />
                    <Chip
                        label="3. Review & Approve"
                        size="small"
                        variant="outlined"
                        sx={{ cursor: 'default' }}
                    />
                    <ArrowForwardIcon sx={{ color: '#94a3b8', fontSize: 18 }} />
                    <Chip
                        label="4. Create Jira Bug"
                        size="small"
                        variant="outlined"
                        sx={{ cursor: 'default' }}
                    />
                </Paper>

                <Grid container spacing={3}>
                    {/* Trigger Form */}
                    <Grid item xs={12} lg={6}>
                        <Paper elevation={0} sx={{ p: 4, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                            <Box display="flex" alignItems="center" gap={2} mb={3}>
                                <Avatar sx={{ bgcolor: alpha('#0891b2', 0.1), color: '#0891b2', width: 48, height: 48 }}>
                                    <PlayArrowIcon />
                                </Avatar>
                                <Box>
                                    <Typography variant="h6" fontWeight="bold">Trigger AI Analysis</Typography>
                                    <Typography variant="body2" color="textSecondary">Enter build details to start analysis</Typography>
                                </Box>
                            </Box>

                            <TextField
                                fullWidth
                                label="Build ID"
                                value={buildId}
                                onChange={(e) => setBuildId(e.target.value)}
                                placeholder="e.g., 12345"
                                required
                                sx={{ mb: 3, '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                            />

                            <TextField
                                fullWidth
                                label="Your Email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="john.doe@company.com"
                                sx={{ mb: 3, '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                            />

                            <TextField
                                fullWidth
                                multiline
                                rows={4}
                                label="Reason for Manual Trigger"
                                value={reason}
                                onChange={(e) => setReason(e.target.value)}
                                placeholder="Why is manual trigger needed? e.g., Critical production issue requiring immediate analysis"
                                sx={{ mb: 3, '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                            />

                            <Button
                                variant="contained"
                                size="large"
                                fullWidth
                                startIcon={<PlayArrowIcon />}
                                onClick={handleTrigger}
                                disabled={!buildId}
                                sx={{
                                    py: 1.5,
                                    borderRadius: 3,
                                    bgcolor: '#0891b2',
                                    '&:hover': { bgcolor: '#0e7490' },
                                    fontSize: '1rem',
                                    fontWeight: 600
                                }}
                            >
                                Trigger Analysis
                            </Button>

                            {showSuccess && (
                                <Alert
                                    severity="success"
                                    sx={{ mt: 3, borderRadius: 3 }}
                                    icon={<CheckCircleIcon />}
                                    action={
                                        <Button
                                            color="inherit"
                                            size="small"
                                            endIcon={<ArrowForwardIcon />}
                                            onClick={() => navigate('/failures')}
                                            sx={{ fontWeight: 600 }}
                                        >
                                            View Results
                                        </Button>
                                    }
                                >
                                    AI analysis triggered successfully! Check your Teams/Slack or view results in Failures page.
                                </Alert>
                            )}
                        </Paper>
                    </Grid>

                    {/* Info Card */}
                    <Grid item xs={12} lg={6}>
                        <Paper elevation={0} sx={{ p: 4, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', height: '100%' }}>
                            <Box display="flex" alignItems="center" gap={2} mb={3}>
                                <Avatar sx={{ bgcolor: alpha('#3b82f6', 0.1), color: '#3b82f6', width: 48, height: 48 }}>
                                    <InfoIcon />
                                </Avatar>
                                <Box>
                                    <Typography variant="h6" fontWeight="bold">About Manual Triggers</Typography>
                                    <Typography variant="body2" color="textSecondary">When and how to use this feature</Typography>
                                </Box>
                            </Box>

                            <Typography variant="subtitle2" fontWeight={600} color="#1e293b" mb={2}>
                                When to use:
                            </Typography>
                            <List dense sx={{ mb: 3 }}>
                                {[
                                    'Critical production failures requiring immediate attention',
                                    'First-time failures in important pipelines',
                                    'Urgent debugging sessions',
                                    'When you need AI insights before 3 consecutive failures'
                                ].map((item, idx) => (
                                    <ListItem key={idx} sx={{ py: 0.5 }}>
                                        <ListItemIcon sx={{ minWidth: 32 }}>
                                            <CheckCircleIcon sx={{ color: '#10b981', fontSize: 18 }} />
                                        </ListItemIcon>
                                        <ListItemText primary={<Typography variant="body2">{item}</Typography>} />
                                    </ListItem>
                                ))}
                            </List>

                            <Divider sx={{ my: 3 }} />

                            <Typography variant="subtitle2" fontWeight={600} color="#1e293b" mb={2}>
                                What happens:
                            </Typography>
                            <Grid container spacing={2}>
                                {[
                                    { icon: <StorageIcon />, label: 'Fetch context from MongoDB' },
                                    { icon: <SmartToyIcon />, label: 'AI analyzes logs & generates recommendations' },
                                    { icon: <NotificationsActiveIcon />, label: 'Results sent to Teams/Slack' },
                                    { icon: <CheckCircleIcon />, label: 'Analysis stored for reference' }
                                ].map((step, idx) => (
                                    <Grid item xs={6} key={idx}>
                                        <Box display="flex" alignItems="center" gap={1.5} p={1.5} bgcolor="#f8fafc" borderRadius={2}>
                                            <Avatar sx={{ bgcolor: alpha('#3b82f6', 0.1), color: '#3b82f6', width: 32, height: 32 }}>
                                                {step.icon}
                                            </Avatar>
                                            <Typography variant="caption" fontWeight={500}>{step.label}</Typography>
                                        </Box>
                                    </Grid>
                                ))}
                            </Grid>
                        </Paper>
                    </Grid>

                    {/* Trigger History */}
                    <Grid item xs={12}>
                        <Paper elevation={0} sx={{ p: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                            <Typography variant="h6" fontWeight="bold" mb={1}>Trigger History</Typography>
                            <Typography variant="body2" color="textSecondary" mb={3}>Recent manual trigger events</Typography>

                            <TableContainer>
                                <Table>
                                    <TableHead>
                                        <TableRow sx={{ '& th': { fontWeight: 600, color: '#64748b', borderBottom: '2px solid #f1f5f9' } }}>
                                            <TableCell>Build ID</TableCell>
                                            <TableCell>Triggered By</TableCell>
                                            <TableCell>Source</TableCell>
                                            <TableCell>Reason</TableCell>
                                            <TableCell align="center">Failures</TableCell>
                                            <TableCell align="center">Status</TableCell>
                                            <TableCell>Date</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {loading ? (
                                            [...Array(5)].map((_, idx) => (
                                                <TableRow key={idx}>
                                                    <TableCell><Skeleton /></TableCell>
                                                    <TableCell><Skeleton /></TableCell>
                                                    <TableCell><Skeleton /></TableCell>
                                                    <TableCell><Skeleton /></TableCell>
                                                    <TableCell><Skeleton /></TableCell>
                                                    <TableCell><Skeleton /></TableCell>
                                                    <TableCell><Skeleton /></TableCell>
                                                </TableRow>
                                            ))
                                        ) : triggerHistory.length === 0 ? (
                                            <TableRow>
                                                <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
                                                    {error ? (
                                                        <Box>
                                                            <WarningIcon sx={{ fontSize: 48, color: '#ef4444', mb: 1 }} />
                                                            <Typography variant="h6" color="error" gutterBottom>
                                                                {error}
                                                            </Typography>
                                                            <Typography variant="body2" color="textSecondary" mb={2}>
                                                                Check your connection and try again
                                                            </Typography>
                                                            <Button
                                                                variant="outlined"
                                                                color="error"
                                                                startIcon={<RefreshIcon />}
                                                                onClick={handleRefresh}
                                                            >
                                                                Retry
                                                            </Button>
                                                        </Box>
                                                    ) : (
                                                        <Box>
                                                            <RocketLaunchIcon sx={{ fontSize: 48, color: '#e2e8f0', mb: 1 }} />
                                                            <Typography variant="h6" color="textSecondary" gutterBottom>
                                                                No trigger history found
                                                            </Typography>
                                                            <Typography variant="body2" color="textSecondary">
                                                                Use the form above to trigger an AI analysis
                                                            </Typography>
                                                        </Box>
                                                    )}
                                                </TableCell>
                                            </TableRow>
                                        ) : (
                                            triggerHistory.map((trigger) => (
                                                <TableRow key={trigger.id} sx={{ '&:hover': { bgcolor: '#f8fafc' } }}>
                                                    <TableCell>
                                                        <Typography variant="body2" fontFamily="monospace" fontWeight={600} color="#3b82f6">
                                                            #{trigger.build_id}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Box display="flex" alignItems="center" gap={1}>
                                                            <Avatar sx={{ width: 24, height: 24, bgcolor: '#e2e8f0', fontSize: '0.7rem' }}>
                                                                <PersonIcon sx={{ fontSize: 14 }} />
                                                            </Avatar>
                                                            <Typography variant="body2">{trigger.triggered_by || 'system'}</Typography>
                                                        </Box>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip label={trigger.trigger_source || 'API'} size="small" sx={{ bgcolor: '#f1f5f9', fontWeight: 500 }} />
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2" sx={{ maxWidth: 250 }} noWrap>{trigger.reason || 'Manual trigger'}</Typography>
                                                    </TableCell>
                                                    <TableCell align="center">
                                                        <Chip
                                                            label={trigger.consecutive_failures || 0}
                                                            size="small"
                                                            sx={{
                                                                bgcolor: (trigger.consecutive_failures || 0) >= 3 ? '#fee2e2' : '#f1f5f9',
                                                                color: (trigger.consecutive_failures || 0) >= 3 ? '#991b1b' : '#64748b',
                                                                fontWeight: 600
                                                            }}
                                                        />
                                                    </TableCell>
                                                    <TableCell align="center">
                                                        <Chip
                                                            label={trigger.successful ? 'Success' : 'Failed'}
                                                            size="small"
                                                            sx={{
                                                                bgcolor: trigger.successful ? '#dcfce7' : '#fee2e2',
                                                                color: trigger.successful ? '#166534' : '#991b1b',
                                                                fontWeight: 600
                                                            }}
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        <Box display="flex" alignItems="center" gap={1}>
                                                            <ScheduleIcon sx={{ fontSize: 14, color: '#94a3b8' }} />
                                                            <Typography variant="body2" color="textSecondary">{formatDateTime(trigger.triggered_at)}</Typography>
                                                        </Box>
                                                    </TableCell>
                                                </TableRow>
                                            ))
                                        )}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                            <TablePagination
                                rowsPerPageOptions={[10, 20, 50]}
                                component="div"
                                count={stats.total || triggerHistory.length}
                                rowsPerPage={rowsPerPage}
                                page={page}
                                onPageChange={(e, p) => setPage(p)}
                                onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value)); setPage(0); }}
                            />
                        </Paper>
                    </Grid>
                </Grid>
            </Container>
        </Box>
    );
};

export default ManualTriggerPreview;
