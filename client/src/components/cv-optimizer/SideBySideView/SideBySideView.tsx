import React from 'react';
import { TextMarker, CV_OPTIMIZER_COLORS } from '../../common/TextMarker';
import './SideBySideView.css';

interface AppliedChange {
  originalText: string;
  newText: string;
  issueId: string;
}

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
  appliedChanges?: AppliedChange[];
}

function stripMarkdown(text: string): string {
  if (!text) return '';
  return text
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/__([^_]+)__/g, '$1')
    .replace(/_([^_]+)_/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/\n{3,}/g, '\n\n');
}

function stripMarkdownFromMarker(text: string): string {
  if (!text) return '';
  return text
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/__([^_]+)__/g, '$1')
    .replace(/_([^_]+)_/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
}

function highlightChangedText(
  content: string, 
  changes: AppliedChange[]
): React.ReactNode[] {
  if (!changes || changes.length === 0 || !content) {
    return [<span key="full">{content}</span>];
  }

  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let workingContent = content;

  const sortedChanges = [...changes].sort((a, b) => {
    const indexA = workingContent.indexOf(stripMarkdown(a.newText));
    const indexB = workingContent.indexOf(stripMarkdown(b.newText));
    return indexA - indexB;
  });

  sortedChanges.forEach((change, i) => {
    const strippedNewText = stripMarkdown(change.newText);
    const index = workingContent.indexOf(strippedNewText, lastIndex);
    
    if (index !== -1) {
      if (index > lastIndex) {
        parts.push(
          <span key={`text-${i}`}>
            {workingContent.substring(lastIndex, index)}
          </span>
        );
      }
      
      parts.push(
        <span key={`change-${i}`} className="change-marker">
          {strippedNewText}
        </span>
      );
      
      lastIndex = index + strippedNewText.length;
    }
  });

  if (lastIndex < workingContent.length) {
    parts.push(
      <span key="remaining">
        {workingContent.substring(lastIndex)}
      </span>
    );
  }

  return parts.length > 0 ? parts : [<span key="full">{content}</span>];
}

const SideBySideView: React.FC<SideBySideViewProps> = ({
  originalCV,
  fixedCV,
  issues,
  fixedIssues,
  appliedChanges = []
}) => {
  const strippedOriginal = stripMarkdown(originalCV);
  const strippedFixed = stripMarkdown(fixedCV);

  const originalMarkers = issues
    .map(issue => ({
      id: issue.id,
      matchText: stripMarkdownFromMarker(issue.matchText || issue.current_text || issue.problematic_text || ''),
      tag: issue.severity as 'critical' | 'important' | 'consider' | 'polish'
    }))
    .filter(m => m.matchText && m.matchText.length >= 3);
  
  const fixedMarkers = issues
    .filter(issue => !fixedIssues.has(issue.id))
    .map(issue => ({
      id: issue.id,
      matchText: stripMarkdownFromMarker(issue.matchText || issue.current_text || issue.problematic_text || ''),
      tag: issue.severity as 'critical' | 'important' | 'consider' | 'polish'
    }))
    .filter(m => m.matchText && m.matchText.length >= 3);

  const hasChanges = appliedChanges.length > 0;

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
            content={strippedOriginal}
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
          {hasChanges ? (
            <div className="change-highlighted-content">
              {highlightChangedText(strippedFixed, appliedChanges)}
            </div>
          ) : (
            <TextMarker
              content={strippedFixed}
              markers={fixedMarkers}
              config={{
                style: 'rectangle',
                tagColors: CV_OPTIMIZER_COLORS
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default SideBySideView;
