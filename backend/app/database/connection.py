"""
Database Connection Module for RAG System

Handles Supabase connection and provides database client utilities.
"""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Manages Supabase database connection and provides client access."""
    
    def __init__(self):
        """Initialize database connection with environment variables."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.client: Optional[Client] = None
        self._initialized = False
        
        logger.info("Database connection manager initialized")
    
    def _initialize_client(self) -> None:
        """Lazy initialization of the Supabase client."""
        if self._initialized:
            return
            
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not found in environment variables")
            self._initialized = True
            return
            
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
            self._initialized = True
            logger.info("Supabase client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            self._initialized = True
            raise
    
    def get_client(self) -> Optional[Client]:
        """Get the Supabase client instance with lazy initialization."""
        if not self._initialized:
            self._initialize_client()
        
        if not self.client:
            logger.warning("Database client not available - check environment variables")
            return None
            
        return self.client
    
    def is_available(self) -> bool:
        """Check if database connection is available."""
        if not self._initialized:
            self._initialize_client()
        return self.client is not None
    
    async def test_connection(self) -> bool:
        """Test database connection."""
        try:
            client = self.get_client()
            if not client:
                return False
            
            # Simple query to test connection
            result = client.table("documents").select("id").limit(1).execute()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False

# Global database connection instance
db_connection = DatabaseConnection()

def get_supabase_client() -> Optional[Client]:
    """Get the Supabase client for use in other modules."""
    return db_connection.get_client()

def is_database_available() -> bool:
    """Check if database is available."""
    return db_connection.is_available()

async def test_database_connection() -> bool:
    """Test the database connection."""
    return await db_connection.test_connection() 