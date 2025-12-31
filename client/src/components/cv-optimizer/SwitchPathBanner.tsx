import React from 'react';

interface SwitchPathBannerProps {
  remainingIssues: number;
  onSwitchToAutoFix: () => void;
  position?: 'top' | 'bottom';
}

const SwitchPathBanner: React.FC<SwitchPathBannerProps> = ({
  remainingIssues,
  onSwitchToAutoFix,
  position = 'top'
}) => {
  const isTop = position === 'top';
  
  return (
    <div className={`bg-blue-50 border border-blue-200 rounded-lg p-4 flex flex-col sm:flex-row items-center justify-between gap-4 ${isTop ? 'mb-6' : 'mt-6'}`}>
      <div className="flex items-center gap-3">
        <span className="text-2xl">💊</span>
        <div>
          <p className="font-medium text-blue-800">
            {isTop ? 'Want the easy way?' : 'Done reviewing?'}
          </p>
          <p className="text-sm text-blue-600">
            Let AI fix all {remainingIssues} issues instantly
          </p>
        </div>
      </div>
      
      <button
        onClick={onSwitchToAutoFix}
        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors whitespace-nowrap"
      >
        🚀 Fix All {remainingIssues} Issues
      </button>
    </div>
  );
};

export default SwitchPathBanner;
