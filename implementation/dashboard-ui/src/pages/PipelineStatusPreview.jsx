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
import { pipelineAPI, monitoringAPI } from '../services/api';

// Pipeline Stages Definition
const pipelineStages = [
    { id: 'trigger', label: 'Trigger Received', icon: <TriggerIcon />, description: 'Analysis request received from manual trigger or cron job' },
    { id: 'queue', label: 'Queued in Celery', icon: <HourglassEmptyIcon />, description: 'Task queued in Celery worker for processing' },
    { id: 'react', label: 'ReAct Agent Analysis', icon: <SmartToyIcon />, description: 'Multi-step reasoning with ReAct agent for error classification' },
    { id: 'crag', label: 'CRAG Verification', icon: <FactCheckIcon />, description: 'Corrective RAG verification and knowledge base lookup' },
    { id: 'gemini', label: 'Gemini Formatting', icon: <AutoFixHighIcon />, description: 'Final formatting and recommendation generation with Gemini' },
    { id: 'complete', label: 'Analysis Complete', icon: <DoneAllIcon />, description: 'Analysis saved and ready for validation' },
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
    const location = useLocation();

    // Fetch pipeline jobs from API
    const fetchPipelineData = useCallback(async () => {
        try {
            const response = await pipelineAPI.getJobs({ limit: 20 });
            const data = response?.data || response;

            // Separate active and completed jobs
            const jobs = data?.jobs || [];
            const active = jobs.filter(j => j.status === 'active' || j.status === 'pending');
            const completed = jobs.filter(j => j.status === 'completed' || j.status === 'failed');

            // Transform jobs to expected format
            const transformedActive = active.map(job => ({
                id: `job-${job.job_id}`,
                buildId: `#${job.build_id}`,
                testName: job.test_name || 'Unknown Test',
                triggerType: job.trigger_source || 'manual',
                triggeredBy: job.triggered_by_user || 'system',
                startedAt: new Date(job.triggered_at),
                currentStage: job.current_stage || 'queue',
                stageProgress: 50,
                estimatedTime: '~30 sec remaining',
                logId: `log_${job.job_id}`,
                logSize: '24 KB',
                logStoredInDB: true,
                stages: {
                    trigger: { status: 'completed', duration: 100 },
                    queue: { status: job.current_stage === 'queue' ? 'in_progress' : 'completed', duration: 500, progress: 50 },
                    react: { status: ['react', 'crag', 'gemini', 'complete'].includes(job.current_stage) ? (job.current_stage === 'react' ? 'in_progress' : 'completed') : 'pending', duration: null, progress: 50 },
                    crag: { status: ['crag', 'gemini', 'complete'].includes(job.current_stage) ? (job.current_stage === 'crag' ? 'in_progress' : 'completed') : 'pending', duration: null },
                    gemini: { status: ['gemini', 'complete'].includes(job.current_stage) ? (job.current_stage === 'gemini' ? 'in_progress' : 'completed') : 'pending', duration: null },
                    complete: { status: job.current_stage === 'complete' ? 'completed' : 'pending', duration: null },
                }
            }));

            const transformedCompleted = completed.map(job => ({
                id: `job-${job.job_id}`,
                buildId: `#${job.build_id}`,
                testName: job.test_name || 'Unknown Test',
                triggerType: job.trigger_source || 'manual',
                status: job.status === 'completed' ? 'success' : 'failed',
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
                const currentStageIndex = getStageIndex(job.currentStage);
                const stage = job.stages[job.currentStage];

                if (stage.status === 'in_progress') {
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
    const queuedCount = activeJobs.filter(j => j.currentStage === 'queue').length;

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
                                Pipeline Status & Logs
                            </Typography>
                            <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                                Real-time tracking with full log access for debugging
                            </Typography>
                        </Box>
                        <Box display="flex" gap={2}>
                            <Chip
                                icon={<StorageIcon sx={{ color: `${theme.success} !important` }} />}
                                label="Logs in MongoDB"
                                sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                            />
                            <Chip
                                icon={<PlayArrowIcon sx={{ color: `${theme.success} !important` }} />}
                                label={`${activeCount} Active`}
                                sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                            />
                            <Chip
                                icon={<HourglassEmptyIcon sx={{ color: `${theme.warning} !important` }} />}
                                label={`${queuedCount} Queued`}
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

                {/* Log Storage Info */}
                <Alert
                    severity="info"
                    icon={<StorageIcon />}
                    sx={{ mb: 3, borderRadius: 3 }}
                    action={
                        <Button color="inherit" size="small" startIcon={<CloudDownloadIcon />}>
                            Export All Logs
                        </Button>
                    }
                >
                    <Typography variant="body2">
                        <strong>Log Storage:</strong> All pipeline logs are automatically stored in MongoDB with 90-day retention.
                        Logs are indexed by job ID, build ID, and timestamp for fast retrieval.
                    </Typography>
                </Alert>

                {/* Active Jobs */}
                <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                        <Typography variant="h6" fontWeight="bold">
                            Active Analyses ({activeJobs.length})
                        </Typography>
                    </Box>

                    {activeJobs.length === 0 ? (
                        <Alert severity="info">No active analysis jobs. Trigger a new analysis to see pipeline progress.</Alert>
                    ) : (
                        activeJobs.map((job) => {
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
                                                const stageData = job.stages[stage.id];
                                                return (
                                                    <Step key={stage.id} completed={stageData.status === 'completed'}>
                                                        <StepLabel
                                                            error={stageData.status === 'failed'}
                                                            StepIconComponent={() => <StageStatusIcon status={stageData.status} />}
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
                        <Typography variant="h6" fontWeight="bold">Recent Completed Analyses</Typography>
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
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {completedJobs.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                                            <Typography variant="body2" color="textSecondary">
                                                No completed jobs found
                                            </Typography>
                                        </TableCell>
                                    </TableRow>
                                ) : completedJobs.map((job) => (
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
                                    </TableRow>
                                ))}
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
        </Box>
    );
};

export default PipelineStatusPreview;
