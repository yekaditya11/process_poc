/**
 * Modern ChatBot Component
 * KPI-based conversational AI with graph generation capabilities
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import {
  Box,
  Paper,
  IconButton,
  Typography,
  Tooltip,
  Badge,
  Chip,
  Collapse,
  Avatar,
} from '@mui/material';
import {
  Close as CloseIcon,
  Minimize as MinimizeIcon,
  Refresh as RefreshIcon,
  SmartToy as BotIcon,
  Fullscreen as FullscreenIcon,
  FullscreenExit as FullscreenExitIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  QuestionAnswer as SuggestionsIcon,
  VolumeUp as SpeakerIcon,
  VolumeOff as MuteIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { chatAnimations, staggerContainer, staggerItem } from '../../utils/animations';

import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import ChatLoadingIndicator from './ChatLoadingIndicator';
import ApiService from '../../services/api';
import '../../styles/chatbot.css';

const ChatBot = ({ moduleContext = null }) => {
  console.log('🤖 ChatBot component initialized with moduleContext:', moduleContext);

  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [hasNewMessage, setHasNewMessage] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speechEnabled, setSpeechEnabled] = useState(false);
  const [suggestionsOpen, setSuggestionsOpen] = useState(false);
  const [persistentSuggestions] = useState([
    "Show recent incidents",
    "Driver safety status",
    "Action tracking summary",
    "Observation trends",
    "Equipment inspection status",
    "Training compliance overview",
    "Risk assessment summary",
    "Safety performance metrics"
  ]);

  // Add a simple test to ensure component is working
  useEffect(() => {
    console.log('🤖 ChatBot component mounted successfully');
    console.log('🤖 Current state - isOpen:', isOpen);

    // Test if we can access the DOM
    if (typeof document !== 'undefined') {
      console.log('🤖 Document is available, portal should work');
    }

    return () => {
      console.log('🤖 ChatBot component unmounting');
    };
  }, []);
  
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    // Only scroll if chat is open and not minimized, and container exists
    if (isOpen && !isMinimized && chatContainerRef.current) {
      // Add a small delay to ensure the container is fully rendered
      setTimeout(() => {
        if (chatContainerRef.current) {
          // Scroll within the chat container only, not the entire page
          chatContainerRef.current.scrollTo({
            top: chatContainerRef.current.scrollHeight,
            behavior: 'smooth'
          });
        }
      }, 100);
    }
  }, [isOpen, isMinimized]);

  useEffect(() => {
    // Only scroll when messages change and chat is open
    if (isOpen && !isMinimized && messages.length > 0) {
      // Use requestAnimationFrame for smoother scrolling
      requestAnimationFrame(() => {
        scrollToBottom();
      });
    }
  }, [messages, scrollToBottom, isOpen, isMinimized]);

  // Ensure chat starts from top when first opened
  useEffect(() => {
    if (isOpen && !isMinimized && chatContainerRef.current && messages.length === 0) {
      chatContainerRef.current.scrollTop = 0;
    }
  }, [isOpen, isMinimized, messages.length]);

  // Initialize conversation when chatbot opens
  useEffect(() => {
    if (isOpen && !sessionId) {
      console.log('🤖 Initializing conversation...');
      initializeConversation();
    }
  }, [isOpen, sessionId]);

  const initializeConversation = async () => {
    try {
      setIsLoading(true);
      console.log('Initializing conversation...');
      const response = await ApiService.startConversation();
      console.log('Start conversation response:', response);

      // Note: axios interceptor returns response.data, so response is already the data object
      if (response && response.success) {
        setSessionId(response.session_id);
        console.log('Session ID set:', response.session_id);

        // Add welcome message
        const welcomeMessage = {
          id: Date.now(),
          role: 'assistant',
          content: response.message || "Hello! I'm your SafetyConnect AI assistant.",
          timestamp: new Date(),
          data_context: response.data_context,
          chart_data: response.chart_data
        };

        setMessages([welcomeMessage]);
      } else {
        console.error('Invalid start conversation response:', response);
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Error initializing conversation:', error);
      // Add fallback welcome message
      const fallbackMessage = {
        id: Date.now(),
        role: 'assistant',
        content: "Hello! I'm your SafetyConnect AI assistant. Ask me about your safety KPIs, incidents, or any other safety-related questions!",
        timestamp: new Date()
      };
      setMessages([fallbackMessage]);
      setSessionId('fallback-session-' + Date.now());
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (messageText) => {
    if (!messageText.trim() || isLoading) return;

    // Add user message immediately
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setIsTyping(true);

    try {
      console.log('Sending chat message:', messageText, 'Session ID:', sessionId, 'Module Context:', moduleContext);

      // Always use general chat endpoint - the AI backend is smart enough to detect
      // module intent from question content and handle ALL module questions
      // This allows the chatbot to answer questions about any module regardless of current page
      const response = await ApiService.sendChatMessage(messageText, sessionId);

      console.log('Chat response received:', response);

      // Note: axios interceptor returns response.data, so response is already the data object
      if (response && response.success) {
        // Add AI response
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: response.message || 'No response message',
          timestamp: new Date(),
          data_context: response.data_context,
          chart_data: response.chart_data,
          suggested_actions: response.suggested_actions || [] // Include follow-up questions
        };

        setMessages(prev => [...prev, aiMessage]);

        // Speak the AI response if speech is enabled
        if (speechEnabled && response.message) {
          setTimeout(() => speakText(response.message), 500);
        }

        // Show notification if chat is closed
        if (!isOpen) {
          setHasNewMessage(true);
        }
      } else {
        console.error('Invalid response structure:', response);
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment.",
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleToggleChat = () => {
    console.log('🤖 Chat toggle clicked, current isOpen:', isOpen);

    const newIsOpen = !isOpen;

    // Simple toggle without scroll interference
    setIsOpen(newIsOpen);
    setIsMinimized(false);
    setIsFullscreen(false);

    if (hasNewMessage) {
      setHasNewMessage(false);
    }

    // Dispatch custom event to notify charts about layout change
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('chatbot-toggle'));
    }, 50);

    console.log('🤖 Chat state will be:', newIsOpen);
  };

  const handleMinimize = () => {
    setIsMinimized(!isMinimized);
    if (isMinimized) {
      setIsFullscreen(false);
    }

    // Dispatch custom event to notify charts about layout change
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('chatbot-toggle'));
    }, 50);
  };

  const handleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
    if (!isFullscreen) {
      setIsMinimized(false);
    }

    // Dispatch custom event to notify charts about layout change
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('chatbot-toggle'));
    }, 50);
  };

  const handleClearChat = async () => {
    try {
      if (sessionId) {
        await ApiService.clearConversation(sessionId);
      }
      setMessages([]);
      setSessionId(null);
      // Reinitialize conversation
      await initializeConversation();
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  const handleSuggestedAction = (action) => {
    handleSendMessage(action);
  };

  const toggleSuggestions = () => {
    setSuggestionsOpen(!suggestionsOpen);
  };

  // Text-to-Speech functionality
  const speakText = (text) => {
    if (!speechEnabled || !('speechSynthesis' in window)) return;

    // Stop any current speech
    window.speechSynthesis.cancel();

    // Clean text for speech (remove markdown, emojis, etc.)
    const cleanText = text
      .replace(/[👋🤖📊⚠️✅❌]/g, '') // Remove emojis
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markdown
      .replace(/\*(.*?)\*/g, '$1') // Remove italic markdown
      .replace(/`(.*?)`/g, '$1') // Remove code markdown
      .trim();

    if (cleanText.length === 0) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 0.8;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  const toggleSpeech = () => {
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
    setSpeechEnabled(!speechEnabled);
  };



  console.log('🤖 ChatBot render - isOpen:', isOpen, 'isMinimized:', isMinimized, 'isFullscreen:', isFullscreen);

  // Check if document.body is available for portal
  if (typeof document === 'undefined' || !document.body) {
    console.log('🤖 Document.body not available, rendering fallback');
    return (
      <div style={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        zIndex: 9999,
        background: 'red',
        color: 'white',
        padding: '10px',
        borderRadius: '5px'
      }}>
        Portal Error - Check Console
      </div>
    );
  }

  // Render chatbot using React Portal to ensure it's completely isolated from parent containers
  try {
    return createPortal(
    <>
      {/* Enhanced Chat Window with Beautiful Animations */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            {...chatAnimations.chatWindow}
            style={{
              position: 'fixed',
              bottom: isFullscreen ? 0 : '100px',
              right: isFullscreen ? 0 : '24px',
              left: isFullscreen ? 0 : 'auto',
              top: isFullscreen ? 0 : 'auto',
              width: isFullscreen ? '100vw' : isMinimized ? '400px' : '500px',
              height: isFullscreen ? '100vh' : isMinimized ? '60px' : '650px',
              zIndex: 9999,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
          >
            <Paper
              elevation={isFullscreen ? 0 : 24}
              sx={{
                width: '100%',
                height: '100%',
                borderRadius: isFullscreen ? 0 : '24px',
                background: 'linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.98) 100%)',
                backdropFilter: 'blur(20px)',
                border: isFullscreen ? 'none' : '1px solid rgba(255, 255, 255, 0.3)',
                boxShadow: isFullscreen
                  ? 'none'
                  : '0 25px 80px rgba(0, 0, 0, 0.15), 0 10px 40px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.6)',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 50%, rgba(255,255,255,0.05) 100%)',
                  pointerEvents: 'none',
                  borderRadius: 'inherit',
                }
              }}
            >
              {/* Enhanced Header with Animations */}
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
              >
                <Box
                  sx={{
                    p: 2,
                    background: 'linear-gradient(135deg, #092f57 0%, #1e40af 100%)',
                    color: 'white',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    borderRadius: isFullscreen ? 0 : '24px 24px 0 0',
                    position: 'relative',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      background: 'linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0))',
                      pointerEvents: 'none',
                      borderRadius: 'inherit',
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, zIndex: 1 }}>
                    <motion.div
                      animate={{
                        rotate: isLoading ? 360 : 0,
                        scale: isLoading ? [1, 1.1, 1] : 1
                      }}
                      transition={{
                        duration: isLoading ? 2 : 0.3,
                        repeat: isLoading ? Infinity : 0,
                        ease: isLoading ? "linear" : "easeInOut"
                      }}
                    >
                      <Avatar
                        sx={{
                          width: 32,
                          height: 32,
                          bgcolor: 'rgba(255,255,255,0.2)',
                          backdropFilter: 'blur(10px)',
                          border: '1px solid rgba(255,255,255,0.3)',
                        }}
                      >
                        <BotIcon sx={{ fontSize: 18, color: 'white' }} />
                      </Avatar>
                    </motion.div>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem', lineHeight: 1.2 }}>
                        SafetyConnect AI
                      </Typography>
                      <Typography variant="caption" sx={{ opacity: 0.8, fontSize: '0.75rem' }}>
                        {isLoading ? 'Thinking...' : ''}
                      </Typography>
                    </Box>
                  </Box>

                  <Box sx={{ display: 'flex', gap: 0.5, zIndex: 1 }}>
                    {/* Speech Toggle Button */}
                    <Tooltip title={speechEnabled ? "Disable speech" : "Enable speech"}>
                      <IconButton
                        onClick={toggleSpeech}
                        size="small"
                        sx={{
                          color: 'white',
                          bgcolor: speechEnabled ? 'rgba(76, 175, 80, 0.2)' : 'rgba(255,255,255,0.1)',
                          border: speechEnabled ? '1px solid rgba(76, 175, 80, 0.3)' : 'none',
                          '&:hover': {
                            bgcolor: speechEnabled ? 'rgba(76, 175, 80, 0.3)' : 'rgba(255,255,255,0.2)'
                          },
                          ...(isSpeaking && {
                            animation: 'pulse-speak 1s infinite',
                            '@keyframes pulse-speak': {
                              '0%': { opacity: 1 },
                              '50%': { opacity: 0.7 },
                              '100%': { opacity: 1 },
                            },
                          }),
                        }}
                      >
                        {speechEnabled ? <SpeakerIcon fontSize="small" /> : <MuteIcon fontSize="small" />}
                      </IconButton>
                    </Tooltip>

                    {/* Minimize Button */}
                    <Tooltip title={isMinimized ? "Expand" : "Minimize"}>
                      <IconButton
                        onClick={handleMinimize}
                        size="small"
                        sx={{
                          color: 'white',
                          bgcolor: 'rgba(255,255,255,0.1)',
                          '&:hover': { bgcolor: 'rgba(255,255,255,0.2)' },
                        }}
                      >
                        {isMinimized ? <ExpandMoreIcon fontSize="small" /> : <MinimizeIcon fontSize="small" />}
                      </IconButton>
                    </Tooltip>

                    {/* Fullscreen Button */}
                    <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
                      <IconButton
                        onClick={handleFullscreen}
                        size="small"
                        sx={{
                          color: 'white',
                          bgcolor: 'rgba(255,255,255,0.1)',
                          '&:hover': { bgcolor: 'rgba(255,255,255,0.2)' },
                        }}
                      >
                        {isFullscreen ? <FullscreenExitIcon fontSize="small" /> : <FullscreenIcon fontSize="small" />}
                      </IconButton>
                    </Tooltip>

                    {/* Clear Chat Button */}
                    <Tooltip title="Clear Chat">
                      <IconButton
                        onClick={handleClearChat}
                        size="small"
                        sx={{
                          color: 'white',
                          bgcolor: 'rgba(255,255,255,0.1)',
                          '&:hover': { bgcolor: 'rgba(255,255,255,0.2)' },
                        }}
                      >
                        <RefreshIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>

                    {/* Close Button */}
                    <Tooltip title="Close Chat">
                      <IconButton
                        onClick={handleToggleChat}
                        size="small"
                        sx={{
                          color: 'white',
                          bgcolor: 'rgba(255,255,255,0.1)',
                          '&:hover': { bgcolor: 'rgba(255,255,255,0.2)' },
                        }}
                      >
                        <CloseIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </motion.div>

              {/* Messages Area - Adjusted Height for Quick Questions */}
              <Collapse in={!isMinimized}>
                <Box
                  ref={chatContainerRef}
                  sx={{
                    // Adjust height based on whether suggestions are open
                    height: isFullscreen
                      ? 'calc(100vh - 160px)'
                      : suggestionsOpen
                        ? '380px'  // Reduced height when suggestions are open
                        : '480px', // Full height when suggestions are closed
                    overflow: 'auto',
                    p: 1.5, // Reduced padding
                    pt: 1,
                    pb: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 0.5, // Reduced gap between messages
                    background: 'linear-gradient(to bottom, rgba(248, 250, 252, 0.5) 0%, rgba(255, 255, 255, 0.8) 100%)',
                    // Ensure scrolling starts from top
                    scrollBehavior: 'smooth',
                    transition: 'height 0.3s ease', // Smooth height transition
                    '&::-webkit-scrollbar': {
                      width: '6px',
                    },
                    '&::-webkit-scrollbar-track': {
                      background: 'rgba(0,0,0,0.05)',
                      borderRadius: '3px',
                    },
                    '&::-webkit-scrollbar-thumb': {
                      background: 'rgba(0,0,0,0.2)',
                      borderRadius: '3px',
                      '&:hover': {
                        background: 'rgba(0,0,0,0.3)',
                      },
                    },
                  }}
                >
                  {/* Welcome Message */}
                  {messages.length === 0 && !isLoading && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
                    >
                      <Paper
                        elevation={0}
                        sx={{
                          p: 1.5,
                          borderRadius: '16px',
                          background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
                          border: '1px solid rgba(59, 130, 246, 0.2)',
                          textAlign: 'center',
                        }}
                      >
                        <motion.div
                          animate={{
                            scale: [1, 1.05, 1],
                            rotate: [0, 5, -5, 0]
                          }}
                          transition={{
                            duration: 3,
                            repeat: Infinity,
                            ease: "easeInOut"
                          }}
                        >
                          <BotIcon sx={{ fontSize: 32, color: '#3b82f6', mb: 0.5 }} />
                        </motion.div>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1e40af', mb: 0.5 }}>
                          Welcome to SafetyConnect AI! 👋
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#64748b', mb: 1 }}>
                          I can help you with ALL safety modules - incidents, risk assessments, actions, driver safety, observations, equipment, and training.
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#94a3b8' }}>
                          Ask me about any safety topic regardless of which page you're on!
                        </Typography>
                      </Paper>
                    </motion.div>
                  )}

                  {/* Messages with Staggered Animations */}
                  <motion.div
                    variants={staggerContainer}
                    initial="initial"
                    animate="animate"
                  >
                    {messages.map((message, index) => (
                      <motion.div
                        key={message.id || index}
                        variants={staggerItem}
                        transition={{ delay: index * 0.1 }}
                      >
                        <ChatMessage
                          message={message}
                          onSuggestedAction={handleSuggestedAction}
                          isSpeaking={isSpeaking}
                          isFullscreen={isFullscreen}
                        />
                      </motion.div>
                    ))}
                  </motion.div>

                  {/* Enhanced Loading Indicator */}
                  {isLoading && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                    >
                      <ChatLoadingIndicator />
                    </motion.div>
                  )}

                  {/* Auto-scroll anchor */}
                  <div ref={messagesEndRef} />
                </Box>
              </Collapse>

              {/* Chat Input Section - Always at Bottom */}
              <Collapse in={!isMinimized}>
                <Box>
                  {/* Quick Questions - Above Input */}
                  <Box
                    sx={{
                      background: 'linear-gradient(135deg, #f8fafc 0%, #ffffff 100%)',
                      borderTop: '1px solid rgba(0,0,0,0.06)',
                    }}
                  >
                    {/* Quick Questions Header with Toggle */}
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        px: 2,
                        py: 0.5,
                        height: '32px',
                      }}
                    >
                      <Typography
                        variant="caption"
                        sx={{
                          color: '#64748b',
                          fontWeight: 600,
                          fontSize: '0.7rem',
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5,
                        }}
                      >
                        <SuggestionsIcon sx={{ fontSize: 12 }} />
                        Quick Questions
                      </Typography>
                      <Tooltip title={suggestionsOpen ? "Hide quick questions" : "Show quick questions"}>
                        <IconButton
                          size="small"
                          onClick={toggleSuggestions}
                          sx={{
                            color: '#64748b',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              color: '#1976d2',
                              bgcolor: 'rgba(25, 118, 210, 0.1)',
                            }
                          }}
                        >
                          {suggestionsOpen ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
                        </IconButton>
                      </Tooltip>
                    </Box>

                    {/* Quick Questions Content - Limited Height */}
                    {suggestionsOpen && (
                      <Box
                        sx={{
                          px: 2,
                          pb: 0.5,
                          borderBottom: '1px solid rgba(0,0,0,0.06)',
                          maxHeight: '100px', // Limit maximum height
                          overflow: 'auto', // Allow scrolling if needed
                        }}
                      >
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.75 }}>
                          {persistentSuggestions.slice(0, 8).map((suggestion, index) => (
                            <Chip
                              key={index}
                              label={suggestion}
                              size="small"
                              clickable
                              onClick={() => handleSendMessage(suggestion)}
                              sx={{
                                fontSize: '0.7rem',
                                height: 24,
                                bgcolor: '#e0f2fe',
                                color: '#0369a1',
                                border: '1px solid #bae6fd',
                                borderRadius: '16px',
                                transition: 'all 0.2s ease',
                                '&:hover': {
                                  bgcolor: '#bae6fd',
                                  borderColor: '#7dd3fc',
                                  transform: 'translateY(-1px)',
                                  boxShadow: '0 2px 8px rgba(3, 105, 161, 0.2)',
                                },
                              }}
                            />
                          ))}
                        </Box>
                      </Box>
                    )}
                  </Box>

                  {/* Chat Input - Fixed at Bottom */}
                  <ChatInput
                    onSendMessage={handleSendMessage}
                    disabled={isLoading}
                  />
                </Box>
              </Collapse>
            </Paper>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Enhanced Chat Toggle Button with Advanced Animations */}
      <AnimatePresence>
        {!isFullscreen && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
            style={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              zIndex: 9999,
            }}
          >
            <Tooltip
              title="Chat with SafetyConnect AI"
              placement="left"
              arrow
              sx={{
                '& .MuiTooltip-tooltip': {
                  bgcolor: 'rgba(0, 0, 0, 0.8)',
                  backdropFilter: 'blur(10px)',
                  fontSize: '0.75rem',
                  fontWeight: 500,
                },
                '& .MuiTooltip-arrow': {
                  color: 'rgba(0, 0, 0, 0.8)',
                },
              }}
            >
              <Badge
                badgeContent={hasNewMessage ? "!" : 0}
                color="error"
                sx={{
                  '& .MuiBadge-badge': {
                    fontSize: '0.75rem',
                    minWidth: '20px',
                    height: '20px',
                    fontWeight: 600,
                    animation: hasNewMessage ? 'pulse-glow 2s infinite' : 'none',
                    background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                    boxShadow: '0 2px 8px rgba(239, 68, 68, 0.4)',
                    '@keyframes pulse-glow': {
                      '0%': {
                        opacity: 1,
                        transform: 'scale(1)',
                        boxShadow: '0 2px 8px rgba(239, 68, 68, 0.4)'
                      },
                      '50%': {
                        opacity: 0.8,
                        transform: 'scale(1.1)',
                        boxShadow: '0 4px 16px rgba(239, 68, 68, 0.6)'
                      },
                      '100%': {
                        opacity: 1,
                        transform: 'scale(1)',
                        boxShadow: '0 2px 8px rgba(239, 68, 68, 0.4)'
                      },
                    },
                  },
                }}
              >
                <motion.div
                  whileHover={{
                    scale: 1.1,
                    rotate: [0, -5, 5, 0],
                    transition: { duration: 0.3, ease: [0.4, 0, 0.2, 1] }
                  }}
                  whileTap={{
                    scale: 0.95,
                    transition: { duration: 0.1 }
                  }}
                  animate={{
                    y: [0, -3, 0],
                    transition: {
                      duration: 4,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }
                  }}
                >
                  <Box
                    onClick={(e) => {
                      console.log('🤖 Toggle button clicked!', e);
                      handleToggleChat();
                    }}
                    sx={{
                      width: 72,
                      height: 72,
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #092f57 0%, #1e40af 50%, #3b82f6 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      boxShadow: '0 10px 40px rgba(9, 47, 87, 0.4), 0 4px 16px rgba(9, 47, 87, 0.2)',
                      border: '3px solid rgba(255, 255, 255, 0.3)',
                      position: 'relative',
                      overflow: 'hidden',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        boxShadow: '0 16px 60px rgba(9, 47, 87, 0.5), 0 8px 24px rgba(9, 47, 87, 0.3)',
                        background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%)',
                        borderColor: 'rgba(255, 255, 255, 0.4)',
                      },
                      '&:active': {
                        boxShadow: '0 8px 32px rgba(9, 47, 87, 0.4)',
                        transform: 'translateY(1px)',
                      },
                      '&::before': {
                        content: '""',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        borderRadius: '50%',
                        background: 'linear-gradient(45deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 50%, rgba(255,255,255,0.1) 100%)',
                        pointerEvents: 'none',
                      },
                      '&::after': {
                        content: '""',
                        position: 'absolute',
                        top: '10%',
                        left: '10%',
                        right: '60%',
                        bottom: '60%',
                        borderRadius: '50%',
                        background: 'rgba(255, 255, 255, 0.3)',
                        filter: 'blur(4px)',
                        pointerEvents: 'none',
                      }
                    }}
                  >
                    <motion.div
                      animate={isLoading ? {
                        rotate: 360,
                        scale: [1, 1.15, 1]
                      } : {
                        rotate: 0,
                        scale: 1
                      }}
                      transition={{
                        duration: isLoading ? 1.5 : 0.3,
                        repeat: isLoading ? Infinity : 0,
                        ease: isLoading ? "linear" : "easeInOut"
                      }}
                      style={{ zIndex: 1 }}
                    >
                      <BotIcon sx={{
                        fontSize: 36,
                        color: 'white',
                        filter: 'drop-shadow(0 2px 6px rgba(0,0,0,0.3))',
                        zIndex: 1,
                      }} />
                    </motion.div>
                  </Box>
                </motion.div>
              </Badge>
            </Tooltip>
          </motion.div>
        )}
      </AnimatePresence>
    </>,
    document.body // Render directly to body to avoid any parent container interference
  );
  } catch (error) {
    console.error('🤖 Portal render error:', error);
    return (
      <div style={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        zIndex: 9999,
        background: 'orange',
        color: 'white',
        padding: '10px',
        borderRadius: '5px'
      }}>
        Portal Error: {error.message}
      </div>
    );
  }
};

export default ChatBot;
