import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  TextField,
  MenuItem,
  Switch,
  FormControlLabel,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Alert,
  Tooltip,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
  FormControl,
  InputLabel,
  Select,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Avatar,
  Badge,
  LinearProgress,
  Skeleton
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import SettingsIcon from '@mui/icons-material/Settings'
import ApiIcon from '@mui/icons-material/Api'
import IntegrationInstructionsIcon from '@mui/icons-material/IntegrationInstructions'
import NotificationsIcon from '@mui/icons-material/Notifications'
import SecurityIcon from '@mui/icons-material/Security'
import StorageIcon from '@mui/icons-material/Storage'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import GitHubIcon from '@mui/icons-material/GitHub'
import BugReportIcon from '@mui/icons-material/BugReport'
import EmailIcon from '@mui/icons-material/Email'
import WebhookIcon from '@mui/icons-material/Webhook'
import KeyIcon from '@mui/icons-material/Key'
import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import RefreshIcon from '@mui/icons-material/Refresh'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import WarningIcon from '@mui/icons-material/Warning'
import SaveIcon from '@mui/icons-material/Save'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import EditIcon from '@mui/icons-material/Edit'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import TuneIcon from '@mui/icons-material/Tune'
import SpeedIcon from '@mui/icons-material/Speed'
import BuildIcon from '@mui/icons-material/Build'
import CloudIcon from '@mui/icons-material/Cloud'
import DataObjectIcon from '@mui/icons-material/DataObject'
import ChatIcon from '@mui/icons-material/Chat'
import LinkIcon from '@mui/icons-material/Link'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'

// Mock integrations
const mockIntegrations = [
  {
    id: 'github',
    name: 'GitHub',
    icon: <GitHubIcon />,
    status: 'connected',
    description: 'Repository access for PR creation',
    config: { org: 'company', repos: ['main-app', 'api-service'] }
  },
  {
    id: 'jira',
    name: 'Jira',
    icon: <BugReportIcon />,
    status: 'connected',
    description: 'Bug tracking and issue creation',
    config: { project: 'DDN', url: 'https://company.atlassian.net' }
  },
  {
    id: 'slack',
    name: 'Slack',
    icon: <ChatIcon />,
    status: 'connected',
    description: 'Notifications and alerts',
    config: { channel: '#test-failures', webhook: '****' }
  },
  {
    id: 'jenkins',
    name: 'Jenkins',
    icon: <BuildIcon />,
    status: 'connected',
    description: 'CI/CD pipeline integration',
    config: { url: 'https://jenkins.company.com', job: 'DDN-Nightly' }
  },
  {
    id: 'teams',
    name: 'Microsoft Teams',
    icon: <ChatIcon />,
    status: 'disconnected',
    description: 'Team notifications',
    config: {}
  },
  {
    id: 'pagerduty',
    name: 'PagerDuty',
    icon: <NotificationsIcon />,
    status: 'disconnected',
    description: 'Incident management',
    config: {}
  }
]

// Mock API Keys
const mockApiKeys = [
  { id: 1, name: 'Production API Key', key: 'ddn_prod_****', created: '2024-01-15', lastUsed: '2024-11-28', status: 'active' },
  { id: 2, name: 'Staging API Key', key: 'ddn_stag_****', created: '2024-03-20', lastUsed: '2024-11-27', status: 'active' },
  { id: 3, name: 'Development Key', key: 'ddn_dev_****', created: '2024-06-10', lastUsed: '2024-11-25', status: 'active' },
  { id: 4, name: 'Old Integration Key', key: 'ddn_old_****', created: '2023-08-01', lastUsed: '2024-01-15', status: 'expired' }
]

