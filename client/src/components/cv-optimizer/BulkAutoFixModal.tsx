import React from 'react';
import { Zap, X } from 'lucide-react';
import './BulkAutoFixModal.css';

interface BulkAutoFixModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  count: number;
  isLoading?: boolean;
}

export const BulkAutoFixModal: React.FC<BulkAutoFixModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  count,
  isLoading = false
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content bulk-fix-modal" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <X size={20} />
        </button>
        
        <div className="modal-header">
          <Zap className="modal-icon" size={32} />
          <h2>Auto Fix {count} Issues?</h2>
        </div>
        
        <div className="modal-body">
          <p>
            This will automatically apply suggested fixes to <strong>{count}</strong> issues.
          </p>
          <p>
            Your CV will be rescanned to show your new score.
          </p>
        </div>
        
        <div className="modal-actions">
          <button 
            className="modal-button secondary"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </button>
          <button 
            className="modal-button primary"
            onClick={onConfirm}
            disabled={isLoading}
          >
            {isLoading ? 'Processing...' : 'Yes, Fix All'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default BulkAutoFixModal;
