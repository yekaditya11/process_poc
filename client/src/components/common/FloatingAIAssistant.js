import React from 'react';
import {
  useTheme,
  useMediaQuery
} from '@mui/material';

const FloatingAIAssistant = ({ 
  isActive, 
  onToggle
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const handleClick = () => {
    onToggle();
  };

  return (
    <div
      className="floating-ai-assistant"
      style={{
        position: 'relative',
        cursor: 'pointer',
        border: 'none',
        outline: 'none',
        background: 'transparent',
        boxShadow: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
      onClick={handleClick}
      title={isActive ? "Close AI Assistant" : "Open AI Assistant"}
    >
      {/* Simple static GIF image */}
      <img
        src="/safety_connect_ai_icon.gif"
        alt="AI Insights Assistant"
        className="ai-insights-icon-enhanced"
        style={{
          width: isMobile ? 70 : 80, // Decreased size slightly
          height: isMobile ? 70 : 80,
          borderRadius: '50%',
          cursor: 'pointer',
          border: 'none !important',
          outline: 'none !important',
          boxSizing: 'border-box',
          objectFit: 'cover',
          objectPosition: 'center center',
          transform: 'scale(1.3)', // Scale up to crop white space
          WebkitTapHighlightColor: 'transparent',
          userSelect: 'none',
          backgroundColor: 'transparent', // Remove white background
          imageRendering: 'crisp-edges',
        }}
      />
    </div>
  );
};

export default FloatingAIAssistant;
