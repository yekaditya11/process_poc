/**
 * Streaming Thinking Indicator
 * Main component that orchestrates the context-aware streaming experience
 */

import React, { useState, useEffect, useRef } from 'react';
import { Box, Paper, Fade } from '@mui/material';
import { ContextAwareStreaming } from './ContextAwareStreaming';
import StreamingMessageRenderer from './StreamingMessageRenderer';
import { useDashboardContext } from '../../../contexts/DashboardContext';

const StreamingThinkingIndicator = ({
  userMessage,
  onComplete,
  isVisible = true,
  maxDuration = 10000 // Maximum duration in ms (10 seconds)
}) => {
  const { context } = useDashboardContext();
  console.log('🎬 StreamingThinkingIndicator context:', context);
  const [streamingData, setStreamingData] = useState(null);
  const [isActive, setIsActive] = useState(false);
  const timeoutRef = useRef(null);
  const startTimeRef = useRef(null);

  useEffect(() => {
    console.log('🎬 StreamingThinkingIndicator useEffect:', { userMessage, isVisible, context });

    if (!userMessage || !isVisible) {
      console.log('🎬 Not starting streaming - missing userMessage or not visible');
      setIsActive(false);
      return;
    }

    // Generate streaming messages based on context
    try {
      console.log('🎬 Generating streaming messages...');

      // Try to generate messages, but provide fallback if it fails
      let data;
      try {
        data = ContextAwareStreaming.generateMessages(userMessage, context);
        console.log('🎬 Generated streaming data:', data);
      } catch (streamingError) {
        console.error('🎬 Error with ContextAwareStreaming, using fallback:', streamingError);
        // Provide a simple fallback
        data = {
          messages: [
            "🧠 Understanding your safety query...",
            "🔍 Connecting to safety databases...",
            "📊 Processing safety data...",
            "🧮 Calculating key metrics...",
            "💡 Generating AI insights...",
            "✅ Preparing comprehensive response..."
          ],
          timing: [1000, 1000, 1000, 1000, 1000, 1000],
          analysis: { questionType: 'general', complexity: 'medium' },
          complexity: 'medium'
        };
      }

      setStreamingData(data);
      setIsActive(true);
      startTimeRef.current = Date.now();

      // Set maximum duration timeout as safety net
      timeoutRef.current = setTimeout(() => {
        handleComplete();
      }, maxDuration);

    } catch (error) {
      console.error('Error initializing streaming:', error);
      // Fallback to simple completion
      setTimeout(handleComplete, 1000);
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [userMessage, isVisible, context, maxDuration]);

  const handleComplete = () => {
    setIsActive(false);
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }

    // Call onComplete with timing information
    if (onComplete) {
      const duration = startTimeRef.current ? Date.now() - startTimeRef.current : 0;
      onComplete({
        duration,
        analysis: streamingData?.analysis,
        complexity: streamingData?.complexity
      });
    }
  };

  // Don't render if not active or no streaming data
  if (!isActive || !streamingData) {
    console.log('🎬 Not rendering StreamingThinkingIndicator:', { isActive, hasStreamingData: !!streamingData });
    return null;
  }

  console.log('🎬 Rendering StreamingThinkingIndicator with data:', streamingData);

  return (
    <Fade in={isActive} timeout={300}>
      <Box sx={{ mb: 2 }}>
        <Paper 
          elevation={2}
          sx={{ 
            borderRadius: 3,
            overflow: 'hidden',
            border: '1px solid',
            borderColor: 'divider',
            background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)'
          }}
        >
          <StreamingMessageRenderer
            messages={streamingData.messages}
            timing={streamingData.timing}
            analysis={streamingData.analysis}
            complexity={streamingData.complexity}
            onComplete={handleComplete}
          />
        </Paper>
      </Box>
    </Fade>
  );
};

export default StreamingThinkingIndicator;
