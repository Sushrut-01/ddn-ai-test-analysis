import React, { useState, useEffect, useCallback } from 'react';
import { Box, Container, Grid, Paper, Typography, Card, CardContent, IconButton, Chip, LinearProgress, Button, Divider, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Avatar, CircularProgress, Skeleton } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, Legend, LineChart, Line } from 'recharts';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import StorageIcon from '@mui/icons-material/Storage';
import CloudIcon from '@mui/icons-material/Cloud';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import SpeedIcon from '@mui/icons-material/Speed';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RefreshIcon from '@mui/icons-material/Refresh';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { useNavigate, useLocation } from 'react-router-dom';
import ServiceControlModern from '../components/ServiceControlModern';
import { useColorTheme } from '../theme/ThemeContext';
import { monitoringAPI, analyticsAPI, failuresAPI } from '../services/api';

// Glassmorphism Stat Card
const StatCard = ({ title, value, trend, trendValue, icon, color, subtitle, loading }) => (
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
            <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                <Box>
                    <Typography variant="body2" color="textSecondary" fontWeight={500} gutterBottom>{title}</Typography>
                    {loading ? (
                        <Skeleton variant="text" width={80} height={50} />
                    ) : (
                        <Typography variant="h3" fontWeight="bold" sx={{ color: '#1a1a2e', letterSpacing: '-0.5px' }}>{value}</Typography>
                    )}
                    {subtitle && <Typography variant="caption" color="textSecondary">{subtitle}</Typography>}
                </Box>
                <Box sx={{
                    p: 1.5,
                    borderRadius: 3,
                    bgcolor: alpha(color, 0.1),
                    color: color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                    {icon}
                </Box>
            </Box>
            <Box display="flex" alignItems="center" mt={2}>
                {trend === 'up' ? (
                    <TrendingUpIcon fontSize="small" sx={{ color: '#10b981' }} />
                ) : (
                    <TrendingDownIcon fontSize="small" sx={{ color: '#ef4444' }} />
                )}
                <Typography
                    variant="body2"
                    sx={{
                        ml: 0.5,
                        fontWeight: 600,
                        color: trend === 'up' ? '#10b981' : '#ef4444'
                    }}
                >
                    {trendValue}
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ ml: 1 }}>vs last week</Typography>
            </Box>
        </CardContent>
    </Card>
);

// System Health Component Card
const SystemHealthCard = ({ name, status, icon: Icon, metrics, loading }) => {
    const isHealthy = status === 'healthy';
    const statusColor = isHealthy ? '#10b981' : '#ef4444';

    return (
        <Paper
            elevation={0}
            sx={{
                p: 2.5,
                borderRadius: 3,
                background: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(10px)',
                border: `2px solid ${alpha(statusColor, 0.2)}`,
                transition: 'all 0.3s ease',
                '&:hover': {
                    borderColor: statusColor,
                    transform: 'scale(1.02)',
                    boxShadow: `0 8px 25px ${alpha(statusColor, 0.15)}`
                }
            }}
        >
            <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Box
                    sx={{
                        p: 1.5,
                        borderRadius: 2,
                        bgcolor: alpha(statusColor, 0.1),
                        display: 'flex'
                    }}
                >
                    <Icon sx={{ color: statusColor, fontSize: 28 }} />
                </Box>
                <Box flex={1}>
                    <Typography variant="subtitle1" fontWeight={600}>{name}</Typography>
                    <Chip
                        label={isHealthy ? 'Healthy' : 'Offline'}
                        size="small"
                        sx={{
                            bgcolor: statusColor,
                            color: 'white',
                            fontWeight: 600,
                            fontSize: '0.7rem',
                            height: 22,
                            borderRadius: 1.5
                        }}
                    />
                </Box>
            </Box>
            {loading ? (
                <Box>
                    <Skeleton variant="text" width="100%" />
                    <Skeleton variant="text" width="80%" />
                </Box>
            ) : metrics && (
                <Box sx={{ mt: 2 }}>
                    {Object.entries(metrics).map(([key, value]) => (
                        <Box key={key} display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                            <Typography variant="caption" color="text.secondary">{key}</Typography>
                            <Typography variant="caption" fontWeight={600}>{value}</Typography>
                        </Box>
                    ))}
                </Box>
            )}
        </Paper>
    );
};

