# Quick Setup Guide

## 🚀 Fastest Way to Get Started (5 minutes)

### Windows Users

#### Step 1: Start Backend
Open Command Prompt or PowerShell in the project folder:
```cmd
start_backend.bat
```

Wait for:
```
INFO:     Application startup complete
```

#### Step 2: Start Frontend
Open a **new** Command Prompt/PowerShell:
```cmd
start_frontend.bat
```

#### Step 3: Open Browser
Navigate to: **http://localhost:3000**

#### Step 4: Login
This project does not include hardcoded demo credentials by default. If you
need a local fallback account for testing, set the environment variable
`ALLOW_DEMO=true` before starting the backend (development only).

**Done!** 🎉

---

### macOS/Linux Users

#### Step 1: Backend Setup (First Time Only)
```bash
python -m venv .venv
source .venv/bin/activate  # or: . .venv/bin/activate (fish shell)
pip install -r requirements.txt
```

#### Step 2: Start Backend
```bash
source .venv/bin/activate
python backend_server.py
```

#### Step 3: Start Frontend (New Terminal)
```bash
npm run build
npm run serve:static
# or: npx serve -s dist -l 3000
```

#### Step 4: Open Browser
Navigate to: **http://localhost:3000**

#### Step 5: Login
There are no built-in demo credentials. For local testing enable a demo
fallback with `ALLOW_DEMO=true` or configure an authentication provider.

**Done!** 🎉

---

## 🔧 Manual Setup (If Batch Scripts Don't Work)

### Backend

**First Time Setup:**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Every Time (Start Backend):**
```bash
# Windows
.venv\Scripts\activate
python backend_server.py

# macOS/Linux
source .venv/bin/activate
python backend_server.py
```

Backend will say:
```
Starting SecureAnswer Backend Server...
API available at: http://localhost:8000
```

### Frontend

**First Time Setup:**
```bash
npm install
npm run build
```

**Every Time (Start Frontend):**
```bash
npm run serve:static
# or
npx serve -s dist -l 3000
# or use Python
python -m http.server 3000 --directory dist
```

Frontend will be available at: **http://localhost:3000**

---

## 🌍 Change Backend URL

**Development (default):**
```
Backend: http://localhost:8000
Frontend: http://localhost:3000
```

**Production (example):**
If your backend is at `https://api.example.com`:

1. Edit `.env` file:
```
VITE_API_BASE_URL=https://api.example.com
```

2. Rebuild frontend:
```bash
npm run build
```

3. Serve again:
```bash
npm run serve:static
```

---

## ❌ Troubleshooting

### "Cannot connect to backend"
1. Check backend is running (should see `Application startup complete`)
2. Check `.env` has correct `VITE_API_BASE_URL`
3. Rebuild frontend: `npm run build`
4. Try `curl http://localhost:8000/health`

### "Port 3000 already in use"
```bash
# Windows - Kill process using port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :3000
kill -9 <PID>

# Or use different port
npx serve -s dist -l 3001
# Then go to http://localhost:3001
```

### "Port 8000 already in use"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>

# Or run on different port
python -m uvicorn backend_server:app --port 9000
# Then update .env: VITE_API_BASE_URL=http://localhost:9000
# Rebuild: npm run build
```

### "npm: command not found"
Node.js is not installed. Download from: https://nodejs.org

### "python: command not found"
Python is not installed. Download from: https://python.org

### Login says "Invalid credentials"
- Username: `demo@example.com` (exactly)
- Password: `demo123` (exactly)
- Click "Use demo" button to auto-fill

---

## 📚 Next Steps

1. ✅ Login works
2. ✅ Can see dashboard
3. Now explore the app:
   - Try uploading a document in **Ingestion**
   - Check **Knowledge Base** 
   - Try **Answer Generation**
   - View **Insights**

See [README.md](README.md) for full documentation
See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

---

## ❓ Help

- **Backend logs**: Watch the terminal where you ran `python backend_server.py`
- **Frontend errors**: Open browser developer console (F12)
- **API testing**: Try `curl http://localhost:8000/api/dashboard`

---

**Need detailed docs?** See [README.md](README.md) and [DEPLOYMENT.md](DEPLOYMENT.md)
