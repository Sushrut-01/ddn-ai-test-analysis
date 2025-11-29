import React, { useState, useEffect } from 'react';
import {
    Box, Container, Paper, Typography, Grid, Button, Chip, Avatar,
    Tabs, Tab, Divider, Alert, IconButton, Tooltip, LinearProgress,
    Dialog, DialogTitle, DialogContent, DialogActions, TextField,
    CircularProgress, Snackbar, Skeleton
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import EditIcon from '@mui/icons-material/Edit';
import BugReportIcon from '@mui/icons-material/BugReport';
import CodeIcon from '@mui/icons-material/Code';
import GitHubIcon from '@mui/icons-material/GitHub';
import BuildIcon from '@mui/icons-material/Build';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import CompareIcon from '@mui/icons-material/Compare';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import WarningIcon from '@mui/icons-material/Warning';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import TerminalIcon from '@mui/icons-material/Terminal';
import DescriptionIcon from '@mui/icons-material/Description';
import AssessmentIcon from '@mui/icons-material/Assessment';
import FolderIcon from '@mui/icons-material/Folder';
import RefreshIcon from '@mui/icons-material/Refresh';
import SendIcon from '@mui/icons-material/Send';
import HistoryIcon from '@mui/icons-material/History';
import { useNavigate, useParams } from 'react-router-dom';
import { failuresAPI } from '../services/api';

const TabPanel = ({ children, value, index }) => (
    <div role="tabpanel" hidden={value !== index}>
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
);

// Quick Access Button Component
const QuickAccessButton = ({ icon, label, url, color }) => (
    <Button
        variant="contained"
        startIcon={icon}
        endIcon={<OpenInNewIcon sx={{ fontSize: 14 }} />}
        onClick={() => window.open(url, '_blank')}
        sx={{
            bgcolor: color,
            '&:hover': { bgcolor: alpha(color, 0.85) },
            borderRadius: 2,
            textTransform: 'none',
            fontWeight: 500,
            fontSize: '0.8rem',
            py: 1
        }}
    >
        {label}
    </Button>
);

const FailureDetailsPreview = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const [tabValue, setTabValue] = useState(0);
    const [feedbackStatus, setFeedbackStatus] = useState(null);
    const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false);
    const [feedbackType, setFeedbackType] = useState(null); // 'reject' or 'refine'
    const [feedbackText, setFeedbackText] = useState('');
    const [isReanalyzing, setIsReanalyzing] = useState(false);
    const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
    const [analysisHistory, setAnalysisHistory] = useState([]);

    // Real data state
    const [loading, setLoading] = useState(true);
    const [failure, setFailure] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchFailureDetails = async () => {
            if (!id) {
                setError('No failure ID provided');
                setLoading(false);
                return;
            }
            try {
                setLoading(true);
                const response = await failuresAPI.getDetails(id);
                const data = response?.data || response;
                setFailure(data);
                setError(null);
            } catch (err) {
                console.error('Error fetching failure details:', err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchFailureDetails();
    }, [id]);

    // Calculate aging days
    const getAgingDays = (timestamp) => {
        if (!timestamp) return 0;
        const date = new Date(timestamp);
        const now = new Date();
        return Math.ceil(Math.abs(now - date) / (1000 * 60 * 60 * 24));
    };

    // Loading state
    if (loading) {
        return (
            <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc', p: 4 }}>
                <Container maxWidth="xl">
                    <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 4, mb: 3 }} />
                    <Grid container spacing={3}>
                        <Grid item xs={12} lg={8}>
                            <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 4, mb: 3 }} />
                            <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 4 }} />
                        </Grid>
                        <Grid item xs={12} lg={4}>
                            <Skeleton variant="rectangular" height={250} sx={{ borderRadius: 4 }} />
                        </Grid>
                    </Grid>
                </Container>
            </Box>
        );
    }

    // Error state
    if (error || !failure) {
        return (
            <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc', p: 4 }}>
                <Container maxWidth="xl">
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error || 'Failed to load failure details'}
                    </Alert>
                    <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/failures')}>
                        Back to Failures
                    </Button>
                </Container>
            </Box>
        );
    }

    // Build failure object from API data
    const buildId = failure.build_id || failure.buildId || id;
    const jobName = failure.job_name || failure.jobName || '-';
    const testName = failure.test_name || failure.testName || '-';
    const timestamp = failure.timestamp || new Date().toISOString();
    const agingDays = getAgingDays(timestamp);
    const errorMessage = failure.error_message || failure.stack_trace || 'No error message available';
    const stackTrace = failure.stack_trace || failure.error_message || 'No stack trace available';

    // Build analysis object (may not exist for all failures)
    const analysis = failure.analysis || {
        classification: failure.classification || 'PENDING',
        confidence_score: failure.confidence || 0,
        severity: failure.severity || 'UNKNOWN',
        root_cause: failure.root_cause || 'Analysis not yet available. Click "Request Analysis" to analyze this failure.',
        recommendation: failure.recommendation || 'No recommendations available yet.',
        before_code: '',
        after_code: '',
        analyzed_at: failure.analyzed_at,
        ai_model: 'Gemini',
        similar_cases: []
    };

    // Build external links (generate from build info)
    const jenkinsBaseUrl = 'http://localhost:8081';
    const jenkins_build_url = `${jenkinsBaseUrl}/job/${jobName}/${failure.build_number || buildId}/`;
    const jenkins_console_url = `${jenkins_build_url}console`;

    const handleAccept = () => {
        setFeedbackStatus('accepted');
        setSnackbar({ open: true, message: 'Analysis accepted! Thank you for your validation.', severity: 'success' });
    };

    const handleRejectClick = () => {
        setFeedbackType('reject');
        setFeedbackDialogOpen(true);
    };

    const handleRefineClick = () => {
        setFeedbackType('refine');
        setFeedbackDialogOpen(true);
    };

    const handleFeedbackSubmit = () => {
        if (!feedbackText.trim()) {
            setSnackbar({ open: true, message: 'Please provide feedback for the AI to improve.', severity: 'warning' });
            return;
        }

        setFeedbackDialogOpen(false);

        if (feedbackType === 'reject') {
            setFeedbackStatus('rejected');
            // Start re-analysis
            setIsReanalyzing(true);
            setSnackbar({ open: true, message: 'Feedback submitted. AI is re-analyzing with your input...', severity: 'info' });

            // Simulate re-analysis
            setTimeout(() => {
                setIsReanalyzing(false);
                setFeedbackStatus('refined');
                setAnalysisHistory([...analysisHistory, { type: 'reject', feedback: feedbackText, timestamp: new Date() }]);
                setSnackbar({ open: true, message: 'Re-analysis complete! Please review the updated analysis.', severity: 'success' });
            }, 3000);
        } else {
            setFeedbackStatus('refining');
            setIsReanalyzing(true);
            setSnackbar({ open: true, message: 'Refinement requested. AI is improving the analysis...', severity: 'info' });

            // Simulate refinement
            setTimeout(() => {
                setIsReanalyzing(false);
                setFeedbackStatus('refined');
                setAnalysisHistory([...analysisHistory, { type: 'refine', feedback: feedbackText, timestamp: new Date() }]);
                setSnackbar({ open: true, message: 'Analysis refined! Please review the improvements.', severity: 'success' });
            }, 3000);
        }

        setFeedbackText('');
    };

    const handleDialogClose = () => {
        setFeedbackDialogOpen(false);
        setFeedbackText('');
    };

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc', pb: 4 }}>
            {/* Header */}
            <Box
                sx={{
                    background: 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)',
                    pt: 3,
                    pb: 6,
                    px: 3,
                    color: 'white',
                    borderBottomLeftRadius: 48,
                    borderBottomRightRadius: 48,
                    mb: -3
                }}
            >
                <Container maxWidth="xl">
                    <Button
                        startIcon={<ArrowBackIcon />}
                        onClick={() => navigate('/failures-preview')}
                        sx={{ color: 'white', mb: 2, '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}
                    >
                        Back to Failures
                    </Button>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                        <Box>
                            <Typography variant="h4" fontWeight="bold" gutterBottom>
                                Failure Details: {buildId}
                            </Typography>
                            <Box display="flex" gap={2} flexWrap="wrap">
                                <Chip label={jobName} sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }} />
                                <Chip label={`${agingDays} days old`} sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }} />
                                <Chip
                                    icon={<SmartToyIcon sx={{ color: 'white !important' }} />}
                                    label={`AI Confidence: ${Math.round(analysis.confidence_score * 100)}%`}
                                    sx={{ bgcolor: '#10b981', color: 'white' }}
                                />
                                {analysisHistory.length > 0 && (
                                    <Chip
                                        icon={<HistoryIcon sx={{ color: 'white !important' }} />}
                                        label={`${analysisHistory.length} Refinement(s)`}
                                        sx={{ bgcolor: '#8b5cf6', color: 'white' }}
                                    />
                                )}
                            </Box>
                        </Box>
                    </Box>
                </Container>
            </Box>

            <Container maxWidth="xl">
                {/* Quick Access Links - IMPORTANT for user verification */}
                <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', bgcolor: '#f0f9ff', border: '1px solid #bae6fd' }}>
                    <Box display="flex" alignItems="center" gap={2} mb={2}>
                        <Avatar sx={{ bgcolor: '#0284c7', width: 40, height: 40 }}>
                            <OpenInNewIcon />
                        </Avatar>
                        <Box>
                            <Typography variant="h6" fontWeight="bold" color="#0c4a6e">
                                Verify Before Approving
                            </Typography>
                            <Typography variant="body2" color="#0369a1">
                                Check these sources to confirm the AI analysis is correct
                            </Typography>
                        </Box>
                    </Box>

                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <Typography variant="subtitle2" color="#0c4a6e" fontWeight={600} mb={1}>
                                Source Code
                            </Typography>
                            <Box display="flex" gap={1.5} flexWrap="wrap">
                                <QuickAccessButton
                                    icon={<GitHubIcon />}
                                    label="Test Case File"
                                    url={failure.github_test_url || '#'}
                                    color="#24292e"
                                />
                                <QuickAccessButton
                                    icon={<CodeIcon />}
                                    label="Source Code"
                                    url={failure.github_source_url || '#'}
                                    color="#6e5494"
                                />
                            </Box>
                        </Grid>

                        <Grid item xs={12}>
                            <Typography variant="subtitle2" color="#0c4a6e" fontWeight={600} mb={1}>
                                Jenkins
                            </Typography>
                            <Box display="flex" gap={1.5} flexWrap="wrap">
                                <QuickAccessButton
                                    icon={<BuildIcon />}
                                    label="Build Page"
                                    url={jenkins_build_url}
                                    color="#D24939"
                                />
                                <QuickAccessButton
                                    icon={<TerminalIcon />}
                                    label="Console Output"
                                    url={jenkins_console_url}
                                    color="#1e3a5f"
                                />
                                <QuickAccessButton
                                    icon={<AssessmentIcon />}
                                    label="Test Report"
                                    url={`${jenkins_build_url}testReport/`}
                                    color="#0891b2"
                                />
                                <QuickAccessButton
                                    icon={<DescriptionIcon />}
                                    label="XML Report"
                                    url={`${jenkins_build_url}testReport/junit.xml`}
                                    color="#059669"
                                />
                            </Box>
                        </Grid>

                        <Grid item xs={12}>
                            <Typography variant="subtitle2" color="#0c4a6e" fontWeight={600} mb={1}>
                                Reports & Artifacts
                            </Typography>
                            <Box display="flex" gap={1.5} flexWrap="wrap">
                                <QuickAccessButton
                                    icon={<AssessmentIcon />}
                                    label="Allure Report"
                                    url={failure.allure_report_url || `${jenkins_build_url}allure/`}
                                    color="#f59e0b"
                                />
                                <QuickAccessButton
                                    icon={<FolderIcon />}
                                    label="Build Artifacts"
                                    url={`${jenkins_build_url}artifact/`}
                                    color="#8b5cf6"
                                />
                            </Box>
                        </Grid>
                    </Grid>
                </Paper>

                {/* Re-analysis Progress */}
                {isReanalyzing && (
                    <Alert
                        severity="info"
                        sx={{ mb: 3, borderRadius: 3 }}
                        icon={<CircularProgress size={20} />}
                    >
                        <Typography variant="subtitle2" fontWeight={600}>
                            AI Re-Analysis in Progress
                        </Typography>
                        <Typography variant="body2">
                            The AI is re-analyzing this failure with your feedback. Please wait...
                        </Typography>
                        <LinearProgress sx={{ mt: 1, borderRadius: 2 }} />
                    </Alert>
                )}

                <Grid container spacing={3}>
                    {/* Left Column - Error & Analysis */}
                    <Grid item xs={12} lg={8}>
                        {/* Error Message */}
                        <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                            <Box display="flex" alignItems="center" gap={2} mb={2}>
                                <Avatar sx={{ bgcolor: alpha('#ef4444', 0.1), color: '#ef4444' }}>
                                    <BugReportIcon />
                                </Avatar>
                                <Typography variant="h6" fontWeight="bold">Error Message</Typography>
                            </Box>
                            <Paper sx={{ p: 2, bgcolor: '#fef2f2', border: '1px solid #fecaca', borderRadius: 2 }}>
                                <Typography variant="body2" fontFamily="monospace" sx={{ whiteSpace: 'pre-wrap', color: '#991b1b' }}>
                                    {errorMessage}
                                </Typography>
                            </Paper>
                        </Paper>

                        {/* AI Root Cause Analysis */}
                        <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                            <Box display="flex" alignItems="center" gap={2} mb={2}>
                                <Avatar sx={{ bgcolor: alpha('#10b981', 0.1), color: '#10b981' }}>
                                    <LightbulbIcon />
                                </Avatar>
                                <Typography variant="h6" fontWeight="bold">AI Root Cause Analysis</Typography>
                                <Chip label={analysis.classification} size="small" sx={{ bgcolor: alpha('#f59e0b', 0.1), color: '#b45309' }} />
                                {feedbackStatus === 'refined' && (
                                    <Chip label="REFINED" size="small" sx={{ bgcolor: '#8b5cf6', color: 'white' }} />
                                )}
                            </Box>
                            <Paper sx={{ p: 2, bgcolor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 2 }}>
                                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', color: '#166534' }}>
                                    {analysis.root_cause}
                                </Typography>
                            </Paper>
                        </Paper>

                        {/* AI Fix Recommendation */}
                        <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                            <Box display="flex" alignItems="center" gap={2} mb={2}>
                                <Avatar sx={{ bgcolor: alpha('#3b82f6', 0.1), color: '#3b82f6' }}>
                                    <CodeIcon />
                                </Avatar>
                                <Typography variant="h6" fontWeight="bold">AI Fix Recommendation</Typography>
                            </Box>
                            <Paper sx={{ p: 2, bgcolor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 2 }}>
                                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', color: '#1e40af' }}>
                                    {analysis.recommendation}
                                </Typography>
                            </Paper>
                        </Paper>

                        {/* Before/After Code Comparison */}
                        <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                            <Box display="flex" alignItems="center" gap={2} mb={3}>
                                <Avatar sx={{ bgcolor: alpha('#8b5cf6', 0.1), color: '#8b5cf6' }}>
                                    <CompareIcon />
                                </Avatar>
                                <Typography variant="h6" fontWeight="bold">Before / After Code Comparison</Typography>
                            </Box>

                            <Grid container spacing={2}>
                                {/* Before Code */}
                                <Grid item xs={12} md={6}>
                                    <Box>
                                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                                            <Chip label="BEFORE (Error)" size="small" sx={{ bgcolor: '#fee2e2', color: '#991b1b', fontWeight: 600 }} />
                                            <Tooltip title="Copy code">
                                                <IconButton size="small"><ContentCopyIcon fontSize="small" /></IconButton>
                                            </Tooltip>
                                        </Box>
                                        <Paper
                                            sx={{
                                                p: 2,
                                                bgcolor: '#1e1e1e',
                                                color: '#f87171',
                                                borderRadius: 2,
                                                border: '2px solid #ef4444',
                                                fontFamily: 'monospace',
                                                fontSize: '0.85rem',
                                                overflow: 'auto',
                                                maxHeight: 300
                                            }}
                                        >
                                            <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                                                {analysis.before_code}
                                            </pre>
                                        </Paper>
                                    </Box>
                                </Grid>

                                {/* After Code */}
                                <Grid item xs={12} md={6}>
                                    <Box>
                                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                                            <Chip label="AFTER (Fixed)" size="small" sx={{ bgcolor: '#dcfce7', color: '#166534', fontWeight: 600 }} />
                                            <Tooltip title="Copy code">
                                                <IconButton size="small"><ContentCopyIcon fontSize="small" /></IconButton>
                                            </Tooltip>
                                        </Box>
                                        <Paper
                                            sx={{
                                                p: 2,
                                                bgcolor: '#1e1e1e',
                                                color: '#4ade80',
                                                borderRadius: 2,
                                                border: '2px solid #10b981',
                                                fontFamily: 'monospace',
                                                fontSize: '0.85rem',
                                                overflow: 'auto',
                                                maxHeight: 300
                                            }}
                                        >
                                            <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                                                {analysis.after_code}
                                            </pre>
                                        </Paper>
                                    </Box>
                                </Grid>
                            </Grid>
                        </Paper>

                        {/* Stack Trace Tab View */}
                        <Paper elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', overflow: 'hidden' }}>
                            <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ borderBottom: '1px solid #e2e8f0', px: 2 }}>
                                <Tab label="Stack Trace" />
                                <Tab label="Full Failure Data" />
                                <Tab label="Similar Errors" />
                                {analysisHistory.length > 0 && <Tab label="Feedback History" />}
                            </Tabs>

                            <TabPanel value={tabValue} index={0}>
                                <Box sx={{ px: 2 }}>
                                    <Paper sx={{ p: 2, bgcolor: '#1e1e1e', color: '#e2e8f0', borderRadius: 2, maxHeight: 400, overflow: 'auto' }}>
                                        <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                                            {stackTrace}
                                        </pre>
                                    </Paper>
                                </Box>
                            </TabPanel>

                            <TabPanel value={tabValue} index={1}>
                                <Box sx={{ px: 2 }}>
                                    <Paper sx={{ p: 2, bgcolor: '#f8fafc', borderRadius: 2, maxHeight: 400, overflow: 'auto' }}>
                                        <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                                            {JSON.stringify(failure, null, 2)}
                                        </pre>
                                    </Paper>
                                </Box>
                            </TabPanel>

                            <TabPanel value={tabValue} index={2}>
                                <Box sx={{ px: 2 }}>
                                    {analysis.similar_cases.map((c, idx) => (
                                        <Paper key={idx} sx={{ p: 2, mb: 2, bgcolor: '#f8fafc', borderRadius: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <Box>
                                                <Typography variant="body2" fontWeight={600}>{c.title}</Typography>
                                                <Typography variant="caption" color="textSecondary">Case #{c.id}</Typography>
                                            </Box>
                                            <Chip label={`${Math.round(c.similarity * 100)}% similar`} size="small" color="primary" />
                                        </Paper>
                                    ))}
                                </Box>
                            </TabPanel>

                            {analysisHistory.length > 0 && (
                                <TabPanel value={tabValue} index={3}>
                                    <Box sx={{ px: 2 }}>
                                        {analysisHistory.map((item, idx) => (
                                            <Paper key={idx} sx={{ p: 2, mb: 2, bgcolor: item.type === 'reject' ? '#fef2f2' : '#fffbeb', borderRadius: 2 }}>
                                                <Box display="flex" alignItems="center" gap={1} mb={1}>
                                                    <Chip
                                                        label={item.type === 'reject' ? 'Rejected' : 'Refinement'}
                                                        size="small"
                                                        sx={{ bgcolor: item.type === 'reject' ? '#ef4444' : '#f59e0b', color: 'white' }}
                                                    />
                                                    <Typography variant="caption" color="textSecondary">
                                                        {item.timestamp.toLocaleString()}
                                                    </Typography>
                                                </Box>
                                                <Typography variant="body2">{item.feedback}</Typography>
                                            </Paper>
                                        ))}
                                    </Box>
                                </TabPanel>
                            )}
                        </Paper>
                    </Grid>

                    {/* Right Column - Actions & Info */}
                    <Grid item xs={12} lg={4}>
                        {/* Validation Actions */}
                        <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', border: '2px solid #e2e8f0' }}>
                            <Typography variant="h6" fontWeight="bold" mb={1}>Validate AI Analysis</Typography>
                            <Typography variant="body2" color="textSecondary" mb={3}>
                                Review the sources above, then approve or reject the analysis
                            </Typography>

                            {feedbackStatus && !isReanalyzing ? (
                                <Box>
                                    <Alert
                                        severity={feedbackStatus === 'accepted' ? 'success' : feedbackStatus === 'rejected' ? 'error' : feedbackStatus === 'refined' ? 'info' : 'warning'}
                                        icon={feedbackStatus === 'accepted' ? <CheckCircleIcon /> : feedbackStatus === 'rejected' ? <CancelIcon /> : <RefreshIcon />}
                                        sx={{ mb: 2 }}
                                    >
                                        {feedbackStatus === 'accepted' && 'Analysis approved and saved!'}
                                        {feedbackStatus === 'rejected' && 'Analysis rejected. Re-analysis requested.'}
                                        {feedbackStatus === 'refining' && 'Refinement in progress...'}
                                        {feedbackStatus === 'refined' && 'Analysis has been refined based on your feedback.'}
                                    </Alert>

                                    {feedbackStatus === 'refined' && (
                                        <Box display="flex" flexDirection="column" gap={2}>
                                            <Button
                                                variant="contained"
                                                fullWidth
                                                startIcon={<CheckCircleIcon />}
                                                onClick={handleAccept}
                                                sx={{ bgcolor: '#10b981', '&:hover': { bgcolor: '#059669' }, py: 1.5, borderRadius: 3 }}
                                            >
                                                Approve Refined Analysis
                                            </Button>
                                            <Button
                                                variant="outlined"
                                                fullWidth
                                                startIcon={<EditIcon />}
                                                onClick={handleRefineClick}
                                                sx={{ borderRadius: 3 }}
                                            >
                                                Request Further Refinement
                                            </Button>
                                        </Box>
                                    )}
                                </Box>
                            ) : !isReanalyzing && (
                                <Box display="flex" flexDirection="column" gap={2}>
                                    <Button
                                        variant="contained"
                                        fullWidth
                                        startIcon={<CheckCircleIcon />}
                                        onClick={handleAccept}
                                        sx={{ bgcolor: '#10b981', '&:hover': { bgcolor: '#059669' }, py: 1.5, borderRadius: 3 }}
                                    >
                                        Approve Analysis
                                    </Button>
                                    <Button
                                        variant="contained"
                                        fullWidth
                                        startIcon={<CancelIcon />}
                                        onClick={handleRejectClick}
                                        sx={{ bgcolor: '#ef4444', '&:hover': { bgcolor: '#dc2626' }, py: 1.5, borderRadius: 3 }}
                                    >
                                        Reject & Re-analyze
                                    </Button>
                                    <Button
                                        variant="contained"
                                        fullWidth
                                        startIcon={<EditIcon />}
                                        onClick={handleRefineClick}
                                        sx={{ bgcolor: '#f59e0b', '&:hover': { bgcolor: '#d97706' }, py: 1.5, borderRadius: 3 }}
                                    >
                                        Request Refinement
                                    </Button>
                                </Box>
                            )}
                        </Paper>

                        {/* Analysis Summary */}
                        <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                            <Typography variant="h6" fontWeight="bold" mb={2}>Analysis Summary</Typography>

                            <Box mb={3}>
                                <Typography variant="body2" color="textSecondary" mb={1}>Confidence Score</Typography>
                                <Box display="flex" alignItems="center" gap={2}>
                                    <Box flex={1}>
                                        <LinearProgress
                                            variant="determinate"
                                            value={analysis.confidence_score * 100}
                                            sx={{
                                                height: 10,
                                                borderRadius: 5,
                                                bgcolor: '#e2e8f0',
                                                '& .MuiLinearProgress-bar': { bgcolor: analysis.confidence_score >= 0.8 ? '#10b981' : '#f59e0b', borderRadius: 5 }
                                            }}
                                        />
                                    </Box>
                                    <Typography variant="h6" fontWeight="bold">{Math.round(analysis.confidence_score * 100)}%</Typography>
                                </Box>
                            </Box>

                            <Divider sx={{ my: 2 }} />

                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <Typography variant="body2" color="textSecondary">Classification</Typography>
                                    <Chip label={analysis.classification} size="small" sx={{ mt: 0.5, bgcolor: alpha('#f59e0b', 0.1), color: '#b45309' }} />
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="body2" color="textSecondary">Severity</Typography>
                                    <Chip
                                        icon={<WarningIcon />}
                                        label={analysis.severity}
                                        size="small"
                                        sx={{ mt: 0.5, bgcolor: analysis.severity === 'HIGH' ? '#fee2e2' : '#fef3c7', color: analysis.severity === 'HIGH' ? '#991b1b' : '#92400e' }}
                                    />
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="body2" color="textSecondary">AI Model</Typography>
                                    <Typography variant="body2" fontWeight={600}>{analysis.ai_model}</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="body2" color="textSecondary">Refinements</Typography>
                                    <Typography variant="body2" fontWeight={600}>{analysisHistory.length}</Typography>
                                </Grid>
                            </Grid>
                        </Paper>

                        {/* Test Info */}
                        <Paper elevation={0} sx={{ p: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                            <Typography variant="h6" fontWeight="bold" mb={2}>Test Information</Typography>

                            <Box mb={2}>
                                <Typography variant="body2" color="textSecondary">Test Name</Typography>
                                <Typography variant="body2" fontWeight={600}>{testName}</Typography>
                            </Box>
                            <Box mb={2}>
                                <Typography variant="body2" color="textSecondary">Job Name</Typography>
                                <Typography variant="body2" fontWeight={600}>{jobName}</Typography>
                            </Box>
                            <Box mb={2}>
                                <Typography variant="body2" color="textSecondary">Build Number</Typography>
                                <Typography variant="body2" fontFamily="monospace" fontWeight={600}>{failure.build_number || buildId}</Typography>
                            </Box>
                            <Box>
                                <Typography variant="body2" color="textSecondary">Failed On</Typography>
                                <Typography variant="body2" fontWeight={600}>{new Date(timestamp).toLocaleString()}</Typography>
                            </Box>
                        </Paper>
                    </Grid>
                </Grid>
            </Container>

            {/* Feedback Dialog */}
            <Dialog open={feedbackDialogOpen} onClose={handleDialogClose} maxWidth="sm" fullWidth>
                <DialogTitle sx={{ fontWeight: 600 }}>
                    {feedbackType === 'reject' ? 'Reject Analysis - Provide Feedback' : 'Request Refinement'}
                </DialogTitle>
                <DialogContent>
                    <Alert severity={feedbackType === 'reject' ? 'error' : 'warning'} sx={{ mb: 3 }}>
                        {feedbackType === 'reject'
                            ? 'The AI will re-analyze this failure using your feedback to improve accuracy.'
                            : 'Provide specific areas where the analysis should be improved.'}
                    </Alert>
                    <TextField
                        fullWidth
                        multiline
                        rows={5}
                        label="Your Feedback"
                        placeholder={feedbackType === 'reject'
                            ? "Explain why the analysis is incorrect. What is the actual root cause? What should the fix be?"
                            : "What aspects of the analysis need improvement? Be specific about what should change."}
                        value={feedbackText}
                        onChange={(e) => setFeedbackText(e.target.value)}
                        sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                    />
                    <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                        Your feedback helps the AI learn and provide better analysis in the future.
                    </Typography>
                </DialogContent>
                <DialogActions sx={{ p: 3 }}>
                    <Button onClick={handleDialogClose}>Cancel</Button>
                    <Button
                        variant="contained"
                        startIcon={<SendIcon />}
                        onClick={handleFeedbackSubmit}
                        sx={{
                            bgcolor: feedbackType === 'reject' ? '#ef4444' : '#f59e0b',
                            '&:hover': { bgcolor: feedbackType === 'reject' ? '#dc2626' : '#d97706' }
                        }}
                    >
                        {feedbackType === 'reject' ? 'Submit & Re-analyze' : 'Submit & Refine'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Snackbar */}
            <Snackbar
                open={snackbar.open}
                autoHideDuration={6000}
                onClose={() => setSnackbar({ ...snackbar, open: false })}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
                <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Box>
    );
};

export default FailureDetailsPreview;
