import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import {
    Box, Container, Paper, Typography, Grid, Button, Chip, Avatar, IconButton,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TablePagination,
    TextField, MenuItem, Dialog, DialogTitle, DialogContent, DialogActions,
    Card, CardContent, Alert, Tooltip, Divider, InputAdornment, LinearProgress,
    Tabs, Tab, Checkbox, Badge, Stepper, Step, StepLabel, FormControlLabel, Switch,
    Skeleton, CircularProgress
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import BugReportIcon from '@mui/icons-material/BugReport';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import LinkIcon from '@mui/icons-material/Link';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import PersonIcon from '@mui/icons-material/Person';
import ScheduleIcon from '@mui/icons-material/Schedule';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import AssignmentIcon from '@mui/icons-material/Assignment';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ErrorIcon from '@mui/icons-material/Error';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import PlaylistAddCheckIcon from '@mui/icons-material/PlaylistAddCheck';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import VerifiedIcon from '@mui/icons-material/Verified';
import WarningIcon from '@mui/icons-material/Warning';
import { jiraAPI } from '../services/api';

const priorities = ['Critical', 'High', 'Medium', 'Low'];
const statuses = ['Open', 'In Progress', 'Resolved', 'Closed'];

const getPriorityColor = (priority) => {
    const colors = {
        Critical: { bg: '#fee2e2', color: '#991b1b' },
        High: { bg: '#ffedd5', color: '#9a3412' },
        Medium: { bg: '#fef3c7', color: '#92400e' },
        Low: { bg: '#dcfce7', color: '#166534' }
    };
    return colors[priority] || colors.Medium;
};

const getStatusColor = (status) => {
    const colors = {
        Open: { bg: '#dbeafe', color: '#1e40af' },
        'In Progress': { bg: '#fef3c7', color: '#92400e' },
        Resolved: { bg: '#dcfce7', color: '#166534' },
        Closed: { bg: '#f1f5f9', color: '#64748b' }
    };
    return colors[status] || colors.Open;
};

const getSeverityColor = (severity) => {
    const colors = {
        CRITICAL: { bg: '#fee2e2', color: '#991b1b' },
        HIGH: { bg: '#ffedd5', color: '#9a3412' },
        MEDIUM: { bg: '#fef3c7', color: '#92400e' },
        LOW: { bg: '#dcfce7', color: '#166534' }
    };
    return colors[severity] || colors.MEDIUM;
};

const JiraBugsPreview = () => {
    const [activeTab, setActiveTab] = useState(0);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [priorityFilter, setPriorityFilter] = useState('');
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [viewDialogOpen, setViewDialogOpen] = useState(false);
    const [selectedBug, setSelectedBug] = useState(null);
    const [creating, setCreating] = useState(false);
    const [selectAnalysesDialogOpen, setSelectAnalysesDialogOpen] = useState(false);
    const [selectedAnalyses, setSelectedAnalyses] = useState([]);
    const [bulkCreateStep, setBulkCreateStep] = useState(0);
    const [bulkCreating, setBulkCreating] = useState(false);

    // Real data state
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [jiraBugs, setJiraBugs] = useState([]);
    const [approvedAnalyses, setApprovedAnalyses] = useState([]);

    const [refreshing, setRefreshing] = useState(false);
    const location = useLocation();

    // Fetch data from API
    const fetchData = useCallback(async (isRefresh = false) => {
        try {
            if (isRefresh) setRefreshing(true);
            else setLoading(true);

            // Fetch Jira bugs
            const bugsResponse = await jiraAPI.getBugs({ limit: 50 });
            const bugsData = bugsResponse?.data || bugsResponse;
            const bugs = (bugsData?.bugs || []).map(bug => ({
                id: bug.jira_key || bug.id,
                title: bug.summary || bug.title,
                status: bug.status ? bug.status.charAt(0).toUpperCase() + bug.status.slice(1).replace('_', ' ') : 'Open',
                priority: bug.priority ? bug.priority.charAt(0).toUpperCase() + bug.priority.slice(1) : 'Medium',
                assignee: bug.assignee,
                reporter: bug.reporter || 'AI Analysis System',
                createdAt: bug.created_at ? new Date(bug.created_at).toLocaleDateString() : '-',
                linkedFailure: bug.build_id ? `#${bug.build_id}` : '-',
                classification: bug.classification || 'UNKNOWN',
                aiConfidence: bug.confidence_score || 0.85,
                jiraUrl: bug.jira_url || `https://jira.example.com/browse/${bug.jira_key}`
            }));
            setJiraBugs(bugs);

            // Fetch approved analyses
            const analysesResponse = await jiraAPI.getApprovedAnalyses(50);
            const analysesData = analysesResponse?.data || analysesResponse;
            const analyses = (analysesData?.analyses || []).map((a, idx) => ({
                id: a.analysis_id || `AI-${2000 + idx}`,
                buildId: a.build_id ? `#${a.build_id}` : '-',
                testName: a.test_name || '-',
                className: a.class_name || '-',
                errorMessage: a.error_message || a.root_cause || '-',
                classification: a.classification || 'UNKNOWN',
                rootCause: a.root_cause || '-',
                recommendation: a.recommendation || '-',
                aiConfidence: a.confidence_score || 0.8,
                severity: a.severity || 'MEDIUM',
                acceptedAt: a.validated_at ? new Date(a.validated_at).toLocaleString() : '-',
                acceptedBy: a.validator_name || 'system',
                bugCreated: false,
                linkedBugId: null
            }));
            setApprovedAnalyses(analyses);
            setError(null);
        } catch (err) {
            console.error('Error fetching Jira data:', err);
            setError(err.message || 'Failed to fetch data');
            setJiraBugs([]);
            setApprovedAnalyses([]);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, []);

    // Auto-fetch on mount and navigation
    useEffect(() => {
        fetchData();
    }, [location.key, fetchData]);

    const handleRefresh = () => fetchData(true);

    // Bug creation form state
    const [bugForm, setBugForm] = useState({
        title: '',
        priority: 'High',
        assignee: '',
        description: ''
    });

    const pendingAnalyses = approvedAnalyses.filter(a => !a.bugCreated);
    const convertedAnalyses = approvedAnalyses.filter(a => a.bugCreated);

    const stats = {
        total: jiraBugs.length,
        open: jiraBugs.filter(b => b.status === 'Open').length,
        inProgress: jiraBugs.filter(b => b.status === 'In Progress').length,
        resolved: jiraBugs.filter(b => b.status === 'Resolved' || b.status === 'Closed').length,
        pendingConversion: pendingAnalyses.length
    };

    const handleCreateBugFromAnalysis = (analysis) => {
        setBugForm({
            title: `[AI] ${analysis.errorMessage.substring(0, 60)}...`,
            priority: analysis.severity === 'HIGH' ? 'High' : analysis.severity === 'CRITICAL' ? 'Critical' : 'Medium',
            assignee: '',
            description: `**Linked Failure:** ${analysis.buildId}\n**Test:** ${analysis.testName}\n**Class:** ${analysis.className}\n**Classification:** ${analysis.classification}\n\n**Error Message:**\n${analysis.errorMessage}\n\n**AI Root Cause Analysis:**\n${analysis.rootCause}\n\n**AI Recommendation:**\n${analysis.recommendation}\n\n**AI Confidence:** ${Math.round(analysis.aiConfidence * 100)}%\n\n**Accepted By:** ${analysis.acceptedBy}\n**Accepted At:** ${analysis.acceptedAt}`
        });
        setCreateDialogOpen(true);
    };

    const handleSubmitBug = () => {
        setCreating(true);
        setTimeout(() => {
            setCreating(false);
            setCreateDialogOpen(false);
            setBugForm({ title: '', priority: 'High', assignee: '', description: '' });
        }, 2000);
    };

    const handleViewBug = (bug) => {
        setSelectedBug(bug);
        setViewDialogOpen(true);
    };

    const handleSelectAnalysis = (id) => {
        setSelectedAnalyses(prev =>
            prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
        );
    };

    const handleSelectAllPending = () => {
        if (selectedAnalyses.length === pendingAnalyses.length) {
            setSelectedAnalyses([]);
        } else {
            setSelectedAnalyses(pendingAnalyses.map(a => a.id));
        }
    };

    const handleOpenBulkCreate = () => {
        setSelectAnalysesDialogOpen(true);
        setBulkCreateStep(0);
        setSelectedAnalyses([]);
    };

    const handleBulkCreateBugs = () => {
        setBulkCreating(true);
        setBulkCreateStep(1);

        // Simulate creating bugs one by one
        let current = 0;
        const interval = setInterval(() => {
            current++;
            if (current >= selectedAnalyses.length) {
                clearInterval(interval);
                setBulkCreating(false);
                setBulkCreateStep(2);
            }
        }, 1000);
    };

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc', pb: 4 }}>
            {/* Header */}
            <Box
                sx={{
                    background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
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
                                Jira Bug Tracking
                            </Typography>
                            <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                                Create bugs from approved AI analyses and track progress
                            </Typography>
                        </Box>
                        <Box display="flex" gap={2}>
                            <Badge badgeContent={pendingAnalyses.length} color="warning">
                                <Button
                                    variant="contained"
                                    startIcon={<PlaylistAddCheckIcon />}
                                    onClick={handleOpenBulkCreate}
                                    sx={{ bgcolor: 'white', color: '#2563eb', '&:hover': { bgcolor: '#f0f9ff' } }}
                                >
                                    Convert Approved Analyses
                                </Button>
                            </Badge>
                            <Button
                                variant="contained"
                                startIcon={<OpenInNewIcon />}
                                onClick={() => window.open('https://company.atlassian.net', '_blank')}
                                sx={{ bgcolor: 'rgba(255,255,255,0.2)', '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' } }}
                            >
                                Open Jira
                            </Button>
                        </Box>
                    </Box>
                </Container>
            </Box>

            <Container maxWidth="xl">
                {/* Stats Cards */}
                <Grid container spacing={3} mb={4}>
                    {[
                        { label: 'Total Bugs', value: stats.total, icon: <BugReportIcon />, color: '#2563eb' },
                        { label: 'Open', value: stats.open, icon: <HourglassEmptyIcon />, color: '#3b82f6' },
                        { label: 'In Progress', value: stats.inProgress, icon: <AssignmentIcon />, color: '#f59e0b' },
                        { label: 'Resolved', value: stats.resolved, icon: <CheckCircleIcon />, color: '#10b981' },
                        { label: 'Pending Conversion', value: stats.pendingConversion, icon: <ThumbUpIcon />, color: '#8b5cf6' },
                    ].map((stat, idx) => (
                        <Grid item xs={6} md={2.4} key={idx}>
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
                <Paper elevation={0} sx={{ borderRadius: 4, mb: 3, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                    <Tabs
                        value={activeTab}
                        onChange={(e, v) => setActiveTab(v)}
                        sx={{ borderBottom: '1px solid', borderColor: 'divider', px: 2 }}
                    >
                        <Tab
                            icon={<BugReportIcon />}
                            label="Jira Bugs"
                            iconPosition="start"
                        />
                        <Tab
                            icon={
                                <Badge badgeContent={pendingAnalyses.length} color="warning" sx={{ '& .MuiBadge-badge': { right: -8 } }}>
                                    <ThumbUpIcon />
                                </Badge>
                            }
                            label="Approved Analyses"
                            iconPosition="start"
                            sx={{ ml: 2 }}
                        />
                    </Tabs>
                </Paper>

                {/* Tab 0: Jira Bugs */}
                {activeTab === 0 && (
                    <>
                        {/* Filters */}
                        <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                            <Grid container spacing={2} alignItems="center">
                                <Grid item xs={12} md={4}>
                                    <TextField
                                        fullWidth
                                        placeholder="Search bugs..."
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                        InputProps={{
                                            startAdornment: <InputAdornment position="start"><SearchIcon color="action" /></InputAdornment>
                                        }}
                                        sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                                    />
                                </Grid>
                                <Grid item xs={6} md={3}>
                                    <TextField
                                        fullWidth
                                        select
                                        label="Status"
                                        value={statusFilter}
                                        onChange={(e) => setStatusFilter(e.target.value)}
                                        sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                                    >
                                        <MenuItem value="">All Statuses</MenuItem>
                                        {statuses.map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
                                    </TextField>
                                </Grid>
                                <Grid item xs={6} md={3}>
                                    <TextField
                                        fullWidth
                                        select
                                        label="Priority"
                                        value={priorityFilter}
                                        onChange={(e) => setPriorityFilter(e.target.value)}
                                        sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                                    >
                                        <MenuItem value="">All Priorities</MenuItem>
                                        {priorities.map(p => <MenuItem key={p} value={p}>{p}</MenuItem>)}
                                    </TextField>
                                </Grid>
                                <Grid item xs={12} md={2}>
                                    <Button fullWidth variant="outlined" sx={{ borderRadius: 3, py: 1.8 }}>
                                        Clear Filters
                                    </Button>
                                </Grid>
                            </Grid>
                        </Paper>

                        {/* Bugs Table */}
                        <Paper elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', overflow: 'hidden' }}>
                            <TableContainer>
                                <Table>
                                    <TableHead>
                                        <TableRow sx={{ bgcolor: '#f8fafc' }}>
                                            <TableCell sx={{ fontWeight: 600 }}>Bug ID</TableCell>
                                            <TableCell sx={{ fontWeight: 600 }}>Title</TableCell>
                                            <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                                            <TableCell sx={{ fontWeight: 600 }}>Priority</TableCell>
                                            <TableCell sx={{ fontWeight: 600 }}>Linked Failure</TableCell>
                                            <TableCell sx={{ fontWeight: 600 }}>AI Confidence</TableCell>
                                            <TableCell sx={{ fontWeight: 600 }}>Assignee</TableCell>
                                            <TableCell sx={{ fontWeight: 600 }}>Created</TableCell>
                                            <TableCell align="center" sx={{ fontWeight: 600 }}>Actions</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {loading ? (
                                            [...Array(5)].map((_, idx) => (
                                                <TableRow key={idx}>
                                                    <TableCell><Skeleton width={80} /></TableCell>
                                                    <TableCell><Skeleton width={200} /></TableCell>
                                                    <TableCell><Skeleton width={80} /></TableCell>
                                                    <TableCell><Skeleton width={80} /></TableCell>
                                                    <TableCell><Skeleton width={80} /></TableCell>
                                                    <TableCell><Skeleton width={80} /></TableCell>
                                                    <TableCell><Skeleton width={100} /></TableCell>
                                                    <TableCell><Skeleton width={80} /></TableCell>
                                                    <TableCell><Skeleton width={40} /></TableCell>
                                                </TableRow>
                                            ))
                                        ) : error ? (
                                            <TableRow>
                                                <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                                                    <ErrorIcon sx={{ fontSize: 48, color: 'error.main', mb: 1 }} />
                                                    <Typography color="error">{error}</Typography>
                                                </TableCell>
                                            </TableRow>
                                        ) : jiraBugs.length === 0 ? (
                                            <TableRow>
                                                <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                                                    <BugReportIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                                                    <Typography color="textSecondary">No Jira bugs found</Typography>
                                                </TableCell>
                                            </TableRow>
                                        ) : jiraBugs.map((bug) => {
                                            const priorityColors = getPriorityColor(bug.priority);
                                            const statusColors = getStatusColor(bug.status);

                                            return (
                                                <TableRow key={bug.id} sx={{ '&:hover': { bgcolor: '#f8fafc' }, cursor: 'pointer' }} onClick={() => handleViewBug(bug)}>
                                                    <TableCell>
                                                        <Chip
                                                            label={bug.id}
                                                            size="small"
                                                            sx={{ bgcolor: '#dbeafe', color: '#1e40af', fontWeight: 600, fontFamily: 'monospace' }}
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        <Box display="flex" alignItems="center" gap={1}>
                                                            {bug.reporter === 'AI Analysis System' && (
                                                                <Tooltip title="Created from AI Analysis">
                                                                    <SmartToyIcon sx={{ color: '#8b5cf6', fontSize: 18 }} />
                                                                </Tooltip>
                                                            )}
                                                            <Typography variant="body2" sx={{ maxWidth: 300 }} noWrap>{bug.title}</Typography>
                                                        </Box>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip label={bug.status} size="small" sx={{ bgcolor: statusColors.bg, color: statusColors.color, fontWeight: 600, fontSize: '0.7rem' }} />
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip
                                                            icon={bug.priority === 'Critical' ? <PriorityHighIcon /> : null}
                                                            label={bug.priority}
                                                            size="small"
                                                            sx={{ bgcolor: priorityColors.bg, color: priorityColors.color, fontWeight: 600, fontSize: '0.7rem', '& .MuiChip-icon': { color: 'inherit' } }}
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip
                                                            icon={<LinkIcon />}
                                                            label={bug.linkedFailure}
                                                            size="small"
                                                            variant="outlined"
                                                            sx={{ fontSize: '0.7rem' }}
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        <Box display="flex" alignItems="center" gap={1}>
                                                            <LinearProgress
                                                                variant="determinate"
                                                                value={bug.aiConfidence * 100}
                                                                sx={{ width: 60, height: 6, borderRadius: 3, bgcolor: '#e2e8f0' }}
                                                            />
                                                            <Typography variant="caption">{Math.round(bug.aiConfidence * 100)}%</Typography>
                                                        </Box>
                                                    </TableCell>
                                                    <TableCell>
                                                        {bug.assignee ? (
                                                            <Box display="flex" alignItems="center" gap={1}>
                                                                <Avatar sx={{ width: 24, height: 24, fontSize: '0.7rem' }}>{bug.assignee[0].toUpperCase()}</Avatar>
                                                                <Typography variant="body2" noWrap sx={{ maxWidth: 120 }}>{bug.assignee.split('@')[0]}</Typography>
                                                            </Box>
                                                        ) : (
                                                            <Chip label="Unassigned" size="small" variant="outlined" />
                                                        )}
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2" color="textSecondary">{bug.createdAt}</Typography>
                                                    </TableCell>
                                                    <TableCell align="center">
                                                        <Tooltip title="Open in Jira">
                                                            <IconButton size="small" onClick={(e) => { e.stopPropagation(); window.open(bug.jiraUrl, '_blank'); }}>
                                                                <OpenInNewIcon fontSize="small" sx={{ color: '#2563eb' }} />
                                                            </IconButton>
                                                        </Tooltip>
                                                    </TableCell>
                                                </TableRow>
                                            );
                                        })}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                            <TablePagination
                                rowsPerPageOptions={[10, 20, 50]}
                                component="div"
                                count={jiraBugs.length}
                                rowsPerPage={rowsPerPage}
                                page={page}
                                onPageChange={(e, p) => setPage(p)}
                                onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value)); setPage(0); }}
                            />
                        </Paper>
                    </>
                )}

                {/* Tab 1: Approved Analyses */}
                {activeTab === 1 && (
                    <Paper elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', overflow: 'hidden' }}>
                        <Box sx={{ p: 3, borderBottom: '1px solid', borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Box>
                                <Typography variant="h6" fontWeight={600}>
                                    Approved AI Analyses
                                </Typography>
                                <Typography variant="body2" color="textSecondary">
                                    Select analyses to convert into Jira bugs
                                </Typography>
                            </Box>
                            <Box display="flex" gap={2}>
                                <Button
                                    variant="outlined"
                                    onClick={handleSelectAllPending}
                                    disabled={pendingAnalyses.length === 0}
                                >
                                    {selectedAnalyses.length === pendingAnalyses.length ? 'Deselect All' : 'Select All Pending'}
                                </Button>
                                <Button
                                    variant="contained"
                                    startIcon={<BugReportIcon />}
                                    disabled={selectedAnalyses.length === 0}
                                    onClick={() => {
                                        setSelectAnalysesDialogOpen(true);
                                        setBulkCreateStep(0);
                                    }}
                                    sx={{ bgcolor: '#2563eb' }}
                                >
                                    Create {selectedAnalyses.length > 0 ? `${selectedAnalyses.length} ` : ''}Bug{selectedAnalyses.length !== 1 ? 's' : ''}
                                </Button>
                            </Box>
                        </Box>

                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow sx={{ bgcolor: '#f8fafc' }}>
                                        <TableCell padding="checkbox">
                                            <Checkbox
                                                checked={selectedAnalyses.length === pendingAnalyses.length && pendingAnalyses.length > 0}
                                                indeterminate={selectedAnalyses.length > 0 && selectedAnalyses.length < pendingAnalyses.length}
                                                onChange={handleSelectAllPending}
                                                disabled={pendingAnalyses.length === 0}
                                            />
                                        </TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Analysis ID</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Build / Test</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Classification</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Severity</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>AI Confidence</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Accepted By</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                                        <TableCell align="center" sx={{ fontWeight: 600 }}>Actions</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {loading ? (
                                        [...Array(3)].map((_, idx) => (
                                            <TableRow key={idx}>
                                                <TableCell><Skeleton width={30} /></TableCell>
                                                <TableCell><Skeleton width={80} /></TableCell>
                                                <TableCell><Skeleton width={100} /></TableCell>
                                                <TableCell><Skeleton width={80} /></TableCell>
                                                <TableCell><Skeleton width={60} /></TableCell>
                                                <TableCell><Skeleton width={80} /></TableCell>
                                                <TableCell><Skeleton width={100} /></TableCell>
                                                <TableCell><Skeleton width={60} /></TableCell>
                                                <TableCell><Skeleton width={40} /></TableCell>
                                            </TableRow>
                                        ))
                                    ) : approvedAnalyses.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                                                <SmartToyIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                                                <Typography color="textSecondary">No approved analyses found</Typography>
                                            </TableCell>
                                        </TableRow>
                                    ) : approvedAnalyses.map((analysis) => {
                                        const severityColors = getSeverityColor(analysis.severity);
                                        const isPending = !analysis.bugCreated;

                                        return (
                                            <TableRow
                                                key={analysis.id}
                                                sx={{
                                                    '&:hover': { bgcolor: '#f8fafc' },
                                                    bgcolor: analysis.bugCreated ? alpha('#10b981', 0.05) : 'inherit'
                                                }}
                                            >
                                                <TableCell padding="checkbox">
                                                    <Checkbox
                                                        checked={selectedAnalyses.includes(analysis.id)}
                                                        onChange={() => handleSelectAnalysis(analysis.id)}
                                                        disabled={analysis.bugCreated}
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    <Chip
                                                        icon={<VerifiedIcon />}
                                                        label={analysis.id}
                                                        size="small"
                                                        sx={{ bgcolor: '#f0fdf4', color: '#166534', fontWeight: 600, fontFamily: 'monospace' }}
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    <Box>
                                                        <Typography variant="body2" fontWeight={600}>{analysis.buildId}</Typography>
                                                        <Typography variant="caption" color="textSecondary">{analysis.testName}</Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Chip
                                                        label={analysis.classification}
                                                        size="small"
                                                        sx={{ bgcolor: '#f1f5f9', fontSize: '0.7rem' }}
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    <Chip
                                                        label={analysis.severity}
                                                        size="small"
                                                        sx={{ bgcolor: severityColors.bg, color: severityColors.color, fontWeight: 600, fontSize: '0.7rem' }}
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    <Box display="flex" alignItems="center" gap={1}>
                                                        <LinearProgress
                                                            variant="determinate"
                                                            value={analysis.aiConfidence * 100}
                                                            sx={{ width: 60, height: 6, borderRadius: 3, bgcolor: '#e2e8f0' }}
                                                        />
                                                        <Typography variant="caption">{Math.round(analysis.aiConfidence * 100)}%</Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Box display="flex" alignItems="center" gap={1}>
                                                        <Avatar sx={{ width: 24, height: 24, fontSize: '0.7rem', bgcolor: '#8b5cf6' }}>
                                                            {analysis.acceptedBy[0].toUpperCase()}
                                                        </Avatar>
                                                        <Box>
                                                            <Typography variant="body2" noWrap sx={{ maxWidth: 100 }}>
                                                                {analysis.acceptedBy.split('@')[0]}
                                                            </Typography>
                                                            <Typography variant="caption" color="textSecondary">
                                                                {analysis.acceptedAt}
                                                            </Typography>
                                                        </Box>
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    {analysis.bugCreated ? (
                                                        <Chip
                                                            icon={<CheckCircleIcon />}
                                                            label={analysis.linkedBugId}
                                                            size="small"
                                                            sx={{ bgcolor: '#dcfce7', color: '#166534', fontWeight: 600 }}
                                                        />
                                                    ) : (
                                                        <Chip
                                                            label="Pending"
                                                            size="small"
                                                            sx={{ bgcolor: '#fef3c7', color: '#92400e' }}
                                                        />
                                                    )}
                                                </TableCell>
                                                <TableCell align="center">
                                                    {!analysis.bugCreated && (
                                                        <Tooltip title="Create Bug">
                                                            <IconButton
                                                                size="small"
                                                                onClick={() => handleCreateBugFromAnalysis(analysis)}
                                                                sx={{ color: '#2563eb' }}
                                                            >
                                                                <BugReportIcon fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>
                                                    )}
                                                    {analysis.bugCreated && (
                                                        <Tooltip title="Open Bug in Jira">
                                                            <IconButton size="small" onClick={() => window.open(`https://company.atlassian.net/browse/${analysis.linkedBugId}`, '_blank')}>
                                                                <OpenInNewIcon fontSize="small" sx={{ color: '#2563eb' }} />
                                                            </IconButton>
                                                        </Tooltip>
                                                    )}
                                                </TableCell>
                                            </TableRow>
                                        );
                                    })}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                )}

                {/* Create Bug Dialog */}
                <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
                    <DialogTitle sx={{ fontWeight: 600 }}>
                        <Box display="flex" alignItems="center" gap={1}>
                            <BugReportIcon sx={{ color: '#2563eb' }} />
                            Create Jira Bug from AI Analysis
                        </Box>
                    </DialogTitle>
                    <DialogContent>
                        <Alert severity="info" sx={{ mb: 3 }}>
                            <Box display="flex" alignItems="center" gap={1}>
                                <SmartToyIcon />
                                <Typography variant="body2">
                                    Pre-filled from approved AI analysis
                                </Typography>
                            </Box>
                        </Alert>

                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    label="Bug Title"
                                    value={bugForm.title}
                                    onChange={(e) => setBugForm({ ...bugForm, title: e.target.value })}
                                    sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                />
                            </Grid>
                            <Grid item xs={6}>
                                <TextField
                                    fullWidth
                                    select
                                    label="Priority"
                                    value={bugForm.priority}
                                    onChange={(e) => setBugForm({ ...bugForm, priority: e.target.value })}
                                    sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                >
                                    {priorities.map(p => <MenuItem key={p} value={p}>{p}</MenuItem>)}
                                </TextField>
                            </Grid>
                            <Grid item xs={6}>
                                <TextField
                                    fullWidth
                                    label="Assignee (email)"
                                    value={bugForm.assignee}
                                    onChange={(e) => setBugForm({ ...bugForm, assignee: e.target.value })}
                                    placeholder="Leave empty for unassigned"
                                    sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    multiline
                                    rows={12}
                                    label="Description"
                                    value={bugForm.description}
                                    onChange={(e) => setBugForm({ ...bugForm, description: e.target.value })}
                                    sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                />
                            </Grid>
                        </Grid>
                    </DialogContent>
                    <DialogActions sx={{ p: 3 }}>
                        <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
                        <Button
                            variant="contained"
                            startIcon={creating ? <HourglassEmptyIcon /> : <SendIcon />}
                            onClick={handleSubmitBug}
                            disabled={creating || !bugForm.title}
                            sx={{ bgcolor: '#2563eb' }}
                        >
                            {creating ? 'Creating in Jira...' : 'Create Bug in Jira'}
                        </Button>
                    </DialogActions>
                </Dialog>

                {/* Bulk Create Bugs Dialog */}
                <Dialog open={selectAnalysesDialogOpen} onClose={() => !bulkCreating && setSelectAnalysesDialogOpen(false)} maxWidth="md" fullWidth>
                    <DialogTitle sx={{ fontWeight: 600 }}>
                        <Box display="flex" alignItems="center" gap={1}>
                            <PlaylistAddCheckIcon sx={{ color: '#8b5cf6' }} />
                            Convert Approved Analyses to Bugs
                        </Box>
                    </DialogTitle>
                    <DialogContent>
                        <Stepper activeStep={bulkCreateStep} sx={{ mb: 4, mt: 2 }}>
                            <Step>
                                <StepLabel>Select Analyses</StepLabel>
                            </Step>
                            <Step>
                                <StepLabel>Creating Bugs</StepLabel>
                            </Step>
                            <Step>
                                <StepLabel>Complete</StepLabel>
                            </Step>
                        </Stepper>

                        {bulkCreateStep === 0 && (
                            <>
                                <Alert severity="info" sx={{ mb: 3 }}>
                                    Select approved AI analyses to convert into Jira bugs. Each analysis will create a separate bug with pre-filled information.
                                </Alert>

                                {pendingAnalyses.length === 0 ? (
                                    <Alert severity="success">
                                        All approved analyses have already been converted to bugs!
                                    </Alert>
                                ) : (
                                    <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                                        {pendingAnalyses.map((analysis) => (
                                            <Card
                                                key={analysis.id}
                                                variant="outlined"
                                                sx={{
                                                    mb: 1,
                                                    cursor: 'pointer',
                                                    border: selectedAnalyses.includes(analysis.id) ? '2px solid #2563eb' : '1px solid #e2e8f0',
                                                    bgcolor: selectedAnalyses.includes(analysis.id) ? alpha('#2563eb', 0.05) : 'white'
                                                }}
                                                onClick={() => handleSelectAnalysis(analysis.id)}
                                            >
                                                <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                                                    <Box display="flex" alignItems="center" gap={2}>
                                                        <Checkbox checked={selectedAnalyses.includes(analysis.id)} />
                                                        <Box flex={1}>
                                                            <Box display="flex" alignItems="center" gap={1}>
                                                                <Chip label={analysis.buildId} size="small" sx={{ fontFamily: 'monospace' }} />
                                                                <Typography variant="body2" fontWeight={600}>
                                                                    {analysis.testName}
                                                                </Typography>
                                                            </Box>
                                                            <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mt: 0.5 }}>
                                                                {analysis.errorMessage.substring(0, 80)}...
                                                            </Typography>
                                                        </Box>
                                                        <Chip
                                                            label={analysis.severity}
                                                            size="small"
                                                            sx={{
                                                                bgcolor: getSeverityColor(analysis.severity).bg,
                                                                color: getSeverityColor(analysis.severity).color
                                                            }}
                                                        />
                                                        <Typography variant="body2" fontWeight={600} color="primary">
                                                            {Math.round(analysis.aiConfidence * 100)}%
                                                        </Typography>
                                                    </Box>
                                                </CardContent>
                                            </Card>
                                        ))}
                                    </Box>
                                )}
                            </>
                        )}

                        {bulkCreateStep === 1 && (
                            <Box sx={{ textAlign: 'center', py: 4 }}>
                                <Box sx={{ position: 'relative', display: 'inline-flex', mb: 3 }}>
                                    <Box sx={{ width: 100, height: 100 }}>
                                        <svg viewBox="0 0 100 100">
                                            <circle cx="50" cy="50" r="45" fill="none" stroke="#e2e8f0" strokeWidth="8" />
                                            <circle
                                                cx="50" cy="50" r="45"
                                                fill="none"
                                                stroke="#2563eb"
                                                strokeWidth="8"
                                                strokeDasharray={`${(283 * selectedAnalyses.length) / pendingAnalyses.length} 283`}
                                                strokeLinecap="round"
                                                transform="rotate(-90 50 50)"
                                            />
                                        </svg>
                                    </Box>
                                    <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <AutoFixHighIcon sx={{ fontSize: 40, color: '#2563eb' }} />
                                    </Box>
                                </Box>
                                <Typography variant="h6">Creating Jira Bugs...</Typography>
                                <Typography variant="body2" color="textSecondary">
                                    Processing {selectedAnalyses.length} analyses
                                </Typography>
                                <LinearProgress sx={{ mt: 3, maxWidth: 300, mx: 'auto' }} />
                            </Box>
                        )}

                        {bulkCreateStep === 2 && (
                            <Box sx={{ textAlign: 'center', py: 4 }}>
                                <Avatar sx={{ width: 80, height: 80, bgcolor: '#dcfce7', mx: 'auto', mb: 2 }}>
                                    <CheckCircleIcon sx={{ fontSize: 48, color: '#166534' }} />
                                </Avatar>
                                <Typography variant="h6" color="success.main">Bugs Created Successfully!</Typography>
                                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                                    {selectedAnalyses.length} bugs have been created in Jira
                                </Typography>
                                <Box sx={{ mt: 3 }}>
                                    {selectedAnalyses.map((id, idx) => (
                                        <Chip
                                            key={id}
                                            label={`DDN-${1236 + idx}`}
                                            sx={{ m: 0.5, bgcolor: '#dbeafe', color: '#1e40af' }}
                                            onClick={() => window.open(`https://company.atlassian.net/browse/DDN-${1236 + idx}`, '_blank')}
                                            icon={<OpenInNewIcon />}
                                        />
                                    ))}
                                </Box>
                            </Box>
                        )}
                    </DialogContent>
                    <DialogActions sx={{ p: 3 }}>
                        {bulkCreateStep === 0 && (
                            <>
                                <Button onClick={() => setSelectAnalysesDialogOpen(false)}>Cancel</Button>
                                <Button
                                    variant="contained"
                                    startIcon={<BugReportIcon />}
                                    onClick={handleBulkCreateBugs}
                                    disabled={selectedAnalyses.length === 0}
                                    sx={{ bgcolor: '#2563eb' }}
                                >
                                    Create {selectedAnalyses.length} Bug{selectedAnalyses.length !== 1 ? 's' : ''}
                                </Button>
                            </>
                        )}
                        {bulkCreateStep === 2 && (
                            <Button variant="contained" onClick={() => { setSelectAnalysesDialogOpen(false); setSelectedAnalyses([]); }}>
                                Done
                            </Button>
                        )}
                    </DialogActions>
                </Dialog>

                {/* View Bug Dialog */}
                <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="md" fullWidth>
                    {selectedBug && (
                        <>
                            <DialogTitle sx={{ fontWeight: 600 }}>
                                <Box display="flex" alignItems="center" gap={2}>
                                    <Chip label={selectedBug.id} sx={{ bgcolor: '#dbeafe', color: '#1e40af', fontWeight: 600 }} />
                                    <Typography variant="h6">{selectedBug.title}</Typography>
                                </Box>
                            </DialogTitle>
                            <DialogContent>
                                <Grid container spacing={3}>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="textSecondary">Status</Typography>
                                        <Chip label={selectedBug.status} sx={{ mt: 0.5, bgcolor: getStatusColor(selectedBug.status).bg, color: getStatusColor(selectedBug.status).color }} />
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="textSecondary">Priority</Typography>
                                        <Chip label={selectedBug.priority} sx={{ mt: 0.5, bgcolor: getPriorityColor(selectedBug.priority).bg, color: getPriorityColor(selectedBug.priority).color }} />
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="textSecondary">Linked Failure</Typography>
                                        <Chip icon={<LinkIcon />} label={selectedBug.linkedFailure} variant="outlined" sx={{ mt: 0.5 }} />
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="textSecondary">Classification</Typography>
                                        <Chip label={selectedBug.classification} sx={{ mt: 0.5, bgcolor: '#f1f5f9' }} />
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="textSecondary">AI Confidence</Typography>
                                        <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                                            <LinearProgress variant="determinate" value={selectedBug.aiConfidence * 100} sx={{ width: 100, height: 8, borderRadius: 4 }} />
                                            <Typography variant="body2" fontWeight={600}>{Math.round(selectedBug.aiConfidence * 100)}%</Typography>
                                        </Box>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="textSecondary">Assignee</Typography>
                                        <Typography variant="body2" fontWeight={600} mt={0.5}>{selectedBug.assignee || 'Unassigned'}</Typography>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="textSecondary">Reporter</Typography>
                                        <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                                            {selectedBug.reporter === 'AI Analysis System' && <SmartToyIcon sx={{ color: '#8b5cf6', fontSize: 18 }} />}
                                            <Typography variant="body2" fontWeight={600}>{selectedBug.reporter}</Typography>
                                        </Box>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="textSecondary">Created</Typography>
                                        <Typography variant="body2" fontWeight={600} mt={0.5}>{selectedBug.createdAt}</Typography>
                                    </Grid>
                                </Grid>
                            </DialogContent>
                            <DialogActions sx={{ p: 3 }}>
                                <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
                                <Button
                                    variant="contained"
                                    startIcon={<OpenInNewIcon />}
                                    onClick={() => window.open(selectedBug.jiraUrl, '_blank')}
                                    sx={{ bgcolor: '#2563eb' }}
                                >
                                    Open in Jira
                                </Button>
                            </DialogActions>
                        </>
                    )}
                </Dialog>
            </Container>
        </Box>
    );
};

export default JiraBugsPreview;
