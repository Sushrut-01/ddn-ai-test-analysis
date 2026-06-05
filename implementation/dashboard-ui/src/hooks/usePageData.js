import { useState, useEffect, useCallback } from 'react'
import { useLocation } from 'react-router-dom'

/**
 * Custom hook for fetching page data with auto-refresh on navigation
 *
 * Features:
 * - Auto-fetch on component mount
 * - Auto-fetch on route navigation (when user navigates to the page)
 * - Manual refresh function
 * - Loading and error states
 * - Optional auto-refresh interval
 *
 * @param {Function} fetchFn - Async function that fetches and returns data
 * @param {Object} options - Configuration options
 * @param {number} options.refreshInterval - Auto-refresh interval in ms (0 = disabled)
 * @param {any} options.initialData - Initial data value
 * @param {Array} options.dependencies - Additional dependencies to trigger refetch
 */
export function usePageData(fetchFn, options = {}) {
  const {
    refreshInterval = 0,
    initialData = null,
    dependencies = []
  } = options

  const location = useLocation()
  const [data, setData] = useState(initialData)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchData = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true)
      } else {
        setLoading(true)
      }
      setError(null)

      const result = await fetchFn()
      setData(result)
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Error fetching data:', err)
      setError(err.message || 'Failed to fetch data')
      setData(initialData)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [fetchFn, initialData])

  const refresh = useCallback(() => {
    fetchData(true)
  }, [fetchData])

  // Fetch on mount and when location changes (navigation)
  useEffect(() => {
    fetchData()
  }, [location.key, ...dependencies])

  // Optional auto-refresh interval
  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(() => {
        fetchData(true)
      }, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [refreshInterval, fetchData])

  return {
    data,
    loading,
    refreshing,
    error,
    refresh,
    lastUpdated,
    isLoading: loading || refreshing
  }
}

/**
 * Simplified hook for multiple API calls on a page
 * Auto-fetches all on navigation
 */
export function usePageLoad(fetchFn, deps = []) {
  const location = useLocation()
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState(null)

  const execute = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true)
      else setLoading(true)
      setError(null)
      await fetchFn()
    } catch (err) {
      console.error('Error:', err)
      setError(err.message || 'Failed to load data')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [fetchFn])

  const refresh = useCallback(() => execute(true), [execute])

  // Auto-fetch on mount and navigation
  useEffect(() => {
    execute()
  }, [location.key, ...deps])

  return { loading, refreshing, error, refresh }
}

export default usePageData
