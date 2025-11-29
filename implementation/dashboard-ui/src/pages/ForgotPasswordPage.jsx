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
      <FloatingShape delay={0} duration={6} size={100} top="10%" left="15%" color="#3b82f6" />
      <FloatingShape delay={1} duration={8} size={150} top="60%" left="10%" color="#8b5cf6" />
      <FloatingShape delay={2} duration={7} size={80} top="20%" left="80%" color="#06b6d4" />
      <FloatingShape delay={0.5} duration={9} size={120} top="70%" left="75%" color="#10b981" />

      <Zoom in timeout={500}>
        <Paper
          elevation={0}
          sx={{
            width: '100%',
            maxWidth: 440,
            p: 4,
            borderRadius: 4,
            bgcolor: 'white',
            boxShadow: '0 25px 80px rgba(0,0,0,0.3)',
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
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <SmartToyIcon sx={{ color: 'white' }} />
            </Box>
            <Typography variant="h5" fontWeight={700} color="#1e293b">
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
                    background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 2
                  }}
                >
                  <LockResetIcon sx={{ fontSize: 40, color: 'white' }} />
                </Box>
                <Typography variant="h5" fontWeight={700} color="#1e293b" gutterBottom>
                  Forgot Password?
                </Typography>
                <Typography variant="body2" color="textSecondary">
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
                        <EmailIcon sx={{ color: '#94a3b8' }} />
                      </InputAdornment>
                    )
                  }}
                  sx={{
                    mb: 3,
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      '&:hover fieldset': { borderColor: '#3b82f6' },
                      '&.Mui-focused fieldset': { borderColor: '#3b82f6' }
                    }
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
                    background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                    fontSize: '1rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    boxShadow: '0 4px 15px rgba(59, 130, 246, 0.4)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #2563eb, #7c3aed)',
                      boxShadow: '0 6px 20px rgba(59, 130, 246, 0.5)'
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
                    bgcolor: '#dcfce7',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 3
                  }}
                >
                  <CheckCircleOutlineIcon sx={{ fontSize: 48, color: '#10b981' }} />
                </Box>
                <Typography variant="h5" fontWeight={700} color="#1e293b" gutterBottom>
                  Check Your Email
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                  We've sent a password reset link to <strong>{email}</strong>. Please check your inbox and follow the instructions.
                </Typography>
                <Typography variant="caption" color="textSecondary" display="block" sx={{ mb: 3 }}>
                  Didn't receive the email? Check your spam folder or{' '}
                  <Link
                    href="#"
                    onClick={(e) => { e.preventDefault(); setSuccess(false) }}
                    sx={{ color: '#3b82f6', fontWeight: 600 }}
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
                    background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                    fontSize: '1rem',
                    fontWeight: 600,
                    textTransform: 'none'
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
                color: '#64748b',
                textTransform: 'none',
                '&:hover': { bgcolor: '#f8fafc' }
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
