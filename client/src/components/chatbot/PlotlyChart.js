/**
 * PlotlyChart Component
 * Renders Plotly charts within the chatbot interface
 * Version: 2024-12-07 - Fixed hover values visibility
 */

import React, { useEffect, useRef, useState } from 'react';
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

// Dynamically import Plotly to avoid SSR issues
let Plot = null;
if (typeof window !== 'undefined') {
  import('react-plotly.js').then((module) => {
    Plot = module.default;
  }).catch((error) => {
    console.error('Failed to load Plotly:', error);
  });
}

const PlotlyChart = ({ chartData, isFullscreen = false }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [plotlyLoaded, setPlotlyLoaded] = useState(false);
  const plotRef = useRef(null);

  // Debug logging
  console.log('PlotlyChart received chartData:', chartData);

  useEffect(() => {
    // Check if Plotly is loaded
    const checkPlotly = async () => {
      try {
        if (typeof window !== 'undefined') {
          const module = await import('react-plotly.js');
          Plot = module.default;
          setPlotlyLoaded(true);
        }
      } catch (err) {
        console.error('Error loading Plotly:', err);
        setError('Failed to load chart library');
      } finally {
        setIsLoading(false);
      }
    };

    checkPlotly();
  }, []);

  // Handle chart resize when fullscreen mode changes
  useEffect(() => {
    if (plotRef.current && plotlyLoaded) {
      // Small delay to allow for layout changes
      const timer = setTimeout(() => {
        if (plotRef.current && plotRef.current.resizeHandler) {
          plotRef.current.resizeHandler();
        }
      }, 300);

      return () => clearTimeout(timer);
    }
  }, [isFullscreen, plotlyLoaded]);

  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: 200,
          gap: 2,
        }}
      >
        <CircularProgress size={24} />
        <Typography variant="body2" color="text.secondary">
          Loading chart...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ my: 2 }}>
        {error}
        <Typography variant="body2" sx={{ mt: 1, fontSize: '0.75rem' }}>
          Debug: Chart data = {JSON.stringify(chartData, null, 2)}
        </Typography>
      </Alert>
    );
  }

  if (!chartData) {
    console.log('PlotlyChart: No chart data provided');
    return (
      <Alert severity="info" sx={{ my: 2 }}>
        No chart data provided
        <Typography variant="body2" sx={{ mt: 1, fontSize: '0.75rem' }}>
          Debug: chartData is {typeof chartData}: {JSON.stringify(chartData)}
        </Typography>
      </Alert>
    );
  }

  if (!plotlyLoaded || !Plot) {
    return (
      <Alert severity="warning" sx={{ my: 2 }}>
        Chart library not loaded (plotlyLoaded: {plotlyLoaded.toString()}, Plot: {Plot ? 'available' : 'null'})
        <Typography variant="body2" sx={{ mt: 1, fontSize: '0.75rem' }}>
          Chart data: {JSON.stringify(chartData, null, 2)}
        </Typography>
      </Alert>
    );
  }

  // Process chart data based on type
  const processChartData = () => {
    try {
      console.log('Processing chart data:', chartData);

      // If chartData has Plotly config, use it directly
      if (chartData.config) {
        console.log('Using Plotly config directly:', chartData.config);
        // The config contains the full Plotly figure with data and layout
        const plotlyConfig = chartData.config;
        return {
          data: plotlyConfig.data || [],
          layout: plotlyConfig.layout || {},
          config: { displayModeBar: false, responsive: true }
        };
      }

      // If chartData type is 'plotly' and has config, use it
      if (chartData.type === 'plotly' && chartData.config) {
        console.log('Using Plotly config from type plotly:', chartData.config);
        const plotlyConfig = chartData.config;
        return {
          data: plotlyConfig.data || [],
          layout: plotlyConfig.layout || {},
          config: { displayModeBar: false, responsive: true }
        };
      }

      // Handle simple chart data formats from server or AI-generated charts
      const chartType = chartData.type || 'bar';
      const chartTitle = chartData.title || 'Chart';
      const chartDataArray = chartData.data || [];

      if (!chartDataArray || chartDataArray.length === 0) {
        throw new Error(`No data provided for chart. Chart type: ${chartType}, Data: ${JSON.stringify(chartDataArray)}`);
      }

      // Validate data structure
      const validData = chartDataArray.filter(item =>
        item &&
        typeof item === 'object' &&
        (item.name || item.label || item.x) &&
        (typeof item.value === 'number' || typeof item.y === 'number' || !isNaN(Number(item.value || item.y)))
      );

      if (validData.length === 0) {
        throw new Error(`No valid data items found. Chart type: ${chartType}, Original data: ${JSON.stringify(chartDataArray)}`);
      }

      console.log(`Processing simple chart - Type: ${chartType}, Title: ${chartTitle}, Valid data length: ${validData.length}/${chartDataArray.length}`);

      // Create enhanced Plotly configuration with better value display
      let plotData;

      if (chartType === 'donut' || chartType === 'pie') {
        const labels = validData.map(item => String(item.name || item.label || item.x || 'Unknown'));
        const values = validData.map(item => Number(item.value || item.y || 0));

        // Generate better colors
        const colors = [
          '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ];

        plotData = [{
          labels: labels,
          values: values,
          type: 'pie',
          hole: chartType === 'donut' ? 0.4 : 0,
          marker: {
            colors: validData.map((item, index) => item.color || colors[index % colors.length]),
            line: {
              color: '#ffffff',
              width: 2
            }
          },
          textinfo: 'percent',
          textposition: 'inside',
          insidetextorientation: 'radial',

          textfont: {
            size: 11,
            color: '#ffffff'
          }
        }];

        console.log('Pie/Donut chart data:', { labels, values, validData });
      } else if (chartType === 'heatmap') {
        // Handle heatmap charts
        const names = chartDataArray.map(item => item.name || item.label || item.x || 'Unknown');
        const values = chartDataArray.map(item => item.value || item.y || 0);

        plotData = [{
          z: [values], // Single row heatmap
          x: names,
          y: ['Value'],
          type: 'heatmap',
          colorscale: 'RdYlBu_r',
          hoverongaps: false,
          hovertemplate: '<b>%{x}</b><br>Value: %{z}<extra></extra>',
          showscale: true
        }];
      } else {
        const xData = validData.map(item => String(item.name || item.label || item.x || 'Unknown'));
        const yData = validData.map(item => Number(item.value || item.y || 0));

        // Generate better colors for bar charts
        const colors = [
          '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ];

        // Create a simple, reliable trace configuration
        const trace = {
          x: xData,
          y: yData,
          type: chartType === 'line' ? 'scatter' : chartType,
          name: 'Count',
          text: yData.map(val => `${val}`),
          textposition: 'outside',
          textfont: {
            size: 12,
            color: '#000'
          },

          showlegend: false
        };

        // Add mode for line charts
        if (chartType === 'line') {
          trace.mode = 'lines+markers';
          trace.line = {
            color: '#1976d2',
            width: 3
          };
          trace.marker = {
            color: '#1976d2',
            size: 8
          };
        } else {
          // Add marker configuration for bar/scatter charts
          trace.marker = {
            color: validData.map((item, index) => item.color || colors[index % colors.length]),
            line: {
              color: 'rgba(255,255,255,0.6)',
              width: 1
            },
            opacity: 0.8
          };

          if (chartType === 'scatter') {
            trace.marker.size = 10;
          }

          // Ensure hover works properly for bars
          if (chartType === 'bar') {
            // Let hovertemplate handle the display
          }
        }

        // Keep it simple - let Plotly handle hover automatically

        plotData = [trace];
        console.log('Bar/Line/Scatter chart data:', {
          chartType,
          xData,
          yData,
          validData,
          trace: trace
        });
      }

      // Create responsive layout configuration based on fullscreen mode
      const layout = {
        title: {
          text: chartTitle,
          font: { size: isFullscreen ? 18 : 14, color: '#092f57' },
          x: 0.5,
          pad: { t: isFullscreen ? 30 : 20 }
        },
        margin: {
          l: chartType === 'donut' || chartType === 'pie' ? (isFullscreen ? 60 : 40) : (isFullscreen ? 100 : 70),
          r: chartType === 'donut' || chartType === 'pie' ? (isFullscreen ? 60 : 40) : (isFullscreen ? 80 : 50),
          t: isFullscreen ? 100 : 70,
          b: chartType === 'donut' || chartType === 'pie' ? (isFullscreen ? 60 : 40) : (isFullscreen ? 100 : 70)
        },
        autosize: true,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Roboto, sans-serif', size: isFullscreen ? 14 : 11 }
      };

      // Add legend for pie/donut charts with responsive sizing
      if (chartType === 'donut' || chartType === 'pie') {
        layout.showlegend = true;
        layout.legend = {
          orientation: isFullscreen ? 'v' : 'h',
          x: isFullscreen ? 1.02 : 0.5,
          xanchor: isFullscreen ? 'left' : 'center',
          y: isFullscreen ? 0.5 : -0.1,
          yanchor: isFullscreen ? 'middle' : 'top',
          font: { size: isFullscreen ? 12 : 10 },
          bgcolor: 'rgba(255,255,255,0.8)',
          bordercolor: 'rgba(0,0,0,0.1)',
          borderwidth: 1
        };
      } else {
        layout.showlegend = false;
      }

      // Add axes for non-pie charts with responsive sizing
      if (chartType !== 'donut' && chartType !== 'pie') {
        layout.xaxis = {
          showgrid: true,
          gridcolor: 'rgba(0,0,0,0.1)',
          tickfont: { size: isFullscreen ? 12 : 9 },
          tickangle: -45,
          automargin: true,
          title: {
            text: '',
            font: { size: isFullscreen ? 14 : 11 }
          }
        };
        layout.yaxis = {
          showgrid: true,
          gridcolor: 'rgba(0,0,0,0.1)',
          tickfont: { size: isFullscreen ? 12 : 9 },
          automargin: true,
          title: {
            text: 'Count',
            font: { size: isFullscreen ? 14 : 11 }
          }
        };
      }

      // Disable hover completely
      layout.hovermode = false;

      // Add donut center annotation
      if (chartType === 'donut') {
        layout.annotations = [{
          text: `<b>Total</b><br>${validData.reduce((sum, item) => sum + (item.value || 0), 0)}`,
          x: 0.5,
          y: 0.5,
          xref: 'paper',
          yref: 'paper',
          showarrow: false,
          font: { size: 14, color: '#333' },
          align: 'center'
        }];
      }

      const config = {
        displayModeBar: false,
        responsive: true,
        showTips: false,
        showAxisDragHandles: false,
        showAxisRangeEntryBoxes: false,
        doubleClick: 'reset',
        staticPlot: false,
        scrollZoom: false,
        editable: false,
        autosizable: true
      };

      return { data: plotData, layout, config };
    } catch (err) {
      console.error('Error processing chart data:', err);
      throw new Error('Failed to process chart data');
    }
  };

  const handleDownload = () => {
    if (plotRef.current) {
      // Use Plotly's built-in download functionality
      const plotElement = plotRef.current.el;
      if (plotElement && window.Plotly) {
        window.Plotly.downloadImage(plotElement, {
          format: 'png',
          width: 800,
          height: 600,
          filename: 'safety-chart'
        });
      }
    }
  };

  const handleFullscreen = () => {
    // Implement fullscreen functionality
    console.log('Fullscreen chart');
  };

  try {
    const { data, layout, config } = processChartData();

    console.log('Final chart data for rendering:', {
      dataLength: data?.length,
      layoutTitle: layout?.title?.text,
      chartType: chartData.type,
      hasConfig: !!chartData.config
    });

    // Dynamic sizing based on fullscreen mode
    const chartHeight = isFullscreen ? '500px' : '350px';
    const containerMinHeight = isFullscreen ? '500px' : '350px';

    return (
      <Box sx={{
        position: 'relative',
        width: '100%',
        minHeight: containerMinHeight,
        height: 'auto',
        '& .plotly': {
          width: '100% !important',
          height: '100% !important'
        },
        '& .plotly .main-svg': {
          overflow: 'visible !important'
        },
        '& .hoverlayer': {
          pointerEvents: 'none !important'
        }
      }}>
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
          <Tooltip title="Download chart">
            <IconButton
              size="small"
              onClick={handleDownload}
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.8)',
                '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.9)' },
              }}
            >
              <DownloadIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Fullscreen">
            <IconButton
              size="small"
              onClick={handleFullscreen}
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.8)',
                '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.9)' },
              }}
            >
              <FullscreenIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Plotly Chart */}
        <Plot
          ref={plotRef}
          data={data}
          layout={layout}
          config={{
            ...config,
            displayModeBar: false,
            responsive: true,
            toImageButtonOptions: {
              format: 'png',
              filename: 'chart',
              height: isFullscreen ? 600 : 400,
              width: isFullscreen ? 900 : 600,
              scale: 1
            }
          }}
          style={{
            width: '100%',
            height: chartHeight,
            minHeight: chartHeight
          }}
          useResizeHandler={true}
          onInitialized={() => console.log('Plotly chart initialized successfully')}
          onError={(err) => console.error('Plotly chart error:', err)}

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
    );
  } catch (err) {
    console.error('Error rendering chart:', err);
    console.error('Chart data that caused error:', chartData);
    return (
      <Alert severity="error" sx={{ my: 2 }}>
        Failed to render chart: {err.message}
        <Typography variant="body2" sx={{ mt: 1, fontSize: '0.75rem' }}>
          Debug: {JSON.stringify(chartData, null, 2)}
        </Typography>
      </Alert>
    );
  }
};

export default PlotlyChart;
