"""
Integration Routes - Bridge between frontend expectations and RAG services
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse
import time
from datetime import datetime
from typing import Optional, List
import os
from pathlib import Path

# Import models (relative imports)
from ..models.rag_schemas import QueryRequest, AnswerRequest

# Import services (relative imports)
from ..services.retrieval_service import RetrieverService
from ..services.generation_service import GenerationService
from ..services.ingestion_service import DocumentIngestionService
from ..services.supabase_service import SupabaseService

router = APIRouter(prefix="/api", tags=["integration"])

# ============================================================================
# SINGLETON SERVICE INSTANCES
# ============================================================================

_retriever = None
_generator = None
_ingester = None
_supabase_service = None

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = RetrieverService()
    return _retriever

def get_generator():
    global _generator
    if _generator is None:
        _generator = GenerationService()
    return _generator

def get_ingester():
    global _ingester
    if _ingester is None:
        _ingester = DocumentIngestionService()
    return _ingester

def get_supabase_service():
    global _supabase_service
    if _supabase_service is None:
        _supabase_service = SupabaseService()
    return _supabase_service

# ============================================================================
# RETRIEVAL ENDPOINT - Frontend compatible
# ============================================================================

@router.post("/retrieval")
async def retrieval(
    query: str = Query(...),
    top_k: int = Query(5),
    use_llm: bool = Query(False)
):
    """
    Retrieval endpoint compatible with frontend expectations.
    
    Returns chunks in format expected by RetrievalDebug.jsx:
    {
        "retrieval_chunks": [
            {
                "doc_id": "doc-001",
                "chunk_id": "chunk-xyz",
                "chunk_text": "...",
                "source_file": "guide.pdf",
                "score": 0.95,
                "combined_score": 0.95
            }
        ]
    }
    """
    try:
        retriever = get_retriever()
        
        # Perform retrieval
        chunks, search_time_ms = retriever.retrieve(
            query=query,
            top_k=top_k
        )
        
        # Format for frontend
        retrieval_chunks = [
            {
                "doc_id": chunk.get("doc_id", "doc-001"),
                "chunk_id": chunk.get("chunk_id", f"chunk-{chunk.get('faiss_idx')}"),
                "chunk_text": chunk.get("text", ""),
                "source_file": chunk.get("source_file", "unknown"),
                "score": chunk.get("similarity_score", 0.0),
                "combined_score": chunk.get("similarity_score", 0.0),
                "rank": chunk.get("rank", 0)
            }
            for chunk in chunks
        ]
        
        return JSONResponse({
            "query": query,
            "retrieval_chunks": retrieval_chunks,
            "context_chunks": retrieval_chunks,
            "total_retrieved": len(retrieval_chunks),
            "search_time_ms": search_time_ms
        }, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

# ============================================================================
# GENERATION ENDPOINT - Frontend compatible
# ============================================================================

@router.post("/generate")
async def generate(
    question: str = Query(...),
    use_llm: bool = Query(True),
    top_k: int = Query(5)
):
    """
    Answer generation endpoint compatible with frontend expectations.
    
    Returns format expected by AnswerGeneration.jsx:
    {
        "answer": "...",
        "confidence": 0.95,
        "generation_mode": "llm",
        "llm_enabled": true,
        "hallucination_risk": false,
        "retrieval_confidence": 0.92,
        "citations": ["doc-001#chunk-xyz"],
        "retrieval_chunks": [...],
        "generation_time_ms": 1250
    }
    """
    try:
        start_time = time.time()
        
        retriever = get_retriever()
        generator = get_generator()
        
        # Step 1: Retrieve context
        chunks, retrieval_time_ms = retriever.retrieve(
            query=question,
            top_k=top_k
        )
        
        # Format chunks for generation
        formatted_chunks = [
            {
                "chunk_id": chunk.get("chunk_id", f"chunk-{chunk.get('faiss_idx')}"),
                "doc_id": chunk.get("doc_id", "doc-001"),
                "text": chunk.get("text", ""),
                "source_file": chunk.get("source_file", "unknown"),
                "similarity_score": chunk.get("similarity_score", 0.0)
            }
            for chunk in chunks
        ]
        
        # Step 2: Generate answer
        if use_llm:
            generation_result = generator.generate(
                query=question,
                context_chunks=formatted_chunks
            )
            answer = generation_result["answer"]
            confidence = generation_result["confidence_score"]
            generation_time_ms = generation_result["generation_time_ms"]
            llm_enabled = generator.provider is not None
        else:
            # Fallback to extractive
            if formatted_chunks:
                answer = formatted_chunks[0]["text"][:300] + "..."
                confidence = 0.7
            else:
                answer = "No relevant information found."
                confidence = 0.3
            generation_time_ms = 0
            llm_enabled = False
        
        # Step 3: Format citations
        citations = [
            f"{chunk.get('doc_id', 'doc-001')}#{chunk.get('chunk_id', 'chunk-0')}"
            for chunk in chunks[:3]  # Top 3 chunks as citations
        ]
        
        # Step 4: Format retrieval chunks for frontend
        retrieval_chunks = [
            {
                "doc_id": chunk.get("doc_id", "doc-001"),
                "chunk_id": chunk.get("chunk_id", f"chunk-{chunk.get('faiss_idx')}"),
                "chunk_text": chunk.get("text", ""),
                "source_file": chunk.get("source_file", "unknown"),
                "score": chunk.get("similarity_score", 0.0),
                "combined_score": chunk.get("similarity_score", 0.0)
            }
            for chunk in chunks
        ]
        
        total_time_ms = (time.time() - start_time) * 1000
        
        return JSONResponse({
            "answer": answer,
            "confidence": confidence,
            "generation_mode": "llm" if use_llm else "extractive",
            "llm_enabled": llm_enabled,
            "hallucination_risk": False,  # TODO: Implement hallucination detection
            "retrieval_confidence": sum(c.get("similarity_score", 0) for c in chunks) / max(len(chunks), 1),
            "citations": citations,
            "retrieval_chunks": retrieval_chunks,
            "generation_time_ms": generation_time_ms,
            "total_time_ms": total_time_ms
        }, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

# ============================================================================
# DASHBOARD ENDPOINTS - Placeholder/stub implementations
# ============================================================================

@router.get("/dashboard")
async def dashboard():
    """Get dashboard statistics"""
    try:
        retriever = get_retriever()
        stats = retriever.get_stats()
        
        return JSONResponse({
            "total_chunks": stats.get("index_size", 0),
            "total_documents": 1,  # TODO: Get from metadata
            "avg_retrieval_time_ms": stats.get("avg_retrieval_time_ms", 0),
            "total_queries": stats.get("total_queries", 0),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity")
async def activity():
    """Get activity logs"""
    return JSONResponse({
        "activities": [],
        "total": 0,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }, status_code=200)

@router.get("/review")
async def review_queue():
    """Get review queue"""
    return JSONResponse({
        "queue": [],
        "total": 0,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }, status_code=200)

@router.post("/review/{answer_id}/approve")
async def approve_answer(answer_id: str):
    """Approve an answer"""
    return JSONResponse({
        "status": "approved",
        "answer_id": answer_id,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }, status_code=200)

@router.post("/review/{answer_id}/reject")
async def reject_answer(answer_id: str):
    """Reject an answer"""
    return JSONResponse({
        "status": "rejected",
        "answer_id": answer_id,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }, status_code=200)

@router.get("/ingestion")
async def ingestion_status():
    """Get ingestion status"""
    try:
        supabase = get_supabase_service()

        if supabase.enabled:
            jobs = supabase.fetch_ingestion_jobs(limit=50)
            completed_count = 0
            failed_count = 0
            pending_count = 0
            files = []

            for job in jobs:
                results = job.get("results") or {}
                raw_status = str(job.get("status") or results.get("status") or "pending").lower()
                if raw_status in {"success", "completed", "done"}:
                    display_status = "completed"
                    completed_count += 1
                elif raw_status in {"failed", "error"}:
                    display_status = "failed"
                    failed_count += 1
                else:
                    display_status = "processing"
                    pending_count += 1

                file_name = results.get("file_name") or results.get("filename") or job.get("id") or "unknown"
                file_size = results.get("file_size")
                if isinstance(file_size, (int, float)):
                    size_label = f"{file_size / (1024 * 1024):.2f} MB"
                elif file_size:
                    size_label = str(file_size)
                else:
                    size_label = "-"

                document_count = results.get("document_count") or results.get("chunks_created") or 0
                files.append({
                    "id": job.get("id"),
                    "name": file_name,
                    "size": size_label,
                    "type": Path(file_name).suffix.lstrip(".").upper() or "FILE",
                    "status": display_status,
                    "documents": document_count,
                    "uploadedAt": job.get("created_at") or job.get("updated_at") or datetime.utcnow().isoformat() + "Z",
                })

            stats = [
                {
                    "label": "Completed",
                    "value": completed_count,
                    "change": "Live",
                    "changeType": "positive",
                    "footer": "Finished ingestion jobs",
                },
                {
                    "label": "Processing",
                    "value": pending_count,
                    "change": "Live",
                    "changeType": "neutral",
                    "footer": "Queued or running jobs",
                },
                {
                    "label": "Failed",
                    "value": failed_count,
                    "change": "Live",
                    "changeType": "negative",
                    "footer": "Jobs that need attention",
                },
            ]

            return JSONResponse({
                "status": "ready",
                "processed": completed_count,
                "failed": failed_count,
                "stats": stats,
                "files": files,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }, status_code=200)

    except Exception as e:
        print(f"Warning: ingestion status fallback due to error: {e}")

    return JSONResponse({
        "status": "ready",
        "processed": 0,
        "failed": 0,
        "stats": [],
        "files": [],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }, status_code=200)

@router.post("/ingestion/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload document for ingestion"""
    tmp_path = None
    try:
        ingester = get_ingester()
        
        # Save temporary file
        import tempfile
        suffix = Path(file.filename).suffix.lower() if file.filename else ""
        if suffix not in {".pdf", ".docx", ".xlsx", ".txt"}:
            suffix = ".txt"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Ingest
        result = ingester.ingest_file(tmp_path, source="upload")

        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        return JSONResponse({
            "status": result["status"],
            "filename": file.filename,
            "chunks_created": result.get("chunks_created", 0),
            "message": result.get("message", "Uploaded successfully")
        }, status_code=200 if result["status"] == "success" else 400)
    
    except Exception as e:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/validation")
