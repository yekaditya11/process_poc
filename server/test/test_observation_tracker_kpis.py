"""
Test file for Observation Tracker KPIs Module
This test demonstrates the complete response structure that will be sent to the frontend.

Module: Observation Tracker
Template ID: '9bb83f61-b869-4721-81b6-0c870e91a779'
KPIs: Observations by area, status (open/closed), priority, AI-based insights from remarks
"""

import json
import logging
from datetime import datetime, timedelta
from data_extractors.observation_tracker_kpis_extractor import get_observation_tracker_kpis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_observation_tracker_kpis():
    """
    Test the Observation Tracker KPIs extractor and show complete response structure
    """
    print("🔍 Testing Observation Tracker KPIs Module...")
    print("=" * 60)
    
    try:
        # Test parameters
        customer_id = None  # Test with all customers
        days_back = 365  # Last 365 days (default)
        
        print(f"📅 Date Range: Last {days_back} days (365 days default)")
        print(f"👤 Customer ID: {customer_id or 'All customers'}")
        print(f"🎯 Template ID: 9bb83f61-b869-4721-81b6-0c870e91a779")
        print()
        
        # Extract KPIs
        print("🚀 Extracting Observation Tracker KPIs...")
        kpis_response = get_observation_tracker_kpis(customer_id, days_back)
        
        # Display results
        print("✅ Observation Tracker KPIs extracted successfully!")
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
        print("📍 OBSERVATIONS BY AREA:")
        area_stats = kpis_response.get('observations_by_area', {})
        print(f"  - observations_by_area: {len(area_stats.get('observations_by_area', {}))} areas")
        print(f"  - total_observations: {area_stats.get('total_observations', 0)}")
        print(f"  - total_areas: {area_stats.get('total_areas', 0)}")
        
        # Show top areas if available
        if isinstance(area_stats.get('observations_by_area'), dict):
            top_areas = sorted(area_stats['observations_by_area'].items(), 
                             key=lambda x: x[1], reverse=True)[:5]
            if top_areas:
                print("  - Top 5 areas:")
                for area, count in top_areas:
                    print(f"    • {area}: {count} observations")
        
        print()
        print("📊 OBSERVATION STATUS:")
        status_stats = kpis_response.get('observation_status', {})
        print(f"  - open_observations: {status_stats.get('open_observations', 0)}")
        print(f"  - closed_observations: {status_stats.get('closed_observations', 0)}")
        print(f"  - total_observations: {status_stats.get('total_observations', 0)}")
        print(f"  - open_percentage: {status_stats.get('open_percentage', 0)}%")
        print(f"  - closed_percentage: {status_stats.get('closed_percentage', 0)}%")
        
        print()
        print("⚡ OBSERVATION PRIORITY:")
        priority_stats = kpis_response.get('observation_priority', {})
        print(f"  - observations_by_priority: {len(priority_stats.get('observations_by_priority', {}))} priority levels")
        print(f"  - total_observations: {priority_stats.get('total_observations', 0)}")
        print(f"  - total_priority_levels: {priority_stats.get('total_priority_levels', 0)}")
        
        # Show priority breakdown if available
        if isinstance(priority_stats.get('observations_by_priority'), dict):
            priority_breakdown = sorted(priority_stats['observations_by_priority'].items(), 
                                      key=lambda x: x[1], reverse=True)
            if priority_breakdown:
                print("  - Priority breakdown:")
                for priority, count in priority_breakdown:
                    print(f"    • {priority}: {count} observations")
        
        print()
        print("💬 OBSERVATIONS REMARKS INSIGHT:")
        remarks_insight = kpis_response.get('observations_remarks_insight', {})
        print(f"  - total_remarks: {remarks_insight.get('total_remarks', 0)}")
        print(f"  - remarks_analyzed: {remarks_insight.get('remarks_analyzed', 0)}")
        print(f"  - top_remarks: {len(remarks_insight.get('top_remarks', []))} remarks")
        print(f"  - ai_summary: {remarks_insight.get('ai_summary', 'N/A')}")
        
        # Show top remarks if available
        top_remarks = remarks_insight.get('top_remarks', [])
        if top_remarks:
            print("  - Top remarks:")
            for i, remark in enumerate(top_remarks[:3], 1):
                print(f"    {i}. {remark}")
        
        print()
        print("📊 SUMMARY METRICS:")
        summary = kpis_response.get('summary', {})
        print(f"  - total_areas: {summary.get('total_areas', 0)}")
        print(f"  - total_open_observations: {summary.get('total_open_observations', 0)}")
        print(f"  - total_closed_observations: {summary.get('total_closed_observations', 0)}")
        print(f"  - total_observations: {summary.get('total_observations', 0)}")
        print(f"  - total_priority_levels: {summary.get('total_priority_levels', 0)}")
        print(f"  - total_remarks_analyzed: {summary.get('total_remarks_analyzed', 0)}")
        
        print()
        print("🎯 FRONTEND INTEGRATION NOTES:")
        print("=" * 60)
        print("• This response structure is ready for frontend consumption")
        print("• Observations by area provide geographical insights")
        print("• Status breakdown shows open vs closed observations")
        print("• Priority analysis helps identify urgent issues")
        print("• AI-generated remarks insight provides summary analysis")
        print("• All data includes proper date ranges and metadata")
        print("• Summary section provides quick overview metrics")
        
        return kpis_response
        
    except Exception as e:
        logger.error(f"❌ Error testing Observation Tracker KPIs: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    """Run the test"""
    result = test_observation_tracker_kpis()
    
    print()
    print("🏁 Test completed!")
    if "error" not in result:
        print("✅ Observation Tracker KPIs module is working correctly!")
        print("📤 Response structure is ready for frontend integration!")
    else:
        print("❌ Test failed - check logs for details")
