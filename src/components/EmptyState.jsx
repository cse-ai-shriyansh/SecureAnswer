import Button from './Button'

export default function EmptyState({
  icon: Icon,
  title,
  description,
  action = null,
  actionLabel = 'Get Started',
}) {
  return (
    <div className="card-base py-16 px-6 text-center">
      {Icon && (
        <div className="flex justify-center mb-4">
          <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center">
            <Icon className="text-primary opacity-50" size={32} />
          </div>
        </div>
      )}

      <h3 className="text-lg font-semibold text-text-primary mb-2">{title}</h3>
      <p className="text-text-secondary mb-6 max-w-sm mx-auto">{description}</p>

      {action && (
        <Button variant="primary" onClick={action}>
          {actionLabel}
        </Button>
      )}
    </div>
  )
}
