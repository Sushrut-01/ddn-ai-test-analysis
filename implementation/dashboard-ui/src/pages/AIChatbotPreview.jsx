import React, { useState, useRef, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Avatar,
  Chip,
  Card,
  CardContent,
  Grid,
  Button,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  CircularProgress,
  Tooltip,
  Fab,
  Collapse,
  Alert,
  LinearProgress,
  Snackbar
} from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import PersonIcon from '@mui/icons-material/Person'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import EmailIcon from '@mui/icons-material/Email'
import BarChartIcon from '@mui/icons-material/BarChart'
import BugReportIcon from '@mui/icons-material/BugReport'
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates'
import HistoryIcon from '@mui/icons-material/History'
import DeleteIcon from '@mui/icons-material/Delete'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import DownloadIcon from '@mui/icons-material/Download'
import MicIcon from '@mui/icons-material/Mic'
import AttachFileIcon from '@mui/icons-material/AttachFile'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import RefreshIcon from '@mui/icons-material/Refresh'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import InfoIcon from '@mui/icons-material/Info'
import TableChartIcon from '@mui/icons-material/TableChart'
import TimelineIcon from '@mui/icons-material/Timeline'
import AssessmentIcon from '@mui/icons-material/Assessment'
import SearchIcon from '@mui/icons-material/Search'
import BuildIcon from '@mui/icons-material/Build'
import { chatAPI, failuresAPI } from '../services/api'

// Copy to clipboard helper
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (err) {
    console.error('Failed to copy:', err)
    return false
  }
}

// Initial chat history
const initialChatHistory = [
  {
    id: 1,
    role: 'assistant',
    content: 'Hello! I\'m your AI Analysis Assistant. I can help you with:\n\n• **Failure Analysis** - Get insights on test failures\n• **Reports** - Generate PDF/Excel reports\n• **Data Queries** - Ask questions about your test data\n• **Bug Creation** - Create Jira bugs from failures\n• **Recommendations** - Get AI-powered suggestions\n\nHow can I help you today?',
    timestamp: new Date(Date.now() - 60000)
  }
]

// Quick action suggestions
const quickActions = [
  { icon: <BugReportIcon />, label: 'Show recent failures', query: 'Show me the recent test failures from today' },
  { icon: <BarChartIcon />, label: 'Generate weekly report', query: 'Generate a weekly failure analysis report' },
  { icon: <TipsAndUpdatesIcon />, label: 'Top failure patterns', query: 'What are the top failure patterns this week?' },
  { icon: <AssessmentIcon />, label: 'AI acceptance rate', query: 'What is the AI analysis acceptance rate?' },
  { icon: <SearchIcon />, label: 'Find similar errors', query: 'Find similar errors to NullPointerException' },
  { icon: <BuildIcon />, label: 'Build health summary', query: 'Give me a build health summary for this week' }
]

