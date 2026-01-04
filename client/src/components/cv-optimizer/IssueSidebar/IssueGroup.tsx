import { ChevronDown, ChevronRight, MapPin, ClipboardList } from 'lucide-react';

interface Issue {
  id: string;
  title: string;
  severity: 'critical' | 'important' | 'consider' | 'polish';
  isHighlightable?: boolean;
}

interface IssueGroupProps {
  severity: 'critical' | 'important' | 'consider' | 'polish';
  issues: Issue[];
  isExpanded: boolean;
  onToggle: () => void;
  onIssueClick: (issueId: string) => void;
  selectedIssueId?: string;
  fixedIssues?: Set<string>;
}

const SEVERITY_LABELS = {
  critical: 'Critical',
  important: 'Important',
  consider: 'Consider',
  polish: 'Polish',
};

const SEVERITY_COLORS = {
  critical: '#DC2626',
  important: '#F59E0B',
  consider: '#3B82F6',
  polish: '#6B7280',
};

export default function IssueGroup({ 
  severity, 
  issues, 
  isExpanded, 
  onToggle, 
  onIssueClick,
  selectedIssueId,
  fixedIssues = new Set()
}: IssueGroupProps) {
  if (issues.length === 0) return null;

  return (
    <div className="issue-group">
      <button className="issue-group-header" onClick={onToggle}>
        {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        <span 
          className="issue-group-dot"
          style={{ 
            width: 8, 
            height: 8, 
            borderRadius: '50%', 
            background: SEVERITY_COLORS[severity],
            marginLeft: 6,
            marginRight: 8
          }}
        />
        <span className="issue-group-label">
          {SEVERITY_LABELS[severity]} ({issues.length})
        </span>
      </button>

      {isExpanded && (
        <div className="issue-group-items">
          {issues.map(issue => {
            const isFixed = fixedIssues.has(issue.id);
            return (
              <div
                key={issue.id}
                className={`issue-item ${selectedIssueId === issue.id ? 'selected' : ''} ${isFixed ? 'issue-fixed' : ''}`}
                onClick={() => onIssueClick(issue.id)}
              >
                {isFixed && <span className="fixed-indicator">✓</span>}
                {issue.isHighlightable ? (
                  <span title="Click to highlight in CV">
                    <MapPin size={12} className="highlight-indicator highlightable" />
                  </span>
                ) : (
                  <span title="General feedback">
                    <ClipboardList size={12} className="highlight-indicator general" />
                  </span>
                )}
                <span className={`${isFixed ? 'issue-title-fixed' : ''} ${!issue.isHighlightable ? 'general-feedback' : ''}`}>
                  {issue.title}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
