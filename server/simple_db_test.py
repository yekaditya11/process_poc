"""
Simple Database Test
Tests basic database connectivity and simple queries
"""

import sys
import os
from sqlalchemy import text

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database_config import db_manager

def test_basic_queries():
    """Test basic database queries"""
    print("🔍 Testing Basic Database Queries")
    print("=" * 50)
    
    try:
        # Test ProcessSafety database
        print("\n📊 ProcessSafety Database:")
        ps_engine = db_manager.process_safety_engine
        
        with ps_engine.connect() as conn:
            # Simple count query
            result = conn.execute(text('SELECT COUNT(*) as total FROM "ProcessSafetyAssignments"'))
            total_permits = result.fetchone().total
            print(f"✅ Total ProcessSafetyAssignments: {total_permits}")
            
            # Get recent records
            result = conn.execute(text('''
                SELECT psa.id, psa.status, psa."createdAt" 
                FROM "ProcessSafetyAssignments" psa 
                ORDER BY psa."createdAt" DESC 
                LIMIT 5
            '''))
            recent_permits = result.fetchall()
            print(f"✅ Recent permits found: {len(recent_permits)}")
            
            for permit in recent_permits:
                print(f"   • ID: {str(permit.id)[:8]}..., Status: {permit.status}, Created: {permit.createdAt}")
        
        # Test SafetyConnect database
        print("\n📊 SafetyConnect Database:")
        sc_engine = db_manager.safety_connect_engine
        
        with sc_engine.connect() as conn:
            # Test Incidents table
            try:
                result = conn.execute(text('SELECT COUNT(*) as total FROM "Incidents"'))
                total_incidents = result.fetchone().total
                print(f"✅ Total Incidents: {total_incidents}")
            except Exception as e:
                print(f"❌ Incidents table error: {str(e)}")
            
            # Test ActionTrackings table
            try:
                result = conn.execute(text('SELECT COUNT(*) as total FROM "ActionTrackings"'))
                total_actions = result.fetchone().total
                print(f"✅ Total ActionTrackings: {total_actions}")
            except Exception as e:
                print(f"❌ ActionTrackings table error: {str(e)}")
            
            # Test InspectionTrackings table
            try:
                result = conn.execute(text('SELECT COUNT(*) as total FROM "InspectionTrackings"'))
                total_inspections = result.fetchone().total
                print(f"✅ Total InspectionTrackings: {total_inspections}")
            except Exception as e:
                print(f"❌ InspectionTrackings table error: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False

def test_simple_permit_query():
    """Test a simple permit query"""
    print("\n🔍 Testing Simple Permit Query")
    print("=" * 50)
    
    try:
        ps_engine = db_manager.process_safety_engine
        
        with ps_engine.connect() as conn:
            # Simple permit statistics
            query = '''
            SELECT 
                COUNT(*) as total_permits,
                COUNT(CASE WHEN psa.status = 'completed' THEN 1 END) as completed_permits,
                COUNT(CASE WHEN psa.status = 'pending' THEN 1 END) as pending_permits
            FROM "ProcessSafetyAssignments" psa
            WHERE psa."createdAt" >= CURRENT_DATE - INTERVAL '30 days'
            '''
            
            result = conn.execute(text(query))
            stats = result.fetchone()
            
            print(f"✅ Last 30 days permit statistics:")
            print(f"   • Total Permits: {stats.total_permits}")
            print(f"   • Completed: {stats.completed_permits}")
            print(f"   • Pending: {stats.pending_permits}")
            
            if stats.total_permits > 0:
                completion_rate = (stats.completed_permits / stats.total_permits) * 100
                print(f"   • Completion Rate: {completion_rate:.1f}%")
            
            return True
            
    except Exception as e:
        print(f"❌ Simple permit query failed: {str(e)}")
        return False

def test_dashboard_data():
    """Test generating simple dashboard data"""
    print("\n🔍 Testing Dashboard Data Generation")
    print("=" * 50)
    
    dashboard_data = {}
    
    try:
        # Get permit data
        ps_engine = db_manager.process_safety_engine
        with ps_engine.connect() as conn:
            result = conn.execute(text('''
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN psa.status = 'completed' THEN 1 END) as completed
                FROM "ProcessSafetyAssignments" psa
                WHERE psa."createdAt" >= CURRENT_DATE - INTERVAL '7 days'
            '''))
            permit_stats = result.fetchone()
            
            dashboard_data['permits'] = {
                'total': permit_stats.total,
                'completed': permit_stats.completed,
                'completion_rate': (permit_stats.completed / permit_stats.total * 100) if permit_stats.total > 0 else 0
            }
            print(f"✅ Permit data: {dashboard_data['permits']}")
        
        # Get incident data (if available)
        sc_engine = db_manager.safety_connect_engine
        with sc_engine.connect() as conn:
            try:
                result = conn.execute(text('''
                    SELECT COUNT(*) as total
                    FROM "Incidents" i
                    WHERE i."createdAt" >= CURRENT_DATE - INTERVAL '7 days'
                '''))
                incident_stats = result.fetchone()
                
                dashboard_data['incidents'] = {
                    'total': incident_stats.total
                }
                print(f"✅ Incident data: {dashboard_data['incidents']}")
                
            except Exception as e:
                print(f"⚠️  Incident data not available: {str(e)}")
                dashboard_data['incidents'] = {'total': 0}
        
        print(f"\n📊 Dashboard Summary:")
        print(f"   • Permits (7 days): {dashboard_data['permits']['total']} total, {dashboard_data['permits']['completion_rate']:.1f}% completed")
        print(f"   • Incidents (7 days): {dashboard_data['incidents']['total']} total")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard data generation failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 AI Safety Summarizer - Simple Database Test")
    print("=" * 60)
    
    try:
        # Test basic queries
        test1 = test_basic_queries()
        
        # Test simple permit query
        test2 = test_simple_permit_query()
        
        # Test dashboard data
        test3 = test_dashboard_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        tests = [
            ("Basic Database Queries", test1),
            ("Simple Permit Query", test2),
            ("Dashboard Data Generation", test3)
        ]
        
        passed = sum(1 for _, result in tests if result)
        total = len(tests)
        
        for test_name, result in tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All database tests passed!")
            print("✅ Your database connections are working correctly")
            print("🔧 You can now run the full AI summarizer")
            return True
        else:
            print("⚠️  Some tests failed - check the error messages above")
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        return False
    finally:
        db_manager.close_connections()

if __name__ == "__main__":
    success = main()
    if success:
        print("\n💡 Next steps:")
        print("   1. Run: python main_app.py --dashboard")
        print("   2. Or run: python run_server.py")
    else:
        print("\n💡 Troubleshooting:")
        print("   1. Check your .env file configuration")
        print("   2. Verify database table names and column names")
        print("   3. Ensure your database user has read permissions")
    
    sys.exit(0 if success else 1)
