/**
 * Global Chart Manager
 * Manages chart addition to dashboard from anywhere in the app
 */

import ApiService from './api';

class ChartManager {
  constructor() {
    this.charts = [];
    this.listeners = [];
    this.loadCharts();
  }

  // Load charts from localStorage and API
  async loadCharts() {
    try {
      // Try API first
      try {
        const response = await ApiService.getUserCharts('anonymous');
        if (response.success && response.charts) {
          this.charts = response.charts;
          this.notifyListeners();
          return;
        }
      } catch (apiError) {
        console.warn('API load failed, using localStorage:', apiError);
      }

      // Fallback to localStorage
      const saved = localStorage.getItem('customDashboardCharts');
      if (saved) {
        this.charts = JSON.parse(saved);
        this.notifyListeners();
      }
    } catch (error) {
      console.error('Error loading charts:', error);
    }
  }

  // Save charts to localStorage
  saveToLocalStorage() {
    try {
      localStorage.setItem('customDashboardCharts', JSON.stringify(this.charts));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  }

  // Add chart from chatbot
  async addChart(chartConfig) {
    try {
      console.log('ChartManager: Adding chart', chartConfig);

      // Try API first
      try {
        const response = await ApiService.addChartToDashboard(
          chartConfig.chartData,
          chartConfig.title || 'AI Generated Chart',
          chartConfig.source || 'chat',
          'anonymous'
        );
        
        if (response.success) {
          // Reload charts from API
          await this.loadCharts();
          this.showNotification('Chart added to dashboard successfully!', 'success');
          return response;
        }
      } catch (apiError) {
        console.warn('API add failed, using localStorage:', apiError);
        
        // Fallback to localStorage
        const newChart = {
          id: `chart_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
          chart_id: `chart_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
          title: chartConfig.title || 'AI Generated Chart',
          chart_data: chartConfig.chartData,
          chartData: chartConfig.chartData, // Keep both for compatibility
          source: chartConfig.source || 'chat',
          created_at: chartConfig.timestamp || new Date().toISOString(),
          size: 6,
          position: this.charts.length
        };

        this.charts.push(newChart);
        this.saveToLocalStorage();
        this.notifyListeners();
        this.showNotification('Chart added to dashboard (saved locally)!', 'success');
        return newChart;
      }
    } catch (error) {
      console.error('Error adding chart:', error);
      this.showNotification('Failed to add chart to dashboard', 'error');
      throw error;
    }
  }

  // Delete chart
  async deleteChart(chartId) {
    try {
      // Try API first
      try {
        await ApiService.deleteChart(chartId);
        await this.loadCharts();
        this.showNotification('Chart removed from dashboard', 'info');
      } catch (apiError) {
        console.warn('API delete failed, using localStorage:', apiError);
        
        // Fallback to localStorage
        this.charts = this.charts.filter(chart => 
          chart.id !== chartId && chart.chart_id !== chartId
        );
        this.saveToLocalStorage();
        this.notifyListeners();
        this.showNotification('Chart removed from dashboard (local only)', 'info');
      }
    } catch (error) {
      console.error('Error deleting chart:', error);
      this.showNotification('Error removing chart', 'error');
    }
  }

  // Update charts (for reordering)
  updateCharts(updatedCharts) {
    this.charts = updatedCharts;
    this.saveToLocalStorage();
    this.notifyListeners();
  }

  // Get all charts
  getCharts() {
    return this.charts;
  }

  // Add listener for chart updates
  addListener(callback) {
    this.listeners.push(callback);
  }

  // Remove listener
  removeListener(callback) {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  // Notify all listeners
  notifyListeners() {
    this.listeners.forEach(callback => {
      try {
        callback(this.charts);
      } catch (error) {
        console.error('Error in chart listener:', error);
      }
    });
  }

  // Show notification (can be overridden by UI components)
  showNotification(message, severity = 'success') {
    console.log(`[${severity.toUpperCase()}] ${message}`);

    // Try to show browser notification if available
    if (window.showNotification) {
      window.showNotification(message, severity);
    } else {
      // Create a custom notification element instead of alert
      this.createCustomNotification(message, severity);
    }
  }

  // Create custom notification when UI notification system is not available
  createCustomNotification(message, severity = 'success') {
    // Remove any existing notifications
    const existingNotification = document.getElementById('chart-manager-notification');
    if (existingNotification) {
      existingNotification.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.id = 'chart-manager-notification';
    notification.style.cssText = `
      position: fixed;
      top: 24px;
      right: 24px;
      z-index: 10000;
      padding: 16px 20px;
      border-radius: 12px;
      color: white;
      font-family: "Roboto", "Helvetica", "Arial", sans-serif;
      font-size: 14px;
      font-weight: 500;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
      transform: translateX(100%);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      max-width: 420px;
      min-width: 300px;
      word-wrap: break-word;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      cursor: pointer;
    `;

    // Set background color based on severity with Material-UI colors
    const colors = {
      success: '#2e7d32',
      error: '#d32f2f',
      warning: '#ed6c02',
      info: '#0288d1'
    };
    notification.style.backgroundColor = colors[severity] || colors.success;

    // Add icon based on severity
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    };
    const icon = icons[severity] || icons.success;

    // Create notification content with close button
    notification.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px;">
        <div style="display: flex; align-items: center; gap: 8px; flex: 1;">
          <span style="font-size: 16px;">${icon}</span>
          <span>${message}</span>
        </div>
        <button
          onclick="this.parentElement.parentElement.click()"
          style="
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.8);
            cursor: pointer;
            font-size: 18px;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background-color 0.2s ease;
          "
          onmouseover="this.style.backgroundColor='rgba(255, 255, 255, 0.1)'"
          onmouseout="this.style.backgroundColor='transparent'"
        >×</button>
      </div>
    `;

    // Add to document
    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
    }, 100);

    // Auto-hide functionality with pause on hover
    let autoHideTimeout;
    const startAutoHide = () => {
      autoHideTimeout = setTimeout(() => {
        hideNotification();
      }, 5000); // 5 seconds
    };

    const hideNotification = () => {
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    };

    // Start auto-hide timer
    startAutoHide();

    // Pause auto-hide on hover
    notification.addEventListener('mouseenter', () => {
      if (autoHideTimeout) {
        clearTimeout(autoHideTimeout);
      }
    });

    // Resume auto-hide when mouse leaves
    notification.addEventListener('mouseleave', () => {
      startAutoHide();
    });

    // Allow manual close on click
    notification.addEventListener('click', () => {
      if (autoHideTimeout) {
        clearTimeout(autoHideTimeout);
      }
      hideNotification();
    });
  }
}

// Create global instance
const chartManager = new ChartManager();

// Expose globally for chatbot integration
window.addChartToDashboard = (chartConfig) => chartManager.addChart(chartConfig);
window.chartManager = chartManager;

export default chartManager;
