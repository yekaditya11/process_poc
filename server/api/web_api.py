"""
Web API for AI Safety Summarizer
Provides REST API endpoints for accessing safety summaries
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import json
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_app import SafetySummarizerApp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Safety Summarizer API",
    description="AI-powered safety management summarization system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins for development
        "https://dbm9gfecpk1ba.cloudfront.net",  # CloudFront distribution
        "http://localhost:3000",  # Local development
        "http://localhost:3001",  # Alternative local port
        "http://127.0.0.1:3000",  # Local development alternative
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
)

# Global app instance
summarizer_app = None

# Pydantic models for request/response
class SummaryRequest(BaseModel):
    customer_id: Optional[str] = None
    days_back: int = 30
    include_raw_data: bool = False

class ModuleSummaryRequest(BaseModel):
    module: str
    customer_id: Optional[str] = None
    days_back: int = 30

class SummaryResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    generated_at: str

@app.on_event("startup")
async def startup_event():
    """Initialize the summarizer app on startup"""
    global summarizer_app
    try:
        logger.info("Initializing AI Safety Summarizer...")
        summarizer_app = SafetySummarizerApp()
        logger.info("AI Safety Summarizer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize summarizer app: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    global summarizer_app
    if summarizer_app:
        summarizer_app.close()
        logger.info("AI Safety Summarizer closed")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "AI Safety Summarizer API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/summary/comprehensive", response_model=SummaryResponse)
async def generate_comprehensive_summary(request: SummaryRequest):
    """
    Generate comprehensive safety summary across all modules
    """
    try:
        logger.info(f"Generating comprehensive summary for customer: {request.customer_id}")

        result = summarizer_app.generate_comprehensive_summary(
            customer_id=request.customer_id,
            days_back=request.days_back,
            include_raw_data=request.include_raw_data
        )

        return SummaryResponse(
            success=True,
            data=result,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating comprehensive summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summary/module", response_model=SummaryResponse)
async def generate_module_summary(request: ModuleSummaryRequest):
    """
    Generate summary for a specific module
    """
    try:
        logger.info(f"Generating module summary for: {request.module}")

        result = summarizer_app.generate_module_summary(
            module=request.module,
            customer_id=request.customer_id,
            days_back=request.days_back
        )

        return SummaryResponse(
            success=True,
            data=result,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating module summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard", response_model=SummaryResponse)
async def get_dashboard_data(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(7, description="Number of days to look back")
):
    """
    Get quick dashboard data for real-time monitoring
    """
    try:
        logger.info(f"Generating dashboard data for customer: {customer_id}")

        result = summarizer_app.get_quick_dashboard_data(customer_id=customer_id, days_back=days_back)

        return SummaryResponse(
            success=True,
            data=result,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary/permit", response_model=SummaryResponse)
async def get_permit_summary(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back")
):
    """Get permit to work summary"""
    try:
        result = summarizer_app.generate_module_summary(
            module="permit",
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=result,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating permit summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary/incident", response_model=SummaryResponse)
async def get_incident_summary(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back")
):
    """Get incident management summary"""
    try:
        result = summarizer_app.generate_module_summary(
            module="incident",
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=result,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating incident summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary/action", response_model=SummaryResponse)
async def get_action_summary(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back")
):
    """Get action tracking summary"""
    try:
        result = summarizer_app.generate_module_summary(
            module="action",
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=result,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating action summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary/inspection", response_model=SummaryResponse)
async def get_inspection_summary(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back")
):
    """Get inspection tracking summary"""
    try:
        result = summarizer_app.generate_module_summary(
            module="inspection",
            customer_id=customer_id,
            days_back=days_back
        )

        return SummaryResponse(
            success=True,
            data=result,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating inspection summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/kpi", response_model=SummaryResponse)
async def get_kpi_metrics(
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    days_back: int = Query(30, description="Number of days to look back")
):
    """Get key performance indicators across all modules with trend analysis"""
    try:
        # Get current period data
        permit_data = summarizer_app.permit_extractor.get_permit_summary_data(customer_id, days_back)
        incident_data = summarizer_app.incident_extractor.get_incident_summary_data(customer_id, days_back)
        action_data = summarizer_app.action_extractor.get_action_summary_data(customer_id, days_back)
        inspection_data = summarizer_app.inspection_extractor.get_inspection_summary_data(customer_id, days_back)

        # Get previous period data for trend calculation
        previous_permit_data = summarizer_app.permit_extractor.get_permit_summary_data(customer_id, days_back * 2)
        previous_incident_data = summarizer_app.incident_extractor.get_incident_summary_data(customer_id, days_back * 2)
        previous_action_data = summarizer_app.action_extractor.get_action_summary_data(customer_id, days_back * 2)
        previous_inspection_data = summarizer_app.inspection_extractor.get_inspection_summary_data(customer_id, days_back * 2)

        # Helper function to calculate trend percentage
        def calculate_trend(current_value, previous_value):
            if previous_value == 0:
                return 0 if current_value == 0 else 100
            return round(((current_value - previous_value) / previous_value) * 100, 1)

        # Calculate trends
        permit_completion_trend = calculate_trend(
            permit_data["permit_statistics"]["completion_rate"],
            previous_permit_data["permit_statistics"]["completion_rate"]
        )

        incident_count_trend = calculate_trend(
            incident_data["incident_statistics"]["total_incidents"],
            previous_incident_data["incident_statistics"]["total_incidents"]
        )

        action_completion_trend = calculate_trend(
            action_data["action_statistics"]["completion_rate"],
            previous_action_data["action_statistics"]["completion_rate"]
        )

        inspection_completion_trend = calculate_trend(
            inspection_data["assignment_statistics"]["completion_rate"],
            previous_inspection_data["assignment_statistics"]["completion_rate"]
        )

        # Extract KPIs with trends
        kpis = {
            "permit_completion_rate": permit_data["permit_statistics"]["completion_rate"],
            "permit_completion_trend": permit_completion_trend,
            "incident_count": incident_data["incident_statistics"]["total_incidents"],
            "incident_count_trend": incident_count_trend,
            "action_completion_rate": action_data["action_statistics"]["completion_rate"],
            "action_completion_trend": action_completion_trend,
            "inspection_completion_rate": inspection_data["assignment_statistics"]["completion_rate"],
            "inspection_completion_trend": inspection_completion_trend,
            "overdue_permits": permit_data["permit_statistics"]["overdue_permits"],
            "overdue_actions": action_data["action_statistics"]["overdue_actions"],
            "overdue_inspections": inspection_data["inspection_statistics"]["overdue_inspections"],
            "injury_incidents": incident_data["incident_statistics"]["injury_incidents"],
            "period": {
                "start_date": (datetime.now() - timedelta(days=days_back)).isoformat(),
                "end_date": datetime.now().isoformat(),
                "days_covered": days_back
            },
            "trends_calculated": True,
            "comparison_period": f"vs previous {days_back} days"
        }

        return SummaryResponse(
            success=True,
            data=kpis,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating KPI metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
