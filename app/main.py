from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from app.core.limiter import limiter
from app.core.config import settings
from app.core.logging_config import setup_logging, setup_access_logging, get_logger
from app.api.endpoints import router as api_router
from time import time

setup_logging(level="INFO", log_file="app.log", console_output=True)
logger = get_logger(__name__)
access_logger = setup_access_logging("access.log")

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.state.limiter = limiter
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc):
    logger.warning(f"Rate limit exceeded for IP: {get_remote_address(request)}")
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded. Maximum 5 requests per minute per IP. {exc.detail}"}
    )

@app.middleware("http")
async def logging_middleware(request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    client_ip = request.client.host if request.client else "unknown"
    access_logger.info(
        f"{client_ip} - {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Time: {process_time:.3f}s"
    )
    return response
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME}...")
    logger.info(f"API Version: {settings.API_V1_STR}")
    logger.info(f"Pinecone Index: {settings.PINECONE_INDEX_NAME}")
    try:
        from app.db.vector_store import vector_store
        logger.info(f"Vector Store initialized successfully")
        logger.info(f"Embedding Model: {settings.EMBEDDING_MODEL}")
    except Exception as e:
        logger.error(f"Failed to initialize Vector Store: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.APP_NAME}...")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Firas Personal AI Backend",
        "docs": "/docs",
        "version": "1.0.0"
    }


