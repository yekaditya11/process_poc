"""
Main Application for AI Safety Summarizer
Orchestrates data extraction and AI summarization across all safety modules
"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import argparse
import os

from data_extractors.permit_to_work_extractor import PermitToWorkExtractor
from data_extractors.incident_management_extractor import IncidentManagementExtractor
from data_extractors.action_tracking_extractor import ActionTrackingExtractor
from data_extractors.inspection_tracking_extractor import InspectionTrackingExtractor
from ai_engine.summarization_engine import SafetySummarizationEngine, SummaryConfig
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
    """Main application class for AI Safety Summarizer"""

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the Safety Summarizer Application

        Args:
            openai_api_key: OpenAI API key for AI summarization
        """
        logger.info("Initializing Safety Summarizer Application")

        # Initialize data extractors
        self.permit_extractor = PermitToWorkExtractor()
        self.incident_extractor = IncidentManagementExtractor()
        self.action_extractor = ActionTrackingExtractor()
        self.inspection_extractor = InspectionTrackingExtractor()

        # Initialize AI engine
        self.ai_engine = SafetySummarizationEngine(api_key=openai_api_key)

        logger.info("Application initialized successfully")

    def generate_comprehensive_summary(self,
                                     customer_id: Optional[str] = None,
                                     days_back: int = 30,
                                     output_file: Optional[str] = None,
                                     include_raw_data: bool = False) -> Dict[str, Any]:
        """
        Generate comprehensive safety summary across all modules

        Args:
            customer_id: Optional customer filter
            days_back: Number of days to look back for data
            output_file: Optional file to save the summary
            include_raw_data: Whether to include raw data in output

        Returns:
            Complete safety summary
        """
        logger.info(f"Starting comprehensive summary generation for customer: {customer_id}, days_back: {days_back}")

        try:
            # Extract data from all modules
            logger.info("Extracting permit to work data...")
            permit_data = self.permit_extractor.get_permit_summary_data(customer_id, days_back)

            logger.info("Extracting incident management data...")
            incident_data = self.incident_extractor.get_incident_summary_data(customer_id, days_back)

            logger.info("Extracting action tracking data...")
            action_data = self.action_extractor.get_action_summary_data(customer_id, days_back)

            logger.info("Extracting inspection tracking data...")
            inspection_data = self.inspection_extractor.get_inspection_summary_data(customer_id, days_back)

            logger.info("Generating AI-powered summary...")
            # Generate AI summary
            ai_summary = self.ai_engine.generate_comprehensive_summary(
                permit_data=permit_data,
                incident_data=incident_data,
                action_data=action_data,
                inspection_data=inspection_data
            )

            # Prepare final output
            final_summary = {
                "summary_info": {
                    "generated_at": datetime.now().isoformat(),
                    "customer_id": customer_id,
                    "analysis_period_days": days_back,
                    "modules_analyzed": ["permit_to_work", "incident_management", "action_tracking", "inspection_tracking"]
                },
                "ai_summary": ai_summary
            }

            # Include raw data if requested
            if include_raw_data:
                final_summary["raw_data"] = {
                    "permit_to_work": permit_data,
                    "incident_management": incident_data,
                    "action_tracking": action_data,
                    "inspection_tracking": inspection_data
                }

            # Save to file if requested
            if output_file:
                self._save_summary_to_file(final_summary, output_file)
                logger.info(f"Summary saved to {output_file}")

            logger.info("Comprehensive summary generation completed successfully")
            return final_summary

        except Exception as e:
            logger.error(f"Error generating comprehensive summary: {str(e)}")
            raise

    def generate_module_summary(self,
                               module: str,
                               customer_id: Optional[str] = None,
                               days_back: int = 30,
                               output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate summary for a specific module

        Args:
            module: Module name (permit, incident, action, inspection)
            customer_id: Optional customer filter
            days_back: Number of days to look back
            output_file: Optional file to save the summary

        Returns:
            Module-specific summary
        """
        logger.info(f"Generating summary for module: {module}")

        try:
            # Extract data based on module
            if module.lower() in ['permit', 'permit_to_work']:
                data = self.permit_extractor.get_permit_summary_data(customer_id, days_back)
                # Use fast comprehensive single-call analysis for speed
                ai_summary = self.ai_engine.generate_fast_comprehensive_analysis('permit', data)
            elif module.lower() in ['incident', 'incident_management']:
                data = self.incident_extractor.get_incident_summary_data(customer_id, days_back)
                ai_summary = self.ai_engine.generate_fast_comprehensive_analysis('incident', data)
            elif module.lower() in ['action', 'action_tracking']:
                data = self.action_extractor.get_action_summary_data(customer_id, days_back)
                ai_summary = self.ai_engine.generate_fast_comprehensive_analysis('action', data)
            elif module.lower() in ['inspection', 'inspection_tracking']:
                data = self.inspection_extractor.get_inspection_summary_data(customer_id, days_back)
                ai_summary = self.ai_engine.generate_fast_comprehensive_analysis('inspection', data)
            else:
                raise ValueError(f"Unknown module: {module}")

            # Prepare output
            summary = {
                "summary_info": {
                    "generated_at": datetime.now().isoformat(),
                    "module": module,
                    "customer_id": customer_id,
                    "analysis_period_days": days_back
                },
                "raw_data": data,
                "ai_summary": ai_summary
            }

            # Save to file if requested
            if output_file:
                self._save_summary_to_file(summary, output_file)
                logger.info(f"Module summary saved to {output_file}")

            logger.info(f"Module summary for {module} completed successfully")
            return summary

        except Exception as e:
            logger.error(f"Error generating module summary for {module}: {str(e)}")
            raise

    def get_quick_dashboard_data(self, customer_id: Optional[str] = None, days_back: int = 7) -> Dict[str, Any]:
        """
        Get quick dashboard data for real-time monitoring

        Args:
            customer_id: Optional customer filter
            days_back: Number of days to look back for data (default: 7)

        Returns:
            Quick dashboard data
        """
        logger.info("Generating quick dashboard data")

        try:
            # Get data for the specified period
            permit_data = self.permit_extractor.get_permit_summary_data(customer_id, days_back)
            incident_data = self.incident_extractor.get_incident_summary_data(customer_id, days_back)
            action_data = self.action_extractor.get_action_summary_data(customer_id, days_back)
            inspection_data = self.inspection_extractor.get_inspection_summary_data(customer_id, days_back)

            # Extract key metrics
            dashboard_data = {
                "last_updated": datetime.now().isoformat(),
                "customer_id": customer_id,
                "permit_metrics": {
                    "total_permits": permit_data["permit_statistics"]["total_permits"],
                    "completion_rate": permit_data["permit_statistics"]["completion_rate"],
                    "overdue_permits": permit_data["permit_statistics"]["overdue_permits"]
                },
                "incident_metrics": {
                    "total_incidents": incident_data["incident_statistics"]["total_incidents"],
                    "injury_incidents": incident_data["incident_statistics"]["injury_incidents"],
                    "action_completion_rate": incident_data["incident_statistics"]["action_completion_rate"]
                },
                "action_metrics": {
                    "total_actions": action_data["action_statistics"]["total_actions"],
                    "completion_rate": action_data["action_statistics"]["completion_rate"],
                    "overdue_actions": action_data["action_statistics"]["overdue_actions"]
                },
                "inspection_metrics": {
                    "total_inspections": inspection_data["inspection_statistics"]["total_inspections"],
                    "completion_rate": inspection_data["assignment_statistics"]["completion_rate"],
                    "overdue_inspections": inspection_data["inspection_statistics"]["overdue_inspections"]
                }
            }

            logger.info("Quick dashboard data generated successfully")
            return dashboard_data

        except Exception as e:
            logger.error(f"Error generating dashboard data: {str(e)}")
            raise

    def _save_summary_to_file(self, summary: Dict[str, Any], filename: str):
        """Save summary to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving summary to file {filename}: {str(e)}")
            raise

    def close(self):
        """Close database connections"""
        logger.info("Closing database connections")
        db_manager.close_connections()

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="AI Safety Summarizer")
    parser.add_argument("--customer-id", help="Customer ID to filter data")
    parser.add_argument("--days-back", type=int, default=30, help="Number of days to look back")
    parser.add_argument("--module", help="Specific module to analyze (permit, incident, action, inspection)")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--include-raw-data", action="store_true", help="Include raw data in output")
    parser.add_argument("--dashboard", action="store_true", help="Generate quick dashboard data")

    args = parser.parse_args()

    # Initialize application
    app = SafetySummarizerApp()

    try:
        if args.dashboard:
            # Generate dashboard data
            result = app.get_quick_dashboard_data(args.customer_id)
        elif args.module:
            # Generate module-specific summary
            result = app.generate_module_summary(
                module=args.module,
                customer_id=args.customer_id,
                days_back=args.days_back,
                output_file=args.output
            )
        else:
            # Generate comprehensive summary
            result = app.generate_comprehensive_summary(
                customer_id=args.customer_id,
                days_back=args.days_back,
                output_file=args.output,
                include_raw_data=args.include_raw_data
            )

        # Print result if no output file specified
        if not args.output:
            print(json.dumps(result, indent=2, default=str))

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        return 1
    finally:
        app.close()

    return 0

if __name__ == "__main__":
    exit(main())
