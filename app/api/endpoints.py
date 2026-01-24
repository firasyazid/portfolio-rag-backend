from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from app.db.vector_store import vector_store
from app.core.config import settings
from app.core.limiter import limiter
from app.services.chunking import chunker
from app.core.logging_config import get_logger
from app.services.rag_service import get_rag_service
from app.services.streaming_service import get_streaming_rag_service
from app.models.api_models import SearchRequest, ChatRequest, ChatResponse, IngestResponse
from app.db.cache import redis_cache
from pathlib import Path
import httpx


def get_limiter():
    """Get limiter from core module."""
    return limiter

router = APIRouter()
logger = get_logger(__name__)

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "pinecone_env": settings.PINECONE_ENVIRONMENT,
        "redis": redis_cache.health_check()
    }

@router.post("/ingest", response_model=IngestResponse)
async def ingest_data_endpoint(background_tasks: BackgroundTasks):
    """
    Ingests all markdown files from data/ directory into Pinecone.
    Runs in background to avoid timeout.
    """
    def ingest_task():
        logger.info("Starting data ingestion...")
        
        # Define data directory
        base_dir = Path(__file__).parent.parent.parent
        data_dir = base_dir / "data"
        
        if not data_dir.exists():
            logger.error(f"Data directory not found at {data_dir}")
            raise FileNotFoundError(f"Data directory not found at {data_dir}")

        try:
            logger.info(f"Checking access to Pinecone index '{vector_store.index_name}'...")
            stats = vector_store.index.describe_index_stats()
            logger.info(f"Index accessible. Current stats: {stats}")
        except Exception as e:
            logger.error(f"Failed to access Pinecone index: {e}")
            raise

        # Iterate over all markdown files
        md_files = list(data_dir.glob("*.md"))
        if not md_files:
            logger.warning("No markdown files found in data directory.")
            return {
                "status": "warning",
                "total_files": 0,
                "total_chunks": 0,
                "message": "No markdown files found in data directory."
            }

        total_chunks = 0
        
        for file_path in md_files:
            logger.info(f"Processing {file_path.name}...")
            
            # Chunk the file
            file_chunks = chunker.process_file(file_path)
            
            if not file_chunks:
                logger.warning(f"No chunks created for {file_path.name}")
                continue
                
            logger.info(f"Generated {len(file_chunks)} chunks for {file_path.name}")
            
            # Upload to Pinecone
            try:
                vector_store.upsert_chunks(file_chunks)
                total_chunks += len(file_chunks)
                logger.info(f"Successfully uploaded chunks for {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to upload chunks for {file_path.name}: {e}")

        logger.info("Ingestion complete!")
        logger.info(f"Total files processed: {len(md_files)}")
        logger.info(f"Total chunks uploaded: {total_chunks}")
        
        return {
            "status": "success",
            "total_files": len(md_files),
            "total_chunks": total_chunks,
            "message": f"Successfully ingested {len(md_files)} files with {total_chunks} chunks"
        }
    
    try:
        background_tasks.add_task(ingest_task)
        return IngestResponse(
            status="processing",
            total_files=0,
            total_chunks=0,
            message="Ingestion started in background. Check logs for progress."
        )
    except Exception as e:
        logger.error(f"Ingest endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_knowledge_base(request: SearchRequest):
    """
    Directly queries the Vector Store. Useful for debugging RAG context.
    """
    try:
        results = vector_store.search(request.query, request.top_k)
        return {"results": results}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("5/minute")
async def chat_endpoint(request: Request, chat_request: ChatRequest):
    """
    Full RAG Pipeline using dependency injection.
    Rate limited to 5 requests per minute per IP.
    """
    try:
        rag_service = get_rag_service()
        result = await rag_service.generate_answer(
            query=chat_request.message,
            top_k=5,
            temperature=0.7
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )

    except Exception as e:
        logger.error(f"Chat pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get cache statistics and metrics.
    Returns memory usage, key count, and cache health.
    """
    try:
        if not redis_cache.enabled or not redis_cache.client:
            return {
                "status": "disabled",
                "message": "Redis caching is disabled"
            }
        
        # Get Redis info
        info = redis_cache.client.info("memory")
        dbsize = redis_cache.client.dbsize()
        tracked_keys = redis_cache.client.scard("cache:keys:set") or 0
        
        return {
            "status": "ok",
            "cache_enabled": redis_cache.enabled,
            "memory": {
                "used_bytes": info.get("used_memory"),
                "used_human": info.get("used_memory_human"),
                "peak_bytes": info.get("used_memory_peak"),
                "evicted_keys": info.get("evicted_keys", 0)
            },
            "keys": {
                "total_db_keys": dbsize,
                "tracked_cache_keys": tracked_keys
            },
            "config": {
                "ttl_seconds": settings.REDIS_TTL,
                "similarity_threshold": settings.CACHE_SIMILARITY_THRESHOLD
            }
        }
    except Exception as e:
        logger.error(f"Cache stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache")
async def flush_cache():
    """
    Flush all cached queries from Redis.
    Useful after updating portfolio data or changing prompts.
    """
    try:
        redis_cache.flushdb()
        return {
            "status": "success",
            "message": "Cache flushed successfully"
        }
    except Exception as e:
        logger.error(f"Cache flush failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
@limiter.limit("5/minute")
async def stream_chat_endpoint(request: Request, chat_request: ChatRequest):
    """
    Streaming RAG Pipeline with input validation.
    Returns server-sent events (JSON lines) with real-time LLM response.
    Rate limited to 5 requests per minute per IP.
    
    Response format:
    - {"type": "sources", "sources": [...]} - Context sources used
    - {"type": "chunk", "content": "..."} - LLM response chunks
    - {"type": "done"} - Stream completed
    - {"type": "error", "message": "..."} - Error occurred
    """
    try:
        streaming_service = get_streaming_rag_service()
        
        async def response_generator():
            async for chunk in streaming_service.stream_answer(
                query=chat_request.message,
                top_k=5,
                temperature=0.7
            ):
                yield chunk
        
        return StreamingResponse(
            response_generator(),
            media_type="application/x-ndjson"  # Newline-delimited JSON
        )
    
    except Exception as e:
        logger.error(f"Streaming chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
