import { useState } from 'react';
import { MapPin, ClipboardList } from 'lucide-react';
import ScoreWidget from './ScoreWidget';
import IssueGroup from './IssueGroup';
import { ProgressSection } from '../ProgressSection';
import '../../../styles/cv-optimizer/sidebar.css';

interface Issue {
  id: string;
  title: string;
  severity: 'critical' | 'important' | 'consider' | 'polish';
  isHighlightable?: boolean;
}

interface IssueSidebarProps {
  score: number;
  originalScore?: number;
  issues: Issue[];
  onIssueClick: (issueId: string) => void;
  selectedIssueId?: string;
  fixedIssues?: Set<string>;
  pendingIssues?: Set<string>;
  pendingChanges?: number;
  onUpdateScore?: () => void;
  isLoading?: boolean;
}

export default function IssueSidebar({ 
  score, 
  originalScore,
  issues, 
  onIssueClick, 
  selectedIssueId,
  fixedIssues = new Set(),
  pendingIssues = new Set(),
  pendingChanges = 0,
  onUpdateScore,
  isLoading = false
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

  const totalCount = issues.length;
  
  const highlightableCount = issues.filter(i => i.isHighlightable).length;
  const generalCount = issues.filter(i => !i.isHighlightable).length;

  return (
    <div className="issue-sidebar">
      <ScoreWidget score={score} originalScore={originalScore} issuesCounts={issuesCounts} />

      {totalCount > 0 && onUpdateScore && (
        <ProgressSection
          issues={issues}
          fixedIssues={fixedIssues}
          pendingIssues={pendingIssues}
          pendingChanges={pendingChanges}
          onUpdateScore={onUpdateScore}
          isLoading={isLoading}
        />
      )}

      <div className="sidebar-divider" />
      
      <div className="issue-legend" data-tour="issues-summary">
        <div className="legend-title">Found {totalCount} opportunities</div>
        <div className="legend-counts">
          <span className="legend-item">
            <MapPin size={10} className="legend-icon highlightable" />
            {highlightableCount} in document
          </span>
          <span className="legend-item">
            <ClipboardList size={10} className="legend-icon general" />
            {generalCount} general
          </span>
        </div>
      </div>

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
