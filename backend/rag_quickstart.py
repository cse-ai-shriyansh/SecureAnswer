#!/usr/bin/env python3
"""
RAG System Quick Start - Initialize and test RAG components
"""

import sys
from pathlib import Path

# Ensure project root and backend package are importable when script is run directly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def check_dependencies():
    """Check if all RAG dependencies are installed"""
    print("🔍 Checking RAG dependencies...")
    
    dependencies = {
        "faiss": "faiss-cpu",
        "sentence_transformers": "sentence-transformers",
        "numpy": "numpy",
        "pydantic": "pydantic",
        "fastapi": "fastapi",
    }
    
    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} (install: pip install {package})")
            missing.append(package)
    
    return missing

def initialize_faiss_index():
    """Initialize an empty FAISS index if not exists"""
    print("\n📦 Initializing FAISS index...")
    
    try:
        import faiss
        import numpy as np
        from pathlib import Path
        
        index_path = Path("kb.faiss")
        
        if index_path.exists():
            print(f"  ℹ️  Index already exists at {index_path}")
            return True
        
        print(f"  Creating new FAISS index...")
        index = faiss.IndexFlatIP(384)  # 384-dim embeddings
        faiss.write_index(index, str(index_path))
        print(f"  ✅ Index created at {index_path}")
        return True
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_retrieval_service():
    """Test the retrieval service"""
    print("\n🔎 Testing Retrieval Service...")
    
    try:
        from services.retrieval_service import RetrieverService
        
        retriever = RetrieverService()
        print(f"  ✅ Retriever initialized")
        print(f"     - Index size: {retriever.index.ntotal} chunks")
        print(f"     - Embedding dim: {retriever.embedding_dim}")
        
        # Test encoding
        query = "How do I get help?"
        embedding = retriever.encode_query(query)
        print(f"  ✅ Query encoding works")
        print(f"     - Query: '{query}'")
        print(f"     - Embedding shape: {embedding.shape}")
        
        return True
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_generation_service():
    """Test the generation service"""
    print("\n🤖 Testing Generation Service...")
    
    try:
        from services.generation_service import GenerationService
        import os
        
        generator = GenerationService()
        print(f"  ✅ Generator initialized")
        print(f"     - Model: {generator.model}")
        print(f"     - Provider: {generator.provider or 'none (using fallback)'}")
        
        if not generator.api_key:
            print(f"  ⚠️  Warning: No API key set. Using fallback generation.")
            print(f"     - Set OPENAI_API_KEY for OpenAI integration")
        
        return True
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ingestion_service():
    """Test the ingestion service"""
    print("\n📄 Testing Ingestion Service...")
    
    try:
        from services.ingestion_service import DocumentIngestionService
        
        ingester = DocumentIngestionService()
        print(f"  ✅ Ingester initialized")
        print(f"     - Chunk size: {ingester.chunk_size}")
        print(f"     - Chunk overlap: {ingester.chunk_overlap}")
        
        stats = ingester.get_stats()
        print(f"  ✅ Ingester stats: {stats}")
        
        return True
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all initialization and tests"""
    print("=" * 60)
    print("🚀 RAG System Quick Start & Verification")
    print("=" * 60)
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        print("\nContinuing with tests...")
    
    # Initialize FAISS
    faiss_ok = initialize_faiss_index()
    
    # Test services
    retrieval_ok = test_retrieval_service()
    generation_ok = test_generation_service()
    ingestion_ok = test_ingestion_service()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    status = {
        "FAISS Index": faiss_ok,
        "Retrieval Service": retrieval_ok,
        "Generation Service": generation_ok,
        "Ingestion Service": ingestion_ok,
    }
    
    all_ok = all(status.values())
    
    for name, ok in status.items():
        symbol = "✅" if ok else "❌"
        print(f"{symbol} {name}")
    
    print("\n" + "=" * 60)
    
    if all_ok:
        print("✅ RAG System is ready!")
        print("\nNext steps:")
        print("1. Start the backend: uvicorn app:app --reload")
        print("2. Visit API docs: http://localhost:8000/docs")
        print("3. Try RAG endpoints: /api/rag/retrieve or /api/rag/answer")
        print("\nFor detailed setup, see: RAG_SETUP.md")
    else:
        print("⚠️  Some components are not ready. Check errors above.")
        print("   Run this script again after fixing issues.")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
