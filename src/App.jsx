import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Ingestion from './pages/Ingestion'
import KnowledgeBase from './pages/KnowledgeBase'
import RetrievalDebug from './pages/RetrievalDebug'
import AnswerGeneration from './pages/AnswerGeneration'
import Validation from './pages/Validation'
import ReviewQueue from './pages/ReviewQueue'
import AnswerLibrary from './pages/AnswerLibrary'
import Insights from './pages/Insights'
import FreshnessMonitor from './pages/FreshnessMonitor'
import Exports from './pages/Exports'
import Login from './pages/Login'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  const enableDevLogin = import.meta.env.DEV || import.meta.env.VITE_ENABLE_DEV_LOGIN === 'true'
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

  const routes = []

  // Only expose the login route when Google OAuth is configured or dev/test login is enabled
  if (googleClientId || enableDevLogin) {
    routes.push({ path: '/login', element: <Login /> })
  }

  routes.push(
    {
      path: '/',
      element: (
        <ProtectedRoute>
          <Layout>
            <Dashboard />
          </Layout>
        </ProtectedRoute>
      ),
    },
    {
      path: '/ingestion',
      element: (
        <ProtectedRoute>
          <Layout>
            <Ingestion />
          </Layout>
        </ProtectedRoute>
      ),
    },
    {
      path: '/knowledge-base',
      element: (
        <ProtectedRoute>
          <Layout>
            <KnowledgeBase />
          </Layout>
        </ProtectedRoute>
      ),
    },
    {
      path: '/retrieval',
      element: (
        <ProtectedRoute>
          <Layout>
            <RetrievalDebug />
          </Layout>
        </ProtectedRoute>
      ),
    },
    {
      path: '/generation',
      element: (
        <ProtectedRoute>
          <Layout>
            <AnswerGeneration />
          </Layout>
        </ProtectedRoute>
      ),
    },
    {
      path: '/validation',
      element: (
        <ProtectedRoute>
          <Layout>
            <Validation />
          </Layout>
        </ProtectedRoute>
      ),
    },
    {
      path: '/review-queue',
      element: (
        <ProtectedRoute>
          <Layout>
            <ReviewQueue />
          </Layout>
        </ProtectedRoute>
      ),
    },
    {
      path: '/answer-library',
      element: (
        <ProtectedRoute>
          <Layout>
            <AnswerLibrary />
          </Layout>
        </ProtectedRoute>
      ),
    },
    {
      path: '/insights',
      element: (
        <ProtectedRoute>
          <Layout>
            <Insights />
          </Layout>
        </ProtectedRoute>
      ),
    },
    {
      path: '/freshness',
      element: (
        <ProtectedRoute>
          <Layout>
            <FreshnessMonitor />
          </Layout>
        </ProtectedRoute>
      ),
    },
    {
      path: '/exports',
      element: (
        <ProtectedRoute>
          <Layout>
            <Exports />
          </Layout>
        </ProtectedRoute>
      ),
    }
  )

  const router = createBrowserRouter(routes, { future: { v7_startTransition: true } })

  return <RouterProvider router={router} />
}

export default App
