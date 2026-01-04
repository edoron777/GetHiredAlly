import React from 'react';
import { X, PartyPopper, BarChart3, AlertTriangle, Save, GitCompare } from 'lucide-react';
import './ResultModal.css';

interface ResultModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: {
    previousScore: number;
    newScore: number;
    fixedCount: number;
    remainingCount: number;
    scoreChange: 'improved' | 'unchanged' | 'dropped';
  } | null;
  onSaveCV?: () => void;
  onCompareVersions?: () => void;
}

export const ResultModal: React.FC<ResultModalProps> = ({
  isOpen,
  onClose,
  data,
  onSaveCV,
  onCompareVersions
}) => {
  if (!isOpen || !data) return null;

  const { previousScore, newScore, fixedCount, remainingCount, scoreChange } = data;
  const scoreDiff = newScore - previousScore;

  const config = {
    improved: {
      icon: <PartyPopper size={40} />,
      title: '🎉 Your CV Has Improved!',
      background: '#F0FDF4',
      borderColor: '#22C55E',
      iconColor: '#22C55E'
    },
    unchanged: {
      icon: <BarChart3 size={40} />,
      title: '📊 Scan Complete',
      background: '#F5F5F5',
      borderColor: '#9CA3AF',
      iconColor: '#6B7280'
    },
    dropped: {
      icon: <AlertTriangle size={40} />,
      title: '⚠️ Score Changed',
      background: '#FEF2F2',
      borderColor: '#EF4444',
      iconColor: '#EF4444'
    }
  };

  const { icon, title, background, borderColor, iconColor } = config[scoreChange];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className="modal-content result-modal"
        style={{ background, borderColor, borderWidth: '2px', borderStyle: 'solid' }}
        onClick={e => e.stopPropagation()}
      >
        <button className="modal-close" onClick={onClose}>
          <X size={20} />
        </button>
        
        <div className="result-modal-header">
          <div className="result-icon" style={{ color: iconColor }}>
            {icon}
          </div>
          <h2>{title}</h2>
        </div>
        
        <div className="score-comparison">
          <span className="score-old">{previousScore}</span>
          <span className="score-arrow">→</span>
          <span className="score-new">{newScore}</span>
        </div>
        
        <div className="score-diff" style={{ color: iconColor }}>
          {scoreDiff > 0 && `+${scoreDiff} points!`}
          {scoreDiff === 0 && 'No change'}
          {scoreDiff < 0 && `${scoreDiff} points`}
        </div>
        
        <div className="result-stats">
          <p>✅ {fixedCount} issues fixed</p>
          <p>📋 {remainingCount} issues remaining</p>
        </div>
        
        <div className="result-actions">
          {onSaveCV && (
            <button className="modal-button primary" onClick={onSaveCV}>
              <Save size={16} />
              Save CV
            </button>
          )}
          {onCompareVersions && (
            <button className="modal-button secondary" onClick={onCompareVersions}>
              <GitCompare size={16} />
              Compare Versions
            </button>
          )}
          <button className="modal-button secondary" onClick={onClose}>
            Keep Editing
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultModal;
