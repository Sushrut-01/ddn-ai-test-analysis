import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
    Box, Container, Paper, Typography, Grid, Button, Chip, Avatar,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    Checkbox, LinearProgress, Card, CardContent, IconButton, Tooltip, Alert,
    Skeleton, CircularProgress
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import RefreshIcon from '@mui/icons-material/Refresh';
import SelectAllIcon from '@mui/icons-material/SelectAll';
import DeselectIcon from '@mui/icons-material/Deselect';
import BoltIcon from '@mui/icons-material/Bolt';
import PendingIcon from '@mui/icons-material/Pending';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import WarningIcon from '@mui/icons-material/Warning';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { failuresAPI, triggerAPI } from '../services/api';

const TriggerAnalysisPreview = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [selectedBuilds, setSelectedBuilds] = useState(new Set());
    const [analysisComplete, setAnalysisComplete] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);
    const [progress, setProgress] = useState(0);

    // Real data state
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [unanalyzedFailures, setUnanalyzedFailures] = useState([]);
    const [error, setError] = useState(null);

    const fetchUnanalyzedFailures = useCallback(async () => {
        try {
            // Fetch failures that haven't been analyzed yet
            const response = await failuresAPI.getList({
                limit: 50,
                analyzed: false
            });
            const data = response?.data || response;
            const failures = data?.failures || [];

            // Group failures by build_id to avoid duplicates
            const buildGroups = {};
            failures.forEach((f) => {
                const buildId = f.build_id || f.buildId || '-';
                if (!buildGroups[buildId]) {
                    buildGroups[buildId] = {
                        id: f._id || f.id,
                        buildId: `#${buildId}`,
                        jobName: f.job_name || f.jobName || '-',
                        rawTimestamp: f.timestamp,
                        timestamp: f.timestamp ? new Date(f.timestamp).toLocaleString() : '-',
                        failCount: f.fail_count || 1,
                        testNames: [],
                        errorMessage: f.error_message || f.stack_trace || 'No error message',
                        status: f.analysis ? 'completed' : f.analyzing ? 'analyzing' : 'pending'
                    };
                }
                buildGroups[buildId].testNames.push(f.test_name || f.testName || 'Unknown Test');
                // Use max fail_count if available
                if (f.fail_count && f.fail_count > buildGroups[buildId].failCount) {
                    buildGroups[buildId].failCount = f.fail_count;
                }
            });

            // Convert to array and add summary test name
            const mappedFailures = Object.values(buildGroups).map((group) => ({
                ...group,
                testName: group.testNames.length > 1
                    ? `${group.testNames[0]} (+${group.testNames.length - 1} more)`
                    : group.testNames[0] || 'Unknown Test'
            }));

            setUnanalyzedFailures(mappedFailures);
            setError(null);
        } catch (err) {
            console.error('Error fetching unanalyzed failures:', err);
            setError(err.message);
            setUnanalyzedFailures([]);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, []);

    useEffect(() => {
        fetchUnanalyzedFailures();
    }, [location.key, fetchUnanalyzedFailures]);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchUnanalyzedFailures();
    };

    const handleSelectAll = () => {
        if (selectedBuilds.size === unanalyzedFailures.length) {
            setSelectedBuilds(new Set());
        } else {
            setSelectedBuilds(new Set(unanalyzedFailures.map(f => f.id)));
        }
    };

    const handleSelect = (id) => {
        const newSelected = new Set(selectedBuilds);
        if (newSelected.has(id)) {
            newSelected.delete(id);
        } else {
            newSelected.add(id);
        }
        setSelectedBuilds(newSelected);
    };

    const handleTrigger = async () => {
        setAnalyzing(true);
        setProgress(0);

        const selectedFailures = unanalyzedFailures.filter(f => selectedBuilds.has(f.id));
        const totalSelected = selectedFailures.length;
        let completed = 0;

        try {
            // Trigger analysis for each selected failure
            for (const failure of selectedFailures) {
                try {
                    await triggerAPI.triggerAnalysis({
                        build_id: failure.buildId.replace('#', ''),
                        triggered_by: 'dashboard_bulk_trigger',
                        reason: 'Bulk analysis trigger from dashboard'
                    });
                } catch (err) {
                    console.error(`Failed to trigger analysis for ${failure.buildId}:`, err);
                }
                completed++;
                setProgress(Math.round((completed / totalSelected) * 100));
            }

            // Refresh the list after all triggers
            await fetchUnanalyzedFailures();
            setSelectedBuilds(new Set());
            setAnalysisComplete(true);
        } catch (err) {
            console.error('Error during bulk trigger:', err);
        } finally {
            setAnalyzing(false);
        }
    };

    const pendingCount = unanalyzedFailures.filter(f => f.status === 'pending').length;
    const analyzingCount = unanalyzedFailures.filter(f => f.status === 'analyzing').length;
    const completedCount = unanalyzedFailures.filter(f => f.status === 'completed').length;

    // Calculate aging days from timestamp
    const getAgingDays = (timestamp) => {
        if (!timestamp) return 0;
        const date = new Date(timestamp);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    };

    // Get aging color based on days
    const getAgingColor = (days) => {
        if (days >= 7) return { bg: '#fee2e2', color: '#991b1b' }; // Red - critical
        if (days >= 3) return { bg: '#fef3c7', color: '#92400e' }; // Orange - warning
        return { bg: '#dcfce7', color: '#166534' }; // Green - ok
    };

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc', pb: 4 }}>
            {/* Header */}
            <Box
                sx={{
                    background: 'linear-gradient(135deg, #ea580c 0%, #c2410c 100%)',
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
                                Manual Trigger Flow
                            </Typography>
                            <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                                Select builds and trigger analysis → goes to RAG Review for approval
                            </Typography>
                        </Box>
                        <Box display="flex" gap={2}>
                            <Button
                                variant="contained"
                                startIcon={<CheckCircleIcon />}
                                onClick={() => navigate('/')}
                                sx={{ bgcolor: 'rgba(255,255,255,0.2)', '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' } }}
                            >
                                View Completed
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
                {/* Navigation Flow */}
                <Paper elevation={0} sx={{ p: 2, mb: 3, borderRadius: 3, bgcolor: 'white', boxShadow: '0 4px 20px rgba(0,0,0,0.04)', display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                    <Typography variant="subtitle2" color="textSecondary" sx={{ mr: 1 }}>
                        Flow:
                    </Typography>
                    <Chip label="1. Select & Trigger" color="warning" size="small" sx={{ fontWeight: 600, bgcolor: '#ea580c', color: 'white' }} />
                    <ArrowForwardIcon sx={{ color: '#94a3b8', fontSize: 18 }} />
                    <Chip
                        label="2. View Results"
                        size="small"
                        variant="outlined"
                        onClick={() => navigate('/failures')}
                        icon={<VisibilityIcon sx={{ fontSize: 16 }} />}
                        sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'rgba(234, 88, 12, 0.1)' } }}
                    />
                    <ArrowForwardIcon sx={{ color: '#94a3b8', fontSize: 18 }} />
                    <Chip label="3. Review & Approve" size="small" variant="outlined" />
                    <ArrowForwardIcon sx={{ color: '#94a3b8', fontSize: 18 }} />
                    <Chip label="4. Create Jira Bug" size="small" variant="outlined" />
                </Paper>

                {/* Analysis Complete Alert */}
                {analysisComplete && (
                    <Alert
                        severity="success"
                        sx={{ mb: 3, borderRadius: 3 }}
                        icon={<CheckCircleIcon />}
                        onClose={() => setAnalysisComplete(false)}
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
                        Bulk analysis completed! View the results in the Failures page.
                    </Alert>
                )}

                {/* Stats Cards */}
                <Grid container spacing={3} mb={4}>
                    {[
                        { label: 'Pending Analysis', value: pendingCount, icon: <PendingIcon />, color: '#f59e0b' },
                        { label: 'Currently Analyzing', value: analyzingCount, icon: <SmartToyIcon />, color: '#3b82f6' },
                        { label: 'Completed Today', value: completedCount, icon: <CheckCircleIcon />, color: '#10b981' },
                        { label: 'Selected', value: selectedBuilds.size, icon: <BoltIcon />, color: '#ea580c' },
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

                {/* Action Bar */}
                <Paper elevation={0} sx={{ p: 2, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box display="flex" gap={2}>
                        <Button
                            variant="outlined"
                            startIcon={selectedBuilds.size === unanalyzedFailures.length ? <DeselectIcon /> : <SelectAllIcon />}
                            onClick={handleSelectAll}
                            sx={{ borderRadius: 3 }}
                        >
                            {selectedBuilds.size === unanalyzedFailures.length ? 'Deselect All' : 'Select All'}
                        </Button>
                        <Typography variant="body2" color="textSecondary" sx={{ alignSelf: 'center' }}>
                            {selectedBuilds.size} of {unanalyzedFailures.length} selected
                        </Typography>
                    </Box>
                    <Button
                        variant="contained"
                        size="large"
                        startIcon={analyzing ? null : <PlayArrowIcon />}
                        onClick={handleTrigger}
                        disabled={selectedBuilds.size === 0 || analyzing}
                        sx={{
                            borderRadius: 3,
                            bgcolor: '#ea580c',
                            '&:hover': { bgcolor: '#c2410c' },
                            px: 4
                        }}
                    >
                        {analyzing ? `Analyzing... ${progress}%` : `Trigger Analysis (${selectedBuilds.size})`}
                    </Button>
                </Paper>

                {/* Progress Bar */}
                {analyzing && (
                    <Alert severity="info" sx={{ mb: 3, borderRadius: 3 }} icon={<SmartToyIcon />}>
                        <Box sx={{ width: '100%' }}>
                            <Typography variant="body2" mb={1}>
                                Analyzing {selectedBuilds.size} failures... Please wait.
                            </Typography>
                            <LinearProgress variant="determinate" value={progress} sx={{ borderRadius: 2 }} />
                        </Box>
                    </Alert>
                )}

                {/* Table */}
                <Paper elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', overflow: 'hidden' }}>
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow sx={{ bgcolor: '#f8fafc' }}>
                                    <TableCell padding="checkbox">
                                        <Checkbox
                                            checked={selectedBuilds.size === unanalyzedFailures.length}
                                            indeterminate={selectedBuilds.size > 0 && selectedBuilds.size < unanalyzedFailures.length}
                                            onChange={handleSelectAll}
                                        />
                                    </TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Build ID</TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Test Name</TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Job</TableCell>
                                    <TableCell align="center" sx={{ fontWeight: 600, color: '#64748b' }}>Fails</TableCell>
                                    <TableCell align="center" sx={{ fontWeight: 600, color: '#64748b' }}>Age</TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Error Message</TableCell>
                                    <TableCell align="center" sx={{ fontWeight: 600, color: '#64748b' }}>Status</TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Timestamp</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {loading ? (
                                    // Loading skeleton rows
                                    [...Array(5)].map((_, idx) => (
                                        <TableRow key={idx}>
                                            <TableCell padding="checkbox"><Skeleton variant="circular" width={20} height={20} /></TableCell>
                                            <TableCell><Skeleton width={60} /></TableCell>
                                            <TableCell><Skeleton width={200} /></TableCell>
                                            <TableCell><Skeleton width={100} /></TableCell>
                                            <TableCell><Skeleton width={30} /></TableCell>
                                            <TableCell><Skeleton width={40} /></TableCell>
                                            <TableCell><Skeleton width={250} /></TableCell>
                                            <TableCell><Skeleton width={80} /></TableCell>
                                            <TableCell><Skeleton width={120} /></TableCell>
                                        </TableRow>
                                    ))
                                ) : unanalyzedFailures.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={9} align="center" sx={{ py: 6 }}>
                                            {error ? (
                                                <Box>
                                                    <WarningIcon sx={{ fontSize: 48, color: '#ef4444', mb: 1 }} />
                                                    <Typography variant="h6" color="error" gutterBottom>
                                                        {error}
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
                                                    <CheckCircleIcon sx={{ fontSize: 48, color: '#10b981', mb: 1 }} />
                                                    <Typography variant="h6" color="textSecondary" gutterBottom>
                                                        All Caught Up!
                                                    </Typography>
                                                    <Typography variant="body2" color="textSecondary">
                                                        No unanalyzed failures at the moment.
                                                    </Typography>
                                                </Box>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    unanalyzedFailures.map((failure) => (
                                        <TableRow
                                            key={failure.id}
                                            sx={{
                                                '&:hover': { bgcolor: '#f8fafc' },
                                                bgcolor: selectedBuilds.has(failure.id) ? alpha('#ea580c', 0.05) : 'transparent'
                                            }}
                                        >
                                            <TableCell padding="checkbox">
                                                <Checkbox
                                                    checked={selectedBuilds.has(failure.id)}
                                                    onChange={() => handleSelect(failure.id)}
                                                    disabled={failure.status !== 'pending'}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2" fontFamily="monospace" fontWeight={600} color="#3b82f6">
                                                    {failure.buildId}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2" fontWeight={500}>{failure.testName}</Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2" color="textSecondary">{failure.jobName}</Typography>
                                            </TableCell>
                                            <TableCell align="center">
                                                <Chip
                                                    label={failure.failCount || 1}
                                                    size="small"
                                                    sx={{
                                                        bgcolor: '#fee2e2',
                                                        color: '#991b1b',
                                                        fontWeight: 600,
                                                        fontSize: '0.75rem',
                                                        minWidth: 28
                                                    }}
                                                />
                                            </TableCell>
                                            <TableCell align="center">
                                                {(() => {
                                                    const days = getAgingDays(failure.rawTimestamp);
                                                    const agingStyle = getAgingColor(days);
                                                    return (
                                                        <Chip
                                                            label={`${days}d`}
                                                            size="small"
                                                            sx={{
                                                                bgcolor: agingStyle.bg,
                                                                color: agingStyle.color,
                                                                fontWeight: 600,
                                                                fontSize: '0.7rem'
                                                            }}
                                                        />
                                                    );
                                                })()}
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2" sx={{ maxWidth: 300 }} noWrap>{failure.errorMessage}</Typography>
                                            </TableCell>
                                            <TableCell align="center">
                                                <Chip
                                                    label={failure.status.toUpperCase()}
                                                    size="small"
                                                    icon={
                                                        failure.status === 'completed' ? <CheckCircleIcon sx={{ fontSize: 14 }} /> :
                                                        failure.status === 'analyzing' ? <SmartToyIcon sx={{ fontSize: 14 }} /> :
                                                        failure.status === 'failed' ? <ErrorIcon sx={{ fontSize: 14 }} /> :
                                                        <PendingIcon sx={{ fontSize: 14 }} />
                                                    }
                                                    sx={{
                                                        bgcolor: failure.status === 'completed' ? '#dcfce7' :
                                                                failure.status === 'analyzing' ? '#dbeafe' :
                                                                failure.status === 'failed' ? '#fee2e2' : '#fef3c7',
                                                        color: failure.status === 'completed' ? '#166534' :
                                                               failure.status === 'analyzing' ? '#1e40af' :
                                                               failure.status === 'failed' ? '#991b1b' : '#92400e',
                                                        fontWeight: 600,
                                                        fontSize: '0.7rem'
                                                    }}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2" color="textSecondary">{failure.timestamp}</Typography>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Paper>
            </Container>
        </Box>
    );
};

export default TriggerAnalysisPreview;
