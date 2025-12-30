import React, { useState, useMemo } from 'react';
import { ChevronDown, ChevronRight, Wrench, BarChart2, PenTool, Plus, Layout } from 'lucide-react';
import { WORK_TYPE_CATEGORIES, getWorkTypeForIssue } from '../../config/workTypeCategories';

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

interface WorkTypeGroupViewProps {
  issues: Issue[];
  displayLevel: number;
  expandedIssues: Set<number>;
  onToggleIssue: (id: number) => void;
}

const iconMap: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  Wrench,
  BarChart2,
  PenTool,
  Plus,
  Layout
};

export default function WorkTypeGroupView({
  issues,
  displayLevel,
  expandedIssues,
  onToggleIssue
}: WorkTypeGroupViewProps) {
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

  const groupedIssues = useMemo(() => {
    return WORK_TYPE_CATEGORIES.map(workType => ({
      ...workType,
      issues: issues.filter(issue => getWorkTypeForIssue(issue.category) === workType.id)
    }));
  }, [issues]);

  const totalMinutes = useMemo(() => {
    return groupedIssues.reduce((acc, group) => {
      return acc + (group.issues.length * group.avgTimePerItem);
    }, 0);
  }, [groupedIssues]);

  const formatTotalTime = (minutes: number) => {
    if (minutes < 60) return `${minutes} minutes`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours} hour${hours > 1 ? 's' : ''}`;
  };

  const severityColors: Record<string, string> = {
    critical: 'bg-red-100 text-red-700',
    high: 'bg-orange-100 text-orange-700',
    medium: 'bg-yellow-100 text-yellow-700',
    low: 'bg-green-100 text-green-700'
  };

  return (
    <div className="space-y-4">
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Estimated total time to implement all suggestions:</p>
            <p className="text-2xl font-bold text-gray-900">{formatTotalTime(totalMinutes)}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Group by type of work</p>
            <p className="text-lg font-semibold text-blue-600">for focused sessions!</p>
          </div>
        </div>
      </div>

      {groupedIssues.map(group => {
        if (group.issues.length === 0) return null;
        
        const isCollapsed = collapsedGroups.has(group.id);
        const IconComponent = iconMap[group.icon] || Wrench;
        const groupTime = group.issues.length * group.avgTimePerItem;

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
                <span className="text-xl">{group.emoji}</span>
                <IconComponent size={20} className={group.color.text} />
                <div className="text-left">
                  <span className={`font-semibold ${group.color.text}`}>
                    {group.name}
                  </span>
                  <p className="text-xs text-gray-600">{group.description}</p>
                </div>
                <span className={`text-sm px-2 py-1 rounded-full ${group.color.bg} ${group.color.text} border ${group.color.border}`}>
                  {group.issues.length}
                </span>
              </div>
              <span className={`text-sm ${group.color.text} opacity-75`}>
                ~{formatTotalTime(groupTime)}
              </span>
            </button>

            {!isCollapsed && (
              <div className="bg-white">
                <div className="px-4 py-2 border-b border-gray-100 bg-gray-50">
                  <p className="text-xs text-gray-500 italic">{group.whyMatters}</p>
                </div>
                <div className="p-4 space-y-3">
                  {group.issues.map(issue => (
                    <div key={issue.id} className="border border-gray-200 rounded-lg overflow-hidden">
                      <button
                        onClick={() => onToggleIssue(issue.id)}
                        className="w-full flex items-center justify-between p-3 hover:bg-gray-50 text-left"
                      >
                        <div className="flex items-center gap-3">
                          {expandedIssues.has(issue.id) ? (
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

                      {(displayLevel >= 2 || expandedIssues.has(issue.id)) && (
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
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
