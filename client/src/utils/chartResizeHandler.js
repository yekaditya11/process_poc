/**
 * Universal Chart Resize Handler
 * Handles resizing for all chart types used in the dashboard
 * Supports: Recharts, Chart.js, ECharts, Plotly
 */

export class ChartResizeHandler {
  constructor() {
    this.chartRefs = new Map();
    this.isResizing = false;
    this.resizeTimeout = null;
  }

  /**
   * Register a chart reference for resize handling
   */
  registerChart(id, chartRef, type = 'auto') {
    this.chartRefs.set(id, { ref: chartRef, type });
  }

  /**
   * Unregister a chart reference
   */
  unregisterChart(id) {
    this.chartRefs.delete(id);
  }

  /**
   * Comprehensive resize handler for all chart types
   */
  resizeAllCharts(delay = 100) {
    if (this.isResizing) return;
    
    this.isResizing = true;
    
    if (this.resizeTimeout) {
      clearTimeout(this.resizeTimeout);
    }

    this.resizeTimeout = setTimeout(() => {
      try {
        // 1. Resize registered Chart.js instances
        this.chartRefs.forEach(({ ref, type }, id) => {
          if (type === 'chartjs' && ref?.current?.chartInstance) {
            ref.current.chartInstance.resize();
          }
        });

        // 2. Force Recharts ResponsiveContainer resize
        this.resizeRechartsContainers();

        // 3. Resize ECharts instances
        this.resizeEChartsInstances();

        // 4. Resize Plotly charts
        this.resizePlotlyCharts();

        // 5. Trigger global window resize for any remaining responsive components
        window.dispatchEvent(new Event('resize'));

      } catch (error) {
        console.warn('Error during chart resize:', error);
      } finally {
        this.isResizing = false;
      }
    }, delay);
  }

  /**
   * Resize Recharts ResponsiveContainer components
   */
  resizeRechartsContainers() {
    const rechartContainers = document.querySelectorAll('.recharts-responsive-container');
    rechartContainers.forEach(container => {
      // Force resize by temporarily changing dimensions
      const originalWidth = container.style.width;
      const originalHeight = container.style.height;
      
      // Trigger resize observer
      container.style.width = '99.9%';
      container.style.height = '99.9%';
      
      requestAnimationFrame(() => {
        container.style.width = originalWidth || '100%';
        container.style.height = originalHeight || '100%';
        
        // Additional trigger for stubborn containers
        setTimeout(() => {
          const resizeEvent = new Event('resize');
          container.dispatchEvent(resizeEvent);
        }, 50);
      });
    });
  }

  /**
   * Resize ECharts instances
   */
  resizeEChartsInstances() {
    // Method 1: Find by echarts instance attribute
    const echartsContainers = document.querySelectorAll('[_echarts_instance_]');
    echartsContainers.forEach(container => {
      const echartsInstance = container._echarts_instance_;
      if (echartsInstance && typeof echartsInstance.resize === 'function') {
        try {
          echartsInstance.resize();
        } catch (error) {
          console.warn('Error resizing ECharts instance:', error);
        }
      }
    });

    // Method 2: Find by class name (ReactECharts)
    const reactEChartsContainers = document.querySelectorAll('.echarts-for-react');
    reactEChartsContainers.forEach(container => {
      const echartsInstance = container.querySelector('div[_echarts_instance_]');
      if (echartsInstance && echartsInstance._echarts_instance_) {
        try {
          echartsInstance._echarts_instance_.resize();
        } catch (error) {
          console.warn('Error resizing ReactECharts instance:', error);
        }
      }
    });
  }

  /**
   * Resize Plotly charts
   */
  resizePlotlyCharts() {
    if (typeof window !== 'undefined' && window.Plotly) {
      try {
        // Method 1: Resize all Plotly plots
        if (window.Plotly.Plots && typeof window.Plotly.Plots.resize === 'function') {
          window.Plotly.Plots.resize();
        }

        // Method 2: Find and resize individual Plotly containers
        const plotlyContainers = document.querySelectorAll('.plotly-graph-div');
        plotlyContainers.forEach(container => {
          if (window.Plotly.Plots && typeof window.Plotly.Plots.resize === 'function') {
            window.Plotly.Plots.resize(container);
          }
        });
      } catch (error) {
        console.warn('Error resizing Plotly charts:', error);
      }
    }
  }

  /**
   * Handle AI panel toggle events with proper timing
   */
  handleAIPanelToggle(event) {
    let delay = 100; // Default delay
    
    if (event?.detail?.phase) {
      switch (event.detail.phase) {
        case 'start':
          delay = 50;
          break;
        case 'mid':
          delay = 200;
          break;
        case 'complete':
          delay = 450;
          break;
        default:
          delay = 100;
      }
    } else if (event?.type === 'resize') {
      delay = 100;
    } else {
      delay = 350; // Legacy events
    }

    this.resizeAllCharts(delay);
  }

  /**
   * Setup event listeners for chart resizing
   */
  setupEventListeners() {
    const handleResize = (event) => this.handleAIPanelToggle(event);

    // Listen for window resize events
    window.addEventListener('resize', handleResize);

    // Listen for AI panel events
    window.addEventListener('ai-panel-toggle', handleResize);

    // Listen for legacy chatbot events
    window.addEventListener('chatbot-toggle', handleResize);

    // Return cleanup function
    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('ai-panel-toggle', handleResize);
      window.removeEventListener('chatbot-toggle', handleResize);
    };
  }

  /**
   * Cleanup all resources
   */
  cleanup() {
    if (this.resizeTimeout) {
      clearTimeout(this.resizeTimeout);
    }
    this.chartRefs.clear();
    this.isResizing = false;
  }
}

// Create a singleton instance
export const chartResizeHandler = new ChartResizeHandler();

/**
 * React hook for easy chart resize handling
 */
export const useChartResize = () => {
  const setupResize = () => chartResizeHandler.setupEventListeners();
  const resizeCharts = (delay) => chartResizeHandler.resizeAllCharts(delay);
  const registerChart = (id, ref, type) => chartResizeHandler.registerChart(id, ref, type);
  const unregisterChart = (id) => chartResizeHandler.unregisterChart(id);

  return {
    setupResize,
    resizeCharts,
    registerChart,
    unregisterChart
  };
};
