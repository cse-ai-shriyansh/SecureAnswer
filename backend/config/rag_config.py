"""
RAG Configuration
"""

import os
from typing import Optional

class RAGConfig:
    """RAG system configuration"""
    
    # Vector Search Settings
    VECTOR_MODEL = os.getenv("VECTOR_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIM = 384
    INDEX_PATH = os.getenv("INDEX_PATH", "./kb.faiss")
    
    # Retrieval Settings
    DEFAULT_TOP_K = 5
    MAX_TOP_K = 50
    MIN_SIMILARITY_SCORE = 0.3
    
    # Generation Settings
    DEFAULT_LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 500
    
    # LLM Provider Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Supabase Settings
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Document Processing
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 50))
    
    # Supported file types
    SUPPORTED_FILE_TYPES = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }
    
    # Cache Settings
    ENABLE_CACHING = True
    CACHE_TTL_SECONDS = 3600  # 1 hour
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        warnings = []
        
        if not cls.GOOGLE_API_KEY:
            warnings.append("Warning: GOOGLE_API_KEY not set. Gemini-based generation won't work.")
        
        if not cls.SUPABASE_URL or not cls.SUPABASE_KEY:
            warnings.append("Warning: Supabase credentials not set. Will fall back to local storage.")
        
        return warnings
