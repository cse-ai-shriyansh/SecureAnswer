#!/usr/bin/env python3
"""
Setup Supabase schema for RAG vectors table and related tables.

This script will:
1. Create the vectors table with embedding column
2. Create activity, ingestion_jobs, users, and user_stats tables
3. Create indexes and RLS policies
4. Enable pgvector extension

Run this after setting up your Supabase project.
"""

import os
import sys
from dotenv import load_dotenv

# Load env
load_dotenv('backend/.env')

def setup_supabase():
    """Setup Supabase schema"""
    try:
        from supabase import create_client
        import postgrest
    except ImportError:
        print("❌ Missing supabase client. Install with: pip install supabase")
        return False
    
    url = os.getenv('SUPABASE_URL', '').strip()
    key = os.getenv('SUPABASE_KEY', '').strip()
    
    if not url or not key:
        print("❌ SUPABASE_URL and SUPABASE_KEY not set in backend/.env")
        return False
    
    print(f"📋 Setting up Supabase schema at {url}")
    print("=" * 70)
    
    # Create client
    client = create_client(url, key)
    
    # SQL queries to run
    sql_queries = [
        # Enable pgvector
        "CREATE EXTENSION IF NOT EXISTS vector;",
        
        # Create vectors table
        """
        CREATE TABLE IF NOT EXISTS public.vectors (
          id BIGSERIAL PRIMARY KEY,
          doc_id TEXT NOT NULL,
          chunk_id TEXT NOT NULL UNIQUE,
          chunk_text TEXT NOT NULL,
          embedding vector(384),
          source_file TEXT,
          approval_status TEXT DEFAULT 'approved',
          document_version INTEGER DEFAULT 1,
          metadata JSONB DEFAULT '{}',
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create indexes
        "CREATE INDEX IF NOT EXISTS idx_vectors_doc_id ON public.vectors(doc_id);",
        "CREATE INDEX IF NOT EXISTS idx_vectors_chunk_id ON public.vectors(chunk_id);",
        "CREATE INDEX IF NOT EXISTS idx_vectors_approval_status ON public.vectors(approval_status);",
        "CREATE INDEX IF NOT EXISTS idx_vectors_source_file ON public.vectors(source_file);",
        
        # Enable RLS on vectors
        "ALTER TABLE public.vectors ENABLE ROW LEVEL SECURITY;",
        
        # RLS policies for vectors
        """
        CREATE POLICY "Allow public read access"
        ON public.vectors
        FOR SELECT
        USING (TRUE);
        """,
    ]
    
    print("\n✅ Schema setup instructions:")
    print("1. Go to your Supabase project dashboard")
    print("2. Open SQL Editor")
    print("3. Run the queries in supabase_vectors_schema.sql")
    print("4. Or paste the SQL below and run it:")
    print("\n" + "=" * 70)
    
    # Read schema file
    try:
        with open('supabase_vectors_schema.sql', 'r') as f:
            schema_sql = f.read()
        print(schema_sql)
    except FileNotFoundError:
        print("❌ supabase_vectors_schema.sql not found")
        return False
    
    print("=" * 70)
    print("\n📝 After running the schema:")
    print("1. Test the vectors table: python -c \"from supabase_client import get_supabase_client; db=get_supabase_client(); print(db.client.table('vectors').select('*').limit(0).execute().data)\"")
    print("2. Your retrieval service will automatically use Supabase for metadata")
    print("3. Embeddings stored in FAISS (local), metadata in Supabase")
    
    return True

if __name__ == '__main__':
    success = setup_supabase()
    sys.exit(0 if success else 1)
