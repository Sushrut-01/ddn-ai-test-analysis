import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box, Container, Paper, Typography, Grid, Button, Chip, Avatar, IconButton,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    Card, CardContent, Alert, Tooltip, CircularProgress, Dialog, DialogTitle,
    DialogContent, DialogActions, TextField, Tabs, Tab, Badge, Snackbar,
    FormControl, InputLabel, Select, MenuItem, Collapse, LinearProgress, Divider
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import { useColorTheme } from '../theme/ThemeContext';
import RefreshIcon from '@mui/icons-material/Refresh';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import EscalatorWarningIcon from '@mui/icons-material/EscalatorWarning';
import PendingActionsIcon from '@mui/icons-material/PendingActions';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import ThumbDownIcon from '@mui/icons-material/ThumbDown';
import SendIcon from '@mui/icons-material/Send';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import CategoryIcon from '@mui/icons-material/Category';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import PercentIcon from '@mui/icons-material/Percent';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ReplayIcon from '@mui/icons-material/Replay';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import DescriptionIcon from '@mui/icons-material/Description';
import StorageIcon from '@mui/icons-material/Storage';
import ArticleIcon from '@mui/icons-material/Article';
import TerminalIcon from '@mui/icons-material/Terminal';
import DataObjectIcon from '@mui/icons-material/DataObject';
import FindInPageIcon from '@mui/icons-material/FindInPage';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import SourceIcon from '@mui/icons-material/Source';
import { ragApprovalAPI, triggerAPI } from '../services/api';

// Input source type icons and colors
const INPUT_SOURCE_CONFIG = {
    xml_report: { icon: <DataObjectIcon sx={{ fontSize: 16 }} />, label: 'XML Report', color: '#3b82f6' },
    console_log: { icon: <TerminalIcon sx={{ fontSize: 16 }} />, label: 'Console Log', color: '#10b981' },
    stack_trace: { icon: <ArticleIcon sx={{ fontSize: 16 }} />, label: 'Stack Trace', color: '#f59e0b' },
    test_output: { icon: <DescriptionIcon sx={{ fontSize: 16 }} />, label: 'Test Output', color: '#8b5cf6' },
    error_message: { icon: <CancelIcon sx={{ fontSize: 16 }} />, label: 'Error Message', color: '#ef4444' },
    build_log: { icon: <StorageIcon sx={{ fontSize: 16 }} />, label: 'Build Log', color: '#06b6d4' }
};

