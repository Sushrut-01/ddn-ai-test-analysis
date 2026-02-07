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

// Service Manager API client (runs on port 5007)
const serviceManagerClient = axios.create({
  baseURL: SERVICE_MANAGER_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
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

// ============================================
// PROJECT CONTEXT HELPERS
// ============================================

/**
 * Get current project ID from localStorage
 * @returns {number} Current project ID (defaults to 1 if not set)
 */
export const getCurrentProjectId = () => {
  const projectId = localStorage.getItem('current_project_id')
  if (!projectId) {
    // Set default project ID to 1 (DDN project) until multi-project API is integrated
    console.warn('getCurrentProjectId: No project selected, using default project ID: 1')
    localStorage.setItem('current_project_id', '1')
    localStorage.setItem('current_project_slug', 'ddn')
    return 1
  }
  return parseInt(projectId)
}

/**
 * Get current project slug from localStorage
 * @returns {string} Current project slug
 */
export const getCurrentProjectSlug = () => {
  return localStorage.getItem('current_project_slug') || ''
}

/**
 * Check if a project is currently selected
 * @returns {boolean} True if project is selected
 */
export const hasProjectSelected = () => {
  return !!localStorage.getItem('current_project_id')
}

/**
 * Clear current project selection
 */
export const clearProjectSelection = () => {
  localStorage.removeItem('current_project_id')
  localStorage.removeItem('current_project_slug')
}

// Add project ID to request headers for all API clients
const addProjectIdInterceptor = (client) => {
  client.interceptors.request.use(
    config => {
      const projectId = localStorage.getItem('current_project_id')
      if (projectId) {
        config.headers['X-Project-ID'] = projectId
      }
      return config
    },
    error => Promise.reject(error)
  )
}

// Apply project ID interceptor to all API clients
addProjectIdInterceptor(api)
addProjectIdInterceptor(knowledgeApiClient)
addProjectIdInterceptor(triggerApiClient)
addProjectIdInterceptor(jiraApiClient)

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

// ============================================
// PROJECT MANAGEMENT APIs
// ============================================

export const projectAPI = {
  // Get all projects accessible to current user
  getAll: () => api.get('/api/projects'),

  // Get specific project details
  getDetails: (projectId) => api.get(`/api/projects/${projectId}`),

  // Create new project (admin only)
  create: (data) => api.post('/api/projects', data),

  // Update project
  update: (projectId, data) => api.put(`/api/projects/${projectId}`, data),

  // Delete project (admin only)
  delete: (projectId) => api.delete(`/api/projects/${projectId}`),

  // Get project configuration
  getConfig: (projectId) => api.get(`/api/projects/${projectId}/config`),

  // Update project configuration
  updateConfig: (projectId, data) => api.put(`/api/projects/${projectId}/config`, data),

  // Get project team members
  getTeam: (projectId) => api.get(`/api/projects/${projectId}/team`),

  // Add user to project
  addMember: (projectId, data) => api.post(`/api/projects/${projectId}/team`, data),

  // Update user role in project
  updateMemberRole: (projectId, userId, data) =>
    api.put(`/api/projects/${projectId}/team/${userId}`, data),

  // Remove user from project
  removeMember: (projectId, userId) =>
    api.delete(`/api/projects/${projectId}/team/${userId}`),

  // Get project activity log
  getActivity: (projectId, params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/projects/${projectId}/activity${queryString ? '?' + queryString : ''}`)
  }
}

// ============================================
// PROJECT-SCOPED APIs (Use current project from localStorage)
// ============================================

// Analytics APIs (Project-scoped)
export const analyticsAPI = {
  getSummary: (timeRange = '7d') => {
    const projectId = getCurrentProjectId()
    return api.get(`/api/projects/${projectId}/analytics/summary?time_range=${timeRange}`)
  },

  getTrends: (timeRange = '30d', aggregation = 'daily') => {
    const projectId = getCurrentProjectId()
    return api.get(`/api/projects/${projectId}/analytics/trends?time_range=${timeRange}&aggregation=${aggregation}`)
  },

  getPatterns: () => {
    const projectId = getCurrentProjectId()
    return api.get(`/api/projects/${projectId}/analytics/patterns`)
  },

  getAcceptanceRate: (timeRange = '30d') => {
    const projectId = getCurrentProjectId()
    return api.get(`/api/projects/${projectId}/analytics/acceptance-rate?time_range=${timeRange}`)
  },

  getRefinementStats: (timeRange = '30d') => {
    const projectId = getCurrentProjectId()
    return api.get(`/api/projects/${projectId}/analytics/refinement-stats?time_range=${timeRange}`)
  },

  // Get project-specific stats
  getProjectStats: (timeRange = '30') => {
    const projectId = getCurrentProjectId()
    return api.get(`/api/projects/${projectId}/stats?time_range=${timeRange}`)
  }
}

// Failures APIs (Project-scoped)
export const failuresAPI = {
  getList: (params = {}) => {
    const projectId = getCurrentProjectId()
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/projects/${projectId}/failures${queryString ? '?' + queryString : ''}`)
  },

  getDetails: (failureId) => {
    const projectId = getCurrentProjectId()
    return api.get(`/api/projects/${projectId}/failures/${failureId}`)
  },

  updateFeedback: (failureId, feedback) => {
    const projectId = getCurrentProjectId()
    return api.post(`/api/projects/${projectId}/failures/${failureId}/feedback`, feedback)
  }
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

// NEW: System Monitoring APIs (Project-scoped where applicable)
export const monitoringAPI = {
  // Global system status
  getSystemStatus: () =>
    api.get('/api/system/status'),

  // Project-specific pipeline flow
  getPipelineFlow: () => {
    const projectId = getCurrentProjectId()
    return api.get(`/api/projects/${projectId}/pipeline/flow`)
  },

  // Project-specific activity
  getActivity: (limit = 20) => {
    const projectId = getCurrentProjectId()
    return api.get(`/api/projects/${projectId}/activity?limit=${limit}`)
  },

  // Project-specific stats
  getStats: () => {
    const projectId = getCurrentProjectId()
    return api.get(`/api/projects/${projectId}/stats`)
  },

  // Global health check
  getHealth: () =>
    api.get('/api/health'),

  // Project-specific build-level metrics
  getBuildsSummary: () => {
    const projectId = getCurrentProjectId()
    return api.get(`/api/projects/${projectId}/builds/summary`)
  }
}

// Service Manager API (port 5007) - All Docker services status
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

// Jira Bugs API (Project-scoped)
export const jiraAPI = {
  // Get list of Jira bugs for current project
  getBugs: async (params = {}) => {
    try {
      const projectId = getCurrentProjectId()
      const queryString = new URLSearchParams(params).toString()
      const response = await api.get(`/api/projects/${projectId}/jira/bugs${queryString ? '?' + queryString : ''}`)
      return response
    } catch (error) {
      console.error('Failed to fetch Jira bugs:', error)
      return { success: false, bugs: [], count: 0 }
    }
  },

  // Get detailed bug information
  getBugDetails: async (issueKey) => {
    try {
      const projectId = getCurrentProjectId()
      const response = await api.get(`/api/projects/${projectId}/jira/bugs/${issueKey}`)
      return response
    } catch (error) {
      console.error('Failed to fetch bug details:', error)
      return { status: 'error', data: null }
    }
  },

  // Create a new Jira issue in project's Jira
  createIssue: async (data) => {
    try {
      const projectId = getCurrentProjectId()
      const response = await api.post(`/api/projects/${projectId}/jira/create-issue`, data)
      return response
    } catch (error) {
      console.error('Failed to create Jira issue:', error)
      return { status: 'error', message: error.message }
    }
  },

  // Legacy method (for backward compatibility)
  createBug: async (data) => {
    return jiraAPI.createIssue(data)
  },

  // Get approved analyses ready for bug creation
  getApprovedAnalyses: (limit = 50) => {
    const projectId = getCurrentProjectId()
    return api.get(`/api/projects/${projectId}/jira/approved-analyses?limit=${limit}`)
  }
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

// API Keys Management
export const apiKeysAPI = {
  // Get all API keys
  getAll: () =>
    api.get('/api/keys'),

  // Create new API key
  create: (data) =>
    api.post('/api/keys', data),

  // Delete/revoke API key
  delete: (keyId) =>
    api.delete(`/api/keys/${keyId}`)
}

// Settings API - Grouped settings management
export const settingsAPI = {
  // Notification settings
  notifications: {
    get: () => api.get('/api/settings/notifications'),
    save: (data) => api.put('/api/settings/notifications', data)
  },

  // Analysis pipeline settings
  analysis: {
    get: () => api.get('/api/settings/analysis'),
    save: (data) => api.put('/api/settings/analysis', data)
  },

  // AI configuration settings
  ai: {
    get: () => api.get('/api/settings/ai'),
    save: (data) => api.put('/api/settings/ai', data)
  }
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

// Test Generator API
export const testGeneratorAPI = {
  // Generate test cases from code
  generate: (data) =>
    api.post('/api/test-generator/generate', data),

  // Generate test cases from documentation
  generateFromDocs: (data) =>
    api.post('/api/copilot/generate-tests', data),

  // Get generated test history
  getHistory: () =>
    api.get('/api/test-generator/history'),

  // Save test cases
  save: (data) =>
    api.post('/api/test-generator/save', data)
}

// User Management API
export const userManagementAPI = {
  // Get all users
  getUsers: () =>
    api.get('/api/users'),

  // Invite new user
  inviteUser: (data) =>
    api.post('/api/users/invite', data),

  // Update user
  updateUser: (userId, data) =>
    api.put(`/api/users/${userId}`, data),

  // Delete user
  deleteUser: (userId) =>
    api.delete(`/api/users/${userId}`),

  // Reset user password
  resetPassword: (userId) =>
    api.post(`/api/users/${userId}/reset-password`),

  // Get roles
  getRoles: () =>
    api.get('/api/roles'),

  // Create role
  createRole: (data) =>
    api.post('/api/roles', data),

  // Update role
  updateRole: (roleId, data) =>
    api.put(`/api/roles/${roleId}`, data),

  // Delete role
  deleteRole: (roleId) =>
    api.delete(`/api/roles/${roleId}`),

  // Get teams
  getTeams: () =>
    api.get('/api/teams'),

  // Create team
  createTeam: (data) =>
    api.post('/api/teams', data)
}

// Export API - for generating reports/exports
export const exportAPI = {
  // Export failures to CSV
  exportFailuresCSV: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/export/failures/csv${queryString ? '?' + queryString : ''}`, {
      responseType: 'blob'
    })
  },

  // Export failures to PDF
  exportFailuresPDF: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/export/failures/pdf${queryString ? '?' + queryString : ''}`, {
      responseType: 'blob'
    })
  },

  // Export audit logs
  exportAuditLogs: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/export/audit-logs${queryString ? '?' + queryString : ''}`, {
      responseType: 'blob'
    })
  },

  // Export analytics report
  exportAnalytics: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/api/export/analytics${queryString ? '?' + queryString : ''}`, {
      responseType: 'blob'
    })
  },

  // Send report via email
  sendReportEmail: (data) =>
    api.post('/api/export/email', data)
}

// Integration API - for testing and managing integrations
export const integrationAPI = {
  // Test connection to a service
  testConnection: (service, config = {}) =>
    api.post('/api/integrations/test', { service, config }),

  // Get all integrations
  getAll: () =>
    api.get('/api/integrations'),

  // Add integration
  add: (data) =>
    api.post('/api/integrations', data),

  // Update integration
  update: (integrationId, data) =>
    api.put(`/api/integrations/${integrationId}`, data),

  // Delete integration
  delete: (integrationId) =>
    api.delete(`/api/integrations/${integrationId}`)
}

export default api
