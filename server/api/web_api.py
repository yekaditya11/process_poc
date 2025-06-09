

"""
FastAPI Web API for SafetyConnect Dashboard
Provides REST endpoints for safety management dashboard KPIs and conversational AI
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_app import SafetySummarizerApp
from ai_engine.conversational_ai import ConversationalAI
from ai_engine.cache_manager import ai_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SafetyConnect Dashboard API",
    description="Safety management dashboard with 4 core KPI modules and conversational AI",
    version="3.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class SummaryResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    generated_at: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = "anonymous"

class ChatResponse(BaseModel):
    success: bool
    session_id: str
    message: str
    suggested_actions: List[str]
    data_context: Optional[Dict[str, Any]] = None
    chart_data: Optional[Dict[str, Any]] = None
    timestamp: str

class ConversationHistoryResponse(BaseModel):
    success: bool
    session_id: str
    history: List[Dict[str, Any]]

class DashboardConfigRequest(BaseModel):
    dashboard_name: str
    charts: List[Dict[str, Any]]
    user_id: Optional[str] = "anonymous"

class DashboardConfigResponse(BaseModel):
    success: bool
    dashboard_id: str
    message: str

# Initialize the main application
summarizer_app = SafetySummarizerApp()

# Initialize conversational AI
conversational_ai = ConversationalAI(summarizer_app)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/debug/chat-test")
async def debug_chat_test():
    """Debug endpoint to test chat functionality"""
    try:
        # Test data extraction
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        incident_data = summarizer_app.incident_extractor.get_all_incident_kpis(
            customer_id=None,
            start_date=start_date,
            end_date=end_date
        )

        # Test conversational AI initialization
        test_session = conversational_ai.start_conversation("test_user")

        # Test message processing
        test_response = conversational_ai.process_message(test_session, "Show recent incidents")

        return {
            "success": True,
            "data_extraction": {
                "incident_data_keys": list(incident_data.keys()) if incident_data else None,
                "incident_data_sample": str(incident_data)[:500] if incident_data else None
            },
            "ai_processing": {
                "session_id": test_session,
                "response_content": test_response.content[:200] if test_response else None,
                "has_chart_data": bool(getattr(test_response, 'chart_data', None)),
                "has_suggested_actions": bool(getattr(test_response, 'suggested_actions', None))
            },
            "openai_available": bool(conversational_ai.openai_client),
            "plotly_available": bool(conversational_ai.plotly_generator)
        }
    except Exception as e:
        logger.error(f"Debug test failed: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get("/metrics/incident-investigation-kpis", response_model=SummaryResponse)
async def get_incident_investigation_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back")
):
    """Get comprehensive incident investigation KPIs"""
    try:
        logger.info(f"Generating incident investigation KPIs for customer: {customer_id}")

        # Get incident investigation KPIs using the new extractor
        kpis = summarizer_app.incident_extractor.get_incident_investigation_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=kpis,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating incident investigation KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/action-tracking-kpis", response_model=SummaryResponse)
async def get_action_tracking_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back")
):
    """Get comprehensive action tracking KPIs"""
    try:
        logger.info(f"Generating action tracking KPIs for customer: {customer_id}")

        # Get action tracking KPIs using the initialized extractor
        kpis = summarizer_app.action_extractor.get_action_tracking_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=kpis,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating action tracking KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/driver-safety-checklist-kpis", response_model=SummaryResponse)
async def get_driver_safety_checklist_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back")
):
    """Get comprehensive driver safety checklist KPIs"""
    try:
        logger.info(f"Generating driver safety checklist KPIs for customer: {customer_id}")

        # Get driver safety checklist KPIs using the initialized extractor
        kpis = summarizer_app.driver_safety_extractor.get_driver_safety_checklist_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=kpis,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating driver safety checklist KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/metrics/observation-tracker-kpis", response_model=SummaryResponse)
async def get_observation_tracker_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back")
):
    """Get comprehensive observation tracker KPIs"""
    try:
        logger.info(f"Generating observation tracker KPIs for customer: {customer_id}")

        # Get observation tracker KPIs using the initialized extractor
        kpis = summarizer_app.observation_tracker_extractor.get_observation_tracker_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=kpis,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating observation tracker KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/equipment-asset-kpis", response_model=SummaryResponse)
async def get_equipment_asset_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back")
):
    """Get comprehensive equipment asset KPIs"""
    try:
        logger.info(f"Generating equipment asset KPIs for customer: {customer_id}")

        # Get equipment asset KPIs using the initialized extractor
        kpis = summarizer_app.equipment_asset_extractor.get_equipment_asset_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=kpis,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating equipment asset KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/employee-training-kpis", response_model=SummaryResponse)
async def get_employee_training_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(365, description="Number of days to look back")
):
    """Get comprehensive employee training and fitness KPIs"""
    try:
        logger.info(f"Generating employee training KPIs for customer: {customer_id}")

        # Get employee training KPIs using the initialized extractor
        kpis = summarizer_app.employee_training_extractor.get_employee_training_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=kpis,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating employee training KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/risk-assessment-kpis", response_model=SummaryResponse)
async def get_risk_assessment_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back")
):
    """Get comprehensive risk assessment KPIs"""
    try:
        logger.info(f"Generating risk assessment KPIs for customer: {customer_id}")

        # Get risk assessment KPIs using the initialized extractor
        kpis = summarizer_app.risk_assessment_extractor.get_risk_assessment_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=kpis,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating risk assessment KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/all-safety-kpis")
async def get_all_safety_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(365, description="Number of days to look back")
):
    """Get all safety KPIs for the comprehensive dashboard"""
    try:
        logger.info(f"Generating all safety KPIs for customer: {customer_id}")

        # Calculate date range for extractors that need it
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Fetch all KPIs from the 4 core modules using correct method names
        incident_kpis = summarizer_app.incident_extractor.get_all_incident_kpis(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )

        action_kpis = summarizer_app.action_extractor.get_all_action_tracking_kpis(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )

        driver_safety_kpis = summarizer_app.driver_safety_extractor.get_driver_safety_checklist_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        observation_kpis = summarizer_app.observation_tracker_extractor.get_observation_tracker_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        equipment_asset_kpis = summarizer_app.equipment_asset_extractor.get_equipment_asset_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        employee_training_kpis = summarizer_app.employee_training_extractor.get_employee_training_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        risk_assessment_kpis = summarizer_app.risk_assessment_extractor.get_risk_assessment_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        # Combine all KPIs into a comprehensive response
        combined_response = {
            "safety_dashboard_data": {
                "incident_investigation": incident_kpis,
                "driver_safety_checklists": driver_safety_kpis,
                "observation_tracker": observation_kpis,
                "action_tracking": action_kpis,
                "equipment_asset_management": equipment_asset_kpis,
                "employee_training_fitness": employee_training_kpis,
                "risk_assessment": risk_assessment_kpis
            },
            "extraction_metadata": {
                "extraction_timestamp": datetime.now().isoformat(),
                "modules_extracted": 7,
                "total_kpis": {
                    "incident_investigation": 13,  # 11 main + 2 insights
                    "driver_safety_checklists": 4,  # Daily/Weekly completion + Vehicle fitness + Overdue drivers
                    "observation_tracker": 4,  # By area + Status + Priority + Remarks insight
                    "action_tracking": 4,  # Actions created + % on time + Open/Closed + Overdue employees
                    "equipment_asset_management": 7,  # Calibration + Expiry + Inspection + Types + Insights
                    "employee_training_fitness": 8,  # Expired + Upcoming + Fitness + Medical + Department + Insights
                    "risk_assessment": 9  # 4 main KPIs + 5 insights
                },
                "template_ids": {
                    "driver_safety_checklists": "a35be57e-dd36-4a21-b05b-e4d4fa836f53",
                    "observation_tracker": "9bb83f61-b869-4721-81b6-0c870e91a779"
                },
                "date_range": {
                    "days_back": days_back,
                    "customer_id": customer_id
                }
            },
            "status": "success"
        }

        return combined_response

    except Exception as e:
        logger.error(f"Error generating all safety KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Conversational AI Endpoints

@app.post("/chat/start", response_model=ChatResponse)
async def start_conversation(
    user_id: str = "anonymous"
):
    """Start a new conversation session"""
    try:
        session_id = conversational_ai.start_conversation(user_id)

        # Get the welcome message
        history = conversational_ai.get_conversation_history(session_id)
        welcome_message = history[-1] if history else None

        if welcome_message:
            return ChatResponse(
                success=True,
                session_id=session_id,
                message=welcome_message.content,
                suggested_actions=welcome_message.suggested_actions or [],
                data_context=welcome_message.data_context,
                timestamp=welcome_message.timestamp.isoformat()
            )
        else:
            return ChatResponse(
                success=True,
                session_id=session_id,
                message="👋 Hello! I'm your SafetyConnect AI assistant.\n\nWhat would you like to know?",
                suggested_actions=[
                    "Show incidents",
                    "Show actions",
                    "Show driver safety",
                    "Show observations"
                ],
                data_context=None,
                timestamp=datetime.now().isoformat()
            )

    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/message", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """Send a message to the conversational AI"""
    try:
        # Process the message
        response_message = conversational_ai.process_message(
            session_id=request.session_id or "default",
            user_message=request.message
        )

        return ChatResponse(
            success=True,
            session_id=request.session_id or "default",
            message=response_message.content,
            suggested_actions=response_message.suggested_actions or [],
            data_context=response_message.data_context,
            chart_data=getattr(response_message, 'chart_data', None),
            timestamp=response_message.timestamp.isoformat()
        )

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Module-specific chat endpoints
@app.post("/chat/modules/{module_name}/message", response_model=ChatResponse)
async def send_module_chat_message(module_name: str, request: ChatRequest):
    """Send a message to the conversational AI with module context"""
    try:
        # Validate module name
        valid_modules = [
            'incident-investigation', 'risk-assessment', 'action-tracking',
            'driver-safety', 'observation-tracker', 'equipment-asset', 'employee-training'
        ]

        if module_name not in valid_modules:
            raise HTTPException(status_code=400, detail=f"Invalid module name. Valid modules: {valid_modules}")

        # Add module context to the message
        module_context_message = f"[Module: {module_name}] {request.message}"

        # Process the message with module context
        response_message = conversational_ai.process_message(
            session_id=request.session_id or f"module_{module_name}",
            user_message=module_context_message
        )

        return ChatResponse(
            success=True,
            session_id=request.session_id or f"module_{module_name}",
            message=response_message.content,
            suggested_actions=response_message.suggested_actions or [],
            data_context=response_message.data_context,
            chart_data=getattr(response_message, 'chart_data', None),
            timestamp=response_message.timestamp.isoformat()
        )

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    try:
        history = conversational_ai.get_conversation_history(session_id)

        history_data = []
        for message in history:
            history_data.append({
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "suggested_actions": message.suggested_actions,
                "data_context": message.data_context
            })

        return ConversationHistoryResponse(
            success=True,
            session_id=session_id,
            history=history_data
        )

    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat/clear/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history for a session"""
    try:
        success = conversational_ai.clear_conversation(session_id)

        return {
            "success": success,
            "message": f"Conversation {session_id} cleared successfully" if success else "Session not found"
        }

    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/insights/{session_id}")
