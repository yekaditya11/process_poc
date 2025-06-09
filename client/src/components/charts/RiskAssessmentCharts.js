/**
 * Risk Assessment Charts Component
 * Displays risk assessment KPIs and visualizations
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
import { motion } from 'framer-motion';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Assessment as AssessmentIcon,
  Security as SecurityIcon,
  TrendingUp as TrendingUpIcon,
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
  PointElement,
  LineElement,
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const RiskAssessmentCharts = ({ data }) => {
  if (!data) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No risk assessment data available
        </Typography>
      </Box>
    );
  }

  // Modern color palette
  const modernColors = {
    primary: '#1e40af',
    error: '#dc2626',
    warning: '#d97706',
    success: '#059669',
    info: '#0284c7',
    secondary: '#7c3aed',
  };

  // Helper function to get risk level color
  const getRiskLevelColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'very_low':
      case 'low':
        return modernColors.success;
      case 'medium':
        return modernColors.warning;
      case 'high':
      case 'very_high':
        return modernColors.error;
      default:
        return '#6b7280';
    }
  };

  // Severity Analysis Chart - using actual API structure
  const severityDistribution = data.severity_analysis?.initial_severity?.distribution || {};
  const severityChartData = {
    labels: Object.keys(severityDistribution),
    datasets: [
      {
        label: 'Initial Severity Distribution',
        data: Object.values(severityDistribution),
        backgroundColor: [
          modernColors.success,
          modernColors.info,
          modernColors.warning,
          modernColors.error,
          '#991b1b',
        ],
        borderColor: '#ffffff',
        borderWidth: 4,
        hoverBorderWidth: 6,
        hoverOffset: 8,
        borderRadius: 8,
      },
    ],
  };

  // Likelihood Analysis Chart - using actual API structure
  const likelihoodDistribution = data.likelihood_analysis?.initial_likelihood?.distribution || {};
  const likelihoodChartData = {
    labels: Object.keys(likelihoodDistribution),
    datasets: [
      {
        label: 'Initial Likelihood Distribution',
        data: Object.values(likelihoodDistribution),
        backgroundColor: [
          modernColors.success,
          modernColors.info,
          modernColors.warning,
          modernColors.error,
          '#991b1b',
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

  // Hazard Effects Chart - using actual API structure
  const hazardEffectsDistribution = data.hazard_effects?.effects_distribution || {};
  const hazardEffectsData = {
    labels: Object.keys(hazardEffectsDistribution).map(key => `${key} (${hazardEffectsDistribution[key]?.meaning || key})`),
    datasets: [
      {
        label: 'Hazard Effects Count',
        data: Object.keys(hazardEffectsDistribution).map(key => hazardEffectsDistribution[key]?.count || 0),
        backgroundColor: [
          modernColors.error,      // P - People
          modernColors.success,    // E - Environment
          modernColors.warning,    // A - Assets
          modernColors.info,       // R - Reputation
        ],
        borderColor: modernColors.primary,
        borderWidth: 0,
        borderRadius: 8,
        borderSkipped: false,
        hoverBackgroundColor: [
          modernColors.error,
          modernColors.success,
          modernColors.warning,
          modernColors.info,
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
          boxWidth: 12,
          boxHeight: 12,
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
      y: {
        beginAtZero: true,
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
      },
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
    },
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

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Grid container spacing={3}>
        {/* Beautiful Key Metrics with Animations */}
        <Grid item xs={12}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
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
                  <AssessmentIcon sx={{
                    position: 'absolute',
                    top: 8,
                    left: 8,
                    fontSize: 20,
                    color: modernColors.primary,
                    opacity: 0.7
                  }} />
                  <Typography variant="h4" sx={{
                    fontWeight: 700,
                    color: modernColors.primary,
                    fontSize: { xs: '1.5rem', sm: '1.8rem' },
                    mb: 0.5
                  }}>
                    {data.number_of_assessments || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#374151', fontWeight: 600, fontSize: '0.8rem' }}>
                    Total Assessments
                  </Typography>
                </Card>
              </motion.div>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
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
                  <WarningIcon sx={{
                    position: 'absolute',
                    top: 8,
                    left: 8,
                    fontSize: 20,
                    color: modernColors.warning,
                    opacity: 0.7
                  }} />
                  <Typography variant="h4" sx={{
                    fontWeight: 700,
                    color: modernColors.warning,
                    fontSize: { xs: '1.5rem', sm: '1.8rem' },
                    mb: 0.5
                  }}>
                    {data.high_residual_risk_activities?.total_high_risk || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#374151', fontWeight: 600, fontSize: '0.8rem' }}>
                    High Risk Activities
                  </Typography>
                </Card>
              </motion.div>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
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
                  <TrendingUpIcon sx={{
                    position: 'absolute',
                    top: 8,
                    left: 8,
                    fontSize: 20,
                    color: modernColors.success,
                    opacity: 0.7
                  }} />
                  <Typography variant="h4" sx={{
                    fontWeight: 700,
                    color: modernColors.success,
                    fontSize: { xs: '1.5rem', sm: '1.8rem' },
                    mb: 0.5
                  }}>
                    {data.measure_effectiveness?.overall_effectiveness?.toFixed(1) || 'N/A'}%
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#374151', fontWeight: 600, fontSize: '0.8rem' }}>
                    Avg. Effectiveness
                  </Typography>
                </Card>
              </motion.div>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
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
                  <SecurityIcon sx={{
                    position: 'absolute',
                    top: 8,
                    left: 8,
                    fontSize: 20,
                    color: modernColors.info,
                    opacity: 0.7
                  }} />
                  <Typography variant="h4" sx={{
                    fontWeight: 700,
                    color: modernColors.info,
                    fontSize: { xs: '1.5rem', sm: '1.8rem' },
                    mb: 0.5
                  }}>
                    {data.common_control_measures?.total_measures || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#374151', fontWeight: 600, fontSize: '0.8rem' }}>
                    Control Measures
                  </Typography>
                </Card>
              </motion.div>
            </Grid>
          </Grid>
        </Grid>

        {/* Beautiful Severity Analysis Chart - NO HOVER on container */}
        <Grid item xs={12} md={6}>
          <motion.div
            variants={itemVariants}
            // Removed whileHover from chart container
          >
            <Paper sx={{
              p: 3,
              height: 340,
              bgcolor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: 2,
              display: 'flex',
              flexDirection: 'column',
              // Removed hover effects from chart container
            }}>
              <Typography variant="h6" sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                fontWeight: 600,
                color: '#092f57',
                mb: 2,
                pb: 1,
                borderBottom: '1px solid #e5e7eb',
                fontSize: '1.1rem'
              }}>
                <WarningIcon sx={{ color: modernColors.warning, fontSize: 20 }} />
                Severity Analysis
              </Typography>
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3, duration: 0.4 }}
              >
                <Box sx={{ height: 250 }}>
                  <Bar data={severityChartData} options={modernChartOptions} />
                </Box>
              </motion.div>
            </Paper>
          </motion.div>
        </Grid>

      {/* Likelihood Analysis */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3, height: 340, bgcolor: 'white', border: '1px solid #e5e7eb' }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 600, color: '#092f57', mb: 2, pb: 1, borderBottom: '1px solid #e5e7eb', fontSize: '1.1rem' }}>
            <AssessmentIcon sx={{ color: modernColors.primary, fontSize: 20 }} />
            Likelihood Distribution
          </Typography>
          <Box sx={{ height: 250 }}>
            <Doughnut data={likelihoodChartData} options={modernDonutOptions} />
          </Box>
        </Paper>
      </Grid>

      {/* Hazard Effects */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3, height: 340, bgcolor: 'white', border: '1px solid #e5e7eb' }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 600, color: '#092f57', mb: 2, pb: 1, borderBottom: '1px solid #e5e7eb', fontSize: '1.1rem' }}>
            <SecurityIcon sx={{ color: modernColors.error, fontSize: 20 }} />
            Hazard Effects (P.E.A.R)
          </Typography>
          <Box sx={{ height: 250 }}>
            <Bar data={hazardEffectsData} options={modernChartOptions} />
          </Box>
        </Paper>
      </Grid>

      {/* Risk Reduction Effectiveness */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3, height: 340, bgcolor: 'white', border: '1px solid #e5e7eb' }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 600, color: '#092f57', mb: 2, pb: 1, borderBottom: '1px solid #e5e7eb', fontSize: '1.1rem' }}>
            <TrendingUpIcon sx={{ color: modernColors.success, fontSize: 20 }} />
            Risk Reduction Effectiveness
          </Typography>
          <Box sx={{ height: 250 }}>
            {data.measure_effectiveness?.effectiveness_breakdown?.high_effectiveness ? (
              <Box>
                <Typography variant="body2" sx={{ color: '#64748b', mb: 2, fontWeight: 500, fontSize: '0.85rem' }}>
                  Overall Effectiveness: {data.measure_effectiveness.overall_effectiveness?.toFixed(1)}%
                </Typography>
                <List dense sx={{ maxHeight: 200, overflow: 'auto' }}>
                  {data.measure_effectiveness.effectiveness_breakdown.high_effectiveness.slice(0, 5).map((item, index) => (
                    <ListItem key={index} sx={{ py: 1, borderBottom: '1px solid #f1f5f9' }}>
                      <ListItemIcon>
                        <CheckCircleIcon sx={{ color: modernColors.success }} fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={item.situation || `Assessment ${item.assessment_no}`}
                        secondary={`Risk Reduction: ${item.reduction_percentage?.toFixed(1)}% (${item.initial_risk_score} → ${item.residual_risk_score})`}
                        primaryTypographyProps={{ fontWeight: 500, color: '#092f57' }}
                        secondaryTypographyProps={{ color: '#64748b' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            ) : (
              <Typography variant="body2" sx={{ color: '#64748b' }}>
                No effectiveness data available
              </Typography>
            )}
          </Box>
        </Paper>
      </Grid>

      {/* Common Hazards */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3, height: 340, bgcolor: 'white', border: '1px solid #e5e7eb' }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 600, color: '#092f57', mb: 2, pb: 1, borderBottom: '1px solid #e5e7eb', fontSize: '1.1rem' }}>
            <WarningIcon sx={{ color: modernColors.warning, fontSize: 20 }} />
            Common Hazards
          </Typography>
          <Box sx={{ maxHeight: 250, overflow: 'auto' }}>
            <List dense>
              {Array.isArray(data.common_hazards?.common_hazards) ? (
                data.common_hazards.common_hazards.slice(0, 10).map((hazard, index) => (
                  <ListItem key={index} sx={{ py: 1, borderBottom: '1px solid #f1f5f9' }}>
                    <ListItemIcon>
                      <WarningIcon sx={{ color: modernColors.warning }} fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary={hazard.hazard || hazard.hazard_type || 'Unknown Hazard'}
                      secondary={hazard.count ? `Count: ${hazard.count}` : ''}
                      primaryTypographyProps={{ fontWeight: 500, color: '#092f57' }}
                      secondaryTypographyProps={{ color: '#64748b' }}
                    />
                  </ListItem>
                ))
              ) : (
                <ListItem>
                  <ListItemText
                    primary="No hazard data available"
                    primaryTypographyProps={{ color: '#64748b' }}
                  />
                </ListItem>
              )}
            </List>
          </Box>
        </Paper>
      </Grid>
      </Grid>
    </motion.div>
  );
};

export default RiskAssessmentCharts;
