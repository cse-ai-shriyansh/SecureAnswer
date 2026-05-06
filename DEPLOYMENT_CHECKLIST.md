# Production Deployment Checklist

## Pre-Deployment (Local)

- [ ] Git initialized and code pushed to GitHub
  - [ ] Repo URL: `https://github.com/YOUR-USERNAME/secureanswer`
  - [ ] Branch: `main`
  - [ ] All files committed

## Supabase Setup

- [ ] Project created at https://app.supabase.com
  - [ ] Project ID: _______________
  - [ ] Project URL: _______________
- [ ] Keys copied and saved securely
  - [ ] Anon key: _______________
  - [ ] Service role key: _______________
- [ ] Database schema deployed (`supabase_vectors_schema.sql`)
  - [ ] Tables created: `vectors`, `activity`, `ingestion_jobs`, `users`, `user_stats`
- [ ] RLS policies enabled on all tables
- [ ] Google OAuth provider enabled in Supabase

## Google OAuth Setup

- [ ] Google Cloud project created
  - [ ] Project name: `SecureAnswer`
  - [ ] Project ID: _______________
- [ ] OAuth 2.0 credentials created
  - [ ] Client ID: _______________
  - [ ] Client Secret: _______________
- [ ] Redirect URIs configured
  - [ ] `http://localhost:3000`
  - [ ] `http://localhost:3001`
  - [ ] `https://your-vercel-domain.vercel.app`
  - [ ] `https://xxxx.supabase.co/auth/v1/callback`
- [ ] Credentials linked to Supabase

## Backend Deployment (Render)

- [ ] Render account created at https://render.com
- [ ] GitHub connected to Render
- [ ] Web service created
  - [ ] Service name: `secureanswer-backend`
  - [ ] Repository: `https://github.com/YOUR-USERNAME/secureanswer`
  - [ ] Branch: `main`
  - [ ] Build command: `pip install -r backend/requirements.txt`
  - [ ] Start command: `gunicorn -k uvicorn.workers.UvicornWorker backend.app:app --bind 0.0.0.0:$PORT`
- [ ] Environment variables set
  - [ ] `APP_ENV=production`
  - [ ] `CORS_ORIGINS=https://your-vercel-domain.vercel.app`
  - [ ] `AUTH_SECRET_KEY=` (32+ chars)
  - [ ] `GOOGLE_CLIENT_ID=` (from Google Cloud)
  - [ ] `SUPABASE_URL=` (from Supabase)
  - [ ] `SUPABASE_KEY=` (anon key)
  - [ ] `SUPABASE_SERVICE_ROLE_KEY=` (service role key)
  - [ ] `GEMINI_API_KEY=` (from Google AI)
  - [ ] `GEMINI_MODEL=gemini-2.5-flash`
  - [ ] `LLM_PROVIDER=gemini`
- [ ] Backend deployed successfully
  - [ ] Render URL: _______________
  - [ ] Health check passes: `{url}/api/health` → 200

## Frontend Deployment (Vercel)

- [ ] Vercel account created at https://vercel.com
- [ ] GitHub connected to Vercel
- [ ] Project created
  - [ ] Project name: `secureanswer`
  - [ ] Repository: `https://github.com/YOUR-USERNAME/secureanswer`
  - [ ] Branch: `main`
- [ ] Environment variables set
  - [ ] `VITE_API_BASE_URL=` (Render backend URL)
  - [ ] `VITE_GOOGLE_CLIENT_ID=` (from Google Cloud)
  - [ ] `VITE_SUPABASE_URL=` (from Supabase)
  - [ ] `VITE_SUPABASE_KEY=` (anon key)
- [ ] Frontend deployed successfully
  - [ ] Vercel URL: _______________
  - [ ] Home page loads without errors

## Post-Deployment Testing

- [ ] Backend health check
  - [ ] Endpoint: `https://{render-url}/api/health`
  - [ ] Response: 200 OK
- [ ] Frontend loads
  - [ ] URL: `https://{vercel-url}`
  - [ ] Dashboard visible
- [ ] Google OAuth login
  - [ ] Login button works
  - [ ] OAuth flow completes
  - [ ] Redirected to dashboard
- [ ] Answer generation
  - [ ] Navigate to "Answer Generation" page
  - [ ] Ask a question
  - [ ] Retrieve chunks from FAISS
  - [ ] Generate answer using Gemini
  - [ ] Display with citations
- [ ] Supabase connectivity
  - [ ] Activity logs visible on Dashboard
  - [ ] User stats showing
  - [ ] No 401/403 errors in browser console

## Post-Deployment Configuration

- [ ] CORS updated with final Vercel URL
  - [ ] Backend `CORS_ORIGINS` updated
  - [ ] Backend redeployed
- [ ] Google OAuth redirect URIs updated
  - [ ] Added `https://secureanswer.vercel.app` (or custom domain)
- [ ] Sample data seeded (optional)
  - [ ] Run `python seed_user_data_fixed.py`
  - [ ] Verify tables populated in Supabase
- [ ] Monitoring enabled
  - [ ] Render logs accessible
  - [ ] Vercel analytics enabled
  - [ ] Supabase monitoring set up

## Production Hardening

- [ ] Auth secret key is secure
  - [ ] At least 32 characters
  - [ ] Random/non-predictable
- [ ] Service role key is SECRET
  - [ ] Never exposed to frontend
  - [ ] Only used on backend
  - [ ] Rotate if accidentally shared
- [ ] RLS policies reviewed
  - [ ] Current: Permissive (for demo)
  - [ ] Plan stricter policies for production
- [ ] Rate limiting active
  - [ ] Auth endpoints: 5 attempts per 15 minutes
  - [ ] Upload endpoint: max 50 MB
- [ ] Error logging enabled
  - [ ] Check Render logs regularly
  - [ ] Set up alerts for critical errors
- [ ] Database backups enabled
  - [ ] Supabase automated backups ON
  - [ ] Retention: 7+ days

## Optional Enhancements

- [ ] Custom domain added
  - [ ] Vercel: `https://your-domain.com`
  - [ ] Backend DNS configured
- [ ] SSL certificate active
  - [ ] Vercel: auto-enabled with custom domain
  - [ ] Render: auto-enabled
- [ ] CDN enabled
  - [ ] Vercel: enabled by default
- [ ] Database indexing optimized
  - [ ] Supabase: indexes on `chunk_id`, `doc_id`, `created_at`
- [ ] Performance monitoring set up
  - [ ] Frontend: Web Vitals tracking
  - [ ] Backend: Response time tracking

---

## Quick Reference URLs

- **GitHub**: https://github.com/YOUR-USERNAME/secureanswer
- **Render Dashboard**: https://dashboard.render.com
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Supabase Dashboard**: https://app.supabase.com
- **Google Cloud Console**: https://console.cloud.google.com

---

**Status**: ⬜ Not Started | 🟨 In Progress | ✅ Complete

