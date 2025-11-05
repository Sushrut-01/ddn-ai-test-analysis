import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  TextField,
  MenuItem,
  Grid,
  CircularProgress,
  Alert,
  Button,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material'
import { knowledgeAPI } from '../services/api'
import { format } from 'date-fns'
import AddKnowledgeDocModal from '../components/AddKnowledgeDocModal'

const SEVERITY_LEVELS = [
  { value: '', label: 'All Severities' },
  { value: 'CRITICAL', label: 'Critical' },
  { value: 'HIGH', label: 'High' },
  { value: 'MEDIUM', label: 'Medium' },
  { value: 'LOW', label: 'Low' }
]

function KnowledgeManagement() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(20)
  const [category, setCategory] = useState('')
  const [severity, setSeverity] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [addModalOpen, setAddModalOpen] = useState(false)
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [selectedDoc, setSelectedDoc] = useState(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [docToDelete, setDocToDelete] = useState(null)

  // Fetch knowledge documents
  const { data: docsData, isLoading: docsLoading, error: docsError } = useQuery(
    ['knowledge-docs', category, severity, searchTerm],
    () => knowledgeAPI.getDocs({
      category: category || undefined,
      severity: severity || undefined,
      search: searchTerm || undefined,
      limit: 100
    }),
    { keepPreviousData: true }
  )

  // Fetch categories
  const { data: categoriesData } = useQuery(
    'knowledge-categories',
    knowledgeAPI.getCategories,
    { staleTime: 5 * 60 * 1000 } // Cache for 5 minutes
  )

  // Fetch statistics
  const { data: statsData } = useQuery(
    'knowledge-stats',
    knowledgeAPI.getStats,
    { refetchInterval: 30000 } // Refresh every 30 seconds
  )

  // Delete mutation
  const deleteMutation = useMutation(
    (docId) => knowledgeAPI.deleteDoc(docId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('knowledge-docs')
        queryClient.invalidateQueries('knowledge-categories')
        queryClient.invalidateQueries('knowledge-stats')
        setDeleteDialogOpen(false)
        setDocToDelete(null)
      }
    }
  )

  // Refresh categories mutation
  const refreshMutation = useMutation(
    knowledgeAPI.refreshCategories,
    {
      onSuccess: () => {
        queryClient.invalidateQueries('knowledge-categories')
      }
    }
  )

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleCategoryChange = (event) => {
    setCategory(event.target.value)
    setPage(0)
  }

  const handleSeverityChange = (event) => {
    setSeverity(event.target.value)
    setPage(0)
  }

  const handleAddDoc = () => {
    setSelectedDoc(null)
    setAddModalOpen(true)
  }

  const handleEditDoc = (doc) => {
    setSelectedDoc(doc)
    setEditModalOpen(true)
  }

  const handleDeleteDoc = (doc) => {
    setDocToDelete(doc)
    setDeleteDialogOpen(true)
  }

  const confirmDelete = () => {
    if (docToDelete) {
      deleteMutation.mutate(docToDelete.id)
    }
  }

  const handleRefreshCategories = () => {
    refreshMutation.mutate()
  }

  const getSeverityColor = (severity) => {
    const colors = {
      'CRITICAL': 'error',
      'HIGH': 'warning',
      'MEDIUM': 'info',
      'LOW': 'success'
    }
    return colors[severity] || 'default'
  }

  const getCategoryColor = (category) => {
    const colors = {
      'CODE_ERROR': 'error',
      'TEST_FAILURE': 'warning',
      'INFRA_ERROR': 'info',
      'DEPENDENCY_ERROR': 'secondary',
      'CONFIG_ERROR': 'primary'
    }
    return colors[category] || 'default'
  }

  const documents = docsData?.documents || []
  const paginatedDocs = documents.slice(page * rowsPerPage, (page + 1) * rowsPerPage)
  const categories = categoriesData?.categories || []
  const stats = statsData?.statistics || {}

  if (docsLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (docsError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Error loading knowledge documents: {docsError.message}
        </Alert>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Knowledge Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage error documentation and knowledge base
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Tooltip title="Refresh Categories">
            <IconButton
              color="primary"
              onClick={handleRefreshCategories}
              disabled={refreshMutation.isLoading}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddDoc}
          >
            Add Knowledge Doc
          </Button>
        </Box>
      </Box>

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" color="primary">
                {stats.total_documents || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Documents
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" color="primary">
                {Object.keys(stats.by_category || {}).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Categories
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" color="primary">
                {stats.recent_additions || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Recent (7 days)
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" color="primary">
                {stats.total_vectors || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Vectors
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              size="small"
              label="Search"
              placeholder="Search error type, message..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              select
              fullWidth
              size="small"
              label="Category"
              value={category}
              onChange={handleCategoryChange}
            >
              <MenuItem value="">All Categories</MenuItem>
              {categories.map((cat) => (
                <MenuItem key={cat.name} value={cat.name}>
                  {cat.name} ({cat.document_count})
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              select
              fullWidth
              size="small"
              label="Severity"
              value={severity}
              onChange={handleSeverityChange}
            >
              {SEVERITY_LEVELS.map((level) => (
                <MenuItem key={level.value} value={level.value}>
                  {level.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        </Grid>
      </Paper>

      {/* Success Messages */}
      {refreshMutation.isSuccess && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => refreshMutation.reset()}>
          Categories refreshed successfully! Found {refreshMutation.data?.count || 0} categories.
        </Alert>
      )}

      {deleteMutation.isSuccess && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => deleteMutation.reset()}>
          Knowledge document deleted successfully!
        </Alert>
      )}

      {/* Documents Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Error ID</TableCell>
                <TableCell>Error Type</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Component</TableCell>
                <TableCell>Updated</TableCell>
                <TableCell>Updated By</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedDocs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                      No knowledge documents found.
                      {searchTerm && ' Try adjusting your search criteria.'}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                paginatedDocs.map((doc) => (
                  <TableRow key={doc.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {doc.error_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {doc.error_type}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={doc.error_category}
                        color={getCategoryColor(doc.error_category)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={doc.severity}
                        color={getSeverityColor(doc.severity)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {doc.component}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {doc.updated_at ? format(new Date(doc.updated_at), 'MMM dd, yyyy HH:mm') : 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {doc.updated_by || doc.created_by || 'system'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Edit">
                        <IconButton
                          size="small"
                          onClick={() => handleEditDoc(doc)}
                          color="primary"
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteDoc(doc)}
                          color="error"
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={documents.length}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[10, 20, 50, 100]}
        />
      </Paper>

      {/* Add/Edit Modal */}
      <AddKnowledgeDocModal
        open={addModalOpen || editModalOpen}
        onClose={() => {
          setAddModalOpen(false)
          setEditModalOpen(false)
          setSelectedDoc(null)
        }}
        document={selectedDoc}
        categories={categories}
        mode={editModalOpen ? 'edit' : 'add'}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this knowledge document?
          </Typography>
          {docToDelete && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="body2">
                <strong>Error ID:</strong> {docToDelete.error_id}
              </Typography>
              <Typography variant="body2">
                <strong>Error Type:</strong> {docToDelete.error_type}
              </Typography>
              <Typography variant="body2">
                <strong>Category:</strong> {docToDelete.error_category}
              </Typography>
            </Box>
          )}
          <Alert severity="warning" sx={{ mt: 2 }}>
            This action cannot be undone. The document will be removed from Pinecone and
            categories will be automatically refreshed.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={confirmDelete}
            color="error"
            variant="contained"
            disabled={deleteMutation.isLoading}
          >
            {deleteMutation.isLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default KnowledgeManagement
