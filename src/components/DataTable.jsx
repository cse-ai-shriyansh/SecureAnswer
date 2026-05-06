import { ChevronUp, ChevronDown } from 'lucide-react'
import { useState } from 'react'

export default function DataTable({
  columns,
  data,
  sortable = true,
  hover = true,
  striped = true,
}) {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })

  const handleSort = (key) => {
    if (!sortable) return

    let direction = 'asc'
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc'
    }
    setSortConfig({ key, direction })
  }

  const sortedData = [...data].sort((a, b) => {
    if (!sortConfig.key) return 0

    const aValue = a[sortConfig.key]
    const bValue = b[sortConfig.key]

    if (typeof aValue === 'string') {
      return sortConfig.direction === 'asc'
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue)
    }

    return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue
  })

  return (
    <div className="card-base overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="border-b border-border bg-bg-secondary">
            {columns.map((col) => (
              <th
                key={col.key}
                onClick={() => handleSort(col.key)}
                className={`px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider ${
                  sortable ? 'cursor-pointer hover:bg-bg-primary' : ''
                } transition-smooth`}
              >
                <div className="flex items-center gap-2">
                  {col.label}
                  {sortConfig.key === col.key && (
                    <span>
                      {sortConfig.direction === 'asc' ? (
                        <ChevronUp size={14} />
                      ) : (
                        <ChevronDown size={14} />
                      )}
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map((row, rowIdx) => (
            <tr
              key={rowIdx}
              className={`border-b border-border transition-smooth ${
                hover ? 'hover:bg-bg-secondary' : ''
              } ${striped && rowIdx % 2 === 0 ? 'bg-bg-primary' : ''}`}
            >
              {columns.map((col) => (
                <td key={col.key} className="px-4 py-3 text-sm text-text-primary">
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
