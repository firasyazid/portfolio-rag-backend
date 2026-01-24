"""
Request and Response models for API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="User query (1-5000 characters)")
    history: Optional[List[Dict[str, str]]] = Field(default=[], description="Conversation history (max 10 messages)")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty or only whitespace')
        return v.strip()
    
    @validator('history')
    def validate_history(cls, v):
        if not v:
            return v
        if len(v) > 10:
            raise ValueError('History limited to 10 messages maximum')
        for item in v:
            if 'role' not in item or 'content' not in item:
                raise ValueError('Each history item must have "role" and "content" keys')
            if item['role'] not in ['user', 'assistant']:
                raise ValueError('Role must be "user" or "assistant"')
            if not item['content'] or len(item['content']) > 5000:
                raise ValueError('Content must be 1-5000 characters')
        return v


class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]


class IngestResponse(BaseModel):
    status: str
    total_files: int
    total_chunks: int
    message: str


__all__ = ['SearchRequest', 'ChatRequest', 'ChatResponse', 'IngestResponse']
