import React, { useMemo } from 'react';
import { SideBySide } from '../../common/SideBySide';
import type { SideBySidePanelConfig, MarkerConfig } from '../../common/SideBySide/types';

interface SideBySideViewProps {
  originalCV: string;
  fixedCV: string;
  issues: Array<{
    id: string;
    severity: string;
    matchText?: string;
    current_text?: string;
    problematic_text?: string;
  }>;
  fixedIssues: Set<string>;
  appliedChanges?: Array<{
    originalText: string;
    newText: string;
    issueId: string;
  }>;
  onIssueClick?: (issueId: string) => void;
}

/**
 * SideBySideView - CV Optimizer specific wrapper
 * Uses the unified SideBySide component internally
 */
export const SideBySideView: React.FC<SideBySideViewProps> = ({
  originalCV,
  fixedCV,
  issues,
  fixedIssues,
  appliedChanges = [],
  onIssueClick,
}) => {
  const leftMarkers: MarkerConfig[] = useMemo(() => {
    return issues.map((issue) => ({
      id: issue.id,
      text: issue.matchText || issue.current_text || issue.problematic_text || '',
      severity: issue.severity as MarkerConfig['severity'],
      type: 'issue' as const,
    }));
  }, [issues]);

  const rightMarkers: MarkerConfig[] = useMemo(() => {
    return issues
      .filter((issue) => !fixedIssues.has(issue.id))
      .map((issue) => ({
        id: issue.id,
        text: issue.matchText || issue.current_text || issue.problematic_text || '',
        severity: issue.severity as MarkerConfig['severity'],
        type: 'issue' as const,
      }));
  }, [issues, fixedIssues]);

  const totalIssues = issues.length;
  const fixedCount = fixedIssues.size;
  const remainingCount = totalIssues - fixedCount;

  const leftPanel: SideBySidePanelConfig = {
    title: 'Original CV',
    content: originalCV,
    type: 'original',
    markers: leftMarkers,
    stats: {
      label: 'issues found',
      value: totalIssues,
      color: 'red',
    },
  };

  const rightPanel: SideBySidePanelConfig = {
    title: 'Fixed CV',
    content: fixedCV,
    type: 'fixed',
    markers: rightMarkers,
    changes: appliedChanges.map((change) => ({
      originalText: change.originalText,
      newText: change.newText,
      issueId: change.issueId,
    })),
    stats: {
      label: fixedCount > 0 ? `${fixedCount} fixed, ${remainingCount} remaining` : 'No fixes yet',
      value: '',
      color: fixedCount > 0 ? 'green' : 'neutral',
    },
  };

  const handleMarkerClick = (id: string, _panel: 'left' | 'right') => {
    onIssueClick?.(id);
  };

  return (
    <SideBySide
      left={leftPanel}
      right={rightPanel}
      syncScroll={true}
      maxHeight="600px"
      onMarkerClick={handleMarkerClick}
    />
  );
};

export default SideBySideView;
