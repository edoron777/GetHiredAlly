import { useState, useEffect } from 'react'
import { X, Maximize2, Minimize2 } from 'lucide-react'

interface VideoModalProps {
  isOpen: boolean
  onClose: () => void
  videoUrl: string
  title?: string
}

export function VideoModal({ isOpen, onClose, videoUrl, title }: VideoModalProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (isExpanded) {
          setIsExpanded(false)
        } else {
          onClose()
        }
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEsc)
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEsc)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, isExpanded, onClose])

  useEffect(() => {
    if (!isOpen) {
      setIsExpanded(false)
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      onClick={onClose}
    >
      <div 
        className={`absolute inset-0 transition-all duration-300 ${
          isExpanded 
            ? 'bg-black bg-opacity-95' 
            : 'bg-black bg-opacity-80'
        }`}
      />

      <div
        className="relative z-10 mx-4 transition-all duration-300 ease-out"
        style={isExpanded ? {
          width: '90vw',
          maxWidth: 'none'
        } : {
          width: '100%',
          maxWidth: '896px'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className={`flex items-center justify-between px-4 py-3 rounded-t-lg transition-colors ${
          isExpanded 
            ? 'bg-black text-white' 
            : 'bg-gray-900 text-white'
        }`}>
          <h3 className="font-medium text-lg">{title || 'How it works'}</h3>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 hover:bg-gray-700 rounded transition-colors"
              aria-label={isExpanded ? 'Minimize video' : 'Expand video'}
              title={isExpanded ? 'Minimize (ESC)' : 'Expand for better viewing'}
            >
              {isExpanded ? (
                <Minimize2 size={20} />
              ) : (
                <Maximize2 size={20} />
              )}
            </button>

            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-700 rounded transition-colors"
              aria-label="Close video"
              title="Close"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        <div
          className="relative bg-black overflow-hidden rounded-b-lg"
          style={isExpanded ? {
            width: '100%',
            height: '80vh',
          } : {
            width: '100%',
            paddingBottom: '56.25%',
            height: 0,
          }}
        >
          <iframe
            className="absolute top-0 left-0 w-full h-full"
            src={isOpen ? `${videoUrl}?rel=0&modestbranding=1` : ''}
            title={title || 'Tutorial video'}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
            allowFullScreen
          />
        </div>

        {isExpanded && (
          <div className="text-center py-3 bg-black text-gray-400 text-sm rounded-b-lg">
            Press ESC to minimize • Click outside to close
          </div>
        )}
      </div>
    </div>
  )
}
