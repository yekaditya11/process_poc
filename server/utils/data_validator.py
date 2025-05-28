"""
Data Validation Utilities
Validates data quality and completeness for AI summarization
"""

from typing import Dict, Any, List, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataValidator:
    """Validates data quality for AI summarization"""
    
    def __init__(self):
        self.validation_rules = {
            "permit_to_work": {
                "required_fields": ["permit_statistics", "status_breakdown"],
                "min_records": 1,
                "critical_metrics": ["completion_rate", "overdue_permits"]
            },
            "incident_management": {
                "required_fields": ["incident_statistics", "type_breakdown"],
                "min_records": 0,  # Incidents can be zero
                "critical_metrics": ["total_incidents", "injury_incidents"]
            },
            "action_tracking": {
                "required_fields": ["action_statistics", "status_breakdown"],
                "min_records": 1,
                "critical_metrics": ["completion_rate", "overdue_actions"]
            },
            "inspection_tracking": {
                "required_fields": ["inspection_statistics", "assignment_statistics"],
                "min_records": 1,
                "critical_metrics": ["total_inspections", "overdue_inspections"]
            }
        }
    
    def validate_module_data(self, module: str, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate data for a specific module
        
        Args:
            module: Module name
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if module not in self.validation_rules:
            issues.append(f"Unknown module: {module}")
            return False, issues
        
        rules = self.validation_rules[module]
        
        # Check required fields
        for field in rules["required_fields"]:
            if field not in data:
                issues.append(f"Missing required field: {field}")
        
        # Check critical metrics
        for metric in rules["critical_metrics"]:
            if not self._check_metric_exists(data, metric):
                issues.append(f"Missing critical metric: {metric}")
        
        # Check data freshness
        if not self._check_data_freshness(data):
            issues.append("Data appears to be stale (older than 24 hours)")
        
        # Check for reasonable data ranges
        range_issues = self._check_data_ranges(module, data)
        issues.extend(range_issues)
        
        return len(issues) == 0, issues
    
    def validate_comprehensive_data(self, all_data: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate data across all modules
        
        Args:
            all_data: Dictionary containing data from all modules
            
        Returns:
            Tuple of (is_valid, dict_of_issues_by_module)
        """
        all_issues = {}
        overall_valid = True
        
        for module in ["permit_to_work", "incident_management", "action_tracking", "inspection_tracking"]:
            if module in all_data:
                is_valid, issues = self.validate_module_data(module, all_data[module])
                if not is_valid:
                    overall_valid = False
                    all_issues[module] = issues
            else:
                overall_valid = False
                all_issues[module] = [f"Module data missing: {module}"]
        
        # Cross-module validation
        cross_issues = self._validate_cross_module_consistency(all_data)
        if cross_issues:
            overall_valid = False
            all_issues["cross_module"] = cross_issues
        
        return overall_valid, all_issues
    
    def _check_metric_exists(self, data: Dict[str, Any], metric: str) -> bool:
        """Check if a metric exists in the data structure"""
        # Navigate through nested dictionaries to find the metric
        for key, value in data.items():
            if isinstance(value, dict):
                if metric in value:
                    return True
                elif self._check_metric_exists(value, metric):
                    return True
        return False
    
    def _check_data_freshness(self, data: Dict[str, Any]) -> bool:
        """Check if data is fresh (generated recently)"""
        if "summary_period" in data:
            try:
                end_date_str = data["summary_period"].get("end_date")
                if end_date_str:
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                    # Data should be within last 24 hours
                    return (datetime.now() - end_date.replace(tzinfo=None)) < timedelta(hours=24)
            except (ValueError, TypeError):
                pass
        return True  # Assume fresh if we can't determine
    
    def _check_data_ranges(self, module: str, data: Dict[str, Any]) -> List[str]:
        """Check if data values are within reasonable ranges"""
        issues = []
        
        # Check completion rates (should be 0-100)
        completion_rates = self._extract_completion_rates(data)
        for rate_name, rate_value in completion_rates.items():
            if rate_value < 0 or rate_value > 100:
                issues.append(f"Invalid completion rate for {rate_name}: {rate_value}%")
        
        # Check for negative counts
        counts = self._extract_counts(data)
        for count_name, count_value in counts.items():
            if count_value < 0:
                issues.append(f"Negative count for {count_name}: {count_value}")
        
        return issues
    
    def _extract_completion_rates(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract completion rates from data"""
        rates = {}
        
        def find_rates(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if "completion_rate" in key.lower() and isinstance(value, (int, float)):
                        rates[f"{prefix}{key}"] = value
                    elif isinstance(value, dict):
                        find_rates(value, f"{prefix}{key}.")
        
        find_rates(data)
        return rates
    
    def _extract_counts(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Extract count values from data"""
        counts = {}
        
        def find_counts(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if ("count" in key.lower() or "total" in key.lower()) and isinstance(value, int):
                        counts[f"{prefix}{key}"] = value
                    elif isinstance(value, dict):
                        find_counts(value, f"{prefix}{key}.")
        
        find_counts(data)
        return counts
    
    def _validate_cross_module_consistency(self, all_data: Dict[str, Any]) -> List[str]:
        """Validate consistency across modules"""
        issues = []
        
        # Check if all modules have the same analysis period
        periods = {}
        for module, data in all_data.items():
            if isinstance(data, dict) and "summary_period" in data:
                period = data["summary_period"]
                periods[module] = (period.get("start_date"), period.get("end_date"))
        
        if len(set(periods.values())) > 1:
            issues.append("Inconsistent analysis periods across modules")
        
        # Check if customer_id is consistent (if present)
        customer_ids = set()
        for module, data in all_data.items():
            if isinstance(data, dict) and "summary_period" in data:
                # Customer ID might be in the data structure
                # This is a placeholder for actual customer ID extraction logic
                pass
        
        return issues
    
    def generate_data_quality_report(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive data quality report"""
        is_valid, issues = self.validate_comprehensive_data(all_data)
        
        # Calculate data completeness scores
        completeness_scores = {}
        for module in ["permit_to_work", "incident_management", "action_tracking", "inspection_tracking"]:
            if module in all_data:
                score = self._calculate_completeness_score(module, all_data[module])
                completeness_scores[module] = score
            else:
                completeness_scores[module] = 0.0
        
        # Calculate overall quality score
        overall_score = sum(completeness_scores.values()) / len(completeness_scores)
        
        return {
            "overall_valid": is_valid,
            "overall_quality_score": round(overall_score, 2),
            "module_completeness_scores": completeness_scores,
            "validation_issues": issues,
            "recommendations": self._generate_quality_recommendations(issues),
            "generated_at": datetime.now().isoformat()
        }
    
    def _calculate_completeness_score(self, module: str, data: Dict[str, Any]) -> float:
        """Calculate completeness score for a module (0-100)"""
        if module not in self.validation_rules:
            return 0.0
        
        rules = self.validation_rules[module]
        total_checks = len(rules["required_fields"]) + len(rules["critical_metrics"])
        passed_checks = 0
        
        # Check required fields
        for field in rules["required_fields"]:
            if field in data:
                passed_checks += 1
        
        # Check critical metrics
        for metric in rules["critical_metrics"]:
            if self._check_metric_exists(data, metric):
                passed_checks += 1
        
        return (passed_checks / total_checks) * 100 if total_checks > 0 else 0.0
    
    def _generate_quality_recommendations(self, issues: Dict[str, List[str]]) -> List[str]:
        """Generate recommendations based on validation issues"""
        recommendations = []
        
        for module, module_issues in issues.items():
            if "missing" in str(module_issues).lower():
                recommendations.append(f"Review data extraction logic for {module}")
            if "stale" in str(module_issues).lower():
                recommendations.append(f"Increase data refresh frequency for {module}")
            if "invalid" in str(module_issues).lower():
                recommendations.append(f"Implement data validation at source for {module}")
        
        if not recommendations:
            recommendations.append("Data quality is good - no specific recommendations")
        
        return recommendations
