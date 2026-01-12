"""Abstract base interface for LLM providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the LLM provider."""
        pass

    @abstractmethod
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 1024,
        stop_sequences: Optional[list] = None,
    ) -> str:
        """Generate chat completion from messages with optional context."""
        pass

    @abstractmethod
    async def generate_rag_response(
        self,
        user_message: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Generate RAG response using retrieved context chunks."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test LLM API connection."""
        pass

    def _prepare_context_from_chunks(self, chunks: List[Dict[str, Any]]) -> str:
        """Prepare context string from document chunks."""
        if not chunks:
            return ""

        context_parts = []
        for i, chunk in enumerate(chunks):
            chunk_text = chunk.get("chunk_text", "")
            document_id = chunk.get("metadata", {}).get("document_id", "Unknown")
            context_part = f"Document {document_id}, Chunk {i + 1}:\n{chunk_text}\n"
            context_parts.append(context_part)

        return "\n".join(context_parts)
