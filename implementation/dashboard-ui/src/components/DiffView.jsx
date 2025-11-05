/**
 * DiffView Component
 * PHASE B: Task B.5
 *
 * Shows before/after code comparison with syntax highlighting
 *
 * Features:
 * - Side-by-side diff view
 * - Syntax highlighting for multiple languages
 * - Line-by-line diff highlighting (red=removed, green=added, yellow=modified)
 * - Line numbers aligned
 * - Collapsible file header
 * - Error line highlighting
 *
 * Usage:
 *   <DiffView
 *     beforeCode="original code"
 *     afterCode="fixed code"
 *     filePath="src/main.js"
 *     errorLine={42}
 *     language="javascript"
 *   />
 */

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Collapse,
  IconButton,
  Chip,
  Divider
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Remove as RemoveIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Folder as FolderIcon
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

/**
 * DiffView Component
 */
const DiffView = ({
  beforeCode = '',
  afterCode = '',
  filePath = 'unknown',
  errorLine = null,
  language = 'auto',
  showLineNumbers = true,
  expanded = true
}) => {
  const [isExpanded, setIsExpanded] = useState(expanded);

  // Detect language from file extension if 'auto'
  const detectLanguage = (path, languageProp) => {
    if (languageProp !== 'auto') return languageProp;

    const ext = path.split('.').pop().toLowerCase();
    const languageMap = {
      'js': 'javascript',
      'jsx': 'jsx',
      'ts': 'typescript',
      'tsx': 'tsx',
      'py': 'python',
      'java': 'java',
      'c': 'c',
      'cpp': 'cpp',
      'cs': 'csharp',
      'go': 'go',
      'rs': 'rust',
      'rb': 'ruby',
      'php': 'php',
      'swift': 'swift',
      'kt': 'kotlin',
      'sql': 'sql',
      'sh': 'bash',
      'yaml': 'yaml',
      'yml': 'yaml',
      'json': 'json',
      'xml': 'xml',
      'html': 'html',
      'css': 'css',
      'md': 'markdown'
    };

    return languageMap[ext] || 'javascript';
  };

  const detectedLanguage = detectLanguage(filePath, language);

  // Split code into lines
  const beforeLines = beforeCode.split('\n');
  const afterLines = afterCode.split('\n');

  // Calculate diff statistics
  const calculateDiffStats = () => {
    let linesAdded = 0;
    let linesRemoved = 0;
    let linesModified = 0;

    const maxLines = Math.max(beforeLines.length, afterLines.length);

    for (let i = 0; i < maxLines; i++) {
      const beforeLine = beforeLines[i] || '';
      const afterLine = afterLines[i] || '';

      if (beforeLine === '' && afterLine !== '') {
        linesAdded++;
      } else if (beforeLine !== '' && afterLine === '') {
        linesRemoved++;
      } else if (beforeLine !== afterLine) {
        linesModified++;
      }
    }

    return { linesAdded, linesRemoved, linesModified };
  };

  const stats = calculateDiffStats();

  // Get file name from path
  const fileName = filePath.split('/').pop();

  // Custom line number component
  const LineNumberComponent = ({ lineNumber, isError, diffType }) => {
    let bgcolor = 'transparent';
    let color = 'text.secondary';

    if (isError) {
      bgcolor = 'error.light';
      color = 'error.contrastText';
    } else if (diffType === 'added') {
      bgcolor = 'success.light';
      color = 'success.contrastText';
    } else if (diffType === 'removed') {
      bgcolor = 'error.light';
      color = 'error.contrastText';
    } else if (diffType === 'modified') {
      bgcolor = 'warning.light';
      color = 'warning.contrastText';
    }

    return (
      <Box
        sx={{
          display: 'inline-block',
          minWidth: '40px',
          px: 1,
          py: 0.25,
          textAlign: 'right',
          fontSize: '0.75rem',
          fontFamily: 'monospace',
          bgcolor,
          color,
          borderRight: '1px solid',
          borderColor: 'divider',
          userSelect: 'none'
        }}
      >
        {lineNumber}
      </Box>
    );
  };

  // Custom code line component with diff highlighting
  const CodeLineComponent = ({ code, lineNumber, diffType, isError }) => {
    let bgcolor = 'transparent';
    let borderLeft = 'none';

    if (isError) {
      bgcolor = 'error.light';
      borderLeft = '3px solid';
      borderLeftColor = 'error.main';
    } else if (diffType === 'added') {
      bgcolor = 'rgba(76, 175, 80, 0.1)';
      borderLeft = '3px solid';
      borderLeftColor = 'success.main';
    } else if (diffType === 'removed') {
      bgcolor = 'rgba(244, 67, 54, 0.1)';
      borderLeft = '3px solid';
      borderLeftColor = 'error.main';
    } else if (diffType === 'modified') {
      bgcolor = 'rgba(255, 152, 0, 0.1)';
      borderLeft = '3px solid';
      borderLeftColor = 'warning.main';
    }

    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'flex-start',
          bgcolor,
          borderLeft,
          borderLeftColor,
          '&:hover': {
            bgcolor: diffType === 'none' ? 'action.hover' : bgcolor
          }
        }}
      >
        <LineNumberComponent lineNumber={lineNumber} isError={isError} diffType={diffType} />
        <Box
          sx={{
            flex: 1,
            px: 1,
            py: 0.25,
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            whiteSpace: 'pre',
            overflow: 'auto'
          }}
        >
          {code || ' '}
        </Box>
      </Box>
    );
  };

  // Determine diff type for each line
  const getDiffType = (beforeLine, afterLine) => {
    if (beforeLine === '' && afterLine !== '') return 'added';
    if (beforeLine !== '' && afterLine === '') return 'removed';
    if (beforeLine !== afterLine) return 'modified';
    return 'none';
  };

  return (
    <Paper elevation={2} sx={{ overflow: 'hidden' }}>
      {/* File Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 1.5,
          bgcolor: 'grey.200',
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FolderIcon fontSize="small" color="primary" />
          <Typography variant="subtitle2" fontFamily="monospace">
            {filePath}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Diff Statistics */}
          {stats.linesAdded > 0 && (
            <Chip
              icon={<AddIcon />}
              label={`+${stats.linesAdded}`}
              size="small"
              color="success"
              variant="outlined"
            />
          )}
          {stats.linesRemoved > 0 && (
            <Chip
              icon={<RemoveIcon />}
              label={`-${stats.linesRemoved}`}
              size="small"
              color="error"
              variant="outlined"
            />
          )}
          {stats.linesModified > 0 && (
            <Chip
              icon={<EditIcon />}
              label={`~${stats.linesModified}`}
              size="small"
              color="warning"
              variant="outlined"
            />
          )}

          {/* Expand/Collapse */}
          <IconButton
            size="small"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
      </Box>

      <Collapse in={isExpanded}>
        {/* Side-by-Side Diff */}
        <Grid container>
          {/* BEFORE (Original Code) */}
          <Grid item xs={12} md={6} sx={{ borderRight: { md: '1px solid' }, borderColor: 'divider' }}>
            <Box sx={{ bgcolor: 'grey.100', p: 1, borderBottom: '1px solid', borderColor: 'divider' }}>
              <Typography variant="caption" fontWeight="bold" color="error">
                BEFORE (Original)
              </Typography>
            </Box>
            <Box sx={{ maxHeight: 400, overflow: 'auto', bgcolor: 'grey.50' }}>
              {beforeLines.map((line, index) => {
                const lineNumber = index + 1;
                const afterLine = afterLines[index] || '';
                const diffType = getDiffType(line, afterLine);
                const isError = errorLine === lineNumber;

                return (
                  <CodeLineComponent
                    key={`before-${index}`}
                    code={line}
                    lineNumber={lineNumber}
                    diffType={diffType === 'added' ? 'none' : diffType}
                    isError={isError}
                  />
                );
              })}
            </Box>
          </Grid>

          {/* AFTER (Fixed Code) */}
          <Grid item xs={12} md={6}>
            <Box sx={{ bgcolor: 'grey.100', p: 1, borderBottom: '1px solid', borderColor: 'divider' }}>
              <Typography variant="caption" fontWeight="bold" color="success">
                AFTER (Fixed)
              </Typography>
            </Box>
            <Box sx={{ maxHeight: 400, overflow: 'auto', bgcolor: 'grey.50' }}>
              {afterLines.map((line, index) => {
                const lineNumber = index + 1;
                const beforeLine = beforeLines[index] || '';
                const diffType = getDiffType(beforeLine, line);
                const isError = errorLine === lineNumber;

                return (
                  <CodeLineComponent
                    key={`after-${index}`}
                    code={line}
                    lineNumber={lineNumber}
                    diffType={diffType === 'removed' ? 'none' : diffType}
                    isError={isError}
                  />
                );
              })}
            </Box>
          </Grid>
        </Grid>

        <Divider />

        {/* Syntax Highlighted Preview (Optional - can be toggled) */}
        <Box sx={{ p: 2, bgcolor: 'grey.900' }}>
          <Typography variant="caption" sx={{ color: 'grey.400', mb: 1, display: 'block' }}>
            Fixed Code Preview (Syntax Highlighted)
          </Typography>
          <SyntaxHighlighter
            language={detectedLanguage}
            style={vscDarkPlus}
            showLineNumbers={showLineNumbers}
            wrapLines={true}
            customStyle={{
              margin: 0,
              borderRadius: '4px',
              fontSize: '0.875rem',
              maxHeight: '300px'
            }}
            lineNumberStyle={{
              minWidth: '3em',
              paddingRight: '1em',
              color: '#858585',
              textAlign: 'right',
              userSelect: 'none'
            }}
          >
            {afterCode}
          </SyntaxHighlighter>
        </Box>
      </Collapse>
    </Paper>
  );
};

export default DiffView;
