export function SkeletonCard({ count = 3 }) {
  return (
    <>
      {[...Array(count)].map((_, idx) => (
        <div key={idx} className="card-base p-6 mb-4">
          <div className="skeleton h-8 w-1/3 mb-4 rounded-md" />
          <div className="space-y-2">
            <div className="skeleton h-4 w-full rounded" />
            <div className="skeleton h-4 w-5/6 rounded" />
            <div className="skeleton h-4 w-4/6 rounded" />
          </div>
        </div>
      ))}
    </>
  )
}

export function SkeletonTable({ rows = 5, cols = 6 }) {
  return (
    <div className="card-base overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="border-b border-border bg-bg-secondary">
            {[...Array(cols)].map((_, idx) => (
              <th key={idx} className="px-4 py-3">
                <div className="skeleton h-4 w-full rounded" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {[...Array(rows)].map((_, rowIdx) => (
            <tr key={rowIdx} className="border-b border-border">
              {[...Array(cols)].map((_, colIdx) => (
                <td key={colIdx} className="px-4 py-3">
                  <div className="skeleton h-4 w-full rounded" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function SkeletonText({ lines = 3 }) {
  return (
    <div className="space-y-3">
      {[...Array(lines)].map((_, idx) => (
        <div key={idx} className="skeleton h-4 rounded" style={{ width: `${Math.random() * 30 + 70}%` }} />
      ))}
    </div>
  )
}