async def get_proactive_insights(session_id: str):
    """Get proactive insights for a conversation session"""
    try:
        insights = conversational_ai.get_proactive_insights(session_id)

        return {
            "success": True,
            "session_id": session_id,
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting proactive insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Individual Module Endpoints

@app.get("/api/modules/incident-investigation/kpis", response_model=SummaryResponse)
async def get_incident_investigation_module_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    days_back: int = Query(365, description="Number of days to look back")
):
    """Get Incident Investigation module KPIs"""
    max_retries = 2
    retry_count = 0

    while retry_count <= max_retries:
        try:
            logger.info(f"Getting Incident Investigation KPIs for customer: {customer_id} (attempt {retry_count + 1})")

            # Validate database session before proceeding
            from config.database_config import db_manager
            if not db_manager.validate_session(summarizer_app.incident_extractor.db_session):
                logger.info("Database session validation failed, recreating session")
                summarizer_app.recreate_database_sessions()

            # Parse dates or use days_back
            if start_date and end_date:
                start_date_obj = datetime.fromisoformat(start_date)
                end_date_obj = datetime.fromisoformat(end_date)
            else:
                end_date_obj = datetime.now()
                start_date_obj = end_date_obj - timedelta(days=days_back)

            kpis = summarizer_app.incident_extractor.get_all_incident_kpis(
                customer_id=customer_id,
                start_date=start_date_obj,
                end_date=end_date_obj
            )

            return SummaryResponse(
                success=True,
                data=kpis,
                generated_at=datetime.now().isoformat()
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error getting incident investigation KPIs (attempt {retry_count + 1}): {error_msg}")

            # Check if it's a connection error and we can retry
            connection_indicators = [
                "server closed the connection",
                "connection unexpectedly",
                "can't reconnect until invalid transaction is rolled back",
                "connection lost",
                "connection refused",
                "connection timeout",
                "connection reset",
                "connection broken"
            ]

            is_connection_error = any(indicator in error_msg.lower() for indicator in connection_indicators)

            if is_connection_error and retry_count < max_retries:
                logger.info("Connection error detected, recreating database sessions")
                try:
                    # Recreate database sessions with enhanced cleanup
                    summarizer_app.recreate_database_sessions()
                    retry_count += 1
                    # Add a small delay before retry
                    import asyncio
                    await asyncio.sleep(1)
                    continue
                except Exception as recreate_error:
                    logger.error(f"Failed to recreate database sessions: {str(recreate_error)}")

            # If not a connection error or max retries reached, raise the exception
            raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/modules/risk-assessment/kpis", response_model=SummaryResponse)
async def get_risk_assessment_module_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(365, description="Number of days to look back")
):
    """Get Risk Assessment module KPIs"""
    try:
        logger.info(f"Getting Risk Assessment KPIs for customer: {customer_id}")

        kpis = summarizer_app.risk_assessment_extractor.get_risk_assessment_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=kpis,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error getting risk assessment KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/modules/action-tracking/kpis", response_model=SummaryResponse)
