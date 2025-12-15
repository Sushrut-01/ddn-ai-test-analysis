import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { ThemeProvider as ColorThemeProvider } from './theme/ThemeContext'
import { AuthProvider } from './context/AuthContext'
import PrivateRoute from './components/PrivateRoute'
import Layout from './components/Layout'

// Production Pages (previously Preview pages)
import Dashboard from './pages/DashboardPreviewNew'
import Failures from './pages/FailuresPreview'
import FailureDetails from './pages/FailureDetailsPreview'
import Analytics from './pages/AnalyticsPreview'
import ManualTrigger from './pages/ManualTriggerPreview'
import BulkTrigger from './pages/TriggerAnalysisPreview'
import Knowledge from './pages/KnowledgeManagementPreview'
import Services from './pages/ServicesMonitoringPreview'
import Pipeline from './pages/PipelineStatusPreview'
import JiraBugs from './pages/JiraBugsPreview'
import PRWorkflow from './pages/PRWorkflowPreview'
import AIChatbot from './pages/AIChatbotPreview'
import TestGenerator from './pages/TestCaseGeneratorPreview'
import Copilot from './pages/CopilotPage'
import Users from './pages/UserManagementPreview'
import Configuration from './pages/ConfigurationPreview'
import Notifications from './pages/NotificationsCenterPreview'
import AuditLog from './pages/AuditLogPreview'
import RAGApproval from './pages/RAGApprovalPreview'
import AIRootCause from './pages/AIRootCausePreview'
import CodeHealing from './pages/FailuresPendingPreview'

// Auth Pages
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'

// Utils
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
    <AuthProvider>
      <ColorThemeProvider>
        <MuiThemeProvider theme={theme}>
          <CssBaseline />
          <Routes>
            {/* Auth pages - outside Layout, no authentication required */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />

            {/* All other routes with Layout and authentication required */}
            <Route path="/*" element={
              <PrivateRoute>
                <Layout>
                  <ErrorBoundary>
                    <Routes>
                      {/* Dashboard & Monitoring */}
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/pipeline" element={<Pipeline />} />
                      <Route path="/services" element={<Services />} />

                      {/* Analysis & Failures */}
                      <Route path="/failures" element={<Dashboard />} /> {/* Redirect to Overview */}
                      <Route path="/failures/:id" element={<FailureDetails />} /> {/* AI Analysis detail page */}
                      <Route path="/bulk-trigger" element={<BulkTrigger />} /> {/* Manual Trigger Flow */}
                      <Route path="/rag-approval" element={<RAGApproval />} /> {/* RAG HITL Review Queue */}
                      <Route path="/approval-flow" element={<Failures />} /> {/* Approval Flow - CODE_ERROR items approved for AI */}
                      <Route path="/ai-root-cause" element={<AIRootCause />} /> {/* AI Root Cause Analysis - dedicated page */}
                      <Route path="/code-healing" element={<CodeHealing />} /> {/* Code Healing Pipeline - PR, Build, Jira flow */}
                      <Route path="/manual-trigger" element={<ManualTrigger />} /> {/* Trigger Records */}
                      <Route path="/analytics" element={<Analytics />} />

                      {/* Integrations */}
                      <Route path="/jira-bugs" element={<JiraBugs />} />
                      <Route path="/pr-workflow" element={<PRWorkflow />} />

                      {/* AI Tools */}
                      <Route path="/ai-chatbot" element={<AIChatbot />} />
                      <Route path="/ai-copilot" element={<Copilot />} />
                      <Route path="/test-generator" element={<TestGenerator />} />
                      <Route path="/knowledge" element={<Knowledge />} />

                      {/* Administration - Some routes may need admin role */}
                      <Route path="/users" element={
                        <PrivateRoute requiredRole="admin">
                          <Users />
                        </PrivateRoute>
                      } />
                      <Route path="/config" element={
                        <PrivateRoute requiredRole="admin">
                          <Configuration />
                        </PrivateRoute>
                      } />
                      <Route path="/notifications" element={<Notifications />} />
                      <Route path="/audit-log" element={<AuditLog />} />
                    </Routes>
                  </ErrorBoundary>
                </Layout>
              </PrivateRoute>
            } />
          </Routes>
        </MuiThemeProvider>
      </ColorThemeProvider>
    </AuthProvider>
  )
}

export default App
