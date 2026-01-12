"""LLM provider factory for managing LM Studio and Gemini clients."""

import os
from enum import Enum
from typing import Optional
from dotenv import load_dotenv
import logging

from .llm_base import BaseLLMClient

load_dotenv()

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    LMSTUDIO = "lmstudio"
    GEMINI = "gemini"


class LLMProviderFactory:
    """Factory for creating and managing LLM clients."""

    _instance: Optional[BaseLLMClient] = None
    _current_provider: Optional[LLMProvider] = None

    @classmethod
    def get_default_provider(cls) -> LLMProvider:
        """Get the default provider from environment."""
        provider_str = os.getenv("LLM_PROVIDER", "lmstudio").lower()
        try:
            return LLMProvider(provider_str)
        except ValueError:
            logger.warning(f"Unknown LLM_PROVIDER '{provider_str}', defaulting to lmstudio")
            return LLMProvider.LMSTUDIO

    @classmethod
    def create_client(cls, provider: Optional[LLMProvider] = None) -> BaseLLMClient:
        """Create an LLM client for the specified provider."""
        if provider is None:
            provider = cls.get_default_provider()

        if provider == LLMProvider.LMSTUDIO:
            from .lmstudio_client import LMStudioClient
            client = LMStudioClient()
            logger.info("Created LM Studio client")
            return client

        elif provider == LLMProvider.GEMINI:
            from .gemini_client import GeminiClient
            client = GeminiClient()
            logger.info("Created Gemini client")
            return client

        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @classmethod
    def get_client(cls, provider: Optional[LLMProvider] = None) -> BaseLLMClient:
        """Get or create an LLM client (singleton pattern per provider)."""
        if provider is None:
            provider = cls.get_default_provider()

        if cls._instance is None or cls._current_provider != provider:
            cls._instance = cls.create_client(provider)
            cls._current_provider = provider

        return cls._instance

    @classmethod
    def switch_provider(cls, provider: LLMProvider) -> BaseLLMClient:
        """Switch to a different LLM provider."""
        logger.info(f"Switching LLM provider to: {provider.value}")
        cls._instance = cls.create_client(provider)
        cls._current_provider = provider
        return cls._instance

    @classmethod
    def get_current_provider(cls) -> Optional[LLMProvider]:
        """Get the currently active provider."""
        return cls._current_provider

    @classmethod
    def get_available_providers(cls) -> list[dict]:
        """Get list of available providers with their configuration status."""
        providers = []

        lmstudio_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
        providers.append({
            "id": LLMProvider.LMSTUDIO.value,
            "name": "LM Studio",
            "description": "Local LLM via LM Studio (OpenAI-compatible API)",
            "configured": bool(lmstudio_url),
            "config": {
                "base_url": lmstudio_url,
                "model": os.getenv("LMSTUDIO_MODEL", "local-model"),
            }
        })

        gemini_key = os.getenv("GEMINI_API_KEY")
        providers.append({
            "id": LLMProvider.GEMINI.value,
            "name": "Google Gemini",
            "description": "Google Gemini API (requires API key)",
            "configured": bool(gemini_key),
            "config": {
                "has_api_key": bool(gemini_key),
            }
        })

        return providers

    @classmethod
    def reset(cls):
        """Reset the factory state."""
        cls._instance = None
        cls._current_provider = None
