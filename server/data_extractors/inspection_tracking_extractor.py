"""
Inspection Tracking Data Extractor
Extracts and processes inspection tracking data from SafetyConnect database
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database_config import db_manager

class InspectionTrackingExtractor:
    """Extracts inspection tracking data for AI summarization"""

    def __init__(self):
        self.session = db_manager.get_safety_connect_session()

    def get_inspection_summary_data(self, customer_id: Optional[str] = None,
                                   days_back: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive inspection tracking summary data

        Args:
            customer_id: Optional customer filter
            days_back: Number of days to look back for data

        Returns:
            Dictionary containing inspection tracking summary data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Base query conditions
        conditions = ['it."createdAt" >= :start_date', 'it."createdAt" <= :end_date', 'it."isDeleted" = false']
        params = {"start_date": start_date, "end_date": end_date}

        if customer_id:
            conditions.append('it."customerId" = :customer_id')
            params["customer_id"] = customer_id

        where_clause = " AND ".join(conditions)

        # Get overall inspection statistics
        inspection_stats = self._get_inspection_statistics(where_clause, params)

        # Get inspection assignment statistics
        assignment_stats = self._get_assignment_statistics(customer_id, days_back)

        # Get overdue inspections
        overdue_inspections = self._get_overdue_inspections(customer_id)

        # Get upcoming inspections
        upcoming_inspections = self._get_upcoming_inspections(customer_id)

        # Get inspection completion trends
        completion_trends = self._get_completion_trends(customer_id, days_back)

        # Get checklist compliance analysis
        compliance_analysis = self._get_compliance_analysis(customer_id, days_back)

        # Get inspection frequency analysis
        frequency_analysis = self._get_frequency_analysis(where_clause, params)

        # Get hierarchy-based analysis
        hierarchy_analysis = self._get_hierarchy_analysis(where_clause, params)

        return {
            "summary_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days_covered": days_back
            },
            "inspection_statistics": inspection_stats,
            "assignment_statistics": assignment_stats,
            "overdue_inspections": overdue_inspections,
            "upcoming_inspections": upcoming_inspections,
            "completion_trends": completion_trends,
            "compliance_analysis": compliance_analysis,
            "frequency_analysis": frequency_analysis,
            "hierarchy_analysis": hierarchy_analysis
        }

    def _get_inspection_statistics(self, where_clause: str, params: Dict) -> Dict[str, Any]:
        """Get basic inspection statistics"""
        query = f"""
        SELECT
            COUNT(*) as total_inspections,
            COUNT(CASE WHEN it."needApproval" = true THEN 1 END) as inspections_requiring_approval,
            COUNT(CASE WHEN it."isAssetEnabled" = true THEN 1 END) as asset_enabled_inspections,
            COUNT(CASE WHEN it."dueDate" < CURRENT_TIMESTAMP THEN 1 END) as overdue_inspections,
            COUNT(CASE WHEN it."dueDate" >= CURRENT_TIMESTAMP AND it."dueDate" <= CURRENT_TIMESTAMP + INTERVAL '7 days' THEN 1 END) as due_this_week,
            AVG(it."alertDays") as avg_alert_days
        FROM "InspectionTrackings" it
        WHERE {where_clause}
        """

        result = self.session.execute(text(query), params).fetchone()
        return {
            "total_inspections": result.total_inspections,
            "inspections_requiring_approval": result.inspections_requiring_approval,
            "asset_enabled_inspections": result.asset_enabled_inspections,
            "overdue_inspections": result.overdue_inspections,
            "due_this_week": result.due_this_week,
            "avg_alert_days": float(result.avg_alert_days or 0)
        }

    def _get_assignment_statistics(self, customer_id: Optional[str], days_back: int) -> Dict[str, Any]:
        """Get inspection assignment statistics"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        conditions = ['ia."createdAt" >= :start_date', 'ia."createdAt" <= :end_date']
        params = {"start_date": start_date, "end_date": end_date}

        if customer_id:
            conditions.append('ia."customerId" = :customer_id')
            params["customer_id"] = customer_id

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT
            COUNT(*) as total_assignments,
            COUNT(CASE WHEN ia."inspectionStatus" = 'completed' THEN 1 END) as completed_assignments,
            COUNT(CASE WHEN ia."inspectionStatus" = 'pending' THEN 1 END) as pending_assignments,
            COUNT(CASE WHEN ia."inspectionStatus" = 'in_progress' THEN 1 END) as in_progress_assignments,
            CASE WHEN COUNT(*) > 0 THEN ROUND(COUNT(CASE WHEN ia."inspectionStatus" = 'completed' THEN 1 END) * 100.0 / COUNT(*), 2) ELSE 0 END as completion_rate,
            AVG(EXTRACT(DAY FROM (ia."updatedAt" - ia."createdAt"))) as avg_completion_days
        FROM "InspectionAssignments" ia
        WHERE {where_clause}
        """

        result = self.session.execute(text(query), params).fetchone()
        return {
            "total_assignments": result.total_assignments,
            "completed_assignments": result.completed_assignments,
            "pending_assignments": result.pending_assignments,
            "in_progress_assignments": result.in_progress_assignments,
            "completion_rate": float(result.completion_rate or 0),
            "avg_completion_days": float(result.avg_completion_days or 0)
        }

    def _get_overdue_inspections(self, customer_id: Optional[str]) -> List[Dict[str, Any]]:
        """Get detailed overdue inspections information"""
        conditions = ['it."dueDate" < CURRENT_TIMESTAMP', 'it."isDeleted" = false']
        params = {}

        if customer_id:
            conditions.append('it."customerId" = :customer_id')
            params["customer_id"] = customer_id

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT
            it.id,
            it.title,
            it.description,
            it."dueDate",
            it."occuranceType",
            EXTRACT(DAY FROM (CURRENT_TIMESTAMP - it."dueDate")) as days_overdue,
            up.name as created_by,
            c."companyName",
            cl.id as checklist_id
        FROM "InspectionTrackings" it
        LEFT JOIN "Users" u ON it."createdBy" = u.id
        LEFT JOIN "UserProfiles" up ON u.id = up."userId"
        LEFT JOIN "Customers" c ON it."customerId" = c.id
        LEFT JOIN "CheckLists" cl ON it."checklistId" = cl.id
        WHERE {where_clause}
        ORDER BY days_overdue DESC
        LIMIT 15
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "inspection_id": str(row.id),
                "title": row.title,
                "description": row.description[:200] + "..." if row.description and len(row.description) > 200 else row.description,
                "due_date": row.dueDate.isoformat() if row.dueDate else None,
                "occurrence_type": row.occuranceType,
                "days_overdue": int(row.days_overdue or 0),
                "created_by": row.created_by,
                "company": row.companyName,
                "has_checklist": row.checklist_id is not None
            }
            for row in results
        ]

    def _get_upcoming_inspections(self, customer_id: Optional[str]) -> List[Dict[str, Any]]:
        """Get upcoming inspections in next 30 days"""
        conditions = [
            'it."dueDate" >= CURRENT_TIMESTAMP',
            'it."dueDate" <= CURRENT_TIMESTAMP + INTERVAL \'30 days\'',
            'it."isDeleted" = false'
        ]
        params = {}

        if customer_id:
            conditions.append('it."customerId" = :customer_id')
            params["customer_id"] = customer_id

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT
            it.id,
            it.title,
            it.description,
            it."dueDate",
            it."occuranceType",
            it."alertDays",
            EXTRACT(DAY FROM (it."dueDate" - CURRENT_TIMESTAMP)) as days_until_due,
            up.name as created_by,
            c."companyName"
        FROM "InspectionTrackings" it
        LEFT JOIN "Users" u ON it."createdBy" = u.id
        LEFT JOIN "UserProfiles" up ON u.id = up."userId"
        LEFT JOIN "Customers" c ON it."customerId" = c.id
        WHERE {where_clause}
        ORDER BY it."dueDate" ASC
        LIMIT 15
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "inspection_id": str(row.id),
                "title": row.title,
                "description": row.description[:200] + "..." if row.description and len(row.description) > 200 else row.description,
                "due_date": row.dueDate.isoformat() if row.dueDate else None,
                "occurrence_type": row.occuranceType,
                "alert_days": row.alertDays,
                "days_until_due": int(row.days_until_due or 0),
                "created_by": row.created_by,
                "company": row.companyName
            }
            for row in results
        ]

    def _get_completion_trends(self, customer_id: Optional[str], days_back: int) -> List[Dict[str, Any]]:
        """Get inspection completion trends"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        conditions = ['ia."updatedAt" >= :start_date', 'ia."updatedAt" <= :end_date', 'ia."inspectionStatus" = \'completed\'']
        params = {"start_date": start_date, "end_date": end_date}

        if customer_id:
            conditions.append('ia."customerId" = :customer_id')
            params["customer_id"] = customer_id

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT
            DATE(ia."updatedAt") as completion_date,
            COUNT(*) as completed_count
        FROM "InspectionAssignments" ia
        WHERE {where_clause}
        GROUP BY DATE(ia."updatedAt")
        ORDER BY completion_date
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "date": row.completion_date.isoformat() if row.completion_date else None,
                "completed_count": row.completed_count
            }
            for row in results
        ]

    def _get_compliance_analysis(self, customer_id: Optional[str], days_back: int) -> Dict[str, Any]:
        """Get checklist compliance analysis for inspections"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        conditions = ['ca."createdAt" >= :start_date', 'ca."createdAt" <= :end_date']
        params = {"start_date": start_date, "end_date": end_date}

        if customer_id:
            # Join through ChecklistAssignments to get customer filter
            conditions.append('cla."customerId" = :customer_id')
            params["customer_id"] = customer_id

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT
            COUNT(ca.id) as total_answers,
            COUNT(CASE WHEN ca.evidence IS NOT NULL THEN 1 END) as answers_with_evidence,
            CASE WHEN COUNT(ca.id) > 0 THEN ROUND(COUNT(CASE WHEN ca.evidence IS NOT NULL THEN 1 END) * 100.0 / COUNT(ca.id), 2) ELSE 0 END as evidence_rate,
            COUNT(CASE WHEN ca.answer IS NOT NULL THEN 1 END) as answered_questions,
            CASE WHEN COUNT(ca.id) > 0 THEN ROUND(COUNT(CASE WHEN ca.answer IS NOT NULL THEN 1 END) * 100.0 / COUNT(ca.id), 2) ELSE 0 END as answer_rate
        FROM "ChecklistAnswers" ca
        JOIN "ChecklistAssignments" cla ON ca."ChecklistAssignmentId" = cla.id
        WHERE {where_clause}
        """

        result = self.session.execute(text(query), params).fetchone()
        return {
            "total_answers": result.total_answers,
            "answers_with_evidence": result.answers_with_evidence,
            "evidence_submission_rate": float(result.evidence_rate or 0),
            "answered_questions": result.answered_questions,
            "answer_rate": float(result.answer_rate or 0)
        }

    def _get_frequency_analysis(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get inspection frequency analysis"""
        query = f"""
        SELECT
            it."occuranceType",
            COUNT(*) as count,
            COUNT(CASE WHEN it."dueDate" < CURRENT_TIMESTAMP THEN 1 END) as overdue_count,
            CASE WHEN COUNT(*) > 0 THEN ROUND(COUNT(CASE WHEN it."dueDate" < CURRENT_TIMESTAMP THEN 1 END) * 100.0 / COUNT(*), 2) ELSE 0 END as overdue_rate
        FROM "InspectionTrackings" it
        WHERE {where_clause} AND it."occuranceType" IS NOT NULL
        GROUP BY it."occuranceType"
        ORDER BY count DESC
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "occurrence_type": row.occuranceType,
                "count": row.count,
                "overdue_count": row.overdue_count,
                "overdue_rate": float(row.overdue_rate or 0)
            }
            for row in results
        ]

    def _get_hierarchy_analysis(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get hierarchy-based inspection analysis"""
        query = f"""
        SELECT
            COALESCE(it.hierarchy->>'department', 'Unknown') as department,
            COUNT(*) as inspection_count,
            COUNT(CASE WHEN it."dueDate" < CURRENT_TIMESTAMP THEN 1 END) as overdue_count,
            AVG(it."alertDays") as avg_alert_days
        FROM "InspectionTrackings" it
        WHERE {where_clause}
        GROUP BY COALESCE(it.hierarchy->>'department', 'Unknown')
        HAVING COUNT(*) > 0
        ORDER BY inspection_count DESC
        LIMIT 10
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "department": row.department,
                "inspection_count": row.inspection_count,
                "overdue_count": row.overdue_count,
                "avg_alert_days": float(row.avg_alert_days or 0)
            }
            for row in results
        ]
