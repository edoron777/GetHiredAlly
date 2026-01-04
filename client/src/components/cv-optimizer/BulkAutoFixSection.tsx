import React from 'react';
import { Zap } from 'lucide-react';
import './BulkAutoFixSection.css';

interface BulkAutoFixSectionProps {
  autoFixableCount: number;
  totalIssues: number;
  onAutoFixClick: () => void;
  isLoading?: boolean;
}

export const BulkAutoFixSection: React.FC<BulkAutoFixSectionProps> = ({
  autoFixableCount,
  totalIssues,
  onAutoFixClick,
  isLoading = false
}) => {
  const manualCount = totalIssues - autoFixableCount;

  return (
    <div className="bulk-auto-fix-section">
      <div className="bulk-auto-fix-header">
        <Zap className="bulk-auto-fix-icon" size={20} />
        <span className="bulk-auto-fix-title">Quick Improvement Available</span>
      </div>
      
      <p className="bulk-auto-fix-description">
        <strong>{autoFixableCount}</strong> of {totalIssues} issues can be fixed automatically
      </p>
      
      <button
        className="bulk-auto-fix-button"
        onClick={onAutoFixClick}
        disabled={isLoading}
      >
        {isLoading ? (
          <>Processing...</>
        ) : (
          <>
            <Zap size={16} />
            Auto Fix {autoFixableCount} Issues
          </>
        )}
      </button>
      
      {manualCount > 0 && (
        <p className="bulk-auto-fix-note">
          The remaining {manualCount} issues need your personal input
        </p>
      )}
    </div>
  );
};

export default BulkAutoFixSection;
