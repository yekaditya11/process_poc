"""
Setup Test Script
Tests database connections and basic functionality
"""

import os
import sys
from datetime import datetime
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from config.database_config import db_manager
        print("✅ Database config imported successfully")
        
        from data_extractors.permit_to_work_extractor import PermitToWorkExtractor
        from data_extractors.incident_management_extractor import IncidentManagementExtractor
        from data_extractors.action_tracking_extractor import ActionTrackingExtractor
        from data_extractors.inspection_tracking_extractor import InspectionTrackingExtractor
        print("✅ Data extractors imported successfully")
        
        from ai_engine.summarization_engine import SafetySummarizationEngine
        print("✅ AI engine imported successfully")
        
        from main_app import SafetySummarizerApp
        print("✅ Main app imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during imports: {str(e)}")
        return False

def test_environment_variables():
    """Test if required environment variables are set"""
    print("\n🔍 Testing environment variables...")
    
    required_vars = [
        "PROCESS_SAFETY_DB_HOST",
        "PROCESS_SAFETY_DB_NAME",
        "PROCESS_SAFETY_DB_USER",
        "SAFETY_CONNECT_DB_HOST",
        "SAFETY_CONNECT_DB_NAME",
        "SAFETY_CONNECT_DB_USER"
    ]
    
    optional_vars = [
        "OPENAI_API_KEY"
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var} is set")
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing_required:
        print(f"❌ Missing required environment variables: {missing_required}")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing optional environment variables: {missing_optional}")
        print("   (These are needed for AI summarization)")
    
    return True

def test_database_connections():
    """Test database connections"""
    print("\n🔍 Testing database connections...")
    
    try:
        from config.database_config import db_manager
        
        # Test ProcessSafety database connection
        try:
            ps_engine = db_manager.process_safety_engine
            with ps_engine.connect() as conn:
                result = conn.execute("SELECT 1")
                result.fetchone()
            print("✅ ProcessSafety database connection successful")
        except Exception as e:
            print(f"❌ ProcessSafety database connection failed: {str(e)}")
            return False
        
        # Test SafetyConnect database connection
        try:
            sc_engine = db_manager.safety_connect_engine
            with sc_engine.connect() as conn:
                result = conn.execute("SELECT 1")
                result.fetchone()
            print("✅ SafetyConnect database connection successful")
        except Exception as e:
            print(f"❌ SafetyConnect database connection failed: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {str(e)}")
        return False

def test_data_extraction():
    """Test basic data extraction"""
    print("\n🔍 Testing data extraction...")
    
    try:
        from data_extractors.permit_to_work_extractor import PermitToWorkExtractor
        from data_extractors.incident_management_extractor import IncidentManagementExtractor
        
        # Test permit data extraction
        try:
            permit_extractor = PermitToWorkExtractor()
            permit_data = permit_extractor.get_permit_summary_data(None, 7)
            print(f"✅ Permit data extracted: {permit_data['permit_statistics']['total_permits']} permits found")
        except Exception as e:
            print(f"❌ Permit data extraction failed: {str(e)}")
            return False
        
        # Test incident data extraction
        try:
            incident_extractor = IncidentManagementExtractor()
            incident_data = incident_extractor.get_incident_summary_data(None, 7)
            print(f"✅ Incident data extracted: {incident_data['incident_statistics']['total_incidents']} incidents found")
        except Exception as e:
            print(f"❌ Incident data extraction failed: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Data extraction test failed: {str(e)}")
        return False

def test_ai_engine():
    """Test AI engine initialization"""
    print("\n🔍 Testing AI engine...")
    
    try:
        from ai_engine.summarization_engine import SafetySummarizationEngine
        
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  Skipping AI engine test - OPENAI_API_KEY not set")
            return True
        
        try:
            ai_engine = SafetySummarizationEngine()
            print("✅ AI engine initialized successfully")
            return True
        except Exception as e:
            print(f"❌ AI engine initialization failed: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ AI engine test failed: {str(e)}")
        return False

def test_main_app():
    """Test main application initialization"""
    print("\n🔍 Testing main application...")
    
    try:
        from main_app import SafetySummarizerApp
        
        app = SafetySummarizerApp()
        print("✅ Main application initialized successfully")
        
        # Test dashboard data generation
        try:
            dashboard_data = app.get_quick_dashboard_data()
            print("✅ Dashboard data generation successful")
            print(f"   Found {dashboard_data['permit_metrics']['total_permits']} permits")
            print(f"   Found {dashboard_data['incident_metrics']['total_incidents']} incidents")
        except Exception as e:
            print(f"❌ Dashboard data generation failed: {str(e)}")
            return False
        finally:
            app.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Main application test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 AI Safety Summarizer - Setup Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Environment Variables", test_environment_variables),
        ("Database Connections", test_database_connections),
        ("Data Extraction", test_data_extraction),
        ("AI Engine", test_ai_engine),
        ("Main Application", test_main_app)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        print("\n💡 Common solutions:")
        print("   1. Make sure .env file is properly configured")
        print("   2. Verify database connections and credentials")
        print("   3. Check if required Python packages are installed")
        print("   4. Ensure OpenAI API key is valid (for AI features)")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
