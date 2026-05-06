import Card from '../components/Card'
import StatCard from '../components/StatCard'
import Progress from '../components/Progress'
import Badge from '../components/Badge'
import Button from '../components/Button'
import Tooltip from '../components/Tooltip'
import useSWR from 'swr'
import { fetchValidation } from '../lib/api'
import { AlertTriangle, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react'

export default function Validation() {
  const { data, error } = useSWR('/validation', fetchValidation, { refreshInterval: 8000 })
  const validations = data?.items || []

  const getRiskColor = (score) => {
    if (score < 0.3) return { variant: 'success', label: 'Low' }
    if (score < 0.6) return { variant: 'warning', label: 'Medium' }
    return { variant: 'danger', label: 'High' }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return CheckCircle
      case 'warning':
        return AlertCircle
      case 'rejected':
        return AlertTriangle
      default:
        return null
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'approved':
        return 'success'
      case 'warning':
        return 'warning'
      case 'rejected':
        return 'danger'
      default:
        return 'default'
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-text-primary mb-2">Answer Validation</h1>
        <p className="text-text-secondary">Monitor quality metrics and risk scores for all answers.</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard icon={CheckCircle} label="Approved" value="-" changeType="positive" footer="" />
        <StatCard icon={AlertCircle} label="Needs Review" value="-" changeType="neutral" footer="" />
        <StatCard icon={AlertTriangle} label="Rejected" value="-" changeType="positive" footer="" />
        <StatCard icon={TrendingUp} label="Avg Risk Score" value="-" changeType="positive" footer="" />
      </div>

      {/* Validations List */}
      <Card>
        <h3 className="text-lg font-semibold text-text-primary mb-6">Recent Validations</h3>
        <div className="space-y-4">
          {validations.map((validation) => {
            const riskColor = getRiskColor(validation.riskScore)
            const StatusIcon = getStatusIcon(validation.status)

            return (
              <div
                key={validation.id}
                className="border border-border rounded-lg p-4 hover:shadow-md hover:border-primary transition-smooth"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start gap-4 flex-1">
                    {StatusIcon && (
                      <Tooltip content={validation.status}>
                        <StatusIcon size={20} className="flex-shrink-0 mt-1 cursor-help" />
                      </Tooltip>
                    )}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className="text-sm font-semibold text-text-primary">
                          {validation.answerId}
                        </span>
                        <span className="text-xs text-text-secondary">—</span>
                        <span className="text-sm text-text-primary">{validation.question}</span>
                      </div>
                      <div className="flex items-center gap-2 mt-2 flex-wrap">
                        <Badge variant={getStatusBadge(validation.status)} className="text-xs">
                          {validation.status}
                        </Badge>
                        <span className="text-xs text-text-secondary">{validation.reviewedAt}</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <Tooltip content={`Risk Level: ${riskColor.label}`}>
                      <div className="flex-shrink-0 px-4 py-2 rounded-lg font-semibold text-sm cursor-help">
                        <Badge variant={riskColor.variant}>
                          {(validation.riskScore * 100).toFixed(0)}
                        </Badge>
                      </div>
                    </Tooltip>
                  </div>
                </div>

                {/* Flags */}
                {validation.flags.length > 0 && (
                  <div className="mb-4 p-3 bg-red-50 rounded-lg border border-red-200">
                    <p className="text-xs font-semibold text-red-700 mb-2">⚠ Detected Issues:</p>
                    <ul className="space-y-1">
                      {validation.flags.map((flag, idx) => (
                        <li key={idx} className="text-xs text-red-600 ml-2">
                          • {flag}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Metrics */}
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <Progress
                    value={validation.metrics.relevance * 100}
                    max={100}
                    label="Relevance"
                    size="sm"
                  />
                  <Progress
                    value={validation.metrics.factuality * 100}
                    max={100}
                    label="Factuality"
                    size="sm"
                  />
                  <Progress
                    value={validation.metrics.completeness * 100}
                    max={100}
                    label="Completeness"
                    size="sm"
                  />
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between">
                  <span className="text-xs text-text-secondary">
                    Reviewed by <span className="font-medium">{validation.reviewedBy}</span>
                  </span>
                  {validation.status === 'warning' && (
                    <Button variant="secondary" size="sm">
                      Review
                    </Button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </Card>

      {/* Risk Distribution */}
      <Card>
        <h3 className="text-lg font-semibold text-text-primary mb-6">Risk Score Distribution</h3>
        <div className="space-y-6">
            {/* Risk distribution will be shown when data is available */}
            {[]}
        </div>
      </Card>
    </div>
  )
}
