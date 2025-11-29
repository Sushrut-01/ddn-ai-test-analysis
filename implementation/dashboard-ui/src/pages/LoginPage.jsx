import React, { useState, useEffect } from 'react'
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
  Chip,
  Tooltip,
  Fade,
  Zoom,
  Slide,
  LinearProgress
} from '@mui/material'
import { alpha, keyframes } from '@mui/material/styles'
import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import EmailIcon from '@mui/icons-material/Email'
import LockIcon from '@mui/icons-material/Lock'
import GoogleIcon from '@mui/icons-material/Google'
import GitHubIcon from '@mui/icons-material/GitHub'
import BusinessIcon from '@mui/icons-material/Business'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import SecurityIcon from '@mui/icons-material/Security'
import SpeedIcon from '@mui/icons-material/Speed'
import BugReportIcon from '@mui/icons-material/BugReport'
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh'
import FingerprintIcon from '@mui/icons-material/Fingerprint'
import MicIcon from '@mui/icons-material/Mic'
import MicOffIcon from '@mui/icons-material/MicOff'
import FaceIcon from '@mui/icons-material/Face'
import GraphicEqIcon from '@mui/icons-material/GraphicEq'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import WavesIcon from '@mui/icons-material/Waves'
import RadarIcon from '@mui/icons-material/Radar'
import MemoryIcon from '@mui/icons-material/Memory'
import { useNavigate, Link as RouterLink } from 'react-router-dom'
import PaletteIcon from '@mui/icons-material/Palette'

// JARVIS Theme Definitions
const jarvisThemes = {
  cyan: {
    name: 'Cyber Cyan',
    primary: '#00d4ff',
    secondary: '#0891b2',
    accent: '#06b6d4',
    gradient: 'linear-gradient(135deg, #0a0f1a 0%, #1a1f2e 50%, #0a0f1a 100%)',
    cardBg: 'rgba(0, 212, 255, 0.03)',
    cardBorder: 'rgba(0, 212, 255, 0.15)',
    glow: 'rgba(0, 212, 255, 0.5)',
    icon: 'SmartToy'
  },
  ironman: {
    name: 'Iron Man',
    primary: '#ff4444',
    secondary: '#ffd700',
    accent: '#ff6b35',
    gradient: 'linear-gradient(135deg, #1a0a0a 0%, #2d1515 50%, #1a0a0a 100%)',
    cardBg: 'rgba(255, 68, 68, 0.03)',
    cardBorder: 'rgba(255, 68, 68, 0.15)',
    glow: 'rgba(255, 68, 68, 0.5)',
    icon: 'Shield'
  },
  matrix: {
    name: 'Matrix',
    primary: '#00ff41',
    secondary: '#008f11',
    accent: '#00ff41',
    gradient: 'linear-gradient(135deg, #0a0f0a 0%, #0d1a0d 50%, #0a0f0a 100%)',
    cardBg: 'rgba(0, 255, 65, 0.03)',
    cardBorder: 'rgba(0, 255, 65, 0.15)',
    glow: 'rgba(0, 255, 65, 0.5)',
    icon: 'Code'
  },
  purple: {
    name: 'Cyberpunk',
    primary: '#bf00ff',
    secondary: '#8b5cf6',
    accent: '#d946ef',
    gradient: 'linear-gradient(135deg, #0f0a1a 0%, #1a0f2e 50%, #0f0a1a 100%)',
    cardBg: 'rgba(191, 0, 255, 0.03)',
    cardBorder: 'rgba(191, 0, 255, 0.15)',
    glow: 'rgba(191, 0, 255, 0.5)',
    icon: 'Bolt'
  },
  ember: {
    name: 'Ember',
    primary: '#ff6b35',
    secondary: '#f59e0b',
    accent: '#fb923c',
    gradient: 'linear-gradient(135deg, #1a0f0a 0%, #2e1a0f 50%, #1a0f0a 100%)',
    cardBg: 'rgba(255, 107, 53, 0.03)',
    cardBorder: 'rgba(255, 107, 53, 0.15)',
    glow: 'rgba(255, 107, 53, 0.5)',
    icon: 'Whatshot'
  },
  arctic: {
    name: 'Arctic',
    primary: '#60a5fa',
    secondary: '#3b82f6',
    accent: '#93c5fd',
    gradient: 'linear-gradient(135deg, #0a0f1a 0%, #0f1a2e 50%, #0a0f1a 100%)',
    cardBg: 'rgba(96, 165, 250, 0.03)',
    cardBorder: 'rgba(96, 165, 250, 0.15)',
    glow: 'rgba(96, 165, 250, 0.5)',
    icon: 'AcUnit'
  },
  gold: {
    name: 'Gold Elite',
    primary: '#ffd700',
    secondary: '#f59e0b',
    accent: '#fbbf24',
    gradient: 'linear-gradient(135deg, #1a150a 0%, #2e250f 50%, #1a150a 100%)',
    cardBg: 'rgba(255, 215, 0, 0.03)',
    cardBorder: 'rgba(255, 215, 0, 0.15)',
    glow: 'rgba(255, 215, 0, 0.5)',
    icon: 'Diamond'
  },
  neon: {
    name: 'Neon Pink',
    primary: '#ff0080',
    secondary: '#ff00ff',
    accent: '#ff1493',
    gradient: 'linear-gradient(135deg, #1a0a12 0%, #2e0f1a 50%, #1a0a12 100%)',
    cardBg: 'rgba(255, 0, 128, 0.03)',
    cardBorder: 'rgba(255, 0, 128, 0.15)',
    glow: 'rgba(255, 0, 128, 0.5)',
    icon: 'Favorite'
  }
}

