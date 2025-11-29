import axios from 'axios'

// API Endpoints - Match docker-compose-unified.yml ports
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5006'
const KNOWLEDGE_API_URL = import.meta.env.VITE_KNOWLEDGE_API_URL || 'http://localhost:5015'
const JIRA_API_URL = import.meta.env.VITE_JIRA_API_URL || 'http://localhost:5009'
const SLACK_API_URL = import.meta.env.VITE_SLACK_API_URL || 'http://localhost:5012'
const SERVICE_MANAGER_URL = import.meta.env.VITE_SERVICE_MANAGER_URL || 'http://localhost:5007'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Separate API client for Knowledge Management (runs on different port)
const knowledgeApiClient = axios.create({
  baseURL: KNOWLEDGE_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Analytics APIs
export const analyticsAPI = {
  getSummary: (timeRange = '7d') =>
    api.get(`/api/analytics/summary?time_range=${timeRange}`),

  getTrends: (timeRange = '30d', aggregation = 'daily') =>
    api.get(`/api/analytics/trends?time_range=${timeRange}&aggregation=${aggregation}`),

  getPatterns: () =>
    api.get('/api/analytics/patterns'),

  getAcceptanceRate: (timeRange = '30d') =>
    api.get(`/api/analytics/acceptance-rate?time_range=${timeRange}`),

  getRefinementStats: (timeRange = '30d') =>
    api.get(`/api/analytics/refinement-stats?time_range=${timeRange}`)
}

// Failures APIs
export const failuresAPI = {
  getList: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/failures?${queryString}`)
  },

  getDetails: (buildId) =>
    api.get(`/api/failures/${buildId}`)
}

// Manual Trigger APIs
export const triggerAPI = {
  triggerAnalysis: (data) =>
    api.post('/api/trigger/manual', data),

  getHistory: (page = 1, limit = 20) =>
    api.get(`/api/trigger/history?page=${page}&limit=${limit}`)
}

// Feedback APIs
export const feedbackAPI = {
  submit: (data) =>
    api.post('/api/feedback/submit', data),

  getRecent: (limit = 20) =>
    api.get(`/api/feedback/recent?limit=${limit}`),

  getRefinementHistory: (buildId) =>
    api.get(`/api/feedback/refinement-history/${buildId}`)
}

// Metrics APIs
export const metricsAPI = {
  getModelMetrics: (timeRange = '7d') =>
    api.get(`/api/metrics/model?time_range=${timeRange}`)
}

// Status APIs
export const statusAPI = {
  getLiveStatus: () =>
    api.get('/api/status/live')
}

// NEW: System Monitoring APIs
export const monitoringAPI = {
  getSystemStatus: () =>
    api.get('/api/system/status'),

  getPipelineFlow: () =>
    api.get('/api/pipeline/flow'),

  getActivity: (limit = 20) =>
    api.get(`/api/activity?limit=${limit}`),

  getStats: () =>
    api.get('/api/stats'),

  getHealth: () =>
    api.get('/api/health')
}

// Knowledge Management APIs (Task 0-HITL-KM)
// Uses separate API client on port 5008
export const knowledgeAPI = {
  // Get all knowledge documents with optional filters
  getDocs: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    const response = await knowledgeApiClient.get(`/api/knowledge/docs${queryString ? '?' + queryString : ''}`)
    return response.data
  },

  // Get specific document by ID
  getDoc: async (docId) => {
    const response = await knowledgeApiClient.get(`/api/knowledge/docs/${docId}`)
    return response.data
  },

  // Add new knowledge document
  addDoc: async (data) => {
    const response = await knowledgeApiClient.post('/api/knowledge/docs', data)
    return response.data
  },

  // Update existing knowledge document
  updateDoc: async (docId, data) => {
    const response = await knowledgeApiClient.put(`/api/knowledge/docs/${docId}`, data)
    return response.data
  },

  // Delete knowledge document
  deleteDoc: async (docId, user = 'system') => {
    const response = await knowledgeApiClient.delete(`/api/knowledge/docs/${docId}?user=${user}`)
    return response.data
  },

  // Get available categories
  getCategories: async () => {
    const response = await knowledgeApiClient.get('/api/knowledge/categories')
    return response.data
  },

  // Trigger category refresh in ReAct agent
  refreshCategories: async () => {
    const response = await knowledgeApiClient.post('/api/knowledge/refresh')
    return response.data
  },

  // Get knowledge base statistics
  getStats: async () => {
    const response = await knowledgeApiClient.get('/api/knowledge/stats')
    return response.data
  }
}

// Phase B: Code Fix Automation APIs
export const fixAPI = {
  // Approve a code fix and trigger PR creation
  approve: (data) =>
    api.post('/api/fixes/approve', data),

  // Reject a code fix
  reject: (data) =>
    api.post('/api/fixes/reject', data),

  // Get status of a fix application
  getStatus: (fixId) =>
    api.get(`/api/fixes/${fixId}/status`),

  // Get fix application history with optional filters
  getHistory: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/fixes/history?${queryString}`)
  },

  // Rollback a fix application
  rollback: (data) =>
    api.post('/api/fixes/rollback', data),

  // Get fix success analytics
  getAnalytics: () =>
    api.get('/api/fixes/analytics')
}

// Jira Bugs API
export const jiraAPI = {
  // Get list of Jira bugs
  getBugs: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/jira/bugs?${queryString}`)
  },

  // Create a new Jira bug from analysis
  createBug: (data) =>
    api.post('/api/jira/bugs', data),

  // Get approved analyses ready for bug creation
  getApprovedAnalyses: (limit = 50) =>
    api.get(`/api/jira/approved-analyses?limit=${limit}`)
}

// Pipeline Jobs API
export const pipelineAPI = {
  // Get active and recent pipeline jobs
  getJobs: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/pipeline/jobs?${queryString}`)
  },

  // Get logs for a specific job
  getJobLogs: (jobId) =>
    api.get(`/api/pipeline/jobs/${jobId}/logs`),

  // Get pipeline flow status
  getFlow: () =>
    api.get('/api/pipeline/flow')
}

// Notifications API
export const notificationsAPI = {
  // Get notifications
  getNotifications: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/notifications?${queryString}`)
  },

  // Mark notification as read
  markAsRead: (notificationId) =>
    api.post(`/api/notifications/${notificationId}/read`),

  // Mark all notifications as read
  markAllAsRead: () =>
    api.post('/api/notifications/read-all')
}

// Audit Log API
export const auditLogAPI = {
  // Get audit log entries
  getEntries: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/audit-log?${queryString}`)
  },

  // Export audit log as CSV
  exportCSV: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return `${API_BASE_URL}/api/audit-log/export?${queryString}`
  }
}

export default api
