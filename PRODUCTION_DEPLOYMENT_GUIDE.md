# Production Deployment Guide - SecureAnswer

Complete step-by-step tutorial to deploy SecureAnswer in production:
- **Backend**: Render (Python/FastAPI)
- **Frontend**: Vercel (React/Vite)
- **Database**: Supabase (PostgreSQL + pgvector)
- **Auth**: Google OAuth 2.0

**Estimated time: 60 minutes**

---

## Prerequisites

1. **GitHub account** - repo linked to GitHub
2. **Render account** - https://render.com (sign up with GitHub)
3. **Vercel account** - https://vercel.com (sign up with GitHub)
4. **Supabase account** - https://supabase.com (create or use existing project)
5. **Google Cloud Console** - https://console.cloud.google.com
6. **Git CLI** - installed and configured

---

## Step 1: Initialize Git & Push to GitHub

### 1.1 Initialize Git (if not already done)

```bash
cd "c:\Users\Lenovo\Desktop\Secure answer"
git init
git config user.email "your-email@example.com"
git config user.name "Your Name"
```

### 1.2 Add all files and create first commit

```bash
git add .
git commit -m "initial: secureanswer production ready"
```

### 1.3 Create GitHub repo & push

1. Go to https://github.com/new
2. Create repo named `secureanswer` (public or private)
3. Do **NOT** initialize with README/LICENSE (we have commits)
4. Copy the commands GitHub provides:

```bash
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/secureanswer.git
git push -u origin main
```

**Verify**: Your code is now on GitHub at `https://github.com/YOUR-USERNAME/secureanswer`

---

## Step 2: Supabase Setup (Database & Auth)

### 2.1 Create Supabase Project

1. Go to https://app.supabase.com
2. Click **"New Project"** → select **"Create a new project"**
3. **Project name**: `secureanswer`
4. **Password**: Generate strong password (save it)
5. **Region**: Pick closest to your users (e.g., `us-east-1`)
6. **Click Create Project** (wait 2-3 min)

### 2.2 Get Supabase Keys

1. Project is created → go to **Settings** → **API**
2. Copy:
   - **Project URL** (looks like `https://xxxx.supabase.co`)
   - **anon key** (public, for frontend)
   - **service_role key** (SECRET! for backend only)
3. Keep these safe - you'll need them soon.

### 2.3 Deploy Database Schema

1. Go to **SQL Editor** → **New query**
2. Paste contents of [`supabase_vectors_schema.sql`](supabase_vectors_schema.sql)
3. Click **Run**
4. Verify tables created: `vectors`, `activity`, `ingestion_jobs`, `users`, `user_stats`, `activity_logs`

### 2.4 Enable Row-Level Security (RLS)

1. Go to **Authentication** → **Policies**
2. Click table **`activity`** → **New Policy** → **For full customization**:
   - Name: `Allow anon insert & select`
   - Target: `activity`
   - Roles: `anon`, `authenticated`
   - Expression: `true` (permissive)
   - Operations: SELECT, INSERT, UPDATE
3. Repeat for `users`, `user_stats`, `activity_logs`, `vectors` tables
4. (Optional) Create stricter policies later; this allows demo data ingestion.

### 2.5 Set Up Google OAuth in Supabase

1. Go to **Authentication** → **Providers**
2. Enable **Google**:
   - Click **Google** toggle
   - Copy **Redirect URL** (e.g., `https://xxxx.supabase.co/auth/v1/callback`)
3. Don't configure Client ID/Secret yet (we'll do that in Google Cloud next)

---

## Step 3: Google OAuth Setup

### 3.1 Create Google OAuth Credentials

1. Go to https://console.cloud.google.com
2. Create new project: **"SecureAnswer"**
3. Go to **APIs & Services** → **OAuth consent screen**:
   - User type: **External**
   - Fill app name: `SecureAnswer`
   - Add your email
   - Scopes: Add `email` and `profile`
   - Test users: Add your email
4. Click **Save & Continue** → **Create OAuth 2.0 Client ID**:
   - Application type: **Web application**
   - Authorized redirect URIs:
     ```
     http://localhost:3000
     http://localhost:3001
     https://your-vercel-domain.vercel.app
     https://xxxx.supabase.co/auth/v1/callback
     ```