async def get_action_tracking_module_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    days_back: int = Query(365, description="Number of days to look back")
):
    """Get Action Tracking module KPIs with enhanced retry logic"""
    max_retries = 2
    retry_count = 0

    while retry_count <= max_retries:
        try:
            logger.info(f"Getting Action Tracking KPIs for customer: {customer_id} (attempt {retry_count + 1})")

            # Validate database session before proceeding
            from config.database_config import db_manager
            if not db_manager.validate_session(summarizer_app.action_extractor.db_session):
                logger.info("Database session validation failed, recreating session")
                summarizer_app.recreate_database_sessions()

            # Parse dates or use days_back
            if start_date and end_date:
                start_date_obj = datetime.fromisoformat(start_date)
                end_date_obj = datetime.fromisoformat(end_date)
            else:
                end_date_obj = datetime.now()
                start_date_obj = end_date_obj - timedelta(days=days_back)

            kpis = summarizer_app.action_extractor.get_all_action_tracking_kpis(
                customer_id=customer_id,
                start_date=start_date_obj,
                end_date=end_date_obj
            )

            return SummaryResponse(
                success=True,
                data=kpis,
                generated_at=datetime.now().isoformat()
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error getting action tracking KPIs (attempt {retry_count + 1}): {error_msg}")

            # Check if it's a connection error and we can retry
            connection_indicators = [
                "server closed the connection",
                "connection unexpectedly",
                "can't reconnect until invalid transaction is rolled back",
                "connection lost",
                "connection refused",
                "connection timeout",
                "connection reset",
                "connection broken"
            ]

            is_connection_error = any(indicator in error_msg.lower() for indicator in connection_indicators)

            if is_connection_error and retry_count < max_retries:
                logger.info("Connection error detected, recreating database sessions")
                try:
                    # Recreate database sessions with enhanced cleanup
                    summarizer_app.recreate_database_sessions()
                    retry_count += 1
                    # Add a small delay before retry
                    import asyncio
                    await asyncio.sleep(1)
                    continue
                except Exception as recreate_error:
                    logger.error(f"Failed to recreate database sessions: {str(recreate_error)}")

            # If not a connection error or max retries reached, raise the exception
            raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/modules/driver-safety/kpis", response_model=SummaryResponse)
async def get_driver_safety_module_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    days_back: int = Query(365, description="Number of days to look back")
):
    """Get Driver Safety module KPIs"""
    try:
        logger.info(f"Getting Driver Safety KPIs for customer: {customer_id}")

        # Parse date strings to datetime objects if provided
        parsed_start_date = None
        parsed_end_date = None

        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

        kpis = summarizer_app.driver_safety_extractor.get_driver_safety_checklist_kpis(
            customer_id=customer_id,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=kpis,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error getting driver safety KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/modules/observation-tracker/kpis", response_model=SummaryResponse)
async def get_observation_tracker_module_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    days_back: int = Query(365, description="Number of days to look back")
):
    """Get Observation Tracker module KPIs"""
    try:
        logger.info(f"Getting Observation Tracker KPIs for customer: {customer_id}")

        # Parse date strings to datetime objects if provided
        parsed_start_date = None
        parsed_end_date = None

        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

        kpis = summarizer_app.observation_tracker_extractor.get_observation_tracker_kpis(
            customer_id=customer_id,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=kpis,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error getting observation tracker KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/modules/equipment-asset/kpis", response_model=SummaryResponse)
async def get_equipment_asset_module_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(365, description="Number of days to look back")
):
    """Get Equipment Asset module KPIs"""
    try:
        logger.info(f"Getting Equipment Asset KPIs for customer: {customer_id}")

        kpis = summarizer_app.equipment_asset_extractor.get_equipment_asset_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=kpis,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error getting equipment asset KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/modules/employee-training/kpis", response_model=SummaryResponse)
async def get_employee_training_module_kpis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(365, description="Number of days to look back")
):
    """Get Employee Training module KPIs"""
    try:
        logger.info(f"Getting Employee Training KPIs for customer: {customer_id}")

        kpis = summarizer_app.employee_training_extractor.get_employee_training_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=kpis,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error getting employee training KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Analysis Endpoints for Individual Modules

class AIAnalysisResponse(BaseModel):
    success: bool
    module: str
    module_name: str
    dashboard_data: Dict[str, Any]
    ai_analysis: Optional[Dict[str, Any]] = None
    generated_at: str
    time_filter: Dict[str, Any]

@app.get("/ai-analysis/incident-investigation", response_model=AIAnalysisResponse)
async def get_incident_investigation_ai_analysis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back"),
    include_ai: bool = Query(True, description="Include AI analysis")
):
    """Get incident investigation data with optional AI analysis"""
    try:
        logger.info(f"Generating incident investigation analysis for customer: {customer_id}")

        # Get dashboard data
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        dashboard_data = summarizer_app.incident_extractor.get_all_incident_kpis(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )

        # Get AI analysis if requested
        ai_analysis = None
        if include_ai and summarizer_app.ai_engine.is_ai_available():
            ai_analysis = summarizer_app.ai_engine.generate_module_specific_analysis(
                dashboard_data, "incident_investigation"
            )

        return AIAnalysisResponse(
            success=True,
            module="incident_investigation",
            module_name="Incident Investigation",
            dashboard_data=dashboard_data,
            ai_analysis=ai_analysis,
            generated_at=datetime.now().isoformat(),
            time_filter={
                "days_back": days_back,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "customer_id": customer_id
            }
        )

    except Exception as e:
        logger.error(f"Error generating incident investigation analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai-analysis/action-tracking", response_model=AIAnalysisResponse)
async def get_action_tracking_ai_analysis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back"),
    include_ai: bool = Query(True, description="Include AI analysis")
):
    """Get action tracking data with optional AI analysis"""
    try:
        logger.info(f"Generating action tracking analysis for customer: {customer_id}")

        # Get dashboard data
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        dashboard_data = summarizer_app.action_extractor.get_all_action_tracking_kpis(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )

        # Get AI analysis if requested
        ai_analysis = None
        if include_ai and summarizer_app.ai_engine.is_ai_available():
            ai_analysis = summarizer_app.ai_engine.generate_module_specific_analysis(
                dashboard_data, "action_tracking"
            )

        return AIAnalysisResponse(
            success=True,
            module="action_tracking",
            module_name="Action Tracking",
            dashboard_data=dashboard_data,
            ai_analysis=ai_analysis,
            generated_at=datetime.now().isoformat(),
            time_filter={
                "days_back": days_back,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "customer_id": customer_id
            }
        )

    except Exception as e:
        logger.error(f"Error generating action tracking analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai-analysis/driver-safety-checklists", response_model=AIAnalysisResponse)
