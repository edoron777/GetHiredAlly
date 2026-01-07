import React, { forwardRef } from 'react';
import type { SideBySidePanelConfig } from './types';
import { TextMarker, CV_OPTIMIZER_COLORS } from '../TextMarker';

interface SideBySidePanelProps extends SideBySidePanelConfig {
  onScroll?: () => void;
  onMarkerClick?: (id: string) => void;
  maxHeight?: string;
}

/**
 * Individual panel for SideBySide component
 * Displays content with optional markers and stats
 */
export const SideBySidePanel = forwardRef<HTMLDivElement, SideBySidePanelProps>(
  (
    {
      title,
      content,
      type,
      markers = [],
      changes = [],
      stats,
      className = '',
      onScroll,
      onMarkerClick,
      maxHeight = '600px',
    },
    ref
  ) => {
    const getHeaderStyle = () => {
      switch (type) {
        case 'original':
          return 'bg-red-50 border-red-200 text-red-800';
        case 'fixed':
          return 'bg-green-50 border-green-200 text-green-800';
        default:
          return 'bg-gray-50 border-gray-200 text-gray-800';
      }
    };

    const getIndicatorColor = () => {
      switch (type) {
        case 'original':
          return 'bg-red-500';
        case 'fixed':
          return 'bg-green-500';
        default:
          return 'bg-gray-500';
      }
    };

    const getStatsBadgeStyle = () => {
      if (!stats?.color) return 'bg-gray-100 text-gray-700';
      
      const colorMap: Record<string, string> = {
        red: 'bg-red-100 text-red-700',
        green: 'bg-green-100 text-green-700',
        amber: 'bg-amber-100 text-amber-700',
        blue: 'bg-blue-100 text-blue-700',
        neutral: 'bg-gray-100 text-gray-700',
      };
      
      return colorMap[stats.color] || colorMap.neutral;
    };

    const highlightChanges = (text: string): React.ReactNode => {
      if (!changes || changes.length === 0) {
        return text;
      }

      let result = text;
      changes.forEach((change) => {
        if (type === 'fixed' && change.newText) {
          result = result.replace(
            change.newText,
            `<mark class="sbs-change-highlight">${change.newText}</mark>`
          );
        }
      });

      return <span dangerouslySetInnerHTML={{ __html: result }} />;
    };

    const renderContent = () => {
      if (markers && markers.length > 0) {
        const textMarkerItems = markers.map((marker) => ({
          id: marker.id,
          matchText: marker.text,
          tag: marker.severity || 'consider',
        }));

        return (
          <TextMarker
            content={content}
            markers={textMarkerItems}
            config={{
              style: 'rectangle',
              tagColors: CV_OPTIMIZER_COLORS,
              onClick: onMarkerClick,
            }}
          />
        );
      }

      if (changes && changes.length > 0) {
        return highlightChanges(content);
      }

      return <div className="whitespace-pre-wrap">{content}</div>;
    };

    return (
      <div className={`sbs-panel flex flex-col border rounded-lg overflow-hidden ${className}`}>
        <div className={`sbs-panel-header px-4 py-3 border-b flex items-center justify-between ${getHeaderStyle()}`}>
          <div className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${getIndicatorColor()}`} />
            <span className="font-semibold">{title}</span>
          </div>
          
          {stats && (
            <span className={`text-sm px-2 py-1 rounded ${getStatsBadgeStyle()}`}>
              {stats.value} {stats.label}
            </span>
          )}
        </div>

        <div
          ref={ref}
          onScroll={onScroll}
          className="sbs-panel-content flex-1 overflow-auto p-4 bg-white"
          style={{ maxHeight }}
        >
          {renderContent()}
        </div>
      </div>
    );
  }
);

SideBySidePanel.displayName = 'SideBySidePanel';

export default SideBySidePanel;
