import axios from 'axios'

// API Endpoints - Match docker-compose-unified.yml ports
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5006'
const KNOWLEDGE_API_URL = import.meta.env.VITE_KNOWLEDGE_API_URL || 'http://localhost:5015'
const JIRA_API_URL = import.meta.env.VITE_JIRA_API_URL || 'http://localhost:5009'
const SLACK_API_URL = import.meta.env.VITE_SLACK_API_URL || 'http://localhost:5012'
const SERVICE_MANAGER_URL = import.meta.env.VITE_SERVICE_MANAGER_URL || 'http://localhost:5007'
const TRIGGER_API_URL = import.meta.env.VITE_TRIGGER_API_URL || 'http://localhost:5004'

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

// Separate API client for Manual Trigger (runs on port 5004)
const triggerApiClient = axios.create({
  baseURL: TRIGGER_API_URL,
  timeout: 120000, // Longer timeout for AI analysis
  headers: {
    'Content-Type': 'application/json'
  }
})

// Response interceptor for trigger API
triggerApiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('Trigger API Error:', error)
    return Promise.reject(error)
  }
)

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
    api.get('/api/health'),

  // Build-level metrics (dual metrics support)
  getBuildsSummary: () =>
    api.get('/api/builds/summary')
}

// Service Manager API (port 5007) - All Docker services status
const serviceManagerClient = axios.create({
  baseURL: SERVICE_MANAGER_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

export const serviceManagerAPI = {
  // Get all services status
  getAllServices: async () => {
    try {
      const response = await serviceManagerClient.get('/api/services/status')
      return response.data
    } catch (error) {
      console.error('Service Manager API Error:', error)
      return {}
    }
  },

  // Start a service
  startService: (serviceName) =>
    serviceManagerClient.post(`/api/services/${serviceName}/start`),

  // Stop a service
  stopService: (serviceName) =>
    serviceManagerClient.post(`/api/services/${serviceName}/stop`),

  // Restart a service
  restartService: (serviceName) =>
    serviceManagerClient.post(`/api/services/${serviceName}/restart`)
}

// External Services APIs (Langfuse, Celery/Flower, n8n, Redis)
const LANGFUSE_URL = import.meta.env.VITE_LANGFUSE_URL || 'http://localhost:3000'
const FLOWER_URL = import.meta.env.VITE_FLOWER_URL || 'http://localhost:5555'
const N8N_URL = import.meta.env.VITE_N8N_URL || 'http://localhost:5678'

// Langfuse API (LLM observability)
export const langfuseAPI = {
  getStats: async () => {
    try {
      // Langfuse public API for dashboard stats
      const response = await fetch(`${LANGFUSE_URL}/api/public/metrics`, {
        headers: { 'Content-Type': 'application/json' }
      })
      if (!response.ok) throw new Error('Langfuse API error')
      return await response.json()
    } catch (error) {
      console.error('Langfuse API Error:', error)
      return null
    }
  }
}

// Flower API (Celery monitoring)
export const flowerAPI = {
  getWorkers: async () => {
    try {
      const response = await fetch(`${FLOWER_URL}/api/workers`)
      if (!response.ok) throw new Error('Flower API error')
      return await response.json()
    } catch (error) {
      console.error('Flower API Error:', error)
      return {}
    }
  },
  getTasks: async () => {
    try {
      const response = await fetch(`${FLOWER_URL}/api/tasks`)
      if (!response.ok) throw new Error('Flower API error')
      return await response.json()
    } catch (error) {
      console.error('Flower API Error:', error)
      return {}
    }
  },
  getStats: async () => {
    try {
      const response = await fetch(`${FLOWER_URL}/dashboard?json=1`)
      if (!response.ok) throw new Error('Flower API error')
      return await response.json()
    } catch (error) {
      console.error('Flower API Error:', error)
      return null
    }
  }
}

// n8n API (Agentic Workflows) - DEPRECATED, use workflowsAPI instead
export const n8nAPI = {
  getWorkflows: async () => {
    // Redirect to our Python workflows API
    return workflowsAPI.getWorkflows()
  },
  getExecutions: async (limit = 20) => {
    // Redirect to our Python workflows API
    return workflowsAPI.getExecutions(limit)
  }
}

// Python-based Agentic Workflows API (replaces n8n)
export const workflowsAPI = {
  getWorkflows: async () => {
    try {
      const response = await api.get('/api/workflows')
      return response.workflows || []
    } catch (error) {
      console.error('Workflows API Error:', error)
      return []
    }
  },
  getWorkflowDetails: async (workflowId) => {
    try {
      const response = await api.get(`/api/workflows/${workflowId}`)
      return response.workflow || null
    } catch (error) {
      console.error('Workflow Details API Error:', error)
      return null
    }
  },
  getExecutions: async (limit = 20) => {
    try {
      const response = await api.get(`/api/workflows/executions?limit=${limit}`)
      return response.executions || []
    } catch (error) {
      console.error('Workflow Executions API Error:', error)
      return []
    }
  },
  getStats: async () => {
    try {
      const response = await api.get('/api/workflows')
      return response.execution_stats || { total: 0, successful: 0, failed: 0 }
    } catch (error) {
      console.error('Workflow Stats API Error:', error)
      return { total: 0, successful: 0, failed: 0 }
    }
  }
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

// AI Chatbot API
export const chatAPI = {
  // Send a chat message
  sendMessage: (message, conversationHistory = []) =>
    api.post('/api/chat', { message, conversation_history: conversationHistory }),

  // Execute specific data queries
  query: (queryType, params = {}) =>
    api.post('/api/chat/query', { query_type: queryType, params })
}

// RAG Approval HITL API (Human-in-the-Loop for non-code errors)
export const ragApprovalAPI = {
  // Get pending RAG approvals for human review
  getPending: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/rag/pending${queryString ? '?' + queryString : ''}`)
  },

  // Approve a RAG suggestion
  approve: (data) =>
    api.post('/api/rag/approve', data),

  // Reject a RAG suggestion with feedback
  reject: (data) =>
    api.post('/api/rag/reject', data),

  // Escalate to AI for deeper analysis
  escalate: (data) =>
    api.post('/api/rag/escalate', data),

  // Get RAG approval statistics
  getStats: () =>
    api.get('/api/rag/stats'),

  // Get RAG approval history (approved, rejected, escalated)
  getHistory: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/rag/history${queryString ? '?' + queryString : ''}`)
  },

  // Add item to RAG approval queue (used by RAG system)
  add: (data) =>
    api.post('/api/rag/add', data)
}

export default api
