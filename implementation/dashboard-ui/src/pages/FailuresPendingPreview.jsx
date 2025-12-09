import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box, Container, Paper, Typography, Grid, Button, Chip, Avatar, IconButton,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    Card, CardContent, Alert, Tooltip, CircularProgress, Dialog, DialogTitle,
    DialogContent, DialogActions, TextField, Stepper, Step, StepLabel, Badge,
    Collapse, Divider, LinearProgress, Snackbar
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import { useColorTheme } from '../theme/ThemeContext';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PendingActionsIcon from '@mui/icons-material/PendingActions';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import BuildIcon from '@mui/icons-material/Build';
import BugReportIcon from '@mui/icons-material/BugReport';
import CodeIcon from '@mui/icons-material/Code';
import GitHubIcon from '@mui/icons-material/GitHub';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import ThumbDownIcon from '@mui/icons-material/ThumbDown';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import MergeIcon from '@mui/icons-material/Merge';
import VerifiedIcon from '@mui/icons-material/Verified';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import { failuresAPI, fixAPI, jiraAPI, monitoringAPI } from '../services/api';

// Code Healing Flow Stages
const HEALING_STAGES = [
    { id: 'ai_analysis', label: 'AI Analysis', icon: <SmartToyIcon />, description: 'AI analyzes code to find error' },
    { id: 'human_approval', label: 'Human Approval', icon: <FactCheckIcon />, description: 'Human approves AI fix suggestion' },
    { id: 'pr_created', label: 'PR Created', icon: <GitHubIcon />, description: 'Pull Request created with fix' },
    { id: 'build_running', label: 'Build Running', icon: <BuildIcon />, description: 'Build triggered to verify fix' },
    { id: 'build_passed', label: 'Build Passed', icon: <VerifiedIcon />, description: 'Build verification successful' },
    { id: 'jira_created', label: 'Jira Created', icon: <BugReportIcon />, description: 'Bug ticket created in Jira' },
];

const getStageIndex = (stageId) => HEALING_STAGES.findIndex(s => s.id === stageId);

const StatCard = ({ title, value, icon, color, loading, onClick }) => (
    <Card
        elevation={0}
        onClick={onClick}
        sx={{
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            cursor: onClick ? 'pointer' : 'default',
            transition: 'all 0.2s',
            '&:hover': onClick ? { transform: 'translateY(-2px)', boxShadow: '0 8px 25px rgba(0,0,0,0.1)' } : {}
        }}
    >
        <CardContent sx={{ p: 2.5 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                    <Typography variant="body2" color="textSecondary" fontWeight={500}>{title}</Typography>
                    {loading ? (
                        <CircularProgress size={24} sx={{ mt: 1 }} />
                    ) : (
                        <Typography variant="h4" fontWeight="bold" sx={{ color }}>{value}</Typography>
                    )}
                </Box>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: alpha(color, 0.1), color }}>
                    {icon}
                </Box>
            </Box>
        </CardContent>
    </Card>
);

