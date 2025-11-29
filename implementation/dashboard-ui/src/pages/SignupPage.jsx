import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Checkbox,
  FormControlLabel,
  Divider,
  IconButton,
  InputAdornment,
  Alert,
  CircularProgress,
  Link,
  Stepper,
  Step,
  StepLabel,
  Grid,
  Chip,
  Avatar,
  Fade,
  Zoom
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import EmailIcon from '@mui/icons-material/Email'
import LockIcon from '@mui/icons-material/Lock'
import PersonIcon from '@mui/icons-material/Person'
import BusinessIcon from '@mui/icons-material/Business'
import GroupsIcon from '@mui/icons-material/Groups'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import GoogleIcon from '@mui/icons-material/Google'
import GitHubIcon from '@mui/icons-material/GitHub'
import { useNavigate, Link as RouterLink } from 'react-router-dom'

// Animated background
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

const steps = ['Account', 'Organization', 'Team']

const plans = [
  { id: 'starter', name: 'Starter', price: 'Free', features: ['5 team members', '100 analyses/month', 'Basic reports'], color: '#64748b' },
  { id: 'pro', name: 'Professional', price: '$49/mo', features: ['25 team members', 'Unlimited analyses', 'Advanced analytics', 'Priority support'], color: '#3b82f6', popular: true },
  { id: 'enterprise', name: 'Enterprise', price: 'Custom', features: ['Unlimited members', 'Custom integrations', 'SLA guarantee', 'Dedicated support'], color: '#8b5cf6' }
]

