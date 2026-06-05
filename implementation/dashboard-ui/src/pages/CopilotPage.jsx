import React, { useState, useRef, useEffect } from 'react'
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Chip,
  Button,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Collapse,
  Alert,
  Snackbar,
  Tooltip
} from '@mui/material'
import {
  Send as SendIcon,
  AttachFile as AttachFileIcon,
  Mic as MicIcon,
  Code as CodeIcon,
  BugReport as BugReportIcon,
  Speed as SpeedIcon,
  Description as DescriptionIcon,
  Security as SecurityIcon,
  Visibility as VisibilityIcon,
  AutoAwesome as AutoAwesomeIcon,
  CheckCircle as CheckCircleIcon,
  Lightbulb as LightbulbIcon,
  ExpandLess,
  ExpandMore
} from '@mui/icons-material'
import { useColorTheme } from '../theme/ThemeContext'
import { copilotAPI } from '../services/api'

function CopilotPage() {
  const { theme } = useColorTheme()
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'ai',
      content: 'Welcome to DDN AI Copilot! I\'m your intelligent coding assistant powered by Gemini Flash 2.0. I can help you with test failure analysis, code debugging, test generation, and more.',
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const [expandedTools, setExpandedTools] = useState({
    'Code Actions': true,
    'Testing': true,
    'Documentation': true,
    'AI Analysis': true
  })
  const [error, setError] = useState(null)
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [attachedFile, setAttachedFile] = useState(null)
  const [isListening, setIsListening] = useState(false)
  const messagesEndRef = useRef(null)
  const chatMessagesRef = useRef(null)
  const fileInputRef = useRef(null)
  const recognitionRef = useRef(null)

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = 'en-US'

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        setInputValue(prev => prev + ' ' + transcript)
        setIsListening(false)
      }

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
        if (event.error === 'not-allowed') {
          setError('Microphone access denied. Please enable it in browser settings.')
        } else {
          setError('Voice input failed. Please try again.')
        }
        setSnackbarOpen(true)
      }

      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort()
      }
    }
  }, [])

  // Handle voice input toggle
  const handleVoiceInput = () => {
    if (!recognitionRef.current) {
      setError('Voice input is not supported in this browser. Try Chrome or Edge.')
      setSnackbarOpen(true)
      return
    }

    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    } else {
      try {
        recognitionRef.current.start()
        setIsListening(true)
      } catch (err) {
        console.error('Voice start error:', err)
        setError('Could not start voice input. Please try again.')
        setSnackbarOpen(true)
      }
    }
  }

  // Handle file attachment
  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
      // Check file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB')
        setSnackbarOpen(true)
        return
      }
      setAttachedFile(file)
    }
  }

  const handleRemoveFile = () => {
    setAttachedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (directMessage = null) => {
    const messageToSend = directMessage || inputValue
    if (!messageToSend.trim() && !attachedFile) return

    // Read attached file if present
    let fileContent = ''
    let displayMessage = messageToSend
    if (attachedFile) {
      try {
        fileContent = await attachedFile.text()
        displayMessage = `${messageToSend}\n\n📎 Attached: ${attachedFile.name}`
      } catch (e) {
        console.error('Error reading file:', e)
      }
    }

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: displayMessage,
      timestamp: new Date()
    }

    const currentInput = attachedFile
      ? `${messageToSend}\n\nFile: ${attachedFile.name}\n\`\`\`\n${fileContent}\n\`\`\``
      : messageToSend
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setAttachedFile(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
    setIsThinking(true)
    setError(null)

    try {
      // Get conversation history for context
      // Map 'ai' role to 'assistant' for OpenAI API compatibility
      const conversationHistory = messages.map(msg => ({
        role: msg.role === 'ai' ? 'assistant' : msg.role,
        content: msg.content
      }))

      // Call the copilot API
      const response = await copilotAPI.chat({
        message: currentInput,
        conversation_history: conversationHistory,
        context: {
          project: 'DDN AI Test Analysis',
          capabilities: ['test_analysis', 'code_debugging', 'test_generation'],
          has_attachment: !!attachedFile
        }
      })

      const aiResponse = {
        id: Date.now() + 1,
        role: 'ai',
        content: response.data?.response || response.response || 'I received your message but couldn\'t generate a response. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiResponse])
    } catch (err) {
      console.error('Copilot API Error:', err)

      // Fallback to simulated response if API fails
      const aiResponse = {
        id: Date.now() + 1,
        role: 'ai',
        content: getSmartResponse(currentInput),
        timestamp: new Date(),
        isSimulated: true
      }
      setMessages(prev => [...prev, aiResponse])

      setError('Using simulated response. Backend API may be unavailable.')
      setSnackbarOpen(true)
    } finally {
      setIsThinking(false)
    }
  }

  const getSmartResponse = (userMessage) => {
    const lowerMsg = userMessage.toLowerCase()

    if (lowerMsg.includes('test') || lowerMsg.includes('failure')) {
      return 'I\'ve analyzed your test failures. Based on the error patterns in your DDN AI project, I can help identify root causes, suggest fixes, and generate test cases. Would you like me to analyze a specific test failure or generate new tests?'
    }

    if (lowerMsg.includes('optimize') || lowerMsg.includes('performance')) {
      return 'I can help optimize your code performance. Some common optimizations include: using list comprehensions, caching database queries, implementing connection pooling, and reducing API calls. Which area would you like to focus on?'
    }

    if (lowerMsg.includes('explain') || lowerMsg.includes('how')) {
      return 'I can explain how the DDN AI system works:\n\n1. **Test Analysis** - AI analyzes test failures using Gemini\n2. **Categorization** - Failures are categorized (CODE_ERROR, TEST_FAILURE, INFRA_ERROR)\n3. **Root Cause Detection** - AI determines underlying issues\n4. **Fix Suggestions** - Provides actionable recommendations\n\nWhat specific component would you like me to explain in detail?'
    }

    if (lowerMsg.includes('debug') || lowerMsg.includes('error')) {
      return 'I can help debug errors in your codebase. Please share the error message or describe the issue you\'re facing, and I\'ll analyze it with context from your DDN AI project.'
    }

    return `I understand you\'re asking about: "${userMessage}"\n\nBased on your DDN AI project context, I can help you with:\n• Analyzing test failures\n• Debugging code errors\n• Optimizing performance\n• Generating tests\n• Explaining code patterns\n\nHow can I assist you further?`
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const quickActions = [
    { label: 'Analyze Failures', icon: <BugReportIcon />, action: 'Analyze test failures in the latest build' },
    { label: 'Generate Tests', icon: <CheckCircleIcon />, action: 'Generate test cases for my code' },
    { label: 'Debug Code', icon: <CodeIcon />, action: 'Debug code errors in my project' },
    { label: 'Explain Code', icon: <LightbulbIcon />, action: 'Explain how the AI analysis works' },
    { label: 'Optimize', icon: <SpeedIcon />, action: 'Optimize performance of my code' },
    { label: 'Code Review', icon: <VisibilityIcon />, action: 'Review code quality and suggest improvements' }
  ]

  const aiTools = {
    'Code Actions': [
      { name: 'Explain Code', icon: <LightbulbIcon />, desc: 'Get detailed explanation' },
      { name: 'Optimize', icon: <SpeedIcon />, desc: 'Improve performance' },
      { name: 'Refactor', icon: <CodeIcon />, desc: 'Restructure code' }
    ],
    'Testing': [
      { name: 'Generate Tests', icon: <CheckCircleIcon />, desc: 'Auto-create unit tests' },
      { name: 'Analyze Failures', icon: <BugReportIcon />, desc: 'Find root causes' }
    ],
    'Documentation': [
      { name: 'Add Docstrings', icon: <DescriptionIcon />, desc: 'Generate documentation' }
    ],
    'AI Analysis': [
      { name: 'Security Scan', icon: <SecurityIcon />, desc: 'Check vulnerabilities' },
      { name: 'Code Review', icon: <VisibilityIcon />, desc: 'AI-powered review' }
    ]
  }

  const handleQuickAction = (action) => {
    handleSendMessage(action)
  }

  const handleToolClick = (toolName) => {
    handleSendMessage(`Run ${toolName} on my code`)
  }

  const toggleToolSection = (section) => {
    setExpandedTools(prev => ({ ...prev, [section]: !prev[section] }))
  }

  const handleSnackbarClose = () => {
    setSnackbarOpen(false)
  }

  // Load chat history on mount
  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const response = await copilotAPI.getHistory(10)
        if (response.data?.history && response.data.history.length > 0) {
          const historyMessages = response.data.history.map((msg, idx) => ({
            id: idx + 1,
            role: msg.role,
            content: msg.content,
            timestamp: new Date(msg.timestamp || Date.now())
          }))
          setMessages(prev => [...historyMessages, ...prev])
        }
      } catch (err) {
        console.error('Failed to load chat history:', err)
        // Continue with welcome message
      }
    }

    loadChatHistory()
  }, [])

  return (
    <Box sx={{ display: 'flex', height: 'calc(100vh - 120px)', gap: 2 }}>
      {/* Main Chat Area */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Paper sx={{ p: 2, mb: 2, bgcolor: theme.surface, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{
              bgcolor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            }}>
              <AutoAwesomeIcon />
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ color: theme.textPrimary, fontWeight: 600 }}>
                DDN AI Copilot
              </Typography>
              <Typography variant="caption" sx={{ color: theme.textSecondary }}>
                Gemini Flash 2.0 • Real-time • Context-aware
              </Typography>
            </Box>
            <Chip
              icon={<Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#10b981' }} />}
              label="Connected"
              size="small"
              sx={{ bgcolor: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }}
            />
          </Box>
        </Paper>

        {/* Quick Actions */}
        <Paper sx={{ p: 2, mb: 2, bgcolor: theme.surface, borderRadius: 2 }}>
          <Typography variant="subtitle2" sx={{ color: theme.textSecondary, mb: 1.5, fontSize: '0.75rem', textTransform: 'uppercase' }}>
            Quick Actions
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {quickActions.map((qa) => (
              <Button
                key={qa.label}
                size="small"
                startIcon={qa.icon}
                onClick={() => handleQuickAction(qa.action)}
                sx={{
                  bgcolor: theme.isDark ? 'rgba(102, 126, 234, 0.15)' : 'rgba(102, 126, 234, 0.1)',
                  color: '#667eea',
                  border: '1px solid rgba(102, 126, 234, 0.3)',
                  '&:hover': {
                    bgcolor: theme.isDark ? 'rgba(102, 126, 234, 0.25)' : 'rgba(102, 126, 234, 0.2)',
                    transform: 'translateY(-2px)',
                    transition: 'all 0.2s'
                  }
                }}
              >
                {qa.label}
              </Button>
            ))}
          </Box>
        </Paper>

        {/* Messages Area */}
        <Paper sx={{
          flex: 1,
          bgcolor: theme.surface,
          borderRadius: 2,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <Box
            ref={chatMessagesRef}
            sx={{
              flex: 1,
              overflowY: 'auto',
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              gap: 2
            }}
          >
            {messages.map((message) => (
              <Box
                key={message.id}
                sx={{
                  display: 'flex',
                  gap: 1.5,
                  animation: 'fadeIn 0.4s ease',
                  '@keyframes fadeIn': {
                    from: { opacity: 0, transform: 'translateY(15px)' },
                    to: { opacity: 1, transform: 'translateY(0)' }
                  }
                }}
              >
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    background: message.role === 'user'
                      ? 'linear-gradient(135deg, #0e639c 0%, #1e88e5 100%)'
                      : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    fontSize: '1rem'
                  }}
                >
                  {message.role === 'user' ? '👤' : '🤖'}
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: theme.textPrimary }}>
                      {message.role === 'user' ? 'You' : 'DDN AI Copilot'}
                    </Typography>
                    <Typography variant="caption" sx={{ color: theme.textSecondary }}>
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </Typography>
                  </Box>
                  <Paper
                    sx={{
                      p: 1.5,
                      bgcolor: message.role === 'user'
                        ? theme.isDark ? 'rgba(14, 99, 156, 0.2)' : 'rgba(14, 99, 156, 0.1)'
                        : theme.isDark ? 'rgba(45, 45, 48, 1)' : 'rgba(245, 245, 245, 1)',
                      border: message.role === 'user' ? '1px solid rgba(14, 99, 156, 0.3)' : 'none',
                      borderRadius: 2,
                      whiteSpace: 'pre-wrap'
                    }}
                  >
                    <Typography variant="body2" sx={{ color: theme.textPrimary, lineHeight: 1.6 }}>
                      {message.content}
                    </Typography>
                  </Paper>
                </Box>
              </Box>
            ))}

            {isThinking && (
              <Box sx={{ display: 'flex', gap: 1.5 }}>
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  }}
                >
                  🤖
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: theme.textPrimary, mb: 0.5 }}>
                    DDN AI Copilot
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      {[0, 1, 2].map((i) => (
                        <Box
                          key={i}
                          sx={{
                            width: 6,
                            height: 6,
                            borderRadius: '50%',
                            bgcolor: theme.textSecondary,
                            animation: 'thinking 1.4s infinite',
                            animationDelay: `${i * 0.2}s`,
                            '@keyframes thinking': {
                              '0%, 60%, 100%': { transform: 'translateY(0)', opacity: 0.5 },
                              '30%': { transform: 'translateY(-8px)', opacity: 1 }
                            }
                          }}
                        />
                      ))}
                    </Box>
                    <Typography variant="caption" sx={{ color: theme.textSecondary }}>
                      Analyzing with AI...
                    </Typography>
                  </Box>
                </Box>
              </Box>
            )}

            <div ref={messagesEndRef} />
          </Box>

          <Divider />

          {/* Input Area */}
          <Box sx={{ p: 2, bgcolor: theme.isDark ? 'rgba(45, 45, 48, 1)' : 'rgba(250, 250, 250, 1)' }}>
            <Paper
              sx={{
                display: 'flex',
                alignItems: 'flex-end',
                gap: 1,
                p: 1.5,
                bgcolor: theme.isDark ? 'rgba(60, 60, 60, 1)' : 'white',
                border: `2px solid ${theme.isDark ? 'rgba(102, 126, 234, 0.3)' : 'rgba(102, 126, 234, 0.2)'}`,
                borderRadius: 2,
                '&:focus-within': {
                  borderColor: '#667eea'
                }
              }}
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                style={{ display: 'none' }}
                accept=".txt,.js,.jsx,.ts,.tsx,.py,.java,.json,.md,.log,.csv,.xml,.html,.css"
              />
              <Tooltip title="Attach File">
                <IconButton
                  size="small"
                  sx={{ color: attachedFile ? '#667eea' : theme.textSecondary }}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <AttachFileIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title={isListening ? "Stop listening" : "Voice input"}>
                <IconButton
                  size="small"
                  onClick={handleVoiceInput}
                  sx={{
                    color: isListening ? '#ef4444' : theme.textSecondary,
                    animation: isListening ? 'pulse 1s infinite' : 'none',
                    '@keyframes pulse': {
                      '0%, 100%': { transform: 'scale(1)' },
                      '50%': { transform: 'scale(1.1)' }
                    }
                  }}
                >
                  <MicIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              {attachedFile && (
                <Chip
                  size="small"
                  label={attachedFile.name}
                  onDelete={handleRemoveFile}
                  sx={{
                    bgcolor: 'rgba(102, 126, 234, 0.1)',
                    color: '#667eea',
                    '& .MuiChip-deleteIcon': { color: '#667eea' }
                  }}
                />
              )}
              <TextField
                fullWidth
                multiline
                maxRows={4}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask DDN AI Copilot anything... (Shift+Enter for new line)"
                variant="standard"
                InputProps={{
                  disableUnderline: true,
                  sx: {
                    color: theme.textPrimary,
                    fontSize: '0.875rem'
                  }
                }}
              />
              <IconButton
                onClick={() => handleSendMessage()}
                disabled={(!inputValue.trim() && !attachedFile) || isThinking}
                sx={{
                  background: (inputValue.trim() || attachedFile) && !isThinking
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    : 'transparent',
                  color: 'white',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    transform: 'scale(1.05)'
                  },
                  '&:disabled': {
                    opacity: 0.3
                  }
                }}
              >
                <SendIcon fontSize="small" />
              </IconButton>
            </Paper>
            <Typography variant="caption" sx={{ color: theme.textSecondary, display: 'block', mt: 1 }}>
              Press Enter to send • Shift+Enter for new line
            </Typography>
          </Box>
        </Paper>
      </Box>

      {/* Right Sidebar - AI Tools */}
      <Paper sx={{
        width: 280,
        bgcolor: theme.surface,
        borderRadius: 2,
        display: 'flex',
        flexDirection: 'column',
        maxHeight: 'calc(100vh - 120px)'
      }}>
        <Box sx={{ p: 2, borderBottom: `1px solid ${theme.isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}` }}>
          <Typography variant="subtitle2" sx={{
            color: theme.textSecondary,
            fontSize: '0.75rem',
            textTransform: 'uppercase',
            fontWeight: 600
          }}>
            AI Tools
          </Typography>
        </Box>
        <Box sx={{ flex: 1, overflowY: 'auto', p: 2 }}>
          {Object.entries(aiTools).map(([section, tools]) => (
            <Box key={section} sx={{ mb: 2 }}>
              <ListItemButton
                onClick={() => toggleToolSection(section)}
                sx={{
                  py: 1,
                  px: 1.5,
                  borderRadius: 1,
                  '&:hover': { bgcolor: theme.isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)' }
                }}
              >
                <Typography variant="caption" sx={{
                  color: theme.textSecondary,
                  fontSize: '0.7rem',
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  flex: 1
                }}>
                  {section}
                </Typography>
                {expandedTools[section] ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />}
              </ListItemButton>
              <Collapse in={expandedTools[section]} timeout="auto" unmountOnExit>
                <List disablePadding>
                  {tools.map((tool) => (
                    <ListItem key={tool.name} disablePadding>
                      <ListItemButton
                        onClick={() => handleToolClick(tool.name)}
                        sx={{
                          py: 1,
                          px: 1.5,
                          borderRadius: 1,
                          border: `1px solid ${theme.isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                          mb: 1,
                          '&:hover': {
                            borderColor: '#667eea',
                            bgcolor: theme.isDark ? 'rgba(102, 126, 234, 0.1)' : 'rgba(102, 126, 234, 0.05)',
                            transform: 'translateX(4px)',
                            transition: 'all 0.2s'
                          }
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 36, color: '#667eea' }}>
                          {tool.icon}
                        </ListItemIcon>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500, color: theme.textPrimary, fontSize: '0.8rem' }}>
                            {tool.name}
                          </Typography>
                          <Typography variant="caption" sx={{ color: theme.textSecondary, fontSize: '0.7rem' }}>
                            {tool.desc}
                          </Typography>
                        </Box>
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </Collapse>
            </Box>
          ))}
        </Box>
      </Paper>

      {/* Error Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleSnackbarClose} severity="warning" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default CopilotPage
