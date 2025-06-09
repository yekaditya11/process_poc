/**
 * Modern Driver Safety Charts Component
 * Enhanced visualizations with animations and modern design
 */

import React from 'react';
import {
  Box,
  Grid,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  useTheme,
  Card,
  CardContent,
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  DirectionsCar as CarIcon,
  Build as BuildIcon,
  TrendingUp as TrendingUpIcon,
  Check as CheckIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import { motion } from 'framer-motion';

// Register Chart.js components
ChartJS.register(
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const DriverSafetyCharts = ({ data = {} }) => {
  const theme = useTheme();

  // Modern color palette
  const modernColors = {
    primary: '#1e40af',
    success: '#059669',
    warning: '#d97706',
    error: '#dc2626',
    info: '#0284c7',
    secondary: '#7c3aed',
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

  // Safety check for data
  if (!data || typeof data !== 'object') {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          No driver safety data available
        </Typography>
      </Box>
    );
  }

  // Extract data with fallbacks
  const {
    daily_completions = {},
    weekly_completions = {},
    vehicle_fitness = {},
    overdue_drivers = {},
  } = data;

  // Prepare completion data
  const dailyPercentage = daily_completions.completion_percentage || 0;
  const weeklyPercentage = weekly_completions.completion_percentage || 0;

  // Vehicle fitness data
  const fitVehicles = vehicle_fitness.fit_vehicles || 0;
  const unfitVehicles = vehicle_fitness.unfit_vehicles || 0;

  // Overdue drivers
  const overdueDriversList = overdue_drivers.overdue_drivers || [];
  const overdueCount = overdueDriversList.length;

  // Modern vehicle fitness donut chart data
  const vehicleFitnessData = {
    labels: ['Fit Vehicles', 'Unfit Vehicles'],
    datasets: [
      {
        data: [fitVehicles, unfitVehicles],
        backgroundColor: [
          modernColors.success,
          modernColors.error,
        ],
        borderColor: '#ffffff',
        borderWidth: 4,
        hoverBorderWidth: 6,
        hoverOffset: 8,
        cutout: '65%',
        spacing: 2,
        borderRadius: 8,
      },
    ],
  };

  // Modern donut chart options
  const modernDonutOptions = {
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
        top: 5,
        bottom: 5,
        left: 5,
        right: 5,
      },
    },
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 12,
          usePointStyle: true,
          pointStyle: 'circle',
          boxWidth: 10,
          boxHeight: 10,
          font: {
            size: 11,
            weight: 600,
            family: 'Inter, system-ui, sans-serif',
          },
          color: '#374151',
          generateLabels: function(chart) {
            const data = chart.data;
            if (data.labels.length && data.datasets.length) {
              return data.labels.map((label, i) => {
                const dataset = data.datasets[0];
                const value = dataset.data[i];
                const total = dataset.data.reduce((a, b) => a + b, 0);
                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0';
                return {
                  text: `${label}: ${value} (${percentage}%)`,
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
                background: `linear-gradient(135deg, ${modernColors.success}15 0%, ${modernColors.success}25 100%)`,
                border: `2px solid ${modernColors.success}30`,
                borderRadius: 3,
                boxShadow: '0 8px 32px rgba(5, 150, 105, 0.15)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                minHeight: 110,
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
                  fontSize: { xs: '1.5rem', sm: '1.8rem' },
                  mb: 0.5
                }}>
                  {Math.round(dailyPercentage)}%
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>
                  Daily Completion
                </Typography>
              </Card>
            </motion.div>
          </Grid>
          <Grid item xs={6} sm={3}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.02, y: -4 }}>
              <Card sx={{
                p: 2,
                textAlign: 'center',
                background: `linear-gradient(135deg, ${modernColors.primary}15 0%, ${modernColors.primary}25 100%)`,
                border: `2px solid ${modernColors.primary}30`,
                borderRadius: 3,
                boxShadow: '0 8px 32px rgba(30, 64, 175, 0.15)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                minHeight: 110,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                position: 'relative',
                '&:hover': {
                  boxShadow: '0 12px 40px rgba(30, 64, 175, 0.25)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <TrendingUpIcon sx={{
                  position: 'absolute',
                  top: 8,
                  left: 8,
                  fontSize: 20,
                  color: modernColors.primary,
                  opacity: 0.7
                }} />
                <Typography variant="h4" sx={{
                  color: modernColors.primary,
                  fontWeight: 700,
                  fontSize: { xs: '1.5rem', sm: '1.8rem' },
                  mb: 0.5
                }}>
                  {Math.round(weeklyPercentage)}%
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>
                  Weekly Completion
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
                minHeight: 110,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                position: 'relative',
                '&:hover': {
                  boxShadow: '0 12px 40px rgba(5, 150, 105, 0.25)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <CheckIcon sx={{
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
                  fontSize: { xs: '1.5rem', sm: '1.8rem' },
                  mb: 0.5
                }}>
                  {fitVehicles}
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>
                  Fit Vehicles
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
                minHeight: 110,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                position: 'relative',
                '&:hover': {
                  boxShadow: '0 12px 40px rgba(220, 38, 38, 0.25)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <ErrorIcon sx={{
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
                  fontSize: { xs: '1.5rem', sm: '1.8rem' },
                  mb: 0.5
                }}>
                  {unfitVehicles}
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>
                  Unfit Vehicles
                </Typography>
              </Card>
            </motion.div>
          </Grid>
        </Grid>



        {/* Modern Charts Section */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.01, y: -2 }}>
              <Card sx={{
                height: 340,
                background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                border: `2px solid ${modernColors.warning}20`,
                borderRadius: 4,
                boxShadow: '0 10px 40px rgba(217, 119, 6, 0.1)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                display: 'flex',
                flexDirection: 'column',
                '&:hover': {
                  boxShadow: '0 15px 50px rgba(217, 119, 6, 0.15)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <CardContent sx={{ p: 3, flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <Typography variant="h6" sx={{
                    fontWeight: 700,
                    color: '#111827',
                    fontSize: '1.1rem',
                    mb: 2,
                    pb: 1,
                    borderBottom: `2px solid ${modernColors.warning}15`
                  }}>
                    ⚠️ Overdue Drivers ({overdueCount})
                  </Typography>
                  <Box sx={{ height: 250, overflow: 'auto' }}>
                    {overdueDriversList.length > 0 ? (
                      <List dense>
                        {overdueDriversList.slice(0, 8).map((driver, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                          >
                            <ListItem sx={{
                              borderRadius: 2,
                              mb: 1,
                              bgcolor: `${modernColors.warning}08`,
                              border: `1px solid ${modernColors.warning}20`,
                              '&:hover': {
                                bgcolor: `${modernColors.warning}15`,
                                transform: 'translateX(4px)',
                                transition: 'all 0.2s ease',
                              }
                            }}>
                              <ListItemIcon>
                                <WarningIcon sx={{ color: modernColors.warning }} />
                              </ListItemIcon>
                              <ListItemText
                                primary={
                                  <Typography sx={{ fontWeight: 600, color: '#374151' }}>
                                    {driver.name || `Driver ${index + 1}`}
                                  </Typography>
                                }
                                secondary={
                                  <Typography sx={{ color: modernColors.warning, fontWeight: 500 }}>
                                    Overdue: {driver.days_overdue || 'N/A'} days
                                  </Typography>
                                }
                              />
                            </ListItem>
                          </motion.div>
                        ))}
                      </List>
                    ) : (
                      <Box
                        sx={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          justifyContent: 'center',
                          height: '100%',
                          color: 'text.secondary',
                        }}
                      >
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ type: "spring", stiffness: 260, damping: 20 }}
                        >
                          <CheckCircleIcon sx={{ fontSize: 64, mb: 2, color: modernColors.success }} />
                        </motion.div>
                        <Typography variant="h6" sx={{ fontWeight: 600, color: modernColors.success }}>
                          No overdue drivers
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Enhanced Vehicle Fitness Chart */}
          <Grid item xs={12} md={6}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.01, y: -2 }}>
              <Card sx={{
                height: 340,
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
                <CardContent sx={{ p: 3, height: '100%' }}>
                  <Typography variant="h6" sx={{
                    fontWeight: 700,
                    color: '#111827',
                    fontSize: '1.1rem',
                    mb: 2,
                    pb: 1,
                    borderBottom: `2px solid ${modernColors.info}15`
                  }}>
                    🚗 Vehicle Fitness Distribution
                  </Typography>
                  <Box sx={{ height: 250 }}>
                    <Doughnut
                      data={vehicleFitnessData}
                      options={modernDonutOptions}
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

export default DriverSafetyCharts;
