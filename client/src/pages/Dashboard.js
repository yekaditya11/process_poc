/**
 * Dashboard Page
 * Main dashboard with overview metrics and charts
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  Paper,
  Alert,
  Fab,
  Tooltip,
  Button,
  Collapse,
  IconButton,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Divider,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Assignment,
  Warning,
  CheckCircle,
  Assessment,
  Refresh,
  ExpandMore,
  ExpandLess,
  DateRange,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
} from '@mui/icons-material';

import MetricCard from '../components/MetricCard';
import DateRangePicker from '../components/DateRangePicker';
import {
  TrendLineChart,
  ModernBarChart,
  DonutChart,
  ComposedChartComponent,
} from '../components/AdvancedCharts';
import ApiService from '../services/api';

const Dashboard = () => {
  const theme = useTheme();
  const [dashboardData, setDashboardData] = useState(null);
  const [kpiData, setKpiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [useCustomDateRange, setUseCustomDateRange] = useState(false);

  // Helper function to process data for charts
  const processChartData = (data) => {
    if (!data) {
      // Return empty data when no real data is available
      return [];
    }

    // Process real data only - create a simple daily distribution
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return days.map((day, index) => ({
      name: day,
      permits: data.permit_summary?.total_permits ? Math.floor(data.permit_summary.total_permits / 7) : 0,
      incidents: data.incident_summary?.total_incidents ? Math.floor(data.incident_summary.total_incidents / 7) : 0,
      actions: data.action_summary?.total_actions ? Math.floor(data.action_summary.total_actions / 7) : 0,
      inspections: data.inspection_summary?.total_inspections ? Math.floor(data.inspection_summary.total_inspections / 7) : 0,
    }));
  };

  // Helper function to create donut chart data
  const createDonutData = (data) => {
    if (!data) return [];

    return [
      { name: 'Permits', value: data.permit_summary?.total_permits || 0 },
      { name: 'Incidents', value: data.incident_summary?.total_incidents || 0 },
      { name: 'Actions', value: data.action_summary?.total_actions || 0 },
      { name: 'Inspections', value: data.inspection_summary?.total_inspections || 0 },
    ];
  };

  // Helper function to create completion rate data
  const createCompletionData = (data) => {
    if (!data) return [];

    return [
      {
        name: 'Permits',
        total: data.permit_summary?.total_permits || 0,
        completed: data.permit_summary?.completed_permits || 0,
      },
      {
        name: 'Actions',
        total: data.action_summary?.total_actions || 0,
        completed: data.action_summary?.completed_actions || 0,
      },
      {
        name: 'Inspections',
        total: data.inspection_summary?.total_inspections || 0,
        completed: data.inspection_summary?.completed_inspections || 0,
      },
    ];
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Calculate effective days back based on date range
      let effectiveDaysBack = 7; // Default for dashboard (was 30, changed to 7 to match backend default)
      if (useCustomDateRange && fromDate && toDate) {
        effectiveDaysBack = Math.ceil((new Date(toDate) - new Date(fromDate)) / (1000 * 60 * 60 * 24)) + 1;
      }

      console.log('Dashboard: Fetching data with parameters:', {
        useCustomDateRange,
        fromDate,
        toDate,
        effectiveDaysBack
      });

      // Fetch dashboard and KPI data in parallel
      const [dashboardResponse, kpiResponse] = await Promise.all([
        ApiService.getDashboardData(null, effectiveDaysBack), // Now supports date filtering
        ApiService.getKPIMetrics(null, effectiveDaysBack), // Pass the calculated days back
      ]);

      console.log('Dashboard data received:', dashboardResponse.data);
      console.log('KPI data received:', kpiResponse.data);

      setDashboardData(dashboardResponse.data);
      setKpiData(kpiResponse.data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [useCustomDateRange, fromDate, toDate]);

  const handleDateRangeChange = (newFromDate, newToDate) => {
    setFromDate(newFromDate);
    setToDate(newToDate);
  };

  const handleDateRangeApply = (newFromDate, newToDate) => {
    setFromDate(newFromDate);
    setToDate(newToDate);
    setUseCustomDateRange(true);
    // fetchDashboardData will be called automatically by useEffect
  };

  const handleDateRangeReset = () => {
    setFromDate('');
    setToDate('');
    setUseCustomDateRange(false);
  };



  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      {/* Header */}
      <Box mb={4}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Safety Dashboard
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Real-time overview of safety management metrics
            </Typography>
            {lastUpdated && (
              <Typography variant="caption" color="text.secondary">
                Last updated: {lastUpdated.toLocaleString()}
              </Typography>
            )}
            {useCustomDateRange && fromDate && toDate && (
              <Typography variant="caption" color="primary" sx={{ display: 'block', mt: 0.5 }}>
                📅 Showing data from {new Date(fromDate).toLocaleDateString()} to {new Date(toDate).toLocaleDateString()}
              </Typography>
            )}
          </Box>

          <Button
            variant={showDatePicker ? "contained" : "outlined"}
            startIcon={<DateRange />}
            endIcon={showDatePicker ? <ExpandLess /> : <ExpandMore />}
            onClick={() => setShowDatePicker(!showDatePicker)}
            size="small"
          >
            Date Filter
          </Button>
        </Box>

        {/* Date Range Picker */}
        <Collapse in={showDatePicker}>
          <DateRangePicker
            fromDate={fromDate}
            toDate={toDate}
            onDateChange={handleDateRangeChange}
            onApply={handleDateRangeApply}
            onReset={handleDateRangeReset}
            disabled={loading}
            showApplyButton={true}
          />
        </Collapse>
      </Box>

      {/* Enhanced Key Metrics */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Permit Completion Rate"
            value={Math.round(kpiData?.permit_completion_rate || 0)}
            unit="%"
            trend={kpiData?.permit_completion_trend > 0 ? "up" : kpiData?.permit_completion_trend < 0 ? "down" : "stable"}
            trendValue={kpiData?.permit_completion_trend || null}
            color="success"
            icon={<Assignment />}
            tooltip="Percentage of permits completed on time"
            loading={loading}
            target={95}
            progress={kpiData?.permit_completion_rate || 0}
            variant="gradient"
            subtitle="Target: 95%"
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Safety Incidents"
            value={kpiData?.incident_count || 0}
            trend={kpiData?.incident_count_trend > 0 ? "up" : kpiData?.incident_count_trend < 0 ? "down" : "stable"}
            trendValue={kpiData?.incident_count_trend || null}
            color="error"
            icon={<Warning />}
            tooltip="Total number of incidents reported this period"
            loading={loading}
            variant="gradient"
            subtitle="Lower is better"
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Action Completion"
            value={Math.round(kpiData?.action_completion_rate || 0)}
            unit="%"
            trend={kpiData?.action_completion_trend > 0 ? "up" : kpiData?.action_completion_trend < 0 ? "down" : "stable"}
            trendValue={kpiData?.action_completion_trend || null}
            color="info"
            icon={<CheckCircle />}
            tooltip="Percentage of corrective actions completed on time"
            loading={loading}
            target={90}
            progress={kpiData?.action_completion_rate || 0}
            variant="gradient"
            subtitle="Target: 90%"
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Inspection Rate"
            value={Math.round(kpiData?.inspection_completion_rate || 0)}
            unit="%"
            trend={kpiData?.inspection_completion_trend > 0 ? "up" : kpiData?.inspection_completion_trend < 0 ? "down" : "stable"}
            trendValue={kpiData?.inspection_completion_trend || null}
            color="primary"
            icon={<Assessment />}
            tooltip="Percentage of scheduled inspections completed"
            loading={loading}
            target={98}
            progress={kpiData?.inspection_completion_rate || 0}
            variant="gradient"
            subtitle="Target: 98%"
          />
        </Grid>
      </Grid>



      {/* Advanced Charts Section */}
      <Grid container spacing={3} mb={4}>
        {/* Main Trend Chart */}
        <Grid item xs={12} lg={8}>
          <TrendLineChart
            data={processChartData(dashboardData)}
            title="Safety Metrics Trends"
            subtitle="Daily trends across all safety modules"
            height={350}
            onRefresh={fetchDashboardData}
            showTrend={true}
            loading={loading}
          />
        </Grid>

        {/* Module Distribution */}
        <Grid item xs={12} lg={4}>
          <DonutChart
            data={createDonutData(dashboardData)}
            title="Module Activity"
            subtitle="Distribution of activities by module"
            height={350}
            colors={['#1976d2', '#d32f2f', '#2e7d32', '#ed6c02']}
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* Secondary Charts */}
      <Grid container spacing={3} mb={4}>
        {/* Completion Rates */}
        <Grid item xs={12} md={6}>
          <ComposedChartComponent
            data={createCompletionData(dashboardData)}
            title="Completion Performance"
            subtitle="Total vs Completed items by module"
            height={300}
          />
        </Grid>


      </Grid>

      {/* Performance Metrics Charts */}
      <Grid container spacing={3} mb={4}>
        {/* Bar Chart for Module Performance */}
        <Grid item xs={12} md={8}>
          <ModernBarChart
            data={[
              { name: 'Permits', completion: kpiData?.permit_completion_rate || 0 },
              { name: 'Actions', completion: kpiData?.action_completion_rate || 0 },
              { name: 'Inspections', completion: kpiData?.inspection_completion_rate || 0 },
            ]}
            title="Module Completion Rates"
            subtitle="Current completion performance by module"
            height={300}
            dataKey="completion"
            color="#1976d2"
          />
        </Grid>


      </Grid>

      {/* Enhanced Alerts & Insights Section */}
      <Grid container spacing={3} mb={4}>
        {/* Critical Alerts */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ height: '100%' }}>
            <CardHeader
              title="Critical Alerts & Actions Required"
              subheader="Items requiring immediate attention"
              action={
                <Chip
                  label={`${((dashboardData?.permit_metrics?.overdue_permits || 0) +
                           (kpiData?.overdue_actions || 0) +
                           (kpiData?.overdue_inspections || 0))} Total`}
                  color="warning"
                  size="small"
                />
              }
            />
            <CardContent>
              <Grid container spacing={2}>
                {dashboardData?.permit_metrics?.overdue_permits > 0 && (
                  <Grid item xs={12} md={6}>
                    <Alert
                      severity="warning"
                      sx={{
                        '& .MuiAlert-message': { width: '100%' },
                        borderRadius: 2,
                      }}
                    >
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2">
                          <strong>{dashboardData.permit_metrics.overdue_permits}</strong> permits overdue
                        </Typography>
                        <Chip label="High Priority" size="small" color="warning" />
                      </Box>
                    </Alert>
                  </Grid>
                )}

                {dashboardData?.incident_metrics?.injury_incidents > 0 && (
                  <Grid item xs={12} md={6}>
                    <Alert
                      severity="error"
                      sx={{
                        '& .MuiAlert-message': { width: '100%' },
                        borderRadius: 2,
                      }}
                    >
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2">
                          <strong>{dashboardData.incident_metrics.injury_incidents}</strong> injury incidents
                        </Typography>
                        <Chip label="Critical" size="small" color="error" />
                      </Box>
                    </Alert>
                  </Grid>
                )}

                {kpiData?.overdue_actions > 0 && (
                  <Grid item xs={12} md={6}>
                    <Alert
                      severity="warning"
                      sx={{
                        '& .MuiAlert-message': { width: '100%' },
                        borderRadius: 2,
                      }}
                    >
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2">
                          <strong>{kpiData.overdue_actions}</strong> actions overdue
                        </Typography>
                        <Chip label="Medium" size="small" color="warning" />
                      </Box>
                    </Alert>
                  </Grid>
                )}

                {kpiData?.overdue_inspections > 0 && (
                  <Grid item xs={12} md={6}>
                    <Alert
                      severity="info"
                      sx={{
                        '& .MuiAlert-message': { width: '100%' },
                        borderRadius: 2,
                      }}
                    >
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2">
                          <strong>{kpiData.overdue_inspections}</strong> inspections overdue
                        </Typography>
                        <Chip label="Medium" size="small" color="info" />
                      </Box>
                    </Alert>
                  </Grid>
                )}

                {/* No alerts message */}
                {(!dashboardData?.permit_metrics?.overdue_permits &&
                  !dashboardData?.incident_metrics?.injury_incidents &&
                  !kpiData?.overdue_actions &&
                  !kpiData?.overdue_inspections) && (
                  <Grid item xs={12}>
                    <Alert severity="success" sx={{ borderRadius: 2 }}>
                      <Typography variant="body2">
                        🎉 All systems operating normally - no critical alerts at this time
                      </Typography>
                    </Alert>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Dynamic Insights */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardHeader
              title="Dynamic Insights"
              subheader="Real-time performance indicators"
            />
            <CardContent>
              <Box display="flex" flexDirection="column" gap={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2" color="text.secondary">
                    Safety Trend
                  </Typography>
                  <Box display="flex" alignItems="center" gap={0.5}>
                    {kpiData?.trends_calculated ? (
                      <>
                        {kpiData.permit_completion_trend > 0 ? (
                          <TrendingUp color="success" fontSize="small" />
                        ) : kpiData.permit_completion_trend < 0 ? (
                          <TrendingDown color="error" fontSize="small" />
                        ) : (
                          <TrendingFlat color="info" fontSize="small" />
                        )}
                        <Typography
                          variant="h6"
                          color={kpiData.permit_completion_trend > 0 ? "success.main" : kpiData.permit_completion_trend < 0 ? "error.main" : "info.main"}
                        >
                          {kpiData.permit_completion_trend > 0 ? '+' : ''}{kpiData.permit_completion_trend}%
                        </Typography>
                      </>
                    ) : (
                      <Typography variant="h6" color="text.secondary">
                        N/A
                      </Typography>
                    )}
                  </Box>
                </Box>
                <Divider />

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2" color="text.secondary">
                    Total Active Items
                  </Typography>
                  <Typography variant="h6" color="primary">
                    {(dashboardData?.permit_summary?.total_permits || 0) +
                     (dashboardData?.action_summary?.total_actions || 0) +
                     (dashboardData?.inspection_summary?.total_inspections || 0)}
                  </Typography>
                </Box>
                <Divider />

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2" color="text.secondary">
                    Completion Progress
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    {Math.round(((kpiData?.permit_completion_rate || 0) +
                                 (kpiData?.action_completion_rate || 0) +
                                 (kpiData?.inspection_completion_rate || 0)) / 3)}%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Refresh FAB */}
      <Tooltip title="Refresh Dashboard">
        <Fab
          color="primary"
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
          }}
          onClick={fetchDashboardData}
          disabled={loading}
        >
          <Refresh />
        </Fab>
      </Tooltip>
    </Box>
  );
};

export default Dashboard;
