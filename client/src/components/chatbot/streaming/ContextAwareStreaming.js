/**
 * Context-Aware Streaming Engine
 * Main engine that generates intelligent streaming messages based on context
 */

import { QuestionAnalyzer } from './QuestionAnalyzer';
import { ComplexityAnalyzer } from '../../../utils/streaming/complexityAnalyzer';
import { 
  MODULE_MESSAGES, 
  CROSS_MODULE_MESSAGES, 
  DEFAULT_MESSAGES,
  FILTER_CONTEXT_MESSAGES 
} from './MessageConfigurations';

export class ContextAwareStreaming {
  static generateMessages(userMessage, dashboardContext) {
    try {
      console.log('🧠 ContextAwareStreaming.generateMessages called with:', { userMessage, dashboardContext });

      // Provide fallback context if none provided
      const context = dashboardContext || {
        activeModule: 'global-dashboard',
        filters: { daysBack: 30 },
        dateRange: { isCustom: false }
      };

      // Analyze the question
      const questionAnalysis = QuestionAnalyzer.analyzeQuestion(userMessage, context);
      
      // Assess complexity
      const complexity = ComplexityAnalyzer.assessComplexity(userMessage, context);
      questionAnalysis.complexity = complexity;

      // Generate base messages
      let messages = this.getBaseMessages(questionAnalysis, context);

      // Add filter context if needed
      messages = this.addFilterContext(messages, context);
      
      // Adjust for complexity
      messages = this.adjustForComplexity(messages, complexity);
      
      // Add timing information
      const timing = this.calculateTiming(messages, complexity);

      const result = {
        messages,
        timing,
        analysis: questionAnalysis,
        complexity
      };

      console.log('🧠 Generated streaming result:', result);
      return result;
    } catch (error) {
      console.error('Error generating streaming messages:', error);
      return this.getFallbackMessages();
    }
  }
  
  static getBaseMessages(analysis, dashboardContext) {
    const { questionType, isMultiModule, detectedModule } = analysis;
    const { activeModule } = dashboardContext;
    
    // Handle cross-module queries
    if (isMultiModule) {
      return this.getCrossModuleMessages(questionType);
    }
    
    // Use detected module or current active module
    const targetModule = detectedModule || activeModule;
    
    // Get module-specific messages
    const moduleMessages = MODULE_MESSAGES[targetModule];
    if (moduleMessages && moduleMessages[questionType]) {
      return [...moduleMessages[questionType]];
    }
    
    // Fallback to default messages
    const defaultMessages = DEFAULT_MESSAGES[questionType] || DEFAULT_MESSAGES.general;
    return [...defaultMessages];
  }
  
  static getCrossModuleMessages(questionType) {
    if (questionType === 'comprehensive-analysis') {
      return [...CROSS_MODULE_MESSAGES['comprehensive-analysis']];
    }
    
    if (questionType === 'comparison') {
      return [...CROSS_MODULE_MESSAGES['module-comparison']];
    }
    
    if (questionType === 'analysis') {
      return [...CROSS_MODULE_MESSAGES['correlation-analysis']];
    }
    
    // Default cross-module messages
    return [...CROSS_MODULE_MESSAGES['comprehensive-analysis']];
  }
  
  static addFilterContext(messages, dashboardContext) {
    const { filters, dateRange } = dashboardContext;
    const contextMessages = [];
    
    // Add customer-specific context
    if (filters.customerId) {
      contextMessages.push(...FILTER_CONTEXT_MESSAGES['customer-specific']);
    }
    
    // Add date range context
    if (dateRange.isCustom || filters.startDate || filters.endDate) {
      contextMessages.push(...FILTER_CONTEXT_MESSAGES['date-range']);
    }
    
    // Add custom filter context
    if (Object.keys(filters).length > 2) { // More than just customerId and daysBack
      contextMessages.push(...FILTER_CONTEXT_MESSAGES['custom-filters']);
    }
    
    // Insert context messages at appropriate positions
    if (contextMessages.length > 0) {
      // Insert after first message
      const result = [messages[0]];
      result.push(...contextMessages.slice(0, 1)); // Add one context message
      result.push(...messages.slice(1));
      return result;
    }
    
    return messages;
  }
  
