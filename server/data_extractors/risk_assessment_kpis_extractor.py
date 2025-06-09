"""
Risk Assessment KPIs Extractor

This module extracts Risk Assessment KPIs from risk_assessment_data.md file.
Focuses on risk assessment data analysis and KPI generation.

KPIs Implemented:
1. Number of risk assessments conducted
2. Severity of Risks (1-5)
3. Likelihood of Risks (A-E)
4. Hazard Effects (P,E,A,R)

Insights Implemented:
5. Common Control Measures
6. Common Recovery Measures
7. Activities with Residual Risk above 1B
8. Common Hazards found
9. Effectiveness of Measures
"""

import os
import re
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj


class RiskAssessmentKPIsExtractor:
    """Extract risk assessment KPIs from risk_assessment_data.md file"""

    def __init__(self):
        """Initialize the extractor"""
        self.data_file_path = os.path.join(os.path.dirname(__file__), '..', 'risk_assessment_data.md')
        self.risk_data = None
        self._load_risk_data()

    def _load_risk_data(self):
        """Load and parse risk assessment data from markdown file"""
        try:
            if not os.path.exists(self.data_file_path):
                logger.error(f"Risk assessment data file not found: {self.data_file_path}")
                self.risk_data = pd.DataFrame()
                return

            # Read the markdown file
            with open(self.data_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Extract table data from markdown
            lines = content.split('\n')
            
            # Find the header line (contains No., Situation/Task, etc.)
            header_line = None
            data_start_line = None
            
            for i, line in enumerate(lines):
                if '**No.**' in line and '**Situation' in line:
                    header_line = i
                    # Skip the separator line (---)
                    data_start_line = i + 2
                    break

            if header_line is None:
                logger.error("Could not find table header in risk assessment data file")
                self.risk_data = pd.DataFrame()
                return

            # Extract headers
            header_line_content = lines[header_line]
            headers = [h.strip().replace('**', '') for h in header_line_content.split('|')[1:-1]]
            
            # Clean up headers
            clean_headers = []
            for header in headers:
                if 'No.' in header:
                    clean_headers.append('No')
                elif 'Situation' in header:
                    clean_headers.append('Situation_Task')
                elif 'Hazard' in header:
                    clean_headers.append('Hazard_Threat')
                elif 'Effect' in header:
                    clean_headers.append('Effect_of_Hazard')
                elif 'Groups' in header:
                    clean_headers.append('Groups_Affected_Consequence')
                elif 'Initial Risk' in header:
                    clean_headers.append('Initial_Risk')
                elif 'Control measures' in header:
                    clean_headers.append('Control_Measures')
                elif 'Residual' in header:
                    clean_headers.append('Residual_Risk')
                else:
                    clean_headers.append(header.replace(' ', '_').replace('/', '_'))

            # Extract data rows
            data_rows = []
            for i in range(data_start_line, len(lines)):
                line = lines[i].strip()
                if not line or line.startswith('#'):
                    break
                if '|' in line:
                    row_data = [cell.strip() for cell in line.split('|')[1:-1]]
                    if len(row_data) == len(clean_headers):
                        data_rows.append(row_data)

            # Create DataFrame
            if data_rows:
                self.risk_data = pd.DataFrame(data_rows, columns=clean_headers)
                logger.info(f"Loaded {len(self.risk_data)} risk assessment records")
            else:
                logger.warning("No data rows found in risk assessment file")
                self.risk_data = pd.DataFrame()

        except Exception as e:
            logger.error(f"Error loading risk assessment data: {str(e)}")
            self.risk_data = pd.DataFrame()

    def _parse_risk_rating(self, risk_string: str) -> Tuple[int, str, List[str]]:
        """Parse risk rating string like '2B (P) (A)' into severity, likelihood, and effects"""
        try:
            if pd.isna(risk_string) or not risk_string:
                return 0, '', []
            
            # Extract severity (number) and likelihood (letter)
            risk_match = re.search(r'(\d+)([A-E])', str(risk_string))
            if risk_match:
                severity = int(risk_match.group(1))
                likelihood = risk_match.group(2)
            else:
                severity = 0
                likelihood = ''
            
            # Extract effects (letters in parentheses)
            effects = re.findall(r'\(([PEAR])\)', str(risk_string))
            
            return severity, likelihood, effects
            
        except Exception as e:
            logger.warning(f"Error parsing risk rating '{risk_string}': {str(e)}")
            return 0, '', []

    def get_number_of_assessments(self) -> Dict[str, Any]:
        """Get total number of risk assessments conducted"""
        try:
            total_assessments = len(self.risk_data)
            
            return {
                "total_assessments": total_assessments,
                "assessment_details": {
                    "data_source": "risk_assessment_data.md",
                    "last_updated": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting number of assessments: {str(e)}")
            return {
                "total_assessments": 0,
                "assessment_details": {},
                "error": str(e)
            }

    def get_severity_analysis(self) -> Dict[str, Any]:
        """Analyze severity of risks (1-5 scale)"""
        try:
            if self.risk_data.empty:
                return {"severity_distribution": {}, "average_severity": 0}
            
            initial_severities = []
            residual_severities = []
            
            for _, row in self.risk_data.iterrows():
                # Parse initial risk
                initial_severity, _, _ = self._parse_risk_rating(row.get('Initial_Risk', ''))
                if initial_severity > 0:
                    initial_severities.append(initial_severity)
                
                # Parse residual risk
                residual_severity, _, _ = self._parse_risk_rating(row.get('Residual_Risk', ''))
                if residual_severity > 0:
                    residual_severities.append(residual_severity)
            
            # Calculate distributions
            initial_dist = {}
            residual_dist = {}
            
            for i in range(1, 6):
                initial_dist[str(i)] = initial_severities.count(i)
                residual_dist[str(i)] = residual_severities.count(i)
            
            return {
                "initial_severity": {
                    "distribution": initial_dist,
                    "average": np.mean(initial_severities) if initial_severities else 0,
                    "max": max(initial_severities) if initial_severities else 0,
                    "min": min(initial_severities) if initial_severities else 0
                },
                "residual_severity": {
                    "distribution": residual_dist,
                    "average": np.mean(residual_severities) if residual_severities else 0,
                    "max": max(residual_severities) if residual_severities else 0,
                    "min": min(residual_severities) if residual_severities else 0
                },
                "severity_reduction": {
                    "average_reduction": (np.mean(initial_severities) - np.mean(residual_severities)) if initial_severities and residual_severities else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing severity: {str(e)}")
            return {"severity_distribution": {}, "average_severity": 0, "error": str(e)}

    def get_likelihood_analysis(self) -> Dict[str, Any]:
        """Analyze likelihood of risks (A-E scale)"""
        try:
            if self.risk_data.empty:
                return {"likelihood_distribution": {}, "most_common_likelihood": ""}

            initial_likelihoods = []
            residual_likelihoods = []

            for _, row in self.risk_data.iterrows():
                # Parse initial risk
                _, initial_likelihood, _ = self._parse_risk_rating(row.get('Initial_Risk', ''))
                if initial_likelihood:
                    initial_likelihoods.append(initial_likelihood)

                # Parse residual risk
                _, residual_likelihood, _ = self._parse_risk_rating(row.get('Residual_Risk', ''))
                if residual_likelihood:
                    residual_likelihoods.append(residual_likelihood)

            # Calculate distributions
            initial_dist = {}
            residual_dist = {}

            for letter in ['A', 'B', 'C', 'D', 'E']:
                initial_dist[letter] = initial_likelihoods.count(letter)
                residual_dist[letter] = residual_likelihoods.count(letter)

            # Find most common
            most_common_initial = max(initial_dist, key=initial_dist.get) if initial_likelihoods else ""
            most_common_residual = max(residual_dist, key=residual_dist.get) if residual_likelihoods else ""

            return {
                "initial_likelihood": {
                    "distribution": initial_dist,
                    "most_common": most_common_initial,
                    "total_assessments": len(initial_likelihoods)
                },
                "residual_likelihood": {
                    "distribution": residual_dist,
                    "most_common": most_common_residual,
                    "total_assessments": len(residual_likelihoods)
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing likelihood: {str(e)}")
            return {"likelihood_distribution": {}, "most_common_likelihood": "", "error": str(e)}

    def get_hazard_effects_analysis(self) -> Dict[str, Any]:
        """Analyze hazard effects (P,E,A,R)"""
        try:
            if self.risk_data.empty:
                return {"effects_distribution": {}, "total_effects": 0}

            all_effects = []
            effects_by_assessment = []

            for _, row in self.risk_data.iterrows():
                # Parse initial risk effects
                _, _, initial_effects = self._parse_risk_rating(row.get('Initial_Risk', ''))
                # Parse residual risk effects
                _, _, residual_effects = self._parse_risk_rating(row.get('Residual_Risk', ''))

                # Combine effects (use initial if available, otherwise residual)
                assessment_effects = initial_effects if initial_effects else residual_effects

                if assessment_effects:
                    effects_by_assessment.append({
                        "assessment_no": row.get('No', ''),
                        "situation": row.get('Situation_Task', ''),
                        "effects": assessment_effects
                    })
                    all_effects.extend(assessment_effects)

            # Calculate distribution
            effects_dist = {}
            effect_meanings = {
                'P': 'People',
                'E': 'Environment',
                'A': 'Assets',
                'R': 'Reputation'
            }

            for effect in ['P', 'E', 'A', 'R']:
                count = all_effects.count(effect)
                effects_dist[effect] = {
                    "count": count,
                    "percentage": (count / len(all_effects) * 100) if all_effects else 0,
                    "meaning": effect_meanings[effect]
                }

            return {
                "effects_distribution": effects_dist,
                "total_effects": len(all_effects),
                "assessments_with_effects": len(effects_by_assessment),
                "effects_by_assessment": effects_by_assessment
            }

        except Exception as e:
            logger.error(f"Error analyzing hazard effects: {str(e)}")
            return {"effects_distribution": {}, "total_effects": 0, "error": str(e)}

    def get_common_control_measures(self) -> Dict[str, Any]:
        """Analyze common control measures"""
        try:
            if self.risk_data.empty:
                return {"common_measures": [], "total_measures": 0}

            all_control_measures = []

            for _, row in self.risk_data.iterrows():
                control_text = row.get('Control_Measures', '')
                if pd.notna(control_text) and control_text:
                    # Extract control measures (lines starting with bullet points or numbers)
                    measures = re.findall(r'(?:•|\*|-|\d+\.)\s*([^•\*\-\d\n]+)', str(control_text))
                    for measure in measures:
                        clean_measure = measure.strip()
                        if len(clean_measure) > 10:  # Filter out very short measures
                            all_control_measures.append(clean_measure)

            # Find common patterns in control measures
            measure_keywords = {}
            common_patterns = [
                'PPE', 'training', 'permit', 'first aid', 'competent', 'certified',
                'inspection', 'barricade', 'ventilation', 'monitoring', 'safety'
            ]

            for keyword in common_patterns:
                count = sum(1 for measure in all_control_measures if keyword.lower() in measure.lower())
                if count > 0:
                    measure_keywords[keyword] = count

            # Get top 10 most common measures
            top_measures = []
            measure_counts = {}

            for measure in all_control_measures:
                # Simplify measure for counting
                simple_measure = re.sub(r'\([^)]*\)', '', measure).strip()[:50]
                measure_counts[simple_measure] = measure_counts.get(simple_measure, 0) + 1

            sorted_measures = sorted(measure_counts.items(), key=lambda x: x[1], reverse=True)
            top_measures = [{"measure": measure, "count": count} for measure, count in sorted_measures[:10]]

            return {
                "common_measures": top_measures,
                "measure_keywords": measure_keywords,
                "total_measures": len(all_control_measures),
                "unique_measures": len(measure_counts)
            }

        except Exception as e:
            logger.error(f"Error analyzing control measures: {str(e)}")
            return {"common_measures": [], "total_measures": 0, "error": str(e)}

    def get_common_recovery_measures(self) -> Dict[str, Any]:
        """Analyze common recovery measures"""
        try:
            if self.risk_data.empty:
                return {"recovery_measures": [], "total_measures": 0}

            all_recovery_measures = []

            for _, row in self.risk_data.iterrows():
                control_text = row.get('Control_Measures', '')
                if pd.notna(control_text) and control_text:
                    # Look for recovery measures section
                    recovery_section = re.search(r'Recovery Measures[:\s]*(.+?)(?=\n\n|\Z)', str(control_text), re.DOTALL | re.IGNORECASE)
                    if recovery_section:
                        recovery_text = recovery_section.group(1)
                        # Extract individual measures
                        measures = re.findall(r'(?:•|\*|-|\d+\.)\s*([^•\*\-\d\n]+)', recovery_text)
                        for measure in measures:
                            clean_measure = measure.strip()
                            if len(clean_measure) > 10:
                                all_recovery_measures.append(clean_measure)

            # Count occurrences of recovery measures
            measure_counts = {}
            for measure in all_recovery_measures:
                simple_measure = re.sub(r'\([^)]*\)', '', measure).strip()[:50]
                measure_counts[simple_measure] = measure_counts.get(simple_measure, 0) + 1

            # Get top recovery measures
            sorted_measures = sorted(measure_counts.items(), key=lambda x: x[1], reverse=True)
            top_measures = [{"measure": measure, "count": count} for measure, count in sorted_measures[:10]]

            # Common recovery keywords
            recovery_keywords = {}
            common_patterns = ['first aid', 'emergency', 'evacuation', 'medical', 'rescue', 'response']

            for keyword in common_patterns:
                count = sum(1 for measure in all_recovery_measures if keyword.lower() in measure.lower())
                if count > 0:
                    recovery_keywords[keyword] = count

            return {
                "recovery_measures": top_measures,
                "recovery_keywords": recovery_keywords,
                "total_measures": len(all_recovery_measures),
                "unique_measures": len(measure_counts)
            }

        except Exception as e:
            logger.error(f"Error analyzing recovery measures: {str(e)}")
            return {"recovery_measures": [], "total_measures": 0, "error": str(e)}

    def get_activities_with_high_residual_risk(self) -> Dict[str, Any]:
        """Get activities with residual risk above 1B"""
        try:
            if self.risk_data.empty:
                return {"high_risk_activities": [], "total_high_risk": 0}

            high_risk_activities = []

            for _, row in self.risk_data.iterrows():
                residual_severity, residual_likelihood, _ = self._parse_risk_rating(row.get('Residual_Risk', ''))

                # Check if residual risk is above 1B
                # Risk levels: 1A < 1B < 1C < 1D < 1E < 2A < 2B, etc.
                is_high_risk = False

                if residual_severity > 1:
                    is_high_risk = True
                elif residual_severity == 1 and residual_likelihood in ['C', 'D', 'E']:
                    is_high_risk = True

                if is_high_risk:
                    # Get hazard text and handle Series
                    hazard_text = row.get('Hazard_Threat', '')
                    if hasattr(hazard_text, 'iloc'):
                        hazard_text = hazard_text.iloc[0] if len(hazard_text) > 0 else ''

                    high_risk_activities.append({
                        "assessment_no": row.get('No', ''),
                        "situation": row.get('Situation_Task', ''),
                        "residual_risk": row.get('Residual_Risk', ''),
                        "severity": residual_severity,
                        "likelihood": residual_likelihood,
                        "hazard": str(hazard_text)
                    })

            return {
                "high_risk_activities": high_risk_activities,
                "total_high_risk": len(high_risk_activities),
                "percentage_high_risk": (len(high_risk_activities) / len(self.risk_data) * 100) if len(self.risk_data) > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error analyzing high residual risk activities: {str(e)}")
            return {"high_risk_activities": [], "total_high_risk": 0, "error": str(e)}

    def get_common_hazards(self) -> Dict[str, Any]:
        """Analyze common hazards found"""
        try:
            if self.risk_data.empty:
                return {"common_hazards": [], "total_hazards": 0}

            all_hazards = []

            for _, row in self.risk_data.iterrows():
                # Get hazard text - handle both single values and Series
                hazard_text = row.get('Hazard_Threat', '')

                # Convert pandas Series to string if needed
                if hasattr(hazard_text, 'iloc'):
                    # It's a Series, get the first value
                    hazard_text = hazard_text.iloc[0] if len(hazard_text) > 0 else ''

                if pd.notna(hazard_text) and str(hazard_text).strip():
                    # Convert to string and split hazards by common separators
                    hazard_str = str(hazard_text)
                    hazards = re.split(r'[,;.\n]|<br>', hazard_str)
                    for hazard in hazards:
                        clean_hazard = hazard.strip()
                        if len(clean_hazard) > 5:
                            all_hazards.append(clean_hazard)

            # Count hazard occurrences
            hazard_counts = {}
            for hazard in all_hazards:
                simple_hazard = hazard.lower().strip()
                hazard_counts[simple_hazard] = hazard_counts.get(simple_hazard, 0) + 1

            # Get top hazards
            sorted_hazards = sorted(hazard_counts.items(), key=lambda x: x[1], reverse=True)
            top_hazards = [{"hazard": hazard, "count": count} for hazard, count in sorted_hazards[:10]]

            # Categorize hazards
            hazard_categories = {
                "physical": ["falling", "slip", "trip", "pressure", "impact"],
                "chemical": ["toxic", "chemical", "vapour", "fumes", "acid"],
                "mechanical": ["equipment", "machinery", "vehicle", "tool"],
                "environmental": ["weather", "temperature", "noise", "dust"]
            }

            category_counts = {}
            for category, keywords in hazard_categories.items():
                count = 0
                for hazard in all_hazards:
                    if any(keyword in hazard.lower() for keyword in keywords):
                        count += 1
                category_counts[category] = count

            return {
                "common_hazards": top_hazards,
                "hazard_categories": category_counts,
                "total_hazards": len(all_hazards),
                "unique_hazards": len(hazard_counts)
            }

        except Exception as e:
            logger.error(f"Error analyzing common hazards: {str(e)}")
            return {"common_hazards": [], "total_hazards": 0, "error": str(e)}

    def get_measure_effectiveness(self) -> Dict[str, Any]:
        """Analyze effectiveness of control measures"""
        try:
            if self.risk_data.empty:
                return {"effectiveness_metrics": {}, "overall_effectiveness": 0}

            effectiveness_data = []
            total_risk_reduction = 0
            assessments_with_reduction = 0

            for _, row in self.risk_data.iterrows():
                initial_severity, initial_likelihood, _ = self._parse_risk_rating(row.get('Initial_Risk', ''))
                residual_severity, residual_likelihood, _ = self._parse_risk_rating(row.get('Residual_Risk', ''))

                if initial_severity > 0 and residual_severity > 0:
                    # Calculate risk scores (simplified: severity * likelihood_numeric)
                    likelihood_values = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}

                    initial_likelihood_val = likelihood_values.get(initial_likelihood, 3)
                    residual_likelihood_val = likelihood_values.get(residual_likelihood, 3)

                    initial_risk_score = initial_severity * initial_likelihood_val
                    residual_risk_score = residual_severity * residual_likelihood_val

                    risk_reduction = initial_risk_score - residual_risk_score
                    reduction_percentage = (risk_reduction / initial_risk_score * 100) if initial_risk_score > 0 else 0

                    effectiveness_data.append({
                        "assessment_no": row.get('No', ''),
                        "situation": row.get('Situation_Task', ''),
                        "initial_risk_score": initial_risk_score,
                        "residual_risk_score": residual_risk_score,
                        "risk_reduction": risk_reduction,
                        "reduction_percentage": reduction_percentage
                    })

                    total_risk_reduction += reduction_percentage
                    assessments_with_reduction += 1

            # Calculate overall effectiveness
            overall_effectiveness = (total_risk_reduction / assessments_with_reduction) if assessments_with_reduction > 0 else 0

            # Categorize effectiveness
            high_effectiveness = [item for item in effectiveness_data if item["reduction_percentage"] >= 50]
            medium_effectiveness = [item for item in effectiveness_data if 25 <= item["reduction_percentage"] < 50]
            low_effectiveness = [item for item in effectiveness_data if item["reduction_percentage"] < 25]

            return {
                "effectiveness_metrics": {
                    "overall_effectiveness_percentage": overall_effectiveness,
                    "high_effectiveness_count": len(high_effectiveness),
                    "medium_effectiveness_count": len(medium_effectiveness),
                    "low_effectiveness_count": len(low_effectiveness),
                    "total_assessments_analyzed": len(effectiveness_data)
                },
                "effectiveness_breakdown": {
                    "high_effectiveness": high_effectiveness[:5],  # Top 5
                    "low_effectiveness": low_effectiveness[:5]     # Bottom 5
                },
                "overall_effectiveness": overall_effectiveness
            }

        except Exception as e:
            logger.error(f"Error analyzing measure effectiveness: {str(e)}")
            return {"effectiveness_metrics": {}, "overall_effectiveness": 0, "error": str(e)}

    def generate_insights(self) -> List[str]:
        """Generate insights based on risk assessment data"""
        insights = []

        try:
            if self.risk_data.empty:
                insights.append("No risk assessment data available for analysis")
                return insights

            # Get analysis data
            severity_analysis = self.get_severity_analysis()
            likelihood_analysis = self.get_likelihood_analysis()
            effects_analysis = self.get_hazard_effects_analysis()
            high_risk_activities = self.get_activities_with_high_residual_risk()
            effectiveness = self.get_measure_effectiveness()

            # Generate insights
            total_assessments = len(self.risk_data)
            insights.append(f"OVERVIEW: {total_assessments} risk assessments have been conducted")

            # Severity insights
            if severity_analysis.get("initial_severity", {}).get("average", 0) > 0:
                avg_initial = severity_analysis["initial_severity"]["average"]
                avg_residual = severity_analysis["residual_severity"]["average"]
                insights.append(f"RISK REDUCTION: Average severity reduced from {avg_initial:.1f} to {avg_residual:.1f}")

            # High risk activities
            high_risk_count = high_risk_activities.get("total_high_risk", 0)
            if high_risk_count > 0:
                insights.append(f"HIGH RISK: {high_risk_count} activities still have residual risk above 1B requiring attention")
            else:
                insights.append("POSITIVE: All activities have been reduced to acceptable risk levels (1B or below)")

            # Effectiveness insight
            effectiveness_pct = effectiveness.get("overall_effectiveness", 0)
            if effectiveness_pct > 70:
                insights.append(f"EXCELLENT: Control measures are highly effective with {effectiveness_pct:.1f}% average risk reduction")
            elif effectiveness_pct > 50:
                insights.append(f"GOOD: Control measures show good effectiveness with {effectiveness_pct:.1f}% average risk reduction")
            else:
                insights.append(f"IMPROVEMENT NEEDED: Control measures effectiveness is {effectiveness_pct:.1f}%, consider strengthening controls")

            # Hazard effects insight
            effects_dist = effects_analysis.get("effects_distribution", {})
            if effects_dist:
                people_risk = effects_dist.get("P", {}).get("count", 0)
                if people_risk == total_assessments:
                    insights.append("PEOPLE FOCUS: All risk assessments involve potential impact to people")

                asset_risk = effects_dist.get("A", {}).get("count", 0)
                if asset_risk > total_assessments * 0.5:
                    insights.append(f"ASSET PROTECTION: {asset_risk} assessments involve potential asset damage")

        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            insights.append("Error generating insights - please check data quality")

        return insights

    def get_risk_assessment_kpis(self, customer_id: Optional[str] = None, days_back: int = 365) -> Dict[str, Any]:
        """Get comprehensive risk assessment KPIs"""
        try:
            logger.info(f"Generating risk assessment KPIs for customer: {customer_id}")

            # Get all KPI components
            assessments_count = self.get_number_of_assessments()
            severity_analysis = self.get_severity_analysis()
            likelihood_analysis = self.get_likelihood_analysis()
            effects_analysis = self.get_hazard_effects_analysis()
            control_measures = self.get_common_control_measures()
            recovery_measures = self.get_common_recovery_measures()
            high_risk_activities = self.get_activities_with_high_residual_risk()
            common_hazards = self.get_common_hazards()
            effectiveness = self.get_measure_effectiveness()
            insights = self.generate_insights()

            # Convert numpy types for JSON serialization
            result = convert_numpy_types({
                # Main KPIs
                "number_of_assessments": assessments_count["total_assessments"],
                "severity_analysis": severity_analysis,
                "likelihood_analysis": likelihood_analysis,
                "hazard_effects": effects_analysis,

                # Insights
                "common_control_measures": control_measures,
                "common_recovery_measures": recovery_measures,
                "high_residual_risk_activities": high_risk_activities,
                "common_hazards": common_hazards,
                "measure_effectiveness": effectiveness,
                "insights": insights,

                # Metadata
                "data_source": "risk_assessment_data.md",
                "last_updated": datetime.now().isoformat(),
                "total_assessments_analyzed": len(self.risk_data)
            })

            logger.info("Risk assessment KPIs generated successfully")
            return result

        except Exception as e:
            logger.error(f"Error getting risk assessment KPIs: {str(e)}")
            return {
                # Main KPIs (4 total)
                "number_of_assessments": 0,
                "severity_analysis": {"severity_distribution": {}, "average_severity": 0},
                "likelihood_analysis": {"likelihood_distribution": {}, "most_common_likelihood": ""},
                "hazard_effects": {"effects_distribution": {}, "total_effects": 0},

                # Insights (5 total)
                "common_control_measures": {"common_measures": [], "total_measures": 0},
                "common_recovery_measures": {"recovery_measures": [], "total_measures": 0},
                "high_residual_risk_activities": {"high_risk_activities": [], "total_high_risk": 0},
                "common_hazards": {"common_hazards": [], "total_hazards": 0},
                "measure_effectiveness": {"effectiveness_metrics": {}, "overall_effectiveness": 0},
                "insights": ["Error generating KPIs - please check data availability"],

                # Metadata
                "error": str(e),
                "data_source": "risk_assessment_data.md",
                "last_updated": datetime.now().isoformat()
            }

    def close(self):
        """Close any resources (placeholder for consistency with other extractors)"""
        pass


# Utility function for easy usage
def get_risk_assessment_kpis(customer_id: Optional[str] = None, days_back: int = 365) -> Dict[str, Any]:
    """
    Utility function to extract all risk assessment KPIs

    Args:
        customer_id: Optional customer ID to filter data (not used for markdown data)
        days_back: Number of days to look back (not used for markdown data)

    Returns:
        Dictionary containing all risk assessment KPIs
    """
    try:
        # Create extractor and get KPIs
        extractor = RiskAssessmentKPIsExtractor()
        kpis = extractor.get_risk_assessment_kpis(customer_id, days_back)

        # Close the extractor
        extractor.close()

        return kpis

    except Exception as e:
        logger.error(f"Error in standalone get_risk_assessment_kpis: {str(e)}")
        return {"error": str(e)}
