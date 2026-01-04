import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Zap, Wrench, HardHat } from 'lucide-react';

interface Issue {
  id: number;
  issue: string;
  severity: string;
  category: string;
  location: string;
  current: string;
  suggestion: string | null;
  fix_difficulty: string;
  additional_info?: string;
  example_before?: string;
  example_after?: string;
}

interface EffortGroupViewProps {
  issues: Issue[];
  displayLevel?: number;
  expandedIssues: Set<number>;
  onToggleIssue: (id: number) => void;
}

interface EffortGroup {
  id: string;
  title: string;
  icon: React.ReactNode;
  timeEstimate: string;
  difficulty: string;
  color: {
    bg: string;
    border: string;
    text: string;
    badge: string;
  };
}

const EFFORT_GROUPS: EffortGroup[] = [
  {
    id: 'quick',
    title: 'Quick Wins',
    icon: <Zap size={20} />,
    timeEstimate: '~5 min each',
    difficulty: 'quick',
    color: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-800',
      badge: 'bg-green-100 text-green-700'
    }
  },
  {
    id: 'medium',
    title: 'Worth the Effort',
    icon: <Wrench size={20} />,
    timeEstimate: '~15 min each',
    difficulty: 'medium',
    color: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      text: 'text-yellow-800',
      badge: 'bg-yellow-100 text-yellow-700'
    }
  },
  {
    id: 'complex',
    title: 'Deep Improvements',
    icon: <HardHat size={20} />,
    timeEstimate: '~30+ min each',
    difficulty: 'complex',
    color: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-800',
      badge: 'bg-blue-100 text-blue-700'
    }
  }
];

function getEffortLevel(issue: Issue): string {
  if (issue.fix_difficulty) {
    return issue.fix_difficulty;
  }
  if (issue.severity === 'critical') {
    return 'quick';
  }
  if (issue.severity === 'high') {
    return 'medium';
  }
  return 'complex';
}

