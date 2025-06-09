/**
 * Enhanced Chat Loading Indicator
 * Beautiful loading animations for the SafetyConnect chatbot
 */

import React from 'react';
import { Box, Typography } from '@mui/material';
import { SmartToy as BotIcon } from '@mui/icons-material';
import { motion } from 'framer-motion';

const ChatLoadingIndicator = ({ message = "AI is analyzing..." }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-start',
        gap: 1,
        py: 1,
        pl: 1, // Add some left padding to align with chat messages
      }}
    >
      {/* Animated Chatbot Symbol on the left */}
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
        {message}
      </Typography>
    </Box>
  );
};

export default ChatLoadingIndicator;
