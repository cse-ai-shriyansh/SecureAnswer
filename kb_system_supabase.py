"""
kb_system_supabase.py

Enhanced Knowledge Base system with Supabase integration.

Stores:
- Chunk text and embeddings in FAISS (local)
- Metadata in Supabase PostgreSQL (vectors table)
- Activity logs in Supabase (activity table)

Falls back to local SQLite if Supabase unavailable.
"""

import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import uuid

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("faiss-cpu and sentence-transformers are required")

try:
    from supabase_client import get_supabase_client
    SUPABASE_AVAILABLE = True
except Exception as e:
    print(f"Warning: Supabase not available: {e}")
    SUPABASE_AVAILABLE = False


@dataclass
class ChunkData:
    """Chunk metadata."""
    doc_id: str
    chunk_id: str
    chunk_text: str
    source_file: str
    approval_status: str
    document_version: int = 1
    created_at: Optional[str] = None


class KnowledgeBaseSupa:
    """Knowledge Base with Supabase backend."""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # FAISS index (local)
        self.index_path = self.data_dir / "kb.faiss"
        self.embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedding_dim = 384

        # Load or create FAISS index
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        else:
            self.index = faiss.IndexFlatIP(self.embedding_dim)

        # Mapping from FAISS index position to chunk_id
        self.chunk_id_map: Dict[int, str] = {}

        # SQLite backup (always available)
        self.db_path = self.data_dir / "kb_metadata.sqlite"
        self._init_db()

        # Supabase client
        self.supabase = None
        if SUPABASE_AVAILABLE:
            try:
                self.supabase = get_supabase_client()
            except Exception as e:
                print(f"Warning: Could not initialize Supabase: {e}")

    def _init_db(self):
        """Initialize SQLite backup database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kb_metadata (
                chunk_id TEXT PRIMARY KEY,
                doc_id TEXT NOT NULL,
                chunk_text TEXT NOT NULL,
                source_file TEXT,
                approval_status TEXT DEFAULT 'approved',
                document_version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_doc_id ON kb_metadata(doc_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_approval ON kb_metadata(approval_status)
        """)

        conn.commit()
        conn.close()

    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        embedding = self.embeddings_model.encode(text, convert_to_numpy=True)
        # Normalize for cosine similarity
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding

    async def store_chunk(
        self,
        doc_id: str,
        chunk_id: str,
        chunk_text: str,
        source_file: str,
        approval_status: str = "approved",
        document_version: int = 1,
    ) -> Dict[str, Any]:
        """
        Store chunk with embedding and metadata.

        Stores embedding in FAISS, metadata in Supabase (or SQLite fallback).
        """
        # Generate embedding
        embedding = self.generate_embedding(chunk_text)

        # Add to FAISS
        self.index.add(np.array([embedding], dtype=np.float32))
        idx = self.index.ntotal - 1
        self.chunk_id_map[idx] = chunk_id

        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))

        # Prepare metadata
        chunk_data = ChunkData(
            doc_id=doc_id,
            chunk_id=chunk_id,
            chunk_text=chunk_text,
            source_file=source_file,
            approval_status=approval_status,
            document_version=document_version,
            created_at=datetime.utcnow().isoformat(),
        )

        # Try Supabase first
        if self.supabase:
            try:
                result = await self.supabase.insert_kb_metadata(
                    doc_id=doc_id,
                    chunk_id=chunk_id,
                    chunk_text=chunk_text,
                    embedding_vector=embedding.tolist(),
                    source_file=source_file,
                    approval_status=approval_status,
                    document_version=document_version,
                )
                print(f"✓ Stored chunk {chunk_id} in Supabase")
                return result
            except Exception as e:
                print(f"Warning: Could not store in Supabase: {e}, falling back to SQLite")

        # Fallback to SQLite
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO kb_metadata
            (chunk_id, doc_id, chunk_text, source_file, approval_status, document_version, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            chunk_id, doc_id, chunk_text, source_file, approval_status, document_version,
            chunk_data.created_at
        ))
        conn.commit()
        conn.close()

        return asdict(chunk_data)

    async def fetch_chunks_by_doc(
        self, doc_ids: List[str], approval_status: str = "approved"
    ) -> List[Dict[str, Any]]:
        """Fetch chunks by document IDs."""
        # Try Supabase first
        if self.supabase:
            try:
                chunks = await self.supabase.get_kb_chunks(
                    doc_ids=doc_ids, approval_status=approval_status, limit=1000
                )
                return chunks
            except Exception as e:
                print(f"Warning: Could not fetch from Supabase: {e}")

        # Fallback to SQLite
        placeholders = ",".join("?" * len(doc_ids))
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT * FROM kb_metadata
            WHERE doc_id IN ({placeholders}) AND approval_status = ?
            ORDER BY created_at DESC
        """, (*doc_ids, approval_status))

        chunks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return chunks

    def search_by_vector(
        self, query_embedding: np.ndarray, k: int = 5
    ) -> List[tuple]:
        """Search FAISS index by embedding vector."""
        if self.index.ntotal == 0:
            return []

        query_normalized = query_embedding / np.linalg.norm(query_embedding)
        distances, indices = self.index.search(
            np.array([query_normalized], dtype=np.float32), k
        )

        results = []
        for distance, idx in zip(distances[0], indices):
            if idx >= 0 and idx in self.chunk_id_map:
                chunk_id = self.chunk_id_map[idx]
                results.append((chunk_id, float(distance)))

        return results

    async def search_semantic(
        self, query: str, doc_ids: Optional[List[str]] = None, k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Semantic search: embed query, search FAISS, fetch metadata.

        Returns chunks with scores.
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Search FAISS
        search_results = self.search_by_vector(query_embedding, k=k)

        if not search_results:
            return []

        # Filter by doc_ids if provided
        if doc_ids:
            # Fetch metadata and filter
            all_chunks = await self.fetch_chunks_by_doc(doc_ids)
            chunk_dict = {c["chunk_id"]: c for c in all_chunks}
        else:
            # Fetch all metadata
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM kb_metadata WHERE approval_status = ?", ("approved",))
            chunk_dict = {row["chunk_id"]: dict(row) for row in cursor.fetchall()}
            conn.close()

        # Build results
        results = []
        for chunk_id, score in search_results:
            if chunk_id in chunk_dict:
                chunk = chunk_dict[chunk_id]
                chunk["similarity_score"] = score
                results.append(chunk)

        return results

    async def log_chunk_access(self, chunk_id: str, user_id: str, action: str):
        """Log chunk access/modification."""
        if self.supabase:
            try:
                await self.supabase.log_activity(
                    event_type=f"chunk_{action}",
                    entity_id=chunk_id,
                    user_id=user_id,
                    metadata={"timestamp": datetime.utcnow().isoformat()},
                )
            except Exception as e:
                print(f"Warning: Could not log activity: {e}")

    def save(self):
        """Persist FAISS index."""
        faiss.write_index(self.index, str(self.index_path))


# Global instance
_kb_supa: Optional[KnowledgeBaseSupa] = None


async def get_kb_supabase() -> KnowledgeBaseSupa:
    """Get or create KB instance."""
    global _kb_supa
    if _kb_supa is None:
        _kb_supa = KnowledgeBaseSupa()
    return _kb_supa
