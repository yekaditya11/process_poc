"""
Action Tracking KPIs Extractor

This module extracts Action Tracking KPIs from ProcessSafety database tables.
Focuses specifically on action tracking module data using subTagId filtering.

KPIs Implemented:
1. Number of Actions Created - count of rows in schedules + histories tables (filter by action tracking subTagIds)
2. % of Actions Completed On Time - actions with "additionalStatus" = "SUBMITTED_ON_TIME" in attribute column
3. Open vs Closed Actions - open actions in schedules table, closed actions in histories table

Insights Implemented:
1. Employees which do not complete their actions on time - users with "additionalStatus" = "OVERDUE"

Database Schema:
- ProcessSafetyTags: Contains module tags including "Action Tracking"
- ProcessSafetySubTags: Contains subtags linked to Action Tracking module via tagId
- ProcessSafetySchedules: Contains open actions (filtered by subTagId for Action Tracking)
- ProcessSafetyHistories: Contains closed actions (filtered by subTagId for Action Tracking)
- Users: For user information
- UserProfiles: Contains department information (department field)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
import json

logger = logging.getLogger(__name__)


class ActionTrackingKPIsExtractor:
    """Extract Action Tracking KPIs from ProcessSafety tables"""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self._action_tracking_subtag_ids = None

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

    def _get_action_tracking_subtag_ids(self, customer_id: Optional[str] = None) -> List[str]:
        """Get subTagIds for action tracking module using Action Tracking tag filtering"""
        if self._action_tracking_subtag_ids is not None:
            return self._action_tracking_subtag_ids

        try:
            # Filter by Action Tracking module using tag name
            query = text("""
                SELECT DISTINCT pst.id
                FROM "ProcessSafetySubTags" pst
                JOIN "ProcessSafetyTags" pt ON pst."tagId" = pt.id
                WHERE LOWER(pt."tagName") LIKE '%action%'
                AND (pst."isDeleted" = false OR pst."isDeleted" IS NULL)
            """)

            result = self._execute_query_safely(query)
            self._action_tracking_subtag_ids = [row[0] for row in result.fetchall()]

            logger.info(f"Found {len(self._action_tracking_subtag_ids)} action tracking subTagIds")
            return self._action_tracking_subtag_ids

        except Exception as e:
            logger.error(f"Error getting action tracking subTagIds: {str(e)}")
            return []

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

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(action_subtag_ids)

            # Count actions in schedules table (open actions)
            schedules_query = text(f"""
                SELECT COUNT(*) 
                FROM "ProcessSafetySchedules" ps
                WHERE ps."subTagId" IN {subtag_ids_tuple}
                AND ps."createdAt" >= :start_date
                AND ps."createdAt" <= :end_date
            """)

            # Count actions in histories table (closed actions)
            histories_query = text(f"""
                SELECT COUNT(*) 
                FROM "ProcessSafetyHistories" ph
                WHERE ph."subTagId" IN {subtag_ids_tuple}
                AND ph."createdAt" >= :start_date
                AND ph."createdAt" <= :end_date
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
            # Rollback the transaction to recover from any error
            try:
                self.db_session.rollback()
            except:
                pass
            return {
                "total_actions_created": 0,
                "schedules_count": 0,
                "histories_count": 0,
                "error": str(e)
            }

    def get_percentage_of_actions_completed_on_time(self, customer_id: Optional[str] = None,
                                                  start_date: Optional[datetime] = None,
                                                  end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get percentage of actions completed on time
        Actions completed on time are where "attribute" column has key "additionalStatus" = "SUBMITTED_ON_TIME"
        % of actions completed on time = (completed actions / total actions) * 100
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
                    "total_actions": 0,
                    "completed_on_time": 0,
                    "percentage_completed_on_time": 0.0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(action_subtag_ids)

            # Query both schedules and histories tables for total actions and on-time completions
            combined_query = text(f"""
                WITH all_actions AS (
                    -- Actions from schedules table (open actions)
                    SELECT
                        ps."attribute",
                        'open' as status
                    FROM "ProcessSafetySchedules" ps
                    WHERE ps."subTagId" IN {subtag_ids_tuple}
                    AND ps."createdAt" >= :start_date
                    AND ps."createdAt" <= :end_date

                    UNION ALL

                    -- Actions from histories table (closed actions)
                    SELECT
                        ph."attribute",
                        'closed' as status
                    FROM "ProcessSafetyHistories" ph
                    WHERE ph."subTagId" IN {subtag_ids_tuple}
                    AND ph."createdAt" >= :start_date
                    AND ph."createdAt" <= :end_date
                )
                SELECT
                    COUNT(*) as total_actions,
                    COUNT(CASE
                        WHEN "attribute"::jsonb->>'additionalStatus' = 'SUBMITTED_ON_TIME'
                        THEN 1
                    END) as completed_on_time
                FROM all_actions
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }

            result = self.db_session.execute(combined_query, params)
            row = result.fetchone()

            total_actions = row[0] if row[0] else 0
            completed_on_time = row[1] if row[1] else 0

            # Calculate percentage
            percentage_completed_on_time = (completed_on_time / total_actions * 100) if total_actions > 0 else 0.0

            return {
                "total_actions": total_actions,
                "completed_on_time": completed_on_time,
                "percentage_completed_on_time": round(percentage_completed_on_time, 2),
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting percentage of actions completed on time: {str(e)}")
            # Rollback the transaction to recover from any error
            try:
                self.db_session.rollback()
            except:
                pass
            return {
                "total_actions": 0,
                "completed_on_time": 0,
                "percentage_completed_on_time": 0.0,
                "error": str(e)
            }

    def get_open_vs_closed_actions(self, customer_id: Optional[str] = None,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get open vs closed actions
        Open actions are actions that exist in schedules table
        Closed actions are actions that exist in histories table
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
                    "closed_actions": 0,
                    "total_actions": 0,
                    "open_percentage": 0.0,
                    "closed_percentage": 0.0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(action_subtag_ids)

            # Count open actions in schedules table
            open_actions_query = text(f"""
                SELECT COUNT(*)
                FROM "ProcessSafetySchedules" ps
                WHERE ps."subTagId" IN {subtag_ids_tuple}
                AND ps."createdAt" >= :start_date
                AND ps."createdAt" <= :end_date
            """)

            # Count closed actions in histories table
            closed_actions_query = text(f"""
                SELECT COUNT(*)
                FROM "ProcessSafetyHistories" ph
                WHERE ph."subTagId" IN {subtag_ids_tuple}
                AND ph."createdAt" >= :start_date
                AND ph."createdAt" <= :end_date
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }

            open_result = self.db_session.execute(open_actions_query, params)
            open_actions = open_result.fetchone()[0]

            closed_result = self.db_session.execute(closed_actions_query, params)
            closed_actions = closed_result.fetchone()[0]

            total_actions = open_actions + closed_actions

            # Calculate percentages
            open_percentage = (open_actions / total_actions * 100) if total_actions > 0 else 0.0
            closed_percentage = (closed_actions / total_actions * 100) if total_actions > 0 else 0.0

            return {
                "open_actions": open_actions,
                "closed_actions": closed_actions,
                "total_actions": total_actions,
                "open_percentage": round(open_percentage, 2),
                "closed_percentage": round(closed_percentage, 2),
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting open vs closed actions: {str(e)}")
            # Rollback the transaction to recover from any error
            try:
                self.db_session.rollback()
            except:
                pass
            return {
                "open_actions": 0,
                "closed_actions": 0,
                "total_actions": 0,
                "open_percentage": 0.0,
                "closed_percentage": 0.0,
                "error": str(e)
            }

    def get_employees_not_completing_on_time(self, customer_id: Optional[str] = None,
                                           start_date: Optional[datetime] = None,
                                           end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get employees which do not complete their actions on time
        Schedules where "attribute" column has key "additionalStatus" = "OVERDUE", userId column is the associated user
        History table "attribute" column has key "additionalStatus" = "OVERDUE" and "associatedUsers" contains user info
        Get user name from "UserProfiles" table

        Note: associatedUsers in ProcessSafetyHistories is stored as JSONB array (jsonb[])
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
                    "overdue_employees": [],
                    "total_overdue_employees": 0,
                    "overdue_actions_count": 0,
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }

            # Convert list to tuple for SQL IN clause
            subtag_ids_tuple = tuple(action_subtag_ids)

            # Query for overdue actions from schedules table
            schedules_query = text(f"""
                SELECT DISTINCT
                    ps."userId",
                    up."name" as user_name,
                    up."department",
                    COUNT(*) as overdue_count
                FROM "ProcessSafetySchedules" ps
                LEFT JOIN "UserProfiles" up ON ps."userId" = up."userId"
                WHERE ps."subTagId" IN {subtag_ids_tuple}
                AND ps."createdAt" >= :start_date
                AND ps."createdAt" <= :end_date
                AND ps."attribute"::jsonb->>'additionalStatus' = 'OVERDUE'
                GROUP BY ps."userId", up."name", up."department"
            """)

            # Query for overdue actions from histories table
            # Note: associatedUsers is array of JSON strings, we need to parse each string and extract associatedId
            histories_query = text(f"""
                WITH unnested_users AS (
                    SELECT
                        ph.id,
                        ph."attribute",
                        ph."createdAt",
                        unnest(ph."associatedUsers") as user_json_string
                    FROM "ProcessSafetyHistories" ph
                    WHERE ph."templateId" IN (
                        SELECT DISTINCT ptc.id
                        FROM "ProcessSafetyTemplatesCollections" ptc
                        WHERE ptc."subTagId" IN {subtag_ids_tuple}
                    )
                    AND ph."createdAt" >= :start_date
                    AND ph."createdAt" <= :end_date
                    AND ph."attribute"::jsonb->>'additionalStatus' = 'OVERDUE'
                ),
                parsed_users AS (
                    SELECT
                        uu.id,
                        uu."attribute",
                        uu."createdAt",
                        (uu.user_json_string::jsonb->>'associatedId')::uuid as user_id
                    FROM unnested_users uu
                    WHERE uu.user_json_string::jsonb->>'associatedId' IS NOT NULL
                    AND uu.user_json_string::jsonb->>'idType' = 'userId'
                )
                SELECT DISTINCT
                    pu.user_id,
                    up."name" as user_name,
                    up."department",
                    COUNT(*) as overdue_count
                FROM parsed_users pu
                LEFT JOIN "UserProfiles" up ON pu.user_id = up."userId"
                GROUP BY pu.user_id, up."name", up."department"
            """)

            params = {
                "start_date": start_date,
                "end_date": end_date
            }

            # Execute schedules query
            schedules_result = self.db_session.execute(schedules_query, params)
            schedules_data = schedules_result.fetchall()

            # Execute histories query with error handling
            histories_data = []
            try:
                histories_result = self.db_session.execute(histories_query, params)
                histories_data = histories_result.fetchall()
            except Exception as hist_error:
                logger.warning(f"Error querying histories for overdue employees: {str(hist_error)}")
                # Rollback the transaction to recover from the error
                self.db_session.rollback()
                logger.info("Skipping histories table for overdue employees due to data structure issues")

            # Combine and aggregate results
            employee_overdue_map = {}
            total_overdue_actions = 0

            # Process schedules data
            for row in schedules_data:
                user_id, user_name, department, overdue_count = row
                if user_id:
                    key = str(user_id)
                    if key not in employee_overdue_map:
                        employee_overdue_map[key] = {
                            "user_id": str(user_id),
                            "user_name": user_name or "Unknown",
                            "department": department or "Unknown",
                            "overdue_actions_count": 0
                        }
                    employee_overdue_map[key]["overdue_actions_count"] += overdue_count
                    total_overdue_actions += overdue_count

            # Process histories data
            for row in histories_data:
                user_id, user_name, department, overdue_count = row
                if user_id:
                    key = str(user_id)
                    if key not in employee_overdue_map:
                        employee_overdue_map[key] = {
                            "user_id": str(user_id),
                            "user_name": user_name or "Unknown",
                            "department": department or "Unknown",
                            "overdue_actions_count": 0
                        }
                    employee_overdue_map[key]["overdue_actions_count"] += overdue_count
                    total_overdue_actions += overdue_count

            # Convert to list and sort by overdue count (descending)
            overdue_employees = list(employee_overdue_map.values())
            overdue_employees.sort(key=lambda x: x["overdue_actions_count"], reverse=True)

            return {
                "overdue_employees": overdue_employees,
                "total_overdue_employees": len(overdue_employees),
                "overdue_actions_count": total_overdue_actions,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting employees not completing on time: {str(e)}")
            # Rollback the transaction to recover from any error
            try:
                self.db_session.rollback()
            except:
                pass
            return {
                "overdue_employees": [],
                "total_overdue_employees": 0,
                "overdue_actions_count": 0,
                "error": str(e)
            }

    def get_all_action_tracking_kpis(self, customer_id: Optional[str] = None,
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get all Action Tracking KPIs and insights in a single call
        """
        try:
            logger.info("Extracting all Action Tracking KPIs and insights...")

            # Get all KPIs
            actions_created = self.get_number_of_actions_created(customer_id, start_date, end_date)
            completion_on_time = self.get_percentage_of_actions_completed_on_time(customer_id, start_date, end_date)
            open_vs_closed = self.get_open_vs_closed_actions(customer_id, start_date, end_date)

            # Get insights
            overdue_employees = self.get_employees_not_completing_on_time(customer_id, start_date, end_date)

            # Format data for frontend compatibility
            total_actions = actions_created.get("total_actions_created", 0)
            on_time_percentage = completion_on_time.get("percentage_completed_on_time", 0.0)
            late_actions = total_actions - completion_on_time.get("completed_on_time", 0)

            return {
                # Frontend-compatible field names and structure
                "actions_created": {
                    "total_actions": total_actions,
                    "actions_this_period": total_actions,  # Same as total for this period
                    **actions_created  # Include all original data
                },
                "on_time_completion": {
                    "on_time_percentage": on_time_percentage,
                    "late_actions": late_actions,
                    **completion_on_time  # Include all original data
                },
                "action_status": {
                    "open_actions": open_vs_closed.get("open_actions", 0),
                    "closed_actions": open_vs_closed.get("closed_actions", 0),
                    "in_progress_actions": open_vs_closed.get("open_actions", 0),  # Assume open = in progress
                    "total_actions": open_vs_closed.get("total_actions", 0),
                    **open_vs_closed  # Include all original data
                },
                "overdue_employees": {
                    "overdue_count": overdue_employees.get("total_overdue_employees", 0),
                    "overdue_employees": overdue_employees.get("overdue_employees", []),
                    **overdue_employees  # Include all original data
                },

                # Keep original structure for backward compatibility
                "action_tracking_kpis": {
                    "number_of_actions_created": actions_created,
                    "percentage_completed_on_time": completion_on_time,
                    "open_vs_closed_actions": open_vs_closed,
                },
                "action_tracking_insights": {
                    "employees_not_completing_on_time": overdue_employees,
                },
                "summary": {
                    "total_actions": total_actions,
                    "open_actions": open_vs_closed.get("open_actions", 0),
                    "closed_actions": open_vs_closed.get("closed_actions", 0),
                    "on_time_completion_rate": on_time_percentage,
                    "total_overdue_employees": overdue_employees.get("total_overdue_employees", 0),
                    "total_overdue_actions": overdue_employees.get("overdue_actions_count", 0)
                },
                "extraction_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting all action tracking KPIs: {str(e)}")
            return {
                # Frontend-compatible field names with error state
                "actions_created": {
                    "total_actions": 0,
                    "actions_this_period": 0,
                    "error": str(e)
                },
                "on_time_completion": {
                    "on_time_percentage": 0.0,
                    "late_actions": 0,
                    "error": str(e)
                },
                "action_status": {
                    "open_actions": 0,
                    "closed_actions": 0,
                    "in_progress_actions": 0,
                    "total_actions": 0,
                    "error": str(e)
                },
                "overdue_employees": {
                    "overdue_count": 0,
                    "overdue_employees": [],
                    "error": str(e)
                },

                # Keep original structure for backward compatibility
                "action_tracking_kpis": {},
                "error": str(e),
                "extraction_timestamp": datetime.now().isoformat()
            }


# Standalone function for testing and external usage
def get_action_tracking_kpis(customer_id: Optional[str] = None, days_back: int = 365) -> Dict[str, Any]:
    """
    Standalone function to get Action Tracking KPIs

    Args:
        customer_id: Optional customer ID for filtering
        days_back: Number of days to look back from current date

    Returns:
        Dictionary containing all Action Tracking KPIs
    """
    try:
        # Import database configuration
        import sys
        import os
        # Add the server directory to Python path
        server_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if server_dir not in sys.path:
            sys.path.append(server_dir)

        from config.database_config import db_manager

        # Get database session (using ProcessSafety database for action tracking)
        db_session = db_manager.get_process_safety_session()
        if not db_session:
            return {"error": "Failed to get database session"}

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Create extractor and get KPIs
        extractor = ActionTrackingKPIsExtractor(db_session)
        kpis = extractor.get_all_action_tracking_kpis(customer_id, start_date, end_date)

        # Close session
        db_session.close()

        return kpis

    except Exception as e:
        logger.error(f"Error in standalone get_action_tracking_kpis: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    """Test the Action Tracking KPIs extractor"""

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    print("🚀 Testing Action Tracking KPIs Extractor...")

    # Test with default parameters (last 30 days)
    kpis = get_action_tracking_kpis(days_back=30)

    if "error" in kpis:
        print(f"❌ Error: {kpis['error']}")
    else:
        print("✅ Successfully extracted Action Tracking KPIs!")
        print(f"📊 Total Actions: {kpis.get('summary', {}).get('total_actions', 0)}")
        print(f"📈 Open Actions: {kpis.get('summary', {}).get('open_actions', 0)}")
        print(f"📉 Closed Actions: {kpis.get('summary', {}).get('closed_actions', 0)}")
        print(f"⏰ On-time Completion Rate: {kpis.get('summary', {}).get('on_time_completion_rate', 0)}%")
        print(f"⚠️ Overdue Employees: {kpis.get('summary', {}).get('total_overdue_employees', 0)}")
        print(f"🔴 Overdue Actions: {kpis.get('summary', {}).get('total_overdue_actions', 0)}")

        # Print detailed results
        print("\n📋 Detailed KPIs:")
        for kpi_name, kpi_data in kpis.get("action_tracking_kpis", {}).items():
            print(f"  {kpi_name}: {kpi_data}")

        print("\n🔍 Detailed Insights:")
        for insight_name, insight_data in kpis.get("action_tracking_insights", {}).items():
            print(f"  {insight_name}: {insight_data}")

    print("\n🎯 Action Tracking KPIs extraction completed!")
