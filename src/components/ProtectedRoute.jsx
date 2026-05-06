import { Navigate } from 'react-router-dom'
import { getToken } from '../lib/auth'

export default function ProtectedRoute({ children }) {
  // Auth disabled for development - allow all access
  return children
}
