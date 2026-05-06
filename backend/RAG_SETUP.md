# RAG (Retrieval-Augmented Generation) System

## Overview

The SecureAnswer RAG system combines vector search with large language models to provide intelligent, context-aware answers. It consists of three core components:

1. **Retrieval** - Vector similarity search using FAISS + Sentence-Transformers
2. **Context Enrichment** - Metadata retrieval from Supabase
3. **Generation** - LLM-based answer generation with source attribution

## Architecture

```
User Query
    ↓
[Embedding] (Sentence-Transformers)
    ↓
[Vector Search] (FAISS Index)
    ↓
[Metadata Retrieval] (Supabase)
    ↓
[Context Assembly]
    ↓
[LLM Generation] (OpenAI/Claude/etc)
    ↓
Answer with Sources
```

## Components

### 1. Retrieval Service (`services/retrieval_service.py`)

Handles vector similarity search and chunk retrieval.

**Key Methods:**
- `retrieve(query, top_k)` - Retrieve relevant chunks for a query
- `batch_retrieve(queries, top_k)` - Retrieve for multiple queries
- `encode_query(query)` - Generate embedding for query
- `get_stats()` - Service statistics

**Configuration:**
- Vector model: `all-MiniLM-L6-v2` (384 dimensions)
- Index type: FAISS IndexFlatIP (Inner Product similarity)
- Normalized embeddings for cosine similarity

### 2. Generation Service (`services/generation_service.py`)

Generates answers using LLMs with context.

**Supported Providers:**
- OpenAI (GPT-3.5, GPT-4)
- Anthropic Claude (with API key)
- Google Gemini (with API key)
- Fallback: Extractive summarization

**Key Methods:**
- `generate(query, context_chunks, max_tokens, temperature)` - Generate answer
- `_build_prompt(query, context_chunks)` - Create LLM prompt
- `get_stats()` - Generation statistics

### 3. Ingestion Service (`services/ingestion_service.py`)

Processes documents and converts to chunks.

**Supported Formats:**
- PDF (using pdfplumber + PyPDF2)
- DOCX (using python-docx)
- XLSX (using openpyxl)
- Plain text

**Features:**
- Automatic text extraction
- Configurable chunking with overlap
- Metadata generation
- Error handling and statistics

## API Endpoints

### Health & Status

```
GET /api/rag/health
GET /api/rag/stats
```

### Retrieval

```
POST /api/rag/retrieve
{
    "query": "How do I reset my password?",
    "top_k": 5,
    "filters": {"source_file": "help.pdf"}
}

Response:
{
    "query": "How do I reset my password?",
    "chunks": [...],
    "total_chunks_retrieved": 5,
    "search_time_ms": 45.2
}
```

### Generation (Full RAG)

```
POST /api/rag/answer
{
    "query": "How do I reset my password?",
    "top_k": 5,
    "model": "gpt-3.5-turbo"
}

Response:
{
    "answer": "To reset your password...",
    "confidence_score": 0.95,
    "source_chunks": [...],
    "model_used": "gpt-3.5-turbo",
    "generation_time_ms": 1250.5,
    "created_at": "2026-05-05T10:30:00Z"
}
```

### Document Management

```
POST /api/rag/documents/upload
GET /api/rag/documents

POST /api/rag/batch-retrieve
POST /api/rag/feedback
```

## Setup Guide

### 1. Environment Variables

Create `.env` in the backend folder:

```env
# Embeddings
VECTOR_MODEL=all-MiniLM-L6-v2

# LLM Provider
LLM_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=sk-...

# Optional: Other LLM providers
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJ...

# Processing
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MAX_FILE_SIZE_MB=50
```

### 2. Install Dependencies

```bash
# From backend folder
pip install -r requirements.txt
```

### 3. Initialize Knowledge Base

```bash
# Place your kb.faiss in the root project directory
# Or create an empty index programmatically

python -c "
from backend.services.retrieval_service import RetrieverService
retriever = RetrieverService()
print(f'Index loaded with {retriever.index.ntotal} chunks')
"
```

