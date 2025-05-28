"""
Simple Test Script - No Database Required
Tests the basic structure without database connections
"""

import json
from datetime import datetime, timedelta

def generate_mock_data():
    """Generate mock data for testing"""

    # Mock permit data
    permit_data = {
        "summary_period": {
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "days_covered": 30
        },
        "permit_statistics": {
            "total_permits": 150,
            "completed_permits": 142,
            "pending_permits": 5,
            "in_progress_permits": 3,
            "overdue_permits": 8,
            "completion_rate": 94.7,
            "avg_completion_days": 2.3
        },
        "status_breakdown": [
            {"status": "completed", "count": 142, "percentage": 94.7},
            {"status": "pending", "count": 5, "percentage": 3.3},
            {"status": "in_progress", "count": 3, "percentage": 2.0}
        ],
        "overdue_permits": [
            {
                "permit_id": "permit-001",
                "template_name": "Hot Work Permit",
                "status": "pending",
                "days_overdue": 5,
                "assigned_user": "John Smith",
                "company": "ABC Manufacturing"
            }
        ]
    }

    # Mock incident data
    incident_data = {
        "summary_period": {
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "days_covered": 30
        },
        "incident_statistics": {
            "total_incidents": 23,
            "injury_incidents": 2,
            "near_miss_incidents": 18,
            "property_damage_incidents": 3,
            "on_job_incidents": 20,
            "off_job_incidents": 3,
            "incidents_with_actions": 21,
            "incidents_with_evidence": 19,
            "action_completion_rate": 91.3
        },
        "type_breakdown": [
            {"type": "Near Miss", "count": 18, "percentage": 78.3},
            {"type": "Property Damage", "count": 3, "percentage": 13.0},
            {"type": "Minor Injury", "count": 2, "percentage": 8.7}
        ],
        "critical_incidents": [
            {
                "incident_id": "inc-001",
                "type": "Minor Injury",
                "category": "Slip and Fall",
                "description": "Employee slipped on wet floor in warehouse area",
                "location": "Warehouse A",
                "reported_by": "Safety Officer",
                "company": "ABC Manufacturing"
            }
        ]
    }

    # Mock action data
    action_data = {
        "summary_period": {
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "days_covered": 30
        },
        "action_statistics": {
            "total_actions": 87,
            "completed_actions": 76,
            "in_progress_actions": 8,
            "pending_actions": 3,
            "overdue_actions": 12,
            "high_priority_actions": 15,
            "critical_priority_actions": 3,
            "completion_rate": 87.4,
            "avg_completion_days": 4.2
        },
        "priority_breakdown": [
            {"priority": "medium", "count": 45, "completion_rate": 91.1},
            {"priority": "high", "count": 15, "completion_rate": 80.0},
            {"priority": "low", "count": 24, "completion_rate": 95.8},
            {"priority": "critical", "count": 3, "completion_rate": 66.7}
        ],
        "overdue_actions": [
            {
                "action_id": "act-001",
                "title": "Install safety barriers",
                "priority": "high",
                "days_overdue": 7,
                "action_owner": "Maintenance Team",
                "location": "Production Floor"
            }
        ]
    }

    # Mock inspection data
    inspection_data = {
        "summary_period": {
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "days_covered": 30
        },
        "inspection_statistics": {
            "total_inspections": 45,
            "inspections_requiring_approval": 12,
            "asset_enabled_inspections": 38,
            "overdue_inspections": 6,
            "due_this_week": 8,
            "avg_alert_days": 7.0
        },
        "assignment_statistics": {
            "total_assignments": 52,
            "completed_assignments": 46,
            "pending_assignments": 4,
            "in_progress_assignments": 2,
            "completion_rate": 88.5,
            "avg_completion_days": 3.1
        },
        "overdue_inspections": [
            {
                "inspection_id": "insp-001",
                "title": "Monthly Fire Safety Inspection",
                "days_overdue": 3,
                "occurrence_type": "monthly",
                "created_by": "Safety Manager"
            }
        ]
    }

    return permit_data, incident_data, action_data, inspection_data

