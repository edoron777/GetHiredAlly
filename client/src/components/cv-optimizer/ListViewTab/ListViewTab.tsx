import { useState } from 'react';
import { AlertCircle, AlertTriangle, Info, Sparkles, ChevronDown, ChevronRight } from 'lucide-react';
import '../../../styles/cv-optimizer/list-view.css';

interface Issue {
  id: string;
  severity: 'critical' | 'important' | 'consider' | 'polish';
  title: string;
  description?: string;
  currentText?: string;
  suggestedText?: string;
}

interface ListViewTabProps {
  issues: Issue[];
  onIssueClick: (issueId: string) => void;
  onApplyFix: (issueId: string, suggestedText: string) => void;
}

const SEVERITY_CONFIG = {
  critical: { 
    icon: AlertCircle, 
    color: '#dc2626', 
    headerBg: '#EF4444',
    cardBg: '#fef2f2', 
    label: 'Critical' 
  },
  important: { 
    icon: AlertTriangle, 
    color: '#ea580c', 
    headerBg: '#F97316',
    cardBg: '#fff7ed', 
    label: 'Important' 
  },
  consider: { 
    icon: Info, 
    color: '#ca8a04', 
    headerBg: '#EAB308',
    cardBg: '#fefce8', 
    label: 'Consider' 
  },
  polish: { 
    icon: Sparkles, 
    color: '#16a34a', 
    headerBg: '#22C55E',
    cardBg: '#f0fdf4', 
    label: 'Polish' 
  },
};

const SEVERITY_ORDER: Array<'critical' | 'important' | 'consider' | 'polish'> = ['critical', 'important', 'consider', 'polish'];

export default function ListViewTab({ issues, onIssueClick, onApplyFix }: ListViewTabProps) {
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    critical: true,
    important: true,
    consider: true,
    polish: true,
  });

  const groupedIssues = SEVERITY_ORDER.reduce((acc, severity) => {
    acc[severity] = issues.filter(issue => issue.severity === severity);
    return acc;
  }, {} as Record<string, Issue[]>);

  const toggleGroup = (severity: string) => {
    setExpandedGroups(prev => ({
      ...prev,
      [severity]: !prev[severity],
    }));
  };

  const expandAll = () => {
    setExpandedGroups({ critical: true, important: true, consider: true, polish: true });
  };

  const collapseAll = () => {
    setExpandedGroups({ critical: false, important: false, consider: false, polish: false });
  };

  return (
    <div className="list-view-container">
      <div className="list-view-header">
        <p className="list-view-summary">
          Found <strong>{issues.length}</strong> opportunities to improve your CV
        </p>

        <div className="list-view-controls">
          <button className="expand-collapse-btn" onClick={expandAll}>
            Expand All
          </button>
          <button className="expand-collapse-btn" onClick={collapseAll}>
            Collapse All
          </button>
        </div>
      </div>

      <div className="severity-groups">
        {SEVERITY_ORDER.map(severity => {
          const config = SEVERITY_CONFIG[severity];
          const severityIssues = groupedIssues[severity];
          const isExpanded = expandedGroups[severity];
          const Icon = config.icon;

          if (severityIssues.length === 0) return null;

          return (
            <div key={severity} className="severity-group">
              <button
                className="severity-group-header"
                style={{ backgroundColor: config.headerBg }}
                onClick={() => toggleGroup(severity)}
              >
                <div className="severity-header-left">
                  <Icon size={18} color="white" />
                  <span className="severity-header-title">
                    {config.label} ({severityIssues.length} {severityIssues.length === 1 ? 'issue' : 'issues'})
                  </span>
                </div>
                <div className="severity-header-chevron">
                  {isExpanded ? <ChevronDown size={20} color="white" /> : <ChevronRight size={20} color="white" />}
                </div>
              </button>

              <div className={`severity-group-content ${isExpanded ? 'expanded' : 'collapsed'}`}>
                {severityIssues.map(issue => (
                  <div key={issue.id} className="issue-card" style={{ borderLeftColor: config.color }}>
                    <div className="issue-card-header">
                      <span 
                        className="issue-severity-badge"
                        style={{ background: config.cardBg, color: config.color }}
                      >
                        <Icon size={14} />
                        {config.label.toUpperCase()}
                      </span>
                      <span className="issue-card-title">{issue.title}</span>
                    </div>

                    {issue.description && (
                      <p className="issue-card-description">{issue.description}</p>
                    )}

                    {issue.currentText && (
                      <div className="issue-card-context">
                        <span className="context-label">Current:</span>
                        <span className="context-text">"{issue.currentText}"</span>
                      </div>
                    )}

                    <div className="issue-card-actions">
                      <button 
                        className="view-details-btn"
                        onClick={() => onIssueClick(issue.id)}
                      >
                        View Details
                      </button>
                      {issue.suggestedText && (
                        <button 
                          className="quick-fix-btn"
                          onClick={() => onApplyFix(issue.id, issue.suggestedText!)}
                        >
                          Quick Fix
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
