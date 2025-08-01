/**
 * Streaming Test Component
 * Test component to verify the context-aware streaming system
 */

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Grid
} from '@mui/material';
import { DashboardContextProvider, useDashboardContext } from '../../contexts/DashboardContext';
import StreamingThinkingIndicator from '../chatbot/streaming/StreamingThinkingIndicator';
import { ContextAwareStreaming } from '../chatbot/streaming/ContextAwareStreaming';

const StreamingTestInner = () => {
  const { context, setActiveModule, setFilters } = useDashboardContext();
  const [testMessage, setTestMessage] = useState('Show me recent incidents');
  const [isStreaming, setIsStreaming] = useState(false);
  const [lastResult, setLastResult] = useState(null);

  const testMessages = [
    'Show me recent incidents',
    'Create a chart for driver safety',
    'Analyze risk assessment trends',
    'Compare incidents and actions',
    'Show equipment maintenance status',
    'Generate training compliance report',
    'What are the observation patterns?',
    'Display comprehensive safety metrics'
  ];

  const modules = [
    'global-dashboard',
    'incident-investigation',
    'risk-assessment',
    'action-tracking',
    'driver-safety',
    'observation-tracker',
    'equipment-asset',
    'employee-training'
  ];

  const handleModuleChange = (event) => {
    setActiveModule(event.target.value);
  };

  const handleDaysBackChange = (days) => {
    setFilters({ daysBack: days });
  };

  const handleTestStreaming = () => {
    setIsStreaming(true);
    setLastResult(null);
  };

  const handleStreamingComplete = (result) => {
    setIsStreaming(false);
    setLastResult(result);
  };

  const previewMessages = () => {
    const result = ContextAwareStreaming.previewMessages(testMessage, context);
    setLastResult(result);
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Context-Aware Streaming Test
      </Typography>

      <Grid container spacing={3}>
        {/* Controls */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Test Controls
            </Typography>

            {/* Module Selection */}
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Active Module</InputLabel>
              <Select
                value={context.activeModule}
                onChange={handleModuleChange}
                label="Active Module"
              >
                {modules.map(module => (
                  <MenuItem key={module} value={module}>
                    {module.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Days Back Filter */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Days Back Filter
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {[7, 30, 90, 365].map(days => (
                  <Chip
                    key={days}
                    label={`${days} days`}
                    onClick={() => handleDaysBackChange(days)}
                    color={context.filters.daysBack === days ? 'primary' : 'default'}
                    variant={context.filters.daysBack === days ? 'filled' : 'outlined'}
                  />
                ))}
              </Box>
            </Box>

            {/* Test Message */}
            <TextField
              fullWidth
              label="Test Message"
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              multiline
              rows={2}
              sx={{ mb: 2 }}
            />

            {/* Quick Test Messages */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Quick Test Messages
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {testMessages.map((message, index) => (
                  <Chip
                    key={index}
                    label={message}
                    onClick={() => setTestMessage(message)}
                    size="small"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                onClick={handleTestStreaming}
                disabled={isStreaming || !testMessage.trim()}
              >
                Test Streaming
              </Button>
              <Button
                variant="outlined"
                onClick={previewMessages}
                disabled={!testMessage.trim()}
              >
                Preview Messages
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Current Context */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Current Context
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Active Module:</strong> {context.activeModule}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Days Back:</strong> {context.filters.daysBack}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Custom Date Range:</strong> {context.dateRange.isCustom ? 'Yes' : 'No'}
              </Typography>
            </Box>

            {lastResult && (
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Last Analysis Result
                </Typography>
                <Box sx={{ mb: 1 }}>
                  <Chip label={`Type: ${lastResult.analysis?.questionType}`} size="small" />
                  <Chip label={`Complexity: ${lastResult.complexity}`} size="small" sx={{ ml: 1 }} />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  <strong>Messages:</strong> {lastResult.messages?.length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>Total Duration:</strong> {lastResult.timing?.reduce((sum, time) => sum + time, 0) || 0}ms
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Streaming Display */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, minHeight: 300 }}>
            <Typography variant="h6" gutterBottom>
              Streaming Display
            </Typography>
            
            {isStreaming ? (
              <StreamingThinkingIndicator
                userMessage={testMessage}
                onComplete={handleStreamingComplete}
                isVisible={isStreaming}
              />
            ) : (
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                minHeight: 200,
                color: 'text.secondary'
              }}>
                <Typography>
                  Click "Test Streaming" to see the context-aware streaming in action
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Message Preview */}
        {lastResult && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Generated Messages Preview
              </Typography>
              {lastResult.messages?.map((message, index) => (
                <Box key={index} sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="body2" sx={{ minWidth: 60 }}>
                    Step {index + 1}:
                  </Typography>
                  <Typography variant="body2">
                    {message}
                  </Typography>
                  <Chip 
                    label={`${lastResult.timing?.[index] || 0}ms`} 
                    size="small" 
                    variant="outlined" 
                  />
                </Box>
              ))}
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

const StreamingTest = () => {
  return (
    <DashboardContextProvider>
      <StreamingTestInner />
    </DashboardContextProvider>
  );
};

export default StreamingTest;
