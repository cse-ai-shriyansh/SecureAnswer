import { X, AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function Toast({ type = 'info', title, message, duration = 4000, onClose = null }) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      onClose?.()
    }, duration)
    return () => clearTimeout(timer)
  }, [duration, onClose])

  if (!isVisible) return null

  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
  }

  const colors = {
    success: 'bg-green-50 border-green-200',
    error: 'bg-red-50 border-red-200',
    warning: 'bg-yellow-50 border-yellow-200',
    info: 'bg-blue-50 border-blue-200',
  }

  const textColors = {
    success: 'text-green-800',
    error: 'text-red-800',
    warning: 'text-yellow-800',
    info: 'text-blue-800',
  }

  const iconColors = {
    success: 'text-green-500',
    error: 'text-red-500',
    warning: 'text-yellow-500',
    info: 'text-blue-500',
  }

  const Icon = icons[type]

  return (
    <div className={`fixed bottom-4 right-4 max-w-md border rounded-lg shadow-lg p-4 ${colors[type]} animate-slide-up z-50`}>
      <div className="flex items-start gap-3">
        <Icon className={`${iconColors[type]} flex-shrink-0 mt-0.5`} size={20} />
        <div className="flex-1">
          {title && <h4 className={`font-semibold ${textColors[type]}`}>{title}</h4>}
          {message && <p className={`text-sm ${textColors[type]} mt-1`}>{message}</p>}
        </div>
        <button
          onClick={() => {
            setIsVisible(false)
            onClose?.()
          }}
          className={`flex-shrink-0 ${textColors[type]} hover:opacity-70 transition-smooth`}
        >
          <X size={18} />
        </button>
      </div>
    </div>
  )
}
