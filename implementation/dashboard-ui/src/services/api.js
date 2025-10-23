import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5005'

const api = axios.create({
  baseURL: API_BASE_URL,
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
    api.get('/api/analytics/patterns')
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
    api.get(`/api/feedback/recent?limit=${limit}`)
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

export default api
