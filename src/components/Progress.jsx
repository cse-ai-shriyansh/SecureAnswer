export default function Progress({ value, max = 100, label = null, size = 'md', showPercent = false }) {
  const percentage = (value / max) * 100

  const sizes = {
    sm: 'h-1.5',
    md: 'h-2',
    lg: 'h-3',
  }

  const getColor = (percent) => {
    if (percent >= 80) return 'bg-green-500'
    if (percent >= 60) return 'bg-blue-500'
    if (percent >= 40) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div>
      {(label || showPercent) && (
        <div className="flex items-center justify-between mb-2">
          {label && <span className="text-sm font-medium text-text-primary">{label}</span>}
          {showPercent && (
            <span className="text-sm font-medium text-text-primary">{percentage.toFixed(0)}%</span>
          )}
        </div>
      )}
      <div className={`w-full bg-border rounded-full overflow-hidden ${sizes[size]}`}>
        <div
          className={`${getColor(percentage)} rounded-full h-full transition-all duration-300 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
