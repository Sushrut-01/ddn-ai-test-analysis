import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import {
    Box, Container, Paper, Typography, Grid, Button, Chip, Avatar, TextField,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    TablePagination, IconButton, InputAdornment, MenuItem, Card, CardContent, Dialog,
    DialogTitle, DialogContent, DialogActions, Skeleton, CircularProgress, Alert
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';
import SearchIcon from '@mui/icons-material/Search';
import VisibilityIcon from '@mui/icons-material/Visibility';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import CategoryIcon from '@mui/icons-material/Category';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import WarningIcon from '@mui/icons-material/Warning';
import { knowledgeAPI } from '../services/api';

const categories = ['CODE_ERROR', 'TEST_FAILURE', 'INFRA_ERROR', 'DEPENDENCY_ERROR', 'CONFIG_ERROR'];
const severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

const getCategoryColor = (category) => {
    const colors = {
        'CODE_ERROR': '#ef4444',
        'TEST_FAILURE': '#f59e0b',
        'INFRA_ERROR': '#3b82f6',
        'DEPENDENCY_ERROR': '#8b5cf6',
        'CONFIG_ERROR': '#10b981'
    };
    return colors[category] || '#64748b';
};

const getSeverityColor = (severity) => {
    const colors = {
        'CRITICAL': '#dc2626',
        'HIGH': '#ea580c',
        'MEDIUM': '#ca8a04',
        'LOW': '#16a34a'
    };
    return colors[severity] || '#64748b';
};

const KnowledgeManagementPreview = () => {
    const location = useLocation();
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [searchTerm, setSearchTerm] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('');
    const [severityFilter, setSeverityFilter] = useState('');
    const [addDialogOpen, setAddDialogOpen] = useState(false);

    // Real data state
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [knowledgeDocs, setKnowledgeDocs] = useState([]);
    const [stats, setStats] = useState(null);
    const [error, setError] = useState(null);

    const fetchKnowledgeDocs = useCallback(async () => {
        try {
            const params = {};
            if (categoryFilter) params.category = categoryFilter;
            if (searchTerm) params.search = searchTerm;

            const [docsRes, statsRes] = await Promise.all([
                knowledgeAPI.getDocs(params),
                knowledgeAPI.getStats().catch(() => null)
            ]);

            const docs = docsRes?.documents || docsRes?.data?.documents || docsRes || [];
            setKnowledgeDocs(Array.isArray(docs) ? docs : []);
            setStats(statsRes);
            setError(null);
        } catch (err) {
            console.error('Error fetching knowledge docs:', err);
            setError(err.message);
            setKnowledgeDocs([]);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, [categoryFilter, searchTerm]);

    useEffect(() => {
        fetchKnowledgeDocs();
    }, [location.key, fetchKnowledgeDocs]);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchKnowledgeDocs();
    };

    const totalDocs = knowledgeDocs.length;
    const totalUsage = knowledgeDocs.reduce((sum, doc) => sum + (doc.usageCount || doc.usage_count || 0), 0);
    const criticalDocs = knowledgeDocs.filter(d => d.severity === 'CRITICAL' || d.severity === 'critical').length;

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc', pb: 4 }}>
            {/* Header */}
            <Box
                sx={{
                    background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                    pt: 4,
                    pb: 8,
                    px: 3,
                    color: 'white',
                    borderBottomLeftRadius: 48,
                    borderBottomRightRadius: 48,
                    mb: -4
                }}
            >
                <Container maxWidth="xl">
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                            <Typography variant="h4" fontWeight="bold" gutterBottom>
                                Knowledge Management
                            </Typography>
                            <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                                Manage solution patterns and best practices for AI recommendations
                            </Typography>
                        </Box>
                        <Box display="flex" gap={2}>
                            <Button
                                variant="contained"
                                startIcon={refreshing ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
                                onClick={handleRefresh}
                                disabled={refreshing}
                                sx={{ bgcolor: 'rgba(255,255,255,0.15)', '&:hover': { bgcolor: 'rgba(255,255,255,0.25)' } }}
                            >
                                {refreshing ? 'Syncing...' : 'Sync'}
                            </Button>
                            <Button
                                variant="contained"
                                startIcon={<AddIcon />}
                                onClick={() => setAddDialogOpen(true)}
                                sx={{ bgcolor: 'white', color: '#059669', '&:hover': { bgcolor: '#f0fdf4' } }}
                            >
                                Add Document
                            </Button>
                        </Box>
                    </Box>
                </Container>
            </Box>

            <Container maxWidth="xl">
                {/* Stats Cards */}
                <Grid container spacing={3} mb={4}>
                    {[
                        { label: 'Total Documents', value: totalDocs, icon: <LibraryBooksIcon />, color: '#059669' },
                        { label: 'Categories', value: categories.length, icon: <CategoryIcon />, color: '#3b82f6' },
                        { label: 'Total Usage', value: totalUsage, icon: <TrendingUpIcon />, color: '#8b5cf6' },
                        { label: 'Critical Issues', value: criticalDocs, icon: <WarningIcon />, color: '#dc2626' },
                    ].map((stat, idx) => (
                        <Grid item xs={6} md={3} key={idx}>
                            <Card elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                                <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                    <Avatar sx={{ bgcolor: alpha(stat.color, 0.1), color: stat.color, width: 48, height: 48 }}>
                                        {stat.icon}
                                    </Avatar>
                                    <Box>
                                        <Typography variant="h4" fontWeight="bold">{stat.value}</Typography>
                                        <Typography variant="body2" color="textSecondary">{stat.label}</Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>

                {/* Filters */}
                <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                    <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                placeholder="Search documents..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                InputProps={{
                                    startAdornment: <InputAdornment position="start"><SearchIcon color="action" /></InputAdornment>,
                                }}
                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                            />
                        </Grid>
                        <Grid item xs={6} md={3}>
                            <TextField
                                fullWidth
                                select
                                label="Category"
                                value={categoryFilter}
                                onChange={(e) => setCategoryFilter(e.target.value)}
                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                            >
                                <MenuItem value="">All Categories</MenuItem>
                                {categories.map((cat) => (
                                    <MenuItem key={cat} value={cat}>{cat.replace('_', ' ')}</MenuItem>
                                ))}
                            </TextField>
                        </Grid>
                        <Grid item xs={6} md={3}>
                            <TextField
                                fullWidth
                                select
                                label="Severity"
                                value={severityFilter}
                                onChange={(e) => setSeverityFilter(e.target.value)}
                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                            >
                                <MenuItem value="">All Severities</MenuItem>
                                {severities.map((sev) => (
                                    <MenuItem key={sev} value={sev}>{sev}</MenuItem>
                                ))}
                            </TextField>
                        </Grid>
                        <Grid item xs={12} md={2}>
                            <Button fullWidth variant="outlined" sx={{ borderRadius: 3, py: 1.8 }}>
                                Clear Filters
                            </Button>
                        </Grid>
                    </Grid>
                </Paper>

                {/* Table */}
                <Paper elevation={0} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', overflow: 'hidden' }}>
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow sx={{ bgcolor: '#f8fafc' }}>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Title</TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Category</TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Severity</TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Solution Preview</TableCell>
                                    <TableCell align="center" sx={{ fontWeight: 600, color: '#64748b' }}>Usage</TableCell>
                                    <TableCell sx={{ fontWeight: 600, color: '#64748b' }}>Created</TableCell>
                                    <TableCell align="center" sx={{ fontWeight: 600, color: '#64748b' }}>Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {knowledgeDocs.map((doc) => (
                                    <TableRow key={doc.id} sx={{ '&:hover': { bgcolor: '#f8fafc' } }}>
                                        <TableCell>
                                            <Typography variant="body2" fontWeight={600}>{doc.title}</Typography>
                                        </TableCell>
                                        <TableCell>
                                            <Chip
                                                label={doc.category.replace('_', ' ')}
                                                size="small"
                                                sx={{
                                                    bgcolor: alpha(getCategoryColor(doc.category), 0.1),
                                                    color: getCategoryColor(doc.category),
                                                    fontWeight: 600,
                                                    fontSize: '0.7rem'
                                                }}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Chip
                                                label={doc.severity}
                                                size="small"
                                                sx={{
                                                    bgcolor: alpha(getSeverityColor(doc.severity), 0.1),
                                                    color: getSeverityColor(doc.severity),
                                                    fontWeight: 600,
                                                    fontSize: '0.7rem'
                                                }}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Typography variant="body2" sx={{ maxWidth: 300 }} noWrap>
                                                {doc.solution}
                                            </Typography>
                                        </TableCell>
                                        <TableCell align="center">
                                            <Chip
                                                label={doc.usageCount}
                                                size="small"
                                                sx={{ bgcolor: '#f1f5f9', fontWeight: 600 }}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Typography variant="body2" color="textSecondary">{doc.createdAt}</Typography>
                                        </TableCell>
                                        <TableCell align="center">
                                            <Box display="flex" gap={0.5} justifyContent="center">
                                                <IconButton size="small" sx={{ color: '#3b82f6' }}>
                                                    <VisibilityIcon fontSize="small" />
                                                </IconButton>
                                                <IconButton size="small" sx={{ color: '#f59e0b' }}>
                                                    <EditIcon fontSize="small" />
                                                </IconButton>
                                                <IconButton size="small" sx={{ color: '#ef4444' }}>
                                                    <DeleteIcon fontSize="small" />
                                                </IconButton>
                                            </Box>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                    <TablePagination
                        rowsPerPageOptions={[10, 20, 50]}
                        component="div"
                        count={knowledgeDocs.length}
                        rowsPerPage={rowsPerPage}
                        page={page}
                        onPageChange={(e, p) => setPage(p)}
                        onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value)); setPage(0); }}
                    />
                </Paper>

                {/* Add Document Dialog */}
                <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="md" fullWidth>
                    <DialogTitle sx={{ fontWeight: 600 }}>Add Knowledge Document</DialogTitle>
                    <DialogContent>
                        <Grid container spacing={2} sx={{ mt: 1 }}>
                            <Grid item xs={12}>
                                <TextField fullWidth label="Title" placeholder="e.g., Null Pointer Exception in UserService" />
                            </Grid>
                            <Grid item xs={6}>
                                <TextField fullWidth select label="Category">
                                    {categories.map((cat) => (
                                        <MenuItem key={cat} value={cat}>{cat.replace('_', ' ')}</MenuItem>
                                    ))}
                                </TextField>
                            </Grid>
                            <Grid item xs={6}>
                                <TextField fullWidth select label="Severity">
                                    {severities.map((sev) => (
                                        <MenuItem key={sev} value={sev}>{sev}</MenuItem>
                                    ))}
                                </TextField>
                            </Grid>
                            <Grid item xs={12}>
                                <TextField fullWidth multiline rows={4} label="Solution" placeholder="Describe the solution or fix for this issue..." />
                            </Grid>
                        </Grid>
                    </DialogContent>
                    <DialogActions sx={{ p: 3 }}>
                        <Button onClick={() => setAddDialogOpen(false)}>Cancel</Button>
                        <Button variant="contained" sx={{ bgcolor: '#059669' }}>Add Document</Button>
                    </DialogActions>
                </Dialog>
            </Container>
        </Box>
    );
};

export default KnowledgeManagementPreview;
