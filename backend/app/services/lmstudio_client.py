"""LM Studio client using OpenAI-compatible API."""

import os
import httpx
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging
from .llm_base import BaseLLMClient
from .constants import (
    GENERATION_TEMPERATURE,
    MAX_OUTPUT_TOKENS,
    STOP_SEQUENCES,
)

load_dotenv()

logger = logging.getLogger(__name__)


class LMStudioClient(BaseLLMClient):
    """Service for LM Studio API interactions."""

    def __init__(self):
        """Initialize LM Studio client."""
        self.base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
        self.model = os.getenv("LMSTUDIO_MODEL", "local-model")
        self.timeout = float(os.getenv("LMSTUDIO_TIMEOUT", "120"))
        logger.info(f"LM Studio client initialized at {self.base_url}")

    @property
    def provider_name(self) -> str:
        return "LM Studio"

    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
        temperature: float = GENERATION_TEMPERATURE,
        max_tokens: int = MAX_OUTPUT_TOKENS,
        stop_sequences: Optional[list] = None,
    ) -> str:
        """Generate chat completion using LM Studio."""
        if stop_sequences is None:
            stop_sequences = STOP_SEQUENCES

        try:
            formatted_messages = []

            if context:
                formatted_messages.append({
                    "role": "system",
                    "content": f"You are a helpful AI assistant. Use the following context to answer questions:\n\n{context}"
                })
            else:
                formatted_messages.append({
                    "role": "system",
                    "content": "You are a helpful AI assistant."
                })

            for message in messages:
                formatted_messages.append({
                    "role": message.get("role", "user"),
                    "content": message.get("content", "")
                })

            payload = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
            }

            if stop_sequences:
                payload["stop"] = stop_sequences

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

            return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Error generating chat completion: {str(e)}")
            raise Exception(f"Chat completion failed: {str(e)}")

    async def generate_rag_response(
        self,
        user_message: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Generate RAG response using retrieved context."""
        try:
            context_text = self._prepare_context_from_chunks(context_chunks)
            messages = []

            if conversation_history:
                messages.extend(conversation_history)

            messages.append({"role": "user", "content": user_message})

            return await self.generate_chat_completion(
                messages=messages,
                context=context_text,
                temperature=GENERATION_TEMPERATURE,
                max_tokens=MAX_OUTPUT_TOKENS,
                stop_sequences=STOP_SEQUENCES,
            )

        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            raise Exception(f"RAG response generation failed: {str(e)}")

    async def test_connection(self) -> bool:
        """Test LM Studio API connection."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/models")
                response.raise_for_status()
                logger.info("LM Studio connection test successful")
                return True
        except Exception as e:
            logger.error(f"LM Studio connection test failed: {str(e)}")
            return False