async def get_driver_safety_ai_analysis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back"),
    include_ai: bool = Query(True, description="Include AI analysis")
):
    """Get driver safety checklist data with optional AI analysis"""
    try:
        logger.info(f"Generating driver safety analysis for customer: {customer_id}")

        # Get dashboard data
        dashboard_data = summarizer_app.driver_safety_extractor.get_driver_safety_checklist_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        # Get AI analysis if requested
        ai_analysis = None
        if include_ai and summarizer_app.ai_engine.is_ai_available():
            ai_analysis = summarizer_app.ai_engine.generate_module_specific_analysis(
                dashboard_data, "driver_safety_checklists"
            )

        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        return AIAnalysisResponse(
            success=True,
            module="driver_safety_checklists",
            module_name="Driver Safety Checklists",
            dashboard_data=dashboard_data,
            ai_analysis=ai_analysis,
            generated_at=datetime.now().isoformat(),
            time_filter={
                "days_back": days_back,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "customer_id": customer_id
            }
        )

    except Exception as e:
        logger.error(f"Error generating driver safety analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai-analysis/observation-tracker", response_model=AIAnalysisResponse)
async def get_observation_tracker_ai_analysis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back"),
    include_ai: bool = Query(True, description="Include AI analysis")
):
    """Get observation tracker data with optional AI analysis"""
    try:
        logger.info(f"Generating observation tracker analysis for customer: {customer_id}")

        # Get dashboard data
        dashboard_data = summarizer_app.observation_tracker_extractor.get_observation_tracker_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        # Get AI analysis if requested
        ai_analysis = None
        if include_ai and summarizer_app.ai_engine.is_ai_available():
            ai_analysis = summarizer_app.ai_engine.generate_module_specific_analysis(
                dashboard_data, "observation_tracker"
            )

        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        return AIAnalysisResponse(
            success=True,
            module="observation_tracker",
            module_name="Observation Tracker",
            dashboard_data=dashboard_data,
            ai_analysis=ai_analysis,
            generated_at=datetime.now().isoformat(),
            time_filter={
                "days_back": days_back,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "customer_id": customer_id
            }
        )

    except Exception as e:
        logger.error(f"Error generating observation tracker analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai-analysis/equipment-asset-management", response_model=AIAnalysisResponse)
async def get_equipment_asset_ai_analysis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back"),
    include_ai: bool = Query(True, description="Include AI analysis")
):
    """Get equipment asset management data with optional AI analysis"""
    try:
        logger.info(f"Generating equipment asset analysis for customer: {customer_id}")

        # Get dashboard data
        dashboard_data = summarizer_app.equipment_asset_extractor.get_equipment_asset_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        # Get AI analysis if requested
        ai_analysis = None
        if include_ai and summarizer_app.ai_engine.is_ai_available():
            ai_analysis = summarizer_app.ai_engine.generate_module_specific_analysis(
                dashboard_data, "equipment_asset_management"
            )

        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        return AIAnalysisResponse(
            success=True,
            module="equipment_asset_management",
            module_name="Equipment Asset Management",
            dashboard_data=dashboard_data,
            ai_analysis=ai_analysis,
            generated_at=datetime.now().isoformat(),
            time_filter={
                "days_back": days_back,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "customer_id": customer_id
            }
        )

    except Exception as e:
        logger.error(f"Error generating equipment asset analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai-analysis/employee-training-fitness", response_model=AIAnalysisResponse)
async def get_employee_training_ai_analysis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(365, description="Number of days to look back"),
    include_ai: bool = Query(True, description="Include AI analysis")
):
    """Get employee training and fitness data with optional AI analysis"""
    try:
        logger.info(f"Generating employee training analysis for customer: {customer_id}")

        # Get dashboard data
        dashboard_data = summarizer_app.employee_training_extractor.get_employee_training_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        # Get AI analysis if requested
        ai_analysis = None
        if include_ai and summarizer_app.ai_engine.is_ai_available():
            ai_analysis = summarizer_app.ai_engine.generate_module_specific_analysis(
                dashboard_data, "employee_training_fitness"
            )

        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        return AIAnalysisResponse(
            success=True,
            module="employee_training_fitness",
            module_name="Employee Training & Fitness",
            dashboard_data=dashboard_data,
            ai_analysis=ai_analysis,
            generated_at=datetime.now().isoformat(),
            time_filter={
                "days_back": days_back,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "customer_id": customer_id
            }
        )

    except Exception as e:
        logger.error(f"Error generating employee training analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai-analysis/risk-assessment", response_model=AIAnalysisResponse)
async def get_risk_assessment_ai_analysis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(365, description="Number of days to look back"),
    include_ai: bool = Query(True, description="Include AI analysis")
):
    """Get risk assessment data with optional AI analysis"""
    try:
        logger.info(f"Generating risk assessment analysis for customer: {customer_id}")

        # Get dashboard data
        dashboard_data = summarizer_app.risk_assessment_extractor.get_risk_assessment_kpis(
            customer_id=customer_id,
            days_back=days_back
        )

        # Get AI analysis if requested
        ai_analysis = None
        if include_ai and summarizer_app.ai_engine.is_ai_available():
            ai_analysis = summarizer_app.ai_engine.generate_module_specific_analysis(
                dashboard_data, "risk_assessment"
            )

        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        return AIAnalysisResponse(
            success=True,
            module="risk_assessment",
            module_name="Risk Assessment",
            dashboard_data=dashboard_data,
            ai_analysis=ai_analysis,
            generated_at=datetime.now().isoformat(),
            time_filter={
                "days_back": days_back,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "customer_id": customer_id
            }
        )

    except Exception as e:
        logger.error(f"Error generating risk assessment analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai-analysis/comprehensive")
