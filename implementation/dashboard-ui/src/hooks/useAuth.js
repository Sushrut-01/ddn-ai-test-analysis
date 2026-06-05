import { useContext } from 'react';
import AuthContext from '../context/AuthContext';

/**
 * Custom hook to access authentication context
 *
 * @returns {Object} Authentication context value
 * @property {Object|null} user - Current authenticated user
 * @property {boolean} loading - Loading state
 * @property {string|null} error - Error message
 * @property {Function} login - Login function (email, password)
 * @property {Function} register - Register function (userData)
 * @property {Function} logout - Logout function
 * @property {Function} refreshToken - Refresh access token
 * @property {Function} hasRole - Check if user has specific role
 * @property {Function} isAdmin - Check if user is admin
 * @property {boolean} isAuthenticated - Whether user is authenticated
 *
 * @example
 * const { user, login, logout, isAdmin } = useAuth();
 *
 * // Login
 * const result = await login('user@example.com', 'password');
 * if (result.success) {
 *   console.log('Logged in as:', user);
 * }
 *
 * // Check admin
 * if (isAdmin()) {
 *   // Show admin features
 * }
 *
 * // Logout
 * await logout();
 */
export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
};

export default useAuth;
