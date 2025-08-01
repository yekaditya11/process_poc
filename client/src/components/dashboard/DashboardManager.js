/**
 * Dashboard Manager Component
 * Manages custom dashboards and chart integration from chatbot
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Alert,
  Snackbar,
  CircularProgress
} from '@mui/material';
import CustomDashboard from './CustomDashboard';
import chartManager from '../../services/chartManager';
import ApiService from '../../services/api';

const DashboardManager = () => {
  const [savedCharts, setSavedCharts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  // Load charts from global chart manager
  useEffect(() => {
    // Get initial charts
    setSavedCharts(chartManager.getCharts());

    // Listen for chart updates
    const handleChartsUpdate = (charts) => {
      setSavedCharts(charts);
    };

    chartManager.addListener(handleChartsUpdate);

    // Override global notification function
    if (typeof window !== 'undefined') {
      // eslint-disable-next-line no-undef
      window['showNotification'] = showNotification;
    }

    return () => {
      chartManager.removeListener(handleChartsUpdate);
    };
  }, []);

  // Delete chart using global chart manager
  const deleteChart = async (chartId) => {
    await chartManager.deleteChart(chartId);
  };

  // Update dashboard (for reordering)
  const updateDashboard = (updatedCharts) => {
    chartManager.updateCharts(updatedCharts);
  };

  // Save dashboard configuration
  const saveDashboard = async (dashboardConfig) => {
    try {
      setLoading(true);
      
      // Save to backend if API is available
      try {
        await ApiService.saveDashboard(
          dashboardConfig.name,
          dashboardConfig.charts,
          'anonymous'
        );
        showNotification(`Dashboard "${dashboardConfig.name}" saved successfully!`, 'success');
      } catch (apiError) {
        console.warn('Backend save failed, using local storage:', apiError);
        // Fallback to localStorage
        const savedDashboards = JSON.parse(localStorage.getItem('savedDashboards') || '[]');
        savedDashboards.push({
          ...dashboardConfig,
          id: `dashboard_${Date.now()}`
        });
        localStorage.setItem('savedDashboards', JSON.stringify(savedDashboards));
        showNotification(`Dashboard "${dashboardConfig.name}" saved locally!`, 'success');
      }
    } catch (error) {
      console.error('Error saving dashboard:', error);
      showNotification('Failed to save dashboard', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Show notification
  const showNotification = (message, severity = 'success') => {
    setNotification({ open: true, message, severity });
  };

  // Close notification
  const closeNotification = () => {
    setNotification({ ...notification, open: false });
  };

  // Debug: Log when component mounts
  useEffect(() => {
    console.log('DashboardManager mounted');
    console.log('Current saved charts:', savedCharts);
  }, [savedCharts]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <CustomDashboard
        savedCharts={savedCharts}
        onSaveChart={saveDashboard}
        onDeleteChart={deleteChart}
        onUpdateDashboard={updateDashboard}
      />

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={4000}
        onClose={closeNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={closeNotification} 
          severity={notification.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DashboardManager;
