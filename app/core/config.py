from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application Config
    APP_NAME: str = "Firas Personal AI Backend"
    API_V1_STR: str = "/api/v1"

    # Pinecone Config
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str  
    PINECONE_INDEX_NAME: str = "firas-portfolio"
    
    # LLM & Embedding Config
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"
    OPENROUTER_API_KEY: str
    
    # Redis Cache Config
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_ENABLED: bool = True
    REDIS_TTL: int = 3600  # Cache TTL in seconds (1 hour)
    
    # Cache Settings
    CACHE_TTL: int = 86400  # 24 hours in seconds
    CACHE_SIMILARITY_THRESHOLD: float = 0.95
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
