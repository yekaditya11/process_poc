"""
Observation Tracker KPIs Extractor

This module extracts Observation Tracker KPIs from ProcessSafety database tables.
Focuses specifically on observation tracking data using templateId filtering.

KPIs Implemented:
1. Observations by Area - same logic as incident KPI f, but question title will be "Where?"
2. Observation Status - Open (schedules), Closed (histories) - rows that exist in schedules are open, in history are closed
3. Observation Priority - same logic as incident KPI f, but question title will be "Severity"

Insights Implemented:
1. Observations based on remarks - same logic as incident KPI f, but question title will be "Incident Description", collect all data answered by user and process with AI to get summary

Database Schema:
- ProcessSafetyTemplatesCollections: Contains the "Report Dangerous Behaviour" template
- ProcessSafetySchedules: Contains open/pending observation reports
- ProcessSafetyHistories: Contains completed observation reports
- CheckLists: Links templates to checklists
- ChecklistQuestions: Contains questions for the checklist
- ChecklistAnswers: Contains user answers to checklist questions
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
import json

logger = logging.getLogger(__name__)


class ObservationTrackerKPIsExtractor:
    """Extract observation tracker KPIs from ProcessSafety tables"""

    def __init__(self, db_session: Session = None):
        # Import database configuration
        from config.database_config import db_manager
        
        if db_session is None:
            self.db_session = db_manager.get_process_safety_session()
            self._should_close_session = True
        else:
            self.db_session = db_session
            self._should_close_session = False
            
        # Observation Tracker template ID as specified in requirements
        self.observation_tracker_template_id = '9bb83f61-b869-4721-81b6-0c870e91a779'

    def close(self):
        """Close database session if we created it"""
        if self._should_close_session and self.db_session:
            self.db_session.close()

    def _recreate_session(self):
        """Recreate database session when connection is lost"""
        try:
            from config.database_config import db_manager
            logger.info("Recreating database session due to connection issue")

            # Clean up current session if it exists
            if self.db_session:
                db_manager.cleanup_session(self.db_session)

            # Get fresh session
            self.db_session = db_manager.create_fresh_session()
            logger.info("Database session recreated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to recreate database session: {str(e)}")
            return False

    def _execute_query_safely(self, query, params=None, max_retries=2):
        """Execute query with proper error handling and retry logic"""
        retry_count = 0

        while retry_count <= max_retries:
            try:
                # Validate session before executing query
                from config.database_config import db_manager
                if not db_manager.validate_session(self.db_session):
                    logger.info("Session validation failed, recreating session")
                    if not self._recreate_session():
                        raise Exception("Failed to recreate database session")

                if params:
                    result = self.db_session.execute(query, params)
                else:
                    result = self.db_session.execute(query)
                return result
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Query execution failed (attempt {retry_count + 1}/{max_retries + 1}): {error_msg}")

                # Always rollback transaction on error, but don't fail if rollback fails
                try:
                    if hasattr(self.db_session, 'rollback'):
                        self.db_session.rollback()
                except Exception as rollback_error:
                    logger.debug(f"Rollback failed during error handling (this is expected): {str(rollback_error)}")

                # Check if this is a connection-related error that might benefit from retry
                if retry_count < max_retries and any(keyword in error_msg.lower() for keyword in [
                    'connection', 'timeout', 'network', 'broken pipe', 'reset', 'rollback', 'transaction'
                ]):
                    retry_count += 1
                    logger.info(f"Retrying query execution (attempt {retry_count + 1}/{max_retries + 1})")

                    # Try to recreate session for connection-related errors
                    if not self._recreate_session():
                        logger.error("Failed to recreate session during retry")
                        break
                else:
                    # Non-retryable error or max retries reached
                    raise e

        # If we get here, all retries failed
        raise Exception(f"Query execution failed after {max_retries + 1} attempts")

    def get_observation_tracker_kpis(self, customer_id: Optional[str] = None,
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None,
                                   days_back: int = 365) -> Dict[str, Any]:
        """
        Get all observation tracker KPIs

        Args:
            customer_id: Optional customer ID to filter data
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            days_back: Number of days to look back for data (used if start_date/end_date not provided)

        Returns:
            Dictionary containing all observation tracker KPIs
        """
        try:
            # Calculate date range - use provided dates or calculate from days_back
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=days_back)

            logger.info(f"Extracting observation tracker KPIs for customer: {customer_id}")

            # Get all KPIs
            observations_by_area = self.get_observations_by_area(customer_id, start_date, end_date)
            observation_status = self.get_observation_status(customer_id, start_date, end_date)
            observation_priority = self.get_observation_priority(customer_id, start_date, end_date)
            observations_remarks_insight = self.get_observations_based_on_remarks(customer_id, start_date, end_date)

            return {
                "template_id": self.observation_tracker_template_id,
                "template_name": "Observation Report",
                "observations_by_area": observations_by_area,
                "observation_status": observation_status,
                "observation_priority": observation_priority,
                "observations_remarks_insight": observations_remarks_insight,
                "summary": {
                    "total_areas": len(observations_by_area.get("observations_by_area", {})),
                    "total_open_observations": observation_status.get("open_observations", 0),
                    "total_closed_observations": observation_status.get("closed_observations", 0),
                    "total_observations": observation_status.get("total_observations", 0),
                    "total_priority_levels": len(observation_priority.get("observations_by_priority", {})),
                    "total_remarks_analyzed": observations_remarks_insight.get("total_remarks", 0)
                },
                "extraction_timestamp": datetime.now().isoformat(),
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days_back": days_back
                }
            }

        except Exception as e:
            logger.error(f"Error getting observation tracker KPIs: {str(e)}")
            # Rollback any pending transaction, but don't fail if rollback fails
            try:
                if hasattr(self.db_session, 'rollback'):
                    self.db_session.rollback()
            except Exception as rollback_error:
                logger.debug(f"Rollback failed during error handling (this is expected): {str(rollback_error)}")
            return {
                "template_id": self.observation_tracker_template_id,
                "template_name": "Report Dangerous Behaviour",
                "observations_by_area": {"error": str(e)},
                "observation_status": {"error": str(e)},
                "observation_priority": {"error": str(e)},
                "observations_remarks_insight": {"error": str(e)},
                "summary": {
                    "total_areas": 0,
                    "total_open_observations": 0,
                    "total_closed_observations": 0,
                    "total_observations": 0,
                    "total_priority_levels": 0,
                    "total_remarks_analyzed": 0
                },
                "error": str(e)
            }

    def get_observations_by_area(self, customer_id: Optional[str] = None,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get observations by area - same logic as incident KPI f, but question title will be "Where?"
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Build where conditions
            conditions = [f'ptc.id = \'{self.observation_tracker_template_id}\'']
            
            if customer_id:
                conditions.append(f'ptc."customerId" = \'{customer_id}\'')

            template_where = " AND ".join(conditions)

            # Query to get area information from observation forms with date filtering - specifically looking for "Where?" question
            area_query = text(f"""
                WITH observation_forms AS (
                    -- Get observation forms from schedules with date filtering
                    SELECT DISTINCT cl.id as checklist_id
                    FROM "ProcessSafetyTemplatesCollections" ptc
                    JOIN "ProcessSafetySchedules" ps ON ptc.id = ps."templateId"
                    JOIN "CheckLists" cl ON ptc.id = cl."templateId"
                    WHERE {template_where}
                    AND ps."createdAt" >= :start_date
                    AND ps."createdAt" <= :end_date

                    UNION

                    -- Get observation forms from histories with date filtering
                    SELECT DISTINCT cl.id as checklist_id
                    FROM "ProcessSafetyTemplatesCollections" ptc
                    JOIN "ProcessSafetyHistories" ph ON ptc.id = ph."templateId"
                    JOIN "CheckLists" cl ON ptc.id = cl."templateId"
                    WHERE {template_where}
                    AND ph."createdAt" >= :start_date
                    AND ph."createdAt" <= :end_date
                )
                SELECT DISTINCT
                    ca."answer",
                    cq."text" as question_text,
                    COUNT(*) as observation_count
                FROM observation_forms of
                JOIN "ChecklistQuestions" cq ON of.checklist_id = cq."checklistId"
                JOIN "ChecklistAnswers" ca ON cq.id = ca."question"
                WHERE LOWER(cq."text") = 'where?'
                AND ca."answer" IS NOT NULL
                AND CAST(ca."answer" AS TEXT) != '[]'
                AND CAST(ca."answer" AS TEXT) != ''
                AND CAST(ca."answer" AS TEXT) != 'null'
                AND LENGTH(CAST(ca."answer" AS TEXT)) > 2
                GROUP BY ca."answer", cq."text"
                ORDER BY observation_count DESC
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }

            result = self._execute_query_safely(area_query, params)
            rows = result.fetchall()

            observations_by_area = {}
            total_observations = 0

            for row in rows:
                try:
                    # Parse the answer (might be JSON)
                    answer_text = row[0]
                    if isinstance(answer_text, str):
                        try:
                            # Try to parse as JSON first
                            parsed_answer = json.loads(answer_text)
                            if isinstance(parsed_answer, list) and len(parsed_answer) > 0:
                                area_name = str(parsed_answer[0])
                            elif isinstance(parsed_answer, str):
                                area_name = parsed_answer
                            else:
                                area_name = str(parsed_answer)
                        except (json.JSONDecodeError, TypeError):
                            # If not JSON, use as string
                            area_name = answer_text
                    else:
                        area_name = str(answer_text)

                    # Clean up area name
                    area_name = area_name.strip().strip('"').strip("'")
                    if area_name and area_name.lower() not in ['null', 'none', '']:
                        observation_count = int(row[2])
                        observations_by_area[area_name] = observation_count
                        total_observations += observation_count

                except Exception as parse_error:
                    logger.warning(f"Error parsing area answer: {row[0]}, error: {str(parse_error)}")
                    continue

            return {
                "observations_by_area": observations_by_area,
                "total_observations": total_observations,
                "total_areas": len(observations_by_area),
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting observations by area: {str(e)}")
            # Rollback any pending transaction, but don't fail if rollback fails
            try:
                if hasattr(self.db_session, 'rollback'):
                    self.db_session.rollback()
            except Exception as rollback_error:
                logger.debug(f"Rollback failed during error handling (this is expected): {str(rollback_error)}")
            return {
                "observations_by_area": {},
                "total_observations": 0,
                "total_areas": 0,
                "error": str(e)
            }

    def get_observation_status(self, customer_id: Optional[str] = None,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get observation status - Open (schedules), Closed (histories)
        Rows that exist in schedules are open, in history are closed
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Build where conditions
            conditions = [f'"templateId" = \'{self.observation_tracker_template_id}\'']

            if customer_id:
                conditions.append(f'"customerId" = \'{customer_id}\'')

            where_clause = " AND ".join(conditions)

            # Query to get open observations from schedules table
            open_query = text(f"""
                SELECT COUNT(*) as open_count
                FROM "ProcessSafetySchedules"
                WHERE {where_clause}
                AND "createdAt" >= :start_date
                AND "createdAt" <= :end_date
            """)

            # Query to get closed observations from histories table
            closed_query = text(f"""
                SELECT COUNT(*) as closed_count
                FROM "ProcessSafetyHistories"
                WHERE {where_clause}
                AND "createdAt" >= :start_date
                AND "createdAt" <= :end_date
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }

            # Execute queries
            open_result = self._execute_query_safely(open_query, params)
            open_count = open_result.scalar() or 0

            closed_result = self._execute_query_safely(closed_query, params)
            closed_count = closed_result.scalar() or 0

            total_observations = open_count + closed_count

            return {
                "open_observations": open_count,
                "closed_observations": closed_count,
                "total_observations": total_observations,
                "open_percentage": round((open_count / total_observations * 100) if total_observations > 0 else 0, 2),
                "closed_percentage": round((closed_count / total_observations * 100) if total_observations > 0 else 0, 2),
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting observation status: {str(e)}")
            return {
                "open_observations": 0,
                "closed_observations": 0,
                "total_observations": 0,
                "open_percentage": 0,
                "closed_percentage": 0,
                "error": str(e)
            }

    def get_observation_priority(self, customer_id: Optional[str] = None,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get observation priority - same logic as incident KPI f, but question title will be "Severity"
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Build where conditions
            conditions = [f'ptc.id = \'{self.observation_tracker_template_id}\'']

            if customer_id:
                conditions.append(f'ptc."customerId" = \'{customer_id}\'')

            template_where = " AND ".join(conditions)

            # Query to get priority information from observation forms with date filtering - specifically looking for "Severity" question
            priority_query = text(f"""
                WITH observation_forms AS (
                    -- Get observation forms from schedules with date filtering
                    SELECT DISTINCT cl.id as checklist_id
                    FROM "ProcessSafetyTemplatesCollections" ptc
                    JOIN "ProcessSafetySchedules" ps ON ptc.id = ps."templateId"
                    JOIN "CheckLists" cl ON ptc.id = cl."templateId"
                    WHERE {template_where}
                    AND ps."createdAt" >= :start_date
                    AND ps."createdAt" <= :end_date

                    UNION

                    -- Get observation forms from histories with date filtering
                    SELECT DISTINCT cl.id as checklist_id
                    FROM "ProcessSafetyTemplatesCollections" ptc
                    JOIN "ProcessSafetyHistories" ph ON ptc.id = ph."templateId"
                    JOIN "CheckLists" cl ON ptc.id = cl."templateId"
                    WHERE {template_where}
                    AND ph."createdAt" >= :start_date
                    AND ph."createdAt" <= :end_date
                )
                SELECT DISTINCT
                    ca."answer",
                    cq."text" as question_text,
                    COUNT(*) as observation_count
                FROM observation_forms of
                JOIN "ChecklistQuestions" cq ON of.checklist_id = cq."checklistId"
                JOIN "ChecklistAnswers" ca ON cq.id = ca."question"
                WHERE LOWER(cq."text") LIKE '%severity%'
                AND ca."answer" IS NOT NULL
                AND CAST(ca."answer" AS TEXT) != '[]'
                AND CAST(ca."answer" AS TEXT) != ''
                AND CAST(ca."answer" AS TEXT) != 'null'
                AND LENGTH(CAST(ca."answer" AS TEXT)) > 2
                GROUP BY ca."answer", cq."text"
                ORDER BY observation_count DESC
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }

            result = self._execute_query_safely(priority_query, params)
            rows = result.fetchall()

            observations_by_priority = {}
            total_observations = 0

            for row in rows:
                try:
                    # Parse the answer (might be JSON)
                    answer_text = row[0]
                    if isinstance(answer_text, str):
                        try:
                            # Try to parse as JSON first
                            parsed_answer = json.loads(answer_text)
                            if isinstance(parsed_answer, list) and len(parsed_answer) > 0:
                                priority_name = str(parsed_answer[0])
                            elif isinstance(parsed_answer, str):
                                priority_name = parsed_answer
                            else:
                                priority_name = str(parsed_answer)
                        except (json.JSONDecodeError, TypeError):
                            # If not JSON, use as string
                            priority_name = answer_text
                    else:
                        priority_name = str(answer_text)

                    # Clean up priority name
                    priority_name = priority_name.strip().strip('"').strip("'")
                    if priority_name and priority_name.lower() not in ['null', 'none', '']:
                        observation_count = int(row[2])
                        observations_by_priority[priority_name] = observation_count
                        total_observations += observation_count

                except Exception as parse_error:
                    logger.warning(f"Error parsing priority answer: {row[0]}, error: {str(parse_error)}")
                    continue

            return {
                "observations_by_priority": observations_by_priority,
                "total_observations": total_observations,
                "total_priority_levels": len(observations_by_priority),
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting observation priority: {str(e)}")
            return {
                "observations_by_priority": {},
                "total_observations": 0,
                "total_priority_levels": 0,
                "error": str(e)
            }

    def get_observations_based_on_remarks(self, customer_id: Optional[str] = None,
                                        start_date: Optional[datetime] = None,
                                        end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get observations based on remarks - same logic as incident KPI f, but question title will be "Incident Description"
        Collect all data answered by user and process with AI to get summary
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Build where conditions
            conditions = [f'ptc.id = \'{self.observation_tracker_template_id}\'']

            if customer_id:
                conditions.append(f'ptc."customerId" = \'{customer_id}\'')

            template_where = " AND ".join(conditions)

            # Query to get observation descriptions from user answers with date filtering
            query = text(f"""
                WITH observation_forms AS (
                    -- Get observation forms from schedules with date filtering
                    SELECT DISTINCT cl.id as checklist_id, ptc."templateName"
                    FROM "ProcessSafetyTemplatesCollections" ptc
                    JOIN "ProcessSafetySchedules" ps ON ptc.id = ps."templateId"
                    JOIN "CheckLists" cl ON ptc.id = cl."templateId"
                    WHERE {template_where}
                    AND ps."createdAt" >= :start_date
                    AND ps."createdAt" <= :end_date

                    UNION

                    -- Get observation forms from histories with date filtering
                    SELECT DISTINCT cl.id as checklist_id, ptc."templateName"
                    FROM "ProcessSafetyTemplatesCollections" ptc
                    JOIN "ProcessSafetyHistories" ph ON ptc.id = ph."templateId"
                    JOIN "CheckLists" cl ON ptc.id = cl."templateId"
                    WHERE {template_where}
                    AND ph."createdAt" >= :start_date
                    AND ph."createdAt" <= :end_date
                )
                SELECT DISTINCT
                    ca."answer",
                    cq."text" as question_text,
                    of."templateName",
                    COUNT(*) as answer_count
                FROM observation_forms of
                JOIN "ChecklistQuestions" cq ON of.checklist_id = cq."checklistId"
                JOIN "ChecklistAnswers" ca ON cq.id = ca."question"
                WHERE LOWER(cq."text") LIKE '%incident description%'
                AND ca."answer" IS NOT NULL
                AND CAST(ca."answer" AS TEXT) != '[]'
                AND CAST(ca."answer" AS TEXT) != ''
                AND CAST(ca."answer" AS TEXT) != 'null'
                AND LENGTH(CAST(ca."answer" AS TEXT)) > 2
                GROUP BY ca."answer", cq."text", of."templateName"
                ORDER BY answer_count DESC
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }

            result = self._execute_query_safely(query, params)
            rows = result.fetchall()

            all_remarks = []
            total_remarks = 0

            for row in rows:
                try:
                    # Parse the answer (might be JSON)
                    answer_text = row[0]
                    if isinstance(answer_text, str):
                        try:
                            # Try to parse as JSON first
                            parsed_answer = json.loads(answer_text)
                            if isinstance(parsed_answer, list) and len(parsed_answer) > 0:
                                remark_text = str(parsed_answer[0])
                            elif isinstance(parsed_answer, str):
                                remark_text = parsed_answer
                            else:
                                remark_text = str(parsed_answer)
                        except (json.JSONDecodeError, TypeError):
                            # If not JSON, use as string
                            remark_text = answer_text
                    else:
                        remark_text = str(answer_text)

                    # Clean up remark text
                    remark_text = remark_text.strip().strip('"').strip("'")
                    if remark_text and remark_text.lower() not in ['null', 'none', '']:
                        answer_count = int(row[3])
                        all_remarks.append({
                            "remark": remark_text,
                            "count": answer_count,
                            "question": row[1]
                        })
                        total_remarks += answer_count

                except Exception as parse_error:
                    logger.warning(f"Error parsing remark answer: {row[0]}, error: {str(parse_error)}")
                    continue

            # Prepare data for AI analysis
            ai_analysis_data = {
                "total_remarks": total_remarks,
                "remarks_count": len(all_remarks),
                "remarks_data": all_remarks[:50],  # Limit to top 50 for AI processing
                "template_name": "Report Dangerous Behaviour",
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

            # Generate AI summary (placeholder for now - can be enhanced with actual AI processing)
            ai_summary = self._generate_ai_summary_for_remarks(all_remarks)

            return {
                "total_remarks": total_remarks,
                "remarks_analyzed": len(all_remarks),
                "top_remarks": all_remarks[:10],  # Top 10 most frequent remarks
                "ai_analysis_data": ai_analysis_data,
                "ai_summary": ai_summary,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting observations based on remarks: {str(e)}")
            return {
                "total_remarks": 0,
                "remarks_analyzed": 0,
                "top_remarks": [],
                "ai_analysis_data": {},
                "ai_summary": "Error analyzing remarks",
                "error": str(e)
            }

    def _generate_ai_summary_for_remarks(self, remarks_data: List[Dict[str, Any]]) -> str:
        """
        Generate AI summary for observation remarks (placeholder implementation)
        This can be enhanced to use actual AI processing
        """
        try:
            if not remarks_data:
                return "No observation remarks found for analysis."

            # Basic analysis without AI for now
            total_remarks = len(remarks_data)
            total_count = sum(remark["count"] for remark in remarks_data)

            # Get top 3 most frequent remarks
            top_remarks = sorted(remarks_data, key=lambda x: x["count"], reverse=True)[:3]

            summary = f"Analysis of {total_remarks} unique observation remarks covering {total_count} total observations. "

            if top_remarks:
                summary += "Most frequently reported observations: "
                for i, remark in enumerate(top_remarks, 1):
                    summary += f"{i}. '{remark['remark']}' ({remark['count']} occurrences)"
                    if i < len(top_remarks):
                        summary += ", "
                summary += ". "

            summary += "This data is ready for comprehensive AI analysis to identify patterns and safety insights."

            return summary

        except Exception as e:
            logger.warning(f"Error generating AI summary: {str(e)}")
            return "Error generating summary for observation remarks."


# Utility function for easy usage
def get_observation_tracker_kpis(customer_id: Optional[str] = None,
                               days_back: int = 365) -> Dict[str, Any]:
    """
    Utility function to extract all observation tracker KPIs

    Args:
        customer_id: Optional customer ID to filter data
        days_back: Number of days to look back if start_date not provided

    Returns:
        Dictionary containing all observation tracker KPIs
    """
    try:
        # Create extractor and get KPIs
        extractor = ObservationTrackerKPIsExtractor()
        kpis = extractor.get_observation_tracker_kpis(customer_id, days_back)

        # Close the extractor
        extractor.close()

        return kpis

    except Exception as e:
        logger.error(f"Error in standalone get_observation_tracker_kpis: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    """Test the Observation Tracker KPIs extractor"""

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    print("🔍 Testing Observation Tracker KPIs Extractor...")

    # Test with default parameters (last 30 days)
    kpis = get_observation_tracker_kpis(days_back=30)

    if "error" in kpis:
        print(f"❌ Error: {kpis['error']}")
    else:
        print("✅ Observation Tracker KPIs extracted successfully!")
        print(f"📊 Template ID: {kpis.get('template_id', 'N/A')}")
        print(f"📊 Template Name: {kpis.get('template_name', 'N/A')}")

        # Display summary
        summary = kpis.get('summary', {})
        print(f"📈 Total Areas: {summary.get('total_areas', 0)}")
        print(f"📈 Open Observations: {summary.get('total_open_observations', 0)}")
        print(f"📈 Closed Observations: {summary.get('total_closed_observations', 0)}")
        print(f"📈 Total Observations: {summary.get('total_observations', 0)}")
        print(f"📈 Priority Levels: {summary.get('total_priority_levels', 0)}")
        print(f"📈 Remarks Analyzed: {summary.get('total_remarks_analyzed', 0)}")

        print(f"⏰ Extraction completed at: {kpis.get('extraction_timestamp', 'N/A')}")

        # Display date range
        date_range = kpis.get('date_range', {})
        print(f"📅 Date Range: {date_range.get('start_date', 'N/A')} to {date_range.get('end_date', 'N/A')}")
        print(f"📅 Days Back: {date_range.get('days_back', 'N/A')}")

    print("🏁 Test completed!")
