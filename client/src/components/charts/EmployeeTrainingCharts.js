/**
 * Employee Training & Fitness Charts Component
 * Displays comprehensive training compliance, certification status, and medical fitness data
 */

import React from 'react';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  useTheme,
  alpha,
} from '@mui/material';
import {
  School as TrainingIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  Business as DepartmentIcon,
} from '@mui/icons-material';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { motion } from 'framer-motion';
import { useChartResize } from '../../utils/chartResizeHandler';

const EmployeeTrainingCharts = ({ data }) => {
  const theme = useTheme();
  const { setupResize } = useChartResize();

  // Setup chart resize handling
  React.useEffect(() => {
    const cleanup = setupResize();
    return cleanup;
  }, [setupResize]);

  // Safely extract data with fallbacks
  const summaryMetrics = data?.summary_metrics || {};
  const expiredTrainings = data?.expired_trainings || {};
  const upcomingExpiry = data?.upcoming_training_expiry || {};
  const fitnessMetrics = data?.fitness_metrics || {};
  const departmentTraining = data?.department_training_status || {};
  const medicalData = data?.medical_data_completeness || {};


  // Modern color palette for charts
  const colors = {
    primary: '#1e40af',
    success: '#059669',
    warning: '#d97706',
    error: '#dc2626',
    info: '#0284c7',
    secondary: '#7c3aed',
  };

  // Prepare training compliance data
  const trainingComplianceData = [
    {
      name: 'Current/Valid',
      value: Math.max(0, summaryMetrics.total_employees - summaryMetrics.employees_with_expired_trainings - summaryMetrics.employees_with_upcoming_expiry),
      color: colors.success
    },
    {
      name: 'Expiring Soon',
      value: summaryMetrics.employees_with_upcoming_expiry || 0,
      color: colors.warning
    },
    {
      name: 'Expired',
      value: summaryMetrics.employees_with_expired_trainings || 0,
      color: colors.error
    }
  ];



  // Prepare department training data
  const departmentData = Object.entries(departmentTraining.departments || {}).map(([dept, info]) => ({
    name: dept,
    expired: info.expired_trainings || 0,
    expiring: info.expiring_trainings || 0,
    total: info.total_employees || 0
  }));



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
        height: 120, // Fixed height for consistency
        bgcolor: alpha(colors[color], 0.05),
        borderRadius: 2,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          boxShadow: '0 8px 25px 0 rgba(0, 0, 0, 0.15)',
          bgcolor: alpha(colors[color], 0.08),
        }
      }}>
        <CardContent sx={{ p: 2, height: '100%', display: 'flex', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
            <motion.div
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ duration: 0.2 }}
            >
              <Box
                sx={{
                  width: 36, // Slightly smaller icon container
                  height: 36,
                  borderRadius: 2,
                  bgcolor: alpha(colors[color], 0.1),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: colors[color],
                  mr: 2,
                }}
              >
                {icon}
              </Box>
            </motion.div>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 700,
                  color: colors[color],
                  fontSize: '1.5rem', // Consistent font size
                  lineHeight: 1.2,
                  mb: 0.5
                }}
              >
                {value}
              </Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  fontSize: '0.875rem',
                  lineHeight: 1.2,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}
              >
                {title}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Box sx={{ p: 2 }}> {/* Reduced padding */}
      {/* Key Metrics Summary */}
      <Grid container spacing={2} sx={{ mb: 3 }}> {/* Reduced spacing and margin */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Employees"
            value={summaryMetrics.total_employees || 0}
            icon={<PersonIcon />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Expired Trainings"
            value={summaryMetrics.employees_with_expired_trainings || 0}
            icon={<WarningIcon />}
            color="error"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Fit for Work"
            value={`${Math.round(summaryMetrics.percentage_fit_employees || 100)}%`}
            icon={<CheckIcon />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Upcoming Expiry"
            value={summaryMetrics.employees_with_upcoming_expiry || 0}
            icon={<ScheduleIcon />}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Enhanced Charts Section */}
      <Grid container spacing={3}>
        {/* Modern Training Compliance Donut Chart */}
        <Grid item xs={12} md={4}>
          <motion.div variants={itemVariants} whileHover={{ scale: 1.01, y: -2 }}>
            <Card sx={{
              height: 320, // Reduced height for more compact design
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
                  fontSize: '1.2rem', // Smaller title
                  mb: 2,
                  pb: 1.5,
                  borderBottom: `2px solid ${colors.primary}15`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1
                }}>
                  <TrainingIcon sx={{ color: colors.primary, fontSize: '1.2rem' }} />
                  Training Compliance
                </Typography>
                <Box sx={{ height: 240 }}> {/* Reduced chart height */}
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={trainingComplianceData}
                        cx="50%"
                        cy="50%"
                        innerRadius={45}
                        outerRadius={75}
                        dataKey="value"
                        label={({ name, value, percent }) => `${(percent * 100).toFixed(0)}%`}
                        labelLine={false}
                        animationBegin={0}
                        animationDuration={1500}
                        labelStyle={{
                          fill: '#1f2937', // Dark text for better visibility
                          fontSize: '14px',
                          fontWeight: 'bold',
                          textAnchor: 'middle'
                        }}
                      >
                        {trainingComplianceData.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={entry.color}
                            stroke="#ffffff"
                            strokeWidth={2}
                          />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#ffffff',
                          border: `2px solid ${colors.primary}`,
                          borderRadius: '8px',
                          color: '#1f2937',
                          fontWeight: 600,
                          fontSize: '12px',
                          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
                        }}
                        formatter={(value, name) => [
                          `${value} employees`,
                          name
                        ]}
                      />
                      <Legend
                        verticalAlign="bottom"
                        height={30}
                        iconType="circle"
                        wrapperStyle={{
                          paddingTop: '15px',
                          fontSize: '11px',
                          fontWeight: 600
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Enhanced Department Training Status */}
        <Grid item xs={12} md={8}>
          <motion.div variants={itemVariants} whileHover={{ scale: 1.005, y: -2 }}>
            <Card sx={{
              height: 320, // Reduced height to match pie chart
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
                  fontSize: '1.2rem', // Smaller title to match
                  mb: 2,
                  pb: 1.5,
                  borderBottom: `2px solid ${colors.info}15`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1
                }}>
                  <DepartmentIcon sx={{ color: colors.info, fontSize: '1.2rem' }} />
                  Training by Department
                </Typography>
                <Box sx={{ height: 240 }}> {/* Reduced chart height */}
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={departmentData} margin={{ top: 15, right: 20, left: 15, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                      <XAxis
                        dataKey="name"
                        tick={{ fontSize: 11, fontWeight: 600, fill: '#6b7280' }}
                        axisLine={{ stroke: '#e5e7eb', strokeWidth: 1 }}
                      />
                      <YAxis
                        tick={{ fontSize: 11, fontWeight: 600, fill: '#6b7280' }}
                        axisLine={{ stroke: '#e5e7eb', strokeWidth: 1 }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'rgba(17, 24, 39, 0.95)',
                          border: `2px solid ${colors.info}`,
                          borderRadius: '8px',
                          color: '#ffffff',
                          fontWeight: 600,
                          fontSize: '12px'
                        }}
                      />
                      <Legend
                        wrapperStyle={{
                          paddingTop: '15px',
                          fontSize: '11px',
                          fontWeight: 600
                        }}
                      />
                      <Bar
                        dataKey="expired"
                        fill={colors.error}
                        name="Expired"
                        radius={[3, 3, 0, 0]}
                        animationBegin={0}
                        animationDuration={1500}
                      />
                      <Bar
                        dataKey="expiring"
                        fill={colors.warning}
                        name="Expiring"
                        radius={[3, 3, 0, 0]}
                        animationBegin={200}
                        animationDuration={1500}
                      />
                      <Bar
                        dataKey="total"
                        fill={colors.info}
                        name="Total"
                        radius={[3, 3, 0, 0]}
                        animationBegin={400}
                        animationDuration={1500}
                      />
                    </BarChart>
                  </ResponsiveContainer>
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

export default EmployeeTrainingCharts;
