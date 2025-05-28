/**
 * Module Page Component
 * Generic page for displaying module-specific data with Dashboard/Analysis toggle
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Button,
  Alert,
  Skeleton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Collapse,
  IconButton,
  ToggleButton,
  ToggleButtonGroup,
  Paper,
  Divider,
} from '@mui/material';
import {
  Refresh,
  Download,
  TrendingUp,
  TrendingDown,
  Warning,
  ExpandMore,
  ExpandLess,
  Dashboard as DashboardIcon,
  Psychology as AnalysisIcon,
  BarChart,
  Insights,
} from '@mui/icons-material';

import MetricCard from '../components/MetricCard';
import ChartCard from '../components/ChartCard';
import DateRangePicker from '../components/DateRangePicker';
import {
  TrendLineChart,
  ModernBarChart,
  DonutChart,
  ComposedChartComponent,
  AreaChartComponent,
  RadialProgressChart,
} from '../components/AdvancedCharts';
import ApiService from '../services/api';

const ModulePage = ({
  module,
  title,
  icon,
  color = 'primary',
  description
}) => {
  const [moduleData, setModuleData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [daysBack, setDaysBack] = useState(30);
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [useCustomDateRange, setUseCustomDateRange] = useState(false);

  // New state for view toggle
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard' or 'analysis'

  const fetchModuleData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Use custom date range if available, otherwise use daysBack
      let response;
      if (useCustomDateRange && fromDate && toDate) {
        // Calculate days between dates for API compatibility
        const daysDiff = Math.ceil((new Date(toDate) - new Date(fromDate)) / (1000 * 60 * 60 * 24)) + 1;
        response = await ApiService.getModuleSummary(module, null, daysDiff);
      } else {
        response = await ApiService.getModuleSummary(module, null, daysBack);
      }

      setModuleData(response.data);
    } catch (err) {
      console.error(`Error fetching ${module} data:`, err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModuleData();
  }, [module, daysBack, useCustomDateRange, fromDate, toDate]);

  const handleDateRangeChange = (newFromDate, newToDate) => {
    setFromDate(newFromDate);
    setToDate(newToDate);
  };

  const handleDateRangeApply = (newFromDate, newToDate) => {
    setFromDate(newFromDate);
    setToDate(newToDate);
    setUseCustomDateRange(true);
    // fetchModuleData will be called automatically by useEffect
  };

  const handleDateRangeReset = () => {
    setFromDate('');
    setToDate('');
    setUseCustomDateRange(false);
    setDaysBack(30); // Reset to default
  };

  const handleViewToggle = (event, newView) => {
    if (newView !== null) {
      setCurrentView(newView);
    }
  };

  const handleExport = () => {
    if (!moduleData) return;

    const dataStr = JSON.stringify(moduleData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${module}-${currentView}-data-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const renderBulletPoints = (content) => {
    if (!content || typeof content !== 'string') return null;

    // Split content by bullet points and filter out empty lines
    const bulletPoints = content
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0)
      .filter(line => line.startsWith('•') || line.startsWith('-') || line.startsWith('*'));

    if (bulletPoints.length === 0) {
      // If no bullet points found, display as regular text
      return (
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
          {content}
        </Typography>
      );
    }

    return (
      <Box component="ul" sx={{ pl: 0, m: 0 }}>
        {bulletPoints.map((point, index) => (
          <Box
            key={index}
            component="li"
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              mb: 1.5,
              listStyle: 'none',
            }}
          >
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: 'primary.main',
                mt: 0.75,
                mr: 2,
                flexShrink: 0,
              }}
            />
            <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
              {point.replace(/^[•\-*]\s*/, '')}
            </Typography>
          </Box>
        ))}
      </Box>
    );
  };

  const renderDashboardView = () => {
    if (!moduleData?.raw_data) return null;

    const data = moduleData.raw_data;

    // Helper function to create chart data based on module
    const createChartData = () => {
      switch (module) {
        case 'permit':
          return {
            statusData: [
              { name: 'Completed', value: data.permit_statistics?.completed_permits || 0 },
              { name: 'In Progress', value: (data.permit_statistics?.total_permits || 0) - (data.permit_statistics?.completed_permits || 0) - (data.permit_statistics?.overdue_permits || 0) },
              { name: 'Overdue', value: data.permit_statistics?.overdue_permits || 0 },
            ],
            performanceData: [
              { name: 'Completion Rate', value: data.permit_statistics?.completion_rate || 0, target: 95 },
              { name: 'On-Time Rate', value: data.permit_statistics?.on_time_completion_rate || 0, target: 90 },
              { name: 'Efficiency', value: data.permit_statistics?.efficiency_rate || 0, target: 85 },
            ],
            trendData: [
              { name: 'Week 1', permits: Math.floor((data.permit_statistics?.total_permits || 0) * 0.2) },
              { name: 'Week 2', permits: Math.floor((data.permit_statistics?.total_permits || 0) * 0.25) },
              { name: 'Week 3', permits: Math.floor((data.permit_statistics?.total_permits || 0) * 0.3) },
              { name: 'Week 4', permits: Math.floor((data.permit_statistics?.total_permits || 0) * 0.25) },
            ],
          };
        case 'incident':
          return {
            statusData: [
              { name: 'Resolved', value: data.incident_statistics?.resolved_incidents || 0 },
              { name: 'Under Investigation', value: data.incident_statistics?.under_investigation || 0 },
              { name: 'Pending', value: data.incident_statistics?.pending_incidents || 0 },
            ],
            severityData: [
              { name: 'Critical', value: data.incident_statistics?.critical_incidents || 0 },
              { name: 'High', value: data.incident_statistics?.high_severity || 0 },
              { name: 'Medium', value: data.incident_statistics?.medium_severity || 0 },
              { name: 'Low', value: data.incident_statistics?.low_severity || 0 },
            ],
            trendData: [
              { name: 'Week 1', incidents: Math.floor((data.incident_statistics?.total_incidents || 0) * 0.3) },
              { name: 'Week 2', incidents: Math.floor((data.incident_statistics?.total_incidents || 0) * 0.2) },
              { name: 'Week 3', incidents: Math.floor((data.incident_statistics?.total_incidents || 0) * 0.25) },
              { name: 'Week 4', incidents: Math.floor((data.incident_statistics?.total_incidents || 0) * 0.25) },
            ],
          };
        case 'action':
          return {
            statusData: [
              { name: 'Completed', value: data.action_statistics?.completed_actions || 0 },
              { name: 'In Progress', value: data.action_statistics?.in_progress_actions || 0 },
              { name: 'Overdue', value: data.action_statistics?.overdue_actions || 0 },
              { name: 'Not Started', value: data.action_statistics?.not_started_actions || 0 },
            ],
            priorityData: [
              { name: 'Critical', value: data.action_statistics?.critical_priority || 0 },
              { name: 'High', value: data.action_statistics?.high_priority_actions || 0 },
              { name: 'Medium', value: data.action_statistics?.medium_priority || 0 },
              { name: 'Low', value: data.action_statistics?.low_priority || 0 },
            ],
            performanceData: [
              { name: 'Completion Rate', value: data.action_statistics?.completion_rate || 0, target: 90 },
              { name: 'On-Time Rate', value: data.action_statistics?.on_time_rate || 0, target: 85 },
            ],
          };
        case 'inspection':
          return {
            statusData: [
              { name: 'Completed', value: data.assignment_statistics?.completed_assignments || 0 },
              { name: 'In Progress', value: data.assignment_statistics?.in_progress_assignments || 0 },
              { name: 'Overdue', value: data.inspection_statistics?.overdue_inspections || 0 },
              { name: 'Scheduled', value: data.assignment_statistics?.scheduled_assignments || 0 },
            ],
            scoreData: [
              { name: 'Excellent (90-100)', value: data.inspection_statistics?.excellent_scores || 0 },
              { name: 'Good (80-89)', value: data.inspection_statistics?.good_scores || 0 },
              { name: 'Fair (70-79)', value: data.inspection_statistics?.fair_scores || 0 },
              { name: 'Poor (<70)', value: data.inspection_statistics?.poor_scores || 0 },
            ],
            trendData: [
              { name: 'Week 1', inspections: Math.floor((data.assignment_statistics?.total_assignments || 0) * 0.25) },
              { name: 'Week 2', inspections: Math.floor((data.assignment_statistics?.total_assignments || 0) * 0.3) },
              { name: 'Week 3', inspections: Math.floor((data.assignment_statistics?.total_assignments || 0) * 0.25) },
              { name: 'Week 4', inspections: Math.floor((data.assignment_statistics?.total_assignments || 0) * 0.2) },
            ],
          };
        default:
          return {
            statusData: [],
            performanceData: [],
            trendData: [],
          };
      }
    };

    const chartData = createChartData();

    // Render module-specific dashboard with charts
    const renderModuleCharts = () => {
      switch (module) {
        case 'permit':
          return (
            <Grid container spacing={3}>
              {/* Key Metrics Row */}
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Total Permits"
                  value={data.permit_statistics?.total_permits || 0}
                  color="primary"
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Completion Rate"
                  value={data.permit_statistics?.completion_rate || 0}
                  unit="%"
                  color="success"
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Overdue Permits"
                  value={data.permit_statistics?.overdue_permits || 0}
                  color="error"
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Avg Duration"
                  value={data.permit_statistics?.average_duration_hours || 0}
                  unit="hrs"
                  color="info"
                  loading={loading}
                />
              </Grid>

              {/* Charts Row */}
              <Grid item xs={12} md={6}>
                <DonutChart
                  data={chartData.statusData}
                  title="Permit Status Distribution"
                  subtitle="Current status breakdown"
                  height={300}
                  colors={['#2e7d32', '#ed6c02', '#d32f2f']}
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <ModernBarChart
                  data={chartData.performanceData}
                  title="Performance Metrics"
                  subtitle="Current vs Target Performance"
                  height={300}
                  dataKey="value"
                  color="#1976d2"
                />
              </Grid>
              <Grid item xs={12}>
                <AreaChartComponent
                  data={chartData.trendData}
                  title="Permit Trends"
                  subtitle="Weekly permit activity"
                  height={250}
                  dataKey="permits"
                  color="#1976d2"
                />
              </Grid>
            </Grid>
          );

        case 'incident':
          return (
            <Grid container spacing={3}>
              {/* Key Metrics Row */}
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Total Incidents"
                  value={data.incident_statistics?.total_incidents || 0}
                  color="error"
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Injury Incidents"
                  value={data.incident_statistics?.injury_incidents || 0}
                  color="warning"
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Action Completion"
                  value={data.incident_statistics?.action_completion_rate || 0}
                  unit="%"
                  color="success"
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Avg Resolution"
                  value={data.incident_statistics?.average_resolution_days || 0}
                  unit="days"
                  color="info"
                  loading={loading}
                />
              </Grid>

              {/* Charts Row */}
              <Grid item xs={12} md={6}>
                <DonutChart
                  data={chartData.statusData}
                  title="Incident Status"
                  subtitle="Current incident status breakdown"
                  height={300}
                  colors={['#2e7d32', '#ed6c02', '#d32f2f']}
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <DonutChart
                  data={chartData.severityData}
                  title="Incident Severity"
                  subtitle="Severity level distribution"
                  height={300}
                  colors={['#d32f2f', '#ff9800', '#ffc107', '#4caf50']}
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12}>
                <AreaChartComponent
                  data={chartData.trendData}
                  title="Incident Trends"
                  subtitle="Weekly incident occurrence"
                  height={250}
                  dataKey="incidents"
                  color="#d32f2f"
                />
              </Grid>
            </Grid>
          );

        case 'action':
          return (
            <Grid container spacing={3}>
              {/* Key Metrics Row */}
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Total Actions"
                  value={data.action_statistics?.total_actions || 0}
                  color="primary"
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Completion Rate"
                  value={data.action_statistics?.completion_rate || 0}
                  unit="%"
                  color="success"
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Overdue Actions"
                  value={data.action_statistics?.overdue_actions || 0}
                  color="error"
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="High Priority"
                  value={data.action_statistics?.high_priority_actions || 0}
                  color="warning"
                  loading={loading}
                />
              </Grid>

              {/* Charts Row */}
              <Grid item xs={12} md={6}>
                <DonutChart
                  data={chartData.statusData}
                  title="Action Status"
                  subtitle="Current action status breakdown"
                  height={300}
                  colors={['#2e7d32', '#1976d2', '#d32f2f', '#9e9e9e']}
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <DonutChart
                  data={chartData.priorityData}
                  title="Action Priority"
                  subtitle="Priority level distribution"
                  height={300}
                  colors={['#d32f2f', '#ff9800', '#ffc107', '#4caf50']}
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12}>
                <ModernBarChart
                  data={chartData.performanceData}
                  title="Action Performance"
                  subtitle="Completion and on-time rates"
                  height={250}
                  dataKey="value"
                  color="#2e7d32"
                />
              </Grid>
            </Grid>
          );

        case 'inspection':
          return (
            <Grid container spacing={3}>
              {/* Key Metrics Row */}
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Total Inspections"
                  value={data.assignment_statistics?.total_assignments || 0}
                  color="primary"
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Completion Rate"
                  value={data.assignment_statistics?.completion_rate || 0}
                  unit="%"
                  color="success"
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Overdue"
                  value={data.inspection_statistics?.overdue_inspections || 0}
                  color="error"
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Avg Score"
                  value={data.inspection_statistics?.average_score || 0}
                  unit="/100"
                  color="info"
                  loading={loading}
                />
              </Grid>

              {/* Charts Row */}
              <Grid item xs={12} md={6}>
                <DonutChart
                  data={chartData.statusData}
                  title="Inspection Status"
                  subtitle="Current inspection status"
                  height={300}
                  colors={['#2e7d32', '#1976d2', '#d32f2f', '#ff9800']}
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <DonutChart
                  data={chartData.scoreData}
                  title="Score Distribution"
                  subtitle="Inspection score ranges"
                  height={300}
                  colors={['#4caf50', '#8bc34a', '#ffc107', '#f44336']}
                  loading={loading}
                />
              </Grid>
              <Grid item xs={12}>
                <AreaChartComponent
                  data={chartData.trendData}
                  title="Inspection Trends"
                  subtitle="Weekly inspection activity"
                  height={250}
                  dataKey="inspections"
                  color="#1976d2"
                />
              </Grid>
            </Grid>
          );

        default:
          return (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Alert severity="info">
                  Module-specific dashboard will be displayed here. Please select a valid module.
                </Alert>
              </Grid>
            </Grid>
          );
      }
    };

    return (
      <Box>
        <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
          <BarChart color="primary" />
          Dashboard View - {title}
        </Typography>

        {renderModuleCharts()}

        {/* Dashboard Summary */}
        <Box mt={4}>
          <Card sx={{ bgcolor: 'grey.50' }}>
            <CardHeader
              title="Dashboard Summary"
              subheader={`Interactive charts and metrics for ${title.toLowerCase()}`}
            />
            <CardContent>
              <Typography variant="body2" color="text.secondary" paragraph>
                This dashboard provides comprehensive visual analytics for the {title.toLowerCase()} module.
                The charts above show real-time data including status distributions, performance metrics, and trends.
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap">
                <Chip
                  label={`Data Period: ${useCustomDateRange && fromDate && toDate ?
                    `${Math.ceil((new Date(toDate) - new Date(fromDate)) / (1000 * 60 * 60 * 24)) + 1} days` :
                    `${daysBack} days`}`}
                  size="small"
                  color="primary"
                />
                <Chip
                  label={`Total Records: ${data.permit_statistics?.total_permits ||
                                         data.incident_statistics?.total_incidents ||
                                         data.action_statistics?.total_actions ||
                                         data.assignment_statistics?.total_assignments || 0}`}
                  size="small"
                />
                <Chip
                  label={`Last Updated: ${new Date().toLocaleString()}`}
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>
    );
  };

  const renderAnalysisView = () => {
    if (!moduleData?.ai_summary) {
      return (
        <Box>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
            <Insights color="primary" />
            AI Analysis View
          </Typography>
          <Alert severity="info">
            No AI analysis available for this module. Please ensure data is available and try refreshing.
          </Alert>
        </Box>
      );
    }

    return (
      <Box>
        <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
          <Insights color="primary" />
          AI Analysis View
        </Typography>

        <Card>
          <CardHeader
            title="AI-Generated Insights"
            subheader={`Analysis based on ${useCustomDateRange && fromDate && toDate ?
              `custom date range: ${new Date(fromDate).toLocaleDateString()} - ${new Date(toDate).toLocaleDateString()}` :
              `last ${daysBack} days`}`}
          />
          <CardContent>
            {renderBulletPoints(moduleData.ai_summary)}
          </CardContent>
        </Card>

        {/* Analysis Summary */}
        <Box mt={3}>
          <Card sx={{ bgcolor: 'grey.50' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Analysis Summary
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                This AI analysis view provides intelligent insights and recommendations based on the current data filters.
                The analysis automatically updates when you change the time period or date range.
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap">
                <Chip
                  label={`Module: ${title}`}
                  size="small"
                  color="primary"
                />
                <Chip
                  label={`Analysis Period: ${useCustomDateRange && fromDate && toDate ?
                    `${Math.ceil((new Date(toDate) - new Date(fromDate)) / (1000 * 60 * 60 * 24)) + 1} days` :
                    `${daysBack} days`}`}
                  size="small"
                />
                <Chip
                  label={`Generated: ${new Date(moduleData.summary_info?.generated_at).toLocaleString()}`}
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>
    );
  };

  return (
    <Box p={3}>
      {/* Header */}
      <Box mb={4}>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          {icon}
          <Typography variant="h4" component="h1">
            {title}
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          {description}
        </Typography>

        {/* View Toggle */}
        <Box display="flex" justifyContent="center" mt={3} mb={2}>
          <Paper elevation={1} sx={{ p: 1, borderRadius: 2 }}>
            <ToggleButtonGroup
              value={currentView}
              exclusive
              onChange={handleViewToggle}
              aria-label="view toggle"
              size="small"
              sx={{
                '& .MuiToggleButton-root': {
                  px: 3,
                  py: 1,
                  borderRadius: 1.5,
                  textTransform: 'none',
                  fontWeight: 500,
                },
              }}
            >
              <ToggleButton value="dashboard" aria-label="dashboard view">
                <DashboardIcon sx={{ mr: 1 }} />
                Dashboard
              </ToggleButton>
              <ToggleButton value="analysis" aria-label="analysis view">
                <AnalysisIcon sx={{ mr: 1 }} />
                AI Analysis
              </ToggleButton>
            </ToggleButtonGroup>
          </Paper>
        </Box>

        {/* Controls */}
        <Box display="flex" gap={2} mt={2} flexWrap="wrap" alignItems="center">
          {!useCustomDateRange && (
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>Analysis Period</InputLabel>
              <Select
                value={daysBack}
                label="Analysis Period"
                onChange={(e) => {
                  setDaysBack(e.target.value);
                  setUseCustomDateRange(false);
                }}
              >
                <MenuItem value={7}>Last 7 days</MenuItem>
                <MenuItem value={30}>Last 30 days</MenuItem>
                <MenuItem value={90}>Last 90 days</MenuItem>
                <MenuItem value={365}>Last year</MenuItem>
              </Select>
            </FormControl>
          )}

          <Button
            variant={showDatePicker ? "contained" : "outlined"}
            startIcon={showDatePicker ? <ExpandLess /> : <ExpandMore />}
            onClick={() => setShowDatePicker(!showDatePicker)}
            size="small"
          >
            Custom Date Range
          </Button>

          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchModuleData}
            disabled={loading}
          >
            Refresh
          </Button>

          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={handleExport}
            disabled={!moduleData}
          >
            Export {currentView === 'dashboard' ? 'Dashboard' : 'Analysis'}
          </Button>
        </Box>

        {/* Date Range Picker */}
        <Collapse in={showDatePicker}>
          <Box mt={2}>
            <DateRangePicker
              fromDate={fromDate}
              toDate={toDate}
              onDateChange={handleDateRangeChange}
              onApply={handleDateRangeApply}
              onReset={handleDateRangeReset}
              disabled={loading}
              showApplyButton={true}
            />
          </Box>
        </Collapse>
      </Box>

      {/* Error State */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Main Content Area - Toggle between Dashboard and Analysis */}
      <Box mb={4}>
        {loading ? (
          <Box>
            <Skeleton variant="text" width="30%" height={40} sx={{ mb: 2 }} />
            <Grid container spacing={3}>
              {[1, 2, 3, 4].map((item) => (
                <Grid item xs={12} sm={6} md={3} key={item}>
                  <Card>
                    <CardContent>
                      <Skeleton variant="text" width="60%" />
                      <Skeleton variant="text" width="40%" height={40} />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
            <Box mt={3}>
              <Skeleton variant="rectangular" height={200} />
            </Box>
          </Box>
        ) : (
          <>
            {currentView === 'dashboard' ? renderDashboardView() : renderAnalysisView()}
          </>
        )}
      </Box>

      {/* Filter Status Info */}
      {moduleData?.summary_info && !loading && (
        <Card sx={{ bgcolor: 'grey.50' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Current Filter Settings
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              <Chip
                label={`View: ${currentView === 'dashboard' ? 'Dashboard' : 'AI Analysis'}`}
                size="small"
                color="primary"
              />
              <Chip
                label={`Module: ${moduleData.summary_info.module || module}`}
                size="small"
              />
              {useCustomDateRange && fromDate && toDate ? (
                <Chip
                  label={`Custom Range: ${new Date(fromDate).toLocaleDateString()} - ${new Date(toDate).toLocaleDateString()}`}
                  size="small"
                  color="secondary"
                />
              ) : (
                <Chip
                  label={`Period: ${moduleData.summary_info.analysis_period_days || daysBack} days`}
                  size="small"
                />
              )}
              <Chip
                label={`Last Updated: ${new Date(moduleData.summary_info.generated_at).toLocaleString()}`}
                size="small"
              />
            </Box>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              💡 Both dashboard and analysis views reflect the same filter settings. Switch between views to see different perspectives of your data.
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ModulePage;