  static adjustForComplexity(messages, complexity) {
    const targetCount = ComplexityAnalyzer.getStepCount(complexity);
    
    if (messages.length === targetCount) {
      return messages;
    }
    
    if (messages.length > targetCount) {
      // Trim messages to target count
      return messages.slice(0, targetCount);
    }
    
    // Add padding messages if needed
    const paddingMessages = [
      "🔄 Processing additional data...",
      "📊 Refining analysis...",
      "🧠 Generating deeper insights...",
      "📈 Optimizing results...",
      "✨ Adding final touches..."
    ];
    
    const result = [...messages];
    const needed = targetCount - messages.length;
    
    for (let i = 0; i < needed && i < paddingMessages.length; i++) {
      // Insert before the last message
      result.splice(-1, 0, paddingMessages[i]);
    }
    
    return result;
  }
  
  static calculateTiming(messages, complexity) {
    const totalDuration = ComplexityAnalyzer.getExpectedDuration(complexity);
    const stepCount = messages.length;
    
    // Calculate timing for each step
    const timings = [];
    let remainingTime = totalDuration;
    
    for (let i = 0; i < stepCount; i++) {
      let stepDuration;
      
      if (i === 0) {
        // First step is usually quick
        stepDuration = Math.min(800, remainingTime * 0.2);
      } else if (i === stepCount - 1) {
        // Last step gets remaining time
        stepDuration = remainingTime;
      } else {
        // Middle steps get equal distribution
        const remainingSteps = stepCount - i;
        stepDuration = remainingTime / remainingSteps;
      }
      
      // Add some randomization for realism (±20%)
      const randomFactor = 0.8 + Math.random() * 0.4;
      stepDuration = Math.max(500, stepDuration * randomFactor);
      
      timings.push(Math.round(stepDuration));
      remainingTime -= stepDuration;
    }
    
    return timings;
  }
  
  static getFallbackMessages() {
    return {
      messages: [
        "🔍 Processing your request...",
        "📊 Analyzing data...",
        "🧠 Generating insights...",
        "✅ Preparing response..."
      ],
      timing: [800, 1200, 1000, 800],
      analysis: {
        questionType: 'general',
        complexity: 'medium'
      },
      complexity: 'medium'
    };
  }
  
  static addCustomerContext(messages, customerId) {
    // Add customer-specific context to messages
    return messages.map(message => {
      if (message.includes('Scanning') || message.includes('Accessing')) {
        return message.replace('...', ` for customer ${customerId}...`);
      }
      return message;
    });
  }
  
  static addTimeContext(messages, timeRange) {
    // Add time range context to messages
    const timeDescription = this.getTimeDescription(timeRange);
    
    return messages.map(message => {
      if (message.includes('Processing') && timeDescription) {
        return message.replace('...', ` (${timeDescription})...`);
      }
      return message;
    });
  }
  
  static getTimeDescription(timeRange) {
    if (timeRange.isCustom && timeRange.start && timeRange.end) {
      const start = new Date(timeRange.start).toLocaleDateString();
      const end = new Date(timeRange.end).toLocaleDateString();
      return `${start} to ${end}`;
    }
    return null;
  }
  
  static previewMessages(userMessage, dashboardContext) {
    // For debugging - preview what messages would be generated
    const result = this.generateMessages(userMessage, dashboardContext);
    
    console.log('Streaming Preview:', {
      userMessage,
      activeModule: dashboardContext.activeModule,
      analysis: result.analysis,
      complexity: result.complexity,
      messages: result.messages,
      timing: result.timing,
      totalDuration: result.timing.reduce((sum, time) => sum + time, 0)
    });
    
    return result;
  }
}