const StatCard = ({ title, value, icon, color, loading }) => (
    <Card elevation={0} sx={{
        borderRadius: 3,
        background: 'rgba(255, 255, 255, 0.9)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
    }}>
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

const RAGApprovalPreview = () => {
    const { theme } = useColorTheme();
    const navigate = useNavigate();
    const [pending, setPending] = useState([]);
    const [stats, setStats] = useState({ pending: 0, approved: 0, rejected: 0, escalated: 0 });
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [selectedItem, setSelectedItem] = useState(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [dialogAction, setDialogAction] = useState('');
    const [feedback, setFeedback] = useState('');
    const [correctCategory, setCorrectCategory] = useState('');
    const [escalateReason, setEscalateReason] = useState('');
    const [selectedCategory, setSelectedCategory] = useState(''); // For approve with category change

    // All available categories
    const ERROR_CATEGORIES = ['CODE_ERROR', 'ENV_CONFIG', 'NETWORK_ERROR', 'INFRA_ERROR', 'UNKNOWN'];
    const [actionLoading, setActionLoading] = useState(false);
    const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
    const [tabValue, setTabValue] = useState(0);
    const [aiAnalysisResult, setAiAnalysisResult] = useState(null); // Track AI analysis result for navigation
    const [retriggering, setRetriggering] = useState(null); // Track which item is being re-triggered
    const [expandedRow, setExpandedRow] = useState(null); // Track expanded row for RAG details
    const [ragHistory, setRagHistory] = useState([]); // RAG completed history
    const [historyLoading, setHistoryLoading] = useState(false);
    const [expandedHistoryRow, setExpandedHistoryRow] = useState(null); // Track expanded history row

    // Toggle row expansion
    const toggleRowExpand = (id) => {
        setExpandedRow(expandedRow === id ? null : id);
    };

    // Get input sources from item (mock data enrichment for demo)
    const getInputSources = (item) => {
        // In production, this would come from the API
        const sources = item.input_sources || [];
        if (sources.length === 0) {
            // Default sources based on typical analysis
            return [
                { type: 'xml_report', count: 1, size: '45 KB' },
                { type: 'console_log', count: 1, size: '128 KB' },
                { type: 'stack_trace', count: item.error_category === 'CODE_ERROR' ? 3 : 1, size: '12 KB' }
            ];
        }
        return sources;
    };

    // Get matched documents from RAG (mock data enrichment for demo)
    const getMatchedDocs = (item) => {
        // In production, this would come from the API
        const docs = item.matched_docs || [];
        if (docs.length === 0) {
            // Generate mock matched docs based on category
            const categoryDocs = {
                'ENV_CONFIG': [
                    { title: 'Environment Setup Guide', similarity: 0.92, category: 'configuration' },
                    { title: 'Docker Compose Troubleshooting', similarity: 0.87, category: 'docker' }
                ],
                'NETWORK_ERROR': [
                    { title: 'Network Timeout Resolution', similarity: 0.89, category: 'network' },
                    { title: 'API Connection Issues', similarity: 0.85, category: 'api' }
                ],
                'INFRA_ERROR': [
                    { title: 'Infrastructure Health Checks', similarity: 0.91, category: 'infra' },
                    { title: 'Service Restart Procedures', similarity: 0.84, category: 'ops' }
                ],
                'DATA_ERROR': [
                    { title: 'Data Validation Patterns', similarity: 0.88, category: 'data' }
                ],
                'UNKNOWN': [
                    { title: 'General Troubleshooting Guide', similarity: 0.75, category: 'general' }
                ]
            };
            return categoryDocs[item.error_category] || categoryDocs['UNKNOWN'];
        }
        return docs;
    };

    // Re-trigger analysis for a build (resumes the flow from trigger stage)
    const handleRetrigger = async (item) => {
        setRetriggering(item.id);
        try {
            const result = await triggerAPI.triggerAnalysis({
                build_id: item.build_id,
                triggered_by_user: 'dashboard_user',
                reason: 'Re-triggered from RAG approval page'
            });
            setSnackbar({
                open: true,
                message: `Analysis re-triggered for ${item.build_id}. New item added to queue.`,
                severity: 'success'
            });
            fetchData(); // Refresh to show new item
        } catch (error) {
            setSnackbar({
                open: true,
                message: `Failed to re-trigger: ${error.message}`,
                severity: 'error'
            });
        } finally {
            setRetriggering(null);
        }
    };

    const fetchData = useCallback(async () => {
        try {
            const [pendingRes, statsRes, historyRes] = await Promise.all([
                ragApprovalAPI.getPending({ limit: 50 }),
                ragApprovalAPI.getStats(),
                ragApprovalAPI.getHistory({ limit: 50 }).catch(() => ({ history: [] }))
            ]);
            setPending(pendingRes.pending || []);
            setStats(statsRes.overall || { pending: 0, approved: 0, rejected: 0, escalated: 0 });
            // Filter history to show only non-CODE_ERROR resolved items (RAG-only resolutions)
            const history = historyRes?.history || [];
            setRagHistory(history);
        } catch (error) {
            console.error('Error fetching RAG data:', error);
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

    const openDialog = (item, action) => {
        setSelectedItem(item);
        setDialogAction(action);
        setFeedback('');
        setCorrectCategory('');
        setEscalateReason('');
        setSelectedCategory(item.error_category || 'UNKNOWN'); // Initialize with current category
        setDialogOpen(true);
    };

    const handleAction = async () => {
        if (!selectedItem) return;
        setActionLoading(true);

        try {
            let result;
            switch (dialogAction) {
                case 'approve':
                    // Include changed category if user modified it
                    const categoryChanged = selectedCategory !== selectedItem.error_category;
                    result = await ragApprovalAPI.approve({
                        approval_id: selectedItem.id,
                        reviewed_by: 'dashboard_user',
                        feedback,
                        new_category: categoryChanged ? selectedCategory : undefined
                    });
                    break;
                case 'reject':
                    result = await ragApprovalAPI.reject({
                        approval_id: selectedItem.id,
                        reviewed_by: 'dashboard_user',
                        feedback,
                        correct_category: correctCategory || undefined
                    });
                    break;
                case 'escalate':
                    result = await ragApprovalAPI.escalate({
                        approval_id: selectedItem.id,
                        reviewed_by: 'dashboard_user',
                        reason: escalateReason || 'Needs deeper AI analysis'
                    });
                    break;
                default:
                    break;
            }

            // Check if AI analysis was triggered (CODE_ERROR approval)
            if (result.ai_triggered && result.build_id) {
                // Store result for navigation prompt
                setAiAnalysisResult({
                    build_id: result.build_id,
                    ai_analysis_id: result.ai_analysis_id,
                    message: result.message
                });
                setSnackbar({
                    open: true,
                    message: `${result.message} - Click to view AI Analysis`,
                    severity: 'info'
                });
            } else {
                setSnackbar({
                    open: true,
                    message: result.message || `${dialogAction} successful`,
                    severity: 'success'
                });
            }

            setDialogOpen(false);
            fetchData();
        } catch (error) {
            setSnackbar({
                open: true,
                message: error.message || `${dialogAction} failed`,
                severity: 'error'
            });
        } finally {
            setActionLoading(false);
        }
    };

    // Navigate to AI analysis approval page
    const handleViewAIAnalysis = () => {
        if (aiAnalysisResult?.build_id) {
            navigate(`/failures/${aiAnalysisResult.build_id}`);
        }
    };

    const getCategoryColor = (category) => {
        const colors = {
            'ENV_CONFIG': '#8b5cf6',
            'NETWORK_ERROR': '#f59e0b',
            'INFRA_ERROR': '#ef4444',
            'DATA_ERROR': '#06b6d4',
            'UNKNOWN': '#6b7280'
        };
        return colors[category] || '#6b7280';
    };

    const getConfidenceColor = (confidence) => {
        const conf = parseFloat(confidence);
        if (conf >= 0.8) return '#10b981';
        if (conf >= 0.6) return '#f59e0b';
        return '#ef4444';
    };

    // Get explanation for why AI analysis is needed or not needed
    const getAIReason = (category) => {
        const reasons = {
            'CODE_ERROR': {
                title: 'Code Bug - AI Analysis Required',
                reason: 'This is a CODE_ERROR that requires AI deep analysis. Claude AI will analyze XML reports, console logs, and stack traces to identify the exact line of code causing the failure.',
                action: 'After approval, AI will find the root cause → Generate fix → Create PR → Run build → If passed, create Jira bug.',
                needsAI: true,
                flowSteps: [
                    'AI analyzes XML reports & logs',
                    'Identifies exact error line in code',
                    'Generates suggested fix',
                    'Creates Pull Request',
                    'Triggers build verification',
                    'If build passes → Creates Jira bug'
                ]
            },
            'ENV_CONFIG': {
                title: 'Environment/Configuration Issue',
                reason: 'This error is caused by environment setup or configuration problems, not code bugs. RAG matched documentation with proven solutions.',
                action: 'Apply the suggested configuration change or environment fix.',
                needsAI: false
            },
            'NETWORK_ERROR': {
                title: 'Network Connectivity Issue',
                reason: 'Network errors are typically transient or infrastructure-related. AI code analysis would not help resolve connectivity issues.',
                action: 'Check network connectivity, firewall rules, or retry the operation.',
                needsAI: false
            },
            'INFRA_ERROR': {
                title: 'Infrastructure Issue',
                reason: 'Infrastructure errors require ops/DevOps intervention, not code changes. RAG matched known infrastructure remediation steps.',
                action: 'Contact DevOps team or follow infrastructure recovery procedures.',
                needsAI: false
            },
            'DATA_ERROR': {
                title: 'Data Quality Issue',
                reason: 'Data errors are caused by invalid or corrupt data, not code logic. Fix requires data correction, not code changes.',
                action: 'Validate and correct the source data, then retry.',
                needsAI: false
            },
            'UNKNOWN': {
                title: 'Unclassified Issue',
                reason: 'Could not determine error type. Manual investigation recommended.',
                action: 'Review logs manually or escalate to AI for deeper analysis.',
                needsAI: false
            }
        };
        return reasons[category] || reasons['UNKNOWN'];
    };

    // Alias for backward compatibility
    const getNoAIReason = getAIReason;

    // Toggle history row expansion
    const toggleHistoryRowExpand = (id) => {
        setExpandedHistoryRow(expandedHistoryRow === id ? null : id);
    };

    return (
        <Box sx={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%)',
            py: 4
        }}>
            <Container maxWidth="xl">
                {/* Header */}
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
                    <Box>
                        <Typography variant="h4" fontWeight="bold" color="#1a1a2e">
                            RAG Approval Queue
                        </Typography>
                        <Typography variant="body1" color="textSecondary">
                            Human-in-the-Loop review for non-code errors identified by RAG
                        </Typography>
                    </Box>
                    <Button
                        variant="outlined"
                        startIcon={refreshing ? <CircularProgress size={18} /> : <RefreshIcon />}
                        onClick={handleRefresh}
                        disabled={refreshing}
                    >
                        Refresh
                    </Button>
                </Box>

                {/* Stats Cards */}
                <Grid container spacing={3} mb={4}>
                    <Grid item xs={12} sm={6} md={3}>
                        <StatCard
                            title="Pending Review"
                            value={stats.pending || 0}
                            icon={<PendingActionsIcon />}
                            color="#f59e0b"
                            loading={loading}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <StatCard
                            title="Approved"
                            value={stats.approved || 0}
                            icon={<CheckCircleIcon />}
                            color="#10b981"
                            loading={loading}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <StatCard
                            title="Rejected"
                            value={stats.rejected || 0}
                            icon={<CancelIcon />}
                            color="#ef4444"
                            loading={loading}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <StatCard
                            title="Escalated to AI"
                            value={stats.escalated || 0}
                            icon={<SmartToyIcon />}
                            color="#3b82f6"
                            loading={loading}
                        />
                    </Grid>
                </Grid>

                {/* Pending Queue Table */}
                <Paper elevation={0} sx={{
                    borderRadius: 3,
                    background: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(10px)',
                    overflow: 'hidden'
                }}>
                    <Box sx={{ p: 3, borderBottom: '1px solid #e5e7eb' }}>
                        <Typography variant="h6" fontWeight={600}>
                            <Badge badgeContent={stats.pending || 0} color="warning" sx={{ mr: 2 }}>
                                <PendingActionsIcon color="action" />
                            </Badge>
                            Pending Approvals
                        </Typography>
                    </Box>

                    {loading ? (
                        <Box display="flex" justifyContent="center" p={4}>
                            <CircularProgress />
                        </Box>
                    ) : pending.length === 0 ? (
                        <Box p={4} textAlign="center">
                            <CheckCircleIcon sx={{ fontSize: 48, color: '#10b981', mb: 2 }} />
                            <Typography variant="h6" color="textSecondary">
                                All caught up! No pending approvals.
                            </Typography>
                        </Box>
                    ) : (
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow sx={{ bgcolor: '#f8fafc' }}>
                                        <TableCell sx={{ fontWeight: 600, width: 40 }}></TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Build ID</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Category</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Inputs Analyzed</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>RAG Suggestion</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Confidence</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Waiting</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }} align="center">Actions</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {pending.map((item) => {
                                        const inputSources = getInputSources(item);
                                        const matchedDocs = getMatchedDocs(item);
                                        const totalInputs = inputSources.reduce((sum, s) => sum + (s.count || 1), 0);

                                        return (
                                        <React.Fragment key={item.id}>
                                            <TableRow
                                                hover
                                                onClick={() => toggleRowExpand(item.id)}
                                                sx={{
                                                    cursor: 'pointer',
                                                    bgcolor: expandedRow === item.id ? '#f8fafc' : 'inherit',
                                                    '&:hover': { bgcolor: '#f1f5f9' }
                                                }}
                                            >
                                                <TableCell>
                                                    <IconButton size="small">
                                                        {expandedRow === item.id ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                                    </IconButton>
                                                </TableCell>
                                                <TableCell>
                                                    <Typography fontWeight={500}>{item.build_id}</Typography>
                                                    <Typography variant="caption" color="textSecondary">
                                                        {item.job_name}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell>
                                                    <Chip
                                                        label={item.error_category}
                                                        size="small"
                                                        sx={{
                                                            bgcolor: alpha(getCategoryColor(item.error_category), 0.1),
                                                            color: getCategoryColor(item.error_category),
                                                            fontWeight: 500
                                                        }}
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    <Box display="flex" alignItems="center" gap={0.5} flexWrap="wrap">
                                                        {inputSources.slice(0, 3).map((source, idx) => {
                                                            const config = INPUT_SOURCE_CONFIG[source.type] || { icon: <DescriptionIcon sx={{ fontSize: 16 }} />, label: source.type, color: '#64748b' };
                                                            return (
                                                                <Tooltip key={idx} title={`${config.label}: ${source.count || 1} file(s)`}>
                                                                    <Chip
                                                                        icon={config.icon}
                                                                        label={source.count || 1}
                                                                        size="small"
                                                                        sx={{
                                                                            bgcolor: alpha(config.color, 0.1),
                                                                            color: config.color,
                                                                            '& .MuiChip-icon': { color: config.color },
                                                                            fontSize: '0.7rem',
                                                                            height: 24
                                                                        }}
                                                                    />
                                                                </Tooltip>
                                                            );
                                                        })}
                                                        <Typography variant="caption" color="textSecondary" sx={{ ml: 0.5 }}>
                                                            {totalInputs} total
                                                        </Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell sx={{ maxWidth: 250 }}>
                                                    <Tooltip title={item.rag_suggestion}>
                                                        <Typography noWrap sx={{ fontSize: '0.875rem' }}>
                                                            {item.rag_suggestion}
                                                        </Typography>
                                                    </Tooltip>
                                                    <Box display="flex" alignItems="center" gap={0.5}>
                                                        <FindInPageIcon sx={{ fontSize: 12, color: '#64748b' }} />
                                                        <Typography variant="caption" color="textSecondary">
                                                            {matchedDocs.length} docs matched | {item.similar_cases_count || 0} similar cases
                                                        </Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Box display="flex" alignItems="center" gap={1}>
                                                        <CircularProgress
                                                            variant="determinate"
                                                            value={parseFloat(item.rag_confidence) * 100}
                                                            size={32}
                                                            sx={{ color: getConfidenceColor(item.rag_confidence) }}
                                                        />
                                                        <Typography fontWeight={500} color={getConfidenceColor(item.rag_confidence)}>
                                                            {Math.round(parseFloat(item.rag_confidence) * 100)}%
                                                        </Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Box display="flex" alignItems="center" gap={0.5}>
                                                        <AccessTimeIcon fontSize="small" color="action" />
                                                        <Typography variant="body2">
                                                            {item.hours_waiting < 1
                                                                ? `${Math.round(item.hours_waiting * 60)}m`
                                                                : `${Math.round(item.hours_waiting)}h`}
                                                        </Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell align="center">
                                                    <Box display="flex" gap={0.5} justifyContent="center">
                                                        <Tooltip title="Approve - Accept RAG suggestion (CODE_ERROR triggers AI analysis)">
                                                            <IconButton
                                                                color="success"
                                                                size="small"
                                                                onClick={(e) => { e.stopPropagation(); openDialog(item, 'approve'); }}
                                                            >
                                                                <ThumbUpIcon fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>
                                                        <Tooltip title="Reject - RAG suggestion is incorrect">
                                                            <IconButton
                                                                color="error"
                                                                size="small"
                                                                onClick={(e) => { e.stopPropagation(); openDialog(item, 'reject'); }}
                                                            >
                                                                <ThumbDownIcon fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>
                                                        <Tooltip title="Escalate - Force AI deep analysis regardless of category">
                                                            <IconButton
                                                                color="primary"
                                                                size="small"
                                                                onClick={(e) => { e.stopPropagation(); openDialog(item, 'escalate'); }}
                                                            >
                                                                <SmartToyIcon fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>
                                                        <Tooltip title="Re-trigger - Start fresh analysis from beginning">
                                                            <IconButton
                                                                color="secondary"
                                                                size="small"
                                                                onClick={(e) => { e.stopPropagation(); handleRetrigger(item); }}
                                                                disabled={retriggering === item.id}
                                                            >
                                                                {retriggering === item.id ? (
                                                                    <CircularProgress size={18} />
                                                                ) : (
                                                                    <ReplayIcon fontSize="small" />
                                                                )}
                                                            </IconButton>
                                                        </Tooltip>
                                                    </Box>
                                                </TableCell>
                                            </TableRow>

                                            {/* Expanded Row - RAG Analysis Details */}
                                            <TableRow>
                                                <TableCell colSpan={8} sx={{ py: 0, borderBottom: expandedRow === item.id ? undefined : 'none' }}>
                                                    <Collapse in={expandedRow === item.id} timeout="auto" unmountOnExit>
                                                        <Box sx={{ py: 3, px: 2, bgcolor: '#f8fafc' }}>
                                                            <Grid container spacing={3}>
                                                                {/* Input Sources Analyzed */}
                                                                <Grid item xs={12} md={4}>
                                                                    <Paper sx={{ p: 2, borderRadius: 2, height: '100%' }}>
                                                                        <Box display="flex" alignItems="center" gap={1} mb={2}>
                                                                            <Avatar sx={{ bgcolor: '#3b82f6', width: 32, height: 32 }}>
                                                                                <SourceIcon sx={{ fontSize: 18 }} />
                                                                            </Avatar>
                                                                            <Typography variant="subtitle2" fontWeight={600}>
                                                                                Input Sources Analyzed
                                                                            </Typography>
                                                                        </Box>
                                                                        {inputSources.map((source, idx) => {
                                                                            const config = INPUT_SOURCE_CONFIG[source.type] || { icon: <DescriptionIcon />, label: source.type, color: '#64748b' };
                                                                            return (
                                                                                <Box key={idx} display="flex" alignItems="center" justifyContent="space-between" mb={1} p={1} bgcolor="#f1f5f9" borderRadius={1}>
                                                                                    <Box display="flex" alignItems="center" gap={1}>
                                                                                        <Box sx={{ color: config.color }}>{config.icon}</Box>
                                                                                        <Typography variant="body2">{config.label}</Typography>
                                                                                    </Box>
                                                                                    <Box display="flex" alignItems="center" gap={1}>
                                                                                        <Chip label={`${source.count || 1} file(s)`} size="small" sx={{ height: 20, fontSize: '0.7rem' }} />
                                                                                        <Typography variant="caption" color="textSecondary">{source.size || '-'}</Typography>
                                                                                    </Box>
                                                                                </Box>
                                                                            );
                                                                        })}
                                                                        <Divider sx={{ my: 1.5 }} />
                                                                        <Box display="flex" justifyContent="space-between">
                                                                            <Typography variant="body2" color="textSecondary">Total Inputs:</Typography>
                                                                            <Typography variant="body2" fontWeight={600}>{totalInputs}</Typography>
                                                                        </Box>
                                                                    </Paper>
                                                                </Grid>

                                                                {/* RAG Matched Documents */}
                                                                <Grid item xs={12} md={4}>
                                                                    <Paper sx={{ p: 2, borderRadius: 2, height: '100%' }}>
                                                                        <Box display="flex" alignItems="center" gap={1} mb={2}>
                                                                            <Avatar sx={{ bgcolor: '#10b981', width: 32, height: 32 }}>
                                                                                <FindInPageIcon sx={{ fontSize: 18 }} />
                                                                            </Avatar>
                                                                            <Typography variant="subtitle2" fontWeight={600}>
                                                                                RAG Matched Documents
                                                                            </Typography>
                                                                        </Box>
                                                                        {matchedDocs.map((doc, idx) => (
                                                                            <Box key={idx} mb={1} p={1.5} bgcolor="#f0fdf4" borderRadius={1} border="1px solid #bbf7d0">
                                                                                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                                                                                    <Typography variant="body2" fontWeight={500} sx={{ flex: 1 }}>
                                                                                        {doc.title}
                                                                                    </Typography>
                                                                                    <Chip
                                                                                        label={`${Math.round(doc.similarity * 100)}%`}
                                                                                        size="small"
                                                                                        sx={{
                                                                                            bgcolor: doc.similarity >= 0.9 ? '#dcfce7' : doc.similarity >= 0.8 ? '#fef3c7' : '#fee2e2',
                                                                                            color: doc.similarity >= 0.9 ? '#166534' : doc.similarity >= 0.8 ? '#92400e' : '#991b1b',
                                                                                            height: 20,
                                                                                            fontSize: '0.7rem'
                                                                                        }}
                                                                                    />
                                                                                </Box>
                                                                                <Chip label={doc.category} size="small" sx={{ mt: 0.5, height: 18, fontSize: '0.65rem', bgcolor: '#e2e8f0' }} />
                                                                            </Box>
                                                                        ))}
                                                                    </Paper>
                                                                </Grid>

                                                                {/* RAG Analysis Summary */}
                                                                <Grid item xs={12} md={4}>
                                                                    <Paper sx={{ p: 2, borderRadius: 2, height: '100%' }}>
                                                                        <Box display="flex" alignItems="center" gap={1} mb={2}>
                                                                            <Avatar sx={{ bgcolor: '#8b5cf6', width: 32, height: 32 }}>
                                                                                <AutoFixHighIcon sx={{ fontSize: 18 }} />
                                                                            </Avatar>
                                                                            <Typography variant="subtitle2" fontWeight={600}>
                                                                                RAG Analysis Summary
                                                                            </Typography>
                                                                        </Box>
                                                                        <Box mb={2}>
                                                                            <Typography variant="caption" color="textSecondary">Identified Error Type:</Typography>
                                                                            <Chip
                                                                                label={item.error_category}
                                                                                sx={{
                                                                                    mt: 0.5,
                                                                                    display: 'block',
                                                                                    bgcolor: alpha(getCategoryColor(item.error_category), 0.15),
                                                                                    color: getCategoryColor(item.error_category),
                                                                                    fontWeight: 600
                                                                                }}
                                                                            />
                                                                        </Box>
                                                                        <Box mb={2}>
                                                                            <Typography variant="caption" color="textSecondary">RAG Suggestion:</Typography>
                                                                            <Typography variant="body2" sx={{ mt: 0.5, p: 1, bgcolor: '#f1f5f9', borderRadius: 1, fontSize: '0.8rem' }}>
                                                                                {item.rag_suggestion}
                                                                            </Typography>
                                                                        </Box>
                                                                        <Box display="flex" justifyContent="space-between" mb={1}>
                                                                            <Typography variant="body2" color="textSecondary">Confidence:</Typography>
                                                                            <Box display="flex" alignItems="center" gap={0.5}>
                                                                                <Box sx={{ width: 60, height: 6, bgcolor: '#e2e8f0', borderRadius: 3, overflow: 'hidden' }}>
                                                                                    <Box sx={{ width: `${parseFloat(item.rag_confidence) * 100}%`, height: '100%', bgcolor: getConfidenceColor(item.rag_confidence), borderRadius: 3 }} />
                                                                                </Box>
                                                                                <Typography variant="body2" fontWeight={600} color={getConfidenceColor(item.rag_confidence)}>
                                                                                    {Math.round(parseFloat(item.rag_confidence) * 100)}%
                                                                                </Typography>
                                                                            </Box>
                                                                        </Box>
                                                                        <Box display="flex" justifyContent="space-between">
                                                                            <Typography variant="body2" color="textSecondary">Similar Cases:</Typography>
                                                                            <Typography variant="body2" fontWeight={600}>{item.similar_cases_count || 0}</Typography>
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
                                    })}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    )}
                </Paper>

                {/* RAG Completed History - Shows resolved items with document matches */}
                <Paper elevation={0} sx={{
                    borderRadius: 3,
                    background: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(10px)',
                    overflow: 'hidden',
                    mt: 3
                }}>
                    <Box sx={{ p: 3, borderBottom: '1px solid #e5e7eb', bgcolor: '#f0fdf4' }}>
                        <Box display="flex" alignItems="center" gap={2}>
                            <Avatar sx={{ bgcolor: '#10b981', width: 40, height: 40 }}>
                                <CheckCircleIcon />
                            </Avatar>
                            <Box>
                                <Typography variant="h6" fontWeight={600} color="#166534">
                                    RAG Resolved History
                                </Typography>
                                <Typography variant="body2" color="textSecondary">
                                    Items resolved by RAG without AI code analysis - click rows to see why
                                </Typography>
                            </Box>
                        </Box>
                    </Box>

                    {ragHistory.length === 0 ? (
                        <Box p={4} textAlign="center">
                            <Typography variant="body1" color="textSecondary">
                                No resolved items yet. Approve pending items to see them here.
                            </Typography>
                        </Box>
                    ) : (
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow sx={{ bgcolor: '#f8fafc' }}>
                                        <TableCell sx={{ fontWeight: 600, width: 40 }}></TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Build #</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Error Category</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Matched Documents</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>RAG Suggestion</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Why No AI Analysis</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>Resolved</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {ragHistory.map((item) => {
                                        const noAIReason = getNoAIReason(item.error_category);
                                        const matchedDocs = getMatchedDocs(item);
                                        const isExpanded = expandedHistoryRow === item.id;
                                        const isCodeError = item.error_category === 'CODE_ERROR';

                                        return (
                                            <React.Fragment key={item.id}>
                                                <TableRow
                                                    hover
                                                    onClick={() => toggleHistoryRowExpand(item.id)}
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
                                                        <Typography variant="caption" color="textSecondary">
                                                            {item.job_name || '-'}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip
                                                            label={item.error_category || 'UNKNOWN'}
                                                            size="small"
                                                            sx={{
                                                                bgcolor: alpha(getCategoryColor(item.error_category), 0.1),
                                                                color: getCategoryColor(item.error_category),
                                                                fontWeight: 600
                                                            }}
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        <Box display="flex" alignItems="center" gap={0.5}>
                                                            <FindInPageIcon sx={{ fontSize: 16, color: '#10b981' }} />
                                                            <Typography variant="body2">
                                                                {matchedDocs.length} docs matched
                                                            </Typography>
                                                        </Box>
                                                    </TableCell>
                                                    <TableCell sx={{ maxWidth: 200 }}>
                                                        <Tooltip title={item.rag_suggestion || '-'}>
                                                            <Typography noWrap variant="body2">
                                                                {item.rag_suggestion || '-'}
                                                            </Typography>
                                                        </Tooltip>
                                                    </TableCell>
                                                    <TableCell>
                                                        {isCodeError ? (
                                                            <Chip
                                                                icon={<SmartToyIcon />}
                                                                label="AI Analyzed"
                                                                size="small"
                                                                sx={{ bgcolor: '#dbeafe', color: '#1e40af', '& .MuiChip-icon': { color: 'inherit', fontSize: 14 } }}
                                                            />
                                                        ) : (
                                                            <Tooltip title={noAIReason.reason}>
                                                                <Chip
                                                                    label={noAIReason.title}
                                                                    size="small"
                                                                    sx={{ bgcolor: '#dcfce7', color: '#166534', fontSize: '0.7rem' }}
                                                                />
                                                            </Tooltip>
                                                        )}
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip
                                                            icon={item.review_status === 'approved' ? <CheckCircleIcon /> :
                                                                  item.review_status === 'rejected' ? <CancelIcon /> : <SmartToyIcon />}
                                                            label={(item.review_status || 'pending').charAt(0).toUpperCase() + (item.review_status || 'pending').slice(1)}
                                                            size="small"
                                                            sx={{
                                                                bgcolor: item.review_status === 'approved' ? '#dcfce7' :
                                                                         item.review_status === 'rejected' ? '#fee2e2' : '#fef3c7',
                                                                color: item.review_status === 'approved' ? '#166534' :
                                                                       item.review_status === 'rejected' ? '#991b1b' : '#92400e',
                                                                '& .MuiChip-icon': { color: 'inherit', fontSize: 14 }
                                                            }}
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="caption" color="textSecondary">
                                                            {item.reviewed_at ? new Date(item.reviewed_at).toLocaleString() : '-'}
                                                        </Typography>
                                                    </TableCell>
                                                </TableRow>

                                                {/* Expanded Details Row */}
                                                <TableRow>
                                                    <TableCell colSpan={8} sx={{ py: 0, borderBottom: isExpanded ? undefined : 'none' }}>
                                                        <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                                                            <Box sx={{ py: 3, px: 2, bgcolor: '#f8fafc' }}>
                                                                <Grid container spacing={3}>
                                                                    {/* Why AI Analysis Needed (CODE_ERROR) or Why NOT Needed (other categories) */}
                                                                    <Grid item xs={12} md={4}>
                                                                        <Paper sx={{
                                                                            p: 2,
                                                                            borderRadius: 2,
                                                                            bgcolor: isCodeError ? '#eff6ff' : '#f0fdf4',
                                                                            border: isCodeError ? '1px solid #bfdbfe' : '1px solid #bbf7d0',
                                                                            height: '100%'
                                                                        }}>
                                                                            <Box display="flex" alignItems="center" gap={1} mb={2}>
                                                                                <Avatar sx={{ bgcolor: isCodeError ? '#3b82f6' : '#10b981', width: 32, height: 32 }}>
                                                                                    {isCodeError ? <SmartToyIcon sx={{ fontSize: 18 }} /> : <TipsAndUpdatesIcon sx={{ fontSize: 18 }} />}
                                                                                </Avatar>
                                                                                <Typography variant="subtitle2" fontWeight={600} color={isCodeError ? '#1e40af' : '#166534'}>
                                                                                    {isCodeError ? 'Why AI Analysis Needed' : 'Why No AI Analysis Needed'}
                                                                                </Typography>
                                                                            </Box>
                                                                            <Typography variant="body2" sx={{ mb: 2 }}>
                                                                                {noAIReason.reason}
                                                                            </Typography>

                                                                            {/* Show flow steps for CODE_ERROR */}
                                                                            {isCodeError && noAIReason.flowSteps && (
                                                                                <Box sx={{ mb: 2 }}>
                                                                                    <Typography variant="caption" color="textSecondary" fontWeight={600}>AI Pipeline Flow:</Typography>
                                                                                    {noAIReason.flowSteps.map((step, idx) => (
                                                                                        <Box key={idx} display="flex" alignItems="center" gap={1} mt={0.5}>
                                                                                            <Chip
                                                                                                label={idx + 1}
                                                                                                size="small"
                                                                                                sx={{
                                                                                                    width: 20,
                                                                                                    height: 20,
                                                                                                    fontSize: '0.65rem',
                                                                                                    bgcolor: '#3b82f6',
                                                                                                    color: 'white'
                                                                                                }}
                                                                                            />
                                                                                            <Typography variant="caption">{step}</Typography>
                                                                                        </Box>
                                                                                    ))}
                                                                                </Box>
                                                                            )}

                                                                            <Divider sx={{ my: 1.5 }} />
                                                                            <Typography variant="caption" color="textSecondary">
                                                                                {isCodeError ? 'Next Step:' : 'Recommended Action:'}
                                                                            </Typography>
                                                                            <Typography variant="body2" fontWeight={500} color={isCodeError ? '#1e40af' : '#166534'}>
                                                                                {noAIReason.action}
                                                                            </Typography>
                                                                        </Paper>
                                                                    </Grid>

                                                                    {/* Matched Documents */}
                                                                    <Grid item xs={12} md={4}>
                                                                        <Paper sx={{ p: 2, borderRadius: 2, height: '100%' }}>
                                                                            <Box display="flex" alignItems="center" gap={1} mb={2}>
                                                                                <Avatar sx={{ bgcolor: '#10b981', width: 32, height: 32 }}>
                                                                                    <FindInPageIcon sx={{ fontSize: 18 }} />
                                                                                </Avatar>
                                                                                <Typography variant="subtitle2" fontWeight={600}>
                                                                                    RAG Matched Documents
                                                                                </Typography>
                                                                            </Box>
                                                                            {matchedDocs.map((doc, idx) => (
                                                                                <Box key={idx} mb={1} p={1.5} bgcolor="#f1f5f9" borderRadius={1}>
                                                                                    <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                                                                                        <Typography variant="body2" fontWeight={500}>
                                                                                            {doc.title}
                                                                                        </Typography>
                                                                                        <Chip
                                                                                            label={`${Math.round(doc.similarity * 100)}% match`}
                                                                                            size="small"
                                                                                            sx={{
                                                                                                bgcolor: doc.similarity >= 0.9 ? '#dcfce7' : doc.similarity >= 0.8 ? '#fef3c7' : '#fee2e2',
                                                                                                color: doc.similarity >= 0.9 ? '#166534' : doc.similarity >= 0.8 ? '#92400e' : '#991b1b',
                                                                                                height: 20,
                                                                                                fontSize: '0.65rem'
                                                                                            }}
                                                                                        />
                                                                                    </Box>
                                                                                    <Chip label={doc.category} size="small" sx={{ mt: 0.5, height: 18, fontSize: '0.6rem', bgcolor: '#e2e8f0' }} />
                                                                                </Box>
                                                                            ))}
                                                                        </Paper>
                                                                    </Grid>

                                                                    {/* RAG Resolution Details */}
                                                                    <Grid item xs={12} md={4}>
                                                                        <Paper sx={{ p: 2, borderRadius: 2, height: '100%' }}>
                                                                            <Box display="flex" alignItems="center" gap={1} mb={2}>
                                                                                <Avatar sx={{ bgcolor: '#8b5cf6', width: 32, height: 32 }}>
                                                                                    <AutoFixHighIcon sx={{ fontSize: 18 }} />
                                                                                </Avatar>
                                                                                <Typography variant="subtitle2" fontWeight={600}>
                                                                                    Resolution Details
                                                                                </Typography>
                                                                            </Box>
                                                                            <Box mb={1.5}>
                                                                                <Typography variant="caption" color="textSecondary">RAG Suggestion:</Typography>
                                                                                <Typography variant="body2" sx={{ p: 1, bgcolor: '#f1f5f9', borderRadius: 1, mt: 0.5 }}>
                                                                                    {item.rag_suggestion || 'No suggestion provided'}
                                                                                </Typography>
                                                                            </Box>
                                                                            <Box mb={1.5}>
                                                                                <Typography variant="caption" color="textSecondary">Confidence Score:</Typography>
                                                                                <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                                                                                    <Box sx={{ flex: 1, height: 8, bgcolor: '#e2e8f0', borderRadius: 4, overflow: 'hidden' }}>
                                                                                        <Box sx={{ width: `${(item.rag_confidence || 0) * 100}%`, height: '100%', bgcolor: getConfidenceColor(item.rag_confidence), borderRadius: 4 }} />
                                                                                    </Box>
                                                                                    <Typography variant="body2" fontWeight={600}>
                                                                                        {Math.round((item.rag_confidence || 0) * 100)}%
                                                                                    </Typography>
                                                                                </Box>
                                                                            </Box>
                                                                            <Box>
                                                                                <Typography variant="caption" color="textSecondary">Reviewed By:</Typography>
                                                                                <Typography variant="body2" fontWeight={500}>{item.reviewed_by || 'System'}</Typography>
                                                                            </Box>
                                                                            {item.review_feedback && (
                                                                                <Box mt={1.5}>
                                                                                    <Typography variant="caption" color="textSecondary">Reviewer Feedback:</Typography>
                                                                                    <Typography variant="body2" sx={{ p: 1, bgcolor: '#fef3c7', borderRadius: 1, mt: 0.5 }}>
                                                                                        {item.review_feedback}
                                                                                    </Typography>
                                                                                </Box>
                                                                            )}
                                                                        </Paper>
                                                                    </Grid>
                                                                </Grid>
                                                            </Box>
                                                        </Collapse>
                                                    </TableCell>
                                                </TableRow>
                                            </React.Fragment>
                                        );
                                    })}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    )}
                </Paper>

                {/* Action Dialog */}
                <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
                    <DialogTitle sx={{ bgcolor: dialogAction === 'approve' ? '#dcfce7' : dialogAction === 'reject' ? '#fee2e2' : '#dbeafe' }}>
                        {dialogAction === 'approve' && '✅ Approve & Resume Flow'}
                        {dialogAction === 'reject' && '❌ Reject & Stop Flow'}
                        {dialogAction === 'escalate' && '🤖 Force AI Deep Analysis'}
                    </DialogTitle>
                    <DialogContent>
                        {selectedItem && (
                            <Box sx={{ mb: 3, p: 2, bgcolor: '#f8fafc', borderRadius: 2 }}>
                                <Typography variant="subtitle2" color="textSecondary">Build</Typography>
                                <Typography fontWeight={500}>{selectedItem.build_id}</Typography>
                                <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 1 }}>Category</Typography>
                                <Chip label={selectedItem.error_category} size="small" sx={{ mt: 0.5 }} />
                                <Typography variant="subtitle2" color="textSecondary" sx={{ mt: 1 }}>RAG Suggestion</Typography>
                                <Typography variant="body2">{selectedItem.rag_suggestion}</Typography>
                            </Box>
                        )}

                        {dialogAction === 'approve' && (
                            <>
                                {/* Category Selector */}
                                <FormControl fullWidth sx={{ mb: 2 }}>
                                    <InputLabel>Error Category</InputLabel>
                                    <Select
                                        value={selectedCategory}
                                        label="Error Category"
                                        onChange={(e) => setSelectedCategory(e.target.value)}
                                    >
                                        {ERROR_CATEGORIES.map((cat) => (
                                            <MenuItem key={cat} value={cat}>
                                                {cat}
                                                {cat === 'CODE_ERROR' && ' (→ AI Analysis)'}
                                                {cat !== 'CODE_ERROR' && ' (→ Resolved)'}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>

                                {/* Flow Explanation */}
                                <Alert
                                    severity={selectedCategory === 'CODE_ERROR' ? 'info' : 'success'}
                                    sx={{ mb: 2 }}
                                >
                                    {selectedCategory === 'CODE_ERROR' ? (
                                        <Typography variant="body2">
                                            <strong>Resume Pipeline:</strong> AI will analyze XML reports, logs, and code to find the exact error line.
                                        </Typography>
                                    ) : (
                                        <Typography variant="body2">
                                            <strong>Mark Resolved:</strong> RAG suggestion accepted. Flow will be marked as complete (no AI analysis needed).
                                        </Typography>
                                    )}
                                </Alert>

                                {selectedCategory !== selectedItem?.error_category && (
                                    <Alert severity="warning" sx={{ mb: 2 }}>
                                        <Typography variant="body2">
                                            Category changed from <strong>{selectedItem?.error_category}</strong> to <strong>{selectedCategory}</strong>
                                        </Typography>
                                    </Alert>
                                )}

                                <TextField
                                    fullWidth
                                    label="Feedback (optional)"
                                    placeholder="e.g., Confirmed - this fixed the issue"
                                    value={feedback}
                                    onChange={(e) => setFeedback(e.target.value)}
                                    multiline
                                    rows={2}
                                />
                            </>
                        )}

                        {dialogAction === 'reject' && (
                            <>
                                <TextField
                                    fullWidth
                                    label="Why is this incorrect?"
                                    placeholder="e.g., This was actually a code error, not config"
                                    value={feedback}
                                    onChange={(e) => setFeedback(e.target.value)}
                                    multiline
                                    rows={2}
                                    sx={{ mb: 2 }}
                                />
                                <TextField
                                    fullWidth
                                    label="Correct Category (optional)"
                                    placeholder="e.g., CODE_ERROR"
                                    value={correctCategory}
                                    onChange={(e) => setCorrectCategory(e.target.value)}
                                />
                            </>
                        )}

                        {dialogAction === 'escalate' && (
                            <TextField
                                fullWidth
                                label="Reason for escalation"
                                placeholder="e.g., Low confidence, needs deeper code analysis"
                                value={escalateReason}
                                onChange={(e) => setEscalateReason(e.target.value)}
                                multiline
                                rows={2}
                            />
                        )}
                    </DialogContent>
                    <DialogActions sx={{ p: 2 }}>
                        <Button onClick={() => setDialogOpen(false)} disabled={actionLoading}>
                            Cancel
                        </Button>
                        <Button
                            variant="contained"
                            onClick={handleAction}
                            disabled={actionLoading}
                            color={dialogAction === 'approve' ? 'success' : dialogAction === 'reject' ? 'error' : 'primary'}
                            startIcon={actionLoading ? <CircularProgress size={18} /> : <SendIcon />}
                        >
                            {dialogAction === 'approve' && (selectedCategory === 'CODE_ERROR' ? 'Resume → AI Analysis' : 'Approve → Resolved')}
                            {dialogAction === 'reject' && 'Stop Flow'}
                            {dialogAction === 'escalate' && 'Force AI Analysis'}
                        </Button>
                    </DialogActions>
                </Dialog>

                {/* Snackbar */}
                <Snackbar
                    open={snackbar.open}
                    autoHideDuration={aiAnalysisResult ? 10000 : 4000}
                    onClose={() => {
                        setSnackbar({ ...snackbar, open: false });
                        if (!snackbar.open) setAiAnalysisResult(null);
                    }}
                >
                    <Alert
                        severity={snackbar.severity}
                        onClose={() => setSnackbar({ ...snackbar, open: false })}
                        action={
                            aiAnalysisResult ? (
                                <Button
                                    color="inherit"
                                    size="small"
                                    onClick={handleViewAIAnalysis}
                                    startIcon={<OpenInNewIcon />}
                                >
                                    View Analysis
                                </Button>
                            ) : null
                        }
                    >
                        {snackbar.message}
                    </Alert>
                </Snackbar>

                {/* AI Analysis Navigation Dialog - shown when CODE_ERROR triggers AI */}
                <Dialog
                    open={!!aiAnalysisResult}
                    onClose={() => setAiAnalysisResult(null)}
                    maxWidth="sm"
                    fullWidth
                >
                    <DialogTitle sx={{ bgcolor: '#3b82f6', color: 'white' }}>
                        🤖 AI Analysis Triggered
                    </DialogTitle>
                    <DialogContent sx={{ pt: 3 }}>
                        <Alert severity="info" sx={{ mb: 2 }}>
                            <Typography variant="subtitle2">
                                CODE_ERROR detected - AI is analyzing XML reports, console logs, and code to find the exact error location.
                            </Typography>
                        </Alert>
                        <Box sx={{ p: 2, bgcolor: '#f8fafc', borderRadius: 2 }}>
                            <Typography variant="body2" color="textSecondary">Build ID</Typography>
                            <Typography fontWeight={600}>{aiAnalysisResult?.build_id}</Typography>
                            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>Analysis ID</Typography>
                            <Typography fontWeight={600}>{aiAnalysisResult?.ai_analysis_id}</Typography>
                        </Box>
                    </DialogContent>
                    <DialogActions sx={{ p: 2, gap: 1 }}>
                        <Button onClick={() => setAiAnalysisResult(null)}>
                            Stay Here
                        </Button>
                        <Button
                            variant="contained"
                            onClick={handleViewAIAnalysis}
                            startIcon={<OpenInNewIcon />}
                        >
                            Go to AI Analysis Approval
                        </Button>
                    </DialogActions>
                </Dialog>
            </Container>
        </Box>
    );
};

export default RAGApprovalPreview;
