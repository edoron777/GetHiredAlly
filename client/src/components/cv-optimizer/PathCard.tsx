import React from 'react';

interface PathCardProps {
  variant: 'blue' | 'red';
  title: string;
  description: string;
  features: string[];
  buttonText: string;
  onClick: () => void;
  badge?: string;
  issueCount?: number;
}

const PathCard: React.FC<PathCardProps> = ({
  variant,
  title,
  description,
  features,
  buttonText,
  onClick,
  badge,
  issueCount
}) => {
  const isBlue = variant === 'blue';
  
  const cardStyles = isBlue
    ? 'border-2 border-blue-400 bg-blue-50 shadow-lg'
    : 'border border-gray-300 bg-gray-50';
    
  const buttonStyles = isBlue
    ? 'bg-blue-600 hover:bg-blue-700 text-white'
    : 'bg-gray-100 hover:bg-gray-200 text-gray-700 border border-gray-300';
    
  const iconBg = isBlue ? 'bg-blue-100' : 'bg-gray-100';
  const icon = isBlue ? '⚡' : '📋';

  return (
    <div className={`rounded-xl p-6 ${cardStyles} flex flex-col h-full`}>
      {/* Icon */}
      <div className={`w-16 h-16 ${iconBg} rounded-full flex items-center justify-center mx-auto mb-4`}>
        <span className="text-3xl">{icon}</span>
      </div>
      
      {/* Title */}
      <h3 className="text-xl font-bold text-gray-800 text-center mb-2">
        {title}
      </h3>
      
      {/* Description */}
      <p className="text-gray-600 text-center mb-4">
        {description}
        {issueCount && (
          <span className="font-semibold"> {issueCount} issues</span>
        )}
      </p>
      
      {/* Divider */}
      <div className="border-t border-gray-200 my-4"></div>
      
      {/* Features */}
      <ul className="space-y-2 mb-6 flex-grow">
        {features.map((feature, index) => (
          <li key={index} className="flex items-center text-gray-600">
            <span className="mr-2">{isBlue ? '✓' : '•'}</span>
            {feature}
          </li>
        ))}
      </ul>
      
      {/* Button */}
      <button
        onClick={onClick}
        className={`w-full py-3 px-6 rounded-lg font-semibold transition-colors ${buttonStyles}`}
      >
        {buttonText}
      </button>
      
      {/* Badge */}
      {badge && (
        <p className="text-center text-sm text-gray-500 mt-3">
          {badge}
        </p>
      )}
    </div>
  );
};

export default PathCard;
