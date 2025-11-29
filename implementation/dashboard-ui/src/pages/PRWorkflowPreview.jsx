import React, { useState, useEffect } from 'react';
import {
    Box, Container, Paper, Typography, Grid, Button, Chip, Avatar, IconButton,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TablePagination,
    Card, CardContent, Alert, Tooltip, Divider, Stepper, Step, StepLabel,
    Dialog, DialogTitle, DialogContent, DialogActions, LinearProgress, Collapse,
    Skeleton, CircularProgress
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import RefreshIcon from '@mui/icons-material/Refresh';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import GitHubIcon from '@mui/icons-material/GitHub';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import ErrorIcon from '@mui/icons-material/Error';
import MergeIcon from '@mui/icons-material/Merge';
import CodeIcon from '@mui/icons-material/Code';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import ScheduleIcon from '@mui/icons-material/Schedule';
import BuildIcon from '@mui/icons-material/Build';
import VerifiedIcon from '@mui/icons-material/Verified';
import CallMergeIcon from '@mui/icons-material/CallMerge';
import CancelIcon from '@mui/icons-material/Cancel';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import ReviewsIcon from '@mui/icons-material/Reviews';
import { fixAPI } from '../services/api';

// PR Workflow Stages
const prStages = [
    { id: 'approved', label: 'Fix Approved', icon: <CheckCircleIcon />, description: 'User approved AI-suggested code fix' },
    { id: 'branch', label: 'Branch Created', icon: <CodeIcon />, description: 'Feature branch created from main' },
    { id: 'commit', label: 'Changes Committed', icon: <GitHubIcon />, description: 'Code changes committed to branch' },
    { id: 'pr_created', label: 'PR Created', icon: <CallMergeIcon />, description: 'Pull request opened on GitHub' },
    { id: 'ci_running', label: 'CI Running', icon: <BuildIcon />, description: 'Automated tests and checks running' },
    { id: 'review', label: 'Code Review', icon: <ReviewsIcon />, description: 'Awaiting code review approval' },
    { id: 'merged', label: 'Merged', icon: <MergeIcon />, description: 'PR merged to main branch' },
];


const getStageIndex = (stageId) => prStages.findIndex(s => s.id === stageId);

const getStatusColor = (status) => {
    switch (status) {
        case 'merged': return { bg: '#dcfce7', color: '#166534', label: 'Merged' };
        case 'review': return { bg: '#fef3c7', color: '#92400e', label: 'In Review' };
        case 'ci_running': return { bg: '#dbeafe', color: '#1e40af', label: 'CI Running' };
        case 'failed': return { bg: '#fee2e2', color: '#991b1b', label: 'CI Failed' };
        case 'closed': return { bg: '#f1f5f9', color: '#64748b', label: 'Closed' };
        default: return { bg: '#e0e7ff', color: '#4338ca', label: 'Open' };
    }
};

const getCIStatusIcon = (status) => {
    switch (status) {
        case 'passed': return <CheckCircleIcon sx={{ color: '#10b981', fontSize: 20 }} />;
        case 'failed': return <ErrorIcon sx={{ color: '#ef4444', fontSize: 20 }} />;
        case 'running': return <HourglassEmptyIcon sx={{ color: '#3b82f6', fontSize: 20 }} />;
        default: return <HourglassEmptyIcon sx={{ color: '#94a3b8', fontSize: 20 }} />;
    }
};

const StageStatusIcon = ({ status }) => {
    switch (status) {
        case 'completed': return <CheckCircleIcon sx={{ color: '#10b981', fontSize: 20 }} />;
        case 'in_progress': return <HourglassEmptyIcon sx={{ color: '#3b82f6', fontSize: 20 }} />;
        case 'failed': return <ErrorIcon sx={{ color: '#ef4444', fontSize: 20 }} />;
        default: return <HourglassEmptyIcon sx={{ color: '#94a3b8', fontSize: 20 }} />;
    }
};

const PRWorkflowPreview = () => {
    const [expandedPR, setExpandedPR] = useState(null);
    const [selectedPR, setSelectedPR] = useState(null);
    const [detailsOpen, setDetailsOpen] = useState(false);

    // Real data state
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [prList, setPrList] = useState([]);
    const [error, setError] = useState(null);

    const fetchPRData = async () => {
        try {
            const response = await fixAPI.getHistory({ limit: 50 });
            const data = response?.data || response;

            if (data?.success) {
                // Transform API data to PR format
                const transformedPRs = (data.fixes || []).map((fix, idx) => ({
                    id: `PR-${fix.pr_number || fix.id}`,
                    prNumber: fix.pr_number || fix.id,
                    title: `fix: ${fix.fix_type || 'Code fix'} for ${fix.failure_id || 'failure'}`,
                    status: fix.status === 'merged' ? 'merged' :
                            fix.status === 'reverted' ? 'failed' :
                            fix.status === 'pr_created' ? 'review' : fix.status,
                    currentStage: fix.status === 'merged' ? 'merged' :
                                  fix.status === 'pending' ? 'approved' : 'pr_created',
                    linkedFailure: `#${fix.failure_id || 'N/A'}`,
                    classification: fix.fix_type?.toUpperCase() || 'CODE_FIX',
                    branch: fix.branch_name || `fix/auto-${fix.id}`,
                    author: 'AI Auto-Fix',
                    approvedBy: fix.applied_by || 'system',
                    createdAt: fix.applied_at,
                    mergedAt: fix.merged_at,
                    aiConfidence: 0.85,
                    filesChanged: 1,
                    additions: 10,
                    deletions: 2,
                    ciStatus: fix.status === 'merged' ? 'passed' :
                              fix.status === 'reverted' ? 'failed' : 'running',
                    reviewers: [],
                    githubUrl: fix.pr_url || '#',
                    stages: {
                        approved: { status: 'completed', timestamp: fix.applied_at },
                        branch: { status: 'completed', timestamp: fix.applied_at },
                        commit: { status: 'completed', timestamp: fix.applied_at },
                        pr_created: { status: fix.pr_number ? 'completed' : 'pending', timestamp: fix.applied_at },
                        ci_running: { status: fix.status === 'merged' ? 'completed' : 'in_progress' },
                        review: { status: fix.status === 'merged' ? 'completed' : 'pending' },
                        merged: { status: fix.status === 'merged' ? 'completed' : 'pending', timestamp: fix.merged_at },
                    }
                }));
                setPrList(transformedPRs);
                setError(null);
            } else {
                setPrList([]);
            }
        } catch (err) {
            console.error('Error fetching PR data:', err);
            setError(err.message?.includes('Network') ? 'No connection to server' : err.message);
            setPrList([]);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        fetchPRData();
    }, []);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchPRData();
    };

    const stats = {
        total: prList.length,
        merged: prList.filter(p => p.status === 'merged').length,
        inProgress: prList.filter(p => ['review', 'ci_running', 'pr_created'].includes(p.status)).length,
        failed: prList.filter(p => p.status === 'failed' || p.status === 'reverted').length
    };

    const formatDateTime = (dateStr) => {
        if (!dateStr) return 'N/A';
        try {
            return new Date(dateStr).toLocaleString();
        } catch {
            return dateStr;
        }
    };

    const handleViewDetails = (pr) => {
        setSelectedPR(pr);
        setDetailsOpen(true);
    };

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc', pb: 4 }}>
            {/* Header */}
            <Box
                sx={{
                    background: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
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
                                PR Workflow
                            </Typography>
                            <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                                Track AI-generated code fix PRs from approval to merge
                            </Typography>
                        </Box>
                        <Box display="flex" gap={2} alignItems="center">
                            <Chip
                                icon={<MergeIcon sx={{ color: '#10b981 !important' }} />}
                                label={`${stats.merged} Merged`}
                                sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                            />
                            <Chip
                                icon={<HourglassEmptyIcon sx={{ color: '#f59e0b !important' }} />}
                                label={`${stats.inProgress} In Progress`}
                                sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                            />
                            <Button
                                variant="contained"
                                startIcon={refreshing ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
                                onClick={handleRefresh}
                                disabled={refreshing}
                                sx={{ bgcolor: 'rgba(255,255,255,0.2)', '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' } }}
                            >
                                Refresh
                            </Button>
                            <Button
                                variant="contained"
                                startIcon={<OpenInNewIcon />}
                                onClick={() => window.open('https://github.com/company/repo/pulls', '_blank')}
                                sx={{ bgcolor: 'rgba(255,255,255,0.2)', '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' } }}
                            >
                                GitHub PRs
                            </Button>
                        </Box>
                    </Box>
                </Container>
            </Box>

            <Container maxWidth="xl">
                {/* Stats Cards */}
                <Grid container spacing={3} mb={4}>
                    {[
                        { label: 'Total PRs', value: stats.total, icon: <CallMergeIcon />, color: '#7c3aed' },
                        { label: 'Merged', value: stats.merged, icon: <MergeIcon />, color: '#10b981' },
                        { label: 'In Progress', value: stats.inProgress, icon: <HourglassEmptyIcon />, color: '#f59e0b' },
                        { label: 'Failed CI', value: stats.failed, icon: <ErrorIcon />, color: '#ef4444' },
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

                {/* PR Workflow Stages Overview */}
                <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                    <Typography variant="h6" fontWeight="bold" mb={3}>PR Workflow Stages</Typography>
                    <Stepper alternativeLabel>
                        {prStages.map((stage) => (
                            <Step key={stage.id} completed={false}>
                                <StepLabel
                                    StepIconComponent={() => (
                                        <Avatar sx={{ bgcolor: alpha('#7c3aed', 0.1), color: '#7c3aed', width: 40, height: 40 }}>
                                            {stage.icon}
                                        </Avatar>
                                    )}
                                >
                                    <Typography variant="body2" fontWeight={600}>{stage.label}</Typography>
                                    <Typography variant="caption" color="textSecondary">{stage.description}</Typography>
                                </StepLabel>
                            </Step>
                        ))}
                    </Stepper>
                </Paper>

                {/* PRs List */}
                <Paper elevation={0} sx={{ p: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                    <Typography variant="h6" fontWeight="bold" mb={3}>Pull Requests</Typography>

                    {/* Error State */}
                    {error && (
                        <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                            <Typography variant="body2"><strong>Error:</strong> {error}</Typography>
                        </Alert>
                    )}

                    {/* Loading State */}
                    {loading ? (
                        [...Array(3)].map((_, idx) => (
                            <Paper key={idx} sx={{ p: 3, mb: 2, borderRadius: 3, border: '1px solid #e2e8f0' }}>
                                <Box display="flex" gap={2} mb={2}>
                                    <Skeleton variant="circular" width={40} height={40} />
                                    <Box flex={1}>
                                        <Skeleton width="60%" height={24} />
                                        <Skeleton width="40%" height={20} />
                                    </Box>
                                </Box>
                                <Skeleton width="100%" height={60} />
                            </Paper>
                        ))
                    ) : prList.length === 0 ? (
                        <Box textAlign="center" py={6}>
                            <GitHubIcon sx={{ fontSize: 64, color: '#e2e8f0', mb: 2 }} />
                            <Typography variant="h6" color="textSecondary">No PR data found</Typography>
                            <Typography variant="body2" color="textSecondary">
                                {error ? 'Check your connection and try again' : 'No code fix PRs have been created yet'}
                            </Typography>
                            <Button
                                variant="outlined"
                                startIcon={<RefreshIcon />}
                                onClick={handleRefresh}
                                sx={{ mt: 2 }}
                            >
                                Retry
                            </Button>
                        </Box>
                    ) : prList.map((pr) => {
                        const statusColors = getStatusColor(pr.status);
                        const currentStageIndex = getStageIndex(pr.currentStage);
                        const isExpanded = expandedPR === pr.id;

                        return (
                            <Paper
                                key={pr.id}
                                sx={{
                                    p: 3,
                                    mb: 2,
                                    borderRadius: 3,
                                    border: pr.status === 'failed' ? '2px solid #fee2e2' : '1px solid #e2e8f0',
                                    bgcolor: pr.status === 'failed' ? '#fffbfb' : '#fafafa'
                                }}
                            >
                                {/* PR Header */}
                                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                                    <Box display="flex" alignItems="flex-start" gap={2}>
                                        <Avatar sx={{ bgcolor: alpha('#7c3aed', 0.1), color: '#7c3aed' }}>
                                            <GitHubIcon />
                                        </Avatar>
                                        <Box>
                                            <Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
                                                <Chip
                                                    label={`#${pr.prNumber}`}
                                                    size="small"
                                                    sx={{ bgcolor: '#e0e7ff', color: '#4338ca', fontWeight: 600 }}
                                                />
                                                <Typography variant="h6" fontWeight="bold">{pr.title}</Typography>
                                            </Box>
                                            <Box display="flex" alignItems="center" gap={2} mt={1} flexWrap="wrap">
                                                <Chip label={statusColors.label} size="small" sx={{ bgcolor: statusColors.bg, color: statusColors.color, fontWeight: 600 }} />
                                                <Box display="flex" alignItems="center" gap={0.5}>
                                                    <SmartToyIcon sx={{ color: '#8b5cf6', fontSize: 16 }} />
                                                    <Typography variant="caption">AI Auto-Fix</Typography>
                                                </Box>
                                                <Box display="flex" alignItems="center" gap={0.5}>
                                                    <CodeIcon sx={{ fontSize: 16, color: '#64748b' }} />
                                                    <Typography variant="caption" color="textSecondary">{pr.branch}</Typography>
                                                </Box>
                                                <Box display="flex" alignItems="center" gap={0.5}>
                                                    {getCIStatusIcon(pr.ciStatus)}
                                                    <Typography variant="caption">CI: {pr.ciStatus}</Typography>
                                                </Box>
                                            </Box>
                                        </Box>
                                    </Box>
                                    <Box display="flex" alignItems="center" gap={1}>
                                        <Tooltip title="Open in GitHub">
                                            <IconButton onClick={() => window.open(pr.githubUrl, '_blank')}>
                                                <OpenInNewIcon />
                                            </IconButton>
                                        </Tooltip>
                                        <IconButton onClick={() => setExpandedPR(isExpanded ? null : pr.id)}>
                                            {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                        </IconButton>
                                    </Box>
                                </Box>

                                {/* Failed CI Error */}
                                {pr.status === 'failed' && pr.ciError && (
                                    <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
                                        <Typography variant="body2"><strong>CI Error:</strong> {pr.ciError}</Typography>
                                    </Alert>
                                )}

                                {/* Progress Stepper */}
                                <Stepper activeStep={currentStageIndex} alternativeLabel>
                                    {prStages.map((stage) => {
                                        const stageData = pr.stages[stage.id];
                                        return (
                                            <Step key={stage.id} completed={stageData?.status === 'completed'}>
                                                <StepLabel
                                                    error={stageData?.status === 'failed'}
                                                    StepIconComponent={() => <StageStatusIcon status={stageData?.status} />}
                                                >
                                                    <Typography variant="caption">
                                                        {stageData?.timestamp ? new Date(stageData.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '-'}
                                                    </Typography>
                                                </StepLabel>
                                            </Step>
                                        );
                                    })}
                                </Stepper>

                                {/* Expanded Details */}
                                <Collapse in={isExpanded}>
                                    <Divider sx={{ my: 2 }} />
                                    <Grid container spacing={3}>
                                        <Grid item xs={12} md={6}>
                                            <Typography variant="subtitle2" color="textSecondary" gutterBottom>PR Details</Typography>
                                            <Grid container spacing={2}>
                                                <Grid item xs={6}>
                                                    <Typography variant="caption" color="textSecondary">Linked Failure</Typography>
                                                    <Typography variant="body2" fontWeight={600}>{pr.linkedFailure}</Typography>
                                                </Grid>
                                                <Grid item xs={6}>
                                                    <Typography variant="caption" color="textSecondary">Classification</Typography>
                                                    <Chip label={pr.classification} size="small" sx={{ mt: 0.5 }} />
                                                </Grid>
                                                <Grid item xs={6}>
                                                    <Typography variant="caption" color="textSecondary">AI Confidence</Typography>
                                                    <Box display="flex" alignItems="center" gap={1}>
                                                        <LinearProgress variant="determinate" value={pr.aiConfidence * 100} sx={{ width: 60, height: 6, borderRadius: 3 }} />
                                                        <Typography variant="body2">{Math.round(pr.aiConfidence * 100)}%</Typography>
                                                    </Box>
                                                </Grid>
                                                <Grid item xs={6}>
                                                    <Typography variant="caption" color="textSecondary">Approved By</Typography>
                                                    <Typography variant="body2" fontWeight={600}>{pr.approvedBy?.split('@')[0]}</Typography>
                                                </Grid>
                                            </Grid>
                                        </Grid>
                                        <Grid item xs={12} md={6}>
                                            <Typography variant="subtitle2" color="textSecondary" gutterBottom>Code Changes</Typography>
                                            <Grid container spacing={2}>
                                                <Grid item xs={4}>
                                                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#f8fafc', borderRadius: 2 }}>
                                                        <Typography variant="h5" fontWeight="bold">{pr.filesChanged}</Typography>
                                                        <Typography variant="caption" color="textSecondary">Files</Typography>
                                                    </Paper>
                                                </Grid>
                                                <Grid item xs={4}>
                                                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#dcfce7', borderRadius: 2 }}>
                                                        <Typography variant="h5" fontWeight="bold" color="#166534">+{pr.additions}</Typography>
                                                        <Typography variant="caption" color="textSecondary">Additions</Typography>
                                                    </Paper>
                                                </Grid>
                                                <Grid item xs={4}>
                                                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#fee2e2', borderRadius: 2 }}>
                                                        <Typography variant="h5" fontWeight="bold" color="#991b1b">-{pr.deletions}</Typography>
                                                        <Typography variant="caption" color="textSecondary">Deletions</Typography>
                                                    </Paper>
                                                </Grid>
                                            </Grid>
                                        </Grid>
                                        <Grid item xs={12}>
                                            <Typography variant="subtitle2" color="textSecondary" gutterBottom>Timeline</Typography>
                                            <Box display="flex" gap={3} flexWrap="wrap">
                                                <Box>
                                                    <Typography variant="caption" color="textSecondary">Created</Typography>
                                                    <Typography variant="body2" fontWeight={600}>{pr.createdAt}</Typography>
                                                </Box>
                                                {pr.mergedAt && (
                                                    <Box>
                                                        <Typography variant="caption" color="textSecondary">Merged</Typography>
                                                        <Typography variant="body2" fontWeight={600}>{pr.mergedAt}</Typography>
                                                    </Box>
                                                )}
                                                {pr.reviewers.length > 0 && (
                                                    <Box>
                                                        <Typography variant="caption" color="textSecondary">Reviewers</Typography>
                                                        <Box display="flex" gap={1}>
                                                            {pr.reviewers.map((r, idx) => (
                                                                <Chip key={idx} avatar={<Avatar>{r[0].toUpperCase()}</Avatar>} label={r.split('@')[0]} size="small" />
                                                            ))}
                                                        </Box>
                                                    </Box>
                                                )}
                                            </Box>
                                        </Grid>
                                    </Grid>
                                </Collapse>
                            </Paper>
                        );
                    })}
                </Paper>

                {/* Info */}
                <Alert severity="info" sx={{ mt: 3, borderRadius: 3 }}>
                    <Typography variant="body2">
                        <strong>PR Workflow:</strong> When user approves an AI-suggested code fix, the system automatically creates a branch, commits the fix, opens a PR, runs CI, and awaits code review before merge.
                    </Typography>
                </Alert>
            </Container>
        </Box>
    );
};

export default PRWorkflowPreview;
