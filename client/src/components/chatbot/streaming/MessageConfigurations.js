/**
 * Message Configurations for Context-Aware Streaming
 * Module-specific and question-type-specific streaming messages
 */

export const MODULE_MESSAGES = {
  'incident-investigation': {
    'show-data': [
      "🧠 Understanding your incident data request...",
      "🔍 Connecting to incident investigation database...",
      "📊 Querying incident records and severity patterns...",
      "🚨 Processing critical incident classifications...",
      "📈 Calculating incident frequency and trends...",
      "🔄 Cross-referencing with safety protocols...",
      "💡 Applying AI algorithms for pattern recognition...",
      "✅ Compiling comprehensive incident summary..."
    ],
    'create-chart': [
      "🧠 Analyzing your visualization requirements...",
      "📊 Identifying optimal incident metrics for charting...",
      "🎨 Selecting best chart type for incident data...",
      "📉 Processing incident frequency and timeline data...",
      "🖼️ Rendering interactive incident visualizations...",
      "🎯 Optimizing chart readability and insights...",
      "✅ Finalizing incident dashboard with AI insights..."
    ],
    'trend-analysis': [
      "🧠 Processing your trend analysis request...",
      "📈 Analyzing incident patterns across time periods...",
      "🔄 Comparing current vs historical incident rates...",
      "📊 Identifying seasonal and cyclical patterns...",
      "🧮 Applying statistical models for trend prediction...",
      "💡 Generating actionable trend insights...",
      "📋 Preparing comprehensive trend analysis report..."
    ],
    'analysis': [
      "🧠 Initiating deep incident data analysis...",
      "🔍 Scanning for incident correlation patterns...",
      "🧮 Calculating risk factors and probability scores...",
      "⚠️ Identifying high-risk incident categories...",
      "📊 Mapping incident causation relationships...",
      "💡 Generating AI-powered safety recommendations...",
      "📋 Compiling detailed incident analysis report..."
    ],
    'general': [
      "🧠 Processing your incident investigation query...",
      "🔍 Accessing comprehensive incident database...",
      "📊 Analyzing incident data with AI algorithms...",
      "🧮 Calculating safety performance metrics...",
      "💡 Generating intelligent safety insights...",
      "✅ Preparing personalized incident report..."
    ]
  },

  'risk-assessment': {
    'show-data': [
      "⚠️ Scanning risk assessment database...",
      "🎯 Analyzing risk severity levels...",
      "📊 Reviewing mitigation strategies...",
      "🔍 Processing risk categories...",
      "✅ Compiling risk summary..."
    ],
    'create-chart': [
      "📊 Mapping risk distribution...",
      "🎨 Designing risk visualization...",
      "📈 Processing risk probability data...",
      "🖼️ Creating risk assessment charts...",
      "✅ Finalizing risk dashboard..."
    ],
    'analysis': [
      "🧮 Calculating risk probability scores...",
      "⚠️ Analyzing high-priority risks...",
      "📊 Mapping risk distribution...",
      "💡 Generating risk recommendations...",
      "📋 Preparing risk analysis report..."
    ],
    'general': [
      "⚠️ Accessing risk assessments...",
      "📊 Processing risk data...",
      "🧠 Analyzing risk patterns...",
      "✅ Preparing risk insights..."
    ]
  },

  'action-tracking': {
    'show-data': [
      "🧠 Understanding your action tracking request...",
      "📋 Connecting to action management database...",
      "✅ Querying action completion status and timelines...",
      "⏰ Analyzing deadline compliance patterns...",
      "👥 Processing assignee performance metrics...",
      "📊 Calculating action efficiency scores...",
      "💡 Applying AI to identify improvement opportunities...",
      "✅ Compiling comprehensive action summary..."
    ],
    'create-chart': [
      "🧠 Analyzing optimal visualization for action data...",
      "📊 Mapping action progress and completion rates...",
      "🎨 Designing intuitive completion tracking charts...",
      "📈 Processing timeline and milestone data...",
      "🖼️ Creating interactive action tracking visuals...",
      "🎯 Optimizing chart layout for maximum insight...",
      "✅ Finalizing action dashboard with smart analytics..."
    ],
    'trend-analysis': [
      "🧠 Processing action trend analysis request...",
      "📈 Analyzing completion patterns over time...",
      "⏰ Tracking deadline performance trends...",
      "📊 Identifying workflow bottlenecks and delays...",
      "� Applying predictive models for future planning...",
      "💡 Generating efficiency improvement insights...",
      "📋 Preparing actionable trend analysis report..."
    ],
    'general': [
      "🧠 Processing your action tracking query...",
      "� Accessing comprehensive action database...",
      "📊 Analyzing action data with intelligent algorithms...",
      "🧮 Calculating performance and efficiency metrics...",
      "💡 Generating smart action management insights...",
      "✅ Preparing personalized action tracking report..."
    ]
  },

  'driver-safety': {
    'show-data': [
      "🚗 Accessing driver safety records...",
      "✅ Reviewing checklist completions...",
      "🔍 Analyzing vehicle fitness data...",
      "📊 Processing driver compliance metrics...",
      "✅ Compiling safety summary..."
    ],
    'create-chart': [
      "🚗 Mapping driver safety metrics...",
      "📊 Designing compliance charts...",
      "📈 Processing checklist data...",
      "🎨 Creating driver performance visuals...",
      "✅ Finalizing safety dashboard..."
    ],
    'analysis': [
      "🧮 Analyzing driver performance...",
      "🚗 Evaluating vehicle fitness trends...",
      "📊 Identifying compliance gaps...",
      "💡 Generating safety recommendations...",
      "📋 Preparing driver safety report..."
    ],
    'general': [
      "🚗 Accessing driver records...",
      "📊 Processing safety data...",
      "🧠 Analyzing compliance patterns...",
      "✅ Preparing safety insights..."
    ]
  },

  'observation-tracker': {
    'show-data': [
      "👁️ Scanning observation database...",
      "📊 Analyzing observation categories...",
      "🔍 Reviewing safety observations...",
      "📈 Processing observation trends...",
      "✅ Compiling observation summary..."
    ],
    'create-chart': [
      "📊 Mapping observation data...",
      "🎨 Designing observation charts...",
      "📈 Processing category distributions...",
      "🖼️ Creating observation visuals...",
      "✅ Finalizing observation dashboard..."
    ],
    'analysis': [
      "🧮 Analyzing observation patterns...",
      "👁️ Identifying recurring issues...",
      "📊 Evaluating observation effectiveness...",
      "💡 Generating improvement suggestions...",
      "📋 Preparing observation analysis..."
    ],
    'general': [
      "👁️ Accessing observations...",
      "📊 Processing observation data...",
      "🧠 Analyzing safety patterns...",
      "✅ Preparing observation insights..."
    ]
  },

  'equipment-asset': {
    'show-data': [
      "🔧 Scanning equipment database...",
      "📊 Analyzing asset conditions...",
      "🔍 Reviewing maintenance schedules...",
      "📈 Processing calibration data...",
      "✅ Compiling equipment summary..."
    ],
    'create-chart': [
      "📊 Mapping equipment metrics...",
      "🎨 Designing asset charts...",
      "📈 Processing maintenance data...",
      "🖼️ Creating equipment visuals...",
      "✅ Finalizing asset dashboard..."
    ],
    'analysis': [
      "🧮 Analyzing equipment performance...",
      "🔧 Evaluating maintenance effectiveness...",
      "📊 Identifying asset risks...",
      "💡 Generating maintenance recommendations...",
      "📋 Preparing equipment analysis..."
    ],
    'general': [
      "🔧 Accessing equipment records...",
      "📊 Processing asset data...",
      "🧠 Analyzing maintenance patterns...",
      "✅ Preparing equipment insights..."
    ]
  },

  'employee-training': {
    'show-data': [
      "🎓 Scanning training database...",
      "📊 Analyzing completion rates...",
      "🔍 Reviewing certification status...",
      "📈 Processing training metrics...",
      "✅ Compiling training summary..."
    ],
    'create-chart': [
      "📊 Mapping training progress...",
      "🎨 Designing certification charts...",
      "📈 Processing completion data...",
      "🖼️ Creating training visuals...",
      "✅ Finalizing training dashboard..."
    ],
    'analysis': [
      "🧮 Analyzing training effectiveness...",
      "🎓 Evaluating skill development...",
      "📊 Identifying training gaps...",
      "💡 Generating development recommendations...",
      "📋 Preparing training analysis..."
    ],
    'general': [
      "🎓 Accessing training records...",
      "📊 Processing education data...",
      "🧠 Analyzing learning patterns...",
      "✅ Preparing training insights..."
    ]
  },

  'global-dashboard': {
    'show-data': [
      "🌐 Scanning all safety modules...",
      "📊 Aggregating cross-module data...",
      "🔍 Analyzing comprehensive metrics...",
      "📈 Processing global KPIs...",
      "✅ Compiling dashboard overview..."
    ],
    'create-chart': [
      "📊 Mapping global safety metrics...",
      "🎨 Designing comprehensive charts...",
      "📈 Processing multi-module data...",
      "🖼️ Creating dashboard visuals...",
      "✅ Finalizing global dashboard..."
    ],
    'analysis': [
      "🧮 Performing comprehensive analysis...",
      "🌐 Cross-referencing all modules...",
      "📊 Identifying system-wide patterns...",
      "💡 Generating holistic recommendations...",
      "📋 Preparing comprehensive report..."
    ],
    'general': [
      "🌐 Accessing all safety data...",
      "📊 Processing global metrics...",
      "🧠 Analyzing system patterns...",
      "✅ Preparing comprehensive insights..."
    ]
  }
};

