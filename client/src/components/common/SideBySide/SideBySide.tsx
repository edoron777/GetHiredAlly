import React from 'react';
import type { SideBySideProps } from './types';
import { SideBySidePanel } from './SideBySidePanel';
import { useSideBySideSync } from './useSideBySideSync';
import './SideBySide.css';

/**
 * SideBySide Component
 * 
 * A reusable side-by-side comparison component for GetHiredAlly.
 * Used for comparing original vs fixed content (CV, answers, etc.)
 * 
 * @example
 * <SideBySide
 *   left={{
 *     title: "Original CV",
 *     content: originalText,
 *     type: "original",
 *     stats: { label: "issues found", value: 9, color: "red" }
 *   }}
 *   right={{
 *     title: "Fixed CV",
 *     content: fixedText,
 *     type: "fixed",
 *     stats: { label: "fixed", value: 5, color: "green" }
 *   }}
 *   syncScroll={true}
 * />
 */
export const SideBySide: React.FC<SideBySideProps> = ({
  left,
  right,
  syncScroll = true,
  maxHeight = '600px',
  onMarkerClick,
  className = '',
}) => {
  const {
    leftPanelRef,
    rightPanelRef,
    handleLeftScroll,
    handleRightScroll,
  } = useSideBySideSync(syncScroll);

  const handleLeftMarkerClick = (id: string) => {
    onMarkerClick?.(id, 'left');
  };

  const handleRightMarkerClick = (id: string) => {
    onMarkerClick?.(id, 'right');
  };

  return (
    <div className={`sbs-container grid grid-cols-1 md:grid-cols-2 gap-4 ${className}`}>
      <SideBySidePanel
        ref={leftPanelRef}
        {...left}
        onScroll={handleLeftScroll}
        onMarkerClick={handleLeftMarkerClick}
        maxHeight={maxHeight}
      />

      <SideBySidePanel
        ref={rightPanelRef}
        {...right}
        onScroll={handleRightScroll}
        onMarkerClick={handleRightMarkerClick}
        maxHeight={maxHeight}
      />
    </div>
  );
};

export default SideBySide;
