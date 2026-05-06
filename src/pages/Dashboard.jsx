import Card from '../components/Card'
import StatCard from '../components/StatCard'
import Progress from '../components/Progress'
import { LineChart } from '../components/ChartCard'
import Avatar from '../components/Avatar'
import Badge from '../components/Badge'
import Tooltip from '../components/Tooltip'
import Button from '../components/Button'
import useSWR from 'swr'
import { fetchDashboard, fetchActivity } from '../lib/api'
import { useNavigate } from 'react-router-dom'
import { TrendingUp, Clock, CheckCircle, AlertCircle, Zap, Activity, ArrowUpRight, Sparkles, CircleDot } from 'lucide-react'

export default function Dashboard() {
  const navigate = useNavigate()
  const { data: dashboardData, error: dashError } = useSWR('/dashboard', fetchDashboard)
  const { data: activityData, error: activityError } = useSWR('/activity', fetchActivity)

  const stats = dashboardData?.stats || []
  const chartData = dashboardData?.chart || []
  const recentActivity = activityData?.items || []
  const summary = dashboardData?.summary || {}
  const systemHealth = dashboardData?.systemHealth || {}
  const statIcons = {
    'Validated Answers': CheckCircle,
    'Pending Review': Clock,
    'Queue Depth': TrendingUp,
    'Total Documents': Activity,
  }

  const isLoading = !dashboardData && !dashError

  return (
    <div className="space-y-8">
      {/* Executive Hero */}
      <section className="grid grid-cols-1 xl:grid-cols-[1.3fr_0.9fr] gap-6 items-stretch">
        <Card className="relative overflow-hidden border border-white/80 shadow-[0_18px_50px_rgba(15,23,42,0.08)]">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_100%_0%,rgba(168,197,218,0.18),transparent_28%),radial-gradient(circle_at_0%_100%,rgba(107,163,212,0.12),transparent_24%)]" />
          <div className="relative flex flex-col gap-6">
            <div className="flex flex-wrap items-center gap-3">
              <span className="inline-flex items-center gap-2 rounded-full border border-border bg-white/80 px-3 py-1.5 text-xs font-medium text-text-secondary">
                <Sparkles size={13} className="text-accent" />
                Premium ops console
              </span>
              <span className="inline-flex items-center gap-2 rounded-full border border-emerald-100 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700">
                <CircleDot size={13} />
                Uptime
              </span>
            </div>

            <div className="max-w-2xl space-y-4">
              <h1 className="text-4xl lg:text-5xl font-semibold tracking-tight text-text-primary leading-[1.04]">
                SecureAnswer keeps approved knowledge moving without friction.
              </h1>
              <p className="text-base lg:text-lg text-text-secondary max-w-xl">
                Track validation, review, freshness, and export workflows in one command center built for enterprise teams.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Button
                variant="primary"
                size="lg"
                className="inline-flex items-center gap-2"
                onClick={() => navigate('/review-queue')}
              >
                Open review queue
                <ArrowUpRight size={16} />
              </Button>
              <Button
                variant="secondary"
                size="lg"
                onClick={() => {
                  const systemHealthSection = document.getElementById('system-health')
                  systemHealthSection?.scrollIntoView({ behavior: 'smooth', block: 'start' })
                }}
              >
                View system health
              </Button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
              {[
                  { label: 'Validated answers', value: summary.approved_chunks ?? '-', hint: 'Stored in Supabase' },
                  { label: 'Pending review', value: summary.pending_chunks ?? '-', hint: 'Awaiting approval' },
                  { label: 'Documents', value: summary.total_documents ?? '-', hint: 'Live indexed content' },
                ].map((item) => (
                  <div key={item.label} className="rounded-2xl border border-border bg-white/70 px-4 py-4 shadow-xs">
                    <p className="text-xs uppercase tracking-[0.2em] text-text-secondary">{item.label}</p>
                    <p className="mt-2 text-2xl font-semibold text-text-primary">{item.value}</p>
                    <p className="mt-1 text-xs text-text-secondary">{item.hint}</p>
                  </div>
                ))}
            </div>
          </div>
        </Card>

        <Card className="flex flex-col gap-5 border border-white/80 shadow-[0_18px_50px_rgba(15,23,42,0.08)]">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-text-secondary">Live brief</p>
              <h3 className="text-lg font-semibold text-text-primary mt-1">Operational snapshot</h3>
            </div>
            <Badge variant="success">Healthy</Badge>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'Queue depth', value: summary.queue_depth ?? '-', tone: 'text-text-primary' },
              { label: 'Freshness', value: `${summary.freshness ?? 0}%`, tone: 'text-success' },
              { label: 'Rejected today', value: summary.rejected_today ?? '-', tone: 'text-warning' },
              { label: 'Exports ready', value: summary.exports_ready ?? '-', tone: 'text-info' },
            ].map((item) => (
              <div key={item.label} className="rounded-2xl border border-border bg-bg-secondary/70 px-4 py-4">
                <p className="text-xs uppercase tracking-[0.2em] text-text-secondary">{item.label}</p>
                <p className={`mt-2 text-3xl font-semibold ${item.tone}`}>{item.value}</p>
              </div>
            ))}
          </div>

          <div className="rounded-2xl border border-border bg-white px-4 py-4 shadow-xs">
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm font-medium text-text-primary">Momentum</p>
              <span className="text-xs text-text-secondary">Last 7 days</span>
            </div>
            <LineChart data={chartData} height={160} />
          </div>
        </Card>
      </section>

      {/* Trust Strip */}
      <Card className="border border-white/80 shadow-xs">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.22em] text-text-secondary">Trusted workflow</p>
            <p className="mt-1 text-sm text-text-primary">
              Enterprise teams use SecureAnswer to keep answers consistent across support, sales, and compliance.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {['Support', 'Operations', 'Compliance', 'Sales'].map((item) => (
              <span key={item} className="rounded-full border border-border bg-bg-secondary px-3 py-1.5 text-xs font-medium text-text-secondary">
                {item}
              </span>
            ))}
          </div>
        </div>
      </Card>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <StatCard
            key={idx}
            icon={statIcons[stat.label]}
            label={stat.label}
            value={stat.value}
            change={stat.change}
            changeType={stat.changeType}
            footer={stat.footer}
          />
        ))}
      </div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Health */}
        <Card id="system-health" className="lg:col-span-1 border border-white/80 shadow-[0_14px_40px_rgba(15,23,42,0.06)]">
          <div className="flex items-center gap-2 mb-6">
            <Activity className="text-primary" size={20} />
            <h3 className="text-lg font-semibold text-text-primary">System Health</h3>
          </div>
          
          <div className="space-y-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-text-primary">Processing Queue</span>
                <Tooltip content={`${systemHealth.processingQueue ?? 0} items waiting`}>
                  <span className="text-sm font-semibold text-text-primary cursor-help">{systemHealth.processingQueue ?? 0}</span>
                </Tooltip>
              </div>
              <Progress value={Math.min(100, (systemHealth.processingQueue ?? 0) * 10)} max={100} />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-text-primary">Storage Used</span>
                <span className="text-sm font-semibold text-text-primary">{systemHealth.storageUsed || '0 chunks'}</span>
              </div>
              <Progress value={Math.min(100, (summary.total_chunks ?? 0) * 2)} max={100} />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-text-primary">API Uptime</span>
                <Badge variant="success" className="text-xs">{systemHealth.apiUptime || '0%'}</Badge>
              </div>
              <Progress value={systemHealth.apiUptime === '99.9%' ? 99.9 : 0} max={100} />
            </div>

            <div className="pt-4 border-t border-border">
              <p className="text-xs text-text-secondary mb-3">Response Times</p>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-text-secondary">p50</span>
                  <span className="text-xs font-semibold text-success">{systemHealth.responseP50 || '-'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-text-secondary">p95</span>
                  <span className="text-xs font-semibold text-primary">{systemHealth.responseP95 || '-'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-text-secondary">p99</span>
                  <span className="text-xs font-semibold text-warning">{systemHealth.responseP99 || '-'}</span>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Query Trends Chart */}
        <Card className="lg:col-span-2 border border-white/80 shadow-[0_14px_40px_rgba(15,23,42,0.06)]">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-text-secondary">Product signal</p>
              <h3 className="text-lg font-semibold text-text-primary mt-1">Query Trend (7 days)</h3>
            </div>
            <Badge variant="info">Live data</Badge>
          </div>
          <LineChart data={chartData} height={260} />
          <div className="mt-6 pt-4 border-t border-border">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-text-secondary mb-1">Total</p>
                  <p className="text-xl font-bold text-text-primary">{summary.query_total ?? 0}</p>
              </div>
              <div>
                <p className="text-xs text-text-secondary mb-1">Avg/Day</p>
                  <p className="text-xl font-bold text-text-primary">{summary.avg_per_day ?? 0}</p>
              </div>
              <div>
                <p className="text-xs text-text-secondary mb-1">Peak</p>
                  <p className="text-xl font-bold text-text-primary">{summary.peak ?? 0}</p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card className="border border-white/80 shadow-[0_14px_40px_rgba(15,23,42,0.06)]">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-text-primary">Recent Activity</h3>
          <Tooltip content="View all activities">
            <button className="text-sm text-primary hover:text-accent transition-smooth cursor-pointer">
              View All →
            </button>
          </Tooltip>
        </div>

        <div className="space-y-4">
          {recentActivity.map((activity) => (
            <div
              key={activity.id}
              className="flex items-start gap-4 p-4 rounded-2xl border border-transparent hover:bg-bg-secondary hover:border-border transition-smooth"
            >
              <Avatar
                initials={activity.user}
                name={activity.userName}
                size="sm"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-semibold text-text-primary">
                    {activity.type}
                  </span>
                  <Badge
                    variant={activity.status === 'completed' ? 'success' : 'warning'}
                    className="text-xs"
                  >
                    {activity.status}
                  </Badge>
                </div>
                <p className="text-sm text-text-secondary">
                  {typeof activity.details === 'string' ? activity.details : JSON.stringify(activity.details || {})}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <Clock size={14} className="text-text-tertiary" />
                  <p className="text-xs text-text-tertiary">{activity.timestamp}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
