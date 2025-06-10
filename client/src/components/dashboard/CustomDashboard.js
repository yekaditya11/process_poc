/**
 * Custom Dashboard Component
 * Allows users to create custom dashboards with AI-generated charts from chatbot
 * Supports drag-and-drop, resizing, and chart management
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  Tooltip,
  Menu,
  MenuItem,
  Fab
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Dashboard as DashboardIcon,
  DragIndicator as DragIcon,
  Fullscreen as FullscreenIcon,
  MoreVert as MoreIcon,
  GridView as GridIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

// Import chart components
import EChartsChart from '../chatbot/EChartsChart';
import PlotlyChart from '../chatbot/PlotlyChart';

const CustomDashboard = ({ savedCharts = [], onSaveChart, onDeleteChart, onUpdateDashboard }) => {
  const [charts, setCharts] = useState(savedCharts);
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedChart, setSelectedChart] = useState(null);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [dashboardName, setDashboardName] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [gridSize, setGridSize] = useState(12); // Default grid size

  useEffect(() => {
    setCharts(savedCharts);
  }, [savedCharts]);

  // Handle drag end for reordering charts
  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const items = Array.from(charts);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setCharts(items);
    if (onUpdateDashboard) {
      onUpdateDashboard(items);
    }
  };

  // Handle chart deletion
  const handleDeleteChart = (chartId) => {
    const updatedCharts = charts.filter(chart =>
      chart.id !== chartId && chart.chart_id !== chartId
    );
    setCharts(updatedCharts);
    if (onDeleteChart) {
      onDeleteChart(chartId);
    }
  };

  // Handle saving dashboard
  const handleSaveDashboard = () => {
    if (!dashboardName.trim()) return;
    
    const dashboardConfig = {
      name: dashboardName,
      charts: charts,
      gridSize: gridSize,
      createdAt: new Date().toISOString()
    };

    if (onSaveChart) {
      onSaveChart(dashboardConfig);
    }
    
    setShowSaveDialog(false);
    setDashboardName('');
  };

  // Render individual chart
  const renderChart = (chart, index) => {
    const chartSize = chart.size || 6; // Default to half width
    const chartId = chart.chart_id || chart.id || `chart_${index}`;

    return (
      <Draggable
        key={chartId}
        draggableId={chartId}
        index={index}
        isDragDisabled={!isEditMode}
      >
        {(provided, snapshot) => (
          <Grid 
            item 
            xs={12} 
            md={chartSize}
            ref={provided.innerRef}
            {...provided.draggableProps}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.3 }}
              style={{
                transform: snapshot.isDragging ? 'rotate(5deg)' : 'none',
                zIndex: snapshot.isDragging ? 1000 : 1,
              }}
            >
              <Card
                sx={{
                  height: 400,
                  position: 'relative',
                  border: isEditMode ? '2px dashed #e0e7ff' : '1px solid #e5e7eb',
                  borderColor: snapshot.isDragging ? '#3b82f6' : undefined,
                  boxShadow: snapshot.isDragging 
                    ? '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
                    : '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                    transform: 'translateY(-2px)',
                  }
                }}
              >
                {/* Chart Header */}
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    p: 2,
                    borderBottom: '1px solid #e5e7eb',
                    bgcolor: '#f8fafc'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {isEditMode && (
                      <Box
                        {...provided.dragHandleProps}
                        sx={{
                          cursor: 'grab',
                          color: '#6b7280',
                          '&:hover': { color: '#374151' }
                        }}
                      >
                        <DragIcon fontSize="small" />
                      </Box>
                    )}
                    <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>
                      {chart.title}
                    </Typography>
                    <Chip
                      label="AI Generated"
                      size="small"
                      sx={{
                        bgcolor: '#dbeafe',
                        color: '#1e40af',
                        fontSize: '0.7rem',
                        height: 20
                      }}
                    />
                  </Box>

                  {isEditMode && (
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Tooltip title="Delete chart">
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteChart(chartId)}
                          sx={{
                            color: '#dc2626',
                            '&:hover': { bgcolor: 'rgba(220, 38, 38, 0.1)' }
                          }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  )}
                </Box>

                {/* Chart Content */}
                <CardContent sx={{ p: 2, height: 'calc(100% - 80px)' }}>
                  <Box sx={{ width: '100%', height: '100%' }}>
                    {(() => {
                      // Handle both chartData and chart_data properties
                      const chartData = chart.chartData || chart.chart_data;

                      if (!chartData) {
                        return (
                          <Box
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              height: '100%',
                              color: '#6b7280'
                            }}
                          >
                            <Typography>Chart data not available</Typography>
                          </Box>
                        );
                      }

                      if (chartData.type === 'echarts') {
                        return (
                          <EChartsChart
                            chartData={chartData}
                            isFullscreen={false}
                          />
                        );
                      } else if (chartData.type === 'plotly') {
                        return (
                          <PlotlyChart
                            chartData={chartData}
                            isFullscreen={false}
                          />
                        );
                      } else {
                        return (
                          <Box
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              height: '100%',
                              color: '#6b7280'
                            }}
                          >
                            <Typography>Unsupported chart type: {chartData.type}</Typography>
                          </Box>
                        );
                      }
                    })()}
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        )}
      </Draggable>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
            Custom Dashboard
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Drag and drop AI-generated charts to create your custom dashboard
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant={isEditMode ? "contained" : "outlined"}
            startIcon={<EditIcon />}
            onClick={() => setIsEditMode(!isEditMode)}
            sx={{
              bgcolor: isEditMode ? '#059669' : 'transparent',
              color: isEditMode ? 'white' : '#059669',
              borderColor: '#059669',
              '&:hover': {
                bgcolor: isEditMode ? '#047857' : 'rgba(5, 150, 105, 0.1)',
              }
            }}
          >
            {isEditMode ? 'Exit Edit' : 'Edit Mode'}
          </Button>

          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={() => setShowSaveDialog(true)}
            disabled={charts.length === 0}
            sx={{
              bgcolor: '#3b82f6',
              '&:hover': { bgcolor: '#2563eb' }
            }}
          >
            Save Dashboard
          </Button>
        </Box>
      </Box>

      {/* Charts Grid */}
      {charts.length === 0 ? (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: 400,
            border: '2px dashed #e5e7eb',
            borderRadius: 2,
            bgcolor: '#f8fafc'
          }}
        >
          <DashboardIcon sx={{ fontSize: 64, color: '#9ca3af', mb: 2 }} />
          <Typography variant="h6" color="textSecondary" gutterBottom>
            No charts added yet
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ textAlign: 'center', maxWidth: 400 }}>
            Start a conversation with the AI chatbot and add generated charts to your custom dashboard using the "+" button on each chart.
          </Typography>
        </Box>
      ) : (
        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="dashboard-charts">
            {(provided) => (
              <Grid
                container
                spacing={3}
                ref={provided.innerRef}
                {...provided.droppableProps}
              >
                <AnimatePresence>
                  {charts.map((chart, index) => renderChart(chart, index))}
                </AnimatePresence>
                {provided.placeholder}
              </Grid>
            )}
          </Droppable>
        </DragDropContext>
      )}

      {/* Save Dashboard Dialog */}
      <Dialog open={showSaveDialog} onClose={() => setShowSaveDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Save Custom Dashboard</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Dashboard Name"
            fullWidth
            variant="outlined"
            value={dashboardName}
            onChange={(e) => setDashboardName(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSaveDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleSaveDashboard}
            variant="contained"
            disabled={!dashboardName.trim()}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CustomDashboard;
