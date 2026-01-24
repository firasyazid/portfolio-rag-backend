---
trigger: always_on
---

1. Code Style & Formatting
PEP 8 Compliance: All Python code must strictly adhere to PEP 8 standards (indentation, naming conventions, imports).

Senior-Level Architecture: Prefer modularity and Decoupling. Use Dependency Injection (e.g., passing the ChromaDB client into services) rather than hardcoding instances.

Type Hinting: Use exhaustive Python type hints (from typing import List, Optional, etc.) for all function signatures and variables.

Pydantic Models: Use Pydantic for all API request/response schemas and internal configuration (BaseSettings).

2. Documentation & Emojis
No Emojis: Do not use emojis in code comments, commit messages, or log strings.

Minimalist Commenting: Do not comment on "what" the code is doing if it is self-explanatory. Use comments only to explain the "why" behind complex logic or specific RAG parameters (like top_k selection).

Docstrings: Use Google-style docstrings for public classes and functions, focusing on parameters and return types.

3. RAG Specific Implementation
Error Handling: Implement robust try-except blocks around LLM API calls and Vector Store queries. Return meaningful HTTP exceptions (404, 503) rather than generic 500 errors.

Environment Safety: Never hardcode API keys. Always use pydantic-settings or python-dotenv to load from .env.

Asynchronous Patterns: Since you are using FastAPI, ensure that all I/O bound tasks (API calls to LLMs, database reads) use async and await with a compatible client (like httpx).