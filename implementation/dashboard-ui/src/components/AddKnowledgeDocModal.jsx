import React, { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  CircularProgress,
  Grid,
  Chip,
  Autocomplete,
  Alert
} from '@mui/material'
import {
  Save as SaveIcon,
  Cancel as CancelIcon
} from '@mui/icons-material'
import { knowledgeAPI } from '../services/api'

const SEVERITY_LEVELS = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
const FREQUENCY_LEVELS = ['VERY_HIGH', 'HIGH', 'MEDIUM', 'LOW', 'RARE']

const COMMON_TAGS = [
  'timeout',
  'network',
  'authentication',
  'permission',
  'configuration',
  'dependency',
  'database',
  'api',
  'memory',
  'disk-space',
  'performance',
  'security',
  'concurrency'
]

/**
 * AddKnowledgeDocModal Component
 *
 * Modal dialog for adding or editing knowledge documentation
 *
 * Props:
 * - open: boolean - Controls modal visibility
 * - onClose: function - Handler for closing modal
 * - document: object - Existing document for edit mode (null for add mode)
 * - categories: array - Available categories from backend
 * - mode: 'add' | 'edit' - Operation mode
 */
function AddKnowledgeDocModal({ open, onClose, document = null, categories = [], mode = 'add' }) {
  const queryClient = useQueryClient()
  const isEditMode = mode === 'edit' && document !== null

  // Form state
  const [formData, setFormData] = useState({
    error_id: '',
    error_type: '',
    error_category: '',
    category_description: '',
    subcategory: '',
    error_message: '',
    component: '',
    file_path: '',
    line_range: '',
    root_cause: '',
    solution: '',
    solution_steps: [],
    prevention: '',
    code_before: '',
    code_after: '',
    severity: 'MEDIUM',
    frequency: 'MEDIUM',
    tags: [],
    test_scenarios: [],
    created_by: 'system',
    updated_by: 'system'
  })

  const [errors, setErrors] = useState({})
  const [newSolutionStep, setNewSolutionStep] = useState('')
  const [newTestScenario, setNewTestScenario] = useState('')

  // Initialize form with document data in edit mode
  useEffect(() => {
    if (isEditMode && document) {
      setFormData({
        error_id: document.error_id || '',
        error_type: document.error_type || '',
        error_category: document.error_category || '',
        category_description: document.category_description || '',
        subcategory: document.subcategory || '',
        error_message: document.error_message || '',
        component: document.component || '',
        file_path: document.file_path || '',
        line_range: document.line_range || '',
        root_cause: document.root_cause || '',
        solution: document.solution || '',
        solution_steps: Array.isArray(document.solution_steps)
          ? document.solution_steps
          : (document.solution_steps ? document.solution_steps.split(',') : []),
        prevention: document.prevention || '',
        code_before: document.code_before || '',
        code_after: document.code_after || '',
        severity: document.severity || 'MEDIUM',
        frequency: document.frequency || 'MEDIUM',
        tags: Array.isArray(document.tags)
          ? document.tags
          : (document.tags ? document.tags.split(',') : []),
        test_scenarios: Array.isArray(document.test_scenarios)
          ? document.test_scenarios
          : (document.test_scenarios ? document.test_scenarios.split(',') : []),
        created_by: document.created_by || 'system',
        updated_by: 'system'
      })
    } else {
      // Reset form for add mode
      setFormData({
        error_id: '',
        error_type: '',
        error_category: '',
        category_description: '',
        subcategory: '',
        error_message: '',
        component: '',
        file_path: '',
        line_range: '',
        root_cause: '',
        solution: '',
        solution_steps: [],
        prevention: '',
        code_before: '',
        code_after: '',
        severity: 'MEDIUM',
        frequency: 'MEDIUM',
        tags: [],
        test_scenarios: [],
        created_by: 'system',
        updated_by: 'system'
      })
    }
    setErrors({})
  }, [isEditMode, document, open])

  // Add mutation
  const addMutation = useMutation(
    (data) => knowledgeAPI.addDoc(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('knowledge-docs')
        queryClient.invalidateQueries('knowledge-categories')
        queryClient.invalidateQueries('knowledge-stats')
        handleClose()
      }
    }
  )

  // Update mutation
  const updateMutation = useMutation(
    ({ id, data }) => knowledgeAPI.updateDoc(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('knowledge-docs')
        queryClient.invalidateQueries('knowledge-categories')
        queryClient.invalidateQueries('knowledge-stats')
        handleClose()
      }
    }
  )

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))

    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }))
    }
  }

  const handleAddSolutionStep = () => {
    if (newSolutionStep.trim()) {
      setFormData(prev => ({
        ...prev,
        solution_steps: [...prev.solution_steps, newSolutionStep.trim()]
      }))
      setNewSolutionStep('')
    }
  }

  const handleRemoveSolutionStep = (index) => {
    setFormData(prev => ({
      ...prev,
      solution_steps: prev.solution_steps.filter((_, i) => i !== index)
    }))
  }

  const handleAddTestScenario = () => {
    if (newTestScenario.trim()) {
      setFormData(prev => ({
        ...prev,
        test_scenarios: [...prev.test_scenarios, newTestScenario.trim()]
      }))
      setNewTestScenario('')
    }
  }

  const handleRemoveTestScenario = (index) => {
    setFormData(prev => ({
      ...prev,
      test_scenarios: prev.test_scenarios.filter((_, i) => i !== index)
    }))
  }

  const validateForm = () => {
    const newErrors = {}

    // Required fields
    if (!formData.error_id.trim()) {
      newErrors.error_id = 'Error ID is required'
    }
    if (!formData.error_type.trim()) {
      newErrors.error_type = 'Error type is required'
    }
    if (!formData.error_category.trim()) {
      newErrors.error_category = 'Error category is required'
    }
    if (!formData.error_message.trim()) {
      newErrors.error_message = 'Error message is required'
    }
    if (!formData.root_cause.trim()) {
      newErrors.root_cause = 'Root cause is required'
    }
    if (!formData.solution.trim() && formData.solution_steps.length === 0) {
      newErrors.solution = 'Either solution text or solution steps are required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = () => {
    if (!validateForm()) {
      return
    }

    const submitData = {
      ...formData,
      updated_by: 'admin' // TODO: Get from auth context
    }

    if (isEditMode) {
      updateMutation.mutate({ id: document.id, data: submitData })
    } else {
      addMutation.mutate(submitData)
    }
  }

  const handleClose = () => {
    setFormData({
      error_id: '',
      error_type: '',
      error_category: '',
      category_description: '',
      subcategory: '',
      error_message: '',
      component: '',
      file_path: '',
      line_range: '',
      root_cause: '',
      solution: '',
      solution_steps: [],
      prevention: '',
      code_before: '',
      code_after: '',
      severity: 'MEDIUM',
      frequency: 'MEDIUM',
      tags: [],
      test_scenarios: [],
      created_by: 'system',
      updated_by: 'system'
    })
    setErrors({})
    setNewSolutionStep('')
    setNewTestScenario('')
    onClose()
  }

  const isLoading = addMutation.isLoading || updateMutation.isLoading
  const error = addMutation.error || updateMutation.error

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="lg"
      fullWidth
      scroll="paper"
    >
      <DialogTitle>
        <Typography variant="h5">
          {isEditMode ? 'Edit Knowledge Document' : 'Add Knowledge Document'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {isEditMode
            ? 'Update the knowledge document. Categories will be automatically refreshed.'
            : 'Add a new error documentation to the knowledge base. Categories will be automatically refreshed.'}
        </Typography>
      </DialogTitle>

      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error.message || 'An error occurred while saving the document'}
          </Alert>
        )}

        <Grid container spacing={2}>
          {/* Basic Information */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Basic Information
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Error ID *"
              value={formData.error_id}
              onChange={(e) => handleChange('error_id', e.target.value)}
              error={!!errors.error_id}
              helperText={errors.error_id || 'Unique identifier (e.g., ERR001)'}
              disabled={isEditMode} // Cannot change ID in edit mode
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Error Type *"
              value={formData.error_type}
              onChange={(e) => handleChange('error_type', e.target.value)}
              error={!!errors.error_type}
              helperText={errors.error_type || 'Brief error type (e.g., TimeoutError)'}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <FormControl fullWidth error={!!errors.error_category}>
              <InputLabel>Error Category *</InputLabel>
              <Select
                value={formData.error_category}
                onChange={(e) => handleChange('error_category', e.target.value)}
                label="Error Category *"
              >
                {categories.map((cat) => (
                  <MenuItem key={cat.name} value={cat.name}>
                    {cat.name} ({cat.document_count})
                  </MenuItem>
                ))}
                <MenuItem value="CODE_ERROR">CODE_ERROR</MenuItem>
                <MenuItem value="TEST_FAILURE">TEST_FAILURE</MenuItem>
                <MenuItem value="INFRA_ERROR">INFRA_ERROR</MenuItem>
                <MenuItem value="DEPENDENCY_ERROR">DEPENDENCY_ERROR</MenuItem>
                <MenuItem value="CONFIG_ERROR">CONFIG_ERROR</MenuItem>
              </Select>
              {errors.error_category && (
                <Typography variant="caption" color="error">
                  {errors.error_category}
                </Typography>
              )}
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Subcategory"
              value={formData.subcategory}
              onChange={(e) => handleChange('subcategory', e.target.value)}
              helperText="Specific subcategory"
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Component"
              value={formData.component}
              onChange={(e) => handleChange('component', e.target.value)}
              helperText="Affected component/service"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Category Description"
              value={formData.category_description}
              onChange={(e) => handleChange('category_description', e.target.value)}
              helperText="Optional description for the category"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Error Message *"
              value={formData.error_message}
              onChange={(e) => handleChange('error_message', e.target.value)}
              error={!!errors.error_message}
              helperText={errors.error_message || 'Full error message as it appears'}
            />
          </Grid>

          {/* Location Information */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Location Information
            </Typography>
          </Grid>

          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="File Path"
              value={formData.file_path}
              onChange={(e) => handleChange('file_path', e.target.value)}
              helperText="Path to the file (e.g., src/components/Button.jsx)"
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Line Range"
              value={formData.line_range}
              onChange={(e) => handleChange('line_range', e.target.value)}
              helperText="Line numbers (e.g., 45-52)"
            />
          </Grid>

          {/* Analysis */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Analysis
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Root Cause *"
              value={formData.root_cause}
              onChange={(e) => handleChange('root_cause', e.target.value)}
              error={!!errors.root_cause}
              helperText={errors.root_cause || 'Detailed explanation of the root cause'}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Solution"
              value={formData.solution}
              onChange={(e) => handleChange('solution', e.target.value)}
              error={!!errors.solution}
              helperText={errors.solution || 'High-level solution description'}
            />
          </Grid>

          {/* Solution Steps */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Solution Steps
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <TextField
                fullWidth
                size="small"
                label="Add solution step"
                value={newSolutionStep}
                onChange={(e) => setNewSolutionStep(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    handleAddSolutionStep()
                  }
                }}
              />
              <Button onClick={handleAddSolutionStep} variant="outlined">
                Add
              </Button>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {formData.solution_steps.map((step, index) => (
                <Chip
                  key={index}
                  label={`${index + 1}. ${step}`}
                  onDelete={() => handleRemoveSolutionStep(index)}
                  size="small"
                />
              ))}
            </Box>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Prevention"
              value={formData.prevention}
              onChange={(e) => handleChange('prevention', e.target.value)}
              helperText="How to prevent this error in the future"
            />
          </Grid>

          {/* Code Examples */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Code Examples (Optional)
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              multiline
              rows={6}
              label="Code Before (Buggy)"
              value={formData.code_before}
              onChange={(e) => handleChange('code_before', e.target.value)}
              helperText="Code snippet showing the error"
              InputProps={{
                sx: { fontFamily: 'monospace', fontSize: '0.875rem' }
              }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              multiline
              rows={6}
              label="Code After (Fixed)"
              value={formData.code_after}
              onChange={(e) => handleChange('code_after', e.target.value)}
              helperText="Code snippet with the fix"
              InputProps={{
                sx: { fontFamily: 'monospace', fontSize: '0.875rem' }
              }}
            />
          </Grid>

          {/* Metadata */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Metadata
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Severity</InputLabel>
              <Select
                value={formData.severity}
                onChange={(e) => handleChange('severity', e.target.value)}
                label="Severity"
              >
                {SEVERITY_LEVELS.map((level) => (
                  <MenuItem key={level} value={level}>
                    {level}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Frequency</InputLabel>
              <Select
                value={formData.frequency}
                onChange={(e) => handleChange('frequency', e.target.value)}
                label="Frequency"
              >
                {FREQUENCY_LEVELS.map((level) => (
                  <MenuItem key={level} value={level}>
                    {level}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <Autocomplete
              multiple
              freeSolo
              options={COMMON_TAGS}
              value={formData.tags}
              onChange={(e, value) => handleChange('tags', value)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Tags"
                  helperText="Select from common tags or add custom tags"
                />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    label={option}
                    size="small"
                    {...getTagProps({ index })}
                  />
                ))
              }
            />
          </Grid>

          {/* Test Scenarios */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Test Scenarios
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <TextField
                fullWidth
                size="small"
                label="Add test scenario"
                value={newTestScenario}
                onChange={(e) => setNewTestScenario(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    handleAddTestScenario()
                  }
                }}
              />
              <Button onClick={handleAddTestScenario} variant="outlined">
                Add
              </Button>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {formData.test_scenarios.map((scenario, index) => (
                <Chip
                  key={index}
                  label={scenario}
                  onDelete={() => handleRemoveTestScenario(index)}
                  size="small"
                />
              ))}
            </Box>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button
          onClick={handleClose}
          startIcon={<CancelIcon />}
          disabled={isLoading}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          startIcon={isLoading ? <CircularProgress size={20} /> : <SaveIcon />}
          disabled={isLoading}
        >
          {isLoading ? 'Saving...' : (isEditMode ? 'Update' : 'Add')}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default AddKnowledgeDocModal
