/**
 * Test component to verify AI panel layout fixes
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Alert,
  Button,
  Paper
} from '@mui/material';

const AIPanelLayoutTest = () => {
  const [aiPanelOpen, setAiPanelOpen] = useState(false);
  const [eventLog, setEventLog] = useState([]);

  useEffect(() => {
    const handleAIPanelEvent = (event) => {
      const timestamp = new Date().toLocaleTimeString();
      const eventData = {
        timestamp,
        type: event.type,
        detail: event.detail || {}
      };
      
      setEventLog(prev => [eventData, ...prev.slice(0, 9)]); // Keep last 10 events
    };

    // Listen for AI panel events
    window.addEventListener('ai-panel-toggle', handleAIPanelEvent);
    window.addEventListener('chatbot-toggle', handleAIPanelEvent);
    window.addEventListener('resize', handleAIPanelEvent);

    return () => {
      window.removeEventListener('ai-panel-toggle', handleAIPanelEvent);
      window.removeEventListener('chatbot-toggle', handleAIPanelEvent);
      window.removeEventListener('resize', handleAIPanelEvent);
    };
  }, []);

  const handleToggle = () => {
    const newState = !aiPanelOpen;
    setAiPanelOpen(newState);

    // Simulate the improved event dispatch
    requestAnimationFrame(() => {
      window.dispatchEvent(new CustomEvent('ai-panel-toggle', {
        detail: { 
          insightsPanelOpen: newState,
          phase: 'start',
          panelWidth: newState ? '35%' : '0%'
        }
      }));
    });

    // Simulate mid-animation event
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('ai-panel-toggle', {
        detail: { 
          insightsPanelOpen: newState,
          phase: 'mid'
        }
      }));
      window.dispatchEvent(new Event('resize'));
    }, 200);

    // Simulate completion event
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('ai-panel-toggle', {
        detail: { 
          insightsPanelOpen: newState,
          phase: 'complete'
        }
      }));
      window.dispatchEvent(new Event('resize'));
    }, 450);
  };

  const clearLog = () => {
    setEventLog([]);
  };

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        AI Panel Layout Test
      </Typography>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            AI Panel Toggle Test
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={aiPanelOpen}
                onChange={handleToggle}
              />
            }
            label={`AI Panel ${aiPanelOpen ? 'Open' : 'Closed'}`}
          />
          
          {aiPanelOpen && (
            <Alert severity="success" sx={{ mt: 2 }}>
              ✅ AI Panel is open! Events should be firing with proper timing.
            </Alert>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Event Log
            </Typography>
            <Button onClick={clearLog} size="small">
              Clear Log
            </Button>
          </Box>
          
          <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
            {eventLog.length === 0 ? (
              <Typography color="text.secondary">
                No events logged yet. Toggle the AI panel to see events.
              </Typography>
            ) : (
              eventLog.map((event, index) => (
                <Paper
                  key={index}
                  sx={{
                    p: 2,
                    mb: 1,
                    bgcolor: event.type === 'ai-panel-toggle' ? '#e3f2fd' : '#f5f5f5'
                  }}
                >
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    {event.timestamp} - {event.type}
                  </Typography>
                  {event.detail && Object.keys(event.detail).length > 0 && (
                    <Typography variant="caption" component="pre" sx={{ mt: 1, display: 'block' }}>
                      {JSON.stringify(event.detail, null, 2)}
                    </Typography>
                  )}
                </Paper>
              ))
            )}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AIPanelLayoutTest;
