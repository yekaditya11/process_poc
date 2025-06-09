"""
Main Application for SafetyConnect Dashboard KPIs
Orchestrates data extraction for the 4 core safety modules dashboard KPIs
"""

import logging
from typing import Optional

from data_extractors.incident_kpis import IncidentKPIsExtractor
from data_extractors.actiontracking_kpis import ActionTrackingKPIsExtractor
from data_extractors.driver_safety_checklist_kpis_extractor import DriverSafetyChecklistKPIsExtractor
from data_extractors.observation_tracker_kpis_extractor import ObservationTrackerKPIsExtractor
from data_extractors.equipment_asset_kpis_extractor import EquipmentAssetKPIsExtractor
from data_extractors.employee_training_kpis_extractor import EmployeeTrainingKPIsExtractor
from data_extractors.risk_assessment_kpis_extractor import RiskAssessmentKPIsExtractor
from ai_engine.summarization_engine import SafetySummarizationEngine
from config.database_config import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_summarizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SafetySummarizerApp:
    """Main application class for SafetyConnect Dashboard KPIs"""

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the SafetyConnect Application

        Args:
            openai_api_key: OpenAI API key for AI summarization
        """
        logger.info("Initializing SafetyConnect Dashboard Application")

        # Initialize all 7 core KPI extractors
        # Note: Some extractors require a db_session, others can create their own
        try:
            self.db_session = db_manager.get_process_safety_session()
            self.incident_extractor = IncidentKPIsExtractor(self.db_session)
            self.action_extractor = ActionTrackingKPIsExtractor(self.db_session)
            self.driver_safety_extractor = DriverSafetyChecklistKPIsExtractor()
            self.observation_tracker_extractor = ObservationTrackerKPIsExtractor()
            self.equipment_asset_extractor = EquipmentAssetKPIsExtractor()
            self.employee_training_extractor = EmployeeTrainingKPIsExtractor()
            self.risk_assessment_extractor = RiskAssessmentKPIsExtractor()

            # Initialize AI engine for conversational AI
            self.ai_engine = SafetySummarizationEngine(api_key=openai_api_key)

            logger.info("SafetyConnect Dashboard Application initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SafetyConnect Dashboard Application: {str(e)}")
            raise

    def recreate_database_sessions(self):
        """Recreate database sessions for extractors that need them"""
        try:
            logger.info("Recreating database sessions for extractors")

            # Clean up existing session if it exists
            if hasattr(self, 'db_session') and self.db_session:
                db_manager.cleanup_session(self.db_session)

            # Get fresh session with validation
            self.db_session = db_manager.create_fresh_session()

            # Update extractors with new session
            self.incident_extractor.db_session = self.db_session
            self.action_extractor.db_session = self.db_session

            # Validate the new session
            if db_manager.validate_session(self.db_session):
                logger.info("Database sessions recreated and validated successfully")
                return True
            else:
                logger.error("Database session validation failed after recreation")
                return False
        except Exception as e:
            logger.error(f"Failed to recreate database sessions: {str(e)}")
            return False

    def close(self):
        """Close database connections"""
        logger.info("Closing database connections")

        # Close individual extractor sessions
        if hasattr(self, 'db_session') and self.db_session:
            try:
                self.db_session.close()
            except Exception as e:
                logger.warning(f"Error closing main db_session: {str(e)}")

        if hasattr(self, 'driver_safety_extractor'):
            try:
                self.driver_safety_extractor.close()
            except Exception as e:
                logger.warning(f"Error closing driver_safety_extractor: {str(e)}")

        if hasattr(self, 'observation_tracker_extractor'):
            try:
                self.observation_tracker_extractor.close()
            except Exception as e:
                logger.warning(f"Error closing observation_tracker_extractor: {str(e)}")

        if hasattr(self, 'equipment_asset_extractor'):
            try:
                self.equipment_asset_extractor.close()
            except Exception as e:
                logger.warning(f"Error closing equipment_asset_extractor: {str(e)}")

        if hasattr(self, 'employee_training_extractor'):
            try:
                self.employee_training_extractor.close()
            except Exception as e:
                logger.warning(f"Error closing employee_training_extractor: {str(e)}")

        # Close the database manager connections
        try:
            db_manager.close_connections()
        except Exception as e:
            logger.warning(f"Error closing database manager connections: {str(e)}")

def main():
    """Main function for command-line usage"""
    print("SafetyConnect AI Safety Summarizer")
    print("Core Safety Modules:")
    print("• Incident Investigation")
    print("• Action Tracking")
    print("• Driver Safety Checklists")
    print("• Observation Tracker")
    print("• Equipment Asset Management")
    print("• Employee Training & Fitness")
    print("• Risk Assessment")
    print("\nUse the web API endpoints to access KPI data and AI insights.")
    print("Start the server with: python run_server.py")

    app = SafetySummarizerApp()

    try:
        logger.info("SafetyConnect application ready")
        print("✅ Application ready for API requests.")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        return 1
    finally:
        app.close()

    return 0

if __name__ == "__main__":
    exit(main())
