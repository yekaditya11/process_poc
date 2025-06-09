"""
Database Configuration for AI Safety Summarizer
Handles connection to ProcessSafety database only
"""

import os
from dataclasses import dataclass
from typing import Optional
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    driver: str = "postgresql+psycopg2"

    @property
    def connection_string(self) -> str:
        from urllib.parse import quote_plus
        # URL encode the password to handle special characters
        encoded_password = quote_plus(self.password)
        return f"{self.driver}://{self.username}:{encoded_password}@{self.host}:{self.port}/{self.database}"

class DatabaseManager:
    """Manages database connection for ProcessSafety only"""

    def __init__(self):
        self.process_safety_config = DatabaseConfig(
            host=os.getenv("PROCESS_SAFETY_DB_HOST", "localhost"),
            port=int(os.getenv("PROCESS_SAFETY_DB_PORT", "5432")),
            database=os.getenv("PROCESS_SAFETY_DB_NAME", "processSafety"),
            username=os.getenv("PROCESS_SAFETY_DB_USER", "postgres"),
            password=os.getenv("PROCESS_SAFETY_DB_PASSWORD", "")
        )

        self._process_safety_engine = None
        self._process_safety_session = None

        logger.info(f"Database config initialized for ProcessSafety: {self.process_safety_config.host}:{self.process_safety_config.port}/{self.process_safety_config.database}")

    @property
    def process_safety_engine(self):
        if self._process_safety_engine is None:
            try:
                self._process_safety_engine = sa.create_engine(
                    self.process_safety_config.connection_string,
                    pool_pre_ping=True,
                    pool_recycle=300,
                    pool_size=10,
                    max_overflow=20,
                    pool_timeout=30,
                    echo=False,
                    connect_args={
                        "connect_timeout": 10,
                        "application_name": "SafetyConnect_Dashboard"
                    }
                )
                logger.info("ProcessSafety database engine created successfully")
            except Exception as e:
                logger.error(f"Failed to create ProcessSafety database engine: {str(e)}")
                raise
        return self._process_safety_engine

    def get_process_safety_session(self):
        """Get ProcessSafety database session with retry logic"""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Always create a new session to avoid transaction issues
                Session = sessionmaker(bind=self.process_safety_engine)
                session = Session()

                # Test the connection with a simple query
                session.execute(sa.text("SELECT 1"))
                session.commit()

                logger.info("ProcessSafety database session created successfully")
                return session
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                logger.warning(f"Failed to create ProcessSafety database session (attempt {retry_count}/{max_retries}): {error_msg}")

                # Clean up failed session
                try:
                    if 'session' in locals():
                        session.rollback()
                        session.close()
                except:
                    pass

                if retry_count >= max_retries:
                    logger.error(f"Failed to create ProcessSafety database session after {max_retries} attempts")
                    raise

                # Reset engine on connection failure to force reconnection
                if self._is_connection_error(error_msg):
                    logger.info("Resetting database engine due to connection issue")
                    self._reset_engine()

                # Wait before retry
                import time
                time.sleep(1)

    def _is_connection_error(self, error_msg: str) -> bool:
        """Check if error is related to database connection"""
        connection_indicators = [
            "server closed the connection",
            "connection unexpectedly",
            "can't reconnect until invalid transaction is rolled back",
            "connection lost",
            "connection refused",
            "connection timeout",
            "connection reset",
            "connection broken"
        ]
        return any(indicator in error_msg.lower() for indicator in connection_indicators)

    def _reset_engine(self):
        """Reset the database engine to force new connections"""
        try:
            if self._process_safety_engine:
                self._process_safety_engine.dispose()
                self._process_safety_engine = None
            logger.info("Database engine reset successfully")
        except Exception as e:
            logger.error(f"Error resetting database engine: {str(e)}")

    def validate_session(self, session):
        """Validate that a database session is still active and usable"""
        try:
            # Try a simple query to test the connection
            session.execute(sa.text("SELECT 1"))
            return True
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"Session validation failed: {error_msg}")

            # Try to rollback any pending transaction
            try:
                session.rollback()
            except:
                pass

            return False

    def cleanup_session(self, session):
        """Safely cleanup a database session"""
        if session:
            try:
                # Rollback any pending transaction
                session.rollback()
                # Close the session
                session.close()
                logger.debug("Database session cleaned up successfully")
            except Exception as e:
                logger.warning(f"Error during session cleanup: {str(e)}")

    def get_validated_session(self):
        """Get a validated database session, creating a new one if needed"""
        try:
            session = self.get_process_safety_session()
            if self.validate_session(session):
                return session
            else:
                # Session is invalid, clean it up and create a new one
                self.cleanup_session(session)
                return self.get_process_safety_session()
        except Exception as e:
            logger.error(f"Failed to get validated session: {str(e)}")
            raise

    def test_connection(self):
        """Test the database connection"""
        try:
            session = self.get_process_safety_session()
            # Simple test query
            result = session.execute(sa.text("SELECT 1"))
            result.fetchone()
            session.close()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False

    def create_fresh_session(self):
        """Create a fresh database session, resetting engine if needed"""
        try:
            # Reset the engine to force new connections
            self._reset_engine()
            return self.get_validated_session()
        except Exception as e:
            logger.error(f"Failed to create fresh session: {str(e)}")
            raise

    def close_connections(self):
        """Close database connections"""
        if self._process_safety_session:
            self.cleanup_session(self._process_safety_session)
            self._process_safety_session = None
        if self._process_safety_engine:
            self._process_safety_engine.dispose()
            self._process_safety_engine = None
        logger.info("Database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

def get_database_connections():
    """
    Get database connection for ProcessSafety database
    Returns a dictionary with session object for backward compatibility
    """
    try:
        session = db_manager.get_validated_session()
        return {
            'processsafety': session,  # lowercase for consistency
            'processafety': session    # alternative key for compatibility
        }
    except Exception as e:
        logger.error(f"Failed to get database connections: {str(e)}")
        return {}

def get_process_safety_session():
    """
    Get ProcessSafety database session directly
    """
    return db_manager.get_validated_session()

def test_database_connection():
    """
    Test the database connection
    """
    return db_manager.test_connection()
