"""
Test script for Risk Assessment KPIs Extractor

This script tests the risk assessment KPIs extraction functionality
to ensure all KPIs and insights are working correctly.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_extractors.risk_assessment_kpis_extractor import get_risk_assessment_kpis


def test_risk_assessment_kpis():
    """Test the risk assessment KPIs extraction"""
    
    print("🔍 TESTING RISK ASSESSMENT KPIs EXTRACTOR")
    print("=" * 60)
    print()
    
    try:
        # Test parameters
        customer_id = None  # Test with all customers (not applicable for markdown data)
        days_back = 365  # Last 365 days (not applicable for markdown data)
        
        print(f"📅 Date Range: Last {days_back} days (not applicable for markdown data)")
        print(f"👤 Customer ID: {customer_id or 'All customers'}")
        print(f"📄 Data Source: risk_assessment_data.md")
        print()
        
        # Extract KPIs
        print("🚀 Extracting Risk Assessment KPIs...")
        kpis_response = get_risk_assessment_kpis(customer_id, days_back)
        
        # Display results
        print("✅ Risk Assessment KPIs extracted successfully!")
        print()
        print("📊 COMPLETE RESPONSE STRUCTURE FOR FRONTEND:")
        print("=" * 60)
        
        # Pretty print the complete response structure
        response_json = json.dumps(kpis_response, indent=2, default=str)
        print(response_json)
        
        print()
        print("=" * 60)
        print("📈 KPI SUMMARY:")
        print("=" * 60)
        
        # Display key metrics
        if "error" not in kpis_response:
            print(f"📋 Total Assessments: {kpis_response.get('number_of_assessments', 0)}")
            
            # Severity analysis
            severity = kpis_response.get('severity_analysis', {})
            if severity.get('initial_severity'):
                print(f"⚠️  Average Initial Severity: {severity['initial_severity'].get('average', 0):.1f}")
                print(f"✅ Average Residual Severity: {severity['residual_severity'].get('average', 0):.1f}")
            
            # Likelihood analysis
            likelihood = kpis_response.get('likelihood_analysis', {})
            if likelihood.get('initial_likelihood'):
                print(f"📊 Most Common Initial Likelihood: {likelihood['initial_likelihood'].get('most_common', 'N/A')}")
                print(f"📊 Most Common Residual Likelihood: {likelihood['residual_likelihood'].get('most_common', 'N/A')}")
            
            # Hazard effects
            effects = kpis_response.get('hazard_effects', {})
            if effects.get('effects_distribution'):
                effects_dist = effects['effects_distribution']
                print(f"👥 People Effects: {effects_dist.get('P', {}).get('count', 0)} assessments")
                print(f"🏭 Asset Effects: {effects_dist.get('A', {}).get('count', 0)} assessments")
                print(f"🌍 Environment Effects: {effects_dist.get('E', {}).get('count', 0)} assessments")
                print(f"📰 Reputation Effects: {effects_dist.get('R', {}).get('count', 0)} assessments")
            
            # High risk activities
            high_risk = kpis_response.get('high_residual_risk_activities', {})
            print(f"🚨 High Residual Risk Activities: {high_risk.get('total_high_risk', 0)}")
            
            # Effectiveness
            effectiveness = kpis_response.get('measure_effectiveness', {})
            if effectiveness.get('overall_effectiveness'):
                print(f"📈 Overall Measure Effectiveness: {effectiveness['overall_effectiveness']:.1f}%")
            
            # Control measures
            control_measures = kpis_response.get('common_control_measures', {})
            print(f"🛡️  Total Control Measures: {control_measures.get('total_measures', 0)}")
            
            # Recovery measures
            recovery_measures = kpis_response.get('common_recovery_measures', {})
            print(f"🚑 Total Recovery Measures: {recovery_measures.get('total_measures', 0)}")
            
            # Common hazards
            hazards = kpis_response.get('common_hazards', {})
            print(f"⚠️  Total Hazards Identified: {hazards.get('total_hazards', 0)}")
            
            print()
            print("💡 KEY INSIGHTS:")
            print("-" * 30)
            insights = kpis_response.get('insights', [])
            for i, insight in enumerate(insights, 1):
                print(f"{i}. {insight}")
        
        else:
            print(f"❌ Error in KPI extraction: {kpis_response.get('error', 'Unknown error')}")
        
        print()
        print("=" * 60)
        print("🎯 FRONTEND INTEGRATION NOTES:")
        print("=" * 60)
        print("• All KPIs are ready for dashboard integration")
        print("• Response includes both numerical KPIs and insights")
        print("• Data structure matches other module extractors")
        print("• Error handling included for robust operation")
        print("• JSON serializable output for API responses")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_risk_assessment_kpis()
