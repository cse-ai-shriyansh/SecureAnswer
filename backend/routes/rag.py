"""
RAG API Routes - Retrieval-Augmented Generation endpoints
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import JSONResponse
import time
import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

# Import models (relative imports)
from ..models.rag_schemas import (
    QueryRequest, AnswerRequest, DocumentUploadRequest,
    RetrievalResult, ChunkResult, AnswerResponse, RAGStats, HealthCheckResponse
)

# Import services (relative imports)
from ..services.retrieval_service import RetrieverService
from ..services.generation_service import GenerationService

router = APIRouter(prefix="/api/rag", tags=["RAG"])

# Initialize services (these would be initialized once at startup)
_retriever_service = None
_generator_service = None

def get_retriever():
    """Get or initialize retriever service"""
    global _retriever_service
    if _retriever_service is None:
        data_dir = Path(__file__).parent.parent.parent  # Root directory
        _retriever_service = RetrieverService(data_dir=str(data_dir))
    return _retriever_service

def get_generator():
    """Get or initialize generator service"""
    global _generator_service
    if _generator_service is None:
        _generator_service = GenerationService()
    return _generator_service

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@router.get("/health", response_model=HealthCheckResponse)
async def rag_health_check():
    """Check RAG system health"""
    try:
        retriever = get_retriever()
        generator = get_generator()
        
        return HealthCheckResponse(
            status="healthy",
            faiss_index_loaded=retriever.index is not None,
            supabase_connected=True,  # TODO: Actually check Supabase
            embedding_model_loaded=retriever.embedding_model is not None,
            llm_available=generator.provider is not None,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/stats", response_model=RAGStats)
async def rag_stats():
    """Get RAG system statistics"""
    try:
        retriever = get_retriever()
        
        return RAGStats(
            total_chunks=retriever.index.ntotal if retriever.index else 0,
            total_documents=1,  # TODO: Calculate from metadata
            avg_chunk_size=512,  # TODO: Calculate from actual chunks
            total_queries_processed=retriever.total_queries,
            avg_retrieval_time_ms=sum(retriever.retrieval_times) / len(retriever.retrieval_times) if retriever.retrieval_times else 0,
            avg_generation_time_ms=0,  # TODO: Get from generator
            last_updated=datetime.utcnow().isoformat() + "Z"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# ============================================================================
# RETRIEVAL ENDPOINTS
# ============================================================================

@router.post("/retrieve", response_model=RetrievalResult)
async def retrieve(request: QueryRequest):
    """
    Retrieve relevant chunks for a query using vector search.
    
    - **query**: User search query
    - **top_k**: Number of results to retrieve (1-50)
    - **filters**: Optional metadata filters
    """
    try:
        retriever = get_retriever()
        
        # Perform retrieval
        chunks, search_time_ms = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters
        )
        
        # Format results
        chunk_results = [
            ChunkResult(
                chunk_id=chunk.get("chunk_id", f"chunk-{chunk.get('faiss_idx')}"),
                doc_id=chunk.get("doc_id", "doc-001"),
                text=chunk.get("text", ""),
                source_file=chunk.get("source_file", "unknown"),
                similarity_score=chunk.get("similarity_score", 0.0),
                approval_status=chunk.get("approval_status", "approved"),
                document_version=chunk.get("document_version", 1),
                created_at=chunk.get("created_at")
            )
            for chunk in chunks
        ]
        
        return RetrievalResult(
            query=request.query,
            chunks=chunk_results,
            total_chunks_retrieved=len(chunk_results),
            search_time_ms=search_time_ms
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

# ============================================================================
# GENERATION ENDPOINTS
# ============================================================================

@router.post("/answer", response_model=AnswerResponse)
async def generate_answer(request: AnswerRequest):
    """
    Generate answer using RAG (retrieve + generate).
    
    - **query**: User question
    - **top_k**: Number of context chunks to retrieve
    - **model**: LLM model to use (default: gpt-3.5-turbo)
    """
    try:
        retriever = get_retriever()
        generator = GenerationService(model=request.model)
        
        # Step 1: Retrieve relevant chunks
        chunks, search_time_ms = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters
        )
        
        # Format chunks for generation
        formatted_chunks = [
            {
                "chunk_id": chunk.get("chunk_id", f"chunk-{chunk.get('faiss_idx')}"),
                "text": chunk.get("text", ""),
                "source_file": chunk.get("source_file", "unknown"),
                "similarity_score": chunk.get("similarity_score", 0.0)
            }
            for chunk in chunks
        ]
        
        # Step 2: Generate answer
        generation_result = generator.generate(
            query=request.query,
            context_chunks=formatted_chunks
        )
        
        # Format source chunks
        source_chunks = [
            ChunkResult(
                chunk_id=chunk.get("chunk_id", f"chunk-{chunk.get('faiss_idx')}"),
                doc_id=chunk.get("doc_id", "doc-001"),
                text=chunk.get("text", ""),
                source_file=chunk.get("source_file", "unknown"),
                similarity_score=chunk.get("similarity_score", 0.0),
                approval_status=chunk.get("approval_status", "approved"),
                document_version=chunk.get("document_version", 1)
            )
            for chunk in chunks
        ]
        
        return AnswerResponse(
            answer=generation_result["answer"],
            confidence_score=generation_result["confidence_score"],
            source_chunks=source_chunks,
            model_used=generation_result["model_used"],
            generation_time_ms=generation_result["generation_time_ms"],
            created_at=generation_result["timestamp"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer generation failed: {str(e)}")

# ============================================================================
# BATCH ENDPOINTS
# ============================================================================

@router.post("/batch-retrieve")
async def batch_retrieve(queries: list = Query(..., description="List of queries")):
    """
    Retrieve results for multiple queries.
    
    - **queries**: List of query strings
    """
    try:
        retriever = get_retriever()
        results = []
        
        for query in queries:
            chunks, search_time_ms = retriever.retrieve(
                query=query,
                top_k=5
            )
            results.append({
                "query": query,
                "chunks_retrieved": len(chunks),
                "search_time_ms": search_time_ms
            })
        
        return {"results": results, "total_queries": len(queries)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch retrieval failed: {str(e)}")

# ============================================================================
# DOCUMENT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    source: str = Query(default="manual", description="Document source")
):
    """
    Upload a document for ingestion into knowledge base.
    
    - **file**: Document file (PDF, DOCX, TXT)
    - **source**: Source identifier for the document
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # TODO: Implement document ingestion logic
        # This would involve:
        # 1. Save file temporarily
        # 2. Extract text using appropriate parser
        # 3. Chunk text
        # 4. Generate embeddings
        # 5. Add to FAISS index
        # 6. Store metadata in Supabase
        
        return JSONResponse({
            "status": "processing",
            "filename": file.filename,
            "message": "Document uploaded successfully. Processing started...",
            "source": source
        }, status_code=202)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/documents")
async def list_documents():
    """List all documents in knowledge base"""
    try:
        # TODO: Get from Supabase
        return {
            "documents": [],
            "total_count": 0,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

# ============================================================================
# FEEDBACK ENDPOINTS
# ============================================================================

@router.post("/feedback")
async def submit_feedback(
    query: str = Query(...),
    answer_id: str = Query(...),
    rating: int = Query(..., ge=1, le=5),
    comment: Optional[str] = Query(None)
):
    """
    Submit feedback on generated answer.
    
    - **query**: Original query
    - **answer_id**: ID of the answer
    - **rating**: Rating 1-5
    - **comment**: Optional feedback comment
    """
    try:
        # TODO: Store feedback in Supabase
        return {
            "status": "success",
            "message": "Feedback recorded",
            "feedback_id": f"feedback-{time.time()}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {str(e)}")
