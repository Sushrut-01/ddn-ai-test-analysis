import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import {
    Box, Container, Paper, Typography, Grid, Button, Chip, Avatar, IconButton,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    LinearProgress, Card, CardContent, Stepper, Step, StepLabel, StepContent,
    Alert, Tooltip, CircularProgress, Collapse, Divider, Dialog, DialogTitle,
    DialogContent, DialogActions, Tabs, Tab, TextField, InputAdornment,
    List, ListItem, ListItemText, ListItemIcon, Badge
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import { useColorTheme } from '../theme/ThemeContext';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ScheduleIcon from '@mui/icons-material/Schedule';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import DoneAllIcon from '@mui/icons-material/DoneAll';
import TriggerIcon from '@mui/icons-material/NotStarted';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import CancelIcon from '@mui/icons-material/Cancel';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import BoltIcon from '@mui/icons-material/Bolt';
import MemoryIcon from '@mui/icons-material/Memory';
import TerminalIcon from '@mui/icons-material/Terminal';
import DownloadIcon from '@mui/icons-material/Download';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import SearchIcon from '@mui/icons-material/Search';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import StorageIcon from '@mui/icons-material/Storage';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import VisibilityIcon from '@mui/icons-material/Visibility';
import FilterListIcon from '@mui/icons-material/FilterList';
import DataObjectIcon from '@mui/icons-material/DataObject';
import { pipelineAPI, monitoringAPI, triggerAPI, ragApprovalAPI } from '../services/api';
import ReplayIcon from '@mui/icons-material/Replay';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import InputLabel from '@mui/material/InputLabel';

// Pipeline Stages Definition - Updated for RAG Approval Flow
const pipelineStages = [
    { id: 'trigger', label: 'Trigger Received', icon: <TriggerIcon />, description: 'Analysis request from manual trigger, cron job, or aging service' },
    { id: 'classify', label: 'Error Classification', icon: <SmartToyIcon />, description: 'LangGraph classifies error type (CODE_ERROR, ENV_CONFIG, NETWORK, INFRA)' },
    { id: 'rag_queue', label: 'RAG Queue', icon: <HourglassEmptyIcon />, description: 'Added to RAG approval queue with preliminary suggestion' },
    { id: 'human_review', label: 'Human Review (HITL)', icon: <FactCheckIcon />, description: 'Human approves/rejects RAG suggestion on approval page' },
    { id: 'ai_analysis', label: 'AI Deep Analysis', icon: <AutoFixHighIcon />, description: 'CODE_ERROR only: Claude analyzes XML, logs to find exact error line' },
    { id: 'complete', label: 'Complete', icon: <DoneAllIcon />, description: 'Analysis complete - ready for fix application or marked resolved' },
];

const getStageIndex = (stageId) => pipelineStages.findIndex(s => s.id === stageId);

const formatDuration = (ms) => {
    if (!ms) return '-';
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
};

const StageStatusIcon = ({ status }) => {
    switch (status) {
        case 'completed':
            return <CheckCircleIcon sx={{ color: '#10b981', fontSize: 20 }} />;
        case 'in_progress':
            return <CircularProgress size={18} sx={{ color: '#3b82f6' }} />;
        case 'failed':
            return <ErrorIcon sx={{ color: '#ef4444', fontSize: 20 }} />;
        default:
            return <HourglassEmptyIcon sx={{ color: '#94a3b8', fontSize: 20 }} />;
    }
};

const LogLevelChip = ({ level }) => {
    const config = {
        'INFO': { bg: '#dbeafe', color: '#1e40af' },
        'DEBUG': { bg: '#f1f5f9', color: '#64748b' },
        'WARNING': { bg: '#fef3c7', color: '#92400e' },
        'ERROR': { bg: '#fee2e2', color: '#991b1b' },
    };
    const { bg, color } = config[level] || config.INFO;
    return <Chip label={level} size="small" sx={{ bgcolor: bg, color, fontSize: '0.65rem', height: 20, minWidth: 60 }} />;
};

const PipelineStatusPreview = () => {
    const { theme } = useColorTheme();
    const [activeJobs, setActiveJobs] = useState([]);
    const [completedJobs, setCompletedJobs] = useState([]);
    const [expandedJob, setExpandedJob] = useState(null);
    const [refreshing, setRefreshing] = useState(false);
    const [logDialogOpen, setLogDialogOpen] = useState(false);
    const [selectedJobForLog, setSelectedJobForLog] = useState(null);
    const [logFilter, setLogFilter] = useState('all');
    const [logSearch, setLogSearch] = useState('');
    const [logTab, setLogTab] = useState(0);
    const [loading, setLoading] = useState(true);
    const [pipelineData, setPipelineData] = useState(null);
    const [error, setError] = useState(null);
    const [jobLogs, setJobLogs] = useState({});
    const [statusFilter, setStatusFilter] = useState('all');
    const [restartDialogOpen, setRestartDialogOpen] = useState(false);
    const [jobToRestart, setJobToRestart] = useState(null);
    const [restarting, setRestarting] = useState(false);
    const [ragStats, setRagStats] = useState({ pending: 0, approved: 0, rejected: 0, escalated: 0 });
    const [approvalHistory, setApprovalHistory] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [historyFilter, setHistoryFilter] = useState('all');
    const location = useLocation();

    // Fetch pipeline jobs and RAG stats from API
    const fetchPipelineData = useCallback(async () => {
        try {
            // Fetch pipeline jobs, RAG stats, and approval history in parallel
            const [jobsResponse, ragStatsResponse, historyResponse] = await Promise.all([
                pipelineAPI.getJobs({ limit: 20 }),
                ragApprovalAPI.getStats().catch(() => ({ overall: {} })),
                ragApprovalAPI.getHistory({ limit: 30 }).catch(() => ({ history: [] }))
            ]);

            const data = jobsResponse?.data || jobsResponse;

            // Update RAG stats
            if (ragStatsResponse?.overall) {
                setRagStats(ragStatsResponse.overall);
            }

            // Update approval history
            if (historyResponse?.history) {
                setApprovalHistory(historyResponse.history);
            }

            // Separate active and completed jobs
            const jobs = data?.jobs || [];
            const active = jobs.filter(j => j.status === 'active' || j.status === 'pending');
            const completed = jobs.filter(j => j.status === 'completed' || j.status === 'failed');

            // Transform jobs to expected format - Updated for RAG Approval Flow
            const transformedActive = active.map(job => {
                // Determine current stage based on job status
                const currentStage = job.current_stage || 'rag_queue';
                const isInRagQueue = job.status === 'pending_approval' || currentStage === 'rag_queue';
                const isInHumanReview = currentStage === 'human_review';
                const isInAiAnalysis = currentStage === 'ai_analysis';

                return {
                    id: `job-${job.job_id}`,
                    buildId: `#${job.build_id}`,
                    testName: job.test_name || 'Unknown Test',
                    triggerType: job.trigger_source || 'manual',
                    triggeredBy: job.triggered_by_user || 'system',
                    startedAt: new Date(job.triggered_at),
                    currentStage: currentStage,
                    errorCategory: job.error_category || 'UNKNOWN',
                    stageProgress: 50,
                    estimatedTime: isInRagQueue ? 'Awaiting human approval' : '~30 sec remaining',
                    logId: `log_${job.job_id}`,
                    logSize: '24 KB',
                    logStoredInDB: true,
                    stages: {
                        trigger: { status: 'completed', duration: 100 },
                        classify: { status: 'completed', duration: 500 },
                        rag_queue: { status: isInRagQueue ? 'in_progress' : 'completed', duration: null, progress: 50 },
                        human_review: { status: isInHumanReview ? 'in_progress' : (isInRagQueue ? 'pending' : 'completed'), duration: null },
                        ai_analysis: { status: isInAiAnalysis ? 'in_progress' : (isInHumanReview || isInRagQueue ? 'pending' : 'completed'), duration: null },
                        complete: { status: currentStage === 'complete' ? 'completed' : 'pending', duration: null },
                    }
                };
            });

            const transformedCompleted = completed.map(job => ({
                id: `job-${job.job_id}`,
                buildId: `#${job.build_id}`,
                testName: job.test_name || 'Unknown Test',
                triggerType: job.trigger_source || 'manual',
                status: job.status === 'completed' ? 'success' : 'failed',
                errorCategory: job.error_category || 'UNKNOWN',
                aiTriggered: job.ai_triggered || false,
                totalDuration: 35000,
                completedAt: job.analyzed_at ? new Date(job.analyzed_at).toLocaleString() : '-',
                logId: `log_${job.job_id}`,
                logSize: '120 KB',
                errorCount: job.status === 'failed' ? 1 : 0,
                warningCount: 0
            }));

            setActiveJobs(transformedActive);
            setCompletedJobs(transformedCompleted);
            setError(null);
        } catch (err) {
            console.error('Error fetching pipeline data:', err);
            setError(err.message || 'Failed to fetch pipeline data');
            setActiveJobs([]);
            setCompletedJobs([]);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, []);

    // Fetch logs for a specific job
    const fetchJobLogs = async (jobId) => {
        try {
            const numericId = jobId.replace('job-', '');
            const response = await pipelineAPI.getJobLogs(numericId);
            const data = response?.data || response;
            setJobLogs(prev => ({ ...prev, [jobId]: data?.logs || [] }));
            return data?.logs || [];
        } catch (err) {
            console.error('Error fetching job logs:', err);
            return [];
        }
    };

    const getJobLogs = (job) => {
        return jobLogs[job.id] || [];
    };

    // Auto-fetch on mount and navigation
    useEffect(() => {
        fetchPipelineData();
    }, [location.key, fetchPipelineData]);

    // Simulate real-time updates
    useEffect(() => {
        const interval = setInterval(() => {
            setActiveJobs(prev => prev.map(job => {
                // Null safety checks
                if (!job?.stages || !job?.currentStage) return job;

                const currentStageIndex = getStageIndex(job.currentStage);
                const stage = job.stages[job.currentStage];

                // Check if stage exists and is in progress
                if (stage?.status === 'in_progress') {
                    const newProgress = Math.min((stage.progress || 0) + Math.random() * 10, 100);
                    return {
                        ...job,
                        stages: {
                            ...job.stages,
                            [job.currentStage]: { ...stage, progress: newProgress }
                        },
                        stageProgress: newProgress
                    };
                }
                return job;
            }));
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchPipelineData();
    };

    const handleViewLogs = async (job) => {
        setSelectedJobForLog(job);
        setLogDialogOpen(true);
        setLogTab(0);
        setLogFilter('all');
        setLogSearch('');
        // Fetch logs for the job
        await fetchJobLogs(job.id);
    };

    const handleDownloadLogs = (job) => {
        const logs = getJobLogs(job);
        if (logs.length === 0) {
            alert('No logs available for this job');
            return;
        }
        const logText = logs.map(l => `[${l.time}] [${l.level}] [${l.source}] ${l.message}`).join('\n');
        const blob = new Blob([logText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pipeline_log_${job.buildId.replace('#', '')}_${job.id}.log`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const handleCopyLogs = (job) => {
        const logs = getJobLogs(job);
        if (logs.length === 0) {
            alert('No logs available for this job');
            return;
        }
        const logText = logs.map(l => `[${l.time}] [${l.level}] [${l.source}] ${l.message}`).join('\n');
        navigator.clipboard.writeText(logText);
    };

    // Handle restart AI analysis
    const handleRestartClick = (job) => {
        setJobToRestart(job);
        setRestartDialogOpen(true);
    };

    const handleRestartConfirm = async () => {
        if (!jobToRestart) return;

        setRestarting(true);
        try {
            const buildId = jobToRestart.buildId.replace('#', '');
            await triggerAPI.triggerAnalysis({
                build_id: buildId,
                reason: 'Manual restart from Pipeline Status page',
                triggered_by: 'dashboard_user'
            });

            // Refresh the job list after restart
            await fetchPipelineData();
            setRestartDialogOpen(false);
            setJobToRestart(null);
        } catch (err) {
            console.error('Error restarting analysis:', err);
            setError('Failed to restart analysis: ' + (err.message || 'Unknown error'));
        } finally {
            setRestarting(false);
        }
    };

    // Filter jobs by status
    const getFilteredJobs = (jobs, isCompleted = false) => {
        if (statusFilter === 'all') return jobs;

        return jobs.filter(job => {
            if (isCompleted) {
                // For completed jobs table
                if (statusFilter === 'completed') return job.status === 'success';
                if (statusFilter === 'error') return job.status === 'failed';
            } else {
                // For active jobs
                if (statusFilter === 'completed') return job.currentStage === 'complete';
                if (statusFilter === 'error') return job.stages && Object.values(job.stages).some(s => s?.status === 'failed');
                if (statusFilter === 'in_progress') return !['complete'].includes(job.currentStage) && !(job.stages && Object.values(job.stages).some(s => s?.status === 'failed'));
            }
            return true;
        });
    };

    const filteredActiveJobs = getFilteredJobs(activeJobs, false);
    const filteredCompletedJobs = getFilteredJobs(completedJobs, true);

    const getFilteredLogs = () => {
        if (!selectedJobForLog) return [];
        const logs = getJobLogs(selectedJobForLog);
        return logs.filter(log => {
            if (logFilter !== 'all' && log.level !== logFilter) return false;
            if (logSearch && !log.message.toLowerCase().includes(logSearch.toLowerCase())) return false;
            return true;
        });
    };

    const activeCount = activeJobs.length;
    const queuedCount = activeJobs.filter(j => j.currentStage === 'rag_queue').length;
    const pendingApproval = ragStats.pending || 0;
    const totalApproved = ragStats.approved || 0;

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
                                Agentic AI & RAG Pipelines
                            </Typography>
                            <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                                Monitor AI analysis workflows, RAG processing, and pipeline status
                            </Typography>
                        </Box>
                        <Box display="flex" gap={2} alignItems="center">
                            <FormControl size="small" sx={{ minWidth: 140 }}>
                                <Select
                                    value={statusFilter}
                                    onChange={(e) => setStatusFilter(e.target.value)}
                                    displayEmpty
                                    sx={{
                                        bgcolor: 'rgba(255,255,255,0.2)',
                                        color: 'white',
                                        '& .MuiOutlinedInput-notchedOutline': { border: 'none' },
                                        '& .MuiSvgIcon-root': { color: 'white' }
                                    }}
                                    startAdornment={<FilterListIcon sx={{ mr: 1, color: 'white' }} />}
                                >
                                    <MenuItem value="all">All Status</MenuItem>
                                    <MenuItem value="completed">Completed</MenuItem>
                                    <MenuItem value="error">Error/Failed</MenuItem>
                                    <MenuItem value="in_progress">In Progress</MenuItem>
                                </Select>
                            </FormControl>
                            <Chip
                                icon={<HourglassEmptyIcon sx={{ color: '#f59e0b !important' }} />}
                                label={`${pendingApproval} Pending Approval`}
                                sx={{ bgcolor: pendingApproval > 0 ? 'rgba(245,158,11,0.3)' : 'rgba(255,255,255,0.2)', color: 'white', fontWeight: pendingApproval > 0 ? 600 : 400 }}
                                onClick={() => window.location.href = '/rag-approval'}
                            />
                            <Chip
                                icon={<CheckCircleIcon sx={{ color: `${theme.success} !important` }} />}
                                label={`${totalApproved} Approved`}
                                sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                            />
                            <Chip
                                icon={<PlayArrowIcon sx={{ color: `${theme.success} !important` }} />}
                                label={`${activeCount} Active`}
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
                        </Box>
                    </Box>
                </Container>
            </Box>

            <Container maxWidth="xl">
                {/* Error State */}
                {error && (
                    <Alert severity="error" sx={{ mb: 3, borderRadius: 3 }}>
                        <Typography variant="body2"><strong>Error:</strong> {error}</Typography>
                    </Alert>
                )}

                {/* Pipeline Stages Overview */}
                <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                    <Typography variant="h6" fontWeight="bold" mb={3}>Pipeline Stages</Typography>
                    <Stepper alternativeLabel>
                        {pipelineStages.map((stage, index) => (
                            <Step key={stage.id} completed={false}>
                                <StepLabel
                                    StepIconComponent={() => (
                                        <Avatar sx={{ bgcolor: alpha('#0891b2', 0.1), color: '#0891b2', width: 40, height: 40 }}>
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

                {/* RAG Approval Flow Info */}
                <Alert
                    severity="info"
                    icon={<FactCheckIcon />}
                    sx={{ mb: 3, borderRadius: 3 }}
                    action={
                        <Button color="inherit" size="small" onClick={() => window.location.href = '/rag-approval'}>
                            Go to RAG Approval
                        </Button>
                    }
                >
                    <Typography variant="body2">
                        <strong>Human-in-the-Loop Flow:</strong> All triggers go to RAG Queue for human approval.
                        <strong> CODE_ERROR</strong> → triggers AI deep analysis after approval.
                        <strong> Other categories</strong> → RAG solution accepted, marked resolved.
                    </Typography>
                </Alert>

                {/* Active Jobs */}
                <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                        <Typography variant="h6" fontWeight="bold">
                            Active Analyses ({filteredActiveJobs.length}{statusFilter !== 'all' ? ` of ${activeJobs.length}` : ''})
                        </Typography>
                    </Box>

                    {filteredActiveJobs.length === 0 ? (
                        <Alert severity="info">
                            {statusFilter !== 'all'
                                ? `No jobs matching filter "${statusFilter}". Try changing the filter.`
                                : 'No active analysis jobs. Trigger a new analysis to see pipeline progress.'}
                        </Alert>
                    ) : (
                        filteredActiveJobs.map((job) => {
                            const currentStageIndex = getStageIndex(job.currentStage);
                            const isExpanded = expandedJob === job.id;

                            return (
                                <Paper
                                    key={job.id}
                                    sx={{
                                        p: 3,
                                        mb: 2,
                                        borderRadius: 3,
                                        border: '1px solid #e2e8f0',
                                        bgcolor: '#fafafa'
                                    }}
                                >
                                    {/* Job Header */}
                                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                                        <Box display="flex" alignItems="center" gap={2}>
                                            <Avatar sx={{ bgcolor: alpha('#0891b2', 0.1), color: '#0891b2' }}>
                                                <AccountTreeIcon />
                                            </Avatar>
                                            <Box>
                                                <Box display="flex" alignItems="center" gap={1}>
                                                    <Typography variant="h6" fontWeight="bold">{job.buildId}</Typography>
                                                    <Chip
                                                        label={job.triggerType === 'manual' ? 'Manual' : 'Cron'}
                                                        size="small"
                                                        sx={{
                                                            bgcolor: job.triggerType === 'manual' ? '#dbeafe' : '#fef3c7',
                                                            color: job.triggerType === 'manual' ? '#1e40af' : '#92400e'
                                                        }}
                                                    />
                                                    <Chip
                                                        icon={<StorageIcon />}
                                                        label={job.logSize}
                                                        size="small"
                                                        variant="outlined"
                                                        sx={{ '& .MuiChip-icon': { fontSize: 14 } }}
                                                    />
                                                </Box>
                                                <Typography variant="body2" color="textSecondary">{job.testName}</Typography>
                                            </Box>
                                        </Box>
                                        <Box display="flex" alignItems="center" gap={1}>
                                            <Tooltip title="View Logs">
                                                <IconButton onClick={() => handleViewLogs(job)} sx={{ color: '#0891b2' }}>
                                                    <TerminalIcon />
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title="Download Logs">
                                                <IconButton onClick={() => handleDownloadLogs(job)}>
                                                    <DownloadIcon />
                                                </IconButton>
                                            </Tooltip>
                                            <Box textAlign="right" sx={{ mx: 2 }}>
                                                <Typography variant="body2" color="textSecondary">
                                                    <AccessTimeIcon sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} />
                                                    {job.estimatedTime}
                                                </Typography>
                                                <Typography variant="caption" color="textSecondary">
                                                    By: {job.triggeredBy}
                                                </Typography>
                                            </Box>
                                            <IconButton onClick={() => setExpandedJob(isExpanded ? null : job.id)}>
                                                {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                            </IconButton>
                                        </Box>
                                    </Box>

                                    {/* Progress Stepper */}
                                    <Box mb={2}>
                                        <Stepper activeStep={currentStageIndex} alternativeLabel>
                                            {pipelineStages.map((stage, index) => {
                                                const stageData = job.stages?.[stage.id] || { status: 'pending', progress: 0 };
                                                return (
                                                    <Step key={stage.id} completed={stageData.status === 'completed'}>
                                                        <StepLabel
                                                            error={stageData.status === 'failed'}
                                                            StepIconComponent={() => <StageStatusIcon status={stageData.status || 'pending'} />}
                                                        >
                                                            <Typography variant="caption">
                                                                {stageData.status === 'completed' ? formatDuration(stageData.duration) :
                                                                 stageData.status === 'in_progress' ? `${Math.round(stageData.progress || 0)}%` : '-'}
                                                            </Typography>
                                                        </StepLabel>
                                                    </Step>
                                                );
                                            })}
                                        </Stepper>
                                    </Box>

                                    {/* Current Stage Progress */}
                                    <Box>
                                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                                            <Typography variant="body2" fontWeight={600}>
                                                Current: {pipelineStages[currentStageIndex]?.label}
                                            </Typography>
                                            <Typography variant="body2" color="primary" fontWeight={600}>
                                                {Math.round(job.stageProgress)}%
                                            </Typography>
                                        </Box>
                                        <LinearProgress
                                            variant="determinate"
                                            value={job.stageProgress}
                                            sx={{
                                                height: 8,
                                                borderRadius: 4,
                                                bgcolor: '#e2e8f0',
                                                '& .MuiLinearProgress-bar': {
                                                    bgcolor: '#0891b2',
                                                    borderRadius: 4
                                                }
                                            }}
                                        />
                                    </Box>

                                    {/* Expanded Details with Live Logs */}
                                    <Collapse in={isExpanded}>
                                        <Divider sx={{ my: 2 }} />
                                        <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                                            <TerminalIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'middle' }} />
                                            Live Log Stream
                                        </Typography>
                                        <Paper
                                            sx={{
                                                p: 2,
                                                bgcolor: '#1e1e1e',
                                                borderRadius: 2,
                                                maxHeight: 200,
                                                overflow: 'auto',
                                                fontFamily: 'monospace',
                                                fontSize: '0.75rem'
                                            }}
                                        >
                                            {getJobLogs(job).length > 0 ? (
                                                getJobLogs(job).slice(-10).map((log, idx) => (
                                                    <Box key={idx} sx={{ mb: 0.5 }}>
                                                        <Typography
                                                            component="span"
                                                            sx={{
                                                                color: log.level === 'ERROR' ? '#ef4444' :
                                                                       log.level === 'WARNING' ? '#f59e0b' :
                                                                       log.level === 'DEBUG' ? '#64748b' : '#10b981',
                                                                fontFamily: 'monospace',
                                                                fontSize: '0.75rem'
                                                            }}
                                                        >
                                                            [{log.time}] [{log.level}] [{log.source}] {log.message}
                                                        </Typography>
                                                    </Box>
                                                ))
                                            ) : (
                                                <Typography sx={{ color: '#64748b', fontFamily: 'monospace', fontSize: '0.75rem' }}>
                                                    Loading logs... Click "View Full Logs" to fetch.
                                                </Typography>
                                            )}
                                        </Paper>
                                        <Box display="flex" gap={1} mt={2}>
                                            <Button size="small" startIcon={<VisibilityIcon />} onClick={() => handleViewLogs(job)}>
                                                View Full Logs
                                            </Button>
                                            <Button size="small" startIcon={<DownloadIcon />} onClick={() => handleDownloadLogs(job)}>
                                                Download
                                            </Button>
                                            <Button size="small" startIcon={<ContentCopyIcon />} onClick={() => handleCopyLogs(job)}>
                                                Copy to Clipboard
                                            </Button>
                                        </Box>
                                    </Collapse>
                                </Paper>
                            );
                        })
                    )}
                </Paper>

                {/* Completed Jobs with Log Access */}
                <Paper elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', overflow: 'hidden' }}>
                    <Box sx={{ p: 3, borderBottom: '1px solid #e2e8f0' }}>
                        <Typography variant="h6" fontWeight="bold">
                            Recent Completed Analyses ({filteredCompletedJobs.length}{statusFilter !== 'all' ? ` of ${completedJobs.length}` : ''})
                        </Typography>
                    </Box>
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow sx={{ bgcolor: '#f8fafc' }}>
                                    <TableCell sx={{ fontWeight: 600 }}>Build ID</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Test Name</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Trigger</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Duration</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Log Info</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Completed</TableCell>
                                    <TableCell align="center" sx={{ fontWeight: 600 }}>Logs</TableCell>
                                    <TableCell align="center" sx={{ fontWeight: 600 }}>Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {filteredCompletedJobs.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                                            <Typography variant="body2" color="textSecondary">
                                                {statusFilter !== 'all'
                                                    ? `No jobs matching filter "${statusFilter}"`
                                                    : 'No completed jobs found'}
                                            </Typography>
                                        </TableCell>
                                    </TableRow>
                                ) : filteredCompletedJobs.map((job) => (
                                    <TableRow key={job.id} sx={{ '&:hover': { bgcolor: '#f8fafc' } }}>
                                        <TableCell>
                                            <Typography variant="body2" fontWeight={600}>{job.buildId}</Typography>
                                        </TableCell>
                                        <TableCell>{job.testName}</TableCell>
                                        <TableCell>
                                            <Chip
                                                label={job.triggerType === 'manual' ? 'Manual' : 'Cron'}
                                                size="small"
                                                sx={{
                                                    bgcolor: job.triggerType === 'manual' ? '#dbeafe' : '#fef3c7',
                                                    color: job.triggerType === 'manual' ? '#1e40af' : '#92400e',
                                                    fontSize: '0.7rem'
                                                }}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Chip
                                                icon={job.status === 'success' ? <CheckCircleIcon /> : <ErrorIcon />}
                                                label={job.status === 'success' ? 'Success' : 'Failed'}
                                                size="small"
                                                sx={{
                                                    bgcolor: job.status === 'success' ? '#dcfce7' : '#fee2e2',
                                                    color: job.status === 'success' ? '#166534' : '#991b1b',
                                                    '& .MuiChip-icon': { color: 'inherit' }
                                                }}
                                            />
                                        </TableCell>
                                        <TableCell>{formatDuration(job.totalDuration)}</TableCell>
                                        <TableCell>
                                            <Box display="flex" alignItems="center" gap={1}>
                                                <Chip label={job.logSize} size="small" variant="outlined" sx={{ fontSize: '0.65rem' }} />
                                                {job.errorCount > 0 && (
                                                    <Badge badgeContent={job.errorCount} color="error" sx={{ '& .MuiBadge-badge': { fontSize: '0.6rem' } }}>
                                                        <ErrorIcon sx={{ fontSize: 16, color: '#ef4444' }} />
                                                    </Badge>
                                                )}
                                                {job.warningCount > 0 && (
                                                    <Badge badgeContent={job.warningCount} color="warning" sx={{ '& .MuiBadge-badge': { fontSize: '0.6rem' } }}>
                                                        <WarningIcon sx={{ fontSize: 16, color: '#f59e0b' }} />
                                                    </Badge>
                                                )}
                                            </Box>
                                        </TableCell>
                                        <TableCell>
                                            <Typography variant="body2" color="textSecondary">{job.completedAt}</Typography>
                                        </TableCell>
                                        <TableCell align="center">
                                            <Tooltip title="View Logs">
                                                <IconButton size="small" onClick={() => handleViewLogs({ ...job, currentStage: 'complete' })}>
                                                    <TerminalIcon fontSize="small" sx={{ color: '#0891b2' }} />
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title="Download Logs">
                                                <IconButton size="small" onClick={() => handleDownloadLogs({ ...job, currentStage: 'complete' })}>
                                                    <DownloadIcon fontSize="small" />
                                                </IconButton>
                                            </Tooltip>
                                        </TableCell>
                                        <TableCell align="center">
                                            {job.status === 'failed' && (
                                                <Tooltip title="Restart AI Analysis">
                                                    <Button
                                                        size="small"
                                                        variant="outlined"
                                                        color="primary"
                                                        startIcon={<ReplayIcon />}
                                                        onClick={() => handleRestartClick(job)}
                                                        sx={{ fontSize: '0.7rem' }}
                                                    >
                                                        Restart
                                                    </Button>
                                                </Tooltip>
                                            )}
                                            {job.status === 'success' && (
                                                <Typography variant="body2" color="textSecondary">-</Typography>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Paper>

                {/* RAG Approval History */}
                <Paper elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', overflow: 'hidden', mt: 3 }}>
                    <Box sx={{ p: 3, borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="h6" fontWeight="bold">
                            RAG Approval History ({approvalHistory.length})
                        </Typography>
                        <FormControl size="small" sx={{ minWidth: 140 }}>
                            <Select
                                value={historyFilter}
                                onChange={(e) => setHistoryFilter(e.target.value)}
                                displayEmpty
                            >
                                <MenuItem value="all">All Status</MenuItem>
                                <MenuItem value="approved">Approved</MenuItem>
                                <MenuItem value="rejected">Rejected</MenuItem>
                                <MenuItem value="escalated">Escalated</MenuItem>
                            </Select>
                        </FormControl>
                    </Box>
                    <TableContainer>
                        <Table size="small">
                            <TableHead>
                                <TableRow sx={{ bgcolor: '#f8fafc' }}>
                                    <TableCell sx={{ fontWeight: 600 }}>Build ID</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Category</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Trigger</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Reviewed By</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Reviewed At</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>AI Triggered</TableCell>
                                    <TableCell sx={{ fontWeight: 600 }}>Notes</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {approvalHistory
                                    .filter(item => historyFilter === 'all' || item.review_status === historyFilter)
                                    .map((item) => (
                                    <TableRow key={item.id} sx={{ '&:hover': { bgcolor: '#f8fafc' } }}>
                                        <TableCell>
                                            <Typography variant="body2" fontWeight={600}>#{item.build_id}</Typography>
                                        </TableCell>
                                        <TableCell>
                                            <Box display="flex" alignItems="center" gap={0.5}>
                                                <Chip
                                                    label={item.error_category || 'UNKNOWN'}
                                                    size="small"
                                                    sx={{
                                                        bgcolor: item.error_category === 'CODE_ERROR' ? '#fee2e2' : '#e0f2fe',
                                                        color: item.error_category === 'CODE_ERROR' ? '#991b1b' : '#0369a1',
                                                        fontSize: '0.7rem'
                                                    }}
                                                />
                                                {item.category_changed && (
                                                    <Tooltip title={`Changed from: ${item.original_category}`}>
                                                        <Chip
                                                            label={`← ${item.original_category}`}
                                                            size="small"
                                                            variant="outlined"
                                                            sx={{ fontSize: '0.6rem', height: 20, color: '#f59e0b' }}
                                                        />
                                                    </Tooltip>
                                                )}
                                            </Box>
                                        </TableCell>
                                        <TableCell>
                                            <Chip
                                                icon={item.review_status === 'approved' ? <CheckCircleIcon /> :
                                                      item.review_status === 'rejected' ? <CancelIcon /> : <BoltIcon />}
                                                label={(item.review_status || 'pending').charAt(0).toUpperCase() + (item.review_status || 'pending').slice(1)}
                                                size="small"
                                                sx={{
                                                    bgcolor: item.review_status === 'approved' ? '#dcfce7' :
                                                             item.review_status === 'rejected' ? '#fee2e2' : '#fef3c7',
                                                    color: item.review_status === 'approved' ? '#166534' :
                                                           item.review_status === 'rejected' ? '#991b1b' : '#92400e',
                                                    '& .MuiChip-icon': { color: 'inherit' }
                                                }}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Chip
                                                label={item.trigger_type || 'MANUAL'}
                                                size="small"
                                                variant="outlined"
                                                sx={{ fontSize: '0.65rem' }}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Typography variant="body2">{item.reviewed_by || '-'}</Typography>
                                        </TableCell>
                                        <TableCell>
                                            <Typography variant="body2" color="textSecondary">
                                                {item.reviewed_at ? new Date(item.reviewed_at).toLocaleString() : '-'}
                                            </Typography>
                                        </TableCell>
                                        <TableCell>
                                            {item.ai_analysis_id ? (
                                                <Chip
                                                    icon={<SmartToyIcon />}
                                                    label={`AI #${item.ai_analysis_id}`}
                                                    size="small"
                                                    sx={{ bgcolor: '#dbeafe', color: '#1e40af', '& .MuiChip-icon': { color: 'inherit', fontSize: 14 } }}
                                                />
                                            ) : (
                                                <Typography variant="body2" color="textSecondary">-</Typography>
                                            )}
                                        </TableCell>
                                        <TableCell>
                                            {item.review_feedback ? (
                                                <Tooltip title={item.review_feedback}>
                                                    <Typography variant="body2" color="textSecondary" sx={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                        {item.review_feedback}
                                                    </Typography>
                                                </Tooltip>
                                            ) : '-'}
                                        </TableCell>
                                    </TableRow>
                                ))}
                                {approvalHistory.filter(item => historyFilter === 'all' || item.review_status === historyFilter).length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                                            <Typography variant="body2" color="textSecondary">
                                                No approval history found
                                            </Typography>
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Paper>
            </Container>

            {/* Log Viewer Dialog */}
            <Dialog open={logDialogOpen} onClose={() => setLogDialogOpen(false)} maxWidth="lg" fullWidth>
                <DialogTitle>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Box display="flex" alignItems="center" gap={1}>
                            <TerminalIcon sx={{ color: '#0891b2' }} />
                            Pipeline Logs - {selectedJobForLog?.buildId}
                        </Box>
                        <Box display="flex" gap={1}>
                            <Button size="small" startIcon={<ContentCopyIcon />} onClick={() => handleCopyLogs(selectedJobForLog)}>
                                Copy
                            </Button>
                            <Button size="small" startIcon={<DownloadIcon />} onClick={() => handleDownloadLogs(selectedJobForLog)}>
                                Download
                            </Button>
                        </Box>
                    </Box>
                </DialogTitle>
                <DialogContent>
                    {/* Log Info Bar */}
                    <Box sx={{ mb: 2, p: 2, bgcolor: '#f8fafc', borderRadius: 2 }}>
                        <Grid container spacing={2}>
                            <Grid item xs={3}>
                                <Typography variant="caption" color="textSecondary">Job ID</Typography>
                                <Typography variant="body2" fontWeight={600}>{selectedJobForLog?.id}</Typography>
                            </Grid>
                            <Grid item xs={3}>
                                <Typography variant="caption" color="textSecondary">Log ID (MongoDB)</Typography>
                                <Typography variant="body2" fontWeight={600} sx={{ fontFamily: 'monospace' }}>{selectedJobForLog?.logId}</Typography>
                            </Grid>
                            <Grid item xs={3}>
                                <Typography variant="caption" color="textSecondary">Log Size</Typography>
                                <Typography variant="body2" fontWeight={600}>{selectedJobForLog?.logSize}</Typography>
                            </Grid>
                            <Grid item xs={3}>
                                <Typography variant="caption" color="textSecondary">Storage</Typography>
                                <Chip icon={<StorageIcon />} label="MongoDB" size="small" color="success" sx={{ '& .MuiChip-icon': { fontSize: 14 } }} />
                            </Grid>
                        </Grid>
                    </Box>

                    {/* Tabs */}
                    <Tabs value={logTab} onChange={(e, v) => setLogTab(v)} sx={{ mb: 2 }}>
                        <Tab label="All Logs" />
                        <Tab label="Errors & Warnings" />
                        <Tab label="By Stage" />
                        <Tab label="Raw JSON" />
                    </Tabs>

                    {/* Filters */}
                    <Box display="flex" gap={2} mb={2}>
                        <TextField
                            size="small"
                            placeholder="Search logs..."
                            value={logSearch}
                            onChange={(e) => setLogSearch(e.target.value)}
                            sx={{ flex: 1 }}
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment>
                            }}
                        />
                        <TextField
                            size="small"
                            select
                            label="Level"
                            value={logFilter}
                            onChange={(e) => setLogFilter(e.target.value)}
                            sx={{ width: 120 }}
                            SelectProps={{ native: true }}
                        >
                            <option value="all">All</option>
                            <option value="INFO">INFO</option>
                            <option value="DEBUG">DEBUG</option>
                            <option value="WARNING">WARNING</option>
                            <option value="ERROR">ERROR</option>
                        </TextField>
                    </Box>

                    {/* Log Content */}
                    {logTab === 0 && (
                        <Paper
                            sx={{
                                p: 2,
                                bgcolor: '#1e1e1e',
                                borderRadius: 2,
                                maxHeight: 400,
                                overflow: 'auto'
                            }}
                        >
                            {getFilteredLogs().map((log, idx) => (
                                <Box
                                    key={idx}
                                    sx={{
                                        py: 0.5,
                                        px: 1,
                                        borderRadius: 1,
                                        '&:hover': { bgcolor: 'rgba(255,255,255,0.05)' },
                                        borderLeft: `3px solid ${
                                            log.level === 'ERROR' ? '#ef4444' :
                                            log.level === 'WARNING' ? '#f59e0b' :
                                            log.level === 'DEBUG' ? '#64748b' : '#10b981'
                                        }`
                                    }}
                                >
                                    <Typography
                                        sx={{
                                            fontFamily: 'monospace',
                                            fontSize: '0.8rem',
                                            color: log.level === 'ERROR' ? '#fca5a5' :
                                                   log.level === 'WARNING' ? '#fcd34d' :
                                                   log.level === 'DEBUG' ? '#94a3b8' : '#a7f3d0'
                                        }}
                                    >
                                        <span style={{ color: '#64748b' }}>[{log.time}]</span>{' '}
                                        <span style={{ color: log.level === 'ERROR' ? '#ef4444' : log.level === 'WARNING' ? '#f59e0b' : '#10b981' }}>
                                            [{log.level}]
                                        </span>{' '}
                                        <span style={{ color: '#38bdf8' }}>[{log.source}]</span>{' '}
                                        {log.message}
                                    </Typography>
                                </Box>
                            ))}
                        </Paper>
                    )}

                    {logTab === 1 && (
                        <Paper sx={{ p: 2, bgcolor: '#1e1e1e', borderRadius: 2, maxHeight: 400, overflow: 'auto' }}>
                            {getFilteredLogs().filter(l => l.level === 'ERROR' || l.level === 'WARNING').map((log, idx) => (
                                <Box key={idx} sx={{ py: 0.5, px: 1, borderLeft: `3px solid ${log.level === 'ERROR' ? '#ef4444' : '#f59e0b'}` }}>
                                    <Typography sx={{ fontFamily: 'monospace', fontSize: '0.8rem', color: log.level === 'ERROR' ? '#fca5a5' : '#fcd34d' }}>
                                        [{log.time}] [{log.level}] [{log.source}] {log.message}
                                    </Typography>
                                </Box>
                            ))}
                            {getFilteredLogs().filter(l => l.level === 'ERROR' || l.level === 'WARNING').length === 0 && (
                                <Typography sx={{ color: '#10b981', fontFamily: 'monospace' }}>No errors or warnings found</Typography>
                            )}
                        </Paper>
                    )}

                    {logTab === 2 && (
                        <Box>
                            {pipelineStages.map(stage => {
                                const stageLogs = getFilteredLogs().filter(l => l.stage === stage.id);
                                if (stageLogs.length === 0) return null;
                                return (
                                    <Box key={stage.id} sx={{ mb: 2 }}>
                                        <Typography variant="subtitle2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                                            {stage.icon} {stage.label} ({stageLogs.length} entries)
                                        </Typography>
                                        <Paper sx={{ p: 1, bgcolor: '#1e1e1e', borderRadius: 1 }}>
                                            {stageLogs.map((log, idx) => (
                                                <Typography key={idx} sx={{ fontFamily: 'monospace', fontSize: '0.75rem', color: '#a7f3d0' }}>
                                                    [{log.time}] {log.message}
                                                </Typography>
                                            ))}
                                        </Paper>
                                    </Box>
                                );
                            })}
                        </Box>
                    )}

                    {logTab === 3 && (
                        <Paper sx={{ p: 2, bgcolor: '#1e1e1e', borderRadius: 2, maxHeight: 400, overflow: 'auto' }}>
                            <pre style={{ margin: 0, color: '#a7f3d0', fontSize: '0.75rem' }}>
                                {JSON.stringify(getFilteredLogs(), null, 2)}
                            </pre>
                        </Paper>
                    )}
                </DialogContent>
                <DialogActions sx={{ p: 2 }}>
                    <Typography variant="caption" color="textSecondary" sx={{ flex: 1 }}>
                        Logs are stored in MongoDB and retained for 90 days. Log ID: {selectedJobForLog?.logId}
                    </Typography>
                    <Button onClick={() => setLogDialogOpen(false)}>Close</Button>
                </DialogActions>
            </Dialog>

            {/* Restart Confirmation Dialog */}
            <Dialog
                open={restartDialogOpen}
                onClose={() => !restarting && setRestartDialogOpen(false)}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle>
                    <Box display="flex" alignItems="center" gap={1}>
                        <ReplayIcon sx={{ color: '#0891b2' }} />
                        Restart AI Analysis
                    </Box>
                </DialogTitle>
                <DialogContent>
                    <Alert severity="info" sx={{ mb: 2 }}>
                        This will restart the AI analysis for the selected build. The previous analysis results will be replaced.
                    </Alert>
                    {jobToRestart && (
                        <Box sx={{ p: 2, bgcolor: '#f8fafc', borderRadius: 2 }}>
                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <Typography variant="caption" color="textSecondary">Build ID</Typography>
                                    <Typography variant="body1" fontWeight={600}>{jobToRestart.buildId}</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="caption" color="textSecondary">Test Name</Typography>
                                    <Typography variant="body2">{jobToRestart.testName}</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="caption" color="textSecondary">Previous Status</Typography>
                                    <Chip
                                        label={jobToRestart.status === 'success' ? 'Success' : 'Failed'}
                                        size="small"
                                        color={jobToRestart.status === 'success' ? 'success' : 'error'}
                                    />
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="caption" color="textSecondary">Trigger Type</Typography>
                                    <Typography variant="body2">{jobToRestart.triggerType}</Typography>
                                </Grid>
                            </Grid>
                        </Box>
                    )}
                </DialogContent>
                <DialogActions sx={{ p: 2 }}>
                    <Button
                        onClick={() => setRestartDialogOpen(false)}
                        disabled={restarting}
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleRestartConfirm}
                        disabled={restarting}
                        startIcon={restarting ? <CircularProgress size={20} color="inherit" /> : <ReplayIcon />}
                    >
                        {restarting ? 'Restarting...' : 'Restart Analysis'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default PipelineStatusPreview;
