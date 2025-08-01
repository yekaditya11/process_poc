"""
Employee Training & Fitness KPIs Extractor
Extracts KPIs and insights from HSE MASTER MATRIX data
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


class EmployeeTrainingKPIsExtractor:
    """Extract employee training and fitness KPIs from HSE MASTER MATRIX file"""

    def __init__(self):
        """Initialize the extractor"""
        self.data_file_path = os.path.join(os.path.dirname(__file__), '..', 'HSE MASTER MATRIX - EXPAT  NAT - Updaed on 29-04-2025.md')
        self.employee_data = None
        # Use a realistic date for testing with the HSE data (which appears to be from 2025)
        self.current_date = datetime(2025, 12, 1)  # December 1, 2025
        self._load_employee_data()

    def _load_employee_data(self):
        """Load and parse employee data from markdown file"""
        try:
            if not os.path.exists(self.data_file_path):
                logger.error(f"Employee data file not found: {self.data_file_path}")
                self.employee_data = pd.DataFrame()
                return

            # Read the markdown file
            with open(self.data_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Extract table data from markdown
            lines = content.split('\n')
            table_start = None
            table_data = []
            
            for i, line in enumerate(lines):
                if '| **Sr No**' in line:
                    table_start = i
                    continue
                elif table_start is not None and line.strip().startswith('|') and '---' not in line:
                    # Clean and split the line
                    row_data = [cell.strip() for cell in line.split('|')[1:-1]]
                    if len(row_data) > 10:  # Ensure it's a data row
                        table_data.append(row_data)
            
            # Define column names based on the header
            columns = [
                'Sr_No', 'Emp_No', 'Employee_Name', 'Designation', 'ID_Card', 'Location',
                'HSE_PP', 'HSE_ORT', 'H2S_3Y', 'CHM_NA', 'SCBA_3Y', 'AHA_2Y', 'AGT_3Y',
                'HSELFS_4Y', 'PTWH_3Y', 'PTWS_3Y', 'HII_NA', 'EA_NA', 'NORM_4Y', 'FW_3Y',
                'CISRS_L1_5Y', 'CISRS_L2_5Y', 'CISRS_Supvr_5Y', 'CISRS_Insptr_5Y',
                'SC_Optr_3Y', 'JM_4Y', 'RB_3Y', 'LIFT_SUP_3Y', 'AP_3Y', 'MEWP_3Y',
                'VM_3Y', 'Hiab_3Y', 'DD02_HV', 'DD03_GR', 'DD04_Tanker', 'DD05_Bus',
                'L_Bus', 'DD06_RT_2Y', 'VTO_3Y', 'CISRS_ASI_5Y', 'CISRS_L3_5Y',
                'NON_PDO_CS_2Y', 'NON_PDO_IFR_2Y', 'NON_PDO_CHA_2Y', 'NON_PDO_WAH_2Y',
                'NON_PDO', 'Unnamed_46', 'OQ_MED_Expiration', 'PDO_MED_Expiration',
                'Medical_Fitness', 'DOB', 'AGE', 'BMI', 'Follow_Up_Finding', 'Framing_Risk_Percent'
            ]
            
            # Create DataFrame
            self.employee_data = pd.DataFrame(table_data, columns=columns[:len(table_data[0])])
            
            # Clean up data types and handle empty values
            self._clean_data()
            
            logger.info(f"Successfully loaded {len(self.employee_data)} employee records")

        except Exception as e:
            logger.error(f"Error loading employee data: {str(e)}")
            self.employee_data = pd.DataFrame()

    def _clean_data(self):
        """Clean and standardize the employee data"""
        if self.employee_data.empty:
            return

        # Replace empty strings and dashes with None
        self.employee_data = self.employee_data.replace(['', '-'], None)
        
        # Get training columns (those with date values)
        self.training_columns = [
            'H2S_3Y', 'SCBA_3Y', 'AHA_2Y', 'AGT_3Y', 'HSELFS_4Y', 'PTWH_3Y',
            'PTWS_3Y', 'NORM_4Y', 'FW_3Y', 'CISRS_L1_5Y', 'CISRS_L2_5Y',
            'CISRS_Supvr_5Y', 'CISRS_Insptr_5Y', 'SC_Optr_3Y', 'JM_4Y',
            'RB_3Y', 'LIFT_SUP_3Y', 'AP_3Y', 'MEWP_3Y', 'VM_3Y', 'Hiab_3Y',
            'DD06_RT_2Y', 'VTO_3Y', 'CISRS_ASI_5Y', 'CISRS_L3_5Y',
            'NON_PDO_CS_2Y', 'NON_PDO_IFR_2Y', 'NON_PDO_CHA_2Y', 'NON_PDO_WAH_2Y'
        ]
        
        # Convert date columns - handle both formats with and without time
        date_columns = self.training_columns + ['OQ_MED_Expiration', 'PDO_MED_Expiration', 'DOB']
        for col in date_columns:
            if col in self.employee_data.columns:
                # First try to parse with time component, then without
                self.employee_data[col] = pd.to_datetime(
                    self.employee_data[col],
                    errors='coerce'
                )

        logger.info("Employee data cleaned and standardized")

    def parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        if not date_str or date_str == '-' or str(date_str).strip() == '' or pd.isna(date_str):
            return None
        
        try:
            # Handle different date formats
            if '00:00:00' in str(date_str):
                return datetime.strptime(str(date_str).split(' ')[0], '%Y-%m-%d')
            else:
                return datetime.strptime(str(date_str), '%Y-%m-%d')
        except:
            return None

    def get_expired_trainings_kpis(self) -> Dict[str, Any]:
        """Calculate number of employees with expired trainings"""
        try:
            if self.employee_data.empty:
                return {
                    "total_employees": 0,
                    "employees_with_expired_trainings": 0,
                    "percentage_with_expired_trainings": 0.0,
                    "expired_training_details": [],
                    "expired_trainings_by_type": {}
                }

            expired_employees = set()
            expired_details = []
            expired_by_type = {}
            
            for _, row in self.employee_data.iterrows():
                employee_expired_trainings = []
                
                for col in self.training_columns:
                    if col in self.employee_data.columns:
                        date_val = row[col]
                        if pd.notna(date_val) and date_val < self.current_date:
                            expired_employees.add(row['Employee_Name'])
                            training_name = col.replace('_', ' ').replace('3Y', '(3 Years)').replace('2Y', '(2 Years)').replace('4Y', '(4 Years)').replace('5Y', '(5 Years)')
                            
                            expired_details.append({
                                'employee': row['Employee_Name'],
                                'emp_no': row['Emp_No'],
                                'training': training_name,
                                'expired_date': date_val.strftime('%Y-%m-%d'),
                                'days_overdue': (self.current_date - date_val).days,
                                'location': row['Location'],
                                'designation': row['Designation']
                            })
                            
                            employee_expired_trainings.append(training_name)
                            
                            # Count by training type
                            if training_name not in expired_by_type:
                                expired_by_type[training_name] = 0
                            expired_by_type[training_name] += 1

            total_employees = len(self.employee_data)
            expired_count = len(expired_employees)
            percentage_expired = (expired_count / total_employees * 100) if total_employees > 0 else 0

            return {
                "total_employees": total_employees,
                "employees_with_expired_trainings": expired_count,
                "percentage_with_expired_trainings": round(percentage_expired, 2),
                "expired_training_details": expired_details,
                "expired_trainings_by_type": expired_by_type
            }

        except Exception as e:
            logger.error(f"Error calculating expired trainings KPIs: {str(e)}")
            return {
                "total_employees": 0,
                "employees_with_expired_trainings": 0,
                "percentage_with_expired_trainings": 0.0,
                "expired_training_details": [],
                "expired_trainings_by_type": {},
                "error": str(e)
            }

    def get_upcoming_training_expiry_kpis(self, months: int = 6) -> Dict[str, Any]:
        """Calculate employees with upcoming training expiry"""
        try:
            if self.employee_data.empty:
                return {
                    "total_employees": 0,
                    "employees_with_upcoming_expiry": 0,
                    "percentage_with_upcoming_expiry": 0.0,
                    "upcoming_expiry_details": [],
                    "upcoming_expiry_by_month": {}
                }

            cutoff_date = self.current_date + timedelta(days=months*30)
            upcoming_employees = set()
            upcoming_details = []
            upcoming_by_month = {}
            
            for _, row in self.employee_data.iterrows():
                for col in self.training_columns:
                    if col in self.employee_data.columns:
                        date_val = row[col]
                        if pd.notna(date_val) and self.current_date <= date_val <= cutoff_date:
                            upcoming_employees.add(row['Employee_Name'])
                            training_name = col.replace('_', ' ').replace('3Y', '(3 Years)').replace('2Y', '(2 Years)').replace('4Y', '(4 Years)').replace('5Y', '(5 Years)')
                            days_remaining = (date_val - self.current_date).days
                            
                            upcoming_details.append({
                                'employee': row['Employee_Name'],
                                'emp_no': row['Emp_No'],
                                'training': training_name,
                                'expiry_date': date_val.strftime('%Y-%m-%d'),
                                'days_remaining': days_remaining,
                                'location': row['Location'],
                                'designation': row['Designation']
                            })
                            
                            # Group by month
                            month_key = date_val.strftime('%Y-%m')
                            if month_key not in upcoming_by_month:
                                upcoming_by_month[month_key] = []
                            upcoming_by_month[month_key].append({
                                'employee': row['Employee_Name'],
                                'training': training_name,
                                'expiry_date': date_val.strftime('%Y-%m-%d')
                            })

            total_employees = len(self.employee_data)
            upcoming_count = len(upcoming_employees)
            percentage_upcoming = (upcoming_count / total_employees * 100) if total_employees > 0 else 0

            return {
                "total_employees": total_employees,
                "employees_with_upcoming_expiry": upcoming_count,
                "percentage_with_upcoming_expiry": round(percentage_upcoming, 2),
                "upcoming_expiry_details": upcoming_details,
                "upcoming_expiry_by_month": upcoming_by_month,
                "analysis_period_months": months
            }

        except Exception as e:
            logger.error(f"Error calculating upcoming training expiry KPIs: {str(e)}")
            return {
                "total_employees": 0,
                "employees_with_upcoming_expiry": 0,
                "percentage_with_upcoming_expiry": 0.0,
                "upcoming_expiry_details": [],
                "upcoming_expiry_by_month": {},
                "error": str(e)
            }

    def get_fitness_kpis(self) -> Dict[str, Any]:
        """Calculate fitness-related KPIs"""
        try:
            if self.employee_data.empty:
                return {
                    "total_employees": 0,
                    "unfit_employees": 0,
                    "fit_employees": 0,
                    "percentage_unfit": 0.0,
                    "percentage_fit": 0.0,
                    "fitness_by_department": {},
                    "unfit_employee_details": []
                }

            total_employees = len(self.employee_data)
            unfit_count = 0
            fit_count = 0
            unfit_details = []

            # Count fitness status
            for _, row in self.employee_data.iterrows():
                fitness_status = str(row['Medical_Fitness']).lower() if pd.notna(row['Medical_Fitness']) else ''

                if 'unfit' in fitness_status or 'not fit' in fitness_status:
                    unfit_count += 1
                    unfit_details.append({
                        'employee': row['Employee_Name'],
                        'emp_no': row['Emp_No'],
                        'location': row['Location'],
                        'designation': row['Designation'],
                        'fitness_status': row['Medical_Fitness'],
                        'follow_up': row['Follow_Up_Finding']
                    })
                elif 'fit' in fitness_status:
                    fit_count += 1

            # Calculate percentages
            percentage_unfit = (unfit_count / total_employees * 100) if total_employees > 0 else 0
            percentage_fit = (fit_count / total_employees * 100) if total_employees > 0 else 0

            # Calculate fit percentage by department
            dept_fitness = {}
            for _, row in self.employee_data.iterrows():
                location = row['Location'] if pd.notna(row['Location']) and row['Location'] != '-' else 'Unspecified'
                if location not in dept_fitness:
                    dept_fitness[location] = {'total': 0, 'fit': 0, 'unfit': 0}

                dept_fitness[location]['total'] += 1
                fitness_status = str(row['Medical_Fitness']).lower() if pd.notna(row['Medical_Fitness']) else ''

                if 'unfit' in fitness_status or 'not fit' in fitness_status:
                    dept_fitness[location]['unfit'] += 1
                elif 'fit' in fitness_status:
                    dept_fitness[location]['fit'] += 1

            # Calculate percentages for each department
            for dept in dept_fitness:
                total = dept_fitness[dept]['total']
                fit = dept_fitness[dept]['fit']
                unfit = dept_fitness[dept]['unfit']
                dept_fitness[dept]['fit_percentage'] = round((fit / total) * 100, 2) if total > 0 else 0
                dept_fitness[dept]['unfit_percentage'] = round((unfit / total) * 100, 2) if total > 0 else 0

            return {
                "total_employees": total_employees,
                "unfit_employees": unfit_count,
                "fit_employees": fit_count,
                "percentage_unfit": round(percentage_unfit, 2),
                "percentage_fit": round(percentage_fit, 2),
                "fitness_by_department": dept_fitness,
                "unfit_employee_details": unfit_details
            }

        except Exception as e:
            logger.error(f"Error calculating fitness KPIs: {str(e)}")
            return {
                "total_employees": 0,
                "unfit_employees": 0,
                "fit_employees": 0,
                "percentage_unfit": 0.0,
                "percentage_fit": 0.0,
                "fitness_by_department": {},
                "unfit_employee_details": [],
                "error": str(e)
            }

    def get_department_training_kpis(self) -> Dict[str, Any]:
        """Calculate training expiries by department"""
        try:
            if self.employee_data.empty:
                return {
                    "departments": {},
                    "total_departments": 0,
                    "departments_with_pending_trainings": 0
                }

            dept_training = {}
            cutoff_date = self.current_date + timedelta(days=365)  # Next 12 months

            for _, row in self.employee_data.iterrows():
                location = row['Location'] if pd.notna(row['Location']) and row['Location'] != '-' else 'Unspecified'
                if location not in dept_training:
                    dept_training[location] = {
                        'employees': [],
                        'total_employees': 0,
                        'expiring_trainings': 0,
                        'expired_trainings': 0,
                        'employees_with_expiring_trainings': 0,
                        'employees_with_expired_trainings': 0
                    }

                dept_training[location]['total_employees'] += 1

                employee_expiring = 0
                employee_expired = 0

                for col in self.training_columns:
                    if col in self.employee_data.columns:
                        date_val = row[col]
                        if pd.notna(date_val):
                            if date_val < self.current_date:
                                employee_expired += 1
                            elif self.current_date <= date_val <= cutoff_date:
                                employee_expiring += 1

                if employee_expiring > 0 or employee_expired > 0:
                    dept_training[location]['employees'].append({
                        'name': row['Employee_Name'],
                        'emp_no': row['Emp_No'],
                        'designation': row['Designation'],
                        'expiring_count': employee_expiring,
                        'expired_count': employee_expired
                    })

                    if employee_expiring > 0:
                        dept_training[location]['employees_with_expiring_trainings'] += 1
                    if employee_expired > 0:
                        dept_training[location]['employees_with_expired_trainings'] += 1

                    dept_training[location]['expiring_trainings'] += employee_expiring
                    dept_training[location]['expired_trainings'] += employee_expired

            # Calculate summary statistics
            total_departments = len(dept_training)
            departments_with_pending = sum(1 for dept_data in dept_training.values()
                                         if dept_data['expired_trainings'] > 0 or dept_data['expiring_trainings'] > 0)

            return {
                "departments": dept_training,
                "total_departments": total_departments,
                "departments_with_pending_trainings": departments_with_pending
            }

        except Exception as e:
            logger.error(f"Error calculating department training KPIs: {str(e)}")
            return {
                "departments": {},
                "total_departments": 0,
                "departments_with_pending_trainings": 0,
                "error": str(e)
            }

    def get_medical_data_completeness_kpis(self) -> Dict[str, Any]:
        """Calculate employees with missing medical details"""
        try:
            if self.employee_data.empty:
                return {
                    "total_employees": 0,
                    "employees_with_missing_medical_data": 0,
                    "percentage_missing_medical_data": 0.0,
                    "missing_data_details": [],
                    "missing_data_by_field": {}
                }

            missing_data_employees = []
            missing_by_field = {
                'BMI': 0,
                'DOB': 0,
                'AGE': 0,
                'Medical_Fitness': 0,
                'OQ_MED_Expiration': 0,
                'PDO_MED_Expiration': 0
            }

            for _, row in self.employee_data.iterrows():
                missing_fields = []

                # Check each medical field
                medical_fields = {
                    'BMI': row['BMI'],
                    'DOB': row['DOB'],
                    'AGE': row['AGE'],
                    'Medical_Fitness': row['Medical_Fitness'],
                    'OQ_MED_Expiration': row['OQ_MED_Expiration'],
                    'PDO_MED_Expiration': row['PDO_MED_Expiration']
                }

                for field, value in medical_fields.items():
                    if pd.isna(value) or str(value).strip() == '' or str(value).strip() == '-':
                        missing_fields.append(field)
                        missing_by_field[field] += 1

                if missing_fields:
                    missing_data_employees.append({
                        'employee': row['Employee_Name'],
                        'emp_no': row['Emp_No'],
                        'location': row['Location'],
                        'designation': row['Designation'],
                        'missing_fields': missing_fields
                    })

            total_employees = len(self.employee_data)
            missing_count = len(missing_data_employees)
            percentage_missing = (missing_count / total_employees * 100) if total_employees > 0 else 0

            return {
                "total_employees": total_employees,
                "employees_with_missing_medical_data": missing_count,
                "percentage_missing_medical_data": round(percentage_missing, 2),
                "missing_data_details": missing_data_employees,
                "missing_data_by_field": missing_by_field
            }

        except Exception as e:
            logger.error(f"Error calculating medical data completeness KPIs: {str(e)}")
            return {
                "total_employees": 0,
                "employees_with_missing_medical_data": 0,
                "percentage_missing_medical_data": 0.0,
                "missing_data_details": [],
                "missing_data_by_field": {},
                "error": str(e)
            }

    def get_medical_expiry_kpis(self, months: int = 6) -> Dict[str, Any]:
        """Calculate medical certification expiry KPIs"""
        try:
            if self.employee_data.empty:
                return {
                    "total_employees": 0,
                    "employees_with_expiring_medical": 0,
                    "employees_with_expired_medical": 0,
                    "percentage_expiring_medical": 0.0,
                    "percentage_expired_medical": 0.0,
                    "medical_expiry_details": []
                }

            cutoff_date = self.current_date + timedelta(days=months*30)
            expiring_employees = set()
            expired_employees = set()
            medical_expiry_details = []

            medical_columns = ['OQ_MED_Expiration', 'PDO_MED_Expiration']

            for _, row in self.employee_data.iterrows():
                for col in medical_columns:
                    if col in self.employee_data.columns:
                        date_val = row[col]
                        if pd.notna(date_val):
                            if date_val < self.current_date:
                                expired_employees.add(row['Employee_Name'])
                                medical_expiry_details.append({
                                    'employee': row['Employee_Name'],
                                    'emp_no': row['Emp_No'],
                                    'medical_type': col.replace('_', ' '),
                                    'expiry_date': date_val.strftime('%Y-%m-%d'),
                                    'status': 'Expired',
                                    'days_overdue': (self.current_date - date_val).days,
                                    'location': row['Location'],
                                    'designation': row['Designation']
                                })
                            elif self.current_date <= date_val <= cutoff_date:
                                expiring_employees.add(row['Employee_Name'])
                                medical_expiry_details.append({
                                    'employee': row['Employee_Name'],
                                    'emp_no': row['Emp_No'],
                                    'medical_type': col.replace('_', ' '),
                                    'expiry_date': date_val.strftime('%Y-%m-%d'),
                                    'status': 'Expiring Soon',
                                    'days_remaining': (date_val - self.current_date).days,
                                    'location': row['Location'],
                                    'designation': row['Designation']
                                })

            total_employees = len(self.employee_data)
            expiring_count = len(expiring_employees)
            expired_count = len(expired_employees)

            percentage_expiring = (expiring_count / total_employees * 100) if total_employees > 0 else 0
            percentage_expired = (expired_count / total_employees * 100) if total_employees > 0 else 0

            return {
                "total_employees": total_employees,
                "employees_with_expiring_medical": expiring_count,
                "employees_with_expired_medical": expired_count,
                "percentage_expiring_medical": round(percentage_expiring, 2),
                "percentage_expired_medical": round(percentage_expired, 2),
                "medical_expiry_details": medical_expiry_details,
                "analysis_period_months": months
            }

        except Exception as e:
            logger.error(f"Error calculating medical expiry KPIs: {str(e)}")
            return {
                "total_employees": 0,
                "employees_with_expiring_medical": 0,
                "employees_with_expired_medical": 0,
                "percentage_expiring_medical": 0.0,
                "percentage_expired_medical": 0.0,
                "medical_expiry_details": [],
                "error": str(e)
            }

    def generate_insights(self) -> List[str]:
        """Generate key insights and findings"""
        insights = []

        try:
            # Calculate all metrics for insights
            expired = self.get_expired_trainings_kpis()
            upcoming = self.get_upcoming_training_expiry_kpis()
            fitness = self.get_fitness_kpis()
            medical_data = self.get_medical_data_completeness_kpis()
            dept_training = self.get_department_training_kpis()
            medical_expiry = self.get_medical_expiry_kpis()

            # Generate insights based on data
            if expired['employees_with_expired_trainings'] > 0:
                insights.append(f"CRITICAL: {expired['employees_with_expired_trainings']} employees have expired training certifications requiring immediate recertification")

            if upcoming['employees_with_upcoming_expiry'] > 0:
                insights.append(f"URGENT: {upcoming['employees_with_upcoming_expiry']} employees have trainings expiring within 6 months")

            if fitness['percentage_unfit'] > 0:
                insights.append(f"HEALTH CONCERN: {fitness['percentage_unfit']}% of employees are unfit for work")
            else:
                insights.append("POSITIVE: All employees are currently fit for work")

            if medical_data['employees_with_missing_medical_data'] > 0:
                insights.append(f"DATA GAP: {medical_data['employees_with_missing_medical_data']} employees have incomplete medical records")

            if medical_expiry['employees_with_expired_medical'] > 0:
                insights.append(f"MEDICAL ALERT: {medical_expiry['employees_with_expired_medical']} employees have expired medical certifications")

            # Department-specific insights
            high_risk_depts = []
            for dept, data in dept_training['departments'].items():
                if data['expired_trainings'] > 0 or data['expiring_trainings'] > 5:
                    high_risk_depts.append(f"{dept} ({data['expired_trainings']} expired, {data['expiring_trainings']} expiring)")

            if high_risk_depts:
                insights.append(f"HIGH PRIORITY DEPARTMENTS: {', '.join(high_risk_depts[:3])}")  # Limit to top 3

            # Training type insights
            if expired.get('expired_trainings_by_type'):
                most_expired = max(expired['expired_trainings_by_type'].items(), key=lambda x: x[1])
                insights.append(f"MOST EXPIRED TRAINING: {most_expired[0]} with {most_expired[1]} expired certifications")

            # Risk assessment insights
            high_risk_employees = []
            for _, row in self.employee_data.iterrows():
                risk_percent = row['Framing_Risk_Percent']
                if pd.notna(risk_percent) and str(risk_percent).replace('%', '').replace('Nil', '0') != '0':
                    try:
                        risk_value = float(str(risk_percent).replace('%', ''))
                        if risk_value > 0.05:  # 0.05% threshold
                            high_risk_employees.append(row['Employee_Name'])
                    except:
                        pass

            if high_risk_employees:
                insights.append(f"HIGH RISK EMPLOYEES: {len(high_risk_employees)} employees require enhanced safety monitoring")

        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            insights.append("Error generating insights - please check data quality")

        return insights

    def get_employee_training_kpis(self, customer_id: Optional[str] = None, days_back: int = 365) -> Dict[str, Any]:
        """Get comprehensive employee training and fitness KPIs"""
        try:
            logger.info(f"Generating employee training KPIs for customer: {customer_id}")

            # Get all KPI components
            expired_trainings = self.get_expired_trainings_kpis()
            upcoming_expiry = self.get_upcoming_training_expiry_kpis()
            fitness_metrics = self.get_fitness_kpis()
            department_training = self.get_department_training_kpis()
            medical_completeness = self.get_medical_data_completeness_kpis()
            medical_expiry = self.get_medical_expiry_kpis()
            insights = self.generate_insights()

            # Combine all KPIs into a comprehensive response
            response = {
                # Main Training KPIs
                "expired_trainings": expired_trainings,
                "upcoming_training_expiry": upcoming_expiry,
                "department_training_status": department_training,

                # Fitness KPIs
                "fitness_metrics": fitness_metrics,

                # Medical KPIs
                "medical_data_completeness": medical_completeness,
                "medical_expiry": medical_expiry,

                # Insights
                "key_insights": insights,

                # Summary metrics for dashboard
                "summary_metrics": {
                    "total_employees": expired_trainings.get("total_employees", 0),
                    "employees_with_expired_trainings": expired_trainings.get("employees_with_expired_trainings", 0),
                    "employees_with_upcoming_expiry": upcoming_expiry.get("employees_with_upcoming_expiry", 0),
                    "percentage_unfit_employees": fitness_metrics.get("percentage_unfit", 0),
                    "percentage_fit_employees": fitness_metrics.get("percentage_fit", 0),
                    "employees_missing_medical_data": medical_completeness.get("employees_with_missing_medical_data", 0),
                    "departments_with_pending_trainings": department_training.get("departments_with_pending_trainings", 0),
                    "employees_with_expired_medical": medical_expiry.get("employees_with_expired_medical", 0)
                },

                # Metadata
                "generated_at": datetime.now().isoformat(),
                "data_source": "HSE MASTER MATRIX - EXPAT NAT - Updated on 29-04-2025"
            }

            # Convert all numpy types to native Python types for JSON serialization
            return convert_numpy_types(response)

        except Exception as e:
            logger.error(f"Error getting employee training KPIs: {str(e)}")
            return {
                "expired_trainings": {},
                "upcoming_training_expiry": {},
                "department_training_status": {},
                "fitness_metrics": {},
                "medical_data_completeness": {},
                "medical_expiry": {},
                "key_insights": [],
                "summary_metrics": {
                    "total_employees": 0,
                    "employees_with_expired_trainings": 0,
                    "employees_with_upcoming_expiry": 0,
                    "percentage_unfit_employees": 0,
                    "percentage_fit_employees": 0,
                    "employees_missing_medical_data": 0,
                    "departments_with_pending_trainings": 0,
                    "employees_with_expired_medical": 0
                },
                "error": str(e)
            }

    def close(self):
        """Close any resources (placeholder for consistency with other extractors)"""
        pass


# Standalone function for testing
def get_employee_training_kpis(customer_id: Optional[str] = None, days_back: int = 365) -> Dict[str, Any]:
    """Standalone function to get employee training KPIs"""
    try:
        extractor = EmployeeTrainingKPIsExtractor()
        kpis = extractor.get_employee_training_kpis(customer_id, days_back)
        extractor.close()
        return kpis
    except Exception as e:
        logger.error(f"Error in standalone get_employee_training_kpis: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    """Test the Employee Training KPIs extractor"""

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    print("👥 Testing Employee Training KPIs Extractor...")

    # Test with default parameters
    kpis = get_employee_training_kpis()

    print("\n📊 EMPLOYEE TRAINING KPIs RESULTS:")
    print("=" * 50)

    if "error" in kpis:
        print(f"❌ Error: {kpis['error']}")
    else:
        summary = kpis.get("summary_metrics", {})
        print(f"👥 Total Employees: {summary.get('total_employees', 0)}")
        print(f"⏰ Expired Trainings: {summary.get('employees_with_expired_trainings', 0)}")
        print(f"📅 Upcoming Expiry: {summary.get('employees_with_upcoming_expiry', 0)}")
        print(f"❌ Unfit Employees: {summary.get('percentage_unfit_employees', 0)}%")
        print(f"✅ Fit Employees: {summary.get('percentage_fit_employees', 0)}%")
        print(f"📋 Missing Medical Data: {summary.get('employees_missing_medical_data', 0)}")
        print(f"🏢 Departments with Pending: {summary.get('departments_with_pending_trainings', 0)}")

        print(f"\n🔍 KEY INSIGHTS:")
        for insight in kpis.get("key_insights", [])[:5]:  # Show top 5 insights
            print(f"• {insight}")

        # Print detailed expired training information
        expired_details = kpis.get("expired_trainings", {}).get("expired_training_details", [])
        if expired_details:
            print(f"\n⚠️ EMPLOYEES WITH EXPIRED TRAININGS:")
            print("=" * 60)
            current_employee = None
            for detail in expired_details:
                if current_employee != detail['employee']:
                    if current_employee is not None:
                        print()  # Add space between employees
                    current_employee = detail['employee']
                    print(f"👤 {detail['employee']} (ID: {detail['emp_no']}) - {detail['designation']}")
                    print(f"   📍 Location: {detail['location']}")

                print(f"   ❌ {detail['training']} - Expired: {detail['expired_date']} ({detail['days_overdue']} days overdue)")

        # Print upcoming expiry information
        upcoming_details = kpis.get("upcoming_training_expiry", {}).get("upcoming_expiry_details", [])
        if upcoming_details:
            print(f"\n📅 EMPLOYEES WITH UPCOMING TRAINING EXPIRY:")
            print("=" * 60)
            current_employee = None
            for detail in upcoming_details:
                if current_employee != detail['employee']:
                    if current_employee is not None:
                        print()  # Add space between employees
                    current_employee = detail['employee']
                    print(f"👤 {detail['employee']} (ID: {detail['emp_no']}) - {detail['designation']}")
                    print(f"   📍 Location: {detail['location']}")

                print(f"   ⏰ {detail['training']} - Expires: {detail['expiry_date']} ({detail['days_remaining']} days remaining)")

        print(f"\n✅ Employee Training KPIs extraction completed successfully!")
        print(f"📁 Data source: HSE MASTER MATRIX")
        print(f"🕒 Generated at: {kpis.get('generated_at', 'Unknown')}")
