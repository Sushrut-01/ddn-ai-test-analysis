import React, { createContext, useContext, useState, useEffect } from 'react'

// Color Theme Definitions - Light and Dark Themes
export const colorThemes = {
  // ============== LIGHT THEMES ==============

  // 1. Ocean Breeze - Cool blues and teals (Light)
  ocean: {
    name: 'Ocean Breeze',
    description: 'Cool blues and teals - Professional and calm',
    mode: 'light',
    primary: '#0891b2',
    primaryDark: '#0e7490',
    primaryLight: '#22d3ee',
    secondary: '#3b82f6',
    accent: '#06b6d4',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    background: '#f0f9ff',
    surface: '#ffffff',
    surfaceHover: '#f8fafc',
    headerGradient: 'linear-gradient(135deg, #0891b2 0%, #0e7490 100%)',
    cardGradient: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
    textPrimary: '#0f172a',
    textSecondary: '#64748b',
    border: '#e2e8f0',
  },

  // 2. Midnight Purple - Deep purples (Light)
  midnight: {
    name: 'Violet Dream',
    description: 'Deep purples with violet accents - Modern and elegant',
    mode: 'light',
    primary: '#7c3aed',
    primaryDark: '#6d28d9',
    primaryLight: '#a78bfa',
    secondary: '#8b5cf6',
    accent: '#c084fc',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#8b5cf6',
    background: '#faf5ff',
    surface: '#ffffff',
    surfaceHover: '#f5f3ff',
    headerGradient: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)',
    cardGradient: 'linear-gradient(135deg, #faf5ff 0%, #ede9fe 100%)',
    textPrimary: '#1e1b4b',
    textSecondary: '#6b7280',
    border: '#e9d5ff',
  },

  // 3. Sunset Orange - Warm oranges and reds (Light)
  sunset: {
    name: 'Sunset Glow',
    description: 'Warm oranges and corals - Energetic and vibrant',
    mode: 'light',
    primary: '#ea580c',
    primaryDark: '#c2410c',
    primaryLight: '#fb923c',
    secondary: '#f97316',
    accent: '#f59e0b',
    success: '#22c55e',
    warning: '#eab308',
    error: '#dc2626',
    info: '#0ea5e9',
    background: '#fffbeb',
    surface: '#ffffff',
    surfaceHover: '#fef3c7',
    headerGradient: 'linear-gradient(135deg, #ea580c 0%, #dc2626 100%)',
    cardGradient: 'linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)',
    textPrimary: '#1c1917',
    textSecondary: '#78716c',
    border: '#fed7aa',
  },

  // 4. Forest Green - Natural greens (Light)
  forest: {
    name: 'Forest Zen',
    description: 'Natural greens and earth tones - Fresh and organic',
    mode: 'light',
    primary: '#059669',
    primaryDark: '#047857',
    primaryLight: '#34d399',
    secondary: '#10b981',
    accent: '#14b8a6',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#0ea5e9',
    background: '#f0fdf4',
    surface: '#ffffff',
    surfaceHover: '#dcfce7',
    headerGradient: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
    cardGradient: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
    textPrimary: '#14532d',
    textSecondary: '#6b7280',
    border: '#bbf7d0',
  },

  // 5. Rose Pink - Soft pinks (Light)
  rose: {
    name: 'Rose Petal',
    description: 'Soft pinks and magentas - Elegant and sophisticated',
    mode: 'light',
    primary: '#db2777',
    primaryDark: '#be185d',
    primaryLight: '#f472b6',
    secondary: '#ec4899',
    accent: '#f43f5e',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#e11d48',
    info: '#3b82f6',
    background: '#fdf2f8',
    surface: '#ffffff',
    surfaceHover: '#fce7f3',
    headerGradient: 'linear-gradient(135deg, #db2777 0%, #be185d 100%)',
    cardGradient: 'linear-gradient(135deg, #fdf2f8 0%, #fce7f3 100%)',
    textPrimary: '#500724',
    textSecondary: '#6b7280',
    border: '#fbcfe8',
  },

  // 6. Corporate Blue - Professional blues (Light)
  corporate: {
    name: 'Corporate Pro',
    description: 'Professional blues - Clean and trustworthy',
    mode: 'light',
    primary: '#1d4ed8',
    primaryDark: '#1e40af',
    primaryLight: '#3b82f6',
    secondary: '#2563eb',
    accent: '#0ea5e9',
    success: '#16a34a',
    warning: '#ca8a04',
    error: '#dc2626',
    info: '#0284c7',
    background: '#f8fafc',
    surface: '#ffffff',
    surfaceHover: '#f1f5f9',
    headerGradient: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
    cardGradient: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
    textPrimary: '#0f172a',
    textSecondary: '#475569',
    border: '#cbd5e1',
  },

  // 7. Aurora Borealis - Multi-color gradients (Light)
  aurora: {
    name: 'Aurora Light',
    description: 'Multi-color gradients - Striking and unique',
    mode: 'light',
    primary: '#06b6d4',
    primaryDark: '#0891b2',
    primaryLight: '#22d3ee',
    secondary: '#8b5cf6',
    accent: '#ec4899',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    background: '#f8fafc',
    surface: '#ffffff',
    surfaceHover: '#f1f5f9',
    headerGradient: 'linear-gradient(135deg, #06b6d4 0%, #8b5cf6 50%, #ec4899 100%)',
    cardGradient: 'linear-gradient(135deg, #f0fdfa 0%, #faf5ff 50%, #fdf2f8 100%)',
    textPrimary: '#0f172a',
    textSecondary: '#64748b',
    border: '#e2e8f0',
  },

  // ============== DARK THEMES ==============

  // 8. Slate Dark - Cool grays (Dark)
  slateDark: {
    name: 'Slate Dark',
    description: 'Cool grays - Easy on the eyes',
    mode: 'dark',
    primary: '#6366f1',
    primaryDark: '#4f46e5',
    primaryLight: '#818cf8',
    secondary: '#8b5cf6',
    accent: '#06b6d4',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    background: '#0f172a',
    surface: '#1e293b',
    surfaceHover: '#334155',
    headerGradient: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
    cardGradient: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
    textPrimary: '#f1f5f9',
    textSecondary: '#94a3b8',
    border: '#334155',
    isDark: true,
  },

  // 9. Ocean Dark - Deep ocean blues (Dark)
  oceanDark: {
    name: 'Ocean Depths',
    description: 'Deep ocean blues - Immersive and focused',
    mode: 'dark',
    primary: '#22d3ee',
    primaryDark: '#06b6d4',
    primaryLight: '#67e8f9',
    secondary: '#38bdf8',
    accent: '#0ea5e9',
    success: '#34d399',
    warning: '#fbbf24',
    error: '#f87171',
    info: '#60a5fa',
    background: '#0c1929',
    surface: '#132f4c',
    surfaceHover: '#1a4166',
    headerGradient: 'linear-gradient(135deg, #132f4c 0%, #0891b2 100%)',
    cardGradient: 'linear-gradient(135deg, #132f4c 0%, #0c4a6e 100%)',
    textPrimary: '#e0f2fe',
    textSecondary: '#7dd3fc',
    border: '#1e4976',
    isDark: true,
  },

  // 10. Midnight Purple Dark (Dark)
  midnightDark: {
    name: 'Midnight Purple',
    description: 'Deep purple vibes - Mysterious and modern',
    mode: 'dark',
    primary: '#a78bfa',
    primaryDark: '#8b5cf6',
    primaryLight: '#c4b5fd',
    secondary: '#c084fc',
    accent: '#e879f9',
    success: '#34d399',
    warning: '#fbbf24',
    error: '#f87171',
    info: '#60a5fa',
    background: '#13111c',
    surface: '#1e1a2e',
    surfaceHover: '#2d2640',
    headerGradient: 'linear-gradient(135deg, #1e1a2e 0%, #581c87 100%)',
    cardGradient: 'linear-gradient(135deg, #1e1a2e 0%, #3b0764 100%)',
    textPrimary: '#f3e8ff',
    textSecondary: '#c4b5fd',
    border: '#3b2a5f',
    isDark: true,
  },

  // 11. Emerald Dark - Deep green (Dark)
  emeraldDark: {
    name: 'Emerald Night',
    description: 'Deep emerald green - Nature-inspired dark mode',
    mode: 'dark',
    primary: '#34d399',
    primaryDark: '#10b981',
    primaryLight: '#6ee7b7',
    secondary: '#2dd4bf',
    accent: '#14b8a6',
    success: '#4ade80',
    warning: '#fbbf24',
    error: '#f87171',
    info: '#60a5fa',
    background: '#0a1612',
    surface: '#122620',
    surfaceHover: '#1a3830',
    headerGradient: 'linear-gradient(135deg, #122620 0%, #047857 100%)',
    cardGradient: 'linear-gradient(135deg, #122620 0%, #064e3b 100%)',
    textPrimary: '#d1fae5',
    textSecondary: '#6ee7b7',
    border: '#1e4a3d',
    isDark: true,
  },

  // 12. Crimson Dark - Deep red (Dark)
  crimsonDark: {
    name: 'Crimson Night',
    description: 'Deep crimson red - Bold and dramatic',
    mode: 'dark',
    primary: '#fb7185',
    primaryDark: '#f43f5e',
    primaryLight: '#fda4af',
    secondary: '#f97316',
    accent: '#fbbf24',
    success: '#34d399',
    warning: '#fbbf24',
    error: '#f87171',
    info: '#60a5fa',
    background: '#1a0a0a',
    surface: '#2a1515',
    surfaceHover: '#3d2020',
    headerGradient: 'linear-gradient(135deg, #2a1515 0%, #991b1b 100%)',
    cardGradient: 'linear-gradient(135deg, #2a1515 0%, #7f1d1d 100%)',
    textPrimary: '#fee2e2',
    textSecondary: '#fca5a5',
    border: '#4a2525',
    isDark: true,
  },

  // 13. Cyber Neon - Neon accents (Dark)
  cyberNeon: {
    name: 'Cyber Neon',
    description: 'Neon accents on black - Futuristic vibes',
    mode: 'dark',
    primary: '#00ff88',
    primaryDark: '#00cc6a',
    primaryLight: '#66ffb3',
    secondary: '#00d4ff',
    accent: '#ff00ff',
    success: '#00ff88',
    warning: '#ffff00',
    error: '#ff3366',
    info: '#00d4ff',
    background: '#000000',
    surface: '#0a0a0a',
    surfaceHover: '#1a1a1a',
    headerGradient: 'linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 100%)',
    cardGradient: 'linear-gradient(135deg, #0a0a0a 0%, #0a1a2e 100%)',
    textPrimary: '#ffffff',
    textSecondary: '#888888',
    border: '#333333',
    isDark: true,
  },

  // 14. Aurora Dark - Multi-color on dark (Dark)
  auroraDark: {
    name: 'Aurora Dark',
    description: 'Northern lights on dark sky - Magical vibes',
    mode: 'dark',
    primary: '#22d3ee',
    primaryDark: '#06b6d4',
    primaryLight: '#67e8f9',
    secondary: '#a78bfa',
    accent: '#f472b6',
    success: '#34d399',
    warning: '#fbbf24',
    error: '#f87171',
    info: '#60a5fa',
    background: '#0f0f1a',
    surface: '#1a1a2e',
    surfaceHover: '#252540',
    headerGradient: 'linear-gradient(135deg, #06b6d4 0%, #8b5cf6 50%, #ec4899 100%)',
    cardGradient: 'linear-gradient(135deg, #1a1a2e 0%, #1e1b4b 50%, #3b0764 100%)',
    textPrimary: '#f1f5f9',
    textSecondary: '#94a3b8',
    border: '#2d2d4a',
    isDark: true,
  },

  // 15. Monokai - Developer favorite (Dark)
  monokai: {
    name: 'Monokai Pro',
    description: 'Classic developer theme - Familiar and productive',
    mode: 'dark',
    primary: '#66d9ef',
    primaryDark: '#3dc9db',
    primaryLight: '#89e5f5',
    secondary: '#a6e22e',
    accent: '#fd971f',
    success: '#a6e22e',
    warning: '#fd971f',
    error: '#f92672',
    info: '#66d9ef',
    background: '#1e1e1e',
    surface: '#272822',
    surfaceHover: '#3e3d32',
    headerGradient: 'linear-gradient(135deg, #272822 0%, #1e1e1e 100%)',
    cardGradient: 'linear-gradient(135deg, #272822 0%, #3e3d32 100%)',
    textPrimary: '#f8f8f2',
    textSecondary: '#75715e',
    border: '#3e3d32',
    isDark: true,
  },

  // 16. Dracula - Another developer favorite (Dark)
  dracula: {
    name: 'Dracula',
    description: 'Popular dark theme - Spooky and stylish',
    mode: 'dark',
    primary: '#bd93f9',
    primaryDark: '#a56eff',
    primaryLight: '#d4b8ff',
    secondary: '#50fa7b',
    accent: '#ff79c6',
    success: '#50fa7b',
    warning: '#f1fa8c',
    error: '#ff5555',
    info: '#8be9fd',
    background: '#1a1a2e',
    surface: '#282a36',
    surfaceHover: '#343746',
    headerGradient: 'linear-gradient(135deg, #282a36 0%, #44475a 100%)',
    cardGradient: 'linear-gradient(135deg, #282a36 0%, #383a4a 100%)',
    textPrimary: '#f8f8f2',
    textSecondary: '#6272a4',
    border: '#44475a',
    isDark: true,
  },
}

// Create Theme Context
const ThemeContext = createContext()

export const ThemeProvider = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState(() => {
    const saved = localStorage.getItem('ddn-dashboard-theme')
    return saved || 'ocean'
  })

  useEffect(() => {
    localStorage.setItem('ddn-dashboard-theme', currentTheme)
  }, [currentTheme])

  const theme = colorThemes[currentTheme]

  // Separate themes by mode
  const lightThemes = Object.entries(colorThemes).filter(([_, t]) => !t.isDark)
  const darkThemes = Object.entries(colorThemes).filter(([_, t]) => t.isDark)

  const value = {
    currentTheme,
    setCurrentTheme,
    theme,
    themes: colorThemes,
    lightThemes,
    darkThemes,
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useColorTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useColorTheme must be used within a ThemeProvider')
  }
  return context
}

export default ThemeContext
