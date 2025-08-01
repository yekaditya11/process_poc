"""
ClickHouse Database Configuration for ETL Pipeline
Handles connection management and operations for ClickHouse analytical database
"""

import os
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from contextlib import contextmanager
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.etl')

logger = logging.getLogger(__name__)

@dataclass
class ClickHouseConfig:
    """ClickHouse connection configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    secure: bool = False
    connect_timeout: int = 10
    send_receive_timeout: int = 300
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters for ClickHouse client"""
        params = {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'username': self.username,
            'password': self.password,
            'connect_timeout': self.connect_timeout,
            'send_receive_timeout': self.send_receive_timeout
        }
        if self.secure:
            params['secure'] = True
        return params

class ClickHouseManager:
    """Manages ClickHouse database connections and operations"""
    
    def __init__(self, config: Optional[ClickHouseConfig] = None):
        if config is None:
            config = ClickHouseConfig(
                host=os.getenv("CLICKHOUSE_HOST", "localhost"),
                port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
                database=os.getenv("CLICKHOUSE_DATABASE", "process_safety_analytics"),
                username=os.getenv("CLICKHOUSE_USERNAME", "default"),
                password=os.getenv("CLICKHOUSE_PASSWORD", ""),
                secure=os.getenv("CLICKHOUSE_SECURE", "false").lower() == "true",
                connect_timeout=int(os.getenv("CLICKHOUSE_CONNECT_TIMEOUT", "10")),
                send_receive_timeout=int(os.getenv("CLICKHOUSE_TIMEOUT", "300"))
            )
        
        self.config = config
        self._client = None
        logger.info(f"ClickHouse manager initialized for {config.host}:{config.port}/{config.database}")
    
    @property
    def client(self):
        """Get ClickHouse client with lazy initialization"""
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    def _create_client(self):
        """Create ClickHouse client"""
        try:
            import clickhouse_connect
            
            # Create client with connection parameters
            client = clickhouse_connect.get_client(**self.config.get_connection_params())
            
            # Test connection
            result = client.query("SELECT 1")
            if result.result_rows[0][0] == 1:
                logger.info("ClickHouse connection established successfully")
                return client
            else:
                raise Exception("Connection test failed")
                
        except ImportError:
            logger.error("ClickHouse client not available. Install with: pip install clickhouse-connect")
            raise
        except Exception as e:
            logger.error(f"Failed to create ClickHouse client: {str(e)}")
            logger.error(f"Connection details: {self.config.host}:{self.config.port}")
            raise
    
    def test_connection(self) -> bool:
        """Test ClickHouse connection"""
        try:
            result = self.client.query("SELECT 1")
            return result.result_rows[0][0] == 1
        except Exception as e:
            logger.error(f"ClickHouse connection test failed: {str(e)}")
            return False
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> Any:
        """Execute a query and return results"""
        try:
            if parameters:
                result = self.client.query(query, parameters=parameters)
            else:
                result = self.client.query(query)
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            logger.error(f"Query: {query[:200]}...")
            raise
    
    def execute_command(self, command: str, parameters: Optional[Dict] = None) -> None:
        """Execute a command (no return value expected)"""
        try:
            if parameters:
                self.client.command(command, parameters=parameters)
            else:
                self.client.command(command)
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            logger.error(f"Command: {command[:200]}...")
            raise
    
    def insert_data(self, table: str, data: List[List], column_names: Optional[List[str]] = None) -> None:
        """Insert data into ClickHouse table"""
        try:
            if column_names:
                self.client.insert(table, data, column_names=column_names)
            else:
                self.client.insert(table, data)
            logger.debug(f"Inserted {len(data)} rows into {table}")
        except Exception as e:
            logger.error(f"Data insertion failed for table {table}: {str(e)}")
            logger.error(f"Data sample: {data[:2] if data else 'No data'}")
            raise
    
    def insert_dataframe(self, table: str, df, column_names: Optional[List[str]] = None) -> None:
        """Insert pandas DataFrame into ClickHouse table"""
        try:
            # Convert DataFrame to list of lists
            data = df.values.tolist()
            if column_names is None:
                column_names = df.columns.tolist()
            
            self.insert_data(table, data, column_names)
            logger.debug(f"Inserted DataFrame with {len(df)} rows into {table}")
        except Exception as e:
            logger.error(f"DataFrame insertion failed for table {table}: {str(e)}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        try:
            query = """
            SELECT count() 
            FROM system.tables 
            WHERE database = {database:String} AND name = {table:String}
            """
            result = self.execute_query(query, {
                'database': self.config.database,
                'table': table_name
            })
            return result.result_rows[0][0] > 0
        except Exception as e:
            logger.error(f"Error checking table existence for {table_name}: {str(e)}")
            return False
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for table"""
        try:
            result = self.execute_query(f"SELECT count() FROM {table_name}")
            return result.result_rows[0][0]
        except Exception as e:
            logger.error(f"Error getting count for table {table_name}: {str(e)}")
            return 0
    
    def get_max_value(self, table_name: str, column_name: str) -> Any:
        """Get maximum value from a column"""
        try:
            result = self.execute_query(f"SELECT max({column_name}) FROM {table_name}")
            return result.result_rows[0][0]
        except Exception as e:
            logger.error(f"Error getting max value for {table_name}.{column_name}: {str(e)}")
            return None
    
    def truncate_table(self, table_name: str) -> None:
        """Truncate table (ClickHouse uses TRUNCATE TABLE)"""
        try:
            self.execute_command(f"TRUNCATE TABLE {table_name}")
            logger.info(f"Truncated table {table_name}")
        except Exception as e:
            logger.error(f"Error truncating table {table_name}: {str(e)}")
            raise
    
    def optimize_table(self, table_name: str) -> None:
        """Optimize table (ClickHouse OPTIMIZE TABLE)"""
        try:
            self.execute_command(f"OPTIMIZE TABLE {table_name}")
            logger.info(f"Optimized table {table_name}")
        except Exception as e:
            logger.warning(f"Table optimization failed for {table_name}: {str(e)}")
    
    def create_database_if_not_exists(self) -> None:
        """Create database if it doesn't exist"""
        try:
            # Connect without database to create it
            admin_params = self.config.get_connection_params()
            admin_params.pop('database', None)
            
            import clickhouse_connect
            admin_client = clickhouse_connect.get_client(**admin_params)
            
            admin_client.command(f"CREATE DATABASE IF NOT EXISTS {self.config.database}")
            logger.info(f"Database {self.config.database} ready")
            
            admin_client.close()
        except Exception as e:
            logger.error(f"Error creating database {self.config.database}: {str(e)}")
            raise
    
    @contextmanager
    def transaction(self):
        """Context manager for transactions (ClickHouse doesn't have traditional transactions)"""
        try:
            yield self.client
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            raise
    
    def close(self):
        """Close ClickHouse connection"""
        if self._client:
            try:
                self._client.close()
                self._client = None
                logger.info("ClickHouse connection closed")
            except Exception as e:
                logger.warning(f"Error closing ClickHouse connection: {str(e)}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Global ClickHouse manager instance
clickhouse_manager = ClickHouseManager()

def get_clickhouse_client():
    """Get ClickHouse client"""
    return clickhouse_manager.client

def test_clickhouse_connection() -> bool:
    """Test ClickHouse connection"""
    return clickhouse_manager.test_connection()
