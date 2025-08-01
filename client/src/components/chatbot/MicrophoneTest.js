/**
 * MicrophoneTest Component
 * Debug component to test microphone functionality
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Alert,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Mic as MicIcon,
  MicOff as MicOffIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

const MicrophoneTest = () => {
  const [testResults, setTestResults] = useState([]);
  const [isTesting, setIsTesting] = useState(false);

  const runMicrophoneTests = async () => {
    setIsTesting(true);
    const results = [];

    // Test 1: Check if we're in a secure context
    try {
      const isSecure = window.isSecureContext;
      results.push({
        test: 'Secure Context',
        status: isSecure ? 'pass' : 'fail',
        message: isSecure ? 'Running on HTTPS or localhost' : 'Not running on HTTPS - microphone will not work',
        details: `isSecureContext: ${isSecure}`
      });
    } catch (error) {
      results.push({
        test: 'Secure Context',
        status: 'error',
        message: 'Could not check secure context',
        details: error.message
      });
    }

    // Test 2: Check for Speech Recognition API
    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const hasSpeechRecognition = !!SpeechRecognition;
      results.push({
        test: 'Speech Recognition API',
        status: hasSpeechRecognition ? 'pass' : 'fail',
        message: hasSpeechRecognition ? 'Speech recognition API available' : 'Speech recognition not supported in this browser',
        details: `SpeechRecognition: ${!!window.SpeechRecognition}, webkitSpeechRecognition: ${!!window.webkitSpeechRecognition}`
      });
    } catch (error) {
      results.push({
        test: 'Speech Recognition API',
        status: 'error',
        message: 'Could not check speech recognition API',
        details: error.message
      });
    }

    // Test 3: Check for MediaDevices API
    try {
      const hasMediaDevices = !!navigator.mediaDevices;
      results.push({
        test: 'MediaDevices API',
        status: hasMediaDevices ? 'pass' : 'fail',
        message: hasMediaDevices ? 'MediaDevices API available' : 'MediaDevices API not supported',
        details: `navigator.mediaDevices: ${hasMediaDevices}`
      });
    } catch (error) {
      results.push({
        test: 'MediaDevices API',
        status: 'error',
        message: 'Could not check MediaDevices API',
        details: error.message
      });
    }

    // Test 4: Check microphone permission
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop());
        results.push({
          test: 'Microphone Permission',
          status: 'pass',
          message: 'Microphone permission granted',
          details: 'Successfully accessed microphone'
        });
      } else {
        results.push({
          test: 'Microphone Permission',
          status: 'fail',
          message: 'MediaDevices API not available',
          details: 'Cannot test microphone permission'
        });
      }
    } catch (error) {
      results.push({
        test: 'Microphone Permission',
        status: 'fail',
        message: 'Microphone permission denied or not available',
        details: error.message
      });
    }

    // Test 5: Check browser info
    try {
      const userAgent = navigator.userAgent;
      const isChrome = userAgent.includes('Chrome');
      const isSafari = userAgent.includes('Safari') && !userAgent.includes('Chrome');
      const isEdge = userAgent.includes('Edg');
      const isFirefox = userAgent.includes('Firefox');
      
      results.push({
        test: 'Browser Compatibility',
        status: (isChrome || isSafari || isEdge) ? 'pass' : 'warning',
        message: (isChrome || isSafari || isEdge) ? 'Browser supports speech recognition' : 'Browser may not support speech recognition',
        details: `Browser: ${userAgent}`
      });
    } catch (error) {
      results.push({
        test: 'Browser Compatibility',
        status: 'error',
        message: 'Could not check browser compatibility',
        details: error.message
      });
    }

    setTestResults(results);
    setIsTesting(false);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pass':
        return <CheckIcon sx={{ color: 'green', fontSize: 16 }} />;
      case 'fail':
        return <ErrorIcon sx={{ color: 'red', fontSize: 16 }} />;
      case 'warning':
        return <InfoIcon sx={{ color: 'orange', fontSize: 16 }} />;
      default:
        return <InfoIcon sx={{ color: 'gray', fontSize: 16 }} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pass':
        return 'success';
      case 'fail':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'info';
    }
  };

  return (
    <Paper sx={{ p: 2, m: 2, maxWidth: 600 }}>
      <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        <MicIcon />
        Microphone Test
      </Typography>
      
      <Button
        variant="contained"
        onClick={runMicrophoneTests}
        disabled={isTesting}
        sx={{ mb: 2 }}
      >
        {isTesting ? 'Running Tests...' : 'Run Microphone Tests'}
      </Button>

      {testResults.length > 0 && (
        <List>
          {testResults.map((result, index) => (
            <React.Fragment key={index}>
              <ListItem>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, width: '100%' }}>
                  {getStatusIcon(result.status)}
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      {result.test}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {result.message}
                    </Typography>
                    <Typography variant="caption" sx={{ fontFamily: 'monospace', color: 'gray' }}>
                      {result.details}
                    </Typography>
                  </Box>
                </Box>
              </ListItem>
              {index < testResults.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      )}

      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="body2">
          <strong>How to fix microphone issues:</strong>
        </Typography>
        <Typography variant="body2" component="div" sx={{ mt: 1 }}>
          <ul>
            <li>Make sure you're using HTTPS or localhost</li>
            <li>Allow microphone permissions in your browser</li>
            <li>Use Chrome, Edge, or Safari for best compatibility</li>
            <li>Check that your microphone is working in other applications</li>
          </ul>
        </Typography>
      </Alert>
    </Paper>
  );
};

export default MicrophoneTest; 