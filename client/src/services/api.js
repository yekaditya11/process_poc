/**
 * API Service for AI Safety Summarizer
 * Handles all communication with the backend API
 */

import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
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

  // Dashboard data
  async getDashboardData(customerId = null, daysBack = 7) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;
    return api.get('/dashboard', { params });
  }

  // Comprehensive summary
  async getComprehensiveSummary(customerId = null, daysBack = 30, includeRawData = false) {
    return api.post('/summary/comprehensive', {
      customer_id: customerId,
      days_back: daysBack,
      include_raw_data: includeRawData,
    });
  }

  // Module-specific summaries
  async getModuleSummary(module, customerId = null, daysBack = 30) {
    return api.post('/summary/module', {
      module,
      customer_id: customerId,
      days_back: daysBack,
    });
  }

  // Permit summary
  async getPermitSummary(customerId = null, daysBack = 30) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;
    return api.get('/summary/permit', { params });
  }

  // Incident summary
  async getIncidentSummary(customerId = null, daysBack = 30) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;
    return api.get('/summary/incident', { params });
  }

  // Action summary
  async getActionSummary(customerId = null, daysBack = 30) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;
    return api.get('/summary/action', { params });
  }

  // Inspection summary
  async getInspectionSummary(customerId = null, daysBack = 30) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;
    return api.get('/summary/inspection', { params });
  }

  // KPI metrics
  async getKPIMetrics(customerId = null, daysBack = 30) {
    const params = { days_back: daysBack };
    if (customerId) params.customer_id = customerId;
    return api.get('/metrics/kpi', { params });
  }
}

// Export singleton instance
export default new ApiService();

// Export individual methods for convenience
export const {
  healthCheck,
  getDashboardData,
  getComprehensiveSummary,
  getModuleSummary,
  getPermitSummary,
  getIncidentSummary,
  getActionSummary,
  getInspectionSummary,
  getKPIMetrics,
} = new ApiService();
