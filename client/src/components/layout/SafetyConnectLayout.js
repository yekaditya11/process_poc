/**
 * SafetyConnectLayout Component
 * Clean, professional layout for SafetyConnect dashboard
 * Features minimal sidebar, clean header, and professional styling
 */

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Breadcrumbs,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  AccountCircle as AccountIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  NavigateNext as NavigateNextIcon,
} from '@mui/icons-material';

const SafetyConnectLayout = ({ 
  children, 
  title, 
  subtitle, 
  headerActions, 
  breadcrumbs = [] 
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      {/* Clean Header - No rounded corners */}
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          bgcolor: '#092f57',
          backdropFilter: 'blur(10px)',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 0,
          color: 'white',
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between', minHeight: '64px !important' }}>
          {/* Left side - Logo */}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {/* SafetyConnect Logo */}
            <Box
              component="img"
              src="/SafetyConnect_logo.png"
              alt="SafetyConnect"
              sx={{
                height: 28,
                objectFit: 'contain',
                filter: 'brightness(0) invert(1)',
              }}
              onError={(e) => {
                e.target.style.display = 'none';
                const textElement = document.createElement('span');
                textElement.textContent = 'SafetyConnect';
                textElement.style.color = 'white';
                textElement.style.fontWeight = '600';
                textElement.style.fontSize = '1.125rem';
                e.target.parentNode.appendChild(textElement);
              }}
            />
          </Box>

          {/* Center - Header Actions */}
          <Box sx={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
            {headerActions}
          </Box>

          {/* Right side - User Menu */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton
              size="large"
              onClick={handleMenu}
              sx={{
                color: 'white',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.1)',
                }
              }}
            >
              <AccountIcon fontSize="large" />
            </IconButton>

            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
              onClick={handleClose}
              PaperProps={{
                elevation: 0,
                sx: {
                  mt: 1.5,
                  minWidth: 180,
                  border: '1px solid #e5e7eb',
                  '& .MuiMenuItem-root': {
                    px: 2,
                    py: 1,
                    '&:hover': {
                      bgcolor: '#f8fafc',
                    },
                  },
                },
              }}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <MenuItem onClick={handleClose}>
                <AccountIcon sx={{ mr: 2, color: '#092f57' }} />
                Profile
              </MenuItem>
              <MenuItem onClick={handleClose}>
                <SettingsIcon sx={{ mr: 2, color: '#092f57' }} />
                Settings
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleClose}>
                <LogoutIcon sx={{ mr: 2, color: '#092f57' }} />
                Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>



      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: '100%',
          bgcolor: '#f8fafc',
          minHeight: 'calc(100vh - 64px)',
          mt: 8,
        }}
      >
        {/* Page Header with Breadcrumbs */}
        {(title || breadcrumbs.length > 0) && (
          <Box
            sx={{
              px: 3,
              py: 2,
              bgcolor: 'white',
              borderBottom: '1px solid #e5e7eb',
            }}
          >
            {breadcrumbs.length > 0 && (
              <Breadcrumbs
                separator={<NavigateNextIcon fontSize="small" />}
                sx={{ mb: 1 }}
              >
                {breadcrumbs.map((crumb, index) => {
                  const IconComponent = crumb.icon;
                  return (
                    <Box
                      key={index}
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.5,
                        color: index === breadcrumbs.length - 1 ? '#092f57' : '#64748b',
                        fontSize: '0.875rem',
                        fontWeight: index === breadcrumbs.length - 1 ? 600 : 400,
                      }}
                    >
                      {IconComponent && <IconComponent sx={{ fontSize: 16 }} />}
                      {crumb.label}
                    </Box>
                  );
                })}
              </Breadcrumbs>
            )}
            
            {title && (
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 600,
                  color: '#092f57',
                  mb: subtitle ? 0.5 : 0,
                }}
              >
                {title}
              </Typography>
            )}
            
            {subtitle && (
              <Typography
                variant="body2"
                sx={{
                  color: '#64748b',
                  fontWeight: 400,
                }}
              >
                {subtitle}
              </Typography>
            )}
          </Box>
        )}

        {/* Page Content */}
        <Box sx={{ p: 0 }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default SafetyConnectLayout;
