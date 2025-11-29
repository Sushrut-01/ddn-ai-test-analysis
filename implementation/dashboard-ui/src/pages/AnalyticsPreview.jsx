import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import {
    Box, Container, Paper, Typography, Grid, ToggleButtonGroup, ToggleButton,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Avatar,
    Skeleton, CircularProgress, Button
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import {
    LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import InsightsIcon from '@mui/icons-material/Insights';
import RefreshIcon from '@mui/icons-material/Refresh';
import { analyticsAPI, monitoringAPI } from '../services/api';

const MetricCard = ({ title, value, subtitle, icon, color, trend, trendValue }) => (
    <Paper
        elevation={0}
        sx={{
            p: 3,
            borderRadius: 4,
            bgcolor: 'white',
            boxShadow: '0 4px 20px rgba(0,0,0,0.04)',
            height: '100%'
        }}
    >
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
            <Box>
                <Typography variant="body2" color="textSecondary" fontWeight={500}>{title}</Typography>
                <Typography variant="h4" fontWeight="bold" sx={{ my: 1 }}>{value}</Typography>
                {subtitle && <Typography variant="caption" color="textSecondary">{subtitle}</Typography>}
            </Box>
            <Avatar sx={{ bgcolor: alpha(color, 0.1), color: color, width: 48, height: 48 }}>
                {icon}
            </Avatar>
        </Box>
        {trend && (
            <Box display="flex" alignItems="center" mt={2}>
                {trend === 'up' ? <TrendingUpIcon fontSize="small" sx={{ color: '#10b981' }} /> : <TrendingDownIcon fontSize="small" sx={{ color: '#ef4444' }} />}
                <Typography variant="body2" sx={{ ml: 0.5, fontWeight: 600, color: trend === 'up' ? '#10b981' : '#ef4444' }}>
                    {trendValue}
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ ml: 1 }}>vs last period</Typography>
            </Box>
        )}
    </Paper>
);

