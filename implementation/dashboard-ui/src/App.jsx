import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Test from './Test'
import Failures from './pages/Failures'
import FailureDetails from './pages/FailureDetails'
import Analytics from './pages/Analytics'
import ManualTrigger from './pages/ManualTrigger'
import KnowledgeManagement from './pages/KnowledgeManagement'
import TriggerAnalysis from './pages/TriggerAnalysis' // Task 0F.7: Bulk analysis page
import ErrorBoundary from './ErrorBoundary'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2'
    },
    secondary: {
      main: '#dc004e'
    },
    success: {
      main: '#4caf50'
    },
    error: {
      main: '#f44336'
    },
    warning: {
      main: '#ff9800'
    }
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif'
  }
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Layout>
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/test" element={<Test />} />
            <Route path="/failures" element={<Failures />} />
            <Route path="/failures/:buildId" element={<FailureDetails />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/manual-trigger" element={<ManualTrigger />} />
            <Route path="/trigger-analysis" element={<TriggerAnalysis />} />
            <Route path="/knowledge" element={<KnowledgeManagement />} />
          </Routes>
        </ErrorBoundary>
      </Layout>
    </ThemeProvider>
  )
}

export default App
