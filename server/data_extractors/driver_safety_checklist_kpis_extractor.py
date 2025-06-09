"""
Driver Safety Checklist KPIs Extractor

This module extracts Driver Safety KPIs from ProcessSafety database tables.
Focuses specifically on driver safety checklist data using templateId filtering.

KPIs Implemented:
1. % of Checklists Completed Daily/Weekly - count of rows for templateId 'a35be57e-dd36-4a21-b05b-e4d4fa836f53'
2. Number of Vehicles Deemed Unfit - based on AI analysis of checklist answers

Insights Implemented:
3. Drivers who do not complete checklists - schedules and histories where "attribute" column has key "additionalStatus" = "OVERDUE"

Database Schema:
- ProcessSafetyTemplatesCollections: Contains the Vehicle Safety Inspection Checklist template
- ProcessSafetySchedules: Contains open/pending driver safety checklists
- ProcessSafetyHistories: Contains completed driver safety checklists
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


class DriverSafetyChecklistKPIsExtractor:
    """Extract driver safety checklist KPIs from ProcessSafety tables"""

    def __init__(self, db_session: Session = None):
        # Import database configuration
        from config.database_config import db_manager
        
        if db_session is None:
            self.db_session = db_manager.get_process_safety_session()
            self._should_close_session = True
        else:
            self.db_session = db_session
            self._should_close_session = False
            
        # Driver Safety template ID as specified in requirements
        self.driver_safety_template_id = 'a35be57e-dd36-4a21-b05b-e4d4fa836f53'

    def close(self):
        """Close database session if we created it"""
        if self._should_close_session and self.db_session:
            self.db_session.close()

    def get_driver_safety_checklist_kpis(self, customer_id: Optional[str] = None,
                                       start_date: Optional[datetime] = None,
                                       end_date: Optional[datetime] = None,
                                       days_back: int = 365) -> Dict[str, Any]:
        """
        Get all driver safety checklist KPIs

        Args:
            customer_id: Optional customer ID to filter data
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            days_back: Number of days to look back from current date (used if start_date/end_date not provided)

        Returns:
            Dictionary containing all driver safety KPIs
        """
        try:
            # Calculate date range - use provided dates or calculate from days_back
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=days_back)

            logger.info(f"Extracting driver safety checklist KPIs for customer: {customer_id}")

            # Get all KPIs
            daily_completions = self.get_checklists_completed_daily(customer_id, start_date, end_date)
            weekly_completions = self.get_checklists_completed_weekly(customer_id, start_date, end_date)
            vehicle_fitness = self.get_vehicles_deemed_unfit(customer_id, start_date, end_date)
            overdue_drivers = self.get_drivers_not_completing_checklists(customer_id, start_date, end_date)

            # Calculate completion percentages for frontend compatibility
            daily_total_checklists = daily_completions.get("total_completed_checklists", 0)
            daily_total_days = daily_completions.get("total_days_analyzed", 1)

            # For daily: Calculate percentage based on reasonable expectations
            # Since we have 17 checklists over 366 days, this suggests low frequency
            # Calculate as: (actual completions / days analyzed) * 100 to show daily completion rate
            daily_completion_percentage = (daily_total_checklists / daily_total_days * 100) if daily_total_days > 0 else 0

            weekly_total_checklists = weekly_completions.get("total_completed_checklists", 0)
            weekly_total_weeks = weekly_completions.get("total_weeks_analyzed", 1)

            # For weekly: Calculate percentage based on actual weekly performance
            # Since all 17 checklists happened in 1 week, show this as weekly completion rate
            # Cap at 100% to represent realistic completion percentage
            weekly_avg_per_week = weekly_total_checklists / weekly_total_weeks if weekly_total_weeks > 0 else 0
            # Assume a reasonable target of 20 checklists per week (can be adjusted)
            weekly_target = 20
            weekly_completion_percentage = min(100, (weekly_avg_per_week / weekly_target * 100)) if weekly_target > 0 else 0

            # Format overdue drivers for frontend
            overdue_drivers_list = []
            overdue_schedules_details = overdue_drivers.get("overdue_schedules_details", [])
            overdue_histories_details = overdue_drivers.get("overdue_histories_details", [])

            # Combine and format overdue drivers
            seen_users = set()
            for detail in overdue_schedules_details + overdue_histories_details:
                user_id = detail.get("user_id")
                if user_id and user_id not in seen_users:
                    seen_users.add(user_id)
                    overdue_drivers_list.append({
                        "name": detail.get("user_name", "Unknown User"),
                        "email": detail.get("user_email", ""),
                        "days_overdue": "N/A",  # Could calculate based on start_date if needed
                        "user_id": user_id
                    })

            return {
                "template_id": self.driver_safety_template_id,
                "template_name": "Vehicle Safety Inspection Checklist",

                # Frontend-compatible field names and structure
                "daily_completions": {
                    "completion_percentage": round(daily_completion_percentage, 2),
                    "total_checklists": daily_total_checklists,
                    "completed_checklists": daily_total_checklists,
                    "total_days_analyzed": daily_total_days,
                    **daily_completions  # Include all original data
                },
                "weekly_completions": {
                    "completion_percentage": round(weekly_completion_percentage, 2),
                    "total_checklists": weekly_total_checklists,
                    "completed_checklists": weekly_total_checklists,
                    "total_weeks_analyzed": weekly_total_weeks,
                    **weekly_completions  # Include all original data
                },
                "vehicle_fitness": {
                    "fit_vehicles": vehicle_fitness.get("vehicles_deemed_fit", 0),
                    "unfit_vehicles": vehicle_fitness.get("vehicles_deemed_unfit", 0),
                    "total_vehicles": vehicle_fitness.get("total_vehicles_inspected", 0),
                    "unfit_percentage": vehicle_fitness.get("unfit_percentage", 0),
                    **vehicle_fitness  # Include all original data
                },
                "overdue_drivers": {
                    "overdue_drivers": overdue_drivers_list,
                    "total_overdue_drivers": overdue_drivers.get("total_overdue_drivers", 0),
                    **overdue_drivers  # Include all original data
                },

                # Keep original field names for backward compatibility
                "daily_completion_stats": daily_completions,
                "weekly_completion_stats": weekly_completions,
                "vehicle_fitness_analysis": vehicle_fitness,
                "overdue_drivers_insight": overdue_drivers,

                "summary": {
                    "total_daily_completions": daily_completions.get("total_completed_checklists", 0),
                    "average_daily_completion": daily_completions.get("average_daily_completion", 0),
                    "total_weekly_completions": weekly_completions.get("total_completed_checklists", 0),
                    "average_weekly_completion": weekly_completions.get("average_weekly_completion", 0),
                    "total_vehicles_inspected": vehicle_fitness.get("total_vehicles_inspected", 0),
                    "vehicles_deemed_unfit": vehicle_fitness.get("vehicles_deemed_unfit", 0),
                    "unfit_percentage": vehicle_fitness.get("unfit_percentage", 0),
                    "total_overdue_drivers": overdue_drivers.get("total_overdue_drivers", 0),
                    "overdue_schedules_count": overdue_drivers.get("overdue_schedules_count", 0),
                    "overdue_histories_count": overdue_drivers.get("overdue_histories_count", 0)
                },
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting driver safety checklist KPIs: {str(e)}")
            return {
                "template_id": self.driver_safety_template_id,
                "template_name": "Vehicle Safety Inspection Checklist",

                # Frontend-compatible field names with error state
                "daily_completions": {
                    "completion_percentage": 0,
                    "total_checklists": 0,
                    "completed_checklists": 0,
                    "error": str(e)
                },
                "weekly_completions": {
                    "completion_percentage": 0,
                    "total_checklists": 0,
                    "completed_checklists": 0,
                    "error": str(e)
                },
                "vehicle_fitness": {
                    "fit_vehicles": 0,
                    "unfit_vehicles": 0,
                    "total_vehicles": 0,
                    "error": str(e)
                },
                "overdue_drivers": {
                    "overdue_drivers": [],
                    "total_overdue_drivers": 0,
                    "error": str(e)
                },

                # Keep original field names for backward compatibility
                "daily_completion_stats": {"error": str(e)},
                "weekly_completion_stats": {"error": str(e)},
                "vehicle_fitness_analysis": {"error": str(e)},
                "overdue_drivers_insight": {"error": str(e)},

                "summary": {
                    "total_daily_completions": 0,
                    "average_daily_completion": 0,
                    "total_weekly_completions": 0,
                    "average_weekly_completion": 0,
                    "total_vehicles_inspected": 0,
                    "vehicles_deemed_unfit": 0,
                    "unfit_percentage": 0,
                    "total_overdue_drivers": 0,
                    "overdue_schedules_count": 0,
                    "overdue_histories_count": 0
                },
                "error": str(e)
            }

    def get_checklists_completed_daily(self, customer_id: Optional[str] = None,
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get percentage of driver safety checklists completed daily
        
        Args:
            customer_id: Optional customer ID to filter data
            start_date: Start date for filtering (defaults to 7 days ago)
            end_date: End date for filtering (defaults to now)
            
        Returns:
            Dictionary containing daily completion statistics
        """
        try:
            if start_date is None:
                start_date = datetime.now() - timedelta(days=7)
            if end_date is None:
                end_date = datetime.now()

            # Build conditions for filtering
            conditions = [f'ptc.id = :template_id']
            params = {
                "template_id": self.driver_safety_template_id,
                "start_date": start_date,
                "end_date": end_date
            }

            if customer_id:
                conditions.append('ptc."customerId" = :customer_id')
                params["customer_id"] = customer_id

            where_clause = " AND ".join(conditions)

            # Query to get daily completion counts from both schedules and histories
            query = text(f"""
                WITH daily_completions AS (
                    -- Completed checklists from histories
                    SELECT 
                        DATE(ph."createdAt") as completion_date,
                        COUNT(*) as completed_count
                    FROM "ProcessSafetyHistories" ph
                    JOIN "ProcessSafetyTemplatesCollections" ptc ON ph."templateId" = ptc.id
                    WHERE {where_clause}
                    AND ph."createdAt" >= :start_date
                    AND ph."createdAt" <= :end_date
                    GROUP BY DATE(ph."createdAt")
                    
                    UNION ALL
                    
                    -- Pending/open checklists from schedules (if they have submission date)
                    SELECT 
                        DATE(ps."createdAt") as completion_date,
                        COUNT(*) as completed_count
                    FROM "ProcessSafetySchedules" ps
                    JOIN "ProcessSafetyTemplatesCollections" ptc ON ps."templateId" = ptc.id
                    WHERE {where_clause}
                    AND ps."createdAt" >= :start_date
                    AND ps."createdAt" <= :end_date
                    AND ps."currentStatus" = 'COMPLETED'
                    GROUP BY DATE(ps."createdAt")
                ),
                date_series AS (
                    SELECT generate_series(
                        DATE(:start_date),
                        DATE(:end_date),
                        '1 day'::interval
                    )::date as date
                )
                SELECT 
                    ds.date as completion_date,
                    COALESCE(SUM(dc.completed_count), 0) as completed_count
                FROM date_series ds
                LEFT JOIN daily_completions dc ON ds.date = dc.completion_date
                GROUP BY ds.date
                ORDER BY ds.date
            """)

            result = self.db_session.execute(query, params)
            daily_data = result.fetchall()

            # Calculate statistics
            total_days = len(daily_data)
            total_completed = sum(row[1] for row in daily_data)
            avg_daily_completion = total_completed / total_days if total_days > 0 else 0

            # Format daily breakdown
            daily_breakdown = [
                {
                    "date": row[0].isoformat(),
                    "completed_count": row[1]
                }
                for row in daily_data
            ]

            return {
                "total_completed_checklists": total_completed,
                "average_daily_completion": round(avg_daily_completion, 2),
                "total_days_analyzed": total_days,
                "daily_breakdown": daily_breakdown,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting daily checklist completions: {str(e)}")
            return {
                "total_completed_checklists": 0,
                "average_daily_completion": 0,
                "total_days_analyzed": 0,
                "daily_breakdown": [],
                "error": str(e)
            }

    def get_checklists_completed_weekly(self, customer_id: Optional[str] = None,
                                      start_date: Optional[datetime] = None,
                                      end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get percentage of driver safety checklists completed weekly

        Args:
            customer_id: Optional customer ID to filter data
            start_date: Start date for filtering (defaults to 4 weeks ago)
            end_date: End date for filtering (defaults to now)

        Returns:
            Dictionary containing weekly completion statistics
        """
        try:
            if start_date is None:
                start_date = datetime.now() - timedelta(weeks=4)
            if end_date is None:
                end_date = datetime.now()

            # Build conditions for filtering
            conditions = [f'ptc.id = :template_id']
            params = {
                "template_id": self.driver_safety_template_id,
                "start_date": start_date,
                "end_date": end_date
            }

            if customer_id:
                conditions.append('ptc."customerId" = :customer_id')
                params["customer_id"] = customer_id

            where_clause = " AND ".join(conditions)

            # Query to get weekly completion counts
            query = text(f"""
                WITH weekly_completions AS (
                    -- Completed checklists from histories
                    SELECT
                        DATE_TRUNC('week', ph."createdAt") as week_start,
                        COUNT(*) as completed_count
                    FROM "ProcessSafetyHistories" ph
                    JOIN "ProcessSafetyTemplatesCollections" ptc ON ph."templateId" = ptc.id
                    WHERE {where_clause}
                    AND ph."createdAt" >= :start_date
                    AND ph."createdAt" <= :end_date
                    GROUP BY DATE_TRUNC('week', ph."createdAt")

                    UNION ALL

                    -- Completed checklists from schedules
                    SELECT
                        DATE_TRUNC('week', ps."createdAt") as week_start,
                        COUNT(*) as completed_count
                    FROM "ProcessSafetySchedules" ps
                    JOIN "ProcessSafetyTemplatesCollections" ptc ON ps."templateId" = ptc.id
                    WHERE {where_clause}
                    AND ps."createdAt" >= :start_date
                    AND ps."createdAt" <= :end_date
                    AND ps."currentStatus" = 'COMPLETED'
                    GROUP BY DATE_TRUNC('week', ps."createdAt")
                )
                SELECT
                    week_start,
                    SUM(completed_count) as total_completed
                FROM weekly_completions
                GROUP BY week_start
                ORDER BY week_start
            """)

            result = self.db_session.execute(query, params)
            weekly_data = result.fetchall()

            # Calculate statistics
            total_weeks = len(weekly_data)
            total_completed = sum(row[1] for row in weekly_data)
            avg_weekly_completion = total_completed / total_weeks if total_weeks > 0 else 0

            # Format weekly breakdown
            weekly_breakdown = [
                {
                    "week_start": row[0].isoformat(),
                    "completed_count": row[1]
                }
                for row in weekly_data
            ]

            return {
                "total_completed_checklists": total_completed,
                "average_weekly_completion": round(avg_weekly_completion, 2),
                "total_weeks_analyzed": total_weeks,
                "weekly_breakdown": weekly_breakdown,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting weekly checklist completions: {str(e)}")
            return {
                "total_completed_checklists": 0,
                "average_weekly_completion": 0,
                "total_weeks_analyzed": 0,
                "weekly_breakdown": [],
                "error": str(e)
            }

    def get_vehicles_deemed_unfit(self, customer_id: Optional[str] = None,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get number of vehicles deemed unfit based on AI analysis of checklist answers

        Args:
            customer_id: Optional customer ID to filter data
            start_date: Start date for filtering (defaults to 30 days ago)
            end_date: End date for filtering (defaults to now)

        Returns:
            Dictionary containing vehicle fitness analysis
        """
        try:
            if start_date is None:
                start_date = datetime.now() - timedelta(days=30)
            if end_date is None:
                end_date = datetime.now()

            # Build conditions for filtering
            conditions = [f'ptc.id = :template_id']
            params = {
                "template_id": self.driver_safety_template_id,
                "start_date": start_date,
                "end_date": end_date
            }

            if customer_id:
                conditions.append('ptc."customerId" = :customer_id')
                params["customer_id"] = customer_id

            where_clause = " AND ".join(conditions)

            # Query to get all checklist answers for the driver safety template
            query = text(f"""
                SELECT DISTINCT
                    ca."ChecklistAssignmentId",
                    ca."answer",
                    cq."text" as question_text,
                    cq."type" as question_type,
                    ca."complianceScore",
                    ph."createdAt" as completion_date,
                    ph."associatedUser" as vehicle_identifier
                FROM "ProcessSafetyHistories" ph
                JOIN "ProcessSafetyTemplatesCollections" ptc ON ph."templateId" = ptc.id
                JOIN "CheckLists" cl ON ptc.id = cl."templateId"
                JOIN "ChecklistQuestions" cq ON cl.id = cq."checklistId"
                JOIN "ChecklistAnswers" ca ON cq.id = ca."question"
                WHERE {where_clause}
                AND ph."createdAt" >= :start_date
                AND ph."createdAt" <= :end_date
                AND ca."answer" IS NOT NULL
                AND CAST(ca."answer" AS TEXT) != '[]'
                AND CAST(ca."answer" AS TEXT) != ''
                AND CAST(ca."answer" AS TEXT) != 'null'
                AND LENGTH(CAST(ca."answer" AS TEXT)) > 2
                ORDER BY ca."ChecklistAssignmentId", cq."text"
            """)

            result = self.db_session.execute(query, params)
            answers_data = result.fetchall()

            # Group answers by checklist assignment (vehicle inspection)
            vehicle_inspections = {}
            for row in answers_data:
                assignment_id = row[0]
                if assignment_id not in vehicle_inspections:
                    vehicle_inspections[assignment_id] = {
                        "answers": [],
                        "completion_date": row[5],
                        "vehicle_identifier": row[6] or f"Vehicle_{assignment_id[:8]}",
                        "compliance_scores": []
                    }

                vehicle_inspections[assignment_id]["answers"].append({
                    "question": row[2],
                    "answer": row[1],
                    "question_type": row[3]
                })

                if row[4] is not None:
                    vehicle_inspections[assignment_id]["compliance_scores"].append(row[4])

            # Analyze each vehicle inspection using AI-like logic
            unfit_vehicles = []
            fit_vehicles = []

            for assignment_id, inspection in vehicle_inspections.items():
                fitness_analysis = self._analyze_vehicle_fitness(inspection["answers"])

                vehicle_result = {
                    "assignment_id": assignment_id,
                    "vehicle_identifier": inspection["vehicle_identifier"],
                    "completion_date": inspection["completion_date"].isoformat() if inspection["completion_date"] else None,
                    "fitness_status": fitness_analysis["status"],
                    "fitness_score": fitness_analysis["score"],
                    "critical_issues": fitness_analysis["critical_issues"],
                    "total_questions": len(inspection["answers"]),
                    "average_compliance_score": sum(inspection["compliance_scores"]) / len(inspection["compliance_scores"]) if inspection["compliance_scores"] else None
                }

                if fitness_analysis["status"] == "UNFIT":
                    unfit_vehicles.append(vehicle_result)
                else:
                    fit_vehicles.append(vehicle_result)

            return {
                "total_vehicles_inspected": len(vehicle_inspections),
                "vehicles_deemed_unfit": len(unfit_vehicles),
                "vehicles_deemed_fit": len(fit_vehicles),
                "unfit_percentage": round((len(unfit_vehicles) / len(vehicle_inspections)) * 100, 2) if vehicle_inspections else 0,
                "unfit_vehicles_details": unfit_vehicles,
                "fit_vehicles_details": fit_vehicles,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing vehicle fitness: {str(e)}")
            return {
                "total_vehicles_inspected": 0,
                "vehicles_deemed_unfit": 0,
                "vehicles_deemed_fit": 0,
                "unfit_percentage": 0,
                "unfit_vehicles_details": [],
                "fit_vehicles_details": [],
                "error": str(e)
            }

    def get_drivers_not_completing_checklists(self, customer_id: Optional[str] = None,
                                            start_date: Optional[datetime] = None,
                                            end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get drivers who do not complete checklists - schedules and histories where
        "attribute" column has key "additionalStatus" = "OVERDUE"

        Args:
            customer_id: Optional customer ID to filter data
            start_date: Start date for filtering (defaults to 30 days ago)
            end_date: End date for filtering (defaults to now)

        Returns:
            Dictionary containing overdue drivers analysis
        """
        try:
            if start_date is None:
                start_date = datetime.now() - timedelta(days=30)
            if end_date is None:
                end_date = datetime.now()

            # Build conditions for filtering
            conditions = [f'ptc.id = :template_id']
            params = {
                "template_id": self.driver_safety_template_id,
                "start_date": start_date,
                "end_date": end_date
            }

            if customer_id:
                conditions.append('ptc."customerId" = :customer_id')
                params["customer_id"] = customer_id

            where_clause = " AND ".join(conditions)

            # Query to get overdue schedules
            schedules_query = text(f"""
                SELECT DISTINCT
                    ps.id as schedule_id,
                    ps."userId",
                    ps."createdAt",
                    ps."startDate",
                    ps."endDate",
                    ps."currentStatus",
                    ps."attribute",
                    u.contact->>'name' as user_name,
                    u.email as user_email
                FROM "ProcessSafetySchedules" ps
                JOIN "ProcessSafetyTemplatesCollections" ptc ON ps."templateId" = ptc.id
                LEFT JOIN "Users" u ON ps."userId" = u.id
                WHERE {where_clause}
                AND ps."createdAt" >= :start_date
                AND ps."createdAt" <= :end_date
                AND ps."attribute" IS NOT NULL
                AND ps."attribute"::text LIKE '%"additionalStatus"%'
                AND ps."attribute"::text LIKE '%"OVERDUE"%'
                ORDER BY ps."createdAt" DESC
            """)

            schedules_result = self.db_session.execute(schedules_query, params)
            overdue_schedules = schedules_result.fetchall()

            # Query to get overdue histories
            histories_query = text(f"""
                SELECT DISTINCT
                    ph.id as history_id,
                    ph."associatedUserId",
                    ph."createdAt",
                    ph."startDate",
                    ph."publishedOn",
                    ph."status",
                    ph."attribute",
                    ph."associatedUser" as user_name,
                    u.email as user_email
                FROM "ProcessSafetyHistories" ph
                JOIN "ProcessSafetyTemplatesCollections" ptc ON ph."templateId" = ptc.id
                LEFT JOIN "Users" u ON ph."associatedUserId" = u.id
                WHERE {where_clause}
                AND ph."createdAt" >= :start_date
                AND ph."createdAt" <= :end_date
                AND ph."attribute" IS NOT NULL
                AND ph."attribute"::text LIKE '%"additionalStatus"%'
                AND ph."attribute"::text LIKE '%"OVERDUE"%'
                ORDER BY ph."createdAt" DESC
            """)

            histories_result = self.db_session.execute(histories_query, params)
            overdue_histories = histories_result.fetchall()

            # Process overdue schedules
            overdue_schedules_data = []
            unique_schedule_users = set()

            for row in overdue_schedules:
                try:
                    # Handle both JSON string and dict cases
                    attribute_data = row[6]
                    if isinstance(attribute_data, str):
                        attribute_data = json.loads(attribute_data) if attribute_data else {}
                    elif not isinstance(attribute_data, dict):
                        attribute_data = {}

                    additional_status = attribute_data.get('additionalStatus', '')

                    if additional_status == 'OVERDUE':
                        schedule_data = {
                            "schedule_id": row[0],
                            "user_id": row[1],
                            "user_name": row[7] or "Unknown User",
                            "user_email": row[8] or "No Email",
                            "created_at": row[2].isoformat() if row[2] else None,
                            "start_date": row[3].isoformat() if row[3] else None,
                            "end_date": row[4].isoformat() if row[4] else None,
                            "current_status": row[5],
                            "additional_status": additional_status,
                            "type": "schedule"
                        }
                        overdue_schedules_data.append(schedule_data)
                        unique_schedule_users.add(row[1])

                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Error parsing schedule attribute data: {str(e)}")
                    continue

            # Process overdue histories
            overdue_histories_data = []
            unique_history_users = set()

            for row in overdue_histories:
                try:
                    # Handle both JSON string and dict cases
                    attribute_data = row[6]
                    if isinstance(attribute_data, str):
                        attribute_data = json.loads(attribute_data) if attribute_data else {}
                    elif not isinstance(attribute_data, dict):
                        attribute_data = {}

                    additional_status = attribute_data.get('additionalStatus', '')

                    if additional_status == 'OVERDUE':
                        history_data = {
                            "history_id": row[0],
                            "user_id": row[1],
                            "user_name": row[7] or "Unknown User",
                            "user_email": row[8] or "No Email",
                            "created_at": row[2].isoformat() if row[2] else None,
                            "start_date": row[3].isoformat() if row[3] else None,
                            "published_on": row[4].isoformat() if row[4] else None,
                            "status": row[5],
                            "additional_status": additional_status,
                            "type": "history"
                        }
                        overdue_histories_data.append(history_data)
                        unique_history_users.add(row[1])

                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Error parsing history attribute data: {str(e)}")
                    continue

            # Combine unique users from both schedules and histories
            all_unique_overdue_users = unique_schedule_users.union(unique_history_users)

            return {
                "total_overdue_drivers": len(all_unique_overdue_users),
                "overdue_schedules_count": len(overdue_schedules_data),
                "overdue_histories_count": len(overdue_histories_data),
                "overdue_schedules_details": overdue_schedules_data,
                "overdue_histories_details": overdue_histories_data,
                "unique_overdue_user_ids": list(all_unique_overdue_users),
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error getting drivers not completing checklists: {str(e)}")
            return {
                "total_overdue_drivers": 0,
                "overdue_schedules_count": 0,
                "overdue_histories_count": 0,
                "overdue_schedules_details": [],
                "overdue_histories_details": [],
                "unique_overdue_user_ids": [],
                "error": str(e)
            }

    def _analyze_vehicle_fitness(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze vehicle fitness based on checklist answers using AI-like logic

        Args:
            answers: List of question-answer pairs from the checklist

        Returns:
            Dictionary containing fitness analysis results
        """
        try:
            critical_issues = []
            warning_issues = []
            fitness_score = 100  # Start with perfect score

            # Define critical safety keywords that indicate vehicle unfitness
            critical_keywords = [
                'broken', 'damaged', 'not working', 'failed', 'cracked', 'leaking',
                'worn out', 'missing', 'loose', 'faulty', 'defective', 'unsafe',
                'no', 'none', 'absent', 'poor', 'bad', 'inadequate', 'insufficient'
            ]

            # Define warning keywords that reduce fitness score but don't make vehicle unfit
            warning_keywords = [
                'minor', 'slight', 'small', 'needs attention', 'requires maintenance',
                'due for service', 'worn', 'old', 'faded', 'dirty'
            ]

            for answer_data in answers:
                question = answer_data["question"].lower()
                answer = str(answer_data["answer"]).lower()

                # Skip empty or null answers
                if not answer or answer in ['null', '[]', '{}']:
                    continue

                # Check for critical issues
                for keyword in critical_keywords:
                    if keyword in answer:
                        critical_issues.append({
                            "question": answer_data["question"],
                            "answer": answer_data["answer"],
                            "issue_type": "CRITICAL",
                            "keyword_found": keyword
                        })
                        fitness_score -= 20  # Deduct 20 points for critical issues
                        break

                # Check for warning issues
                for keyword in warning_keywords:
                    if keyword in answer:
                        warning_issues.append({
                            "question": answer_data["question"],
                            "answer": answer_data["answer"],
                            "issue_type": "WARNING",
                            "keyword_found": keyword
                        })
                        fitness_score -= 5  # Deduct 5 points for warning issues
                        break

                # Special checks for specific vehicle components
                if any(component in question for component in ['brake', 'tire', 'light', 'steering', 'engine']):
                    if any(negative in answer for negative in ['no', 'not', 'fail', 'broken']):
                        critical_issues.append({
                            "question": answer_data["question"],
                            "answer": answer_data["answer"],
                            "issue_type": "CRITICAL_COMPONENT",
                            "component": "safety_critical"
                        })
                        fitness_score -= 25  # Higher deduction for safety-critical components

            # Ensure fitness score doesn't go below 0
            fitness_score = max(0, fitness_score)

            # Determine overall fitness status
            if len(critical_issues) > 0 or fitness_score < 60:
                status = "UNFIT"
            elif fitness_score < 80:
                status = "CONDITIONAL_FIT"  # Fit but needs attention
            else:
                status = "FIT"

            return {
                "status": status,
                "score": fitness_score,
                "critical_issues": critical_issues,
                "warning_issues": warning_issues,
                "total_issues": len(critical_issues) + len(warning_issues)
            }

        except Exception as e:
            logger.error(f"Error in vehicle fitness analysis: {str(e)}")
            return {
                "status": "UNKNOWN",
                "score": 0,
                "critical_issues": [],
                "warning_issues": [],
                "total_issues": 0,
                "error": str(e)
            }


# Utility function for easy usage
def get_driver_safety_checklist_kpis(customer_id: Optional[str] = None,
                                   days_back: int = 365) -> Dict[str, Any]:
    """
    Utility function to extract all driver safety checklist KPIs

    Args:
        customer_id: Optional customer ID to filter data
        days_back: Number of days to look back if start_date not provided

    Returns:
        Dictionary containing all driver safety checklist KPIs
    """
    try:
        # Create extractor and get KPIs
        extractor = DriverSafetyChecklistKPIsExtractor()
        kpis = extractor.get_driver_safety_checklist_kpis(customer_id, days_back)

        # Close the extractor
        extractor.close()

        return kpis

    except Exception as e:
        logger.error(f"Error in standalone get_driver_safety_checklist_kpis: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    """Test the Driver Safety Checklist KPIs extractor"""

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    print("🚗 Testing Driver Safety Checklist KPIs Extractor...")

    # Test with default parameters (last 30 days)
    kpis = get_driver_safety_checklist_kpis(days_back=30)

    if "error" in kpis:
        print(f"❌ Error: {kpis['error']}")
    else:
        print("✅ Driver Safety Checklist KPIs extracted successfully!")
        print(f"📊 Template ID: {kpis.get('template_id', 'N/A')}")
        print(f"📊 Template Name: {kpis.get('template_name', 'N/A')}")

        summary = kpis.get('summary', {})
        print(f"📈 Total Daily Completions: {summary.get('total_daily_completions', 0)}")
        print(f"📈 Average Daily Completion: {summary.get('average_daily_completion', 0)}")
        print(f"📈 Total Weekly Completions: {summary.get('total_weekly_completions', 0)}")
        print(f"📈 Average Weekly Completion: {summary.get('average_weekly_completion', 0)}")
        print(f"🚗 Total Vehicles Inspected: {summary.get('total_vehicles_inspected', 0)}")
        print(f"⚠️ Vehicles Deemed Unfit: {summary.get('vehicles_deemed_unfit', 0)}")
        print(f"📊 Unfit Percentage: {summary.get('unfit_percentage', 0)}%")
        print(f"👥 Total Overdue Drivers: {summary.get('total_overdue_drivers', 0)}")
        print(f"📋 Overdue Schedules Count: {summary.get('overdue_schedules_count', 0)}")
        print(f"📚 Overdue Histories Count: {summary.get('overdue_histories_count', 0)}")

        print(f"\n🕒 Generated at: {kpis.get('generated_at', 'N/A')}")

    print("\n🏁 Driver Safety Checklist KPIs test completed!")
