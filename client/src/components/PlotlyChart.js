/**
 * PlotlyChart Component
 * Renders interactive Plotly charts with colors and advanced features
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Download,
  Fullscreen,
  Psychology,
  Palette,
} from '@mui/icons-material';

// Dynamically import Plotly to avoid SSR issues
const Plot = React.lazy(() => import('react-plotly.js'));

const PlotlyChart = ({ 
  chartData, 
  compact = false, 
  showControls = true,
  onToggleChartType = null 
}) => {
  const [isFullscreen, setIsFullscreen] = React.useState(false);
  const [useInteractive, setUseInteractive] = React.useState(true);

  if (!chartData || !chartData.plotly_config) {
    return null;
  }

  const { plotly_config, title, ai_generated } = chartData;

  // Handle fullscreen toggle
  const handleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  // Handle download
  const handleDownload = () => {
    const dataStr = JSON.stringify(plotly_config, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${title.replace(/\s+/g, '_').toLowerCase()}_plotly_config.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Plotly configuration
  const config = {
    displayModeBar: useInteractive,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
    displaylogo: false,
    responsive: true,
    toImageButtonOptions: {
      format: 'png',
      filename: title.replace(/\s+/g, '_').toLowerCase(),
      height: 500,
      width: 700,
      scale: 1
    }
  };

  // Layout updates for responsive design
  const layout = {
    ...plotly_config.config.layout,
    autosize: true,
    margin: compact ? 
      { l: 40, r: 40, t: 60, b: 40 } : 
      { l: 50, r: 50, t: 80, b: 50 },
    height: isFullscreen ? window.innerHeight - 200 : (compact ? 300 : 400),
    font: {
      family: "Arial, sans-serif",
      size: compact ? 10 : 12,
      color: '#333'
    },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
  };

  return (
    <Card
      sx={{
        mt: 2,
        mb: 1,
        maxWidth: isFullscreen ? '95vw' : (compact ? 400 : 800),
        width: isFullscreen ? '95vw' : 'auto',
        boxShadow: ai_generated ? 3 : 2,
        border: ai_generated ? '2px solid #9c27b0' : '1px solid #e0e0e0',
        background: ai_generated ? 'linear-gradient(135deg, #f3e5f5 0%, #ffffff 100%)' : 'white',
        position: isFullscreen ? 'fixed' : 'relative',
        top: isFullscreen ? '50%' : 'auto',
        left: isFullscreen ? '50%' : 'auto',
        transform: isFullscreen ? 'translate(-50%, -50%)' : 'none',
        zIndex: isFullscreen ? 9999 : 'auto',
        '&::before': ai_generated ? {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: 'linear-gradient(90deg, #9c27b0, #673ab7, #3f51b5)',
          borderRadius: '4px 4px 0 0'
        } : {}
      }}
    >
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <Palette sx={{ color: '#092f57' }} />
            <Typography variant={compact ? "subtitle2" : "h6"} fontWeight="bold">
              {title}
            </Typography>
            {ai_generated && (
              <Tooltip title="AI-Generated Plotly Visualization">
                <Psychology sx={{ color: '#9c27b0', fontSize: 18 }} />
              </Tooltip>
            )}
            <Typography variant="caption" sx={{ ml: 1, color: '#666' }}>
              Interactive Plotly Chart
            </Typography>
          </Box>
        }
        action={
          showControls && (
            <Box display="flex" alignItems="center" gap={1}>
              {onToggleChartType && (
                <FormControlLabel
                  control={
                    <Switch
                      checked={useInteractive}
                      onChange={(e) => setUseInteractive(e.target.checked)}
                      size="small"
                    />
                  }
                  label="Interactive"
                  sx={{ mr: 1 }}
                />
              )}
              <Tooltip title="Toggle Fullscreen">
                <IconButton size="small" onClick={handleFullscreen}>
                  <Fullscreen />
                </IconButton>
              </Tooltip>
              <Tooltip title="Download Chart Config">
                <IconButton size="small" onClick={handleDownload}>
                  <Download />
                </IconButton>
              </Tooltip>
            </Box>
          )
        }
        sx={{ pb: 1 }}
      />
      <CardContent sx={{ pt: 0 }}>
        <React.Suspense 
          fallback={
            <Box 
              display="flex" 
              justifyContent="center" 
              alignItems="center" 
              height={compact ? 300 : 400}
            >
              <Typography>Loading interactive chart...</Typography>
            </Box>
          }
        >
          <Plot
            data={plotly_config.config.data}
            layout={layout}
            config={config}
            style={{ width: '100%', height: '100%' }}
            useResizeHandler={true}
          />
        </React.Suspense>

        {/* Chart Information */}
        <Box mt={2}>
          <Typography variant="caption" color="text.secondary">
            Chart Type: {plotly_config.chart_type} | 
            Data Points: {plotly_config.config.data?.[0]?.x?.length || plotly_config.config.data?.[0]?.labels?.length || 0}
            {ai_generated && (
              <span style={{ marginLeft: '8px', color: '#9c27b0' }}>
                • AI-Generated with Plotly
              </span>
            )}
          </Typography>
        </Box>

        {/* Interactive Features Info */}
        {useInteractive && (
          <Box 
            mt={1} 
            p={1} 
            sx={{ 
              bgcolor: '#f5f5f5', 
              borderRadius: 1,
              border: '1px solid #e0e0e0'
            }}
          >
            <Typography variant="caption" color="text.primary">
              💡 Interactive Features: Hover for details, zoom, pan, download as image
            </Typography>
          </Box>
        )}

        {/* AI Generation Info */}
        {ai_generated && (
          <Box
            mt={2}
            p={2}
            sx={{
              bgcolor: '#f3e5f5',
              borderRadius: 1,
              border: '1px solid #9c27b0'
            }}
          >
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <Psychology sx={{ color: '#9c27b0', fontSize: 18 }} />
              <Typography variant="subtitle2" fontWeight="bold" color="#9c27b0">
                AI-Generated Plotly Visualization
              </Typography>
            </Box>
            <Typography variant="body2" color="text.primary">
              This interactive chart was generated by AI using your actual safety data. 
              You can interact with it, zoom, pan, and download it as an image.
            </Typography>
          </Box>
        )}
      </CardContent>

      {/* Fullscreen overlay */}
      {isFullscreen && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            bgcolor: 'rgba(0,0,0,0.8)',
            zIndex: 9998,
          }}
          onClick={handleFullscreen}
        />
      )}
    </Card>
  );
};

export default PlotlyChart;
