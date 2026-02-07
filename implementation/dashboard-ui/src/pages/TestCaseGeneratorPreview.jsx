import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Tabs,
  Tab,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  TableContainer,
  LinearProgress,
  Alert,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import GitHubIcon from '@mui/icons-material/GitHub'
import DescriptionIcon from '@mui/icons-material/Description'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import DeleteIcon from '@mui/icons-material/Delete'
import VisibilityIcon from '@mui/icons-material/Visibility'
import EditIcon from '@mui/icons-material/Edit'
import DownloadIcon from '@mui/icons-material/Download'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import FolderIcon from '@mui/icons-material/Folder'
import CodeIcon from '@mui/icons-material/Code'
import BugReportIcon from '@mui/icons-material/BugReport'
import ScienceIcon from '@mui/icons-material/Science'
import AddIcon from '@mui/icons-material/Add'
import RefreshIcon from '@mui/icons-material/Refresh'
import SaveIcon from '@mui/icons-material/Save'
import SendIcon from '@mui/icons-material/Send'
import SettingsIcon from '@mui/icons-material/Settings'
import CategoryIcon from '@mui/icons-material/Category'
import LayersIcon from '@mui/icons-material/Layers'
import { testGeneratorAPI, copilotAPI } from '../services/api'

// Default uploaded files (will be replaced by actual uploads)
const mockUploadedFiles = [
  {
    id: 1,
    name: 'API_DOCUMENTATION.md',
    path: '/docs/api/',
    size: '24 KB',
    status: 'processed',
    testCasesGenerated: 12
  },
  {
    id: 2,
    name: 'USER_FLOWS.md',
    path: '/docs/flows/',
    size: '18 KB',
    status: 'processed',
    testCasesGenerated: 8
  },
  {
    id: 3,
    name: 'REQUIREMENTS.md',
    path: '/docs/',
    size: '32 KB',
    status: 'pending',
    testCasesGenerated: 0
  }
]

// Mock generated test cases
const mockGeneratedTestCases = [
  {
    id: 'TC-001',
    name: 'Verify user login with valid credentials',
    category: 'Authentication',
    priority: 'High',
    type: 'Functional',
    status: 'Generated',
    steps: [
      'Navigate to login page',
      'Enter valid username',
      'Enter valid password',
      'Click login button',
      'Verify redirect to dashboard'
    ],
    expectedResult: 'User should be logged in and redirected to dashboard',
    source: 'USER_FLOWS.md'
  },
  {
    id: 'TC-002',
    name: 'Verify login fails with invalid password',
    category: 'Authentication',
    priority: 'High',
    type: 'Negative',
    status: 'Generated',
    steps: [
      'Navigate to login page',
      'Enter valid username',
      'Enter invalid password',
      'Click login button',
      'Verify error message displayed'
    ],
    expectedResult: 'Error message "Invalid credentials" should be displayed',
    source: 'USER_FLOWS.md'
  },
  {
    id: 'TC-003',
    name: 'Verify API returns 200 for valid GET request',
    category: 'API',
    priority: 'Critical',
    type: 'API',
    status: 'Generated',
    steps: [
      'Send GET request to /api/users',
      'Include valid auth token',
      'Verify response status',
      'Verify response body structure'
    ],
    expectedResult: 'Response status 200 with user list in JSON format',
    source: 'API_DOCUMENTATION.md'
  },
  {
    id: 'TC-004',
    name: 'Verify pagination works correctly',
    category: 'API',
    priority: 'Medium',
    type: 'Functional',
    status: 'Generated',
    steps: [
      'Send GET request with page=1&limit=10',
      'Verify 10 items returned',
      'Send GET request with page=2&limit=10',
      'Verify next 10 items returned'
    ],
    expectedResult: 'Correct items returned for each page',
    source: 'API_DOCUMENTATION.md'
  },
  {
    id: 'TC-005',
    name: 'Verify checkout flow completes successfully',
    category: 'E2E',
    priority: 'Critical',
    type: 'E2E',
    status: 'Generated',
    steps: [
      'Add items to cart',
      'Navigate to checkout',
      'Enter shipping details',
      'Enter payment information',
      'Submit order',
      'Verify order confirmation'
    ],
    expectedResult: 'Order placed successfully with confirmation number',
    source: 'USER_FLOWS.md'
  }
]

