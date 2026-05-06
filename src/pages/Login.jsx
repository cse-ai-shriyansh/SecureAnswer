import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '../components/Button'
import Card from '../components/Card'
import { login, loginWithGoogle, testLogin } from '../lib/auth'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [googleReady, setGoogleReady] = useState(false)
  const googleButtonRef = useRef(null)
  const nav = useNavigate()
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  const enableDevLogin = import.meta.env.DEV || import.meta.env.VITE_ENABLE_DEV_LOGIN === 'true'
  const enableTestLogin = import.meta.env.DEV || import.meta.env.VITE_ENABLE_TEST_LOGIN === 'true'

  // Bypass login if auth is disabled
  useEffect(() => {
    if (!googleClientId && !enableDevLogin) {
      // Auth disabled - redirect to dashboard
      nav('/', { replace: true })
    }
  }, [googleClientId, enableDevLogin, nav])

  useEffect(() => {
    if (!googleClientId) return

    const existingScript = document.querySelector('script[data-google-identity]')
    const initGoogle = () => {
      if (!window.google?.accounts?.id || !googleButtonRef.current) return

      window.google.accounts.id.initialize({
        client_id: googleClientId,
        callback: async (response) => {
          setError(null)
          setLoading(true)
          try {
            await loginWithGoogle(response.credential)
            nav('/')
          } catch (err) {
            setError(err.message || 'Google sign-in failed')
          } finally {
            setLoading(false)
          }
        },
      })

      googleButtonRef.current.innerHTML = ''
      window.google.accounts.id.renderButton(googleButtonRef.current, {
        theme: 'outline',
        size: 'large',
        width: 320,
        text: 'signin_with',
        shape: 'pill',
      })
      setGoogleReady(true)
    }

    if (window.google?.accounts?.id) {
      initGoogle()
      return undefined
    }

    const script = existingScript || document.createElement('script')
    if (!existingScript) {
      script.src = 'https://accounts.google.com/gsi/client'
      script.async = true
      script.defer = true
      script.dataset.googleIdentity = 'true'
      script.onload = initGoogle
      document.head.appendChild(script)
    } else {
      script.onload = initGoogle
    }

    return undefined
  }, [googleClientId, nav])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login({ email, password })
      nav('/')
    } catch (e) {
      setError(e.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleTestLogin = async () => {
    setError(null)
    setLoading(true)
    try {
      await testLogin()
      nav('/')
    } catch (e) {
      setError(e.message || 'Test login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-transparent">
      <Card className="w-full max-w-md space-y-6">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-text-secondary mb-2">SecureAnswer</p>
          <h2 className="text-2xl font-semibold mb-2">Sign in</h2>
          <p className="text-sm text-text-secondary">Use Google OAuth for production access.</p>
        </div>

        {googleClientId ? (
          <div className="space-y-3">
            <div ref={googleButtonRef} className="min-h-[44px]" />
            {!googleReady && <p className="text-xs text-text-secondary">Loading Google sign-in…</p>}
          </div>
        ) : (
          <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            Google OAuth is not configured yet. Add <span className="font-medium">VITE_GOOGLE_CLIENT_ID</span> to enable production sign-in.
          </div>
        )}

        {enableDevLogin && (
          <form onSubmit={handleSubmit} className="space-y-4 pt-2 border-t border-border">
            <p className="text-xs uppercase tracking-[0.2em] text-text-secondary">Dev fallback</p>
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" className="input-base w-full" />
            <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password" className="input-base w-full" />
            {error && <div className="text-sm text-danger">{error}</div>}
            <div className="flex items-center gap-3">
              <Button type="submit" variant="primary" disabled={loading}>{loading ? 'Signing in…' : 'Sign in'}</Button>
            </div>
          </form>
        )}

        {!enableDevLogin && error && <div className="text-sm text-danger">{error}</div>}

        {enableTestLogin && (
          <div className="pt-2 border-t border-border">
            <p className="text-xs uppercase tracking-[0.2em] text-text-secondary mb-3">Testing access</p>
            <Button type="button" variant="secondary" disabled={loading} onClick={handleTestLogin}>
              {loading ? 'Signing in…' : 'Continue as test user'}
            </Button>
          </div>
        )}
      </Card>
    </div>
  )
}
