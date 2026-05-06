import Card from '../components/Card'
import Badge from '../components/Badge'
import Button from '../components/Button'
import { Search, Filter, Eye, Edit, Trash2, Clock } from 'lucide-react'
import { useState } from 'react'
import useSWR from 'swr'
import { fetchKnowledgeBase } from '../lib/api'

export default function KnowledgeBase() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')

  const { data } = useSWR(['/kb', searchTerm], () => fetchKnowledgeBase(searchTerm), { revalidateOnFocus: false })
  const documents = data?.items || []
  const filteredDocuments = documents.filter((doc) => {
    const matchesFilter = filterStatus === 'all' || doc.status === filterStatus
    return matchesFilter
  })

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'success'
      case 'pending':
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
      <Card>
        <div className="space-y-4">
          <div className="flex items-center gap-2 relative">
            <Search size={20} className="absolute left-3 text-text-secondary" />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-2 border border-border rounded-md bg-bg-primary text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50 transition-smooth"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter size={20} className="text-text-secondary" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-border rounded-md bg-bg-card text-text-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50 transition-smooth"
            >
              <option value="all">All Status</option>
              <option value="approved">Approved</option>
              <option value="pending">Pending</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Documents Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                  Document
                </th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                  Version
                </th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                  Sections
                </th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                  Status
                </th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                  Last Modified
                </th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                  Approved By
                </th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredDocuments.map((doc) => (
                <tr key={doc.id} className="border-b border-border hover:bg-bg-primary transition-smooth">
                  <td className="py-4 px-4">
                    <div>
                      <p className="text-sm font-medium text-text-primary">{doc.title}</p>
                      <p className="text-xs text-text-secondary mt-1">{doc.file}</p>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <span className="text-sm font-medium text-text-primary">{doc.version}</span>
                  </td>
                  <td className="py-4 px-4">
                    <span className="text-sm text-text-secondary">{doc.sections}</span>
                  </td>
                  <td className="py-4 px-4">
                    <Badge variant={getStatusColor(doc.status)}>
                      {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                    </Badge>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-2 text-sm text-text-secondary">
                      <Clock size={16} />
                      {doc.lastModified}
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <span className="text-sm text-text-secondary">{doc.approvedBy}</span>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-2">
                      <button className="p-2 hover:bg-bg-primary rounded-md transition-smooth text-text-secondary hover:text-text-primary">
                        <Eye size={18} />
                      </button>
                      <button className="p-2 hover:bg-bg-primary rounded-md transition-smooth text-text-secondary hover:text-text-primary">
                        <Edit size={18} />
                      </button>
                      <button className="p-2 hover:bg-bg-primary rounded-md transition-smooth text-text-secondary hover:text-text-primary">
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Version History Sample */}
      <Card>
        <h3 className="text-lg font-semibold text-text-primary mb-6">Recent Version Updates</h3>
        <p className="text-sm text-text-secondary">
          Version history will appear here once document metadata is stored in Supabase.
        </p>
      </Card>
    </div>
  )
}
