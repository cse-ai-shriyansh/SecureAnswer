export default function Avatar({ initials, name, size = 'md', status = null, image = null }) {
  const sizes = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg',
  }

  const colors = [
    'bg-blue-100 text-blue-700',
    'bg-purple-100 text-purple-700',
    'bg-pink-100 text-pink-700',
    'bg-green-100 text-green-700',
    'bg-yellow-100 text-yellow-700',
    'bg-indigo-100 text-indigo-700',
  ]

  const getColorByInitials = (initials) => {
    const charCode = initials.charCodeAt(0)
    return colors[charCode % colors.length]
  }

  return (
    <div className="relative inline-flex">
      {image ? (
        <img
          src={image}
          alt={name}
          className={`${sizes[size]} rounded-full object-cover border-2 border-bg-primary`}
        />
      ) : (
        <div
          className={`${sizes[size]} rounded-full flex items-center justify-center font-semibold ${getColorByInitials(initials)}`}
          title={name}
        >
          {initials}
        </div>
      )}

      {/* Status indicator */}
      {status && (
        <div
          className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-bg-card ${
            status === 'online'
              ? 'bg-green-500'
              : status === 'busy'
              ? 'bg-red-500'
              : status === 'away'
              ? 'bg-yellow-500'
              : 'bg-gray-400'
          }`}
        />
      )}
    </div>
  )
}
