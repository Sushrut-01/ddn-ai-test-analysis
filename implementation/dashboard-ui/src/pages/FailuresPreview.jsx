import React, { useState, useEffect, useCallback } from 'react';
import {
    Box, Container, Paper, Typography, Table, TableBody, TableCell, TableContainer,
    TableHead, TableRow, Chip, IconButton, TextField, MenuItem, Grid, Button,
    InputAdornment, TablePagination, Avatar, LinearProgress, Skeleton, CircularProgress
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import VisibilityIcon from '@mui/icons-material/Visibility';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import RefreshIcon from '@mui/icons-material/Refresh';
import DownloadIcon from '@mui/icons-material/Download';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import HowToVoteIcon from '@mui/icons-material/HowToVote';
import Alert from '@mui/material/Alert';
import Tooltip from '@mui/material/Tooltip';
import { useNavigate, useLocation } from 'react-router-dom';
import { useColorTheme } from '../theme/ThemeContext';
import { failuresAPI, monitoringAPI, ragApprovalAPI, exportAPI } from '../services/api';

const ERROR_CATEGORIES = [
    { value: '', label: 'All Categories' },
    { value: 'CODE_ERROR', label: 'Code Error', color: '#ef4444' },
    { value: 'TEST_FAILURE', label: 'Test Failure', color: '#f59e0b' },
    { value: 'INFRA_ERROR', label: 'Infrastructure', color: '#3b82f6' },
    { value: 'DEPENDENCY_ERROR', label: 'Dependency', color: '#8b5cf6' },
    { value: 'CONFIG_ERROR', label: 'Config Error', color: '#10b981' }
];

const VALIDATION_STATUSES = [
    { value: '', label: 'All Statuses' },
    { value: 'accepted', label: 'Accepted', color: '#10b981' },
    { value: 'rejected', label: 'Rejected', color: '#ef4444' },
    { value: 'refining', label: 'Refining', color: '#f59e0b' },
    { value: 'pending', label: 'Pending', color: '#64748b' }
];

const getAgingColor = (days) => {
    if (days >= 7) return { bg: '#fee2e2', color: '#991b1b' };
    if (days >= 3) return { bg: '#fef3c7', color: '#92400e' };
    return { bg: '#dcfce7', color: '#166534' };
};

const getCategoryColor = (category) => {
    const cat = ERROR_CATEGORIES.find(c => c.value === category);
    return cat?.color || '#64748b';
};

const getValidationColor = (status) => {
    const s = VALIDATION_STATUSES.find(v => v.value === status);
    return s?.color || '#64748b';
};

const FailuresPreview = () => {
    const { theme } = useColorTheme();
    const navigate = useNavigate();
    const location = useLocation();
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [searchTerm, setSearchTerm] = useState('');
    const [category, setCategory] = useState('');
    const [validationStatus, setValidationStatus] = useState('');

    // Determine page mode based on route
    const isApprovalFlow = location.pathname === '/approval-flow';
    const isAIRootCause = location.pathname === '/ai-root-cause';

    // Page configuration based on route
    const pageConfig = {
        title: isApprovalFlow ? 'AI Analysis Approval' : isAIRootCause ? 'AI Root Cause Analysis' : 'Test Failures',
        subtitle: isApprovalFlow
            ? 'CODE_ERROR items from RAG Review - Click eye button to approve AI analysis'
            : isAIRootCause
                ? 'All AI analyses with root cause details and fix suggestions'
                : 'Browse and analyze test failure history with AI insights',
        icon: isApprovalFlow ? <HowToVoteIcon /> : isAIRootCause ? <SmartToyIcon /> : <ErrorIcon />
    };

    // Real data state
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [failures, setFailures] = useState([]);
    const [stats, setStats] = useState(null);
    const [totalCount, setTotalCount] = useState(0);
    const [error, setError] = useState(null);

    const fetchFailures = useCallback(async () => {
        try {
            if (isApprovalFlow) {
                // For Approval Flow, fetch CODE_ERROR items approved in RAG Review
                const [historyRes, statsRes] = await Promise.all([
                    ragApprovalAPI.getHistory({ limit: 100 }),
                    monitoringAPI.getStats()
                ]);

                // Filter to only CODE_ERROR approved items
                const approvedCodeErrors = (historyRes?.history || []).filter(item =>
                    item.error_category === 'CODE_ERROR' &&
                    item.review_status === 'approved'
                );

                // Transform to match failures format
                const transformedData = approvedCodeErrors.map(item => ({
                    _id: item.id,
                    id: item.id,
                    build_id: item.build_id,
                    job_name: item.job_name,
                    test_name: item.job_name,
                    error_category: item.error_category,
                    classification: item.error_category,
                    error_message: item.rag_suggestion,
                    timestamp: item.reviewed_at || item.created_at,
                    analysis: {
                        confidence: parseFloat(item.rag_confidence) || 0.85,
                        classification: item.error_category
                    },
                    validation_status: item.ai_analysis_id ? 'analyzed' : 'pending',
                    ai_analysis_id: item.ai_analysis_id
                }));

                setFailures(transformedData);
                setTotalCount(transformedData.length);
                setStats(statsRes);
                setError(null);
            } else {
                // For other pages, use the regular failures API
                const params = {
                    limit: rowsPerPage,
                    skip: page * rowsPerPage,
                    analyzed: 'true'
                };
                if (searchTerm) params.search = searchTerm;
                if (category) params.category = category;
                if (validationStatus) params.validation_status = validationStatus;

                const [failuresRes, statsRes] = await Promise.all([
                    failuresAPI.getList(params),
                    monitoringAPI.getStats()
                ]);

                const failuresData = failuresRes?.data?.failures || failuresRes?.failures || [];
                setFailures(failuresData);
                setTotalCount(failuresRes?.data?.total || failuresRes?.total || failuresData.length);
                setStats(statsRes);
                setError(null);
            }
        } catch (err) {
            console.error('Error fetching failures:', err);
            setError(err.message);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, [page, rowsPerPage, searchTerm, category, validationStatus, isApprovalFlow]);

    useEffect(() => {
        setLoading(true);
        fetchFailures();
    }, [location.key, fetchFailures]);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchFailures();
    };

    const handleExport = async () => {
        try {
            const header = 'Build ID,Test Name,Job,Timestamp,Category,Status,Root Cause\n'
            const csvContent = failures.map(f =>
                `"${f.build_id || f.buildId || ''}","${f.test_name || f.testName || ''}","${f.job_name || f.jobName || ''}","${f.timestamp || ''}","${f.classification || f.analysis?.classification || ''}","${f.validation_status || f.status || ''}","${(f.error_message || f.stack_trace || '').replace(/"/g, '""').replace(/\n/g, ' ')}"`
            ).join('\n')
            const blob = new Blob([header + csvContent], { type: 'text/csv;charset=utf-8;' })
            const url = URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.download = `failures_export_${new Date().toISOString().split('T')[0]}.csv`
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            URL.revokeObjectURL(url)
        } catch (err) {
            console.error('Export failed:', err)
        }
    };

    // Calculate aging days from timestamp
    const getAgingDays = (timestamp) => {
        if (!timestamp) return 0;
        const date = new Date(timestamp);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    };

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: theme.background, pb: 4 }}>
            {/* Header */}
            <Box
                sx={{
                    background: theme.headerGradient,
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
                                {pageConfig.title}
                            </Typography>
                            <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                                {pageConfig.subtitle}
                            </Typography>
                        </Box>
                        <Box display="flex" gap={2}>
                            <Button
                                variant="contained"
                                startIcon={<DownloadIcon />}
                                onClick={handleExport}
                                sx={{ bgcolor: 'rgba(255,255,255,0.15)', '&:hover': { bgcolor: 'rgba(255,255,255,0.25)' } }}
                            >
                                Export
                            </Button>
                            <Button
                                variant="contained"
                                startIcon={refreshing ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
                                onClick={handleRefresh}
                                disabled={refreshing}
                                sx={{ bgcolor: 'rgba(255,255,255,0.15)', '&:hover': { bgcolor: 'rgba(255,255,255,0.25)' } }}
                            >
                                {refreshing ? 'Refreshing...' : 'Refresh'}
                            </Button>
                        </Box>
                    </Box>
                </Container>
            </Box>

            <Container maxWidth="xl">
                {/* Info Alert for Approval Flow */}
                {isApprovalFlow && (
                    <Alert
                        severity="info"
                        icon={<HowToVoteIcon />}
                        sx={{ mb: 3, borderRadius: 3 }}
                    >
                        <Typography variant="body2">
                            <strong>Workflow:</strong> These CODE_ERROR items were approved in RAG Review for AI deep analysis.
                            Click the <VisibilityIcon sx={{ fontSize: 16, verticalAlign: 'middle', mx: 0.5 }} /> button to view
                            AI analysis details and approve for PR creation.
                        </Typography>
                    </Alert>
                )}

                {/* Stats Cards */}
                <Grid container spacing={3} mb={4}>
                    {[
                        { label: 'Total Failures', value: loading ? '-' : (stats?.total_failures || 0).toLocaleString(), icon: <ErrorIcon />, color: '#ef4444' },
                        { label: 'Analyzed', value: loading ? '-' : (stats?.total_analyzed || 0).toLocaleString(), icon: <SmartToyIcon />, color: '#3b82f6' },
                        { label: 'Last 24h', value: loading ? '-' : (stats?.failures_last_24h || 0).toLocaleString(), icon: <WarningIcon />, color: '#f59e0b' },
                        { label: 'Avg Confidence', value: loading ? '-' : `${Math.round(parseFloat(stats?.avg_confidence || 0) * 100)}%`, icon: <CheckCircleIcon />, color: '#10b981' },
                    ].map((stat, idx) => (
                        <Grid item xs={6} md={3} key={idx}>
                            <Paper
                                elevation={0}
                                sx={{
                                    p: 3,
                                    borderRadius: 4,
                                    bgcolor: 'white',
                                    boxShadow: '0 4px 20px rgba(0,0,0,0.04)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 2
                                }}
                            >
                                <Avatar sx={{ bgcolor: alpha(stat.color, 0.1), color: stat.color, width: 48, height: 48 }}>
                                    {stat.icon}
                                </Avatar>
                                <Box>
                                    {loading ? (
                                        <Skeleton width={60} height={32} />
                                    ) : (
                                        <Typography variant="h5" fontWeight="bold">{stat.value}</Typography>
                                    )}
                                    <Typography variant="body2" color="textSecondary">{stat.label}</Typography>
                                </Box>
                            </Paper>
                        </Grid>
                    ))}
                </Grid>

                {/* Filters */}
                <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                    <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                placeholder="Search by build ID, test name, job..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                InputProps={{
                                    startAdornment: <InputAdornment position="start"><SearchIcon color="action" /></InputAdornment>,
                                }}
                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                            />
                        </Grid>
                        <Grid item xs={6} md={3}>
                            <TextField
                                fullWidth
                                select
                                label="Error Category"
                                value={category}
                                onChange={(e) => setCategory(e.target.value)}
                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                            >
                                {ERROR_CATEGORIES.map((opt) => (
                                    <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                                ))}
                            </TextField>
                        </Grid>
                        <Grid item xs={6} md={3}>
                            <TextField
                                fullWidth
                                select
                                label="Validation Status"
                                value={validationStatus}
                                onChange={(e) => setValidationStatus(e.target.value)}
                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                            >
                                {VALIDATION_STATUSES.map((opt) => (
                                    <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                                ))}
                            </TextField>
                        </Grid>
                        <Grid item xs={12} md={2}>
                            <Button fullWidth variant="outlined" startIcon={<FilterListIcon />} sx={{ borderRadius: 3, py: 1.8 }}>
                                More Filters
                            </Button>
                        </Grid>
                    </Grid>
                </Paper>

                {/* Table */}
                <Paper elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', overflow: 'hidden' }}>
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow sx={{ bgcolor: '#f8fafc' }}>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Build ID</TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Test Name</TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Job</TableCell>
                                    <TableCell align="center" sx={{ fontWeight: 600, color: '#64748b' }}>Age</TableCell>
                                    <TableCell align="center" sx={{ fontWeight: 600, color: '#64748b' }}>AI Status</TableCell>
                                    <TableCell align="center" sx={{ fontWeight: 600, color: '#64748b' }}>Validation</TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Category</TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Root Cause</TableCell>
                                    <TableCell align="center" sx={{ fontWeight: 600, color: '#64748b' }}>Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {loading ? (
                                    // Loading skeleton rows
                                    [...Array(5)].map((_, idx) => (
                                        <TableRow key={idx}>
                                            <TableCell><Skeleton width={80} /></TableCell>
                                            <TableCell><Skeleton width={200} /></TableCell>
                                            <TableCell><Skeleton width={100} /></TableCell>
                                            <TableCell><Skeleton width={40} /></TableCell>
                                            <TableCell><Skeleton width={80} /></TableCell>
                                            <TableCell><Skeleton width={60} /></TableCell>
                                            <TableCell><Skeleton width={80} /></TableCell>
                                            <TableCell><Skeleton width={200} /></TableCell>
                                            <TableCell><Skeleton width={30} /></TableCell>
                                        </TableRow>
                                    ))
                                ) : failures.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                                            <Typography color="textSecondary">No failures found</Typography>
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    failures.map((failure) => {
                                        const agingDays = getAgingDays(failure.timestamp);
                                        const agingStyle = getAgingColor(agingDays);
                                        const confidence = failure.analysis?.confidence || 0;
                                        const hasAnalysis = !!failure.analysis;
                                        const validationStat = failure.validation_status || failure.status || 'pending';
                                        const errorCategory = failure.classification || failure.analysis?.classification || null;
                                        const rootCause = failure.error_message || failure.stack_trace || '-';

                                        return (
                                            <TableRow key={failure._id || failure.id} sx={{ '&:hover': { bgcolor: '#f8fafc' } }}>
                                                <TableCell>
                                                    <Typography variant="body2" fontFamily="monospace" fontWeight={600} color="#3b82f6">
                                                        {failure.build_id || failure.buildId || '-'}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell>
                                                    <Typography variant="body2" fontWeight={500}>{failure.test_name || failure.testName || '-'}</Typography>
                                                </TableCell>
                                                <TableCell>
                                                    <Typography variant="body2" color="textSecondary">{failure.job_name || failure.jobName || '-'}</Typography>
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Chip
                                                        label={`${agingDays}d`}
                                                        size="small"
                                                        sx={{ bgcolor: agingStyle.bg, color: agingStyle.color, fontWeight: 600, fontSize: '0.7rem' }}
                                                    />
                                                </TableCell>
                                                <TableCell align="center">
                                                    {hasAnalysis ? (
                                                        <Box display="flex" alignItems="center" justifyContent="center" gap={1}>
                                                            <Box sx={{ width: 50, height: 6, borderRadius: 3, bgcolor: '#e2e8f0', overflow: 'hidden' }}>
                                                                <Box sx={{ width: `${confidence * 100}%`, height: '100%', borderRadius: 3, bgcolor: confidence >= 0.9 ? '#10b981' : confidence >= 0.75 ? '#f59e0b' : '#ef4444' }} />
                                                            </Box>
                                                            <Typography variant="caption" fontWeight={600}>{Math.round(confidence * 100)}%</Typography>
                                                        </Box>
                                                    ) : (
                                                        <Chip label="Pending" size="small" variant="outlined" sx={{ fontSize: '0.7rem' }} />
                                                    )}
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Chip
                                                        label={validationStat.toUpperCase()}
                                                        size="small"
                                                        sx={{
                                                            bgcolor: alpha(getValidationColor(validationStat), 0.1),
                                                            color: getValidationColor(validationStat),
                                                            fontWeight: 600,
                                                            fontSize: '0.65rem'
                                                        }}
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    {errorCategory ? (
                                                        <Chip
                                                            label={errorCategory.replace('_', ' ')}
                                                            size="small"
                                                            sx={{
                                                                bgcolor: alpha(getCategoryColor(errorCategory), 0.1),
                                                                color: getCategoryColor(errorCategory),
                                                                fontWeight: 500,
                                                                fontSize: '0.7rem'
                                                            }}
                                                        />
                                                    ) : '-'}
                                                </TableCell>
                                                <TableCell>
                                                    <Typography variant="body2" sx={{ maxWidth: 250 }} noWrap>
                                                        {rootCause}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Tooltip title={isApprovalFlow ? "View AI Analysis & Approve for PR" : "View Details"}>
                                                        <IconButton
                                                            size="small"
                                                            sx={{
                                                                color: isApprovalFlow ? '#10b981' : '#3b82f6',
                                                                bgcolor: isApprovalFlow ? alpha('#10b981', 0.1) : 'transparent',
                                                                '&:hover': {
                                                                    bgcolor: isApprovalFlow ? alpha('#10b981', 0.2) : alpha('#3b82f6', 0.1)
                                                                }
                                                            }}
                                                            onClick={() => {
                                                                if (isApprovalFlow) {
                                                                    // For approval flow, navigate to Code Healing Pipeline page
                                                                    navigate('/code-healing');
                                                                } else {
                                                                    // Use build_id for navigation
                                                                    const navId = failure.build_id || failure.buildId || failure._id || failure.id;
                                                                    navigate(`/failures/${navId}`);
                                                                }
                                                            }}
                                                        >
                                                            {isApprovalFlow ? <ThumbUpIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
                                                        </IconButton>
                                                    </Tooltip>
                                                </TableCell>
                                            </TableRow>
                                        );
                                    })
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                    <TablePagination
                        rowsPerPageOptions={[10, 20, 50]}
                        component="div"
                        count={totalCount}
                        rowsPerPage={rowsPerPage}
                        page={page}
                        onPageChange={(e, p) => setPage(p)}
                        onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value)); setPage(0); }}
                    />
                </Paper>
            </Container>
        </Box>
    );
};

export default FailuresPreview;
