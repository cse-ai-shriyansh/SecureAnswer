import Card from '../components/Card'
import Badge from '../components/Badge'
import Button from '../components/Button'
import { AlertTriangle, Calendar, RotateCcw, Eye, Edit } from 'lucide-react'
import { useMemo } from 'react'
import useSWR from 'swr'
import { fetchFreshness } from '../lib/api'

export default function FreshnessMonitor() {
  const { data } = useSWR('/freshness', fetchFreshness, { refreshInterval: 15000 })
  const staleAnswers = data?.stale || []
  const freshnessScore = useMemo(() => {
    const documents = data?.documents || []
    if (!documents.length) return null

    const now = new Date()
    const scores = documents.map((doc) => {
      const lastUpdated = new Date(doc.lastUpdated)
      const ageInDays = Number.isNaN(lastUpdated.getTime())
        ? 30
        : Math.max(0, (now - lastUpdated) / (1000 * 60 * 60 * 24))

      let score = 100 - Math.min(70, ageInDays * 2.2)
      if (doc.status === 'pending') score -= 8
      if (doc.status === 'rejected') score -= 18
      return Math.max(0, Math.min(100, score))
    })

    return Math.round(scores.reduce((sum, value) => sum + value, 0) / scores.length)
  }, [data?.documents])

  const freshnessColor = (() => {
    if (freshnessScore == null) return 'text-text-secondary'
    if (freshnessScore >= 80) return 'text-emerald-600'
    if (freshnessScore >= 60) return 'text-amber-500'
    return 'text-red-500'
  })()

  const freshnessLabel = (() => {
    if (freshnessScore == null) return 'No data'
    if (freshnessScore >= 80) return 'Healthy'
    if (freshnessScore >= 60) return 'Needs attention'
    return 'Stale'
  })()

  const meterOffset = freshnessScore == null ? 264 : 264 - (264 * freshnessScore) / 100

  const getStalenessColor = (staleness) => {
    switch (staleness) {
      case 'critical':
        return { bg: 'bg-red-100', text: 'text-red-700', badge: 'danger' }
      case 'warning':
        return { bg: 'bg-yellow-100', text: 'text-yellow-700', badge: 'warning' }
      case 'caution':
        return { bg: 'bg-blue-100', text: 'text-blue-700', badge: 'info' }
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-700', badge: 'default' }
    }
  }

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high':
        return 'bg-red-100 text-red-700'
      case 'medium':
        return 'bg-yellow-100 text-yellow-700'
      case 'low':
        return 'bg-blue-100 text-blue-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const stats = data?.stats || []

  const criticalCount = staleAnswers.filter((a) => a.staleness === 'critical').length
  const warningCount = staleAnswers.filter((a) => a.staleness === 'warning').length

  return (
    <div className="space-y-8">
      {/* Alert */}
      {criticalCount > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 flex items-start gap-3">
          <AlertTriangle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <h3 className="font-semibold text-red-700 mb-1">Urgent Action Required</h3>
            <p className="text-sm text-red-600">
              You have {criticalCount} critical answers that need immediate updates. These answers are likely causing user confusion.
            </p>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <Card key={idx}>
            <p className="text-xs text-text-secondary mb-1">{stat.label}</p>
            <p className="text-2xl font-semibold text-text-primary">{stat.value}</p>
          </Card>
        ))}
      </div>

      {/* Freshness Score Gauge */}
      <Card>
        <h3 className="text-lg font-semibold text-text-primary mb-6">Overall Freshness</h3>
        <div className="flex flex-col md:flex-row items-center gap-8">
          {/* Meter */}
          <div className="flex-shrink-0 w-44 h-44 relative">
            <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
              <defs>
                <linearGradient id="freshness-meter-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#ef4444" />
                  <stop offset="35%" stopColor="#f59e0b" />
                  <stop offset="70%" stopColor="#84cc16" />
                  <stop offset="100%" stopColor="#22c55e" />
                </linearGradient>
              </defs>

              <circle cx="60" cy="60" r="42" fill="none" stroke="#e5e7eb" strokeWidth="10" />
              <circle
                cx="60"
                cy="60"
                r="42"
                fill="none"
                stroke="url(#freshness-meter-gradient)"
                strokeWidth="10"
                strokeLinecap="round"
                strokeDasharray="264"
                strokeDashoffset={meterOffset}
              />

              <circle cx="60" cy="60" r="28" fill="white" stroke="#e5e7eb" strokeWidth="1.5" />
              <line
                x1="60"
                y1="60"
                x2={freshnessScore == null ? 60 : 60 + Math.cos((Math.PI * 2 * freshnessScore) / 100 - Math.PI / 2) * 32}
                y2={freshnessScore == null ? 28 : 60 + Math.sin((Math.PI * 2 * freshnessScore) / 100 - Math.PI / 2) * 32}
                stroke="#111827"
                strokeWidth="3"
                strokeLinecap="round"
              />
              <circle cx="60" cy="60" r="4" fill="#111827" />
            </svg>

            <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
              <p className={`text-4xl font-semibold ${freshnessColor}`}>
                {freshnessScore == null ? '-' : `${freshnessScore}%`}
              </p>
              <p className="mt-1 text-xs uppercase tracking-[0.22em] text-text-secondary">
                {freshnessLabel}
              </p>
            </div>
          </div>

          {/* Details */}
          <div className="flex-1">
            <p className={`text-4xl font-bold mb-2 ${freshnessColor}`}>
              {freshnessScore == null ? '-' : `${freshnessScore}%`}
            </p>
            <p className="text-text-secondary text-sm mb-6">
              {freshnessScore == null
                ? 'Overall freshness metrics are available when the system reports data.'
                : 'This meter is derived from document age and review status in the latest backend response.'}
            </p>
            <Button variant="primary">Refresh All Stale Answers</Button>
          </div>
        </div>
      </Card>

      {/* Stale Answers List */}
      <Card>
        <h3 className="text-lg font-semibold text-text-primary mb-6">Stale Answers</h3>
        <div className="space-y-3">
          {staleAnswers.map((answer) => {
            const colors = getStalenessColor(answer.staleness)
            return (
              <div
                key={answer.id}
                className={`border border-border rounded-md p-4 hover:border-primary transition-smooth ${colors.bg}`}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className={`font-semibold text-sm ${colors.text}`}>
                        {answer.question}
                      </h4>
                      <Badge variant={colors.badge} className="text-xs">
                        {answer.staleness.charAt(0).toUpperCase() + answer.staleness.slice(1)}
                      </Badge>
                    </div>
                    <p className={`text-xs ${colors.text} opacity-75`}>
                      Last updated: {answer.lastUpdated}
                    </p>
                  </div>
                  <Badge variant="default" className={`text-xs flex-shrink-0 ${getImpactColor(answer.impact)}`}>
                    {answer.impact} impact
                  </Badge>
                </div>

                {/* Reason */}
                <div className="mb-3 p-3 bg-white bg-opacity-50 rounded text-sm text-text-primary">
                  <p className="font-medium mb-1">Reason for staleness:</p>
                  <p className="text-text-secondary text-sm">{answer.reason}</p>
                </div>

                {/* Stats */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 text-xs text-text-secondary">
                    <Eye size={14} />
                    {answer.views} views this month
                  </div>
                  <div className="text-xs text-text-secondary">
                    {Math.ceil(
                      (new Date() - new Date(Date.now() - parseInt(answer.lastUpdated) * 86400000)) / (1000 * 60 * 60 * 24)
                    )}{' '}
                    days old
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button variant="primary" size="sm" className="flex-1">
                    <Edit size={16} className="inline mr-1" />
                    Update Now
                  </Button>
                  <Button variant="ghost" size="sm">
                    <RotateCcw size={16} />
                  </Button>
                </div>
              </div>
            )
          })}
        </div>
      </Card>

      {/* Freshness Timeline */}
      <Card>
        <h3 className="text-lg font-semibold text-text-primary mb-6">Update Timeline</h3>
        <div className="space-y-4">
          {[
            { days: 'Last 7 days', count: 12, percentage: 15 },
            { days: 'Last 14 days', count: 18, percentage: 22 },
            { days: 'Last 30 days', count: 34, percentage: 42 },
            { days: 'Last 90 days', count: 52, percentage: 64 },
          ].map((period, idx) => (
            <div key={idx}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-text-primary">{period.days}</span>
                <span className="text-sm font-medium text-text-primary">{period.count} answers</span>
              </div>
              <div className="w-full bg-border rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: `${period.percentage}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
