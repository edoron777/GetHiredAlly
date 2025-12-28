import { useState } from 'react';
import { Play } from 'lucide-react';
import { Link } from 'react-router-dom';
import { VideoModal } from './VideoModal';
import { ServiceConfig } from '../../config/homePageServices';

interface ServiceCardProps {
  service: ServiceConfig;
}

export function ServiceCard({ service }: ServiceCardProps) {
  const [showVideo, setShowVideo] = useState(false);

  const {
    icon,
    title,
    description,
    buttonText,
    route,
    videoUrl,
    videoTitle,
    isComingSoon
  } = service;

  return (
    <>
      <div
        className={`
          rounded-xl p-6 transition-all duration-300
          ${isComingSoon
            ? 'bg-gray-50 border-2 border-dashed border-gray-300 opacity-70'
            : 'bg-white border border-gray-200 shadow-md hover:shadow-lg'
          }
        `}
      >
        {isComingSoon && (
          <div className="mb-3">
            <span className="inline-block px-3 py-1 text-xs font-medium text-orange-700 bg-orange-100 rounded-full">
              Coming Soon
            </span>
          </div>
        )}

        <div className="flex items-center gap-3 mb-4">
          <span className="text-3xl">{icon}</span>
          <h3 className={`text-xl font-bold ${isComingSoon ? 'text-gray-500' : 'text-gray-900'}`}>
            {title}
          </h3>
        </div>

        <p className={`mb-6 leading-relaxed ${isComingSoon ? 'text-gray-400' : 'text-gray-600'}`}>
          {description}
        </p>

        {isComingSoon ? (
          <button
            disabled
            className="w-full py-3 px-4 rounded-lg bg-gray-200 text-gray-500 font-medium cursor-not-allowed"
          >
            {buttonText}
          </button>
        ) : (
          <Link
            to={route || '#'}
            className="block w-full py-3 px-4 rounded-lg text-white font-medium text-center transition-colors"
            style={{ backgroundColor: '#1E3A5F' }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#162d4a'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#1E3A5F'}
          >
            {buttonText}
          </Link>
        )}

        {!isComingSoon && videoUrl && (
          <button
            onClick={() => setShowVideo(true)}
            className="w-full mt-4 flex items-center justify-center gap-2 text-sm text-gray-500 hover:text-blue-600 transition-colors"
          >
            <Play size={16} className="fill-current" />
            Watch how it works
          </button>
        )}
      </div>

      {videoUrl && (
        <VideoModal
          isOpen={showVideo}
          onClose={() => setShowVideo(false)}
          videoUrl={videoUrl}
          title={videoTitle || `How ${title} Works`}
        />
      )}
    </>
  );
}
