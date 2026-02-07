import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  InputAdornment,
  Alert,
  CircularProgress,
  Link,
  Fade,
  Zoom
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import EmailIcon from '@mui/icons-material/Email'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import LockResetIcon from '@mui/icons-material/LockReset'
import { useNavigate, Link as RouterLink } from 'react-router-dom'

const FloatingShape = ({ delay, duration, size, top, left, color }) => (
  <Box
    sx={{
      position: 'absolute',
      top,
      left,
      width: size,
      height: size,
      borderRadius: '50%',
      background: `linear-gradient(135deg, ${alpha(color, 0.3)}, ${alpha(color, 0.1)})`,
      animation: `float ${duration}s ease-in-out infinite`,
      animationDelay: `${delay}s`,
      filter: 'blur(1px)',
      '@keyframes float': {
        '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
        '50%': { transform: 'translateY(-20px) rotate(180deg)' }
      }
    }}
  />
)

function ForgotPasswordPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!email || !email.includes('@')) {
      setError('Please enter a valid email address')
      return
    }

    setLoading(true)
    setError('')

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))

    setSuccess(true)
    setLoading(false)
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)'
      }}
    >
      {/* Background Elements */}
      <FloatingShape delay={0} duration={6} size={100} top="10%" left="15%" color="#10b981" />
      <FloatingShape delay={1} duration={8} size={150} top="60%" left="10%" color="#14b8a6" />
      <FloatingShape delay={2} duration={7} size={80} top="20%" left="80%" color="#10b981" />
      <FloatingShape delay={0.5} duration={9} size={120} top="70%" left="75%" color="#14b8a6" />

      <Zoom in timeout={500}>
        <Paper
          elevation={0}
          sx={{
            width: '100%',
            maxWidth: 440,
            p: 4,
            borderRadius: 4,
            background: 'linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(31, 41, 55, 0.95) 50%, rgba(17, 24, 39, 0.95) 100%)',
            backdropFilter: 'blur(20px)',
            border: '1.5px solid',
            borderColor: alpha('#10b981', 0.3),
            boxShadow: '0 25px 80px rgba(0,0,0,0.6), 0 0 40px rgba(16, 185, 129, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
            position: 'relative',
            zIndex: 1,
            m: 2
          }}
        >
          {/* Logo */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 4, justifyContent: 'center' }}>
            <Box
              sx={{
                width: 44,
                height: 44,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #10b981, #14b8a6)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 12px rgba(16, 185, 129, 0.4), inset 0 1px 4px rgba(255, 255, 255, 0.2)',
                border: '1px solid rgba(16, 185, 129, 0.3)'
              }}
            >
              <SmartToyIcon sx={{ color: 'white', filter: 'drop-shadow(0 2px 3px rgba(0, 0, 0, 0.3))' }} />
            </Box>
            <Typography variant="h5" fontWeight={700} sx={{ color: '#f9fafb', textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)' }}>
              DDN AI Platform
            </Typography>
          </Box>

          {!success ? (
            <>
              {/* Icon */}
              <Box sx={{ textAlign: 'center', mb: 3 }}>
                <Box
                  sx={{
                    width: 80,
                    height: 80,
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #10b981, #14b8a6)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 2,
                    boxShadow: '0 0 30px rgba(16, 185, 129, 0.6), inset 0 2px 8px rgba(255, 255, 255, 0.15)',
                    border: '2px solid rgba(16, 185, 129, 0.3)'
                  }}
                >
                  <LockResetIcon sx={{ fontSize: 40, color: 'white', filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3))' }} />
                </Box>
                <Typography variant="h5" fontWeight={700} sx={{ color: '#f9fafb', mb: 1, textShadow: '0 2px 8px rgba(0, 0, 0, 0.4)' }}>
                  Forgot Password?
                </Typography>
                <Typography variant="body2" sx={{ color: '#9ca3af', fontSize: '0.95rem', lineHeight: 1.6 }}>
                  No worries! Enter your email address and we'll send you instructions to reset your password.
                </Typography>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
                  {error}
                </Alert>
              )}

              <form onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setError('') }}
                  placeholder="you@company.com"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <EmailIcon sx={{ color: '#10b981' }} />
                      </InputAdornment>
                    )
                  }}
                  sx={{
                    mb: 3,
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      '& fieldset': { borderColor: alpha('#10b981', 0.3) },
                      '&:hover fieldset': { borderColor: '#10b981' },
                      '&.Mui-focused fieldset': { borderColor: '#10b981', borderWidth: '2px' }
                    },
                    '& .MuiInputLabel-root': { color: '#9ca3af' },
                    '& .MuiInputLabel-root.Mui-focused': { color: '#10b981' },
                    '& .MuiInputBase-input': { color: '#f9fafb' }
                  }}
                />

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  disabled={loading}
                  sx={{
                    py: 1.5,
                    borderRadius: 2,
                    background: 'linear-gradient(135deg, #10b981, #14b8a6)',
                    fontSize: '1rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    letterSpacing: '0.3px',
                    boxShadow: '0 4px 20px rgba(16, 185, 129, 0.5)',
                    transition: 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #14b8a6, #10b981)',
                      boxShadow: '0 6px 24px rgba(16, 185, 129, 0.6)',
                      transform: 'translateY(-2px)'
                    }
                  }}
                >
                  {loading ? <CircularProgress size={24} color="inherit" /> : 'Send Reset Link'}
                </Button>
              </form>
            </>
          ) : (
            /* Success State */
            <Fade in timeout={500}>
              <Box sx={{ textAlign: 'center' }}>
                <Box
                  sx={{
                    width: 80,
                    height: 80,
                    borderRadius: '50%',
                    background: alpha('#10b981', 0.15),
                    border: '2px solid rgba(16, 185, 129, 0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 3,
                    boxShadow: '0 0 30px rgba(16, 185, 129, 0.4)'
                  }}
                >
                  <CheckCircleOutlineIcon sx={{ fontSize: 48, color: '#10b981', filter: 'drop-shadow(0 0 8px rgba(16, 185, 129, 0.6))' }} />
                </Box>
                <Typography variant="h5" fontWeight={700} sx={{ color: '#f9fafb', mb: 1, textShadow: '0 2px 8px rgba(0, 0, 0, 0.4)' }}>
                  Check Your Email
                </Typography>
                <Typography variant="body2" sx={{ color: '#9ca3af', mb: 3, fontSize: '0.95rem', lineHeight: 1.6 }}>
                  We've sent a password reset link to <strong style={{ color: '#10b981' }}>{email}</strong>. Please check your inbox and follow the instructions.
                </Typography>
                <Typography variant="caption" display="block" sx={{ mb: 3, color: '#9ca3af' }}>
                  Didn't receive the email? Check your spam folder or{' '}
                  <Link
                    href="#"
                    onClick={(e) => { e.preventDefault(); setSuccess(false) }}
                    sx={{ color: '#10b981', fontWeight: 600, textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
                  >
                    try again
                  </Link>
                </Typography>
                <Button
                  fullWidth
                  variant="contained"
                  onClick={() => navigate('/login')}
                  sx={{
                    py: 1.5,
                    borderRadius: 2,
                    background: 'linear-gradient(135deg, #10b981, #14b8a6)',
                    fontSize: '1rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    letterSpacing: '0.3px',
                    boxShadow: '0 4px 20px rgba(16, 185, 129, 0.5)',
                    transition: 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #14b8a6, #10b981)',
                      boxShadow: '0 6px 24px rgba(16, 185, 129, 0.6)',
                      transform: 'translateY(-2px)'
                    }
                  }}
                >
                  Back to Login
                </Button>
              </Box>
            </Fade>
          )}

          {/* Back to Login */}
          {!success && (
            <Button
              fullWidth
              startIcon={<ArrowBackIcon />}
              onClick={() => navigate('/login')}
              sx={{
                mt: 2,
                color: '#9ca3af',
                textTransform: 'none',
                transition: 'all 0.3s ease',
                '&:hover': {
                  bgcolor: alpha('#10b981', 0.1),
                  color: '#10b981'
                }
              }}
            >
              Back to Login
            </Button>
          )}
        </Paper>
      </Zoom>
    </Box>
  )
}

export default ForgotPasswordPage
