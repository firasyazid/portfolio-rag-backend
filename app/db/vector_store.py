from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class VectorStore:
    def __init__(self):
        logger.info("Initializing Vector Store...")
        
        # 1. Initialize Pinecone
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.index = self.pc.Index(self.index_name)
        
        # 2. Initialize Embedding Model 
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
    
    def embed_text(self, text: str) -> List[float]:
        """Generates a vector embedding for a document chunk."""
        return self.model.encode(text).tolist()

    def embed_query(self, query: str) -> List[float]:
        """Generates a vector embedding for a search query.
        BGE models require a special prefix for query text (not for documents).
        """
        prefixed = f"Represent this sentence for searching relevant passages: {query}"
        return self.model.encode(prefixed).tolist()

    def upsert_chunks(self, chunks: List[Dict]):
        """
        Takes a list of chunks (from chunking service), embeds them, 
        and accepts them into Pinecone.
        """
        vectors = []
        logger.info(f"Embedding {len(chunks)} chunks...")
        
        for chunk in chunks:
            vector = self.embed_text(chunk['text'])
            vectors.append({
                "id": chunk['id'],
                "values": vector,
                "metadata": {
                    "text": chunk['text'],
                    **chunk['metadata']
                }
            })
            
        # Upsert in batches of 100 to be safe
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            logger.info(f"Upserting batch {i} to {i+len(batch)}")
            self.index.upsert(vectors=batch)
            
        logger.info("Upsert complete.")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Embeds the query and searches Pinecone.
        Returns matches with full metadata for RAG context building.
        """
        query_vector = self.embed_query(query)
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        
        matches = []
        for match in results['matches']:
            matches.append({
                "score": match['score'],
                "text": match['metadata'].get('text', ''),
                "source": match['metadata'].get('source', ''),
                "header": match['metadata'].get('header', 'N/A'),
                "header_level": match['metadata'].get('header_level', ''),
                "section_type": match['metadata'].get('section_type', '')
            })
        return matches

# Singleton instance
vector_store = VectorStore()
