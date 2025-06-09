"""
Equipment Asset KPIs Extractor
Extracts KPIs and insights from Equipment Asset Details data
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
import re

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


class EquipmentAssetKPIsExtractor:
    """Extract equipment asset KPIs from Equipment_Asset_Details.md file"""

    def __init__(self):
        """Initialize the extractor"""
        self.data_file_path = os.path.join(os.path.dirname(__file__), '..', 'Equipment_Asset_Details.md')
        self.equipment_data = None
        self._load_equipment_data()

    def _load_equipment_data(self):
        """Load and parse equipment data from markdown file"""
        try:
            if not os.path.exists(self.data_file_path):
                logger.error(f"Equipment data file not found: {self.data_file_path}")
                self.equipment_data = pd.DataFrame()
                return

            # Read the markdown file
            with open(self.data_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Extract table data from markdown
            lines = content.split('\n')
            
            # Find the header line (contains Asset ID, Asset, Type, etc.)
            header_line = None
            data_start_line = None
            
            for i, line in enumerate(lines):
                if '**Asset ID**' in line:
                    header_line = i
                    # Skip the separator line (---)
                    data_start_line = i + 2
                    break
            
            if header_line is None:
                logger.error("Could not find table header in equipment data file")
                self.equipment_data = pd.DataFrame()
                return

            # Extract headers
            header_line_content = lines[header_line]
            headers = [h.strip().replace('**', '') for h in header_line_content.split('|')[1:-1]]
            
            # Extract data rows
            data_rows = []
            for i in range(data_start_line, len(lines)):
                line = lines[i].strip()
                if line and '|' in line and not line.startswith('Total lines'):
                    # Split by | and clean up
                    row_data = [cell.strip() for cell in line.split('|')[1:-1]]
                    if len(row_data) == len(headers):
                        data_rows.append(row_data)

            # Create DataFrame
            self.equipment_data = pd.DataFrame(data_rows, columns=headers)
            
            # Clean up data types and handle empty values
            self._clean_data()
            
            logger.info(f"Successfully loaded {len(self.equipment_data)} equipment records")

        except Exception as e:
            logger.error(f"Error loading equipment data: {str(e)}")
            self.equipment_data = pd.DataFrame()

    def _clean_data(self):
        """Clean and standardize the equipment data"""
        if self.equipment_data.empty:
            return

        # Replace empty strings with None
        self.equipment_data = self.equipment_data.replace('', None)
        
        # Convert date columns
        date_columns = ['Calibration Expiry Date', 'Last Inspection Date', 'Next Service']
        for col in date_columns:
            if col in self.equipment_data.columns:
                self.equipment_data[col] = pd.to_datetime(
                    self.equipment_data[col], 
                    format='%Y-%m-%d', 
                    errors='coerce'
                )

        # Standardize Yes/No columns
        yes_no_columns = ['Calibration Certificate Valid', 'Anomalies/Deviations']
        for col in yes_no_columns:
            if col in self.equipment_data.columns:
                self.equipment_data[col] = self.equipment_data[col].map({
                    'Yes': True, 
                    'No': False, 
                    None: None
                })

        logger.info("Equipment data cleaned and standardized")

    def get_calibration_certificate_kpis(self) -> Dict[str, Any]:
        """Calculate calibration certificate related KPIs"""
        try:
            if self.equipment_data.empty:
                return {
                    "total_equipment": 0,
                    "equipment_with_valid_certificates": 0,
                    "equipment_without_valid_certificates": 0,
                    "percentage_with_valid_certificates": 0.0,
                    "percentage_without_valid_certificates": 0.0,
                    "equipment_with_missing_certificate_info": 0
                }

            total_equipment = len(self.equipment_data)
            
            # Count equipment with valid certificates
            valid_cert_mask = self.equipment_data['Calibration Certificate Valid'] == True
            equipment_with_valid = int(valid_cert_mask.sum())

            # Count equipment without valid certificates
            invalid_cert_mask = self.equipment_data['Calibration Certificate Valid'] == False
            equipment_without_valid = int(invalid_cert_mask.sum())

            # Count equipment with missing certificate information
            missing_cert_mask = self.equipment_data['Calibration Certificate Valid'].isna()
            equipment_missing_info = int(missing_cert_mask.sum())

            # Calculate percentages
            percentage_with_valid = (equipment_with_valid / total_equipment * 100) if total_equipment > 0 else 0
            percentage_without_valid = (equipment_without_valid / total_equipment * 100) if total_equipment > 0 else 0

            return {
                "total_equipment": total_equipment,
                "equipment_with_valid_certificates": equipment_with_valid,
                "equipment_without_valid_certificates": equipment_without_valid,
                "percentage_with_valid_certificates": round(percentage_with_valid, 2),
                "percentage_without_valid_certificates": round(percentage_without_valid, 2),
                "equipment_with_missing_certificate_info": equipment_missing_info
            }

        except Exception as e:
            logger.error(f"Error calculating calibration certificate KPIs: {str(e)}")
            return {
                "total_equipment": 0,
                "equipment_with_valid_certificates": 0,
                "equipment_without_valid_certificates": 0,
                "percentage_with_valid_certificates": 0.0,
                "percentage_without_valid_certificates": 0.0,
                "equipment_with_missing_certificate_info": 0,
                "error": str(e)
            }

    def get_calibration_expiry_kpis(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Calculate upcoming/expired calibration certificate KPIs"""
        try:
            if self.equipment_data.empty:
                return {
                    "total_equipment_with_expiry_dates": 0,
                    "expired_calibrations": 0,
                    "upcoming_calibrations": 0,
                    "percentage_expired": 0.0,
                    "percentage_upcoming": 0.0,
                    "expired_equipment_details": [],
                    "upcoming_equipment_details": []
                }

            # Filter equipment that has calibration expiry dates
            equipment_with_dates = self.equipment_data[
                self.equipment_data['Calibration Expiry Date'].notna()
            ].copy()

            if equipment_with_dates.empty:
                return {
                    "total_equipment_with_expiry_dates": 0,
                    "expired_calibrations": 0,
                    "upcoming_calibrations": 0,
                    "percentage_expired": 0.0,
                    "percentage_upcoming": 0.0,
                    "expired_equipment_details": [],
                    "upcoming_equipment_details": []
                }

            current_date = datetime.now()
            future_date = current_date + timedelta(days=days_ahead)

            # Find expired calibrations
            expired_mask = equipment_with_dates['Calibration Expiry Date'] < current_date
            expired_equipment = equipment_with_dates[expired_mask]

            # Find upcoming calibrations (expiring within specified days)
            upcoming_mask = (
                (equipment_with_dates['Calibration Expiry Date'] >= current_date) &
                (equipment_with_dates['Calibration Expiry Date'] <= future_date)
            )
            upcoming_equipment = equipment_with_dates[upcoming_mask]

            total_with_dates = int(len(equipment_with_dates))
            expired_count = int(len(expired_equipment))
            upcoming_count = int(len(upcoming_equipment))

            # Calculate percentages
            percentage_expired = (expired_count / total_with_dates * 100) if total_with_dates > 0 else 0
            percentage_upcoming = (upcoming_count / total_with_dates * 100) if total_with_dates > 0 else 0

            # Prepare detailed lists
            expired_details = []
            for _, row in expired_equipment.iterrows():
                expired_details.append({
                    "asset_id": row['Asset ID'],
                    "asset_name": row['Asset'],
                    "type": row['Type'],
                    "location": row['Location'],
                    "expiry_date": row['Calibration Expiry Date'].strftime('%Y-%m-%d'),
                    "days_overdue": (current_date - row['Calibration Expiry Date']).days
                })

            upcoming_details = []
            for _, row in upcoming_equipment.iterrows():
                upcoming_details.append({
                    "asset_id": row['Asset ID'],
                    "asset_name": row['Asset'],
                    "type": row['Type'],
                    "location": row['Location'],
                    "expiry_date": row['Calibration Expiry Date'].strftime('%Y-%m-%d'),
                    "days_until_expiry": (row['Calibration Expiry Date'] - current_date).days
                })

            return {
                "total_equipment_with_expiry_dates": total_with_dates,
                "expired_calibrations": expired_count,
                "upcoming_calibrations": upcoming_count,
                "percentage_expired": round(percentage_expired, 2),
                "percentage_upcoming": round(percentage_upcoming, 2),
                "expired_equipment_details": expired_details,
                "upcoming_equipment_details": upcoming_details,
                "analysis_period_days": days_ahead
            }

        except Exception as e:
            logger.error(f"Error calculating calibration expiry KPIs: {str(e)}")
            return {
                "total_equipment_with_expiry_dates": 0,
                "expired_calibrations": 0,
                "upcoming_calibrations": 0,
                "percentage_expired": 0.0,
                "percentage_upcoming": 0.0,
                "expired_equipment_details": [],
                "upcoming_equipment_details": [],
                "error": str(e)
            }

    def get_inspection_completion_kpis(self) -> Dict[str, Any]:
        """Calculate equipment inspection completion KPIs"""
        try:
            if self.equipment_data.empty:
                return {
                    "total_equipment": 0,
                    "equipment_with_completed_inspections": 0,
                    "equipment_with_pending_inspections": 0,
                    "percentage_completed": 0.0,
                    "percentage_pending": 0.0,
                    "inspection_completion_by_type": {},
                    "equipment_without_inspection_status": 0
                }

            total_equipment = len(self.equipment_data)

            # Count completed inspections
            completed_mask = self.equipment_data['Inspection Status'] == 'Completed'
            completed_count = int(completed_mask.sum())

            # Count pending inspections
            pending_mask = self.equipment_data['Inspection Status'] == 'Pending'
            pending_count = int(pending_mask.sum())

            # Count equipment without inspection status
            no_status_mask = self.equipment_data['Inspection Status'].isna()
            no_status_count = int(no_status_mask.sum())

            # Calculate percentages
            percentage_completed = (completed_count / total_equipment * 100) if total_equipment > 0 else 0
            percentage_pending = (pending_count / total_equipment * 100) if total_equipment > 0 else 0

            # Calculate inspection completion by equipment type
            inspection_by_type = {}
            equipment_types = self.equipment_data['Asset'].unique()

            for eq_type in equipment_types:
                if pd.isna(eq_type):
                    continue

                type_equipment = self.equipment_data[self.equipment_data['Asset'] == eq_type]
                type_total = int(len(type_equipment))
                type_completed = int(len(type_equipment[type_equipment['Inspection Status'] == 'Completed']))
                type_pending = int(len(type_equipment[type_equipment['Inspection Status'] == 'Pending']))

                type_completion_percentage = (type_completed / type_total * 100) if type_total > 0 else 0

                inspection_by_type[eq_type] = {
                    "total_equipment": type_total,
                    "completed_inspections": type_completed,
                    "pending_inspections": type_pending,
                    "completion_percentage": round(type_completion_percentage, 2)
                }

            return {
                "total_equipment": total_equipment,
                "equipment_with_completed_inspections": completed_count,
                "equipment_with_pending_inspections": pending_count,
                "percentage_completed": round(percentage_completed, 2),
                "percentage_pending": round(percentage_pending, 2),
                "inspection_completion_by_type": inspection_by_type,
                "equipment_without_inspection_status": no_status_count
            }

        except Exception as e:
            logger.error(f"Error calculating inspection completion KPIs: {str(e)}")
            return {
                "total_equipment": 0,
                "equipment_with_completed_inspections": 0,
                "equipment_with_pending_inspections": 0,
                "percentage_completed": 0.0,
                "percentage_pending": 0.0,
                "inspection_completion_by_type": {},
                "equipment_without_inspection_status": 0,
                "error": str(e)
            }

    def get_equipment_types_and_counts(self) -> Dict[str, Any]:
        """Get types and number of equipment"""
        try:
            if self.equipment_data.empty:
                return {
                    "total_equipment": 0,
                    "equipment_by_asset_type": {},
                    "equipment_by_type_category": {},
                    "equipment_by_location": {},
                    "unique_asset_types": 0,
                    "unique_type_categories": 0,
                    "unique_locations": 0
                }

            total_equipment = len(self.equipment_data)

            # Count by Asset (main equipment type)
            asset_counts = self.equipment_data['Asset'].value_counts().to_dict()

            # Count by Type (sub-category)
            type_counts = self.equipment_data['Type'].value_counts().to_dict()

            # Count by Location
            location_counts = self.equipment_data['Location'].value_counts().to_dict()

            # Remove NaN keys if they exist
            asset_counts = {k: v for k, v in asset_counts.items() if pd.notna(k)}
            type_counts = {k: v for k, v in type_counts.items() if pd.notna(k)}
            location_counts = {k: v for k, v in location_counts.items() if pd.notna(k)}

            return {
                "total_equipment": total_equipment,
                "equipment_by_asset_type": asset_counts,
                "equipment_by_type_category": type_counts,
                "equipment_by_location": location_counts,
                "unique_asset_types": len(asset_counts),
                "unique_type_categories": len(type_counts),
                "unique_locations": len(location_counts)
            }

        except Exception as e:
            logger.error(f"Error calculating equipment types and counts: {str(e)}")
            return {
                "total_equipment": 0,
                "equipment_by_asset_type": {},
                "equipment_by_type_category": {},
                "equipment_by_location": {},
                "unique_asset_types": 0,
                "unique_type_categories": 0,
                "unique_locations": 0,
                "error": str(e)
            }

    def get_equipment_insights(self, days_since_inspection_threshold: int = 365) -> Dict[str, Any]:
        """Get equipment insights for anomalies, overdue inspections, and certificate issues"""
        try:
            if self.equipment_data.empty:
                return {
                    "equipment_not_inspected_recently": [],
                    "equipment_without_proper_certificates": [],
                    "equipment_with_anomalies": [],
                    "total_equipment_needing_attention": 0
                }

            current_date = datetime.now()
            threshold_date = current_date - timedelta(days=days_since_inspection_threshold)

            # Equipment that haven't been inspected in a while
            old_inspection_equipment = []
            for _, row in self.equipment_data.iterrows():
                last_inspection = row['Last Inspection Date']
                if pd.notna(last_inspection) and last_inspection < threshold_date:
                    days_since = (current_date - last_inspection).days
                    old_inspection_equipment.append({
                        "asset_id": row['Asset ID'],
                        "asset_name": row['Asset'],
                        "type": row['Type'],
                        "location": row['Location'],
                        "last_inspection_date": last_inspection.strftime('%Y-%m-%d'),
                        "days_since_inspection": days_since,
                        "inspection_status": row['Inspection Status']
                    })

            # Equipment without proper calibration certificates
            no_cert_equipment = []
            for _, row in self.equipment_data.iterrows():
                cert_valid = row['Calibration Certificate Valid']
                if cert_valid == False or pd.isna(cert_valid):
                    no_cert_equipment.append({
                        "asset_id": row['Asset ID'],
                        "asset_name": row['Asset'],
                        "type": row['Type'],
                        "location": row['Location'],
                        "certificate_status": "Invalid" if cert_valid == False else "Missing",
                        "calibration_expiry_date": row['Calibration Expiry Date'].strftime('%Y-%m-%d') if pd.notna(row['Calibration Expiry Date']) else None
                    })

            # Equipment with anomalies/deviations
            anomaly_equipment = []
            for _, row in self.equipment_data.iterrows():
                if row['Anomalies/Deviations'] == True:
                    # Collect condition information
                    condition_issues = []
                    condition_columns = [
                        'Pressure Gauge', 'Hose & Nozzle', 'Lock & Pin', 'General Condition',
                        'Cut Mark', 'Major Continuous Crack', 'Deep Crack', 'Protective Layer',
                        'Connector Condition', 'Strap Condition', 'Shell Condition', 'Door Seal',
                        'Wiring', 'Power Cord', 'Electrode Holder'
                    ]

                    for col in condition_columns:
                        if col in self.equipment_data.columns and pd.notna(row[col]):
                            value = row[col]
                            if value in ['Needs Replacement', 'Needs Inspection', 'Poor', 'Broken', 'Frayed', 'Present', 'Near Coupling', 'Major', 'Minor', 'Loose']:
                                condition_issues.append(f"{col}: {value}")

                    anomaly_equipment.append({
                        "asset_id": row['Asset ID'],
                        "asset_name": row['Asset'],
                        "type": row['Type'],
                        "location": row['Location'],
                        "inspection_status": row['Inspection Status'],
                        "condition_issues": condition_issues,
                        "last_inspection_date": row['Last Inspection Date'].strftime('%Y-%m-%d') if pd.notna(row['Last Inspection Date']) else None
                    })

            # Calculate total equipment needing attention (unique equipment across all categories)
            all_asset_ids = set()
            for equipment_list in [old_inspection_equipment, no_cert_equipment, anomaly_equipment]:
                for equipment in equipment_list:
                    all_asset_ids.add(equipment['asset_id'])

            return {
                "equipment_not_inspected_recently": old_inspection_equipment,
                "equipment_without_proper_certificates": no_cert_equipment,
                "equipment_with_anomalies": anomaly_equipment,
                "total_equipment_needing_attention": len(all_asset_ids),
                "inspection_threshold_days": days_since_inspection_threshold
            }

        except Exception as e:
            logger.error(f"Error calculating equipment insights: {str(e)}")
            return {
                "equipment_not_inspected_recently": [],
                "equipment_without_proper_certificates": [],
                "equipment_with_anomalies": [],
                "total_equipment_needing_attention": 0,
                "error": str(e)
            }

    def get_equipment_asset_kpis(self, customer_id: Optional[str] = None, days_back: int = 365) -> Dict[str, Any]:
        """Get comprehensive equipment asset KPIs"""
        try:
            logger.info(f"Generating equipment asset KPIs for customer: {customer_id}")

            # Get all KPI components
            calibration_kpis = self.get_calibration_certificate_kpis()
            expiry_kpis = self.get_calibration_expiry_kpis(days_ahead=30)
            inspection_kpis = self.get_inspection_completion_kpis()
            equipment_types_kpis = self.get_equipment_types_and_counts()
            insights = self.get_equipment_insights(days_since_inspection_threshold=365)

            # Combine all KPIs into a comprehensive response
            response = {
                # Main KPIs
                "calibration_certificates": calibration_kpis,
                "calibration_expiry": expiry_kpis,
                "inspection_completion": inspection_kpis,
                "equipment_types_and_counts": equipment_types_kpis,

                # Insights
                "equipment_insights": insights,

                # Summary metrics for dashboard
                "summary_metrics": {
                    "total_equipment": equipment_types_kpis.get("total_equipment", 0),
                    "percentage_with_valid_certificates": calibration_kpis.get("percentage_with_valid_certificates", 0),
                    "percentage_expired_calibrations": expiry_kpis.get("percentage_expired", 0),
                    "percentage_upcoming_calibrations": expiry_kpis.get("percentage_upcoming", 0),
                    "percentage_completed_inspections": inspection_kpis.get("percentage_completed", 0),
                    "equipment_needing_attention": insights.get("total_equipment_needing_attention", 0),
                    "unique_equipment_types": equipment_types_kpis.get("unique_asset_types", 0)
                },

                # Metadata
                "generated_at": datetime.now().isoformat(),
                "data_source": "Equipment_Asset_Details.md"
            }

            # Convert all numpy types to native Python types for JSON serialization
            return convert_numpy_types(response)

        except Exception as e:
            logger.error(f"Error getting equipment asset KPIs: {str(e)}")
            return {
                "calibration_certificates": {},
                "calibration_expiry": {},
                "inspection_completion": {},
                "equipment_types_and_counts": {},
                "equipment_insights": {},
                "summary_metrics": {
                    "total_equipment": 0,
                    "percentage_with_valid_certificates": 0,
                    "percentage_expired_calibrations": 0,
                    "percentage_upcoming_calibrations": 0,
                    "percentage_completed_inspections": 0,
                    "equipment_needing_attention": 0,
                    "unique_equipment_types": 0
                },
                "error": str(e)
            }

    def close(self):
        """Close any resources (placeholder for consistency with other extractors)"""
        pass