5. Copy **Client ID** (you'll need this)
6. Also get **Client Secret** (for backend)

### 3.2 Link Google OAuth to Supabase

1. Go back to Supabase → **Authentication** → **Providers** → **Google**
2. Paste Google **Client ID** and **Client Secret**
3. Click **Save**

---

## Step 4: Environment Variables Setup

### 4.1 Backend `.env` for Production

Update `/backend/.env` with production values:

```env
# Environment
APP_ENV=production
FLASK_ENV=production

# Server
PORT=8000

# CORS - Vercel frontend domain
CORS_ORIGINS=https://your-vercel-domain.vercel.app,https://secureanswer.vercel.app

# Auth
AUTH_SECRET_KEY=your-super-secret-random-key-32-chars-minimum
GOOGLE_CLIENT_ID=YOUR-GOOGLE-CLIENT-ID
ENABLE_DEV_LOGIN=false
ENABLE_TEST_LOGIN=false

# Supabase - PRODUCTION KEYS
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJhbGc...  # anon key (public, safe in frontend)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...  # service_role (SECRET! backend only)

# LLM
GEMINI_API_KEY=YOUR-GEMINI-API-KEY
GEMINI_MODEL=gemini-2.5-flash
LLM_PROVIDER=gemini

# Upload settings
MAX_UPLOAD_MB=50
MAX_REQUEST_BODY_BYTES=5000000
```

### 4.2 Frontend `.env.production` for Vercel

Create `/vercel.env.production.json`:

```json
{
  "env": {
    "VITE_API_BASE_URL": "https://your-render-backend-url.onrender.com",
    "VITE_GOOGLE_CLIENT_ID": "YOUR-GOOGLE-CLIENT-ID",
    "VITE_SUPABASE_URL": "https://xxxx.supabase.co",
    "VITE_SUPABASE_KEY": "eyJhbGc..."
  }
}
```

Or use Vercel dashboard → **Settings** → **Environment Variables**:
- `VITE_API_BASE_URL`: `https://your-render-backend.onrender.com`
- `VITE_GOOGLE_CLIENT_ID`: Your Google Client ID
- `VITE_SUPABASE_URL`: Supabase URL
- `VITE_SUPABASE_KEY`: Supabase anon key

---

## Step 5: Deploy Backend to Render

### 5.1 Connect GitHub to Render

1. Go to https://render.com/dashboard
2. Click **New +** → **Web Service**
3. **Connect GitHub** → select your `secureanswer` repo
4. Choose branch: `main`

### 5.2 Configure Backend Service

**Name**: `secureanswer-backend`

**Environment**: `Python 3.11`

**Build Command**:
```bash
pip install -r backend/requirements.txt
```

**Start Command**:
```bash
gunicorn -k uvicorn.workers.UvicornWorker backend.app:app --bind 0.0.0.0:$PORT
```

**Instance Type**: `Free` (0.25 CPU, 0.5 GB RAM - good for testing)

### 5.3 Add Environment Variables

In Render dashboard, go to **Environment**:

```
APP_ENV=production
CORS_ORIGINS=https://your-vercel-domain.vercel.app
AUTH_SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=YOUR-GOOGLE-CLIENT-ID
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
GEMINI_API_KEY=YOUR-GEMINI-API-KEY
GEMINI_MODEL=gemini-2.5-flash
LLM_PROVIDER=gemini
MAX_UPLOAD_MB=50
```

### 5.4 Deploy

Click **Create Web Service** → watch deployment logs

Once deployed:
- You'll get a URL like: `https://secureanswer-backend.onrender.com`
- Test health: `https://secureanswer-backend.onrender.com/api/health`

**Save this URL** - you need it for frontend config.

---

## Step 6: Deploy Frontend to Vercel

### 6.1 Connect to Vercel

1. Go to https://vercel.com/dashboard
2. Click **Add New...** → **Project**
3. **Import from Git** → select your `secureanswer` repo
4. Choose branch: `main`

### 6.2 Configure Frontend Project

**Project Name**: `secureanswer`

**Framework**: Vite is auto-detected ✓

**Root Directory**: `./` (default)

**Build Command**: `npm run build` (auto-detected)

**Output Directory**: `dist` (auto-detected)

### 6.3 Add Environment Variables

Click **Environment Variables**:

```
VITE_API_BASE_URL=https://secureanswer-backend.onrender.com
VITE_GOOGLE_CLIENT_ID=YOUR-GOOGLE-CLIENT-ID
VITE_SUPABASE_URL=https://xxxx.supabase.co
VITE_SUPABASE_KEY=eyJhbGc...
```

### 6.4 Deploy

Click **Deploy** → wait for build (2-3 min)

You'll get a Vercel URL like: `https://secureanswer.vercel.app`

---

## Step 7: Post-Deployment Configuration

### 7.1 Update CORS on Backend

1. Go to Render backend settings
2. Update `CORS_ORIGINS` env var:
   ```
   https://secureanswer.vercel.app
   ```

### 7.2 Update Google OAuth Redirect URIs

1. Go to Google Cloud Console → OAuth 2.0 credentials
2. Add Vercel domain to **Authorized Redirect URIs**:
   ```
   https://secureanswer.vercel.app
   ```

### 7.3 Seed Sample Data (Optional)

SSH into Render backend or run locally to seed Supabase:

```bash
cd "c:\Users\Lenovo\Desktop\Secure answer"
python seed_user_data_fixed.py
```

This populates `users`, `activity`, `activity_logs`, `user_stats` tables.

---

## Step 8: Test End-to-End

### 8.1 Test Backend

```bash
curl https://secureanswer-backend.onrender.com/api/health
```

Expected:
```json
{
  "status": "ok",
  "environment": "production",
  "version": "1.0.0"
}
```

### 8.2 Test Frontend

1. Open https://secureanswer.vercel.app
2. **Dashboard**: Should load (may show 0 data initially)
3. **Answer Generation**:
   - Type a question
   - Click **Generate Answer**
   - Should retrieve chunks and generate response from Gemini

### 8.3 Test Google OAuth

1. Click **Login** on frontend
2. Click **Sign in with Google**
3. Authenticate with your Google account
4. Should redirect to dashboard with JWT token

### 8.4 Test Supabase Connection

1. Go to **Insights** tab in frontend
2. Should show chunk counts from `vectors` table
3. Go to **Dashboard** → should show user stats from Supabase tables

---

## Step 9: Production Hardening

### 9.1 Secure Secrets

- [ ] Rotate `AUTH_SECRET_KEY` in production
- [ ] Rotate `SUPABASE_SERVICE_ROLE_KEY` if exposed
- [ ] Restrict Supabase RLS policies (currently permissive for demo)
- [ ] Use Vercel Secrets Manager or environment variables for sensitive data

### 9.2 Monitor & Logs

**Render**:
- Go to **Logs** to see backend errors
- Set up alerts for failed deployments

**Vercel**:
- Go to **Deployments** → **Analytics** to monitor frontend performance
- Check **Error Tracking** for runtime errors

### 9.3 Set Up Automated Deployments

Both Render and Vercel auto-deploy on `git push main`:
- Any push to `main` branch triggers rebuild
- Takes ~3-5 min per service

---

## Step 10: Custom Domain (Optional)

### 10.1 Vercel Custom Domain

1. Vercel dashboard → **Settings** → **Domains**
2. Add custom domain (e.g., `secureanswer.com`)
3. Update DNS records (Vercel provides instructions)

### 10.2 Render Custom Domain

1. Render dashboard → **Environment** → **Custom Domain**
2. Add domain
3. Update DNS records

---

## Troubleshooting

### Backend won't start on Render

**Error**: `ModuleNotFoundError`
- Check `backend/requirements.txt` exists
- Verify all imports in `backend/app.py`
- View Render logs for exact error

**Error**: `CORS error in browser`
- Update `CORS_ORIGINS` env var with correct Vercel domain
- Redeploy backend

### Frontend can't reach backend

**Error**: `Network error` or `CORS blocked`
- Check `VITE_API_BASE_URL` is set to Render backend URL
- Verify backend CORS includes frontend origin
- Check network tab in browser DevTools

### Supabase auth failing

**Error**: `401 Unauthorized` on Supabase calls
- Verify `SUPABASE_KEY` is the **anon key** (not service role)
- Check RLS policies allow anonymous access (they should for demo)
- Verify tables exist in Supabase SQL Editor

### Google OAuth not working

**Error**: `redirect_uri_mismatch`
- Add exact Vercel URL to Google OAuth Redirect URIs
- Include trailing slash if needed
- Verify `VITE_GOOGLE_CLIENT_ID` matches Google Cloud project

---

## Environment Variables Reference

### Backend (Render)

| Variable | Example | Required | Note |
|----------|---------|----------|------|
| `APP_ENV` | `production` | ✓ | Production mode |
| `CORS_ORIGINS` | `https://secureanswer.vercel.app` | ✓ | Frontend domain |
| `AUTH_SECRET_KEY` | `your-32-char-secret-key` | ✓ | JWT signing key |
| `GOOGLE_CLIENT_ID` | `123...apps.googleusercontent.com` | ✓ | Google OAuth |
| `SUPABASE_URL` | `https://xxxx.supabase.co` | ✓ | Database URL |
| `SUPABASE_KEY` | `eyJhbGc...` | ✓ | Anon key (public) |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGc...` | ✗ | Admin key (optional) |
| `GEMINI_API_KEY` | `AIza...` | ✓ | LLM API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | ✓ | Model name |
| `LLM_PROVIDER` | `gemini` | ✓ | Provider name |

### Frontend (Vercel)

| Variable | Example | Required | Note |
|----------|---------|----------|------|
| `VITE_API_BASE_URL` | `https://secureanswer-backend.onrender.com` | ✓ | Backend API |
| `VITE_GOOGLE_CLIENT_ID` | `123...apps.googleusercontent.com` | ✓ | Google OAuth |
| `VITE_SUPABASE_URL` | `https://xxxx.supabase.co` | ✓ | Database URL |
| `VITE_SUPABASE_KEY` | `eyJhbGc...` | ✓ | Anon key (public) |

---

## Next Steps

1. **Monitor production** - check logs daily for first week
2. **Set up CI/CD alerts** - get notified of deployment failures
3. **Implement analytics** - track user behavior, errors
4. **Plan database backups** - enable Supabase automated backups
5. **Scale as needed** - upgrade Render/Vercel plans if traffic increases

---

## Support Resources

- **Render docs**: https://render.com/docs
- **Vercel docs**: https://vercel.com/docs
- **Supabase docs**: https://supabase.com/docs
- **FastAPI docs**: https://fastapi.tiangolo.com
- **React docs**: https://react.dev

---

**Deployment complete! 🚀**