async def get_comprehensive_ai_analysis(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back"),
    include_ai: bool = Query(True, description="Include AI analysis"),
    modules: Optional[str] = Query("all", description="Comma-separated list of modules or 'all'")
):
    """Get comprehensive analysis across all or selected modules"""
    try:
        logger.info(f"Generating comprehensive analysis for customer: {customer_id}")

        # Parse modules parameter
        if modules == "all":
            selected_modules = ["incident_investigation", "action_tracking", "driver_safety_checklists", "observation_tracker", "equipment_asset_management", "employee_training_fitness", "risk_assessment"]
        else:
            selected_modules = [m.strip() for m in modules.split(",")]

        # Get dashboard data for all selected modules
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        all_dashboard_data = {}

        if "incident_investigation" in selected_modules:
            all_dashboard_data["incident_investigation"] = summarizer_app.incident_extractor.get_all_incident_kpis(
                customer_id=customer_id, start_date=start_date, end_date=end_date
            )

        if "action_tracking" in selected_modules:
            all_dashboard_data["action_tracking"] = summarizer_app.action_extractor.get_all_action_tracking_kpis(
                customer_id=customer_id, start_date=start_date, end_date=end_date
            )

        if "driver_safety_checklists" in selected_modules:
            all_dashboard_data["driver_safety_checklists"] = summarizer_app.driver_safety_extractor.get_driver_safety_checklist_kpis(
                customer_id=customer_id, days_back=days_back
            )

        if "observation_tracker" in selected_modules:
            all_dashboard_data["observation_tracker"] = summarizer_app.observation_tracker_extractor.get_observation_tracker_kpis(
                customer_id=customer_id, days_back=days_back
            )

        if "equipment_asset_management" in selected_modules:
            all_dashboard_data["equipment_asset_management"] = summarizer_app.equipment_asset_extractor.get_equipment_asset_kpis(
                customer_id=customer_id, days_back=days_back
            )

        if "employee_training_fitness" in selected_modules:
            all_dashboard_data["employee_training_fitness"] = summarizer_app.employee_training_extractor.get_employee_training_kpis(
                customer_id=customer_id, days_back=days_back
            )

        if "risk_assessment" in selected_modules:
            all_dashboard_data["risk_assessment"] = summarizer_app.risk_assessment_extractor.get_risk_assessment_kpis(
                customer_id=customer_id, days_back=days_back
            )

        # Get comprehensive AI analysis if requested
        comprehensive_ai_analysis = None
        if include_ai and summarizer_app.ai_engine.is_ai_available():
            comprehensive_ai_analysis = summarizer_app.ai_engine.generate_comprehensive_summary(all_dashboard_data)

        return {
            "success": True,
            "analysis_type": "comprehensive",
            "modules_analyzed": selected_modules,
            "dashboard_data": all_dashboard_data,
            "ai_analysis": comprehensive_ai_analysis,
            "generated_at": datetime.now().isoformat(),
            "time_filter": {
                "days_back": days_back,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "customer_id": customer_id
            },
            "metadata": {
                "modules_count": len(selected_modules),
                "ai_enabled": include_ai,
                "ai_available": summarizer_app.ai_engine.is_ai_available()
            }
        }

    except Exception as e:
        logger.error(f"Error generating comprehensive analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Analysis Status and Configuration Endpoints

@app.get("/ai-analysis/status")
async def get_ai_analysis_status():
    """Get AI analysis system status"""
    try:
        return {
            "success": True,
            "ai_available": summarizer_app.ai_engine.is_ai_available(),
            "supported_modules": summarizer_app.ai_engine.get_supported_modules(),
            "cache_stats": summarizer_app.ai_engine.get_cache_stats(),
            "system_info": {
                "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
                "analysis_capabilities": [
                    "module_specific_analysis",
                    "comprehensive_analysis",
                    "time_filtering",
                    "caching"
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error getting AI analysis status: {str(e)}")
        return {
            "success": False,
            "ai_available": False,
            "error": str(e)
        }

@app.post("/dashboard/save", response_model=DashboardConfigResponse)
async def save_dashboard_config(request: DashboardConfigRequest):
    """Save dashboard configuration"""
    try:
        # For now, save to a simple file-based storage
        # In production, this would be saved to a database
        import json
        import os
        from datetime import datetime

        dashboard_id = f"{request.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create dashboards directory if it doesn't exist
        dashboards_dir = "dashboards"
        if not os.path.exists(dashboards_dir):
            os.makedirs(dashboards_dir)

        # Save dashboard configuration
        config = {
            "dashboard_id": dashboard_id,
            "dashboard_name": request.dashboard_name,
            "user_id": request.user_id,
            "charts": request.charts,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        config_path = os.path.join(dashboards_dir, f"{dashboard_id}.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        return DashboardConfigResponse(
            success=True,
            dashboard_id=dashboard_id,
            message="Dashboard saved successfully"
        )

    except Exception as e:
        logger.error(f"Error saving dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/load/{dashboard_id}")
async def load_dashboard_config(dashboard_id: str):
    """Load dashboard configuration"""
    try:
        import json
        import os

        config_path = os.path.join("dashboards", f"{dashboard_id}.json")

        if not os.path.exists(config_path):
            raise HTTPException(status_code=404, detail="Dashboard not found")

        with open(config_path, 'r') as f:
            config = json.load(f)

        return {
            "success": True,
            "data": config
        }

    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/list")
async def list_dashboards(user_id: Optional[str] = Query("anonymous", description="User ID filter")):
    """List all dashboards for a user"""
    try:
        import json
        import os

        dashboards_dir = "dashboards"
        if not os.path.exists(dashboards_dir):
            return {"success": True, "data": []}

        dashboards = []
        for filename in os.listdir(dashboards_dir):
            if filename.endswith('.json'):
                config_path = os.path.join(dashboards_dir, filename)
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)

                    # Filter by user_id if specified
                    if user_id == "all" or config.get("user_id") == user_id:
                        dashboards.append({
                            "dashboard_id": config.get("dashboard_id"),
                            "dashboard_name": config.get("dashboard_name"),
                            "user_id": config.get("user_id"),
                            "chart_count": len(config.get("charts", [])),
                            "created_at": config.get("created_at"),
                            "updated_at": config.get("updated_at")
                        })
                except Exception as e:
                    logger.warning(f"Error reading dashboard config {filename}: {str(e)}")
                    continue

        # Sort by updated_at descending
        dashboards.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

        return {
            "success": True,
            "data": dashboards
        }

    except Exception as e:
        logger.error(f"Error listing dashboards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Insights Feedback Endpoint
@app.post("/ai-analysis/feedback")
async def submit_insight_feedback(feedback_data: dict):
    """Submit feedback for AI insights and get additional insights based on feedback"""
    try:
        logger.info(f"📝 Received insight feedback: {feedback_data}")

        module = feedback_data.get('module')
        insight_text = feedback_data.get('insight_text')
        feedback_type = feedback_data.get('feedback_type')  # 'positive' or 'negative'

        # Store feedback (in a real implementation, you'd store this in a database)
        # For now, we'll just log it and generate additional insights based on positive feedback

        additional_insights = []

        if feedback_type == 'positive':
            # Generate more insights similar to the positively rated one
            logger.info(f"✅ Positive feedback for insight: {insight_text}")

            # Use AI to generate similar insights based on the positively rated insight
            try:
                similar_insights = await generate_similar_insights(module, insight_text)
                additional_insights.extend(similar_insights)
            except Exception as e:
                logger.warning(f"Could not generate similar insights: {str(e)}")

        elif feedback_type == 'negative':
            # Log negative feedback for future improvement
            logger.info(f"❌ Negative feedback for insight: {insight_text}")
            # In a real implementation, you might use this to improve the AI model

        return {
            "success": True,
            "message": f"Feedback received for {feedback_type} rating",
            "additional_insights": additional_insights,
            "feedback_stored": True
        }

    except Exception as e:
        logger.error(f"Error processing insight feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_similar_insights(module: str, positive_insight: str):
    """Generate additional insights similar to a positively rated insight"""
    try:
        # Use the AI engine to generate similar insights
        if not summarizer_app.ai_engine.is_ai_available():
            return []

        # Create a prompt to generate similar insights
        prompt = f"""
        Based on this positively rated safety insight for the {module} module:
        "{positive_insight}"

        Generate 2-3 additional similar insights that would be valuable for safety management.
        Focus on the same type of analysis and provide actionable insights.

        Return only the insights as a JSON array of objects with 'text' and 'sentiment' fields.
        Example: [{"text": "insight text", "sentiment": "positive"}]
        """

        # Call OpenAI to generate similar insights
        response = await summarizer_app.ai_engine.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a safety analysis expert. Generate concise, actionable safety insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        # Parse the response
        import json
        insights_text = response.choices[0].message.content.strip()

        # Try to parse as JSON
        try:
            insights_json = json.loads(insights_text)
            if isinstance(insights_json, list):
                return insights_json
        except:
            # If JSON parsing fails, create insights from the text
            return [{"text": insights_text, "sentiment": "positive"}]

    except Exception as e:
        logger.error(f"Error generating similar insights: {str(e)}")
        return []

# Generate More Insights Endpoint
@app.post("/ai-analysis/generate-more")
async def generate_more_insights(request_data: dict):
    """Generate additional data-driven insights based on actual module data"""
    try:
        logger.info(f"🔄 Generating more data-driven insights: {request_data}")

        module = request_data.get('module')
        existing_insights = request_data.get('existing_insights', [])
        positive_examples = request_data.get('positive_examples', [])
        count = request_data.get('count', 5)

        if not module:
            raise HTTPException(status_code=400, detail="Module is required")

        # Get fresh module data for analysis
        module_data = await get_module_data_for_insights(module)

        # Generate new insights using actual data
        new_insights = await generate_data_driven_insights(
            module, module_data, existing_insights, positive_examples, count
        )

        return {
            "success": True,
            "additional_insights": new_insights,
            "count": len(new_insights),
            "message": f"Generated {len(new_insights)} data-driven insights for {module}"
        }

    except Exception as e:
        logger.error(f"Error generating more insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_module_data_for_insights(module: str):
    """Get fresh module data for generating insights"""
    try:
        from datetime import datetime, timedelta

        if module == 'incident-investigation':
            # Use the correct method name: get_all_incident_kpis
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            return summarizer_app.incident_extractor.get_all_incident_kpis(
                customer_id=None, start_date=start_date, end_date=end_date
            )
        elif module == 'action-tracking':
            # Use the correct method name: get_all_action_tracking_kpis
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            return summarizer_app.action_extractor.get_all_action_tracking_kpis(
                customer_id=None, start_date=start_date, end_date=end_date
            )
        elif module == 'driver-safety':
            # Use the correct method name: get_driver_safety_checklist_kpis
            return summarizer_app.driver_safety_extractor.get_driver_safety_checklist_kpis(
                customer_id=None, days_back=30
            )
        elif module == 'observation-tracker':
            # Use the correct method name: get_observation_tracker_kpis
            return summarizer_app.observation_tracker_extractor.get_observation_tracker_kpis(
                customer_id=None, days_back=30
            )
        elif module == 'equipment-asset':
            # Use the correct method name: get_equipment_asset_kpis
            return summarizer_app.equipment_asset_extractor.get_equipment_asset_kpis(
                customer_id=None, days_back=30
            )
        elif module == 'employee-training':
            # Use the correct method name: get_employee_training_kpis
            return summarizer_app.employee_training_extractor.get_employee_training_kpis(
                customer_id=None, days_back=365
            )
        elif module == 'risk-assessment':
            # Use the correct method name: get_risk_assessment_kpis
            return summarizer_app.risk_assessment_extractor.get_risk_assessment_kpis(
                customer_id=None, days_back=30
            )
        else:
            return None
    except Exception as e:
        logger.error(f"Error getting module data for {module}: {str(e)}")
        return None

async def generate_data_driven_insights(module: str, module_data: dict, existing_insights: list, positive_examples: list, count: int = 5):
    """Generate insights based on actual module data analysis"""
    try:
        if not module_data:
            logger.warning(f"No module data available for {module}, using fallback")
            return generate_fallback_additional_insights(module, count)

        if not summarizer_app.ai_engine.is_ai_available():
            return generate_data_driven_fallback_insights(module, module_data, count)

        # Extract key data points for analysis
        data_summary = extract_data_points_for_analysis(module, module_data)

        # Create existing insights text
        existing_text = "\n".join([f"- {insight}" for insight in existing_insights])
        positive_text = "\n".join([f"- {insight}" for insight in positive_examples]) if positive_examples else "None provided"

        prompt = f"""
        Analyze the following REAL DATA from the {module.replace('-', ' ').title()} module and generate {count} NEW data-driven insights.

        ACTUAL DATA TO ANALYZE:
        {data_summary}

        EXISTING INSIGHTS (DO NOT DUPLICATE):
        {existing_text}

        POSITIVELY RATED INSIGHTS (use similar analytical style):
        {positive_text}

        Requirements:
        1. Generate exactly {count} NEW insights based ONLY on the actual data provided
        2. Focus on data patterns, trends, and specific numbers
        3. Do NOT make generic recommendations
        4. Analyze what the data reveals about performance, trends, or issues
        5. Include specific metrics and percentages where relevant
        6. Do NOT duplicate any existing insights
        7. Each insight should reveal something specific about the data

        Examples of good data-driven insights:
        - "Department X shows 40% higher incident rate compared to average"
        - "Response time increased by 25% in the last month compared to previous period"
        - "Location Y accounts for 60% of all safety observations"

        Return as JSON array: [{{"text": "specific data insight", "sentiment": "positive/negative/neutral"}}]
        """

        response = summarizer_app.ai_engine.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data analyst specializing in safety metrics. Generate insights based ONLY on the actual data provided, not generic recommendations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7  # Moderate temperature for focused analysis
        )

        # Parse and filter response
        import json
        insights_text = response.choices[0].message.content.strip()

        try:
            # Clean the response text
            insights_text = insights_text.strip()
            if insights_text.startswith('```json'):
                insights_text = insights_text.replace('```json', '').replace('```', '').strip()

            logger.info(f"Parsing data-driven AI response: {insights_text[:200]}...")

            insights_json = json.loads(insights_text)
            if isinstance(insights_json, list):
                filtered_insights = []
                for insight in insights_json:
                    if isinstance(insight, dict):
                        insight_text = insight.get('text', '').strip()
                        sentiment = insight.get('sentiment', 'neutral')

                        # Check for duplicates
                        is_duplicate = any(
                            insight_text.lower() in existing.lower() or existing.lower() in insight_text.lower()
                            for existing in existing_insights
                        )
                        if not is_duplicate and insight_text and len(filtered_insights) < count:
                            filtered_insights.append({
                                "text": insight_text,
                                "sentiment": sentiment
                            })

                logger.info(f"Generated {len(filtered_insights)} data-driven insights")
                return filtered_insights

        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {str(e)}, using fallback")
            return generate_data_driven_fallback_insights(module, module_data, count)

    except Exception as e:
        logger.error(f"Error generating data-driven insights: {str(e)}")
        return generate_data_driven_fallback_insights(module, module_data, count)

def extract_data_points_for_analysis(module: str, module_data: dict):
    """Extract key data points from module data for AI analysis"""
    try:
        data_points = []

        if module == 'incident-investigation':
            # Extract incident-specific data using correct field names
            if 'incidents_reported' in module_data:
                data_points.append(f"Total incidents reported: {module_data['incidents_reported']}")
            if 'open_incidents' in module_data:
                data_points.append(f"Open incidents: {module_data['open_incidents']}")
            if 'closed_incidents' in module_data:
                data_points.append(f"Closed incidents: {module_data['closed_incidents']}")
            if 'investigation_completion_time_mins' in module_data:
                hours = round(module_data['investigation_completion_time_mins'] / 60, 1)
                data_points.append(f"Average investigation completion time: {hours} hours ({module_data['investigation_completion_time_mins']} minutes)")
            if 'incidents_by_location' in module_data:
                for location, count in module_data['incidents_by_location'].items():
                    data_points.append(f"Incidents at {location}: {count}")
            if 'incident_types' in module_data:
                for incident_type, count in module_data['incident_types'].items():
                    data_points.append(f"{incident_type} incidents: {count}")
            if 'people_injured' in module_data:
                data_points.append(f"People injured: {module_data['people_injured']}")
            if 'actions_created' in module_data:
                data_points.append(f"Actions created: {module_data['actions_created']}")
            if 'open_actions_percentage' in module_data:
                data_points.append(f"Open actions percentage: {module_data['open_actions_percentage']}%")
            if 'days_since_last_incident' in module_data:
                data_points.append(f"Days since last incident: {module_data['days_since_last_incident']}")

        elif module == 'action-tracking':
            # Extract action tracking data using correct field names
            if 'actions_created' in module_data:
                actions_data = module_data['actions_created']
                if isinstance(actions_data, dict):
                    if 'total_actions' in actions_data:
                        data_points.append(f"Total actions created: {actions_data['total_actions']}")
                    if 'actions_this_period' in actions_data:
                        data_points.append(f"Actions created this period: {actions_data['actions_this_period']}")

            if 'on_time_completion' in module_data:
                completion_data = module_data['on_time_completion']
                if isinstance(completion_data, dict):
                    if 'on_time_percentage' in completion_data:
                        data_points.append(f"On-time completion rate: {completion_data['on_time_percentage']}%")
                    if 'late_actions' in completion_data:
                        data_points.append(f"Late actions: {completion_data['late_actions']}")

            if 'action_status' in module_data:
                status_data = module_data['action_status']
                if isinstance(status_data, dict):
                    if 'open_actions' in status_data:
                        data_points.append(f"Open actions: {status_data['open_actions']}")
                    if 'closed_actions' in status_data:
                        data_points.append(f"Closed actions: {status_data['closed_actions']}")
                    if 'in_progress_actions' in status_data:
                        data_points.append(f"In progress actions: {status_data['in_progress_actions']}")

            if 'overdue_employees' in module_data:
                overdue_data = module_data['overdue_employees']
                if isinstance(overdue_data, dict) and 'overdue_count' in overdue_data:
                    data_points.append(f"Employees with overdue actions: {overdue_data['overdue_count']}")

        elif module == 'driver-safety':
            # Extract driver safety data
            if 'daily_completions' in module_data:
                daily_data = module_data['daily_completions']
                if isinstance(daily_data, dict):
                    if 'total_completed_checklists' in daily_data:
                        data_points.append(f"Daily checklists completed: {daily_data['total_completed_checklists']}")
                    if 'completion_percentage' in daily_data:
                        data_points.append(f"Daily completion rate: {daily_data['completion_percentage']}%")

            if 'vehicle_fitness' in module_data:
                fitness_data = module_data['vehicle_fitness']
                if isinstance(fitness_data, dict):
                    if 'unfit_vehicles' in fitness_data:
                        data_points.append(f"Vehicles deemed unfit: {fitness_data['unfit_vehicles']}")

        # If no specific data found, extract general metrics
        if not data_points:
            logger.info(f"No specific extraction for {module}, using general extraction")
            for key, value in module_data.items():
                if isinstance(value, (int, float)):
                    data_points.append(f"{key.replace('_', ' ').title()}: {value}")
                elif isinstance(value, dict) and len(value) < 10:  # Small dictionaries
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, (int, float, str)):
                            data_points.append(f"{sub_key}: {sub_value}")

        result = "\n".join(data_points[:25])  # Increased limit for more data
        logger.info(f"Extracted data points for {module}: {result[:200]}...")
        return result

    except Exception as e:
        logger.error(f"Error extracting data points: {str(e)}")
        return "No specific data available for analysis"

def generate_data_driven_fallback_insights(module: str, module_data: dict, count: int = 5):
    """Generate fallback insights based on actual data when AI is not available"""
    try:
        insights = []

        if module == 'incident-investigation' and module_data:
            if 'total_incidents' in module_data:
                total = module_data['total_incidents']
                insights.append({"text": f"Total incident count of {total} indicates current safety performance level", "sentiment": "neutral"})

            if 'open_incidents' in module_data and 'total_incidents' in module_data:
                open_count = module_data['open_incidents']
                total = module_data['total_incidents']
                if total > 0:
                    percentage = round((open_count / total) * 100, 1)
                    sentiment = "negative" if percentage > 50 else "neutral"
                    insights.append({"text": f"{percentage}% of incidents remain open ({open_count} out of {total})", "sentiment": sentiment})

            if 'incidents_by_location' in module_data:
                locations = module_data['incidents_by_location']
                if locations:
                    max_location = max(locations.items(), key=lambda x: x[1])
                    insights.append({"text": f"{max_location[0]} has the highest incident count with {max_location[1]} incidents", "sentiment": "negative"})

        # Add more module-specific fallback logic here

        return insights[:count]

    except Exception as e:
        logger.error(f"Error generating data-driven fallback: {str(e)}")
        return [{"text": "Unable to analyze current data", "sentiment": "neutral"}]

async def generate_additional_insights(module: str, existing_insights: list, positive_examples: list, count: int = 5):
    """Generate additional insights avoiding duplicates and considering positive feedback"""
    try:
        if not summarizer_app.ai_engine.is_ai_available():
            # Return fallback insights if AI is not available
            return generate_fallback_additional_insights(module, count)

        # Create a comprehensive prompt
        existing_text = "\n".join([f"- {insight}" for insight in existing_insights])
        positive_text = "\n".join([f"- {insight}" for insight in positive_examples]) if positive_examples else "None provided"

        prompt = f"""
        Generate {count} NEW safety insights for the {module.replace('-', ' ').title()} module.

        EXISTING INSIGHTS (DO NOT DUPLICATE):
        {existing_text}

        POSITIVELY RATED INSIGHTS (use as style examples):
        {positive_text}

        Requirements:
        1. Generate exactly {count} completely NEW insights
        2. Do NOT duplicate any existing insights
        3. Focus on actionable safety recommendations
        4. If positive examples exist, follow their style and depth
        5. Each insight should be specific and valuable
        6. Include sentiment analysis (positive/negative/neutral)

        Return as JSON array with this exact format:
        [{{"text": "insight text here", "sentiment": "positive"}}, {{"text": "another insight", "sentiment": "negative"}}]
        """

        response = summarizer_app.ai_engine.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a safety analysis expert. Generate unique, actionable safety insights without duplicating existing ones."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.8  # Higher temperature for more variety
        )

        # Parse the response
        import json
        insights_text = response.choices[0].message.content.strip()

        try:
            # Clean the response text first
            insights_text = insights_text.strip()
            if insights_text.startswith('```json'):
                insights_text = insights_text.replace('```json', '').replace('```', '').strip()

            logger.info(f"Attempting to parse AI response: {insights_text[:200]}...")

            insights_json = json.loads(insights_text)
            if isinstance(insights_json, list):
                # Filter out any potential duplicates
                filtered_insights = []
                for insight in insights_json:
                    if isinstance(insight, dict):
                        insight_text = insight.get('text', '').strip()
                        sentiment = insight.get('sentiment', 'neutral')

                        # Check for duplicates (case-insensitive, basic similarity)
                        is_duplicate = any(
                            insight_text.lower() in existing.lower() or existing.lower() in insight_text.lower()
                            for existing in existing_insights
                        )
                        if not is_duplicate and insight_text and len(filtered_insights) < count:
                            filtered_insights.append({
                                "text": insight_text,
                                "sentiment": sentiment
                            })

                logger.info(f"Successfully generated {len(filtered_insights)} unique insights")
                return filtered_insights

        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {str(e)}, attempting text extraction")
            # If JSON parsing fails, try to extract insights from text
            lines = insights_text.split('\n')
            insights = []
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*') or line.startswith('1.') or line.startswith('2.')):
                    clean_text = line.lstrip('-•*123456789. ').strip()
                    if clean_text and len(insights) < count:
                        # Check for duplicates
                        is_duplicate = any(
                            clean_text.lower() in existing.lower() or existing.lower() in clean_text.lower()
                            for existing in existing_insights
                        )
                        if not is_duplicate:
                            insights.append({"text": clean_text, "sentiment": "neutral"})

            logger.info(f"Extracted {len(insights)} insights from text format")
            return insights

    except Exception as e:
        logger.error(f"Error generating additional insights with AI: {str(e)}")
        return generate_fallback_additional_insights(module, count)

def generate_fallback_additional_insights(module: str, count: int = 5):
    """Generate fallback insights when AI is not available"""
    fallback_insights = {
        'incident-investigation': [
            {"text": "Implement predictive analytics to identify incident patterns before they occur", "sentiment": "positive"},
            {"text": "Establish cross-departmental incident review committees for comprehensive analysis", "sentiment": "positive"},
            {"text": "Develop mobile incident reporting apps for real-time data collection", "sentiment": "positive"},
            {"text": "Create incident severity scoring systems for better resource allocation", "sentiment": "neutral"},
            {"text": "Regular training on root cause analysis techniques shows measurable improvement", "sentiment": "positive"}
        ],
        'action-tracking': [
            {"text": "Automated reminder systems increase action completion rates by 35%", "sentiment": "positive"},
            {"text": "Visual progress dashboards improve team accountability and transparency", "sentiment": "positive"},
            {"text": "Integration with calendar systems ensures timely action execution", "sentiment": "positive"},
            {"text": "Escalation protocols for overdue actions need clearer definition", "sentiment": "negative"},
            {"text": "Regular action effectiveness reviews help optimize future planning", "sentiment": "positive"}
        ],
        'driver-safety': [
            {"text": "Telematics data integration provides real-time driver behavior insights", "sentiment": "positive"},
            {"text": "Gamification of safety metrics increases driver engagement significantly", "sentiment": "positive"},
            {"text": "Regular vehicle maintenance schedules reduce safety incidents by 40%", "sentiment": "positive"},
            {"text": "Driver fatigue monitoring systems show promising early results", "sentiment": "positive"},
            {"text": "Weather-based driving alerts help prevent weather-related incidents", "sentiment": "positive"}
        ],
        'observation-tracker': [
            {"text": "Digital observation forms reduce data entry errors by 60%", "sentiment": "positive"},
            {"text": "Photo documentation enhances observation quality and follow-up actions", "sentiment": "positive"},
            {"text": "Trend analysis of observations reveals systemic safety improvements", "sentiment": "positive"},
            {"text": "Observer training programs improve observation accuracy and consistency", "sentiment": "positive"},
            {"text": "Real-time observation sharing enables immediate corrective actions", "sentiment": "positive"}
        ],
        'equipment-asset': [
            {"text": "Predictive maintenance reduces equipment failures by 45%", "sentiment": "positive"},
            {"text": "IoT sensors provide continuous equipment health monitoring", "sentiment": "positive"},
            {"text": "Digital asset registers improve maintenance scheduling efficiency", "sentiment": "positive"},
            {"text": "Equipment lifecycle analysis optimizes replacement planning", "sentiment": "positive"},
            {"text": "Maintenance cost tracking reveals opportunities for process improvement", "sentiment": "positive"}
        ],
        'employee-training': [
            {"text": "VR-based safety training shows 70% better retention rates", "sentiment": "positive"},
            {"text": "Microlearning modules improve training completion rates significantly", "sentiment": "positive"},
            {"text": "Competency-based assessments ensure practical skill development", "sentiment": "positive"},
            {"text": "Regular refresher training maintains high safety awareness levels", "sentiment": "positive"},
            {"text": "Peer-to-peer training programs enhance knowledge sharing", "sentiment": "positive"}
        ],
        'risk-assessment': [
            {"text": "Dynamic risk assessment tools adapt to changing work conditions", "sentiment": "positive"},
            {"text": "Risk heat maps provide visual representation of workplace hazards", "sentiment": "positive"},
            {"text": "Collaborative risk assessments improve hazard identification accuracy", "sentiment": "positive"},
            {"text": "Regular risk review cycles ensure assessments remain current", "sentiment": "positive"},
            {"text": "Integration with incident data enhances risk prediction capabilities", "sentiment": "positive"}
        ]
    }

    module_insights = fallback_insights.get(module, fallback_insights['incident-investigation'])
    return module_insights[:count]

@app.get("/cache/stats")
async def get_cache_statistics():
    """Get AI response cache statistics"""
    try:
        stats = ai_cache.get_stats()
        return {
            "success": True,
            "data": stats,
            "message": f"Cache hit rate: {stats['hit_rate_percent']}% - {stats['api_calls_saved']} API calls saved"
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return {
            "success": False,
            "data": {},
            "message": "Cache statistics unavailable"
        }

@app.post("/cache/clear")
async def clear_cache(pattern: Optional[str] = Query(None, description="Pattern to match for selective clearing")):
    """Clear AI response cache"""
    try:
        if pattern:
            ai_cache.invalidate_pattern(pattern)
            return {
                "success": True,
                "message": f"Cache entries matching '{pattern}' cleared"
            }
        else:
            ai_cache.clear()
            return {
                "success": True,
                "message": "All cache entries cleared"
            }
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return {
            "success": False,
            "message": "Failed to clear cache"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