def generate_simple_summary(permit_data, incident_data, action_data, inspection_data):
    """Generate a simple text summary without AI"""

    summary = f"""
=== SAFETY MANAGEMENT SUMMARY ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Period: Last 30 days

🔧 PERMIT TO WORK PERFORMANCE:
• Total Permits: {permit_data['permit_statistics']['total_permits']}
• Completion Rate: {permit_data['permit_statistics']['completion_rate']:.1f}%
• Overdue Permits: {permit_data['permit_statistics']['overdue_permits']}
• Average Completion Time: {permit_data['permit_statistics']['avg_completion_days']:.1f} days

🚨 INCIDENT MANAGEMENT:
• Total Incidents: {incident_data['incident_statistics']['total_incidents']}
• Injury Incidents: {incident_data['incident_statistics']['injury_incidents']}
• Near Miss Reports: {incident_data['incident_statistics']['near_miss_incidents']}
• Action Completion Rate: {incident_data['incident_statistics']['action_completion_rate']:.1f}%

📋 ACTION TRACKING:
• Total Actions: {action_data['action_statistics']['total_actions']}
• Completion Rate: {action_data['action_statistics']['completion_rate']:.1f}%
• Overdue Actions: {action_data['action_statistics']['overdue_actions']}
• High Priority Actions: {action_data['action_statistics']['high_priority_actions']}

🔍 INSPECTION TRACKING:
• Total Inspections: {inspection_data['inspection_statistics']['total_inspections']}
• Completion Rate: {inspection_data['assignment_statistics']['completion_rate']:.1f}%
• Overdue Inspections: {inspection_data['inspection_statistics']['overdue_inspections']}
• Due This Week: {inspection_data['inspection_statistics']['due_this_week']}

⚠️ CRITICAL ALERTS:
"""

    # Add alerts based on data
    alerts = []

    if permit_data['permit_statistics']['overdue_permits'] > 5:
        alerts.append(f"• HIGH: {permit_data['permit_statistics']['overdue_permits']} permits are overdue")

    if incident_data['incident_statistics']['injury_incidents'] > 0:
        alerts.append(f"• CRITICAL: {incident_data['incident_statistics']['injury_incidents']} injury incidents reported")

    if action_data['action_statistics']['overdue_actions'] > 10:
        alerts.append(f"• HIGH: {action_data['action_statistics']['overdue_actions']} actions are overdue")

    if inspection_data['inspection_statistics']['overdue_inspections'] > 5:
        alerts.append(f"• MEDIUM: {inspection_data['inspection_statistics']['overdue_inspections']} inspections are overdue")

    if not alerts:
        alerts.append("• No critical issues identified")

    summary += "\n".join(alerts)

    summary += f"""

💡 KEY INSIGHTS:
• Overall permit compliance is strong at {permit_data['permit_statistics']['completion_rate']:.1f}%
• Incident reporting shows good near-miss culture ({incident_data['incident_statistics']['near_miss_incidents']} near misses vs {incident_data['incident_statistics']['injury_incidents']} injuries)
• Action tracking needs attention with {action_data['action_statistics']['overdue_actions']} overdue items
• Inspection program is performing well with {inspection_data['assignment_statistics']['completion_rate']:.1f}% completion rate

📊 RECOMMENDATIONS:
1. Focus on reducing overdue permits through better scheduling
2. Investigate root causes of injury incidents for prevention
3. Implement escalation process for overdue high-priority actions
4. Continue current inspection practices while addressing overdue items
"""

    return summary

def generate_dashboard_data(permit_data, incident_data, action_data, inspection_data):
    """Generate dashboard-style data"""

    dashboard = {
        "last_updated": datetime.now().isoformat(),
        "summary_period": "Last 30 days",
        "key_metrics": {
            "permit_completion_rate": permit_data['permit_statistics']['completion_rate'],
            "total_incidents": incident_data['incident_statistics']['total_incidents'],
            "action_completion_rate": action_data['action_statistics']['completion_rate'],
            "inspection_completion_rate": inspection_data['assignment_statistics']['completion_rate']
        },
        "alerts": {
            "critical": incident_data['incident_statistics']['injury_incidents'],
            "high": permit_data['permit_statistics']['overdue_permits'] + action_data['action_statistics']['overdue_actions'],
            "medium": inspection_data['inspection_statistics']['overdue_inspections']
        },
        "trends": {
            "permits_trend": "stable",
            "incidents_trend": "improving",
            "actions_trend": "needs_attention",
            "inspections_trend": "good"
        }
    }

    return dashboard

def main():
    """Main test function"""
    print("🧪 AI Safety Summarizer - Simple Test")
    print("=" * 50)

    try:
        # Generate mock data
        print("📊 Generating mock safety data...")
        permit_data, incident_data, action_data, inspection_data = generate_mock_data()
        print("✅ Mock data generated successfully")

        # Generate simple summary
        print("\n📝 Generating summary...")
        summary = generate_simple_summary(permit_data, incident_data, action_data, inspection_data)
        print("✅ Summary generated successfully")

        # Display summary
        print(summary)

        # Generate dashboard data
        print("\n📈 Generating dashboard data...")
        dashboard = generate_dashboard_data(permit_data, incident_data, action_data, inspection_data)
        print("✅ Dashboard data generated successfully")

        # Save outputs
        with open("test_summary.txt", "w", encoding='utf-8') as f:
            f.write(summary)
        print("💾 Summary saved to test_summary.txt")

        with open("test_dashboard.json", "w", encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2, default=str, ensure_ascii=False)
        print("💾 Dashboard data saved to test_dashboard.json")

        print("\n🎉 Simple test completed successfully!")
        print("📁 Check the generated files for outputs")

        return True

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ The basic structure is working correctly!")
        print("🔧 Next steps:")
        print("   1. Set up your database connections in .env file")
        print("   2. Install required packages: pip install -r requirements.txt")
        print("   3. Run: python test_setup.py")
    else:
        print("\n❌ Basic test failed - check the error messages above")
