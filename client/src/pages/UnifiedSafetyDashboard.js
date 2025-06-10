/**
 * Unified Safety Dashboard
 * Single dashboard with module dropdown, AI analysis toggle, and integrated chatbot
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  FormControl,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Psychology as AIIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  DirectionsCar as CarIcon,
  Visibility as VisibilityIcon,
  Build as BuildIcon,
  School as SchoolIcon,
  Assessment as AssessmentIcon,
  Dashboard as DashboardIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

// Import components
import ErrorBoundary from '../components/common/ErrorBoundary';
import DatePickerFilter from '../components/filters/DatePickerFilter';
import SafetyConnectLayout from '../components/layout/SafetyConnectLayout';

// Import chart components
import GlobalDashboardCharts from '../components/charts/GlobalDashboardCharts';
import IncidentCharts from '../components/charts/IncidentCharts';
import RiskAssessmentCharts from '../components/charts/RiskAssessmentCharts';
import ActionTrackingCharts from '../components/charts/ActionTrackingCharts';
import DriverSafetyCharts from '../components/charts/DriverSafetyCharts';
import ObservationCharts from '../components/charts/ObservationCharts';
import EquipmentAssetCharts from '../components/charts/EquipmentAssetCharts';
import EmployeeTrainingCharts from '../components/charts/EmployeeTrainingCharts';

// Import custom dashboard
import DashboardManager from '../components/dashboard/DashboardManager';

// Import unified insights panel
import UnifiedInsightsPanel from '../components/insights/UnifiedInsightsPanel';

// Import API service
import ApiService from '../services/api';

// Module configuration
const SAFETY_MODULES = [
  {
    id: 'global-dashboard',
    label: 'Global Dashboard',
    icon: DashboardIcon,
    color: '#1f2937'
  },
  {
    id: 'incident-investigation',
    label: 'Incident Investigation',
    icon: SecurityIcon,
    color: '#dc2626'
  },
  {
    id: 'risk-assessment',
    label: 'Risk Assessment',
    icon: AssessmentIcon,
    color: '#ea580c'
  },
  {
    id: 'action-tracking',
    label: 'Action Tracking',
    icon: TrendingUpIcon,
    color: '#059669'
  },
  {
    id: 'driver-safety',
    label: 'Driver Safety',
    icon: CarIcon,
    color: '#0284c7'
  },
  {
    id: 'observation-tracker',
    label: 'Observation Tracker',
    icon: VisibilityIcon,
    color: '#7c3aed'
  },
  {
    id: 'equipment-asset',
    label: 'Equipment & Assets',
    icon: BuildIcon,
    color: '#be185d'
  },
  {
    id: 'employee-training',
    label: 'Employee Training',
    icon: SchoolIcon,
    color: '#0891b2'
  },
  {
    id: 'custom-dashboard',
    label: 'Custom Dashboard',
    icon: DashboardIcon,
    color: '#7c3aed'
  }
];

const UnifiedSafetyDashboard = () => {
  const navigate = useNavigate();

  // State management
  const [selectedModule, setSelectedModule] = useState('global-dashboard');
  const [aiAnalysisEnabled, setAiAnalysisEnabled] = useState(false);
  const [moduleData, setModuleData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dateRange, setDateRange] = useState({
    startDate: null,
    endDate: null,
    daysBack: 365
  });

  // AI Analysis state
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState(null);

  // Feedback state - tracks feedback for each insight by index
  const [insightFeedback, setInsightFeedback] = useState({});

  // State for generating more insights
  const [loadingMoreInsights, setLoadingMoreInsights] = useState(false);

  // State for insights panel expansion
  const [insightsPanelExpanded, setInsightsPanelExpanded] = useState(false);

  // State to force chart re-render when AI panel toggles
  const [chartRenderKey, setChartRenderKey] = useState(0);

  // Get current module info
  const currentModule = SAFETY_MODULES.find(m => m.id === selectedModule);

  // Fetch module data
  const fetchModuleData = async (moduleId, dateParams) => {
    // Custom dashboard doesn't need data fetching
    if (moduleId === 'custom-dashboard') {
      setLoading(false);
      setModuleData({}); // Set empty data to indicate loaded
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const { startDate, endDate, daysBack } = dateParams;
      const apiStartDate = startDate ? startDate.toISOString().split('T')[0] : null;
      const apiEndDate = endDate ? endDate.toISOString().split('T')[0] : null;
      const apiDaysBack = daysBack || 365;

      let data;
      switch (moduleId) {
        case 'global-dashboard':
          data = await ApiService.getAllKPIs(null, apiDaysBack);
          break;
        case 'incident-investigation':
          data = await ApiService.getIncidentInvestigationModuleKPIs(
            null, apiStartDate, apiEndDate, apiDaysBack
          );
          break;
        case 'risk-assessment':
          data = await ApiService.getRiskAssessmentModuleKPIs(null, apiDaysBack);
          break;
        case 'action-tracking':
          data = await ApiService.getActionTrackingModuleKPIs(
            null, apiStartDate, apiEndDate, apiDaysBack
          );
          break;
        case 'driver-safety':
          data = await ApiService.getDriverSafetyModuleKPIs(
            null, apiStartDate, apiEndDate, apiDaysBack
          );
          break;
        case 'observation-tracker':
          data = await ApiService.getObservationTrackerModuleKPIs(
            null, apiStartDate, apiEndDate, apiDaysBack
          );
          break;
        case 'equipment-asset':
          data = await ApiService.getEquipmentAssetModuleKPIs(null, apiDaysBack);
          break;
        case 'employee-training':
          data = await ApiService.getEmployeeTrainingModuleKPIs(null, apiDaysBack);
          break;
        default:
          throw new Error(`Unknown module: ${moduleId}`);
      }

      setModuleData(data?.data || data);
    } catch (err) {
      console.error(`Error fetching ${moduleId} data:`, err);
      setError(`Failed to load ${currentModule?.label || moduleId} data. Please try again.`);
    } finally {
      setLoading(false);
    }
  };



  // Load data when module or date range changes
  useEffect(() => {
    fetchModuleData(selectedModule, dateRange);
  }, [selectedModule, dateRange]);

  // Fetch AI analysis when module data changes and AI is enabled
  useEffect(() => {
    console.log('🤖 AI useEffect triggered:', { aiAnalysisEnabled, hasModuleData: !!moduleData, selectedModule });
    if (aiAnalysisEnabled && moduleData) {
      console.log('🤖 Auto-fetching AI analysis due to data change');
      fetchAIAnalysis(selectedModule, moduleData);
    }
  }, [moduleData, aiAnalysisEnabled, selectedModule]);

  // Handle chart resizing when insights panel toggles
  useEffect(() => {
    // Optimized resize handling with proper timing
    const triggerResize = () => {
      // Immediate notification for layout change start
      requestAnimationFrame(() => {
        window.dispatchEvent(new CustomEvent('ai-panel-toggle', {
          detail: {
            insightsPanelOpen: aiAnalysisEnabled,
            phase: 'start'
          }
        }));
      });

      // Resize during animation (mid-point)
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
        window.dispatchEvent(new CustomEvent('ai-panel-toggle', {
          detail: {
            insightsPanelOpen: aiAnalysisEnabled,
            phase: 'mid'
          }
        }));
      }, 200); // Half of animation duration

      // Final resize after animation completes
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
        window.dispatchEvent(new CustomEvent('ai-panel-toggle', {
          detail: {
            insightsPanelOpen: aiAnalysisEnabled,
            phase: 'complete'
          }
        }));
      }, 450); // Slightly after animation duration (400ms)
    };

    triggerResize();
  }, [aiAnalysisEnabled]);

  // Handle module change
  const handleModuleChange = (event) => {
    const newModule = event.target.value;
    setSelectedModule(newModule);
    setModuleData(null);
    // Reset feedback and loading states when module changes
    setInsightFeedback({});
    setLoadingMoreInsights(false);
  };

  // Handle AI toggle - Show/hide AI insights card inline
  const handleAIToggle = (event) => {
    const isEnabled = event.target.checked;
    console.log('🤖 AI Toggle clicked:', isEnabled);
    console.log('🤖 Current moduleData:', moduleData ? 'Available' : 'Not available');
    console.log('🤖 Current selectedModule:', selectedModule);

    setAiAnalysisEnabled(isEnabled);

    // Force chart re-render by updating key
    setChartRenderKey(prev => prev + 1);

    // If enabling AI, fetch AI analysis for current module
    if (isEnabled && moduleData) {
      console.log('🤖 Fetching AI analysis...');
      fetchAIAnalysis(selectedModule, moduleData);
    } else if (isEnabled && !moduleData) {
      console.log('🤖 AI enabled but no module data available yet');
    }

    // Improved event dispatch for layout changes
    requestAnimationFrame(() => {
      // Notify about AI panel toggle with detailed information
      const responsiveWidth = isEnabled ? '40%' : '0%';
      window.dispatchEvent(new CustomEvent('ai-panel-toggle', {
        detail: {
          insightsPanelOpen: isEnabled,
          phase: 'start',
          panelWidth: responsiveWidth
        }
      }));

      // Also dispatch legacy event for backward compatibility
      window.dispatchEvent(new CustomEvent('chatbot-toggle', {
        detail: { insightsPanelOpen: isEnabled }
      }));
    });
  };

  // Handle date range change
  const handleDateRangeChange = (newDateRange) => {
    setDateRange(newDateRange);
  };

  // Fetch AI Analysis for current module
  const fetchAIAnalysis = async (moduleId, data) => {
    console.log('🤖 fetchAIAnalysis called:', { moduleId, hasData: !!data });
    setAiLoading(true);
    setAiError(null);
    // Reset feedback and loading states when fetching new analysis
    setInsightFeedback({});
    setLoadingMoreInsights(false);

    try {
      const { daysBack } = dateRange;
      const apiDaysBack = daysBack || 365;
      console.log('🤖 API call parameters:', { moduleId, apiDaysBack });

      let aiData;
      switch (moduleId) {
        case 'global-dashboard':
          aiData = await ApiService.generateComprehensiveAIAnalysis(null, apiDaysBack);
          break;
        case 'incident-investigation':
          aiData = await ApiService.getIncidentInvestigationAIAnalysis(null, apiDaysBack, true);
          break;
        case 'action-tracking':
          aiData = await ApiService.getActionTrackingAIAnalysis(null, apiDaysBack, true);
          break;
        case 'driver-safety':
          aiData = await ApiService.getDriverSafetyAIAnalysis(null, apiDaysBack, true);
          break;
        case 'observation-tracker':
          aiData = await ApiService.getObservationTrackerAIAnalysis(null, apiDaysBack, true);
          break;
        case 'equipment-asset':
          aiData = await ApiService.getEquipmentAssetAIAnalysis(null, apiDaysBack, true);
          break;
        case 'employee-training':
          aiData = await ApiService.getEmployeeTrainingAIAnalysis(null, apiDaysBack, true);
          break;
        case 'risk-assessment':
          aiData = await ApiService.getRiskAssessmentAIAnalysis(null, apiDaysBack, true);
          break;
        default:
          throw new Error(`AI analysis not available for module: ${moduleId}`);
      }

      console.log('🤖 AI API response:', aiData);
      const analysisData = aiData?.ai_analysis || aiData;
      console.log('🤖 Setting AI analysis:', analysisData);
      setAiAnalysis(analysisData);
    } catch (err) {
      console.error(`🤖 Error fetching AI analysis for ${moduleId}:`, err);
      setAiError(`Failed to load AI insights. Please try again.`);
    } finally {
      setAiLoading(false);
    }
  };

  // Handle refresh
  const handleRefresh = () => {
    fetchModuleData(selectedModule, dateRange);
    if (aiAnalysisEnabled) {
      fetchAIAnalysis(selectedModule, moduleData);
    }
  };

  // Handle insight feedback
  const handleInsightFeedback = async (insightIndex, feedbackType, event) => {
    try {
      // Prevent event bubbling to avoid triggering other handlers
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }

      // Update local state immediately for responsive UI
      setInsightFeedback(prev => ({
        ...prev,
        [insightIndex]: feedbackType
      }));

      // Get the insight text for the API call
      const insight = aiAnalysis?.insights?.[insightIndex];
      const insightText = typeof insight === 'string' ? insight : insight?.text;

      if (!insightText) {
        console.error('No insight text found for index:', insightIndex);
        return;
      }

      // Send feedback to backend
      const feedbackData = {
        module: selectedModule,
        insight_index: insightIndex,
        insight_text: insightText,
        feedback_type: feedbackType,
        timestamp: new Date().toISOString()
      };

      console.log('📝 Sending insight feedback:', feedbackData);
      console.log('📝 Current loading state before feedback:', loading);
      console.log('📝 Current aiLoading state before feedback:', aiLoading);

      // Call API to submit feedback and potentially get more insights
      const response = await ApiService.submitInsightFeedback(feedbackData);

      console.log('📝 Feedback response received:', response);
      console.log('📝 Current loading state after feedback:', loading);
      console.log('📝 Current aiLoading state after feedback:', aiLoading);

      if (response?.additional_insights) {
        // If the API returns additional insights based on feedback, update the analysis
        setAiAnalysis(prev => ({
          ...prev,
          insights: [...(prev?.insights || []), ...response.additional_insights]
        }));
        console.log('✨ Added additional insights based on feedback:', response.additional_insights);
      }

    } catch (error) {
      console.error('Error submitting insight feedback:', error);
      // Revert the feedback state on error
      setInsightFeedback(prev => {
        const newState = { ...prev };
        delete newState[insightIndex];
        return newState;
      });
    }
  };

  // Handle generating more insights based on feedback
  const handleGenerateMoreInsights = async (event) => {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    if (!aiAnalysis?.insights || loadingMoreInsights) return;

    setLoadingMoreInsights(true);

    try {
      console.log('🔄 Generating more insights based on feedback...');

      // Get positive feedback insights to use as examples
      const positiveInsights = aiAnalysis.insights
        .map((insight, index) => ({
          text: typeof insight === 'string' ? insight : insight.text,
          feedback: insightFeedback[index],
          index
        }))
        .filter(item => item.feedback === 'positive')
        .map(item => item.text);

      // Get all existing insights to avoid duplicates
      const existingInsights = aiAnalysis.insights.map(insight =>
        typeof insight === 'string' ? insight : insight.text
      );

      // Call API to generate more data-driven insights
      const response = await ApiService.generateMoreInsights({
        module: selectedModule,
        existing_insights: existingInsights,
        positive_examples: positiveInsights,
        count: 5,
        data_driven: true // Request data-driven insights, not recommendations
      });

      if (response?.additional_insights && response.additional_insights.length > 0) {
        // Add new insights to existing ones with animation
        setAiAnalysis(prev => ({
          ...prev,
          insights: [...(prev?.insights || []), ...response.additional_insights]
        }));

        console.log(`✨ Added ${response.additional_insights.length} new insights based on feedback`);

        // Show success message briefly
        setTimeout(() => {
          console.log('🎉 New insights successfully integrated');
        }, 500);
      } else {
        console.log('⚠️ No additional insights generated');
        setAiError('No new insights could be generated. Try providing more feedback first.');
      }

    } catch (error) {
      console.error('Error generating more insights:', error);
      setAiError('Failed to generate more insights. Please try again.');
    } finally {
      setLoadingMoreInsights(false);
    }
  };

  // Handle removing insights
  const handleRemoveInsight = (insightIndex) => {
    console.log(`Removing insight ${insightIndex}`);

    if (aiAnalysis && aiAnalysis.insights) {
      const updatedInsights = aiAnalysis.insights.filter((_, index) => index !== insightIndex);
      setAiAnalysis(prev => ({
        ...prev,
        insights: updatedInsights
      }));

      // Update feedback state to remove the deleted insight and adjust indices
      setInsightFeedback(prev => {
        const newFeedback = {};
        Object.keys(prev).forEach(key => {
          const index = parseInt(key);
          if (index < insightIndex) {
            newFeedback[index] = prev[key];
          } else if (index > insightIndex) {
            newFeedback[index - 1] = prev[key];
          }
          // Skip the deleted insight (index === insightIndex)
        });
        return newFeedback;
      });
    }
  };

  // Render module charts
  const renderModuleCharts = () => {
    // Custom dashboard doesn't need moduleData
    if (selectedModule === 'custom-dashboard') {
      return <DashboardManager />;
    }

    if (!moduleData) return null;

    switch (selectedModule) {
      case 'global-dashboard':
        return <GlobalDashboardCharts data={moduleData} />;
      case 'incident-investigation':
        return <IncidentCharts data={moduleData} />;
      case 'risk-assessment':
        return <RiskAssessmentCharts data={moduleData} />;
      case 'action-tracking':
        return <ActionTrackingCharts data={moduleData} />;
      case 'driver-safety':
        return <DriverSafetyCharts data={moduleData} />;
      case 'observation-tracker':
        return <ObservationCharts data={moduleData} />;
      case 'equipment-asset':
        return <EquipmentAssetCharts data={moduleData} />;
      case 'employee-training':
        return <EmployeeTrainingCharts data={moduleData} />;
      default:
        return <Alert severity="warning">Module charts not implemented yet.</Alert>;
    }
  };

  // Clean header actions - minimal
  const headerActions = (
    <>
      {/* Keep header minimal - AI toggle moved to module level */}
    </>
  );

  return (
    <ErrorBoundary>
      <SafetyConnectLayout
        headerActions={headerActions}
      >

        <Box sx={{ px: 1.5, py: 2 }}> {/* Reduced padding from 3 to 1.5 for more width */}
          {/* Simplified Clean Header */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            {/* Clean Controls Row - Module Dropdown Left, Date Picker & Reload Right */}
            <Box sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              mb: 3,
              py: 2,
              borderBottom: '1px solid #e5e7eb'
            }}>
              {/* Beautiful Module Dropdown with Animations */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
              >
                <FormControl size="small" sx={{ minWidth: 280 }}>
                  <Select
                    value={selectedModule}
                    onChange={handleModuleChange}
                    displayEmpty
                    sx={{
                      bgcolor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: 0.5, // Reduced border radius
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      '& .MuiOutlinedInput-notchedOutline': {
                        border: 'none',
                      },
                      '&:hover': {
                        bgcolor: '#f8fafc',
                        boxShadow: '0 4px 12px 0 rgba(0, 0, 0, 0.1)',
                        transform: 'translateY(-1px)',
                      },
                      '& .MuiSelect-select': {
                        py: 1.5,
                        px: 2,
                      }
                    }}
                  >
                    {SAFETY_MODULES.map((module, index) => {
                      const IconComponent = module.icon;
                      return (
                        <MenuItem
                          key={module.id}
                          value={module.id}
                          sx={{
                            borderRadius: 0.25, // Reduced border radius
                            mx: 1,
                            my: 0.5,
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              backgroundColor: `${module.color}15`,
                              transform: 'translateX(4px)',
                            },
                          }}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <motion.div
                              whileHover={{ scale: 1.1, rotate: 5 }}
                              transition={{ duration: 0.2 }}
                            >
                              <IconComponent sx={{ fontSize: 20, color: module.color }} />
                            </motion.div>
                            <Typography sx={{ fontWeight: 500 }}>{module.label}</Typography>
                          </Box>
                        </MenuItem>
                      );
                    })}
                  </Select>
                </FormControl>
              </motion.div>

              {/* Right side - AI Toggle, Date Picker & Reload */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {/* AI Analysis Toggle with Slide Effect */}
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{
                    type: "spring",
                    stiffness: 300,
                    damping: 30,
                    delay: 0.1
                  }}
                >
                  <FormControlLabel
                    control={
                      <motion.div
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        transition={{ type: "spring", stiffness: 400, damping: 17 }}
                      >
                        <Switch
                          checked={aiAnalysisEnabled}
                          onChange={handleAIToggle}
                          sx={{
                            '& .MuiSwitch-switchBase': {
                              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                              '&.Mui-checked': {
                                color: '#10b981',
                                transform: 'translateX(20px)',
                                '& + .MuiSwitch-track': {
                                  backgroundColor: '#10b981',
                                  opacity: 1,
                                },
                              },
                            },
                            '& .MuiSwitch-track': {
                              borderRadius: 12,
                              backgroundColor: '#e5e7eb',
                              opacity: 1,
                              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                            },
                            '& .MuiSwitch-thumb': {
                              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
                              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                            },
                          }}
                        />
                      </motion.div>
                    }
                    label={
                      <motion.div
                        animate={{
                          x: aiAnalysisEnabled ? 5 : 0,
                          scale: aiAnalysisEnabled ? 1.02 : 1,
                        }}
                        transition={{
                          type: "spring",
                          stiffness: 300,
                          damping: 25
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <motion.div
                            animate={{
                              rotate: aiAnalysisEnabled ? 360 : 0,
                              scale: aiAnalysisEnabled ? 1.1 : 1,
                            }}
                            transition={{
                              duration: 0.5,
                              type: "spring",
                              stiffness: 200,
                              damping: 15
                            }}
                          >
                            <AIIcon sx={{
                              fontSize: 18,
                              color: aiAnalysisEnabled ? '#10b981' : '#6b7280',
                              transition: 'color 0.3s ease'
                            }} />
                          </motion.div>
                          <Typography sx={{
                            color: aiAnalysisEnabled ? '#092f57' : '#6b7280',
                            fontSize: '0.875rem',
                            fontWeight: aiAnalysisEnabled ? 600 : 500,
                            transition: 'all 0.3s ease'
                          }}>
                            AI Insights
                          </Typography>
                        </Box>
                      </motion.div>
                    }
                  />
                </motion.div>

                {/* Compact Date Picker */}
                <DatePickerFilter
                  dateRange={dateRange}
                  onDateRangeChange={handleDateRangeChange}
                  showDaysBackOption={true}
                  compact={true}
                />

                {/* Reload Button */}
                <Tooltip title="Refresh Data">
                  <IconButton
                    onClick={handleRefresh}
                    disabled={loading}
                    sx={{
                      bgcolor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: 1.5,
                      p: 1.5,
                      '&:hover': {
                        bgcolor: '#f8fafc',
                      },
                      '&:disabled': {
                        bgcolor: '#f1f5f9',
                      }
                    }}
                  >
                    <RefreshIcon sx={{ fontSize: 20, color: loading ? '#94a3b8' : '#092f57' }} />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>


          </motion.div>

          {/* Error Display */}
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              <Alert severity="error" sx={{ mb: 3, border: '1px solid #fecaca' }}>
                {error}
              </Alert>
            </motion.div>
          )}

          {/* Main Content Area - Responsive Layout */}
          <Box sx={{
            display: 'flex',
            gap: 2, // Reduced gap from 3 to 2 for more space utilization
            minHeight: '600px',
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            overflow: 'hidden', // Prevent layout shifts during animation
            position: 'relative'
          }}>
            {/* Dashboard Content - Adjusts width based on insights panel */}
            <Box sx={{
              flex: aiAnalysisEnabled ? '1 1 60%' : '1 1 100%',
              transition: 'flex 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              minWidth: 0, // Prevents flex item from overflowing
              maxWidth: aiAnalysisEnabled ? '60%' : '100%',
              overflow: 'hidden' // Ensure content doesn't overflow during transition
            }}>
              <AnimatePresence mode="wait">
                <motion.div
                  key={selectedModule}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                {/* Module Card - Clean Design */}
                <Card
                  sx={{
                    minHeight: 600,
                    bgcolor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: 2,
                    overflow: 'hidden',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    height: '100%'
                  }}
                >
                  <CardContent sx={{ p: 3, height: '100%' }}>
                    {loading ? (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Box sx={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          justifyContent: 'center',
                          py: 8,
                          gap: 2
                        }}>
                          {/* Beautiful Loading Animation with Module Icon */}
                          <motion.div
                            animate={{
                              rotate: [0, 10, -10, 0],
                              y: [0, -5, 5, 0],
                              scale: [1, 1.1, 0.9, 1]
                            }}
                            transition={{
                              duration: 2,
                              repeat: Infinity,
                              ease: "easeInOut"
                            }}
                          >
                            {(() => {
                              const currentModule = SAFETY_MODULES.find(m => m.id === selectedModule);
                              const IconComponent = currentModule?.icon || CircularProgress;
                              return currentModule ? (
                                <IconComponent
                                  sx={{
                                    fontSize: 48,
                                    color: currentModule.color,
                                    filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1))'
                                  }}
                                />
                              ) : (
                                <CircularProgress size={48} sx={{ color: '#092f57' }} />
                              );
                            })()}
                          </motion.div>
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                          >
                            <Typography
                              variant="h6"
                              sx={{
                                color: '#6b7280',
                                fontWeight: 500,
                                textAlign: 'center'
                              }}
                            >
                              Loading {SAFETY_MODULES.find(m => m.id === selectedModule)?.label}...
                            </Typography>
                          </motion.div>
                        </Box>
                      </motion.div>
                    ) : (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Box
                          key={`charts-${chartRenderKey}-${aiAnalysisEnabled ? 'with-ai' : 'without-ai'}`}
                          sx={{
                            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                            width: '100%',
                            overflow: 'hidden'
                          }}
                        >
                          {/* Module Charts - Clean Display */}
                          {renderModuleCharts()}
                        </Box>
                      </motion.div>
                    )}
                  </CardContent>
                </Card>
                </motion.div>
              </AnimatePresence>
            </Box>

            {/* Unified Insights Panel - Slides in from right */}
            <AnimatePresence>
              {aiAnalysisEnabled && (
                <motion.div
                  initial={{ opacity: 0, x: 300, width: 0 }}
                  animate={{
                    opacity: 1,
                    x: 0,
                    width: '40%'
                  }}
                  exit={{ opacity: 0, x: 300, width: 0 }}
                  transition={{
                    duration: 0.4,
                    ease: [0.4, 0, 0.2, 1]
                  }}
                  style={{
                    flex: '0 0 40%',
                    minWidth: '420px',
                    maxWidth: 'none' // Remove max width constraint to use full 40%
                  }}
                >
                  <UnifiedInsightsPanel
                    aiAnalysis={aiAnalysis}
                    aiLoading={aiLoading}
                    aiError={aiError}
                    insightFeedback={insightFeedback}
                    loadingMoreInsights={loadingMoreInsights}
                    selectedModule={selectedModule}
                    onClose={() => {
                      setAiAnalysisEnabled(false);
                      // Improved event dispatch for panel close
                      requestAnimationFrame(() => {
                        window.dispatchEvent(new CustomEvent('ai-panel-toggle', {
                          detail: {
                            insightsPanelOpen: false,
                            phase: 'start',
                            panelWidth: '0%'
                          }
                        }));

                        // Legacy event for backward compatibility
                        window.dispatchEvent(new CustomEvent('chatbot-toggle', {
                          detail: { insightsPanelOpen: false }
                        }));
                      });
                    }}
                    onFeedback={handleInsightFeedback}
                    onGenerateMore={handleGenerateMoreInsights}
                    onRemoveInsight={handleRemoveInsight}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </Box>
        </Box>
      </SafetyConnectLayout>
    </ErrorBoundary>
  );
};

export default UnifiedSafetyDashboard;
