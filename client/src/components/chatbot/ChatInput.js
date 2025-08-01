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
  Mic as MicIcon,
  MicOff as MicOffIcon,
  AttachFile as AttachIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { chatAnimations } from '../../utils/animations';

const ChatInput = ({ onSendMessage, disabled, placeholder }) => {
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [micError, setMicError] = useState(null);
  const [micSupported, setMicSupported] = useState(false);
  const [micPermission, setMicPermission] = useState('unknown');
  const inputRef = useRef(null);

  useEffect(() => {
    // Focus input when component mounts
    if (inputRef.current) {
      inputRef.current.focus();
    }

    // Check for speech recognition support
    const checkSpeechRecognitionSupport = () => {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (SpeechRecognition) {
        setMicSupported(true);
        
        // Check if we're in a secure context
        if (!window.isSecureContext) {
          setMicError('Microphone access requires HTTPS. Please use HTTPS or localhost.');
          return;
        }

        // Initialize speech recognition
        const recognitionInstance = new SpeechRecognition();
        
        recognitionInstance.continuous = false;
        recognitionInstance.interimResults = false;
        recognitionInstance.lang = 'en-US';

        recognitionInstance.onstart = () => {
          setIsListening(true);
          setIsRecording(true);
          setMicError(null);
        };

        recognitionInstance.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          setMessage(transcript);
          setIsListening(false);
          setIsRecording(false);
        };

        recognitionInstance.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          setIsListening(false);
          setIsRecording(false);
          
          // Handle specific error types
          switch (event.error) {
            case 'not-allowed':
              setMicError('Microphone permission denied. Please allow microphone access in your browser settings.');
              setMicPermission('denied');
              break;
            case 'no-speech':
              setMicError('No speech detected. Please try speaking again.');
              break;
            case 'audio-capture':
              setMicError('Audio capture failed. Please check your microphone settings.');
              break;
            case 'network':
              setMicError('Network error. Please check your internet connection.');
              break;
            default:
              setMicError(`Speech recognition error: ${event.error}`);
          }
        };

        recognitionInstance.onend = () => {
          setIsListening(false);
          setIsRecording(false);
        };

        setRecognition(recognitionInstance);
      } else {
        setMicSupported(false);
        setMicError('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
      }
    };

    checkSpeechRecognitionSupport();
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

  const handleVoiceInput = async () => {
    if (!micSupported) {
      alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (!window.isSecureContext) {
      alert('Microphone access requires HTTPS. Please use HTTPS or localhost.');
      return;
    }

    if (disabled) return;

    if (isListening) {
      // Stop recording
      recognition.stop();
    } else {
      // Check microphone permission first
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop()); // Stop the stream immediately
        setMicPermission('granted');
        
        // Start recording
        try {
          recognition.start();
        } catch (error) {
          console.error('Error starting speech recognition:', error);
          setIsRecording(false);
          setIsListening(false);
          setMicError('Failed to start speech recognition. Please try again.');
        }
      } catch (permissionError) {
        console.error('Microphone permission error:', permissionError);
        setMicPermission('denied');
        setMicError('Microphone permission denied. Please allow microphone access in your browser settings.');
      }
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

      {/* Error Alert */}
      {micError && (
        <Box sx={{ mx: 1.5, mt: 0.5 }}>
          <Alert 
            severity="warning" 
            sx={{ 
              fontSize: '0.75rem',
              py: 0.5,
              '& .MuiAlert-message': {
                fontSize: '0.75rem',
              }
            }}
            onClose={() => setMicError(null)}
          >
            {micError}
          </Alert>
        </Box>
      )}

      {/* Recording Indicator - Fixed height to prevent layout shift */}
      <Box
        sx={{
          height: isRecording ? '28px' : '0px', // Fixed height transition
          overflow: 'hidden',
          transition: 'height 0.2s ease',
        }}
      >
        {isRecording && (
          <Box
            sx={{
              mx: 1.5,
              mt: 0.5,
              mb: 0.5,
              p: 0.5,
              bgcolor: '#fee2e2',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 0.5,
              height: '18px',
            }}
          >
            <Box
              sx={{
                width: 4,
                height: 4,
                borderRadius: '50%',
                bgcolor: '#dc2626',
                animation: 'pulse 1s infinite',
                '@keyframes pulse': {
                  '0%': { opacity: 1 },
                  '50%': { opacity: 0.5 },
                  '100%': { opacity: 1 },
                },
              }}
            />
            <Typography
              variant="caption"
              sx={{
                color: '#dc2626',
                fontSize: '0.7rem',
              }}
            >
              {isListening ? 'Listening...' : 'Recording...'}
            </Typography>
          </Box>
        )}
      </Box>

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
          
          {/* Audio Button */}
          <Tooltip 
            title={
              !micSupported ? 'Speech recognition not supported' :
              !window.isSecureContext ? 'HTTPS required for microphone' :
              micPermission === 'denied' ? 'Microphone permission denied' :
              isRecording ? 'Stop recording' : 'Start voice input'
            }
          >
            <span>
              <IconButton
                onClick={handleVoiceInput}
                disabled={disabled || !micSupported || !window.isSecureContext || micPermission === 'denied'}
                size="small"
                sx={{
                  width: 32,
                  height: 32,
                  background: isRecording
                    ? 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)'
                    : micPermission === 'denied' || !micSupported
                    ? '#e5e7eb'
                    : 'linear-gradient(135deg, #092f57 0%, #1e40af 100%)',
                  color: isRecording ? 'white' : 
                         micPermission === 'denied' || !micSupported ? '#9ca3af' : 'white',
                  borderRadius: '50%',
                  flexShrink: 0, // Prevent button from shrinking
                  '&.Mui-disabled': {
                    background: '#e5e7eb',
                    color: '#9ca3af',
                  },
                }}
              >
                {micPermission === 'denied' || !micSupported ? 
                  <MicOffIcon sx={{ fontSize: 16 }} /> : 
                  <MicIcon sx={{ fontSize: 16 }} />
                }
              </IconButton>
            </span>
          </Tooltip>

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
