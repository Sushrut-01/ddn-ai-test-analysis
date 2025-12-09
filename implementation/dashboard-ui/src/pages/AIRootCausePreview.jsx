import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box, Container, Paper, Typography, Grid, Button, Chip, Avatar, IconButton,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    TextField, MenuItem, InputAdornment, TablePagination, Card, CardContent,
    Tooltip, Collapse, Alert, Divider, LinearProgress, Skeleton, CircularProgress
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
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import BugReportIcon from '@mui/icons-material/BugReport';
import CodeIcon from '@mui/icons-material/Code';
import DescriptionIcon from '@mui/icons-material/Description';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import ThumbDownIcon from '@mui/icons-material/ThumbDown';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import { useColorTheme } from '../theme/ThemeContext';
import { failuresAPI, monitoringAPI } from '../services/api';

const ERROR_CATEGORIES = [
    { value: '', label: 'All Categories' },
    { value: 'CODE_ERROR', label: 'Code Error', color: '#ef4444' },
    { value: 'ENV_CONFIG', label: 'Environment/Config', color: '#f59e0b' },
    { value: 'NETWORK_ERROR', label: 'Network Error', color: '#3b82f6' },
    { value: 'INFRA_ERROR', label: 'Infrastructure', color: '#8b5cf6' },
    { value: 'UNKNOWN', label: 'Unknown', color: '#64748b' }
];

const CONFIDENCE_LEVELS = [
    { value: '', label: 'All Confidence' },
    { value: 'high', label: 'High (>80%)', min: 0.8 },
    { value: 'medium', label: 'Medium (50-80%)', min: 0.5, max: 0.8 },
    { value: 'low', label: 'Low (<50%)', max: 0.5 }
];

const getCategoryColor = (category) => {
    const cat = ERROR_CATEGORIES.find(c => c.value === category);
    return cat?.color || '#64748b';
};

const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#10b981';
    if (confidence >= 0.5) return '#f59e0b';
    return '#ef4444';
};

