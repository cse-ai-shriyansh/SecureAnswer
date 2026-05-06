"""
Supabase Setup Guide for SecureAnswer

This guide walks you through setting up Supabase and configuring SecureAnswer
to use your database schema.
"""

# ============================================================================
# STEP 1: CREATE SUPABASE PROJECT
# ============================================================================
"""
1. Go to https://supabase.com and sign up
2. Create a new project
3. Wait for the project to initialize
4. Get your project credentials from:
   - Settings > API > Project URL (SUPABASE_URL)
   - Settings > API > Project API Keys > anon public (SUPABASE_KEY)
"""

# ============================================================================
# STEP 2: CREATE REQUIRED TABLES
# ============================================================================
"""
Run these SQL queries in the Supabase SQL Editor (https://app.supabase.com/project/_/sql)

This creates the tables shown in your database schema diagram.
"""

SUPABASE_SQL_SETUP = """
-- Create vectors table for KB metadata and embeddings
CREATE TABLE vectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_id TEXT NOT NULL,
    chunk_id TEXT UNIQUE NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(384),  -- all-MiniLM-L6-v2 has 384 dimensions
    source_file TEXT,
    approval_status VARCHAR DEFAULT 'approved',
    document_version INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for semantic search
CREATE INDEX idx_vectors_embedding ON vectors USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_vectors_doc_id ON vectors(doc_id);
CREATE INDEX idx_vectors_approval_status ON vectors(approval_status);
CREATE INDEX idx_vectors_chunk_id ON vectors(chunk_id);

-- Create activity table
CREATE TABLE activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,  -- 'chunk_created', 'chunk_updated', 'chunk_deleted', etc.
    entity_id UUID NOT NULL,  -- reference to chunk_id or document_id
    user_id UUID NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_activity_entity_id ON activity(entity_id);
CREATE INDEX idx_activity_user_id ON activity(user_id);
CREATE INDEX idx_activity_created_at ON activity(created_at DESC);

-- Create activity_logs table
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    action_type VARCHAR NOT NULL,  -- 'login', 'generate_answer', 'approve_answer', etc.
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at DESC);

-- Create ingestion_jobs table
CREATE TABLE ingestion_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    status VARCHAR NOT NULL,  -- 'pending', 'processing', 'completed', 'failed'
    results JSONB,  -- {file_name, chunks_created, document_count, errors, ...}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_ingestion_jobs_user_id ON ingestion_jobs(user_id);
CREATE INDEX idx_ingestion_jobs_status ON ingestion_jobs(status);
CREATE INDEX idx_ingestion_jobs_created_at ON ingestion_jobs(created_at DESC);

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR UNIQUE NOT NULL,
    name TEXT,
    role VARCHAR DEFAULT 'user',  -- 'user', 'admin', 'moderator'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- Create user_stats table
CREATE TABLE user_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL,
    total_actions INT DEFAULT 0,
    total_logins INT DEFAULT 0,
    last_active TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_stats_user_id ON user_stats(user_id);

-- Enable Row Level Security (RLS) for users table (optional but recommended)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;
"""

# ============================================================================
# STEP 3: INSTALL SUPABASE PYTHON CLIENT
# ============================================================================
"""
pip install supabase
"""

# ============================================================================
# STEP 4: CONFIGURE ENVIRONMENT
# ============================================================================
"""
Add to your .env file:

SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key

Example:
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key
"""

# ============================================================================
# STEP 5: UPDATE BACKEND TO USE SUPABASE
# ============================================================================
"""
The backend has been updated to support Supabase integration:

File: supabase_client.py
- SupabaseDB class handles all database operations
- Async methods for metadata, activity, ingestion jobs, user stats

File: kb_system_supabase.py
- KnowledgeBaseSupa class with Supabase + FAISS integration
- Falls back to SQLite if Supabase unavailable
- Stores embeddings locally in FAISS, metadata in Supabase

Usage in backend:
    from supabase_client import get_supabase_client
    
    db = get_supabase_client()
    
    # Log activity
    await db.log_activity(
        event_type="chunk_created",
        entity_id=chunk_id,
        user_id=user_id
    )
    
    # Create ingestion job
    job = await db.create_ingestion_job(
        user_id=user_id,
        file_name="guidelines.pdf",
        file_size=2400000,
        document_count=14
    )
"""

