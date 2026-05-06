import Card from '../components/Card'
import Badge from '../components/Badge'
import Button from '../components/Button'
import { Download, File, Calendar, User, Clock, AlertCircle } from 'lucide-react'
import { useState } from 'react'
import useSWR from 'swr'
import { fetchExports, createExport } from '../lib/api'

export default function Exports() {
  const [exportFormat, setExportFormat] = useState('excel')
  const [selectedColumns, setSelectedColumns] = useState([
    'question',
    'answer',
    'category',
    'status',
  ])

  const toggleColumn = (column) => {
    setSelectedColumns((prev) =>
      prev.includes(column)
        ? prev.filter((c) => c !== column)
        : [...prev, column]
    )
  }

  const availableColumns = [
    { id: 'question', label: 'Question', checked: true },
    { id: 'answer', label: 'Answer', checked: true },
    { id: 'category', label: 'Category', checked: true },
    { id: 'status', label: 'Status', checked: true },
    { id: 'citations', label: 'Citations', checked: false },
    { id: 'confidence', label: 'Confidence Score', checked: false },
    { id: 'views', label: 'Views', checked: false },
    { id: 'rating', label: 'Rating', checked: false },
  ]

  const { data } = useSWR('/exports', fetchExports, { revalidateOnFocus: false })
  const recentExports = data?.items || []
  const stats = data?.stats || {}

  // Estimate export size and time based on format and record count
  const getEstimatedStats = () => {
    const recordCount = stats.approved_records || 0
    const formats = {
      excel: { size: (recordCount * 2.5) / 1024, time: Math.ceil(recordCount / 100) + 1 },
      csv: { size: (recordCount * 2.0) / 1024, time: Math.ceil(recordCount / 150) + 1 },
      json: { size: (recordCount * 3.0) / 1024, time: Math.ceil(recordCount / 80) + 1 },
      xml: { size: (recordCount * 4.0) / 1024, time: Math.ceil(recordCount / 60) + 1 },
    }
    return formats[exportFormat] || formats.csv
  }

  const estimatedStats = getEstimatedStats()

  const getFormatIcon = (format) => {
    switch (format) {
      case 'Excel':
        return '📊'
      case 'JSON':
        return '{ }'
      case 'CSV':
        return '📋'
      default:
        return '📄'
    }
  }

  const handleExport = () => {
    const payload = {
      format: exportFormat,
      columns: selectedColumns,
      filters: {},
    }
    createExport(payload)
      .then(() => alert('Export started — you will be notified when ready'))
      .catch((e) => alert('Export failed'))
  }

  return (
    <div className="space-y-8">
      {/* Export Configuration */}
      <Card>
        <h3 className="text-lg font-semibold text-text-primary mb-6">Create New Export</h3>

        {/* Format Selection */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-text-primary mb-3">
            Export Format
          </label>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            {[
              { id: 'excel', label: 'Excel', icon: '📊' },
              { id: 'json', label: 'JSON', icon: '{ }' },
              { id: 'csv', label: 'CSV', icon: '📋' },
              { id: 'xml', label: 'XML', icon: '< >' },
            ].map((format) => (
              <button
                key={format.id}
                onClick={() => setExportFormat(format.id)}
                className={`p-4 rounded-md border-2 transition-smooth text-center ${
                  exportFormat === format.id
                    ? 'bg-secondary border-primary'
                    : 'bg-bg-primary border-border hover:border-primary'
                }`}
              >
                <div className="text-2xl mb-2">{format.icon}</div>
                <p className={`text-sm font-medium ${exportFormat === format.id ? 'text-text-primary' : 'text-text-secondary'}`}>
                  {format.label}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Column Selection */}
        <div className="mb-8 pb-8 border-b border-border">
          <label className="block text-sm font-medium text-text-primary mb-3">
            Select Columns ({selectedColumns.length}/{availableColumns.length})
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {availableColumns.map((column) => (
              <label
                key={column.id}
                className="flex items-center gap-2 p-3 rounded-md bg-bg-primary hover:bg-secondary transition-smooth cursor-pointer border border-border"
              >
                <input
                  type="checkbox"
                  checked={selectedColumns.includes(column.id)}
                  onChange={() => toggleColumn(column.id)}
                  className="w-4 h-4 rounded cursor-pointer"
                />
                <span className="text-sm text-text-primary">{column.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Status Filter
            </label>
            <select className="w-full px-4 py-2 border border-border rounded-md bg-bg-card text-text-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50 transition-smooth">
              <option>All Status</option>
              <option>Approved</option>
              <option>Pending</option>
              <option>Rejected</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Date Range
            </label>
            <select className="w-full px-4 py-2 border border-border rounded-md bg-bg-card text-text-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50 transition-smooth">
              <option>Last 30 days</option>
              <option>Last 90 days</option>
              <option>Last 6 months</option>
              <option>All time</option>
            </select>
          </div>
        </div>

        {/* Export Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 pb-8 border-b border-border">
          <div className="p-4 bg-bg-primary rounded-md">
            <p className="text-xs text-text-secondary mb-1">Total Records</p>
            <p className="text-2xl font-semibold text-text-primary">{stats.approved_records ?? 0}</p>
            <p className="text-xs text-text-secondary mt-1">Approved & ready</p>
          </div>
          <div className="p-4 bg-bg-primary rounded-md">
            <p className="text-xs text-text-secondary mb-1">Estimated Size</p>
            <p className="text-2xl font-semibold text-text-primary">{estimatedStats.size.toFixed(1)} MB</p>
            <p className="text-xs text-text-secondary mt-1">For {exportFormat} export</p>
          </div>
          <div className="p-4 bg-bg-primary rounded-md">
            <p className="text-xs text-text-secondary mb-1">Export Time</p>
            <p className="text-2xl font-semibold text-text-primary">{estimatedStats.time}s</p>
            <p className="text-xs text-text-secondary mt-1">Estimated duration</p>
          </div>
        </div>

        {/* Export Button */}
        <Button
          variant="primary"
          onClick={handleExport}
          className="w-full md:w-auto flex items-center justify-center"
        >
          <Download size={18} className="mr-2" />
          Export Now
        </Button>
      </Card>

      {/* Recent Exports */}
      <Card>
        <h3 className="text-lg font-semibold text-text-primary mb-6">Recent Exports</h3>
        {recentExports.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                    File Name
                  </th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                    Format
                  </th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                    Records
                  </th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                    Size
                  </th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                    Created
                  </th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                    By
                  </th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                {recentExports.map((exp) => (
                  <tr
                    key={exp.id}
                    className="border-b border-border hover:bg-bg-primary transition-smooth"
                  >
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <File size={20} className="text-primary opacity-70" />
                        <span className="text-sm font-medium text-text-primary">{exp.name}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className="text-sm text-text-secondary">{exp.format}</span>
                    </td>
                    <td className="py-4 px-4">
                      <span className="text-sm font-medium text-text-primary">{exp.records}</span>
                    </td>
                    <td className="py-4 px-4">
                      <span className="text-sm text-text-secondary">{exp.size}</span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-1 text-sm text-text-secondary">
                        <Clock size={14} />
                        {exp.createdAt.split('T')[0]}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className="text-sm text-text-secondary">{exp.createdBy}</span>
                    </td>
                    <td className="py-4 px-4">
                      <Button variant="ghost" size="sm">
                        <Download size={18} />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <AlertCircle size={40} className="mx-auto mb-3 text-text-secondary opacity-50" />
            <p className="text-text-secondary">No exports yet. Create your first export above.</p>
          </div>
        )}
      </Card>

      {/* Export History & Scheduling */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-semibold text-text-primary mb-6">Export Statistics</h3>
          <div className="space-y-4">
            {[
              { label: 'Total Exports Created', value: stats.total_exports_created ?? 0 },
              { label: 'This Month', value: stats.this_month ?? 0 },
              { label: 'Most Used Format', value: stats.most_used_format ?? '-' },
              { label: 'Storage Used', value: stats.storage_used ?? '0 MB' },
            ].map((stat, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-bg-primary rounded-md">
                <span className="text-sm text-text-secondary">{stat.label}</span>
                <span className="text-sm font-semibold text-text-primary">{stat.value}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold text-text-primary mb-6">Data Available for Export</h3>
          <div className="space-y-3">
            {[
              { label: 'Total Records', value: stats.total_records_available ?? 0, hint: 'All records indexed' },
              { label: 'Approved & Ready', value: stats.approved_records ?? 0, hint: 'Can export immediately' },
              { label: 'Pending Review', value: stats.pending_records ?? 0, hint: 'Awaiting approval' },
            ].map((item, idx) => (
              <div
                key={idx}
                className="p-4 border border-border rounded-md hover:border-primary transition-smooth"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-text-primary">{item.label}</span>
                  <span className="text-lg font-semibold text-primary">{item.value}</span>
                </div>
                <p className="text-xs text-text-secondary mt-1">{item.hint}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
