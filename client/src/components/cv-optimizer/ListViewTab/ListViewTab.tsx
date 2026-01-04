import { useState } from 'react';
import { AlertCircle, AlertTriangle, Info, Sparkles, ChevronDown, ChevronRight } from 'lucide-react';
import { SEVERITY_COLORS } from '@/constants/severityColors';
import '../../../styles/cv-optimizer/list-view.css';

interface Issue {
  id: string;
  severity: 'critical' | 'important' | 'consider' | 'polish';
  title: string;
  description?: string;
  currentText?: string;
}

interface ListViewTabProps {
  issues: Issue[];
  onIssueClick: (issueId: string) => void;
}

const SEVERITY_CONFIG = {
  critical: { 
    icon: AlertCircle, 
    color: SEVERITY_COLORS.critical.primary, 
    headerBg: SEVERITY_COLORS.critical.primary,
    cardBg: SEVERITY_COLORS.critical.background, 
    label: 'Critical' 
  },
  important: { 
    icon: AlertTriangle, 
    color: SEVERITY_COLORS.important.primary, 
    headerBg: SEVERITY_COLORS.important.primary,
    cardBg: SEVERITY_COLORS.important.background, 
    label: 'Important' 
  },
  consider: { 
    icon: Info, 
    color: SEVERITY_COLORS.consider.primary, 
    headerBg: SEVERITY_COLORS.consider.primary,
    cardBg: SEVERITY_COLORS.consider.background, 
    label: 'Consider' 
  },
  polish: { 
    icon: Sparkles, 
    color: SEVERITY_COLORS.polish.primary, 
    headerBg: SEVERITY_COLORS.polish.primary,
    cardBg: SEVERITY_COLORS.polish.background, 
    label: 'Polish' 
  },
};

const SEVERITY_ORDER: Array<'critical' | 'important' | 'consider' | 'polish'> = ['critical', 'important', 'consider', 'polish'];

export default function ListViewTab({ issues, onIssueClick }: ListViewTabProps) {
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
                  <div 
                    key={issue.id}
                    className="issue-row"
                    onClick={() => onIssueClick(issue.id)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => e.key === 'Enter' && onIssueClick(issue.id)}
                  >
                    <span className="issue-status-icon">○</span>
                    <div className="issue-row-content">
                      <span className="issue-row-title">{issue.title}</span>
                      <span className="issue-row-preview">
                        {issue.currentText 
                          ? `"${issue.currentText.substring(0, 60)}${issue.currentText.length > 60 ? '...' : ''}"` 
                          : issue.description?.substring(0, 80)}
                      </span>
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
