"""
RAG System Models and Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ============================================================================
# REQUEST MODELS
# ============================================================================

class QueryRequest(BaseModel):
    """User query request for RAG"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to retrieve")
    filters: Optional[dict] = Field(None, description="Optional metadata filters")
    
    class Config:
        example = {
            "query": "How do I reset my password?",
            "top_k": 5,
            "filters": {"source_file": "help_docs.pdf"}
        }

class AnswerRequest(BaseModel):
    """Request for generating answer based on retrieved context"""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=50)
    filters: Optional[dict] = None
    model: str = Field(default="gpt-3.5-turbo", description="LLM model to use")
    
    class Config:
        example = {
            "query": "What are the benefits of our product?",
            "top_k": 5,
            "model": "gpt-3.5-turbo"
        }

class DocumentUploadRequest(BaseModel):
    """Request for uploading a document"""
    filename: str = Field(..., description="Document filename")
    source: str = Field(default="manual", description="Document source")
    metadata: Optional[dict] = Field(None, description="Additional metadata")

# ============================================================================
# RESPONSE MODELS
# ============================================================================

class ChunkResult(BaseModel):
    """Retrieved chunk with metadata"""
    chunk_id: str
    doc_id: str
    text: str
    source_file: str
    similarity_score: float
    approval_status: str
    document_version: int
    created_at: Optional[str] = None
    
    class Config:
        example = {
            "chunk_id": "chunk-001",
            "doc_id": "doc-001",
            "text": "This is a relevant chunk of text...",
            "source_file": "guide.pdf",
            "similarity_score": 0.92,
            "approval_status": "approved",
            "document_version": 1
        }

class RetrievalResult(BaseModel):
    """Result from retrieval service"""
    query: str
    chunks: List[ChunkResult]
    total_chunks_retrieved: int
    search_time_ms: float
    
    class Config:
        example = {
            "query": "How do I reset my password?",
            "chunks": [],
            "total_chunks_retrieved": 5,
            "search_time_ms": 45.2
        }

class AnswerResponse(BaseModel):
    """Generated answer with source attribution"""
    answer: str
    confidence_score: Optional[float] = None
    source_chunks: List[ChunkResult]
    model_used: str
    generation_time_ms: float
    created_at: str
    
    class Config:
        example = {
            "answer": "To reset your password, go to the login page and click 'Forgot Password'...",
            "confidence_score": 0.95,
            "source_chunks": [],
            "model_used": "gpt-3.5-turbo",
            "generation_time_ms": 1250.5,
            "created_at": "2026-05-05T10:30:00Z"
        }

class RAGStats(BaseModel):
    """RAG system statistics"""
    total_chunks: int
    total_documents: int
    avg_chunk_size: float
    total_queries_processed: int
    avg_retrieval_time_ms: float
    avg_generation_time_ms: float
    last_updated: str
    
    class Config:
        example = {
            "total_chunks": 1250,
            "total_documents": 45,
            "avg_chunk_size": 512,
            "total_queries_processed": 892,
            "avg_retrieval_time_ms": 50.3,
            "avg_generation_time_ms": 1100.5,
            "last_updated": "2026-05-05T10:30:00Z"
        }

class HealthCheckResponse(BaseModel):
    """RAG system health check"""
    status: str
    faiss_index_loaded: bool
    supabase_connected: bool
    embedding_model_loaded: bool
    llm_available: bool
    timestamp: str
