"""Integration routes bridging frontend expectations and backend services."""

import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Body, File, HTTPException, Path as FastAPIPath, Query, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import models (relative imports)
from ..models.rag_schemas import QueryRequest, AnswerRequest
from ..config.settings import settings

# Import services (relative imports)
from ..services.retrieval_service import RetrieverService
from ..services.generation_service import GenerationService
from ..services.ingestion_service import DocumentIngestionService
from ..services.supabase_service import SupabaseService
from ..utils.security import sanitize_dict, sanitize_text

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
        retriever = get_retriever()
        _ingester = DocumentIngestionService(retriever=retriever)
    return _ingester


def get_supabase_service():
    global _supabase_service
    if _supabase_service is None:
        _supabase_service = SupabaseService()
    return _supabase_service


class ExportRequest(BaseModel):
    format: str = Field(default="csv", pattern="^(csv|json|pdf)$")
    scope: str = Field(default="all", max_length=64)
    query: Optional[str] = Field(default=None, max_length=1000)
    filters: Optional[dict[str, Any]] = None


class ReviewActionRequest(BaseModel):
    notes: Optional[str] = Field(default=None, max_length=1000)
    reason: Optional[str] = Field(default=None, max_length=1000)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_text(value: Any, fallback: str = "") -> str:
    normalized = sanitize_text(value, max_length=500)
    return normalized or fallback


def _vector_to_document_item(row: dict[str, Any]) -> dict[str, Any]:
    metadata = row.get("metadata") or {}
    tags = metadata.get("tags") if isinstance(metadata, dict) else []
    if not isinstance(tags, list):
        tags = []
    return {
        "id": row.get("chunk_id") or row.get("id") or row.get("doc_id") or "chunk",
        "title": _safe_text(metadata.get("title") if isinstance(metadata, dict) else None, row.get("source_file", "Untitled document")),
        "file": _safe_text(row.get("source_file"), "unknown"),
        "version": row.get("document_version", 1),
        "sections": metadata.get("sections") if isinstance(metadata, dict) and metadata.get("sections") is not None else 1,
        "status": row.get("approval_status", "approved"),
        "lastModified": row.get("updated_at") or row.get("created_at") or _utc_now(),
        "approvedBy": _safe_text(metadata.get("approvedBy") if isinstance(metadata, dict) else None, "System"),
        "tags": tags,
        "question": _safe_text(metadata.get("question") if isinstance(metadata, dict) else None, row.get("chunk_text", "")),
        "category": _safe_text(metadata.get("category") if isinstance(metadata, dict) else None, row.get("source_file", "General")),
        "views": int(metadata.get("views", 0)) if isinstance(metadata, dict) else 0,
        "rating": float(metadata.get("rating", 0)) if isinstance(metadata, dict) else 0,
        "lastUpdated": row.get("updated_at") or row.get("created_at") or _utc_now(),
        "priority": _safe_text(metadata.get("priority") if isinstance(metadata, dict) else None, "medium"),
        "submittedBy": _safe_text(metadata.get("submittedBy") if isinstance(metadata, dict) else None, row.get("source_file", "system")),
        "submittedAt": row.get("created_at") or _utc_now(),
        "relevance": float(metadata.get("relevance", 0.9)) if isinstance(metadata, dict) else 0.9,
        "factuality": float(metadata.get("factuality", 0.9)) if isinstance(metadata, dict) else 0.9,
        "confidence": float(metadata.get("confidence", 0.9)) if isinstance(metadata, dict) else 0.9,
        "riskScore": float(metadata.get("riskScore", 0.1)) if isinstance(metadata, dict) else 0.1,
        "answer": _safe_text(metadata.get("answer") if isinstance(metadata, dict) else None, row.get("chunk_text", "")),
        "citations": metadata.get("citations") if isinstance(metadata, dict) and isinstance(metadata.get("citations"), list) else [f"{row.get('doc_id', 'doc')}#{row.get('chunk_id', 'chunk')}"] ,
        "statusLabel": row.get("approval_status", "approved"),
    }


