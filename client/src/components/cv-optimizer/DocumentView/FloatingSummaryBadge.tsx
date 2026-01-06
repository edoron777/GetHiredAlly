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

const SEVERITY_COLORS: Record<string, { primary: string; background: string }> = {
  critical: { 
    primary: '#990033',
    background: 'rgba(153, 0, 51, 0.1)',
  },
  important: { 
    primary: '#990099',
    background: 'rgba(153, 0, 153, 0.1)',
  },
  consider: { 
    primary: '#1E5A85',
    background: 'rgba(30, 90, 133, 0.1)',
  },
  polish: { 
    primary: '#008080',
    background: 'rgba(0, 128, 128, 0.1)',
  },
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
              <span 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: SEVERITY_COLORS.critical.primary }}
              ></span>
              <span className="text-sm text-gray-600">{counts.critical} critical</span>
            </div>
          )}
          {counts.important > 0 && (
            <div className="flex items-center gap-2">
              <span 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: SEVERITY_COLORS.important.primary }}
              ></span>
              <span className="text-sm text-gray-600">{counts.important} important</span>
            </div>
          )}
          {counts.consider > 0 && (
            <div className="flex items-center gap-2">
              <span 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: SEVERITY_COLORS.consider.primary }}
              ></span>
              <span className="text-sm text-gray-600">{counts.consider} consider</span>
            </div>
          )}
          {counts.polish > 0 && (
            <div className="flex items-center gap-2">
              <span 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: SEVERITY_COLORS.polish.primary }}
              ></span>
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
                  <div 
                    className="text-xs font-semibold uppercase mb-1"
                    style={{ color: SEVERITY_COLORS[severity]?.primary || '#6B7280' }}
                  >
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
                      <span 
                        className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0"
                        style={{ backgroundColor: SEVERITY_COLORS[severity]?.primary || '#6B7280' }}
                      ></span>
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
