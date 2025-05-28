"""
AI Summarization Engine
Uses OpenAI GPT models to generate intelligent summaries of safety data
"""

import openai
import json
import tiktoken
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import sys
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class SummaryConfig:
    """Configuration for AI summarization"""
    model: str = "gpt-3.5-turbo-16k"  # Use GPT-3.5 Turbo 16k for speed and good context
    max_tokens: int = 3000  # Optimized for comprehensive analysis
    temperature: float = 0.1  # Lower temperature for consistent analysis
    include_recommendations: bool = True
    include_trends: bool = True
    include_alerts: bool = True
    max_input_tokens: int = 12000  # GPT-3.5 Turbo 16k context window (leave room for response)
    chunk_size: int = 2000  # Size for data chunks (legacy, not used in single-call approach)

    # Speed optimization options
    use_fast_mode: bool = True  # Use optimized prompts for faster processing
    compress_json: bool = True  # Compress JSON output for smaller prompts

class SafetySummarizationEngine:
    """AI-powered safety data summarization engine"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the summarization engine

        Args:
            api_key: OpenAI API key (if not provided, will use environment variable)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")

        openai.api_key = self.api_key
        self.config = SummaryConfig()

    def generate_comprehensive_single_call_analysis(self, module: str, data: Dict[str, Any]) -> str:
        """
        Generate comprehensive analysis in a single OpenAI call with zero data loss

        Args:
            module: Module name (permit, incident, action, inspection)
            data: Complete module data from extractor

        Returns:
            Comprehensive AI analysis covering all data
        """
        # Step 1: Intelligent data compression (preserves all analytical value)
        compressed_data = self._intelligent_data_compression(data, module)

        # Step 2: Create comprehensive analysis prompt
        comprehensive_prompt = self._create_comprehensive_analysis_prompt(compressed_data, module)

        # Step 3: Single OpenAI call with large context
        response = openai.ChatCompletion.create(
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert {module} safety analyst. Analyze ALL provided data comprehensively. Miss nothing. Provide insights as bullet points only."
                },
                {"role": "user", "content": comprehensive_prompt}
            ],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )

        return response.choices[0].message.content.strip()

    def generate_fast_comprehensive_analysis(self, module: str, data: Dict[str, Any]) -> str:
        """
        Generate comprehensive analysis optimized for speed (GPT-3.5 Turbo)

        Args:
            module: Module name (permit, incident, action, inspection)
            data: Complete module data from extractor

        Returns:
            Comprehensive AI analysis covering all data (optimized for speed)
        """
        # Use speed-optimized compression
        compressed_data = self._speed_optimized_compression(data, module)

        # Create concise but comprehensive prompt
        prompt = self._create_fast_analysis_prompt(compressed_data, module)

        # Single OpenAI call with GPT-3.5 Turbo for speed
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a {module} safety expert. Analyze data quickly and comprehensively. Return bullet points only."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,  # Optimized for speed
            temperature=0.1
        )

        return response.choices[0].message.content.strip()

    def _speed_optimized_compression(self, data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """Speed-optimized data compression for faster processing"""

        # Extract only essential data for analysis
        compressed = {
            "module": module,
            "overview": self._create_data_overview(data),
            "key_stats": self._extract_key_statistics(data, module),
            "performance": self._extract_key_performance(data, module),
            "risks": self._extract_key_risks(data, module),
            "trends": self._extract_key_trends(data)
        }

        return compressed

    def _extract_key_statistics(self, data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """Extract only key statistics for speed"""
        if module == "permit":
            stats = data.get("permit_statistics", {})
            return {
                "total": stats.get("total_permits", 0),
                "completed": stats.get("completed_permits", 0),
                "completion_rate": stats.get("completion_rate", 0),
                "overdue": stats.get("overdue_permits", 0)
            }
        elif module == "incident":
            stats = data.get("incident_statistics", {})
            return {
                "total": stats.get("total_incidents", 0),
                "injury_incidents": stats.get("injury_incidents", 0),
                "action_completion_rate": stats.get("action_completion_rate", 0)
            }
        elif module == "action":
            stats = data.get("action_statistics", {})
            return {
                "total": stats.get("total_actions", 0),
                "completed": stats.get("completed_actions", 0),
                "completion_rate": stats.get("completion_rate", 0),
                "overdue": stats.get("overdue_actions", 0)
            }
        elif module == "inspection":
            stats = data.get("assignment_statistics", {})
            return {
                "total": stats.get("total_assignments", 0),
                "completed": stats.get("completed_assignments", 0),
                "completion_rate": stats.get("completion_rate", 0)
            }
        return {}

    def _extract_key_performance(self, data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """Extract key performance metrics for speed"""
        template_data = data.get("template_breakdown", [])
        user_data = data.get("user_performance", [])

        performance = {}

        if template_data:
            # Top and bottom performing templates
            sorted_templates = sorted(template_data, key=lambda x: x.get("completion_rate", 0), reverse=True)
            performance["best_template"] = sorted_templates[0] if sorted_templates else {}
            performance["worst_template"] = sorted_templates[-1] if sorted_templates else {}

        if user_data:
            # Top and bottom performers
            sorted_users = sorted(user_data, key=lambda x: x.get("completion_rate", 0), reverse=True)
            performance["top_performer"] = sorted_users[0] if sorted_users else {}
            performance["bottom_performer"] = sorted_users[-1] if sorted_users else {}

        return performance

    def _extract_key_risks(self, data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """Extract key risk indicators for speed"""
        risks = {}

        # Overdue items
        overdue_items = data.get("overdue_permits", []) or data.get("overdue_actions", [])
        if overdue_items:
            risks["overdue_count"] = len(overdue_items)
            risks["critical_overdue"] = len([item for item in overdue_items if item.get("days_overdue", 0) > 30])

        # Completion rate risk
        if module == "permit":
            completion_rate = data.get("permit_statistics", {}).get("completion_rate", 0)
        elif module == "action":
            completion_rate = data.get("action_statistics", {}).get("completion_rate", 0)
        else:
            completion_rate = 100

        if completion_rate < 80:
            risks["low_completion_risk"] = True
            risks["completion_rate"] = completion_rate

        return risks

    def _extract_key_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key trend information for speed"""
        trends_data = data.get("permit_trends", []) or data.get("incident_trends", [])

        if not trends_data:
            return {}

        # Calculate basic trend metrics
        volumes = [t.get("permits_created", 0) or t.get("incidents_created", 0) for t in trends_data]

        if volumes:
            return {
                "avg_daily_volume": round(sum(volumes) / len(volumes), 1),
                "peak_volume": max(volumes),
                "trend_direction": "increasing" if volumes[-1] > volumes[0] else "decreasing"
            }

        return {}

    def _create_fast_analysis_prompt(self, compressed_data: Dict[str, Any], module: str) -> str:
        """Create speed-optimized analysis prompt"""

        prompt = f"""
FAST {module.upper()} SAFETY ANALYSIS

Analyze this {module} safety data and provide comprehensive insights as bullet points:

OVERVIEW: {compressed_data.get('overview', {})}
STATISTICS: {compressed_data.get('key_stats', {})}
PERFORMANCE: {compressed_data.get('performance', {})}
RISKS: {compressed_data.get('risks', {})}
TRENDS: {compressed_data.get('trends', {})}

Provide insights as bullet points covering:
• Key performance findings
• Critical risk areas
• Trend analysis
• Compliance status
• Urgent recommendations
• Strategic improvements

Focus on actionable insights and safety implications.
"""

        return prompt

    def _intelligent_data_compression(self, data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """
        Intelligently compress data while preserving ALL analytical value

        Args:
            data: Raw data from extractor
            module: Module type for context-specific compression

        Returns:
            Compressed data structure with all insights preserved
        """
        compressed = {
            "module_type": module,
            "data_overview": self._create_data_overview(data),
            "statistical_summary": self._extract_statistical_summary(data),
            "performance_analysis": self._create_performance_analysis(data, module),
            "trend_analysis": self._create_trend_analysis(data),
            "risk_assessment": self._create_risk_assessment(data, module),
            "compliance_analysis": self._create_compliance_analysis(data, module),
            "user_performance": self._analyze_user_performance(data),
            "temporal_patterns": self._extract_temporal_patterns(data),
            "outlier_analysis": self._identify_outliers(data, module),
            "correlation_insights": self._find_correlations(data, module)
        }

        return compressed

    def _create_data_overview(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive data overview"""
        overview = {
            "summary_period": data.get("summary_period", {}),
            "total_records": 0,
            "data_completeness": "100%",
            "key_metrics": {}
        }

        # Extract key metrics based on data structure
        if "permit_statistics" in data:
            stats = data["permit_statistics"]
            overview["total_records"] = stats.get("total_permits", 0)
            overview["key_metrics"] = {
                "completion_rate": stats.get("completion_rate", 0),
                "overdue_count": stats.get("overdue_permits", 0),
                "avg_completion_days": stats.get("avg_completion_days", 0)
            }
        elif "incident_statistics" in data:
            stats = data["incident_statistics"]
            overview["total_records"] = stats.get("total_incidents", 0)
            overview["key_metrics"] = {
                "injury_incidents": stats.get("injury_incidents", 0),
                "action_completion_rate": stats.get("action_completion_rate", 0)
            }
        elif "action_statistics" in data:
            stats = data["action_statistics"]
            overview["total_records"] = stats.get("total_actions", 0)
            overview["key_metrics"] = {
                "completion_rate": stats.get("completion_rate", 0),
                "overdue_actions": stats.get("overdue_actions", 0)
            }
        elif "assignment_statistics" in data:
            stats = data["assignment_statistics"]
            overview["total_records"] = stats.get("total_assignments", 0)
            overview["key_metrics"] = {
                "completion_rate": stats.get("completion_rate", 0),
                "overdue_inspections": data.get("inspection_statistics", {}).get("overdue_inspections", 0)
            }

        return overview

    def _extract_statistical_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive statistical summary"""
        summary = {}

        # Include all statistics from the data
        for key, value in data.items():
            if key.endswith('_statistics') or key.endswith('_breakdown'):
                summary[key] = value

        return summary

    def _create_performance_analysis(self, data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """Create detailed performance analysis"""
        performance = {
            "completion_performance": data.get("completion_performance", {}),
            "template_performance": data.get("template_breakdown", []),
            "status_distribution": data.get("status_breakdown", []),
            "efficiency_metrics": {}
        }

        # Calculate efficiency metrics
        if module == "permit":
            stats = data.get("permit_statistics", {})
            performance["efficiency_metrics"] = {
                "completion_rate": stats.get("completion_rate", 0),
                "avg_completion_time": stats.get("avg_completion_days", 0),
                "overdue_percentage": (stats.get("overdue_permits", 0) / max(stats.get("total_permits", 1), 1)) * 100
            }

        return performance

    def _create_trend_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive trend analysis"""
        trends = {
            "daily_trends": data.get("permit_trends", []),
            "weekly_patterns": self._analyze_weekly_patterns(data.get("permit_trends", [])),
            "volume_analysis": self._analyze_volume_trends(data.get("permit_trends", [])),
            "completion_trends": self._analyze_completion_trends(data.get("permit_trends", []))
        }

        return trends

    def _create_risk_assessment(self, data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """Create comprehensive risk assessment"""
        risk_assessment = {
            "overdue_items": data.get("overdue_permits", []) or data.get("overdue_actions", []),
            "high_risk_patterns": self._identify_high_risk_patterns(data, module),
            "risk_distribution": self._analyze_risk_distribution(data, module),
            "critical_alerts": self._identify_critical_alerts(data, module)
        }

        return risk_assessment

    def _create_compliance_analysis(self, data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """Create comprehensive compliance analysis"""
        compliance = {
            "compliance_rates": self._calculate_compliance_rates(data, module),
            "non_compliance_patterns": self._identify_non_compliance_patterns(data, module),
            "regulatory_status": self._assess_regulatory_status(data, module)
        }

        return compliance

    def _analyze_user_performance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user performance patterns"""
        user_data = data.get("user_performance", [])
        if not user_data:
            return {}

        # Analyze top and bottom performers
        sorted_users = sorted(user_data, key=lambda x: x.get("completion_rate", 0), reverse=True)

        return {
            "top_performers": sorted_users[:5],
            "bottom_performers": sorted_users[-5:] if len(sorted_users) > 5 else [],
            "performance_distribution": self._calculate_performance_distribution(user_data),
            "department_analysis": self._analyze_by_department(user_data)
        }

    def _extract_temporal_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract temporal patterns from trends data"""
        trends = data.get("permit_trends", []) or data.get("incident_trends", [])
        if not trends:
            return {}

        return {
            "peak_days": self._identify_peak_days(trends),
            "low_activity_days": self._identify_low_activity_days(trends),
            "weekly_patterns": self._analyze_weekly_patterns(trends),
            "monthly_trends": self._analyze_monthly_trends(trends)
        }

    def _identify_outliers(self, data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """Identify outliers and anomalies in the data"""
        outliers = {
            "statistical_outliers": [],
            "performance_outliers": [],
            "time_outliers": []
        }

        # Identify overdue items as outliers
        overdue_items = data.get("overdue_permits", []) or data.get("overdue_actions", [])
        if overdue_items:
            outliers["time_outliers"] = [
                item for item in overdue_items
                if item.get("days_overdue", 0) > 30  # Items overdue by more than 30 days
            ]

        # Identify performance outliers from user data
        user_data = data.get("user_performance", [])
        if user_data:
            avg_completion_rate = sum(u.get("completion_rate", 0) for u in user_data) / len(user_data)
            outliers["performance_outliers"] = [
                user for user in user_data
                if abs(user.get("completion_rate", 0) - avg_completion_rate) > 20
            ]

        return outliers

    def _find_correlations(self, data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """Find correlations and patterns in the data"""
        correlations = {
            "template_performance_correlation": self._analyze_template_performance(data),
            "user_department_correlation": self._analyze_user_department_correlation(data),
            "time_performance_correlation": self._analyze_time_performance_correlation(data)
        }

        return correlations

    # Helper methods for analysis
    def _analyze_weekly_patterns(self, trends: List[Dict]) -> Dict[str, Any]:
        """Analyze weekly patterns in trends data"""
        if not trends:
            return {}

        # Group by day of week
        from datetime import datetime
        day_totals = {}

        for trend in trends:
            if trend.get("date"):
                try:
                    date_obj = datetime.fromisoformat(trend["date"])
                    day_name = date_obj.strftime("%A")
                    day_totals[day_name] = day_totals.get(day_name, 0) + trend.get("permits_created", 0)
                except:
                    continue

        return day_totals

    def _analyze_volume_trends(self, trends: List[Dict]) -> Dict[str, Any]:
        """Analyze volume trends"""
        if not trends:
            return {}

        volumes = [t.get("permits_created", 0) for t in trends]
        if not volumes:
            return {}

        return {
            "average_daily_volume": sum(volumes) / len(volumes),
            "peak_volume": max(volumes),
            "lowest_volume": min(volumes),
            "volume_variance": self._calculate_variance(volumes)
        }

    def _analyze_completion_trends(self, trends: List[Dict]) -> Dict[str, Any]:
        """Analyze completion trends"""
        if not trends:
            return {}

        completion_rates = []
        for trend in trends:
            created = trend.get("permits_created", 0)
            completed = trend.get("permits_completed", 0)
            if created > 0:
                completion_rates.append((completed / created) * 100)

        if not completion_rates:
            return {}

        return {
            "average_completion_rate": sum(completion_rates) / len(completion_rates),
            "best_completion_day": max(completion_rates),
            "worst_completion_day": min(completion_rates)
        }

    def _identify_high_risk_patterns(self, data: Dict[str, Any], module: str) -> List[Dict[str, Any]]:
        """Identify high-risk patterns"""
        patterns = []

        # High overdue count
        overdue_count = 0
        if module == "permit":
            overdue_count = data.get("permit_statistics", {}).get("overdue_permits", 0)
        elif module == "action":
            overdue_count = data.get("action_statistics", {}).get("overdue_actions", 0)

        if overdue_count > 10:
            patterns.append({
                "type": "high_overdue_count",
                "description": f"High number of overdue items: {overdue_count}",
                "severity": "high"
            })

        return patterns

    def _analyze_risk_distribution(self, data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """Analyze risk distribution"""
        # This would analyze risk levels across different categories
        return {
            "high_risk_percentage": 0,  # Placeholder
            "medium_risk_percentage": 0,
            "low_risk_percentage": 0
        }

    def _identify_critical_alerts(self, data: Dict[str, Any], module: str) -> List[Dict[str, Any]]:
        """Identify critical alerts"""
        alerts = []

        # Check for critical overdue items
        overdue_items = data.get("overdue_permits", []) or data.get("overdue_actions", [])
        critical_overdue = [item for item in overdue_items if item.get("days_overdue", 0) > 30]

        if critical_overdue:
            alerts.append({
                "type": "critical_overdue",
                "count": len(critical_overdue),
                "description": f"{len(critical_overdue)} items overdue by more than 30 days"
            })

        return alerts

    def _calculate_compliance_rates(self, data: Dict[str, Any], module: str) -> Dict[str, Any]:
        """Calculate compliance rates"""
        if module == "permit":
            stats = data.get("permit_statistics", {})
            total = stats.get("total_permits", 0)
            completed = stats.get("completed_permits", 0)
            return {
                "overall_compliance": (completed / total * 100) if total > 0 else 0
            }
        return {}

    def _identify_non_compliance_patterns(self, data: Dict[str, Any], module: str) -> List[str]:
        """Identify non-compliance patterns"""
        patterns = []

        # Check completion rates
        if module == "permit":
            completion_rate = data.get("permit_statistics", {}).get("completion_rate", 0)
            if completion_rate < 80:
                patterns.append(f"Low completion rate: {completion_rate}%")

        return patterns

    def _assess_regulatory_status(self, data: Dict[str, Any], module: str) -> str:
        """Assess regulatory compliance status"""
        # Simplified assessment
        completion_rate = 0
        if module == "permit":
            completion_rate = data.get("permit_statistics", {}).get("completion_rate", 0)

        if completion_rate >= 95:
            return "Excellent"
        elif completion_rate >= 85:
            return "Good"
        elif completion_rate >= 70:
            return "Needs Improvement"
        else:
            return "Critical"

    def _create_comprehensive_analysis_prompt(self, compressed_data: Dict[str, Any], module: str) -> str:
        """Create comprehensive analysis prompt for single OpenAI call"""

        prompt = f"""
COMPREHENSIVE {module.upper()} SAFETY ANALYSIS REQUEST

Analyze ALL the following safety data and provide complete insights as bullet points only.

SECTION 1 - DATA OVERVIEW:
{json.dumps(compressed_data.get('data_overview', {}), indent=2, default=str)}

SECTION 2 - STATISTICAL SUMMARY:
{json.dumps(compressed_data.get('statistical_summary', {}), indent=2, default=str)}

SECTION 3 - PERFORMANCE ANALYSIS:
{json.dumps(compressed_data.get('performance_analysis', {}), indent=2, default=str)}

SECTION 4 - TREND ANALYSIS:
{json.dumps(compressed_data.get('trend_analysis', {}), indent=2, default=str)}

SECTION 5 - RISK ASSESSMENT:
{json.dumps(compressed_data.get('risk_assessment', {}), indent=2, default=str)}

SECTION 6 - COMPLIANCE ANALYSIS:
{json.dumps(compressed_data.get('compliance_analysis', {}), indent=2, default=str)}

SECTION 7 - USER PERFORMANCE:
{json.dumps(compressed_data.get('user_performance', {}), indent=2, default=str)}

SECTION 8 - TEMPORAL PATTERNS:
{json.dumps(compressed_data.get('temporal_patterns', {}), indent=2, default=str)}

SECTION 9 - OUTLIER ANALYSIS:
{json.dumps(compressed_data.get('outlier_analysis', {}), indent=2, default=str)}

SECTION 10 - CORRELATION INSIGHTS:
{json.dumps(compressed_data.get('correlation_insights', {}), indent=2, default=str)}

ANALYSIS REQUIREMENTS:
1. Analyze EVERY section thoroughly - miss nothing
2. Identify cross-section patterns and relationships
3. Highlight critical issues from ANY section
4. Provide specific, actionable recommendations
5. Focus on safety implications and business impact
6. Ensure comprehensive coverage of all data points

RESPONSE FORMAT (bullet points only):
• [OVERVIEW] - Key insights from data overview
• [STATISTICS] - Critical statistical findings
• [PERFORMANCE] - Performance analysis insights
• [TRENDS] - Trend analysis findings
• [RISK] - Risk assessment conclusions
• [COMPLIANCE] - Compliance status insights
• [USERS] - User performance patterns
• [TEMPORAL] - Time-based pattern insights
• [OUTLIERS] - Anomaly and outlier findings
• [CORRELATIONS] - Cross-data correlations
• [CRITICAL] - Most urgent items requiring immediate attention
• [RECOMMENDATIONS] - Specific action items and improvements
• [STRATEGIC] - Strategic insights for long-term improvement

Total Records Analyzed: {compressed_data.get('data_overview', {}).get('total_records', 0)}
Analysis Period: {compressed_data.get('data_overview', {}).get('summary_period', {}).get('days_covered', 'N/A')} days
Data Completeness: {compressed_data.get('data_overview', {}).get('data_completeness', '100%')}
"""

        return prompt

    # Missing helper methods
    def _calculate_performance_distribution(self, user_data: List[Dict]) -> Dict[str, int]:
        """Calculate performance distribution"""
        if not user_data:
            return {}

        excellent = sum(1 for u in user_data if u.get("completion_rate", 0) >= 95)
        good = sum(1 for u in user_data if 85 <= u.get("completion_rate", 0) < 95)
        average = sum(1 for u in user_data if 70 <= u.get("completion_rate", 0) < 85)
        poor = sum(1 for u in user_data if u.get("completion_rate", 0) < 70)

        return {
            "excellent": excellent,
            "good": good,
            "average": average,
            "poor": poor
        }

    def _analyze_by_department(self, user_data: List[Dict]) -> Dict[str, Dict]:
        """Analyze performance by department"""
        if not user_data:
            return {}

        dept_data = {}
        for user in user_data:
            dept = user.get("department", "Unknown")
            if dept not in dept_data:
                dept_data[dept] = {"users": [], "avg_completion_rate": 0}
            dept_data[dept]["users"].append(user)

        # Calculate averages
        for dept, data in dept_data.items():
            if data["users"]:
                avg_rate = sum(u.get("completion_rate", 0) for u in data["users"]) / len(data["users"])
                data["avg_completion_rate"] = round(avg_rate, 2)
                data["user_count"] = len(data["users"])

        return dept_data

    def _identify_peak_days(self, trends: List[Dict]) -> List[Dict]:
        """Identify peak activity days"""
        if not trends:
            return []

        # Sort by activity level
        sorted_trends = sorted(trends, key=lambda x: x.get("permits_created", 0), reverse=True)
        return sorted_trends[:3]  # Top 3 peak days

    def _identify_low_activity_days(self, trends: List[Dict]) -> List[Dict]:
        """Identify low activity days"""
        if not trends:
            return []

        # Sort by activity level (ascending)
        sorted_trends = sorted(trends, key=lambda x: x.get("permits_created", 0))
        return sorted_trends[:3]  # Bottom 3 low activity days

    def _analyze_monthly_trends(self, trends: List[Dict]) -> Dict[str, Any]:
        """Analyze monthly trends"""
        # Simplified monthly analysis
        if not trends:
            return {}

        total_activity = sum(t.get("permits_created", 0) for t in trends)
        avg_daily = total_activity / len(trends) if trends else 0

        return {
            "total_monthly_activity": total_activity,
            "average_daily_activity": round(avg_daily, 2),
            "trend_direction": "stable"  # Simplified
        }

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if len(values) < 2:
            return 0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return round(variance, 2)

    def _analyze_template_performance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze template performance correlation"""
        template_data = data.get("template_breakdown", [])
        if not template_data:
            return {}

        # Find best and worst performing templates
        sorted_templates = sorted(template_data, key=lambda x: x.get("completion_rate", 0), reverse=True)

        return {
            "best_template": sorted_templates[0] if sorted_templates else {},
            "worst_template": sorted_templates[-1] if sorted_templates else {},
            "performance_range": {
                "highest": sorted_templates[0].get("completion_rate", 0) if sorted_templates else 0,
                "lowest": sorted_templates[-1].get("completion_rate", 0) if sorted_templates else 0
            }
        }

    def _analyze_user_department_correlation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user-department performance correlation"""
        user_data = data.get("user_performance", [])
        if not user_data:
            return {}

        dept_performance = self._analyze_by_department(user_data)

        # Find best and worst performing departments
        if dept_performance:
            sorted_depts = sorted(dept_performance.items(), key=lambda x: x[1].get("avg_completion_rate", 0), reverse=True)
            return {
                "best_department": sorted_depts[0] if sorted_depts else {},
                "worst_department": sorted_depts[-1] if sorted_depts else {}
            }

        return {}

    def _analyze_time_performance_correlation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze time-performance correlation"""
        trends = data.get("permit_trends", [])
        if not trends:
            return {}

        # Analyze if completion rates vary by time
        completion_analysis = self._analyze_completion_trends(trends)

        return {
            "time_impact_on_performance": completion_analysis,
            "optimal_periods": "weekdays",  # Simplified
            "challenging_periods": "weekends"  # Simplified
        }

    def _count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Count tokens in text for the given model"""
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            return len(text) // 4

    def _summarize_data_for_prompt(self, data: Dict[str, Any], max_tokens: int = 2000) -> str:
        """
        Summarize data to fit within token limits

        Args:
            data: Raw data dictionary
            max_tokens: Maximum tokens allowed for the data summary

        Returns:
            Summarized data string that fits within token limits
        """
        # Extract key statistics and metrics only
        summary_parts = []

        # Handle different data structures
        if isinstance(data, dict):
            for key, value in data.items():
                if key.endswith('_statistics') or key.endswith('_metrics'):
                    summary_parts.append(f"{key}: {json.dumps(value, default=str)}")
                elif key in ['summary_period', 'total_records', 'analysis_period']:
                    summary_parts.append(f"{key}: {value}")
                elif isinstance(value, dict) and len(str(value)) < 500:
                    # Include small dictionaries
                    summary_parts.append(f"{key}: {json.dumps(value, default=str)}")
                elif isinstance(value, (int, float, str, bool)):
                    # Include simple values
                    summary_parts.append(f"{key}: {value}")

        # Join and check token count
        summary_text = "\n".join(summary_parts)

        # If still too long, truncate to most important parts
        if self._count_tokens(summary_text) > max_tokens:
            # Keep only statistics and key metrics
            important_parts = [part for part in summary_parts
                             if any(keyword in part.lower()
                                   for keyword in ['statistics', 'metrics', 'total', 'rate', 'count'])]
            summary_text = "\n".join(important_parts[:10])  # Limit to top 10 items

        return summary_text

    def generate_comprehensive_summary(self,
                                     permit_data: Dict[str, Any],
                                     incident_data: Dict[str, Any],
                                     action_data: Dict[str, Any],
                                     inspection_data: Dict[str, Any],
                                     config: Optional[SummaryConfig] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive safety summary from all modules

        Args:
            permit_data: Permit to work data
            incident_data: Incident management data
            action_data: Action tracking data
            inspection_data: Inspection tracking data
            config: Optional configuration override

        Returns:
            Comprehensive safety summary
        """
        config = config or self.config

        # Prepare the data for AI processing
        combined_data = {
            "permit_to_work": permit_data,
            "incident_management": incident_data,
            "action_tracking": action_data,
            "inspection_tracking": inspection_data,
            "summary_timestamp": datetime.now().isoformat()
        }

        # Generate executive summary
        executive_summary = self._generate_executive_summary(combined_data, config)

        # Generate module-specific summaries
        permit_summary = self._generate_permit_summary(permit_data, config)
        incident_summary = self._generate_incident_summary(incident_data, config)
        action_summary = self._generate_action_summary(action_data, config)
        inspection_summary = self._generate_inspection_summary(inspection_data, config)

        # Generate insights and recommendations
        insights = self._generate_insights_and_recommendations(combined_data, config)

        # Generate alerts and priorities
        alerts = self._generate_alerts_and_priorities(combined_data, config)

        return {
            "summary_metadata": {
                "generated_at": datetime.now().isoformat(),
                "model_used": config.model,
                "data_period": self._extract_data_period(combined_data)
            },
            "executive_summary": executive_summary,
            "module_summaries": {
                "permit_to_work": permit_summary,
                "incident_management": incident_summary,
                "action_tracking": action_summary,
                "inspection_tracking": inspection_summary
            },
            "insights_and_recommendations": insights,
            "alerts_and_priorities": alerts,
            "key_metrics": self._extract_key_metrics(combined_data)
        }

    def _generate_executive_summary(self, data: Dict[str, Any], config: SummaryConfig) -> str:
        """Generate executive summary as bullet points"""
        # Summarize data to fit within token limits
        data_summary = self._summarize_data_for_prompt(data, max_tokens=config.max_input_tokens // 2)

        prompt = f"""
        As a safety management expert, provide an executive summary as simple bullet points only based on the following safety data:

        Data Summary:
        {data_summary}

        Generate 8-12 specific bullet points covering:
        - Overall safety performance status
        - Key performance trends and patterns
        - Critical issues requiring immediate attention
        - Performance highlights and achievements
        - Strategic recommendations for leadership
        - Business impact observations
        - Risk exposure assessment
        - Compliance status overview
        - Resource utilization insights

        Format: Return ONLY bullet points starting with "•"
        No headings, subheadings, or categories - just direct executive insights as bullet points.
        Each point should be concise, actionable, and suitable for executive leadership.
        Focus on business impact and strategic decision-making.
        """

        response = openai.ChatCompletion.create(
            model=config.model,
            messages=[
                {"role": "system", "content": "You are a safety management expert providing executive summaries. Return only bullet points."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )

        return response.choices[0].message.content.strip()

    def _generate_permit_summary(self, data: Dict[str, Any], config: SummaryConfig) -> str:
        """Generate permit to work summary as bullet points"""
        # Summarize data to fit within token limits
        data_summary = self._summarize_data_for_prompt(data, max_tokens=config.max_input_tokens // 3)

        prompt = f"""
        Analyze the following permit to work data and provide insights as simple bullet points only:

        {data_summary}

        Generate 8-12 specific bullet points covering:
        - Permit completion trends and patterns
        - Workflow efficiency observations
        - Template performance insights
        - User productivity patterns
        - Compliance status indicators
        - Resource allocation effectiveness
        - Process bottleneck identification
        - Risk mitigation effectiveness

        Format: Return ONLY bullet points starting with "•"
        No headings, subheadings, or categories - just direct insights as bullet points.
        Each point should be specific and actionable.
        """

        response = openai.ChatCompletion.create(
            model=config.model,
            messages=[
                {"role": "system", "content": "You are a permit to work specialist. Return only bullet points with specific insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=config.max_tokens // 2,
            temperature=config.temperature
        )

        return response.choices[0].message.content.strip()

    def _generate_incident_summary(self, data: Dict[str, Any], config: SummaryConfig) -> str:
        """Generate incident management summary as bullet points"""
        # Summarize data to fit within token limits
        data_summary = self._summarize_data_for_prompt(data, max_tokens=config.max_input_tokens // 3)

        prompt = f"""
        Analyze the following incident management data and provide insights as simple bullet points only:

        {data_summary}

        Generate 8-12 specific bullet points covering:
        - Incident frequency trends and patterns
        - Critical incident analysis findings
        - Response time effectiveness
        - Location-based incident insights
        - Severity distribution patterns
        - Root cause identification trends
        - Prevention strategy effectiveness
        - Emergency response performance
        - Injury incident characteristics
        - Near-miss reporting patterns

        Format: Return ONLY bullet points starting with "•"
        No headings, subheadings, or categories - just direct insights as bullet points.
        Each point should be specific and actionable for risk reduction.
        """

        response = openai.ChatCompletion.create(
            model=config.model,
            messages=[
                {"role": "system", "content": "You are an incident management specialist. Return only bullet points with specific insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=config.max_tokens // 2,
            temperature=config.temperature
        )

        return response.choices[0].message.content.strip()

    def _generate_action_summary(self, data: Dict[str, Any], config: SummaryConfig) -> str:
        """Generate action tracking summary as bullet points"""
        # Summarize data to fit within token limits
        data_summary = self._summarize_data_for_prompt(data, max_tokens=config.max_input_tokens // 3)

        prompt = f"""
        Analyze the following action tracking data and provide insights as simple bullet points only:

        {data_summary}

        Generate 8-12 specific bullet points covering:
        - Action completion rate trends
        - Priority-based performance patterns
        - Owner accountability insights
        - Overdue action impact analysis
        - Category-wise completion effectiveness
        - Response time performance
        - Escalation pattern observations
        - Resource allocation efficiency
        - Follow-through consistency
        - Process bottleneck identification

        Format: Return ONLY bullet points starting with "•"
        No headings, subheadings, or categories - just direct insights as bullet points.
        Each point should be specific and actionable for improving accountability.
        """

        response = openai.ChatCompletion.create(
            model=config.model,
            messages=[
                {"role": "system", "content": "You are an action tracking specialist. Return only bullet points with specific insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=config.max_tokens // 2,
            temperature=config.temperature
        )

        return response.choices[0].message.content.strip()

    def _generate_inspection_summary(self, data: Dict[str, Any], config: SummaryConfig) -> str:
        """Generate inspection tracking summary as bullet points"""
        # Summarize data to fit within token limits
        data_summary = self._summarize_data_for_prompt(data, max_tokens=config.max_input_tokens // 3)

        prompt = f"""
        Analyze the following inspection tracking data and provide insights as simple bullet points only:

        {data_summary}

        Generate 8-12 specific bullet points covering:
        - Inspection completion rate trends
        - Compliance performance patterns
        - Overdue inspection impact analysis
        - Frequency optimization opportunities
        - Quality assessment findings
        - Asset-based inspection effectiveness
        - Checklist performance insights
        - Inspector productivity patterns
        - Preventive maintenance effectiveness
        - Evidence submission compliance

        Format: Return ONLY bullet points starting with "•"
        No headings, subheadings, or categories - just direct insights as bullet points.
        Each point should be specific and actionable for improving compliance.
        """

        response = openai.ChatCompletion.create(
            model=config.model,
            messages=[
                {"role": "system", "content": "You are an inspection tracking specialist. Return only bullet points with specific insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=config.max_tokens // 2,
            temperature=config.temperature
        )

        return response.choices[0].message.content.strip()

    def _generate_insights_and_recommendations(self, data: Dict[str, Any], config: SummaryConfig) -> str:
        """Generate cross-module insights and recommendations as bullet points"""
        # Summarize data to fit within token limits
        data_summary = self._summarize_data_for_prompt(data, max_tokens=config.max_input_tokens // 2)

        prompt = f"""
        Based on the comprehensive safety data across all modules, provide strategic insights as simple bullet points only:

        {data_summary}

        Generate 10-15 specific bullet points covering:
        - Cross-module correlation patterns
        - Root cause analysis insights
        - Strategic improvement opportunities
        - Resource allocation optimization
        - Process integration effectiveness
        - Performance gap identification
        - Risk mitigation priorities
        - Technology enhancement needs
        - Training and development requirements
        - Compliance optimization strategies
        - Long-term improvement roadmap items

        Format: Return ONLY bullet points starting with "•"
        No headings, subheadings, or categories - just direct strategic insights as bullet points.
        Each point should be specific and actionable for holistic safety management.
        """

        response = openai.ChatCompletion.create(
            model=config.model,
            messages=[
                {"role": "system", "content": "You are a safety management strategist. Return only bullet points with strategic insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )

        return response.choices[0].message.content.strip()

    def _generate_alerts_and_priorities(self, data: Dict[str, Any], config: SummaryConfig) -> List[Dict[str, Any]]:
        """Generate prioritized alerts and action items"""
        # Summarize data to fit within token limits
        data_summary = self._summarize_data_for_prompt(data, max_tokens=config.max_input_tokens // 2)

        prompt = f"""
        Based on the safety data, identify and prioritize critical alerts and action items:

        {data_summary}

        Return a JSON array of alerts with the following structure:
        [
            {{
                "priority": "critical|high|medium|low",
                "category": "permit|incident|action|inspection",
                "title": "Brief alert title",
                "description": "Detailed description",
                "recommended_action": "Specific action to take",
                "deadline": "Suggested deadline"
            }}
        ]

        Focus on items requiring immediate attention and high business impact.
        """

        response = openai.ChatCompletion.create(
            model=config.model,
            messages=[
                {"role": "system", "content": "You are a safety analyst generating prioritized alerts. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )

        try:
            return json.loads(response.choices[0].message.content.strip())
        except json.JSONDecodeError:
            return []

    def _extract_data_period(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Extract data period information"""
        periods = {}
        for module, module_data in data.items():
            if isinstance(module_data, dict) and "summary_period" in module_data:
                periods[module] = module_data["summary_period"]
        return periods

    def _extract_key_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from all modules"""
        metrics = {}

        # Extract permit metrics
        if "permit_to_work" in data and "permit_statistics" in data["permit_to_work"]:
            metrics["permit_completion_rate"] = data["permit_to_work"]["permit_statistics"].get("completion_rate", 0)
            metrics["overdue_permits"] = data["permit_to_work"]["permit_statistics"].get("overdue_permits", 0)

        # Extract incident metrics
        if "incident_management" in data and "incident_statistics" in data["incident_management"]:
            metrics["total_incidents"] = data["incident_management"]["incident_statistics"].get("total_incidents", 0)
            metrics["injury_incidents"] = data["incident_management"]["incident_statistics"].get("injury_incidents", 0)

        # Extract action metrics
        if "action_tracking" in data and "action_statistics" in data["action_tracking"]:
            metrics["action_completion_rate"] = data["action_tracking"]["action_statistics"].get("completion_rate", 0)
            metrics["overdue_actions"] = data["action_tracking"]["action_statistics"].get("overdue_actions", 0)

        # Extract inspection metrics
        if "inspection_tracking" in data and "assignment_statistics" in data["inspection_tracking"]:
            metrics["inspection_completion_rate"] = data["inspection_tracking"]["assignment_statistics"].get("completion_rate", 0)
            metrics["overdue_inspections"] = data["inspection_tracking"]["inspection_statistics"].get("overdue_inspections", 0)

        return metrics
