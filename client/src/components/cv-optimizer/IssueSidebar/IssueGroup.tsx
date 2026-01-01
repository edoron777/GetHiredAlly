import { ChevronDown, ChevronRight } from 'lucide-react';

interface Issue {
  id: string;
  title: string;
  severity: 'critical' | 'important' | 'consider' | 'polish';
}

interface IssueGroupProps {
  severity: 'critical' | 'important' | 'consider' | 'polish';
  issues: Issue[];
  isExpanded: boolean;
  onToggle: () => void;
  onIssueClick: (issueId: string) => void;
  selectedIssueId?: string;
}

const SEVERITY_LABELS = {
  critical: 'Critical',
  important: 'Important',
  consider: 'Consider',
  polish: 'Polish',
};

const SEVERITY_COLORS = {
  critical: '#dc2626',
  important: '#ea580c',
  consider: '#ca8a04',
  polish: '#16a34a',
};

export default function IssueGroup({ 
  severity, 
  issues, 
  isExpanded, 
  onToggle, 
  onIssueClick,
  selectedIssueId 
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
          {issues.map(issue => (
            <div
              key={issue.id}
              className={`issue-item ${selectedIssueId === issue.id ? 'selected' : ''}`}
              onClick={() => onIssueClick(issue.id)}
            >
              {issue.title}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
