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
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not found in environment variables")
            return
            
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise
    
    def get_client(self) -> Client:
        """Get the Supabase client instance."""
        if not self.client:
            raise Exception("Database client not initialized. Check environment variables.")
        return self.client
    
    async def test_connection(self) -> bool:
        """Test database connection."""
        try:
            if not self.client:
                return False
            
            # Simple query to test connection
            result = self.client.table("documents").select("id").limit(1).execute()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False

# Global database connection instance
db_connection = DatabaseConnection()

def get_supabase_client() -> Client:
    """Get the Supabase client for use in other modules."""
    return db_connection.get_client()

async def test_database_connection() -> bool:
    """Test the database connection."""
    return await db_connection.test_connection() 