#!/usr/bin/env python3
"""
Test script to verify database connection improvements
"""

import sys
import os
from pathlib import Path

# Add the server directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import logging
from datetime import datetime, timedelta
from config.database_config import db_manager, test_database_connection
from data_extractors.incident_kpis import IncidentKPIsExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_connection():
    """Test basic database connection"""
    logger.info("Testing basic database connection...")
    try:
        result = test_database_connection()
        if result:
            logger.info("✅ Basic database connection test passed")
            return True
        else:
            logger.error("❌ Basic database connection test failed")
            return False
    except Exception as e:
        logger.error(f"❌ Basic database connection test failed with exception: {str(e)}")
        return False

def test_session_creation():
    """Test database session creation"""
    logger.info("Testing database session creation...")
    try:
        session = db_manager.get_process_safety_session()
        if session:
            logger.info("✅ Database session creation test passed")
            session.close()
            return True
        else:
            logger.error("❌ Database session creation test failed")
            return False
    except Exception as e:
        logger.error(f"❌ Database session creation test failed with exception: {str(e)}")
        return False

def test_session_validation():
    """Test session validation functionality"""
    logger.info("Testing session validation...")
    try:
        session = db_manager.get_validated_session()

        # Test validation
        if db_manager.validate_session(session):
            logger.info("✅ Session validation test passed")

            # Test cleanup
            db_manager.cleanup_session(session)
            logger.info("✅ Session cleanup test passed")
            return True
        else:
            logger.error("❌ Session validation test failed")
            return False
    except Exception as e:
        logger.error(f"❌ Session validation test failed with exception: {str(e)}")
        return False

def test_connection_recovery():
    """Test connection recovery after simulated failure"""
    logger.info("Testing connection recovery...")
    try:
        # Get initial session
        session1 = db_manager.get_validated_session()
        logger.info("Got initial session")

        # Simulate connection loss
        db_manager._reset_engine()
        logger.info("Simulated connection reset")

        # Try to get a fresh session
        session2 = db_manager.create_fresh_session()

        if db_manager.validate_session(session2):
            logger.info("✅ Connection recovery test passed")
            db_manager.cleanup_session(session2)
            return True
        else:
            logger.error("❌ Connection recovery test failed")
            return False
    except Exception as e:
        logger.error(f"❌ Connection recovery test failed with exception: {str(e)}")
        return False

def test_incident_kpis_extractor():
    """Test incident KPIs extractor with connection recovery"""
    logger.info("Testing incident KPIs extractor...")
    try:
        session = db_manager.get_process_safety_session()
        extractor = IncidentKPIsExtractor(session)
        
        # Test getting subtag IDs
        subtag_ids = extractor._get_all_subtag_ids()
        logger.info(f"Found {len(subtag_ids)} incident subtag IDs")
        
        # Test getting incidents reported
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        incidents_data = extractor.get_incidents_reported(
            customer_id=None,
            start_date=start_date,
            end_date=end_date
        )
        
        logger.info(f"Incidents reported: {incidents_data.get('total_incidents', 0)}")
        logger.info("✅ Incident KPIs extractor test passed")
        
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Incident KPIs extractor test failed with exception: {str(e)}")
        return False

def test_fresh_session_creation():
    """Test fresh session creation"""
    logger.info("Testing fresh session creation...")
    try:
        session = db_manager.create_fresh_session()
        if session:
            logger.info("✅ Fresh session creation test passed")
            session.close()
            return True
        else:
            logger.error("❌ Fresh session creation test failed")
            return False
    except Exception as e:
        logger.error(f"❌ Fresh session creation test failed with exception: {str(e)}")
        return False

def main():
    """Run all database connection tests"""
    logger.info("Starting database connection tests...")
    logger.info("=" * 50)
    
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Session Creation", test_session_creation),
        ("Session Validation", test_session_validation),
        ("Connection Recovery", test_connection_recovery),
        ("Fresh Session Creation", test_fresh_session_creation),
        ("Incident KPIs Extractor", test_incident_kpis_extractor),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running test: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                logger.error(f"Test {test_name} failed")
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {str(e)}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error(f"❌ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
