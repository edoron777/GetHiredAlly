import { TextMarker, CV_OPTIMIZER_COLORS } from '../../common/TextMarker'

interface CVIssue {
  id: string;
  severity: 'critical' | 'important' | 'consider' | 'polish';
  matchText?: string;
  title?: string;
}

interface CVDocumentProps {
  cvContent: {
    fullText: string;
  };
  issues?: CVIssue[];
  onIssueClick?: (issueId: string) => void;
}

export default function CVDocument({ cvContent, issues = [], onIssueClick }: CVDocumentProps) {
  console.log('=== CVDOCUMENT DEBUG ===');
  console.log('1. cvContent.fullText length:', cvContent?.fullText?.length);
  console.log('2. cvContent.fullText preview:', cvContent?.fullText?.substring(0, 200));
  console.log('3. issues received:', issues?.length);
  console.log('4. first issue:', issues?.[0]);
  
  if (issues?.length > 0 && cvContent?.fullText) {
    issues.forEach((issue, i) => {
      const found = issue.matchText ? cvContent.fullText.includes(issue.matchText) : false;
      console.log(`Issue ${i + 1} matchText "${issue.matchText?.substring(0, 30)}..." found in CV: ${found}`);
    });
  }
  console.log('=== END DEBUG ===');

  if (!cvContent?.fullText) {
    return (
      <div className="text-gray-500 text-center py-10">
        No CV content to display
      </div>
    );
  }

  const markers = issues
    .filter(issue => issue.matchText && issue.matchText.length > 0)
    .map(issue => ({
      id: issue.id?.toString() || '',
      matchText: issue.matchText || '',
      tag: issue.severity || 'consider'
    }));

  return (
    <div className="cv-document">
      <TextMarker
        content={cvContent.fullText}
        markers={markers}
        config={{
          style: 'underline',
          tagColors: CV_OPTIMIZER_COLORS,
          icon: { 
            icon: 'ⓘ', 
            position: 'after' 
          },
          onClick: (id) => {
            console.log('Marker clicked:', id);
            onIssueClick?.(id);
          },
          className: 'cv-content-text'
        }}
      />
    </div>
  );
}
