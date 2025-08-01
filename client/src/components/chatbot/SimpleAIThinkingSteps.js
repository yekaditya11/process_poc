/**
 * Single Card AI Thinking Steps Component
 * Shows AI thinking process as streaming text within a single message card
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Avatar,
  Paper,
  LinearProgress
} from '@mui/material';
import {
  SmartToy as BotIcon,
  Psychology as BrainIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const SimpleAIThinkingSteps = ({
  userMessage = "Processing your request",
  isApiComplete = false,
  apiStatus = null
}) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [displayedSteps, setDisplayedSteps] = useState([]);
  const [isComplete, setIsComplete] = useState(false);
  const [isLooping, setIsLooping] = useState(false);

  // Debug logging to confirm this component is being used
  console.log('🎯 SimpleAIThinkingSteps rendered with:', {
    userMessage,
    isApiComplete,
    apiStatus,
    currentStepIndex,
    displayedStepsCount: displayedSteps.length
  });

  // AI thinking steps
  const thinkingSteps = [
    "🧠 Understanding your safety query...",
    "🔍 Connecting to safety databases...",
    "📊 Analyzing safety data patterns...",
    "🧮 Calculating key performance metrics...",
    "💡 Generating AI-powered insights...",
    "✅ Preparing comprehensive response..."
  ];

  const stepDetails = [
    "Analyzing your question and identifying key safety concepts",
    "Establishing secure connections to safety management systems",
    "Processing incident, risk, and compliance data with AI algorithms",
    "Computing trends, correlations, and performance indicators",
    "Applying machine learning models for intelligent recommendations",
    "Formatting results with actionable safety insights"
  ];

  useEffect(() => {
    let timeoutId;
    let stepIndex = 0;

    const showNextStep = () => {
      if (stepIndex < thinkingSteps.length) {
        // Add the current step to displayed steps
        setDisplayedSteps(prev => [...prev, {
          text: thinkingSteps[stepIndex],
          detail: stepDetails[stepIndex],
          index: stepIndex,
          timestamp: new Date()
        }]);

        setCurrentStepIndex(stepIndex);
        stepIndex++;

        // Schedule next step
        if (stepIndex < thinkingSteps.length) {
          timeoutId = setTimeout(showNextStep, 1200); // 1.2 seconds between steps
        } else {
          // All initial steps shown, start looping if API not complete
          setIsLooping(true);
          if (!isApiComplete) {
            timeoutId = setTimeout(continueThinking, 1500);
          } else {
            setTimeout(() => setIsComplete(true), 500);
          }
        }
      }
    };

    const continueThinking = () => {
      if (!isApiComplete && !isComplete) {
        // Add additional thinking steps while waiting for API
        const additionalSteps = [
          "🔄 Refining analysis with additional data...",
          "🎯 Cross-referencing safety standards...",
          "📈 Optimizing recommendations...",
          "🔍 Validating insights for accuracy...",
          "⚡ Finalizing comprehensive response...",
          "🧠 Applying advanced AI reasoning..."
        ];

        const randomStep = additionalSteps[Math.floor(Math.random() * additionalSteps.length)];
        const randomDetail = "Continuing deep analysis to provide the most accurate and helpful safety insights";

        setDisplayedSteps(prev => [...prev, {
          text: randomStep,
          detail: randomDetail,
          index: prev.length,
          timestamp: new Date(),
          isLooping: true
        }]);

        // Continue looping every 2 seconds until API completes
        timeoutId = setTimeout(continueThinking, 2000);
      }
    };

    // Start showing steps after initial delay
    timeoutId = setTimeout(showNextStep, 300);

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, []);

  // Effect to handle API completion
  useEffect(() => {
    if (isApiComplete && !isComplete) {
      console.log('🎯 API completed, finishing thinking steps...');
      // Add final completion step
      setDisplayedSteps(prev => [...prev, {
        text: "✅ Response ready! Analysis complete.",
        detail: "Successfully processed your safety query with comprehensive insights",
        index: prev.length,
        timestamp: new Date(),
        isFinal: true
      }]);

      // Mark as complete after a short delay
      setTimeout(() => setIsComplete(true), 800);
    }
  }, [isApiComplete, isComplete]);

  // Format timestamp like other chat messages
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Calculate progress percentage
  const progress = (displayedSteps.length / thinkingSteps.length) * 100;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'flex-start',
        gap: 0.25,
        mb: 0.8,
      }}
    >
      {/* AI Avatar */}
      <Avatar
        sx={{
          width: 28,
          height: 28,
          bgcolor: 'primary.main',
          border: '2px solid rgba(255, 255, 255, 0.9)',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
          mt: 0.5,
        }}
      >
        <motion.div
          animate={{
            rotate: !isComplete ? [0, 360] : 0,
            scale: !isComplete ? [1, 1.1, 1] : 1
          }}
          transition={{
            rotate: { duration: 2, repeat: !isComplete ? Infinity : 0, ease: "linear" },
            scale: { duration: 1, repeat: !isComplete ? Infinity : 0, ease: "easeInOut" }
          }}
        >
          <BotIcon sx={{ fontSize: 16, color: 'white' }} />
        </motion.div>
      </Avatar>

      {/* Single Message Card with Streaming Content */}
      <Box sx={{ flex: 1, maxWidth: '85%' }}>
        <Paper
          elevation={1}
          sx={{
            p: 2,
            borderRadius: '18px 18px 18px 4px',
            background: isComplete
              ? 'linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%)'
              : '#f8fafc',
            border: isComplete
              ? '1px solid rgba(76, 175, 80, 0.2)'
              : '1px solid #e2e8f0',
            boxShadow: isComplete
              ? '0 2px 8px rgba(76, 175, 80, 0.1)'
              : '0 2px 8px rgba(0, 0, 0, 0.05)',
            transition: 'all 0.5s ease',
            position: 'relative'
          }}
        >




          {/* Streaming Steps */}
          <Box sx={{ minHeight: 120 }}>
            {displayedSteps.map((step, index) => (
              <motion.div
                key={step.index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, ease: "easeOut" }}
              >
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
                  {/* Step Number Circle */}
                  <Box sx={{ position: 'relative', flexShrink: 0 }}>
                    <motion.div
                      animate={{
                        scale: step.isLooping ? [1, 1.2, 1] : 1,
                        rotate: step.isLooping ? [0, 5, -5, 0] : 0
                      }}
                      transition={{
                        scale: { duration: 1, repeat: step.isLooping ? Infinity : 0 },
                        rotate: { duration: 0.5, repeat: step.isLooping ? Infinity : 0 }
                      }}
                    >
                      <Box
                        sx={{
                          width: 32,
                          height: 32,
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          bgcolor: step.isFinal ? 'success.main' :
                                   step.isLooping ? 'warning.main' : 'primary.main',
                          color: 'white',
                          fontSize: '0.875rem',
                          fontWeight: 600,
                          border: '2px solid',
                          borderColor: step.isFinal ? 'success.dark' :
                                      step.isLooping ? 'warning.dark' : 'primary.dark',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                        }}
                      >
                        {step.isFinal ? '✓' : step.isLooping ? '⟳' : (index + 1)}
                      </Box>
                    </motion.div>
                    
                    {/* Connecting Line */}
                    {index < displayedSteps.length - 1 && (
                      <Box
                        sx={{
                          position: 'absolute',
                          left: '50%',
                          top: '100%',
                          width: '2px',
                          height: '20px',
                          bgcolor: step.isFinal ? 'success.main' : 'primary.main',
                          transform: 'translateX(-50%)',
                          opacity: 0.6
                        }}
                      />
                    )}
                  </Box>

                  {/* Step Content */}
                  <Box sx={{ flex: 1, pt: 0.5 }}>
                    {/* Step Text */}
                    <Typography
                      variant="body2"
                      sx={{
                        color: step.isFinal ? 'success.main' :
                               step.isLooping ? 'warning.main' : 'text.primary',
                        fontWeight: step.isFinal ? 700 : 600,
                        fontSize: '0.9rem',
                        lineHeight: 1.4,
                        mb: 0.5
                      }}
                    >
                      {step.text}
                    </Typography>

                    {/* Step Detail */}
                    <Typography
                      variant="caption"
                      sx={{
                        color: step.isFinal ? 'success.dark' :
                               step.isLooping ? 'warning.dark' : 'text.secondary',
                        fontStyle: 'italic',
                        fontSize: '0.75rem',
                        lineHeight: 1.3,
                        display: 'block',
                        opacity: step.isLooping ? 0.7 : 1
                      }}
                    >
                      {step.detail}
                    </Typography>
                  </Box>
                </Box>
              </motion.div>
            ))}

            {/* Progress Indicator */}
            {!isComplete && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                <Box sx={{ mt: 2, mb: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={(displayedSteps.length / thinkingSteps.length) * 100}
                    sx={{
                      height: 4,
                      borderRadius: 2,
                      backgroundColor: 'grey.200',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 2,
                        background: 'linear-gradient(90deg, #1976d2 0%, #42a5f5 100%)'
                      }
                    }}
                  />
                  <Typography
                    variant="caption"
                    sx={{
                      color: 'text.secondary',
                      fontSize: '0.7rem',
                      mt: 0.5,
                      display: 'block'
                    }}
                  >
                    Step {displayedSteps.length} of {thinkingSteps.length}
                  </Typography>
                </Box>
              </motion.div>
            )}
          </Box>

          {/* Footer with timestamp */}
          <Typography
            variant="caption"
            sx={{
              color: 'text.disabled',
              fontSize: '0.7rem',
              mt: 1,
              display: 'block',
              textAlign: 'right'
            }}
          >
            {formatTimestamp(new Date())}
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
};

export default SimpleAIThinkingSteps;