const FailuresPendingPreview = () => {
    const { theme } = useColorTheme();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [pendingItems, setPendingItems] = useState([]);
    const [expandedRow, setExpandedRow] = useState(null);
    const [stats, setStats] = useState({
        pendingApproval: 0,
        prCreated: 0,
        buildRunning: 0,
        buildPassed: 0,
        jiraCreated: 0
    });
    const [actionDialogOpen, setActionDialogOpen] = useState(false);
    const [selectedItem, setSelectedItem] = useState(null);
    const [actionType, setActionType] = useState('');
    const [actionLoading, setActionLoading] = useState(false);
    const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

    // Fetch pending items
    const fetchData = useCallback(async () => {
        try {
            // Fetch failures with AI analysis that are pending in the healing flow
            const [failuresRes, statsRes] = await Promise.all([
                failuresAPI.getList({ analyzed: 'true', limit: 50 }),
                monitoringAPI.getStats().catch(() => ({}))
            ]);

            const failures = failuresRes?.data?.failures || failuresRes?.failures || [];

            // Transform and enrich with healing flow status
            const enrichedItems = failures.map(f => ({
                ...f,
                healing_stage: f.healing_stage || (f.ai_approved ? 'pr_created' : 'human_approval'),
                pr_url: f.pr_url || null,
                pr_number: f.pr_number || null,
                build_status: f.build_status || 'pending',
                jira_key: f.jira_key || null,
                jira_url: f.jira_url || null
            }));

            setPendingItems(enrichedItems);

            // Calculate stats
            const pendingApproval = enrichedItems.filter(i => i.healing_stage === 'human_approval').length;
            const prCreated = enrichedItems.filter(i => i.healing_stage === 'pr_created').length;
            const buildRunning = enrichedItems.filter(i => i.healing_stage === 'build_running').length;
            const buildPassed = enrichedItems.filter(i => i.healing_stage === 'build_passed').length;
            const jiraCreated = enrichedItems.filter(i => i.healing_stage === 'jira_created').length;

            setStats({ pendingApproval, prCreated, buildRunning, buildPassed, jiraCreated });
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, [fetchData]);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchData();
    };

    const toggleRowExpand = (id) => {
        setExpandedRow(expandedRow === id ? null : id);
    };

    // Action handlers
    const openActionDialog = (item, action) => {
        setSelectedItem(item);
        setActionType(action);
        setActionDialogOpen(true);
    };

    const handleApproveForPR = async () => {
        if (!selectedItem) return;
        setActionLoading(true);
        try {
            await fixAPI.approve({
                build_id: selectedItem.build_id,
                approved_by: 'dashboard_user'
            });
            setSnackbar({ open: true, message: 'Fix approved! PR will be created.', severity: 'success' });
            setActionDialogOpen(false);
            fetchData();
        } catch (error) {
            setSnackbar({ open: true, message: 'Failed to approve: ' + error.message, severity: 'error' });
        } finally {
            setActionLoading(false);
        }
    };

    const handleRejectFix = async () => {
        if (!selectedItem) return;
        setActionLoading(true);
        try {
            await fixAPI.reject({
                build_id: selectedItem.build_id,
                rejected_by: 'dashboard_user',
                reason: 'Manual rejection from dashboard'
            });
            setSnackbar({ open: true, message: 'Fix rejected.', severity: 'info' });
            setActionDialogOpen(false);
            fetchData();
        } catch (error) {
            setSnackbar({ open: true, message: 'Failed to reject: ' + error.message, severity: 'error' });
        } finally {
            setActionLoading(false);
        }
    };

    const handleCreateJira = async () => {
        if (!selectedItem) return;
        setActionLoading(true);
        try {
            await jiraAPI.createBug({
                build_id: selectedItem.build_id,
                error_category: selectedItem.error_category,
                root_cause: selectedItem.root_cause,
                suggested_fix: selectedItem.suggested_fix,
                file_path: selectedItem.file_path,
                line_number: selectedItem.line_number
            });
            setSnackbar({ open: true, message: 'Jira bug created successfully!', severity: 'success' });
            setActionDialogOpen(false);
            fetchData();
        } catch (error) {
            setSnackbar({ open: true, message: 'Failed to create Jira: ' + error.message, severity: 'error' });
        } finally {
            setActionLoading(false);
        }
    };

    const getStageColor = (stage) => {
        const colors = {
            'ai_analysis': '#3b82f6',
            'human_approval': '#f59e0b',
            'pr_created': '#8b5cf6',
            'build_running': '#06b6d4',
            'build_passed': '#10b981',
            'jira_created': '#ec4899'
        };
        return colors[stage] || '#64748b';
    };

    const getStageLabel = (stage) => {
        const labels = {
            'ai_analysis': 'AI Analyzing',
            'human_approval': 'Awaiting Approval',
            'pr_created': 'PR Created',
            'build_running': 'Build Running',
            'build_passed': 'Build Passed',
            'jira_created': 'Jira Created'
        };
        return labels[stage] || stage;
    };

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: theme.background, pb: 4 }}>
            {/* Header */}
            <Box
                sx={{
                    background: 'linear-gradient(135deg, #7c3aed 0%, #4c1d95 100%)',
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
                                    <AutoFixHighIcon />
                                </Avatar>
                                <Typography variant="h4" fontWeight="bold">
                                    Code Healing Pipeline
                                </Typography>
                            </Box>
                            <Typography variant="subtitle1" sx={{ opacity: 0.9, ml: 8 }}>
                                Track CODE_ERROR fixes from AI analysis to Jira creation
                            </Typography>
                        </Box>
                        <Box display="flex" gap={2}>
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
                {/* Flow Stages Overview */}
                <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                    <Typography variant="h6" fontWeight="bold" mb={3}>Code Healing Flow</Typography>
                    <Stepper alternativeLabel>
                        {HEALING_STAGES.map((stage, index) => (
                            <Step key={stage.id} completed={false}>
                                <StepLabel
                                    StepIconComponent={() => (
                                        <Avatar sx={{ bgcolor: alpha(getStageColor(stage.id), 0.1), color: getStageColor(stage.id), width: 40, height: 40 }}>
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

                {/* Stats Cards */}
                <Grid container spacing={3} mb={4}>
                    <Grid item xs={6} md={2.4}>
                        <StatCard
                            title="Pending Approval"
                            value={loading ? '-' : stats.pendingApproval}
                            icon={<PendingActionsIcon />}
                            color="#f59e0b"
                            loading={loading}
                        />
                    </Grid>
                    <Grid item xs={6} md={2.4}>
                        <StatCard
                            title="PR Created"
                            value={loading ? '-' : stats.prCreated}
                            icon={<GitHubIcon />}
                            color="#8b5cf6"
                            loading={loading}
                        />
                    </Grid>
                    <Grid item xs={6} md={2.4}>
                        <StatCard
                            title="Build Running"
                            value={loading ? '-' : stats.buildRunning}
                            icon={<BuildIcon />}
                            color="#06b6d4"
                            loading={loading}
                        />
                    </Grid>
                    <Grid item xs={6} md={2.4}>
                        <StatCard
                            title="Build Passed"
                            value={loading ? '-' : stats.buildPassed}
                            icon={<VerifiedIcon />}
                            color="#10b981"
                            loading={loading}
                        />
                    </Grid>
                    <Grid item xs={6} md={2.4}>
                        <StatCard
                            title="Jira Created"
                            value={loading ? '-' : stats.jiraCreated}
                            icon={<BugReportIcon />}
                            color="#ec4899"
                            loading={loading}
                        />
                    </Grid>
                </Grid>

                {/* Info Alert */}
                <Alert
                    severity="info"
                    sx={{ mb: 3, borderRadius: 3 }}
                    icon={<AutoFixHighIcon />}
                >
                    <Typography variant="body2">
                        <strong>Code Healing Pipeline:</strong> After AI identifies the error line and suggests a fix,
                        human approval triggers PR creation &#8594; Build verification &#8594; If build passes, approve to create Jira bug.
                    </Typography>
                </Alert>

                {/* Pending Items Table */}
                <Paper elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', overflow: 'hidden' }}>
                    {loading && <LinearProgress />}
                    <Box sx={{ p: 3, borderBottom: '1px solid #e5e7eb' }}>
                        <Typography variant="h6" fontWeight={600}>
                            <Badge badgeContent={pendingItems.length} color="primary" sx={{ mr: 2 }}>
                                <CodeIcon color="action" />
                            </Badge>
                            CODE_ERROR Items in Healing Pipeline
                        </Typography>
                    </Box>

                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow sx={{ bgcolor: '#f8fafc' }}>
                                    <TableCell sx={{ fontWeight: 600, width: 40 }}></TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Build #</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Test / Error</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Current Stage</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>File / Line</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>PR Status</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Build Status</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Jira</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }} align="center">Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {loading ? (
                                    [...Array(3)].map((_, idx) => (
                                        <TableRow key={idx}>
                                            <TableCell colSpan={9} sx={{ py: 2 }}>
                                                <Box sx={{ height: 60, bgcolor: '#f1f5f9', borderRadius: 2, animation: 'pulse 1.5s infinite' }} />
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : pendingItems.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={9} align="center" sx={{ py: 8 }}>
                                            <AutoFixHighIcon sx={{ fontSize: 48, color: '#cbd5e1', mb: 2 }} />
                                            <Typography variant="h6" color="textSecondary">No CODE_ERROR items in pipeline</Typography>
                                            <Typography variant="body2" color="textSecondary">
                                                When CODE_ERROR is approved in RAG Review, it will appear here
                                            </Typography>
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    pendingItems.filter(item => item.error_category === 'CODE_ERROR').map((item) => {
                                        const currentStageIndex = getStageIndex(item.healing_stage);
                                        const isExpanded = expandedRow === item._id;

                                        return (
                                            <React.Fragment key={item._id}>
                                                <TableRow
                                                    hover
                                                    onClick={() => toggleRowExpand(item._id)}
                                                    sx={{
                                                        cursor: 'pointer',
                                                        bgcolor: isExpanded ? '#f8fafc' : 'inherit',
                                                        '&:hover': { bgcolor: '#f1f5f9' }
                                                    }}
                                                >
                                                    <TableCell>
                                                        <IconButton size="small">
                                                            {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                                        </IconButton>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography fontWeight={600}>#{item.build_id}</Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2" fontWeight={500}>
                                                            {item.test_name || item.job_name || '-'}
                                                        </Typography>
                                                        <Tooltip title={item.root_cause || item.error_message}>
                                                            <Typography variant="caption" color="error" sx={{ display: 'block', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                                {item.root_cause || item.error_message || '-'}
                                                            </Typography>
                                                        </Tooltip>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip
                                                            icon={HEALING_STAGES[currentStageIndex]?.icon}
                                                            label={getStageLabel(item.healing_stage)}
                                                            size="small"
                                                            sx={{
                                                                bgcolor: alpha(getStageColor(item.healing_stage), 0.1),
                                                                color: getStageColor(item.healing_stage),
                                                                '& .MuiChip-icon': { color: 'inherit' },
                                                                fontWeight: 600
                                                            }}
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        {item.file_path ? (
                                                            <Box>
                                                                <Typography variant="caption" sx={{ fontFamily: 'monospace', display: 'block' }}>
                                                                    {item.file_path.split('/').pop()}
                                                                </Typography>
                                                                <Chip label={`Line ${item.line_number || '?'}`} size="small" sx={{ height: 18, fontSize: '0.65rem', bgcolor: '#fee2e2', color: '#991b1b' }} />
                                                            </Box>
                                                        ) : '-'}
                                                    </TableCell>
                                                    <TableCell>
                                                        {item.pr_number ? (
                                                            <Chip
                                                                icon={<GitHubIcon />}
                                                                label={`PR #${item.pr_number}`}
                                                                size="small"
                                                                sx={{ bgcolor: '#f3e8ff', color: '#7c3aed', '& .MuiChip-icon': { color: 'inherit', fontSize: 14 } }}
                                                                onClick={(e) => { e.stopPropagation(); window.open(item.pr_url, '_blank'); }}
                                                            />
                                                        ) : (
                                                            <Chip label="Pending" size="small" variant="outlined" />
                                                        )}
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip
                                                            icon={item.build_status === 'passed' ? <CheckCircleIcon /> :
                                                                  item.build_status === 'failed' ? <ErrorIcon /> :
                                                                  item.build_status === 'running' ? <CircularProgress size={12} /> : <HourglassEmptyIcon />}
                                                            label={item.build_status === 'passed' ? 'Passed' :
                                                                   item.build_status === 'failed' ? 'Failed' :
                                                                   item.build_status === 'running' ? 'Running' : 'Pending'}
                                                            size="small"
                                                            sx={{
                                                                bgcolor: item.build_status === 'passed' ? '#dcfce7' :
                                                                         item.build_status === 'failed' ? '#fee2e2' :
                                                                         item.build_status === 'running' ? '#dbeafe' : '#f1f5f9',
                                                                color: item.build_status === 'passed' ? '#166534' :
                                                                       item.build_status === 'failed' ? '#991b1b' :
                                                                       item.build_status === 'running' ? '#1e40af' : '#64748b',
                                                                '& .MuiChip-icon': { color: 'inherit', fontSize: 14 }
                                                            }}
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        {item.jira_key ? (
                                                            <Chip
                                                                icon={<BugReportIcon />}
                                                                label={item.jira_key}
                                                                size="small"
                                                                sx={{ bgcolor: '#fce7f3', color: '#be185d', '& .MuiChip-icon': { color: 'inherit', fontSize: 14 } }}
                                                                onClick={(e) => { e.stopPropagation(); window.open(item.jira_url, '_blank'); }}
                                                            />
                                                        ) : (
                                                            <Chip label="Not Created" size="small" variant="outlined" sx={{ fontSize: '0.7rem' }} />
                                                        )}
                                                    </TableCell>
                                                    <TableCell align="center">
                                                        <Box display="flex" gap={0.5} justifyContent="center">
                                                            {/* Show appropriate actions based on stage */}
                                                            {item.healing_stage === 'human_approval' && (
                                                                <>
                                                                    <Tooltip title="Approve - Create PR with fix">
                                                                        <IconButton
                                                                            color="success"
                                                                            size="small"
                                                                            onClick={(e) => { e.stopPropagation(); openActionDialog(item, 'approve'); }}
                                                                        >
                                                                            <ThumbUpIcon fontSize="small" />
                                                                        </IconButton>
                                                                    </Tooltip>
                                                                    <Tooltip title="Reject fix suggestion">
                                                                        <IconButton
                                                                            color="error"
                                                                            size="small"
                                                                            onClick={(e) => { e.stopPropagation(); openActionDialog(item, 'reject'); }}
                                                                        >
                                                                            <ThumbDownIcon fontSize="small" />
                                                                        </IconButton>
                                                                    </Tooltip>
                                                                </>
                                                            )}
                                                            {item.healing_stage === 'build_passed' && !item.jira_key && (
                                                                <Tooltip title="Create Jira Bug">
                                                                    <IconButton
                                                                        color="primary"
                                                                        size="small"
                                                                        onClick={(e) => { e.stopPropagation(); openActionDialog(item, 'jira'); }}
                                                                    >
                                                                        <BugReportIcon fontSize="small" />
                                                                    </IconButton>
                                                                </Tooltip>
                                                            )}
                                                            <Tooltip title="View Details">
                                                                <IconButton
                                                                    size="small"
                                                                    onClick={(e) => { e.stopPropagation(); navigate(`/failures/${item.build_id || item._id}`); }}
                                                                >
                                                                    <OpenInNewIcon fontSize="small" />
                                                                </IconButton>
                                                            </Tooltip>
                                                        </Box>
                                                    </TableCell>
                                                </TableRow>

                                                {/* Expanded Details */}
                                                <TableRow>
                                                    <TableCell colSpan={9} sx={{ py: 0, borderBottom: isExpanded ? undefined : 'none' }}>
                                                        <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                                                            <Box sx={{ py: 3, px: 2, bgcolor: '#f8fafc' }}>
                                                                {/* Progress Stepper */}
                                                                <Box mb={3}>
                                                                    <Stepper activeStep={currentStageIndex} alternativeLabel>
                                                                        {HEALING_STAGES.map((stage, index) => (
                                                                            <Step key={stage.id} completed={index < currentStageIndex}>
                                                                                <StepLabel
                                                                                    StepIconComponent={() => (
                                                                                        <Avatar
                                                                                            sx={{
                                                                                                bgcolor: index <= currentStageIndex ? getStageColor(stage.id) : '#e2e8f0',
                                                                                                color: 'white',
                                                                                                width: 32,
                                                                                                height: 32
                                                                                            }}
                                                                                        >
                                                                                            {index < currentStageIndex ? <CheckCircleIcon sx={{ fontSize: 18 }} /> : stage.icon}
                                                                                        </Avatar>
                                                                                    )}
                                                                                >
                                                                                    <Typography variant="caption">{stage.label}</Typography>
                                                                                </StepLabel>
                                                                            </Step>
                                                                        ))}
                                                                    </Stepper>
                                                                </Box>

                                                                <Grid container spacing={3}>
                                                                    {/* Root Cause */}
                                                                    <Grid item xs={12} md={4}>
                                                                        <Paper sx={{ p: 2, borderRadius: 2, bgcolor: '#fef2f2', border: '1px solid #fecaca' }}>
                                                                            <Typography variant="subtitle2" fontWeight={600} color="#991b1b" mb={1}>
                                                                                Root Cause Identified
                                                                            </Typography>
                                                                            <Typography variant="body2">
                                                                                {item.root_cause || item.error_message || 'No root cause identified'}
                                                                            </Typography>
                                                                            {item.file_path && (
                                                                                <Box mt={1} p={1} bgcolor="white" borderRadius={1}>
                                                                                    <Typography variant="caption" fontFamily="monospace">
                                                                                        {item.file_path}:{item.line_number}
                                                                                    </Typography>
                                                                                </Box>
                                                                            )}
                                                                        </Paper>
                                                                    </Grid>

                                                                    {/* Suggested Fix */}
                                                                    <Grid item xs={12} md={4}>
                                                                        <Paper sx={{ p: 2, borderRadius: 2, bgcolor: '#f0fdf4', border: '1px solid #bbf7d0' }}>
                                                                            <Typography variant="subtitle2" fontWeight={600} color="#166534" mb={1}>
                                                                                AI Suggested Fix
                                                                            </Typography>
                                                                            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                                                                {item.suggested_fix || 'No fix suggestion available'}
                                                                            </Typography>
                                                                        </Paper>
                                                                    </Grid>

                                                                    {/* Status & Actions */}
                                                                    <Grid item xs={12} md={4}>
                                                                        <Paper sx={{ p: 2, borderRadius: 2 }}>
                                                                            <Typography variant="subtitle2" fontWeight={600} mb={2}>
                                                                                Pipeline Status
                                                                            </Typography>
                                                                            <Box display="flex" flexDirection="column" gap={1}>
                                                                                <Box display="flex" justifyContent="space-between">
                                                                                    <Typography variant="body2" color="textSecondary">PR:</Typography>
                                                                                    <Typography variant="body2" fontWeight={500}>
                                                                                        {item.pr_number ? `#${item.pr_number}` : 'Not created'}
                                                                                    </Typography>
                                                                                </Box>
                                                                                <Box display="flex" justifyContent="space-between">
                                                                                    <Typography variant="body2" color="textSecondary">Build:</Typography>
                                                                                    <Typography variant="body2" fontWeight={500}>
                                                                                        {item.build_status || 'Pending'}
                                                                                    </Typography>
                                                                                </Box>
                                                                                <Box display="flex" justifyContent="space-between">
                                                                                    <Typography variant="body2" color="textSecondary">Jira:</Typography>
                                                                                    <Typography variant="body2" fontWeight={500}>
                                                                                        {item.jira_key || 'Not created'}
                                                                                    </Typography>
                                                                                </Box>
                                                                            </Box>
                                                                            <Divider sx={{ my: 2 }} />
                                                                            <Box display="flex" gap={1}>
                                                                                {item.healing_stage === 'human_approval' && (
                                                                                    <Button
                                                                                        variant="contained"
                                                                                        size="small"
                                                                                        color="success"
                                                                                        startIcon={<ThumbUpIcon />}
                                                                                        onClick={() => openActionDialog(item, 'approve')}
                                                                                        fullWidth
                                                                                    >
                                                                                        Approve Fix
                                                                                    </Button>
                                                                                )}
                                                                                {item.healing_stage === 'build_passed' && !item.jira_key && (
                                                                                    <Button
                                                                                        variant="contained"
                                                                                        size="small"
                                                                                        color="primary"
                                                                                        startIcon={<BugReportIcon />}
                                                                                        onClick={() => openActionDialog(item, 'jira')}
                                                                                        fullWidth
                                                                                    >
                                                                                        Create Jira
                                                                                    </Button>
                                                                                )}
                                                                            </Box>
                                                                        </Paper>
                                                                    </Grid>
                                                                </Grid>
                                                            </Box>
                                                        </Collapse>
                                                    </TableCell>
                                                </TableRow>
                                            </React.Fragment>
                                        );
                                    })
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Paper>
            </Container>

            {/* Action Dialog */}
            <Dialog open={actionDialogOpen} onClose={() => setActionDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle sx={{
                    bgcolor: actionType === 'approve' ? '#dcfce7' :
                             actionType === 'reject' ? '#fee2e2' : '#dbeafe'
                }}>
                    {actionType === 'approve' && 'Approve Fix & Create PR'}
                    {actionType === 'reject' && 'Reject Fix Suggestion'}
                    {actionType === 'jira' && 'Create Jira Bug'}
                </DialogTitle>
                <DialogContent>
                    {selectedItem && (
                        <Box sx={{ mt: 2 }}>
                            <Box sx={{ p: 2, bgcolor: '#f8fafc', borderRadius: 2, mb: 2 }}>
                                <Typography variant="subtitle2" color="textSecondary">Build</Typography>
                                <Typography fontWeight={600}>#{selectedItem.build_id}</Typography>
                                <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 1 }}>Error</Typography>
                                <Typography variant="body2">{selectedItem.root_cause || selectedItem.error_message}</Typography>
                            </Box>

                            {actionType === 'approve' && (
                                <Alert severity="info">
                                    <Typography variant="body2">
                                        Approving will create a Pull Request with the AI-suggested fix.
                                        After PR is merged, a build will be triggered to verify the fix.
                                    </Typography>
                                </Alert>
                            )}

                            {actionType === 'jira' && (
                                <Alert severity="info">
                                    <Typography variant="body2">
                                        Build has passed! Creating a Jira bug will document the error and the fix applied.
                                    </Typography>
                                </Alert>
                            )}
                        </Box>
                    )}
                </DialogContent>
                <DialogActions sx={{ p: 2 }}>
                    <Button onClick={() => setActionDialogOpen(false)} disabled={actionLoading}>
                        Cancel
                    </Button>
                    <Button
                        variant="contained"
                        onClick={
                            actionType === 'approve' ? handleApproveForPR :
                            actionType === 'reject' ? handleRejectFix : handleCreateJira
                        }
                        disabled={actionLoading}
                        color={actionType === 'approve' ? 'success' : actionType === 'reject' ? 'error' : 'primary'}
                        startIcon={actionLoading ? <CircularProgress size={18} /> : null}
                    >
                        {actionType === 'approve' && 'Create PR'}
                        {actionType === 'reject' && 'Reject'}
                        {actionType === 'jira' && 'Create Jira'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Snackbar */}
            <Snackbar
                open={snackbar.open}
                autoHideDuration={4000}
                onClose={() => setSnackbar({ ...snackbar, open: false })}
            >
                <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Box>
    );
};

export default FailuresPendingPreview;
