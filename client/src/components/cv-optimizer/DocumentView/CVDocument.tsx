import IssueMarker from './IssueMarker';
import InfoIcon from './InfoIcon';

interface CVSection {
  type: 'header' | 'summary' | 'experience' | 'education' | 'skills' | 'other';
  title?: string;
  content: string;
  startIndex: number;
  endIndex: number;
}

interface CVIssue {
  id: string;
  severity: 'critical' | 'important' | 'consider' | 'polish';
  matchText?: string;
  lineIndex?: number;
}

interface CVDocumentProps {
  cvContent: {
    fullText: string;
    sections?: CVSection[];
  };
  issues?: CVIssue[];
  onIssueClick?: (issueId: string) => void;
}

function isHeaderLine(line: string): boolean {
  const trimmed = line.trim();
  if (!trimmed) return false;
  const isAllCaps = trimmed === trimmed.toUpperCase() && trimmed.length > 2 && /[A-Z]/.test(trimmed);
  const endsWithColon = trimmed.endsWith(':') && trimmed.length > 3;
  return isAllCaps || endsWithColon;
}

function isBulletLine(line: string): boolean {
  const trimmed = line.trim();
  return /^[•\-\*]\s/.test(trimmed);
}

function applyMarkers(
  text: string, 
  issues: CVIssue[], 
  onIssueClick?: (issueId: string) => void
): React.ReactNode {
  if (!issues || issues.length === 0) {
    return text;
  }

  const sortedIssues = issues
    .filter(issue => issue.matchText && text.includes(issue.matchText))
    .sort((a, b) => {
      const aIndex = text.indexOf(a.matchText!);
      const bIndex = text.indexOf(b.matchText!);
      return aIndex - bIndex;
    });

  if (sortedIssues.length === 0) {
    return text;
  }

  const result: React.ReactNode[] = [];
  let lastIndex = 0;

  sortedIssues.forEach((issue, idx) => {
    const matchIndex = text.indexOf(issue.matchText!, lastIndex);
    if (matchIndex === -1) return;

    if (matchIndex > lastIndex) {
      result.push(text.slice(lastIndex, matchIndex));
    }

    result.push(
      <IssueMarker
        key={`marker-${issue.id}-${idx}`}
        severity={issue.severity}
        issueId={issue.id}
        onClick={onIssueClick}
      >
        {issue.matchText}
      </IssueMarker>
    );
    result.push(
      <InfoIcon
        key={`icon-${issue.id}-${idx}`}
        severity={issue.severity}
        issueId={issue.id}
        onClick={onIssueClick || (() => {})}
      />
    );

    lastIndex = matchIndex + issue.matchText!.length;
  });

  if (lastIndex < text.length) {
    result.push(text.slice(lastIndex));
  }

  return result;
}

function renderFullTextWithIssues(
  fullText: string, 
  issues: CVIssue[],
  onIssueClick?: (issueId: string) => void
) {
  const lines = fullText.split('\n');
  
  return lines.map((line, index) => {
    const trimmed = line.trim();
    const lineIssues = issues.filter(i => i.lineIndex === index || (i.matchText && trimmed.includes(i.matchText)));
    
    if (!trimmed) {
      return <div key={index} className="h-3" />;
    }
    
    if (isHeaderLine(trimmed)) {
      return (
        <div key={index} className="cv-section-title">
          {applyMarkers(trimmed.replace(/:$/, ''), lineIssues, onIssueClick)}
        </div>
      );
    }
    
    if (isBulletLine(trimmed)) {
      const bulletContent = trimmed.replace(/^[•\-\*]\s*/, '');
      return (
        <div key={index} className="cv-bullet">
          {applyMarkers(bulletContent, lineIssues, onIssueClick)}
        </div>
      );
    }
    
    return (
      <div key={index} className="cv-paragraph">
        {applyMarkers(trimmed, lineIssues, onIssueClick)}
      </div>
    );
  });
}

function renderSection(
  section: CVSection, 
  index: number,
  issues: CVIssue[],
  onIssueClick?: (issueId: string) => void
) {
  const sectionIssues = issues.filter(i => 
    i.matchText && section.content.includes(i.matchText)
  );

  switch (section.type) {
    case 'header':
      return (
        <div key={index} className="cv-header">
          <div className="cv-name">
            {applyMarkers(section.content.split('\n')[0], sectionIssues, onIssueClick)}
          </div>
          <div className="cv-contact">
            {section.content.split('\n').slice(1).join(' | ')}
          </div>
        </div>
      );
    
    case 'summary':
      return (
        <div key={index} className="cv-section">
          {section.title && <div className="cv-section-title">{section.title}</div>}
          <div className="cv-paragraph">
            {applyMarkers(section.content, sectionIssues, onIssueClick)}
          </div>
        </div>
      );
    
    case 'experience':
    case 'education':
    case 'skills':
    case 'other':
    default:
      return (
        <div key={index} className="cv-section">
          {section.title && <div className="cv-section-title">{section.title}</div>}
          {section.content.split('\n').map((line, lineIndex) => {
            const trimmed = line.trim();
            const lineIssues = sectionIssues.filter(i => i.matchText && trimmed.includes(i.matchText));
            
            if (!trimmed) return <div key={lineIndex} className="h-2" />;
            
            if (isBulletLine(trimmed)) {
              const bulletContent = trimmed.replace(/^[•\-\*]\s*/, '');
              return (
                <div key={lineIndex} className="cv-bullet">
                  {applyMarkers(bulletContent, lineIssues, onIssueClick)}
                </div>
              );
            }
            
            return (
              <div key={lineIndex} className="cv-paragraph">
                {applyMarkers(trimmed, lineIssues, onIssueClick)}
              </div>
            );
          })}
        </div>
      );
  }
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

  if (cvContent.sections && cvContent.sections.length > 0) {
    return (
      <div className="cv-document">
        {cvContent.sections.map((section, index) => 
          renderSection(section, index, issues, onIssueClick)
        )}
      </div>
    );
  }

  return (
    <div className="cv-document">
      {renderFullTextWithIssues(cvContent.fullText, issues, onIssueClick)}
    </div>
  );
}
