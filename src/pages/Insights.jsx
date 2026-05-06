import Card from '../components/Card'
import Badge from '../components/Badge'
import { TrendingUp, BarChart3, PieChart, LineChart as LCIcon } from 'lucide-react'
import useSWR from 'swr'
import { fetchInsights } from '../lib/api'

export default function Insights() {
  const metrics = []

  const { data } = useSWR('/insights', fetchInsights, { refreshInterval: 15000 })
  const topQuestions = data?.topQuestions || []

  const categoryBreakdown = data?.categoryBreakdown || []

  const hourlyTrend = data?.hourlyTrend || []

  const maxQueries = hourlyTrend.length ? Math.max(...hourlyTrend.map((h) => h.queries)) : 1

  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, idx) => (
          <Card key={idx}>
            <p className="text-xs text-text-secondary mb-1">{metric.label}</p>
            <p className="text-2xl font-semibold text-text-primary">{metric.value}</p>
            <p className={`text-xs mt-2 ${metric.positive ? 'text-green-600' : 'text-red-600'}`}>
              {metric.change} vs last month
            </p>
          </Card>
        ))}
      </div>

      {/* Top Questions & Category Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Questions */}
        <Card>
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp size={20} className="text-primary" />
            <h3 className="text-lg font-semibold text-text-primary">Top Questions</h3>
          </div>
          <div className="space-y-3">
            {topQuestions.map((item) => (
              <div key={item.rank} className="flex items-center justify-between pb-3 border-b border-border last:border-b-0">
                <div className="flex items-center gap-3 flex-1">
                  <div className="w-6 h-6 rounded-full bg-secondary flex items-center justify-center text-xs font-semibold text-primary">
                    {item.rank}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-text-primary">{item.question}</p>
                    <p className="text-xs text-text-secondary mt-1">{item.count} queries</p>
                  </div>
                </div>
                <Badge variant="info" className="text-xs flex-shrink-0">
                  {item.trend}
                </Badge>
              </div>
            ))}
          </div>
        </Card>

        {/* Category Breakdown */}
        <Card>
          <div className="flex items-center gap-2 mb-6">
            <PieChart size={20} className="text-primary" />
            <h3 className="text-lg font-semibold text-text-primary">By Category</h3>
          </div>
          <div className="space-y-4">
            {categoryBreakdown.map((item, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-text-primary">{item.category}</span>
                  <span className="text-sm text-text-secondary">{item.percentage}%</span>
                </div>
                <div className="w-full bg-border rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${item.percentage}%` }}
                  ></div>
                </div>
                <p className="text-xs text-text-secondary mt-1">{item.count} queries</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Hourly Trend */}
      <Card>
        <div className="flex items-center gap-2 mb-6">
          <LCIcon size={20} className="text-primary" />
          <h3 className="text-lg font-semibold text-text-primary">Query Trend (24h)</h3>
        </div>

        {/* Simple Bar Chart */}
        <div className="space-y-3">
          {hourlyTrend.map((item) => (
            <div key={item.hour} className="flex items-center gap-3">
              <span className="text-xs text-text-secondary w-12">{item.hour}</span>
              <div className="flex-1">
                <div className="bg-border rounded-full h-6 relative">
                  <div
                    className="bg-primary h-6 rounded-full transition-all duration-300 flex items-center justify-end pr-2"
                    style={{ width: `${(item.queries / maxQueries) * 100}%` }}
                  >
                    {(item.queries / maxQueries) * 100 > 15 && (
                      <span className="text-xs font-medium text-white">{item.queries}</span>
                    )}
                  </div>
                </div>
              </div>
              <span className="text-xs font-medium text-text-primary w-12 text-right">
                {item.queries}
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* Performance Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-semibold text-text-primary mb-6">Response Quality</h3>
          <div className="space-y-4">
            {[
              { label: 'Relevance', value: 92 },
              { label: 'Accuracy', value: 88 },
              { label: 'Completeness', value: 85 },
              { label: 'Clarity', value: 90 },
            ].map((item, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-text-primary">{item.label}</span>
                  <span className="text-sm font-semibold text-text-primary">{item.value}%</span>
                </div>
                <div className="w-full bg-border rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full"
                    style={{ width: `${item.value}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold text-text-primary mb-6">System Health</h3>
          <div className="space-y-4">
            {[
              { label: 'API Uptime', value: 99.9, unit: '%' },
              { label: 'Avg Response Time', value: 342, unit: 'ms' },
              { label: 'Error Rate', value: 0.3, unit: '%' },
              { label: 'Daily Active Users', value: 2847, unit: '' },
            ].map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-bg-primary rounded-md"
              >
                <span className="text-sm text-text-secondary">{item.label}</span>
                <span className="text-sm font-semibold text-text-primary">
                  {item.value}
                  {item.unit}
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
