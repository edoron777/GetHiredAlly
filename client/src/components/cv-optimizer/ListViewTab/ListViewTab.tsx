import { useState } from 'react';
import { AlertCircle, AlertTriangle, Info, Sparkles, ChevronDown } from 'lucide-react';
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
  critical: { icon: AlertCircle, color: '#dc2626', bg: '#fef2f2', label: 'CRITICAL' },
  important: { icon: AlertTriangle, color: '#ea580c', bg: '#fff7ed', label: 'IMPORTANT' },
  consider: { icon: Info, color: '#ca8a04', bg: '#fefce8', label: 'CONSIDER' },
  polish: { icon: Sparkles, color: '#16a34a', bg: '#f0fdf4', label: 'POLISH' },
};

const SEVERITY_ORDER = ['critical', 'important', 'consider', 'polish'];

export default function ListViewTab({ issues, onIssueClick, onApplyFix }: ListViewTabProps) {
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'impact' | 'severity'>('severity');
  const [showFilterDropdown, setShowFilterDropdown] = useState(false);
  const [showSortDropdown, setShowSortDropdown] = useState(false);

  const filteredIssues = issues.filter(issue => 
    filterSeverity === 'all' || issue.severity === filterSeverity
  );

  const sortedIssues = [...filteredIssues].sort((a, b) => {
    if (sortBy === 'severity') {
      return SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity);
    }
    return 0;
  });

  return (
    <div className="list-view-container">
      <div className="list-view-header">
        <p className="list-view-summary">
          Found <strong>{issues.length}</strong> opportunities to improve your CV
        </p>

        <div className="list-view-controls">
          <div className="dropdown-wrapper">
            <button 
              className="dropdown-trigger"
              onClick={() => { setShowFilterDropdown(!showFilterDropdown); setShowSortDropdown(false); }}
            >
              Show: {filterSeverity === 'all' ? 'All' : SEVERITY_CONFIG[filterSeverity as keyof typeof SEVERITY_CONFIG]?.label}
              <ChevronDown size={14} />
            </button>
            {showFilterDropdown && (
              <div className="dropdown-menu">
                <div className="dropdown-item" onClick={() => { setFilterSeverity('all'); setShowFilterDropdown(false); }}>All</div>
                <div className="dropdown-item" onClick={() => { setFilterSeverity('critical'); setShowFilterDropdown(false); }}>Critical</div>
                <div className="dropdown-item" onClick={() => { setFilterSeverity('important'); setShowFilterDropdown(false); }}>Important</div>
                <div className="dropdown-item" onClick={() => { setFilterSeverity('consider'); setShowFilterDropdown(false); }}>Consider</div>
                <div className="dropdown-item" onClick={() => { setFilterSeverity('polish'); setShowFilterDropdown(false); }}>Polish</div>
              </div>
            )}
          </div>

          <div className="dropdown-wrapper">
            <button 
              className="dropdown-trigger"
              onClick={() => { setShowSortDropdown(!showSortDropdown); setShowFilterDropdown(false); }}
            >
              Sort: {sortBy === 'severity' ? 'By Severity' : 'By Impact'}
              <ChevronDown size={14} />
            </button>
            {showSortDropdown && (
              <div className="dropdown-menu">
                <div className="dropdown-item" onClick={() => { setSortBy('severity'); setShowSortDropdown(false); }}>By Severity</div>
                <div className="dropdown-item" onClick={() => { setSortBy('impact'); setShowSortDropdown(false); }}>By Impact</div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="issue-cards-list">
        {sortedIssues.map(issue => {
          const config = SEVERITY_CONFIG[issue.severity];
          const Icon = config.icon;

          return (
            <div key={issue.id} className="issue-card" style={{ borderLeftColor: config.color }}>
              <div className="issue-card-header">
                <span 
                  className="issue-severity-badge"
                  style={{ background: config.bg, color: config.color }}
                >
                  <Icon size={14} />
                  {config.label}
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
          );
        })}
      </div>
    </div>
  );
}
