/**
 * EChartsChart Component
 * Renders Apache ECharts within the chatbot interface for enhanced interactivity
 * Version: 2024-12-07 - Interactive charts with zoom, brush, and animations
 */

import React, { useEffect, useState, useRef } from 'react';
import {
  Box,
  Typography,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Fullscreen as FullscreenIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import ReactECharts from 'echarts-for-react';
import { motion } from 'framer-motion';
import { chatAnimations } from '../../utils/animations';

const EChartsChart = ({ chartData, isFullscreen = false }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const chartRef = useRef(null);

  // Debug logging
  console.log('EChartsChart received chartData:', chartData);

  useEffect(() => {
    // Simulate loading time for smooth transition
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 300);

    return () => clearTimeout(timer);
  }, []);

  // Process chart data and convert to ECharts format
  const processChartData = () => {
    try {
      console.log('Processing chart data for ECharts:', chartData);

      // If chartData has ECharts config, use it directly
      if (chartData.echarts_config) {
        console.log('Using ECharts config directly:', chartData.echarts_config);
        return chartData.echarts_config;
      }

      // Convert from simple chart data format to ECharts format
      const chartType = chartData.type || 'bar';
      const chartTitle = chartData.title || 'Chart';
      const chartDataArray = chartData.data || [];

      if (!chartDataArray || chartDataArray.length === 0) {
        throw new Error(`No data provided for chart. Chart type: ${chartType}, Data: ${JSON.stringify(chartDataArray)}`);
      }

      // Validate data structure
      const validData = chartDataArray.filter(item => 
        item && 
        (item.name || item.label || item.x) && 
        (item.value !== undefined || item.y !== undefined)
      );

      if (validData.length === 0) {
        throw new Error('No valid data points found');
      }

      // Generate ECharts configuration based on chart type
      return generateEChartsConfig(chartType, chartTitle, validData);

    } catch (err) {
      console.error('Error processing chart data:', err);
      throw new Error('Failed to process chart data');
    }
  };

  // Generate ECharts configuration
  const generateEChartsConfig = (chartType, title, data) => {
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
        textStyle: {
          color: '#333'
        },
        confine: true
      },
      legend: {
        orient: 'horizontal',
        bottom: 10,
        textStyle: {
          color: '#666'
        }
      },
      animation: true,
      animationDuration: 1200,
      animationEasing: 'elasticOut',
      animationDelay: (idx) => idx * 50
    };

    switch (chartType) {
      case 'bar':
        return {
          ...baseConfig,
          xAxis: {
            type: 'category',
            data: data.map(item => item.name || item.label || item.x),
            axisLabel: {
              color: '#666',
              rotate: data.length > 6 ? 45 : 0
            }
          },
          yAxis: {
            type: 'value',
            axisLabel: {
              color: '#666'
            }
          },
          series: [{
            type: 'bar',
            data: data.map((item, index) => ({
              value: item.value || item.y || 0,
              itemStyle: {
                color: item.color || getColorPalette()[index % getColorPalette().length]
              }
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            animationDelay: (idx) => idx * 100
          }],
          dataZoom: [
            {
              type: 'inside',
              start: 0,
              end: 100
            },
            {
              start: 0,
              end: 100,
              height: 30,
              bottom: 50
            }
          ]
        };

      case 'line':
        return {
          ...baseConfig,
          xAxis: {
            type: 'category',
            data: data.map(item => item.name || item.label || item.x),
            axisLabel: {
              color: '#666'
            }
          },
          yAxis: {
            type: 'value',
            axisLabel: {
              color: '#666'
            }
          },
          series: [{
            type: 'line',
            data: data.map(item => item.value || item.y || 0),
            smooth: true,
            lineStyle: {
              color: '#1976d2',
              width: 3
            },
            itemStyle: {
              color: '#1976d2'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [{
                  offset: 0, color: 'rgba(25, 118, 210, 0.3)'
                }, {
                  offset: 1, color: 'rgba(25, 118, 210, 0.05)'
                }]
              }
            },
            emphasis: {
              focus: 'series'
            }
          }],
          dataZoom: [
            {
              type: 'inside',
              start: 0,
              end: 100
            }
          ]
        };

      case 'pie':
      case 'donut':
        return {
          ...baseConfig,
          series: [{
            type: 'pie',
            radius: chartType === 'donut' ? ['40%', '70%'] : '70%',
            center: ['50%', '50%'],
            data: data.map((item, index) => ({
              name: item.name || item.label || item.x,
              value: item.value || item.y || 0,
              itemStyle: {
                color: item.color || getColorPalette()[index % getColorPalette().length]
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
              formatter: '{b}: {c} ({d}%)'
            },
            animationType: 'scale',
            animationEasing: 'elasticOut'
          }]
        };

      case 'scatter':
        return {
          ...baseConfig,
          xAxis: {
            type: 'value',
            axisLabel: {
              color: '#666'
            }
          },
          yAxis: {
            type: 'value',
            axisLabel: {
              color: '#666'
            }
          },
          series: [{
            type: 'scatter',
            data: data.map((item, index) => [
              item.x || index,
              item.value || item.y || 0
            ]),
            symbolSize: 10,
            itemStyle: {
              color: '#1976d2'
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }],
          brush: {
            toolbox: ['rect', 'polygon', 'clear'],
            xAxisIndex: 0
          }
        };

      default:
        return generateEChartsConfig('bar', title, data);
    }
  };

  // Color palette for charts
  const getColorPalette = () => [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
  ];

  // Handle chart events
  const onChartReady = (chartInstance) => {
    console.log('ECharts chart initialized successfully');
    
    // Add click event for interactivity
    chartInstance.on('click', (params) => {
      console.log('Chart clicked:', params);
      // You can add custom click handlers here
    });

    // Add brush event for data selection
    chartInstance.on('brushSelected', (params) => {
      console.log('Data selected:', params);
      // You can add custom brush handlers here
    });
  };

  const chartHeight = isFullscreen ? '70vh' : '350px';

  if (isLoading) {
    return (
      <motion.div
        {...chatAnimations.chartLoading}
      >
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: chartHeight,
            bgcolor: 'rgba(0, 0, 0, 0.02)',
            borderRadius: '12px',
          }}
        >
          <motion.div
            {...chatAnimations.typing}
          >
            <CircularProgress size={40} sx={{ color: '#092f57' }} />
          </motion.div>
        </Box>
      </motion.div>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ borderRadius: '12px' }}>
        {error}
      </Alert>
    );
  }

  if (!chartData || Object.keys(chartData).length === 0) {
    return (
      <Alert severity="info" sx={{ borderRadius: '12px' }}>
        No chart data available
      </Alert>
    );
  }

  try {
    const echartsOption = processChartData();

    return (
      <motion.div
        {...chatAnimations.chartEntrance}
      >
        <Box sx={{ position: 'relative', width: '100%' }}>
        {/* Chart Controls */}
        <Box
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            zIndex: 10,
            display: 'flex',
            gap: 0.5,
          }}
        >
          <Tooltip title="Download Chart">
            <IconButton
              size="small"
              onClick={() => {
                if (chartRef.current) {
                  const chartInstance = chartRef.current.getEchartsInstance();
                  const url = chartInstance.getDataURL({
                    type: 'png',
                    backgroundColor: '#fff'
                  });
                  const link = document.createElement('a');
                  link.download = 'chart.png';
                  link.href = url;
                  link.click();
                }
              }}
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.9)',
                '&:hover': { bgcolor: 'rgba(255, 255, 255, 1)' },
              }}
            >
              <DownloadIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Refresh Chart">
            <IconButton
              size="small"
              onClick={() => {
                if (chartRef.current) {
                  const chartInstance = chartRef.current.getEchartsInstance();
                  chartInstance.resize();
                }
              }}
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.9)',
                '&:hover': { bgcolor: 'rgba(255, 255, 255, 1)' },
              }}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        {/* ECharts Chart */}
        <ReactECharts
          ref={chartRef}
          option={echartsOption}
          style={{
            width: '100%',
            height: chartHeight,
            minHeight: chartHeight
          }}
          onChartReady={onChartReady}
          opts={{
            renderer: 'canvas',
            useDirtyRect: false
          }}
        />

        {/* Chart Info */}
        {chartData.title && (
          <Typography
            variant="caption"
            sx={{
              display: 'block',
              textAlign: 'center',
              mt: 1,
              color: '#64748b',
              fontStyle: 'italic',
            }}
          >
            {chartData.ai_generated && '🤖 AI Generated • '}
            {chartData.title}
          </Typography>
        )}
        </Box>
      </motion.div>
    );
  } catch (err) {
    console.error('Error rendering ECharts:', err);
    return (
      <Alert severity="error" sx={{ borderRadius: '12px' }}>
        Error rendering chart: {err.message}
      </Alert>
    );
  }
};

export default EChartsChart;
