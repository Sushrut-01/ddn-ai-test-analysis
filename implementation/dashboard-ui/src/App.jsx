import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Failures from './pages/Failures'
import FailureDetails from './pages/FailureDetails'
import Analytics from './pages/Analytics'
import ManualTrigger from './pages/ManualTrigger'

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
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/failures" element={<Failures />} />
          <Route path="/failures/:buildId" element={<FailureDetails />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/manual-trigger" element={<ManualTrigger />} />
        </Routes>
      </Layout>
    </ThemeProvider>
  )
}

export default App
