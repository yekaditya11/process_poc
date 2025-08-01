/**
 * Simple Streaming Test Component
 * A minimal streaming component to test if the basic concept works
 */

import React, { useState, useEffect } from 'react';
import { Box, Typography, LinearProgress } from '@mui/material';

const SimpleStreamingTest = ({ userMessage, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  const messages = [
    "🔍 Analyzing your request...",
    "📊 Processing safety data...",
    "🧠 Generating insights...",
    "✅ Preparing response..."
  ];

  const timings = [1000, 1500, 1200, 800];

  useEffect(() => {
    if (!userMessage) return;

    console.log('🧪 SimpleStreamingTest starting for:', userMessage);
    
    let stepIndex = 0;
    setCurrentStep(0);
    setIsComplete(false);

    const executeStep = () => {
      if (stepIndex >= messages.length) {
        setIsComplete(true);
        if (onComplete) {
          setTimeout(onComplete, 500);
        }
        return;
      }

      setCurrentStep(stepIndex);
      
      setTimeout(() => {
        stepIndex++;
        executeStep();
      }, timings[stepIndex] || 1000);
    };

    executeStep();
  }, [userMessage, onComplete]);

  if (!userMessage) return null;

  return (
    <Box sx={{ p: 2, border: '1px solid #ddd', borderRadius: 2, mb: 2 }}>
      <Typography variant="subtitle2" gutterBottom>
        Simple Streaming Test
      </Typography>
      
      <LinearProgress 
        variant="determinate" 
        value={(currentStep / messages.length) * 100} 
        sx={{ mb: 2 }}
      />

      {messages.map((message, index) => (
        <Box 
          key={index}
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1, 
            mb: 1,
            opacity: index <= currentStep ? 1 : 0.3,
            transition: 'opacity 0.3s ease'
          }}
        >
          <Typography variant="body2">
            {index < currentStep ? '✅' : index === currentStep ? '⏳' : '⭕'}
          </Typography>
          <Typography variant="body2">
            {message}
          </Typography>
        </Box>
      ))}

      {isComplete && (
        <Box sx={{ mt: 2, p: 1, backgroundColor: 'success.light', borderRadius: 1 }}>
          <Typography variant="body2" color="success.dark">
            ✅ Streaming complete!
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default SimpleStreamingTest;
