"""Local Vector Store Service - FAISS-based vector storage and similarity search."""

import os
import json
import uuid
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from .constants import N_RESULTS, MINIMUM_SCORE

logger = logging.getLogger(__name__)


class LocalVectorStore:
    """Service for vector storage and similarity search using FAISS."""

    def __init__(
        self, persist_directory: str = "./faiss_db", embedding_dim: int = 1536
    ):
        """Initialize vector store with FAISS."""
        self.persist_directory = persist_directory
        self.embedding_dim = embedding_dim
        self.index_path = os.path.join(persist_directory, "index.faiss")
        self.metadata_path = os.path.join(persist_directory, "metadata.json")

        os.makedirs(persist_directory, exist_ok=True)

        self._index = None
        self._metadata = {}  # chunk_id -> metadata (includes document_id)
        self._doc_chunks = {}  # document_id -> list of chunk_ids

        self._load_index()
        logger.info(f"FAISS vector store initialized at {persist_directory}")

    def _load_index(self):
        """Load index and metadata from disk if they exist."""
        try:
            if os.path.exists(self.index_path):
                self._index = faiss.read_index(self.index_path)
                logger.info(f"Loaded FAISS index with {self._index.ntotal} vectors")

            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, "r") as f:
                    data = json.load(f)
                    self._metadata = data.get("metadata", {})
                    self._doc_chunks = data.get("doc_chunks", {})
                logger.info(f"Loaded metadata for {len(self._metadata)} chunks")
        except Exception as e:
            logger.warning(f"Could not load existing index: {e}")

    def _save_index(self):
        """Save index and metadata to disk."""
        try:
            if self._index is not None:
                faiss.write_index(self._index, self.index_path)

            data = {
                "metadata": self._metadata,
                "doc_chunks": self._doc_chunks,
            }
            with open(self.metadata_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info("Index and metadata saved")
        except Exception as e:
            logger.error(f"Error saving index: {e}")

    async def store_document_chunks(
        self,
        document_id: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> bool:
        """Store document chunks with their embeddings."""
        if not chunks:
            return True

        embeddings_array = np.array(embeddings).astype("float32")

        if self._index is None:
            self._index = faiss.IndexFlatL2(self.embedding_dim)

        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = str(uuid.uuid4())

            self._metadata[chunk_id] = {
                "document_id": document_id,
                "chunk_index": chunk["chunk_index"],
                "chunk_text": chunk["chunk_text"],
                "created_at": datetime.utcnow().isoformat(),
                **chunk.get("metadata", {}),
            }

            if document_id not in self._doc_chunks:
                self._doc_chunks[document_id] = []
            self._doc_chunks[document_id].append(chunk_id)

        self._index.add(embeddings_array)
        self._save_index()

        logger.info(f"Stored {len(chunks)} chunks for document {document_id}")
        return True

    async def search_similar_chunks(
        self,
        query_embedding: List[float],
        document_ids: Optional[List[str]] = None,
        limit: int = N_RESULTS,
        similarity_threshold: float = MINIMUM_SCORE,
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks using vector similarity."""
        if self._index is None or self._index.ntotal == 0:
            logger.warning("Index is empty")
            return []

        query_array = np.array([query_embedding]).astype("float32")

        if limit > self._index.ntotal:
            limit = self._index.ntotal

        distances, indices = self._index.search(query_array, limit)

        similar_chunks = []
        chunk_ids = list(self._metadata.keys())

        for distance, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(chunk_ids):
                continue

            chunk_id = chunk_ids[idx]
            chunk_meta = self._metadata.get(chunk_id, {})
            chunk_doc_id = chunk_meta.get("document_id")

            if document_ids and chunk_doc_id not in document_ids:
                continue

            similarity_score = 1.0 / (1.0 + distance / 100.0)

            if similarity_score >= similarity_threshold:
                similar_chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": chunk_doc_id or "unknown",
                    "chunk_text": chunk_meta.get("chunk_text", ""),
                    "chunk_index": chunk_meta.get("chunk_index", 0),
                    "metadata": {
                        k: v for k, v in chunk_meta.items() if k != "chunk_text"
                    },
                    "similarity_score": similarity_score,
                })

        logger.info(f"Found {len(similar_chunks)} similar chunks above threshold")
        return similar_chunks

    async def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Retrieve all chunks for a specific document."""
        chunk_ids = self._doc_chunks.get(document_id, [])

        chunks = []
        for chunk_id in chunk_ids:
            chunk_meta = self._metadata.get(chunk_id, {})
            chunks.append({
                "chunk_id": chunk_id,
                "chunk_text": chunk_meta.get("chunk_text", ""),
                "chunk_index": chunk_meta.get("chunk_index", 0),
                "metadata": {
                    k: v for k, v in chunk_meta.items() if k != "chunk_text"
                },
            })

        chunks.sort(key=lambda x: x["chunk_index"])
        logger.info(f"Retrieved {len(chunks)} chunks for document {document_id}")
        return chunks

    async def delete_document_chunks(self, document_id: str) -> bool:
        """Delete all chunks for a document (metadata only, index unchanged)."""
        chunk_ids = self._doc_chunks.get(document_id, [])

        if not chunk_ids:
            logger.warning(f"No chunks found for document {document_id}")
            return True

        for chunk_id in chunk_ids:
            self._metadata.pop(chunk_id, None)

        self._doc_chunks.pop(document_id, None)
        self._save_index()

        logger.info(f"Deleted {len(chunk_ids)} chunks for document {document_id}")
        return True

    async def get_chunk_statistics(self, document_id: str) -> Dict[str, Any]:
        """Get statistics about chunks for a document."""
        chunks = await self.get_document_chunks(document_id)

        if not chunks:
            return {"total_chunks": 0, "total_characters": 0, "average_chunk_size": 0}

        total_chunks = len(chunks)
        total_characters = sum(len(chunk["chunk_text"]) for chunk in chunks)
        average_chunk_size = total_characters / total_chunks if total_chunks > 0 else 0

        return {
            "total_chunks": total_chunks,
            "total_characters": total_characters,
            "average_chunk_size": average_chunk_size,
        }

    async def test_connection(self) -> bool:
        """Test vector store connection."""
        try:
            count = self._index.ntotal if self._index else 0
            logger.info(f"Vector store connection test successful. Total chunks: {count}")
            return True
        except Exception as e:
            logger.error(f"Vector store connection test failed: {e}")
            return False

    def get_all_document_ids(self) -> List[str]:
        """Get all unique document IDs in the vector store."""
        return list(self._doc_chunks.keys())

    def delete_all(self) -> bool:
        """Delete all data from the vector store."""
        try:
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)

            self._index = None
            self._metadata = {}
            self._doc_chunks = {}

            logger.warning("All data deleted from vector store")
            return True
        except Exception as e:
            logger.error(f"Error deleting all data: {e}")
            return False
