import React from 'react';

interface IssuesSummaryBoxProps {
  totalIssues: number;
  breakdown: {
    critical: number;
    important: number;
    consider: number;
    polish: number;
    // Legacy support
    high?: number;
    medium?: number;
    low?: number;
  };
  estimatedMinutes?: number;
}

const IssuesSummaryBox: React.FC<IssuesSummaryBoxProps> = ({
  totalIssues,
  breakdown
}) => {
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
      
      {/* Priority Breakdown - supports both new (important/consider/polish) and legacy (high/medium/low) */}
      <div className="flex flex-wrap justify-center gap-2">
        {breakdown.critical > 0 && (
          <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
            🔴 {breakdown.critical} Critical
          </span>
        )}
        {(breakdown.important > 0 || (breakdown.high && breakdown.high > 0)) && (
          <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm font-medium">
            🟠 {breakdown.important || breakdown.high} Important
          </span>
        )}
        {(breakdown.consider > 0 || (breakdown.medium && breakdown.medium > 0)) && (
          <span className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium">
            🟡 {breakdown.consider || breakdown.medium} Consider
          </span>
        )}
        {(breakdown.polish > 0 || (breakdown.low && breakdown.low > 0)) && (
          <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
            🟢 {breakdown.polish || breakdown.low} Polish
          </span>
        )}
      </div>
    </div>
  );
};

export default IssuesSummaryBox;
