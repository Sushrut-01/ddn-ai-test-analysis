/**
 * Code Fix Approval Component
 * PHASE B: Task B.4
 *
 * Displays AI-proposed code fixes with approve/reject functionality
 *
 * Features:
 * - Fix metadata (confidence, category, files affected)
 * - Before/After code diff view
 * - Three action buttons: Approve, Reject, Request Feedback
 * - PR status tracking after approval
 * - Loading states and error handling
 *
 * Usage:
 *   <CodeFixApproval
 *     analysisId={123}
 *     fixData={fixData}
 *     onApprove={handleApprove}
 *     onReject={handleReject}
 *     onFeedback={handleFeedback}
 *   />
 */

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  ButtonGroup,
  Chip,
  Alert,
  CircularProgress,
  LinearProgress,
  Divider,
  Collapse,
  IconButton,
  Link,
  Tooltip
} from '@mui/material';
import {
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Feedback as FeedbackIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Code as CodeIcon,
  BugReport as BugIcon,
  Build as BuildIcon,
  Category as CategoryIcon,
  Speed as ConfidenceIcon,
  GitHub as GitHubIcon,
  OpenInNew as ExternalLinkIcon
} from '@mui/icons-material';

import DiffView from './DiffView';

/**
 * CodeFixApproval Component
 */
