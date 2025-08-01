/**
 * Enhanced Chat Loading Indicator with Context-Aware Streaming
 * Beautiful loading animations for the SafetyConnect chatbot
 */

import React, { useState, useEffect } from 'react';
import { Box, Typography, LinearProgress } from '@mui/material';
import { SmartToy as BotIcon } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useDashboardContext } from '../../contexts/DashboardContext';

const ChatLoadingIndicator = ({
  message,
  userMessage = null,
  enableContextualStreaming = true
}) => {
  const { context } = useDashboardContext();
  const [currentStep, setCurrentStep] = useState(0);
  const [streamingMessages, setStreamingMessages] = useState([]);

  // Context-aware streaming messages
  useEffect(() => {
    if (!enableContextualStreaming || !userMessage) {
      setStreamingMessages([message || "🤖 Processing your safety query..."]);
      return;
    }

    // Generate context-aware messages based on current module and user question
    const generateContextualMessages = () => {
      const module = context?.activeModule || 'global-dashboard';
      const question = userMessage.toLowerCase();

      let messages = ["🔍 Analyzing your request..."];

      // Add module-specific context
      if (module === 'incident-investigation') {
        messages.push("📋 Accessing incident database...");
      } else if (module === 'driver-safety') {
        messages.push("🚗 Reviewing driver safety records...");
      } else if (module === 'risk-assessment') {
        messages.push("⚠️ Evaluating risk factors...");
      } else if (module === 'action-tracking') {
        messages.push("✅ Checking action items...");
      } else if (module === 'observation-tracking') {
        messages.push("👁️ Analyzing observation data...");
      } else if (module === 'equipment-inspection') {
        messages.push("🔧 Reviewing equipment status...");
      } else if (module === 'training-management') {
        messages.push("📚 Checking training records...");
      } else {
        messages.push("📊 Processing safety data...");
      }

      // Add question-specific context
      if (question.includes('trend') || question.includes('pattern')) {
        messages.push("📈 Identifying trends and patterns...");
      } else if (question.includes('status') || question.includes('summary')) {
        messages.push("📋 Compiling status summary...");
      } else if (question.includes('compliance') || question.includes('regulation')) {
        messages.push("📜 Checking compliance requirements...");
      } else if (question.includes('recent') || question.includes('latest')) {
        messages.push("🕒 Fetching recent data...");
      }

      messages.push("🧠 Generating insights...");
      messages.push("✅ Preparing response...");

      return messages;
    };

    const messages = generateContextualMessages();
    setStreamingMessages(messages);
    setCurrentStep(0);

    // Animate through messages
    let stepIndex = 0;
    const interval = setInterval(() => {
      if (stepIndex < messages.length - 1) {
        stepIndex++;
        setCurrentStep(stepIndex);
      } else {
        clearInterval(interval);
      }
    }, 800);

    return () => clearInterval(interval);
  }, [userMessage, context, enableContextualStreaming, message]);

  const currentMessage = streamingMessages[currentStep] || streamingMessages[0] || "🤖 Processing your safety query...";
  const progress = streamingMessages.length > 1 ? ((currentStep + 1) / streamingMessages.length) * 100 : 0;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
        py: 1,
        pl: 1,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        {/* Animated Chatbot Symbol */}
        <motion.div
          animate={{
            rotate: [0, 10, -10, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <BotIcon
            sx={{
              fontSize: 20,
              color: '#1976d2',
              opacity: 0.8,
            }}
          />
        </motion.div>

        <Typography
          variant="body2"
          sx={{
            color: '#64748b',
            fontSize: '0.9rem',
            fontStyle: 'italic',
          }}
        >
          {currentMessage}
        </Typography>
      </Box>

      {/* Progress bar for contextual streaming */}
      {enableContextualStreaming && userMessage && streamingMessages.length > 1 && (
        <Box sx={{ width: '100%', ml: 3 }}>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              height: 2,
              borderRadius: 1,
              backgroundColor: '#e3f2fd',
              '& .MuiLinearProgress-bar': {
                backgroundColor: '#1976d2',
              }
            }}
          />
        </Box>
      )}
    </Box>
  );
};

export default ChatLoadingIndicator;
