"""
Lazy-loading embedding service to reduce memory footprint on startup.
Only loads the SentenceTransformer model when first needed.
"""

from typing import Optional, List
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class LazyEmbeddingService:
    """
    Lazy-loads the embedding model only when first needed.
    Saves ~300MB of RAM on app startup for Render's 512MB limit.
    """
    
    def __init__(self):
        """Initialize without loading the model."""
        self.model = None
        self.model_name = settings.EMBEDDING_MODEL
        logger.info(f"LazyEmbeddingService initialized (model not loaded yet)")
    
    def _ensure_loaded(self):
        """Load model only on first use."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
    
    def encode(self, text: str) -> List[float]:
        """
        Encode a document chunk to embeddings.
        Loads model on first call.
        """
        self._ensure_loaded()
        return self.model.encode(text).tolist()

    def encode_query(self, text: str) -> List[float]:
        """
        Encode a search query to embeddings.
        BGE models require a special prefix for query text (not for documents).
        Loads model on first call.
        """
        self._ensure_loaded()
        prefixed = f"Represent this sentence for searching relevant passages: {text}"
        return self.model.encode(prefixed).tolist()
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Encode multiple texts to embeddings.
        Loads model on first call.
        """
        self._ensure_loaded()
        return self.model.encode(texts).tolist()


# Global instance - lazy loads on first use
embedding_service = LazyEmbeddingService()