# ============================================================================
# STEP 6: MIGRATION FROM SQLITE TO SUPABASE
# ============================================================================
"""
If you already have data in SQLite, use the migration script:
    python migrate_to_supabase.py

This will:
1. Read all chunks from kb_metadata.sqlite
2. Upload them to Supabase vectors table with embeddings
3. Verify data integrity
4. Keep SQLite as backup
"""

# ============================================================================
# STEP 7: VERIFY SETUP
# ============================================================================
"""
Test the connection:
    python -c "from supabase_client import get_supabase_client; db = get_supabase_client(); print('✓ Supabase connected')"

Expected output:
    ✓ Supabase connected
"""

# ============================================================================
# DATABASE SCHEMA REFERENCE
# ============================================================================
"""
vectors table - Knowledge base chunks with embeddings
├── id (UUID): Primary key
├── doc_id (TEXT): Document identifier (e.g., "pdf_123")
├── chunk_id (TEXT): Unique chunk identifier
├── chunk_text (TEXT): The actual text content
├── embedding (VECTOR(384)): 384-dimensional embedding for semantic search
├── source_file (TEXT): Original file name
├── approval_status (VARCHAR): 'approved', 'pending', 'rejected'
├── document_version (INTEGER): Version of document
├── metadata (JSONB): Additional metadata (tags, keywords, etc)
├── created_at (TIMESTAMP): Creation timestamp
└── updated_at (TIMESTAMP): Last update timestamp

activity table - Document/system events
├── id (UUID): Primary key
├── event_type (TEXT): Type of event (chunk_created, chunk_updated, etc)
├── entity_id (UUID): Reference to what changed
├── user_id (UUID): Who made the change
├── metadata (JSONB): Additional event details
└── created_at (TIMESTAMP): When it happened

activity_logs table - User action history
├── id (UUID): Primary key
├── user_id (UUID): Which user
├── action_type (VARCHAR): What they did (login, generate_answer, etc)
├── metadata (JSONB): Request/response details
└── created_at (TIMESTAMP): When it happened

ingestion_jobs table - PDF/document ingestion tracking
├── id (UUID): Primary key
├── user_id (UUID): Who initiated the ingestion
├── status (VARCHAR): 'pending', 'processing', 'completed', 'failed'
├── results (JSONB): {file_name, chunks_created, document_count, errors}
├── created_at (TIMESTAMP): When job started
└── updated_at (TIMESTAMP): When job last updated

users table - User profiles
├── id (UUID): Primary key
├── email (VARCHAR): Unique email
├── name (TEXT): Display name
├── role (VARCHAR): 'user', 'admin', 'moderator'
└── created_at (TIMESTAMP): Account creation time

user_stats table - User statistics
├── id (UUID): Primary key
├── user_id (UUID): Reference to user
├── total_actions (INT): Total actions performed
├── total_logins (INT): Total login count
├── last_active (TIMESTAMP): Last activity timestamp
├── created_at (TIMESTAMP): Record creation time
└── updated_at (TIMESTAMP): Last update time
"""

# ============================================================================
# COMMON OPERATIONS
# ============================================================================
"""
# Retrieve KB chunks for a document
chunks = await db.get_kb_chunks(doc_ids=["doc_123"], approval_status="approved")

# Log user activity
await db.log_activity(
    event_type="document_ingested",
    entity_id=doc_id,
    user_id=user_id,
    metadata={"chunk_count": 14}
)

# Create ingestion job
job = await db.create_ingestion_job(
    user_id=user_id,
    file_name="company_guidelines.pdf",
    file_size=2400000,
    document_count=14
)

# Update job status
await db.update_ingestion_job(
    job_id=job["id"],
    status="completed",
    results={"chunks_created": 14, "errors": []}
)

# Get user stats
stats = await db.get_user_stats(user_id)

# Get dashboard statistics
dashboard = await db.get_dashboard_stats()
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================
"""
Issue: "Supabase credentials missing"
Solution: Set SUPABASE_URL and SUPABASE_KEY environment variables

Issue: Vector search not working
Solution: Check that pgvector extension is enabled in Supabase:
    - Go to Database > Extensions
    - Search for "pgvector"
    - Toggle it ON

Issue: Foreign key constraint errors
Solution: Ensure users table is created before referencing it in other tables

Issue: Performance issues with large vectors
Solution: The IVFFLAT index with lists=100 is optimized for ~1M embeddings.
For larger datasets, adjust:
    CREATE INDEX idx_vectors_embedding ON vectors 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 200);
"""

print(__doc__)
