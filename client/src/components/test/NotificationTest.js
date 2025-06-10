import React from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Alert
} from '@mui/material';
import {
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import chartManager from '../../services/chartManager';

const NotificationTest = () => {
  const testNotifications = [
    {
      message: 'Chart added to dashboard successfully!',
      severity: 'success',
      icon: <SuccessIcon />,
      color: '#2e7d32'
    },
    {
      message: 'Failed to save chart to dashboard',
      severity: 'error',
      icon: <ErrorIcon />,
      color: '#d32f2f'
    },
    {
      message: 'Dashboard manager not available',
      severity: 'warning',
      icon: <WarningIcon />,
      color: '#ed6c02'
    },
    {
      message: 'Chart saved locally due to network issues',
      severity: 'info',
      icon: <InfoIcon />,
      color: '#0288d1'
    }
  ];

  const showTestNotification = (message, severity) => {
    chartManager.showNotification(message, severity);
  };

  const showAllNotifications = () => {
    testNotifications.forEach((notification, index) => {
      setTimeout(() => {
        showTestNotification(notification.message, notification.severity);
      }, index * 1000); // Stagger notifications by 1 second
    });
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        🔔 Notification System Test
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        This page tests the new notification system that replaces alerts when adding charts to the dashboard.
        The notifications appear in the top-right corner and can be dismissed by clicking or will auto-hide after 5 seconds.
      </Alert>

      <Grid container spacing={3}>
        {/* Individual Notification Tests */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Individual Notification Tests
              </Typography>
              <Typography variant="body2" sx={{ mb: 3, color: 'text.secondary' }}>
                Click each button to test different notification types:
              </Typography>
              
              <Grid container spacing={2}>
                {testNotifications.map((notification, index) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={notification.icon}
                      onClick={() => showTestNotification(notification.message, notification.severity)}
                      sx={{
                        borderColor: notification.color,
                        color: notification.color,
                        '&:hover': {
                          borderColor: notification.color,
                          backgroundColor: `${notification.color}10`
                        }
                      }}
                    >
                      Test {notification.severity.charAt(0).toUpperCase() + notification.severity.slice(1)}
                    </Button>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Batch Test */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Batch Test
              </Typography>
              <Typography variant="body2" sx={{ mb: 3, color: 'text.secondary' }}>
                Test multiple notifications in sequence:
              </Typography>
              
              <Button
                variant="contained"
                fullWidth
                onClick={showAllNotifications}
                sx={{
                  bgcolor: '#3b82f6',
                  '&:hover': { bgcolor: '#2563eb' }
                }}
              >
                Show All Notifications
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Features */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Notification Features
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h6" color="primary">
                      ✨
                    </Typography>
                    <Typography variant="subtitle2" gutterBottom>
                      Material Design
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Consistent with MUI theme
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h6" color="primary">
                      🎯
                    </Typography>
                    <Typography variant="subtitle2" gutterBottom>
                      Auto-Hide
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Disappears after 5 seconds
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h6" color="primary">
                      ⏸️
                    </Typography>
                    <Typography variant="subtitle2" gutterBottom>
                      Hover to Pause
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Pauses auto-hide on hover
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h6" color="primary">
                      👆
                    </Typography>
                    <Typography variant="subtitle2" gutterBottom>
                      Click to Dismiss
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Manual close anytime
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Usage Instructions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                How It Works
              </Typography>
              <Typography variant="body2" component="div">
                <ol>
                  <li><strong>Chart Addition:</strong> When you click the "+" button on a chart in the chatbot, a success notification appears instead of an alert</li>
                  <li><strong>Error Handling:</strong> If something goes wrong, an error notification shows the issue</li>
                  <li><strong>Fallback System:</strong> If the main notification system isn't available, custom notifications are created</li>
                  <li><strong>No More Alerts:</strong> All dashboard-related alerts have been replaced with these smooth notifications</li>
                </ol>
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default NotificationTest;