function AIChatbotPreview() {
  const [messages, setMessages] = useState(initialChatHistory)
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [showQuickActions, setShowQuickActions] = useState(true)
  const [emailDialogOpen, setEmailDialogOpen] = useState(false)
  const [pdfDialogOpen, setPdfDialogOpen] = useState(false)
  const [emailTo, setEmailTo] = useState('')
  const [reportType, setReportType] = useState('weekly')
  const [generating, setGenerating] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' })
  const [bugDialogOpen, setBugDialogOpen] = useState(false)
  const [selectedFailure, setSelectedFailure] = useState(null)
  const messagesEndRef = useRef(null)

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity })
  }

  const handleCopyMessage = async (content) => {
    const success = await copyToClipboard(content)
    showSnackbar(success ? 'Copied to clipboard!' : 'Failed to copy', success ? 'success' : 'error')
  }

  const handleExportExcel = async () => {
    try {
      showSnackbar('Generating Excel report...', 'info')
      // Call the stats API and format as CSV
      const response = await fetch('http://localhost:5006/api/stats')
      const data = await response.json()

      // Create CSV content
      const csvContent = `DDN Test Failure Report\nGenerated: ${new Date().toISOString()}\n\n` +
        `Metric,Value\n` +
        `Total Failures,${data.data?.total_failures || 0}\n` +
        `AI Analyzed,${data.data?.ai_analyzed || 0}\n` +
        `Avg Confidence,${data.data?.avg_confidence || 0}%\n` +
        `Accepted,${data.data?.accepted || 0}\n` +
        `Rejected,${data.data?.rejected || 0}\n`

      // Download as CSV
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `failure_report_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      window.URL.revokeObjectURL(url)

      showSnackbar('Excel report downloaded!', 'success')
    } catch (error) {
      showSnackbar('Failed to generate report: ' + error.message, 'error')
    }
  }

  const handleCreateBug = () => {
    // Add a message asking for failure details
    const bugMessage = {
      id: messages.length + 1,
      role: 'assistant',
      content: `🐛 **Create Jira Bug**\n\nTo create a bug ticket, please provide:\n1. The build ID or failure you want to report\n2. Any additional context\n\nOr say "Create bug for latest failure" and I'll help you create a ticket.\n\n*Jira is configured for: ${window.location.hostname.includes('localhost') ? 'sushrutnistane2001.atlassian.net' : 'your Jira instance'}*`,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, bugMessage])
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const messageToSend = inputValue
    setInputValue('')
    setIsTyping(true)
    setShowQuickActions(false)

    try {
      // Build conversation history for context
      const conversationHistory = messages.slice(-10).map(m => ({
        role: m.role,
        content: m.content
      }))

      // Call the real API
      const response = await chatAPI.sendMessage(messageToSend, conversationHistory)
      const data = response?.data || response

      const aiResponse = {
        id: messages.length + 2,
        role: 'assistant',
        content: data.response || 'I apologize, but I could not process your request. Please try again.',
        timestamp: new Date(),
        data: data.data // Include any structured data
      }
      setMessages(prev => [...prev, aiResponse])
    } catch (error) {
      console.error('Chat API error:', error)
      const errorResponse = {
        id: messages.length + 2,
        role: 'assistant',
        content: `I'm having trouble connecting to the AI service. Please check that the dashboard API is running.\n\n**Error:** ${error.message || 'Connection failed'}`,
        timestamp: new Date(),
        isError: true
      }
      setMessages(prev => [...prev, errorResponse])
    } finally {
      setIsTyping(false)
    }
  }

  const handleQuickAction = async (query) => {
    // Directly send the query instead of setting input
    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: query,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setIsTyping(true)
    setShowQuickActions(false)

    try {
      const conversationHistory = messages.slice(-10).map(m => ({
        role: m.role,
        content: m.content
      }))

      const response = await chatAPI.sendMessage(query, conversationHistory)
      const data = response?.data || response

      const aiResponse = {
        id: messages.length + 2,
        role: 'assistant',
        content: data.response || 'I could not process your request.',
        timestamp: new Date(),
        data: data.data
      }
      setMessages(prev => [...prev, aiResponse])
    } catch (error) {
      console.error('Chat API error:', error)
      const errorResponse = {
        id: messages.length + 2,
        role: 'assistant',
        content: `Connection error: ${error.message || 'Failed to reach AI service'}`,
        timestamp: new Date(),
        isError: true
      }
      setMessages(prev => [...prev, errorResponse])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleGeneratePDF = () => {
    setGenerating(true)
    setTimeout(() => {
      setGenerating(false)
      setPdfDialogOpen(false)
      // Add confirmation message
      const confirmMessage = {
        id: messages.length + 1,
        role: 'assistant',
        content: `✅ **PDF Report Generated Successfully!**\n\n📄 File: \`${reportType}_failure_report_${new Date().toISOString().split('T')[0]}.pdf\`\n📦 Size: 2.4 MB\n\nThe report has been downloaded to your system.`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, confirmMessage])
    }, 2000)
  }

  const handleSendEmail = () => {
    setGenerating(true)
    setTimeout(() => {
      setGenerating(false)
      setEmailDialogOpen(false)
      // Add confirmation message
      const confirmMessage = {
        id: messages.length + 1,
        role: 'assistant',
        content: `✅ **Email Sent Successfully!**\n\n📧 To: ${emailTo}\n📋 Subject: DDN AI Analysis - ${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report\n\nThe report has been sent to the specified email address.`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, confirmMessage])
    }, 2000)
  }

  const clearChat = () => {
    setMessages(initialChatHistory)
    setShowQuickActions(true)
  }

  const pastConversations = [
    { id: 1, title: 'Weekly failure analysis', date: '2 hours ago' },
    { id: 2, title: 'Bug creation for DDN-1234', date: 'Yesterday' },
    { id: 3, title: 'Integration test patterns', date: '2 days ago' },
    { id: 4, title: 'Monthly report generation', date: '1 week ago' }
  ]

  return (
    <Box sx={{ height: 'calc(100vh - 100px)', display: 'flex', gap: 2 }}>
      {/* Sidebar - Chat History */}
      <Paper
        elevation={0}
        sx={{
          width: showHistory ? 280 : 0,
          overflow: 'hidden',
          transition: 'width 0.3s',
          borderRadius: 3,
          border: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Typography variant="subtitle1" fontWeight={600}>
            <HistoryIcon sx={{ mr: 1, verticalAlign: 'middle', fontSize: 20 }} />
            Chat History
          </Typography>
        </Box>
        <List dense>
          {pastConversations.map((conv) => (
            <ListItemButton key={conv.id} sx={{ py: 1.5 }}>
              <ListItemText
                primary={conv.title}
                secondary={conv.date}
                primaryTypographyProps={{ fontSize: '0.875rem', noWrap: true }}
                secondaryTypographyProps={{ fontSize: '0.75rem' }}
              />
            </ListItemButton>
          ))}
        </List>
      </Paper>

      {/* Main Chat Area */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Paper
          elevation={0}
          sx={{
            p: 2,
            mb: 2,
            borderRadius: 3,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 48, height: 48 }}>
                <SmartToyIcon sx={{ fontSize: 28 }} />
              </Avatar>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  AI Analysis Assistant
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Ask questions, generate reports, get insights
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Toggle History">
                <IconButton
                  onClick={() => setShowHistory(!showHistory)}
                  sx={{ color: 'white' }}
                >
                  <HistoryIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="New Chat">
                <IconButton onClick={clearChat} sx={{ color: 'white' }}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Paper>

        {/* Quick Actions */}
        <Collapse in={showQuickActions}>
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1.5, px: 1 }}>
              <AutoAwesomeIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'middle' }} />
              Quick Actions
            </Typography>
            <Grid container spacing={1}>
              {quickActions.map((action, index) => (
                <Grid item xs={6} md={4} key={index}>
                  <Card
                    variant="outlined"
                    sx={{
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      '&:hover': {
                        borderColor: 'primary.main',
                        bgcolor: 'primary.50',
                        transform: 'translateY(-2px)'
                      }
                    }}
                    onClick={() => handleQuickAction(action.query)}
                  >
                    <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box sx={{ color: 'primary.main' }}>{action.icon}</Box>
                        <Typography variant="body2" fontWeight={500}>
                          {action.label}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        </Collapse>

        {/* Messages Area */}
        <Paper
          elevation={0}
          sx={{
            flex: 1,
            overflow: 'auto',
            p: 2,
            borderRadius: 3,
            border: '1px solid',
            borderColor: 'divider',
            bgcolor: '#fafafa'
          }}
        >
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                mb: 2
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  gap: 1.5,
                  maxWidth: '80%',
                  flexDirection: message.role === 'user' ? 'row-reverse' : 'row'
                }}
              >
                <Avatar
                  sx={{
                    bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                    width: 36,
                    height: 36
                  }}
                >
                  {message.role === 'user' ? <PersonIcon /> : <SmartToyIcon />}
                </Avatar>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    bgcolor: message.role === 'user' ? 'primary.main' : 'white',
                    color: message.role === 'user' ? 'white' : 'text.primary',
                    border: message.role === 'user' ? 'none' : '1px solid',
                    borderColor: 'divider'
                  }}
                >
                  <Typography
                    variant="body2"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      '& strong': { fontWeight: 600 },
                      '& code': {
                        bgcolor: message.role === 'user' ? 'rgba(255,255,255,0.2)' : 'grey.100',
                        px: 0.5,
                        borderRadius: 0.5,
                        fontFamily: 'monospace'
                      }
                    }}
                    dangerouslySetInnerHTML={{
                      __html: message.content
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/`(.*?)`/g, '<code>$1</code>')
                        .replace(/\n/g, '<br/>')
                    }}
                  />
                  {message.role === 'assistant' && (
                    <Box sx={{ display: 'flex', gap: 0.5, mt: 1.5, pt: 1, borderTop: '1px solid', borderColor: 'divider' }}>
                      <Tooltip title="Copy">
                        <IconButton size="small" onClick={() => handleCopyMessage(message.content)}>
                          <ContentCopyIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Download as PDF">
                        <IconButton size="small" onClick={() => setPdfDialogOpen(true)}>
                          <PictureAsPdfIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Send via Email">
                        <IconButton size="small" onClick={() => setEmailDialogOpen(true)}>
                          <EmailIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Export Data">
                        <IconButton size="small" onClick={handleExportExcel}>
                          <TableChartIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  )}
                </Paper>
              </Box>
            </Box>
          ))}

          {isTyping && (
            <Box sx={{ display: 'flex', gap: 1.5, mb: 2 }}>
              <Avatar sx={{ bgcolor: 'secondary.main', width: 36, height: 36 }}>
                <SmartToyIcon />
              </Avatar>
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  borderRadius: 2,
                  bgcolor: 'white',
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={16} />
                  <Typography variant="body2" color="text.secondary">
                    AI is analyzing...
                  </Typography>
                </Box>
              </Paper>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Paper>

        {/* Input Area */}
        <Paper
          elevation={0}
          sx={{
            p: 2,
            mt: 2,
            borderRadius: 3,
            border: '1px solid',
            borderColor: 'divider'
          }}
        >
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Attach File">
              <IconButton>
                <AttachFileIcon />
              </IconButton>
            </Tooltip>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Ask me anything about your test failures, reports, or data..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              variant="outlined"
              size="small"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2
                }
              }}
            />
            <Tooltip title="Voice Input">
              <IconButton>
                <MicIcon />
              </IconButton>
            </Tooltip>
            <Button
              variant="contained"
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isTyping}
              sx={{ borderRadius: 2, px: 3 }}
            >
              <SendIcon />
            </Button>
          </Box>
          <Box sx={{ display: 'flex', gap: 1, mt: 1.5, flexWrap: 'wrap' }}>
            <Chip
              size="small"
              icon={<PictureAsPdfIcon />}
              label="Generate PDF"
              onClick={() => setPdfDialogOpen(true)}
              variant="outlined"
            />
            <Chip
              size="small"
              icon={<EmailIcon />}
              label="Email Report"
              onClick={() => setEmailDialogOpen(true)}
              variant="outlined"
            />
            <Chip
              size="small"
              icon={<TableChartIcon />}
              label="Export Excel"
              onClick={handleExportExcel}
              variant="outlined"
              sx={{ cursor: 'pointer' }}
            />
            <Chip
              size="small"
              icon={<BugReportIcon />}
              label="Create Bug"
              onClick={handleCreateBug}
              variant="outlined"
              sx={{ cursor: 'pointer' }}
            />
          </Box>
        </Paper>
      </Box>

      {/* Right Sidebar - Insights */}
      <Paper
        elevation={0}
        sx={{
          width: 280,
          p: 2,
          borderRadius: 3,
          border: '1px solid',
          borderColor: 'divider',
          display: { xs: 'none', lg: 'block' }
        }}
      >
        <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
          <TipsAndUpdatesIcon sx={{ mr: 1, verticalAlign: 'middle', fontSize: 20, color: 'warning.main' }} />
          AI Insights
        </Typography>

        <Alert severity="info" sx={{ mb: 2, '& .MuiAlert-message': { fontSize: '0.8rem' } }}>
          3 new failures detected in the last hour
        </Alert>

        <Card variant="outlined" sx={{ mb: 2 }}>
          <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
            <Typography variant="caption" color="text.secondary">Today's Stats</Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
              <Box>
                <Typography variant="h6" fontWeight={600} color="error.main">7</Typography>
                <Typography variant="caption">Failures</Typography>
              </Box>
              <Box>
                <Typography variant="h6" fontWeight={600} color="success.main">85%</Typography>
                <Typography variant="caption">AI Accuracy</Typography>
              </Box>
              <Box>
                <Typography variant="h6" fontWeight={600} color="primary.main">4</Typography>
                <Typography variant="caption">Bugs Created</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
          Suggested Queries
        </Typography>
        <List dense>
          <ListItemButton sx={{ borderRadius: 1, mb: 0.5 }} onClick={() => handleQuickAction('Show failures from DDN-1247')}>
            <ListItemIcon sx={{ minWidth: 32 }}>
              <SearchIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="Show failures from DDN-1247"
              primaryTypographyProps={{ fontSize: '0.8rem' }}
            />
          </ListItemButton>
          <ListItemButton sx={{ borderRadius: 1, mb: 0.5 }} onClick={() => handleQuickAction('Compare this week vs last week')}>
            <ListItemIcon sx={{ minWidth: 32 }}>
              <TimelineIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="Compare weekly trends"
              primaryTypographyProps={{ fontSize: '0.8rem' }}
            />
          </ListItemButton>
          <ListItemButton sx={{ borderRadius: 1 }} onClick={() => handleQuickAction('What needs my attention?')}>
            <ListItemIcon sx={{ minWidth: 32 }}>
              <ErrorIcon fontSize="small" color="error" />
            </ListItemIcon>
            <ListItemText
              primary="What needs attention?"
              primaryTypographyProps={{ fontSize: '0.8rem' }}
            />
          </ListItemButton>
        </List>
      </Paper>

      {/* PDF Dialog */}
      <Dialog open={pdfDialogOpen} onClose={() => setPdfDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PictureAsPdfIcon color="error" />
            Generate PDF Report
          </Box>
        </DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Report Type</InputLabel>
            <Select
              value={reportType}
              label="Report Type"
              onChange={(e) => setReportType(e.target.value)}
            >
              <MenuItem value="daily">Daily Summary</MenuItem>
              <MenuItem value="weekly">Weekly Analysis</MenuItem>
              <MenuItem value="monthly">Monthly Report</MenuItem>
              <MenuItem value="custom">Custom Date Range</MenuItem>
            </Select>
          </FormControl>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              The report will include:
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon><CheckCircleIcon color="success" fontSize="small" /></ListItemIcon>
                <ListItemText primary="Failure summary and trends" />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircleIcon color="success" fontSize="small" /></ListItemIcon>
                <ListItemText primary="AI analysis acceptance rate" />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircleIcon color="success" fontSize="small" /></ListItemIcon>
                <ListItemText primary="Top failure patterns" />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircleIcon color="success" fontSize="small" /></ListItemIcon>
                <ListItemText primary="Recommendations" />
              </ListItem>
            </List>
          </Box>
          {generating && <LinearProgress sx={{ mt: 2 }} />}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPdfDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleGeneratePDF}
            disabled={generating}
            startIcon={generating ? <CircularProgress size={16} /> : <DownloadIcon />}
          >
            {generating ? 'Generating...' : 'Download PDF'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Email Dialog */}
      <Dialog open={emailDialogOpen} onClose={() => setEmailDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <EmailIcon color="primary" />
            Send Report via Email
          </Box>
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Email Address"
            type="email"
            value={emailTo}
            onChange={(e) => setEmailTo(e.target.value)}
            placeholder="recipient@company.com"
            sx={{ mt: 2 }}
          />
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Report Type</InputLabel>
            <Select
              value={reportType}
              label="Report Type"
              onChange={(e) => setReportType(e.target.value)}
            >
              <MenuItem value="daily">Daily Summary</MenuItem>
              <MenuItem value="weekly">Weekly Analysis</MenuItem>
              <MenuItem value="monthly">Monthly Report</MenuItem>
            </Select>
          </FormControl>
          {generating && <LinearProgress sx={{ mt: 2 }} />}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEmailDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSendEmail}
            disabled={generating || !emailTo}
            startIcon={generating ? <CircularProgress size={16} /> : <SendIcon />}
          >
            {generating ? 'Sending...' : 'Send Email'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default AIChatbotPreview
