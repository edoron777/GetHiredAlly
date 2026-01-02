import React from 'react';
import { TextMarker, CV_OPTIMIZER_COLORS } from '../../common/TextMarker';

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
}

const SideBySideView: React.FC<SideBySideViewProps> = ({
  originalCV,
  fixedCV,
  issues,
  fixedIssues
}) => {
  const originalMarkers = issues
    .map(issue => ({
      id: issue.id,
      matchText: issue.matchText || issue.current_text || issue.problematic_text || '',
      tag: issue.severity as 'critical' | 'important' | 'consider' | 'polish'
    }))
    .filter(m => m.matchText && m.matchText.length >= 3);
  
  const fixedMarkers = issues
    .filter(issue => !fixedIssues.has(issue.id))
    .map(issue => ({
      id: issue.id,
      matchText: issue.matchText || issue.current_text || issue.problematic_text || '',
      tag: issue.severity as 'critical' | 'important' | 'consider' | 'polish'
    }))
    .filter(m => m.matchText && m.matchText.length >= 3);

  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="border rounded-lg overflow-hidden">
        <div className="bg-red-100 px-4 py-3 border-b flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500"></span>
            <span className="font-medium text-red-800">Original CV</span>
          </div>
          <span className="text-sm text-red-600">
            {issues.length} issues found
          </span>
        </div>
        <div className="p-4 max-h-[600px] overflow-y-auto bg-red-50/30 whitespace-pre-wrap font-mono text-sm">
          <TextMarker
            content={originalCV}
            markers={originalMarkers}
            config={{
              style: 'rectangle',
              tagColors: CV_OPTIMIZER_COLORS
            }}
          />
        </div>
      </div>
      
      <div className="border rounded-lg overflow-hidden">
        <div className="bg-green-100 px-4 py-3 border-b flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-500"></span>
            <span className="font-medium text-green-800">Fixed CV</span>
          </div>
          <span className="text-sm text-green-600">
            {fixedIssues.size} fixed, {issues.length - fixedIssues.size} remaining
          </span>
        </div>
        <div className="p-4 max-h-[600px] overflow-y-auto bg-green-50/30 whitespace-pre-wrap font-mono text-sm">
          <TextMarker
            content={fixedCV}
            markers={fixedMarkers}
            config={{
              style: 'rectangle',
              tagColors: CV_OPTIMIZER_COLORS
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default SideBySideView;
