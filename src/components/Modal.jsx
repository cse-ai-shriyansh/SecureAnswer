import { X } from 'lucide-react'

export default function Modal({ isOpen, onClose, title, children, actions = null, size = 'md' }) {
  if (!isOpen) return null

  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-2xl',
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-40 transition-smooth"
        onClick={onClose}
      />

      {/* Modal */}
      <div
        className={`relative bg-bg-card rounded-lg shadow-xl ${sizes[size]} w-full mx-4 animate-scale-up`}
      >
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between px-6 py-4 border-b border-border">
            <h2 className="text-lg font-semibold text-text-primary">{title}</h2>
            <button
              onClick={onClose}
              className="p-1 text-text-secondary hover:text-text-primary transition-smooth hover:bg-bg-secondary rounded-md"
            >
              <X size={20} />
            </button>
          </div>
        )}

        {/* Content */}
        <div className="px-6 py-4 max-h-96 overflow-y-auto">{children}</div>

        {/* Actions */}
        {actions && (
          <div className="flex items-center justify-end gap-2 px-6 py-4 border-t border-border bg-bg-secondary rounded-b-lg">
            {actions}
          </div>
        )}
      </div>
    </div>
  )
}
