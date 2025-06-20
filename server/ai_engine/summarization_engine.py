"""
AI Summarization Engine for SafetyConnect
Provides detailed AI-powered analysis and summarization for safety modules using OpenAI
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass

try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False
    OpenAI = None

# Check if tiktoken is available for accurate token counting
try:
    import tiktoken
    tiktoken_available = True
except ImportError:
    tiktoken_available = False

from .cache_manager import cached_ai_response, ai_cache

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ModuleAnalysis:
    """Data class for module analysis results"""
    module_name: str
    summary: str
    key_insights: List[str]
    recommendations: List[str]
    risk_level: str
    data_quality: str
    timestamp: datetime

class SafetySummarizationEngine:
    """
    AI-powered summarization engine for safety modules
    Generates detailed bullet-point summaries using OpenAI
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI summarization engine
        
        Args:
            api_key: OpenAI API key (if not provided, will use environment variable)
        """
        self.openai_client = None
        
        # Initialize OpenAI client with high-performance settings
        if openai_available:
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if api_key:
                import httpx
                # Configure timeout settings optimized for large context models
                self.openai_client = OpenAI(
                    api_key=api_key,
                    timeout=httpx.Timeout(90.0, read=60.0, write=10.0, connect=5.0),  # Longer timeouts for large models
                    max_retries=2  # Allow retries for large context processing
                )
                logger.info("SafetySummarizationEngine: OpenAI client initialized with high-performance settings")
            else:
                logger.warning("SafetySummarizationEngine: OpenAI API key not found")
        else:
            logger.warning("SafetySummarizationEngine: OpenAI not available")
        
        # Module configuration
        self.module_configs = {
            "incident_investigation": {
                "name": "Incident Investigation",
                "focus_areas": ["incident_trends", "investigation_efficiency", "safety_performance", "action_creation"],
                "risk_indicators": ["open_incidents", "investigation_time", "injury_count", "unsafe_locations"]
            },
            "action_tracking": {
                "name": "Action Tracking",
                "focus_areas": ["completion_rates", "overdue_actions", "employee_performance", "action_effectiveness"],
                "risk_indicators": ["overdue_percentage", "incomplete_actions", "recurring_issues"]
            },
            "driver_safety_checklists": {
                "name": "Driver Safety Checklists",
                "focus_areas": ["compliance_rates", "vehicle_fitness", "driver_behavior", "safety_protocols"],
                "risk_indicators": ["unfit_vehicles", "incomplete_checklists", "overdue_inspections"]
            },
            "observation_tracker": {
                "name": "Observation Tracker",
                "focus_areas": ["observation_trends", "safety_concerns", "area_risks", "behavioral_patterns"],
                "risk_indicators": ["high_priority_observations", "recurring_issues", "unsafe_areas"]
            },
            "equipment_asset_management": {
                "name": "Equipment Asset Management",
                "focus_areas": ["calibration_compliance", "inspection_completion", "equipment_condition", "maintenance_schedules"],
                "risk_indicators": ["expired_calibrations", "overdue_inspections", "equipment_anomalies", "missing_certificates"]
            },
            "employee_training_fitness": {
                "name": "Employee Training & Fitness",
                "focus_areas": ["training_compliance", "certification_status", "medical_fitness", "competency_management"],
                "risk_indicators": ["expired_trainings", "unfit_employees", "missing_certifications", "overdue_renewals"]
            },
            "risk_assessment": {
                "name": "Risk Assessment",
                "focus_areas": ["risk_identification", "severity_analysis", "likelihood_assessment", "control_effectiveness"],
                "risk_indicators": ["high_residual_risk", "inadequate_controls", "common_hazards", "measure_effectiveness"]
            }
        }

        # Model preferences and context limits - optimized for speed based on token count
        self.model_context_limits = {
            "gpt-3.5-turbo": 16384,     # Fastest model - prioritize for speed under 16k tokens
            "gpt-3.5-turbo-1106": 16384, # Latest fast model
            "gpt-3.5-turbo-16k": 16384, # Fast model with larger context
            "gpt-4o-mini": 128000,      # Backup - slower but more capable
            "gpt-4o": 128000,           # Fallback - slowest but most capable
            "gpt-4-turbo-preview": 128000,  # Legacy fallback
            "gpt-4": 8192,              # Legacy fallback
        }

        # Token threshold for model selection (16,000 tokens)
        self.token_threshold = 16000

        # Speed-optimized models for requests under 16k tokens
        self.fast_models = [
            "gpt-3.5-turbo",           # Fastest model for small requests
            "gpt-3.5-turbo-1106",      # Latest fast model
            "gpt-3.5-turbo-16k",       # Fast model with larger context
        ]

        # Large context models for requests over 16k tokens
        self.large_context_models = [
            "gpt-4o",                  # Latest large context model (128k tokens)
            "gpt-4o-mini",             # Fast large context model (128k tokens)
            "gpt-4-turbo-preview",     # Large context model (128k tokens)
        ]

        # Initialize tiktoken encoder for accurate token counting
        self.tiktoken_encoder = None
        if tiktoken_available:
            try:
                self.tiktoken_encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
                logger.info("Tiktoken encoder initialized for accurate token counting")
            except Exception as e:
                logger.warning(f"Failed to initialize tiktoken encoder: {e}")
                self.tiktoken_encoder = None
    
    @cached_ai_response("module_analysis", ttl_seconds=3600)  # 1 hour cache for better performance
    def generate_module_specific_analysis(self, module_data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """
        Generate comprehensive AI analysis for a specific safety module
        
        Args:
            module_data: The KPI data for the module
            module: Module identifier (incident_investigation, action_tracking, etc.)
            
        Returns:
            Dict containing detailed analysis with bullet points
        """
        if not self.openai_client:
            return self._generate_fallback_analysis(module_data, module)
        
        try:
            logger.info(f"Starting AI analysis for {module} module")
            
            # Get module configuration
            config = self.module_configs.get(module, {})
            module_name = config.get("name", module.replace("_", " ").title())
            
            # Prepare data for analysis
            analysis_data = self._prepare_module_data(module_data, module)
            
            # Generate AI analysis
            logger.info(f"Making OpenAI API call for {module} module analysis")
            analysis_result = self._call_openai_for_analysis(analysis_data, module, config)
            
            if analysis_result:
                logger.info(f"AI analysis completed for {module} with {len(analysis_result.get('key_insights', []))} insights")
                return analysis_result
            else:
                logger.warning(f"AI analysis failed for {module}, using fallback")
                return self._generate_fallback_analysis(module_data, module)
                
        except Exception as e:
            logger.error(f"Error in AI analysis for {module}: {str(e)}")
            return self._generate_fallback_analysis(module_data, module)
    
    def _prepare_module_data(self, module_data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """Prepare and clean module data for AI analysis"""
        try:
            # Remove None values and clean data
            cleaned_data = {}
            for key, value in module_data.items():
                if value is not None:
                    if isinstance(value, dict):
                        # Clean nested dictionaries and limit size
                        cleaned_value = {k: v for k, v in value.items() if v is not None}
                        if cleaned_value:
                            # Limit nested dict size to prevent token overflow
                            if len(cleaned_value) > 20:
                                # Keep only the most important items
                                sorted_items = sorted(cleaned_value.items(), key=lambda x: str(x[1]), reverse=True)
                                cleaned_value = dict(sorted_items[:20])
                            cleaned_data[key] = cleaned_value
                    elif isinstance(value, list) and value:
                        # Limit list size to prevent token overflow
                        if len(value) > 50:
                            cleaned_data[key] = value[:50]  # Take first 50 items
                        else:
                            cleaned_data[key] = value
                    elif not isinstance(value, (dict, list)):
                        cleaned_data[key] = value

            # Truncate data if it's too large
            cleaned_data = self._truncate_large_data(cleaned_data)

            # Add metadata
            analysis_data = {
                "module": module,
                "module_name": self.module_configs.get(module, {}).get("name", module),
                "data": cleaned_data,
                "analysis_timestamp": datetime.now().isoformat(),
                "data_points_count": len(cleaned_data)
            }

            return analysis_data

        except Exception as e:
            logger.error(f"Error preparing module data: {str(e)}")
            return {"module": module, "data": module_data, "error": str(e)}

    def _truncate_large_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Truncate data if it's too large to prevent token overflow"""
        try:
            # Estimate token count (rough approximation: 1 token ≈ 4 characters)
            data_str = json.dumps(data, default=str)
            estimated_tokens = len(data_str) // 4

            # If estimated tokens > 3000, truncate the data
            if estimated_tokens > 3000:
                logger.warning(f"Data too large ({estimated_tokens} estimated tokens), truncating...")

                # Keep only the most important keys
                important_keys = [
                    'total', 'count', 'rate', 'percentage', 'average', 'mean',
                    'incidents', 'actions', 'observations', 'checklists',
                    'open', 'closed', 'completed', 'overdue', 'pending'
                ]

                truncated_data = {}
                for key, value in data.items():
                    # Always keep important keys
                    if any(important_key in key.lower() for important_key in important_keys):
                        truncated_data[key] = value
                    # For other keys, only keep if we haven't reached limit
                    elif len(truncated_data) < 15:
                        if isinstance(value, dict) and len(value) > 10:
                            # Truncate large nested dicts
                            truncated_data[key] = dict(list(value.items())[:10])
                        elif isinstance(value, list) and len(value) > 20:
                            # Truncate large lists
                            truncated_data[key] = value[:20]
                        else:
                            truncated_data[key] = value

                return truncated_data

            return data

        except Exception as e:
            logger.error(f"Error truncating data: {str(e)}")
            return data
    
    def _call_openai_for_analysis(self, analysis_data: Dict[str, Any], module: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make OpenAI API call for module analysis"""
        try:
            # Create specialized prompt for the module
            prompt = self._create_analysis_prompt(analysis_data, module, config)

            # Select optimal model based on prompt size and 16k token threshold
            optimal_model = self._select_optimal_model(prompt)

            # Get prioritized list of models to try
            models_to_try = self._get_models_to_try(optimal_model)

            for model in models_to_try:
                try:
                    response = self.openai_client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a safety management expert. Provide concise, actionable insights in JSON format."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        max_tokens=2000,  # Increased for more detailed analysis with large context models
                        temperature=0.1   # Very low temperature for focused responses
                    )
                    logger.info(f"Successfully used model: {model}")
                    break
                except Exception as model_error:
                    logger.warning(f"Model {model} failed: {str(model_error)}")
                    if model == models_to_try[-1]:  # Last model
                        raise model_error
                    continue
            
            ai_response = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                # Extract JSON from response
                start_idx = ai_response.find('{')
                end_idx = ai_response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = ai_response[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    # Add metadata
                    result["ai_generated"] = True
                    result["analysis_timestamp"] = datetime.now().isoformat()
                    result["module"] = module
                    
                    return result
                else:
                    logger.error("No valid JSON found in AI response")
                    return None
                    
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing AI response JSON: {str(e)}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return None
    
    def _generate_fallback_analysis(self, module_data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """Generate fallback analysis when AI is not available"""
        config = self.module_configs.get(module, {})
        module_name = config.get("name", module.replace("_", " ").title())

        return {
            "module": module,
            "module_name": module_name,
            "summary": f"Basic analysis for {module_name} module. AI analysis unavailable.",
            "risk_level": "Unknown",
            "insights": [
                {"text": f"Current status: Data collected for {len(module_data)} metrics", "sentiment": "neutral"},
                {"text": "Current capability: Basic data collection operational", "sentiment": "positive"},
                {"text": "Current limitation: Detailed AI analysis requires OpenAI API access", "sentiment": "negative"},
                {"text": "Current state: Manual review required for comprehensive insights", "sentiment": "negative"},
                {"text": "Current data quality: Available but unprocessed", "sentiment": "neutral"},
                {"text": "Current monitoring: Basic metrics tracking active", "sentiment": "positive"},
                {"text": "Current analysis depth: Limited without AI capabilities", "sentiment": "negative"},
                {"text": "Current operational status: Data systems functioning", "sentiment": "positive"},
                {"text": "Enable AI analysis for detailed insights", "sentiment": "neutral"},
                {"text": "Configure automated AI-powered reporting", "sentiment": "neutral"}
            ],
            "ai_generated": False,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def _create_analysis_prompt(self, analysis_data: Dict[str, Any], module: str, config: Dict[str, Any]) -> str:
        """Create specialized analysis prompt for each module"""
        module_name = config.get("name", module)
        focus_areas = config.get("focus_areas", [])
        risk_indicators = config.get("risk_indicators", [])

        prompt = f"""
Analyze the following {module_name} safety data and provide actionable insights in JSON format.

MODULE DATA:
{json.dumps(analysis_data, indent=2, default=str)}

ANALYSIS REQUIREMENTS:
1. Focus on these key areas: {', '.join(focus_areas)}
2. Pay special attention to these risk indicators: {', '.join(risk_indicators)}
3. Provide specific, actionable insights with clear data points

REQUIRED JSON OUTPUT FORMAT:
{{
    "summary": "Brief 2-3 sentence summary of current safety status",
    "risk_level": "Low|Medium|High|Critical",
    "insights": [
        {{
            "text": "Current incident rate is 15 per month, down 20% from last quarter",
            "sentiment": "positive"
        }},
        {{
            "text": "Driver safety compliance stands at 87.5%, exceeding industry standard",
            "sentiment": "positive"
        }},
        {{
            "text": "Action tracking completion rate is 78.2%, indicating room for improvement",
            "sentiment": "negative"
        }},
        {{
            "text": "Equipment failure accounts for 53% of incidents, requiring attention",
            "sentiment": "negative"
        }},
        {{
            "text": "Factory floor shows highest incident concentration at 67% of total",
            "sentiment": "negative"
        }},
        {{
            "text": "Response time averages 2.3 hours, meeting target of under 3 hours",
            "sentiment": "positive"
        }},
        {{
            "text": "Training completion rate is 92%, with 8% pending certification",
            "sentiment": "positive"
        }},
        {{
            "text": "Safety observations increased 15% this month compared to last",
            "sentiment": "positive"
        }},
        {{
            "text": "Recommend focusing on equipment maintenance protocols",
            "sentiment": "neutral"
        }},
        {{
            "text": "Priority action: Review factory floor safety procedures",
            "sentiment": "neutral"
        }}
    ]
}}

ANALYSIS GUIDELINES:
- Generate exactly 10 simple, clear bullet points with sentiment classification
- Use plain language without complex formatting
- Include specific numbers and percentages where available
- Focus on current status and key findings
- Keep each point concise and easy to understand
- Include 8 current state observations and 2 recommendations
- Avoid technical jargon and complex analysis
- Make insights actionable and practical
- Use simple sentence structure
- Focus on what matters most for safety management

SENTIMENT CLASSIFICATION RULES:
- "positive": Good performance, improvements, achievements, meeting targets, exceeding standards
- "negative": Problems, failures, below targets, risks, incidents, areas needing attention
- "neutral": Recommendations, actions, general observations without clear positive/negative impact

Respond ONLY with the JSON object, no additional text.
"""
        return prompt

    def generate_comprehensive_summary(self, all_modules_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive summary across all safety modules

        Args:
            all_modules_data: Dictionary containing data from all modules

        Returns:
            Comprehensive cross-module analysis
        """
        if not self.openai_client:
            return self._generate_fallback_comprehensive_summary(all_modules_data)

        try:
            logger.info("Generating comprehensive cross-module safety analysis")

            # Prepare comprehensive data
            comprehensive_data = {
                "analysis_timestamp": datetime.now().isoformat(),
                "modules_analyzed": list(all_modules_data.keys()),
                "total_modules": len(all_modules_data),
                "module_data": all_modules_data
            }

            # Create comprehensive analysis prompt
            prompt = self._create_comprehensive_prompt(comprehensive_data)

            # Select optimal model based on prompt size and 16k token threshold
            optimal_model = self._select_optimal_model(prompt)

            # Get prioritized list of models to try
            models_to_try = self._get_models_to_try(optimal_model)

            for model in models_to_try:
                try:
                    response = self.openai_client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a safety consultant. Provide concise executive-level safety analysis in JSON format."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        max_tokens=3000,  # Increased for comprehensive analysis with large context models
                        temperature=0.1   # Very low for focused response
                    )
                    logger.info(f"Comprehensive analysis successfully used model: {model}")
                    break
                except Exception as model_error:
                    logger.warning(f"Comprehensive analysis model {model} failed: {str(model_error)}")
                    if model == models_to_try[-1]:  # Last model
                        raise model_error
                    continue

            ai_response = response.choices[0].message.content.strip()

            # Parse JSON response
            try:
                start_idx = ai_response.find('{')
                end_idx = ai_response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = ai_response[start_idx:end_idx]
                    result = json.loads(json_str)

                    # Add metadata
                    result["ai_generated"] = True
                    result["analysis_timestamp"] = datetime.now().isoformat()
                    result["modules_count"] = len(all_modules_data)

                    logger.info("Comprehensive safety analysis completed successfully")
                    return result
                else:
                    logger.error("No valid JSON found in comprehensive analysis response")
                    return self._generate_fallback_comprehensive_summary(all_modules_data)

            except json.JSONDecodeError as e:
                logger.error(f"Error parsing comprehensive analysis JSON: {str(e)}")
                return self._generate_fallback_comprehensive_summary(all_modules_data)

        except Exception as e:
            logger.error(f"Error generating comprehensive analysis: {str(e)}")
            return self._generate_fallback_comprehensive_summary(all_modules_data)

    def _create_comprehensive_prompt(self, comprehensive_data: Dict[str, Any]) -> str:
        """Create prompt for comprehensive cross-module analysis"""
        modules = comprehensive_data.get("modules_analyzed", [])

        # Create a more concise summary of the data to avoid token limits
        data_summary = self._create_data_summary(comprehensive_data.get("module_data", {}))

        prompt = f"""
Analyze the SPECIFIC SAFETY DATA provided below and generate insights based on the ACTUAL NUMBERS and METRICS shown.

DATA TO ANALYZE:
{data_summary}

MODULES ANALYZED: {', '.join(modules)}

REQUIRED JSON OUTPUT FORMAT:
{{
    "summary": "2-3 sentence summary based on the actual data values provided",
    "risk_level": "Low|Medium|High|Critical",
    "insights": [
        {{
            "text": "With [X] incidents reported and [Y] days since last incident, [specific analysis with numbers]",
            "sentiment": "positive|negative|neutral"
        }},
        {{
            "text": "Action tracking shows [X]% completion rate with [Y] open and [Z] closed actions, indicating [analysis]",
            "sentiment": "positive|negative|neutral"
        }},
        {{
            "text": "Employee training shows [X]% expired trainings affecting [Y] employees out of [Z] total staff",
            "sentiment": "positive|negative|neutral"
        }},
        {{
            "text": "Equipment calibration at [X]% with [Y] valid certificates represents [analysis with comparison]",
            "sentiment": "positive|negative|neutral"
        }},
        {{
            "text": "Driver safety checklist completion at [X]% compared to [comparison metric] shows [specific gap/strength]",
            "sentiment": "positive|negative|neutral"
        }},
        {{
            "text": "Observation tracker recorded [X] total observations with [top area] having [Y] observations ([Z]% of total)",
            "sentiment": "positive|negative|neutral"
        }},
        {{
            "text": "Risk assessment module shows [X] total assessments with [specific metric analysis]",
            "sentiment": "positive|negative|neutral"
        }},
        {{
            "text": "Cross-module comparison: [Module A] at [X]% vs [Module B] at [Y]% shows [Z] percentage point difference",
            "sentiment": "positive|negative|neutral"
        }},
        {{
            "text": "Performance ranking: [Best module] leads at [X]% while [worst module] trails at [Y]%, indicating [analysis]",
            "sentiment": "positive|negative|neutral"
        }},
        {{
            "text": "Overall safety metrics show [X] total incidents, [Y]% action completion, and [Z]% training compliance",
            "sentiment": "positive|negative|neutral"
        }},
        {{
            "text": "Critical concern: [Specific metric] at [X]% is [comparison] indicating [specific risk/issue]",
            "sentiment": "positive|negative|neutral"
        }},
        {{
            "text": "Business impact: [X] incidents and [Y]% completion rates suggest [specific operational impact]",
            "sentiment": "positive|negative|neutral"
        }},
        {{
            "text": "Recommendation: Focus on [specific area] where [metric] at [X]% needs improvement to reach [target]%",
            "sentiment": "neutral"
        }},
        {{
            "text": "Priority action: Address [worst metric] at [X]% which is [Y] points below acceptable performance",
            "sentiment": "neutral"
        }}
    ]
}}

CRITICAL REQUIREMENTS:
- EVERY SINGLE INSIGHT MUST include specific numbers, percentages, or counts from the data
- ALWAYS start insights with the actual data values: "With X incidents...", "At Y% completion...", "Z employees have..."
- NEVER write generic statements without numbers
- ALWAYS compare actual values when analyzing performance
- ALWAYS calculate and show ratios, percentages, and differences
- ALWAYS reference the exact metric names and their values
- If no numbers are available for a topic, skip that insight entirely

MANDATORY FORMAT FOR EACH INSIGHT:
- Start with actual numbers: "With [X number/percentage]..."
- Include comparisons: "X is higher/lower than Y..."
- Show calculations: "X out of Y total means Z%..."
- Reference specific modules: "In [module name], [specific metric] shows [exact value]..."

EXAMPLE REQUIRED INSIGHTS FORMAT:
✅ GOOD: "With 15 incidents reported and 45 open actions, the incident-to-action ratio of 1:3 indicates significant follow-up workload"
✅ GOOD: "Driver safety completion at 78% lags behind equipment calibration at 92%, showing a 14 percentage point performance gap"
✅ GOOD: "23% of employees (46 out of 200 total) have expired training, representing nearly 1 in 4 staff members"
✅ GOOD: "Observation tracker shows 127 total observations with Manufacturing (45 observations) and Warehouse (32 observations) as top areas"

❌ BAD: "Organizational safety maturity level needs improvement"
❌ BAD: "There are concerns in safety management practices"
❌ BAD: "Training compliance requires attention"

Respond ONLY with the JSON object, no additional text.
"""
        return prompt

    def _create_data_summary(self, module_data: Dict[str, Any]) -> str:
        """Create a detailed summary of module data for AI analysis"""
        try:
            summary_lines = []

            for module, data in module_data.items():
                if not data:
                    continue

                module_name = self.module_configs.get(module, {}).get("name", module)
                summary_lines.append(f"\n{module_name.upper()}:")

                # Extract and organize metrics by importance
                key_metrics = []

                def extract_metrics(data_dict, prefix=""):
                    """Recursively extract numeric metrics"""
                    for key, value in data_dict.items():
                        full_key = f"{prefix}_{key}" if prefix else key

                        if isinstance(value, (int, float)):
                            # Format percentages and counts appropriately
                            if 'percentage' in key.lower() or 'rate' in key.lower():
                                key_metrics.append(f"{full_key}: {value}%")
                            elif 'count' in key.lower() or 'total' in key.lower():
                                key_metrics.append(f"{full_key}: {value} items")
                            else:
                                key_metrics.append(f"{full_key}: {value}")
                        elif isinstance(value, dict) and len(value) <= 8:
                            # Include nested dictionaries with important metrics
                            extract_metrics(value, full_key)
                        elif isinstance(value, str) and value.replace('.', '').isdigit():
                            # Handle string numbers
                            key_metrics.append(f"{full_key}: {value}")

                extract_metrics(data)

                # Prioritize important metrics (incidents, actions, percentages)
                priority_metrics = []
                other_metrics = []

                for metric in key_metrics:
                    if any(keyword in metric.lower() for keyword in
                          ['incident', 'action', 'percentage', 'completion', 'expired', 'unfit', 'open', 'closed']):
                        priority_metrics.append(metric)
                    else:
                        other_metrics.append(metric)

                # Show priority metrics first, then others
                all_metrics = priority_metrics + other_metrics

                if all_metrics:
                    # Group metrics for better readability
                    for i in range(0, len(all_metrics), 4):
                        group = all_metrics[i:i+4]
                        summary_lines.append("  " + " | ".join(group))
                else:
                    summary_lines.append("  No numeric metrics available")

            return "\n".join(summary_lines)

        except Exception as e:
            logger.error(f"Error creating data summary: {str(e)}")
            return "Data summary unavailable due to processing error"

    def _estimate_token_count(self, text: str) -> int:
        """Estimate token count for a given text using tiktoken if available"""
        if self.tiktoken_encoder:
            try:
                # Use tiktoken for accurate token counting
                tokens = self.tiktoken_encoder.encode(text)
                return len(tokens)
            except Exception as e:
                logger.warning(f"Tiktoken encoding failed: {e}, falling back to character estimation")

        # Fallback: More accurate estimation: ~4 characters per token for English text
        return len(text) // 4

    def _select_optimal_model(self, prompt: str) -> str:
        """Select the optimal model based on prompt length and 16k token threshold"""
        estimated_tokens = self._estimate_token_count(prompt)

        # Add buffer for response tokens (2000-2500)
        total_estimated_tokens = estimated_tokens + 2500

        logger.info(f"Estimated tokens: {estimated_tokens}, total with buffer: {total_estimated_tokens}")

        # Use 16k token threshold for model selection
        if total_estimated_tokens <= self.token_threshold:
            # Use fast models for requests under 16k tokens
            for model in self.fast_models:
                if total_estimated_tokens <= self.model_context_limits.get(model, 16384):
                    logger.info(f"Selected fast model {model} for {estimated_tokens} estimated input tokens (under 16k threshold)")
                    return model
        else:
            # Use large context models for requests over 16k tokens
            for model in self.large_context_models:
                if total_estimated_tokens <= self.model_context_limits.get(model, 128000):
                    logger.info(f"Selected large context model {model} for {estimated_tokens} estimated input tokens (over 16k threshold)")
                    return model

        # If all models would exceed context, use the largest context model available
        logger.warning(f"Prompt too large ({estimated_tokens} tokens), using gpt-4o with truncation")
        return "gpt-4o"

    def _get_models_to_try(self, optimal_model: str) -> List[str]:
        """Get prioritized list of models to try based on optimal model selection"""
        if optimal_model in self.fast_models:
            # For fast models, try fast models first, then fallback to large context
            models_to_try = self.fast_models.copy()
            # Add large context models as fallback
            for model in self.large_context_models:
                if model not in models_to_try:
                    models_to_try.append(model)
        else:
            # For large context models, try large context models first
            models_to_try = self.large_context_models.copy()
            # Add fast models as fallback (though they likely won't work for large requests)
            for model in self.fast_models:
                if model not in models_to_try:
                    models_to_try.append(model)

        # Ensure optimal model is first
        if optimal_model and optimal_model not in models_to_try:
            models_to_try.insert(0, optimal_model)
        elif optimal_model and optimal_model in models_to_try:
            models_to_try.remove(optimal_model)
            models_to_try.insert(0, optimal_model)

        return models_to_try

    def _generate_fallback_comprehensive_summary(self, all_modules_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback comprehensive summary when AI is not available"""
        modules = list(all_modules_data.keys())

        return {
            "summary": f"Comprehensive safety analysis across {len(modules)} modules. AI analysis unavailable for detailed insights.",
            "risk_level": "Unknown",
            "insights": [
                {"text": f"Current organizational status: Data collected from {len(modules)} safety modules", "sentiment": "neutral"},
                {"text": "Current data collection: Multiple safety modules actively monitored", "sentiment": "positive"},
                {"text": "Current system status: Data collection systems operational", "sentiment": "positive"},
                {"text": "Current analytical capability: Limited without AI processing", "sentiment": "negative"},
                {"text": "Current cross-module analysis: Requires AI capabilities for correlation", "sentiment": "negative"},
                {"text": "Current data quality: Available but unprocessed across modules", "sentiment": "neutral"},
                {"text": "Current monitoring scope: Basic metrics tracking across all modules", "sentiment": "positive"},
                {"text": "Current operational state: Manual analysis required for detailed insights", "sentiment": "negative"},
                {"text": "Current limitation: Manual analysis may miss critical patterns", "sentiment": "negative"},
                {"text": "Current infrastructure: Systems ready for AI enhancement", "sentiment": "positive"},
                {"text": "Current baseline: Metrics available for future comparison", "sentiment": "positive"},
                {"text": "Current readiness: Prepared for comprehensive AI analysis", "sentiment": "positive"},
                {"text": "Enable AI analysis for strategic cross-module insights", "sentiment": "neutral"},
                {"text": "Configure comprehensive AI-powered organizational analysis", "sentiment": "neutral"}
            ],
            "ai_generated": False,
            "analysis_timestamp": datetime.now().isoformat(),
            "modules_count": len(modules)
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get AI cache statistics"""
        return ai_cache.get_stats()

    def clear_cache(self):
        """Clear AI response cache"""
        ai_cache.clear()
        logger.info("AI response cache cleared")

    def is_ai_available(self) -> bool:
        """Check if AI analysis is available"""
        return self.openai_client is not None

    def get_supported_modules(self) -> List[str]:
        """Get list of supported modules for analysis"""
        return list(self.module_configs.keys())

    def get_module_config(self, module: str) -> Dict[str, Any]:
        """Get configuration for a specific module"""
        return self.module_configs.get(module, {})
