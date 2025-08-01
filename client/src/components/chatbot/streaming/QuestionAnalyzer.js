/**
 * Question Analyzer
 * Analyzes user questions to determine intent and appropriate streaming messages
 */

import { QUESTION_PATTERNS, MODULE_KEYWORDS } from '../../../utils/streaming/messagePatterns';

export class QuestionAnalyzer {
  static detectQuestionType(message, currentModule = null) {
    const lowerMessage = message.toLowerCase();
    
    // Check each question pattern
    for (const [type, patterns] of Object.entries(QUESTION_PATTERNS)) {
      if (patterns.some(pattern => pattern.test(lowerMessage))) {
        return type;
      }
    }
    
    // If no specific pattern found, try to infer from context
    return this.inferQuestionType(lowerMessage, currentModule);
  }
  
  static inferQuestionType(message, currentModule) {
    // Chart-related keywords
    if (this.containsChartKeywords(message)) {
      return 'create-chart';
    }
    
    // Analysis keywords
    if (this.containsAnalysisKeywords(message)) {
      return 'analysis';
    }
    
    // Data display keywords
    if (this.containsDataKeywords(message)) {
      return 'show-data';
    }
    
    // Default to general if nothing specific found
    return 'general';
  }
  
  static containsChartKeywords(message) {
    const chartKeywords = [
      'chart', 'graph', 'plot', 'visualize', 'visual',
      'bar', 'line', 'pie', 'scatter', 'histogram'
    ];
    return chartKeywords.some(keyword => message.includes(keyword));
  }
  
  static containsAnalysisKeywords(message) {
    const analysisKeywords = [
      'analyze', 'analysis', 'insight', 'pattern', 'trend',
      'correlation', 'relationship', 'deep', 'detailed'
    ];
    return analysisKeywords.some(keyword => message.includes(keyword));
  }
  
  static containsDataKeywords(message) {
    const dataKeywords = [
      'show', 'display', 'get', 'fetch', 'retrieve',
      'view', 'see', 'list', 'data', 'information'
    ];
    return dataKeywords.some(keyword => message.includes(keyword));
  }
  
  static detectModuleFromMessage(message) {
    const lowerMessage = message.toLowerCase();
    
    for (const [module, patterns] of Object.entries(MODULE_KEYWORDS)) {
      if (patterns.some(pattern => pattern.test(lowerMessage))) {
        return module;
      }
    }
    
    return null;
  }
  
  static detectMultipleModules(message) {
    const lowerMessage = message.toLowerCase();
    const detectedModules = [];
    
    for (const [module, patterns] of Object.entries(MODULE_KEYWORDS)) {
      if (patterns.some(pattern => pattern.test(lowerMessage))) {
        detectedModules.push(module);
      }
    }
    
    return detectedModules;
  }
  
  static isCrossModuleQuery(message) {
    const detectedModules = this.detectMultipleModules(message);
    return detectedModules.length > 1;
  }
  
  static detectTimeContext(message) {
    const lowerMessage = message.toLowerCase();
    
    // Recent/current time indicators
    if (/recent|latest|current|today|this week|this month/i.test(lowerMessage)) {
      return 'recent';
    }
    
    // Historical time indicators
    if (/historical|past|previous|last year|archive|old/i.test(lowerMessage)) {
      return 'historical';
    }
    
    // Custom date range indicators
    if (/between|from.*to|specific.*date|range|period/i.test(lowerMessage)) {
      return 'custom';
    }
    
    return 'default';
  }
  
  static detectUrgency(message) {
    const lowerMessage = message.toLowerCase();
    
    const urgentKeywords = [
      'urgent', 'critical', 'immediate', 'emergency',
      'asap', 'priority', 'alert', 'warning'
    ];
    
    return urgentKeywords.some(keyword => lowerMessage.includes(keyword));
  }
  
  static detectDataScope(message) {
    const lowerMessage = message.toLowerCase();
    
    // Comprehensive scope
    if (/all|everything|comprehensive|complete|full|entire/i.test(lowerMessage)) {
      return 'comprehensive';
    }
    
    // Summary scope
    if (/summary|overview|brief|highlights|key/i.test(lowerMessage)) {
      return 'summary';
    }
    
    // Detailed scope
    if (/detailed|deep|thorough|extensive|in-depth/i.test(lowerMessage)) {
      return 'detailed';
    }
    
    // Specific scope
    if (/specific|particular|certain|individual/i.test(lowerMessage)) {
      return 'specific';
    }
    
    return 'standard';
  }
  
  static analyzeQuestion(message, dashboardContext) {
    const analysis = {
      questionType: this.detectQuestionType(message, dashboardContext.activeModule),
      detectedModule: this.detectModuleFromMessage(message),
      isMultiModule: this.isCrossModuleQuery(message),
      timeContext: this.detectTimeContext(message),
      urgency: this.detectUrgency(message),
      dataScope: this.detectDataScope(message),
      complexity: 'medium' // Will be overridden by ComplexityAnalyzer
    };
    
    // Adjust question type based on context
    if (analysis.isMultiModule) {
      analysis.questionType = 'comprehensive-analysis';
    }
    
    if (analysis.urgency) {
      analysis.questionType = 'alert';
    }
    
    return analysis;
  }
  
  static getContextualHints(analysis, dashboardContext) {
    const hints = [];
    
    // Module context hints
    if (analysis.detectedModule && analysis.detectedModule !== dashboardContext.activeModule) {
      hints.push(`Switching context to ${analysis.detectedModule}`);
    }
    
    // Time context hints
    if (analysis.timeContext === 'custom' && !dashboardContext.dateRange.isCustom) {
      hints.push('Custom date range detected');
    }
    
    // Complexity hints
    if (analysis.isMultiModule) {
      hints.push('Cross-module analysis required');
    }
    
    // Urgency hints
    if (analysis.urgency) {
      hints.push('High priority request');
    }
    
    return hints;
  }
}
