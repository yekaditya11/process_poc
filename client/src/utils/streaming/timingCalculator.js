/**
 * Timing Calculator for Streaming Messages
 * Calculates realistic timing for streaming steps
 */

export class TimingCalculator {
  static calculateStepTiming(messages, totalDuration, complexity) {
    const stepCount = messages.length;
    if (stepCount === 0) return [];

    const timings = [];
    let remainingTime = totalDuration;

    // Define timing patterns based on complexity
    const patterns = {
      'simple': [0.3, 0.4, 0.3], // Quick, medium, quick
      'medium': [0.2, 0.3, 0.3, 0.2], // Gradual build-up
      'complex': [0.15, 0.25, 0.25, 0.2, 0.15], // Even distribution
      'cross-module': [0.1, 0.2, 0.25, 0.25, 0.15, 0.05] // Front-loaded
    };

    const pattern = patterns[complexity] || patterns['medium'];
    
    // If we have more steps than pattern, extend the pattern
    let weights = [...pattern];
    while (weights.length < stepCount) {
      weights.push(0.15); // Default weight for extra steps
    }
    
    // If we have fewer steps than pattern, truncate
    if (weights.length > stepCount) {
      weights = weights.slice(0, stepCount);
    }

    // Normalize weights to sum to 1
    const totalWeight = weights.reduce((sum, weight) => sum + weight, 0);
    const normalizedWeights = weights.map(weight => weight / totalWeight);

    // Calculate timings with some randomization
    for (let i = 0; i < stepCount; i++) {
      let stepDuration = totalDuration * normalizedWeights[i];
      
      // Add randomization (±15%)
      const randomFactor = 0.85 + Math.random() * 0.3;
      stepDuration *= randomFactor;
      
      // Ensure minimum duration
      stepDuration = Math.max(500, stepDuration);
      
      // Ensure we don't exceed remaining time
      if (i === stepCount - 1) {
        stepDuration = Math.max(500, remainingTime);
      } else {
        stepDuration = Math.min(stepDuration, remainingTime - (500 * (stepCount - i - 1)));
      }
      
      timings.push(Math.round(stepDuration));
      remainingTime -= stepDuration;
    }

    return timings;
  }

  static getRealisticTiming(messageType, complexity) {
    // Base durations for different message types (in milliseconds)
    const baseDurations = {
      'scanning': 1200,
      'analyzing': 1800,
      'processing': 1500,
      'generating': 1600,
      'compiling': 1000,
      'finalizing': 800,
      'creating': 1400,
      'reviewing': 1300,
      'calculating': 1700,
      'mapping': 1100
    };

    // Detect message type from content
    const detectType = (message) => {
      const lowerMessage = message.toLowerCase();
      for (const [type, duration] of Object.entries(baseDurations)) {
        if (lowerMessage.includes(type)) {
          return duration;
        }
      }
      return 1200; // Default duration
    };

    // Complexity multipliers
    const complexityMultipliers = {
      'simple': 0.8,
      'medium': 1.0,
      'complex': 1.3,
      'cross-module': 1.5
    };

    const multiplier = complexityMultipliers[complexity] || 1.0;
    
    if (typeof messageType === 'string') {
      // Single message
      return Math.round(detectType(messageType) * multiplier);
    } else if (Array.isArray(messageType)) {
      // Array of messages
      return messageType.map(message => 
        Math.round(detectType(message) * multiplier)
      );
    }

    return 1200; // Fallback
  }

  static addProgressiveDelay(timings) {
    // Add slight progressive delay to make it feel more natural
    return timings.map((timing, index) => {
      const progressiveFactor = 1 + (index * 0.05); // 5% increase per step
      return Math.round(timing * progressiveFactor);
    });
  }

  static adjustForUserExpectation(timings, userMessage) {
    // Adjust timing based on user message complexity
    const messageLength = userMessage.length;
    const wordCount = userMessage.split(' ').length;
    
    let adjustmentFactor = 1.0;
    
    // Longer messages might expect longer processing
    if (wordCount > 20) {
      adjustmentFactor = 1.2;
    } else if (wordCount < 5) {
      adjustmentFactor = 0.8;
    }
    
    // Questions with multiple parts expect longer processing
    const questionMarks = (userMessage.match(/\?/g) || []).length;
    if (questionMarks > 1) {
      adjustmentFactor *= 1.15;
    }
    
    return timings.map(timing => Math.round(timing * adjustmentFactor));
  }

  static ensureMinimumDuration(timings, minTotal = 2000) {
    const currentTotal = timings.reduce((sum, timing) => sum + timing, 0);
    
    if (currentTotal < minTotal) {
      const scaleFactor = minTotal / currentTotal;
      return timings.map(timing => Math.round(timing * scaleFactor));
    }
    
    return timings;
  }

  static ensureMaximumDuration(timings, maxTotal = 8000) {
    const currentTotal = timings.reduce((sum, timing) => sum + timing, 0);
    
    if (currentTotal > maxTotal) {
      const scaleFactor = maxTotal / currentTotal;
      return timings.map(timing => Math.round(timing * scaleFactor));
    }
    
    return timings;
  }

  static optimizeForUX(timings, messages, userMessage, complexity) {
    let optimizedTimings = [...timings];
    
    // Apply realistic timing based on message content
    optimizedTimings = this.getRealisticTiming(messages, complexity);
    
    // Add progressive delay
    optimizedTimings = this.addProgressiveDelay(optimizedTimings);
    
    // Adjust for user expectation
    optimizedTimings = this.adjustForUserExpectation(optimizedTimings, userMessage);
    
    // Ensure reasonable bounds
    optimizedTimings = this.ensureMinimumDuration(optimizedTimings);
    optimizedTimings = this.ensureMaximumDuration(optimizedTimings);
    
    return optimizedTimings;
  }
}
