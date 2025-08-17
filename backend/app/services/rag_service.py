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
from ..database.connection import get_supabase_client, is_database_available

logger = logging.getLogger(__name__)

class RAGService:
    """Main RAG orchestration service."""
    
    def __init__(self):
        """Initialize RAG service with lazy loading of components."""
        self.document_processor = None
        self.chunking_service = None
        self.gemini_client = None
        self.vector_store = None
        self.supabase = None
        self._initialized = False
        
        logger.info("RAG service initialized")
    
    def _initialize_components(self):
        """Lazy initialization of service components."""
        if self._initialized:
            return
            
        try:
            # Initialize core services
            self.document_processor = DocumentProcessor()
            self.chunking_service = ChunkingService()
            self.gemini_client = GeminiClient()
            self.vector_store = VectorStore()
            
            # Initialize database connection
            self.supabase = get_supabase_client()
            
            self._initialized = True
            logger.info("RAG service components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service components: {str(e)}")
            self._initialized = True
            raise
    
    def _ensure_initialized(self):
        """Ensure service components are initialized."""
        if not self._initialized:
            self._initialize_components()
    
    async def process_document(self, file) -> Dict[str, Any]:
        """
        Process a document through the complete RAG pipeline.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Dictionary with processing results
        """
        try:
            self._ensure_initialized()
            
            # Check database availability
            if not is_database_available():
                raise Exception("Database is not available. Please check your configuration.")
            
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
            if embeddings:
                logger.info(f"Embedding length: {len(embeddings[0])}")
            
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
            self._ensure_initialized()
            
            # Check database availability
            if not is_database_available():
                raise Exception("Database is not available. Please check your configuration.")
            
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
                # Validate or convert `conversation_id` to UUID
                try:
                    conversation_id = str(uuid.UUID(conversation_id))
                except ValueError:
                    logger.warning(f"Invalid conversation_id format received: {conversation_id}. Generating new UUID.")
                    conversation_id = str(uuid.uuid4())
                
                # Ensure conversation exists
                await self._ensure_conversation_exists(conversation_id)
                
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
            else:
                # Generate a new conversation ID if none provided
                conversation_id = str(uuid.uuid4())
                await self._ensure_conversation_exists(conversation_id)
            
            logger.info("RAG chat completed")
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
            if not self.supabase:
                raise Exception("Database connection not available")
                
            document_id = str(uuid.uuid4())
            document_data = {
                "id": document_id,
                "user_id": "00000000-0000-0000-0000-000000000000",  # Anonymous user for testing
                "title": processed_doc.get("title") or processed_doc.get("filename") or "Untitled Document",
                "content": processed_doc.get("text_content", ""),
                "file_path": processed_doc["file_path"],
                "file_type": processed_doc["metadata"].get("content_type", "unknown"),
                "file_size": processed_doc["metadata"]["file_size"],
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
            if not self.supabase:
                logger.warning("Database not available, skipping status update")
                return False
                
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
            if not self.supabase:
                logger.warning("Database not available, skipping conversation save")
                return str(uuid.uuid4())
                
            message_id = str(uuid.uuid4())
            message_data = {
                "id": message_id,
                "conversation_id": conversation_id,
                "user_id": "00000000-0000-0000-0000-000000000000",
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
    
    async def _ensure_conversation_exists(self, conversation_id: str) -> None:
        """
        Ensure a conversation with the given ID exists in the conversations table.
        If not, insert a new conversation row.
        """
        if not self.supabase:
            logger.warning("Database not available, skipping conversation existence check")
            return
        result = self.supabase.table("conversations").select("id").eq("id", conversation_id).execute()
        if not result.data:
            # Insert new conversation
            self.supabase.table("conversations").insert({
                "id": conversation_id,
                "title": "Chat Session",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
    
    async def get_document_info(self, document_id: str) -> Dict[str, Any]:
        """
        Get document information and statistics.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document information dictionary
        """
        try:
            self._ensure_initialized()
            
            if not self.supabase:
                raise Exception("Database is not available")
                
            result = self.supabase.table("documents").select("*").eq("id", document_id).execute()
            
            if not result.data:
                raise Exception(f"Document {document_id} not found")
                
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error getting document info: {str(e)}")
            raise Exception(f"Failed to get document info: {str(e)}")
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all its associated data.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deletion was successful
        """
        try:
            self._ensure_initialized()
            
            if not self.supabase:
                raise Exception("Database is not available")
            
            # Delete chunks first
            await self.vector_store.delete_document_chunks(document_id)
            
            # Delete document metadata
            result = self.supabase.table("documents").delete().eq("id", document_id).execute()
            
            logger.info(f"Document {document_id} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get all documents from the database.
        
        Returns:
            List of document information dictionaries
        """
        try:
            self._ensure_initialized()
            
            if not self.supabase:
                raise Exception("Database is not available")
                
            result = self.supabase.table("documents").select("*").order("created_at", desc=True).execute()
            
            documents = []
            for doc in result.data:
                documents.append({
                    "id": doc["id"],
                    "filename": doc["filename"],
                    "upload_date": doc["created_at"],
                    "status": doc["status"],
                    "page_count": doc.get("page_count"),
                    "word_count": doc.get("word_count"),
                    "file_size": doc.get("file_size", 0)
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error getting all documents: {str(e)}")
            raise Exception(f"Failed to get documents: {str(e)}")
    
    async def test_all_connections(self) -> Dict[str, bool]:
        """
        Test all service connections.
        
        Returns:
            Dictionary with connection status for each service
        """
        try:
            self._ensure_initialized()
            
            results = {
                "database": is_database_available(),
                "gemini": await self.gemini_client.test_connection(),
                "vector_store": True  # Vector store uses database
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing connections: {str(e)}")
            return {
                "database": False,
                "gemini": False,
                "vector_store": False
            } 