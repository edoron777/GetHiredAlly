import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useServiceSession } from './useServiceSession';
import type { ServiceSessionData } from './sessionTypes';

interface UserSessionKeepProps {
  serviceName: string;
  onStartNew?: () => void;
}

interface ConfirmDialogProps {
  isOpen: boolean;
  session: ServiceSessionData;
  onCancel: () => void;
  onConfirm: () => void;
  onDownload?: () => void;
}

const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  session,
  onCancel,
  onConfirm,
  onDownload
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Start New Analysis?
        </h3>
        <p className="text-gray-600 mb-4">
          This will clear your current work:
        </p>
        <div className="bg-gray-50 rounded p-3 mb-4">
          <p className="font-medium text-gray-900">{session.displayTitle}</p>
          <p className="text-sm text-gray-500">{session.summary}</p>
        </div>
        <p className="text-sm text-gray-500 mb-6">
          You can download your results before starting over.
        </p>
        <div className="flex gap-3 justify-end flex-wrap">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          {onDownload && (
            <button
              onClick={onDownload}
              className="px-4 py-2 border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
            >
              Download Results
            </button>
          )}
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Start New
          </button>
        </div>
      </div>
    </div>
  );
};

const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  return date.toLocaleDateString();
};

export const UserSessionKeep: React.FC<UserSessionKeepProps> = ({
  serviceName,
  onStartNew
}) => {
  const { session, isLoading, archiveSession } = useServiceSession(serviceName);
  const [showConfirm, setShowConfirm] = useState(false);

  if (isLoading || !session) {
    return null;
  }

  const handleStartNew = async () => {
    const success = await archiveSession();
    if (success) {
      setShowConfirm(false);
      onStartNew?.();
    }
  };

  const handleDownload = () => {
    const exportUrl = `${session.metadata?.exportUrl || '#'}`;
    if (exportUrl !== '#') {
      window.open(exportUrl, '_blank');
    }
  };

  return (
    <>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-blue-900 flex items-center gap-2">
              You have work in progress
            </h3>
            <p className="text-sm text-blue-700 mt-1 truncate">
              {session.summary}
            </p>
            <p className="text-xs text-blue-500 mt-1">
              Last updated: {formatTimeAgo(session.updatedAt)}
            </p>
          </div>
          <div className="flex gap-3">
            <Link
              to={session.continueUrl}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Continue
            </Link>
            <button
              onClick={() => setShowConfirm(true)}
              className="bg-white text-blue-600 border border-blue-300 px-4 py-2 rounded-lg hover:bg-blue-50 transition-colors font-medium"
            >
              Start New
            </button>
          </div>
        </div>
      </div>

      <ConfirmDialog
        isOpen={showConfirm}
        session={session}
        onCancel={() => setShowConfirm(false)}
        onConfirm={handleStartNew}
        onDownload={session.metadata?.exportUrl ? handleDownload : undefined}
      />
    </>
  );
};

export default UserSessionKeep;
