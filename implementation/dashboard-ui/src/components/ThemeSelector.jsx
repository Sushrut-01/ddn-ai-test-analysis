import React, { useState } from 'react'
import {
  Box,
  IconButton,
  Popover,
  Typography,
  Grid,
  Tooltip,
  Paper,
  Chip,
  Fade,
  Tabs,
  Tab,
  Divider
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import PaletteIcon from '@mui/icons-material/Palette'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import LightModeIcon from '@mui/icons-material/LightMode'
import { useColorTheme } from '../theme/ThemeContext'

const ThemeSelector = () => {
  const { currentTheme, setCurrentTheme, theme, lightThemes, darkThemes } = useColorTheme()
  const [anchorEl, setAnchorEl] = useState(null)
  const [tabValue, setTabValue] = useState(theme.isDark ? 1 : 0)

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const handleThemeChange = (themeKey) => {
    setCurrentTheme(themeKey)
  }

  const open = Boolean(anchorEl)

  const ThemeCard = ({ themeKey, t, isSelected }) => (
    <Paper
      elevation={0}
      onClick={() => handleThemeChange(themeKey)}
      sx={{
        p: 1.5,
        cursor: 'pointer',
        border: '2px solid',
        borderColor: isSelected ? t.primary : 'transparent',
        borderRadius: 2,
        transition: 'all 0.2s ease',
        position: 'relative',
        overflow: 'hidden',
        bgcolor: t.isDark ? t.surface : '#f8fafc',
        '&:hover': {
          borderColor: alpha(t.primary, 0.5),
          transform: 'translateY(-2px)',
          boxShadow: `0 4px 12px ${alpha(t.primary, 0.2)}`
        }
      }}
    >
      {/* Color Preview Bar */}
      <Box
        sx={{
          height: 36,
          borderRadius: 1.5,
          background: t.headerGradient,
          mb: 1.5,
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Accent dots */}
        <Box sx={{ position: 'absolute', bottom: 6, right: 6, display: 'flex', gap: 0.5 }}>
          <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: t.success }} />
          <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: t.warning }} />
          <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: t.error }} />
        </Box>
      </Box>

      {/* Theme Name */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box>
          <Typography
            variant="body2"
            fontWeight={600}
            sx={{ color: t.isDark ? t.textPrimary : t.textPrimary, fontSize: '0.8rem' }}
          >
            {t.name}
          </Typography>
        </Box>
        {isSelected && (
          <CheckCircleIcon sx={{ color: t.primary, fontSize: 18 }} />
        )}
      </Box>

      {/* Color Swatches */}
      <Box sx={{ display: 'flex', gap: 0.5, mt: 1 }}>
        <Box sx={{ width: 14, height: 14, borderRadius: '50%', bgcolor: t.primary, border: '2px solid white', boxShadow: '0 1px 2px rgba(0,0,0,0.1)' }} />
        <Box sx={{ width: 14, height: 14, borderRadius: '50%', bgcolor: t.secondary, border: '2px solid white', boxShadow: '0 1px 2px rgba(0,0,0,0.1)' }} />
        <Box sx={{ width: 14, height: 14, borderRadius: '50%', bgcolor: t.accent, border: '2px solid white', boxShadow: '0 1px 2px rgba(0,0,0,0.1)' }} />
      </Box>
    </Paper>
  )

  return (
    <>
      <Tooltip title="Change Theme">
        <IconButton
          onClick={handleClick}
          sx={{
            color: 'inherit',
            transition: 'transform 0.2s',
            '&:hover': { transform: 'rotate(15deg)' }
          }}
        >
          <PaletteIcon />
        </IconButton>
      </Tooltip>

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        TransitionComponent={Fade}
        PaperProps={{
          sx: {
            p: 2,
            width: 480,
            maxHeight: '80vh',
            borderRadius: 3,
            boxShadow: '0 20px 40px rgba(0,0,0,0.15)',
          }
        }}
      >
        <Typography variant="h6" fontWeight={600} sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <PaletteIcon sx={{ color: theme.primary }} />
          Choose Your Theme
        </Typography>

        {/* Tabs for Light/Dark */}
        <Tabs
          value={tabValue}
          onChange={(e, v) => setTabValue(v)}
          sx={{
            mb: 2,
            '& .MuiTab-root': {
              minHeight: 40,
              fontWeight: 600,
            }
          }}
        >
          <Tab
            icon={<LightModeIcon sx={{ fontSize: 18 }} />}
            iconPosition="start"
            label={`Light (${lightThemes.length})`}
          />
          <Tab
            icon={<DarkModeIcon sx={{ fontSize: 18 }} />}
            iconPosition="start"
            label={`Dark (${darkThemes.length})`}
          />
        </Tabs>

        {/* Light Themes */}
        {tabValue === 0 && (
          <Box sx={{ maxHeight: 400, overflow: 'auto', pr: 1 }}>
            <Grid container spacing={1.5}>
              {lightThemes.map(([key, t]) => (
                <Grid item xs={4} key={key}>
                  <ThemeCard themeKey={key} t={t} isSelected={currentTheme === key} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Dark Themes */}
        {tabValue === 1 && (
          <Box sx={{ maxHeight: 400, overflow: 'auto', pr: 1 }}>
            <Grid container spacing={1.5}>
              {darkThemes.map(([key, t]) => (
                <Grid item xs={4} key={key}>
                  <ThemeCard themeKey={key} t={t} isSelected={currentTheme === key} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        <Divider sx={{ my: 2 }} />

        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="caption" color="textSecondary">
            Current:
          </Typography>
          <Chip
            icon={theme.isDark ? <DarkModeIcon sx={{ fontSize: 14 }} /> : <LightModeIcon sx={{ fontSize: 14 }} />}
            label={theme.name}
            size="small"
            sx={{
              bgcolor: alpha(theme.primary, 0.1),
              color: theme.primary,
              fontWeight: 600,
              '& .MuiChip-icon': { color: theme.primary }
            }}
          />
        </Box>
      </Popover>
    </>
  )
}

export default ThemeSelector
