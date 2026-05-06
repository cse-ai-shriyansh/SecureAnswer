const TOKEN_KEY = 'sa_token'

export function setToken(token) {
  try {
    localStorage.setItem(TOKEN_KEY, token)
  } catch (e) {}
}

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch (e) {
    return null
  }
}

export function clearToken() {
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch (e) {}
}

function base64UrlDecode(value) {
  const base64 = value.replace(/-/g, '+').replace(/_/g, '/')
  const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4)
  return JSON.parse(atob(padded))
}

export function getSession() {
  const token = getToken()
  if (!token || !token.includes('.')) return null
  try {
    const [payload] = token.split('.')
    const data = base64UrlDecode(payload)
    if (data.exp && Date.now() / 1000 >= data.exp) {
      clearToken()
      return null
    }
    return data
  } catch (e) {
    return null
  }
}

export function getCurrentUser() {
  const session = getSession()
  return session?.user || session || null
}

export async function login({ email, password }) {
  // Development fallback login helper — expects backend /api/auth/login returning { token, user }
  try {
    const res = await fetch((import.meta.env.VITE_API_BASE_URL || '') + '/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) throw new Error('Login failed')
    const data = await res.json()
    if (data?.token) setToken(data.token)
    return data
  } catch (e) {
    throw e
  }
}

export async function testLogin() {
  const res = await fetch((import.meta.env.VITE_API_BASE_URL || '') + '/api/auth/test-login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({}))
    throw new Error(error.detail || 'Test login failed')
  }
  const data = await res.json()
  if (data?.token) setToken(data.token)
  return data
}

export async function loginWithGoogle(idToken) {
  const res = await fetch((import.meta.env.VITE_API_BASE_URL || '') + '/api/auth/google', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_token: idToken }),
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({}))
    throw new Error(error.detail || 'Google sign-in failed')
  }
  const data = await res.json()
  if (data?.token) setToken(data.token)
  return data
}

export async function logout() {
  try {
    await fetch((import.meta.env.VITE_API_BASE_URL || '') + '/api/auth/logout', { method: 'POST' })
  } catch (e) {}
  clearToken()
}
