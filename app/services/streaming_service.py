import httpx
import json
import asyncio
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
        llm_endpoint: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent",
        api_key: Optional[str] = None
    ):
        """Initialize streaming service with dependencies."""
        self.vector_store = vector_store
        self.semantic_cache = semantic_cache
        self.llm_model = llm_model or settings.LLM_MODEL
        self.llm_endpoint = llm_endpoint
        self.api_key = api_key or settings.GEMINI_API_KEY
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
            
            # Step 3: Stream from LLM with retries
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Streaming from LLM: {self.llm_model} (Attempt {attempt + 1}/{max_retries})")
                    
                    headers = {
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": f"{system_prompt}\n\nUser: {query}"
                            }]
                        }],
                        "generationConfig": {
                            "temperature": temperature,
                            "maxOutputTokens": 2048
                        }
                    }
                    
                    async with httpx.AsyncClient() as client:
                        async with client.stream(
                            "POST",
                            f"{self.llm_endpoint}?key={self.api_key}&alt=sse",
                            headers=headers,
                            json=payload,
                            timeout=120.0
                        ) as response:
                            if response.status_code != 200:
                                try:
                                    error_text = await response.aread()
                                    error_text = error_text.decode()
                                except:
                                    error_text = f"HTTP {response.status_code}"
                                
                                logger.error(f"LLM API Error (Status {response.status_code}): {error_text[:200]}")
                                
                                if attempt < max_retries - 1:
                                    wait_time = 2 ** attempt
                                    logger.warning(f"Retrying streaming in {wait_time}s...")
                                    await asyncio.sleep(wait_time)
                                    continue
                                
                                yield json.dumps({
                                    "type": "error",
                                    "message": "Our system is currently down. Please try again in a few minutes."
                                }) + "\n"
                                return
                            
                            async for line in response.aiter_lines():
                                line = line.strip()
                                if not line:
                                    continue
                                
                                # Process Server-Sent Events (SSE) format
                                if line.startswith("data:"):
                                    json_str = line[5:].strip()
                                    if json_str == "[DONE]":
                                        continue
                                        
                                    try:
                                        chunk_data = json.loads(json_str)
                                        
                                        # Extract content from Gemini response
                                        if "candidates" in chunk_data and len(chunk_data["candidates"]) > 0:
                                            candidate = chunk_data["candidates"][0]
                                            if "content" in candidate and "parts" in candidate["content"]:
                                                parts = candidate["content"]["parts"]
                                                if len(parts) > 0 and "text" in parts[0]:
                                                    content = parts[0]["text"]
                                                    
                                                    if content:
                                                        chunk_output = json.dumps({
                                                            "type": "chunk",
                                                            "content": content
                                                        }) + "\n"
                                                        yield chunk_output
                                                        
                                    except json.JSONDecodeError as e:
                                        logger.warning(f"Failed to parse SSE JSON: {e}")
                                        continue
                                        
                                # Also handle the non-SSE array format just in case
                                # Some Gemini versions might return a JSON array without alt=sse
                                elif line.startswith("{") or line.startswith("[") or line.startswith("},"):
                                    # Fallback simple parsing for non-SSE array format chunks
                                    clean_line = line.strip()
                                    if clean_line.startswith("["): clean_line = clean_line[1:].strip()
                                    if clean_line.endswith("]"): clean_line = clean_line[:-1].strip()
                                    if clean_line.endswith(","): clean_line = clean_line[:-1].strip()
                                    
                                    if clean_line and clean_line.startswith("{") and clean_line.endswith("}"):
                                        try:
                                            chunk_data = json.loads(clean_line)
                                            if "candidates" in chunk_data and len(chunk_data["candidates"]) > 0:
                                                candidate = chunk_data["candidates"][0]
                                                if "content" in candidate and "parts" in candidate["content"]:
                                                    parts = candidate["content"]["parts"]
                                                    if len(parts) > 0 and "text" in parts[0]:
                                                        content = parts[0]["text"]
                                                        if content:
                                                            chunk_output = json.dumps({"type": "chunk", "content": content}) + "\n"
                                                            yield chunk_output
                                        except json.JSONDecodeError:
                                            pass
                            
                            # If we reached here, the stream finished successfully
                            yield json.dumps({"type": "done"}) + "\n"
                            return # Exit the retry loop and the function
                            
                except Exception as e:
                    logger.error(f"Streaming attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        yield json.dumps({
                            "type": "error",
                            "message": "Our system is experiencing connection issues. Please try again in a few minutes."
                        }) + "\n"
                        return
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
        
        except Exception as e:
            logger.error(f"Streaming failed: {e}", exc_info=True)
            yield json.dumps({
                "type": "error",
                "message": "The system encountered an unexpected error. Please try again shortly."
            }) + "\n"


def get_streaming_rag_service():
    """Factory function for dependency injection."""
    from app.services.semantic_cache import get_semantic_cache
    return StreamingRAGService(
        vector_store=vector_store,
        semantic_cache=get_semantic_cache()
    )
