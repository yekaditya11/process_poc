"""
Incident Management Data Extractor
Extracts and processes incident data from SafetyConnect database
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database_config import db_manager

class IncidentManagementExtractor:
    """Extracts incident management data for AI summarization"""

    def __init__(self):
        self.session = db_manager.get_safety_connect_session()

    def get_incident_summary_data(self, customer_id: Optional[str] = None,
                                 days_back: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive incident management summary data

        Args:
            customer_id: Optional customer filter
            days_back: Number of days to look back for data

        Returns:
            Dictionary containing incident summary data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Base query conditions
        conditions = ['i."createdAt" >= :start_date', 'i."createdAt" <= :end_date']
        params = {"start_date": start_date, "end_date": end_date}

        if customer_id:
            conditions.append('i."customerId" = :customer_id')
            params["customer_id"] = customer_id

        where_clause = " AND ".join(conditions)

        # Get overall incident statistics
        incident_stats = self._get_incident_statistics(where_clause, params)

        # Get incident type breakdown
        type_breakdown = self._get_type_breakdown(where_clause, params)

        # Get incident category breakdown
        category_breakdown = self._get_category_breakdown(where_clause, params)

        # Get incident trends
        incident_trends = self._get_incident_trends(where_clause, params)

        # Get location analysis
        location_analysis = self._get_location_analysis(where_clause, params)

        # Get recent critical incidents
        critical_incidents = self._get_critical_incidents(where_clause, params)

        # Get action status for incidents
        action_status = self._get_incident_action_status(where_clause, params)

        return {
            "summary_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days_covered": days_back
            },
            "incident_statistics": incident_stats,
            "type_breakdown": type_breakdown,
            "category_breakdown": category_breakdown,
            "incident_trends": incident_trends,
            "location_analysis": location_analysis,
            "critical_incidents": critical_incidents,
            "action_status": action_status
        }

    def _get_incident_statistics(self, where_clause: str, params: Dict) -> Dict[str, Any]:
        """Get basic incident statistics"""
        query = f"""
        SELECT
            COUNT(*) as total_incidents,
            COUNT(CASE WHEN i.type ILIKE '%injury%' THEN 1 END) as injury_incidents,
            COUNT(CASE WHEN i.type ILIKE '%near miss%' THEN 1 END) as near_miss_incidents,
            COUNT(CASE WHEN i.type ILIKE '%property damage%' THEN 1 END) as property_damage_incidents,
            0 as on_job_incidents,
            0 as off_job_incidents,
            COUNT(CASE WHEN i.action IS NOT NULL AND i.action != '' THEN 1 END) as incidents_with_actions,
            0 as incidents_with_evidence
        FROM "Incidents" i
        WHERE {where_clause}
        """

        result = self.session.execute(text(query), params).fetchone()
        return {
            "total_incidents": result.total_incidents,
            "injury_incidents": result.injury_incidents,
            "near_miss_incidents": result.near_miss_incidents,
            "property_damage_incidents": result.property_damage_incidents,
            "on_job_incidents": result.on_job_incidents,
            "off_job_incidents": result.off_job_incidents,
            "incidents_with_actions": result.incidents_with_actions,
            "incidents_with_evidence": result.incidents_with_evidence,
            "action_completion_rate": round((result.incidents_with_actions / result.total_incidents * 100), 2) if result.total_incidents > 0 else 0
        }

    def _get_type_breakdown(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get incident type breakdown"""
        query = f"""
        SELECT
            type,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM "Incidents" i
        WHERE {where_clause} AND type IS NOT NULL
        GROUP BY type
        ORDER BY count DESC
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "type": row.type,
                "count": row.count,
                "percentage": float(row.percentage)
            }
            for row in results
        ]

    def _get_category_breakdown(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get incident category breakdown"""
        query = f"""
        SELECT
            category,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM "Incidents" i
        WHERE {where_clause} AND category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "category": row.category,
                "count": row.count,
                "percentage": float(row.percentage)
            }
            for row in results
        ]

    def _get_incident_trends(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get incident trends by day"""
        query = f"""
        SELECT
            DATE(i.datetime) as incident_date,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN type ILIKE '%injury%' THEN 1 END) as injury_count,
            COUNT(CASE WHEN type ILIKE '%near miss%' THEN 1 END) as near_miss_count
        FROM "Incidents" i
        WHERE {where_clause}
        GROUP BY DATE(i.datetime)
        ORDER BY incident_date
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "date": row.incident_date.isoformat() if row.incident_date else None,
                "total_incidents": row.incident_count,
                "injury_count": row.injury_count,
                "near_miss_count": row.near_miss_count
            }
            for row in results
        ]

    def _get_location_analysis(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get incident location analysis"""
        query = f"""
        SELECT
            COALESCE(address->>'location', 'Unknown') as location,
            COUNT(*) as incident_count,
            COUNT(CASE WHEN type ILIKE '%injury%' THEN 1 END) as injury_count
        FROM "Incidents" i
        WHERE {where_clause}
        GROUP BY COALESCE(address->>'location', 'Unknown')
        HAVING COUNT(*) > 0
        ORDER BY incident_count DESC
        LIMIT 10
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "location": row.location,
                "incident_count": row.incident_count,
                "injury_count": row.injury_count
            }
            for row in results
        ]

    def _get_critical_incidents(self, where_clause: str, params: Dict) -> List[Dict[str, Any]]:
        """Get recent critical incidents"""
        query = f"""
        SELECT
            i.id,
            i.type,
            i.category,
            i.description,
            i.datetime,
            i."wasOnJob",
            COALESCE(i.address->>'location', 'Unknown') as location,
            up.name as reported_by,
            c."companyName"
        FROM "Incidents" i
        LEFT JOIN "Users" u ON i."createdBy" = u.id
        LEFT JOIN "UserProfiles" up ON u.id = up."userId"
        LEFT JOIN "Customers" c ON i."customerId" = c.id
        WHERE {where_clause}
        AND (i.type ILIKE '%injury%' OR i.type ILIKE '%serious%' OR i.type ILIKE '%critical%')
        ORDER BY i.datetime DESC
        LIMIT 10
        """

        results = self.session.execute(text(query), params).fetchall()
        return [
            {
                "incident_id": str(row.id),
                "type": row.type,
                "category": row.category,
                "description": row.description[:200] + "..." if row.description and len(row.description) > 200 else row.description,
                "datetime": row.datetime.isoformat() if row.datetime else None,
                "was_on_job": row.wasOnJob,
                "location": row.location,
                "reported_by": row.reported_by,
                "company": row.companyName
            }
            for row in results
        ]

    def _get_incident_action_status(self, where_clause: str, params: Dict) -> Dict[str, Any]:
        """Get action status for incidents"""
        query = f"""
        SELECT
            COUNT(*) as total_incidents,
            COUNT(CASE WHEN action IS NOT NULL AND action != '' THEN 1 END) as incidents_with_actions,
            COUNT(CASE WHEN action IS NULL OR action = '' THEN 1 END) as incidents_without_actions,
            AVG(CASE WHEN action IS NOT NULL AND action != '' THEN
                EXTRACT(DAY FROM (i."updatedAt" - i."createdAt")) END) as avg_action_response_days
        FROM "Incidents" i
        WHERE {where_clause}
        """

        result = self.session.execute(text(query), params).fetchone()
        return {
            "total_incidents": result.total_incidents,
            "incidents_with_actions": result.incidents_with_actions,
            "incidents_without_actions": result.incidents_without_actions,
            "action_completion_rate": round((result.incidents_with_actions / result.total_incidents * 100), 2) if result.total_incidents > 0 else 0,
            "avg_action_response_days": float(result.avg_action_response_days or 0)
        }
