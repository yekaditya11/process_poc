"""
Conversational AI Engine for SafetyConnect
Provides natural language interaction with safety management data
Updated to work with latest server architecture and data extractors
"""

import json
import logging
import os
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from decimal import Decimal

try:
    from openai import OpenAI
    openai_available = True
    print("✅ OpenAI imported successfully")
except ImportError as e:
    openai_available = False
    OpenAI = None
    print(f"❌ OpenAI import failed: {e}")

# Check if tiktoken is available for accurate token counting
try:
    import tiktoken
    tiktoken_available = True
    print("✅ Tiktoken imported successfully")
except ImportError as e:
    tiktoken_available = False
    print(f"❌ Tiktoken import failed: {e}")

# Import chart generators
try:
    from .plotly_chart_generator import PlotlyChartGenerator
    plotly_available = True
    print("✅ Plotly chart generator imported successfully")
except ImportError as e:
    plotly_available = False
    PlotlyChartGenerator = None
    print(f"❌ Plotly chart generator import failed: {e}")

try:
    from .echarts_chart_generator import EChartsGenerator
    echarts_available = True
    print("✅ ECharts generator imported successfully")
except ImportError as e:
    echarts_available = False
    EChartsGenerator = None
    print(f"❌ ECharts generator import failed: {e}")

# Import cache manager
try:
    from .cache_manager import cached_ai_response, ai_cache
    cache_available = True
except ImportError:
    cache_available = False
    cached_ai_response = None
    ai_cache = None

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal objects and UUIDs"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if hasattr(obj, '__class__') and obj.__class__.__name__ == 'UUID':
            return str(obj)
        # Handle UUID import variations
        try:
            from uuid import UUID
            if isinstance(obj, UUID):
                return str(obj)
        except ImportError:
            pass
        return super(DecimalEncoder, self).default(obj)


def safe_json_dumps(obj, **kwargs):
    """Safe JSON dumps that handles Decimal objects"""
    return json.dumps(obj, cls=DecimalEncoder, **kwargs)

@dataclass
class ConversationContext:
    """Stores conversation context and history"""
    user_id: str
    session_id: str
    conversation_history: List[Dict[str, Any]]
    current_filters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class ChatMessage:
    """Represents a chat message"""
    role: str
    content: str
    timestamp: datetime
    data_context: Optional[Dict[str, Any]] = None
    suggested_actions: Optional[List[str]] = None
    chart_data: Optional[Dict[str, Any]] = None