### 4. Run Backend

```bash
cd backend
uvicorn app:app --reload
```

Access API docs at: `http://localhost:8000/docs`

## Usage Examples

### Python

```python
from backend.services.retrieval_service import RetrieverService
from backend.services.generation_service import GenerationService

# Initialize services
retriever = RetrieverService()
generator = GenerationService(model="gpt-3.5-turbo")

# Retrieve relevant chunks
chunks, search_time = retriever.retrieve(
    query="What is your refund policy?",
    top_k=5
)

# Generate answer with context
result = generator.generate(
    query="What is your refund policy?",
    context_chunks=chunks
)

print(result["answer"])
```

### cURL

```bash
# Retrieve chunks
curl -X POST "http://localhost:8000/api/rag/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I reset my password?",
    "top_k": 5
  }'

# Generate answer (RAG)
curl -X POST "http://localhost:8000/api/rag/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I reset my password?",
    "top_k": 5,
    "model": "gpt-3.5-turbo"
  }'
```

### JavaScript/Frontend

```javascript
// Retrieve
const response = await fetch('http://localhost:8000/api/rag/retrieve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        query: "How do I reset my password?",
        top_k: 5
    })
});
const result = await response.json();
console.log(result.chunks);

// Generate answer
const answerResponse = await fetch('http://localhost:8000/api/rag/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        query: "How do I reset my password?",
        top_k: 5,
        model: "gpt-3.5-turbo"
    })
});
const answer = await answerResponse.json();
console.log(answer.answer);
```

## Performance Tuning

### Retrieval Optimization

```python
# Increase chunk size for longer context
service = RetrieverService(
    chunk_size=1024,      # Default: 512
    chunk_overlap=100     # Default: 50
)

# Batch retrieve (multiple queries)
results = retriever.batch_retrieve(
    queries=["Q1", "Q2", "Q3"],
    top_k=5
)
```

### Generation Optimization

```python
# Adjust temperature for consistency
result = generator.generate(
    query="question",
    context_chunks=chunks,
    temperature=0.3      # Lower = more deterministic
)

# Use faster model for performance
generator = GenerationService(model="gpt-3.5-turbo")

# Reduce max tokens for speed
result = generator.generate(
    query="question",
    context_chunks=chunks,
    max_tokens=200        # Default: 500
)
```

## Monitoring & Debugging

### Get System Stats

```bash
curl http://localhost:8000/api/rag/stats
```

### Health Check

```bash
curl http://localhost:8000/api/rag/health
```

### Logs

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Troubleshooting

### FAISS Index Not Found

```
Error: FileNotFoundError: kb.faiss
```

**Solution:** Make sure `kb.faiss` exists in the project root. Create an empty index:

```python
import faiss
import numpy as np
index = faiss.IndexFlatIP(384)
faiss.write_index(index, "kb.faiss")
```

### OpenAI API Key Error

```
Error: AuthenticationError: Incorrect API key provided
```

**Solution:** 
1. Set `OPENAI_API_KEY` in `.env`
2. Verify API key is valid at openai.com
3. Check API key permissions

### Slow Retrieval

- Reduce `top_k` parameter
- Use smaller vector model
- Implement FAISS index sharding for large datasets

### Low Answer Quality

- Increase `top_k` to provide more context
- Use higher quality LLM (GPT-4 vs GPT-3.5)
- Ensure documents are well-chunked
- Implement feedback loop for improvement

## Advanced Features (TODO)

- [ ] Reranking with cross-encoders
- [ ] Multi-hop reasoning
- [ ] Query expansion/refinement
- [ ] Caching of frequent queries
- [ ] A/B testing framework
- [ ] Feedback-based fine-tuning
- [ ] Multi-language support
- [ ] Custom embedding models

## Production Deployment

See [../DEPLOYMENT.md](../DEPLOYMENT.md) for production deployment guidelines.

## References

- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Sentence-Transformers](https://www.sbert.net/)
- [OpenAI API](https://platform.openai.com)
- [Supabase](https://supabase.com)