export const CROSS_MODULE_MESSAGES = {
  'comprehensive-analysis': [
    "🔍 Scanning all safety modules...",
    "📊 Cross-referencing incident and risk data...",
    "🧮 Analyzing inter-module correlations...",
    "📈 Processing comprehensive metrics...",
    "🧠 Generating holistic insights...",
    "📋 Compiling comprehensive report..."
  ],
  'module-comparison': [
    "⚖️ Comparing module performance...",
    "📊 Analyzing cross-module trends...",
    "🔄 Processing comparative metrics...",
    "📈 Identifying performance gaps...",
    "💡 Generating comparison insights...",
    "✅ Finalizing comparative analysis..."
  ],
  'correlation-analysis': [
    "🔗 Identifying data correlations...",
    "📊 Mapping inter-module relationships...",
    "🧮 Calculating correlation coefficients...",
    "📈 Analyzing causal relationships...",
    "🧠 Generating correlation insights...",
    "📋 Preparing relationship analysis..."
  ]
};

export const DEFAULT_MESSAGES = {
  'show-data': [
    "🔍 Accessing safety database...",
    "📊 Processing requested data...",
    "🧠 Analyzing information...",
    "✅ Preparing response..."
  ],
  'create-chart': [
    "📊 Identifying relevant metrics...",
    "🎨 Designing visualization...",
    "📈 Processing data points...",
    "🖼️ Rendering chart...",
    "✅ Finalizing visualization..."
  ],
  'analysis': [
    "🧮 Performing data analysis...",
    "📊 Identifying patterns...",
    "💡 Generating insights...",
    "📋 Preparing analysis report..."
  ],
  'general': [
    "🔍 Processing your request...",
    "📊 Analyzing data...",
    "🧠 Generating insights...",
    "✅ Preparing response..."
  ]
};

export const FILTER_CONTEXT_MESSAGES = {
  'customer-specific': [
    "🏢 Filtering for specific customer...",
    "📊 Processing customer-specific data...",
    "🔍 Analyzing customer metrics..."
  ],
  'date-range': [
    "📅 Applying date range filter...",
    "⏰ Processing time-specific data...",
    "📈 Analyzing temporal patterns..."
  ],
  'custom-filters': [
    "🎯 Applying custom filters...",
    "📊 Processing filtered dataset...",
    "🔍 Analyzing targeted metrics..."
  ]
};