export default function EffortGroupView({
  issues,
  expandedIssues,
  onToggleIssue
}: EffortGroupViewProps) {
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(new Set());

  const toggleGroup = (groupId: string) => {
    setCollapsedGroups(prev => {
      const next = new Set(prev);
      if (next.has(groupId)) {
        next.delete(groupId);
      } else {
        next.add(groupId);
      }
      return next;
    });
  };

  const groupedIssues = EFFORT_GROUPS.map(group => ({
    ...group,
    issues: issues.filter(issue => getEffortLevel(issue) === group.difficulty)
  }));

  return (
    <div className="space-y-4">
      {groupedIssues.map(group => {
        if (group.issues.length === 0) return null;
        
        const isCollapsed = collapsedGroups.has(group.id);

        return (
          <div 
            key={group.id}
            className={`border ${group.color.border} rounded-xl overflow-hidden`}
          >
            <button
              onClick={() => toggleGroup(group.id)}
              className={`
                w-full flex items-center justify-between p-4 
                ${group.color.bg} hover:opacity-90 transition-opacity
              `}
            >
              <div className="flex items-center gap-3">
                {isCollapsed ? (
                  <ChevronRight size={20} className={group.color.text} />
                ) : (
                  <ChevronDown size={20} className={group.color.text} />
                )}
                <span className={group.color.text}>{group.icon}</span>
                <span className={`font-semibold ${group.color.text}`}>
                  {group.title}
                </span>
                <span className={`text-sm px-2 py-1 rounded-full ${group.color.badge}`}>
                  {group.issues.length} suggestion{group.issues.length !== 1 ? 's' : ''}
                </span>
              </div>
              <span className={`text-sm ${group.color.text} opacity-75`}>
                {group.timeEstimate}
              </span>
            </button>

            {!isCollapsed && (
              <div className="p-4 space-y-3 bg-white">
                {group.issues.map(issue => (
                  <IssueCard
                    key={issue.id}
                    issue={issue}
                    isExpanded={expandedIssues.has(issue.id)}
                    onToggle={() => onToggleIssue(issue.id)}
                    effortColor={group.color}
                  />
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

interface IssueCardProps {
  issue: Issue;
  isExpanded: boolean;
  onToggle: () => void;
  effortColor: EffortGroup['color'];
}

const SEVERITY_DISPLAY: Record<string, string> = {
  'critical': 'Critical',
  'important': 'Important',
  'consider': 'Consider',
  'polish': 'Polish',
  'high': 'Important',
  'medium': 'Consider',
  'low': 'Polish'
};

const SEVERITY_COLORS: Record<string, string> = {
  'critical': 'bg-red-100 text-red-700',
  'important': 'bg-orange-100 text-orange-700',
  'consider': 'bg-yellow-100 text-yellow-700',
  'polish': 'bg-green-100 text-green-700',
  'high': 'bg-orange-100 text-orange-700',
  'medium': 'bg-yellow-100 text-yellow-700',
  'low': 'bg-green-100 text-green-700'
};

function IssueCard({ 
  issue, 
  isExpanded, 
  onToggle,
}: IssueCardProps) {

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-3 hover:bg-gray-50 text-left"
      >
        <div className="flex items-center gap-3">
          {isExpanded ? (
            <ChevronDown size={18} className="text-gray-400" />
          ) : (
            <ChevronRight size={18} className="text-gray-400" />
          )}
          <span className="font-medium text-gray-900">{issue.issue}</span>
        </div>
        <span className={`text-xs px-2 py-1 rounded-full ${SEVERITY_COLORS[issue.severity] || 'bg-gray-100 text-gray-700'}`}>
          {SEVERITY_DISPLAY[issue.severity] || issue.severity}
        </span>
      </button>

      {isExpanded && (
        <div className="p-3 bg-gray-50 border-t border-gray-100">
          <div className="grid grid-cols-2 gap-4 mb-3">
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Category</p>
              <p className="text-sm text-gray-700">{issue.category}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Location</p>
              <p className="text-sm text-gray-700">{issue.location}</p>
            </div>
          </div>

          {issue.current && issue.current.length > 0 && !issue.current.startsWith('Not found') && (
            <div className="mb-3">
              <p className="text-xs text-gray-500 uppercase tracking-wide mb-1 flex items-center gap-1">
                <span className="text-amber-500">⚠</span> Issue in Your CV
              </p>
              <div className="bg-amber-50 border border-amber-200 rounded p-2">
                <p className="text-amber-800 font-mono text-sm">"{issue.current}"</p>
              </div>
            </div>
          )}

          {issue.current && issue.current.startsWith('Not found') && (
            <div className="mb-3">
              <p className="text-xs text-gray-500 uppercase tracking-wide mb-1 flex items-center gap-1">
                <span className="text-gray-400">🔍</span> Searched In
              </p>
              <div className="bg-gray-50 border border-gray-200 rounded p-2">
                <p className="text-gray-600 text-sm italic">{issue.current}</p>
              </div>
            </div>
          )}

          {issue.example_before && (
            <div className="mb-3">
              <p className="text-xs text-gray-500 uppercase tracking-wide mb-1 flex items-center gap-1">
                <span className="text-red-500">✗</span> Example (needs improvement)
              </p>
              <div className="bg-red-50 border border-red-200 rounded p-2">
                <p className="text-red-800 text-sm italic">"{issue.example_before}"</p>
              </div>
            </div>
          )}

          {issue.example_after && (
            <div className="mb-3">
              <p className="text-xs text-gray-500 uppercase tracking-wide mb-1 flex items-center gap-1">
                <span className="text-green-500">✓</span> Example (improved)
              </p>
              <div className="bg-green-50 border border-green-200 rounded p-2">
                <p className="text-green-800 text-sm">"{issue.example_after}"</p>
              </div>
            </div>
          )}

          {issue.suggestion && (
            <div className="mb-3">
              <p className="text-xs text-gray-500 uppercase tracking-wide mb-1 flex items-center gap-1">
                <span>💡</span> How to Fix
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded p-2">
                <p className="text-blue-800 text-sm">{issue.suggestion}</p>
              </div>
            </div>
          )}

          {issue.additional_info && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Additional Information</p>
              <p className="text-gray-600 text-sm">{issue.additional_info}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
