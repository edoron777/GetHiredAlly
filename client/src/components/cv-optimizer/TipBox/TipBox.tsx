import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import '../../../styles/cv-optimizer/tipbox.css';

interface TipBoxProps {
  isOpen: boolean;
  onClose: () => void;
  issue: {
    id: string;
    severity: 'critical' | 'important' | 'consider' | 'polish';
    issueType: string;
    title: string;
    description: string;
    currentText?: string;
    suggestedText?: string;
    impact: string;
    howToFix: string;
  };
  onApplyFix?: (issueId: string, suggestedText: string) => void;
}

const SEVERITY_COLORS = {
  critical: { bg: '#fef2f2', text: '#dc2626', border: '#dc2626' },
  important: { bg: '#fff7ed', text: '#ea580c', border: '#ea580c' },
  consider: { bg: '#fefce8', text: '#ca8a04', border: '#ca8a04' },
  polish: { bg: '#f0fdf4', text: '#16a34a', border: '#16a34a' },
};

const SEVERITY_LABELS = {
  critical: 'Critical',
  important: 'Important',
  consider: 'Consider',
  polish: 'Polish',
};

export default function TipBox({ isOpen, onClose, issue, onApplyFix }: TipBoxProps) {
  const [editedText, setEditedText] = useState(issue.suggestedText || '');

  useEffect(() => {
    setEditedText(issue.suggestedText || '');
  }, [issue.suggestedText]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const colors = SEVERITY_COLORS[issue.severity];

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleApply = () => {
    if (onApplyFix && editedText) {
      onApplyFix(issue.id, editedText);
    }
    onClose();
  };

  return (
    <div className="tipbox-overlay" onClick={handleOverlayClick}>
      <div className="tipbox-modal">
        <div className="tipbox-header">
          <div className="flex items-center gap-3">
            <span 
              className="tipbox-severity-badge"
              style={{ 
                background: colors.bg, 
                color: colors.text,
                border: `1px solid ${colors.border}`
              }}
            >
              {SEVERITY_LABELS[issue.severity]}
            </span>
            <h3 className="tipbox-title">{issue.title}</h3>
          </div>
          <button onClick={onClose} className="tipbox-close">
            <X size={20} />
          </button>
        </div>

        <div className="tipbox-body">
          <div className="tipbox-section">
            <div className="tipbox-section-title">Why This Matters</div>
            <p className="tipbox-description">{issue.impact}</p>
          </div>

          {issue.currentText && (
            <div className="tipbox-section">
              <div className="tipbox-section-title">Current Text</div>
              <div className="tipbox-text-box tipbox-current">
                "{issue.currentText}"
              </div>
            </div>
          )}

          {issue.suggestedText && (
            <div className="tipbox-section">
              <div className="tipbox-section-title">Suggested Improvement</div>
              <textarea
                className="tipbox-textarea"
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
              />
            </div>
          )}

          <div className="tipbox-section">
            <div className="tipbox-section-title">How to Fix</div>
            <p className="tipbox-description">{issue.howToFix}</p>
          </div>
        </div>

        <div className="tipbox-footer">
          {issue.suggestedText && onApplyFix && (
            <button 
              onClick={handleApply}
              className="tipbox-btn tipbox-btn-primary"
            >
              Apply to CV
            </button>
          )}
          <button 
            onClick={onClose}
            className="tipbox-btn tipbox-btn-secondary"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
