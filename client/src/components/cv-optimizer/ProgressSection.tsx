import React, { useMemo } from 'react';
import { Clock, RefreshCw } from 'lucide-react';
import './ProgressSection.css';

interface Issue {
  id?: string;
  issue_code?: string;
  severity: 'critical' | 'important' | 'consider' | 'polish';
}

interface ProgressSectionProps {
  issues: Issue[];
  fixedIssues: Set<string>;
  pendingIssues: Set<string>;
  pendingChanges: number;
  onUpdateScore: () => void;
  isLoading?: boolean;
}

const SEVERITY_WEIGHTS = {
  critical: 9,
  important: 6,
  consider: 4,
  polish: 2
};

export const ProgressSection: React.FC<ProgressSectionProps> = ({
  issues,
  fixedIssues,
  pendingIssues,
  pendingChanges,
  onUpdateScore,
  isLoading = false
}) => {
  const { progress, addressedCount, totalCount } = useMemo(() => {
    if (!issues || issues.length === 0) {
      return { progress: 0, addressedCount: 0, totalCount: 0 };
    }
    
    const totalWeight = issues.reduce((sum, issue) => 
      sum + (SEVERITY_WEIGHTS[issue.severity] || 2), 0);
    
    const addressedWeight = issues.reduce((sum, issue) => {
      const issueId = issue.id || issue.issue_code || '';
      if (fixedIssues.has(issueId) || pendingIssues.has(issueId)) {
        return sum + (SEVERITY_WEIGHTS[issue.severity] || 2);
      }
      return sum;
    }, 0);
    
    const addressedCount = fixedIssues.size + pendingIssues.size;
    const progress = totalWeight > 0 
      ? Math.round((addressedWeight / totalWeight) * 100) 
      : 0;
    
    return { progress, addressedCount, totalCount: issues.length };
  }, [issues, fixedIssues, pendingIssues]);

  return (
    <div className="progress-section">
      <h3 className="progress-title">Progress</h3>
      
      <div className="progress-bar-container">
        <div 
          className="progress-bar-fill"
          style={{ width: `${progress}%` }}
        />
      </div>
      
      <p className="progress-text">
        {addressedCount} of {totalCount} issues addressed ({progress}%)
      </p>
      
      {pendingChanges > 0 && (
        <div className="pending-changes-box">
          <div className="pending-header">
            <Clock size={16} />
            <span>{pendingChanges} changes pending</span>
          </div>
          
          <button
            className="update-score-button"
            onClick={onUpdateScore}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <RefreshCw size={16} className="animate-spin" />
                Updating...
              </>
            ) : (
              <>
                <RefreshCw size={16} />
                Update &amp; See New Score
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default ProgressSection;
