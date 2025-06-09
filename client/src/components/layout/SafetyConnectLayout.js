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
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Breadcrumbs,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  AccountCircle as AccountIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Dashboard as DashboardIcon,
  Menu as MenuIcon,
  NavigateNext as NavigateNextIcon,
} from '@mui/icons-material';

const drawerWidth = 200; // Reduced from 240 for minimal design

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
  const [mobileOpen, setMobileOpen] = useState(false);

  // Navigation items - minimal design
  const navigationItems = [
    {
      text: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/dashboard',
      active: location.pathname === '/' || location.pathname === '/dashboard'
    }
  ];

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
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
          {/* Left side - Logo and Mobile Menu */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{
                mr: 1,
                display: { sm: 'none' },
                color: 'white',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.1)',
                }
              }}
            >
              <MenuIcon />
            </IconButton>

            {/* SafetyConnect Logo */}
            <Box
              component="img"
              src="/SafetyConnect_logo.png"
              alt="SafetyConnect"
              sx={{
                height: 32,
                objectFit: 'contain',
                filter: 'brightness(0) invert(1)',
              }}
              onError={(e) => {
                e.target.style.display = 'none';
                const textElement = document.createElement('span');
                textElement.textContent = 'SafetyConnect';
                textElement.style.color = 'white';
                textElement.style.fontWeight = '600';
                textElement.style.fontSize = '1.25rem';
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
              sx={{
                color: 'white',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.1)',
                }
              }}
            >
              <SettingsIcon />
            </IconButton>

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
              <Avatar
                sx={{
                  width: 28,
                  height: 28,
                  bgcolor: 'rgba(255, 255, 255, 0.2)',
                  color: 'white',
                  fontSize: '0.75rem',
                  border: '1px solid rgba(255, 255, 255, 0.3)'
                }}
              >
                U
              </Avatar>
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

      {/* Minimal Sidebar Navigation */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              mt: 8,
              bgcolor: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              border: 'none',
              borderRight: '1px solid #e5e7eb',
            },
          }}
        >
          <List sx={{ p: 1 }}>
            {navigationItems.map((item) => (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    mb: 0.5,
                    bgcolor: item.active ? '#e3f2fd' : 'transparent',
                    '&:hover': {
                      bgcolor: item.active ? '#e3f2fd' : '#f8fafc',
                    },
                    minHeight: 40,
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {React.cloneElement(item.icon, {
                      sx: { 
                        color: item.active ? '#1976d2' : '#092f57',
                        fontSize: 20
                      }
                    })}
                  </ListItemIcon>
                  <ListItemText
                    primary={item.text}
                    primaryTypographyProps={{
                      fontWeight: item.active ? 600 : 500,
                      color: item.active ? '#1976d2' : '#092f57',
                      fontSize: '0.875rem'
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              mt: 8,
              bgcolor: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              border: 'none',
              borderRight: '1px solid #e5e7eb',
            },
          }}
          open
        >
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3, staggerChildren: 0.1 }}
          >
            <List sx={{ p: 1 }}>
              {navigationItems.map((item, index) => (
                <motion.div
                  key={item.text}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{
                    duration: 0.3,
                    delay: index * 0.1,
                    ease: [0.4, 0, 0.2, 1]
                  }}
                >
                  <ListItem disablePadding>
                    <motion.div
                      whileHover={{
                        scale: 1.02,
                        x: 4,
                        transition: { duration: 0.2 }
                      }}
                      whileTap={{ scale: 0.98 }}
                      style={{ width: '100%' }}
                    >
                      <ListItemButton
                        onClick={() => handleNavigation(item.path)}
                        sx={{
                          mb: 0.5,
                          borderRadius: 0.5, // Reduced border radius
                          bgcolor: item.active ? '#e3f2fd' : 'transparent',
                          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                          '&:hover': {
                            bgcolor: item.active ? '#e3f2fd' : '#f8fafc',
                            boxShadow: '0 2px 8px 0 rgba(0, 0, 0, 0.1)',
                          },
                          minHeight: 40,
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <motion.div
                            whileHover={{ scale: 1.1, rotate: 5 }}
                            transition={{ duration: 0.2 }}
                          >
                            {React.cloneElement(item.icon, {
                              sx: {
                                color: item.active ? '#1976d2' : '#092f57',
                                fontSize: 20
                              }
                            })}
                          </motion.div>
                        </ListItemIcon>
                        <ListItemText
                          primary={item.text}
                          primaryTypographyProps={{
                            fontWeight: item.active ? 600 : 500,
                            color: item.active ? '#1976d2' : '#092f57',
                            fontSize: '0.875rem'
                          }}
                        />
                      </ListItemButton>
                    </motion.div>
                  </ListItem>
                </motion.div>
              ))}
            </List>
          </motion.div>
        </Drawer>
      </Box>

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
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
