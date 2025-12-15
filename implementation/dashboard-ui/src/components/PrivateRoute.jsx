import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { useAuth } from '../hooks/useAuth';

/**
 * PrivateRoute Component
 *
 * Protects routes that require authentication.
 * Redirects to login if user is not authenticated.
 * Optionally checks for specific roles.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Child components to render if authenticated
 * @param {string} [props.requiredRole] - Optional role required to access route
 * @param {string} [props.redirectTo='/login'] - Redirect path if not authenticated
 *
 * @example
 * // Require authentication
 * <PrivateRoute>
 *   <Dashboard />
 * </PrivateRoute>
 *
 * @example
 * // Require admin role
 * <PrivateRoute requiredRole="admin">
 *   <AdminPanel />
 * </PrivateRoute>
 */
const PrivateRoute = ({
  children,
  requiredRole = null,
  redirectTo = '/login'
}) => {
  const { user, loading, isAuthenticated, hasRole } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          gap: 2
        }}
      >
        <CircularProgress size={48} />
        <Typography variant="body1" color="text.secondary">
          Verifying authentication...
        </Typography>
      </Box>
    );
  }

  // Not authenticated - redirect to login
  if (!isAuthenticated) {
    return (
      <Navigate
        to={redirectTo}
        state={{ from: location }}
        replace
      />
    );
  }

  // Check for required role if specified
  if (requiredRole && !hasRole(requiredRole)) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          gap: 2,
          px: 3
        }}
      >
        <Typography variant="h4" color="error">
          Access Denied
        </Typography>
        <Typography variant="body1" color="text.secondary" textAlign="center">
          You don't have permission to access this page.
          <br />
          Required role: <strong>{requiredRole}</strong>
          <br />
          Your role: <strong>{user?.role || 'unknown'}</strong>
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Navigate to="/dashboard" replace />
        </Box>
      </Box>
    );
  }

  // Authenticated and authorized - render children
  return <>{children}</>;
};

export default PrivateRoute;
