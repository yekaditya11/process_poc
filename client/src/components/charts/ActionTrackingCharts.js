/**
 * Modern Action Tracking Charts Component
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
  Card,
  CardContent,
} from '@mui/material';
import {
  Assignment as AssignmentIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  PlaylistAddCheck as PlaylistAddCheckIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  AccessTime as AccessTimeIcon,
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import { motion } from 'framer-motion';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const ActionTrackingCharts = ({ data = {} }) => {
  // Modern color palette
  const modernColors = {
    primary: '#1e40af',
    error: '#dc2626',
    warning: '#d97706',
    success: '#059669',
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
          No action tracking data available
        </Typography>
      </Box>
    );
  }

  // Extract data with fallbacks
  const {
    actions_created = {},
    on_time_completion = {},
    action_status = {},
    overdue_employees = {},
  } = data;

  // Actions data
  const totalActions = actions_created.total_actions || 0;
  const actionsThisPeriod = actions_created.actions_this_period || 0;

  // On-time completion data
  const onTimePercentage = on_time_completion.percentage || 0;
  const onTimeActions = on_time_completion.on_time_actions || 0;
  const lateActions = on_time_completion.late_actions || 0;

  // Status data
  const openActions = action_status.open_actions || 0;
  const closedActions = action_status.closed_actions || 0;
  const inProgressActions = action_status.in_progress_actions || 0;

  // Overdue employees
  const overdueEmployeesList = overdue_employees.overdue_employees || [];
  const overdueCount = overdueEmployeesList.length;

  // Modern status donut chart data
  const statusData = {
    labels: ['Open', 'In Progress', 'Closed'],
    datasets: [
      {
        data: [openActions, inProgressActions, closedActions],
        backgroundColor: [
          modernColors.warning,
          modernColors.info,
          modernColors.success,
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

  // Modern completion bar chart data
  const completionData = {
    labels: ['On Time', 'Late'],
    datasets: [
      {
        label: 'Action Completion',
        data: [onTimeActions, lateActions],
        backgroundColor: [
          modernColors.success,
          modernColors.error,
        ],
        borderColor: [
          modernColors.success,
          modernColors.error,
        ],
        borderWidth: 0,
        borderRadius: 8,
        borderSkipped: false,
        hoverBackgroundColor: [
          modernColors.success,
          modernColors.error,
        ],
        hoverBorderWidth: 2,
      },
    ],
  };

  // Modern chart options
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
          boxWidth: 8,
          boxHeight: 8,
          font: {
            size: 11,
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

  // Modern donut chart options
  const modernDonutOptions = {
    ...modernChartOptions,
    scales: undefined,
    layout: {
      padding: {
        top: 5,
        bottom: 5,
        left: 5,
        right: 15,
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
          padding: 10,
          boxWidth: 10,
          boxHeight: 10,
          font: {
            size: 10,
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
                <PlaylistAddCheckIcon sx={{
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
                  {totalActions}
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>
                  Total Actions
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
                minHeight: 110,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                position: 'relative',
                '&:hover': {
                  boxShadow: '0 12px 40px rgba(217, 119, 6, 0.25)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <RadioButtonUncheckedIcon sx={{
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
                  fontSize: { xs: '1.5rem', sm: '1.8rem' },
                  mb: 0.5
                }}>
                  {openActions}
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.8rem'
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
                  {Math.round(onTimePercentage)}%
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>
                  On Time
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
                <AccessTimeIcon sx={{
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
                  {overdueCount}
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>
                  Overdue
                </Typography>
              </Card>
            </motion.div>
          </Grid>
        </Grid>

        {/* Modern Progress Indicator */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.005, y: -2 }}>
              <Card sx={{
                p: 3,
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
                <Typography variant="h6" sx={{
                  fontWeight: 700,
                  color: '#111827',
                  fontSize: '1.2rem',
                  mb: 2,
                  pb: 1,
                  borderBottom: `2px solid ${modernColors.info}15`
                }}>
                  📊 On-Time Completion Performance
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body1" sx={{ fontWeight: 600, color: '#374151' }}>Completion Rate</Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: modernColors.primary }}>{Math.round(onTimePercentage)}%</Typography>
                </Box>
                <Box sx={{
                  height: 12,
                  bgcolor: '#f1f5f9',
                  borderRadius: 3,
                  position: 'relative',
                  overflow: 'hidden',
                  border: `2px solid ${modernColors.info}20`,
                }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${onTimePercentage}%` }}
                    transition={{ duration: 1.5, ease: "easeInOut" }}
                    style={{
                      height: '100%',
                      background: onTimePercentage >= 80
                        ? `linear-gradient(90deg, ${modernColors.success} 0%, #10b981 100%)`
                        : onTimePercentage >= 60
                        ? `linear-gradient(90deg, ${modernColors.warning} 0%, #f59e0b 100%)`
                        : `linear-gradient(90deg, ${modernColors.error} 0%, #ef4444 100%)`,
                      borderRadius: '2px',
                    }}
                  />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                  <Typography variant="body2" sx={{ color: modernColors.success, fontWeight: 600 }}>
                    ✅ {onTimeActions} on time
                  </Typography>
                  <Typography variant="body2" sx={{ color: modernColors.error, fontWeight: 600 }}>
                    ⏰ {lateActions} late
                  </Typography>
                </Box>
              </Card>
            </motion.div>
          </Grid>
        </Grid>

        {/* Modern Charts Section */}
        <Grid container spacing={3}>
          {/* Enhanced Action Status Donut */}
          <Grid item xs={12} md={6}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.01, y: -2 }}>
              <Card sx={{
                height: 340,
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
                <CardContent sx={{ p: 3, height: '100%' }}>
                  <Typography variant="h6" sx={{
                    fontWeight: 700,
                    color: '#111827',
                    fontSize: '1.1rem',
                    mb: 2,
                    pb: 1,
                    borderBottom: `2px solid ${modernColors.secondary}15`
                  }}>
                    🎯 Action Status Distribution
                  </Typography>
                  <Box sx={{ height: 250 }}>
                    <Doughnut
                      data={statusData}
                      options={modernDonutOptions}
                    />
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Enhanced Completion Performance */}
          <Grid item xs={12} md={6}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.01, y: -2 }}>
              <Card sx={{
                height: 340,
                background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                border: `2px solid ${modernColors.primary}20`,
                borderRadius: 4,
                boxShadow: '0 10px 40px rgba(30, 64, 175, 0.1)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  boxShadow: '0 15px 50px rgba(30, 64, 175, 0.15)',
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
                    borderBottom: `2px solid ${modernColors.primary}15`
                  }}>
                    📈 Completion Performance
                  </Typography>
                  <Box sx={{ height: 250 }}>
                    <Bar
                      data={completionData}
                      options={modernChartOptions}
                    />
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Enhanced Overdue Employees */}
          <Grid item xs={12}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.005, y: -2 }}>
              <Card sx={{
                background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                border: `2px solid ${modernColors.error}20`,
                borderRadius: 4,
                boxShadow: '0 10px 40px rgba(220, 38, 38, 0.1)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  boxShadow: '0 15px 50px rgba(220, 38, 38, 0.15)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{
                    fontWeight: 700,
                    color: '#111827',
                    fontSize: '1.1rem',
                    mb: 2,
                    pb: 1,
                    borderBottom: `2px solid ${modernColors.error}15`
                  }}>
                    ⚠️ Overdue Employees ({overdueCount})
                  </Typography>
                  <Box sx={{ height: 250, overflow: 'auto' }}>
                    {overdueEmployeesList.length > 0 ? (
                      <List dense>
                        {overdueEmployeesList.slice(0, 8).map((employee, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                          >
                            <ListItem sx={{
                              borderRadius: 2,
                              mb: 1,
                              bgcolor: `${modernColors.error}08`,
                              border: `1px solid ${modernColors.error}20`,
                              '&:hover': {
                                bgcolor: `${modernColors.error}15`,
                                transform: 'translateX(4px)',
                                transition: 'all 0.2s ease',
                              }
                            }}>
                              <ListItemIcon>
                                <WarningIcon sx={{ color: modernColors.error }} />
                              </ListItemIcon>
                              <ListItemText
                                primary={
                                  <Typography sx={{ fontWeight: 600, color: '#374151' }}>
                                    {employee.name || `Employee ${index + 1}`}
                                  </Typography>
                                }
                                secondary={
                                  <Box>
                                    <Typography variant="body2" component="span" sx={{ color: modernColors.error, fontWeight: 500 }}>
                                      {employee.overdue_actions || 1} overdue actions
                                    </Typography>
                                    {employee.days_overdue && (
                                      <Typography variant="body2" component="span" sx={{ ml: 1, color: modernColors.error, fontWeight: 500 }}>
                                        • {employee.days_overdue} days overdue
                                      </Typography>
                                    )}
                                  </Box>
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
                          color: '#64748b',
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
                          No overdue employees
                        </Typography>
                      </Box>
                    )}
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

export default ActionTrackingCharts;
