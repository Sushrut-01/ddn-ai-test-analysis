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
  LinearProgress
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

// Mock chat history
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

// Sample conversation responses (mock AI responses)
const mockResponses = {
  'failures': `Based on my analysis, here are the **recent test failures**:

| Build ID | Test Name | Category | AI Confidence |
|----------|-----------|----------|---------------|
| DDN-1247 | LoginTest.testAuth | Authentication | 92% |
| DDN-1246 | PaymentTest.checkout | Integration | 87% |
| DDN-1245 | APITest.timeout | Network | 78% |

**Key Insights:**
• 3 failures in the last 24 hours
• Most common category: Integration (45%)
• Average AI confidence: 85.7%

Would you like me to generate a detailed PDF report or create bugs for these failures?`,

  'report': `I'll generate a **Weekly Failure Analysis Report** for you.

**Report Preview:**
📊 **Period:** Nov 22 - Nov 29, 2024
📈 **Total Failures:** 24
✅ **AI Analyzed:** 22 (91.7%)
🎯 **Acceptance Rate:** 78%

**Top Categories:**
1. Integration Errors (8)
2. Timeout Issues (6)
3. Authentication Failures (5)
4. Data Validation (5)

**Recommendations:**
• Review integration test environment stability
• Consider increasing timeout thresholds for API tests
• Update authentication test data

Would you like me to:
1. 📄 **Download as PDF**
2. 📧 **Send via Email**
3. 📊 **Export as Excel**`,

  'patterns': `Here are the **Top Failure Patterns** this week:

### 1. NullPointerException (8 occurrences)
- **Root Cause:** Missing null checks in service layer
- **Affected Tests:** UserService, PaymentService
- **AI Suggestion:** Add Optional<> wrapper

### 2. Connection Timeout (6 occurrences)
- **Root Cause:** Database connection pool exhaustion
- **Affected Tests:** Integration tests
- **AI Suggestion:** Increase pool size, add retry logic

### 3. Assertion Failures (5 occurrences)
- **Root Cause:** Test data mismatch
- **Affected Tests:** Data validation tests
- **AI Suggestion:** Refresh test fixtures

Would you like me to create Jira bugs for these patterns?`,

  'acceptance': `**AI Analysis Acceptance Rate Summary:**

📊 **Overall Rate:** 78.5%

**Breakdown by Category:**
| Category | Accepted | Rejected | Refined |
|----------|----------|----------|---------|
| Code Errors | 85% | 10% | 5% |
| Integration | 75% | 15% | 10% |
| Timeout | 72% | 18% | 10% |
| Data Issues | 80% | 12% | 8% |

**Trend:** ↑ 5% improvement from last week

**Insights:**
• Code error analysis has highest accuracy
• Integration errors need more context for better analysis
• User refinements are helping improve the model

Would you like to see detailed refinement feedback?`,

  'default': `I understand you're asking about that. Let me analyze the data...

Based on my analysis of your test data:

• **Total Tests:** 1,247 in the last 7 days
• **Pass Rate:** 94.2%
• **AI Analyzed Failures:** 73 out of 78

I can help you with:
1. Generate detailed reports (PDF/Excel)
2. Create Jira bugs from failures
3. Find similar past errors
4. Get AI recommendations

What would you like to explore further?`
}

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
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const getAIResponse = (query) => {
    const lowerQuery = query.toLowerCase()
    if (lowerQuery.includes('failure') || lowerQuery.includes('error')) {
      return mockResponses.failures
    } else if (lowerQuery.includes('report') || lowerQuery.includes('generate')) {
      return mockResponses.report
    } else if (lowerQuery.includes('pattern') || lowerQuery.includes('common')) {
      return mockResponses.patterns
    } else if (lowerQuery.includes('acceptance') || lowerQuery.includes('rate')) {
      return mockResponses.acceptance
    }
    return mockResponses.default
  }

  const handleSendMessage = () => {
    if (!inputValue.trim()) return

    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)
    setShowQuickActions(false)

    // Simulate AI response delay
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        role: 'assistant',
        content: getAIResponse(inputValue),
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiResponse])
      setIsTyping(false)
    }, 1500)
  }

  const handleQuickAction = (query) => {
    setInputValue(query)
    setTimeout(() => handleSendMessage(), 100)
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
                        <IconButton size="small">
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
                        <IconButton size="small">
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
              variant="outlined"
            />
            <Chip
              size="small"
              icon={<BugReportIcon />}
              label="Create Bug"
              variant="outlined"
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
    </Box>
  )
}

export default AIChatbotPreview
