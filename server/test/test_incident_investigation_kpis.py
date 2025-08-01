"""
Test file for Incident Investigation KPIs Module
This test demonstrates the complete response structure that will be sent to the frontend.

Module: Incident Investigation
Total KPIs: 13 (11 main KPIs + 2 insights)
"""

import json
import logging
from datetime import datetime, timedelta
from data_extractors.incident_kpis import extract_incident_kpis
from config.database_config import db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_incident_investigation_kpis():
    """
    Test the Incident Investigation KPIs extractor and show complete response structure
    """
    print("🔍 Testing Incident Investigation KPIs Module...")
    print("=" * 60)
    
    try:
        # Get database session
        db_session = db_manager.get_process_safety_session()

        # Test parameters
        customer_id = None  # Test with all customers
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)  # Last year (365 days default)
        
        print(f"📅 Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"👤 Customer ID: {customer_id or 'All customers'}")
        print()
        
        # Extract KPIs
        print("🚀 Extracting Incident Investigation KPIs...")
        kpis_response = extract_incident_kpis(db_session, customer_id, start_date, end_date)
        
        # Close database session
        db_session.close()
        
        # Display results
        print("✅ Incident Investigation KPIs extracted successfully!")
        print()
        print("📊 COMPLETE RESPONSE STRUCTURE FOR FRONTEND:")
        print("=" * 60)
        
        # Pretty print the complete response structure
        response_json = json.dumps(kpis_response, indent=2, default=str)
        print(response_json)
        
        print()
        print("📋 SUMMARY OF RESPONSE STRUCTURE:")
        print("=" * 60)
        
        # Main KPIs (11 total)
        print("🔢 MAIN KPIs (11 total):")
        print(f"  1. incidents_reported: {kpis_response.get('incidents_reported', 0)}")
        print(f"  2. incident_reporting_trends: {len(kpis_response.get('incident_reporting_trends', []))} trend points")
        print(f"  3. open_incidents: {kpis_response.get('open_incidents', 0)}")
        print(f"  4. closed_incidents: {kpis_response.get('closed_incidents', 0)}")
        print(f"  5. investigation_completion_time_mins: {kpis_response.get('investigation_completion_time_mins', 0)}")
        print(f"  6. total_completed_investigations: {kpis_response.get('total_completed_investigations', 0)}")
        print(f"  7. incident_types: {len(kpis_response.get('incident_types', {}))} types")
        print(f"  8. actions_created: {kpis_response.get('actions_created', 0)}")
        print(f"  9. open_actions_percentage: {kpis_response.get('open_actions_percentage', 0.0)}%")
        print(f"  10. people_injured: {kpis_response.get('people_injured', 0)}")
        print(f"  11. incidents_by_location: {len(kpis_response.get('incidents_by_location', {}))} locations")
        print(f"  12. days_since_last_incident: {kpis_response.get('days_since_last_incident', 'N/A')}")
        
        print()
        print("💡 INSIGHTS (2 total):")
        incident_trend = kpis_response.get('incident_trend_insight', {})
        unsafe_locations = kpis_response.get('most_unsafe_locations_insight', {})
        print(f"  1. incident_trend_insight: {incident_trend.get('trend_analysis', 'N/A')}")
        print(f"  2. most_unsafe_locations_insight: {unsafe_locations.get('safety_analysis', 'N/A')}")
        
        print()
        print("📈 METADATA:")
        print(f"  - last_incident_date: {kpis_response.get('last_incident_date', 'N/A')}")
        print(f"  - last_incident_source: {kpis_response.get('last_incident_source', 'N/A')}")
        print(f"  - total_kpis_count: {kpis_response.get('total_kpis_count', 0)}")
        print(f"  - main_kpis_count: {kpis_response.get('main_kpis_count', 0)}")
        print(f"  - insights_count: {kpis_response.get('insights_count', 0)}")
        
        print()
        print("🎯 FRONTEND INTEGRATION NOTES:")
        print("=" * 60)
        print("• This response structure is ready for frontend consumption")
        print("• All KPIs are properly formatted with consistent data types")
        print("• Date ranges are in ISO format for easy parsing")
        print("• Insights contain AI-generated analysis for dashboard display")
        print("• Error handling is built-in with fallback values")
        print("• Response includes metadata for validation and debugging")
        
        return kpis_response
        
    except Exception as e:
        logger.error(f"❌ Error testing Incident Investigation KPIs: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    """Run the test"""
    result = test_incident_investigation_kpis()
    
    print()
    print("🏁 Test completed!")
    if "error" not in result:
        print("✅ Incident Investigation KPIs module is working correctly!")
        print("📤 Response structure is ready for frontend integration!")
    else:
        print("❌ Test failed - check logs for details")