class ConversationalAI:
    """Conversational AI engine for SafetyConnect"""

    def __init__(self, summarizer_app):
        self.summarizer_app = summarizer_app
        self.conversations: Dict[str, ConversationContext] = {}

        # Initialize OpenAI client with high-performance settings
        self.openai_client = None
        if openai_available:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                import httpx
                # Configure for large context models with appropriate timeouts
                self.openai_client = OpenAI(
                    api_key=api_key,
                    timeout=httpx.Timeout(60.0, read=45.0, write=10.0, connect=5.0),  # Longer timeouts for large models
                    max_retries=2  # Allow retries for large context processing
                )
                logger.info("OpenAI client initialized with high-performance settings")
            else:
                logger.warning("OpenAI API key not found")
        else:
            logger.warning("OpenAI not available")

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

        # Initialize chart generators
        self.plotly_generator = None
        if plotly_available:
            self.plotly_generator = PlotlyChartGenerator()
            logger.info("Plotly chart generator initialized")
        else:
            logger.warning("Plotly not available")

        self.echarts_generator = None
        if echarts_available:
            self.echarts_generator = EChartsGenerator()
            logger.info("ECharts generator initialized")
        else:
            logger.warning("ECharts not available")

        # Enhanced system prompt for safety data
        self.system_prompt = """You are SafetyConnect AI, an expert safety management assistant.
        You help users understand their safety data including incidents, actions, driver safety, and observations.

        Guidelines:
        - Provide clear, actionable insights about safety metrics
        - Use specific numbers and percentages when available
        - Highlight safety concerns and trends
        - Suggest preventive measures when appropriate
        - Be concise but informative
        - Use safety terminology appropriately

        When discussing data:
        - Always mention the time period being analyzed
        - Highlight any concerning trends or patterns
        - Provide context for the numbers (good/bad/average)
        - Suggest follow-up actions when relevant"""

        # System prompt for AI responses
        self.system_prompt = """You are SafetyConnect AI, a safety management assistant.
        You analyze safety data across 7 modules: Incident Investigation, Action Tracking, Driver Safety Checklists, Observation Tracker, Equipment Asset Management, Employee Training, and Risk Assessment.

        CRITICAL INSTRUCTIONS:
        - ONLY use actual data provided in the data context
        - NEVER generate fictional examples or sample data
        - If no data is available, clearly state that no data is available
        - If data shows zero values, report the actual zero values
        - Always be truthful about what the data shows
        - Give CONCISE, DIRECT answers in 1-2 lines maximum
        - Use bullet points for multiple items
        - NO verbose explanations or lengthy descriptions
        - NO phrases like "Based on the data" or "According to the information"
        - Start directly with the key facts and numbers
        - Be professional, data-driven, and actionable
        """

        # Intent keywords for basic classification
        self.keywords = {
            'incidents': ['incident', 'accident', 'injury', 'investigation'],
            'actions': ['action', 'task', 'follow', 'corrective'],
            'driver_safety': ['driver', 'vehicle', 'checklist', 'safety'],
            'observations': ['observation', 'tracker', 'area', 'priority', 'unsafe'],
            'equipment': ['equipment', 'asset', 'calibration', 'inspection', 'maintenance', 'certificate', 'anomaly', 'deviation'],
            'employee_training': ['employee', 'training', 'fitness', 'certification', 'medical', 'expired', 'competency', 'skill', 'course', 'renewal'],
            'risk_assessment': ['risk', 'assessment', 'hazard', 'severity', 'likelihood', 'control', 'measure', 'residual', 'threat']
        }

    def start_conversation(self, user_id: str, session_id: str = None) -> str:
        """Start a new conversation session"""
        if not session_id:
            session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        context = ConversationContext(
            user_id=user_id,
            session_id=session_id,
            conversation_history=[],
            current_filters={'days_back': None, 'modules': ['all']},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.conversations[session_id] = context

        # Add welcome message
        welcome_content = "Hello! I'm your SafetyConnect AI assistant.\n\nWhat would you like to know?"
        welcome_message = self._add_message(session_id, 'assistant', welcome_content)
        welcome_message.suggested_actions = [
            "Show incidents",
            "Show actions",
            "Show driver safety",
            "Show observations",
            "Show equipment assets"
        ]

        return session_id

    def process_message(self, session_id: str, user_message: str) -> ChatMessage:
        """Process user message and generate AI response"""
        try:
            if session_id not in self.conversations:
                # Start new conversation if session doesn't exist
                session_id = self.start_conversation("anonymous", session_id)

            context = self.conversations[session_id]

            # Add user message to history
            self._add_message(session_id, 'user', user_message)

            # Analyze user intent
            intent = self._analyze_intent(user_message)

            # Extract any filters or parameters from message
            extracted_filters = self._extract_filters(user_message)
            if extracted_filters:
                context.current_filters.update(extracted_filters)

            # Generate response based on intent and context
            response = self._generate_response(context, user_message, intent)

            # Add assistant response to history
            assistant_message = self._add_message(session_id, 'assistant', response['content'])
            assistant_message.data_context = response.get('data_context')
            assistant_message.suggested_actions = response.get('suggested_actions')
            assistant_message.chart_data = response.get('chart_data')

            context.updated_at = datetime.now()

            return assistant_message

        except Exception as e:
            logger.error(f"Error processing message '{user_message}': {str(e)}", exc_info=True)
            error_response = ChatMessage(
                role='assistant',
                content="I apologize, but I encountered an error processing your request. Please try again or rephrase your question.",
                timestamp=datetime.now()
            )
            return error_response

    def _analyze_intent(self, message: str) -> str:
        """Enhanced intent analysis using keywords with module-specific routing"""
        message_lower = message.lower()

        # Log the original message for debugging
        logger.info(f"Analyzing intent for message: '{message}'")

        # Extract actual user message if it has module context prefix
        actual_message = message_lower
        module_context = None
        if message_lower.startswith('[module:'):
            # Extract module context and actual message
            end_bracket = message_lower.find(']')
            if end_bracket != -1:
                module_context = message_lower[8:end_bracket].strip()  # Remove '[module:' and get module name
                actual_message = message_lower[end_bracket + 1:].strip()  # Get message after ']'

                logger.info(f"Module context extracted: '{module_context}', actual message: '{actual_message}'")

                # Map module context to intent directly
                module_mapping = {
                    'incident-investigation': 'incident_investigation',
                    'action-tracking': 'action_tracking',
                    'driver-safety': 'driver_safety',
                    'observation-tracker': 'observation_tracker',
                    'equipment-asset': 'equipment_asset',
                    'employee-training': 'employee_training',
                    'risk-assessment': 'risk_assessment'
                }

                if module_context in module_mapping:
                    logger.info(f"Module context detected: {module_context} -> {module_mapping[module_context]}")

                    # ALWAYS prioritize the actual question content over module context
                    # This ensures the AI answers what the user actually asked, not just the current page
                    question_intent = self._detect_intent_from_content(actual_message)
                    logger.info(f"Question content intent: {question_intent}, Module context intent: {module_mapping[module_context]}")

                    if question_intent != 'general_query':
                        logger.info(f"Using question intent '{question_intent}' over module context '{module_context}'")
                        return question_intent
                    else:
                        logger.info(f"Using module context intent '{module_mapping[module_context]}' as fallback")
                        return module_mapping[module_context]

        # Module-specific intent detection with improved keyword matching
        module_keywords = {
            'incident_investigation': [
                'incident', 'investigation', 'accident', 'injury', 'near miss',
                'safety incident', 'incident report', 'incident analysis', 'incident trends',
                'incident types', 'incident severity', 'incident location', 'incident department',
                'location', 'locations', 'where', 'department', 'departments', 'area', 'areas'
            ],
            'risk_assessment': [
                'risk', 'assessment', 'hazard', 'risk analysis', 'risk evaluation',
                'severity', 'likelihood', 'control measures', 'residual risk', 'risk matrix',
                'hazard identification', 'risk mitigation', 'risk register'
            ],
            'action_tracking': [
                'action', 'tracking', 'corrective action', 'preventive action', 'action plan',
                'action items', 'action status', 'action completion', 'action due', 'overdue actions',
                'action assignment', 'action progress', 'follow up'
            ],
            'driver_safety': [
                'driver', 'vehicle', 'checklist', 'driver safety', 'vehicle inspection',
                'pre-trip', 'post-trip', 'vehicle fitness', 'driver compliance', 'vehicle maintenance',
                'driving behavior', 'fleet safety', 'vehicle checklist'
            ],
            'observation_tracker': [
                'observation', 'tracker', 'behavior', 'unsafe behavior', 'safe behavior',
                'observation report', 'behavioral observation', 'safety observation',
                'observation trends', 'observation analysis', 'workplace observation'
            ],
            'equipment_asset': [
                'equipment', 'asset', 'calibration', 'inspection', 'maintenance',
                'equipment management', 'asset management', 'equipment status', 'calibration due',
                'equipment inspection', 'asset tracking', 'equipment compliance'
            ],
            'employee_training': [
                'employee', 'training', 'certification', 'fitness', 'medical fitness',
                'training compliance', 'employee certification', 'training status', 'expired training',
                'training records', 'employee development', 'competency', 'expire', 'expires',
                'expired', 'expiry', 'traning', 'trainig', 'employess', 'employe'
            ]
        }

        # Use the actual message (without module prefix) for keyword matching
        search_message = actual_message

        # Score-based intent detection for better accuracy
        intent_scores = {}
        for module, keywords in module_keywords.items():
            score = sum(1 for keyword in keywords if keyword in search_message)
            if score > 0:
                intent_scores[module] = score

        # Return the intent with the highest score
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            logger.info(f"Intent scores: {intent_scores}, selected: {best_intent}")
            return best_intent

        # Fall back to general intent analysis
        for intent, keywords in self.keywords.items():
            if any(keyword in search_message for keyword in keywords):
                logger.info(f"Fallback intent detected: {intent}")
                return intent

        logger.info("No specific intent detected, using general_query")
        return 'general_query'

    def _detect_intent_from_content(self, message: str) -> str:
        """Detect intent from message content only (used for mismatch detection)"""
        message_lower = message.lower()

        # Module-specific intent detection
        module_keywords = {
            'incident_investigation': [
                'incident', 'investigation', 'accident', 'injury', 'near miss',
                'safety incident', 'incident report', 'incident analysis', 'incident trends',
                'incident types', 'incident severity', 'incident location', 'incident department',
                'location', 'locations', 'where', 'department', 'departments', 'area', 'areas'
            ],
            'risk_assessment': [
                'risk', 'assessment', 'hazard', 'risk analysis', 'risk evaluation',
                'severity', 'likelihood', 'control measures', 'residual risk', 'risk matrix',
                'hazard identification', 'risk mitigation', 'risk register'
            ],
            'action_tracking': [
                'action', 'tracking', 'corrective action', 'preventive action', 'action plan',
                'action items', 'action status', 'action completion', 'action due', 'overdue actions',
                'action assignment', 'action progress', 'follow up'
            ],
            'driver_safety': [
                'driver', 'vehicle', 'checklist', 'driver safety', 'vehicle inspection',
                'pre-trip', 'post-trip', 'vehicle fitness', 'driver compliance', 'vehicle maintenance',
                'driving behavior', 'fleet safety', 'vehicle checklist'
            ],
            'observation_tracker': [
                'observation', 'tracker', 'behavior', 'unsafe behavior', 'safe behavior',
                'observation report', 'behavioral observation', 'safety observation',
                'observation trends', 'observation analysis', 'workplace observation'
            ],
            'equipment_asset': [
                'equipment', 'asset', 'calibration', 'inspection', 'maintenance',
                'equipment management', 'asset management', 'equipment status', 'calibration due',
                'equipment inspection', 'asset tracking', 'equipment compliance'
            ],
            'employee_training': [
                'employee', 'training', 'certification', 'fitness', 'medical fitness',
                'training compliance', 'employee certification', 'training status', 'expired training',
                'training records', 'employee development', 'competency', 'expire', 'expires',
                'expired', 'expiry', 'traning', 'trainig', 'employess', 'employe'
            ]
        }

        # Check for module-specific keywords
        for module, keywords in module_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return module

        return 'general_query'

    def _extract_filters(self, message: str) -> Dict[str, Any]:
        """Extract filters and parameters from user message"""
        filters = {}
        message_lower = message.lower()

        # Extract time periods
        if 'last week' in message_lower or '7 days' in message_lower:
            filters['days_back'] = 7
        elif 'last month' in message_lower or '30 days' in message_lower:
            filters['days_back'] = 30
        elif 'last quarter' in message_lower or '90 days' in message_lower:
            filters['days_back'] = 90
        elif 'last year' in message_lower or '365 days' in message_lower:
            filters['days_back'] = 365

        # Extract specific modules (5 core modules)
        if 'incident' in message_lower or 'investigation' in message_lower:
            filters['modules'] = ['incident']
        elif 'action' in message_lower:
            filters['modules'] = ['action']
        elif 'driver' in message_lower or 'vehicle' in message_lower or 'checklist' in message_lower:
            filters['modules'] = ['driver_safety']
        elif 'observation' in message_lower or 'tracker' in message_lower or 'unsafe' in message_lower:
            filters['modules'] = ['observations']
        elif 'equipment' in message_lower or 'asset' in message_lower or 'calibration' in message_lower or 'inspection' in message_lower:
            filters['modules'] = ['equipment_assets']

        return filters

    def _generate_response(self, context: ConversationContext, user_message: str, intent: str) -> Dict[str, Any]:
        """Generate AI response based on context and intent"""
        try:
            # Clean the user message for better logging
            clean_user_message = user_message
            if clean_user_message.lower().startswith('[module:'):
                end_bracket = clean_user_message.find(']')
                if end_bracket != -1:
                    clean_user_message = clean_user_message[end_bracket + 1:].strip()

            logger.info(f"=== QUESTION-RESPONSE ALIGNMENT TRACKING ===")
            logger.info(f"Original message: '{user_message}'")
            logger.info(f"Clean message: '{clean_user_message}'")
            logger.info(f"Detected intent: {intent}")

            # Get relevant data based on intent and filters
            data_context = self._get_relevant_data(context, intent)
            logger.info(f"Data context keys: {list(data_context.keys()) if data_context else 'None'}")

            # Check if we have meaningful data to work with
            has_meaningful_data = self._has_meaningful_data(data_context)
            logger.info(f"Has meaningful data: {has_meaningful_data}")

            # Validate question-data alignment
            self._validate_question_data_alignment(clean_user_message, intent, data_context)

            # Create conversation prompt
            conversation_prompt = self._build_conversation_prompt(context, user_message, data_context)

            # Generate AI response using OpenAI or fallback
            if self.openai_client and has_meaningful_data:
                logger.info(f"Using OpenAI to generate response for intent: {intent}")
                try:
                    # Truncate conversation prompt if too long to prevent context overflow
                    truncated_prompt = self._truncate_prompt_for_context(conversation_prompt)
                    logger.info(f"Prompt length: {len(truncated_prompt)} characters")

                    # Select optimal model based on prompt size and 16k token threshold
                    optimal_model = self._select_optimal_model(truncated_prompt)

                    response = self.openai_client.chat.completions.create(
                        model=optimal_model,
                        messages=[
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": truncated_prompt}
                        ],
                        max_tokens=1000,  # Increased for more detailed responses
                        temperature=0.1  # Very low temperature for focused response
                    )
                    ai_response = self._clean_ai_response(response.choices[0].message.content.strip())
                    logger.info(f"OpenAI response generated: {ai_response[:100]}...")
                    logger.info(f"=== RESPONSE ALIGNMENT CHECK: Question '{clean_user_message}' -> Response '{ai_response[:50]}...' ===")
                except Exception as e:
                    logger.error(f"Error calling OpenAI: {str(e)}", exc_info=True)
                    logger.info("Falling back to fallback response due to OpenAI error")
                    ai_response = self._generate_fallback_response(user_message, intent, data_context)
            else:
                # Use fallback response when OpenAI is not available OR when there's no meaningful data
                logger.info(f"Using fallback response. OpenAI available: {bool(self.openai_client)}, Has data: {has_meaningful_data}, Intent: {intent}")
                ai_response = self._generate_fallback_response(user_message, intent, data_context)

            # Generate suggested follow-up actions
            suggested_actions = self._generate_suggested_actions(intent, data_context)

            # Generate chart data if applicable
            logger.info("Generating chart data")
            chart_data = self._generate_chart_data(user_message, intent, data_context)
            logger.info(f"Chart data generated: {bool(chart_data)}")
            if chart_data:
                # Check for ECharts structure
                if chart_data.get('type') == 'echarts':
                    has_config = bool(chart_data.get('echarts_config'))
                    has_data = bool(chart_data.get('echarts_config', {}).get('series'))
                    logger.info(f"Chart data structure: type={chart_data.get('type')}, has_config={has_config}, has_data={has_data}")
                else:
                    # Check for other chart structures
                    has_config = bool(chart_data.get('config'))
                    has_data = bool(chart_data.get('data'))
                    logger.info(f"Chart data structure: type={chart_data.get('type')}, has_config={has_config}, has_data={has_data}")

            return {
                'content': ai_response,
                'data_context': data_context,
                'suggested_actions': suggested_actions,
                'chart_data': chart_data
            }

        except Exception as e:
            logger.error(f"Error generating response for '{user_message}': {str(e)}", exc_info=True)
            return {
                'content': "I'm having trouble accessing the data right now. Please try again in a moment.",
                'data_context': {},
                'suggested_actions': [],
                'chart_data': None
            }

    def _get_relevant_data(self, context: ConversationContext, intent: str) -> Dict[str, Any]:
        """Get data based on what user is actually asking about - independent of current module context"""
        try:
            data = {}
            days_back = context.current_filters.get('days_back') or 365  # Ensure days_back is never None

            # Calculate proper date range for extractors
            end_date_obj = datetime.now()
            start_date_obj = end_date_obj - timedelta(days=days_back)

            # Get the actual user message to analyze what they're asking about
            user_message = context.conversation_history[-1]['content'] if context.conversation_history else ""
            user_message_lower = user_message.lower()

            # Clean the message to remove module context prefix if present
            clean_message = user_message_lower
            if clean_message.startswith('[module:'):
                end_bracket = clean_message.find(']')
                if end_bracket != -1:
                    clean_message = clean_message[end_bracket + 1:].strip()

            logger.info(f"Analyzing user message for data needs: '{user_message}' -> clean: '{clean_message}'")
            logger.info(f"Detected intent: {intent}")

            # Use intent-based data fetching for more accurate matching
            # This ensures we fetch exactly what the user is asking about

            # Map intent to data fetching functions
            intent_data_mapping = {
                'incident_investigation': self._fetch_incident_data,
                'equipment_asset': self._fetch_equipment_data,
                'employee_training': self._fetch_training_data,
                'action_tracking': self._fetch_action_data,
                'driver_safety': self._fetch_driver_data,
                'observation_tracker': self._fetch_observation_data,
                'risk_assessment': self._fetch_risk_data
            }

            # Fetch data based on detected intent
            if intent in intent_data_mapping:
                logger.info(f"Fetching data for intent: {intent}")
                module_data = intent_data_mapping[intent](days_back, start_date_obj, end_date_obj)
                if module_data:
                    # Use the correct key for the data
                    data_key = intent.replace('_investigation', '').replace('_tracking', '').replace('_tracker', '').replace('_asset', '_assets')
                    if intent == 'incident_investigation':
                        data_key = 'incidents'
                    elif intent == 'action_tracking':
                        data_key = 'actions'
                    elif intent == 'observation_tracker':
                        data_key = 'observations'
                    elif intent == 'equipment_asset':
                        data_key = 'equipment_assets'

                    data[data_key] = module_data
                    logger.info(f"Successfully fetched {data_key} data")
            else:
                logger.info(f"No specific data fetching for intent: {intent}, providing general guidance")
                data = {
                    'summary': 'I can help you with: Equipment & Assets, Incidents, Employee Training, Actions, Driver Safety, Observations, or Risk Assessments. Please ask about a specific topic.'
                }

            return data

        except Exception as e:
            logger.error(f"Error getting relevant data: {str(e)}")
            return {}

    def _fetch_incident_data(self, days_back, start_date_obj, end_date_obj):
        """Fetch incident investigation data"""
        try:
            return self.summarizer_app.incident_extractor.get_all_incident_kpis(
                customer_id=None,
                start_date=start_date_obj,
                end_date=end_date_obj
            )
        except Exception as e:
            logger.warning(f"Error getting incident data: {str(e)}")
            return None

    def _fetch_equipment_data(self, days_back, start_date_obj, end_date_obj):
        """Fetch equipment asset data"""
        try:
            return self.summarizer_app.equipment_asset_extractor.get_equipment_asset_kpis(
                customer_id=None,
                days_back=days_back
            )
        except Exception as e:
            logger.warning(f"Error getting equipment data: {str(e)}")
            return None

    def _fetch_training_data(self, days_back, start_date_obj, end_date_obj):
        """Fetch employee training data"""
        try:
            return self.summarizer_app.employee_training_extractor.get_employee_training_kpis(
                customer_id=None,
                days_back=days_back
            )
        except Exception as e:
            logger.warning(f"Error getting employee training data: {str(e)}")
            return None

    def _fetch_action_data(self, days_back, start_date_obj, end_date_obj):
        """Fetch action tracking data"""
        try:
            return self.summarizer_app.action_extractor.get_all_action_tracking_kpis(
                customer_id=None,
                start_date=start_date_obj,
                end_date=end_date_obj
            )
        except Exception as e:
            logger.warning(f"Error getting action data: {str(e)}")
            return None

    def _fetch_driver_data(self, days_back, start_date_obj, end_date_obj):
        """Fetch driver safety data"""
        try:
            return self.summarizer_app.driver_safety_extractor.get_driver_safety_checklist_kpis(
                customer_id=None,
                days_back=days_back
            )
        except Exception as e:
            logger.warning(f"Error getting driver safety data: {str(e)}")
            return None

    def _fetch_observation_data(self, days_back, start_date_obj, end_date_obj):
        """Fetch observation tracker data"""
        try:
            return self.summarizer_app.observation_tracker_extractor.get_observation_tracker_kpis(
                customer_id=None,
                days_back=days_back
            )
        except Exception as e:
            logger.warning(f"Error getting observation data: {str(e)}")
            return None

    def _fetch_risk_data(self, days_back, start_date_obj, end_date_obj):
        """Fetch risk assessment data"""
        try:
            return self.summarizer_app.risk_assessment_extractor.get_risk_assessment_kpis(
                customer_id=None,
                days_back=days_back
            )
        except Exception as e:
            logger.warning(f"Error getting risk assessment data: {str(e)}")
            return None

    def _validate_question_data_alignment(self, user_message: str, intent: str, data_context: Dict[str, Any]) -> None:
        """Validate that the data context aligns with the user's question"""
        user_message_lower = user_message.lower()

        # Check for potential mismatches
        question_keywords = {
            'incident': ['incident', 'accident', 'injury', 'investigation'],
            'training': ['training', 'employee', 'certification', 'fitness', 'expired'],
            'equipment': ['equipment', 'asset', 'calibration', 'inspection'],
            'action': ['action', 'tracking', 'corrective', 'preventive'],
            'driver': ['driver', 'vehicle', 'checklist', 'safety'],
            'observation': ['observation', 'behavior', 'unsafe', 'safe'],
            'risk': ['risk', 'assessment', 'hazard', 'severity']
        }

        # Detect what the user is asking about
        user_asking_about = []
        for topic, keywords in question_keywords.items():
            if any(keyword in user_message_lower for keyword in keywords):
                user_asking_about.append(topic)

        # Check what data we have
        data_available = list(data_context.keys()) if data_context else []

        logger.info(f"User asking about: {user_asking_about}")
        logger.info(f"Data available: {data_available}")
        logger.info(f"Intent: {intent}")

        # Log potential mismatches
        if user_asking_about:
            primary_topic = user_asking_about[0]
            expected_data_keys = {
                'incident': ['incidents'],
                'training': ['employee_training'],
                'equipment': ['equipment_assets'],
                'action': ['actions'],
                'driver': ['driver_safety'],
                'observation': ['observations'],
                'risk': ['risk_assessment']
            }

            expected_keys = expected_data_keys.get(primary_topic, [])
            if expected_keys and not any(key in data_available for key in expected_keys):
                logger.warning(f"POTENTIAL MISMATCH: User asking about '{primary_topic}' but no relevant data found. Expected: {expected_keys}, Available: {data_available}")
            else:
                logger.info(f"ALIGNMENT OK: User asking about '{primary_topic}' and relevant data is available")

    def _build_conversation_prompt(self, context: ConversationContext, user_message: str, data_context: Dict[str, Any]) -> str:
        """Build conversation prompt with context and data - improved for better question-answer alignment"""
        # Get recent conversation history
        recent_history = context.conversation_history[-5:] if len(context.conversation_history) > 5 else context.conversation_history

        history_text = ""
        for msg in recent_history:
            history_text += f"{msg['role'].title()}: {msg['content']}\n"

        # Clean the user message to remove module context prefix
        clean_user_message = user_message
        if clean_user_message.lower().startswith('[module:'):
            end_bracket = clean_user_message.find(']')
            if end_bracket != -1:
                clean_user_message = clean_user_message[end_bracket + 1:].strip()

        # Send FULL JSON data to AI instead of just summary
        try:
            # Convert data_context to JSON string for AI using safe serialization
            full_data_json = safe_json_dumps(data_context, indent=2)
        except Exception as e:
            logger.warning(f"Error serializing data context: {e}")
            # Fallback to summary if JSON serialization fails
            full_data_json = self._summarize_data_context(data_context)

        # Enhanced prompt with better question-answer alignment instructions
        prompt = f"""
Recent Context: {history_text[-200:] if history_text else 'New conversation'}

User's Exact Question: {clean_user_message}

Available Data (Full JSON): {full_data_json}

CRITICAL INSTRUCTIONS FOR QUESTION-ANSWER ALIGNMENT:
- Answer EXACTLY what the user asked in their question: "{clean_user_message}"
- If the user asks about incidents, focus ONLY on incident data
- If the user asks about training, focus ONLY on training data
- If the user asks about equipment, focus ONLY on equipment data
- DO NOT provide information about other modules unless specifically asked
- Give a CONCISE, DIRECT answer in 1-2 lines maximum
- Include specific numbers and percentages from the relevant JSON data above
- Use bullet points for multiple items or key facts
- NO verbose explanations or lengthy descriptions
- NO phrases like "Based on the data" or "According to the information"
- Start directly with the key facts and numbers that answer the user's question
- If no relevant data is available for the user's question, clearly state that

Direct Answer to "{clean_user_message}":"""

        return prompt

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

        # Add buffer for response tokens (1000-1500 for conversational responses)
        total_estimated_tokens = estimated_tokens + 1500

        logger.info(f"Conversational AI - Estimated tokens: {estimated_tokens}, total with buffer: {total_estimated_tokens}")

        # Use 16k token threshold for model selection
        if total_estimated_tokens <= self.token_threshold:
            # Use fast models for requests under 16k tokens
            for model in self.fast_models:
                logger.info(f"Selected fast model {model} for {estimated_tokens} estimated input tokens (under 16k threshold)")
                return model
        else:
            # Use large context models for requests over 16k tokens
            for model in self.large_context_models:
                logger.info(f"Selected large context model {model} for {estimated_tokens} estimated input tokens (over 16k threshold)")
                return model

        # Fallback to GPT-4o if no model is suitable
        logger.warning(f"Prompt too large ({estimated_tokens} tokens), using gpt-4o as fallback")
        return "gpt-4o"

    def _truncate_prompt_for_context(self, prompt: str, max_tokens: int = 12000) -> str:
        """Truncate prompt to prevent OpenAI context length exceeded errors"""
        try:
            # Rough estimation: 1 token ≈ 4 characters
            max_chars = max_tokens * 4

            if len(prompt) <= max_chars:
                return prompt

            logger.warning(f"Prompt too long ({len(prompt)} chars), truncating to {max_chars} chars")

            # Try to truncate intelligently by keeping the user question and recent context
            lines = prompt.split('\n')

            # Find the user message line
            user_message_idx = -1
            for i, line in enumerate(lines):
                if line.startswith('User Message:'):
                    user_message_idx = i
                    break

            if user_message_idx >= 0:
                # Keep everything from user message onwards and truncate data section
                user_section = '\n'.join(lines[user_message_idx:])
                available_chars = max_chars - len(user_section) - 1000  # Reserve space

                if available_chars > 0:
                    # Truncate the data section
                    data_section = '\n'.join(lines[:user_message_idx])
                    if len(data_section) > available_chars:
                        data_section = data_section[:available_chars] + "\n\n[DATA TRUNCATED - Only showing partial data due to size limits]"

                    return data_section + '\n' + user_section

            # Fallback: simple truncation
            truncated = prompt[:max_chars]
            return truncated + "\n\n[TRUNCATED - Please ask more specific questions for detailed data]"

        except Exception as e:
            logger.error(f"Error truncating prompt: {str(e)}")
            # Emergency fallback
            return prompt[:8000] + "\n\n[TRUNCATED DUE TO ERROR]"

    def _summarize_data_context(self, data_context: Dict[str, Any]) -> str:
        """Summarize data context for prompt - optimized for specific module data only"""
        if not data_context:
            return "No specific data available"

        summary = []
        has_any_data = False

        # Handle summary for general queries
        if 'summary' in data_context:
            return data_context['summary']

        if 'incidents' in data_context:
            incidents = data_context['incidents']
            # Check if there's actual incident data
            total_incidents = incidents.get('incidents_reported', 0)
            if isinstance(total_incidents, dict):
                total_incidents = total_incidents.get('total_incidents_reported', 0)
            if total_incidents > 0 or any(v for v in incidents.values() if isinstance(v, (dict, int, float)) and v):
                # Provide key metrics only - more concise
                open_incidents = incidents.get('open_incidents', 0)
                closed_incidents = incidents.get('closed_incidents', 0)
                severity_dist = incidents.get('severity_distribution', {})
                summary.append(f"Incident Data: {total_incidents} total incidents ({open_incidents} open, {closed_incidents} closed)")
                if severity_dist:
                    summary.append(f"Severity breakdown: {severity_dist}")
                has_any_data = True
            else:
                summary.append("Incident Investigation: No incidents found in the selected period")

        if 'actions' in data_context:
            actions = data_context['actions']
            total_actions = actions.get('actions_created', 0)
            if isinstance(total_actions, dict):
                total_actions = total_actions.get('total_actions_created', 0)
            if total_actions > 0:
                on_time_pct = actions.get('on_time_completion', {}).get('percentage', 0)
                overdue_count = actions.get('overdue_actions', {}).get('count', 0)
                summary.append(f"Action Tracking: {total_actions} actions ({on_time_pct}% on-time, {overdue_count} overdue)")
                has_any_data = True
            else:
                summary.append("Action Tracking: No actions found")

        if 'driver_safety' in data_context:
            driver_safety = data_context['driver_safety']
            total_checklists = driver_safety.get('daily_completions', {}).get('total_completed', 0)
            if total_checklists > 0:
                completion_pct = driver_safety.get('daily_completions', {}).get('completion_percentage', 0)
                summary.append(f"Driver Safety: {total_checklists} checklists completed ({completion_pct}% completion rate)")
                has_any_data = True
            else:
                summary.append("Driver Safety: No checklists found")

        if 'observations' in data_context:
            observations = data_context['observations']
            total_observations = observations.get('observations_by_area', {}).get('total_observations', 0)
            if total_observations > 0:
                safe_count = observations.get('behavior_analysis', {}).get('safe_behaviors', 0)
                unsafe_count = observations.get('behavior_analysis', {}).get('unsafe_behaviors', 0)
                summary.append(f"Observations: {total_observations} total ({safe_count} safe, {unsafe_count} unsafe behaviors)")
                has_any_data = True
            else:
                summary.append("Observations: No observations found")

        if 'equipment_assets' in data_context:
            equipment_assets = data_context['equipment_assets']
            total_equipment = equipment_assets.get('summary_metrics', {}).get('total_equipment', 0)
            if total_equipment > 0:
                valid_certs_pct = equipment_assets.get('summary_metrics', {}).get('percentage_with_valid_certificates', 0)
                due_calibration = equipment_assets.get('calibration_status', {}).get('due_for_calibration', 0)
                summary.append(f"Equipment Assets: {total_equipment} total equipment ({valid_certs_pct}% valid certs, {due_calibration} due for calibration)")
                has_any_data = True
            else:
                summary.append("Equipment Assets: No equipment found")

        if 'employee_training' in data_context:
            employee_training = data_context['employee_training']
            expired_count = employee_training.get('expired_trainings', {}).get('employees_with_expired_trainings', 0)
            total_employees = employee_training.get('expired_trainings', {}).get('total_employees', 0)
            upcoming_expiry = employee_training.get('upcoming_expiry', {}).get('employees_with_upcoming_expiry', 0)

            if total_employees > 0:
                # Calculate compliance rate
                compliance_rate = ((total_employees - expired_count) / total_employees * 100) if total_employees > 0 else 0

                # Get department breakdown
                dept_breakdown = employee_training.get('expired_trainings', {}).get('department_breakdown', {})
                dept_info = ""
                if dept_breakdown:
                    dept_list = [f"{dept}: {count} expired" for dept, count in dept_breakdown.items() if count > 0]
                    if dept_list:
                        dept_info = f" Department breakdown: {', '.join(dept_list)}."

                # Get training type breakdown
                training_breakdown = employee_training.get('expired_trainings', {}).get('training_type_breakdown', {})
                training_info = ""
                if training_breakdown:
                    training_list = [f"{training}: {count}" for training, count in training_breakdown.items() if count > 0]
                    if training_list:
                        training_info = f" Most critical expired trainings: {', '.join(training_list)}."

                summary.append(f"Employee Training Status: {total_employees} total employees, {expired_count} have expired training certifications ({compliance_rate:.1f}% compliance rate). {upcoming_expiry} employees have training expiring within 6 months.{dept_info}{training_info}")
                has_any_data = True
            else:
                summary.append("Employee Training: No training data found")

        if 'risk_assessment' in data_context:
            risk_assessment = data_context['risk_assessment']
            total_assessments = risk_assessment.get('number_of_assessments', 0)
            if total_assessments > 0:
                avg_initial = risk_assessment.get('severity_analysis', {}).get('initial_severity', {}).get('average', 0)
                avg_residual = risk_assessment.get('severity_analysis', {}).get('residual_severity', {}).get('average', 0)
                summary.append(f"Risk Assessment: {total_assessments} assessments (avg severity: {avg_initial:.1f} → {avg_residual:.1f})")
                has_any_data = True
            else:
                summary.append("Risk Assessment: No assessments found")

        if not has_any_data:
            return "No data available for the requested module. Please check if data exists for the selected time period."

        return "\n".join(summary)

    def _has_meaningful_data(self, data_context: Dict[str, Any]) -> bool:
        """Check if the data context contains meaningful data to avoid sending empty data to OpenAI"""
        if not data_context:
            logger.info("No data context provided")
            return False

        # Check each module for meaningful data
        for module_name, module_data in data_context.items():
            if not isinstance(module_data, dict):
                continue

            logger.info(f"Checking meaningful data for module: {module_name}")

            # Check for non-zero values in the module data
            if module_name == 'incidents':
                total_incidents = module_data.get('incidents_reported', 0)
                if isinstance(total_incidents, dict):
                    total_incidents = total_incidents.get('total_incidents_reported', 0)
                logger.info(f"Incidents: total_incidents = {total_incidents}")
                if total_incidents > 0:
                    return True

            elif module_name == 'actions':
                total_actions = module_data.get('actions_created', 0)
                if isinstance(total_actions, dict):
                    total_actions = total_actions.get('total_actions_created', 0)
                logger.info(f"Actions: total_actions = {total_actions}")
                if total_actions > 0:
                    return True

            elif module_name == 'driver_safety':
                total_checklists = module_data.get('daily_completions', {}).get('total_completed', 0)
                logger.info(f"Driver Safety: total_checklists = {total_checklists}")
                if total_checklists > 0:
                    return True

            elif module_name == 'observations':
                total_observations = module_data.get('observations_by_area', {}).get('total_observations', 0)
                logger.info(f"Observations: total_observations = {total_observations}")
                if total_observations > 0:
                    return True

            elif module_name == 'equipment_assets':
                total_equipment = module_data.get('summary_metrics', {}).get('total_equipment', 0)
                logger.info(f"Equipment: total_equipment = {total_equipment}")
                if total_equipment > 0:
                    return True
                # Also check for calibration data even if total_equipment is 0
                calibration_certs = module_data.get('calibration_certificates', {})
                if calibration_certs and any(v > 0 for v in calibration_certs.values() if isinstance(v, (int, float))):
                    logger.info(f"Equipment: Found calibration data")
                    return True

            elif module_name == 'employee_training':
                # Enhanced employee training data detection
                total_employees = module_data.get('expired_trainings', {}).get('total_employees', 0)
                expired_count = module_data.get('expired_trainings', {}).get('employees_with_expired_trainings', 0)
                upcoming_count = module_data.get('upcoming_expiry', {}).get('employees_with_upcoming_expiry', 0)

                logger.info(f"Employee Training: total_employees = {total_employees}, expired = {expired_count}, upcoming = {upcoming_count}")

                # Consider data meaningful if we have any employee data at all
                if total_employees > 0:
                    return True

                # Also check summary metrics as fallback
                summary_metrics = module_data.get('summary_metrics', {})
                if summary_metrics.get('total_employees', 0) > 0:
                    logger.info(f"Employee Training: Found data in summary_metrics")
                    return True

            elif module_name == 'risk_assessment':
                total_assessments = module_data.get('number_of_assessments', 0)
                logger.info(f"Risk Assessment: total_assessments = {total_assessments}")
                if total_assessments > 0:
                    return True

            # Check for any nested data with non-zero values
            for key, value in module_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, (int, float)) and sub_value > 0:
                            logger.info(f"Found meaningful data in {module_name}.{key}.{sub_key} = {sub_value}")
                            return True

        logger.info("No meaningful data found in any module")
        return False

    def _clean_ai_response(self, response: str) -> str:
        """Clean AI response to remove problematic formatting while intelligently preserving bullet points"""
        if not response:
            return response

        # Remove excessive markdown formatting that causes display issues
        cleaned = response

        # Remove triple asterisks and other problematic markdown
        cleaned = re.sub(r'\*\*\*+', '', cleaned)  # Remove triple or more asterisks
        cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)  # Remove bold formatting
        cleaned = re.sub(r'#{1,6}\s*', '', cleaned)  # Remove heading markers

        # Remove verbose phrases that we don't want
        cleaned = re.sub(r'^(Based on the data|According to the information|The data shows|Looking at the data)[,:]?\s*', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r'^(From the available data|The information indicates|Analysis reveals)[,:]?\s*', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)

        # Smart bullet point formatting - only convert actual list items, not descriptive text
        lines = cleaned.split('\n')
        processed_lines = []

        for line in lines:
            stripped_line = line.strip()

            # Skip empty lines
            if not stripped_line:
                processed_lines.append(line)
                continue

            # Don't convert lines that are clearly descriptive text or headers
            # These patterns indicate descriptive text, not list items
            if (stripped_line.endswith(':') or
                stripped_line.endswith('include') or
                stripped_line.endswith('includes') or
                stripped_line.lower().startswith('details') or
                stripped_line.lower().startswith('summary') or
                stripped_line.lower().startswith('breakdown') or
                stripped_line.lower().startswith('analysis') or
                stripped_line.lower().startswith('overview') or
                re.match(r'^\d+\s+(employees?|incidents?|actions?|items?)', stripped_line.lower())):
                processed_lines.append(line)
                continue

            # Convert actual list items to bullet points
            # Only convert if it starts with bullet/dash/asterisk and contains meaningful content
            if re.match(r'^\s*[•*-]\s+.+', line):
                # Extract the content after the bullet/dash/asterisk
                content_match = re.match(r'^\s*[•*-]\s+(.+)', line)
                if content_match:
                    content = content_match.group(1)
                    # Only convert if it looks like a list item (not just a single word or number)
                    if len(content.split()) > 1 or '(' in content:
                        processed_lines.append('• ' + content)
                    else:
                        processed_lines.append(line)
                else:
                    processed_lines.append(line)
            else:
                processed_lines.append(line)

        cleaned = '\n'.join(processed_lines)

        # Clean up extra whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # Remove excessive line breaks
        cleaned = cleaned.strip()

        return cleaned

    def _generate_suggested_actions(self, intent: str, data_context: Dict[str, Any]) -> List[str]:
        """Generate module-specific suggested follow-up actions based on intent"""
        if intent == 'incident_investigation':
            return [
                "Show incident trends by severity",
                "Which departments have the most incidents?",
                "What are the common incident types?",
                "How long do investigations take on average?"
            ]
        elif intent == 'action_tracking':
            return [
                "Show me overdue actions",
                "What's my action completion rate?",
                "Which actions need immediate attention?",
                "Show me action completion by department"
            ]
        elif intent == 'driver_safety':
            return [
                "What's our driver safety checklist completion rate?",
                "How many vehicles are deemed unfit?",
                "Show me driver safety compliance trends",
                "Which vehicles need safety attention?"
            ]
        elif intent == 'observation_tracker':
            return [
                "Show observations by area",
                "What's the observation priority breakdown?",
                "Show me observation trends",
                "Which areas need more observation attention?"
            ]
        elif 'equipment' in intent or 'asset' in intent or 'calibration' in intent or 'inspection' in intent:
            return [
                "Show equipment calibration status",
                "Which equipment needs inspection?",
                "What's our equipment compliance rate?",
                "Show equipment by type",
                "Which equipment has anomalies?"
            ]
        elif intent == 'employee_training':
            return [
                "Show employees with expired trainings",
                "What's our training compliance rate?",
                "Which employees need medical checkups?",
                "Show training expiry by department",
                "Who has upcoming training renewals?"
            ]
        elif 'risk_assessment' in intent or 'risk' in intent or 'hazard' in intent or 'assessment' in intent:
            return [
                "Show risk assessment summary",
                "What are the common hazards identified?",
                "Which activities have high residual risk?",
                "How effective are our control measures?",
                "Show risk severity and likelihood analysis"
            ]
        else:
            return [
                "Show incidents",
                "Show actions",
                "Show driver safety",
                "Show observations",
                "Show equipment assets",
                "Show employee training",
                "Show risk assessments"
            ]

    def _generate_chart_data(self, user_message: str, intent: str, data_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart data using AI and ECharts for enhanced interactivity"""
        if not data_context:
            return None

        try:
            # First, try to generate chart specification using AI
            chart_spec = None
            if self.openai_client:
                chart_spec = self._generate_ai_chart_spec(user_message, data_context)

            # If no AI chart spec, create a fallback chart based on intent
            if not chart_spec:
                chart_spec = self._generate_fallback_chart_spec(intent, data_context)

            if not chart_spec:
                return None

            # Prioritize ECharts for enhanced interactivity
            if self.echarts_generator:
                echarts_config = self.echarts_generator.generate_chart(chart_spec)
                if echarts_config:
                    logger.info("Generated ECharts configuration for enhanced interactivity")
                    return echarts_config

            # Fallback to Plotly if ECharts is not available
            if self.plotly_generator:
                plotly_config = self.plotly_generator.generate_chart(chart_spec)
                if plotly_config:
                    logger.info("Generated Plotly configuration as fallback")
                    return plotly_config

            # Basic chart configuration as final fallback
            result = {
                'type': chart_spec.get('type', 'bar'),
                'title': chart_spec.get('title', 'Data Visualization'),
                'data': chart_spec.get('data', []),
                'ai_generated': chart_spec.get('ai_generated', False),
                'showValues': chart_spec.get('showValues', True),
                'showLabels': chart_spec.get('showLabels', True),
                'showLegend': chart_spec.get('showLegend', True)
            }

            return result

        except Exception as e:
            logger.error(f"Error in chart generation: {str(e)}")
            return None

    def _generate_ai_chart_spec(self, user_message: str, data_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart specification using AI"""
        try:
            prompt = f"""
            User asked: "{user_message}"
            Available data: {safe_json_dumps(data_context, indent=2)}

            Create a chart with proper labels and values. Respond with ONLY this JSON format:
            {{
                "create_chart": true,
                "type": "bar|donut|line|pie|scatter",
                "title": "Descriptive Chart Title",
                "data": [
                    {{"name": "Category Name", "value": 123, "label": "123 items", "color": "#FF6B6B"}},
                    {{"name": "Another Category", "value": 456, "label": "456 items", "color": "#4ECDC4"}}
                ],
                "showValues": true,
                "showLabels": true,
                "showLegend": true
            }}

            If no chart needed, respond with: {{"create_chart": false}}
            Extract real data only. Use meaningful colors and ensure all values are visible.
            """

            # Truncate prompt for chart generation too
            truncated_prompt = self._truncate_prompt_for_context(prompt, max_tokens=8000)

            # Select optimal model for chart generation (usually fast models are sufficient)
            chart_model = self._select_optimal_model(truncated_prompt)
            # For chart generation, prefer fast models even if over threshold (charts are simpler)
            if chart_model in self.large_context_models:
                chart_model = self.fast_models[0]  # Use fastest model for chart generation
                logger.info(f"Using fast model {chart_model} for chart generation instead of {chart_model}")

            response = self.openai_client.chat.completions.create(
                model=chart_model,
                messages=[
                    {"role": "system", "content": "You are a chart generator. Respond only with valid JSON."},
                    {"role": "user", "content": truncated_prompt}
                ],
                max_tokens=400,  # Reduced for faster response
                temperature=0.1  # Very low for fastest response
            )

            ai_response = response.choices[0].message.content.strip()

            # Extract JSON
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                chart_spec = json.loads(json_str)

                if chart_spec.get('create_chart', False):
                    return {
                        'type': chart_spec.get('type', 'bar'),
                        'title': chart_spec.get('title', 'Data Visualization'),
                        'data': chart_spec.get('data', []),
                        'ai_generated': True
                    }

        except Exception as e:
            logger.error(f"Error in AI chart generation: {str(e)}")

        return None

    def _generate_fallback_chart_spec(self, intent: str, data_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback chart specification based on intent and available data"""
        try:
            # Generate charts based on intent and available data
            if intent == 'incident_investigation' and 'incidents' in data_context:
                return self._create_incident_chart(data_context['incidents'])
            elif intent == 'action_tracking' and 'actions' in data_context:
                return self._create_action_chart(data_context['actions'])
            elif intent == 'driver_safety' and 'driver_safety' in data_context:
                return self._create_driver_safety_chart(data_context['driver_safety'])
            elif intent == 'observation_tracker' and 'observations' in data_context:
                return self._create_observation_chart(data_context['observations'])
            elif intent == 'equipment_asset' and 'equipment_assets' in data_context:
                return self._create_equipment_asset_chart(data_context['equipment_assets'])
            elif intent == 'employee_training' and 'employee_training' in data_context:
                return self._create_employee_training_chart(data_context['employee_training'])
            elif intent == 'risk_assessment' and 'risk_assessment' in data_context:
                return self._create_risk_assessment_chart(data_context['risk_assessment'])

            # Default: create a summary chart if multiple modules have data
            return self._create_summary_chart(data_context)

        except Exception as e:
            logger.error(f"Error in fallback chart generation: {str(e)}")
            return None

    def _create_incident_chart(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create incident-specific chart"""
        logger.info(f"Creating incident chart with data keys: {list(incident_data.keys())}")

        if 'incident_types_breakdown' in incident_data:
            breakdown = incident_data['incident_types_breakdown']
            logger.info(f"Incident types breakdown: {breakdown}")
            data = []
            for key, value in breakdown.items():
                if key.endswith('_pct') or key in ['total_incidents', 'breakdown_percentages', 'description']:
                    continue
                if isinstance(value, (int, float)) and value > 0:
                    data.append({'name': key.replace('_', ' ').title(), 'value': value})

            logger.info(f"Chart data created: {data}")
            if data:
                chart_result = {
                    'type': 'donut',
                    'title': 'Incident Types Breakdown',
                    'data': data,
                    'ai_generated': False
                }
                logger.info(f"Returning chart: {chart_result}")
                return chart_result

        # Fallback: try to create chart from other incident data
        if 'incidents_reported' in incident_data:
            reported = incident_data['incidents_reported']
            logger.info(f"Trying fallback with incidents_reported: {reported}")

            # Handle both dictionary and integer formats
            total_incidents = 0
            if isinstance(reported, dict):
                # Dictionary format: {'total_incidents_reported': 25}
                total_incidents = reported.get('total_incidents_reported', 0)
            elif isinstance(reported, (int, float)):
                # Integer format: 25
                total_incidents = reported

            if total_incidents > 0:
                # Create a simple chart showing total incidents
                data = [{'name': 'Total Incidents', 'value': total_incidents}]
                chart_result = {
                    'type': 'bar',
                    'title': 'Incidents Reported',
                    'data': data,
                    'ai_generated': False
                }
                logger.info(f"Returning fallback chart: {chart_result}")
                return chart_result

        logger.info("No incident types breakdown found, returning None")
        return None

    def _create_action_chart(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create action-specific chart"""
        if 'actions_created' in action_data:
            actions = action_data['actions_created']
            data = [
                {'name': 'Completed', 'value': actions.get('completed_actions', 0)},
                {'name': 'Open', 'value': actions.get('open_actions', 0)}
            ]

            if any(item['value'] > 0 for item in data):
                return {
                    'type': 'pie',
                    'title': 'Action Status Distribution',
                    'data': data,
                    'ai_generated': False
                }

        return None

    def _create_driver_safety_chart(self, driver_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create driver safety-specific chart"""
        if self.plotly_generator:
            return self.plotly_generator.generate_safety_dashboard_chart('driver_safety', driver_data)
        return None

    def _create_observation_chart(self, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create observation-specific chart"""
        if self.plotly_generator:
            return self.plotly_generator.generate_safety_dashboard_chart('observations', observation_data)
        return None

    def _create_equipment_asset_chart(self, equipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create equipment asset-specific chart"""
        try:
            # Create calibration certificate status chart
            calibration_certs = equipment_data.get('calibration_certificates', {})
            if calibration_certs:
                data = [
                    {'name': 'Valid Certificates', 'value': calibration_certs.get('equipment_with_valid_certificates', 0)},
                    {'name': 'Invalid Certificates', 'value': calibration_certs.get('equipment_without_valid_certificates', 0)},
                    {'name': 'Missing Info', 'value': calibration_certs.get('equipment_with_missing_certificate_info', 0)}
                ]

                if any(item['value'] > 0 for item in data):
                    return {
                        'type': 'donut',
                        'title': 'Equipment Calibration Certificate Status',
                        'data': data,
                        'ai_generated': False
                    }

            # Fallback to equipment types chart
            equipment_types = equipment_data.get('equipment_types_and_counts', {}).get('equipment_by_asset_type', {})
            if equipment_types:
                data = [{'name': name, 'value': count} for name, count in equipment_types.items()]
                if data:
                    return {
                        'type': 'bar',
                        'title': 'Equipment Types Distribution',
                        'data': data,
                        'ai_generated': False
                    }
        except Exception as e:
            logger.error(f"Error creating equipment asset chart: {str(e)}")

        return None

    def _create_employee_training_chart(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create enhanced employee training-specific chart with detailed labels"""
        try:
            # Create detailed training expiry chart
            expired_trainings = training_data.get('expired_trainings', {})
            upcoming_expiry = training_data.get('upcoming_expiry', {})
            total_employees = expired_trainings.get('total_employees', 0)
            expired_count = expired_trainings.get('employees_with_expired_trainings', 0)
            upcoming_count = upcoming_expiry.get('employees_with_upcoming_expiry', 0)
            current_count = max(0, total_employees - expired_count - upcoming_count)

            if total_employees > 0:
                # Enhanced data with labels and colors
                data = [
                    {
                        'name': 'Expired Training',
                        'value': expired_count,
                        'label': f'{expired_count} employees ({(expired_count/total_employees*100):.1f}%)',
                        'color': '#FF6B6B'  # Red for expired
                    },
                    {
                        'name': 'Expiring Soon (6 months)',
                        'value': upcoming_count,
                        'label': f'{upcoming_count} employees ({(upcoming_count/total_employees*100):.1f}%)',
                        'color': '#FFD93D'  # Yellow for warning
                    },
                    {
                        'name': 'Current/Valid Training',
                        'value': current_count,
                        'label': f'{current_count} employees ({(current_count/total_employees*100):.1f}%)',
                        'color': '#6BCF7F'  # Green for valid
                    }
                ]

                return {
                    'type': 'donut',
                    'title': f'Employee Training Status ({total_employees} Total Employees)',
                    'data': data,
                    'ai_generated': False,
                    'showValues': True,
                    'showLabels': True,
                    'showLegend': True,
                    'options': {
                        'responsive': True,
                        'maintainAspectRatio': False,
                        'plugins': {
                            'legend': {
                                'display': True,
                                'position': 'bottom',
                                'labels': {
                                    'usePointStyle': True,
                                    'padding': 20
                                }
                            },
                            'tooltip': {
                                'enabled': True,
                                'callbacks': {
                                    'label': 'function(context) { return context.parsed + " employees (" + (context.parsed/context.dataset.data.reduce((a,b) => a+b, 0)*100).toFixed(1) + "%)"; }'
                                }
                            },
                            'datalabels': {
                                'display': True,
                                'color': '#000',
                                'font': {
                                    'weight': 'bold',
                                    'size': 12
                                },
                                'formatter': 'function(value, context) { return value + " (" + (value/context.dataset.data.reduce((a,b) => a+b, 0)*100).toFixed(1) + "%)"; }'
                            }
                        }
                    }
                }

            # Fallback to fitness metrics if training data not available
            fitness_metrics = training_data.get('fitness_metrics', {})
            if fitness_metrics:
                fit_count = fitness_metrics.get('fit_employees', 0)
                unfit_count = fitness_metrics.get('unfit_employees', 0)
                total_fitness = fit_count + unfit_count

                if total_fitness > 0:
                    data = [
                        {
                            'name': 'Fit Employees',
                            'value': fit_count,
                            'label': f'{fit_count} employees ({(fit_count/total_fitness*100):.1f}%)',
                            'color': '#6BCF7F'
                        },
                        {
                            'name': 'Unfit Employees',
                            'value': unfit_count,
                            'label': f'{unfit_count} employees ({(unfit_count/total_fitness*100):.1f}%)',
                            'color': '#FF6B6B'
                        }
                    ]

                    return {
                        'type': 'donut',
                        'title': f'Employee Fitness Status ({total_fitness} Total)',
                        'data': data,
                        'ai_generated': False,
                        'showValues': True,
                        'showLabels': True,
                        'showLegend': True
                    }

        except Exception as e:
            logger.error(f"Error creating employee training chart: {str(e)}")

        return None

    def _create_risk_assessment_chart(self, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create risk assessment-specific chart"""
        try:
            # Create severity analysis chart
            severity_analysis = risk_data.get('severity_analysis', {})
            if severity_analysis.get('initial_severity', {}).get('distribution'):
                initial_dist = severity_analysis['initial_severity']['distribution']
                data = []
                for severity, count in initial_dist.items():
                    if count > 0:
                        data.append({'name': f'Severity {severity}', 'value': count})

                if data:
                    return {
                        'type': 'bar',
                        'title': 'Risk Severity Distribution (Initial)',
                        'data': data,
                        'ai_generated': False
                    }

            # Fallback to hazard effects chart
            effects_analysis = risk_data.get('hazard_effects', {})
            if effects_analysis.get('effects_distribution'):
                effects_dist = effects_analysis['effects_distribution']
                data = []
                for effect, info in effects_dist.items():
                    count = info.get('count', 0)
                    meaning = info.get('meaning', effect)
                    if count > 0:
                        data.append({'name': meaning, 'value': count})

                if data:
                    return {
                        'type': 'donut',
                        'title': 'Hazard Effects Distribution',
                        'data': data,
                        'ai_generated': False
                    }

        except Exception as e:
            logger.error(f"Error creating risk assessment chart: {str(e)}")

        return None

    def _create_summary_chart(self, data_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary chart across all modules"""
        data = []

        if 'incidents' in data_context:
            incidents_reported = data_context['incidents'].get('incidents_reported', 0)
            total = 0
            if isinstance(incidents_reported, dict):
                total = incidents_reported.get('total_incidents_reported', 0)
            elif isinstance(incidents_reported, (int, float)):
                total = incidents_reported
            if total > 0:
                data.append({'name': 'Incidents', 'value': total})

        if 'actions' in data_context:
            total = data_context['actions'].get('actions_created', {}).get('total_actions_created', 0)
            if total > 0:
                data.append({'name': 'Actions', 'value': total})

        if 'equipment_assets' in data_context:
            total = data_context['equipment_assets'].get('summary_metrics', {}).get('total_equipment', 0)
            if total > 0:
                data.append({'name': 'Equipment', 'value': total})

        if 'employee_training' in data_context:
            total = data_context['employee_training'].get('summary_metrics', {}).get('total_employees', 0)
            if total > 0:
                data.append({'name': 'Employees', 'value': total})

        if 'risk_assessment' in data_context:
            total = data_context['risk_assessment'].get('number_of_assessments', 0)
            if total > 0:
                data.append({'name': 'Risk Assessments', 'value': total})

        if data:
            return {
                'type': 'bar',
                'title': 'Safety Metrics Overview',
                'data': data,
                'ai_generated': False
            }

        return None

    def _add_message(self, session_id: str, role: str, content: str) -> ChatMessage:
        """Add message to conversation history"""
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )

        if session_id in self.conversations:
            self.conversations[session_id].conversation_history.append({
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat()
            })

        return message

    def get_conversation_history(self, session_id: str) -> List[ChatMessage]:
        """Get conversation history for a session"""
        if session_id not in self.conversations:
            return []

        history = []
        for msg in self.conversations[session_id].conversation_history:
            history.append(ChatMessage(
                role=msg['role'],
                content=msg['content'],
                timestamp=datetime.fromisoformat(msg['timestamp'])
            ))

        return history

    def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            return True
        return False

    def get_proactive_insights(self, session_id: str) -> List[str]:
        """Generate proactive insights based on current data"""
        try:
            if session_id not in self.conversations:
                return []

            context = self.conversations[session_id]
            data = self._get_relevant_data(context, 'show_metrics')

            insights = []

            # Analyze data for proactive insights from 4 core modules
            if 'incidents' in data:
                incidents = data['incidents']
                incidents_reported = incidents.get('incidents_reported', 0)
                total_incidents = 0
                if isinstance(incidents_reported, dict):
                    total_incidents = incidents_reported.get('total_incidents_reported', 0)
                elif isinstance(incidents_reported, (int, float)):
                    total_incidents = incidents_reported
                if total_incidents > 5:
                    insights.append("🚨 You have multiple incidents this period. Would you like me to analyze investigation trends?")

            if 'actions' in data:
                actions = data['actions']
                completion_rate = actions.get('on_time_completion', {}).get('on_time_completion_percentage', 100)
                if completion_rate < 80:
                    insights.append("📋 Action completion is falling behind. Let me show you which actions need immediate attention.")

            if 'driver_safety' in data:
                driver_safety = data['driver_safety']
                unfit_vehicles = driver_safety.get('vehicles_deemed_unfit', {}).get('total_unfit_vehicles', 0)
                if unfit_vehicles > 0:
                    insights.append("🚗 You have vehicles deemed unfit. Would you like to see which vehicles need attention?")

            if 'observations' in data:
                observations = data['observations']
                total_observations = observations.get('observations_by_area', {}).get('total_observations', 0)
                if total_observations > 10:
                    insights.append("�️ You have multiple safety observations. Let me show you the areas that need most attention.")

            if 'equipment_assets' in data:
                equipment_assets = data['equipment_assets']
                expired_calibrations = equipment_assets.get('summary_metrics', {}).get('percentage_expired_calibrations', 0)
                equipment_needing_attention = equipment_assets.get('summary_metrics', {}).get('equipment_needing_attention', 0)

                if expired_calibrations > 30:
                    insights.append("🔧 You have equipment with expired calibrations. Would you like to see which equipment needs immediate attention?")
                elif equipment_needing_attention > 5:
                    insights.append("⚠️ Multiple equipment items need attention for inspections or maintenance.")

            if 'employee_training' in data:
                employee_training = data['employee_training']
                expired_trainings = employee_training.get('summary_metrics', {}).get('employees_with_expired_trainings', 0)
                unfit_percentage = employee_training.get('summary_metrics', {}).get('percentage_unfit_employees', 0)
                missing_medical = employee_training.get('summary_metrics', {}).get('employees_missing_medical_data', 0)

                if expired_trainings > 0:
                    insights.append(f"🎓 {expired_trainings} employees have expired training certifications. Would you like to see who needs recertification?")
                elif unfit_percentage > 0:
                    insights.append(f"🏥 {unfit_percentage}% of employees are unfit for work. Let me show you the details.")
                elif missing_medical > 5:
                    insights.append(f"📋 {missing_medical} employees have incomplete medical records. Would you like to see who needs medical data updates?")

            if 'risk_assessment' in data:
                risk_assessment = data['risk_assessment']
                total_assessments = risk_assessment.get('number_of_assessments', 0)
                high_risk_activities = risk_assessment.get('high_residual_risk_activities', {}).get('total_high_risk', 0)
                effectiveness = risk_assessment.get('measure_effectiveness', {}).get('overall_effectiveness', 100)

                if high_risk_activities > 0:
                    insights.append(f"⚠️ {high_risk_activities} activities still have high residual risk. Would you like to see which activities need attention?")
                elif effectiveness < 50:
                    insights.append(f"📊 Control measure effectiveness is {effectiveness:.1f}%. Let me show you how to improve risk controls.")
                elif total_assessments > 5:
                    insights.append(f"📋 {total_assessments} risk assessments completed. Would you like to see the risk analysis summary?")

            return insights[:3]  # Limit to 3 proactive insights

        except Exception as e:
            logger.error(f"Error generating proactive insights: {str(e)}")
            return []

    def _generate_fallback_response(self, user_message: str, intent: str, data_context: Dict[str, Any]) -> str:
        """Enhanced fallback response that provides actual data when available - improved for question alignment"""
        has_data = self._has_meaningful_data(data_context)

        # Clean the user message
        clean_user_message = user_message
        if clean_user_message.lower().startswith('[module:'):
            end_bracket = clean_user_message.find(']')
            if end_bracket != -1:
                clean_user_message = clean_user_message[end_bracket + 1:].strip()

        user_message_lower = clean_user_message.lower()

        logger.info(f"Generating fallback response for: '{clean_user_message}', Intent: {intent}, Has data: {has_data}")

        if has_data:
            # Generate specific responses based on what user is asking about

            # Handle employee training questions specifically
            if any(keyword in user_message_lower for keyword in ['employee', 'training', 'expired', 'expire', 'expiry']):
                if 'employee_training' in data_context:
                    train_data = data_context['employee_training']
                    total_emp = train_data.get('expired_trainings', {}).get('total_employees', 0)
                    expired = train_data.get('expired_trainings', {}).get('employees_with_expired_trainings', 0)
                    upcoming = train_data.get('upcoming_expiry', {}).get('employees_with_upcoming_expiry', 0)

                    if total_emp > 0:
                        if expired > 0:
                            response = f"{expired} employees have expired training certifications out of {total_emp} total employees."
                            if upcoming > 0:
                                response += f" Additionally, {upcoming} employees have training expiring within 6 months."
                            return response
                        elif upcoming > 0:
                            return f"{upcoming} employees have training expiring within 6 months out of {total_emp} total employees."
                        else:
                            return f"All {total_emp} employees have current training certifications."

            # Handle equipment questions
            if any(keyword in user_message_lower for keyword in ['equipment', 'asset', 'calibration', 'certificate']):
                if 'equipment_assets' in data_context:
                    eq_data = data_context['equipment_assets']
                    total_eq = eq_data.get('summary_metrics', {}).get('total_equipment', 0)
                    if total_eq > 0:
                        valid_certs = eq_data.get('summary_metrics', {}).get('percentage_with_valid_certificates', 0)
                        return f"{total_eq} total equipment items with {valid_certs}% having valid certificates."

            # Handle incident questions
            if any(keyword in user_message_lower for keyword in ['incident', 'accident', 'investigation']):
                if 'incidents' in data_context:
                    inc_data = data_context['incidents']
                    incidents_reported = inc_data.get('incidents_reported', 0)
                    total_inc = 0
                    if isinstance(incidents_reported, dict):
                        total_inc = incidents_reported.get('total_incidents', 0) or incidents_reported.get('total_incidents_reported', 0)
                    elif isinstance(incidents_reported, (int, float)):
                        total_inc = incidents_reported
                    if total_inc > 0:
                        return f"{total_inc} incidents reported in the selected period."

            # General data summary if no specific match
            summary_parts = []
            if 'equipment_assets' in data_context:
                eq_data = data_context['equipment_assets']
                total_eq = eq_data.get('summary_metrics', {}).get('total_equipment', 0)
                if total_eq > 0:
                    valid_certs = eq_data.get('summary_metrics', {}).get('percentage_with_valid_certificates', 0)
                    summary_parts.append(f"Equipment: {total_eq} total ({valid_certs}% valid certificates)")

            if 'incidents' in data_context:
                inc_data = data_context['incidents']
                incidents_reported = inc_data.get('incidents_reported', 0)
                total_inc = 0
                if isinstance(incidents_reported, dict):
                    total_inc = incidents_reported.get('total_incidents', 0) or incidents_reported.get('total_incidents_reported', 0)
                elif isinstance(incidents_reported, (int, float)):
                    total_inc = incidents_reported
                if total_inc > 0:
                    summary_parts.append(f"Incidents: {total_inc} total")

            if 'employee_training' in data_context:
                train_data = data_context['employee_training']
                total_emp = train_data.get('expired_trainings', {}).get('total_employees', 0)
                if total_emp > 0:
                    expired = train_data.get('expired_trainings', {}).get('employees_with_expired_trainings', 0)
                    summary_parts.append(f"Employees: {total_emp} total ({expired} with expired training)")

            if summary_parts:
                return "✓ Data available: " + ", ".join(summary_parts) + ". Ask specific questions for detailed insights."
            else:
                return "✓ Data available. Ask specific questions for detailed insights."
        else:
            return "No data found for your query. Try asking about: equipment status, incident reports, employee training, actions, driver safety, observations, or risk assessments."
