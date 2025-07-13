"""
RAG Service - Main Orchestration Service

Coordinates the entire RAG pipeline: document processing, chunking, embedding, and retrieval.
"""

import uuid
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .document_processor import DocumentProcessor
from .chunking_service import ChunkingService
from .gemini_client import GeminiClient
from .vector_store import VectorStore
from ..database.connection import get_supabase_client

logger = logging.getLogger(__name__)

class RAGService:
    """Main RAG orchestration service."""
    
    def __init__(self):
        """Initialize RAG service with all required components."""
        self.document_processor = DocumentProcessor()
        self.chunking_service = ChunkingService()
        self.gemini_client = GeminiClient()
        self.vector_store = VectorStore()
        self.supabase = get_supabase_client()
        
        logger.info("RAG service initialized successfully")
    
    async def process_document(self, file) -> Dict[str, Any]:
        """
        Process a document through the complete RAG pipeline.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Step 1: Process document and extract text
            logger.info("Starting document processing")
            processed_doc = await self.document_processor.process_document(file)
            
            # Step 2: Chunk the extracted text
            logger.info("Chunking document text")
            chunks = self.chunking_service.chunk_text(
                processed_doc["text_content"], 
                processed_doc["file_id"]
            )
            
            # Step 3: Generate embeddings for chunks
            logger.info("Generating embeddings")
            chunk_texts = [chunk["chunk_text"] for chunk in chunks]
            embeddings = await self.gemini_client.generate_embeddings(chunk_texts)
            
            # Step 4: Store document metadata
            logger.info("Storing document metadata")
            document_id = await self._store_document_metadata(processed_doc)
            
            # Step 5: Store chunks and embeddings
            logger.info("Storing chunks and embeddings")
            await self.vector_store.store_document_chunks(document_id, chunks, embeddings)
            
            # Step 6: Update document status
            await self._update_document_status(document_id, "processed")
            
            logger.info(f"Document processing completed: {document_id}")
            return {
                "document_id": document_id,
                "filename": processed_doc["filename"],
                "status": "processed",
                "chunks_created": len(chunks),
                "file_size": processed_doc["metadata"]["file_size"],
                "word_count": processed_doc["metadata"].get("word_count", 0)
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise Exception(f"Document processing failed: {str(e)}")
    
    async def chat_with_documents(
        self, 
        user_message: str, 
        document_ids: Optional[List[str]] = None,
        conversation_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Chat with documents using RAG.
        
        Args:
            user_message: User's question or message
            document_ids: Optional list of document IDs to search
            conversation_id: Optional conversation ID for context
            conversation_history: Optional conversation history
            
        Returns:
            Dictionary with response and sources
        """
        try:
            # Step 1: Generate embedding for user query
            logger.info("Generating query embedding")
            query_embeddings = await self.gemini_client.generate_embeddings([user_message])
            query_embedding = query_embeddings[0]
            
            # Step 2: Search for similar chunks
            logger.info("Searching for similar chunks")
            similar_chunks = await self.vector_store.search_similar_chunks(
                query_embedding, 
                document_ids,
                limit=5
            )
            
            # Step 3: Generate RAG response
            logger.info("Generating RAG response")
            response = await self.gemini_client.generate_rag_response(
                user_message,
                similar_chunks,
                conversation_history
            )
            
            # Step 4: Save conversation if needed
            if conversation_id:
                await self._save_conversation_message(
                    conversation_id, 
                    "user", 
                    user_message
                )
                await self._save_conversation_message(
                    conversation_id, 
                    "assistant", 
                    response,
                    similar_chunks
                )
            
            logger.info("RAG chat completed successfully")
            return {
                "response": response,
                "sources": similar_chunks,
                "conversation_id": conversation_id,
                "message_id": str(uuid.uuid4())
            }
            
        except Exception as e:
            logger.error(f"Error in RAG chat: {str(e)}")
            raise Exception(f"RAG chat failed: {str(e)}")
    
    async def _store_document_metadata(self, processed_doc: Dict[str, Any]) -> str:
        """
        Store document metadata in database.
        
        Args:
            processed_doc: Processed document data
            
        Returns:
            Document ID
        """
        try:
            document_id = str(uuid.uuid4())
            document_data = {
                "id": document_id,
                "filename": processed_doc["filename"],
                "file_path": processed_doc["file_path"],
                "content_type": processed_doc["metadata"]["content_type"],
                "file_size": processed_doc["metadata"]["file_size"],
                "page_count": processed_doc["metadata"].get("page_count"),
                "word_count": processed_doc["metadata"].get("word_count"),
                "status": "processing",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("documents").insert(document_data).execute()
            
            return document_id
            
        except Exception as e:
            logger.error(f"Error storing document metadata: {str(e)}")
            raise Exception(f"Failed to store document metadata: {str(e)}")
    
    async def _update_document_status(self, document_id: str, status: str) -> bool:
        """
        Update document status.
        
        Args:
            document_id: Document ID
            status: New status
            
        Returns:
            True if update was successful
        """
        try:
            result = self.supabase.table("documents").update({
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", document_id).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating document status: {str(e)}")
            return False
    
    async def _save_conversation_message(
        self, 
        conversation_id: str, 
        role: str, 
        content: str,
        sources: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Save a conversation message.
        
        Args:
            conversation_id: Conversation ID
            role: Message role (user/assistant)
            content: Message content
            sources: Optional sources for assistant messages
            
        Returns:
            Message ID
        """
        try:
            message_id = str(uuid.uuid4())
            message_data = {
                "id": message_id,
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "sources": sources or [],
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("chat_messages").insert(message_data).execute()
            
            return message_id
            
        except Exception as e:
            logger.error(f"Error saving conversation message: {str(e)}")
            raise Exception(f"Failed to save conversation message: {str(e)}")
    
    async def get_document_info(self, document_id: str) -> Dict[str, Any]:
        """
        Get document information and statistics.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document information dictionary
        """
        try:
            # Get document metadata
            result = self.supabase.table("documents").select("*").eq("id", document_id).execute()
            
            if not result.data:
                raise Exception("Document not found")
            
            document = result.data[0]
            
            # Get chunk statistics
            chunk_stats = await self.vector_store.get_chunk_statistics(document_id)
            
            return {
                "document": document,
                "chunk_statistics": chunk_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting document info: {str(e)}")
            raise Exception(f"Failed to get document info: {str(e)}")
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all its chunks.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deletion was successful
        """
        try:
            # Delete chunks first
            await self.vector_store.delete_document_chunks(document_id)
            
            # Delete document metadata
            result = self.supabase.table("documents").delete().eq("id", document_id).execute()
            
            logger.info(f"Deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise Exception(f"Failed to delete document: {str(e)}")
    
    async def test_all_connections(self) -> Dict[str, bool]:
        """
        Test all service connections.
        
        Returns:
            Dictionary with connection test results
        """
        results = {}
        
        try:
            # Test database connection
            results["database"] = await self.vector_store.test_connection()
        except Exception as e:
            results["database"] = False
            logger.error(f"Database connection test failed: {str(e)}")
        
        try:
            # Test Gemini connection
            results["gemini"] = await self.gemini_client.test_connection()
        except Exception as e:
            results["gemini"] = False
            logger.error(f"Gemini connection test failed: {str(e)}")
        
        return results 