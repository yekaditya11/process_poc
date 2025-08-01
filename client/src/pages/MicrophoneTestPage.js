/**
 * MicrophoneTestPage
 * A page to test microphone functionality and debug issues
 */

import React from 'react';
import { Box, Typography, Container } from '@mui/material';
import MicrophoneTest from '../components/chatbot/MicrophoneTest';
import ChatBot from '../components/chatbot/ChatBot';

const MicrophoneTestPage = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" sx={{ mb: 3, textAlign: 'center' }}>
        Microphone Test Page
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 4, textAlign: 'center' }}>
        Use this page to test microphone functionality and debug any issues with voice input in the chatbot.
      </Typography>

      <MicrophoneTest />
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Test Chatbot with Microphone
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          Open the chatbot below and try using the microphone button to test voice input functionality.
        </Typography>
      </Box>
      
      <ChatBot />
    </Container>
  );
};

export default MicrophoneTestPage; 