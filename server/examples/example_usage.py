"""
Example Usage of AI Safety Summarizer
Demonstrates how to use the AI Safety Summarizer programmatically
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_app import SafetySummarizerApp
from utils.data_validator import DataValidator

def example_comprehensive_summary():
    """Example: Generate comprehensive summary"""
    print("=== Comprehensive Summary Example ===")
    
    # Initialize the app
    app = SafetySummarizerApp()
    
    try:
        # Generate comprehensive summary for last 30 days
        summary = app.generate_comprehensive_summary(
            customer_id=None,  # All customers
            days_back=30,
            include_raw_data=False
        )
        
        print("✅ Comprehensive summary generated successfully!")
        print(f"📊 Executive Summary Preview:")
        print(summary["ai_summary"]["executive_summary"][:200] + "...")
        
        # Save to file
        with open("comprehensive_summary_example.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        print("💾 Summary saved to comprehensive_summary_example.json")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        app.close()

def example_module_summary():
    """Example: Generate module-specific summary"""
    print("\n=== Module Summary Example ===")
    
    app = SafetySummarizerApp()
    
    try:
        # Generate permit to work summary
        permit_summary = app.generate_module_summary(
            module="permit",
            customer_id=None,
            days_back=30
        )
        
        print("✅ Permit to Work summary generated!")
        print(f"📋 Summary Preview:")
        print(permit_summary["ai_summary"][:200] + "...")
        
        # Generate incident summary
        incident_summary = app.generate_module_summary(
            module="incident",
            customer_id=None,
            days_back=30
        )
        
        print("✅ Incident Management summary generated!")
        print(f"🚨 Summary Preview:")
        print(incident_summary["ai_summary"][:200] + "...")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        app.close()

def example_dashboard_data():
    """Example: Get dashboard data"""
    print("\n=== Dashboard Data Example ===")
    
    app = SafetySummarizerApp()
    
    try:
        # Get quick dashboard data
        dashboard = app.get_quick_dashboard_data(customer_id=None)
        
        print("✅ Dashboard data generated!")
        print("📈 Key Metrics:")
        print(f"   Permit Completion Rate: {dashboard['permit_metrics']['completion_rate']:.1f}%")
        print(f"   Total Incidents: {dashboard['incident_metrics']['total_incidents']}")
        print(f"   Action Completion Rate: {dashboard['action_metrics']['completion_rate']:.1f}%")
        print(f"   Inspection Completion Rate: {dashboard['inspection_metrics']['completion_rate']:.1f}%")
        
        # Save dashboard data
        with open("dashboard_example.json", "w") as f:
            json.dump(dashboard, f, indent=2, default=str)
        print("💾 Dashboard data saved to dashboard_example.json")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        app.close()

def example_data_validation():
    """Example: Validate data quality"""
    print("\n=== Data Validation Example ===")
    
    app = SafetySummarizerApp()
    validator = DataValidator()
    
    try:
        # Extract data from all modules
        permit_data = app.permit_extractor.get_permit_summary_data(None, 30)
        incident_data = app.incident_extractor.get_incident_summary_data(None, 30)
        action_data = app.action_extractor.get_action_summary_data(None, 30)
        inspection_data = app.inspection_extractor.get_inspection_summary_data(None, 30)
        
        # Combine all data
        all_data = {
            "permit_to_work": permit_data,
            "incident_management": incident_data,
            "action_tracking": action_data,
            "inspection_tracking": inspection_data
        }
        
        # Generate data quality report
        quality_report = validator.generate_data_quality_report(all_data)
        
        print("✅ Data quality report generated!")
        print(f"📊 Overall Quality Score: {quality_report['overall_quality_score']:.1f}/100")
        print(f"✅ Data Valid: {quality_report['overall_valid']}")
        
        print("\n📋 Module Completeness Scores:")
        for module, score in quality_report['module_completeness_scores'].items():
            print(f"   {module}: {score:.1f}%")
        
        if quality_report['validation_issues']:
            print("\n⚠️  Validation Issues:")
            for module, issues in quality_report['validation_issues'].items():
                print(f"   {module}: {issues}")
        
        print("\n💡 Recommendations:")
        for rec in quality_report['recommendations']:
            print(f"   • {rec}")
        
        # Save quality report
        with open("data_quality_report.json", "w") as f:
            json.dump(quality_report, f, indent=2, default=str)
        print("💾 Quality report saved to data_quality_report.json")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        app.close()

def example_custom_analysis():
    """Example: Custom analysis with specific parameters"""
    print("\n=== Custom Analysis Example ===")
    
    app = SafetySummarizerApp()
    
    try:
        # Custom analysis for specific customer and time period
        customer_id = "your-customer-uuid-here"  # Replace with actual customer ID
        
        print(f"🔍 Analyzing data for customer: {customer_id}")
        print(f"📅 Time period: Last 7 days")
        
        # Get data for last 7 days
        permit_data = app.permit_extractor.get_permit_summary_data(customer_id, 7)
        incident_data = app.incident_extractor.get_incident_summary_data(customer_id, 7)
        
        print("📊 Quick Analysis Results:")
        print(f"   Permits in last 7 days: {permit_data['permit_statistics']['total_permits']}")
        print(f"   Incidents in last 7 days: {incident_data['incident_statistics']['total_incidents']}")
        
        # Check for critical issues
        overdue_permits = permit_data['permit_statistics']['overdue_permits']
        injury_incidents = incident_data['incident_statistics']['injury_incidents']
        
        if overdue_permits > 0:
            print(f"⚠️  ALERT: {overdue_permits} overdue permits!")
        
        if injury_incidents > 0:
            print(f"🚨 CRITICAL: {injury_incidents} injury incidents!")
        
        if overdue_permits == 0 and injury_incidents == 0:
            print("✅ No critical issues found in the last 7 days")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        app.close()

def main():
    """Run all examples"""
    print("🤖 AI Safety Summarizer - Example Usage")
    print("=" * 50)
    
    # Check if environment is properly configured
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   Some examples may fail without proper API key configuration")
        print()
    
    try:
        # Run examples
        example_dashboard_data()
        example_module_summary()
        example_data_validation()
        example_custom_analysis()
        example_comprehensive_summary()  # This one uses OpenAI API
        
        print("\n🎉 All examples completed successfully!")
        print("📁 Check the generated files for detailed outputs")
        
    except Exception as e:
        print(f"\n❌ Example execution failed: {str(e)}")
        print("💡 Make sure your database connections and API keys are properly configured")

if __name__ == "__main__":
    main()
