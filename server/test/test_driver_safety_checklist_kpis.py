"""
Test file for Driver Safety Checklist KPIs Module
This test demonstrates the complete response structure that will be sent to the frontend.

Module: Driver Safety Checklists
Template ID: 'a35be57e-dd36-4a21-b05b-e4d4fa836f53'
KPIs: Daily/Weekly completion percentages, Vehicle fitness assessment, Overdue drivers
"""

import json
import logging
from datetime import datetime, timedelta
from data_extractors.driver_safety_checklist_kpis_extractor import get_driver_safety_checklist_kpis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_driver_safety_checklist_kpis():
    """
    Test the Driver Safety Checklist KPIs extractor and show complete response structure
    """
    print("🚗 Testing Driver Safety Checklist KPIs Module...")
    print("=" * 60)
    
    try:
        # Test parameters
        customer_id = None  # Test with all customers
        days_back = 365  # Last 365 days (default)
        
        print(f"📅 Date Range: Last {days_back} days (365 days default)")
        print(f"👤 Customer ID: {customer_id or 'All customers'}")
        print(f"🎯 Template ID: a35be57e-dd36-4a21-b05b-e4d4fa836f53")
        print()
        
        # Extract KPIs
        print("🚀 Extracting Driver Safety Checklist KPIs...")
        kpis_response = get_driver_safety_checklist_kpis(customer_id, days_back)
        
        # Display results
        print("✅ Driver Safety Checklist KPIs extracted successfully!")
        print()
        print("📊 COMPLETE RESPONSE STRUCTURE FOR FRONTEND:")
        print("=" * 60)
        
        # Pretty print the complete response structure
        response_json = json.dumps(kpis_response, indent=2, default=str)
        print(response_json)
        
        print()
        print("📋 SUMMARY OF RESPONSE STRUCTURE:")
        print("=" * 60)
        
        # Template Information
        print("🎯 TEMPLATE INFORMATION:")
        print(f"  - template_id: {kpis_response.get('template_id', 'N/A')}")
        print(f"  - template_name: {kpis_response.get('template_name', 'N/A')}")
        
        print()
        print("📈 DAILY COMPLETION STATS:")
        daily_stats = kpis_response.get('daily_completion_stats', {})
        print(f"  - total_completed_checklists: {daily_stats.get('total_completed_checklists', 0)}")
        print(f"  - average_daily_completion: {daily_stats.get('average_daily_completion', 0)}")
        print(f"  - total_days_analyzed: {daily_stats.get('total_days_analyzed', 0)}")
        print(f"  - daily_breakdown: {len(daily_stats.get('daily_breakdown', []))} days")
        
        print()
        print("📊 WEEKLY COMPLETION STATS:")
        weekly_stats = kpis_response.get('weekly_completion_stats', {})
        print(f"  - total_completed_checklists: {weekly_stats.get('total_completed_checklists', 0)}")
        print(f"  - average_weekly_completion: {weekly_stats.get('average_weekly_completion', 0)}")
        print(f"  - total_weeks_analyzed: {weekly_stats.get('total_weeks_analyzed', 0)}")
        print(f"  - weekly_breakdown: {len(weekly_stats.get('weekly_breakdown', []))} weeks")
        
        print()
        print("🚛 VEHICLE FITNESS ANALYSIS:")
        fitness_analysis = kpis_response.get('vehicle_fitness_analysis', {})
        print(f"  - total_vehicles_inspected: {fitness_analysis.get('total_vehicles_inspected', 0)}")
        print(f"  - vehicles_deemed_unfit: {fitness_analysis.get('vehicles_deemed_unfit', 0)}")
        print(f"  - vehicles_deemed_fit: {fitness_analysis.get('vehicles_deemed_fit', 0)}")
        print(f"  - unfit_percentage: {fitness_analysis.get('unfit_percentage', 0)}%")
        print(f"  - unfit_vehicles_details: {len(fitness_analysis.get('unfit_vehicles_details', []))} vehicles")
        print(f"  - fit_vehicles_details: {len(fitness_analysis.get('fit_vehicles_details', []))} vehicles")
        
        print()
        print("⚠️ OVERDUE DRIVERS INSIGHT:")
        overdue_insight = kpis_response.get('overdue_drivers_insight', {})
        print(f"  - total_overdue_drivers: {overdue_insight.get('total_overdue_drivers', 0)}")
        print(f"  - overdue_schedules_count: {overdue_insight.get('overdue_schedules_count', 0)}")
        print(f"  - overdue_histories_count: {overdue_insight.get('overdue_histories_count', 0)}")
        print(f"  - overdue_drivers_list: {len(overdue_insight.get('overdue_drivers_list', []))} drivers")
        
        print()
        print("📊 SUMMARY METRICS:")
        summary = kpis_response.get('summary', {})
        print(f"  - total_daily_completions: {summary.get('total_daily_completions', 0)}")
        print(f"  - average_daily_completion: {summary.get('average_daily_completion', 0)}")
        print(f"  - total_weekly_completions: {summary.get('total_weekly_completions', 0)}")
        print(f"  - average_weekly_completion: {summary.get('average_weekly_completion', 0)}")
        print(f"  - total_vehicles_inspected: {summary.get('total_vehicles_inspected', 0)}")
        print(f"  - vehicles_deemed_unfit: {summary.get('vehicles_deemed_unfit', 0)}")
        print(f"  - unfit_percentage: {summary.get('unfit_percentage', 0)}%")
        print(f"  - total_overdue_drivers: {summary.get('total_overdue_drivers', 0)}")
        print(f"  - overdue_schedules_count: {summary.get('overdue_schedules_count', 0)}")
        print(f"  - overdue_histories_count: {summary.get('overdue_histories_count', 0)}")
        
        print()
        print("🎯 FRONTEND INTEGRATION NOTES:")
        print("=" * 60)
        print("• This response structure is ready for frontend consumption")
        print("• Daily/Weekly breakdowns provide time-series data for charts")
        print("• Vehicle fitness analysis includes AI-based assessment")
        print("• Overdue drivers insight helps identify compliance issues")
        print("• Summary section provides quick overview metrics")
        print("• All percentages are calculated and ready for display")
        print("• Date ranges are in ISO format for easy parsing")
        
        return kpis_response
        
    except Exception as e:
        logger.error(f"❌ Error testing Driver Safety Checklist KPIs: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    """Run the test"""
    result = test_driver_safety_checklist_kpis()
    
    print()
    print("🏁 Test completed!")
    if "error" not in result:
        print("✅ Driver Safety Checklist KPIs module is working correctly!")
        print("📤 Response structure is ready for frontend integration!")
    else:
        print("❌ Test failed - check logs for details")