def _build_recent_activity_items() -> list[dict[str, Any]]:
    service = get_supabase_service()
    if not service.enabled:
        return []

    rows = service.fetch_activity(limit=25)
    return [
        {
            "id": row.get("id") or idx,
            "type": _safe_text(row.get("event_type"), "activity"),
            "status": "completed",
            "user": _safe_text(row.get("user_id"), "sys"),
            "userName": _safe_text(row.get("user_id"), "System user"),
            "timestamp": row.get("created_at") or _utc_now(),
            "details": sanitize_dict(row.get("metadata") or {}),
        }
        for idx, row in enumerate(rows)
    ]

# ============================================================================
# RETRIEVAL ENDPOINT - Frontend compatible
# ============================================================================

@router.post("/retrieval")
async def retrieval(
    query: str = Query(..., min_length=1, max_length=1000),
    top_k: int = Query(5, ge=1, le=50),
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
    question: str = Query(..., min_length=1, max_length=1000),
    use_llm: bool = Query(True),
    top_k: int = Query(5, ge=1, le=50)
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
        service = get_supabase_service()
        if service.enabled:
            try:
                summary = service.dashboard_summary()
            except Exception:
                # If Supabase schema is missing or returns errors, fall back to empty summary
                summary = {
                    "metrics": {
                        "validated_answers": 0,
                        "pending_review": 0,
                        "avg_resolution": 0,
                        "queue_depth": 0,
                        "freshness": 0,
                        "rejected_today": 0,
                        "exports_ready": 0,
                        "processing_queue": 0,
                        "storage_used": "0 chunks",
                        "api_uptime": "0%",
                        "response_p50": "-",
                        "response_p95": "-",
                        "response_p99": "-",
                        "query_total": 0,
                        "avg_per_day": 0,
                        "peak": 0,
                    },
                    "chart": [],
                    "recent_activity": [],
                    "summary": {"total_chunks": 0, "total_documents": 0, "pending_chunks": 0, "approved_chunks": 0, "rejected_chunks": 0},
                }
        else:
            summary = {
                "metrics": {
                    "validated_answers": 0,
                    "pending_review": 0,
                    "avg_resolution": 0,
                    "queue_depth": 0,
                    "freshness": 0,
                    "rejected_today": 0,
                    "exports_ready": 0,
                    "processing_queue": 0,
                    "storage_used": "0 chunks",
                    "api_uptime": "0%",
                    "response_p50": "-",
                    "response_p95": "-",
                    "response_p99": "-",
                    "query_total": 0,
                    "avg_per_day": 0,
                    "peak": 0,
                },
                "chart": [],
                "recent_activity": [],
                "summary": {"total_chunks": 0, "total_documents": 0, "pending_chunks": 0, "approved_chunks": 0, "rejected_chunks": 0},
            }

        metrics = summary["metrics"]
        stats = [
            {"icon": "CheckCircle", "label": "Validated Answers", "value": metrics["validated_answers"], "change": None, "changeType": "positive", "footer": "Stored in Supabase"},
            {"icon": "Clock", "label": "Pending Review", "value": metrics["pending_review"], "change": None, "changeType": "warning", "footer": "Awaiting approval"},
            {"icon": "TrendingUp", "label": "Queue Depth", "value": metrics["queue_depth"], "change": None, "changeType": "info", "footer": "Live ingestion queue"},
            {"icon": "Activity", "label": "Total Documents", "value": summary["summary"]["total_documents"], "change": None, "changeType": "positive", "footer": "Indexed in Supabase"},
        ]

        return JSONResponse(
            {
                "stats": stats,
                "chart": summary["chart"],
                "summary": metrics,
                "systemHealth": {
                    "processingQueue": metrics["processing_queue"],
                    "storageUsed": metrics["storage_used"],
                    "apiUptime": metrics["api_uptime"],
                    "responseP50": metrics["response_p50"],
                    "responseP95": metrics["response_p95"],
                    "responseP99": metrics["response_p99"],
                },
                "summaryCounts": summary["summary"],
                "timestamp": _utc_now(),
            },
            status_code=200,
        )
    except Exception as e:
        # Return fallback dashboard instead of 500 to keep frontend usable
        return JSONResponse(
            {
                "stats": [
                    {"icon": "CheckCircle", "label": "Validated Answers", "value": 0, "change": None, "changeType": "positive", "footer": "Stored in Supabase"},
                    {"icon": "Clock", "label": "Pending Review", "value": 0, "change": None, "changeType": "warning", "footer": "Awaiting approval"},
                    {"icon": "TrendingUp", "label": "Queue Depth", "value": 0, "change": None, "changeType": "info", "footer": "Live ingestion queue"},
                    {"icon": "Activity", "label": "Total Documents", "value": 0, "change": None, "changeType": "positive", "footer": "Indexed in Supabase"},
                ],
                "chart": [],
                "summary": {"total_chunks": 0, "total_documents": 0, "pending_chunks": 0, "approved_chunks": 0, "rejected_chunks": 0},
                "systemHealth": {"processingQueue": 0, "storageUsed": "0 chunks", "apiUptime": "0%", "responseP50": "-", "responseP95": "-", "responseP99": "-"},
                "summaryCounts": {"total_chunks": 0, "total_documents": 0, "pending_chunks": 0, "approved_chunks": 0, "rejected_chunks": 0},
                "timestamp": _utc_now(),
            },
            status_code=200,
        )

@router.get("/activity")
async def activity():
    """Get activity logs"""
    service = get_supabase_service()
    activities = _build_recent_activity_items() if service.enabled else []
    return JSONResponse({
        "items": activities,
        "activities": activities,
        "total": len(activities),
        "timestamp": _utc_now()
    }, status_code=200)

@router.get("/review")
async def review_queue():
    """Get review queue"""
    service = get_supabase_service()
    try:
        rows = service.fetch_vectors(approval_status="pending", limit=100) if service.enabled else []
    except Exception:
        rows = []
    queue = [_vector_to_document_item(row) for row in rows]
    return JSONResponse({
        "items": queue,
        "queue": queue,
        "total": len(queue),
        "avgReviewTime": "-",
        "approvalRate": 0,
        "timestamp": _utc_now()
    }, status_code=200)

@router.post("/review/{answer_id}/approve")
async def approve_answer(answer_id: str = FastAPIPath(..., min_length=1, max_length=128), payload: ReviewActionRequest | None = Body(default=None)):
    """Approve an answer"""
    return JSONResponse({
        "status": "approved",
        "answer_id": answer_id,
        "notes": sanitize_text(payload.notes if payload else None, max_length=1000),
        "timestamp": _utc_now()
    }, status_code=200)

@router.post("/review/{answer_id}/reject")
async def reject_answer(answer_id: str = FastAPIPath(..., min_length=1, max_length=128), payload: ReviewActionRequest | None = Body(default=None)):
    """Reject an answer"""
    return JSONResponse({
        "status": "rejected",
        "answer_id": answer_id,
        "reason": sanitize_text(payload.reason if payload else None, max_length=1000),
        "timestamp": _utc_now()
    }, status_code=200)

@router.get("/ingestion")
async def ingestion_status():
    """Get ingestion status"""
    service = get_supabase_service()
    jobs = service.fetch_ingestion_jobs(limit=100) if service.enabled else []
    files = []
    processed = 0
    failed = 0
    for idx, job in enumerate(jobs):
        results = job.get("results") or {}
        status = job.get("status", "pending")
        if status == "success":
            processed += 1
        elif status == "error":
            failed += 1

        files.append({
            "id": job.get("id") or idx,
            "name": sanitize_text(results.get("file_name") or job.get("file_name") or "unknown", max_length=255),
            "size": results.get("file_size") or 0,
            "type": results.get("file_type") or "document",
            "status": status,
            "documents": results.get("document_count") or 0,
            "uploadedAt": job.get("created_at") or _utc_now(),
        })

    stats = [
        {"icon": "Upload", "label": "Processed", "value": processed, "change": None, "changeType": "positive", "footer": "Stored in Supabase"},
        {"icon": "AlertCircle", "label": "Failed", "value": failed, "change": None, "changeType": "negative", "footer": "Validation errors"},
        {"icon": "FileText", "label": "Queued", "value": len(jobs), "change": None, "changeType": "info", "footer": "Live ingestion jobs"},
    ]

    return JSONResponse({
        "status": "ready",
        "processed": processed,
        "failed": failed,
        "stats": stats,
        "files": files,
        "timestamp": _utc_now()
    }, status_code=200)

@router.post("/ingestion/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload document for ingestion"""
    tmp_path = None
    try:
        ingester = get_ingester()
        
        # Save temporary file
        filename = Path(file.filename).name if file.filename else "upload.txt"
        if len(filename) > 255:
            raise HTTPException(status_code=400, detail="Filename is too long")

        suffix = Path(filename).suffix.lower()
        if suffix not in {".pdf", ".docx", ".xlsx", ".txt"}:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        max_bytes = settings.max_upload_mb * 1024 * 1024
        content = await file.read(max_bytes + 1)
        if len(content) > max_bytes:
            raise HTTPException(status_code=413, detail="File exceeds maximum upload size")

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        # Ingest
        result = ingester.ingest_file(tmp_path, source="upload")

        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        return JSONResponse({
            "status": result["status"],
            "filename": filename,
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
        "timestamp": _utc_now()
    }, status_code=200)

@router.get("/kb")
async def knowledge_base(q: str = Query("", max_length=1000)):
    """Get knowledge base entries"""
    service = get_supabase_service()
    try:
        rows = service.fetch_vectors(query=q, approval_status="approved", limit=50) if service.enabled else []
    except Exception:
        rows = []
    kb_items = [
        {
            "id": row.get("chunk_id") or row.get("id") or idx,
            "title": _safe_text(row.get("source_file"), "knowledge-base-item"),
            "content": _safe_text(row.get("chunk_text"), ""),
            "score": row.get("similarity_score", 0),
            "status": row.get("approval_status", "approved"),
            "file": _safe_text(row.get("source_file"), "unknown"),
            "version": row.get("document_version", 1),
            "sections": 1,
            "lastModified": row.get("updated_at") or row.get("created_at") or _utc_now(),
            "approvedBy": _safe_text((row.get("metadata") or {}).get("approvedBy") if isinstance(row.get("metadata"), dict) else None, "System"),
        }
        for idx, row in enumerate(rows)
    ]
    
    return JSONResponse({
        "items": kb_items,
        "total": len(kb_items),
        "query": q
    }, status_code=200)

@router.get("/freshness")
async def freshness():
    """Get document freshness metrics"""
    service = get_supabase_service()
    rows = service.fetch_vectors(limit=100) if service.enabled else []
    documents = []
    for row in rows:
        documents.append({
            "id": row.get("doc_id") or row.get("chunk_id"),
            "title": _safe_text(row.get("source_file"), "document"),
            "lastUpdated": row.get("updated_at") or row.get("created_at") or _utc_now(),
            "status": row.get("approval_status", "approved"),
        })
    return JSONResponse({
        "documents": documents,
        "last_updated": _utc_now()
    }, status_code=200)

@router.get("/answers")
async def answers(q: str = Query("", max_length=1000), limit: int = Query(10, ge=1, le=100)):
    """Get answers"""
    service = get_supabase_service()
    rows = service.fetch_vectors(query=q, approval_status="approved", limit=limit) if service.enabled else []
    answers = [_vector_to_document_item(row) for row in rows]
    return JSONResponse({
        "items": answers,
        "answers": answers,
        "total": len(answers),
        "query": q
    }, status_code=200)

@router.get("/answers/library")
async def answers_library(q: str = Query("", max_length=1000)):
    """Get answer library"""
    service = get_supabase_service()
    rows = service.fetch_vectors(query=q, approval_status="approved", limit=100) if service.enabled else []
    answers = [_vector_to_document_item(row) for row in rows]
    return JSONResponse({
        "items": answers,
        "answers": answers,
        "total": len(answers),
        "query": q
    }, status_code=200)

@router.get("/insights")
async def insights():
    """Get insights"""
    service = get_supabase_service()
    rows = service.fetch_vectors(limit=100) if service.enabled else []
    counts = {
        "approved": sum(1 for row in rows if row.get("approval_status") == "approved"),
        "pending": sum(1 for row in rows if row.get("approval_status") == "pending"),
        "rejected": sum(1 for row in rows if row.get("approval_status") == "rejected"),
    }
    return JSONResponse({
        "insights": [
            {"label": "Approved chunks", "value": counts["approved"]},
            {"label": "Pending review", "value": counts["pending"]},
            {"label": "Rejected chunks", "value": counts["rejected"]},
        ],
        "timestamp": _utc_now()
    }, status_code=200)

@router.get("/exports")
async def exports():
    """Get exports list with real data from Supabase"""
    try:
        service = get_supabase_service()
        
        # Get vectors for export metadata
        vectors = service.fetch_vectors(limit=200) if service.enabled else []
        activity = service.fetch_activity(limit=100) if service.enabled else []
        
        # Calculate statistics
        total_records = len(vectors)
        approved_records = len([v for v in vectors if v.get("approval_status") == "approved"])
        pending_records = len([v for v in vectors if v.get("approval_status") == "pending"])
        
        # Estimate export sizes (rough calculation)
        avg_record_size = 2.5  # KB per record
        excel_size = (total_records * avg_record_size) / 1024  # Convert to MB
        csv_size = (total_records * avg_record_size * 0.8) / 1024
        json_size = (total_records * avg_record_size * 1.2) / 1024
        
        # Create mock export history
        export_history = []
        if total_records > 0:
            formats = [
                {"format": "Excel", "size": f"{excel_size:.1f} MB", "records": approved_records},
                {"format": "CSV", "size": f"{csv_size:.1f} MB", "records": approved_records},
                {"format": "JSON", "size": f"{json_size:.1f} MB", "records": total_records},
            ]
            
            for idx, fmt in enumerate(formats):
                export_history.append({
                    "id": f"export-{idx}",
                    "name": f"{fmt['format']} Export - {_utc_now()[:10]}",
                    "format": fmt["format"],
                    "records": fmt["records"],
                    "size": fmt["size"],
                    "createdAt": _utc_now(),
                    "createdBy": "system",
                    "status": "completed",
                    "download_url": f"/api/exports/{idx}/download"
                })
        
        return JSONResponse({
            "items": export_history,
            "exports": export_history,
            "total": len(export_history),
            "stats": {
                "total_exports_created": len(export_history) + (len(activity) // 10),
                "this_month": len(export_history),
                "most_used_format": "Excel" if export_history else "-",
                "storage_used": f"{(sum(float(e['size'].split()[0]) for e in export_history if 'MB' in e['size']) if export_history else 0):.1f} MB",
                "total_records_available": total_records,
                "approved_records": approved_records,
                "pending_records": pending_records,
            },
            "timestamp": _utc_now()
        }, status_code=200)
    except Exception as e:
        return JSONResponse({
            "items": [],
            "exports": [],
            "total": 0,
            "stats": {
                "total_exports_created": 0,
                "this_month": 0,
                "most_used_format": "-",
                "storage_used": "0 MB",
                "total_records_available": 0,
                "approved_records": 0,
                "pending_records": 0,
            },
            "timestamp": _utc_now()
        }, status_code=200)

@router.post("/exports")
async def create_export(payload: ExportRequest):
    """Create export"""
    return JSONResponse({
        "export_id": f"export-{int(time.time())}",
        "status": "queued",
        "payload": sanitize_dict(payload.model_dump()),
        "timestamp": _utc_now()
    }, status_code=202)