const AIRootCausePreview = () => {
    const { theme } = useColorTheme();
    const navigate = useNavigate();
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [searchTerm, setSearchTerm] = useState('');
    const [category, setCategory] = useState('');
    const [confidenceFilter, setConfidenceFilter] = useState('');
    const [expandedRow, setExpandedRow] = useState(null);

    // Data state
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [analyses, setAnalyses] = useState([]);
    const [stats, setStats] = useState(null);
    const [totalCount, setTotalCount] = useState(0);

    const fetchAnalyses = useCallback(async () => {
        try {
            const params = {
                limit: rowsPerPage,
                skip: page * rowsPerPage,
                analyzed: 'true' // Only get analyzed items
            };
            if (searchTerm) params.search = searchTerm;
            if (category) params.category = category;

            const [failuresRes, statsRes] = await Promise.all([
                failuresAPI.getList(params),
                monitoringAPI.getStats()
            ]);

            const data = failuresRes?.data?.failures || failuresRes?.failures || [];
            setAnalyses(data);
            setTotalCount(failuresRes?.data?.total || failuresRes?.total || data.length);
            setStats(statsRes);
        } catch (err) {
            console.error('Error fetching analyses:', err);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, [page, rowsPerPage, searchTerm, category]);

    useEffect(() => {
        setLoading(true);
        fetchAnalyses();
    }, [fetchAnalyses]);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchAnalyses();
    };

    const handleViewDetails = (analysis) => {
        const buildId = analysis?.build_id || analysis?.buildId || analysis?._id || '';
        if (buildId) {
            navigate(`/failures/${buildId}`);
        } else {
            console.error('No build ID found for analysis:', analysis);
        }
    };

    const handleCopyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
    };

    const toggleRowExpand = (id) => {
        setExpandedRow(expandedRow === id ? null : id);
    };

    // Calculate summary stats
    const summaryStats = {
        totalAnalyses: totalCount,
        highConfidence: analyses.filter(a => (a.confidence || 0) >= 0.8).length,
        codeErrors: analyses.filter(a => a.error_category === 'CODE_ERROR').length,
        avgConfidence: analyses.length > 0
            ? Math.round(analyses.reduce((sum, a) => sum + (a.confidence || 0), 0) / analyses.length * 100)
            : 0
    };

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: theme.background, pb: 4 }}>
            {/* Header */}
            <Box
                sx={{
                    background: 'linear-gradient(135deg, #dc2626 0%, #991b1b 100%)',
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
                            <Box display="flex" alignItems="center" gap={2} mb={1}>
                                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 48, height: 48 }}>
                                    <BugReportIcon />
                                </Avatar>
                                <Typography variant="h4" fontWeight="bold">
                                    AI Root Cause Analysis
                                </Typography>
                            </Box>
                            <Typography variant="subtitle1" sx={{ opacity: 0.9, ml: 8 }}>
                                Deep AI analysis results with root cause identification and fix suggestions
                            </Typography>
                        </Box>
                        <Box display="flex" gap={2}>
                            <Button
                                variant="contained"
                                startIcon={<DownloadIcon />}
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
                                Refresh
                            </Button>
                        </Box>
                    </Box>
                </Container>
            </Box>

            <Container maxWidth="xl">
                {/* Summary Stats Cards */}
                <Grid container spacing={3} mb={4}>
                    {[
                        { label: 'Total Analyses', value: loading ? '-' : summaryStats.totalAnalyses, icon: <SmartToyIcon />, color: '#3b82f6', desc: 'AI-analyzed failures' },
                        { label: 'High Confidence', value: loading ? '-' : summaryStats.highConfidence, icon: <CheckCircleIcon />, color: '#10b981', desc: 'Confidence > 80%' },
                        { label: 'Code Errors', value: loading ? '-' : summaryStats.codeErrors, icon: <CodeIcon />, color: '#ef4444', desc: 'Requiring code fixes' },
                        { label: 'Avg Confidence', value: loading ? '-' : `${summaryStats.avgConfidence}%`, icon: <TipsAndUpdatesIcon />, color: '#f59e0b', desc: 'Analysis accuracy' },
                    ].map((stat, idx) => (
                        <Grid item xs={6} md={3} key={idx}>
                            <Card elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                                <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                    <Avatar sx={{ bgcolor: alpha(stat.color, 0.1), color: stat.color, width: 56, height: 56 }}>
                                        {stat.icon}
                                    </Avatar>
                                    <Box>
                                        {loading ? (
                                            <Skeleton width={60} height={36} />
                                        ) : (
                                            <Typography variant="h4" fontWeight="bold">{stat.value}</Typography>
                                        )}
                                        <Typography variant="body2" color="textSecondary">{stat.label}</Typography>
                                        <Typography variant="caption" color="textSecondary">{stat.desc}</Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>

                {/* Filters */}
                <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                    <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                placeholder="Search by build ID, test name, error message..."
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
                                label="Confidence Level"
                                value={confidenceFilter}
                                onChange={(e) => setConfidenceFilter(e.target.value)}
                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                            >
                                {CONFIDENCE_LEVELS.map((opt) => (
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

                {/* Info Alert */}
                <Alert
                    severity="info"
                    sx={{ mb: 3, borderRadius: 3 }}
                    icon={<TipsAndUpdatesIcon />}
                >
                    <Typography variant="body2">
                        <strong>AI Root Cause Analysis</strong> uses Claude AI to analyze XML reports, console logs, and stack traces to identify the exact line of code causing failures.
                        Click on any row to expand and see the full analysis with suggested fixes.
                    </Typography>
                </Alert>

                {/* Analysis Table */}
                <Paper elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', overflow: 'hidden' }}>
                    {loading && <LinearProgress />}
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow sx={{ bgcolor: '#f8fafc' }}>
                                    <TableCell sx={{ fontWeight: 600, width: 40 }}></TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Build ID</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Test / Job</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Category</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Confidence</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Root Cause</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Analyzed</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {loading ? (
                                    [...Array(5)].map((_, idx) => (
                                        <TableRow key={idx}>
                                            <TableCell colSpan={9}><Skeleton height={60} /></TableCell>
                                        </TableRow>
                                    ))
                                ) : analyses.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={9} align="center" sx={{ py: 8 }}>
                                            <SmartToyIcon sx={{ fontSize: 48, color: '#cbd5e1', mb: 2 }} />
                                            <Typography variant="h6" color="textSecondary">No AI analyses found</Typography>
                                            <Typography variant="body2" color="textSecondary">
                                                Trigger analysis from the Manual Trigger Flow page
                                            </Typography>
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    analyses.map((analysis) => (
                                        <React.Fragment key={analysis._id || analysis.build_id}>
                                            <TableRow
                                                hover
                                                sx={{
                                                    cursor: 'pointer',
                                                    '&:hover': { bgcolor: '#f8fafc' },
                                                    bgcolor: expandedRow === analysis._id ? '#f1f5f9' : 'inherit'
                                                }}
                                                onClick={() => toggleRowExpand(analysis._id)}
                                            >
                                                <TableCell>
                                                    <IconButton size="small">
                                                        {expandedRow === analysis._id ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                                    </IconButton>
                                                </TableCell>
                                                <TableCell>
                                                    <Typography variant="body2" fontWeight={600}>
                                                        #{analysis.build_id || '-'}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell>
                                                    <Box>
                                                        <Typography variant="body2" fontWeight={500}>
                                                            {analysis.test_name || analysis.job_name || '-'}
                                                        </Typography>
                                                        <Typography variant="caption" color="textSecondary">
                                                            {analysis.job_name || '-'}
                                                        </Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Chip
                                                        label={analysis.error_category || 'UNKNOWN'}
                                                        size="small"
                                                        sx={{
                                                            bgcolor: alpha(getCategoryColor(analysis.error_category), 0.1),
                                                            color: getCategoryColor(analysis.error_category),
                                                            fontWeight: 600,
                                                            fontSize: '0.7rem'
                                                        }}
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    <Box display="flex" alignItems="center" gap={1}>
                                                        <Box
                                                            sx={{
                                                                width: 60,
                                                                height: 6,
                                                                borderRadius: 3,
                                                                bgcolor: '#e2e8f0',
                                                                overflow: 'hidden'
                                                            }}
                                                        >
                                                            <Box
                                                                sx={{
                                                                    width: `${(analysis.confidence || 0) * 100}%`,
                                                                    height: '100%',
                                                                    bgcolor: getConfidenceColor(analysis.confidence || 0),
                                                                    borderRadius: 3
                                                                }}
                                                            />
                                                        </Box>
                                                        <Typography variant="body2" fontWeight={500}>
                                                            {Math.round((analysis.confidence || 0) * 100)}%
                                                        </Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Tooltip title={analysis.root_cause || analysis.error_message || '-'}>
                                                        <Typography
                                                            variant="body2"
                                                            sx={{
                                                                maxWidth: 200,
                                                                overflow: 'hidden',
                                                                textOverflow: 'ellipsis',
                                                                whiteSpace: 'nowrap'
                                                            }}
                                                        >
                                                            {analysis.root_cause || analysis.error_message || '-'}
                                                        </Typography>
                                                    </Tooltip>
                                                </TableCell>
                                                <TableCell>
                                                    <Chip
                                                        icon={analysis.validation_status === 'accepted' ? <ThumbUpIcon /> :
                                                              analysis.validation_status === 'rejected' ? <ThumbDownIcon /> : null}
                                                        label={analysis.validation_status || 'Pending'}
                                                        size="small"
                                                        sx={{
                                                            bgcolor: analysis.validation_status === 'accepted' ? '#dcfce7' :
                                                                     analysis.validation_status === 'rejected' ? '#fee2e2' : '#f1f5f9',
                                                            color: analysis.validation_status === 'accepted' ? '#166534' :
                                                                   analysis.validation_status === 'rejected' ? '#991b1b' : '#64748b',
                                                            '& .MuiChip-icon': { color: 'inherit', fontSize: 14 }
                                                        }}
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    <Box display="flex" alignItems="center" gap={0.5}>
                                                        <AccessTimeIcon sx={{ fontSize: 14, color: '#94a3b8' }} />
                                                        <Typography variant="caption" color="textSecondary">
                                                            {analysis.analyzed_at ? new Date(analysis.analyzed_at).toLocaleDateString() : '-'}
                                                        </Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Box display="flex" gap={0.5}>
                                                        <Tooltip title="View Full Details">
                                                            <IconButton
                                                                size="small"
                                                                onClick={(e) => { e.stopPropagation(); handleViewDetails(analysis); }}
                                                                sx={{ bgcolor: '#e0f2fe', '&:hover': { bgcolor: '#bae6fd' } }}
                                                            >
                                                                <OpenInNewIcon sx={{ fontSize: 18, color: '#0284c7' }} />
                                                            </IconButton>
                                                        </Tooltip>
                                                        <Tooltip title="Copy Root Cause">
                                                            <IconButton
                                                                size="small"
                                                                onClick={(e) => { e.stopPropagation(); handleCopyToClipboard(analysis.root_cause || analysis.error_message || ''); }}
                                                            >
                                                                <ContentCopyIcon sx={{ fontSize: 18 }} />
                                                            </IconButton>
                                                        </Tooltip>
                                                    </Box>
                                                </TableCell>
                                            </TableRow>

                                            {/* Expanded Row Details */}
                                            <TableRow>
                                                <TableCell colSpan={9} sx={{ py: 0, borderBottom: expandedRow === analysis._id ? undefined : 'none' }}>
                                                    <Collapse in={expandedRow === analysis._id} timeout="auto" unmountOnExit>
                                                        <Box sx={{ py: 3, px: 2 }}>
                                                            <Grid container spacing={3}>
                                                                {/* Root Cause Section */}
                                                                <Grid item xs={12} md={6}>
                                                                    <Paper sx={{ p: 2, bgcolor: '#fef2f2', borderRadius: 2, border: '1px solid #fecaca' }}>
                                                                        <Box display="flex" alignItems="center" gap={1} mb={1}>
                                                                            <BugReportIcon sx={{ color: '#dc2626' }} />
                                                                            <Typography variant="subtitle2" fontWeight={600} color="#991b1b">
                                                                                Root Cause Identified
                                                                            </Typography>
                                                                        </Box>
                                                                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                                                            {analysis.root_cause || analysis.error_message || 'No root cause identified'}
                                                                        </Typography>
                                                                        {analysis.file_path && (
                                                                            <Box mt={1} p={1} bgcolor="white" borderRadius={1}>
                                                                                <Typography variant="caption" color="textSecondary">File:</Typography>
                                                                                <Typography variant="body2" fontFamily="monospace">
                                                                                    {analysis.file_path}:{analysis.line_number || '?'}
                                                                                </Typography>
                                                                            </Box>
                                                                        )}
                                                                    </Paper>
                                                                </Grid>

                                                                {/* Suggested Fix Section */}
                                                                <Grid item xs={12} md={6}>
                                                                    <Paper sx={{ p: 2, bgcolor: '#f0fdf4', borderRadius: 2, border: '1px solid #bbf7d0' }}>
                                                                        <Box display="flex" alignItems="center" gap={1} mb={1}>
                                                                            <TipsAndUpdatesIcon sx={{ color: '#16a34a' }} />
                                                                            <Typography variant="subtitle2" fontWeight={600} color="#166534">
                                                                                Suggested Fix
                                                                            </Typography>
                                                                        </Box>
                                                                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                                                            {analysis.suggested_fix || analysis.fix_suggestion || 'No fix suggestion available'}
                                                                        </Typography>
                                                                    </Paper>
                                                                </Grid>

                                                                {/* Error Details */}
                                                                <Grid item xs={12}>
                                                                    <Paper sx={{ p: 2, bgcolor: '#f8fafc', borderRadius: 2 }}>
                                                                        <Box display="flex" alignItems="center" gap={1} mb={1}>
                                                                            <DescriptionIcon sx={{ color: '#64748b' }} />
                                                                            <Typography variant="subtitle2" fontWeight={600}>
                                                                                Error Details
                                                                            </Typography>
                                                                        </Box>
                                                                        <Box
                                                                            sx={{
                                                                                p: 1.5,
                                                                                bgcolor: '#1e293b',
                                                                                borderRadius: 1,
                                                                                fontFamily: 'monospace',
                                                                                fontSize: '0.75rem',
                                                                                color: '#e2e8f0',
                                                                                maxHeight: 150,
                                                                                overflow: 'auto'
                                                                            }}
                                                                        >
                                                                            <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                                                                                {analysis.stack_trace || analysis.error_message || 'No stack trace available'}
                                                                            </pre>
                                                                        </Box>
                                                                    </Paper>
                                                                </Grid>

                                                                {/* Actions */}
                                                                <Grid item xs={12}>
                                                                    <Box display="flex" gap={2} justifyContent="flex-end">
                                                                        <Button
                                                                            variant="outlined"
                                                                            startIcon={<ContentCopyIcon />}
                                                                            onClick={() => handleCopyToClipboard(JSON.stringify(analysis, null, 2))}
                                                                        >
                                                                            Copy Full Analysis
                                                                        </Button>
                                                                        <Button
                                                                            variant="contained"
                                                                            startIcon={<OpenInNewIcon />}
                                                                            onClick={() => handleViewDetails(analysis)}
                                                                            sx={{ bgcolor: '#3b82f6' }}
                                                                        >
                                                                            View Full Details
                                                                        </Button>
                                                                    </Box>
                                                                </Grid>
                                                            </Grid>
                                                        </Box>
                                                    </Collapse>
                                                </TableCell>
                                            </TableRow>
                                        </React.Fragment>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                    <TablePagination
                        component="div"
                        count={totalCount}
                        page={page}
                        onPageChange={(e, newPage) => setPage(newPage)}
                        rowsPerPage={rowsPerPage}
                        onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
                        rowsPerPageOptions={[5, 10, 25, 50]}
                    />
                </Paper>
            </Container>
        </Box>
    );
};

export default AIRootCausePreview;
