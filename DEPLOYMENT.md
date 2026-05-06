# SecureAnswer - Separate Frontend & Backend Deployment

This document explains how to run SecureAnswer with the frontend and backend bundled separately.

## Architecture

```
SecureAnswer Enterprise Platform
├── Frontend (React + Vite)
│   ├── Built: npm run build → dist/
│   ├── Serve: node frontend_server.js (or python -m http.server)
│   └── Port: 3000 (or configurable)
└── Backend (FastAPI + Python)
    ├── API Server: backend_server.py
    ├── Ingestion Pipeline: ingestion_system.py
    ├── Port: 8000
    └── CORS enabled for cross-origin requests
```

## Prerequisites

### Frontend
- Node.js 18+ and npm
- Dependencies: `npm install`

### Backend
- Python 3.9+
- Virtual environment: `python -m venv .venv`
- Dependencies: `pip install -r requirements.txt`

## Quick Start

### Option 1: Windows Batch Scripts (Easiest)

**Terminal 1 - Backend:**
```cmd
start_backend.bat
```

**Terminal 2 - Frontend:**
```cmd
start_frontend.bat
```

Then open http://localhost:3000 in your browser.

---

### Option 2: Manual Commands

**Backend Setup (Run once):**
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# or (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Start Backend (Terminal 1):**
```bash
# Activate environment (if not already active)
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Run backend
python backend_server.py
# or
python -m uvicorn backend_server:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: http://localhost:8000

**Start Frontend (Terminal 2):**

First build the frontend:
```bash
npm run build
```

Then serve it:
```bash
# Option A: Using Node.js
node frontend_server.js

# Option B: Using npx serve
npx serve -s dist -l 3000

# Option C: Using Python
python -m http.server 3000 --directory dist
```

Frontend will be available at: http://localhost:3000

---

## Configuration

### Environment Variables

The frontend uses `VITE_API_BASE_URL` to connect to the backend.

**Development (.env.development):**
```
VITE_API_BASE_URL=http://localhost:8000
VITE_PORT=3002
VITE_DEBUG=true
```

**Production (.env.production):**
```
VITE_API_BASE_URL=http://localhost:8000
VITE_PORT=3000
VITE_DEBUG=false
```

### Changing Backend URL

To point the frontend to a different backend:

1. Edit `.env` or `.env.production`
2. Update `VITE_API_BASE_URL` to your backend URL
3. Rebuild frontend if needed: `npm run build`

Examples:
```
# Local backend on different port
VITE_API_BASE_URL=http://localhost:9000

# Remote backend
VITE_API_BASE_URL=https://api.secureanswer.example.com

# Backend with custom path
VITE_API_BASE_URL=https://example.com/secureanswer/api
```

---

## Backend API Endpoints

The backend exposes the following API:

### Authentication
- `POST /api/auth/login` - Login with credentials
    - Note: No demo credentials are shipped. For local testing you can
        enable a development fallback by setting `ALLOW_DEMO=true` in the
        backend environment, but this must not be used in production.

### Ingestion
- `POST /api/ingestion/upload` - Upload document for processing
- `GET /api/ingestion/status/{job_id}` - Get ingestion job status
- `GET /api/ingestion/results/{job_id}` - Get ingestion results

### Data Endpoints
- `GET /api/dashboard` - Dashboard metrics
- `GET /api/activity` - Recent activity
- `GET /api/review` - Review queue
- `GET /api/insights` - Analytics and insights
- `GET /api/exports` - Export list

### Health
- `GET /health` - Health check endpoint

---

## Deployment Scenarios

### Scenario 1: Both on Same Server

**Backend:** Runs on port 8000, serves API only
**Frontend:** Runs on port 3000, serves static files
**Communication:** Frontend → Backend via `http://localhost:8000`

```
User Browser
    ↓
http://localhost:3000 (Frontend on Node)
    ↓
API calls to http://localhost:8000 (Backend on Python)
```

**Environment:** `.env.production`
```
VITE_API_BASE_URL=http://localhost:8000
```

---

### Scenario 2: Backend Serves Both

**Backend:** FastAPI serves both API and frontend static files
**Frontend:** Served by backend at `/`

```bash
# Build frontend
npm run build

# Place dist/ in same directory as backend_server.py

# Start backend
python backend_server.py
```

Backend automatically mounts the dist folder and serves it.

**URL:** http://localhost:8000 (for both frontend and API)

---

### Scenario 3: Separate Domains

**Backend:** https://api.secureanswer.example.com
**Frontend:** https://secureanswer.example.com

**Environment:** `.env.production`
```
VITE_API_BASE_URL=https://api.secureanswer.example.com
```

CORS must be configured in backend:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://secureanswer.example.com"],
    ...
)
```

---

## Building for Production

### Frontend Build
```bash
npm run build
# Output: dist/ folder with optimized static files
```

### Backend Packaging
The backend is already standalone in `backend_server.py`.

For production:
1. Copy `backend_server.py` and all Python modules to server
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run with a production ASGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 backend_server:app
   ```

---

## Troubleshooting

### CORS Errors
If you see CORS errors, ensure:
1. Backend is running with CORS middleware enabled
2. Frontend is making requests to the correct backend URL
3. Backend `allow_origins` includes your frontend URL

### Frontend Can't Connect to Backend
1. Check if backend is running: `curl http://localhost:8000/health`
2. Verify `VITE_API_BASE_URL` in `.env`
3. Check browser console for the actual URL being requested
4. Ensure no firewall is blocking the connection

### Port Already in Use
```bash
# Windows - Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

---

## Development Workflow

1. **Start Backend:**
   ```bash
   # Terminal 1
   .venv\Scripts\activate
   python backend_server.py
   ```

2. **Start Frontend Dev Server (for hot reload):**
   ```bash
   # Terminal 2
   npm run dev
   # Runs on http://localhost:5173 (or next available port)
   ```

3. **Access Application:**
   - Dev server: http://localhost:5173
   - API: http://localhost:8000

4. **Make Changes:**
   - Frontend: Changes auto-reload in dev server
   - Backend: Changes auto-reload (with --reload flag)

---

## Performance Notes

- Frontend build size: ~530KB (gzipped: ~168KB)
- CSS: ~37KB (gzipped: ~6.7KB)
- Chunk size warning: Consider code-splitting for very large deployments
- API response caching: Uses SWR client-side caching

---

## Security Considerations

### CORS Configuration
Update `allow_origins` in `backend_server.py` for production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Only allow your frontend
    allow_credentials=True,
    allow_methods=["POST", "GET"],  # Restrict methods
    allow_headers=["*"],
)
```

### Authentication
Demo credentials are for development only. In production:
1. Implement real user authentication
2. Use secure token storage (not localStorage)
3. Implement token refresh logic
4. Add rate limiting to login endpoint

### Environment Variables
Never commit sensitive information to version control:
- Use `.env.local` for local overrides (add to `.gitignore`)
- Use environment variables on production servers
- Keep API keys and secrets outside the repository

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs: `backend_server.py` console output
3. Check browser console for frontend errors
4. Verify both services are running on correct ports

---

**Last Updated:** May 2, 2026
**Version:** 1.0.0
