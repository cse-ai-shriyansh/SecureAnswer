import axios from 'axios'

// Get backend URL from environment or use default
const backendURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: backendURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

import { getToken } from './auth'

// Attach bearer token automatically if present
api.interceptors.request.use((config) => {
  try {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  } catch (e) {
    // ignore auth errors in interceptor
  }
  return config
})

// Add response error handler
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', {
      status: error.response?.status,
      url: error.response?.config?.url,
      data: error.response?.data,
      message: error.message
    })
    return Promise.reject(error)
  }
)

export default api

export async function fetchDashboard() {
  const res = await api.get('/api/dashboard')
  return res.data
}

export async function fetchActivity() {
  const res = await api.get('/api/activity')
  return res.data
}

export async function fetchReviewQueue() {
  const res = await api.get('/api/review')
  return res.data
}

export async function approveAnswer(id, payload = {}) {
  const res = await api.post(`/api/review/${id}/approve`, payload)
  return res.data
}

export async function rejectAnswer(id, payload = {}) {
  const res = await api.post(`/api/review/${id}/reject`, payload)
  return res.data
}

export async function fetchIngestion() {
  const res = await api.get('/api/ingestion')
  return res.data
}

export async function uploadFile(formData) {
  const res = await api.post('/api/ingestion/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return res.data
}

export async function fetchValidation() {
  const res = await api.get('/api/validation')
  return res.data
}

export async function fetchKnowledgeBase(q = '') {
  const res = await api.get('/api/kb', { params: { q } })
  return res.data
}

export async function fetchFreshness() {
  const res = await api.get('/api/freshness')
  return res.data
}

export async function fetchAnswers(params = {}) {
  const res = await api.get('/api/answers', { params })
  return res.data
}

export async function fetchAnswerLibrary(q = '') {
  const res = await api.get('/api/answers/library', { params: { q } })
  return res.data
}

export async function generateAnswer(payload) {
  const params = {
    question: payload.question || payload.query || '',
    use_llm: payload.use_llm !== false,
    top_k: payload.top_k || 5
  }
  const res = await api.post('/api/generate', null, { params })
  return res.data
}

export async function runRetrieval(query, options = {}) {
  const params = {
    query,
    top_k: options.top_k || 5,
    use_llm: options.use_llm !== false
  }
  const res = await api.post('/api/retrieval', null, { params })
  return res.data
}

export async function fetchInsights() {
  const res = await api.get('/api/insights')
  return res.data
}

export async function fetchExports() {
  const res = await api.get('/api/exports')
  return res.data
}

export async function createExport(payload) {
  const res = await api.post('/api/exports', payload)
  return res.data
}

// RAG-focused aliases used by dedicated pages/components.
export async function retrieveContext(query, topK = 5) {
  return runRetrieval(query, { top_k: topK })
}

export async function uploadDocument(file, source = 'manual') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('source', source)
  return uploadFile(formData)
}

export async function getRAGHealth() {
  const res = await api.get('/api/rag/health')
  return res.data
}

export async function getRAGStats() {
  const res = await api.get('/api/rag/stats')
  return res.data
}

export async function submitFeedback(payload) {
  const res = await api.post('/api/rag/feedback', payload)
  return res.data
}
