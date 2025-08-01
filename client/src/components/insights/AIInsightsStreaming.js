/**
 * AI Insights Streaming Component
 * Simple streaming feedback while AI analysis is being generated
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Search as SearchIcon,
  DataObject as DataIcon,
  TrendingUp as TrendIcon,
  Lightbulb as InsightIcon,
  AutoAwesome as SparkleIcon,
  Assessment as AssessmentIcon,
  Security as SecurityIcon,
  Speed as ProcessIcon,
  DirectionsCar as CarIcon,
  Visibility as VisibilityIcon,
  Build as BuildIcon,
  School as SchoolIcon,
  Psychology as BrainIcon
} from '@mui/icons-material';

// Simple message configurations
const AI_INSIGHTS_MESSAGES = {
  'incident-investigation': [
    { text: "Scanning incident database...", icon: SearchIcon },
    { text: "Processing incident patterns...", icon: DataIcon },
    { text: "Identifying critical incidents...", icon: SecurityIcon },
    { text: "Calculating incident trends...", icon: TrendIcon },
    { text: "Evaluating safety protocols...", icon: SecurityIcon },
    { text: "Applying AI algorithms...", icon: BrainIcon },
    { text: "Generating incident insights...", icon: InsightIcon },
    { text: "Compiling analysis report...", icon: SparkleIcon },
    { text: "Finalizing recommendations...", icon: AssessmentIcon }
  ],
  'action-tracking': [
    { text: "Scanning action database...", icon: SearchIcon },
    { text: "Processing completion rates...", icon: DataIcon },
    { text: "Evaluating deadline compliance...", icon: ProcessIcon },
    { text: "Calculating efficiency metrics...", icon: TrendIcon },
    { text: "Identifying overdue actions...", icon: AssessmentIcon },
    { text: "Applying AI algorithms...", icon: BrainIcon },
    { text: "Generating efficiency insights...", icon: InsightIcon },
    { text: "Compiling action report...", icon: SparkleIcon },
    { text: "Finalizing action recommendations...", icon: AssessmentIcon }
  ],
  'driver-safety': [
    { text: "Scanning driver safety data...", icon: CarIcon },
    { text: "Processing compliance metrics...", icon: DataIcon },
    { text: "Evaluating vehicle fitness...", icon: BuildIcon },
    { text: "Calculating safety scores...", icon: TrendIcon },
    { text: "Identifying safety gaps...", icon: AssessmentIcon },
    { text: "Applying AI algorithms...", icon: BrainIcon },
    { text: "Generating safety insights...", icon: InsightIcon },
    { text: "Compiling safety report...", icon: SparkleIcon },
    { text: "Finalizing safety recommendations...", icon: AssessmentIcon }
  ],
  'observation-tracker': [
    { text: "Scanning observation data...", icon: VisibilityIcon },
    { text: "Processing safety patterns...", icon: DataIcon },
    { text: "Evaluating observation categories...", icon: AssessmentIcon },
    { text: "Calculating observation trends...", icon: TrendIcon },
    { text: "Identifying recurring issues...", icon: AssessmentIcon },
    { text: "Applying AI algorithms...", icon: BrainIcon },
    { text: "Generating observation insights...", icon: InsightIcon },
    { text: "Compiling observation report...", icon: SparkleIcon },
    { text: "Finalizing observation recommendations...", icon: AssessmentIcon }
  ],
  'equipment-asset': [
    { text: "Scanning equipment database...", icon: BuildIcon },
    { text: "Processing maintenance records...", icon: DataIcon },
    { text: "Evaluating asset conditions...", icon: SearchIcon },
    { text: "Calculating maintenance schedules...", icon: TrendIcon },
    { text: "Identifying equipment risks...", icon: AssessmentIcon },
    { text: "Applying AI algorithms...", icon: BrainIcon },
    { text: "Generating equipment insights...", icon: InsightIcon },
    { text: "Compiling equipment report...", icon: SparkleIcon },
    { text: "Finalizing equipment recommendations...", icon: AssessmentIcon }
  ],
  'employee-training': [
    { text: "Scanning training database...", icon: SchoolIcon },
    { text: "Processing completion rates...", icon: DataIcon },
    { text: "Evaluating certification status...", icon: AssessmentIcon },
    { text: "Calculating training metrics...", icon: TrendIcon },
    { text: "Identifying training gaps...", icon: AssessmentIcon },
    { text: "Applying AI algorithms...", icon: BrainIcon },
    { text: "Generating training insights...", icon: InsightIcon },
    { text: "Compiling training report...", icon: SparkleIcon },
    { text: "Finalizing training recommendations...", icon: AssessmentIcon }
  ],
  'risk-assessment': [
    { text: "Scanning risk database...", icon: AssessmentIcon },
    { text: "Processing risk levels...", icon: DataIcon },
    { text: "Evaluating mitigation strategies...", icon: SecurityIcon },
    { text: "Calculating risk probabilities...", icon: TrendIcon },
    { text: "Identifying high-priority risks...", icon: AssessmentIcon },
    { text: "Applying AI algorithms...", icon: BrainIcon },
    { text: "Generating risk insights...", icon: InsightIcon },
    { text: "Compiling risk report...", icon: SparkleIcon },
    { text: "Finalizing risk recommendations...", icon: AssessmentIcon }
  ],
  'global-dashboard': [
    { text: "Scanning all modules...", icon: SearchIcon },
    { text: "Processing comprehensive data...", icon: DataIcon },
    { text: "Cross-referencing metrics...", icon: ProcessIcon },
    { text: "Calculating system-wide trends...", icon: TrendIcon },
    { text: "Identifying patterns across modules...", icon: SearchIcon },
    { text: "Applying AI algorithms...", icon: BrainIcon },
    { text: "Generating holistic insights...", icon: InsightIcon },
    { text: "Compiling comprehensive report...", icon: SparkleIcon },
    { text: "Finalizing global recommendations...", icon: AssessmentIcon }
  ],
  'default': [
    { text: "Starting AI analysis...", icon: BrainIcon },
    { text: "Processing safety data...", icon: DataIcon },
    { text: "Analyzing patterns...", icon: SearchIcon },
    { text: "Calculating metrics...", icon: TrendIcon },
    { text: "Identifying key areas...", icon: AssessmentIcon },
    { text: "Applying AI algorithms...", icon: BrainIcon },
    { text: "Generating insights...", icon: InsightIcon },
    { text: "Compiling report...", icon: SparkleIcon },
    { text: "Finalizing recommendations...", icon: AssessmentIcon }
  ]
};

const AIInsightsStreaming = ({
  module,
  isVisible = true,
  onComplete,
  maxDuration = 12000 // 12 seconds for AI analysis
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [isComplete, setIsComplete] = useState(false);
  const timeoutRef = useRef(null);
  const startTimeRef = useRef(Date.now());

  // Get messages for the specific module
  const getMessages = (module) => {
    return AI_INSIGHTS_MESSAGES[module] || AI_INSIGHTS_MESSAGES.default;
  };

  useEffect(() => {
    if (!isVisible || !module) {
      setIsComplete(false);
      return;
    }

    const messages = getMessages(module);
    const timing = messages.map(() => 1300); // 1.3 seconds per step for 9 steps = ~12 seconds

    startTimeRef.current = Date.now();
    setCurrentStep(0);
    setCompletedSteps([]);
    setIsComplete(false);

    const executeStep = (stepIndex) => {
      if (stepIndex >= messages.length) {
        // Stay on the last step, don't restart
        setCurrentStep(messages.length - 1);
        setCompletedSteps(prev => [...prev, messages.length - 1]);
        return;
      }

      setCurrentStep(stepIndex);
      setCompletedSteps(prev => [...prev, stepIndex]);

      const stepDuration = timing[stepIndex] || 1300;

      timeoutRef.current = setTimeout(() => {
        executeStep(stepIndex + 1);
      }, stepDuration);
    };

    executeStep(0);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [module, isVisible]);

  const handleComplete = () => {
    setIsComplete(true);
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }

    if (onComplete) {
      const duration = startTimeRef.current ? Date.now() - startTimeRef.current : 0;
      onComplete({ duration, module });
    }
  };

  const getStepIcon = (isActive, isCompleted, IconComponent) => {
    if (isCompleted) {
      return <CheckCircleIcon sx={{ color: 'success.main', fontSize: 18 }} />;
    }
    if (isActive) {
      return <IconComponent sx={{ color: 'primary.main', fontSize: 18 }} />;
    }
    return <IconComponent sx={{ color: 'grey.400', fontSize: 18 }} />;
  };

  const getStepColor = (stepIndex) => {
    if (completedSteps.includes(stepIndex)) return 'success.main';
    if (stepIndex === currentStep && !isComplete) return 'primary.main';
    return 'grey.500';
  };

  // Don't render if not visible
  if (!isVisible) {
    return null;
  }

  const messages = getMessages(module);

  return (
    <Box sx={{ p: 2 }}>
      <Stepper orientation="vertical" sx={{ '& .MuiStepConnector-line': { minHeight: 20 } }}>
        {messages.map((message, index) => (
          <Step key={index} active={index <= currentStep} completed={completedSteps.includes(index)}>
            <StepLabel
              StepIconComponent={() => getStepIcon(
                index === currentStep && !isComplete, 
                completedSteps.includes(index), 
                message.icon
              )}
              sx={{
                '& .MuiStepLabel-label': {
                  fontWeight: index === currentStep && !isComplete ? 600 : 400,
                  color: getStepColor(index),
                  fontSize: '0.9rem',
                  lineHeight: 1.3
                }
              }}
            >
              {message.text}
            </StepLabel>
          </Step>
        ))}
      </Stepper>
    </Box>
  );
};

export default AIInsightsStreaming; 