/**
 * Equipment Asset Charts Component
 * Displays equipment asset management KPIs and visualizations
 */

import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Build as BuildIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Error as ErrorIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip as ChartTooltip,
  Legend as ChartLegend,
  ArcElement,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import { motion } from 'framer-motion';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  ChartTooltip,
  ChartLegend,
  ArcElement
);

const EquipmentAssetCharts = ({ data }) => {
  const theme = useTheme();

  // Safely extract data with fallbacks
  const summaryMetrics = data?.summary_metrics || {};
  const calibrationCerts = data?.calibration_certificates || {};
  const calibrationExpiry = data?.calibration_expiry || {};
  const inspectionCompletion = data?.inspection_completion || {};
  const equipmentTypes = data?.equipment_types_and_counts || {};
  const insights = data?.equipment_insights || {};

  // Modern color palette for charts
  const colors = {
    primary: '#1e40af',
    success: '#059669',
    warning: '#d97706',
    error: '#dc2626',
    info: '#0284c7',
    secondary: '#7c3aed',
  };

  // Prepare data for calibration certificate pie chart
  const calibrationData = [
    {
      name: 'Valid Certificates',
      value: calibrationCerts.equipment_with_valid_certificates || 0,
      color: colors.success,
    },
    {
      name: 'Invalid Certificates',
      value: calibrationCerts.equipment_without_valid_certificates || 0,
      color: colors.error,
    },
    {
      name: 'Missing Info',
      value: calibrationCerts.equipment_with_missing_certificate_info || 0,
      color: colors.warning,
    },
  ];

  // Prepare data for inspection completion by type
  const inspectionByType = Object.entries(inspectionCompletion.inspection_completion_by_type || {}).map(
    ([type, data]) => ({
      name: type,
      completed: data.completion_percentage || 0,
      pending: 100 - (data.completion_percentage || 0),
      total: data.total_equipment || 0,
    })
  );

  // Prepare data for equipment types distribution
  const equipmentTypesData = Object.entries(equipmentTypes.equipment_by_asset_type || {}).map(
    ([type, count]) => ({
      name: type,
      count: count,
      color: colors.primary,
    })
  );

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.95 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] }
    }
  };

  const StatCard = ({ title, value, icon, color = 'primary' }) => (
    <motion.div
      variants={itemVariants}
      whileHover={{
        scale: 1.02,
        y: -4,
        transition: { duration: 0.2 }
      }}
    >
      <Card sx={{
        p: 2,
        textAlign: 'center',
        background: `linear-gradient(135deg, ${colors[color]}15 0%, ${colors[color]}25 100%)`,
        border: `2px solid ${colors[color]}30`,
        borderRadius: 3,
        boxShadow: `0 8px 32px ${colors[color]}15`,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        minHeight: 110,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        position: 'relative',
        '&:hover': {
          boxShadow: `0 12px 40px ${colors[color]}25`,
          transform: 'translateY(-2px)',
        }
      }}>
        {React.cloneElement(icon, {
          sx: {
            position: 'absolute',
            top: 8,
            left: 8,
            fontSize: 20,
            color: colors[color],
            opacity: 0.7
          }
        })}
        <Typography variant="h4" sx={{
          color: colors[color],
          fontWeight: 700,
          fontSize: { xs: '1.5rem', sm: '1.8rem' },
          mb: 0.5
        }}>
          {value}
        </Typography>
        <Typography variant="body2" sx={{
          color: '#374151',
          fontWeight: 600,
          fontSize: '0.8rem'
        }}>
          {title}
        </Typography>
      </Card>
    </motion.div>
  );

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Grid container spacing={2}>
      {/* Summary Statistics */}
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Total Equipment"
          value={summaryMetrics.total_equipment || 0}
          icon={<BuildIcon />}
          color="primary"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Valid Certificates"
          value={`${Math.round(summaryMetrics.percentage_with_valid_certificates || 0)}%`}
          icon={<CheckCircleIcon />}
          color="success"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Expired Calibrations"
          value={`${Math.round(summaryMetrics.percentage_expired_calibrations || 0)}%`}
          icon={<ErrorIcon />}
          color="error"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Completed Inspections"
          value={`${Math.round(summaryMetrics.percentage_completed_inspections || 0)}%`}
          icon={<AssignmentIcon />}
          color="info"
        />
      </Grid>

      {/* Charts Section */}
      <Grid item xs={12} sx={{ mt: 2 }}>
        <Grid container spacing={3}>
      {/* Enhanced Calibration Certificate Status */}
      <Grid item xs={12} md={6}>
        <motion.div variants={itemVariants} whileHover={{ scale: 1.01, y: -2 }}>
          <Card sx={{
            height: 340,
            background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            border: `2px solid ${colors.success}20`,
            borderRadius: 4,
            boxShadow: '0 10px 40px rgba(5, 150, 105, 0.1)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            display: 'flex',
            flexDirection: 'column',
            '&:hover': {
              boxShadow: '0 15px 50px rgba(5, 150, 105, 0.15)',
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
                borderBottom: `2px solid ${colors.success}15`
              }}>
                📋 Calibration Certificate Status
              </Typography>
              <Box sx={{ flex: 1, height: 250 }}>
                <Doughnut
                  data={{
                    labels: calibrationData.map(item => item.name),
                    datasets: [{
                      data: calibrationData.map(item => item.value),
                      backgroundColor: calibrationData.map(item => item.color),
                      borderColor: '#ffffff',
                      borderWidth: 2,
                      hoverBorderWidth: 3,
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {
                      padding: {
                        top: 5,
                        bottom: 5,
                        left: 5,
                        right: 15,
                      },
                    },
                    plugins: {
                      legend: {
                        position: 'right',
                        align: 'center',
                        labels: {
                          padding: 10,
                          usePointStyle: true,
                          pointStyle: 'circle',
                          boxWidth: 10,
                          boxHeight: 10,
                          font: {
                            size: 10,
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
                        }
                      },
                      tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#ffffff',
                        bodyColor: '#e5e7eb',
                        borderColor: colors.success,
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
                    animation: {
                      duration: 1500,
                      easing: 'easeInOutQuart',
                    },
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      </Grid>

      {/* Enhanced Equipment Types Distribution */}
      <Grid item xs={12} md={6}>
        <motion.div variants={itemVariants} whileHover={{ scale: 1.01, y: -2 }}>
          <Card sx={{
            height: 340,
            background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            border: `2px solid ${colors.primary}20`,
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
                borderBottom: `2px solid ${colors.primary}15`
              }}>
                🔧 Equipment Types Distribution
              </Typography>
              <Box sx={{ height: 250 }}>
                <Bar
                  data={{
                    labels: equipmentTypesData.map(item => item.name),
                    datasets: [{
                      label: 'Equipment Count',
                      data: equipmentTypesData.map(item => item.count),
                      backgroundColor: colors.primary,
                      borderColor: colors.primary,
                      borderWidth: 1,
                      borderRadius: 4,
                      borderSkipped: false,
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
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
                        borderColor: colors.primary,
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
                      y: {
                        beginAtZero: true,
                        grid: {
                          color: '#f3f4f6',
                          drawBorder: false,
                        },
                        ticks: {
                          color: '#6b7280',
                          font: {
                            size: 11,
                            weight: 600,
                            family: 'Inter, system-ui, sans-serif',
                          },
                        },
                      },
                      x: {
                        grid: {
                          display: false,
                        },
                        ticks: {
                          color: '#6b7280',
                          font: {
                            size: 11,
                            weight: 600,
                            family: 'Inter, system-ui, sans-serif',
                          },
                        },
                      },
                    },
                    animation: {
                      duration: 1500,
                      easing: 'easeInOutQuart',
                    },
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      </Grid>

      {/* Enhanced Inspection Completion by Type */}
      <Grid item xs={12} md={8}>
        <motion.div variants={itemVariants} whileHover={{ scale: 1.005, y: -2 }}>
          <Card sx={{
            height: 340,
            background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            border: `2px solid ${colors.info}20`,
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
                borderBottom: `2px solid ${colors.info}15`
              }}>
                📊 Inspection Completion by Equipment Type
              </Typography>
              <Box sx={{ height: 250 }}>
                <Bar
                  data={{
                    labels: inspectionByType.map(item => item.name),
                    datasets: [
                      {
                        label: 'Completed %',
                        data: inspectionByType.map(item => item.completed),
                        backgroundColor: colors.success,
                        borderColor: colors.success,
                        borderWidth: 1,
                        borderRadius: 4,
                        borderSkipped: false,
                      },
                      {
                        label: 'Pending %',
                        data: inspectionByType.map(item => item.pending),
                        backgroundColor: colors.warning,
                        borderColor: colors.warning,
                        borderWidth: 1,
                        borderRadius: 4,
                        borderSkipped: false,
                      }
                    ]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
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
                        borderColor: colors.info,
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
                      y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                          color: '#f3f4f6',
                          drawBorder: false,
                        },
                        ticks: {
                          color: '#6b7280',
                          font: {
                            size: 11,
                            weight: 600,
                            family: 'Inter, system-ui, sans-serif',
                          },
                          callback: function(value) {
                            return value + '%';
                          }
                        },
                      },
                      x: {
                        grid: {
                          display: false,
                        },
                        ticks: {
                          color: '#6b7280',
                          font: {
                            size: 11,
                            weight: 600,
                            family: 'Inter, system-ui, sans-serif',
                          },
                        },
                      },
                    },
                    animation: {
                      duration: 1500,
                      easing: 'easeInOutQuart',
                    },
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      </Grid>

      {/* Enhanced Equipment Needing Attention */}
      <Grid item xs={12} md={4}>
        <motion.div variants={itemVariants} whileHover={{ scale: 1.01, y: -2 }}>
          <Card sx={{
            height: 340,
            background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            border: `2px solid ${colors.warning}20`,
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
                borderBottom: `2px solid ${colors.warning}15`
              }}>
                ⚠️ Equipment Needing Attention
              </Typography>
              <Box sx={{ mb: 1.5, textAlign: 'center' }}>
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 260, damping: 20 }}
                >
                  <Typography variant="h3" sx={{
                    color: colors.warning,
                    fontWeight: 700,
                    fontSize: '2rem', // Reduced from 2.5rem
                    mb: 0.3 // Reduced margin
                  }}>
                    {insights.total_equipment_needing_attention || 0}
                  </Typography>
                </motion.div>
                <Typography variant="body2" sx={{ // Changed from body1 to body2
                  color: '#374151',
                  fontWeight: 600,
                  fontSize: '0.85rem' // Smaller font size
                }}>
                  Equipment requiring attention
                </Typography>
              </Box>

              <List dense sx={{
                maxHeight: 200,
                overflow: 'auto',
                py: 0,
                '&::-webkit-scrollbar': {
                  width: '4px',
                },
                '&::-webkit-scrollbar-track': {
                  background: '#f1f1f1',
                },
                '&::-webkit-scrollbar-thumb': {
                  background: colors.warning,
                  borderRadius: '2px',
                },
              }}>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 }}
                >
                  <ListItem sx={{
                    borderRadius: 2,
                    mb: 0.5, // Reduced margin
                    py: 0.5, // Reduced padding
                    bgcolor: `${colors.error}08`,
                    border: `1px solid ${colors.error}20`,
                    '&:hover': {
                      bgcolor: `${colors.error}15`,
                      transform: 'translateX(4px)',
                      transition: 'all 0.2s ease',
                    }
                  }}>
                    <ListItemIcon sx={{ minWidth: 32 }}> {/* Reduced icon space */}
                      <WarningIcon sx={{ color: colors.error, fontSize: 18 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography sx={{ fontWeight: 600, color: '#374151', fontSize: '0.85rem' }}>
                          Not Inspected Recently
                        </Typography>
                      }
                      secondary={
                        <Typography sx={{ color: colors.error, fontWeight: 500, fontSize: '0.75rem' }}>
                          {insights.equipment_not_inspected_recently?.length || 0} equipment
                        </Typography>
                      }
                    />
                  </ListItem>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <ListItem sx={{
                    borderRadius: 2,
                    mb: 0.5, // Reduced margin
                    py: 0.5, // Reduced padding
                    bgcolor: `${colors.warning}08`,
                    border: `1px solid ${colors.warning}20`,
                    '&:hover': {
                      bgcolor: `${colors.warning}15`,
                      transform: 'translateX(4px)',
                      transition: 'all 0.2s ease',
                    }
                  }}>
                    <ListItemIcon sx={{ minWidth: 32 }}> {/* Reduced icon space */}
                      <ErrorIcon sx={{ color: colors.warning, fontSize: 18 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography sx={{ fontWeight: 600, color: '#374151', fontSize: '0.85rem' }}>
                          Missing Certificates
                        </Typography>
                      }
                      secondary={
                        <Typography sx={{ color: colors.warning, fontWeight: 500, fontSize: '0.75rem' }}>
                          {insights.equipment_without_proper_certificates?.length || 0} equipment
                        </Typography>
                      }
                    />
                  </ListItem>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <ListItem sx={{
                    borderRadius: 2,
                    mb: 0.5, // Reduced margin
                    py: 0.5, // Reduced padding
                    bgcolor: `${colors.error}08`,
                    border: `1px solid ${colors.error}20`,
                    '&:hover': {
                      bgcolor: `${colors.error}15`,
                      transform: 'translateX(4px)',
                      transition: 'all 0.2s ease',
                    }
                  }}>
                    <ListItemIcon sx={{ minWidth: 32 }}> {/* Reduced icon space */}
                      <BuildIcon sx={{ color: colors.error, fontSize: 18 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography sx={{ fontWeight: 600, color: '#374151', fontSize: '0.85rem' }}>
                          With Anomalies
                        </Typography>
                      }
                      secondary={
                        <Typography sx={{ color: colors.error, fontWeight: 500, fontSize: '0.75rem' }}>
                          {insights.equipment_with_anomalies?.length || 0} equipment
                        </Typography>
                      }
                    />
                  </ListItem>
                </motion.div>
              </List>
            </CardContent>
          </Card>
        </motion.div>
      </Grid>
      </Grid>
        </Grid>
      </Grid>
    </motion.div>
  );
};

export default EquipmentAssetCharts;
