"""
Database Configuration for AI Safety Summarizer
Handles connections to both ProcessSafety and SafetyConnect databases
"""

import os
from dataclasses import dataclass
from typing import Optional
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    """Manages database connections for both ProcessSafety and SafetyConnect"""

    def __init__(self):
        self.process_safety_config = DatabaseConfig(
            host=os.getenv("PROCESS_SAFETY_DB_HOST", "localhost"),
            port=int(os.getenv("PROCESS_SAFETY_DB_PORT", "5432")),
            database=os.getenv("PROCESS_SAFETY_DB_NAME", "processsafety"),
            username=os.getenv("PROCESS_SAFETY_DB_USER", "postgres"),
            password=os.getenv("PROCESS_SAFETY_DB_PASSWORD", "")
        )

        self.safety_connect_config = DatabaseConfig(
            host=os.getenv("SAFETY_CONNECT_DB_HOST", "localhost"),
            port=int(os.getenv("SAFETY_CONNECT_DB_PORT", "5432")),
            database=os.getenv("SAFETY_CONNECT_DB_NAME", "safetyconnect"),
            username=os.getenv("SAFETY_CONNECT_DB_USER", "postgres"),
            password=os.getenv("SAFETY_CONNECT_DB_PASSWORD", "")
        )

        self._process_safety_engine = None
        self._safety_connect_engine = None
        self._process_safety_session = None
        self._safety_connect_session = None

    @property
    def process_safety_engine(self):
        if self._process_safety_engine is None:
            self._process_safety_engine = sa.create_engine(
                self.process_safety_config.connection_string,
                pool_pre_ping=True,
                pool_recycle=300
            )
        return self._process_safety_engine

    @property
    def safety_connect_engine(self):
        if self._safety_connect_engine is None:
            self._safety_connect_engine = sa.create_engine(
                self.safety_connect_config.connection_string,
                pool_pre_ping=True,
                pool_recycle=300
            )
        return self._safety_connect_engine

    def get_process_safety_session(self):
        if self._process_safety_session is None:
            Session = sessionmaker(bind=self.process_safety_engine)
            self._process_safety_session = Session()
        return self._process_safety_session

    def get_safety_connect_session(self):
        if self._safety_connect_session is None:
            Session = sessionmaker(bind=self.safety_connect_engine)
            self._safety_connect_session = Session()
        return self._safety_connect_session

    def close_connections(self):
        """Close all database connections"""
        if self._process_safety_session:
            self._process_safety_session.close()
        if self._safety_connect_session:
            self._safety_connect_session.close()
        if self._process_safety_engine:
            self._process_safety_engine.dispose()
        if self._safety_connect_engine:
            self._safety_connect_engine.dispose()

# Global database manager instance
db_manager = DatabaseManager()