function SignupPage() {
  const navigate = useNavigate()
  const [activeStep, setActiveStep] = useState(0)
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [formData, setFormData] = useState({
    // Step 1: Account
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false,
    // Step 2: Organization
    companyName: '',
    companySize: '',
    industry: '',
    // Step 3: Team & Plan
    teamName: '',
    selectedPlan: 'pro',
    inviteEmails: ''
  })

  const handleChange = (e) => {
    const { name, value, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: e.target.type === 'checkbox' ? checked : value
    }))
    setError('')
  }

  const validateStep = () => {
    switch (activeStep) {
      case 0:
        if (!formData.firstName || !formData.lastName) {
          setError('Please enter your full name')
          return false
        }
        if (!formData.email || !formData.email.includes('@')) {
          setError('Please enter a valid email address')
          return false
        }
        if (formData.password.length < 8) {
          setError('Password must be at least 8 characters')
          return false
        }
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match')
          return false
        }
        if (!formData.agreeTerms) {
          setError('Please agree to the Terms of Service')
          return false
        }
        return true
      case 1:
        if (!formData.companyName) {
          setError('Please enter your company name')
          return false
        }
        return true
      case 2:
        if (!formData.teamName) {
          setError('Please enter a team name')
          return false
        }
        return true
      default:
        return true
    }
  }

  const handleNext = () => {
    if (validateStep()) {
      if (activeStep === steps.length - 1) {
        handleSubmit()
      } else {
        setActiveStep(prev => prev + 1)
      }
    }
  }

  const handleBack = () => {
    setActiveStep(prev => prev - 1)
    setError('')
  }

  const handleSubmit = async () => {
    setLoading(true)
    await new Promise(resolve => setTimeout(resolve, 2000))

    localStorage.setItem('ddn-user', JSON.stringify({
      email: formData.email,
      name: `${formData.firstName} ${formData.lastName}`,
      company: formData.companyName,
      team: formData.teamName,
      plan: formData.selectedPlan
    }))

    navigate('/dashboard')
  }

  const handleSocialSignup = (provider) => {
    setLoading(true)
    setTimeout(() => {
      setActiveStep(1) // Skip to organization step
      setFormData(prev => ({
        ...prev,
        email: `user@${provider}.com`,
        firstName: 'Demo',
        lastName: 'User'
      }))
      setLoading(false)
    }, 1000)
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        position: 'relative',
        overflow: 'hidden',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)'
      }}
    >
      {/* Background Elements */}
      <FloatingShape delay={0} duration={6} size={100} top="10%" left="5%" color="#3b82f6" />
      <FloatingShape delay={1} duration={8} size={150} top="60%" left="10%" color="#8b5cf6" />
      <FloatingShape delay={2} duration={7} size={80} top="30%" left="85%" color="#06b6d4" />
      <FloatingShape delay={0.5} duration={9} size={120} top="70%" left="80%" color="#10b981" />

      {/* Left Branding Panel */}
      <Box
        sx={{
          flex: 1,
          display: { xs: 'none', lg: 'flex' },
          flexDirection: 'column',
          justifyContent: 'center',
          p: 6,
          position: 'relative',
          zIndex: 1
        }}
      >
        <Fade in timeout={800}>
          <Box>
            {/* Logo */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 4 }}>
              <Box
                sx={{
                  width: 60,
                  height: 60,
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 10px 40px rgba(59, 130, 246, 0.4)'
                }}
              >
                <SmartToyIcon sx={{ fontSize: 32, color: 'white' }} />
              </Box>
              <Box>
                <Typography variant="h4" fontWeight={700} color="white">
                  DDN AI Platform
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                  Intelligent Test Failure Analysis
                </Typography>
              </Box>
            </Box>

            <Typography
              variant="h3"
              fontWeight={700}
              sx={{
                color: 'white',
                mb: 2,
                background: 'linear-gradient(90deg, #fff, #94a3b8)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                lineHeight: 1.3
              }}
            >
              Start Your Journey<br />To Smarter Testing
            </Typography>

            <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.7)', mb: 5, maxWidth: 450 }}>
              Join thousands of teams using AI-powered analysis to reduce debugging time and improve software quality.
            </Typography>

            {/* Stats */}
            <Grid container spacing={3}>
              {[
                { value: '70%', label: 'Faster Debugging' },
                { value: '1M+', label: 'Failures Analyzed' },
                { value: '500+', label: 'Teams Worldwide' }
              ].map((stat, idx) => (
                <Grid item xs={4} key={idx}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      bgcolor: 'rgba(255,255,255,0.1)',
                      backdropFilter: 'blur(10px)',
                      textAlign: 'center'
                    }}
                  >
                    <Typography variant="h4" fontWeight={700} color="white">
                      {stat.value}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                      {stat.label}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        </Fade>
      </Box>

      {/* Right Panel - Signup Form */}
      <Box
        sx={{
          flex: { xs: 1, lg: 0.7 },
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 3,
          position: 'relative',
          zIndex: 1
        }}
      >
        <Zoom in timeout={500}>
          <Paper
            elevation={0}
            sx={{
              width: '100%',
              maxWidth: 520,
              p: 4,
              borderRadius: 4,
              bgcolor: 'white',
              boxShadow: '0 25px 80px rgba(0,0,0,0.3)',
              maxHeight: '90vh',
              overflow: 'auto'
            }}
          >
            {/* Mobile Logo */}
            <Box sx={{ display: { xs: 'flex', lg: 'none' }, alignItems: 'center', gap: 1.5, mb: 3, justifyContent: 'center' }}>
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

            <Typography variant="h5" fontWeight={700} color="#1e293b" gutterBottom>
              Create your account
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
              Get started with your free trial today
            </Typography>

            {/* Stepper */}
            <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>

            {error && (
              <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
                {error}
              </Alert>
            )}

            {/* Step 1: Account Details */}
            {activeStep === 0 && (
              <Box>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="First Name"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleChange}
                      InputProps={{
                        startAdornment: <InputAdornment position="start"><PersonIcon sx={{ color: '#94a3b8' }} /></InputAdornment>
                      }}
                      sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Last Name"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleChange}
                      sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                    />
                  </Grid>
                </Grid>

                <TextField
                  fullWidth
                  label="Email Address"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  sx={{ mt: 2, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start"><EmailIcon sx={{ color: '#94a3b8' }} /></InputAdornment>
                  }}
                />

                <TextField
                  fullWidth
                  label="Password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleChange}
                  sx={{ mt: 2, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start"><LockIcon sx={{ color: '#94a3b8' }} /></InputAdornment>,
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" size="small">
                          {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                />

                <TextField
                  fullWidth
                  label="Confirm Password"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  sx={{ mt: 2, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start"><LockIcon sx={{ color: '#94a3b8' }} /></InputAdornment>
                  }}
                />

                <FormControlLabel
                  control={
                    <Checkbox
                      name="agreeTerms"
                      checked={formData.agreeTerms}
                      onChange={handleChange}
                      sx={{ '&.Mui-checked': { color: '#3b82f6' } }}
                    />
                  }
                  label={
                    <Typography variant="body2" color="textSecondary">
                      I agree to the <Link href="#" sx={{ color: '#3b82f6' }}>Terms of Service</Link> and <Link href="#" sx={{ color: '#3b82f6' }}>Privacy Policy</Link>
                    </Typography>
                  }
                  sx={{ mt: 2 }}
                />

                <Divider sx={{ my: 3 }}>
                  <Typography variant="caption" color="textSecondary">Or sign up with</Typography>
                </Divider>

                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<GoogleIcon />}
                    onClick={() => handleSocialSignup('google')}
                    sx={{ py: 1.2, borderRadius: 2, borderColor: '#e2e8f0', color: '#64748b', textTransform: 'none' }}
                  >
                    Google
                  </Button>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<GitHubIcon />}
                    onClick={() => handleSocialSignup('github')}
                    sx={{ py: 1.2, borderRadius: 2, borderColor: '#e2e8f0', color: '#64748b', textTransform: 'none' }}
                  >
                    GitHub
                  </Button>
                </Box>
              </Box>
            )}

            {/* Step 2: Organization */}
            {activeStep === 1 && (
              <Box>
                <TextField
                  fullWidth
                  label="Company Name"
                  name="companyName"
                  value={formData.companyName}
                  onChange={handleChange}
                  sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start"><BusinessIcon sx={{ color: '#94a3b8' }} /></InputAdornment>
                  }}
                />

                <TextField
                  fullWidth
                  select
                  label="Company Size"
                  name="companySize"
                  value={formData.companySize}
                  onChange={handleChange}
                  sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  SelectProps={{ native: true }}
                >
                  <option value="">Select size</option>
                  <option value="1-10">1-10 employees</option>
                  <option value="11-50">11-50 employees</option>
                  <option value="51-200">51-200 employees</option>
                  <option value="201-500">201-500 employees</option>
                  <option value="500+">500+ employees</option>
                </TextField>

                <TextField
                  fullWidth
                  select
                  label="Industry"
                  name="industry"
                  value={formData.industry}
                  onChange={handleChange}
                  sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  SelectProps={{ native: true }}
                >
                  <option value="">Select industry</option>
                  <option value="technology">Technology</option>
                  <option value="finance">Finance</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="retail">Retail</option>
                  <option value="manufacturing">Manufacturing</option>
                  <option value="other">Other</option>
                </TextField>
              </Box>
            )}

            {/* Step 3: Team & Plan */}
            {activeStep === 2 && (
              <Box>
                <TextField
                  fullWidth
                  label="Team Name"
                  name="teamName"
                  value={formData.teamName}
                  onChange={handleChange}
                  placeholder="e.g., QA Team, Platform Engineering"
                  sx={{ mb: 3, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start"><GroupsIcon sx={{ color: '#94a3b8' }} /></InputAdornment>
                  }}
                />

                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 2 }}>
                  Choose your plan
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, mb: 3 }}>
                  {plans.map((plan) => (
                    <Paper
                      key={plan.id}
                      elevation={0}
                      onClick={() => setFormData(prev => ({ ...prev, selectedPlan: plan.id }))}
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        border: '2px solid',
                        borderColor: formData.selectedPlan === plan.id ? plan.color : '#e2e8f0',
                        cursor: 'pointer',
                        position: 'relative',
                        transition: 'all 0.2s ease',
                        '&:hover': { borderColor: plan.color }
                      }}
                    >
                      {plan.popular && (
                        <Chip
                          label="Popular"
                          size="small"
                          sx={{
                            position: 'absolute',
                            top: -10,
                            right: 16,
                            bgcolor: plan.color,
                            color: 'white',
                            fontSize: '0.65rem',
                            fontWeight: 600
                          }}
                        />
                      )}
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box>
                          <Typography variant="subtitle1" fontWeight={600}>{plan.name}</Typography>
                          <Typography variant="body2" color="textSecondary">{plan.features[0]}</Typography>
                        </Box>
                        <Box sx={{ textAlign: 'right' }}>
                          <Typography variant="h6" fontWeight={700} color={plan.color}>{plan.price}</Typography>
                          {formData.selectedPlan === plan.id && (
                            <CheckCircleIcon sx={{ color: plan.color, fontSize: 20 }} />
                          )}
                        </Box>
                      </Box>
                    </Paper>
                  ))}
                </Box>

                <TextField
                  fullWidth
                  label="Invite Team Members (optional)"
                  name="inviteEmails"
                  value={formData.inviteEmails}
                  onChange={handleChange}
                  placeholder="email1@company.com, email2@company.com"
                  multiline
                  rows={2}
                  helperText="Separate multiple emails with commas"
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                />
              </Box>
            )}

            {/* Navigation Buttons */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
              <Button
                disabled={activeStep === 0}
                onClick={handleBack}
                startIcon={<ArrowBackIcon />}
                sx={{ borderRadius: 2, textTransform: 'none' }}
              >
                Back
              </Button>
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={loading}
                endIcon={activeStep === steps.length - 1 ? null : <ArrowForwardIcon />}
                sx={{
                  py: 1.2,
                  px: 4,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                  textTransform: 'none',
                  fontWeight: 600
                }}
              >
                {loading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : activeStep === steps.length - 1 ? (
                  'Create Account'
                ) : (
                  'Continue'
                )}
              </Button>
            </Box>

            {/* Login Link */}
            <Typography variant="body2" color="textSecondary" sx={{ mt: 3, textAlign: 'center' }}>
              Already have an account?{' '}
              <Link
                component={RouterLink}
                to="/login"
                underline="hover"
                sx={{ color: '#3b82f6', fontWeight: 600 }}
              >
                Sign in
              </Link>
            </Typography>
          </Paper>
        </Zoom>
      </Box>
    </Box>
  )
}

export default SignupPage
