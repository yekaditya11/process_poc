"""
Permit to Work Data Extractor
Extracts and processes permit to work data from ProcessSafety database
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database_config import db_manager

class PermitToWorkExtractor:
    """Extracts permit to work data for AI summarization"""

    def __init__(self):
        self.session = db_manager.get_process_safety_session()

    def get_permit_summary_data(self, customer_id: Optional[str] = None,
                               days_back: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive permit to work summary data

        Args:
            customer_id: Optional customer filter
            days_back: Number of days to look back for data

        Returns:
            Dictionary containing permit to work summary data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Base query conditions
        conditions = ['psa."createdAt" >= :start_date', 'psa."createdAt" <= :end_date']
        params = {"start_date": start_date, "end_date": end_date}

        if customer_id:
            conditions.append('psa."customerId" = :customer_id')
            params["customer_id"] = customer_id

        where_clause = " AND ".join(conditions)

        # Get overall permit statistics
        permit_stats = self._get_permit_statistics(where_clause, params)

        # Get permit status breakdown
        status_breakdown = self._get_status_breakdown(where_clause, params)

        # Get template type breakdown
        template_breakdown = self._get_template_breakdown(where_clause, params)

        # Get permit trends
        permit_trends = self._get_permit_trends(where_clause, params)

        # Get overdue permits
        overdue_permits = self._get_overdue_permits(customer_id)

        # Get completion performance
        completion_performance = self._get_completion_performance(where_clause, params)

        # Get user performance
        user_performance = self._get_user_performance(where_clause, params)

        return {
            "summary_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days_covered": days_back
            },
            "permit_statistics": permit_stats,
            "status_breakdown": status_breakdown,
            "template_breakdown": template_breakdown,
            "permit_trends": permit_trends,
            "overdue_permits": overdue_permits,
            "completion_performance": completion_performance,
            "user_performance": user_performance
        }

    def _get_permit_statistics(self, where_clause: str, params: Dict) -> Dict[str, Any]:
        """Get basic permit statistics"""
        query = f"""
        SELECT
            COUNT(*) as total_permits,
            COUNT(CASE WHEN psa.status = 'completed' THEN 1 END) as completed_permits,
            COUNT(CASE WHEN psa.status = 'in_progress' THEN 1 END) as in_progress_permits,
            COUNT(CASE WHEN psa.status = 'pending' THEN 1 END) as pending_permits,
            COUNT(CASE WHEN psa."dueDate" < CURRENT_TIMESTAMP AND psa.status != 'completed' THEN 1 END) as overdue_permits,
            CASE WHEN COUNT(*) > 0 THEN ROUND(COUNT(CASE WHEN psa.status = 'completed' THEN 1 END) * 100.0 / COUNT(*), 2) ELSE 0 END as completion_rate,
            AVG(EXTRACT(DAY FROM (psa."submissionDate" - psa."createdAt"))) as avg_completion_days
        FROM "ProcessSafetyAssignments" psa
        WHERE {where_clause}
        """

        result = self.session.execute(text(query), params).fetchone()
        return {
            "total_permits": result.total_permits,
            "completed_permits": result.completed_permits,
            "in_progress_permits": result.in_progress_permits,
            "pending_permits": result.pending_permits,
            "overdue_permits": result.overdue_permits,
            "completion_rate": float(result.completion_rate or 0),
            "avg_completion_days": float(result.avg_completion_days or 0)
        }

    def _get_status_breakdown(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get permit status breakdown"""
        query = f"""
        SELECT
            psa.status,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM "ProcessSafetyAssignments" psa
        WHERE {where_clause}
        GROUP BY psa.status
        ORDER BY count DESC
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "status": row.status,
                "count": row.count,
                "percentage": float(row.percentage)
            }
            for row in results
        ]

    def _get_template_breakdown(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get permit template type breakdown"""
        query = f"""
        SELECT
            ptc."templateName",
            ptc.type,
            COUNT(psa.id) as permit_count,
            COUNT(CASE WHEN psa.status = 'completed' THEN 1 END) as completed_count,
            CASE WHEN COUNT(psa.id) > 0 THEN ROUND(COUNT(CASE WHEN psa.status = 'completed' THEN 1 END) * 100.0 / COUNT(psa.id), 2) ELSE 0 END as completion_rate
        FROM "ProcessSafetyAssignments" psa
        JOIN "ProcessSafetyTemplatesCollections" ptc ON psa."templateId" = ptc.id
        WHERE {where_clause}
        GROUP BY ptc."templateName", ptc.type
        ORDER BY permit_count DESC

        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "template_name": row.templateName,
                "template_type": row.type,
                "permit_count": row.permit_count,
                "completed_count": row.completed_count,
                "completion_rate": float(row.completion_rate or 0)
            }
            for row in results
        ]

    def _get_permit_trends(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get permit trends by day"""
        query = f"""
        SELECT
            DATE(psa."createdAt") as permit_date,
            COUNT(*) as permits_created,
            COUNT(CASE WHEN psa."submissionDate" IS NOT NULL THEN 1 END) as permits_completed
        FROM "ProcessSafetyAssignments" psa
        WHERE {where_clause}
        GROUP BY DATE(psa."createdAt")
        ORDER BY permit_date
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "date": row.permit_date.isoformat() if row.permit_date else None,
                "permits_created": row.permits_created,
                "permits_completed": row.permits_completed
            }
            for row in results
        ]

    def _get_overdue_permits(self, customer_id: Optional[str]) -> List[Dict[str, Any]]:
        """Get detailed overdue permits information"""
        conditions = ['psa."dueDate" < CURRENT_TIMESTAMP', 'psa.status != \'completed\'']
        params = {}

        if customer_id:
            conditions.append('psa."customerId" = :customer_id')
            params["customer_id"] = customer_id

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT
            psa.id,
            ptc."templateName",
            ptc.type as template_type,
            psa.status,
            psa."dueDate",
            EXTRACT(DAY FROM (CURRENT_TIMESTAMP - psa."dueDate")) as days_overdue,
            up.name as completed_by_name,
            c."companyName"
        FROM "ProcessSafetyAssignments" psa
        JOIN "ProcessSafetyTemplatesCollections" ptc ON psa."templateId" = ptc.id
        LEFT JOIN "Users" u ON psa."completedBy" = u.id
        LEFT JOIN "UserProfiles" up ON u.id = up."userId"
        LEFT JOIN "Customers" c ON psa."customerId" = c.id
        WHERE {where_clause}
        ORDER BY days_overdue DESC

        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "permit_id": str(row.id),
                "template_name": row.templateName,
                "template_type": row.template_type,
                "status": row.status,
                "due_date": row.dueDate.isoformat() if row.dueDate else None,
                "days_overdue": int(row.days_overdue or 0),
                "assigned_to": row.completed_by_name,
                "company": row.companyName
            }
            for row in results
        ]

    def _get_completion_performance(self, where_clause: str, params: Dict) -> Dict[str, Any]:
        """Get permit completion performance metrics"""
        query = f"""
        SELECT
            COUNT(*) as total_permits,
            COUNT(CASE WHEN psa.status = 'completed' THEN 1 END) as completed_permits,
            COUNT(CASE WHEN psa."submissionDate" <= psa."dueDate" THEN 1 END) as on_time_completions,
            AVG(EXTRACT(DAY FROM (psa."submissionDate" - psa."createdAt"))) as avg_completion_time,
            AVG(EXTRACT(DAY FROM (psa."dueDate" - psa."createdAt"))) as avg_allowed_time
        FROM "ProcessSafetyAssignments" psa
        WHERE {where_clause} AND psa.status = 'completed'
        """

        result = self.session.execute(text(query), params).fetchone()
        total_permits = result.total_permits or 0
        on_time_rate = (result.on_time_completions / total_permits * 100) if total_permits > 0 else 0

        return {
            "total_completed": total_permits,
            "on_time_completions": result.on_time_completions or 0,
            "on_time_completion_rate": round(on_time_rate, 2),
            "avg_completion_time_days": float(result.avg_completion_time or 0),
            "avg_allowed_time_days": float(result.avg_allowed_time or 0)
        }

    def _get_user_performance(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get user performance metrics for permits"""
        query = f"""
        SELECT
            up.name as user_name,
            up.department,
            COUNT(psa.id) as total_permits,
            COUNT(CASE WHEN psa.status = 'completed' THEN 1 END) as completed_permits,
            COUNT(CASE WHEN psa."dueDate" < CURRENT_TIMESTAMP AND psa.status != 'completed' THEN 1 END) as overdue_permits,
            CASE WHEN COUNT(psa.id) > 0 THEN ROUND(COUNT(CASE WHEN psa.status = 'completed' THEN 1 END) * 100.0 / COUNT(psa.id), 2) ELSE 0 END as completion_rate,
            AVG(EXTRACT(DAY FROM (psa."submissionDate" - psa."createdAt"))) as avg_completion_days
        FROM "ProcessSafetyAssignments" psa
        JOIN "Users" u ON psa."completedBy" = u.id
        JOIN "UserProfiles" up ON u.id = up."userId"
        WHERE {where_clause}
        GROUP BY u.id, up.name, up.department
        HAVING COUNT(psa.id) >= 2
        ORDER BY completion_rate DESC, total_permits DESC
      
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "user_name": row.user_name,
                "department": row.department,
                "total_permits": row.total_permits,
                "completed_permits": row.completed_permits,
                "overdue_permits": row.overdue_permits,
                "completion_rate": float(row.completion_rate or 0),
                "avg_completion_days": float(row.avg_completion_days or 0)
            }
            for row in results
        ]