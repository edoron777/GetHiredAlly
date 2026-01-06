import { TextMarker, CV_OPTIMIZER_COLORS } from '../../common/TextMarker'

interface CVIssue {
  id: string;
  severity: 'critical' | 'important' | 'consider' | 'polish';
  matchText?: string;
  current_text?: string;
  current?: string;
  problematic_text?: string;
  title?: string;
  issue_code?: string;
}

interface CVDocumentProps {
  cvContent: {
    fullText: string;
  };
  issues?: CVIssue[];
  onIssueClick?: (issueId: string) => void;
}

const NO_MARKER_ISSUES = [
  // Length/structure issues - no specific text to highlight
  'LENGTH_CV_TOO_LONG',
  'LENGTH_CV_TOO_SHORT',
  'LENGTH_SUMMARY_TOO_LONG',
  'LENGTH_EXPERIENCE_TOO_DETAILED',
  'LENGTH_EDUCATION_TOO_DETAILED',
  'CONTENT_SUMMARY_TOO_LONG',
  'CONTENT_JOB_DESCRIPTION_TOO_LONG',
  'CONTENT_EDUCATION_DESCRIPTION_TOO_SHORT',
  'CONTENT_JOB_DESCRIPTION_TOO_SHORT',
  'FORMAT_POOR_VISUAL_HIERARCHY',
  'STRUCTURE_EDUCATION_BEFORE_EXPERIENCE',
  // Presence issues - "Not found in:" matched text won't exist in CV
  'CONTACT_MISSING_LINKEDIN',
  'CONTACT_MISSING_GITHUB',
  'CONTACT_MISSING_EMAIL',
  'CONTACT_MISSING_PHONE',
  'CONTENT_MISSING_SUMMARY',
  'CONTENT_MISSING_METRICS',
  'CONTENT_MISSING_IMPACT',
  'FORMAT_MISSING_SECTION_HEADERS',
  'FORMAT_SKILLS_SECTION_MISSING',
];

const findWordBoundaryMatch = (content: string, matchText: string): boolean => {
  if (!matchText || !content) return false;
  
  const trimmedMatch = matchText.trim();
  
  if (trimmedMatch.length <= 2) {
    const escaped = trimmedMatch.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const wordBoundaryRegex = new RegExp(`\\b${escaped}\\b`, 'i');
    return wordBoundaryRegex.test(content);
  }
  
  return content.includes(trimmedMatch);
};

const isValidMarkerForIssue = (issue: CVIssue, cvContent: string): { valid: boolean; matchText: string } => {
  if (issue.issue_code && NO_MARKER_ISSUES.includes(issue.issue_code)) {
    return { valid: false, matchText: '' };
  }
  
  const matchText = issue.current || issue.matchText || issue.current_text || issue.problematic_text || '';
  
  if (!matchText || matchText.trim() === '') {
    return { valid: false, matchText: '' };
  }
  
  const trimmed = matchText.trim();
  
  if (trimmed.startsWith('Not found in:')) {
    return { valid: false, matchText: '' };
  }
  
  if (trimmed.length < 1) {
    return { valid: false, matchText: '' };
  }
  
  const invalidPatterns = [
    /^\d+\s*words/i,
    /^\d+\s*months?\s*gap/i,
    /^years?\s*found/i,
    /^both\s*['"]/i,
    /^(I,\s*)+I/i,
    /\.\.\./,
    /^\d+\s*found:/i,
  ];
  
  for (const pattern of invalidPatterns) {
    if (pattern.test(matchText)) {
      return { valid: false, matchText: '' };
    }
  }
  
  if (findWordBoundaryMatch(cvContent, matchText)) {
    return { valid: true, matchText: trimmed };
  }
  
  return { valid: false, matchText: '' };
};

export const classifyIssues = (issues: CVIssue[], cvContent: string) => {
  const highlightable: CVIssue[] = [];
  const nonHighlightable: CVIssue[] = [];
  
  for (const issue of issues) {
    const result = isValidMarkerForIssue(issue, cvContent);
    
    if (result.valid) {
      highlightable.push({ ...issue, matchText: result.matchText });
    } else {
      nonHighlightable.push({ ...issue, matchText: '' });
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

  const validMarkers: { id: string; matchText: string; tag: string }[] = [];
  
  for (const issue of issues) {
    const result = isValidMarkerForIssue(issue, cvContent.fullText);
    if (result.valid) {
      validMarkers.push({
        id: issue.id?.toString() || '',
        matchText: result.matchText,
        tag: issue.severity || 'consider'
      });
    }
  }

  return (
    <div className="cv-document">
      <TextMarker
        content={cvContent.fullText}
        markers={validMarkers}
        config={{
          style: 'rectangle',
          tagColors: CV_OPTIMIZER_COLORS,
          icon: { 
            icon: '', 
            position: 'before' 
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
