import React, { useState } from 'react';
import { ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';

interface Issue {
  issue_code: string;
  display_name: string;
  severity: string;
  explanation?: string;
}

interface FloatingSummaryBadgeProps {
  issues: Issue[];
  onIssueClick?: (issueCode: string) => void;
}

const NO_MARKER_ISSUES = [
  'LENGTH_CV_TOO_LONG',
  'LENGTH_CV_TOO_SHORT',
  'LENGTH_SUMMARY_TOO_LONG',
  'LENGTH_EXPERIENCE_TOO_DETAILED',
  'CONTENT_JOB_DESCRIPTION_TOO_LONG',
  'CONTENT_JOB_DESCRIPTION_TOO_SHORT',
  'CONTENT_EDUCATION_DESCRIPTION_TOO_SHORT',
  'CONTACT_MISSING_LINKEDIN',
  'CONTACT_MISSING_GITHUB',
  'CONTACT_MISSING_EMAIL',
  'CONTACT_MISSING_PHONE',
  'CONTACT_MISSING_LOCATION',
  'FORMAT_SECTION_ORDER_VIOLATION',
  'FORMAT_SKILLS_SECTION_MISSING',
  'FORMAT_MISSING_SECTION_HEADERS',
  'CONTENT_MISSING_SUMMARY',
];

const SEVERITY_COLORS: Record<string, { bg: string; text: string; dot: string }> = {
  critical: { bg: 'bg-red-100', text: 'text-red-700', dot: 'bg-red-500' },
  important: { bg: 'bg-orange-100', text: 'text-orange-700', dot: 'bg-orange-500' },
  consider: { bg: 'bg-blue-100', text: 'text-blue-700', dot: 'bg-blue-500' },
  polish: { bg: 'bg-gray-100', text: 'text-gray-600', dot: 'bg-gray-400' },
};

export const FloatingSummaryBadge: React.FC<FloatingSummaryBadgeProps> = ({ issues, onIssueClick }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const documentLevelIssues = issues.filter(issue => 
    NO_MARKER_ISSUES.includes(issue.issue_code)
  );

  if (documentLevelIssues.length === 0) {
    return null;
  }

  const bySeverity = documentLevelIssues.reduce((acc, issue) => {
    const severity = issue.severity || 'consider';
    if (!acc[severity]) acc[severity] = [];
    acc[severity].push(issue);
    return acc;
  }, {} as Record<string, Issue[]>);

  const counts = {
    critical: bySeverity.critical?.length || 0,
    important: bySeverity.important?.length || 0,
    consider: bySeverity.consider?.length || 0,
    polish: bySeverity.polish?.length || 0,
  };

  const severityOrder = ['critical', 'important', 'consider', 'polish'];

  return (
    <div className="fixed right-4 top-1/3 z-50">
      <div 
        className="bg-white rounded-lg shadow-lg border border-gray-200 cursor-pointer hover:shadow-xl transition-shadow min-w-[140px]"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="px-3 py-2 flex items-center gap-2 border-b border-gray-100">
          <AlertCircle className="w-4 h-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">General Issues</span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-gray-400 ml-auto" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-400 ml-auto" />
          )}
        </div>

        <div className="px-3 py-2 space-y-1">
          {counts.critical > 0 && (
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500"></span>
              <span className="text-sm text-gray-600">{counts.critical} critical</span>
            </div>
          )}
          {counts.important > 0 && (
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-orange-500"></span>
              <span className="text-sm text-gray-600">{counts.important} important</span>
            </div>
          )}
          {counts.consider > 0 && (
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-blue-500"></span>
              <span className="text-sm text-gray-600">{counts.consider} consider</span>
            </div>
          )}
          {counts.polish > 0 && (
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-gray-400"></span>
              <span className="text-sm text-gray-600">{counts.polish} polish</span>
            </div>
          )}
        </div>

        {isExpanded && (
          <div className="border-t border-gray-100 max-h-64 overflow-y-auto">
            {severityOrder.map(severity => {
              const issueList = bySeverity[severity];
              if (!issueList || issueList.length === 0) return null;
              
              return (
                <div key={severity} className="px-3 py-2">
                  <div className={`text-xs font-semibold uppercase ${SEVERITY_COLORS[severity]?.text || 'text-gray-600'} mb-1`}>
                    {severity} ({issueList.length})
                  </div>
                  {issueList.map((issue, idx) => (
                    <div 
                      key={idx} 
                      className="flex items-start gap-2 py-1 hover:bg-gray-50 rounded cursor-pointer"
                      onClick={(e) => {
                        e.stopPropagation();
                        onIssueClick?.(issue.issue_code);
                      }}
                    >
                      <span className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${SEVERITY_COLORS[severity]?.dot || 'bg-gray-400'}`}></span>
                      <span className="text-sm text-gray-700">{issue.display_name}</span>
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default FloatingSummaryBadge;
