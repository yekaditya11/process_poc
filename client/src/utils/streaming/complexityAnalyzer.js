/**
 * Complexity Analyzer
 * Determines the complexity level of user questions for appropriate streaming duration
 */

import { COMPLEXITY_INDICATORS, MODULE_KEYWORDS } from './messagePatterns';

export class ComplexityAnalyzer {
  static assessComplexity(message, dashboardContext) {
    const { filters, activeModule, queryHistory } = dashboardContext;
    
    let complexityScore = 0;
    const lowerMessage = message.toLowerCase();
    
    // Base complexity from message content
    complexityScore += this.analyzeMessageComplexity(lowerMessage);
    
    // Add complexity based on filters
    complexityScore += this.analyzeFilterComplexity(filters);
    
    // Add complexity based on module
    complexityScore += this.analyzeModuleComplexity(activeModule);
    
    // Add complexity based on query history (context awareness)
    complexityScore += this.analyzeContextComplexity(queryHistory, lowerMessage);
    
    // Convert score to complexity level
    return this.scoreToComplexity(complexityScore);
  }
  
  static analyzeMessageComplexity(message) {
    let score = 0;
    
    // Check for complexity indicators
    COMPLEXITY_INDICATORS.simple.forEach(pattern => {
      if (pattern.test(message)) score += 1;
    });
    
    COMPLEXITY_INDICATORS.medium.forEach(pattern => {
      if (pattern.test(message)) score += 2;
    });
    
    COMPLEXITY_INDICATORS.complex.forEach(pattern => {
      if (pattern.test(message)) score += 3;
    });
    
    // Check for multiple modules mentioned
    const modulesFound = Object.keys(MODULE_KEYWORDS).filter(module => 
      MODULE_KEYWORDS[module].some(pattern => pattern.test(message))
    );
    
    if (modulesFound.length > 1) {
      score += 3; // Cross-module queries are complex
    }
    
    // Check for multiple question types
    const questionWords = ['what', 'how', 'why', 'when', 'where', 'which'];
    const questionCount = questionWords.filter(word => 
      message.includes(word)
    ).length;
    
    if (questionCount > 1) {
      score += 2; // Multiple questions increase complexity
    }
    
    // Check message length (longer messages tend to be more complex)
    const wordCount = message.split(' ').length;
    if (wordCount > 15) score += 1;
    if (wordCount > 25) score += 2;
    
    return score;
  }
  
  static analyzeFilterComplexity(filters) {
    let score = 0;
    
    // Custom date ranges add complexity
    if (filters.startDate && filters.endDate) {
      score += 2;
    }
    
    // Customer-specific queries add complexity
    if (filters.customerId) {
      score += 1;
    }
    
    // Long time ranges add complexity
    if (filters.daysBack > 365) {
      score += 2;
    } else if (filters.daysBack > 90) {
      score += 1;
    }
    
    return score;
  }
  
  static analyzeModuleComplexity(activeModule) {
    // Some modules are inherently more complex
    const moduleComplexity = {
      'global-dashboard': 3, // Most complex - all modules
      'incident-investigation': 2, // Complex - detailed analysis
      'risk-assessment': 2, // Complex - risk calculations
      'action-tracking': 1, // Medium - tracking data
      'driver-safety': 1, // Medium - checklist data
      'observation-tracker': 1, // Medium - observation data
      'equipment-asset': 2, // Complex - asset management
      'employee-training': 1 // Medium - training records
    };
    
    return moduleComplexity[activeModule] || 1;
  }
  
  static analyzeContextComplexity(queryHistory, currentMessage) {
    let score = 0;
    
    // If this is a follow-up question, it might be more complex
    if (queryHistory.length > 0) {
      const lastQuery = queryHistory[queryHistory.length - 1];
      
      // Check for follow-up indicators
      const followUpIndicators = [
        'also', 'additionally', 'furthermore', 'moreover',
        'and', 'plus', 'what about', 'how about'
      ];
      
      const isFollowUp = followUpIndicators.some(indicator => 
        currentMessage.includes(indicator)
      );
      
      if (isFollowUp) {
        score += 1;
      }
      
      // If asking about different module than last query, add complexity
      if (lastQuery.module && this.detectModuleFromMessage(currentMessage) !== lastQuery.module) {
        score += 1;
      }
    }
    
    return score;
  }
  
  static detectModuleFromMessage(message) {
    for (const [module, patterns] of Object.entries(MODULE_KEYWORDS)) {
      if (patterns.some(pattern => pattern.test(message))) {
        return module;
      }
    }
    return null;
  }
  
  static scoreToComplexity(score) {
    if (score <= 2) return 'simple';
    if (score <= 5) return 'medium';
    if (score <= 8) return 'complex';
    return 'cross-module';
  }
  
  static getExpectedDuration(complexity) {
    // Return expected duration in milliseconds
    const durations = {
      'simple': 2000,    // 2 seconds
      'medium': 4000,    // 4 seconds
      'complex': 6000,   // 6 seconds
      'cross-module': 8000 // 8 seconds
    };
    
    return durations[complexity] || 3000;
  }
  
  static getStepCount(complexity) {
    // Return number of streaming steps
    const stepCounts = {
      'simple': 3,
      'medium': 4,
      'complex': 5,
      'cross-module': 6
    };
    
    return stepCounts[complexity] || 3;
  }
}
