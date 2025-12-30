import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Zap, Wrench, HardHat } from 'lucide-react';

interface Issue {
  id: number;
  issue: string;
  severity: string;
  category: string;
  location: string;
  current_text: string;
  suggested_fix: string;
  fix_difficulty: string;
  additional_info?: string;
}

interface EffortGroupViewProps {
  issues: Issue[];
  displayLevel: number;
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
  displayLevel,
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
                    displayLevel={displayLevel}
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
  displayLevel: number;
  isExpanded: boolean;
  onToggle: () => void;
  effortColor: EffortGroup['color'];
}

function IssueCard({ 
  issue, 
  displayLevel, 
  isExpanded, 
  onToggle,
}: IssueCardProps) {
  const severityColors: Record<string, string> = {
    critical: 'bg-red-100 text-red-700',
    high: 'bg-orange-100 text-orange-700',
    medium: 'bg-yellow-100 text-yellow-700',
    low: 'bg-green-100 text-green-700'
  };

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
        <span className={`text-xs px-2 py-1 rounded-full ${severityColors[issue.severity] || 'bg-gray-100 text-gray-700'}`}>
          {issue.severity}
        </span>
      </button>

      {(displayLevel >= 2 || isExpanded) && (
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

          {displayLevel >= 3 && (
            <div className={displayLevel >= 4 ? 'mb-3' : ''}>
              <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Suggested Fix</p>
              <div className="bg-green-50 border border-green-200 rounded p-2">
                <p className="text-green-800 text-sm">{issue.suggested_fix}</p>
              </div>
            </div>
          )}

          {displayLevel >= 4 && (
            <div className="mb-3">
              <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Found</p>
              <div className="bg-red-50 border border-red-200 rounded p-2">
                <p className="text-red-800 font-mono text-sm">"{issue.current_text}"</p>
              </div>
            </div>
          )}

          {displayLevel >= 4 && issue.additional_info && (
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
