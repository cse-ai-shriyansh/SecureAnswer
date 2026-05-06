import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Upload,
  BookOpen,
  Search,
  Zap,
  Shield,
  ClipboardList,
  BookMarked,
  Eye,
  RefreshCw,
  Download,
  Menu,
  X,
  Settings,
  LogOut,
  Bell,
  HelpCircle,
} from 'lucide-react'
import { useState } from 'react'
import Avatar from './Avatar'
import Tooltip from './Tooltip'
import { getSession, logout } from '../lib/auth'

const sidebarItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
  { icon: Upload, label: 'Ingestion', path: '/ingestion' },
  { icon: BookOpen, label: 'Knowledge Base', path: '/knowledge-base' },
  { icon: Search, label: 'Retrieval', path: '/retrieval' },
  { icon: Zap, label: 'Generation', path: '/generation' },
  { icon: Shield, label: 'Validation', path: '/validation' },
  { icon: ClipboardList, label: 'Review Queue', path: '/review-queue' },
  { icon: BookMarked, label: 'Answer Library', path: '/answer-library' },
  { icon: Eye, label: 'Insights', path: '/insights' },
  { icon: RefreshCw, label: 'Freshness Monitor', path: '/freshness' },
  { icon: Download, label: 'Exports', path: '/exports' },
]

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [notificationOpen, setNotificationOpen] = useState(false)
  const [notificationCount, setNotificationCount] = useState(0)
  const [notifications, setNotifications] = useState([])
  const [profileOpen, setProfileOpen] = useState(false)
  const session = getSession()
  const location = useLocation()
  
  // Use default values if auth is disabled
  const userName = session?.name || session?.user?.name || session?.email || 'Developer'
  const userEmail = session?.email || session?.user?.email || 'dev@secureanswer.local'
  const userRole = session?.provider ? session.provider : 'Development mode'
  const userInitials = userName
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('') || 'SA'

  return (
    <div className="flex min-h-screen bg-transparent overflow-hidden text-text-primary">
      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-full w-72 bg-white/85 backdrop-blur-xl border-r border-white/70 shadow-[8px_0_36px_rgba(15,23,42,0.05)] transition-smooth z-40 lg:static lg:z-auto ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="px-6 py-6 border-b border-border/70">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-text-primary flex items-center justify-center shadow-sm">
                  <div className="w-4 h-4 rounded-full bg-secondary" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold tracking-tight text-text-primary">SecureAnswer</h1>
                  <p className="text-xs text-text-secondary">Enterprise knowledge ops</p>
                </div>
              </div>
              <span className="inline-flex items-center rounded-full border border-border bg-bg-secondary px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-text-secondary">
                Live
              </span>
            </div>
            <p className="text-xs text-text-secondary leading-5">
              Command center for approved answers, audits, and knowledge freshness.
            </p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto px-4 py-6">
            <div className="mb-4 rounded-2xl border border-border bg-bg-secondary/80 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-text-secondary mb-1">
                Workspace
              </p>
              <p className="text-sm font-medium text-text-primary">Live backend connected</p>
              <p className="text-xs text-text-secondary mt-1">Session authenticated via API</p>
            </div>
            <ul className="space-y-1.5">
              {sidebarItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <li key={item.path}>
                    <Link
                      to={item.path}
                      onClick={() => setSidebarOpen(false)}
                      className={`group flex items-center gap-3 px-4 py-3 rounded-2xl transition-smooth border ${
                        isActive
                          ? 'bg-text-primary text-white border-text-primary shadow-sm'
                          : 'text-text-secondary border-transparent hover:bg-bg-secondary hover:border-border'
                      }`}
                    >
                      <Icon size={18} className={isActive ? 'text-white' : 'text-text-secondary group-hover:text-text-primary'} />
                      <span className="text-sm font-medium">{item.label}</span>
                    </Link>
                  </li>
                )
              })}
            </ul>
          </nav>

          {/* Footer */}
          <div className="border-t border-border/70 px-4 py-6 space-y-2 bg-gradient-to-b from-transparent to-bg-secondary/70">
            <Tooltip content="Settings">
              <button className="w-full flex items-center gap-3 px-4 py-2.5 rounded-2xl text-text-secondary hover:bg-white transition-smooth border border-transparent hover:border-border">
                <Settings size={20} />
                <span className="text-sm">Settings</span>
              </button>
            </Tooltip>
              <Tooltip content="Logout">
              <button
                onClick={() => {
                  clearToken()
                  window.location.href = '/login'
                }}
                className="w-full flex items-center gap-3 px-4 py-2.5 rounded-2xl text-text-secondary hover:bg-white transition-smooth border border-transparent hover:border-border"
              >
                <LogOut size={20} />
                <span className="text-sm">Logout</span>
              </button>
            </Tooltip>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(168,197,218,0.14),transparent_28%),radial-gradient(circle_at_15%_20%,rgba(255,255,255,0.55),transparent_24%)]" />
        {/* Top navigation bar */}
        <header className="sticky top-0 z-20 bg-white/70 backdrop-blur-xl border-b border-white/70 px-6 py-4 shadow-xs">
          <div className="flex items-center justify-between gap-6">
            {/* Left */}
            <div className="flex items-center gap-4">
              {/* Mobile menu button */}
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-lg hover:bg-bg-secondary transition-smooth"
              >
                {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
              </button>

              {/* Page title */}
              <div className="hidden sm:block">
                <h2 className="text-xl font-semibold text-text-primary">
                  {sidebarItems.find((item) => item.path === location.pathname)?.label}
                </h2>
                <p className="text-xs text-text-secondary">Premium operations console</p>
              </div>
            </div>

            {/* Right - Actions */}
            <div className="flex items-center gap-4">
              <span className="hidden xl:inline-flex items-center rounded-full border border-border bg-white px-3 py-1.5 text-xs font-medium text-text-secondary shadow-xs">
                Production connected
              </span>
              {/* Search */}
              <div className="hidden md:flex items-center gap-2 bg-bg-secondary rounded-lg px-3 py-2">
                <Search size={18} className="text-text-secondary opacity-50" />
                <input
                  type="text"
                  placeholder="Search answers, docs, people"
                  className="bg-transparent border-none outline-none text-sm w-44 placeholder-text-tertiary"
                />
              </div>

              {/* Help */}
              <Tooltip content="Help Center">
                <button className="p-2 rounded-lg hover:bg-bg-secondary transition-smooth text-text-secondary hover:text-text-primary">
                  <HelpCircle size={20} />
                </button>
              </Tooltip>

              {/* Notifications */}
              <Tooltip content="Notifications">
                <button
                  onClick={() => setNotificationOpen(!notificationOpen)}
                  className="p-2 rounded-lg hover:bg-bg-secondary transition-smooth text-text-secondary hover:text-text-primary relative"
                >
                  <Bell size={20} />
                  {notificationCount > 0 && (
                    <div className="absolute top-0 right-0 -mt-1 -mr-1 w-4 h-4 bg-danger rounded-full flex items-center justify-center text-xs text-white">
                      {notificationCount}
                    </div>
                  )}
                </button>
              </Tooltip>

              {/* Notifications dropdown */}
              {notificationOpen && (
                <div className="absolute right-16 top-14 w-80 bg-white/95 backdrop-blur-xl rounded-2xl border border-white/80 shadow-xl z-50 animate-slide-down">
                  <div className="p-3 border-b border-border font-semibold">Notifications</div>
                  <div className="max-h-64 overflow-auto p-2 space-y-2">
                    {notifications.length === 0 ? (
                      <div className="p-3 text-xs text-text-secondary">No notifications</div>
                    ) : (
                      notifications.map((n, idx) => (
                        <div key={idx} className="p-2 rounded hover:bg-bg-secondary">
                          <div className="text-sm font-medium">{n.title}</div>
                          <div className="text-xs text-text-secondary">{n.body}</div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}

              {/* User Profile */}
              <div className="relative">
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-3 p-2 rounded-2xl hover:bg-bg-secondary transition-smooth border border-transparent hover:border-border"
                >
                  <Avatar initials={userInitials} name={userName} size="md" status="online" />
                  <div className="hidden sm:block text-left">
                      <p className="text-sm font-medium text-text-primary">{userName}</p>
                      <p className="text-xs text-text-secondary">{userRole}</p>
                    </div>
                </button>

                {/* Profile Dropdown */}
                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white/95 backdrop-blur-xl rounded-2xl border border-white/80 shadow-xl z-50 animate-slide-down">
                    <div className="px-4 py-3 border-b border-border">
                      <p className="text-sm font-semibold text-text-primary">{userName}</p>
                      <p className="text-xs text-text-secondary">{userEmail}</p>
                    </div>
                    <div className="py-2">
                      <button className="w-full px-4 py-2 text-sm text-text-secondary hover:bg-bg-secondary hover:text-text-primary transition-smooth text-left">
                        Profile
                      </button>
                      <button className="w-full px-4 py-2 text-sm text-text-secondary hover:bg-bg-secondary hover:text-text-primary transition-smooth text-left">
                        Preferences
                      </button>
                      <button className="w-full px-4 py-2 text-sm text-text-secondary hover:bg-bg-secondary hover:text-text-primary transition-smooth text-left">
                        Team Settings
                      </button>
                    </div>
                    <div className="py-2 border-t border-border">
                      <button
                        onClick={async () => {
                          try {
                            await logout()
                          } catch (e) {
                            // Auth disabled - just continue
                          }
                          window.location.href = '/login'
                        }}
                        className="w-full px-4 py-2 text-sm text-danger hover:bg-red-50 transition-smooth text-left"
                      >
                        Sign Out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Main content area */}
        <main className="flex-1 overflow-auto relative">
          <div className="mx-auto w-full max-w-[1600px] p-6 md:p-8 lg:p-10">{children}</div>
        </main>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 lg:hidden z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}
