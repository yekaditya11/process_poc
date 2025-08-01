/**
 * Enhanced AI Thinking Steps Renderer
 * Shows detailed step-by-step AI thinking process with engaging animations
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Chip,
  Fade,
  Grow,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Avatar,
  Divider
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  Psychology as BrainIcon,
  Search as SearchIcon,
  Analytics as AnalyticsIcon,
  AutoAwesome as SparkleIcon,
  DataObject as DataIcon,
  TrendingUp as TrendIcon,
  Lightbulb as InsightIcon,
  Speed as ProcessIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import './StreamingMessageRenderer.css';

// Enhanced thinking step icons mapping
const getStepIcon = (message, isActive, isCompleted) => {
  const iconProps = {
    sx: {
      fontSize: 20,
      color: isCompleted ? 'success.main' : isActive ? 'primary.main' : 'grey.400'
    }
  };

  if (message.includes('🔍') || message.includes('Analyzing')) return <SearchIcon {...iconProps} />;
  if (message.includes('📊') || message.includes('data')) return <DataIcon {...iconProps} />;
  if (message.includes('🧠') || message.includes('thinking')) return <BrainIcon {...iconProps} />;
  if (message.includes('📈') || message.includes('trend')) return <TrendIcon {...iconProps} />;
  if (message.includes('💡') || message.includes('insight')) return <InsightIcon {...iconProps} />;
  if (message.includes('⚡') || message.includes('processing')) return <ProcessIcon {...iconProps} />;
  if (message.includes('✨') || message.includes('generating')) return <SparkleIcon {...iconProps} />;

  return isCompleted ? <CheckCircleIcon {...iconProps} /> :
         isActive ? <RadioButtonUncheckedIcon {...iconProps} className="rotating-icon" /> :
         <RadioButtonUncheckedIcon {...iconProps} />;
};

const StreamingMessageRenderer = ({
  messages,
  timing,
  onComplete,
  analysis,
  complexity
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [isComplete, setIsComplete] = useState(false);
  const [progress, setProgress] = useState(0);
  const [thinkingDetails, setThinkingDetails] = useState('');
  const timeoutRef = useRef(null);
  const startTimeRef = useRef(Date.now());

  // Enhanced thinking details for each step
  const getThinkingDetails = (stepIndex, message) => {
    const details = {
      0: "Parsing your question and identifying key safety concepts...",
      1: "Determining which safety modules contain relevant data...",
      2: "Establishing database connections and preparing queries...",
      3: "Executing optimized SQL queries across safety databases...",
      4: "Processing raw data and calculating key performance indicators...",
      5: "Applying AI algorithms to identify patterns and trends...",
      6: "Cross-referencing data points for comprehensive analysis...",
      7: "Generating contextual insights based on safety best practices...",
      8: "Formatting results and preparing visualizations...",
      9: "Finalizing response with actionable recommendations..."
    };

    return details[stepIndex] || "Processing your request with advanced AI algorithms...";
  };

  useEffect(() => {
    if (messages.length === 0) return;

    startTimeRef.current = Date.now();
    setCurrentStep(0);
    setCompletedSteps([]);
    setIsComplete(false);
    setProgress(0);
    setThinkingDetails('');

    const executeStep = (stepIndex) => {
      if (stepIndex >= messages.length) {
        setIsComplete(true);
        setProgress(100);
        setThinkingDetails('Analysis complete! Ready to provide insights.');
        if (onComplete) {
          setTimeout(onComplete, 800); // Slightly longer delay for better UX
        }
        return;
      }

      setCurrentStep(stepIndex);
      setThinkingDetails(getThinkingDetails(stepIndex, messages[stepIndex]));

      // Update progress
      const progressValue = ((stepIndex + 1) / messages.length) * 100;
      setProgress(progressValue);

      const stepDuration = timing[stepIndex] || 1000;

      timeoutRef.current = setTimeout(() => {
        setCompletedSteps(prev => [...prev, stepIndex]);
        executeStep(stepIndex + 1);
      }, stepDuration);
    };

    executeStep(0);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [messages, timing, onComplete]);

  const getStepColor = (stepIndex) => {
    if (completedSteps.includes(stepIndex)) return 'success.main';
    if (stepIndex === currentStep && !isComplete) return 'primary.main';
    return 'grey.500';
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

  const formatElapsedTime = () => {
    const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
    return `${elapsed}s`;
  };

  const getComplexityDescription = (complexity) => {
    const descriptions = {
      'simple': 'Quick analysis of basic safety metrics',
      'medium': 'Comprehensive analysis across multiple data points',
      'complex': 'Deep analysis with cross-module correlations',
      'cross-module': 'Advanced multi-module safety assessment'
    };
    return descriptions[complexity] || 'Processing safety data';
  };

  return (
    <Card
      elevation={0}
      sx={{
        maxWidth: 500,
        background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 3
      }}
    >
      <CardContent sx={{ p: 3 }}>
        {/* AI Thinking Header */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <motion.div
              animate={{
                rotate: isComplete ? 0 : [0, 360],
                scale: [1, 1.1, 1]
              }}
              transition={{
                rotate: { duration: 2, repeat: isComplete ? 0 : Infinity, ease: "linear" },
                scale: { duration: 1.5, repeat: Infinity, ease: "easeInOut" }
              }}
            >
              <Avatar sx={{
                bgcolor: 'primary.main',
                width: 40,
                height: 40,
                boxShadow: '0 4px 12px rgba(25, 118, 210, 0.3)'
              }}>
                <BrainIcon />
              </Avatar>
            </motion.div>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary' }}>
                AI Safety Analysis
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                {isComplete ? 'Analysis Complete' : 'Processing your request...'}
              </Typography>
            </Box>
          </Box>

          {/* Enhanced Progress Bar */}
          <Box sx={{ mb: 2 }}>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 4,
                  background: 'linear-gradient(90deg, #1976d2 0%, #42a5f5 100%)'
                }
              }}
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                {Math.round(progress)}% Complete
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                {formatElapsedTime()}
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Enhanced Stepper */}
        <Stepper
          orientation="vertical"
          activeStep={currentStep}
          sx={{
            '& .MuiStepConnector-line': {
              minHeight: 20,
              borderLeftWidth: '2px',
              borderColor: 'primary.main'
            },
            '& .MuiStepConnector-root': {
              left: 16,
              top: 32
            }
          }}
        >
          {messages.map((message, index) => (
            <Step key={index} completed={completedSteps.includes(index)}>
              <StepLabel
                StepIconComponent={() => (
                  <motion.div
                    animate={{
                      scale: index === currentStep && !isComplete ? [1, 1.2, 1] : 1,
                      rotate: index === currentStep && !isComplete ? [0, 5, -5, 0] : 0
                    }}
                    transition={{
                      scale: { duration: 1, repeat: Infinity },
                      rotate: { duration: 0.5, repeat: Infinity }
                    }}
                  >
                    <Box
                      sx={{
                        width: 6,
                        height: 6,
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        bgcolor: completedSteps.includes(index) ? 'success.main' : 
                                 index === currentStep ? 'primary.main' : 'grey.400',
                        color: 'white',
                        fontSize: '0.25rem',
                        fontWeight: 600,
                        border: '0.5px solid',
                        borderColor: completedSteps.includes(index) ? 'success.dark' : 
                                    index === currentStep ? 'primary.dark' : 'grey.500'
                      }}
                    >
                      {completedSteps.includes(index) ? '✓' : ''}
                    </Box>
                  </motion.div>
                )}
                sx={{
                  '& .MuiStepLabel-label': {
                    color: getStepColor(index),
                    fontWeight: index === currentStep ? 600 : 400,
                    fontSize: '0.9rem'
                  }
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {message}
                  </Typography>
                  {index === currentStep && !isComplete && (
                    <motion.div
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          bgcolor: 'primary.main'
                        }}
                      />
                    </motion.div>
                  )}
                </Box>
              </StepLabel>
              <StepContent>
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <Typography
                    variant="body2"
                    sx={{
                      color: 'text.secondary',
                      fontStyle: 'italic',
                      pl: 2,
                      mt: 1
                    }}
                  >
                    {index === currentStep ? thinkingDetails : getThinkingDetails(index, message)}
                  </Typography>
                </motion.div>
              </StepContent>
            </Step>
          ))}
        </Stepper>

        {/* Completion Status */}
        {isComplete && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Box sx={{ mt: 3, p: 2, bgcolor: 'success.50', borderRadius: 2, border: '1px solid', borderColor: 'success.200' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CheckCircleIcon sx={{ color: 'success.main' }} />
                <Typography variant="body2" sx={{ color: 'success.main', fontWeight: 600 }}>
                  Analysis Complete
                </Typography>
              </Box>
              <Typography variant="caption" sx={{ color: 'success.dark', display: 'block', mt: 0.5 }}>
                Ready to provide comprehensive safety insights
              </Typography>
            </Box>
          </motion.div>
        )}
      </CardContent>
    </Card>
  );
};

export default StreamingMessageRenderer;
