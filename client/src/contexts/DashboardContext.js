/**
 * Dashboard Context Provider
 * Manages dashboard state and context for intelligent streaming messages
 */

import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { useLocation } from 'react-router-dom';

const DashboardContext = createContext();

export const useDashboardContext = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboardContext must be used within a DashboardContextProvider');
  }
  return context;
};

// Hook to safely use location
const useOptionalLocation = () => {
  try {
    return useLocation();
  } catch (error) {
    // If not in router context, return null
    return null;
  }
};

export const DashboardContextProvider = ({ children }) => {
  const location = useOptionalLocation();
  
  const [context, setContext] = useState({
    activeModule: 'global-dashboard',
    filters: {
      customerId: null,
      daysBack: 30,
      startDate: null,
      endDate: null
    },
    dateRange: {
      isCustom: false,
      start: null,
      end: null
    },
    lastQuery: null,
    queryHistory: [],
    isLoading: false
  });

  // Update context when route changes (only if location is available)
  useEffect(() => {
    if (!location) return; // Skip if not in router context

    const path = location.pathname;
    if (path.includes('incident')) {
      updateContext({ activeModule: 'incident-investigation' });
    } else if (path.includes('risk')) {
      updateContext({ activeModule: 'risk-assessment' });
    } else if (path.includes('action')) {
      updateContext({ activeModule: 'action-tracking' });
    } else if (path.includes('driver')) {
      updateContext({ activeModule: 'driver-safety' });
    } else if (path.includes('observation')) {
      updateContext({ activeModule: 'observation-tracker' });
    } else if (path.includes('equipment')) {
      updateContext({ activeModule: 'equipment-asset' });
    } else if (path.includes('training')) {
      updateContext({ activeModule: 'employee-training' });
    }
  }, [location]);

  const updateContext = useCallback((updates) => {
    setContext(prev => ({
      ...prev,
      ...updates,
      lastUpdated: new Date().toISOString()
    }));
  }, []);

  const addToQueryHistory = useCallback((query, response) => {
    setContext(prev => ({
      ...prev,
      queryHistory: [
        ...prev.queryHistory.slice(-9), // Keep last 10 queries
        {
          query,
          response,
          timestamp: new Date().toISOString(),
          module: prev.activeModule
        }
      ],
      lastQuery: query
    }));
  }, []);

  const setActiveModule = useCallback((module) => {
    updateContext({ activeModule: module });
  }, [updateContext]);

  const setFilters = useCallback((filters) => {
    setContext(prev => ({
      ...prev,
      filters: { ...prev.filters, ...filters }
    }));
  }, []);

  const setDateRange = useCallback((dateRange) => {
    updateContext({ dateRange });
  }, [updateContext]);

  const setLoading = useCallback((isLoading) => {
    updateContext({ isLoading });
  }, [updateContext]);

  const value = useMemo(() => ({
    context,
    updateContext,
    addToQueryHistory,
    setActiveModule,
    setFilters,
    setDateRange,
    setLoading
  }), [context, updateContext, addToQueryHistory, setActiveModule, setFilters, setDateRange, setLoading]);

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  );
};

export default DashboardContext;
