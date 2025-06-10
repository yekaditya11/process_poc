/**
 * API Service for AI Safety Summarizer
 * Handles all communication with the backend API
 */

import axios from 'axios';
import requestOptimizer from '../utils/requestOptimizer';

// Base API configuration
// const API_BASE_URL ='http://13.51.171.153:9000';
const API_BASE_URL ='http://localhost:9000';


const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // Increased to 2 minutes for large context model processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Response Error:', error);

    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.error || 'Server error occurred';
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error - please check your connection');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred');
    }
  }
);

// API Service Class
class ApiService {
  // Health check
  async healthCheck() {
    return api.get('/health');
  }

  // Removed unwanted API methods:
  // - getDashboardData (replaced by unified dashboard)
  // - getComprehensiveSummary (not needed for 4-module focus)
  // - getModuleSummary (not needed for 4-module focus)
  // - getPermitSummary (not in required 4 modules)
  // - getIncidentSummary (not in required 4 modules)
  // - getActionSummary (not in required 4 modules)
  // - getInspectionSummary (not in required 4 modules)
  // - getKPIMetrics (replaced by specific KPI endpoints)
  // Only keeping the 4 required KPI endpoints and conversational AI

  // Incident Investigation KPIs - Optimized
  async getIncidentInvestigationKPIs(customerId = null, daysBack = 30) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    // Use optimized request with caching
    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/incident-investigation-kpis`,
      { params }
    );
  }

  // Action Tracking KPIs - Optimized
  async getActionTrackingKPIs(customerId = null, daysBack = 30) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/action-tracking-kpis`,
      { params }
    );
  }

  // Driver Safety Checklist KPIs - Optimized
  async getDriverSafetyChecklistKPIs(customerId = null, daysBack = 30) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/driver-safety-checklist-kpis`,
      { params }
    );
  }

  // Observation Tracker KPIs - Optimized
  async getObservationTrackerKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/observation-tracker-kpis`,
      { params }
    );
  }

  // Equipment Asset KPIs - Optimized
  async getEquipmentAssetKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/equipment-asset-kpis`,
      { params }
    );
  }

  // Risk Assessment KPIs - Optimized
  async getRiskAssessmentKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/risk-assessment-kpis`,
      { params }
    );
  }

  // Employee Training KPIs - Optimized
  async getEmployeeTrainingKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/employee-training-kpis`,
      { params }
    );
  }

  // Fetch all KPIs for the safety dashboard - Optimized
  async getAllKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/all-safety-kpis`,
      { params }
    );
  }

  // Individual Module KPI Endpoints
  async getIncidentInvestigationModuleKPIs(customerId = null, startDate = null, endDate = null, daysBack = 365) {
    // Validate parameters - don't send null daysBack
    const params = { days_back: daysBack || 365 };
    if (customerId) params.customer_id = customerId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    // Skip cache if custom date range is used to ensure fresh data
    const skipCache = startDate && endDate;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/incident-investigation/kpis`,
      { params, skipCache }
    );
  }

  async getRiskAssessmentModuleKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/risk-assessment/kpis`,
      { params }
    );
  }

  async getActionTrackingModuleKPIs(customerId = null, startDate = null, endDate = null, daysBack = 365) {
    // Validate parameters - don't send null daysBack
    const params = { days_back: daysBack || 365 };
    if (customerId) params.customer_id = customerId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    // Skip cache if custom date range is used to ensure fresh data
    const skipCache = startDate && endDate;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/action-tracking/kpis`,
      { params, skipCache }
    );
  }

  async getDriverSafetyModuleKPIs(customerId = null, startDate = null, endDate = null, daysBack = 365) {
    // Validate parameters - don't send null daysBack
    const params = { days_back: daysBack || 365 };
    if (customerId) params.customer_id = customerId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    // Skip cache if custom date range is used to ensure fresh data
    const skipCache = startDate && endDate;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/driver-safety/kpis`,
      { params, skipCache }
    );
  }

  async getObservationTrackerModuleKPIs(customerId = null, startDate = null, endDate = null, daysBack = 365) {
    // Validate parameters - don't send null daysBack
    const params = { days_back: daysBack || 365 };
    if (customerId) params.customer_id = customerId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    // Skip cache if custom date range is used to ensure fresh data
    const skipCache = startDate && endDate;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/observation-tracker/kpis`,
      { params, skipCache }
    );
  }

  async getEquipmentAssetModuleKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/equipment-asset/kpis`,
      { params }
    );
  }

  async getEmployeeTrainingModuleKPIs(customerId = null, daysBack = 365) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/api/modules/employee-training/kpis`,
      { params }
    );
  }

  // Conversational AI Chat Methods
  async startConversation(userId = 'anonymous') {
    return api.post('/chat/start', { user_id: userId });
  }

  async sendChatMessage(message, sessionId = null, userId = 'anonymous') {
    // Use debouncing for chat messages to prevent rapid-fire requests
    const debounceKey = `chat_${sessionId}_${userId}`;

    return requestOptimizer.debouncedRequest(
      debounceKey,
      () => api.post('/chat/message', {
        message,
        session_id: sessionId,
        user_id: userId
      }),
      300 // 300ms debounce for chat
    );
  }

  async getChatHistory(sessionId) {
    return api.get(`/chat/history/${sessionId}`);
  }

  async clearConversation(sessionId) {
    return api.delete(`/chat/clear/${sessionId}`);
  }

  async getProactiveInsights(sessionId) {
    return api.get(`/chat/insights/${sessionId}`);
  }

  // Module-specific chat methods
  async sendModuleChatMessage(moduleName, message, sessionId = null) {
    return api.post(`/chat/modules/${moduleName}/message`, {
      message,
      session_id: sessionId
    });
  }

  // AI Analysis Methods - New endpoints for individual modules
  async getIncidentInvestigationAIAnalysis(customerId = null, daysBack = 30, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/incident-investigation`,
      {
        params,
        skipCache: false,  // Allow caching for better performance
        timeout: 120000    // Increased to 2 minutes for large context model processing
      }
    );
  }

  async getActionTrackingAIAnalysis(customerId = null, daysBack = 30, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/action-tracking`,
      {
        params,
        skipCache: false,  // Allow caching for better performance
        timeout: 120000
      }
    );
  }

  async getDriverSafetyAIAnalysis(customerId = null, daysBack = 30, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/driver-safety-checklists`,
      {
        params,
        skipCache: false,  // Allow caching for better performance
        timeout: 120000
      }
    );
  }

  async getObservationTrackerAIAnalysis(customerId = null, daysBack = 30, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/observation-tracker`,
      {
        params,
        skipCache: false,  // Allow caching for better performance
        timeout: 120000  // Increased to 2 minutes for large context model processing
      }
    );
  }

  async getEquipmentAssetAIAnalysis(customerId = null, daysBack = 30, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/equipment-asset-management`,
      { params, skipCache: true }
    );
  }

  async getRiskAssessmentAIAnalysis(customerId = null, daysBack = 30, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/risk-assessment`,
      { params, skipCache: true }
    );
  }

  async getEmployeeTrainingAIAnalysis(customerId = null, daysBack = 30, includeAI = true) {
    const params = { days_back: daysBack, include_ai: includeAI };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/employee-training-fitness`,
      { params, skipCache: true }
    );
  }

  async getComprehensiveAIAnalysis(customerId = null, daysBack = 30, includeAI = true, modules = 'all') {
    const params = {
      days_back: daysBack,
      include_ai: includeAI,
      modules: modules
    };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/comprehensive`,
      { params }
    );
  }

  async getAIAnalysisStatus() {
    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/ai-analysis/status`,
      { params: {} }
    );
  }

  // Submit insight feedback and get additional insights
  async submitInsightFeedback(feedbackData) {
    return api.post('/ai-analysis/feedback', feedbackData);
  }

  // Generate more insights based on feedback and existing insights
  async generateMoreInsights(requestData) {
    return api.post('/ai-analysis/generate-more', requestData);
  }

  // Legacy methods for backward compatibility
  async generateAIAnalysis(module, customerId = null, daysBack = 30) {
    // Map to new endpoints
    switch (module) {
      case 'incident_investigation':
        return this.getIncidentInvestigationAIAnalysis(customerId, daysBack, true);
      case 'action_tracking':
        return this.getActionTrackingAIAnalysis(customerId, daysBack, true);
      case 'driver_safety_checklists':
        return this.getDriverSafetyAIAnalysis(customerId, daysBack, true);
      case 'observation_tracker':
        return this.getObservationTrackerAIAnalysis(customerId, daysBack, true);
      case 'equipment_asset_management':
        return this.getEquipmentAssetAIAnalysis(customerId, daysBack, true);
      case 'risk_assessment':
        return this.getRiskAssessmentAIAnalysis(customerId, daysBack, true);
      case 'employee_training_fitness':
        return this.getEmployeeTrainingAIAnalysis(customerId, daysBack, true);
      default:
        throw new Error(`Unknown module: ${module}`);
    }
  }

  async generateComprehensiveAIAnalysis(customerId = null, daysBack = 30, modules = null) {
    const modulesList = modules ? modules.join(',') : 'all';
    return this.getComprehensiveAIAnalysis(customerId, daysBack, true, modulesList);
  }

  // Dashboard Management Methods
  async saveDashboard(dashboardName, charts, userId = 'anonymous') {
    return api.post('/dashboard/save', {
      dashboard_name: dashboardName,
      charts: charts,
      user_id: userId
    });
  }

  async loadDashboard(dashboardId) {
    return api.get(`/dashboard/load/${dashboardId}`);
  }

  async listDashboards(userId = 'anonymous') {
    const params = { user_id: userId };
    return api.get('/dashboard/list', { params });
  }

  // Chart Management Methods
  async addChartToDashboard(chartData, title, source = 'chat', userId = 'anonymous') {
    return api.post('/dashboard/add-chart', {
      chart_data: chartData,
      title: title,
      source: source,
      user_id: userId
    });
  }

  async getUserCharts(userId = 'anonymous') {
    return api.get(`/dashboard/charts/${userId}`);
  }

  async deleteChart(chartId) {
    return api.delete(`/dashboard/charts/${chartId}`);
  }

  // Generic metrics fetcher for real-time updates - Optimized
  async getMetrics(endpoint, customerId = null, daysBack = 30) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;

    return requestOptimizer.optimizedRequest(
      `${API_BASE_URL}/metrics/${endpoint}`,
      { params }
    );
  }

  // Optimization utilities
  getOptimizationStats() {
    return requestOptimizer.getStats();
  }

  invalidateCache(pattern) {
    return requestOptimizer.invalidateCache(pattern);
  }

  resetOptimizer() {
    return requestOptimizer.reset();
  }
}

