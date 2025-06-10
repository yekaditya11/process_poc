/**
 * Modern Observation Tracker Charts Component
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
  useTheme,
  Card,
  CardContent,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  CheckCircle as CheckCircleIcon,
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

const ObservationCharts = ({ data = {} }) => {
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
          No observation data available
        </Typography>
      </Box>
    );
  }

  // Extract data with fallbacks
  const {
    observations_by_area = {},
    observation_status = {},
    observation_priority = {},
    observations_remarks_insight = {},
  } = data;

  // Area data
  const areaObservations = observations_by_area.observations_by_area || {};
  const totalObservations = observations_by_area.total_observations || 0;
  const totalAreas = observations_by_area.total_areas || 0;

  // Status data
  const openObservations = observation_status.open_observations || 0;
  const closedObservations = observation_status.closed_observations || 0;

  // Priority data
  const priorityObservations = observation_priority.observations_by_priority || {};

  // Remarks data
  const totalRemarks = observations_remarks_insight.total_remarks || 0;
  const topRemarks = observations_remarks_insight.top_remarks || [];

  // Modern area chart data (top 10 areas)
  const areaEntries = Object.entries(areaObservations).slice(0, 10);
  const areaData = {
    labels: areaEntries.map(([area]) => area),
    datasets: [
      {
        label: 'Observations by Area',
        data: areaEntries.map(([, count]) => count),
        backgroundColor: modernColors.warning,
        borderColor: modernColors.warning,
        borderWidth: 0,
        borderRadius: 8,
        borderSkipped: false,
        hoverBackgroundColor: modernColors.error,
        hoverBorderColor: modernColors.error,
        hoverBorderWidth: 2,
      },
    ],
  };

  // Modern priority donut chart data
  const priorityEntries = Object.entries(priorityObservations);
  const priorityData = {
    labels: priorityEntries.map(([priority]) => priority),
    datasets: [
      {
        data: priorityEntries.map(([, count]) => count),
        backgroundColor: [
          modernColors.error,
          modernColors.warning,
          modernColors.info,
          modernColors.success,
          modernColors.secondary,
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

  // Donut chart specific options
  const donutOptions = {
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
                <VisibilityIcon sx={{
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
                  {totalObservations}
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>
                  Total Observations
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
                <RadioButtonUncheckedIcon sx={{
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
                  {openObservations}
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
                  {closedObservations}
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.8rem'
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
                background: `linear-gradient(135deg, ${modernColors.info}15 0%, ${modernColors.info}25 100%)`,
                border: `2px solid ${modernColors.info}30`,
                borderRadius: 3,
                boxShadow: '0 8px 32px rgba(2, 132, 199, 0.15)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                minHeight: 110,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                position: 'relative',
                '&:hover': {
                  boxShadow: '0 12px 40px rgba(2, 132, 199, 0.25)',
                  transform: 'translateY(-2px)',
                }
              }}>
                <AccessTimeIcon sx={{
                  position: 'absolute',
                  top: 8,
                  left: 8,
                  fontSize: 20,
                  color: modernColors.info,
                  opacity: 0.7
                }} />
                <Typography variant="h4" sx={{
                  color: modernColors.info,
                  fontWeight: 700,
                  fontSize: { xs: '1.5rem', sm: '1.8rem' },
                  mb: 0.5
                }}>
                  {totalAreas}
                </Typography>
                <Typography variant="body2" sx={{
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>
                  Areas
                </Typography>
              </Card>
            </motion.div>
          </Grid>
        </Grid>

        {/* Modern Charts Section */}
        <Grid container spacing={3}>
          {/* Enhanced Observations by Area */}
          <Grid item xs={12} md={4}>
            <motion.div variants={cardVariants} whileHover={{ scale: 1.01, y: -2 }}>
              <Card sx={{
                height: 340,
                background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                border: `2px solid ${modernColors.warning}20`,
                borderRadius: 4,
                boxShadow: '0 10px 40px rgba(217, 119, 6, 0.1)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  boxShadow: '0 15px 50px rgba(217, 119, 6, 0.15)',
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
                    borderBottom: `2px solid ${modernColors.warning}15`
                  }}>
                    📊 Observations by Area
                  </Typography>
                  <Box sx={{ height: 250 }}>
                    {areaEntries.length > 0 ? (
                      <Bar data={areaData} options={modernChartOptions} />
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
                        <Typography variant="h6" sx={{ fontWeight: 600, color: '#6b7280', mb: 1 }}>
                          No area data available
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#9ca3af', textAlign: 'center' }}>
                          {closedObservations > 0
                            ? `${closedObservations} observations submitted but no location data provided`
                            : 'No observations have been submitted yet'
                          }
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Enhanced Priority Breakdown Donut */}
          <Grid item xs={12} md={4}>
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
                    🎯 Priority Breakdown
                  </Typography>
                  <Box sx={{ height: 250 }}>
                    {priorityEntries.length > 0 ? (
                      <Doughnut data={priorityData} options={donutOptions} />
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
                        <Typography variant="h6" sx={{ fontWeight: 600, color: '#6b7280', mb: 1 }}>
                          No priority data available
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#9ca3af', textAlign: 'center' }}>
                          {closedObservations > 0
                            ? `${closedObservations} observations submitted but no severity data provided`
                            : 'No observations have been submitted yet'
                          }
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Enhanced Top Remarks */}
          <Grid item xs={12} md={4}>
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
                    💬 Top Remarks ({totalRemarks} total)
                  </Typography>
                  <Box sx={{ height: 250, overflow: 'auto' }}>
                    {topRemarks.length > 0 ? (
                      <List dense>
                        {topRemarks.slice(0, 6).map((remark, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                          >
                            <ListItem sx={{
                              borderRadius: 2,
                              mb: 1,
                              bgcolor: `${modernColors.info}08`,
                              border: `1px solid ${modernColors.info}20`,
                              '&:hover': {
                                bgcolor: `${modernColors.info}15`,
                                transform: 'translateX(4px)',
                                transition: 'all 0.2s ease',
                              }
                            }}>
                              <ListItemText
                                primary={
                                  <Typography sx={{ fontWeight: 600, color: '#374151' }}>
                                    {remark.remark || remark}
                                  </Typography>
                                }
                                secondary={
                                  typeof remark === 'object' ? (
                                    <Typography sx={{ color: modernColors.info, fontWeight: 500 }}>
                                      Count: {remark.count || 1}
                                    </Typography>
                                  ) : undefined
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
                        <Typography variant="h6" sx={{ fontWeight: 600, color: '#6b7280', mb: 1 }}>
                          No remarks available
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#9ca3af', textAlign: 'center' }}>
                          {closedObservations > 0
                            ? `${closedObservations} observations submitted but no description data provided`
                            : 'No observations have been submitted yet'
                          }
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

export default ObservationCharts;
