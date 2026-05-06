"""
Supabase Database Client

Provides integration with Supabase PostgreSQL database for:
- Knowledge base metadata storage (replacing SQLite)
- Activity logging
- Ingestion job tracking
- User statistics

Schema tables:
- activity: tracks document events (add, update, delete)
- activity_logs: tracks user actions
- ingestion_jobs: tracks PDF/document ingestion jobs
- users: stores user information
- user_stats: stores user statistics
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import json
import uuid

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError("supabase is required: pip install supabase")


class SupabaseDB:
    """Supabase database client for SecureAnswer."""

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize Supabase client.

        Args:
            url: Supabase project URL (env: SUPABASE_URL)
            key: Supabase API key (env: SUPABASE_KEY)
        """
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "Supabase credentials missing. Set SUPABASE_URL and SUPABASE_KEY environment variables."
            )

        self.client: Client = create_client(self.url, self.key)

    # ========================
    # KB METADATA OPERATIONS
    # ========================

    async def insert_kb_metadata(
        self,
        doc_id: str,
        chunk_id: str,
        chunk_text: str,
        embedding_vector: List[float],
        source_file: str,
        approval_status: str = "approved",
        document_version: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Insert knowledge base chunk with metadata and embedding.

        Creates/updates entry in vectors table with embedding.
        """
        if metadata is None:
            metadata = {}

        data = {
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "chunk_text": chunk_text,
            "embedding": embedding_vector,  # Supabase will store as vector type
            "source_file": source_file,
            "approval_status": approval_status,
            "document_version": document_version,
            "metadata": metadata,
            "created_at": datetime.utcnow().isoformat(),
        }

        result = self.client.table("vectors").insert(data).execute()
        return result.data[0] if result.data else data

    async def get_kb_chunks(
        self,
        doc_ids: Optional[List[str]] = None,
        approval_status: str = "approved",
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Retrieve knowledge base chunks by doc_ids and approval status."""
        query = self.client.table("vectors").select("*")

        if doc_ids:
            query = query.in_("doc_id", doc_ids)

        query = query.eq("approval_status", approval_status).limit(limit)
        result = query.execute()
        return result.data

    async def update_chunk_status(
        self, chunk_id: str, approval_status: str
    ) -> Dict[str, Any]:
        """Update approval status of a chunk."""
        result = (
            self.client.table("vectors")
            .update({"approval_status": approval_status})
            .eq("chunk_id", chunk_id)
            .execute()
        )
        return result.data[0] if result.data else {}

    # ========================
    # INGESTION JOB OPERATIONS
    # ========================

    async def create_ingestion_job(
        self,
        user_id: str,
        file_name: str,
        file_size: int,
        document_count: int,
        status: str = "pending",
    ) -> Dict[str, Any]:
        """Create a new ingestion job."""
        job_id = str(uuid.uuid4())
        data = {
            "id": job_id,
            "user_id": user_id,
            "status": status,
            "results": {
                "file_name": file_name,
                "file_size": file_size,
                "document_count": document_count,
                "chunks_created": 0,
                "errors": [],
            },
            "created_at": datetime.utcnow().isoformat(),
        }

        result = self.client.table("ingestion_jobs").insert(data).execute()
        return result.data[0] if result.data else data

    async def update_ingestion_job(
        self, job_id: str, status: str, results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update ingestion job status and results."""
        update_data = {
            "status": status,
            "results": results,
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = (
            self.client.table("ingestion_jobs")
            .update(update_data)
            .eq("id", job_id)
            .execute()
        )
        return result.data[0] if result.data else {}

    async def get_ingestion_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an ingestion job by ID."""
        result = (
            self.client.table("ingestion_jobs").select("*").eq("id", job_id).execute()
        )
        return result.data[0] if result.data else None

    # ========================
    # ACTIVITY LOGGING
    # ========================

    async def log_activity(
        self,
        event_type: str,
        entity_id: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Log a document/system event to activity table."""
        if metadata is None:
            metadata = {}

        data = {
            "event_type": event_type,
            "entity_id": entity_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
        }

        result = self.client.table("activity").insert(data).execute()
        return result.data[0] if result.data else data

    async def log_action(
        self,
        user_id: str,
        action_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Log a user action to activity_logs table."""
        if metadata is None:
            metadata = {}

        data = {
            "user_id": user_id,
            "action_type": action_type,
            "metadata": metadata,
            "created_at": datetime.utcnow().isoformat(),
        }

        result = self.client.table("activity_logs").insert(data).execute()
        return result.data[0] if result.data else data

    async def get_activities(
        self, entity_id: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve activities, optionally filtered by entity_id."""
        query = self.client.table("activity").select("*").order(
            "created_at", desc=True
        )

        if entity_id:
            query = query.eq("entity_id", entity_id)

        result = query.limit(limit).execute()
        return result.data

    # ========================
    # USER OPERATIONS
    # ========================

    async def get_or_create_user(
        self, email: str, name: str = "", role: str = "user"
    ) -> Dict[str, Any]:
        """Get existing user or create new one."""
        # Check if user exists
        result = (
            self.client.table("users").select("*").eq("email", email).execute()
        )

        if result.data:
            return result.data[0]

        # Create new user
        user_id = str(uuid.uuid4())
        data = {
            "id": user_id,
            "email": email,
            "name": name,
            "role": role,
            "created_at": datetime.utcnow().isoformat(),
        }

        result = self.client.table("users").insert(data).execute()
        return result.data[0] if result.data else data

    # ========================
    # USER STATS OPERATIONS
    # ========================

    async def update_user_stats(
        self, user_id: str, action_type: str = "action"
    ) -> Dict[str, Any]:
        """Update user statistics (total_actions, last_active)."""
        # Get or create stats record
        result = (
            self.client.table("user_stats")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        now = datetime.utcnow().isoformat()

        if result.data:
            # Update existing stats
            stats = result.data[0]
            update_data = {
                "total_actions": stats.get("total_actions", 0) + 1,
                "last_active": now,
                "updated_at": now,
            }

            if action_type == "login":
                update_data["total_logins"] = stats.get("total_logins", 0) + 1

            update_result = (
                self.client.table("user_stats")
                .update(update_data)
                .eq("user_id", user_id)
                .execute()
            )
            return update_result.data[0] if update_result.data else {}
        else:
            # Create new stats record
            stats_id = str(uuid.uuid4())
            data = {
                "id": stats_id,
                "user_id": user_id,
                "total_actions": 1,
                "total_logins": 1 if action_type == "login" else 0,
                "last_active": now,
                "created_at": now,
                "updated_at": now,
            }

            insert_result = self.client.table("user_stats").insert(data).execute()
            return insert_result.data[0] if insert_result.data else data

    async def get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user statistics."""
        result = (
            self.client.table("user_stats")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    # ========================
    # DASHBOARD / ANALYTICS
    # ========================

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics for dashboard."""
        # Get total ingestion jobs
        jobs_result = (
            self.client.table("ingestion_jobs")
            .select("status")
            .execute()
        )

        total_jobs = len(jobs_result.data)
        pending_jobs = len([j for j in jobs_result.data if j["status"] == "pending"])
        completed_jobs = len([j for j in jobs_result.data if j["status"] == "completed"])

        # Get total users
        users_result = self.client.table("users").select("id").execute()
        total_users = len(users_result.data)

        # Get recent activities
        activities_result = (
            self.client.table("activity")
            .select("*")
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )

        return {
            "total_jobs": total_jobs,
            "pending_jobs": pending_jobs,
            "completed_jobs": completed_jobs,
            "total_users": total_users,
            "recent_activities": activities_result.data[:10],
        }


# Singleton instance
_db: Optional[SupabaseDB] = None


def get_supabase_client() -> SupabaseDB:
    """Get or create Supabase client singleton."""
    global _db
    if _db is None:
        _db = SupabaseDB()
    return _db
