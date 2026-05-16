import { Navigate, useLocation } from 'react-router-dom'
import { getSession } from '../lib/auth'

export default function ProtectedRoute({ children }) {
  const location = useLocation()
  const session = getSession()

  const enableDevLogin = import.meta.env.DEV || import.meta.env.VITE_ENABLE_DEV_LOGIN === 'true'
  const enableTestLogin = import.meta.env.DEV || import.meta.env.VITE_ENABLE_TEST_LOGIN === 'true'
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  const authConfigured = Boolean(googleClientId || enableDevLogin || enableTestLogin)

  // Keep legacy behavior only when auth is not configured at all.
  if (!authConfigured) return children

  if (!session) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  return children
}
