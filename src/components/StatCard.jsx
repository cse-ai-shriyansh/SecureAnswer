export default function StatCard({
  icon: Icon,
  label,
  value,
  change,
  changeType = 'positive',
  footer = null,
  onClick = null,
}) {
  const changeColor =
    changeType === 'positive'
      ? 'text-green-600'
      : changeType === 'negative'
      ? 'text-red-600'
      : 'text-text-secondary'

  return (
    <div
      onClick={onClick}
      className={`card-base p-6 transition-smooth ${onClick ? 'cursor-pointer hover:shadow-md hover:-translate-y-0.5' : ''}`}
    >
      {/* Header with icon and change */}
      <div className="flex items-center justify-between mb-5">
        {Icon && (
          <div className="w-12 h-12 rounded-2xl bg-bg-secondary border border-border flex items-center justify-center shadow-xs">
            <Icon className="text-text-primary" size={22} />
          </div>
        )}
        {change && <span className={`text-xs font-semibold ${changeColor}`}>{change}</span>}
      </div>

      {/* Content */}
      <p className="text-xs text-text-secondary uppercase tracking-[0.22em] mb-1.5">{label}</p>
      <p className="text-3xl font-semibold text-text-primary mb-3">{value}</p>

      {/* Footer */}
      {footer && <p className="text-xs text-text-secondary">{footer}</p>}
    </div>
  )
}
