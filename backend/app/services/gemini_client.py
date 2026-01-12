"""Google Gemini client for embeddings and chat completions."""

import os
import asyncio
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging
from .llm_base import BaseLLMClient
from .constants import (
    GEMINI_EMBEDDING_MODEL,
    GEMINI_EMBEDDING_DIM,
    GEMINI_CHAT_MODEL,
    GENERATION_TEMPERATURE,
    MAX_OUTPUT_TOKENS,
    STOP_SEQUENCES,
)

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiClient(BaseLLMClient):
    """Service for Google Gemini API interactions."""

    EMBEDDING_DIM = GEMINI_EMBEDDING_DIM

    def __init__(self):
        """Initialize Gemini client with API key."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        try:
            import google.genai as genai

            self.genai = genai
            self.client = genai.Client(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "google-genai package is required for Gemini. Install with: pip install google-genai"
            )

        self.embedding_model = GEMINI_EMBEDDING_MODEL
        self.chat_model = GEMINI_CHAT_MODEL
        logger.info(
            f"Gemini client initialized for {self.EMBEDDING_DIM}-dim embeddings"
        )

    @property
    def provider_name(self) -> str:
        return "Google Gemini"

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        try:
            embeddings = []
            batch_size = 100

            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                batch_embeddings = []

                for text in batch:
                    result = self.client.models.embed_content(
                        model=self.embedding_model,
                        contents=text,
                        config={"output_dimensionality": 1536},
                    )
                    batch_embeddings.append(result.embeddings[0].values)

                embeddings.extend(batch_embeddings)

                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)

            if embeddings:
                logger.info(f"Embedding length: {len(embeddings[0])}")
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise Exception(f"Embedding generation failed: {str(e)}")

    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
        temperature: float = GENERATION_TEMPERATURE,
        max_tokens: int = MAX_OUTPUT_TOKENS,
        stop_sequences: Optional[list] = None,
    ) -> str:
        """Generate chat completion with optional context."""
        if stop_sequences is None:
            stop_sequences = STOP_SEQUENCES

        try:
            chat = self.client.chats.create(
                model=self.chat_model,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    "stop_sequences": stop_sequences,
                },
                history=[],
            )

            if context:
                system_message = f"You are a helpful AI assistant. Use the following context to answer questions: {context}"
                chat.send_message(system_message)

            for message in messages:
                if message["role"] == "user":
                    response = chat.send_message(
                        message["content"],
                        config={
                            "temperature": temperature,
                            "max_output_tokens": max_tokens,
                            "stop_sequences": stop_sequences,
                        },
                    )
                    return response.text

            if messages:
                last_message = messages[-1]["content"]
                response = chat.send_message(
                    last_message,
                    config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                        "stop_sequences": stop_sequences,
                    },
                )
                return response.text

            return "No message provided"

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
        """Test Gemini API connection."""
        try:
            self.client.models.embed_content(
                model=self.embedding_model, contents="test"
            )
            return True
        except Exception as e:
            logger.error(f"Gemini connection test failed: {str(e)}")
            return False
