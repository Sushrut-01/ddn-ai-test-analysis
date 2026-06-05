import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import {
    Box, Container, Paper, Typography, Grid, Button, Chip, Avatar, IconButton,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    LinearProgress, Card, CardContent, Tabs, Tab, Divider, Alert, Tooltip,
    CircularProgress, Skeleton
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import RefreshIcon from '@mui/icons-material/Refresh';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import StorageIcon from '@mui/icons-material/Storage';
import MemoryIcon from '@mui/icons-material/Memory';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import SpeedIcon from '@mui/icons-material/Speed';
import TimelineIcon from '@mui/icons-material/Timeline';
import TaskAltIcon from '@mui/icons-material/TaskAlt';
import PendingActionsIcon from '@mui/icons-material/PendingActions';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import PlayCircleIcon from '@mui/icons-material/PlayCircle';
import StopCircleIcon from '@mui/icons-material/StopCircle';
import SettingsIcon from '@mui/icons-material/Settings';
import CachedIcon from '@mui/icons-material/Cached';
import DataObjectIcon from '@mui/icons-material/DataObject';
import WorkIcon from '@mui/icons-material/Work';
import BoltIcon from '@mui/icons-material/Bolt';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { monitoringAPI, serviceManagerAPI, langfuseAPI, flowerAPI, n8nAPI, workflowsAPI } from '../services/api';

const TabPanel = ({ children, value, index }) => (
    <div role="tabpanel" hidden={value !== index}>
        {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
);

const StatusChip = ({ status }) => {
    const colors = {
        running: { bg: '#dcfce7', color: '#166534', label: 'Running' },
        stopped: { bg: '#fee2e2', color: '#991b1b', label: 'Stopped' },
        warning: { bg: '#fef3c7', color: '#92400e', label: 'Warning' },
        online: { bg: '#dcfce7', color: '#166534', label: 'Online' },
        active: { bg: '#dbeafe', color: '#1e40af', label: 'Active' },
        inactive: { bg: '#f1f5f9', color: '#64748b', label: 'Inactive' },
        SUCCESS: { bg: '#dcfce7', color: '#166534', label: 'Success' },
        FAILURE: { bg: '#fee2e2', color: '#991b1b', label: 'Failed' },
        PROCESSING: { bg: '#fef3c7', color: '#92400e', label: 'Processing' },
        success: { bg: '#dcfce7', color: '#166534', label: 'Success' },
        error: { bg: '#fee2e2', color: '#991b1b', label: 'Error' },
    };
    const config = colors[status] || colors.running;
    return (
        <Chip
            label={config.label}
            size="small"
            sx={{ bgcolor: config.bg, color: config.color, fontWeight: 600, fontSize: '0.7rem' }}
        />
    );
};

const ServicesMonitoringPreview = () => {
    const location = useLocation();
    const [tabValue, setTabValue] = useState(0);
    const [refreshing, setRefreshing] = useState(false);
    const [loading, setLoading] = useState(true);
    const [systemStatus, setSystemStatus] = useState(null);
    const [stats, setStats] = useState(null);
    const [dockerServices, setDockerServices] = useState({});
    const [error, setError] = useState(null);

    // External services state
    const [langfuseStats, setLangfuseStats] = useState(null);
    const [celeryWorkers, setCeleryWorkers] = useState({});
    const [celeryTasks, setCeleryTasks] = useState({});
    const [n8nWorkflows, setN8nWorkflows] = useState([]);
    const [n8nExecutions, setN8nExecutions] = useState([]);

    const fetchServiceStatus = useCallback(async () => {
        try {
            // Fetch all data in parallel
            const [statusRes, statsRes, servicesRes, langfuseRes, workersRes, tasksRes, workflowsRes, executionsRes] = await Promise.all([
                monitoringAPI.getSystemStatus(),
                monitoringAPI.getStats(),
                serviceManagerAPI.getAllServices(),
                langfuseAPI.getStats().catch(() => null),
                flowerAPI.getWorkers().catch(() => ({})),
                flowerAPI.getTasks().catch(() => ({})),
                workflowsAPI.getWorkflows().catch(() => []),
                workflowsAPI.getExecutions().catch(() => [])
            ]);
            setSystemStatus(statusRes);
            setStats(statsRes);
            setDockerServices(servicesRes || {});
            setLangfuseStats(langfuseRes);
            setCeleryWorkers(workersRes);
            setCeleryTasks(tasksRes);
            setN8nWorkflows(workflowsRes);
            setN8nExecutions(executionsRes);
            setError(null);
        } catch (err) {
            console.error('Error fetching service status:', err);
            setError(err.message);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, []);

    useEffect(() => {
        fetchServiceStatus();
        const interval = setInterval(fetchServiceStatus, 30000);
        return () => clearInterval(interval);
    }, [location.key, fetchServiceStatus]);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchServiceStatus();
    };

    // Build services list from real API data (Docker services + Database components)
    const buildServicesList = () => {
        const services = [];

        // Service icons mapping
        const serviceIcons = {
            mongodb: <StorageIcon />,
            postgresql: <StorageIcon />,
            pinecone: <MemoryIcon />,
            pinecone_knowledge: <MemoryIcon />,
            pinecone_failures: <MemoryIcon />,
            ai_service: <SmartToyIcon />,
            ai_analysis: <SmartToyIcon />,
            redis: <MemoryIcon />,
            dashboard_api: <SettingsIcon />,
            dashboard_ui: <SettingsIcon />,
            manual_trigger: <BoltIcon />,
            aging: <HourglassEmptyIcon />,
            jira: <WorkIcon />,
            slack: <WorkIcon />,
            knowledge_api: <StorageIcon />,
            langfuse: <TimelineIcon />,
            langfuse_db: <StorageIcon />,
            flower: <WorkIcon />,
            n8n: <AccountTreeIcon />,
            mcp_github: <SettingsIcon />,
            mcp_mongodb: <StorageIcon />,
            reranking: <SmartToyIcon />,
            self_healing: <CachedIcon />,
            jenkins: <WorkIcon />,
        };

        // Service URLs mapping
        const serviceUrls = {
            dashboard_ui: 'http://localhost:5173',
            dashboard_api: 'http://localhost:5006',
            ai_analysis: 'http://localhost:5000',
            langfuse: 'http://localhost:3000',
            flower: 'http://localhost:5555',
            n8n: 'http://localhost:5678',
            jenkins: 'http://localhost:8081',
            jira: 'http://localhost:5009',
            slack: 'http://localhost:5012',
        };

        // Add Docker services from service manager API
        if (dockerServices && Object.keys(dockerServices).length > 0) {
            Object.entries(dockerServices).forEach(([key, data]) => {
                services.push({
                    name: data.name || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                    port: data.port || '-',
                    status: data.running ? 'running' : 'stopped',
                    type: key.includes('db') || key.includes('postgres') || key.includes('mongo') ? 'database' :
                          key.includes('api') ? 'api' :
                          key.includes('ui') ? 'frontend' : 'service',
                    icon: serviceIcons[key] || <SettingsIcon />,
                    url: serviceUrls[key] || (data.port ? `http://localhost:${data.port}` : null),
                    memory: '-',
                    source: 'docker',
                    details: data
                });
            });
        }

        // Add database components from system status API (if not already added from docker services)
        if (systemStatus?.components) {
            const existingNames = services.map(s => s.name.toLowerCase());

            Object.entries(systemStatus.components).forEach(([name, data]) => {
                const displayName = name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

                // Skip if already exists from docker services
                if (existingNames.some(n => n.includes(name.split('_')[0]))) return;

                const componentPorts = {
                    mongodb: 'Cloud',
                    pinecone: 'Cloud',
                    pinecone_knowledge: 'Cloud',
                    pinecone_failures: 'Cloud',
                };

                services.push({
                    name: displayName,
                    port: componentPorts[name] || '-',
                    status: data.status === 'healthy' || data.connected ? 'running' : 'stopped',
                    type: name.includes('pinecone') ? 'vector' :
                          name.includes('mongo') || name.includes('postgres') ? 'database' : 'service',
                    icon: serviceIcons[name] || <SettingsIcon />,
                    url: null,
                    memory: '-',
                    source: 'component',
                    details: data
                });
            });
        }

        // Sort: running first, then by name
        return services.sort((a, b) => {
            if (a.status === 'running' && b.status !== 'running') return -1;
            if (a.status !== 'running' && b.status === 'running') return 1;
            return a.name.localeCompare(b.name);
        });
    };

    const allServices = buildServicesList();
    const runningServices = allServices.filter(s => s.status === 'running').length;
    const stoppedServices = allServices.filter(s => s.status === 'stopped').length;

    // Build real data from API responses
    const workerCount = Object.keys(celeryWorkers).length;
    const taskList = Object.values(celeryTasks);
    const succeededTasks = taskList.filter(t => t.state === 'SUCCESS').length;
    const failedTasks = taskList.filter(t => t.state === 'FAILURE').length;

    const langfuseData = {
        totalTraces: langfuseStats?.traces || stats?.total_analyzed || 0,
        totalGenerations: langfuseStats?.generations || stats?.total_analyzed || 0,
        avgLatency: langfuseStats?.avgLatency || 0,
        totalTokens: langfuseStats?.totalTokens || 0,
        totalCost: langfuseStats?.totalCost || 0,
        successRate: langfuseStats?.successRate || (stats?.avg_confidence ? Math.round(parseFloat(stats.avg_confidence) * 100) : 0),
        models: langfuseStats?.models || [],
        recentTraces: langfuseStats?.recentTraces || [],
        latencyTrend: langfuseStats?.latencyTrend || []
    };

    const celeryData = {
        activeWorkers: workerCount,
        tasksProcessed: taskList.length || stats?.total_analyzed || 0,
        tasksQueued: taskList.filter(t => t.state === 'PENDING').length,
        tasksSucceeded: succeededTasks || stats?.total_analyzed || 0,
        tasksFailed: failedTasks,
        successRate: taskList.length > 0 ? Math.round((succeededTasks / taskList.length) * 100) : 100,
        avgProcessingTime: 0,
        workers: Object.entries(celeryWorkers).map(([name, data]) => ({
            name,
            status: data.status || 'active',
            processed: data.stats?.total || 0,
            active: data.active || 0
        })),
        recentTasks: taskList.slice(0, 10).map(t => ({
            name: t.name || 'Unknown Task',
            status: t.state,
            duration: t.runtime ? `${t.runtime.toFixed(2)}s` : '-',
            timestamp: t.received ? new Date(t.received * 1000).toLocaleString() : '-'
        })),
        taskTrend: []
    };

    const redisData = {
        connected: dockerServices?.redis?.running || true,
        usedMemory: dockerServices?.redis?.memory || '-',
        peakMemory: '-',
        totalKeys: 0,
        hitRate: 0,
        missRate: 0,
        opsPerSec: 0,
        connectedClients: 0,
        queueLength: 0,
        cacheStats: { hits: 0, misses: 0, expired: 0 },
        keyDistribution: []
    };

    // Build workflow data from Python workflows API
    const activeWorkflows = n8nWorkflows.filter(w => w.status === 'active').length;
    const successfulExecs = n8nExecutions.filter(e => e.status === 'completed').length;
    const failedExecs = n8nExecutions.filter(e => e.status === 'failed').length;

    const n8nData = {
        totalWorkflows: n8nWorkflows.length,
        activeWorkflows: activeWorkflows,
        totalExecutions: n8nExecutions.length,
        successfulExecutions: successfulExecs,
        failedExecutions: failedExecs,
        successRate: n8nExecutions.length > 0 ? Math.round((successfulExecs / n8nExecutions.length) * 100) : 100,
        workflows: n8nWorkflows.map(w => ({
            name: w.name || 'Unnamed Workflow',
            version: w.version || '1.0.0',
            type: w.type || 'complete',
            nodeCount: w.node_count || 0,
            status: w.status || 'active',
            executions: n8nExecutions.filter(e => e.workflow_id === w.id).length || 0,
            lastRun: w.updated_at ? new Date(w.updated_at).toLocaleString() : '-',
            lastStatus: w.status === 'active' ? 'success' : 'inactive',
            tags: w.tags || [],
            description: w.description || ''
        }))
    };

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc', pb: 4 }}>
            {/* Header */}
            <Box
                sx={{
                    background: 'linear-gradient(135deg, #10b981, #14b8a6)',
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
                                Services Monitoring
                            </Typography>
                            <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                                Monitor Langfuse, Celery, Redis, Agentic Workflows and all backend services
                            </Typography>
                        </Box>
                        <Box display="flex" gap={2}>
                            <Chip
                                icon={<CheckCircleIcon sx={{ color: '#10b981 !important' }} />}
                                label={`${runningServices} Running`}
                                sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                            />
                            {stoppedServices > 0 && (
                                <Chip
                                    icon={<ErrorIcon sx={{ color: '#ef4444 !important' }} />}
                                    label={`${stoppedServices} Stopped`}
                                    sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                                />
                            )}
                            <Button
                                variant="contained"
                                startIcon={refreshing ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
                                onClick={handleRefresh}
                                disabled={refreshing}
                                sx={{ bgcolor: 'rgba(255,255,255,0.2)', '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' } }}
                            >
                                {refreshing ? 'Refreshing...' : 'Refresh All'}
                            </Button>
                        </Box>
                    </Box>
                </Container>
            </Box>

            <Container maxWidth="xl">
                {/* Quick Stats */}
                <Grid container spacing={3} mb={4}>
                    {[
                        { label: 'Total Components', value: loading ? '-' : allServices.length, icon: <SettingsIcon />, color: '#10b981' },
                        { label: 'Total Failures', value: loading ? '-' : (stats?.total_failures || 0).toLocaleString(), icon: <TimelineIcon />, color: '#14b8a6' },
                        { label: 'Analyzed', value: loading ? '-' : (stats?.total_analyzed || 0).toLocaleString(), icon: <TaskAltIcon />, color: '#10b981' },
                        { label: 'System Status', value: loading ? '-' : (systemStatus?.overall_status || 'unknown').toUpperCase(), icon: <SpeedIcon />, color: systemStatus?.overall_status === 'healthy' ? '#10b981' : '#f59e0b' },
                    ].map((stat, idx) => (
                        <Grid item xs={6} md={3} key={idx}>
                            <Card elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
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
                <Paper elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', mb: 3 }}>
                    <Tabs
                        value={tabValue}
                        onChange={(e, v) => setTabValue(v)}
                        sx={{ borderBottom: '1px solid #e2e8f0', px: 2 }}
                    >
                        <Tab icon={<SettingsIcon />} iconPosition="start" label="All Services" />
                        <Tab icon={<TimelineIcon />} iconPosition="start" label="Langfuse (LLM)" />
                        <Tab icon={<WorkIcon />} iconPosition="start" label="Celery Tasks" />
                        <Tab icon={<MemoryIcon />} iconPosition="start" label="Redis Cache" />
                        <Tab icon={<AccountTreeIcon />} iconPosition="start" label="Agentic Workflows" />
                    </Tabs>

                    {/* Tab 0: All Services */}
                    <TabPanel value={tabValue} index={0}>
                        <Box sx={{ p: 3 }}>
                            <TableContainer>
                                <Table>
                                    <TableHead>
                                        <TableRow sx={{ bgcolor: '#f8fafc' }}>
                                            <TableCell sx={{ fontWeight: 600 }}>Service</TableCell>
                                            <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                                            <TableCell sx={{ fontWeight: 600 }}>Port</TableCell>
                                            <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                                            <TableCell sx={{ fontWeight: 600 }}>Memory</TableCell>
                                            <TableCell sx={{ fontWeight: 600 }} align="center">Actions</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {allServices.map((service, idx) => (
                                            <TableRow key={idx} sx={{ '&:hover': { bgcolor: '#f8fafc' } }}>
                                                <TableCell>
                                                    <Box display="flex" alignItems="center" gap={1.5}>
                                                        <Avatar sx={{ width: 32, height: 32, bgcolor: alpha('#10b981', 0.1), color: '#10b981' }}>
                                                            {service.icon}
                                                        </Avatar>
                                                        <Typography variant="body2" fontWeight={600}>{service.name}</Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Chip label={service.type.toUpperCase()} size="small" sx={{ bgcolor: '#f1f5f9', fontSize: '0.7rem' }} />
                                                </TableCell>
                                                <TableCell>
                                                    <Typography variant="body2" fontFamily="monospace">{service.port}</Typography>
                                                </TableCell>
                                                <TableCell>
                                                    <StatusChip status={service.status} />
                                                </TableCell>
                                                <TableCell>
                                                    <Typography variant="body2">{service.memory}</Typography>
                                                </TableCell>
                                                <TableCell align="center">
                                                    {service.url && (
                                                        <Tooltip title="Open in new tab">
                                                            <IconButton
                                                                size="small"
                                                                onClick={() => window.open(service.url, '_blank')}
                                                                sx={{ color: '#10b981' }}
                                                            >
                                                                <OpenInNewIcon fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>
                                                    )}
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </Box>
                    </TabPanel>

                    {/* Tab 1: Langfuse */}
                    <TabPanel value={tabValue} index={1}>
                        <Box sx={{ p: 3 }}>
                            <Grid container spacing={3}>
                                {/* Stats Cards */}
                                <Grid item xs={12}>
                                    <Grid container spacing={2}>
                                        {[
                                            { label: 'Total Traces', value: langfuseData.totalTraces.toLocaleString(), icon: <TimelineIcon />, color: '#14b8a6' },
                                            { label: 'Generations', value: langfuseData.totalGenerations.toLocaleString(), icon: <SmartToyIcon />, color: '#10b981' },
                                            { label: 'Avg Latency', value: `${langfuseData.avgLatency}ms`, icon: <SpeedIcon />, color: '#f59e0b' },
                                            { label: 'Total Tokens', value: `${(langfuseData.totalTokens / 1000000).toFixed(1)}M`, icon: <DataObjectIcon />, color: '#10b981' },
                                            { label: 'Total Cost', value: `$${langfuseData.totalCost.toFixed(2)}`, icon: <MonetizationOnIcon />, color: '#ef4444' },
                                            { label: 'Success Rate', value: `${langfuseData.successRate}%`, icon: <CheckCircleIcon />, color: '#059669' },
                                        ].map((stat, idx) => (
                                            <Grid item xs={6} md={2} key={idx}>
                                                <Paper sx={{ p: 2, borderRadius: 3, textAlign: 'center', bgcolor: alpha(stat.color, 0.05) }}>
                                                    <Avatar sx={{ bgcolor: alpha(stat.color, 0.1), color: stat.color, mx: 'auto', mb: 1 }}>
                                                        {stat.icon}
                                                    </Avatar>
                                                    <Typography variant="h5" fontWeight="bold">{stat.value}</Typography>
                                                    <Typography variant="caption" color="textSecondary">{stat.label}</Typography>
                                                </Paper>
                                            </Grid>
                                        ))}
                                    </Grid>
                                </Grid>

                                {/* Model Usage */}
                                <Grid item xs={12} md={6}>
                                    <Paper sx={{ p: 3, borderRadius: 3 }}>
                                        <Typography variant="h6" fontWeight="bold" mb={2}>Model Usage</Typography>
                                        <TableContainer>
                                            <Table size="small">
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell sx={{ fontWeight: 600 }}>Model</TableCell>
                                                        <TableCell align="right" sx={{ fontWeight: 600 }}>Calls</TableCell>
                                                        <TableCell align="right" sx={{ fontWeight: 600 }}>Tokens</TableCell>
                                                        <TableCell align="right" sx={{ fontWeight: 600 }}>Cost</TableCell>
                                                        <TableCell align="right" sx={{ fontWeight: 600 }}>Latency</TableCell>
                                                    </TableRow>
                                                </TableHead>
                                                <TableBody>
                                                    {langfuseData.models.map((model, idx) => (
                                                        <TableRow key={idx}>
                                                            <TableCell><Chip label={model.name} size="small" /></TableCell>
                                                            <TableCell align="right">{model.calls.toLocaleString()}</TableCell>
                                                            <TableCell align="right">{(model.tokens / 1000).toFixed(0)}K</TableCell>
                                                            <TableCell align="right">${model.cost.toFixed(2)}</TableCell>
                                                            <TableCell align="right">{model.avgLatency}ms</TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </TableContainer>
                                    </Paper>
                                </Grid>

                                {/* Latency Trend */}
                                <Grid item xs={12} md={6}>
                                    <Paper sx={{ p: 3, borderRadius: 3 }}>
                                        <Typography variant="h6" fontWeight="bold" mb={2}>Latency Trend</Typography>
                                        <ResponsiveContainer width="100%" height={200}>
                                            <AreaChart data={langfuseData.latencyTrend}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="time" />
                                                <YAxis />
                                                <RechartsTooltip />
                                                <Area type="monotone" dataKey="latency" stroke="#10b981" fill={alpha('#10b981', 0.2)} />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    </Paper>
                                </Grid>

                                {/* Recent Traces */}
                                <Grid item xs={12}>
                                    <Paper sx={{ p: 3, borderRadius: 3 }}>
                                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                                            <Typography variant="h6" fontWeight="bold">Recent Traces</Typography>
                                            <Button startIcon={<OpenInNewIcon />} onClick={() => window.open('http://localhost:3000', '_blank')}>
                                                Open Langfuse
                                            </Button>
                                        </Box>
                                        <TableContainer>
                                            <Table size="small">
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell sx={{ fontWeight: 600 }}>Trace ID</TableCell>
                                                        <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                                                        <TableCell sx={{ fontWeight: 600 }}>Model</TableCell>
                                                        <TableCell align="right" sx={{ fontWeight: 600 }}>Tokens</TableCell>
                                                        <TableCell align="right" sx={{ fontWeight: 600 }}>Latency</TableCell>
                                                        <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                                                        <TableCell sx={{ fontWeight: 600 }}>Time</TableCell>
                                                    </TableRow>
                                                </TableHead>
                                                <TableBody>
                                                    {langfuseData.recentTraces.map((trace, idx) => (
                                                        <TableRow key={idx}>
                                                            <TableCell><Typography variant="body2" fontFamily="monospace">{trace.id}</Typography></TableCell>
                                                            <TableCell>{trace.name}</TableCell>
                                                            <TableCell><Chip label={trace.model} size="small" /></TableCell>
                                                            <TableCell align="right">{trace.tokens.toLocaleString()}</TableCell>
                                                            <TableCell align="right">{trace.latency}ms</TableCell>
                                                            <TableCell><StatusChip status={trace.status} /></TableCell>
                                                            <TableCell>{trace.time}</TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </TableContainer>
                                    </Paper>
                                </Grid>
                            </Grid>
                        </Box>
                    </TabPanel>

                    {/* Tab 2: Celery */}
                    <TabPanel value={tabValue} index={2}>
                        <Box sx={{ p: 3 }}>
                            <Grid container spacing={3}>
                                {/* Stats */}
                                <Grid item xs={12}>
                                    <Grid container spacing={2}>
                                        {[
                                            { label: 'Active Workers', value: celeryData.activeWorkers, icon: <WorkIcon />, color: '#10b981' },
                                            { label: 'Tasks Processed', value: celeryData.tasksProcessed, icon: <TaskAltIcon />, color: '#14b8a6' },
                                            { label: 'Tasks Queued', value: celeryData.tasksQueued, icon: <PendingActionsIcon />, color: '#f59e0b' },
                                            { label: 'Success Rate', value: `${celeryData.successRate}%`, icon: <CheckCircleIcon />, color: '#059669' },
                                            { label: 'Failed', value: celeryData.tasksFailed, icon: <ErrorIcon />, color: '#ef4444' },
                                            { label: 'Avg Time', value: `${(celeryData.avgProcessingTime / 1000).toFixed(1)}s`, icon: <SpeedIcon />, color: '#10b981' },
                                        ].map((stat, idx) => (
                                            <Grid item xs={6} md={2} key={idx}>
                                                <Paper sx={{ p: 2, borderRadius: 3, textAlign: 'center', bgcolor: alpha(stat.color, 0.05) }}>
                                                    <Typography variant="h4" fontWeight="bold" color={stat.color}>{stat.value}</Typography>
                                                    <Typography variant="caption" color="textSecondary">{stat.label}</Typography>
                                                </Paper>
                                            </Grid>
                                        ))}
                                    </Grid>
                                </Grid>

                                {/* Workers */}
                                <Grid item xs={12} md={6}>
                                    <Paper sx={{ p: 3, borderRadius: 3 }}>
                                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                                            <Typography variant="h6" fontWeight="bold">Workers</Typography>
                                            <Button startIcon={<OpenInNewIcon />} size="small" onClick={() => window.open('http://localhost:5555', '_blank')}>
                                                Flower Dashboard
                                            </Button>
                                        </Box>
                                        <TableContainer>
                                            <Table size="small">
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell sx={{ fontWeight: 600 }}>Worker</TableCell>
                                                        <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                                                        <TableCell align="right" sx={{ fontWeight: 600 }}>Processed</TableCell>
                                                        <TableCell align="right" sx={{ fontWeight: 600 }}>Active</TableCell>
                                                    </TableRow>
                                                </TableHead>
                                                <TableBody>
                                                    {celeryData.workers.map((worker, idx) => (
                                                        <TableRow key={idx}>
                                                            <TableCell>{worker.name}</TableCell>
                                                            <TableCell><StatusChip status={worker.status} /></TableCell>
                                                            <TableCell align="right">{worker.processed}</TableCell>
                                                            <TableCell align="right">
                                                                <Chip label={worker.active} size="small" color={worker.active > 0 ? 'primary' : 'default'} />
                                                            </TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </TableContainer>
                                    </Paper>
                                </Grid>

                                {/* Task Trend */}
                                <Grid item xs={12} md={6}>
                                    <Paper sx={{ p: 3, borderRadius: 3 }}>
                                        <Typography variant="h6" fontWeight="bold" mb={2}>Task Trend</Typography>
                                        <ResponsiveContainer width="100%" height={200}>
                                            <BarChart data={celeryData.taskTrend}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="time" />
                                                <YAxis />
                                                <RechartsTooltip />
                                                <Bar dataKey="success" fill="#10b981" name="Success" />
                                                <Bar dataKey="failed" fill="#ef4444" name="Failed" />
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </Paper>
                                </Grid>

                                {/* Recent Tasks */}
                                <Grid item xs={12}>
                                    <Paper sx={{ p: 3, borderRadius: 3 }}>
                                        <Typography variant="h6" fontWeight="bold" mb={2}>Recent Tasks</Typography>
                                        <TableContainer>
                                            <Table size="small">
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell sx={{ fontWeight: 600 }}>Task ID</TableCell>
                                                        <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                                                        <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                                                        <TableCell align="right" sx={{ fontWeight: 600 }}>Duration</TableCell>
                                                        <TableCell sx={{ fontWeight: 600 }}>Time</TableCell>
                                                    </TableRow>
                                                </TableHead>
                                                <TableBody>
                                                    {celeryData.recentTasks.map((task, idx) => (
                                                        <TableRow key={idx}>
                                                            <TableCell><Typography variant="body2" fontFamily="monospace">{task.id}</Typography></TableCell>
                                                            <TableCell>{task.name}</TableCell>
                                                            <TableCell><StatusChip status={task.status} /></TableCell>
                                                            <TableCell align="right">{task.duration ? `${(task.duration / 1000).toFixed(1)}s` : '-'}</TableCell>
                                                            <TableCell>{task.time}</TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </TableContainer>
                                    </Paper>
                                </Grid>
                            </Grid>
                        </Box>
                    </TabPanel>

                    {/* Tab 3: Redis */}
                    <TabPanel value={tabValue} index={3}>
                        <Box sx={{ p: 3 }}>
                            <Grid container spacing={3}>
                                {/* Stats */}
                                <Grid item xs={12}>
                                    <Grid container spacing={2}>
                                        {[
                                            { label: 'Memory Used', value: redisData.usedMemory, icon: <MemoryIcon />, color: '#10b981' },
                                            { label: 'Total Keys', value: redisData.totalKeys.toLocaleString(), icon: <StorageIcon />, color: '#14b8a6' },
                                            { label: 'Hit Rate', value: `${redisData.hitRate}%`, icon: <CheckCircleIcon />, color: '#059669' },
                                            { label: 'Ops/sec', value: redisData.opsPerSec.toLocaleString(), icon: <SpeedIcon />, color: '#f59e0b' },
                                            { label: 'Connected Clients', value: redisData.connectedClients, icon: <WorkIcon />, color: '#10b981' },
                                            { label: 'Queue Length', value: redisData.queueLength, icon: <PendingActionsIcon />, color: '#ef4444' },
                                        ].map((stat, idx) => (
                                            <Grid item xs={6} md={2} key={idx}>
                                                <Paper sx={{ p: 2, borderRadius: 3, textAlign: 'center', bgcolor: alpha(stat.color, 0.05) }}>
                                                    <Typography variant="h5" fontWeight="bold" color={stat.color}>{stat.value}</Typography>
                                                    <Typography variant="caption" color="textSecondary">{stat.label}</Typography>
                                                </Paper>
                                            </Grid>
                                        ))}
                                    </Grid>
                                </Grid>

                                {/* Cache Stats */}
                                <Grid item xs={12} md={6}>
                                    <Paper sx={{ p: 3, borderRadius: 3 }}>
                                        <Typography variant="h6" fontWeight="bold" mb={2}>Cache Performance</Typography>
                                        <Box mb={3}>
                                            <Box display="flex" justifyContent="space-between" mb={1}>
                                                <Typography variant="body2">Hit Rate</Typography>
                                                <Typography variant="body2" fontWeight={600}>{redisData.hitRate}%</Typography>
                                            </Box>
                                            <LinearProgress
                                                variant="determinate"
                                                value={redisData.hitRate}
                                                sx={{ height: 10, borderRadius: 5, bgcolor: '#fee2e2', '& .MuiLinearProgress-bar': { bgcolor: '#10b981' } }}
                                            />
                                        </Box>
                                        <Grid container spacing={2}>
                                            <Grid item xs={4}>
                                                <Box textAlign="center" p={2} bgcolor="#dcfce7" borderRadius={2}>
                                                    <Typography variant="h5" fontWeight="bold" color="#166534">{redisData.cacheStats.hits.toLocaleString()}</Typography>
                                                    <Typography variant="caption">Hits</Typography>
                                                </Box>
                                            </Grid>
                                            <Grid item xs={4}>
                                                <Box textAlign="center" p={2} bgcolor="#fee2e2" borderRadius={2}>
                                                    <Typography variant="h5" fontWeight="bold" color="#991b1b">{redisData.cacheStats.misses.toLocaleString()}</Typography>
                                                    <Typography variant="caption">Misses</Typography>
                                                </Box>
                                            </Grid>
                                            <Grid item xs={4}>
                                                <Box textAlign="center" p={2} bgcolor="#fef3c7" borderRadius={2}>
                                                    <Typography variant="h5" fontWeight="bold" color="#92400e">{redisData.cacheStats.expired.toLocaleString()}</Typography>
                                                    <Typography variant="caption">Expired</Typography>
                                                </Box>
                                            </Grid>
                                        </Grid>
                                    </Paper>
                                </Grid>

                                {/* Key Distribution */}
                                <Grid item xs={12} md={6}>
                                    <Paper sx={{ p: 3, borderRadius: 3 }}>
                                        <Typography variant="h6" fontWeight="bold" mb={2}>Key Distribution</Typography>
                                        <ResponsiveContainer width="100%" height={200}>
                                            <PieChart>
                                                <Pie
                                                    data={redisData.keyDistribution}
                                                    cx="50%"
                                                    cy="50%"
                                                    innerRadius={50}
                                                    outerRadius={80}
                                                    dataKey="value"
                                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                                >
                                                    {redisData.keyDistribution.map((entry, index) => (
                                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                                    ))}
                                                </Pie>
                                                <RechartsTooltip />
                                            </PieChart>
                                        </ResponsiveContainer>
                                    </Paper>
                                </Grid>
                            </Grid>
                        </Box>
                    </TabPanel>

                    {/* Tab 4: Python Agentic Workflows */}
                    <TabPanel value={tabValue} index={4}>
                        <Box sx={{ p: 3 }}>
                            <Grid container spacing={3}>
                                {/* Stats */}
                                <Grid item xs={12}>
                                    <Grid container spacing={2}>
                                        {[
                                            { label: 'Total Workflows', value: n8nData.totalWorkflows, icon: <AccountTreeIcon />, color: '#10b981' },
                                            { label: 'Active', value: n8nData.activeWorkflows, icon: <PlayCircleIcon />, color: '#14b8a6' },
                                            { label: 'Executions (30d)', value: n8nData.totalExecutions, icon: <TaskAltIcon />, color: '#10b981' },
                                            { label: 'Success Rate', value: `${n8nData.successRate}%`, icon: <CheckCircleIcon />, color: '#059669' },
                                        ].map((stat, idx) => (
                                            <Grid item xs={6} md={3} key={idx}>
                                                <Paper sx={{ p: 2, borderRadius: 3, textAlign: 'center', bgcolor: alpha(stat.color, 0.05) }}>
                                                    <Typography variant="h4" fontWeight="bold" color={stat.color}>{stat.value}</Typography>
                                                    <Typography variant="caption" color="textSecondary">{stat.label}</Typography>
                                                </Paper>
                                            </Grid>
                                        ))}
                                    </Grid>
                                </Grid>

                                {/* Workflows Table */}
                                <Grid item xs={12}>
                                    <Paper sx={{ p: 3, borderRadius: 3 }}>
                                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                                            <Typography variant="h6" fontWeight="bold">Python Agentic Workflows</Typography>
                                            <Chip label="DDN AI Analysis System" size="small" color="primary" />
                                        </Box>
                                        <TableContainer>
                                            <Table>
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell sx={{ fontWeight: 600 }}>Workflow Name</TableCell>
                                                        <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                                                        <TableCell sx={{ fontWeight: 600 }}>Version</TableCell>
                                                        <TableCell align="center" sx={{ fontWeight: 600 }}>Nodes</TableCell>
                                                        <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                                                        <TableCell sx={{ fontWeight: 600 }}>Last Updated</TableCell>
                                                    </TableRow>
                                                </TableHead>
                                                <TableBody>
                                                    {n8nData.workflows.length > 0 ? n8nData.workflows.map((wf, idx) => (
                                                        <TableRow key={idx} sx={{ '&:hover': { bgcolor: '#f8fafc' } }}>
                                                            <TableCell>
                                                                <Box display="flex" alignItems="center" gap={1}>
                                                                    <AccountTreeIcon sx={{ color: '#10b981', fontSize: 20 }} />
                                                                    <Box>
                                                                        <Typography variant="body2" fontWeight={600}>{wf.name}</Typography>
                                                                        {wf.description && (
                                                                            <Typography variant="caption" color="textSecondary" sx={{ display: 'block', maxWidth: 300 }}>
                                                                                {wf.description.substring(0, 80)}...
                                                                            </Typography>
                                                                        )}
                                                                    </Box>
                                                                </Box>
                                                            </TableCell>
                                                            <TableCell>
                                                                <Chip
                                                                    label={wf.type?.replace('_', ' ').toUpperCase() || 'COMPLETE'}
                                                                    size="small"
                                                                    sx={{
                                                                        bgcolor: wf.type === 'manual_trigger' ? alpha('#10b981', 0.1) :
                                                                                 wf.type === 'refinement' ? '#fef3c7' :
                                                                                 wf.type === 'auto_fix' ? '#dcfce7' : '#f1f5f9',
                                                                        color: wf.type === 'manual_trigger' ? '#10b981' :
                                                                               wf.type === 'refinement' ? '#92400e' :
                                                                               wf.type === 'auto_fix' ? '#166534' : '#475569',
                                                                        fontSize: '0.7rem'
                                                                    }}
                                                                />
                                                            </TableCell>
                                                            <TableCell>
                                                                <Typography variant="body2" fontFamily="monospace">{wf.version}</Typography>
                                                            </TableCell>
                                                            <TableCell align="center">
                                                                <Chip label={wf.nodeCount} size="small" color="default" />
                                                            </TableCell>
                                                            <TableCell><StatusChip status={wf.status} /></TableCell>
                                                            <TableCell>
                                                                <Typography variant="body2">{wf.lastRun}</Typography>
                                                            </TableCell>
                                                        </TableRow>
                                                    )) : (
                                                        <TableRow>
                                                            <TableCell colSpan={6} align="center">
                                                                <Typography color="textSecondary">No workflows found. Check /implementation/workflows/ directory.</Typography>
                                                            </TableCell>
                                                        </TableRow>
                                                    )}
                                                </TableBody>
                                            </Table>
                                        </TableContainer>
                                    </Paper>
                                </Grid>
                            </Grid>
                        </Box>
                    </TabPanel>
                </Paper>

                {/* Info Alert */}
                <Alert severity="info" sx={{ borderRadius: 3 }}>
                    <Typography variant="body2">
                        <strong>Note:</strong> Real-time monitoring dashboards:
                        Langfuse (<a href="http://localhost:3000" target="_blank" rel="noreferrer">:3000</a>),
                        Flower (<a href="http://localhost:5555" target="_blank" rel="noreferrer">:5555</a>).
                        Agentic Workflows are Python-based and defined in <code>/implementation/workflows/</code>.
                    </Typography>
                </Alert>
            </Container>
        </Box>
    );
};

export default ServicesMonitoringPreview;
