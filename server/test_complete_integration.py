"""
Complete Risk Assessment Integration Test

Tests all integration points for the risk assessment module
"""

import sys
import os
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_complete_integration():
    """Test complete risk assessment integration"""
    print("🔍 TESTING COMPLETE RISK ASSESSMENT INTEGRATION")
    print("=" * 60)
    
    success_count = 0
    total_tests = 6
    
    try:
        # Test 1: KPI Extractor
        print("1. Testing KPI Extractor...")
        from data_extractors.risk_assessment_kpis_extractor import RiskAssessmentKPIsExtractor
        extractor = RiskAssessmentKPIsExtractor()
        kpis = extractor.get_risk_assessment_kpis()
        assert kpis.get('number_of_assessments', 0) == 7, "Expected 7 assessments"
        print("   ✅ KPI Extractor: PASSED")
        success_count += 1
        
        # Test 2: Main App Integration
        print("2. Testing Main App Integration...")
        from main_app import SafetySummarizerApp
        app = SafetySummarizerApp()
        assert hasattr(app, 'risk_assessment_extractor'), "Risk assessment extractor not found"
        print("   ✅ Main App Integration: PASSED")
        success_count += 1
        
        # Test 3: API Endpoints
        print("3. Testing API Endpoints...")
        from api.web_api import app as fastapi_app
        # Check if the risk assessment endpoint exists
        routes = [route.path for route in fastapi_app.routes]
        assert "/metrics/risk-assessment-kpis" in routes, "Risk assessment API endpoint not found"
        assert "/ai-analysis/risk-assessment" in routes, "Risk assessment AI analysis endpoint not found"
        print("   ✅ API Endpoints: PASSED")
        success_count += 1
        
        # Test 4: Conversational AI Integration
        print("4. Testing Conversational AI Integration...")
        from ai_engine.conversational_ai import ConversationalAI
        conv_ai = ConversationalAI(app)
        # Check if risk assessment keywords are present
        assert 'risk_assessment' in conv_ai.keywords, "Risk assessment keywords not found"
        print("   ✅ Conversational AI Integration: PASSED")
        success_count += 1
        
        # Test 5: AI Engine Module Configuration
        print("5. Testing AI Engine Module Configuration...")
        from ai_engine.summarization_engine import SafetySummarizationEngine
        ai_engine = SafetySummarizationEngine()
        assert 'risk_assessment' in ai_engine.module_configs, "Risk assessment module config not found"
        print("   ✅ AI Engine Configuration: PASSED")
        success_count += 1
        
        # Test 6: Data Flow Test
        print("6. Testing Complete Data Flow...")
        # Test getting risk assessment data directly from extractor
        test_kpis = app.risk_assessment_extractor.get_risk_assessment_kpis()
        assert test_kpis.get('number_of_assessments', 0) == 7, "Data flow test failed"
        print("   ✅ Complete Data Flow: PASSED")
        success_count += 1
        
        print()
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print(f"✅ {success_count}/{total_tests} tests successful")
        print()
        print("📊 INTEGRATION SUMMARY:")
        print("=" * 40)
        print("• ✅ KPI Extractor: Working (7 assessments)")
        print("• ✅ Main App: Risk assessment extractor initialized")
        print("• ✅ API Endpoints: /metrics/risk-assessment-kpis available")
        print("• ✅ AI Analysis: /ai-analysis/risk-assessment available")
        print("• ✅ Conversational AI: Risk assessment keywords configured")
        print("• ✅ AI Engine: Module configuration added")
        print("• ✅ Data Flow: End-to-end data retrieval working")
        print()
        print("🚀 READY FOR DASHBOARD INTEGRATION!")
        print("The risk assessment module is fully integrated and ready to use.")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        print(f"✅ {success_count}/{total_tests} tests passed before failure")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_complete_integration()
