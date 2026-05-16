"""
Retrieval Service - Vector search with FAISS (no Supabase vectors)
"""

import os
import json
import time
import hashlib
import sqlite3
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import sys
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class RetrieverService:
    """
    RAG Retrieval Service - Vector search with FAISS (local-only).
    
    Uses:
    - FAISS IndexFlatIP for vector similarity search (384-dim embeddings)
    - Sentence-Transformers for embedding generation
    - SQLite for chunk metadata (no Supabase vectors table)
    """
    
    def __init__(self, data_dir: str = "./data", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize retriever service.
        
        Args:
            data_dir: Directory containing FAISS index and metadata
            model_name: Sentence transformer model for embeddings
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_path = self.data_dir / "kb.faiss"
        self.metadata_db = self.data_dir / "kb_metadata.sqlite"

        self.faiss = None
        self.np = np
        self.sentence_transformers = None
        
        # Initialize embedding model (local-first, deterministic fallback)
        self.embedding_model = None
        self.embedding_dim = 384
        self._load_embedding_model(model_name)
        
        # Initialize SQLite metadata store
        self._init_metadata_db()
        
        # Load or create FAISS index
        self.index = None
        self.chunk_id_map = {}
        self._load_faiss_index()
        
        # Track retrieval stats
        self.retrieval_times = []
        self.total_queries = 0
        
    def _init_metadata_db(self):
        """Initialize SQLite database for chunk metadata"""
        try:
            conn = sqlite3.connect(str(self.metadata_db))
            cursor = conn.cursor()
            
            # Create chunks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    faiss_idx INTEGER PRIMARY KEY,
                    chunk_id TEXT UNIQUE NOT NULL,
                    doc_id TEXT NOT NULL,
                    chunk_text TEXT,
                    source_file TEXT,
                    approval_status TEXT DEFAULT 'approved',
                    document_version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunk_id ON chunks(chunk_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_id ON chunks(doc_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_file ON chunks(source_file)")
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not initialize metadata DB: {e}")
    
    def store_chunk_metadata(self, faiss_idx: int, chunk_id: str, doc_id: str, 
                           chunk_text: str, source_file: str, approval_status: str = "approved"):
        """Store chunk metadata in SQLite"""
        try:
            conn = sqlite3.connect(str(self.metadata_db))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO chunks 
                (faiss_idx, chunk_id, doc_id, chunk_text, source_file, approval_status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (faiss_idx, chunk_id, doc_id, chunk_text, source_file, approval_status))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error storing metadata: {e}")
    
    def get_chunk_metadata(self, faiss_idx: int) -> Dict:
        """Retrieve chunk metadata from SQLite"""
        try:
            conn = sqlite3.connect(str(self.metadata_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT chunk_id, doc_id, chunk_text, source_file, approval_status
                FROM chunks WHERE faiss_idx = ?
            """, (faiss_idx,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                md = dict(row)
                # Provide a consistent `text` key used by generation code
                if "chunk_text" in md:
                    md["text"] = md.get("chunk_text")
                return md
            return {}
        except Exception as e:
            print(f"Error retrieving metadata: {e}")
            return {}
        
    def _load_faiss_index(self):
        """Load FAISS index from disk or create new one"""
        if self.faiss is None:
            import faiss as faiss_module

            self.faiss = faiss_module

        if self.index_path.exists():
            print(f"Loading FAISS index from {self.index_path}")
            self.index = self.faiss.read_index(str(self.index_path))
        else:
            print(f"Creating new FAISS index")
            self.index = self.faiss.IndexFlatIP(self.embedding_dim)

    def _load_embedding_model(self, model_name: str):
        """Load embedding model using local cache only, then fallback to deterministic embeddings."""
        print(f"Loading embedding model (local-first): {model_name}")
        try:
            from sentence_transformers import SentenceTransformer

            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            self.embedding_model = SentenceTransformer(model_name)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            print(f"Embedding model ready (dim={self.embedding_dim})")
        except Exception as exc:
            print(f"Embedding model unavailable, using hash fallback: {exc}")
            self.embedding_model = None
            self.embedding_dim = 384

    def _hash_encode(self, text: str) -> "np.ndarray":
        """Deterministic local embedding fallback used when no transformer model is available."""
        if self.np is None:
            import numpy as np_module

            self.np = np_module

        vector = self.np.zeros(self.embedding_dim, dtype=self.np.float32)
        tokens = text.lower().split()
        if not tokens:
            tokens = [""]

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "little") % self.embedding_dim
            vector[idx] += 1.0

        norm = self.np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector.reshape(1, -1)
    
    def encode_query(self, query: str) -> "np.ndarray":
        """
        Encode query to embedding vector.
        
        Args:
            query: Query text
            
        Returns:
            Embedding vector (1D array)
        """
        if self.embedding_model is not None:
            embedding = self.embedding_model.encode(query, convert_to_numpy=True)
            if self.np is None:
                import numpy as np_module

                self.np = np_module

            norm = self.np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            return embedding.reshape(1, -1)

        return self._hash_encode(query)
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5,
        filters: Optional[Dict] = None,
        metadata_retriever = None
    ) -> Tuple[List[Dict], float]:
        """
        Retrieve most relevant chunks for a query.
        
        Args:
            query: User query text
            top_k: Number of results to return
            filters: Optional metadata filters
            metadata_retriever: Function to retrieve chunk metadata
            
        Returns:
            Tuple of (retrieved_chunks, search_time_ms)
        """
        start_time = time.time()
        
        # Encode query
        query_embedding = self.encode_query(query)

        if self.index.ntotal == 0:
            search_time_ms = (time.time() - start_time) * 1000
            self.retrieval_times.append(search_time_ms)
            self.total_queries += 1
            return [], search_time_ms

        # If no external metadata retriever provided, default to local SQLite retriever
        if metadata_retriever is None:
            metadata_retriever = self.get_chunk_metadata
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        search_time_ms = (time.time() - start_time) * 1000
        self.retrieval_times.append(search_time_ms)
        self.total_queries += 1
        
        # Retrieve metadata for each result
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # Invalid index
                continue
            
            chunk_data = {
                "rank": i + 1,
                "similarity_score": float(distance),
                "faiss_idx": int(idx)
            }
            
            # Get chunk metadata if function provided
            if metadata_retriever and callable(metadata_retriever):
                metadata = metadata_retriever(int(idx))
                chunk_data.update(metadata)
            
            results.append(chunk_data)
        
        return results, search_time_ms
    
    def batch_retrieve(
        self,
        queries: List[str],
        top_k: int = 5,
        metadata_retriever = None
    ) -> List[Tuple[List[Dict], float]]:
        """
        Retrieve results for multiple queries.
        
        Args:
            queries: List of query texts
            top_k: Number of results per query
            metadata_retriever: Function to retrieve metadata
            
        Returns:
            List of (chunks, search_time) tuples
        """
        return [
            self.retrieve(q, top_k, None, metadata_retriever)
            for q in queries
        ]
    
    def get_stats(self) -> Dict:
        """Get retrieval service statistics"""
        if not self.retrieval_times:
            return {
                "index_size": self.index.ntotal,
                "embedding_dim": self.embedding_dim,
                "total_queries": 0,
                "avg_retrieval_time_ms": 0
            }
        
        return {
            "index_size": self.index.ntotal,
            "embedding_dim": self.embedding_dim,
            "total_queries": self.total_queries,
            "avg_retrieval_time_ms": sum(self.retrieval_times) / len(self.retrieval_times)
        }


class MockMetadataRetriever:
    """Mock metadata retriever for testing"""
    
    def __init__(self):
        self.metadata_store = {}
    
    def __call__(self, faiss_idx: int) -> Dict:
        """Retrieve metadata for FAISS index"""
        # This would normally query Supabase or SQLite
        return self.metadata_store.get(faiss_idx, {
            "chunk_id": f"chunk-{faiss_idx}",
            "doc_id": f"doc-001",
            "text": f"Sample chunk {faiss_idx}",
            "source_file": "example.pdf",
            "approval_status": "approved",
            "document_version": 1
        })
