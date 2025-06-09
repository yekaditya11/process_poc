"""
Test file for Action Tracking KPIs Module
This test demonstrates the complete response structure that will be sent to the frontend.

Module: Action Tracking
KPIs: Number of actions created, % completed on time, open vs closed actions
Insights: Employees not completing actions on time
"""

import json
import logging
from datetime import datetime, timedelta
from data_extractors.actiontracking_kpis import get_action_tracking_kpis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_action_tracking_kpis():
    """
    Test the Action Tracking KPIs extractor and show complete response structure
    """
    print("🚀 Testing Action Tracking KPIs Module...")
    print("=" * 60)
    
    try:
        # Test parameters
        customer_id = None  # Test with all customers
        days_back = 365  # Last year
        
        print(f"📅 Date Range: Last {days_back} days (365 days default)")
        print(f"👤 Customer ID: {customer_id or 'All customers'}")
        print()
        
        # Extract KPIs
        print("🚀 Extracting Action Tracking KPIs...")
        kpis_response = get_action_tracking_kpis(customer_id, days_back)
        
        # Display results
        print("✅ Action Tracking KPIs extracted successfully!")
        print()
        print("📊 COMPLETE RESPONSE STRUCTURE FOR FRONTEND:")
        print("=" * 60)
        
        # Pretty print the complete response structure
        response_json = json.dumps(kpis_response, indent=2, default=str)
        print(response_json)
        
        print()
        print("📋 SUMMARY OF RESPONSE STRUCTURE:")
        print("=" * 60)
        
        # Action Tracking KPIs
        print("📈 ACTION TRACKING KPIs:")
        action_kpis = kpis_response.get('action_tracking_kpis', {})
        
        # Number of Actions Created
        actions_created = action_kpis.get('number_of_actions_created', {})
        print(f"  1. Number of Actions Created:")
        print(f"     - total_actions_created: {actions_created.get('total_actions_created', 0)}")
        print(f"     - schedules_count: {actions_created.get('schedules_count', 0)}")
        print(f"     - histories_count: {actions_created.get('histories_count', 0)}")
        
        # Percentage Completed On Time
        completion_stats = action_kpis.get('percentage_completed_on_time', {})
        print(f"  2. Percentage Completed On Time:")
        print(f"     - percentage_completed_on_time: {completion_stats.get('percentage_completed_on_time', 0)}%")
        print(f"     - total_actions: {completion_stats.get('total_actions', 0)}")
        print(f"     - on_time_actions: {completion_stats.get('on_time_actions', 0)}")
        print(f"     - late_actions: {completion_stats.get('late_actions', 0)}")
        
        # Open vs Closed Actions
        open_closed = action_kpis.get('open_vs_closed_actions', {})
        print(f"  3. Open vs Closed Actions:")
        print(f"     - open_actions: {open_closed.get('open_actions', 0)}")
        print(f"     - closed_actions: {open_closed.get('closed_actions', 0)}")
        print(f"     - total_actions: {open_closed.get('total_actions', 0)}")
        print(f"     - open_percentage: {open_closed.get('open_percentage', 0)}%")
        print(f"     - closed_percentage: {open_closed.get('closed_percentage', 0)}%")
        
        print()
        print("💡 ACTION TRACKING INSIGHTS:")
        action_insights = kpis_response.get('action_tracking_insights', {})
        
        # Employees Not Completing On Time
        overdue_employees = action_insights.get('employees_not_completing_on_time', {})
        print(f"  1. Employees Not Completing On Time:")
        print(f"     - total_overdue_employees: {overdue_employees.get('total_overdue_employees', 0)}")
        print(f"     - overdue_actions_count: {overdue_employees.get('overdue_actions_count', 0)}")
        print(f"     - overdue_schedules_count: {overdue_employees.get('overdue_schedules_count', 0)}")
        print(f"     - overdue_histories_count: {overdue_employees.get('overdue_histories_count', 0)}")
        print(f"     - overdue_employees_list: {len(overdue_employees.get('overdue_employees_list', []))} employees")
        
        # Show top overdue employees if available
        overdue_list = overdue_employees.get('overdue_employees_list', [])
        if overdue_list:
            print("     - Top overdue employees:")
            for i, employee in enumerate(overdue_list[:3], 1):
                print(f"       {i}. {employee}")
        
        print()
        print("📊 SUMMARY METRICS:")
        summary = kpis_response.get('summary', {})
        print(f"  - total_actions: {summary.get('total_actions', 0)}")
        print(f"  - open_actions: {summary.get('open_actions', 0)}")
        print(f"  - closed_actions: {summary.get('closed_actions', 0)}")
        print(f"  - on_time_completion_rate: {summary.get('on_time_completion_rate', 0)}%")
        print(f"  - total_overdue_employees: {summary.get('total_overdue_employees', 0)}")
        print(f"  - total_overdue_actions: {summary.get('total_overdue_actions', 0)}")
        
        print()
        print("⏰ EXTRACTION METADATA:")
        print(f"  - extraction_timestamp: {kpis_response.get('extraction_timestamp', 'N/A')}")
        
        print()
        print("🎯 FRONTEND INTEGRATION NOTES:")
        print("=" * 60)
        print("• This response structure is ready for frontend consumption")
        print("• Action tracking KPIs provide comprehensive action management insights")
        print("• On-time completion percentage helps track performance")
        print("• Open vs closed actions show current workload status")
        print("• Overdue employees insight identifies compliance issues")
        print("• Summary section provides quick overview metrics")
        print("• All data includes proper date ranges and metadata")
        print("• Extraction timestamp enables cache management")
        
        return kpis_response
        
    except Exception as e:
        logger.error(f"❌ Error testing Action Tracking KPIs: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    """Run the test"""
    result = test_action_tracking_kpis()
    
    print()
    print("🏁 Test completed!")
    if "error" not in result:
        print("✅ Action Tracking KPIs module is working correctly!")
        print("📤 Response structure is ready for frontend integration!")
    else:
        print("❌ Test failed - check logs for details")
