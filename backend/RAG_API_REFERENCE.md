# RAG API Quick Reference

## System Health & Status

### Health Check
```bash
GET /api/rag/health
```
Response: System status with component health

### Statistics
```bash
GET /api/rag/stats
```
Response: System statistics (chunks, documents, query counts, timings)

---

## Retrieval (Vector Search)

### Single Query Retrieval
```bash
POST /api/rag/retrieve
Content-Type: application/json

{
    "query": "How do I reset my password?",
    "top_k": 5,
    "filters": null
}
```

**Parameters:**
- `query` (string, required) - Your search query
- `top_k` (integer, default: 5) - Number of results (1-50)
- `filters` (object, optional) - Metadata filters

**Response:**
```json
{
    "query": "How do I reset my password?",
    "chunks": [
        {
            "chunk_id": "chunk-xyz",
            "doc_id": "doc-001",
            "text": "To reset your password...",
            "source_file": "help.pdf",
            "similarity_score": 0.95,
            "approval_status": "approved",
            "document_version": 1
        }
    ],
    "total_chunks_retrieved": 5,
    "search_time_ms": 45.2
}
```

### Batch Retrieval
```bash
POST /api/rag/batch-retrieve?queries=Q1&queries=Q2&queries=Q3
```

---

## Generation (Full RAG)

### Generate Answer with Context
```bash
POST /api/rag/answer
Content-Type: application/json

{
    "query": "What is your refund policy?",
    "top_k": 5,
    "model": "gpt-3.5-turbo"
}
```

**Parameters:**
- `query` (string, required) - Your question
- `top_k` (integer, default: 5) - Context chunks to retrieve
- `model` (string, default: "gpt-3.5-turbo") - LLM model to use

**Available Models:**
- `gpt-3.5-turbo` - OpenAI (requires OPENAI_API_KEY)
- `gpt-4` - OpenAI GPT-4 (requires OPENAI_API_KEY)
- `claude-3-opus` - Anthropic (requires ANTHROPIC_API_KEY)
- `gemini-pro` - Google (requires GOOGLE_API_KEY)

**Response:**
```json
{
    "answer": "Our refund policy allows returns within 30 days of purchase...",
    "confidence_score": 0.95,
    "source_chunks": [
        {
            "chunk_id": "chunk-xyz",
            "text": "...",
            "source_file": "policy.pdf",
            "similarity_score": 0.92
        }
    ],
    "model_used": "gpt-3.5-turbo",
    "generation_time_ms": 1250.5,
    "created_at": "2026-05-05T10:30:00Z"
}
```

---

## Document Management

### Upload Document
```bash
POST /api/rag/documents/upload
Content-Type: multipart/form-data

file: <PDF, DOCX, TXT, or XLSX file>
source: manual
```

**Supported Formats:**
- `.pdf` - PDF documents
- `.docx` - Microsoft Word
- `.xlsx` - Microsoft Excel
- `.txt` - Plain text

**Response:** (202 Accepted)
```json
{
    "status": "processing",
    "filename": "guide.pdf",
    "message": "Document uploaded successfully. Processing started...",
    "source": "manual"
}
```

### List Documents
```bash
GET /api/rag/documents
```

**Response:**
```json
{
    "documents": [
        {
            "doc_id": "doc-001",
            "filename": "guide.pdf",
            "chunks_count": 45,
            "source": "manual",
            "uploaded_at": "2026-05-05T10:00:00Z"
        }
    ],
    "total_count": 1,
    "last_updated": "2026-05-05T10:30:00Z"
}
```

---

## Feedback

### Submit Answer Feedback
```bash
POST /api/rag/feedback?query=Q&answer_id=ID&rating=5&comment=Great+answer
```

**Parameters:**
- `query` (string, required) - Original query
- `answer_id` (string, required) - Answer ID
- `rating` (integer, required) - Rating 1-5
- `comment` (string, optional) - Feedback text

**Response:**
```json
{
    "status": "success",
    "message": "Feedback recorded",
    "feedback_id": "feedback-12345"
}
```

---

## Python Examples

### Retrieval
```python
import requests

response = requests.post(
    "http://localhost:8000/api/rag/retrieve",
    json={
        "query": "How do I contact support?",
        "top_k": 5
    }
)

result = response.json()
for chunk in result["chunks"]:
    print(f"Score: {chunk['similarity_score']:.2f}")
    print(f"Text: {chunk['text'][:100]}...")
```

### Answer Generation
```python
import requests

response = requests.post(
    "http://localhost:8000/api/rag/answer",
    json={
        "query": "What are your business hours?",
        "top_k": 5,
        "model": "gpt-3.5-turbo"
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence_score']:.2%}")
print(f"Generation time: {result['generation_time_ms']:.0f}ms")
```

### Document Upload
```python
import requests

files = {"file": open("policy.pdf", "rb")}
response = requests.post(
    "http://localhost:8000/api/rag/documents/upload",
    files=files,
    data={"source": "manual"}
)

print(response.json())
```

---

## JavaScript/Fetch Examples

### Retrieval
```javascript
const response = await fetch('http://localhost:8000/api/rag/retrieve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        query: 'How do I change my password?',
        top_k: 5
    })
});

const data = await response.json();
console.log('Chunks:', data.chunks);
```

### Answer Generation
```javascript
const response = await fetch('http://localhost:8000/api/rag/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        query: 'What payment methods do you accept?',
        top_k: 5,
        model: 'gpt-3.5-turbo'
    })
});

const data = await response.json();
console.log('Answer:', data.answer);
console.log('Confidence:', data.confidence_score);
```

---

## Error Responses

### 400 Bad Request
```json
{
    "detail": "Invalid request parameters"
}
```

### 500 Internal Server Error
```json
{
    "detail": "Retrieval failed: [error message]"
}
```

---

## Performance Tips

1. **Faster Retrieval:**
   - Reduce `top_k` (e.g., 3 instead of 5)
   - Use batch retrieval for multiple queries

2. **Faster Generation:**
   - Use `gpt-3.5-turbo` instead of `gpt-4`
   - Reduce `max_tokens` in configuration
   - Increase `temperature` for faster responses (less consistent)

3. **Better Quality:**
   - Increase `top_k` for more context
   - Use `gpt-4` instead of `gpt-3.5-turbo`
   - Add more documents to knowledge base

4. **Cost Optimization:**
   - Cache frequent queries
   - Use batch processing
   - Monitor token usage

---

## Configuration

Set these environment variables in `.env`:

```env
# LLM Settings
LLM_MODEL=gpt-3.5-turbo
DEFAULT_TOP_K=5
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=500

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Retrieval Settings
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MIN_SIMILARITY_SCORE=0.3
```

---

## Troubleshooting

**Q: "No module named 'faiss'"**  
A: Install: `pip install faiss-cpu`

**Q: "OPENAI_API_KEY not found"**  
A: Set in `.env` or environment: `OPENAI_API_KEY=sk-...`

**Q: "kb.faiss not found"**  
A: Run: `python rag_quickstart.py` to initialize

**Q: Slow responses**  
A: Check `/api/rag/stats`, reduce `top_k`, or check API rate limits

**Q: Low answer quality**  
A: Increase `top_k`, use better LLM (GPT-4), or add more documents

---

## Links

- [Full RAG Documentation](RAG_SETUP.md)
- [Backend README](README.md)
- [API Docs (Interactive)](http://localhost:8000/docs)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [FAISS Docs](https://github.com/facebookresearch/faiss)
