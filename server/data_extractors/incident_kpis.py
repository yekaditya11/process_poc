"""
Incident Investigation KPIs Extractor

This module extracts key performance indicators (KPIs) related to incident investigation
from the ProcessSafetySchedules and ProcessSafetyHistories tables.

Total: 13 KPIs (11 main KPIs + 2 insights)

Main KPIs (11):
1. Incidents Reported - count of rows in schedules + histories tables (filtered by incident subTagIds)
2. Incident Reporting Trends - weekly, monthly, quarterly trends using createdAt column
3. Open Incidents - count of rows in schedules table
4. Closed Incidents - count of rows in histories table
5. Time taken to complete Investigation - using "incResolvedTimeInMins" key in attribute column
6. Types of Incidents - classification based on user answers to 'Incident Description' questions
7. Number of Actions Created - using specific subTagId "1c6d7b7a-8feb-487d-8640-03fcd6b0275f"
8. Percentage of Open Actions - ratio of open to total actions
9. Number of People Injured - from "Number of Injuries" question in incident forms
10. Incidents Reported by Location - from "Where?" question in incident forms
11. Days since last reported incident - from schedules createdAt or histories scheduleCreatedAt

Insights (2):
12. Incident Trend - incident creation trends from schedules and histories tables
13. Most Unsafe Locations - analysis of locations with highest incident counts from "Where?" question
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
import json

logger = logging.getLogger(__name__)


class IncidentKPIsExtractor:
    """Extract incident investigation KPIs from ProcessSafety tables"""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self._all_subtag_ids = None
        self._action_tracking_subtag_ids = None

    def _handle_sql_error(self, error_msg: str):
        """Handle SQL errors by rolling back transaction and logging"""
        try:
            self.db_session.rollback()
            logger.error(f"SQL Error handled: {error_msg}")
        except Exception as rollback_error:
            logger.error(f"Error during rollback: {str(rollback_error)}")

    def _is_connection_error(self, error_msg: str) -> bool:
        """Check if error is related to database connection"""
        connection_indicators = [
            "server closed the connection",
            "connection unexpectedly",
            "can't reconnect until invalid transaction is rolled back",
            "connection lost",
            "connection refused",
            "connection timeout"
        ]
        return any(indicator in error_msg.lower() for indicator in connection_indicators)

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

                # Check if it's a connection error
                if self._is_connection_error(error_msg) and retry_count < max_retries:
                    logger.info("Connection error detected, attempting to recreate session")
                    if self._recreate_session():
                        retry_count += 1
                        continue

                # If not a connection error or max retries reached, raise the exception
                raise

    def _format_sql_in_clause(self, values_list: List[str], column_name: str) -> str:
        """Format SQL IN clause properly handling single and multiple values"""
        if not values_list:
            return f"{column_name} IN (NULL)"  # This will match nothing
        elif len(values_list) == 1:
            # For single value, use = instead of IN
            return f"{column_name} = '{values_list[0]}'"
        else:
            # For multiple values, use IN with proper tuple formatting
            values_str = "', '".join(values_list)
            return f"{column_name} IN ('{values_str}')"

    def _get_all_subtag_ids(self, customer_id: Optional[str] = None) -> List[str]:
        """Get subTagIds for incident module only (filtered by incident-related tags/subtags)"""
        if self._all_subtag_ids is not None:
            return self._all_subtag_ids

        try:
            # Match your SQL query exactly - no customer filtering unless specifically needed
            query = text("""
                SELECT DISTINCT pst.id
                FROM "ProcessSafetySubTags" pst
                JOIN "ProcessSafetyTags" pt ON pst."tagId" = pt.id
                WHERE (
                    LOWER(pt."tagName") LIKE '%incident%'
                    OR LOWER(pst."subTag") LIKE '%incident%'
                )
                AND (pst."isDeleted" = false OR pst."isDeleted" IS NULL)
            """)

            result = self._execute_query_safely(query)
            self._all_subtag_ids = [row[0] for row in result.fetchall()]

            logger.info(f"Found {len(self._all_subtag_ids)} incident-related subTagIds")
            return self._all_subtag_ids

        except Exception as e:
            logger.error(f"Error getting incident subTagIds: {str(e)}")
            return []

    def _get_action_tracking_subtag_ids(self, customer_id: Optional[str] = None) -> List[str]:
        """Get specific subTagId for action tracking as per requirements"""
        if self._action_tracking_subtag_ids is not None:
            return self._action_tracking_subtag_ids

        try:
            # Use the specific subTagId mentioned in requirements: "1c6d7b7a-8feb-487d-8640-03fcd6b0275f"
            specific_subtag_id = "1c6d7b7a-8feb-487d-8640-03fcd6b0275f"

            # Verify this subTagId exists in the database
            query = text("""
                SELECT id
                FROM "ProcessSafetySubTags"
                WHERE id = :subtag_id
                AND ("isDeleted" = false OR "isDeleted" IS NULL)
            """)

            result = self._execute_query_safely(query, {"subtag_id": specific_subtag_id})
            row = result.fetchone()

            if row:
                self._action_tracking_subtag_ids = [specific_subtag_id]
                logger.info(f"Found specific action tracking subTagId: {specific_subtag_id}")
            else:
                logger.warning(f"Specific action tracking subTagId not found: {specific_subtag_id}")
                self._action_tracking_subtag_ids = []

            return self._action_tracking_subtag_ids

        except Exception as e:
            logger.error(f"Error getting action tracking subTagIds: {str(e)}")
            return []

    def get_incidents_reported(self, customer_id: Optional[str] = None,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get total incidents reported - count of rows in schedules + histories tables (filtered by subTagId for incident module)
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Get incident-related subtag IDs only
            incident_subtag_ids = self._get_all_subtag_ids(customer_id)

            if not incident_subtag_ids:
                return {
                    "total_incidents": 0,
                    "schedules_count": 0,
                    "histories_count": 0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(incident_subtag_ids)

            # Build conditions for schedules - no customer filtering
            schedules_conditions = [
                f'ps."subTagId" IN {subtag_ids_tuple}',
                'ps."createdAt" >= :start_date',
                'ps."createdAt" <= :end_date'
            ]
            schedules_where = " AND ".join(schedules_conditions)

            # Count from schedules
            schedules_query = text(f"""
                SELECT COUNT(*) as schedules_count
                FROM "ProcessSafetySchedules" ps
                WHERE {schedules_where}
            """)

            # Build conditions for histories - no customer filtering
            histories_conditions = [
                f'ph."subTagId" IN {subtag_ids_tuple}',
                'ph."createdAt" >= :start_date',
                'ph."createdAt" <= :end_date'
            ]
            histories_where = " AND ".join(histories_conditions)

            histories_query = text(f"""
                SELECT COUNT(*) as histories_count
                FROM "ProcessSafetyHistories" ph
                WHERE {histories_where}
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            schedules_result = self.db_session.execute(schedules_query, params)
            schedules_count = schedules_result.fetchone()[0]

            histories_result = self.db_session.execute(histories_query, params)
            histories_count = histories_result.fetchone()[0]

            total_incidents = schedules_count + histories_count

            return {
                "total_incidents": total_incidents,
                "schedules_count": schedules_count,
                "histories_count": histories_count,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting incidents reported: {str(e)}")
            return {
                "total_incidents": 0,
                "schedules_count": 0,
                "histories_count": 0,
                "error": str(e)
            }

    def get_incident_reporting_trends(self, customer_id: Optional[str] = None,
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None,
                                    trend_type: str = "monthly") -> Dict[str, Any]:
        """
        Get incident reporting trends - weekly, monthly, quarterly (filtered by subTagId for incident module)
        using createdAt column for date filtering
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                if trend_type == "weekly":
                    start_date = end_date - timedelta(weeks=12)  # Last 12 weeks
                elif trend_type == "yearly":
                    start_date = end_date - timedelta(days=365*3)  # Last 3 years
                elif trend_type == "quarterly":
                    start_date = end_date - timedelta(days=365*2)  # Last 2 years
                else:  # monthly
                    start_date = end_date - timedelta(days=365)  # Last year

            # Get incident-related subtag IDs only
            incident_subtag_ids = self._get_all_subtag_ids(customer_id)

            if not incident_subtag_ids:
                return {
                    "trend_type": trend_type,
                    "trends": [],
                    "total_incidents": 0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(incident_subtag_ids)

            # Define date grouping based on trend type
            if trend_type == "weekly":
                date_trunc = "week"
                date_format = "YYYY-\"W\"WW"  # Year-Week format
            elif trend_type == "yearly":
                date_trunc = "year"
                date_format = "YYYY"  # Year format
            elif trend_type == "quarterly":
                date_trunc = "quarter"
                date_format = "YYYY-\"Q\"Q"  # Year-Quarter format
            else:  # monthly
                date_trunc = "month"
                date_format = "YYYY-MM"  # Year-Month format

            # Build conditions for schedules - no customer filtering
            schedules_conditions = [
                f'ps."subTagId" IN {subtag_ids_tuple}',
                'ps."createdAt" >= :start_date',
                'ps."createdAt" <= :end_date'
            ]
            schedules_where = " AND ".join(schedules_conditions)

            # Build conditions for histories - no customer filtering
            histories_conditions = [
                f'ph."subTagId" IN {subtag_ids_tuple}',
                'ph."createdAt" >= :start_date',
                'ph."createdAt" <= :end_date'
            ]
            histories_where = " AND ".join(histories_conditions)

            # Query for schedules trends
            schedules_query = text(f"""
                SELECT
                    TO_CHAR(DATE_TRUNC('{date_trunc}', ps."createdAt"), '{date_format}') as period_label,
                    COUNT(*) as count
                FROM "ProcessSafetySchedules" ps
                WHERE {schedules_where}
                GROUP BY DATE_TRUNC('{date_trunc}', ps."createdAt")
                ORDER BY DATE_TRUNC('{date_trunc}', ps."createdAt")
            """)

            # Query for histories trends
            histories_query = text(f"""
                SELECT
                    TO_CHAR(DATE_TRUNC('{date_trunc}', ph."createdAt"), '{date_format}') as period_label,
                    COUNT(*) as count
                FROM "ProcessSafetyHistories" ph
                WHERE {histories_where}
                GROUP BY DATE_TRUNC('{date_trunc}', ph."createdAt")
                ORDER BY DATE_TRUNC('{date_trunc}', ph."createdAt")
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }

            # Execute queries
            schedules_result = self.db_session.execute(schedules_query, params)
            histories_result = self.db_session.execute(histories_query, params)

            # Combine results
            trends_dict = {}
            total_incidents = 0

            # Process schedules data
            for row in schedules_result.fetchall():
                period_label = row[0]
                count = row[1]
                if period_label not in trends_dict:
                    trends_dict[period_label] = {"schedules": 0, "histories": 0, "total": 0}
                trends_dict[period_label]["schedules"] = count
                trends_dict[period_label]["total"] += count
                total_incidents += count

            # Process histories data
            for row in histories_result.fetchall():
                period_label = row[0]
                count = row[1]
                if period_label not in trends_dict:
                    trends_dict[period_label] = {"schedules": 0, "histories": 0, "total": 0}
                trends_dict[period_label]["histories"] = count
                trends_dict[period_label]["total"] += count
                total_incidents += count

            # Convert to list format
            trends = []
            for period_label in sorted(trends_dict.keys()):
                data = trends_dict[period_label]
                trends.append({
                    "period": period_label,
                    "schedules_count": data["schedules"],
                    "histories_count": data["histories"],
                    "total_count": data["total"]
                })

            return {
                "trend_type": trend_type,
                "trends": trends,
                "total_incidents": total_incidents,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting incident reporting trends: {str(e)}")
            return {
                "trend_type": trend_type,
                "trends": [],
                "total_incidents": 0,
                "error": str(e)
            }

    def get_open_incidents(self, customer_id: Optional[str] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get count of open incidents - count of rows in schedules table (filtered by subTagId for incident module)
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Get incident-related subtag IDs only
            incident_subtag_ids = self._get_all_subtag_ids(customer_id)

            if not incident_subtag_ids:
                return {
                    "open_incidents": 0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(incident_subtag_ids)

            # Build conditions with date filtering
            conditions = [
                f'ps."subTagId" IN {subtag_ids_tuple}',
                'ps."createdAt" >= :start_date',
                'ps."createdAt" <= :end_date'
            ]

            where_clause = " AND ".join(conditions)

            query = text(f"""
                SELECT COUNT(*) as open_incidents
                FROM "ProcessSafetySchedules" ps
                WHERE {where_clause}
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            result = self.db_session.execute(query, params)
            open_incidents = result.fetchone()[0]

            return {
                "open_incidents": open_incidents,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting open incidents: {str(e)}")
            return {
                "open_incidents": 0,
                "error": str(e)
            }

    def get_closed_incidents(self, customer_id: Optional[str] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get count of closed incidents - count of rows in histories table (filtered by subTagId for incident module)
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Get incident-related subtag IDs only
            incident_subtag_ids = self._get_all_subtag_ids(customer_id)

            if not incident_subtag_ids:
                return {
                    "closed_incidents": 0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(incident_subtag_ids)

            # Build conditions - no customer filtering
            conditions = [
                f'ph."subTagId" IN {subtag_ids_tuple}',
                'ph."createdAt" >= :start_date',
                'ph."createdAt" <= :end_date'
            ]

            where_clause = " AND ".join(conditions)

            query = text(f"""
                SELECT COUNT(*) as closed_incidents
                FROM "ProcessSafetyHistories" ph
                WHERE {where_clause}
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            result = self.db_session.execute(query, params)
            closed_incidents = result.fetchone()[0]

            return {
                "closed_incidents": closed_incidents,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting closed incidents: {str(e)}")
            return {
                "closed_incidents": 0,
                "error": str(e)
            }

    def get_investigation_completion_time(self, customer_id: Optional[str] = None,
                                        start_date: Optional[datetime] = None,
                                        end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get time taken to complete investigation using "incResolvedTimeInMins"
        key in attribute column of histories table (filtered by subTagId for incident module)
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Get incident-related subtag IDs only
            incident_subtag_ids = self._get_all_subtag_ids(customer_id)

            if not incident_subtag_ids:
                return {
                    "average_completion_time_mins": 0,
                    "total_completed_investigations": 0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(incident_subtag_ids)

            # Build conditions - no customer filtering
            conditions = [
                f'ph."subTagId" IN {subtag_ids_tuple}',
                'ph."createdAt" >= :start_date',
                'ph."createdAt" <= :end_date',
                'ph."attribute" IS NOT NULL',
                "ph.\"attribute\"::text LIKE '%incResolvedTimeInMins%'"
            ]

            where_clause = " AND ".join(conditions)

            # Query to extract incResolvedTimeInMins from attribute JSON
            query = text(f"""
                SELECT
                    CAST(ph."attribute"->>'incResolvedTimeInMins' AS NUMERIC) as resolved_time_mins
                FROM "ProcessSafetyHistories" ph
                WHERE {where_clause}
                AND ph."attribute"->>'incResolvedTimeInMins' IS NOT NULL
                AND ph."attribute"->>'incResolvedTimeInMins' != ''
                AND ph."attribute"->>'incResolvedTimeInMins' ~ '^[0-9]+\.?[0-9]*$'
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            result = self.db_session.execute(query, params)
            rows = result.fetchall()

            if not rows:
                return {
                    "average_completion_time_mins": 0,
                    "total_completed_investigations": 0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Extract completion times
            completion_times = []
            for row in rows:
                resolved_time_mins = float(row[0]) if row[0] is not None else 0
                if resolved_time_mins > 0:  # Only include valid positive times
                    completion_times.append(resolved_time_mins)

            if not completion_times:
                return {
                    "average_completion_time_mins": 0,
                    "total_completed_investigations": 0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Calculate simple statistics
            total_investigations = len(completion_times)
            average_time = sum(completion_times) / total_investigations

            return {
                "average_completion_time_mins": round(average_time, 2),
                "total_completed_investigations": total_investigations,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting investigation completion time: {str(e)}")
            return {
                "average_completion_time_mins": 0,
                "total_completed_investigations": 0,
                "error": str(e)
            }

    def get_incident_types_classification(self, customer_id: Optional[str] = None,
                                        start_date: Optional[datetime] = None,
                                        end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get incident types classification based on user descriptions from incident forms
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Get incident-related subtag IDs only
            incident_subtag_ids = self._get_all_subtag_ids(customer_id)

            if not incident_subtag_ids:
                return {
                    "incident_types": {},
                    "total_classified": 0,
                    "unclassified": 0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(incident_subtag_ids)

            # Build conditions for templates
            template_conditions = [f'ptc."subTagId" IN {subtag_ids_tuple}']
            template_where = " AND ".join(template_conditions)

            # Query to get incident descriptions from user answers with date filtering
            query = text(f"""
                WITH incident_forms AS (
                    -- Get incident forms from schedules with date filtering
                    SELECT DISTINCT cl.id as checklist_id, ptc."templateName"
                    FROM "ProcessSafetyTemplatesCollections" ptc
                    JOIN "ProcessSafetySchedules" ps ON ptc.id = ps."templateId"
                    JOIN "CheckLists" cl ON ptc.id = cl."templateId"
                    WHERE {template_where}
                    AND ps."createdAt" >= :start_date
                    AND ps."createdAt" <= :end_date

                    UNION

                    -- Get incident forms from histories with date filtering
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
                    if."templateName",
                    COUNT(*) as answer_count
                FROM incident_forms if
                JOIN "ChecklistQuestions" cq ON if.checklist_id = cq."checklistId"
                JOIN "ChecklistAnswers" ca ON cq.id = ca."question"
                WHERE LOWER(cq."text") LIKE '%incident description%'
                AND ca."answer" IS NOT NULL
                AND CAST(ca."answer" AS TEXT) != '[]'
                AND CAST(ca."answer" AS TEXT) != ''
                AND CAST(ca."answer" AS TEXT) != 'null'
                AND LENGTH(CAST(ca."answer" AS TEXT)) > 2
                GROUP BY ca."answer", cq."text", if."templateName"
                ORDER BY answer_count DESC
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            result = self.db_session.execute(query, params)
            rows = result.fetchall()

            # Define incident type classification keywords
            incident_types_keywords = {
                "Fatality": ["death", "fatality", "fatal", "died", "dead", "mortality"],
                "Personal Injury": ["injury", "injured", "hurt", "wound", "cut", "bruise", "fracture", "sprain", "strain"],
                "Road Traffic Accident": ["traffic", "vehicle", "car", "truck", "road", "collision", "crash", "accident"],
                "Asset damage": ["damage", "broken", "equipment", "machinery", "asset", "property damage", "structural"],
                "Fire /Explosion": ["fire", "explosion", "blast", "burn", "flame", "ignition", "combustion"],
                "Man lost": ["lost", "missing", "disappeared", "whereabouts unknown", "cannot locate"],
                "Major Spillage": ["spill", "spillage", "leak", "discharge", "overflow", "contamination"],
                "Property theft": ["theft", "stolen", "robbery", "burglary", "missing property", "unauthorized removal"],
                "Occupational Illness": ["illness", "disease", "sickness", "health", "medical", "occupational health"],
                "Others": []  # Default category for unmatched descriptions
            }

            # Initialize counters
            incident_classification = {key: 0 for key in incident_types_keywords.keys()}
            total_classified = 0
            unclassified_descriptions = []

            # Classify each answer
            for row in rows:
                answer = str(row[0]).lower() if row[0] else ""
                answer_count = row[3]

                classified = False

                # Check against each incident type
                for incident_type, keywords in incident_types_keywords.items():
                    if incident_type == "Others":
                        continue

                    # Check if any keyword matches the description
                    for keyword in keywords:
                        if keyword.lower() in answer:
                            incident_classification[incident_type] += answer_count
                            total_classified += answer_count
                            classified = True
                            break

                    if classified:
                        break

                # If not classified, add to "Others"
                if not classified:
                    incident_classification["Others"] += answer_count
                    unclassified_descriptions.append({
                        "description": answer[:100] + "..." if len(answer) > 100 else answer,
                        "count": answer_count
                    })

            # Calculate total including "Others"
            total_with_others = sum(incident_classification.values())

            return {
                "incident_types": incident_classification,
                "total_classified": total_with_others,
                "unclassified_descriptions": unclassified_descriptions[:10],  # Show top 10 unclassified
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting incident types classification: {str(e)}")
            return {
                "incident_types": {},
                "total_classified": 0,
                "unclassified_descriptions": [],
                "error": str(e)
            }

    def get_number_of_actions_created(self, customer_id: Optional[str] = None,
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get number of actions created - count of rows in schedules + histories tables
        filtered by subTagId for action tracking module
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            action_subtag_ids = self._get_action_tracking_subtag_ids(customer_id)

            if not action_subtag_ids:
                return {
                    "total_actions_created": 0,
                    "schedules_count": 0,
                    "histories_count": 0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Build conditions using the helper method for SQL IN clause
            subtag_condition = self._format_sql_in_clause(action_subtag_ids, 'ps."subTagId"')

            # Count from schedules
            schedules_conditions = [
                subtag_condition,
                'ps."createdAt" >= :start_date',
                'ps."createdAt" <= :end_date'
            ]
            schedules_where = " AND ".join(schedules_conditions)

            schedules_query = text(f"""
                SELECT COUNT(*) as schedules_count
                FROM "ProcessSafetySchedules" ps
                WHERE {schedules_where}
            """)

            # Count from histories
            subtag_condition_hist = self._format_sql_in_clause(action_subtag_ids, 'ph."subTagId"')
            histories_conditions = [
                subtag_condition_hist,
                'ph."createdAt" >= :start_date',
                'ph."createdAt" <= :end_date'
            ]
            histories_where = " AND ".join(histories_conditions)

            histories_query = text(f"""
                SELECT COUNT(*) as histories_count
                FROM "ProcessSafetyHistories" ph
                WHERE {histories_where}
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            schedules_result = self.db_session.execute(schedules_query, params)
            schedules_count = schedules_result.fetchone()[0]

            histories_result = self.db_session.execute(histories_query, params)
            histories_count = histories_result.fetchone()[0]

            total_actions = schedules_count + histories_count

            return {
                "total_actions_created": total_actions,
                "schedules_count": schedules_count,
                "histories_count": histories_count,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting number of actions created: {str(e)}")
            return {
                "total_actions_created": 0,
                "schedules_count": 0,
                "histories_count": 0,
                "error": str(e)
            }

    def get_percentage_of_open_actions(self, customer_id: Optional[str] = None,
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get percentage of open actions
        Open actions = count of action rows in schedules table
        Total actions = count of action rows in schedules + histories tables
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            action_subtag_ids = self._get_action_tracking_subtag_ids(customer_id)

            if not action_subtag_ids:
                return {
                    "open_actions": 0,
                    "total_actions": 0,
                    "open_actions_percentage": 0.0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Build conditions using the helper method for SQL IN clause with date filtering
            subtag_condition = self._format_sql_in_clause(action_subtag_ids, 'ps."subTagId"')

            # Count open actions (from schedules) with date filtering
            open_conditions = [
                subtag_condition,
                'ps."createdAt" >= :start_date',
                'ps."createdAt" <= :end_date'
            ]
            open_where = " AND ".join(open_conditions)

            open_query = text(f"""
                SELECT COUNT(*) as open_actions
                FROM "ProcessSafetySchedules" ps
                WHERE {open_where}
            """)

            # Count total actions (from schedules + histories) with date filtering
            total_schedules_query = text(f"""
                SELECT COUNT(*) as schedules_count
                FROM "ProcessSafetySchedules" ps
                WHERE {open_where}
            """)

            subtag_condition_hist = self._format_sql_in_clause(action_subtag_ids, 'ph."subTagId"')
            histories_conditions = [
                subtag_condition_hist,
                'ph."createdAt" >= :start_date',
                'ph."createdAt" <= :end_date'
            ]
            histories_where = " AND ".join(histories_conditions)

            total_histories_query = text(f"""
                SELECT COUNT(*) as histories_count
                FROM "ProcessSafetyHistories" ph
                WHERE {histories_where}
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }

            # Execute queries
            open_result = self.db_session.execute(open_query, params)
            open_actions = open_result.fetchone()[0]

            schedules_result = self.db_session.execute(total_schedules_query, params)
            schedules_count = schedules_result.fetchone()[0]

            histories_result = self.db_session.execute(total_histories_query, params)
            histories_count = histories_result.fetchone()[0]

            total_actions = schedules_count + histories_count

            # Calculate percentage
            if total_actions > 0:
                open_percentage = (open_actions / total_actions) * 100
            else:
                open_percentage = 0.0

            return {
                "open_actions": open_actions,
                "total_actions": total_actions,
                "open_actions_percentage": round(open_percentage, 2),
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting percentage of open actions: {str(e)}")
            return {
                "open_actions": 0,
                "total_actions": 0,
                "open_actions_percentage": 0.0,
                "error": str(e)
            }

    def get_number_of_people_injured(self, customer_id: Optional[str] = None,
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get number of people injured from incident form answers using "Number of Injuries" question
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Get from incident form answers only (ProcessSafety database only)
            incident_forms_data = self._get_injuries_from_incident_forms(customer_id, start_date, end_date)

            total_people_injured = incident_forms_data.get("total_people_injured", 0)

            return {
                "total_people_injured": total_people_injured,
                "incident_forms": incident_forms_data,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting number of people injured: {str(e)}")
            return {
                "total_people_injured": 0,
                "incident_forms": {},
                "error": str(e)
            }

    def _get_injuries_from_incident_forms(self, customer_id: Optional[str] = None,
                                         start_date: Optional[datetime] = None,
                                         end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get injury data from incident form answers"""
        try:
            # Get incident-related subtag IDs only
            incident_subtag_ids = self._get_all_subtag_ids(customer_id)

            if not incident_subtag_ids:
                return {
                    "total_people_injured": 0,
                    "injury_incidents_count": 0,
                    "source": "IncidentForms"
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(incident_subtag_ids)

            # Build conditions for templates
            template_conditions = [f'ptc."subTagId" IN {subtag_ids_tuple}']
            template_where = " AND ".join(template_conditions)

            # Query to get answers about people injured - specifically looking for "Number of Injuries" question
            # Note: Since this queries form answers, we need to join with schedules/histories to apply date filtering
            query = text(f"""
                WITH incident_forms AS (
                    -- Get incident forms from schedules with date filtering
                    SELECT DISTINCT cl.id as checklist_id
                    FROM "ProcessSafetyTemplatesCollections" ptc
                    JOIN "ProcessSafetySchedules" ps ON ptc.id = ps."templateId"
                    JOIN "CheckLists" cl ON ptc.id = cl."templateId"
                    WHERE {template_where}
                    AND ps."createdAt" >= :start_date
                    AND ps."createdAt" <= :end_date

                    UNION

                    -- Get incident forms from histories with date filtering
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
                    cq."text" as question_text
                FROM incident_forms if
                JOIN "ChecklistQuestions" cq ON if.checklist_id = cq."checklistId"
                JOIN "ChecklistAnswers" ca ON cq.id = ca."question"
                WHERE LOWER(cq."text") LIKE '%number of injuries%'
                AND ca."answer" IS NOT NULL
                AND CAST(ca."answer" AS TEXT) != '[]'
                AND CAST(ca."answer" AS TEXT) != ''
                AND CAST(ca."answer" AS TEXT) != 'null'
                AND LENGTH(CAST(ca."answer" AS TEXT)) > 2
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            result = self.db_session.execute(query, params)
            rows = result.fetchall()

            total_injured = 0
            injury_incidents = 0

            # Process each answer to extract number of injured people
            for row in rows:
                answer = str(row[0]).strip() if row[0] else ""
                question_text = str(row[1]) if row[1] else ""

                if answer:
                    injury_incidents += 1

                    # Try to extract numeric value from the answer
                    injured_count = self._extract_injury_count(answer)
                    total_injured += injured_count

            return {
                "total_people_injured": total_injured,
                "injury_incidents_count": injury_incidents,
                "source": "IncidentForms"
            }

        except Exception as e:
            logger.error(f"Error getting injuries from incident forms: {str(e)}")
            return {
                "total_people_injured": 0,
                "injury_incidents_count": 0,
                "error": str(e)
            }

    def _extract_injury_count(self, answer: str) -> int:
        """
        Extract numeric count of injured people from text answer
        """
        try:
            import re

            # Clean the answer
            answer = answer.lower().strip()

            # Handle common text responses
            if any(word in answer for word in ['none', 'no one', 'zero', 'nil', 'no injury', 'no injuries']):
                return 0

            if any(word in answer for word in ['one', 'single']):
                return 1

            if any(word in answer for word in ['two', 'couple']):
                return 2

            if any(word in answer for word in ['three']):
                return 3

            if any(word in answer for word in ['four']):
                return 4

            if any(word in answer for word in ['five']):
                return 5

            # Extract numbers using regex
            numbers = re.findall(r'\d+', answer)
            if numbers:
                # Take the first number found
                return int(numbers[0])

            # If we can't extract a number but there's an answer, assume 1 person
            if answer and answer not in ['', '[]', 'null']:
                return 1

            return 0

        except Exception as e:
            logger.error(f"Error extracting injury count from '{answer}': {str(e)}")
            # If we can't parse but there's an answer, assume 1 person injured
            return 1 if answer and answer.strip() else 0

    def get_incidents_by_department(self, customer_id: Optional[str] = None,
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get incidents reported by department based on user profiles
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Get incident-related subtag IDs only
            incident_subtag_ids = self._get_all_subtag_ids(customer_id)

            if not incident_subtag_ids:
                return {
                    "incidents_by_department": {},
                    "total_incidents": 0,
                    "unknown_department": 0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(incident_subtag_ids)

            # Build conditions for schedules
            schedules_conditions = [
                f'ps."subTagId" IN {subtag_ids_tuple}',
                'ps."createdAt" >= :start_date',
                'ps."createdAt" <= :end_date'
            ]
            schedules_where = " AND ".join(schedules_conditions)

            # Query for schedules with department info
            schedules_query = text(f"""
                SELECT
                    COALESCE(up."department", 'Unknown') as department,
                    COUNT(*) as incident_count
                FROM "ProcessSafetySchedules" ps
                LEFT JOIN "UserProfiles" up ON ps."userId" = up."userId"
                WHERE {schedules_where}
                GROUP BY COALESCE(up."department", 'Unknown')
            """)

            # Build conditions for histories
            histories_conditions = [
                f'ph."subTagId" IN {subtag_ids_tuple}',
                'ph."createdAt" >= :start_date',
                'ph."createdAt" <= :end_date'
            ]
            histories_where = " AND ".join(histories_conditions)

            # Query for histories with department info
            histories_query = text(f"""
                SELECT
                    COALESCE(up."department", 'Unknown') as department,
                    COUNT(*) as incident_count
                FROM "ProcessSafetyHistories" ph
                LEFT JOIN "UserProfiles" up ON ph."associatedUserId" = up."userId"
                WHERE {histories_where}
                GROUP BY COALESCE(up."department", 'Unknown')
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }            # Execute queries
            schedules_result = self.db_session.execute(schedules_query, params)
            histories_result = self.db_session.execute(histories_query, params)

            # Combine results
            department_counts = {}
            total_incidents = 0
            unknown_department = 0

            # Process schedules data
            for row in schedules_result.fetchall():
                department = row[0] if row[0] and row[0].strip() else "Unknown"
                count = row[1]
                if department not in department_counts:
                    department_counts[department] = 0
                department_counts[department] += count
                total_incidents += count
                if department == "Unknown":
                    unknown_department += count

            # Process histories data
            for row in histories_result.fetchall():
                department = row[0] if row[0] and row[0].strip() else "Unknown"
                count = row[1]
                if department not in department_counts:
                    department_counts[department] = 0
                department_counts[department] += count
                total_incidents += count
                if department == "Unknown":
                    unknown_department += count

            return {
                "incidents_by_department": department_counts,
                "total_incidents": total_incidents,
                "unknown_department": unknown_department,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting incidents by department: {str(e)}")
            return {
                "incidents_by_department": {},
                "total_incidents": 0,
                "unknown_department": 0,
                "error": str(e)
            }

    def get_incidents_by_location(self, customer_id: Optional[str] = None,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get incidents reported by location from incident forms and assignment data
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Get incident-related subtag IDs only
            incident_subtag_ids = self._get_all_subtag_ids(customer_id)

            if not incident_subtag_ids:
                return {
                    "incidents_by_location": {},
                    "total_incidents": 0,
                    "unknown_location": 0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(incident_subtag_ids)

            # Build conditions for templates
            template_conditions = [f'ptc."subTagId" IN {subtag_ids_tuple}']
            template_where = " AND ".join(template_conditions)

            # Query to get location information from incident forms with date filtering - specifically looking for "Where?" question
            location_query = text(f"""
                WITH incident_forms AS (
                    -- Get incident forms from schedules with date filtering
                    SELECT DISTINCT cl.id as checklist_id
                    FROM "ProcessSafetyTemplatesCollections" ptc
                    JOIN "ProcessSafetySchedules" ps ON ptc.id = ps."templateId"
                    JOIN "CheckLists" cl ON ptc.id = cl."templateId"
                    WHERE {template_where}
                    AND ps."createdAt" >= :start_date
                    AND ps."createdAt" <= :end_date

                    UNION

                    -- Get incident forms from histories with date filtering
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
                    COUNT(*) as incident_count
                FROM incident_forms if
                JOIN "ChecklistQuestions" cq ON if.checklist_id = cq."checklistId"
                JOIN "ChecklistAnswers" ca ON cq.id = ca."question"
                WHERE LOWER(cq."text") = 'where?'
                AND ca."answer" IS NOT NULL
                AND CAST(ca."answer" AS TEXT) != '[]'
                AND CAST(ca."answer" AS TEXT) != ''
                AND CAST(ca."answer" AS TEXT) != 'null'
                AND LENGTH(CAST(ca."answer" AS TEXT)) > 2
                GROUP BY ca."answer", cq."text"
                ORDER BY incident_count DESC
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            result = self.db_session.execute(location_query, params)
            rows = result.fetchall()

            location_counts = {}
            total_incidents = 0
            unknown_location = 0

            # Process location answers
            for row in rows:
                answer = str(row[0]).strip() if row[0] else ""
                incident_count = row[2]

                if answer:
                    # Clean and normalize location name
                    location = self._normalize_location_name(answer)
                    if location == "Unknown":
                        unknown_location += incident_count
                    else:
                        if location not in location_counts:
                            location_counts[location] = 0
                        location_counts[location] += incident_count
                    total_incidents += incident_count

            # Note: ChecklistAssignments table doesn't have address column in this database
            # Only using location data from incident form answers for now

            return {
                "incidents_by_location": location_counts,
                "total_incidents": total_incidents,
                "unknown_location": unknown_location,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting incidents by location: {str(e)}")
            return {
                "incidents_by_location": {},
                "total_incidents": 0,
                "unknown_location": 0,
                "error": str(e)
            }

    def _normalize_location_name(self, location_text: str) -> str:
        """
        Normalize location names for consistent grouping
        """
        try:
            if not location_text or location_text.strip() == "":
                return "Unknown"

            # Clean the location text
            location = location_text.strip()

            # Handle JSON array format like ['Location Name']
            if location.startswith('[') and location.endswith(']'):
                try:
                    import json
                    parsed = json.loads(location)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        location = str(parsed[0]).strip()
                except:
                    # If JSON parsing fails, try to extract manually
                    location = location.strip('[]"\'').strip()

            # Remove quotes if present
            location = location.strip('"\'')

            # Convert to title case for consistency
            location = location.title()

            # Handle common variations
            if not location or location.lower() in ['', 'null', 'none', 'n/a', 'na']:
                return "Unknown"

            return location

        except Exception as e:
            logger.error(f"Error normalizing location '{location_text}': {str(e)}")
            return "Unknown"

    def get_days_since_last_incident(self, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get days since last reported incident
        - First check schedules table for last "createdAt"
        - If no incidents in schedules, check histories table for last "scheduleCreatedAt"
        - If no incidents found in either, return "no incident reported"
        """
        try:
            # Get incident-related subtag IDs only
            incident_subtag_ids = self._get_all_subtag_ids(customer_id)

            if not incident_subtag_ids:
                return {
                    "days_since_last_incident": None,
                    "last_incident_date": None,
                    "status": "no_subtags_found",
                    "source": None
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(incident_subtag_ids)

            # First, check schedules table for the most recent incident
            schedules_conditions = [f'ps."subTagId" IN {subtag_ids_tuple}']
            schedules_where = " AND ".join(schedules_conditions)

            schedules_query = text(f"""
                SELECT MAX(ps."createdAt") as last_incident_date
                FROM "ProcessSafetySchedules" ps
                WHERE {schedules_where}
            """)

            params = {}
            schedules_result = self.db_session.execute(schedules_query, params)
            schedules_row = schedules_result.fetchone()
            last_schedules_date = schedules_row[0] if schedules_row and schedules_row[0] else None

            if last_schedules_date:
                # Found incident in schedules table
                current_date = datetime.now()

                # Handle timezone-aware vs timezone-naive datetime comparison
                if last_schedules_date.tzinfo is not None:
                    # Database datetime is timezone-aware, make current_date timezone-aware too
                    from datetime import timezone
                    current_date = current_date.replace(tzinfo=timezone.utc)
                else:
                    # Database datetime is timezone-naive, ensure current_date is also naive
                    current_date = current_date.replace(tzinfo=None)

                days_since = (current_date - last_schedules_date).days

                return {
                    "days_since_last_incident": days_since,
                    "last_incident_date": last_schedules_date.isoformat(),
                    "status": "incident_found",
                    "source": "schedules_table"
                }

            # If no incidents in schedules, check histories table using scheduleCreatedAt
            histories_conditions = [f'ph."subTagId" IN {subtag_ids_tuple}']
            histories_where = " AND ".join(histories_conditions)

            histories_query = text(f"""
                SELECT MAX(ph."scheduleCreatedAt") as last_incident_date
                FROM "ProcessSafetyHistories" ph
                WHERE {histories_where}
                AND ph."scheduleCreatedAt" IS NOT NULL
            """)

            histories_result = self.db_session.execute(histories_query, params)
            histories_row = histories_result.fetchone()
            last_histories_date = histories_row[0] if histories_row and histories_row[0] else None

            if last_histories_date:
                # Found incident in histories table
                current_date = datetime.now()

                # Handle timezone-aware vs timezone-naive datetime comparison
                if last_histories_date.tzinfo is not None:
                    # Database datetime is timezone-aware, make current_date timezone-aware too
                    from datetime import timezone
                    current_date = current_date.replace(tzinfo=timezone.utc)
                else:
                    # Database datetime is timezone-naive, ensure current_date is also naive
                    current_date = current_date.replace(tzinfo=None)

                days_since = (current_date - last_histories_date).days

                return {
                    "days_since_last_incident": days_since,
                    "last_incident_date": last_histories_date.isoformat(),
                    "status": "incident_found",
                    "source": "histories_table"
                }

            # No incidents found in either table
            return {
                "days_since_last_incident": None,
                "last_incident_date": None,
                "status": "no_incident_reported",
                "source": None
            }

        except Exception as e:
            logger.error(f"Error getting days since last incident: {str(e)}")
            return {
                "days_since_last_incident": None,
                "last_incident_date": None,
                "status": "error",
                "source": None,
                "error": str(e)
            }

    def get_incident_trend_insight(self, customer_id: Optional[str] = None,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get incident trend insight - incident created based on "createdAt" column in schedules table,
        and "scheduleCreatedAt" in histories table
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Get incident-related subtag IDs only
            incident_subtag_ids = self._get_all_subtag_ids(customer_id)

            if not incident_subtag_ids:
                return {
                    "incident_trend": [],
                    "total_incidents": 0,
                    "trend_analysis": "No incident data available",
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(incident_subtag_ids)

            # Query for schedules trends (using createdAt)
            schedules_query = text(f"""
                SELECT
                    DATE_TRUNC('month', ps."createdAt") as month_date,
                    TO_CHAR(ps."createdAt", 'YYYY-MM') as month_label,
                    COUNT(*) as count
                FROM "ProcessSafetySchedules" ps
                WHERE ps."subTagId" IN {subtag_ids_tuple}
                AND ps."createdAt" >= :start_date
                AND ps."createdAt" <= :end_date
                GROUP BY DATE_TRUNC('month', ps."createdAt"), TO_CHAR(ps."createdAt", 'YYYY-MM')
                ORDER BY DATE_TRUNC('month', ps."createdAt")
            """)

            # Query for histories trends (using scheduleCreatedAt)
            histories_query = text(f"""
                SELECT
                    DATE_TRUNC('month', ph."scheduleCreatedAt") as month_date,
                    TO_CHAR(ph."scheduleCreatedAt", 'YYYY-MM') as month_label,
                    COUNT(*) as count
                FROM "ProcessSafetyHistories" ph
                WHERE ph."subTagId" IN {subtag_ids_tuple}
                AND ph."scheduleCreatedAt" >= :start_date
                AND ph."scheduleCreatedAt" <= :end_date
                AND ph."scheduleCreatedAt" IS NOT NULL
                GROUP BY DATE_TRUNC('month', ph."scheduleCreatedAt"), TO_CHAR(ph."scheduleCreatedAt", 'YYYY-MM')
                ORDER BY DATE_TRUNC('month', ph."scheduleCreatedAt")
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }

            # Execute queries
            schedules_result = self.db_session.execute(schedules_query, params)
            histories_result = self.db_session.execute(histories_query, params)

            # Combine results
            trends_dict = {}
            total_incidents = 0

            # Process schedules data
            for row in schedules_result.fetchall():
                month_label = row[1]
                count = row[2]
                if month_label not in trends_dict:
                    trends_dict[month_label] = {"schedules": 0, "histories": 0, "total": 0}
                trends_dict[month_label]["schedules"] = count
                trends_dict[month_label]["total"] += count
                total_incidents += count

            # Process histories data
            for row in histories_result.fetchall():
                month_label = row[1]
                count = row[2]
                if month_label not in trends_dict:
                    trends_dict[month_label] = {"schedules": 0, "histories": 0, "total": 0}
                trends_dict[month_label]["histories"] = count
                trends_dict[month_label]["total"] += count
                total_incidents += count

            # Convert to list format and analyze trend
            trends = []
            for month_label in sorted(trends_dict.keys()):
                data = trends_dict[month_label]
                trends.append({
                    "month": month_label,
                    "schedules_count": data["schedules"],
                    "histories_count": data["histories"],
                    "total_count": data["total"]
                })

            # Simple trend analysis
            trend_analysis = "Stable"
            if len(trends) >= 2:
                recent_avg = sum(t["total_count"] for t in trends[-3:]) / min(3, len(trends[-3:]))
                earlier_avg = sum(t["total_count"] for t in trends[:3]) / min(3, len(trends[:3]))

                if recent_avg > earlier_avg * 1.2:
                    trend_analysis = "Increasing"
                elif recent_avg < earlier_avg * 0.8:
                    trend_analysis = "Decreasing"

            return {
                "incident_trend": trends,
                "total_incidents": total_incidents,
                "trend_analysis": trend_analysis,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting incident trend insight: {str(e)}")
            return {
                "incident_trend": [],
                "total_incidents": 0,
                "trend_analysis": "Error analyzing trend",
                "error": str(e)
            }

    def get_most_unsafe_locations_insight(self, customer_id: Optional[str] = None,
                                        start_date: Optional[datetime] = None,
                                        end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get most unsafe locations insight - same logic as incidents by location but specifically for "Where?" question
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Get incident-related subtag IDs only
            incident_subtag_ids = self._get_all_subtag_ids(customer_id)

            if not incident_subtag_ids:
                return {
                    "most_unsafe_locations": [],
                    "total_incidents": 0,
                    "safety_analysis": "No location data available",
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(incident_subtag_ids)

            # Build conditions for templates
            template_conditions = [f'ptc."subTagId" IN {subtag_ids_tuple}']
            template_where = " AND ".join(template_conditions)

            # Query to get location information from incident forms with date filtering - specifically "Where?" question
            location_query = text(f"""
                WITH incident_forms AS (
                    -- Get incident forms from schedules with date filtering
                    SELECT DISTINCT cl.id as checklist_id
                    FROM "ProcessSafetyTemplatesCollections" ptc
                    JOIN "ProcessSafetySchedules" ps ON ptc.id = ps."templateId"
                    JOIN "CheckLists" cl ON ptc.id = cl."templateId"
                    WHERE {template_where}
                    AND ps."createdAt" >= :start_date
                    AND ps."createdAt" <= :end_date

                    UNION

                    -- Get incident forms from histories with date filtering
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
                    COUNT(*) as incident_count
                FROM incident_forms if
                JOIN "ChecklistQuestions" cq ON if.checklist_id = cq."checklistId"
                JOIN "ChecklistAnswers" ca ON cq.id = ca."question"
                WHERE LOWER(cq."text") = 'where?'
                AND ca."answer" IS NOT NULL
                AND CAST(ca."answer" AS TEXT) != '[]'
                AND CAST(ca."answer" AS TEXT) != ''
                AND CAST(ca."answer" AS TEXT) != 'null'
                AND LENGTH(CAST(ca."answer" AS TEXT)) > 2
                GROUP BY ca."answer"
                ORDER BY incident_count DESC
                LIMIT 10
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            result = self.db_session.execute(location_query, params)
            rows = result.fetchall()

            unsafe_locations = []
            total_incidents = 0

            # Process location answers
            for row in rows:
                answer = str(row[0]).strip() if row[0] else ""
                incident_count = row[1]

                if answer:
                    # Clean and normalize location name
                    location = self._normalize_location_name(answer)
                    if location != "Unknown":
                        unsafe_locations.append({
                            "location": location,
                            "incident_count": incident_count
                        })
                        total_incidents += incident_count

            # Safety analysis
            safety_analysis = "No significant safety concerns identified"
            if unsafe_locations:
                top_location = unsafe_locations[0]
                if top_location["incident_count"] >= 3:
                    safety_analysis = f"High risk area identified: {top_location['location']} with {top_location['incident_count']} incidents"
                elif len(unsafe_locations) >= 5:
                    safety_analysis = f"Multiple locations showing safety concerns. Top location: {top_location['location']}"
                else:
                    safety_analysis = f"Moderate safety concerns. Most incidents at: {top_location['location']}"

            return {
                "most_unsafe_locations": unsafe_locations,
                "total_incidents": total_incidents,
                "safety_analysis": safety_analysis,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting most unsafe locations insight: {str(e)}")
            return {
                "most_unsafe_locations": [],
                "total_incidents": 0,
                "safety_analysis": "Error analyzing location safety",
                "error": str(e)
            }

    def get_all_incident_kpis(self, customer_id: Optional[str] = None,
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get all incident investigation KPIs in a single response
        Total: 13 KPIs (11 main KPIs + 2 insights)
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Last year

            # Get all 11 main KPIs
            incidents_reported = self.get_incidents_reported(customer_id, start_date, end_date)

            # Get trends for all time periods (weekly, monthly, yearly)
            weekly_trends = self.get_incident_reporting_trends(customer_id, start_date, end_date, "weekly")
            monthly_trends = self.get_incident_reporting_trends(customer_id, start_date, end_date, "monthly")
            yearly_trends = self.get_incident_reporting_trends(customer_id, start_date, end_date, "yearly")

            open_incidents = self.get_open_incidents(customer_id, start_date, end_date)
            closed_incidents = self.get_closed_incidents(customer_id, start_date, end_date)
            completion_time = self.get_investigation_completion_time(customer_id, start_date, end_date)
            incident_types = self.get_incident_types_classification(customer_id, start_date, end_date)
            actions_created = self.get_number_of_actions_created(customer_id, start_date, end_date)
            open_actions_percentage = self.get_percentage_of_open_actions(customer_id, start_date, end_date)
            people_injured = self.get_number_of_people_injured(customer_id, start_date, end_date)
            incidents_by_location = self.get_incidents_by_location(customer_id, start_date, end_date)
            days_since_last_incident = self.get_days_since_last_incident(customer_id)

            # Get 2 insights
            incident_trend_insight = self.get_incident_trend_insight(customer_id, start_date, end_date)
            unsafe_locations_insight = self.get_most_unsafe_locations_insight(customer_id, start_date, end_date)

            # Format trends data for frontend compatibility
            def format_trends_for_frontend(trends_data):
                """Convert backend trend format to frontend expected format"""
                trends = trends_data.get("trends", [])
                return [
                    {
                        "period": trend["period"],
                        "count": trend["total_count"],  # Frontend expects 'count' not 'total_count'
                        "schedules_count": trend["schedules_count"],
                        "histories_count": trend["histories_count"],
                        "total_count": trend["total_count"]
                    }
                    for trend in trends
                ]

            return {
                # Main KPIs (11 total)
                "incidents_reported": incidents_reported.get("total_incidents", 0),
                "incident_reporting_trends": format_trends_for_frontend(monthly_trends),  # Default to monthly for backward compatibility
                "incident_reporting_trends_weekly": format_trends_for_frontend(weekly_trends),
                "incident_reporting_trends_monthly": format_trends_for_frontend(monthly_trends),
                "incident_reporting_trends_yearly": format_trends_for_frontend(yearly_trends),
                "open_incidents": open_incidents.get("open_incidents", 0),
                "closed_incidents": closed_incidents.get("closed_incidents", 0),
                "investigation_completion_time_mins": completion_time.get("average_completion_time_mins", 0),
                "total_completed_investigations": completion_time.get("total_completed_investigations", 0),
                "incident_types": incident_types.get("incident_types", {}),
                "actions_created": actions_created.get("total_actions_created", 0),
                "open_actions_percentage": open_actions_percentage.get("open_actions_percentage", 0.0),
                "people_injured": people_injured.get("total_people_injured", 0),
                "incidents_by_location": incidents_by_location.get("incidents_by_location", {}),
                "days_since_last_incident": days_since_last_incident.get("days_since_last_incident"),

                # Insights (2 total)
                "incident_trend_insight": incident_trend_insight,
                "most_unsafe_locations_insight": unsafe_locations_insight,

                # Metadata
                "last_incident_date": days_since_last_incident.get("last_incident_date"),
                "last_incident_source": days_since_last_incident.get("source"),
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_kpis_count": 13,
                "main_kpis_count": 11,
                "insights_count": 2
            }

        except Exception as e:
            logger.error(f"Error getting all incident KPIs: {str(e)}")
            return {
                # Main KPIs (11 total)
                "incidents_reported": 0,
                "incident_reporting_trends": [],
                "open_incidents": 0,
                "closed_incidents": 0,
                "investigation_completion_time_mins": 0,
                "total_completed_investigations": 0,
                "incident_types": {},
                "actions_created": 0,
                "open_actions_percentage": 0.0,
                "people_injured": 0,
                "incidents_by_location": {},
                "days_since_last_incident": None,

                # Insights (2 total)
                "incident_trend_insight": {"incident_trend": [], "total_incidents": 0, "trend_analysis": "Error"},
                "most_unsafe_locations_insight": {"most_unsafe_locations": [], "total_incidents": 0, "safety_analysis": "Error"},

                # Metadata
                "last_incident_date": None,
                "last_incident_source": None,
                "total_kpis_count": 13,
                "main_kpis_count": 11,
                "insights_count": 2,
                "error": str(e)
            }


# Utility function for easy usage
def extract_incident_kpis(db_session: Session, customer_id: Optional[str] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Utility function to extract all incident investigation KPIs

    Args:
        db_session: SQLAlchemy database session
        customer_id: Optional customer ID to filter data
        start_date: Optional start date for filtering (defaults to 1 year ago)
        end_date: Optional end date for filtering (defaults to now)

    Returns:
        Dictionary containing all incident investigation KPIs
    """
    extractor = IncidentKPIsExtractor(db_session)
    return extractor.get_all_incident_kpis(customer_id, start_date, end_date)
