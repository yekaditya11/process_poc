/**
 * Modern Incident Investigation Charts Component
 * Enhanced visualizations with animations and modern design
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Grid,
  Typography,
  Paper,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  Card,
  CardContent,
} from '@mui/material';
import {
  Report as ReportIcon,
  ErrorOutline as ErrorOutlineIcon,
  CheckCircle as CheckCircleIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { motion } from 'framer-motion';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const IncidentCharts = ({ data = {} }) => {
  const [trendPeriod, setTrendPeriod] = useState('monthly');
  const chartRefs = useRef({});

  // Handle chart resizing when chatbot opens/closes or window resizes
  useEffect(() => {
    const handleResize = () => {
      // Small delay to allow for chatbot animation to complete
      setTimeout(() => {
        // Resize all Chart.js instances
        Object.values(chartRefs.current).forEach(chartRef => {
          if (chartRef && chartRef.chartInstance) {
            chartRef.chartInstance.resize();
          }
        });
      }, 350); // Slightly longer than chatbot animation (300ms)
    };

    // Listen for window resize events
    window.addEventListener('resize', handleResize);

    // Also listen for custom chatbot events if they exist
    window.addEventListener('chatbot-toggle', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('chatbot-toggle', handleResize);
    };
  }, []);

  // Function to register chart references
  const registerChart = (chartId, chartRef) => {
    if (chartRef) {
      chartRefs.current[chartId] = chartRef;
    }
  };

  // Safety check for data
  if (!data || typeof data !== 'object') {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          No incident data available
        </Typography>
      </Box>
    );
  }

  // Extract data with fallbacks
  const {
    incidents_reported = 0,
    incident_reporting_trends = [],
    incident_reporting_trends_weekly = [],
    incident_reporting_trends_monthly = [],
    incident_reporting_trends_yearly = [],
    open_incidents = 0,
    closed_incidents = 0,
    incident_types = {},
    incidents_by_location = {},
    people_injured = 0,
  } = data;

  // Get current trend data based on selected period
  const getCurrentTrendData = () => {
    switch (trendPeriod) {
      case 'weekly':
        return incident_reporting_trends_weekly;
      case 'yearly':
        return incident_reporting_trends_yearly;
      case 'monthly':
      default:
        return incident_reporting_trends_monthly.length > 0 ? incident_reporting_trends_monthly : incident_reporting_trends;
    }
  };

  const currentTrendData = getCurrentTrendData();

  // Modern color palette with gradients
  const modernColors = {
    primary: '#1e40af',
    primaryGradient: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
    error: '#dc2626',
    errorGradient: 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)',
    warning: '#d97706',
    warningGradient: 'linear-gradient(135deg, #d97706 0%, #f59e0b 100%)',
    success: '#059669',
    successGradient: 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
    info: '#0284c7',
    infoGradient: 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)',
    secondary: '#7c3aed',
    secondaryGradient: 'linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%)',
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.95 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: { duration: 0.5, ease: [0.4, 0, 0.2, 1] }
    }
  };

  // Modern trend chart data with enhanced styling
  const trendData = {
    labels: currentTrendData.map(item => item.period || 'N/A'),
    datasets: [
      {
        label: 'Incidents Reported',
        data: currentTrendData.map(item => item.count || 0),
        borderColor: modernColors.error,
        backgroundColor: modernColors.error + '15',
        fill: true,
        tension: 0.4,
        borderWidth: 3,
        pointBackgroundColor: modernColors.error,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 3,
        pointRadius: 6,
        pointHoverRadius: 8,
        pointHoverBackgroundColor: modernColors.error,
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 3,
        shadowOffsetX: 0,
        shadowOffsetY: 4,
        shadowBlur: 8,
        shadowColor: modernColors.error + '30',
      },
    ],
  };

  // Modern donut chart data with enhanced colors and effects
  const typesData = {
    labels: Object.keys(incident_types),
    datasets: [
      {
        data: Object.values(incident_types),
        backgroundColor: [
          modernColors.error,
          modernColors.warning,
          modernColors.info,
          modernColors.success,
          modernColors.secondary,
          '#8b5cf6',
          '#06b6d4',
          '#84cc16',
          '#f59e0b',
          '#ef4444',
        ],
        borderColor: '#ffffff',
        borderWidth: 4,
        hoverBorderWidth: 6,
        hoverOffset: 8,
        cutout: '65%',
        spacing: 2,
        borderRadius: 8,
        borderJoinStyle: 'round',
      },
    ],
  };

  // Modern locations chart with gradient bars
  const locationsData = {
    labels: Object.keys(incidents_by_location).slice(0, 10), // Top 10 locations
    datasets: [
      {
        label: 'Incidents by Location',
        data: Object.values(incidents_by_location).slice(0, 10),
        backgroundColor: modernColors.primary,
        borderColor: modernColors.primary,
        borderWidth: 0,
        borderRadius: 8,
        borderSkipped: false,
        hoverBackgroundColor: modernColors.error,
        hoverBorderColor: modernColors.error,
        hoverBorderWidth: 2,
      },
    ],
  };

  // Modern chart options with enhanced styling
  const modernChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: 'index',
    },
    animation: {
      duration: 1500,
      easing: 'easeInOutQuart',
    },
    layout: {
      padding: {
        top: 10,
        bottom: 10,
        left: 10,
        right: 10,
      },
    },
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 15,
          usePointStyle: true,
          pointStyle: 'circle',
          boxWidth: 8,
          boxHeight: 8,
          font: {
            size: 12,
            weight: 600,
            family: 'Inter, system-ui, sans-serif',
          },
          color: '#374151',
        },
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.95)',
        titleColor: '#ffffff',
        bodyColor: '#e5e7eb',
        borderColor: modernColors.primary,
        borderWidth: 2,
        cornerRadius: 12,
        titleFont: {
          size: 14,
          weight: 700,
          family: 'Inter, system-ui, sans-serif',
        },
        bodyFont: {
          size: 13,
          weight: 500,
          family: 'Inter, system-ui, sans-serif',
        },
        padding: 16,
        displayColors: true,
        boxPadding: 8,
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: '#6b7280',
          font: {
            size: 12,
            weight: 600,
            family: 'Inter, system-ui, sans-serif',
          },
          padding: 8,
        },
        border: {
          color: '#e5e7eb',
          width: 2,
        },
      },
      y: {
        grid: {
          color: '#f3f4f6',
          lineWidth: 1,
          drawBorder: false,
        },
        ticks: {
          color: '#6b7280',
          font: {
            size: 12,
            weight: 600,
            family: 'Inter, system-ui, sans-serif',
          },
          padding: 12,
        },
        border: {
          color: '#e5e7eb',
          width: 2,
        },
        beginAtZero: true,
      },
    },
  };

  // Donut chart specific options
  const donutOptions = {
    ...modernChartOptions,
    scales: undefined,
    layout: {
      padding: {
        top: 10,
        bottom: 10,
        left: 10,
        right: 20,
      },
    },
    plugins: {
      ...modernChartOptions.plugins,
      legend: {
        ...modernChartOptions.plugins.legend,
        position: 'right',
        align: 'center',
        labels: {
          ...modernChartOptions.plugins.legend.labels,
          padding: 12,
          boxWidth: 12,
          boxHeight: 12,
          font: {
            size: 11,
            weight: 600,
            family: 'Inter, system-ui, sans-serif',
          },
          generateLabels: function(chart) {
            const data = chart.data;
            if (data.labels.length && data.datasets.length) {
              return data.labels.map((label, i) => {
                const dataset = data.datasets[0];
                const value = dataset.data[i];
                const total = dataset.data.reduce((a, b) => a + b, 0);
                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0';
                // Truncate long labels to prevent overflow
                const truncatedLabel = label.length > 15 ? label.substring(0, 15) + '...' : label;
                return {
                  text: `${truncatedLabel}: ${value} (${percentage}%)`,
                  fillStyle: dataset.backgroundColor[i],
                  strokeStyle: dataset.borderColor,
                  lineWidth: dataset.borderWidth,
                  hidden: false,
                  index: i
                };
              });
            }
            return [];
          }
        }
      }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Box>
        {/* Modern Animated Key Metrics Row */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6} sm={3}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.02, y: -4 }}>
              <Card sx={{
                p: 2,
                textAlign: 'center',
                background: `linear-gradient(135deg, ${modernColors.error}15 0%, ${modernColors.error}25 100%)`,
                border: `2px solid ${modernColors.error}30`,
                borderRadius: 3,
                boxShadow: '0 8px 32px rgba(220, 38, 38, 0.15)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                minHeight: 120,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                position: 'relative',
                '&:hover': {
                  boxShadow: '0 12px 40px rgba(220, 38, 38, 0.25)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <ReportIcon sx={{
                  position: 'absolute',
                  top: 8,
                  left: 8,
                  fontSize: 20,
                  color: modernColors.error,
                  opacity: 0.7
                }} />
                <Typography variant="h4" sx={{
                  color: modernColors.error,
                  fontWeight: 700,
                  fontSize: { xs: '1.5rem', sm: '2rem' },
                  mb: 0.5
                }}>
                  {incidents_reported}
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.85rem'
                }}>
                  Total Incidents
                </Typography>
              </Card>
            </motion.div>
          </Grid>
          <Grid item xs={6} sm={3}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.02, y: -4 }}>
              <Card sx={{
                p: 2,
                textAlign: 'center',
                background: `linear-gradient(135deg, ${modernColors.warning}15 0%, ${modernColors.warning}25 100%)`,
                border: `2px solid ${modernColors.warning}30`,
                borderRadius: 3,
                boxShadow: '0 8px 32px rgba(217, 119, 6, 0.15)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                minHeight: 120,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                position: 'relative',
                '&:hover': {
                  boxShadow: '0 12px 40px rgba(217, 119, 6, 0.25)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <ErrorOutlineIcon sx={{
                  position: 'absolute',
                  top: 8,
                  left: 8,
                  fontSize: 20,
                  color: modernColors.warning,
                  opacity: 0.7
                }} />
                <Typography variant="h4" sx={{
                  color: modernColors.warning,
                  fontWeight: 700,
                  fontSize: { xs: '1.5rem', sm: '2rem' },
                  mb: 0.5
                }}>
                  {open_incidents}
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.85rem'
                }}>
                  Open
                </Typography>
              </Card>
            </motion.div>
          </Grid>
          <Grid item xs={6} sm={3}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.02, y: -4 }}>
              <Card sx={{
                p: 2,
                textAlign: 'center',
                background: `linear-gradient(135deg, ${modernColors.success}15 0%, ${modernColors.success}25 100%)`,
                border: `2px solid ${modernColors.success}30`,
                borderRadius: 3,
                boxShadow: '0 8px 32px rgba(5, 150, 105, 0.15)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                minHeight: 120,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                position: 'relative',
                '&:hover': {
                  boxShadow: '0 12px 40px rgba(5, 150, 105, 0.25)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <CheckCircleIcon sx={{
                  position: 'absolute',
                  top: 8,
                  left: 8,
                  fontSize: 20,
                  color: modernColors.success,
                  opacity: 0.7
                }} />
                <Typography variant="h4" sx={{
                  color: modernColors.success,
                  fontWeight: 700,
                  fontSize: { xs: '1.5rem', sm: '2rem' },
                  mb: 0.5
                }}>
                  {closed_incidents}
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.85rem'
                }}>
                  Closed
                </Typography>
              </Card>
            </motion.div>
          </Grid>
          <Grid item xs={6} sm={3}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.02, y: -4 }}>
              <Card sx={{
                p: 2,
                textAlign: 'center',
                background: `linear-gradient(135deg, ${modernColors.error}15 0%, ${modernColors.error}25 100%)`,
                border: `2px solid ${modernColors.error}30`,
                borderRadius: 3,
                boxShadow: '0 8px 32px rgba(220, 38, 38, 0.15)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                minHeight: 120,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                position: 'relative',
                '&:hover': {
                  boxShadow: '0 12px 40px rgba(220, 38, 38, 0.25)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <PersonIcon sx={{
                  position: 'absolute',
                  top: 8,
                  left: 8,
                  fontSize: 20,
                  color: modernColors.error,
                  opacity: 0.7
                }} />
                <Typography variant="h4" sx={{
                  color: modernColors.error,
                  fontWeight: 700,
                  fontSize: { xs: '1.5rem', sm: '2rem' },
                  mb: 0.5
                }}>
                  {people_injured}
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.85rem'
                }}>
                  Injured
                </Typography>
              </Card>
            </motion.div>
          </Grid>
        </Grid>

        {/* Modern Animated Charts Row */}
        <Grid container spacing={3}>
          {/* Enhanced Incident Trends */}
          <Grid item xs={12} md={6}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.01, y: -2 }}>
              <Card sx={{
                height: 380,
                background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                border: `2px solid ${modernColors.primary}20`,
                borderRadius: 4,
                boxShadow: '0 10px 40px rgba(30, 64, 175, 0.1)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                display: 'flex',
                flexDirection: 'column',
                '&:hover': {
                  boxShadow: '0 15px 50px rgba(30, 64, 175, 0.15)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <CardContent sx={{ p: 4, height: '100%' }}>
                  <Box sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    mb: 3,
                    pb: 2,
                    borderBottom: `2px solid ${modernColors.primary}15`
                  }}>
                    <Typography variant="h5" sx={{
                      fontWeight: 700,
                      color: '#111827',
                      fontSize: '1.4rem'
                    }}>
                      📈 Incident Trends
                    </Typography>
                    <FormControl size="small" sx={{ minWidth: 140 }}>
                      <InputLabel sx={{ fontWeight: 600 }}>Period</InputLabel>
                      <Select
                        value={trendPeriod}
                        label="Period"
                        onChange={(e) => setTrendPeriod(e.target.value)}
                        sx={{
                          borderRadius: 2,
                          '& .MuiOutlinedInput-notchedOutline': {
                            borderColor: modernColors.primary + '40',
                            borderWidth: 2,
                          },
                          '&:hover .MuiOutlinedInput-notchedOutline': {
                            borderColor: modernColors.primary,
                          },
                          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                            borderColor: modernColors.primary,
                          },
                        }}
                      >
                        <MenuItem value="weekly">📅 Weekly</MenuItem>
                        <MenuItem value="monthly">📊 Monthly</MenuItem>
                        <MenuItem value="yearly">📈 Yearly</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>
                  <Box sx={{ height: 280 }}>
                    <Line
                      ref={(ref) => registerChart('trendChart', ref)}
                      data={trendData}
                      options={modernChartOptions}
                    />
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Modern Incident Types Donut */}
          <Grid item xs={12} md={6}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.01, y: -2 }}>
              <Card sx={{
                height: 380,
                background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                border: `2px solid ${modernColors.secondary}20`,
                borderRadius: 4,
                boxShadow: '0 10px 40px rgba(124, 58, 237, 0.1)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  boxShadow: '0 15px 50px rgba(124, 58, 237, 0.15)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <CardContent sx={{ p: 4, height: '100%' }}>
                  <Typography variant="h5" sx={{
                    fontWeight: 700,
                    color: '#111827',
                    fontSize: '1.4rem',
                    mb: 3,
                    pb: 2,
                    borderBottom: `2px solid ${modernColors.secondary}15`
                  }}>
                    🎯 Incident Types
                  </Typography>
                  <Box sx={{ height: 280 }}>
                    <Doughnut
                      ref={(ref) => registerChart('typesChart', ref)}
                      data={typesData}
                      options={donutOptions}
                    />
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Enhanced Incidents by Location */}
          <Grid item xs={12}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.005, y: -2 }}>
              <Card sx={{
                height: 380,
                background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                border: `2px solid ${modernColors.info}20`,
                borderRadius: 4,
                boxShadow: '0 10px 40px rgba(2, 132, 199, 0.1)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  boxShadow: '0 15px 50px rgba(2, 132, 199, 0.15)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <CardContent sx={{ p: 4, height: '100%' }}>
                  <Typography variant="h5" sx={{
                    fontWeight: 700,
                    color: '#111827',
                    fontSize: '1.4rem',
                    mb: 3,
                    pb: 2,
                    borderBottom: `2px solid ${modernColors.info}15`
                  }}>
                    📍 Top Incident Locations
                  </Typography>
                  <Box sx={{ height: 280 }}>
                    <Bar
                      ref={(ref) => registerChart('locationsChart', ref)}
                      data={locationsData}
                      options={modernChartOptions}
                    />
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>
      </Box>
    </motion.div>
  );
};

export default IncidentCharts;
