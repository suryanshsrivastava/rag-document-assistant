"""
Vector Store Service for RAG System

Handles vector storage and similarity search using Supabase.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from ..database.connection import get_supabase_client

logger = logging.getLogger(__name__)

class VectorStore:
    """Service for vector storage and similarity search."""
    
    def __init__(self):
        """Initialize vector store with Supabase client."""
        self.supabase = get_supabase_client()
        
    async def store_document_chunks(
        self, 
        document_id: str, 
        chunks: List[Dict[str, Any]], 
        embeddings: List[List[float]]
    ) -> bool:
        """
        Store document chunks with their embeddings.
        
        Args:
            document_id: ID of the parent document
            chunks: List of chunk dictionaries
            embeddings: List of embedding vectors
            
        Returns:
            True if storage was successful
        """
        try:
            # Prepare data for insertion
            chunk_data = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_record = {
                    "id": str(uuid.uuid4()),
                    "document_id": document_id,
                    "chunk_text": chunk["chunk_text"],
                    "chunk_index": chunk["chunk_index"],
                    "embedding": embedding,
                    "metadata": chunk.get("metadata", {}),
                    "created_at": datetime.utcnow().isoformat()
                }
                chunk_data.append(chunk_record)
            
            # Insert chunks into database
            result = self.supabase.table("document_chunks").insert(chunk_data).execute()
            
            logger.info(f"Stored {len(chunk_data)} chunks for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing document chunks: {str(e)}")
            raise Exception(f"Failed to store document chunks: {str(e)}")
    
    async def search_similar_chunks(
        self, 
        query_embedding: List[float], 
        document_ids: Optional[List[str]] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity.
        
        Args:
            query_embedding: Embedding vector of the query
            document_ids: Optional list of document IDs to search within
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar chunks with metadata
        """
        try:
            # Build query
            query = self.supabase.table("document_chunks").select(
                "id, document_id, chunk_text, chunk_index, metadata, embedding"
            )
            
            # Filter by document IDs if provided
            if document_ids:
                query = query.in_("document_id", document_ids)
            
            # Perform vector similarity search
            # Note: This assumes Supabase has pgvector extension enabled
            # The exact syntax may vary based on your Supabase setup
            result = query.order(
                f"embedding <-> '{query_embedding}'::vector"
            ).limit(limit).execute()
            
            # Process results
            similar_chunks = []
            for row in result.data:
                chunk_data = {
                    "chunk_id": row["id"],
                    "document_id": row["document_id"],
                    "chunk_text": row["chunk_text"],
                    "chunk_index": row["chunk_index"],
                    "metadata": row.get("metadata", {}),
                    "similarity_score": 1.0  # Placeholder - calculate actual similarity
                }
                similar_chunks.append(chunk_data)
            
            logger.info(f"Found {len(similar_chunks)} similar chunks")
            return similar_chunks
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {str(e)}")
            raise Exception(f"Vector search failed: {str(e)}")
    
    async def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all chunks for a specific document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            List of document chunks
        """
        try:
            result = self.supabase.table("document_chunks").select(
                "id, chunk_text, chunk_index, metadata"
            ).eq("document_id", document_id).order("chunk_index").execute()
            
            chunks = []
            for row in result.data:
                chunk_data = {
                    "chunk_id": row["id"],
                    "chunk_text": row["chunk_text"],
                    "chunk_index": row["chunk_index"],
                    "metadata": row.get("metadata", {})
                }
                chunks.append(chunk_data)
            
            logger.info(f"Retrieved {len(chunks)} chunks for document {document_id}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error retrieving document chunks: {str(e)}")
            raise Exception(f"Failed to retrieve document chunks: {str(e)}")
    
    async def delete_document_chunks(self, document_id: str) -> bool:
        """
        Delete all chunks for a specific document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            True if deletion was successful
        """
        try:
            result = self.supabase.table("document_chunks").delete().eq("document_id", document_id).execute()
            
            logger.info(f"Deleted chunks for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document chunks: {str(e)}")
            raise Exception(f"Failed to delete document chunks: {str(e)}")
    
    async def get_chunk_statistics(self, document_id: str) -> Dict[str, Any]:
        """
        Get statistics about chunks for a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Dictionary with chunk statistics
        """
        try:
            chunks = await self.get_document_chunks(document_id)
            
            if not chunks:
                return {
                    "total_chunks": 0,
                    "total_characters": 0,
                    "average_chunk_size": 0
                }
            
            total_chunks = len(chunks)
            total_characters = sum(len(chunk["chunk_text"]) for chunk in chunks)
            average_chunk_size = total_characters / total_chunks
            
            return {
                "total_chunks": total_chunks,
                "total_characters": total_characters,
                "average_chunk_size": average_chunk_size
            }
            
        except Exception as e:
            logger.error(f"Error getting chunk statistics: {str(e)}")
            return {
                "total_chunks": 0,
                "total_characters": 0,
                "average_chunk_size": 0
            }
    
    async def test_connection(self) -> bool:
        """
        Test vector store connection.
        
        Returns:
            True if connection is successful
        """
        try:
            # Simple query to test connection
            result = self.supabase.table("document_chunks").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Vector store connection test failed: {str(e)}")
            return False 