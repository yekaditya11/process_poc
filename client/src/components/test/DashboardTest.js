/**
 * Dashboard Test Component
 * Test the drag-and-drop dashboard functionality
 */

import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import DashboardManager from '../dashboard/DashboardManager';

const DashboardTest = () => {
  const [testCharts] = useState([
    {
      id: 'test_chart_1',
      chart_id: 'test_chart_1',
      title: 'Sample Incident Trends',
      chart_data: {
        type: 'echarts',
        echarts_config: {
          title: { text: 'Incident Trends' },
          xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May'] },
          yAxis: { type: 'value' },
          series: [{
            data: [5, 3, 8, 2, 6],
            type: 'line',
            smooth: true
          }]
        }
      },
      source: 'test',
      created_at: new Date().toISOString(),
      size: 6
    },
    {
      id: 'test_chart_2',
      chart_id: 'test_chart_2',
      title: 'Action Status Distribution',
      chart_data: {
        type: 'echarts',
        echarts_config: {
          title: { text: 'Action Status' },
          series: [{
            type: 'pie',
            data: [
              { value: 15, name: 'Open' },
              { value: 25, name: 'In Progress' },
              { value: 35, name: 'Completed' }
            ]
          }]
        }
      },
      source: 'test',
      created_at: new Date().toISOString(),
      size: 6
    }
  ]);

  const addTestChart = async () => {
    if (window.addChartToDashboard) {
      const randomChart = testCharts[Math.floor(Math.random() * testCharts.length)];
      const newChart = {
        ...randomChart,
        title: `${randomChart.title} (${Date.now()})`,
        chartData: randomChart.chart_data
      };

      try {
        await window.addChartToDashboard(newChart);
        console.log('Test chart added successfully');
      } catch (error) {
        console.error('Error adding test chart:', error);
      }
    } else {
      // Use the chart manager's notification system instead of alert
      if (window.chartManager) {
        window.chartManager.showNotification(
          'Dashboard manager not available. Please navigate to Custom Dashboard first.',
          'warning'
        );
      } else {
        console.warn('Dashboard manager not available. Please navigate to Custom Dashboard first.');
      }
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard Test Page
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3 }}>
        This page demonstrates the drag-and-drop dashboard functionality.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Test Chart Addition
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Click the button below to add a test chart to your custom dashboard.
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={addTestChart}
                sx={{ bgcolor: '#3b82f6' }}
              >
                Add Test Chart
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Instructions
              </Typography>
              <Typography variant="body2" component="div">
                <ol>
                  <li>Navigate to the "Custom Dashboard" module</li>
                  <li>Start a chat with the AI and ask for charts</li>
                  <li>Click the "+" button on any generated chart</li>
                  <li>Switch to Custom Dashboard to see your charts</li>
                  <li>Use "Edit Mode" to drag and rearrange charts</li>
                </ol>
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          Custom Dashboard
        </Typography>
        <DashboardManager />
      </Box>
    </Box>
  );
};

export default DashboardTest;
