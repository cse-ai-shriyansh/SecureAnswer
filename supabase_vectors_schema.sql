-- Supabase Vectors Table Schema
-- Run this in the Supabase SQL Editor to set up the vectors table for RAG storage

-- Enable vector extension (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create vectors table for KB chunks
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

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_vectors_doc_id ON public.vectors(doc_id);
CREATE INDEX IF NOT EXISTS idx_vectors_chunk_id ON public.vectors(chunk_id);
CREATE INDEX IF NOT EXISTS idx_vectors_approval_status ON public.vectors(approval_status);
CREATE INDEX IF NOT EXISTS idx_vectors_source_file ON public.vectors(source_file);
CREATE INDEX IF NOT EXISTS idx_vectors_created_at ON public.vectors(created_at);

-- Create HNSW index on embedding for fast similarity search
CREATE INDEX IF NOT EXISTS idx_vectors_embedding 
ON public.vectors 
USING hnsw (embedding vector_ip_ops)
WITH (m=4, ef_construction=64);

-- Enable RLS (Row Level Security)
ALTER TABLE public.vectors ENABLE ROW LEVEL SECURITY;

-- Allow public read access (anon role can select)
CREATE POLICY "Allow public read access"
ON public.vectors
FOR SELECT
USING (TRUE);

-- Allow authenticated users to insert/update/delete
CREATE POLICY "Allow authenticated insert"
ON public.vectors
FOR INSERT
WITH CHECK (auth.role() = 'authenticated' OR TRUE);

CREATE POLICY "Allow authenticated update"
ON public.vectors
FOR UPDATE
USING (auth.role() = 'authenticated' OR TRUE);

CREATE POLICY "Allow authenticated delete"
ON public.vectors
FOR DELETE
USING (auth.role() = 'authenticated' OR TRUE);

-- Ensure activity table exists
CREATE TABLE IF NOT EXISTS public.activity (
  id BIGSERIAL PRIMARY KEY,
  event_type TEXT NOT NULL,
  entity_id TEXT,
  user_id TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for activity
CREATE INDEX IF NOT EXISTS idx_activity_event_type ON public.activity(event_type);
CREATE INDEX IF NOT EXISTS idx_activity_entity_id ON public.activity(entity_id);
CREATE INDEX IF NOT EXISTS idx_activity_user_id ON public.activity(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_created_at ON public.activity(created_at);

-- Enable RLS on activity
ALTER TABLE public.activity ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read activity"
ON public.activity
FOR SELECT
USING (TRUE);

CREATE POLICY "Allow insert activity"
ON public.activity
FOR INSERT
WITH CHECK (TRUE);

-- Ensure ingestion_jobs table exists
CREATE TABLE IF NOT EXISTS public.ingestion_jobs (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  status TEXT DEFAULT 'pending',
  results JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for ingestion_jobs
CREATE INDEX IF NOT EXISTS idx_ingestion_jobs_user_id ON public.ingestion_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_ingestion_jobs_status ON public.ingestion_jobs(status);
CREATE INDEX IF NOT EXISTS idx_ingestion_jobs_created_at ON public.ingestion_jobs(created_at);

-- Enable RLS on ingestion_jobs
ALTER TABLE public.ingestion_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read ingestion"
ON public.ingestion_jobs
FOR SELECT
USING (TRUE);

CREATE POLICY "Allow insert ingestion"
ON public.ingestion_jobs
FOR INSERT
WITH CHECK (TRUE);

CREATE POLICY "Allow update ingestion"
ON public.ingestion_jobs
FOR UPDATE
USING (TRUE);

-- Ensure users table exists
CREATE TABLE IF NOT EXISTS public.users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  role TEXT DEFAULT 'user',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on email
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);

-- Enable RLS on users
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read users"
ON public.users
FOR SELECT
USING (TRUE);

-- Ensure user_stats table exists
CREATE TABLE IF NOT EXISTS public.user_stats (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  total_actions INTEGER DEFAULT 0,
  total_logins INTEGER DEFAULT 0,
  last_active TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id
CREATE INDEX IF NOT EXISTS idx_user_stats_user_id ON public.user_stats(user_id);

-- Enable RLS on user_stats
ALTER TABLE public.user_stats ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read stats"
ON public.user_stats
FOR SELECT
USING (TRUE);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to vectors table
DROP TRIGGER IF EXISTS update_vectors_updated_at ON public.vectors;
CREATE TRIGGER update_vectors_updated_at
BEFORE UPDATE ON public.vectors
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Apply updated_at trigger to ingestion_jobs table
DROP TRIGGER IF EXISTS update_ingestion_jobs_updated_at ON public.ingestion_jobs;
CREATE TRIGGER update_ingestion_jobs_updated_at
BEFORE UPDATE ON public.ingestion_jobs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Apply updated_at trigger to user_stats table
DROP TRIGGER IF EXISTS update_user_stats_updated_at ON public.user_stats;
CREATE TRIGGER update_user_stats_updated_at
BEFORE UPDATE ON public.user_stats
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

COMMIT;
