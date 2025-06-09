"""
AI Engine Module for SafetyConnect
Provides AI-powered analysis and summarization capabilities
"""

from .summarization_engine import SafetySummarizationEngine, ModuleAnalysis
from .cache_manager import ai_cache, cached_ai_response
from .conversational_ai import ConversationalAI

try:
    from .plotly_chart_generator import PlotlyChartGenerator
    plotly_available = True
except ImportError:
    plotly_available = False
    PlotlyChartGenerator = None

__all__ = [
    'SafetySummarizationEngine',
    'ModuleAnalysis', 
    'ConversationalAI',
    'ai_cache',
    'cached_ai_response'
]

if plotly_available:
    __all__.append('PlotlyChartGenerator')