// Keyframe animations
const pulse = keyframes`
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.8; }
`

const rotate = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`

const scanLine = keyframes`
  0% { top: 0%; }
  100% { top: 100%; }
`

const wave = keyframes`
  0%, 100% { transform: scaleY(0.5); }
  50% { transform: scaleY(1.5); }
`

const glow = keyframes`
  0%, 100% { box-shadow: 0 0 5px #00d4ff, 0 0 10px #00d4ff, 0 0 15px #00d4ff; }
  50% { box-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff, 0 0 30px #00d4ff, 0 0 40px #00d4ff; }
`

const typewriter = keyframes`
  from { width: 0; }
  to { width: 100%; }
`

// Floating shapes with circuit pattern
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

// Circuit lines background
const CircuitBackground = ({ theme }) => (
  <Box
    sx={{
      position: 'absolute',
      inset: 0,
      opacity: 0.1,
      background: `
        linear-gradient(90deg, transparent 98%, ${theme?.primary || '#00d4ff'} 98%),
        linear-gradient(0deg, transparent 98%, ${theme?.primary || '#00d4ff'} 98%)
      `,
      backgroundSize: '50px 50px',
      animation: `${pulse} 4s ease-in-out infinite`
    }}
  />
)

// AI Voice Waveform
const VoiceWaveform = ({ active, theme }) => (
  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, height: 40 }}>
    {[...Array(12)].map((_, i) => (
      <Box
        key={i}
        sx={{
          width: 3,
          height: active ? `${Math.random() * 30 + 10}px` : 4,
          bgcolor: active ? (theme?.primary || '#00d4ff') : '#64748b',
          borderRadius: 2,
          transition: 'all 0.1s ease',
          animation: active ? `${wave} ${0.3 + Math.random() * 0.3}s ease-in-out infinite` : 'none',
          animationDelay: `${i * 0.05}s`
        }}
      />
    ))}
  </Box>
)

// AI Core Animation
const AICore = ({ speaking, theme }) => {
  const t = theme || { primary: '#00d4ff', secondary: '#0891b2', accent: '#06b6d4', glow: 'rgba(0, 212, 255, 0.5)' }
  return (
    <Box
      sx={{
        position: 'relative',
        width: 120,
        height: 120,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
    >
      {/* Outer ring */}
      <Box
        sx={{
          position: 'absolute',
          width: 120,
          height: 120,
          borderRadius: '50%',
          border: '2px solid',
          borderColor: speaking ? t.primary : t.secondary,
          animation: `${rotate} 10s linear infinite`,
          '&::before': {
            content: '""',
            position: 'absolute',
            top: -4,
            left: '50%',
            width: 8,
            height: 8,
            borderRadius: '50%',
            bgcolor: t.primary,
            boxShadow: `0 0 10px ${t.primary}`
          }
        }}
      />
      {/* Middle ring */}
      <Box
        sx={{
          position: 'absolute',
          width: 90,
          height: 90,
          borderRadius: '50%',
          border: '2px dashed',
          borderColor: alpha(t.primary, 0.5),
          animation: `${rotate} 8s linear infinite reverse`
        }}
      />
      {/* Inner core */}
      <Box
        sx={{
          width: 60,
          height: 60,
          borderRadius: '50%',
          background: `linear-gradient(135deg, ${t.secondary}, ${t.primary}, ${t.accent})`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          animation: speaking ? `${pulse} 0.5s ease-in-out infinite` : `${pulse} 2s ease-in-out infinite`,
          boxShadow: `0 0 30px ${t.glow}`
        }}
      >
        <SmartToyIcon sx={{ fontSize: 32, color: 'white' }} />
      </Box>
    </Box>
  )
}

// Face scan animation
const FaceScanOverlay = ({ active, theme }) => {
  const themeColor = theme?.primary || '#00d4ff'
  return (
    <Box
      sx={{
        position: 'absolute',
        inset: 0,
        borderRadius: 3,
        overflow: 'hidden',
        opacity: active ? 1 : 0,
        transition: 'opacity 0.3s ease'
      }}
    >
      {/* Scan line */}
      <Box
        sx={{
          position: 'absolute',
          left: 0,
          right: 0,
          height: 2,
          background: `linear-gradient(90deg, transparent, ${themeColor}, transparent)`,
          animation: active ? `${scanLine} 2s linear infinite` : 'none',
          boxShadow: `0 0 20px ${themeColor}`
        }}
      />
      {/* Corner brackets */}
      {['top-left', 'top-right', 'bottom-left', 'bottom-right'].map((pos) => (
        <Box
          key={pos}
          sx={{
            position: 'absolute',
            width: 20,
            height: 20,
            borderColor: themeColor,
            borderStyle: 'solid',
            borderWidth: 0,
            ...(pos.includes('top') && { top: 10, borderTopWidth: 2 }),
            ...(pos.includes('bottom') && { bottom: 10, borderBottomWidth: 2 }),
            ...(pos.includes('left') && { left: 10, borderLeftWidth: 2 }),
            ...(pos.includes('right') && { right: 10, borderRightWidth: 2 })
          }}
        />
      ))}
    </Box>
  )
}

// JARVIS Messages
const jarvisGreetings = [
  "Good to see you. I'm ready to assist.",
  "Welcome back. All systems operational.",
  "Hello! Security protocols initialized.",
  "Greetings. Ready for authentication.",
  "Systems online. Awaiting your credentials."
]

const jarvisResponses = {
  typing: "Analyzing input patterns...",
  email: "Email format validated.",
  password: "Encryption protocols active.",
  authenticating: "Initiating secure handshake...",
  success: "Authentication successful. Welcome aboard!",
  error: "Access denied. Please verify credentials.",
  voice: "Voice recognition activated. Please speak your passphrase.",
  face: "Facial recognition initiated. Please look at the camera.",
  fingerprint: "Biometric scanner ready. Place your finger on the sensor."
}

function LoginPage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [loginMethod, setLoginMethod] = useState('email')

  // JARVIS states
  const [jarvisMessage, setJarvisMessage] = useState('')
  const [jarvisSpeaking, setJarvisSpeaking] = useState(false)
  const [voiceActive, setVoiceActive] = useState(false)
  const [faceScanning, setFaceScanning] = useState(false)
  const [fingerprintScanning, setFingerprintScanning] = useState(false)
  const [authProgress, setAuthProgress] = useState(0)
  const [showThemeSelector, setShowThemeSelector] = useState(false)

  // JARVIS Theme state
  const [currentJarvisTheme, setCurrentJarvisTheme] = useState(() => {
    const saved = localStorage.getItem('jarvis-theme')
    return saved || 'cyan'
  })
  const jTheme = jarvisThemes[currentJarvisTheme]

  const handleThemeChange = (themeKey) => {
    setCurrentJarvisTheme(themeKey)
    localStorage.setItem('jarvis-theme', themeKey)
    typeMessage(`Theme changed to ${jarvisThemes[themeKey].name}. Visual systems updated.`)
  }

  // Initialize JARVIS greeting
  useEffect(() => {
    const greeting = jarvisGreetings[Math.floor(Math.random() * jarvisGreetings.length)]
    typeMessage(greeting)
  }, [])

  const typeMessage = (message) => {
    setJarvisSpeaking(true)
    setJarvisMessage('')
    let i = 0
    const interval = setInterval(() => {
      if (i < message.length) {
        setJarvisMessage(prev => prev + message[i])
        i++
      } else {
        clearInterval(interval)
        setJarvisSpeaking(false)
      }
    }, 30)
  }

  const handleChange = (e) => {
    const { name, value, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'rememberMe' ? checked : value
    }))
    setError('')

    // JARVIS feedback
    if (name === 'email' && value.includes('@')) {
      typeMessage(jarvisResponses.email)
    } else if (name === 'password' && value.length > 0) {
      typeMessage(jarvisResponses.password)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    typeMessage(jarvisResponses.authenticating)

    // Animate progress
    const progressInterval = setInterval(() => {
      setAuthProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval)
          return 100
        }
        return prev + 10
      })
    }, 150)

    await new Promise(resolve => setTimeout(resolve, 2000))

    if (formData.email && formData.password) {
      typeMessage(jarvisResponses.success)
      await new Promise(resolve => setTimeout(resolve, 1000))
      localStorage.setItem('ddn-user', JSON.stringify({
        email: formData.email,
        name: formData.email.split('@')[0],
        loginTime: new Date().toISOString()
      }))
      navigate('/dashboard')
    } else {
      typeMessage(jarvisResponses.error)
      setError('Please enter valid credentials')
    }
    setLoading(false)
    setAuthProgress(0)
  }

  const handleVoiceLogin = () => {
    setVoiceActive(true)
    typeMessage(jarvisResponses.voice)

    setTimeout(() => {
      setVoiceActive(false)
      typeMessage("Voice pattern recognized. Authenticating...")
      setLoading(true)

      setTimeout(() => {
        localStorage.setItem('ddn-user', JSON.stringify({
          email: 'voice@ddn.com',
          name: 'Voice User',
          loginTime: new Date().toISOString()
        }))
        navigate('/dashboard')
      }, 1500)
    }, 3000)
  }

  const handleFaceLogin = () => {
    setFaceScanning(true)
    typeMessage(jarvisResponses.face)

    setTimeout(() => {
      setFaceScanning(false)
      typeMessage("Facial features matched. Access granted.")
      setLoading(true)

      setTimeout(() => {
        localStorage.setItem('ddn-user', JSON.stringify({
          email: 'face@ddn.com',
          name: 'Face ID User',
          loginTime: new Date().toISOString()
        }))
        navigate('/dashboard')
      }, 1500)
    }, 3000)
  }

  const handleFingerprintLogin = () => {
    setFingerprintScanning(true)
    typeMessage(jarvisResponses.fingerprint)

    setTimeout(() => {
      setFingerprintScanning(false)
      typeMessage("Biometric verification complete. Welcome!")
      setLoading(true)

      setTimeout(() => {
        localStorage.setItem('ddn-user', JSON.stringify({
          email: 'biometric@ddn.com',
          name: 'Biometric User',
          loginTime: new Date().toISOString()
        }))
        navigate('/dashboard')
      }, 1500)
    }, 2500)
  }

  const handleSocialLogin = (provider) => {
    typeMessage(`Connecting to ${provider} secure servers...`)
    setLoading(true)
    setTimeout(() => {
      localStorage.setItem('ddn-user', JSON.stringify({
        email: `user@${provider}.com`,
        name: `${provider} User`,
        loginTime: new Date().toISOString()
      }))
      navigate('/dashboard')
    }, 1500)
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        position: 'relative',
        overflow: 'hidden',
        background: jTheme.gradient,
        transition: 'background 0.5s ease'
      }}
    >
      {/* Theme Selector Button */}
      <Tooltip title="Change JARVIS Theme">
        <IconButton
          onClick={() => setShowThemeSelector(!showThemeSelector)}
          sx={{
            position: 'fixed',
            top: 20,
            right: 20,
            zIndex: 1000,
            bgcolor: alpha(jTheme.primary, 0.1),
            border: '1px solid',
            borderColor: alpha(jTheme.primary, 0.3),
            color: jTheme.primary,
            backdropFilter: 'blur(10px)',
            '&:hover': {
              bgcolor: alpha(jTheme.primary, 0.2),
              transform: 'rotate(15deg)'
            },
            transition: 'all 0.3s ease'
          }}
        >
          <PaletteIcon />
        </IconButton>
      </Tooltip>

      {/* Theme Selector Panel */}
      <Zoom in={showThemeSelector}>
        <Paper
          elevation={0}
          sx={{
            position: 'fixed',
            top: 70,
            right: 20,
            zIndex: 1000,
            p: 2,
            borderRadius: 3,
            bgcolor: alpha('#0a0f1a', 0.95),
            backdropFilter: 'blur(20px)',
            border: '1px solid',
            borderColor: alpha(jTheme.primary, 0.3),
            boxShadow: `0 20px 40px rgba(0,0,0,0.4), 0 0 20px ${jTheme.glow}`,
            display: showThemeSelector ? 'block' : 'none',
            minWidth: 280
          }}
        >
          <Typography variant="subtitle2" sx={{ color: jTheme.primary, mb: 2, fontWeight: 600, letterSpacing: 1 }}>
            SELECT JARVIS THEME
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 1.5 }}>
            {Object.entries(jarvisThemes).map(([key, theme]) => (
              <Box
                key={key}
                onClick={() => { handleThemeChange(key); setShowThemeSelector(false) }}
                sx={{
                  p: 1.5,
                  borderRadius: 2,
                  bgcolor: currentJarvisTheme === key ? alpha(theme.primary, 0.15) : alpha(theme.primary, 0.05),
                  border: '2px solid',
                  borderColor: currentJarvisTheme === key ? theme.primary : 'transparent',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    bgcolor: alpha(theme.primary, 0.1),
                    borderColor: alpha(theme.primary, 0.5),
                    transform: 'translateY(-2px)'
                  }
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box
                    sx={{
                      width: 24,
                      height: 24,
                      borderRadius: '50%',
                      background: `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})`,
                      boxShadow: `0 0 10px ${theme.glow}`
                    }}
                  />
                  <Typography variant="caption" sx={{ color: theme.primary, fontWeight: 600 }}>
                    {theme.name}
                  </Typography>
                </Box>
              </Box>
            ))}
          </Box>
          <Typography variant="caption" sx={{ color: '#64748b', mt: 2, display: 'block', textAlign: 'center' }}>
            Theme persists across sessions
          </Typography>
        </Paper>
      </Zoom>

      <CircuitBackground theme={jTheme} />

      {/* Animated Background Elements */}
      <FloatingShape delay={0} duration={6} size={100} top="10%" left="5%" color={jTheme.primary} />
      <FloatingShape delay={1} duration={8} size={150} top="60%" left="10%" color={jTheme.secondary} />
      <FloatingShape delay={2} duration={7} size={80} top="30%" left="80%" color={jTheme.primary} />
      <FloatingShape delay={0.5} duration={9} size={120} top="70%" left="75%" color={jTheme.accent} />

      {/* Left Panel - JARVIS Interface */}
      <Box
        sx={{
          flex: 1,
          display: { xs: 'none', lg: 'flex' },
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          p: 6,
          position: 'relative',
          zIndex: 1
        }}
      >
        <Fade in timeout={800}>
          <Box sx={{ textAlign: 'center', maxWidth: 550 }}>
            {/* AI Core */}
            <Box sx={{ mb: 3 }}>
              <AICore speaking={jarvisSpeaking} theme={jTheme} />
            </Box>

            {/* JARVIS Title */}
            <Typography
              variant="h3"
              fontWeight={700}
              sx={{
                color: jTheme.primary,
                mb: 0.5,
                textShadow: `0 0 20px ${jTheme.glow}`,
                letterSpacing: 8,
                transition: 'all 0.3s ease'
              }}
            >
              D.D.N. AI
            </Typography>
            <Typography
              variant="body2"
              sx={{ color: 'rgba(255,255,255,0.5)', mb: 1, letterSpacing: 4 }}
            >
              DIGITAL DEFENSE NETWORK
            </Typography>
            <Typography
              variant="caption"
              sx={{ color: jTheme.primary, letterSpacing: 2, display: 'block', mb: 3, transition: 'color 0.3s ease' }}
            >
              v2.0.1 | Enterprise Edition
            </Typography>

            {/* JARVIS Message Box */}
            <Paper
              elevation={0}
              sx={{
                p: 2.5,
                borderRadius: 2,
                bgcolor: jTheme.cardBg,
                border: '1px solid',
                borderColor: jTheme.cardBorder,
                minHeight: 70,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 3,
                transition: 'all 0.3s ease'
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {jarvisSpeaking && (
                  <GraphicEqIcon sx={{ color: jTheme.primary, animation: `${pulse} 0.5s ease-in-out infinite` }} />
                )}
                <Typography
                  sx={{
                    color: jTheme.primary,
                    fontFamily: 'monospace',
                    fontSize: '0.9rem',
                    textShadow: `0 0 10px ${alpha(jTheme.primary, 0.3)}`,
                    transition: 'color 0.3s ease'
                  }}
                >
                  {jarvisMessage}
                  {jarvisSpeaking && <span style={{ animation: 'blink 1s infinite' }}>|</span>}
                </Typography>
              </Box>
            </Paper>

            {/* Product Info Cards */}
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2, mb: 3 }}>
              {[
                { icon: <BugReportIcon />, value: '10K+', label: 'Failures Analyzed', color: '#ef4444' },
                { icon: <AutoFixHighIcon />, value: '95%', label: 'AI Accuracy', color: '#10b981' },
                { icon: <SpeedIcon />, value: '70%', label: 'Faster Debug', color: '#f59e0b' },
                { icon: <SecurityIcon />, value: '256-bit', label: 'Encryption', color: '#8b5cf6' }
              ].map((stat, idx) => (
                <Box
                  key={idx}
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    bgcolor: jTheme.cardBg,
                    border: '1px solid',
                    borderColor: jTheme.cardBorder,
                    textAlign: 'center',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      bgcolor: alpha(jTheme.primary, 0.08),
                      borderColor: alpha(jTheme.primary, 0.4),
                      transform: 'translateY(-2px)'
                    }
                  }}
                >
                  {React.cloneElement(stat.icon, { sx: { color: stat.color, fontSize: 24, mb: 0.5 } })}
                  <Typography variant="h6" fontWeight={700} sx={{ color: 'white' }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#94a3b8' }}>
                    {stat.label}
                  </Typography>
                </Box>
              ))}
            </Box>

            {/* Key Features */}
            <Box sx={{ textAlign: 'left', mb: 3 }}>
              <Typography variant="overline" sx={{ color: jTheme.primary, letterSpacing: 2, mb: 1, display: 'block', transition: 'color 0.3s ease' }}>
                Platform Capabilities
              </Typography>
              {[
                'AI-Powered Root Cause Analysis',
                'Automated Jira Bug Creation',
                'Real-time Pipeline Monitoring',
                'Human-in-the-Loop Validation',
                'Multi-LLM Support (GPT-4, Claude, Gemini)'
              ].map((feature, idx) => (
                <Box
                  key={idx}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    py: 0.5,
                    color: 'rgba(255,255,255,0.8)',
                    fontSize: '0.85rem'
                  }}
                >
                  <Box
                    sx={{
                      width: 6,
                      height: 6,
                      borderRadius: '50%',
                      bgcolor: jTheme.primary,
                      boxShadow: `0 0 6px ${jTheme.primary}`,
                      transition: 'all 0.3s ease'
                    }}
                  />
                  {feature}
                </Box>
              ))}
            </Box>

            {/* Status Indicators */}
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3 }}>
              {[
                { icon: <VerifiedUserIcon />, label: 'Secure', active: true },
                { icon: <MemoryIcon />, label: 'AI Ready', active: true },
                { icon: <RadarIcon />, label: 'Scanning', active: loading }
              ].map((item, idx) => (
                <Box key={idx} sx={{ textAlign: 'center' }}>
                  <Box
                    sx={{
                      width: 44,
                      height: 44,
                      borderRadius: '50%',
                      bgcolor: alpha(item.active ? jTheme.primary : '#64748b', 0.1),
                      border: '1px solid',
                      borderColor: item.active ? jTheme.primary : '#64748b',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 0.5,
                      animation: item.active ? `${pulse} 2s ease-in-out infinite` : 'none',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    {React.cloneElement(item.icon, {
                      sx: { color: item.active ? jTheme.primary : '#64748b', fontSize: 20, transition: 'color 0.3s ease' }
                    })}
                  </Box>
                  <Typography variant="caption" sx={{ color: item.active ? jTheme.primary : '#64748b', fontSize: '0.7rem', transition: 'color 0.3s ease' }}>
                    {item.label}
                  </Typography>
                </Box>
              ))}
            </Box>

            {/* Voice Waveform */}
            {voiceActive && (
              <Box sx={{ mt: 3 }}>
                <VoiceWaveform active={voiceActive} theme={jTheme} />
                <Typography variant="caption" sx={{ color: jTheme.primary, mt: 1, display: 'block', transition: 'color 0.3s ease' }}>
                  Listening...
                </Typography>
              </Box>
            )}

            {/* Footer */}
            <Typography
              variant="caption"
              sx={{ color: 'rgba(255,255,255,0.3)', mt: 3, display: 'block' }}
            >
              Powered by Advanced AI • Enterprise Security • 24/7 Support
            </Typography>
          </Box>
        </Fade>
      </Box>

      {/* Right Panel - Login Form */}
      <Box
        sx={{
          flex: { xs: 1, lg: 0.6 },
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 3,
          position: 'relative',
          zIndex: 1
        }}
      >
        <FaceScanOverlay active={faceScanning} theme={jTheme} />

        <Zoom in timeout={500}>
          <Paper
            elevation={0}
            sx={{
              width: '100%',
              maxWidth: 440,
              p: 4,
              borderRadius: 3,
              bgcolor: alpha('#1e293b', 0.9),
              backdropFilter: 'blur(20px)',
              border: '1px solid',
              borderColor: alpha(jTheme.primary, 0.2),
              boxShadow: `0 25px 80px rgba(0,0,0,0.5), 0 0 40px ${alpha(jTheme.primary, 0.1)}`,
              transition: 'all 0.3s ease'
            }}
          >
            {/* Mobile Logo */}
            <Box sx={{ display: { xs: 'flex', lg: 'none' }, alignItems: 'center', gap: 1.5, mb: 3, justifyContent: 'center' }}>
              <Box
                sx={{
                  width: 44,
                  height: 44,
                  borderRadius: 2,
                  background: `linear-gradient(135deg, ${jTheme.primary}, ${jTheme.secondary})`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'background 0.3s ease'
                }}
              >
                <SmartToyIcon sx={{ color: 'white' }} />
              </Box>
              <Typography variant="h5" fontWeight={700} sx={{ color: jTheme.primary, transition: 'color 0.3s ease' }}>
                DDN AI
              </Typography>
            </Box>

            <Typography variant="h5" fontWeight={700} sx={{ color: 'white' }} gutterBottom>
              Secure Access
            </Typography>
            <Typography variant="body2" sx={{ color: '#94a3b8', mb: 3 }}>
              Multiple authentication methods available
            </Typography>

            {/* Auth Progress */}
            {loading && (
              <Box sx={{ mb: 2 }}>
                <LinearProgress
                  variant="determinate"
                  value={authProgress}
                  sx={{
                    height: 4,
                    borderRadius: 2,
                    bgcolor: alpha(jTheme.primary, 0.1),
                    '& .MuiLinearProgress-bar': {
                      bgcolor: jTheme.primary,
                      boxShadow: `0 0 10px ${jTheme.primary}`
                    }
                  }}
                />
              </Box>
            )}

            {error && (
              <Alert
                severity="error"
                sx={{
                  mb: 2,
                  borderRadius: 2,
                  bgcolor: alpha('#ef4444', 0.1),
                  color: '#ef4444',
                  border: '1px solid',
                  borderColor: alpha('#ef4444', 0.3)
                }}
              >
                {error}
              </Alert>
            )}

            {/* Advanced Biometric Options */}
            <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
              {[
                { id: 'email', label: 'Credentials', icon: <EmailIcon sx={{ fontSize: 16 }} /> },
                { id: 'voice', label: 'Voice', icon: <MicIcon sx={{ fontSize: 16 }} /> },
                { id: 'face', label: 'Face ID', icon: <FaceIcon sx={{ fontSize: 16 }} /> },
                { id: 'fingerprint', label: 'Biometric', icon: <FingerprintIcon sx={{ fontSize: 16 }} /> }
              ].map((method) => (
                <Chip
                  key={method.id}
                  label={method.label}
                  icon={method.icon}
                  onClick={() => setLoginMethod(method.id)}
                  sx={{
                    bgcolor: loginMethod === method.id ? alpha(jTheme.primary, 0.2) : alpha('#64748b', 0.1),
                    color: loginMethod === method.id ? jTheme.primary : '#94a3b8',
                    border: '1px solid',
                    borderColor: loginMethod === method.id ? jTheme.primary : 'transparent',
                    fontWeight: 600,
                    transition: 'all 0.2s ease',
                    '&:hover': { bgcolor: alpha(jTheme.primary, 0.15) },
                    '& .MuiChip-icon': { color: loginMethod === method.id ? jTheme.primary : '#94a3b8' }
                  }}
                />
              ))}
            </Box>

            {/* Email Login Form */}
            {loginMethod === 'email' && (
              <form onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="Email Address"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="you@company.com"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <EmailIcon sx={{ color: jTheme.primary, transition: 'color 0.3s ease' }} />
                      </InputAdornment>
                    )
                  }}
                  sx={{
                    mb: 2,
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      bgcolor: alpha('#0a1929', 0.8),
                      color: jTheme.primary,
                      transition: 'all 0.3s ease',
                      '& fieldset': { borderColor: alpha(jTheme.primary, 0.3), transition: 'border-color 0.3s ease' },
                      '&:hover fieldset': { borderColor: jTheme.primary },
                      '&.Mui-focused fieldset': { borderColor: jTheme.primary, borderWidth: 2 }
                    },
                    '& .MuiInputLabel-root': { color: '#64748b' },
                    '& .MuiInputLabel-root.Mui-focused': { color: jTheme.primary },
                    '& .MuiOutlinedInput-input': {
                      color: '#e2e8f0',
                      '&::placeholder': { color: '#475569', opacity: 1 }
                    },
                    '& .MuiOutlinedInput-input:-webkit-autofill': {
                      WebkitBoxShadow: '0 0 0 100px #0a1929 inset',
                      WebkitTextFillColor: '#e2e8f0'
                    }
                  }}
                />

                <TextField
                  fullWidth
                  label="Password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Enter your password"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LockIcon sx={{ color: jTheme.primary, transition: 'color 0.3s ease' }} />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                          size="small"
                          sx={{ color: jTheme.primary, transition: 'color 0.3s ease' }}
                        >
                          {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                  sx={{
                    mb: 2,
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      bgcolor: alpha('#0a1929', 0.8),
                      color: jTheme.primary,
                      transition: 'all 0.3s ease',
                      '& fieldset': { borderColor: alpha(jTheme.primary, 0.3), transition: 'border-color 0.3s ease' },
                      '&:hover fieldset': { borderColor: jTheme.primary },
                      '&.Mui-focused fieldset': { borderColor: jTheme.primary, borderWidth: 2 }
                    },
                    '& .MuiInputLabel-root': { color: '#64748b' },
                    '& .MuiInputLabel-root.Mui-focused': { color: jTheme.primary },
                    '& .MuiOutlinedInput-input': {
                      color: '#e2e8f0',
                      '&::placeholder': { color: '#475569', opacity: 1 }
                    },
                    '& .MuiOutlinedInput-input:-webkit-autofill': {
                      WebkitBoxShadow: '0 0 0 100px #0a1929 inset',
                      WebkitTextFillColor: '#e2e8f0'
                    }
                  }}
                />

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        name="rememberMe"
                        checked={formData.rememberMe}
                        onChange={handleChange}
                        sx={{ color: '#64748b', '&.Mui-checked': { color: jTheme.primary }, transition: 'color 0.3s ease' }}
                      />
                    }
                    label={<Typography variant="body2" sx={{ color: '#94a3b8' }}>Remember me</Typography>}
                  />
                  <Link
                    component={RouterLink}
                    to="/forgot-password"
                    underline="hover"
                    sx={{ color: jTheme.primary, fontSize: '0.875rem', fontWeight: 500, transition: 'color 0.3s ease' }}
                  >
                    Forgot password?
                  </Link>
                </Box>

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  disabled={loading}
                  sx={{
                    py: 1.5,
                    borderRadius: 2,
                    background: `linear-gradient(135deg, ${jTheme.secondary}, ${jTheme.primary})`,
                    fontSize: '1rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    boxShadow: `0 4px 15px ${jTheme.glow}`,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      background: `linear-gradient(135deg, ${jTheme.primary}, ${jTheme.accent})`,
                      boxShadow: `0 6px 20px ${jTheme.glow}`
                    }
                  }}
                >
                  {loading ? <CircularProgress size={24} color="inherit" /> : 'Initialize Access'}
                </Button>
              </form>
            )}

            {/* Voice Login */}
            {loginMethod === 'voice' && (
              <Box sx={{ textAlign: 'center', py: 3 }}>
                <Box
                  onClick={handleVoiceLogin}
                  sx={{
                    width: 100,
                    height: 100,
                    borderRadius: '50%',
                    bgcolor: voiceActive ? alpha(jTheme.primary, 0.2) : alpha('#64748b', 0.1),
                    border: '2px solid',
                    borderColor: voiceActive ? jTheme.primary : '#64748b',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 3,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    boxShadow: voiceActive ? `0 0 20px ${jTheme.glow}` : 'none',
                    '&:hover': { borderColor: jTheme.primary, bgcolor: alpha(jTheme.primary, 0.1) }
                  }}
                >
                  {voiceActive ? (
                    <MicIcon sx={{ fontSize: 48, color: jTheme.primary, transition: 'color 0.3s ease' }} />
                  ) : (
                    <MicOffIcon sx={{ fontSize: 48, color: '#64748b' }} />
                  )}
                </Box>
                <VoiceWaveform active={voiceActive} theme={jTheme} />
                <Typography variant="body1" sx={{ color: 'white', mt: 2 }} fontWeight={600}>
                  {voiceActive ? 'Listening...' : 'Tap to speak your passphrase'}
                </Typography>
                <Typography variant="caption" sx={{ color: '#64748b', mt: 1, display: 'block' }}>
                  Voice biometrics with AI verification
                </Typography>
              </Box>
            )}

            {/* Face ID Login */}
            {loginMethod === 'face' && (
              <Box sx={{ textAlign: 'center', py: 3 }}>
                <Box
                  onClick={handleFaceLogin}
                  sx={{
                    width: 100,
                    height: 100,
                    borderRadius: '50%',
                    bgcolor: faceScanning ? alpha(jTheme.primary, 0.2) : alpha('#64748b', 0.1),
                    border: '2px solid',
                    borderColor: faceScanning ? jTheme.primary : '#64748b',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 3,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    animation: faceScanning ? `${pulse} 1s ease-in-out infinite` : 'none',
                    boxShadow: faceScanning ? `0 0 20px ${jTheme.glow}` : 'none',
                    '&:hover': { borderColor: jTheme.primary, bgcolor: alpha(jTheme.primary, 0.1) }
                  }}
                >
                  <FaceIcon sx={{ fontSize: 48, color: faceScanning ? jTheme.primary : '#64748b', transition: 'color 0.3s ease' }} />
                </Box>
                <Typography variant="body1" sx={{ color: 'white' }} fontWeight={600}>
                  {faceScanning ? 'Scanning facial features...' : 'Tap to start Face ID'}
                </Typography>
                <Typography variant="caption" sx={{ color: '#64748b', mt: 1, display: 'block' }}>
                  3D facial recognition with liveness detection
                </Typography>
              </Box>
            )}

            {/* Fingerprint Login */}
            {loginMethod === 'fingerprint' && (
              <Box sx={{ textAlign: 'center', py: 3 }}>
                <Box
                  onClick={handleFingerprintLogin}
                  sx={{
                    width: 100,
                    height: 100,
                    borderRadius: '50%',
                    bgcolor: fingerprintScanning ? alpha(jTheme.primary, 0.2) : alpha('#64748b', 0.1),
                    border: '2px solid',
                    borderColor: fingerprintScanning ? jTheme.primary : '#64748b',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 3,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    boxShadow: fingerprintScanning ? `0 0 20px ${jTheme.glow}` : 'none',
                    '&:hover': { borderColor: jTheme.primary, bgcolor: alpha(jTheme.primary, 0.1) }
                  }}
                >
                  <FingerprintIcon sx={{ fontSize: 48, color: fingerprintScanning ? jTheme.primary : '#64748b', transition: 'color 0.3s ease' }} />
                </Box>
                <Typography variant="body1" sx={{ color: 'white' }} fontWeight={600}>
                  {fingerprintScanning ? 'Verifying biometrics...' : 'Tap to scan fingerprint'}
                </Typography>
                <Typography variant="caption" sx={{ color: '#64748b', mt: 1, display: 'block' }}>
                  256-bit encrypted biometric verification
                </Typography>
              </Box>
            )}

            {/* Divider */}
            <Divider sx={{ my: 3, borderColor: alpha('#64748b', 0.3) }}>
              <Typography variant="caption" sx={{ color: '#64748b' }}>
                Or continue with
              </Typography>
            </Divider>

            {/* Social Login Buttons */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<GoogleIcon />}
                onClick={() => handleSocialLogin('google')}
                sx={{
                  py: 1.2,
                  borderRadius: 2,
                  borderColor: alpha('#64748b', 0.3),
                  color: '#94a3b8',
                  textTransform: 'none',
                  fontWeight: 500,
                  transition: 'all 0.3s ease',
                  '&:hover': { borderColor: jTheme.primary, color: jTheme.primary, bgcolor: alpha(jTheme.primary, 0.05) }
                }}
              >
                Google
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<GitHubIcon />}
                onClick={() => handleSocialLogin('github')}
                sx={{
                  py: 1.2,
                  borderRadius: 2,
                  borderColor: alpha('#64748b', 0.3),
                  color: '#94a3b8',
                  textTransform: 'none',
                  fontWeight: 500,
                  transition: 'all 0.3s ease',
                  '&:hover': { borderColor: jTheme.primary, color: jTheme.primary, bgcolor: alpha(jTheme.primary, 0.05) }
                }}
              >
                GitHub
              </Button>
              <Tooltip title="Microsoft SSO">
                <Button
                  variant="outlined"
                  onClick={() => handleSocialLogin('microsoft')}
                  sx={{
                    py: 1.2,
                    px: 2,
                    borderRadius: 2,
                    borderColor: alpha('#64748b', 0.3),
                    color: '#94a3b8',
                    minWidth: 'auto',
                    transition: 'all 0.3s ease',
                    '&:hover': { borderColor: jTheme.primary, bgcolor: alpha(jTheme.primary, 0.05) }
                  }}
                >
                  <BusinessIcon />
                </Button>
              </Tooltip>
            </Box>

            {/* Sign Up Link */}
            <Typography variant="body2" sx={{ color: '#94a3b8', mt: 3, textAlign: 'center' }}>
              Don't have an account?{' '}
              <Link
                component={RouterLink}
                to="/signup"
                underline="hover"
                sx={{ color: jTheme.primary, fontWeight: 600, transition: 'color 0.3s ease' }}
              >
                Request Access
              </Link>
            </Typography>

            {/* Demo Credentials */}
            <Box
              sx={{
                mt: 3,
                p: 2,
                borderRadius: 2,
                bgcolor: jTheme.cardBg,
                border: '1px dashed',
                borderColor: jTheme.cardBorder,
                transition: 'all 0.3s ease'
              }}
            >
              <Typography variant="caption" fontWeight={600} sx={{ color: jTheme.primary, transition: 'color 0.3s ease' }}>
                Demo Access:
              </Typography>
              <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block' }}>
                Any email/password works, or try Voice/Face/Biometric
              </Typography>
            </Box>
          </Paper>
        </Zoom>
      </Box>

      {/* CSS for blinking cursor */}
      <style>{`
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
      `}</style>
    </Box>
  )
}

export default LoginPage