const DashboardPreviewNew = () => {
    const { theme } = useColorTheme();
    const navigate = useNavigate();
    const location = useLocation();

    // State for API data
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState(null);
    const [systemStatus, setSystemStatus] = useState(null);
    const [recentFailures, setRecentFailures] = useState([]);
    const [error, setError] = useState(null);

    // Fetch data from API
    const fetchDashboardData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const [statsRes, statusRes, failuresRes] = await Promise.all([
                monitoringAPI.getStats(),
                monitoringAPI.getSystemStatus(),
                failuresAPI.getList({ limit: 10 })
            ]);

            setStats(statsRes);
            setSystemStatus(statusRes);
            setRecentFailures(failuresRes?.data?.failures || []);
        } catch (err) {
            console.error('Dashboard fetch error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    // Auto-fetch on mount, navigation, and every 30 seconds
    useEffect(() => {
        fetchDashboardData();
        const interval = setInterval(fetchDashboardData, 30000);
        return () => clearInterval(interval);
    }, [location.key, fetchDashboardData]);

    // Build system components from API data
    const systemComponents = systemStatus?.components ? [
        {
            name: 'MongoDB',
            status: systemStatus.components.mongodb?.status || 'offline',
            icon: StorageIcon,
            metrics: {
                'Failures': systemStatus.components.mongodb?.total_failures?.toLocaleString() || '0',
                'Status': systemStatus.components.mongodb?.connected ? 'Connected' : 'Disconnected'
            }
        },
        {
            name: 'PostgreSQL',
            status: systemStatus.components.postgresql?.status || 'offline',
            icon: StorageIcon,
            metrics: {
                'Analyses': systemStatus.components.postgresql?.total_analyses?.toLocaleString() || '0',
                'Status': systemStatus.components.postgresql?.connected ? 'Connected' : 'Disconnected'
            }
        },
        {
            name: 'Pinecone',
            status: systemStatus.components.pinecone?.status || 'offline',
            icon: CloudIcon,
            metrics: {
                'Vectors': systemStatus.components.pinecone?.total_vectors?.toLocaleString() || '0',
                'Status': systemStatus.components.pinecone?.connected ? 'Active' : 'Inactive'
            }
        },
        {
            name: 'AI Service',
            status: systemStatus.components.ai_service?.status || 'offline',
            icon: SmartToyIcon,
            metrics: {
                'Status': systemStatus.components.ai_service?.connected ? 'Active' : 'Inactive',
                'RAG': systemStatus.components.ai_service?.rag_enabled ? 'Enabled' : 'Disabled'
            }
        },
    ] : [];

    // Format time ago
    const formatTimeAgo = (timestamp) => {
        if (!timestamp) return 'Unknown';
        const now = new Date();
        const time = new Date(timestamp);
        const diff = Math.floor((now - time) / 1000);
        if (diff < 60) return `${diff} secs ago`;
        if (diff < 3600) return `${Math.floor(diff / 60)} mins ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
        return `${Math.floor(diff / 86400)} days ago`;
    };

    // Calculate pass rate
    const totalFailures = stats?.total_failures || 0;
    const failures24h = stats?.failures_last_24h || 0;
    const analyzed = stats?.total_analyzed || 0;
    const avgConfidence = stats?.avg_confidence ? parseFloat(stats.avg_confidence) * 100 : 0;

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: theme.background, pb: 4 }}>
            {/* Hero Header Section */}
            <Box
                sx={{
                    background: theme.headerGradient,
                    pt: 4,
                    pb: 10,
                    px: 3,
                    color: 'white',
                    borderBottomLeftRadius: 48,
                    borderBottomRightRadius: 48,
                    mb: -6,
                    position: 'relative',
                    overflow: 'hidden'
                }}
            >
                {/* Decorative elements */}
                <Box sx={{ position: 'absolute', top: -100, right: -100, width: 300, height: 300, borderRadius: '50%', bgcolor: 'rgba(255,255,255,0.05)' }} />
                <Box sx={{ position: 'absolute', bottom: -50, left: -50, width: 200, height: 200, borderRadius: '50%', bgcolor: 'rgba(255,255,255,0.03)' }} />
                <Box sx={{ position: 'absolute', top: 50, left: '30%', width: 150, height: 150, borderRadius: '50%', bgcolor: 'rgba(255,255,255,0.02)' }} />

                <Container maxWidth="xl" sx={{ position: 'relative', zIndex: 1 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                        <Box>
                            <Typography variant="h4" fontWeight="bold" gutterBottom sx={{ letterSpacing: '-0.5px' }}>
                                DDN AI Test Analysis
                            </Typography>
                            <Typography variant="subtitle1" sx={{ opacity: 0.85, maxWidth: 500 }}>
                                Intelligent Test Failure Analysis & Real-time Monitoring Dashboard
                            </Typography>
                        </Box>
                        <Box display="flex" gap={2}>
                            <Button
                                variant="contained"
                                startIcon={loading ? <CircularProgress size={16} color="inherit" /> : <RefreshIcon />}
                                onClick={fetchDashboardData}
                                disabled={loading}
                                sx={{
                                    bgcolor: 'rgba(255,255,255,0.15)',
                                    backdropFilter: 'blur(10px)',
                                    '&:hover': { bgcolor: 'rgba(255,255,255,0.25)' }
                                }}
                            >
                                Refresh
                            </Button>
                            <Chip
                                label={systemStatus?.overall_status === 'healthy' ? 'Live Updates' : 'Connecting...'}
                                sx={{
                                    bgcolor: systemStatus?.overall_status === 'healthy' ? theme.success : theme.warning,
                                    color: 'white',
                                    fontWeight: 600,
                                    px: 1
                                }}
                            />
                        </Box>
                    </Box>

                    {/* Quick Action Chips */}
                    <Box display="flex" gap={1.5} flexWrap="wrap">
                        <Chip
                            icon={<SmartToyIcon sx={{ color: 'white !important' }} />}
                            label="AI-Powered Analysis"
                            sx={{ bgcolor: 'rgba(255,255,255,0.15)', color: 'white', fontWeight: 500 }}
                        />
                        <Chip
                            icon={<SpeedIcon sx={{ color: 'white !important' }} />}
                            label="Real-time Monitoring"
                            sx={{ bgcolor: 'rgba(255,255,255,0.15)', color: 'white', fontWeight: 500 }}
                        />
                        <Chip
                            icon={<StorageIcon sx={{ color: 'white !important' }} />}
                            label="Multi-DB Support"
                            sx={{ bgcolor: 'rgba(255,255,255,0.15)', color: 'white', fontWeight: 500 }}
                        />
                    </Box>
                </Container>
            </Box>

            <Container maxWidth="xl">
                {error && (
                    <Paper sx={{ p: 2, mb: 3, bgcolor: '#fee2e2', color: '#991b1b', borderRadius: 2 }}>
                        <Typography>Error loading dashboard: {error}</Typography>
                    </Paper>
                )}

                {/* Service Control Panel */}
                <Paper
                    elevation={0}
                    sx={{
                        p: 3,
                        mb: 4,
                        borderRadius: 4,
                        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
                        boxShadow: '0 4px 20px rgba(0,0,0,0.04)'
                    }}
                >
                    <ServiceControlModern />
                </Paper>

                {/* Stats Grid */}
                <Grid container spacing={3} mb={4}>
                    <Grid item xs={12} sm={6} md={3}>
                        <StatCard
                            title="Total Test Failures"
                            value={totalFailures.toLocaleString()}
                            trend="up"
                            trendValue={`${failures24h} today`}
                            icon={<ErrorIcon sx={{ fontSize: 28 }} />}
                            color="#ef4444"
                            subtitle="Across all builds"
                            loading={loading}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <StatCard
                            title="AI Analyses"
                            value={analyzed.toLocaleString()}
                            trend="up"
                            trendValue={`${stats?.analyzed_24h || 0} today`}
                            icon={<SmartToyIcon sx={{ fontSize: 28 }} />}
                            color="#3b82f6"
                            subtitle="Completed analyses"
                            loading={loading}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <StatCard
                            title="7-Day Failures"
                            value={(stats?.failures_last_7d || 0).toLocaleString()}
                            trend="down"
                            trendValue="-12%"
                            icon={<CheckCircleIcon sx={{ fontSize: 28 }} />}
                            color="#10b981"
                            subtitle="Last 7 days"
                            loading={loading}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <StatCard
                            title="Avg Confidence"
                            value={`${avgConfidence.toFixed(0)}%`}
                            trend="up"
                            trendValue="+3.5%"
                            icon={<SpeedIcon sx={{ fontSize: 28 }} />}
                            color="#8b5cf6"
                            subtitle="AI confidence score"
                            loading={loading}
                        />
                    </Grid>
                </Grid>

                {/* System Health Section */}
                <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ mb: 2, color: '#1e293b' }}>
                    System Health Overview
                </Typography>
                <Grid container spacing={2} sx={{ mb: 4 }}>
                    {loading ? (
                        [1,2,3,4].map((i) => (
                            <Grid item xs={12} sm={6} md={3} key={i}>
                                <Skeleton variant="rounded" height={150} />
                            </Grid>
                        ))
                    ) : (
                        systemComponents.map((component, index) => (
                            <Grid item xs={12} sm={6} md={3} key={index}>
                                <SystemHealthCard {...component} loading={loading} />
                            </Grid>
                        ))
                    )}
                </Grid>

                {/* Recent Test Failures */}
                <Paper
                    elevation={0}
                    sx={{
                        p: 3,
                        borderRadius: 4,
                        bgcolor: 'white',
                        boxShadow: '0 4px 20px rgba(0,0,0,0.04)'
                    }}
                >
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                        <Box>
                            <Typography variant="h6" fontWeight="bold" color="#1e293b">Recent Test Failures</Typography>
                            <Typography variant="caption" color="textSecondary">Latest test failures from MongoDB ({recentFailures.length} shown)</Typography>
                        </Box>
                        <Button
                            variant="outlined"
                            endIcon={<ArrowForwardIcon />}
                            onClick={() => navigate('/failures')}
                            sx={{ borderRadius: 2 }}
                        >
                            View All
                        </Button>
                    </Box>

                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow sx={{ '& th': { fontWeight: 600, color: '#64748b', borderBottom: '2px solid #f1f5f9' } }}>
                                    <TableCell>Build ID</TableCell>
                                    <TableCell>Test Name</TableCell>
                                    <TableCell>Suite</TableCell>
                                    <TableCell align="center">Status</TableCell>
                                    <TableCell>Error</TableCell>
                                    <TableCell>Time</TableCell>
                                    <TableCell align="center">Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {loading ? (
                                    [1,2,3,4,5].map((i) => (
                                        <TableRow key={i}>
                                            <TableCell><Skeleton /></TableCell>
                                            <TableCell><Skeleton /></TableCell>
                                            <TableCell><Skeleton /></TableCell>
                                            <TableCell><Skeleton /></TableCell>
                                            <TableCell><Skeleton /></TableCell>
                                            <TableCell><Skeleton /></TableCell>
                                            <TableCell><Skeleton /></TableCell>
                                        </TableRow>
                                    ))
                                ) : recentFailures.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={7} align="center">
                                            <Typography color="textSecondary">No recent failures found</Typography>
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    recentFailures.map((failure, index) => (
                                        <TableRow
                                            key={failure._id || index}
                                            sx={{
                                                '&:hover': { bgcolor: '#f8fafc' },
                                                '& td': { borderBottom: '1px solid #f1f5f9' }
                                            }}
                                        >
                                            <TableCell>
                                                <Typography variant="body2" fontFamily="monospace" fontWeight={600} color="#3b82f6">
                                                    {failure.build_id}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2" fontWeight={500} sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                    {failure.test_name}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="caption" color="textSecondary">
                                                    {failure.suite_name || failure.test_suite}
                                                </Typography>
                                            </TableCell>
                                            <TableCell align="center">
                                                <Chip
                                                    label={failure.status?.toUpperCase() || 'FAILED'}
                                                    size="small"
                                                    sx={{
                                                        fontWeight: 600,
                                                        fontSize: '0.7rem',
                                                        bgcolor: '#fee2e2',
                                                        color: '#991b1b'
                                                    }}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="caption" color="textSecondary" sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'block' }}>
                                                    {failure.error_message?.substring(0, 50)}...
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="caption" color="textSecondary">
                                                    {formatTimeAgo(failure.timestamp)}
                                                </Typography>
                                            </TableCell>
                                            <TableCell align="center">
                                                <Button
                                                    size="small"
                                                    variant="outlined"
                                                    startIcon={<VisibilityIcon />}
                                                    onClick={() => navigate(`/failures/${failure._id}`)}
                                                    sx={{ borderRadius: 2, textTransform: 'none' }}
                                                >
                                                    View
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Paper>

                {/* Footer Info Card */}
                <Box
                    sx={{
                        mt: 4,
                        p: 3,
                        borderRadius: 4,
                        background: theme.headerGradient,
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 3
                    }}
                >
                    <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.15)', width: 56, height: 56 }}>
                        <SmartToyIcon sx={{ fontSize: 32 }} />
                    </Avatar>
                    <Box flex={1}>
                        <Typography variant="h6" fontWeight={600}>
                            {systemStatus?.overall_status === 'healthy' ? 'AI Monitoring Active' : 'Connecting to Services...'}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.85 }}>
                            {systemStatus?.overall_status === 'healthy'
                                ? 'Real-time system health monitoring is enabled. All components are being tracked and analyzed continuously.'
                                : 'Attempting to connect to backend services. Please ensure all Docker containers are running.'}
                        </Typography>
                    </Box>
                    <Button
                        variant="contained"
                        onClick={() => navigate('/services')}
                        sx={{
                            bgcolor: 'rgba(255,255,255,0.15)',
                            '&:hover': { bgcolor: 'rgba(255,255,255,0.25)' }
                        }}
                    >
                        View Services
                    </Button>
                </Box>
            </Container>
        </Box>
    );
};

export default DashboardPreviewNew;
