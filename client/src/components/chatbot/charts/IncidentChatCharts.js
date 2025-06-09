/**
 * Enhanced Incident Investigation Chat Charts
 * Specialized visualizations for incident data in chat interface
 */

import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import ReactECharts from 'echarts-for-react';
import { chatAnimations } from '../../../utils/animations';

const IncidentChatCharts = ({ chartData, isFullscreen = false }) => {
  const chartHeight = isFullscreen ? '70vh' : '350px';

  // Enhanced color palette for incident charts
  const incidentColors = {
    critical: '#dc2626',
    high: '#ea580c', 
    medium: '#d97706',
    low: '#059669',
    closed: '#10b981',
    open: '#f59e0b',
    investigating: '#3b82f6'
  };

  const generateIncidentChart = () => {
    const { type, data, title } = chartData;

    const baseConfig = {
      title: {
        text: title,
        left: 'center',
        textStyle: {
          color: '#092f57',
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#ddd',
        borderWidth: 1,
        textStyle: { color: '#333' },
        confine: true,
        formatter: function(params) {
          return `
            <div style="padding: 8px;">
              <strong>${params.name}</strong><br/>
              <span style="color: ${params.color};">●</span> 
              ${params.value} incidents (${params.percent}%)
            </div>
          `;
        }
      },
      animation: true,
      animationDuration: 1500,
      animationEasing: 'elasticOut'
    };

    switch (type) {
      case 'incident_severity':
        return {
          ...baseConfig,
          series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '50%'],
            data: data.map((item, index) => ({
              name: item.name,
              value: item.value,
              itemStyle: {
                color: incidentColors[item.name.toLowerCase()] || incidentColors.medium
              },
              emphasis: {
                itemStyle: {
                  shadowBlur: 15,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            })),
            label: {
              show: true,
              formatter: '{b}: {c}',
              fontSize: 12,
              fontWeight: 'bold'
            },
            animationType: 'scale',
            animationEasing: 'elasticOut'
          }]
        };

      case 'incident_trends':
        return {
          ...baseConfig,
          xAxis: {
            type: 'category',
            data: data.map(item => item.name),
            axisLabel: { color: '#666', rotate: 45 }
          },
          yAxis: {
            type: 'value',
            axisLabel: { color: '#666' }
          },
          series: [{
            type: 'line',
            data: data.map(item => item.value),
            smooth: true,
            lineStyle: {
              color: incidentColors.critical,
              width: 3
            },
            itemStyle: { color: incidentColors.critical },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(220, 38, 38, 0.3)' },
                  { offset: 1, color: 'rgba(220, 38, 38, 0.05)' }
                ]
              }
            },
            emphasis: { focus: 'series' }
          }]
        };

      case 'incident_status':
        return {
          ...baseConfig,
          series: [{
            type: 'pie',
            radius: '70%',
            center: ['50%', '50%'],
            data: data.map(item => ({
              name: item.name,
              value: item.value,
              itemStyle: {
                color: incidentColors[item.name.toLowerCase()] || incidentColors.medium
              }
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              show: true,
              formatter: '{b}: {c} ({d}%)',
              fontSize: 11
            }
          }]
        };

      default:
        return baseConfig;
    }
  };

  const chartOption = generateIncidentChart();

  return (
    <motion.div
      {...chatAnimations.chartEntrance}
    >
      <Box sx={{ position: 'relative', width: '100%' }}>
        {/* Chart Header */}
        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip
            label="Incident Analysis"
            size="small"
            sx={{
              bgcolor: '#fee2e2',
              color: '#dc2626',
              fontWeight: 'bold',
              fontSize: '0.75rem'
            }}
          />
          <Typography variant="caption" sx={{ color: '#64748b', fontStyle: 'italic' }}>
            🤖 AI Generated Visualization
          </Typography>
        </Box>

        {/* Enhanced ECharts */}
        <ReactECharts
          option={chartOption}
          style={{
            width: '100%',
            height: chartHeight,
            minHeight: chartHeight
          }}
          opts={{
            renderer: 'canvas',
            useDirtyRect: false
          }}
        />

        {/* Chart Footer */}
        <Box sx={{ mt: 1, textAlign: 'center' }}>
          <Typography
            variant="caption"
            sx={{
              color: '#64748b',
              fontSize: '0.7rem',
              fontStyle: 'italic'
            }}
          >
            📊 Interactive chart - Click and drag to explore data
          </Typography>
        </Box>
      </Box>
    </motion.div>
  );
};

export default IncidentChatCharts;
