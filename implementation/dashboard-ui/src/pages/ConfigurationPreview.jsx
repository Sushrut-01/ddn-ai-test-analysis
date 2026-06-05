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
  Skeleton,
  CircularProgress
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
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
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
import { configAPI, monitoringAPI, apiKeysAPI, settingsAPI, integrationAPI } from '../services/api'

// Default integrations (from system status)
const defaultIntegrations = [
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
    config: { project: 'DDN', url: 'https://sushrutnistane097-1768028782643.atlassian.net' }
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

  // Fetch integrations and configuration from API
  React.useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch system status to get integration statuses
        const systemStatus = await monitoringAPI.getSystemStatus()

        if (systemStatus?.components) {
          const components = systemStatus.components
          const transformedIntegrations = [
            {
              id: 'mongodb',
              name: 'MongoDB',
              icon: <StorageIcon />,
              status: components.mongodb?.status === 'healthy' ? 'connected' : 'disconnected',
              description: 'Test data storage',
              config: { failures: components.mongodb?.total_failures || 0 }
            },
            {
              id: 'postgresql',
              name: 'PostgreSQL',
              icon: <StorageIcon />,
              status: components.postgresql?.status === 'healthy' ? 'connected' : 'disconnected',
              description: 'Analysis storage',
              config: { analyses: components.postgresql?.total_analyses || 0 }
            },
            {
              id: 'pinecone',
              name: 'Pinecone',
              icon: <CloudIcon />,
              status: components.pinecone?.status === 'healthy' ? 'connected' : 'disconnected',
              description: 'Vector embeddings',
              config: { vectors: components.pinecone?.total_vectors || 0 }
            },
            {
              id: 'ai-service',
              name: 'AI Service',
              icon: <SmartToyIcon />,
              status: components.ai_service?.status === 'healthy' ? 'connected' : 'disconnected',
              description: 'AI analysis engine',
              config: {
                openai: components.ai_service?.openai_available ? 'Enabled' : 'Disabled',
                rag: components.ai_service?.rag_enabled ? 'Enabled' : 'Disabled'
              }
            },
            {
              id: 'github',
              name: 'GitHub',
              icon: <GitHubIcon />,
              status: 'connected', // Assumed connected if token exists
              description: 'PR creation & code access',
              config: {}
            },
            {
              id: 'jira',
              name: 'Jira',
              icon: <BugReportIcon />,
              status: 'connected', // Would need separate check
              description: 'Bug tracking integration',
              config: {}
            }
          ]
          setIntegrations(transformedIntegrations)
        }

        // Fetch configuration settings
        try {
          const configData = await configAPI.getAll()
          if (configData?.configs) {
            // Update AI settings from config
            const aiConfigs = configData.configs.filter(c => c.category === 'ai')
            // Could update aiSettings state here
          }
        } catch (configErr) {
          console.warn('Could not fetch configurations:', configErr)
        }

        // Fetch API keys
        try {
          const keysData = await apiKeysAPI.getAll()
          if (keysData?.keys) {
            setApiKeys(keysData.keys.map(k => ({
              id: k.id,
              name: k.name,
              key: k.key,
              created: k.created_at?.split('T')[0] || 'Unknown',
              lastUsed: k.last_used_at?.split('T')[0] || 'Never',
              status: k.status
            })))
          }
        } catch (keyErr) {
          console.warn('Could not fetch API keys:', keyErr)
        }

        // Fetch notification settings
        try {
          const notifData = await settingsAPI.notifications.get()
          if (notifData?.settings) {
            setNotificationSettings(prev => ({ ...prev, ...notifData.settings }))
          }
        } catch (notifErr) {
          console.warn('Could not fetch notification settings:', notifErr)
        }

        // Fetch analysis settings
        try {
          const analysisData = await settingsAPI.analysis.get()
          if (analysisData?.settings) {
            setAnalysisSettings(prev => ({ ...prev, ...analysisData.settings }))
          }
        } catch (analysisErr) {
          console.warn('Could not fetch analysis settings:', analysisErr)
        }

        // Fetch AI settings
        try {
          const aiData = await settingsAPI.ai.get()
          if (aiData?.settings) {
            setAiSettings(prev => ({ ...prev, ...aiData.settings }))
          }
        } catch (aiErr) {
          console.warn('Could not fetch AI settings:', aiErr)
        }

        setError(null)
      } catch (err) {
        console.error('Error fetching configuration:', err)
        setError(err.message?.includes('Network') ? 'No connection to server' : err.message)
        // Use fallback data on error
        setIntegrations(defaultIntegrations)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  // New key state
  const [newKeyName, setNewKeyName] = useState('')
  const [generatedKey, setGeneratedKey] = useState(null)

  // Generate new API key
  const handleGenerateKey = async () => {
    try {
      setSaving(true)
      const keyName = newKeyName || `API Key ${apiKeys.length + 1}`
      const response = await apiKeysAPI.create({ name: keyName, created_by: 'dashboard_user' })

      if (response?.success && response?.key) {
        // Show the generated key (only shown once!)
        setGeneratedKey(response.key.key)

        // Add to list
        setApiKeys(prev => [...prev, {
          id: response.key.id,
          name: response.key.name,
          key: response.key.key_preview,
          created: new Date().toISOString().split('T')[0],
          lastUsed: 'Never',
          status: 'active'
        }])

        setNewKeyName('')
        setAddKeyDialogOpen(false)
      }
    } catch (err) {
      console.error('Error generating API key:', err)
      setError('Failed to generate API key')
    } finally {
      setSaving(false)
    }
  }

  // Delete API key
  const handleDeleteKey = async (keyId) => {
    try {
      await apiKeysAPI.delete(keyId)
      setApiKeys(prev => prev.filter(k => k.id !== keyId))
    } catch (err) {
      console.error('Error deleting API key:', err)
    }
  }

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

  const [saveSuccess, setSaveSuccess] = useState(false)
  const [saveError, setSaveError] = useState(null)

  const handleSave = async () => {
    setSaving(true)
    setSaveError(null)
    setSaveSuccess(false)

    try {
      // Save all settings in parallel
      await Promise.all([
        settingsAPI.notifications.save(notificationSettings),
        settingsAPI.analysis.save(analysisSettings),
        settingsAPI.ai.save(aiSettings)
      ])

      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)
    } catch (err) {
      console.error('Error saving settings:', err)
      setSaveError('Failed to save settings. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const [testingConnection, setTestingConnection] = useState(false)
  const [connectionResult, setConnectionResult] = useState(null)

  const handleTestConnection = async (integration) => {
    setSelectedIntegration(integration)
    setTestConnectionDialogOpen(true)
    setTestingConnection(true)
    setConnectionResult(null)

    try {
      const response = await integrationAPI.testConnection(integration.name)
      if (response?.success && response.result) {
        setConnectionResult(response.result)
      } else {
        setConnectionResult({
          status: 'error',
          message: response?.error || 'Connection test failed'
        })
      }
    } catch (err) {
      console.error('Test connection error:', err)
      setConnectionResult({
        status: 'error',
        message: err.message || 'Failed to test connection'
      })
    } finally {
      setTestingConnection(false)
    }
  }

  const handleConnect = async (integration) => {
    try {
      const response = await integrationAPI.add({
        name: integration.name,
        type: integration.type || 'service',
        enabled: true
      })
      if (response?.success) {
        setSaveSuccess(true)
        // Refresh integrations
        fetchIntegrations()
      }
    } catch (err) {
      console.error('Connect error:', err)
      setSaveError('Failed to connect integration')
    }
  }

  const handleDisconnect = async (integration) => {
    if (!window.confirm(`Are you sure you want to disconnect ${integration.name}?`)) return

    try {
      // For now, just update the local state
      setIntegrations(prev => prev.map(i =>
        i.name === integration.name ? { ...i, connected: false } : i
      ))
      setSaveSuccess(true)
    } catch (err) {
      console.error('Disconnect error:', err)
      setSaveError('Failed to disconnect integration')
    }
  }

  const fetchIntegrations = async () => {
    try {
      const response = await integrationAPI.getAll()
      if (response?.success && response.integrations) {
        // Merge with default integrations
        const updated = defaultIntegrations.map(def => {
          const found = response.integrations.find(i => i.name.toLowerCase() === def.name.toLowerCase())
          return found ? { ...def, connected: found.status === 'connected' || found.status === 'configured' } : def
        })
        setIntegrations(updated)
      }
    } catch (err) {
      console.error('Fetch integrations error:', err)
    }
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

      {/* Save status alerts */}
      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSaveSuccess(false)}>
          Settings saved successfully!
        </Alert>
      )}
      {saveError && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setSaveError(null)}>
          {saveError}
        </Alert>
      )}

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
                        <IconButton size="small" color="error" onClick={() => handleDeleteKey(apiKey.id)}>
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
            {testingConnection ? (
              <>
                <CircularProgress size={48} sx={{ mb: 2 }} />
                <Typography variant="body1">Testing connection...</Typography>
              </>
            ) : connectionResult ? (
              <>
                <Avatar sx={{
                  width: 64,
                  height: 64,
                  bgcolor: connectionResult.status === 'connected' ? '#dcfce7' : connectionResult.status === 'configured' ? '#fef3c7' : '#fee2e2',
                  mx: 'auto',
                  mb: 2
                }}>
                  {connectionResult.status === 'connected' ? (
                    <CheckCircleIcon sx={{ fontSize: 40, color: '#166534' }} />
                  ) : connectionResult.status === 'configured' ? (
                    <CheckCircleIcon sx={{ fontSize: 40, color: '#d97706' }} />
                  ) : (
                    <ErrorOutlineIcon sx={{ fontSize: 40, color: '#dc2626' }} />
                  )}
                </Avatar>
                <Typography
                  variant="h6"
                  color={connectionResult.status === 'connected' ? 'success.main' : connectionResult.status === 'configured' ? 'warning.main' : 'error.main'}
                >
                  {connectionResult.status === 'connected' ? 'Connection Successful!' :
                   connectionResult.status === 'configured' ? 'Configured (Not Verified)' : 'Connection Failed'}
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  {connectionResult.message || `${selectedIntegration?.name} status: ${connectionResult.status}`}
                </Typography>
              </>
            ) : (
              <Typography variant="body2" color="textSecondary">
                Click Test to check connection status
              </Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestConnectionDialogOpen(false)}>Close</Button>
          <Button
            variant="contained"
            onClick={() => handleTestConnection(selectedIntegration)}
            disabled={testingConnection}
          >
            {testingConnection ? 'Testing...' : 'Test Again'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add API Key Dialog */}
      <Dialog open={addKeyDialogOpen} onClose={() => { setAddKeyDialogOpen(false); setGeneratedKey(null); }} maxWidth="sm" fullWidth>
        <DialogTitle>Generate New API Key</DialogTitle>
        <DialogContent>
          {generatedKey ? (
            <>
              <Alert severity="success" sx={{ mt: 2 }}>
                API key generated successfully! Copy it now - it won't be shown again.
              </Alert>
              <TextField
                fullWidth
                label="Your API Key"
                value={generatedKey}
                sx={{ mt: 2, fontFamily: 'monospace' }}
                InputProps={{
                  readOnly: true,
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => navigator.clipboard.writeText(generatedKey)}>
                        <ContentCopyIcon />
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
            </>
          ) : (
            <>
              <TextField
                fullWidth
                label="Key Name"
                placeholder="e.g., Production API Key"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                sx={{ mt: 2 }}
              />
              <Alert severity="warning" sx={{ mt: 2 }}>
                The API key will only be shown once after generation. Make sure to copy and store it securely.
              </Alert>
            </>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => { setAddKeyDialogOpen(false); setGeneratedKey(null); }}>
            {generatedKey ? 'Done' : 'Cancel'}
          </Button>
          {!generatedKey && (
            <Button variant="contained" startIcon={saving ? <CircularProgress size={16} /> : <KeyIcon />} onClick={handleGenerateKey} disabled={saving}>
              Generate Key
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default ConfigurationPreview
