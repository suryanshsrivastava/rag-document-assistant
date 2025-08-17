"""
Gemini Client Service for RAG System

Handles Google Gemini API interactions for embeddings and chat completions.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv
import logging
from .constants import GEMINI_EMBEDDING_MODEL, GEMINI_EMBEDDING_DIM, GEMINI_CHAT_MODEL, GENERATION_TEMPERATURE, MAX_OUTPUT_TOKENS, STOP_SEQUENCES
# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GeminiClient:
    """Service for Google Gemini API interactions."""
    EMBEDDING_DIM = GEMINI_EMBEDDING_DIM  # Use constant
    
    def __init__(self):
        """Initialize Gemini client with API key."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        self.client = genai.Client(api_key=self.api_key)
        
        # Initialize models
        self.embedding_model = GEMINI_EMBEDDING_MODEL  # Use constant
        self.chat_model = GEMINI_CHAT_MODEL  # Use constant
        
        logger.info(f"Gemini client initialized for {self.EMBEDDING_DIM}-dim embeddings")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            
            # Process in batches to handle rate limits
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Generate embeddings using Gemini
                batch_embeddings = []
                
                for text in batch:
                    # Use the correct API call for embedding generation
                    result = self.client.models.embed_content(
                        model=self.embedding_model,
                        contents=text,
                        config={'output_dimensionality': 1536},
                    )
                    batch_embeddings.append(result.embeddings[0].values)
                
                embeddings.extend(batch_embeddings)
                
                # Add delay between batches to respect rate limits
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
        max_output_tokens: int = MAX_OUTPUT_TOKENS,
        stop_sequences: list = STOP_SEQUENCES
    ) -> str:
        """
        Generate chat completion with optional context.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            context: Optional context to prepend to the conversation
            temperature: Sampling temperature for response generation
            
        Returns:
            Generated response text
        """
        try:
            # Initialize Gemini model
            chat = self.client.chats.create(
                model=self.chat_model,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_output_tokens,
                    "stop_sequences": stop_sequences
                },
                history=[]
            )
        
            
            # Add context if provided
            if context:
                system_message = f"You are a helpful AI assistant. Use the following context to answer questions: {context}"
                # Add system message to conversation
                chat.send_message(system_message)
            
            # Add user messages
            for message in messages:
                if message["role"] == "user":
                    response = chat.send_message(
                        message["content"],
                        config={
                            "temperature": temperature,
                            "max_output_tokens": max_output_tokens,
                            "stop_sequences": stop_sequences
                        }
                    )
                    return response.text
            
            # If no user message found, use the last message
            if messages:
                last_message = messages[-1]["content"]
                response = chat.send_message(
                    last_message,
                    config={
                        "temperature": temperature,
                        "max_output_tokens": max_output_tokens,
                        "stop_sequences": stop_sequences
                    }
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
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate RAG response using retrieved context.
        
        Args:
            user_message: User's question or message
            context_chunks: List of relevant document chunks
            conversation_history: Optional conversation history
            
        Returns:
            Generated response with context
        """
        try:
            # Prepare context from chunks
            context_text = self._prepare_context_from_chunks(context_chunks)
            
            # Prepare messages
            messages = []
            
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Generate response with context
            response = await self.generate_chat_completion(
                messages=messages,
                context=context_text,
                temperature=GENERATION_TEMPERATURE,
                max_output_tokens=MAX_OUTPUT_TOKENS,
                stop_sequences=STOP_SEQUENCES
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            raise Exception(f"RAG response generation failed: {str(e)}")
    
    def _prepare_context_from_chunks(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Prepare context string from document chunks.
        
        Args:
            chunks: List of document chunks with text and metadata
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return ""
        
        context_parts = []
        for i, chunk in enumerate(chunks):
            chunk_text = chunk.get("chunk_text", "")
            document_id = chunk.get("metadata", {}).get("document_id", "Unknown")
            
            context_part = f"Document {document_id}, Chunk {i+1}:\n{chunk_text}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    async def test_connection(self) -> bool:
        """
        Test Gemini API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple test by generating a small embedding
            test_text = "test"
            result = genai.embed_content(
                model=self.embedding_model,
                content=test_text
            )
            return True
        except Exception as e:
            logger.error(f"Gemini connection test failed: {str(e)}")
            return False 

# Test function to check embedding dimension
async def test_embedding_dimension():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    test_text = "test embedding dimension"
    result = genai.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        content=test_text
    )
    embedding = result['embedding']
    print(f"Test embedding length: {len(embedding)}")
    return len(embedding) 