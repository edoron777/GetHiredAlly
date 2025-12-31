import React from 'react';

interface IssuesSummaryBoxProps {
  totalIssues: number;
  breakdown: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  estimatedMinutes: number;
}

const IssuesSummaryBox: React.FC<IssuesSummaryBoxProps> = ({
  totalIssues,
  breakdown,
  estimatedMinutes
}) => {
  const hours = Math.floor(estimatedMinutes / 60);
  const minutes = estimatedMinutes % 60;
  const timeString = hours > 0 
    ? `${hours}h ${minutes}m` 
    : `${minutes} minutes`;

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 mb-8">
      {/* Header */}
      <div className="text-center mb-4">
        <span className="text-3xl">⚠️</span>
        <h3 className="text-2xl font-bold text-gray-800 mt-2">
          {totalIssues} Issues Detected
        </h3>
        <p className="text-gray-600 mt-1">
          These issues could hurt your chances with recruiters
        </p>
      </div>
      
      {/* Priority Breakdown */}
      <div className="flex flex-wrap justify-center gap-2 mb-4">
        {breakdown.critical > 0 && (
          <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
            🔴 {breakdown.critical} Quick Wins
          </span>
        )}
        {breakdown.high > 0 && (
          <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm font-medium">
            🟠 {breakdown.high} Important
          </span>
        )}
        {breakdown.medium > 0 && (
          <span className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium">
            🟡 {breakdown.medium} Consider
          </span>
        )}
        {breakdown.low > 0 && (
          <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
            🟢 {breakdown.low} Polish
          </span>
        )}
      </div>
      
      {/* Time Estimate */}
      <div className="text-center p-3 bg-white rounded-lg border border-amber-200">
        <span className="text-gray-500">⏱️ Estimated manual fix time:</span>
        <span className="text-xl font-bold text-gray-800 ml-2">{timeString}</span>
      </div>
    </div>
  );
};

export default IssuesSummaryBox;
