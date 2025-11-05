import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  Chip,
  Link,
  Collapse,
  Button
} from '@mui/material'
import {
  GitHub as GitHubIcon,
  ContentCopy as ContentCopyIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Code as CodeIcon,
  Link as LinkIcon
} from '@mui/icons-material'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

/**
 * CodeSnippet Component - Task 0E.7
 *
 * Displays GitHub source code with syntax highlighting, line numbers,
 * and error line highlighting for CODE_ERROR analysis.
 *
 * Props:
 * - fileData: object - GitHub file data from API
 *   {
 *     file_path: string,
 *     content: string,
 *     total_lines: number,
 *     line_range: string,
 *     sha: string,
 *     url: string,
 *     repo: string,
 *     branch: string
 *   }
 * - errorLine: number - Line number to highlight (optional)
 * - maxHeight: number - Maximum height in pixels (default: 500)
 * - defaultExpanded: boolean - Whether to start expanded (default: true)
 * - showHeader: boolean - Whether to show file header (default: true)
 */
function CodeSnippet({
  fileData,
  errorLine = null,
  maxHeight = 500,
  defaultExpanded = true,
  showHeader = true
}) {
  const [expanded, setExpanded] = useState(defaultExpanded)
  const [copied, setCopied] = useState(false)

  if (!fileData || !fileData.content) {
    return null
  }

  // Extract language from file extension
  const getLanguage = (filePath) => {
    const ext = filePath.split('.').pop().toLowerCase()
    const languageMap = {
      'js': 'javascript',
      'jsx': 'jsx',
      'ts': 'typescript',
      'tsx': 'tsx',
      'py': 'python',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c',
      'h': 'c',
      'cs': 'csharp',
      'go': 'go',
      'rs': 'rust',
      'rb': 'ruby',
      'php': 'php',
      'sql': 'sql',
      'sh': 'bash',
      'yaml': 'yaml',
      'yml': 'yaml',
      'json': 'json',
      'xml': 'xml',
      'html': 'html',
      'css': 'css',
      'md': 'markdown'
    }
    return languageMap[ext] || 'text'
  }

  // Parse line range if available
  const getStartLine = () => {
    if (!fileData.line_range) return 1

    // Handle formats like "Lines 138-148" or "Complete file"
    const match = fileData.line_range.match(/(\d+)/)
    return match ? parseInt(match[1]) : 1
  }

  const language = getLanguage(fileData.file_path)
  const startLine = getStartLine()
  const fileName = fileData.file_path.split('/').pop()

  // Copy code to clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(fileData.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  // Custom line props to highlight error line
  const getLineProps = (lineNumber) => {
    const actualLineNumber = startLine + lineNumber - 1
    const isErrorLine = errorLine && actualLineNumber === errorLine

    return {
      style: {
        backgroundColor: isErrorLine ? 'rgba(255, 82, 82, 0.15)' : 'transparent',
        display: 'block',
        width: '100%',
        borderLeft: isErrorLine ? '3px solid #ff5252' : '3px solid transparent',
        paddingLeft: isErrorLine ? '5px' : '8px'
      }
    }
  }

  return (
    <Paper
      elevation={2}
      sx={{
        mt: 2,
        mb: 2,
        overflow: 'hidden',
        border: '1px solid',
        borderColor: 'divider'
      }}
    >
      {/* Header */}
      {showHeader && (
        <Box
          sx={{
            p: 2,
            bgcolor: 'grey.100',
            borderBottom: '1px solid',
            borderColor: 'divider',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
            <CodeIcon fontSize="small" color="action" />
            <Typography variant="subtitle2" fontWeight={600} sx={{ fontFamily: 'monospace' }}>
              {fileData.file_path}
            </Typography>
            <Chip
              label={fileData.line_range || `${fileData.total_lines} lines`}
              size="small"
              sx={{ ml: 1 }}
            />
            {errorLine && (
              <Chip
                label={`Error at line ${errorLine}`}
                size="small"
                color="error"
                sx={{ ml: 1 }}
              />
            )}
          </Box>

          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            {/* GitHub Link */}
            {fileData.url && (
              <Tooltip title="View on GitHub">
                <IconButton
                  size="small"
                  component="a"
                  href={fileData.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ color: 'text.secondary' }}
                >
                  <GitHubIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}

            {/* Copy Button */}
            <Tooltip title={copied ? 'Copied!' : 'Copy code'}>
              <IconButton
                size="small"
                onClick={handleCopy}
                sx={{ color: copied ? 'success.main' : 'text.secondary' }}
              >
                <ContentCopyIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            {/* Expand/Collapse */}
            <Tooltip title={expanded ? 'Collapse' : 'Expand'}>
              <IconButton
                size="small"
                onClick={() => setExpanded(!expanded)}
                sx={{ color: 'text.secondary' }}
              >
                {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      )}

      {/* Code Content */}
      <Collapse in={expanded}>
        <Box
          sx={{
            maxHeight,
            overflow: 'auto',
            bgcolor: '#1e1e1e', // Match VS Code Dark theme
            '& pre': {
              margin: 0,
              padding: '16px !important',
              fontSize: '13px',
              lineHeight: 1.6
            }
          }}
        >
          <SyntaxHighlighter
            language={language}
            style={vscDarkPlus}
            showLineNumbers={true}
            startingLineNumber={startLine}
            wrapLines={true}
            lineProps={(lineNumber) => getLineProps(lineNumber)}
            customStyle={{
              margin: 0,
              padding: 16,
              backgroundColor: '#1e1e1e'
            }}
          >
            {fileData.content}
          </SyntaxHighlighter>
        </Box>

        {/* Footer with metadata */}
        <Box
          sx={{
            p: 1.5,
            bgcolor: 'grey.50',
            borderTop: '1px solid',
            borderColor: 'divider',
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            flexWrap: 'wrap'
          }}
        >
          {fileData.repo && (
            <Typography variant="caption" color="text.secondary">
              <strong>Repository:</strong> {fileData.repo}
            </Typography>
          )}
          {fileData.branch && (
            <Typography variant="caption" color="text.secondary">
              <strong>Branch:</strong> {fileData.branch}
            </Typography>
          )}
          {fileData.sha && (
            <Typography variant="caption" color="text.secondary">
              <strong>Commit:</strong> {fileData.sha.substring(0, 7)}
            </Typography>
          )}
          {fileData.size_bytes && (
            <Typography variant="caption" color="text.secondary">
              <strong>Size:</strong> {(fileData.size_bytes / 1024).toFixed(1)} KB
            </Typography>
          )}
        </Box>
      </Collapse>
    </Paper>
  )
}

/**
 * CodeSnippetList Component
 *
 * Displays multiple code snippets from GitHub files
 *
 * Props:
 * - githubFiles: array - Array of GitHub file data objects
 * - errorLine: number - Line number to highlight in first file (optional)
 * - title: string - Section title (default: "GitHub Source Code")
 * - emptyMessage: string - Message when no files (default: "No GitHub code available")
 */
export function CodeSnippetList({
  githubFiles = [],
  errorLine = null,
  title = 'GitHub Source Code',
  emptyMessage = 'No GitHub code available for this error'
}) {
  if (!githubFiles || githubFiles.length === 0) {
    return (
      <Paper
        elevation={1}
        sx={{
          p: 3,
          mt: 2,
          textAlign: 'center',
          bgcolor: 'grey.50'
        }}
      >
        <CodeIcon sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
        <Typography variant="body2" color="text.secondary">
          {emptyMessage}
        </Typography>
      </Paper>
    )
  }

  return (
    <Box sx={{ mt: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <GitHubIcon color="action" />
        <Typography variant="h6" fontWeight={600}>
          {title}
        </Typography>
        <Chip
          label={`${githubFiles.length} file${githubFiles.length > 1 ? 's' : ''}`}
          size="small"
          color="primary"
          variant="outlined"
        />
      </Box>

      {githubFiles.map((file, index) => (
        <CodeSnippet
          key={index}
          fileData={file}
          errorLine={index === 0 ? errorLine : null} // Only highlight error in first file
          defaultExpanded={index === 0} // Only expand first file by default
        />
      ))}
    </Box>
  )
}

export default CodeSnippet
