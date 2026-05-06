import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line, Bar } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  ChartTooltip,
  Legend,
  Filler
)

export default function ChartCard({ title, children, footer = null }) {
  return (
    <div className="card-base p-6">
      {title && <h3 className="text-lg font-semibold text-text-primary mb-6">{title}</h3>}
      
      {/* Chart content */}
      <div className="mb-4">{children}</div>

      {/* Footer */}
      {footer && (
        <div className="pt-4 border-t border-border text-xs text-text-secondary">
          {footer}
        </div>
      )}
    </div>
  )
}

export function SimpleChart({ data, height = 200 }) {
  const labels = data.map((d) => d.label)
  const values = data.map((d) => d.value)

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Value',
        data: values,
        backgroundColor: 'rgba(168,197,218,0.6)',
        borderColor: 'rgba(107,163,212,0.9)',
        borderWidth: 1,
        borderRadius: 6,
      },
    ],
  }

  const options = {
    maintainAspectRatio: false,
    scales: {
      x: { grid: { display: false }, ticks: { color: '#6B7280' } },
      y: { grid: { color: '#EEF2F7' }, ticks: { color: '#6B7280' } },
    },
    plugins: { legend: { display: false }, tooltip: { enabled: true } },
  }

  return (
    <div style={{ height }} className="w-full">
      <Bar data={chartData} options={options} />
    </div>
  )
}

export function LineChart({ data, height = 200 }) {
  if (!data || data.length < 2) return null

  const labels = data.map((d) => d.label)
  const values = data.map((d) => d.value)

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Trend',
        data: values,
        fill: true,
        backgroundColor: (ctx) => {
          const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, ctx.chart.height)
          gradient.addColorStop(0, 'rgba(168,197,218,0.35)')
          gradient.addColorStop(1, 'rgba(168,197,218,0)')
          return gradient
        },
        borderColor: 'rgba(107,163,212,0.95)',
        tension: 0.3,
        pointRadius: 3,
      },
    ],
  }

  const options = {
    maintainAspectRatio: false,
    scales: {
      x: { grid: { display: false }, ticks: { color: '#6B7280' } },
      y: { grid: { color: '#EEF2F7' }, ticks: { color: '#6B7280' } },
    },
    plugins: { legend: { display: false }, tooltip: { enabled: true } },
  }

  return (
    <div style={{ height }} className="w-full">
      <Line data={chartData} options={options} />
    </div>
  )
}
