/**
 * Insights Streaming Test Component
 * Demonstrates the streaming functionality for insights panel
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid
} from '@mui/material';
import { PlayArrow as PlayIcon, Stop as StopIcon } from '@mui/icons-material';

import { InsightsStreamingEngine } from '../streaming';
import InsightsStreamingRenderer from '../streaming/InsightsStreamingRenderer';

const InsightsStreamingTest = () => {
  const [selectedModule, setSelectedModule] = useState('global-dashboard');
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingData, setStreamingData] = useState(null);
  const [streamingComplete, setStreamingComplete] = useState(false);

  const modules = [
    { id: 'global-dashboard', name: 'Global Dashboard' },
    { id: 'incident-investigation', name: 'Incident Investigation' },
    { id: 'action-tracking', name: 'Action Tracking' },
    { id: 'driver-safety', name: 'Driver Safety' },
    { id: 'observation-tracker', name: 'Observation Tracker' },
    { id: 'equipment-asset', name: 'Equipment Asset' },
    { id: 'employee-training', name: 'Employee Training' },
    { id: 'risk-assessment', name: 'Risk Assessment' }
  ];

  const startStreaming = () => {
    console.log('🚀 Starting insights streaming test for module:', selectedModule);
    setIsStreaming(true);
    setStreamingComplete(false);
    
    const dashboardContext = {
      activeModule: selectedModule,
      filters: { daysBack: 30 },
      dateRange: { isCustom: false }
    };
    
    const streamData = InsightsStreamingEngine.generateInsightsStream(
      selectedModule, 
      dashboardContext, 
      'comprehensive'
    );
    
    setStreamingData(streamData);
  };

  const stopStreaming = () => {
    console.log('⏹️ Stopping insights streaming test');
    setIsStreaming(false);
    setStreamingData(null);
    setStreamingComplete(false);
  };

  const handleStreamingComplete = (result) => {
    console.log('✅ Insights streaming test completed:', result);
    setStreamingComplete(true);
    setIsStreaming(false);
  };

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Insights Streaming Test
      </Typography>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Test Configuration
          </Typography>
          
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Select Module</InputLabel>
                <Select
                  value={selectedModule}
                  onChange={(e) => setSelectedModule(e.target.value)}
                  label="Select Module"
                  disabled={isStreaming}
                >
                  {modules.map((module) => (
                    <MenuItem key={module.id} value={module.id}>
                      {module.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  startIcon={<PlayIcon />}
                  onClick={startStreaming}
                  disabled={isStreaming}
                  sx={{
                    bgcolor: '#059669',
                    '&:hover': { bgcolor: '#047857' }
                  }}
                >
                  Start Streaming
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<StopIcon />}
                  onClick={stopStreaming}
                  disabled={!isStreaming}
                  sx={{
                    borderColor: '#dc2626',
                    color: '#dc2626',
                    '&:hover': { 
                      borderColor: '#b91c1c',
                      bgcolor: 'rgba(220, 38, 38, 0.1)'
                    }
                  }}
                >
                  Stop Streaming
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Streaming Renderer */}
      {isStreaming && streamingData && (
        <Card>
          <CardContent>
            <InsightsStreamingRenderer
              messages={streamingData.messages}
              timing={streamingData.timing}
              onComplete={handleStreamingComplete}
              moduleId={selectedModule}
              analysisType={streamingData.analysisType}
              context={streamingData.context}
            />
          </CardContent>
        </Card>
      )}

      {/* Completion Status */}
      {streamingComplete && (
        <Card sx={{ mt: 2, bgcolor: 'success.light' }}>
          <CardContent>
            <Typography variant="h6" sx={{ color: 'success.contrastText' }}>
              ✅ Streaming Test Completed Successfully!
            </Typography>
            <Typography variant="body2" sx={{ color: 'success.contrastText', mt: 1 }}>
              The insights streaming functionality is working correctly. You can now integrate this into the main insights panel.
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      <Card sx={{ mt: 3, bgcolor: 'info.light' }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: 'info.contrastText', mb: 1 }}>
            How to Use
          </Typography>
          <Typography variant="body2" sx={{ color: 'info.contrastText' }}>
            1. Select a module from the dropdown above
            2. Click "Start Streaming" to begin the AI analysis simulation
            3. Watch the step-by-step analysis process with animations
            4. The streaming shows how AI processes data and generates insights
            5. This demonstrates the same functionality that will be integrated into the main insights panel
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default InsightsStreamingTest; 