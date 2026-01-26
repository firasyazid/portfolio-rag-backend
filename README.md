---
title: Portfolio RAG Backend
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# RAG-Powered Portfolio AI Backend

A production-ready Retrieval-Augmented Generation (RAG) system that transforms portfolio data into an intelligent, conversational API. Built with FastAPI, Pinecone, and advanced semantic caching.

## Overview

This backend powers an AI assistant that answers questions about a software engineer's portfolio using state-of-the-art RAG architecture. It ingests markdown-formatted resume data, chunks it intelligently, stores it in a vector database, and serves contextual answers through a high-performance API.

## Key Features

### 1. Intelligent Data Ingestion
- **Hierarchical Chunking**: Strategy B implementation that preserves document structure
- **Semantic Segmentation**: Splits content by markdown headers (## and ###) while maintaining context
- **Metadata Enrichment**: Each chunk includes source, header, section type, and word count
- **Batch Processing**: Efficient upload to Pinecone with progress logging

### 2. Semantic Caching
- **Cosine Similarity Matching**: Checks query similarity against cached responses (threshold: 0.95)
- **Redis-Based Storage**: 24-hour TTL with automatic eviction policies
- **Performance Boost**: Sub-second response times for repeated/similar queries
- **Cache Invalidation**: Automatic flush on data re-ingestion

### 3. RAG Pipeline
- **Vector Search**: Pinecone-powered similarity search with sentence-transformers embeddings
- **Context Assembly**: Retrieves top-k relevant chunks and formats them for LLM consumption
- **LLM Integration**: OpenRouter API with support for multiple models (Llama, Mistral, Gemini)
- **Prompt Engineering**: Centralized prompt management with multiple variants (default, concise, technical, recruiter)

### 4. Production-Ready API
- **Rate Limiting**: 5 requests/minute per IP on chat endpoints
- **Input Validation**: Pydantic models with length limits and sanitization
- **Error Handling**: Comprehensive exception handling with detailed logging
- **Health Monitoring**: Redis and Pinecone connection status endpoints
- **CORS Middleware**: Configurable cross-origin resource sharing

### 5. Observability
- **Structured Logging**: Detailed cache hit/miss tracking, LLM call logging, and performance metrics
- **Cache Statistics**: Real-time memory usage, key count, and eviction tracking
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Architecture

```
┌─────────────────┐
│   Client/UI     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│   FastAPI Application           │
│   - Rate Limiting               │
│   - Input Validation            │
│   - CORS Middleware             │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   RAG Service (DI-Based)        │
│   1. Check Semantic Cache       │
│   2. Embed Query                │
│   3. Vector Search (Pinecone)   │
│   4. Build Context              │
│   5. Call LLM (OpenRouter)      │
│   6. Cache Result               │
└────────┬────────────────────────┘
         │
    ┌────┴─────┬──────────────────┐
    ▼          ▼                  ▼
┌────────┐ ┌────────┐      ┌────────────┐
│ Redis  │ │Pinecone│      │ OpenRouter │
│ Cache  │ │ Vector │      │    LLM     │
└────────┘ └────────┘      └────────────┘
```

## Technology Stack

- **Framework**: FastAPI (async Python web framework)
- **Vector Database**: Pinecone (serverless vector search)
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
- **Cache**: Redis (with cosine similarity search)
- **LLM**: OpenRouter API (Llama 3.3 70B Instruct)
- **Rate Limiting**: SlowAPI
- **Validation**: Pydantic v2

## Installation

### Prerequisites
- Python 3.8+
- Pinecone account (free tier available)
- Redis instance (local or cloud)
- OpenRouter API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Backend-RAG
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables (`.env`):
```env
# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX_NAME=firas-portfolio

# OpenRouter
OPENROUTER_API_KEY=your_openrouter_key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=  # Optional
REDIS_ENABLED=true

# Cache Settings
CACHE_TTL=86400
CACHE_SIMILARITY_THRESHOLD=0.95
```

5. Ingest data:
```bash
python ingest.py
```

6. Start the server:
```bash
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Health & Monitoring
- `GET /api/v1/health` - System health check
- `GET /api/v1/cache/stats` - Cache statistics and memory usage

### Data Management
- `POST /api/v1/ingest` - Ingest markdown files into vector database
- `DELETE /api/v1/cache` - Flush all cached queries

### Query
- `POST /api/v1/search` - Direct vector search (debugging)
  ```json
  {
    "query": "What programming languages does Firas know?",
    "top_k": 5
  }
  ```

- `POST /api/v1/chat` - RAG-powered conversational endpoint
  ```json
  {
    "message": "What is Firas's experience with AI?",
    "history": []
  }
  ```
  
  Response:
  ```json
  {
    "answer": "Firas has extensive experience with AI...",
    "sources": [
      {
        "score": 0.89,
        "text": "...",
        "source": "projects.md",
        "header": "AI & Machine Learning Projects"
      }
    ]
  }
  ```

## Project Structure

```
Backend-RAG/
├── app/
│   ├── api/
│   │   └── endpoints.py          # API routes
│   ├── core/
│   │   ├── config.py             # Environment configuration
│   │   └── limiter.py            # Rate limiting setup
│   ├── db/
│   │   ├── vector_store.py       # Pinecone wrapper
│   │   └── cache.py              # Redis client
│   ├── services/
│   │   ├── chunking.py           # Markdown chunker (Strategy B)
│   │   ├── rag_service.py        # Main RAG pipeline
│   │   └── semantic_cache.py     # Cache similarity logic
│   ├── prompts/
│   │   └── system_prompts.py     # Centralized prompt templates
│   └── main.py                   # FastAPI app entry point
├── data/                         # Markdown files (resume, projects, etc.)
├── ingest.py                     # Data ingestion script
├── test_cache.py                 # Cache verification tool
├── requirements.txt
└── .env
```

## Configuration

### Chunking Strategy
- **Method**: Hierarchical (Strategy B)
- **Primary Split**: `##` headers (sections)
- **Secondary Split**: `###` headers (sub-sections)
- **Minimum Chunk Size**: 5 words
- **Metadata**: source, header, header_level, section_type, word_count

### Caching
- **Similarity Algorithm**: Cosine similarity (pure Python implementation)
- **Threshold**: 0.95 (configurable)
- **TTL**: 24 hours (configurable)
- **Eviction Policy**: Least Recently Used (LRU)

### Rate Limiting
- **Chat Endpoints**: 5 requests/minute per IP
- **Search Endpoint**: Unlimited (for debugging)

## Usage Examples

### Test Cache Performance
```bash
python test_cache.py
```

Expected output:
```
[TEST 1] First query - Should MISS cache and call LLM
Response time: 4.23s

[TEST 2] Same query - Should HIT cache
Response time: 0.08s

Cache is working correctly!
```

### Query via curl
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Firas'\''s current role?"}'
```

### Check Cache Stats
```bash
curl http://localhost:8000/api/v1/cache/stats
```

## Performance

- **Cache Hit**: <100ms response time
- **Cache Miss**: 2-10s (LLM dependent)
- **Vector Search**: ~200ms for top-5 similarity search
- **Embedding Generation**: ~50ms per query
- **Total Chunks Stored**: 235 vectors (from 8 markdown files)

## Security Features

- Input validation (max 5000 characters)
- Rate limiting per IP
- Environment-based secrets
- CORS configured for specific origins (update in production)
- No sensitive data in logs

## Deployment Considerations

1. **Environment Variables**: Use secure secret management (AWS Secrets Manager, HashiCorp Vault)
2. **Redis**: Use managed Redis (Upstash, Redis Cloud) for persistence
3. **Pinecone**: Free tier supports 1GB (sufficient for portfolio use)
4. **Scaling**: Stateless design allows horizontal scaling
5. **HTTPS**: Deploy behind reverse proxy (nginx, Caddy) with SSL

## Future Enhancements

- Conversation memory with session tracking
- Multi-language support
- Conversation analytics dashboard
- A/B testing for different prompts
- Vector database migration tools

## License

MIT

## Author

Built by Firas Yazid as a demonstration of production-grade RAG architecture and modern Python API development.

---

**API Documentation**: http://localhost:8000/docs  
**Live Demo**: https://firasyazid.github.io/e-portfolio/