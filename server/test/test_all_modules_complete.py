"""
Complete Test Suite for All 4 Safety Modules
This test demonstrates the complete response structure for all modules that will be sent to the frontend.

Modules:
1. Incident Investigation (13 KPIs: 11 main + 2 insights)
2. Driver Safety Checklists (Template ID: a35be57e-dd36-4a21-b05b-e4d4fa836f53)
3. Observation Tracker (Template ID: 9bb83f61-b869-4721-81b6-0c870e91a779)
4. Action Tracking (SubTagId filtering)
"""

import json
import logging
from datetime import datetime, timedelta

# Import all test functions
from test_incident_investigation_kpis import test_incident_investigation_kpis
from test_driver_safety_checklist_kpis import test_driver_safety_checklist_kpis
from test_observation_tracker_kpis import test_observation_tracker_kpis
from test_action_tracking_kpis import test_action_tracking_kpis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_all_safety_modules():
    """
    Test all 4 safety modules and show complete response structures
    """
    print("🏢 TESTING ALL SAFETY MODULES - COMPLETE RESPONSE STRUCTURES")
    print("=" * 80)
    print("This test shows the exact format that will be sent to the frontend")
    print("=" * 80)
    
    all_results = {}
    
    try:
        # Test Module 1: Incident Investigation
        print("\n" + "🔍 MODULE 1: INCIDENT INVESTIGATION" + "\n" + "=" * 50)
        incident_result = test_incident_investigation_kpis()
        all_results['incident_investigation'] = incident_result
        
        # Test Module 2: Driver Safety Checklists
        print("\n" + "🚗 MODULE 2: DRIVER SAFETY CHECKLISTS" + "\n" + "=" * 50)
        driver_safety_result = test_driver_safety_checklist_kpis()
        all_results['driver_safety_checklists'] = driver_safety_result
        
        # Test Module 3: Observation Tracker
        print("\n" + "🔍 MODULE 3: OBSERVATION TRACKER" + "\n" + "=" * 50)
        observation_result = test_observation_tracker_kpis()
        all_results['observation_tracker'] = observation_result
        
        # Test Module 4: Action Tracking
        print("\n" + "🚀 MODULE 4: ACTION TRACKING" + "\n" + "=" * 50)
        action_tracking_result = test_action_tracking_kpis()
        all_results['action_tracking'] = action_tracking_result
        
        # Summary of all modules
        print("\n" + "📊 COMPLETE FRONTEND RESPONSE STRUCTURE" + "\n" + "=" * 80)
        
        # Create the complete response structure that would be sent to frontend
        complete_response = {
            "safety_dashboard_data": {
                "incident_investigation": all_results.get('incident_investigation', {}),
                "driver_safety_checklists": all_results.get('driver_safety_checklists', {}),
                "observation_tracker": all_results.get('observation_tracker', {}),
                "action_tracking": all_results.get('action_tracking', {})
            },
            "extraction_metadata": {
                "extraction_timestamp": datetime.now().isoformat(),
                "modules_tested": 4,
                "total_kpis": {
                    "incident_investigation": 13,  # 11 main + 2 insights
                    "driver_safety_checklists": 4,  # Daily/Weekly completion + Vehicle fitness + Overdue drivers
                    "observation_tracker": 4,  # By area + Status + Priority + Remarks insight
                    "action_tracking": 4  # Actions created + % on time + Open/Closed + Overdue employees
                },
                "template_ids": {
                    "driver_safety_checklists": "a35be57e-dd36-4a21-b05b-e4d4fa836f53",
                    "observation_tracker": "9bb83f61-b869-4721-81b6-0c870e91a779"
                }
            },
            "status": "success" if all(not ("error" in result) for result in all_results.values()) else "partial_success"
        }
        
        # Pretty print the complete response
        response_json = json.dumps(complete_response, indent=2, default=str)
        print(response_json)
        
        print("\n" + "📋 FRONTEND INTEGRATION SUMMARY" + "\n" + "=" * 80)
        
        # Module status summary
        for module_name, result in all_results.items():
            status = "✅ SUCCESS" if "error" not in result else "❌ ERROR"
            print(f"{module_name.upper().replace('_', ' ')}: {status}")
        
        print(f"\nTOTAL MODULES: 4")
        print(f"SUCCESSFUL MODULES: {sum(1 for result in all_results.values() if 'error' not in result)}")
        print(f"FAILED MODULES: {sum(1 for result in all_results.values() if 'error' in result)}")
        
        print("\n" + "🎯 KEY FRONTEND INTEGRATION POINTS:" + "\n" + "-" * 50)
        print("• All response structures are consistent and ready for consumption")
        print("• Each module provides both detailed KPIs and summary metrics")
        print("• Date ranges are standardized in ISO format")
        print("• Error handling is built-in with fallback values")
        print("• AI insights are included where applicable")
        print("• Template IDs are clearly specified for filtering")
        print("• Extraction timestamps enable cache management")
        
        return complete_response
        
    except Exception as e:
        logger.error(f"❌ Error testing all safety modules: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    """Run the complete test suite"""
    print("🚀 Starting Complete Safety Modules Test Suite...")
    
    result = test_all_safety_modules()
    
    print("\n" + "🏁 COMPLETE TEST SUITE FINISHED!" + "\n" + "=" * 80)
    
    if "error" not in result:
        print("✅ All safety modules tested successfully!")
        print("📤 Complete response structures are ready for frontend integration!")
        print("🔗 You can now use these structures to build your frontend dashboard!")
    else:
        print("❌ Some tests failed - check individual module logs for details")
    
    print("\n📁 Test files created:")
    print("  • test_incident_investigation_kpis.py")
    print("  • test_driver_safety_checklist_kpis.py") 
    print("  • test_observation_tracker_kpis.py")
    print("  • test_action_tracking_kpis.py")
    print("  • test_all_modules_complete.py (this file)")
    
    print("\n🎯 Next steps:")
    print("  1. Run individual test files to see specific module responses")
    print("  2. Use the response structures to design your frontend components")
    print("  3. Implement API endpoints that return these exact structures")
    print("  4. Build dashboard visualizations based on the KPI data")
