# Personal AI Assistant - Project Implementation Plan

## Project Overview
**Goal**: Build a RAG-powered personal AI assistant capable of answering questions about Firas Yazid’s professional background (experience, projects, skills, education).
**Tech Stack**: 
- **Backend**: FastAPI
- **Database**: ChromaDB (Vector Store)
- **Embeddings**: SentenceTransformers
- **LLM**: Free LLM API (OpenRouter or FreeFlow)
- **Deployment**: Docker, Render

---

## Phase 1: Environment Setup & Foundation
**Objective**: specific the project structure and install dependencies.
- [ ] Initialize Python project (Poetry or pip/venv).
- [x] Create directory structure:
  ```
  Backend-RAG/
  ├── app/
  │   ├── core/          # Config configurations
  │   ├── db/            # Database logic (ChromaDB)
  │   ├── services/      # RAG logic (Ingestion, Retrieval, LLM)
  │   ├── api/           # API routes
  │   └── main.py        # App entry point
  ├── data/              # Raw text data (CVs, etc.)
  └── requirements.txt
  ```
- [ ] Install Core Dependencies: `fastapi`, `uvicorn`, `chromadb`, `sentence-transformers`, `python-dotenv`, `requests` (or `httpx`).

## Phase 2: RAG Core - Ingestion & Retrieval
**Objective**: Build the system to store and retrieve personal data.
- [ ] **Data Preparation**: Collect Firas Yazid’s data (Markdown or plain text files) in the `data/` folder.
- [ ] **Chunking Logic**: Implement a utility to split text (e.g., by paragraph or character count) to ensure context fits in the LLM window.
- [ ] **Embedding Service**: Initialize `SentenceTransformers` to create vector embeddings from text chunks.
- [ ] **Vector Store Setup**: 
  - Configure ChromaDB client.
  - specific a collection.
- [ ] **Ingestion Script**: Create a script designed to load data, chunk it, embed it, and save it to ChromaDB.
- [ ] **Search Verification**: Write a test script to query ChromaDB and ensure relevant context is returned.

## Phase 3: LLM Integration & Logic
**Objective**: Connect the retrieval system to a Generative AI model.
- [ ] **LLM Provider Setup**: Get API keys for OpenRouter or chosen free provider.
- [ ] **Prompt Engineering**: Design a system prompt that instructs the AI to answer specifically based on the provided context.
  - *Format*: "You are an assistant. Answer based on this context: {context}. Question: {question}"
- [ ] **RAG Pipeline Implementation**: 
  - Function: `generate_response(query)`
  - Step 1: Embed query.
  - Step 2: Retrieve top-k documents from ChromaDB.
  - Step 3: Construct prompt.
  - Step 4: Call LLM API.
  - Step 5: Return answer.

## Phase 4: REST API with FastAPI
**Objective**: Expose the RAG logic via HTTP endpoints.
- [ ] **Setup FastAPI App**: Initialize `app` in `main.py`.
- [ ] **Endpoints**:
  - `POST /api/v1/chat`: Accepts JSON `{ "question": "..." }`, returns `{ "answer": "...", "sources": [...] }`.
  - `GET /health`: Returns service status.
- [ ] **CORS Middleware**: Allow requests from frontend/local origins.
- [ ] **Request Validation**: Use Pydantic models for input/output validation.

## Phase 5: Containerization
**Objective**: Package the application for consistent deployment.
- [ ] **Dockerfile**: Create a multi-stage Docker build for python environment.
- [ ] **Docker Compose**: Setup `docker-compose.yml` to define the service and volume config for ChromaDB persistence.
- [ ] **Testing**: Verify the container runs locally and API is accessible.

## Phase 6: Production Deployment (Render)
**Objective**: Deploy the API live.
- [ ] **Render Configuration**: Create a Web Service on Render.
- [ ] **Environment Variables**: secure API keys and configs in Render dashboard.
- [ ] **Storage Strategy**: Determine if using Render Disk for ChromaDB persistence or re-ingesting on startup (if using free tier without disks).
- [ ] **Live Test**: Verify the public endpoint.

## Phase 7: Optimization & Extras (Optional)
**Objective**: Enhance performance and maintainability.
- [ ] **LangChain Integration**: Refactor manual RAG steps to use LangChain chains if complexity grows.
- [ ] **Advanced Retrieval**: Implement hybrid search or re-ranking if accuracy needs improvement.
- [ ] **Conversational Memory**: Add history support so users can ask follow-up questions.
