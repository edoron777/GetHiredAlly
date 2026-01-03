import { TextMarker, CV_OPTIMIZER_COLORS } from '../../common/TextMarker'

interface CVIssue {
  id: string;
  severity: 'critical' | 'important' | 'consider' | 'polish';
  matchText?: string;
  current_text?: string;
  current?: string;
  problematic_text?: string;
  title?: string;
}

interface CVDocumentProps {
  cvContent: {
    fullText: string;
  };
  issues?: CVIssue[];
  onIssueClick?: (issueId: string) => void;
}

const isValidMarker = (matchText: string | undefined | null, cvContent: string): boolean => {
  if (!matchText || matchText.trim() === '') {
    return false;
  }
  
  if (matchText.trim().length < 3) {
    return false;
  }
  
  const invalidPatterns = [
    /^\d+\s*words/i,
    /^\d+\s*months?\s*gap/i,
    /^years?\s*found/i,
    /^both\s*['"]/i,
    /^(I,\s*)+I/i,
    /\.\.\./,
  ];
  
  for (const pattern of invalidPatterns) {
    if (pattern.test(matchText)) {
      return false;
    }
  }
  
  return cvContent.includes(matchText);
};

export const classifyIssues = (issues: CVIssue[], cvContent: string) => {
  const highlightable: CVIssue[] = [];
  const nonHighlightable: CVIssue[] = [];
  
  for (const issue of issues) {
    const matchText = issue.current || issue.matchText || issue.current_text || issue.problematic_text || '';
    
    if (isValidMarker(matchText, cvContent)) {
      highlightable.push({ ...issue, matchText });
    } else {
      nonHighlightable.push({ ...issue, matchText });
    }
  }
  
  return { highlightable, nonHighlightable, all: issues };
};

export default function CVDocument({ cvContent, issues = [], onIssueClick }: CVDocumentProps) {
  if (!cvContent?.fullText) {
    return (
      <div className="text-gray-500 text-center py-10">
        No CV content to display
      </div>
    );
  }

  const allMarkers = issues.map(issue => ({
    id: issue.id?.toString() || '',
    matchText: issue.current || issue.matchText || issue.current_text || issue.problematic_text || '',
    tag: issue.severity || 'consider'
  }));

  const validMarkers = allMarkers.filter(marker => 
    isValidMarker(marker.matchText, cvContent.fullText)
  );

  console.log('Markers stats:', {
    total: allMarkers.length,
    valid: validMarkers.length,
    invalid: allMarkers.length - validMarkers.length
  });

  return (
    <div className="cv-document">
      <TextMarker
        content={cvContent.fullText}
        markers={validMarkers}
        config={{
          style: 'underline',
          tagColors: CV_OPTIMIZER_COLORS,
          icon: { 
            icon: 'ⓘ', 
            position: 'after' 
          },
          onClick: (id) => {
            onIssueClick?.(id);
          },
          className: 'cv-content-text'
        }}
      />
    </div>
  );
}