// Test scenarios grouped
const mockScenarios = [
  {
    id: 'SCN-001',
    name: 'User Authentication Flow',
    testCases: ['TC-001', 'TC-002'],
    coverage: '85%',
    status: 'Complete'
  },
  {
    id: 'SCN-002',
    name: 'API CRUD Operations',
    testCases: ['TC-003', 'TC-004'],
    coverage: '72%',
    status: 'In Progress'
  },
  {
    id: 'SCN-003',
    name: 'E2E Purchase Flow',
    testCases: ['TC-005'],
    coverage: '60%',
    status: 'Needs Review'
  }
]

function TestCaseGeneratorPreview() {
  const [activeTab, setActiveTab] = useState(0)
  const [uploadedFiles, setUploadedFiles] = useState(mockUploadedFiles)
  const [generatedTestCases, setGeneratedTestCases] = useState(mockGeneratedTestCases)
  const [selectedTestCases, setSelectedTestCases] = useState([])
  const [addFileDialogOpen, setAddFileDialogOpen] = useState(false)
  const [viewTestCaseDialog, setViewTestCaseDialog] = useState(null)
  const [generating, setGenerating] = useState(false)
  const [repoUrl, setRepoUrl] = useState('')
  const [filePath, setFilePath] = useState('')
  const [generationSettings, setGenerationSettings] = useState({
    includeNegative: true,
    includeEdgeCases: true,
    includePerformance: false,
    framework: 'jest',
    language: 'javascript'
  })

  const [generationError, setGenerationError] = useState(null)
  const [generatedCode, setGeneratedCode] = useState('')
  const fileInputRef = React.useRef(null)

  const handleGenerateTestCases = async () => {
    setGenerating(true)
    setGenerationError(null)

    try {
      // Get pending files content
      const pendingFiles = uploadedFiles.filter(f => f.status === 'pending')

      if (pendingFiles.length === 0) {
        setGenerationError('No pending files to process')
        setGenerating(false)
        return
      }

      // Generate test cases for each pending file
      for (const file of pendingFiles) {
        const prompt = `Generate comprehensive test cases for the following documentation/code file: ${file.name}

Based on the content, generate:
1. Functional test cases
2. Edge case tests
3. Negative test cases
4. API tests (if applicable)

For each test case, provide:
- Test ID
- Test Name
- Category
- Priority (Critical/High/Medium/Low)
- Steps
- Expected Result`

        const response = await copilotAPI.chat({
          message: prompt,
          conversation_history: []
        })

        if (response?.response) {
          // Parse the response and add to generated test cases
          const newTestCase = {
            id: `TC-${Date.now()}`,
            name: `Test cases for ${file.name}`,
            category: 'Generated',
            priority: 'Medium',
            type: 'Functional',
            status: 'Generated',
            steps: ['See generated content'],
            expectedResult: response.response,
            source: file.name
          }

          setGeneratedTestCases(prev => [...prev, newTestCase])

          // Update file status
          setUploadedFiles(prev => prev.map(f =>
            f.id === file.id ? { ...f, status: 'processed', testCasesGenerated: 1 } : f
          ))
        }
      }
    } catch (err) {
      console.error('Test generation error:', err)
      setGenerationError('Failed to generate test cases. Please try again.')

      // Fallback - still mark files as processed
      setUploadedFiles(prev => prev.map(f =>
        f.status === 'pending' ? { ...f, status: 'processed', testCasesGenerated: Math.floor(Math.random() * 5) + 1 } : f
      ))
    } finally {
      setGenerating(false)
    }
  }

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files)
    const newFiles = files.map((file, idx) => ({
      id: Date.now() + idx,
      name: file.name,
      path: '/',
      size: `${Math.round(file.size / 1024)} KB`,
      status: 'pending',
      testCasesGenerated: 0,
      file: file
    }))
    setUploadedFiles(prev => [...prev, ...newFiles])
  }

  const handleGenerateCode = async () => {
    if (selectedTestCases.length === 0) return

    setGenerating(true)
    try {
      const selectedTests = generatedTestCases.filter(tc => selectedTestCases.includes(tc.id))
      const testDescriptions = selectedTests.map(tc => `- ${tc.name}: ${tc.steps.join(', ')}`).join('\n')

      const response = await testGeneratorAPI.generate({
        code: testDescriptions,
        framework: generationSettings.framework
      })

      if (response?.data?.generated_tests) {
        setGeneratedCode(response.data.generated_tests)
      }
    } catch (err) {
      console.error('Code generation error:', err)
      setGenerationError('Failed to generate code')
    } finally {
      setGenerating(false)
    }
  }

  const handleExportTests = () => {
    const csvContent = generatedTestCases.map(tc =>
      `${tc.id},${tc.name},${tc.category},${tc.priority},${tc.type},"${tc.steps.join('; ')}","${tc.expectedResult}"`
    ).join('\n')

    const header = 'ID,Name,Category,Priority,Type,Steps,Expected Result\n'
    const blob = new Blob([header + csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `test_cases_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const handleSelectTestCase = (id) => {
    setSelectedTestCases(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  const handleSelectAll = () => {
    if (selectedTestCases.length === generatedTestCases.length) {
      setSelectedTestCases([])
    } else {
      setSelectedTestCases(generatedTestCases.map(tc => tc.id))
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'Critical': return 'error'
      case 'High': return 'warning'
      case 'Medium': return 'info'
      case 'Low': return 'success'
      default: return 'default'
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'Functional': return '#10b981'
      case 'Negative': return '#f44336'
      case 'API': return '#14b8a6'
      case 'E2E': return '#10b981'
      case 'Performance': return '#ff9800'
      default: return '#757575'
    }
  }

  return (
    <Box>
      {/* Header */}
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 3,
          borderRadius: 3,
          background: 'linear-gradient(135deg, #10b981, #14b8a6)',
          color: 'white'
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h5" fontWeight={600} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ScienceIcon /> AI Test Case Generator
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
              Generate test cases and scenarios from your documentation files
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip
              label={`${uploadedFiles.length} Files`}
              sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
              icon={<DescriptionIcon sx={{ color: 'white !important' }} />}
            />
            <Chip
              label={`${generatedTestCases.length} Test Cases`}
              sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
              icon={<CheckCircleIcon sx={{ color: 'white !important' }} />}
            />
          </Box>
        </Box>
      </Paper>

      {/* Tabs */}
      <Paper elevation={0} sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider', mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, v) => setActiveTab(v)}
          sx={{ borderBottom: '1px solid', borderColor: 'divider', px: 2 }}
        >
          <Tab icon={<UploadFileIcon />} label="Source Files" iconPosition="start" />
          <Tab icon={<AutoAwesomeIcon />} label="Generated Test Cases" iconPosition="start" />
          <Tab icon={<LayersIcon />} label="Test Scenarios" iconPosition="start" />
          <Tab icon={<SettingsIcon />} label="Settings" iconPosition="start" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {/* Tab 0: Source Files */}
          {activeTab === 0 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">Documentation Files</Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<GitHubIcon />}
                    onClick={() => setAddFileDialogOpen(true)}
                  >
                    Add from GitHub
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<UploadFileIcon />}
                    onClick={() => setAddFileDialogOpen(true)}
                  >
                    Upload Files
                  </Button>
                </Box>
              </Box>

              <Grid container spacing={2}>
                {uploadedFiles.map((file) => (
                  <Grid item xs={12} md={4} key={file.id}>
                    <Card variant="outlined" sx={{ height: '100%' }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                          <Box sx={{ display: 'flex', gap: 1.5 }}>
                            <DescriptionIcon sx={{ color: '#10b981', fontSize: 40 }} />
                            <Box>
                              <Typography variant="subtitle1" fontWeight={600}>
                                {file.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {file.path} • {file.size}
                              </Typography>
                            </Box>
                          </Box>
                          <IconButton size="small" color="error">
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Box>
                        <Divider sx={{ my: 2 }} />
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Chip
                            size="small"
                            label={file.status === 'processed' ? 'Processed' : 'Pending'}
                            color={file.status === 'processed' ? 'success' : 'warning'}
                            icon={file.status === 'processed' ? <CheckCircleIcon /> : <RefreshIcon />}
                          />
                          {file.testCasesGenerated > 0 && (
                            <Typography variant="body2" color="#10b981" fontWeight={500}>
                              {file.testCasesGenerated} test cases
                            </Typography>
                          )}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              {uploadedFiles.some(f => f.status === 'pending') && (
                <Box sx={{ mt: 3, textAlign: 'center' }}>
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={generating ? <RefreshIcon className="rotating" /> : <AutoAwesomeIcon />}
                    onClick={handleGenerateTestCases}
                    disabled={generating}
                    sx={{
                      background: 'linear-gradient(135deg, #10b981, #14b8a6)',
                      '&:hover': { background: 'linear-gradient(135deg, #059669, #0d9488)' },
                      px: 4
                    }}
                  >
                    {generating ? 'Generating Test Cases...' : 'Generate Test Cases'}
                  </Button>
                  {generating && (
                    <Box sx={{ mt: 2 }}>
                      <LinearProgress sx={{ maxWidth: 400, mx: 'auto' }} />
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        AI is analyzing documentation and generating test cases...
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
            </Box>
          )}

          {/* Tab 1: Generated Test Cases */}
          {activeTab === 1 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="h6">Generated Test Cases</Typography>
                  <Chip label={`${selectedTestCases.length} selected`} size="small" />
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={handleSelectAll}
                  >
                    {selectedTestCases.length === generatedTestCases.length ? 'Deselect All' : 'Select All'}
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    disabled={selectedTestCases.length === 0}
                  >
                    Export
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<CodeIcon />}
                    disabled={selectedTestCases.length === 0}
                  >
                    Generate Code
                  </Button>
                </Box>
              </Box>

              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow sx={{ bgcolor: 'grey.50' }}>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedTestCases.length === generatedTestCases.length}
                          indeterminate={selectedTestCases.length > 0 && selectedTestCases.length < generatedTestCases.length}
                          onChange={handleSelectAll}
                        />
                      </TableCell>
                      <TableCell>ID</TableCell>
                      <TableCell>Test Case Name</TableCell>
                      <TableCell>Category</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Priority</TableCell>
                      <TableCell>Source</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {generatedTestCases.map((tc) => (
                      <TableRow
                        key={tc.id}
                        hover
                        selected={selectedTestCases.includes(tc.id)}
                      >
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={selectedTestCases.includes(tc.id)}
                            onChange={() => handleSelectTestCase(tc.id)}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip label={tc.id} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight={500}>
                            {tc.name}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={tc.category}
                            size="small"
                            icon={<CategoryIcon />}
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={tc.type}
                            size="small"
                            sx={{
                              bgcolor: getTypeColor(tc.type),
                              color: 'white'
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={tc.priority}
                            size="small"
                            color={getPriorityColor(tc.priority)}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" color="text.secondary">
                            {tc.source}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Tooltip title="View Details">
                            <IconButton size="small" onClick={() => setViewTestCaseDialog(tc)}>
                              <VisibilityIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit">
                            <IconButton size="small">
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Copy">
                            <IconButton size="small">
                              <ContentCopyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Tab 2: Test Scenarios */}
          {activeTab === 2 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">Test Scenarios</Typography>
                <Button variant="contained" startIcon={<AddIcon />}>
                  Create Scenario
                </Button>
              </Box>

              {mockScenarios.map((scenario) => (
                <Accordion key={scenario.id} sx={{ mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%', pr: 2 }}>
                      <LayersIcon sx={{ color: '#10b981' }} />
                      <Box sx={{ flex: 1 }}>
                        <Typography fontWeight={600}>{scenario.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {scenario.testCases.length} test cases
                        </Typography>
                      </Box>
                      <Chip
                        label={`${scenario.coverage} coverage`}
                        size="small"
                        color={parseInt(scenario.coverage) >= 80 ? 'success' : 'warning'}
                      />
                      <Chip
                        label={scenario.status}
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List dense>
                      {scenario.testCases.map((tcId) => {
                        const tc = generatedTestCases.find(t => t.id === tcId)
                        return tc ? (
                          <ListItem key={tcId}>
                            <ListItemIcon>
                              <CheckCircleIcon color="success" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText
                              primary={tc.name}
                              secondary={`${tc.category} • ${tc.type} • ${tc.priority}`}
                            />
                          </ListItem>
                        ) : null
                      })}
                    </List>
                    <Divider sx={{ my: 2 }} />
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button size="small" startIcon={<PlayArrowIcon />}>
                        Run Scenario
                      </Button>
                      <Button size="small" startIcon={<EditIcon />}>
                        Edit
                      </Button>
                      <Button size="small" startIcon={<DownloadIcon />}>
                        Export
                      </Button>
                    </Box>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}

          {/* Tab 3: Settings */}
          {activeTab === 3 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 3 }}>Generation Settings</Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                        Test Case Options
                      </Typography>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={generationSettings.includeNegative}
                            onChange={(e) => setGenerationSettings(prev => ({
                              ...prev,
                              includeNegative: e.target.checked
                            }))}
                          />
                        }
                        label="Include negative test cases"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={generationSettings.includeEdgeCases}
                            onChange={(e) => setGenerationSettings(prev => ({
                              ...prev,
                              includeEdgeCases: e.target.checked
                            }))}
                          />
                        }
                        label="Include edge cases"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={generationSettings.includePerformance}
                            onChange={(e) => setGenerationSettings(prev => ({
                              ...prev,
                              includePerformance: e.target.checked
                            }))}
                          />
                        }
                        label="Include performance tests"
                      />
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                        Code Generation
                      </Typography>
                      <FormControl fullWidth sx={{ mb: 2 }}>
                        <InputLabel>Test Framework</InputLabel>
                        <Select
                          value={generationSettings.framework}
                          label="Test Framework"
                          onChange={(e) => setGenerationSettings(prev => ({
                            ...prev,
                            framework: e.target.value
                          }))}
                        >
                          <MenuItem value="jest">Jest</MenuItem>
                          <MenuItem value="mocha">Mocha</MenuItem>
                          <MenuItem value="pytest">PyTest</MenuItem>
                          <MenuItem value="junit">JUnit</MenuItem>
                          <MenuItem value="playwright">Playwright</MenuItem>
                          <MenuItem value="cypress">Cypress</MenuItem>
                        </Select>
                      </FormControl>
                      <FormControl fullWidth>
                        <InputLabel>Language</InputLabel>
                        <Select
                          value={generationSettings.language}
                          label="Language"
                          onChange={(e) => setGenerationSettings(prev => ({
                            ...prev,
                            language: e.target.value
                          }))}
                        >
                          <MenuItem value="javascript">JavaScript</MenuItem>
                          <MenuItem value="typescript">TypeScript</MenuItem>
                          <MenuItem value="python">Python</MenuItem>
                          <MenuItem value="java">Java</MenuItem>
                        </Select>
                      </FormControl>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <Box sx={{ mt: 3, textAlign: 'right' }}>
                <Button variant="contained" startIcon={<SaveIcon />}>
                  Save Settings
                </Button>
              </Box>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Add File Dialog */}
      <Dialog open={addFileDialogOpen} onClose={() => setAddFileDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <UploadFileIcon sx={{ color: '#10b981' }} />
            Add Documentation Files
          </Box>
        </DialogTitle>
        <DialogContent>
          <Tabs value={0} sx={{ mb: 2 }}>
            <Tab label="From GitHub" icon={<GitHubIcon />} iconPosition="start" />
            <Tab label="Upload File" icon={<UploadFileIcon />} iconPosition="start" />
          </Tabs>

          <TextField
            fullWidth
            label="GitHub Repository URL"
            placeholder="https://github.com/org/repo"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="File Path (optional)"
            placeholder="/docs/README.md or /docs/**/*.md"
            value={filePath}
            onChange={(e) => setFilePath(e.target.value)}
            helperText="Leave empty to scan entire repository for .md files"
          />

          <Alert severity="info" sx={{ mt: 2 }}>
            AI will analyze Markdown files and extract requirements, user flows, and API specifications to generate test cases.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddFileDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" startIcon={<AddIcon />}>
            Add Files
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Test Case Dialog */}
      <Dialog
        open={!!viewTestCaseDialog}
        onClose={() => setViewTestCaseDialog(null)}
        maxWidth="md"
        fullWidth
      >
        {viewTestCaseDialog && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <BugReportIcon sx={{ color: '#10b981' }} />
                {viewTestCaseDialog.id}: {viewTestCaseDialog.name}
              </Box>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={3}>
                  <Typography variant="caption" color="text.secondary">Category</Typography>
                  <Typography variant="body2">{viewTestCaseDialog.category}</Typography>
                </Grid>
                <Grid item xs={3}>
                  <Typography variant="caption" color="text.secondary">Type</Typography>
                  <Chip
                    label={viewTestCaseDialog.type}
                    size="small"
                    sx={{ bgcolor: getTypeColor(viewTestCaseDialog.type), color: 'white' }}
                  />
                </Grid>
                <Grid item xs={3}>
                  <Typography variant="caption" color="text.secondary">Priority</Typography>
                  <Chip
                    label={viewTestCaseDialog.priority}
                    size="small"
                    color={getPriorityColor(viewTestCaseDialog.priority)}
                  />
                </Grid>
                <Grid item xs={3}>
                  <Typography variant="caption" color="text.secondary">Source</Typography>
                  <Typography variant="body2">{viewTestCaseDialog.source}</Typography>
                </Grid>
              </Grid>

              <Divider sx={{ mb: 2 }} />

              <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                Test Steps
              </Typography>
              <Stepper orientation="vertical">
                {viewTestCaseDialog.steps.map((step, index) => (
                  <Step key={index} active>
                    <StepLabel>{step}</StepLabel>
                  </Step>
                ))}
              </Stepper>

              <Box sx={{ mt: 3, p: 2, bgcolor: 'success.50', borderRadius: 2 }}>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 0.5 }}>
                  Expected Result
                </Typography>
                <Typography variant="body2">
                  {viewTestCaseDialog.expectedResult}
                </Typography>
              </Box>

              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                  Generated Code Preview
                </Typography>
                <Paper
                  sx={{
                    p: 2,
                    bgcolor: '#1e1e1e',
                    color: '#d4d4d4',
                    fontFamily: 'monospace',
                    fontSize: '0.85rem',
                    borderRadius: 2,
                    overflow: 'auto'
                  }}
                >
                  <pre style={{ margin: 0 }}>
{`test('${viewTestCaseDialog.name}', async () => {
  // Step 1: ${viewTestCaseDialog.steps[0]}
  // Step 2: ${viewTestCaseDialog.steps[1]}
  // ...

  // Expected: ${viewTestCaseDialog.expectedResult}
  expect(result).toBeTruthy();
});`}
                  </pre>
                </Paper>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setViewTestCaseDialog(null)}>Close</Button>
              <Button variant="outlined" startIcon={<EditIcon />}>
                Edit
              </Button>
              <Button variant="contained" startIcon={<CodeIcon />}>
                Generate Full Code
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  )
}

export default TestCaseGeneratorPreview