// Create singleton instance
const apiService = new ApiService();

// Add requestOptimizer to window for debugging
if (typeof window !== 'undefined') {
  window.requestOptimizer = requestOptimizer;
}

// Export singleton instance
export default apiService;

// Export individual methods for convenience - all safety KPI endpoints, conversational AI, and AI analysis
export const {
  healthCheck,
  getIncidentInvestigationKPIs,
  getActionTrackingKPIs,
  getDriverSafetyChecklistKPIs,
  getObservationTrackerKPIs,
  getEquipmentAssetKPIs,
  getRiskAssessmentKPIs,
  getEmployeeTrainingKPIs,
  getAllKPIs,
  // Module-specific KPI endpoints
  getIncidentInvestigationModuleKPIs,
  getRiskAssessmentModuleKPIs,
  getActionTrackingModuleKPIs,
  getDriverSafetyModuleKPIs,
  getObservationTrackerModuleKPIs,
  getEquipmentAssetModuleKPIs,
  getEmployeeTrainingModuleKPIs,
  // Chat methods
  startConversation,
  sendChatMessage,
  sendModuleChatMessage,
  getChatHistory,
  clearConversation,
  getProactiveInsights,
  // AI Analysis methods
  generateAIAnalysis,
  generateComprehensiveAIAnalysis,
  getIncidentInvestigationAIAnalysis,
  getActionTrackingAIAnalysis,
  getDriverSafetyAIAnalysis,
  getObservationTrackerAIAnalysis,
  getEquipmentAssetAIAnalysis,
  getRiskAssessmentAIAnalysis,
  getEmployeeTrainingAIAnalysis,
  getComprehensiveAIAnalysis,
  getAIAnalysisStatus,
} = apiService;

