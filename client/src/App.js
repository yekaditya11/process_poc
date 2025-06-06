/**
 * Main App Component
 * AI Safety Summarizer Frontend Application
 */

import React, { useState } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import {
  ThemeProvider,
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  useMediaQuery,
  Divider,
  Switch,
  FormControlLabel,
  Button,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Assignment as PermitIcon,
  Warning as IncidentIcon,
  CheckCircle as ActionIcon,
  Assessment as InspectionIcon,
  Brightness4,
  Brightness7,
} from '@mui/icons-material';

import { lightTheme, darkTheme } from './theme/theme';
import ModulePage from './pages/ModulePage';

const drawerWidth = 280;

const navigationItems = [
  { text: 'Permit to Work', icon: <PermitIcon />, path: '/permits' },
  { text: 'Incident Management', icon: <IncidentIcon />, path: '/incidents' },
  { text: 'Action Tracking', icon: <ActionIcon />, path: '/actions' },
  { text: 'Inspection Tracking', icon: <InspectionIcon />, path: '/inspections' },
];

function App() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const isMobile = useMediaQuery('(max-width:600px)');

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const theme = darkMode ? darkTheme : lightTheme;

  const drawer = (
    <Box>
      <List>
        {navigationItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component="a"
              href={item.path}
              onClick={() => isMobile && setMobileOpen(false)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          {/* Full Width Top Navigation Bar */}
          <AppBar
            position="fixed"
            sx={{
              width: '100%',
              zIndex: (theme) => theme.zIndex.drawer + 1
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{ mr: 2, display: { sm: 'none' } }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                SafetyConnect
              </Typography>
              <IconButton
                color="inherit"
                onClick={() => setDarkMode(!darkMode)}
                sx={{ ml: 1 }}
              >
                {darkMode ? <Brightness7 /> : <Brightness4 />}
              </IconButton>
            </Toolbar>
          </AppBar>

          {/* Sidebar Navigation */}
          <Box
            component="nav"
            sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
          >
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
                  mt: 8, // Add margin top to account for AppBar
                },
              }}
            >
              {drawer}
            </Drawer>
            <Drawer
              variant="permanent"
              sx={{
                display: { xs: 'none', sm: 'block' },
                '& .MuiDrawer-paper': {
                  boxSizing: 'border-box',
                  width: drawerWidth,
                  mt: 8, // Add margin top to account for AppBar
                },
              }}
              open
            >
              {drawer}
            </Drawer>
          </Box>

          {/* Main Content Area */}
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              width: { sm: `calc(100% - ${drawerWidth}px)` },
              mt: 8, // Add margin top to account for AppBar
            }}
          >
            <Routes>
              <Route path="/" element={<Navigate to="/permits" replace />} />
              <Route
                path="/permits"
                element={
                  <ModulePage
                    module="permit"
                    title="Permit to Work"
                    icon={<PermitIcon color="primary" />}
                    description="Manage and track permit to work processes with interactive dashboards and AI-powered insights"
                  />
                }
              />
              <Route
                path="/incidents"
                element={
                  <ModulePage
                    module="incident"
                    title="Incident Management"
                    icon={<IncidentIcon color="error" />}
                    description="Track and analyze safety incidents with comprehensive reporting and AI analysis"
                  />
                }
              />
              <Route
                path="/actions"
                element={
                  <ModulePage
                    module="action"
                    title="Action Tracking"
                    icon={<ActionIcon color="success" />}
                    description="Monitor corrective and preventive actions with performance analytics and insights"
                  />
                }
              />
              <Route
                path="/inspections"
                element={
                  <ModulePage
                    module="inspection"
                    title="Inspection Tracking"
                    icon={<InspectionIcon color="info" />}
                    description="Manage safety inspections and audits with detailed analytics and AI recommendations"
                  />
                }
              />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