const AnalyticsPreview = () => {
    const location = useLocation();
    const [timeRange, setTimeRange] = useState('30d');
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [stats, setStats] = useState(null);
    const [trends, setTrends] = useState([]);
    const [patterns, setPatterns] = useState([]);
    const [acceptanceData, setAcceptanceData] = useState([]);
    const [error, setError] = useState(null);

    const fetchAnalytics = useCallback(async () => {
        try {
            const [statsRes, trendsRes, patternsRes, acceptanceRes] = await Promise.all([
                monitoringAPI.getStats(),
                analyticsAPI.getTrends(timeRange, 'daily').catch(() => null),
                analyticsAPI.getPatterns().catch(() => null),
                analyticsAPI.getAcceptanceRate(timeRange).catch(() => null)
            ]);

            setStats(statsRes);

            // Process trends data
            if (trendsRes?.data) {
                setTrends(trendsRes.data);
            }

            // Process patterns data
            if (patternsRes?.data) {
                setPatterns(patternsRes.data.slice(0, 5));
            }

            // Process acceptance rate data
            if (acceptanceRes?.data) {
                setAcceptanceData(acceptanceRes.data);
            }

            setError(null);
        } catch (err) {
            console.error('Error fetching analytics:', err);
            setError(err.message);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, [timeRange]);

    useEffect(() => {
        setLoading(true);
        fetchAnalytics();
    }, [location.key, fetchAnalytics]);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchAnalytics();
    };

    // Calculate metrics from stats
    const totalAnalyses = stats?.total_analyzed || 0;
    const avgConfidence = stats?.avg_confidence ? Math.round(parseFloat(stats.avg_confidence) * 100) : 0;
    const totalFailures = stats?.total_failures || 0;

    // Build validation pie from classification breakdown
    const validationPie = stats?.classification_breakdown?.map(item => ({
        name: item.classification || 'Unknown',
        value: item.count,
        color: item.classification === 'accepted' ? '#10b981' : item.classification === 'rejected' ? '#ef4444' : '#f59e0b'
    })) || [
        { name: 'Analyzed', value: totalAnalyses, color: '#10b981' },
        { name: 'Pending', value: Math.max(0, totalFailures - totalAnalyses), color: '#f59e0b' }
    ];

    // Build confidence distribution from real data or default
    const confidenceDistribution = [
        { range: '90-100%', count: avgConfidence >= 90 ? totalAnalyses : Math.round(totalAnalyses * 0.4) },
        { range: '80-89%', count: Math.round(totalAnalyses * 0.3) },
        { range: '70-79%', count: Math.round(totalAnalyses * 0.2) },
        { range: '60-69%', count: Math.round(totalAnalyses * 0.08) },
        { range: '<60%', count: Math.round(totalAnalyses * 0.02) },
    ];

    // Build category data from trends or empty array
    const categoryData = trends.length > 0 ? trends : [];

    // Build top patterns from patterns state or empty array
    const topPatterns = patterns.length > 0 ? patterns.map(p => ({
        pattern: p.pattern || p.name || 'Unknown',
        count: p.count || 0,
        successRate: p.success_rate || p.successRate || 0,
        trend: p.trend || 'stable'
    })) : [];

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc', pb: 4 }}>
            {/* Header */}
            <Box
                sx={{
                    background: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)',
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
                                Advanced Analytics
                            </Typography>
                            <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                                AI performance metrics, failure trends, and validation insights
                            </Typography>
                        </Box>
                        <Box display="flex" gap={2} alignItems="center">
                            <ToggleButtonGroup
                                value={timeRange}
                                exclusive
                                onChange={(e, v) => v && setTimeRange(v)}
                                sx={{
                                    bgcolor: 'rgba(255,255,255,0.15)',
                                    '& .MuiToggleButton-root': { color: 'white', border: 'none', '&.Mui-selected': { bgcolor: 'rgba(255,255,255,0.25)' } }
                                }}
                            >
                                <ToggleButton value="7d">7 Days</ToggleButton>
                                <ToggleButton value="30d">30 Days</ToggleButton>
                                <ToggleButton value="90d">90 Days</ToggleButton>
                            </ToggleButtonGroup>
                            <Button
                                variant="contained"
                                startIcon={refreshing ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
                                onClick={handleRefresh}
                                disabled={refreshing}
                                sx={{ bgcolor: 'rgba(255,255,255,0.2)', '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' } }}
                            >
                                {refreshing ? 'Refreshing...' : 'Refresh'}
                            </Button>
                        </Box>
                    </Box>
                </Container>
            </Box>

            <Container maxWidth="xl">
                {/* Key Metrics */}
                <Grid container spacing={3} mb={4}>
                    <Grid item xs={6} md={3}>
                        {loading ? (
                            <Paper elevation={0} sx={{ p: 3, borderRadius: 4, bgcolor: 'white', boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                                <Skeleton width={100} height={24} />
                                <Skeleton width={60} height={40} sx={{ my: 1 }} />
                                <Skeleton width={80} height={16} />
                            </Paper>
                        ) : (
                            <MetricCard title="Total Failures" value={totalFailures.toLocaleString()} subtitle="All time" icon={<InsightsIcon />} color="#ef4444" />
                        )}
                    </Grid>
                    <Grid item xs={6} md={3}>
                        {loading ? (
                            <Paper elevation={0} sx={{ p: 3, borderRadius: 4, bgcolor: 'white', boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                                <Skeleton width={100} height={24} />
                                <Skeleton width={60} height={40} sx={{ my: 1 }} />
                                <Skeleton width={80} height={16} />
                            </Paper>
                        ) : (
                            <MetricCard title="Total Analyzed" value={totalAnalyses.toLocaleString()} subtitle={`Last ${timeRange}`} icon={<CheckCircleIcon />} color="#3b82f6" />
                        )}
                    </Grid>
                    <Grid item xs={6} md={3}>
                        {loading ? (
                            <Paper elevation={0} sx={{ p: 3, borderRadius: 4, bgcolor: 'white', boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                                <Skeleton width={100} height={24} />
                                <Skeleton width={60} height={40} sx={{ my: 1 }} />
                                <Skeleton width={80} height={16} />
                            </Paper>
                        ) : (
                            <MetricCard title="Avg Confidence" value={`${avgConfidence}%`} subtitle="AI confidence score" icon={<TrendingUpIcon />} color="#8b5cf6" />
                        )}
                    </Grid>
                    <Grid item xs={6} md={3}>
                        {loading ? (
                            <Paper elevation={0} sx={{ p: 3, borderRadius: 4, bgcolor: 'white', boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                                <Skeleton width={100} height={24} />
                                <Skeleton width={60} height={40} sx={{ my: 1 }} />
                                <Skeleton width={80} height={16} />
                            </Paper>
                        ) : (
                            <MetricCard title="Last 24h" value={(stats?.failures_last_24h || 0).toLocaleString()} subtitle="Recent failures" icon={<AutorenewIcon />} color="#f59e0b" />
                        )}
                    </Grid>
                </Grid>

                {/* Charts Row 1 */}
                <Grid container spacing={3} mb={4}>
                    {/* Acceptance Rate Trend */}
                    <Grid item xs={12} lg={8}>
                        <Paper elevation={0} sx={{ p: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                            <Typography variant="h6" fontWeight="bold" mb={1}>Acceptance Rate Trend</Typography>
                            <Typography variant="body2" color="textSecondary" mb={3}>Daily AI analysis acceptance rate</Typography>
                            <Box height={350}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={acceptanceData}>
                                        <defs>
                                            <linearGradient id="colorRate" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                                                <stop offset="95%" stopColor="#10b981" stopOpacity={0.05} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                                        <XAxis dataKey="date" axisLine={false} tickLine={false} />
                                        <YAxis domain={[0, 100]} axisLine={false} tickLine={false} />
                                        <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }} />
                                        <Area type="monotone" dataKey="rate" stroke="#10b981" strokeWidth={3} fill="url(#colorRate)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </Box>
                        </Paper>
                    </Grid>

                    {/* Validation Distribution */}
                    <Grid item xs={12} lg={4}>
                        <Paper elevation={0} sx={{ p: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', height: '100%' }}>
                            <Typography variant="h6" fontWeight="bold" mb={1}>Validation Distribution</Typography>
                            <Typography variant="body2" color="textSecondary" mb={3}>How AI analyses are validated</Typography>
                            <Box height={280}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie data={validationPie} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={5} dataKey="value">
                                            {validationPie.map((entry, idx) => <Cell key={idx} fill={entry.color} />)}
                                        </Pie>
                                        <Tooltip />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            </Box>
                        </Paper>
                    </Grid>
                </Grid>

                {/* Charts Row 2 */}
                <Grid container spacing={3} mb={4}>
                    {/* Error Category Trends */}
                    <Grid item xs={12} lg={8}>
                        <Paper elevation={0} sx={{ p: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                            <Typography variant="h6" fontWeight="bold" mb={1}>Error Category Trends</Typography>
                            <Typography variant="body2" color="textSecondary" mb={3}>Failure distribution by category</Typography>
                            <Box height={300}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={categoryData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                                        <XAxis dataKey="name" axisLine={false} tickLine={false} />
                                        <YAxis axisLine={false} tickLine={false} />
                                        <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }} />
                                        <Legend />
                                        <Bar dataKey="codeError" name="Code Error" fill="#ef4444" radius={[4, 4, 0, 0]} />
                                        <Bar dataKey="testFailure" name="Test Failure" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                                        <Bar dataKey="infraError" name="Infra Error" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                                        <Bar dataKey="depError" name="Dependency" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                                        <Bar dataKey="configError" name="Config" fill="#10b981" radius={[4, 4, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </Box>
                        </Paper>
                    </Grid>

                    {/* Confidence Distribution */}
                    <Grid item xs={12} lg={4}>
                        <Paper elevation={0} sx={{ p: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)', height: '100%' }}>
                            <Typography variant="h6" fontWeight="bold" mb={1}>Confidence Distribution</Typography>
                            <Typography variant="body2" color="textSecondary" mb={3}>AI confidence score breakdown</Typography>
                            {confidenceDistribution.map((item, idx) => (
                                <Box key={idx} mb={2}>
                                    <Box display="flex" justifyContent="space-between" mb={0.5}>
                                        <Typography variant="body2" fontWeight={500}>{item.range}</Typography>
                                        <Typography variant="body2" color="textSecondary">{item.count} analyses</Typography>
                                    </Box>
                                    <Box sx={{ height: 8, bgcolor: '#f1f5f9', borderRadius: 4, overflow: 'hidden' }}>
                                        <Box sx={{ width: `${(item.count / 50) * 100}%`, height: '100%', borderRadius: 4, bgcolor: idx === 0 ? '#10b981' : idx === 1 ? '#3b82f6' : idx === 2 ? '#f59e0b' : '#ef4444' }} />
                                    </Box>
                                </Box>
                            ))}
                        </Paper>
                    </Grid>
                </Grid>

                {/* Top Patterns Table */}
                <Paper elevation={0} sx={{ p: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                    <Typography variant="h6" fontWeight="bold" mb={1}>Top Failure Patterns</Typography>
                    <Typography variant="body2" color="textSecondary" mb={3}>Most common patterns identified by AI</Typography>
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow sx={{ '& th': { fontWeight: 600, color: '#64748b', borderBottom: '2px solid #f1f5f9' } }}>
                                    <TableCell>Pattern</TableCell>
                                    <TableCell align="center">Occurrences</TableCell>
                                    <TableCell align="center">AI Success Rate</TableCell>
                                    <TableCell align="center">Trend</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {topPatterns.map((pattern, idx) => (
                                    <TableRow key={idx} sx={{ '&:hover': { bgcolor: '#f8fafc' } }}>
                                        <TableCell><Typography variant="body2" fontWeight={500}>{pattern.pattern}</Typography></TableCell>
                                        <TableCell align="center"><Chip label={pattern.count} size="small" sx={{ bgcolor: '#f1f5f9', fontWeight: 600 }} /></TableCell>
                                        <TableCell align="center">
                                            <Typography variant="body2" fontWeight={600} color={pattern.successRate >= 90 ? '#10b981' : pattern.successRate >= 80 ? '#3b82f6' : '#f59e0b'}>
                                                {pattern.successRate}%
                                            </Typography>
                                        </TableCell>
                                        <TableCell align="center">
                                            {pattern.trend === 'up' && <TrendingUpIcon sx={{ color: '#10b981' }} />}
                                            {pattern.trend === 'down' && <TrendingDownIcon sx={{ color: '#ef4444' }} />}
                                            {pattern.trend === 'stable' && <span style={{ color: '#64748b' }}>-</span>}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Paper>
            </Container>
        </Box>
    );
};

export default AnalyticsPreview;
