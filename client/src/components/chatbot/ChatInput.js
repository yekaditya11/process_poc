/**
 * ChatInput Component
 * Input field for sending messages to the chatbot
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Tooltip,
  Typography,
  Alert,
} from '@mui/material';
import {
  Send as SendIcon,
  AttachFile as AttachIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { chatAnimations } from '../../utils/animations';

const ChatInput = ({ onSendMessage, disabled, placeholder }) => {
  const [message, setMessage] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    // Focus input when component mounts
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };



  return (
    <Box
      sx={{
        background: 'white',
        position: 'relative', // Ensure stable positioning
        minHeight: '70px', // Fixed minimum height to prevent layout shifts
      }}
    >
      {/* Separator Line */}
      <Box
        sx={{
          height: '1px',
          background: 'linear-gradient(90deg, transparent 0%, #e2e8f0 50%, transparent 100%)',
          mx: 2,
        }}
      />



      {/* Input Section - Fixed at bottom */}
      <Box sx={{ p: 1.5 }}>
        <Box
          component="form"
          onSubmit={handleSubmit}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }}
        >
          {/* Input Box */}
          <TextField
            ref={inputRef}
            fullWidth
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={disabled}
            variant="outlined"
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                height: '36px',
                borderRadius: '18px',
                background: 'white',
                '& fieldset': {
                  borderColor: '#1976d2',
                  borderWidth: '1px',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#1976d2',
                  borderWidth: '1px',
                },
              },
              '& .MuiInputBase-input': {
                fontSize: '0.85rem',
                padding: '8px 14px',
                height: '20px',
              },
            }}
          />
          


          {/* Send Button */}
          <IconButton
            type="submit"
            disabled={disabled || !message.trim()}
            size="small"
            sx={{
              width: 32,
              height: 32,
              bgcolor: message.trim() ? '#1976d2' : '#f1f5f9',
              color: message.trim() ? 'white' : '#94a3b8',
              borderRadius: '50%',
              flexShrink: 0, // Prevent button from shrinking
              '&.Mui-disabled': {
                bgcolor: '#f1f5f9',
                color: '#cbd5e1',
              },
            }}
          >
            <SendIcon sx={{ fontSize: 16 }} />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};

export default ChatInput;
