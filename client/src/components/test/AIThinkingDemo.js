/**
 * AI Thinking Steps Demo Component
 * Demonstrates the enhanced AI thinking process with different complexity levels
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField
} from '@mui/material';
import {
  Psychology as BrainIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';

import StreamingThinkingIndicator from '../chatbot/streaming/StreamingThinkingIndicator';
import { useDashboardContext } from '../../contexts/DashboardContext';

const AIThinkingDemo = () => {
  const { context } = useDashboardContext();
  const [isRunning, setIsRunning] = useState(false);
  const [selectedQuery, setSelectedQuery] = useState('');
  const [customQuery, setCustomQuery] = useState('');
  const [selectedModule, setSelectedModule] = useState('incident-investigation');
  const [currentDemo, setCurrentDemo] = useState(null);

  // Demo queries with different complexity levels
  const demoQueries = {
    simple: [
      "Show recent incidents",
      "Display driver safety status",
      "List open actions",
      "Show equipment count"
    ],
    medium: [
      "Analyze incident trends over the last 3 months",
      "Create a chart showing action completion rates",
      "Compare driver safety compliance across departments",
      "Show risk assessment distribution by category"
    ],
    complex: [
      "Provide comprehensive analysis of safety performance with correlations between incidents and training completion",
      "Generate detailed trend analysis comparing incident rates, action completion, and driver safety across all modules",
      "Create advanced visualization showing relationship between equipment failures and incident patterns",
      "Analyze cross-module safety patterns and provide AI-powered recommendations for improvement"
    ],
    'cross-module': [
      "Perform comprehensive safety assessment across all modules with predictive analytics",
      "Generate executive dashboard with AI insights correlating incidents, risks, actions, and training effectiveness",
      "Create advanced multi-dimensional analysis showing safety ecosystem relationships and optimization opportunities",
      "Provide strategic safety intelligence with machine learning insights across all safety management modules"
    ]
  };

  const modules = [
    { id: 'incident-investigation', name: 'Incident Investigation' },
    { id: 'risk-assessment', name: 'Risk Assessment' },
    { id: 'action-tracking', name: 'Action Tracking' },
    { id: 'driver-safety', name: 'Driver Safety' },
    { id: 'observation-tracker', name: 'Observation Tracker' },
    { id: 'equipment-asset', name: 'Equipment Asset' },
    { id: 'employee-training', name: 'Employee Training' }
  ];

  const handleStartDemo = (query, complexity) => {
    if (isRunning) return;
    
    setIsRunning(true);
    setCurrentDemo({ query, complexity });
    
    // Auto-stop after demo completes
    setTimeout(() => {
      setIsRunning(false);
      setCurrentDemo(null);
    }, getComplexityDuration(complexity) + 2000);
  };

  const handleStopDemo = () => {
    setIsRunning(false);
    setCurrentDemo(null);
  };

  const handleCustomDemo = () => {
    if (!customQuery.trim() || isRunning) return;
    handleStartDemo(customQuery, 'medium');
  };

  const getComplexityDuration = (complexity) => {
    const durations = {
      'simple': 4000,
      'medium': 6000,
      'complex': 10000,
      'cross-module': 15000
    };
    return durations[complexity] || 6000;
  };

  const getComplexityColor = (complexity) => {
    const colors = {
      'simple': 'success',
      'medium': 'warning',
      'complex': 'error',
      'cross-module': 'secondary'
    };
    return colors[complexity] || 'primary';
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <BrainIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            AI Thinking Steps Demo
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Experience how our AI processes different types of safety queries with intelligent step-by-step thinking
          </Typography>
        </motion.div>
      </Box>

      {/* Demo Controls */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            Demo Controls
          </Typography>
          
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Active Module</InputLabel>
                <Select
                  value={selectedModule}
                  onChange={(e) => setSelectedModule(e.target.value)}
                  label="Active Module"
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
              <TextField
                fullWidth
                size="small"
                label="Custom Query"
                value={customQuery}
                onChange={(e) => setCustomQuery(e.target.value)}
                placeholder="Enter your own query to test..."
              />
            </Grid>
            
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleCustomDemo}
                disabled={isRunning || !customQuery.trim()}
                startIcon={<PlayIcon />}
              >
                Test
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Demo Sections */}
      <Grid container spacing={3}>
        {Object.entries(demoQueries).map(([complexity, queries]) => (
          <Grid item xs={12} md={6} key={complexity}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Chip 
                    label={complexity.charAt(0).toUpperCase() + complexity.slice(1)} 
                    color={getComplexityColor(complexity)}
                    variant="filled"
                    sx={{ fontWeight: 600 }}
                  />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Queries
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {queries.map((query, index) => (
                    <Button
                      key={index}
                      variant="outlined"
                      size="small"
                      onClick={() => handleStartDemo(query, complexity)}
                      disabled={isRunning}
                      sx={{ 
                        justifyContent: 'flex-start',
                        textAlign: 'left',
                        textTransform: 'none',
                        p: 1.5
                      }}
                    >
                      {query}
                    </Button>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Demo Area */}
      {isRunning && currentDemo && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <Card sx={{ mt: 4, bgcolor: 'background.paper' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  AI Thinking Process Demo
                </Typography>
                <Button
                  variant="outlined"
                  color="error"
                  onClick={handleStopDemo}
                  startIcon={<StopIcon />}
                  size="small"
                >
                  Stop Demo
                </Button>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  Query: "{currentDemo.query}"
                </Typography>
                <Chip 
                  label={`Complexity: ${currentDemo.complexity}`}
                  color={getComplexityColor(currentDemo.complexity)}
                  size="small"
                />
              </Box>
              
              <Divider sx={{ mb: 3 }} />
              
              <StreamingThinkingIndicator
                userMessage={currentDemo.query}
                onComplete={() => {
                  console.log('Demo thinking process completed');
                  setTimeout(() => {
                    setIsRunning(false);
                    setCurrentDemo(null);
                  }, 2000);
                }}
                isVisible={isRunning}
                maxDuration={getComplexityDuration(currentDemo.complexity)}
              />
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Instructions */}
      {!isRunning && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <Card sx={{ mt: 4, bgcolor: 'info.light' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                How to Use This Demo
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Click any query button to see how AI processes different complexity levels
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Try custom queries in the text field to test your own scenarios
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Change the active module to see context-aware thinking steps
              </Typography>
              <Typography variant="body2">
                • Watch how AI thinking adapts based on query complexity and module context
              </Typography>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </Box>
  );
};

export default AIThinkingDemo;
