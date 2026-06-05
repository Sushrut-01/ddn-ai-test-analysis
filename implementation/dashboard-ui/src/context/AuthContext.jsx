import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

// Auth service base URL
const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:5013';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing token on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('auth_token');

      if (token) {
        try {
          // Verify token and get user info
          const response = await axios.get(`${AUTH_API_URL}/api/auth/me`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });

          if (response.data.success) {
            setUser(response.data.data.user);
          } else {
            // Token invalid, clear it
            localStorage.removeItem('auth_token');
            localStorage.removeItem('refresh_token');
          }
        } catch (error) {
          console.error('Token verification failed:', error);
          // Token expired or invalid
          localStorage.removeItem('auth_token');
          localStorage.removeItem('refresh_token');
        }
      }

      setLoading(false);
    };

    initAuth();
  }, []);

  // Login function
  const login = async (email, password) => {
    try {
      console.log('🔐 AuthContext.login() called');
      console.log('🔐 Email:', email);
      console.log('🔐 API URL:', AUTH_API_URL);

      setError(null);
      const response = await axios.post(`${AUTH_API_URL}/api/auth/login`, {
        email,
        password
      });

      console.log('🔐 API Response:', response.data);

      if (response.data.status === 'success' && response.data.data) {
        const { access_token, refresh_token, user: userData } = response.data.data;

        console.log('✅ Login successful, storing tokens...');

        // Store tokens
        localStorage.setItem('auth_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);

        // Set user
        setUser(userData);

        console.log('✅ User set:', userData);

        return { success: true };
      } else {
        console.error('❌ Login failed:', response.data.message);
        setError(response.data.message || 'Login failed');
        return { success: false, error: response.data.message };
      }
    } catch (error) {
      console.error('❌ Login error:', error);
      console.error('❌ Error response:', error.response?.data);

      const errorMessage = error.response?.data?.message || 'Login failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      setError(null);
      const response = await axios.post(`${AUTH_API_URL}/api/auth/register`, userData);

      if (response.data.success) {
        const { access_token, refresh_token, user: newUser } = response.data.data;

        // Store tokens
        localStorage.setItem('auth_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);

        // Set user
        setUser(newUser);

        return { success: true };
      } else {
        setError(response.data.message || 'Registration failed');
        return { success: false, error: response.data.message };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Registration failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Logout function
  const logout = async () => {
    try {
      const token = localStorage.getItem('auth_token');

      if (token) {
        // Call logout endpoint
        await axios.post(
          `${AUTH_API_URL}/api/auth/logout`,
          {},
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local state and storage
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    }
  };

  // Refresh token function
  const refreshToken = async () => {
    try {
      const refresh = localStorage.getItem('refresh_token');

      if (!refresh) {
        throw new Error('No refresh token');
      }

      const response = await axios.post(`${AUTH_API_URL}/api/auth/refresh`, {
        refresh_token: refresh
      });

      if (response.data.success) {
        const { access_token, refresh_token: newRefreshToken } = response.data.data;

        // Update tokens
        localStorage.setItem('auth_token', access_token);
        if (newRefreshToken) {
          localStorage.setItem('refresh_token', newRefreshToken);
        }

        return access_token;
      } else {
        throw new Error('Token refresh failed');
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      // Clear tokens and logout
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
      return null;
    }
  };

  // Check if user has specific role
  const hasRole = (role) => {
    return user?.role === role;
  };

  // Check if user is admin
  const isAdmin = () => {
    return user?.role === 'admin';
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    refreshToken,
    hasRole,
    isAdmin,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
