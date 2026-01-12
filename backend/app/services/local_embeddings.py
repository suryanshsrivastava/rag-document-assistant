"""Local embeddings service using sentence-transformers."""

import os
from typing import List
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class LocalEmbeddings:
    """Service for local embedding generation using sentence-transformers."""

    def __init__(self, model_name: str = None):
        """Initialize with a sentence-transformer model name."""
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
        self._model = None
        self._embedding_dim = None
        logger.info(f"Local embeddings service initialized with model: {self.model_name}")

    def _load_model(self):
        """Lazy load the embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                
                logger.info(f"Loading embedding model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                self._embedding_dim = self._model.get_sentence_embedding_dimension()
                logger.info(f"Model loaded. Embedding dimension: {self._embedding_dim}")
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for local embeddings. "
                    "Install with: pip install sentence-transformers"
                )
        return self._model

    @property
    def embedding_dim(self) -> int:
        """Get the embedding dimension of the model."""
        if self._embedding_dim is None:
            self._load_model()
        return self._embedding_dim

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        try:
            model = self._load_model()
            embeddings = model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 10,
                normalize_embeddings=True,
            )
            embeddings_list = [emb.tolist() for emb in embeddings]
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings_list

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise Exception(f"Embedding generation failed: {str(e)}")

    async def test_connection(self) -> bool:
        """Test embedding model loading."""
        try:
            model = self._load_model()
            test_embedding = model.encode(["test"], convert_to_numpy=True)
            logger.info(f"Local embeddings test successful. Dimension: {len(test_embedding[0])}")
            return True
        except Exception as e:
            logger.error(f"Local embeddings test failed: {str(e)}")
            return False
