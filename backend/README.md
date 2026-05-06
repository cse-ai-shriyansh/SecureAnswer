# Backend - Fresh Start (FastAPI)

A modern async backend application using FastAPI, tailored to the existing project environment.

## Directory Structure

```
backend/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies (use root venv)
├── .env.example           # Environment variables template
├── README.md              # This file
│
├── config/                # Configuration
│   ├── __init__.py
│   └── settings.py        # Application settings
│
├── routes/                # API endpoints
│   ├── __init__.py
│   └── health.py          # Health check routes
│
├── models/                # Data models & schemas
│   ├── __init__.py
│   └── schemas.py         # Pydantic models
│
├── services/              # Business logic
│   ├── __init__.py
│   └── example_service.py # Example service
│
└── utils/                 # Utility functions
    ├── __init__.py
    └── helpers.py         # Helper functions
```

## Getting Started

### Prerequisites
- Existing virtual environment at project root: `..\.venv\`
- Python 3.8+

### Setup

1. **Activate the root virtual environment** (from project root):
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

2. **Install backend dependencies** (FastAPI requirements):
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file** (optional, copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

### Running the Application

**Option 1: Direct Python execution**
```bash
python app.py
```

**Option 2: Using Uvicorn** (recommended for development)
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

### API Documentation

- **Interactive Docs (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative Docs (ReDoc)**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## API Endpoints


## RAG (Retrieval-Augmented Generation) System

Complete vector search + LLM system for intelligent question-answering.

**Key Endpoints:**
- `POST /api/rag/retrieve` - Find relevant chunks using vector search
- `POST /api/rag/answer` - Full RAG pipeline (retrieve + generate answer)
- `POST /api/rag/documents/upload` - Ingest documents into knowledge base
- `GET /api/rag/health` - RAG system status
- `GET /api/rag/stats` - RAG system statistics

**Quick Example:**
```bash
curl -X POST "http://localhost:8000/api/rag/answer" \
   -H "Content-Type: application/json" \
   -d '{"query": "How do I reset my password?", "top_k": 5, "model": "gpt-3.5-turbo"}'
```

**Full Documentation:** See [RAG_SETUP.md](RAG_SETUP.md)

## Development

### Add New Routes

1. Create a new file in `routes/` (e.g., `routes/users.py`)
2. Define router and endpoints:
   ```python
   from fastapi import APIRouter
   router = APIRouter(prefix="/api", tags=["users"])
   
   @router.get("/users")
   async def get_users():
       return {"users": []}
   ```
3. Include router in `app.py`:
   ```python
   from routes.users import router as users_router
   app.include_router(users_router)
   ```

### Add New Services

1. Create service class in `services/` (e.g., `services/user_service.py`)
2. Import and use in routes

### Add New Models

1. Define Pydantic models in `models/schemas.py` or separate files
2. Use in route handlers for request/response validation

## Environment Variables

See `.env.example` for available options:
- `FLASK_ENV` - Environment mode (development/production)
- `PORT` - Server port (default: 8000)

## Testing

Run tests with pytest:
```bash
pytest
```

With coverage:
```bash
pytest --cov=.
```

## Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Notes

- This backend uses the **root project's virtual environment** (`.venv`)
- All dependencies are managed in the root `requirements.txt` (FastAPI packages are already included)
- The backend is designed to be modular and easily extensible