async def validation():
    """Get validation results"""
    return JSONResponse({
        "validations": [],
        "total": 0,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }, status_code=200)

@router.get("/kb")
async def knowledge_base(q: str = Query("")):
    """Get knowledge base entries"""
    retriever = get_retriever()
    
    if q:
        chunks, _ = retriever.retrieve(query=q, top_k=10)
        kb_items = [
            {
                "id": chunk.get("chunk_id", ""),
                "title": chunk.get("source_file", ""),
                "content": chunk.get("text", ""),
                "score": chunk.get("similarity_score", 0)
            }
            for chunk in chunks
        ]
    else:
        kb_items = []
    
    return JSONResponse({
        "items": kb_items,
        "total": len(kb_items),
        "query": q
    }, status_code=200)

@router.get("/freshness")
async def freshness():
    """Get document freshness metrics"""
    return JSONResponse({
        "documents": [],
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }, status_code=200)

@router.get("/answers")
async def answers(q: str = Query(""), limit: int = Query(10)):
    """Get answers"""
    return JSONResponse({
        "answers": [],
        "total": 0,
        "query": q
    }, status_code=200)

@router.get("/answers/library")
async def answers_library(q: str = Query("")):
    """Get answer library"""
    return JSONResponse({
        "answers": [],
        "total": 0,
        "query": q
    }, status_code=200)

@router.get("/insights")
async def insights():
    """Get insights"""
    return JSONResponse({
        "insights": [],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }, status_code=200)

@router.get("/exports")
async def exports():
    """Get exports"""
    return JSONResponse({
        "exports": [],
        "total": 0
    }, status_code=200)

@router.post("/exports")
async def create_export(payload: dict):
    """Create export"""
    return JSONResponse({
        "export_id": "export-123",
        "status": "queued",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }, status_code=202)
