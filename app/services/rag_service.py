import httpx
import asyncio
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class RAGService:
    """
    Retrieval-Augmented Generation Service.
    Handles the complete RAG pipeline: Retrieval -> Context Building -> LLM Generation.
    
    Uses Dependency Injection for better testability and modularity.
    """
    
    def __init__(
        self, 
        vector_store,
        semantic_cache=None,
        llm_model: str = None,
        llm_endpoint: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        api_key: Optional[str] = None
    ):
        """
        Initialize RAG Service with injected dependencies.
        
        Args:
            vector_store: Vector database instance (e.g., Pinecone wrapper)
            semantic_cache: Semantic cache instance (optional)
            llm_model: Gemini model identifier (defaults from settings)
            llm_endpoint: LLM API endpoint
            api_key: Gemini API key (defaults to settings)
        """
        self.vector_store = vector_store
        self.semantic_cache = semantic_cache
        self.llm_model = llm_model or settings.LLM_MODEL
        self.llm_endpoint = llm_endpoint
        self.api_key = api_key or settings.GEMINI_API_KEY
    
    async def generate_answer(
        self, 
        query: str, 
        top_k: int = 5,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline with semantic caching.
        
        Args:
            query: User's question
            top_k: Number of context chunks to retrieve
            temperature: LLM temperature (0-1)
            
        Returns:
            Dict with 'answer' and 'sources'
        """
        # Step 0: Check Semantic Cache
        if self.semantic_cache:
            query_embedding = self.vector_store.embed_query(query)
            cached_result = self.semantic_cache.check_cache(query_embedding, query)
            
            if cached_result:
                logger.info(
                    f"[RAG CACHE HIT] Returning cached answer | "
                    f"Similarity: {cached_result.get('similarity', 0):.4f}"
                )
                return {
                    "answer": cached_result["answer"],
                    "sources": cached_result["sources"]
                }
        
        # Step 1: Retrieval
        logger.info(f"Retrieving top {top_k} contexts for query: {query[:50]}...")
        context_results = self.vector_store.search(query, top_k=top_k)
        
        # Step 2: Build Context String
        context_str = self._build_context(context_results)
        
        # Step 3: Build System Prompt
        system_prompt = self._build_system_prompt(context_str)
        
        # Step 4: Call LLM
        logger.info(f"Calling LLM: {self.llm_model}")
        answer = await self._call_llm(system_prompt, query, temperature)
        
        logger.info(f"Generated answer ({len(answer)} chars)")
        
        # Step 5: Cache the result
        if self.semantic_cache:
            query_embedding = self.vector_store.embed_query(query)
            self.semantic_cache.set_cache(query_embedding, query, answer, context_results)
        
        return {
            "answer": answer,
            "sources": context_results
        }
    
    def _build_context(self, results: List[Dict]) -> str:
        """Format retrieval results into a context string."""
        from app.prompts import get_context_template
        
        template = get_context_template()
        context_parts = []
        
        for res in results:
            context_parts.append(
                template.format(
                    source=res['source'],
                    header=res.get('header', 'N/A'),
                    text=res['text']
                )
            )
        return "\n".join(context_parts)
    
    def _build_system_prompt(self, context: str) -> str:
        """Build the system prompt with context using centralized prompts."""
        from app.prompts import get_rag_system_prompt
        return get_rag_system_prompt(context)
    
    async def _call_llm(
        self, 
        system_prompt: str, 
        user_message: str,
        temperature: float
    ) -> str:
        """Call Google Gemini LLM API with retries."""
        
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    headers = {
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": f"{system_prompt}\n\nUser: {user_message}"
                            }]
                        }],
                        "generationConfig": {
                            "temperature": temperature,
                            "maxOutputTokens": 2048
                        }
                    }
                    
                    logger.info(f"Calling Gemini with model: {self.llm_model} (Attempt {attempt + 1}/{max_retries})")
                    
                    response = await client.post(
                        f"{self.llm_endpoint}?key={self.api_key}",
                        headers=headers,
                        json=payload,
                        timeout=60.0
                    )
                    
                    if response.status_code != 200:
                        error_text = response.text[:200]
                        logger.error(f"LLM API Error (Status {response.status_code}): {error_text}")
                        # If it's the last attempt, raise the error
                        if attempt == max_retries - 1:
                            raise Exception(f"LLM provider error after {max_retries} attempts: {error_text}")
                        
                        # Otherwise, wait and retry (exponential backoff)
                        wait_time = 2 ** attempt
                        logger.warning(f"Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                        
                    llm_data = response.json()
                    answer = llm_data["candidates"][0]["content"]["parts"][0]["text"]
                    return answer
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise e
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

def get_rag_service():
    """
    Factory function for dependency injection.
    Creates RAG service with injected vector store and semantic cache.
    """
    from app.db.vector_store import vector_store
    from app.services.semantic_cache import get_semantic_cache
    
    semantic_cache = get_semantic_cache()
    return RAGService(vector_store=vector_store, semantic_cache=semantic_cache)

