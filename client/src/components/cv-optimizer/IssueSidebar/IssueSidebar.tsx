import { useState } from 'react';
import ScoreWidget from './ScoreWidget';
import IssueGroup from './IssueGroup';
import '../../../styles/cv-optimizer/sidebar.css';

interface Issue {
  id: string;
  title: string;
  severity: 'critical' | 'important' | 'consider' | 'polish';
}

interface IssueSidebarProps {
  score: number;
  issues: Issue[];
  onIssueClick: (issueId: string) => void;
  selectedIssueId?: string;
  fixedIssues?: Set<string>;
}

export default function IssueSidebar({ 
  score, 
  issues, 
  onIssueClick, 
  selectedIssueId,
  fixedIssues = new Set()
}: IssueSidebarProps) {
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    critical: true,
    important: false,
    consider: false,
    polish: false,
  });

  const groupedIssues = {
    critical: issues.filter(i => i.severity === 'critical'),
    important: issues.filter(i => i.severity === 'important'),
    consider: issues.filter(i => i.severity === 'consider'),
    polish: issues.filter(i => i.severity === 'polish'),
  };

  const issuesCounts = {
    critical: groupedIssues.critical.length,
    important: groupedIssues.important.length,
    consider: groupedIssues.consider.length,
    polish: groupedIssues.polish.length,
  };

  const toggleGroup = (severity: string) => {
    setExpandedGroups(prev => ({
      ...prev,
      [severity]: !prev[severity],
    }));
  };

  const fixedCount = fixedIssues.size;
  const totalCount = issues.length;
  const progressPercent = totalCount > 0 ? (fixedCount / totalCount) * 100 : 0;

  return (
    <div className="issue-sidebar">
      <ScoreWidget score={score} issuesCounts={issuesCounts} />

      {totalCount > 0 && (
        <div className="progress-summary">
          <div className="progress-text">
            Progress: {fixedCount} / {totalCount} fixed
          </div>
          <div className="progress-bar-bg">
            <div 
              className="progress-bar-fill"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      )}

      <div className="sidebar-divider" />

      <div className="issue-groups">
        {(['critical', 'important', 'consider', 'polish'] as const).map(severity => (
          <IssueGroup
            key={severity}
            severity={severity}
            issues={groupedIssues[severity]}
            isExpanded={expandedGroups[severity]}
            onToggle={() => toggleGroup(severity)}
            onIssueClick={onIssueClick}
            selectedIssueId={selectedIssueId}
            fixedIssues={fixedIssues}
          />
        ))}
      </div>
    </div>
  );
}
