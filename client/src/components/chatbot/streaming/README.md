# Context-Aware Streaming System

This directory contains the implementation of the context-aware streaming system that provides intelligent, module-specific thinking messages for the SafetyConnect AI chatbot.

## 🎯 Features

- **Context-Aware Messages**: Different messages based on current dashboard module
- **Question Type Detection**: Analyzes user questions to show relevant processing steps
- **Complexity Analysis**: Adjusts streaming duration based on question complexity
- **Realistic Timing**: Natural timing patterns that feel authentic
- **Visual Animations**: Smooth animations with progress indicators

## 📁 File Structure

```
streaming/
├── StreamingThinkingIndicator.js    # Main streaming component
├── StreamingMessageRenderer.js      # UI rendering with animations
├── ContextAwareStreaming.js         # Core streaming engine
├── QuestionAnalyzer.js             # Question intent detection
├── MessageConfigurations.js        # Module-specific messages
└── StreamingMessageRenderer.css    # Animations and styles
```

## 🚀 Usage

### Basic Usage

```jsx
import StreamingThinkingIndicator from './streaming/StreamingThinkingIndicator';
import { DashboardContextProvider } from '../../../contexts/DashboardContext';

// Wrap your app with context provider
<DashboardContextProvider>
  <YourApp />
</DashboardContextProvider>

// Use the streaming indicator
<StreamingThinkingIndicator
  userMessage="Show me recent incidents"
  onComplete={(result) => console.log('Streaming complete:', result)}
  isVisible={true}
/>
```

### Integration with ChatBot

The streaming system is already integrated into the ChatBot component. It automatically:

1. Detects the current dashboard module
2. Analyzes the user's question
3. Shows appropriate streaming messages
4. Completes when the API response arrives

## 🧠 How It Works

### 1. Context Detection
- Reads current dashboard module from context
- Detects applied filters and date ranges
- Considers query history for follow-up questions

### 2. Question Analysis
- Parses user message for intent (show-data, create-chart, analysis, etc.)
- Detects mentioned modules
- Identifies complexity level

### 3. Message Generation
- Selects appropriate messages for the module and question type
- Adjusts message count based on complexity
- Adds filter-specific context messages

### 4. Timing Calculation
- Calculates realistic timing for each step
- Adds randomization for natural feel
- Ensures minimum and maximum durations

## 📊 Module-Specific Messages

Each safety module has its own set of messages:

### Incident Investigation
- "🔍 Scanning incident database..."
- "📊 Analyzing incident severity patterns..."
- "🚨 Reviewing critical incidents..."

### Driver Safety
- "🚗 Accessing driver safety records..."
- "✅ Reviewing checklist completions..."
- "🔍 Analyzing vehicle fitness data..."

### Risk Assessment
- "⚠️ Scanning risk assessment database..."
- "🎯 Analyzing risk severity levels..."
- "📊 Reviewing mitigation strategies..."

## 🎨 Customization

### Adding New Modules

1. Add module messages to `MessageConfigurations.js`:
```javascript
'your-module': {
  'show-data': [
    "🔍 Your custom message...",
    "📊 Another step...",
    "✅ Final step..."
  ]
}
```

2. Add module keywords to `messagePatterns.js`:
```javascript
'your-module': [
  /your-keyword/i,
  /another-keyword/i
]
```

### Adding New Question Types

1. Add patterns to `messagePatterns.js`:
```javascript
'your-question-type': [
  /your-pattern/i,
  /another-pattern/i
]
```

2. Add messages to `MessageConfigurations.js` for each module.

## 🧪 Testing

Visit `/test-streaming` to test the streaming system with different:
- Dashboard modules
- Question types
- Filter configurations
- Message complexities

## 🎯 Best Practices

1. **Keep messages concise** - Users scan quickly
2. **Use relevant emojis** - Visual cues help understanding
3. **Match module context** - Messages should feel specific to the domain
4. **Vary timing** - Avoid mechanical feeling
5. **Test thoroughly** - Different combinations of context

## 🔧 Configuration

The system can be configured through:

- **Complexity thresholds** in `complexityAnalyzer.js`
- **Timing patterns** in `timingCalculator.js`
- **Message templates** in `MessageConfigurations.js`
- **Detection patterns** in `messagePatterns.js`

## 📈 Performance

- **Lightweight**: No heavy computations during streaming
- **Efficient**: Messages generated once and cached
- **Responsive**: Adapts to actual API response times
- **Accessible**: Supports reduced motion preferences
