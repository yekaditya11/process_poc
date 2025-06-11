import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Box,
  Typography,
  useTheme,
  useMediaQuery
} from '@mui/material';

const FloatingAIAssistant = ({ 
  isActive, 
  onToggle, 
  isLoading = false,
  hasNewInsights = false 
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [isHovered, setIsHovered] = useState(false);
  const handleClick = () => {
    onToggle();
  };

  // Cosmic universe orb variants - deep space with stellar effects
  const orbVariants = {
    idle: {
      scale: [1, 1.05, 1],
      background: [
        "radial-gradient(circle at 30% 30%, #0c1445 0%, #1e3a8a 20%, #312e81 40%, #1e1b4b 70%, #0f0f23 100%)",
        "radial-gradient(circle at 70% 70%, #1e1b4b 0%, #312e81 20%, #1e3a8a 40%, #0c1445 70%, #0f0f23 100%)",
        "radial-gradient(circle at 50% 20%, #312e81 0%, #1e3a8a 20%, #1e1b4b 40%, #0c1445 70%, #0f0f23 100%)",
        "radial-gradient(circle at 30% 30%, #0c1445 0%, #1e3a8a 20%, #312e81 40%, #1e1b4b 70%, #0f0f23 100%)"
      ],
      boxShadow: [
        "0 0 40px rgba(30, 58, 138, 0.8), 0 0 80px rgba(30, 58, 138, 0.4), 0 0 120px rgba(15, 15, 35, 0.6)",
        "0 0 50px rgba(49, 46, 129, 0.8), 0 0 90px rgba(30, 27, 75, 0.4), 0 0 130px rgba(15, 15, 35, 0.6)",
        "0 0 40px rgba(30, 58, 138, 0.8), 0 0 80px rgba(30, 58, 138, 0.4), 0 0 120px rgba(15, 15, 35, 0.6)"
      ],
      transition: {
        duration: 3,
        repeat: Infinity,
        ease: "easeInOut"
      }
    },
    hover: {
      scale: [1.1, 1.2, 1.1],
      background: [
        "radial-gradient(circle at 40% 60%, #1e3a8a 0%, #1e40af 20%, #3b82f6 50%, #1d4ed8 80%, #0f172a 100%)",
        "radial-gradient(circle at 60% 40%, #1d4ed8 0%, #3b82f6 20%, #1e40af 50%, #1e3a8a 80%, #0f172a 100%)",
        "radial-gradient(circle at 30% 70%, #3b82f6 0%, #1e40af 20%, #1d4ed8 50%, #1e3a8a 80%, #0f172a 100%)",
        "radial-gradient(circle at 40% 60%, #1e3a8a 0%, #1e40af 20%, #3b82f6 50%, #1d4ed8 80%, #0f172a 100%)"
      ],
      boxShadow: [
        "0 0 60px rgba(59, 130, 246, 0.9), 0 0 120px rgba(30, 64, 175, 0.6), 0 0 180px rgba(30, 64, 175, 0.3)",
        "0 0 70px rgba(30, 64, 175, 0.9), 0 0 140px rgba(59, 130, 246, 0.6), 0 0 200px rgba(29, 78, 216, 0.3)",
        "0 0 60px rgba(59, 130, 246, 0.9), 0 0 120px rgba(30, 64, 175, 0.6), 0 0 180px rgba(30, 64, 175, 0.3)"
      ],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }
    },
    active: {
      scale: [1.15, 1.25, 1.15],
      background: [
        "radial-gradient(circle at 50% 50%, #3b82f6 0%, #1e40af 25%, #1d4ed8 50%, #1e3a8a 75%, #0f172a 100%)",
        "radial-gradient(circle at 30% 70%, #60a5fa 0%, #3b82f6 25%, #1e40af 50%, #1d4ed8 75%, #0f172a 100%)",
        "radial-gradient(circle at 70% 30%, #1e40af 0%, #3b82f6 25%, #60a5fa 50%, #1e40af 75%, #0f172a 100%)",
        "radial-gradient(circle at 50% 50%, #3b82f6 0%, #1e40af 25%, #1d4ed8 50%, #1e3a8a 75%, #0f172a 100%)"
      ],
      boxShadow: [
        "0 0 80px rgba(59, 130, 246, 1), 0 0 160px rgba(30, 64, 175, 0.8), 0 0 240px rgba(30, 64, 175, 0.4), inset 0 0 30px rgba(255, 255, 255, 0.1)",
        "0 0 90px rgba(96, 165, 250, 1), 0 0 180px rgba(59, 130, 246, 0.8), 0 0 270px rgba(30, 64, 175, 0.4), inset 0 0 40px rgba(255, 255, 255, 0.1)",
        "0 0 80px rgba(59, 130, 246, 1), 0 0 160px rgba(30, 64, 175, 0.8), 0 0 240px rgba(30, 64, 175, 0.4), inset 0 0 30px rgba(255, 255, 255, 0.1)"
      ],
      transition: {
        duration: 2.5,
        repeat: Infinity,
        ease: "easeInOut"
      }
    },
    loading: {
      scale: [1, 1.3, 0.9, 1.2, 1],
      background: [
        "radial-gradient(circle at 50% 50%, #60a5fa 0%, #3b82f6 30%, #1e40af 60%, #1e3a8a 100%)",
        "radial-gradient(circle at 30% 70%, #3b82f6 0%, #60a5fa 30%, #1e40af 60%, #1d4ed8 100%)",
        "radial-gradient(circle at 70% 30%, #1e40af 0%, #3b82f6 30%, #60a5fa 60%, #1e3a8a 100%)",
        "radial-gradient(circle at 20% 80%, #60a5fa 0%, #1e40af 30%, #3b82f6 60%, #1d4ed8 100%)",
        "radial-gradient(circle at 50% 50%, #3b82f6 0%, #60a5fa 30%, #1e40af 60%, #1e3a8a 100%)"
      ],
      boxShadow: [
        "0 0 60px rgba(96, 165, 250, 0.9), 0 0 120px rgba(59, 130, 246, 0.6), 0 0 180px rgba(30, 64, 175, 0.3)",
        "0 0 70px rgba(59, 130, 246, 0.9), 0 0 140px rgba(96, 165, 250, 0.6), 0 0 200px rgba(30, 64, 175, 0.3)",
        "0 0 60px rgba(96, 165, 250, 0.9), 0 0 120px rgba(59, 130, 246, 0.6), 0 0 180px rgba(30, 64, 175, 0.3)"
      ],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  // Flowing stars from center outward
  const starFlowVariants = {
    hidden: {
      scale: 0,
      opacity: 0,
      x: 0,
      y: 0
    },
    visible: (direction) => ({
      scale: [0, 1, 0.8, 0],
      opacity: [0, 1, 0.7, 0],
      x: [0, direction.x * 15, direction.x * 22], // Reduced for smaller orb
      y: [0, direction.y * 15, direction.y * 22],
      transition: {
        duration: 2 + Math.random() * 1,
        repeat: Infinity,
        delay: Math.random() * 2,
        ease: "easeOut"
      }
    })
  };

  // Floating energy particles around the orb
  const energyParticleVariants = {
    hidden: { scale: 0, opacity: 0 },
    visible: {
      scale: [0, 1, 0],
      opacity: [0, 0.9, 0],
      x: [0, (Math.random() - 0.5) * 60],
      y: [0, (Math.random() - 0.5) * 60],
      transition: {
        duration: 3 + Math.random() * 2,
        repeat: Infinity,
        delay: Math.random() * 2,
        ease: "easeOut"
      }
    }
  };

  return (
    <>
      {/* Main cosmic orb in header */}
      <motion.div
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
        onHoverStart={() => setIsHovered(true)}
        onHoverEnd={() => setIsHovered(false)}
        title={isActive ? "Close AI Assistant" : "Open AI Assistant"}
        animate={{
          y: [0, -4, 0],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        {/* Main magical energy orb */}
        <motion.div
          style={{
            width: isMobile ? 36 : 40, // Reduced to match icon button size
            height: isMobile ? 36 : 40,
            borderRadius: '50%',
            position: 'relative',
            cursor: 'pointer',
            border: 'none',
            outline: 'none',
            boxSizing: 'border-box',
            overflow: 'visible', // Changed to visible to show spilling sparkles
            WebkitTapHighlightColor: 'transparent',
            userSelect: 'none',
          }}
          initial="idle"
          animate={isLoading ? "loading" : isActive ? "active" : isHovered ? "hover" : "idle"}
          variants={orbVariants}
        >
          {/* Flowing stars from center in all directions */}
          <AnimatePresence>
            {[...Array(32)].map((_, i) => {
              // Calculate direction for each star (360 degrees divided by number of stars)
              const angle = (i * 11.25) * (Math.PI / 180); // 360/32 = 11.25 degrees
              const direction = {
                x: Math.cos(angle),
                y: Math.sin(angle)
              };

              return (
                <motion.div
                  key={`flowing-star-${i}`}
                  style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    width: Math.random() * 2 + 1,
                    height: Math.random() * 2 + 1,
                    borderRadius: '50%',
                    background: 'radial-gradient(circle, rgba(255,255,255,1), rgba(255,255,255,0.8))',
                    transform: 'translate(-50%, -50%)',
                    pointerEvents: 'none',
                    boxShadow: '0 0 4px rgba(255,255,255,0.9)',
                  }}
                  initial="hidden"
                  animate="visible"
                  custom={direction}
                  variants={starFlowVariants}
                />
              );
            })}
          </AnimatePresence>

          {/* Secondary layer of flowing stars */}
          <AnimatePresence>
            {[...Array(24)].map((_, i) => {
              // Offset angles for secondary layer
              const angle = (i * 15 + 7.5) * (Math.PI / 180); // Offset by 7.5 degrees
              const direction = {
                x: Math.cos(angle),
                y: Math.sin(angle)
              };

              return (
                <motion.div
                  key={`flowing-star-2-${i}`}
                  style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    width: Math.random() * 1.5 + 0.5,
                    height: Math.random() * 1.5 + 0.5,
                    borderRadius: '50%',
                    background: 'radial-gradient(circle, rgba(255,255,255,0.8), rgba(255,255,255,0.6))',
                    transform: 'translate(-50%, -50%)',
                    pointerEvents: 'none',
                    boxShadow: '0 0 3px rgba(255,255,255,0.7)',
                  }}
                  initial="hidden"
                  animate="visible"
                  custom={direction}
                  variants={starFlowVariants}
                />
              );
            })}
          </AnimatePresence>

          {/* Micro stars for dense flow effect */}
          <AnimatePresence>
            {[...Array(16)].map((_, i) => {
              // Random directions for micro stars
              const angle = (i * 22.5 + Math.random() * 10) * (Math.PI / 180);
              const direction = {
                x: Math.cos(angle),
                y: Math.sin(angle)
              };

              return (
                <motion.div
                  key={`micro-star-${i}`}
                  style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    width: Math.random() * 1 + 0.5,
                    height: Math.random() * 1 + 0.5,
                    borderRadius: '50%',
                    background: 'radial-gradient(circle, rgba(255,255,255,0.9), rgba(255,255,255,0.4))',
                    transform: 'translate(-50%, -50%)',
                    pointerEvents: 'none',
                    boxShadow: '0 0 2px rgba(255,255,255,0.6)',
                  }}
                  initial="hidden"
                  animate="visible"
                  custom={direction}
                  variants={starFlowVariants}
                />
              );
            })}
          </AnimatePresence>


        </motion.div>

        {/* Floating energy particles around the orb */}
        <AnimatePresence>
          {(isActive || isLoading || isHovered) && (
            <>
              {[...Array(5)].map((_, i) => (
                <motion.div
                  key={`energy-${i}`}
                  style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    width: 3,
                    height: 3,
                    borderRadius: '50%',
                    background: isActive
                      ? 'radial-gradient(circle, rgba(59, 130, 246, 0.9), rgba(30, 64, 175, 0.5))'
                      : isLoading
                      ? 'radial-gradient(circle, rgba(96, 165, 250, 0.9), rgba(59, 130, 246, 0.5))'
                      : 'radial-gradient(circle, rgba(96, 165, 250, 0.8), rgba(59, 130, 246, 0.4))',
                    transform: 'translate(-50%, -50%)',
                    pointerEvents: 'none',
                    boxShadow: isActive
                      ? '0 0 8px rgba(59, 130, 246, 0.8)'
                      : isLoading
                      ? '0 0 8px rgba(96, 165, 250, 0.8)'
                      : '0 0 6px rgba(96, 165, 250, 0.6)',
                  }}
                  initial="hidden"
                  animate="visible"
                  exit="hidden"
                  variants={energyParticleVariants}
                />
              ))}
            </>
          )}
        </AnimatePresence>

        {/* Pulsing notification ring for new insights */}
        <AnimatePresence>
          {hasNewInsights && !isActive && (
            <motion.div
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                width: isMobile ? 46 : 50, // Adjusted for smaller orb
                height: isMobile ? 46 : 50,
                borderRadius: '50%',
                border: '2px solid rgba(96, 165, 250, 0.6)',
                transform: 'translate(-50%, -50%)',
                pointerEvents: 'none',
              }}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{
                scale: [0.8, 1.2, 0.8],
                opacity: [0, 0.8, 0],
              }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
          )}
        </AnimatePresence>
      </motion.div>


    </>
  );
};

export default FloatingAIAssistant;
