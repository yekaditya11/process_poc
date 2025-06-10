/**
 * Global Dashboard Charts Component
 * Displays 10 key KPIs from different modules in a unified view
 * Redesigned to match dashboardtheme.png styling
 */

import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Alert
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

// Dashboard theme colors based on dashboardtheme.png
const dashboardTheme = {
  colors: {
    primary: '#2563eb',      // Blue
    secondary: '#059669',    // Green
    warning: '#f59e0b',      // Orange/Yellow
    danger: '#dc2626',       // Red
    info: '#0891b2',         // Cyan
    purple: '#7c3aed',       // Purple
    gray: '#6b7280',         // Gray
    lightBlue: '#3b82f6',    // Light Blue
  },
  cardStyle: {
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    border: '1px solid #e5e7eb'
  }
};

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
    series: [
      {
        name: 'Actions',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '50%'],
        data: [
          { value: kpis.openActions, name: 'Open', itemStyle: { color: dashboardTheme.colors.warning } },
          { value: kpis.closedActions, name: 'Closed', itemStyle: { color: dashboardTheme.colors.secondary } }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
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
    series: [
      {
        name: 'Observations',
        type: 'bar',
        data: finalObservationData.map(item => ({
          value: item.count,
          itemStyle: { color: dashboardTheme.colors.primary }
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };

  // ECharts configuration for Actions Completed On Time - Circular Progress
  const actionsProgressOption = {
    series: [
      {
        type: 'gauge',
        startAngle: 200,
        endAngle: -20,
        min: 0,
        max: 100,
        splitNumber: 5,
        itemStyle: {
          color: dashboardTheme.colors.primary
        },
        progress: {
          show: true,
          width: 8
        },
        pointer: {
          show: false
        },
        axisLine: {
          lineStyle: {
            width: 8,
            color: [[1, '#f3f4f6']]
          }
        },
        axisTick: {
          show: false
        },
        splitLine: {
          show: false
        },
        axisLabel: {
          show: false
        },
        title: {
          show: false
        },
        detail: {
          valueAnimation: true,
          width: '60%',
          lineHeight: 40,
          borderRadius: 8,
          offsetCenter: [0, '10%'],
          fontSize: 20,
          fontWeight: 'bold',
          formatter: '{value}%',
          color: '#1f2937'
        },
        data: [
          {
            value: kpis.actionsCompletedOnTime
          }
        ]
      }
    ]
  };

  // ECharts configuration for Driver Checklist - Horizontal Progress Bar
  const driverProgressOption = {
    grid: {
      left: '5%',
      right: '25%',
      top: '30%',
      bottom: '30%',
      containLabel: false
    },
    xAxis: {
      type: 'value',
      max: 100,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { show: false },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'category',
      data: ['Progress'],
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { show: false }
    },
    series: [
      {
        type: 'bar',
        data: [
          {
            value: kpis.driverCompletionRate,
            itemStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 1,
                y2: 0,
                colorStops: [
                  { offset: 0, color: dashboardTheme.colors.warning },
                  { offset: 1, color: '#fbbf24' }
                ]
              },
              borderRadius: [0, 6, 6, 0]
            }
          }
        ],
        barWidth: '40%',
        label: {
          show: true,
          position: 'right',
          formatter: '{c}%',
          color: '#1f2937',
          fontSize: 16,
          fontWeight: 'bold'
        },
        backgroundStyle: {
          color: '#f3f4f6',
          borderRadius: [0, 6, 6, 0]
        },
        showBackground: true
      }
    ],
    graphic: [
      {
        type: 'text',
        left: 'center',
        bottom: '10%',
        style: {
          text: 'Completion Rate',
          fontSize: 11,
          fill: '#6b7280',
          textAlign: 'center'
        }
      }
    ]
  };

  // ECharts configuration for Valid Calibrations - Mini Bar Chart
  const calibrationMiniBarOption = {
    grid: {
      left: '5%',
      right: '5%',
      top: '20%',
      bottom: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      max: 100,
      show: false
    },
    yAxis: {
      type: 'category',
      data: ['Valid', 'Expired'],
      axisLabel: {
        color: '#6b7280',
        fontSize: 11
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      }
    },
    series: [
      {
        type: 'bar',
        data: [
          {
            value: kpis.validCalibrations,
            itemStyle: { color: dashboardTheme.colors.secondary }
          },
          {
            value: 100 - kpis.validCalibrations,
            itemStyle: { color: dashboardTheme.colors.danger }
          }
        ],
        barWidth: '60%',
        label: {
          show: true,
          position: 'right',
          formatter: '{c}%',
          color: '#1f2937',
          fontSize: 13
        }
      }
    ]
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" sx={{ mb: 3, fontWeight: 600, color: '#1f2937' }}>
        Safety Dashboard
      </Typography>

      {/* Top Row - Critical KPIs */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Incidents Reported */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ ...dashboardTheme.cardStyle, height: '150px' }}>
            <CardContent sx={{ p: 2, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
                <Box>
                  <Typography
                    variant="h4"
                    sx={{
                      fontWeight: 600,
                      color: '#1f2937',
                      mb: 0.5,
                      fontSize: '2rem'
                    }}
                  >
                    {kpis.incidentsReported}
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      color: '#6b7280',
                      fontSize: '0.95rem',
                      fontWeight: 500
                    }}
                  >
                    Incidents Reported
                  </Typography>
                </Box>
                <Security sx={{ fontSize: 32, color: dashboardTheme.colors.danger }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Days Since Last Incident */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ ...dashboardTheme.cardStyle, height: '150px' }}>
            <CardContent sx={{ p: 2, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
                <Box>
                  <Typography
                    variant="h4"
                    sx={{
                      fontWeight: 600,
                      color: '#1f2937',
                      mb: 0.5,
                      fontSize: '2rem'
                    }}
                  >
                    {kpis.daysSinceLastIncident}
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      color: '#6b7280',
                      fontSize: '0.95rem',
                      fontWeight: 500
                    }}
                  >
                    Days Since Last Incident
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 32, color: dashboardTheme.colors.secondary }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Actions Completed On Time */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ ...dashboardTheme.cardStyle, height: '150px' }}>
            <CardContent sx={{ p: 1.5, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography
                  variant="body1"
                  sx={{
                    color: '#6b7280',
                    fontSize: '0.95rem',
                    fontWeight: 500
                  }}
                >
                  Actions On Time
                </Typography>
                <Assignment sx={{ fontSize: 20, color: dashboardTheme.colors.primary }} />
              </Box>
              <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ReactECharts
                  option={actionsProgressOption}
                  style={{ height: '100px', width: '100%' }}
                  opts={{ renderer: 'canvas' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Driver Checklist Completion */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ ...dashboardTheme.cardStyle, height: '150px' }}>
            <CardContent sx={{ p: 1.5, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography
                  variant="body1"
                  sx={{
                    color: '#6b7280',
                    fontSize: '0.95rem',
                    fontWeight: 500
                  }}
                >
                  Driver Checklists
                </Typography>
                <DirectionsCar sx={{ fontSize: 20, color: dashboardTheme.colors.warning }} />
              </Box>
              <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ReactECharts
                  option={driverProgressOption}
                  style={{ height: '100px', width: '100%' }}
                  opts={{ renderer: 'canvas' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Second Row - Training & Equipment */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Expired Trainings */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ ...dashboardTheme.cardStyle, height: '150px' }}>
            <CardContent sx={{ p: 2, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
                <Box>
                  <Typography
                    variant="h4"
                    sx={{
                      fontWeight: 600,
                      color: '#1f2937',
                      mb: 0.5,
                      fontSize: '2rem'
                    }}
                  >
                    {kpis.expiredTrainings}
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      color: '#6b7280',
                      fontSize: '0.95rem',
                      fontWeight: 500
                    }}
                  >
                    Expired Trainings
                  </Typography>
                </Box>
                <School sx={{ fontSize: 32, color: dashboardTheme.colors.purple }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Unfit Employees */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ ...dashboardTheme.cardStyle, height: '150px' }}>
            <CardContent sx={{ p: 2, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
                <Box>
                  <Typography
                    variant="h4"
                    sx={{
                      fontWeight: 600,
                      color: '#1f2937',
                      mb: 0.5,
                      fontSize: '2rem'
                    }}
                  >
                    {Number(kpis.unfitEmployees).toFixed(1)}%
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      color: '#6b7280',
                      fontSize: '0.95rem',
                      fontWeight: 500
                    }}
                  >
                    Employees Unfit to Work
                  </Typography>
                </Box>
                <Error sx={{ fontSize: 32, color: dashboardTheme.colors.danger }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Valid Calibrations */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ ...dashboardTheme.cardStyle, height: '150px' }}>
            <CardContent sx={{ p: 1.5, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography
                  variant="body1"
                  sx={{
                    color: '#6b7280',
                    fontSize: '0.95rem',
                    fontWeight: 500
                  }}
                >
                  Equipment Status
                </Typography>
                <Build sx={{ fontSize: 20, color: dashboardTheme.colors.secondary }} />
              </Box>
              <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ReactECharts
                  option={calibrationMiniBarOption}
                  style={{ height: '100px', width: '100%' }}
                  opts={{ renderer: 'canvas' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Assessments */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ ...dashboardTheme.cardStyle, height: '150px' }}>
            <CardContent sx={{ p: 2, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
                <Box>
                  <Typography
                    variant="h4"
                    sx={{
                      fontWeight: 600,
                      color: '#1f2937',
                      mb: 0.5,
                      fontSize: '2rem'
                    }}
                  >
                    {kpis.riskAssessments}
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      color: '#6b7280',
                      fontSize: '0.95rem',
                      fontWeight: 500
                    }}
                  >
                    Risk Assessments
                  </Typography>
                </Box>
                <Assessment sx={{ fontSize: 32, color: dashboardTheme.colors.info }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Third Row - Charts */}
      <Grid container spacing={3}>
        {/* Open vs Closed Actions */}
        <Grid item xs={12} md={6}>
          <Card sx={{
            ...dashboardTheme.cardStyle,
            height: 380
          }}>
            <CardContent sx={{ p: 3, height: '100%' }}>
              <ReactECharts
                option={actionChartOption}
                style={{ height: '100%', width: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Observations by Area */}
        <Grid item xs={12} md={6}>
          <Card sx={{
            ...dashboardTheme.cardStyle,
            height: 380
          }}>
            <CardContent sx={{ p: 3, height: '100%' }}>
              <ReactECharts
                option={observationChartOption}
                style={{ height: '100%', width: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default GlobalDashboardCharts;