const CodeFixApproval = ({
  analysisId,
  fixData,
  onApprove,
  onReject,
  onFeedback,
  prStatus = null,  // PR status after approval {pr_number, pr_url, status}
  disabled = false
}) => {
  // State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(true);
  const [showDiff, setShowDiff] = useState(true);

  // Extract fix data
  const {
    error_type,
    error_category,
    error_message,
    component,
    file_path,
    line_number,
    root_cause,
    fix_recommendation,
    severity,
    confidence_score,
    github_files,
    build_id
  } = fixData || {};

  // Calculate confidence percentage
  const confidencePercent = Math.round((confidence_score || 0) * 100);

  // Get confidence color
  const getConfidenceColor = (score) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  // Get severity color
  const getSeverityColor = (sev) => {
    const severityLower = (sev || '').toLowerCase();
    if (severityLower === 'critical') return 'error';
    if (severityLower === 'high') return 'warning';
    if (severityLower === 'medium') return 'info';
    return 'default';
  };

  // Handle approve action
  const handleApproveClick = async () => {
    setLoading(true);
    setError(null);

    try {
      await onApprove(analysisId);
    } catch (err) {
      setError(err.message || 'Failed to approve fix');
    } finally {
      setLoading(false);
    }
  };

  // Handle reject action
  const handleRejectClick = async () => {
    setLoading(true);
    setError(null);

    try {
      await onReject(analysisId);
    } catch (err) {
      setError(err.message || 'Failed to reject fix');
    } finally {
      setLoading(false);
    }
  };

  // Handle feedback action
  const handleFeedbackClick = async () => {
    setLoading(true);
    setError(null);

    try {
      await onFeedback(analysisId);
    } catch (err) {
      setError(err.message || 'Failed to request feedback');
    } finally {
      setLoading(false);
    }
  };

  // Get original and fixed code
  const getCodeSnippets = () => {
    // Original code from github_files
    let originalCode = '';
    if (github_files && github_files.length > 0) {
      originalCode = github_files[0].content || '';
    }

    // Fixed code from fix_recommendation
    // Try to extract code block from markdown
    const codeBlockMatch = fix_recommendation?.match(/```[\w]*\n([\s\S]*?)\n```/);
    let fixedCode = '';

    if (codeBlockMatch) {
      fixedCode = codeBlockMatch[1];
    } else {
      // If no code block, use the recommendation text
      fixedCode = fix_recommendation || '';
    }

    return { originalCode, fixedCode };
  };

  const { originalCode, fixedCode } = getCodeSnippets();

  if (!fixData) {
    return (
      <Alert severity="info">
        No fix recommendation available for this analysis.
      </Alert>
    );
  }

  return (
    <Paper elevation={3} sx={{ mt: 2, mb: 2 }}>
      {/* Loading bar */}
      {loading && <LinearProgress />}

      {/* Header */}
      <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <BuildIcon />
            <Typography variant="h6">
              Proposed Code Fix
            </Typography>
            {prStatus && (
              <Chip
                size="small"
                label={`PR #${prStatus.pr_number}`}
                color="success"
                sx={{ ml: 2 }}
              />
            )}
          </Box>
          <IconButton
            size="small"
            onClick={() => setExpanded(!expanded)}
            sx={{ color: 'white' }}
          >
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
      </Box>

      <Collapse in={expanded}>
        <Box sx={{ p: 3 }}>
          {/* Error display */}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Fix Metadata Cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {/* Confidence Score */}
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <ConfidenceIcon color={getConfidenceColor(confidence_score)} />
                    <Typography variant="subtitle2" color="text.secondary">
                      AI Confidence
                    </Typography>
                  </Box>
                  <Typography variant="h4" color={getConfidenceColor(confidence_score) + '.main'}>
                    {confidencePercent}%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={confidencePercent}
                    color={getConfidenceColor(confidence_score)}
                    sx={{ mt: 1 }}
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* Error Category */}
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <CategoryIcon color="primary" />
                    <Typography variant="subtitle2" color="text.secondary">
                      Category
                    </Typography>
                  </Box>
                  <Typography variant="h6">
                    {error_category}
                  </Typography>
                  <Chip
                    label={severity}
                    size="small"
                    color={getSeverityColor(severity)}
                    sx={{ mt: 1 }}
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* Files Affected */}
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <CodeIcon color="primary" />
                    <Typography variant="subtitle2" color="text.secondary">
                      Files Affected
                    </Typography>
                  </Box>
                  <Typography variant="h4">
                    1
                  </Typography>
                  <Tooltip title={file_path}>
                    <Typography variant="body2" color="text.secondary" noWrap>
                      {file_path?.split('/').pop()}
                    </Typography>
                  </Tooltip>
                </CardContent>
              </Card>
            </Grid>

            {/* Build Info */}
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <BugIcon color="error" />
                    <Typography variant="subtitle2" color="text.secondary">
                      Build ID
                    </Typography>
                  </Box>
                  <Typography variant="h6" noWrap>
                    {build_id}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" noWrap>
                    Line {line_number}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          {/* Error Summary */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Error Summary
            </Typography>
            <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                {error_type}
              </Typography>
              <Typography variant="body2">
                {error_message}
              </Typography>
            </Box>
          </Box>

          {/* Root Cause Analysis */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Root Cause Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {root_cause}
            </Typography>
          </Box>

          {/* Fix Recommendation */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recommended Fix
            </Typography>
            <Box sx={{ bgcolor: 'success.50', p: 2, borderRadius: 1, border: '1px solid', borderColor: 'success.200' }}>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                {fix_recommendation}
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Code Diff View */}
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">
                Code Changes
              </Typography>
              <Button
                size="small"
                onClick={() => setShowDiff(!showDiff)}
                startIcon={showDiff ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              >
                {showDiff ? 'Hide Diff' : 'Show Diff'}
              </Button>
            </Box>

            <Collapse in={showDiff}>
              <DiffView
                beforeCode={originalCode}
                afterCode={fixedCode}
                filePath={file_path}
                errorLine={line_number}
                language="auto"
              />
            </Collapse>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* PR Status (if PR created) */}
          {prStatus && (
            <Box sx={{ mb: 3 }}>
              <Alert
                severity="success"
                icon={<GitHubIcon />}
                action={
                  <Button
                    color="inherit"
                    size="small"
                    endIcon={<ExternalLinkIcon />}
                    component={Link}
                    href={prStatus.pr_url}
                    target="_blank"
                    rel="noopener"
                  >
                    View PR
                  </Button>
                }
              >
                <Typography variant="subtitle2">
                  Pull Request Created: #{prStatus.pr_number}
                </Typography>
                <Typography variant="body2">
                  Status: {prStatus.status || 'open'}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {prStatus.pr_url}
                </Typography>
              </Alert>
            </Box>
          )}

          {/* Action Buttons */}
          {!prStatus && (
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 4 }}>
              <ButtonGroup variant="contained" size="large" disabled={disabled || loading}>
                {/* Approve Button */}
                <Button
                  color="success"
                  startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <ApproveIcon />}
                  onClick={handleApproveClick}
                  disabled={disabled || loading}
                  sx={{ minWidth: 150 }}
                >
                  {loading ? 'Approving...' : 'Approve & Create PR'}
                </Button>

                {/* Reject Button */}
                <Button
                  color="error"
                  startIcon={<RejectIcon />}
                  onClick={handleRejectClick}
                  disabled={disabled || loading}
                  sx={{ minWidth: 120 }}
                >
                  Reject Fix
                </Button>

                {/* Request Feedback Button */}
                <Button
                  color="warning"
                  startIcon={<FeedbackIcon />}
                  onClick={handleFeedbackClick}
                  disabled={disabled || loading}
                  sx={{ minWidth: 150 }}
                >
                  Request Changes
                </Button>
              </ButtonGroup>
            </Box>
          )}

          {/* Help Text */}
          {!prStatus && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="body2" color="text.secondary" align="center">
                <strong>Approve:</strong> Creates a GitHub PR with this fix for review
                {' · '}
                <strong>Reject:</strong> Discards this fix recommendation
                {' · '}
                <strong>Request Changes:</strong> Ask AI to refine the fix
              </Typography>
            </Box>
          )}

          {/* Warning */}
          {confidencePercent < 70 && !prStatus && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Low Confidence Warning
              </Typography>
              <Typography variant="body2">
                The AI confidence for this fix is below 70%. Please carefully review the proposed changes before approving.
                Consider requesting changes or manual review instead.
              </Typography>
            </Alert>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
};

export default CodeFixApproval;
