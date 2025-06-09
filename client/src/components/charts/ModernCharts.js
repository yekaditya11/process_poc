/**
 * Modern Chart Components for Professional Dashboard
 * Using Chart.js and Recharts for beautiful visualizations
 */

import React from 'react';
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
  TimeScale,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { LineChart, Line as RechartsLine, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar as RechartsBar, PieChart, Pie, Cell } from 'recharts';
import { Box, Typography, Card, CardContent } from '@mui/material';
import 'chartjs-adapter-date-fns';

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
  TimeScale
);

// Professional color palette
const COLORS = {
  primary: '#1e40af',
  secondary: '#059669',
  accent: '#dc2626',
  warning: '#d97706',
  info: '#0891b2',
  success: '#16a34a',
  neutral: '#6b7280',
  light: '#f3f4f6'
};

const CHART_COLORS = [
  '#1e40af', '#059669', '#dc2626', '#d97706', 
  '#0891b2', '#7c3aed', '#be185d', '#0d9488'
];

// Modern Trend Line Chart
export const TrendLineChart = ({ data, title, height = 300 }) => {
  const chartData = {
    labels: data?.map(item => new Date(item.week_start || item.month_start).toLocaleDateString()) || [],
    datasets: [
      {
        label: 'Incidents',
        data: data?.map(item => item.incident_count) || [],
        borderColor: COLORS.primary,
        backgroundColor: `${COLORS.primary}20`,
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: COLORS.primary,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: COLORS.primary,
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: false,
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: COLORS.neutral,
          font: {
            size: 12
          }
        }
      },
      y: {
        grid: {
          color: '#e5e7eb',
          drawBorder: false
        },
        ticks: {
          color: COLORS.neutral,
          font: {
            size: 12
          }
        }
      }
    },
    elements: {
      point: {
        hoverBackgroundColor: COLORS.primary
      }
    }
  };

  return (
    <Card sx={{ height: height + 80, boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb' }}>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#111827' }}>
          {title}
        </Typography>
        <Box sx={{ height: height }}>
          <Line data={chartData} options={options} />
        </Box>
      </CardContent>
    </Card>
  );
};

// Modern Donut Chart for Incident Types
export const IncidentTypesDonut = ({ data, title, height = 300 }) => {
  const chartData = {
    labels: data?.map(item => item.type) || [],
    datasets: [
      {
        data: data?.map(item => item.count) || [],
        backgroundColor: CHART_COLORS,
        borderColor: '#ffffff',
        borderWidth: 3,
        hoverBorderWidth: 4,
        cutout: '60%',
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 20,
          font: {
            size: 12
          },
          color: COLORS.neutral
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: COLORS.primary,
        borderWidth: 1,
        cornerRadius: 8,
        callbacks: {
          label: function(context) {
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((context.parsed / total) * 100).toFixed(1);
            return `${context.label}: ${context.parsed} (${percentage}%)`;
          }
        }
      }
    }
  };

  return (
    <Card sx={{ height: height + 80, boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb' }}>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#111827' }}>
          {title}
        </Typography>
        <Box sx={{ height: height }}>
          <Doughnut data={chartData} options={options} />
        </Box>
      </CardContent>
    </Card>
  );
};

// Modern Bar Chart for Location/Department Breakdown
export const LocationBarChart = ({ data, title, height = 300 }) => {
  const chartData = {
    labels: data?.map(item => item.location || item.department || 'Unknown') || [],
    datasets: [
      {
        label: 'Incidents',
        data: data?.map(item => item.incident_count) || [],
        backgroundColor: COLORS.primary,
        borderColor: COLORS.primary,
        borderWidth: 0,
        borderRadius: 6,
        borderSkipped: false,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: COLORS.primary,
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: false,
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: COLORS.neutral,
          font: {
            size: 12
          }
        }
      },
      y: {
        grid: {
          color: '#e5e7eb',
          drawBorder: false
        },
        ticks: {
          color: COLORS.neutral,
          font: {
            size: 12
          }
        }
      }
    }
  };

  return (
    <Card sx={{ height: height + 80, boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb' }}>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#111827' }}>
          {title}
        </Typography>
        <Box sx={{ height: height }}>
          <Bar data={chartData} options={options} />
        </Box>
      </CardContent>
    </Card>
  );
};

// Gauge Chart Component for Percentages
export const GaugeChart = ({ value, title, maxValue = 100, color = COLORS.primary }) => {
  const percentage = maxValue > 0 ? Math.min((value / maxValue) * 100, 100) : 0;

  return (
    <Card sx={{ height: 220, boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb' }}>
      <CardContent sx={{ p: 3, textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#111827' }}>
          {title}
        </Typography>
        <Box sx={{ position: 'relative', display: 'inline-block', mb: 2 }}>
          <svg width="140" height="140" viewBox="0 0 140 140">
            <circle
              cx="70"
              cy="70"
              r="60"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="10"
            />
            <circle
              cx="70"
              cy="70"
              r="60"
              fill="none"
              stroke={color}
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={`${percentage * 3.77} 377`}
              transform="rotate(-90 70 70)"
              style={{ transition: 'stroke-dasharray 0.5s ease' }}
            />
          </svg>
          <Typography
            variant="h3"
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              fontWeight: 700,
              color: '#111827',
              fontSize: '2.5rem'
            }}
          >
            {Math.round(percentage)}%
          </Typography>
        </Box>

      </CardContent>
    </Card>
  );
};
