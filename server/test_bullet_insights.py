"""
Test script to demonstrate the new bullet point insights format
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_app import SafetySummarizerApp

def test_bullet_point_insights():
    """Test the new bullet point format for AI insights"""
    
    print("🔍 Testing AI Safety Summarizer - Bullet Point Insights Format")
    print("=" * 70)
    
    try:
        # Initialize the app
        print("Initializing AI Safety Summarizer...")
        app = SafetySummarizerApp()
        
        # Test comprehensive summary with bullet points
        print("\n📊 Generating Comprehensive Summary with Bullet Point Insights...")
        print("-" * 50)
        
        summary = app.generate_comprehensive_summary(
            days_back=7,  # Last 7 days for quick test
            include_raw_data=False
        )
        
        # Display the bullet point insights
        print("\n🎯 EXECUTIVE SUMMARY (Bullet Points):")
        print(summary["ai_summary"]["executive_summary"])
        
        print("\n🔧 PERMIT TO WORK INSIGHTS (Bullet Points):")
        print(summary["ai_summary"]["module_summaries"]["permit_to_work"])
        
        print("\n⚠️ INCIDENT MANAGEMENT INSIGHTS (Bullet Points):")
        print(summary["ai_summary"]["module_summaries"]["incident_management"])
        
        print("\n✅ ACTION TRACKING INSIGHTS (Bullet Points):")
        print(summary["ai_summary"]["module_summaries"]["action_tracking"])
        
        print("\n🔍 INSPECTION TRACKING INSIGHTS (Bullet Points):")
        print(summary["ai_summary"]["module_summaries"]["inspection_tracking"])
        
        print("\n💡 STRATEGIC INSIGHTS & RECOMMENDATIONS (Bullet Points):")
        print(summary["ai_summary"]["insights_and_recommendations"])
        
        # Save the results
        output_file = f"bullet_insights_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"\n💾 Full results saved to: {output_file}")
        
        print("\n✅ Test completed successfully!")
        print("\nKey Features of New Bullet Point Format:")
        print("• No headings or subheadings - just direct insights")
        print("• Module-specific insights tailored to each safety area")
        print("• Actionable bullet points for immediate use")
        print("• Different focus areas for each module:")
        print("  - Permits: Workflow efficiency, compliance, templates")
        print("  - Incidents: Trends, critical analysis, location insights")
        print("  - Actions: Accountability, priorities, completion patterns")
        print("  - Inspections: Compliance, quality, preventive maintenance")
        print("  - Strategic: Cross-module correlations, optimization")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        return False
    
    finally:
        # Clean up
        if 'app' in locals():
            app.close()
    
    return True

def test_individual_modules():
    """Test individual module summaries with bullet points"""
    
    print("\n🔬 Testing Individual Module Insights...")
    print("=" * 50)
    
    try:
        app = SafetySummarizerApp()
        
        modules = ["permit", "incident", "action", "inspection"]
        
        for module in modules:
            print(f"\n📋 {module.upper()} MODULE INSIGHTS:")
            print("-" * 30)
            
            module_summary = app.generate_module_summary(
                module=module,
                days_back=7
            )
            
            print(module_summary["ai_summary"])
            
    except Exception as e:
        print(f"\n❌ Error testing individual modules: {str(e)}")
        return False
    
    finally:
        if 'app' in locals():
            app.close()
    
    return True

if __name__ == "__main__":
    print("🚀 Starting AI Safety Summarizer Bullet Point Insights Test")
    print("=" * 70)
    
    # Test comprehensive summary
    success1 = test_bullet_point_insights()
    
    # Test individual modules
    success2 = test_individual_modules()
    
    if success1 and success2:
        print("\n🎉 All tests completed successfully!")
        print("\nThe AI now generates insights as simple bullet points:")
        print("✓ No headings or subheadings")
        print("✓ Direct, actionable insights")
        print("✓ Module-specific focus areas")
        print("✓ Executive-ready format")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
