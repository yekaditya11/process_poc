/**
 * Global Dashboard Charts Component
 * Displays 10 key KPIs from different modules in a unified view
 * Redesigned to match other dashboard styling patterns
 */

import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Alert,
  alpha
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Security,
  Assignment,
  DirectionsCar,
  Build,
  School,
  Assessment
} from '@mui/icons-material';
import ReactECharts from 'echarts-for-react';
import { motion } from 'framer-motion';

// Color scheme consistent with other dashboards
const colors = {
  primary: '#1e40af',
  secondary: '#059669',
  success: '#059669',
  warning: '#d97706',
  error: '#dc2626',
  info: '#0284c7',
  purple: '#7c3aed',
  gray: '#6b7280'
};

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 30, scale: 0.9 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.6,
      ease: [0.4, 0, 0.2, 1],
      type: "spring",
      stiffness: 100,
      damping: 15
    }
  }
};

const chartVariants = {
  hidden: { opacity: 0, y: 40, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.8,
      ease: [0.4, 0, 0.2, 1],
      type: "spring",
      stiffness: 80,
      damping: 20
    }
  }
};

// StatCard component matching other dashboards
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
      height: 120,
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
                width: 36,
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
                fontSize: '1.5rem',
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

const GlobalDashboardCharts = ({ data }) => {
  console.log('GlobalDashboardCharts received data:', data);

  if (!data || !data.safety_dashboard_data) {
    return (
      <Alert severity="info">
        Loading global dashboard data...
      </Alert>
    );
  }

  const {
    incident_investigation,
    action_tracking,
    driver_safety_checklists,
    observation_tracker,
    equipment_asset_management,
    employee_training_fitness,
    risk_assessment
  } = data.safety_dashboard_data;

  // Extract the 10 KPIs with safety checks based on actual API response
  const kpis = {
    incidentsReported: Number(incident_investigation?.incidents_reported) || 0,
    openActions: Number(action_tracking?.action_status?.open_actions) || 0,
    closedActions: Number(action_tracking?.action_status?.closed_actions) || 0,
    actionsCompletedOnTime: Number(action_tracking?.on_time_completion?.percentage_completed_on_time) || 0,
    expiredTrainings: Number(employee_training_fitness?.expired_trainings?.employees_with_expired_trainings) || 0,
    unfitEmployees: Number(employee_training_fitness?.fitness_metrics?.percentage_unfit) || 0,
    driverCompletionRate: Number(driver_safety_checklists?.daily_completions?.completion_percentage) || 0,
    validCalibrations: Number(equipment_asset_management?.summary_metrics?.percentage_with_valid_certificates) || 0,
    riskAssessments: Number(risk_assessment?.total_assessments_analyzed) || 0,
    observationsByArea: observation_tracker?.observations_by_area?.observations_by_area || {},
    daysSinceLastIncident: Number(incident_investigation?.days_since_last_incident) || 0
  };

  console.log('Extracted KPIs:', kpis);



  // Prepare observation data for bar chart
  const observationData = Object.entries(kpis.observationsByArea || {})
    .map(([area, count]) => ({
      area: String(area).length > 15 ? String(area).substring(0, 15) + '...' : String(area),
      count: Number(count) || 0
    }))
    .filter(item => item.count > 0)
    .slice(0, 8); // Show top 8 areas

  // If no observation data, show sample data for demonstration
  const finalObservationData = observationData.length > 0 ? observationData : [
    { area: 'Shop Floor', count: 3 },
    { area: 'Warehouse', count: 3 },
    { area: 'Loading Dock', count: 1 },
    { area: 'Workshop', count: 2 }
  ];

  // ECharts configuration for Action Tracking Pie Chart
  const actionChartOption = {
    title: {
      text: 'Open vs Closed Actions',
      left: 'center',
      textStyle: {
        color: '#1f2937',
        fontSize: 20,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      bottom: 10,
      textStyle: {
        color: '#6b7280',
        fontSize: 14
      }
    },
    animation: true,
    animationDuration: 1500,
    animationEasing: 'elasticOut',
    animationDelay: (idx) => idx * 200,
    series: [
      {
        name: 'Actions',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '50%'],
        data: [
          { value: kpis.openActions, name: 'Open', itemStyle: { color: colors.warning } },
          { value: kpis.closedActions, name: 'Closed', itemStyle: { color: colors.success } }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        animationType: 'scale',
        animationEasing: 'elasticOut',
        animationDelay: (idx) => idx * 300
      }
    ]
  };

  // ECharts configuration for Observations Bar Chart
  const observationChartOption = {
    title: {
      text: 'Observations by Area',
      left: 'center',
      textStyle: {
        color: '#1f2937',
        fontSize: 20,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: finalObservationData.map(item => item.area),
      axisLabel: {
        rotate: 45,
        color: '#6b7280',
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#6b7280',
        fontSize: 12
      }
    },
    animation: true,
    animationDuration: 1200,
    animationEasing: 'cubicOut',
    animationDelay: (idx) => idx * 100,
    series: [
      {
        name: 'Observations',
        type: 'bar',
        data: finalObservationData.map(item => ({
          value: item.count,
          itemStyle: { color: colors.primary }
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        animationDelay: (idx) => idx * 150,
        animationEasing: 'bounceOut'
      }
    ]
  };



  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 600, color: '#1f2937' }}>
          Safety Dashboard
        </Typography>

        {/* Key Metrics Summary */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {/* Incidents Reported */}
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Incidents Reported"
              value={kpis.incidentsReported}
              icon={<Security />}
              color="error"
            />
          </Grid>

          {/* Days Since Last Incident */}
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Days Since Last Incident"
              value={kpis.daysSinceLastIncident}
              icon={<CheckCircle />}
              color="success"
            />
          </Grid>

          {/* Actions Completed On Time */}
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Actions On Time"
              value={`${kpis.actionsCompletedOnTime}%`}
              icon={<Assignment />}
              color="primary"
            />
          </Grid>

          {/* Driver Checklist Completion */}
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Driver Checklists"
              value={`${kpis.driverCompletionRate}%`}
              icon={<DirectionsCar />}
              color="warning"
            />
          </Grid>

          {/* Expired Trainings */}
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Expired Trainings"
              value={kpis.expiredTrainings}
              icon={<School />}
              color="purple"
            />
          </Grid>

          {/* Unfit Employees */}
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Employees Unfit to Work"
              value={`${Number(kpis.unfitEmployees).toFixed(1)}%`}
              icon={<Error />}
              color="error"
            />
          </Grid>

          {/* Valid Calibrations */}
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Valid Calibrations"
              value={`${kpis.validCalibrations}%`}
              icon={<Build />}
              color="success"
            />
          </Grid>

          {/* Risk Assessments */}
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Risk Assessments"
              value={kpis.riskAssessments}
              icon={<Assessment />}
              color="info"
            />
          </Grid>
        </Grid>

        {/* Charts Section */}
        <Grid container spacing={3} sx={{ mt: 2 }}>
          {/* Open vs Closed Actions */}
          <Grid item xs={12} md={6}>
            <motion.div
              key={`action-chart-${kpis.openActions}-${kpis.closedActions}`}
              variants={chartVariants}
              whileHover={{ scale: 1.02, y: -4 }}
              transition={{ duration: 0.2 }}
            >
              <Card sx={{
                height: 450,
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
                    📊 Open vs Closed Actions
                  </Typography>
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5, duration: 0.6 }}
                  >
                    <Box sx={{ height: 360 }}>
                      <ReactECharts
                        key={`action-echart-${kpis.openActions}-${kpis.closedActions}`}
                        option={actionChartOption}
                        style={{ height: '100%', width: '100%' }}
                        opts={{ renderer: 'canvas' }}
                      />
                    </Box>
                  </motion.div>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Observations by Area */}
          <Grid item xs={12} md={6}>
            <motion.div
              key={`observation-chart-${finalObservationData.length}`}
              variants={chartVariants}
              whileHover={{ scale: 1.02, y: -4 }}
              transition={{ duration: 0.2 }}
            >
              <Card sx={{
                height: 450,
                background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                border: `2px solid ${colors.success}20`,
                borderRadius: 4,
                boxShadow: '0 10px 40px rgba(5, 150, 105, 0.1)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  boxShadow: '0 15px 50px rgba(5, 150, 105, 0.15)',
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
                    borderBottom: `2px solid ${colors.success}15`
                  }}>
                    📍 Observations by Area
                  </Typography>
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.7, duration: 0.6 }}
                  >
                    <Box sx={{ height: 360 }}>
                      <ReactECharts
                        key={`observation-echart-${finalObservationData.length}`}
                        option={observationChartOption}
                        style={{ height: '100%', width: '100%' }}
                        opts={{ renderer: 'canvas' }}
                      />
                    </Box>
                  </motion.div>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>
      </Box>
    </motion.div>
  );
};

export default GlobalDashboardCharts;
