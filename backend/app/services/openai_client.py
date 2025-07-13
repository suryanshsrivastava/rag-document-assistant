"""
OpenAI Client Service for RAG System

Handles OpenAI API interactions for embeddings and chat completions.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Service for OpenAI API interactions."""
    
    def __init__(self):
        """Initialize OpenAI client with API key."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.embedding_model = "text-embedding-3-small"
        self.chat_model = "gpt-4"
        
        logger.info("OpenAI client initialized successfully")
    
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
                
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )
                
                batch_embeddings = [embedding.embedding for embedding in response.data]
                embeddings.extend(batch_embeddings)
                
                # Add delay between batches to respect rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise Exception(f"Embedding generation failed: {str(e)}")
    
    async def generate_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        context: Optional[str] = None,
        temperature: float = 0.7
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
            # Prepare messages with context if provided
            prepared_messages = []
            
            if context:
                system_message = {
                    "role": "system",
                    "content": f"You are a helpful AI assistant. Use the following context to answer questions: {context}"
                }
                prepared_messages.append(system_message)
            
            prepared_messages.extend(messages)
            
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=prepared_messages,
                temperature=temperature,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            logger.info("Generated chat completion successfully")
            
            return response_text
            
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
                temperature=0.7
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
        Test OpenAI API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple test with a short text
            test_embeddings = await self.generate_embeddings(["test"])
            return len(test_embeddings) > 0
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {str(e)}")
            return False 