import { useRef, useCallback } from 'react';

/**
 * Custom hook for synchronized scrolling between two panels
 * @param enabled - Whether sync scrolling is enabled
 * @returns Refs and handler for both panels
 */
export function useSideBySideSync(enabled: boolean = true) {
  const leftPanelRef = useRef<HTMLDivElement>(null);
  const rightPanelRef = useRef<HTMLDivElement>(null);
  const isSyncing = useRef(false);

  const handleScroll = useCallback(
    (source: 'left' | 'right') => {
      if (!enabled || isSyncing.current) return;

      const sourcePanel = source === 'left' ? leftPanelRef.current : rightPanelRef.current;
      const targetPanel = source === 'left' ? rightPanelRef.current : leftPanelRef.current;

      if (!sourcePanel || !targetPanel) return;

      isSyncing.current = true;

      // Calculate scroll percentage
      const scrollPercentage = sourcePanel.scrollTop / 
        (sourcePanel.scrollHeight - sourcePanel.clientHeight);

      // Apply to target panel
      const targetScrollTop = scrollPercentage * 
        (targetPanel.scrollHeight - targetPanel.clientHeight);

      targetPanel.scrollTop = targetScrollTop;

      // Reset syncing flag after a short delay
      requestAnimationFrame(() => {
        isSyncing.current = false;
      });
    },
    [enabled]
  );

  const handleLeftScroll = useCallback(() => handleScroll('left'), [handleScroll]);
  const handleRightScroll = useCallback(() => handleScroll('right'), [handleScroll]);

  return {
    leftPanelRef,
    rightPanelRef,
    handleLeftScroll,
    handleRightScroll,
  };
}