function ConfigurationPreview() {
  const [activeTab, setActiveTab] = useState(0)
  const [showApiKey, setShowApiKey] = useState({})
  const [saving, setSaving] = useState(false)
  const [addKeyDialogOpen, setAddKeyDialogOpen] = useState(false)
  const [testConnectionDialogOpen, setTestConnectionDialogOpen] = useState(false)
  const [selectedIntegration, setSelectedIntegration] = useState(null)

  // Real data state
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [integrations, setIntegrations] = useState([])
  const [apiKeys, setApiKeys] = useState([])

  // Fetch integrations and API keys from API
  React.useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch integrations status
        const intResponse = await fetch('http://localhost:5001/api/monitoring/services')
        if (intResponse.ok) {
          const data = await intResponse.json()
          const services = data?.services || data || []
          const transformedIntegrations = services.map(s => ({
            id: s.name?.toLowerCase().replace(/\s+/g, '-') || s.id,
            name: s.name || 'Unknown',
            icon: s.name?.toLowerCase() === 'github' ? <GitHubIcon /> :
                  s.name?.toLowerCase() === 'jira' ? <BugReportIcon /> :
                  s.name?.toLowerCase() === 'slack' ? <ChatIcon /> :
                  s.name?.toLowerCase() === 'jenkins' ? <BuildIcon /> :
                  <IntegrationInstructionsIcon />,
            status: s.status === 'healthy' || s.status === 'running' ? 'connected' : 'disconnected',
            description: s.description || s.name || '-',
            config: s.config || {}
          }))
          setIntegrations(transformedIntegrations)
        }
        setError(null)
      } catch (err) {
        console.error('Error fetching configuration:', err)
        setError(err.message?.includes('Network') ? 'No connection to server' : err.message)
        setIntegrations([])
        setApiKeys([])
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  // AI Settings
  const [aiSettings, setAiSettings] = useState({
    model: 'gemini-pro',
    confidenceThreshold: 75,
    maxRetries: 3,
    enableCRAG: true,
    enableReAct: true,
    autoRefine: false,
    refinementIterations: 2
  })

  // Notification Settings
  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    slackNotifications: true,
    teamsNotifications: false,
    onNewFailure: true,
    onAnalysisComplete: true,
    onLowConfidence: true,
    onBugCreated: false,
    dailyDigest: true,
    digestTime: '09:00'
  })

  // Analysis Settings
  const [analysisSettings, setAnalysisSettings] = useState({
    autoTrigger: true,
    triggerDelay: 5,
    batchSize: 10,
    parallelAnalysis: 3,
    retentionDays: 90,
    archiveEnabled: true
  })

  const handleSave = () => {
    setSaving(true)
    setTimeout(() => setSaving(false), 1500)
  }

  const handleTestConnection = (integration) => {
    setSelectedIntegration(integration)
    setTestConnectionDialogOpen(true)
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc', pb: 4 }}>
      {/* Header */}
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 3,
          borderRadius: 3,
          background: 'linear-gradient(135deg, #475569 0%, #334155 100%)',
          color: 'white'
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h5" fontWeight={600} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SettingsIcon /> Configuration & Settings
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
              Manage integrations, API keys, AI settings, and notifications
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={saving ? <RefreshIcon /> : <SaveIcon />}
            onClick={handleSave}
            disabled={saving}
            sx={{ bgcolor: 'white', color: '#334155', '&:hover': { bgcolor: '#f1f5f9' } }}
          >
            {saving ? 'Saving...' : 'Save All Changes'}
          </Button>
        </Box>
      </Paper>

      {/* Tabs */}
      <Paper elevation={0} sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
        <Tabs
          value={activeTab}
          onChange={(e, v) => setActiveTab(v)}
          sx={{ borderBottom: '1px solid', borderColor: 'divider', px: 2 }}
        >
          <Tab icon={<IntegrationInstructionsIcon />} label="Integrations" iconPosition="start" />
          <Tab icon={<KeyIcon />} label="API Keys" iconPosition="start" />
          <Tab icon={<SmartToyIcon />} label="AI Settings" iconPosition="start" />
          <Tab icon={<NotificationsIcon />} label="Notifications" iconPosition="start" />
          <Tab icon={<TuneIcon />} label="Analysis Settings" iconPosition="start" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {/* Integrations Tab */}
          {activeTab === 0 && (
            <>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">Connected Services</Typography>
                <Button variant="outlined" startIcon={<AddIcon />}>
                  Add Integration
                </Button>
              </Box>

              <Grid container spacing={3}>
                {loading ? (
                  [...Array(4)].map((_, idx) => (
                    <Grid item xs={12} md={6} key={idx}>
                      <Card variant="outlined">
                        <CardContent>
                          <Box sx={{ display: 'flex', gap: 2 }}>
                            <Skeleton variant="circular" width={48} height={48} />
                            <Box sx={{ flex: 1 }}>
                              <Skeleton width="60%" height={24} />
                              <Skeleton width="80%" height={20} />
                            </Box>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))
                ) : error ? (
                  <Grid item xs={12}>
                    <Alert severity="error">{error}</Alert>
                  </Grid>
                ) : integrations.length === 0 ? (
                  <Grid item xs={12}>
                    <Alert severity="info">No integrations configured. Click "Add Integration" to connect services.</Alert>
                  </Grid>
                ) : integrations.map((integration) => (
                  <Grid item xs={12} md={6} key={integration.id}>
                    <Card
                      variant="outlined"
                      sx={{
                        opacity: integration.status === 'disconnected' ? 0.6 : 1,
                        border: integration.status === 'connected' ? '1px solid #10b981' : '1px solid #e2e8f0'
                      }}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <Box sx={{ display: 'flex', gap: 2 }}>
                            <Avatar sx={{ bgcolor: integration.status === 'connected' ? '#10b981' : '#94a3b8' }}>
                              {integration.icon}
                            </Avatar>
                            <Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="subtitle1" fontWeight={600}>{integration.name}</Typography>
                                <Chip
                                  size="small"
                                  label={integration.status === 'connected' ? 'Connected' : 'Disconnected'}
                                  sx={{
                                    bgcolor: integration.status === 'connected' ? '#dcfce7' : '#fee2e2',
                                    color: integration.status === 'connected' ? '#166534' : '#991b1b',
                                    fontSize: '0.65rem'
                                  }}
                                />
                              </Box>
                              <Typography variant="body2" color="textSecondary">{integration.description}</Typography>
                            </Box>
                          </Box>
                        </Box>

                        {integration.status === 'connected' && (
                          <Box sx={{ mt: 2, p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
                            <Typography variant="caption" color="textSecondary">Configuration</Typography>
                            <Box sx={{ mt: 0.5 }}>
                              {Object.entries(integration.config).map(([key, value]) => (
                                <Typography key={key} variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                                  {key}: {Array.isArray(value) ? value.join(', ') : value}
                                </Typography>
                              ))}
                            </Box>
                          </Box>
                        )}

                        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                          {integration.status === 'connected' ? (
                            <>
                              <Button size="small" startIcon={<EditIcon />}>Configure</Button>
                              <Button size="small" startIcon={<PlayArrowIcon />} onClick={() => handleTestConnection(integration)}>
                                Test
                              </Button>
                              <Button size="small" color="error" startIcon={<LinkIcon />}>Disconnect</Button>
                            </>
                          ) : (
                            <Button size="small" variant="contained" startIcon={<LinkIcon />}>
                              Connect
                            </Button>
                          )}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </>
          )}

          {/* API Keys Tab */}
          {activeTab === 1 && (
            <>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Box>
                  <Typography variant="h6">API Keys</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Manage API keys for external integrations
                  </Typography>
                </Box>
                <Button variant="contained" startIcon={<AddIcon />} onClick={() => setAddKeyDialogOpen(true)}>
                  Generate New Key
                </Button>
              </Box>

              <Alert severity="warning" sx={{ mb: 3 }}>
                API keys provide full access to your account. Keep them secure and never share them publicly.
              </Alert>

              <List>
                {loading ? (
                  [...Array(3)].map((_, idx) => (
                    <ListItem key={idx} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2, mb: 1 }}>
                      <ListItemIcon><Skeleton variant="circular" width={24} height={24} /></ListItemIcon>
                      <ListItemText primary={<Skeleton width="40%" />} secondary={<Skeleton width="60%" />} />
                    </ListItem>
                  ))
                ) : apiKeys.length === 0 ? (
                  <ListItem sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                    <ListItemText primary="No API keys configured" secondary="Click 'Generate New Key' to create one" />
                  </ListItem>
                ) : apiKeys.map((apiKey) => (
                  <ListItem
                    key={apiKey.id}
                    sx={{
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 2,
                      mb: 1,
                      bgcolor: apiKey.status === 'expired' ? alpha('#f59e0b', 0.05) : 'white'
                    }}
                  >
                    <ListItemIcon>
                      <KeyIcon sx={{ color: apiKey.status === 'active' ? '#10b981' : '#f59e0b' }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography fontWeight={600}>{apiKey.name}</Typography>
                          <Chip
                            size="small"
                            label={apiKey.status}
                            sx={{
                              bgcolor: apiKey.status === 'active' ? '#dcfce7' : '#fef3c7',
                              color: apiKey.status === 'active' ? '#166534' : '#92400e',
                              fontSize: '0.65rem'
                            }}
                          />
                        </Box>
                      }
                      secondary={
                        <Box sx={{ display: 'flex', gap: 2, mt: 0.5 }}>
                          <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                            {showApiKey[apiKey.id] ? 'ddn_prod_a1b2c3d4e5f6g7h8' : apiKey.key}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            Created: {apiKey.created}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            Last used: {apiKey.lastUsed}
                          </Typography>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Tooltip title={showApiKey[apiKey.id] ? 'Hide' : 'Show'}>
                        <IconButton
                          size="small"
                          onClick={() => setShowApiKey(prev => ({ ...prev, [apiKey.id]: !prev[apiKey.id] }))}
                        >
                          {showApiKey[apiKey.id] ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Copy">
                        <IconButton size="small">
                          <ContentCopyIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Regenerate">
                        <IconButton size="small">
                          <RefreshIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton size="small" color="error">
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </>
          )}

          {/* AI Settings Tab */}
          {activeTab === 2 && (
            <>
              <Typography variant="h6" sx={{ mb: 3 }}>AI Analysis Configuration</Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                        <SmartToyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Model Settings
                      </Typography>

                      <FormControl fullWidth sx={{ mb: 3 }}>
                        <InputLabel>AI Model</InputLabel>
                        <Select
                          value={aiSettings.model}
                          label="AI Model"
                          onChange={(e) => setAiSettings({ ...aiSettings, model: e.target.value })}
                        >
                          <MenuItem value="gemini-pro">Gemini Pro</MenuItem>
                          <MenuItem value="gemini-pro-vision">Gemini Pro Vision</MenuItem>
                          <MenuItem value="gpt-4">GPT-4</MenuItem>
                          <MenuItem value="gpt-4-turbo">GPT-4 Turbo</MenuItem>
                          <MenuItem value="claude-3">Claude 3</MenuItem>
                        </Select>
                      </FormControl>

                      <Box sx={{ mb: 3 }}>
                        <Typography variant="body2" gutterBottom>
                          Confidence Threshold: {aiSettings.confidenceThreshold}%
                        </Typography>
                        <Slider
                          value={aiSettings.confidenceThreshold}
                          onChange={(e, v) => setAiSettings({ ...aiSettings, confidenceThreshold: v })}
                          min={50}
                          max={100}
                          marks={[
                            { value: 50, label: '50%' },
                            { value: 75, label: '75%' },
                            { value: 100, label: '100%' }
                          ]}
                        />
                        <Typography variant="caption" color="textSecondary">
                          Analyses below this threshold will be flagged for manual review
                        </Typography>
                      </Box>

                      <TextField
                        fullWidth
                        type="number"
                        label="Max Retries"
                        value={aiSettings.maxRetries}
                        onChange={(e) => setAiSettings({ ...aiSettings, maxRetries: parseInt(e.target.value) })}
                        InputProps={{ inputProps: { min: 1, max: 5 } }}
                      />
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                        <TuneIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Analysis Features
                      </Typography>

                      <List>
                        <ListItem>
                          <ListItemText
                            primary="CRAG (Corrective RAG)"
                            secondary="Use knowledge base for context-aware analysis"
                          />
                          <Switch
                            checked={aiSettings.enableCRAG}
                            onChange={(e) => setAiSettings({ ...aiSettings, enableCRAG: e.target.checked })}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="ReAct Agent"
                            secondary="Enable reasoning and action chain for complex errors"
                          />
                          <Switch
                            checked={aiSettings.enableReAct}
                            onChange={(e) => setAiSettings({ ...aiSettings, enableReAct: e.target.checked })}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="Auto-Refinement"
                            secondary="Automatically refine low-confidence analyses"
                          />
                          <Switch
                            checked={aiSettings.autoRefine}
                            onChange={(e) => setAiSettings({ ...aiSettings, autoRefine: e.target.checked })}
                          />
                        </ListItem>
                      </List>

                      {aiSettings.autoRefine && (
                        <TextField
                          fullWidth
                          type="number"
                          label="Max Refinement Iterations"
                          value={aiSettings.refinementIterations}
                          onChange={(e) => setAiSettings({ ...aiSettings, refinementIterations: parseInt(e.target.value) })}
                          InputProps={{ inputProps: { min: 1, max: 5 } }}
                          sx={{ mt: 2 }}
                        />
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </>
          )}

          {/* Notifications Tab */}
          {activeTab === 3 && (
            <>
              <Typography variant="h6" sx={{ mb: 3 }}>Notification Preferences</Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                        Channels
                      </Typography>
                      <List>
                        <ListItem>
                          <ListItemIcon><EmailIcon /></ListItemIcon>
                          <ListItemText primary="Email Notifications" />
                          <Switch
                            checked={notificationSettings.emailNotifications}
                            onChange={(e) => setNotificationSettings({ ...notificationSettings, emailNotifications: e.target.checked })}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon><ChatIcon /></ListItemIcon>
                          <ListItemText primary="Slack Notifications" />
                          <Switch
                            checked={notificationSettings.slackNotifications}
                            onChange={(e) => setNotificationSettings({ ...notificationSettings, slackNotifications: e.target.checked })}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon><ChatIcon /></ListItemIcon>
                          <ListItemText primary="Microsoft Teams" />
                          <Switch
                            checked={notificationSettings.teamsNotifications}
                            onChange={(e) => setNotificationSettings({ ...notificationSettings, teamsNotifications: e.target.checked })}
                          />
                        </ListItem>
                      </List>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                        Events
                      </Typography>
                      <List>
                        <ListItem>
                          <ListItemText primary="New Test Failure" secondary="When a new failure is detected" />
                          <Switch
                            checked={notificationSettings.onNewFailure}
                            onChange={(e) => setNotificationSettings({ ...notificationSettings, onNewFailure: e.target.checked })}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText primary="Analysis Complete" secondary="When AI analysis finishes" />
                          <Switch
                            checked={notificationSettings.onAnalysisComplete}
                            onChange={(e) => setNotificationSettings({ ...notificationSettings, onAnalysisComplete: e.target.checked })}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText primary="Low Confidence" secondary="When analysis confidence is below threshold" />
                          <Switch
                            checked={notificationSettings.onLowConfidence}
                            onChange={(e) => setNotificationSettings({ ...notificationSettings, onLowConfidence: e.target.checked })}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText primary="Bug Created" secondary="When a Jira bug is created" />
                          <Switch
                            checked={notificationSettings.onBugCreated}
                            onChange={(e) => setNotificationSettings({ ...notificationSettings, onBugCreated: e.target.checked })}
                          />
                        </ListItem>
                      </List>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                        Daily Digest
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={notificationSettings.dailyDigest}
                              onChange={(e) => setNotificationSettings({ ...notificationSettings, dailyDigest: e.target.checked })}
                            />
                          }
                          label="Send daily summary email"
                        />
                        {notificationSettings.dailyDigest && (
                          <TextField
                            type="time"
                            label="Send Time"
                            value={notificationSettings.digestTime}
                            onChange={(e) => setNotificationSettings({ ...notificationSettings, digestTime: e.target.value })}
                            size="small"
                            sx={{ width: 150 }}
                          />
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </>
          )}

          {/* Analysis Settings Tab */}
          {activeTab === 4 && (
            <>
              <Typography variant="h6" sx={{ mb: 3 }}>Analysis Pipeline Settings</Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                        <PlayArrowIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Trigger Settings
                      </Typography>

                      <List>
                        <ListItem>
                          <ListItemText
                            primary="Auto-Trigger Analysis"
                            secondary="Automatically analyze new failures"
                          />
                          <Switch
                            checked={analysisSettings.autoTrigger}
                            onChange={(e) => setAnalysisSettings({ ...analysisSettings, autoTrigger: e.target.checked })}
                          />
                        </ListItem>
                      </List>

                      {analysisSettings.autoTrigger && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="body2" gutterBottom>
                            Trigger Delay: {analysisSettings.triggerDelay} minutes
                          </Typography>
                          <Slider
                            value={analysisSettings.triggerDelay}
                            onChange={(e, v) => setAnalysisSettings({ ...analysisSettings, triggerDelay: v })}
                            min={0}
                            max={30}
                            marks={[
                              { value: 0, label: 'Immediate' },
                              { value: 15, label: '15m' },
                              { value: 30, label: '30m' }
                            ]}
                          />
                          <Typography variant="caption" color="textSecondary">
                            Wait time before triggering analysis after failure detection
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                        <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Performance Settings
                      </Typography>

                      <TextField
                        fullWidth
                        type="number"
                        label="Batch Size"
                        value={analysisSettings.batchSize}
                        onChange={(e) => setAnalysisSettings({ ...analysisSettings, batchSize: parseInt(e.target.value) })}
                        helperText="Max failures to process in one batch"
                        sx={{ mb: 2 }}
                      />

                      <TextField
                        fullWidth
                        type="number"
                        label="Parallel Analysis"
                        value={analysisSettings.parallelAnalysis}
                        onChange={(e) => setAnalysisSettings({ ...analysisSettings, parallelAnalysis: parseInt(e.target.value) })}
                        helperText="Number of concurrent analyses"
                      />
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                        <StorageIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Data Retention
                      </Typography>

                      <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            type="number"
                            label="Retention Period (days)"
                            value={analysisSettings.retentionDays}
                            onChange={(e) => setAnalysisSettings({ ...analysisSettings, retentionDays: parseInt(e.target.value) })}
                            helperText="How long to keep analysis data"
                          />
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <FormControlLabel
                            control={
                              <Switch
                                checked={analysisSettings.archiveEnabled}
                                onChange={(e) => setAnalysisSettings({ ...analysisSettings, archiveEnabled: e.target.checked })}
                              />
                            }
                            label="Archive old data instead of deleting"
                          />
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </>
          )}
        </Box>
      </Paper>

      {/* Test Connection Dialog */}
      <Dialog open={testConnectionDialogOpen} onClose={() => setTestConnectionDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Test Connection: {selectedIntegration?.name}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Avatar sx={{ width: 64, height: 64, bgcolor: '#dcfce7', mx: 'auto', mb: 2 }}>
              <CheckCircleIcon sx={{ fontSize: 40, color: '#166534' }} />
            </Avatar>
            <Typography variant="h6" color="success.main">Connection Successful!</Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
              {selectedIntegration?.name} is properly configured and responding.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestConnectionDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Add API Key Dialog */}
      <Dialog open={addKeyDialogOpen} onClose={() => setAddKeyDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Generate New API Key</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Key Name"
            placeholder="e.g., Production API Key"
            sx={{ mt: 2 }}
          />
          <Alert severity="warning" sx={{ mt: 2 }}>
            The API key will only be shown once after generation. Make sure to copy and store it securely.
          </Alert>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setAddKeyDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" startIcon={<KeyIcon />}>
            Generate Key
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default ConfigurationPreview
