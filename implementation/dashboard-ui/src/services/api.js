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

// Separate API client for Jira Integration (runs on port 5009)
const jiraApiClient = axios.create({
  baseURL: JIRA_API_URL,
  timeout: 30000,
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

// Response interceptor for Jira API
jiraApiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('Jira API Error:', error)
    return Promise.reject(error)
  }
)

// JWT Token Management
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })

  failedQueue = []
}

// Request interceptor - Add JWT token to all requests
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle token expiration
api.interceptors.response.use(
  response => response.data,
  async error => {
    const originalRequest = error.config

    // If 401 Unauthorized and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return axios(originalRequest)
          })
          .catch(err => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')

      if (!refreshToken) {
        // No refresh token, redirect to login
        localStorage.removeItem('auth_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        // Try to refresh the token
        const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:5013'
        const response = await axios.post(`${AUTH_API_URL}/api/auth/refresh`, {
          refresh_token: refreshToken
        })

        if (response.data.success) {
          const { access_token, refresh_token: newRefreshToken } = response.data.data

          // Update tokens
          localStorage.setItem('auth_token', access_token)
          if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken)
          }

          // Update authorization header
          api.defaults.headers.common.Authorization = `Bearer ${access_token}`
          originalRequest.headers.Authorization = `Bearer ${access_token}`

          // Process queued requests
          processQueue(null, access_token)

          isRefreshing = false

          // Retry original request
          return axios(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        processQueue(refreshError, null)
        isRefreshing = false

        localStorage.removeItem('auth_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'

        return Promise.reject(refreshError)
      }
    }

    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Add JWT interceptor to other API clients
const addJWTInterceptor = (client) => {
  client.interceptors.request.use(
    config => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    error => Promise.reject(error)
  )
}

// Apply to all API clients
addJWTInterceptor(knowledgeApiClient)
addJWTInterceptor(triggerApiClient)
addJWTInterceptor(jiraApiClient)
addJWTInterceptor(serviceManagerClient)

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
  // Get list of Jira bugs from Jira service (port 5009)
  getBugs: async (params = {}) => {
    try {
      const queryString = new URLSearchParams(params).toString()
      const response = await jiraApiClient.get(`/api/bugs${queryString ? '?' + queryString : ''}`)
      return response
    } catch (error) {
      console.error('Failed to fetch Jira bugs:', error)
      return { status: 'error', data: { issues: [], total: 0 } }
    }
  },

  // Get detailed bug information from Jira service
  getBugDetails: async (issueKey) => {
    try {
      const response = await jiraApiClient.get(`/api/bugs/${issueKey}`)
      return response
    } catch (error) {
      console.error('Failed to fetch bug details:', error)
      return { status: 'error', data: null }
    }
  },

  // Create a new Jira bug from analysis
  createBug: async (data) => {
    try {
      const response = await jiraApiClient.post('/api/jira/create-issue', data)
      return response
    } catch (error) {
      console.error('Failed to create Jira bug:', error)
      return { status: 'error', message: error.message }
    }
  },

  // Get approved analyses ready for bug creation (from dashboard API)
  getApprovedAnalyses: (limit = 50) =>
    api.get(`/api/failures?analyzed=true&classification=CODE_ERROR&limit=${limit}`)
}

// GitHub PR API (for PR Workflow page)
export const githubAPI = {
  // Get list of pull requests
  getPRs: async (params = {}) => {
    try {
      const queryString = new URLSearchParams(params).toString()
      const response = await api.get(`/api/github/prs${queryString ? '?' + queryString : ''}`)
      return response
    } catch (error) {
      console.error('Failed to fetch GitHub PRs:', error)
      return { status: 'error', data: { prs: [], total: 0 } }
    }
  },

  // Get detailed PR information
  getPRDetails: async (prNumber) => {
    try {
      const response = await api.get(`/api/github/pr/${prNumber}`)
      return response
    } catch (error) {
      console.error('Failed to fetch PR details:', error)
      return { status: 'error', data: null }
    }
  }
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

// Authentication API
const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:5013'

export const authAPI = {
  // Register new user
  register: async (userData) => {
    const response = await axios.post(`${AUTH_API_URL}/api/auth/register`, userData)
    return response.data
  },

  // Login user
  login: async (email, password) => {
    const response = await axios.post(`${AUTH_API_URL}/api/auth/login`, { email, password })
    return response.data
  },

  // Logout user
  logout: async (token) => {
    const response = await axios.post(
      `${AUTH_API_URL}/api/auth/logout`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    )
    return response.data
  },

  // Get current user info
  getCurrentUser: async (token) => {
    const response = await axios.get(`${AUTH_API_URL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    return response.data
  },

  // Refresh access token
  refreshToken: async (refreshToken) => {
    const response = await axios.post(`${AUTH_API_URL}/api/auth/refresh`, {
      refresh_token: refreshToken
    })
    return response.data
  },

  // Get all users (admin only)
  getUsers: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    const response = await axios.get(
      `${AUTH_API_URL}/api/users${queryString ? '?' + queryString : ''}`,
      { headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` } }
    )
    return response.data
  },

  // Update user
  updateUser: async (userId, data) => {
    const response = await axios.put(`${AUTH_API_URL}/api/users/${userId}`, data, {
      headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` }
    })
    return response.data
  },

  // Delete user (admin only)
  deleteUser: async (userId) => {
    const response = await axios.delete(`${AUTH_API_URL}/api/users/${userId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` }
    })
    return response.data
  },

  // Get user stats
  getUserStats: async (userId) => {
    const response = await axios.get(`${AUTH_API_URL}/api/users/${userId}/stats`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` }
    })
    return response.data
  }
}

// Configuration Management API
export const configAPI = {
  // Get all configurations
  getAll: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/config${queryString ? '?' + queryString : ''}`)
  },

  // Get specific configuration
  get: (configKey) =>
    api.get(`/api/config/${configKey}`),

  // Update configuration
  update: (configKey, data) =>
    api.put(`/api/config/${configKey}`, data),

  // Test configuration (SMTP, Jira, GitHub)
  test: (data) =>
    api.post('/api/config/test', data),

  // Get configuration categories
  getCategories: () =>
    api.get('/api/config/categories')
}

// Copilot API - AI-powered code assistant
export const copilotAPI = {
  // Send a chat message and get AI response
  chat: (data) =>
    api.post('/api/copilot/chat', data),

  // Stream chat response (for real-time streaming)
  streamChat: async (data, onChunk) => {
    const response = await fetch(`${API_BASE_URL}/api/copilot/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n').filter(line => line.trim())

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6))
            onChunk(data)
          } catch (e) {
            console.error('Failed to parse stream data:', e)
          }
        }
      }
    }
  },

  // Get chat history
  getHistory: (limit = 50) =>
    api.get(`/api/copilot/history?limit=${limit}`),

  // Clear chat history
  clearHistory: () =>
    api.delete('/api/copilot/history'),

  // Analyze code snippet
  analyzeCode: (data) =>
    api.post('/api/copilot/analyze', data),

  // Generate code based on description
  generateCode: (data) =>
    api.post('/api/copilot/generate', data),

  // Explain code
  explainCode: (data) =>
    api.post('/api/copilot/explain', data),

  // Optimize code
  optimizeCode: (data) =>
    api.post('/api/copilot/optimize', data),

  // Generate tests
  generateTests: (data) =>
    api.post('/api/copilot/generate-tests', data),

  // Review code
  reviewCode: (data) =>
    api.post('/api/copilot/review', data)
}

export default api