# Standalone function for testing
def get_equipment_asset_kpis(customer_id: Optional[str] = None, days_back: int = 365) -> Dict[str, Any]:
    """Standalone function to get equipment asset KPIs"""
    try:
        extractor = EquipmentAssetKPIsExtractor()
        kpis = extractor.get_equipment_asset_kpis(customer_id, days_back)
        extractor.close()
        return kpis
    except Exception as e:
        logger.error(f"Error in standalone get_equipment_asset_kpis: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    """Test the Equipment Asset KPIs extractor"""

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    print("🏭 Testing Equipment Asset KPIs Extractor...")

    # Test with default parameters
    kpis = get_equipment_asset_kpis()

    print("\n📊 EQUIPMENT ASSET KPIs RESULTS:")
    print("=" * 50)

    if "error" in kpis:
        print(f"❌ Error: {kpis['error']}")
    else:
        summary = kpis.get("summary_metrics", {})
        print(f"📋 Total Equipment: {summary.get('total_equipment', 0)}")
        print(f"✅ Valid Certificates: {summary.get('percentage_with_valid_certificates', 0)}%")
        print(f"⏰ Expired Calibrations: {summary.get('percentage_expired_calibrations', 0)}%")
        print(f"🔍 Completed Inspections: {summary.get('percentage_completed_inspections', 0)}%")
        print(f"⚠️ Equipment Needing Attention: {summary.get('equipment_needing_attention', 0)}")
        print(f"🏷️ Unique Equipment Types: {summary.get('unique_equipment_types', 0)}")

        print(f"\n✅ Equipment Asset KPIs extraction completed successfully!")
        print(f"📁 Data source: Equipment_Asset_Details.md")
        print(f"🕒 Generated at: {kpis.get('generated_at', 'Unknown')}")
