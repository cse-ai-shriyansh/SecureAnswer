import { useState } from 'react'

export default function Tooltip({ children, content, position = 'top' }) {
  const [isVisible, setIsVisible] = useState(false)

  const positions = {
    top: 'bottom-full mb-2 left-1/2 transform -translate-x-1/2',
    bottom: 'top-full mt-2 left-1/2 transform -translate-x-1/2',
    left: 'right-full mr-2 top-1/2 transform -translate-y-1/2',
    right: 'left-full ml-2 top-1/2 transform -translate-y-1/2',
  }

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onFocus={() => setIsVisible(true)}
        onBlur={() => setIsVisible(false)}
      >
        {children}
      </div>

      {isVisible && (
        <div
          className={`absolute ${positions[position]} whitespace-nowrap px-3 py-2 bg-text-primary text-white text-xs rounded-md shadow-lg animate-fade-in z-40`}
        >
          {content}
          {/* Arrow */}
          <div
            className={`absolute w-0 h-0 border-4 ${
              position === 'top'
                ? 'top-full left-1/2 transform -translate-x-1/2 border-t-text-primary border-r-transparent border-b-transparent border-l-transparent'
                : position === 'bottom'
                ? 'bottom-full left-1/2 transform -translate-x-1/2 border-b-text-primary border-r-transparent border-t-transparent border-l-transparent'
                : position === 'left'
                ? 'left-full top-1/2 transform -translate-y-1/2 border-l-text-primary border-t-transparent border-b-transparent border-r-transparent'
                : 'right-full top-1/2 transform -translate-y-1/2 border-r-text-primary border-t-transparent border-b-transparent border-l-transparent'
            }`}
          />
        </div>
      )}
    </div>
  )
}
