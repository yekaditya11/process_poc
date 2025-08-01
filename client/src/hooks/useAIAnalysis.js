/**
 * useAIAnalysis Hook
 * Manages AI analysis data for individual modules and comprehensive analysis
 */

import { useState, useEffect, useCallback } from 'react';
import {
  getIncidentInvestigationAIAnalysis,
  getActionTrackingAIAnalysis,
  getDriverSafetyAIAnalysis,
  getObservationTrackerAIAnalysis,
  getComprehensiveAIAnalysis,
  getAIAnalysisStatus,
} from '../services/api';

export const useAIAnalysis = () => {
  const [analysisData, setAnalysisData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [aiStatus, setAiStatus] = useState(null);

  // Get AI system status
  const fetchAIStatus = useCallback(async () => {
    try {
      const status = await getAIAnalysisStatus();
      setAiStatus(status);
      return status;
    } catch (err) {
      console.error('Error fetching AI status:', err);
      setAiStatus({ ai_available: false, error: err.message });
      return { ai_available: false };
    }
  }, []);

  // Fetch analysis for a specific module
  const fetchModuleAnalysis = useCallback(async (module, options = {}) => {
    const {
      customerId = null,
      daysBack = 30,
      includeAI = true
    } = options;

    console.log('useAIAnalysis: Starting fetchModuleAnalysis for:', module, options);

    try {
      setLoading(true);
      setError(null);

      let response;
      switch (module) {
        case 'incident_investigation':
          response = await getIncidentInvestigationAIAnalysis(customerId, daysBack, includeAI);
          break;
        case 'action_tracking':
          response = await getActionTrackingAIAnalysis(customerId, daysBack, includeAI);
          break;
        case 'driver_safety_checklists':
          response = await getDriverSafetyAIAnalysis(customerId, daysBack, includeAI);
          break;
        case 'observation_tracker':
          response = await getObservationTrackerAIAnalysis(customerId, daysBack, includeAI);
          break;
        default:
          throw new Error(`Unknown module: ${module}`);
      }

      console.log('useAIAnalysis: Raw API response:', response);
      console.log('useAIAnalysis: AI analysis in response:', response?.ai_analysis);
      console.log('useAIAnalysis: Insights count:', response?.ai_analysis?.insights?.length);

      if (response && response.success) {
        console.log('useAIAnalysis: Setting analysis data for module:', module);

        // Force state update with a new object reference
        setAnalysisData(prev => {
          const newData = {
            ...prev,
            [module]: { ...response } // Create new object reference
          };
          console.log('useAIAnalysis: Updated analysisData:', newData);
          console.log('useAIAnalysis: New data for module:', newData[module]);
          return newData;
        });

        console.log('useAIAnalysis: State update completed for module:', module);
        return response;
      } else {
        console.log('useAIAnalysis: Invalid response format:', response);
        throw new Error('Invalid response format');
      }
    } catch (err) {
      console.error(`Error fetching ${module} analysis:`, err);
      setError(err);

      // Return mock data for development
      const mockResponse = getMockModuleAnalysis(module, includeAI);
      console.log('useAIAnalysis: Using mock data for module:', module, mockResponse);
      setAnalysisData(prev => ({
        ...prev,
        [module]: mockResponse
      }));
      return mockResponse;
    } finally {
      setLoading(false);
      console.log('useAIAnalysis: fetchModuleAnalysis completed for:', module);
    }
  }, []);

  // Fetch comprehensive analysis
  const fetchComprehensiveAnalysis = useCallback(async (options = {}) => {
    const {
      customerId = null,
      daysBack = 30,
      includeAI = true,
      modules = 'all'
    } = options;

    try {
      setLoading(true);
      setError(null);

      const response = await getComprehensiveAIAnalysis(customerId, daysBack, includeAI, modules);

      if (response && response.success) {
        setAnalysisData(prev => ({
          ...prev,
          comprehensive: response
        }));
        return response;
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      console.error('Error fetching comprehensive analysis:', err);
      setError(err);
      
      // Return mock data for development
      const mockResponse = getMockComprehensiveAnalysis(includeAI);
      setAnalysisData(prev => ({
        ...prev,
        comprehensive: mockResponse
      }));
      return mockResponse;
    } finally {
      setLoading(false);
    }
  }, []);

  // Note: AI status is now fetched manually when needed

  return {
    analysisData,
    loading,
    error,
    aiStatus,
    fetchModuleAnalysis,
    fetchComprehensiveAnalysis,
    fetchAIStatus,
  };
};

// Mock data generators for development
const getMockModuleAnalysis = (module, includeAI) => {
  const baseData = {
    success: true,
    module: module,
    module_name: getModuleName(module),
    dashboard_data: getMockDashboardData(module),
    generated_at: new Date().toISOString(),
    time_filter: {
      days_back: 30,
      start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      end_date: new Date().toISOString(),
      customer_id: null
    }
  };

  if (includeAI) {
    baseData.ai_analysis = getMockAIAnalysis(module);
  }

  return baseData;
};

const getMockComprehensiveAnalysis = (includeAI) => {
  const baseData = {
    success: true,
    analysis_type: "comprehensive",
    modules_analyzed: ["incident_investigation", "action_tracking", "driver_safety_checklists", "observation_tracker"],
    dashboard_data: {
      incident_investigation: getMockDashboardData('incident_investigation'),
      action_tracking: getMockDashboardData('action_tracking'),
      driver_safety_checklists: getMockDashboardData('driver_safety_checklists'),
      observation_tracker: getMockDashboardData('observation_tracker')
    },
    generated_at: new Date().toISOString(),
    time_filter: {
      days_back: 30,
      start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      end_date: new Date().toISOString(),
      customer_id: null
    },
    metadata: {
      modules_count: 4,
      ai_enabled: includeAI,
      ai_available: true
    }
  };

  if (includeAI) {
    baseData.ai_analysis = {
      summary: "Overall safety performance shows strong compliance across all modules with opportunities for improvement in incident response times.",
      risk_level: "Medium",
      insights: [
        { text: "Current incident rate of 15 incidents per month shows 20% improvement from last quarter", sentiment: "positive" },
        { text: "Driver safety compliance at 87.5% exceeds industry standard of 85%", sentiment: "positive" },
        { text: "Action tracking completion rate of 78.2% indicates room for improvement", sentiment: "negative" },
        { text: "Observation tracker shows 88 total observations with 73.9% closure rate", sentiment: "neutral" },
        { text: "Equipment failure remains the leading cause of incidents at 53%", sentiment: "negative" },
        { text: "Factory floor continues to be the highest risk area with 67% of incidents", sentiment: "negative" },
        { text: "Current investigation completion time averages 48 hours, meeting SLA requirements", sentiment: "positive" },
        { text: "Vehicle fitness rate of 90.3% demonstrates effective maintenance programs", sentiment: "positive" },
        { text: "PPE compliance issues represent 19% of all safety observations", sentiment: "negative" },
        { text: "Overdue actions affect 22% of assigned personnel requiring attention", sentiment: "negative" },
        { text: "Implement targeted equipment maintenance program to reduce failure incidents", sentiment: "neutral" },
        { text: "Establish monthly safety training focused on factory floor operations", sentiment: "neutral" }
      ]
    };
  }

  return baseData;
};

const getModuleName = (module) => {
  const names = {
    incident_investigation: "Incident Investigation",
    action_tracking: "Action Tracking",
    driver_safety_checklists: "Driver Safety Checklists",
    observation_tracker: "Observation Tracker"
  };
  return names[module] || module;
};

const getMockDashboardData = (module) => {
  // Return simplified mock data for each module
  const mockData = {
    incident_investigation: { incidents_reported: 15, open_incidents: 3, closed_incidents: 12 },
    action_tracking: { actions_created: 25, actions_completed: 20, overdue_actions: 5 },
    driver_safety_checklists: { checklists_completed: 45, vehicles_unfit: 2, compliance_rate: 87.5 },
    observation_tracker: { total_observations: 88, open_observations: 23, closed_observations: 65 }
  };
  return mockData[module] || {};
};

const getMockAIAnalysis = (module) => {
  const analyses = {
    incident_investigation: {
      summary: "Incident investigation module shows moderate activity with 15 incidents reported and 3 still under investigation.",
      risk_level: "Medium",
      insights: [
        { text: "Current incident count of 15 represents a 10% decrease from previous period", sentiment: "positive" },
        { text: "Investigation completion time averages 48 hours, meeting target SLA", sentiment: "positive" },
        { text: "Equipment failure accounts for 53% of all reported incidents", sentiment: "negative" },
        { text: "Factory floor remains the highest risk area with 10 incidents", sentiment: "negative" },
        { text: "Personal injury incidents decreased by 25% compared to last month", sentiment: "positive" },
        { text: "Property damage incidents show stable trend with 8 occurrences", sentiment: "neutral" },
        { text: "Near miss reporting increased by 15%, indicating improved safety culture", sentiment: "positive" },
        { text: "Environmental incidents remain low at 2 occurrences this period", sentiment: "positive" },
        { text: "Implement preventive maintenance program for critical equipment", sentiment: "neutral" },
        { text: "Conduct safety walkthrough focused on factory floor operations", sentiment: "neutral" }
      ]
    },
    action_tracking: {
      summary: "Action tracking shows good progress with 80% completion rate, though 5 actions remain overdue.",
      risk_level: "Low",
      insights: [
        "• Total of 25 actions created this period, up 15% from last month",
        "• Completion rate of 80% meets organizational target of 75%",
        "• Average action completion time is 5.2 days, within acceptable range",
        "• 5 overdue actions require immediate attention from supervisors",
        "• Corrective actions show 85% effectiveness rate based on follow-up",
        "• Preventive actions account for 40% of all actions created",
        "• High-priority actions completed within 24 hours in 90% of cases",
        "• Employee engagement in action completion improved by 12%",
        "• Establish weekly review process for overdue actions",
        "• Implement automated reminders for action due dates"
      ]
    },
    driver_safety_checklists: {
      summary: "Driver safety compliance at 87.5% with 2 vehicles currently deemed unfit for operation.",
      risk_level: "Low",
      insights: [
        "• Daily checklist completion rate of 87.5% exceeds target of 85%",
        "• 45 checklists completed out of 52 scheduled this week",
        "• Vehicle fitness rate of 93.5% indicates effective maintenance",
        "• 2 vehicles currently unfit due to brake and tire issues",
        "• Pre-trip inspection compliance improved by 8% this quarter",
        "• Driver training completion rate stands at 96% organization-wide",
        "• Vehicle defect reporting increased by 20%, showing improved awareness",
        "• Fuel efficiency improved by 5% due to better vehicle maintenance",
        "• Schedule immediate repairs for unfit vehicles",
        "• Recognize top-performing drivers for consistent compliance"
      ]
    },
    observation_tracker: {
      summary: "Observation tracking shows active safety monitoring with 88 observations and 74% closure rate.",
      risk_level: "Medium",
      insights: [
        "• Total of 88 observations recorded, up 12% from previous period",
        "• Closure rate of 73.9% indicates good follow-through on issues",
        "• Production area accounts for 28% of all safety observations",
        "• PPE compliance issues represent 19% of observations",
        "• Housekeeping concerns decreased by 15% showing improvement",
        "• High-priority observations resolved within 24 hours in 85% of cases",
        "• Employee-reported observations increased by 22%, showing engagement",
        "• Repeat observations in same areas decreased by 18%",
        "• Focus training on PPE compliance in production areas",
        "• Implement monthly safety observation review meetings"
      ]
    }
  };
  return analyses[module] || { summary: "No analysis available", risk_level: "Unknown", insights: [] };
};

export default useAIAnalysis;
