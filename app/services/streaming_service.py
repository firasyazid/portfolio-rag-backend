import httpx
import json
from typing import Dict, Any, AsyncGenerator, List, Optional
from app.core.config import settings
from app.db.vector_store import vector_store
from app.prompts import get_rag_system_prompt, get_context_template
from app.core.logging_config import get_logger
from app.services.embedding_service import embedding_service

logger = get_logger(__name__)

class StreamingRAGService:
    """
    Streaming RAG Service for real-time response generation.
    Handles context retrieval and streams LLM responses back to client.
    """
    
    def __init__(
        self,
        vector_store,
        semantic_cache=None,
        llm_model: str = None,
        llm_endpoint: str = "https://openrouter.ai/api/v1/chat/completions",
        api_key: Optional[str] = None
    ):
        """Initialize streaming service with dependencies."""
        self.vector_store = vector_store
        self.semantic_cache = semantic_cache
        self.llm_model = llm_model or settings.LLM_MODEL
        self.llm_endpoint = llm_endpoint
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.embedding_service = embedding_service  # Lazy-loaded
    
    def _build_context(self, results: List[Dict]) -> str:
        """Format retrieval results into context string."""
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
        """Build system prompt with context."""
        return get_rag_system_prompt(context)
    
    async def stream_answer(
        self,
        query: str,
        top_k: int = 5,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        Stream RAG response with context.
        Yields JSON lines with either 'chunk' (content) or 'sources' (metadata).
        
        Args:
            query: User's question
            top_k: Number of context chunks to retrieve
            temperature: LLM temperature
            
        Yields:
            JSON-formatted strings with streaming data
        """
        try:
            # Step 0: Check Semantic Cache
            query_embedding = self.embedding_service.encode(query)
            
            if self.semantic_cache:
                cached_result = self.semantic_cache.check_cache(query_embedding, query)
                if cached_result:
                    logger.info(f"✅ Returning cached answer (similarity: {cached_result.get('similarity', 0):.3f})")
                    # Yield cached sources
                    sources_data = {
                        "type": "sources",
                        "sources": cached_result["sources"],
                        "from_cache": True
                    }
                    yield json.dumps(sources_data) + "\n"
                    
                    # Stream cached answer in chunks
                    answer = cached_result["answer"]
                    chunk_size = 50
                    for i in range(0, len(answer), chunk_size):
                        chunk_data = {
                            "type": "chunk",
                            "content": answer[i:i+chunk_size]
                        }
                        yield json.dumps(chunk_data) + "\n"
                    
                    # Mark as done
                    yield json.dumps({"type": "done"}) + "\n"
                    return
            
            # Step 1: Retrieval
            logger.info(f"Retrieving context for query: {query[:50]}...")
            context_results = self.vector_store.search(query, top_k=top_k)
            
            # Send sources first
            sources_data = {
                "type": "sources",
                "sources": context_results
            }
            yield json.dumps(sources_data) + "\n"
            
            # Step 2: Build context and system prompt
            context_str = self._build_context(context_results)
            system_prompt = self._build_system_prompt(context_str)
            
            # Step 3: Stream from LLM
            logger.info(f"Streaming from LLM: {self.llm_model}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://firas-portfolio.com",
                "X-Title": "Firas Portfolio RAG Stream"
            }
            
            payload = {
                "model": self.llm_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                "temperature": temperature,
                "stream": True  # Enable streaming
            }
            
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    self.llm_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=120.0
                ) as response:
                    if response.status_code != 200:
                        try:
                            error_text = response.text
                        except:
                            error_text = f"HTTP {response.status_code}"
                        logger.error(f"LLM API Error: {error_text[:200]}")
                        yield json.dumps({
                            "type": "error",
                            "message": f"LLM provider error: {error_text[:100]}"
                        }) + "\n"
                        return
                    
                    logger.info("Receiving streaming response from LLM...")
                    
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        
                        # Parse OpenRouter SSE format
                        if line.startswith("data: "):
                            data_str = line[6:]   
                            
                            if data_str == "[DONE]":
                                logger.info("Stream completed")
                                yield json.dumps({"type": "done"}) + "\n"
                                continue
                            
                            try:
                                chunk_data = json.loads(data_str)
                                
                                # Extract content from choice
                                if "choices" in chunk_data and len(chunk_data["choices"]) > 0:
                                    delta = chunk_data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    
                                    if content:
                                        yield json.dumps({
                                            "type": "chunk",
                                            "content": content
                                        }) + "\n"
                                        
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse SSE data: {data_str[:50]}")
                                continue
        
        except Exception as e:
            logger.error(f"Streaming failed: {e}", exc_info=True)
            yield json.dumps({
                "type": "error",
                "message": str(e)
            }) + "\n"


def get_streaming_rag_service():
    """Factory function for dependency injection."""
    from app.services.semantic_cache import get_semantic_cache
    return StreamingRAGService(
        vector_store=vector_store,
        semantic_cache=get_semantic_cache()
    )
