export default function Badge({ children, variant = 'default', className = '' }) {
  const variants = {
    default: 'bg-bg-secondary text-text-primary border border-border',
    success: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
    warning: 'bg-amber-50 text-amber-700 border border-amber-100',
    danger: 'bg-red-50 text-red-700 border border-red-100',
    info: 'bg-blue-50 text-blue-700 border border-blue-100',
  }

  return (
    <span
      className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${variants[variant]} ${className}`}
    >
      {children}
    </span>
  )
}
