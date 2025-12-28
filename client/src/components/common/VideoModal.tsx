import { useState, useEffect } from 'react';
import { X, Maximize2, Minimize2 } from 'lucide-react';

interface VideoModalProps {
  isOpen: boolean;
  onClose: () => void;
  videoUrl: string;
  title?: string;
}

export function VideoModal({ 
  isOpen, 
  onClose, 
  videoUrl, 
  title = 'How it works' 
}: VideoModalProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (isExpanded) {
          setIsExpanded(false);
        } else {
          onClose();
        }
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, isExpanded, onClose]);

  useEffect(() => {
    if (!isOpen) {
      setIsExpanded(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-black bg-opacity-90" />

      <div
        className={`relative z-10 w-full transition-all duration-300 ${
          isExpanded ? 'max-w-[90vw]' : 'max-w-4xl'
        }`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-4 py-3 bg-gray-900 rounded-t-lg">
          <h3 className="text-white font-medium text-lg">{title}</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 text-white hover:bg-gray-700 rounded transition-colors"
              title={isExpanded ? 'Minimize (ESC)' : 'Expand for better viewing'}
            >
              {isExpanded ? <Minimize2 size={20} /> : <Maximize2 size={20} />}
            </button>
            <button
              onClick={onClose}
              className="p-2 text-white hover:bg-gray-700 rounded transition-colors"
              title="Close"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="relative bg-black rounded-b-lg overflow-hidden"
             style={{ paddingBottom: '56.25%' }}>
          <iframe
            className="absolute inset-0 w-full h-full"
            src={`${videoUrl}?rel=0&modestbranding=1&autoplay=1`}
            title={title}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
            allowFullScreen
          />
        </div>

        <div className="text-center py-2 text-gray-400 text-sm">
          Press ESC to {isExpanded ? 'minimize' : 'close'} • Click outside to close
        </div>
      </div>
    </div>
  );
}
