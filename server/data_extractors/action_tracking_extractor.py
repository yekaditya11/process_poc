"""
Action Tracking Data Extractor
Extracts and processes action tracking data from SafetyConnect database
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database_config import db_manager

class ActionTrackingExtractor:
    """Extracts action tracking data for AI summarization"""

    def __init__(self):
        self.session = db_manager.get_safety_connect_session()

    def get_action_summary_data(self, customer_id: Optional[str] = None,
                               days_back: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive action tracking summary data

        Args:
            customer_id: Optional customer filter
            days_back: Number of days to look back for data

        Returns:
            Dictionary containing action tracking summary data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Base query conditions
        conditions = ['at."createdAt" >= :start_date', 'at."createdAt" <= :end_date', 'at."isDeleted" = false']
        params = {"start_date": start_date, "end_date": end_date}

        if customer_id:
            conditions.append('at."customerId" = :customer_id')
            params["customer_id"] = customer_id

        where_clause = " AND ".join(conditions)

        # Get overall action statistics
        action_stats = self._get_action_statistics(where_clause, params)

        # Get action status breakdown
        status_breakdown = self._get_status_breakdown(where_clause, params)

        # Get priority breakdown
        priority_breakdown = self._get_priority_breakdown(where_clause, params)

        # Get category breakdown
        category_breakdown = self._get_category_breakdown(where_clause, params)

        # Get overdue actions
        overdue_actions = self._get_overdue_actions(customer_id)

        # Get action completion trends
        completion_trends = self._get_completion_trends(where_clause, params)

        # Get action owner performance
        owner_performance = self._get_owner_performance(where_clause, params)

        # Get location-based analysis
        location_analysis = self._get_location_analysis(where_clause, params)

        return {
            "summary_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days_covered": days_back
            },
            "action_statistics": action_stats,
            "status_breakdown": status_breakdown,
            "priority_breakdown": priority_breakdown,
            "category_breakdown": category_breakdown,
            "overdue_actions": overdue_actions,
            "completion_trends": completion_trends,
            "owner_performance": owner_performance,
            "location_analysis": location_analysis
        }

    def _get_action_statistics(self, where_clause: str, params: Dict) -> Dict[str, Any]:
        """Get basic action statistics"""
        query = f"""
        SELECT
            COUNT(*) as total_actions,
            COUNT(CASE WHEN at."actionStatus" = 'completed' THEN 1 END) as completed_actions,
            COUNT(CASE WHEN at."actionStatus" = 'in_progress' THEN 1 END) as in_progress_actions,
            COUNT(CASE WHEN at."actionStatus" = 'pending' THEN 1 END) as pending_actions,
            COUNT(CASE WHEN at."dueDate" < CURRENT_TIMESTAMP AND at."actionStatus" != 'completed' THEN 1 END) as overdue_actions,
            COUNT(CASE WHEN at.priority = 'high' THEN 1 END) as high_priority_actions,
            COUNT(CASE WHEN at.priority = 'critical' THEN 1 END) as critical_priority_actions,
            CASE WHEN COUNT(*) > 0 THEN ROUND(COUNT(CASE WHEN at."actionStatus" = 'completed' THEN 1 END) * 100.0 / COUNT(*), 2) ELSE 0 END as completion_rate,
            AVG(EXTRACT(DAY FROM (at."closureDate" - at."createdAt"))) as avg_completion_days
        FROM "ActionTrackings" at
        WHERE {where_clause}
        """

        result = self.session.execute(text(query), params).fetchone()
        return {
            "total_actions": result.total_actions,
            "completed_actions": result.completed_actions,
            "in_progress_actions": result.in_progress_actions,
            "pending_actions": result.pending_actions,
            "overdue_actions": result.overdue_actions,
            "high_priority_actions": result.high_priority_actions,
            "critical_priority_actions": result.critical_priority_actions,
            "completion_rate": float(result.completion_rate or 0),
            "avg_completion_days": float(result.avg_completion_days or 0)
        }

    def _get_status_breakdown(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get action status breakdown"""
        query = f"""
        SELECT
            at."actionStatus",
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM "ActionTrackings" at
        WHERE {where_clause}
        GROUP BY at."actionStatus"
        ORDER BY count DESC
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "status": row.actionStatus,
                "count": row.count,
                "percentage": float(row.percentage)
            }
            for row in results
        ]

    def _get_priority_breakdown(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get action priority breakdown"""
        query = f"""
        SELECT
            at.priority,
            COUNT(*) as count,
            COUNT(CASE WHEN at."actionStatus" = 'completed' THEN 1 END) as completed_count,
            CASE WHEN COUNT(*) > 0 THEN ROUND(COUNT(CASE WHEN at."actionStatus" = 'completed' THEN 1 END) * 100.0 / COUNT(*), 2) ELSE 0 END as completion_rate
        FROM "ActionTrackings" at
        WHERE {where_clause} AND at.priority IS NOT NULL
        GROUP BY at.priority
        ORDER BY
            CASE at.priority
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
                ELSE 5
            END
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "priority": row.priority,
                "count": row.count,
                "completed_count": row.completed_count,
                "completion_rate": float(row.completion_rate or 0)
            }
            for row in results
        ]

    def _get_category_breakdown(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get action category breakdown"""
        query = f"""
        SELECT
            at.category,
            COUNT(*) as count,
            COUNT(CASE WHEN at."actionStatus" = 'completed' THEN 1 END) as completed_count,
            CASE WHEN COUNT(*) > 0 THEN ROUND(COUNT(CASE WHEN at."actionStatus" = 'completed' THEN 1 END) * 100.0 / COUNT(*), 2) ELSE 0 END as completion_rate
        FROM "ActionTrackings" at
        WHERE {where_clause} AND at.category IS NOT NULL
        GROUP BY at.category
        ORDER BY count DESC
      
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "category": row.category,
                "count": row.count,
                "completed_count": row.completed_count,
                "completion_rate": float(row.completion_rate or 0)
            }
            for row in results
        ]

    def _get_overdue_actions(self, customer_id: Optional[str]) -> List[Dict[str, Any]]:
        """Get detailed overdue actions information"""
        conditions = ['at."dueDate" < CURRENT_TIMESTAMP', 'at."actionStatus" != \'completed\'', 'at."isDeleted" = false']
        params = {}

        if customer_id:
            conditions.append('at."customerId" = :customer_id')
            params["customer_id"] = customer_id

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT
            at.id,
            at.title,
            at.priority,
            at.category,
            at."dueDate",
            at."actionStatus",
            EXTRACT(DAY FROM (CURRENT_TIMESTAMP - at."dueDate")) as days_overdue,
            up_owner.name as action_owner,
            up_manager.name as reporting_manager,
            at.location,
            c."companyName"
        FROM "ActionTrackings" at
        LEFT JOIN "Users" u_owner ON at."actionOwner" = u_owner.id
        LEFT JOIN "UserProfiles" up_owner ON u_owner.id = up_owner."userId"
        LEFT JOIN "Users" u_manager ON at."reportingManager" = u_manager.id
        LEFT JOIN "UserProfiles" up_manager ON u_manager.id = up_manager."userId"
        LEFT JOIN "Customers" c ON at."customerId" = c.id
        WHERE {where_clause}
        ORDER BY days_overdue DESC, at.priority DESC
   
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "action_id": str(row.id),
                "title": row.title,
                "priority": row.priority,
                "category": row.category,
                "due_date": row.dueDate.isoformat() if row.dueDate else None,
                "status": row.actionStatus,
                "days_overdue": int(row.days_overdue or 0),
                "action_owner": row.action_owner,
                "reporting_manager": row.reporting_manager,
                "location": row.location,
                "company": row.companyName
            }
            for row in results
        ]

    def _get_completion_trends(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get action completion trends by day"""
        query = f"""
        SELECT
            DATE(at."closureDate") as completion_date,
            COUNT(*) as completed_count,
            COUNT(CASE WHEN at.priority IN ('high', 'critical') THEN 1 END) as high_priority_completed
        FROM "ActionTrackings" at
        WHERE {where_clause} AND at."actionStatus" = 'completed' AND at."closureDate" IS NOT NULL
        GROUP BY DATE(at."closureDate")
        ORDER BY completion_date
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "date": row.completion_date.isoformat() if row.completion_date else None,
                "completed_count": row.completed_count,
                "high_priority_completed": row.high_priority_completed
            }
            for row in results
        ]

    def _get_owner_performance(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get action owner performance metrics"""
        query = f"""
        SELECT
            up.name as owner_name,
            up.department,
            COUNT(at.id) as total_actions,
            COUNT(CASE WHEN at."actionStatus" = 'completed' THEN 1 END) as completed_actions,
            COUNT(CASE WHEN at."dueDate" < CURRENT_TIMESTAMP AND at."actionStatus" != 'completed' THEN 1 END) as overdue_actions,
            CASE WHEN COUNT(at.id) > 0 THEN ROUND(COUNT(CASE WHEN at."actionStatus" = 'completed' THEN 1 END) * 100.0 / COUNT(at.id), 2) ELSE 0 END as completion_rate,
            AVG(EXTRACT(DAY FROM (at."closureDate" - at."createdAt"))) as avg_completion_days
        FROM "ActionTrackings" at
        JOIN "Users" u ON at."actionOwner" = u.id
        JOIN "UserProfiles" up ON u.id = up."userId"
        WHERE {where_clause}
        GROUP BY u.id, up.name, up.department
        HAVING COUNT(at.id) >= 3
        ORDER BY completion_rate DESC, total_actions DESC
    
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "owner_name": row.owner_name,
                "department": row.department,
                "total_actions": row.total_actions,
                "completed_actions": row.completed_actions,
                "overdue_actions": row.overdue_actions,
                "completion_rate": float(row.completion_rate or 0),
                "avg_completion_days": float(row.avg_completion_days or 0)
            }
            for row in results
        ]

    def _get_location_analysis(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get location-based action analysis"""
        query = f"""
        SELECT
            at.location,
            COUNT(*) as total_actions,
            COUNT(CASE WHEN at."actionStatus" = 'completed' THEN 1 END) as completed_actions,
            COUNT(CASE WHEN at.priority IN ('high', 'critical') THEN 1 END) as high_priority_actions,
            CASE WHEN COUNT(*) > 0 THEN ROUND(COUNT(CASE WHEN at."actionStatus" = 'completed' THEN 1 END) * 100.0 / COUNT(*), 2) ELSE 0 END as completion_rate
        FROM "ActionTrackings" at
        WHERE {where_clause} AND at.location IS NOT NULL
        GROUP BY at.location
        HAVING COUNT(*) > 0
        ORDER BY total_actions DESC
       
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "location": row.location,
                "total_actions": row.total_actions,
                "completed_actions": row.completed_actions,
                "high_priority_actions": row.high_priority_actions,
                "completion_rate": float(row.completion_rate or 0)
            }
            for row in results
        ]