// Additional exports for the new dashboard
export const fetchAllKPIs = (customerId = null, daysBack = 365) =>
  apiService.getAllKPIs(customerId, daysBack);

export const fetchIncidentKPIs = (customerId = null, daysBack = 365) =>
  apiService.getIncidentInvestigationKPIs(customerId, daysBack);

export const fetchDriverSafetyKPIs = (customerId = null, daysBack = 365) =>
  apiService.getDriverSafetyChecklistKPIs(customerId, daysBack);

export const fetchObservationKPIs = (customerId = null, daysBack = 365) =>
  apiService.getObservationTrackerKPIs(customerId, daysBack);

export const fetchActionTrackingKPIs = (customerId = null, daysBack = 365) =>
  apiService.getActionTrackingKPIs(customerId, daysBack);

export const fetchEquipmentAssetKPIs = (customerId = null, daysBack = 365) =>
  apiService.getEquipmentAssetKPIs(customerId, daysBack);

export const fetchRiskAssessmentKPIs = (customerId = null, daysBack = 365) =>
  apiService.getRiskAssessmentKPIs(customerId, daysBack);

export const fetchEmployeeTrainingKPIs = (customerId = null, daysBack = 365) =>
  apiService.getEmployeeTrainingKPIs(customerId, daysBack);
