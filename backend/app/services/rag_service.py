"""RAG service orchestrating document processing, embedding, and retrieval."""

import uuid
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .document_processor import DocumentProcessor
from .chunking_service import ChunkingService
from .local_vector_store import LocalVectorStore
from .local_embeddings import LocalEmbeddings
from .llm_provider import LLMProviderFactory, LLMProvider
from .llm_base import BaseLLMClient

logger = __import__("logging").getLogger(__name__)


class RAGService:
    """Main RAG orchestration service with local storage."""

    def __init__(self):
        """Initialize RAG service with local storage."""
        self.document_processor = None
        self.chunking_service = None
        self.llm_client: Optional[BaseLLMClient] = None
        self.embeddings_client = None
        self.vector_store = None
        self._initialized = False

        backend_dir = Path(__file__).parent.parent.parent
        self.metadata_dir = backend_dir / "document_metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        logger.info("RAG service initialized with local storage")

    def _initialize_components(self):
        """Lazy initialization of service components."""
        if self._initialized:
            return

        try:
            self.document_processor = DocumentProcessor()
            self.chunking_service = ChunkingService()
            self.llm_client = LLMProviderFactory.get_client()
            self.embeddings_client = LocalEmbeddings()
            backend_dir = Path(__file__).parent.parent.parent
            self.vector_store = LocalVectorStore(
                persist_directory=str(backend_dir / "faiss_db"),
                embedding_dim=self.embeddings_client.embedding_dim
            )
            self._initialized = True
            logger.info(f"RAG components initialized with LLM: {self.llm_client.provider_name}")

        except Exception as e:
            logger.error(f"Failed to initialize RAG components: {str(e)}")
            self._initialized = True
            raise

    def _ensure_initialized(self):
        """Ensure service components are initialized."""
        if not self._initialized:
            self._initialize_components()

    def switch_llm_provider(self, provider: LLMProvider) -> Dict[str, Any]:
        """Switch the LLM provider."""
        try:
            self._ensure_initialized()
            self.llm_client = LLMProviderFactory.switch_provider(provider)
            logger.info(f"Switched to: {provider.value}")
            return {
                "success": True,
                "provider": provider.value,
                "provider_name": self.llm_client.provider_name,
            }
        except Exception as e:
            logger.error(f"Failed to switch LLM provider: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_current_llm_provider(self) -> Dict[str, Any]:
        """Get information about the current LLM provider."""
        self._ensure_initialized()
        current = LLMProviderFactory.get_current_provider()
        return {
            "provider": current.value if current else None,
            "provider_name": self.llm_client.provider_name if self.llm_client else None,
        }

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available LLM providers."""
        return LLMProviderFactory.get_available_providers()

    async def process_document(self, file) -> Dict[str, Any]:
        """Process a document through complete RAG pipeline."""
        try:
            self._ensure_initialized()

            processed_doc = await self.document_processor.process_document(file)
            chunks = self.chunking_service.chunk_text(
                processed_doc["text_content"], processed_doc["file_id"]
            )

            chunk_texts = [chunk["chunk_text"] for chunk in chunks]
            embeddings = await self.embeddings_client.generate_embeddings(chunk_texts)

            document_id = str(uuid.uuid4())
            await self._store_document_metadata(document_id, processed_doc, len(chunks))
            await self.vector_store.store_document_chunks(document_id, chunks, embeddings)

            logger.info(f"Document processed: {document_id}")
            return {
                "document_id": document_id,
                "filename": processed_doc["filename"],
                "status": "processed",
                "chunks_created": len(chunks),
                "file_size": processed_doc["metadata"]["file_size"],
                "word_count": processed_doc["metadata"].get("word_count", 0),
            }

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise Exception(f"Document processing failed: {str(e)}")

    async def chat_with_documents(
        self,
        user_message: str,
        document_ids: Optional[List[str]] = None,
        conversation_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Chat with documents using RAG."""
        try:
            self._ensure_initialized()

            query_embeddings = await self.embeddings_client.generate_embeddings([user_message])
            query_embedding = query_embeddings[0]

            similar_chunks = await self.vector_store.search_similar_chunks(
                query_embedding, document_ids, limit=5
            )

            response = await self.llm_client.generate_rag_response(
                user_message, similar_chunks, conversation_history
            )

            if not conversation_id:
                conversation_id = str(uuid.uuid4())

            return {
                "response": response,
                "sources": similar_chunks,
                "conversation_id": conversation_id,
                "message_id": str(uuid.uuid4()),
                "llm_provider": self.llm_client.provider_name,
            }

        except Exception as e:
            logger.error(f"Error in RAG chat: {str(e)}")
            raise Exception(f"RAG chat failed: {str(e)}")

    async def _store_document_metadata(
        self, document_id: str, processed_doc: Dict[str, Any], chunk_count: int
    ) -> None:
        """Store document metadata in local JSON file."""
        try:
            metadata = {
                "id": document_id,
                "filename": processed_doc.get("filename") or "Unknown",
                "file_type": processed_doc["metadata"].get("content_type", "unknown"),
                "file_size": processed_doc["metadata"]["file_size"],
                "word_count": processed_doc["metadata"].get("word_count", 0),
                "chunk_count": chunk_count,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            metadata_path = self.metadata_dir / f"{document_id}.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

        except Exception as e:
            logger.error(f"Error storing metadata: {str(e)}")
            raise Exception(f"Failed to store document metadata: {str(e)}")

    async def _load_document_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Load document metadata from local JSON file."""
        try:
            metadata_path = self.metadata_dir / f"{document_id}.json"
            if not metadata_path.exists():
                return None
            with open(metadata_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata: {str(e)}")
            return None

    async def get_document_info(self, document_id: str) -> Dict[str, Any]:
        """Get document information and statistics."""
        try:
            self._ensure_initialized()
            metadata = await self._load_document_metadata(document_id)
            if not metadata:
                raise Exception(f"Document {document_id} not found")
            return metadata
        except Exception as e:
            logger.error(f"Error getting document info: {str(e)}")
            raise Exception(f"Failed to get document info: {str(e)}")

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its associated data."""
        try:
            self._ensure_initialized()
            await self.vector_store.delete_document_chunks(document_id)

            metadata_path = self.metadata_dir / f"{document_id}.json"
            if metadata_path.exists():
                metadata_path.unlink()

            logger.info(f"Document deleted: {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False

    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents from local storage."""
        try:
            self._ensure_initialized()
            documents = []

            for metadata_file in self.metadata_dir.glob("*.json"):
                try:
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                        documents.append({
                            "id": metadata["id"],
                            "filename": metadata["filename"],
                            "upload_date": metadata["created_at"],
                            "status": "processed",
                            "page_count": None,
                            "word_count": metadata.get("word_count"),
                            "file_size": metadata.get("file_size", 0),
                        })
                except Exception as e:
                    logger.error(f"Error loading {metadata_file}: {str(e)}")
                    continue

            documents.sort(key=lambda x: x["upload_date"], reverse=True)
            return documents

        except Exception as e:
            logger.error(f"Error getting documents: {str(e)}")
            raise Exception(f"Failed to get documents: {str(e)}")

    async def test_all_connections(self) -> Dict[str, bool]:
        """Test all service connections."""
        try:
            self._ensure_initialized()
            return {
                "database": True,
                "llm": await self.llm_client.test_connection() if self.llm_client else False,
                "embeddings": await self.embeddings_client.test_connection(),
                "vector_store": await self.vector_store.test_connection(),
            }
        except Exception as e:
            logger.error(f"Error testing connections: {str(e)}")
            return {"database": False, "llm": False, "vector_store": False}
